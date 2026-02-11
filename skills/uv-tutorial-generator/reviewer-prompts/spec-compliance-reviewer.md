# Tutorial — Spec Compliance Reviewer Prompt

Use this template when dispatching a reviewer subagent to verify a tutorial meets the skill’s non-negotiables.

```
Task tool (general-purpose):
  description: "Tutorial spec compliance review: <topic_slug>"
  prompt: |
    You are reviewing a tutorial artifact for SPEC COMPLIANCE.

    ## Artifact to Review

    - Tutorial root folder: <PATH_TO_exercises/tutorials/<topic_slug>/>

    ## Ground Rules

    - Do NOT trust the author's claims. Open the files and verify directly.
    - Be strict: this is a gate. If any non-negotiable is missing, FAIL.
    - Cite issues by file path + section header (or snippet), and propose concrete fixes.

    ## Non-Negotiables (Must Pass)

    - No placeholders: no `<...>` and no `{like_this}` template markers remain anywhere.
    - Tutorial structure exists: root `README.md` and at least one `chapters/01_*/README.md`.
    - Root `README.md` includes prerequisites and a clear learning path.
    - Each chapter includes:
      - Objectives (2–4 concrete learnings)
      - Conceptual model (diagram + terms)
      - Code tour with file:line pointers
      - Runnable example: command + expected output excerpt
      - Exercises (>= 2) with acceptance criteria (“what counts as correct”)
    - At least one runnable example was actually executed and includes captured expected output.

    ## Output Format

    Verdict: PASS/FAIL

    Blocking issues:
    1. [file] [section] -> [what's missing/wrong] -> [required fix]
    2. ...

    Non-blocking suggestions (optional):
    - ...
```
