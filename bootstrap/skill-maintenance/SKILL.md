---
name: uv-bootstrap-skill-maintenance
description: "Maintain and curate the pkbllm skills repository. Use when adding/importing a new skill, merging skills from external repos, updating or refactoring existing skills, regenerating the generated `skills/` mirror, or ensuring licensing/compliance and naming conventions (all skills must start with `uv-`)."
---

# Skill repo maintenance (pkbllm)

## Source of truth

- Treat canonical skill folders under `knowledge/`, `productivity/`, `human/`, `bootstrap/` as the source of truth.
- Treat `skills/` as generated output (mirror). Never edit `skills/` by hand.

## Add or import a skill (from another repo)

1. **Clone reference repos under `.references/`** (for one-time study and provenance). Never depend on `.references/` at runtime.
2. **Copy only what you need** into canonical folders, then adapt it for pkbllm:
   - Remove upstream extras inside skills (e.g. `README.md`, `QUICK_REFERENCE.md`, ad-hoc test files) unless truly required.
   - Keep skills self-contained: `SKILL.md` + optional `scripts/`, `references/`, `assets/`.
3. **Rename the skill**:
   - `SKILL.md` frontmatter `name:` must start with `uv-`.
   - Choose names for discoverability and to avoid collisions (use verbs when possible).
4. **Make it work in pkbllm conventions**:
   - If a skill targets the HUMAN materials repo, use `$HUMAN_MATERIAL_PATH` and store bulky artifacts under `.references/` (gitignored) and tracked outputs under `research/`, `slides/`, `manuscripts/`, `exercises/`.
   - Prefer the pkbllm config precedence:
     - `$HUMAN_MATERIAL_PATH/.agents/config.toml` (repo override)
     - `~/.agents/config.toml` (user default)
5. **Handle licensing**:
   - Check upstream `LICENSE` / notices in `.references/…`.
   - If the upstream material is not distributable, do not import it.
   - Add an entry to `THIRD_PARTY_NOTICES.md` describing what was taken and the license.
   - If helpful, record a `license:` field in the imported skill frontmatter (e.g. `MIT`, `Apache-2.0`).

## Regenerate the mirror and README tables

After changing canonical skills, run:

```bash
python bootstrap/scripts/update_skills_mirror.py all
```

This regenerates:
- `skills/` (mirrored skills, slugs derived from frontmatter `name`)
- `skills/manifest.json`
- `README.md` `<TABLE>` sections across the repo (excluding `.references/` and `docs/`)

## Quick checks before committing

- `python -m compileall -q <changed_script_paths>`
- `npx -y skills add . --list` (should report a skill count and not error)
- Ensure no generated artifacts accidentally got committed (especially under any `.references/`).

