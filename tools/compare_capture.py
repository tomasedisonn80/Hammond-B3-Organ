#!/usr/bin/env python3
"""Bounded digital comparisons and fixed policies under capture-comparison-v1.

This module implements metrics, report admission and uncertainty-aware policy
evaluation from docs/CAPTURE_COMPARISON_CONTRACT.md. Audio loading, corrections
and a command-line wrapper are separate work. Numerical agreement establishes
neither physical fidelity nor correspondence to particular original audio bytes.
"""

from __future__ import annotations

import copy
import hashlib
import math
import re

try:  # Package import and direct import with tools on sys.path are both supported.
    from .capture_common import DataError, parse_json_bytes, validate_json_value
except ImportError:
    from capture_common import DataError, parse_json_bytes, validate_json_value


METRIC_CONTRACT = "capture-comparison-v1"
MAX_CHANNELS = 16
MAX_FRAMES = 262144
MAX_FREQUENCIES = 64
MAX_SAMPLES = 4194304
MAX_SPECTRAL_WORK = 16777216
MAX_REPORT_NUMBER = 2e18
MAX_POLICY_BYTES = 65536
MAX_POLICY_NODES = 4096
MAX_POLICY_DEPTH = 8
MAX_POLICY_NUMBER = 1e6

_POLICY_ANALYSIS_FIELDS = (
    "sample_rate_hz", "channel_count", "frame_count", "window", "floor_fs",
    "frequencies_hz",
)
_POLICY_POINTWISE_UNITS = {
    "absolute_dc_bias_fs": "FS", "rms_error_fs": "FS",
    "max_abs_error_fs": "FS", "normalized_rms_error": "ratio",
}
_POLICY_FREQUENCY_UNITS = {
    "complex_abs_error_fs": "FS", "normalized_complex_error": "ratio",
    "absolute_phase_error_rad": "rad",
}
_POLICY_ID = re.compile(r"[a-z][a-z0-9_-]{0,63}")

_POINTWISE_UNITS = (
    ("reference_dc_fs", "FS"),
    ("candidate_dc_fs", "FS"),
    ("dc_bias_fs", "FS"),
    ("absolute_dc_bias_fs", "FS"),
    ("reference_rms_fs", "FS"),
    ("candidate_rms_fs", "FS"),
    ("rms_error_fs", "FS"),
    ("max_abs_error_fs", "FS"),
    ("normalized_rms_error", "ratio"),
    ("signal_to_error_db", "dB"),
)
_FREQUENCY_UNITS = (
    ("reference_magnitude_fs", "FS"),
    ("candidate_magnitude_fs", "FS"),
    ("complex_abs_error_fs", "FS"),
    ("normalized_complex_error", "ratio"),
    ("reference_phase_rad", "rad"),
    ("candidate_phase_rad", "rad"),
    ("phase_error_rad", "rad"),
    ("absolute_phase_error_rad", "rad"),
)


class ComparisonError(ValueError):
    """Invalid comparison input, report shape or declared resource bound."""


def _require(condition, label, message):
    if not condition:
        raise ComparisonError(f"{label}: {message}")


def _keys(value, expected, label):
    fields = frozenset(expected)
    _require(type(value) is dict and set(value) == fields, label,
             "expected exactly " + ", ".join(sorted(fields)))


def _literal(value, expected, label):
    _require(type(value) is type(expected) and value == expected, label,
             f"expected {expected!r}")


def _integer(value, low, high, label):
    _require(type(value) is int and low <= value <= high, label,
             f"expected an exact integer in {low}..{high}")


def _number(value, low, high, label):
    # Test the magnitude before isfinite, so enormous Python integers cannot
    # overflow an implicit conversion performed by math.isfinite.
    _require(type(value) in (int, float) and low <= value <= high
             and math.isfinite(value), label,
             f"expected a finite exact integer/float in [{low}, {high}]")


def _analysis_parameters(sample_rate_hz, channel_count, frame_count,
                         frequencies_hz, window, floor_fs, *,
                         sequence_types=(list, tuple)):
    """Shared bounded geometry admission; no sample or spectral traversal."""
    _integer(sample_rate_hz, 1, 768000, "sample_rate_hz")
    _integer(channel_count, 1, MAX_CHANNELS, "channel_count")
    _integer(frame_count, 1, MAX_FRAMES, "frame_count")
    _require(type(window) is str
             and window in ("rectangular", "hann_symmetric"), "window",
             "expected rectangular or hann_symmetric")
    _require(window != "hann_symmetric" or frame_count >= 3, "window",
             "hann_symmetric needs at least three frames")
    _number(floor_fs, 1e-12, 1e6, "floor_fs")
    _require(type(frequencies_hz) in sequence_types, "frequencies_hz",
             "expected an exact admitted sequence type")
    _require(len(frequencies_hz) <= MAX_FREQUENCIES, "frequencies_hz",
             "at most 64 frequencies are admitted")
    previous = None
    for index, frequency in enumerate(frequencies_hz):
        _number(frequency, 0, sample_rate_hz / 2,
                f"frequencies_hz[{index}]")
        _require(previous is None or previous < frequency, "frequencies_hz",
                 "frequencies must be strictly increasing and unique")
        previous = frequency
    _require(channel_count * frame_count <= MAX_SAMPLES, "analysis",
             "channel/frame work exceeds 4194304")
    _require(channel_count * frame_count * len(frequencies_hz)
             <= MAX_SPECTRAL_WORK, "analysis",
             "selected-frequency work exceeds 16777216")


def _metric(value, unit, reason=None):
    return {"value": value, "unit": unit, "undefined_reason": reason}


def _signal_to_error_reason(reference_rms, error_rms, floor_fs):
    if reference_rms <= floor_fs:
        return "reference_at_or_below_floor"
    if error_rms == 0:
        return "zero_error"
    if error_rms <= floor_fs:
        return "error_at_or_below_floor"
    return None


def _phase_reason(reference_magnitude, candidate_magnitude, floor_fs):
    reference_masked = reference_magnitude <= floor_fs
    candidate_masked = candidate_magnitude <= floor_fs
    if reference_masked and candidate_masked:
        return "both_at_or_below_floor"
    if reference_masked:
        return "reference_at_or_below_floor"
    if candidate_masked:
        return "candidate_at_or_below_floor"
    return None


def _phase(coefficient):
    value = math.atan2(coefficient.imag, coefficient.real)
    return math.pi if value == -math.pi else value


def _pointwise(reference, candidate, floor_fs):
    count = len(reference)
    errors = [c - r for r, c in zip(reference, candidate)]
    reference_rms = math.sqrt(math.fsum(x * x for x in reference) / count)
    candidate_rms = math.sqrt(math.fsum(x * x for x in candidate) / count)
    error_rms = math.sqrt(math.fsum(x * x for x in errors) / count)
    bias = math.fsum(errors) / count
    normalized_reason = (
        "reference_at_or_below_floor" if reference_rms <= floor_fs else None
    )
    db_reason = _signal_to_error_reason(reference_rms, error_rms, floor_fs)
    return {
        "reference_dc_fs": _metric(math.fsum(reference) / count, "FS"),
        "candidate_dc_fs": _metric(math.fsum(candidate) / count, "FS"),
        "dc_bias_fs": _metric(bias, "FS"),
        "absolute_dc_bias_fs": _metric(abs(bias), "FS"),
        "reference_rms_fs": _metric(reference_rms, "FS"),
        "candidate_rms_fs": _metric(candidate_rms, "FS"),
        "rms_error_fs": _metric(error_rms, "FS"),
        "max_abs_error_fs": _metric(max(abs(x) for x in errors), "FS"),
        "normalized_rms_error": _metric(
            None if normalized_reason else error_rms / reference_rms,
            "ratio", normalized_reason),
        "signal_to_error_db": _metric(
            None if db_reason else 20 * math.log10(reference_rms / error_rms),
            "dB", db_reason),
    }


def _window_weights(frame_count, window):
    if window == "rectangular":
        return [1.0] * frame_count
    # Endpoint zeroes are explicit, not trigonometric approximations.
    return [0.0] + [
        0.5 * (1 - math.cos(2 * math.pi * n / (frame_count - 1)))
        for n in range(1, frame_count - 1)
    ] + [0.0]


def _frequency_row(reference, candidate, frequency, sample_rate_hz,
                   weights, weight_sum, floor_fs):
    # Only one frequency's vectors exist at a time: no C*N*K table is built.
    cosine = []
    sine = []
    for n in range(len(reference)):
        angle = 2 * math.pi * float(frequency) * n / sample_rate_hz
        cosine.append(math.cos(angle))
        sine.append(-math.sin(angle))

    def coefficient(samples):
        real = math.fsum(w * x * cs for w, x, cs
                         in zip(weights, samples, cosine)) / weight_sum
        imag = math.fsum(w * x * sn for w, x, sn
                         in zip(weights, samples, sine)) / weight_sum
        return complex(real, imag)

    reference_coefficient = coefficient(reference)
    candidate_coefficient = coefficient(candidate)
    reference_magnitude = abs(reference_coefficient)
    candidate_magnitude = abs(candidate_coefficient)
    error = abs(candidate_coefficient - reference_coefficient)
    reference_reason = ("reference_at_or_below_floor"
                        if reference_magnitude <= floor_fs else None)
    candidate_reason = ("candidate_at_or_below_floor"
                        if candidate_magnitude <= floor_fs else None)
    phase_reason = _phase_reason(reference_magnitude, candidate_magnitude,
                                 floor_fs)
    phase_error = (None if phase_reason else
                   _phase(candidate_coefficient * reference_coefficient.conjugate()))
    return {
        "frequency_hz": frequency,
        "reference_coefficient": {
            "real_fs": reference_coefficient.real,
            "imag_fs": reference_coefficient.imag,
        },
        "candidate_coefficient": {
            "real_fs": candidate_coefficient.real,
            "imag_fs": candidate_coefficient.imag,
        },
        "metrics": {
            "reference_magnitude_fs": _metric(reference_magnitude, "FS"),
            "candidate_magnitude_fs": _metric(candidate_magnitude, "FS"),
            "complex_abs_error_fs": _metric(error, "FS"),
            "normalized_complex_error": _metric(
                None if reference_reason else error / reference_magnitude,
                "ratio", reference_reason),
            "reference_phase_rad": _metric(
                None if reference_reason else _phase(reference_coefficient),
                "rad", reference_reason),
            "candidate_phase_rad": _metric(
                None if candidate_reason else _phase(candidate_coefficient),
                "rad", candidate_reason),
            "phase_error_rad": _metric(phase_error, "rad", phase_reason),
            "absolute_phase_error_rad": _metric(
                None if phase_reason else abs(phase_error), "rad", phase_reason),
        },
        "phase_mask": phase_reason or "none",
    }


def compare_signals(reference_channels, candidate_channels, sample_rate_hz, *,
                    frequencies_hz=(), window="rectangular", floor_fs=1e-12) -> dict:
    """Compare channel-major arrays exactly as supplied, without corrections.

    Geometry and work budgets are checked before any spectral calculation. All
    scalar samples are validated before metrics are produced, then explicitly
    converted to binary64 one channel pair at a time. Returned containers are
    fresh and never alias caller-owned mutable containers.
    """
    for label, channels in (("reference_channels", reference_channels),
                            ("candidate_channels", candidate_channels)):
        _require(type(channels) in (list, tuple), label,
                 "expected an exact list or tuple of channels")
        _require(1 <= len(channels) <= MAX_CHANNELS, label,
                 "expected between 1 and 16 channels")
        for index, channel in enumerate(channels):
            _require(type(channel) in (list, tuple), f"{label}[{index}]",
                     "expected an exact list or tuple of samples")
    channel_count = len(reference_channels)
    _require(len(candidate_channels) == channel_count, "channels",
             "reference and candidate channel counts must agree")
    frame_count = len(reference_channels[0])
    _analysis_parameters(sample_rate_hz, channel_count, frame_count,
                         frequencies_hz, window, floor_fs)
    for label, channels in (("reference_channels", reference_channels),
                            ("candidate_channels", candidate_channels)):
        for index, channel in enumerate(channels):
            _require(len(channel) == frame_count, f"{label}[{index}]",
                     "every channel must have the same frame count")
    for label, channels in (("reference_channels", reference_channels),
                            ("candidate_channels", candidate_channels)):
        for index, channel in enumerate(channels):
            for frame, sample in enumerate(channel):
                if (type(sample) not in (int, float)
                        or not -1e6 <= sample <= 1e6
                        or not math.isfinite(sample)):
                    raise ComparisonError(
                        f"{label}[{index}][{frame}]: expected a finite exact "
                        "integer/float in [-1000000, 1000000]")

    frequencies = list(frequencies_hz)
    floor = float(floor_fs)
    weights = _window_weights(frame_count, window) if frequencies else None
    weight_sum = math.fsum(weights) if weights is not None else None
    channels = []
    for index in range(channel_count):
        reference = [float(x) for x in reference_channels[index]]
        candidate = [float(x) for x in candidate_channels[index]]
        channels.append({
            "reference_channel_index": index,
            "candidate_channel_index": index,
            "metrics": _pointwise(reference, candidate, floor),
            "frequencies": [
                _frequency_row(reference, candidate, frequency, sample_rate_hz,
                               weights, weight_sum, floor)
                for frequency in frequencies
            ],
        })
    report = {
        "schema_version": 1,
        "metric_contract": METRIC_CONTRACT,
        "sample_rate_hz": sample_rate_hz,
        "channel_count": channel_count,
        "frame_count": frame_count,
        "analysis": {
            "pairing": "index",
            "frame_start": 0,
            "frame_stop": frame_count,
            "window": window,
            "floor_fs": floor,
            "frequencies_hz": frequencies,
            "dft_normalization": "weighted_mean",
            "transform": "none",
        },
        "channels": channels,
        "physical_fidelity": "not_established",
    }
    validate_comparison_report(report)
    return report


def _report_guard(report):
    try:
        # A valid near-floor normalized error can approach 2e18. The common
        # helper's metadata-oriented default of 1e12 would reject such reports.
        validate_json_value(report, max_nodes=65536, max_depth=12,
                            max_number=MAX_REPORT_NUMBER)
    except DataError as error:
        raise ComparisonError(f"comparison: {error}") from error
    pending = [report]
    while pending:
        value = pending.pop()
        if type(value) in (dict, list):
            _require(len(value) <= 4096, "comparison",
                     "generic containers may have at most 4096 members")
            pending.extend(value.values() if type(value) is dict else value)


def _validate_metric(metric, unit, label, *, reason=None, nonnegative=False,
                     phase=False, absolute_phase=False):
    _keys(metric, ("value", "unit", "undefined_reason"), label)
    _literal(metric["unit"], unit, label + ".unit")
    _literal(metric["undefined_reason"], reason, label + ".undefined_reason")
    value = metric["value"]
    if reason is not None:
        _literal(value, None, label + ".value")
        return
    low = 0 if nonnegative or absolute_phase else -MAX_REPORT_NUMBER
    high = math.pi if phase or absolute_phase else MAX_REPORT_NUMBER
    _number(value, low, high, label + ".value")
    if phase:
        _require(-math.pi < value <= math.pi, label + ".value",
                 "phase must lie in (-pi, pi]")


def _validate_pointwise(metrics, floor_fs, label):
    _keys(metrics, (key for key, _ in _POINTWISE_UNITS), label)
    for key, unit in _POINTWISE_UNITS[:8]:
        _validate_metric(metrics[key], unit, label + "." + key,
                         nonnegative=key not in (
                             "reference_dc_fs", "candidate_dc_fs", "dc_bias_fs"))
    reference_rms = metrics["reference_rms_fs"]["value"]
    error_rms = metrics["rms_error_fs"]["value"]
    _validate_metric(
        metrics["normalized_rms_error"], "ratio", label + ".normalized_rms_error",
        reason=("reference_at_or_below_floor"
                if reference_rms <= floor_fs else None), nonnegative=True)
    _validate_metric(
        metrics["signal_to_error_db"], "dB", label + ".signal_to_error_db",
        reason=_signal_to_error_reason(reference_rms, error_rms, floor_fs))


def _validate_frequency(row, frequency, floor_fs, label):
    _keys(row, ("frequency_hz", "reference_coefficient", "candidate_coefficient",
                "metrics", "phase_mask"), label)
    _number(row["frequency_hz"], 0, 384000, label + ".frequency_hz")
    _require(row["frequency_hz"] == frequency, label + ".frequency_hz",
             "frequency must equal its declared analysis entry")
    for side in ("reference_coefficient", "candidate_coefficient"):
        _keys(row[side], ("real_fs", "imag_fs"), label + "." + side)
        for component in ("real_fs", "imag_fs"):
            _number(row[side][component], -MAX_REPORT_NUMBER, MAX_REPORT_NUMBER,
                    f"{label}.{side}.{component}")
    metrics = row["metrics"]
    _keys(metrics, (key for key, _ in _FREQUENCY_UNITS), label + ".metrics")
    for key, unit in _FREQUENCY_UNITS[:3]:
        _validate_metric(metrics[key], unit, f"{label}.metrics.{key}",
                         nonnegative=True)
    reference_magnitude = metrics["reference_magnitude_fs"]["value"]
    candidate_magnitude = metrics["candidate_magnitude_fs"]["value"]
    reference_reason = ("reference_at_or_below_floor"
                        if reference_magnitude <= floor_fs else None)
    candidate_reason = ("candidate_at_or_below_floor"
                        if candidate_magnitude <= floor_fs else None)
    phase_reason = _phase_reason(reference_magnitude, candidate_magnitude,
                                 floor_fs)
    _validate_metric(metrics["normalized_complex_error"], "ratio",
                     label + ".metrics.normalized_complex_error",
                     reason=reference_reason, nonnegative=True)
    _validate_metric(metrics["reference_phase_rad"], "rad",
                     label + ".metrics.reference_phase_rad",
                     reason=reference_reason, phase=True)
    _validate_metric(metrics["candidate_phase_rad"], "rad",
                     label + ".metrics.candidate_phase_rad",
                     reason=candidate_reason, phase=True)
    _validate_metric(metrics["phase_error_rad"], "rad",
                     label + ".metrics.phase_error_rad",
                     reason=phase_reason, phase=True)
    _validate_metric(metrics["absolute_phase_error_rad"], "rad",
                     label + ".metrics.absolute_phase_error_rad",
                     reason=phase_reason, absolute_phase=True)
    _literal(row["phase_mask"], phase_reason or "none", label + ".phase_mask")


def validate_comparison_report(comparison) -> None:
    """Admit an exact section-5 report without mutating it.

    This reusable gate enforces bounded JSON, metadata, geometry, units, numeric
    ranges and the floor-dependent null reasons/masks. It cannot authenticate
    source audio or recalculate metrics for which the samples are absent.
    """
    _report_guard(comparison)
    _keys(comparison, ("schema_version", "metric_contract", "sample_rate_hz",
                       "channel_count", "frame_count", "analysis", "channels",
                       "physical_fidelity"), "comparison")
    _literal(comparison["schema_version"], 1, "comparison.schema_version")
    _literal(comparison["metric_contract"], METRIC_CONTRACT,
             "comparison.metric_contract")
    _literal(comparison["physical_fidelity"], "not_established",
             "comparison.physical_fidelity")
    analysis = comparison["analysis"]
    _keys(analysis, ("pairing", "frame_start", "frame_stop", "window", "floor_fs",
                     "frequencies_hz", "dft_normalization", "transform"),
          "comparison.analysis")
    channel_count = comparison["channel_count"]
    frame_count = comparison["frame_count"]
    frequencies = analysis["frequencies_hz"]
    floor = analysis["floor_fs"]
    _analysis_parameters(comparison["sample_rate_hz"], channel_count, frame_count,
                         frequencies, analysis["window"], floor,
                         sequence_types=(list,))
    for field, expected in (("pairing", "index"), ("frame_start", 0),
                             ("frame_stop", frame_count),
                             ("dft_normalization", "weighted_mean"),
                             ("transform", "none")):
        _literal(analysis[field], expected, "comparison.analysis." + field)
    channels = comparison["channels"]
    _require(type(channels) is list and len(channels) == channel_count,
             "comparison.channels", "expected exactly channel_count rows")
    for index, channel in enumerate(channels):
        label = f"comparison.channels[{index}]"
        _keys(channel, ("reference_channel_index", "candidate_channel_index",
                        "metrics", "frequencies"), label)
        _literal(channel["reference_channel_index"], index,
                 label + ".reference_channel_index")
        _literal(channel["candidate_channel_index"], index,
                 label + ".candidate_channel_index")
        _validate_pointwise(channel["metrics"], floor, label + ".metrics")
        rows = channel["frequencies"]
        _require(type(rows) is list and len(rows) == len(frequencies),
                 label + ".frequencies", "expected every declared frequency row")
        for frequency_index, frequency in enumerate(frequencies):
            _validate_frequency(rows[frequency_index], frequency, floor,
                                f"{label}.frequencies[{frequency_index}]")


def _policy_text(value, label):
    _require(type(value) is str and 0 < len(value) <= 2048
             and bool(value.strip()), label,
             "expected nonblank text of at most 2048 characters")
    _require(not any(ord(char) < 32 or 127 <= ord(char) <= 159
                     for char in value), label,
             "control characters are forbidden")
    # The common JSON parser already rejects unpaired surrogates, including
    # those introduced through JSON escape sequences.


def _policy_id(value, label):
    _require(type(value) is str and _POLICY_ID.fullmatch(value) is not None,
             label, "expected ID matching [a-z][a-z0-9_-]{0,63}")


def _policy_text_guard(value):
    """Enforce policy-wide text/container bounds after bounded JSON parsing."""
    pending = [value]
    while pending:
        item = pending.pop()
        if type(item) in (dict, list):
            _require(len(item) <= 4096, "policy",
                     "generic containers may have at most 4096 members")
            if type(item) is dict:
                for key in item:
                    _policy_text(key, "policy JSON key")
                pending.extend(item.values())
            else:
                pending.extend(item)
        elif type(item) is str:
            _policy_text(item, "policy JSON text")


def _policy_known_text(value, label):
    _keys(value, ("value", "unknown_reason"), label)
    if value["value"] is None:
        _policy_text(value["unknown_reason"], label + ".unknown_reason")
    else:
        _policy_text(value["value"], label + ".value")
        _literal(value["unknown_reason"], None, label + ".unknown_reason")


def _policy_target(target, analysis, label):
    _keys(target, ("channel_index", "frequency_hz", "metric"), label)
    _integer(target["channel_index"], 0, analysis["channel_count"] - 1,
             label + ".channel_index")
    metric = target["metric"]
    _require(type(metric) is str, label + ".metric",
             "expected a typed metric name")
    frequency = target["frequency_hz"]
    if frequency is None:
        _require(metric in _POLICY_POINTWISE_UNITS, label + ".metric",
                 "expected an admitted pointwise upper-bound metric")
        return _POLICY_POINTWISE_UNITS[metric]
    _number(frequency, 0, analysis["sample_rate_hz"] / 2,
            label + ".frequency_hz")
    _require(frequency in analysis["frequencies_hz"], label + ".frequency_hz",
             "frequency must exactly match a selected analysis frequency")
    _require(metric in _POLICY_FREQUENCY_UNITS, label + ".metric",
             "expected an admitted frequency upper-bound metric")
    return _POLICY_FREQUENCY_UNITS[metric]


def _policy_uncertainty(uncertainty, unit, evidence_class, label):
    _keys(uncertainty, ("margin", "unit", "basis", "evidence",
                        "unknown_reason"), label)
    _literal(uncertainty["unit"], unit, label + ".unit")
    basis = uncertainty["basis"]
    _require(type(basis) is str
             and basis in ("unknown", "declared_margin", "synthetic_numerical"),
             label + ".basis", "expected a declared uncertainty basis")
    if basis == "unknown":
        _literal(uncertainty["margin"], None, label + ".margin")
        _literal(uncertainty["evidence"], None, label + ".evidence")
        _policy_text(uncertainty["unknown_reason"], label + ".unknown_reason")
        return
    _number(uncertainty["margin"], 0, MAX_POLICY_NUMBER, label + ".margin")
    if basis == "declared_margin":
        _require(uncertainty["margin"] > 0, label + ".margin",
                 "declared_margin must be strictly positive")
    else:
        _literal(evidence_class, "synthetic_numerical_fixture",
                 label + ".synthetic_evidence_class")
    _policy_text(uncertainty["evidence"], label + ".evidence")
    _literal(uncertainty["unknown_reason"], None, label + ".unknown_reason")


def parse_policy(policy_json: bytes) -> dict:
    """Admit exact policy bytes and all intrinsic semantics without a report.

    This additive preflight API performs no audio work or grading. It returns
    the freshly parsed object without inserting, normalizing or dropping fields.
    Keep the original bytes separately: their hash, not a reserialization's,
    identifies the policy used by evaluate_policy.
    """
    try:
        policy = parse_json_bytes(policy_json, max_bytes=MAX_POLICY_BYTES,
                                  max_nodes=MAX_POLICY_NODES,
                                  max_depth=MAX_POLICY_DEPTH,
                                  max_number=MAX_POLICY_NUMBER)
    except DataError as error:
        raise ComparisonError(f"policy: {error}") from error
    _policy_text_guard(policy)
    _keys(policy, ("schema_version", "metric_contract", "policy_id",
                   "evidence_class", "evaluation_role", "freeze_evidence",
                   "analysis", "criteria"), "policy")
    _literal(policy["schema_version"], 1, "policy.schema_version")
    _literal(policy["metric_contract"], METRIC_CONTRACT,
             "policy.metric_contract")
    _policy_id(policy["policy_id"], "policy.policy_id")
    _require(type(policy["evidence_class"]) is str
             and policy["evidence_class"] in (
                 "synthetic_numerical_fixture", "digital_comparison"),
             "policy.evidence_class", "expected an admitted digital evidence class")
    _require(type(policy["evaluation_role"]) is str
             and policy["evaluation_role"] in (
                 "fit", "validation", "final_test", "unassigned"),
             "policy.evaluation_role", "expected an admitted evaluation role")
    _policy_known_text(policy["freeze_evidence"], "policy.freeze_evidence")
    analysis = policy["analysis"]
    _keys(analysis, _POLICY_ANALYSIS_FIELDS, "policy.analysis")
    _analysis_parameters(analysis["sample_rate_hz"], analysis["channel_count"],
                         analysis["frame_count"], analysis["frequencies_hz"],
                         analysis["window"], analysis["floor_fs"],
                         sequence_types=(list,))
    criteria = policy["criteria"]
    _require(type(criteria) is list and 1 <= len(criteria) <= 256,
             "policy.criteria", "expected between 1 and 256 criteria")
    identifiers, targets = set(), set()
    for index, criterion in enumerate(criteria):
        label = f"policy.criteria[{index}]"
        _keys(criterion, ("criterion_id", "target", "upper_bound", "unit",
                          "rationale", "uncertainty"), label)
        ident = criterion["criterion_id"]
        _policy_id(ident, label + ".criterion_id")
        _require(ident not in identifiers, label + ".criterion_id",
                 "criterion IDs must be unique")
        identifiers.add(ident)
        target = criterion["target"]
        unit = _policy_target(target, analysis, label + ".target")
        target_key = (target["channel_index"], target["frequency_hz"],
                      target["metric"])
        _require(target_key not in targets, label + ".target",
                 "criterion target triples must be unique")
        targets.add(target_key)
        _number(criterion["upper_bound"], 0, MAX_POLICY_NUMBER,
                label + ".upper_bound")
        _literal(criterion["unit"], unit, label + ".unit")
        _policy_text(criterion["rationale"], label + ".rationale")
        _policy_uncertainty(criterion["uncertainty"], unit,
                            policy["evidence_class"], label + ".uncertainty")
    return policy


def evaluate_policy(comparison, policy_json: bytes) -> dict:
    """Evaluate every frozen upper-bound criterion, retaining missing evidence.

    A complete uncertainty interval must fit the declared bound for a numerical
    pass. Exact original policy bytes are hashed, and every returned mutable
    container is independent of caller-owned comparison containers. Neither a
    verdict nor the byte hash establishes physical fidelity or freeze chronology.
    """
    policy = parse_policy(policy_json)
    validate_comparison_report(comparison)
    analysis = policy["analysis"]
    for field in _POLICY_ANALYSIS_FIELDS:
        observed = (comparison[field] if field in (
            "sample_rate_hz", "channel_count", "frame_count")
            else comparison["analysis"][field])
        _require(analysis[field] == observed, "policy.analysis." + field,
                 "must exactly match the supplied comparison analysis")

    comparison_copy = copy.deepcopy(comparison)
    frequency_indices = {frequency: index
                         for index, frequency in enumerate(analysis["frequencies_hz"])}
    evaluated = []
    for criterion in policy["criteria"]:
        target = criterion["target"]
        channel = comparison_copy["channels"][target["channel_index"]]
        frequency = target["frequency_hz"]
        metric = (channel["metrics"][target["metric"]] if frequency is None else
                  channel["frequencies"][frequency_indices[frequency]]["metrics"][target["metric"]])
        value = metric["value"]
        margin = criterion["uncertainty"]["margin"]
        lower = upper = None
        interval_reason = None
        if value is None:
            verdict, reason = "inconclusive", "metric_undefined"
            interval_reason = reason
        elif margin is None:
            verdict, reason = "inconclusive", "uncertainty_unknown"
            interval_reason = reason
        else:
            lower = max(0, value - margin)
            upper = value + margin
            if upper <= criterion["upper_bound"]:
                verdict, reason = "pass", "within_upper_bound"
            elif lower > criterion["upper_bound"]:
                verdict, reason = "fail", "above_upper_bound"
            else:
                verdict, reason = "inconclusive", "interval_overlaps_upper_bound"
        evaluated.append({
            "criterion_id": criterion["criterion_id"],
            "target": copy.deepcopy(target),
            "observed": copy.deepcopy(metric),
            "upper_bound": criterion["upper_bound"],
            "uncertainty": copy.deepcopy(criterion["uncertainty"]),
            "interval": {"lower": lower, "upper": upper, "unit": criterion["unit"],
                         "undefined_reason": interval_reason},
            "numerical_verdict": verdict,
            "reason": reason,
            "physical_fidelity": "not_established",
        })
    verdicts = {item["numerical_verdict"] for item in evaluated}
    overall = ("fail" if "fail" in verdicts else
               "inconclusive" if "inconclusive" in verdicts else "pass")
    # Comparison values are bounded by 2e18 and policy margins by 1e6. Interval
    # sums remain finite but can exceed 2e18; the comparison-only guard must not
    # be reapplied to this larger evaluation envelope.
    return {
        "schema_version": 1,
        "metric_contract": METRIC_CONTRACT,
        "policy_id": policy["policy_id"],
        "policy_sha256": hashlib.sha256(policy_json).hexdigest(),
        "evidence_class": policy["evidence_class"],
        "evaluation_role": policy["evaluation_role"],
        "preregistration": "not_established",
        "numerical_verdict": overall,
        "criteria": evaluated,
        "comparison": comparison_copy,
        "physical_fidelity": "not_established",
    }
