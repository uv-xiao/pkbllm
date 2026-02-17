# Per-skill eval cases

Curated eval cases (prompts + expectations) live under:

`evals/skills/<skill-slug>/`

The eval runner will also generate a default smoke suite when curated cases are missing, but curated cases are preferred for real coverage.

## Recommended format

Create `evals/skills/<skill-slug>/prompts.csv` with:

```csv
id,should_trigger,prompt
explicit,true,"Do X using the $uv-skill-name skill"
implicit,true,"Do X (without naming the skill)"
negative,false,"Adjacent request that should not match this skill"
```

Add more rows as you discover real failures/regressions.

