#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional


REPO_ROOT = Path(__file__).resolve().parents[2]


def _now_id() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S")


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _write_text(path: Path, text: str) -> None:
    _ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, obj: Any) -> None:
    _write_text(path, json.dumps(obj, indent=2, sort_keys=True) + "\n")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _input_or_die(prompt: str = "") -> str:
    try:
        return input(prompt)
    except EOFError as e:
        raise SystemExit(
            "Interactive input is unavailable. If you launched via a piped shell command, rerun with a TTY "
            "or pass --no-interactive --task '...' --done '...'."
        ) from e


def _prompt(label: str, default: Optional[str] = None) -> str:
    if default is None:
        return _input_or_die(f"{label}: ").strip()
    raw = _input_or_die(f"{label} [{default}]: ").strip()
    return raw or default


def _prompt_multiline(label: str) -> str:
    print(f"{label} (end with empty line):")
    lines: list[str] = []
    while True:
        line = _input_or_die()
        if not line.strip():
            break
        lines.append(line.rstrip("\n"))
    return "\n".join(lines).strip()


def _which(cmd: str) -> Optional[str]:
    return shutil.which(cmd)


def _agent_dest(target: Path, agent: str) -> Path:
    a = agent.strip().lower()
    if a == "codex":
        return target / ".codex" / "skills"
    if a in {"agents", "agent"}:
        # Best-effort for other runtimes that follow the same convention.
        return target / f".{a}" / "skills"
    # Unknown: default to codex-like.
    return target / ".codex" / "skills"


def _copy_skill_dir(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, copy_function=shutil.copy2)


def _list_mirror_skill_names(pkb_root: Path) -> set[str]:
    root = pkb_root / "skills"
    out: set[str] = set()
    if not root.is_dir():
        return out
    for d in root.iterdir():
        if not d.is_dir():
            continue
        skill_md = d / "SKILL.md"
        if not skill_md.exists():
            continue
        text = _read_text(skill_md)
        for line in text.splitlines()[:120]:
            if line.startswith("name:"):
                name = line.split(":", 1)[1].strip().strip("'\"")
                if name.startswith("uv-"):
                    out.add(name)
                break
    return out


def _snapshot_skills_for_codex(pkb_root: Path, work_dir: Path) -> None:
    """
    Provide pkb skills to codex via `.codex/skills` inside `work_dir`.
    We intentionally use the generated `skills/` mirror as the surface.
    """
    skills_src = pkb_root / "skills"
    if not skills_src.is_dir():
        raise FileNotFoundError(f"Missing skills mirror at {skills_src}. Run update_skills_mirror.py all.")
    codex_dir = work_dir / ".codex"
    _ensure_dir(codex_dir)
    dst = codex_dir / "skills"
    if dst.exists() or dst.is_symlink():
        if dst.is_dir() and not dst.is_symlink():
            shutil.rmtree(dst)
        else:
            dst.unlink()
    dst.symlink_to(skills_src, target_is_directory=True)


def _run_codex_exec(
    *,
    prompt: str,
    work_dir: Path,
    output_schema: Path,
    output_last_message: Path,
    timeout_s: int,
    debug_dir: Path,
    tag: str,
) -> dict[str, Any]:
    if _which("codex") is None:
        raise RuntimeError("Missing `codex` CLI on PATH.")
    _ensure_dir(work_dir)
    _ensure_dir(debug_dir)

    cmd = [
        "codex",
        "exec",
        "--json",
        "--sandbox",
        "read-only",
        "--skip-git-repo-check",
        "-c",
        'approval_policy="never"',
        "-C",
        str(work_dir),
        "--output-schema",
        str(output_schema),
        "--output-last-message",
        str(output_last_message),
        prompt,
    ]
    _write_text(debug_dir / f"{tag}.prompt.txt", prompt)
    _write_text(debug_dir / f"{tag}.cmd.txt", " ".join(cmd) + "\n")
    try:
        res = subprocess.run(
            cmd,
            cwd=str(work_dir),
            text=True,
            capture_output=True,
            timeout=timeout_s,
            env=os.environ,
        )
    except subprocess.TimeoutExpired as e:
        _write_text(debug_dir / f"{tag}.stdout.jsonl", (e.stdout or ""))
        _write_text(debug_dir / f"{tag}.stderr.txt", (e.stderr or "") + f"\nTIMEOUT after {timeout_s}s\n")
        raise

    _write_text(debug_dir / f"{tag}.stdout.jsonl", res.stdout or "")
    _write_text(debug_dir / f"{tag}.stderr.txt", res.stderr or "")
    if res.returncode != 0:
        raise RuntimeError(f"codex exec failed (exit {res.returncode}); see {debug_dir}/{tag}.stderr.txt")
    try:
        obj = json.loads(_read_text(output_last_message))
        if not isinstance(obj, dict):
            raise ValueError("last message is not an object")
        return obj
    except Exception as e:
        raise RuntimeError(f"Failed to parse structured output JSON: {e}")


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Agent-assisted task bootstrap for pkbllm.")
    ap.add_argument("--target", default=".", help="Target project directory to update (default: cwd).")
    ap.add_argument("--agent", default="codex", help="Target agent name for installation (default: codex).")
    ap.add_argument(
        "--install-mode",
        choices=["copy", "skills-cli", "none"],
        default="copy",
        help="How to install selected skills into the target repo (default: copy).",
    )
    ap.add_argument("--agents-md", default="AGENTS.md", help="AGENTS.md path relative to target (default: AGENTS.md).")
    ap.add_argument("--task", default=None, help="One-sentence task description (non-interactive).")
    ap.add_argument("--done", default=None, help="Definition of done (non-interactive).")
    ap.add_argument("--constraints", default=None, help="Constraints/preferences (non-interactive).")
    ap.add_argument("--top", type=int, default=12, help="How many skills to consider.")
    ap.add_argument("--debug-dir", default=None, help="Write debug logs to this directory (default: artifacts/task-start/<ts>).")
    ap.add_argument("--timeout-s", type=int, default=180, help="Timeout per codex call.")
    ap.add_argument("--no-interactive", action="store_true", help="Fail if required fields are missing.")
    args = ap.parse_args(argv)

    pkb_root = REPO_ROOT
    target = Path(args.target).expanduser().resolve()
    agents_md_path = (target / args.agents_md).resolve()
    expected_install_dest = _agent_dest(target, args.agent)

    debug_dir = Path(args.debug_dir).expanduser().resolve() if args.debug_dir else (pkb_root / "artifacts" / "task-start" / _now_id())
    _ensure_dir(debug_dir)
    _write_json(
        debug_dir / "meta.json",
        {
            "ts": dt.datetime.now(dt.timezone.utc).isoformat(),
            "pkb_root": str(pkb_root),
            "target": str(target),
            "agent": args.agent,
            "install_mode": args.install_mode,
            "agents_md": str(agents_md_path),
        },
    )

    if not target.exists():
        raise SystemExit(f"Target directory does not exist: {target}")

    if not args.no_interactive:
        args.agent = _prompt("选择安装目标 agent（codex/agents/agent）", args.agent or "codex")
        args.install_mode = _prompt("安装方式（copy/skills-cli/none）", args.install_mode or "copy")
        expected_install_dest = _agent_dest(target, args.agent)

    # Gather initial user inputs (minimal + adaptive follow-ups done by the agent).
    task = args.task
    done = args.done
    constraints = args.constraints
    if task is None:
        if args.no_interactive:
            raise SystemExit("--task is required in --no-interactive mode.")
        task = _prompt("任务描述（1句话）")
    if done is None:
        if args.no_interactive:
            raise SystemExit("--done is required in --no-interactive mode.")
        done = _prompt("Done 定义（1句话）")
    if constraints is None:
        if args.no_interactive:
            constraints = ""
        else:
            constraints = _prompt_multiline("约束/偏好（依赖、网络、风格、仓库规则）")

    base_context = f"""Task: {task}
Definition of done: {done}
Constraints:
{constraints}
"""

    mirror_skills = _list_mirror_skill_names(pkb_root)
    if not mirror_skills:
        raise SystemExit("No skills found under pkbllm skills/. Did you run update_skills_mirror.py all?")

    # Create a temp workspace to run codex with pkb skills mounted under .codex/skills.
    work_dir = debug_dir / "work"
    _ensure_dir(work_dir)
    _snapshot_skills_for_codex(pkb_root, work_dir)

    # 1) Ask the agent for a few task-specific clarifying questions (brainstorm-lite).
    questions_schema = pkb_root / "evals" / "schemas" / "skill_response.schema.json"
    questions_out = debug_dir / "questions.json"
    q_prompt = f"""You are helping bootstrap a task by assembling pkbllm skills into AGENTS.md.

Return a JSON object that matches the provided output schema.

Do NOT execute commands or write files.

Use the $uv-start-task skill.

Given this task context:
```text
{base_context}
```

Ask 3 concise clarifying questions that would materially change which skills to choose.
In `steps`, include the two CLI commands the user will run later:
- `python .../pkb_agents_md.py recommend --query ...`
- `python .../pkb_agents_md.py assemble --query ... --agents-md ./AGENTS.md --pick --init`
"""
    q_obj = _run_codex_exec(
        prompt=q_prompt,
        work_dir=work_dir,
        output_schema=questions_schema,
        output_last_message=questions_out,
        timeout_s=max(30, int(args.timeout_s)),
        debug_dir=debug_dir,
        tag="questions",
    )
    q_list = q_obj.get("questions") if isinstance(q_obj, dict) else None
    questions: list[str] = [x for x in (q_list or []) if isinstance(x, str)]
    _write_json(debug_dir / "questions.parsed.json", {"questions": questions})

    answers: list[str] = []
    if questions and not args.no_interactive:
        print("\n== 需要你回答几个问题（用于选技能） ==")
        for i, q in enumerate(questions[:3], start=1):
            ans = _prompt(f"Q{i}: {q}")
            answers.append(ans)
    else:
        answers = ["", "", ""]

    # 2) Ask the agent to output a structured plan: which skills to install + embed.
    plan_schema = pkb_root / "evals" / "schemas" / "task_bootstrap.schema.json"
    plan_out = debug_dir / "plan.json"
    plan_prompt = f"""You are helping bootstrap a task using pkbllm by assembling full skill notes into a repo's AGENTS.md.

Return a JSON object that matches the provided output schema.

You MAY read skills from the injected pkbllm skill set, but do not execute shell commands or write files.

Use the $uv-find-skills skill and the $uv-start-task skill as guidance, but you are not installing anything yourself.

Task context:
```text
{base_context}
```

Clarifying Q&A:
1) {questions[0] if len(questions)>0 else "(none)"} -> {answers[0]}
2) {questions[1] if len(questions)>1 else "(none)"} -> {answers[1]}
3) {questions[2] if len(questions)>2 else "(none)"} -> {answers[2]}

Constraints:
- Choose 3 to 8 skills (uv-*) total.
- Prefer minimal, high-impact skills that directly help complete the task.
- `agents_md.mode` must be `full_embed` and should embed the same skills you select.
- `install.mode` should match this value: {args.install_mode!r}
- `install.agent` should match this value: {args.agent!r}
- `install.destination_dir` should match this value: {str(expected_install_dest.relative_to(target))!r}
- `agents_md.target_path` should be: {args.agents_md!r}
- If uncertain, include warnings.
"""
    plan = _run_codex_exec(
        prompt=plan_prompt,
        work_dir=work_dir,
        output_schema=plan_schema,
        output_last_message=plan_out,
        timeout_s=max(30, int(args.timeout_s)),
        debug_dir=debug_dir,
        tag="plan",
    )
    _write_json(debug_dir / "plan.parsed.json", plan)

    # Validate skills exist.
    selected = plan.get("selected_skills") if isinstance(plan, dict) else None
    selected_skills: list[str] = [s for s in (selected or []) if isinstance(s, str)]
    selected_skills = [s for s in selected_skills if s.startswith("uv-")]
    selected_skills = list(dict.fromkeys(selected_skills))  # de-dup preserve order
    if not (3 <= len(selected_skills) <= 8):
        raise SystemExit(f"Agent selected {len(selected_skills)} skills; expected 3..8. See {debug_dir}/plan.parsed.json")
    missing = [s for s in selected_skills if s not in mirror_skills]
    if missing:
        raise SystemExit(f"Agent selected unknown skill(s): {missing}. See {debug_dir}/plan.parsed.json")

    # Assemble AGENTS.md using pkb_agents_md (full embed).
    assemble_cmd = [
        sys.executable,
        str(pkb_root / "bootstrap" / "scripts" / "pkb_agents_md.py"),
        "--source",
        "mirror",
        "assemble",
        "--query",
        base_context,
        "--agents-md",
        str(agents_md_path),
        "--init",
    ]
    for s in selected_skills:
        assemble_cmd.extend(["--skill", s])
    _write_text(debug_dir / "assemble.cmd.txt", " ".join(assemble_cmd) + "\n")
    subprocess.run(assemble_cmd, check=True, cwd=str(pkb_root), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Install skills into target repo.
    install_mode = (plan.get("install") or {}).get("mode") if isinstance(plan.get("install"), dict) else args.install_mode
    if install_mode not in {"copy", "skills-cli", "none"}:
        install_mode = args.install_mode

    # Ignore any agent-provided destination; compute locally.
    dest_root = _agent_dest(target, args.agent)

    if install_mode == "none":
        _write_text(debug_dir / "install.txt", "install skipped (mode=none)\n")
    elif install_mode == "skills-cli":
        if _which("npx") is None:
            raise SystemExit("install-mode=skills-cli requires npx, but it was not found.")
        # Install from the pkbllm clone path into the target project.
        for s in selected_skills:
            cmd = ["npx", "-y", "skills", "add", str(pkb_root), "-a", args.agent, "--skill", s, "-y"]
            subprocess.run(cmd, check=True, cwd=str(target), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _write_text(debug_dir / "install.txt", f"installed {len(selected_skills)} via skills-cli\n")
    else:
        _ensure_dir(dest_root)
        for s in selected_skills:
            src = pkb_root / "skills" / s
            dst = dest_root / s
            if not src.is_dir():
                raise SystemExit(f"Missing skill in mirror: {src}")
            _copy_skill_dir(src, dst)
        _write_text(debug_dir / "install.txt", f"installed {len(selected_skills)} by copy into {dest_root}\n")

    # Final summary for the user.
    print("\n== 完成 ==")
    print(f"- target: {target}")
    print(f"- AGENTS.md updated: {agents_md_path}")
    print(f"- skills ({len(selected_skills)}): {', '.join(selected_skills)}")
    print(f"- install_mode: {install_mode}")
    print(f"- debug_dir: {debug_dir}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        raise SystemExit(0)
