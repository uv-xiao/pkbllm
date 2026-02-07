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
    """
    Minimal TOML reader for:

      [pkbllm]
      key = "value"

    Only supports string values. Ignores everything else.
    """
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
        if not in_section:
            continue
        if "=" not in line:
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
    """
    Config precedence (repo overrides user):
      1) ~/.agents/config.toml
      2) <repo_root>/.agents/config.toml
    """
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


def _parse_key_file_text(raw: str) -> Optional[str]:
    raw = raw.strip()
    if not raw:
        return None
    if "OPENROUTER_API_KEY=" in raw:
        for line in raw.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("OPENROUTER_API_KEY="):
                value = line.split("=", 1)[1].strip()
                return value or None
        return None
    return raw


def load_openrouter_api_key(*, repo_root: Path, cfg: dict[str, str]) -> Optional[str]:
    env = os.getenv("OPENROUTER_API_KEY")
    if env:
        return env.strip() or None

    key_file = cfg.get("openrouter_api_key_file", ".OPENROUTER_API_KEY")
    key_path = Path(key_file)
    if not key_path.is_absolute():
        key_path = repo_root / key_path
    if not key_path.exists():
        return None
    try:
        raw = key_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None
    return _parse_key_file_text(raw)


def resolve_human_material_root() -> Optional[Path]:
    target = os.getenv("HUMAN_MATERIAL_PATH")
    if not target:
        return None
    root = Path(target).expanduser()
    if root.exists():
        return root.resolve()
    return None

