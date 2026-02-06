---
name: styled-artifacts
description: "Generate slide images and final PDF/PPTX from v2 styled prompts ($HUMAN_MATERIAL_PATH/slides/<deck>/prompts/styled/<deck>.md), storing intermediates in $HUMAN_MATERIAL_PATH/slides/<deck>/artifacts/<deck>/work/. Use when the user asks to render/generate/export slides from a Styled PROMPT into images/PDF/PPTX."
---

# Styled Artifacts (Styled PROMPT → Images + PDF/PPTX)

## Quick start

All slider skills store their working files under:

- `${HUMAN_MATERIAL_PATH}/slides/<deck>/`

Recommended deck layout:

- `${HUMAN_MATERIAL_PATH}/slides/<deck>/materials/` (inputs)
- `${HUMAN_MATERIAL_PATH}/slides/<deck>/prompts/content/<deck>.md`
- `${HUMAN_MATERIAL_PATH}/slides/<deck>/prompts/styled/<deck>.md`
- `${HUMAN_MATERIAL_PATH}/slides/<deck>/artifacts/<deck>/work/` (intermediates)
- `${HUMAN_MATERIAL_PATH}/slides/<deck>/artifacts/<deck>/<deck>.pdf`
- `${HUMAN_MATERIAL_PATH}/slides/<deck>/artifacts/<deck>/<deck>.pptx` (image-based PPTX)

Generate all artifacts into a per-deck workdir:

- `OPENROUTER_API_KEY=... python3 skills/styled-artifacts/scripts/styled_prompts_to_artifacts.py --prompts "$HUMAN_MATERIAL_PATH/slides/<deck>/prompts/styled/<deck>.md" --workdir "$HUMAN_MATERIAL_PATH/slides/<deck>/artifacts/<deck>/work" --pdf "$HUMAN_MATERIAL_PATH/slides/<deck>/artifacts/<deck>/<deck>.pdf" --pptx "$HUMAN_MATERIAL_PATH/slides/<deck>/artifacts/<deck>/<deck>.pptx"`

## Workflow (recommended)

1. Generate slide images into `$HUMAN_MATERIAL_PATH/slides/<deck>/artifacts/<deck>/work/slides/`.
2. Assemble PDF/PPTX.
3. Keep generation cheap: review happens on prompts (content/styled), not on final artifacts.

## Existing output behavior (workdir versioning)

To avoid clobbering prior outputs, the renderer auto-versions the workdir:

- If `--workdir .../artifacts/<deck>/work` already exists, it will write to `.../artifacts/<deck>/work-2`, `work-3`, ...
- For iterative edits where you want to keep prior slide images, pass `--reuse-workdir`.

## Modification & iteration (cheap)

### Regenerate specific slides

Edit `$HUMAN_MATERIAL_PATH/slides/<deck>/prompts/styled/<deck>.md`, then regenerate only the affected slide numbers:

- `OPENROUTER_API_KEY=... python3 skills/styled-artifacts/scripts/styled_prompts_to_artifacts.py --prompts "$HUMAN_MATERIAL_PATH/slides/<deck>/prompts/styled/<deck>.md" --workdir "$HUMAN_MATERIAL_PATH/slides/<deck>/artifacts/<deck>/work" --reuse-workdir --only 7`
- `... --only 2,5,8`
- `... --only 5-8`

If you pass `--pdf/--pptx` together with `--only`, the script expects the other slide images to already exist in the same reused workdir.

### Add / delete / reorder slides

- Keep slide numbers unique: `## Slide N: ...` must not repeat.
- When inserting a slide, renumber subsequent slides and regenerate the affected range with `--only`.
- When deleting a slide, renumber subsequent slides and regenerate the affected range with `--only`.

## Notes

- Expects `prompts/styled/*.md` to contain blocks like `## Slide N: Title`.
- Keeps intermediate slide PNGs and logs under `$HUMAN_MATERIAL_PATH/slides/<deck>/artifacts/<deck>/work/`.
- If a slide references `.svg` images, they are rasterized before being sent to image models (some providers reject SVG inputs).
- PPTX outputs:
  - **Image PPTX** (`--pptx`): slide images packaged into a PPTX (fast; not truly editable).

## Editable PPTX (use `$pptx` skill)

This repo intentionally does not ship the `pptx` skill (it was proprietary in the upstream source).
If you need a truly editable PPTX (native text boxes, tables, shapes), use a separate licensed PPTX
workflow and treat the generated PDF / image-PPTX as the visual reference.

References:
- `references/consistency-protocol.md`
- `references/pipeline-notes.md`

## Completion behavior (required)

When this skill is triggered:

1. **Do only this step**: render the artifacts the user explicitly requested (images / PDF / image-PPTX).
2. **Do not invoke other skills automatically** (e.g. `$pptx` for editable PPTX) unless explicitly requested.
3. **End your response with recommended next steps** (options + commands to run next).

Recommended next steps (include this block in your response):

- **Outputs**: point to the workdir and final artifact paths.
- **Iterate cheaply** (after editing `$HUMAN_MATERIAL_PATH/slides/<deck>/prompts/styled/<deck>.md`):
  - `OPENROUTER_API_KEY=... python3 skills/styled-artifacts/scripts/styled_prompts_to_artifacts.py --prompts "$HUMAN_MATERIAL_PATH/slides/<deck>/prompts/styled/<deck>.md" --workdir "$HUMAN_MATERIAL_PATH/slides/<deck>/artifacts/<deck>/work" --reuse-workdir --only 7`
