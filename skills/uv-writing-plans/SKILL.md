---
name: uv-writing-plans
description: Use when you have a spec or requirements for a multi-step task, before touching code
---

# Writing Plans

## Overview

Write comprehensive implementation plans assuming the engineer has zero context for our codebase and questionable taste. Document everything they need to know: which files to touch for each task, code, testing, docs they might need to check, how to test it. Give them the whole plan as bite-sized tasks. DRY. YAGNI. TDD. Frequent commits.

Assume they are a skilled developer, but know almost nothing about our toolset or problem domain. Assume they don't know good test design very well.

**Announce at start:** "I'm using the writing-plans skill to create the implementation plan."

**Where the plan lives (planning-with-files style):** write the plan to `task_plan.md` in the *target project root* (not inside this pkb repo). Also maintain:
- `findings.md` — discoveries/notes worth keeping
- `progress.md` — execution log (commands, test results, errors)

Use the templates in:
- `productivity/writing-plans/references/task_plan.md`
- `productivity/writing-plans/references/findings.md`
- `productivity/writing-plans/references/progress.md`

## Bite-Sized Task Granularity

**Each step is one action (2-5 minutes):**
- "Write the failing test" - step
- "Run it to make sure it fails" - step
- "Implement the minimal code to make the test pass" - step
- "Run the tests and make sure they pass" - step
- "Commit" - step

## Plan file header (`task_plan.md`)

**Every `task_plan.md` MUST start with:**

```markdown
# Task plan: <feature name>

**Owner:** <human/agent>  
**Status:** planning | in_progress | blocked | complete  
**Last updated:** <YYYY-MM-DD>  

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---
```

## Task Structure

```markdown
## Phase N: <phase name>

**Status:** planned | in_progress | blocked | complete

### Task N.M: <task name>

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

**Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

**Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
```

## Remember
- Exact file paths always
- Complete code in plan (not "add validation")
- Exact commands with expected output
- Reference relevant skills with @ syntax
- DRY, YAGNI, TDD, frequent commits

## Execution Handoff

After writing `task_plan.md`, proceed by invoking `uv-executing-plans` in the **current session** (default).

Only use git worktrees if the user explicitly requests worktree/isolation. If a worktree is used and the work completes, follow `uv-finishing-a-development-branch`.
