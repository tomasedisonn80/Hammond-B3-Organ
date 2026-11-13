#!/usr/bin/env python3
"""Independent offline nodal AC reference for the admitted nominal scanner graph.

This module stamps physical edges directly. It does not import the native
runtime's reduced-state formulation or generated operators. All results concern
an ideal documentary circuit, never measured Hammond hardware.
"""

from __future__ import annotations

import argparse
import cmath
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
import math
import os
import stat
from pathlib import Path
import sys
import tempfile
from typing import Any

from compile_scanner_line import load_profile, load_profile_with_digest, normalized_profile

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROFILE = ROOT / "data/scanner/atlas-late-b3-nominal-v1.json"
MODES = ("vibrato", "chorus")
MAX_FREQUENCY_HZ = 1.0e9
MAX_REPORT_BYTES = 16 * 1024 * 1024
PHASE_MAGNITUDE_FLOOR = 1.0e-4
RESIDUAL_LIMIT = 1.0e-9
GRID_ID = "scanner-ac-20-20000-log121-plus-5000-9000-step25-v1"
EXPERIMENT_KEYS = {"termination_ohms", "divider_attachment", "output_reference", "output_sign", "reverse_output"}


class ReferenceError(ValueError):
    """A reference input, topology or numerical solve is inadmissible."""


@dataclass(frozen=True)
class Element:
    id: str
    kind: str
    positive: str
    negative: str
    value_si: float


@dataclass(frozen=True)
class Network:
    model_id: str
    base_model_id: str
    authoring_canonical_sha256: str
    nodes: tuple[str, ...]
    components: tuple[Element, ...]
    outputs: tuple[tuple[str, str, str], ...]
    experiment: tuple[tuple[str, Any], ...] = ()

    @property
    def nominal(self) -> bool:
        return not self.experiment


def _real(value: Any, label: str, low: float, high: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ReferenceError(f"{label} must be a real number")
    try:
        number = float(value)
    except (ValueError, OverflowError) as exc:
        raise ReferenceError(f"{label} is not a finite real number") from exc
    if not math.isfinite(number) or not low <= number <= high:
        raise ReferenceError(f"{label} must be finite and in [{low}, {high}]")
    return number


def _mode(mode: str) -> None:
    if mode not in MODES:
        raise ReferenceError("mode must be exactly vibrato or chorus")


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def prepare_network(profile: dict[str, Any], *,
                    experiment: dict[str, Any] | None = None) -> Network:
    """Admit the exact nominal graph, then optionally apply named experiments.

    Experiments are deliberately not re-admitted under the nominal identity.
    Their full descriptions travel with every response and report. They are
    numerical sensitivity probes, not alternate production profiles.
    """
    admitted = normalized_profile(profile)
    if experiment is None:
        experiment = {}
    if not isinstance(experiment, dict) or set(experiment) - EXPERIMENT_KEYS:
        raise ReferenceError("unknown experiment field")
    changes: dict[str, Any] = {}
    if "termination_ohms" in experiment:
        changes["termination_ohms"] = _real(
            experiment["termination_ohms"], "termination_ohms", 1.0, 1.0e9)
    if "divider_attachment" in experiment:
        if experiment["divider_attachment"] != "after-inductor":
            raise ReferenceError("divider_attachment experiment must be after-inductor")
        changes["divider_attachment"] = "after-inductor"
    if "output_reference" in experiment:
        if experiment["output_reference"] != "return":
            raise ReferenceError("output_reference experiment must be return")
        changes["output_reference"] = "return"
    if "output_sign" in experiment:
        if experiment["output_sign"] != "reversed":
            raise ReferenceError("output_sign experiment must be reversed")
        changes["output_sign"] = "reversed"
    if "reverse_output" in experiment:
        if experiment["reverse_output"] not in tuple(f"v{k}" for k in range(1, 20)):
            raise ReferenceError("reverse_output must name one of v1..v19")
        if "output_sign" in experiment:
            raise ReferenceError("choose either one reversed output or all reversed outputs")
        changes["reverse_output"] = experiment["reverse_output"]
    components = []
    for row in admitted["components"]:
        positive = row["positive"]
        value = row["value"]["si_value"]
        if row["id"] == "Rt" and "termination_ohms" in changes:
            value = changes["termination_ohms"]
        if (changes.get("divider_attachment") == "after-inductor"
                and row["id"] in {f"R{k}+" for k in range(1, 7)}):
            positive = f"p{row['id'][1]}"
        components.append(Element(row["id"], row["kind"], positive,
                                  row["negative"], float(value)))
    outputs = tuple((row["id"], row["positive"],
                     "r" if changes.get("output_reference") == "return" else row["negative"])
                    for row in admitted["outputs"])
    if changes.get("output_sign") == "reversed":
        outputs = tuple((name, q, p) for name, p, q in outputs)
    elif "reverse_output" in changes:
        outputs = tuple((name, q, p) if name == changes["reverse_output"] else (name, p, q)
                        for name, p, q in outputs)
    base_id = admitted["model_id"]
    model_id = ("scanner-experiment-v1-" + hashlib.sha256(
        _canonical_bytes({"base_model_id": base_id, "changes": changes})).hexdigest()[:16]
        if changes else base_id)
    return Network(model_id, base_id, hashlib.sha256(_canonical_bytes(profile)).hexdigest(),
                   tuple(admitted["nodes"]), tuple(components), outputs,
                   tuple(sorted(changes.items())))


def _network(value: Network | dict[str, Any], experiment: dict[str, Any] | None) -> Network:
    if isinstance(value, Network):
        if experiment is not None:
            raise ReferenceError("apply an experiment once, while preparing the network")
        return value
    return prepare_network(value, experiment=experiment)


def default_frequency_grid() -> tuple[float, ...]:
    """Frozen before runtime grading: 121 log points plus 161 detail points."""
    grid = {round(20.0 * 1000.0 ** (j / 120.0), 12) for j in range(121)}
    grid.update(float(f) for f in range(5000, 9001, 25))
    grid.add(20.0)
    grid.add(20000.0)
    return tuple(sorted(grid))


def _admittance(component: Element, omega: float) -> complex:
    if component.kind == "R":
        return complex(1.0 / component.value_si)
    if component.kind == "L":
        return 1.0 / complex(0.0, omega * component.value_si)
    if component.kind == "C":
        return complex(0.0, omega * component.value_si)
    raise ReferenceError("unsupported admitted component type")


def _stamp(network: Network, mode: str, frequency_hz: float
           ) -> tuple[list[str], list[list[complex]], list[complex]]:
    # Ideal source and short are constraints, never huge numerical admittances.
    known = {"g": 0.0j, "p0": 1.0 + 0.0j}
    if mode == "vibrato":
        known["r"] = 0.0j
    unknown = [node for node in network.nodes if node not in known]
    index = {node: j for j, node in enumerate(unknown)}
    n = len(unknown)
    if not 1 <= n <= 32:
        raise ReferenceError("unsupported nodal system dimension")
    matrix = [[0.0j for _ in range(n)] for _ in range(n)]
    rhs = [0.0j for _ in range(n)]
    omega = math.tau * frequency_hz
    for element in network.components:
        y = _admittance(element, omega)
        p, q = element.positive, element.negative
        # Sum branch currents leaving each unknown node; fixed voltage terms
        # move to the RHS. The same edge contributes to both endpoint equations.
        for here, there in ((p, q), (q, p)):
            if here not in index:
                continue
            row = index[here]
            matrix[row][row] += y
            if there in index:
                matrix[row][index[there]] -= y
            else:
                rhs[row] += y * known[there]
    return unknown, matrix, rhs


def _infinity_norm(matrix: list[list[complex]]) -> float:
    return max((sum(abs(v) for v in row) for row in matrix), default=0.0)


def _factor_scaled(matrix: list[list[complex]]
                   ) -> tuple[list[list[complex]], list[int], list[float], list[list[complex]]]:
    scales = [max((abs(v) for v in row), default=0.0) for row in matrix]
    if any(not math.isfinite(v) or v <= 0.0 for v in scales):
        raise ReferenceError("zero or nonfinite nodal equation scale")
    scaled = [[v / scales[i] for v in row] for i, row in enumerate(matrix)]
    lu = [row[:] for row in scaled]
    n = len(lu)
    swaps: list[int] = []
    for k in range(n):
        pivot = max(range(k, n), key=lambda i: abs(lu[i][k]))
        size = abs(lu[pivot][k])
        if not math.isfinite(size) or size <= 1.0e-15:
            raise ReferenceError("singular or numerically unresolved nodal system")
        swaps.append(pivot)
        if pivot != k:
            lu[k], lu[pivot] = lu[pivot], lu[k]
        diagonal = lu[k][k]
        for i in range(k + 1, n):
            factor = lu[i][k] / diagonal
            lu[i][k] = factor
            if factor:
                for j in range(k + 1, n):
                    lu[i][j] -= factor * lu[k][j]
    return lu, swaps, scales, scaled


def _solve_factored(lu: list[list[complex]], swaps: list[int],
                    rhs: list[complex]) -> list[complex]:
    answer = rhs[:]
    n = len(answer)
    for k, pivot in enumerate(swaps):
        if pivot != k:
            answer[k], answer[pivot] = answer[pivot], answer[k]
    for i in range(n):
        answer[i] -= sum(lu[i][j] * answer[j] for j in range(i))
    for i in range(n - 1, -1, -1):
        answer[i] = (answer[i] - sum(lu[i][j] * answer[j]
                                    for j in range(i + 1, n))) / lu[i][i]
    if any(not math.isfinite(z.real) or not math.isfinite(z.imag) for z in answer):
        raise ReferenceError("nonfinite nodal solution")
    return answer


def _residual(matrix: list[list[complex]], solution: list[complex],
              rhs: list[complex]) -> float:
    residual = max((abs(sum(a * z for a, z in zip(row, solution)) - b)
                    for row, b in zip(matrix, rhs)), default=0.0)
    denominator = (_infinity_norm(matrix) * max(map(abs, solution), default=0.0)
                   + max(map(abs, rhs), default=0.0))
    if denominator == 0.0:
        return 0.0 if residual == 0.0 else math.inf
    return residual / denominator


def _condition(lu: list[list[complex]], swaps: list[int],
               scaled: list[list[complex]]) -> float:
    # Explicit inverse-column solves, practical for this bounded 24/25-node
    # offline reference. This estimates the induced infinity condition of the
    # row-scaled matrix; it is not an unscaled MNA or a hardware uncertainty.
    n = len(lu)
    inverse_row_sums = [0.0] * n
    for column in range(n):
        rhs = [complex(i == column) for i in range(n)]
        values = _solve_factored(lu, swaps, rhs)
        for row, value in enumerate(values):
            inverse_row_sums[row] += abs(value)
    return _infinity_norm(scaled) * max(inverse_row_sums)


def solve_ac(profile: Network | dict[str, Any], mode: str, frequency_hz: float, *,
             experiment: dict[str, Any] | None = None,
             estimate_condition: bool = True) -> dict[str, Any]:
    """Solve a one-volt finite-frequency drive; currents are amperes per volt.

    ``taps`` contains nineteen complex signed voltages in v1..v19 order.
    Frequencies are physical analog Hz. DC is intentionally handled by the
    separate exact ``dc_reference`` function, not an arbitrarily low frequency.
    """
    _mode(mode)
    frequency_hz = _real(frequency_hz, "frequency_hz", 1.0e-6, MAX_FREQUENCY_HZ)
    if not isinstance(estimate_condition, bool):
        raise ReferenceError("estimate_condition must be bool")
    network = _network(profile, experiment)
    unknown, matrix, rhs = _stamp(network, mode, frequency_hz)
    lu, swaps, scales, scaled = _factor_scaled(matrix)
    scaled_rhs = [b / scale for b, scale in zip(rhs, scales)]
    solution = _solve_factored(lu, swaps, scaled_rhs)
    nodes = {"g": 0.0j, "p0": 1.0 + 0.0j}
    if mode == "vibrato":
        nodes["r"] = 0.0j
    nodes.update(zip(unknown, solution))
    omega = math.tau * frequency_hz
    current = 0.0j
    for element in network.components:
        branch = _admittance(element, omega) * (nodes[element.positive] - nodes[element.negative])
        if element.positive == "p0":
            current += branch
        if element.negative == "p0":
            current -= branch
    raw_residual = _residual(matrix, solution, rhs)
    scaled_residual = _residual(scaled, solution, scaled_rhs)
    condition = _condition(lu, swaps, scaled) if estimate_condition else None
    if condition is not None and not math.isfinite(condition):
        raise ReferenceError("nonfinite condition estimate")
    return {
        "mode": mode, "frequency_hz": frequency_hz,
        "model_id": network.model_id, "base_model_id": network.base_model_id,
        "nominal": network.nominal,
        "experiment": dict(network.experiment),
        "taps": tuple(nodes[p] - nodes[q] for _, p, q in network.outputs),
        "tap_ids": tuple(row[0] for row in network.outputs),
        "node_voltages": nodes, "return_voltage": nodes["r"],
        "input_current": current, "input_current_dimensionless": 15000.0 * current,
        "dimension": len(unknown),
        "normalized_residual": raw_residual,
        "scaled_normalized_residual": scaled_residual,
        "scaled_condition_inf": condition,
        "conditioning_indicator": None if condition is None else condition * 2.0**-52,
        "conditioning_limited": None if condition is None else condition * 2.0**-52 > 1.0e-4,
        "residual_within_budget": max(raw_residual, scaled_residual) <= RESIDUAL_LIMIT,
    }


def dc_reference(profile: Network | dict[str, Any], mode: str, *,
                 experiment: dict[str, Any] | None = None) -> dict[str, Any]:
    """Exact rational DC limit, independent of complex stamping/factorization.

    All admitted inductors become shorts and capacitors become open circuits.
    Pre/post-inductor divider mutations intentionally have identical DC values.
    """
    _mode(mode)
    network = _network(profile, experiment)
    resistors = {e.id: Fraction(str(e.value_si)) for e in network.components if e.kind == "R"}
    branches = [resistors[f"R{k}+"] + resistors[f"R{k}-"] for k in range(1, 7)]
    conductance = 1 / resistors["Rt"] + sum((1 / value for value in branches), Fraction())
    parallel = 1 / conductance
    input_resistance = parallel if mode == "vibrato" else parallel + resistors["Rc"]
    return_voltage = Fraction() if mode == "vibrato" else resistors["Rc"] / input_resistance
    nodes = {"g": Fraction(), **{f"p{k}": Fraction(1) for k in range(19)}, "r": return_voltage}
    for k, resistance in enumerate(branches, 1):
        nodes[f"d{k}"] = return_voltage + (1 - return_voltage) * resistors[f"R{k}-"] / resistance
    return {
        "mode": mode, "frequency_hz": 0, "model_id": network.model_id,
        "base_model_id": network.base_model_id, "nominal": network.nominal, "experiment": dict(network.experiment),
        "parallel_resistance_ohms": parallel, "input_resistance_ohms": input_resistance,
        "return_voltage": return_voltage, "input_current": 1 / input_resistance,
        "tap_ids": tuple(row[0] for row in network.outputs),
        "taps": tuple(nodes[p] - nodes[q] for _, p, q in network.outputs),
        "node_voltages": nodes,
    }


def _complex_json(value: complex) -> dict[str, float]:
    return {"real": value.real, "imag": value.imag}


def _fraction_json(value: Fraction) -> dict[str, Any]:
    return {"numerator": value.numerator, "denominator": value.denominator,
            "decimal": float(value)}


def _dc_json(result: dict[str, Any]) -> dict[str, Any]:
    return {"mode": result["mode"], "frequency_hz": 0,
            **{key: _fraction_json(result[key]) for key in
               ("parallel_resistance_ohms", "input_resistance_ohms", "return_voltage", "input_current")},
            "taps": [{"id": name, **_fraction_json(value)}
                     for name, value in zip(result["tap_ids"], result["taps"])]}


def _add_phase_and_delay(rows: list[dict[str, Any]]) -> None:
    # Never bridge a below-floor bin or independently shift a tap's phase origin.
    for tap_index in range(19):
        segment: list[int] = []
        previous_raw: float | None = None
        previous_unwrapped: float | None = None
        for index, row in enumerate(rows):
            tap = row["taps"][tap_index]
            if tap["magnitude"] < PHASE_MAGNITUDE_FLOOR:
                _finish_delay_segment(rows, tap_index, segment)
                segment = []
                previous_raw = previous_unwrapped = None
                tap["phase_exclusion_reason"] = "magnitude-below-1e-4"
                continue
            raw = tap["phase_radians"]
            unwrapped = raw if previous_raw is None else previous_unwrapped + math.remainder(raw - previous_raw, math.tau)
            tap["unwrapped_phase_radians"] = unwrapped
            segment.append(index)
            previous_raw, previous_unwrapped = raw, unwrapped
        _finish_delay_segment(rows, tap_index, segment)


def _finish_delay_segment(rows: list[dict[str, Any]], tap_index: int, segment: list[int]) -> None:
    if len(segment) < 2:
        if segment:
            rows[segment[0]]["taps"][tap_index]["group_delay_exclusion_reason"] = "fewer-than-two-adjacent-eligible-bins"
        return
    for position, index in enumerate(segment):
        left = segment[max(0, position - 1)]
        right = segment[min(len(segment) - 1, position + 1)]
        phase_difference = (rows[right]["taps"][tap_index]["unwrapped_phase_radians"]
                            - rows[left]["taps"][tap_index]["unwrapped_phase_radians"])
        frequency_difference = rows[right]["frequency_hz"] - rows[left]["frequency_hz"]
        rows[index]["taps"][tap_index]["group_delay_seconds"] = -phase_difference / (math.tau * frequency_difference)
        rows[index]["taps"][tap_index]["group_delay_exclusion_reason"] = None


def build_report(profile: dict[str, Any], *,
                 frequencies: tuple[float, ...] | list[float] | None = None,
                 modes: tuple[str, ...] = MODES,
                 experiment: dict[str, Any] | None = None,
                 estimate_condition: bool = True) -> dict[str, Any]:
    """Build a bounded JSON-ready report without writing any files."""
    network = prepare_network(profile, experiment=experiment)
    grid = default_frequency_grid() if frequencies is None else tuple(frequencies)
    if not grid or len(grid) > 1024:
        raise ReferenceError("frequency grid must contain 1..1024 entries")
    grid = tuple(_real(v, "frequency_hz", 1.0e-6, MAX_FREQUENCY_HZ) for v in grid)
    if any(a >= b for a, b in zip(grid, grid[1:])):
        raise ReferenceError("frequency grid must be strictly increasing")
    if (not isinstance(modes, (tuple, list)) or not modes or len(modes) > 2
            or any(type(mode) is not str for mode in modes) or len(set(modes)) != len(modes)):
        raise ReferenceError("mode selection must contain one or two distinct modes")
    for mode in modes:
        _mode(mode)
    report: dict[str, Any] = {
        "schema_version": 1,
        "reference_id": "independent-nodal-scanner-ac-v1",
        "scope": "ideal documentary circuit mathematics; not measured hardware or native-runtime qualification",
        "model_id": network.model_id, "base_model_id": network.base_model_id,
        "nominal": network.nominal,
        "experiment": dict(network.experiment),
        "authoring_canonical_sha256": network.authoring_canonical_sha256,
        "frequency_grid_id": GRID_ID if frequencies is None else "explicit-user-grid",
        "frequency_grid_hz": list(grid),
        "excitation": {"voltage": 1.0, "unit": "V", "positive": "p0", "negative": "g"},
        "input_current_convention": "positive from the ideal source into the passive line, A/V",
        "outputs_reference": "r" if dict(network.experiment).get("output_reference") == "return" else "g",
        "output_sign": ("reversed" if dict(network.experiment).get("output_sign") == "reversed"
                        else "one-reversed" if "reverse_output" in dict(network.experiment) else "positive"),
        "reversed_output": dict(network.experiment).get("reverse_output"),
        "linear_solve": {"method": "edge-admittance nodal elimination; row-max scaling; partial-pivot complex LU",
                         "condition": "induced infinity condition of row-scaled matrix via all inverse columns" if estimate_condition else "not computed",
                         "residual_limit": RESIDUAL_LIMIT,
                         "conditioning_limited_threshold": "kappa_inf(A_scaled)*2^-52 > 1e-4"},
        "phase": {"magnitude_floor": PHASE_MAGNITUDE_FLOOR,
                  "unwrapping": "adjacent eligible bins; fresh principal phase after a gap; no per-tap alignment",
                  "group_delay": "negative physical-omega secant; centered interior and one-sided segment endpoints"},
        "dc": [], "modes": [],
    }
    failures = []
    conditioning_limited = []
    maximum_residual = 0.0
    for mode in modes:
        report["dc"].append(_dc_json(dc_reference(network, mode)))
        rows = []
        for frequency in grid:
            solved = solve_ac(network, mode, frequency, estimate_condition=estimate_condition)
            residual = max(solved["normalized_residual"], solved["scaled_normalized_residual"])
            maximum_residual = max(maximum_residual, residual)
            if solved["conditioning_limited"]:
                conditioning_limited.append({"mode": mode, "frequency_hz": frequency,
                                             "indicator": solved["conditioning_indicator"]})
            if not solved["residual_within_budget"]:
                failures.append({"mode": mode, "frequency_hz": frequency, "residual": residual})
            rows.append({
                "frequency_hz": frequency,
                "taps": [{"id": name, **_complex_json(value), "magnitude": abs(value),
                          "phase_radians": cmath.phase(value), "unwrapped_phase_radians": None,
                          "group_delay_seconds": None, "phase_exclusion_reason": None,
                          "group_delay_exclusion_reason": "phase-ineligible"}
                         for name, value in zip(solved["tap_ids"], solved["taps"])],
                "return_voltage": _complex_json(solved["return_voltage"]),
                "input_current_a_per_v": _complex_json(solved["input_current"]),
                "input_current_times_15000_ohms": _complex_json(solved["input_current_dimensionless"]),
                "dimension": solved["dimension"],
                "normalized_residual": solved["normalized_residual"],
                "scaled_normalized_residual": solved["scaled_normalized_residual"],
                "scaled_condition_inf": solved["scaled_condition_inf"],
                "conditioning_indicator": solved["conditioning_indicator"],
                "conditioning_limited": solved["conditioning_limited"],
            })
        _add_phase_and_delay(rows)
        report["modes"].append({"mode": mode, "responses": rows})
    report["summary"] = {"positive_frequency_solutions": len(grid) * len(modes),
                         "tap_transfers": len(grid) * len(modes) * 19,
                         "maximum_normalized_residual": maximum_residual,
                         "residual_failures": failures,
                         "conditioning_limited_bins": conditioning_limited,
                         "residual_budget_passed": not failures,
                         "runtime_comparison_performed": False,
                         "physical_fidelity_established": False}
    return report


def write_report(path: Path, report: dict[str, Any]) -> None:
    """Atomically replace a report only after full finite serialization succeeds."""
    try:
        payload = (json.dumps(report, indent=2, allow_nan=False) + "\n").encode("utf-8")
    except (TypeError, ValueError, OverflowError) as exc:
        raise ReferenceError(f"report cannot be serialized: {exc}") from exc
    if len(payload) > MAX_REPORT_BYTES:
        raise ReferenceError("report exceeds 16 MiB")
    path = Path(path)
    if path.exists() or path.is_symlink():
        if not stat.S_ISREG(path.lstat().st_mode):
            raise ReferenceError("report destination must be a regular file or a new path")
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(prefix=f".{path.name}.", suffix=".tmp",
                                         dir=path.parent, delete=False) as stream:
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--output", type=Path, required=True, help="atomically replace after a complete successful solve")
    parser.add_argument("--mode", choices=(*MODES, "both"), default="both")
    parser.add_argument("--frequencies", help="comma-separated increasing analog Hz; default uses the frozen grid")
    parser.add_argument("--skip-condition", action="store_true", help="report condition estimates as not computed")
    parser.add_argument("--termination-ohms", type=float, help="explicitly non-nominal sensitivity experiment")
    parser.add_argument("--dividers-after-inductor", action="store_true", help="explicitly wrong-topology detection experiment")
    parser.add_argument("--outputs-relative-to-return", action="store_true", help="explicitly wrong-reference experiment")
    parser.add_argument("--reverse-output-sign", action="store_true", help="explicitly reversed signed-observation experiment")
    parser.add_argument("--reverse-output", choices=tuple(f"v{k}" for k in range(1, 20)),
                        help="reverse exactly one signed output, preserving the other eighteen")
    args = parser.parse_args(argv)
    try:
        if (args.input.resolve() == args.output.resolve()
                or (args.output.exists() and os.path.samefile(args.input, args.output))):
            raise ReferenceError("input and output must be different paths")
        profile, input_sha256 = load_profile_with_digest(args.input)
        experiment = {}
        if args.termination_ohms is not None:
            experiment["termination_ohms"] = args.termination_ohms
        if args.dividers_after_inductor:
            experiment["divider_attachment"] = "after-inductor"
        if args.outputs_relative_to_return:
            experiment["output_reference"] = "return"
        if args.reverse_output_sign:
            experiment["output_sign"] = "reversed"
        if args.reverse_output is not None:
            experiment["reverse_output"] = args.reverse_output
        frequencies = None
        if args.frequencies is not None:
            if len(args.frequencies) > 32768:
                raise ReferenceError("frequency argument exceeds its size bound")
            frequencies = tuple(float(v) for v in args.frequencies.split(","))
        report = build_report(profile, frequencies=frequencies,
                              modes=MODES if args.mode == "both" else (args.mode,),
                              experiment=experiment, estimate_condition=not args.skip_condition)
        report["input_file_sha256"] = input_sha256
        if not report["summary"]["residual_budget_passed"]:
            raise ReferenceError("numerical residual budget failed; destination preserved")
        write_report(args.output, report)
        print(json.dumps(report["summary"], sort_keys=True))
        return 0
    except (OSError, ValueError, OverflowError, RecursionError) as exc:
        print(f"scanner AC reference: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
