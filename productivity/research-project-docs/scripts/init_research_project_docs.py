#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path


def _copy_tree(src: Path, dst: Path, *, force: bool) -> None:
    for root, dirs, files in os.walk(src):
        rel = Path(root).relative_to(src)
        target_dir = dst / rel
        target_dir.mkdir(parents=True, exist_ok=True)

        for d in dirs:
            (target_dir / d).mkdir(parents=True, exist_ok=True)

        for f in files:
            src_file = Path(root) / f
            dst_file = target_dir / f
            if dst_file.exists() and not force:
                continue
            shutil.copy2(src_file, dst_file)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scaffold research-project documentation structure into a target repo."
    )
    parser.add_argument(
        "--project-root",
        required=True,
        help="Path to the target research repo (will be created if missing).",
    )
    parser.add_argument(
        "--docs-root",
        default="docs",
        help="Docs root path relative to project root (default: docs). Use '.' for repo root.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files.",
    )
    args = parser.parse_args()

    project_root = Path(args.project_root).expanduser().resolve()
    docs_root_rel = Path(args.docs_root)
    docs_root = (project_root / docs_root_rel).resolve()

    project_root.mkdir(parents=True, exist_ok=True)
    docs_root.mkdir(parents=True, exist_ok=True)

    skill_dir = Path(__file__).resolve().parents[1]
    template_dir = skill_dir / "assets" / "template"
    if not template_dir.exists():
        raise SystemExit(f"Template dir not found: {template_dir}")

    _copy_tree(template_dir, docs_root, force=args.force)

    print(f"Scaffolded research docs into: {docs_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

