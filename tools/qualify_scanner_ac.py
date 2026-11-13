#!/usr/bin/env python3
"""Compare the native scanner recurrence/process path with independent nodal AC.

The frozen grid and budgets live in SCANNER_NUMERICAL_CONTRACT.md. This report
retains same-hertz failures separately from bilinear-warped discrete parity.
Only the standard library and the independently stamped AC reference are used.
"""
from __future__ import annotations

import argparse
import cmath
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import stat
import subprocess
import sys
import tempfile
from typing import Any, Callable

from compile_scanner_line import compile_profile, load_profile_with_digest
from scanner_ac_reference import dc_reference, prepare_network, solve_ac

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROFILE = ROOT / "data/scanner/atlas-late-b3-nominal-v1.json"
HOST_RATES = (44100, 48000, 96000)
MULTIPLIERS = (1, 2, 4, 8, 16)
MODES = ("vibrato", "chorus")
PROCESS_FREQUENCIES = (100.0, 997.0, 5000.0, 7000.0)
STARTUP_SECONDS = (0.125, 0.25, 0.5, 1.0)
CHANNELS = tuple(f"v{k}" for k in range(1, 20)) + ("return", "input_current_times_15000_ohms")
MODEL_ID = "atlas-late-b3-nominal-line-v1"
REALIZATION_ID = "scaled-physical-trapezoidal-scanner-line-v1"
QUALIFICATION_ID = "scanner-native-independent-ac-parity-v1"
CONTRACT_ID = "scanner-numerics-v1"
FROZEN_CONTRACT_SHA256 = "3999a3a409d397401e135e8285704092bad130911468802370bf6da404d58ff9"
RESIDUAL_LIMIT = 1e-9
PHASE_FLOOR = 1e-4
MAX_REPORT_BYTES = 128 * 1024 * 1024
MAX_PROBE_BYTES = 8 * 1024 * 1024
SOURCE_FILES = (
    "include/hammond/ScannerLine.h", "include/hammond/Types.h", "src/ScannerLine.cpp",
    "tools/scanner_line_probe.cpp", "tools/CliArguments.h", "include/hammond/detail/Decimal.h",
    "tools/compile_scanner_line.py",
    "tools/scanner_ac_reference.py", "tools/qualify_scanner_ac.py",
    "docs/SCANNER_NUMERICAL_CONTRACT.md", "data/scanner-line.schema.json",
)


class QualificationError(ValueError):
    """Rejected inputs, untrustworthy output or an incomplete computation."""


def _number(value: Any, name: str, low: float = -math.inf,
            high: float = math.inf) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise QualificationError(f"{name} must be a finite number")
    try:
        result = float(value)
    except (OverflowError, ValueError) as exc:
        raise QualificationError(f"{name} must be a finite number") from exc
    if not math.isfinite(result) or not low <= result <= high:
        raise QualificationError(f"{name} must be finite and within [{low}, {high}]")
    return result


def frequency_grid() -> tuple[float, ...]:
    """Literal contract grid; do not infer it from the implementation's bins."""
    geometric = [round(20.0 * 1000.0 ** (j / 120.0), 12) for j in range(121)]
    geometric[0], geometric[-1] = 20.0, 20000.0
    return tuple(sorted(set(geometric) | set(float(f) for f in range(5000, 9001, 25))))


def _grid(values: Any, name: str, low: float, high: float) -> tuple[float, ...]:
    if not isinstance(values, (tuple, list)) or not 1 <= len(values) <= 1024:
        raise QualificationError(f"{name} requires 1..1024 numbers")
    numbers = tuple(_number(value, name, low, high) for value in values)
    if any(left >= right for left, right in zip(numbers, numbers[1:])):
        raise QualificationError(f"{name} must be strictly increasing without duplicates")
    return numbers


def _selection(values: Any, allowed: tuple[Any, ...], name: str) -> tuple[Any, ...]:
    if not isinstance(values, (tuple, list)) or not values or len(values) > len(allowed):
        raise QualificationError(f"invalid {name} selection")
    if any(isinstance(value, bool) or value not in allowed for value in values):
        raise QualificationError(f"unsupported {name}")
    if len(set(values)) != len(values):
        raise QualificationError(f"duplicate {name}")
    return tuple(values)


def _complex(value: Any, name: str) -> complex:
    if not isinstance(value, list) or len(value) != 2:
        raise QualificationError(f"{name} must contain [real, imaginary]")
    return complex(_number(value[0], name), _number(value[1], name))


def _pair(value: complex) -> list[float]:
    return [float(value.real), float(value.imag)]


def _vectors(record: Any) -> tuple[complex, ...]:
    if not isinstance(record, dict):
        raise QualificationError("probe transfer must be an object")
    taps = record.get("taps")
    if not isinstance(taps, list) or len(taps) != 19:
        raise QualificationError("probe transfer requires all nineteen signed taps")
    return (tuple(_complex(value, "tap") for value in taps)
            + (_complex(record.get("return_gain"), "return_gain"),
               15000.0 * _complex(record.get("input_admittance"), "input_admittance")))


def _oracle_vectors(record: dict[str, Any]) -> tuple[complex, ...]:
    return (tuple(complex(value) for value in record["taps"])
            + (complex(record["return_voltage"]), 15000.0 * complex(record["input_current"])))


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise QualificationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise QualificationError(f"nonfinite JSON number: {value}")


def run_probe(probe: Path, operation: str, rate: int, mode: str,
              options: list[str], authoring_sha256: str) -> dict[str, Any]:
    """Invoke a bounded native operation and validate its electrical identity."""
    command = [str(probe), "--operation", operation, "--sample-rate", str(rate),
               "--mode", mode, *options]
    try:
        result = subprocess.run(command, capture_output=True, check=False, timeout=180)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise QualificationError(f"native probe did not complete: {exc}") from exc
    if len(result.stdout) > MAX_PROBE_BYTES or len(result.stderr) > MAX_PROBE_BYTES:
        raise QualificationError("native probe output exceeded 8 MiB")
    if result.returncode:
        diagnostic = result.stderr.decode("utf-8", errors="replace")[:2000]
        raise QualificationError(f"native probe exited {result.returncode}: {diagnostic}")
    try:
        record = json.loads(result.stdout.decode("utf-8"), object_pairs_hook=_unique_object,
                            parse_constant=_reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise QualificationError(f"invalid native probe JSON: {exc}") from exc
    if not isinstance(record, dict):
        raise QualificationError("native probe JSON must be an object")
    for key, expected in (("schema_version", 1), ("model_id", MODEL_ID),
                          ("realization_id", REALIZATION_ID), ("authoring_sha256", authoring_sha256),
                          ("sample_rate_hz", rate), ("mode", mode)):
        if record.get(key) != expected or isinstance(record.get(key), bool):
            raise QualificationError(f"native probe identity mismatch for {key}")
    if record.get("probe_id") != "scanner-line-probe-v1" or record.get("operation") != operation:
        raise QualificationError("native probe operation identity does not match")
    if record.get("clock_convention") != ("previous_endpoint_at_minus_one_sample;"
            "first_processed_knot_at_zero;frame_counts_completed_intervals"):
        raise QualificationError("native probe endpoint convention does not match")
    method = {"response": "prepared_discrete_recurrence_solve",
              "sine": "actual_process_frame_cos_sin_constant_least_squares"}.get(operation)
    if method is None or record.get("measurement_method") != method:
        raise QualificationError("native probe measurement method does not match")
    _number(record.get("preparation_residual"), "preparation residual", 0.0, RESIDUAL_LIMIT)
    return record


def compare_vectors(actual: tuple[complex, ...], expected: tuple[complex, ...],
                    absolute: float, relative: float) -> dict[str, Any]:
    if len(actual) != len(expected) or not actual:
        raise QualificationError("comparison vectors have incompatible shapes")
    errors, limits, ratios = [], [], []
    for found, wanted in zip(actual, expected):
        if not all(math.isfinite(part) for part in (found.real, found.imag, wanted.real, wanted.imag)):
            raise QualificationError("comparison contains nonfinite complex data")
        error = abs(found - wanted)
        limit = absolute + relative * abs(wanted)
        errors.append(error)
        limits.append(limit)
        ratios.append(error / limit)
    return {"absolute_error": errors, "limit": limits, "error_over_limit": ratios,
            "failed_channels": [CHANNELS[index] for index, ratio in enumerate(ratios) if ratio > 1.0]}


def phase_diagnostics(frequencies: tuple[float, ...], native: list[tuple[complex, ...]],
                      reference: list[tuple[complex, ...]]) -> list[dict[str, Any]]:
    """Pairwise eligible segments; never bridge a null or fit a phase offset."""
    if len(frequencies) != len(native) or len(native) != len(reference):
        raise QualificationError("phase vectors have incompatible lengths")
    result = []
    for channel in range(19):
        row: dict[str, Any] = {"channel": CHANNELS[channel], "native_phase_rad": [None] * len(native),
                              "reference_phase_rad": [None] * len(native),
                              "native_group_delay_s": [None] * len(native),
                              "reference_group_delay_s": [None] * len(native), "exclusions": []}
        segment: list[int] = []

        def finish() -> None:
            if not segment:
                return
            if len(segment) == 1:
                row["exclusions"].append({"index": segment[0], "kind": "group_delay",
                                          "reason": "single-bin-eligible-segment"})
                segment.clear()
                return
            for position, index in enumerate(segment):
                left = segment[max(0, position - 1)]
                right = segment[min(len(segment) - 1, position + 1)]
                denominator = math.tau * (frequencies[right] - frequencies[left])
                for prefix in ("native", "reference"):
                    row[f"{prefix}_group_delay_s"][index] = -(
                        row[f"{prefix}_phase_rad"][right] - row[f"{prefix}_phase_rad"][left]) / denominator
            segment.clear()

        for index, (actual, expected) in enumerate(zip(native, reference)):
            actual_ok = abs(actual[channel]) >= PHASE_FLOOR
            expected_ok = abs(expected[channel]) >= PHASE_FLOOR
            if not actual_ok or not expected_ok:
                finish()
                missing = "both" if not actual_ok and not expected_ok else "native" if not actual_ok else "reference"
                row["exclusions"].append({"index": index, "kind": "phase_and_group_delay",
                                          "reason": f"{missing}-magnitude-below-1e-4"})
                continue
            for prefix, values in (("native", actual), ("reference", expected)):
                phase = cmath.phase(values[channel])
                if segment:
                    previous = row[f"{prefix}_phase_rad"][segment[-1]]
                    phase = previous + math.remainder(phase - previous, math.tau)
                row[f"{prefix}_phase_rad"][index] = phase
            segment.append(index)
        finish()
        result.append(row)
    return result


def _diagnostics(native: dict[str, Any], reference: dict[str, Any] | None) -> dict[str, Any]:
    residual = _number(native.get("normalized_residual"), "native residual", 0.0)
    condition = _number(native.get("condition_inf"), "native condition", 0.0)
    record: dict[str, Any] = {"native_normalized_residual": residual, "native_condition_inf": condition,
                              "native_conditioning_limited": condition * 2.0 ** -52 > 1e-4,
                              "residual_failure": residual > RESIDUAL_LIMIT}
    if reference is not None:
        oracle_residual = max(reference["normalized_residual"], reference["scaled_normalized_residual"])
        record.update(reference_normalized_residual=reference["normalized_residual"],
                      reference_scaled_normalized_residual=reference["scaled_normalized_residual"],
                      reference_scaled_condition_inf=reference["scaled_condition_inf"],
                      reference_conditioning_limited=reference["conditioning_limited"])
        record["residual_failure"] |= oracle_residual > RESIDUAL_LIMIT
    return record


def _status(failures: int, limited: int = 0) -> str:
    return "failed" if failures else "inconclusive" if limited else "passed"


def _hash(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def source_snapshot(root: Path, profile: Path, probe: Path) -> dict[str, Any]:
    source_hashes = {name: _hash(root / name) for name in SOURCE_FILES}
    source_hashes["authoring_input"] = _hash(profile)
    source_hashes["native_executable"] = _hash(probe)
    identity = hashlib.sha256(json.dumps(source_hashes, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {"sha256": identity, "files_sha256": source_hashes}


def _build_metadata(probe: Path) -> dict[str, Any]:
    result: dict[str, Any] = {"python_version": platform.python_version(), "platform": platform.platform(),
                              "precision": "native binary64 complex and real; Python binary64; rational DC",
                              "build_relationship": "caller must associate this executable with the recorded source snapshot"}
    for parent in (probe.parent, probe.parent.parent):
        cache = parent / "CMakeCache.txt"
        if cache.is_file():
            result["cmake_cache_sha256"] = _hash(cache)
            values = {}
            for line in cache.read_text(encoding="utf-8", errors="replace").splitlines():
                if line.startswith(("CMAKE_BUILD_TYPE:", "CMAKE_CXX_COMPILER:", "CMAKE_CXX_FLAGS:",
                                    "CMAKE_CXX_FLAGS_RELEASE:", "CMAKE_GENERATOR:", "HAMMOND_ENABLE_SANITIZERS:")):
                    key, value = line.split("=", 1)
                    values[key.split(":", 1)[0]] = value
            result["cmake_values"] = values
            break
    return result


def qualify(probe: Path, *, profile_path: Path = DEFAULT_PROFILE, root: Path = ROOT,
            host_rates: tuple[int, ...] = HOST_RATES, multipliers: tuple[int, ...] = MULTIPLIERS,
            modes: tuple[str, ...] = MODES, frequencies: tuple[float, ...] | None = None,
            include_process: bool = True, process_frequencies: tuple[float, ...] = PROCESS_FREQUENCIES,
            progress: Callable[[str], None] | None = None) -> dict[str, Any]:
    """Compute the report. Valid numerical failures are results, not exceptions."""
    probe, profile_path, root = Path(probe).resolve(), Path(profile_path).resolve(), Path(root).resolve()
    if not probe.is_file():
        raise QualificationError("native probe executable does not exist")
    host_rates = _selection(host_rates, HOST_RATES, "host rates")
    multipliers = _selection(multipliers, MULTIPLIERS, "multipliers")
    modes = _selection(modes, MODES, "modes")
    if type(include_process) is not bool:
        raise QualificationError("include_process must be bool")
    grid = frequency_grid() if frequencies is None else _grid(frequencies, "frequencies", 1e-6, 20000.0)
    process_frequencies = _grid(process_frequencies, "process frequencies", 1.0, 20000.0)
    before = source_snapshot(root, profile_path, probe)
    if before["files_sha256"]["docs/SCANNER_NUMERICAL_CONTRACT.md"] != FROZEN_CONTRACT_SHA256:
        raise QualificationError("frozen scanner-numerics-v1 contract bytes have changed")
    profile, digest = load_profile_with_digest(profile_path)
    network = prepare_network(profile)
    combinations = [{"host_rate_hz": int(host), "multiplier": int(factor),
                     "internal_rate_hz": int(host * factor), "case_ids": [f"{int(host * factor)}-{mode}" for mode in modes]}
                    for host in host_rates for factor in multipliers]
    rates = sorted({row["internal_rate_hz"] for row in combinations})
    report: dict[str, Any] = {
        "schema_version": 1, "qualification_id": QUALIFICATION_ID, "contract_id": CONTRACT_ID,
        "contract_sha256": FROZEN_CONTRACT_SHA256, "model_id": MODEL_ID,
        "realization_id": REALIZATION_ID, "reference_id": "independent-nodal-scanner-ac-v1",
        "authoring_sha256": digest, "compiled_header_sha256": hashlib.sha256(compile_profile(profile_path, "header").encode("utf-8")).hexdigest(),
        "source_snapshot": before, "toolchain": _build_metadata(probe),
        "frequency_grid_hz": list(grid), "channels": list(CHANNELS),
        "channel_units": ["V/V"] * 20 + ["15000 ohm * A/V"],
        "rate_combinations": combinations, "distinct_internal_rates_hz": rates,
        "scope": {"stationary_full_contract_grid": (grid == frequency_grid() and set(host_rates) == set(HOST_RATES)
                                                     and set(multipliers) == set(MULTIPLIERS) and set(modes) == set(MODES)),
                  "process_full_contract_frequencies": (include_process and process_frequencies == PROCESS_FREQUENCIES),
                  "G3_full_gate": "not_assessed_here: independent transient/state gates are separate",
                  "G5_full_gate": "not_assessed_here: transient, rotating output and resampling/filter gates are separate",
                  "physical_fidelity_established": False, "engine_or_native_plugin_integration_tested": False},
        "conventions": {"bilinear_kappa": "2 * internal_rate_hz; no prewarp",
                        "analog_warp_hz": "internal_rate_hz / pi * tan(pi * physical_hz / internal_rate_hz)",
                        "source": "one-volt p0 relative to g; input current positive into line",
                        "complex_values": "[real, imaginary]; no fitted sign/gain/phase/latency",
                        "input_reconstruction": "trapezoidal two-endpoint forcing",
                        "clock": "cold state at previous endpoint; first processed endpoint is n=0 and completed count1",
                        "phase": "pairwise magnitude >=1e-4; unwrap only contiguous eligible bins",
                        "group_delay": "negative phase secants in physical digital omega, including warped-reference diagnostics",
                        "shared_rate_cases": "identical internal rates computed once and explicitly referenced by all host/multiplier labels"},
        "budgets": {"DC": [1e-10, 1e-9], "G3_warp_matched": [1e-8, 1e-6],
                    "G5_same_hertz_taps": [1e-3, 1e-2], "solve_residual": 1e-9,
                    "conditioning_indicator": "condition_inf * 2^-52 <=1e-4",
                    "process_startup_and_half_window": "1e-8 + 1e-6*abs(later estimate), per channel; no fitted shift",
                    "startup_protocol_id": "scanner-process-settling-refinement-v1",
                    "startup_seconds": list(STARTUP_SECONDS),
                    "startup_policy": "retain all attempts; stop at two consecutive half-window-stable fits whose complex difference meets the same bound; grade the final settled fit against independent AC"},
        "stationary_cases": [], "process_cases": [], "summary": {},
    }
    oracle_cache: dict[tuple[str, float], dict[str, Any]] = {}

    def oracle(mode: str, frequency: float) -> dict[str, Any]:
        key = mode, frequency
        if key not in oracle_cache:
            oracle_cache[key] = solve_ac(network, mode, frequency)
        return oracle_cache[key]

    stationary_failures = stationary_limited = same_failures = dc_failures = 0
    for rate in rates:
        for mode in modes:
            if progress:
                progress(f"stationary {rate} Hz {mode}: DC + {len(grid)} positive bins")
            raw = run_probe(probe, "response", rate, mode,
                            ["--frequencies", ",".join(format(f, ".17g") for f in (0.0, *grid))], digest)
            rows = raw.get("responses")
            if not isinstance(rows, list) or len(rows) != len(grid) + 1:
                raise QualificationError("native response count does not match requested grid")
            if any(_number(row.get("frequency_hz"), "response frequency") != frequency
                   for row, frequency in zip(rows, (0.0, *grid)) if isinstance(row, dict)):
                raise QualificationError("native frequency labels do not match requested grid")
            if any(not isinstance(row, dict) for row in rows):
                raise QualificationError("native response rows must be objects")
            expected_dc = _oracle_vectors(dc_reference(network, mode))
            native_dc = _vectors(rows[0])
            dc = {"native": [_pair(value) for value in native_dc],
                  "rational_reference": [[str(value.numerator), str(value.denominator)]
                                         for value in (*dc_reference(network, mode)["taps"],
                                                       dc_reference(network, mode)["return_voltage"],
                                                       15000 * dc_reference(network, mode)["input_current"])],
                  "comparison": compare_vectors(native_dc, expected_dc, 1e-10, 1e-9),
                  "solve": _diagnostics(rows[0], None)}
            dc_failures += len(dc["comparison"]["failed_channels"])
            case: dict[str, Any] = {"case_id": f"{rate}-{mode}", "internal_rate_hz": rate, "mode": mode,
                                    "probe_id": raw["probe_id"], "clock_convention": raw["clock_convention"],
                                    "dc": dc, "responses": []}
            native_values, warped_values, same_values = [], [], []
            for frequency, native_row in zip(grid, rows[1:]):
                mapped_hz = rate / math.pi * math.tan(math.pi * frequency / rate)
                warped = oracle(mode, mapped_hz)
                same = oracle(mode, frequency)
                native = _vectors(native_row)
                expected = _oracle_vectors(warped)
                unwarped = _oracle_vectors(same)
                warp_comparison = compare_vectors(native, expected, 1e-8, 1e-6)
                same_comparison = compare_vectors(native[:19], unwarped[:19], 1e-3, 1e-2)
                diagnostics = _diagnostics(native_row, warped)
                same_diagnostics = {key: same[key] for key in ("normalized_residual", "scaled_normalized_residual",
                                                               "scaled_condition_inf", "conditioning_limited")}
                stationary_failures += len(warp_comparison["failed_channels"]) + int(diagnostics["residual_failure"])
                stationary_limited += int(diagnostics["native_conditioning_limited"] or warped["conditioning_limited"])
                same_failures += len(same_comparison["failed_channels"])
                case["responses"].append({"frequency_hz": frequency, "mapped_analog_hz": mapped_hz,
                                           "native": [_pair(v) for v in native],
                                           "warped_reference": [_pair(v) for v in expected],
                                           "same_hertz_reference": [_pair(v) for v in unwarped],
                                           "native_input_admittance_a_per_v": native_row["input_admittance"],
                                           "warped_reference_input_admittance_a_per_v": _pair(warped["input_current"]),
                                           "same_hertz_reference_input_admittance_a_per_v": _pair(same["input_current"]),
                                           "G3_warp_matched": warp_comparison, "G5_same_hertz_taps": same_comparison,
                                           "solve": diagnostics, "same_hertz_reference_solve": same_diagnostics})
                native_values.append(native)
                warped_values.append(expected)
                same_values.append(unwarped)
            case["warp_matched_phase"] = phase_diagnostics(grid, native_values, warped_values)
            case["same_hertz_phase"] = phase_diagnostics(grid, native_values, same_values)
            dc_solve_fail = int(dc["solve"]["residual_failure"])
            dc_limited = int(dc["solve"]["native_conditioning_limited"])
            stationary_failures += dc_solve_fail
            stationary_limited += dc_limited
            case_warp_failures = len(dc["comparison"]["failed_channels"]) + dc_solve_fail + sum(
                len(row["G3_warp_matched"]["failed_channels"]) + int(row["solve"]["residual_failure"])
                for row in case["responses"])
            case_limited = dc_limited + sum(int(row["solve"]["native_conditioning_limited"] or
                                                row["solve"]["reference_conditioning_limited"])
                                           for row in case["responses"])
            case_same_failures = sum(len(row["G5_same_hertz_taps"]["failed_channels"]) for row in case["responses"])
            same_reference_failure = any(max(row["same_hertz_reference_solve"]["normalized_residual"],
                                             row["same_hertz_reference_solve"]["scaled_normalized_residual"],
                                             row["solve"]["native_normalized_residual"]) > RESIDUAL_LIMIT
                                         for row in case["responses"])
            same_limited = any(row["same_hertz_reference_solve"]["conditioning_limited"] or
                               row["solve"]["native_conditioning_limited"] for row in case["responses"])
            case["summary"] = {"G3_stationary_status": _status(case_warp_failures, case_limited),
                               "G3_failed_comparisons_or_solves": case_warp_failures,
                               "conditioning_limited_bins": case_limited,
                               "G5_same_hertz_status": _status(case_same_failures + int(same_reference_failure), int(same_limited)),
                               "G5_same_hertz_failed_taps": case_same_failures,
                               "G5_same_hertz_failed_bins": sum(bool(row["G5_same_hertz_taps"]["failed_channels"]) for row in case["responses"])}
            report["stationary_cases"].append(case)

    process_failures = process_limited = process_unsettled = 0
    if include_process:
        for rate in rates:
            for mode in modes:
                if progress:
                    progress(f"process {rate} Hz {mode}: {len(process_frequencies)} carriers, bounded startup refinement")
                for frequency in process_frequencies:
                    expected_record = oracle(mode, rate / math.pi * math.tan(math.pi * frequency / rate))
                    expected = _oracle_vectors(expected_record)
                    measurements = []
                    startup = None
                    settled = False
                    for seconds in STARTUP_SECONDS:
                        warmup = math.ceil(rate * seconds)
                        count = max(math.ceil(rate * 0.125), math.ceil(8.0 * rate / frequency))
                        raw = run_probe(probe, "sine", rate, mode,
                                        ["--frequency", format(frequency, ".17g"), "--warmup-frames", str(warmup),
                                         "--measurement-frames", str(count), "--amplitude", "1"], digest)
                        if (raw.get("frequency_hz") != frequency or raw.get("amplitude_volts") != 1.0
                                or raw.get("warmup_frames") != warmup or raw.get("measurement_frames") != count):
                            raise QualificationError("native sine labels do not match requested experiment")
                        estimate = _vectors(raw.get("transfer"))
                        first = _vectors(raw.get("first_half_transfer"))
                        second = _vectors(raw.get("second_half_transfer"))
                        rms = raw.get("fit_residual_rms")
                        if not isinstance(rms, dict) or not isinstance(rms.get("taps_volts"), list) or len(rms["taps_volts"]) != 19:
                            raise QualificationError("native sine residual diagnostics are incomplete")
                        for value in (*rms["taps_volts"], rms.get("return_volts"), rms.get("input_current_amps")):
                            _number(value, "sine residual RMS", 0.0)
                        _number(raw.get("half_window_max_difference"), "half-window difference", 0.0)
                        measurements.append({"warmup_frames": warmup, "measurement_frames": count,
                                             "transfer": [_pair(v) for v in estimate],
                                             "first_half_transfer": [_pair(v) for v in first],
                                             "second_half_transfer": [_pair(v) for v in second],
                                             "native_input_admittance_a_per_v": raw["transfer"]["input_admittance"],
                                             "fit_residual_rms": rms,
                                             "reported_half_window_max_difference": raw["half_window_max_difference"],
                                             "G3_warp_matched": compare_vectors(estimate, expected, 1e-8, 1e-6),
                                             "half_window_convergence": compare_vectors(first, second, 1e-8, 1e-6)})
                        if len(measurements) >= 2:
                            earlier = tuple(complex(*v) for v in measurements[-2]["transfer"])
                            later = tuple(complex(*v) for v in measurements[-1]["transfer"])
                            startup = compare_vectors(earlier, later, 1e-8, 1e-6)
                            measurements[-1]["difference_from_previous_startup"] = startup
                            settled = (not startup["failed_channels"] and not any(
                                row["half_window_convergence"]["failed_channels"] for row in measurements[-2:]))
                            if settled:
                                break
                    reference_bad = not expected_record["residual_within_budget"]
                    failures = (len(measurements[-1]["G3_warp_matched"]["failed_channels"]) + int(reference_bad)) if settled else 0
                    limited = int(expected_record["conditioning_limited"])
                    process_failures += failures
                    process_limited += limited
                    process_unsettled += int(not settled)
                    report["process_cases"].append({"case_id": f"{rate}-{mode}-{frequency:g}",
                                                    "internal_rate_hz": rate, "mode": mode, "frequency_hz": frequency,
                                                    "warped_reference": [_pair(v) for v in expected],
                                                    "reference_solve": {key: expected_record[key] for key in
                                                                        ("normalized_residual", "scaled_normalized_residual",
                                                                         "scaled_condition_inf", "conditioning_limited")},
                                                    "measurements": measurements, "startup_convergence": startup,
                                                    "settled": settled, "accepted_measurement_index": len(measurements)-1 if settled else None,
                                                    "status": _status(failures, limited + int(not settled))})
    after = source_snapshot(root, profile_path, probe)
    if after != before:
        raise QualificationError("a qualification input or native executable changed during the run")
    report["source_snapshot_verified_unchanged"] = True
    report["summary"] = {
        "host_multiplier_pairs": len(combinations), "distinct_internal_rates": len(rates),
        "distinct_stationary_cases": len(report["stationary_cases"]),
        "distinct_positive_native_solutions": len(rates) * len(modes) * len(grid),
        "logical_positive_native_solutions": len(combinations) * len(modes) * len(grid),
        "logical_positive_tap_comparisons": len(combinations) * len(modes) * len(grid) * 19,
        "independent_ac_solves": len(oracle_cache),
        "G3_DC_failed_channels": dc_failures,
        "G3_stationary_failed_comparisons_or_solves": stationary_failures + dc_failures,
        "G3_stationary_conditioning_limited_bins": stationary_limited,
        "G3_stationary_status": _status(stationary_failures + dc_failures, stationary_limited),
        "G5_same_hertz_failed_taps_distinct_rate_cases": same_failures,
        "G5_same_hertz_status": ("failed" if any(case["summary"]["G5_same_hertz_status"] == "failed" for case in report["stationary_cases"])
                                 else "inconclusive" if any(case["summary"]["G5_same_hertz_status"] == "inconclusive" for case in report["stationary_cases"])
                                 else "passed"),
        "process_carrier_cases": len(report["process_cases"]),
        "process_measurements": sum(len(case["measurements"]) for case in report["process_cases"]),
        "process_unsettled_cases": sum(not case["settled"] for case in report["process_cases"]),
        "retained_early_process_attempts_outside_complex_budget": sum(bool(measurement["G3_warp_matched"]["failed_channels"])
            for case in report["process_cases"] for measurement in case["measurements"][:-1]),
        "G3_process_failed_comparisons_or_solves": process_failures,
        "G3_process_conditioning_limited_cases": process_limited,
        "G3_process_status": _status(process_failures, process_limited + process_unsettled) if include_process else "not_run",
    }
    return report


def write_report(path: Path, report: dict[str, Any], *, protected: tuple[Path, ...] = ()) -> None:
    """Serialize finite bounded data, then atomically replace a regular output."""
    path = Path(path)
    try:
        payload = (json.dumps(report, ensure_ascii=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")
    except (ValueError, TypeError, OverflowError, RecursionError) as exc:
        raise QualificationError(f"report serialization failed: {exc}") from exc
    if len(payload) > MAX_REPORT_BYTES:
        raise QualificationError("report exceeds 128 MiB")
    for source in protected:
        if path.resolve() == Path(source).resolve() or (path.exists() and Path(source).exists() and os.path.samefile(path, source)):
            raise QualificationError("output aliases a protected qualification input")
    if path.exists() or path.is_symlink():
        if not stat.S_ISREG(path.lstat().st_mode):
            raise QualificationError("output must be a regular file or new path")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent, delete=False) as stream:
            temporary = stream.name
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass


def _csv(value: str) -> tuple[float, ...]:
    try:
        values = tuple(float(part) for part in value.split(","))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected comma-separated numbers") from exc
    if not values or not all(math.isfinite(number) for number in values):
        raise argparse.ArgumentTypeError("expected finite comma-separated numbers")
    return values


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe", type=Path, required=True)
    parser.add_argument("--input", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--host-rates", type=_csv, default=HOST_RATES)
    parser.add_argument("--multipliers", type=_csv, default=MULTIPLIERS)
    parser.add_argument("--frequencies", type=_csv)
    parser.add_argument("--mode", choices=MODES, action="append")
    parser.add_argument("--skip-process", action="store_true", help="retain an explicit not_run process gate")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)
    try:
        report = qualify(args.probe, profile_path=args.input, host_rates=args.host_rates,
                         multipliers=args.multipliers, modes=tuple(args.mode) if args.mode else MODES,
                         frequencies=args.frequencies, include_process=not args.skip_process,
                         progress=None if args.quiet else lambda message: print(message, file=sys.stderr, flush=True))
        protected = tuple(ROOT / name for name in SOURCE_FILES) + (args.probe, args.input)
        write_report(args.output, report, protected=protected)
        print(json.dumps(report["summary"], sort_keys=True, allow_nan=False))
        statuses = [report["summary"]["G3_stationary_status"]]
        if not args.skip_process:
            statuses.append(report["summary"]["G3_process_status"])
        return 0 if all(status == "passed" for status in statuses) else 1
    except (QualificationError, ValueError, OSError, OverflowError) as exc:
        print(f"scanner AC qualification rejected: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
