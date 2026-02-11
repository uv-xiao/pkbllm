# Repo Analysis — Spec Compliance Reviewer Prompt

Use this template when dispatching a reviewer subagent to verify a `repo_analysis.md` meets the skill’s non-negotiables.

```
Task tool (general-purpose):
  description: "Repo analysis spec compliance review: <repo_slug>"
  prompt: |
    You are reviewing a repo analysis artifact for SPEC COMPLIANCE.

    ## Artifact to Review

    - Repo analysis markdown: <PATH_TO_repo_analysis.md>

    ## Ground Rules

    - Do NOT trust the author's claims. Open the file and verify directly.
    - Be strict: this is a gate. If any non-negotiable is missing, FAIL.
    - Prefer specific citations: section header + exact snippet (1 line) + what to change.

    ## Non-Negotiables (Must Pass)

    - Actionable: contains real paths and file:line pointers (not vague descriptions).
    - No placeholders: no `<...>` and no `{like_this}` template markers remain anywhere.
    - Includes: TL;DR, architecture map, module map table, primary workflows, key components table (>= 6 entries).
    - Claims grounded: any “does X” behavior claim has a file:line pointer or a linked evidence artifact.

    ## LLM-Specific Gate (Only If LLM-related == yes)

    Verify the doc includes, grounded in code with file:line pointers:
    - prefill vs decode loop (real nesting, not generic transformer pseudocode)
    - KV cache (layout + update path)
    - scheduler/batching
    - sampling/decoding

    ## Output Format

    Verdict: PASS/FAIL

    Blocking issues (if any):
    1. [Section] - [1-line snippet] -> [required fix]
    2. ...

    Non-blocking suggestions (optional):
    - ...
```
