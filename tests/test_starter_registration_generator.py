#!/usr/bin/env python3
"""Exercise the native, create-only starter-pack developer generator.

HAMMOND_STARTER_GENERATOR_EXECUTABLE is required. When supplied,
HAMMOND_REGISTRATION_EXECUTABLE also checks every payload with the native
parser/serializer. HAMMOND_SOURCE_DIR selects the checked-in payload directory.
This suite never reads the independently authored recipe manifest and contains
no duplicate musical recipe table. Separate acceptance owns that comparison.
"""

import json
import os
from pathlib import Path
import signal
import stat
import subprocess
import tempfile
import unittest
import uuid

try:
    import resource
except ImportError:
    resource = None


ROOT = Path(os.environ.get("HAMMOND_SOURCE_DIR", Path(__file__).resolve().parents[1])).resolve()
SCHEMA = "hammond-starter-generator-v1"
REGISTRATION_SUFFIX = ".b3registration"
PERFORMANCE_SUFFIX = ".b3performance"


def required_executable(variable):
    value = os.environ.get(variable)
    if not value:
        raise RuntimeError(f"Set {variable} to a coherently built native executable")
    path = Path(value).resolve()
    if not path.is_file():
        raise RuntimeError(f"Missing configured executable: {path}")
    return path


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate report field: {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f"Nonfinite report value: {value}")


def decode_json(data):
    return json.loads(data.decode("utf-8"), object_pairs_hook=strict_object,
                      parse_constant=reject_constant)


def snapshot(directory):
    """Capture all immediate payload bytes, refusing hidden extra objects."""
    result = {}
    for path in sorted(directory.iterdir()):
        if path.is_symlink() or not path.is_file():
            raise AssertionError(f"Unexpected nonregular output: {path}")
        result[path.name] = path.read_bytes()
    return result


class StarterRegistrationGeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generator = required_executable("HAMMOND_STARTER_GENERATOR_EXECUTABLE")
        cls.registration = (required_executable("HAMMOND_REGISTRATION_EXECUTABLE")
                            if "HAMMOND_REGISTRATION_EXECUTABLE" in os.environ else None)
        cls.workspace = tempfile.TemporaryDirectory(prefix="hammond-starter-generator-")
        cls.workspace_path = Path(cls.workspace.name)
        cls.generated = cls.workspace_path / "baseline generated entries"
        try:
            cls.baseline_run = subprocess.run(
                [str(cls.generator), "--output", str(cls.generated)],
                cwd=cls.workspace_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                timeout=30, check=False)
            if cls.baseline_run.returncode != 0:
                raise RuntimeError(
                    f"Initial generator failed ({cls.baseline_run.returncode}): "
                    f"{cls.baseline_run.stdout!r} {cls.baseline_run.stderr!r}")
            cls.payloads = snapshot(cls.generated)
            cls.baseline_records = [decode_json(line) for line in cls.baseline_run.stdout.splitlines()]
        except BaseException:
            cls.workspace.cleanup()
            raise

    @classmethod
    def tearDownClass(cls):
        cls.workspace.cleanup()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="case-", dir=self.workspace_path)
        self.case = Path(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)

    def run_generator(self, *arguments, cwd=None, **options):
        options.setdefault("stdout", subprocess.PIPE)
        options.setdefault("stderr", subprocess.PIPE)
        return subprocess.run([str(self.generator), *map(str, arguments)],
                              cwd=cwd or self.case, timeout=30, check=False, **options)

    def reports(self, process):
        self.assertIsInstance(process.stdout, bytes)
        self.assertNotIn(b"\r", process.stdout)
        self.assertTrue(process.stdout.endswith(b"\n"), process.stdout)
        records = [decode_json(line) for line in process.stdout.splitlines()]
        self.assertTrue(records)
        for record in records:
            self.assertEqual(record["schema"], SCHEMA)
        self.assertEqual(records[-1]["event"], "summary")
        self.assertEqual(sum(record["event"] == "summary" for record in records), 1)
        return records

    def assert_success(self, process, directory):
        self.assertEqual(process.returncode, 0, (process.stdout, process.stderr))
        self.assertEqual(process.stderr, b"")
        records = self.reports(process)
        self.assertEqual(len(records), 25)
        files, summary = records[:-1], records[-1]
        self.assertEqual(summary["status"], "Complete")
        self.assertEqual(summary["committed_count"], 24)
        self.assertEqual(summary["attempted_count"], 24)
        self.assertEqual(summary["unattempted_count"], 0)
        self.assertIsNone(summary["uncertain_file"])
        for index, record in enumerate(files):
            self.assertEqual(record["event"], "file")
            self.assertEqual(record["status"], "Saved")
            self.assertIs(record["committed"], True)
            self.assertEqual(record["file"].split(" ", 1)[0], f"{index // 2 + 1:02}")
            suffix = REGISTRATION_SUFFIX if index % 2 == 0 else PERFORMANCE_SUFFIX
            self.assertTrue(record["file"].endswith(suffix), record)
            if index % 2:
                self.assertEqual(record["file"][:-len(PERFORMANCE_SUFFIX)],
                                 files[index - 1]["file"][:-len(REGISTRATION_SUFFIX)])
        payloads = snapshot(directory)
        self.assertEqual(sorted(payloads), sorted(record["file"] for record in files))
        self.assertEqual(len(payloads), 24)
        return payloads

    def assert_refused(self, process, status=None):
        self.assertNotEqual(process.returncode, 0, (process.stdout, process.stderr))
        records = self.reports(process)
        self.assertEqual(len(records), 1)
        summary = records[0]
        if status is not None:
            self.assertEqual(summary["status"], status)
        self.assertEqual(summary["committed_count"], 0)
        self.assertEqual(summary["attempted_count"], 0)
        self.assertEqual(summary["unattempted_count"], 24)
        self.assertIsNone(summary["uncertain_file"])

    def test_complete_generation_reports_every_file_in_contract_order(self):
        self.assertEqual(self.assert_success(self.baseline_run, self.generated), self.payloads)

    def test_pairs_have_identical_plain_control_bytes_and_final_lf(self):
        registrations = sorted(name for name in self.payloads if name.endswith(REGISTRATION_SUFFIX))
        self.assertEqual(len(registrations), 12)
        for name in registrations:
            with self.subTest(file=name):
                counterpart = name[:-len(REGISTRATION_SUFFIX)] + PERFORMANCE_SUFFIX
                payload = self.payloads[name]
                self.assertEqual(payload, self.payloads[counterpart])
                self.assertTrue(payload.startswith(b"B3CONTROLS4\n"))
                self.assertTrue(payload.endswith(b"\nend\n"))
                self.assertNotIn(b"\r", payload)
                self.assertLessEqual(len(payload), 16 * 1024)
                payload.decode("ascii")

    def test_help_has_no_filesystem_side_effect(self):
        result = self.run_generator("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(b"--output DIR", result.stdout)
        self.assertIn(b"not atomic", result.stdout)
        self.assertEqual(result.stderr, b"")
        self.assertEqual(list(self.case.iterdir()), [])

    def test_bad_arguments_refuse_without_creating_output(self):
        destination = self.case / "must remain missing"
        cases = [[], ["--output"], ["--unknown"], ["--output", ""],
                 ["--output", str(destination), "extra"],
                 ["--help", "--output", str(destination)],
                 ["--output", "--help"], ["--output", "bad\npath"],
                 ["--output", "x" * 4097], [str(destination)]]
        for arguments in cases:
            with self.subTest(arguments=arguments if len(str(arguments)) < 200 else "oversize"):
                result = self.run_generator(*arguments)
                self.assertNotEqual(result.returncode, 0)
                # run_windows rejects invalid/oversize Unicode before the common
                # parser, using the repository wrapper's stderr diagnostic.
                if result.stdout:
                    self.assert_refused(result, "UsageError")
                else:
                    self.assertEqual(os.name, "nt", result.stderr)
                    self.assertTrue(result.stderr)
                self.assertFalse(destination.exists())
                self.assertEqual(list(self.case.iterdir()), [])

    def test_existing_empty_directory_is_supported(self):
        directory = self.case / "empty staging"
        directory.mkdir()
        actual = self.assert_success(self.run_generator("--output", directory), directory)
        self.assertEqual(actual, self.payloads)

    def test_missing_child_uses_existing_unicode_parent(self):
        parent = self.case / "parent caf\u00e9 \u0394 \u65e5\u672c"
        parent.mkdir()
        directory = parent / "new \u97f3\u8272 entries"
        environment = dict(os.environ, LC_ALL="C")
        result = self.run_generator("--output", directory, env=environment)
        self.assertEqual(self.assert_success(result, directory), self.payloads)
        self.assertEqual(list(parent.iterdir()), [directory])

    def test_relative_output_is_resolved_from_foreign_working_directory(self):
        directory = self.case / "relative staging"
        result = self.run_generator("--output", directory.name, cwd=self.case)
        self.assertEqual(self.assert_success(result, directory), self.payloads)
        self.assertEqual(list(self.case.iterdir()), [directory])

    def test_missing_parent_is_not_created_recursively(self):
        parent = self.case / "missing parent"
        result = self.run_generator("--output", parent / "child")
        self.assert_refused(result, "MissingParent")
        self.assertFalse(parent.exists())
        self.assertEqual(list(self.case.iterdir()), [])

    def test_unrelated_existing_file_refuses_before_any_save(self):
        directory = self.case / "occupied"
        directory.mkdir()
        sentinel = directory / "unrelated.txt"
        sentinel.write_bytes(b"preserve these exact bytes\x00\xff")
        before = snapshot(directory)
        self.assert_refused(self.run_generator("--output", directory), "OutputNotEmpty")
        self.assertEqual(snapshot(directory), before)

    def test_existing_entry_collision_is_preserved_without_retry(self):
        directory = self.case / "collision"
        directory.mkdir()
        name = self.baseline_records[0]["file"]
        (directory / name).write_bytes(b"existing collision is not a control document\n")
        before = snapshot(directory)
        self.assert_refused(self.run_generator("--output", directory), "OutputNotEmpty")
        self.assertEqual(snapshot(directory), before)

    def test_complete_destination_rerun_preserves_all_bytes(self):
        before = snapshot(self.generated)
        self.assert_refused(self.run_generator("--output", self.generated), "OutputNotEmpty")
        self.assertEqual(snapshot(self.generated), before)

    def test_file_destination_is_preserved(self):
        target = self.case / "ordinary file"
        target.write_bytes(b"not a directory\n")
        self.assert_refused(self.run_generator("--output", target), "InvalidOutput")
        self.assertEqual(target.read_bytes(), b"not a directory\n")
        self.assertEqual(list(self.case.iterdir()), [target])

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO destination requires POSIX")
    def test_fifo_destination_refuses_without_blocking(self):
        target = self.case / "fifo"
        os.mkfifo(target)
        self.assert_refused(self.run_generator("--output", target), "InvalidOutput")
        self.assertTrue(stat.S_ISFIFO(target.stat().st_mode))
        self.assertEqual(list(self.case.iterdir()), [target])

    def test_authored_pack_directory_and_entries_are_protected(self):
        pack = ROOT / "data/registrations/starter-v1"
        for target in (pack, pack / "entries"):
            with self.subTest(target=target):
                self.assert_refused(self.run_generator("--output", target), "ProtectedPath")

    def test_empty_child_of_authored_pack_is_protected_before_creation(self):
        target = ROOT / "data/registrations/starter-v1" / ("generator-refusal-" + uuid.uuid4().hex)
        self.assertFalse(target.exists())
        self.assert_refused(self.run_generator("--output", target), "ProtectedPath")
        self.assertFalse(target.exists())

    def test_symlink_alias_of_authored_pack_is_protected(self):
        alias = self.case / "pack alias"
        try:
            alias.symlink_to(ROOT / "data/registrations/starter-v1", target_is_directory=True)
        except (NotImplementedError, OSError) as error:
            self.skipTest(f"Directory symlink is unavailable: {error}")
        target = alias / ("generator-refusal-" + uuid.uuid4().hex)
        self.assert_refused(self.run_generator("--output", target), "ProtectedPath")
        self.assertFalse(target.exists())

    def test_regeneration_matches_every_checked_in_payload_byte(self):
        entries = ROOT / "data/registrations/starter-v1/entries"
        self.assertTrue(entries.is_dir(), "Generate and admit the 24 checked-in payloads before this gate")
        checked_in = snapshot(entries)
        self.assertEqual(len(checked_in), 24)
        self.assertEqual(sorted(checked_in), sorted(self.payloads))
        for name, expected in checked_in.items():
            with self.subTest(file=name):
                self.assertEqual(self.payloads[name], expected)

    def test_native_parser_and_serializer_reproduce_each_generated_file(self):
        if self.registration is None:
            self.skipTest("Optional HAMMOND_REGISTRATION_EXECUTABLE was not supplied")
        listed = subprocess.run([str(self.registration), "list", "--library", str(self.generated)],
                                cwd=self.case, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                timeout=30, check=False)
        self.assertEqual(listed.returncode, 0, (listed.stdout, listed.stderr))
        catalog = decode_json(listed.stdout)["catalog"]
        self.assertTrue(catalog["complete"])
        self.assertEqual(catalog["candidate_count"], 24)
        self.assertEqual(catalog["warning_count"], 0)
        self.assertEqual([entry["key"] for entry in catalog["entries"]],
                         [record["file"] for record in self.baseline_records[:-1]])
        for name, payload in self.payloads.items():
            with self.subTest(file=name):
                result = subprocess.run([str(self.registration), "inspect", "--library", str(self.generated),
                                         "--key", name], cwd=self.case, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, timeout=30, check=False)
                self.assertEqual(result.returncode, 0, (result.stdout, result.stderr))
                report = decode_json(result.stdout)
                self.assertEqual(report["code"], "Valid")
                self.assertEqual(report["entry"]["status"], "Valid")
                self.assertEqual(report["entry"]["key"], name)
                self.assertEqual(report["entry"]["canonical_controls"].encode("ascii"), payload)

    @unittest.skipUnless(resource is not None and hasattr(resource, "RLIMIT_FSIZE") and
                         hasattr(signal, "SIGXFSZ"), "Deterministic file-size failure requires POSIX resource limits")
    def test_partial_write_failure_reports_commits_and_retains_them(self):
        first, second, third = [record["file"] for record in self.baseline_records[:3]]
        limit = len(self.payloads[first])
        self.assertEqual(len(self.payloads[second]), limit)
        self.assertGreater(len(self.payloads[third]), limit,
                           "The observed third payload must exercise the selected file-size boundary")

        def limit_child_files():
            signal.signal(signal.SIGXFSZ, signal.SIG_IGN)
            resource.setrlimit(resource.RLIMIT_FSIZE, (limit, limit))

        directory = self.case / "partial batch"
        result = self.run_generator("--output", directory, preexec_fn=limit_child_files)
        self.assertNotEqual(result.returncode, 0, (result.stdout, result.stderr))
        self.assertEqual(result.stderr, b"")
        records = self.reports(result)
        self.assertEqual(len(records), 4)
        self.assertEqual([record["file"] for record in records[:-1]], [first, second, third])
        self.assertEqual([record["committed"] for record in records[:-1]], [True, True, False])
        self.assertEqual([record["status"] for record in records[:-1]], ["Saved", "Saved", "WriteFailed"])
        summary = records[-1]
        self.assertEqual(summary["status"], "Stopped")
        self.assertEqual(summary["committed_count"], 2)
        self.assertEqual(summary["attempted_count"], 3)
        self.assertEqual(summary["unattempted_count"], 21)
        self.assertIsNone(summary["uncertain_file"])
        retained = {first: self.payloads[first], second: self.payloads[second]}
        self.assertEqual(snapshot(directory), retained)
        self.assert_refused(self.run_generator("--output", directory), "OutputNotEmpty")
        self.assertEqual(snapshot(directory), retained)

    @unittest.skipUnless(os.name == "posix", "Closed-pipe reporting test requires POSIX SIGPIPE semantics")
    def test_broken_report_pipe_stops_after_first_commit(self):
        read_descriptor, write_descriptor = os.pipe()
        os.close(read_descriptor)
        directory = self.case / "closed report pipe"
        try:
            result = self.run_generator("--output", directory, stdout=write_descriptor)
        finally:
            os.close(write_descriptor)
        self.assertEqual(result.returncode, 5, result.stderr)
        self.assertIn(b"ReportFailed", result.stderr)
        self.assertIn(b"committed_count=1", result.stderr)
        self.assertIn(b"attempted_count=1", result.stderr)
        self.assertIn(b"current_publication=committed", result.stderr)
        first = self.baseline_records[0]["file"]
        self.assertIn(first.encode("ascii"), result.stderr)
        self.assertEqual(snapshot(directory), {first: self.payloads[first]})


if __name__ == "__main__":
    unittest.main()
