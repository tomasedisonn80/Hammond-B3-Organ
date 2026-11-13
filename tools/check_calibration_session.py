#!/usr/bin/env python3
"""Check retained calibration-session accounting, not dispatch or hardware claims."""

from __future__ import annotations

import argparse
from collections import Counter
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys

SESSION = "2026-11-13-calibration"
BASELINE = "38c1fac949368fa54bd86c6c00a5997a73480f5e"
DIRECTORY = Path("docs/development") / SESSION
MAX_MANIFEST_BYTES = 256 * 1024
MAX_NOTE_BYTES = 128 * 1024
MAX_OWNED_FILE_BYTES = 64 * 1024 * 1024
MAX_OWNED_FILES = 64
MAX_PATH_CHARACTERS = 512
STATES = ("planned", "running", "complete")


def _object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def _constant(value: str) -> object:
    raise ValueError(f"nonstandard JSON constant: {value}")


def _integer(value: object) -> bool:
    return type(value) is int


def _relative(value: object) -> bool:
    if not isinstance(value, str) or not 0 < len(value) <= MAX_PATH_CHARACTERS:
        return False
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        return False
    if "\\" in value or ":" in value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and all(part not in ("", ".", "..")
                                          for part in value.split("/"))


def _regular(root: Path, relative: str, limit: int) -> Path:
    """Inspect every component; do not accept links even within the repository."""
    if not _relative(relative):
        raise ValueError("path must be a safe normalized repository-relative path")
    candidate = root
    parts = relative.split("/")
    for index, part in enumerate(parts):
        candidate /= part
        metadata = candidate.lstat()
        if stat.S_ISLNK(metadata.st_mode):
            raise ValueError(f"symbolic links are not allowed: {relative}")
        if getattr(metadata, "st_file_attributes", 0) & getattr(
            stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400
        ):
            raise ValueError(f"Windows reparse points are not allowed: {relative}")
        if index < len(parts) - 1:
            if not stat.S_ISDIR(metadata.st_mode):
                raise ValueError(f"path parent must be a real directory: {relative}")
        elif not stat.S_ISREG(metadata.st_mode):
            raise ValueError(f"path must be a regular file: {relative}")
        elif metadata.st_size > limit:
            raise ValueError(f"file exceeds {limit}-byte limit: {relative}")
    if not candidate.resolve(strict=True).is_relative_to(root):
        raise ValueError(f"path leaves the repository: {relative}")
    return candidate


def _read_text(root: Path, relative: str, limit: int) -> str:
    candidate = _regular(root, relative, limit)
    # A bounded read also catches growth after the size check. O_NONBLOCK avoids
    # a blocking FIFO if the final component changes between inspection/open.
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    descriptor = os.open(candidate, flags)
    try:
        stream = os.fdopen(descriptor, "rb")
    except BaseException:
        os.close(descriptor)
        raise
    with stream:
        metadata = os.fstat(stream.fileno())
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > limit:
            raise ValueError(f"input must remain a bounded regular file: {relative}")
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ValueError(f"file exceeds {limit}-byte limit: {relative}")
    return data.decode("utf-8")


def check(repo: Path, expected_complete: int | None = None) -> dict[str, object]:
    """Read this manifest once and report declared states without promoting them."""
    errors: list[str] = []
    counts: Counter[str] = Counter()
    identities: set[str] = set()
    notes: set[str] = set()
    completed_waves: list[int] = []
    report: dict[str, object] = {
        "schema_version": 1,
        "session_id": SESSION,
        "baseline_commit": BASELINE,
        "scope": "retained_accounting_consistency_only",
        "external_dispatch_attested": False,
        "physical_fidelity": "not_established",
        "expected_complete": expected_complete,
        "errors": errors,
    }

    def finish() -> dict[str, object]:
        report.update(
            status="failed" if errors else "passed",
            counts={state: counts[state] for state in STATES},
            distinct_actual_agents=len(identities),
            completed_waves=completed_waves,
            error_count=len(errors),
        )
        return report

    if expected_complete is not None and (
        not _integer(expected_complete) or not 0 <= expected_complete <= 60
    ):
        errors.append("expected_complete must be an integer in 0..60")
        return finish()
    try:
        root = Path(repo).resolve(strict=True)
        if not root.is_dir():
            raise ValueError("repository must be a directory")
        manifest = json.loads(
            _read_text(root, (DIRECTORY / "assignments.json").as_posix(), MAX_MANIFEST_BYTES),
            object_pairs_hook=_object, parse_constant=_constant,
        )
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        errors.append(f"cannot read manifest: {exc}")
        return finish()
    fields = {"schema_version", "session_id", "baseline_commit", "requested_agents",
              "requested_waves", "concurrency", "assignments"}
    if not isinstance(manifest, dict) or set(manifest) != fields:
        errors.append("manifest members must match the calibration session schema")
        return finish()
    for key, expected in (("schema_version", 1), ("requested_agents", 60),
                          ("requested_waves", 10), ("concurrency", 3)):
        if not _integer(manifest[key]) or manifest[key] != expected:
            errors.append(f"{key} must be integer {expected}")
    if manifest["session_id"] != SESSION:
        errors.append("wrong session identity")
    if manifest["baseline_commit"] != BASELINE:
        errors.append("baseline_commit must match this session's exact starting commit")
    rows = manifest["assignments"]
    if not isinstance(rows, list) or len(rows) != 60:
        errors.append("exactly 60 ordered assignment slots are required")
        return finish()
    row_fields = {"assignment", "wave", "state", "agent", "scope", "note", "owned_files"}
    for index, row in enumerate(rows, 1):
        prefix = f"assignment {index}: "
        if not isinstance(row, dict) or set(row) != row_fields:
            errors.append(prefix + "unexpected or missing members")
            continue
        wave = (index - 1) // 6 + 1
        if not _integer(row["assignment"]) or row["assignment"] != index:
            errors.append(prefix + "identity/order mismatch")
        if not _integer(row["wave"]) or row["wave"] != wave:
            errors.append(prefix + "wave must contain its six ordered assignments")
        state = row["state"]
        if not isinstance(state, str) or state not in STATES:
            errors.append(prefix + "invalid state")
            continue
        counts[state] += 1
        agent = row["agent"]
        canonical_agent = f"/root/cal_w{wave}_a{index:02d}"
        if state == "planned":
            if agent is not None:
                errors.append(prefix + "planned work cannot claim a dispatched identity")
        else:
            if not isinstance(agent, str) or agent != canonical_agent:
                errors.append(prefix + "actual work needs its canonical current-session worker identity")
            if isinstance(agent, str):
                if agent in identities:
                    errors.append(prefix + "worker identity was counted more than once")
                elif agent == canonical_agent:
                    identities.add(agent)
        scope = row["scope"]
        if not isinstance(scope, str) or not scope.strip() or len(scope) > 1000 or any(
            ord(char) < 32 or ord(char) == 127 for char in scope
        ):
            errors.append(prefix + "scope must be bounded nonempty text without control characters")
        owned = row["owned_files"]
        if not isinstance(owned, list) or len(owned) > MAX_OWNED_FILES or any(
            not _relative(filename) for filename in owned
        ):
            errors.append(prefix + "owned_files must be a bounded list of safe repository-relative paths")
            owned = []
        elif len(set(owned)) != len(owned):
            errors.append(prefix + "duplicate owned path")
        note = row["note"]
        if state == "planned":
            if note is not None or row["owned_files"] != []:
                errors.append(prefix + "planned work must have a null note and empty owned_files")
            continue
        if not isinstance(note, str) or not re.fullmatch(
            rf"{index:02d}-[a-z0-9]+(?:-[a-z0-9]+)*\.md", note
        ) or len(note) > 160:
            errors.append(prefix + "note must be a session-local Markdown filename with matching assignment ID")
            continue
        if note in notes:
            errors.append(prefix + "note was counted more than once")
        notes.add(note)
        expected_path = (DIRECTORY / note).as_posix()
        if expected_path not in owned:
            errors.append(prefix + "owned_files omits the assignment note")
        if state != "complete":
            continue
        try:
            text = _read_text(root, expected_path, MAX_NOTE_BYTES)
            mentioned_agents = re.findall(r"/root/[A-Za-z0-9_/-]+", text)
            if len(text.strip()) < 200 or "\x00" in text or canonical_agent not in mentioned_agents:
                raise ValueError("completed note needs substantive content and its exact canonical worker identity")
        except (OSError, UnicodeError, ValueError) as exc:
            errors.append(prefix + f"completed note is invalid: {exc}")
        for filename in owned:
            try:
                _regular(root, filename, MAX_OWNED_FILE_BYTES)
            except (OSError, ValueError) as exc:
                errors.append(prefix + f"completed owned file is unavailable: {filename}: {exc}")
    for wave in range(1, 11):
        group = rows[(wave - 1) * 6:wave * 6]
        if all(isinstance(row, dict) and row.get("state") == "complete" for row in group):
            completed_waves.append(wave)
    if expected_complete is not None and counts["complete"] != expected_complete:
        errors.append(f"expected {expected_complete} completed assignments, observed {counts['complete']}")
    return finish()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--expected-complete", type=int)
    parser.add_argument("--json", action="store_true", help="emit a machine-readable report")
    args = parser.parse_args()
    result = check(args.repo, args.expected_complete)
    if args.json:
        print(json.dumps(result, sort_keys=True, allow_nan=False))
    else:
        print(f"Calibration retained accounting: {result['status']}; {result['counts']}")
        for error in result["errors"]:
            print(error, file=sys.stderr)
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
