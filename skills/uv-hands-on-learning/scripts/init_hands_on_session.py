#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as _dt
import re
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
        return f"<unavailable: {e}>"


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(content, encoding="utf-8")


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

    env_md = "\n".join(
        [
            "# Environment",
            "",
            f"**Date:** {_dt.date.today().isoformat()}",
            f"**Repo spec:** {args.repo}",
            f"**Local clone:** {clone_path}",
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
        ]
    )
    _write_text(reports_dir / "environment.md", env_md)

    plan_md = "\n".join(
        [
            "# Experiment plan",
            "",
            "Link to repo analysis: `../repo_analysis.md` (one level up).",
            "",
            "## Hypotheses",
            "",
            "- <what do you expect to be the bottleneck and why?>",
            "",
            "## Workload matrix",
            "",
            "| Workload | Batch | Seq len | Dtype | Notes |",
            "| --- | --- | --- | --- | --- |",
            "| <name> | <b> | <s> | <bf16/fp16/...> | <notes> |",
            "",
            "## Metrics",
            "",
            "- latency (p50/p95)",
            "- throughput (tokens/s or samples/s)",
            "- memory (GB), KV cache usage",
            "",
            "## Baselines",
            "",
            "- <baseline 1>",
            "",
            "## How to run",
            "",
            "Record exact commands and save logs under `results/`.",
            "",
        ]
    )
    _write_text(reports_dir / "plan.md", plan_md)

    report_md = "\n".join(
        [
            "# Hands-on report",
            "",
            "## What I ran",
            "",
            "| Date | Command | Result summary | Evidence |",
            "| --- | --- | --- | --- |",
            "| <YYYY-MM-DD> | <cmd> | <summary> | `results/<file>` |",
            "",
            "## Observations",
            "",
            "- <event-level observations>",
            "",
            "## Next steps",
            "",
            "- <next step>",
            "",
        ]
    )
    _write_text(reports_dir / "report.md", report_md)

    print(f"CLONE={clone_path}")
    print(f"SESSION={base}")
    print(f"ENV={reports_dir / 'environment.md'}")
    print(f"PLAN={reports_dir / 'plan.md'}")
    print(f"REPORT={reports_dir / 'report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

