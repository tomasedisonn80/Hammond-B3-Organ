#!/usr/bin/env python3
"""Independent CLI fixtures for A54; all fabricated records live outside the repo."""

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


SESSION = Path("docs/development/2026-11-14-interface-continuation")
NOTE = """# Temporary structural fixture

This synthetic note exists only to exercise the retained-record checker. It is
not a report of an actual worker, dispatch, accepted implementation or execution.
The independent fixture provides a small substantive narrative so that the
checker can distinguish ordinary retained prose from empty files, headings and
code-only placeholders. No product, model, physical or publication claim follows.
"""


def manifest():
    return {
        "schema": 1, "session": "2026-11-14-interface-continuation",
        "requested_agents": 60, "requested_waves": 10, "batch_size": 3,
        "base_commit": "d493e998e5dd7cf44db46854e87309745063ac54",
        "scheduling": "Synthetic CLI verification only; these are not actual dispatched workers.",
        "assignments": [
            {"number": number, "wave": (number - 1) // 6 + 1,
             "agent": f"/root/w{(number - 1) // 6 + 1:02d}_a{number:02d}_fixture",
             "scope": "Temporary schema fixture, not a real assignment.",
             "status": "accepted", "result": f"note-{number:02d}.md",
             "acceptance": "Synthetic checker fixture; no substantive acceptance claimed."}
            for number in range(1, 61)
        ],
    }


def call(checker, root, progress=False):
    command = [sys.executable, "-B", str(checker), "--repo", str(root), "--json"]
    if progress:
        command.append("--in-progress")
    completed = subprocess.run(command, text=True, capture_output=True, timeout=10)
    assert not completed.stderr, completed.stderr
    return completed.returncode, json.loads(completed.stdout), completed.stdout


def summary(returncode, report):
    return {key: report[key] for key in (
        "status", "mode", "record_consistency_valid", "completion_valid", "counts",
        "missing_numbers", "error_count", "errors", "manifest", "checked_notes_sha256"
    )} | {"exit_code": returncode}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[4])
    args = parser.parse_args()
    repo = args.repo.resolve(strict=True)
    checker = repo / "tools/check_interface_session.py"
    cases = []

    def case(name, mutate=None, expected=1, error=None, progress=False, after_write=None):
        with tempfile.TemporaryDirectory(prefix="hammond-a54-") as temporary:
            area = Path(temporary).resolve()
            assert not area.is_relative_to(repo), "fixture must be outside the repository"
            root = area / "fixture"
            session = root / SESSION
            session.mkdir(parents=True)
            data = manifest()
            for row in data["assignments"]:
                (session / row["result"]).write_text(NOTE, encoding="utf-8")
            if mutate:
                mutate(data, session)
            path = session / "assignments.json"
            path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            if after_write:
                after_write(path, area)
            returncode, report, output = call(checker, root, progress)
            assert returncode == expected, (name, returncode, report)
            codes = {item["code"] for item in report["errors"]}
            if error:
                assert error in codes, (name, codes)
            if expected:
                assert report["completion_valid"] is False and report["status"] == "failed"
            elif name == "complete_60":
                assert report["completion_valid"] is True
                assert report["counts"]["accepted"] == 60
                assert report["counts"]["distinct_agents"] == 60
                assert report["accepted_waves"] == list(range(1, 11))
                again = call(checker, root, progress)
                assert again[0] == 0 and again[2] == output, "same inputs must emit identical JSON"
            elif progress:
                assert report["status"] == "incomplete" and report["completion_valid"] is False
                assert report["record_consistency_valid"] is True
            cases.append({"case": name, "expected_exit": expected, "actual_exit": returncode,
                          "status": report["status"], "error_codes": sorted(codes),
                          "completion_valid": report["completion_valid"]})

    def row(field, value, index=0):
        return lambda data, _: data["assignments"][index].__setitem__(field, value)

    def partial(data, _):
        data["assignments"] = data["assignments"][:7]
        data["assignments"][-1]["status"] = "running"
        del data["assignments"][-1]["result"]
        del data["assignments"][-1]["acceptance"]

    def note_file(action):
        return lambda data, session: action(session / data["assignments"][0]["result"])

    def linked_note(data, session):
        path = session / data["assignments"][0]["result"]
        target = session.parents[3] / "outside-note.md"
        target.write_text(NOTE, encoding="utf-8")
        path.unlink()
        path.symlink_to(target)

    def linked_parent(data, session):
        target = session.parents[3] / "outside-directory"
        target.mkdir()
        (target / "note.md").write_text(NOTE, encoding="utf-8")
        (session / "alias").symlink_to(target, target_is_directory=True)
        data["assignments"][0]["result"] = "alias/note.md"

    def linked_manifest(path, area):
        target = area / "external-manifest.json"
        path.rename(target)
        path.symlink_to(target)

    def raw_replace(old, new):
        return lambda path, _: path.write_text(path.read_text().replace(old, new, 1), encoding="utf-8")

    case("complete_60", expected=0)
    case("complete_60_out_of_dispatch_order", lambda d, _: d["assignments"].reverse(), expected=0)
    case("partial_actual_records", partial, expected=0, progress=True)
    case("partial_default_rejected", partial, error="completion_count")
    case("empty_in_progress", lambda d, _: d.__setitem__("assignments", []), expected=0, progress=True)
    case("duplicate_number", row("number", 59, 59), error="number_duplicate")
    case("missing_middle_number", lambda d, _: d["assignments"].pop(28), error="completion_count")
    case("out_of_range_number", row("number", 61, 59), error="number_type")
    case("extra_future_row", lambda d, _: d["assignments"].append(copy.deepcopy(d["assignments"][-1])),
         error="assignments_type")
    case("wrong_wave", row("wave", 1, 6), error="wave_mapping")
    case("duplicate_identity", row("agent", "/root/w01_a01_fixture", 1), error="agent_duplicate")
    case("empty_identity", row("agent", " "), error="agent_identity")
    case("identity_wrong_number", row("agent", "/root/w01_a02_other"), error="agent_mapping")
    case("running_default_rejected", row("status", "running"), error="completion_status")
    case("planned_rejected_in_progress", row("status", "planned"), error="status_invalid", progress=True)
    case("future_status_rejected", row("status", "future"), error="status_invalid")
    case("completed_is_not_accepted", row("status", "completed"), error="status_invalid")
    case("status_wrong_type", row("status", []), error="status_invalid")
    case("scope_empty", row("scope", " \n\t"), error="text_required")
    case("acceptance_missing", lambda d, _: d["assignments"][0].pop("acceptance"), error="row_fields")
    case("acceptance_empty", row("acceptance", ""), error="text_required")
    case("result_missing", lambda d, _: d["assignments"][0].pop("result"), error="result_path")
    case("result_empty", row("result", " "), error="result_path")
    case("duplicate_note", row("result", "note-01.md", 1), error="note_duplicate")
    case("missing_note", note_file(lambda path: path.unlink()), error="note_read")
    case("empty_note", note_file(lambda path: path.write_text("")), error="note_substance")
    case("heading_only_note", note_file(lambda path: path.write_text("# Done\n")), error="note_substance")
    case("code_only_note", note_file(lambda path: path.write_text("```text\n" + NOTE + "\n```\n")),
         error="note_substance")
    case("comment_only_note", note_file(lambda path: path.write_text("<!--\n" + NOTE + "\n-->\n")),
         error="note_substance")
    case("invalid_utf8_note", note_file(lambda path: path.write_bytes(b"\xff")), error="note_read")
    case("oversized_note", note_file(lambda path: path.write_bytes(b"a" * (128 * 1024 + 1))),
         error="note_read")
    case("path_parent_escape", row("result", "../outside.md"), error="result_path")
    case("path_absolute", row("result", "/tmp/outside.md"), error="result_path")
    case("path_windows_drive", row("result", "C:/outside.md"), error="result_path")
    case("path_backslash", row("result", "..\\outside.md"), error="result_path")
    case("path_empty_component", row("result", "nested//note.md"), error="result_path")
    case("note_symlink", linked_note, error="result_path")
    case("parent_symlink", linked_parent, error="result_path")
    case("manifest_symlink", after_write=linked_manifest, error="manifest_read")
    case("note_is_directory", note_file(lambda path: (path.unlink(), path.mkdir())), error="result_path")
    if hasattr(os, "mkfifo"):
        case("note_is_fifo", note_file(lambda path: (path.unlink(), os.mkfifo(path))), error="result_path")
    case("schema_boolean", lambda d, _: d.__setitem__("schema", True), error="manifest_type")
    case("number_boolean", row("number", True), error="number_type")
    case("number_float", row("number", 1.0), error="manifest_read")
    case("wrong_session", lambda d, _: d.__setitem__("session", "another-session"), error="session_identity")
    case("wrong_base", lambda d, _: d.__setitem__("base_commit", "0" * 40), error="base_identity")
    case("unexpected_manifest_field", lambda d, _: d.__setitem__("invented", True), error="manifest_fields")
    case("unexpected_row_field", row("planned", True), error="row_fields")
    case("row_wrong_type", lambda d, _: d["assignments"].__setitem__(0, []), error="row_type")
    case("duplicate_json_member", after_write=raw_replace('"schema": 1', '"schema": 1, "schema": 1'),
         error="manifest_read")
    case("nonstandard_json_constant", after_write=raw_replace('"requested_agents": 60', '"requested_agents": NaN'),
         error="manifest_read")

    strict_code, strict, _ = call(checker, repo)
    progress_code, progress, _ = call(checker, repo, progress=True)
    assert strict_code == 1 and strict["status"] == "failed" and not strict["completion_valid"], strict
    assert progress_code == 0 and progress["status"] == "incomplete", progress
    assert progress["record_consistency_valid"] and not progress["completion_valid"], progress
    report = {
        "schema_version": 1, "assignment": 54, "status": "passed",
        "scope": "standalone checker CLI verification; no application/build/CI execution",
        "checker_sha256": hashlib.sha256(checker.read_bytes()).hexdigest(),
        "verification_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "fixture_policy": "Constructed manifests and notes were temporary, outside the repository and removed.",
        "fixture_case_count": len(cases), "fixture_cases": cases,
        "real_manifest_strict": summary(strict_code, strict),
        "real_manifest_in_progress": summary(progress_code, progress),
        "claim": "Fixtures prove specified rejection behavior only; real dispatch and acceptance require root/A59/A60 review.",
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
