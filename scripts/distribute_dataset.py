"""Dataset distribution helper.

This script is CI-friendly and safe to run without credentials.
It validates files and logs which target syncs are possible.
"""

from __future__ import annotations

import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_FILES = [
    ROOT / "data" / "companies.json",
    ROOT / "data" / "categories.json",
    ROOT / "data" / "locations.json",
]


def validate_json_files() -> None:
    for file in DATA_FILES:
        if not file.exists():
            raise FileNotFoundError(f"Missing dataset file: {file}")
        with file.open("r", encoding="utf-8") as f:
            json.load(f)
    print("Dataset JSON validation: OK")


def sync_huggingface() -> None:
    token = os.getenv("HF_TOKEN")
    if not token:
        print("HuggingFace sync skipped: HF_TOKEN is not set")
        return
    print("HuggingFace sync ready (implement upload API call when repo/dataset id is finalized)")


def sync_kaggle() -> None:
    username = os.getenv("KAGGLE_USERNAME")
    key = os.getenv("KAGGLE_KEY")
    if not username or not key:
        print("Kaggle sync skipped: KAGGLE_USERNAME/KAGGLE_KEY missing")
        return
    print("Kaggle sync ready (implement kaggle datasets version command when dataset slug is finalized)")


def sync_zenodo() -> None:
    token = os.getenv("ZENODO_TOKEN")
    if not token:
        print("Zenodo sync skipped: ZENODO_TOKEN is not set")
        return
    print("Zenodo sync ready (implement deposition upload when concept DOI is available)")


def main() -> None:
    validate_json_files()
    sync_huggingface()
    sync_kaggle()
    sync_zenodo()


if __name__ == "__main__":
    main()
