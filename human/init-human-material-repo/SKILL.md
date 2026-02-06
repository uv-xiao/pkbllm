---
name: init-human-material-repo
description: "Initialize a dedicated HUMAN_MATERIAL_PATH git repository for generated human-facing materials. Use when a user asks to set up a new materials repo/folder for slides/manuscripts/exercises, create the expected file structure under $HUMAN_MATERIAL_PATH, and create a local-only .OPENROUTER_API_KEY file for slider rendering."
---

# Initialize a HUMAN_MATERIAL_PATH repo

Run the initializer script to create a git repo and the expected directory structure.

## Command

Prefer passing an explicit path; otherwise rely on `HUMAN_MATERIAL_PATH`.

```bash
python human/init-human-material-repo/scripts/init_human_material_repo.py --path /abs/path/to/human-materials
```

Or:

```bash
HUMAN_MATERIAL_PATH=/abs/path/to/human-materials python human/init-human-material-repo/scripts/init_human_material_repo.py
```

## What it creates

- Git repo at the target path (if not already a git repo)
- `slides/` workspace:
  - `slides/styles/*.md` (minimal style briefs)
  - `slides/README.md` describing per-deck structure:
    - `slides/<deck>/materials/`
    - `slides/<deck>/configs/deck.yaml`
    - `slides/<deck>/prompts/{content,styled}/`
    - `slides/<deck>/artifacts/<deck>/...`
- `manuscripts/`, `exercises/`
- `.OPENROUTER_API_KEY` (created but gitignored)
- `.OPENROUTER_API_KEY.example` (tracked)
- `.gitignore` with safe defaults (secrets + bulky intermediates)

