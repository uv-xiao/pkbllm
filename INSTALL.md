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

Install all skills globally (user scope):

```bash
npx skills add . -g -a codex --skill '*' -y
```

## Optional environment variables

Some skills may refer to these paths:

- `PKB_PATH`: absolute path to this repository checkout
- `HUMAN_MATERIAL_PATH`: where to store generated human-facing materials (slides, manuscripts, exercises)

## Maintainers

After editing canonical skills, regenerate the `skills/` mirror and refresh README indexes:

```bash
python bootstrap/scripts/update_skills_mirror.py all
```
