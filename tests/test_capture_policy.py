#!/usr/bin/env python3
"""Independent policy admission and interval-decision acceptance.

Reports are hand-built constant-signal or explicitly labeled structural fixtures.
Expected decisions are literal contract examples and separate binary64 boundary
calculations. No producer metric/evaluation helper supplies an expected verdict.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import compare_capture as subject


POINT_TARGETS = {
    "absolute_dc_bias_fs": "FS",
    "rms_error_fs": "FS",
    "max_abs_error_fs": "FS",
    "normalized_rms_error": "ratio",
}
FREQUENCY_TARGETS = {
    "complex_abs_error_fs": "FS",
    "normalized_complex_error": "ratio",
    "absolute_phase_error_rad": "rad",
}
EVALUATION_KEYS = {
    "schema_version", "metric_contract", "policy_id", "policy_sha256",
    "evidence_class", "evaluation_role", "preregistration", "numerical_verdict",
    "criteria", "comparison", "physical_fidelity",
}
CRITERION_KEYS = {
    "criterion_id", "target", "observed", "upper_bound", "uncertainty",
    "interval", "numerical_verdict", "reason", "physical_fidelity",
}


def known(value, unit):
    return {"value": value, "unit": unit, "undefined_reason": None}


def absent(reason, unit):
    return {"value": None, "unit": unit, "undefined_reason": reason}


def constant_report(reference=1.0, candidate=1.25, *, channels=1, frames=4,
                    frequencies=(0,), rate=8, floor=1e-12):
    """Hand report for nonnegative constants; non-DC bins require one frame.

The one-frame variant has equal coefficients at every supplied frequency. The
ordinary variant uses only DC, so no numerical producer or DFT oracle is needed.
"""
    assert reference >= 0 and candidate >= 0
    assert frames == 1 or all(frequency == 0 for frequency in frequencies)
    error = abs(candidate - reference)
    reference_masked = reference <= floor
    candidate_masked = candidate <= floor
    normalized_reason = "reference_at_or_below_floor" if reference_masked else None
    db_reason = ("reference_at_or_below_floor" if reference_masked else
                 "zero_error" if error == 0 else
                 "error_at_or_below_floor" if error <= floor else None)
    phase_reason = ("both_at_or_below_floor" if reference_masked and candidate_masked else
                    "reference_at_or_below_floor" if reference_masked else
                    "candidate_at_or_below_floor" if candidate_masked else None)
    point = {
        "reference_dc_fs": known(reference, "FS"),
        "candidate_dc_fs": known(candidate, "FS"),
        "dc_bias_fs": known(candidate - reference, "FS"),
        "absolute_dc_bias_fs": known(error, "FS"),
        "reference_rms_fs": known(reference, "FS"),
        "candidate_rms_fs": known(candidate, "FS"),
        "rms_error_fs": known(error, "FS"),
        "max_abs_error_fs": known(error, "FS"),
        "normalized_rms_error": (absent(normalized_reason, "ratio") if normalized_reason
                                 else known(error / reference, "ratio")),
        "signal_to_error_db": (absent(db_reason, "dB") if db_reason else
                               known(20 * math.log10(reference / error), "dB")),
    }
    spectral = {
        "reference_magnitude_fs": known(reference, "FS"),
        "candidate_magnitude_fs": known(candidate, "FS"),
        "complex_abs_error_fs": known(error, "FS"),
        "normalized_complex_error": (absent(normalized_reason, "ratio") if normalized_reason
                                     else known(error / reference, "ratio")),
        "reference_phase_rad": (absent("reference_at_or_below_floor", "rad")
                                if reference_masked else known(0.0, "rad")),
        "candidate_phase_rad": (absent("candidate_at_or_below_floor", "rad")
                                if candidate_masked else known(0.0, "rad")),
        "phase_error_rad": (absent(phase_reason, "rad") if phase_reason else known(0.0, "rad")),
        "absolute_phase_error_rad": (absent(phase_reason, "rad") if phase_reason else known(0.0, "rad")),
    }
    rows = []
    for channel in range(channels):
        bins = [{
            "frequency_hz": frequency,
            "reference_coefficient": {"real_fs": reference, "imag_fs": 0.0},
            "candidate_coefficient": {"real_fs": candidate, "imag_fs": 0.0},
            "metrics": copy.deepcopy(spectral),
            "phase_mask": phase_reason or "none",
        } for frequency in frequencies]
        rows.append({"reference_channel_index": channel, "candidate_channel_index": channel,
                     "metrics": copy.deepcopy(point), "frequencies": bins})
    return {
        "schema_version": 1, "metric_contract": "capture-comparison-v1",
        "sample_rate_hz": rate, "channel_count": channels, "frame_count": frames,
        "analysis": {"pairing": "index", "frame_start": 0, "frame_stop": frames,
                     "window": "rectangular", "floor_fs": floor,
                     "frequencies_hz": list(frequencies),
                     "dft_normalization": "weighted_mean", "transform": "none"},
        "channels": rows, "physical_fidelity": "not_established",
    }


def criterion(ident="rms-limit", metric="rms_error_fs", *, channel=0,
              frequency=None, bound=0.375, margin=0.125,
              basis="synthetic_numerical"):
    unit = (POINT_TARGETS if frequency is None else FREQUENCY_TARGETS)[metric]
    uncertainty = {
        "margin": margin, "unit": unit, "basis": basis,
        "evidence": "Independent literal binary64 interval fixture; no physical uncertainty claim.",
        "unknown_reason": None,
    }
    if basis == "unknown":
        uncertainty.update(margin=None, evidence=None,
                           unknown_reason="No applicable decision-margin evidence was supplied.")
    return {
        "criterion_id": ident,
        "target": {"channel_index": channel, "frequency_hz": frequency, "metric": metric},
        "upper_bound": bound, "unit": unit,
        "rationale": "Predeclared independent interval acceptance fixture.",
        "uncertainty": uncertainty,
    }


def policy(report=None, *, criteria=None, evidence_class="synthetic_numerical_fixture",
           role="validation"):
    if report is None:
        report = constant_report()
    analysis = {key: report[key] for key in ("sample_rate_hz", "channel_count", "frame_count")}
    analysis.update({key: copy.deepcopy(report["analysis"][key])
                     for key in ("window", "floor_fs", "frequencies_hz")})
    return {
        "schema_version": 1, "metric_contract": "capture-comparison-v1",
        "policy_id": "independent-policy-v1", "evidence_class": evidence_class,
        "evaluation_role": role,
        "freeze_evidence": {"value": None,
                            "unknown_reason": "No independent chronology was established by this fixture."},
        "analysis": analysis, "criteria": [criterion()] if criteria is None else criteria,
    }


def wire(value, *, pretty=False, ascii_only=False):
    options = {"sort_keys": False, "ensure_ascii": ascii_only, "allow_nan": False}
    if pretty:
        options["indent"] = 2
    else:
        options["separators"] = (",", ":")
    return (json.dumps(value, **options) + "\n").encode("utf-8")


def target_metric(report, target):
    """Literal report lookup for assertions, not a policy-decision algorithm."""
    channel = report["channels"][target["channel_index"]]
    if target["frequency_hz"] is None:
        return channel["metrics"][target["metric"]]
    row = next(item for item in channel["frequencies"]
               if item["frequency_hz"] == target["frequency_hz"])
    return row["metrics"][target["metric"]]


class PolicyCase(unittest.TestCase):
    def reject(self, value, *, report=None, raw=False):
        payload = value if raw else wire(value)
        with self.assertRaises(subject.ComparisonError):
            subject.parse_policy(payload)
        with self.assertRaises(subject.ComparisonError):
            subject.evaluate_policy(constant_report() if report is None else report, payload)

    def evaluate(self, report=None, value=None):
        report = constant_report() if report is None else report
        value = policy(report) if value is None else value
        payload = wire(value)
        result = subject.evaluate_policy(report, payload)
        self.assertEqual(set(result), EVALUATION_KEYS)
        self.assertIs(type(result["schema_version"]), int)
        self.assertEqual(result["schema_version"], 1)
        self.assertEqual(result["metric_contract"], "capture-comparison-v1")
        self.assertEqual(result["policy_id"], value["policy_id"])
        self.assertEqual(result["policy_sha256"], hashlib.sha256(payload).hexdigest())
        self.assertEqual(result["evidence_class"], value["evidence_class"])
        self.assertEqual(result["evaluation_role"], value["evaluation_role"])
        self.assertEqual(result["comparison"], report)
        self.assertEqual(result["preregistration"], "not_established")
        self.assertEqual(result["physical_fidelity"], "not_established")
        self.assertEqual(len(result["criteria"]), len(value["criteria"]))
        for actual, expected in zip(result["criteria"], value["criteria"]):
            self.assertEqual(set(actual), CRITERION_KEYS)
            for field in ("criterion_id", "target", "upper_bound", "uncertainty"):
                self.assertEqual(actual[field], expected[field])
            self.assertEqual(actual["observed"], target_metric(report, expected["target"]))
            self.assertEqual(set(actual["interval"]), {"lower", "upper", "unit", "undefined_reason"})
            self.assertEqual(actual["interval"]["unit"], expected["unit"])
            self.assertEqual(actual["physical_fidelity"], "not_established")
        json.dumps(result, allow_nan=False)
        return result


class PolicyParsingAcceptance(PolicyCase):
    def test_parse_returns_exact_value_and_fresh_nested_containers(self):
        value = policy()
        payload = wire(value)
        before = bytes(payload)
        first = subject.parse_policy(payload)
        second = subject.parse_policy(payload)
        self.assertEqual(first, value)
        self.assertEqual(second, value)
        first["analysis"]["frequencies_hz"].append(2)
        first["criteria"][0]["uncertainty"]["evidence"] = "changed caller copy"
        self.assertEqual(second, value)
        self.assertEqual(payload, before)

    def test_parse_has_no_comparison_or_sample_dependency(self):
        with mock.patch.object(subject, "validate_comparison_report", side_effect=AssertionError("unexpected report")), \
                mock.patch.object(subject, "compare_signals", side_effect=AssertionError("unexpected samples")):
            self.assertEqual(subject.parse_policy(wire(policy())), policy())

    def test_policy_requires_exact_bytes(self):
        class BytesChild(bytes):
            pass
        payload = wire(policy())
        for bad in (payload.decode(), bytearray(payload), memoryview(payload), BytesChild(payload), None, {}, 1):
            with self.subTest(kind=type(bad).__name__):
                self.reject(bad, raw=True)

    def test_json_lexical_encoding_and_root_rejections(self):
        payload = wire(policy())
        bad_values = [b"", b" ", b"null", b"[]", b"true", b"{}", payload + b"{}",
                      b"\xef\xbb\xbf" + payload, b"\xff", b"{", payload[:-2], b"// comment\n" + payload]
        for bad in bad_values:
            with self.subTest(payload=bad[:28]):
                self.reject(bad, raw=True)

    def test_duplicate_json_keys_rejected_at_every_policy_object_level(self):
        original = wire(policy())
        tokens = [b'"schema_version":1', b'"value":null', b'"sample_rate_hz":8',
                  b'"criterion_id":"rms-limit"', b'"channel_index":0', b'"margin":0.125']
        for token in tokens:
            with self.subTest(token=token):
                self.assertIn(token, original)
                self.reject(original.replace(token, token + b"," + token, 1), raw=True)

    def test_nonfinite_overflow_and_numeric_token_length(self):
        payload = wire(policy())
        for token in (b"NaN", b"Infinity", b"-Infinity", b"1e999", b"9" * 65):
            with self.subTest(token=token):
                self.reject(payload.replace(b'"upper_bound":0.375', b'"upper_bound":' + token), raw=True)
        token64 = b"0." + b"0" * 61 + b"1"
        self.assertEqual(len(token64), 64)
        accepted = payload.replace(b'"upper_bound":0.375', b'"upper_bound":' + token64)
        self.assertEqual(subject.parse_policy(accepted)["criteria"][0]["upper_bound"], 1e-62)
        self.reject(payload.replace(b'"upper_bound":0.375', b'"upper_bound":' + b"0." + b"0" * 62 + b"1"), raw=True)

    def test_exact_byte_limit_includes_whitespace(self):
        payload = wire(policy())
        at_limit = payload + b" " * (65536 - len(payload))
        self.assertEqual(len(at_limit), 65536)
        self.assertEqual(subject.parse_policy(at_limit), policy())
        self.assertEqual(subject.evaluate_policy(constant_report(), at_limit)["policy_sha256"],
                         hashlib.sha256(at_limit).hexdigest())
        self.reject(at_limit + b" ", raw=True)

    def test_generic_deep_and_oversized_values_are_bounded_rejections(self):
        for extra in ([0] * 4097, {f"x{i}": 0 for i in range(4097)}):
            value = policy()
            value["unexpected"] = extra
            self.reject(value)
        value = policy()
        nested = 0
        for _ in range(10):
            nested = [nested]
        value["criteria"][0]["rationale"] = nested
        self.reject(value)

    def test_required_and_unknown_keys_at_every_object_level(self):
        paths = [(), ("freeze_evidence",), ("analysis",), ("criteria", 0),
                 ("criteria", 0, "target"), ("criteria", 0, "uncertainty")]
        for path in paths:
            for mutation in ("missing", "unknown"):
                with self.subTest(path=path, mutation=mutation):
                    value = policy()
                    obj = value
                    for key in path:
                        obj = obj[key]
                    if mutation == "missing":
                        obj.pop(next(iter(obj)))
                    else:
                        obj["unexpected"] = 0
                    self.reject(value)

    def test_every_nested_policy_object_requires_an_object(self):
        paths = [("freeze_evidence",), ("analysis",), ("criteria", 0),
                 ("criteria", 0, "target"), ("criteria", 0, "uncertainty")]
        for path in paths:
            for bad in (None, True, 1, "object", [], [0]):
                with self.subTest(path=path, value=bad):
                    value = policy()
                    target = value
                    for key in path[:-1]:
                        target = target[key]
                    target[path[-1]] = bad
                    self.reject(value)

    def test_schema_identity_evidence_class_and_role_are_exact(self):
        for field, values in {
            "schema_version": [True, 1.0, "1", 0, 2, None],
            "metric_contract": [None, "capture-comparison-v2", True, []],
            "evidence_class": [None, "hardware", "synthetic", True, []],
            "evaluation_role": [None, "held_out", "final", "FINAL_TEST", True, []],
        }.items():
            for bad in values:
                with self.subTest(field=field, value=bad):
                    value = policy()
                    value[field] = bad
                    self.reject(value)

    def test_ids_are_exact_portable_and_length_bounded(self):
        for field in ("policy_id", "criterion_id"):
            def assign(value, ident):
                (value if field == "policy_id" else value["criteria"][0])[field] = ident
            value = policy()
            assign(value, "a" + "0_-" * 21)
            self.assertEqual(len((value if field == "policy_id" else value["criteria"][0])[field]), 64)
            self.assertEqual(subject.parse_policy(wire(value)), value)
            for bad in ("", "A", "1abc", "a.b", "a/b", "a b", "é", "a\n", "a" * 65, True, 1, None):
                with self.subTest(field=field, value=bad):
                    value = policy()
                    assign(value, bad)
                    self.reject(value)

    def test_text_is_unicode_nonblank_control_free_and_bounded(self):
        paths = [
            ("criteria", 0, "rationale"),
            ("criteria", 0, "uncertainty", "evidence"),
            ("criteria", 0, "uncertainty", "unknown_reason"),
            ("freeze_evidence", "unknown_reason"),
            ("freeze_evidence", "value"),
        ]
        def fixture_for_path(path):
            value = policy()
            if path == ("freeze_evidence", "value"):
                value["freeze_evidence"]["unknown_reason"] = None
            elif path == ("criteria", 0, "uncertainty", "unknown_reason"):
                value["criteria"][0] = criterion(basis="unknown")
            return value
        for path in paths:
            for bad in ("", "   ", "a\x00b", "a\x1fb", "a\x7fb", "a\x85b", "a\x9fb", "a" * 2049, None, 7, []):
                with self.subTest(path=path, value=repr(bad)[:30]):
                    value = fixture_for_path(path)
                    target = value
                    for key in path[:-1]:
                        target = target[key]
                    target[path[-1]] = bad
                    self.reject(value)
            value = fixture_for_path(path)
            target = value
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = "Ω" * 2048
            self.assertEqual(subject.parse_policy(wire(value)), value)
        value = policy()
        value["criteria"][0]["rationale"] = "Independent Ω fixture 🎼"
        self.assertEqual(subject.parse_policy(wire(value)), value)
        value["criteria"][0]["rationale"] = "bad\ud800surrogate"
        self.reject(wire(value, ascii_only=True), raw=True)

    def test_freeze_known_and_unknown_branches_are_exclusive(self):
        for branch in (
                {"value": "retained-study/revision-1", "unknown_reason": None},
                {"value": None, "unknown_reason": "Chronology has not been independently verified."}):
            value = policy()
            value["freeze_evidence"] = branch
            self.assertEqual(subject.parse_policy(wire(value)), value)
        for branch in ({"value": None, "unknown_reason": None},
                       {"value": "record", "unknown_reason": "also unknown"},
                       {"value": " ", "unknown_reason": None},
                       {"value": 42, "unknown_reason": None}):
            value = policy()
            value["freeze_evidence"] = branch
            self.reject(value)

    def test_policy_geometry_types_and_scalar_boundaries(self):
        cases = {
            "sample_rate_hz": [True, 8.0, 0, 768001, "8", None],
            "channel_count": [True, 1.0, 0, 17, "1", None],
            "frame_count": [True, 4.0, 0, 262145, "4", None],
            "floor_fs": [True, 0, 1e-13, 1000001, "0.1", None],
            "window": [None, "hann", "HANN_SYMMETRIC", True, []],
        }
        for field, values in cases.items():
            for bad in values:
                with self.subTest(field=field, value=bad):
                    value = policy()
                    value["analysis"][field] = bad
                    self.reject(value)
        for rate in (1, 768000):
            for floor in (1e-12, 1000000):
                value = policy()
                value["analysis"].update(sample_rate_hz=rate, floor_fs=floor)
                self.assertEqual(subject.parse_policy(wire(value)), value)

    def test_policy_frequency_types_order_count_and_nyquist(self):
        for bad in (None, "0", {}, [True], [-1], [5], [1, 0], [0, 0.0], list(range(65))):
            with self.subTest(frequencies=bad):
                value = policy()
                value["analysis"]["frequencies_hz"] = bad
                self.reject(value)
        for frequencies in ([], [0, 4], [0.0, 4.0]):
            value = policy()
            value["analysis"]["frequencies_hz"] = frequencies
            self.assertEqual(subject.parse_policy(wire(value)), value)

    def test_policy_hann_minimum_and_work_preflight(self):
        for frames in (1, 2):
            value = policy()
            value["analysis"].update(window="hann_symmetric", frame_count=frames)
            self.reject(value)
        value = policy()
        value["analysis"].update(window="hann_symmetric", frame_count=3)
        self.assertEqual(subject.parse_policy(wire(value)), value)
        value = policy()
        value["analysis"].update(sample_rate_hz=128, channel_count=2,
                                 frame_count=262144, frequencies_hz=list(range(32)))
        self.assertEqual(subject.parse_policy(wire(value)), value)
        value["analysis"]["frequencies_hz"].append(32)
        self.reject(value)
        value = policy()
        value["analysis"].update(channel_count=16, frame_count=262144, frequencies_hz=[])
        self.assertEqual(subject.parse_policy(wire(value)), value)

    def test_criterion_count_limits_and_all_256_unique_targets(self):
        report = constant_report(channels=16, frames=1, frequencies=range(16), rate=128)
        entries = []
        for channel in range(16):
            for frequency in range(16):
                row = criterion("a" + format(len(entries), "x"), "complex_abs_error_fs",
                                channel=channel, frequency=frequency, bound=1, margin=0)
                row["rationale"] = "x"
                row["uncertainty"]["evidence"] = "x"
                entries.append(row)
        value = policy(report, criteria=entries)
        value["policy_id"] = "a"
        value["freeze_evidence"]["unknown_reason"] = "x"
        self.assertLessEqual(len(wire(value)), 65536)
        self.assertEqual(subject.parse_policy(wire(value)), value)
        result = self.evaluate(report, value)
        self.assertEqual(len(result["criteria"]), 256)
        self.assertEqual(result["numerical_verdict"], "pass")
        self.reject(policy(report, criteria=[]), report=report)
        excessive = copy.deepcopy(value)
        extra = criterion("overflow", "absolute_phase_error_rad", frequency=0, bound=1, margin=0)
        extra["rationale"] = "x"
        extra["uncertainty"]["evidence"] = "x"
        excessive["criteria"].append(extra)
        self.assertLessEqual(len(wire(excessive)), 65536)
        self.reject(excessive, report=report)
        for bad in ({}, None, "criteria", True):
            value = policy()
            value["criteria"] = bad
            self.reject(value)

    def test_criterion_id_and_target_identity_are_independently_unique(self):
        value = policy(criteria=[criterion(), criterion("different", "max_abs_error_fs")])
        self.assertEqual(subject.parse_policy(wire(value)), value)
        value["criteria"][1]["criterion_id"] = value["criteria"][0]["criterion_id"]
        self.reject(value)
        value = policy(criteria=[criterion(), criterion("other")])
        self.reject(value)
        value = policy(criteria=[criterion("a", "complex_abs_error_fs", frequency=0),
                                 criterion("b", "complex_abs_error_fs", frequency=0.0)])
        self.reject(value)

    def test_only_seven_typed_targets_are_admitted(self):
        entries = [criterion(f"point-{index}", metric, bound=1, margin=0)
                   for index, metric in enumerate(POINT_TARGETS)]
        entries += [criterion(f"frequency-{index}", metric, frequency=0, bound=1, margin=0)
                    for index, metric in enumerate(FREQUENCY_TARGETS)]
        value = policy(criteria=entries)
        self.assertEqual(subject.parse_policy(wire(value)), value)
        self.assertEqual(self.evaluate(value=value)["numerical_verdict"], "pass")
        rejected = ["reference_dc_fs", "candidate_dc_fs", "dc_bias_fs", "reference_rms_fs",
                    "candidate_rms_fs", "signal_to_error_db", "rms_error_fs.value",
                    "__import__('os')", "*", "/channels/0/metrics", "", None, True, []]
        for metric in rejected:
            with self.subTest(metric=metric):
                value = policy()
                value["criteria"][0]["target"]["metric"] = metric
                self.reject(value)
        for metric in ("reference_magnitude_fs", "candidate_magnitude_fs", "reference_phase_rad",
                       "candidate_phase_rad", "phase_error_rad", "rms_error_fs"):
            value = policy()
            value["criteria"][0]["target"].update(metric=metric, frequency_hz=0)
            self.reject(value)
        for metric in FREQUENCY_TARGETS:
            value = policy()
            value["criteria"][0]["target"]["metric"] = metric
            self.reject(value)

    def test_target_channels_and_frequencies_are_exact_and_present(self):
        for field, values in {"channel_index": [True, 0.0, -1, 1, None, "0"],
                              "frequency_hz": [True, -1, 1, "0", [], {}]}.items():
            for bad in values:
                with self.subTest(field=field, value=bad):
                    value = policy(criteria=[criterion("dc", "complex_abs_error_fs", frequency=0)])
                    value["criteria"][0]["target"][field] = bad
                    self.reject(value)
        value = policy(criteria=[criterion("dc", "complex_abs_error_fs", frequency=0.0)])
        self.assertEqual(subject.parse_policy(wire(value)), value)
        self.assertEqual(self.evaluate(value=value)["numerical_verdict"], "pass")

    def test_units_upper_bounds_and_margin_numbers_are_exact(self):
        for field in ("unit",):
            for bad in ("fs", "V", "ratio", None, True, []):
                value = policy()
                value["criteria"][0][field] = bad
                self.reject(value)
                value = policy()
                value["criteria"][0]["uncertainty"][field] = bad
                self.reject(value)
        for field, values in {"upper_bound": [True, -1e-300, 1000001, "1", None, []],
                              "margin": [True, -1e-300, 1000001, "0", [], {}]}.items():
            for bad in values:
                value = policy()
                target = value["criteria"][0]
                if field == "margin":
                    target = target["uncertainty"]
                target[field] = bad
                self.reject(value)
        for bound in (0, 1000000):
            for margin in (0, 1000000):
                value = policy(criteria=[criterion(bound=bound, margin=margin)])
                self.assertEqual(subject.parse_policy(wire(value)), value)

    def test_unknown_uncertainty_has_only_its_explicit_shape(self):
        value = policy(criteria=[criterion(basis="unknown")])
        self.assertEqual(subject.parse_policy(wire(value)), value)
        for field, bad in (("margin", 0), ("evidence", "claimed"),
                           ("unknown_reason", None), ("unknown_reason", " ")):
            invalid = copy.deepcopy(value)
            invalid["criteria"][0]["uncertainty"][field] = bad
            self.reject(invalid)

    def test_declared_margin_is_positive_and_requires_evidence(self):
        for evidence_class in ("digital_comparison", "synthetic_numerical_fixture"):
            value = policy(criteria=[criterion(basis="declared_margin", margin=0.125)],
                           evidence_class=evidence_class)
            self.assertEqual(subject.parse_policy(wire(value)), value)
            for field, bad in (("margin", 0), ("margin", None), ("evidence", None),
                               ("evidence", " "), ("unknown_reason", "also unknown")):
                invalid = copy.deepcopy(value)
                invalid["criteria"][0]["uncertainty"][field] = bad
                self.reject(invalid)

    def test_synthetic_margin_cannot_authorize_digital_zero_uncertainty(self):
        value = policy(criteria=[criterion(margin=0)])
        self.assertEqual(subject.parse_policy(wire(value)), value)
        value["evidence_class"] = "digital_comparison"
        self.reject(value)
        value["criteria"][0]["uncertainty"]["margin"] = 0.125
        self.reject(value)
        for bad in ("none", "standard_uncertainty", None, True, []):
            value = policy()
            value["criteria"][0]["uncertainty"]["basis"] = bad
            self.reject(value)


class PolicyDecisionAcceptance(PolicyCase):
    def test_four_literal_interval_decisions_and_exact_report_shape(self):
        # The first and fourth cases deliberately touch opposite interval ends.
        cases = [
            (0.25, 0.125, 0.375, 0.125, 0.375, "pass", "within_upper_bound"),
            (0.5, 0.125, 0.25, 0.375, 0.625, "fail", "above_upper_bound"),
            (0.25, 0.125, 0.25, 0.125, 0.375, "inconclusive", "interval_overlaps_upper_bound"),
            (0.375, 0.125, 0.25, 0.25, 0.5, "inconclusive", "interval_overlaps_upper_bound"),
        ]
        for observed, margin, limit, lower, upper, verdict, reason in cases:
            with self.subTest(observed=observed, margin=margin, limit=limit):
                report = constant_report(0, observed)
                value = policy(report, criteria=[criterion(bound=limit, margin=margin)])
                result = self.evaluate(report, value)
                row = result["criteria"][0]
                self.assertEqual(row["interval"], {"lower": lower, "upper": upper,
                                                   "unit": "FS", "undefined_reason": None})
                self.assertEqual(row["numerical_verdict"], verdict)
                self.assertEqual(row["reason"], reason)
                self.assertEqual(result["numerical_verdict"], verdict)

    def test_synthetic_exact_zero_pass_and_unknown_zero_remains_inconclusive(self):
        report = constant_report(0, 0)
        result = self.evaluate(report, policy(report, criteria=[criterion(bound=0, margin=0)]))
        self.assertEqual(result["numerical_verdict"], "pass")
        self.assertEqual(result["criteria"][0]["interval"],
                         {"lower": 0, "upper": 0, "unit": "FS", "undefined_reason": None})
        value = policy(report, criteria=[criterion(bound=0, basis="unknown")],
                       evidence_class="digital_comparison")
        result = self.evaluate(report, value)
        self.assertEqual(result["numerical_verdict"], "inconclusive")
        self.assertEqual(result["criteria"][0]["reason"], "uncertainty_unknown")
        self.assertEqual(result["criteria"][0]["interval"],
                         {"lower": None, "upper": None, "unit": "FS", "undefined_reason": "uncertainty_unknown"})

    def test_interval_lower_is_clamped_only_at_zero(self):
        report = constant_report(0, 0.125)
        result = self.evaluate(report, policy(report, criteria=[criterion(bound=0.5, margin=0.25)]))
        self.assertEqual(result["criteria"][0]["interval"],
                         {"lower": 0, "upper": 0.375, "unit": "FS", "undefined_reason": None})
        self.assertEqual(result["numerical_verdict"], "pass")

    def test_adjacent_binary64_boundary_has_no_hidden_epsilon_or_rounding(self):
        limit = 0.25
        for observed, verdict in ((math.nextafter(limit, -math.inf), "pass"),
                                  (limit, "pass"), (math.nextafter(limit, math.inf), "fail")):
            report = constant_report(0, observed)
            result = self.evaluate(report, policy(report, criteria=[criterion(bound=limit, margin=0)]))
            self.assertEqual(result["numerical_verdict"], verdict)
            self.assertEqual(result["criteria"][0]["interval"]["upper"], observed)
        center = math.nextafter(0.375, math.inf)
        report = constant_report(0, center)
        result = self.evaluate(report, policy(report, criteria=[criterion(bound=0.25, margin=0.125)]))
        self.assertGreater(result["criteria"][0]["interval"]["lower"], 0.25)
        self.assertEqual(result["numerical_verdict"], "fail")

    def test_widening_margin_never_turns_failure_or_overlap_into_pass(self):
        for observed in (0.25, 0.375, 0.5):
            verdicts = []
            for margin in (0, 0.125, 0.25, 0.5, 1):
                report = constant_report(0, observed)
                result = self.evaluate(report, policy(report, criteria=[criterion(bound=0.25, margin=margin)]))
                verdicts.append(result["numerical_verdict"])
            first_nonpass = next((i for i, verdict in enumerate(verdicts) if verdict != "pass"), len(verdicts))
            self.assertNotIn("pass", verdicts[first_nonpass:])
        self.assertEqual(verdicts, ["fail", "fail", "inconclusive", "inconclusive", "inconclusive"])

    def test_missing_metric_precedes_unknown_margin_and_retains_original_reasons(self):
        report = constant_report(0, 0.25)
        for metric, frequency, unit in (("normalized_rms_error", None, "ratio"),
                                         ("normalized_complex_error", 0, "ratio"),
                                         ("absolute_phase_error_rad", 0, "rad")):
            value = policy(report, criteria=[criterion("masked", metric, frequency=frequency,
                                                       basis="unknown")])
            result = self.evaluate(report, value)
            row = result["criteria"][0]
            self.assertEqual(row["numerical_verdict"], "inconclusive")
            self.assertEqual(row["reason"], "metric_undefined")
            self.assertEqual(row["interval"], {"lower": None, "upper": None,
                                               "unit": unit, "undefined_reason": "metric_undefined"})
            self.assertIsNone(row["observed"]["value"])
            self.assertEqual(row["observed"]["undefined_reason"], "reference_at_or_below_floor")
            self.assertEqual(row["uncertainty"]["unknown_reason"],
                             value["criteria"][0]["uncertainty"]["unknown_reason"])

    def test_both_silent_and_candidate_silent_phase_reasons_remain_present(self):
        for reference, candidate, reason in ((0, 0, "both_at_or_below_floor"),
                                              (1, 0, "candidate_at_or_below_floor")):
            report = constant_report(reference, candidate)
            value = policy(report, criteria=[criterion("phase", "absolute_phase_error_rad", frequency=0)])
            result = self.evaluate(report, value)
            row = result["criteria"][0]
            self.assertEqual(row["reason"], "metric_undefined")
            self.assertEqual(row["observed"]["undefined_reason"], reason)
            self.assertEqual(result["comparison"]["channels"][0]["frequencies"][0]["phase_mask"], reason)

    def test_fail_precedence_and_all_criteria_order_are_retained(self):
        report = constant_report(0, 0.5)
        entries = [
            criterion("first-fail", "max_abs_error_fs", bound=0.25, margin=0.125),
            criterion("then-masked", "normalized_rms_error", bound=1, basis="unknown"),
            criterion("then-pass", "rms_error_fs", bound=0.625, margin=0.125),
            criterion("then-unknown", "absolute_dc_bias_fs", bound=1, basis="unknown"),
        ]
        value = policy(report, criteria=entries)
        result = self.evaluate(report, value)
        self.assertEqual(result["numerical_verdict"], "fail")
        self.assertEqual([row["criterion_id"] for row in result["criteria"]],
                         [row["criterion_id"] for row in entries])
        self.assertEqual([row["numerical_verdict"] for row in result["criteria"]],
                         ["fail", "inconclusive", "pass", "inconclusive"])
        value["criteria"].reverse()
        reversed_result = self.evaluate(report, value)
        self.assertEqual(reversed_result["numerical_verdict"], "fail")
        self.assertEqual([row["criterion_id"] for row in reversed_result["criteria"]],
                         [row["criterion_id"] for row in value["criteria"]])

    def test_no_aggregate_average_hides_a_failing_channel(self):
        report = constant_report(channels=2)
        report["channels"][1] = constant_report(0, 0.5)["channels"][0]
        report["channels"][1].update(reference_channel_index=1, candidate_channel_index=1)
        value = policy(report, criteria=[criterion("channel-one-pass", channel=0),
                                         criterion("channel-two-fail", channel=1, bound=0.25, margin=0.125)])
        result = self.evaluate(report, value)
        self.assertEqual([row["numerical_verdict"] for row in result["criteria"]], ["pass", "fail"])
        self.assertEqual(result["numerical_verdict"], "fail")

    def test_inconclusive_dominates_other_passes_without_failure(self):
        value = policy(criteria=[criterion(), criterion("unknown", "max_abs_error_fs", basis="unknown")])
        result = self.evaluate(value=value)
        self.assertEqual([row["numerical_verdict"] for row in result["criteria"]], ["pass", "inconclusive"])
        self.assertEqual(result["numerical_verdict"], "inconclusive")

    def test_policy_hash_binds_exact_whitespace_unicode_and_numeric_spelling(self):
        value = policy()
        value["criteria"][0]["rationale"] = "Independent Ω fixture"
        payloads = [wire(value), wire(value, pretty=True), wire(value, ascii_only=True),
                    wire(value).replace(b'"schema_version":1', b'"schema_version":1 '),
                    wire(value).replace(b'"upper_bound":0.375', b'"upper_bound":3.75e-1')]
        self.assertEqual(len(set(payloads)), len(payloads))
        results = [subject.evaluate_policy(constant_report(), payload) for payload in payloads]
        self.assertEqual(len({item["policy_sha256"] for item in results}), len(payloads))
        for payload, result in zip(payloads, results):
            self.assertEqual(result["policy_sha256"], hashlib.sha256(payload).hexdigest())
            self.assertEqual(result["numerical_verdict"], "pass")
        content = [{key: value for key, value in result.items() if key != "policy_sha256"} for result in results]
        self.assertTrue(all(item == content[0] for item in content))

    def test_known_freeze_and_all_roles_never_establish_preregistration(self):
        for role in ("fit", "validation", "final_test", "unassigned"):
            for freeze in ({"value": "retained-freeze/revision-a", "unknown_reason": None},
                           {"value": None, "unknown_reason": "No verified chronology exists."}):
                value = policy(role=role)
                value["freeze_evidence"] = freeze
                result = self.evaluate(value=value)
                self.assertEqual(result["evaluation_role"], role)
                self.assertEqual(result["numerical_verdict"], "pass")
                self.assertEqual(result["preregistration"], "not_established")

    def test_every_policy_analysis_field_must_match_comparison(self):
        mismatches = {"sample_rate_hz": 16, "channel_count": 2, "frame_count": 5,
                      "window": "hann_symmetric", "floor_fs": 1e-10, "frequencies_hz": [0, 1]}
        for field, changed in mismatches.items():
            with self.subTest(field=field):
                value = policy()
                value["analysis"][field] = changed
                self.assertEqual(subject.parse_policy(wire(value)), value)
                with self.assertRaises(subject.ComparisonError):
                    subject.evaluate_policy(constant_report(), wire(value))

    def test_valid_numeric_frequency_spellings_match_without_nearest_bin_search(self):
        value = policy(criteria=[criterion("dc", "complex_abs_error_fs", frequency=0.0)])
        value["analysis"]["frequencies_hz"] = [0.0]
        self.assertEqual(self.evaluate(value=value)["numerical_verdict"], "pass")
        value["analysis"]["frequencies_hz"] = [math.nextafter(0.0, 1.0)]
        value["criteria"][0]["target"]["frequency_hz"] = math.nextafter(0.0, 1.0)
        with self.assertRaises(subject.ComparisonError):
            subject.evaluate_policy(constant_report(), wire(value))

    def test_untargeted_metrics_and_complete_comparison_are_retained(self):
        report = constant_report(frames=1, frequencies=(0, 1, 4))
        value = policy(report, criteria=[criterion(bound=1, margin=0)])
        result = self.evaluate(report, value)
        self.assertEqual(result["comparison"], report)
        self.assertEqual(len(result["comparison"]["channels"][0]["metrics"]), 10)
        self.assertEqual([row["frequency_hz"] for row in result["comparison"]["channels"][0]["frequencies"]], [0, 1, 4])
        self.assertTrue(all(len(row["metrics"]) == 8 for row in result["comparison"]["channels"][0]["frequencies"]))

    def test_valid_near_floor_large_ratio_is_a_failure_not_an_input_rejection(self):
        reference = math.nextafter(1e-12, math.inf)
        report = constant_report(reference, 1e6)
        value = policy(report, criteria=[criterion("relative", "normalized_rms_error",
                                                    bound=1e6, margin=1, basis="declared_margin")],
                       evidence_class="digital_comparison")
        result = self.evaluate(report, value)
        row = result["criteria"][0]
        expected = (1e6 - reference) / reference
        self.assertEqual(row["observed"]["value"], expected)
        self.assertGreater(expected, 1e17)
        self.assertEqual(row["numerical_verdict"], "fail")
        self.assertEqual(row["interval"]["upper"], expected + 1)

    def test_interval_composition_can_exceed_comparison_numeric_bound(self):
        # This is an admitted structural report fixture, not a claimed audio
        # realization of a 2e18 FS error. The evaluator grades supplied reports.
        report = constant_report()
        report["channels"][0]["metrics"]["max_abs_error_fs"]["value"] = 2e18
        value = policy(report, criteria=[criterion("large", "max_abs_error_fs", bound=1e6,
                                                    margin=1e6, basis="declared_margin")],
                       evidence_class="digital_comparison")
        result = self.evaluate(report, value)
        row = result["criteria"][0]
        self.assertEqual(row["interval"]["lower"], 2e18 - 1e6)
        self.assertEqual(row["interval"]["upper"], 2e18 + 1e6)
        self.assertGreater(row["interval"]["upper"], 2e18)
        self.assertTrue(math.isfinite(row["interval"]["upper"]))
        self.assertEqual(row["numerical_verdict"], "fail")
        self.assertEqual(result["numerical_verdict"], "fail")


class PolicyCompositionAcceptance(PolicyCase):
    def test_evaluator_reuses_public_intrinsic_parser(self):
        parser = subject.parse_policy
        with mock.patch.object(subject, "parse_policy", wraps=parser) as observed:
            self.evaluate()
        self.assertEqual(observed.call_count, 1)
        self.assertEqual(observed.call_args.args, (wire(policy()),))

    def test_invalid_untargeted_report_content_is_not_ignored(self):
        mutations = [
            lambda r: r.update(unexpected=0),
            lambda r: r.update(schema_version=True),
            lambda r: r["analysis"].update(transform="gain_fit"),
            lambda r: r["channels"][0]["metrics"]["candidate_dc_fs"].update(value=math.nan),
            lambda r: r["channels"][0]["metrics"]["absolute_dc_bias_fs"].update(value=-1),
            lambda r: r["channels"][0]["metrics"]["rms_error_fs"].update(unit="V"),
            lambda r: r["channels"][0]["frequencies"][0].update(phase_mask="both_at_or_below_floor"),
            lambda r: r["channels"][0].update(frequencies=[]),
            lambda r: r.update(physical_fidelity="pass"),
        ]
        for index, mutate in enumerate(mutations):
            with self.subTest(case=index):
                report = constant_report()
                mutate(report)
                with self.assertRaises(subject.ComparisonError):
                    subject.evaluate_policy(report, wire(policy()))

    def test_comparison_traversal_bounds_reject_without_partial_result(self):
        for report in (None, [], True, {"nested": [0] * 65537},
                       {"nested": {str(i): 0 for i in range(4097)}}):
            with self.assertRaises(subject.ComparisonError):
                subject.evaluate_policy(report, wire(policy()))
        report = constant_report()
        report["self"] = report
        with self.assertRaises(subject.ComparisonError):
            subject.evaluate_policy(report, wire(policy()))
        report = constant_report()
        nested = 0
        for _ in range(14):
            nested = [nested]
        report["nested"] = nested
        with self.assertRaises(subject.ComparisonError):
            subject.evaluate_policy(report, wire(policy()))

    def test_returned_containers_do_not_alias_inputs_or_other_calls(self):
        report = constant_report()
        value = policy()
        payload = wire(value)
        before_report, before_policy = copy.deepcopy(report), copy.deepcopy(value)
        first = subject.evaluate_policy(report, payload)
        second = subject.evaluate_policy(report, payload)
        first["comparison"]["channels"][0]["metrics"]["rms_error_fs"]["value"] = 999
        first["criteria"][0]["target"]["metric"] = "changed"
        first["criteria"][0]["uncertainty"]["evidence"] = "changed"
        first["criteria"][0]["observed"]["value"] = 888
        self.assertEqual(second["criteria"][0]["observed"]["value"], 0.25)
        self.assertEqual(second["comparison"], before_report)
        self.assertEqual(report, before_report)
        self.assertEqual(value, before_policy)
        self.assertEqual(payload, wire(before_policy))

    def test_rejected_policy_preserves_comparison_and_existing_external_file(self):
        report = constant_report()
        before = copy.deepcopy(report)
        value = policy()
        value["criteria"][0]["uncertainty"]["margin"] = -1
        with tempfile.TemporaryDirectory(prefix="capture-policy-acceptance-") as directory:
            path = Path(directory) / "retained-report.json"
            original = b'{"historical":"retain me"}\n'
            path.write_bytes(original)
            inventory = sorted(item.name for item in Path(directory).iterdir())
            with self.assertRaises(subject.ComparisonError):
                subject.evaluate_policy(report, wire(value))
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(sorted(item.name for item in Path(directory).iterdir()), inventory)
        self.assertEqual(report, before)

    def test_rejected_comparison_preserves_input_and_policy_bytes(self):
        report = constant_report()
        report["channels"][0]["metrics"]["rms_error_fs"]["unit"] = "invalid"
        before = copy.deepcopy(report)
        payload = wire(policy())
        with self.assertRaises(subject.ComparisonError):
            subject.evaluate_policy(report, payload)
        self.assertEqual(report, before)
        self.assertEqual(payload, wire(policy()))

    def test_repeated_evaluation_is_deterministic_and_finite(self):
        report = constant_report()
        payload = wire(policy())
        results = [subject.evaluate_policy(report, payload) for _ in range(3)]
        encoded = [json.dumps(result, sort_keys=True, ensure_ascii=False,
                              allow_nan=False) for result in results]
        self.assertEqual(encoded[0], encoded[1])
        self.assertEqual(encoded[1], encoded[2])


if __name__ == "__main__":
    unittest.main()
