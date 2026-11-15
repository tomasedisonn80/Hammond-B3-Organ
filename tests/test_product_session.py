#!/usr/bin/env python3
"""Synthetic temporary fixtures only; none of these rows represent dispatched workers."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock


REPO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("product_session_checker", REPO / "tools/check_product_session.py")
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)
BODY = """# Synthetic accounting fixture

This document exists only inside an isolated temporary test directory. It is
deliberately fabricated test data and never records a real dispatched worker,
integrator decision, product change, executed platform experiment, or published
result. The fixture exercises a structural accounting contract using ordinary
prose with enough varied words to distinguish a narrative from repeated filler.

The declared task concerns a bounded source file and a clearly named ownership
scope. Its acceptance text describes a synthetic review condition. Associated
byte identities allow the tests to detect changed content, missing files,
invalid paths, duplicate records, contradictory statuses, incorrect wave
membership, unexpected schema fields, and unsafe filesystem references.

No actual application runs here. Hardware behavior, sound quality, native
accessibility, electrical accuracy, dispatch authenticity, and product readiness
remain outside this test. The expected next step is an independent review of
the validator's observed output followed by the appropriate real session gate.
"""


class ProductSessionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="b3-product-record-test-")
        self.addCleanup(self.temp.cleanup)
        self.temporary = Path(self.temp.name)
        self.root = self.temporary / "repo"
        self.session = self.root / CHECKER.DIRECTORY
        (self.session / "notes").mkdir(parents=True)
        self.manifest_path = self.root / CHECKER.MANIFEST
        self.manifest = {
            "schema": "b3-product-session-v1", "session": CHECKER.SESSION,
            "started_at_utc": "2026-11-15", "client_date": "2026-11-14",
            "start_commit": CHECKER.START_COMMIT, "requested_agents": 60,
            "requested_waves": 10, "concurrency": 3, "assignments": [],
        }
        for number in range(1, 8):
            self.add_row(number, "accepted" if number <= 6 else "running")
        self.save()

    def add_row(self, number, status="accepted"):
        identifier = f"A{number:02d}"
        wave = (number - 1) // 6 + 1
        note = f"notes/{identifier}-synthetic-fixture.md"
        row = {"id": identifier, "wave": wave, "agent": f"/root/w{wave:02d}_a{number:02d}_synthetic_fixture",
               "task": "Check the explicitly synthetic record fixture", "status": status,
               "note": note, "owned_files": [(CHECKER.DIRECTORY / note).as_posix()]}
        if status != "running":
            row["acceptance"] = "Synthetic review condition for a temporary fixture only"
            self.write_note(row)
        self.manifest["assignments"].append(row)
        return row

    def write_note(self, row, body=None):
        raw = (BODY + f"\nFixture identity: {row['id']}.\n") if body is None else body
        if isinstance(raw, str):
            raw = raw.encode("utf-8")
        (self.session / row["note"]).write_bytes(raw)
        row["note_sha256"] = hashlib.sha256(raw).hexdigest()

    def save(self):
        self.manifest_path.write_text(json.dumps(self.manifest, indent=2), encoding="utf-8")

    def check(self, progress=True):
        self.save()
        return CHECKER.check(self.root, allow_incomplete=progress)

    def assert_error(self, report, code=None):
        self.assertEqual(report["status"], "failed")
        self.assertFalse(report["completion_valid"])
        self.assertGreater(report["error_count"], 0)
        if code:
            self.assertIn(code, {error["code"] for error in report["errors"]}, report["errors"])

    def symlink(self, target, path, directory=False):
        try:
            path.symlink_to(target, target_is_directory=directory)
        except OSError as exc:
            self.skipTest(f"runner cannot create symbolic links: {exc}")

    def test_partial_progress_never_certifies_completion(self):
        report = self.check()
        self.assertEqual(report["status"], "incomplete")
        self.assertTrue(report["record_consistency_valid"])
        self.assertFalse(report["completion_valid"])
        self.assertEqual(report["counts"]["recorded"], 7)
        self.assertEqual(report["counts"]["verified_accepted_notes"], 6)
        self.assertEqual(report["accepted_waves"], [1])
        self.assertEqual(len(report["missing_ids"]), 53)
        self.assert_error(self.check(False), "completion_count")

    def test_complete_synthetic_fixture_requires_exact_sixty_and_ten_waves(self):
        running = self.manifest["assignments"].pop()
        self.assertEqual(running["id"], "A07")
        for number in range(7, 61):
            self.add_row(number)
        report = self.check(False)
        self.assertEqual(report["status"], "passed", report["errors"])
        self.assertTrue(report["completion_valid"])
        self.assertEqual(report["accepted_waves"], list(range(1, 11)))
        self.assertEqual(report["counts"]["verified_accepted_notes"], 60)
        self.assertEqual(report["manifest"]["sha256"], hashlib.sha256(self.manifest_path.read_bytes()).hexdigest())
        self.assertFalse(report["external_dispatch_attested"])
        self.assertFalse(report["product_or_model_readiness_attested"])
        self.assertIn("cannot attest actual tool dispatch", report["claim"])
        self.assertFalse(self.check()["completion_valid"])
        self.manifest["assignments"][-1]["status"] = "review_complete"
        self.assertEqual(self.check()["error_count"], 0)
        self.assert_error(self.check(False), "completion_status")

    def test_running_optional_notes_but_declared_evidence_must_match(self):
        row = self.manifest["assignments"][-1]
        note = row.pop("note")
        self.assertEqual(self.check()["error_count"], 0)
        row["note_sha256"] = "0" * 64
        self.assert_error(self.check(), "note_path")
        row["note"] = note
        self.assert_error(self.check(), "note_read")
        self.write_note(row, "Draft narrative may still be short.\n")
        self.assertEqual(self.check()["error_count"], 0)
        row["note_sha256"] = "0" * 64
        self.assert_error(self.check(), "note_hash_mismatch")
        row["status"] = "review_complete"
        row["acceptance"] = "Awaiting integrator review of this synthetic fixture"
        self.write_note(row, "Short draft is not accepted evidence.\n")
        self.assert_error(self.check(), "note_substance")

    def test_id_agent_and_wave_identity_mutations(self):
        original = copy.deepcopy(self.manifest)
        cases = [("id", value, "id_invalid") for value in ("A00", "A61", "A1", 1, None, [], {})]
        cases += [("wave", value, "wave_mapping") for value in (True, 1.0, 2, 0, "1", None)]
        cases += [("agent", value, "agent_identity") for value in
                  ("/root", "/root//w01_a01_fixture", "/root/w1_a01_fixture", "/root/w01_a01_TODO",
                   "/root/w01_a01_unassigned", "/root/w01_a01_fixture/child", "relative", None)]
        cases += [("agent", "/root/w02_a07_fixture", "agent_mapping")]
        for field, value, code in cases:
            with self.subTest(field=field, value=value):
                self.manifest = copy.deepcopy(original)
                self.manifest["assignments"][0][field] = value
                # JSON floats are rejected before the wave schema check.
                self.assert_error(self.check(), "manifest_read" if type(value) is float else code)
        self.manifest = copy.deepcopy(original)
        self.manifest["assignments"][1] = copy.deepcopy(self.manifest["assignments"][0])
        report = self.check()
        for code in ("id_duplicate", "agent_duplicate", "note_duplicate"):
            self.assert_error(report, code)

    def test_schema_count_and_actual_status_are_not_coercible(self):
        original = copy.deepcopy(self.manifest)
        for field, value in (("schema", "b3-refinement-session-v1"), ("session", "historical"),
                             ("start_commit", "0" * 40), ("requested_agents", "60"),
                             ("requested_agents", 59), ("requested_waves", 9), ("concurrency", True),
                             ("started_at_utc", "2026-11-14"), ("client_date", "2026-11-15")):
            with self.subTest(field=field):
                self.manifest = copy.deepcopy(original)
                self.manifest[field] = value
                self.assert_error(self.check(), "manifest_identity")
        for state in ("planned", "complete", "queued", True, [], None):
            self.manifest = copy.deepcopy(original)
            self.manifest["assignments"][0]["status"] = state
            self.assert_error(self.check(), "status_invalid")
        self.manifest = copy.deepcopy(original)
        self.manifest["unexpected"] = "ignored metadata must not hide a schema typo"
        self.assert_error(self.check(), "manifest_fields")
        self.manifest = copy.deepcopy(original)
        self.manifest["assignments"] = [self.manifest["assignments"][0]] * 61
        self.assert_error(self.check(), "assignments_type")

    def test_required_task_acceptance_and_owned_fields(self):
        original = copy.deepcopy(self.manifest)
        for field in ("task", "acceptance"):
            for value in (None, "", "  ", "TODO: fill this", "pending", "x\x00", [], 42):
                with self.subTest(field=field, value=value):
                    self.manifest = copy.deepcopy(original)
                    self.manifest["assignments"][0][field] = value
                    self.assert_error(self.check(), "text_required")
        for value in ([], "src/file.cpp", None, ["a"] * 129):
            self.manifest = copy.deepcopy(original)
            self.manifest["assignments"][0]["owned_files"] = value
            self.assert_error(self.check(), "ownership_list")
        self.manifest = copy.deepcopy(original)
        del self.manifest["assignments"][0]["note_sha256"]
        self.assert_error(self.check(), "row_fields")
        self.manifest["assignments"][0]["accepted"] = True
        self.assert_error(self.check(), "row_fields")

    def test_hash_tampering_and_crlf_use_raw_bytes(self):
        row = self.manifest["assignments"][0]
        note = self.session / row["note"]
        note.write_text(BODY + "Changed retained bytes.\n", encoding="utf-8")
        self.assert_error(self.check(), "note_hash_mismatch")
        for digest in (None, "0" * 63, "F" * 64, [], 0):
            row["note_sha256"] = digest
            self.assert_error(self.check(), "note_hash")
        self.write_note(row, BODY.replace("\n", "\r\n"))
        report = self.check()
        self.assertEqual(report["error_count"], 0, report["errors"])
        self.assertEqual(report["checked_notes"][0]["sha256"], hashlib.sha256(note.read_bytes()).hexdigest())

    def test_substantive_floor_does_not_impose_retroactive_word_ceiling(self):
        row = self.manifest["assignments"][0]
        bad = ("", "Evidence. " * 150, "# TODO: supply evidence\n" + BODY,
               "Short prose.\n<!--" + BODY + "-->", "Short prose.\n```text\n" + BODY + "```\n",
               "Short prose.\n~~~~\n" + BODY + "~~~~\n",
               "Short prose.\n" + "\n".join("    " + line for line in BODY.splitlines()))
        for body in bad:
            with self.subTest(body=body[:30]):
                self.write_note(row, body)
                self.assert_error(self.check(), "note_substance")
        self.write_note(row, BODY * 7)
        report = self.check()
        self.assertEqual(report["error_count"], 0)
        self.assertGreater(report["checked_notes"][0]["narrative_words"], 900)
        for body in (b"\xff", (BODY + "\x00").encode(), (BODY + "bare\rcarriage").encode()):
            self.write_note(row, body)
            self.assert_error(self.check(), "note_read")

    def test_note_paths_cannot_leave_current_session_or_change_identity(self):
        original = copy.deepcopy(self.manifest)
        unsafe = ("../notes/A01-fixture.md", "/tmp/A01-fixture.md", "C:/A01-fixture.md",
                  "notes/../A01-fixture.md", "notes//A01-fixture.md", "notes/A02-fixture.md",
                  "notes/A01-fixture.txt", "notes/A01-fixture.md/", "notes\\A01-fixture.md",
                  "docs/development/historical/notes/A01-fixture.md", "notes/A01-fixture\x00.md", None, [])
        for index in (0, 6):
            for value in unsafe:
                with self.subTest(index=index, value=value):
                    self.manifest = copy.deepcopy(original)
                    self.manifest["assignments"][index]["note"] = value
                    self.assert_error(self.check(), "note_path")

    def test_ownership_supports_actual_scopes_and_directories(self):
        row = self.manifest["assignments"][0]
        source = self.root / "apps/standalone/View.cpp"
        source.parent.mkdir(parents=True)
        source.write_text("// Synthetic source only.\n", encoding="utf-8")
        row["owned_files"] += ["apps/standalone/View.cpp (MIDI overlay only)", "apps/standalone/"]
        report = self.check()
        self.assertEqual(report["error_count"], 0, report["errors"])
        owned = next(item for item in report["checked_ownership"] if item["scope"])
        self.assertEqual(owned["path"], "apps/standalone/View.cpp")
        self.assertEqual(owned["scope"], "MIDI overlay only")
        self.assertTrue(any(item["directory"] for item in report["checked_ownership"]))
        self.manifest["assignments"][-1]["owned_files"].append("future/new-file.cpp (declared running scope)")
        self.assertEqual(self.check()["error_count"], 0)
        row["owned_files"].append("future/new-file.cpp")
        self.assert_error(self.check(), "ownership_path")

    def test_ownership_traversal_globs_malformed_scopes_and_special_paths_fail(self):
        original = copy.deepcopy(self.manifest)
        bad = ("../outside", "/tmp/outside", "C:/outside", "apps\\source.cpp", "a/../b", ".",
               "a//b", "a/./b", "tools/*", "tools/[ab].py", "a\x00b", "a\nb", "a//",
               "a ( )", "a (missing closing parenthesis", " a", "a ", "a/ b", "", None, [])
        for value in bad:
            with self.subTest(value=value):
                self.manifest = copy.deepcopy(original)
                self.manifest["assignments"][-1]["owned_files"] = [value]
                self.assert_error(self.check(), "ownership_path")
        self.manifest = copy.deepcopy(original)
        row = self.manifest["assignments"][0]
        row["owned_files"] *= 2
        self.assert_error(self.check(), "ownership_path")
        row["owned_files"] = [row["owned_files"][0] + "/"]
        self.assert_error(self.check(), "ownership_path")

    def test_missing_accepted_notes_and_nonregular_files_fail_closed(self):
        row = self.manifest["assignments"][0]
        note = self.session / row["note"]
        note.unlink()
        self.assert_error(self.check(), "note_read")
        note.mkdir()
        self.assert_error(self.check(), "note_path")
        note.rmdir()
        self.write_note(row)
        self.save()
        self.manifest_path.unlink()
        self.manifest_path.mkdir()
        self.assert_error(CHECKER.check(self.root, True), "manifest_read")

    def test_symlink_leaf_parent_ownership_and_root_are_rejected(self):
        row = self.manifest["assignments"][0]
        note = self.session / row["note"]
        outside = self.temporary / "outside.md"
        outside.write_bytes(note.read_bytes())
        note.unlink()
        self.symlink(outside, note)
        self.assert_error(self.check(), "note_path")
        note.unlink()
        self.write_note(row)
        owned = self.root / "escape"
        self.symlink(self.temporary, owned, directory=True)
        row["owned_files"].append("escape/outside.md (scoped link must still fail)")
        self.assert_error(self.check(), "ownership_path")
        row["owned_files"].pop()
        target = self.temporary / "moved-notes"
        (self.session / "notes").rename(target)
        self.symlink(target, self.session / "notes", directory=True)
        self.assert_error(self.check(), "note_path")
        alias = self.temporary / "repo-alias"
        self.symlink(self.root, alias, directory=True)
        self.assert_error(CHECKER.check(alias, True), "manifest_read")

    @unittest.skipUnless(hasattr(os, "mkfifo"), "runner has no FIFO support")
    def test_fifo_inputs_are_rejected_before_open(self):
        for path in (self.manifest_path, self.session / self.manifest["assignments"][0]["note"]):
            original = path.read_bytes()
            path.unlink()
            os.mkfifo(path)
            self.assert_error(CHECKER.check(self.root, True))
            path.unlink()
            path.write_bytes(original)

    def test_reparse_points_are_rejected_on_windows_metadata(self):
        original = Path.lstat
        for marked in (self.root, self.root / "docs", self.session / "notes",
                       self.session / self.manifest["assignments"][0]["note"]):
            def altered(path, *args, **kwargs):
                metadata = original(path, *args, **kwargs)
                return (SimpleNamespace(st_mode=metadata.st_mode, st_file_attributes=0x400)
                        if path == marked else metadata)
            with self.subTest(path=marked), mock.patch.object(Path, "lstat", autospec=True, side_effect=altered):
                self.assert_error(CHECKER.check(self.root, True))

    def test_bounded_parser_rejects_duplicate_numbers_encoding_and_depth(self):
        original = self.manifest_path.read_text(encoding="utf-8")
        values = ("{", "null", "[]", "true", "[" * 2000 + "]" * 2000,
                  original.replace('"requested_agents": 60', '"requested_agents": 60, "requested_agents": 60'),
                  original.replace('"id": "A01"', '"id": "A01", "id": "A01"'),
                  *[original.replace('"wave": 1', f'"wave": {value}', 1)
                    for value in ("NaN", "Infinity", "-Infinity", "1.0", "1e0", "9" * 9000)])
        for value in values:
            with self.subTest(value=value[:35]):
                self.manifest_path.write_text(value, encoding="utf-8")
                self.assert_error(CHECKER.check(self.root, True))
        self.manifest_path.write_bytes(b"\xff")
        self.assert_error(CHECKER.check(self.root, True), "manifest_read")
        self.save()
        self.assert_error(CHECKER.check(None, True), "manifest_read")
        self.assert_error(CHECKER.check(self.root, "true"), "manifest_read")

    def test_byte_bounds_are_exact_and_have_no_word_ceiling(self):
        row = self.manifest["assignments"][0]
        raw = BODY.encode()
        self.write_note(row, raw + b" " * (CHECKER.MAX_NOTE_BYTES - len(raw)))
        self.save()
        raw = self.manifest_path.read_bytes()
        self.manifest_path.write_bytes(raw + b" " * (CHECKER.MAX_MANIFEST_BYTES - len(raw)))
        self.assertEqual(CHECKER.check(self.root, True)["error_count"], 0)
        self.manifest_path.write_bytes(self.manifest_path.read_bytes() + b" ")
        self.assert_error(CHECKER.check(self.root, True), "manifest_read")
        self.write_note(row, b"x" * (CHECKER.MAX_NOTE_BYTES + 1))
        self.assert_error(self.check(), "note_read")

    def test_changed_inputs_during_open_are_rejected(self):
        note = self.session / self.manifest["assignments"][0]["note"]
        original = os.open
        observed = []
        def mutate(path, *args, **kwargs):
            if Path(path) == note:
                observed.append(path)
                note.write_text(BODY + "Changed during open.\n", encoding="utf-8")
            return original(path, *args, **kwargs)
        with mock.patch.object(CHECKER.os, "open", side_effect=mutate):
            self.assert_error(CHECKER.check(self.root, True), "note_read")
        self.assertEqual(len(observed), 1)

    def test_cli_progress_success_and_strict_failure_are_machine_readable(self):
        command = [sys.executable, str(REPO / CHECKER.SOURCE), "--repo", str(self.root), "--json"]
        for suffix, expected in ((["--allow-incomplete"], 0), ([], 1)):
            result = subprocess.run(command + suffix, text=True, capture_output=True, check=False,
                                    env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
            self.assertEqual(result.returncode, expected, result.stderr)
            self.assertEqual(result.stderr, "")
            self.assertFalse(json.loads(result.stdout)["completion_valid"])
        self.manifest["assignments"][0]["note_sha256"] = "0" * 64
        self.save()
        result = subprocess.run(command + ["--allow-incomplete"], text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 1)
        self.assert_error(json.loads(result.stdout), "note_hash_mismatch")


if __name__ == "__main__":
    unittest.main()
