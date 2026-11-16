#!/usr/bin/env python3
"""Replay A46's small author check against a retained real incomplete snapshot.

Run from the repository root and redirect stdout to a new report if desired.
Only temporary copies are mutated; this harness never changes the live ledger,
notes, retained snapshot or prior report. No synthetic accepted worker is added.
"""

import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import tempfile


DIRECTORY = Path("docs/development/2026-11-15-streaming-continuation")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def tree_hashes(root):
    return {p.relative_to(root).as_posix(): digest(p.read_bytes())
            for p in sorted(root.rglob("*")) if p.is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    checker = repo / DIRECTORY / "reports/check_streaming_session.py"
    snapshot = repo / DIRECTORY / "reports/A46-ledger-snapshot.json.gz"
    raw = gzip.decompress(snapshot.read_bytes())
    source = json.loads(raw)
    accepted_row = next(i for i, row in enumerate(source["assignments"])
                        if row["status"] == "accepted")
    notes = {}
    for row in source["assignments"]:
        for ref in row["owned_paths"]:
            if ref.startswith((DIRECTORY / "notes").as_posix() + "/") and (repo / ref).is_file():
                notes[ref] = (repo / ref).read_bytes()
    first = source["assignments"][accepted_row]
    first_note = next(p for p in first["owned_paths"] if "/notes/" in p)

    def run(name, expected_codes=(), strict=False, mutation=None, path_style="relative"):
        with tempfile.TemporaryDirectory(prefix="A46-streaming-session-") as location:
            root = Path(location)
            ledger = root / DIRECTORY / "assignments.json"
            ledger.parent.mkdir(parents=True)
            ledger.write_bytes(raw)
            for ref, content in notes.items():
                target = root / ref
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
            data = copy.deepcopy(source)
            if mutation:
                mutation(data, root)
                ledger.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            command = [sys.executable, "-B", str(checker)]
            if path_style == "relative":
                command += ["--repo", ".", "--session", str(DIRECTORY)]
            elif path_style == "absolute":
                command += ["--repo", str(root), "--session", str(ledger)]
            if strict:
                command.append("--strict")
            before = tree_hashes(root)
            process = subprocess.run(command, cwd=root, capture_output=True, text=True, check=False)
            after = tree_hashes(root)
            result = json.loads(process.stdout)
            codes = {error["code"] for error in result["errors"]}
            expected_exit = 1 if expected_codes else 0
            passed = (process.returncode == expected_exit
                      and result["valid"] == (expected_exit == 0)
                      and not result["strict_record_closure"]
                      and set(expected_codes).issubset(codes)
                      and before == after and not process.stderr)
            return {"case": name, "passed": passed, "exit": process.returncode,
                    "expected_exit": expected_exit, "required_error_codes": list(expected_codes),
                    "errors": result["errors"], "valid": result["valid"],
                    "strict_record_closure": result["strict_record_closure"],
                    "input_files_unchanged": before == after,
                    "path_style": path_style, "mode": result["mode"],
                    "counts": result.get("counts")}

    def change(field, value):
        def mutate(data, root):
            data["assignments"][accepted_row][field] = value
        return mutate

    def duplicate(data, root):
        data["assignments"].append(copy.deepcopy(first))

    def remove_note(data, root):
        (root / first_note).unlink()

    def placeholder(data, root):
        content = b"# A01\n\nTODO.\n"
        (root / first_note).write_bytes(content)
        data["assignments"][accepted_row]["note_sha256"] = digest(content)

    def old_session(data, root):
        data["session"] = "2026-11-15-product-continuation"

    def old_note(data, root):
        row = data["assignments"][accepted_row]
        row["owned_paths"] = [p.replace("2026-11-15-streaming-continuation",
                                        "2026-11-15-product-continuation")
                              if p == first_note else p for p in row["owned_paths"]]

    cases = [
        run("real incomplete snapshot: default repository CWD", path_style="default"),
        run("real incomplete snapshot: absolute repo and ledger paths", path_style="absolute"),
        run("strict incomplete snapshot", ("incomplete_numbers", "unaccepted_numbers", "incomplete_waves"), strict=True),
        run("duplicate actual record / repeated follow-up", ("duplicate_number", "duplicate_agent"), mutation=duplicate),
        run("assignment in wrong wave", ("wrong_wave",), mutation=change("wave", 2)),
        run("missing accepted note", ("note_input",), mutation=remove_note),
        run("stale accepted note hash", ("note_hash_mismatch",), mutation=change("note_sha256", "0" * 64)),
        run("placeholder note with refreshed hash", ("note_substance",), mutation=placeholder),
        run("older session cannot supply credit", ("metadata",), mutation=old_session),
        run("owned note in an older session", ("owned_note",), mutation=old_note),
        run("planned slot cannot close strict mode", ("status", "incomplete_numbers", "incomplete_waves"),
            strict=True, mutation=change("status", "planned")),
    ]
    report = {
        "schema": "b3-streaming-session-author-checks-v1", "author": "/root/w08_a46",
        "scope": "bounded author checks of retained-record validation, not worker or product acceptance",
        "cwd": str(repo), "python": platform.python_version(),
        "command": f"python3 -B {DIRECTORY}/reports/A46-author-checks.py --repo .",
        "checker_sha256": digest(checker.read_bytes()),
        "harness_sha256": digest(Path(__file__).read_bytes()),
        "snapshot": {"path": snapshot.relative_to(repo).as_posix(),
                     "gzip_sha256": digest(snapshot.read_bytes()), "ledger_sha256": digest(raw),
                     "records": len(source["assignments"]),
                     "accepted": sum(row["status"] == "accepted" for row in source["assignments"])},
        "long_note_compatibility": {"maximum_note_bytes": max(map(len, notes.values())),
                                    "notes_over_2000_bytes": sum(len(v) > 2000 for v in notes.values()),
                                    "no_global_2000_byte_limit": True},
        "cases": cases, "passed": all(case["passed"] for case in cases),
        "limits": "All mutations used temporary copies of the real incomplete snapshot. No full-session strict pass is claimed. Root must run strict mode after actual acceptance of all sixty workers. This does not test adversarial filesystem races or authenticate external dispatch.",
    }
    print(json.dumps(report, separators=(",", ":")))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
