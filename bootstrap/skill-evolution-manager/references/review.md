# Review checklist (skill evolution)

Use this before claiming an evolution is applied.

## Canonical (PKB_PATH)

- The canonical `SKILL.md` was updated (not `skills/`).
- The skill has exactly one bounded Learned section:
  - `<!-- PKB:EVOLUTION:BEGIN -->`
  - `<!-- PKB:EVOLUTION:END -->`
- `evolution.json` is valid JSON and contains only schema fields.
- No placeholders like `<...>` remain.
- `python bootstrap/scripts/update_skills_mirror.py all` was run (so `skills/` mirror reflects the change).

## Local installs (best-effort)

- Updated only existing installs; did not install “for all agents”.
- If no installs were found, reported that explicitly.

