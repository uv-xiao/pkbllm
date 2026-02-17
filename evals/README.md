# Skill evals

This folder contains **tracked eval sources** (prompts, schemas, deterministic check configs).

Generated run outputs (JSONL traces, judge outputs, summaries) are written under `artifacts/`.

## What an eval is (pattern)

Prompt(s) → captured run (JSONL trace + filesystem artifacts) → deterministic checks → optional rubric-based grading (structured JSON) → score you can compare over time.

## Layout

- `evals/schemas/` — JSON Schemas for structured grading outputs
- `evals/skills/` — per-skill eval cases (curated over time)
- `evals/skill_evaluation.md` — how the eval mechanism works
