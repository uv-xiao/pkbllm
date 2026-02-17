from __future__ import annotations

import csv
import json
import os
import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Optional


REPO_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_ROOTS = [
    REPO_ROOT / "bootstrap",
    REPO_ROOT / "common",
    REPO_ROOT / "human",
    REPO_ROOT / "knowledge",
    REPO_ROOT / "productivity",
]

EVALS_ROOT = REPO_ROOT / "evals"
EVALS_SKILLS_ROOT = EVALS_ROOT / "skills"
ARTIFACTS_ROOT = REPO_ROOT / "artifacts" / "skill-evals"


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    canonical_dir: Path
    skill_md: Path
    slug: str


@dataclass(frozen=True)
class PromptCase:
    case_id: str
    should_trigger: bool
    prompt: str
    sandbox: str = "workspace-write"
    timeout_s: int = 180
    max_commands: Optional[int] = None
    max_input_tokens: Optional[int] = None
    max_output_tokens: Optional[int] = None
    max_total_tokens: Optional[int] = None
    output_schema: Optional[Path] = None
    judge: bool = False
    require_files: tuple[str, ...] = ()
    must_include: tuple[str, ...] = ()
    must_not_include: tuple[str, ...] = ()
    fixture: Optional[Path] = None


@dataclass(frozen=True)
class CodexRun:
    exit_code: int
    stdout: str
    stderr: str
    duration_s: float


_SLUG_BAD = re.compile(r"[^a-z0-9._-]+")


def skill_slug(name: str) -> str:
    slug = name.strip().lower()
    slug = re.sub(r"\s+", "-", slug)
    slug = slug.replace("/", "").replace("\\", "").replace(":", "")
    slug = _SLUG_BAD.sub("-", slug).strip("-")
    if not slug:
        raise ValueError(f"Could not slugify skill name: {name!r}")
    return slug


def read_frontmatter(skill_md: Path) -> dict[str, str]:
    lines = skill_md.read_text(encoding="utf-8", errors="replace").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"SKILL.md missing frontmatter (expected leading '---'): {skill_md}")
    out: dict[str, str] = {}
    for line in lines[1:250]:
        if line.strip() == "---":
            break
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and key not in out:
            out[key] = value
    return out


def discover_skills() -> list[Skill]:
    skill_mds: list[Path] = []
    for root in CANONICAL_ROOTS:
        if not root.exists():
            continue
        skill_mds.extend(p for p in root.rglob("SKILL.md") if p.name == "SKILL.md")
    skill_mds = sorted(set(skill_mds))

    skills: list[Skill] = []
    seen_slugs: dict[str, Path] = {}
    for skill_md in skill_mds:
        fm = read_frontmatter(skill_md)
        name = (fm.get("name") or "").strip()
        description = (fm.get("description") or "").strip()
        if not name:
            raise ValueError(f"Missing frontmatter name: {skill_md}")
        slug = skill_slug(name)
        if slug in seen_slugs:
            raise ValueError(f"slug collision: {slug!r} from {skill_md} and {seen_slugs[slug]}")
        seen_slugs[slug] = skill_md
        skills.append(
            Skill(
                name=name,
                description=description,
                canonical_dir=skill_md.parent,
                skill_md=skill_md,
                slug=slug,
            )
        )
    return skills


def load_curated_cases(skill: Skill) -> Optional[list[PromptCase]]:
    skill_evals_dir = EVALS_SKILLS_ROOT / skill.slug
    prompts_csv = skill_evals_dir / "prompts.csv"
    if not prompts_csv.exists():
        return None
    cases: list[PromptCase] = []
    with prompts_csv.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            case_id = (row.get("id") or "").strip()
            should_trigger_raw = (row.get("should_trigger") or "").strip().lower()
            prompt = (row.get("prompt") or "").strip()
            if not case_id or not prompt:
                continue
            if should_trigger_raw not in {"true", "false"}:
                continue
            sandbox = (row.get("sandbox") or "").strip() or "workspace-write"
            timeout_s_raw = (row.get("timeout_s") or "").strip()
            max_commands_raw = (row.get("max_commands") or "").strip()
            max_input_tokens_raw = (row.get("max_input_tokens") or "").strip()
            max_output_tokens_raw = (row.get("max_output_tokens") or "").strip()
            max_total_tokens_raw = (row.get("max_total_tokens") or "").strip()
            output_schema_raw = (row.get("output_schema") or "").strip()
            judge_raw = (row.get("judge") or "").strip().lower()
            require_files_raw = (row.get("require_files") or "").strip()
            must_include_raw = (row.get("must_include") or "").strip()
            must_not_include_raw = (row.get("must_not_include") or "").strip()
            fixture_raw = (row.get("fixture") or "").strip()

            timeout_s = int(timeout_s_raw) if timeout_s_raw.isdigit() else 180
            max_commands = int(max_commands_raw) if max_commands_raw.isdigit() else None
            max_input_tokens = int(max_input_tokens_raw) if max_input_tokens_raw.isdigit() else None
            max_output_tokens = int(max_output_tokens_raw) if max_output_tokens_raw.isdigit() else None
            max_total_tokens = int(max_total_tokens_raw) if max_total_tokens_raw.isdigit() else None
            output_schema = (REPO_ROOT / output_schema_raw) if output_schema_raw else None
            judge = judge_raw == "true"
            require_files = tuple(p.strip() for p in require_files_raw.split(";") if p.strip())
            must_include = tuple(p.strip() for p in must_include_raw.split("|") if p.strip())
            must_not_include = tuple(p.strip() for p in must_not_include_raw.split("|") if p.strip())
            fixture = (skill_evals_dir / fixture_raw) if fixture_raw else None

            cases.append(
                PromptCase(
                    case_id=case_id,
                    should_trigger=(should_trigger_raw == "true"),
                    prompt=prompt,
                    sandbox=sandbox,
                    timeout_s=timeout_s,
                    max_commands=max_commands,
                    max_input_tokens=max_input_tokens,
                    max_output_tokens=max_output_tokens,
                    max_total_tokens=max_total_tokens,
                    output_schema=output_schema,
                    judge=judge,
                    require_files=require_files,
                    must_include=must_include,
                    must_not_include=must_not_include,
                    fixture=fixture,
                )
            )
    return cases or None


def default_smoke_cases(skill: Skill) -> list[PromptCase]:
    default_schema = EVALS_ROOT / "schemas" / "skill_response.schema.json"
    explicit = PromptCase(
        case_id="smoke-explicit",
        should_trigger=True,
        prompt=(
            f"Use the ${skill.name} skill.\n\n"
            "Goal: Demonstrate the skill on a small, realistic scenario.\n\n"
            "Constraints:\n"
            "- Keep it small and finish cleanly.\n"
            "- Prefer a structured, actionable response.\n"
            "- Do not run shell commands or write files unless the skill clearly requires it; if you do, keep it to <= 3 commands.\n\n"
            "- Do not download/clone large repos or install big dependencies.\n\n"
            f"Scenario:\n{skill.description or '(no description provided)'}"
        ),
        sandbox="read-only",
        timeout_s=180,
        max_commands=0,
        output_schema=default_schema if default_schema.exists() else None,
        judge=False,
    )

    implicit = PromptCase(
        case_id="smoke-implicit",
        should_trigger=True,
        prompt=(
            "Do the following task in a small, reliable, repeatable way. Do not mention any skill by name.\n\n"
            f"{skill.description or '(no description provided)'}"
        ),
        sandbox="read-only",
        timeout_s=180,
        max_commands=0,
        output_schema=default_schema if default_schema.exists() else None,
        judge=False,
    )

    negative = PromptCase(
        case_id="smoke-negative",
        should_trigger=False,
        prompt=(
            "Do a tiny unrelated edit: create a file named `UNRELATED.txt` containing the single line `ok`.\n"
            "Do not scaffold projects or run setup workflows."
        ),
        sandbox="read-only",
        timeout_s=120,
        max_commands=0,
        output_schema=default_schema if default_schema.exists() else None,
        judge=False,
    )

    return [explicit, implicit, negative]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str) -> None:
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, obj: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def snapshot_skills_to_dir(skills: Iterable[Skill], snapshot_dir: Path) -> None:
    """
    Create a snapshot of canonical skills in `snapshot_dir/<skill-slug>/...`.
    Intended to be referenced from eval workspaces via symlink.
    """
    import shutil

    ensure_dir(snapshot_dir)
    for s in skills:
        dst = snapshot_dir / s.slug
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(s.canonical_dir, dst, copy_function=shutil.copy2)


def _safe_env_for_codex(base_env: dict[str, str], fake_home: Path) -> dict[str, str]:
    env = dict(base_env)
    env["HOME"] = str(fake_home)
    env.setdefault("XDG_CONFIG_HOME", str(fake_home / ".config"))
    env.setdefault("XDG_DATA_HOME", str(fake_home / ".local" / "share"))
    env.setdefault("XDG_STATE_HOME", str(fake_home / ".local" / "state"))
    return env


def run_codex_exec(
    *,
    prompt: str,
    work_dir: Path,
    sandbox: str,
    output_schema: Optional[Path] = None,
    output_last_message: Optional[Path] = None,
    extra_args: Optional[list[str]] = None,
    env_overrides: Optional[dict[str, str]] = None,
    timeout_s: int = 60 * 20,
) -> CodexRun:
    """
    Runs codex non-interactively in `work_dir` and captures stdout/stderr.

    Notes:
    - Uses `--skip-git-repo-check` since eval workspaces are often not git repos.
    - Sets HOME to an empty directory inside the workspace to avoid loading user-level skills/config.
    """
    ensure_dir(work_dir)
    fake_home = work_dir / ".eval_home"
    ensure_dir(fake_home)
    # Avoid noisy startup errors in environments where ~/.zshenv sources ~/.cargo/env.
    try:
        ensure_dir(fake_home / ".cargo")
        (fake_home / ".cargo" / "env").write_text("", encoding="utf-8")
    except Exception:
        pass
    # Seed auth/config into the isolated HOME so `codex exec` can run without
    # inheriting user-level skills from the real ~/.codex/skills.
    try:
        import shutil

        real_codex = Path(os.path.expanduser("~")) / ".codex"
        fake_codex = fake_home / ".codex"
        ensure_dir(fake_codex)
        for fname in ["auth.json", "config.toml", "version.json"]:
            src = real_codex / fname
            dst = fake_codex / fname
            if src.exists() and not dst.exists():
                shutil.copy2(src, dst)
    except Exception:
        # Best-effort: if this fails, codex may still work if auth is provided via env.
        pass

    args: list[str] = [
        "codex",
        "exec",
        "--json",
        "--sandbox",
        sandbox,
        "--skip-git-repo-check",
        "-c",
        'approval_policy="never"',
        "-C",
        str(work_dir),
    ]
    if output_schema is not None:
        args.extend(["--output-schema", str(output_schema)])
    if output_last_message is not None:
        args.extend(["--output-last-message", str(output_last_message)])
    if extra_args:
        args.extend(extra_args)
    args.append(prompt)

    start = time.time()
    try:
        res = subprocess.run(
            args,
            cwd=str(work_dir),
            env={
                **_safe_env_for_codex(os.environ, fake_home),
                **(env_overrides or {}),
            },
            text=True,
            capture_output=True,
            timeout=timeout_s,
        )
        end = time.time()
        return CodexRun(
            exit_code=int(res.returncode),
            stdout=res.stdout,
            stderr=res.stderr,
            duration_s=end - start,
        )
    except subprocess.TimeoutExpired as e:
        end = time.time()
        stdout = e.stdout if isinstance(e.stdout, str) else ""
        stderr = e.stderr if isinstance(e.stderr, str) else ""
        stderr = (stderr + "\n" if stderr else "") + f"TIMEOUT after {timeout_s}s\n"
        return CodexRun(
            exit_code=124,
            stdout=stdout,
            stderr=stderr,
            duration_s=end - start,
        )


def iter_jsonl_events(jsonl_text: str) -> Iterable[dict[str, Any]]:
    for line in jsonl_text.splitlines():
        line = line.strip()
        if not line.startswith("{") or not line.endswith("}"):
            continue
        try:
            yield json.loads(line)
        except Exception:
            continue


def extract_commands(events: Iterable[dict[str, Any]]) -> list[str]:
    cmds: list[str] = []
    seen_ids: set[str] = set()
    for e in events:
        if e.get("type") != "item.completed":
            continue
        item = e.get("item") or {}
        if item.get("type") == "command_execution":
            item_id = item.get("id")
            if isinstance(item_id, str):
                if item_id in seen_ids:
                    continue
                seen_ids.add(item_id)
            cmd = item.get("command")
            if isinstance(cmd, str):
                cmds.append(cmd)
    return cmds


def extract_final_agent_message(events: Iterable[dict[str, Any]]) -> Optional[str]:
    text: Optional[str] = None
    for e in events:
        if e.get("type") != "item.completed":
            continue
        item = e.get("item") or {}
        if item.get("type") == "agent_message":
            t = item.get("text")
            if isinstance(t, str):
                text = t
    return text


def _is_skill_doc_read_command(cmd: str) -> bool:
    # Codex may read skill content from the injected snapshot using shell tools.
    # This shouldn't count as "thrashing" for max_commands purposes.
    if ("skills_snapshot" in cmd) and ("SKILL.md" in cmd):
        return True

    # Some agent runtimes do a quick directory probe in a fresh workspace.
    # Treat these as ignorable to keep max_commands=0 meaningful for "no real actions".
    # We intentionally keep this narrow (no pipes/redirections/complex shell).
    m = re.match(r"^/bin/zsh\s+-lc\s+(.+)$", cmd.strip())
    inner = m.group(1).strip() if m else cmd.strip()
    if (inner.startswith("'") and inner.endswith("'")) or (inner.startswith('"') and inner.endswith('"')):
        inner = inner[1:-1].strip()
    if inner in {"ls", "pwd", "ls -la", "ls -l", "ls -1"}:
        return True
    if inner.startswith("ls "):
        # Allow simple `ls <path>` variants.
        if all(ch.isalnum() or ch in " ./_-:" for ch in inner):
            return True
    return False


def extract_token_usage(events: Iterable[dict[str, Any]]) -> dict[str, int]:
    """
    Best-effort usage extraction from codex JSONL traces.

    We sum across all `turn.completed` events.
    """
    totals = {"turns": 0, "input_tokens": 0, "cached_input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    for e in events:
        if e.get("type") != "turn.completed":
            continue
        totals["turns"] += 1
        usage = e.get("usage") or {}
        for k in ["input_tokens", "cached_input_tokens", "output_tokens"]:
            v = usage.get(k)
            if isinstance(v, int):
                totals[k] += v
            elif isinstance(v, str) and v.isdigit():
                totals[k] += int(v)
    totals["total_tokens"] = totals["input_tokens"] + totals["output_tokens"]
    return totals


def deterministic_grade(*, codex_run: CodexRun, trace_events: list[dict[str, Any]]) -> dict[str, Any]:
    cmds = extract_commands(trace_events)
    effective_cmds = [c for c in cmds if not _is_skill_doc_read_command(c)]
    final_msg = extract_final_agent_message(trace_events)
    usage = extract_token_usage(trace_events)

    # Lightweight smoke checks; keep this explainable.
    return {
        "exit_code": codex_run.exit_code,
        "duration_s": round(codex_run.duration_s, 3),
        "command_count_total": len(cmds),
        "command_count_effective": len(effective_cmds),
        "usage": usage,
        "has_final_message": bool(final_msg and final_msg.strip()),
        "pass": (codex_run.exit_code == 0) and bool(final_msg and final_msg.strip()),
    }


def summarize_markdown(rows: list[dict[str, Any]]) -> str:
    lines = ["# Skill eval summary", "", "| Skill | Case | Pass | Notes |", "| --- | --- | --- | --- |"]
    for r in rows:
        skill = r.get("skill", "")
        case_id = r.get("case_id", "")
        ok = "PASS" if r.get("pass") else "FAIL"
        notes = (r.get("notes") or "").replace("\n", " ").strip()
        lines.append(f"| `{skill}` | `{case_id}` | {ok} | {notes} |")
    lines.append("")
    return "\n".join(lines)
