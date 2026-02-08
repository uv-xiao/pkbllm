#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional


def find_repo_root(start: Path) -> Path:
    for candidate in [start] + list(start.parents):
        if (candidate / ".git").exists():
            return candidate
    return start.resolve()


def resolve_human_material_root() -> Optional[Path]:
    target = os.getenv("HUMAN_MATERIAL_PATH")
    if not target:
        return None
    root = Path(target).expanduser()
    if root.exists():
        return root.resolve()
    return None

