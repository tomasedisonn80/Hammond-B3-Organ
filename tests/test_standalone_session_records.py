#!/usr/bin/env python3
"""Synthetic retained-record fixtures, not evidence of actual agent dispatch."""

import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/check_standalone_session.py"
SPEC = importlib.util.spec_from_file_location("standalone_session_checker", TOOL)
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


class StandaloneSessionRecordsTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="hammond-standalone-records-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / "résumé 音"
        self.session = self.root / CHECKER.SESSION_PATH
        self.session.mkdir(parents=True)
        # Copy, never link: malformed-PDF fixtures cannot change the supplied source.
        shutil.copyfile(ROOT / CHECKER.SOURCE_PATH, self.root / CHECKER.SOURCE_PATH)
        self.manifest = {
            "schema_version": 1, "session": "2026-11-13-next-phases",
            "baseline_commit": "ba0d9c9c75bd7a39152470f9f7ddb82287cb01b1",
            "requested_assignments": 60, "requested_waves": 10, "concurrency_limit": 3,
            "scope": "Synthetic checker fixture; no actual participant is represented.",
            "assignments": [],
        }
        for number in range(1, 7):
            self.add_record(number)
        self.add_record(7, "running", retain=False)
        self.add_record(8, "blocked", retain=False)
        self.save()

    def add_record(self, number, status="completed", retain=True):
        wave = (number - 1) // 6 + 1
        report = (CHECKER.SESSION_PATH / f"{number:02d}-fixture.md").as_posix()
        record = {"number": number, "wave": wave,
                  "agent": f"/root/w{wave:02d}_a{number:02d}_fixture", "status": status,
                  "report": report, "owned_files": [report, f"future/owned-{number}.cpp"]}
        self.manifest["assignments"].append(record)
        if retain:
            self.write_report(record)
        return record

    def write_report(self, record):
        text = f"Evidence record\n\nActual worker: `{record['agent']}`.\n"
        if record["number"] <= 6:
            first, last = CHECKER.ATLAS_RANGES[record["number"] - 1]
            text += f"Declared PDF pages {first}-{last}; SHA-256 `{CHECKER.SOURCE_SHA256}`.\n"
        (self.root / record["report"]).write_text(text, encoding="utf-8")

    def save(self):
        (self.session / "assignments.json").write_text(
            json.dumps(self.manifest, indent=2) + "\n", encoding="utf-8")

    def check(self, expected_complete=None):
        self.save()
        return CHECKER.check_standalone_session(self.root, expected_complete)

    def cli(self, *args):
        return subprocess.run([sys.executable, "-B", str(TOOL), "--repo", str(self.root), *args],
                              capture_output=True, text=True, timeout=20, check=False)

    def test_progress_counts_retain_blockers_and_all_500_declared_pages(self):
        result = self.check(6)
        self.assertEqual(result["counts"], {"running": 1, "completed": 6, "blocked": 1})
        self.assertEqual((result["dispatched"], result["not_dispatched"]), (8, 52))
        self.assertEqual(result["completed_waves"], 1)
        self.assertEqual(result["retained_atlas_pages"], 500)
        self.assertEqual(result["wave_counts"][1],
                         {"wave": 2, "running": 1, "completed": 0, "blocked": 1,
                          "not_dispatched": 4})
        with self.assertRaisesRegex(CHECKER.SessionRecordError, "expected 60.*found 6"):
            self.check(60)

    def test_final_gate_requires_sixty_distinct_completed_current_records(self):
        for record in self.manifest["assignments"]:
            record["status"] = "completed"
            self.write_report(record)
        for number in range(9, 61):
            self.add_record(number)
        result = self.check(60)
        self.assertEqual(result["completed_waves"], 10)
        self.assertEqual(result["not_dispatched"], 0)
        self.manifest["assignments"][-1]["status"] = "blocked"
        with self.assertRaisesRegex(CHECKER.SessionRecordError, "found 59 completed"):
            self.check(60)

    def test_historical_ledgers_and_unassigned_notes_never_add_participants(self):
        old = self.root / "docs/development/2026-11-13-pedals"
        old.mkdir()
        (old / "assignments.json").write_text('{"completed":60}', encoding="utf-8")
        (self.session / "60-unassigned.md").write_text("Unassigned draft", encoding="utf-8")
        self.assertEqual(self.check()["dispatched"], 8)
        self.manifest["assignments"] = []
        result = self.check(0)
        self.assertEqual(result["dispatched"], 0)
        self.assertEqual(result["retained_atlas_pages"], 0)

    def test_order_gaps_and_running_report_contents_do_not_promote_completion(self):
        self.write_report(self.manifest["assignments"][6])
        self.add_record(14)
        self.manifest["assignments"].reverse()
        result = self.check(7)
        self.assertEqual(result["dispatched"], 9)
        self.assertEqual(result["counts"]["running"], 1)

    def test_exact_schema_session_baseline_and_integer_counts(self):
        original = copy.deepcopy(self.manifest)
        for key, value in (("schema_version", True), ("schema_version", 2),
                           ("session", "2026-11-13-scanner"), ("baseline_commit", "ba0d9c9"),
                           ("requested_assignments", "60"), ("requested_assignments", 59),
                           ("requested_waves", 9), ("concurrency_limit", 4), ("scope", ""),
                           ("scope", None), ("assignments", {})):
            with self.subTest(key=key, value=value):
                self.manifest = copy.deepcopy(original)
                self.manifest[key] = value
                with self.assertRaises(ValueError):
                    self.check()
        for key in ("scope", "surprise"):
            self.manifest = copy.deepcopy(original)
            if key == "scope":
                del self.manifest[key]
            else:
                self.manifest[key] = True
            with self.assertRaisesRegex(CHECKER.SessionRecordError, "manifest fields"):
                self.check()

    def test_malformed_json_duplicate_keys_and_non_integer_numbers(self):
        path = self.session / "assignments.json"
        original = path.read_text(encoding="utf-8")
        cases = ("{", original.replace('"schema_version": 1', '"schema_version": 1, "schema_version": 1'),
                 original.replace('"number": 1', '"number": 1.0', 1),
                 original.replace('"number": 1', '"number": NaN', 1),
                 original.replace('"number": 1', '"number": Infinity', 1))
        for text in cases:
            with self.subTest(text=text[:30]):
                path.write_text(text, encoding="utf-8")
                with self.assertRaises(ValueError):
                    CHECKER.check_standalone_session(self.root)

    def test_numbers_waves_statuses_and_agent_identity_are_structural(self):
        original = copy.deepcopy(self.manifest)
        for key, value in (("number", True), ("number", 0), ("number", 61), ("number", 2),
                           ("wave", True), ("wave", 2), ("status", "planned"),
                           ("status", "complete"), ("status", None), ("agent", None),
                           ("agent", "w01_a01_fixture"), ("agent", "/root/placeholder"),
                           ("agent", "/root/w01_a01_Fixture"),
                           ("agent", "/root/w02_a01_fixture"),
                           ("agent", "/root/w01_a02_fixture")):
            with self.subTest(key=key, value=value):
                self.manifest = copy.deepcopy(original)
                self.manifest["assignments"][0][key] = value
                with self.assertRaises(ValueError):
                    self.check()
        self.manifest = copy.deepcopy(original)
        self.manifest["assignments"][1]["agent"] = original["assignments"][0]["agent"]
        with self.assertRaisesRegex(CHECKER.SessionRecordError, "duplicate agent"):
            self.check()
        self.manifest = copy.deepcopy(original)
        self.manifest["assignments"].append(copy.deepcopy(original["assignments"][0]))
        with self.assertRaisesRegex(CHECKER.SessionRecordError, "duplicate assignment"):
            self.check()

    def test_reports_must_match_this_session_number_and_declared_ownership(self):
        original = copy.deepcopy(self.manifest)
        for value in ("docs/development/2026-11-13-pedals/01-fixture.md",
                      (CHECKER.SESSION_PATH / "02-fixture.md").as_posix(),
                      (CHECKER.SESSION_PATH / "1-fixture.md").as_posix()):
            self.manifest = copy.deepcopy(original)
            self.manifest["assignments"][0]["report"] = value
            with self.assertRaisesRegex(CHECKER.SessionRecordError, "report must be in this session"):
                self.check()
        self.manifest = copy.deepcopy(original)
        self.manifest["assignments"][0]["owned_files"] = ["tools/unrelated.py"]
        with self.assertRaisesRegex(CHECKER.SessionRecordError, "must own its report"):
            self.check()

    def test_unsafe_paths_are_rejected_for_reports_and_owned_files(self):
        original = copy.deepcopy(self.manifest)
        bad_paths = ("", "/tmp/report.md", "../report.md", "a/../report.md", "a/./b",
                     "a//b", "a/", "C:/report.md", "a\\b", "a\x00b", "a\nb", None)
        for value in bad_paths:
            for field in ("report", "owned_files"):
                with self.subTest(value=value, field=field):
                    self.manifest = copy.deepcopy(original)
                    self.manifest["assignments"][0][field] = [value] if field == "owned_files" else value
                    with self.assertRaisesRegex(CHECKER.SessionRecordError, "safe normalized"):
                        self.check()

    def test_duplicate_empty_and_invalid_owned_lists_are_rejected(self):
        original = copy.deepcopy(self.manifest)
        report = original["assignments"][0]["report"]
        for value in ([], None, report, [report, report], [report, {}]):
            with self.subTest(value=value):
                self.manifest = copy.deepcopy(original)
                self.manifest["assignments"][0]["owned_files"] = value
                with self.assertRaises(ValueError):
                    self.check()

    def test_symlinked_reports_parent_paths_and_owned_paths_are_rejected(self):
        record = self.manifest["assignments"][0]
        report = self.root / record["report"]
        target = self.root / "copy.md"
        target.write_bytes(report.read_bytes())
        report.unlink()
        try:
            report.symlink_to(target)
        except OSError as error:
            self.skipTest(f"symlinks unavailable: {error}")
        with self.assertRaisesRegex(CHECKER.SessionRecordError, "must not contain a link"):
            self.check()
        report.unlink()
        report.write_bytes(target.read_bytes())
        (self.root / "linked").symlink_to(self.session, target_is_directory=True)
        record["owned_files"].append("linked/future.cpp")
        with self.assertRaisesRegex(CHECKER.SessionRecordError, "must not contain a link"):
            self.check()
        record["owned_files"].pop()
        docs = self.root / "docs"
        actual_docs = self.root / "actual-docs"
        docs.rename(actual_docs)
        docs.symlink_to(actual_docs, target_is_directory=True)
        with self.assertRaisesRegex(CHECKER.SessionRecordError, "must not contain a link"):
            CHECKER.check_standalone_session(self.root)

    def test_completed_note_requires_exact_narrative_identity_not_a_heading_template(self):
        record = self.manifest["assignments"][0]
        path = self.root / record["report"]
        original = path.read_text(encoding="utf-8")
        for contents in ("", original.replace(record["agent"], record["agent"] + "_extra"),
                         original.replace(record["agent"], "/root/w01_a01_other"),
                         "```text\n" + original + "```\n"):
            with self.subTest(contents=contents[:20]):
                path.write_text(contents, encoding="utf-8")
                with self.assertRaisesRegex(CHECKER.SessionRecordError, "identify its canonical agent"):
                    self.check()
        for heading in ("No heading required", "# Assignment 01: retained note", "# Different editorial title"):
            path.write_bytes((heading + "\r\n" + original.replace("\n", "\r\n")).encode("utf-8"))
            self.assertEqual(self.check()["counts"]["completed"], 6)
        path.unlink()
        with self.assertRaisesRegex(CHECKER.SessionRecordError, "missing its report"):
            self.check()

    def test_atlas_range_and_hash_cannot_be_replaced_with_other_source_claims(self):
        record = self.manifest["assignments"][0]
        path = self.root / record["report"]
        original = path.read_text(encoding="utf-8")
        for contents, error in ((original.replace("1-84", "1-83"), "page range"),
                                (original.replace(CHECKER.SOURCE_SHA256, "0" * 64), "exact source PDF hash")):
            path.write_text(contents, encoding="utf-8")
            with self.assertRaisesRegex(CHECKER.SessionRecordError, error):
                self.check()

    def test_source_pdf_bytes_are_hashed_and_missing_or_changed_source_fails(self):
        pdf = self.root / CHECKER.SOURCE_PATH
        with pdf.open("r+b") as stream:
            stream.write(b"altered")
        with self.assertRaisesRegex(CHECKER.SessionRecordError, "source PDF SHA-256 mismatch"):
            self.check()
        pdf.unlink()
        with self.assertRaises(OSError):
            self.check()

    def test_completion_expectation_type_and_range_are_checked(self):
        for expected in (True, -1, 61, "6", 6.0):
            with self.subTest(expected=expected), self.assertRaisesRegex(
                    CHECKER.SessionRecordError, "expected-complete must be an integer"):
                self.check(expected)

    def test_cli_json_reports_errors_and_preserves_exact_input_bytes_and_mtimes(self):
        paths = [self.session / "assignments.json", *self.session.glob("*-fixture.md")]
        before = {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in paths}
        result = self.cli("--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["counts"]["completed"], 6)
        self.assertEqual({path: (path.read_bytes(), path.stat().st_mtime_ns) for path in paths}, before)
        result = self.cli("--json", "--expected-complete", "60")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["status"], "failed")
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
