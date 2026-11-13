#!/usr/bin/env python3
"""Independent checks of the proposed capture contract; no hardware evidence.

Fixtures below are written from docs/CAPTURE_FORMAT.md, without producer helpers.
All retained byte fixtures are tiny, explicitly synthetic, temporary test assets.
"""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import copy
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "tools" / "validate_capture.py"
EXAMPLE_PATH = ROOT / "data" / "capture-planned-example.json"
SPEC = importlib.util.spec_from_file_location("capture_validator_test_subject", VALIDATOR_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {VALIDATOR_PATH}")
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)

# These bounds are copied from the public contract, not the validator constants.
JSON_BYTE_LIMIT = 65536
ARTIFACT_BYTE_LIMIT = 268435456
SYNTHETIC_RAW = struct.pack("<f", 0.125)
SYNTHETIC_DERIVED = struct.pack("<f", 0.25)


def known(value):
    return {"value": value, "unknown_reason": None}


def unknown(reason="Unresolved in this deliberately synthetic metadata test."):
    return {"value": None, "unknown_reason": reason}


def uncalibrated(unit):
    return {"status": "uncalibrated", "value": None, "unit": unit,
            "standard_uncertainty": None, "evidence": None,
            "unknown_reason": "No physical calibration has been acquired."}


def not_applicable():
    return {"status": "not_applicable", "value": None, "unit": None,
            "standard_uncertainty": None, "evidence": None,
            "unknown_reason": "Generated software test bytes have no physical calibration."}


def planned_capture():
    return {
        "schema_version": 1,
        "contract_origin": "project-proposed-v1",
        "capture_id": "independent-planning-test",
        "status": "planned",
        "status_reason": "Planning fixture only; no acquisition or specimen exists.",
        "capture_kind": "hardware",
        "specimen": {key: unknown() for key in
                     ("specimen_id", "variant", "revision", "identity_evidence")},
        "acquisition": {key: unknown() for key in
                        ("started_at_utc", "operator_id", "session_id")},
        "digital": {"format": unknown(), "sample_rate_hz": unknown(),
                    "channel_count": unknown(), "channels": []},
        "physical_clock": uncalibrated("Hz"),
        "stimulus": {key: unknown() for key in
                     ("description", "controls", "conditions", "synchronization")},
        "signal_path": {key: unknown() for key in ("description", "bypass", "loading")},
        "files": [],
        "partition": {"role": "unassigned", "group_id": unknown(),
                      "rationale": "No take exists; preserve related future takes together."},
        "rights": unknown("No store, analyze, derive-model or redistribution declaration exists."),
    }


def file_record(file_id="raw", path="raw.bin", payload=SYNTHETIC_RAW,
                kind="raw", parents=()):
    return {
        "file_id": file_id, "kind": kind, "path": path,
        "size_bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest(),
        "parents": list(parents),
        "derivation": None if kind != "derived" else {
            "operation": "Multiply a synthetic scalar by two.",
            "tool": "independent-capture-test", "tool_version": "1",
            "parameters": "Synthetic scalar 0.125 to 0.25; no hardware samples.",
        },
    }


def synthetic_record():
    record = planned_capture()
    record.update(capture_id="independent-synthetic-test", status="recorded",
                  status_reason=None, capture_kind="synthetic")
    record["specimen"] = {
        "specimen_id": unknown("This synthetic fixture has no physical specimen."),
        "variant": known("Generated test scalar; no Hammond or Leslie measurement."),
        "revision": known("Independent test fixture version 1."),
        "identity_evidence": known("tests/test_capture.py generates synthetic bytes."),
    }
    record["acquisition"] = {
        "started_at_utc": known("2024-02-29T12:34:56.125Z"),
        "operator_id": known("synthetic-test"), "session_id": known("synthetic-session"),
    }
    record["digital"] = {
        "format": known("raw_float32_le"), "sample_rate_hz": known(48000),
        "channel_count": known(1), "channels": [{
            "channel_id": "synthetic-channel", "index": 0,
            "boundary": known("synthetic"),
            "port_reference": known("Generated software scalar; no electrical or acoustic port."),
            "calibration": not_applicable(),
        }],
    }
    record["physical_clock"] = not_applicable()
    record["stimulus"]["description"] = known("One synthetic floating-point sample.")
    record["signal_path"]["description"] = known("Generated bytes with no physical signal chain.")
    record["files"] = [file_record()]
    record["partition"] = {
        "role": "unassigned", "group_id": known("synthetic-group"),
        "rationale": "All synthetic derivatives remain in this single test group.",
    }
    return record


def with_derivative():
    record = synthetic_record()
    record["files"].append(file_record("doubled", "derived/doubled.bin", SYNTHETIC_DERIVED,
                                      "derived", ["raw"]))
    return record


def hardware_channel_plan(boundary="preamp_GG", unit="V/FS"):
    record = planned_capture()
    record["digital"] = {
        "format": known("wav_pcm24"), "sample_rate_hz": known(96000),
        "channel_count": known(1), "channels": [{
            "channel_id": "proposed-channel", "index": 0,
            "boundary": unknown() if boundary is None else known(boundary),
            "port_reference": unknown("Port identities and loading await the acquisition plan."),
            "calibration": uncalibrated(unit),
        }],
    }
    return record


def at_path(value, path):
    for key in path:
        value = value[key]
    return value


def object_paths(value, path=()):
    if type(value) is dict:
        yield path
        for key, child in value.items():
            yield from object_paths(child, path + (key,))
    elif type(value) is list:
        for index, child in enumerate(value):
            yield from object_paths(child, path + (index,))


def without_file_identity(info):
    return SimpleNamespace(st_dev=0, st_ino=0, st_mode=info.st_mode,
                           st_size=info.st_size, st_mtime_ns=info.st_mtime_ns,
                           st_ctime_ns=info.st_ctime_ns)


def platform_without_descriptor_identity():
    # A concrete metadata variant, without changing pathlib's real host platform.
    platform_os = SimpleNamespace(**vars(os))
    platform_os.name = "nt"
    platform_os.fstat = lambda fd: without_file_identity(os.fstat(fd))
    return platform_os


class CaptureTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="hammond synthetic capture ")
        self.addCleanup(directory.cleanup)
        self.work = Path(directory.name).resolve()
        self.path = self.work / "capture.json"
        self.record = synthetic_record()

    def rejected(self, value):
        with self.assertRaises(validator.CaptureError):
            validator.validate_capture(value)

    def reject_change(self, path, value, base=None):
        changed = copy.deepcopy(self.record if base is None else base)
        at_path(changed, path[:-1])[path[-1]] = value
        self.rejected(changed)

    def write_manifest(self, value, path=None):
        path = self.path if path is None else path
        path.write_text(json.dumps(value, allow_nan=False), encoding="utf-8")
        return path

    def retain_artifacts(self, record):
        for artifact in record["files"]:
            path = self.work / artifact["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            payload = SYNTHETIC_DERIVED if artifact["kind"] == "derived" else SYNTHETIC_RAW
            path.write_bytes(payload)

    def cli(self, *arguments, cwd=None):
        return subprocess.run([sys.executable, str(VALIDATOR_PATH), *map(str, arguments)],
                              cwd=self.work if cwd is None else cwd, capture_output=True,
                              text=True, check=False, timeout=10)

    def assert_capture_failure(self, result):
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertIn("capture error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_independent_planned_and_recorded_synthetic_fixtures(self):
        for record in (planned_capture(), hardware_channel_plan(), self.record, with_derivative()):
            with self.subTest(status=record["status"], kind=record["capture_kind"]):
                self.assertIsNone(validator.validate_capture(record))
                self.assertEqual(validator.load_capture(self.write_manifest(record)), record)
        self.assertFalse((self.work / "raw.bin").exists())
        plan = synthetic_record()
        plan.update(status="planned", status_reason="Synthetic capture has not been generated.", files=[])
        plan["acquisition"]["started_at_utc"] = unknown("Only a synthetic plan exists.")
        validator.validate_capture(plan)

    def test_committed_example_remains_an_explicit_plan(self):
        original = EXAMPLE_PATH.read_bytes()
        example = validator.load_capture(EXAMPLE_PATH)
        self.assertEqual(example["status"], "planned")
        self.assertEqual(example["capture_kind"], "hardware")
        self.assertEqual(example["contract_origin"], "project-proposed-v1")
        self.assertEqual(example["files"], [])
        self.assertIsNone(example["acquisition"]["started_at_utc"]["value"])
        self.assertIsNone(example["specimen"]["specimen_id"]["value"])
        self.assertEqual(example["physical_clock"]["status"], "uncalibrated")
        self.assertIsNone(example["physical_clock"]["value"])
        self.assertEqual(EXAMPLE_PATH.read_bytes(), original)

    def test_in_memory_hardware_declaration_can_preserve_unknown_calibration(self):
        # This is only a hypothetical API argument. Do not serialize it, create
        # its claimed file, or treat successful validation as an acquisition.
        declaration = hardware_channel_plan()
        declaration.update(capture_id="hypothetical-hardware-admission-test",
                           status="recorded", status_reason=None)
        declaration["acquisition"] = copy.deepcopy(self.record["acquisition"])
        declaration["partition"] = copy.deepcopy(self.record["partition"])
        declaration["files"] = [file_record(path="absent-hypothetical-artifact.bin")]
        declaration["files"][0]["sha256"] = "0" * 64  # Unverified placeholder declaration.
        declaration["signal_path"]["description"] = known(
            "Hypothetical API case only. No hardware specimen, recording or calibration exists.")
        before = copy.deepcopy(declaration)
        validator.validate_capture(declaration)
        self.assertEqual(declaration, before)
        self.assertIsNone(declaration["specimen"]["specimen_id"]["value"])
        self.assertIsNone(declaration["physical_clock"]["value"])
        self.assertIsNone(declaration["digital"]["channels"][0]["calibration"]["value"])
        self.assertFalse((self.work / declaration["files"][0]["path"]).exists())

    def test_validation_and_rejected_validation_do_not_mutate_metadata(self):
        for record in (planned_capture(), with_derivative(), hardware_channel_plan()):
            original = copy.deepcopy(record)
            validator.validate_capture(record)
            self.assertEqual(record, original)
            validator.validate_capture(dict(reversed(list(record.items()))))
            self.assertEqual(record, original)
        invalid = with_derivative()
        invalid["files"][1]["parents"].append("missing-parent")
        original = copy.deepcopy(invalid)
        self.rejected(invalid)
        self.assertEqual(invalid, original)

    def test_every_required_key_and_unknown_key_at_every_object_level(self):
        for source in (planned_capture(), with_derivative()):
            for path in object_paths(source):
                target = at_path(source, path)
                for key in target:
                    candidate = copy.deepcopy(source)
                    del at_path(candidate, path)[key]
                    with self.subTest(path=path, missing=key):
                        self.rejected(candidate)
                candidate = copy.deepcopy(source)
                at_path(candidate, path)["unexpected_field"] = None
                with self.subTest(path=path, extra=True):
                    self.rejected(candidate)

    def test_root_and_container_types_are_exact_json_types(self):
        for value in (None, [], (), True, 1, "capture", object()):
            with self.subTest(value_type=type(value).__name__):
                self.rejected(value)
        for path in (("files",), ("digital", "channels"), ("specimen",),
                     ("partition",), ("physical_clock",), ("rights",)):
            for invalid in (None, True, "wrong", ()):
                with self.subTest(path=path, invalid=invalid):
                    self.reject_change(path, invalid)

    def test_boolean_float_and_nonfinite_numeric_substitutes_are_rejected(self):
        paths = (("schema_version",), ("digital", "sample_rate_hz", "value"),
                 ("digital", "channel_count", "value"),
                 ("digital", "channels", 0, "index"), ("files", 0, "size_bytes"))
        for path in paths:
            for value in (True, False, 1.0, float("nan"), float("inf"), -float("inf"),
                          10 ** 400, "1"):
                with self.subTest(path=path, value_type=type(value).__name__):
                    self.reject_change(path, value)

    def test_enum_version_and_identity_domains(self):
        for path, value in ((('schema_version',), 2), (('contract_origin',), "atlas-recovered"),
                            (('status',), "measured"), (('capture_kind',), "calibrated"),
                            (('digital', 'format', 'value'), "mp3"),
                            (('partition', 'role'), "training"), (('files', 0, 'kind'), "capture"),
                            (('digital', 'channels', 0, 'boundary', 'value'), "Hammond output")):
            self.reject_change(path, value)
        paths = (("capture_id",), ("acquisition", "operator_id", "value"),
                 ("acquisition", "session_id", "value"), ("partition", "group_id", "value"),
                 ("digital", "channels", 0, "channel_id"), ("files", 0, "file_id"))
        for path in paths:
            for value in ("", " ", "Upper", "1starts-with-number", "a/b", "a.b", "a" * 65, None):
                with self.subTest(path=path, value=value):
                    self.reject_change(path, value)
        candidate = synthetic_record()
        candidate["capture_id"] = "a" + "_" * 63
        validator.validate_capture(candidate)
        plan = planned_capture()
        plan["specimen"]["specimen_id"] = known("proposed-subject-id")
        validator.validate_capture(plan)
        self.reject_change(("specimen", "specimen_id", "value"), "Bad ID", plan)

    def test_unknown_reason_pairs_do_not_silently_default_values(self):
        for path in object_paths(self.record):
            value = at_path(self.record, path)
            if set(value) != {"value", "unknown_reason"}:
                continue
            for pair in ({"value": None, "unknown_reason": None},
                         {"value": None, "unknown_reason": "  "},
                         {"value": value["value"] if value["value"] is not None else "placeholder",
                          "unknown_reason": "A known value cannot also be unknown."}):
                with self.subTest(path=path, pair=pair):
                    self.reject_change(path, pair)
        original = copy.deepcopy(self.record)
        validator.validate_capture(self.record)
        self.assertIsNone(self.record["physical_clock"]["value"])
        self.assertIsNone(self.record["digital"]["channels"][0]["calibration"]["value"])
        self.assertEqual(self.record, original)

    def test_text_is_bounded_nonblank_and_free_of_controls_or_surrogates(self):
        for path in (("stimulus", "description", "value"), ("partition", "rationale"),
                     ("specimen", "identity_evidence", "value")):
            for value in ("", "   ", "bad\nline", "bad\x00text", "a" * 2049, "\ud800"):
                with self.subTest(path=path, value=repr(value)[:50]):
                    self.reject_change(path, value)
        for text in ("a" * 2048, "Synthetic café metadata — no physical acquisition."):
            candidate = synthetic_record()
            candidate["stimulus"]["description"] = known(text)
            validator.validate_capture(candidate)

    def test_utc_timestamp_checks_real_dates_and_exact_timezone_form(self):
        path = ("acquisition", "started_at_utc", "value")
        for timestamp in ("2024-02-29T00:00:00Z", "2000-02-29T23:59:59.1Z",
                          "2026-12-31T23:59:59.123456Z"):
            candidate = synthetic_record()
            candidate["acquisition"]["started_at_utc"] = known(timestamp)
            validator.validate_capture(candidate)
        for timestamp in ("2026-02-29T00:00:00Z", "2024-02-30T00:00:00Z",
                          "2026-04-31T00:00:00Z", "0000-01-01T00:00:00Z",
                          "2026-01-01T24:00:00Z", "2026-01-01T00:60:00Z",
                          "2026-01-01T00:00:60Z", "2026-01-01T00:00:00.1234567Z",
                          "2026-01-01T00:00:00+01:00", "2026-01-01T00:00:00+00:00",
                          "2026-01-01T00:00:00", "2026-01-01 00:00:00Z", "not-a-time"):
            with self.subTest(timestamp=timestamp):
                self.reject_change(path, timestamp)

    def test_recorded_fields_cannot_remain_unknown(self):
        paths = (("acquisition", "started_at_utc"), ("acquisition", "operator_id"),
                 ("acquisition", "session_id"), ("digital", "format"),
                 ("digital", "sample_rate_hz"), ("digital", "channel_count"),
                 ("partition", "group_id"))
        for path in paths:
            candidate = synthetic_record()
            at_path(candidate, path[:-1])[path[-1]] = unknown()
            if path == ("digital", "channel_count"):
                candidate["digital"]["channels"] = []
            with self.subTest(path=path):
                self.rejected(candidate)

    def test_status_rules_for_planned_and_recorded_records(self):
        plan = planned_capture()
        self.reject_change(("files",), [file_record()], plan)
        self.reject_change(("acquisition", "started_at_utc"), known("2024-02-29T12:00:00Z"), plan)
        for reason in (None, "", " "):
            self.reject_change(("status_reason",), reason, plan)
        self.reject_change(("status_reason",), "Not acquired yet.")
        self.reject_change(("files",), [])
        self.reject_change(("files",), [file_record(kind="support")])
        plan["acquisition"]["operator_id"] = known("intended-operator")
        plan["acquisition"]["session_id"] = known("intended-session")
        validator.validate_capture(plan)

    def test_synthetic_and_hardware_boundary_and_calibration_states_stay_distinct(self):
        self.reject_change(("specimen", "specimen_id"), known("pretend-instrument"))
        self.reject_change(("digital", "channels", 0, "boundary"), known("preamp_GG"))
        self.reject_change(("digital", "channels", 0, "boundary"), unknown())
        self.reject_change(("physical_clock",), uncalibrated("Hz"))
        self.reject_change(("digital", "channels", 0, "calibration"), uncalibrated(None))
        plan = hardware_channel_plan()
        self.reject_change(("physical_clock",), not_applicable(), plan)
        self.reject_change(("digital", "channels", 0, "calibration"), not_applicable(), plan)
        self.reject_change(("digital", "channels", 0, "boundary"), known("synthetic"), plan)

    def test_all_documented_digital_formats_and_numeric_endpoints(self):
        for file_format in ("wav_pcm16", "wav_pcm24", "wav_pcm32", "wav_float32", "wav_float64",
                            "flac_pcm16", "flac_pcm24", "raw_float32_le"):
            plan = hardware_channel_plan()
            plan["digital"]["format"] = known(file_format)
            validator.validate_capture(plan)
        for rate in (1, 768000):
            candidate = synthetic_record()
            candidate["digital"]["sample_rate_hz"] = known(rate)
            validator.validate_capture(candidate)
        for rate in (0, -1, 768001):
            self.reject_change(("digital", "sample_rate_hz", "value"), rate)
        for count in (0, -1, 17):
            self.reject_change(("digital", "channel_count", "value"), count)

    def test_channels_have_unique_identity_and_exact_ordered_indices(self):
        candidate = synthetic_record()
        candidate["digital"]["channel_count"] = known(16)
        first = candidate["digital"]["channels"][0]
        candidate["digital"]["channels"] = [dict(copy.deepcopy(first), channel_id=f"channel-{i}", index=i)
                                              for i in range(16)]
        validator.validate_capture(candidate)
        self.reject_change(("digital", "channels", 1, "channel_id"), "channel-0", candidate)
        self.reject_change(("digital", "channels", 1, "index"), 0, candidate)
        self.reject_change(("digital", "channels"), list(reversed(candidate["digital"]["channels"])), candidate)
        self.reject_change(("digital", "channels"), candidate["digital"]["channels"][:-1], candidate)
        plan = hardware_channel_plan()
        self.reject_change(("digital", "channel_count"), unknown(), plan)

    def test_boundary_units_are_not_interchangeable_or_inferred(self):
        units = {"pickup_unloaded": "V/FS", "generator_loaded_terminal": "V/FS",
                 "preamp_GG": "V/FS", "electrical_voltage": "V/FS",
                 "electrical_current": "A/FS", "acoustic_microphone": "Pa/FS", None: None}
        for boundary, unit in units.items():
            plan = hardware_channel_plan(boundary, unit)
            validator.validate_capture(plan)
            wrong = "V/FS" if unit != "V/FS" else "Pa/FS"
            with self.subTest(boundary=boundary):
                self.reject_change(("digital", "channels", 0, "calibration", "unit"), wrong, plan)
        for unit in (None, "kHz", "V/FS"):
            self.reject_change(("physical_clock", "unit"), unit, planned_capture())
        self.reject_change(("physical_clock", "unit"), "Hz")
        plan = hardware_channel_plan()
        before = copy.deepcopy(plan["physical_clock"])
        validator.validate_capture(plan)
        self.assertEqual(plan["physical_clock"], before)
        self.assertIsNone(plan["physical_clock"]["value"])

    def test_uncalibrated_and_not_applicable_fields_have_explicit_missing_evidence(self):
        for base, path in ((planned_capture(), ("physical_clock",)),
                           (hardware_channel_plan(), ("digital", "channels", 0, "calibration")),
                           (self.record, ("physical_clock",)),
                           (self.record, ("digital", "channels", 0, "calibration"))):
            for key, value in (("value", 1.0), ("standard_uncertainty", 0.0),
                               ("evidence", "Invented evidence must not fill an unknown."),
                               ("unknown_reason", None), ("unknown_reason", " "), ("status", "measured")):
                with self.subTest(path=path, key=key, status=base["status"]):
                    self.reject_change(path + (key,), value, base)
        # A complete but explicitly hypothetical calibration declaration cannot
        # turn a plan or synthetic record into measured hardware evidence.
        forbidden = {"status": "calibrated", "value": 48000.0, "unit": "Hz",
                     "standard_uncertainty": 0.0, "evidence": "Hypothetical rejected test only.",
                     "unknown_reason": None}
        self.reject_change(("physical_clock",), forbidden, planned_capture())
        self.reject_change(("physical_clock",), forbidden)

    def test_file_identity_size_digest_and_aggregate_bounds(self):
        for size in (1, ARTIFACT_BYTE_LIMIT):
            candidate = synthetic_record()
            candidate["files"][0]["size_bytes"] = size
            validator.validate_capture(candidate)
        for size in (0, -1, ARTIFACT_BYTE_LIMIT + 1):
            self.reject_change(("files", 0, "size_bytes"), size)
        for digest in ("0" * 63, "0" * 65, "z" * 64, "A" * 64, None):
            self.reject_change(("files", 0, "sha256"), digest)
        candidate = synthetic_record()
        candidate["files"] = [file_record(f"raw-{i}", f"raw-{i}.bin") for i in range(32)]
        validator.validate_capture(candidate)
        candidate["files"].append(file_record("raw-32", "raw-32.bin"))
        self.rejected(candidate)
        candidate["files"] = [file_record(f"raw-{i}", f"raw-{i}.bin") for i in range(3)]
        for artifact in candidate["files"][:2]:
            artifact["size_bytes"] = ARTIFACT_BYTE_LIMIT
        self.rejected(candidate)  # Two maximum artifacts plus four bytes exceed 512 MiB.
        candidate["files"].pop()
        validator.validate_capture(candidate)

    def test_file_ids_and_casefolded_paths_are_unique_but_equal_digests_are_allowed(self):
        candidate = synthetic_record()
        candidate["files"].append(file_record("second", "second.bin"))
        validator.validate_capture(candidate)
        self.assertEqual(candidate["files"][0]["sha256"], candidate["files"][1]["sha256"])
        self.reject_change(("files", 1, "file_id"), "raw", candidate)
        for path in ("raw.bin", "RAW.BIN"):
            self.reject_change(("files", 1, "path"), path, candidate)

    def test_file_paths_are_confined_portable_and_bounded(self):
        invalid_paths = ("../raw.bin", "a/../raw.bin", "./raw.bin", "/raw.bin", "a//raw.bin",
                         "raw.bin/", "a/./raw.bin", "C:/raw.bin", "C:\\raw.bin", "a\\raw.bin",
                         "//server/share/raw.bin", "a:raw.bin", "bad name.bin", "_raw.bin",
                         "raw.bin.", "é.bin", "a" * 65, "/".join(["a"] * 9),
                         "/".join(["a" * 30] * 8), "CON", "con.bin", "AUX", "PRN", "NUL",
                         "COM1.bin", "LPT9.bin", "a/../b", "a\x00.bin")
        for path in invalid_paths:
            with self.subTest(path=repr(path)):
                self.reject_change(("files", 0, "path"), path)
        valid_paths = ("a", "nested/raw.bin", "a..bin", "/".join(["a" * 29] * 7 + ["b" * 30]))
        self.assertEqual(len(valid_paths[-1]), 240)
        for path in valid_paths:
            candidate = synthetic_record()
            candidate["files"][0]["path"] = path
            validator.validate_capture(candidate)

    def test_raw_support_and_derived_ancestry_have_distinct_requirements(self):
        candidate = with_derivative()
        candidate["files"].append(file_record("support", "support.bin", kind="support"))
        validator.validate_capture(candidate)
        for index in (0, 2):
            self.reject_change(("files", index, "parents"), ["doubled"], candidate)
            self.reject_change(("files", index, "derivation"), candidate["files"][1]["derivation"], candidate)
        self.reject_change(("files", 1, "parents"), [], candidate)
        self.reject_change(("files", 1, "derivation"), None, candidate)
        for key in ("operation", "tool", "tool_version", "parameters"):
            self.reject_change(("files", 1, "derivation", key), " ", candidate)
        self.reject_change(("files", 1, "parents"), ["support"], candidate)

    def test_local_parents_resolve_are_unique_and_cannot_form_cycles(self):
        candidate = with_derivative()
        for parents in (["missing"], ["doubled"], ["raw", "raw"], [True]):
            self.reject_change(("files", 1, "parents"), parents, candidate)
        candidate["files"].append(file_record("third", "third.bin", SYNTHETIC_DERIVED,
                                              "derived", ["doubled"]))
        validator.validate_capture(candidate)
        self.reject_change(("files", 1, "parents"), ["third"], candidate)
        candidate["files"].reverse()
        validator.validate_capture(candidate)  # A DAG need not be serialized topologically.

    def test_parent_limit_and_shared_raw_ancestor_diamond(self):
        candidate = synthetic_record()
        candidate["files"] = [file_record(f"raw-{i}", f"raw-{i}.bin") for i in range(17)]
        candidate["files"].append(file_record("combined", "combined.bin", SYNTHETIC_DERIVED,
                                              "derived", [f"raw-{i}" for i in range(16)]))
        validator.validate_capture(candidate)
        candidate["files"][-1]["parents"].append("raw-16")
        self.rejected(candidate)
        diamond = with_derivative()
        diamond["files"].append(file_record("sibling", "sibling.bin", SYNTHETIC_DERIVED, "derived", ["raw"]))
        diamond["files"].append(file_record("merged", "merged.bin", SYNTHETIC_DERIVED,
                                            "derived", ["doubled", "sibling"]))
        validator.validate_capture(diamond)

    def test_partition_membership_is_manifest_wide_and_requires_group_identity(self):
        for role in ("fit", "held_out", "unassigned"):
            candidate = with_derivative()
            candidate["partition"]["role"] = role
            validator.validate_capture(candidate)
        for role in ("fit", "held_out"):
            plan = planned_capture()
            plan["partition"]["role"] = role
            self.rejected(plan)
            plan["partition"]["group_id"] = known("proposed-whole-take")
            validator.validate_capture(plan)
        for extra_key, value in (("group_id", "another-group"), ("role", "held_out"),
                                 ("partition", {"role": "held_out"})):
            candidate = with_derivative()
            candidate["files"][1][extra_key] = value
            self.rejected(candidate)

    def test_strict_json_duplicate_nonfinite_utf8_and_malformed_inputs(self):
        good = json.dumps(self.record)
        bad_inputs = [
            good.replace('"schema_version": 1', '"schema_version": 1, "schema_version": 1', 1).encode(),
            good.replace('"index": 0', '"index": 0, "index": 0', 1).encode(),
            good.encode() + b" trailing", b"\xff", b"\xef\xbb\xbf" + good.encode(),
            b"[]", b"null", b"true", b"{", b"",
        ]
        for token in ("NaN", "Infinity", "-Infinity", "1e999", "9" * 65):
            bad_inputs.append(good.replace('"value": 48000', '"value": ' + token, 1).encode())
        for index, payload in enumerate(bad_inputs):
            self.path.write_bytes(payload)
            with self.subTest(index=index), self.assertRaises(validator.CaptureError):
                validator.load_capture(self.path)

    def test_json_byte_limit_rejects_an_otherwise_valid_padded_document(self):
        good = json.dumps(self.record).encode()
        self.assertLess(len(good), JSON_BYTE_LIMIT)
        exact = good + b" " * (JSON_BYTE_LIMIT - len(good))
        self.path.write_bytes(exact)
        self.assertEqual(validator.load_capture(self.path), self.record)
        self.path.write_bytes(exact + b" ")
        with self.assertRaises(validator.CaptureError):
            validator.load_capture(self.path)

    def test_deep_wide_or_unsupported_json_is_a_controlled_rejection(self):
        payloads = (b"[" * 2000 + b"]" * 2000,
                    b"[" + b",".join([b"0"] * 4097) + b"]",
                    b'{"extra":' + b"[" * 17 + b"0" + b"]" * 17 + b"}")
        for payload in payloads:
            self.path.write_bytes(payload)
            with self.subTest(size=len(payload)), self.assertRaises(validator.CaptureError):
                validator.load_capture(self.path)
        for path in (self.work / "missing.json", self.work):
            with self.subTest(path=str(path)), self.assertRaises(validator.CaptureError):
                validator.load_capture(path)

    def test_explicit_byte_check_recomputes_sizes_hashes_and_reports_only_integrity(self):
        record = with_derivative()
        self.retain_artifacts(record)
        original = copy.deepcopy(record)
        report = validator.check_capture_files(record, self.work)
        self.assertEqual(report, {
            "capture_id": record["capture_id"], "status": "verified", "files_checked": 2,
            "bytes_checked": 8, "scope": "declared-byte-integrity-only",
            "authenticity": "not_established", "calibration": "not_established",
            "physical_fidelity": "not_established",
        })
        self.assertEqual(record, original)
        self.assertEqual((self.work / "raw.bin").read_bytes(), SYNTHETIC_RAW)
        self.assertEqual((self.work / "derived/doubled.bin").read_bytes(), SYNTHETIC_DERIVED)

    def test_default_structure_does_not_require_file_existence_or_verify_digests(self):
        self.record["files"][0]["sha256"] = "0" * 64
        validator.validate_capture(self.record)
        self.assertEqual(validator.load_capture(self.write_manifest(self.record)), self.record)
        with self.assertRaises(validator.CaptureError):
            validator.check_capture_files(self.record, self.work)
        (self.work / "raw.bin").write_bytes(SYNTHETIC_RAW)
        with self.assertRaises(validator.CaptureError):
            validator.check_capture_files(self.record, self.work)

    def test_byte_checker_rejects_plans_and_revalidates_metadata(self):
        with self.assertRaises(validator.CaptureError):
            validator.check_capture_files(planned_capture(), self.work)
        self.retain_artifacts(self.record)
        self.record["files"][0]["path"] = "../outside.bin"
        with self.assertRaises(validator.CaptureError):
            validator.check_capture_files(self.record, self.work)

    def test_changed_artifact_size_or_hash_is_rejected_without_mutating_record(self):
        self.retain_artifacts(self.record)
        original = copy.deepcopy(self.record)
        for payload in (SYNTHETIC_DERIVED, SYNTHETIC_RAW + b"x", b""):
            (self.work / "raw.bin").write_bytes(payload)
            with self.subTest(payload=payload), self.assertRaises(validator.CaptureError):
                validator.check_capture_files(self.record, self.work)
            self.assertEqual(self.record, original)

    def test_byte_checker_rejects_missing_nonregular_files_and_invalid_roots(self):
        with self.assertRaises(validator.CaptureError):
            validator.check_capture_files(self.record, self.work)
        (self.work / "raw.bin").mkdir()
        with self.assertRaises(validator.CaptureError):
            validator.check_capture_files(self.record, self.work)
        (self.work / "raw.bin").rmdir()
        self.retain_artifacts(self.record)
        for root in (self.work / "missing-root", self.work / "raw.bin"):
            with self.subTest(root=str(root)), self.assertRaises(validator.CaptureError):
                validator.check_capture_files(self.record, root)

    def test_symlink_file_directory_and_root_cannot_alias_artifacts(self):
        target = self.work / "synthetic-target.bin"
        target.write_bytes(SYNTHETIC_RAW)
        link = self.work / "raw.bin"
        link.symlink_to(target)
        with self.assertRaises(validator.CaptureError):
            validator.check_capture_files(self.record, self.work)
        link.unlink()
        target_directory = self.work / "target-directory"
        target_directory.mkdir()
        (target_directory / "raw.bin").write_bytes(SYNTHETIC_RAW)
        directory_link = self.work / "alias"
        directory_link.symlink_to(target_directory, target_is_directory=True)
        self.record["files"][0]["path"] = "alias/raw.bin"
        with self.assertRaises(validator.CaptureError):
            validator.check_capture_files(self.record, self.work)
        self.record["files"][0]["path"] = "raw.bin"
        with self.assertRaises(validator.CaptureError):
            validator.check_capture_files(self.record, directory_link)

    def test_hardlink_aliases_reject_but_independent_equal_byte_copies_pass(self):
        record = synthetic_record()
        record["files"].append(file_record("second", "second.bin"))
        self.retain_artifacts(record)
        self.assertEqual(validator.check_capture_files(record, self.work)["files_checked"], 2)
        (self.work / "second.bin").unlink()
        os.link(self.work / "raw.bin", self.work / "second.bin")
        with self.assertRaises(validator.CaptureError):
            validator.check_capture_files(record, self.work)

    def test_path_identity_preserves_alias_check_when_descriptor_identity_is_unavailable(self):
        record = synthetic_record()
        record["files"].append(file_record("second", "second.bin"))
        self.retain_artifacts(record)
        with mock.patch.object(validator, "os", platform_without_descriptor_identity()):
            self.assertEqual(validator.check_capture_files(record, self.work)["files_checked"], 2)
            (self.work / "second.bin").unlink()
            os.link(self.work / "raw.bin", self.work / "second.bin")
            with self.assertRaisesRegex(validator.CaptureError, "hardlink alias"):
                validator.check_capture_files(record, self.work)

    def test_unavailable_file_identity_cannot_silently_qualify_alias_check(self):
        self.retain_artifacts(self.record)
        real_lstat = Path.lstat

        def unavailable(path):
            return without_file_identity(real_lstat(path))

        with mock.patch.object(validator, "os", platform_without_descriptor_identity()), \
                mock.patch.object(Path, "lstat", unavailable):
            with self.assertRaisesRegex(validator.CaptureError, "file identity unavailable"):
                validator.check_capture_files(self.record, self.work)

    def test_cli_default_reports_structure_and_explicit_unestablished_claims(self):
        self.write_manifest(self.record)
        result = self.cli("--input", self.path)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(json.loads(result.stdout), {
            "capture_id": self.record["capture_id"], "record_status": "recorded",
            "structural_validation": "pass", "file_check": None,
            "authenticity": "not_established", "calibration": "not_established",
            "physical_fidelity": "not_established",
        })
        self.assertFalse((self.work / "raw.bin").exists())
        result = self.cli("--input", EXAMPLE_PATH)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["record_status"], "planned")
        self.assertIsNone(json.loads(result.stdout)["file_check"])

    def test_cli_explicit_check_supports_default_and_separate_artifact_roots(self):
        self.write_manifest(self.record)
        self.retain_artifacts(self.record)
        result = self.cli("--input", self.path, "--check-files")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["file_check"]["bytes_checked"], 4)
        separate = self.work / "metadata"
        separate.mkdir()
        metadata = self.write_manifest(self.record, separate / "capture.json")
        result = self.cli("--input", metadata, "--check-files", "--artifact-root", self.work)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)["file_check"]
        self.assertEqual(report["scope"], "declared-byte-integrity-only")
        for claim in ("authenticity", "calibration", "physical_fidelity"):
            self.assertEqual(report[claim], "not_established")
        self.assert_capture_failure(self.cli("--input", metadata, "--check-files"))

    def test_cli_failures_are_clear_and_never_emit_a_success_report(self):
        self.path.write_text("{}", encoding="utf-8")
        self.assert_capture_failure(self.cli("--input", self.path))
        self.assert_capture_failure(self.cli("--input", self.work / "missing.json"))
        self.assert_capture_failure(self.cli("--input", EXAMPLE_PATH, "--check-files"))
        self.write_manifest(self.record)
        self.assert_capture_failure(self.cli("--input", self.path, "--check-files"))
        for arguments in ((), ("--input", self.path, "--artifact-root", self.work),
                          ("--input", self.path, "--unknown-option")):
            result = self.cli(*arguments)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertEqual(result.stdout, "")
            self.assertIn("error", result.stderr.lower())
            self.assertNotIn("Traceback", result.stderr)

    def test_public_main_returns_status_and_does_not_change_input_file(self):
        self.write_manifest(self.record)
        before = self.path.read_bytes()
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = validator.main(["--input", str(self.path)])
        self.assertEqual(status, 0)
        self.assertEqual(stderr.getvalue(), "")
        self.assertIsNone(json.loads(stdout.getvalue())["file_check"])
        self.assertEqual(self.path.read_bytes(), before)
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = validator.main(["--input", str(self.work / "missing.json")])
        self.assertEqual(status, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("capture error:", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
