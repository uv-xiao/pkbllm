---
name: uv-bootstrap-ml-knowledge-authoring
description: "Create and curate new ML domain knowledge skills in this repo. Use when adding a new `knowledge/ML/*` skill, extending the curated ML taxonomy (model-architecture, training, distributed, serving, paper, kernel, agents), scaffolding a new skill folder, and ensuring naming (`uv-*`), licensing, and the generated `skills/` mirror stay consistent."
---

# Author ML knowledge skills (pkbllm)

## Goal

Add a new ML knowledge skill under `knowledge/ML/` that matches this repo’s conventions and stays high-signal.

## Curated ML taxonomy (fixed)

Put new ML skills under exactly one of these categories:

- `model-architecture/`
- `training/` (post-training)
- `distributed/`
- `serving/`
- `paper/`
- `kernel/` (to fill)
- `agents/` (to fill)

If it doesn’t fit, don’t add it. Extend taxonomy only with explicit repo-level intent.

## House style (baked-in)

This repo’s ML skills follow a consistent structure. Do not “study exemplars at runtime”; instead, apply these rules:

### 1) Frontmatter schema

All ML skills must have `name:` starting with `uv-`. Prefer this full schema (extra fields are allowed):

```yaml
---
name: uv-<skill-slug>
description: "<what it is>. Use when <trigger phrases and contexts>."
license: MIT
tags: [Short, Tags, Here]
dependencies: [optional, list, of, python, packages]
---
```

Notes:
- `license:` is optional but recommended (most ML skills here are MIT-derived).
- Keep `description:` focused on **when to use** triggers; the body is loaded later.

### 2) Minimum viable sections (copy/paste template)

Use these headings in `SKILL.md`:

1. `## Quick start` — the shortest command/code snippet that works
2. `## When to use` — 5–12 bullets of trigger phrases
3. `## Core concepts` — 1–2 screens; define key terms precisely
4. `## Workflows` — common tasks as checklists
5. `## Pitfalls` — failure modes + debugging checks
6. `## References` — primary docs/papers/repos (prefer authoritative)

### 3) High-signal rubric (avoid doc dumps)

Include a new skill only if it meaningfully improves at least one of:
- **Workflow**: a repeatable procedure with decision points and commands
- **Debuggability**: concrete failure modes + how to diagnose
- **Implementation**: minimal runnable snippets + integration points
- **Comparative clarity**: when to choose this over alternatives

Avoid:
- Pasting entire upstream docs (low signal, hard to maintain)
- Vague “overview only” skills with no commands/checklists
- Duplicating an existing skill’s scope (prefer updating it)

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

## Category-specific guidance (distilled)

### `model-architecture/`

Focus on:
- the **one core idea** (e.g., state-space recurrence, routing, draft/verify)
- minimal pseudocode or algorithm sketch
- what changes at inference time (KV cache? batching? memory shape?)

### `training/` (post-training)

Focus on:
- objective + data requirements
- training loop topology (actors/critics/rollouts, preference pairs, etc.)
- scaling knobs and common instabilities

### `distributed/`

Focus on:
- parallelism axes (DP/TP/PP/CP/EP) and what each breaks
- sharding/checkpointing patterns
- “first failure” debugging (NCCL hangs, OOMs, divergence)

### `serving/`

Focus on:
- request lifecycle (prefill vs decode), batching, cache semantics
- deployment shapes (single node vs multi node), observability hooks
- latency/throughput tradeoffs and failure modes

### `paper/`

Focus on:
- reproducible writing workflow and citation correctness
- camera-ready checklists, positioning, and common reviewer objections

### `kernel/` and `agents/` (to fill)

Start with:
- a minimal workflow + tooling (profilers, tracing, reproduction harness)
- a small glossary + “where to look in code”

## References (kept in this skill)

Read `bootstrap/ml-knowledge-authoring/references/ml-skill-style-guide.md` for a short, copy-ready template and checklists.

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
