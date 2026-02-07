---
name: uv-check-programming-exercise
description: "Check the programming exercise answer in a local HUMAN materials exercise pack. Use when asked to run tests, diagnose failures, or compare my_solution.py to the golden solution.py under $HUMAN_MATERIAL_PATH/exercises/<paper_slug>/programming/."
---

# Check programming exercise

Run unit tests:

```bash
python $HUMAN_MATERIAL_PATH/exercises/<paper_slug>/programming/tests.py
```

If tests fail:
- Identify the failing case
- Explain what the expected behavior should be
- Suggest a minimal fix in `my_solution.py`

If requested, reveal or reference `solution.py` as the golden answer.

