# Hands-on Learning — Spec Compliance / Evidence Reviewer Prompt

Use this template when dispatching a reviewer subagent to verify a hands-on session meets requirements and is evidence-backed.

```
Task tool (general-purpose):
  description: "Hands-on session spec compliance review: <repo_slug>/<session>"
  prompt: |
    You are reviewing a hands-on learning session for SPEC COMPLIANCE and EVIDENCE.

    ## Session Root

    - Session directory: <PATH_TO_hands_on/<session>/>

    ## Ground Rules

    - Do NOT trust the author's claims. Open the files and verify directly.
    - Be strict: this is a gate. If any requirement is missing, FAIL.
    - Cite issues by file path + section header, and point to the evidence gap.

    ## Required Structure (Must Exist)

    - `reports/INDEX.md`
    - `reports/environment.md`
    - `reports/plan.md`
    - `reports/report.md`
    - `results/` exists and contains raw outputs referenced by the reports (gitignored is fine)
    - `scripts/` contains runnable helpers (at least one actual run command exists somewhere in the session)

    ## Evidence Gates (Must Pass)

    - `reports/environment.md` includes toolchain + package versions and links to raw evidence under `results/`.
    - `reports/plan.md` includes falsifiable hypotheses and a runnable workload matrix (not a wish list).
    - `reports/report.md` includes a “What I ran” table with exact commands.
    - Every nontrivial claim in `reports/report.md` is supported by:
      - a short excerpt (few lines), AND
      - a link/path to a raw artifact under `results/`.
    - If any run failed: `reports/report.md` includes the full error text, exact command, and unblock steps.

    ## Output Format

    Verdict: PASS/FAIL

    Blocking issues:
    1. [file] [section] -> [what's missing/wrong] -> [required fix]
    2. ...

    Non-blocking suggestions (optional):
    - ...
```
