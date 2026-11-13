#!/usr/bin/env python3
"""Check this pedal session's retained records; do not attest external execution."""

import argparse
import json
import os
from pathlib import Path
import re
import stat
import sys


SESSION_ID = "2026-11-13-pedals"
BASELINE_COMMIT = "b4fc61ccfcc59724f14fb0cee947ed7bb7142075"
SESSION_PATH = Path("docs/development") / SESSION_ID
SLOT_COUNT = 60
WAVE_COUNT = 10
SLOTS_PER_WAVE = 6
MAX_MANIFEST_BYTES = 64 * 1024
MAX_NOTE_BYTES = 128 * 1024
MAX_DIRECTORY_ENTRIES = 256
MAX_ERROR_CHARS = 1000
STATES = ("planned", "running", "complete")
NOTE_NAME = re.compile(r"([0-9]{2})-[a-z0-9]+(?:-[a-z0-9]+)*\.md\Z")
AGENT_NAME = re.compile(r"/root/w([0-9]{2})_a([0-9]{2})_[a-z0-9]+(?:_[a-z0-9]+)*\Z")
AGENT_TOKEN = re.compile(r"(?<![a-zA-Z0-9_/])/root/[a-zA-Z0-9_/]+(?![a-zA-Z0-9_/])")
NOTE_TITLE = re.compile(r"#\s+(?:(?:pedal\s+)?(?:assignment|review|agent)\s+)?([0-9]{1,2})\b",
                        re.IGNORECASE)
OWNER_PREFIX = re.compile(r"^(?:[-+*]\s+)?(?:actual\s+)?(?:owner|agent|worker|assignment)\b",
                          re.IGNORECASE)
CLAIM = ("Retained assignment-record consistency only; actual dispatch, semantic review, "
         "test execution and publication require the integrator's separate evidence.")


class LedgerError(ValueError):
    """A missing, malformed or inconsistent retained pedal-session record."""


def require(condition, message):
    if not condition:
        raise LedgerError(message)


def _is_link(metadata):
    # is_symlink alone does not include all Windows directory reparse points.
    return (stat.S_ISLNK(metadata.st_mode) or
            bool(getattr(metadata, "st_file_attributes", 0) &
                 getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)))


def _signature(metadata):
    return (metadata.st_dev, metadata.st_ino, metadata.st_mode, metadata.st_size,
            metadata.st_mtime_ns, metadata.st_ctime_ns)


def _read_text(path, limit):
    """Read bounded regular bytes and normalize CRLF without rewriting input.

    Cross-API checks compare file identity/type/size. Full before/after checks
    stay within the same API because Windows path/descriptor metadata can differ.
    The caller supplies a quiescent checkout; this is not a filesystem sandbox.
    """
    before = path.lstat()
    require(not _is_link(before) and stat.S_ISREG(before.st_mode),
            f"not a regular, non-link file: {path.name}")
    require(before.st_size <= limit, f"file exceeds byte limit: {path.name}")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    flags |= getattr(os, "O_NONBLOCK", 0)
    with os.fdopen(os.open(path, flags), "rb") as source:
        opened = os.fstat(source.fileno())
        require(stat.S_ISREG(opened.st_mode) and os.path.samestat(before, opened) and
                before.st_size == opened.st_size, f"file changed while opening: {path.name}")
        raw = source.read(limit + 1)
        require(len(raw) <= limit, f"file exceeds byte limit: {path.name}")
        require(len(raw) == opened.st_size and _signature(opened) ==
                _signature(os.fstat(source.fileno())), f"file changed while reading: {path.name}")
    after = path.lstat()
    require(_signature(before) == _signature(after) and not _is_link(after),
            f"file changed while reading: {path.name}")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    require("\r" not in text and "\x00" not in text,
            f"file contains a bare CR or NUL: {path.name}")
    return text


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON field: {key[:80]}")
        result[key] = value
    return result


def _integer(value):
    require(len(value) <= 20, "JSON integer exceeds supported length")
    return int(value)


def _reject_number(value):
    raise LedgerError(f"non-integer JSON number: {value[:80]}")


def _prose_lines(text):
    """Ignore fenced examples when looking for titles, ownership and narrative."""
    fence_character = None
    fence_length = 0
    for line in text.splitlines():
        stripped = line.strip()
        fence = re.match(r"^(`{3,}|~{3,})", stripped)
        if fence_character is not None:
            if (fence is not None and fence[1][0] == fence_character and
                    len(fence[1]) >= fence_length and not stripped[len(fence[1]):].strip()):
                fence_character = None
            continue
        if fence is not None:
            fence_character = fence[1][0]
            fence_length = len(fence[1])
            continue
        yield line


def _check_complete_note(text, record):
    slot, name, agent = record["assignment"], record["note"], record["agent"]
    lines = list(_prose_lines(text))
    titles = [line for line in lines if line.startswith("# ")]
    title = NOTE_TITLE.match(titles[0]) if titles else None
    require(title is not None and int(title[1]) == slot,
            f"complete note title must identify assignment {slot:02d}: {name}")
    owners = []
    for line in lines:
        plain = line.replace("**", "").strip()
        if OWNER_PREFIX.match(plain):
            owners.extend(AGENT_TOKEN.findall(plain))
    require(owners and all(owner == agent for owner in owners),
            f"complete note must explicitly identify its canonical owner: {name}")

    # This is only a minimum retained-report structure, not a semantic quality
    # judgement. Existing notes use different heading and ownership formats.
    sections = []
    for line in lines:
        if line.startswith("## "):
            sections.append([])
        elif sections and line.strip() and not line.lstrip().startswith("#"):
            if not OWNER_PREFIX.match(line.replace("**", "").strip()):
                sections[-1].append(line)
    populated = sum(len(re.findall(r"\w+", "\n".join(section))) >= 8 for section in sections)
    require(populated >= 2,
            f"complete note needs at least two populated narrative sections: {name}")


def check_pedal_session(repo, expected_complete=None):
    """Return the validated declared counts without promoting any assignment.

    Only this session's manifest and direct numbered notes are read. Older
    sixty-worker sessions, Git history and external execution are not consulted.
    """
    require(expected_complete is None or
            (type(expected_complete) is int and 0 <= expected_complete <= SLOT_COUNT),
            "expected-complete must be an integer from 0 to 60")
    repo = Path(repo).resolve(strict=True)
    require(repo.is_dir(), "repository root must be a directory")
    session_dir = repo
    for component in SESSION_PATH.parts:
        session_dir /= component
        metadata = session_dir.lstat()
        require(not _is_link(metadata) and stat.S_ISDIR(metadata.st_mode),
                f"session path must contain only real directories: {component}")

    manifest = json.loads(_read_text(session_dir / "assignments.json", MAX_MANIFEST_BYTES),
                          object_pairs_hook=_unique_object, parse_int=_integer,
                          parse_float=_reject_number, parse_constant=_reject_number)
    require(type(manifest) is dict and set(manifest) == {
        "schema_version", "session_id", "baseline_commit", "requested_agents",
        "requested_waves", "assignments"}, "invalid manifest fields")
    for field, expected in (("schema_version", 1), ("requested_agents", SLOT_COUNT),
                            ("requested_waves", WAVE_COUNT)):
        require(type(manifest[field]) is int and manifest[field] == expected,
                f"{field} must be integer {expected}")
    require(manifest["session_id"] == SESSION_ID, "manifest names a different session")
    require(manifest["baseline_commit"] == BASELINE_COMMIT, "manifest has a different baseline")
    records = manifest["assignments"]
    require(type(records) is list and len(records) == SLOT_COUNT,
            "manifest must contain exactly 60 assignment slots")

    counts = dict.fromkeys(STATES, 0)
    waves = [dict.fromkeys(STATES, 0) for _ in range(WAVE_COUNT)]
    assignments, agents, notes = {}, set(), {}
    for record in records:
        require(type(record) is dict and set(record) == {
            "assignment", "wave", "state", "agent", "scope", "note"},
            "invalid assignment fields")
        slot = record["assignment"]
        require(type(slot) is int and 1 <= slot <= SLOT_COUNT,
                "assignment must be an integer from 1 to 60")
        require(slot not in assignments, f"duplicate assignment slot: {slot:02d}")
        assignments[slot] = record
        wave = (slot - 1) // SLOTS_PER_WAVE + 1
        require(type(record["wave"]) is int and record["wave"] == wave,
                f"assignment {slot:02d} must belong to wave {wave:02d}")
        state = record["state"]
        require(type(state) is str and state in STATES, f"assignment {slot:02d} has invalid state")
        counts[state] += 1
        waves[wave - 1][state] += 1
        if state == "planned":
            require(record["agent"] is None and record["scope"] is None and record["note"] is None,
                    f"planned assignment {slot:02d} must have null agent, scope and note")
            continue
        scope = record["scope"]
        require(type(scope) is str and 0 < len(scope.strip()) and len(scope) <= 1000 and "\x00" not in scope,
                f"dispatched assignment {slot:02d} needs a bounded nonempty scope")
        agent = record["agent"]
        match = AGENT_NAME.fullmatch(agent) if type(agent) is str and len(agent) <= 256 else None
        require(match is not None, f"assignment {slot:02d} needs a canonical agent identity")
        require(agent not in agents, f"duplicate actual agent identity at assignment {slot:02d}")
        agents.add(agent)
        require((int(match[1]), int(match[2])) == (wave, slot),
                f"assignment {slot:02d} agent names a different wave or slot")
        note = record["note"]
        if state == "running" and note is None:
            continue
        match = NOTE_NAME.fullmatch(note) if type(note) is str and len(note) <= 160 else None
        require(match is not None and int(match[1]) == slot,
                f"assignment {slot:02d} note must be a session-local filename with matching ID")
        notes[note] = record

    numbered = {}
    with os.scandir(session_dir) as entries:
        for count, entry in enumerate(entries, 1):
            require(count <= MAX_DIRECTORY_ENTRIES, "session directory exceeds entry limit")
            if not entry.name or not entry.name[0].isdigit():
                continue
            match = NOTE_NAME.fullmatch(entry.name)
            require(match is not None, f"noncanonical numbered note: {entry.name}")
            slot = int(match[1])
            require(1 <= slot <= SLOT_COUNT, f"extra numbered note: {entry.name}")
            require(slot not in numbered, f"duplicate numbered note for assignment {slot:02d}")
            require(entry.name in notes, f"unassigned numbered note: {entry.name}")
            numbered[slot] = entry.name

    retained = dict.fromkeys(("complete", "running"), 0)
    for name, record in notes.items():
        present = numbered.get(record["assignment"]) == name
        require(present or record["state"] == "running",
                f"complete assignment {record['assignment']:02d} is missing retained note: {name}")
        if not present:
            continue
        text = _read_text(session_dir / name, MAX_NOTE_BYTES)
        retained[record["state"]] += 1
        if record["state"] == "complete":
            _check_complete_note(text, record)

    require(expected_complete is None or counts["complete"] == expected_complete,
            f"expected {expected_complete} complete assignments; found {counts['complete']} "
            f"complete, {counts['running']} running, {counts['planned']} planned")
    return {
        "schema_version": 1, "status": "passed", "session_id": SESSION_ID,
        "baseline_commit": BASELINE_COMMIT, "counts": counts, "dispatched": len(agents),
        "retained_notes": retained, "completed_waves": sum(w["complete"] == 6 for w in waves),
        "wave_counts": [dict(wave=index + 1, **value) for index, value in enumerate(waves)],
        "expected_complete": expected_complete, "claim": CLAIM,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1],
                        help="repository/archive root; defaults to this script's parent repository")
    parser.add_argument("--expected-complete", type=int, metavar="N",
                        help="require exactly N complete records, from 0 to 60; 60 is the final gate")
    parser.add_argument("--json", action="store_true", help="emit a structured report on stdout")
    args = parser.parse_args(argv)
    try:
        result = check_pedal_session(args.repo, args.expected_complete)
    except (LedgerError, OSError, UnicodeError, json.JSONDecodeError, RecursionError) as error:
        result = {"schema_version": 1, "status": "failed", "session_id": SESSION_ID,
                  "error": str(error)[:MAX_ERROR_CHARS]}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif result["status"] == "passed":
        counts = result["counts"]
        print(f"PASS {SESSION_ID}: {counts['complete']} complete, {counts['running']} running, "
              f"{counts['planned']} planned; {result['dispatched']} distinct dispatched agents; "
              f"{result['completed_waves']}/10 complete waves")
        print(CLAIM)
    else:
        print(f"FAIL {SESSION_ID}: {result['error']}", file=sys.stderr)
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
