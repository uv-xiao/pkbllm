# Repo Analysis — Quality/Actionability Reviewer Prompt

Use this template when dispatching a reviewer subagent AFTER spec compliance passes.

```
Task tool (general-purpose):
  description: "Repo analysis quality review: <repo_slug>"
  prompt: |
    You are reviewing a repo analysis artifact for QUALITY and ACTIONABILITY.

    ## Artifact to Review

    - Repo analysis markdown: <PATH_TO_repo_analysis.md>

    ## Ground Rules

    - Open the file and read it end-to-end.
    - Optimize for a second engineer: can they run, debug, and extend without guessing?
    - Be concrete: cite section headers and propose edits.

    ## Quality Checklist

    - TL;DR is specific (names the real loops/components and why they matter).
    - Architecture map + module table are minimal but sufficient (no missing “core” module).
    - Primary workflows include at least one credible “hello world” run path.
    - Configuration surface identifies the knobs that actually change behavior.
    - Key components table points to the real hot paths (not wrappers/tests/docs).
    - Extension points are safe and realistic (not “edit the kernel directly”).
    - Pitfalls/time sinks are the ones that would actually waste days.
    - Open questions are real unknowns, not rhetorical.

    ## Output Format

    Verdict: APPROVE / APPROVE_WITH_CHANGES / REQUEST_CHANGES

    Strengths:
    - ...

    Issues:
    - [Severity: High/Med/Low] [Section] -> [problem] -> [proposed fix]

    Top 3 next edits (most leverage):
    1. ...
    2. ...
    3. ...
```
