# Routing cheatsheet (v2)

## Inputs → next skill

- `$HUMAN_MATERIAL_PATH/slides/<deck>/materials/...` or pasted notes → `content-prompts`
- `$HUMAN_MATERIAL_PATH/slides/<deck>/prompts/content/<deck>.md` → `styled-prompts`
- `$HUMAN_MATERIAL_PATH/slides/<deck>/prompts/styled/<deck>.md` → `styled-artifacts`

## Outputs → stop after

- Content PROMPT → `content-prompts`
- Styled PROMPT → `styled-prompts`
- Images/PDF/PPTX → `styled-artifacts`

## Style files

Preset style briefs live in `$HUMAN_MATERIAL_PATH/slides/styles/*.md` (example: `$HUMAN_MATERIAL_PATH/slides/styles/blueprint.md`).

Recommended style precedence:

1. Explicit user request (e.g. “use blueprint” → `$HUMAN_MATERIAL_PATH/slides/styles/blueprint.md`)
2. `$HUMAN_MATERIAL_PATH/slides/<deck>/configs/deck.yaml` (`style:`)
3. Default to `$HUMAN_MATERIAL_PATH/slides/styles/blueprint.md`

## Workdirs

All intermediates should be kept under:

- `$HUMAN_MATERIAL_PATH/slides/<deck>/artifacts/<deck>/work/`
