---
name: uv-bootstrap-skill-linking
description: "Maintain relationships between pkbllm skills so workflows compose cleanly. Use when adding a new skill or changing workflows and you want to (1) decide which skills should be co-invoked, (2) update SKILL.md trigger descriptions and Integration sections, and (3) keep the generated mirror/manifest and README <TABLE> indexes consistent."
---

# Skill linking (relationships between skills)

Skills only “compose” if they explicitly say how. This skill maintains that glue.

## Relationship types

For two skills A and B, decide which applies:

- **Prerequisite:** B assumes A already ran (A creates files/structure B needs).
- **Companion:** A and B should be used together in the same workflow.
- **Follow-up:** B should be invoked after A produces an artifact (plan → execution, feature → docs sync).
- **Escalation:** B is used when A hits failure modes (execution → debugging).

## Add or update a relationship (workflow)

1. Identify the concrete scenario (“when does a user need both?”).
2. Pick one relationship type from the list above.
3. Update **both** skills (canonical folders only):
   - In skill A: add a short “Integration” section (or update it) with a bullet like:
     - “When doing X, also use `uv-skill-b` to do Y.”
   - In skill B: add a reciprocal bullet:
     - “Use alongside `uv-skill-a` when doing X.”
4. Strengthen **triggering** (frontmatter `description:`):
   - Add “Use when …” phrasing that includes the joint scenario.
   - Avoid platform-specific wording; focus on intent.

## Don’t create dependency loops

If A “requires” B and B “requires” A, neither is actionable. Prefer:

- A lists B as follow-up/companion
- B lists A as prerequisite

## How to check relationships are consistent

Run these from the pkb repo:

```bash
python bootstrap/scripts/update_skills_mirror.py all
rg -n \"Pairs well with|Integration\" -S productivity bootstrap common human knowledge | head
```

Optional: list installable skills:

```bash
npx -y skills add . --list
```

## Common patterns in this repo

- Plan → execute: `uv-writing-plans` ↔ `uv-executing-plans`
- Execute → debug: `uv-executing-plans` ↔ `uv-systematic-debugging`
- Feature change → docs sync: `uv-executing-plans` ↔ `uv-research-project-docs`

