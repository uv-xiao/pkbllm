---
name: uv-tutorial-generator
description: Create structured tutorials from repo analysis and hands-on learning artifacts. Use when turning an ML/LLM codebase understanding into teachable material with objectives, diagrams, runnable examples, and exercises stored under $HUMAN_MATERIAL_PATH/exercises/.
---

# Tutorial generator (from repo analysis + hands-on)

This skill converts:
- `repo_analysis.md` (architecture + code locations)
- hands-on session reports (commands + results + observations)

into a tutorial under `$HUMAN_MATERIAL_PATH/exercises/tutorials/<topic>/`.

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

## Integration

Prerequisites:
- Use `uv-repo-analysis` first (source of truth for code locations).
- Use `uv-hands-on-learning` to create real evidence and workloads.

Maintenance:
- If you add/change these workflows, run `uv-bootstrap-skill-linking`.
