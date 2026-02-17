#!/usr/bin/env python3

from __future__ import annotations

import csv
from pathlib import Path

from skill_eval_lib import EVALS_SKILLS_ROOT, discover_skills, ensure_dir


def _write_prompts_csv(path: Path, rows: list[dict[str, str]]) -> None:
    ensure_dir(path.parent)
    fieldnames = [
        "id",
        "should_trigger",
        "prompt",
        "sandbox",
        "timeout_s",
        "max_commands",
        "output_schema",
        "judge",
        "require_files",
        "must_include",
        "must_not_include",
        "fixture",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})


def main() -> int:
    skills = discover_skills()
    default_schema = "evals/schemas/skill_response.schema.json"

    import argparse

    ap = argparse.ArgumentParser(description="Generate per-skill eval prompts.csv files.")
    ap.add_argument("--overwrite", action="store_true", help="Overwrite existing prompts.csv.")
    args = ap.parse_args()

    created = 0
    overwritten = 0
    skipped = 0
    for s in skills:
        skill_dir = EVALS_SKILLS_ROOT / s.slug
        prompts_csv = skill_dir / "prompts.csv"
        if prompts_csv.exists() and not args.overwrite:
            skipped += 1
            continue
        if prompts_csv.exists() and args.overwrite:
            overwritten += 1

        # Baseline: read-only, structured output, no commands.
        base_prompt = (
            "You are being evaluated. If you use any skill(s), list their names in `invoked_skills`.\n\n"
            "Return a JSON object that matches the provided output schema.\n\n"
        )

        explicit = {
            "id": "explicit",
            "should_trigger": "true",
            "prompt": base_prompt
            + f"Use the ${s.name} skill.\n\n"
            + "Task: Provide the smallest correct, actionable response for a realistic scenario covered by the skill.\n"
            + "Constraints: do not execute commands; do not write files.\n\n"
            + f"Scenario (from skill description): {s.description or '(missing)'}\n",
            "sandbox": "read-only",
            "timeout_s": "120",
            "max_commands": "0",
            "output_schema": default_schema,
            "judge": "true",
            "must_include": f"\\\"{s.name}\\\"",
        }

        implicit = {
            "id": "implicit",
            "should_trigger": "true",
            "prompt": base_prompt
            + "Do not mention any skill name.\n\n"
            + "Task: Respond as you would in a real session.\n"
            + "Constraints: do not execute commands; do not write files.\n\n"
            + f"User request: {s.description or '(missing)'}\n",
            "sandbox": "read-only",
            "timeout_s": "120",
            "max_commands": "0",
            "output_schema": default_schema,
            "judge": "true",
            "must_include": f"\\\"{s.name}\\\"",
        }

        negative = {
            "id": "negative",
            "should_trigger": "false",
            "prompt": base_prompt
            + "Do not mention any skill name.\n\n"
            + "User request: Give me a 1-sentence explanation of what a binary search is.\n"
            + "Constraints: do not execute commands; do not write files.\n",
            "sandbox": "read-only",
            "timeout_s": "90",
            "max_commands": "0",
            "output_schema": default_schema,
            "judge": "true",
            "must_not_include": f"\\\"{s.name}\\\"",
        }

        rows = [explicit, implicit, negative]

        # Deterministic E2E cases for script-backed skills where we can verify tangible outputs
        # without relying on external network/API access.
        if s.slug == "uv-init-human-material-repo":
            rows.append(
                {
                    "id": "init-e2e",
                    "should_trigger": "true",
                    "prompt": (
                        "Use the $uv-init-human-material-repo skill.\n\n"
                        "Task: Initialize the human materials repo at $HUMAN_MATERIAL_PATH by running:\n"
                        "`python human/init-human-material-repo/scripts/init_human_material_repo.py`\n\n"
                        "Then verify these files exist under $HUMAN_MATERIAL_PATH:\n"
                        "- `.agents/config.toml`\n"
                        "- `slides/README.md`\n"
                    ),
                    "sandbox": "workspace-write",
                    "timeout_s": "180",
                    "max_commands": "8",
                    "output_schema": "",
                    "judge": "false",
                    "require_files": "human_materials/.agents/config.toml;human_materials/slides/README.md",
                    "fixture": "",
                }
            )

        if s.slug == "uv-create-paper-exercises":
            rows.append(
                {
                    "id": "scaffold-e2e",
                    "should_trigger": "true",
                    "prompt": (
                        "Use the $uv-create-paper-exercises skill.\n\n"
                        "Task: Scaffold a paper exercise pack under $HUMAN_MATERIAL_PATH by running:\n"
                        "`python human/exercises/create-paper-exercises/scripts/scaffold_exercise_pack.py --slug test-paper`\n\n"
                        "Then verify these files exist:\n"
                        "- `$HUMAN_MATERIAL_PATH/exercises/test-paper/README.md`\n"
                        "- `$HUMAN_MATERIAL_PATH/exercises/test-paper/skills/uv-check-programming/SKILL.md`\n"
                    ),
                    "sandbox": "workspace-write",
                    "timeout_s": "180",
                    "max_commands": "8",
                    "output_schema": "",
                    "judge": "false",
                    "require_files": (
                        "human_materials/exercises/test-paper/README.md;"
                        "human_materials/exercises/test-paper/skills/uv-check-programming/SKILL.md"
                    ),
                    "fixture": "",
                }
            )

        if s.slug == "uv-tutorial-generator":
            rows.append(
                {
                    "id": "init-tutorial-e2e",
                    "should_trigger": "true",
                    "prompt": (
                        "Use the $uv-tutorial-generator skill.\n\n"
                        "Task: Initialize a tutorial under $HUMAN_MATERIAL_PATH by running:\n"
                        "`python human/exercises/tutorial-generator/scripts/init_tutorial.py --topic vllm-internals --chapter intro`\n\n"
                        "Then verify these files exist:\n"
                        "- `$HUMAN_MATERIAL_PATH/exercises/tutorials/vllm-internals/README.md`\n"
                        "- `$HUMAN_MATERIAL_PATH/exercises/tutorials/vllm-internals/chapters/01_intro/README.md`\n"
                    ),
                    "sandbox": "workspace-write",
                    "timeout_s": "180",
                    "max_commands": "10",
                    "output_schema": "",
                    "judge": "false",
                    "require_files": (
                        "human_materials/exercises/tutorials/vllm-internals/README.md;"
                        "human_materials/exercises/tutorials/vllm-internals/chapters/01_intro/README.md"
                    ),
                    "fixture": "",
                }
            )

        if s.slug == "uv-repo-analysis":
            rows.append(
                {
                    "id": "init-e2e",
                    "should_trigger": "true",
                    "prompt": (
                        "Use the $uv-repo-analysis skill.\n\n"
                        "Task:\n"
                        "1) Create a tiny local git repo in the current directory:\n"
                        "   - `mkdir -p dummy_repo && git init dummy_repo`\n"
                        "2) Initialize a repo-analysis workspace under $HUMAN_MATERIAL_PATH for that repo:\n"
                        "   - `python human/repo-analysis/scripts/init_repo_analysis.py ./dummy_repo --slug dummy`\n\n"
                        "Then verify `$HUMAN_MATERIAL_PATH/research/dummy/repo_analysis.md` exists.\n"
                    ),
                    "sandbox": "workspace-write",
                    "timeout_s": "240",
                    "max_commands": "12",
                    "output_schema": "",
                    "judge": "false",
                    "require_files": "human_materials/research/dummy/repo_analysis.md",
                    "fixture": "",
                }
            )

        if s.slug == "uv-hands-on-learning":
            rows.append(
                {
                    "id": "init-session-e2e",
                    "should_trigger": "true",
                    "prompt": (
                        "Use the $uv-hands-on-learning skill.\n\n"
                        "Task:\n"
                        "1) Create a tiny local git repo in the current directory:\n"
                        "   - `mkdir -p dummy_repo && git init dummy_repo`\n"
                        "2) Initialize a hands-on session under $HUMAN_MATERIAL_PATH for that repo:\n"
                        "   - `python human/hands-on-learning/scripts/init_hands_on_session.py ./dummy_repo --slug dummy --session test`\n\n"
                        "Then verify these files exist:\n"
                        "- `$HUMAN_MATERIAL_PATH/research/dummy/hands_on/test/reports/INDEX.md`\n"
                        "- `$HUMAN_MATERIAL_PATH/research/dummy/hands_on/test/reports/environment.md`\n"
                    ),
                    "sandbox": "workspace-write",
                    "timeout_s": "300",
                    "max_commands": "16",
                    "output_schema": "",
                    "judge": "false",
                    "require_files": (
                        "human_materials/research/dummy/hands_on/test/reports/INDEX.md;"
                        "human_materials/research/dummy/hands_on/test/reports/environment.md"
                    ),
                    "fixture": "",
                }
            )

        if s.slug == "uv-research-project-docs":
            rows.append(
                {
                    "id": "docs-e2e",
                    "should_trigger": "true",
                    "prompt": (
                        "Use the $uv-research-project-docs skill.\n\n"
                        "Task: Scaffold the research-project docs template into a new local repo directory by running:\n"
                        "`python productivity/research-project-docs/scripts/init_research_project_docs.py --project-root ./project --docs-root docs`\n\n"
                        "Then verify these files exist:\n"
                        "- `project/docs/spec.md`\n"
                        "- `project/docs/evals/_template.md`\n"
                    ),
                    "sandbox": "workspace-write",
                    "timeout_s": "180",
                    "max_commands": "8",
                    "output_schema": "",
                    "judge": "false",
                    "require_files": "project/docs/spec.md;project/docs/evals/_template.md",
                    "fixture": "",
                }
            )

        # Add a special, deterministic E2E for the mirror-regeneration skill.
        if s.slug == "uv-bootstrap-skill-maintenance":
            rows.append(
                {
                    "id": "mirror-e2e",
                    "should_trigger": "true",
                    "prompt": (
                        "Use the $uv-bootstrap-skill-maintenance skill.\n\n"
                        "Task: Regenerate the skills mirror in this repo by running:\n"
                        "`python bootstrap/scripts/update_skills_mirror.py all`\n\n"
                        "Then verify `skills/manifest.json` exists.\n"
                    ),
                    "sandbox": "workspace-write",
                    "timeout_s": "180",
                    "max_commands": "6",
                    "output_schema": "",
                    "judge": "false",
                    "require_files": "skills/manifest.json",
                    "fixture": "fixtures/mirror-e2e",
                }
            )

        _write_prompts_csv(prompts_csv, rows)
        if not args.overwrite:
            created += 1

    print(f"created: {created}")
    print(f"overwritten: {overwritten}")
    print(f"skipped: {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
