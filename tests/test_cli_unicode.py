#!/usr/bin/env python3
"""Actual offline CLIs: lossless paths, strict tokens and unchanged publication.

CTest must provide all six executables and their matching compiled profile.
Missing inputs are errors. These cases exercise the native entry points of the
platform running them; a POSIX run does not qualify Windows wmain conversion.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


TOOLS = ("render", "benchmark", "model_info", "parameter_info",
         "console_trace", "pedal_trace")
FILE_TOOLS = ("render", "console_trace", "pedal_trace")
UNICODE_NAME = "caf\u00e9 \u97f3 \U0001f3b9"
SCORE = ("0 pedal_on lower 1 100\n"
         "64 note_on upper 60 100\n"
         "256 pedal_off lower 1 0\n"
         "384 note_off upper 60 0\n")


def without_timings(report):
    result = copy.deepcopy(report)
    for case in result["cases"]:
        for key in ("call_time_ns", "observed_p95_interval_fraction",
                    "observed_max_interval_fraction"):
            del case[key]
    return result


class CliUnicodeTests(unittest.TestCase):
    calls = {tool: 0 for tool in TOOLS}

    @classmethod
    def setUpClass(cls):
        cls.original = {}
        for tool in TOOLS:
            variable = f"HAMMOND_{tool.upper()}_EXECUTABLE"
            path = Path(os.environ.get(variable, ""))
            if not path.is_file():
                raise RuntimeError(f"Missing {variable}; build all six offline CLIs with CTest")
            cls.original[tool] = path.resolve()
        profile = Path(os.environ.get("HAMMOND_TEST_PROFILE", ""))
        if not profile.is_file():
            raise RuntimeError("Missing HAMMOND_TEST_PROFILE; build the matching profile")
        cls.profile_bytes = profile.read_bytes()
        temporary = tempfile.TemporaryDirectory(prefix="hammond-unicode-executables-")
        cls.addClassCleanup(temporary.cleanup)
        directory = Path(temporary.name) / UNICODE_NAME
        directory.mkdir()
        cls.unicode = {}
        for tool, original in cls.original.items():
            suffix = ".exe" if os.name == "nt" else ""
            target = directory / f"hammond_{tool} {UNICODE_NAME}{suffix}"
            shutil.copy2(original, target)
            cls.unicode[tool] = target

    @classmethod
    def tearDownClass(cls):
        print(f"CLI Unicode actual invocations on {os.name}: " +
              ", ".join(f"{tool}={count}" for tool, count in cls.calls.items()))

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="hammond-cli-unicode-")
        self.addCleanup(temporary.cleanup)
        self.work = Path(temporary.name)
        self.directories = {False: self.work / "ascii", True: self.work / UNICODE_NAME}
        self.profiles = {}
        self.scores = {}
        for unicode, directory in self.directories.items():
            directory.mkdir()
            name = UNICODE_NAME if unicode else "ascii"
            self.profiles[unicode] = directory / f"profile {name}.b3p"
            self.scores[unicode] = directory / f"score {name}.events"
            self.profiles[unicode].write_bytes(self.profile_bytes)
            self.scores[unicode].write_text(SCORE, encoding="ascii", newline="\n")
        self.serial = 0

    def paths(self):
        return {path.relative_to(self.work):
                hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
                for path in self.work.rglob("*")}

    def output(self, tool, unicode=True):
        self.serial += 1
        suffix = "wav" if tool == "render" else "csv"
        name = UNICODE_NAME if unicode else "ascii"
        return self.directories[unicode] / f"result {name} {self.serial}.{suffix}"

    def arguments(self, tool, *, unicode=True, output=None, relative=False):
        def path(value):
            return str(value.name if relative else value)

        if tool == "model_info":
            return []
        if tool == "parameter_info":
            return ["--normalized", "0.5"]
        result = ["--profile", path(self.profiles[unicode])]
        if tool == "render":
            result += ["--events", path(self.scores[unicode]), "--frames", "512",
                       "--sample-rate", "48000", "--block-size", "64", "--seed", "37",
                       "--drawbars", "008000000", "--pedal-drawbars", "60"]
        elif tool == "benchmark":
            result += ["--case", "all_keys", "--sample-rate", "48000",
                       "--block-size", "64", "--warmup", "1", "--iterations", "2",
                       "--seed", "37"]
        else:
            result += ["--scenario", "partial" if tool == "console_trace" else "overlap",
                       "--sample-rate", "44100", "--seed", "37"]
        if tool in FILE_TOOLS:
            result += ["--output", path(output)]
        return result

    def invoke(self, tool, arguments, *, unicode=True):
        type(self).calls[tool] += 1
        binary = self.unicode[tool] if unicode else self.original[tool]
        return subprocess.run([str(binary), *map(str, arguments)],
                              cwd=self.directories[unicode], capture_output=True,
                              check=False, timeout=30)

    def successful(self, tool, arguments, *, unicode=True):
        result = self.invoke(tool, arguments, unicode=unicode)
        self.assertEqual(result.returncode, 0, (tool, result.stdout, result.stderr))
        self.assertEqual(result.stderr, b"")
        return result

    def rejected(self, tool, arguments, needle=None):
        before = self.paths()
        result = self.invoke(tool, arguments)
        self.assertEqual(result.returncode, 1, (tool, result.stdout, result.stderr))
        self.assertEqual(result.stdout, b"")
        self.assertTrue(result.stderr.startswith(f"hammond_{tool}: ".encode("ascii")))
        if needle is not None:
            self.assertIn(needle, result.stderr)
        self.assertEqual(self.paths(), before, "Rejection changed inputs or left temporary work")
        return result

    def test_help_from_unicode_executable_and_working_directory(self):
        for tool in TOOLS:
            with self.subTest(tool=tool):
                before = self.paths()
                reference = self.successful(tool, ["--help"], unicode=False)
                actual = self.successful(tool, ["--help"])
                self.assertEqual(actual.stdout, reference.stdout)
                self.assertIn(f"hammond_{tool}".encode("ascii"), actual.stdout)
                self.assertEqual(self.paths(), before)

    def test_renderer_unicode_profile_score_and_output_are_byte_identical(self):
        reference_output = self.output("render", False)
        reference = self.successful("render", self.arguments(
            "render", unicode=False, output=reference_output), unicode=False)
        expected = reference_output.read_bytes()
        self.assertEqual(len(expected), 44 + 512 * 4)
        self.assertNotEqual(expected[44:], b"\0" * (512 * 4))
        for relative in (False, True):
            with self.subTest(relative=relative):
                output = self.output("render")
                before = self.paths()
                actual = self.successful("render", self.arguments(
                    "render", output=output, relative=relative))
                self.assertEqual(actual.stdout, reference.stdout)
                self.assertEqual(output.read_bytes(), expected)
                self.assertEqual(self.paths(), before | {
                    output.relative_to(self.work): hashlib.sha256(expected).hexdigest()})

    def test_both_trace_tools_preserve_csv_bytes_under_unicode_paths(self):
        for tool in ("console_trace", "pedal_trace"):
            reference_output = self.output(tool, False)
            reference = self.successful(tool, self.arguments(
                tool, unicode=False, output=reference_output), unicode=False)
            self.assertEqual(reference.stdout, b"")
            expected = reference_output.read_bytes()
            self.assertGreater(len(expected), 5292)
            data_lines = [line for line in expected.splitlines() if not line.startswith(b"# ")]
            self.assertEqual(len(data_lines), 5293)
            for relative in (False, True):
                with self.subTest(tool=tool, relative=relative):
                    output = self.output(tool)
                    before = self.paths()
                    actual = self.successful(tool, self.arguments(
                        tool, output=output, relative=relative))
                    self.assertEqual(actual.stdout, b"")
                    self.assertEqual(output.read_bytes(), expected)
                    self.assertEqual(self.paths(), before | {
                        output.relative_to(self.work): hashlib.sha256(expected).hexdigest()})

    def test_benchmark_unicode_profile_preserves_all_non_timing_fields(self):
        before = self.paths()
        reference = self.successful("benchmark", self.arguments(
            "benchmark", unicode=False), unicode=False)
        expected = without_timings(json.loads(reference.stdout))
        self.assertRegex(expected["cases"][0]["sample_checksum"], r"^[0-9a-f]{16}$")
        for relative in (False, True):
            with self.subTest(relative=relative):
                actual = self.successful("benchmark", self.arguments(
                    "benchmark", relative=relative))
                self.assertEqual(without_timings(json.loads(actual.stdout)), expected)
                self.assertEqual(self.paths(), before)

    def test_metadata_and_parameter_decimal_boundary_keep_exact_bytes(self):
        for tool, arguments in (("model_info", []), ("parameter_info", []),
                                ("parameter_info", ["--normalized", "0.5"]),
                                ("parameter_info", ["--normalized", "0." + "0" * 126])):
            with self.subTest(tool=tool, arguments=arguments):
                before = self.paths()
                reference = self.successful(tool, arguments, unicode=False)
                actual = self.successful(tool, arguments)
                self.assertEqual(actual.stdout, reference.stdout)
                self.assertTrue(actual.stdout.endswith(b"\n"))
                self.assertNotIn(b"\r", actual.stdout)
                self.assertIsInstance(json.loads(actual.stdout), dict)
                self.assertEqual(self.paths(), before)
        self.rejected("parameter_info", ["--normalized", "0." + "0" * 127], b"128 bytes")

    def test_fullwidth_numbers_and_signs_never_become_ascii(self):
        cases = {
            "render": (("--sample-rate", "\uff148000"), ("--block-size", "\uff164"),
                       ("--frames", "\uff1512"), ("--seed", "\uff137"),
                       ("--drawbars", "00\uff18000000"), ("--pedal-drawbars", "\uff160")),
            "benchmark": (("--sample-rate", "\uff148000"), ("--block-size", "\uff164"),
                          ("--iterations", "\uff12"), ("--warmup", "\uff11"),
                          ("--seed", "\uff137")),
            "console_trace": (("--sample-rate", "\uff144100"), ("--seed", "\uff137")),
            "pedal_trace": (("--sample-rate", "\uff144100"), ("--seed", "\uff137")),
            "parameter_info": (("--normalized", "\uff10.\uff15"),
                               ("--normalized", "\uff0b0.5"),
                               ("--normalized", "\uff0d0.0")),
        }
        for tool, values in cases.items():
            for flag, value in values:
                with self.subTest(tool=tool, flag=flag, value=value):
                    arguments = self.arguments(tool, output=self.output(tool))
                    arguments[arguments.index(flag) + 1] = value
                    self.rejected(tool, arguments)

    def test_fullwidth_help_and_enumerations_are_rejected(self):
        for tool in TOOLS:
            with self.subTest(tool=tool):
                self.rejected(tool, ["--\uff48\uff45\uff4c\uff50"])
        for tool, flag, value in (("benchmark", "--case", "\uff41\uff4c\uff4c"),
                                  ("console_trace", "--scenario", "\uff50artial"),
                                  ("pedal_trace", "--scenario", "\uff4fverlap")):
            with self.subTest(tool=tool, flag=flag):
                arguments = self.arguments(tool, output=self.output(tool))
                arguments[arguments.index(flag) + 1] = value
                self.rejected(tool, arguments)

    def test_argument_limits_count_utf8_bytes_and_keep_oversized_diagnostics(self):
        for tool, flag, allowed_error, oversized_error in (
            ("render", "--drawbars", b"exactly nine digits", b"oversized"),
            ("benchmark", "--case", b"Unknown case", b"oversized"),
            ("console_trace", "--scenario", b"Scenario must be", b"1..4096 bytes"),
            ("pedal_trace", "--scenario", b"Scenario must be", b"1..4096 bytes"),
        ):
            for excess in (False, True):
                with self.subTest(tool=tool, excess=excess):
                    value = "\u00e9" * 2048 + ("x" if excess else "")
                    self.assertEqual(len(value.encode("utf-8")), 4096 + int(excess))
                    arguments = self.arguments(tool, output=self.output(tool))
                    arguments[arguments.index(flag) + 1] = value
                    self.rejected(tool, arguments, oversized_error if excess else allowed_error)

    def test_renderer_missing_unicode_path_retains_diagnostic_spelling(self):
        missing = self.directories[True] / f"missing {UNICODE_NAME}.b3p"
        arguments = self.arguments("render", output=self.output("render"))
        arguments[arguments.index("--profile") + 1] = str(missing)
        self.rejected("render", arguments, str(missing).encode("utf-8"))

    def test_existing_unicode_outputs_are_never_overwritten(self):
        for tool in FILE_TOOLS:
            with self.subTest(tool=tool):
                output = self.output(tool)
                output.write_bytes(b"existing output must survive\x00\xff\r\n")
                self.rejected(tool, self.arguments(tool, output=output), b"exist")

    def test_competing_unicode_publishers_leave_one_complete_reference_file(self):
        for tool in FILE_TOOLS:
            with self.subTest(tool=tool):
                reference = self.output(tool, False)
                self.successful(tool, self.arguments(tool, unicode=False, output=reference),
                                unicode=False)
                expected = reference.read_bytes()
                output = self.output(tool)
                arguments = self.arguments(tool, output=output)
                before = self.paths()
                processes = []
                try:
                    for _ in range(2):
                        type(self).calls[tool] += 1
                        processes.append(subprocess.Popen(
                            [str(self.unicode[tool]), *arguments], cwd=self.directories[True],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE))
                    results = [(process, *process.communicate(timeout=30)) for process in processes]
                finally:
                    for process in processes:
                        if process.poll() is None:
                            process.kill()
                        process.communicate()
                self.assertEqual(sorted(process.returncode for process in processes), [0, 1],
                                 [(process.returncode, out, err) for process, out, err in results])
                for process, stdout, stderr in results:
                    if process.returncode == 0:
                        self.assertEqual(stderr, b"")
                        if tool != "render":
                            self.assertEqual(stdout, b"")
                    else:
                        self.assertEqual(stdout, b"")
                        self.assertTrue(stderr.startswith(f"hammond_{tool}: ".encode("ascii")))
                self.assertEqual(output.read_bytes(), expected)
                self.assertEqual(self.paths(), before | {
                    output.relative_to(self.work): hashlib.sha256(expected).hexdigest()})


if __name__ == "__main__":
    unittest.main()
