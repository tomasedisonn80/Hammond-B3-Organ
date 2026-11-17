#!/usr/bin/env python3
"""Read-only record validation; this does not prove dispatch or product quality."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path, PurePosixPath
import re


SESSION = "2026-11-16-heading-title-continuation"
BASE = "113c29b7b14c8fde0859bc405ef8e4141a131ea6"
PDF_SHA256 = "4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769"
ROOT_KEYS = {"session", "base_commit", "requested_workers", "waves",
             "maximum_concurrent_workers", "workers"}
WORKER_KEYS = {"id", "wave", "agent", "task", "owned_paths", "status", "dispatched_at"}
ACCEPTED_KEYS = {"accepted_at", "note", "note_sha256", "root_review"}
COVERAGE_KEYS = {"pdf_sha256", "pages", "coverage", "scope"}
READING_KEYS = {"worker", "agent", "first", "last", "extract_sha256", "note_sha256"}
MIN_NOTE_BYTES = 301
MAX_RECORD_BYTES = 2 * 1024 * 1024


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON member {key!r}")
        result[key] = value
    return result


def invalid_constant(value: str) -> None:
    raise ValueError(f"nonfinite JSON number {value}")


def read_json(path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"expected a regular JSON file: {path.name}")
    if path.stat().st_size > MAX_RECORD_BYTES:
        raise ValueError(f"JSON record exceeds {MAX_RECORD_BYTES} bytes: {path.name}")
    result = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object,
                        parse_constant=invalid_constant)
    if not isinstance(result, dict):
        raise ValueError(f"expected a JSON object: {path.name}")
    return result


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def digest_string(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def relative_path(value: object) -> bool:
    if not nonempty(value) or "\\" in value or "\x00" in value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and all(part not in {"", ".", ".."}
                                        for part in value.split("/"))


def validate(session: Path, strict: bool) -> dict:
    errors: list[str] = []
    by_id: dict[str, dict] = {}
    assigned: Counter[int] = Counter()
    accepted: Counter[int] = Counter()
    agents: set[str] = set()
    note_hashes: dict[str, str] = {}

    def check(condition: bool, message: str) -> bool:
        if not condition:
            errors.append(message)
        return condition

    def keys(value: dict, expected: set[str], label: str) -> None:
        if set(value) != expected:
            errors.append(f"{label}: missing keys {sorted(expected - set(value))}; "
                          f"unexpected keys {sorted(set(value) - expected)}")

    def timestamp(value: object, label: str) -> datetime | None:
        try:
            if not isinstance(value, str):
                raise ValueError("not a string")
            parsed = datetime.fromisoformat(value)
            if parsed.utcoffset() is None:
                raise ValueError("timezone missing")
            return parsed
        except (TypeError, ValueError):
            errors.append(f"{label}: expected an ISO-8601 timestamp with timezone")
            return None

    def note_hash(worker: str) -> str | None:
        if worker in note_hashes:
            return note_hashes[worker]
        path = session / "notes" / f"{worker}.md"
        try:
            if not check(path.resolve().is_relative_to(session), f"{worker}: note escapes session"):
                return None
            if not check(path.is_file() and not path.is_symlink(),
                         f"{worker}: missing regular note"):
                return None
            if not check(path.stat().st_size <= MAX_RECORD_BYTES,
                         f"{worker}: note exceeds {MAX_RECORD_BYTES} bytes"):
                return None
            data = path.read_bytes()
            check(len(data) >= MIN_NOTE_BYTES, f"{worker}: note is not substantive in size")
            check(bool(data.decode("utf-8").strip()), f"{worker}: empty note")
            result = hashlib.sha256(data).hexdigest()
            note_hashes[worker] = result
            return result
        except (OSError, UnicodeError) as error:
            errors.append(f"{worker}: cannot inspect note: {error}")
            return None

    try:
        ledger = read_json(session / "assignments.json")
        keys(ledger, ROOT_KEYS, "ledger")
        for key, expected in (("session", SESSION), ("base_commit", BASE),
                              ("requested_workers", 60), ("waves", 10),
                              ("maximum_concurrent_workers", 3)):
            value = ledger.get(key)
            check(type(value) is type(expected) and value == expected,
                  f"ledger.{key}: expected {expected!r}")
        rows = ledger.get("workers")
        if not check(isinstance(rows, list), "ledger.workers: expected an array"):
            rows = []
        check(len(rows) <= 60, "ledger.workers: more than sixty records")
        for index, row in enumerate(rows):
            label = f"worker record {index + 1}"
            if not check(isinstance(row, dict), f"{label}: expected an object"):
                continue
            worker = row.get("id")
            if not check(isinstance(worker, str) and
                         re.fullmatch(r"A(?:0[1-9]|[1-5][0-9]|60)", worker) is not None,
                         f"{label}: id must be A01 through A60"):
                continue
            label = worker
            if not check(worker not in by_id, f"{worker}: duplicate worker id"):
                continue
            by_id[worker] = row
            number = int(worker[1:])
            wave = (number - 1) // 6 + 1
            assigned[wave] += 1
            check(type(row.get("wave")) is int and row["wave"] == wave,
                  f"{worker}: wave must be {wave}")
            state = row.get("status")
            check(state in {"dispatched", "accepted"} if isinstance(state, str) else False,
                  f"{worker}: status must be dispatched or accepted")
            keys(row, WORKER_KEYS | (ACCEPTED_KEYS if state == "accepted" else set()), label)
            agent = row.get("agent")
            expected_agent = f"/root/w{wave:02}_a{number:02}"
            check(agent == expected_agent, f"{worker}: agent must be {expected_agent}")
            if isinstance(agent, str):
                check(agent not in agents, f"{worker}: duplicate agent identity")
                agents.add(agent)
            check(nonempty(row.get("task")), f"{worker}: task is missing")
            owned = row.get("owned_paths")
            if check(isinstance(owned, list) and bool(owned),
                     f"{worker}: owned_paths must be a nonempty array"):
                check(all(relative_path(path) for path in owned),
                      f"{worker}: ownership paths must be safe relative paths")
                if all(isinstance(path, str) for path in owned):
                    check(len(set(owned)) == len(owned), f"{worker}: duplicate ownership path")
                check(f"notes/{worker}.md" in owned, f"{worker}: own note is not assigned")
            dispatched = timestamp(row.get("dispatched_at"), f"{worker}.dispatched_at")
            if state == "accepted":
                accepted[wave] += 1
                finished = timestamp(row.get("accepted_at"), f"{worker}.accepted_at")
                if dispatched is not None and finished is not None:
                    check(finished >= dispatched, f"{worker}: acceptance precedes dispatch record")
                check(row.get("note") == f"notes/{worker}.md", f"{worker}: unexpected note path")
                check(nonempty(row.get("root_review")), f"{worker}: root review is missing")
                expected = row.get("note_sha256")
                check(digest_string(expected), f"{worker}: invalid note SHA-256")
                actual = note_hash(worker)
                if actual is not None:
                    check(actual == expected, f"{worker}: accepted note SHA-256 differs")
        for wave, count in assigned.items():
            check(count <= 6, f"wave {wave}: more than six workers")
    except (OSError, UnicodeError, ValueError, RecursionError) as error:
        errors.append(f"ledger: {error}")

    coverage_ok = False
    try:
        receipt = read_json(session / "reports" / "atlas-reading-coverage.json")
        prior_errors = len(errors)
        keys(receipt, COVERAGE_KEYS, "atlas receipt")
        check(type(receipt.get("pages")) is int and receipt["pages"] == 500,
              "atlas receipt: expected exactly 500 pages")
        check(nonempty(receipt.get("scope")), "atlas receipt: scope is missing")
        check(receipt.get("pdf_sha256") == PDF_SHA256, "atlas receipt: unexpected PDF identity")
        pdf = session.parents[2] / "Hammond_B3_Leslie_Research_Atlas_500pp.pdf"
        if check(pdf.is_file() and not pdf.is_symlink(), "atlas: missing regular source PDF"):
            check(file_sha256(pdf) == PDF_SHA256, "atlas: source PDF SHA-256 differs")
        coverage = receipt.get("coverage")
        if not check(isinstance(coverage, list), "atlas coverage: expected an array"):
            coverage = []
        check(len(coverage) == 6, "atlas coverage: expected six reading records")
        seen_readers: set[str] = set()
        pages: list[int] = []
        for index, reading in enumerate(coverage):
            if not check(isinstance(reading, dict), f"atlas reading {index + 1}: expected an object"):
                continue
            keys(reading, READING_KEYS, f"atlas reading {index + 1}")
            worker = reading.get("worker")
            if not check(isinstance(worker, str) and worker in {f"A{n:02}" for n in range(1, 7)},
                         f"atlas reading {index + 1}: expected A01 through A06"):
                continue
            check(worker not in seen_readers, f"atlas: duplicate reader {worker}")
            seen_readers.add(worker)
            number = int(worker[1:])
            first, last = (number - 1) * 84 + 1, min(number * 84, 500)
            for key, expected in (("first", first), ("last", last)):
                check(type(reading.get(key)) is int and reading[key] == expected,
                      f"atlas {worker}: {key} must be {expected}")
            if type(reading.get("first")) is int and type(reading.get("last")) is int:
                if check(1 <= reading["first"] <= reading["last"] <= 500,
                         f"atlas {worker}: invalid page range"):
                    pages.extend(range(reading["first"], reading["last"] + 1))
            row = by_id.get(worker, {})
            check(row.get("status") == "accepted", f"atlas {worker}: reading worker is not accepted")
            check(reading.get("agent") == row.get("agent") == f"/root/w01_a{number:02}",
                  f"atlas {worker}: agent identity differs")
            check(digest_string(reading.get("extract_sha256")), f"atlas {worker}: invalid extract digest")
            expected = reading.get("note_sha256")
            check(digest_string(expected), f"atlas {worker}: invalid note digest")
            check(expected == row.get("note_sha256"), f"atlas {worker}: ledger note digest differs")
            actual = note_hash(worker)
            if actual is not None:
                check(actual == expected, f"atlas {worker}: retained note digest differs")
        check(sorted(pages) == list(range(1, 501)), "atlas coverage: gaps, overlaps or missing pages")
        coverage_ok = len(errors) == prior_errors
    except (OSError, UnicodeError, ValueError, RecursionError) as error:
        errors.append(f"atlas: {error}")

    if strict:
        check(set(by_id) == {f"A{n:02}" for n in range(1, 61)},
              "strict closure requires all sixty distinct worker records")
        check(sum(accepted.values()) == 60, "strict closure requires sixty accepted notes")
        for wave in range(1, 11):
            check(assigned[wave] == accepted[wave] == 6,
                  f"strict closure requires six accepted workers in wave {wave}")
    return {
        "schema_version": 1, "session": SESSION, "strict": strict,
        "status": "pass" if not errors else "fail", "workers_recorded": len(by_id),
        "workers_accepted": sum(accepted.values()),
        "pending_workers": sorted(worker for worker, row in by_id.items()
                                  if row.get("status") != "accepted"),
        "waves": [{"wave": wave, "recorded": assigned[wave], "accepted": accepted[wave]}
                  for wave in range(1, 11)],
        "atlas_record_verified": coverage_ok, "errors": errors,
        "scope": "Record consistency only. Does not prove external dispatch, actual concurrency, "
                 "reading, product quality, fidelity, CI or publication. Extract hashes are checked "
                 "for format; transient extracted text is not required in a future checkout.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="require sixty accepted workers in ten complete waves")
    args = parser.parse_args()
    report = validate(Path(__file__).resolve().parent, args.strict)
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
