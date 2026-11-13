#!/usr/bin/env python3
"""Check retained records for this continuation, not external agent execution."""

import argparse
import json
import os
from pathlib import Path
import re
import stat
import sys


SESSION = "2026-11-13-continuation"
SESSION_PATH = Path("docs/development") / SESSION
MANIFEST_NAME = "assignments.json"
MAX_FILE_BYTES = 128 * 1024
MAX_DIRECTORY_ENTRIES = 256
SLOT_COUNT = 60
STATUSES = ("planned", "running", "complete")
NOTE_NAME = re.compile(r"([0-9]{2})-[a-z0-9]+(?:-[a-z0-9]+)*\.md\Z")
AGENT_NAME = re.compile(r"/root/w([0-9]{2})_a([0-9]{2})_[a-z0-9_]+\Z")
NOTE_HEADING = re.compile(
    r"# (?:(?:Continuation )?(?:assignment|review|agent) )?([0-9]{2})\b", re.IGNORECASE
)
AGENT_LINE = re.compile(
    r"^[ \t]*(?:-[ \t]+)?(?:\*\*)?(?:Actual )?Agent:(?:\*\*)?[ \t]*(.*)$",
    re.IGNORECASE | re.MULTILINE
)
AGENT_VALUE = re.compile(r"`(/root/[a-z0-9_]+)`(?:[.;,].*)?[ \t]*\Z", re.IGNORECASE)


class LedgerError(ValueError):
    """A missing or inconsistent retained assignment record."""


def require(condition, message):
    if not condition:
        raise LedgerError(message)


def read_text(path):
    """Read one bounded regular file; never follow a note/manifest symlink."""
    metadata = path.lstat()
    require(stat.S_ISREG(metadata.st_mode), f"not a regular file: {path.name}")
    require(metadata.st_size <= MAX_FILE_BYTES, f"file exceeds byte limit: {path.name}")
    with path.open("rb") as source:
        raw = source.read(MAX_FILE_BYTES + 1)
    require(len(raw) <= MAX_FILE_BYTES, f"file exceeds byte limit: {path.name}")
    # Identity rules apply to logical lines on both LF and CRLF checkouts.
    # Keep the bound on original bytes; normalization neither writes files nor
    # relaxes the requirement for exactly one matching explicit owner line.
    return raw.decode("utf-8").replace("\r\n", "\n")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON field: {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise LedgerError(f"non-finite JSON value: {value}")


def check_continuation(root, expected_complete=None):
    """Return actual declared counts after validating this session's records.

    The caller/integrator supplies truthful state transitions. Existing files
    never promote an assignment, and prior-session records are never read.
    """
    require(expected_complete is None or
            (type(expected_complete) is int and 0 <= expected_complete <= SLOT_COUNT),
            "expected-complete must be an integer from 0 to 60")
    root = Path(root).resolve(strict=True)
    session_dir = root
    for component in SESSION_PATH.parts:
        session_dir = session_dir / component
        require(not session_dir.is_symlink(), "session path must not contain symlinks")
    require(session_dir.is_dir(), f"missing session directory: {SESSION_PATH.as_posix()}")
    manifest = json.loads(read_text(session_dir / MANIFEST_NAME),
                          object_pairs_hook=unique_object, parse_constant=reject_constant)
    require(type(manifest) is dict and set(manifest) ==
            {"schema_version", "session", "assignments"}, "invalid manifest fields")
    require(type(manifest["schema_version"]) is int and manifest["schema_version"] == 1,
            "schema_version must be 1")
    require(manifest["session"] == SESSION, "manifest names a different session")
    assignments = manifest["assignments"]
    require(type(assignments) is list and len(assignments) == SLOT_COUNT,
            "manifest must contain exactly 60 assignment slots")

    counts = dict.fromkeys(STATUSES, 0)
    agents = set()
    expected_notes = {}
    for slot, record in enumerate(assignments, 1):
        require(type(record) is dict and set(record) ==
                {"id", "wave", "scope", "status", "agent", "note"},
                f"slot {slot:02d}: invalid assignment fields")
        require(type(record["id"]) is int and record["id"] == slot,
                "assignment IDs must be unique and ordered from 01 through 60")
        wave = (slot - 1) // 6 + 1
        require(type(record["wave"]) is int and record["wave"] == wave,
                f"assignment {slot:02d}: must belong to wave {wave:02d}")
        scope = record["scope"]
        require(type(scope) is str and 0 < len(scope.strip()) <= 1000,
                f"assignment {slot:02d}: scope must be nonempty and bounded")
        status = record["status"]
        require(type(status) is str and status in STATUSES,
                f"assignment {slot:02d}: invalid status")
        counts[status] += 1
        if status == "planned":
            require(record["agent"] is None and record["note"] is None,
                    f"planned assignment {slot:02d}: agent and note must be null")
            continue

        agent = record["agent"]
        match = AGENT_NAME.fullmatch(agent) if type(agent) is str else None
        require(match is not None, f"assignment {slot:02d}: missing canonical agent identity")
        require(agent not in agents, f"assignment {slot:02d}: duplicate actual agent identity")
        agents.add(agent)
        require((int(match[1]), int(match[2])) == (wave, slot),
                f"assignment {slot:02d}: agent identity belongs to another wave or slot")

        note = record["note"]
        if status == "running" and note is None:
            continue
        match = NOTE_NAME.fullmatch(note) if type(note) is str else None
        require(match is not None and int(match[1]) == slot,
                f"assignment {slot:02d}: note must be a session-local filename with matching ID")
        expected_notes[note] = record

    # Direct entries only: no repository walk, original-ledger access or recursion.
    numbered_notes = {}
    with os.scandir(session_dir) as entries:
        for count, entry in enumerate(entries, 1):
            require(count <= MAX_DIRECTORY_ENTRIES, "session directory exceeds entry limit")
            if not entry.name or not entry.name[0].isdigit():
                continue
            match = NOTE_NAME.fullmatch(entry.name)
            require(match is not None, f"noncanonical numbered note: {entry.name}")
            slot = int(match[1])
            require(1 <= slot <= SLOT_COUNT, f"extra numbered note: {entry.name}")
            require(slot not in numbered_notes, f"duplicate numbered note ID: {slot:02d}")
            numbered_notes[slot] = entry.name

    for slot, name in numbered_notes.items():
        require(name in expected_notes, f"unassigned numbered note: {name}")
        record = expected_notes[name]
        contents = read_text(session_dir / name)
        heading = NOTE_HEADING.match(contents.lstrip())
        require(heading is not None and int(heading[1]) == slot,
                f"note heading does not match assignment {slot:02d}: {name}")
        owner_lines = AGENT_LINE.findall(contents)
        identity = AGENT_VALUE.fullmatch(owner_lines[0]) if len(owner_lines) == 1 else None
        require(identity is not None and identity[1] == record["agent"],
                f"note must have exactly one matching explicit Agent identity: {name}")

    for name, record in expected_notes.items():
        if record["status"] == "complete":
            require(numbered_notes.get(record["id"]) == name,
                    f"complete assignment {record['id']:02d} is missing retained note: {name}")

    require(expected_complete is None or counts["complete"] == expected_complete,
            f"expected {expected_complete} complete assignments; found {counts['complete']} "
            f"complete, {counts['running']} running, {counts['planned']} planned")
    return {
        "status": "passed",
        "session": SESSION,
        "counts": counts,
        "dispatched": len(agents),
        "numbered_notes": len(numbered_notes),
        "waves": 10,
        "slots_per_wave": 6,
        "claim": "retained assignment-record consistency; external execution not attested",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1],
                        help="repository/archive root (only the designated session is read)")
    parser.add_argument("--expected-complete", type=int, metavar="N",
                        help="require exactly N completed assignments; use 60 for the final gate")
    parser.add_argument("--json", action="store_true", help="emit a structured result")
    args = parser.parse_args(argv)
    try:
        result = check_continuation(args.root, args.expected_complete)
    except (LedgerError, OSError, UnicodeError, json.JSONDecodeError, RecursionError) as error:
        result = {"status": "failed", "session": SESSION, "error": str(error)}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif result["status"] == "passed":
        counts = result["counts"]
        print(f"PASS {SESSION}: {counts['complete']} complete, {counts['running']} running, "
              f"{counts['planned']} planned; {result['dispatched']} distinct dispatched agents; "
              f"{result['numbered_notes']} retained numbered notes; 10 waves x 6 slots")
        print(result["claim"])
    else:
        print(f"FAIL {SESSION}: {result['error']}", file=sys.stderr)
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
