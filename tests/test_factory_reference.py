#!/usr/bin/env python3
"""Independent frozen-data comparisons and adversarial evidence mutations."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def import_tool(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


factory = import_tool("factory_reference", "validate_factory_reference.py")
compiler = import_tool("factory_profile_compiler", "compile_profile.py")


def leaf_paths(value, path=()):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from leaf_paths(child, path + (key,))
    elif isinstance(value, list) and value:
        for index, child in enumerate(value):
            yield from leaf_paths(child, path + (index,))
    else:
        yield path, value


def put(value, path, replacement):
    for part in path[:-1]:
        value = value[part]
    value[path[-1]] = replacement


class FactoryReferenceTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="hammond factory reference ")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.manifest = factory.expected_manifest()
        self.files = [factory.MANIFEST_PATH, factory.PROFILE_PATH, factory.PEDAL_PATH]
        for reading in self.manifest["readings"]:
            self.files.extend([reading["note"], reading["manual"]["path"], reading["pedal"]["path"]])
        for filename in self.files:
            target = self.root / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / filename, target)

    def write_json(self, filename, value):
        (self.root / filename).write_bytes(
            (json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + "\n").encode("utf-8"))

    def mutate_csv(self, filename, row, column, value):
        path = self.root / filename
        lines = path.read_text(encoding="utf-8").splitlines()
        fields = lines[row].split(",")
        fields[column] = value
        lines[row] = ",".join(fields)
        path.write_bytes(("\n".join(lines) + "\n").encode("utf-8"))

    def failure(self):
        with self.assertRaises(factory.FactoryReferenceError) as caught:
            factory.validate_reference(self.root)
        return str(caught.exception)

    def test_all_readings_and_targets_match_without_mutation(self):
        before = {name: (self.root / name).read_bytes() for name in self.files}
        report = factory.validate_reference(self.root)
        self.assertEqual(report["status"], "exact-match")
        self.assertEqual(report["manual_assignments"], 61 * 9)
        self.assertEqual(report["pedal_positions"], 25 * 8)
        self.assertEqual(report["pedal_connected"], 195)
        self.assertEqual(report["pedal_disconnections"],
                         [[8, "c2"], [9, "c2"], [10, "c2"], [11, "c2"], [12, "c2"]])
        self.assertEqual(report["mismatches"], {
            "a_b_manual": 0, "a_b_pedal": 0,
            "a_target_manual": 0, "a_target_pedal": 0,
            "b_target_manual": 0, "b_target_pedal": 0,
        })
        self.assertIn("not-checked", report["source_pdf_check"])
        self.assertEqual(before, {name: (self.root / name).read_bytes() for name in self.files})

    def test_compiler_routes_and_original_identities_are_unchanged(self):
        profile = compiler.load_profile(ROOT / factory.PROFILE_PATH)
        self.assertIs(profile["manual_map"]["independent_factory_verification"], False)
        self.assertEqual(compiler.authoring_sha256(profile),
                         "49791eac8d0b556b0abd2018b8cabc6f240161edab8a9fa0ef97905f2badda83")
        text = compiler.compile_profile(profile)
        self.assertEqual(hashlib.sha256(text.encode("utf-8")).hexdigest(),
                         "b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f")
        lines = text.splitlines()
        start = lines.index("manual_map 61 9") + 1
        compiled = [[int(token) for token in line.split()] for line in lines[start:-1]]
        self.assertEqual(len(compiled), 61)
        self.assertEqual(sum(map(len, compiled)), 549)
        for reading in self.manifest["readings"]:
            independent = factory.parse_transcription((ROOT / reading["manual"]["path"]).read_bytes(), "manual")
            self.assertEqual(compiled, independent)

    def test_numeric_disagreements_report_every_changed_cell_and_locator(self):
        filename = "data/references/review-a-manual.csv"
        for row, column in ((1, 1), (36, 9), (37, 1), (44, 9), (56, 9), (61, 9)):
            self.mutate_csv(filename, row, column, "14")
        before = (self.root / filename).read_bytes()
        error = self.failure()
        self.assertIn("raw SHA-256 mismatch", error)
        for cell in ("manual 1/d1", "manual 36/d9", "manual 37/d1",
                     "manual 44/d9", "manual 56/d9", "manual 61/d9"):
            self.assertIn(cell, error)
        self.assertIn("PDF 155, printed 3-76", error)
        self.assertIn("PDF 156, printed 3-77", error)
        self.assertIn("A versus B", error)
        self.assertIn("A versus target", error)
        self.assertEqual(before, (self.root / filename).read_bytes())

    def test_target_manual_change_is_not_hidden_by_reference_agreement(self):
        profile = factory.load_json(self.root / factory.PROFILE_PATH)
        profile["manual_map"]["tone_ids"][60][8] = 86
        self.write_json(factory.PROFILE_PATH, profile)
        error = self.failure()
        self.assertIn("manual 61/d9", error)
        self.assertIn("85 != 86", error)
        self.assertIn("A versus target", error)
        self.assertIn("B versus target", error)
        self.assertIn("canonical SHA-256 mismatch", error)

    def test_same_change_in_all_three_inputs_cannot_rewrite_frozen_history(self):
        for label in ("a", "b"):
            self.mutate_csv(f"data/references/review-{label}-manual.csv", 61, 9, "86")
        profile = factory.load_json(self.root / factory.PROFILE_PATH)
        profile["manual_map"]["tone_ids"][60][8] = 86
        self.write_json(factory.PROFILE_PATH, profile)
        error = self.failure()
        self.assertEqual(error.count("raw SHA-256 mismatch"), 3)
        self.assertIn("canonical SHA-256 mismatch", error)

    def test_all_five_disconnections_are_checked_individually(self):
        original = factory.load_json(self.root / factory.PEDAL_PATH)
        for pedal in range(8, 13):
            with self.subTest(pedal=pedal):
                value = copy.deepcopy(original)
                value["rows"][pedal - 1]["sources"][1] = 20
                self.write_json(factory.PEDAL_PATH, value)
                error = self.failure()
                self.assertIn(f"pedal {pedal}/c2", error)
                self.assertIn("expected null disconnection", error)
                self.assertIn("PDF 157, printed 3-78", error)
                self.assertIn("None != 20", error)

    def test_shifted_null_fails_even_when_connection_counts_still_match(self):
        value = factory.load_json(self.root / factory.PEDAL_PATH)
        value["rows"][7]["sources"][1:3] = [20, None]
        self.write_json(factory.PEDAL_PATH, value)
        error = self.failure()
        self.assertIn("pedal 8/c2", error)
        self.assertIn("pedal 8/c3", error)
        self.assertIn("expected connected integer", error)

    def test_csv_empty_cell_added_or_removed_is_reported(self):
        self.mutate_csv("data/references/review-b-pedal.csv", 7, 2, "")
        self.mutate_csv("data/references/review-b-pedal.csv", 12, 2, "24")
        error = self.failure()
        self.assertIn("pedal 7/c2", error)
        self.assertIn("pedal 12/c2", error)
        self.assertIn("A versus B", error)
        self.assertIn("B versus target", error)

    def test_target_boolean_float_string_zero_and_null_ids_fail(self):
        profile = factory.load_json(self.root / factory.PROFILE_PATH)
        for wrong in (True, 13.0, "13", 0, 92, None):
            with self.subTest(wrong=wrong):
                value = copy.deepcopy(profile)
                value["manual_map"]["tone_ids"][0][0] = wrong
                self.write_json(factory.PROFILE_PATH, value)
                self.assertIn("invalid source", self.failure())
        self.write_json(factory.PROFILE_PATH, profile)
        pedal = factory.load_json(self.root / factory.PEDAL_PATH)
        for wrong in (True, 8.0, "8", 0, 92):
            with self.subTest(pedal_wrong=wrong):
                value = copy.deepcopy(pedal)
                value["rows"][7]["sources"][1] = wrong
                self.write_json(factory.PEDAL_PATH, value)
                self.assertIn("invalid source", self.failure())

    def test_target_shapes_order_and_columns_fail(self):
        profile = factory.load_json(self.root / factory.PROFILE_PATH)
        pedal = factory.load_json(self.root / factory.PEDAL_PATH)
        cases = [
            (factory.PROFILE_PATH, profile, ("manual_map", "tone_ids"), profile["manual_map"]["tone_ids"][:-1]),
            (factory.PROFILE_PATH, profile, ("manual_map", "tone_ids", 60), [61]),
            (factory.PROFILE_PATH, profile, ("manual_map", "drawbar_order"), list(reversed(factory.DRAWBARS))),
            (factory.PEDAL_PATH, pedal, ("rows",), pedal["rows"][:-1]),
            (factory.PEDAL_PATH, pedal, ("rows", 24, "pedal_id"), 24),
            (factory.PEDAL_PATH, pedal, ("rows", 24, "pedal_id"), 25.0),
            (factory.PEDAL_PATH, pedal, ("columns",), list(reversed(factory.PEDAL_COLUMNS))),
        ]
        for name, original, path, replacement in cases:
            with self.subTest(path=path):
                value = copy.deepcopy(original)
                put(value, path, replacement)
                self.write_json(name, value)
                self.failure()
                shutil.copyfile(ROOT / name, self.root / name)

    def test_original_provenance_promotion_is_rejected(self):
        profile = factory.load_json(self.root / factory.PROFILE_PATH)
        profile["manual_map"]["independent_factory_verification"] = True
        self.write_json(factory.PROFILE_PATH, profile)
        self.assertIn("independent_factory_verification", self.failure())
        shutil.copyfile(ROOT / factory.PROFILE_PATH, self.root / factory.PROFILE_PATH)
        pedal = factory.load_json(self.root / factory.PEDAL_PATH)
        pedal["provenance"]["independent_factory_transcription_status"] = "verified"
        self.write_json(factory.PEDAL_PATH, pedal)
        self.assertIn("independent_factory_transcription_status", self.failure())

    def test_every_manifest_leaf_is_part_of_the_contract(self):
        for path, original in leaf_paths(self.manifest):
            with self.subTest(path=path):
                value = copy.deepcopy(self.manifest)
                replacement = ([1] if original == [] else
                               not original if type(original) is bool else
                               original + 1 if type(original) is int else
                               "changed" if original is None else str(original) + " changed")
                put(value, path, replacement)
                with self.assertRaises(factory.FactoryReferenceError):
                    factory.validate_manifest(value)
        for value in (True, 1.0):
            changed = copy.deepcopy(self.manifest)
            changed["schema_version"] = value
            with self.assertRaises(factory.FactoryReferenceError):
                factory.validate_manifest(changed)
        changed = copy.deepcopy(self.manifest)
        changed["unknown"] = "not allowed"
        with self.assertRaises(factory.FactoryReferenceError):
            factory.validate_manifest(changed)

    def test_manifest_cannot_redirect_inputs_or_claim_false_source_identity(self):
        for path, replacement in [
            (("readings", 0, "manual", "path"), "../outside.csv"),
            (("source", "sha256"), "0" * 64),
            (("source", "table_locators", 0, "printed_page"), "3-16"),
            (("source", "applicable_models"), ["A-100"]),
            (("comparison", "manual_assignments"), 548),
            (("claim_boundary", "measured_specimen"), True),
        ]:
            with self.subTest(path=path):
                value = copy.deepcopy(self.manifest)
                put(value, path, replacement)
                self.write_json(factory.MANIFEST_PATH, value)
                self.assertIn("manifest", self.failure())

    def test_csv_shapes_headers_identity_and_line_endings_are_strict(self):
        data = (ROOT / "data/references/review-a-manual.csv").read_bytes()
        lines = data.splitlines()
        cases = [
            b"\n".join(lines[:-1]) + b"\n",
            data + lines[-1] + b"\n",
            data.replace(b"key,d1", b"key,d2", 1),
            data.replace(b"\n1,13", b"\n2,13", 1),
            data.replace(b"\n1,13,", b"\n1,", 1),
            data.replace(b"\n1,13,", b"\n1,13,13,", 1),
            data.replace(b"\n", b"\r\n"),
            data.rstrip(b"\n"),
            b"\xef\xbb\xbf" + data,
            b"\xff" + data,
            b"x" * (factory.MAX_CSV_BYTES + 1),
        ]
        for payload in cases:
            with self.subTest(payload=payload[:60]):
                with self.assertRaises(factory.FactoryReferenceError):
                    factory.parse_transcription(payload, "manual")
        with self.assertRaises(factory.FactoryReferenceError):
            factory.parse_transcription(data, "unknown")

    def test_csv_identifier_syntax_is_strict(self):
        data = (ROOT / "data/references/review-a-manual.csv").read_bytes()
        for wrong in (b"01", b"+13", b"13.0", b"1e1", b"NaN", b"True",
                      b" 13", b"13 ", b"", b"0", b"92", b"-13"):
            with self.subTest(wrong=wrong):
                payload = data.replace(b"\n1,13,", b"\n1," + wrong + b",", 1)
                with self.assertRaises(factory.FactoryReferenceError):
                    factory.parse_transcription(payload, "manual")

    def test_json_parsing_bounds_duplicates_and_nonfinite_values(self):
        path = self.root / "invalid.json"
        cases = [
            b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}',
            b'{"x":1e9999}', b'{"x":-Infinity}', b"\xff",
            b"\xef\xbb\xbf{}", b"{", b"[" * 30 + b"0" + b"]" * 30,
            b'{"x":"' + b"x" * 4097 + b'"}',
            b"[" + b"0," * factory.MAX_NODES + b"0]",
            b" " * (factory.MAX_JSON_BYTES + 1),
        ]
        for payload in cases:
            with self.subTest(payload=payload[:60]):
                path.write_bytes(payload)
                with self.assertRaises(factory.FactoryReferenceError):
                    factory.load_json(path)

    def test_missing_nonregular_or_empty_review_inputs_fail_cleanly(self):
        with self.assertRaises(factory.FactoryReferenceError):
            factory.load_json(self.root / "missing.json")
        with self.assertRaises(factory.FactoryReferenceError):
            factory.load_json(self.root)
        (self.root / self.manifest["readings"][1]["note"]).write_bytes(b"")
        self.assertIn("empty review note", self.failure())

    def test_json_rejects_unpaired_surrogate_strings_and_keys(self):
        path = self.root / "unicode.json"
        for payload in (b'{"value":"\\ud800"}', b'{"value":"\\udfff"}',
                        b'{"\\ud800":"value"}', b'{"\\udfff":"value"}'):
            with self.subTest(payload=payload):
                path.write_bytes(payload)
                with self.assertRaisesRegex(factory.FactoryReferenceError, "invalid UTF-8 JSON"):
                    factory.load_json(path)
        path.write_bytes(b'{"\\ud83d\\ude00":"\\ud83d\\ude00"}')
        self.assertEqual(factory.load_json(path), {"\U0001f600": "\U0001f600"})

    def test_surrogate_target_fails_through_public_api_and_cli(self):
        path = self.root / factory.PROFILE_PATH
        profile = json.loads(path.read_bytes())
        profile["frequency_model"]["reason"] = "\ud800"
        path.write_bytes(json.dumps(profile, ensure_ascii=True, allow_nan=False).encode("ascii"))
        retained = path.read_bytes()
        with self.assertRaisesRegex(factory.FactoryReferenceError, "invalid UTF-8 JSON"):
            factory.validate_reference(self.root)
        result = subprocess.run([sys.executable, str(ROOT / "tools/validate_factory_reference.py"),
                                 "--root", str(self.root)],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("factory reference error:", result.stderr)
        self.assertIn("invalid UTF-8 JSON", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(path.read_bytes(), retained)

    def test_optional_source_is_hashed_without_trusting_its_filename(self):
        source = self.root / "Hammond-factory-service.pdf"
        source.write_bytes(b"%PDF-1.5\nnot the retained source\n")
        with self.assertRaises(factory.FactoryReferenceError) as caught:
            factory.validate_reference(self.root, source)
        self.assertIn("source PDF: expected 7077593 raw bytes", str(caught.exception))
        self.assertIn("source PDF: raw SHA-256 mismatch", str(caught.exception))

    def test_diagnostics_are_bounded_even_for_many_valid_numeric_changes(self):
        profile = factory.load_json(self.root / factory.PROFILE_PATH)
        profile["manual_map"]["tone_ids"] = [[13] * 9 for _ in range(61)]
        self.write_json(factory.PROFILE_PATH, profile)
        with self.assertRaises(factory.FactoryReferenceError) as caught:
            factory.validate_reference(self.root)
        error = caught.exception
        self.assertEqual(len(error.diagnostics), factory.MAX_DIAGNOSTICS)
        self.assertGreater(error.total, factory.MAX_DIAGNOSTICS)
        self.assertIn("additional diagnostics omitted", str(error))
        self.assertIn("manual 1/d2", str(error))

    def test_cli_returns_machine_readable_success_and_clean_failure(self):
        tool = ROOT / "tools" / "validate_factory_reference.py"
        result = subprocess.run([sys.executable, str(tool), "--root", str(self.root)],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["manual_assignments"], 549)
        self.mutate_csv("data/references/review-b-manual.csv", 61, 9, "86")
        result = subprocess.run([sys.executable, str(tool), "--root", str(self.root)],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("manual 61/d9", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
