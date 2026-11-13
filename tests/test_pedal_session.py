#!/usr/bin/env python3
"""Independent retained-record fixtures for the current pedal session only."""

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/check_pedal_session.py"
SPEC = importlib.util.spec_from_file_location("check_pedal_session", TOOL)
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)
SESSION = Path("docs/development/2026-11-13-pedals")


class PedalSessionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="hammond-pedal-session-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / "Unicode résumé 音"
        self.session = self.root / SESSION
        self.session.mkdir(parents=True)
        self.manifest = {
            "schema_version": 1,
            "session_id": "2026-11-13-pedals",
            "baseline_commit": "b4fc61ccfcc59724f14fb0cee947ed7bb7142075",
            "requested_agents": 60,
            "requested_waves": 10,
            "assignments": [
                {"assignment": slot, "wave": (slot - 1) // 6 + 1, "state": "planned",
                 "agent": None, "scope": None, "note": None}
                for slot in range(1, 61)
            ],
        }
        self.activate(1)
        self.activate(2, "running")
        self.activate(7)  # A real parallel completion need not be contiguous.
        self.save()

    def activate(self, slot, state="complete", retain=True):
        record = self.manifest["assignments"][slot - 1]
        record.update(state=state, agent=f"/root/w{record['wave']:02d}_a{slot:02d}_fixture",
                      scope=f"Independent synthetic acceptance fixture for slot {slot}",
                      note=f"{slot:02d}-fixture.md")
        if retain:
            (self.session / record["note"]).write_text(
                f"# Assignment {slot:02d} — synthetic retained-record fixture\n\n"
                f"Owner: `{record['agent']}`.\n\n"
                "## Work and evidence\n\n"
                "This synthetic fixture records a declared check and its explicit example outcome.\n\n"
                "## Handoff and limits\n\n"
                "The fixture is only a checker input and does not represent an actual worker.\n",
                encoding="utf-8",
            )

    def save(self):
        (self.session / "assignments.json").write_text(
            json.dumps(self.manifest, indent=2) + "\n", encoding="utf-8"
        )

    def check(self, **kwargs):
        self.save()
        return CHECKER.check_pedal_session(self.root, **kwargs)

    def cli(self, *args):
        return subprocess.run([sys.executable, "-B", str(TOOL), "--repo", str(self.root), *args],
                              capture_output=True, text=True, check=False, timeout=20)

    def test_progress_is_declared_and_never_promoted_by_a_note(self):
        report = self.check(expected_complete=2)
        self.assertEqual(report["counts"], {"complete": 2, "running": 1, "planned": 57})
        self.assertEqual(report["dispatched"], 3)
        self.assertEqual(report["retained_notes"], {"complete": 2, "running": 1})
        self.assertEqual(report["completed_waves"], 0)
        self.assertEqual(report["wave_counts"][0],
                         {"wave": 1, "complete": 1, "running": 1, "planned": 4})
        for expected in (0, 3, 60):
            with self.subTest(expected=expected), self.assertRaisesRegex(
                    CHECKER.LedgerError, f"expected {expected} complete.*found 2 complete"):
                self.check(expected_complete=expected)

    def test_running_notes_can_be_absent_or_unfinished(self):
        path = self.session / "02-fixture.md"
        path.unlink()
        self.assertEqual(self.check()["retained_notes"], {"complete": 2, "running": 0})
        path.write_bytes(b"")
        self.assertEqual(self.check()["counts"]["complete"], 2)
        path.write_text("Partial draft\n", encoding="utf-8")
        self.assertEqual(self.check()["retained_notes"]["running"], 1)
        path.unlink()
        self.manifest["assignments"][1]["note"] = None
        self.assertEqual(self.check()["dispatched"], 3)

    def test_completed_wave_count_and_record_order_are_not_guessed(self):
        for slot in range(1, 7):
            self.activate(slot)
        self.manifest["assignments"].reverse()
        report = self.check(expected_complete=7)
        self.assertEqual(report["completed_waves"], 1)
        self.assertEqual(report["wave_counts"][0],
                         {"wave": 1, "complete": 6, "running": 0, "planned": 0})

    def test_crlf_manifest_notes_and_varied_existing_owner_formats(self):
        variants = (
            ("# 01 - Fixture", "Owner: /root/w01_a01_fixture"),
            ("# Assignment 01: fixture", "**Agent:** `/root/w01_a01_fixture`"),
            ("# Assignment 01: fixture", "- Actual worker: `/root/w01_a01_fixture`."),
            ("# Assignment 01: fixture",
             "- Actual assignment: `1`, wave `1`, agent `/root/w01_a01_fixture`."),
        )
        path = self.session / "01-fixture.md"
        original = path.read_text(encoding="utf-8")
        for title, owner in variants:
            with self.subTest(owner=owner):
                contents = original.splitlines()
                contents[0], contents[2] = title, owner
                # Assignment 02's actual note has ownership before the title.
                contents[0], contents[2] = contents[2], contents[0]
                path.write_bytes(("\r\n".join(contents) + "\r\n").encode("utf-8"))
                self.save()
                manifest = self.session / "assignments.json"
                manifest.write_bytes(manifest.read_text(encoding="utf-8").replace(
                    "\n", "\r\n").encode("utf-8"))
                self.assertEqual(CHECKER.check_pedal_session(self.root)["counts"]["complete"], 2)

    def test_read_only_check_preserves_exact_manifest_and_note_bytes(self):
        self.save()
        paths = list(self.session.iterdir())
        before = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in paths}
        CHECKER.check_pedal_session(self.root)
        result = self.cli("--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual({p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in paths}, before)
        self.assertEqual({p.name for p in self.session.iterdir()}, set(before))

    def test_exact_session_baseline_schema_and_request_counts(self):
        original = copy.deepcopy(self.manifest)
        for field, value, message in (
            ("schema_version", True, "schema_version"),
            ("schema_version", 2, "schema_version"),
            ("session_id", "2026-11-13-continuation", "different session"),
            ("baseline_commit", "0" * 40, "different baseline"),
            ("baseline_commit", "b4fc61c", "different baseline"),
            ("requested_agents", 59, "requested_agents"),
            ("requested_agents", "60", "requested_agents"),
            ("requested_waves", 9, "requested_waves"),
            ("requested_waves", True, "requested_waves"),
        ):
            with self.subTest(field=field, value=value):
                self.manifest = copy.deepcopy(original)
                self.manifest[field] = value
                with self.assertRaisesRegex(CHECKER.LedgerError, message):
                    self.check()
        self.manifest = original
        self.manifest["status"] = "complete"
        with self.assertRaisesRegex(CHECKER.LedgerError, "manifest fields"):
            self.check()

    def test_slots_are_exactly_sixty_unique_in_their_assigned_waves(self):
        original = copy.deepcopy(self.manifest)
        for field, value, message in (
            ("assignment", 1, "duplicate assignment slot"),
            ("assignment", 0, "integer from 1 to 60"),
            ("assignment", 61, "integer from 1 to 60"),
            ("assignment", True, "integer from 1 to 60"),
            ("wave", 2, "must belong to wave 01"),
            ("wave", True, "must belong to wave 01"),
            ("state", "done", "invalid state"),
            ("state", ["complete"], "invalid state"),
        ):
            with self.subTest(field=field, value=value):
                self.manifest = copy.deepcopy(original)
                self.manifest["assignments"][1][field] = value
                with self.assertRaisesRegex(CHECKER.LedgerError, message):
                    self.check()
        self.manifest = copy.deepcopy(original)
        self.manifest["assignments"].pop()
        with self.assertRaisesRegex(CHECKER.LedgerError, "exactly 60"):
            self.check()
        self.manifest = original
        self.manifest["assignments"][0]["status"] = "complete"
        with self.assertRaisesRegex(CHECKER.LedgerError, "assignment fields"):
            self.check()

    def test_dispatched_owners_are_canonical_unique_and_slot_specific(self):
        original = copy.deepcopy(self.manifest)
        for agent, message in (
            (None, "canonical agent"), ("w01_a02_fixture", "canonical agent"),
            ("/root/w01_a02_Fixture", "canonical agent"),
            ("/root/w01_a02_fixture/child", "canonical agent"),
            ("/root/w01_a01_fixture", "duplicate actual agent"),
            ("/root/w02_a08_fixture", "different wave or slot"),
            ("/root/w01_a02_" + "a" * 257, "canonical agent"),
        ):
            with self.subTest(agent=agent):
                self.manifest = copy.deepcopy(original)
                self.manifest["assignments"][1]["agent"] = agent
                with self.assertRaisesRegex(CHECKER.LedgerError, message):
                    self.check()

    def test_planned_slots_cannot_claim_dispatch_scope_or_notes(self):
        for field, value in (("agent", "/root/w01_a03_fixture"),
                             ("scope", "Already implemented"), ("note", "03-fixture.md")):
            with self.subTest(field=field):
                self.manifest["assignments"][2][field] = value
                with self.assertRaisesRegex(CHECKER.LedgerError, "planned assignment 03"):
                    self.check()
                self.manifest["assignments"][2][field] = None
        for value in (None, "", " \t\n", "x" * 1001, " " * 1000 + "x", "hidden\x00claim"):
            with self.subTest(scope=value):
                self.manifest["assignments"][0]["scope"] = value
                with self.assertRaisesRegex(CHECKER.LedgerError, "bounded nonempty scope"):
                    self.check()

    def test_strict_note_paths_cannot_escape_or_change_the_slot(self):
        for note in (None, "../agent-notes/01-fixture.md", "/tmp/01-fixture.md",
                     "C:\\notes\\01-fixture.md", "..\\01-fixture.md", "sub/01-fixture.md",
                     "07-fixture.md", "01-Fixture.md", "01-fixture.md.", "01-fixture.md\n",
                     "01-" + "a" * 160 + ".md"):
            with self.subTest(note=note):
                self.manifest["assignments"][0]["note"] = note
                with self.assertRaisesRegex(CHECKER.LedgerError, "session-local filename"):
                    self.check()

    def test_complete_note_must_exist_and_be_a_regular_file(self):
        path = self.session / "01-fixture.md"
        path.unlink()
        with self.assertRaisesRegex(CHECKER.LedgerError, "complete assignment 01 is missing"):
            self.check()
        path.mkdir()
        with self.assertRaisesRegex(CHECKER.LedgerError, "not a regular"):
            self.check()

    def test_title_canonical_ownership_and_minimum_report_structure(self):
        path = self.session / "01-fixture.md"
        original = path.read_text(encoding="utf-8")
        variants = (
            ("", "note title"),
            (original.replace("Assignment 01", "Assignment 07"), "note title"),
            (original.replace("Owner:", "Reference:"), "canonical owner"),
            (original.replace("w01_a01_fixture", "w02_a07_fixture"), "canonical owner"),
            (original.replace("w01_a01_fixture", "w01_a01_fixture_suffix"), "canonical owner"),
            (original + "\nAgent: `/root/w01_a02_other`.\n", "canonical owner"),
            (original.split("## Work")[0], "two populated narrative sections"),
            (original.split("## Handoff")[0], "two populated narrative sections"),
            (original.split("## Work")[0] + "## Result\n\nTODO\n\n## Next\n\nTBD\n",
             "two populated narrative sections"),
        )
        for contents, message in variants:
            with self.subTest(message=message, contents=contents[:100]):
                path.write_text(contents, encoding="utf-8")
                with self.assertRaisesRegex(CHECKER.LedgerError, message):
                    self.check()

    def test_fenced_examples_do_not_supply_title_owner_or_narrative(self):
        path = self.session / "01-fixture.md"
        original = path.read_text(encoding="utf-8")
        for delimiter in ("```", "~~~~"):
            with self.subTest(delimiter=delimiter):
                path.write_text(f"{delimiter}\n{original}{delimiter}\n", encoding="utf-8")
                with self.assertRaisesRegex(CHECKER.LedgerError, "note title"):
                    self.check()
                owner = "Owner: `/root/w01_a01_fixture`."
                path.write_text(original.replace(owner, f"{delimiter}\n{owner}\n{delimiter}"),
                                encoding="utf-8")
                with self.assertRaisesRegex(CHECKER.LedgerError, "canonical owner"):
                    self.check()

    def test_extra_duplicate_and_unassigned_numbered_notes_reject(self):
        for name, message in (("01-copy.md", "duplicate numbered note|unassigned numbered note"),
                              ("61-extra.md", "extra numbered note"),
                              ("1-short.md", "noncanonical numbered note"),
                              ("03-premature.md", "unassigned numbered note")):
            with self.subTest(name=name):
                path = self.session / name
                path.write_text("This is not another dispatched worker.\n", encoding="utf-8")
                with self.assertRaisesRegex(CHECKER.LedgerError, message):
                    self.check()
                path.unlink()

    def test_both_old_sixty_worker_sessions_cannot_supply_current_credit(self):
        for name in ("agent-notes", "2026-11-13-continuation"):
            old = self.root / "docs/development" / name
            old.mkdir()
            for slot in range(1, 61):
                (old / f"{slot:02d}-fixture.md").write_text(
                    "A historical record that must not count in this session.\n", encoding="utf-8")
        self.assertEqual(self.check()["counts"]["complete"], 2)
        (self.session / "01-fixture.md").unlink()
        with self.assertRaisesRegex(CHECKER.LedgerError, "missing retained note"):
            self.check()

    def test_manifest_and_note_bounds_unicode_and_line_ending_errors(self):
        path = self.session / "01-fixture.md"
        for raw, message in ((b"x" * (128 * 1024 + 1), "exceeds byte limit"),
                             (b"# bad\rline\n", "bare CR"), (b"a\x00b", "NUL")):
            with self.subTest(message=message):
                path.write_bytes(raw)
                with self.assertRaisesRegex(CHECKER.LedgerError, message):
                    self.check()
        path.write_bytes(b"\xff")
        with self.assertRaises(UnicodeError):
            self.check()
        (self.session / "assignments.json").write_bytes(b" " * (64 * 1024 + 1))
        with self.assertRaisesRegex(CHECKER.LedgerError, "exceeds byte limit"):
            CHECKER.check_pedal_session(self.root)

    def test_json_duplicate_fields_floats_nonfinite_and_long_integers_reject(self):
        path = self.session / "assignments.json"
        for raw, message in ((b'{"schema_version":1,"schema_version":1}', "duplicate JSON field"),
                             (b'{"value":NaN}', "non-integer JSON number"),
                             (b'{"value":Infinity}', "non-integer JSON number"),
                             (b'{"value":1.0}', "non-integer JSON number"),
                             (b'{"value":' + b"9" * 5000 + b"}", "integer exceeds")):
            with self.subTest(message=message):
                path.write_bytes(raw)
                with self.assertRaisesRegex(CHECKER.LedgerError, message):
                    CHECKER.check_pedal_session(self.root)

    def test_directory_entry_count_is_bounded(self):
        for index in range(257):
            (self.session / f"unrelated-{index}.txt").touch()
        with self.assertRaisesRegex(CHECKER.LedgerError, "directory exceeds entry limit"):
            self.check()

    def test_native_symlink_notes_and_session_directory_are_not_followed(self):
        original = self.session / "01-fixture.md"
        target = self.root / "outside-note.md"
        target.write_bytes(original.read_bytes())
        original.unlink()
        try:
            original.symlink_to(target)
        except OSError as error:
            self.skipTest(f"native symlink creation is unavailable: {error}")
        with self.assertRaisesRegex(CHECKER.LedgerError, "not a regular"):
            self.check()
        original.unlink()
        original.write_bytes(target.read_bytes())
        moved = self.root / "moved-session"
        self.session.rename(moved)
        self.session.symlink_to(moved, target_is_directory=True)
        with self.assertRaisesRegex(CHECKER.LedgerError, "only real directories"):
            CHECKER.check_pedal_session(self.root)

    def test_cross_api_timestamp_representation_does_not_invent_a_change(self):
        real_fstat = CHECKER.os.fstat

        def descriptor_view(fd):
            actual = real_fstat(fd)
            class DescriptorView:
                def __getattr__(self, name):
                    if name == "st_ctime_ns":
                        return actual.st_ctime_ns + 123456
                    return getattr(actual, name)
            return DescriptorView()

        with mock.patch.object(CHECKER.os, "fstat", side_effect=descriptor_view):
            self.assertEqual(self.check()["counts"]["complete"], 2)

    def test_changed_descriptor_metadata_still_rejects(self):
        real_fstat = CHECKER.os.fstat
        calls = 0

        def changed_descriptor(fd):
            nonlocal calls
            actual = real_fstat(fd)
            calls += 1
            class DescriptorView:
                def __getattr__(self, name):
                    if name == "st_mtime_ns":
                        return actual.st_mtime_ns + calls
                    return getattr(actual, name)
            # Freeze the two distinct views, as a real stat_result does.
            view = DescriptorView()
            view.st_mtime_ns = actual.st_mtime_ns + calls
            return view

        with mock.patch.object(CHECKER.os, "fstat", side_effect=changed_descriptor):
            with self.assertRaisesRegex(CHECKER.LedgerError, "changed while reading"):
                self.check()

    def test_expected_count_argument_and_explicit_full_sixty_gate(self):
        for expected in (-1, 61, True, 2.0, "2"):
            with self.subTest(expected=expected), self.assertRaisesRegex(
                    CHECKER.LedgerError, "integer from 0 to 60"):
                self.check(expected_complete=expected)
        failed = self.cli("--expected-complete", "60", "--json")
        self.assertEqual(failed.returncode, 1)
        self.assertIn("found 2 complete", json.loads(failed.stdout)["error"])
        for slot in range(1, 61):
            self.activate(slot)
        self.save()
        passed = self.cli("--expected-complete", "60", "--json")
        self.assertEqual(passed.returncode, 0, passed.stderr + passed.stdout)
        report = json.loads(passed.stdout)
        self.assertEqual(report["counts"], {"complete": 60, "planned": 0, "running": 0})
        self.assertEqual(report["dispatched"], 60)
        self.assertEqual(report["completed_waves"], 10)
        self.assertEqual(report["retained_notes"], {"complete": 60, "running": 0})

    def test_cli_controlled_failures_have_no_traceback(self):
        manifest = self.session / "assignments.json"
        for raw in (b"{invalid", b"\xff", b"[" * 2000, b'{"value":' + b"8" * 5000 + b"}"):
            with self.subTest(prefix=raw[:20]):
                manifest.write_bytes(raw)
                result = self.cli("--json")
                self.assertEqual(result.returncode, 1, result.stderr)
                report = json.loads(result.stdout)
                self.assertEqual(report["status"], "failed")
                self.assertLessEqual(len(report["error"]), 1000)
                self.assertNotIn("Traceback", result.stderr)
        self.save()
        human = self.cli("--expected-complete", "60")
        self.assertEqual(human.returncode, 1)
        self.assertEqual(human.stdout, "")
        self.assertIn("FAIL 2026-11-13-pedals", human.stderr)
        syntax = self.cli("--expected-complete", "2.0")
        self.assertEqual(syntax.returncode, 2)

    def test_actual_source_archive_records_are_consistent_without_a_final_claim(self):
        report = CHECKER.check_pedal_session(ROOT)
        self.assertEqual(sum(report["counts"].values()), 60)
        self.assertEqual(report["dispatched"], report["counts"]["complete"] + report["counts"]["running"])
        self.assertEqual(report["retained_notes"]["complete"], report["counts"]["complete"])
        self.assertIsNone(report["expected_complete"])


if __name__ == "__main__":
    unittest.main()
