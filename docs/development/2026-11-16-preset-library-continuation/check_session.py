#!/usr/bin/env python3
"""Read-only consistency check for this session's actual worker receipts."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    directory = Path(__file__).resolve().parent
    data = json.loads((directory / "assignments.json").read_text())
    records = data["workers"]
    errors: list[str] = []
    ids = [record["id"] for record in records]
    agents = [record["agent"] for record in records]
    if len(ids) != len(set(ids)) or len(agents) != len(set(agents)):
        errors.append("Duplicate worker or actual agent identity")
    accepted = 0
    waves: dict[int, int] = {}
    for record in records:
        number = int(record["id"][1:])
        wave = record["wave"]
        if number < 1 or number > 60 or wave != (number - 1) // 6 + 1:
            errors.append(f"Invalid wave/id: {record['id']}")
        waves[wave] = waves.get(wave, 0) + 1
        if record["status"] == "accepted":
            accepted += 1
            note = directory / "notes" / (record["id"] + ".md")
            if not note.is_file() or note.stat().st_size < 300:
                errors.append(f"Missing substantive note: {record['id']}")
            elif hashlib.sha256(note.read_bytes()).hexdigest() != record.get("note_sha256"):
                errors.append(f"Accepted note changed: {record['id']}")
            if not record.get("acceptance"):
                errors.append(f"Missing root acceptance: {record['id']}")
    if args.strict and (len(records) != 60 or accepted != 60 or
                        waves != {wave: 6 for wave in range(1, 11)}):
        errors.append("Strict closure requires 60 distinct accepted workers in ten waves of six")
    result = {"schema_version": 1, "strict": args.strict, "dispatched": len(records),
              "accepted": accepted, "waves": waves, "errors": errors,
              "scope": "Record consistency only; not dispatch, code, fidelity or publication proof."}
    print(json.dumps(result, indent=2, sort_keys=True))
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
