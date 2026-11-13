#!/usr/bin/env python3
"""Small retained-record fixtures, independent of the historical 60-note ledger."""

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/check_continuation.py"
SPEC = importlib.util.spec_from_file_location("check_continuation", TOOL)
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


class ContinuationLedgerTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="hammond-continuation-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.session = self.root / "docs/development/2026-11-13-continuation"
        self.session.mkdir(parents=True)
        self.manifest = {
            "schema_version": 1,
            "session": "2026-11-13-continuation",
            "assignments": [
                {"id": slot, "wave": (slot - 1) // 6 + 1,
                 "scope": f"Synthetic assignment {slot}", "status": "planned",
                 "agent": None, "note": None}
                for slot in range(1, 61)
            ],
        }
        self.activate(1)
        self.activate(2, "running")
        self.activate(7)  # Completion need not be contiguous during parallel work.
        self.save()

    def activate(self, slot, status="complete"):
        record = self.manifest["assignments"][slot - 1]
        record.update(status=status, agent=f"/root/w{record['wave']:02d}_a{slot:02d}_fixture",
                      note=f"{slot:02d}-fixture.md")
        (self.session / record["note"]).write_text(
            f"# Assignment {slot:02d} — synthetic check\n\n"
            f"Agent: `{record['agent']}`\n\nRetained fixture outcome.\n", encoding="utf-8"
        )

    def save(self):
        (self.session / "assignments.json").write_text(
            json.dumps(self.manifest, indent=2) + "\n", encoding="utf-8"
        )

    def check(self, **kwargs):
        self.save()
        return CHECKER.check_continuation(self.root, **kwargs)

    def test_progress_counts_do_not_promote_running_note(self):
        report = self.check(expected_complete=2)
        self.assertEqual(report["counts"], {"planned": 57, "running": 1, "complete": 2})
        self.assertEqual(report["dispatched"], 3)
        self.assertEqual(report["numbered_notes"], 3)
        with self.assertRaisesRegex(CHECKER.LedgerError, "expected 3 complete.*found 2"):
            self.check(expected_complete=3)
        with self.assertRaisesRegex(CHECKER.LedgerError, "expected 60 complete.*found 2"):
            self.check(expected_complete=60)

    def test_running_record_can_wait_for_its_note(self):
        (self.session / "02-fixture.md").unlink()
        self.assertEqual(self.check()["numbered_notes"], 2)
        self.manifest["assignments"][1]["note"] = None
        self.assertEqual(self.check()["counts"]["running"], 1)

    def test_missing_complete_note_fails(self):
        (self.session / "01-fixture.md").unlink()
        with self.assertRaisesRegex(CHECKER.LedgerError, "complete assignment 01 is missing"):
            self.check()

    def test_duplicate_and_extra_numbered_notes_fail(self):
        for name, message in (("01-copy.md", "duplicate numbered note"),
                              ("61-extra.md", "extra numbered note"),
                              ("1-short.md", "noncanonical numbered note")):
            with self.subTest(name=name):
                path = self.session / name
                path.write_text("# Not an additional assignment\n", encoding="utf-8")
                with self.assertRaisesRegex(CHECKER.LedgerError, message):
                    self.check()
                path.unlink()

    def test_note_heading_and_owner_must_match_slot(self):
        note = self.session / "01-fixture.md"
        original = note.read_text(encoding="utf-8")
        for source, replacement, message in (
            ("Assignment 01", "Assignment 07", "note heading"),
            ("w01_a01_fixture", "w02_a07_fixture", "matching explicit Agent"),
            ("Agent:", "Reviewer reference:", "matching explicit Agent"),
        ):
            with self.subTest(source=source):
                note.write_text(original.replace(source, replacement), encoding="utf-8")
                with self.assertRaisesRegex(CHECKER.LedgerError, message):
                    self.check()
        for duplicate in ("`/root/w01_a01_fixture`", "w01_a01_fixture"):
            with self.subTest(duplicate=duplicate):
                note.write_text(original + f"\nAgent: {duplicate}\n", encoding="utf-8")
                with self.assertRaisesRegex(CHECKER.LedgerError, "exactly one"):
                    self.check()

    def test_exact_allocation_and_unique_actual_identities(self):
        original = copy.deepcopy(self.manifest)
        for field, value, message in (
            ("id", 1, "unique and ordered"),
            ("wave", 2, "must belong to wave 01"),
            ("agent", "/root/w01_a01_fixture", "duplicate actual agent"),
            ("agent", "/root/w02_a08_fixture", "another wave or slot"),
        ):
            with self.subTest(field=field, value=value):
                self.manifest = copy.deepcopy(original)
                self.manifest["assignments"][1][field] = value
                with self.assertRaisesRegex(CHECKER.LedgerError, message):
                    self.check()
        self.manifest = original
        self.manifest["assignments"].pop()
        with self.assertRaisesRegex(CHECKER.LedgerError, "exactly 60"):
            self.check()

    def test_planned_slots_cannot_claim_agents_or_retained_notes(self):
        record = self.manifest["assignments"][2]
        record["agent"] = "/root/w01_a03_fixture"
        with self.assertRaisesRegex(CHECKER.LedgerError, "planned assignment 03"):
            self.check()
        record["agent"] = None
        (self.session / "03-premature.md").write_text("# Assignment 03\n", encoding="utf-8")
        with self.assertRaisesRegex(CHECKER.LedgerError, "unassigned numbered note"):
            self.check()

    def test_original_sixty_notes_cannot_supply_continuation_credit(self):
        old = self.root / "docs/development/agent-notes"
        old.mkdir()
        for slot in range(1, 61):
            (old / f"{slot:02d}-fixture.md").write_text("original session\n", encoding="utf-8")
        self.assertEqual(self.check()["counts"]["complete"], 2)
        self.assertEqual(self.check()["numbered_notes"], 3)
        (self.session / "01-fixture.md").unlink()
        with self.assertRaisesRegex(CHECKER.LedgerError, "missing retained note"):
            self.check()

    def test_note_paths_cannot_leave_or_rename_the_assigned_slot(self):
        for note in ("../agent-notes/01-fixture.md", "/tmp/01-fixture.md", "07-fixture.md"):
            with self.subTest(note=note):
                self.manifest["assignments"][0]["note"] = note
                with self.assertRaisesRegex(CHECKER.LedgerError, "session-local filename"):
                    self.check()

    def test_bounded_read_and_duplicate_json_fields(self):
        note = self.session / "01-fixture.md"
        note.write_bytes(b"x" * (128 * 1024 + 1))
        with self.assertRaisesRegex(CHECKER.LedgerError, "exceeds byte limit"):
            self.check()
        (self.session / "assignments.json").write_text(
            '{"schema_version":1,"schema_version":1}\n', encoding="utf-8"
        )
        with self.assertRaisesRegex(CHECKER.LedgerError, "duplicate JSON field"):
            CHECKER.check_continuation(self.root)

    def test_explicit_cli_final_gate_and_controlled_failure(self):
        command = [sys.executable, "-B", str(TOOL), "--root", str(self.root),
                   "--expected-complete", "60", "--json"]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["status"], "failed")
        self.assertIn("found 2 complete", result.stdout)
        for slot in range(1, 61):
            self.activate(slot)
        self.save()
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertEqual(json.loads(result.stdout)["counts"],
                         {"planned": 0, "running": 0, "complete": 60})
        (self.session / "assignments.json").write_text("{invalid", encoding="utf-8")
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["status"], "failed")
        self.assertNotIn("Traceback", result.stderr)

    def test_actual_source_archive_records_are_consistent(self):
        result = CHECKER.check_continuation(ROOT)
        self.assertEqual(sum(result["counts"].values()), 60)
        self.assertEqual(result["dispatched"],
                         result["counts"]["complete"] + result["counts"]["running"])


if __name__ == "__main__":
    unittest.main()
