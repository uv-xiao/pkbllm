# Bootstrap

Skills and scripts used to maintain this repository (indexing, mirror generation).

## Structure

| Path | What it contains |
| --- | --- |
| `bootstrap/scripts/` | Maintenance scripts (mirror + README index updates) |

## <TABLE>
<!-- PKBLLM_TABLE_START -->
| Path | Type | Description |
| --- | --- | --- |
| `find-skills/` | skill | Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for X", "is there a skill that can...", or express interest in extending capabilities. This skill should be used when the user is looking for functionality that might exist as an installable skill. |
| `ml-knowledge-authoring/` | skill | Create and curate new ML domain knowledge skills in this repo. Use when adding a new `knowledge/ML/*` skill, extending the curated ML taxonomy (model-architecture, training, distributed, serving, paper, kernel, agents), scaffolding a new skill folder, and ensuring naming (`uv-*`), licensing, and the generated `skills/` mirror stay consistent. |
| `scripts/` | dir | Small utilities for maintaining this repo. |
| `skill-maintenance/` | skill | Maintain and curate the pkbllm skills repository. Use when adding/importing a new skill, merging skills from external repos, updating or refactoring existing skills, regenerating the generated `skills/` mirror, or ensuring licensing/compliance and naming conventions (all skills must start with `uv-`). |
<!-- PKBLLM_TABLE_END -->
