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


def _strip_toml_comment(value: str) -> str:
    in_quote = False
    quote_char = ""
    out: list[str] = []
    for ch in value:
        if in_quote:
            out.append(ch)
            if ch == quote_char:
                in_quote = False
                quote_char = ""
            continue
        if ch in {"'", '"'}:
            in_quote = True
            quote_char = ch
            out.append(ch)
            continue
        if ch == "#":
            break
        out.append(ch)
    return "".join(out).strip()


def parse_pkbllm_config(config_path: Path) -> dict[str, str]:
    try:
        lines = config_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return {}

    in_section = False
    out: dict[str, str] = {}
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            in_section = line == "[pkbllm]"
            continue
        if not in_section or "=" not in line:
            continue
        k, v = line.split("=", 1)
        key = k.strip()
        val = _strip_toml_comment(v.strip())
        if val.startswith(("\"", "'")) and val.endswith(("\"", "'")) and len(val) >= 2:
            val = val[1:-1]
        if key and val:
            out[key] = val
    return out


def load_config(repo_root: Path) -> dict[str, str]:
    user_agents_dir = Path.home() / ".agents"
    config_paths = [
        user_agents_dir / "config.toml",
        repo_root / ".agents" / "config.toml",
    ]
    cfg: dict[str, str] = {}
    for cp in config_paths:
        if cp.exists():
            cfg.update(parse_pkbllm_config(cp))
    return cfg


def resolve_config_path(repo_root: Path, cfg: dict[str, str], *, key: str, default_rel: str) -> Path:
    raw = cfg.get(key, default_rel)
    p = Path(raw).expanduser()
    if not p.is_absolute():
        p = repo_root / p
    return p

