#!/usr/bin/env python3
"""Cross-language registry/native conversion checks using the actual executable.

CTest supplies HAMMOND_PARAMETER_INFO_EXECUTABLE. Missing build prerequisites
are failures; these are internal mapping checks, not native host qualification.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import struct
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "independent_parameter_registry", ROOT / "tools" / "validate_parameters.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Cannot load the independent Python registry converter")
registry_api = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(registry_api)

ROOT_KEYS = frozenset(("schema_version", "registry_schema_version", "model", "scope",
                       "status", "verification_scope", "host_exports_verified",
                       "native_host_curves_verified",
                       "normalized", "parameters"))
RECORD_KEYS = frozenset(("id", "path", "kind", "unit", "minimum", "maximum",
                         "default_plain", "default_normalized", "step_count", "event"))
EVENT_KEYS = frozenset(("offset", "type", "manual", "index", "value"))
LEGACY_IDS = (set(range(4096, 4105)) | set(range(4112, 4121)) |
              set(range(4128, 4137)) | set(range(4144, 4153)) | {8192, 8208, 8209})
VERSION_2_IDS = LEGACY_IDS | {12288, 12289, 12290, 12291}
VERSION_3_IDS = VERSION_2_IDS | {16384, 16385}
ALL_IDS = VERSION_3_IDS | {20480, 20481}
LEGACY_DIGEST = "61669b54e0a0499da950ece28c855e70ab4cb815d204f625f0aee8542d8b4f1b"
VERSION_2_DIGEST = "5e161206e203cce130330b993590d892182c4ead62daba50b468b5348d70bed2"
VERSION_3_DIGEST = "13ba488bec90154c960c3fd700dc4a774aff5664caf5d68472821493f22d1cad"


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate native JSON key: {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f"Nonfinite JSON number: {value}")


def json_integer(text):
    # JSON permits the spelling -0. Retain its sign while requiring real integer
    # token types for all nonnegative version/ID/count/index fields separately.
    return -0.0 if text == "-0" else int(text)


def bits(value):
    return struct.pack("!d", float(value))


def exact_discrete(value, steps):
    numerator, denominator = value.as_integer_ratio()
    return (2 * numerator * steps + denominator) // (2 * denominator)


def nearest_binary64(numerator, denominator):
    # Independent integer-rational nearest-even oracle, not a production table.
    target = Fraction(numerator, denominator)
    low, high = 0, 0x3ff0000000000000
    decode = lambda raw: struct.unpack("!d", struct.pack("!Q", raw))[0]
    while low + 1 < high:
        middle = (low + high) // 2
        if Fraction.from_float(decode(middle)) <= target:
            low = middle
        else:
            high = middle
    low_distance = target - Fraction.from_float(decode(low))
    high_distance = Fraction.from_float(decode(high)) - target
    return decode(low if low_distance < high_distance or
                  (low_distance == high_distance and low % 2 == 0) else high)


PRESET_THRESHOLDS = tuple(nearest_binary64(2 * k + 1, 22) for k in range(11))
PRESET_CANONICAL = tuple(nearest_binary64(k, 11) for k in range(12))


class ParameterBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = os.environ.get("HAMMOND_PARAMETER_INFO_EXECUTABLE")
        if not raw or not Path(raw).is_file():
            raise RuntimeError(
                "Missing HAMMOND_PARAMETER_INFO_EXECUTABLE. Build hammond_parameter_info "
                "and run CTest or set the explicit executable path. Native checks were not run.")
        cls.executable = Path(raw).resolve()
        cls.registry = registry_api.load_registry(ROOT / "data" / "parameter-registry.json")
        cls.by_id = {record["id"]: record for record in cls.registry["parameters"]}
        if set(cls.by_id) != ALL_IDS or len(cls.by_id) != 47:
            raise RuntimeError("The independent 47-ID compatibility inventory has changed")
        cls.calls = 0

    @classmethod
    def tearDownClass(cls):
        print(f"parameter bridge: {cls.calls} actual diagnostic CLI calls")

    def invoke(self, arguments=(), **kwargs):
        type(self).calls += 1
        return subprocess.run([str(self.executable), *arguments],
                              capture_output=True, timeout=15, check=False, **kwargs)

    def successful(self, value, spelling=None):
        text = repr(value) if spelling is None else spelling
        result = self.invoke(("--normalized", text))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, b"")
        return self.inspect(result.stdout, value)

    def inspect(self, raw, normalized):
        self.assertLess(len(raw), 32 * 1024)
        self.assertTrue(raw.endswith(b"\n"))
        self.assertNotIn(b"\r", raw)
        data = json.loads(raw.decode("ascii"), object_pairs_hook=unique_object,
                          parse_constant=reject_constant, parse_int=json_integer)
        self.assertEqual(set(data), ROOT_KEYS)
        self.assertIs(type(data["schema_version"]), int)
        self.assertEqual(data["schema_version"], 2)
        self.assertIs(type(data["registry_schema_version"]), int)
        self.assertEqual(data["registry_schema_version"], 4)
        self.assertEqual(data["model"], "exclusive-fixed-percussion-pedal-console-v4")
        self.assertEqual(data["scope"], "implemented-console-subset")
        self.assertEqual(data["status"], "proposed-internal")
        self.assertEqual(data["verification_scope"], "sdk-free-core-parameter-mapping")
        self.assertIs(data["host_exports_verified"], False)
        self.assertIs(data["native_host_curves_verified"], False)
        self.assertIn(type(data["normalized"]), (int, float))
        self.assertEqual(bits(data["normalized"]), bits(normalized))
        self.assertIs(type(data["parameters"]), list)
        self.assertEqual(len(data["parameters"]), 47)
        self.assertEqual([record["id"] for record in data["parameters"]], sorted(ALL_IDS))
        for record in data["parameters"]:
            self.assertEqual(set(record), RECORD_KEYS)
            self.assertIs(type(record["id"]), int)
            original = self.by_id[record["id"]]
            for key in ("path", "kind", "unit", "minimum", "maximum", "step_count"):
                self.assertEqual(record[key], original[key])
            self.assertIs(type(record["step_count"]), int)
            self.assertEqual(record["default_plain"], original["default"])
            self.assertEqual(record["default_normalized"], original["normalized"]["default"])
            for key in ("minimum", "maximum", "default_plain", "default_normalized"):
                self.assertIn(type(record[key]), (int, float))
                self.assertTrue(math.isfinite(record[key]))
            event = record["event"]
            self.assertEqual(set(event), EVENT_KEYS)
            self.assertIs(type(event["offset"]), int)
            self.assertEqual(event["offset"], 0)
            self.assertIs(type(event["index"]), int)
            for key in ("type", "manual", "index"):
                self.assertEqual(event[key], original["engine_event"][key])
            python_plain = registry_api.normalized_to_value(original, normalized)
            self.assertIn(type(event["value"]), (int, float))
            self.assertTrue(math.isfinite(event["value"]))
            self.assertEqual(event["value"], python_plain)
            if original["step_count"]:
                oracle = (sum(normalized >= threshold for threshold in PRESET_THRESHOLDS)
                          if original["kind"] == "preset_selector" else
                          exact_discrete(normalized, original["step_count"]))
                self.assertEqual(event["value"], oracle)
                if event["value"] == 0:
                    self.assertEqual(math.copysign(1, event["value"]), 1)
            else:
                self.assertEqual(bits(event["value"]), bits(normalized))
        return data

    def test_default_output_has_exact_registry_targets_and_metadata(self):
        implicit = self.invoke()
        explicit = self.invoke(("--normalized", "0.5"))
        self.assertEqual(implicit.returncode, 0, implicit.stderr)
        self.assertEqual(explicit.returncode, 0, explicit.stderr)
        self.assertEqual(implicit.stderr, b"")
        self.assertEqual(explicit.stderr, b"")
        self.assertEqual(implicit.stdout, explicit.stdout)
        output = self.inspect(implicit.stdout, 0.5)
        for record in output["parameters"]:
            expected_event = registry_api.normalized_to_event(self.registry, record["id"], 0.5)
            self.assertEqual({k: v for k, v in record["event"].items() if k != "offset"},
                             expected_event)

    def test_every_half_step_and_immediate_binary64_neighbor(self):
        thresholds = [index / 16 for index in range(1, 16, 2)] + [0.5] + list(PRESET_THRESHOLDS)
        for threshold in thresholds:
            for value in (math.nextafter(threshold, 0), threshold,
                          math.nextafter(threshold, 1)):
                with self.subTest(threshold=threshold, normalized=value):
                    self.successful(value)

    def test_canonical_positions_expression_and_subnormal_boundaries(self):
        values = [index / 8 for index in range(9)] + list(PRESET_CANONICAL)
        values += [-0.0, math.nextafter(0.0, 1.0), float.fromhex("0x1.0p-1022"),
                   math.nextafter(1.0, 0.0), 0.12345678901234567]
        for value in values:
            with self.subTest(normalized=value):
                self.successful(value)

    def test_numeric_spellings_and_maximum_token_length(self):
        cases = ((0.5, ".5"), (0.5, "+.5"), (0.5, "5e-1"),
                 (0.5, "0.50000000000000000"), (1.0, "1."),
                 (1.0, "1e0"), (0.0, "0e-9999"), (-0.0, "-0.0"))
        for value, text in cases:
            with self.subTest(spelling=text):
                self.successful(value, text)
        longest = "0." + "0" * 125 + "1"
        self.assertEqual(len(longest), 128)
        self.successful(float(longest), longest)

    def test_strict_cli_rejection_leaves_stdout_empty(self):
        bad_values = ("", " ", " 0.5", "0.5 ", "\t0.5", "0.5\n", ".", "+", "-",
                      "nan", "NaN", "inf", "-inf", "Infinity", "0x1p-1", "0x0.8",
                      "0,5", "1_0", "0.5garbage", "1e", "--help", "-0.0001",
                      "-5e-324", "1.0000000000000002", "2", "1e309", "1e-9999",
                      "0" * 129, "0." + "0" * 126 + "1")
        arguments = [("--normalized", value) for value in bad_values]
        arguments += [("--normalized",), ("--unknown",), ("--normalized=0.5",),
                      ("0.5",), ("--help", "extra"), ("--help", "--normalized", "0.5"),
                      ("--normalized", "0.5", "--help"),
                      ("--normalized", "0.5", "--normalized", "0.25"),
                      ("--normalized", "0.5", "extra")]
        for args in arguments:
            with self.subTest(arguments=args):
                result = self.invoke(args)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, b"")
                self.assertTrue(result.stderr)

    def test_help_and_environment_do_not_mutate_default_metadata(self):
        help_result = self.invoke(("--help",))
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        self.assertEqual(help_result.stderr, b"")
        self.assertIn(b"--normalized", help_result.stdout)
        self.assertIn(b"47 compiled internal parameter mappings", help_result.stdout)
        self.assertLess(len(help_result.stdout), 4096)
        baseline = self.invoke()
        for locale_name in ("C", "de_DE.UTF-8", "fr_FR.UTF-8"):
            environment = dict(os.environ, LC_ALL=locale_name, LC_NUMERIC=locale_name)
            result = self.invoke(env=environment)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stderr, b"")
            self.assertEqual(result.stdout, baseline.stdout)
        self.inspect(baseline.stdout, 0.5)

    def test_export_scope_distinguishes_registry_provenance_from_native_verification(self):
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stderr)
        data = self.inspect(result.stdout, 0.5)
        # Schema 2 describes this SDK-free invocation. The frozen registry's
        # original authoring provenance is not a live native capability report.
        self.assertNotIn("native_host_curves_implemented", data)
        self.assertNotIn("native_module_path", data)
        self.assertNotIn("native_module_sha256", data)
        help_result = self.invoke(("--help",))
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        self.assertIn(b"SDK-free compiled core mapping", help_result.stdout)
        self.assertIn(b"does not inspect a native module", help_result.stdout)
        self.assertIn(b"artifact-specific verification", help_result.stdout)
        self.assertNotIn(b"no native host exports or curves are verified", help_result.stdout)

    def test_portable_stdout_failure_is_reported_and_preserves_file(self):
        with tempfile.TemporaryDirectory(prefix="hammond parameter output ") as temporary:
            path = Path(temporary) / "read-only-output.bin"
            original = b"retained stdout destination\n"
            path.write_bytes(original)
            with path.open("rb", buffering=0) as output:
                type(self).calls += 1
                result = subprocess.run([str(self.executable)], stdout=output,
                                        stderr=subprocess.PIPE, timeout=15, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(b"stdout", result.stderr.lower())
            self.assertEqual(path.read_bytes(), original)

    def test_legacy_record_identity_remains_independently_frozen(self):
        historical = sorted((record for record in self.registry["parameters"]
                             if record["id"] in LEGACY_IDS), key=lambda record: record["id"])
        self.assertEqual(len(historical), 39)
        canonical = json.dumps(historical, sort_keys=True, separators=(",", ":"),
                               ensure_ascii=True).encode("ascii")
        self.assertEqual(hashlib.sha256(canonical).hexdigest(), LEGACY_DIGEST)
        converted = self.successful(0.375)
        for record in converted["parameters"]:
            if record["id"] in LEGACY_IDS:
                event = registry_api.normalized_to_event(self.registry, record["id"], 0.375)
                self.assertEqual(record["event"], {"offset": 0, **event})

    def test_all_43_previous_records_keep_their_independent_compatibility_digest(self):
        historical = sorted((record for record in self.registry["parameters"]
                             if record["id"] in VERSION_2_IDS), key=lambda record: record["id"])
        self.assertEqual(len(historical), 43)
        canonical = json.dumps(historical, sort_keys=True, separators=(",", ":"),
                               ensure_ascii=True).encode("ascii")
        self.assertEqual(hashlib.sha256(canonical).hexdigest(), VERSION_2_DIGEST)
        frozen = json.loads((ROOT / "data" / "references" / "parameter-registry-v2.json").read_bytes())
        self.assertEqual(historical, sorted(frozen["parameters"], key=lambda record: record["id"]))

    def test_all_45_previous_records_keep_their_independent_compatibility_digest(self):
        historical = sorted((record for record in self.registry["parameters"]
                             if record["id"] in VERSION_3_IDS), key=lambda record: record["id"])
        self.assertEqual(len(historical), 45)
        canonical = json.dumps(historical, sort_keys=True, separators=(",", ":"),
                               ensure_ascii=True).encode("ascii")
        self.assertEqual(hashlib.sha256(canonical).hexdigest(), VERSION_3_DIGEST)

    def test_presets_export_exact_targets_and_downward_rounded_equality(self):
        for numerator in (3, 5, 7, 15, 17):
            threshold = nearest_binary64(numerator, 22)
            self.assertLess(Fraction.from_float(threshold), Fraction(numerator, 22))
            result = self.successful(threshold)
            by_id = {record["id"]: record for record in result["parameters"]}
            for identifier, manual in ((20480, "upper"), (20481, "lower")):
                record = by_id[identifier]
                self.assertEqual(record["path"], f"manual.{manual}.preset_selection")
                self.assertEqual(record["kind"], "preset_selector")
                self.assertEqual(record["unit"], "preset-key-index")
                self.assertEqual(record["step_count"], 11)
                self.assertEqual(record["default_plain"], 11)
                self.assertEqual(record["default_normalized"], 1)
                self.assertEqual(record["event"], {"offset": 0, "type": "select_preset",
                                                   "manual": manual, "index": 0,
                                                   "value": (numerator + 1) // 2})

    def test_pedal_mixture_records_export_canonical_lower_targets(self):
        converted = self.successful(0.5)
        by_id = {record["id"]: record for record in converted["parameters"]}
        for index, identifier in enumerate((16384, 16385)):
            record = by_id[identifier]
            self.assertEqual(record["path"], f"pedal.drawbar.mixture{index + 1}")
            self.assertEqual(record["kind"], "pedal_drawbar_position")
            self.assertEqual(record["unit"], "drawbar-position")
            self.assertEqual(record["step_count"], 8)
            self.assertEqual(record["default_plain"], 0)
            self.assertEqual(record["event"], {"offset": 0, "type": "pedal_drawbar",
                                               "manual": "lower", "index": index, "value": 4})


if __name__ == "__main__":
    unittest.main()
