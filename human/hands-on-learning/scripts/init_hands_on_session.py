#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as _dt
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

from pkbllm_config import find_repo_root, load_config, resolve_config_path, resolve_human_material_root


_NON_SLUG = re.compile(r"[^a-z0-9]+")


def _slugify(value: str) -> str:
    v = value.strip().lower()
    v = v.replace("_", "-")
    v = _NON_SLUG.sub("-", v).strip("-")
    return v or "session"


def _repo_name_from_url(url: str) -> str:
    tail = url.rstrip("/").split("/")[-1]
    if tail.endswith(".git"):
        tail = tail[:-4]
    return tail


def _ensure_clone(repo_spec: str, repos_dir: Path, *, update: bool) -> Path:
    if Path(repo_spec).expanduser().exists():
        return Path(repo_spec).expanduser().resolve()

    name = _repo_name_from_url(repo_spec)
    slug = _slugify(name)
    clone_path = repos_dir / slug
    clone_path.parent.mkdir(parents=True, exist_ok=True)

    if clone_path.exists() and (clone_path / ".git").exists():
        if update:
            subprocess.run(["git", "-C", str(clone_path), "fetch", "--all", "--prune"], check=False)
        return clone_path

    subprocess.run(["git", "clone", "--depth", "1", repo_spec, str(clone_path)], check=True)
    return clone_path


def _run_capture(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT).strip()
    except Exception as e:
        return f"[unavailable: {e}]"


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(content, encoding="utf-8")

def _write_text_overwrite(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def _file_contains_any(path: Path, needles: list[str]) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return False
    return any(n in text for n in needles)

def _copy_skeleton(skeleton_dir: Path, dest: Path) -> None:
    if not skeleton_dir.exists():
        return
    for src in skeleton_dir.rglob("*"):
        rel = src.relative_to(skeleton_dir)
        dst = dest / rel
        if src.is_dir():
            dst.mkdir(parents=True, exist_ok=True)
            continue
        if dst.exists():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Initialize a hands-on learning session under $HUMAN_MATERIAL_PATH.")
    p.add_argument("repo", help="Repo URL (git clone) or local path")
    p.add_argument("--slug", help="Override repo slug under $HUMAN_MATERIAL_PATH/research/<slug>/")
    p.add_argument("--session", help="Session name (default: YYYYMMDD-hands-on)")
    p.add_argument("--update", action="store_true", help="If already cloned, fetch updates (best effort).")
    args = p.parse_args(argv)

    human_root = resolve_human_material_root()
    if not human_root:
        print("HUMAN_MATERIAL_PATH is not set or does not exist.", file=sys.stderr)
        return 2

    repo_root = human_root if (human_root / ".git").exists() else find_repo_root(human_root)
    cfg = load_config(repo_root)
    repos_dir = resolve_config_path(repo_root, cfg, key="repos_dir", default_rel=".references/repos")
    clone_path = _ensure_clone(args.repo, repos_dir, update=bool(args.update))

    repo_slug = _slugify(args.slug or clone_path.name)
    session = _slugify(args.session or (_dt.date.today().strftime("%Y%m%d") + "-hands-on"))

    base = repo_root / "research" / repo_slug / "hands_on" / session
    scripts_dir = base / "scripts"
    results_dir = base / "results"
    reports_dir = base / "reports"

    for d in [scripts_dir, results_dir, reports_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # Copy a session skeleton (reports + scripts + .gitignore) without overwriting existing files.
    skill_dir = Path(__file__).resolve().parents[1]
    skeleton_dir = skill_dir / "assets" / "session_skeleton"
    _copy_skeleton(skeleton_dir, base)

    # Fill common report files if they are still uninitialized skeleton templates.
    head = _run_capture(["git", "-C", str(clone_path), "rev-parse", "HEAD"]).splitlines()[0] if (clone_path / ".git").exists() else ""
    sha_short = head[:12] if head else ""

    index_path = reports_dir / "INDEX.md"
    if index_path.exists() and _file_contains_any(index_path, ["{session_name}", "{repo_url_or_path}"]):
        index_md = "\n".join(
            [
                "# Hands-on session index",
                "",
                f"**Session:** `{session}`",
                f"**Repo spec:** {args.repo}",
                f"**Local clone:** {clone_path}",
                f"**Commit:** {sha_short or 'unknown'}",
                "",
                "## Entry points",
                "",
                "- Repo analysis: `../../repo_analysis.md`",
                "- Environment: `environment.md`",
                "- Plan: `plan.md`",
                "- Report: `report.md`",
                "",
                "## What to look at first",
                "",
                "1) `report.md` (what actually happened)",
                "2) `environment.md` (is the setup credible?)",
                "3) `plan.md` (what was intended?)",
                "4) `results/` logs and traces (raw evidence; gitignored)",
                "",
            ]
        )
        _write_text_overwrite(index_path, index_md)

    env_md = "\n".join(
        [
            "# Environment",
            "",
            f"**Captured:** {_dt.datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}",
            f"**Repo spec:** {args.repo}",
            f"**Local clone:** {clone_path}",
            f"**Commit:** {sha_short or 'unknown'}",
            "",
            "## System",
            "",
            "```text",
            _run_capture(["uname", "-a"]),
            "```",
            "",
            "## GPU (if available)",
            "",
            "```text",
            _run_capture(["nvidia-smi"]),
            "```",
            "",
            "## Tooling",
            "",
            "```text",
            "python: " + _run_capture([sys.executable, "--version"]),
            "git: " + _run_capture(["git", "--version"]),
            "```",
            "",
            "## Notes",
            "",
            "- This file is a quick snapshot created by the init script.",
            "- For a more complete capture (including pip freeze), run: `bash scripts/capture_environment.sh`",
            "- Raw evidence should live under `results/` (gitignored).",
            "",
        ]
    )
    env_path = reports_dir / "environment.md"
    if (not env_path.exists()) or _file_contains_any(env_path, ["{repo_url_or_path}", "{git_sha_or_tag}"]):
        _write_text_overwrite(env_path, env_md)

    plan_md = "\n".join(
        [
            "# Experiment plan",
            "",
            "Link to repo analysis: `../../repo_analysis.md`.",
            "",
            "## Goal (one sentence)",
            "",
            "TODO",
            "",
            "## Hypotheses",
            "",
            "- TODO: Write 1–3 falsifiable hypotheses (what you expect and why).",
            "",
            "## Workload matrix",
            "",
            "| Workload | Batch | Seq len | Dtype | Notes |",
            "| --- | --- | --- | --- | --- |",
            "| prefill | 1 | 1024 in / 1 out | fp16 | cold vs warm |",
            "| decode | 16 | 128 in / 32 out | fp16 | kv_len sweep |",
            "",
            "## Metrics",
            "",
            "- latency (p50/p95)",
            "- throughput (tokens/s or samples/s)",
            "- memory (GB), KV cache usage",
            "",
            "## Baselines",
            "",
            "- Baseline A: smallest known-good example from the repo/docs.",
            "- Baseline B: a tiny ungated model or microbench for fast iteration.",
            "",
            "## How to run",
            "",
            "Record exact commands and save logs under `results/`.",
            "",
        ]
    )
    plan_path = reports_dir / "plan.md"
    if (not plan_path.exists()) or _file_contains_any(plan_path, ["{goal}", "{hypothesis_1}"]):
        _write_text_overwrite(plan_path, plan_md)

    report_md = "\n".join(
        [
            "# Hands-on report",
            "",
            "## What I ran",
            "",
            "| Date | Command | Result summary | Evidence |",
            "| --- | --- | --- | --- |",
            f"| {_dt.date.today().isoformat()} | TODO | TODO | `results/` |",
            "",
            "## Observations",
            "",
            "- TODO: Write event-level observations tied to evidence (log lines, trace files, metrics).",
            "",
            "## Next steps",
            "",
            "- TODO: Add 3–5 concrete next steps (each with a command or file:line pointer).",
            "",
        ]
    )
    report_path = reports_dir / "report.md"
    if (not report_path.exists()) or _file_contains_any(report_path, ["{command}", "{observation_1}"]):
        _write_text_overwrite(report_path, report_md)

    print(f"CLONE={clone_path}")
    print(f"SESSION={base}")
    print(f"ENV={reports_dir / 'environment.md'}")
    print(f"PLAN={reports_dir / 'plan.md'}")
    print(f"REPORT={reports_dir / 'report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
