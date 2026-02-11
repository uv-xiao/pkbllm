# Review policy

## What counts as “done”

A tutorial is “done” when a reader can:

- follow the setup chapter to get a working environment,
- run at least one example end-to-end and see the expected output,
- and complete exercises that reinforce the core ideas.

## Required elements (minimum)

For each chapter:

- Objectives (2–4 concrete learnings)
- Conceptual model (diagram + terms)
- Code tour (file:line pointers)
- Runnable example (command + expected output excerpt)
- Exercises (at least 2)

For the tutorial root `README.md`:

- prerequisites
- learning path
- pointers to repo analysis and hands-on evidence (if applicable)

## Common failure modes

- Examples are not runnable (missing deps, missing expected output, missing commands).
- No file:line pointers (reader can’t connect concepts to code).
- Exercises are vague (“read about X”) instead of tasks with acceptance criteria.

## Quick placeholder scan (recommended)

Run this against the tutorial folder before review:

```bash
rg -n \"\\{[a-zA-Z0-9_]+\\}|<\\.\\.\\.>\" \"$HUMAN_MATERIAL_PATH/exercises/tutorials/<topic_slug>/\" -S
```

## Subagent review gates (recommended)

If you have subagent tooling available, use two review passes:

1) **Spec compliance** using `reviewer-prompts/spec-compliance-reviewer.md`
2) **Quality/teaching** using `reviewer-prompts/quality-reviewer.md`
