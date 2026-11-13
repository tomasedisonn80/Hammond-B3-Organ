#!/usr/bin/env python3
"""Validate retained records for the standalone session without changing them."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import stat
import sys


SESSION = "2026-11-13-next-phases"
SESSION_PATH = Path("docs/development") / SESSION
BASELINE = "ba0d9c9c75bd7a39152470f9f7ddb82287cb01b1"
SOURCE_PATH = "Hammond_B3_Leslie_Research_Atlas_500pp.pdf"
SOURCE_SHA256 = "4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769"
STATES = ("running", "completed", "blocked")
AGENT = re.compile(r"/root/w([0-9]{2})_a([0-9]{2})_[a-z0-9]+(?:_[a-z0-9]+)*\Z")
AGENT_TOKEN = re.compile(r"(?<![\w/])/root/[A-Za-z0-9_/-]+")
REPORT_NAME = re.compile(r"([0-9]{2})-[a-z0-9]+(?:-[a-z0-9]+)*\.md\Z")
# Reference coverage declared in this session's six retained reading reports.
# This table and the checker do not constitute another reading of the PDF.
ATLAS_RANGES = ((1, 84), (85, 168), (169, 252), (253, 336), (337, 420), (421, 500))
CLAIM = ("Retained record consistency only; dispatch, substantive acceptance, test "
         "execution, publication and physical fidelity require separate evidence.")


class SessionRecordError(ValueError):
    """An invalid or inconsistent standalone-session record."""


def require(condition, message):
    if not condition:
        raise SessionRecordError(message)


def _safe_path(repo, value):
    """Admit a normalized repository-relative path; reject existing links."""
    require(type(value) is str and 0 < len(value) <= 1024 and
            not any(ord(char) < 32 or ord(char) == 127 for char in value) and
            "\\" not in value and ":" not in value and
            all(part not in ("", ".", "..") for part in value.split("/")),
            "path must be a safe normalized repository-relative path")
    path = repo
    parts = value.split("/")
    for index, part in enumerate(parts):
        path /= part
        try:
            metadata = path.lstat()
        except FileNotFoundError:
            continue  # Running assignments can own files not yet created.
        require(not stat.S_ISLNK(metadata.st_mode) and not
                (getattr(metadata, "st_file_attributes", 0) &
                 getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)),
                f"path must not contain a link: {value}")
        require(index == len(parts) - 1 or stat.S_ISDIR(metadata.st_mode),
                f"path parent must be a directory: {value}")
    return path


def _read_text(path):
    require(stat.S_ISREG(path.stat().st_mode), f"not a regular file: {path.name}")
    with path.open("rb") as source:
        raw = source.read(128 * 1024 + 1)
    require(len(raw) <= 128 * 1024, f"text file exceeds 128 KiB: {path.name}")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    require("\x00" not in text and "\r" not in text,
            f"text file contains NUL or bare CR: {path.name}")
    return text


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON field: {key}")
        result[key] = value
    return result


def _reject_number(value):
    raise SessionRecordError(f"non-integer JSON number: {value}")


def _prose(text):
    """Keep narrative identifiers, excluding fenced examples without fixing headings."""
    lines, fence = [], None
    for line in text.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence):
                fence = None
        elif marker:
            fence = marker[1]
        else:
            lines.append(line)
    return "\n".join(lines)


def check_standalone_session(repo, expected_complete=None):
    """Check only this session and return actual declared counts, never promotions."""
    require(expected_complete is None or
            (type(expected_complete) is int and 0 <= expected_complete <= 60),
            "expected-complete must be an integer from 0 to 60")
    repo = Path(repo).resolve(strict=True)
    require(repo.is_dir(), "repository root must be a directory")
    manifest_path = _safe_path(repo, (SESSION_PATH / "assignments.json").as_posix())
    manifest = json.loads(_read_text(manifest_path), object_pairs_hook=_unique_object,
                          parse_float=_reject_number, parse_constant=_reject_number)
    require(type(manifest) is dict and set(manifest) == {
        "schema_version", "session", "baseline_commit", "requested_assignments",
        "requested_waves", "concurrency_limit", "scope", "assignments"},
        "invalid manifest fields")
    for field, expected in (("schema_version", 1), ("requested_assignments", 60),
                            ("requested_waves", 10), ("concurrency_limit", 3)):
        require(type(manifest[field]) is int and manifest[field] == expected,
                f"{field} must be integer {expected}")
    require(manifest["session"] == SESSION, "manifest names a different session")
    require(manifest["baseline_commit"] == BASELINE, "manifest has a different baseline")
    require(type(manifest["scope"]) is str and 0 < len(manifest["scope"].strip()) <= 1000
            and "\x00" not in manifest["scope"], "scope must be nonempty bounded text")
    records = manifest["assignments"]
    require(type(records) is list and len(records) <= 60,
            "assignments must list at most 60 actually dispatched records")

    counts = dict.fromkeys(STATES, 0)
    waves = [dict.fromkeys(STATES, 0) for _ in range(10)]
    numbers, agents, reports = set(), set(), set()
    retained_atlas_pages = 0
    for record in records:
        require(type(record) is dict and set(record) == {
            "number", "wave", "agent", "status", "report", "owned_files"},
            "invalid assignment fields")
        number = record["number"]
        require(type(number) is int and 1 <= number <= 60,
                "assignment number must be an integer from 1 to 60")
        require(number not in numbers, f"duplicate assignment number: {number}")
        numbers.add(number)
        wave = (number - 1) // 6 + 1
        require(type(record["wave"]) is int and record["wave"] == wave,
                f"assignment {number} must belong to wave {wave}")
        agent = record["agent"]
        match = AGENT.fullmatch(agent) if type(agent) is str and len(agent) <= 256 else None
        require(match is not None, f"assignment {number} needs a canonical agent identity")
        require(agent not in agents, f"duplicate agent identity: {agent}")
        require((int(match[1]), int(match[2])) == (wave, number),
                f"assignment {number} agent names a different wave or number")
        agents.add(agent)
        state = record["status"]
        require(type(state) is str and state in STATES, f"assignment {number} has invalid status")
        counts[state] += 1
        waves[wave - 1][state] += 1

        report = _safe_path(repo, record["report"])
        match = REPORT_NAME.fullmatch(report.name)
        require(report.parent == repo / SESSION_PATH and match is not None and
                int(match[1]) == number,
                f"assignment {number} report must be in this session with matching number")
        require(record["report"] not in reports, "duplicate report path")
        reports.add(record["report"])
        owned = record["owned_files"]
        require(type(owned) is list and 0 < len(owned) <= 256,
                f"assignment {number} needs a bounded nonempty owned_files list")
        seen_paths = set()
        for value in owned:
            _safe_path(repo, value)
            require(value not in seen_paths, f"assignment {number} repeats an owned path")
            seen_paths.add(value)
        require(record["report"] in seen_paths, f"assignment {number} must own its report")
        if state != "completed":
            continue
        require(report.is_file(), f"completed assignment {number} is missing its report")
        prose = _prose(_read_text(report))
        require(agent in AGENT_TOKEN.findall(prose),
                f"completed report {number} must identify its canonical agent")
        if number <= 6:
            first, last = ATLAS_RANGES[number - 1]
            require(re.search(rf"(?<!\d){first}\s*[-–—]\s*{last}(?!\d)", prose),
                    f"atlas report {number} must retain page range {first}-{last}")
            require(SOURCE_SHA256 in re.findall(r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])", prose),
                    f"atlas report {number} must retain the exact source PDF hash")
            retained_atlas_pages += last - first + 1

    source = _safe_path(repo, SOURCE_PATH)
    require(stat.S_ISREG(source.stat().st_mode), "source PDF must be a regular file")
    digest = hashlib.sha256()
    with source.open("rb") as pdf:
        for block in iter(lambda: pdf.read(1024 * 1024), b""):
            digest.update(block)
    require(digest.hexdigest() == SOURCE_SHA256, "source PDF SHA-256 mismatch")
    require(expected_complete is None or counts["completed"] == expected_complete,
            f"expected {expected_complete} completed assignments; found {counts['completed']} "
            f"completed, {counts['running']} running, {counts['blocked']} blocked")
    return {
        "schema_version": 1, "status": "passed", "session": SESSION,
        "baseline_commit": BASELINE, "source_pdf_sha256": SOURCE_SHA256,
        "counts": counts, "dispatched": len(records), "not_dispatched": 60 - len(records),
        "completed_waves": sum(wave["completed"] == 6 for wave in waves),
        "wave_counts": [dict(wave=index + 1, not_dispatched=6 - sum(values.values()), **values)
                        for index, values in enumerate(waves)],
        "retained_atlas_pages": retained_atlas_pages,
        "expected_complete": expected_complete, "claim": CLAIM,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--expected-complete", type=int, metavar="N",
                        help="require exactly N completed records (0-60); use 60 for final closure")
    parser.add_argument("--json", action="store_true", help="print a structured report")
    args = parser.parse_args(argv)
    try:
        result = check_standalone_session(args.repo, args.expected_complete)
    except (ValueError, OSError, UnicodeError, RecursionError) as error:
        result = {"schema_version": 1, "status": "failed", "session": SESSION,
                  "error": str(error)[:1000]}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif result["status"] == "passed":
        counts = result["counts"]
        print(f"PASS {SESSION}: {counts['completed']} completed, {counts['running']} running, "
              f"{counts['blocked']} blocked; {result['dispatched']} distinct dispatched agents; "
              f"{result['not_dispatched']} not dispatched; {result['completed_waves']}/10 completed waves")
        print(CLAIM)
    else:
        print(f"FAIL {SESSION}: {result['error']}", file=sys.stderr)
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
