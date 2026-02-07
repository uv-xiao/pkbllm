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
| `ml-knowledge-authoring/` | skill | Create and curate new ML domain knowledge skills in this repo. Use when adding a new `knowledge/ML/*` skill, extending the curated ML taxonomy (model-architecture, training, distributed, serving, paper, kernel, agents), scaffolding a new skill folder, and ensuring naming (`uv-*`), licensing, and the generated `skills/` mirror stay consistent. |
| `scripts/` | dir | Small utilities for maintaining this repo. |
| `skill-maintenance/` | skill | Maintain and curate the pkbllm skills repository. Use when adding/importing a new skill, merging skills from external repos, updating or refactoring existing skills, regenerating the generated `skills/` mirror, or ensuring licensing/compliance and naming conventions (all skills must start with `uv-`). |
<!-- PKBLLM_TABLE_END -->
