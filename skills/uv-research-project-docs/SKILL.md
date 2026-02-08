---
name: uv-research-project-docs
description: Create and maintain the research-project documentation structure (analysis/features/implementation/progress/workloads/spec/evaluation + feats/ impls/ evals/). Use when starting a new research repo, evolving a framework during design/development/evaluation, or when adding/changing features so docs/spec/eval stay synchronized with implementation.
---

# Research project docs

Maintain a predictable set of documents that evolves with the project, so humans can stay in sync with the code and evaluation.

## The document set (docs root)

This skill manages a *docs root* directory (default recommendation: `docs/` in the target repo). It contains:

- `analysis.md` — rationale: scenarios, requirements, gaps, and why they matter; 3–5 key aspects; map each challenge → technique/feature.
- `features.md` — concise list of features with links to `feats/*.md`.
- `implementation.md` — roadmap to implement the framework; link into `impls/*.md`.
- `progress.md` — component completeness diagram + execution log.
- `workloads.md` — typical workloads where the technique helps.
- `spec.md` — formal specs (DSL/IR) and key APIs/ABIs.
- `evaluation.md` — experiment plan and methodology; link into `evals/*.md`.
- `feats/` — per-feature deep dives (`feats/<slug>.md`).
- `impls/` — per-component implementation notes (`impls/<slug>.md`).
- `evals/` — per-experiment details (`evals/<slug>.md`).

## Initialize the structure

Use the scaffold script (works against any target repo path):

```bash
# Run from this skill directory (the folder containing this SKILL.md):
python scripts/init_research_project_docs.py \
  --project-root /abs/path/to/your/repo \
  --docs-root docs
```

Notes:
- Use `--docs-root .` if you want the files at repo root (not recommended).
- The script will not overwrite existing files unless you pass `--force`.

## Keep docs synchronized (the rule)

Whenever you add/modify a feature, or change behavior:

1. Update `features.md` (add/update a row, link the detailed doc)
2. Update/add `feats/<feature>.md` (what + why + UX/API surface + non-goals)
3. Update `implementation.md` and/or `impls/<component>.md` (how it’s built)
4. If the change impacts interfaces: update `spec.md`
5. If the change impacts evaluation: update `evaluation.md` and/or `evals/<exp>.md`
6. Update `progress.md` diagram/status so “what’s done” matches reality

If you are executing an implementation plan (`task_plan.md`), add an explicit task after any feature-completing task: “sync research docs”.

## Writing rules (keep it tight)

- Prefer tables + short sections over walls of text.
- Every major claim in `analysis.md` should point to: a feature, spec surface, implementation component, or evaluation plan.
- Each `feats/<slug>.md` should define: **Status**, **User story**, **API/UX**, **Constraints**, **Testing/eval hooks**, **Open questions**.

## Integration

Pairs well with:
- `uv-writing-plans` — include “sync docs” tasks in `task_plan.md`
- `uv-executing-plans` — keep docs in sync while executing
- `uv-bootstrap-skill-linking` — keep skill relationships updated when adding new workflows
