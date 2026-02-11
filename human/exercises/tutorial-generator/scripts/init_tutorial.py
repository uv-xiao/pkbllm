#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as _dt
import re
import sys
from pathlib import Path
from typing import Optional

from pkbllm_config import find_repo_root, resolve_human_material_root


_NON_SLUG = re.compile(r"[^a-z0-9]+")


def _slugify(value: str) -> str:
    v = value.strip().lower()
    v = v.replace("_", "-")
    v = _NON_SLUG.sub("-", v).strip("-")
    return v or "topic"


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Initialize a tutorial under $HUMAN_MATERIAL_PATH/exercises/tutorials/.")
    p.add_argument("--topic", required=True, help="Tutorial topic slug/title (e.g. 'vllm-internals').")
    p.add_argument("--chapter", default="intro", help="First chapter name (default: intro).")
    args = p.parse_args(argv)

    human_root = resolve_human_material_root()
    if not human_root:
        print("HUMAN_MATERIAL_PATH is not set or does not exist.", file=sys.stderr)
        return 2

    repo_root = human_root if (human_root / ".git").exists() else find_repo_root(human_root)

    topic = _slugify(args.topic)
    chapter = "01_" + _slugify(args.chapter)
    base = repo_root / "exercises" / "tutorials" / topic
    chapter_dir = base / "chapters" / chapter

    (chapter_dir / "examples").mkdir(parents=True, exist_ok=True)
    (chapter_dir / "exercises").mkdir(parents=True, exist_ok=True)

    readme = "\n".join(
        [
            f"# Tutorial: {args.topic}",
            "",
            f"**Created:** {_dt.date.today().isoformat()}",
            "",
            "## Prerequisites",
            "",
            "- Python 3.10+.",
            "- Any project-specific deps (fill these in).",
            "",
            "## Learning path",
            "",
            f"- `chapters/{chapter}/README.md` — first chapter",
            "",
            "## References",
            "",
            "- Repo analysis (recommended): TODO: link to the repo analysis you used.",
            "- Hands-on evidence (recommended): TODO: link to the hands-on session report and evidence you used.",
            "",
        ]
    )
    _write_text(base / "README.md", readme)

    chapter_readme = "\n".join(
        [
            f"# 01 — {args.chapter}",
            "",
            "## Objectives",
            "",
            "- TODO: Add 2–4 concrete learning objectives.",
            "",
            "## Conceptual model",
            "",
            "```mermaid",
            "flowchart LR",
            "  A[Input] --> B[Core idea] --> C[Output]",
            "```",
            "",
            "## Code tour",
            "",
            "- `path/to/file.py:123` — TODO: what to read",
            "",
            "## Runnable example",
            "",
            "Command:",
            "",
            "```bash",
            "python examples/your_example.py",
            "```",
            "",
            "Expected output (captured from a real run):",
            "",
            "```text",
            "TODO",
            "```",
            "",
            "## Exercises",
            "",
            "1) TODO: exercise prompt",
            "2) TODO: exercise prompt",
            "",
        ]
    )
    _write_text(chapter_dir / "README.md", chapter_readme)

    print(f"TUTORIAL={base}")
    print(f"CHAPTER={chapter_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
