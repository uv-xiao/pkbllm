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
    write_evolution,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge a JSON delta into <skill_dir>/evolution.json (dedupe, stable).")
    parser.add_argument("skill_dir", type=Path, help="Skill directory containing SKILL.md")
    parser.add_argument("--json", dest="json_arg", help="JSON object string to merge")
    parser.add_argument("--json-file", type=Path, help="Path to JSON file to merge")
    args = parser.parse_args()

    try:
        delta_raw = load_json_from_arg(args.json_arg, args.json_file)
        delta = normalize_delta(delta_raw)
        existing = load_evolution(args.skill_dir)
        merged = merge_evolution(existing, delta)
        path = write_evolution(args.skill_dir, merged)
        print(str(path))
        return 0
    except EvolutionError as e:
        print(f"error: {e}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

