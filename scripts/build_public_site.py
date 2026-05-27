#!/usr/bin/env python3
from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "public-site"

ROOT_FILES = [
    "index.html",
    "catalog.json",
    "tag_index.json",
    "llms.txt",
    "sitemap.xml",
    "robots.txt",
    "README.md",
    "MASTER_KZ.md",
    "MASTER_RU.md",
    "AI_METHOD.md",
    "AI_SCHEMA.md",
    "AI_FAQ.md",
    ".nojekyll",
    "BingSiteAuth.xml",
    "7f559c9f7d60484fa802ab03c9328995.txt",
    "9a1f3247e0e9496aa35d6b290e5862bb.txt",
]

DIRS_TO_COPY = ["company", ".well-known", "docs"]


def copy_file(rel_path: str) -> None:
    src = ROOT / rel_path
    if not src.exists():
        raise FileNotFoundError(f"Missing required public file: {rel_path}")
    dst = OUT_DIR / rel_path
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def copy_dir(rel_path: str) -> None:
    src = ROOT / rel_path
    if not src.exists() or not src.is_dir():
        raise FileNotFoundError(f"Missing required public directory: {rel_path}")
    dst = OUT_DIR / rel_path
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def main() -> int:
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True, exist_ok=True)


    for rel_file in ROOT_FILES:
        if rel_file == "README.md":
            src = ROOT / rel_file
            dst = OUT_DIR / rel_file
            content = src.read_text(encoding="utf-8")
            dst.write_text(content, encoding="utf-8-sig", newline="\n")
        else:
            copy_file(rel_file)

    for rel_dir in DIRS_TO_COPY:
        copy_dir(rel_dir)

    # --- Cloudflare Pages _headers for charset enforcement ---
    headers_content = (
        "/*.md\n"
        "  Content-Type: text/markdown; charset=utf-8\n"
        "\n"
        "/*.txt\n"
        "  Content-Type: text/plain; charset=utf-8\n"
        "\n"
        "/llms.txt\n"
        "  Content-Type: text/plain; charset=utf-8\n"
    )
    (OUT_DIR / "_headers").write_text(headers_content, encoding="utf-8", newline="\n")

    print(f"[OK] Built publish bundle: {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
