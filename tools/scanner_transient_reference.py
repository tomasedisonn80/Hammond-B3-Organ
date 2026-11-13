#!/usr/bin/env python3
"""Independent full-circuit transient reference for the nominal scanner line.

Every resistor and reactive companion is stamped from the admitted signed graph.
The native reduced-state model and the AC reference's solver are not imported.
Trapezoidal companions establish a matched-step reference; only an explicitly
converged refinement study can support a continuous-time accuracy comparison.
This offline standard-library tool is not an audio-callback implementation.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import stat
import sys
import tempfile
from typing import Sequence

from compile_scanner_line import load_profile_with_digest, normalized_profile


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROFILE = ROOT / "data/scanner/atlas-late-b3-nominal-v1.json"
REFERENCE_ID = "scanner-full-graph-trapezoidal-reference-v1"
MODES = ("vibrato", "chorus")
MAX_KNOTS = 10000
MAX_INTERNAL_STEPS = 1_280_000
MAX_REPORT_BYTES = 64 * 1024 * 1024
MAX_INPUT_VOLTS = 64.0
MAX_CAPACITOR_VOLTS = 1.0e6
MAX_INDUCTOR_AMPS = 100.0
MAX_NODE_VOLTS = 1.0e9
MAX_FRAMES = (1 << 64) - 1
MNA_CURRENT_SCALE_OHMS = 15000.0
RESIDUAL_LIMIT = 1.0e-9
FIXTURES = ("step-positive", "step-negative", "pulse-positive", "pulse-negative",
            "multisine", "charged-c1", "charged-c18", "energized-l1", "energized-l18")


class TransientError(ValueError):
    """Invalid input, inconsistent state or failed numerical reference solve."""


def _number(value: object, name: str, limit: float) -> float:
    if type(value) not in (int, float):
        raise TransientError(f"{name} must be a finite real number")
    try:
        result = float(value)
    except OverflowError as exc:
        raise TransientError(f"{name} exceeds its finite bound") from exc
    if not math.isfinite(result) or abs(result) > limit:
        raise TransientError(f"{name} exceeds finite bound {limit}")
    return result


def _rate(value: object) -> float:
    result = _number(value, "sample_rate", 12_288_000.0)
    if result < 8000.0:
        raise TransientError("reference sample_rate must be in [8000,12288000] Hz")
    return result


def _mode(value: object) -> str:
    if type(value) is not str or value not in MODES:
        raise TransientError("mode must be vibrato or chorus")
    return value


def _vector(value: object, name: str, limit: float) -> tuple[float, ...]:
    if type(value) not in (tuple, list) or len(value) != 18:
        raise TransientError(f"{name} must have exactly eighteen entries")
    return tuple(_number(v, name, limit) for v in value)


@dataclass(frozen=True)
class PhysicalState:
    capacitor_volts: tuple[float, ...] = (0.0,) * 18
    inductor_amps: tuple[float, ...] = (0.0,) * 18
    previous_input_volts: float = 0.0
    frames: int = 0


def _state(value: PhysicalState | None) -> PhysicalState:
    if value is None:
        return PhysicalState()
    if type(value) is not PhysicalState:
        raise TransientError("state must be a PhysicalState")
    if type(value.frames) is not int or not 0 <= value.frames <= MAX_FRAMES:
        raise TransientError("state frame count is outside uint64 range")
    return PhysicalState(_vector(value.capacitor_volts, "capacitor_volts", MAX_CAPACITOR_VOLTS),
                         _vector(value.inductor_amps, "inductor_amps", MAX_INDUCTOR_AMPS),
                         _number(value.previous_input_volts, "previous_input_volts", MAX_INPUT_VOLTS),
                         value.frames)


class _Cholesky:
    """Independent symmetric diagonal scaling and sparse triangular solves."""

    def __init__(self, matrix: list[list[float]]) -> None:
        count = len(matrix)
        self.scale = tuple(math.sqrt(matrix[i][i]) for i in range(count))
        if any(not math.isfinite(v) or v <= 0.0 for v in self.scale):
            raise TransientError("nonpositive nodal diagonal")
        lower = [[0.0] * count for _ in range(count)]
        for row in range(count):
            for column in range(row + 1):
                residual = matrix[row][column] / (self.scale[row] * self.scale[column])
                for k in range(column):
                    residual -= lower[row][k] * lower[column][k]
                if row == column:
                    if not math.isfinite(residual) or residual <= 1.0e-15:
                        raise TransientError("nodal matrix is singular or not positive definite")
                    lower[row][column] = math.sqrt(residual)
                else:
                    lower[row][column] = residual / lower[column][column]
        # Only exact zeros are omitted; no numerical sparsification threshold.
        self.diagonal = tuple(lower[i][i] for i in range(count))
        self.rows = tuple(tuple((j, lower[i][j]) for j in range(i) if lower[i][j] != 0.0)
                          for i in range(count))
        self.columns = tuple(tuple((j, lower[j][i]) for j in range(i + 1, count)
                                   if lower[j][i] != 0.0) for i in range(count))

    def solve(self, rhs: Sequence[float]) -> list[float]:
        values = [rhs[i] / self.scale[i] for i in range(len(self.scale))]
        for row, entries in enumerate(self.rows):
            value = values[row]
            for column, coefficient in entries:
                value -= coefficient * values[column]
            values[row] = value / self.diagonal[row]
        for row in range(len(values) - 1, -1, -1):
            value = values[row]
            for column, coefficient in self.columns[row]:
                value -= coefficient * values[column]
            values[row] = value / self.diagonal[row]
        return [values[i] / self.scale[i] for i in range(len(values))]


class _AlgebraicInverse:
    """Off-line Gauss-Jordan solve of the scaled, nonsingular initial-state MNA.

    This inverts an algebraic constraint system, never the singular energy E.
    It is separate from the Cholesky companion solver and any native/AC LU.
    """

    def __init__(self, matrix: list[list[float]]) -> None:
        count = len(matrix)
        work = [row[:] + [float(i == j) for j in range(count)]
                for i, row in enumerate(matrix)]
        for column in range(count):
            pivot = max(range(column, count), key=lambda row: abs(work[row][column]))
            if abs(work[pivot][column]) < 1.0e-14:
                raise TransientError("initial physical-state constraints are singular")
            work[column], work[pivot] = work[pivot], work[column]
            divisor = work[column][column]
            work[column] = [value / divisor for value in work[column]]
            for row in range(count):
                if row == column:
                    continue
                multiplier = work[row][column]
                if multiplier != 0.0:
                    work[row] = [a - multiplier * b for a, b in zip(work[row], work[column])]
        self.inverse = tuple(tuple(row[count:]) for row in work)
        self.matrix = tuple(tuple(row) for row in matrix)
        self.norm = max(sum(abs(v) for v in row) for row in matrix)
        self.condition_inf_estimate = self.norm * max(sum(abs(v) for v in row) for row in self.inverse)

    def solve(self, rhs: Sequence[float]) -> tuple[list[float], float]:
        result = [math.fsum(a * b for a, b in zip(row, rhs)) for row in self.inverse]
        numerator = max(abs(math.fsum(a * b for a, b in zip(row, result)) - value)
                        for row, value in zip(self.matrix, rhs))
        denominator = self.norm * max(map(abs, result), default=0.0) + max(map(abs, rhs), default=0.0)
        residual = numerator / denominator if denominator else (0.0 if numerator == 0.0 else math.inf)
        if not math.isfinite(residual) or residual > RESIDUAL_LIMIT:
            raise TransientError("initial MNA residual exceeds its declared bound")
        return result, residual


@dataclass(frozen=True)
class _Branch:
    name: str
    positive: int
    negative: int
    value: float


@dataclass(frozen=True)
class _History:
    physical: PhysicalState
    nodes: tuple[float, ...]
    capacitor_currents: tuple[float, ...]
    inductor_voltages: tuple[float, ...]
    residual: float
    kcl_residual: float


class _Topology:
    def __init__(self, nodes: tuple[str, ...], drive_node: int, ground_node: int,
                 return_node: int, resistors: tuple[_Branch, ...], capacitors: tuple[_Branch, ...],
                 inductors: tuple[_Branch, ...], sample_rate: float, mode: str) -> None:
        self.nodes = nodes
        self.drive_node = drive_node
        self.return_node = return_node
        self.resistors, self.capacitors, self.inductors = resistors, capacitors, inductors
        fixed = {ground_node, drive_node}
        if mode == "vibrato":
            fixed.add(return_node)
        # Divider-first ordering keeps the graph factor sparse without reducing
        # electrical state or assuming a cascade of unloaded sections.
        self.free = tuple(sorted((i for i in range(len(nodes)) if i not in fixed),
                                 key=lambda i: (nodes[i] == "r", nodes[i][0],
                                                int(nodes[i][1:]) if nodes[i][1:].isdigit() else 0)))
        self.index = {node: row for row, node in enumerate(self.free)}
        count = len(self.free)
        matrix = [[0.0] * count for _ in range(count)]
        drive = [0.0] * count
        self.gc = tuple(2.0 * sample_rate * branch.value for branch in capacitors)
        self.gl = tuple(1.0 / (2.0 * sample_rate * branch.value) for branch in inductors)

        def stamp(target: list[list[float]], coupling: list[float], branch: _Branch,
                  conductance: float) -> None:
            for a, b in ((branch.positive, branch.negative), (branch.negative, branch.positive)):
                row = self.index.get(a)
                if row is None:
                    continue
                target[row][row] += conductance
                column = self.index.get(b)
                if column is not None:
                    target[row][column] -= conductance
                elif b == drive_node:
                    coupling[row] += conductance

        resistance = [[0.0] * count for _ in range(count)]
        resistance_drive = [0.0] * count
        for branch in resistors:
            stamp(matrix, drive, branch, 1.0 / branch.value)
            stamp(resistance, resistance_drive, branch, 1.0 / branch.value)
        for branches, conductances in ((capacitors, self.gc), (inductors, self.gl)):
            for branch, conductance in zip(branches, conductances):
                stamp(matrix, drive, branch, conductance)
        self.drive = tuple(drive)
        self.factor = _Cholesky(matrix)
        self.matrix_norm = max(sum(abs(v) for v in row) for row in matrix)
        inverse_columns = [self.factor.solve([float(i == j) for i in range(count)])
                           for j in range(count)]
        self.condition_inf_estimate = self.matrix_norm * max(
            sum(abs(inverse_columns[j][i]) for j in range(count)) for i in range(count))
        scale = self.factor.scale
        scaled_norm = max(sum(abs(matrix[i][j] / (scale[i] * scale[j])) for j in range(count))
                          for i in range(count))
        self.scaled_condition_inf_estimate = scaled_norm * max(
            sum(abs(scale[i] * inverse_columns[j][i] * scale[j]) for j in range(count))
            for i in range(count))
        self.dimension = count
        self.reactive_indices = tuple((self.index.get(branch.positive), self.index.get(branch.negative))
                                      for branch in (*capacitors, *inductors))
        # Initial-state MNA: known inductor currents are current sources;
        # capacitor voltages are imposed ideal source constraints, with unknown
        # capacitor currents scaled by 15000 ohms. Only resistors stamp G.
        size = count + len(capacitors)
        initial = [[0.0] * size for _ in range(size)]
        for row in range(count):
            for column in range(count):
                initial[row][column] = resistance[row][column] * MNA_CURRENT_SCALE_OHMS
        for cap_index, branch in enumerate(capacitors):
            for node, sign in ((branch.positive, 1.0), (branch.negative, -1.0)):
                row = self.index.get(node)
                if row is not None:
                    initial[row][count + cap_index] += sign
                    initial[count + cap_index][row] += sign
        self.initial_system = _AlgebraicInverse(initial)
        self.initial_drive = tuple(value * MNA_CURRENT_SCALE_OHMS for value in resistance_drive)

    def full_nodes(self, solved: Sequence[float], input_volts: float) -> tuple[float, ...]:
        result = [0.0] * len(self.nodes)
        result[self.drive_node] = input_volts
        for node, value in zip(self.free, solved):
            result[node] = value
        if any(not math.isfinite(value) or abs(value) > MAX_NODE_VOLTS for value in result):
            raise TransientError("solved node voltage exceeds finite reference bound")
        return tuple(result)

    def _kcl(self, nodes: Sequence[float], capacitor_currents: Sequence[float],
             inductor_currents: Sequence[float]) -> tuple[float, float]:
        balance = [0.0] * len(nodes)
        for branches, currents in ((self.capacitors, capacitor_currents),
                                   (self.inductors, inductor_currents)):
            for branch, current in zip(branches, currents):
                balance[branch.positive] += current
                balance[branch.negative] -= current
        for branch in self.resistors:
            current = (nodes[branch.positive] - nodes[branch.negative]) / branch.value
            balance[branch.positive] += current
            balance[branch.negative] -= current
        return max(abs(balance[node]) for node in self.free), balance[self.drive_node]

    def reconstruct(self, state: PhysicalState) -> _History:
        rhs = [value * state.previous_input_volts for value in self.initial_drive] + list(state.capacitor_volts)
        for branch, current in zip(self.inductors, state.inductor_amps):
            positive, negative = self.index.get(branch.positive), self.index.get(branch.negative)
            if positive is not None:
                rhs[positive] -= current * MNA_CURRENT_SCALE_OHMS
            if negative is not None:
                rhs[negative] += current * MNA_CURRENT_SCALE_OHMS
        for cap_index, branch in enumerate(self.capacitors):
            if branch.positive == self.drive_node:
                rhs[self.dimension + cap_index] -= state.previous_input_volts
            if branch.negative == self.drive_node:
                rhs[self.dimension + cap_index] += state.previous_input_volts
        solved, residual = self.initial_system.solve(rhs)
        nodes = self.full_nodes(solved[:self.dimension], state.previous_input_volts)
        currents = tuple(value / MNA_CURRENT_SCALE_OHMS for value in solved[self.dimension:])
        voltages = tuple(nodes[b.positive] - nodes[b.negative] for b in self.inductors)
        kcl, _ = self._kcl(nodes, currents, state.inductor_amps)
        return _History(state, nodes, currents, voltages, residual, kcl)

    def advance(self, old: _History, input_volts: float) -> _History:
        if old.physical.frames == MAX_FRAMES:
            raise TransientError("reference frame timeline would overflow")
        cap_history = tuple(-current - conductance * voltage for current, conductance, voltage in
                            zip(old.capacitor_currents, self.gc, old.physical.capacitor_volts))
        ind_history = tuple(current + conductance * voltage for current, conductance, voltage in
                            zip(old.physical.inductor_amps, self.gl, old.inductor_voltages))
        rhs = [value * input_volts for value in self.drive]
        for (positive, negative), current in zip(self.reactive_indices, (*cap_history, *ind_history)):
            if positive is not None:
                rhs[positive] -= current
            if negative is not None:
                rhs[negative] += current
        solved = self.factor.solve(rhs)
        nodes = self.full_nodes(solved, input_volts)
        cap_volts = tuple(nodes[b.positive] - nodes[b.negative] for b in self.capacitors)
        ind_volts = tuple(nodes[b.positive] - nodes[b.negative] for b in self.inductors)
        cap_current = tuple(g * v + h for g, v, h in zip(self.gc, cap_volts, cap_history))
        ind_current = tuple(g * v + h for g, v, h in zip(self.gl, ind_volts, ind_history))
        physical = _state(PhysicalState(cap_volts, ind_current, input_volts, old.physical.frames + 1))
        kcl, _ = self._kcl(nodes, cap_current, ind_current)
        denominator = self.matrix_norm * max(map(abs, solved), default=0.0) + max(map(abs, rhs), default=0.0)
        residual = kcl / denominator if denominator else (0.0 if kcl == 0.0 else math.inf)
        if not math.isfinite(residual) or residual > RESIDUAL_LIMIT:
            raise TransientError("companion nodal residual exceeds its declared bound")
        return _History(physical, nodes, cap_current, ind_volts, residual, kcl)


class TransientLine:
    """Owned offline reference with physical-state-preserving mode/rate changes."""

    def __init__(self, profile: dict, sample_rate: float, mode: str,
                 state: PhysicalState | None = None) -> None:
        graph = normalized_profile(profile)
        self.model_id = graph["model_id"]
        canonical = json.dumps(profile, sort_keys=True, separators=(",", ":"), allow_nan=False)
        self.authoring_canonical_sha256 = hashlib.sha256(canonical.encode()).hexdigest()
        self._nodes = tuple(graph["nodes"])
        index = {name: i for i, name in enumerate(self._nodes)}
        self._drive_node = index[graph["drive"]["positive"]]
        self._ground_node = index[graph["ground"]]
        self._return_node = index[graph["return_switch"]["positive"]]
        self._taps = tuple((item["id"], index[item["positive"]], index[item["negative"]])
                           for item in graph["outputs"])
        self._branches = {}
        for kind in ("R", "C", "L"):
            records = [item for item in graph["components"] if item["kind"] == kind]
            if kind in ("C", "L"):
                records.sort(key=lambda item: int(item["id"][1:]))
            self._branches[kind] = tuple(_Branch(item["id"], index[item["positive"]],
                                                index[item["negative"]], item["value"]["si_value"])
                                         for item in records)
        self._rate = _rate(sample_rate)
        self._mode = _mode(mode)
        self._topologies = self._prepare(self._rate)
        self._history = self._topologies[self._mode].reconstruct(_state(state))

    def _prepare(self, sample_rate: float) -> dict[str, _Topology]:
        return {mode: _Topology(self._nodes, self._drive_node, self._ground_node, self._return_node,
                                self._branches["R"], self._branches["C"], self._branches["L"],
                                sample_rate, mode) for mode in MODES}

    @property
    def sample_rate(self) -> float:
        return self._rate

    @property
    def mode(self) -> str:
        return self._mode

    def state(self) -> PhysicalState:
        return self._history.physical

    def restore_state(self, state: PhysicalState) -> None:
        if type(state) is not PhysicalState:
            raise TransientError("restore_state needs an explicit PhysicalState")
        candidate = self._topologies[self._mode].reconstruct(_state(state))
        self._history = candidate

    def set_mode(self, mode: str) -> None:
        selected = _mode(mode)
        if selected != self._mode:
            candidate = self._topologies[selected].reconstruct(self.state())
            self._mode, self._history = selected, candidate

    def reconfigure_sample_rate(self, sample_rate: float) -> None:
        selected = _rate(sample_rate)
        if selected == self._rate:
            return
        topologies = self._prepare(selected)
        history = topologies[self._mode].reconstruct(self.state())
        self._rate, self._topologies, self._history = selected, topologies, history

    def preparation_diagnostics(self) -> dict:
        """Condition estimates use computed inverses; they are not rigorous bounds."""
        modes = {}
        for mode, topology in self._topologies.items():
            estimates = {"physical_companion_condition_inf_estimate": topology.condition_inf_estimate,
                         "scaled_companion_condition_inf_estimate": topology.scaled_condition_inf_estimate,
                         "scaled_initial_mna_condition_inf_estimate": topology.initial_system.condition_inf_estimate}
            modes[mode] = {"free_node_count": topology.dimension,
                           "initial_mna_dimension": len(topology.initial_system.matrix), **estimates,
                           "conditioning_limited": any(value * 2.0**-52 > 1.0e-4
                                                       for value in estimates.values())}
        return {"sample_rate": self._rate,
                "condition_method": "infinity norms of matrices and binary64 computed inverses",
                "companion_residual_matrix": "unscaled physical nodal conductance G",
                "companion_factor_scaling": "D^-1 G D^-1; D_ii=sqrt(G_ii)",
                "initial_mna_scaling": "KCL rows and capacitor-current unknowns multiplied by 15000 ohms",
                "residual_limit": RESIDUAL_LIMIT, "modes": modes}

    def _frame(self, history: _History, mode: str, advanced: bool) -> dict:
        state, nodes = history.physical, history.nodes
        _, source_current = self._topologies[mode]._kcl(nodes, history.capacitor_currents,
                                                       state.inductor_amps)
        energy = 0.5 * math.fsum(branch.value * value * value for branches, values in
                                 ((self._branches["C"], state.capacitor_volts),
                                  (self._branches["L"], state.inductor_amps))
                                 for branch, value in zip(branches, values))
        return {"frame": state.frames,
                "advanced": advanced, "sample_rate": self._rate, "mode": mode,
                "input_volts": state.previous_input_volts,
                "taps_volts": tuple(nodes[positive] - nodes[negative] for _, positive, negative in self._taps),
                "return_volts": nodes[self._return_node], "input_current_amps": source_current,
                "energy_joules": energy, "capacitor_volts": state.capacitor_volts,
                "inductor_amps": state.inductor_amps,
                "normalized_residual": history.residual, "kcl_residual_amps": history.kcl_residual}

    def observe(self) -> dict:
        return self._frame(self._history, self._mode, False)

    def process_frame(self, input_volts: float, mode: str | None = None) -> dict:
        value = _number(input_volts, "input_volts", MAX_INPUT_VOLTS)
        selected = self._mode if mode is None else _mode(mode)
        topology = self._topologies[selected]
        old = self._history if selected == self._mode else topology.reconstruct(self.state())
        candidate = topology.advance(old, value)
        frame = self._frame(candidate, selected, True)
        self._mode, self._history = selected, candidate
        return frame


def _inputs(values: Sequence[float]) -> tuple[float, ...]:
    if type(values) not in (list, tuple) or not 1 <= len(values) <= MAX_KNOTS:
        raise TransientError(f"inputs must contain 1..{MAX_KNOTS} knot values")
    return tuple(_number(value, "input knot", MAX_INPUT_VOLTS) for value in values)


def render_trace(profile: dict, inputs: Sequence[float], sample_rate: float, mode: str,
                 initial_state: PhysicalState | None = None, subdivisions: int = 1) -> list[dict]:
    """Interpolate the same knot polygon and report only its requested endpoints.

    Previous endpoint is t=-1/sample_rate; returned knot n is at n/sample_rate.
    Internal frame counts refer to solver substeps, not host knots.
    """
    values = _inputs(inputs)
    if type(subdivisions) is not int or subdivisions not in (1, 2, 4, 8, 16, 32, 64, 128):
        raise TransientError("subdivisions must be a power of two from 1 through 128")
    knot_rate = _rate(sample_rate)
    if len(values) * subdivisions > MAX_INTERNAL_STEPS:
        raise TransientError("trace exceeds internal-step bound")
    state = _state(initial_state)
    if state.frames > MAX_FRAMES - len(values) * subdivisions:
        raise TransientError("trace frame timeline would overflow")
    line = TransientLine(profile, knot_rate * subdivisions, mode, state)
    result = []
    previous = state.previous_input_volts
    for knot, value in enumerate(values):
        for step in range(1, subdivisions + 1):
            # Preserve the literal knot endpoint, rather than a rounded blend.
            current = value if step == subdivisions else previous + (value - previous) * (step / subdivisions)
            frame = line.process_frame(current)
        frame["knot"] = knot
        frame["time_seconds"] = knot / knot_rate
        result.append(frame)
        previous = value
    return result


def fixture(name: str, sample_rate: float = 48000.0, frames: int = 2400) -> tuple[tuple[float, ...], PhysicalState]:
    if name not in FIXTURES:
        raise TransientError("unknown transient fixture")
    rate = _rate(sample_rate)
    if type(frames) is not int or not 1 <= frames <= MAX_KNOTS:
        raise TransientError("fixture frame count is outside bounds")
    values = [0.0] * frames
    caps, currents = [0.0] * 18, [0.0] * 18
    if name.startswith("step-"):
        values = [1.0 if name.endswith("positive") else -1.0] * frames
    elif name.startswith("pulse-"):
        values[0] = 1.0 if name.endswith("positive") else -1.0
    elif name == "multisine":
        values = [sum(math.sin(2.0 * math.pi * frequency * n / rate)
                      for frequency in (137, 997, 3113, 5087, 6971)) / 5.0 for n in range(frames)]
    elif name == "charged-c1":
        caps[0] = 1.0
    elif name == "charged-c18":
        caps[17] = -1.0
    elif name == "energized-l1":
        currents[0] = 1.0e-4
    elif name == "energized-l18":
        currents[17] = -1.0e-4
    return tuple(values), PhysicalState(tuple(caps), tuple(currents))


def compare_traces(first: Sequence[dict], second: Sequence[dict]) -> dict:
    """Fixed-scale reference-refinement metrics; never fit gain or alignment."""
    if (type(first) not in (list, tuple) or type(second) not in (list, tuple)
            or not 1 <= len(first) <= MAX_KNOTS or len(first) != len(second)):
        raise TransientError("trace comparison needs equal nonempty knot counts")
    for trace in (first, second):
        for knot, frame in enumerate(trace):
            if type(frame) is not dict or type(frame.get("knot")) is not int or frame["knot"] != knot:
                raise TransientError("trace has a malformed knot record")
            _number(frame.get("time_seconds"), "trace time", 1.0e6)
            _mode(frame.get("mode"))
            _number(frame.get("input_volts"), "trace input", MAX_INPUT_VOLTS)
            for field, count, bound in (("taps_volts", 19, MAX_NODE_VOLTS),
                                        ("capacitor_volts", 18, MAX_CAPACITOR_VOLTS),
                                        ("inductor_amps", 18, MAX_INDUCTOR_AMPS)):
                values = frame.get(field)
                if type(values) not in (list, tuple) or len(values) != count:
                    raise TransientError(f"trace {field} dimensions are invalid")
                for value in values:
                    _number(value, field, bound)
            _number(frame.get("return_volts"), "trace return", MAX_NODE_VOLTS)
            _number(frame.get("input_current_amps"), "trace input current", 1.0e9)
    if any(any(a[key] != b[key] for key in ("knot", "time_seconds", "mode", "input_volts"))
           for a, b in zip(first, second)):
        raise TransientError("trace knot/time/mode/input coordinates differ")
    channels = []
    for field, count, scale, required in (("taps_volts", 19, 1.0, True),
                                         ("capacitor_volts", 18, 1.0, True),
                                         ("inductor_amps", 18, 1.0e-4, True),
                                         ("return_volts", 1, 1.0, False),
                                         ("input_current_amps", 1, 1.0e-4, False)):
        for index in range(count):
            differences = [((a[field][index] - b[field][index]) if count > 1 else (a[field] - b[field])) / scale
                           for a, b in zip(first, second)]
            if any(not math.isfinite(v) for v in differences):
                raise TransientError("nonfinite trace comparison")
            rms = math.sqrt(math.fsum(value * value for value in differences) / len(differences))
            maximum = max(map(abs, differences))
            channels.append({"field": field, "index": index if count > 1 else None,
                             "normalization": scale, "required": required,
                             "normalized_rms": rms, "normalized_maximum": maximum,
                             "within_reference_budget": rms <= 2.0e-6 and maximum <= 1.0e-5})
    return {"rms_bound": 2.0e-6, "maximum_bound": 1.0e-5, "channels": channels,
            "within_reference_budget": all(row["within_reference_budget"]
                                            for row in channels if row["required"])}


def refinement_study(profile: dict, inputs: Sequence[float], sample_rate: float, mode: str,
                     initial_state: PhysicalState | None = None,
                     refinements: Sequence[int] = (8, 16, 32, 64, 128)) -> dict:
    values = _inputs(inputs)
    if (type(refinements) not in (list, tuple) or not 3 <= len(refinements) <= 5
            or tuple(refinements) != (8, 16, 32, 64, 128)[:len(refinements)]):
        raise TransientError("refinements must be the frozen prefix 8,16,32[,64,128]")
    previous, records, consecutive, performed = None, [], 0, []
    for factor in refinements:
        trace = render_trace(profile, values, sample_rate, mode, initial_state, factor)
        performed.append(factor)
        if previous is not None:
            metrics = compare_traces(previous, trace)
            records.append({"coarse": performed[-2], "fine": factor, **metrics})
            consecutive = consecutive + 1 if metrics["within_reference_budget"] else 0
        previous = trace
        if consecutive >= 2:
            break
    return {"status": "converged" if consecutive >= 2 else "inconclusive",
            "performed_subdivisions": performed, "consecutive_passing_refinements": consecutive,
            "comparisons": records, "finest_trace": previous,
            "preparation_diagnostics": [TransientLine(profile, sample_rate * factor, mode).preparation_diagnostics()
                                        for factor in performed],
            "physical_fidelity_established": False}


def write_report(path: str | Path, report: dict, input_path: str | Path | None = None) -> None:
    target = Path(path)
    if input_path is not None:
        source = Path(input_path)
        if target.resolve() == source.resolve() or (target.exists() and os.path.samefile(target, source)):
            raise TransientError("report must not replace or alias its source profile")
    try:
        payload = (json.dumps(report, indent=2, allow_nan=False) + "\n").encode("utf-8")
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise TransientError(f"report is not finite JSON: {exc}") from exc
    if len(payload) > MAX_REPORT_BYTES:
        raise TransientError("report exceeds 64 MiB")
    if target.exists() or target.is_symlink():
        if not stat.S_ISREG(target.lstat().st_mode):
            raise TransientError("report destination must be a regular file or new path")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(prefix=f".{target.name}.", suffix=".tmp",
                                         dir=target.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mode", choices=MODES, default="vibrato")
    parser.add_argument("--fixture", choices=FIXTURES, default="step-positive")
    parser.add_argument("--sample-rate", type=float, default=48000.0)
    parser.add_argument("--frames", type=int, default=2400)
    parser.add_argument("--subdivisions", type=int, default=1)
    parser.add_argument("--study", action="store_true", help="run frozen refinements until two successive comparisons pass")
    parser.add_argument("--max-refinement", type=int, choices=(32, 64, 128), default=128)
    args = parser.parse_args(argv)
    try:
        if (args.output.resolve() == args.input.resolve()
                or (args.output.exists() and os.path.samefile(args.output, args.input))):
            raise TransientError("report must not replace or alias its source profile")
        profile, digest = load_profile_with_digest(args.input)
        values, initial = fixture(args.fixture, args.sample_rate, args.frames)
        report = {"schema_version": 1, "reference_id": REFERENCE_ID,
                  "model_id": profile["model_id"], "input_file_sha256": digest,
                  "reference_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  "numerical_contract_id": "scanner-numerics-v1",
                  "numerical_contract_sha256": hashlib.sha256(
                      (ROOT / "docs/SCANNER_NUMERICAL_CONTRACT.md").read_bytes()).hexdigest(),
                  "scope": "independent-nominal-full-circuit-transient-reference",
                  "method": "trapezoidal-capacitor-inductor-companions",
                  "input_reconstruction": "linear-between-fixed-knots",
                  "previous_endpoint_seconds": -1.0 / args.sample_rate,
                  "first_reported_endpoint_seconds": 0.0,
                  "fixture": args.fixture, "mode": args.mode, "sample_rate": args.sample_rate,
                  "frames": args.frames, "frozen_fixture_length": args.frames == 2400,
                  "frozen_fixture_grid": args.frames == 2400 and args.sample_rate == 48000.0,
                  "initial_state": {"capacitor_volts": initial.capacitor_volts,
                                    "inductor_amps": initial.inductor_amps,
                                    "previous_input_volts": initial.previous_input_volts, "frames": initial.frames},
                  "physical_fidelity_established": False, "runtime_comparison_performed": False}
        if args.study:
            if args.subdivisions != 1:
                raise TransientError("--study owns refinement factors; omit --subdivisions")
            factors = tuple(value for value in (8, 16, 32, 64, 128) if value <= args.max_refinement)
            report["refinement"] = refinement_study(profile, values, args.sample_rate, args.mode, initial, factors)
            trace = report["refinement"]["finest_trace"]
            reference_status = report["refinement"]["status"]
        else:
            trace = render_trace(profile, values, args.sample_rate, args.mode, initial, args.subdivisions)
            report["subdivisions"] = args.subdivisions
            report["preparation_diagnostics"] = TransientLine(
                profile, args.sample_rate * args.subdivisions, args.mode).preparation_diagnostics()
            report["trace"] = trace
            reference_status = "matched-step-only; convergence-not-tested"
        report["summary"] = {"reference_status": reference_status,
                             "maximum_normalized_residual": max(frame["normalized_residual"] for frame in trace),
                             "maximum_kcl_residual_amps": max(frame["kcl_residual_amps"] for frame in trace),
                             "final_energy_joules": trace[-1]["energy_joules"]}
        write_report(args.output, report, args.input)
        print(json.dumps(report["summary"], sort_keys=True))
        return 0
    except (OSError, ValueError, OverflowError, RecursionError) as exc:
        print(f"scanner transient reference: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
