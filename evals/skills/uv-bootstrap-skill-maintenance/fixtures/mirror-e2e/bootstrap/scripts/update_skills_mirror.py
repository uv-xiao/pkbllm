#!/usr/bin/env python3

# Copied from pkbllm/bootstrap/scripts/update_skills_mirror.py for eval fixture usage.

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


def _count_skills_under(root: Path) -> int:
    count = 0
    for p in root.rglob("SKILL.md"):
        if p.name == "SKILL.md":
            count += 1
    return count


def _load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _readme_table_roots(cfg: dict) -> list[str]:
    value = cfg.get("readme_table_roots")
    if isinstance(value, list) and all(isinstance(x, str) for x in value):
        return list(value)
    return list(DEFAULT_README_TABLE_ROOTS)


def _is_allowed_readme(readme: Path, allowed_roots: list[str]) -> bool:
    try:
        rel = readme.relative_to(ROOT)
    except Exception:
        return False
    if str(rel) == "README.md" and "README.md" in allowed_roots:
        return True
    if len(rel.parts) >= 2 and rel.parts[0] in allowed_roots and rel.parts[1] == "README.md":
        return True
    return False


def _has_skill_ancestor(dir_path: Path) -> bool:
    for p in [dir_path, *dir_path.parents]:
        if p == ROOT:
            break
        if (p / "SKILL.md").is_file():
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
    updated = "\n".join(lines) + "\n"
    if updated != original:
        readme_path.write_text(updated, encoding="utf-8")
        return True
    return False


def _readme_table_for_dir(dir_path: Path) -> str:
    rows: list[tuple[str, str, str]] = []
    for child in sorted(dir_path.iterdir()):
        if child.name.startswith("."):
            continue
        if child.is_dir():
            skill_count = _count_skills_under(child)
            desc = _first_paragraph(child / "README.md") if (child / "README.md").is_file() else ""
            if skill_count:
                rows.append((str(child.relative_to(dir_path)), "group", f"{desc} ({skill_count} skill(s))".strip()))
            else:
                rows.append((str(child.relative_to(dir_path)), "dir", desc))
            continue
        if child.is_file() and child.name == "README.md":
            continue
        if child.is_file() and child.suffix in {".md", ".py", ".sh", ".json"}:
            rows.append((str(child.relative_to(dir_path)), "file", _first_paragraph(child) if child.suffix == ".md" else "Data file"))

    header = "| Path | Type | Description |\n| --- | --- | --- |"
    body = "\n".join(f"| `{p}` | {t} | {d} |" for p, t, d in rows if p)
    return header + ("\n" + body if body else "")


def update_readme_table(readme_path: Path) -> bool:
    if not readme_path.is_file():
        return False
    if (readme_path.parent / "SKILL.md").is_file():
        return False
    original = readme_path.read_text(encoding="utf-8", errors="replace")
    lines = original.splitlines()
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
        if ".references" in readme.parts:
            continue
        if "docs" in readme.parts:
            continue
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

