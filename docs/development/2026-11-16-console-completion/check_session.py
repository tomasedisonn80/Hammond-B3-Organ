#!/usr/bin/env python3
"""Read-only consistency check of this console session's actual assignments.

From any working directory, run this file with Python 3 and optionally --strict.
There is no --repo option. Progress permits incomplete dispatch and unpinned
running notes. Strict requires all A01..A60 accepted in ten waves of six.

Only assignments are counted; plans, history, followups and owned_paths confer
no worker credit. The only known states are running and accepted. An accepted
record requires a nonblank root_review and a matching SHA-256 of its UTF-8 note.
The mechanical note floor is 300 bytes, 200 non-whitespace characters and 30
whitespace-separated tokens; root still judges the substance independently.
Notes must be ordinary files at notes/Axx.md, without symlink components.
An optional hash on a running record is also checked but never accepts it.
Optional owned_paths are checked for relative path syntax only, not ownership.

This checks a local snapshot, not external dispatch, historical concurrency,
independent review quality, product quality, fidelity or publication. It never
creates notes, rewrites or sorts the ledger, or accepts a worker automatically.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re


SESSION = "2026-11-16-console-completion"
BASE_COMMIT = "9d60dbf462a90fe422fd4e69757fe202264acb7c"
EXPECTED_IDS = tuple(f"A{number:02d}" for number in range(1, 61))
STATES = ("running", "accepted")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
SCOPE = (
    "Local record and note-byte consistency only; no proof of external dispatch, "
    "historical concurrency, review quality, product quality, fidelity or publication."
)


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant: {value}")


def _finite_float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"non-finite JSON number: {value}")
    return number


def _nonblank(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _relative_path(value: object) -> bool:
    return (
        isinstance(value, str)
        and bool(value)
        and value == value.strip()
        and "\\" not in value
        and ":" not in value
        and all(ord(char) >= 32 and ord(char) != 127 for char in value)
        and all(part not in ("", ".", "..") for part in value.split("/"))
    )


def _check_note(directory: Path, record: dict, label: str, errors: list[str]) -> bool:
    """Check safe paths even for unpinned work; final bytes only when required."""
    expected = f"notes/{record['id']}.md"
    if not _relative_path(record.get("note")) or record.get("note") != expected:
        errors.append(f"{label}: note must be exactly {expected!r}")
        return False
    note = directory / expected
    pinned = record.get("state") == "accepted" or "note_sha256" in record
    try:
        # Reject internal aliases as well as escaping symlinks. A note is evidence
        # for this exact worker path, not another file reached through an alias.
        if note.parent.is_symlink() or note.is_symlink() or note.resolve() != note:
            errors.append(f"{label}: note path has a symlink or escapes its location")
            return False
        if not note.exists() and not pinned:
            return False  # An unfinished running note need not exist yet.
        if not note.is_file():
            errors.append(f"{label}: note is missing or is not an ordinary file")
            return False
        if not pinned:
            return False  # Unfinished bytes are not final evidence.
        raw = note.read_bytes()
        content = raw.decode("utf-8")
    except (OSError, RuntimeError, UnicodeError, ValueError) as exc:
        errors.append(f"{label}: cannot read a safe UTF-8 note: {exc}")
        return False
    valid = True
    if len(raw) < 300 or len("".join(content.split())) < 200 or len(content.split()) < 30:
        errors.append(f"{label}: note does not meet the documented substantive-text floor")
        valid = False
    digest = record.get("note_sha256")
    if not isinstance(digest, str) or SHA256.fullmatch(digest) is None:
        errors.append(f"{label}: note_sha256 must be 64 lowercase hexadecimal characters")
        valid = False
    elif hashlib.sha256(raw).hexdigest() != digest:
        errors.append(f"{label}: accepted/pinned note bytes changed (SHA-256 mismatch)")
        valid = False
    return valid


def check_session(directory: Path, strict: bool = False) -> dict:
    """Validate one ledger snapshot without changing its files or record order."""
    directory = directory.resolve()
    ledger = directory / "assignments.json"
    errors: list[str] = []
    result = {
        "schema_version": 1,
        "session": SESSION,
        "strict": strict,
        "ledger": str(ledger),
        "ledger_sha256": None,
        "dispatched": 0,
        "accepted": 0,
        "running": 0,
        "accepted_notes_verified": 0,
        "waves": {},
        "record_order": [],
        "complete": False,
        "errors": errors,
        "scope": SCOPE,
    }
    try:
        if ledger.is_symlink():
            raise ValueError("assignments.json must not be a symlink")
        if not ledger.is_file():
            raise ValueError("assignments.json is missing or is not an ordinary file")
        raw = ledger.read_bytes()
        result["ledger_sha256"] = hashlib.sha256(raw).hexdigest()
        data = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object,
                          parse_constant=_reject_constant, parse_float=_finite_float)
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        errors.append(f"Cannot read unambiguous JSON ledger: {exc}")
        return result
    if not isinstance(data, dict):
        errors.append("Ledger root must be an object")
        return result
    for field, expected in (("schema_version", 1), ("requested_workers", 60),
                            ("requested_waves", 10), ("max_concurrent_workers", 3)):
        if type(data.get(field)) is not int or data[field] != expected:
            errors.append(f"{field} must be the integer {expected}")
    for field, expected in (("session", SESSION), ("base_commit", BASE_COMMIT)):
        if data.get(field) != expected:
            errors.append(f"{field} must identify this session: {expected}")
    records = data.get("assignments")
    if not isinstance(records, list):
        errors.append("assignments must be an array of actual worker records")
        return result
    result["dispatched"] = len(records)
    if len(records) > 60:
        errors.append("More than 60 actual assignment records")
    ids: set[str] = set()
    agents: set[str] = set()
    for index, record in enumerate(records):
        label = f"assignments[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{label}: record must be an object")
            continue
        worker = record.get("id")
        result["record_order"].append(worker)
        valid_id = isinstance(worker, str) and worker in EXPECTED_IDS
        if not valid_id:
            errors.append(f"{label}: id must be exactly A01 through A60")
        else:
            label += f" ({worker})"
            if worker in ids:
                errors.append(f"{label}: duplicate worker id")
            ids.add(worker)
        wave = record.get("wave")
        if type(wave) is not int or not 1 <= wave <= 10:
            errors.append(f"{label}: wave must be an integer from 1 through 10")
        else:
            result["waves"][wave] = result["waves"].get(wave, 0) + 1
            if valid_id and wave != (int(worker[1:]) - 1) // 6 + 1:
                errors.append(f"{label}: wave does not match worker id")
        agent = record.get("agent")
        if not isinstance(agent, str):
            errors.append(f"{label}: agent must be a canonical /root/wXX_aYY string")
        else:
            if agent in agents:
                errors.append(f"{label}: duplicate actual agent identity")
            agents.add(agent)
            if valid_id:
                number = int(worker[1:])
                expected = f"/root/w{(number - 1) // 6 + 1:02d}_a{number:02d}"
                if agent != expected:
                    errors.append(f"{label}: agent must be {expected}")
        if not _nonblank(record.get("task")):
            errors.append(f"{label}: task must be a nonblank string")
        state = record.get("state")
        if state not in STATES:
            errors.append(f"{label}: unknown state; only running and accepted are defined")
        else:
            result[state] += 1
        if state == "accepted" or "root_review" in record:
            if not _nonblank(record.get("root_review")):
                errors.append(f"{label}: root_review must be a nonblank string")
        if "owned_paths" in record:
            paths = record["owned_paths"]
            if not isinstance(paths, list) or any(not _relative_path(path) for path in paths):
                errors.append(f"{label}: owned_paths must contain canonical relative paths")
        if valid_id and _check_note(directory, record, label, errors) and state == "accepted":
            result["accepted_notes_verified"] += 1
    if result["running"] > 3:
        errors.append("More than three records are currently running; historical concurrency is unverified")
    closed = (len(records) == 60 and ids == set(EXPECTED_IDS)
              and result["accepted"] == 60 and result["accepted_notes_verified"] == 60
              and result["waves"] == {wave: 6 for wave in range(1, 11)})
    if strict and not closed:
        errors.append("Strict closure requires A01..A60 accepted, with verified notes, in exactly ten waves of six")
    result["complete"] = closed and not errors
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true",
                        help="require all 60 actual records accepted with verified notes")
    args = parser.parse_args()
    directory = Path(__file__).resolve().parent
    result = check_session(directory, strict=args.strict)
    result["repository"] = str(directory.parents[2])
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return int(bool(result["errors"]))


if __name__ == "__main__":
    raise SystemExit(main())
