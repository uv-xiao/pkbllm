# Hands-on Learning — Quality/Actionability Reviewer Prompt

Use this template when dispatching a reviewer subagent AFTER spec compliance passes.

```
Task tool (general-purpose):
  description: "Hands-on session quality review: <repo_slug>/<session>"
  prompt: |
    You are reviewing a hands-on learning session for QUALITY and ACTIONABILITY.

    ## Session Root

    - Session directory: <PATH_TO_hands_on/<session>/>

    ## Ground Rules

    - Read `reports/INDEX.md` first, then follow the links.
    - Optimize for a second engineer: can they rerun the work and learn from it?
    - Be concrete: cite file + section and propose edits.

    ## Quality Checklist

    - The session focuses on a small number of workloads with clear baselines.
    - Observations are event-level (what happened when) rather than just final numbers.
    - Hypotheses are tied to code locations (file:line) or trace evidence where possible.
    - Next steps are ranked, each with a command or file pointer (not vague “optimize X”).
    - The report distinguishes “I ran this” vs “I believe this” cleanly.
    - The reader can reproduce at least one key result in <30 minutes.

    ## Output Format

    Verdict: APPROVE / APPROVE_WITH_CHANGES / REQUEST_CHANGES

    Strengths:
    - ...

    Issues:
    - [Severity: High/Med/Low] [file] [section] -> [problem] -> [proposed fix]

    Top 3 edits (most leverage):
    1. ...
    2. ...
    3. ...
```
