#!/usr/bin/env python3

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional


EVOLUTION_FILENAME = "evolution.json"
MARKER_BEGIN = "<!-- PKB:EVOLUTION:BEGIN -->"
MARKER_END = "<!-- PKB:EVOLUTION:END -->"

_ALLOWED_LIST_KEYS = ("preferences", "fixes", "pitfalls", "verification")
_ALLOWED_KEYS = set(("version", "updated_at", "examples", *_ALLOWED_LIST_KEYS))


class EvolutionError(RuntimeError):
    pass


def _now_iso_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _clean_line(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _dedupe_preserve_order(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for raw in items:
        if not isinstance(raw, str):
            continue
        item = _clean_line(raw)
        if not item:
            continue
        if len(item) > 600:
            item = item[:600].rstrip() + "…"
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def parse_frontmatter_name(skill_md: Path) -> str:
    lines = skill_md.read_text(encoding="utf-8", errors="replace").splitlines()
    if not lines or lines[0].strip() != "---":
        raise EvolutionError(f"SKILL.md missing frontmatter: {skill_md}")
    for line in lines[1:200]:
        if line.strip() == "---":
            break
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip().strip("'\"")
    raise EvolutionError(f"SKILL.md missing frontmatter name: {skill_md}")


def load_json_from_arg(json_arg: Optional[str], json_path: Optional[Path]) -> dict[str, Any]:
    if json_arg and json_path:
        raise EvolutionError("Pass only one of --json or --json-file.")
    if json_path:
        return json.loads(json_path.read_text(encoding="utf-8"))
    if json_arg:
        return json.loads(json_arg)
    raise EvolutionError("Missing JSON input: pass --json or --json-file.")


def normalize_delta(delta: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(delta, dict):
        raise EvolutionError("Evolution delta must be a JSON object.")
    unknown = set(delta.keys()) - _ALLOWED_KEYS
    if unknown:
        raise EvolutionError(f"Unknown evolution keys: {sorted(unknown)}")

    normalized: dict[str, Any] = {}
    for k in _ALLOWED_LIST_KEYS:
        v = delta.get(k)
        if v is None:
            continue
        if not isinstance(v, list):
            raise EvolutionError(f"Key {k!r} must be a list of strings.")
        normalized[k] = _dedupe_preserve_order(v)

    examples = delta.get("examples")
    if examples is not None:
        if not isinstance(examples, list):
            raise EvolutionError("Key 'examples' must be a list.")
        norm_examples: list[dict[str, str]] = []
        for ex in examples:
            if not isinstance(ex, dict):
                continue
            cmd = ex.get("command")
            if not isinstance(cmd, str) or not _clean_line(cmd):
                continue
            title = ex.get("title")
            expected = ex.get("expected")
            item: dict[str, str] = {"command": _clean_line(cmd)}
            if isinstance(title, str) and _clean_line(title):
                item["title"] = _clean_line(title)[:200]
            if isinstance(expected, str) and _clean_line(expected):
                item["expected"] = _clean_line(expected)[:300]
            norm_examples.append(item)
        normalized["examples"] = norm_examples[:50]

    return normalized


def load_evolution(skill_dir: Path) -> dict[str, Any]:
    path = skill_dir / EVOLUTION_FILENAME
    if not path.is_file():
        return {"version": 1}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise EvolutionError(f"Invalid evolution file (expected object): {path}")
        return data
    except json.JSONDecodeError as e:
        raise EvolutionError(f"Invalid JSON in {path}: {e}") from e


def merge_evolution(existing: dict[str, Any], delta: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {"version": int(existing.get("version") or 1)}
    out["updated_at"] = _now_iso_utc()

    for k in _ALLOWED_LIST_KEYS:
        merged = []
        if isinstance(existing.get(k), list):
            merged.extend(existing.get(k))
        if isinstance(delta.get(k), list):
            merged.extend(delta.get(k))
        if merged:
            out[k] = _dedupe_preserve_order(merged)[:200]

    existing_examples = existing.get("examples")
    delta_examples = delta.get("examples")
    examples: list[dict[str, str]] = []
    if isinstance(existing_examples, list):
        examples.extend([x for x in existing_examples if isinstance(x, dict)])
    if isinstance(delta_examples, list):
        examples.extend([x for x in delta_examples if isinstance(x, dict)])
    if examples:
        dedup: dict[str, dict[str, str]] = {}
        for ex in examples:
            cmd = ex.get("command")
            if not isinstance(cmd, str) or not _clean_line(cmd):
                continue
            key = _clean_line(cmd)
            if key in dedup:
                continue
            item: dict[str, str] = {"command": _clean_line(cmd)}
            title = ex.get("title")
            expected = ex.get("expected")
            if isinstance(title, str) and _clean_line(title):
                item["title"] = _clean_line(title)[:200]
            if isinstance(expected, str) and _clean_line(expected):
                item["expected"] = _clean_line(expected)[:300]
            dedup[key] = item
        out["examples"] = list(dedup.values())[:100]

    return out


def write_evolution(skill_dir: Path, evolution: dict[str, Any]) -> Path:
    path = skill_dir / EVOLUTION_FILENAME
    path.write_text(
        json.dumps(evolution, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path


def _render_list_section(title: str, items: list[str]) -> str:
    if not items:
        return ""
    lines = [f"### {title}", ""]
    for item in items:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def render_learned_markdown(evolution: dict[str, Any]) -> str:
    parts: list[str] = []
    parts.append(MARKER_BEGIN)
    parts.append("## Learned (session-derived)")
    parts.append("")
    parts.append(
        "This section is generated from `evolution.json` by `uv-skill-evolution-manager`. "
        "Edits should go through `evolution.json` and `scripts/smart_stitch.py` so the content survives updates."
    )
    parts.append("")

    for key, header in (
        ("preferences", "Preferences"),
        ("fixes", "Fixes"),
        ("pitfalls", "Pitfalls"),
        ("verification", "Verification"),
    ):
        items = evolution.get(key)
        if isinstance(items, list):
            rendered = _render_list_section(header, _dedupe_preserve_order(items))
            if rendered:
                parts.append(rendered.rstrip())

    examples = evolution.get("examples")
    if isinstance(examples, list) and examples:
        parts.append("### Examples")
        parts.append("")
        for ex in examples[:50]:
            if not isinstance(ex, dict):
                continue
            cmd = ex.get("command")
            if not isinstance(cmd, str) or not _clean_line(cmd):
                continue
            title = ex.get("title")
            expected = ex.get("expected")
            if isinstance(title, str) and _clean_line(title):
                parts.append(f"- **{_clean_line(title)}**")
            parts.append(f"  - Command: `{_clean_line(cmd)}`")
            if isinstance(expected, str) and _clean_line(expected):
                parts.append(f"  - Expected: `{_clean_line(expected)}`")
        parts.append("")

    parts.append(MARKER_END)
    parts.append("")
    return "\n".join(parts)


@dataclass(frozen=True)
class StitchResult:
    skill_md: Path
    evolution_json: Path
    inserted: bool


def stitch_skill_md(skill_dir: Path) -> StitchResult:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        raise EvolutionError(f"Missing SKILL.md in skill dir: {skill_dir}")

    evolution_json_path = skill_dir / EVOLUTION_FILENAME
    if not evolution_json_path.is_file():
        raise EvolutionError(f"Missing {EVOLUTION_FILENAME} in skill dir: {skill_dir}")

    evolution = load_evolution(skill_dir)
    learned_block = render_learned_markdown(evolution)
    original = skill_md.read_text(encoding="utf-8", errors="replace")

    if MARKER_BEGIN in original and MARKER_END in original:
        pattern = re.compile(
            re.escape(MARKER_BEGIN) + r".*?" + re.escape(MARKER_END) + r"\n?",
            flags=re.DOTALL,
        )
        updated = pattern.sub(learned_block, original)
        inserted = False
    else:
        sep = "" if original.endswith("\n") else "\n"
        updated = original + sep + "\n" + learned_block
        inserted = True

    if updated != original:
        skill_md.write_text(updated, encoding="utf-8")

    return StitchResult(skill_md=skill_md, evolution_json=evolution_json_path, inserted=inserted)

