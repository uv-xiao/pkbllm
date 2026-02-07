#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path
from typing import Optional

import os


def _slugify(value: str) -> str:
    s = value.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "paper"


def _rmtree(path: Path) -> None:
    if not path.exists():
        return
    if path.is_file() or path.is_symlink():
        path.unlink()
        return
    shutil.rmtree(path)


def _copy_pack(template_root: Path, dest_root: Path, *, slug: str) -> None:
    if dest_root.exists():
        raise FileExistsError(str(dest_root))
    shutil.copytree(template_root, dest_root)

    # Turn skill templates into real local skills and fill placeholders.
    for templ in dest_root.rglob("SKILL.template.md"):
        skill_md = templ.with_name("SKILL.md")
        templ.rename(skill_md)

    for skill_md in dest_root.rglob("SKILL.md"):
        try:
            text = skill_md.read_text(encoding="utf-8")
        except Exception:
            continue
        updated = text.replace("<paper_slug>", slug)
        if updated != text:
            skill_md.write_text(updated, encoding="utf-8")


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Scaffold an exercise pack under $HUMAN_MATERIAL_PATH/exercises/<slug>/")
    p.add_argument("--slug", required=True, help="Pack slug (e.g. 'attention-is-all-you-need')")
    p.add_argument("--human-material-path", help="Override HUMAN_MATERIAL_PATH")
    p.add_argument("--overwrite", action="store_true", help="Overwrite existing pack folder if present")
    args = p.parse_args(argv)

    raw_root = args.human_material_path or os.getenv("HUMAN_MATERIAL_PATH")
    if not raw_root:
        print("Missing --human-material-path and HUMAN_MATERIAL_PATH is not set.", file=sys.stderr)
        return 2
    human_root = Path(raw_root).expanduser().resolve()

    slug = _slugify(args.slug)

    template_root = Path(__file__).resolve().parent.parent / "assets" / "pack"
    if not template_root.exists():
        print(f"Missing template pack at: {template_root}", file=sys.stderr)
        return 2

    dest_root = human_root / "exercises" / slug
    if dest_root.exists():
        if not args.overwrite:
            print(f"Destination exists: {dest_root}. Use --overwrite to replace.", file=sys.stderr)
            return 2
        _rmtree(dest_root)

    dest_root.parent.mkdir(parents=True, exist_ok=True)
    _copy_pack(template_root, dest_root, slug=slug)

    print(str(dest_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
