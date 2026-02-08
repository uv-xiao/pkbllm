---
name: uv-create-paper-exercises
description: "Create learning exercises from a research paper (arXiv URL/PDF). Use when turning a paper into (1) a programming exercise (extract the core technique into a coding problem with tests) and (2) a modeling exercise (extract formulas/reasoning into calculation problems with worked solutions). Generates an exercise pack under $HUMAN_MATERIAL_PATH/exercises/<paper_slug>/ including local mini-skills to check answers and reveal golden solutions."
---

# Create exercises from a paper

## Goal

From a single paper, generate two exercise tracks:

1. **Programming**: turn the central technique into a coding problem with a crisp spec + tests.
2. **Modeling**: turn the paper’s formulas/derivations into calculation problems with worked solutions.

The output should be an exercise pack with:
- Clear prompts
- Golden solutions
- Automated checkers
- Local mini-skills to check answers on demand

## Output location

Create the pack under:

- `$HUMAN_MATERIAL_PATH/exercises/<paper_slug>/`

Downloads/clones should go under (gitignored):

- `$HUMAN_MATERIAL_PATH/.references/` (PDFs, arXiv zips, cloned repos)

## Scaffold the pack

Use the scaffold script to create the file structure:

```bash
# Run from this skill directory (the folder containing this SKILL.md):
python scripts/scaffold_exercise_pack.py --slug <paper_slug>
```

Then fill in the prompts/solutions based on the paper.

## Programming exercise workflow

1. **Find the central technique**:
   - Identify the smallest “core loop” that makes the method work (data structure + algorithm).
2. **Extract a clean problem**:
   - Define input/output precisely.
   - Specify constraints.
   - Provide 2–3 small examples.
3. **Create a testable interface**:
   - Implement as a single function in `my_solution.py` (user) and `solution.py` (golden).
4. **Write tests**:
   - Include edge cases and one randomized property check (if applicable).
5. **(Optional) Use the paper’s code repo**:
   - If the paper links code, clone it under `$HUMAN_MATERIAL_PATH/.references/repos/`.
   - Read it for correctness and for test cases; do not copy large chunks verbatim.

## Modeling exercise workflow

1. **Locate the modeling logic**:
   - The key formula(s), scaling law(s), or performance reasoning in the paper.
2. **Turn it into 3–6 questions**:
   - Use numbers so the learner can compute concrete outputs.
   - Include at least one “interpret the result” question.
3. **Provide golden answers + explanations**:
   - `answers.json` for numeric targets
   - `SOLUTION.md` for step-by-step reasoning
4. **Add a checker**:
   - Compare `my_answers.json` against `answers.json` with tolerances.

## Local answer-checking mini-skills

The scaffold creates two local mini-skills under:
- `$HUMAN_MATERIAL_PATH/exercises/<paper_slug>/skills/uv-check-programming/`
- `$HUMAN_MATERIAL_PATH/exercises/<paper_slug>/skills/uv-check-modeling/`

Use them to:
- Run checks
- Print diffs / failed tests
- Reveal golden solutions + explanations when asked
