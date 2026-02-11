# Tutorial — Quality/Teaching Reviewer Prompt

Use this template when dispatching a reviewer subagent AFTER spec compliance passes.

```
Task tool (general-purpose):
  description: "Tutorial quality review: <topic_slug>"
  prompt: |
    You are reviewing a tutorial artifact for QUALITY (teaching + usability).

    ## Artifact to Review

    - Tutorial root folder: <PATH_TO_exercises/tutorials/<topic_slug>/>

    ## Ground Rules

    - Read the root `README.md` first, then go chapter by chapter in order.
    - Optimize for a reader who has the repo analysis but not your brain.
    - Be concrete: cite file + section and propose edits.

    ## Quality Checklist

    - The learning path is coherent and incremental (no big concept jumps).
    - Conceptual models match the code tour (vocabulary is consistent).
    - Runnable examples are minimal and targeted (not a huge benchmark first).
    - Exercises reinforce the chapter's mental model and are realistically doable.
    - The tutorial points back to repo analysis / hands-on evidence at the right moments.
    - No “trust me” sections: unclear claims are backed by code pointers or output.

    ## Output Format

    Verdict: APPROVE / APPROVE_WITH_CHANGES / REQUEST_CHANGES

    Strengths:
    - ...

    Issues:
    - [Severity: High/Med/Low] [file] [section] -> [problem] -> [proposed fix]

    Top 3 next edits (most leverage):
    1. ...
    2. ...
    3. ...
```
