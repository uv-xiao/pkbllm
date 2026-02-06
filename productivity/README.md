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
| `executing-plans/` | skill | Use when you have a written implementation plan to execute in a separate session with review checkpoints |
| `find-skills/` | skill | Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for X", "is there a skill that can...", or express interest in extending capabilities. This skill should be used when the user is looking for functionality that might exist as an installable skill. |
| `finishing-a-development-branch/` | skill | Use when implementation is complete, all tests pass, and you need to decide how to integrate the work - guides completion of development work by presenting structured options for merge, PR, or cleanup |
| `receiving-code-review/` | skill | Use when receiving code review feedback, before implementing suggestions, especially if feedback seems unclear or technically questionable - requires technical rigor and verification, not performative agreement or blind implementation |
| `requesting-code-review/` | skill | Use when completing tasks, implementing major features, or before merging to verify work meets requirements |
| `subagent-driven-development/` | skill | Use when executing implementation plans with independent tasks in the current session |
| `systematic-debugging/` | skill | Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes |
| `test-driven-development/` | skill | Use when implementing any feature or bugfix, before writing implementation code |
| `using-git-worktrees/` | skill | Use when starting feature work that needs isolation from current workspace or before executing implementation plans - creates isolated git worktrees with smart directory selection and safety verification |
| `using-superpowers/` | skill | Use when starting any conversation - establishes how to find and use skills, requiring Skill tool invocation before ANY response including clarifying questions |
| `verification-before-completion/` | skill | Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims; evidence before assertions always |
| `writing-plans/` | skill | Use when you have a spec or requirements for a multi-step task, before touching code |
| `writing-skills/` | skill | Use when creating new skills, editing existing skills, or verifying skills work before deployment |
<!-- PKBLLM_TABLE_END -->
