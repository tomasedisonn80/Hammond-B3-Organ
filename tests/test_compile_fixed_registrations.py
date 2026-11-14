#!/usr/bin/env python3
"""Frozen native-data admission and atomic-publication acceptance.

Expected taps come from A10's independent source-read PresetTestOracle.h, never
from the production compiler's constants or the authoring catalog. The existing
catalog compiler has its own deeper source-admission suite; these tests exercise
the additional raw identity gate and real native-output publication boundary.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))
import compile_fixed_registrations as compiler


SOURCE_INPUTS = (
    ROOT / "data/registrations/atlas-chapel-nominal-v1.json",
    ROOT / "data/registrations/review-a-chapel.csv",
    ROOT / "data/registrations/review-b-chapel.csv",
)
RAW_INPUTS = tuple(path.read_bytes() for path in SOURCE_INPUTS)
FROZEN_HASH = "c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf"
SENTINEL = b"existing native output must survive\x00\xff\n"
ORACLE_TEXT = (ROOT / "tests/PresetTestOracle.h").read_text(encoding="utf-8")
ORACLE_ROWS = tuple(
    tuple(int(value) for value in row.split(","))
    for row in re.findall(r"\{([0-8](?:,\s*[0-8]){8})\},\s*//", ORACLE_TEXT)
)


class FixedRegistrationCompilerTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="fixed-registration-compiler-")
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.inputs = tuple(self.directory / name for name in ("authoring.json", "a.csv", "b.csv"))
        for path, raw in zip(self.inputs, RAW_INPUTS):
            path.write_bytes(raw)
        self.output = self.directory / "FixedRegistrationData.h"

    def compile(self) -> str:
        return compiler.compile_fixed_registrations(*self.inputs)

    def arguments(self) -> list[str]:
        return ["--input", str(self.inputs[0]), "--review-a", str(self.inputs[1]),
                "--review-b", str(self.inputs[2]), "--output", str(self.output)]

    def cli(self, arguments: list[str] | None = None) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-B", str(TOOLS / "compile_fixed_registrations.py"),
             *(self.arguments() if arguments is None else arguments)],
            capture_output=True, check=False, timeout=10)

    def reject_cli(self, arguments: list[str] | None = None, expected: int = 1) -> bytes:
        self.output.write_bytes(SENTINEL)
        before_inputs = tuple(path.read_bytes() if path.is_file() else None for path in self.inputs)
        before_names = sorted(path.name for path in self.directory.iterdir())
        result = self.cli(arguments)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        self.assertEqual(result.stdout, b"")
        self.assertNotIn(b"Traceback", result.stderr)
        self.assertEqual(self.output.read_bytes(), SENTINEL)
        self.assertEqual(sorted(path.name for path in self.directory.iterdir()), before_names)
        self.assertEqual(tuple(path.read_bytes() if path.is_file() else None for path in self.inputs),
                         before_inputs)
        return result.stderr

    def test_all_eighteen_generated_rows_match_independent_source_oracle(self) -> None:
        self.assertEqual(len(ORACLE_ROWS), 18)
        actual = tuple(
            tuple(int(value) for value in row.split(","))
            for row in re.findall(r"FixedRegistrationPositions\{([0-8](?:, [0-8]){8})\}",
                                  self.compile())
        )
        self.assertEqual(actual, ORACLE_ROWS)
        self.assertEqual(sum(len(row) for row in actual), 162)

    def test_strict_three_input_admission_is_reused_once(self) -> None:
        original = compiler.chapel.compile_chapel_presets
        with mock.patch.object(compiler.chapel, "compile_chapel_presets", wraps=original) as admit:
            text = self.compile()
        admit.assert_called_once_with(*self.inputs)
        self.assertIn("kFixedRegistrationPositions", text)
        self.assertEqual(tuple(path.read_bytes() for path in self.inputs), RAW_INPUTS)
        self.assertFalse(self.output.exists())

    def test_output_has_frozen_raw_identity_and_deterministic_native_storage(self) -> None:
        first = self.compile()
        self.assertEqual(self.compile(), first)
        self.assertEqual(hashlib.sha256(RAW_INPUTS[0]).hexdigest(), FROZEN_HASH)
        self.assertIn('kFixedRegistrationCatalogId = "atlas-chapel-nominal-v1";', first)
        self.assertIn(f'kFixedRegistrationCatalogRawSha256 = "{FROZEN_HASH}";', first)
        canonical = json.dumps(json.loads(RAW_INPUTS[0]), sort_keys=True,
                               separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        self.assertNotEqual(hashlib.sha256(canonical).hexdigest(), FROZEN_HASH)
        self.assertTrue(first.endswith("\n"))
        self.assertNotIn("\r", first)
        self.assertNotIn(str(self.directory), first)
        self.assertLess(len(first.encode("utf-8")), 8192)
        self.assertIn("inline constexpr std::array", first)
        self.assertNotIn("std::vector", first)
        self.assertNotIn("std::string ", first)

    def test_equivalent_authoring_bytes_remain_documentary_valid_but_native_rejects(self) -> None:
        for changed in (
            json.dumps(json.loads(RAW_INPUTS[0]), sort_keys=True, separators=(",", ":")).encode(),
            RAW_INPUTS[0] + b"\n",
            RAW_INPUTS[0].replace(b"\n", b"\r\n"),
        ):
            with self.subTest(sha256=hashlib.sha256(changed).hexdigest()):
                self.inputs[0].write_bytes(changed)
                admitted = json.loads(compiler.chapel.compile_chapel_presets(*self.inputs))
                self.assertEqual(admitted["model_id"], "atlas-chapel-nominal-v1")
                self.assertEqual(len(admitted["registrations"]), 18)
                with self.assertRaisesRegex(compiler.FixedRegistrationCompileError, "authoring raw SHA-256"):
                    self.compile()
                self.assertIn(b"authoring raw SHA-256", self.reject_cli())

    def test_strict_catalog_rejects_changed_taps_identity_and_limitations_first(self) -> None:
        for path, value in (
            (("registrations", 0, "drawbars"), "105320000"),
            (("registrations", 17, "drawbars"), "427866243"),
            (("model_id",), "atlas-chapel-nominal-v2"),
            (("limitations", "loaded_tap_gains"), "measured"),
            (("registrations", 0, "preset_name"), "Invented voice name"),
        ):
            with self.subTest(path=path):
                candidate = json.loads(RAW_INPUTS[0])
                selected = candidate
                for key in path[:-1]:
                    selected = selected[key]
                selected[path[-1]] = value
                self.inputs[0].write_text(json.dumps(candidate), encoding="utf-8")
                error = self.reject_cli()
                self.assertIn(b"authoring", error)
                self.assertNotIn(b"authoring raw SHA-256", error)

    def test_each_review_remains_mandatory_frozen_and_distinct(self) -> None:
        for index in (1, 2):
            for changed in (RAW_INPUTS[index] + b"\n",
                            RAW_INPUTS[index].replace(b"005320000", b"105320000", 1)):
                with self.subTest(index=index, sha256=hashlib.sha256(changed).hexdigest()):
                    self.inputs[index].write_bytes(changed)
                    self.assertIn(b"review", self.reject_cli())
                    self.inputs[index].write_bytes(RAW_INPUTS[index])
            self.inputs[index].unlink()
            self.assertIn(b"cannot read", self.reject_cli())
            self.inputs[index].write_bytes(RAW_INPUTS[index])
        with self.assertRaisesRegex(compiler.FixedRegistrationCompileError, "distinct files"):
            compiler.compile_fixed_registrations(self.inputs[0], self.inputs[1], self.inputs[1])

    def test_invalid_json_and_oversized_input_reject_without_output_mutation(self) -> None:
        compact = json.dumps(json.loads(RAW_INPUTS[0]), separators=(",", ":")).encode()
        candidates = (
            b"", b"\xff", RAW_INPUTS[0][:-5],
            compact.replace(b'"schema_version":1', b'"schema_version":1,"schema_version":1', 1),
            compact.replace(b'"schema_version":1', b'"schema_version":1.0', 1),
            compact.replace(b'"schema_version":1', b'"schema_version":NaN', 1),
            b" " * (64 * 1024 + 1),
        )
        for candidate in candidates:
            with self.subTest(bytes=len(candidate)):
                self.inputs[0].write_bytes(candidate)
                self.assertIn(b"fixed-registration compile error:", self.reject_cli())

    def test_input_symlink_rejects_without_following_it(self) -> None:
        alias = self.directory / "authoring-alias.json"
        try:
            alias.symlink_to(self.inputs[0])
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"symlink creation unavailable: {error}")
        arguments = self.arguments()
        arguments[1] = str(alias)
        self.assertIn(b"nonsymlink regular file", self.reject_cli(arguments))

    def test_successful_cli_replaces_output_without_changing_source_or_old_hardlink(self) -> None:
        self.output.write_bytes(SENTINEL)
        old_link = self.directory / "old-output.h"
        try:
            os.link(self.output, old_link)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"hardlink creation unavailable: {error}")
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout, b"")
        self.assertEqual(result.stderr, b"")
        self.assertEqual(self.output.read_bytes(), self.compile().encode("utf-8"))
        self.assertEqual(old_link.read_bytes(), SENTINEL)
        self.assertFalse(self.output.samefile(old_link))
        self.assertEqual(tuple(path.read_bytes() for path in self.inputs), RAW_INPUTS)
        self.assertFalse(list(self.directory.glob("*.tmp")))

    def test_successful_cli_creates_new_output_with_exact_lf_bytes(self) -> None:
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.output.read_bytes(), self.compile().encode("utf-8"))
        self.assertNotIn(b"\r", self.output.read_bytes())
        self.assertEqual(tuple(path.read_bytes() for path in self.inputs), RAW_INPUTS)

    def test_atomic_publisher_rejects_every_source_as_output(self) -> None:
        text = self.compile()
        for source in self.inputs:
            with self.subTest(source=source.name):
                with self.assertRaisesRegex(compiler.FixedRegistrationCompileError, "alias"):
                    compiler.write_fixed_registrations(source, text, self.inputs)
                self.assertEqual(tuple(path.read_bytes() for path in self.inputs), RAW_INPUTS)

    def test_atomic_publisher_rejects_source_hardlinks(self) -> None:
        text = self.compile()
        for source in self.inputs:
            alias = self.directory / (source.name + ".alias")
            try:
                os.link(source, alias)
            except (OSError, NotImplementedError) as error:
                self.skipTest(f"hardlink creation unavailable: {error}")
            with self.subTest(source=source.name):
                with self.assertRaisesRegex(compiler.FixedRegistrationCompileError, "alias"):
                    compiler.write_fixed_registrations(alias, text, self.inputs)
                self.assertEqual(tuple(path.read_bytes() for path in self.inputs), RAW_INPUTS)

    def test_atomic_publisher_rejects_output_symlinks_directories_and_missing_parent(self) -> None:
        text = self.compile()
        invalid_directory = self.directory / "directory.h"
        invalid_directory.mkdir()
        for destination in (invalid_directory, self.directory / "missing" / "header.h"):
            with self.subTest(destination=destination):
                with self.assertRaises(compiler.FixedRegistrationCompileError):
                    compiler.write_fixed_registrations(destination, text, self.inputs)
        self.output.write_bytes(SENTINEL)
        alias = self.directory / "output-alias.h"
        try:
            alias.symlink_to(self.output)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"symlink creation unavailable: {error}")
        with self.assertRaisesRegex(compiler.FixedRegistrationCompileError, "nonsymlink"):
            compiler.write_fixed_registrations(alias, text, self.inputs)
        self.assertEqual(self.output.read_bytes(), SENTINEL)
        self.assertFalse((self.directory / "missing").exists())

    def test_atomic_publisher_failure_cleans_temporary_and_preserves_previous_output(self) -> None:
        text = self.compile()
        for operation in ("fsync", "replace"):
            with self.subTest(operation=operation):
                self.output.write_bytes(SENTINEL)
                before_names = sorted(path.name for path in self.directory.iterdir())
                with mock.patch.object(compiler.chapel.os, operation,
                                       side_effect=OSError("injected publication failure")) as failure:
                    with self.assertRaisesRegex(compiler.FixedRegistrationCompileError, "injected"):
                        compiler.write_fixed_registrations(self.output, text, self.inputs)
                    failure.assert_called_once()
                self.assertEqual(self.output.read_bytes(), SENTINEL)
                self.assertEqual(sorted(path.name for path in self.directory.iterdir()), before_names)
                self.assertEqual(tuple(path.read_bytes() for path in self.inputs), RAW_INPUTS)

    def test_short_write_never_replaces_output_and_removes_temporary(self) -> None:
        text = self.compile()
        self.output.write_bytes(SENTINEL)
        before_names = sorted(path.name for path in self.directory.iterdir())
        original = compiler.chapel.tempfile.NamedTemporaryFile

        class ShortWrite:
            def __init__(self, *args, **kwargs):
                self.sink = original(*args, **kwargs)
                self.name = self.sink.name

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return self.sink.__exit__(*args)

            def write(self, payload):
                return self.sink.write(payload[:-1])

        with mock.patch.object(compiler.chapel.tempfile, "NamedTemporaryFile", ShortWrite):
            with self.assertRaisesRegex(compiler.FixedRegistrationCompileError, "complete"):
                compiler.write_fixed_registrations(self.output, text, self.inputs)
        self.assertEqual(self.output.read_bytes(), SENTINEL)
        self.assertEqual(sorted(path.name for path in self.directory.iterdir()), before_names)

    def test_publication_rejects_invalid_text_and_missing_input_identities(self) -> None:
        self.output.write_bytes(SENTINEL)
        for text, inputs in ((None, self.inputs), (b"bytes", self.inputs), ("", self.inputs),
                             ("x" * (64 * 1024 + 1), self.inputs),
                             (self.compile(), self.inputs[:2])):
            with self.subTest(text_type=type(text).__name__, input_count=len(inputs)):
                with self.assertRaises(compiler.FixedRegistrationCompileError):
                    compiler.write_fixed_registrations(self.output, text, inputs)
                self.assertEqual(self.output.read_bytes(), SENTINEL)

    def test_strict_cli_rejects_unknown_abbreviated_duplicate_and_missing_arguments(self) -> None:
        complete = self.arguments()
        invalid = [[], complete + ["--unknown"], complete + ["extra"],
                   ["--in", *complete[1:]]]
        for index in (0, 2, 4, 6):
            invalid.append(complete[:index] + complete[index + 2:])
            invalid.append(complete + complete[index:index + 2])
        for arguments in invalid:
            with self.subTest(arguments=arguments):
                self.reject_cli(arguments, expected=2)
        result = self.cli(["--help"])
        self.assertEqual(result.returncode, 0)
        self.assertIn(b"--review-a", result.stdout)
        self.assertIn(b"--review-b", result.stdout)
        self.assertEqual(self.output.read_bytes(), SENTINEL)


if __name__ == "__main__":
    unittest.main()
