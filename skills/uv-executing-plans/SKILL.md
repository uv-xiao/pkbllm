---
name: uv-executing-plans
description: Use when you have a written implementation plan (task_plan.md) and need to execute it in the current session with persistent file-based progress tracking
---

# Executing Plans

## Overview

Load the plan, review critically, execute tasks phase-by-phase, and keep progress durable on disk.

**Core principle:** Keep the plan + findings + progress in files so humans and agents stay aligned across long tasks.

**Announce at start:** "I'm using the executing-plans skill to implement this plan."

## File-based tracking rules (planning-with-files distilled)

- **Create plan first:** don’t start execution without `task_plan.md`.
- **Read before decide:** before major decisions, re-read `task_plan.md` to refresh goals.
- **Update after act:** after completing a task or phase, update phase status and log results.
- **2-action rule:** after every ~2 tool/command iterations, write key learnings to `progress.md`/`findings.md` so context doesn’t drift.
- **3 strikes on errors:** do not repeat the same failing action more than once; change approach each attempt, then escalate.

## The Process

### Step 0: Ensure planning files exist

In the target project root, ensure these exist (create if missing):
- `task_plan.md` (phases + status)
- `findings.md` (discoveries)
- `progress.md` (execution log)

### Step 1: Load and review the plan

1. Read `task_plan.md`
2. Identify blockers/ambiguities **before** starting
3. If blocked: mark the relevant phase/task as `blocked` and ask the human for clarification
4. If clear: set overall plan `Status: in_progress`

### Step 2: Execute by phase (default)

For each phase marked `planned`:
1. Change phase status → `in_progress`
2. Execute tasks in order (one task at a time)
3. After each task:
   - log what you did in `progress.md` (commands + results)
   - record new knowledge in `findings.md` (if any)
4. When all tasks in the phase are done and verified: mark phase → `complete`

### Step 3: Stop conditions

Stop and ask the human when:
- a task requires product decisions or ambiguous behavior
- verification fails repeatedly (use the “3 strikes” idea: change approach each time)
- the plan needs restructuring (add a new phase, reorder, split tasks)

### Step 4: Completion

When all phases are `complete`:
- mark overall plan `Status: complete`
- summarize results (what changed + how it was verified)

If and only if a git worktree/feature branch workflow was explicitly used, invoke `uv-finishing-a-development-branch`.

## When to Stop and Ask for Help

**STOP executing immediately when:**
- Hit a blocker mid-batch (missing dependency, test fails, instruction unclear)
- Plan has critical gaps preventing starting
- You don't understand an instruction
- Verification fails repeatedly

**Ask for clarification rather than guessing.**

## When to Revisit Earlier Steps

**Return to Review (Step 1) when:**
- Partner updates the plan based on your feedback
- Fundamental approach needs rethinking

**Don't force through blockers** - stop and ask.

## Remember
- Review plan critically first
- Follow plan steps exactly
- Don't skip verifications
- Reference skills when plan says to
- Update `task_plan.md` phase status as you go
- Log key actions/results to `progress.md`
- Stop when blocked; don’t guess

## Integration

Pairs well with:
- `uv-writing-plans` — creates `task_plan.md`
- `uv-systematic-debugging` — when stuck on failing tests/bugs
- `uv-verification-before-completion` — when about to claim “done”
