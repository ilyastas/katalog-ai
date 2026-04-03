from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

SKIP_FILES = {"ai-catalog.json", "schema.json", "object_form.json", "core.json"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Find a company by id in root JSONL data files, refresh ver.d to today, "
            "increment ver.s, and write the file back in JSONL format."
        )
    )
    parser.add_argument("company_id", help="Company id to update")
    parser.add_argument("amount", help="Payment amount for audit/logging")
    return parser.parse_args()


def validate_amount(raw_amount: str) -> str:
    try:
        normalized = Decimal(raw_amount)
    except InvalidOperation as exc:
        raise SystemExit(f"Invalid amount: {raw_amount}") from exc

    if normalized < 0:
        raise SystemExit("Amount must be non-negative")

    return format(normalized, "f").rstrip("0").rstrip(".") or "0"


def iter_data_files(repo_root: Path):
    for path in sorted(repo_root.glob("*.json")):
        if path.name in SKIP_FILES:
            continue
        yield path


def load_records(json_path: Path) -> list[dict]:
    raw = json_path.read_text(encoding="utf-8").strip()
    if not raw:
        return []

    try:
        if raw.startswith("["):
            payload = json.loads(raw)
            if not isinstance(payload, list):
                raise ValueError("expected a JSON array")
            return [item for item in payload if isinstance(item, dict)]

        records: list[dict] = []
        for line_number, line in enumerate(raw.splitlines(), start=1):
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            if not isinstance(item, dict):
                raise ValueError(f"line {line_number} is not a JSON object")
            records.append(item)
        return records
    except (json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"{json_path.name}: {exc}") from exc


def write_records(json_path: Path, records: list[dict]) -> None:
    with json_path.open("w", encoding="utf-8", newline="") as fh:
        for index, record in enumerate(records):
            if index:
                fh.write("\n")
            fh.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")))


def update_company_record(repo_root: Path, company_id: str, amount: str) -> int:
    today = date.today().isoformat()

    for json_path in iter_data_files(repo_root):
        try:
            payload = load_records(json_path)
        except ValueError as exc:
            print(f"Skipping invalid JSON file: {exc}", file=sys.stderr)
            continue

        updated = False
        for item in payload:
            if item.get("id") != company_id:
                continue

            ver = item.get("ver")
            if not isinstance(ver, dict):
                ver = {}
                item["ver"] = ver

            current_score = ver.get("s", 0)
            try:
                current_score = int(current_score)
            except (TypeError, ValueError):
                current_score = 0

            ver["d"] = today
            ver["s"] = current_score + 1
            updated = True
            break

        if updated:
            write_records(json_path, payload)
            print(
                f"Updated {company_id} in {json_path.name}: "
                f"ver.d={today}, ver.s={ver['s']}, amount={amount}"
            )
            return 0

    print("Company not found", file=sys.stderr)
    return 1


def main() -> int:
    args = parse_args()
    amount = validate_amount(args.amount)
    repo_root = Path(__file__).resolve().parents[1]
    return update_company_record(repo_root, args.company_id, amount)


if __name__ == "__main__":
    raise SystemExit(main())
