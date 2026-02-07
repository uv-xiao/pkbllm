# Agent notes for this repo

## Canonical vs distribution

- Canonical (curated) skill sources live under `common/`, `knowledge/`, `productivity/`, `human/`, and `bootstrap/`.
- `skills/` is a generated mirror intended for `npx skills` consumers.
- Do not hand-edit `skills/`; update the canonical skill and re-run:
  - `python bootstrap/scripts/update_skills_mirror.py all`

## Naming conventions

- All skills in this repo must have `SKILL.md` frontmatter `name:` starting with `uv-`.

## HUMAN_MATERIAL_PATH conventions

If a skill targets the human materials repo:

- Tracked outputs go under `$HUMAN_MATERIAL_PATH/` (typically `slides/`, `research/`, `manuscripts/`, `exercises/`).
- Downloads/clones go under `$HUMAN_MATERIAL_PATH/.references/` (gitignored).
- Config precedence (repo overrides user):
  - `$HUMAN_MATERIAL_PATH/.agents/config.toml`
  - `~/.agents/config.toml`

## References (one-time bootstrap)

`.references/` may hold cloned upstream repositories used for one-time import/bootstrapping.

- `.references/` is ignored by git (except `.references/README.md`).
- There is intentionally no maintained “sync from references” script; skills evolve in this repo.

## Licensing

When importing/adapting from upstream repos, update `THIRD_PARTY_NOTICES.md` and ensure the material is distributable.
