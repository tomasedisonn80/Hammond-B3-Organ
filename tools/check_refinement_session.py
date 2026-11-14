#!/usr/bin/env python3
"""Check retained refinement records; strict sixty-assignment completion is the default."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat


SESSION = "2026-11-14-reference-refinement"
STARTING_COMMIT = "8bd999efc13e309b932e6ac41d72ceb7b9b80a5f"
DIRECTORY = Path("docs/development") / SESSION
MANIFEST = (DIRECTORY / "assignments.json").as_posix()
SOURCE = "tools/check_refinement_session.py"
MAX_MANIFEST_BYTES = 256 * 1024
MAX_NOTE_BYTES = 128 * 1024
MAX_CHECKER_BYTES = 256 * 1024
MIN_NARRATIVE_WORDS = 100
MIN_DISTINCT_WORDS = 40
IDS = frozenset(f"A{number:02d}" for number in range(1, 61))
AGENT = re.compile(r"/root/w([0-9]{2})_a([0-9]{2})_([a-z0-9]+(?:_[a-z0-9]+)*)\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
NOTE_NAME = re.compile(r"(A[0-9]{2})-[a-z0-9]+(?:[-_][a-z0-9]+)*\.md\Z")
PLACEHOLDER = re.compile(
    r"(?:todo|tbd|placeholder|unassigned|lorem ipsum)(?:\b|_)", re.IGNORECASE)
CLAIM = (
    "Retained record consistency only. This does not prove actual dispatch, "
    "substantive acceptance, semantic truth, test execution, publication, visual "
    "fidelity, product readiness or physical/model fidelity. The narrative floor "
    "is a structural check, not substantive review."
)


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON member: {key[:80]}")
        result[key] = value
    return result


def _integer(value):
    if len(value) > 8:
        raise ValueError("JSON integer exceeds the eight-character input limit")
    return int(value)


def _reject_number(value):
    raise ValueError(f"non-integer JSON number: {value[:80]}")


def _placeholder(text):
    first = text.strip().splitlines()[0].strip(" #>*_`[]{}():.-\t") if text.strip() else ""
    return (first.casefold() in {"pending", "unknown", "none", "n/a", "na", "not started"}
            or bool(PLACEHOLDER.match(first)))


def _text(value, limit=8192):
    return (type(value) is str and 0 < len(value) <= limit and bool(value.strip())
            and not any((ord(char) < 32 and char not in "\n\t") or ord(char) == 127
                        for char in value)
            and not _placeholder(value))


def _link(metadata):
    return (stat.S_ISLNK(metadata.st_mode) or bool(
        getattr(metadata, "st_file_attributes", 0)
        & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)))


def _identity(metadata):
    return (metadata.st_dev, metadata.st_ino, metadata.st_mode)


def _signature(metadata):
    return _identity(metadata) + (metadata.st_size, metadata.st_mtime_ns, metadata.st_ctime_ns)


def _safe_path(root, relative, allow_missing=True):
    """Admit only normalized repository paths; check each existing component."""
    if (type(relative) is not str or not 0 < len(relative) <= 1024
            or "\\" in relative or ":" in relative
            or any(ord(char) < 32 or ord(char) == 127 for char in relative)
            or any(part in ("", ".", "..") for part in relative.split("/"))):
        raise ValueError("path must use normalized relative POSIX syntax")
    path, identities = root, []
    parts = relative.split("/")
    for index, part in enumerate(parts):
        path /= part
        try:
            metadata = path.lstat()
        except FileNotFoundError:
            if not allow_missing:
                raise
            identities.append(None)
            continue
        if _link(metadata):
            raise ValueError("path contains a symbolic link or reparse point")
        expected = stat.S_ISREG if index == len(parts) - 1 else stat.S_ISDIR
        if not expected(metadata.st_mode):
            raise ValueError("path needs real directories and a regular file")
        identities.append(_identity(metadata))
    if not path.resolve().is_relative_to(root):
        raise ValueError("path leaves the repository")
    return path, identities


def _read(root, relative, limit):
    path, identities = _safe_path(root, relative, allow_missing=False)
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
        if (len(raw) > limit or len(raw) != opened.st_size
                or _signature(opened) != _signature(os.fstat(stream.fileno()))):
            raise ValueError("file changed while reading or exceeded its byte limit")
    _, after_identities = _safe_path(root, relative, allow_missing=False)
    if identities != after_identities or _signature(before) != _signature(path.lstat()):
        raise ValueError("file or path changed while reading")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    if any((ord(char) < 32 and char not in "\n\t") or ord(char) == 127 for char in text):
        raise ValueError("text contains a forbidden control character")
    return raw, text


def _narrative(text):
    """Exclude comments, fenced code and indented code from the structural floor."""
    text = re.sub(r"<!--.*?(?:-->|$)", "", text, flags=re.DOTALL)
    lines, fence = [], None
    for line in text.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if fence:
            if (marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence)
                    and not line[marker.end():].strip()):
                fence = None
        elif marker:
            fence = marker[1]
        elif not line.startswith(("    ", "\t")):
            lines.append(line)
    return "\n".join(lines).strip()


def check(repo, in_progress=False):
    """Return exact retained identities and declared counts without altering any input."""
    errors, note_records = [], []
    ids, agents, paths, accepted_ids = set(), set(), set(), set()
    counts = {"recorded": 0, "accepted": 0, "running": 0, "invalid_status": 0,
              "malformed_rows": 0, "verified_accepted_notes": 0}
    waves = [{"wave": wave, "recorded": 0, "accepted": 0, "running": 0}
             for wave in range(1, 11)]
    report = {
        "schema_version": 1, "session": SESSION, "starting_commit": STARTING_COMMIT,
        "mode": "in_progress" if in_progress is True else "strict_completion",
        "required_accepted": 60, "required_waves": 10, "assignments_per_wave": 6,
        "concurrency_limit_including_root": 4,
        "minimum_narrative_words": MIN_NARRATIVE_WORDS,
        "minimum_distinct_narrative_words": MIN_DISTINCT_WORDS,
        "checker": {"path": SOURCE, "sha256": None, "bytes": None},
        "manifest": {"path": MANIFEST, "sha256": None, "bytes": None},
        "scope": "retained_accounting_consistency_only",
        "external_dispatch_attested": False, "semantic_acceptance_attested": False,
        "execution_attested": False, "visual_fidelity_attested": False,
        "product_or_model_readiness_attested": False, "claim": CLAIM,
    }

    def error(code, location, message):
        errors.append({"code": code, "location": location, "message": str(message)[:500]})

    def failure(code, location, exc):
        error(code, location, (exc.strerror or str(exc)) if isinstance(exc, OSError) else str(exc))

    def finish():
        consistency = not errors
        missing = sorted(IDS - ids)
        complete = (consistency and counts["recorded"] == 60 and not missing
                    and len(agents) == 60 and counts["accepted"] == 60
                    and counts["verified_accepted_notes"] == 60
                    and all(wave["recorded"] == wave["accepted"] == 6 for wave in waves))
        if in_progress is not True:
            if counts["recorded"] != 60 or missing or len(agents) != 60:
                error("completion_count", "assignments",
                      "strict completion needs exactly 60 distinct actual identities, A01-A60")
            if counts["accepted"] != 60:
                error("completion_status", "assignments",
                      f"strict completion needs 60 accepted records; found {counts['accepted']}")
        note_records.sort(key=lambda item: (item["id"], item["note"]))
        identity = json.dumps(note_records, sort_keys=True, separators=(",", ":")).encode("utf-8")
        # Progress mode never certifies completion; run the strict gate to do that.
        completion = complete and in_progress is False
        report.update(
            status="failed" if errors else "passed" if completion else "incomplete",
            record_consistency_valid=consistency, completion_valid=completion,
            counts=dict(counts, distinct_ids=len(ids), distinct_agents=len(agents),
                        distinct_note_paths=len(paths)),
            missing_ids=missing,
            accepted_waves=[wave for wave in range(1, 11)
                            if {f"A{number:02d}" for number in range((wave - 1) * 6 + 1, wave * 6 + 1)}
                            <= accepted_ids and waves[wave - 1]["recorded"] == 6],
            wave_counts=waves, checked_notes=note_records,
            checked_notes_sha256=hashlib.sha256(identity).hexdigest(),
            error_count=len(errors), errors=errors,
        )
        return report

    try:
        source = Path(__file__).absolute()
        raw, _ = _read(source.parent.resolve(), source.name, MAX_CHECKER_BYTES)
        report["checker"].update(sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
        if type(in_progress) is not bool:
            raise ValueError("in_progress must be a boolean")
        root = Path(repo).absolute()
        if _link(root.lstat()):
            raise ValueError("repository root cannot be a symbolic link or reparse point")
        root = root.resolve(strict=True)
        if not root.is_dir():
            raise ValueError("repository root must be a directory")
        raw, text = _read(root, MANIFEST, MAX_MANIFEST_BYTES)
        report["manifest"].update(sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
        manifest = json.loads(text, object_pairs_hook=_object, parse_int=_integer,
                              parse_float=_reject_number, parse_constant=_reject_number)
    except (OSError, UnicodeError, ValueError, TypeError, RuntimeError) as exc:
        failure("manifest_read", MANIFEST, exc)
        return finish()

    fields = {"schema_version", "session", "starting_commit", "requested_agents",
              "requested_waves", "concurrency_limit_including_root", "counting", "assignments"}
    if type(manifest) is not dict or set(manifest) != fields:
        error("manifest_fields", "manifest", "members must match this exact session schema")
        return finish()
    for key, expected in (("schema_version", 1), ("requested_agents", 60),
                          ("requested_waves", 10), ("concurrency_limit_including_root", 4)):
        if type(manifest[key]) is not int or manifest[key] != expected:
            error("manifest_type", key, f"must be integer {expected}, excluding boolean and float")
    if type(manifest["session"]) is not str or manifest["session"] != SESSION:
        error("session_identity", "session", "must identify this exact refinement session")
    if type(manifest["starting_commit"]) is not str or manifest["starting_commit"] != STARTING_COMMIT:
        error("starting_identity", "starting_commit", "must match the canonical full starting commit")
    if not _text(manifest["counting"]):
        error("text_required", "counting", "needs bounded non-placeholder text")
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
        required = {"id", "wave", "agent", "status", "scope"}
        allowed = required | {"note", "note_sha256", "result"}
        state = row.get("status")
        if state == "accepted":
            required = allowed
        if not required <= set(row) <= allowed:
            error("row_fields", location, "missing required or unexpected assignment members")
        identifier = row.get("id")
        valid_id = type(identifier) is str and identifier in IDS
        if not valid_id:
            error("id_invalid", location + ".id", "must be an exact ID from A01 through A60")
        else:
            if identifier in ids:
                error("id_duplicate", location + ".id", "ID appears more than once")
            ids.add(identifier)
        number = int(identifier[1:]) if valid_id else None
        wave = (number - 1) // 6 + 1 if valid_id else None
        valid_wave = type(row.get("wave")) is int and row["wave"] == wave
        if not valid_wave:
            error("wave_mapping", location + ".wave", "must match six consecutive IDs per wave, 1-10")
        else:
            waves[wave - 1]["recorded"] += 1
        agent = row.get("agent")
        match = AGENT.fullmatch(agent) if type(agent) is str and len(agent) <= 256 else None
        if not match or any(token in {"todo", "tbd", "placeholder", "unassigned"}
                            for token in match[3].split("_")):
            error("agent_identity", location + ".agent", "needs a canonical /root/wNN_aNN_name identity")
        else:
            if agent in agents:
                error("agent_duplicate", location + ".agent", "identity appears more than once")
            agents.add(agent)
            if (int(match[1]), int(match[2])) != (wave, number):
                error("agent_mapping", location + ".agent", "identity must match this row's wave and ID")
        if type(state) is not str or state not in ("accepted", "running"):
            counts["invalid_status"] += 1
            error("status_invalid", location + ".status", "only actual accepted/running records are allowed")
        else:
            counts[state] += 1
            if valid_wave:
                waves[wave - 1][state] += 1
                if state == "accepted":
                    accepted_ids.add(identifier)
        for field in ("scope", "result"):
            if field == "scope" or state == "accepted" or field in row:
                if not _text(row.get(field)):
                    error("text_required", location + "." + field, "needs bounded non-placeholder text")
        declared = row.get("note_sha256")
        valid_hash = type(declared) is str and SHA256.fullmatch(declared) is not None
        if (state == "accepted" or "note_sha256" in row) and not valid_hash:
            error("note_hash", location + ".note_sha256", "needs an exact lowercase SHA-256 digest")
        if state != "accepted" and "note" not in row:
            if "note_sha256" in row:
                error("note_path", location + ".note", "a declared note hash requires a note path")
            continue
        relative = row.get("note")
        try:
            path, _ = _safe_path(root, relative)
            name = NOTE_NAME.fullmatch(path.name)
            if path.parent != root / DIRECTORY / "notes" or not name:
                raise ValueError("note must be an Axx-name.md file in this session's notes directory")
            if relative in paths:
                error("note_duplicate", location + ".note", "note path is reused by another record")
            paths.add(relative)
            if not valid_id or name[1] != identifier:
                raise ValueError("note filename must match the assignment ID")
            if state != "accepted" and not path.exists() and "note_sha256" not in row:
                continue  # A running assignment may explicitly name an unwritten note.
        except (OSError, ValueError, RuntimeError) as exc:
            failure("note_path", location + ".note", exc)
            continue
        try:
            raw, text = _read(root, relative, MAX_NOTE_BYTES)
            digest = hashlib.sha256(raw).hexdigest()
            prose = _narrative(text)
            words = re.findall(r"\w+", prose)
            distinct = len({word.casefold() for word in words})
            substantive = (len(words) >= MIN_NARRATIVE_WORDS and distinct >= MIN_DISTINCT_WORDS
                           and not _placeholder(prose))
            matches = valid_hash and digest == declared
            if state == "accepted" and not substantive:
                error("note_substance", location + ".note",
                      "accepted note needs 100 narrative words, 40 distinct words and no placeholder body")
            if (state == "accepted" or "note_sha256" in row) and not matches:
                error("note_hash_mismatch", location + ".note_sha256", "declared SHA-256 does not match actual bytes")
            if state == "accepted" and substantive and matches:
                counts["verified_accepted_notes"] += 1
            note_records.append({"id": identifier, "note": relative, "status": state,
                                 "bytes": len(raw), "sha256": digest,
                                 "declared_sha256": declared if valid_hash else None,
                                 "sha256_matches": matches, "narrative_words": len(words),
                                 "distinct_narrative_words": distinct, "structural_floor_met": substantive})
        except (OSError, UnicodeError, ValueError, RuntimeError) as exc:
            failure("note_read", location + ".note", exc)
    return finish()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--in-progress", action="store_true",
                        help="validate partial records without certifying completion")
    parser.add_argument("--json", action="store_true", help="emit JSON (also the default)")
    args = parser.parse_args(argv)
    report = check(args.repo, args.in_progress)
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
