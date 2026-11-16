#!/usr/bin/env python3
"""Read-only consistency check for the 2026-11-16 runtime worker ledger.

Progress: python3 -B docs/development/2026-11-16-runtime-continuation/reports/check_session.py --repo .
Closure: add --strict to require A01--A60 accepted in ten waves of six.
Adversarial fixtures: --self-test (writes only inside a temporary directory).

Only this session's assignments.json supplies worker credit. A running record
does not need a finished note. Accepted records need the canonical current-session
note, its exact SHA-256 and acceptance prose. Other retained session notes are
read only to reject identical-byte reuse; their workers never enter the counts.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import stat
import sys
import tempfile


SESSION = "2026-11-16-runtime-continuation"
DIRECTORY = f"docs/development/{SESSION}"
LEDGER = f"{DIRECTORY}/assignments.json"
META = {
    "schema_version": 1,
    "base_commit": "3520c96adcdcf4ce4bcb860082354bf0050a89c3",
    "requested_workers": 60,
    "waves": 10,
    "max_concurrent_workers": 3,
}
REQUIRED = {"id", "wave", "agent", "status", "task", "owned_paths"}
ACCEPTED = {"note", "note_sha256", "acceptance"}
IDS = {f"A{number:02d}" for number in range(1, 61)}
LIMIT = 512 * 1024
LIMITS = (
    "Retained-record consistency only: this checker does not attest actual or new "
    "external dispatch, chronology, measured concurrency, ownership handoffs, "
    "substantive quality, correctness, test execution, publication or fidelity. "
    "Canonical agent names are session-local records, not global identity proof. "
    "Owned paths are declared scopes, not verified completed deliverables. "
    "Prose floors reject empty/placeholder records but cannot grade the work. "
    "Other-session comparison detects exact note-byte reuse only; edited copies "
    "and fabricated claims require independent review. Files are read without "
    "locking; run again after the integrator finishes changing records."
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


def prose(value, minimum):
    if not isinstance(value, str) or value != value.strip():
        return False
    words = re.findall(r"[A-Za-z]+", value.casefold())
    placeholders = {"todo", "tbd", "pending", "placeholder", "none", "na", "ok",
                    "done", "accepted", "pass", "passed", "complete", "completed",
                    "not", "started", "to", "be", "determined"}
    return len(words) >= minimum and bool(set(words) - placeholders)


def safe_path(root, value):
    """Admit exact portable relative paths, without lexical or symlink aliases."""
    if (not isinstance(value, str) or not value or value != value.strip()
            or any(c in value for c in '\\:*?[]<>"|')
            or any(ord(c) < 32 or ord(c) == 127 for c in value)):
        raise ValueError("expected an exact repository-relative path without glob/control syntax")
    parts = value.split("/")
    if any(part in ("", ".", "..") or part != part.strip() or part.endswith(".")
           or re.fullmatch(r"(?i)(?:con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?", part)
           for part in parts):
        raise ValueError("absolute, traversal, empty-component and platform-alias paths are forbidden")
    path = root
    for part in parts:
        path /= part
        try:
            mode = path.lstat().st_mode
        except FileNotFoundError:
            continue  # An owned scope may name a not-yet-created deliverable.
        if stat.S_ISLNK(mode):
            raise ValueError("path and every parent must be free of symlink aliases")
    return path


def read_regular(path):
    if not stat.S_ISREG(path.lstat().st_mode):
        raise ValueError("expected a regular file")
    with path.open("rb") as stream:
        raw = stream.read(LIMIT + 1)
    if len(raw) > LIMIT:
        raise ValueError(f"record exceeds {LIMIT} bytes")
    return raw


def narrative_words(value):
    """Exclude headings, comments and code blocks from a modest prose floor."""
    value = re.sub(r"<!--.*?(?:-->|$)", "", value, flags=re.DOTALL)
    words, fence = [], None
    for line in value.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if fence:
            if (marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence)
                    and not line[marker.end():].strip()):
                fence = None
        elif marker:
            fence = marker[1]
        elif not line.lstrip().startswith("#") and not line.startswith(("    ", "\t")):
            words.extend(re.findall(r"[A-Za-z]+(?:['-][A-Za-z]+)*", line.casefold()))
    return words


def check(repo, strict=False):
    errors = []
    waves = [{"wave": wave, "recorded": 0, "accepted": 0, "verified": 0}
             for wave in range(1, 11)]
    report = {
        "schema": "b3-runtime-session-check-v1", "session": SESSION,
        "mode": "strict" if strict else "progress", "valid": False,
        "strict_record_closure": False, "scope": "retained-record-consistency-only",
        "external_dispatch_attested": False, "limits": LIMITS, "errors": errors,
        "counts": {"records": 0, "unique_ids": 0, "unique_canonical_agents": 0,
                   "accepted": 0, "running": 0, "verified_accepted_notes": 0},
        "waves": waves, "other_session_notes_compared": 0,
    }

    def error(code, at, message):
        errors.append({"code": code, "at": at, "message": message})

    try:
        root = Path(repo).expanduser().resolve(strict=True)
        if not root.is_dir():
            raise ValueError("repository root must be a directory")
        raw = read_regular(safe_path(root, LEDGER))
        report["ledger"] = {"path": LEDGER, "bytes": len(raw),
                            "sha256": hashlib.sha256(raw).hexdigest()}
        report["checker_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        data = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object,
                          parse_constant=reject_constant)
    except (OSError, ValueError, UnicodeError, RecursionError) as exc:
        error("input", "ledger", str(exc))
        return report
    if not isinstance(data, dict) or set(data) != set(META) | {"assignments"}:
        error("schema", "ledger", "top-level fields must match this session's schema exactly")
        return report
    for field, expected in META.items():
        if type(data[field]) is not type(expected) or data[field] != expected:
            error("metadata", field, f"this session requires {expected!r}")
    rows = data["assignments"]
    if not isinstance(rows, list):
        error("assignments", "assignments", "expected an array of actual worker records")
        return report
    report["counts"]["records"] = len(rows)
    if len(rows) > 60:
        error("assignments", "assignments", "at most sixty records are allowed")
        return report

    # These notes supply negative reuse checks only, never positive worker credit.
    historical_hashes = {}
    try:
        for path in sorted((root / "docs/development").glob("*/notes/*.md")):
            relative = path.relative_to(root).as_posix()
            if relative.startswith(DIRECTORY + "/"):
                continue
            old_raw = read_regular(safe_path(root, relative))
            historical_hashes.setdefault(hashlib.sha256(old_raw).hexdigest(), relative)
            report["other_session_notes_compared"] += 1
    except (OSError, ValueError) as exc:
        error("history_input", "other session notes", str(exc))

    ids, agents, canonical_agents, accepted, running, verified = set(), set(), set(), set(), set(), set()
    note_hashes, note_inodes, path_inodes = {}, {}, {}
    for index, row in enumerate(rows):
        at, before = f"assignments[{index}]", len(errors)
        if not isinstance(row, dict) or not REQUIRED <= set(row):
            error("worker_schema", at, "worker must be an object with every required field")
            continue
        if set(row) - REQUIRED - ACCEPTED:
            error("worker_schema", at, "unknown worker fields are not part of this session schema")
        worker = row["id"]
        if not isinstance(worker, str) or worker not in IDS:
            error("id", at, "id must be exactly A01 through A60")
            continue
        number = int(worker[1:])
        wave = (number - 1) // 6 + 1
        if worker in ids:
            error("duplicate_id", at, f"{worker} is already recorded")
        else:
            waves[wave - 1]["recorded"] += 1
        ids.add(worker)
        if type(row["wave"]) is not int or row["wave"] != wave:
            error("wave", at, f"{worker} belongs to wave {wave}")
        agent, expected_agent = row["agent"], f"/root/w{wave:02d}_a{number:02d}"
        if not isinstance(agent, str) or agent != expected_agent:
            error("agent", at, f"expected canonical worker identity {expected_agent}")
        else:
            canonical_agents.add(agent)
        if isinstance(agent, str):
            if agent in agents:
                error("duplicate_agent", at, "one recorded worker identity cannot supply two workers")
            agents.add(agent)
        if not prose(row["task"], 3):
            error("task", at, "task requires at least three non-placeholder description words")
        status = row["status"]
        if status not in ("running", "accepted"):
            error("status", at, "only actually running or accepted records are allowed")
        expected_note = f"{DIRECTORY}/notes/{worker}.md"
        owned = row["owned_paths"]
        if not isinstance(owned, list) or not owned:
            error("owned_paths", at, "owned_paths must be a nonempty array")
            owned = []
        seen_paths = set()
        for item in owned:
            try:
                path = safe_path(root, item)
                if item in seen_paths:
                    error("duplicate_owned_path", at, f"repeated owned path {item}")
                seen_paths.add(item)
                if path.exists():
                    info = path.stat()
                    inode = (info.st_dev, info.st_ino)
                    if inode in path_inodes and path_inodes[inode] != item:
                        error("owned_path_alias", at, f"{item} aliases {path_inodes[inode]}")
                    path_inodes[inode] = item
            except (OSError, ValueError) as exc:
                error("owned_path", at, str(exc))
        if expected_note not in seen_paths:
            error("owned_note", at, f"worker must own its exact note path {expected_note}")

        if status == "running":
            running.add(worker)
            if set(row) & ACCEPTED:
                error("premature_acceptance", at, "running records must omit note/hash/acceptance fields")
        elif status == "accepted":
            if worker not in accepted:
                waves[wave - 1]["accepted"] += 1
            accepted.add(worker)
            if row.get("note") != expected_note:
                error("note_path", at, f"accepted note must be exactly {expected_note}")
            if not prose(row.get("acceptance"), 6):
                error("acceptance", at, "acceptance requires at least six non-placeholder description words")
            digest = row.get("note_sha256")
            if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
                error("note_hash", at, "note_sha256 must contain 64 lowercase hexadecimal characters")
            try:
                note = safe_path(root, expected_note)
                note_raw = read_regular(note)
                actual_digest = hashlib.sha256(note_raw).hexdigest()
                if actual_digest != digest:
                    error("note_hash_mismatch", at, "note bytes do not match note_sha256")
                words = narrative_words(note_raw.decode("utf-8"))
                if len(words) < 40 or len(set(words)) < 20:
                    error("note_substance", at, "note needs forty prose words, including twenty distinct words")
                if actual_digest in historical_hashes:
                    error("previous_session_note", at, f"identical note bytes occur in {historical_hashes[actual_digest]}")
                if actual_digest in note_hashes:
                    error("duplicate_note_bytes", at, f"note bytes already used by {note_hashes[actual_digest]}")
                note_hashes[actual_digest] = worker
                info = note.stat()
                inode = (info.st_dev, info.st_ino)
                if inode in note_inodes:
                    error("note_alias", at, f"note file is also used by {note_inodes[inode]}")
                note_inodes[inode] = worker
            except (OSError, ValueError, UnicodeError) as exc:
                error("note_input", at, str(exc))
            if len(errors) == before:
                verified.add(worker)
                waves[wave - 1]["verified"] += 1

    report["counts"].update(unique_ids=len(ids), unique_canonical_agents=len(canonical_agents),
                            accepted=len(accepted), running=len(running),
                            verified_accepted_notes=len(verified))
    report["missing_ids"] = sorted(IDS - ids)
    report["unaccepted_ids"] = sorted(ids - accepted)
    if strict and (ids != IDS or accepted != IDS or verified != IDS):
        error("incomplete", "assignments", "strict closure requires A01 through A60 accepted with verified notes")
    if strict and any(item["verified"] != 6 for item in waves):
        error("incomplete_waves", "assignments", "strict closure requires ten waves of six verified records")
    report["valid"] = not errors
    report["strict_record_closure"] = strict and not errors
    return report


def self_test():
    """Temporary fixtures test parser, counts, provenance, paths and note bytes."""
    with tempfile.TemporaryDirectory(prefix="b3-runtime-ledger-") as temporary:
        root = Path(temporary)
        session = root / DIRECTORY
        (session / "notes").mkdir(parents=True)
        text = ("This synthetic note exercises record validation with distinct ordinary words. "
                "The fixture describes source inspection, documented assumptions, retained "
                "evidence, observed limitations, preserved interfaces, and specific next "
                "actions for integration. These invented statements establish neither real "
                "dispatch nor implementation quality, independent acceptance, publication, "
                "physical calibration, audio fidelity, or product completion.\n")
        rows, note_bytes = [], {}
        for number in range(1, 61):
            worker, wave = f"A{number:02d}", (number - 1) // 6 + 1
            note = f"{DIRECTORY}/notes/{worker}.md"
            raw = (f"# Synthetic {worker}\n\n" + text).encode()
            (root / note).write_bytes(raw)
            note_bytes[worker] = raw
            rows.append({"id": worker, "wave": wave, "agent": f"/root/w{wave:02d}_a{number:02d}",
                         "status": "accepted", "task": "Synthetic validator acceptance fixture",
                         "owned_paths": [note], "note": note,
                         "note_sha256": hashlib.sha256(raw).hexdigest(),
                         "acceptance": "Synthetic note admitted only for this temporary validator exercise."})
        baseline = {**META, "assignments": rows}
        ledger, cases = session / "assignments.json", []

        def run(name, data, expected=True, strict=False, raw=None, code=None):
            ledger.write_bytes(raw if raw is not None else json.dumps(data).encode())
            result = check(root, strict)
            if result["valid"] != expected or (code and not any(e["code"] == code for e in result["errors"])):
                raise AssertionError((name, result))
            cases.append(name)
            return result

        result = run("complete_strict", baseline, strict=True)
        if result["counts"]["verified_accepted_notes"] != 60 or not result["strict_record_closure"]:
            raise AssertionError("strict counts/closure")
        partial = {**META, "assignments": copy.deepcopy(rows[:1])}
        run("partial_progress", partial)
        run("partial_strict_rejected", partial, False, True, code="incomplete")
        empty = {**META, "assignments": []}
        run("empty_progress", empty)
        run("empty_strict_rejected", empty, False, True, code="incomplete")
        running = copy.deepcopy(partial)
        running["assignments"][0]["status"] = "running"
        for key in ACCEPTED:
            running["assignments"][0].pop(key)
        first_note = root / rows[0]["note"]
        first_note.unlink()
        run("running_without_note", running)
        run("accepted_missing_note", partial, False, code="note_input")
        first_note.write_bytes(note_bytes["A01"])
        mutations = {
            "wrong_base": (lambda d: d.update(base_commit="0" * 40), "metadata"),
            "boolean_schema": (lambda d: d.update(schema_version=True), "metadata"),
            "wrong_worker_target": (lambda d: d.update(requested_workers=59), "metadata"),
            "wrong_wave_target": (lambda d: d.update(waves=9), "metadata"),
            "wrong_concurrency_target": (lambda d: d.update(max_concurrent_workers=6), "metadata"),
            "unknown_top_field": (lambda d: d.update(prior_workers=60), "schema"),
            "nonarray_workers": (lambda d: d.update(assignments={}), "assignments"),
            "too_many_workers": (lambda d: d["assignments"].append(copy.deepcopy(rows[0])), "assignments"),
            "nonobject_worker": (lambda d: d["assignments"].__setitem__(0, []), "worker_schema"),
            "missing_worker_field": (lambda d: d["assignments"][0].pop("agent"), "worker_schema"),
            "unknown_worker_field": (lambda d: d["assignments"][0].update(plan_only=True), "worker_schema"),
            "id_alias": (lambda d: d["assignments"][0].update(id="A1"), "id"),
            "id_boolean": (lambda d: d["assignments"][0].update(id=True), "id"),
            "id_out_of_range": (lambda d: d["assignments"][0].update(id="A61"), "id"),
            "duplicate_id": (lambda d: d["assignments"][1].update(id="A01"), "duplicate_id"),
            "wrong_wave": (lambda d: d["assignments"][6].update(wave=1), "wave"),
            "boolean_wave": (lambda d: d["assignments"][0].update(wave=True), "wave"),
            "duplicate_agent": (lambda d: d["assignments"][1].update(agent=rows[0]["agent"]), "duplicate_agent"),
            "agent_alias": (lambda d: d["assignments"][0].update(agent="/root/./w01_a01"), "agent"),
            "agent_followup": (lambda d: d["assignments"][0].update(agent="/root/w01_a01/review"), "agent"),
            "agent_nonstring": (lambda d: d["assignments"][0].update(agent=[]), "agent"),
            "planned_status": (lambda d: d["assignments"][0].update(status="planned"), "status"),
            "status_nonstring": (lambda d: d["assignments"][0].update(status={}), "status"),
            "empty_task": (lambda d: d["assignments"][0].update(task="  "), "task"),
            "placeholder_task": (lambda d: d["assignments"][0].update(task="To be determined"), "task"),
            "placeholder_acceptance": (lambda d: d["assignments"][0].update(acceptance="TODO " * 6), "acceptance"),
            "missing_acceptance": (lambda d: d["assignments"][0].pop("acceptance"), "acceptance"),
            "hash_type": (lambda d: d["assignments"][0].update(note_sha256=[]), "note_hash"),
            "hash_syntax": (lambda d: d["assignments"][0].update(note_sha256="G" * 64), "note_hash"),
            "hash_mismatch": (lambda d: d["assignments"][0].update(note_sha256="0" * 64), "note_hash_mismatch"),
            "note_alias": (lambda d: d["assignments"][0].update(note=rows[1]["note"]), "note_path"),
            "old_note_path": (lambda d: d["assignments"][0].update(note="docs/development/old/notes/A01.md"), "note_path"),
            "owned_path_type": (lambda d: d["assignments"][0].update(owned_paths="README.md"), "owned_paths"),
            "owned_path_member_type": (lambda d: d["assignments"][0]["owned_paths"].append({}), "owned_path"),
            "unowned_note": (lambda d: d["assignments"][0].update(owned_paths=["README.md"]), "owned_note"),
            "duplicate_owned_path": (lambda d: d["assignments"][0]["owned_paths"].append(rows[0]["note"]), "duplicate_owned_path"),
            "running_acceptance": (lambda d: d["assignments"][0].update(status="running"), "premature_acceptance"),
        }
        for name, (mutate, code) in mutations.items():
            data = copy.deepcopy(baseline)
            mutate(data)
            run(name, data, False, code=code)
        for number, path in enumerate(("../outside", "/absolute", "./README.md", "docs//file",
                                      "docs/../file", "C:/file", "docs\\file", "reports/*",
                                      "file\x00name", "docs/file.", "docs/NUL.txt")):
            data = copy.deepcopy(partial)
            data["assignments"][0]["owned_paths"].append(path)
            run(f"unsafe_path_{number}", data, False, code="owned_path")
        for name, raw in (("duplicate_json_field", b'{"schema_version":1,"schema_version":1}'),
                          ("nonfinite_json", b'{"schema_version":NaN}'),
                          ("invalid_utf8", b'\xff'), ("invalid_json", b'{'),
                          ("oversized_ledger", b' ' * (LIMIT + 1))):
            run(name, None, False, raw=raw, code="input")
        # Python versions differ on whether this reaches JSON parsing or schema
        # admission; either path must reject it cleanly, without an uncaught error.
        run("deep_json", None, False, raw=b'[' * 2000 + b']' * 2000)
        run("nonobject_ledger", [], False, code="schema")
        for name, raw, code in (("changed_note", note_bytes["A01"] + b"changed\n", "note_hash_mismatch"),
                                ("blank_note", b"", "note_substance"),
                                ("heading_and_code_only", b"# " + text.encode() + b"\n```\n" + text.encode() + b"```\n", "note_substance"),
                                ("invalid_note_encoding", b"\xff", "note_input"),
                                ("oversized_note", b"x" * (LIMIT + 1), "note_input"),
                                ("duplicate_note_bytes", note_bytes["A02"], "duplicate_note_bytes")):
            first_note.write_bytes(raw)
            data = copy.deepcopy(baseline)
            if name != "changed_note":
                data["assignments"][0]["note_sha256"] = hashlib.sha256(raw).hexdigest()
            run(name, data, False, code=code)
        first_note.unlink()
        first_note.symlink_to(root / rows[1]["note"])
        run("symlink_note", baseline, False, code="note_input")
        first_note.unlink()
        first_note.hardlink_to(root / rows[1]["note"])
        run("hardlink_note", baseline, False, code="note_alias")
        first_note.unlink()
        first_note.write_bytes(note_bytes["A01"])
        (root / "alias").symlink_to(session, target_is_directory=True)
        aliased = copy.deepcopy(partial)
        aliased["assignments"][0]["owned_paths"].append("alias/reports/new.py")
        run("symlink_parent_scope", aliased, False, code="owned_path")
        old_note = root / "docs/development/previous-session/notes/A01.md"
        old_note.parent.mkdir(parents=True)
        old_note.write_bytes(note_bytes["A01"])
        run("previous_session_bytes", partial, False, code="previous_session_note")
        old_note.write_bytes(b"Different historical note; it supplies no current worker credit.\n")
        result = run("historical_records_never_count", empty)
        if result["counts"]["records"] != 0 or result["other_session_notes_compared"] != 1:
            raise AssertionError("historical worker credit leaked")
        run("final_complete_strict", baseline, strict=True)
        return {"valid": True, "checks": len(cases), "cases": cases,
                "scope": "synthetic-validator-self-tests-only",
                "checker_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", default=".", help="repository root (default: current directory)")
    parser.add_argument("--strict", action="store_true", help="require all sixty accepted records")
    parser.add_argument("--self-test", action="store_true", help="run temporary adversarial fixtures instead")
    args = parser.parse_args()
    result = self_test() if args.self_test else check(args.repo, args.strict)
    print(json.dumps(result, indent=2, ensure_ascii=True, allow_nan=False))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
