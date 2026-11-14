#!/usr/bin/env python3
"""Check this interface session's retained accounting; require completion by default."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys


SESSION = "2026-11-14-interface-continuation"
BASE_COMMIT = "d493e998e5dd7cf44db46854e87309745063ac54"
DIRECTORY = Path("docs/development") / SESSION
MANIFEST = (DIRECTORY / "assignments.json").as_posix()
SOURCE = "tools/check_interface_session.py"
MAX_MANIFEST_BYTES = 256 * 1024
MAX_NOTE_BYTES = 128 * 1024
AGENT = re.compile(r"/root/w([0-9]{2})_a([0-9]{2})_[a-z0-9]+(?:_[a-z0-9]+)*\Z")
CLAIM = ("Retained record consistency only. This does not attest actual dispatch, "
         "substantive acceptance, semantic truth, test execution, publication, "
         "product readiness or physical/model fidelity.")


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON member: {key[:80]}")
        result[key] = value
    return result


def _reject_number(value):
    raise ValueError(f"non-integer JSON number: {value[:80]}")


def _text(value, limit=8192):
    return (type(value) is str and 0 < len(value) <= limit and bool(value.strip()) and
            not any(ord(char) < 32 and char not in "\n\t" or ord(char) == 127
                    for char in value))


def _link(metadata):
    return (stat.S_ISLNK(metadata.st_mode) or bool(
        getattr(metadata, "st_file_attributes", 0) &
        getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)))


def _safe_path(root, relative):
    """Resolve normalized paths below root, rejecting links at every component."""
    if (type(relative) is not str or not 0 < len(relative) <= 1024 or not relative.strip() or
            "\\" in relative or ":" in relative or
            any(ord(char) < 32 or ord(char) == 127 for char in relative) or
            any(part in ("", ".", "..") for part in relative.split("/"))):
        raise ValueError("path must use normalized relative POSIX syntax")
    path = root
    parts = relative.split("/")
    for index, part in enumerate(parts):
        path /= part
        try:
            metadata = path.lstat()
        except FileNotFoundError:
            continue  # An actual running assignment may name an unwritten note.
        if _link(metadata):
            raise ValueError("path contains a symbolic link or reparse point")
        expected_type = stat.S_ISREG if index == len(parts) - 1 else stat.S_ISDIR
        if not expected_type(metadata.st_mode):
            raise ValueError("path must contain real directories and a regular file")
    if not path.resolve().is_relative_to(root):
        raise ValueError("path leaves the repository")
    return path


def _signature(metadata):
    return (metadata.st_dev, metadata.st_ino, metadata.st_mode, metadata.st_size,
            metadata.st_mtime_ns, metadata.st_ctime_ns)


def _read(root, relative, limit):
    path = _safe_path(root, relative)
    before = path.lstat()
    if before.st_size > limit:
        raise ValueError(f"file exceeds {limit}-byte limit")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    descriptor = os.open(path, flags)
    try:
        stream = os.fdopen(descriptor, "rb")
    except BaseException:
        os.close(descriptor)
        raise
    with stream:
        opened = os.fstat(stream.fileno())
        if (not stat.S_ISREG(opened.st_mode) or not os.path.samestat(before, opened)
                or before.st_size != opened.st_size):
            raise ValueError("file changed while opening")
        raw = stream.read(limit + 1)
        if (len(raw) > limit or len(raw) != opened.st_size or
                _signature(opened) != _signature(os.fstat(stream.fileno()))):
            raise ValueError("file changed while reading or exceeded its byte limit")
    if _signature(before) != _signature(path.lstat()):
        raise ValueError("file changed while reading")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    if "\x00" in text or "\r" in text:
        raise ValueError("text contains NUL or bare carriage return")
    return raw, text


def _narrative(text):
    """A small structural floor, with no required heading or owner-token format."""
    text = re.sub(r"<!--.*?(?:-->|$)", "", text, flags=re.DOTALL)
    lines, fence = [], None
    for line in text.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if fence:
            if (marker and marker[1][0] == fence[0] and
                    len(marker[1]) >= len(fence) and not line[marker.end():].strip()):
                fence = None
        elif marker:
            fence = marker[1]
        else:
            lines.append(line)
    return "\n".join(lines).strip()


def check(repo, in_progress=False):
    """Return declared counts and exact input identities without changing records."""
    errors, note_records = [], []
    numbers, agents, note_paths, accepted_numbers = set(), set(), set(), set()
    counts = {"recorded": 0, "accepted": 0, "running": 0, "invalid_status": 0,
              "malformed_rows": 0, "substantive_accepted_notes": 0}
    waves = [{"wave": wave, "recorded": 0, "accepted": 0, "running": 0}
             for wave in range(1, 11)]
    report = {
        "schema_version": 1, "session": SESSION, "base_commit": BASE_COMMIT,
        "mode": "in_progress" if in_progress else "strict_completion",
        "required_accepted": 60, "required_waves": 10, "assignments_per_wave": 6,
        "checker": {"path": SOURCE, "sha256": None},
        "manifest": {"path": MANIFEST, "sha256": None, "bytes": None},
        "scope": "retained_accounting_consistency_only",
        "external_dispatch_attested": False, "semantic_acceptance_attested": False,
        "product_or_model_readiness_attested": False, "claim": CLAIM,
    }

    def error(code, location, message):
        errors.append({"code": code, "location": location, "message": message})

    def finish():
        consistency = not errors
        missing = sorted(set(range(1, 61)) - numbers)
        complete = (consistency and counts["recorded"] == 60 and not missing and
                    counts["accepted"] == 60 and counts["substantive_accepted_notes"] == 60)
        if not in_progress:
            if counts["recorded"] != 60 or missing:
                error("completion_count", "assignments",
                      "strict completion requires exactly one record for every number 1-60")
            if counts["accepted"] != 60:
                error("completion_status", "assignments",
                      f"strict completion requires 60 accepted records; found {counts['accepted']}")
        note_records.sort(key=lambda item: (item["number"], item["result"]))
        note_identity = json.dumps(note_records, sort_keys=True, separators=(",", ":")).encode()
        report.update(
            status="failed" if errors else "passed" if complete else "incomplete",
            record_consistency_valid=consistency, completion_valid=complete,
            counts=dict(counts, distinct_numbers=len(numbers), distinct_agents=len(agents)),
            missing_numbers=missing,
            accepted_waves=[wave for wave in range(1, 11)
                            if set(range((wave - 1) * 6 + 1, wave * 6 + 1)) <= accepted_numbers
                            and waves[wave - 1]["recorded"] == 6],
            wave_counts=waves, checked_notes=note_records,
            checked_notes_sha256=hashlib.sha256(note_identity).hexdigest(),
            error_count=len(errors), errors=errors,
        )
        return report

    try:
        report["checker"]["sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        if type(in_progress) is not bool:
            raise ValueError("in_progress must be a boolean")
        root = Path(repo).resolve(strict=True)
        if not root.is_dir():
            raise ValueError("repository root must be a directory")
        raw, text = _read(root, MANIFEST, MAX_MANIFEST_BYTES)
        report["manifest"].update(sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
        manifest = json.loads(text, object_pairs_hook=_object,
                              parse_float=_reject_number, parse_constant=_reject_number)
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        error("manifest_read", MANIFEST, exc.strerror if isinstance(exc, OSError) else str(exc))
        return finish()

    fields = {"schema", "session", "requested_agents", "requested_waves", "batch_size",
              "base_commit", "scheduling", "assignments"}
    if type(manifest) is not dict or set(manifest) != fields:
        error("manifest_fields", "manifest", "members must match this session's existing schema")
        return finish()
    for key, value in (("schema", 1), ("requested_agents", 60),
                       ("requested_waves", 10), ("batch_size", 3)):
        if type(manifest[key]) is not int or manifest[key] != value:
            error("manifest_type", key, f"must be integer {value}, excluding boolean and float")
    if manifest["session"] != SESSION:
        error("session_identity", "session", "must identify this exact interface session")
    if manifest["base_commit"] != BASE_COMMIT:
        error("base_identity", "base_commit", "must match this session's exact starting commit")
    if not _text(manifest["scheduling"]):
        error("text_required", "scheduling", "must be nonempty bounded text")
    rows = manifest["assignments"]
    if type(rows) is not list or len(rows) > 60:
        error("assignments_type", "assignments", "must be a list of at most 60 actual records")
        return finish()
    counts["recorded"] = len(rows)
    for index, row in enumerate(rows):
        location = f"assignments[{index}]"
        if type(row) is not dict:
            counts["malformed_rows"] += 1
            error("row_type", location, "must be an assignment object")
            continue
        required = {"number", "wave", "agent", "scope", "status"}
        allowed = required | {"result", "acceptance"}
        if row.get("status") == "accepted":
            required = allowed
        if not required <= set(row) <= allowed:
            error("row_fields", location, "missing required or unexpected assignment members")
        number = row.get("number")
        valid_number = type(number) is int and 1 <= number <= 60
        if not valid_number:
            error("number_type", location + ".number", "must be an integer in 1-60")
        elif number in numbers:
            error("number_duplicate", location + ".number", f"number {number} appears more than once")
        else:
            numbers.add(number)
        wave = (number - 1) // 6 + 1 if valid_number else None
        valid_wave = type(row.get("wave")) is int and row["wave"] == wave
        if not valid_wave:
            error("wave_mapping", location + ".wave", "must equal (number - 1) // 6 + 1")
        if valid_wave:
            waves[wave - 1]["recorded"] += 1
        agent = row.get("agent")
        match = AGENT.fullmatch(agent) if type(agent) is str and len(agent) <= 256 else None
        if not match:
            error("agent_identity", location + ".agent", "needs a nonempty canonical /root/wNN_aNN_name identity")
        else:
            if agent in agents:
                error("agent_duplicate", location + ".agent", "identity appears more than once")
            agents.add(agent)
            if (int(match[1]), int(match[2])) != (wave, number):
                error("agent_mapping", location + ".agent", "identity must match this row's wave and number")
        state = row.get("status")
        if type(state) is not str or state not in ("accepted", "running"):
            counts["invalid_status"] += 1
            error("status_invalid", location + ".status", "only actual accepted/running records are allowed")
        else:
            counts[state] += 1
            if valid_wave:
                waves[wave - 1][state] += 1
            if state == "accepted" and valid_wave:
                accepted_numbers.add(number)
        for field in ("scope", "acceptance"):
            if field == "scope" or state == "accepted" or field in row:
                if not _text(row.get(field)):
                    error("text_required", location + "." + field, "must be nonempty bounded text")
        if state != "accepted" and "result" not in row:
            continue
        result = row.get("result")
        try:
            # Validate the declared relative path before adding the session prefix.
            _safe_path(root / DIRECTORY, result)
            relative = (DIRECTORY / result).as_posix()
            _safe_path(root, relative)
            if relative in note_paths:
                error("note_duplicate", location + ".result", "result note is reused by another row")
            note_paths.add(relative)
        except (OSError, ValueError) as exc:
            error("result_path", location + ".result",
                  exc.strerror if isinstance(exc, OSError) else str(exc))
            continue
        if state != "accepted":
            continue
        try:
            raw, text = _read(root, relative, MAX_NOTE_BYTES)
            prose = _narrative(text)
            words = len(re.findall(r"\w+", prose))
            if len(prose) < 200 or words < 30:
                error("note_substance", location + ".result",
                      "accepted note needs at least 200 narrative characters and 30 words")
            else:
                counts["substantive_accepted_notes"] += 1
            note_records.append({"number": number if valid_number else index + 1,
                                 "result": result, "bytes": len(raw),
                                 "sha256": hashlib.sha256(raw).hexdigest(),
                                 "narrative_words": words})
        except (OSError, UnicodeError, ValueError) as exc:
            error("note_read", location + ".result",
                  exc.strerror if isinstance(exc, OSError) else str(exc))
    return finish()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--in-progress", action="store_true",
                        help="allow actual running/missing assignments; report incomplete explicitly")
    parser.add_argument("--json", action="store_true", help="emit a deterministic JSON report")
    args = parser.parse_args(argv)
    report = check(args.repo, args.in_progress)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    else:
        counts = report["counts"]
        print(f"{report['status'].upper()} {SESSION}: {counts['accepted']}/60 declared accepted; "
              f"{counts['recorded']} recorded, {counts['running']} running; "
              f"completion_valid={report['completion_valid']}")
        print(CLAIM)
        for error in report["errors"]:
            print(f"{error['code']} at {error['location']}: {error['message']}", file=sys.stderr)
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
