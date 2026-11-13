#!/usr/bin/env python3
"""Tests of proposed metadata and scalar conversion, not host or DSP behavior."""

from __future__ import annotations

import copy
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "tools" / "validate_parameters.py"
REGISTRY_PATH = ROOT / "data" / "parameter-registry.json"
SPEC = importlib.util.spec_from_file_location("hammond_parameter_registry", VALIDATOR_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {VALIDATOR_PATH}")
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)
REGISTRY = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def at_path(value, path):
    for key in path:
        value = value[key]
    return value


class ParameterTests(unittest.TestCase):
    def setUp(self):
        self.registry = copy.deepcopy(REGISTRY)
        self.by_id = {parameter["id"]: parameter for parameter in self.registry["parameters"]}

    def reject_change(self, path, value):
        registry = copy.deepcopy(REGISTRY)
        at_path(registry, path[:-1])[path[-1]] = value
        with self.assertRaises(validator.ParameterError):
            validator.validate_registry(registry)

    def test_exact_39_id_inventory_and_defaults(self):
        expected = set(range(4096, 4105)) | set(range(4112, 4121))
        expected |= set(range(4128, 4137)) | set(range(4144, 4153))
        expected |= {8192, 8208, 8209}
        self.assertEqual(set(self.by_id), expected)
        self.assertEqual(len(self.registry["parameters"]), 39)
        self.assertIsNone(validator.validate_registry(self.registry))
        self.assertEqual(validator.load_registry(REGISTRY_PATH), self.registry)
        for identifier, parameter in self.by_id.items():
            self.assertEqual(parameter["default"], 0 if identifier < 8192 else 1)
            self.assertEqual(parameter["normalized"]["default"], 0.0 if identifier < 8192 else 1.0)
        self.assertEqual(sum(p["kind"] == "drawbar_position" for p in self.by_id.values()), 36)
        self.assertEqual(sum(p["kind"] == "bank_selector" for p in self.by_id.values()), 2)

    def test_all_four_banks_have_permanent_distinct_targets(self):
        expected_banks = ((4096, "upper", "A", 0), (4112, "upper", "B", 9),
                          (4128, "lower", "A", 0), (4144, "lower", "B", 9))
        targets = set()
        for base, manual, bank, first_index in expected_banks:
            for drawbar in range(9):
                parameter = self.by_id[base + drawbar]
                self.assertIn(f"manual.{manual}.bank.{bank}.drawbar.", parameter["path"])
                self.assertEqual(parameter["engine_event"], {
                    "type": "bank_drawbar", "manual": manual, "index": first_index + drawbar})
                targets.add((manual, first_index + drawbar))
        self.assertEqual(len(targets), 36)

    def test_expression_is_one_global_surrogate(self):
        expression = self.by_id[8192]
        self.assertEqual(expression["path"], "global.expression")
        self.assertEqual(expression["unit"], "normalized-linear-gain-surrogate")
        self.assertEqual(expression["step_count"], 0)
        self.assertEqual(validator.normalized_to_event(self.registry, 8192, 0.37),
                         {"type": "expression", "manual": "upper", "index": 0, "value": 0.37})

    def test_selectors_are_exclusive_ab_and_cancel_is_excluded(self):
        for identifier, manual in ((8208, "upper"), (8209, "lower")):
            self.assertEqual(self.by_id[identifier]["unit"], "bank-index-0=A-1=B")
            self.assertEqual(self.by_id[identifier]["step_count"], 1)
            self.assertEqual(validator.normalized_to_event(self.registry, identifier, 0.0),
                             {"type": "select_bank", "manual": manual, "index": 0, "value": 0})
            self.assertEqual(validator.normalized_to_event(self.registry, identifier, 1.0)["value"], 1)
        self.assertEqual({p["engine_event"]["type"] for p in self.by_id.values()},
                         {"bank_drawbar", "select_bank", "expression"})
        self.assertTrue(all("cancel" not in p["path"] for p in self.by_id.values()))

    def test_proposed_evidence_and_pending_host_scope(self):
        self.assertEqual(self.registry["status"], "proposed-internal")
        provenance = self.registry["provenance"]
        for key in ("companion_recovered", "host_exports_verified", "native_host_curves_implemented"):
            self.assertIs(provenance[key], False)
            self.reject_change(("provenance", key), True)
        for parameter in self.by_id.values():
            self.assertEqual(parameter["evidence_class"], "proposed")
            self.assertIn(402, parameter["source_pages"])

    def test_validation_is_read_only_and_record_order_is_not_identity(self):
        before = copy.deepcopy(self.registry)
        validator.validate_registry(self.registry)
        self.assertEqual(self.registry, before)
        self.registry["parameters"].reverse()
        validator.validate_registry(self.registry)
        for identifier in (4096, 4112, 4128, 4144, 8192, 8208, 8209):
            self.assertEqual(validator.normalized_to_event(self.registry, identifier, 0.5),
                             validator.normalized_to_event(before, identifier, 0.5))

    def test_version_model_scope_and_status_are_exact(self):
        for key, bad in (("schema_version", 2), ("schema_version", True),
                         ("model", "measured-console"), ("scope", "full-62-parameter-atlas"),
                         ("status", "exported-vst3")):
            with self.subTest(key=key, value=bad):
                self.reject_change((key,), bad)

    def test_missing_extra_and_colliding_identities_reject(self):
        for operation in ("remove", "append", "duplicate"):
            candidate = copy.deepcopy(REGISTRY)
            if operation == "remove":
                candidate["parameters"].pop()
            elif operation == "append":
                candidate["parameters"].append(copy.deepcopy(candidate["parameters"][0]))
            else:
                candidate["parameters"][1] = copy.deepcopy(candidate["parameters"][0])
            with self.subTest(operation=operation), self.assertRaises(validator.ParameterError):
                validator.validate_registry(candidate)
        self.reject_change(("parameters", 1, "id"), 4096)
        self.reject_change(("parameters", 1, "path"), self.by_id[4096]["path"])
        self.reject_change(("parameters", 1, "engine_event", "index"), 0)
        self.reject_change(("parameters", 0, "id"), 4105)  # Deliberate gap is not an allocated ID.

    def test_bank_identity_cannot_follow_a_visible_or_selected_bank(self):
        self.reject_change(("parameters", 0, "engine_event", "type"), "drawbar")
        self.reject_change(("parameters", 0, "engine_event", "index"), 9)
        self.reject_change(("parameters", 0, "engine_event", "manual"), "lower")
        self.reject_change(("parameters", 9, "path"), "manual.upper.selected.drawbar.16ft")
        before = validator.normalized_to_event(self.registry, 4096, 0.5)
        for identifier in (8208, 8209):
            validator.normalized_to_event(self.registry, identifier, 0.0)
            validator.normalized_to_event(self.registry, identifier, 1.0)
        self.assertEqual(validator.normalized_to_event(self.registry, 4096, 0.5), before)
        self.assertEqual(before["index"], 0)
        self.assertEqual(validator.normalized_to_event(self.registry, 4112, 0.5)["index"], 9)

    def test_drawbar_normalization_is_position_not_amplitude(self):
        parameter = self.by_id[4096]
        self.assertEqual(parameter["unit"], "drawbar-position")
        self.assertEqual(parameter["normalized"]["meaning"], "position-fraction-not-amplitude")
        self.assertEqual(validator.normalized_to_value(parameter, 0.5), 4)
        self.assertEqual(validator.normalized_to_event(self.registry, 4096, 0.5)["value"], 4)
        self.assertEqual(validator.value_to_normalized(parameter, 4), 0.5)
        self.reject_change(("parameters", 0, "unit"), "linear-amplitude")
        self.reject_change(("parameters", 0, "normalized", "meaning"), "audio-amplitude")
        self.reject_change(("parameters", 0, "normalized", "to_plain"), "u")
        self.reject_change(("parameters", 0, "step_count"), 0)

    def test_exact_targets_ranges_defaults_steps_and_source_pages(self):
        bad_fields = (("minimum", -1), ("maximum", 9), ("default", 8),
                      ("step_count", 9), ("evidence_class", "measured"),
                      ("source_pages", [397]), ("label", "Unrelated control"))
        for key, value in bad_fields:
            with self.subTest(key=key):
                self.reject_change(("parameters", 0, key), value)
        self.reject_change(("parameters", 36, "default"), 0)
        self.reject_change(("parameters", 37, "default"), 0)
        self.reject_change(("parameters", 38, "engine_event", "index"), 1)
        self.reject_change(("parameters", 37, "normalized", "default"), 0.0)
        self.reject_change(("parameters", 37, "normalized", "to_plain"), "floor(u * 2)")

    def test_unknown_or_missing_keys_reject_at_every_object_level(self):
        paths = ((), ("provenance",), ("parameters", 0),
                 ("parameters", 0, "normalized"), ("parameters", 0, "engine_event"))
        for path in paths:
            for operation in ("unknown", "missing"):
                candidate = copy.deepcopy(REGISTRY)
                target = at_path(candidate, path)
                if operation == "unknown":
                    target["unexpected"] = 0
                else:
                    del target[next(iter(target))]
                with self.subTest(path=path, operation=operation), self.assertRaises(validator.ParameterError):
                    validator.validate_registry(candidate)

    def test_nonfinite_domains_and_boolean_numbers_reject(self):
        for index in (0, 36, 37):
            for path in (("minimum",), ("maximum",), ("default",),
                         ("normalized", "minimum"), ("normalized", "maximum"), ("normalized", "default")):
                for value in (float("nan"), float("inf"), -float("inf"), True, 10 ** 400):
                    with self.subTest(index=index, path=path, value_type=type(value).__name__):
                        self.reject_change(("parameters", index) + path, value)
        for path in (("parameters", 0, "id"), ("parameters", 0, "step_count"),
                     ("parameters", 0, "engine_event", "index"),
                     ("parameters", 0, "source_pages", 0)):
            self.reject_change(path, True)
        for value in (-1, 1 << 32, 4096.0, "4096", None):
            self.reject_change(("parameters", 0, "id"), value)

    def test_all_canonical_values_round_trip(self):
        for parameter in self.by_id.values():
            values = (0.0, 0.125, 0.37, 1.0) if parameter["kind"] == "expression" else range(parameter["maximum"] + 1)
            for plain in values:
                with self.subTest(identifier=parameter["id"], plain=plain):
                    normalized = validator.value_to_normalized(parameter, plain)
                    self.assertEqual(validator.normalized_to_value(parameter, normalized), plain)
            self.assertEqual(validator.normalized_to_value(parameter, 0), parameter["minimum"])
            self.assertEqual(validator.normalized_to_value(parameter, 1), parameter["maximum"])

    def test_round_half_up_at_and_immediately_around_every_threshold(self):
        for identifier, count in ((4096, 8), (8208, 1), (8209, 1)):
            for lower in range(count):
                threshold = (lower + 0.5) / count
                parameter = self.by_id[identifier]
                with self.subTest(identifier=identifier, threshold=threshold):
                    self.assertEqual(validator.normalized_to_value(parameter, math.nextafter(threshold, 0.0)), lower)
                    self.assertEqual(validator.normalized_to_value(parameter, threshold), lower + 1)
                    self.assertEqual(validator.normalized_to_value(parameter, math.nextafter(threshold, 1.0)), lower + 1)

    def test_conversion_rejects_nonfinite_and_out_of_range_without_clipping(self):
        for identifier in (4096, 8192, 8208):
            parameter = self.by_id[identifier]
            for invalid in (-0.001, math.nextafter(1.0, math.inf), float("nan"),
                            float("inf"), -float("inf"), True, "0.5", None, 10 ** 400):
                with self.subTest(identifier=identifier, invalid_type=type(invalid).__name__):
                    with self.assertRaises(validator.ParameterError):
                        validator.normalized_to_value(parameter, invalid)
                    with self.assertRaises(validator.ParameterError):
                        validator.normalized_to_event(self.registry, identifier, invalid)
            for invalid in (-1, parameter["maximum"] + 1, float("nan"), float("inf"), True):
                with self.assertRaises(validator.ParameterError):
                    validator.value_to_normalized(parameter, invalid)
        for identifier in (4096, 8208):
            with self.assertRaises(validator.ParameterError):
                validator.value_to_normalized(self.by_id[identifier], 0.5)

    def test_event_mapping_rejects_unknown_id_and_returns_an_independent_payload(self):
        for invalid in (4105, -1, 1 << 32, True, 4096.0, "4096"):
            with self.subTest(identifier=invalid), self.assertRaises(validator.ParameterError):
                validator.normalized_to_event(self.registry, invalid, 0.5)
        event = validator.normalized_to_event(self.registry, 4096, 0.5)
        self.assertEqual(set(event), {"type", "manual", "index", "value"})
        event["index"] = 17
        self.assertEqual(self.by_id[4096]["engine_event"]["index"], 0)
        self.assertEqual(self.registry, REGISTRY)
        self.registry["parameters"][0]["engine_event"]["index"] = 9
        before = copy.deepcopy(self.registry)
        with self.assertRaises(validator.ParameterError):
            validator.normalized_to_event(self.registry, 8192, 1.0)
        self.assertEqual(self.registry, before)

    def test_file_parser_rejects_duplicate_keys_nonfinite_and_malformed_input(self):
        good = json.dumps(REGISTRY)
        bad_inputs = [
            b'{"schema_version":1,"schema_version":1}',
            good.replace('"index": 0', '"index": 0, "index": 0', 1).encode(),
            good.replace('"maximum": 8', '"maximum": NaN', 1).encode(),
            good.replace('"maximum": 8', '"maximum": Infinity', 1).encode(),
            good.replace('"maximum": 8', '"maximum": 1e999', 1).encode(),
            good.encode() + b' trailing', b'\xff', b'[]',
            b'[' * 2000 + b']' * 2000,
            b' ' * (validator.MAX_INPUT_BYTES + 1),
        ]
        with tempfile.TemporaryDirectory(prefix="hammond parameters ") as directory:
            path = Path(directory) / "registry.json"
            for index, payload in enumerate(bad_inputs):
                path.write_bytes(payload)
                with self.subTest(index=index), self.assertRaises(validator.ParameterError):
                    validator.load_registry(path)
            with self.assertRaises(validator.ParameterError):
                validator.load_registry(Path(directory) / "missing.json")

    def test_cli_reports_valid_scope_and_rejects_bad_input(self):
        result = subprocess.run([sys.executable, str(VALIDATOR_PATH), str(REGISTRY_PATH)],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("39 proposed internal parameters", result.stdout)
        self.assertIn("host mapping remains pending", result.stdout)
        with tempfile.TemporaryDirectory(prefix="hammond parameters cli ") as directory:
            path = Path(directory) / "bad.json"
            path.write_text("{}", encoding="utf-8")
            result = subprocess.run([sys.executable, str(VALIDATOR_PATH), str(path)],
                                    capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 1)
            self.assertIn("validation failed", result.stderr)
            self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
