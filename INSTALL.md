# Installation

This repo is a skills repository compatible with the Skills CLI (`npx skills`).

## Install with the Skills CLI

List available skills:

```bash
npx skills add . --list
```

Install all skills to Codex (project scope):

```bash
npx skills add . -a codex --skill '*' -y
```

Important:

- Avoid installing “for all agents” (e.g., by omitting `-a ...`). Always target a single agent, like `-a codex`.
- Prefer project-scope installs over global installs to avoid surprising cross-project changes.

If you accidentally created local install folders (e.g. `.agent/`, `.agents/`, `.cursor/`, etc.), they are gitignored in this repo.

## Optional environment variables

Some skills may refer to these paths:

- `PKB_PATH`: absolute path to this repository checkout
- `HUMAN_MATERIAL_PATH`: where to store generated human-facing materials (slides, manuscripts, exercises). Slider skills use `$HUMAN_MATERIAL_PATH/slides/<deck>/...`.

## Maintainers

After editing canonical skills, regenerate the `skills/` mirror and refresh README indexes:

```bash
python bootstrap/scripts/update_skills_mirror.py all
```
