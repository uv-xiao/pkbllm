# Agent notes for this repo

## Canonical vs distribution

- Canonical (curated) skill sources live under `knowledge/`, `productivity/`, `human/`, and `bootstrap/`.
- `skills/` is a generated mirror intended for `npx skills` consumers.
- Do not hand-edit `skills/`; update the canonical skill and re-run:
  - `python bootstrap/scripts/update_skills_mirror.py all`

## References (one-time bootstrap)

`.references/` may hold cloned upstream repositories used for one-time import/bootstrapping.

- `.references/` is ignored by git (except `.references/README.md`).
- There is intentionally no maintained “sync from references” script; skills evolve in this repo.
