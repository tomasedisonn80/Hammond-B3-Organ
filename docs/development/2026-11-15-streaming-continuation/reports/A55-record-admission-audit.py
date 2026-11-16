#!/usr/bin/env python3
"""Bounded independent admission checks; only temporary copies are mutated.

The retained A55 snapshot is an actual incomplete ledger, not manufactured
sixty-worker closure. Accepted note bytes must still match that snapshot.
Run from the repository root; stdout is a new JSON report.
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


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def inventory(root):
    return {
        p.relative_to(root).as_posix(): (
            {"symlink": str(p.readlink())} if p.is_symlink()
            else {"sha256": sha(p.read_bytes())}
        )
        for p in sorted(root.rglob("*")) if p.is_file() or p.is_symlink()
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    reports = repo / DIRECTORY / "reports"
    checker = reports / "check_streaming_session.py"
    snapshot = reports / "A55-ledger-snapshot.json.gz"
    raw = gzip.decompress(snapshot.read_bytes())
    source = json.loads(raw)
    accepted = [r for r in source["assignments"] if r["status"] == "accepted"]
    notes = {}
    for row in accepted:
        ref = next(p for p in row["owned_paths"]
                   if p.startswith((DIRECTORY / "notes").as_posix() + "/"))
        content = (repo / ref).read_bytes()
        if sha(content) != row["note_sha256"]:
            raise ValueError(f"retained accepted note bytes changed: {ref}")
        notes[ref] = content
    first_index = next(i for i, row in enumerate(source["assignments"])
                       if row["status"] == "accepted")
    first = source["assignments"][first_index]
    first_ref = next(p for p in first["owned_paths"] if p in notes)

    def run(name, expected_codes=(), mutation=None, raw_mutation=None, strict=False):
        with tempfile.TemporaryDirectory(prefix="A55-record-admission-") as location:
            root = Path(location)
            ledger = root / DIRECTORY / "assignments.json"
            ledger.parent.mkdir(parents=True)
            for ref, content in notes.items():
                target = root / ref
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
            data = copy.deepcopy(source)
            if mutation:
                mutation(data, root)
            content = json.dumps(data, indent=2).encode() + b"\n" if mutation else raw
            ledger.write_bytes(raw_mutation(content) if raw_mutation else content)
            command = [sys.executable, "-B", str(checker), "--repo", ".",
                       "--strict" if strict else "--progress"]
            before = inventory(root)
            process = subprocess.run(command, cwd=root, capture_output=True,
                                     text=True, check=False)
            after = inventory(root)
            result = json.loads(process.stdout)
            codes = [error["code"] for error in result["errors"]]
            expected_exit = 1 if expected_codes else 0
            passed = (process.returncode == expected_exit
                      and result["valid"] == (expected_exit == 0)
                      and result["strict_record_closure"] is False
                      and set(codes) == set(expected_codes)
                      and before == after and process.stderr == "")
            return {"case": name, "mode": result["mode"], "passed": passed,
                    "expected_exit": expected_exit, "exit": process.returncode,
                    "expected_error_codes": list(expected_codes), "errors": result["errors"],
                    "input_files_unchanged": before == after, "valid": result["valid"],
                    "strict_record_closure": result["strict_record_closure"],
                    "counts": result.get("counts"), "ledger_sha256": result["ledger"]["sha256"]}

    def field(name, value):
        def mutate(data, root):
            data["assignments"][first_index][name] = value
        return mutate

    def lowered_totals(data, root):
        data.update(requested_workers=53, requested_waves=9, workers_per_wave=5)

    def replace_note(content):
        def mutate(data, root):
            (root / first_ref).write_bytes(content)
            data["assignments"][first_index]["note_sha256"] = sha(content)
        return mutate

    def redirected_note(data, root):
        target = root / "docs/development/2026-11-15-product-continuation/notes/copied.md"
        target.parent.mkdir(parents=True)
        target.write_bytes(notes[first_ref])
        note = root / first_ref
        note.unlink()
        note.symlink_to(target)

    padding = ("alpha bravo charlie delta echo foxtrot golf hotel india juliet kilo lima "
               "mike november oscar papa quebec romeo sierra tango uniform victor whiskey "
               "xray yankee zulu amber bronze cobalt denim emerald fuchsia green hazel ivory "
               "jade khaki lavender magenta navy ochre purple quartz red silver teal")
    hidden = (f"# A01\n\nTODO.\n\n<!-- {padding} -->\n# {padding}\n"
              f"```text\n{padding}\n```\n~~~text\n{padding}\n~~~\n    {padding}\n").encode()
    repeated = ("# A01\n\n" + "pending deferred later waiting unfinished unavailable " * 12 + "\n").encode()
    cases = [
        run("actual incomplete snapshot and all genuine long accepted notes"),
        run("strict refuses actual incomplete snapshot",
            ("incomplete_numbers", "unaccepted_numbers", "incomplete_waves"), strict=True),
        run("targets cannot shrink from sixty / ten / six", ("metadata",), mutation=lowered_totals),
        run("boolean cannot stand for integer worker one", ("number",), mutation=field("number", True)),
        run("follow-up child path cannot become a distinct worker", ("agent_identity",),
            mutation=field("agent", first["agent"] + "/followup")),
        run("accepted row still needs nonblank acceptance", ("acceptance",),
            mutation=field("acceptance", " \t\n")),
        run("duplicate JSON member cannot override a row", ("input",),
            raw_mutation=lambda b: b.replace(b'"number": 1,', b'"number": 1, "number": 1,', 1)),
        run("comments headings fences and indentation cannot pad a placeholder", ("note_substance",),
            mutation=replace_note(hidden)),
        run("repeated short vocabulary cannot satisfy the distinct-word floor", ("note_substance",),
            mutation=replace_note(repeated)),
        run("matching bytes via older-session symlink cannot supply a current note", ("note_input",),
            mutation=redirected_note),
    ]
    author = json.loads((reports / "A46-author-checks.json").read_bytes())
    author_raw = gzip.decompress((reports / "A46-ledger-snapshot.json.gz").read_bytes())
    author_data = json.loads(author_raw)
    author_bindings = {
        "checker": sha(checker.read_bytes()) == author["checker_sha256"],
        "harness": sha((reports / "A46-author-checks.py").read_bytes()) == author["harness_sha256"],
        "snapshot_archive": sha((reports / "A46-ledger-snapshot.json.gz").read_bytes()) == author["snapshot"]["gzip_sha256"],
        "snapshot_ledger": sha(author_raw) == author["snapshot"]["ledger_sha256"],
        "snapshot_records": len(author_data["assignments"]) == author["snapshot"]["records"] == 47,
        "snapshot_accepted": sum(r["status"] == "accepted" for r in author_data["assignments"]) == author["snapshot"]["accepted"] == 44,
        "original_accepted_notes": all(
            sha((repo / next(p for p in row["owned_paths"] if "/notes/" in p)).read_bytes()) == row["note_sha256"]
            for row in author_data["assignments"] if row["status"] == "accepted"),
        "eleven_retained_successful_author_cases": len(author["cases"]) == 11
            and all(c["passed"] for c in author["cases"]),
    }
    report = {
        "schema": "b3-streaming-session-independent-admission-v1", "reviewer": "/root/w10_a55",
        "cwd": str(repo), "python": platform.python_version(),
        "command": f"python3 -B {DIRECTORY}/reports/A55-record-admission-audit.py --repo .",
        "checker_sha256": sha(checker.read_bytes()), "harness_sha256": sha(Path(__file__).read_bytes()),
        "snapshot": {"path": snapshot.relative_to(repo).as_posix(), "ledger_sha256": sha(raw),
                     "archive_sha256": sha(snapshot.read_bytes()), "records": len(source["assignments"]),
                     "accepted": len(accepted)},
        "author_evidence": {"report_sha256": sha((reports / "A46-author-checks.json").read_bytes()),
                            "bindings": author_bindings, "author_cases_rerun": False},
        "long_note_compatibility": {"accepted_notes_over_2000_bytes": sum(len(x) > 2000 for x in notes.values()),
                                    "maximum_accepted_note_bytes": max(map(len, notes.values())),
                                    "early_reader_bytes": {f"A{n:02d}": len(notes[next(p for p in notes if f"/A{n:02d}-" in p)])
                                                           for n in range(1, 7)}},
        "cases": cases, "passed": all(c["passed"] for c in cases) and all(author_bindings.values()),
        "limits": ("Ten bounded processes: two real-snapshot checks and eight complementary structural mutations. "
                   "Author results were inspected and their input identities independently matched, not rerun. "
                   "No accepted worker was added and no successful sixty-worker strict result is claimed. "
                   "The prose floor cannot recognize all semantic placeholders, invented work or copied narrative. "
                   "No external dispatch, chronology, concurrency, technical quality, product, platform or publication acceptance follows."),
    }
    print(json.dumps(report, separators=(",", ":")))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
