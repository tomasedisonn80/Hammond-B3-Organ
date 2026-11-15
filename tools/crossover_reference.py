#!/usr/bin/env python3
"""Independent ideal Leslie 122 crossover reference and registry admission.

The series/parallel calculation and direct edge-stamped nodal calculation use
the admitted documentary circuit, not the native implementation or its state
matrices. Results are electrical resistor-fixture experiments, not measurements.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "data/crossover/leslie-122-ideal-v1.json"
REFERENCE_ID = "leslie-crossover-independent-analog-reference-v1"
GRID_ID = "crossover-log121-10-20000-plus-400-800-1600-v1"
ERROR_LIMIT = 2.0e-10
MAX_REGISTRY_BYTES = 64 * 1024

# A fixed model has a fixed evidence contract. Field-by-field admission gives
# actionable errors and distinguishes an ideal zero from an unknown measurement.
EXPECTED_REGISTRY = {
    "schema_version": 1,
    "model_id": "atlas-leslie-122-ideal-crossover-v1",
    "realization_id": "physical-trapezoidal-leslie-crossover-v1",
    "evidence_class": "atlas-documentary-with-explicit-ideal-assumptions",
    "target": {
        "cabinet_family": "Leslie 122", "divider_assembly": "052803",
        "documentary_year": 1971, "specimen_identity": None,
        "specimen_status": "not-acquired",
        "related_assembly": {
            "id": "113860", "documentary_year": 1979,
            "status": "atlas-reported-context-only; not an admitted substitute profile",
        },
    },
    "source": {
        "document": "Hammond_B3_Leslie_Research_Atlas_500pp.pdf",
        "sha256": "4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769",
        "pages": [271, 272, 273, 274, 275, 276],
        "verification": "atlas-read; manufacturer drawings not independently inspected",
        "atlas_citations": ["S044-01", "S044-02"],
        "missing_companion": "reference_code/crossover_ac_reference.py is cited by the atlas but was not supplied",
    },
    "nodes": ["A", "B", "H", "W"], "reference_node": "B",
    "components": [
        {"id": "L2", "kind": "inductor", "nodes": ["A", "H"], "value": 0.0032,
         "unit": "H", "evidence": "documentary-nominal", "source_page": 271, "topology_page": 272},
        {"id": "L3", "kind": "inductor", "nodes": ["A", "W"], "value": 0.0052,
         "unit": "H", "evidence": "documentary-nominal", "source_page": 271, "topology_page": 272},
        {"id": "C16A", "kind": "capacitor", "nodes": ["H", "B"], "value": 0.0000078,
         "unit": "F", "evidence": "documentary-nominal", "source_page": 271, "topology_page": 272},
        {"id": "C16B", "kind": "capacitor", "nodes": ["W", "B"], "value": 0.0000125,
         "unit": "F", "evidence": "documentary-nominal", "source_page": 271, "topology_page": 272},
    ],
    "ideal_loads": [
        {"id": "RT", "nodes": ["A", "H"], "resistance": 16.0, "unit": "ohm",
         "evidence": "explicit-ideal-test-assumption", "source_page": 273},
        {"id": "RW", "nodes": ["W", "B"], "resistance": 16.0, "unit": "ohm",
         "evidence": "explicit-ideal-test-assumption", "source_page": 273},
    ],
    "ports": {
        "input_voltage": {"positive_node": "A", "negative_node": "B", "unit": "V"},
        "input_current": {"positive_direction": "source into A", "unit": "A"},
        "treble_voltage": {"positive_node": "A", "negative_node": "H", "unit": "V"},
        "treble_current": {"positive_direction": "A to H through RT", "unit": "A"},
        "bass_voltage": {"positive_node": "W", "negative_node": "B", "unit": "V"},
        "bass_current": {"positive_direction": "W to B through RW", "unit": "A"},
    },
    "simulation_assumptions": {
        "source": "ideal imposed input voltage", "source_impedance_ohm": 0.0,
        "inductor_series_resistance_ohm": 0.0,
        "capacitor_loss": "ideal; no ESR or leakage in this numerical fixture",
        "driver_loads": "constant resistors; not loudspeaker models",
        "acoustics": "absent", "engine_integration": False, "physical_measurement_claim": False,
    },
    "unknown_physical_fields": {
        "reason": "No identified specimen, primary-drawing independent transcription or calibrated measurements acquired",
        "winding_resistance_ohm": None, "capacitor_esr_ohm": None,
        "capacitor_leakage_ohm": None, "actual_driver_complex_impedances": None,
        "amplifier_source_impedance": None, "acoustic_polarity": None,
        "serial_applicability": None, "measurement_uncertainty": None,
    },
    "numerics": {
        "sample_rates_hz": [44100, 48000, 96000, 192000],
        "state_order": ["V(H)-V(B)", "V(W)-V(B)", "I(L2:A->H)", "I(L3:A->W)"],
        "input_reconstruction": "endpoint-trapezoidal", "prewarp": False,
        "max_block_frames": 4096, "default_loads_only_are_atlas_fixture": True,
        "alternative_resistive_load_range_ohm": [1.0, 1024.0],
        "limits_are_computational_not_device_ratings": True,
        "max_abs_input_volts": 64.0, "max_abs_capacitor_volts": 65536.0,
        "max_abs_inductor_amps": 256.0, "max_energy_joules": 1000000.0,
    },
}


class ReferenceError(ValueError):
    """An inadmissible registry, experiment, or numerical result."""


def _match(actual: Any, expected: Any, path: str) -> None:
    if isinstance(expected, dict):
        if not isinstance(actual, dict) or set(actual) != set(expected):
            raise ReferenceError(f"{path}: fields must be exactly {', '.join(expected)}")
        for name, value in expected.items():
            _match(actual[name], value, f"{path}.{name}")
    elif isinstance(expected, list):
        if not isinstance(actual, list) or len(actual) != len(expected):
            raise ReferenceError(f"{path}: expected ordered list of {len(expected)} entries")
        for index, value in enumerate(expected):
            _match(actual[index], value, f"{path}[{index}]")
    elif isinstance(expected, float):
        if (type(actual) not in (int, float) or actual != expected
                or not math.isfinite(actual)):
            raise ReferenceError(f"{path}: expected finite documentary/fixture value {expected!r}")
    elif type(actual) is not type(expected) or actual != expected:
        raise ReferenceError(f"{path}: expected {expected!r}")


def validate_registry(registry: Any) -> None:
    """Reject unknown fields and every departure from this v1 model contract."""
    _match(registry, EXPECTED_REGISTRY, "registry")


def _no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ReferenceError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _no_nonfinite(text: str) -> None:
    raise ReferenceError(f"nonfinite JSON number: {text}")


def _read_registry(path: Path) -> tuple[dict[str, Any], bytes]:
    try:
        with path.open("rb") as stream:
            raw = stream.read(MAX_REGISTRY_BYTES + 1)
        if len(raw) > MAX_REGISTRY_BYTES:
            raise ReferenceError(f"registry exceeds {MAX_REGISTRY_BYTES} bytes")
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_no_duplicate_keys,
                           parse_constant=_no_nonfinite)
    except ReferenceError:
        raise
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        raise ReferenceError(f"cannot read registry: {exc}") from exc
    validate_registry(value)
    return value, raw


def load_registry(path: Path | str = DEFAULT_REGISTRY) -> dict[str, Any]:
    return _read_registry(Path(path))[0]


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def _number(value: Any, name: str, minimum: float, maximum: float) -> float:
    if type(value) not in (int, float):
        raise ReferenceError(f"{name} must be a real number")
    try:
        number = float(value)
    except OverflowError as exc:
        raise ReferenceError(f"{name} must be finite") from exc
    if not math.isfinite(number) or not minimum <= number <= maximum:
        raise ReferenceError(f"{name} must be finite and in [{minimum}, {maximum}]")
    return number


@dataclass(frozen=True)
class Element:
    id: str
    kind: str
    positive: str
    negative: str
    value: float


@dataclass(frozen=True)
class Network:
    components: tuple[Element, ...]
    treble_ohms: float
    bass_ohms: float
    registry_canonical_sha256: str
    registry_bytes_sha256: str | None = None

    @property
    def nominal_loads(self) -> bool:
        return self.treble_ohms == 16.0 and self.bass_ohms == 16.0


@dataclass(frozen=True)
class Response:
    treble_gain: complex
    bass_gain: complex
    input_admittance: complex
    normalized_residual: float | None = None
    node_voltages: tuple[tuple[str, complex], ...] = ()


def prepare_network(registry: dict[str, Any], *, treble_ohms: float = 16.0,
                    bass_ohms: float = 16.0) -> Network:
    validate_registry(registry)
    treble = _number(treble_ohms, "treble_ohms", 1.0, 1024.0)
    bass = _number(bass_ohms, "bass_ohms", 1.0, 1024.0)
    elements = [Element(row["id"], row["kind"], *row["nodes"], float(row["value"]))
                for row in registry["components"]]
    for row, resistance in zip(registry["ideal_loads"], (treble, bass)):
        elements.append(Element(row["id"], "resistor", *row["nodes"], resistance))
    return Network(tuple(elements), treble, bass, hashlib.sha256(_canonical(registry)).hexdigest())


def load_network(path: Path | str = DEFAULT_REGISTRY, *, treble_ohms: float = 16.0,
                 bass_ohms: float = 16.0) -> Network:
    registry, raw = _read_registry(Path(path))
    network = prepare_network(registry, treble_ohms=treble_ohms, bass_ohms=bass_ohms)
    return Network(network.components, network.treble_ohms, network.bass_ohms,
                   network.registry_canonical_sha256, hashlib.sha256(raw).hexdigest())


def default_frequency_grid() -> tuple[float, ...]:
    """121 log points plus three literal points; preserve requested multiplicity."""
    grid = [10.0 * 2000.0 ** (index / 120.0) for index in range(121)]
    grid[0], grid[-1] = 10.0, 20000.0
    return tuple(sorted(grid + [400.0, 800.0, 1600.0]))


def _frequency(value: float) -> float:
    # No audio-band or Nyquist assumption: the later native comparison uses
    # warped analog frequencies. Nonfinite intermediate arithmetic is rejected.
    return _number(value, "frequency_hz", 0.0, sys.float_info.max / math.tau)


def _finite_response(response: Response) -> Response:
    values = (response.treble_gain, response.bass_gain, response.input_admittance)
    if not all(math.isfinite(v.real) and math.isfinite(v.imag) for v in values):
        raise ReferenceError("nonfinite analog response")
    return response


def analog_response(network: Network, frequency_hz: float) -> Response:
    """Independent series/parallel impedances; floating RT remains across A-H."""
    frequency = _frequency(frequency_hz)
    if frequency == 0.0:
        return Response(0.0j, 1.0 + 0.0j, complex(1.0 / network.bass_ohms))
    values = {element.id: element.value for element in network.components}
    s = complex(0.0, math.tau * frequency)
    try:
        parallel_treble = 1.0 / (1.0 / (s * values["L2"]) + 1.0 / values["RT"])
        parallel_bass = 1.0 / (s * values["C16B"] + 1.0 / values["RW"])
        treble_branch = parallel_treble + 1.0 / (s * values["C16A"])
        bass_branch = s * values["L3"] + parallel_bass
        return _finite_response(Response(parallel_treble / treble_branch,
                                         parallel_bass / bass_branch,
                                         1.0 / treble_branch + 1.0 / bass_branch))
    except (ArithmeticError, ValueError) as exc:
        raise ReferenceError(f"unresolved series/parallel calculation: {exc}") from exc


def _solve(matrix: list[list[complex]], rhs: list[complex]) -> tuple[list[complex], float]:
    n = len(rhs)
    a = [row[:] + [value] for row, value in zip(matrix, rhs)]
    for column in range(n):
        pivot = max(range(column, n), key=lambda row: abs(a[row][column]))
        if abs(a[pivot][column]) == 0.0:
            raise ReferenceError("singular nodal matrix")
        a[column], a[pivot] = a[pivot], a[column]
        for row in range(column + 1, n):
            multiplier = a[row][column] / a[column][column]
            for k in range(column, n + 1):
                a[row][k] -= multiplier * a[column][k]
    solution = [0.0j] * n
    for row in reversed(range(n)):
        solution[row] = (a[row][n] - sum(a[row][k] * solution[k]
                         for k in range(row + 1, n))) / a[row][row]
    residual = max(abs(sum(matrix[row][k] * solution[k] for k in range(n)) - rhs[row])
                   for row in range(n))
    norm_m = max(sum(abs(value) for value in row) for row in matrix)
    norm_x = max(abs(value) for value in solution)
    norm_r = max(abs(value) for value in rhs)
    normalized = residual / max(1.0, norm_m * norm_x + norm_r)
    if (not math.isfinite(normalized)
            or not all(math.isfinite(v.real) and math.isfinite(v.imag) for v in solution)):
        raise ReferenceError("nonfinite nodal solve")
    return solution, normalized


def nodal_response(network: Network, frequency_hz: float) -> Response:
    """Stamp every physical edge into KCL; solve unknown H and W potentials."""
    frequency = _frequency(frequency_hz)
    if frequency == 0.0:
        # L2/L3 are ideal shorts and C16A/C16B open; A=H=W=1, B=0.
        return Response(0.0j, 1.0 + 0.0j, complex(1.0 / network.bass_ohms), 0.0,
                        (("A", 1.0 + 0.0j), ("B", 0.0j), ("H", 1.0 + 0.0j), ("W", 1.0 + 0.0j)))
    known = {"A": 1.0 + 0.0j, "B": 0.0j}
    unknown = {"H": 0, "W": 1}
    matrix = [[0.0j] * 2 for _ in range(2)]
    rhs = [0.0j] * 2
    s = complex(0.0, math.tau * frequency)
    edges = []
    try:
        for element in network.components:
            if element.kind == "inductor":
                admittance = 1.0 / (s * element.value)
            elif element.kind == "capacitor":
                admittance = s * element.value
            else:
                admittance = complex(1.0 / element.value)
            edges.append((element.positive, element.negative, admittance))
            for here, there in ((element.positive, element.negative),
                                (element.negative, element.positive)):
                if here not in unknown:
                    continue
                row = unknown[here]
                matrix[row][row] += admittance
                if there in unknown:
                    matrix[row][unknown[there]] -= admittance
                else:
                    rhs[row] += admittance * known[there]
        solution, residual = _solve(matrix, rhs)
        voltages = {**known, **{name: solution[index] for name, index in unknown.items()}}
        # By KCL the source current equals total passive current returning to
        # the reference node. Sum those stamped edges rather than the source
        # edges: near DC, A/H/W are almost equipotential and subtracting A-H
        # or A-W before dividing by s*L destroys the small reactive current.
        # The graph, not a copied transfer polynomial, selects these terms.
        source_current = sum(y * (voltages[p] - voltages[q]) if q == "B"
                             else y * (voltages[q] - voltages[p])
                             for p, q, y in edges if "B" in (p, q))
        return _finite_response(Response(voltages["A"] - voltages["H"],
                                         voltages["W"] - voltages["B"], source_current,
                                         residual, tuple(sorted(voltages.items()))))
    except (ArithmeticError, ValueError) as exc:
        raise ReferenceError(f"unresolved nodal calculation: {exc}") from exc


def normalized_error(actual: complex, reference: complex) -> float:
    return abs(actual - reference) / max(1.0, abs(reference))


def _response_json(response: Response) -> dict[str, Any]:
    result = {name: {"real": getattr(response, name).real, "imag": getattr(response, name).imag}
              for name in ("treble_gain", "bass_gain", "input_admittance")}
    result["normalized_residual"] = response.normalized_residual
    return result


def make_report(network: Network) -> dict[str, Any]:
    rows = []
    maxima = {name: 0.0 for name in ("treble_gain", "bass_gain", "input_admittance")}
    max_residual = 0.0
    max_power_error = 0.0
    grid = default_frequency_grid()
    for frequency in grid:
        analytic = analog_response(network, frequency)
        nodal = nodal_response(network, frequency)
        errors = {name: normalized_error(getattr(nodal, name), getattr(analytic, name))
                  for name in maxima}
        for name, value in errors.items():
            maxima[name] = max(maxima[name], value)
        max_residual = max(max_residual, nodal.normalized_residual or 0.0)
        dissipation = (abs(nodal.treble_gain) ** 2 / network.treble_ohms
                       + abs(nodal.bass_gain) ** 2 / network.bass_ohms)
        max_power_error = max(max_power_error,
                              abs(nodal.input_admittance.real - dissipation) / max(1.0, dissipation))
        rows.append({"frequency_hz": frequency, "series_parallel": _response_json(analytic),
                     "nodal": _response_json(nodal), "normalized_errors": errors})
    return {
        "schema_version": 1, "reference_id": REFERENCE_ID,
        "model_id": EXPECTED_REGISTRY["model_id"],
        "native_realization_id_for_later_comparison": EXPECTED_REGISTRY["realization_id"],
        "registry_canonical_sha256": network.registry_canonical_sha256,
        "registry_bytes_sha256": network.registry_bytes_sha256,
        "reference_code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "evidence_class": EXPECTED_REGISTRY["evidence_class"],
        "source": EXPECTED_REGISTRY["source"],
        "target": EXPECTED_REGISTRY["target"],
        "atlas_bytes_verified_by_this_tool": False,
        "physical_measurement_claim": False, "engine_integration": False,
        "unknown_physical_fields": EXPECTED_REGISTRY["unknown_physical_fields"],
        "simulation_assumptions": EXPECTED_REGISTRY["simulation_assumptions"],
        "experiment": {"kind": "atlas-ideal-resistor-fixture" if network.nominal_loads
                       else "alternative-resistor-experiment", "treble_ohms": network.treble_ohms,
                       "bass_ohms": network.bass_ohms, "actual_driver_measurements": False},
        "units": {"frequency": "Hz", "treble_gain": "V/V", "bass_gain": "V/V",
                  "input_admittance": "A/V"},
        "grid": {"id": GRID_ID, "requested_count": len(grid), "unique_count": len(set(grid)),
                 "duplicate_count": len(grid) - len(set(grid)), "dc_is_separate": True},
        "dc": {"frequency_hz": 0.0, "series_parallel": _response_json(analog_response(network, 0.0)),
               "nodal": _response_json(nodal_response(network, 0.0))},
        "acceptance": {"normalized_error_limit": ERROR_LIMIT, "maximum_errors": maxima,
                       "maximum_nodal_residual": max_residual,
                       "maximum_normalized_power_balance_error": max_power_error,
                       "passed": max(maxima.values()) <= ERROR_LIMIT,
                       "scope": "analog algebra only; no native processing, same-Hz audible or physical qualification"},
        "responses": rows,
    }


def _write_output(path: Path, text: str, registry_path: Path) -> None:
    if path.resolve() in (registry_path.resolve(), Path(__file__).resolve()):
        raise ReferenceError("output must not replace the registry or reference source")
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                         dir=path.parent, prefix=f".{path.name}.",
                                         suffix=".tmp", delete=False) as stream:
            temporary = stream.name
            stream.write(text)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            Path(temporary).unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--treble-ohms", type=float, default=16.0,
                        help="Explicit constant-resistor experiment, 1..1024 ohm (default 16)")
    parser.add_argument("--bass-ohms", type=float, default=16.0,
                        help="Explicit constant-resistor experiment, 1..1024 ohm (default 16)")
    parser.add_argument("--output", type=Path, help="JSON report path; omit or use - for stdout")
    args = parser.parse_args(argv)
    try:
        network = load_network(args.registry, treble_ohms=args.treble_ohms, bass_ohms=args.bass_ohms)
        report = make_report(network)
        text = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False) + "\n"
        if args.output is None or str(args.output) == "-":
            sys.stdout.write(text)
        else:
            _write_output(args.output, text, args.registry)
        return 0 if report["acceptance"]["passed"] else 1
    except (ReferenceError, OSError, ValueError) as exc:
        print(f"crossover_reference: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
