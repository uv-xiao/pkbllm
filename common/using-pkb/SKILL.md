---
name: uv-using-pkb
description: "Use pkbllm skills effectively. Use at the start of a session when working from a pkbllm repo checkout: discover which `uv-*` skill to invoke, understand the canonical-vs-generated layout (don’t edit `skills/`), install/list skills via Skills-CLI, and follow HUMAN_MATERIAL_PATH conventions (slides/research/exercises plus .references/ downloads with config.toml overrides)."
---

# Using pkbllm skills

## The rule

If there is any reasonable chance a `uv-*` skill applies, invoke it before doing work. Prefer the most specific skill over a generic one.

## Find skills (fast)

- List installed skills (Skills-CLI):

```bash
npx -y skills add . --list
```

- Browse the pkbllm index:
  - `skills/manifest.json` (generated; good for searching)
  - `README.md` tables under `knowledge/`, `productivity/`, `human/`, `bootstrap/`

- Search by keyword:

```bash
rg -n "name:\\s+uv-|description:" -S knowledge productivity human bootstrap
```

## Canonical vs generated

- **Canonical sources of truth**: `knowledge/`, `productivity/`, `human/`, `bootstrap/`
- **Generated mirror**: `skills/` (do not edit)

If you changed canonical skills, regenerate:

```bash
python bootstrap/scripts/update_skills_mirror.py all
```

## HUMAN_MATERIAL_PATH conventions

If the task is “human-facing” (slides, paper reports, exercise packs):

1) Initialize a materials repo (once):

- Use `uv-init-human-material-repo`

2) Put **tracked outputs** here:

- `$HUMAN_MATERIAL_PATH/slides/…`
- `$HUMAN_MATERIAL_PATH/research/…`
- `$HUMAN_MATERIAL_PATH/exercises/…`

3) Put **downloads/clones** (gitignored) here:

- `$HUMAN_MATERIAL_PATH/.references/`

Default layout:
- `.references/pdfs/`
- `.references/arxiv/`
- `.references/repos/`

Override paths (repo overrides user):
- `$HUMAN_MATERIAL_PATH/.agents/config.toml`
- `~/.agents/config.toml`

## Naming

All skills in pkbllm use the `uv-` prefix in `SKILL.md` frontmatter `name:`. Use that exact name when referencing a skill.

