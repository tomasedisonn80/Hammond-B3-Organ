#!/usr/bin/env python3
"""Local-only standard-library tests; all ledgers/notes here are SYNTHETIC.

Fixtures exist only in isolated temporary directories under this reports folder.
No actual assignments, accepted notes, production code or native builds change.
The sixty-record fixture tests checker logic and is never dispatch evidence.
Run: python3 -B docs/development/2026-11-16-console-completion/reports/A40-validator-tests.py
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "check_session.py"
SPEC = importlib.util.spec_from_file_location("console_session_checker", SOURCE)
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


class SyntheticSessionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="A40-synthetic-", dir=SOURCE.parent / "reports")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "synthetic-repository"
        self.directory = self.repo / "docs" / "development" / CHECKER.SESSION
        (self.directory / "notes").mkdir(parents=True)
        self.ledger = self.directory / "assignments.json"
        self.data = {
            "schema_version": 1,
            "session": CHECKER.SESSION,
            "base_commit": CHECKER.BASE_COMMIT,
            "requested_workers": 60,
            "requested_waves": 10,
            "max_concurrent_workers": 3,
            "fixture_kind": "SYNTHETIC CHECKER TEST ONLY; NO WORKER DISPATCH",
            "assignments": [],
        }

    def record(self, number=1, state="accepted"):
        worker = f"A{number:02d}"
        wave = (number - 1) // 6 + 1
        record = {
            "id": worker, "wave": wave, "agent": f"/root/w{wave:02d}_a{number:02d}",
            "task": "SYNTHETIC checker fixture; no actual worker or product evidence",
            "state": state, "note": f"notes/{worker}.md",
        }
        if state == "accepted":
            content = (
                f"# SYNTHETIC CHECKER FIXTURE {worker}\n\n"
                "This temporary note exercises parser, path and content validation only. "
                "It records no dispatch, real review, completed assignment or product result. "
                "The fixture has enough explicit words to exercise the mechanical text floor. "
                "Its bytes are generated solely inside an isolated test directory and are removed "
                "when the test finishes. Sixty such fixtures never establish sixty real workers.\n"
            ).encode("utf-8")
            (self.directory / record["note"]).write_bytes(content)
            record["note_sha256"] = hashlib.sha256(content).hexdigest()
            record["root_review"] = "SYNTHETIC test review, never real root acceptance."
        self.data["assignments"].append(record)
        return record

    def run_check(self, strict=False):
        self.ledger.write_text(json.dumps(self.data, indent=2) + "\n", encoding="utf-8")
        before = self.ledger.read_bytes()
        result = CHECKER.check_session(self.directory, strict=strict)
        self.assertEqual(before, self.ledger.read_bytes(), "checker must not mutate ledger bytes")
        return result

    def assert_refused(self, substring, strict=False):
        result = self.run_check(strict)
        self.assertTrue(result["errors"], result)
        self.assertFalse(result["complete"])
        self.assertIn(substring, "\n".join(result["errors"]))
        return result

    def test_progress_allows_empty_or_incomplete_actual_dispatch(self):
        self.assertEqual([], self.run_check()["errors"])
        self.record()
        self.record(2, "running")
        result = self.run_check()
        self.assertEqual([], result["errors"])
        self.assertEqual((2, 1, 1, 1), tuple(result[key] for key in
                         ("dispatched", "accepted", "running", "accepted_notes_verified")))
        self.assertFalse(result["complete"])
        self.assertFalse((self.directory / "notes/A02.md").exists())
        self.assert_refused("Strict closure", strict=True)

    def test_running_unpinned_partial_note_is_not_accepted(self):
        record = self.record(state="running")
        (self.directory / record["note"]).write_text("Draft", encoding="utf-8")
        result = self.run_check()
        self.assertEqual([], result["errors"])
        self.assertEqual(0, result["accepted_notes_verified"])
        self.assertEqual(0, result["accepted"])

    def test_pinned_running_note_is_checked_without_acceptance(self):
        record = self.record()
        record["state"] = "running"
        result = self.run_check()
        self.assertEqual([], result["errors"])
        self.assertEqual(0, result["accepted"])
        (self.directory / record["note"]).write_text("Changed draft", encoding="utf-8")
        self.assert_refused("SHA-256 mismatch")

    def test_strict_sixty_record_fixture_is_explicitly_synthetic(self):
        for number in range(1, 61):
            self.record(number)
        result = self.run_check(strict=True)
        self.assertEqual([], result["errors"])
        self.assertEqual((60, 60, 60), tuple(result[key] for key in
                         ("dispatched", "accepted", "accepted_notes_verified")))
        self.assertEqual({wave: 6 for wave in range(1, 11)}, result["waves"])
        self.assertTrue(result["complete"])
        self.assertIn("SYNTHETIC", self.data["fixture_kind"])

    def test_strict_sixty_records_still_require_all_acceptances(self):
        for number in range(1, 61):
            self.record(number, "running" if number == 60 else "accepted")
        result = self.assert_refused("Strict closure", strict=True)
        self.assertEqual(59, result["accepted"])

    def test_plans_history_followups_and_old_workers_are_never_counted(self):
        self.record(1)
        for key in ("planned", "queue", "history", "followups", "workers"):
            self.data[key] = [{"id": f"A{number:02d}", "state": "accepted"}
                              for number in range(1, 61)]
        (self.directory / "ROOT_NEXT_QUEUE.md").write_text("60 planned workers", encoding="utf-8")
        result = self.run_check()
        self.assertEqual((1, 1), (result["dispatched"], result["accepted"]))
        self.assert_refused("Strict closure", strict=True)

    def test_record_order_and_optional_owned_paths_are_preserved(self):
        first = self.record(15)
        self.record(14)
        first["owned_paths"] = ["apps/standalone/LibraryModel.h", "notes/A15.md", "reports/example.json"]
        expected = copy.deepcopy(self.data)
        result = self.run_check()
        self.assertEqual([], result["errors"])
        self.assertEqual(["A15", "A14"], result["record_order"])
        self.assertEqual(expected, json.loads(self.ledger.read_text(encoding="utf-8")))

    def test_duplicate_keys_are_rejected_at_root_record_and_ignored_metadata(self):
        self.record()
        valid = json.dumps(self.data)
        payloads = [
            valid.replace('"requested_workers": 60', '"requested_workers": 59, "requested_workers": 60'),
            valid.replace('"id": "A01"', '"id": "A02", "id": "A01"'),
            valid[:-1] + ', "history": {"accepted": false, "accepted": true}}',
        ]
        for payload in payloads:
            with self.subTest(payload=payload[:100]):
                self.ledger.write_text(payload, encoding="utf-8")
                result = CHECKER.check_session(self.directory)
                self.assertIn("duplicate JSON key", "\n".join(result["errors"]))

    def test_bad_json_nonfinite_unicode_and_root_shapes_are_rejected(self):
        for payload in (b"{", b"[]", b"null", b"\xff", b'{"history":NaN}',
                        b'{"history":Infinity}', b'{"history":-Infinity}',
                        b'{"id":1e999}', b'{"history":-1e999}'):
            with self.subTest(payload=payload):
                self.ledger.write_bytes(payload)
                self.assertTrue(CHECKER.check_session(self.directory)["errors"])

    def test_metadata_requires_exact_integer_counts_and_session_identity(self):
        self.record()
        for field, values in {
            "schema_version": [True, 1.0, 2], "requested_workers": [59, 61, "60", True],
            "requested_waves": [9, 11, 10.0], "max_concurrent_workers": [2, 4, "3"],
            "session": ["another-session", None], "base_commit": ["0" * 40, None],
        }.items():
            original = self.data[field]
            for value in values:
                with self.subTest(field=field, value=value):
                    self.data[field] = value
                    self.assert_refused(field)
            self.data[field] = original

    def test_assignment_shapes_are_checked_without_tracebacks(self):
        for value in (None, {}, "workers", True):
            self.data["assignments"] = value
            self.assert_refused("assignments must be an array")
        for value in (None, [], "A01", 1):
            self.data["assignments"] = [value]
            self.assert_refused("record must be an object")

    def test_malformed_ids_and_duplicate_worker_or_agent_are_refused(self):
        record = self.record()
        for value in (None, 1, [], {}, "A1", "A00", "A61", "a01", "A001", "A01 "):
            with self.subTest(value=value):
                record["id"] = value
                self.assert_refused("id must be exactly")
        record["id"] = "A01"
        self.data["assignments"].append(copy.deepcopy(record))
        self.assert_refused("duplicate worker id")
        self.data["assignments"].pop()
        second = self.record(2)
        second["agent"] = record["agent"]
        self.assert_refused("duplicate actual agent identity")

    def test_wave_and_canonical_agent_mapping_are_enforced(self):
        record = self.record(7)
        for value in (0, 11, 2.0, True, "2", None, []):
            record["wave"] = value
            self.assert_refused("wave must be an integer")
        record["wave"] = 1
        self.assert_refused("wave does not match worker id")
        record["wave"] = 2
        for value in ("/root/w01_a07", "/root/w2_a7", "/root/w02_a07/followup", "historic", None, []):
            record["agent"] = value
            self.assert_refused("agent must be")

    def test_undefined_states_tasks_and_review_semantics_are_refused(self):
        record = self.record()
        for value in (None, True, 1, {}, [], "done", "accepted-with-followup", "ACCEPTED", "planned"):
            record["state"] = value
            self.assert_refused("unknown state")
        record["state"] = "accepted"
        for field in ("task", "root_review"):
            original = record.pop(field)
            self.assert_refused(field)
            for value in (None, True, [], "", " \n\t"):
                record[field] = value
                self.assert_refused(field)
            record[field] = original

    def test_four_current_running_records_exceed_declared_limit(self):
        for number in range(1, 5):
            self.record(number, "running")
        self.assert_refused("More than three records")

    def test_note_paths_cannot_escape_alias_or_belong_to_another_worker(self):
        record = self.record()
        for value in (None, [], "", "/tmp/note.md", "../note.md", "notes/../notes/A01.md",
                      "notes//A01.md", "./notes/A01.md", "notes/A02.md", "notes/A01.md/",
                      "C:/notes/A01.md", "notes\\A01.md", "notes/A01.md\x00"):
            with self.subTest(value=value):
                record["note"] = value
                self.assert_refused("note must be exactly")

    def test_owned_paths_remain_optional_but_cannot_carry_bad_paths(self):
        record = self.record()
        for value in (None, "notes/A01.md", ["../escape"], ["/absolute"], ["C:/drive"],
                      ["a\\b"], ["a//b"], ["a/./b"], ["a\x00b"], [True]):
            record["owned_paths"] = value
            self.assert_refused("owned_paths")

    def test_missing_directory_empty_and_non_utf8_final_notes_are_refused(self):
        record = self.record()
        note = self.directory / record["note"]
        note.unlink()
        self.assert_refused("note is missing")
        note.mkdir()
        self.assert_refused("not an ordinary file")
        note.rmdir()
        for payload in (b"", b" " * 1000, b"# Done\n", b"x" * 1000, b"\xff" * 1000):
            note.write_bytes(payload)
            record["note_sha256"] = hashlib.sha256(payload).hexdigest()
            self.assertTrue(self.run_check()["errors"], payload[:20])

    def test_missing_bad_and_changed_hashes_are_refused(self):
        record = self.record()
        digest = record.pop("note_sha256")
        self.assert_refused("note_sha256")
        for value in (None, True, [], "", "g" * 64, digest.upper(), digest[:-1]):
            record["note_sha256"] = value
            self.assert_refused("note_sha256")
        record["note_sha256"] = "0" * 64
        self.assert_refused("SHA-256 mismatch")
        record["note_sha256"] = digest
        with (self.directory / record["note"]).open("ab") as stream:
            stream.write(b"\nChanged after acceptance.\n")
        self.assert_refused("SHA-256 mismatch")

    def test_note_symlink_escape_and_internal_alias_are_refused(self):
        record = self.record()
        note = self.directory / record["note"]
        original = note.read_bytes()
        note.unlink()
        for target in (self.root / "outside-note.md", self.directory / "notes/alias.md"):
            target.write_bytes(original)
            note.symlink_to(target)
            self.assert_refused("symlink")
            note.unlink()
        # A missing running target must not make an escaping symlink acceptable.
        record["state"] = "running"
        record.pop("note_sha256")
        note.symlink_to(self.root / "not-created.md")
        self.assert_refused("symlink")

    def test_notes_directory_symlink_escape_and_ledger_symlink_are_refused(self):
        self.record()
        notes = self.directory / "notes"
        moved = self.root / "outside-notes"
        notes.rename(moved)
        notes.symlink_to(moved, target_is_directory=True)
        self.assert_refused("symlink")
        notes.unlink()
        moved.rename(notes)
        self.run_check()
        target = self.root / "outside-ledger.json"
        self.ledger.rename(target)
        self.ledger.symlink_to(target)
        self.assertIn("must not be a symlink", "\n".join(CHECKER.check_session(self.directory)["errors"]))

    def test_missing_ledger_returns_structured_error(self):
        self.assertIn("Cannot read", "\n".join(CHECKER.check_session(self.directory)["errors"]))

    def test_cli_infers_own_session_from_another_cwd_and_does_not_write(self):
        self.record()
        self.record(2, "running")
        self.run_check()
        script = self.directory / "check_session.py"
        script.write_bytes(SOURCE.read_bytes())
        before = {str(path.relative_to(self.root)): path.read_bytes()
                  for path in self.root.rglob("*") if path.is_file()}
        for arguments, code in (([], 0), (["--strict"], 1)):
            completed = subprocess.run([sys.executable, "-B", str(script), *arguments],
                                       cwd=self.root, capture_output=True, text=True, check=False)
            self.assertEqual(code, completed.returncode, completed.stderr)
            result = json.loads(completed.stdout)
            self.assertEqual(str(self.repo), result["repository"])
            self.assertEqual((2, 1), (result["dispatched"], result["accepted"]))
        after = {str(path.relative_to(self.root)): path.read_bytes()
                 for path in self.root.rglob("*") if path.is_file()}
        self.assertEqual(before, after, "CLI must not create files or modify ledger/notes")


if __name__ == "__main__":
    unittest.main(verbosity=2)
