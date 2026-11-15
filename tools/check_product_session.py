#!/usr/bin/env python3
"""Validate this product session's retained records; strict completion is the default.

Use --allow-incomplete while actual assignments are still being dispatched or
reviewed. That mode never certifies closure. Both modes reject inconsistent
accepted evidence. This is an accounting check, not dispatch or product evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat


SESSION = "2026-11-15-product-continuation"
START_COMMIT = "647ae1b2b6ad8d30ee28ab348b94f974fb6aadbb"
DIRECTORY = Path("docs/development") / SESSION
MANIFEST = (DIRECTORY / "assignments.json").as_posix()
SOURCE = "tools/check_product_session.py"
IDS = frozenset(f"A{number:02d}" for number in range(1, 61))
AGENT = re.compile(r"/root/w([0-9]{2})_a([0-9]{2})_([a-z0-9]+(?:_[a-z0-9]+)*)\Z")
NOTE = re.compile(r"notes/(A[0-9]{2})-[a-z0-9]+(?:[-_][a-z0-9]+)*\.md\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
MAX_MANIFEST_BYTES = 256 * 1024
MAX_NOTE_BYTES = 128 * 1024
MIN_NARRATIVE_WORDS = 100
MIN_DISTINCT_WORDS = 40
CLAIM = (
    "Retained record consistency only. This cannot attest actual tool dispatch, "
    "substantive integrator review, semantic truth, test execution, publication, "
    "product readiness, visual equality or physical/model fidelity. The narrative "
    "floor is a structural check; it does not replace substantive acceptance."
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
        raise ValueError("JSON integer exceeds eight characters")
    return int(value)


def _reject_number(value):
    raise ValueError(f"non-integer JSON number: {value[:80]}")


def _placeholder(text):
    first = text.strip().splitlines()[0].strip(" #>*_`[]{}():.-\t") if text.strip() else ""
    return (first.casefold() in {"pending", "unknown", "none", "n/a", "na", "not started"}
            or re.match(r"(?:todo|tbd|placeholder|unassigned|lorem ipsum)(?:\b|_)",
                        first, re.IGNORECASE) is not None)


def _text(value, limit=8192):
    return (type(value) is str and 0 < len(value) <= limit and bool(value.strip())
            and not any((ord(c) < 32 and c not in "\n\t") or ord(c) == 127 for c in value)
            and not _placeholder(value))


def _link(metadata):
    return (stat.S_ISLNK(metadata.st_mode) or bool(
        getattr(metadata, "st_file_attributes", 0)
        & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)))


def _identity(metadata):
    return metadata.st_dev, metadata.st_ino, metadata.st_mode


def _signature(metadata):
    return _identity(metadata) + (metadata.st_size, metadata.st_mtime_ns, metadata.st_ctime_ns)


def _safe_path(root, relative, *, allow_missing=False, directory_ok=False):
    """Check canonical local references without following symlinks/reparse points."""
    if (type(relative) is not str or not 0 < len(relative) <= 1024
            or "\\" in relative or ":" in relative or any(c in relative for c in "*?[]")
            or any(ord(c) < 32 or ord(c) == 127 for c in relative)
            or any(part in ("", ".", "..") or part != part.strip() for part in relative.split("/"))):
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
        last = index == len(parts) - 1
        if not (stat.S_ISDIR(metadata.st_mode) if not last else
                stat.S_ISREG(metadata.st_mode) or (directory_ok and stat.S_ISDIR(metadata.st_mode))):
            raise ValueError("path needs real directories and a regular file or admitted directory")
        identities.append(_identity(metadata))
    if not path.resolve().is_relative_to(root):
        raise ValueError("path leaves the repository")
    return path, identities


def _read(root, relative, limit):
    # The bounded reader mirrors the repository's retained-record reader policy:
    # reject special files before open, reject links, and detect changed inputs.
    path, identities = _safe_path(root, relative)
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
        if not stat.S_ISREG(opened.st_mode) or _signature(before) != _signature(opened):
            raise ValueError("file changed while opening")
        raw = stream.read(limit + 1)
        if (len(raw) > limit or len(raw) != opened.st_size
                or _signature(opened) != _signature(os.fstat(stream.fileno()))):
            raise ValueError("file changed while reading or exceeded its byte limit")
    _, after = _safe_path(root, relative)
    if identities != after or _signature(before) != _signature(path.lstat()):
        raise ValueError("file or path changed while reading")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    if any((ord(c) < 32 and c not in "\n\t") or ord(c) == 127 for c in text):
        raise ValueError("text contains a forbidden control character")
    return raw, text


def _ownership(reference):
    """Separate the existing ledger's optional ' (scope)' suffix from its path."""
    if type(reference) is not str or len(reference) > 2048 or reference != reference.strip():
        raise ValueError("ownership needs a bounded path, optionally followed by ' (scope)'")
    path, marker, suffix = reference.partition(" (")
    scope = None
    if marker:
        if not suffix.endswith(")") or not _text(suffix[:-1], 1024):
            raise ValueError("ownership scope must be nonempty text in a closing parenthesis")
        scope = suffix[:-1]
    directory = path.endswith("/")
    return path[:-1] if directory else path, scope, directory


def _narrative(text):
    """Exclude comments, fenced code and indented code from the narrative floor."""
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


def check(repo, allow_incomplete=False):
    """Return declared counts, byte identities and errors without changing inputs."""
    errors, notes, ownership = [], [], []
    ids, agents, note_paths, accepted_ids = set(), set(), set(), set()
    counts = {"recorded": 0, "accepted": 0, "review_complete": 0, "running": 0,
              "invalid_status": 0, "verified_accepted_notes": 0}
    waves = [{"wave": wave, "recorded": 0, "accepted": 0, "review_complete": 0, "running": 0}
             for wave in range(1, 11)]
    report = {
        "schema": "b3-product-session-check-v1", "session": SESSION,
        "start_commit": START_COMMIT,
        "mode": "allow_incomplete" if allow_incomplete is True else "strict_completion",
        "required_accepted": 60, "required_waves": 10, "assignments_per_wave": 6,
        "minimum_narrative_words": MIN_NARRATIVE_WORDS,
        "minimum_distinct_narrative_words": MIN_DISTINCT_WORDS,
        "checker": {"path": SOURCE, "sha256": None, "bytes": None},
        "manifest": {"path": MANIFEST, "sha256": None, "bytes": None},
        "scope": "retained_record_consistency_only", "external_dispatch_attested": False,
        "semantic_acceptance_attested": False, "execution_attested": False,
        "product_or_model_readiness_attested": False, "claim": CLAIM,
    }

    def error(code, location, message):
        message = message.strerror or str(message) if isinstance(message, OSError) else str(message)
        errors.append({"code": code, "location": location, "message": message[:500]})

    def finish():
        consistent = not errors
        missing = sorted(IDS - ids)
        if allow_incomplete is not True:
            if counts["recorded"] != 60 or missing or len(agents) != 60:
                error("completion_count", "assignments", "strict closure requires 60 distinct IDs A01-A60 and agents")
            if counts["accepted"] != 60 or counts["verified_accepted_notes"] != 60:
                error("completion_status", "assignments", "strict closure requires 60 accepted, verified notes")
            if not all(wave["recorded"] == wave["accepted"] == 6 for wave in waves):
                error("completion_waves", "assignments", "strict closure requires ten waves of six accepted records")
        complete = not errors and allow_incomplete is False
        note_identity = json.dumps(notes, sort_keys=True, separators=(",", ":")).encode("utf-8")
        report.update(
            status="failed" if errors else "passed" if complete else "incomplete",
            record_consistency_valid=consistent, completion_valid=complete,
            counts=dict(counts, distinct_ids=len(ids), distinct_agents=len(agents),
                        distinct_note_paths=len(note_paths)),
            missing_ids=missing, wave_counts=waves,
            accepted_waves=[wave["wave"] for wave in waves if wave["recorded"] == wave["accepted"] == 6
                            and {f"A{n:02d}" for n in range((wave["wave"] - 1) * 6 + 1, wave["wave"] * 6 + 1)}
                            <= accepted_ids],
            checked_notes=notes, checked_notes_sha256=hashlib.sha256(note_identity).hexdigest(),
            checked_ownership=ownership, error_count=len(errors), errors=errors)
        return report

    try:
        if type(allow_incomplete) is not bool:
            raise ValueError("allow_incomplete must be boolean")
        source = Path(__file__).absolute()
        raw, _ = _read(source.parent.resolve(), source.name, 256 * 1024)
        report["checker"].update(sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
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
        error("manifest_read", MANIFEST, exc)
        return finish()

    expected = {"schema": "b3-product-session-v1", "session": SESSION,
                "started_at_utc": "2026-11-15", "client_date": "2026-11-14",
                "start_commit": START_COMMIT, "requested_agents": 60,
                "requested_waves": 10, "concurrency": 3}
    if type(manifest) is not dict or set(manifest) != set(expected) | {"assignments"}:
        error("manifest_fields", "manifest", "members must match this product session's v1 schema")
        return finish()
    for field, value in expected.items():
        if type(manifest[field]) is not type(value) or manifest[field] != value:
            error("manifest_identity", field, f"must be {value!r} with the exact declared type")
    rows = manifest["assignments"]
    if type(rows) is not list or len(rows) > 60:
        error("assignments_type", "assignments", "must be a list of at most 60 actual records")
        return finish()
    counts["recorded"] = len(rows)
    for index, row in enumerate(rows):
        location = f"assignments[{index}]"
        if type(row) is not dict:
            error("row_type", location, "must be an assignment object")
            continue
        required = {"id", "wave", "agent", "task", "status", "owned_files"}
        allowed = required | {"note", "result", "acceptance", "note_sha256"}
        state = row.get("status")
        evidence_required = state in ("accepted", "review_complete")
        if evidence_required:
            required |= {"note", "acceptance", "note_sha256"}
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
        if not match or any(word in {"todo", "tbd", "placeholder", "unassigned"} for word in match[3].split("_")):
            error("agent_identity", location + ".agent", "needs a canonical /root/wNN_aNN_name identity")
        else:
            if agent in agents:
                error("agent_duplicate", location + ".agent", "agent identity appears more than once")
            agents.add(agent)
            if (int(match[1]), int(match[2])) != (wave, number):
                error("agent_mapping", location + ".agent", "agent must match this row's wave and ID")
        if type(state) is not str or state not in ("accepted", "review_complete", "running"):
            counts["invalid_status"] += 1
            error("status_invalid", location + ".status", "only actual running/review_complete/accepted states are allowed")
        else:
            counts[state] += 1
            if valid_wave:
                waves[wave - 1][state] += 1
                if state == "accepted":
                    accepted_ids.add(identifier)
        for field in ("task", "acceptance", "result"):
            if field == "task" or (field == "acceptance" and evidence_required) or field in row:
                if not _text(row.get(field)):
                    error("text_required", location + "." + field, "needs bounded non-placeholder text")

        owned = row.get("owned_files")
        if type(owned) is not list or not 1 <= len(owned) <= 128:
            error("ownership_list", location + ".owned_files", "needs 1-128 scoped file or directory references")
        else:
            seen = set()
            for offset, reference in enumerate(owned):
                try:
                    relative, scope, directory = _ownership(reference)
                    path, identities = _safe_path(root, relative, allow_missing=not evidence_required, directory_ok=True)
                    exists = identities[-1] is not None
                    if directory and exists and not path.is_dir():
                        raise ValueError("a trailing slash must identify a directory")
                    key = (relative, scope)
                    if key in seen:
                        raise ValueError("duplicate ownership reference")
                    seen.add(key)
                    ownership.append({"id": identifier, "path": relative, "scope": scope,
                                      "exists": exists, "directory": path.is_dir() if exists else directory})
                except (OSError, ValueError, RuntimeError) as exc:
                    error("ownership_path", location + f".owned_files[{offset}]", exc)

        declared = row.get("note_sha256")
        valid_hash = type(declared) is str and SHA256.fullmatch(declared) is not None
        if (evidence_required or "note_sha256" in row) and not valid_hash:
            error("note_hash", location + ".note_sha256", "needs an exact lowercase SHA-256 digest")
        if not evidence_required and "note" not in row:
            if "note_sha256" in row:
                error("note_path", location + ".note", "a declared hash requires a note path")
            continue
        relative = row.get("note")
        try:
            name = NOTE.fullmatch(relative) if type(relative) is str and len(relative) <= 256 else None
            if not name or not valid_id or name[1] != identifier:
                raise ValueError("note must be notes/Axx-name.md in this session, matching the row ID")
            if relative in note_paths:
                error("note_duplicate", location + ".note", "note path appears more than once")
            note_paths.add(relative)
            reference = (DIRECTORY / relative).as_posix()
            path, identities = _safe_path(root, reference, allow_missing=True)
            if not evidence_required and identities[-1] is None and "note_sha256" not in row:
                continue
        except (OSError, ValueError, RuntimeError) as exc:
            error("note_path", location + ".note", exc)
            continue
        try:
            raw, text = _read(root, reference, MAX_NOTE_BYTES)
            digest = hashlib.sha256(raw).hexdigest()
            prose = _narrative(text)
            words = re.findall(r"\w+", prose)
            distinct = len({word.casefold() for word in words})
            substantive = (len(words) >= MIN_NARRATIVE_WORDS and distinct >= MIN_DISTINCT_WORDS
                           and not _placeholder(prose))
            matches = valid_hash and digest == declared
            if evidence_required and not substantive:
                error("note_substance", location + ".note", "reviewed/accepted note needs 100 narrative words and 40 distinct words")
            if (evidence_required or "note_sha256" in row) and not matches:
                error("note_hash_mismatch", location + ".note_sha256", "declared SHA-256 does not match retained bytes")
            if state == "accepted" and substantive and matches:
                counts["verified_accepted_notes"] += 1
            notes.append({"id": identifier, "note": relative, "status": state, "bytes": len(raw),
                          "sha256": digest, "declared_sha256": declared if valid_hash else None,
                          "sha256_matches": matches, "narrative_words": len(words),
                          "distinct_narrative_words": distinct, "structural_floor_met": substantive})
        except (OSError, UnicodeError, ValueError, RuntimeError) as exc:
            error("note_read", location + ".note", exc)
    return finish()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--allow-incomplete", action="store_true",
                        help="check actual progress without certifying closure; accepted evidence stays mandatory")
    parser.add_argument("--json", action="store_true", help="emit JSON (also the default)")
    args = parser.parse_args(argv)
    report = check(args.repo, args.allow_incomplete)
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
