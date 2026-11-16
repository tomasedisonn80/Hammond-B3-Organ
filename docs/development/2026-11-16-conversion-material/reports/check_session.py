#!/usr/bin/env python3
"""Read-only validation of this continuation's actual worker records.

Run from the repository root with --repo .; progress is the default, while
--strict requires sixty accepted records. --self-test uses only temporary files.
For a reassigned owned path, the later row supplies:
  "handoffs": [{"path": "apps/example.cpp", "from_number": 16,
                "reason": "Previous owner returned; root reassigned the repair."}]
Paths are exact repository-relative paths, not globs. Notes are session-relative
notes/Axx.md and must also appear in owned_paths with their repository prefix.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
import tempfile


SESSION = "2026-11-16-conversion-material"
DIRECTORY = PurePosixPath("docs/development") / SESSION
BASE = "a411268fd498f65c083203137831bf5afed83bd8"
META = {"schema": "b3-session-workers-v1", "base_commit": BASE,
        "session": SESSION, "requested_workers": 60, "wave_count": 10,
        "wave_size": 6, "max_concurrent_workers": 3}
ROW_REQUIRED = {"number", "wave", "agent_id", "task", "owned_paths", "status", "note"}
ROW_OPTIONAL = {"note_sha256", "acceptance", "handoffs"}
LIMITS = (
    "Only retained ledger structure, stated ownership handoffs and accepted note "
    "bytes are checked. This does not attest actual/new external dispatch, "
    "chronology, concurrency, quality, correctness, test execution, publication "
    "or fidelity. The concurrency value is a declared limit, not a measured peak. "
    "Owned paths are scopes, not a verified list of completed deliverables. "
    "The narrative floor detects empty records, not substantive acceptance."
)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON field {key!r}")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f"nonfinite JSON token {value}")


def prose(value, minimum=3):
    if not isinstance(value, str) or value != value.strip():
        return False
    if re.fullmatch(r"(?i)(?:todo|tbd|pending|placeholder|not started|to be determined)[.! ]*", value):
        return False
    return len(re.findall(r"[A-Za-z]+", value)) >= minimum


def normalized_path(value):
    return (isinstance(value, str) and bool(value) and value == value.strip()
            and not PurePosixPath(value).is_absolute()
            and not any(c in value for c in "\\:*?[]\x00\r\n")
            and all(part not in ("", ".", "..") for part in value.split("/")))


def safe_path(root, value):
    if not normalized_path(value):
        raise ValueError("path must be normalized and relative, without glob syntax")
    path = root
    for part in value.split("/"):
        path = path / part
        if path.is_symlink():
            raise ValueError("path and its parents must not be symlinks")
    return path


def read_file(path, limit):
    if not path.is_file():
        raise ValueError("expected a regular file")
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise ValueError(f"file exceeds the {limit}-byte record limit")
    return raw


def narrative_words(value):
    value = re.sub(r"<!--.*?(?:-->|$)", "", value, flags=re.DOTALL)
    result, fence = [], None
    for line in value.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if fence:
            if (marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence)
                    and not line[marker.end():].strip()):
                fence = None
        elif marker:
            fence = marker[1]
        elif not line.lstrip().startswith("#") and not line.startswith(("    ", "\t")):
            result.extend(re.findall(r"[A-Za-z]+(?:['-][A-Za-z]+)*", line.casefold()))
    return result


def overlaps(first, second):
    return first == second or first.startswith(second + "/") or second.startswith(first + "/")


def check(repo, strict=False):
    errors = []
    report = {"schema": "b3-conversion-material-session-check-v1", "session": SESSION,
              "mode": "strict" if strict else "progress", "valid": False,
              "strict_record_closure": False, "scope": "retained-record-consistency-only",
              "external_dispatch_attested": False, "limits": LIMITS, "errors": errors}

    def error(code, at, message):
        errors.append({"code": code, "at": at, "message": message})

    try:
        root = Path(repo).expanduser().resolve(strict=True)
        if not root.is_dir():
            raise ValueError("repository root must be a directory")
        ledger = safe_path(root, str(DIRECTORY / "assignments.json"))
        raw = read_file(ledger, 512 * 1024)
        report["ledger"] = {"path": str(DIRECTORY / "assignments.json"), "bytes": len(raw),
                            "sha256": hashlib.sha256(raw).hexdigest()}
        report["checker_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        data = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object,
                          parse_constant=reject_constant)
    except (OSError, ValueError, UnicodeError, RecursionError) as exc:
        error("input", "ledger", str(exc))
        return report
    if not isinstance(data, dict) or set(data) != set(META) | {"workers"}:
        error("schema", "ledger", "top-level fields must match this session schema exactly")
        return report
    for key, value in META.items():
        if type(data[key]) is not type(value) or data[key] != value:
            error("metadata", key, f"this session requires {value!r}")
    workers = data["workers"]
    if not isinstance(workers, list) or len(workers) > 60:
        error("workers", "workers", "expected zero through sixty actual worker objects")
        return report

    numbers, agents, notes, accepted, verified = set(), set(), set(), set(), set()
    owners, prior_rows = [], {}
    waves = [{"wave": i, "recorded": 0, "accepted": 0, "verified": 0} for i in range(1, 11)]
    previous_number = 0
    for index, row in enumerate(workers):
        at, start_errors = f"workers[{index}]", len(errors)
        if not isinstance(row, dict) or not ROW_REQUIRED <= set(row) or set(row) - ROW_REQUIRED - ROW_OPTIONAL:
            error("worker_schema", at, "required worker fields missing or unknown fields present")
            continue
        number, wave, agent = row["number"], row["wave"], row["agent_id"]
        if type(number) is not int or not 1 <= number <= 60:
            error("number", at, "number must be an integer from one through sixty")
            continue
        if number in numbers:
            error("duplicate_number", at, f"worker A{number:02d} is already recorded")
        if number <= previous_number:
            error("record_order", at, "rows must be in increasing worker-number order")
        previous_number = number
        numbers.add(number)
        expected_wave = (number - 1) // 6 + 1
        if type(wave) is not int or wave != expected_wave:
            error("wave", at, f"A{number:02d} must belong to wave {expected_wave}")
        else:
            waves[wave - 1]["recorded"] += 1
        expected_agent = f"/root/w{expected_wave:02d}_a{number:02d}"
        if agent != expected_agent:
            error("agent_id", at, f"expected distinct worker identity {expected_agent}")
        if isinstance(agent, str):
            if agent in agents:
                error("duplicate_agent", at, "follow-ups and earlier records cannot count as new workers")
            agents.add(agent)
        if not prose(row["task"]):
            error("task", at, "task must contain a non-placeholder description")
        status = row["status"]
        if status not in ("dispatched", "accepted"):
            error("status", at, "only dispatched or accepted actual records are admitted")
        note = row["note"]
        expected_note = f"notes/A{number:02d}.md"
        if note != expected_note:
            error("note_path", at, f"note must be session-relative {expected_note}")
        if isinstance(note, str):
            if note in notes:
                error("duplicate_note", at, "notes cannot be reused for another worker")
            notes.add(note)
        owned = row["owned_paths"]
        if not isinstance(owned, list) or not owned or not all(normalized_path(p) for p in owned):
            error("owned_paths", at, "owned_paths must be nonempty normalized exact repository paths")
            owned = []
        elif len(set(owned)) != len(owned):
            error("duplicate_owned_path", at, "owned_paths contains a duplicate")
        note_relative = str(DIRECTORY / expected_note)
        if note_relative not in owned:
            error("owned_note", at, "the worker must own its exact note path")
        handoffs = row.get("handoffs", [])
        transfers = {}
        if not isinstance(handoffs, list):
            error("handoffs", at, "handoffs must be an array")
            handoffs = []
        for item in handoffs:
            if (not isinstance(item, dict) or set(item) != {"path", "from_number", "reason"}
                    or not normalized_path(item.get("path"))
                    or type(item.get("from_number")) is not int
                    or not 1 <= item["from_number"] < number or not prose(item.get("reason"), 5)):
                error("handoff_schema", at, "handoff needs exact path, earlier from_number and a substantive reason")
                continue
            if item["path"] in transfers:
                error("duplicate_handoff", at, "one transfer per newly owned path is allowed")
            transfers[item["path"]] = item["from_number"]
        used = set()
        for path in owned:
            try:
                safe_path(root, path)
            except (OSError, ValueError) as exc:
                error("owned_path_input", path, str(exc))
            conflicts = [(p, n) for p, n in owners if overlaps(p, path)]
            if conflicts:
                previous = max(n for _, n in conflicts)
                if transfers.get(path) != previous or prior_rows.get(previous) != "accepted":
                    error("ownership_overlap", path,
                          f"requires explicit handoff from already accepted A{previous:02d}")
                else:
                    used.add(path)
            owners.append((path, number))
        for path in set(transfers) - used:
            error("unused_handoff", path, "handoff must name an actually overlapping newly owned path")
        prior_rows[number] = status
        if status == "accepted":
            accepted.add(number)
            waves[expected_wave - 1]["accepted"] += 1
            if not prose(row.get("acceptance"), 6):
                error("acceptance", at, "accepted records require substantive non-placeholder acceptance prose")
            digest = row.get("note_sha256")
            if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
                error("note_hash", at, "note_sha256 must be 64 lowercase hex characters")
            try:
                note_raw = read_file(safe_path(root, note_relative), 256 * 1024)
                words = narrative_words(note_raw.decode("utf-8"))
                if hashlib.sha256(note_raw).hexdigest() != digest:
                    error("note_hash_mismatch", note_relative, "accepted note bytes changed or hash is wrong")
                if len(words) < 40 or len(set(words)) < 20:
                    error("note_substance", note_relative, "requires forty prose words and twenty distinct prose words")
            except (OSError, ValueError, UnicodeError) as exc:
                error("note_input", note_relative, str(exc))
            if len(errors) == start_errors:
                verified.add(number)
                waves[expected_wave - 1]["verified"] += 1
        elif "note_sha256" in row or "acceptance" in row:
            error("premature_acceptance", at, "dispatched records must not carry acceptance/hash fields")

    missing = sorted(set(range(1, 61)) - numbers)
    pending = sorted(numbers - accepted)
    report.update(counts={"records": len(workers), "unique_agents": len(agents),
                          "accepted": len(accepted), "verified_notes": len(verified)},
                  waves=waves, missing_numbers=missing, unaccepted_numbers=pending)
    if strict and (missing or pending or len(verified) != 60):
        error("incomplete", "workers", "strict closure requires all sixty distinct accepted, verified records")
    if strict and any(w["verified"] != 6 for w in waves):
        error("incomplete_waves", "workers", "strict closure requires six verified records in each of ten waves")
    report["valid"] = not errors
    report["strict_record_closure"] = strict and not errors
    return report


def self_test():
    """Exercise admission failures without modifying the selected repository."""
    with tempfile.TemporaryDirectory(prefix="b3-session-check-") as directory:
        root = Path(directory)
        session = root / DIRECTORY
        (session / "notes").mkdir(parents=True)
        text = ("This synthetic note exercises record validation with distinct ordinary words. "
                "The worker inspected source behavior, documented assumptions, recorded evidence, "
                "reviewed limitations, preserved existing interfaces, and supplied specific next "
                "actions for integration. These fixture statements establish neither real dispatch "
                "nor implementation quality or product fidelity.\n")
        rows = []
        for n in range(1, 61):
            note = f"notes/A{n:02d}.md"
            raw = (f"# Synthetic A{n:02d}\n\n" + text).encode()
            (session / note).write_bytes(raw)
            wave = (n - 1) // 6 + 1
            rows.append({"number": n, "wave": wave, "agent_id": f"/root/w{wave:02d}_a{n:02d}",
                         "task": "Synthetic validation fixture worker", "owned_paths": [str(DIRECTORY / note)],
                         "status": "accepted", "note": note, "note_sha256": hashlib.sha256(raw).hexdigest(),
                         "acceptance": "Synthetic note is admitted solely for validator self testing."})
        baseline = {**META, "workers": rows}
        ledger = session / "assignments.json"
        results = []

        def run(name, data, expected, strict=False, raw=None):
            ledger.write_bytes(raw if raw is not None else json.dumps(data).encode())
            report = check(root, strict)
            assert report["valid"] == expected, (name, report)
            results.append(name)

        run("complete_strict", baseline, True, True)
        incomplete = {**META, "workers": [copy.deepcopy(rows[0])]}
        run("partial_progress", incomplete, True)
        run("partial_strict_rejected", incomplete, False, True)
        dispatched = copy.deepcopy(incomplete)
        dispatched["workers"][0].update(status="dispatched")
        dispatched["workers"][0].pop("acceptance")
        dispatched["workers"][0].pop("note_sha256")
        (session / rows[0]["note"]).unlink()
        run("missing_dispatched_note", dispatched, True)
        run("missing_accepted_note", incomplete, False)
        (session / rows[0]["note"]).write_text("# Synthetic A01\n\n" + text)
        mutations = {
            "wrong_base": lambda d: d.update(base_commit="0" * 40),
            "boolean_count": lambda d: d.update(wave_size=True),
            "unknown_field": lambda d: d.update(placeholder="unused"),
            "wrong_wave": lambda d: d["workers"][0].update(wave=2),
            "boolean_number": lambda d: d["workers"][0].update(number=True),
            "duplicate_agent": lambda d: d["workers"][1].update(agent_id=rows[0]["agent_id"]),
            "duplicate_number": lambda d: d["workers"][1].update(number=1),
            "duplicate_note": lambda d: d["workers"][1].update(note=rows[0]["note"]),
            "placeholder_task": lambda d: d["workers"][0].update(task="To be determined"),
            "placeholder_acceptance": lambda d: d["workers"][0].update(acceptance="TODO"),
            "bad_note_hash": lambda d: d["workers"][0].update(note_sha256="0" * 64),
            "escape_note": lambda d: d["workers"][0].update(note="../other/notes/A01.md"),
            "glob_owned_path": lambda d: d["workers"][0]["owned_paths"].append("reports/*"),
            "duplicate_owned_path": lambda d: d["workers"][0]["owned_paths"].append(rows[0]["owned_paths"][0]),
            "unrecorded_overlap": lambda d: [d["workers"][i]["owned_paths"].append("tools/shared.py") for i in (0, 1)],
        }
        for name, mutate in mutations.items():
            data = copy.deepcopy(baseline)
            mutate(data)
            run(name, data, False)
        run("duplicate_json_member", None, False, raw=b'{"schema":1,"schema":2}')
        run("nonfinite_json", None, False, raw=b'{"schema":NaN}')
        run("deep_invalid_json", None, False, raw=b"[" * 2000 + b"]" * 2000)
        transfer = copy.deepcopy(baseline)
        for i in (0, 1):
            transfer["workers"][i]["owned_paths"].append("tools/shared.py")
        transfer["workers"][1]["handoffs"] = [{"path": "tools/shared.py", "from_number": 1,
            "reason": "Previous worker returned; root reassigned this source file."}]
        run("explicit_handoff", transfer, True, True)
        transfer["workers"][0]["status"] = "dispatched"
        transfer["workers"][0].pop("note_sha256")
        transfer["workers"][0].pop("acceptance")
        run("handoff_before_acceptance", transfer, False)
        note_path = session / rows[0]["note"]
        note_path.unlink()
        note_path.symlink_to(session / rows[1]["note"])
        run("symlink_note", baseline, False)
        note_path.unlink()
        note_path.write_text("# Only heading\n\nTODO\n")
        weak = copy.deepcopy(baseline)
        weak["workers"][0]["note_sha256"] = hashlib.sha256(note_path.read_bytes()).hexdigest()
        run("placeholder_note", weak, False)
        return {"valid": True, "checks": len(results), "cases": results,
                "scope": "synthetic-validator-self-tests-only"}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    report = self_test() if args.self_test else check(args.repo, args.strict)
    print(json.dumps(report, indent=2, ensure_ascii=True, allow_nan=False))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
