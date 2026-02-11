#!/usr/bin/env python3

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from evolution_lib import EvolutionError, parse_frontmatter_name


CANONICAL_ROOTS = ("bootstrap", "common", "human", "knowledge", "productivity")


@dataclass(frozen=True)
class LocatedSkill:
    root: Path
    skill_dir: Path


def iter_skill_dirs_under(root: Path) -> Iterable[Path]:
    if not root.exists():
        return
    for skill_md in root.rglob("SKILL.md"):
        parent = skill_md.parent
        if parent.name.startswith("."):
            continue
        yield parent


def locate_canonical_skill(pkb_path: Path, skill_name: str) -> Optional[LocatedSkill]:
    for rel in CANONICAL_ROOTS:
        root = pkb_path / rel
        for d in iter_skill_dirs_under(root):
            try:
                name = parse_frontmatter_name(d / "SKILL.md")
            except EvolutionError:
                continue
            if name == skill_name:
                return LocatedSkill(root=root, skill_dir=d)
    return None


def _project_local_roots(project_root: Path) -> list[Path]:
    return [
        project_root / ".agent" / "skills",
        project_root / ".agents" / "skills",
        project_root / ".cursor" / "skills",
        project_root / ".cline" / "skills",
        project_root / ".codex" / "skills",
        project_root / ".claude" / "skills",
    ]


def _user_local_roots(include_all_agents: bool) -> list[Path]:
    home = Path.home()
    roots = [home / ".codex" / "skills"]
    if include_all_agents:
        roots.extend(
            [
                home / ".agents" / "skills",
                home / ".claude" / "skills",
            ]
        )
    return roots


def locate_local_installs(
    skill_name: str,
    project_root: Path,
    extra_roots: Optional[list[Path]] = None,
    include_all_agents: bool = False,
) -> list[LocatedSkill]:
    roots = [p for p in _project_local_roots(project_root) if p.exists()]
    roots.extend([p for p in _user_local_roots(include_all_agents) if p.exists()])
    if extra_roots:
        roots.extend([p for p in extra_roots if p.exists()])

    found: list[LocatedSkill] = []
    for root in roots:
        for d in iter_skill_dirs_under(root):
            skill_md = d / "SKILL.md"
            try:
                name = parse_frontmatter_name(skill_md)
            except EvolutionError:
                continue
            if name == skill_name:
                found.append(LocatedSkill(root=root, skill_dir=d))
    dedup: dict[Path, LocatedSkill] = {x.skill_dir.resolve(): x for x in found}
    return list(dedup.values())


def infer_pkb_path(explicit: Optional[Path]) -> Path:
    if explicit:
        return explicit
    env = Path.cwd()
    for candidate in [env] + list(env.parents):
        if all((candidate / r).exists() for r in ("bootstrap", "skills")):
            return candidate
    raise EvolutionError("Could not infer PKB_PATH from cwd; pass --pkb-path.")

