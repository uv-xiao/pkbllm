---
name: uv-check-modeling-exercise
description: "Check the modeling exercise answers in a local HUMAN materials exercise pack. Use when asked to verify my_answers.json against answers.json, explain mismatches, and provide the worked solution under $HUMAN_MATERIAL_PATH/exercises/<paper_slug>/modeling/."
---

# Check modeling exercise

Run the checker:

```bash
python $HUMAN_MATERIAL_PATH/exercises/<paper_slug>/modeling/check.py
```

If mismatches occur:
- Show the key(s) that differ
- Recompute the relevant steps
- Point to `SOLUTION.md` for the worked explanation

