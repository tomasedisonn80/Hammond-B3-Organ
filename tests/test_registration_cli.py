#!/usr/bin/env python3
"""Author subprocess checks for the offline registration CLI contract.

The root build supplies HAMMOND_REGISTRATION_EXECUTABLE. These checks exercise
actual files and processes; they never build or silently substitute a binary.
Independent race, fault-injection and platform acceptance remain separate.
"""

import errno
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


STATE4 = """B3CONTROLS4
registration_catalog atlas-chapel-nominal-v1 sha256 c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf
expression 0.375
percussion enabled 1 harmonic third volume soft decay fast
pedal drawbars 2 7
manual upper selected A fixed_registration C# route_enabled 0
bank A 0 1 2 3 4 5 6 7 8
bank B 8 7 6 5 4 3 2 1 0
manual lower selected B fixed_registration A route_enabled 1
bank A 1 3 5 7 0 2 4 6 8
bank B 8 6 4 2 0 7 5 3 1
end
"""
ENVELOPE = {"schema", "command", "outcome", "code", "message", "committed",
            "catalog", "entry", "input", "save", "usage"}


def historical_state(version):
    lines = STATE4.splitlines()
    lines[0] = f"B3CONTROLS{version}"
    lines = [line for line in lines if not line.startswith("registration_catalog ")]
    if version == 1:
        lines = [line for line in lines if not line.startswith("percussion ")]
    if version <= 2:
        lines = [line for line in lines if not line.startswith("pedal ")]
    return "\n".join(line.replace(" fixed_registration C#", "")
                     .replace(" fixed_registration A", "") for line in lines) + "\n"


def no_nonfinite(value):
    raise ValueError(f"Nonfinite JSON constant: {value}")


class RegistrationCliTests(unittest.TestCase):
    calls = 0

    @classmethod
    def setUpClass(cls):
        executable = os.environ.get("HAMMOND_REGISTRATION_EXECUTABLE")
        if not executable or not Path(executable).is_file():
            raise RuntimeError("Set HAMMOND_REGISTRATION_EXECUTABLE to the matching built CLI")
        cls.executable = str(Path(executable).resolve())

    @classmethod
    def tearDownClass(cls):
        print(f"registration CLI author suite: {cls.calls} actual subprocess invocations")

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="hammond-registration-cli-")
        self.addCleanup(temporary.cleanup)
        self.work = Path(temporary.name).resolve()
        self.input = self.work / "input.controls"
        self.input.write_bytes(STATE4.encode("ascii"))
        self.library = self.work / "library"

    def invoke(self, *arguments, expected=0, cwd=None):
        type(self).calls += 1
        result = subprocess.run([self.executable, *map(str, arguments)],
                                cwd=cwd or self.work, capture_output=True,
                                check=False, timeout=15)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        self.assertEqual(result.stderr, b"")
        self.assertTrue(result.stdout.endswith(b"\n"))
        self.assertEqual(result.stdout.count(b"\n"), 1)
        self.assertLessEqual(len(result.stdout), 1024 * 1024)
        report = json.loads(result.stdout.decode("utf-8"), parse_constant=no_nonfinite)
        self.assertEqual(set(report), ENVELOPE)
        self.assertEqual(report["schema"], "hammond-registration-cli-v1")
        self.assertEqual(report["outcome"], "ok" if expected == 0 else "warning" if expected == 1 else "error")
        self.assertLessEqual(len(report["message"].encode("utf-8")), 256)
        return report

    def import_input(self, *, name="Example", scope="registration", source=None,
                     library=None, expected=0):
        return self.invoke("import", "--input", source or self.input,
                           "--library", library or self.library, "--name", name,
                           "--scope", scope, expected=expected)

    def assert_path(self, path_report, expected):
        self.assertEqual(set(path_report), {"encoding", "value"})
        if os.name == "nt":
            encoding = "windows-utf16le-hex"
            raw = str(expected).encode("utf-16le")
        else:
            encoding = "posix-bytes-hex"
            raw = os.fsencode(expected)
        self.assertEqual(path_report, {"encoding": encoding, "value": raw.hex()})

    def test_help_and_missing_empty_catalogs_are_read_only(self):
        help_report = self.invoke("--help")
        self.assertEqual(help_report["command"], "help")
        self.assertEqual(help_report["code"], "Help")
        self.assertEqual(len(help_report["usage"]), 5)
        missing = self.invoke("list", "--library", self.library)
        self.assertEqual(missing["code"], "MissingDirectory")
        self.assertTrue(missing["catalog"]["complete"])
        self.assertFalse(self.library.exists())
        self.library.mkdir()
        empty = self.invoke("list", "--library", self.library)
        self.assertEqual(empty["code"], "Empty")
        self.assertEqual(empty["catalog"]["entries"], [])
        self.assertEqual(empty["committed"], False)

    def test_argument_grammar_rejects_before_mutation(self):
        cases = [(), ("unknown",), ("--help", "extra"),
                 ("list",), ("list", "--library"),
                 ("list", "--library", ""), ("list", "--library", "--bad"),
                 ("list", "--library=x", "unused"),
                 ("list", "--lib", "x"),
                 ("list", "--library", "x", "--library", "y"),
                 ("inspect", "--library", "x", "--key", "../Bad.b3registration"),
                 ("inspect", "--library", "x", "--key", "Bad.B3REGISTRATION"),
                 ("list", "--library", "bad\npath"),
                 ("list", "--library", "bad\x7fpath"),
                 ("list", "--library", "x" * 4097),
                 ("list", *(["--library", "x"] * 6)),
                 ("materialize", "--library", "x" * 4096,
                  "--key", "x" * 4096, "--current", "x" * 4096,
                  "--destination", "x" * 4096, "--name", "x" * 4096)]
        if os.name != "nt":
            cases.append(("list", "--library", os.fsdecode(b"bad-\xff")))
        before = set(self.work.iterdir())
        for arguments in cases:
            with self.subTest(arguments=tuple(str(value)[:60] for value in arguments)):
                report = self.invoke(*arguments, expected=2)
                self.assertEqual(report["code"], "UsageError")
                self.assertIs(report["committed"], False)
                self.assertEqual(set(self.work.iterdir()), before)
        for name in ("CON", "LPT1", "-bad", "bad.", "\u97f3", "x" * 49):
            with self.subTest(name=name):
                self.assertEqual(self.import_input(name=name, expected=2)["code"], "UsageError")
        self.assertEqual(self.import_input(scope="Registration", expected=2)["code"], "UsageError")
        self.assertFalse(self.library.exists())

    def test_import_inspect_preserve_every_retained_field(self):
        saved = self.invoke("import", "--scope", "registration", "--name", "Example",
                            "--library", self.library, "--input", self.input)
        self.assertEqual(saved["code"], "Saved")
        self.assertIs(saved["committed"], True)
        self.assertEqual(saved["input"]["canonical_controls"], STATE4)
        self.assertEqual(saved["input"]["source_version"], 4)
        self.assertEqual(saved["input"]["source_bytes"], len(STATE4))
        output = self.library / "Example.b3registration"
        self.assertEqual(output.read_bytes(), STATE4.encode("ascii"))
        self.assert_path(saved["input"]["path"], self.input)
        self.assert_path(saved["save"]["path"], output)
        before = set(self.work.rglob("*"))
        inspected = self.invoke("inspect", "--key", output.name, "--library", self.library)
        self.assertEqual(inspected["entry"]["canonical_controls"], STATE4)
        self.assertEqual(inspected["entry"]["scope"], "registration")
        self.assertIsNone(inspected["input"])
        self.assertIsNone(inspected["save"])
        self.assertEqual(set(self.work.rglob("*")), before)
        absent = self.invoke("inspect", "--library", self.library,
                             "--key", "example.b3registration", expected=3)
        self.assertEqual(absent["code"], "NotFound")
        self.assertIsNone(absent["entry"])

    def test_materialize_both_scopes_and_current_argument_policy(self):
        self.import_input()
        self.import_input(name="Performance", scope="performance")
        current = self.work / "current.controls"
        current.write_text(STATE4.replace("expression 0.375", "expression 0.8125")
                           .replace("pedal drawbars 2 7", "pedal drawbars 8 8"),
                           encoding="ascii", newline="\n")
        destination = self.work / "prepared"
        base = ("materialize", "--library", self.library, "--destination", destination)
        required = self.invoke(*base, "--key", "Example.b3registration", "--name", "Missing", expected=2)
        self.assertEqual(required["code"], "UsageError")
        forbidden = self.invoke(*base, "--key", "Performance.b3performance", "--name", "Extra",
                                "--current", current, expected=2)
        self.assertEqual(forbidden["code"], "UsageError")
        self.assertFalse(destination.exists())
        registration = self.invoke(*base, "--key", "Example.b3registration", "--name", "Registration",
                                   "--current", current)
        self.assertEqual(registration["entry"]["canonical_controls"], STATE4)
        self.assertEqual(registration["save"]["scope"], "performance")
        expected = STATE4.replace("expression 0.375", "expression 0.8125")
        self.assertEqual((destination / "Registration.b3performance").read_text(encoding="ascii"), expected)
        self.invoke(*base, "--key", "Performance.b3performance", "--name", "Performance")
        self.assertEqual((destination / "Performance.b3performance").read_bytes(), STATE4.encode("ascii"))
        for name, canonical in (("Registration", expected), ("Performance", STATE4)):
            loaded = self.invoke("inspect", "--library", destination, "--key", name + ".b3performance")
            self.assertEqual(loaded["entry"]["canonical_controls"], canonical)

    def test_legacy_versions_migrate_only_published_fields(self):
        for version in (1, 2, 3):
            with self.subTest(version=version):
                source = self.work / f"v{version}.controls"
                text = " \t\n" + historical_state(version)
                source.write_bytes(text.encode("ascii"))
                report = self.import_input(source=source, name=f"Version {version}")
                expected = STATE4.replace("fixed_registration C#", "fixed_registration none")
                expected = expected.replace("fixed_registration A", "fixed_registration none")
                if version <= 2:
                    expected = expected.replace("pedal drawbars 2 7", "pedal drawbars 0 0")
                if version == 1:
                    expected = expected.replace("percussion enabled 1 harmonic third volume soft decay fast",
                                                "percussion enabled 0 harmonic second volume normal decay slow")
                self.assertEqual(report["input"]["source_version"], version)
                self.assertEqual(report["input"]["source_bytes"], len(text))
                self.assertEqual(report["input"]["canonical_controls"], expected)
                self.assertEqual((self.library / f"Version {version}.b3registration").read_text(encoding="ascii"), expected)

    def test_payload_refusals_and_inclusive_size_limit(self):
        invalid = ["", "B3CONTROLS9\n", STATE4 + "trailing\n",
                   STATE4.replace("c9f1dd2d", "09f1dd2d"),
                   STATE4.replace("bank A 0 1", "bank A 00 1"),
                   STATE4.replace("expression 0.375", "expression nan")]
        for number, text in enumerate(invalid):
            with self.subTest(number=number):
                source = self.work / f"invalid-{number}.controls"
                source.write_bytes(text.encode("ascii"))
                report = self.import_input(source=source, expected=3)
                self.assertEqual(report["code"], "InvalidPayload")
                self.assertIsNone(report["input"]["canonical_controls"])
                self.assertFalse(self.library.exists())
        source = self.work / "boundary.controls"
        source.write_bytes(STATE4.encode("ascii") + b" " * (16384 - len(STATE4)))
        report = self.import_input(source=source, name="Boundary")
        self.assertEqual(report["input"]["source_bytes"], 16384)
        source.write_bytes(source.read_bytes() + b" ")
        refused = self.import_input(source=source, name="Oversize", expected=3)
        self.assertEqual(refused["code"], "InputTooLarge")
        self.assertFalse((self.library / "Oversize.b3registration").exists())

    def test_catalog_order_warnings_and_invalid_selection(self):
        self.import_input(name="Zulu")
        self.import_input(name="Alpha", scope="performance")
        self.import_input(name="alpha")
        (self.library / "Broken.b3registration").write_text("invalid", encoding="ascii")
        (self.library / "-bad.b3registration").write_text(STATE4, encoding="ascii")
        report = self.invoke("list", "--library", self.library, expected=1)
        catalog = report["catalog"]
        self.assertEqual([entry["key"] for entry in catalog["entries"]],
                         ["alpha.b3registration", "Alpha.b3performance", "Broken.b3registration", "Zulu.b3registration"])
        self.assertEqual(catalog["candidate_count"], 5)
        self.assertEqual(catalog["invalid_name_count"], 1)
        self.assertEqual(catalog["invalid_entry_count"], 1)
        self.assertEqual(catalog["warning_count"], 2)
        invalid = self.invoke("inspect", "--library", self.library, "--key", "Broken.b3registration", expected=3)
        self.assertEqual(invalid["code"], "InvalidPayload")
        self.assertIsNone(invalid["entry"]["canonical_controls"])
        valid = self.invoke("inspect", "--library", self.library, "--key", "Zulu.b3registration", expected=1)
        self.assertEqual(valid["code"], "Valid")
        saved = self.import_input(name="Warning", expected=1)
        self.assertEqual(saved["code"], "Saved")
        self.assertIs(saved["committed"], True)
        self.assertEqual(saved["save"]["refreshed_catalog"]["warning_count"], 2)

    def test_exact_spelling_does_not_bypass_case_ambiguity(self):
        self.library.mkdir()
        first = self.library / "Same.b3registration"
        second = self.library / "same.b3registration"
        first.write_bytes(STATE4.encode("ascii"))
        second.write_bytes(STATE4.encode("ascii"))
        if first.samefile(second):
            self.skipTest("This volume aliases case variants; distinct entries cannot be created")
        report = self.invoke("inspect", "--library", self.library, "--key", "Same.b3registration", expected=3)
        self.assertEqual(report["code"], "Ambiguous")
        self.assertEqual(report["catalog"]["ambiguous_entry_count"], 2)

    def test_catalog_capacity_edges_and_failed_scans_have_no_partial_rows(self):
        self.library.mkdir()
        for index in range(128):
            (self.library / f"Entry {index:03}.b3registration").write_bytes(STATE4.encode("ascii"))
        full = self.invoke("list", "--library", self.library)
        self.assertEqual(len(full["catalog"]["entries"]), 128)
        self.assertEqual(self.import_input(name="Extra", expected=3)["code"], "CapacityExceeded")
        (self.library / "Extra.b3registration").write_bytes(STATE4.encode("ascii"))
        overflow = self.invoke("list", "--library", self.library, expected=3)
        self.assertEqual(overflow["code"], "CapacityExceeded")
        self.assertFalse(overflow["catalog"]["complete"])
        self.assertEqual(overflow["catalog"]["entries"], [])
        items = self.work / "items"
        items.mkdir()
        for index in range(512):
            (items / f"unrelated-{index}").touch()
        edge = self.invoke("list", "--library", items)
        self.assertEqual(edge["catalog"]["directory_items"], 512)
        self.assertEqual(self.import_input(library=items, expected=3)["code"], "CapacityExceeded")
        (items / "one-more").touch()
        self.assertEqual(self.invoke("list", "--library", items, expected=3)["code"], "CapacityExceeded")

    def test_missing_nonregular_roots_and_collisions_preserve_bytes(self):
        missing = self.import_input(source=self.work / "absent.controls", expected=4)
        self.assertEqual(missing["code"], "InputUnavailable")
        directory = self.import_input(source=self.work, expected=3)
        self.assertEqual(directory["code"], "InputNotRegularFile")
        self.assertEqual(self.invoke("list", "--library", self.input, expected=3)["code"], "InvalidRoot")
        self.assertEqual(self.import_input(library=self.work / "missing-parent" / "library", expected=4)["code"], "DirectoryUnavailable")
        self.import_input()
        output = self.library / "Example.b3registration"
        before = output.read_bytes()
        self.input.write_bytes(STATE4.replace("expression 0.375", "expression 0.125").encode("ascii"))
        collision = self.import_input(name="example", expected=3)
        self.assertEqual(collision["code"], "NameExists")
        self.assertFalse(collision["committed"])
        self.assertEqual(output.read_bytes(), before)
        self.assertEqual(set(self.library.iterdir()), {output})

    @unittest.skipIf(os.name == "nt", "POSIX link and FIFO fixture")
    def test_leaf_links_and_fifos_refuse_but_ancestor_links_work(self):
        leaf = self.work / "leaf.controls"
        leaf.symlink_to(self.input)
        self.assertEqual(self.import_input(source=leaf, expected=3)["code"], "InputNotRegularFile")
        fifo = self.work / "fifo.controls"
        os.mkfifo(fifo)
        self.assertEqual(self.import_input(source=fifo, expected=3)["code"], "InputNotRegularFile")
        actual = self.work / "actual"
        actual.mkdir()
        source = actual / "source.controls"
        source.write_bytes(STATE4.encode("ascii"))
        ancestor = self.work / "ancestor"
        ancestor.symlink_to(actual, target_is_directory=True)
        report = self.import_input(source=ancestor / source.name, name="Ancestor")
        self.assert_path(report["input"]["path"], source)

    def test_unicode_and_quote_ancestor_path_reports_are_exact(self):
        folder = self.work / "\u97f3_\u00e9_\U0001f3b9"
        if os.name != "nt":
            folder = folder.with_name(folder.name + '"\\')
        folder.mkdir()
        source = folder / "input.controls"
        source.write_bytes(STATE4.encode("ascii"))
        report = self.import_input(source=source, library=folder / "library")
        self.assert_path(report["input"]["path"], source)
        self.assert_path(report["save"]["path"], folder / "library" / "Example.b3registration")

    @unittest.skipIf(os.name == "nt", "POSIX non-UTF-8 native ancestor")
    def test_non_utf8_cwd_ancestor_uses_native_hex(self):
        folder = self.work / os.fsdecode(b"ancestor-\xff")
        try:
            folder.mkdir()
        except OSError as error:
            if error.errno in (errno.EILSEQ, errno.EINVAL):
                self.skipTest(f"This volume rejects invalid UTF-8 filenames: {error}")
            raise
        (folder / "input.controls").write_bytes(STATE4.encode("ascii"))
        report = self.invoke("import", "--input", "input.controls", "--library", "library",
                             "--name", "Bytes", "--scope", "performance", cwd=folder)
        self.assert_path(report["input"]["path"], folder / "input.controls")
        self.assert_path(report["save"]["path"], folder / "library" / "Bytes.b3performance")

    def test_broken_stdout_returns_report_failed_after_committing(self):
        read_fd, write_fd = os.pipe()
        os.close(read_fd)
        try:
            type(self).calls += 1
            result = subprocess.run([self.executable, "import", "--input", str(self.input),
                                     "--library", str(self.library), "--name", "Committed",
                                     "--scope", "performance"], cwd=self.work,
                                    stdout=write_fd, stderr=subprocess.PIPE, check=False, timeout=15)
        finally:
            os.close(write_fd)
        self.assertEqual(result.returncode, 5, result.stderr)
        self.assertIn(b"ReportFailed", result.stderr)
        self.assertLessEqual(len(result.stderr), 256)
        self.assertEqual(result.stderr.count(b"\n"), 1)
        self.assertEqual((self.library / "Committed.b3performance").read_bytes(), STATE4.encode("ascii"))


if __name__ == "__main__":
    unittest.main()
