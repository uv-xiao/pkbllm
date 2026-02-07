#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[3]


_SAFE_DIR_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def _validate_dir_name(value: str) -> str:
    v = value.strip()
    if not _SAFE_DIR_RE.match(v):
        raise ValueError(f"Invalid --dir {value!r}. Use [a-z0-9._-] only.")
    return v


def _validate_skill_name(value: str) -> str:
    v = value.strip()
    if not v.startswith("uv-"):
        raise ValueError("Skill frontmatter name must start with 'uv-'.")
    if any(ch.isspace() for ch in v):
        raise ValueError("Skill name must not contain whitespace.")
    return v


def _write(path: Path, content: str, *, overwrite: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        raise FileExistsError(str(path))
    path.write_text(content, encoding="utf-8")


def _skill_md(*, name: str, description: str, title: str) -> str:
    desc = description.strip().replace("\n", " ").strip()
    return (
        "---\n"
        f"name: {name}\n"
        f'description: "{desc}"\n'
        "---\n\n"
        f"# {title}\n\n"
        "## Quick start\n\n"
        "- TODO: add a minimal command or code snippet\n\n"
        "## When to use\n\n"
        "- TODO: add trigger phrases and contexts\n\n"
        "## Core concepts\n\n"
        "- TODO\n\n"
        "## Workflows\n\n"
        "- TODO\n\n"
        "## Pitfalls\n\n"
        "- TODO\n"
    )


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Scaffold a new `knowledge/ML/*` skill directory.")
    p.add_argument(
        "--category",
        required=True,
        choices=["model-architecture", "training", "distributed", "serving", "paper", "kernel", "agents"],
        help="Top-level ML category under knowledge/ML/.",
    )
    p.add_argument("--dir", required=True, help="Directory name under the category (e.g. flashinfer, triton).")
    p.add_argument("--name", required=True, help="Skill frontmatter name (must start with uv-).")
    p.add_argument("--description", required=True, help="Skill frontmatter description (include when-to-use triggers).")
    p.add_argument("--title", help="H1 title for the SKILL.md (defaults to --dir).")
    p.add_argument("--with-references", action="store_true", help="Create references/ directory.")
    p.add_argument("--with-scripts", action="store_true", help="Create scripts/ directory.")
    p.add_argument("--with-assets", action="store_true", help="Create assets/ directory.")
    p.add_argument("--overwrite", action="store_true", help="Overwrite SKILL.md if it already exists.")
    p.add_argument("--dry-run", action="store_true", help="Print paths that would be created without writing.")
    args = p.parse_args(argv)

    dir_name = _validate_dir_name(args.dir)
    skill_name = _validate_skill_name(args.name)
    title = (args.title or dir_name).strip()

    skill_dir = ROOT / "knowledge" / "ML" / args.category / dir_name
    skill_md = skill_dir / "SKILL.md"

    to_create: list[Path] = [skill_md]
    if args.with_references:
        to_create.append(skill_dir / "references" / ".keep")
    if args.with_scripts:
        to_create.append(skill_dir / "scripts" / ".keep")
    if args.with_assets:
        to_create.append(skill_dir / "assets" / ".keep")

    if args.dry_run:
        for path in to_create:
            print(str(path))
        return 0

    _write(skill_md, _skill_md(name=skill_name, description=args.description, title=title), overwrite=bool(args.overwrite))

    for path in to_create[1:]:
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text("", encoding="utf-8")

    print(str(skill_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
