#!/usr/bin/env python3
"""Independent blackbox checks for gaps in the registration author suite.

Run against the exact root-built binary named by HAMMOND_REGISTRATION_EXECUTABLE.
No builds, injected production switches, timing races, or implicit executable
fallbacks are used. Native writer fault seams retain their separate coverage.
"""

import errno
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


CONTROLS = """B3CONTROLS4
registration_catalog atlas-chapel-nominal-v1 sha256 c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf
expression 0.625
percussion enabled 0 harmonic second volume normal decay slow
pedal drawbars 7 1
manual upper selected B fixed_registration none route_enabled 0
bank A 8 0 6 0 4 0 2 0 0
bank B 0 1 0 3 0 5 0 7 8
manual lower selected A fixed_registration G# route_enabled 1
bank A 1 2 3 4 5 6 7 8 0
bank B 8 0 0 0 0 0 0 0 1
end
"""
ENVELOPE_FIELDS = {"schema", "command", "outcome", "code", "message",
                   "committed", "catalog", "entry", "input", "save", "usage"}
CATALOG_FIELDS = {"status", "complete", "reason", "directory_items",
                  "candidate_count", "invalid_name_count", "invalid_entry_count",
                  "ambiguous_entry_count", "warning_count", "entries"}
ROW_FIELDS = {"key", "name", "scope", "status", "reason"}


def distinct_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON member: {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f"Nonfinite JSON constant: {value}")


class RegistrationCliAdmissionTests(unittest.TestCase):
    calls = 0

    @classmethod
    def setUpClass(cls):
        executable = os.environ.get("HAMMOND_REGISTRATION_EXECUTABLE")
        if not executable or not Path(executable).is_file():
            raise RuntimeError("Set HAMMOND_REGISTRATION_EXECUTABLE to the matching built CLI")
        cls.executable = str(Path(executable).resolve())

    @classmethod
    def tearDownClass(cls):
        print(f"registration CLI independent admission: {cls.calls} subprocess invocations")

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="hammond-cli-admission-")
        self.addCleanup(temporary.cleanup)
        self.work = Path(temporary.name).resolve()
        self.source = self.work / "source"
        self.source.mkdir()
        self.input = self.work / "input.controls"
        self.input.write_bytes(CONTROLS.encode("ascii"))
        self.destination = self.work / "prepared"

    def arguments(self, *arguments):
        return [self.executable, *(os.fspath(value) if isinstance(value, os.PathLike)
                                   else value for value in arguments)]

    def invoke(self, *arguments, expected, code, cwd=None):
        type(self).calls += 1
        completed = subprocess.run(self.arguments(*arguments), cwd=cwd or self.work,
                                   capture_output=True, timeout=15, check=False)
        self.assertEqual(completed.returncode, expected, completed.stdout + completed.stderr)
        self.assertEqual(completed.stderr, b"")
        self.assertTrue(completed.stdout.endswith(b"\n"))
        self.assertEqual(completed.stdout.count(b"\n"), 1)
        self.assertNotIn(b"\r", completed.stdout)
        self.assertLessEqual(len(completed.stdout), 1024 * 1024)
        report = json.loads(completed.stdout.decode("utf-8", errors="strict"),
                            object_pairs_hook=distinct_object, parse_constant=reject_constant)
        self.assertEqual(set(report), ENVELOPE_FIELDS)
        self.assertEqual(report["schema"], "hammond-registration-cli-v1")
        self.assertEqual(report["code"], code)
        self.assertEqual(report["outcome"], {0: "ok", 1: "warning"}.get(expected, "error"))
        self.assertIn(report["command"], (None, "help", "list", "inspect", "import", "materialize"))
        self.assertTrue(report["committed"] is None or type(report["committed"]) is bool)
        self.assert_diagnostics(report)
        self.assert_catalog(report["catalog"])
        if report["entry"] is not None:
            self.assertEqual(set(report["entry"]), ROW_FIELDS | {"canonical_controls"})
        if report["input"] is not None:
            self.assertEqual(set(report["input"]), {"path", "source_version", "source_bytes", "canonical_controls"})
        if report["save"] is not None:
            self.assertEqual(set(report["save"]), {"status", "reason", "key", "scope", "path", "refreshed_catalog"})
            self.assert_catalog(report["save"]["refreshed_catalog"])
        return report

    def assert_diagnostics(self, value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key in ("message", "reason"):
                    self.assertIsInstance(item, str)
                    self.assertLessEqual(len(item.encode("utf-8")), 256)
                self.assert_diagnostics(item)
        elif isinstance(value, list):
            for item in value:
                self.assert_diagnostics(item)

    def assert_catalog(self, catalog):
        if catalog is None:
            return
        self.assertEqual(set(catalog), CATALOG_FIELDS)
        self.assertIs(type(catalog["complete"]), bool)
        for field in ("directory_items", "candidate_count", "invalid_name_count",
                      "invalid_entry_count", "ambiguous_entry_count", "warning_count"):
            self.assertIs(type(catalog[field]), int)
            self.assertGreaterEqual(catalog[field], 0)
        for row in catalog["entries"]:
            self.assertEqual(set(row), ROW_FIELDS)
            self.assertIn(row["scope"], ("registration", "performance"))
        if not catalog["complete"]:
            self.assertEqual(catalog["entries"], [])

    def assert_path(self, value, path):
        encoding = "windows-utf16le-hex" if os.name == "nt" else "posix-bytes-hex"
        native = str(path).encode("utf-16le") if os.name == "nt" else os.fsencode(path)
        self.assertEqual(value, {"encoding": encoding, "value": native.hex()})

    def add_entry(self, name="Selected", scope="performance", content=CONTROLS, root=None):
        path = (root or self.source) / f"{name}.b3{scope}"
        path.write_bytes(content.encode("ascii"))
        return path

    def materialize(self, key="Selected.b3performance", name="Prepared", current=None):
        arguments = ["materialize", "--library", self.source, "--key", key,
                     "--destination", self.destination, "--name", name]
        if current is not None:
            arguments.extend(("--current", current))
        return arguments

    def import_arguments(self, source=None, library=None, name="Imported", scope="performance"):
        return ["import", "--input", source or self.input,
                "--library", library or self.destination, "--name", name, "--scope", scope]

    @unittest.skipIf(os.name == "nt", "POSIX supplies literal argv bytes")
    def test_distinct_malformed_utf8_classes_are_json_usage_errors(self):
        malformed = (b"\x80", b"\xc0\xaf", b"\xe0\x80\xaf", b"\xed\xa0\x80",
                     b"\xf4\x90\x80\x80", b"\xf5\x80\x80\x80", b"\xe2\x82", b"\xe2A\xac")
        for token in malformed:
            for is_command in (False, True):
                with self.subTest(token=token, is_command=is_command):
                    args = [token] if is_command else ["list", "--library", token]
                    report = self.invoke(*args, expected=2, code="UsageError")
                    self.assertEqual(report["command"], None if is_command else "list")
                    self.assertIs(report["committed"], False)
                    for field in ("catalog", "entry", "input", "save", "usage"):
                        self.assertIsNone(report[field])
        self.assertEqual(set(self.work.iterdir()), {self.source, self.input})

    @unittest.skipIf(os.name == "nt", "POSIX overlong component has a stable filesystem refusal")
    def test_multibyte_token_limit_counts_bytes_and_allows_nonascii_controls(self):
        exact = "é" * 2048
        self.assertEqual(len(exact.encode("utf-8")), 4096)
        admitted = self.invoke("list", "--library", exact, expected=4, code="DirectoryUnavailable")
        self.assertIsNotNone(admitted["catalog"])
        rejected = self.invoke("list", "--library", exact + "x", expected=2, code="UsageError")
        self.assertIsNone(rejected["catalog"])
        for character in ("\t", "\r", "\x1f"):
            with self.subTest(character=character):
                self.invoke("list", "--library", "bad" + character, expected=2, code="UsageError")
        # The contract excludes ASCII controls, not every Unicode control codepoint.
        self.invoke("list", "--library", "missing-\u0085", expected=0, code="MissingDirectory")
        self.assertEqual(set(self.work.iterdir()), {self.source, self.input})

    def test_import_option_errors_precede_missing_input_and_directory_creation(self):
        base = self.import_arguments(source=self.work / "absent.controls")
        cases = [base + ["stray"], base + ["--input", self.input],
                 base[:-2] + ["--scope=performance", "ignored"],
                 base[:-2] + ["--sco", "performance"],
                 base[:-1] + [""], base[:-1] + ["--performance"],
                 ["--help", "--library", self.destination]]
        for arguments in cases:
            with self.subTest(arguments=arguments):
                report = self.invoke(*arguments, expected=2, code="UsageError")
                self.assertIs(report["committed"], False)
                self.assertIsNone(report["input"])
                self.assertIsNone(report["save"])
                self.assertFalse(self.destination.exists())

    def test_prefixed_option_shaped_paths_are_admitted_and_reported_exactly(self):
        input_path = self.work / "--input"
        input_path.write_bytes(CONTROLS.encode("ascii"))
        self.invoke(*self.import_arguments(source="--input", library="./--library"),
                    expected=2, code="UsageError")
        self.assertFalse((self.work / "--library").exists())
        report = self.invoke(*self.import_arguments(source="./--input", library="./--library"),
                             expected=0, code="Saved")
        self.assert_path(report["input"]["path"], input_path)
        output = self.work / "--library" / "Imported.b3performance"
        self.assert_path(report["save"]["path"], output)
        self.assertEqual(output.read_bytes(), CONTROLS.encode("ascii"))

    def test_incomplete_catalog_blocks_inspect_and_materialize_before_current_read(self):
        selected = self.add_entry(scope="registration")
        self.destination.mkdir()
        guard = self.destination / "Existing.b3performance"
        guard.write_bytes(b"retain existing bytes\x00\xff")
        for bound in ("candidates", "directory_items"):
            added = []
            count = 128 if bound == "candidates" else 512
            for index in range(count):
                name = f"-invalid{index}.b3performance" if bound == "candidates" else f"ignored{index}"
                path = self.source / name
                path.touch()
                added.append(path)
            for arguments in (["inspect", "--library", self.source, "--key", selected.name],
                              self.materialize(selected.name, current=self.work / "absent.controls")):
                with self.subTest(bound=bound, command=arguments[0]):
                    report = self.invoke(*arguments, expected=3, code="CapacityExceeded")
                    self.assertFalse(report["catalog"]["complete"])
                    self.assertEqual(report["catalog"]["entries"], [])
                    self.assertIsNone(report["entry"])
                    self.assertIsNone(report["input"])
                    self.assertIsNone(report["save"])
                    self.assertIs(report["committed"], False)
                    self.assertEqual(guard.read_bytes(), b"retain existing bytes\x00\xff")
                    self.assertEqual(set(self.destination.iterdir()), {guard})
            for path in added:
                path.unlink()

    def test_scope_option_overrides_input_suffix_and_current_refusal_precedes_read(self):
        misleading = self.work / "Saved.b3performance"
        misleading.write_bytes(CONTROLS.encode("ascii"))
        imported = self.invoke(*self.import_arguments(source=misleading, library=self.source,
                                                      name="Twin", scope="registration"),
                               expected=0, code="Saved")
        self.assertEqual(imported["save"]["key"], "Twin.b3registration")
        self.assertEqual((self.source / "Twin.b3registration").read_bytes(), CONTROLS.encode("ascii"))
        self.add_entry(name="Twin")
        for key, current in (("Twin.b3registration", None),
                             ("Twin.b3performance", self.work / "absent.controls")):
            with self.subTest(key=key):
                report = self.invoke(*self.materialize(key, current=current), expected=2, code="UsageError")
                self.assertEqual(report["catalog"]["ambiguous_entry_count"], 0)
                self.assertEqual(report["entry"]["key"], key)
                self.assertEqual(report["entry"]["canonical_controls"], CONTROLS)
                self.assertIsNone(report["input"])
                self.assertIsNone(report["save"])
                self.assertFalse(self.destination.exists())

    def test_source_warnings_survive_materialize_but_do_not_mask_input_failure(self):
        self.add_entry(scope="registration")
        self.add_entry(name="Broken", content="invalid")
        current_text = CONTROLS.replace("expression 0.625", "expression 0.125").replace("pedal drawbars 7 1", "pedal drawbars 0 8")
        self.input.write_bytes(current_text.encode("ascii"))
        saved = self.invoke(*self.materialize("Selected.b3registration", current=self.input),
                            expected=1, code="Saved")
        self.assertIs(saved["committed"], True)
        self.assertEqual(saved["catalog"]["warning_count"], 1)
        self.assertEqual(saved["save"]["status"], "Saved")
        self.assertEqual(saved["save"]["refreshed_catalog"]["warning_count"], 0)
        output = self.destination / "Prepared.b3performance"
        expected = CONTROLS.replace("expression 0.625", "expression 0.125")
        self.assertEqual(output.read_bytes(), expected.encode("ascii"))
        report = self.invoke(*self.materialize("Selected.b3registration", name="Refused",
                                              current=self.work / "absent.controls"),
                             expected=4, code="InputUnavailable")
        self.assertEqual(report["catalog"]["warning_count"], 1)
        self.assertEqual(report["entry"]["canonical_controls"], CONTROLS)
        self.assertIsNone(report["input"]["canonical_controls"])
        self.assertIsNone(report["save"])
        self.assertIs(report["committed"], False)
        self.assertEqual(set(self.destination.iterdir()), {output})
        self.assertEqual(output.read_bytes(), expected.encode("ascii"))

    @unittest.skipIf(os.name == "nt", "POSIX non-UTF-8/control-byte ancestor reached through a link")
    def test_resolved_link_ancestors_preserve_nonutf8_and_control_path_bytes(self):
        actual = self.work / os.fsdecode(b'ancestor-\xff"\\\n')
        try:
            actual.mkdir()
        except OSError as error:
            if error.errno in (errno.EILSEQ, errno.EINVAL):
                self.skipTest(f"This volume rejects invalid UTF-8 filenames: {error}")
            raise
        (actual / "input.controls").write_bytes(CONTROLS.encode("ascii"))
        alias = self.work / "alias"
        alias.symlink_to(actual, target_is_directory=True)
        report = self.invoke(*self.import_arguments(source=alias / "input.controls", library=alias / "library"),
                             expected=0, code="Saved")
        self.assert_path(report["input"]["path"], actual / "input.controls")
        output = actual / "library" / "Imported.b3performance"
        self.assert_path(report["save"]["path"], output)
        self.assertEqual(output.read_bytes(), CONTROLS.encode("ascii"))

    def test_two_capacity_catalogs_are_complete_in_one_bounded_report(self):
        self.add_entry()
        self.destination.mkdir()
        for index in range(127):
            name = f"Row {index:03} " + "x" * 40
            self.assertEqual(len(name), 48)
            for root in (self.source, self.destination):
                self.add_entry(name=name, content="invalid", root=root)
        report = self.invoke(*self.materialize(), expected=1, code="Saved")
        self.assertIs(report["committed"], True)
        self.assertEqual(report["entry"]["canonical_controls"], CONTROLS)
        for catalog in (report["catalog"], report["save"]["refreshed_catalog"]):
            self.assertTrue(catalog["complete"])
            self.assertEqual(len(catalog["entries"]), 128)
            self.assertEqual(catalog["candidate_count"], 128)
            self.assertEqual(catalog["warning_count"], 127)
        self.assertEqual((self.destination / "Prepared.b3performance").read_bytes(), CONTROLS.encode("ascii"))

    def closed_stdout(self, *arguments):
        read_fd, write_fd = os.pipe()
        os.close(read_fd)
        try:
            type(self).calls += 1
            completed = subprocess.run(self.arguments(*arguments), cwd=self.work,
                                       stdout=write_fd, stderr=subprocess.PIPE,
                                       timeout=15, check=False)
        finally:
            os.close(write_fd)
        self.assertEqual(completed.returncode, 5, completed.stderr)
        self.assertLessEqual(len(completed.stderr), 256)
        self.assertEqual(completed.stderr.count(b"\n"), 1)
        self.assertTrue(completed.stderr.endswith(b"\n"))
        self.assertIn(b"ReportFailed", completed.stderr)
        completed.stderr.decode("utf-8", errors="strict")

    def test_closed_stdout_overrides_precommit_results_and_retains_warning_commit(self):
        self.closed_stdout("--help")
        self.closed_stdout(*self.import_arguments(name="-invalid"))
        self.assertFalse(self.destination.exists())
        selected = self.add_entry()
        self.add_entry(name="Broken", content="invalid")
        self.closed_stdout(*self.materialize())
        output = self.destination / "Prepared.b3performance"
        self.assertEqual(output.read_bytes(), CONTROLS.encode("ascii"))
        # A second closed report cannot turn the create-only collision into a retry.
        self.closed_stdout(*self.materialize())
        self.assertEqual(set(self.destination.iterdir()), {output})
        self.assertEqual(output.read_bytes(), CONTROLS.encode("ascii"))
        self.assertEqual(selected.read_bytes(), CONTROLS.encode("ascii"))
        self.assertEqual(self.input.read_bytes(), CONTROLS.encode("ascii"))


if __name__ == "__main__":
    unittest.main()
