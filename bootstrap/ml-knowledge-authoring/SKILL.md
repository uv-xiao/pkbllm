---
name: uv-bootstrap-ml-knowledge-authoring
description: "Create and curate new ML domain knowledge skills in this repo. Use when adding a new `knowledge/ML/*` skill, extending the curated ML taxonomy (model-architecture, training, distributed, serving, paper, kernel, agents), scaffolding a new skill folder, and ensuring naming (`uv-*`), licensing, and the generated `skills/` mirror stay consistent."
---

# Author ML knowledge skills (pkbllm)

## Goal

Add a new ML knowledge skill under `knowledge/ML/` that matches this repo’s conventions and stays high-signal.

## Before you write anything

1) **Pick the category** (keep the taxonomy small):

- `model-architecture/`
- `training/` (post-training)
- `distributed/`
- `serving/`
- `paper/`
- `kernel/` (to fill)
- `agents/` (to fill)

2) **Study existing exemplars** in the target category (copy structure, not content):

- Open 1–2 existing skills under `knowledge/ML/<category>/.../SKILL.md`
- Note their:
  - “When to use” phrasing
  - Quick-start commands
  - Common pitfalls / troubleshooting
  - Any required configuration patterns

3) **Decide what “valuable” means** (avoid adding duplicates):

- Include the skill only if it adds new capabilities, better workflow, or a clearer mental model than what already exists.
- If it overlaps heavily, prefer **updating the existing skill** instead of adding a new one.

## Scaffold a new skill folder

Use the scaffold script to create a new skill directory + template `SKILL.md`:

```bash
python bootstrap/ml-knowledge-authoring/scripts/scaffold_ml_knowledge_skill.py \
  --category model-architecture \
  --dir flashinfer \
  --name uv-flashinfer-kernels \
  --description "Kernel-level guidance for FlashInfer attention/kernels. Use when profiling/optimizing FlashInfer, understanding operator paths, or integrating into serving stacks."
```

The script:
- Creates `knowledge/ML/<category>/<dir>/`
- Writes `SKILL.md` with `uv-*` naming
- Optionally creates `references/`, `scripts/`, `assets/`

## Write the skill (minimum viable content)

In `SKILL.md`:

- Frontmatter:
  - `name:` must start with `uv-`
  - `description:` should include **when to use** triggers
- Body sections (recommended):
  - Quick start (commands, minimal example)
  - Concepts (1–2 screens)
  - Common workflows (bullet lists are fine)
  - Pitfalls / debugging checklist
  - References (links to primary docs/papers)

## Keep the repo consistent

1) Regenerate the mirror and README tables:

```bash
python bootstrap/scripts/update_skills_mirror.py all
```

2) Validate the repo is still installable:

```bash
npx -y skills add . --list
```

3) Licensing:

- If you imported/adapted material from a third-party repo, ensure it’s distributable and update `THIRD_PARTY_NOTICES.md`.

