#!/usr/bin/env python3
"""Read-only accounting for this streaming session; progress is the default.

From the repository root:
  python3 -B docs/development/2026-11-15-streaming-continuation/reports/check_streaming_session.py --repo .
  python3 -B docs/development/2026-11-15-streaming-continuation/reports/check_streaming_session.py --repo . --strict

--session accepts a session directory or assignments.json, relative to --repo
or absolute inside it. Notes remain repository-relative, as in this ledger.
Only dispatched/accepted rows belong to this actual-assignment schema. Planned
slots and follow-ups must not be added as new workers. No note-size ceiling is
imposed: the early reading/contract notes predate later compact-note requests.
The modest narrative floor below detects empty/placeholder evidence, not quality.
This helper belongs to the documentation workflow, outside production inputs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys


SESSION = "2026-11-15-streaming-continuation"
DIRECTORY = PurePosixPath("docs/development") / SESSION
BASE_COMMIT = "4aac394cde4da40906b615573a8779aee2d9a37a"
WORKERS, WAVES, PER_WAVE = 60, 10, 6
MIN_WORDS, MIN_DISTINCT_WORDS = 40, 20
LIMITS = (
    "Checks root's retained ledger and accepted note bytes only; does not prove "
    "actual tool dispatch, chronology/concurrency, substantive review, technical "
    "correctness, test execution, publication, product readiness or fidelity. "
    "Only accepted notes are verified, not every owned deliverable. The narrative "
    "floor is structural and has no maximum note-size rule."
)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON member {key!r}")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f"invalid JSON constant {value}")


def text_present(value):
    return isinstance(value, str) and bool(value.strip())


def relative_path(value):
    return (text_present(value) and value == value.strip()
            and "\\" not in value and ":" not in value
            and not PurePosixPath(value).is_absolute()
            and all(part not in ("", ".", "..") for part in value.split("/")))


def narrative_words(text):
    """Count prose outside comments, headings and fenced/indented code."""
    text = re.sub(r"<!--.*?(?:-->|$)", "", text, flags=re.DOTALL)
    lines, fence = [], None
    for line in text.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if fence:
            if (marker and marker[1][0] == fence[0]
                    and len(marker[1]) >= len(fence)
                    and not line[marker.end():].strip()):
                fence = None
        elif marker:
            fence = marker[1]
        elif not line.lstrip().startswith("#") and not line.startswith(("    ", "\t")):
            lines.append(line)
    return re.findall(r"[A-Za-z]+(?:['-][A-Za-z]+)*", "\n".join(lines).casefold())


def check(repo, session, strict=False):
    errors = []
    report = {
        "schema": "b3-streaming-session-check-v1", "session": SESSION,
        "mode": "strict" if strict else "progress", "valid": False,
        "strict_record_closure": False,
        "scope": "retained-ledger-and-note-consistency-only",
        "external_dispatch_attested": False,
        "requirements": {"workers": WORKERS, "waves": WAVES, "per_wave": PER_WAVE},
        "narrative_floor": {"words": MIN_WORDS, "distinct_words": MIN_DISTINCT_WORDS},
        "limits": LIMITS, "errors": errors,
    }

    def error(code, at, message):
        errors.append({"code": code, "at": at, "message": message})

    try:
        repo = Path(repo).expanduser().resolve(strict=True)
        if not repo.is_dir():
            raise ValueError("--repo must be a directory")
        selected = Path(session).expanduser()
        selected = selected if selected.is_absolute() else repo / selected
        ledger = selected if selected.name == "assignments.json" else selected / "assignments.json"
        ledger = ledger.resolve(strict=True)
        ledger_relative = ledger.relative_to(repo).as_posix()
        raw = ledger.read_bytes()
        report["ledger"] = {"path": ledger_relative, "sha256": hashlib.sha256(raw).hexdigest(),
                            "bytes": len(raw)}
        report["checker_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        data = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object,
                          parse_constant=reject_constant)
    except (OSError, ValueError, UnicodeError) as exc:
        error("input", "ledger", str(exc))
        return report

    if not isinstance(data, dict):
        error("schema", "ledger", "ledger must be a JSON object")
        return report
    expected = {"schema_version": 1, "session": SESSION, "base_commit": BASE_COMMIT,
                "requested_workers": WORKERS, "requested_waves": WAVES,
                "workers_per_wave": PER_WAVE}
    for key, value in expected.items():
        if type(data.get(key)) is not type(value) or data.get(key) != value:
            error("metadata", key, f"this session requires {value!r}")
    assignments = data.get("assignments")
    if not isinstance(assignments, list):
        error("schema", "assignments", "assignments must be a list")
    if errors:
        return report

    numbers, agents, accepted, verified = set(), set(), set(), set()
    per_wave = [{"wave": wave, "recorded": 0, "accepted": 0, "verified": 0}
                for wave in range(1, WAVES + 1)]
    if len(assignments) > WORKERS:
        error("too_many_records", "assignments", "only sixty actual assignments are allowed")

    for index, row in enumerate(assignments):
        at = f"assignments[{index}]"
        start_errors = len(errors)
        if not isinstance(row, dict):
            error("schema", at, "assignment must be an object")
            continue
        number, wave, agent = row.get("number"), row.get("wave"), row.get("agent")
        if type(number) is not int or not 1 <= number <= WORKERS:
            error("number", at, "number must be an integer from 1 through 60")
            continue
        expected_wave = (number - 1) // PER_WAVE + 1
        if number in numbers:
            error("duplicate_number", at, f"A{number:02d} is already recorded")
        numbers.add(number)
        if type(wave) is not int or wave != expected_wave:
            error("wrong_wave", at, f"A{number:02d} belongs to wave {expected_wave}")
        else:
            per_wave[wave - 1]["recorded"] += 1
        expected_agent = f"/root/w{expected_wave:02d}_a{number:02d}"
        if not text_present(agent) or agent != expected_agent:
            error("agent_identity", at, f"actual identity must be {expected_agent}")
        if isinstance(agent, str):
            if agent in agents:
                error("duplicate_agent", at, f"{agent} is already recorded; a follow-up is not a new worker")
            agents.add(agent)
        if not text_present(row.get("task")):
            error("task", at, "task must be nonempty text")
        status = row.get("status")
        if status not in ("dispatched", "accepted"):
            error("status", at, "actual records require status 'dispatched' or 'accepted'; planned slots do not count")

        owned = row.get("owned_paths")
        note_reference = None
        if not isinstance(owned, list) or not owned or not all(relative_path(p) for p in owned):
            error("owned_paths", at, "owned_paths must contain normalized repository-relative paths")
        else:
            if len(set(owned)) != len(owned):
                error("owned_paths", at, "owned_paths contains a duplicate")
            note_directory = (DIRECTORY / "notes").as_posix()
            notes = [p for p in owned if p.startswith(note_directory + "/")]
            pattern = rf"A{number:02d}(?:-[a-z0-9]+(?:[-_][a-z0-9]+)*)?\.md"
            if len(notes) != 1 or not re.fullmatch(pattern, notes[0][len(note_directory) + 1:]):
                error("owned_note", at, f"own exactly one {note_directory}/A{number:02d}[-suffix].md note")
            else:
                note_reference = notes[0]

        if status != "accepted":
            continue
        accepted.add(number)
        if type(wave) is int and wave == expected_wave:
            per_wave[wave - 1]["accepted"] += 1
        if not text_present(row.get("acceptance")):
            error("acceptance", at, "accepted records require nonempty acceptance text")
        expected_hash = row.get("note_sha256")
        if not isinstance(expected_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
            error("note_hash", at, "accepted note_sha256 must be 64 lowercase hexadecimal characters")
        if note_reference is not None:
            try:
                note = repo / note_reference
                # A current-session pathname cannot redirect to an older session.
                if note.resolve(strict=True) != note.absolute():
                    raise ValueError("owned note must be a direct file in this session, without symlink redirection")
                if not note.is_file():
                    raise ValueError("owned note must be a regular file")
                note_raw = note.read_bytes()
                note_text = note_raw.decode("utf-8")
            except (OSError, ValueError, UnicodeError) as exc:
                error("note_input", note_reference, str(exc))
            else:
                if hashlib.sha256(note_raw).hexdigest() != expected_hash:
                    error("note_hash_mismatch", note_reference, "current note bytes do not match accepted note_sha256")
                words = narrative_words(note_text)
                if len(words) < MIN_WORDS or len(set(words)) < MIN_DISTINCT_WORDS:
                    error("note_substance", note_reference,
                          f"note requires at least {MIN_WORDS} prose words and {MIN_DISTINCT_WORDS} distinct prose words")
        if len(errors) == start_errors:
            verified.add(number)
            per_wave[expected_wave - 1]["verified"] += 1

    missing = sorted(set(range(1, WORKERS + 1)) - numbers)
    pending = sorted(numbers - accepted)
    report.update({
        "counts": {"records": len(assignments), "unique_numbers": len(numbers),
                   "unique_agents": len(agents), "accepted_numbers": len(accepted),
                   "verified_accepted_notes": len(verified)},
        "waves": per_wave, "missing_numbers": missing, "unaccepted_numbers": pending,
    })
    if strict:
        if missing:
            error("incomplete_numbers", "assignments", f"strict closure is missing numbers {missing}")
        if pending:
            error("unaccepted_numbers", "assignments", f"strict closure requires accepted status for {pending}")
        incomplete = [w["wave"] for w in per_wave if w["verified"] != PER_WAVE]
        if incomplete:
            error("incomplete_waves", "assignments",
                  f"strict closure requires six verified accepted notes in every wave; incomplete waves {incomplete}")
    report["valid"] = not errors
    report["strict_record_closure"] = strict and not errors
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", default=".", help="repository root (default: current directory)")
    parser.add_argument("--session", default=str(DIRECTORY),
                        help="session directory or assignments.json, relative to --repo or absolute inside it")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--strict", action="store_true", help="require all sixty accepted records and ten complete waves")
    mode.add_argument("--progress", action="store_true", help="check consistency without closure (default)")
    args = parser.parse_args()
    report = check(args.repo, args.session, strict=args.strict)
    print(json.dumps(report, separators=(",", ":"), ensure_ascii=True))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
