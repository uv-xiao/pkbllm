#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from evolution_lib import (
    EvolutionError,
    load_evolution,
    load_json_from_arg,
    merge_evolution,
    normalize_delta,
    stitch_skill_md,
    write_evolution,
)
from skill_locator import infer_pkb_path, locate_canonical_skill, locate_local_installs


def _apply_to_skill_dir(skill_dir: Path, delta: dict) -> None:
    existing = load_evolution(skill_dir)
    merged = merge_evolution(existing, delta)
    write_evolution(skill_dir, merged)
    stitch_skill_md(skill_dir)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Apply an evolution JSON delta to canonical skills (PKB_PATH), local installs, or both."
    )
    parser.add_argument("--skill-name", required=True, help="Skill frontmatter name (e.g. uv-hands-on-learning)")
    parser.add_argument("--scope", choices=("pkb", "local", "both"), default="both")
    parser.add_argument("--json", dest="json_arg", help="JSON delta object string")
    parser.add_argument("--json-file", type=Path, help="Path to JSON delta file")
    parser.add_argument("--pkb-path", type=Path, help="Path to pkbllm repo root (PKB_PATH)")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root to scan for local installs (default: cwd)",
    )
    parser.add_argument(
        "--extra-local-root",
        type=Path,
        action="append",
        default=[],
        help="Extra root(s) to scan for local installs (repeatable)",
    )
    parser.add_argument(
        "--include-all-agents",
        action="store_true",
        help="Also scan and update user-scope multi-agent installs (e.g. ~/.agents/skills).",
    )
    args = parser.parse_args()

    try:
        delta_raw = load_json_from_arg(args.json_arg, args.json_file)
        delta = normalize_delta(delta_raw)
    except EvolutionError as e:
        print(f"error: {e}")
        return 2

    skill_name = args.skill_name.strip()
    if not skill_name.startswith("uv-"):
        print("error: --skill-name must start with 'uv-'.")
        return 2

    failures: list[str] = []

    if args.scope in ("pkb", "both"):
        try:
            pkb_path = infer_pkb_path(args.pkb_path)
            located = locate_canonical_skill(pkb_path, skill_name)
            if not located:
                failures.append(f"pkb: not found: {skill_name}")
            else:
                _apply_to_skill_dir(located.skill_dir, delta)
                print(f"pkb: updated {located.skill_dir}")
        except EvolutionError as e:
            failures.append(f"pkb: {e}")

    if args.scope in ("local", "both"):
        installs = locate_local_installs(
            skill_name=skill_name,
            project_root=args.project_root,
            extra_roots=args.extra_local_root or None,
            include_all_agents=args.include_all_agents,
        )
        if not installs:
            print("local: no installs found (skipped)")
        else:
            for located in sorted(installs, key=lambda x: str(x.skill_dir)):
                try:
                    _apply_to_skill_dir(located.skill_dir, delta)
                    print(f"local: updated {located.skill_dir}")
                except EvolutionError as e:
                    failures.append(f"local: {located.skill_dir}: {e}")

    if failures:
        print("errors:")
        for f in failures:
            print(f"- {f}")
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

