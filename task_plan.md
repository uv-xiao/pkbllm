# Task plan: bootstrap install cleanup and superpowers sync

**Owner:** agent  
**Status:** complete  
**Last updated:** 2026-03-08  

**Goal:** Synchronize productivity skills from `.references/superpowers`, simplify the public install/bootstrap entrypoints, and add CI coverage for both human-guided and LLM-guided installation flows.  
**Architecture:** Update the canonical productivity skill sources to the latest upstream workflow text while preserving `uv-` naming and pkbllm-specific conventions. Refactor the bootstrap scripts around a shared agent-detection/install helper so `INSTALL.md` can present two clear modes backed by the same behavior. Add GitHub Actions that run deterministic install checks on every PR and keep the LLM-backed path on a secret-gated workflow that never exposes provider credentials to public forks.  
**Tech stack:** Bash, Python 3, GitHub Actions, unittest, generated `skills/` mirror tooling  

---

## Scope

- In scope:
  - Sync canonical productivity skill content from `.references/superpowers`
  - Clean up install/bootstrap docs and scripts around two user-facing modes
  - Add agent auto-detection/default selection for supported coding agents
  - Add CI for both install modes, with secret-safe LLM workflow wiring
- Out of scope:
  - Running live Kimi/Claude API calls from this session
  - Changing non-productivity canonical skill families
  - Reworking the broader eval framework beyond what install CI needs

## Phases

## Phase 1: Sync productivity skills from superpowers

**Status:** complete

### Task 1.1: Update diverged productivity SKILL.md files

**Files:**
- Modify: `productivity/brainstorming/SKILL.md`
- Modify: `productivity/executing-plans/SKILL.md`
- Modify: `productivity/requesting-code-review/SKILL.md`
- Modify: `productivity/subagent-driven-development/SKILL.md`
- Modify: `productivity/systematic-debugging/SKILL.md`
- Modify: `productivity/using-git-worktrees/SKILL.md`
- Modify: `productivity/using-superpowers/SKILL.md`
- Modify: `productivity/writing-plans/SKILL.md`
- Modify: `productivity/writing-skills/SKILL.md`
- Test: `python bootstrap/scripts/update_skills_mirror.py all`

**Steps:**
1. Compare canonical productivity skills against `.references/superpowers/skills/*`.
2. Apply upstream wording/logic updates while preserving `uv-` names and pkbllm-specific conventions.
3. Re-read changed skills for broken references to `superpowers:*` or non-pkb paths.
4. Regenerate the `skills/` mirror and README tables.
5. Lint skill metadata and mirror consistency.

**Verification:**
- Command(s): `python bootstrap/scripts/update_skills_mirror.py all && python bootstrap/scripts/lint_skills.py --check-evals`
- Expected: mirror regeneration succeeds and lint exits 0

## Phase 2: Unify install/bootstrap behavior and docs

**Status:** complete

### Task 2.1: Add shared agent detection and install destination logic

**Files:**
- Create: `bootstrap/scripts/pkb_install_lib.py`
- Modify: `bootstrap/scripts/pkb_task_start.sh`
- Modify: `bootstrap/scripts/pkb_task_start_agent.py`
- Modify: `bootstrap/scripts/pkb_task_start_agent.sh`
- Test: `bootstrap/scripts/test_bootstrap_install_modes.py`

**Steps:**
1. Write failing tests for agent detection and install destination handling.
2. Add a shared Python helper for supported agents and default detection.
3. Update human-guided and LLM-guided bootstrap flows to use the shared helper.
4. Fix `pkb_task_start.sh` copy mode so it respects the selected/detected agent.
5. Verify both scripts still support non-interactive usage where applicable.

**Verification:**
- Command(s): `python3 -m unittest bootstrap.scripts.test_pkb_task_start_agent_sh bootstrap.scripts.test_bootstrap_install_modes -v`
- Expected: all bootstrap-focused tests pass

### Task 2.2: Rewrite INSTALL.md around two install modes

**Files:**
- Modify: `INSTALL.md`
- Modify: `bootstrap/scripts/README.md`
- Test: `python bootstrap/scripts/update_skills_mirror.py all`

**Steps:**
1. Rewrite `INSTALL.md` to present two primary flows: human-selected and LLM-selected.
2. Document wget/curl entrypoints, supported agents, auto-detection behavior, and explicit overrides.
3. Remove outdated or duplicative installation guidance that conflicts with the new entry surface.
4. Ensure examples use the new script contracts consistently.
5. Re-read for command correctness and consistency with script help text.

**Verification:**
- Command(s): `bash bootstrap/scripts/pkb_task_start.sh --help && bash bootstrap/scripts/pkb_task_start_agent.sh --help`
- Expected: help text matches documented modes/options

## Phase 3: Add CI for install success

**Status:** complete

### Task 3.1: Add deterministic CI for human-guided install mode

**Files:**
- Create: `.github/workflows/install-checks.yml`
- Modify: `bootstrap/scripts/test_pkb_task_start_agent_sh.py`
- Create: `bootstrap/scripts/test_install_ci_helpers.py`
- Test: `python3 -m unittest ...`

**Steps:**
1. Add unit/integration-style tests that simulate install flows without external network/API calls.
2. Add a GitHub Actions workflow for lint, mirror regeneration diff check, and deterministic install tests.
3. Ensure workflows work on public PRs without secrets.
4. Verify workflow YAML syntax and local test commands.
5. Document what the workflow covers.

**Verification:**
- Command(s): `python3 -m unittest bootstrap.scripts.test_pkb_task_start_agent_sh bootstrap.scripts.test_bootstrap_install_modes bootstrap.scripts.test_install_ci_helpers -v`
- Expected: all deterministic CI-targeted tests pass

### Task 3.2: Add secret-gated LLM install workflow wiring

**Files:**
- Create: `.github/workflows/llm-install-checks.yml`
- Create: `bootstrap/scripts/run_llm_install_check.py`
- Modify: `INSTALL.md`
- Test: `python3 -m py_compile bootstrap/scripts/run_llm_install_check.py`

**Steps:**
1. Create a manual/scheduled GitHub Actions workflow for the LLM-selected install mode.
2. Gate execution so secrets are only used on trusted events and never on forked PRs.
3. Wire the workflow for Claude Code plus Kimi/OpenAI-compatible API env vars without echoing them.
4. Add a small runner script that validates required env vars and drives the LLM install check.
5. Document the secret contract and safe triggering model.

**Verification:**
- Command(s): `python3 -m py_compile bootstrap/scripts/run_llm_install_check.py`
- Expected: script compiles cleanly and workflow references only secret/env names, not literal tokens

## Findings / notes

- `pkb_task_start.sh` currently ignores `--agent` in `copy` mode and hardcodes installs into `.codex/skills`.
- There is no existing CI config in the repo.
- Divergence from `.references/superpowers` is concentrated in productivity `SKILL.md` files rather than auxiliary prompt/reference files.
- Safe default for LLM CI is GitHub Actions `workflow_dispatch` / scheduled runs only, with secrets unavailable to public fork PRs.
- `.references/superpowers` showed two clearly stale productivity skills (`brainstorming`, `using-superpowers`) plus several smaller pkb-specific drift points where `superpowers:` references needed adapting back to `uv-`.
- Kimi CLI documentation prefers project-local `.agents/skills` and also recognizes `.kimi/skills`, `.claude/skills`, and `.codex/skills`, so copy-mode installs now prefer `.agents/skills` for Kimi while reusing an existing Kimi-specific root when present.

## Progress log

| Date | Change | Evidence (command / link / output) |
| --- | --- | --- |
| 2026-03-08 | Audited install scripts, docs, and reference superpowers repo | `sed -n '1,260p' INSTALL.md`, `sed -n '1,320p' bootstrap/scripts/pkb_task_start.sh`, `diff -q .references/superpowers/skills/* productivity/*/SKILL.md` |
| 2026-03-08 | Identified missing CI and install bug in human-guided flow | explorer report + `pkb_task_start.sh` copy-mode hardcoded `.codex/skills` |
| 2026-03-08 | Added shared agent resolution, non-interactive human bootstrap, Claude-capable LLM bootstrap, and CI workflows | `python3 -m unittest bootstrap.scripts.test_bootstrap_install_modes bootstrap.scripts.test_pkb_task_start_agent_sh -v` |
| 2026-03-08 | Regenerated mirror + README tables and linted skills after productivity sync | `python3 bootstrap/scripts/update_skills_mirror.py all`, `python3 bootstrap/scripts/lint_skills.py --check-evals` |
| 2026-03-08 | Verified shell wrappers and Python entrypoints | `bash -n bootstrap/scripts/pkb_task_start.sh && bash -n bootstrap/scripts/pkb_task_start_agent.sh`, `python3 -m py_compile bootstrap/scripts/pkb_install_lib.py bootstrap/scripts/pkb_task_start_agent.py bootstrap/scripts/run_llm_install_check.py` |

## Errors encountered

| Error | Attempt | Fix / next step |
| --- | --- | --- |
| N/A | N/A | N/A |
