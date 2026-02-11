---
name: uv-tutorial-generator
description: Create structured tutorials from repo analysis and hands-on learning artifacts. Use when turning an ML/LLM codebase understanding into teachable material with objectives, diagrams, runnable examples, and exercises stored under $HUMAN_MATERIAL_PATH/exercises/.
---

# Tutorial generator (from repo analysis + hands-on)

This skill converts:
- `repo_analysis.md` (architecture + code locations)
- hands-on session reports (commands + results + observations)

into a tutorial under `$HUMAN_MATERIAL_PATH/exercises/tutorials/<topic>/`.

## Non-negotiables (requirements)

- Tutorials must be runnable: at least one example per tutorial is executed and includes captured expected output.
- Tutorials must be source-grounded: code tours include file:line pointers.
- Exercises must be checkable: tasks include “what counts as correct”.
- No placeholder markers like `<...>` may remain in tracked tutorial markdown.

## Output locations (pkbllm convention)

- `$HUMAN_MATERIAL_PATH/exercises/tutorials/<topic_slug>/README.md`
- `$HUMAN_MATERIAL_PATH/exercises/tutorials/<topic_slug>/chapters/`

## Quick start

```bash
# Run from this skill directory (the folder containing this SKILL.md):
python scripts/init_tutorial.py --topic \"vllm-internals\"
```

## Tutorial structure (default)

```
exercises/tutorials/<topic>/
├── README.md
└── chapters/
    └── 01_<chapter>/
        ├── README.md
        ├── examples/
        └── exercises/
```

## How to write good tutorials

Each chapter should include:

1. **Objectives** (what the reader will learn)
2. **Conceptual model** (diagram + vocabulary)
3. **Code tour** (file paths + line numbers)
4. **Runnable example** (expected output)
5. **Exercises** (questions + hints; optionally link to `uv-create-paper-exercises` packs)

Prefer compact visuals:
- Mermaid `flowchart` for architecture
- ASCII boxes for data structures
- Small pseudocode blocks for loop nesting

## Templates / assets

- Chapter template: `assets/chapter_README_template.md`
- Exercise template: `assets/exercise_template.md`
- Exercise patterns: `references/exercise-patterns.md`

## Integration

Prerequisites:
- Use `uv-repo-analysis` first (source of truth for code locations).
- Use `uv-hands-on-learning` to create real evidence and workloads.

Maintenance:
- If you add/change these workflows, run `uv-bootstrap-skill-linking`.

## Review policy

- Review checklist: `review.md`
- Common pitfalls: `pitfalls.md`

### Subagent review gates (recommended)

If you have subagent tooling available, add two explicit review gates before calling a tutorial “done”:

1) **Gate 1 — Spec compliance**: verify required elements exist (structure, runnable examples + expected output, file:line pointers, exercises with acceptance criteria) and no placeholders remain.
2) **Gate 2 — Quality**: verify the tutorial is coherent, teaches the right mental model, and is runnable end-to-end by a reader.

Prompt templates:
- Gate 1: `reviewer-prompts/spec-compliance-reviewer.md`
- Gate 2: `reviewer-prompts/quality-reviewer.md`
