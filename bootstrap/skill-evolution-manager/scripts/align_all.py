#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from evolution_lib import EVOLUTION_FILENAME, EvolutionError, stitch_skill_md
from skill_locator import CANONICAL_ROOTS, infer_pkb_path, iter_skill_dirs_under


def _stitch_if_present(skill_dir: Path) -> bool:
    if not (skill_dir / "SKILL.md").is_file():
        return False
    if not (skill_dir / EVOLUTION_FILENAME).is_file():
        return False
    stitch_skill_md(skill_dir)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Re-stitch Learned sections for all skills that have evolution.json.")
    parser.add_argument("--scope", choices=("pkb", "local", "both"), default="both")
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

    stitched = 0
    failures: list[str] = []

    if args.scope in ("pkb", "both"):
        try:
            pkb_path = infer_pkb_path(args.pkb_path)
            for rel in CANONICAL_ROOTS:
                root = pkb_path / rel
                for d in iter_skill_dirs_under(root):
                    try:
                        if _stitch_if_present(d):
                            stitched += 1
                    except EvolutionError as e:
                        failures.append(f"pkb: {d}: {e}")
        except EvolutionError as e:
            failures.append(f"pkb: {e}")

    if args.scope in ("local", "both"):
        roots = [
            args.project_root / ".agent" / "skills",
            args.project_root / ".agents" / "skills",
            args.project_root / ".cursor" / "skills",
            args.project_root / ".cline" / "skills",
            args.project_root / ".codex" / "skills",
            args.project_root / ".claude" / "skills",
            Path.home() / ".codex" / "skills",
            *args.extra_local_root,
        ]
        if args.include_all_agents:
            roots.extend(
                [
                    Path.home() / ".agents" / "skills",
                    Path.home() / ".claude" / "skills",
                ]
            )
        for root in [r for r in roots if r.exists()]:
            for d in iter_skill_dirs_under(root):
                try:
                    if _stitch_if_present(d):
                        stitched += 1
                except EvolutionError as e:
                    failures.append(f"local: {d}: {e}")

    print(f"stitched: {stitched}")
    if failures:
        print("errors:")
        for f in failures:
            print(f"- {f}")
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

