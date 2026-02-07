#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional

from pkbllm_config import find_repo_root, load_config, resolve_config_path, resolve_human_material_root


_NEW_ID_RE = re.compile(r"(?P<id>\d{4}\.\d{4,5})(?P<v>v\d+)?$")


def _normalize_arxiv_id(value: str) -> str:
    v = value.strip()
    if not v:
        raise ValueError("empty arXiv id/url")

    if "arxiv.org" in v and (v.startswith("http://") or v.startswith("https://")):
        u = urllib.parse.urlparse(v)
        path = u.path.strip("/")
        # /abs/<id>, /pdf/<id>.pdf, /src/<id>, /e-print/<id>
        parts = path.split("/")
        if len(parts) >= 2 and parts[0] in {"abs", "pdf", "src", "e-print"}:
            tail = parts[1]
        else:
            tail = parts[-1]
        tail = tail.removesuffix(".pdf")
        v = tail

    # Keep version suffix if present
    m = _NEW_ID_RE.search(v)
    if m:
        return m.group("id") + (m.group("v") or "")

    # Fall back: allow legacy ids like cs/9901001
    if "/" in v and not v.startswith("/"):
        return v

    raise ValueError(f"unrecognized arXiv id: {value!r}")


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "pkbllm/uv-read-arxiv-paper"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        dest.write_bytes(resp.read())


def _download_src(arxiv_id: str, dest: Path) -> None:
    # arXiv serves source through multiple endpoints; try /src then /e-print.
    tried: list[str] = []
    for endpoint in ["src", "e-print"]:
        url = f"https://arxiv.org/{endpoint}/{arxiv_id}"
        tried.append(url)
        try:
            _download(url, dest)
            return
        except Exception:
            continue
    raise RuntimeError(f"Failed to download source. Tried: {tried}")


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Download arXiv PDF and source into $HUMAN_MATERIAL_PATH/.references/")
    p.add_argument("arxiv", help="arXiv URL or id (e.g. https://arxiv.org/abs/2601.07372)")
    p.add_argument("--pdf-only", action="store_true", help="Download only the PDF")
    p.add_argument("--src-only", action="store_true", help="Download only the source tarball")
    p.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    args = p.parse_args(argv)

    human_root = resolve_human_material_root()
    if not human_root:
        print("HUMAN_MATERIAL_PATH is not set or does not exist.", file=sys.stderr)
        return 2

    repo_root = human_root if (human_root / ".git").exists() else find_repo_root(human_root)
    cfg = load_config(repo_root)

    pdfs_dir = resolve_config_path(repo_root, cfg, key="pdfs_dir", default_rel=".references/pdfs")
    arxiv_dir = resolve_config_path(repo_root, cfg, key="arxiv_dir", default_rel=".references/arxiv")

    arxiv_id = _normalize_arxiv_id(args.arxiv)
    pdf_path = pdfs_dir / f"{arxiv_id}.pdf"
    src_path = arxiv_dir / f"{arxiv_id}.tar.gz"

    want_pdf = not args.src_only
    want_src = not args.pdf_only

    if want_pdf:
        if pdf_path.exists() and not args.overwrite:
            print(str(pdf_path))
        else:
            _download(f"https://arxiv.org/pdf/{arxiv_id}.pdf", pdf_path)
            print(str(pdf_path))

    if want_src:
        if src_path.exists() and not args.overwrite:
            print(str(src_path))
        else:
            _download_src(arxiv_id, src_path)
            print(str(src_path))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

