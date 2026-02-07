# Productivity

Skills for day-to-day engineering work with coding agents (planning, reviews, testing, execution).

## Structure

| Path | What it contains |
| --- | --- |
| `productivity/<skill>/` | Engineering workflow skills (planning, reviews, testing, execution) |

## <TABLE>
<!-- PKBLLM_TABLE_START -->
| Path | Type | Description |
| --- | --- | --- |
| `brainstorming/` | skill | You MUST use this before any creative work - creating features, building components, adding functionality, or modifying behavior. Explores user intent, requirements and design before implementation. |
| `dispatching-parallel-agents/` | skill | Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies |
| `executing-plans/` | skill | Use when you have a written implementation plan (task_plan.md) and need to execute it in the current session with persistent file-based progress tracking |
| `finishing-a-development-branch/` | skill | Use when implementation is complete, all tests pass, and you need to decide how to integrate the work - guides completion of development work by presenting structured options for merge, PR, or cleanup |
| `receiving-code-review/` | skill | Use when receiving code review feedback, before implementing suggestions, especially if feedback seems unclear or technically questionable - requires technical rigor and verification, not performative agreement or blind implementation |
| `requesting-code-review/` | skill | Use when completing tasks, implementing major features, or before merging to verify work meets requirements |
| `subagent-driven-development/` | skill | Use when executing an implementation plan in a git worktree/feature branch and you explicitly want subagent-per-task execution with review gates |
| `systematic-debugging/` | skill | Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes |
| `test-driven-development/` | skill | Use when implementing any feature or bugfix, before writing implementation code |
| `using-git-worktrees/` | skill | Use only when the user explicitly requests worktree/isolation for feature work. Creates isolated git worktrees with smart directory selection and safety verification. |
| `using-superpowers/` | skill | Use when starting any conversation or task to establish how to find and apply relevant `uv-*` skills early (without platform-specific assumptions). |
| `verification-before-completion/` | skill | Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims; evidence before assertions always |
| `writing-plans/` | skill | Use when you have a spec or requirements for a multi-step task, before touching code |
| `writing-skills/` | skill | Use when creating new skills, editing existing skills, or verifying skills work before deployment |
<!-- PKBLLM_TABLE_END -->
