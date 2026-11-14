#!/usr/bin/env python3
"""Independent declaration-readiness contract acceptance; no acquired evidence.

Literal expectations and fictional metadata are authored from
docs/CAPTURE_READINESS.md and CAPTURE_FORMAT.md. No producer table or private
readiness function computes an expected result. Fault hooks qualify named paths,
not operating-system-wide or physical behavior.
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
import shutil
import stat
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "capture_readiness.py"
sys.path.insert(0, str(TOOL.parent))
SPEC = importlib.util.spec_from_file_location("independent_readiness_subject", TOOL)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {TOOL}")
readiness = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = readiness
SPEC.loader.exec_module(readiness)

ORIGIN = "project-proposed-capture-readiness-v1"
ROOT_KEYS = {"schema_version", "contract_origin", "scope", "capture_id",
             "capture_kind", "record_status", "status", "input", "manifest",
             "calibration_context", "checks", "summary", "claims"}
CLAIMS = {key: "not_established" for key in (
    "artifact_integrity", "audio_content", "authenticity", "calibration",
    "permissions", "corpus_independence", "physical_fidelity")}

# This is the independent literal table from the public contract. In particular,
# it is not imported from the implementation's _CHECKS or _CHANNEL_CHECKS.
CHECKS = (
    ("specimen.specimen_id", "specimen", "Record the actual hardware specimen identifier after identity review."),
    ("specimen.variant", "specimen", "Record the hardware variant or the synthetic model identity."),
    ("specimen.revision", "specimen", "Record the applicable hardware revision or synthetic code/model revision."),
    ("specimen.identity_evidence", "specimen", "Locate retained evidence for the declared subject and configuration identity."),
    ("acquisition.started_at_utc", "acquisition", "Record the actual acquisition start time only after acquisition occurs."),
    ("acquisition.operator_id", "acquisition", "Assign or record a stable operator identifier."),
    ("acquisition.session_id", "acquisition", "Assign or record the acquisition session identifier."),
    ("digital.format", "digital", "Declare the raw acquisition format and later check the actual stream."),
    ("digital.sample_rate_hz", "digital", "Declare the raw digital sample rate without substituting it for physical clock calibration."),
    ("digital.channel_count", "digital", "Declare the raw channel count and ordered channel map."),
    ("physical_clock", "clock", "Obtain and review physical clock calibration evidence for the actual acquisition setup."),
    ("stimulus.description", "stimulus", "Describe the intended or observed stimulus and retain its schedule."),
    ("stimulus.controls", "stimulus", "Declare the control settings and complete gesture/state history."),
    ("stimulus.conditions", "stimulus", "Declare the relevant operating conditions with units and unresolved quantities."),
    ("stimulus.synchronization", "stimulus", "Describe synchronization and its evidence without inferring it from a shared group."),
    ("signal_path.description", "signal_path", "Describe the connected path and separately identify its equipment or synthetic stages."),
    ("signal_path.bypass", "signal_path", "Declare the bypass states applicable to this signal path."),
    ("signal_path.loading", "signal_path", "Declare connected loads or an explicit synthetic context without inferring physical impedance."),
    ("rights", "rights", "Locate separate store, analyze, derive-model and redistribute decisions for review."),
    ("partition.role", "partition", "Assign the intended analysis role after whole-group and purpose review."),
    ("partition.group_id", "partition", "Declare the complete related acquisition group before analysis."),
)
CHANNEL_CHECKS = (
    ("boundary", "Identify the channel signal boundary without changing its physical meaning."),
    ("port_reference", "Declare the channel port, polarity/reference or microphone identity and pose."),
    ("calibration", "Obtain and review channel scale and uncertainty evidence at the declared boundary."),
)


def known(value):
    return {"value": value, "unknown_reason": None}


def unknown(path):
    return {"value": None, "unknown_reason": "  Unresolved " + path + " — μ  "}


def uncalibrated(unit, label):
    return {"status": "uncalibrated", "value": None, "unit": unit,
            "standard_uncertainty": None, "evidence": None,
            "unknown_reason": "  No observed calibration for " + label + " — μ  "}


def nonphysical(label):
    return {"status": "not_applicable", "value": None, "unit": None,
            "standard_uncertainty": None, "evidence": None,
            "unknown_reason": "  Synthetic " + label + "; no physical scale — μ  "}


def calibrated(unit, value):
    return {"status": "calibrated", "value": value, "unit": unit,
            "standard_uncertainty": 0.125, "evidence": "unread/evidence-μ.txt",
            "unknown_reason": None}


def plan():
    return {
        "schema_version": 1, "contract_origin": "project-proposed-v1",
        "capture_id": "independent-readiness-plan", "status": "planned",
        "status_reason": "Fictional planning fixture only; nothing was acquired.",
        "capture_kind": "hardware",
        "specimen": {name: unknown("specimen." + name) for name in
                     ("specimen_id", "variant", "revision", "identity_evidence")},
        "acquisition": {name: unknown("acquisition." + name) for name in
                        ("started_at_utc", "operator_id", "session_id")},
        "digital": {"format": unknown("digital.format"),
                    "sample_rate_hz": unknown("digital.sample_rate_hz"),
                    "channel_count": unknown("digital.channel_count"), "channels": []},
        "physical_clock": uncalibrated("Hz", "clock"),
        "stimulus": {name: unknown("stimulus." + name) for name in
                     ("description", "controls", "conditions", "synchronization")},
        "signal_path": {name: unknown("signal_path." + name) for name in
                        ("description", "bypass", "loading")},
        "files": [], "partition": {"role": "unassigned",
                                      "group_id": unknown("partition.group_id"),
                                      "rationale": "  No actual fit or held-out take — μ  "},
        "rights": unknown("rights"),
    }


def recorded(kind="hardware", channels=1):
    """Fictional declarations only; deliberately absent artifacts/evidence."""
    value = plan()
    value.update(status="recorded", status_reason=None, capture_kind=kind,
                 capture_id="independent-readiness-" + kind)
    value["specimen"] = {
        "specimen_id": known("fictional-specimen") if kind == "hardware" else
                       unknown("synthetic specimen exemption"),
        "variant": known("Fictional metadata fixture — no instrument measurement"),
        "revision": known("Independent fixture revision one"),
        "identity_evidence": known("unread/identity-evidence.txt"),
    }
    value["acquisition"] = {
        "started_at_utc": known("2024-02-29T10:11:12.123456Z"),
        "operator_id": known("fictional-operator"), "session_id": known("fictional-session"),
    }
    value["digital"] = {
        "format": known("raw_float32_le"), "sample_rate_hz": known(48000),
        "channel_count": known(channels), "channels": [],
    }
    for index in range(channels):
        value["digital"]["channels"].append({
            "channel_id": f"channel-{index}", "index": index,
            "boundary": known("synthetic" if kind == "synthetic" else "preamp_GG"),
            "port_reference": known("Fictional port declaration " + str(index)),
            "calibration": nonphysical("channel " + str(index)) if kind == "synthetic" else
                           calibrated("V/FS", 0.25),
        })
    value["physical_clock"] = nonphysical("clock") if kind == "synthetic" else calibrated("Hz", 48000)
    for section in ("stimulus", "signal_path"):
        for name in value[section]:
            value[section][name] = known("Fictional " + section + "." + name + " — μ")
    value["files"] = [{"file_id": "raw", "kind": "raw", "path": "absent/raw.f32",
                       "size_bytes": 4, "sha256": "a" * 64, "parents": [], "derivation": None}]
    value["partition"] = {"role": "fit", "group_id": known("fictional-group"),
                           "rationale": "Fictional metadata only; no independent acquisition."}
    value["rights"] = known("unread/rights-decisions.txt")
    return value


def encode(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2,
                       allow_nan=False) + "\n").encode("utf-8")


def field(value, path):
    for component in path.split("."):
        value = value[component]
    return value


def node_count(value):
    pending = [value]
    total = 0
    while pending:
        item = pending.pop()
        total += 1
        if type(item) is dict:
            pending.extend(item.values())
        elif type(item) is list:
            pending.extend(item)
    return total


def container_depth(value):
    pending, deepest = [(value, 0)], 0
    while pending:
        item, depth = pending.pop()
        if type(item) in (dict, list):
            deepest = max(deepest, depth)
            children = item.values() if type(item) is dict else item
            pending.extend((child, depth + 1) for child in children)
    return deepest


class _BinaryStandard:
    def __init__(self, buffer=None):
        self.buffer = io.BytesIO() if buffer is None else buffer

    def write(self, text):
        raise AssertionError("real binary-buffer path must not use terminal text encoding")


class _ShortText(io.StringIO):
    def write(self, value):
        super().write(value[:7])
        return 7


class ReadinessCase(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="readiness independent μ ")
        self.addCleanup(temporary.cleanup)
        # Match canonical ancestor observations when fault hooks compare paths.
        self.root = Path(temporary.name).resolve(strict=True)
        self.path = self.root / "capture.json"

    def write(self, value=None, *, payload=None, path=None):
        target = self.path if path is None else path
        data = encode(plan() if value is None else value) if payload is None else payload
        target.write_bytes(data)
        return target

    def inspect(self, value=None):
        return readiness.inspect_readiness(self.write(value))

    def reject(self, expected, path=None):
        with self.assertRaises(readiness.ReadinessError) as raised:
            readiness.inspect_readiness(self.path if path is None else path)
        self.assertEqual(raised.exception.code, expected)
        self.assertIsInstance(raised.exception, ValueError)
        self.assertEqual(str(raised.exception), raised.exception.message)
        self.assertTrue(raised.exception.message)
        return raised.exception

    def main(self, args, *, stdout=None, stderr=None):
        out = io.StringIO() if stdout is None else stdout
        err = io.StringIO() if stderr is None else stderr
        with redirect_stdout(out), redirect_stderr(err):
            code = readiness.main(args)
        return code, out, err

    def assert_error(self, result, code, error_code):
        actual, out, err = result
        self.assertEqual(actual, code)
        self.assertEqual(out.getvalue(), "")
        value = json.loads(err.getvalue())
        self.assertEqual(set(value), {"schema_version", "contract_origin", "status", "error"})
        self.assertEqual(value["schema_version"], 1)
        self.assertEqual(value["contract_origin"], ORIGIN)
        self.assertEqual(value["status"], "rejected")
        self.assertEqual(set(value["error"]), {"code", "message"})
        self.assertEqual(value["error"]["code"], error_code)
        self.assertTrue(value["error"]["message"])
        self.assertEqual(err.getvalue().encode("utf-8"), encode(value))
        return value

    def assert_report(self, report, manifest, payload):
        self.assertEqual(set(report), ROOT_KEYS)
        self.assertEqual(report["schema_version"], 1)
        self.assertEqual(report["contract_origin"], ORIGIN)
        self.assertEqual(report["scope"], "declared-metadata-only")
        self.assertEqual(report["capture_id"], manifest["capture_id"])
        self.assertEqual(report["capture_kind"], manifest["capture_kind"])
        self.assertEqual(report["record_status"], manifest["status"])
        self.assertEqual(report["manifest"], manifest)
        self.assertEqual(report["calibration_context"], "raw_acquisition_only")
        self.assertEqual(report["input"], {"sha256": hashlib.sha256(payload).hexdigest(),
                                            "size_bytes": len(payload)})
        self.assertEqual(report["claims"], CLAIMS)
        expected_paths = [item[0] for item in CHECKS]
        for index in range(len(manifest["digital"]["channels"])):
            expected_paths.extend(f"digital.channels[{index}].{item[0]}" for item in CHANNEL_CHECKS)
        self.assertEqual([item["path"] for item in report["checks"]], expected_paths)
        self.assertEqual(len(set(expected_paths)), len(expected_paths))
        self.assertEqual([item["category"] for item in report["checks"]],
                         [item[1] for item in CHECKS] + ["channel"] * (len(expected_paths) - 21))
        counts = {"total": len(expected_paths), "declared": 0, "missing": 0, "not_applicable": 0}
        for item in report["checks"]:
            self.assertEqual(set(item), {"path", "category", "state", "reason", "action"})
            self.assertIn(item["state"], {"declared", "missing", "not_applicable"})
            counts[item["state"]] += 1
        self.assertEqual(report["summary"], counts)
        self.assertTrue(all(type(number) is int for number in report["summary"].values()))
        self.assertNotIn(str(self.root), encode(report).decode("utf-8"))


class DeclarationSemantics(ReadinessCase):
    def test_all_unknown_plan_has_literal_checks_actions_and_reasons(self):
        manifest = plan()
        report = self.inspect(manifest)
        self.assert_report(report, manifest, encode(manifest))
        self.assertEqual(report["status"], "planned")
        self.assertEqual(report["summary"], {"total": 21, "declared": 0, "missing": 21, "not_applicable": 0})
        for item, (path, category, action) in zip(report["checks"], CHECKS):
            expected_reason = (manifest["partition"]["rationale"] if path == "partition.role"
                               else field(manifest, path)["unknown_reason"])
            self.assertEqual(item, {"path": path, "category": category, "state": "missing",
                                    "reason": expected_reason, "action": action})

    def test_supplied_plan_retains_its_original_declared_intention(self):
        path = ROOT / "data" / "capture-planned-example.json"
        payload = path.read_bytes()
        manifest = json.loads(payload)
        report = readiness.inspect_readiness(path)
        self.assert_report(report, manifest, payload)
        self.assertEqual(report["status"], "planned")
        self.assertEqual(report["summary"], {"total": 21, "declared": 1, "missing": 20, "not_applicable": 0})
        self.assertEqual(report["checks"][11], {"path": "stimulus.description", "category": "stimulus",
                                                "state": "declared", "reason": None, "action": None})

    def test_complete_hardware_declarations_do_not_establish_physical_claims(self):
        manifest = recorded()
        report = self.inspect(manifest)
        self.assert_report(report, manifest, encode(manifest))
        self.assertEqual(report["status"], "declarations_complete")
        self.assertEqual(report["summary"], {"total": 24, "declared": 24, "missing": 0, "not_applicable": 0})
        self.assertTrue(all(item["state"] == "declared" and item["reason"] is None and
                            item["action"] is None for item in report["checks"]))
        self.assertFalse((self.root / "absent").exists())

    def test_synthetic_exemptions_are_exact_and_do_not_create_unity_scales(self):
        manifest = recorded("synthetic")
        report = self.inspect(manifest)
        self.assert_report(report, manifest, encode(manifest))
        self.assertEqual(report["status"], "declarations_complete")
        self.assertEqual(report["summary"], {"total": 24, "declared": 21, "missing": 0, "not_applicable": 3})
        for index, original in ((0, manifest["specimen"]["specimen_id"]),
                                (10, manifest["physical_clock"]),
                                (23, manifest["digital"]["channels"][0]["calibration"])):
            self.assertEqual(report["checks"][index]["state"], "not_applicable")
            self.assertEqual(report["checks"][index]["reason"], original["unknown_reason"])
            self.assertIsNone(report["checks"][index]["action"])
            self.assertIsNone(original["value"])

    def test_synthetic_unknowns_outside_exemptions_stay_missing(self):
        manifest = recorded("synthetic")
        for section, name in (("specimen", "variant"), ("specimen", "revision"),
                              ("specimen", "identity_evidence"), ("stimulus", "synchronization")):
            manifest[section][name] = unknown(section + "." + name)
        manifest["digital"]["channels"][0]["port_reference"] = unknown("port")
        manifest["rights"] = unknown("rights")
        report = self.inspect(manifest)
        self.assertEqual(report["status"], "declarations_incomplete")
        self.assertEqual(report["summary"], {"total": 24, "declared": 15, "missing": 6, "not_applicable": 3})
        self.assertEqual([item["path"] for item in report["checks"] if item["state"] == "missing"],
                         ["specimen.variant", "specimen.revision", "specimen.identity_evidence",
                          "stimulus.synchronization", "rights", "digital.channels[0].port_reference"])

    def test_each_optional_hardware_unknown_retains_literal_reason_and_action(self):
        indices = [0, 1, 2, 3, 11, 12, 13, 14, 15, 16, 17, 18]
        for index in indices:
            with self.subTest(path=CHECKS[index][0]):
                manifest = recorded()
                path, category, action = CHECKS[index]
                parts = path.split(".")
                owner = manifest if len(parts) == 1 else manifest[parts[0]]
                owner[parts[-1]] = unknown(path)
                report = self.inspect(manifest)
                self.assertEqual(report["status"], "declarations_incomplete")
                self.assertEqual(report["summary"]["missing"], 1)
                self.assertEqual(report["checks"][index], {"path": path, "category": category,
                    "state": "missing", "reason": unknown(path)["unknown_reason"], "action": action})

    def test_uncalibrated_hardware_clock_and_channels_remain_missing(self):
        manifest = recorded(channels=2)
        manifest["physical_clock"] = uncalibrated("Hz", "clock")
        for index, channel in enumerate(manifest["digital"]["channels"]):
            channel["calibration"] = uncalibrated("V/FS", "channel " + str(index))
        report = self.inspect(manifest)
        self.assertEqual(report["summary"], {"total": 27, "declared": 24, "missing": 3, "not_applicable": 0})
        for index in (10, 23, 26):
            self.assertEqual(report["checks"][index]["state"], "missing")
            self.assertIsNotNone(report["checks"][index]["action"])
        self.assertEqual(report["claims"], CLAIMS)

    def test_unknown_channel_boundary_port_and_scale_have_separate_actions(self):
        manifest = recorded()
        channel = manifest["digital"]["channels"][0]
        channel["boundary"], channel["port_reference"] = unknown("boundary"), unknown("port")
        channel["calibration"] = uncalibrated(None, "unknown boundary")
        report = self.inspect(manifest)
        self.assertEqual(report["summary"]["missing"], 3)
        for item, (name, action) in zip(report["checks"][21:], CHANNEL_CHECKS):
            self.assertEqual(item, {"path": "digital.channels[0]." + name, "category": "channel",
                "state": "missing", "reason": channel[name]["unknown_reason"], "action": action})

    def test_partition_roles_do_not_assert_validation_or_holdout_history(self):
        for role, expected in (("fit", "declared"), ("held_out", "declared"), ("unassigned", "missing")):
            with self.subTest(role=role):
                manifest = recorded()
                manifest["partition"]["role"] = role
                report = self.inspect(manifest)
                self.assertEqual(report["checks"][19]["state"], expected)
                self.assertEqual(report["checks"][19]["reason"],
                    manifest["partition"]["rationale"] if role == "unassigned" else None)
                self.assertEqual(report["claims"], CLAIMS)

    def test_planning_status_dominates_high_declaration_count(self):
        manifest = recorded("synthetic", channels=16)
        manifest.update(status="planned", status_reason="Declared intentions only.", files=[])
        manifest["acquisition"]["started_at_utc"] = unknown("not yet acquired")
        report = self.inspect(manifest)
        self.assertEqual(report["status"], "planned")
        self.assertEqual(report["summary"], {"total": 69, "declared": 50, "missing": 1, "not_applicable": 18})

    def test_actual_sixteen_channel_boundary_has_sixty_nine_ordered_checks(self):
        for kind in ("hardware", "synthetic"):
            with self.subTest(kind=kind):
                manifest = recorded(kind, channels=16)
                report = self.inspect(manifest)
                self.assert_report(report, manifest, encode(manifest))
                self.assertEqual(report["summary"]["total"], 69)
                self.assertEqual(report["checks"][-1]["path"], "digital.channels[15].calibration")
                self.assertEqual(report["summary"]["not_applicable"], 18 if kind == "synthetic" else 0)

    def test_derived_context_retains_raw_declarations_without_inheriting_scale(self):
        manifest = recorded()
        manifest["files"].append({"file_id": "derived", "kind": "derived", "path": "processed/new.wav",
            "size_bytes": 8, "sha256": "b" * 64, "parents": ["raw"],
            "derivation": {"operation": "Fictional resampling and gain declaration", "tool": "fixture",
                           "tool_version": "1", "parameters": "Output 96000 Hz and gain 2; not executed."}})
        report = self.inspect(manifest)
        self.assertEqual(report["manifest"], manifest)
        self.assertEqual(report["calibration_context"], "raw_acquisition_only")
        self.assertEqual(len(report["checks"]), 24)
        self.assertEqual(report["manifest"]["digital"]["sample_rate_hz"]["value"], 48000)
        self.assertEqual(report["claims"], CLAIMS)

    def test_original_bytes_identity_is_not_a_canonical_reserialization(self):
        manifest = plan()
        compact = json.dumps(manifest, ensure_ascii=True, separators=(",", ":")).encode("ascii")
        spaced = b" \r\n" + encode(manifest) + b"\t "
        a = readiness.inspect_readiness(self.write(payload=compact))
        b = readiness.inspect_readiness(self.write(payload=spaced))
        self.assertEqual(a["manifest"], b["manifest"])
        self.assertEqual(a["input"], {"sha256": hashlib.sha256(compact).hexdigest(), "size_bytes": len(compact)})
        self.assertEqual(b["input"], {"sha256": hashlib.sha256(spaced).hexdigest(), "size_bytes": len(spaced)})
        self.assertNotEqual(a["input"]["sha256"], b["input"]["sha256"])
        a.pop("input"); b.pop("input")
        self.assertEqual(a, b)

    def test_separate_calls_are_deeply_independent_and_input_is_unchanged(self):
        self.write(recorded("synthetic"))
        before = self.path.read_bytes()
        a, b = readiness.inspect_readiness(self.path), readiness.inspect_readiness(self.path)
        self.assertEqual(a, b)
        a["manifest"]["digital"]["channels"][0]["calibration"]["value"] = 999
        a["checks"][0]["reason"] = "changed externally"
        a["summary"]["missing"] = 999
        a["claims"]["physical_fidelity"] = "invented"
        self.assertEqual(b, readiness.inspect_readiness(self.path))
        self.assertEqual(self.path.read_bytes(), before)

    def test_only_manifest_is_read_once_and_evidence_locators_are_not_followed(self):
        self.write(recorded())
        original_open = os.open
        calls = []
        def observed_open(path, *args, **kwargs):
            calls.append(Path(path))
            self.assertEqual(Path(path), self.path)
            return original_open(path, *args, **kwargs)
        with mock.patch.object(readiness.common.os, "open", side_effect=observed_open), \
             mock.patch.object(readiness.capture, "check_capture_files", side_effect=AssertionError("no artifact audit")):
            report = readiness.inspect_readiness(self.path)
        self.assertEqual(calls, [self.path])
        self.assertEqual(report["status"], "declarations_complete")

    def test_unicode_relocation_and_foreign_working_directory_are_deterministic(self):
        self.write(recorded("synthetic"))
        another = self.root / "relocated Ω"
        another.mkdir()
        clone = another / "manifest μ.json"
        shutil.copyfile(self.path, clone)
        original = readiness.inspect_readiness(self.path)
        self.assertEqual(original, readiness.inspect_readiness(clone))
        with mock.patch("os.getcwd", return_value=str(another)):
            # Explicit absolute paths do not depend on cwd metadata hooks.
            self.assertEqual(original, readiness.inspect_readiness(clone))


class InputAdmission(ReadinessCase):
    def test_exact_public_path_types_reject_other_pathlike_objects(self):
        selected = str(self.path)
        class StringSubclass(str):
            pass
        class PathLike:
            def __fspath__(self):
                return selected
        invalid = [None, True, False, 7, 1.0, b"capture.json", [], {}, "",
                   StringSubclass(str(self.path)), PathLike()]
        for path in invalid:
            with self.subTest(type=type(path).__name__, value=repr(path)):
                self.reject("invalid_argument", path=path if path is not None else False)
        self.write()
        self.assertEqual(readiness.inspect_readiness(str(self.path)), readiness.inspect_readiness(self.path))

    def test_none_api_path_rejects_without_reading_current_directory(self):
        with self.assertRaises(readiness.ReadinessError) as raised:
            readiness.inspect_readiness(None)
        self.assertEqual(raised.exception.code, "invalid_argument")

    def test_actual_inclusive_and_excess_original_byte_limits(self):
        payload = encode(plan())
        padded = payload + b" " * (65536 - len(payload))
        self.write(payload=padded)
        report = readiness.inspect_readiness(self.path)
        self.assertEqual(report["input"], {"sha256": hashlib.sha256(padded).hexdigest(), "size_bytes": 65536})
        self.write(payload=padded + b" ")
        with mock.patch.object(readiness.common.os, "open", side_effect=AssertionError("oversize input must reject before open")):
            self.reject("input_error")

    def test_json_byte_syntax_and_duplicate_keys_reject_as_input_errors(self):
        payload = encode(plan())
        variants = [b"", b"\xef\xbb\xbf" + payload, b"\xff" + payload,
                    payload + b"{}", b'{"x":1,"x":2}',
                    payload.replace(b'"schema_version": 1', b'"schema_version": 1, "schema_version": 1'),
                    payload.replace(b'"value": null', b'"value": null, "value": null', 1),
                    b'{"x":NaN}', b'{"x":Infinity}', b'{"x":-Infinity}',
                    b'{"x":1e1000}', b'{"x":"\\ud800"}', b'{"\\udfff":1}',
                    b'{"x":"literal\ncontrol"}']
        for data in variants:
            with self.subTest(payload=data[:70]):
                self.write(payload=data)
                self.reject("input_error")

    def test_exact_numeric_token_and_magnitude_boundary_stage(self):
        for data, code in ((b"0." + b"0" * 62, "invalid_manifest"),
                           (b"0." + b"0" * 63, "input_error"),
                           (b"1000000000000", "invalid_manifest"),
                           (b"1000000000001", "input_error"),
                           (b"-1000000000001", "input_error")):
            with self.subTest(payload=data):
                self.write(payload=data)
                self.reject(code)

    def test_actual_json_value_node_boundary_precedes_v1_shape_admission(self):
        for count, code in ((4095, "invalid_manifest"), (4096, "input_error")):
            with self.subTest(total_nodes=count + 1):
                value = [0] * count
                self.assertEqual(node_count(value), count + 1)
                self.write(payload=json.dumps(value, separators=(",", ":")).encode("ascii"))
                self.reject(code)

    def test_actual_container_depth_boundary_precedes_v1_shape_admission(self):
        for arrays, code in ((17, "invalid_manifest"), (18, "input_error")):
            with self.subTest(deepest_container=arrays - 1):
                payload = b"[" * arrays + b"0" + b"]" * arrays
                self.assertEqual(container_depth(json.loads(payload)), arrays - 1)
                self.write(payload=payload)
                self.reject(code)

    def test_nonmanifest_json_values_and_wrong_exact_types_reject(self):
        for value in (None, True, 1, 1.0, "a string", [], {}):
            with self.subTest(value=value):
                self.write(payload=encode(value))
                self.reject("invalid_manifest")
        for version in (True, 1.0, "1"):
            with self.subTest(version=version):
                value = plan(); value["schema_version"] = version
                self.write(value); self.reject("invalid_manifest")
        value = recorded(); value["digital"]["sample_rate_hz"] = known(True)
        self.write(value); self.reject("invalid_manifest")

    def test_unknown_keys_and_missing_keys_at_nested_objects_reject(self):
        for location in ((), ("specimen",), ("specimen", "variant"), ("partition",),
                         ("physical_clock",), ("digital", "channels", 0)):
            for change in ("extra", "missing"):
                with self.subTest(location=location, change=change):
                    value = recorded()
                    owner = value
                    for part in location:
                        owner = owner[part]
                    if change == "extra":
                        owner["invented"] = 1
                    else:
                        del owner[next(iter(owner))]
                    self.write(value); self.reject("invalid_manifest")

    def test_unknown_known_and_control_text_consistency_remains_v1(self):
        fixtures = []
        value = plan(); value["rights"] = {"value": None, "unknown_reason": None}; fixtures.append(value)
        value = plan(); value["rights"] = {"value": "known", "unknown_reason": "contradiction"}; fixtures.append(value)
        value = plan(); value["rights"] = unknown("reason"); value["rights"]["unknown_reason"] = " \t "; fixtures.append(value)
        value = plan(); value["rights"] = known("escaped\ncontrol"); fixtures.append(value)
        value = plan(); value["rights"] = known("x" * 2049); fixtures.append(value)
        for index, value in enumerate(fixtures):
            with self.subTest(index=index):
                self.write(value); self.reject("invalid_manifest")

    def test_calendar_record_status_and_required_recorded_fields_are_enforced(self):
        fixtures = []
        value = recorded(); value["acquisition"]["started_at_utc"] = known("2023-02-29T10:11:12Z"); fixtures.append(value)
        value = plan(); value["acquisition"]["started_at_utc"] = known("2024-02-29T10:11:12Z"); fixtures.append(value)
        value = recorded(); value["status_reason"] = "claimed plan"; fixtures.append(value)
        for section, name in (("acquisition", "operator_id"), ("acquisition", "session_id"),
                              ("digital", "format"), ("digital", "sample_rate_hz"),
                              ("partition", "group_id")):
            value = recorded(); value[section][name] = unknown(section + name); fixtures.append(value)
        for index, value in enumerate(fixtures):
            with self.subTest(index=index):
                self.write(value); self.reject("invalid_manifest")

    def test_hardware_synthetic_calibration_units_and_state_rules_are_preserved(self):
        fixtures = []
        value = recorded(); value["physical_clock"] = nonphysical("clock"); fixtures.append(value)
        value = recorded("synthetic"); value["specimen"]["specimen_id"] = known("false-physical-id"); fixtures.append(value)
        value = recorded("synthetic"); value["physical_clock"] = calibrated("Hz", 48000); fixtures.append(value)
        value = recorded(); value["digital"]["channels"][0]["calibration"]["unit"] = "Pa/FS"; fixtures.append(value)
        value = recorded(); value["digital"]["channels"][0]["boundary"] = known("synthetic"); fixtures.append(value)
        value = recorded("synthetic"); value["digital"]["channels"][0]["boundary"] = known("preamp_GG"); fixtures.append(value)
        value = recorded(); value["physical_clock"]["value"] = 0; fixtures.append(value)
        value = recorded(); value["physical_clock"]["standard_uncertainty"] = -1; fixtures.append(value)
        value = recorded(); value["physical_clock"]["evidence"] = None; fixtures.append(value)
        for index, value in enumerate(fixtures):
            with self.subTest(index=index):
                self.write(value); self.reject("invalid_manifest")

    def test_channel_count_order_identity_and_seventeen_channel_excess_reject(self):
        fixtures = []
        value = recorded(channels=17); fixtures.append(value)
        value = recorded(channels=2); value["digital"]["channels"].reverse(); fixtures.append(value)
        value = recorded(channels=2); value["digital"]["channels"][1]["channel_id"] = "channel-0"; fixtures.append(value)
        value = recorded(); value["digital"]["channel_count"] = known(2); fixtures.append(value)
        value = plan(); value["digital"]["channels"] = recorded()["digital"]["channels"]; fixtures.append(value)
        for index, value in enumerate(fixtures):
            with self.subTest(index=index):
                self.write(value); self.reject("invalid_manifest")

    def test_file_ancestry_and_portable_path_semantics_are_still_validated(self):
        for path in ("../raw.f32", "/raw.f32", "C:\\raw.f32", "raw/CON.txt", "μ.f32"):
            with self.subTest(path=path):
                value = recorded(); value["files"][0]["path"] = path
                self.write(value); self.reject("invalid_manifest")
        value = recorded(); value["files"] = []
        self.write(value); self.reject("invalid_manifest")
        value = recorded(); value["files"][0].update(kind="derived", parents=["raw"],
            derivation={"operation": "cycle", "tool": "fixture", "tool_version": "1", "parameters": "none"})
        self.write(value); self.reject("invalid_manifest")

    def test_missing_directory_fifo_and_symlink_leaves_reject(self):
        self.reject("input_error")
        self.reject("input_error", self.root)
        if hasattr(os, "mkfifo"):
            fifo = self.root / "fifo"
            try:
                os.mkfifo(fifo)
            except OSError as error:
                self.skipTest("native FIFO unavailable: " + str(error))
            self.reject("input_error", fifo)
        self.write()
        alias = self.root / "alias.json"
        try:
            alias.symlink_to(self.path)
        except (OSError, NotImplementedError) as error:
            self.skipTest("native symlink unavailable: " + str(error))
        self.reject("input_error", alias)

    def test_parent_alias_and_hardlinked_manifest_are_allowed(self):
        self.write()
        hardlink = self.root / "hardlink.json"
        alias = self.root / "parent-alias"
        try:
            os.link(self.path, hardlink)
            alias.symlink_to(self.root, target_is_directory=True)
        except (OSError, NotImplementedError) as error:
            self.skipTest("native link capability unavailable: " + str(error))
        expected = readiness.inspect_readiness(self.path)
        self.assertEqual(expected, readiness.inspect_readiness(hardlink))
        self.assertEqual(expected, readiness.inspect_readiness(alias / self.path.name))

    def test_controlled_reparse_leaf_metadata_rejects(self):
        self.write()
        original = Path.lstat
        reached = []
        def reparse(path, *args, **kwargs):
            information = original(path, *args, **kwargs)
            if path == self.path:
                reached.append(path)
                return SimpleNamespace(st_mode=information.st_mode, st_file_attributes=0x400)
            return information
        with mock.patch.object(Path, "lstat", autospec=True, side_effect=reparse):
            self.reject("input_error")
        self.assertTrue(reached)

    def test_descriptor_wrap_error_and_cancellation_release_open_input(self):
        self.write()
        original_open = os.open
        for failure in (OSError("injected wrapping failure"), KeyboardInterrupt("cancelled wrapping")):
            descriptors = []
            def observed_open(*args, **kwargs):
                descriptor = original_open(*args, **kwargs)
                descriptors.append(descriptor)
                return descriptor
            with self.subTest(type=type(failure).__name__), \
                 mock.patch.object(readiness.common.os, "open", side_effect=observed_open), \
                 mock.patch.object(readiness.common.os, "fdopen", side_effect=failure):
                if isinstance(failure, OSError):
                    self.reject("input_error")
                else:
                    with self.assertRaises(KeyboardInterrupt):
                        readiness.inspect_readiness(self.path)
            self.assertEqual(len(descriptors), 1)
            with self.assertRaises(OSError):
                os.fstat(descriptors[0])

    def test_observed_in_place_mutation_during_read_rejects(self):
        self.write()
        original_fdopen = os.fdopen
        target = self.path
        class MutatingStream:
            def __init__(self, source): self.source = source
            def __enter__(self): self.source.__enter__(); return self
            def __exit__(self, *args): return self.source.__exit__(*args)
            def fileno(self): return self.source.fileno()
            def read(self, size):
                result = self.source.read(size)
                with target.open("ab") as other: other.write(b" ")
                return result
        with mock.patch.object(readiness.common.os, "fdopen",
                               side_effect=lambda *args, **kwargs: MutatingStream(original_fdopen(*args, **kwargs))):
            self.reject("input_error")


class ReportAdmission(ReadinessCase):
    def test_report_byte_guard_inclusive_and_adjacent_reduced_boundary(self):
        self.write(recorded("synthetic", channels=16))
        expected = readiness.inspect_readiness(self.path)
        length = len(encode(expected))
        self.assertLess(length, 1048576)
        with mock.patch.object(readiness, "MAX_REPORT_BYTES", length):
            self.assertEqual(readiness.inspect_readiness(self.path), expected)
        with mock.patch.object(readiness, "MAX_REPORT_BYTES", length - 1):
            self.reject("report_limit")

    def test_report_node_guard_inclusive_and_adjacent_reduced_boundary(self):
        self.write(recorded("synthetic", channels=16))
        expected = readiness.inspect_readiness(self.path)
        count = node_count(expected)
        self.assertLess(count, 16384)
        with mock.patch.object(readiness, "MAX_REPORT_NODES", count):
            self.assertEqual(readiness.inspect_readiness(self.path), expected)
        with mock.patch.object(readiness, "MAX_REPORT_NODES", count - 1):
            self.reject("report_limit")

    def test_report_depth_guard_inclusive_and_adjacent_reduced_boundary(self):
        self.write(recorded("synthetic"))
        expected = readiness.inspect_readiness(self.path)
        depth = container_depth(expected)
        self.assertLess(depth, 24)
        with mock.patch.object(readiness, "MAX_REPORT_DEPTH", depth):
            self.assertEqual(readiness.inspect_readiness(self.path), expected)
        with mock.patch.object(readiness, "MAX_REPORT_DEPTH", depth - 1):
            self.reject("report_limit")

    def test_maximum_v1_calibration_number_is_retained_without_conversion(self):
        manifest = recorded()
        calibration = manifest["digital"]["channels"][0]["calibration"]
        calibration.update(value=1e12, standard_uncertainty=1e12)
        report = self.inspect(manifest)
        self.assertEqual(report["manifest"]["digital"]["channels"][0]["calibration"], calibration)
        self.assertEqual(report["status"], "declarations_complete")
        self.assertEqual(report["claims"], CLAIMS)

    def test_output_limit_rejection_never_publishes_or_prints_partial_report(self):
        self.write()
        target = self.root / "report.json"
        with mock.patch.object(readiness, "MAX_REPORT_BYTES", 1):
            self.assert_error(self.main(["--input", str(self.path), "--output", str(target)]), 1, "report_limit")
        self.assertFalse(target.exists())
        self.assertEqual(sorted(path.name for path in self.root.iterdir()), ["capture.json"])


class CommandLineAndPublication(ReadinessCase):
    def test_all_success_statuses_have_exact_canonical_text_and_exit(self):
        incomplete = recorded(); incomplete["rights"] = unknown("rights")
        for manifest, expected_code, expected_status in (
                (plan(), 3, "planned"), (incomplete, 3, "declarations_incomplete"),
                (recorded("synthetic"), 0, "declarations_complete")):
            with self.subTest(status=expected_status):
                self.write(manifest)
                code, out, err = self.main(["--input", str(self.path)])
                self.assertEqual(code, expected_code)
                self.assertEqual(err.getvalue(), "")
                report = json.loads(out.getvalue())
                self.assertEqual(report["status"], expected_status)
                self.assert_report(report, manifest, encode(manifest))
                self.assertEqual(out.getvalue().encode("utf-8"), encode(report))

    def test_real_cli_foreign_cwd_unicode_paths_and_ascii_terminal_encoding(self):
        manifest = recorded("synthetic")
        self.path = self.root / "capture Ω.json"
        self.write(manifest)
        foreign = self.root / "unrelated cwd"
        foreign.mkdir()
        environment = dict(os.environ, PYTHONIOENCODING="ascii:strict", PYTHONDONTWRITEBYTECODE="1")
        result = subprocess.run([sys.executable, "-B", str(TOOL), "--input", str(self.path)],
                                cwd=foreign, env=environment, capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, b"")
        report = json.loads(result.stdout.decode("utf-8"))
        self.assert_report(report, manifest, encode(manifest))
        self.assertEqual(result.stdout, encode(report))
        self.assertIn("μ".encode("utf-8"), result.stdout)
        self.assertFalse(list(foreign.iterdir()))

    def test_real_cli_relative_input_and_all_four_exit_categories(self):
        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        cases = [(recorded("synthetic"), ["--input", "capture.json"], 0),
                 (plan(), ["--input", "capture.json"], 3),
                 ({}, ["--input", "capture.json"], 1),
                 (plan(), ["--in", "capture.json"], 2)]
        for value, arguments, code in cases:
            with self.subTest(code=code):
                self.write(value)
                result = subprocess.run([sys.executable, "-B", str(TOOL), *arguments], cwd=self.root,
                                        env=environment, capture_output=True, timeout=20)
                self.assertEqual(result.returncode, code, result.stderr)
                if code in (0, 3):
                    self.assertEqual(result.stderr, b"")
                    self.assertEqual(result.stdout, encode(json.loads(result.stdout)))
                else:
                    self.assertEqual(result.stdout, b"")
                    self.assertEqual(result.stderr, encode(json.loads(result.stderr)))

    def test_binary_stdout_buffer_bypasses_text_encoding(self):
        self.write(recorded())
        binary = _BinaryStandard()
        code, _, err = self.main(["--input", str(self.path)], stdout=binary)
        self.assertEqual(code, 0)
        self.assertEqual(err.getvalue(), "")
        actual = binary.buffer.getvalue()
        self.assertEqual(actual, encode(json.loads(actual)))

    def test_main_none_reads_real_argv_without_raising_system_exit(self):
        self.write()
        with mock.patch.object(sys, "argv", ["capture_readiness.py", "--input", str(self.path)]):
            code, out, err = self.main(None)
        self.assertEqual(code, 3)
        self.assertEqual(json.loads(out.getvalue())["status"], "planned")
        self.assertEqual(err.getvalue(), "")

    def test_exact_argv_container_and_token_types_are_enforced(self):
        class ListSubclass(list): pass
        class StringSubclass(str): pass
        for arguments in ((), "--help", True, 2, b"--help", ListSubclass(["--help"]),
                          [True], [Path("x")], [StringSubclass("--help")]):
            with self.subTest(arguments=repr(arguments)):
                self.assert_error(self.main(arguments), 2, "invalid_argument")

    def test_missing_unknown_abbreviated_and_repeated_options_reject(self):
        self.write()
        for arguments in ([], ["--input"], ["--input", ""], ["--input="],
                          ["--in", str(self.path)], ["--input", str(self.path), "--out", "x"],
                          ["--input", str(self.path), "--unknown"],
                          ["--input", str(self.path), "--input", str(self.path)],
                          ["--input=" + str(self.path), "--input=" + str(self.path)],
                          ["--input", str(self.path), "--output", ""],
                          ["--input", str(self.path), "--output="],
                          ["--input", str(self.path), "--output", "a", "--output", "b"],
                          ["--input", str(self.path), "unexpected"]):
            with self.subTest(arguments=arguments):
                self.assert_error(self.main(arguments), 2, "invalid_argument")
        self.assertEqual(sorted(path.name for path in self.root.iterdir()), ["capture.json"])

    def test_help_has_zero_exit_and_no_input_read(self):
        for option in ("-h", "--help"):
            with self.subTest(option=option), mock.patch.object(readiness.common, "read_json",
                    side_effect=AssertionError("help must not read an input")):
                code, out, err = self.main([option])
                self.assertEqual(code, 0)
                self.assertIn("--input", out.getvalue())
                self.assertIn("--output", out.getvalue())
                self.assertEqual(err.getvalue(), "")

    def test_input_and_manifest_rejection_codes_preserve_every_existing_file(self):
        target = self.root / "existing-report.json"
        target.write_bytes(b"existing independent sentinel")
        for payload, error_code in ((b"not JSON", "input_error"), (b"{}", "invalid_manifest")):
            with self.subTest(error=error_code):
                self.write(payload=payload)
                before = {p.name: p.read_bytes() for p in self.root.iterdir()}
                self.assert_error(self.main(["--input", str(self.path), "--output", str(target)]), 1, error_code)
                self.assertEqual({p.name: p.read_bytes() for p in self.root.iterdir()}, before)

    def test_report_file_equals_stdout_and_is_published_before_stdout(self):
        self.write(recorded("synthetic"))
        destination = self.root / "new report μ.json"
        original_input = self.path.read_bytes()
        class Observer(io.StringIO):
            def write(inner, text):
                self.assertTrue(destination.is_file())
                self.assertEqual(destination.read_bytes(), text.encode("utf-8"))
                return super().write(text)
        code, out, err = self.main(["--input", str(self.path), "--output", str(destination)], stdout=Observer())
        self.assertEqual(code, 0)
        self.assertEqual(err.getvalue(), "")
        self.assertEqual(destination.read_bytes(), out.getvalue().encode("utf-8"))
        self.assertEqual(destination.read_bytes(), encode(json.loads(out.getvalue())))
        self.assertEqual(self.path.read_bytes(), original_input)
        self.assertEqual(sorted(path.name for path in self.root.iterdir()), ["capture.json", "new report μ.json"])

    def test_existing_file_and_input_destination_are_never_replaced(self):
        self.write(recorded())
        target = self.root / "report.json"
        target.write_bytes(b"retained report bytes")
        for destination in (target, self.path):
            with self.subTest(destination=destination.name):
                before = {p.name: p.read_bytes() for p in self.root.iterdir()}
                self.assert_error(self.main(["--input", str(self.path), "--output", str(destination)]), 1, "output_error")
                self.assertEqual({p.name: p.read_bytes() for p in self.root.iterdir()}, before)

    def test_existing_hardlink_to_input_is_preserved(self):
        self.write()
        target = self.root / "hardlink.json"
        try:
            os.link(self.path, target)
        except OSError as error:
            self.skipTest("native hard link unavailable: " + str(error))
        before = self.path.read_bytes()
        self.assert_error(self.main(["--input", str(self.path), "--output", str(target)]), 1, "output_error")
        self.assertEqual(target.read_bytes(), before)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertTrue(os.path.samefile(target, self.path))

    def test_existing_directory_and_dangling_symlink_are_preserved(self):
        self.write()
        directory = self.root / "directory"
        directory.mkdir()
        self.assert_error(self.main(["--input", str(self.path), "--output", str(directory)]), 1, "output_error")
        self.assertTrue(directory.is_dir())
        self.assertFalse(list(directory.iterdir()))
        alias = self.root / "dangling.json"
        try:
            alias.symlink_to("missing-target.json")
        except (OSError, NotImplementedError) as error:
            self.skipTest("native symlink unavailable: " + str(error))
        self.assert_error(self.main(["--input", str(self.path), "--output", str(alias)]), 1, "output_error")
        self.assertTrue(alias.is_symlink())
        self.assertEqual(os.readlink(alias), "missing-target.json")
        self.assertFalse((self.root / "missing-target.json").exists())

    def test_missing_output_parent_is_not_created(self):
        self.write()
        target = self.root / "absent-directory" / "new.json"
        self.assert_error(self.main(["--input", str(self.path), "--output", str(target)]), 1, "output_error")
        self.assertFalse(target.parent.exists())
        self.assertEqual([p.name for p in self.root.iterdir()], ["capture.json"])

    def test_destination_created_during_publication_remains_unchanged(self):
        self.write()
        target = self.root / "raced.json"
        original_link = os.link
        def racing_link(source, destination, *args, **kwargs):
            self.assertEqual(Path(destination), target)
            target.write_bytes(b"other writer wins")
            return original_link(source, destination, *args, **kwargs)
        with mock.patch.object(readiness.common.os, "link", side_effect=racing_link):
            self.assert_error(self.main(["--input", str(self.path), "--output", str(target)]), 1, "output_error")
        self.assertEqual(target.read_bytes(), b"other writer wins")
        self.assertFalse(list(self.root.glob(".capture-json-*")))

    def test_completed_publication_cleanup_failure_is_reported_without_deleting_file(self):
        self.write(recorded("synthetic"))
        target = self.root / "complete.json"
        expected = encode(readiness.inspect_readiness(self.path))
        original_unlink = Path.unlink
        def cleanup_error(path, *args, **kwargs):
            result = original_unlink(path, *args, **kwargs)
            if path.name.startswith(".capture-json-"):
                raise OSError("injected cleanup failure after actual unlink")
            return result
        with mock.patch.object(Path, "unlink", autospec=True, side_effect=cleanup_error):
            report = self.assert_error(self.main(["--input", str(self.path), "--output", str(target)]), 1, "output_error")
        self.assertIn("published and remains complete", report["error"]["message"])
        self.assertIn("cleanup", report["error"]["message"])
        self.assertEqual(target.read_bytes(), expected)
        self.assertFalse(list(self.root.glob(".capture-json-*")))

    def test_primary_and_cleanup_failure_contexts_survive_wrapper(self):
        self.write()
        target = self.root / "unpublished.json"
        original_unlink = Path.unlink
        def cleanup_error(path, *args, **kwargs):
            result = original_unlink(path, *args, **kwargs)
            if path.name.startswith(".capture-json-"):
                raise OSError("independent cleanup failure")
            return result
        with mock.patch.object(readiness.common.os, "link", side_effect=OSError("independent primary failure")), \
             mock.patch.object(Path, "unlink", autospec=True, side_effect=cleanup_error):
            error = self.assert_error(self.main(["--input", str(self.path), "--output", str(target)]), 1, "output_error")
        self.assertIn("independent primary failure", error["error"]["message"])
        self.assertIn("independent cleanup failure", error["error"]["message"])
        self.assertFalse(target.exists())

    def test_stdout_failure_after_publication_keeps_complete_file(self):
        self.write(recorded())
        target = self.root / "published.json"
        expected = encode(readiness.inspect_readiness(self.path))
        class FailedText(io.StringIO):
            def write(inner, text):
                self.assertEqual(target.read_bytes(), expected)
                raise OSError("independent stdout failure")
        result = self.main(["--input", str(self.path), "--output", str(target)], stdout=FailedText())
        error = self.assert_error(result, 1, "stream_error")
        self.assertIn("stdout delivery failed", error["error"]["message"])
        self.assertEqual(target.read_bytes(), expected)

    def test_short_text_write_returns_failure_and_retains_partial_delivery(self):
        self.write()
        code, out, err = self.main(["--input", str(self.path)], stdout=_ShortText())
        self.assertEqual(code, 1)
        self.assertEqual(len(out.getvalue()), 7)
        self.assertEqual(json.loads(err.getvalue())["error"]["code"], "stream_error")
        self.assertIn("incomplete", json.loads(err.getvalue())["error"]["message"])

    def test_short_binary_write_returns_failure_and_retains_partial_bytes(self):
        self.write()
        class ShortBytes(io.BytesIO):
            def write(self, data):
                super().write(data[:11])
                return 11
        output = _BinaryStandard(ShortBytes())
        code, _, err = self.main(["--input", str(self.path)], stdout=output)
        self.assertEqual(code, 1)
        self.assertEqual(len(output.buffer.getvalue()), 11)
        self.assertEqual(json.loads(err.getvalue())["error"]["code"], "stream_error")

    def test_flush_failure_is_not_success_after_complete_stdout_delivery(self):
        self.write()
        class FailedFlush(io.BytesIO):
            def flush(self): raise OSError("injected flush failure")
        output = _BinaryStandard(FailedFlush())
        code, _, err = self.main(["--input", str(self.path)], stdout=output)
        self.assertEqual(code, 1)
        self.assertEqual(output.buffer.getvalue(), encode(json.loads(output.buffer.getvalue())))
        self.assertEqual(json.loads(err.getvalue())["error"]["code"], "stream_error")

    def test_stderr_failure_retains_the_original_nonzero_exit(self):
        class FailedError(io.StringIO):
            def write(self, value): raise OSError("stderr unavailable")
        for arguments, expected in (([], 2), (["--input", str(self.path)], 1)):
            with self.subTest(expected=expected):
                code, out, _ = self.main(arguments, stderr=FailedError())
                self.assertEqual(code, expected)
                self.assertEqual(out.getvalue(), "")

    def test_binary_stderr_uses_utf8_for_unicode_input_errors(self):
        self.path = self.root / "missing Ω.json"
        output, error = io.StringIO(), _BinaryStandard()
        code, _, _ = self.main(["--input", str(self.path)], stdout=output, stderr=error)
        self.assertEqual(code, 1)
        self.assertEqual(output.getvalue(), "")
        payload = error.buffer.getvalue()
        self.assertEqual(payload, encode(json.loads(payload)))
        self.assertIn("Ω".encode("utf-8"), payload)

    def test_help_stream_failure_is_contextual_nonzero(self):
        class FailedHelp(io.StringIO):
            def write(self, text): raise OSError("help unavailable")
        error = self.assert_error(self.main(["--help"], stdout=FailedHelp()), 1, "stream_error")
        self.assertIn("help delivery failed", error["error"]["message"])

    def test_external_cancellation_during_admission_validation_or_output_propagates(self):
        self.write()
        target = self.root / "not-created.json"
        stages = ((readiness.common, "read_json"), (readiness.capture, "validate_capture"),
                  (readiness.common, "write_json_new"))
        for owner, name in stages:
            for interruption in (KeyboardInterrupt("external cancellation"), SystemExit(73)):
                with self.subTest(stage=name, kind=type(interruption).__name__), \
                     mock.patch.object(owner, name, side_effect=interruption):
                    out, err = io.StringIO(), io.StringIO()
                    with redirect_stdout(out), redirect_stderr(err), self.assertRaises(type(interruption)):
                        readiness.main(["--input", str(self.path), "--output", str(target)])
                    self.assertEqual(out.getvalue(), "")
                    self.assertEqual(err.getvalue(), "")
                    self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
