#!/usr/bin/env python3
"""Independent documentary/compiler and failure-atomicity gates for pedal data."""

from __future__ import annotations

import copy
import csv
import hashlib
import importlib.util
import io
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
SPEC = importlib.util.spec_from_file_location("compile_pedal_routing", TOOLS / "compile_pedal_routing.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot import pedal compiler")
compiler = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(compiler)
INPUTS = (ROOT / "data/pedal-map.json", ROOT / "data/references/factory-table-iii.json",
          ROOT / "data/references/review-a-pedal.csv", ROOT / "data/references/review-b-pedal.csv")
RAW = tuple(path.read_bytes() for path in INPUTS)
MAP = json.loads(RAW[0])
REFERENCE = json.loads(RAW[1])
ENTRY = re.compile(r"^    PedalRoute\{PedalId\{(\d+)\}, (\d+), "
                   r"PedalBus::(Brown|Red|Orange|Yellow), (?:ToneId\{(\d+)\}|(std::nullopt))\},$",
                   re.MULTILINE)


class PedalCompilerTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="pedal-compiler-")
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.inputs = tuple(self.directory / name for name in ("map.json", "reference.json", "a.csv", "b.csv"))
        for path, raw in zip(self.inputs, RAW):
            path.write_bytes(raw)
        self.output = self.directory / "nested" / "PedalRoutingData.h"

    def compile(self):
        return compiler.compile_pedal_routing(*self.inputs)

    def cli(self, output=None):
        return subprocess.run(
            [sys.executable, "-B", str(TOOLS / "compile_pedal_routing.py"),
             "--input", str(self.inputs[0]), "--reference", str(self.inputs[1]),
             "--review-a", str(self.inputs[2]), "--review-b", str(self.inputs[3]),
             "--output", str(self.output if output is None else output)],
            capture_output=True, text=True, check=False)

    def assert_cli_rejected_preserves_output(self):
        self.output.parent.mkdir(exist_ok=True)
        self.output.write_bytes(b"existing generated header\n")
        result = self.cli()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertIn("pedal compile error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(self.output.read_bytes(), b"existing generated header\n")
        self.assertEqual(list(self.output.parent.iterdir()), [self.output])

    def test_all_generated_entries_match_both_csvs_with_separate_branches(self):
        text = self.compile()
        entries = ENTRY.findall(text)
        self.assertEqual(len(entries), 200)
        for raw in RAW[2:]:
            reader = csv.reader(io.StringIO(raw.decode("utf-8")))
            self.assertEqual(next(reader), ["pedal"] + [f"c{i}" for i in range(1, 9)])
            for row in reader:
                pedal = int(row[0])
                for column, expected in enumerate(row[1:]):
                    generated = entries[(pedal - 1) * 8 + column]
                    self.assertEqual(generated[:3], (str(pedal), str(column),
                                                     ("Brown", "Red", "Orange", "Yellow")[column // 2]))
                    self.assertEqual(generated[3], expected)
                    self.assertEqual(generated[4], "std::nullopt" if expected == "" else "")
        self.assertEqual(sum(bool(entry[4]) for entry in entries), 5)
        for pedal in range(1, 8):
            left, right = entries[(pedal - 1) * 8 + 1:(pedal - 1) * 8 + 3]
            self.assertEqual(left[3], right[3])
            self.assertEqual((left[2], right[2]), ("Brown", "Red"))

    def test_identity_constants_are_actual_raw_and_canonical_digests(self):
        text = self.compile()
        canonical = json.dumps(MAP, sort_keys=True, separators=(",", ":"),
                               ensure_ascii=False, allow_nan=False).encode()
        expected = {
            "kPedalMapId": MAP["map_id"],
            "kPedalMapRawSha256": hashlib.sha256(RAW[0]).hexdigest(),
            "kPedalMapCanonicalSha256": hashlib.sha256(canonical).hexdigest(),
            "kFactoryComparisonId": REFERENCE["reference_id"],
            "kFactoryComparisonRawSha256": hashlib.sha256(RAW[1]).hexdigest(),
            "kPedalReviewASha256": hashlib.sha256(RAW[2]).hexdigest(),
            "kPedalReviewBSha256": hashlib.sha256(RAW[3]).hexdigest(),
        }
        for name, value in expected.items():
            self.assertIn(f'inline constexpr std::string_view {name} = "{value}";', text)
        self.assertNotEqual(expected["kPedalMapRawSha256"], expected["kPedalMapCanonicalSha256"])

    def test_output_is_deterministic_lf_only_without_paths_or_timestamps(self):
        first = self.compile()
        self.assertEqual(self.compile(), first)
        self.assertTrue(first.endswith("\n"))
        self.assertNotIn("\r", first)
        self.assertNotIn(str(self.directory), first)
        self.assertLess(len(first.encode()), compiler.MAX_OUTPUT_BYTES)
        self.assertIn("std::nullopt", first)
        self.assertNotIn("ToneId{0}", first)
        self.assertNotIn("gain", first)
        for path, raw in zip(self.inputs, RAW):
            self.assertEqual(path.read_bytes(), raw)

    def test_cli_publishes_and_replaces_only_after_complete_validation(self):
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertIn("200 positions, 195 connected, 5 disconnected", result.stdout)
        expected = self.output.read_bytes()
        self.output.write_bytes(b"obsolete header")
        again = self.cli()
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertEqual(self.output.read_bytes(), expected)
        self.assertEqual(list(self.output.parent.iterdir()), [self.output])
        for path, raw in zip(self.inputs, RAW):
            self.assertEqual(path.read_bytes(), raw)

    def test_invalid_map_ids_sources_and_bus_metadata_reject_without_output_change(self):
        variants = []
        for replacement in (0, 92, True, "1", None):
            value = copy.deepcopy(MAP)
            value["rows"][0]["sources"][0] = replacement
            variants.append(value)
        value = copy.deepcopy(MAP)
        value["rows"][7]["sources"][1] = 20
        variants.append(value)
        value = copy.deepcopy(MAP)
        value["bus_columns"]["brown"] = [0, 2]
        variants.append(value)
        value = copy.deepcopy(MAP)
        value["rows"].pop()
        variants.append(value)
        value = copy.deepcopy(MAP)
        value["map_id"] = "invented-map"
        variants.append(value)
        for value in variants:
            with self.subTest(value=value.get("map_id")):
                self.inputs[0].write_text(json.dumps(value))
                self.assert_cli_rejected_preserves_output()

    def test_both_independent_csv_inputs_are_compared_cell_by_cell(self):
        for index in (2, 3):
            for original, altered, location in (
                (b"1,1,13,13,25", b"1,2,13,13,25", "pedal 1/c1"),
                (b"8,8,,20,32", b"8,8,20,20,32", "pedal 8/c2"),
                (b"25,25,44,37", b"25,25,,37", "pedal 25/c2"),
            ):
                with self.subTest(index=index, location=location):
                    self.inputs[index].write_bytes(RAW[index].replace(original, altered))
                    with self.assertRaisesRegex(compiler.PedalCompileError, location):
                        self.compile()
                    self.assert_cli_rejected_preserves_output()
                    self.inputs[index].write_bytes(RAW[index])

    def test_csv_shape_encoding_and_identity_are_strict(self):
        for payload in (RAW[2].replace(b"pedal,c1", b"pedal,c0"),
                        RAW[2] + b"\n", RAW[2].replace(b"\n", b"\r\n"),
                        RAW[2][:-1], b"\xff\n", RAW[2].replace(b"1,1,13", b"01,1,13")):
            with self.subTest(prefix=payload[:30]):
                self.inputs[2].write_bytes(payload)
                self.assert_cli_rejected_preserves_output()

    def test_changed_manifest_claims_counts_ids_and_hashes_are_rejected(self):
        for group, field, value in (
            (None, "reference_id", "other-comparison"),
            ("claim_boundary", "physical_fidelity_established", True),
            ("comparison", "pedal_connected", 200),
            ("claim_boundary", "original_authoring_provenance_changed", True),
        ):
            manifest = copy.deepcopy(REFERENCE)
            (manifest if group is None else manifest[group])[field] = value
            self.inputs[1].write_text(json.dumps(manifest))
            self.assert_cli_rejected_preserves_output()
        manifest = copy.deepcopy(REFERENCE)
        manifest["targets"]["pedal"]["raw_sha256"] = "0" * 64
        self.inputs[1].write_text(json.dumps(manifest))
        self.assert_cli_rejected_preserves_output()
        manifest = copy.deepcopy(REFERENCE)
        manifest["unexpected"] = False
        self.inputs[1].write_text(json.dumps(manifest))
        self.assert_cli_rejected_preserves_output()

    def test_map_raw_identity_cannot_be_replaced_by_equivalent_json(self):
        self.inputs[0].write_bytes(json.dumps(MAP, sort_keys=True).encode())
        with self.assertRaisesRegex(compiler.PedalCompileError, "raw bytes|raw SHA-256"):
            self.compile()
        self.assert_cli_rejected_preserves_output()

    def test_reference_raw_digest_tracks_semantically_identical_formatting(self):
        raw = json.dumps(REFERENCE, sort_keys=True, separators=(",", ":")).encode()
        self.inputs[1].write_bytes(raw)
        text = self.compile()
        self.assertIn(f'kFactoryComparisonRawSha256 = "{hashlib.sha256(raw).hexdigest()}";', text)
        self.assertEqual(ENTRY.findall(text), ENTRY.findall(compiler.compile_pedal_routing(*INPUTS)))

    def test_json_parser_rejects_duplicate_names_nonfinite_and_bad_encoding(self):
        malformed = (b"", b"{", b"\xff", b'{"schema_version":1,"schema_version":1}',
                     b'{"schema_version":NaN}', b'{"schema_version":1.0}',
                     b'{"schema_version":1e0}', b"[" * 2000 + b"0" + b"]" * 2000)
        for index in (0, 1):
            for payload in malformed:
                with self.subTest(index=index, prefix=payload[:30]):
                    self.inputs[index].write_bytes(payload)
                    self.assert_cli_rejected_preserves_output()
            self.inputs[index].write_bytes(RAW[index])

    def test_input_byte_bounds_and_inclusive_reference_limit(self):
        limits = (compiler.MAX_MAP_BYTES, compiler.MAX_REFERENCE_BYTES,
                  compiler.MAX_REVIEW_BYTES, compiler.MAX_REVIEW_BYTES)
        for index, limit in enumerate(limits):
            with self.subTest(index=index):
                self.inputs[index].write_bytes(RAW[index] + b" " * (limit + 1 - len(RAW[index])))
                with self.assertRaisesRegex(compiler.PedalCompileError, "at most|byte limit"):
                    self.compile()
                self.assert_cli_rejected_preserves_output()
                self.inputs[index].write_bytes(RAW[index])
        # The reference permits formatting differences; exactly its byte limit
        # is admissible and retains the actual byte digest, without enlarging C++.
        self.inputs[1].write_bytes(RAW[1] + b" " * (compiler.MAX_REFERENCE_BYTES - len(RAW[1])))
        self.assertEqual(len(ENTRY.findall(self.compile())), 200)

    def test_missing_and_nonregular_inputs_reject_without_partial_output(self):
        for index in range(4):
            self.inputs[index].unlink()
            self.assert_cli_rejected_preserves_output()
            self.inputs[index].mkdir()
            self.assert_cli_rejected_preserves_output()
            self.inputs[index].rmdir()
            self.inputs[index].write_bytes(RAW[index])

    def test_output_must_not_alias_any_input_by_path_or_hard_link(self):
        for path, raw in zip(self.inputs, RAW):
            with self.subTest(path=path.name):
                result = self.cli(path)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("alias", result.stderr)
                self.assertEqual(path.read_bytes(), raw)
                linked = self.directory / "linked-output.h"
                os.link(path, linked)
                result = self.cli(linked)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("alias", result.stderr)
                self.assertEqual(path.read_bytes(), raw)
                self.assertEqual(linked.read_bytes(), raw)
                linked.unlink()

    def test_replace_failure_preserves_old_output_and_removes_temporary(self):
        text = self.compile()
        self.output.parent.mkdir()
        self.output.write_bytes(b"keep old output")
        with mock.patch.object(compiler.os, "replace", side_effect=OSError("injected replace failure")):
            with self.assertRaisesRegex(compiler.PedalCompileError, "injected replace failure"):
                compiler.write_compiled_header(self.output, text, self.inputs)
        self.assertEqual(self.output.read_bytes(), b"keep old output")
        self.assertEqual(list(self.output.parent.iterdir()), [self.output])

    def test_output_bounds_and_directory_target_fail_without_input_mutation(self):
        with self.assertRaisesRegex(compiler.PedalCompileError, "byte bound"):
            compiler.write_compiled_header(self.output, "x" * (compiler.MAX_OUTPUT_BYTES + 1), self.inputs)
        self.assertFalse(self.output.exists())
        self.output.mkdir(parents=True)
        with self.assertRaises(compiler.PedalCompileError):
            compiler.write_compiled_header(self.output, self.compile(), self.inputs)
        self.assertTrue(self.output.is_dir())
        self.assertEqual(list(self.output.parent.iterdir()), [self.output])
        for path, raw in zip(self.inputs, RAW):
            self.assertEqual(path.read_bytes(), raw)


if __name__ == "__main__":
    unittest.main()
