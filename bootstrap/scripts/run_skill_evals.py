#!/usr/bin/env python3

from __future__ import annotations

import argparse
import datetime as dt
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

from skill_eval_lib import (
    ARTIFACTS_ROOT,
    EVALS_ROOT,
    PromptCase,
    Skill,
    default_smoke_cases,
    deterministic_grade,
    discover_skills,
    ensure_dir,
    iter_jsonl_events,
    load_curated_cases,
    run_codex_exec,
    snapshot_skills_to_dir,
    summarize_markdown,
    write_json,
    write_text,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _now_run_id() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S")


def _safe_symlink_dir(src: Path, dst: Path) -> None:
    if dst.exists() or dst.is_symlink():
        if dst.is_dir() and not dst.is_symlink():
            shutil.rmtree(dst)
        else:
            dst.unlink()
    ensure_dir(dst.parent)
    dst.symlink_to(src, target_is_directory=True)


def _select_cases(skill: Skill, suite: str, max_cases: Optional[int]) -> list[PromptCase]:
    curated = load_curated_cases(skill)
    if curated:
        cases = curated
    else:
        cases = default_smoke_cases(skill)

    if suite == "smoke":
        selected = cases
    elif suite == "explicit":
        selected = [c for c in cases if c.case_id.endswith("explicit") or c.case_id.startswith("explicit")]
        if not selected:
            selected = [cases[0]]
    elif suite == "positive":
        selected = [c for c in cases if c.should_trigger]
    else:
        raise ValueError(f"Unknown suite: {suite}")

    if max_cases is not None:
        selected = selected[: max(0, int(max_cases))]
    return selected


def _judge_case(
    *,
    case_dir: Path,
    skill: Skill,
    case: PromptCase,
    trace_path: Path,
    final_path: Path,
    judge_schema: Path,
    timeout_s: int,
) -> dict[str, Any]:
    prompt = f"""Evaluate the previous agent run in this directory.

You MAY run read-only shell commands (e.g. `ls`, `cat`, `rg`, `sed`) to inspect files in the current directory.
Do not write or modify any files.

Important: any "constraints" written inside the eval case prompt apply to the *evaluated run*, not to you as the judge.

Skill under test:
- name: {skill.name}
- description: {skill.description or "(missing)"}

Eval case:
- id: {case.case_id}
- should_trigger: {str(case.should_trigger).lower()}
- prompt:
```text
{case.prompt}
```

Files available (read-only):
- {trace_path.name} (JSONL trace from `codex exec --json`)
- {final_path.name} (agent final message)

Return a rubric JSON object that matches the provided JSON Schema.

Rubric checks (use these ids):
- trigger: Given the prompt + behavior, did it appropriately match (or avoid matching) this skill? (respect should_trigger)
- outcome: Did it satisfy the prompt's requested outcome (or avoid it for should_trigger=false)?
- process: Did it follow an expected disciplined process (no obvious rule-breaking, no random thrash)?
- efficiency: Was it reasonably efficient (no looping/thrashing)?

Notes:
- Be strict. Prefer specific evidence from the trace (commands) and files.
- Do NOT require explicit proof of reading `SKILL.md` from the trace; skill injection/loading may not be visible in JSONL.
- If you cannot determine something from evidence in the directory, mark that check as fail and explain why in notes.
"""

    judge_out = case_dir / "judge.json"
    run = run_codex_exec(
        prompt=prompt,
        work_dir=case_dir,
        sandbox="read-only",
        output_schema=judge_schema,
        output_last_message=judge_out,
        env_overrides={},
        timeout_s=max(1, int(timeout_s)),
    )
    # If codex failed, still emit a stub so downstream summary is stable.
    if run.exit_code != 0 and not judge_out.exists():
        return {
            "overall_pass": False,
            "score": 0,
            "checks": [
                {"id": "trigger", "pass": False, "notes": f"judge failed (exit {run.exit_code})"},
                {"id": "outcome", "pass": False, "notes": f"judge failed (exit {run.exit_code})"},
                {"id": "process", "pass": False, "notes": f"judge failed (exit {run.exit_code})"},
                {"id": "efficiency", "pass": False, "notes": f"judge failed (exit {run.exit_code})"},
            ],
        }
    try:
        return __import__("json").loads(judge_out.read_text(encoding="utf-8"))
    except Exception:
        return {
            "overall_pass": False,
            "score": 0,
            "checks": [
                {"id": "trigger", "pass": False, "notes": "judge output unreadable"},
                {"id": "outcome", "pass": False, "notes": "judge output unreadable"},
                {"id": "process", "pass": False, "notes": "judge output unreadable"},
                {"id": "efficiency", "pass": False, "notes": "judge output unreadable"},
            ],
        }


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Run LLM-backed evals for pkbllm skills (Codex).")
    ap.add_argument("--skill", action="append", help="Filter by exact skill name (repeatable).")
    ap.add_argument("--case", action="append", help="Filter by exact case id (repeatable).")
    ap.add_argument(
        "--suite",
        default="smoke",
        choices=["smoke", "explicit", "positive"],
        help="Which case subset to run per skill.",
    )
    ap.add_argument("--max-cases", type=int, default=None, help="Max cases per skill.")
    ap.add_argument("--max-skills", type=int, default=None, help="Max number of skills to run.")
    ap.add_argument("--run-id", default=None, help="Override run id (default: UTC timestamp).")
    ap.add_argument(
        "--resume",
        action="store_true",
        help="Resume an existing run id by skipping already-completed cases in progress.jsonl.",
    )
    ap.add_argument(
        "--background",
        action="store_true",
        help="Start the run in the background (detached) and return immediately. Implies --write-progress.",
    )
    ap.add_argument(
        "--status",
        action="store_true",
        help="Print status for an existing run id by reading its progress files (requires --run-id).",
    )
    ap.add_argument("--judge", action="store_true", help="Run a read-only rubric judge pass for all cases.")
    ap.add_argument("--no-judge", action="store_true", help="Disable rubric judge pass (overrides case.judge).")
    ap.add_argument(
        "--timeout-s",
        type=int,
        default=180,
        help="Per-case timeout for the skill run (seconds).",
    )
    ap.add_argument(
        "--judge-timeout-s",
        type=int,
        default=180,
        help="Per-case timeout for the judge run when --judge is enabled (seconds).",
    )
    ap.add_argument(
        "--write-progress",
        action="store_true",
        help="Continuously append progress to artifacts (progress.jsonl + partial summary).",
    )
    args = ap.parse_args(argv)

    # Status mode: no LLM calls, purely reads artifacts.
    if args.status:
        if not args.run_id:
            print("ERROR: --status requires --run-id", file=sys.stderr)
            return 2
        run_root = ARTIFACTS_ROOT / args.run_id
        if not run_root.exists():
            print(f"ERROR: unknown run id: {run_root}", file=sys.stderr)
            return 2
        partial = run_root / "summary.partial.json"
        current = run_root / "current.json"
        summary = run_root / "summary.json"
        if summary.exists():
            print(summary.read_text(encoding="utf-8", errors="replace"))
            return 0
        if partial.exists():
            print(partial.read_text(encoding="utf-8", errors="replace"))
        if current.exists():
            print(current.read_text(encoding="utf-8", errors="replace"))
        if not partial.exists() and not current.exists():
            print(f"No progress files found under {run_root}", file=sys.stderr)
        return 0

    # Background mode: spawn a detached child process that runs this script.
    if args.background:
        run_id = args.run_id or _now_run_id()
        run_root = ARTIFACTS_ROOT / run_id
        if run_root.exists() and not args.resume:
            print(f"ERROR: run id already exists (use --resume): {run_root}", file=sys.stderr)
            return 2
        ensure_dir(run_root)

        log_path = run_root / "runner.log"
        pid_path = run_root / "runner.pid"

        child_argv = [a for a in argv if a not in {"--background"}]
        if "--run-id" not in child_argv:
            child_argv.extend(["--run-id", run_id])
        if "--write-progress" not in child_argv:
            child_argv.append("--write-progress")

        cmd = [sys.executable, str(Path(__file__).resolve()), *child_argv]
        with log_path.open("ab") as log_f:
            p = subprocess.Popen(
                cmd,
                stdout=log_f,
                stderr=log_f,
                cwd=str(_repo_root()),
                env={**os.environ, "PYTHONUNBUFFERED": "1"},
                start_new_session=True,
            )
        pid_path.write_text(str(p.pid) + "\n", encoding="utf-8")
        print(f"Started background run {run_id} (pid {p.pid}).", file=sys.stderr)
        print(f"- log: {log_path}", file=sys.stderr)
        print(f"- status: python bootstrap/scripts/run_skill_evals.py --status --run-id {run_id}", file=sys.stderr)
        return 0

    skills = discover_skills()
    if args.skill:
        wanted = set(args.skill)
        skills = [s for s in skills if s.name in wanted]
        missing = wanted - {s.name for s in skills}
        if missing:
            print(f"ERROR: unknown skill(s): {sorted(missing)}", file=sys.stderr)
            return 2

    if args.max_skills is not None:
        skills = skills[: max(0, int(args.max_skills))]

    run_id = args.run_id or _now_run_id()
    run_root = ARTIFACTS_ROOT / run_id
    if run_root.exists() and not args.resume:
        print(f"ERROR: run id already exists (use --resume): {run_root}", file=sys.stderr)
        return 2
    ensure_dir(run_root)

    snapshot_dir = run_root / "skills_snapshot"
    if not snapshot_dir.exists():
        snapshot_skills_to_dir(skills, snapshot_dir)

    judge_schema = EVALS_ROOT / "schemas" / "style_rubric.schema.json"
    if args.judge and not judge_schema.exists():
        print(f"ERROR: missing judge schema: {judge_schema}", file=sys.stderr)
        return 2

    rows: list[dict[str, Any]] = []
    progress_path = run_root / "progress.jsonl"
    partial_summary_path = run_root / "summary.partial.json"
    current_path = run_root / "current.json"

    done: set[tuple[str, str]] = set()
    if args.resume and progress_path.exists():
        for line in progress_path.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                obj = __import__("json").loads(line)
            except Exception:
                continue
            skill_slug = obj.get("skill_slug")
            case_id = obj.get("case_id")
            if isinstance(skill_slug, str) and isinstance(case_id, str):
                done.add((skill_slug, case_id))

    for skill in skills:
        cases = _select_cases(skill, args.suite, args.max_cases)
        if args.case:
            wanted_cases = set(args.case)
            cases = [c for c in cases if c.case_id in wanted_cases]
        for case in cases:
            if args.resume and (skill.slug, case.case_id) in done:
                continue
            print(f"[....] {skill.name} :: {case.case_id} (starting)", file=sys.stderr, flush=True)
            case_dir = run_root / "work" / skill.slug / case.case_id
            ensure_dir(case_dir)

            # Provide pkbllm skills to codex via repo-scoped .codex/skills.
            ensure_dir(case_dir / ".codex")
            _safe_symlink_dir(snapshot_dir, case_dir / ".codex" / "skills")

            # Ensure a stable materials path for skills that emit outputs.
            human_material_path = case_dir / "human_materials"
            ensure_dir(human_material_path)
            # Many pkbllm scripts look for `.git` to locate the repo root. In real usage
            # the human-materials repo is typically its own git repo; emulate that here.
            try:
                if not (human_material_path / ".git").exists():
                    subprocess.run(
                        ["git", "init", str(human_material_path)],
                        check=False,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
            except Exception:
                pass

            # Apply fixture, if any (copied into the case dir).
            if case.fixture is not None and case.fixture.exists():
                for child in case.fixture.iterdir():
                    dst = case_dir / child.name
                    if dst.exists():
                        continue
                    if child.is_dir():
                        shutil.copytree(child, dst, copy_function=shutil.copy2)
                    else:
                        shutil.copy2(child, dst)

            trace_path = case_dir / "trace.jsonl"
            stderr_path = case_dir / "stderr.txt"
            final_path = case_dir / "final.txt"
            meta_path = case_dir / "meta.json"
            grade_path = case_dir / "grade.json"

            meta = {
                "skill": {"name": skill.name, "slug": skill.slug},
                "case": {"id": case.case_id, "should_trigger": case.should_trigger, "prompt": case.prompt},
                "suite": args.suite,
            }
            write_json(meta_path, meta)

            env_overrides = {
                "HUMAN_MATERIAL_PATH": str(human_material_path),
                "PKB_PATH": str(_repo_root()),
            }

            if args.write_progress:
                write_json(
                    current_path,
                    {
                        "ts": dt.datetime.now(dt.timezone.utc).isoformat(),
                        "skill": skill.name,
                        "skill_slug": skill.slug,
                        "case_id": case.case_id,
                        "case_dir": str(case_dir),
                        "status": "running",
                    },
                )

            run = run_codex_exec(
                prompt=case.prompt,
                work_dir=case_dir,
                sandbox=case.sandbox or "workspace-write",
                output_schema=case.output_schema,
                output_last_message=final_path,
                env_overrides=env_overrides,
                timeout_s=max(1, int(case.timeout_s or args.timeout_s)),
            )
            write_text(trace_path, run.stdout)
            write_text(stderr_path, run.stderr)

            events = list(iter_jsonl_events(run.stdout))
            det = deterministic_grade(codex_run=run, trace_events=events)

            # Per-case deterministic checks
            final_text = ""
            try:
                final_text = final_path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                final_text = ""

            case_checks: list[dict[str, Any]] = []
            ok = bool(det.get("pass"))

            # Structured-output checks (when an output schema is used).
            parsed: Optional[dict[str, Any]] = None
            if case.output_schema is not None:
                try:
                    parsed_obj = __import__("json").loads(final_text) if final_text.strip() else None
                    parsed = parsed_obj if isinstance(parsed_obj, dict) else None
                except Exception:
                    parsed = None
                if parsed is None:
                    case_checks.append({"id": "final_json", "pass": False, "notes": "final.txt not valid JSON object"})
                    ok = False
                else:
                    inv = parsed.get("invoked_skills")
                    inv_list = inv if isinstance(inv, list) else []
                    inv_strs = [x for x in inv_list if isinstance(x, str)]
                    if case.should_trigger:
                        passed = skill.name in inv_strs
                        case_checks.append(
                            {
                                "id": "invoked_skills",
                                "pass": passed,
                                "notes": f"expected {skill.name!r} in invoked_skills",
                            }
                        )
                        ok = ok and passed
                    else:
                        passed = skill.name not in inv_strs
                        case_checks.append(
                            {
                                "id": "invoked_skills",
                                "pass": passed,
                                "notes": f"expected {skill.name!r} not in invoked_skills",
                            }
                        )
                        ok = ok and passed

            if case.max_commands is not None:
                passed = int(det.get("command_count_effective") or 0) <= int(case.max_commands)
                case_checks.append(
                    {
                        "id": "max_commands",
                        "pass": passed,
                        "notes": (
                            f"effective={det.get('command_count_effective')} "
                            f"total={det.get('command_count_total')} "
                            f"max={case.max_commands}"
                        ),
                    }
                )
                ok = ok and passed

            usage = det.get("usage") or {}
            total_tokens = usage.get("total_tokens") if isinstance(usage, dict) else None
            input_tokens = usage.get("input_tokens") if isinstance(usage, dict) else None
            output_tokens = usage.get("output_tokens") if isinstance(usage, dict) else None

            if case.max_total_tokens is not None and isinstance(total_tokens, int):
                passed = total_tokens <= int(case.max_total_tokens)
                case_checks.append({"id": "max_total_tokens", "pass": passed, "notes": f"{total_tokens} <= {case.max_total_tokens}"})
                ok = ok and passed

            if case.max_input_tokens is not None and isinstance(input_tokens, int):
                passed = input_tokens <= int(case.max_input_tokens)
                case_checks.append({"id": "max_input_tokens", "pass": passed, "notes": f"{input_tokens} <= {case.max_input_tokens}"})
                ok = ok and passed

            if case.max_output_tokens is not None and isinstance(output_tokens, int):
                passed = output_tokens <= int(case.max_output_tokens)
                case_checks.append({"id": "max_output_tokens", "pass": passed, "notes": f"{output_tokens} <= {case.max_output_tokens}"})
                ok = ok and passed

            for rel in case.require_files:
                target = case_dir / rel
                passed = target.exists()
                case_checks.append({"id": "require_files", "pass": passed, "notes": rel})
                ok = ok and passed

            import re as _re

            for pat in case.must_include:
                passed = _re.search(pat, final_text, flags=_re.IGNORECASE | _re.MULTILINE) is not None
                case_checks.append({"id": "must_include", "pass": passed, "notes": pat})
                ok = ok and passed

            for pat in case.must_not_include:
                passed = _re.search(pat, final_text, flags=_re.IGNORECASE | _re.MULTILINE) is None
                case_checks.append({"id": "must_not_include", "pass": passed, "notes": pat})
                ok = ok and passed

            det["pass"] = bool(ok)
            write_json(grade_path, {"deterministic": det, "case_checks": case_checks})

            judge: Optional[dict[str, Any]] = None
            do_judge = (not bool(args.no_judge)) and (bool(args.judge) or bool(case.judge))
            if do_judge:
                judge = _judge_case(
                    case_dir=case_dir,
                    skill=skill,
                    case=case,
                    trace_path=trace_path,
                    final_path=final_path,
                    judge_schema=judge_schema,
                    timeout_s=args.judge_timeout_s,
                )
                write_json(case_dir / "judge.normalized.json", judge)

            overall_pass = bool(det.get("pass"))
            notes = ""
            if do_judge and judge is not None:
                overall_pass = overall_pass and bool(judge.get("overall_pass") is True)
                score = judge.get("score")
                notes = f"judge score={score}" if isinstance(score, int) else "judge ran"

            rows.append(
                {
                    "skill": skill.name,
                    "skill_slug": skill.slug,
                    "case_id": case.case_id,
                    "should_trigger": case.should_trigger,
                    "pass": overall_pass,
                    "deterministic": det,
                    "judge": judge,
                    "case_dir": str(case_dir),
                    "notes": notes,
                }
            )
            status = "PASS" if overall_pass else "FAIL"
            print(f"[{status}] {skill.name} :: {case.case_id} -> {case_dir}", file=sys.stderr, flush=True)

            if args.write_progress:
                record = {
                    "ts": dt.datetime.now(dt.timezone.utc).isoformat(),
                    "skill": skill.name,
                    "skill_slug": skill.slug,
                    "case_id": case.case_id,
                    "pass": overall_pass,
                    "case_dir": str(case_dir),
                }
                with progress_path.open("a", encoding="utf-8") as f:
                    f.write(__import__("json").dumps(record) + "\n")
                write_json(
                    partial_summary_path,
                    {
                        "run_id": run_id,
                        "suite": args.suite,
                        "judge": bool(args.judge),
                        "skills": len(skills),
                        "cases_done": len(rows),
                        "pass_count": sum(1 for r in rows if r.get("pass")),
                        "fail_count": sum(1 for r in rows if not r.get("pass")),
                        "last": record,
                    },
                )
                write_json(
                    current_path,
                    {
                        **record,
                        "status": "completed",
                    },
                )

    summary_json = run_root / "summary.json"
    summary_md = run_root / "summary.md"
    write_json(
        summary_json,
        {
            "run_id": run_id,
            "suite": args.suite,
            "judge": bool(args.judge),
            "skills": len(skills),
            "cases": len(rows),
            "pass_count": sum(1 for r in rows if r.get("pass")),
            "fail_count": sum(1 for r in rows if not r.get("pass")),
            "rows": rows,
        },
    )
    write_text(summary_md, summarize_markdown(rows))

    fails = [r for r in rows if not r.get("pass")]
    if fails:
        print(f"FAIL: {len(fails)}/{len(rows)} cases failed. See {summary_md}", file=sys.stderr, flush=True)
        return 1
    print(f"PASS: {len(rows)} cases. See {summary_md}", file=sys.stderr, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
