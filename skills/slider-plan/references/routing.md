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

Preset style briefs live in `styles/*.md` (example: `styles/blueprint.md`).

Recommended style precedence:

1. Explicit user request (e.g. “use blueprint” → `styles/blueprint.md`)
2. `configs/deck.yaml` (`style:`)
3. Default to `styles/blueprint.md`

## Workdirs

All intermediates should be kept under:

- `$HUMAN_MATERIAL_PATH/slides/<deck>/artifacts/<deck>/work/`
