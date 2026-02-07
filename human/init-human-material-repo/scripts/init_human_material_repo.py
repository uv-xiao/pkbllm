#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path


def _write_text(path: Path, content: str, *, overwrite: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        return
    path.write_text(content, encoding="utf-8")


def _ensure_git_repo(root: Path) -> None:
    if (root / ".git").exists():
        return
    subprocess.run(["git", "init", str(root)], check=True)


def _default_gitignore() -> str:
    return """# Secrets
.OPENROUTER_API_KEY

# Python
__pycache__/
*.pyc

# macOS
.DS_Store

# Local references (downloads, zips, clones)
.references/*
!.references/README.md

# Slides: bulky intermediates
slides/**/artifacts/**/work*/
slides/**/artifacts/**/downloads/
slides/**/artifacts/**/rasterized/

"""


def _default_config_toml() -> str:
    return """[pkbllm]
# Paths are relative to the HUMAN_MATERIAL_PATH repo root unless absolute.
pdfs_dir = ".references/pdfs"
arxiv_dir = ".references/arxiv"
repos_dir = ".references/repos"

# OpenRouter API key file. Supported formats:
# - raw key string
# - a single line: OPENROUTER_API_KEY=...
openrouter_api_key_file = ".OPENROUTER_API_KEY"
"""


def _slides_readme() -> str:
    return """# Slides workspace

This folder holds slide decks created with the pkbllm slider skills.

## Expected deck structure

For a deck named `<deck>`, use:

- `slides/<deck>/materials/` — input notes, images, source files
- `slides/<deck>/configs/deck.yaml` — optional preferences (audience, language, style, etc.)
- `slides/<deck>/prompts/content/<deck>.md` — Content PROMPT (planning)
- `slides/<deck>/prompts/styled/<deck>.md` — Styled PROMPT (layout + styling)
- `slides/<deck>/artifacts/<deck>/work/` — intermediates (PNG slides, logs)
- `slides/<deck>/artifacts/<deck>/<deck>.pdf` — rendered PDF
- `slides/<deck>/artifacts/<deck>/<deck>.pptx` — image-based PPTX

## Styles

Minimal style briefs live under `slides/styles/`.

"""


def _style_blueprint() -> str:
    return """# blueprint

A clean default style for technical decks.

- Background: light, subtle texture allowed but keep high contrast.
- Typography: sans-serif, readable. Strong hierarchy (title > subtitle > body).
- Layout: generous margins, consistent alignment, avoid dense paragraphs.
- Color: one accent color for emphasis; avoid rainbow palettes.
- Components: rounded callouts, simple icons, thin arrows.

"""


def _style_chalkboard() -> str:
    return """# chalkboard

A hand-drawn chalkboard vibe.

- Background: dark slate / chalkboard texture.
- Typography: chalk-like handwritten feel; keep body text large.
- Layout: simple regions; avoid tiny details.
- Color: off-white as primary; 1–2 chalk accent colors.
- Components: sketchy boxes/arrows, marker highlights.

"""


def _style_sketch_notes() -> str:
    return """# sketch-notes

A sketch-notes / whiteboard style.

- Background: white paper, light grid optional.
- Typography: mix of clean sans-serif + hand-drawn labels.
- Layout: icons and diagrams with short labels; avoid long text blocks.
- Color: black lines + 1 accent marker color.
- Components: hand-drawn containers, arrows, simple pictograms.

"""


def _deck_template_yaml() -> str:
    return """# Deck preferences (optional)
# Example:
# audience: "ML engineers"
# language: "en"
# style: "blueprint"
# dimensions:
#   mood: "neutral"
#   density: "medium"

"""


def init_repo(root: Path, *, overwrite: bool) -> None:
    root.mkdir(parents=True, exist_ok=True)
    _ensure_git_repo(root)

    _write_text(root / ".gitignore", _default_gitignore(), overwrite=overwrite)
    _write_text(
        root / ".OPENROUTER_API_KEY",
        "",
        overwrite=False,
    )
    _write_text(
        root / ".OPENROUTER_API_KEY.example",
        "OPENROUTER_API_KEY=put-your-key-here\n",
        overwrite=overwrite,
    )

    (root / ".references").mkdir(parents=True, exist_ok=True)
    (root / ".references" / "pdfs").mkdir(parents=True, exist_ok=True)
    (root / ".references" / "arxiv").mkdir(parents=True, exist_ok=True)
    (root / ".references" / "repos").mkdir(parents=True, exist_ok=True)
    _write_text(
        root / ".references" / "README.md",
        """# Local references (gitignored)

Put downloaded PDFs, arXiv source zips, cloned repos, and other large/local reference artifacts here.

Suggested layout:

- `.references/pdfs/` (PDFs)
- `.references/arxiv/` (source zips / extracted sources)
- `.references/repos/` (cloned code repos)

""",
        overwrite=overwrite,
    )

    (root / ".agents").mkdir(parents=True, exist_ok=True)
    _write_text(root / ".agents" / "config.toml", _default_config_toml(), overwrite=overwrite)

    # Top-level folders
    for d in ["slides", "manuscripts", "exercises"]:
        (root / d).mkdir(parents=True, exist_ok=True)

    # Slides structure
    _write_text(root / "slides" / "README.md", _slides_readme(), overwrite=overwrite)
    (root / "slides" / "styles").mkdir(parents=True, exist_ok=True)
    _write_text(root / "slides" / "styles" / "blueprint.md", _style_blueprint(), overwrite=overwrite)
    _write_text(root / "slides" / "styles" / "chalkboard.md", _style_chalkboard(), overwrite=overwrite)
    _write_text(root / "slides" / "styles" / "sketch-notes.md", _style_sketch_notes(), overwrite=overwrite)

    # Provide a deck template folder as an example (non-deck-specific).
    template = root / "slides" / "_template"
    for d in ["materials", "prompts/content", "prompts/styled", "artifacts", "configs"]:
        (template / d).mkdir(parents=True, exist_ok=True)
    _write_text(template / "configs" / "deck.yaml", _deck_template_yaml(), overwrite=overwrite)


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a HUMAN_MATERIAL_PATH git repo.")
    parser.add_argument(
        "--path",
        help="Target path for the human materials repo. Defaults to $HUMAN_MATERIAL_PATH.",
    )
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing template files.")
    args = parser.parse_args()

    target = args.path or os.getenv("HUMAN_MATERIAL_PATH")
    if not target:
        raise SystemExit("Missing --path and HUMAN_MATERIAL_PATH is not set.")

    root = Path(target).expanduser().resolve()
    init_repo(root, overwrite=bool(args.overwrite))
    print(str(root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
