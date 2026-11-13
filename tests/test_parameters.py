#!/usr/bin/env python3
"""Tests of proposed metadata and scalar conversion, not host or DSP behavior."""

from __future__ import annotations

import copy
import hashlib
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

# Frozen from the original 39 full records at commit 7a24a30, before this extension.
# This oracle is independent of the validator's expected-record generator. Canonical
# encoding: sort records by numeric ID, sort keys recursively, compact ASCII JSON.
LEGACY_IDS = (set(range(4096, 4105)) | set(range(4112, 4121)) |
              set(range(4128, 4137)) | set(range(4144, 4153)) | {8192, 8208, 8209})
LEGACY_RECORDS_SHA256 = "61669b54e0a0499da950ece28c855e70ab4cb815d204f625f0aee8542d8b4f1b"

# Captured from committed parent 6768ef2388819ebbaaf7cc23bdf72265dc72c561
# before any pedal registry edits. Preserve this fixture and both digests.
VERSION_2_PATH = ROOT / "data" / "references" / "parameter-registry-v2.json"
VERSION_2_IDS = LEGACY_IDS | {12288, 12289, 12290, 12291}
VERSION_2_FILE_SHA256 = "658858a8e0f3e722ae1deef1c80e799ab5761c60213af22d5e80696996fd50f5"
VERSION_2_RECORDS_SHA256 = "5e161206e203cce130330b993590d892182c4ead62daba50b468b5348d70bed2"


def legacy_records_digest(parameters):
    records = sorted((p for p in parameters if p["id"] in LEGACY_IDS), key=lambda p: p["id"])
    canonical = json.dumps(records, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("ascii")).hexdigest()


def version_2_records_digest(parameters):
    records = sorted((p for p in parameters if p["id"] in VERSION_2_IDS), key=lambda p: p["id"])
    canonical = json.dumps(records, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("ascii")).hexdigest()


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

    def test_exact_45_id_inventory_and_defaults(self):
        expected = VERSION_2_IDS | {16384, 16385}
        self.assertEqual(set(self.by_id), expected)
        self.assertEqual(len(self.registry["parameters"]), 45)
        self.assertIsNone(validator.validate_registry(self.registry))
        self.assertEqual(validator.load_registry(REGISTRY_PATH), self.registry)
        for identifier, parameter in self.by_id.items():
            expected_default = 1 if identifier in (8192, 8208, 8209) else 0
            self.assertEqual(parameter["default"], expected_default)
            self.assertEqual(parameter["normalized"]["default"], float(expected_default))
        self.assertEqual(sum(p["kind"] == "drawbar_position" for p in self.by_id.values()), 36)
        self.assertEqual(sum(p["kind"] == "bank_selector" for p in self.by_id.values()), 2)
        self.assertEqual(sum(p["kind"] == "percussion_switch" for p in self.by_id.values()), 4)
        self.assertEqual(sum(p["kind"] == "pedal_drawbar_position" for p in self.by_id.values()), 2)

    def test_all_43_earlier_whole_records_match_immutable_committed_fixture(self):
        raw = VERSION_2_PATH.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), VERSION_2_FILE_SHA256)
        historical = json.loads(raw)
        self.assertEqual(historical["schema_version"], 2)
        self.assertEqual(historical["model"], "exclusive-ab-percussion-console-v2")
        self.assertEqual({p["id"] for p in historical["parameters"]}, VERSION_2_IDS)
        self.assertEqual(len(historical["parameters"]), 43)
        self.assertEqual(version_2_records_digest(historical["parameters"]), VERSION_2_RECORDS_SHA256)
        current = sorted((p for p in self.registry["parameters"] if p["id"] in VERSION_2_IDS),
                         key=lambda p: p["id"])
        self.assertEqual(current, sorted(historical["parameters"], key=lambda p: p["id"]))
        self.assertEqual(version_2_records_digest(self.registry["parameters"]), VERSION_2_RECORDS_SHA256)
        self.registry["parameters"].reverse()
        self.assertEqual(version_2_records_digest(self.registry["parameters"]), VERSION_2_RECORDS_SHA256)
        self.by_id[12290]["normalized"]["meaning"] = "audio-amplitude"
        self.assertNotEqual(version_2_records_digest(self.registry["parameters"]), VERSION_2_RECORDS_SHA256)

    def test_version_2_registry_document_requires_explicit_upgrade(self):
        historical = json.loads(VERSION_2_PATH.read_bytes())
        before = copy.deepcopy(historical)
        with self.assertRaisesRegex(validator.ParameterError, "registry.schema_version"):
            validator.validate_registry(historical)
        with self.assertRaisesRegex(validator.ParameterError, "registry.schema_version"):
            validator.load_registry(VERSION_2_PATH)
        self.assertEqual(historical, before)
        for record in historical["parameters"]:
            self.assertEqual(validator.normalized_to_value(record, 0.5),
                             validator.normalized_to_value(self.by_id[record["id"]], 0.5))

    def test_pedal_mixtures_have_distinct_permanent_position_targets(self):
        before = copy.deepcopy(self.registry)
        for index, identifier in enumerate((16384, 16385)):
            parameter = self.by_id[identifier]
            self.assertEqual(parameter["path"], f"pedal.drawbar.mixture{index + 1}")
            self.assertEqual(parameter["label"], f"Pedal Mixture {index + 1}")
            self.assertEqual(parameter["kind"], "pedal_drawbar_position")
            self.assertEqual(parameter["unit"], "drawbar-position")
            self.assertEqual((parameter["minimum"], parameter["maximum"], parameter["default"],
                              parameter["step_count"]), (0, 8, 0, 8))
            self.assertEqual(parameter["normalized"], {
                "minimum": 0.0, "maximum": 1.0, "default": 0.0,
                "to_plain": "floor(u * 8 + 0.5)", "to_normalized": "x / 8",
                "meaning": "position-fraction-not-amplitude"})
            for position in range(9):
                normalized = position / 8
                self.assertEqual(validator.value_to_normalized(parameter, position), normalized)
                self.assertEqual(validator.normalized_to_event(self.registry, identifier, normalized),
                                 {"type": "pedal_drawbar", "manual": "lower",
                                  "index": index, "value": position})
            # Manual bank selection and other pedal conversions carry no state.
            for selector in (8208, 8209):
                for selection in (0.0, 1.0):
                    validator.normalized_to_event(self.registry, selector, selection)
                    validator.normalized_to_event(self.registry, 16385 - index, 1.0)
                    self.assertEqual(validator.normalized_to_event(self.registry, identifier, 0.5),
                                     {"type": "pedal_drawbar", "manual": "lower",
                                      "index": index, "value": 4})
        self.assertEqual(self.registry, before)

    def test_pedal_records_cannot_be_reinterpreted_as_manual_or_audio_gain_controls(self):
        for index in (43, 44):
            for key, value in (("id", 16386), ("label", "16-foot calibrated pedal"),
                               ("kind", "drawbar_position"), ("unit", "linear-amplitude"),
                               ("maximum", 1), ("default", 8), ("step_count", 0),
                               ("source_pages", [139]), ("evidence_class", "measured")):
                with self.subTest(index=index, field=key):
                    self.reject_change(("parameters", index, key), value)
            for key, value in (("type", "bank_drawbar"), ("manual", "upper"), ("index", 2)):
                self.reject_change(("parameters", index, "engine_event", key), value)
            for key, value in (("to_plain", "u"), ("to_normalized", "x"),
                               ("meaning", "audio-amplitude")):
                self.reject_change(("parameters", index, "normalized", key), value)

    def test_original_39_whole_records_match_independent_frozen_digest(self):
        self.assertEqual(sum(p["id"] in LEGACY_IDS for p in self.registry["parameters"]), 39)
        self.assertEqual(legacy_records_digest(self.registry["parameters"]), LEGACY_RECORDS_SHA256)
        self.registry["parameters"].reverse()
        self.assertEqual(legacy_records_digest(self.registry["parameters"]), LEGACY_RECORDS_SHA256)
        # A semantic change is detectable even if a future validator is changed
        # to agree with it; this independent baseline must not be regenerated.
        self.by_id[4096]["normalized"]["meaning"] = "audio-amplitude"
        self.assertNotEqual(legacy_records_digest(self.registry["parameters"]), LEGACY_RECORDS_SHA256)

    def test_percussion_controls_have_distinct_retained_targets_and_binary_laws(self):
        expected = ((12288, "enabled", "0=off-1=on"),
                    (12289, "harmonic", "0=second-1=third"),
                    (12290, "volume", "0=normal-1=soft"),
                    (12291, "decay", "0=slow-1=fast"))
        for index, (identifier, setting, choices) in enumerate(expected):
            with self.subTest(setting=setting):
                parameter = self.by_id[identifier]
                self.assertEqual(parameter["path"], f"percussion.{setting}")
                self.assertEqual(parameter["unit"], f"{setting}-index-{choices}")
                self.assertEqual((parameter["minimum"], parameter["maximum"],
                                  parameter["default"], parameter["step_count"]), (0, 1, 0, 1))
                self.assertEqual(parameter["normalized"], {
                    "minimum": 0.0, "maximum": 1.0, "default": 0.0,
                    "to_plain": "floor(u + 0.5)", "to_normalized": "x",
                    "meaning": "percussion-setting-index-fraction"})
                for normalized, plain in ((0.0, 0), (math.nextafter(0.5, 0.0), 0),
                                          (0.5, 1), (math.nextafter(0.5, 1.0), 1), (1.0, 1)):
                    self.assertEqual(validator.normalized_to_event(self.registry, identifier, normalized),
                                     {"type": "percussion", "manual": "upper", "index": index, "value": plain})

    def test_percussion_payload_creation_is_independent_of_selection_and_other_settings(self):
        before = copy.deepcopy(self.registry)
        for selector_id in (8208, 8209):
            for selected_bank in (0.0, 1.0):
                validator.normalized_to_event(self.registry, selector_id, selected_bank)
                for identifier in (12288, 12289, 12290, 12291):
                    validator.normalized_to_event(self.registry, identifier, 1.0)
                    event = validator.normalized_to_event(self.registry, identifier, 0.0)
                    self.assertEqual(event["index"], identifier - 12288)
                    self.assertEqual(event["value"], 0)
        self.assertEqual(self.registry, before)

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
                         {"bank_drawbar", "select_bank", "expression", "percussion", "pedal_drawbar"})
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
        for identifier in self.by_id:
            self.assertEqual(validator.normalized_to_event(self.registry, identifier, 0.5),
                             validator.normalized_to_event(before, identifier, 0.5))

    def test_version_model_scope_and_status_are_exact(self):
        for key, bad in (("schema_version", 1), ("schema_version", 2),
                         ("schema_version", 4), ("schema_version", 3.0), ("schema_version", True),
                         ("model", "measured-console"), ("scope", "full-62-parameter-atlas"),
                         ("status", "exported-vst3")):
            with self.subTest(key=key, value=bad):
                self.reject_change((key,), bad)

    def test_historical_registry_document_requires_explicit_upgrade(self):
        historical = copy.deepcopy(REGISTRY)
        historical["schema_version"] = 1
        historical["model"] = "ideal-exclusive-ab-console-v1"
        historical["parameters"] = [p for p in historical["parameters"] if p["id"] in LEGACY_IDS]
        historical["provenance"] = {
            "evidence_class": "proposed",
            "applicable_variant": "nominal B-3/AO-28 console engineering subset",
            "atlas_file": "Hammond_B3_Leslie_Research_Atlas_500pp.pdf",
            "atlas_pages": [389, 397, 398, 399, 400, 401, 402],
            "implementation_sources": ["docs/CONSOLE_EXTENSION.md", "include/hammond/ControlState.h"],
            "companion_recovered": False, "host_exports_verified": False,
            "native_host_curves_implemented": False, "uncertainty": None,
            "reason": "Original internal IDs, ranges, defaults and conversions for the current ideal console. "
                      "The absent 62-entry atlas companion was not recovered; no hardware calibration or host mapping is claimed.",
        }
        original = copy.deepcopy(historical)
        with self.assertRaisesRegex(validator.ParameterError, "registry.schema_version"):
            validator.validate_registry(historical)
        self.assertEqual(historical, original)
        with tempfile.TemporaryDirectory(prefix="hammond old parameters ") as directory:
            path = Path(directory) / "version1.json"
            path.write_text(json.dumps(historical), encoding="utf-8")
            with self.assertRaisesRegex(validator.ParameterError, "registry.schema_version"):
                validator.load_registry(path)
        self.assertEqual(legacy_records_digest(historical["parameters"]), LEGACY_RECORDS_SHA256)

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

    def test_percussion_metadata_cannot_change_units_defaults_or_event_meaning(self):
        for index in range(39, 43):
            for field, value in (("id", 12292), ("kind", "expression"),
                                 ("unit", "seconds"), ("minimum", -1), ("maximum", 2),
                                 ("default", 1), ("step_count", 0),
                                 ("evidence_class", "measured"), ("source_pages", [134])):
                with self.subTest(index=index, field=field):
                    self.reject_change(("parameters", index, field), value)
            for field, value in (("type", "select_bank"), ("manual", "lower"),
                                 ("index", 4), ("index", True), ("index", 0.0)):
                with self.subTest(index=index, target=field):
                    self.reject_change(("parameters", index, "engine_event", field), value)
            self.reject_change(("parameters", index, "normalized", "default"), 1.0)
            self.reject_change(("parameters", index, "normalized", "to_plain"), "u")
            self.reject_change(("parameters", index, "normalized", "meaning"), "audio-amplitude")
        for field in ("id", "path", "engine_event"):
            self.reject_change(("parameters", 40, field), copy.deepcopy(self.by_id[12288][field]))

    def test_unknown_or_missing_keys_reject_at_every_object_level(self):
        paths = ((), ("provenance",), ("parameters", 0),
                 ("parameters", 0, "normalized"), ("parameters", 0, "engine_event"),
                 ("parameters", 39), ("parameters", 39, "normalized"),
                 ("parameters", 39, "engine_event"),
                 ("parameters", 43), ("parameters", 43, "normalized"),
                 ("parameters", 43, "engine_event"))
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
        for index in (0, 36, 37, 39, 40, 41, 42, 43, 44):
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
        for identifier, parameter in self.by_id.items():
            count = parameter["step_count"]
            for lower in range(count):
                threshold = (lower + 0.5) / count
                with self.subTest(identifier=identifier, threshold=threshold):
                    self.assertEqual(validator.normalized_to_value(parameter, math.nextafter(threshold, 0.0)), lower)
                    self.assertEqual(validator.normalized_to_value(parameter, threshold), lower + 1)
                    self.assertEqual(validator.normalized_to_value(parameter, math.nextafter(threshold, 1.0)), lower + 1)

    def test_conversion_rejects_nonfinite_and_out_of_range_without_clipping(self):
        for identifier in (4096, 8192, 8208, 12288, 12289, 12290, 12291, 16384, 16385):
            parameter = self.by_id[identifier]
            for invalid in (-0.001, math.nextafter(0.0, -math.inf), math.nextafter(1.0, math.inf), float("nan"),
                            float("inf"), -float("inf"), True, "0.5", None, 10 ** 400):
                with self.subTest(identifier=identifier, invalid_type=type(invalid).__name__):
                    with self.assertRaises(validator.ParameterError):
                        validator.normalized_to_value(parameter, invalid)
                    with self.assertRaises(validator.ParameterError):
                        validator.normalized_to_event(self.registry, identifier, invalid)
            for invalid in (-1, parameter["maximum"] + 1, float("nan"), float("inf"),
                            -float("inf"), True, "1", None, 10 ** 400):
                with self.assertRaises(validator.ParameterError):
                    validator.value_to_normalized(parameter, invalid)
        for identifier in (4096, 8208, 12288, 12289, 12290, 12291, 16384, 16385):
            with self.assertRaises(validator.ParameterError):
                validator.value_to_normalized(self.by_id[identifier], 0.5)

    def test_event_mapping_rejects_unknown_id_and_returns_an_independent_payload(self):
        for invalid in (4105, 12287, 12292, 16383, 16386, -1, 1 << 32, True, 4096.0, "4096"):
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
            good.replace('"path": "percussion.enabled"',
                         '"path": "percussion.enabled", "path": "percussion.enabled"', 1).encode(),
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
        self.assertIn("45 proposed internal parameters", result.stdout)
        self.assertIn("exclusive-ab-percussion-pedal-console-v3", result.stdout)
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
