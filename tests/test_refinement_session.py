#!/usr/bin/env python3
"""Synthetic temporary fixtures only: these records never represent real workers."""

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


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/check_refinement_session.py"
SPEC = importlib.util.spec_from_file_location("refinement_session_checker", TOOL)
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)
SESSION = Path("docs/development/2026-11-14-reference-refinement")
BODY = """This temporary document is a synthetic unit test fixture. Its worker names,
assignment states and acceptance descriptions have no relationship to actual
collaboration dispatch. The paragraphs describe expected checker behavior and do
not claim that any product experiment or physical measurement has occurred.

The input contract contains exactly sixty unique identifiers arranged into ten
logical waves, with six identifiers in each wave. Accepted entries require an
existing Markdown note, a declared digest matching the original bytes, and a
bounded narrative body. A running entry can omit its unfinished evidence. Strict
completion must reject that partial ledger while the explicit progress mode
reports incomplete status. Earlier sessions contribute no entries to this fixture.

Path checks cover traversal, aliases, missing documents, symbolic links and special
files. Numeric checks distinguish integers from booleans and floating values.
Duplicate object members are malformed before record validation begins. Narrative
checks exclude comments and fenced source examples. Reports retain actual input
hashes, declared counts and limitations. These structural assertions cannot prove
dispatch, substantive review, execution, publication, visual equality or instrument
fidelity. Every generated file remains inside a disposable test directory.
"""


class RefinementSessionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="synthetic-refinement-checker-")
        self.addCleanup(temporary.cleanup)
        self.temporary = Path(temporary.name).resolve()
        self.root = self.temporary / "synthetic résumé 音"
        self.session = self.root / SESSION
        (self.session / "notes").mkdir(parents=True)
        self.manifest_path = self.session / "assignments.json"
        # Independently authored fixture, never copied from or written to a real manifest.
        self.manifest = {
            "schema_version": 1, "session": "2026-11-14-reference-refinement",
            "starting_commit": "8bd999efc13e309b932e6ac41d72ceb7b9b80a5f",
            "requested_agents": 60, "requested_waves": 10,
            "concurrency_limit_including_root": 4,
            "counting": "Synthetic test identities only; no actual dispatch is represented.",
            "assignments": [self.make_row(number, number <= 6) for number in range(1, 9)],
        }
        self.save()

    def make_row(self, number, accepted=True):
        wave = (number - 1) // 6 + 1
        row = {"id": f"A{number:02d}", "wave": wave,
               "agent": f"/root/w{wave:02d}_a{number:02d}_synthetic_fixture",
               "status": "accepted" if accepted else "running",
               "scope": "Synthetic fixture validating retained record consistency."}
        if accepted:
            row.update(note=(SESSION / "notes" / f"A{number:02d}-synthetic-fixture.md").as_posix(),
                       result="Synthetic expected outcome, never an actual acceptance report.")
            self.write_note(row)
        return row

    def write_note(self, row, text=BODY):
        raw = text.encode("utf-8") if isinstance(text, str) else text
        (self.root / row["note"]).write_bytes(raw)
        row["note_sha256"] = hashlib.sha256(raw).hexdigest()

    def save(self):
        self.manifest_path.write_text(json.dumps(self.manifest, ensure_ascii=True, indent=2) + "\n",
                                      encoding="utf-8")

    def check(self, in_progress=True):
        self.save()
        return CHECKER.check(self.root, in_progress)

    def complete(self):
        self.manifest["assignments"] = [self.make_row(number) for number in range(1, 61)]

    def assert_error(self, report, code=None):
        self.assertEqual(report["status"], "failed", report)
        self.assertFalse(report["completion_valid"], report)
        self.assertGreater(report["error_count"], 0, report)
        if code:
            self.assertIn(code, {error["code"] for error in report["errors"]}, report["errors"])

    def cli(self, *args):
        return subprocess.run([sys.executable, str(TOOL), "--repo", str(self.root), *args],
                              capture_output=True, text=True, timeout=15, check=False)

    def symlink(self, target, link, directory=False):
        try:
            link.symlink_to(target, target_is_directory=directory)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"runner cannot create this synthetic symlink: {exc}")

    def test_progress_reports_exact_hashes_and_never_mutates_inputs(self):
        before = {path: path.read_bytes() for path in self.session.rglob("*") if path.is_file()}
        report = CHECKER.check(self.root, True)
        self.assertEqual(report["status"], "incomplete", report)
        self.assertTrue(report["record_consistency_valid"])
        self.assertFalse(report["completion_valid"])
        self.assertEqual(report["counts"]["recorded"], 8)
        self.assertEqual(report["counts"]["accepted"], 6)
        self.assertEqual(report["counts"]["running"], 2)
        self.assertEqual(report["counts"]["verified_accepted_notes"], 6)
        self.assertEqual(report["counts"]["distinct_agents"], 8)
        self.assertEqual(report["accepted_waves"], [1])
        self.assertEqual(report["missing_ids"], [f"A{number:02d}" for number in range(9, 61)])
        self.assertEqual(report["manifest"]["sha256"], hashlib.sha256(before[self.manifest_path]).hexdigest())
        self.assertEqual(report["checker"]["sha256"], hashlib.sha256(TOOL.read_bytes()).hexdigest())
        for record in report["checked_notes"]:
            raw = (self.root / record["note"]).read_bytes()
            self.assertEqual(record["bytes"], len(raw))
            self.assertEqual(record["sha256"], hashlib.sha256(raw).hexdigest())
            self.assertTrue(record["sha256_matches"])
        aggregate = json.dumps(report["checked_notes"], sort_keys=True, separators=(",", ":")).encode()
        self.assertEqual(report["checked_notes_sha256"], hashlib.sha256(aggregate).hexdigest())
        for field in ("external_dispatch_attested", "semantic_acceptance_attested", "execution_attested",
                      "visual_fidelity_attested", "product_or_model_readiness_attested"):
            self.assertIs(report[field], False)
        self.assertIn("Retained record consistency only", report["claim"])
        self.assertEqual(before, {path: path.read_bytes() for path in before})

    def test_default_strict_cli_rejects_partial_and_progress_is_explicit(self):
        strict = self.cli()
        self.assertEqual(strict.returncode, 1, strict.stderr)
        report = json.loads(strict.stdout)
        self.assert_error(report, "completion_count")
        self.assert_error(report, "completion_status")
        self.assertTrue(report["record_consistency_valid"])
        progress = self.cli("--in-progress", "--json")
        self.assertEqual(progress.returncode, 0, progress.stderr)
        self.assertEqual(json.loads(progress.stdout)["status"], "incomplete")
        self.assertFalse(json.loads(progress.stdout)["completion_valid"])
        self.assertEqual(progress.stderr, "")

    def test_complete_synthetic_fixture_requires_sixty_unique_accepted_notes(self):
        self.complete()
        report = self.check(False)
        self.assertEqual(report["status"], "passed", report["errors"])
        self.assertTrue(report["completion_valid"])
        self.assertEqual(report["counts"]["verified_accepted_notes"], 60)
        self.assertEqual(report["counts"]["distinct_ids"], 60)
        self.assertEqual(report["counts"]["distinct_agents"], 60)
        self.assertEqual(report["accepted_waves"], list(range(1, 11)))
        self.assertTrue(all(row["recorded"] == row["accepted"] == 6 for row in report["wave_counts"]))
        self.assertEqual(self.cli("--json").returncode, 0)
        progress = self.check(True)
        self.assertFalse(progress["completion_valid"], "progress mode never substitutes for the strict gate")
        self.manifest["assignments"][-1]["status"] = "running"
        self.assert_error(self.check(False), "completion_status")

    def test_other_sessions_unassigned_notes_and_row_order_do_not_add_workers(self):
        historical = self.root / "docs/development/historical"
        historical.mkdir()
        (historical / "assignments.json").write_text('{"accepted":60}', encoding="utf-8")
        (self.session / "notes/A60-unassigned.md").write_text(BODY, encoding="utf-8")
        self.manifest["assignments"].reverse()
        report = self.check()
        self.assertEqual(report["counts"]["recorded"], 8)
        self.assertEqual(report["counts"]["accepted"], 6)
        self.assertFalse(report["completion_valid"])
        self.assertEqual(report["error_count"], 0)
        self.manifest["assignments"] = []
        self.assertEqual(self.check()["counts"]["distinct_agents"], 0)
        self.assert_error(self.check(False), "completion_count")

    def test_exact_manifest_schema_numbers_and_identity(self):
        original = copy.deepcopy(self.manifest)
        mutations = [(key, value) for key in ("schema_version", "requested_agents", "requested_waves",
                                              "concurrency_limit_including_root")
                     for value in (True, False, 1.0, "1", None, 0, 61)]
        mutations += [("session", "2026-11-14-interface-continuation"), ("session", []),
                      ("starting_commit", "8bd999e"), ("starting_commit", "0" * 40),
                      ("assignments", None), ("assignments", {}), ("counting", "TBD")]
        for key, value in mutations:
            with self.subTest(key=key, value=value):
                self.manifest = copy.deepcopy(original)
                self.manifest[key] = value
                self.assert_error(self.check())
        for key in original:
            self.manifest = copy.deepcopy(original)
            del self.manifest[key]
            self.assert_error(self.check(), "manifest_fields")
        self.manifest = {**original, "completed": True}
        self.assert_error(self.check(), "manifest_fields")
        self.manifest = original
        self.manifest["assignments"] *= 8
        self.assert_error(self.check(), "assignments_type")

    def test_row_types_required_fields_and_no_planned_placeholders(self):
        original = copy.deepcopy(self.manifest)
        for value in (None, [], True, "worker", {}):
            self.manifest = copy.deepcopy(original)
            self.manifest["assignments"][0] = value
            self.assert_error(self.check())
        for field in original["assignments"][0]:
            self.manifest = copy.deepcopy(original)
            del self.manifest["assignments"][0][field]
            self.assert_error(self.check(), "row_fields")
        for value in (None, True, [], {}, "planned", "complete", "ACCEPTED", "pending"):
            self.manifest = copy.deepcopy(original)
            self.manifest["assignments"][0]["status"] = value
            self.assert_error(self.check(), "status_invalid")
        self.manifest = copy.deepcopy(original)
        self.manifest["assignments"][0]["extra"] = 1
        self.assert_error(self.check(), "row_fields")

    def test_ids_waves_names_duplicates_and_mismatches_are_rejected(self):
        original = copy.deepcopy(self.manifest)
        mutations = [("id", value) for value in (None, True, 1, [], "A1", "a01", "A00", "A61", "A02")]
        mutations += [("wave", value) for value in (None, True, 1.0, "1", 0, 2, 11)]
        mutations += [("agent", value) for value in (
            None, [], "/root", "/root/w1_a01_worker", "/root/w01_a1_worker", "/root/w02_a01_worker",
            "/root/w01_a02_worker", "/root/w01_a01_", "/root/w01_a01_placeholder_worker",
            "/root/w01_a01_worker\n", "/root/w01_a01_" + "x" * 257)]
        for field, value in mutations:
            with self.subTest(field=field, value=value):
                self.manifest = copy.deepcopy(original)
                self.manifest["assignments"][0][field] = value
                self.assert_error(self.check())
        for field, code in (("id", "id_duplicate"), ("agent", "agent_duplicate"), ("note", "note_duplicate")):
            self.manifest = copy.deepcopy(original)
            self.manifest["assignments"][1][field] = self.manifest["assignments"][0][field]
            self.assert_error(self.check(), code)

    def test_text_and_hash_types_are_bounded_and_not_placeholder_values(self):
        original = copy.deepcopy(self.manifest)
        for field in ("scope", "result"):
            for value in (None, [], True, "", " ", "TBD", "TODO: write this", "[placeholder]",
                          "bad\x00text", "bad\x7ftext", "x" * 8193):
                self.manifest = copy.deepcopy(original)
                self.manifest["assignments"][0][field] = value
                self.assert_error(self.check(), "text_required")
        for value in (None, [], True, "", "0" * 63, "G" * 64, "A" * 64, "0" * 65):
            self.manifest = copy.deepcopy(original)
            self.manifest["assignments"][0]["note_sha256"] = value
            self.assert_error(self.check(), "note_hash")

    def test_duplicate_json_numbers_encoding_and_depth_fail_without_tracebacks(self):
        original = self.manifest_path.read_text(encoding="utf-8")
        texts = ("{", "null", "[]", "true", "[" * 2000 + "]" * 2000, original + "\x7f",
                 original.replace('"schema_version": 1', '"schema_version": 1, "schema_version": 1'),
                 original.replace('"id": "A01"', '"id": "A01", "id": "A01"'),
                 *[original.replace('"wave": 1', f'"wave": {value}', 1)
                   for value in ("NaN", "Infinity", "-Infinity", "1.0", "1e0", "9" * 9000)])
        for text in texts:
            with self.subTest(text=text[:45]):
                self.manifest_path.write_text(text, encoding="utf-8")
                self.assert_error(CHECKER.check(self.root, True))
        self.manifest_path.write_bytes(b"\xff")
        self.assert_error(CHECKER.check(self.root, True), "manifest_read")
        self.manifest_path.unlink()
        self.assert_error(CHECKER.check(self.root), "manifest_read")
        self.assert_error(CHECKER.check(self.root / "missing"), "manifest_read")
        self.assert_error(CHECKER.check(None), "manifest_read")
        self.save()
        self.assert_error(CHECKER.check(self.manifest_path), "manifest_read")
        self.assert_error(CHECKER.check(self.root, "true"), "manifest_read")

    def test_note_hash_changes_and_raw_crlf_identity(self):
        row = self.manifest["assignments"][0]
        note = self.root / row["note"]
        note.write_text(BODY + "A synthetic alteration changes retained bytes.\n", encoding="utf-8")
        report = self.check()
        self.assert_error(report, "note_hash_mismatch")
        record = report["checked_notes"][0]
        self.assertFalse(record["sha256_matches"])
        self.assertEqual(record["sha256"], hashlib.sha256(note.read_bytes()).hexdigest())
        self.write_note(row, BODY.replace("\n", "\r\n"))
        self.assertEqual(self.check()["error_count"], 0)

    def test_structural_floor_excludes_code_comments_repetition_and_placeholders(self):
        row = self.manifest["assignments"][0]
        bad = ("", "Evidence. " * 200, "# TODO: fill this evidence\n\n" + BODY,
               "Short prose.\n<!--" + BODY + "-->", "Short prose.\n```text\n" + BODY + "```\n",
               "Short prose.\n~~~~\n" + BODY + "~~~~\n",
               "Short prose.\n" + "\n".join("    " + line for line in BODY.splitlines()))
        for text in bad:
            self.write_note(row, text)
            self.assert_error(self.check(), "note_substance")
        words = BODY.split()
        self.write_note(row, " ".join(words[:99]))
        self.assert_error(self.check(), "note_substance")
        self.write_note(row, " ".join(words[:100]))
        self.assertEqual(self.check()["error_count"], 0)
        for raw in (b"\xff" * 500, (BODY + "\x00").encode(), (BODY + "bare\rcarriage").encode()):
            self.write_note(row, raw)
            self.assert_error(self.check(), "note_read")

    def test_safe_session_note_paths_are_required_in_both_modes(self):
        original = copy.deepcopy(self.manifest)
        unsafe = (None, True, [], "", "../note.md", "/tmp/note.md", "C:/note.md", "a\\b.md",
                  "a/../b.md", "a//b.md", "a/./b.md", "a/b.md/", "a\n.md", "a\x00.md",
                  "a\x7f.md", "x" * 1025, "file:stream", "docs/development/historical/A01.md",
                  (SESSION / "notes/A02-wrong-slot.md").as_posix(),
                  (SESSION / "notes/A01-fixture.txt").as_posix(),
                  (SESSION / "reports/A01-fixture.md").as_posix())
        for index in (0, 6):
            for value in unsafe:
                with self.subTest(index=index, value=value):
                    self.manifest = copy.deepcopy(original)
                    self.manifest["assignments"][index]["note"] = value
                    self.assert_error(self.check(), "note_path")

    def test_missing_accepted_note_and_running_optional_evidence(self):
        row = self.manifest["assignments"][0]
        (self.root / row["note"]).unlink()
        self.assert_error(self.check(), "note_read")
        self.write_note(row)
        running = self.manifest["assignments"][6]
        running["note"] = (SESSION / "notes/A07-unwritten.md").as_posix()
        self.assertEqual(self.check()["error_count"], 0)
        running["note_sha256"] = "0" * 64
        self.assert_error(self.check(), "note_read")
        del running["note"]
        self.assert_error(self.check(), "note_path")

    def test_input_size_limits_are_exact_and_bounded(self):
        row = self.manifest["assignments"][0]
        body = BODY.encode()
        self.write_note(row, body + b" " * (128 * 1024 - len(body)))
        self.save()
        raw = self.manifest_path.read_bytes()
        self.manifest_path.write_bytes(raw + b" " * (256 * 1024 - len(raw)))
        self.assertEqual(CHECKER.check(self.root, True)["error_count"], 0)
        self.manifest_path.write_bytes(self.manifest_path.read_bytes() + b" ")
        self.assert_error(CHECKER.check(self.root, True), "manifest_read")
        self.write_note(row, b"x" * (128 * 1024 + 1))
        self.assert_error(self.check(), "note_read")

    def test_nonregular_files_and_symlink_leaves_cannot_be_evidence(self):
        note = self.root / self.manifest["assignments"][0]["note"]
        for path in (self.manifest_path, note):
            original = path.read_bytes()
            path.unlink()
            path.mkdir()
            self.assert_error(CHECKER.check(self.root, True))
            path.rmdir()
            path.write_bytes(original)
            for outside in (False, True):
                target = (self.temporary if outside else self.root) / "synthetic-target"
                target.write_bytes(original)
                path.unlink()
                self.symlink(target, path)
                self.assert_error(CHECKER.check(self.root, True))
                path.unlink()
                path.write_bytes(original)
                target.unlink()

    @unittest.skipUnless(hasattr(os, "mkfifo"), "runner has no FIFO support")
    def test_fifos_are_rejected_before_open(self):
        for path in (self.manifest_path, self.root / self.manifest["assignments"][0]["note"]):
            original = path.read_bytes()
            path.unlink()
            os.mkfifo(path)
            self.assert_error(CHECKER.check(self.root, True))
            path.unlink()
            path.write_bytes(original)

    def test_symlinked_parent_and_repository_root_are_rejected(self):
        notes = self.session / "notes"
        target = self.temporary / "synthetic-notes"
        notes.rename(target)
        self.symlink(target, notes, directory=True)
        self.assert_error(CHECKER.check(self.root, True), "note_path")
        alias = self.temporary / "synthetic-root-alias"
        self.symlink(self.root, alias, directory=True)
        self.assert_error(CHECKER.check(alias, True), "manifest_read")

    def test_windows_reparse_metadata_rejects_root_parent_and_leaf(self):
        original_lstat = Path.lstat
        for marked in (self.root, self.root / "docs/development", self.session / "notes",
                       self.root / self.manifest["assignments"][0]["note"]):
            observed = []

            def mark(path, *args, **kwargs):
                metadata = original_lstat(path, *args, **kwargs)
                if path == marked:
                    observed.append(path)
                    return SimpleNamespace(st_mode=metadata.st_mode, st_file_attributes=0x400)
                return metadata

            with self.subTest(path=marked), mock.patch.object(Path, "lstat", autospec=True, side_effect=mark):
                self.assert_error(CHECKER.check(self.root, True))
                self.assertTrue(observed)

    def test_changed_file_during_open_and_read_is_rejected(self):
        row = self.manifest["assignments"][0]
        note = self.root / row["note"]
        original_open = os.open
        observed = []

        def mutate_before_open(path, *args, **kwargs):
            if Path(path) == note:
                observed.append(path)
                note.write_text(BODY + "Changed during the synthetic open operation.\n", encoding="utf-8")
            return original_open(path, *args, **kwargs)

        with mock.patch.object(CHECKER.os, "open", side_effect=mutate_before_open):
            self.assert_error(CHECKER.check(self.root, True), "note_read")
        self.assertEqual(len(observed), 1)
        self.write_note(row)
        self.save()
        original_fstat = os.fstat
        expected = note.stat()
        observed.clear()

        def altered_metadata(descriptor):
            metadata = original_fstat(descriptor)
            if os.path.samestat(metadata, expected):
                observed.append(descriptor)
                if len(observed) == 2:
                    return SimpleNamespace(st_dev=metadata.st_dev, st_ino=metadata.st_ino,
                                           st_mode=metadata.st_mode, st_size=metadata.st_size,
                                           st_mtime_ns=metadata.st_mtime_ns + 1,
                                           st_ctime_ns=metadata.st_ctime_ns)
            return metadata

        with mock.patch.object(CHECKER.os, "fstat", side_effect=altered_metadata):
            self.assert_error(CHECKER.check(self.root, True), "note_read")
        self.assertEqual(len(observed), 2)

    def test_fdopen_failure_releases_the_acquired_descriptor(self):
        original_open = os.open
        acquired = []

        def acquire(*args, **kwargs):
            descriptor = original_open(*args, **kwargs)
            acquired.append(descriptor)
            return descriptor

        with mock.patch.object(CHECKER.os, "open", side_effect=acquire), mock.patch.object(
                CHECKER.os, "fdopen", side_effect=OSError("synthetic fdopen failure")):
            self.assert_error(CHECKER.check(self.root, True), "manifest_read")
        self.assertEqual(len(acquired), 1)
        with self.assertRaises(OSError):
            os.fstat(acquired[0])


if __name__ == "__main__":
    unittest.main()
