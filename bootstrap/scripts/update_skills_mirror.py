#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Iterable, Optional, TypedDict


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "bootstrap" / "scripts" / "update_skills_mirror.config.json"
DEFAULT_README_TABLE_ROOTS = [
    "README.md",
    "bootstrap",
    "common",
    "human",
    "knowledge",
    "productivity",
]


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _rmtree(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
        return
    if path.is_dir():
        shutil.rmtree(path)


def _copytree(src: Path, dst: Path) -> None:
    if dst.exists():
        _rmtree(dst)
    _ensure_dir(dst.parent)
    shutil.copytree(src, dst, copy_function=shutil.copy2)


def _parse_frontmatter_name(skill_md: Path) -> str:
    content = skill_md.read_text(encoding="utf-8", errors="replace").splitlines()
    if not content or content[0].strip() != "---":
        raise ValueError(f"SKILL.md missing frontmatter: {skill_md}")
    for line in content[1:100]:
        if line.strip() == "---":
            break
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip().strip("'\"")
    raise ValueError(f"SKILL.md missing name: {skill_md}")


def _parse_frontmatter_description(skill_md: Path) -> str:
    content = skill_md.read_text(encoding="utf-8", errors="replace").splitlines()
    if not content or content[0].strip() != "---":
        return ""
    for line in content[1:150]:
        if line.strip() == "---":
            break
        if line.startswith("description:"):
            return line.split(":", 1)[1].strip().strip("'\"")
    return ""


def _parse_frontmatter_license(skill_md: Path) -> str:
    content = skill_md.read_text(encoding="utf-8", errors="replace").splitlines()
    if not content or content[0].strip() != "---":
        return ""
    for line in content[1:200]:
        if line.strip() == "---":
            break
        if line.startswith("license:"):
            return line.split(":", 1)[1].strip().strip("'\"")
    return ""


def _is_distributable_license(license_value: str) -> bool:
    if not license_value:
        return True
    lower = license_value.lower()
    if "proprietary" in lower:
        return False
    if "all rights reserved" in lower:
        return False
    return True


_SLUG_BAD = re.compile(r"[^a-z0-9._-]+")


def _skill_slug(name: str) -> str:
    slug = name.strip().lower()
    slug = re.sub(r"\s+", "-", slug)
    slug = slug.replace("/", "").replace("\\", "").replace(":", "")
    slug = _SLUG_BAD.sub("-", slug)
    slug = slug.strip("-")
    if not slug:
        raise ValueError(f"Could not slugify skill name: {name!r}")
    return slug


class SkillManifestEntry(TypedDict):
    name: str
    slug: str
    description: str
    canonical_path: str


def _iter_dirs_with_skill_md(root: Path) -> Iterable[Path]:
    for skill_md in root.rglob("SKILL.md"):
        if skill_md.name != "SKILL.md":
            continue
        parent = skill_md.parent
        if parent.name.startswith("."):
            continue
        yield parent


def build_skills_mirror(
    canonical_roots: list[Path],
) -> list[SkillManifestEntry]:
    skills_root = ROOT / "skills"
    _ensure_dir(skills_root)

    # Clean generated skill folders, keep README.md.
    for entry in skills_root.iterdir():
        if entry.name == "README.md":
            continue
        _rmtree(entry)

    imported: list[SkillManifestEntry] = []
    seen_slugs: dict[str, Path] = {}

    for canonical_root in canonical_roots:
        if not canonical_root.exists():
            continue
        for skill_dir in sorted(set(_iter_dirs_with_skill_md(canonical_root))):
            skill_md = skill_dir / "SKILL.md"
            name = _parse_frontmatter_name(skill_md)
            description = _parse_frontmatter_description(skill_md)
            license_value = _parse_frontmatter_license(skill_md)
            if not _is_distributable_license(license_value):
                print(
                    f"Skipping non-distributable skill {name!r} ({license_value}) at {skill_dir}",
                    file=sys.stderr,
                )
                continue
            if not name.startswith("uv-"):
                raise SystemExit(f"Skill name must start with 'uv-': {name!r} ({skill_md})")
            slug = _skill_slug(name)
            if slug in seen_slugs:
                raise SystemExit(
                    f"slug collision: {slug!r} from {skill_dir} and {seen_slugs[slug]}"
                )
            seen_slugs[slug] = skill_dir

            dst = skills_root / slug
            _copytree(skill_dir, dst)

            imported.append(
                {
                    "name": name,
                    "slug": slug,
                    "description": description,
                    "canonical_path": str(skill_dir.relative_to(ROOT)),
                }
            )

    (skills_root / "manifest.json").write_text(
        json.dumps(sorted(imported, key=lambda x: x["slug"]), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return imported


def _first_paragraph(readme: Path) -> str:
    try:
        lines = readme.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return ""
    buf: list[str] = []
    in_code = False
    for line in lines:
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if line.startswith("#"):
            continue
        if line.strip() == "":
            if buf:
                break
            continue
        buf.append(line.strip())
    return " ".join(buf)[:220].strip()


def _count_skills_under(path: Path) -> int:
    return sum(1 for _ in path.rglob("SKILL.md"))


def _load_config() -> dict:
    if not CONFIG_PATH.is_file():
        return {}
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        raise SystemExit(f"Failed to parse config: {CONFIG_PATH} ({e})")


def _readme_table_roots(cfg: dict) -> list[str]:
    roots = cfg.get("readme_table_roots")
    if isinstance(roots, list) and all(isinstance(x, str) for x in roots):
        return roots
    return list(DEFAULT_README_TABLE_ROOTS)


def _has_skill_ancestor(dir_path: Path) -> bool:
    for candidate in [dir_path] + list(dir_path.parents):
        if candidate == ROOT.parent:
            break
        if (candidate / "SKILL.md").is_file():
            return True
        if candidate == ROOT:
            break
    return False


def _has_git_submodule_ancestor(path: Path) -> bool:
    """
    Skip README.md files inside git submodules to avoid mutating vendored content.
    A submodule typically contains a `.git` file (or directory) at its root.
    """
    for candidate in [path] + list(path.parents):
        if candidate == ROOT:
            break
        git_marker = candidate / ".git"
        if git_marker.exists():
            return True
    return False


def _is_allowed_readme(readme: Path, allowed_roots: list[str]) -> bool:
    rel = readme.relative_to(ROOT)
    for root in allowed_roots:
        root_p = Path(root)
        if root_p == Path("README.md"):
            if rel == Path("README.md"):
                return True
            continue
        if root_p == Path("."):
            return True
        # treat as directory prefix
        if rel.parts and rel.parts[0] == root_p.parts[0]:
            return True
    return False


def _remove_readme_table(readme_path: Path) -> bool:
    if not readme_path.is_file():
        return False
    original = readme_path.read_text(encoding="utf-8", errors="replace")
    lines = original.splitlines()

    drop_from: Optional[int] = None
    for i, line in enumerate(lines):
        if line.strip() == "## <TABLE>":
            drop_from = i
            break
    if drop_from is None:
        return False

    lines = lines[:drop_from]
    while lines and lines[-1].strip() == "":
        lines.pop()
    updated = "\n".join(lines + [""])
    if updated != original:
        readme_path.write_text(updated, encoding="utf-8")
        return True
    return False


def _readme_table_for_dir(dir_path: Path) -> str:
    rows: list[tuple[str, str, str]] = []

    if dir_path == ROOT:
        candidates = [
            ("common/", "dir", "Shared cross-domain skills"),
            ("knowledge/", "dir", "Domain and research skills"),
            ("productivity/", "dir", "Engineering workflow skills"),
            ("human/", "dir", "Skills for human-facing materials"),
            ("bootstrap/", "dir", "Repository maintenance scripts"),
            ("skills/", "dir", "Generated Skills-CLI mirror (do not edit)"),
            ("INSTALL.md", "file", "Installation instructions"),
            ("LICENSE", "file", "Repository license"),
            ("THIRD_PARTY_NOTICES.md", "file", "Third-party notices and licenses"),
        ]
        rows.extend(candidates)
    else:
        for child in sorted(dir_path.iterdir(), key=lambda p: p.name.lower()):
            if child.name.startswith("."):
                continue
            if child.name in {"__pycache__"}:
                continue

            rel = child.name + ("/" if child.is_dir() else "")

            if child.is_dir() and (child / "SKILL.md").is_file():
                name = _parse_frontmatter_name(child / "SKILL.md")
                desc = _parse_frontmatter_description(child / "SKILL.md")
                license_value = _parse_frontmatter_license(child / "SKILL.md")
                if not _is_distributable_license(license_value):
                    continue
                rows.append((rel, "skill", desc or name))
                continue

            if child.is_dir():
                skill_count = _count_skills_under(child)
                if skill_count:
                    desc = _first_paragraph(child / "README.md") if (child / "README.md").is_file() else ""
                    tail = f"{skill_count} skill(s)"
                    rows.append((rel, "group", f"{desc} ({tail})".strip()))
                else:
                    desc = _first_paragraph(child / "README.md") if (child / "README.md").is_file() else ""
                    rows.append((rel, "dir", desc))
                continue

            if child.is_file() and child.name in {"README.md"}:
                continue

            if child.is_file():
                if child.suffix not in {".md", ".py", ".sh", ".json"}:
                    continue
                if child.suffix == ".md":
                    desc = _first_paragraph(child)
                elif child.suffix in {".py", ".sh"}:
                    desc = "Script"
                else:
                    desc = "Data file"
                rows.append((rel, "file", desc))
                continue

    header = "| Path | Type | Description |\n| --- | --- | --- |"
    body = "\n".join(f"| `{p}` | {t} | {d} |" for p, t, d in rows if p)
    return header + ("\n" + body if body else "")


def update_readme_table(readme_path: Path) -> bool:
    if not readme_path.is_file():
        return False

    # Never touch README.md that belongs to a skill directory.
    if (readme_path.parent / "SKILL.md").is_file():
        return False

    original = readme_path.read_text(encoding="utf-8", errors="replace")
    lines = original.splitlines()

    # Drop any existing table section (we enforce it at the end).
    drop_from: Optional[int] = None
    for i, line in enumerate(lines):
        if line.strip() == "## <TABLE>":
            drop_from = i
            break
    if drop_from is not None:
        lines = lines[:drop_from]

    while lines and lines[-1].strip() == "":
        lines.pop()

    table = _readme_table_for_dir(readme_path.parent)
    new_block = [
        "## <TABLE>",
        "<!-- PKBLLM_TABLE_START -->",
        table,
        "<!-- PKBLLM_TABLE_END -->",
        "",
    ]
    updated = "\n".join(lines + [""] + new_block)
    if updated != original:
        readme_path.write_text(updated, encoding="utf-8")
        return True
    return False


def update_all_readmes(root: Path) -> int:
    cfg = _load_config()
    allowed_roots = _readme_table_roots(cfg)

    updated = 0
    for readme in sorted(root.rglob("README.md")):
        if _has_git_submodule_ancestor(readme.parent):
            continue
        # Skip reference clones.
        if ".references" in readme.parts:
            continue
        # Skip docs entirely.
        if "docs" in readme.parts:
            continue

        # Only maintain README tables in configured roots. Also never inject tables
        # into README.md files inside a skill directory subtree.
        if not _is_allowed_readme(readme, allowed_roots) or _has_skill_ancestor(readme.parent):
            if _remove_readme_table(readme):
                updated += 1
            continue

        if update_readme_table(readme):
            updated += 1
    return updated


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Update the generated `skills/` mirror and refresh README.md <TABLE> sections."
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="all",
        choices=["all", "build-mirror", "update-readmes"],
        help="What to do.",
    )
    parser.add_argument("--no-mirror", action="store_true", help="Skip regenerating `skills/`.")
    parser.add_argument("--no-readmes", action="store_true", help="Skip updating README tables.")
    args = parser.parse_args(argv)

    canonical_roots = [
        ROOT / "common",
        ROOT / "knowledge",
        ROOT / "productivity",
        ROOT / "human",
        ROOT / "bootstrap",
    ]

    if args.command in ("all", "build-mirror") and not args.no_mirror:
        build_skills_mirror(canonical_roots)

    if args.command in ("all", "update-readmes") and not args.no_readmes:
        update_all_readmes(ROOT)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
