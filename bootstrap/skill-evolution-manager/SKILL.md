---
name: uv-skill-evolution-manager
description: "Evolve skills safely from real session feedback by persisting structured learnings (`evolution.json`) and stitching an idempotent 'Learned' section into `SKILL.md`. Supports updating both PKB_PATH canonical skills and any local installed skill copies (best-effort) without installing for all agents."
license: MIT
---

# Skill evolution manager (pkbllm)

This skill helps you continuously improve skills based on real sessions, without losing fixes when skills are updated.

It does this by:
1) extracting structured learnings into `evolution.json`, and
2) stitching those learnings into a bounded section in `SKILL.md` (idempotent re-apply).

This is adapted from `KKKKhazix/Khazix-Skills` (MIT) and made pkbllm-compatible.

## Canonical vs installed (pkbllm rules)

- **Canonical source of truth (PKB_PATH)** lives under: `bootstrap/`, `common/`, `human/`, `knowledge/`, `productivity/`.
- `skills/` is **generated**. Never edit it by hand.
- Local skill installs (e.g. a project `.agents/skills` or `~/.codex/skills`) are not canonical and are often gitignored.

If you evolve canonical skills, regenerate mirrors:

```bash
python bootstrap/scripts/update_skills_mirror.py all
```

## Non-negotiables (requirements)

- **Evidence-first**: only add learnings supported by the session (errors, user feedback, successful commands).
- **No arbitrary prompt injection**: store structured constraints, pitfalls, and verification steps (see schema).
- **Idempotent**: repeated stitching must not duplicate content.
- **No “install for all agents”**: update existing local installs if found; do not install globally unless explicitly requested.
- **Never edit `skills/` by hand**: only update canonical + regenerate.

## Data model (`evolution.json`)

Each evolved skill keeps a sibling file:

```
<skill_dir>/
├── SKILL.md
└── evolution.json
```

Schema (see `assets/evolution.schema.json`):
- `preferences`: user preferences / defaults
- `fixes`: concrete fixes (platform quirks, known issues)
- `pitfalls`: common mistakes to avoid
- `verification`: commands/checks to run before claiming success
- `examples`: short “worked examples” (command + expected snippet)

## Workflow (the evolution loop)

### 1) Review the session

For each invoked skill:
- What worked?
- What failed? (exact error)
- What did the user request as a preference?
- What verification would have caught the issue earlier?

### 2) Extract structured learnings

Produce a JSON object matching the schema. Keep each item short, specific, and testable when possible.

### 3) Apply + stitch (canonical and/or local)

Apply to a single skill name:

```bash
python scripts/apply_evolution.py --skill-name uv-hands-on-learning --scope both --json '{"pitfalls":["Always keep raw logs under results/ (gitignored) and copy only small excerpts into evidence/."], "verification":["Confirm no tracked files under any hands_on/**/results/." ]}'
```

Scopes:
- `pkb`: update canonical skill under `PKB_PATH` (or inferred repo root)
- `local`: update locally installed copies (default: project scope + `~/.codex/skills`)
- `both`: do both

### 4) Align after updates

When skills are updated/refactored, re-stitch to re-apply the learned section:

```bash
python scripts/align_all.py --scope pkb
python scripts/align_all.py --scope local
```

## Review policy (must follow)

Before saying “evolution applied”:
- The target `SKILL.md` contains a single Learned section bounded by markers.
- `evolution.json` is valid JSON and contains only schema fields.
- Canonical changes are mirrored by running `python bootstrap/scripts/update_skills_mirror.py all`.
- Local installs were updated only if found; otherwise, report “no local installs found”.

Checklist: `references/review.md`

## Common pitfalls

- Editing `skills/` directly instead of canonical.
- Adding vague learnings (“be careful”, “run tests”) rather than concrete items.
- Adding session-specific secrets or environment-specific paths into canonical skills.
- Forgetting to re-stitch after a skill update (learned section disappears).

Expanded list: `references/pitfalls.md`

## Scripts

- `scripts/apply_evolution.py`: apply a JSON delta to `pkb`, `local`, or `both` scopes.
- `scripts/merge_evolution.py`: merge JSON delta into `evolution.json` (dedupe, stable).
- `scripts/smart_stitch.py`: update/insert the bounded Learned section in `SKILL.md`.
- `scripts/align_all.py`: re-stitch all skills that have an `evolution.json`.

## References / assets

- Schema: `assets/evolution.schema.json`
- Example: `assets/evolution.example.json`
- Learned section format: `assets/learned_section_template.md`

