#!/usr/bin/env python3
from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import math
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Optional


REPO_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_ROOTS = [
    REPO_ROOT / "bootstrap",
    REPO_ROOT / "common",
    REPO_ROOT / "human",
    REPO_ROOT / "knowledge",
    REPO_ROOT / "productivity",
]

START_MARKER = "<!-- PKBLLM-AGENTS-NOTE-START -->"
END_MARKER = "<!-- PKBLLM-AGENTS-NOTE-END -->"


@dataclasses.dataclass(frozen=True)
class SkillDoc:
    name: str
    description: str
    skill_md: Path
    body: str
    tokens: tuple[str, ...]
    outbound_refs: tuple[str, ...]


_NON_WORD = re.compile(r"[^a-z0-9]+")
_SKILL_REF = re.compile(r"\buv-[a-z0-9][a-z0-9-]*\b", flags=re.IGNORECASE)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _tokenize(text: str) -> list[str]:
    text = text.lower()
    text = _NON_WORD.sub(" ", text)
    parts = [p for p in text.split() if p]
    # very small stoplist, keep conservative (we want recall > precision)
    stop = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "to",
        "of",
        "in",
        "on",
        "for",
        "with",
        "is",
        "are",
        "be",
        "this",
        "that",
    }
    return [p for p in parts if p not in stop and len(p) > 1]


def _read_frontmatter(skill_md: Path) -> dict[str, str]:
    lines = _read_text(skill_md).splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    out: dict[str, str] = {}
    for line in lines[1:250]:
        if line.strip() == "---":
            break
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        key = k.strip()
        val = v.strip().strip("'\"")
        if key and key not in out:
            out[key] = val
    return out


def iter_canonical_skills(repo_root: Path) -> Iterable[SkillDoc]:
    for root in CANONICAL_ROOTS:
        if not root.is_dir():
            continue
        for skill_md in root.rglob("SKILL.md"):
            if skill_md.name != "SKILL.md":
                continue
            fm = _read_frontmatter(skill_md)
            name = (fm.get("name") or "").strip()
            if not name.startswith("uv-"):
                continue
            description = (fm.get("description") or "").strip()
            body = _read_text(skill_md)
            tokens = tuple(_tokenize(f"{name}\n{description}\n{body}"))
            refs = tuple(sorted({m.lower() for m in _SKILL_REF.findall(body) if m.lower() != name.lower()}))
            yield SkillDoc(
                name=name,
                description=description,
                skill_md=skill_md,
                body=body,
                tokens=tokens,
                outbound_refs=refs,
            )


def _git_rev(repo_root: Path) -> str:
    try:
        out = subprocess.check_output(["git", "-C", str(repo_root), "rev-parse", "HEAD"], text=True).strip()
        return out[:12]
    except Exception:
        return "unknown"


def _build_idf(docs: list[SkillDoc]) -> dict[str, float]:
    df: dict[str, int] = {}
    for d in docs:
        seen = set(d.tokens)
        for t in seen:
            df[t] = df.get(t, 0) + 1
    n = max(1, len(docs))
    # BM25-ish idf
    return {t: math.log((n - c + 0.5) / (c + 0.5) + 1.0) for t, c in df.items()}


def _score_query(query: str, docs: list[SkillDoc], *, top_k: int = 12) -> list[tuple[SkillDoc, float, dict[str, float]]]:
    q_tokens = _tokenize(query)
    if not q_tokens:
        return []
    idf = _build_idf(docs)
    q_set = set(q_tokens)

    # Precompute graph (outbound references)
    by_name = {d.name.lower(): d for d in docs}
    inbound: dict[str, set[str]] = {}
    for d in docs:
        for ref in d.outbound_refs:
            inbound.setdefault(ref, set()).add(d.name.lower())

    # Query intent priors by directory family.
    qtok = set(q_tokens)
    workflow = {
        "refactor",
        "bug",
        "fix",
        "tests",
        "test",
        "pytest",
        "ci",
        "lint",
        "review",
        "pr",
        "merge",
        "branch",
        "commit",
        "repo",
        "worktree",
    }
    content = {"slides", "pptx", "pdf", "paper", "manuscript", "exercise", "tutorial"}
    ml = {
        "train",
        "training",
        "gpu",
        "cuda",
        "pytorch",
        "model",
        "llm",
        "rl",
        "tune",
        "finetune",
        "quantization",
        "serving",
        "inference",
        "distributed",
    }

    def prior_for(path: Path) -> float:
        p = str(path).replace("\\", "/")
        if "/productivity/" in p or p.endswith("/productivity"):
            family = "productivity"
        elif "/knowledge/" in p or p.endswith("/knowledge"):
            family = "knowledge"
        elif "/human/" in p or p.endswith("/human"):
            family = "human"
        elif "/bootstrap/" in p or p.endswith("/bootstrap"):
            family = "bootstrap"
        else:
            family = "common"

        if qtok & workflow:
            if family in {"productivity", "common", "bootstrap"}:
                return 1.12
            return 0.92
        if qtok & content:
            if family == "human":
                return 1.18
            return 0.95
        if qtok & ml:
            if family == "knowledge":
                return 1.15
            return 0.97
        return 1.0

    # BM25 length normalization to avoid very long SKILL.md dominating.
    avgdl = sum(len(d.tokens) for d in docs) / max(1, len(docs))
    k1 = 1.2
    b = 0.75

    scored: list[tuple[SkillDoc, float, dict[str, float]]] = []
    for d in docs:
        tf: dict[str, int] = {}
        for t in d.tokens:
            if t in q_set:
                tf[t] = tf.get(t, 0) + 1

        dl = max(1, len(d.tokens))
        denom_norm = k1 * (1.0 - b + b * (dl / max(1.0, avgdl)))
        base = 0.0
        for t, tfv in tf.items():
            itf = (tfv * (k1 + 1.0)) / (tfv + denom_norm)
            base += idf.get(t, 0.0) * itf

        # Small boosts:
        # - name substring match
        q_l = query.lower().strip()
        if q_l and q_l.replace(" ", "-") in d.name.lower():
            base *= 1.25

        # - relational boost: if linked to high-base skills, pull it up a bit
        # We only apply after we have a rough set; do a cheap one-hop heuristic:
        rel = 0.0
        for ref in d.outbound_refs:
            if ref in by_name and any(tok in ref for tok in q_set):
                rel += 0.15
        for src in inbound.get(d.name.lower(), set()):
            if any(tok in src for tok in q_set):
                rel += 0.08

        prior = prior_for(d.skill_md)
        score = (base + rel) * prior
        explain = {"base": base, "rel": rel, "prior": prior}
        if score > 0:
            scored.append((d, score, explain))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[: max(1, int(top_k))]


def _print_recommendations(rows: list[tuple[SkillDoc, float, dict[str, float]]], *, repo_root: Path) -> None:
    if not rows:
        print("No matches.")
        return
    for i, (d, s, explain) in enumerate(rows, start=1):
        relpath = d.skill_md.relative_to(repo_root)
        prior = explain.get("prior", 1.0)
        print(
            f"{i:>2}. {d.name}  (score={s:.3f}, base={explain['base']:.3f}, rel={explain['rel']:.3f}, prior={prior:.2f})"
        )
        if d.description:
            print(f"    {d.description}")
        print(f"    {relpath}")


def _read_agents_md(path: Path) -> str:
    if not path.exists():
        return ""
    return _read_text(path)


def _inject_marked_block(existing: str, block: str) -> str:
    wrapped = f"{START_MARKER}\n{block.rstrip()}\n{END_MARKER}\n"
    if START_MARKER in existing and END_MARKER in existing:
        start = existing.index(START_MARKER)
        end = existing.index(END_MARKER) + len(END_MARKER)
        # preserve surrounding content
        before = existing[:start].rstrip() + "\n"
        after = existing[end:].lstrip()
        return before + wrapped + after
    if existing.strip():
        sep = "\n" if existing.endswith("\n") else "\n\n"
        return existing + sep + wrapped
    return wrapped


def _render_full_embed(*, query: str, selected: list[SkillDoc], repo_root: Path) -> str:
    ts = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    rev = _git_rev(repo_root)
    header = [
        "# pkbllm assembled task notes",
        "",
        f"- query: {query.strip()}",
        f"- generated_at_utc: {ts}",
        f"- pkbllm_rev: {rev}",
        "- skills:",
        *[f"  - {s.name} ({s.skill_md.relative_to(repo_root)})" for s in selected],
        "",
        "---",
        "",
        "## Embedded skills",
        "",
        "These are verbatim `SKILL.md` bodies embedded for passive in-band context.",
        "",
    ]
    parts = ["\n".join(header)]
    for s in selected:
        rel = s.skill_md.relative_to(repo_root)
        parts.append(f"### {s.name}\n\n(Source: `{rel}`)\n\n{s.body.rstrip()}\n")
    return "\n".join(parts).rstrip() + "\n"


def _pick_interactive(rows: list[tuple[SkillDoc, float, dict[str, float]]]) -> list[SkillDoc]:
    if not rows:
        return []
    while True:
        raw = input("Pick skills by number (e.g. '1 2 5'), or 'a' for all shown, or 'q' to quit: ").strip()
        if raw.lower() == "q":
            return []
        if raw.lower() == "a":
            return [d for (d, _, _) in rows]
        nums: list[int] = []
        ok = True
        for part in raw.split():
            if not part.isdigit():
                ok = False
                break
            nums.append(int(part))
        if not ok or not nums:
            print("Invalid selection.")
            continue
        selected: list[SkillDoc] = []
        for n in nums:
            if 1 <= n <= len(rows):
                selected.append(rows[n - 1][0])
        if selected:
            return selected
        print("No valid indices selected.")


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="Assemble pkbllm skills into a project AGENTS.md block (passive in-band context)."
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="List available canonical pkbllm skills.")

    p_show = sub.add_parser("show", help="Print a skill's SKILL.md to stdout.")
    p_show.add_argument("skill", help="Exact skill name (e.g. uv-writing-plans).")

    p_rec = sub.add_parser("recommend", help="Recommend skills for a task query.")
    p_rec.add_argument("--query", required=True, help="Task query (free-form).")
    p_rec.add_argument("--top", type=int, default=12, help="Number of results to show.")

    p_asm = sub.add_parser("assemble", help="Write an embedded-skills block into AGENTS.md.")
    p_asm.add_argument("--query", required=True, help="Task query (used in header + recommendations).")
    p_asm.add_argument("--agents-md", default="AGENTS.md", help="Target AGENTS.md path (default: ./AGENTS.md).")
    p_asm.add_argument("--top", type=int, default=12, help="Number of recommended skills to consider.")
    p_asm.add_argument("--pick", action="store_true", help="Interactively pick skills from recommendations.")
    p_asm.add_argument("--skill", action="append", default=[], help="Select skill by exact name (repeatable).")
    p_asm.add_argument(
        "--init",
        action="store_true",
        help="If AGENTS.md does not exist, initialize it with a short header before injecting the block.",
    )
    p_asm.add_argument("--dry-run", action="store_true", help="Print the block that would be injected; do not write.")

    args = ap.parse_args(argv)
    repo_root = REPO_ROOT
    docs = list(iter_canonical_skills(repo_root))

    if args.cmd == "list":
        for d in sorted(docs, key=lambda x: x.name):
            rel = d.skill_md.relative_to(repo_root)
            line = f"{d.name}  ({rel})"
            if d.description:
                line += f" — {d.description}"
            print(line)
        return 0

    if args.cmd == "show":
        by_name = {d.name: d for d in docs}
        if args.skill not in by_name:
            print(f"ERROR: unknown skill: {args.skill!r}", file=sys.stderr)
            return 2
        sys.stdout.write(by_name[args.skill].body)
        return 0

    if args.cmd == "recommend":
        rows = _score_query(args.query, docs, top_k=args.top)
        _print_recommendations(rows, repo_root=repo_root)
        return 0

    if args.cmd == "assemble":
        rows = _score_query(args.query, docs, top_k=args.top)
        selected: list[SkillDoc] = []

        by_name = {d.name: d for d in docs}
        for name in args.skill:
            if name not in by_name:
                print(f"ERROR: unknown skill: {name!r}", file=sys.stderr)
                return 2
            selected.append(by_name[name])

        if args.pick:
            print("Recommendations:")
            _print_recommendations(rows, repo_root=repo_root)
            picked = _pick_interactive(rows)
            selected.extend(picked)

        if not selected:
            # Default behavior: take the top 3 recommendations.
            selected = [d for (d, _, _) in rows[:3]]

        # De-dup preserve order
        seen: set[str] = set()
        uniq: list[SkillDoc] = []
        for d in selected:
            if d.name in seen:
                continue
            seen.add(d.name)
            uniq.append(d)
        selected = uniq

        block = _render_full_embed(query=args.query, selected=selected, repo_root=repo_root)

        if args.dry_run:
            sys.stdout.write(f"{START_MARKER}\n{block}{END_MARKER}\n")
            return 0

        target = Path(args.agents_md).expanduser().resolve()
        existing = _read_agents_md(target)
        if args.init and not target.exists():
            existing = "# AGENTS.md\n\nThis file provides persistent context to coding agents.\n\n"
        updated = _inject_marked_block(existing, block)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(updated, encoding="utf-8")
        print(f"Updated {target} ({len(selected)} skills).")
        return 0

    return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        # Allow piping to `head`/`rg` without stack traces.
        try:
            sys.stdout.close()
        except Exception:
            pass
        raise SystemExit(0)
