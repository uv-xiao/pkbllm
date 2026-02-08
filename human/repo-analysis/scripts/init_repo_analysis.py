#!/usr/bin/env python3
from __future__ import annotations

import argparse
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
    return v or "repo"


def _repo_name_from_url(url: str) -> str:
    tail = url.rstrip("/").split("/")[-1]
    if tail.endswith(".git"):
        tail = tail[:-4]
    return tail


def _ensure_clone(repo_spec: str, repos_dir: Path, *, update: bool) -> tuple[Path, str]:
    """
    Returns (clone_path, display_name).
    """
    if Path(repo_spec).expanduser().exists():
        p = Path(repo_spec).expanduser().resolve()
        return p, p.name

    name = _repo_name_from_url(repo_spec)
    slug = _slugify(name)
    clone_path = repos_dir / slug
    clone_path.parent.mkdir(parents=True, exist_ok=True)

    if clone_path.exists() and (clone_path / ".git").exists():
        if update:
            subprocess.run(["git", "-C", str(clone_path), "fetch", "--all", "--prune"], check=False)
        return clone_path, name

    subprocess.run(["git", "clone", "--depth", "1", repo_spec, str(clone_path)], check=True)
    return clone_path, name


def _git_head_sha(repo_path: Path) -> str:
    try:
        out = subprocess.check_output(["git", "-C", str(repo_path), "rev-parse", "HEAD"], text=True).strip()
        return out[:12]
    except Exception:
        return "unknown"


def _write_report_from_template(report_path: Path, *, repo_name: str, repo_spec: str, clone_path: Path, sha: str) -> None:
    template_path = Path(__file__).resolve().parents[1] / "assets" / "repo_analysis_template.md"
    text = template_path.read_text(encoding="utf-8")
    text = text.replace("<repo name>", repo_name)
    text = text.replace("<url>", repo_spec)
    text = text.replace("<path>", str(clone_path))
    text = text.replace("<sha>", sha)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    if not report_path.exists():
        report_path.write_text(text, encoding="utf-8")


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Initialize a pkbllm repo-analysis workspace under $HUMAN_MATERIAL_PATH.")
    p.add_argument("repo", help="Repo URL (git clone) or local path")
    p.add_argument("--slug", help="Override repo slug used under $HUMAN_MATERIAL_PATH/research/<slug>/")
    p.add_argument("--update", action="store_true", help="If already cloned, fetch updates (best effort).")
    args = p.parse_args(argv)

    human_root = resolve_human_material_root()
    if not human_root:
        print("HUMAN_MATERIAL_PATH is not set or does not exist.", file=sys.stderr)
        return 2

    repo_root = human_root if (human_root / ".git").exists() else find_repo_root(human_root)
    cfg = load_config(repo_root)

    repos_dir = resolve_config_path(repo_root, cfg, key="repos_dir", default_rel=".references/repos")
    clone_path, display_name = _ensure_clone(args.repo, repos_dir, update=bool(args.update))

    repo_slug = _slugify(args.slug or clone_path.name or display_name)
    out_dir = repo_root / "research" / repo_slug
    report_path = out_dir / "repo_analysis.md"

    sha = _git_head_sha(clone_path)
    _write_report_from_template(report_path, repo_name=display_name, repo_spec=args.repo, clone_path=clone_path, sha=sha)

    print(f"CLONE={clone_path}")
    print(f"REPORT={report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

