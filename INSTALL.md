# Installation

This repo is a skills repository compatible with the Skills CLI (`npx skills`).

## One-liner installer (recommended)

This does everything end-to-end without assuming you’re already in a pkbllm checkout:

```bash
curl -fsSL https://raw.githubusercontent.com/uv-xiao/pkbllm/main/bootstrap/scripts/pkb_skills_install.sh | bash
```

Or with `wget`:

```bash
wget -qO- https://raw.githubusercontent.com/uv-xiao/pkbllm/main/bootstrap/scripts/pkb_skills_install.sh | bash
```

With options:

```bash
curl -fsSL https://raw.githubusercontent.com/uv-xiao/pkbllm/main/bootstrap/scripts/pkb_skills_install.sh | bash -s -- --repo-dir ~/src/pkbllm --ref main
```

Dev mode (use an existing local pkbllm checkout; no clone/pull):

```bash
curl -fsSL https://raw.githubusercontent.com/uv-xiao/pkbllm/main/bootstrap/scripts/pkb_skills_install.sh | bash -s -- --dev --repo-dir ~/src/pkbllm
```

## Install with the Skills CLI

List available skills:

```bash
npx skills add . --list
```

## Recommended: repo-local install (and cleanup)

If you have pkb skills installed in other locations (e.g. `~/.codex/skills`, `~/.agents/skills`, `<repo>/.codex/skills`, etc.), reset them and install repo-locally under `<repo>/.agent/skills`:

```bash
python bootstrap/scripts/pkb_skills_reset.py
```

By default this uses `npx skills remove` (global + project scope, all agents) for exhaustive cleanup, then does a filesystem sweep for common leftover install folders.

Useful flags:

- Preview actions: `python bootstrap/scripts/pkb_skills_reset.py --dry-run`
- Overwrite existing repo-local install: `python bootstrap/scripts/pkb_skills_reset.py --force`
- Copy instead of symlink: `python bootstrap/scripts/pkb_skills_reset.py --copy --force`
- Skip `npx skills remove` cleanup: `python bootstrap/scripts/pkb_skills_reset.py --no-skills-cli`

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
