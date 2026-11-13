#!/usr/bin/env python3
"""Check retained rotary-session accounting, not external dispatch or fidelity."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path, PurePosixPath
import re
import sys

SESSION = "2026-11-13-rotary"
DIRECTORY = Path("docs/development") / SESSION
MAX_MANIFEST_BYTES = 256 * 1024
MAX_NOTE_BYTES = 128 * 1024


def _object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def _integer(value: object) -> bool:
    return type(value) is int


def _relative(value: object) -> bool:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and all(p not in ("", ".", "..") for p in value.split("/"))


def check(repo: Path, expected_complete: int | None = None) -> dict[str, object]:
    errors: list[str] = []
    counts: Counter[str] = Counter()
    identities: set[str] = set()
    notes: set[str] = set()
    completed_waves: list[int] = []
    root = repo.resolve()
    path = root / DIRECTORY / "assignments.json"
    report: dict[str, object] = {
        "session_id": SESSION,
        "scope": "retained_accounting_consistency_only",
        "external_dispatch_attested": False,
        "physical_fidelity": "not_established",
        "expected_complete": expected_complete,
        "errors": errors,
    }

    def finish() -> dict[str, object]:
        report.update(
            status="failed" if errors else "passed",
            counts={state: counts[state] for state in ("planned", "running", "complete")},
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
        if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_MANIFEST_BYTES:
            raise ValueError("manifest must be a bounded regular file")
        if not path.resolve().is_relative_to(root):
            raise ValueError("manifest leaves the repository")
        manifest = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_object)
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        errors.append(f"cannot read manifest: {exc}")
        return finish()
    fields = {"schema_version", "session_id", "baseline_commit", "requested_agents",
              "requested_waves", "concurrency", "assignments"}
    if not isinstance(manifest, dict) or set(manifest) != fields:
        errors.append("manifest members must match the rotary session schema")
        return finish()
    for key, expected in (("schema_version", 1), ("requested_agents", 60), ("requested_waves", 10)):
        if not _integer(manifest[key]) or manifest[key] != expected:
            errors.append(f"{key} must be integer {expected}")
    if manifest["session_id"] != SESSION:
        errors.append("wrong session identity")
    if not isinstance(manifest["baseline_commit"], str) or not re.fullmatch(r"[0-9a-f]{40}", manifest["baseline_commit"]):
        errors.append("baseline_commit must identify an actual full Git commit")
    if not _integer(manifest["concurrency"]) or manifest["concurrency"] != 3:
        errors.append("this session records three concurrent worker slots")
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
        if not _integer(row["assignment"]) or row["assignment"] != index:
            errors.append(prefix + "identity/order mismatch")
        if not _integer(row["wave"]) or row["wave"] != (index - 1) // 6 + 1:
            errors.append(prefix + "wave must contain its six ordered assignments")
        state = row["state"]
        if not isinstance(state, str) or state not in ("planned", "running", "complete"):
            errors.append(prefix + "invalid state")
            continue
        counts[state] += 1
        agent = row["agent"]
        if state == "planned":
            if agent is not None:
                errors.append(prefix + "planned work cannot claim a dispatched identity")
        elif not isinstance(agent, str) or not re.fullmatch(r"/root/[a-z0-9_]+", agent):
            errors.append(prefix + "actual work needs its canonical worker identity")
        elif agent in identities:
            errors.append(prefix + "worker identity was counted more than once")
        else:
            identities.add(agent)
        if not isinstance(row["scope"], str) or not row["scope"].strip():
            errors.append(prefix + "scope is missing")
        owned = row["owned_files"]
        if not isinstance(owned, list) or any(not _relative(p) for p in owned):
            errors.append(prefix + "owned_files must contain repository-relative paths")
            owned = []
        elif len(set(owned)) != len(owned):
            errors.append(prefix + "duplicate owned path")
        note = row["note"]
        if state == "planned" and note is None:
            continue
        if not _relative(note) or "/" in str(note) or not str(note).endswith(".md"):
            errors.append(prefix + "note must be one Markdown filename in this session")
            continue
        if note in notes:
            errors.append(prefix + "note was counted more than once")
        notes.add(note)
        expected_path = (DIRECTORY / str(note)).as_posix()
        if expected_path not in owned:
            errors.append(prefix + "owned_files omits the assignment note")
        if state != "complete":
            continue
        note_path = root / expected_path
        try:
            if note_path.is_symlink() or not note_path.is_file() or note_path.stat().st_size > MAX_NOTE_BYTES:
                raise ValueError("completed note must be a bounded regular file")
            if not note_path.resolve().is_relative_to(root):
                raise ValueError("completed note leaves the repository")
            text = note_path.read_text(encoding="utf-8")
            if len(text.strip()) < 200 or not isinstance(agent, str) or agent not in text:
                raise ValueError("completed note needs substantive content and its actual worker identity")
            for filename in owned:
                candidate = root / filename
                if not candidate.is_file() or not candidate.resolve().is_relative_to(root):
                    errors.append(prefix + f"completed owned file is unavailable: {filename}")
        except (OSError, UnicodeError, ValueError) as exc:
            errors.append(prefix + str(exc))
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
        print(f"Rotary retained accounting: {result['status']}; {result['counts']}")
        for error in result["errors"]:
            print(error, file=sys.stderr)
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
