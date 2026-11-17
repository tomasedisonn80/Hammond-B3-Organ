#!/usr/bin/env python3
"""Read-only record checks for the 2026-11-16 UI delivery continuation.

Default mode accepts incomplete, internally consistent progress. --strict
requires all sixty accepted records in ten complete waves. Neither mode proves
external dispatch, actual concurrency, substantive review, product quality or
publication. It reads only this session's ledger and accepted note files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import stat
import sys


METADATA = {
    "schema_version": 1,
    "session": "2026-11-16-ui-delivery",
    "base_commit": "6047723b595259de355c74342e48a8ae2ee1e228",
    "requested_workers": 60,
    "requested_waves": 10,
    "max_concurrent_workers": 3,
}
REQUIRED_FIELDS = {"id", "wave", "agent", "task", "state", "note"}
ID = re.compile(r"A[0-9]{2}\Z")
AGENT = re.compile(r"/root(?:/[a-z][a-z0-9_]*)+\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
MAX_LEDGER_BYTES = 256 * 1024
MAX_NOTE_BYTES = 64 * 1024
MIN_NOTE_CHARACTERS = 200
MIN_NOTE_WORDS = 40
LIMITATION = (
    "Checks record and note-byte consistency only; does not establish external "
    "dispatch, actual concurrency, substantive review, product quality or publication."
)


class RecordError(ValueError):
    """The supplied session records do not satisfy this versioned schema."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RecordError(message)


def read_regular(path: Path, limit: int) -> bytes:
    # lstat rejects symlinks, directories and nonregular inputs before opening.
    require(stat.S_ISREG(path.lstat().st_mode), f"not a regular file: {path.name}")
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    require(len(raw) <= limit, f"file exceeds {limit}-byte limit: {path.name}")
    return raw


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise RecordError(f"non-JSON numeric constant: {value}")


def validate(session_dir: Path, *, strict: bool = False) -> dict:
    """Validate one snapshot; never creates, edits or accepts a worker record."""
    session_dir = session_dir.resolve(strict=True)
    raw = read_regular(session_dir / "assignments.json", MAX_LEDGER_BYTES)
    data = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object,
                      parse_constant=reject_constant)
    require(type(data) is dict, "ledger must be a JSON object")
    require(set(data) == set(METADATA) | {"assignments"}, "unknown or missing ledger fields")
    for key, expected in METADATA.items():
        require(type(data[key]) is type(expected) and data[key] == expected,
                f"unsupported {key}: expected {expected!r}")
    rows = data["assignments"]
    require(type(rows) is list and len(rows) <= 60, "assignments must contain at most 60 records")
    notes_dir = session_dir / "notes"
    require(not notes_dir.is_symlink(), "notes directory must not be a symlink")
    if notes_dir.exists():
        require(notes_dir.is_dir(), "notes must be a directory")
    identifiers, agents = set(), set()
    waves = [{"wave": wave, "recorded": 0, "accepted": 0, "running": 0}
             for wave in range(1, 11)]
    for index, row in enumerate(rows):
        where = f"assignment {index + 1}"
        require(type(row) is dict, f"{where}: expected an object")
        require(REQUIRED_FIELDS <= set(row) <= REQUIRED_FIELDS | {"note_sha256"},
                f"{where}: unknown or missing record fields")
        identifier = row["id"]
        require(type(identifier) is str and ID.fullmatch(identifier) is not None,
                f"{where}: invalid ID")
        number = int(identifier[1:])
        require(1 <= number <= 60, f"{identifier}: ID outside A01–A60")
        require(identifier not in identifiers, f"duplicate ID: {identifier}")
        identifiers.add(identifier)
        wave = (number - 1) // 6 + 1
        require(type(row["wave"]) is int and row["wave"] == wave,
                f"{identifier}: expected wave {wave}")
        agent = row["agent"]
        require(type(agent) is str and len(agent) <= 256 and AGENT.fullmatch(agent) is not None,
                f"{identifier}: invalid canonical agent name")
        require(agent not in agents, f"duplicate agent: {agent}")
        agents.add(agent)
        require(type(row["task"]) is str and 0 < len(row["task"].strip()) <= 2000,
                f"{identifier}: task must be nonempty text of at most 2000 characters")
        state = row["state"]
        require(type(state) is str and state in {"running", "accepted"},
                f"{identifier}: state must be running or accepted")
        # Exact relative paths also prevent traversal, absolute paths and note reuse.
        require(row["note"] == f"notes/{identifier}.md",
                f"{identifier}: note must be notes/{identifier}.md within this session")
        note = notes_dir / f"{identifier}.md"
        require(not note.is_symlink(), f"{identifier}: note must not be a symlink")
        if state == "accepted":
            digest = row.get("note_sha256")
            require(type(digest) is str and SHA256.fullmatch(digest) is not None,
                    f"{identifier}: accepted record needs a lowercase SHA-256")
            note_raw = read_regular(note, MAX_NOTE_BYTES)
            text = note_raw.decode("utf-8")
            require(len(text.strip()) >= MIN_NOTE_CHARACTERS and
                    len(text.split()) >= MIN_NOTE_WORDS,
                    f"{identifier}: note needs at least {MIN_NOTE_CHARACTERS} characters "
                    f"and {MIN_NOTE_WORDS} words; content still needs human review")
            require(hashlib.sha256(note_raw).hexdigest() == digest,
                    f"{identifier}: accepted note SHA-256 mismatch")
        else:
            require("note_sha256" not in row,
                    f"{identifier}: running record cannot carry an accepted-note hash")
        waves[wave - 1]["recorded"] += 1
        waves[wave - 1][state] += 1
    accepted = sum(wave["accepted"] for wave in waves)
    running = sum(wave["running"] for wave in waves)
    complete = [wave["wave"] for wave in waves if wave["accepted"] == 6]
    if strict:
        require(identifiers == {f"A{i:02d}" for i in range(1, 61)} and
                accepted == 60 and len(complete) == 10,
                f"strict closure needs 60 accepted records and 10 complete waves; "
                f"found {len(rows)} records, {accepted} accepted and {len(complete)} complete waves")
    return {
        "status": "passed", "mode": "strict" if strict else "progress",
        "session": METADATA["session"], "ledger_sha256": hashlib.sha256(raw).hexdigest(),
        "recorded": len(rows), "accepted": accepted, "running": running,
        "unrecorded": 60 - len(rows), "complete_waves": complete, "waves": waves,
        "error_count": 0, "errors": [], "scope": LIMITATION,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="require all sixty accepted records")
    args = parser.parse_args(argv)
    try:
        result = validate(Path(__file__).resolve().parent, strict=args.strict)
    except (OSError, ValueError, RecursionError) as error:
        result = {"status": "failed", "mode": "strict" if args.strict else "progress",
                  "session": METADATA["session"], "error_count": 1,
                  "errors": [str(error)], "scope": LIMITATION}
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
