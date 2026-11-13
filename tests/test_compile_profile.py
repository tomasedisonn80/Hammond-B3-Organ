#!/usr/bin/env python3
"""Strict authoring/CLI regression tests; Python standard library only.

The six manual rows below are transcribed from atlas PDF p.102 independently of
the compiler's mapping helper. Pitch checks concern the proposed 12-TET model
on pp.61/66, not production gearing or a measured specimen. Canonical JSON here
means the project's Python JSON convention, not RFC 8785 canonicalization.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
COMPILER_PATH = ROOT / "tools" / "compile_profile.py"
PROFILE_PATH = ROOT / "data" / "profiles" / "nominal-unmeasured-v1.json"
SCHEMA_PATH = ROOT / "data" / "profile.schema.json"
SPEC = importlib.util.spec_from_file_location("hammond_profile_compiler", COMPILER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {COMPILER_PATH}")
compiler = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(compiler)

PROFILE = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
PRINTED_MANUAL_ROWS = {
    1: [13, 20, 13, 25, 32, 37, 41, 44, 49],
    13: [13, 32, 25, 37, 44, 49, 53, 56, 61],
    43: [43, 62, 55, 67, 74, 79, 83, 86, 91],
    44: [44, 63, 56, 68, 75, 80, 84, 87, 80],
    56: [56, 75, 68, 80, 87, 80, 84, 87, 80],
    61: [61, 80, 73, 85, 80, 85, 89, 80, 85],
}


def at_path(value, path):
    for key in path:
        value = value[key]
    return value


def dictionary_paths(value, path=()):
    """Include every authoring object, including objects late in source arrays."""
    if isinstance(value, dict):
        yield path
        for key, child in value.items():
            yield from dictionary_paths(child, path + (key,))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from dictionary_paths(child, path + (index,))


def reverse_objects(value):
    if isinstance(value, dict):
        return {key: reverse_objects(child) for key, child in reversed(value.items())}
    if isinstance(value, list):
        return [reverse_objects(child) for child in value]
    return value


def canonical_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


class ProfileTestCase(unittest.TestCase):
    def setUp(self):
        self.profile = copy.deepcopy(PROFILE)
        self.directory = tempfile.TemporaryDirectory(prefix="hammond profile tests ")
        self.addCleanup(self.directory.cleanup)
        self.work = Path(self.directory.name)

    def reject_value(self, path, value):
        profile = copy.deepcopy(PROFILE)
        at_path(profile, path[:-1])[path[-1]] = value
        with self.assertRaises(compiler.ProfileError):
            compiler.compile_profile(profile)

    def load_bytes(self, payload):
        path = self.work / "authoring.json"
        path.write_bytes(payload)
        return compiler.load_profile(path)


class NominalProfileTests(ProfileTestCase):
    def test_valid_profile_retains_explicit_unknowns(self):
        self.assertEqual(compiler.load_profile(PROFILE_PATH), self.profile)
        self.assertIsNone(compiler.validate_profile(self.profile))
        self.assertEqual(self.profile["evidence_status"], "unmeasured")
        self.assertIs(self.profile["manual_map"]["independent_factory_verification"], False)
        for field in ("specimen_id", "ao28_revision", "measurements"):
            record = self.profile["reference"][field]
            self.assertIsNone(record["value"])
            self.assertEqual(record["evidence_class"], "unknown")
            self.assertIsNone(record["uncertainty"])
            self.assertIsNone(record["acquisition_reference"])
            self.assertTrue(record["reason"].strip())

    def test_six_independent_printed_manual_rows(self):
        compiled_rows = compiler.compile_profile(self.profile).splitlines()[98:159]
        for key, expected in PRINTED_MANUAL_ROWS.items():
            with self.subTest(playing_key=key):
                self.assertEqual(self.profile["manual_map"]["tone_ids"][key - 1], expected)
                self.assertEqual([int(value) for value in compiled_rows[key - 1].split()], expected)

    def test_all_91_frequencies_and_independent_pitch_anchors(self):
        sources = self.profile["sources"]
        self.assertEqual([source["tone_id"] for source in sources], list(range(1, 92)))
        frequencies = [source["frequency_hz"] for source in sources]
        # Decimal anchors calculated from the explicitly proposed 12-TET mode.
        anchors = {1: 32.70319566257483, 13: 65.40639132514966,
                   46: 440.0, 73: 2093.004522404789, 91: 5919.91076338615}
        for tone_id, expected in anchors.items():
            with self.subTest(anchor=tone_id):
                self.assertTrue(math.isclose(frequencies[tone_id - 1], expected, rel_tol=1e-14))
        self.assertEqual(frequencies[45], 440.0)
        for index, frequency in enumerate(frequencies):
            with self.subTest(tone_id=index + 1):
                self.assertTrue(math.isfinite(frequency))
                self.assertGreater(frequency, 0)
                self.assertLess(frequency, 44100 / 2)
                # Invert the frequency equation to expose indexing errors without
                # reusing nominal_frequency() or copying its exponent expression.
                self.assertAlmostEqual(69 + 12 * math.log2(frequency / 440), index + 24, places=12)
                if index:
                    self.assertGreater(frequency, frequencies[index - 1])
                if index + 12 < len(frequencies):
                    self.assertAlmostEqual(frequencies[index + 12] / frequency, 2, places=14)

    def test_drawbar_scale_and_all_manual_routes_have_supported_shapes(self):
        gains = self.profile["drawbar_gains"]["values"]
        self.assertEqual(len(gains), 9)
        self.assertEqual(gains[0], 0)
        self.assertEqual(gains[-1], 1)
        for lower, upper in zip(gains[1:], gains[2:]):
            self.assertAlmostEqual(20 * math.log10(upper / lower), 3, places=13)
        rows = self.profile["manual_map"]["tone_ids"]
        self.assertEqual(len(rows), 61)
        for row in rows:
            self.assertEqual(len(row), 9)
            self.assertTrue(all(type(tone) is int and 13 <= tone <= 91 for tone in row))

    def test_canonical_digest_uses_project_json_bytes_including_metadata(self):
        self.profile["output_gain"]["reason"] += " Unicode round-trip: café, Δ."
        expected = canonical_bytes(self.profile)
        digest = hashlib.sha256(expected).hexdigest()
        self.assertEqual(compiler.canonical_json(self.profile), expected)
        self.assertIn("café, Δ".encode("utf-8"), expected)
        self.assertNotIn(b"\\u00e9", expected)
        self.assertFalse(expected.endswith(b"\n"))
        self.assertEqual(compiler.authoring_sha256(self.profile), digest)
        self.assertEqual(compiler.compile_profile(self.profile).splitlines()[2],
                         "authoring_sha256 " + digest)
        self.assertNotEqual(compiler.authoring_sha256(PROFILE), digest)

    def test_canonical_convention_preserves_integer_versus_float_authoring(self):
        # Python's JSON spelling is intentional; do not substitute RFC 8785.
        integer_profile = copy.deepcopy(self.profile)
        integer_profile["sources"][0]["peak_amplitude"] = 1
        self.assertNotEqual(compiler.canonical_json(integer_profile),
                            compiler.canonical_json(self.profile))
        self.assertNotEqual(compiler.authoring_sha256(integer_profile),
                            compiler.authoring_sha256(self.profile))
        original_lines = compiler.compile_profile(self.profile).splitlines()
        integer_lines = compiler.compile_profile(integer_profile).splitlines()
        self.assertEqual(original_lines[:2] + original_lines[3:],
                         integer_lines[:2] + integer_lines[3:])

    def test_compilation_is_deterministic_across_key_order_and_json_whitespace(self):
        original = compiler.compile_profile(self.profile)
        reordered = reverse_objects(self.profile)
        self.assertEqual(compiler.compile_profile(reordered), original)
        self.assertEqual(compiler.compile_profile(self.profile), original)
        loaded = self.load_bytes(json.dumps(reordered, indent=4).encode("utf-8") + b"\n")
        self.assertEqual(compiler.compile_profile(loaded).encode("utf-8"), original.encode("utf-8"))

    def test_compiled_text_contains_exact_complete_ordered_payload(self):
        compiled = compiler.compile_profile(self.profile)
        lines = compiled.splitlines()
        self.assertTrue(compiled.endswith("\n"))
        self.assertFalse(compiled.endswith("\n\n"))
        self.assertNotIn("\r", compiled)
        self.assertEqual(len(lines), 160)
        self.assertEqual(lines[:2], ["B3PROFILE 1", "profile_id nominal-unmeasured-v1"])
        self.assertEqual(lines[2], "authoring_sha256 " + hashlib.sha256(canonical_bytes(self.profile)).hexdigest())
        self.assertEqual(lines[3], "output_gain 0.03")
        self.assertEqual(lines[4].split()[0], "drawbar_gains")
        self.assertEqual([float(value) for value in lines[4].split()[1:]],
                         self.profile["drawbar_gains"]["values"])
        self.assertEqual(lines[5], "sources 91")
        for index, line in enumerate(lines[6:97]):
            values = line.split()
            self.assertEqual(len(values), 4)
            self.assertEqual(int(values[0]), index + 1)
            self.assertEqual([float(value) for value in values[1:]],
                             [self.profile["sources"][index]["frequency_hz"], 1.0, 0.0])
        self.assertEqual(lines[97], "manual_map 61 9")
        self.assertEqual([[int(value) for value in line.split()] for line in lines[98:159]],
                         self.profile["manual_map"]["tone_ids"])
        self.assertEqual(lines[-1], "end")
        self.assertLessEqual(len(compiled.encode("utf-8")), 128 * 1024)

    def test_validation_hashing_and_compilation_do_not_modify_input(self):
        before = copy.deepcopy(self.profile)
        for operation in (compiler.validate_profile, compiler.canonical_json,
                          compiler.authoring_sha256, compiler.compile_profile):
            with self.subTest(operation=operation.__name__):
                operation(self.profile)
                self.assertEqual(self.profile, before)
        self.profile["sources"][-1]["frequency_hz"] = None
        before = copy.deepcopy(self.profile)
        with self.assertRaises(compiler.ProfileError):
            compiler.compile_profile(self.profile)
        self.assertEqual(self.profile, before)


class AuthoringRejectionTests(ProfileTestCase):
    def test_unknown_fields_are_rejected_at_every_object(self):
        for path in dictionary_paths(PROFILE):
            with self.subTest(path=path):
                profile = copy.deepcopy(PROFILE)
                at_path(profile, path)["unrecognized_field"] = "unexpected"
                with self.assertRaises(compiler.ProfileError):
                    compiler.compile_profile(profile)

    def test_every_required_field_is_rejected_if_absent_or_unexpectedly_null(self):
        for path in dictionary_paths(PROFILE):
            for key, value in at_path(PROFILE, path).items():
                with self.subTest(path=path + (key,), value="absent"):
                    profile = copy.deepcopy(PROFILE)
                    del at_path(profile, path)[key]
                    with self.assertRaises(compiler.ProfileError):
                        compiler.compile_profile(profile)
                if value is not None:
                    with self.subTest(path=path + (key,), value=None):
                        self.reject_value(path + (key,), None)

    def test_unknown_versions_models_and_provenance_are_rejected(self):
        cases = {
            ("schema_version",): [0, 2, "1"],
            ("model_version",): [0, 2, "1"],
            ("profile_id",): ["measured-specimen", "nominal-unmeasured-v2"],
            ("model",): ["ideal-shared-sine-v2"],
            ("evidence_status",): ["measured"],
            ("source_document", "sha256"): ["0" * 64],
            ("source_document", "id"): ["another-document"],
            ("frequency_model", "id"): ["rational-gearing-v1"],
            ("frequency_model", "formula"): ["440 * 2**((tone_id - 45) / 12)"],
            ("manual_map", "algorithm"): ["clamp-to-91"],
            ("manual_map", "key_domain"): ["midi_note"],
            ("manual_map", "tone_domain"): ["zero_based_storage_index"],
            ("manual_map", "independent_factory_verification"): [True, 0],
            ("drawbar_gains", "model"): ["linear"],
            ("model_boundaries", "waveform"): ["measured-pickup-voltage"],
            ("model_boundaries", "leslie"): ["measured-122"],
        }
        for path, values in cases.items():
            for value in values:
                with self.subTest(path=path, value=value):
                    self.reject_value(path, value)

    def test_units_and_evidence_cannot_be_relabelled(self):
        for path in dictionary_paths(PROFILE):
            record = at_path(PROFILE, path)
            if "unit" in record:
                with self.subTest(path=path, field="unit"):
                    self.reject_value(path + ("unit",), "volts")
            if "evidence_class" in record and "reason" in record:
                for field, values in {
                    "evidence_class": ["invented", "measured"],
                    "applicable_variant": ["Leslie-147"],
                    "reason": ["", " \t\n"],
                    "uncertainty": [0],
                    "acquisition_reference": ["unverified-capture"],
                }.items():
                    for value in values:
                        with self.subTest(path=path, field=field, value=value):
                            self.reject_value(path + (field,), value)
                locator = path + ("source_locator",)
                self.reject_value(locator + ("document_id",), "unrelated-source")
                pages = record["source_locator"]["pdf_pages"]
                for replacement in ([0] + pages[1:], [501] + pages[1:],
                                    [pages[1]] + pages[1:]):
                    with self.subTest(path=locator, pages=replacement):
                        self.reject_value(locator + ("pdf_pages",), replacement)
        for field in ("specimen_id", "ao28_revision", "measurements"):
            self.reject_value(("reference", field, "value"), 0)

    def test_booleans_are_not_numeric_parameters(self):
        paths = [
            ("schema_version",), ("model_version",),
            ("frequency_model", "a4_hz"), ("frequency_model", "anchor_tone_id"),
            ("frequency_model", "source_locator", "pdf_pages", 0),
            ("sources", 0, "tone_id"), ("sources", 45, "frequency_hz"),
            ("sources", 90, "peak_amplitude"), ("sources", 0, "base_phase_turns"),
            ("manual_map", "offsets", 0), ("manual_map", "tone_ids", 60, 8),
            ("drawbar_gains", "values", 0), ("drawbar_gains", "values", 8),
            ("output_gain", "value"),
        ]
        for path in paths:
            for value in (False, True):
                with self.subTest(path=path, value=value):
                    self.reject_value(path, value)

    def test_nonfinite_and_unrepresentable_numbers_are_rejected(self):
        paths = [("sources", 0, "frequency_hz"), ("sources", 90, "peak_amplitude"),
                 ("sources", 45, "base_phase_turns"), ("drawbar_gains", "values", 4),
                 ("output_gain", "value")]
        for path in paths:
            for value in (math.nan, math.inf, -math.inf, 10 ** 1000):
                with self.subTest(path=path, kind=type(value).__name__):
                    self.reject_value(path, value)

    def test_every_source_id_must_be_unique_and_in_its_declared_position(self):
        for index in range(91):
            with self.subTest(tone_id=index + 1):
                self.reject_value(("sources", index, "tone_id"), (index + 1) % 91 + 1)
        for value in (0, 92, 1.0, "1"):
            self.reject_value(("sources", 0, "tone_id"), value)
        swapped = copy.deepcopy(self.profile["sources"])
        swapped[0], swapped[-1] = swapped[-1], swapped[0]
        self.reject_value(("sources",), swapped)

    def test_source_map_and_gain_counts_are_exact(self):
        paths = [("sources",), ("manual_map", "tone_ids"),
                 ("manual_map", "tone_ids", 0), ("manual_map", "tone_ids", 60),
                 ("manual_map", "drawbar_order"), ("manual_map", "offsets"),
                 ("drawbar_gains", "values")]
        for path in paths:
            values = at_path(PROFILE, path)
            for replacement in (values[:-1], values + [copy.deepcopy(values[-1])]):
                with self.subTest(path=path, length=len(replacement)):
                    self.reject_value(path, replacement)

    def test_every_source_numeric_value_must_match_the_named_baseline(self):
        for index, source in enumerate(PROFILE["sources"]):
            for field, replacement in (
                ("frequency_hz", math.nextafter(source["frequency_hz"], math.inf)),
                ("peak_amplitude", 0.5), ("base_phase_turns", 0.25),
            ):
                with self.subTest(tone_id=index + 1, field=field):
                    self.reject_value(("sources", index, field), replacement)
        for path, values in {
            ("sources", 0, "frequency_hz"): [0, -1, 22050, "440"],
            ("sources", 0, "peak_amplitude"): [-0.1, 1.1],
            ("sources", 0, "base_phase_turns"): [-0.1, 1],
            ("frequency_model", "a4_hz"): [441.0],
            ("frequency_model", "anchor_tone_id"): [45],
            ("output_gain", "value"): [0, 0.031, -1, 1.01],
        }.items():
            for value in values:
                with self.subTest(path=path, value=value):
                    self.reject_value(path, value)
        for position in range(9):
            with self.subTest(drawbar_position=position):
                self.reject_value(("drawbar_gains", "values", position), 0.01)

    def test_every_manual_cell_and_drawbar_definition_is_validated(self):
        for key, row in enumerate(PROFILE["manual_map"]["tone_ids"]):
            for drawbar, tone in enumerate(row):
                with self.subTest(playing_key=key + 1, drawbar=drawbar + 1):
                    self.reject_value(("manual_map", "tone_ids", key, drawbar),
                                      14 if tone == 13 else 13)
        for value in (0, 1, 12, 92, -1, 13.0, "13"):
            with self.subTest(out_of_domain=value):
                self.reject_value(("manual_map", "tone_ids", 0, 0), value)
        for index in range(9):
            self.reject_value(("manual_map", "offsets", index), -1)
            self.reject_value(("manual_map", "drawbar_order", index), "unrecognized")

    def test_duplicate_json_keys_reject_equal_conflicting_and_escaped_names(self):
        raw = json.dumps(PROFILE)
        cases = [
            raw.replace('"schema_version": 1', '"schema_version": 1, "schema_version": 1', 1),
            raw.replace('"schema_version": 1', '"schema_version": 2, "schema_version": 1', 1),
            raw.replace('"schema_version": 1', '"schema_version": 1, "\\u0073chema_version": 1', 1),
            raw.replace('"tone_id": 1', '"tone_id": 91, "tone_id": 1', 1),
        ]
        for raw_json in cases:
            with self.subTest(json_prefix=raw_json[:90]):
                with self.assertRaisesRegex(compiler.ProfileError, "duplicate"):
                    self.load_bytes(raw_json.encode("utf-8"))

    def test_nonfinite_json_literals_and_overflow_exponents_are_rejected(self):
        raw = json.dumps(PROFILE)
        for literal in ("NaN", "Infinity", "-Infinity", "1e9999", "-1e9999"):
            with self.subTest(literal=literal):
                payload = raw.replace('"value": 0.03', '"value": ' + literal, 1)
                with self.assertRaises(compiler.ProfileError):
                    self.load_bytes(payload.encode("utf-8"))

    def test_malformed_encoding_json_and_nonobject_roots_fail_cleanly(self):
        for payload in (b"", b"{", b"{} trailing", b"\xff", b"null", b"true", b"[]", b"42",
                        b'"text"', b'{"schema_version": "\\ud800"}',
                        b"[" * 1500 + b"0" + b"]" * 1500):
            with self.subTest(payload_prefix=payload[:50]):
                with self.assertRaises(compiler.ProfileError):
                    self.load_bytes(payload)

    def test_file_byte_limit_includes_insignificant_json_whitespace(self):
        raw = canonical_bytes(PROFILE)
        exact_limit = raw + b" " * (256 * 1024 - len(raw))
        self.assertEqual(self.load_bytes(exact_limit), PROFILE)
        with self.assertRaisesRegex(compiler.ProfileError, "byte limit"):
            self.load_bytes(exact_limit + b" ")

    def test_imported_trees_have_bounded_strings_depth_width_and_node_count(self):
        self.profile["output_gain"]["reason"] = "x" * 4096
        compiler.validate_profile(self.profile)
        self.reject_value(("output_gain", "reason"), "x" * 4097)
        self.reject_value(("output_gain", "reason"), "\ud800")
        deep = 0
        for _ in range(25):
            deep = [deep]
        for value, message in (
            (deep, "nesting"),
            (list(range(1025)), "1024"),
            ({str(index): None for index in range(65)}, "64"),
            ([[0] * 1000 for _ in range(21)], "JSON values"),
        ):
            with self.subTest(limit=message):
                profile = copy.deepcopy(PROFILE)
                profile["unexpected"] = value
                with self.assertRaisesRegex(compiler.ProfileError, message):
                    compiler.validate_profile(profile)

    def test_imported_non_json_values_and_cycles_raise_profile_errors(self):
        for value in ({1: "nonstring key"}, (1, 2), {1, 2}, b"bytes", object()):
            with self.subTest(type=type(value).__name__):
                self.reject_value(("output_gain", "value"), value)
        self.profile["recursive"] = self.profile
        with self.assertRaises(compiler.ProfileError):
            compiler.validate_profile(self.profile)


class SchemaContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def test_schema_closes_objects_and_declares_every_property_required(self):
        self.assertEqual(self.schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(set(self.schema["properties"]), set(PROFILE))
        objects = []
        for path in dictionary_paths(self.schema):
            node = at_path(self.schema, path)
            if node.get("type") == "object":
                objects.append(path)
                with self.subTest(path=path):
                    self.assertIs(node.get("additionalProperties"), False)
                    self.assertEqual(set(node["required"]), set(node["properties"]))
        self.assertGreater(len(objects), 10)

    def test_schema_declares_fixed_source_manual_and_gain_domains(self):
        properties = self.schema["properties"]
        for key in ("schema_version", "model_version", "model", "profile_id", "evidence_status"):
            self.assertEqual(properties[key]["const"], PROFILE[key])
        source_array = properties["sources"]
        self.assertEqual((source_array["minItems"], source_array["maxItems"]), (91, 91))
        self.assertEqual(source_array["items"]["$ref"], "#/$defs/source")
        source = self.schema["$defs"]["source"]["properties"]
        self.assertEqual(set(source), set(PROFILE["sources"][0]))
        self.assertEqual(source["tone_id"]["type"], "integer")
        self.assertEqual((source["tone_id"]["minimum"], source["tone_id"]["maximum"]), (1, 91))
        self.assertEqual(source["frequency_hz"]["type"], "number")
        self.assertEqual(source["frequency_hz"]["exclusiveMinimum"], 0)
        rows = properties["manual_map"]["properties"]["tone_ids"]
        self.assertEqual((rows["minItems"], rows["maxItems"]), (61, 61))
        row = rows["items"]
        self.assertEqual((row["minItems"], row["maxItems"]), (9, 9))
        self.assertEqual(row["items"], {"type": "integer", "minimum": 13, "maximum": 91})
        gains = properties["drawbar_gains"]["properties"]["values"]
        self.assertEqual((gains["minItems"], gains["maxItems"]), (9, 9))
        self.assertEqual(gains["items"], {"type": "number", "minimum": 0, "maximum": 1})


class CompilerCliTests(ProfileTestCase):
    def setUp(self):
        super().setUp()
        self.input = self.work / "authoring input.json"
        self.input.write_bytes(PROFILE_PATH.read_bytes())
        self.output = self.work / "compiled output.b3p"

    def run_cli(self, *arguments, hash_seed="0"):
        environment = os.environ.copy()
        environment["PYTHONHASHSEED"] = hash_seed
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run([sys.executable, str(COMPILER_PATH), *map(str, arguments)],
                              cwd=self.work, env=environment, capture_output=True,
                              text=True, encoding="utf-8", timeout=20, check=False)

    def assert_cli_failure(self, result):
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertTrue(result.stderr.strip())
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_cli_compiles_deterministic_bytes_from_unrelated_working_directory(self):
        expected = compiler.compile_profile(PROFILE).encode("utf-8")
        original = self.input.read_bytes()
        for seed in ("1", "987654"):
            result = self.run_cli("--input", self.input, "--output", self.output, hash_seed=seed)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(self.output.read_bytes(), expected)
            self.assertIn(hashlib.sha256(canonical_bytes(PROFILE)).hexdigest(), result.stdout)
            self.assertEqual(result.stderr, "")
        self.assertEqual(self.input.read_bytes(), original)
        self.assertEqual(set(self.work.iterdir()), {self.input, self.output})

    def test_check_without_output_validates_without_creating_files(self):
        original = self.input.read_bytes()
        result = self.run_cli("--input", self.input, "--check")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("checked nominal-unmeasured-v1", result.stdout)
        self.assertEqual(self.input.read_bytes(), original)
        self.assertEqual(set(self.work.iterdir()), {self.input})

    def test_check_requires_exact_output_bytes_and_never_rewrites_them(self):
        expected = compiler.compile_profile(PROFILE).encode("utf-8")
        variants = [expected, expected[:-1], expected.replace(b"\n", b"\r\n"),
                    expected + b" ", expected.replace(b"output_gain 0.03", b"output_gain 3e-2"),
                    expected.replace(b"sources 91", b"sources 90"), b"stale output"]
        for payload in variants:
            with self.subTest(payload_length=len(payload)):
                self.output.write_bytes(payload)
                before = self.output.stat().st_mtime_ns
                result = self.run_cli("--input", self.input, "--output", self.output, "--check")
                if payload == expected:
                    self.assertEqual(result.returncode, 0, result.stderr)
                else:
                    self.assert_cli_failure(result)
                self.assertEqual(self.output.read_bytes(), payload)
                self.assertEqual(self.output.stat().st_mtime_ns, before)

    def test_check_missing_or_oversized_output_fails_without_writing(self):
        result = self.run_cli("--input", self.input, "--output", self.output, "--check")
        self.assert_cli_failure(result)
        self.assertFalse(self.output.exists())
        payload = b"x" * (128 * 1024 + 1)
        self.output.write_bytes(payload)
        result = self.run_cli("--input", self.input, "--output", self.output, "--check")
        self.assert_cli_failure(result)
        self.assertEqual(self.output.read_bytes(), payload)

    def test_failed_compilation_preserves_existing_and_absent_outputs(self):
        raw = json.dumps(PROFILE)
        payloads = [b"{", b"\xff", b" " * (256 * 1024 + 1),
                    raw.replace('"schema_version": 1', '"schema_version": 2', 1).encode(),
                    raw.replace('"value": 0.03', '"value": null', 1).encode(),
                    raw.replace('"value": 0.03', '"value": NaN', 1).encode(),
                    raw.replace('"schema_version": 1',
                                '"schema_version": 1, "schema_version": 1', 1).encode()]
        sentinel = b"previous useful compiled file\n"
        for present in (False, True):
            for index, payload in enumerate(payloads):
                with self.subTest(existing_output=present, malformed_case=index):
                    self.input.write_bytes(payload)
                    if present:
                        self.output.write_bytes(sentinel)
                    elif self.output.exists():
                        self.output.unlink()
                    result = self.run_cli("--input", self.input, "--output", self.output)
                    self.assert_cli_failure(result)
                    self.assertEqual(self.input.read_bytes(), payload)
                    self.assertEqual(self.output.exists(), present)
                    if present:
                        self.assertEqual(self.output.read_bytes(), sentinel)
                    self.assertEqual(set(self.work.iterdir()),
                                     {self.input, self.output} if present else {self.input})

    def test_missing_input_and_invalid_output_targets_fail_cleanly(self):
        self.output.write_bytes(b"preserve this output")
        result = self.run_cli("--input", self.work / "missing.json", "--output", self.output)
        self.assert_cli_failure(result)
        self.assertEqual(self.output.read_bytes(), b"preserve this output")
        absent_parent = self.work / "absent" / "output.b3p"
        result = self.run_cli("--input", self.input, "--output", absent_parent)
        self.assert_cli_failure(result)
        self.assertFalse(absent_parent.parent.exists())
        directory_output = self.work / "directory.b3p"
        directory_output.mkdir()
        marker = directory_output / "keep.txt"
        marker.write_bytes(b"keep")
        result = self.run_cli("--input", self.input, "--output", directory_output)
        self.assert_cli_failure(result)
        self.assertEqual(marker.read_bytes(), b"keep")
        self.assertEqual(set(self.work.iterdir()), {self.input, self.output, directory_output})

    def test_output_is_required_unless_check_is_requested(self):
        result = self.run_cli("--input", self.input)
        self.assert_cli_failure(result)
        self.assertEqual(set(self.work.iterdir()), {self.input})

    def assert_collision_rejected(self, input_path, output_path):
        original = self.input.read_bytes()
        files_before = set(self.work.iterdir())
        result = self.run_cli("--input", input_path, "--output", output_path)
        self.assert_cli_failure(result)
        self.assertIn("input", result.stderr)
        self.assertIn("output", result.stderr)
        self.assertEqual(self.input.read_bytes(), original)
        self.assertEqual(set(self.work.iterdir()), files_before)

    def test_same_path_and_lexical_aliases_cannot_overwrite_authoring(self):
        self.assert_collision_rejected(self.input, self.input)
        self.assert_collision_rejected(self.input.name, "./" + self.input.name)
        subdirectory = self.work / "subdirectory"
        subdirectory.mkdir()
        self.assert_collision_rejected(self.input, subdirectory / ".." / self.input.name)

    def test_symlink_input_output_aliases_cannot_overwrite_authoring(self):
        alias = self.work / "input-symlink.json"
        try:
            alias.symlink_to(self.input)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"symlinks unavailable: {error}")
        self.assert_collision_rejected(self.input, alias)
        self.assertTrue(alias.is_symlink())
        self.assert_collision_rejected(alias, self.input)

    def test_hardlink_input_output_aliases_cannot_replace_authoring(self):
        alias = self.work / "input-hardlink.json"
        try:
            os.link(self.input, alias)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"hardlinks unavailable: {error}")
        self.assert_collision_rejected(self.input, alias)
        self.assertTrue(os.path.samefile(self.input, alias))


if __name__ == "__main__":
    unittest.main(verbosity=2)
