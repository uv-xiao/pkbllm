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
| `skill-linking/` | skill | Maintain relationships between pkbllm skills so workflows compose cleanly. Use when adding a new skill or changing workflows and you want to (1) decide which skills should be co-invoked, (2) update SKILL.md trigger descriptions and Integration sections, and (3) keep the generated mirror/manifest and README <TABLE> indexes consistent. |
| `skill-maintenance/` | skill | Maintain and curate the pkbllm skills repository. Use when adding/importing a new skill, merging skills from external repos, updating or refactoring existing skills, regenerating the generated `skills/` mirror, or ensuring licensing/compliance and naming conventions (all skills must start with `uv-`). |
<!-- PKBLLM_TABLE_END -->
