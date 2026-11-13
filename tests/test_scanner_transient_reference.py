#!/usr/bin/env python3
"""Independent physical checks for the full-graph transient reference.

Literal documentary values and KCL/energy identities construct expectations;
no producer matrix, factorization, branch list or DC helper is reused. This is
bounded regression, not the complete G5 convergence or native parity suite.
"""

from __future__ import annotations

import copy
from dataclasses import replace
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import scanner_transient_reference as reference  # noqa: E402

PROFILE_PATH = ROOT / "data/scanner/atlas-late-b3-nominal-v1.json"
PROFILE = json.loads(PROFILE_PATH.read_bytes())
TOOL = ROOT / "tools/scanner_transient_reference.py"
MODES = ("vibrato", "chorus")
RATES = (44100.0, 48000.0, 96000.0)
UPPER = (27000, 56000, 39000, 33000, 18000, 12000)
LOWER = (68000, 150000, 150000, 180000, 180000, 180000)
SERIES = tuple(a + b for a, b in zip(UPPER, LOWER))
CAPACITANCE = (4.0e-9,) * 17 + (1.0e-9,)
ZERO = (0.0,) * 18


def literal_observation(state, mode):
    """Resistor KCL at the common return and the six divider junctions."""
    u = state.previous_input_volts
    r = 0.0 if mode == "vibrato" else (state.inductor_amps[0] + u / 95000.0) / (1 / 22000.0 + 1 / 95000.0)
    p = (u,) + tuple(r + value for value in state.capacitor_volts)
    taps = tuple((LOWER[k] * p[k] + UPPER[k] * r) / SERIES[k] for k in range(6)) + p[6:]
    current = state.inductor_amps[0] + (u - r) / 95000.0
    energy = math.fsum(0.5 * c * v * v for c, v in zip(CAPACITANCE, state.capacitor_volts))
    energy += math.fsum(0.25 * i * i for i in state.inductor_amps)
    return taps, r, current, energy


def literal_derivative(state, mode):
    """KCL at p1..p18 and L*di/dt=voltage, independently in physical units."""
    _, r, _, _ = literal_observation(state, mode)
    nodes = (state.previous_input_volts,) + tuple(r + value for value in state.capacitor_volts)
    capacitor_slopes = []
    for k, (voltage, capacitance) in enumerate(zip(state.capacitor_volts, CAPACITANCE)):
        onward = state.inductor_amps[k + 1] if k < 17 else 0.0
        resistor = voltage / SERIES[k + 1] if k < 5 else voltage / 15000.0 if k == 17 else 0.0
        capacitor_slopes.append((state.inductor_amps[k] - onward - resistor) / capacitance)
    return tuple(capacitor_slopes), tuple((nodes[k] - nodes[k + 1]) / 0.5 for k in range(18))


def midpoint_power(first, second, mode):
    mid = reference.PhysicalState(
        tuple((a + b) / 2 for a, b in zip(first.capacitor_volts, second.capacitor_volts)),
        tuple((a + b) / 2 for a, b in zip(first.inductor_amps, second.inductor_amps)),
        (first.previous_input_volts + second.previous_input_volts) / 2)
    taps, r, current, _ = literal_observation(mid, mode)
    p = (mid.previous_input_volts,) + tuple(r + value for value in mid.capacitor_volts)
    dissipation = math.fsum((p[k] - taps[k]) ** 2 / UPPER[k] + (taps[k] - r) ** 2 / LOWER[k]
                           for k in range(6))
    dissipation += (p[18] - r) ** 2 / 15000.0 + r * r / 22000.0
    return mid.previous_input_volts * current, dissipation


def seeded_state():
    return reference.PhysicalState(tuple(0.2 * math.sin(k + 0.3) for k in range(18)),
                                   tuple(2.0e-5 * math.cos(2 * k + 0.7) for k in range(18)),
                                   0.375, 127)


class ScannerTransientReferenceTests(unittest.TestCase):
    def assertClose(self, actual, expected, absolute=2.0e-12, relative=2.0e-11):
        self.assertTrue(math.isfinite(actual))
        self.assertLessEqual(abs(actual - expected), absolute + relative * abs(expected),
                             f"actual={actual!r}, expected={expected!r}")

    def assertObservation(self, line):
        frame, state = line.observe(), line.state()
        taps, common, current, energy = literal_observation(state, line.mode)
        self.assertEqual(frame["frame"], state.frames)
        self.assertFalse(frame["advanced"])
        self.assertEqual(frame["capacitor_volts"], state.capacitor_volts)
        self.assertEqual(frame["inductor_amps"], state.inductor_amps)
        for actual, expected in zip(frame["taps_volts"], taps):
            self.assertClose(actual, expected)
        self.assertClose(frame["return_volts"], common)
        self.assertClose(frame["input_current_amps"], current, 2.0e-16)
        self.assertClose(frame["energy_joules"], energy, 1.0e-23)
        self.assertLessEqual(frame["normalized_residual"], 1.0e-9)
        self.assertLessEqual(frame["kcl_residual_amps"], 2.0e-14)
        if line.mode == "chorus":
            self.assertClose(current, common / 22000.0, 2.0e-16)

    def cli(self, *arguments):
        return subprocess.run([sys.executable, str(TOOL), *map(str, arguments)], cwd=ROOT,
                              capture_output=True, text=True, timeout=30, check=False)

    def test_exact_resistor_dc_equilibria_and_constant_continuation(self):
        parallel = Fraction(1, 1) / (Fraction(1, 15000) + sum(Fraction(1, value) for value in SERIES))
        self.assertEqual(parallel, Fraction(92438660160000, 9455738267))
        for mode in MODES:
            return_fraction = Fraction(0) if mode == "vibrato" else Fraction(22000) / (22000 + parallel)
            local = 1 - return_fraction
            expected_taps = tuple(return_fraction + local * Fraction(b, d) for b, d in zip(LOWER, SERIES)) + (Fraction(1),) * 13
            currents = tuple(float(local * (Fraction(1, 15000) + sum(Fraction(1, SERIES[node]) for node in range(k + 1, 6))))
                             for k in range(18))
            initial = reference.PhysicalState((float(local),) * 18, currents, 1.0, 123)
            for rate in RATES:
                with self.subTest(mode=mode, rate=rate):
                    line = reference.TransientLine(PROFILE, rate, mode, initial)
                    for _ in range(64):
                        frame = line.process_frame(1.0)
                    for actual, expected in zip(frame["taps_volts"], expected_taps):
                        self.assertClose(actual, float(expected))
                    self.assertClose(frame["return_volts"], float(return_fraction))
                    self.assertClose(frame["input_current_amps"], float(1 / (parallel + (22000 if mode == "chorus" else 0))), 2.0e-16)
                    self.assertEqual(line.state().frames, 187)
                    self.assertObservation(line)

    def test_all_signed_physical_basis_reconstruction(self):
        for mode in MODES:
            line = reference.TransientLine(PROFILE, 48000.0, mode)
            for coordinate in range(36):
                for sign in (-1.0, 1.0):
                    values = [0.0] * 36
                    values[coordinate] = sign * (1.0 if coordinate < 18 else 1.0e-4)
                    state = reference.PhysicalState(tuple(values[:18]), tuple(values[18:]), 0.0, coordinate)
                    with self.subTest(mode=mode, coordinate=coordinate, sign=sign):
                        line.restore_state(state)
                        self.assertEqual(line.state(), state)
                        self.assertObservation(line)
                        line.process_frame(0.0)
                        self.assertObservation(line)

    def test_all_coordinate_trapezoidal_endpoint_identities(self):
        for mode in MODES:
            for rate in RATES:
                line = reference.TransientLine(PROFILE, rate, mode, seeded_state())
                for frame in range(96):
                    before = line.state()
                    d_before = literal_derivative(before, mode)
                    line.process_frame(0.6 * math.sin(frame * 0.31))
                    after = line.state()
                    d_after = literal_derivative(after, mode)
                    for kind, old_values, new_values in ((0, before.capacitor_volts, after.capacitor_volts),
                                                         (1, before.inductor_amps, after.inductor_amps)):
                        scale = 1.0 if kind == 0 else 1.0e-4
                        for k in range(18):
                            expected_delta = (d_before[kind][k] + d_after[kind][k]) / (2 * rate)
                            self.assertClose((new_values[k] - old_values[k]) / scale, expected_delta / scale,
                                             1.0e-11, 1.0e-10)
                    self.assertObservation(line)

    def test_discrete_source_work_and_all_resistor_dissipation(self):
        for mode in MODES:
            for rate in RATES:
                line = reference.TransientLine(PROFILE, rate, mode, seeded_state())
                for n in range(192):
                    old = line.state()
                    old_energy = literal_observation(old, mode)[3]
                    frame = line.process_frame(0.75 * math.cos(0.413 * n))
                    supplied, dissipated = midpoint_power(old, line.state(), mode)
                    self.assertGreaterEqual(dissipated, 0.0)
                    self.assertClose(frame["energy_joules"] - old_energy,
                                     (supplied - dissipated) / rate, 2.0e-20, 2.0e-10)

    def test_zero_source_passivity_of_four_charged_families(self):
        for mode in MODES:
            for name in ("charged-c1", "charged-c18", "energized-l1", "energized-l18"):
                _, state = reference.fixture(name, frames=1)
                line = reference.TransientLine(PROFILE, 48000.0, mode, state)
                initial = previous = literal_observation(state, mode)[3]
                for _ in range(512):
                    energy = line.process_frame(0.0)["energy_joules"]
                    self.assertLessEqual(energy - previous, 1.0e-12 * initial + 1.0e-24)
                    self.assertLessEqual(energy - initial, 1.0e-10 * initial + 1.0e-24)
                    previous = energy
                self.assertLess(previous, initial)

    def test_mode_and_all_ordered_rate_changes_preserve_physical_state(self):
        for mode in MODES:
            for old_rate in RATES:
                for new_rate in RATES:
                    line = reference.TransientLine(PROFILE, old_rate, mode, seeded_state())
                    for n in range(17):
                        line.process_frame(math.sin(n * 0.29))
                    checkpoint = line.state()
                    line.reconfigure_sample_rate(new_rate)
                    self.assertEqual(line.state(), checkpoint)
                    self.assertEqual(line.sample_rate, new_rate)
                    self.assertObservation(line)
                    other = MODES[mode == "vibrato"]
                    line.set_mode(other)
                    self.assertEqual(line.state(), checkpoint)
                    self.assertObservation(line)
                    control = reference.TransientLine(PROFILE, new_rate, other, checkpoint)
                    for n in range(16):
                        value = math.cos(n * 0.19)
                        self.assertEqual(line.process_frame(value), control.process_frame(value))

    def test_in_frame_return_switch_matches_explicit_stopped_switch(self):
        for mode in MODES:
            line = reference.TransientLine(PROFILE, 48000.0, mode, seeded_state())
            control = copy.deepcopy(line)
            for n in range(96):
                target = MODES[(n // 7) % 2]
                control.set_mode(target)
                value = 0.3 * math.sin(n * 0.37)
                self.assertEqual(line.process_frame(value, target), control.process_frame(value))

    def test_polarity_reverses_every_signed_observation_and_state(self):
        state = seeded_state()
        negative = reference.PhysicalState(tuple(-v for v in state.capacitor_volts),
                                            tuple(-i for i in state.inductor_amps),
                                            -state.previous_input_volts, state.frames)
        for mode in MODES:
            a = reference.TransientLine(PROFILE, 48000.0, mode, state)
            b = reference.TransientLine(PROFILE, 48000.0, mode, negative)
            for n in range(128):
                value = 0.7 * math.sin(n * 0.23)
                fa, fb = a.process_frame(value), b.process_frame(-value)
                for field in ("taps_volts", "capacitor_volts", "inductor_amps"):
                    self.assertEqual(fa[field], tuple(-v for v in fb[field]))
                for field in ("return_volts", "input_current_amps"):
                    self.assertEqual(fa[field], -fb[field])
                self.assertEqual(fa["energy_joules"], fb["energy_joules"])

    def test_rejections_preserve_precharged_state_and_future_frames(self):
        base = reference.TransientLine(PROFILE, 48000.0, "chorus", seeded_state())
        for n in range(31):
            base.process_frame(math.sin(n * 0.13))
        state = base.state()
        actions = []
        for value in (True, "1", None, math.nan, math.inf, -math.inf,
                      math.nextafter(64.0, math.inf), math.nextafter(-64.0, -math.inf)):
            actions.append(lambda line, value=value: line.process_frame(value, "vibrato"))
        for value in (None, True, "", "Chorus", [], 0):
            actions.append(lambda line, value=value: line.set_mode(value))
        for value in (True, "48000", 0.0, math.nan, math.inf, 7999.0, 12288001.0):
            actions.append(lambda line, value=value: line.reconfigure_sample_rate(value))
        invalid_states = [None, {}, replace(state, frames=True), replace(state, frames=-1),
                          replace(state, frames=1 << 64), replace(state, capacitor_volts=(0.0,) * 17),
                          replace(state, inductor_amps=(0.0,) * 19),
                          replace(state, previous_input_volts=math.nan), replace(state, previous_input_volts=True)]
        for field in ("capacitor_volts", "inductor_amps"):
            for index in range(18):
                values = list(getattr(state, field))
                values[index] = math.nan
                invalid_states.append(replace(state, **{field: tuple(values)}))
            bound = 1.0e6 if field == "capacitor_volts" else 100.0
            for value in (math.inf, -math.inf, True, math.nextafter(bound, math.inf), math.nextafter(-bound, -math.inf)):
                values = list(getattr(state, field))
                values[0] = value
                invalid_states.append(replace(state, **{field: tuple(values)}))
        actions.extend(lambda line, value=value: line.restore_state(value) for value in invalid_states)
        for index, action in enumerate(actions):
            with self.subTest(action=index):
                line, control = copy.deepcopy(base), copy.deepcopy(base)
                before = line.observe()
                with self.assertRaises(reference.TransientError):
                    action(line)
                self.assertEqual(line.state(), state)
                self.assertEqual(line.observe(), before)
                self.assertEqual((line.mode, line.sample_rate), ("chorus", 48000.0))
                for n in range(8):
                    value = 0.2 * math.cos(n * 0.41)
                    self.assertEqual(line.process_frame(value), control.process_frame(value))

    def test_counter_overflow_and_observation_do_not_advance(self):
        state = replace(seeded_state(), frames=(1 << 64) - 2)
        line = reference.TransientLine(PROFILE, 48000.0, "chorus", state)
        self.assertEqual(line.observe(), line.observe())
        self.assertEqual(line.state(), state)
        self.assertEqual(line.process_frame(0.0)["frame"], (1 << 64) - 1)
        before = line.state()
        with self.assertRaises(reference.TransientError):
            line.process_frame(0.0, "vibrato")
        self.assertEqual(line.state(), before)
        self.assertEqual(line.mode, "chorus")
        control = copy.deepcopy(line)
        usable = replace(before, frames=31)
        line.restore_state(usable)
        control.restore_state(usable)
        self.assertEqual(line.process_frame(0.1), control.process_frame(0.1))

    def test_fixture_definitions_and_dimensions_match_frozen_contract(self):
        names = ("step-positive", "step-negative", "pulse-positive", "pulse-negative", "multisine",
                 "charged-c1", "charged-c18", "energized-l1", "energized-l18")
        self.assertEqual(reference.FIXTURES, names)
        for name in names:
            inputs, state = reference.fixture(name)
            self.assertEqual(len(inputs), 2400)
            self.assertEqual((state.previous_input_volts, state.frames), (0.0, 0))
            if name.startswith("step-"):
                self.assertEqual(inputs, (1.0 if name.endswith("positive") else -1.0,) * 2400)
            elif name.startswith("pulse-"):
                self.assertEqual(inputs, (1.0 if name.endswith("positive") else -1.0,) + (0.0,) * 2399)
            elif name == "multisine":
                for n, value in enumerate(inputs):
                    expected = math.fsum(math.sin(math.tau * f * n / 48000) for f in (137, 997, 3113, 5087, 6971)) / 5
                    self.assertClose(value, expected, 2.0e-16, 2.0e-15)
            else:
                self.assertEqual(inputs, (0.0,) * 2400)
            expected_caps, expected_currents = [0.0] * 18, [0.0] * 18
            if name == "charged-c1": expected_caps[0] = 1.0
            if name == "charged-c18": expected_caps[-1] = -1.0
            if name == "energized-l1": expected_currents[0] = 1.0e-4
            if name == "energized-l18": expected_currents[-1] = -1.0e-4
            self.assertEqual(state.capacitor_volts, tuple(expected_caps))
            self.assertEqual(state.inductor_amps, tuple(expected_currents))

    def test_trace_linear_input_polygon_and_endpoint_origin(self):
        state = replace(seeded_state(), frames=7)
        values = (-0.7, 0.2, 0.9)
        trace = reference.render_trace(PROFILE, values, 48000, "chorus", state, subdivisions=8)
        line = reference.TransientLine(PROFILE, 384000, "chorus", state)
        previous = state.previous_input_volts
        for knot, value in enumerate(values):
            for substep in range(1, 9):
                endpoint = value if substep == 8 else previous + (value - previous) * substep / 8
                expected = line.process_frame(endpoint)
            actual = dict(trace[knot])
            self.assertEqual(actual.pop("knot"), knot)
            self.assertEqual(actual.pop("time_seconds"), knot / 48000)
            self.assertEqual(actual, expected)
            self.assertEqual(actual["frame"], 7 + 8 * (knot + 1))
            previous = value

    def test_trace_input_bounds_and_overflow_reject(self):
        for inputs in ([], (), "1", [True], [math.nan], [65.0], [0.0] * 10001):
            with self.assertRaises(reference.TransientError):
                reference.render_trace(PROFILE, inputs, 48000, "vibrato")
        for factor in (True, 0, 3, 8.0, 256):
            with self.assertRaises(reference.TransientError):
                reference.render_trace(PROFILE, [0.0], 48000, "vibrato", subdivisions=factor)
        with self.assertRaises(reference.TransientError):
            reference.render_trace(PROFILE, [0.0], 48000, "vibrato",
                                   replace(seeded_state(), frames=(1 << 64) - 8), 8)
        for name, frames in (("missing", 1), ("multisine", True), ("multisine", 0), ("multisine", 10001)):
            with self.assertRaises(reference.TransientError):
                reference.fixture(name, frames=frames)

    def test_comparison_uses_fixed_current_scale_and_every_required_channel(self):
        trace = reference.render_trace(PROFILE, [0.0] * 4, 48000, "vibrato")
        self.assertTrue(reference.compare_traces(trace, trace)["within_reference_budget"])
        for field, count, scale in (("taps_volts", 19, 1.0), ("capacitor_volts", 18, 1.0), ("inductor_amps", 18, 1.0e-4)):
            for index in range(count):
                changed = copy.deepcopy(trace)
                values = list(changed[1][field]); values[index] = 1.1e-5 * scale; changed[1][field] = tuple(values)
                result = reference.compare_traces(trace, changed)
                self.assertFalse(result["within_reference_budget"])
                channel = next(row for row in result["channels"] if row["field"] == field and row["index"] == index)
                self.assertClose(channel["normalized_rms"], 5.5e-6, 1.0e-18)
                self.assertClose(channel["normalized_maximum"], 1.1e-5, 1.0e-18)
        changed = copy.deepcopy(trace)
        changed[0]["return_volts"] = 0.1
        changed[0]["input_current_amps"] = 0.1
        result = reference.compare_traces(trace, changed)
        self.assertTrue(result["within_reference_budget"])
        self.assertEqual(sum(row["required"] for row in result["channels"]), 55)
        self.assertEqual(len(result["channels"]), 57)
        self.assertEqual((result["rms_bound"], result["maximum_bound"]), (2.0e-6, 1.0e-5))

    def test_comparison_rejects_nonfinite_dimensions_and_misalignment(self):
        trace = reference.render_trace(PROFILE, [0.0, 0.1], 48000, "chorus")
        for field, value in (("knot", True), ("knot", 7), ("time_seconds", 0.123),
                             ("time_seconds", math.nan), ("mode", "vibrato"), ("input_volts", 0.2),
                             ("taps_volts", (0.0,) * 18), ("capacitor_volts", (math.inf,) * 18),
                             ("inductor_amps", (True,) * 18), ("return_volts", math.inf),
                             ("input_current_amps", math.nan)):
            changed = copy.deepcopy(trace); changed[0][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(reference.TransientError):
                reference.compare_traces(trace, changed)
        for other in ([], trace[:1], "trace"):
            with self.assertRaises(reference.TransientError):
                reference.compare_traces(trace, other)

    def test_rms_and_maximum_comparison_budgets_each_reject_independently(self):
        trace = reference.render_trace(PROFILE, [0.0] * 64, 48000, "vibrato")
        for spread, amplitude in ((False, 1.1e-5), (True, 2.1e-6)):
            changed = copy.deepcopy(trace)
            for frame in changed if spread else changed[:1]:
                values = list(frame["taps_volts"])
                values[18] = amplitude
                frame["taps_volts"] = tuple(values)
            result = reference.compare_traces(trace, changed)
            self.assertFalse(result["within_reference_budget"])
            channel = next(row for row in result["channels"]
                           if row["field"] == "taps_volts" and row["index"] == 18)
            self.assertEqual(channel["normalized_rms"] > 2.0e-6, spread)
            self.assertEqual(channel["normalized_maximum"] > 1.0e-5, not spread)

    def test_refinement_requires_two_successive_real_comparisons(self):
        result = reference.refinement_study(PROFILE, (0.0,) * 8, 48000, "chorus")
        self.assertEqual(result["status"], "converged")
        self.assertEqual(result["performed_subdivisions"], [8, 16, 32])
        self.assertEqual(result["consecutive_passing_refinements"], 2)
        self.assertEqual([(row["coarse"], row["fine"]) for row in result["comparisons"]], [(8, 16), (16, 32)])
        self.assertFalse(result["physical_fidelity_established"])
        inputs, initial = reference.fixture("charged-c18", frames=16)
        unresolved = reference.refinement_study(PROFILE, inputs, 48000, "chorus", initial, (8, 16, 32))
        self.assertEqual(unresolved["status"], "inconclusive")
        self.assertLess(unresolved["consecutive_passing_refinements"], 2)
        self.assertFalse(all(row["within_reference_budget"] for row in unresolved["comparisons"]))
        for factors in ((8, 16), (16, 32, 64), (8, 32, 64), (8, 16, 32, 128), "8,16,32"):
            with self.assertRaises(reference.TransientError):
                reference.refinement_study(PROFILE, (0.0,), 48000, "chorus", refinements=factors)

    def test_diagnostics_keep_matrix_scaling_and_conditioning_visible(self):
        report = reference.TransientLine(PROFILE, 48000, "vibrato").preparation_diagnostics()
        self.assertEqual(report["residual_limit"], 1.0e-9)
        self.assertIn("binary64", report["condition_method"])
        self.assertIn("unscaled", report["companion_residual_matrix"])
        for mode, count in (("vibrato", 24), ("chorus", 25)):
            row = report["modes"][mode]
            self.assertEqual(row["free_node_count"], count)
            self.assertEqual(row["initial_mna_dimension"], count + 18)
            conditions = [value for name, value in row.items() if name.endswith("condition_inf_estimate")]
            self.assertEqual(len(conditions), 3)
            self.assertTrue(all(math.isfinite(value) and value >= 1 for value in conditions))
            self.assertEqual(row["conditioning_limited"], any(value * 2.0 ** -52 > 1.0e-4 for value in conditions))

    def test_atomic_report_rejects_nonfinite_and_preserves_existing_file(self):
        with tempfile.TemporaryDirectory(prefix="scanner transient output ") as temporary:
            work = Path(temporary); target = work / "report.json"
            target.write_bytes(b"previous destination\n")
            for bad in ({"bad": math.nan}, {"bad": math.inf}, {"bad": object()}):
                with self.assertRaises(reference.TransientError):
                    reference.write_report(target, bad)
                self.assertEqual(target.read_bytes(), b"previous destination\n")
            with mock.patch.object(reference.os, "replace", side_effect=OSError("injected replace failure")):
                with self.assertRaises(OSError):
                    reference.write_report(target, {"finite": 1.0})
            self.assertEqual(target.read_bytes(), b"previous destination\n")
            self.assertEqual(sorted(path.name for path in work.iterdir()), ["report.json"])
            with mock.patch.object(reference, "MAX_REPORT_BYTES", 8):
                with self.assertRaises(reference.TransientError):
                    reference.write_report(target, {"longer": "payload"})
            self.assertEqual(reference.MAX_REPORT_BYTES, 64 * 1024 * 1024)
            reference.write_report(target, {"finite": 1.0})
            self.assertEqual(json.loads(target.read_text()), {"finite": 1.0})

    def test_report_source_alias_and_nonregular_destinations_reject(self):
        with tempfile.TemporaryDirectory(prefix="scanner transient aliases ") as temporary:
            work = Path(temporary); source = work / "profile.json"; source.write_bytes(PROFILE_PATH.read_bytes())
            before = source.read_bytes()
            with self.assertRaises(reference.TransientError):
                reference.write_report(source, {"x": 1}, source)
            alias = work / "hardlink.json"
            os.link(source, alias)
            with self.assertRaises(reference.TransientError):
                reference.write_report(alias, {"x": 1}, source)
            self.assertEqual(source.read_bytes(), before)
            directory = work / "directory"; directory.mkdir()
            with self.assertRaises(reference.TransientError):
                reference.write_report(directory, {"x": 1})
            # Some Windows accounts cannot create symlinks. The POSIX branch is
            # an actual symlink test; hardlink/directory coverage is unconditional.
            if os.name != "nt":
                symlink = work / "symbolic.json"; symlink.symlink_to(source)
                with self.assertRaises(reference.TransientError):
                    reference.write_report(symlink, {"x": 1})
                dangling = work / "dangling.json"; dangling.symlink_to(work / "missing")
                with self.assertRaises(reference.TransientError):
                    reference.write_report(dangling, {"x": 1})

    def test_cli_provenance_clock_and_failure_preservation(self):
        with tempfile.TemporaryDirectory(prefix="scanner transient cli ") as temporary:
            output = Path(temporary) / "trace.json"
            result = self.cli("--output", output, "--fixture", "charged-c18", "--mode", "chorus", "--frames", 8)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(output.read_text())
            self.assertEqual(report["schema_version"], 1)
            self.assertEqual(report["input_file_sha256"], hashlib.sha256(PROFILE_PATH.read_bytes()).hexdigest())
            self.assertEqual(report["reference_source_sha256"], hashlib.sha256(TOOL.read_bytes()).hexdigest())
            self.assertEqual(report["numerical_contract_sha256"], hashlib.sha256((ROOT / "docs/SCANNER_NUMERICAL_CONTRACT.md").read_bytes()).hexdigest())
            self.assertFalse(report["frozen_fixture_grid"])
            self.assertFalse(report["physical_fidelity_established"])
            self.assertFalse(report["runtime_comparison_performed"])
            self.assertEqual(report["previous_endpoint_seconds"], -1 / 48000)
            self.assertEqual(report["first_reported_endpoint_seconds"], 0)
            self.assertEqual((report["trace"][0]["frame"], report["trace"][0]["knot"], report["trace"][0]["time_seconds"]), (1, 0, 0))
            self.assertEqual(report["summary"]["reference_status"], "matched-step-only; convergence-not-tested")
            original = output.read_bytes()
            for arguments in (("--sample-rate", "nan"), ("--frames", "0"), ("--study", "--subdivisions", "8")):
                bad = self.cli("--output", output, *arguments)
                self.assertEqual(bad.returncode, 2)
                self.assertIn("scanner transient reference:", bad.stderr)
                self.assertEqual(output.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
