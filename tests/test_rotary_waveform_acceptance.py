#!/usr/bin/env python3
"""Run and admit the native R4 waveform probe; ordinary invocation is smoke.

The full ten-second fixture is opt-in with ``--mode full``.  Every invocation
keeps a new receipt directory, including failed and interrupted native runs.
``--self-test`` exercises report admission without invoking a native renderer;
it is deliberately separate from the ordinary CTest smoke invocation.
Only Python's standard library and the separately authored repository oracles
are used.  No Python-generated samples substitute for native probe evidence.
"""

from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
from decimal import Context, Decimal, localcontext
import gzip
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import re
import shlex
import signal
import struct
import subprocess
import sys
import tempfile
import time
import unittest
import uuid


ROOT = Path(__file__).resolve().parents[1]
RATES = (44100, 48000, 96000, 192000)
PATTERNS = {
    "fixed_1": [1], "fixed_7": [7], "fixed_64": [64],
    "fixed_257": [257], "fixed_4096": [4096],
    "irregular_v1": [3, 1, 511, 7, 4096, 64, 257, 1023, 2, 389, 11, 2048, 5, 127],
}
FIXTURE_IDS = {"full": "rotary-r4-full-stream-v1",
               "smoke": "rotary-r4-shifted-input-smoke-v1"}
REFERENCE_ID = "independent-long-double-waveform-v1"
CONTRACT_ID = "rotary-numerics-v1"
SMOKE_FRAMES = 4097
WAVEFORM_BUDGET = Decimal("2e-5")
REFERENCE_RESIDUAL = Decimal("1e-14")
NATIVE_RESIDUAL = Decimal("1e-11")
MAX_STREAM_BYTES = 24 * 1024 * 1024
MAX_RETAINED_BYTES = 32 * 1024 * 1024
MAX_RUN_BYTES = 64 * 1024 * 1024
DECIMAL_CONTEXT = Context(prec=100, Emin=-999999999, Emax=999999999)
SESSION_REPORTS = "docs/development/2026-11-14-waveform-continuation/reports"
STATIC_REPORT = f"{SESSION_REPORTS}/a14-history-acceptance.json"
STATIC_GRID = f"{SESSION_REPORTS}/a14-static-grid.csv.gz"
REQUIRED_SOURCES = (
    "CMakeLists.txt", "CMakePresets.json", ".github/workflows/ci.yml",
    "include/hammond/RotaryTypes.h", "include/hammond/RotaryMotion.h",
    "include/hammond/RotaryPropagation.h", "include/hammond/RotaryHistory.h",
    "include/hammond/RotaryRenderer.h", "src/RotaryMotion.cpp",
    "src/RotaryPropagation.cpp", "src/RotaryHistory.cpp",
    "src/RotaryStreamingPath.cpp", "src/RotaryRenderer.cpp",
    "src/RotaryRendererInternal.h", "tests/probes/rotary_waveform_probe.cpp",
    "tests/reference/rotary_waveform_reference.h",
    "tests/test_rotary_waveform_acceptance.py", "tests/test_rotary_reference.py",
    "tests/test_rotary_motion_acceptance.py", "tests/test_rotary_propagation_acceptance.py",
    "tests/test_rotary_history_acceptance.cpp", "tests/test_capture_install.py",
    "tools/rotary_reference.py", "docs/ROTARY_NUMERICAL_CONTRACT.md",
    "docs/ROTARY_PROPAGATION_CONTRACT.md", "docs/ROTARY_RENDERER_CONTRACT.md",
    "docs/ROTARY_WAVEFORM_ACCEPTANCE.md", "docs/WAVEFORM_BUILD_PLAN.md",
    STATIC_REPORT, STATIC_GRID,
)

# Exact binary64 fixture inputs are promoted by the independent Decimal oracle.
ROTORS = (
    {"origin": (-0.12, 0.07, 1.10), "radius": 0.18, "slow": 4.2, "fast": 40.5,
     "up": 0.67, "down": 1.10, "direction": 1, "phase": 0.31, "speed": 7.25},
    {"origin": (0.09, -0.05, 0.35), "radius": 0.22, "slow": 3.1, "fast": 31.0,
     "up": 1.40, "down": 2.60, "direction": -1, "phase": 4.40, "speed": 5.75},
)
MICROPHONES = ((1.35, -0.80, 1.25), (-1.20, -0.65, 0.90))


class AdmissionError(ValueError):
    """Native output is present but cannot establish the requested experiment."""


def require(condition, message):
    if not condition:
        raise AdmissionError(message)


def number(value, name, *, minimum=None, maximum=None):
    require(type(value) in (int, float, Decimal), f"{name}: finite number required")
    value = Decimal.from_float(value) if isinstance(value, float) else Decimal(value)
    require(value.is_finite(), f"{name}: nonfinite number")
    # Every fixture quantity is bounded well inside binary64 range.  Retain
    # long-double decimal digits, but reject exponent bombs/overflow spellings.
    require(math.isfinite(float(value)), f"{name}: number exceeds the fixture's finite range")
    if minimum is not None:
        require(value >= Decimal(str(minimum)), f"{name}: below {minimum}")
    if maximum is not None:
        require(value <= Decimal(str(maximum)), f"{name}: exceeds {maximum}")
    return value


def integer(value, name, *, minimum=0, exact=None):
    require(type(value) is int and value >= minimum, f"{name}: integer >= {minimum} required")
    if exact is not None:
        require(value == exact, f"{name}: expected {exact}, got {value}")
    return value


def object_value(value, name):
    require(isinstance(value, dict), f"{name}: object required")
    return value


def array_value(value, name, length=None):
    require(isinstance(value, list), f"{name}: array required")
    if length is not None:
        require(len(value) == length, f"{name}: expected {length} entries, got {len(value)}")
    return value


def sha256_value(value, name):
    require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value),
            f"{name}: lowercase SHA-256 required")
    return value


def reject_nonfinite(value, path="$", depth=0):
    require(depth <= 64, f"{path}: JSON nesting exceeds 64")
    if type(value) in (float, Decimal):
        number(value, path)
    elif isinstance(value, dict):
        for key, item in value.items():
            reject_nonfinite(item, f"{path}.{key}", depth + 1)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            reject_nonfinite(item, f"{path}[{index}]", depth + 1)


def parse_probe_json(raw):
    """Exactly one JSON object, no duplicate keys or non-JSON NaN/Infinity.

    Decimal retains the probe's long-double max_digits10 trace digits.  The
    original byte stream remains the authoritative serialized native record.
    """
    require(isinstance(raw, bytes), "probe stdout must be bytes")
    require(0 < len(raw) <= MAX_STREAM_BYTES, "probe stdout missing or over stream budget")

    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def constant(value):
        raise AdmissionError(f"nonfinite JSON token: {value}")

    try:
        result = json.loads(raw.decode("utf-8"), parse_float=Decimal,
                            parse_constant=constant, object_pairs_hook=pairs)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise AdmissionError(f"probe stdout is not exactly one UTF-8 JSON record: {error}") from error
    object_value(result, "probe report")
    reject_nonfinite(result)
    return result


def frames_for(mode, rate):
    return 10 * rate if mode == "full" else SMOKE_FRAMES


def expected_events(rate, mode):
    c, t = "chorale", "tremolo"
    rows = [(0, 0, t), (0, 0, c), (1, 1, t), (6, 0, t), (7, 0, c), (8, 0, t),
            (63, 1, c), (64, 1, t), (65, 1, c), (256, 0, c), (257, 0, t), (258, 0, c),
            (4095, 0, t), (4096, 1, t), (4097, 0, c),
            (rate // 2 - 1, 0, t), (rate // 2, 1, c), (rate // 2 + 1, 1, t),
            (2 * rate, 0, t), (2 * rate, 1, t), (3 * rate + 17, 0, c),
            (4 * rate - 1, 1, c), (4 * rate, 0, t), (4 * rate, 0, c),
            (4 * rate, 0, t), (5 * rate + 64, 1, t), (6 * rate - 1, 0, c),
            (6 * rate, 1, c), (6 * rate + 1, 0, t), (7 * rate + 257, 1, t),
            (8 * rate - 1, 0, c), (8 * rate, 1, c), (9 * rate, 0, t),
            (10 * rate, 0, c), (10 * rate, 1, t)]
    return [{"frame": frame, "rotor": rotor, "command": command}
            for frame, rotor, command in rows if frame <= frames_for(mode, rate)]


def selected_frames(rate, mode):
    return ([0, 7, 256, 4096, rate // 2, 2 * rate - 1, 2 * rate,
             4 * rate, 6 * rate, 9 * rate, 10 * rate - 1]
            if mode == "full" else [0, 7, 256, 4096])


def convergence_frames(rate, mode):
    return ([0, 1, 7, 64, 257, 4096, rate // 2 - 1, rate // 2, rate // 2 + 1,
             2 * rate - 1, 2 * rate, 3 * rate + 17, 4 * rate,
             6 * rate - 1, 6 * rate, 6 * rate + 1, 9 * rate, 10 * rate - 1]
            if mode == "full" else [0, 1, 7, 64, 257, 4096])


def expected_totals(mode):
    reference_frames = sum(frames_for(mode, rate) for rate in RATES)
    return {
        "rate_count": 4, "completed_partitions": 24,
        "reference_frames": reference_frames,
        "reference_scalar_comparisons": 2 * reference_frames,
        "reference_path_solutions": 4 * reference_frames,
        "native_frames": 6 * reference_frames,
        "native_path_solutions": 24 * reference_frames,
        "partition_compared_samples": 10 * reference_frames,
        "partition_equal_samples": 10 * reference_frames,
        "native_events_consumed": 6 * sum(len(expected_events(rate, mode)) for rate in RATES),
        "selected_trace_paths": sum(4 * len(selected_frames(rate, mode)) for rate in RATES),
        "convergence_pairs": sum(4 * len(convergence_frames(rate, mode)) for rate in RATES),
        "auxiliary_convergence_path_solutions": sum(8 * len(convergence_frames(rate, mode)) for rate in RATES),
    }


def exact_number(actual, expected, name):
    # Native JSON prints the exact binary64 fixture through max_digits10; a
    # literal such as 0.31 therefore need not have only two decimal places.
    require(float(number(actual, name)) == float(expected), f"{name}: frozen value changed")


def assert_close(actual, expected, tolerance, name):
    require(abs(number(actual, name) - number(expected, name)) <= Decimal(str(tolerance)),
            f"{name}: inconsistent recorded values")


def assert_recorded_difference(actual, reference, recorded, precision, tolerance, name):
    """Replay a binary64 subtraction from its round-trip decimal tokens.

    At 53 bits, subtracting the *printed decimals* can lose the cancellation
    retained by the native operation.  max_digits10=17 recovers each binary64
    operand exactly, so require the same result with no numerical allowance.
    Canonical numeric tokens prevent shortened/fabricated decimal precision
    from adding any uncertainty.  Wider references keep their existing checks.
    """
    values = [number(value, name) for value in (actual, reference, recorded)]
    if precision["digits"] == 53:
        require(sys.float_info.radix == 2 and sys.float_info.mant_dig == 53
                and sys.float_info.rounds == 1, "Python binary64 round-to-nearest replay required")
        replay = [float(value) for value in values]
        for value, binary in zip(values, replay):
            require(value == Decimal(format(binary, ".17g")),
                    f"{name}: noncanonical binary64 max_digits10 token")
        require(abs(replay[0] - replay[1]) == replay[2],
                f"{name}: inconsistent recorded binary64 difference")
    else:
        assert_close(abs(values[0] - values[1]), values[2], tolerance, name)


def successful(value, name, *, completed=False):
    object_value(value, name)
    require(value.get("status") == "pass", f"{name}: status is not pass")
    if completed:
        require(value.get("completed") is True, f"{name}: incomplete")


def no_frame_failures(value, name):
    object_value(value, name)
    integer(value["count"], name + ".count", exact=0)
    require(value["complete"] is True, name + ": incomplete failure accounting")
    require(value["first_frame"] == -1 and value["last_frame"] == -1,
            name + ": inconsistent empty failure range")


def binary64_bits(value, bits, name):
    number(value, name)
    require(isinstance(bits, str) and re.fullmatch(r"[0-9a-f]{16}", bits),
            name + ": binary64 hex bits missing")
    require(struct.pack(">d", float(value)).hex() == bits,
            name + ": decimal value and binary64 bits disagree")


def validate_position(value, name):
    object_value(value, name)
    integer(value["frame"], name + ".frame", minimum=-(2**63))
    fraction = number(value["fraction"], name + ".fraction", minimum=0)
    require(fraction < 1, name + ": fraction must be < 1")
    binary64_bits(fraction, value["fraction_bits"], name + ".fraction")


def validate_motion(value, name):
    object_value(value, name)
    number(value["phase_rad"], name + ".phase_rad", minimum=0, maximum=math.tau)
    number(value["speed_rad_s"], name + ".speed_rad_s", minimum=0, maximum=200)
    integer(value["turns"], name + ".turns", minimum=-(2**63))
    binary64_bits(value["phase_rad"], value["phase_bits"], name + ".phase")
    binary64_bits(value["speed_rad_s"], value["speed_bits"], name + ".speed")


def validate_native_path(value, name):
    object_value(value, name)
    for key in ("delay_s", "distance_m", "distance_gain"):
        require(number(value[key], name + "." + key) > 0, name + ": positive path values required")
    number(value["emission_phase_rad"], name + ".phase", minimum=0, maximum=math.tau)
    number(value["radial_speed_m_s"], name + ".radial_speed")
    number(value["frequency_ratio"], name + ".ratio", minimum="0.8", maximum="1.333333333333334")
    require(abs(number(value["residual_s"], name + ".residual")) <= NATIVE_RESIDUAL,
            name + ": native residual budget failed")
    iterations = integer(value["iterations"], name + ".iterations", minimum=1)
    require(iterations <= 48, name + ": native iteration budget failed")


def validate_final_state(state, rate, frames, events, name):
    object_value(state, name)
    require(state["prepared"] is True, name + ": renderer unprepared")
    exact_number(state["sample_rate"], rate, name + ".sample_rate")
    integer(state["frame"], name + ".frame", exact=frames)
    integer(state["max_frame"], name + ".max_frame", exact=86400 * rate)
    commands = ["chorale", "chorale"]
    for event in events:
        commands[event["rotor"]] = event["command"]
    require(state["commands"] == commands, name + ": final inclusive-boundary commands differ")
    for key in ("motion", "epoch_initial"):
        for rotor, value in enumerate(array_value(state[key], name + "." + key, 2)):
            validate_motion(value, f"{name}.{key}[{rotor}]")
    for rotor, expected in enumerate(ROTORS):
        initial = state["epoch_initial"][rotor]
        exact_number(initial["phase_rad"], expected["phase"], name + ".epoch_initial.phase")
        exact_number(initial["speed_rad_s"], expected["speed"], name + ".epoch_initial.speed")
        integer(initial["turns"], name + ".epoch_initial.turns", exact=0)
    for rotor, segment in enumerate(array_value(state["segments"], name + ".segments", 2)):
        integer(segment["anchor_frame"], name + ".anchor_frame")
        require(segment["anchor_frame"] <= frames, name + ": future segment anchor")
        validate_motion(segment["initial"], name + ".segment.initial")
        exact_number(segment["target_rad_s"], ROTORS[rotor]["fast" if commands[rotor] == "tremolo" else "slow"], name + ".target")
        require(float(number(segment["tau_s"], name + ".tau")) in (ROTORS[rotor]["up"], ROTORS[rotor]["down"]),
                name + ": unknown time constant")
        require(segment["direction"] == ROTORS[rotor]["direction"], name + ": direction changed")


def validate_diagnostics(value, frames, name):
    object_value(value, name)
    require(value["path_order"] == "rotor_major", name + ": path order changed")
    require(value["has_rendered_sample"] is True, name + ": no rendered sample")
    integer(value["last_input_frame"], name + ".last_input_frame", exact=frames - 1)
    validate_position(value["last_observation"], name + ".last_observation")
    require(value["last_observation"]["frame"] == frames - 3
            and value["last_observation"]["fraction"] == 0, name + ": observation differs from n-2")
    number(value["max_solver_residual_s"], name + ".max_residual", minimum=0, maximum=NATIVE_RESIDUAL)
    require(1 <= integer(value["max_solver_iterations"], name + ".max_iterations") <= 48,
            name + ": native iteration budget failed")
    for index, path in enumerate(array_value(value["last_paths"], name + ".last_paths", 4)):
        validate_native_path(path, f"{name}.path[{index}]")
    for index, position in enumerate(array_value(value["last_emissions"], name + ".last_emissions", 4)):
        validate_position(position, f"{name}.emission[{index}]")


def validate_fixture(fixture):
    require(fixture["synthetic_engineering_fixture"] is True, "fixture evidence class changed")
    mapping = {"radius_m": "radius", "slow_rad_s": "slow", "fast_rad_s": "fast",
               "tau_up_s": "up", "tau_down_s": "down", "initial_phase_rad": "phase",
               "initial_speed_rad_s": "speed", "direction": "direction"}
    for rotor, value in enumerate(array_value(fixture["rotors"], "fixture.rotors", 2)):
        integer(value["rotor"], "fixture.rotor", exact=rotor)
        require(value["initial_command"] == "chorale", "fixture initial command changed")
        for field, source in mapping.items():
            exact_number(value[field], ROTORS[rotor][source], "fixture." + field)
        for actual, expected in zip(array_value(value["origin_m"], "fixture.origin", 3), ROTORS[rotor]["origin"]):
            exact_number(actual, expected, "fixture.origin")
    for actual, expected in zip(array_value(fixture["microphones_m"], "fixture.microphones", 2), MICROPHONES):
        for component, coordinate in zip(array_value(actual, "fixture.microphone", 3), expected):
            exact_number(component, coordinate, "fixture.microphone")
    exact_number(fixture["sound_speed_m_s"], 343, "fixture.sound_speed")
    exact_number(fixture["reference_distance_m"], 1, "fixture.reference_distance")


def validate_precision(environment):
    successful(environment, "precision_environment")
    require(environment["fast_math_enabled"] is False, "native fast-math is forbidden")
    require(environment["rounding_is_to_nearest"] is True, "native rounding must be to nearest")
    integer(environment["rounding_mode"], "rounding_mode")
    for key in ("compiler", "standard_library", "platform", "build_configuration", "build_flags"):
        require(isinstance(environment[key], str) and environment[key], "missing precision/environment " + key)
    integer(environment["cplusplus"], "cplusplus", minimum=202002)
    for name in ("double", "long_double"):
        precision = object_value(environment[name], name)
        integer(precision["radix"], name + ".radix", exact=2)
        for key in ("digits", "digits10", "max_digits10", "sizeof"):
            integer(precision[key], name + "." + key, minimum=1)
        require(type(precision["is_iec559"]) is bool, name + ": IEC559 fact missing")
    require(environment["double"]["digits"] == 53 and environment["double"]["sizeof"] == 8,
            "binary64 double required")
    for name in ("double", "long_double"):
        precision = environment[name]
        if precision["digits"] == 53:
            require(precision["digits10"] == 15 and precision["max_digits10"] == 17
                    and precision["is_iec559"] is True,
                    name + ": inconsistent binary64 precision metadata")
    require(environment["long_double"]["digits"] >= 53, "reference precision below double")
    require(environment["wider_than_double"] is (environment["long_double"]["digits"] > 53),
            "false extra-precision claim")


def validate_report(report, mode):
    try:
        return _validate_report(report, mode)
    except (KeyError, TypeError, IndexError, OverflowError) as error:
        raise AdmissionError(f"incomplete or malformed native report: {error}") from error


def _validate_report(report, mode):
    require(mode in FIXTURE_IDS, "unknown requested mode")
    object_value(report, "report")
    reject_nonfinite(report)
    successful(report, "native report", completed=True)
    integer(report["schema_version"], "schema_version", exact=1)
    require(report["mode"] == mode, "native mode differs from requested mode")
    for key in ("fixture_id", "experiment_id"):
        require(report[key] == FIXTURE_IDS[mode], f"{key}: smoke/full identity mismatch")
    require(report["reference_id"] == REFERENCE_ID, "reference identity changed")
    require(report["contract_id"] == CONTRACT_ID, "numerical contract changed")
    require(report["renderer_contract_id"] == "rotary-renderer-v1", "renderer contract changed")
    require(report["model_id"] == "nominal-effective-mouth-rotary-v1", "model identity changed")
    require(report["full_duration_seconds"] == (10 if mode == "full" else None), "full duration declaration wrong")
    integer(report["required_rate_count"], "required_rate_count", exact=4)
    integer(report["partition_count"], "partition_count", exact=6)
    require(report["required_rates"] == list(RATES), "required rate set changed")
    require(report["fixed_blocks"] == [1, 7, 64, 257, 4096], "fixed partitions changed")
    require(report["irregular_blocks"] == PATTERNS["irregular_v1"], "irregular partition changed")
    totals = expected_totals(mode)
    for key, expected in totals.items():
        integer(report["totals"][key], "totals." + key, exact=expected)
    integer(report["required_reference_frames"], "required_reference_frames", exact=totals["reference_frames"])
    integer(report["required_native_frames"], "required_native_frames", exact=totals["native_frames"])
    require(report["exception"] == "" and report["failures"] == [], "native failure record present")
    validate_precision(report["precision_environment"])
    validate_fixture(report["fixture"])
    require(report["provenance"]["sha256_self_check_passed"] is True, "native SHA-256 self check failed")
    integer(report["provenance"]["sha256_self_check_vectors"], "hash self check vectors", exact=3)
    require(report["provenance"]["stream_encoding"] == "frame_interleaved_little_endian_binary64", "stream digest encoding changed")
    signal_values = report["signal"]
    require(signal_values["seed_hex"] == "726f746172792d34", "signal seed changed")
    require(signal_values["input_frame_shift_in_sample_rates"] == (0 if mode == "full" else 2), "input frame shift changed")
    require(signal_values["negative_history"] == "zero", "negative waveform history changed")
    require(signal_values["input_channel_order"] == ["horn", "drum"]
            and signal_values["output_channel_order"] == ["left", "right"], "channel order changed")
    policy = report["comparison_policy"]
    require(policy["algorithmic_latency_frames"] == 2 and policy["observation"] == "(n-2)/Fs", "latency/observation changed")
    for key, expected in (("normalized_maximum_limit", WAVEFORM_BUDGET),
                          ("reference_residual_target_s", "5e-15"),
                          ("reference_residual_limit_s", REFERENCE_RESIDUAL),
                          ("native_residual_limit_s", NATIVE_RESIDUAL)):
        exact_number(policy[key], expected, "comparison_policy." + key)
    integer(policy["native_iteration_limit"], "native_iteration_limit", exact=48)
    for key in ("fitted_gain", "fitted_time_shift", "clipping", "frequency_remapping"):
        require(policy[key] is False, "forbidden waveform comparison adjustment: " + key)
    require(policy["reference_to_native_path"] == [0, 2, 1, 3], "path index mapping changed")
    resource = report["resource_observations"]
    integer(resource["max_canonical_audio_bytes"], "max_canonical_audio_bytes",
            exact=16 * max(frames_for(mode, rate) for rate in RATES))
    integer(resource["canonical_audio_limit_bytes"], "canonical_audio_limit_bytes", exact=30720000)
    require(resource["full_waveform_buffers"] == 1 and resource["reference_audio_buffered"] is False,
            "native buffering policy changed")
    number(resource["wall_seconds"], "native wall_seconds", minimum=0)
    for key in ("sizeof_waveform_history", "sizeof_motion_frame_history", "sizeof_renderer_state", "sizeof_renderer_diagnostics"):
        integer(resource[key], key, minimum=1)
    rates = array_value(report["rates"], "rates", 4)
    require([row["rate"] for row in rates] == list(RATES), "missing, repeated or reordered rate")
    for row in rates:
        validate_rate(row, mode, report["precision_environment"]["long_double"])
    return {"status": "pass", "mode": mode, "fixture_id": FIXTURE_IDS[mode],
            "totals": totals,
            "maximum_normalized_error": max(number(channel["maximum_normalized_error"], "error")
                                              for row in rates for channel in row["channels"])}


def validate_rate(row, mode, precision):
    rate, frames = row["rate"], frames_for(mode, row["rate"])
    name = f"rate[{rate}]"
    successful(row, name, completed=True)
    integer(row["required_frames"], name + ".required_frames", exact=frames)
    integer(row["reference_frames"], name + ".reference_frames", exact=frames)
    integer(row["reference_scalar_comparisons"], name + ".reference_scalar_comparisons", exact=2 * frames)
    assert_close(row["duration_seconds"], Decimal(frames) / rate, "1e-16", name + ".duration_seconds")
    integer(row["canonical_audio_bytes"], name + ".canonical_audio_bytes", exact=16 * frames)
    expected = expected_events(rate, mode)
    require(row["events"] == expected, name + ": ordered events differ, including final boundary")
    integer(row["event_count"], name + ".event_count", exact=len(expected))
    channels = array_value(row["channels"], name + ".channels", 2)
    for index, channel in enumerate(channels):
        successful(channel, name + ".channel")
        integer(channel["channel"], name + ".channel", exact=index)
        integer(channel["samples"], name + ".samples", exact=frames)
        normalization = number(channel["normalization_G"], name + ".G", minimum="1e-100")
        expected_g = 0.0
        for rotor in ROTORS:
            displacement = [MICROPHONES[index][axis] - rotor["origin"][axis] for axis in range(3)]
            minimum = math.sqrt((math.hypot(*displacement[:2]) - rotor["radius"]) ** 2 + displacement[2] ** 2)
            expected_g += 1.0 / minimum
        assert_close(normalization, expected_g, "2e-12", name + ".normalization_G")
        maximum = number(channel["maximum_absolute_error"], name + ".maximum_absolute_error", minimum=0)
        rms = number(channel["rms_absolute_error"], name + ".rms_absolute_error", minimum=0)
        normalized_max = number(channel["maximum_normalized_error"], name + ".maximum_normalized_error", minimum=0, maximum=WAVEFORM_BUDGET)
        normalized_rms = number(channel["rms_normalized_error"], name + ".rms_normalized_error", minimum=0, maximum=WAVEFORM_BUDGET)
        require(rms <= maximum and normalized_rms <= normalized_max, name + ": RMS exceeds maximum")
        assert_close(normalized_max, maximum / normalization, "1e-19", name + ".normalized_maximum")
        assert_close(normalized_rms, rms / normalization, "1e-19", name + ".normalized_rms")
        worst = integer(channel["worst_frame"], name + ".worst_frame")
        require(worst < frames, name + ": worst frame out of range")
        assert_recorded_difference(channel["worst_actual"], channel["worst_reference"],
                                   maximum, precision, "1e-18", name + ".worst_error")
        no_frame_failures(channel["failures"], name + ".waveform_failures")
    solver = row["reference_solver"]
    integer(solver["path_solutions"], name + ".reference_path_solutions", exact=4 * frames)
    number(solver["max_residual_s"], name + ".reference_residual", minimum=0, maximum=REFERENCE_RESIDUAL)
    require(1 <= integer(solver["max_evaluations"], name + ".reference_evaluations") <= 122,
            name + ": reference evaluation count outside bounded solver")
    require(integer(solver["max_contraction_steps"], name + ".contraction_steps") <= 24, name + ": contraction cap exceeded")
    require(integer(solver["max_bisections"], name + ".bisections") <= 96, name + ": bisection cap exceeded")
    sha256_value(row["reference_audio_sha256"], name + ".reference_audio_sha256")
    regions = array_value(row["signal_regions"], name + ".signal_regions", 3)
    counts = [2 * rate, 7 * rate - rate // 8, rate + rate // 8] if mode == "full" else [0, frames, 0]
    for region, identifier, count in zip(regions, ("impulses", "bounded_input", "explicit_silence"), counts):
        require(region["id"] == identifier and region["required"] is (mode == "full" or identifier == "bounded_input"), name + ": signal region changed")
        integer(region["frames"], name + ".region.frames", exact=count)
        for key in ("input_nonzero", "actual_nonzero", "reference_nonzero", "nonzero_comparison_count"):
            for value in array_value(region[key], name + ".region." + key, 2):
                require(integer(value, name + ".region." + key) <= count, name + ": invalid nonzero count")
                if count and identifier != "explicit_silence":
                    require(value > 0, name + ": silent impulse/bounded comparison cannot pass")
        if identifier == "impulses" and mode == "full":
            require(region["input_nonzero"] == [2, 2], name + ": isolated impulses missing")
        if identifier == "explicit_silence":
            require(region["input_nonzero"] == [0, 0], name + ": explicit silence contains input")
    partitions = array_value(row["partitions"], name + ".partitions", 6)
    require([part["id"] for part in partitions] == list(PATTERNS), name + ": missing/repeated/reordered partition")
    baseline = partitions[0]
    for index, part in enumerate(partitions):
        tag = name + "." + part["id"]
        successful(part, tag, completed=True)
        require(part["baseline"] is (index == 0), tag + ": incorrect baseline")
        require(part["pattern"] == PATTERNS[part["id"]], tag + ": block pattern changed")
        integer(part["native_frames"], tag + ".native_frames", exact=frames)
        integer(part["native_path_solutions"], tag + ".native_paths", exact=4 * frames)
        integer(part["events_consumed"], tag + ".events_consumed", exact=len(expected))
        integer(part["process_calls"], tag + ".process_calls", minimum=1)
        require(1 <= integer(part["max_block_observed"], tag + ".max_block") <= max(part["pattern"]), tag + ": wrong observed block")
        number(part["max_native_residual_s"], tag + ".max_native_residual", minimum=0, maximum=NATIVE_RESIDUAL)
        require(1 <= integer(part["max_native_iterations"], tag + ".iterations") <= 48, tag + ": native iterations exceeded")
        for key in ("input_sha256", "audio_sha256"):
            sha256_value(part[key], tag + "." + key)
            require(part[key] == baseline[key], tag + ": partition stream hash changed")
        for channel, comparison in enumerate(array_value(part["audio_bit_comparison"], tag + ".audio_bit_comparison", 2)):
            integer(comparison["channel"], tag + ".comparison.channel", exact=channel)
            for key in ("compared_samples", "equal_samples"):
                integer(comparison[key], tag + "." + key, exact=frames if index else 0)
            exact_number(comparison["max_absolute_difference"], 0, tag + ".max_audio_difference")
            no_frame_failures(comparison["failures"], tag + ".audio_failures")
        for key, count in (("final_state_comparison", 32), ("final_diagnostics_comparison", 46)):
            comparison = part[key]
            integer(comparison["field_count"], tag + "." + key + ".field_count", exact=count if index else 0)
            require(comparison["match"] is True and comparison["mismatched_fields"] == [], tag + ": final fields differ")
            require(comparison["floating_comparison"] == "binary64_bits" and comparison["compares_struct_padding"] is False, tag + ": comparison is not exact named fields")
        validate_final_state(part["final_state"], rate, frames, expected, tag + ".state")
        validate_diagnostics(part["final_diagnostics"], frames, tag + ".diagnostics")
        require(part["final_state"] == baseline["final_state"], tag + ": serialized final state differs")
        require(part["final_diagnostics"] == baseline["final_diagnostics"], tag + ": serialized diagnostics differ")
    for rotor, final in enumerate(array_value(row["final_reference_motion"], name + ".final_reference_motion", 2)):
        integer(final["rotor"], name + ".final.rotor", exact=rotor)
        require(final["passed"] is True and final["command_match"] is True, name + ": final reference motion failed")
        for metric, reference_key, slope in (("angle", "angle_rad", "4e-15"), ("speed", "speed_rad_s", "4e-14")):
            suffix = "rad" if metric == "angle" else "rad_s"
            limit = Decimal("5e-12") + Decimal(slope) * abs(number(final[reference_key], name + ".final.reference"))
            assert_close(final[f"{metric}_limit_{suffix}"], limit, "1e-24", name + ".final.limit")
            number(final[f"{metric}_error_{suffix}"], name + ".final.error", minimum=0, maximum=limit)
    validate_selected_paths(row, mode, precision)


def validate_selected_paths(row, mode, precision):
    rate, name = row["rate"], f"rate[{row['rate']}]"
    traces = array_value(row["selected_traces"], name + ".selected_traces", 4 * len(selected_frames(rate, mode)))
    expected = {(frame, rotor, channel) for frame in selected_frames(rate, mode) for rotor in range(2) for channel in range(2)}
    actual = {(trace["frame"], trace["rotor"], trace["channel"]) for trace in traces}
    require(actual == expected, name + ": selected traces missing/repeated/moved")
    for trace in traces:
        require(trace["observation_frame"] == trace["frame"] - 2, name + ": trace observation changed")
        require(trace["reference_path_index"] == 2 * trace["channel"] + trace["rotor"]
                and trace["native_path_index"] == 2 * trace["rotor"] + trace["channel"], name + ": trace path mapping wrong")
        require(trace["has_native"] is True, name + ": trace lacks native diagnostic")
        for key in ("delay_s", "distance_m", "distance_gain"):
            require(number(trace[key], name + ".trace." + key) > 0, name + ": invalid reference path")
        require(0 <= number(trace["fraction"], name + ".trace.fraction") < 1, name + ": invalid reference fraction")
        integer(trace["emission_frame"], name + ".trace.emission_frame", minimum=-(2**63))
        number(trace["angle_rad"], name + ".trace.angle")
        number(trace["speed_rad_s"], name + ".trace.speed", minimum=0, maximum=200)
        number(trace["frequency_ratio"], name + ".trace.ratio", minimum="0.8", maximum="1.333333333333334")
        require(abs(number(trace["residual_s"], name + ".trace.residual")) <= REFERENCE_RESIDUAL, name + ": reference trace residual failed")
        require(1 <= integer(trace["evaluations"], name + ".trace.evaluations") <= 122, name + ": reference trace evaluations invalid")
        validate_native_path(trace["native_path"], name + ".trace.native_path")
        validate_position(trace["native_emission"], name + ".trace.native_emission")
    convergence = row["reference_convergence"]
    for key, limit in (("difference_limit_s", "2e-14"), ("contractive_target_s", "5e-15"), ("bisection_target_s", "1e-16")):
        exact_number(convergence[key], limit, name + ".convergence." + key)
    pairs = array_value(convergence["pairs"], name + ".convergence.pairs", 4 * len(convergence_frames(rate, mode)))
    integer(convergence["pair_count"], name + ".pair_count", exact=len(pairs))
    expected = {(frame, rotor, channel) for frame in convergence_frames(rate, mode) for rotor in range(2) for channel in range(2)}
    require({(pair["frame"], pair["rotor"], pair["channel"]) for pair in pairs} == expected, name + ": convergence coordinates missing/repeated")
    for pair in pairs:
        require(pair["passed"] is True, name + ": convergence comparison failed")
        require(pair["reference_path_index"] == 2 * pair["channel"] + pair["rotor"], name + ": convergence path order wrong")
        difference = number(pair["difference_s"], name + ".convergence.difference", minimum=0, maximum="2e-14")
        assert_recorded_difference(pair["contractive_delay_s"], pair["bisection_delay_s"],
                                   difference, precision, "1e-22", name + ".convergence.recorded_difference")
        for prefix, limit in (("contractive", "5e-15"), ("bisection", "1e-16")):
            require(abs(number(pair[prefix + "_residual_s"], name + ".residual")) <= Decimal(limit), name + ": convergence residual target failed")
            require(1 <= integer(pair[prefix + "_evaluations"], name + ".evaluations") <= 122, name + ": convergence evaluations outside cap")


def load_decimal_reference():
    path = ROOT / "tests/test_rotary_propagation_acceptance.py"
    spec = importlib.util.spec_from_file_location("_waveform_cartesian_reference", path)
    require(spec is not None and spec.loader is not None, "cannot load independent Cartesian reference")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    require(module.ref.PRECISION >= 80, "independent motion precision below 80 decimal digits")
    return module


def decimal_path_bisection(reference, timeline, scene, observation):
    lower_distance, upper_distance, _ = reference.distance_bounds(scene)
    sound_speed = Decimal.from_float(scene["c"])
    lower, upper = lower_distance / sound_speed, upper_distance / sound_speed

    def residual(delay):
        motion = timeline.state_at(observation - delay)
        distance = reference.geometry(scene, motion.angle_rad, motion.speed_rad_s)["distance"]
        return delay - distance / sound_speed

    require(residual(lower) <= 0 <= residual(upper), "independent Decimal path failed to bracket")
    for iteration in range(1, 97):
        midpoint = (lower + upper) / 2
        value = residual(midpoint)
        if abs(value) <= Decimal("1e-16"):
            return midpoint, value, iteration
        if value < 0:
            lower = midpoint
        else:
            upper = midpoint
    raise AdmissionError("independent Decimal path did not meet 1e-16 s in 96 bisections")


def selected_decimal_checks(report):
    """Qualify the independent long-double reference at its actual query points."""
    reference = load_decimal_reference()
    measured, failures = {}, []
    paths = 0
    maximum_bisections = 0
    maximum_bisection_residual = Decimal(0)
    started = time.monotonic()

    def measure(name, actual, expected, budget, where):
        actual, expected, budget = (number(value, name) for value in (actual, expected, budget))
        error = abs(actual - expected)
        metric = measured.setdefault(name, {"count": 0, "maximum_absolute_error": Decimal(-1),
            "maximum_budget_fraction": Decimal(0), "sum_squared_error": Decimal(0), "worst": None})
        metric["count"] += 1
        metric["sum_squared_error"] += error * error
        metric["maximum_budget_fraction"] = max(metric["maximum_budget_fraction"], error / budget)
        detail = {"position": where, "actual": actual, "reference": expected,
                  "absolute_error": error, "budget": budget}
        if error > metric["maximum_absolute_error"]:
            metric["maximum_absolute_error"], metric["worst"] = error, detail
        if error > budget:
            failures.append({"metric": name, **detail})

    with localcontext(DECIMAL_CONTEXT):
        for rate_row in report["rates"]:
            rate = rate_row["rate"]
            timelines = []
            for rotor, values in enumerate(ROTORS):
                profile = reference.ref.MotionProfile(
                    *(Decimal.from_float(values[key]) for key in ("slow", "fast", "up", "down")),
                    values["direction"])
                events = [reference.ref.CommandEvent(reference.ref.frame_time(event["frame"], rate), event["command"])
                          for event in rate_row["events"] if event["rotor"] == rotor]
                timelines.append(reference.ref.RotorTimeline(
                    profile, Decimal.from_float(values["phase"]), Decimal.from_float(values["speed"]), "chorale", events))
            for trace in rate_row["selected_traces"]:
                paths += 1
                rotor, channel = trace["rotor"], trace["channel"]
                where = {"rate": rate, "frame": trace["frame"], "rotor": rotor, "channel": channel,
                         "emission_frame": trace["emission_frame"], "fraction": trace["fraction"]}
                timeline = timelines[rotor]
                emission_time = (Decimal(trace["emission_frame"]) + number(trace["fraction"], "fraction")) / rate
                motion = timeline.state_at(emission_time)
                measure("motion_angle_rad", trace["angle_rad"], motion.angle_rad,
                        Decimal("5e-12") + Decimal("4e-15") * abs(motion.angle_rad), where)
                measure("motion_speed_rad_s", trace["speed_rad_s"], motion.speed_rad_s,
                        Decimal("5e-12") + Decimal("4e-14") * abs(motion.speed_rad_s), where)
                scene = {**ROTORS[rotor], "mic": MICROPHONES[channel], "c": 343.0}
                geometry = reference.geometry(scene, motion.angle_rad, motion.speed_rad_s)
                measure("distance_m", trace["distance_m"], geometry["distance"], Decimal("2e-12"), where)
                measure("frequency_ratio", trace["frequency_ratio"], geometry["ratio"], Decimal("2e-10"), where)
                observation = Decimal(trace["observation_frame"]) / rate
                delay, residual, iterations = decimal_path_bisection(reference, timeline, scene, observation)
                measure("root_delay_s", trace["delay_s"], delay, Decimal("1e-14"), where)
                maximum_bisections = max(maximum_bisections, iterations)
                maximum_bisection_residual = max(maximum_bisection_residual, abs(residual))
        for metric in measured.values():
            metric["rms_error"] = (metric.pop("sum_squared_error") / metric["count"]).sqrt()
    required = expected_totals(report["mode"])["selected_trace_paths"]
    require(paths == required, "incomplete selected Decimal cross-check")
    return {"status": "pass" if not failures else "fail", "selected_paths": paths,
            "motion_precision_digits": reference.ref.PRECISION, "cartesian_precision_digits": 100,
            "motion_queries": "actual long-double split emission positions",
            "root_queries": "original integer n-2 observation positions; independent motion and Cartesian bisection",
            "root_target_s": "1e-16", "root_difference_limit_s": "1e-14",
            "maximum_bisections": maximum_bisections,
            "maximum_bisection_residual_s": maximum_bisection_residual,
            "metrics": measured, "failures": failures, "wall_seconds": time.monotonic() - started,
            "scope": "qualifies selected independent long-double reference queries; complete native audio is compared by the C++ probe"}


def retained_static_grid():
    """Admit A14's retained complete native grid without rerunning that gate."""
    report_path, grid_path = ROOT / STATIC_REPORT, ROOT / STATIC_GRID
    require(report_path.is_file() and grid_path.is_file(), "retained A14 static-grid report/artifact missing")
    report = parse_probe_json(report_path.read_bytes())
    require(report["status"] == "pass" and report["source_stable"] is True
            and report["failures"] == [], "retained A14 acceptance did not pass stably")
    grid = report["static_grid"]
    for key in ("evaluated_rows", "written_rows"):
        integer(grid[key], "retained_static_grid." + key, exact=33280)
    integer(grid["columns"], "retained_static_grid.columns", exact=7)
    require(grid["all_coordinates_verified"] is True and grid["lossless_round_trip_verified"] is True,
            "retained static grid lacks complete coordinate/lossless checks")
    require(digest(grid_path) == grid["compressed_sha256"], "retained static-grid compressed digest changed")
    raw_hash, raw_bytes, rows = hashlib.sha256(), 0, 0
    with gzip.open(grid_path, "rb") as stream:
        for line_number, line in enumerate(stream):
            raw_hash.update(line)
            raw_bytes += len(line)
            require(raw_bytes <= 8 * 1024 * 1024, "retained static grid exceeds its bounded raw size")
            fields = line.decode("ascii").strip().split(",")
            if line_number == 0:
                require(fields == ["fraction_index", "frequency_index", "native_real", "native_imag",
                                   "ideal_real", "ideal_imag", "complex_error"], "retained grid columns changed")
                continue
            require(len(fields) == 7, "retained grid has incomplete row")
            require((int(fields[0]), int(fields[1])) == divmod(rows, 512), "retained grid missing/reordered coordinate")
            require(all(Decimal(value).is_finite() for value in fields[2:]), "retained grid nonfinite value")
            rows += 1
    require(rows == 33280 and raw_hash.hexdigest() == grid["raw_sha256"]
            and raw_bytes == grid["raw_bytes"], "retained grid is incomplete or has changed raw bytes")
    tested_sources = report["source_sha256_after"]
    require(tested_sources == report["source_sha256_before"], "retained static-grid source drift")
    differences = [name for name, expected in tested_sources.items()
                   if not (ROOT / name).is_file() or digest(ROOT / name) != expected]
    native_sources = {name for name in tested_sources if name.startswith(("src/", "include/", "tests/"))}
    require(not native_sources.intersection(differences), "retained static-grid native inputs differ from current source")
    number(report["static_low_band"]["maximum"], "retained static low-band error", minimum=0, maximum="0.005")
    return {"status": "pass", "execution": "retained external A14 result; native grid not rerun",
            "report": identity(report_path), "grid": identity(grid_path), "rows": rows,
            "raw_sha256": raw_hash.hexdigest(), "raw_bytes": raw_bytes,
            "native_sources_match": True, "other_recorded_source_differences": differences,
            "tested_source_sha256": tested_sources,
            "maximum_low_band_error": report["static_low_band"]["maximum"],
            "maximum_full_band_error": report["static_full_band"]["maximum"],
            "scope": "low-band cubic limit and complete high-band characterization; no broadband audible-fidelity claim"}


def digest(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def identity(path):
    path = Path(path)
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": digest(path)}


def source_inventory(root=ROOT):
    paths = {root / name for name in REQUIRED_SOURCES}
    for directory in ("src", "include", "cmake", "tests/probes", "tests/reference"):
        paths.update(path for path in (root / directory).rglob("*")
                     if path.is_file() and path.suffix in (".cpp", ".h", ".hpp", ".cmake"))
    missing = sorted(str(path.relative_to(root)) for path in paths if not path.is_file())
    require(not missing, "missing qualification source inputs: " + ", ".join(missing))
    return {str(path.relative_to(root)): digest(path) for path in sorted(paths)}


def git_output(arguments, root):
    completed = subprocess.run(["git", *arguments], cwd=root, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, timeout=20, check=False)
    require(completed.returncode == 0,
            f"git {' '.join(arguments[:2])} failed: {completed.stderr.decode('utf-8', 'replace')}")
    return completed.stdout


def source_snapshot(root=ROOT):
    sources = source_inventory(root)
    status = git_output(["status", "--porcelain=v1", "--untracked-files=all", "--", *sources], root)
    patch = git_output(["diff", "--no-ext-diff", "--binary", "HEAD", "--", *sources], root)
    return {
        "git_head": git_output(["rev-parse", "HEAD"], root).decode("ascii").strip(),
        "git_tree": git_output(["rev-parse", "HEAD^{tree}"], root).decode("ascii").strip(),
        "dirty_overlay": bool(status),
        "relevant_status_porcelain": status.decode("utf-8", "surrogateescape"),
        "tracked_overlay_diff_sha256": hashlib.sha256(patch).hexdigest(),
        "tracked_overlay_diff_bytes": len(patch),
        "worktree_source_sha256": sources,
        "untracked_overlay_policy": "included by exact worktree SHA-256, even when absent from Git HEAD",
    }


def compare_source_snapshots(before, after):
    require(before["git_head"] == after["git_head"], "Git HEAD changed during qualification")
    old, new = before["worktree_source_sha256"], after["worktree_source_sha256"]
    changed = sorted(name for name in old.keys() | new.keys() if old.get(name) != new.get(name))
    require(not changed, "qualification source bytes changed: " + ", ".join(changed))


def build_facts(executable):
    """Observe generated compile commands; never infer core flags from the probe."""
    build_root = next((path for path in executable.parents
                       if (path / "CMakeCache.txt").is_file()), None)
    if build_root is None:
        return {"status": "not_available", "reason": "no ancestor CMakeCache.txt",
                "source_to_binary_attestation": False}
    cache_path = build_root / "CMakeCache.txt"
    cache = {}
    for line in cache_path.read_text(encoding="utf-8").splitlines():
        if line and not line.startswith(("#", "//")) and "=" in line and ":" in line.split("=", 1)[0]:
            key, value = line.split("=", 1)
            name = key.split(":", 1)[0]
            if (name.startswith(("CMAKE_CXX_", "CMAKE_BUILD_", "CMAKE_CONFIGURATION_"))
                    or name in ("CMAKE_GENERATOR", "CMAKE_HOME_DIRECTORY", "HAMMOND_ENABLE_SANITIZERS")):
                cache[name] = value
    result = {"status": "observed", "build_root": str(build_root),
              "cache": cache, "files": [identity(cache_path)], "compile_commands": [],
              "source_to_binary_attestation": False,
              "attestation_limit": "source and executable bytes are bound at execution; build freshness is the build-before-run target's responsibility"}
    commands_path = build_root / "compile_commands.json"
    if commands_path.is_file():
        result["files"].append(identity(commands_path))
        commands = json.loads(commands_path.read_text(encoding="utf-8"))
        for row in commands:
            source = Path(row["file"])
            if not source.is_absolute():
                source = Path(row["directory"]) / source
            if source.resolve().parent == ROOT / "src" or source.resolve() == ROOT / "tests/probes/rotary_waveform_probe.cpp":
                result["compile_commands"].append(row)
    result["has_probe_command"] = any(Path(row["file"]).name == "rotary_waveform_probe.cpp"
                                       for row in result["compile_commands"])
    result["has_required_core_commands"] = all(
        any(Path(row["file"]).name == name for row in result["compile_commands"])
        for name in ("RotaryMotion.cpp", "RotaryPropagation.cpp", "RotaryHistory.cpp",
                     "RotaryStreamingPath.cpp", "RotaryRenderer.cpp"))
    command_text = "\n".join(row.get("command", " ".join(row.get("arguments", [])))
                             for row in result["compile_commands"])
    result["unsafe_float_options"] = re.findall(r"(?i)(?:^|\s)(-ffast-math|-Ofast|/fp:fast)(?=\s|$)", command_text)
    result["explicit_float_options"] = sorted(set(re.findall(
        r"(?i)(?:^|\s)(-f(?:no-)?fast-math|-ffp-contract=\S+|/fp:\S+)(?=\s|$)", command_text)))
    result["floating_contraction_policy"] = "explicit option above, otherwise compiler default; no stronger policy inferred"
    return result


def directory_bytes(directory):
    return sum(path.stat().st_size for path in Path(directory).rglob("*") if path.is_file())


def run_native(executable, mode, directory, timeout_seconds):
    stdout_path, stderr_path = directory / "native.stdout.json", directory / "native.stderr.txt"
    result = {"argv": [str(executable), "--mode", mode], "cwd": str(directory),
              "timeout_seconds": timeout_seconds, "exit_code": None,
              "timed_out": False, "resource_limit_exceeded": None,
              "started_utc": datetime.now(timezone.utc).isoformat(), "started": False}
    started = time.monotonic()
    peak_bytes = 0
    try:
        with stdout_path.open("xb") as stdout, stderr_path.open("xb") as stderr:
            with subprocess.Popen(result["argv"], cwd=directory, stdin=subprocess.DEVNULL,
                                  stdout=stdout, stderr=stderr,
                                  start_new_session=(os.name == "posix")) as process:
                result["started"] = True
                while process.poll() is None:
                    elapsed = time.monotonic() - started
                    peak_bytes = max(peak_bytes, directory_bytes(directory))
                    if elapsed >= timeout_seconds:
                        result["timed_out"] = True
                    if max(stdout_path.stat().st_size, stderr_path.stat().st_size) > MAX_STREAM_BYTES:
                        result["resource_limit_exceeded"] = "native output stream exceeded 24 MiB"
                    elif peak_bytes > MAX_RUN_BYTES:
                        result["resource_limit_exceeded"] = "run directory exceeded 64 MiB"
                    if result["timed_out"] or result["resource_limit_exceeded"]:
                        if os.name == "posix":
                            os.killpg(process.pid, signal.SIGKILL)
                        else:
                            process.kill()
                        break
                    try:
                        process.wait(timeout=min(0.25, max(0.001, timeout_seconds - elapsed)))
                    except subprocess.TimeoutExpired:
                        pass
                result["exit_code"] = process.wait()
    except OSError as error:
        result["launch_error"] = f"{type(error).__name__}: {error}"
    result["wall_seconds"] = time.monotonic() - started
    result["finished_utc"] = datetime.now(timezone.utc).isoformat()
    result["peak_observed_run_bytes"] = max(peak_bytes, directory_bytes(directory))
    result["stdout"] = identity(stdout_path)
    result["stderr"] = identity(stderr_path)
    return result


def json_ready(value):
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, dict):
        return {key: json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(item) for item in value]
    return value


def write_json(path, value):
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(json_ready(value), ensure_ascii=True,
                                    indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def validate_process_result(result):
    require(result.get("started") is True, "native probe did not start: " + result.get("launch_error", "unknown launch failure"))
    require(not result["timed_out"], "native probe timed out; full/smoke work is incomplete")
    require(result["resource_limit_exceeded"] is None, str(result["resource_limit_exceeded"]))
    require(result["exit_code"] == 0, f"native probe returned nonzero exit {result['exit_code']}")
    require(result["stdout"]["bytes"] <= MAX_STREAM_BYTES and result["stderr"]["bytes"] <= MAX_STREAM_BYTES,
            "native stream exceeded 24 MiB")
    require(result["peak_observed_run_bytes"] <= MAX_RUN_BYTES, "run directory exceeded 64 MiB")


def validate_build_facts(facts, mode):
    require(not facts.get("unsafe_float_options"), "fast-math compiler option in core/probe build commands")
    if mode == "full":
        require(facts.get("status") == "observed" and facts.get("has_probe_command")
                and facts.get("has_required_core_commands"),
                "full qualification requires actual CMake compile commands for the probe and five rotary core sources")


def qualify(executable, mode, report_parent, timeout_seconds):
    """One native process; fresh evidence directory even on setup/process failure."""
    report_parent = report_parent.resolve()
    report_parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    run_id = f"{mode}-{stamp}-{uuid.uuid4().hex[:8]}"
    directory = report_parent / run_id
    directory.mkdir()
    started = time.monotonic()
    report = {
        "schema_version": 1, "runner_id": "rotary-waveform-acceptance-runner-v1",
        "status": "fail", "completed": False, "mode": mode, "fixture_id": FIXTURE_IDS[mode],
        "run_id": run_id, "run_directory": str(directory),
        "runner_invocation": [sys.executable, *sys.argv],
        "runner_cwd": str(Path.cwd()), "started_utc": datetime.now(timezone.utc).isoformat(),
        "source_root": str(ROOT), "failures": [], "groups": {},
        "runtime": {"python": sys.version, "python_executable": sys.executable,
                    "platform": platform.platform(), "machine": platform.machine(),
                    "byteorder": sys.byteorder},
        "retention_policy": "fresh run directory; original native stdout/stderr retained byte-for-byte; latest.json only points to the latest completed receipt",
        "decimal_encoding": "Decimal quantities in this qualification JSON are exact decimal strings; native.stdout.json preserves original native JSON numeric tokens",
        "limits": {"native_timeout_seconds": timeout_seconds, "each_stream_bytes": MAX_STREAM_BYTES,
                   "retained_run_bytes": MAX_RETAINED_BYTES, "scratch_run_bytes": MAX_RUN_BYTES},
        "source_binding_limit": "before/after source, build metadata and executable hashes bind observed bytes; generated commands do not prove a preexisting executable was freshly compiled; use the build-before-run CMake target",
        "scope": "native R4 waveform and exact partition qualification plus selected reference and retained static-grid checks",
        "separate_gates": {"transaction_lifecycle": "not_run", "R5_audible_policy": "not_run",
                           "R6_device_deadlines": "not_run", "physical_fidelity": "not_run"},
    }

    def stage(name, action):
        try:
            result = action()
            report["groups"][name] = "pass"
            return result
        except Exception as error:
            report["groups"][name] = "fail"
            report["failures"].append({"stage": name, "type": type(error).__name__, "message": str(error)})
            return None

    before = stage("source_before", source_snapshot)
    report["source_before"] = before

    def admit_executable():
        require(executable is not None, "missing probe: set HAMMOND_ROTARY_WAVEFORM_PROBE_EXECUTABLE or --probe")
        require(executable.is_file(), f"native probe not found: {executable}")
        return identity(executable)

    binary_before = stage("executable_before", admit_executable)
    report["executable_before"] = binary_before
    build_before = None
    if binary_before:
        build_before = stage("build_metadata_before", lambda: build_facts(executable))
        if build_before is not None:
            stage("build_options", lambda: validate_build_facts(build_before, mode))
    report["build_before"] = build_before
    native = None
    if not report["failures"]:
        native = stage("native_process_capture", lambda: run_native(executable, mode, directory, timeout_seconds))
        report["native_process"] = native
        if native:
            stage("native_process_exit", lambda: validate_process_result(native))
            parsed = stage("native_json", lambda: parse_probe_json((directory / "native.stdout.json").read_bytes()))
            if parsed is not None:
                report["native_precision_environment"] = parsed.get("precision_environment")
                report["native_report_status"] = parsed.get("status")
                report["native_totals"] = parsed.get("totals")
                report["native_resource_observations"] = parsed.get("resource_observations")
                summary = stage("native_report_admission", lambda: validate_report(parsed, mode))
                report["native_admission"] = summary
                if summary is not None:
                    checks = stage("selected_decimal_crosscheck", lambda: selected_decimal_checks(parsed))
                    report["selected_decimal_crosscheck"] = checks
                    if checks is not None and checks["status"] != "pass":
                        report["groups"]["selected_decimal_crosscheck"] = "fail"
                        report["failures"].append({"stage": "selected_decimal_crosscheck",
                                                  "message": "one or more frozen high-precision budgets failed"})
                    report["retained_static_grid"] = stage("retained_static_grid", retained_static_grid)
    else:
        report["groups"]["native_process_capture"] = "not_run"
    after = stage("source_after", source_snapshot)
    report["source_after"] = after
    if before is not None and after is not None:
        stage("source_stability", lambda: compare_source_snapshots(before, after))
    if binary_before:
        binary_after = stage("executable_after", lambda: identity(executable))
        report["executable_after"] = binary_after
        if binary_after is not None:
            stage("executable_stability", lambda: require(
                (binary_before["bytes"], binary_before["sha256"]) ==
                (binary_after["bytes"], binary_after["sha256"]), "native executable changed during qualification"))
    if build_before is not None:
        build_after = stage("build_metadata_after", lambda: build_facts(executable))
        report["build_after"] = build_after
        if build_after is not None:
            stage("build_metadata_stability", lambda: require(build_before == build_after,
                                                             "generated build inputs changed during qualification"))
    report["completed"] = native is not None and report["groups"].get("native_report_admission") == "pass"
    report["status"] = "fail" if report["failures"] else "pass"
    report["wall_seconds"] = time.monotonic() - started
    report["finished_utc"] = datetime.now(timezone.utc).isoformat()
    report_path = directory / "qualification.json"
    write_json(report_path, report)
    retained_bytes = directory_bytes(directory)
    report["retained_bytes_observed_before_final_receipt"] = retained_bytes
    if retained_bytes > MAX_RETAINED_BYTES:
        report["status"] = "fail"
        report["failures"].append({"stage": "retained_size", "message": "retained evidence exceeded 32 MiB; files were not truncated"})
    write_json(report_path, report)
    write_json(report_parent / "latest.json", {
        "schema_version": 1, "mode": mode, "status": report["status"], "run_id": run_id,
        "qualification_json": str(report_path), "qualification_sha256": digest(report_path),
        "finished_utc": report["finished_utc"],
    })
    return report, report_path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("smoke", "full"), default="smoke")
    parser.add_argument("--probe", type=Path, default=os.environ.get("HAMMOND_ROTARY_WAVEFORM_PROBE_EXECUTABLE"))
    parser.add_argument("--report-dir", type=Path, default=os.environ.get("HAMMOND_ROTARY_WAVEFORM_REPORT_DIR"))
    parser.add_argument("--timeout-seconds", type=float)
    parser.add_argument("--self-test", action="store_true",
                        help="run report-admission mutation tests only; never qualifies a native waveform")
    arguments = parser.parse_args(argv)
    if arguments.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(ReportAdmissionTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        return 0 if result.wasSuccessful() else 1
    timeout = arguments.timeout_seconds if arguments.timeout_seconds is not None else (1500 if arguments.mode == "full" else 90)
    if not math.isfinite(timeout) or timeout <= 0:
        parser.error("--timeout-seconds must be finite and positive")
    executable = Path(arguments.probe).expanduser().resolve() if arguments.probe else None
    parent = arguments.report_dir or ((executable.parent if executable else ROOT.parent) / "rotary-waveform" / arguments.mode)
    try:
        report, path = qualify(executable, arguments.mode, Path(parent).expanduser(), timeout)
    except (OSError, ValueError) as error:
        print(f"rotary waveform runner failed to retain a qualification receipt: {error}", file=sys.stderr)
        return 1
    print(json.dumps({"status": report["status"], "mode": arguments.mode,
                      "qualification_json": str(path), "wall_seconds": report["wall_seconds"],
                      "failures": report["failures"]}, allow_nan=False))
    return 0 if report["status"] == "pass" else 1


def protocol_fixture(mode):
    """Synthetic schema-only fixture for mutations, never native qualification.

    Field layout follows A19's observed schema-v1 smoke serialization.  The
    deliberately artificial trajectory is never sent to qualify() or the
    selected Decimal gate, and cannot stand in for a native result.
    """
    def bits(value):
        return struct.pack(">d", float(value)).hex()

    def position(frame, fraction=0):
        return {"frame": frame, "fraction": fraction, "fraction_bits": bits(fraction)}

    def motion(phase=0, speed=0):
        return {"phase_rad": phase, "phase_bits": bits(phase), "turns": 0,
                "speed_rad_s": speed, "speed_bits": bits(speed)}

    def path():
        return {"delay_s": 0.004, "distance_m": 1.372, "distance_gain": 1 / 1.372,
                "emission_phase_rad": 0, "radial_speed_m_s": 0, "frequency_ratio": 1,
                "residual_s": 0, "iterations": 1}

    def no_failures():
        return {"count": 0, "first_frame": -1, "last_frame": -1, "complete": True}

    def precision(digits, digits10, max_digits10, size):
        return {"radix": 2, "digits": digits, "digits10": digits10,
                "max_digits10": max_digits10, "sizeof": size, "is_iec559": True}

    totals = expected_totals(mode)
    result = {
        "schema_version": 1, "status": "pass", "completed": True, "mode": mode,
        "fixture_id": FIXTURE_IDS[mode], "experiment_id": FIXTURE_IDS[mode],
        "reference_id": REFERENCE_ID, "contract_id": CONTRACT_ID,
        "renderer_contract_id": "rotary-renderer-v1",
        "model_id": "nominal-effective-mouth-rotary-v1",
        "full_duration_seconds": 10 if mode == "full" else None,
        "required_rate_count": 4, "partition_count": 6, "required_rates": list(RATES),
        "fixed_blocks": [1, 7, 64, 257, 4096], "irregular_blocks": PATTERNS["irregular_v1"],
        "required_reference_frames": totals["reference_frames"],
        "required_native_frames": totals["native_frames"], "totals": totals,
        "exception": "", "failures": [],
        "precision_environment": {
            "status": "pass", "fast_math_enabled": False, "rounding_is_to_nearest": True,
            "rounding_mode": 0, "compiler": "schema fixture", "standard_library": "schema fixture",
            "platform": "schema fixture", "build_configuration": "schema fixture",
            "build_flags": "schema fixture", "cplusplus": 202002,
            "double": precision(53, 15, 17, 8), "long_double": precision(64, 18, 21, 16),
            "wider_than_double": True},
        "fixture": {"synthetic_engineering_fixture": True, "rotors": [],
                    "microphones_m": [list(value) for value in MICROPHONES],
                    "sound_speed_m_s": 343, "reference_distance_m": 1},
        "provenance": {"sha256_self_check_passed": True, "sha256_self_check_vectors": 3,
                       "stream_encoding": "frame_interleaved_little_endian_binary64"},
        "signal": {"seed_hex": "726f746172792d34", "input_frame_shift_in_sample_rates": 0 if mode == "full" else 2,
                   "negative_history": "zero", "input_channel_order": ["horn", "drum"],
                   "output_channel_order": ["left", "right"]},
        "comparison_policy": {
            "algorithmic_latency_frames": 2, "observation": "(n-2)/Fs",
            "normalized_maximum_limit": WAVEFORM_BUDGET,
            "reference_residual_target_s": Decimal("5e-15"), "reference_residual_limit_s": REFERENCE_RESIDUAL,
            "native_residual_limit_s": NATIVE_RESIDUAL, "native_iteration_limit": 48,
            "fitted_gain": False, "fitted_time_shift": False, "clipping": False,
            "frequency_remapping": False, "reference_to_native_path": [0, 2, 1, 3]},
        "resource_observations": {
            "max_canonical_audio_bytes": 16 * max(frames_for(mode, rate) for rate in RATES),
            "canonical_audio_limit_bytes": 30720000, "full_waveform_buffers": 1,
            "reference_audio_buffered": False, "wall_seconds": 1,
            "sizeof_waveform_history": 131112, "sizeof_motion_frame_history": 917608,
            "sizeof_renderer_state": 248, "sizeof_renderer_diagnostics": 368},
        "rates": [],
    }
    for rotor, values in enumerate(ROTORS):
        result["fixture"]["rotors"].append({
            "rotor": rotor, "origin_m": list(values["origin"]), "radius_m": values["radius"],
            "slow_rad_s": values["slow"], "fast_rad_s": values["fast"], "tau_up_s": values["up"],
            "tau_down_s": values["down"], "direction": values["direction"],
            "initial_phase_rad": values["phase"], "initial_speed_rad_s": values["speed"],
            "initial_command": "chorale"})
    for rate in RATES:
        frames, events = frames_for(mode, rate), expected_events(rate, mode)
        commands = ["chorale", "chorale"]
        for event in events:
            commands[event["rotor"]] = event["command"]
        state = {"prepared": True, "sample_rate": rate, "frame": frames, "max_frame": 86400 * rate,
                 "commands": commands, "motion": [motion(), motion()],
                 "epoch_initial": [motion(value["phase"], value["speed"]) for value in ROTORS],
                 "segments": [{"anchor_frame": frames, "initial": motion(),
                               "target_rad_s": value["fast" if commands[rotor] == "tremolo" else "slow"],
                               "tau_s": value["up"], "direction": value["direction"]}
                              for rotor, value in enumerate(ROTORS)]}
        diagnostics = {"path_order": "rotor_major", "has_rendered_sample": True,
                       "last_input_frame": frames - 1, "last_observation": position(frames - 3),
                       "max_solver_residual_s": 0, "max_solver_iterations": 1,
                       "last_paths": [path() for _ in range(4)],
                       "last_emissions": [position(frames - 1000) for _ in range(4)]}
        row = {"rate": rate, "status": "pass", "completed": True, "required_frames": frames,
               "reference_frames": frames, "reference_scalar_comparisons": 2 * frames,
               "duration_seconds": Decimal(frames) / rate, "canonical_audio_bytes": 16 * frames,
               "events": events, "event_count": len(events), "channels": [], "signal_regions": [],
               "partitions": [], "reference_audio_sha256": "a" * 64,
               "reference_solver": {"path_solutions": 4 * frames, "max_residual_s": 0,
                                    "max_evaluations": 1, "max_contraction_steps": 0, "max_bisections": 0},
               "selected_traces": [], "final_reference_motion": [],
               "reference_convergence": {"difference_limit_s": Decimal("2e-14"),
                                         "contractive_target_s": Decimal("5e-15"),
                                         "bisection_target_s": Decimal("1e-16"),
                                         "pair_count": 4 * len(convergence_frames(rate, mode)), "pairs": []}}
        for channel in range(2):
            normalization = sum(1 / math.sqrt(
                (math.hypot(*(MICROPHONES[channel][axis] - value["origin"][axis] for axis in range(2)))
                 - value["radius"]) ** 2 + (MICROPHONES[channel][2] - value["origin"][2]) ** 2)
                for value in ROTORS)
            row["channels"].append({"channel": channel, "status": "pass", "samples": frames,
                "normalization_G": normalization, "maximum_absolute_error": 0, "rms_absolute_error": 0,
                "maximum_normalized_error": 0, "rms_normalized_error": 0,
                "worst_frame": 0, "worst_actual": 0, "worst_reference": 0, "failures": no_failures()})
        counts = [2 * rate, 7 * rate - rate // 8, rate + rate // 8] if mode == "full" else [0, frames, 0]
        for index, (identifier, count) in enumerate(zip(("impulses", "bounded_input", "explicit_silence"), counts)):
            nonzero = 2 if index == 0 and count else (1 if index == 1 else 0)
            row["signal_regions"].append({"id": identifier, "required": mode == "full" or index == 1,
                "frames": count, "input_nonzero": [nonzero] * 2, "actual_nonzero": [nonzero] * 2,
                "reference_nonzero": [nonzero] * 2, "nonzero_comparison_count": [nonzero] * 2})
        for index, (identifier, pattern) in enumerate(PATTERNS.items()):
            part = {"id": identifier, "status": "pass", "completed": True, "baseline": index == 0,
                    "pattern": list(pattern), "native_frames": frames, "native_path_solutions": 4 * frames,
                    "events_consumed": len(events), "process_calls": frames, "max_block_observed": pattern[0],
                    "max_native_residual_s": 0, "max_native_iterations": 1,
                    "input_sha256": "b" * 64, "audio_sha256": "c" * 64,
                    "final_state": copy.deepcopy(state), "final_diagnostics": copy.deepcopy(diagnostics),
                    "audio_bit_comparison": [{"channel": channel, "compared_samples": frames if index else 0,
                                             "equal_samples": frames if index else 0,
                                             "max_absolute_difference": 0, "failures": no_failures()}
                                            for channel in range(2)]}
            for key, count in (("final_state_comparison", 32), ("final_diagnostics_comparison", 46)):
                part[key] = {"field_count": count if index else 0, "match": True, "mismatched_fields": [],
                             "floating_comparison": "binary64_bits", "compares_struct_padding": False}
            row["partitions"].append(part)
        for rotor in range(2):
            row["final_reference_motion"].append({"rotor": rotor, "passed": True, "command_match": True,
                "angle_rad": 0, "speed_rad_s": 0, "angle_limit_rad": Decimal("5e-12"),
                "speed_limit_rad_s": Decimal("5e-12"), "angle_error_rad": 0, "speed_error_rad_s": 0})
        for frame in selected_frames(rate, mode):
            for channel in range(2):
                for rotor in range(2):
                    row["selected_traces"].append({"frame": frame, "observation_frame": frame - 2,
                        "rotor": rotor, "channel": channel, "reference_path_index": 2 * channel + rotor,
                        "native_path_index": 2 * rotor + channel, "has_native": True,
                        "delay_s": 0.004, "distance_m": 1.372, "distance_gain": 1 / 1.372,
                        "emission_frame": frame - 1000, "fraction": 0, "angle_rad": 0, "speed_rad_s": 0,
                        "frequency_ratio": 1, "residual_s": 0, "evaluations": 1,
                        "native_path": path(), "native_emission": position(frame - 1000)})
        for frame in convergence_frames(rate, mode):
            for channel in range(2):
                for rotor in range(2):
                    row["reference_convergence"]["pairs"].append({
                        "frame": frame, "rotor": rotor, "channel": channel,
                        "reference_path_index": 2 * channel + rotor, "passed": True,
                        "contractive_delay_s": Decimal("0.004"), "bisection_delay_s": Decimal("0.004"),
                        "difference_s": 0, "contractive_residual_s": 0, "bisection_residual_s": 0,
                        "contractive_evaluations": 1, "bisection_evaluations": 1})
        result["rates"].append(row)
    return result


class ReportAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.fixture = protocol_fixture("smoke")

    def binary64_fixture(self):
        """Schema-only fixture serialized at the actual 53-bit report precision."""
        report = copy.deepcopy(self.fixture)
        environment = report["precision_environment"]
        environment["long_double"] = copy.deepcopy(environment["double"])
        environment["wider_than_double"] = False
        for row in report["rates"]:
            for pair in row["reference_convergence"]["pairs"]:
                for key in ("contractive_delay_s", "bisection_delay_s"):
                    pair[key] = Decimal(format(float(pair[key]), ".17g"))
        return report

    def test_actual_hosted_binary64_cancellation(self):
        # Exact tokens shared by the macOS arm64 and Windows MSVC artifacts
        # 14136740173 / 14135784437, run 43651384583 at published 487064d.
        report = self.binary64_fixture()
        channel = report["rates"][0]["channels"][0]
        channel.update(parse_probe_json(b'''{
            "normalization_G":1.3017406088759063,
            "maximum_absolute_error":3.3640093488607192e-10,
            "rms_absolute_error":6.9060749589231244e-11,
            "maximum_normalized_error":2.5842393837322525e-10,
            "rms_normalized_error":5.3052619791025582e-11,
            "worst_actual":-0.1490543302277674,
            "worst_reference":-0.14905433056416834}'''))
        pair = report["rates"][0]["reference_convergence"]["pairs"][0]
        pair.update(parse_probe_json(b'''{
            "contractive_delay_s":0.0046545491618496812,
            "bisection_delay_s":0.0046545491618498035,
            "difference_s":1.222980050563649e-16}'''))
        # Preserve the original failures; the repair does not widen either
        # decimal consistency floor or any waveform/solver acceptance budget.
        for actual, reference, difference, tolerance in (
            (channel["worst_actual"], channel["worst_reference"], channel["maximum_absolute_error"], "1e-18"),
            (pair["contractive_delay_s"], pair["bisection_delay_s"], pair["difference_s"], "1e-22"),
        ):
            with self.subTest(tolerance=tolerance), self.assertRaises(AdmissionError):
                assert_close(abs(actual - reference), difference, tolerance, "original decimal subtraction")
        self.assertEqual(validate_report(report, "smoke")["status"], "pass")

    def test_binary64_difference_rejects_changed_and_coarse_tokens(self):
        precision = self.fixture["precision_environment"]["double"]
        actual, reference, recorded = map(Decimal, (
            "-0.1490543302277674", "-0.14905433056416834", "3.3640093488607192e-10"))
        assert_recorded_difference(actual, reference, recorded, precision, "1e-18", "actual hosted maximum")
        # A single result ULP is far below the old 1e-18 consistency floor,
        # but must now fail.  Every mutated token is still full precision.
        for index in range(3):
            values = [actual, reference, recorded]
            values[index] = Decimal(format(math.nextafter(float(values[index]), math.inf), ".17g"))
            with self.subTest(changed_operand=index), self.assertRaises(AdmissionError):
                assert_recorded_difference(*values, precision, "1e-18", "changed binary64 subtraction")
        for coarse in (Decimal("-0.149054330227767"), Decimal("-0.1490543")):
            with self.subTest(coarse=coarse), self.assertRaises(AdmissionError):
                assert_recorded_difference(coarse, reference, recorded, precision, "1e-18", "coarse token")
        # Legal short tokens are exact values, not permission for a wider bin.
        assert_recorded_difference(Decimal("0.5"), Decimal("0.25"), Decimal("0.25"),
                                   precision, "1e-18", "exact short tokens")
        for invalid in (Decimal("NaN"), Decimal("Infinity"), float("nan")):
            with self.subTest(nonfinite=invalid), self.assertRaises(AdmissionError):
                assert_recorded_difference(invalid, reference, recorded, precision, "1e-18", "nonfinite")

    def test_binary64_convergence_rejects_one_ulp_change(self):
        report = self.binary64_fixture()
        pair = report["rates"][0]["reference_convergence"]["pairs"][0]
        pair.update(parse_probe_json(b'''{
            "contractive_delay_s":0.0046545491618496812,
            "bisection_delay_s":0.0046545491618498035,
            "difference_s":1.222980050563649e-16}'''))
        self.assertEqual(validate_report(report, "smoke")["status"], "pass")
        pair["difference_s"] = Decimal(format(math.nextafter(float(pair["difference_s"]), math.inf), ".17g"))
        with self.assertRaisesRegex(AdmissionError, "inconsistent recorded binary64 difference"):
            validate_report(report, "smoke")

    def test_binary64_precision_metadata_cannot_inflate_allowance(self):
        for name in ("double", "long_double"):
            for key, value in (("radix", 10), ("digits10", 14), ("max_digits10", 6),
                               ("max_digits10", 21), ("is_iec559", False)):
                report = self.binary64_fixture()
                report["precision_environment"][name][key] = value
                with self.subTest(type=name, field=key, value=value), self.assertRaises(AdmissionError):
                    validate_report(report, "smoke")

    def test_wider_precision_keeps_original_difference_floors(self):
        precision = self.fixture["precision_environment"]["long_double"]
        for tolerance in ("1e-18", "1e-22"):
            floor = Decimal(tolerance)
            assert_recorded_difference(Decimal("0.5"), Decimal("0.5"), floor,
                                       precision, tolerance, "unchanged wider precision floor")
            with self.subTest(tolerance=tolerance), self.assertRaises(AdmissionError):
                assert_recorded_difference(Decimal("0.5"), Decimal("0.5"), floor * Decimal("1.01"),
                                           precision, tolerance, "beyond wider precision floor")

    def test_complete_schema_fixture_for_each_mode(self):
        for mode in ("smoke", "full"):
            with self.subTest(mode=mode):
                self.assertEqual(validate_report(protocol_fixture(mode), mode)["status"], "pass")

    def test_missing_duplicate_rate_partition_and_channel_fail(self):
        cases = [
            ("missing rate", lambda row: row["rates"].pop()),
            ("duplicate rate", lambda row: row["rates"].__setitem__(1, copy.deepcopy(row["rates"][0]))),
            ("missing partition", lambda row: row["rates"][0]["partitions"].pop()),
            ("duplicate partition", lambda row: row["rates"][0]["partitions"].__setitem__(1, copy.deepcopy(row["rates"][0]["partitions"][0]))),
            ("missing channel", lambda row: row["rates"][0]["channels"].pop()),
            ("missing trace", lambda row: row["rates"][0]["selected_traces"].pop()),
            ("missing convergence pair", lambda row: row["rates"][0]["reference_convergence"]["pairs"].pop()),
        ]
        self.assert_mutations_rejected(cases)

    def test_counts_modes_failures_and_nonfinite_budgets_fail(self):
        cases = [
            ("wrong frames", lambda row: row["rates"][0].__setitem__("reference_frames", SMOKE_FRAMES - 1)),
            ("wrong total", lambda row: row["totals"].__setitem__("native_frames", 1)),
            ("wrong mode", lambda row: row.__setitem__("mode", "full")),
            ("wrong identity", lambda row: row.__setitem__("fixture_id", FIXTURE_IDS["full"])),
            ("incomplete", lambda row: row.__setitem__("completed", False)),
            ("failed status", lambda row: row.__setitem__("status", "fail")),
            ("failed partition", lambda row: row["rates"][0]["partitions"][1].__setitem__("status", "fail")),
            ("NaN maximum", lambda row: row["rates"][0]["channels"][0].__setitem__("maximum_normalized_error", float("nan"))),
            ("infinite RMS", lambda row: row["rates"][0]["channels"][0].__setitem__("rms_absolute_error", Decimal("Infinity"))),
            ("budget exceeded", lambda row: row["rates"][0]["channels"][0].__setitem__("maximum_normalized_error", Decimal("2.1e-5"))),
            ("budget relaxed", lambda row: row["comparison_policy"].__setitem__("normalized_maximum_limit", Decimal("3e-5"))),
            ("bool count", lambda row: row.__setitem__("required_rate_count", True)),
            ("silent harness", lambda row: row["rates"][0]["signal_regions"][1].__setitem__("nonzero_comparison_count", [0, 0])),
            ("fast math", lambda row: row["precision_environment"].__setitem__("fast_math_enabled", True)),
            ("false wider claim", lambda row: row["precision_environment"].__setitem__("wider_than_double", False)),
        ]
        self.assert_mutations_rejected(cases)

    def test_exact_replay_events_state_diagnostics_and_traces_fail_closed(self):
        cases = [
            ("short direct comparison", lambda row: row["rates"][0]["partitions"][1]["audio_bit_comparison"][0].__setitem__("compared_samples", SMOKE_FRAMES - 1)),
            ("digest only", lambda row: row["rates"][0]["partitions"][1].pop("audio_bit_comparison")),
            ("state fields missing", lambda row: row["rates"][0]["partitions"][1]["final_state_comparison"].__setitem__("field_count", 31)),
            ("diagnostic fields missing", lambda row: row["rates"][0]["partitions"][1]["final_diagnostics_comparison"].__setitem__("field_count", 45)),
            ("input digest differs", lambda row: row["rates"][0]["partitions"][1].__setitem__("input_sha256", "d" * 64)),
            ("audio digest differs", lambda row: row["rates"][0]["partitions"][1].__setitem__("audio_sha256", "d" * 64)),
            ("final command lost", lambda row: row["rates"][0]["partitions"][1]["final_state"]["commands"].__setitem__(0, "tremolo")),
            ("final state drift", lambda row: row["rates"][0]["partitions"][1]["final_state"]["motion"][0].__setitem__("turns", 1)),
            ("diagnostic drift", lambda row: row["rates"][0]["partitions"][1]["final_diagnostics"].__setitem__("max_solver_iterations", 2)),
            ("tie reordered", lambda row: row["rates"][0]["events"].reverse()),
            ("boundary command missing", lambda row: row["rates"][0]["events"].pop()),
            ("observation moved", lambda row: row["rates"][0]["selected_traces"][0].__setitem__("observation_frame", 0)),
            ("root target failed", lambda row: row["rates"][0]["reference_convergence"]["pairs"][0].__setitem__("bisection_residual_s", Decimal("2e-16"))),
        ]
        self.assert_mutations_rejected(cases)

    def assert_mutations_rejected(self, cases):
        for name, mutation in cases:
            with self.subTest(mutation=name):
                report = copy.deepcopy(self.fixture)
                mutation(report)
                with self.assertRaises(AdmissionError):
                    validate_report(report, "smoke")

    def test_json_requires_one_record_duplicate_free_finite_numbers(self):
        for raw in (b"", b"{}\n{}", b'{"x":1,"x":2}', b'{"x":NaN}',
                    b'{"x":Infinity}', b'{"x":-Infinity}', b'{"x":1e1000000000}', b"\xff"):
            with self.subTest(raw=raw[:50]):
                with self.assertRaises((AdmissionError, ValueError)):
                    parse_probe_json(raw)
        parsed = parse_probe_json(b'{"trace":0.123456789012345678901}')
        self.assertEqual(parsed["trace"], Decimal("0.123456789012345678901"))

    def test_source_receipts_detect_changed_inputs(self):
        before = {"git_head": "a" * 40, "worktree_source_sha256": {"src/RotaryRenderer.cpp": "b" * 64}}
        compare_source_snapshots(before, copy.deepcopy(before))
        for field in ("changed", "added", "removed", "head"):
            after = copy.deepcopy(before)
            if field == "changed":
                after["worktree_source_sha256"]["src/RotaryRenderer.cpp"] = "c" * 64
            elif field == "added":
                after["worktree_source_sha256"]["src/new.cpp"] = "c" * 64
            elif field == "removed":
                after["worktree_source_sha256"].clear()
            else:
                after["git_head"] = "c" * 40
            with self.subTest(field=field), self.assertRaises(AdmissionError):
                compare_source_snapshots(before, after)

    def test_nonzero_timeout_and_missing_native_cannot_pass(self):
        good = {"started": True, "timed_out": False, "resource_limit_exceeded": None,
                "exit_code": 0, "stdout": {"bytes": 2}, "stderr": {"bytes": 0},
                "peak_observed_run_bytes": 2}
        validate_process_result(good)
        for key, value in (("started", False), ("timed_out", True), ("exit_code", 7),
                           ("exit_code", -9), ("resource_limit_exceeded", "over budget")):
            invalid = {**good, key: value}
            with self.subTest(key=key, value=value), self.assertRaises(AdmissionError):
                validate_process_result(invalid)

    def test_native_capture_retains_missing_executable_failure(self):
        with tempfile.TemporaryDirectory(prefix="rotary-waveform-admission-") as value:
            directory = Path(value)
            result = run_native(directory / "missing-native-probe", "smoke", directory, 1)
            self.assertFalse(result["started"])
            self.assertIsNone(result["exit_code"])
            self.assertTrue((directory / "native.stdout.json").is_file())
            self.assertTrue((directory / "native.stderr.txt").is_file())
            with self.assertRaises(AdmissionError):
                validate_process_result(result)

    def test_full_requires_recorded_actual_build_options(self):
        with self.assertRaises(AdmissionError):
            validate_build_facts({"status": "not_available"}, "full")
        validate_build_facts({"status": "not_available"}, "smoke")
        with self.assertRaises(AdmissionError):
            validate_build_facts({"unsafe_float_options": ["-ffast-math"]}, "smoke")


if __name__ == "__main__":
    sys.exit(main())
