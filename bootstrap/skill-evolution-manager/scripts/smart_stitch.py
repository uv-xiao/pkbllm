#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from evolution_lib import EvolutionError, stitch_skill_md


def main() -> int:
    parser = argparse.ArgumentParser(description="Stitch the Learned section into <skill_dir>/SKILL.md from evolution.json.")
    parser.add_argument("skill_dir", type=Path, help="Skill directory containing SKILL.md and evolution.json")
    args = parser.parse_args()

    try:
        res = stitch_skill_md(args.skill_dir)
        action = "inserted" if res.inserted else "updated"
        print(f"{action}: {res.skill_md}")
        return 0
    except EvolutionError as e:
        print(f"error: {e}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

