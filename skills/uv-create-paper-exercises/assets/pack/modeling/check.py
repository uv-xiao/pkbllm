#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from pathlib import Path


def _as_number(value):
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        return float(value.strip())
    raise TypeError(f"not a number: {value!r}")


def main() -> int:
    root = Path(__file__).resolve().parent
    golden = json.loads((root / "answers.json").read_text(encoding="utf-8"))
    mine = json.loads((root / "my_answers.json").read_text(encoding="utf-8"))

    tol_abs = 1e-6
    tol_rel = 1e-6

    ok = True
    for k, gv in golden.items():
        if k not in mine:
            print(f"Missing key: {k}")
            ok = False
            continue
        try:
            g = _as_number(gv)
            m = _as_number(mine[k])
        except Exception as e:
            print(f"Bad value for {k}: {e}")
            ok = False
            continue
        if not math.isclose(g, m, rel_tol=tol_rel, abs_tol=tol_abs):
            print(f"Mismatch {k}: got {m} expected {g}")
            ok = False
    extra = sorted(set(mine.keys()) - set(golden.keys()))
    for k in extra:
        print(f"Extra key (ignored): {k}")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
