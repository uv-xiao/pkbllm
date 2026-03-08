# Installation

This repo is a skills repository compatible with the Skills CLI (`npx skills`) and task bootstrap scripts.

## Recommended entrypoints

There are two user-facing task bootstrap modes:

1. Human-selected skills
2. LLM-selected skills from a task description

Both are designed to be run directly with `curl` or `wget`.

### Human-selected skills

Use this when you want recommendations but still choose the exact skills yourself:

```bash
curl -fsSL https://raw.githubusercontent.com/uv-xiao/pkbllm/main/bootstrap/scripts/pkb_task_start.sh | bash -s --
```

```bash
wget -qO- https://raw.githubusercontent.com/uv-xiao/pkbllm/main/bootstrap/scripts/pkb_task_start.sh | bash -s --
```

Non-interactive form (useful for CI/local scripting):

```bash
curl -fsSL https://raw.githubusercontent.com/uv-xiao/pkbllm/main/bootstrap/scripts/pkb_task_start.sh | bash -s -- \
  --no-interactive \
  --task "Add robust planning and debugging workflows" \
  --done "Relevant skills are installed and AGENTS.md is assembled" \
  --skills "uv-brainstorming uv-writing-plans uv-systematic-debugging"
```

### LLM-selected skills

Use this when you want the bootstrap script to ask an LLM to choose the skills from your task description:

```bash
curl -fsSL https://raw.githubusercontent.com/uv-xiao/pkbllm/main/bootstrap/scripts/pkb_task_start_agent.sh | bash -s --
```

```bash
wget -qO- https://raw.githubusercontent.com/uv-xiao/pkbllm/main/bootstrap/scripts/pkb_task_start_agent.sh | bash -s --
```

You can pick the LLM runner explicitly:

```bash
curl -fsSL https://raw.githubusercontent.com/uv-xiao/pkbllm/main/bootstrap/scripts/pkb_task_start_agent.sh | bash -s -- \
  --selector claude \
  --agent kimi
```

Non-interactive form:

```bash
curl -fsSL https://raw.githubusercontent.com/uv-xiao/pkbllm/main/bootstrap/scripts/pkb_task_start_agent.sh | bash -s -- \
  --selector claude \
  --agent kimi \
  --no-interactive \
  --task "Bootstrap this repo for feature work with planning and code review" \
  --done "AGENTS.md and installed skills are ready for the target agent"
```

### Agent auto-detection and overrides

Both task bootstrap scripts accept `--agent auto|claude|codex|kimi|agents|agent`.

- `auto` inspects the target repo and available CLIs, then picks the best match
- `claude` installs into `.claude/skills`
- `codex` installs into `.codex/skills`
- `kimi` prefers `.agents/skills`, and falls back to existing Kimi-compatible roots such as `.kimi/skills`
- `agents` installs into `.agents/skills`
- `agent` installs into `.agent/skills`

Override detection any time with `--agent ...`.

## Install all skills into a repo (no task selection)

If you want a straight project-local install of the full pkb skill set:

```bash
curl -fsSL https://raw.githubusercontent.com/uv-xiao/pkbllm/main/bootstrap/scripts/pkb_skills_install.sh | bash
```

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

Task bootstrap options (examples):

- Target repo: `... | bash -s -- --target /path/to/repo`
- Keep the temp clone: `... | bash -s -- --keep`
- Use Skills CLI install instead of copy: `... | bash -s -- --install-mode skills-cli --agent codex`
- Force Claude Code target: `... | bash -s -- --agent claude`
- Force Kimi target: `... | bash -s -- --agent kimi`
- Force Claude as the LLM selector: `... | bash -s -- --selector claude`

LLM mode notes:

- `pkb_task_start_agent.sh` supports `--selector auto|claude|codex`
- In a real terminal, the wrapper reattaches prompts to `/dev/tty`
- In CI or other non-TTY environments, use `--no-interactive --task "..." --done "..."` so the wrapper does not attempt prompts

## Recommended: repo-local install (and cleanup)

If you have pkb skills installed in other locations (e.g. `~/.codex/skills`, `~/.agents/skills`, `<repo>/.codex/skills`, etc.), reset them and install repo-locally under `<repo>/.agent/skills`:

```bash
python bootstrap/scripts/pkb_skills_reset.py
```

By default this uses `npx skills remove` (global + project scope) plus a filesystem sweep over `~/.*/skills` and common local install folders to catch leftovers across different agents/tools.

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

## CI

This repo now expects two installation checks:

- Deterministic PR CI in `.github/workflows/install-checks.yml`
  - Regenerates `skills/` + README tables
  - Verifies the worktree stays clean
  - Lints skills/evals
  - Runs the bootstrap shell/unit tests
- Secret-gated LLM CI in `.github/workflows/llm-install-checks.yml`
  - Runs only on `workflow_dispatch` or `schedule`
  - Uses Claude Code as the selector CLI
  - Uses Kimi through Anthropic-compatible env vars

Recommended secrets for the LLM workflow:

- `KIMI_API_KEY`

The workflow maps that secret to the same Claude Code over Kimi environment used locally:

- `ANTHROPIC_BASE_URL=https://api.kimi.com/coding/`
- `ANTHROPIC_AUTH_TOKEN=$KIMI_API_KEY`
- `ANTHROPIC_MODEL=kimi-for-coding`

Those secrets are never used on public PRs because the LLM workflow is not triggered by `pull_request`.

## Maintainers

After editing canonical skills, regenerate the `skills/` mirror and refresh README indexes:

```bash
python bootstrap/scripts/update_skills_mirror.py all
```
