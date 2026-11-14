#!/usr/bin/env python3
"""Independent integer/rational acceptance of the appended preset parameters.

CTest supplies both actual native executables. Missing executables or an
unavailable rounding environment fail rather than silently skip native checks.
No expected threshold or canonical value is imported from production tables.
"""

from __future__ import annotations

from contextlib import contextmanager
import ctypes
from fractions import Fraction
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import struct
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "preset_oracle_actual_parameter_api", ROOT / "tools" / "validate_parameters.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Cannot load the actual Python parameter conversion API")
API = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(API)

ONE = 0x3FF0000000000000
NEGATIVE_ZERO = 0x8000000000000000
HALF = 0x3FE0000000000000
NEW_IDS = (20480, 20481)
OLD_IDS = (set(range(4096, 4105)) | set(range(4112, 4121)) |
           set(range(4128, 4137)) | set(range(4144, 4153)) |
           {8192, 8208, 8209, 12288, 12289, 12290, 12291, 16384, 16385})
OLD45_DIGEST = "13ba488bec90154c960c3fd700dc4a774aff5664caf5d68472821493f22d1cad"
REPRESENTATIVES = {4096: 8, 8192: 0, 8208: 1, 12288: 1, 16384: 8}
UNKNOWN_IDS = (0, 4095, 4105, 4111, 4121, 4127, 4137, 4143, 4153, 8191, 8193,
               8207, 8210, 12287, 12292, 16383, 16386, 20479, 20482,
               0x7FFFFFFF, 0xFFFFFFFF)


def decode(raw):
    return struct.unpack("!d", struct.pack("!Q", raw))[0]


def encode(value):
    return struct.unpack("!Q", struct.pack("!d", float(value)))[0]


def nearest_ratio_bits(numerator, denominator):
    """Round a nonnegative normal ratio <= 1 using integer quotient/remainder.

    Normalize n/d to [1,2), form its 53-bit significand, and round the integer
    quotient to nearest with ties to even. The returned bits never depend on
    Python floating-point division, float.fromhex, or a production lookup table.
    """
    if not 0 <= numerator <= denominator or denominator <= 0:
        raise ValueError("oracle requires 0 <= numerator <= denominator")
    if numerator == 0:
        return 0
    exponent = 0
    while numerator < denominator:
        numerator <<= 1
        exponent -= 1
    significand, remainder = divmod(numerator << 52, denominator)
    if 2 * remainder > denominator or (2 * remainder == denominator and significand & 1):
        significand += 1
    if significand == 1 << 53:
        significand >>= 1
        exponent += 1
    if not -1022 <= exponent <= 0:
        raise ValueError("oracle requires a normal binary64 result")
    return ((exponent + 1023) << 52) | (significand - (1 << 52))


def exact_binary64(raw):
    """Decode finite binary64 directly to a Fraction; no float conversion."""
    sign = -1 if raw >> 63 else 1
    exponent = (raw >> 52) & 0x7FF
    significand = raw & ((1 << 52) - 1)
    if exponent == 0x7FF:
        raise ValueError("nonfinite binary64 has no rational value")
    if exponent:
        significand |= 1 << 52
        power = exponent - 1075
    else:
        power = -1074
    return (Fraction(sign * (significand << power), 1) if power >= 0 else
            Fraction(sign * significand, 1 << -power))


THRESHOLDS = tuple(nearest_ratio_bits(2 * k + 1, 22) for k in range(11))
CANONICAL = tuple(nearest_ratio_bits(k, 11) for k in range(12))


def preset_value(raw):
    # Positive binary64 encodings have the same ordering as their numeric values.
    return 0 if raw == NEGATIVE_ZERO else sum(raw >= threshold for threshold in THRESHOLDS)


def old_value(raw, steps):
    if not steps:
        return decode(raw)
    value = exact_binary64(raw)
    shifted = value * steps + Fraction(1, 2)
    return shifted.numerator // shifted.denominator


def required_executable(variable, target):
    value = os.environ.get(variable)
    if not value or not Path(value).is_file():
        raise RuntimeError(f"Missing {variable}; build {target} and run CTest, or set its "
                           "explicit path. Required native checks were not run.")
    return Path(value).resolve()


class RoundingEnvironment:
    def __init__(self):
        candidates = (None, "ucrtbase.dll") if sys.platform == "win32" else (None,)
        for candidate in candidates:
            try:
                library = ctypes.CDLL(candidate)
                get = library.fegetround
                set_mode = library.fesetround
            except (OSError, AttributeError):
                continue
            get.argtypes = []
            get.restype = ctypes.c_int
            set_mode.argtypes = [ctypes.c_int]
            set_mode.restype = ctypes.c_int
            self.library, self.get, self.set_mode = library, get, set_mode
            break
        else:
            raise RuntimeError("Cannot access fegetround/fesetround; four-mode Python checks not run")
        if self.get() == -1:
            raise RuntimeError("Cannot read Python caller's floating-point rounding mode")

    @contextmanager
    def mode(self, code):
        original = self.get()
        if self.set_mode(code) != 0 or self.get() != code:
            self.set_mode(original)
            raise RuntimeError(f"Required native-reported rounding mode {code} is unavailable")
        try:
            yield
        finally:
            if self.set_mode(original) != 0 or self.get() != original:
                raise RuntimeError("Could not restore Python caller's rounding mode")


class PresetParameterOracleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.executable = required_executable("HAMMOND_PARAMETER_INFO_EXECUTABLE",
                                             "hammond_parameter_info")
        probe = required_executable("HAMMOND_PRESET_PARAMETER_BOUNDARIES_EXECUTABLE",
                                    "test_preset_parameter_boundaries")
        cls.registry = API.load_registry(ROOT / "data" / "parameter-registry.json")
        cls.by_id = {record["id"]: record for record in cls.registry["parameters"]}
        cls.fenv = RoundingEnvironment()
        result = subprocess.run([str(probe), "--vectors"], capture_output=True,
                                text=True, check=False, timeout=20)
        if result.returncode or result.stderr:
            raise RuntimeError(f"Native four-mode oracle failed: {result.stderr or result.stdout}")
        lines = result.stdout.splitlines()
        if not lines or lines[0] != "preset-parameter-boundaries-v1":
            raise RuntimeError("Unexpected native oracle protocol")
        cls.modes, cls.samples = {}, {}
        for line in lines[1:-1]:
            fields = line.split()
            if len(fields) == 3 and fields[0] == "mode":
                if fields[1] in cls.modes:
                    raise RuntimeError("Duplicate native rounding mode")
                cls.modes[fields[1]] = int(fields[2])
            elif len(fields) == 6 and fields[0] == "sample":
                _, mode, operation, identifier, raw_input, raw_output = fields
                key = (mode, operation, int(identifier), int(raw_input, 16))
                if key in cls.samples:
                    raise RuntimeError("Duplicate native conversion vector")
                cls.samples[key] = int(raw_output, 16)
            else:
                raise RuntimeError(f"Malformed native oracle line: {line}")
        cls.summary = tuple(int(count) for count in lines[-1].split()[1:])
        if (lines[-1].split()[0] != "complete" or cls.summary != (688, 296, 84) or
                len(cls.samples) != cls.summary[0] or
                set(cls.modes) != {"nearest", "downward", "upward", "towardzero"} or
                len(set(cls.modes.values())) != 4):
            raise RuntimeError("Incomplete native boundary, rejection, or four-mode coverage")
        cls.cli_calls = 0

    @classmethod
    def tearDownClass(cls):
        print(f"preset parameter oracle: {len(cls.samples)} actual native vectors, "
              f"{cls.summary[1]} atomic conversion rejections, {cls.summary[2]} descriptor "
              f"rejections; {cls.cli_calls} actual 47-record CLI calls; four Python modes")

    def test_integer_construction_has_exact_nearest_even_certificates(self):
        cases = [(k, 11, CANONICAL[k]) for k in range(12)]
        cases += [(2 * k + 1, 22, THRESHOLDS[k]) for k in range(11)]
        for numerator, denominator, raw in cases:
            with self.subTest(ratio=(numerator, denominator)):
                exact = Fraction(numerator, denominator)
                if raw == 0:
                    self.assertEqual(exact, 0)
                    continue
                value = exact_binary64(raw)
                lower_midpoint = (exact_binary64(raw - 1) + value) / 2
                upper_midpoint = (value + exact_binary64(raw + 1)) / 2
                self.assertLessEqual(lower_midpoint, exact)
                self.assertLessEqual(exact, upper_midpoint)
                if exact in (lower_midpoint, upper_midpoint):
                    self.assertEqual(raw & 1, 0)
        # Exercise both tie directions and a carry to 1.0 in the oracle itself.
        for numerator, denominator, expected in (
                ((1 << 53) + 1, 1 << 54, HALF),
                ((1 << 53) + 3, 1 << 54, HALF + 2),
                ((1 << 54) - 1, 1 << 54, ONE)):
            self.assertEqual(nearest_ratio_bits(numerator, denominator), expected)
        downward = [2 * k + 1 for k, raw in enumerate(THRESHOLDS)
                    if exact_binary64(raw) < Fraction(2 * k + 1, 22)]
        self.assertEqual(downward, [3, 5, 7, 15, 17])
        for raw in THRESHOLDS:
            self.assertEqual(encode(math.nextafter(decode(raw), 0.0)), raw - 1)
            self.assertEqual(encode(math.nextafter(decode(raw), 1.0)), raw + 1)

    def test_complete_old45_identity_and_exact_appended_metadata(self):
        self.assertEqual(set(self.by_id), OLD_IDS | set(NEW_IDS))
        old = [self.by_id[identifier] for identifier in sorted(OLD_IDS)]
        self.assertEqual(len(old), 45)
        payload = json.dumps(old, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=True).encode("ascii")
        self.assertEqual(hashlib.sha256(payload).hexdigest(), OLD45_DIGEST)
        self.assertEqual(self.registry["schema_version"], 4)
        self.assertEqual(self.registry["model"], "exclusive-fixed-percussion-pedal-console-v4")
        pages = [50, 52, 121, 122, 124, 126, 153, 389, 397, 398, 401, 402, 410, 415, 418]
        for identifier, manual in zip(NEW_IDS, ("upper", "lower")):
            self.assertEqual(self.by_id[identifier], {
                "id": identifier, "path": f"manual.{manual}.preset_selection",
                "label": f"{manual.title()} preset selection", "kind": "preset_selector",
                "unit": "preset-key-index", "minimum": 0, "maximum": 11,
                "default": 11, "step_count": 11, "evidence_class": "proposed",
                "source_pages": pages,
                "engine_event": {"type": "select_preset", "manual": manual, "index": 0},
                "normalized": {
                    "minimum": 0.0, "maximum": 1.0, "default": 1.0,
                    "meaning": "exclusive-preset-key-index-fraction",
                    "to_plain": "count(u >= nearest-binary64((2*k+1)/22), k=0..10)",
                    "to_normalized": "nearest-binary64(x / 11)",
                },
            })

    def test_new_selectors_agree_bit_for_bit_in_all_four_modes(self):
        normalized_inputs = {raw + delta for raw in THRESHOLDS for delta in (-1, 0, 1)}
        normalized_inputs.update(CANONICAL)
        normalized_inputs.update((NEGATIVE_ZERO, 1, 0x0010000000000000, ONE - 1))
        plain_inputs = {encode(k): CANONICAL[k] for k in range(12)}
        plain_inputs[NEGATIVE_ZERO] = 0
        expected_keys = set()
        for name, code in self.modes.items():
            with self.fenv.mode(code):
                # Re-derive the bits in each mode, rather than merely trusting
                # values constructed before the caller mode was changed.
                self.assertEqual(tuple(nearest_ratio_bits(k, 11) for k in range(12)), CANONICAL)
                for identifier in NEW_IDS:
                    record = self.by_id[identifier]
                    for raw in normalized_inputs:
                        key = (name, "N", identifier, raw)
                        expected_keys.add(key)
                        expected = encode(preset_value(raw))
                        self.assertEqual(self.samples[key], expected, key)
                        event = API.normalized_to_event(self.registry, identifier, decode(raw))
                        self.assertEqual(event, {**record["engine_event"], "value": preset_value(raw)})
                        self.assertEqual(encode(event["value"]), expected, key)
                        self.assertEqual(encode(API.normalized_to_value(record, decode(raw))), expected, key)
                        self.assertEqual(self.fenv.get(), code)
                    for raw, expected in plain_inputs.items():
                        key = (name, "P", identifier, raw)
                        expected_keys.add(key)
                        self.assertEqual(self.samples[key], expected, key)
                        self.assertEqual(encode(API.value_to_normalized(record, decode(raw))), expected, key)
                        self.assertEqual(self.fenv.get(), code)
        actual_keys = {key for key in self.samples if key[2] in NEW_IDS}
        self.assertEqual(actual_keys, expected_keys)
        self.assertEqual(len(expected_keys), 496)

    def test_legacy_conversions_keep_their_original_zero_semantics(self):
        native_keys = set()
        observed_old_zero_differences = 0
        for name, code in self.modes.items():
            with self.fenv.mode(code):
                for identifier, steps in REPRESENTATIVES.items():
                    record = self.by_id[identifier]
                    for raw in (NEGATIVE_ZERO, 1, HALF - 1, HALF, HALF + 1, ONE):
                        key = (name, "N", identifier, raw)
                        native_keys.add(key)
                        expected = encode(old_value(raw, steps))
                        self.assertEqual(self.samples[key], expected, key)
                        self.assertEqual(encode(API.normalized_to_value(record, decode(raw))), expected, key)
                    maximum = 8 if steps == 8 else 1
                    pairs = [(NEGATIVE_ZERO, NEGATIVE_ZERO), (0, 0), (encode(maximum), ONE)]
                    if steps == 8:
                        pairs.append((encode(4), HALF))
                    if steps == 0:
                        pairs.append((0x3FD8000000000000, 0x3FD8000000000000))
                    for raw, expected in pairs:
                        key = (name, "P", identifier, raw)
                        native_keys.add(key)
                        self.assertEqual(self.samples[key], expected, key)
                        # Baseline Python subtraction preserves a distinct old
                        # +0 -> -0 result in downward mode. New selectors have
                        # no such exception. Do not silently rewrite old laws.
                        python_expected = NEGATIVE_ZERO if raw == 0 and name == "downward" else expected
                        actual = encode(API.value_to_normalized(record, decode(raw)))
                        self.assertEqual(actual, python_expected, key)
                        observed_old_zero_differences += actual != self.samples[key]
                        self.assertEqual(self.fenv.get(), code)
                for identifier in OLD_IDS:
                    record = self.by_id[identifier]
                    for raw in (0, NEGATIVE_ZERO):
                        expected = NEGATIVE_ZERO if raw or name == "downward" else 0
                        self.assertEqual(encode(API.value_to_normalized(record, decode(raw))), expected)
                    self.assertEqual(encode(API.value_to_normalized(record, record["maximum"])), ONE)
                    self.assertEqual(self.fenv.get(), code)
        self.assertEqual(native_keys, {key for key in self.samples if key[2] in OLD_IDS})
        self.assertEqual(len(native_keys), 192)
        self.assertEqual(observed_old_zero_differences, 5)

    def test_python_rejections_preserve_registry_and_caller_mode(self):
        original = json.dumps(self.registry, sort_keys=True, separators=(",", ":"))
        invalid_normalized = (NEGATIVE_ZERO + 1, ONE + 1, encode(2),
                              0x7FF0000000000000, 0xFFF0000000000000,
                              0x7FF8000000001234, 0xFFF8000000005678)
        invalid_plain = (NEGATIVE_ZERO + 1, encode(11) + 1, encode(12), encode(0.5),
                         ONE - 1, 1, 0x7FF0000000000000, 0xFFF0000000000000,
                         0x7FF8000000001234)
        for name, code in self.modes.items():
            with self.fenv.mode(code):
                for identifier in NEW_IDS:
                    record = self.by_id[identifier]
                    for raw in invalid_normalized:
                        with self.assertRaises(API.ParameterError, msg=(name, identifier, raw)):
                            API.normalized_to_event(self.registry, identifier, decode(raw))
                        self.assertEqual(self.fenv.get(), code)
                    for raw in invalid_plain:
                        with self.assertRaises(API.ParameterError, msg=(name, identifier, raw)):
                            API.value_to_normalized(record, decode(raw))
                        self.assertEqual(self.fenv.get(), code)
                for identifier in UNKNOWN_IDS:
                    with self.assertRaises(API.ParameterError, msg=(name, identifier)):
                        API.normalized_to_event(self.registry, identifier, 0.5)
                    self.assertEqual(self.fenv.get(), code)
        self.assertEqual(json.dumps(self.registry, sort_keys=True, separators=(",", ":")), original)

    def test_actual_cli_matches_oracle_for_every_threshold_and_canonical(self):
        inputs = {raw + delta for raw in THRESHOLDS for delta in (-1, 0, 1)}
        inputs.update(CANONICAL)
        inputs.update((NEGATIVE_ZERO, 1, 0x0010000000000000, ONE - 1))
        for raw in sorted(inputs):
            value = decode(raw)
            type(self).cli_calls += 1
            result = subprocess.run([str(self.executable), "--normalized", repr(value)],
                                    capture_output=True, check=False, timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stderr, b"")
            data = json.loads(result.stdout, parse_int=lambda text: -0.0 if text == "-0" else int(text))
            self.assertEqual(encode(data["normalized"]), raw)
            self.assertEqual(data["registry_schema_version"], 4)
            self.assertEqual(data["model"], "exclusive-fixed-percussion-pedal-console-v4")
            self.assertEqual(len(data["parameters"]), 47)
            self.assertEqual({record["id"] for record in data["parameters"]}, OLD_IDS | set(NEW_IDS))
            for actual in data["parameters"]:
                record = self.by_id[actual["id"]]
                for field in ("path", "kind", "unit", "minimum", "maximum", "step_count"):
                    self.assertEqual(actual[field], record[field])
                self.assertEqual(actual["default_plain"], record["default"])
                self.assertEqual(actual["default_normalized"], record["normalized"]["default"])
                expected = (preset_value(raw) if actual["id"] in NEW_IDS else
                            old_value(raw, record["step_count"]))
                self.assertEqual(actual["event"], {"offset": 0, **record["engine_event"], "value": expected})
                self.assertEqual(encode(actual["event"]["value"]), encode(expected))
                self.assertEqual(encode(API.normalized_to_value(record, value)), encode(expected))
        self.assertEqual(type(self).cli_calls, 49)


if __name__ == "__main__":
    unittest.main()
