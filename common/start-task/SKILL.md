---
name: uv-start-task
description: "Use at the start of a task to assemble relevant pkbllm skill notes into the project’s AGENTS.md (passive, in-band context). Guides the user to run the pkb agents-md CLI (recommend + assemble), pick skills, and set up minimal repo context so any agent can immediately work with the right constraints."
---

# Start a task (assemble AGENTS.md)

This skill treats pkbllm skills as **notes**: instead of relying on “skill invocation” at runtime, you assemble the relevant skill texts into the project’s `AGENTS.md` so any agent has the context automatically.

## Quick start

From the target project repo (the repo you’re working on), run:

```bash
python /path/to/pkbllm/bootstrap/scripts/pkb_agents_md.py recommend --query "<your task>"
python /path/to/pkbllm/bootstrap/scripts/pkb_agents_md.py assemble --query "<your task>" --agents-md ./AGENTS.md --pick --init
```

This writes/updates a marked block in `AGENTS.md`:

- `<!-- PKBLLM-AGENTS-NOTE-START -->`
- `<!-- PKBLLM-AGENTS-NOTE-END -->`

## Workflow

1) Clarify the task in one sentence (what “done” means).
2) Use the CLI to **recommend** likely skills.
3) Use the CLI to **assemble** a curated set into `AGENTS.md` (interactive pick).
4) Start doing the task with the agent — it now has the assembled notes in-band.

## Notes

- The CLI is idempotent: re-running it replaces the marked block.
- If you want a fully non-interactive flow, pass `--skill uv-...` repeatedly to `assemble`.
