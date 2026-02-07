# pkbllm — Personal Knowledge Base for LLM Work

`pkbllm` is a structured collection of **agent skills** (reusable instruction sets) plus
lightweight **knowledge organization** to help:

- Humans stay effective as LLM tooling evolves
- Coding/research agents work more reliably (planning, testing, reviews, execution)

This repo is designed to be installable with the Skills CLI (`npx skills`) while still
keeping a maintainable, curated internal structure.

## What’s included

- **Productivity skills** for engineering workflows (imported from `obra/superpowers`)
- **ML / research skills** (imported from `Orchestra-Research/AI-research-SKILLs`)
- **Human-material skills** for slides and artifacts (imported from `uv-xiao/slider`)
- A **generated `skills/` mirror** compatible with `npx skills`

## Quickstart

List available skills:

```bash
npx skills add . --list
```

Install everything to Codex (project scope):

```bash
npx skills add . -a codex --skill '*' -y
```

See `INSTALL.md` for more install options and environment variables.

## Repo layout

Canonical (curated) skill locations:

- `productivity/` — day-to-day engineering skills
- `knowledge/` — domain and research skills
- `human/` — skills for generating human-facing materials
- `bootstrap/` — scripts to maintain this repo

Distribution surface for the Skills CLI:

- `skills/` — generated mirror of all skills (direct children are skills)

Reference repositories (optional, not committed):

- `.references/` — local clones used for one-time bootstrapping (skills evolve in this repo after import)

## Maintaining the `skills/` mirror

Canonical skills live under `knowledge/`, `productivity/`, `human/`, and `bootstrap/`.

The top-level `skills/` directory is a generated mirror intended for `npx skills`. After adding or
editing canonical skills, regenerate the mirror and refresh README indexes:

```bash
python bootstrap/scripts/update_skills_mirror.py all
```

## References

- `obra/superpowers` — productive engineering workflow skills
- `Orchestra-Research/AI-research-SKILLs` — ML/research tool skills
- `uv-xiao/slider` — slide/artifact generation skills
- `vercel-labs/skills` — Skills CLI ecosystem conventions

## License

- Repository license: see `LICENSE`
- Third-party notices: see `THIRD_PARTY_NOTICES.md`

## <TABLE>
<!-- PKBLLM_TABLE_START -->
| Path | Type | Description |
| --- | --- | --- |
| `common/` | dir | Shared cross-domain skills |
| `knowledge/` | dir | Domain and research skills |
| `productivity/` | dir | Engineering workflow skills |
| `human/` | dir | Skills for human-facing materials |
| `bootstrap/` | dir | Repository maintenance scripts |
| `skills/` | dir | Generated Skills-CLI mirror (do not edit) |
| `INSTALL.md` | file | Installation instructions |
| `LICENSE` | file | Repository license |
| `THIRD_PARTY_NOTICES.md` | file | Third-party notices and licenses |
<!-- PKBLLM_TABLE_END -->
