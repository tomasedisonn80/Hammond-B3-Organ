#!/usr/bin/env python3
"""Independent ideal-circuit checks, not a scanner hardware/runtime qualification.

The second AC calculation is a loaded-ladder impedance recursion from literal
atlas values. It imports no nodal stamps, matrix factors or producer DC helper.
"""

from __future__ import annotations

import copy
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import scanner_ac_reference as reference  # noqa: E402


PROFILE_PATH = ROOT / "data/scanner/atlas-late-b3-nominal-v1.json"
TOOL_PATH = ROOT / "tools/scanner_ac_reference.py"
PROFILE_BYTES = PROFILE_PATH.read_bytes()
PROFILE = json.loads(PROFILE_BYTES)
MODES = ("vibrato", "chorus")
TAP_IDS = tuple(f"v{k}" for k in range(1, 20))

# Atlas p.157, independently retained literal ohm values. No values below are
# read from the producer's expected graph or normalized representation.
UPPER_OHMS = (27000, 56000, 39000, 33000, 18000, 12000)
LOWER_OHMS = (68000, 150000, 150000, 180000, 180000, 180000)

# Exact resistor-network answers calculated from those documentary values.
# Keeping literal fractions catches changes in the producer's DC assembly.
DC_PARALLEL = Fraction(92438660160000, 9455738267)
DC_RETURN = Fraction(9455738267, 13657495547)
DC_INPUT_CURRENT = {
    "vibrato": Fraction(9455738267, 92438660160000),
    "chorus": Fraction(9455738267, 300464902034000),
}
DC_TAPS = {
    "vibrato": (Fraction(68, 95), Fraction(75, 103), Fraction(50, 63),
                Fraction(60, 71), Fraction(10, 11), Fraction(15, 16))
                + (Fraction(1),) * 13,
    "chorus": (Fraction(12463311899, 13657495547),
               Fraction(12515270267, 13657495547),
               Fraction(12790466267, 13657495547),
               Fraction(13006519067, 13657495547),
               Fraction(146030693737, 150232451017),
               Fraction(13394885717, 13657495547))
               + (Fraction(1),) * 13,
}


def required_grid() -> tuple[float, ...]:
    geometric = [round(20.0 * 1000.0 ** (j / 120.0), 12) for j in range(121)]
    geometric[0], geometric[-1] = 20.0, 20000.0
    return tuple(sorted(set(geometric) | set(range(5000, 9001, 25))))


def ladder_answer(frequency: float, mode: str, *, termination: float = 15000.0,
                  dividers_after: bool = False) -> tuple[tuple[complex, ...], complex, complex]:
    """Backward load impedance, then forward voltage propagation, all O(18).

    Collapse each early *resistive* divider to its series resistance while
    determining loading; recover its observation only after the loaded line
    voltages are known. The moving return is the series Rc voltage. This uses
    neither a node matrix nor Gaussian elimination.
    """
    s = complex(0.0, math.tau * frequency)
    loads = [0.0j] * 19
    loads[18] = 1.0 / (1.0 / termination + s * 1.0e-9)
    for node in range(17, -1, -1):
        shunt = s * 4.0e-9 if node else 0.0j
        divider = node - 1 if dividers_after else node
        if 0 <= divider < 6:
            shunt += 1.0 / (UPPER_OHMS[divider] + LOWER_OHMS[divider])
        onward = 1.0 / (s * 0.5 + loads[node + 1])
        loads[node] = 1.0 / (shunt + onward)
    return_resistance = 22000.0 if mode == "chorus" else 0.0
    input_current = 1.0 / (return_resistance + loads[0])
    common_return = return_resistance * input_current
    relative = [1.0 - common_return]
    for node in range(1, 19):
        relative.append(relative[-1] * loads[node] / (s * 0.5 + loads[node]))
    taps = []
    for divider in range(6):
        node = divider + 1 if dividers_after else divider
        ratio = LOWER_OHMS[divider] / (UPPER_OHMS[divider] + LOWER_OHMS[divider])
        taps.append(common_return + ratio * relative[node])
    taps.extend(common_return + relative[node] for node in range(6, 19))
    return tuple(taps), common_return, input_current


class ScannerAcReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.network = reference.prepare_network(PROFILE)
        cls.grid = required_grid()
        # One actual full-grid pass; later tests reuse these immutable responses.
        cls.responses = {(mode, frequency): reference.solve_ac(cls.network, mode, frequency)
                         for mode in MODES for frequency in cls.grid}

    def assertComplexClose(self, actual, expected, *, absolute=1.0e-10, relative=1.0e-9):
        self.assertTrue(math.isfinite(actual.real) and math.isfinite(actual.imag))
        self.assertLessEqual(abs(actual - expected), absolute + relative * abs(expected),
                             f"actual={actual!r}, expected={expected!r}")

    def cli(self, *arguments):
        return subprocess.run([sys.executable, str(TOOL_PATH), *map(str, arguments)],
                              cwd=ROOT, text=True, capture_output=True, timeout=30,
                              check=False)

    def test_frozen_grid_and_exact_fractional_dc_answers(self):
        self.assertEqual(len(self.grid), 282)
        self.assertEqual(reference.default_frequency_grid(), self.grid)
        self.assertEqual((self.grid[0], self.grid[-1]), (20.0, 20000.0))
        for mode in MODES:
            with self.subTest(mode=mode):
                answer = reference.dc_reference(self.network, mode)
                self.assertEqual(answer["parallel_resistance_ohms"], DC_PARALLEL)
                self.assertEqual(answer["input_resistance_ohms"],
                                 DC_PARALLEL + (22000 if mode == "chorus" else 0))
                self.assertEqual(answer["input_current"], DC_INPUT_CURRENT[mode])
                self.assertEqual(answer["return_voltage"], DC_RETURN if mode == "chorus" else 0)
                self.assertEqual(answer["tap_ids"], TAP_IDS)
                self.assertEqual(answer["taps"], DC_TAPS[mode])
                self.assertTrue(all(isinstance(value, Fraction) for value in answer["taps"]))

    def test_all_grid_outputs_against_independent_loaded_ladder(self):
        maximum_tap_error = 0.0
        for (mode, frequency), actual in self.responses.items():
            with self.subTest(mode=mode, frequency=frequency):
                expected, common_return, current = ladder_answer(frequency, mode)
                self.assertEqual(actual["tap_ids"], TAP_IDS)
                self.assertEqual(len(actual["taps"]), 19)
                self.assertEqual(actual["dimension"], 24 if mode == "vibrato" else 25)
                for got, wanted in zip(actual["taps"], expected):
                    maximum_tap_error = max(maximum_tap_error, abs(got - wanted))
                    self.assertComplexClose(got, wanted)
                self.assertComplexClose(actual["return_voltage"], common_return)
                self.assertComplexClose(actual["input_current"], current,
                                        absolute=1.0e-14, relative=1.0e-9)
                self.assertEqual(actual["input_current_dimensionless"],
                                 15000.0 * actual["input_current"])
        self.assertEqual(len(self.responses) * 19, 10716)
        print(f"independent ladder: 10716 tap comparisons, maximum error {maximum_tap_error:.17g}")

    def test_full_grid_solve_evidence_is_finite_and_not_conditioning_limited(self):
        for key, answer in self.responses.items():
            with self.subTest(mode_frequency=key):
                self.assertEqual(answer["node_voltages"]["g"], 0.0j)
                self.assertEqual(answer["node_voltages"]["p0"], 1.0 + 0.0j)
                for voltage in answer["node_voltages"].values():
                    self.assertTrue(math.isfinite(voltage.real) and math.isfinite(voltage.imag))
                for name in ("normalized_residual", "scaled_normalized_residual"):
                    self.assertTrue(math.isfinite(answer[name]))
                    self.assertGreaterEqual(answer[name], 0.0)
                    self.assertLessEqual(answer[name], 1.0e-9)
                self.assertTrue(answer["residual_within_budget"])
                self.assertTrue(math.isfinite(answer["scaled_condition_inf"]))
                self.assertGreaterEqual(answer["scaled_condition_inf"], 1.0 - 1.0e-12)
                self.assertLessEqual(answer["conditioning_indicator"], 1.0e-4)
                self.assertFalse(answer["conditioning_limited"])
                self.assertTrue(answer["nominal"])
                self.assertEqual(answer["experiment"], {})
                self.assertEqual(answer["model_id"], "atlas-late-b3-nominal-line-v1")

    def test_passive_input_power_matches_literal_resistor_dissipation(self):
        for key, answer in self.responses.items():
            with self.subTest(mode_frequency=key):
                nodes = answer["node_voltages"]
                dissipated = abs(nodes["p18"] - nodes["r"]) ** 2 / 15000.0
                dissipated += abs(nodes["r"]) ** 2 / 22000.0
                for k, (upper, lower) in enumerate(zip(UPPER_OHMS, LOWER_OHMS), 1):
                    dissipated += abs(nodes[f"p{k - 1}"] - nodes[f"d{k}"]) ** 2 / upper
                    dissipated += abs(nodes[f"d{k}"] - nodes["r"]) ** 2 / lower
                # Both sides omit the same 1/2 factor for peak-phasor power.
                self.assertGreater(answer["input_current"].real, 0.0)
                self.assertAlmostEqual(answer["input_current"].real, dissipated, delta=1.0e-12)

    def test_low_frequency_limit_approaches_independent_dc(self):
        for mode in MODES:
            distances = []
            for frequency in (0.05, 0.005):
                actual = reference.solve_ac(self.network, mode, frequency)
                distance = max(abs(tap - float(wanted))
                               for tap, wanted in zip(actual["taps"], DC_TAPS[mode]))
                distances.append(distance)
                self.assertComplexClose(actual["input_current"],
                                        complex(float(DC_INPUT_CURRENT[mode])),
                                        absolute=1.0e-8, relative=0.0)
            self.assertLess(distances[-1], 1.0e-3)
            self.assertLess(distances[-1], distances[0] * 0.2)

    def test_wrong_divider_has_same_dc_but_independently_detectable_ac(self):
        wrong = reference.prepare_network(PROFILE, experiment={"divider_attachment": "after-inductor"})
        self.assertFalse(wrong.nominal)
        self.assertNotEqual(wrong.model_id, self.network.model_id)
        for mode in MODES:
            self.assertEqual(reference.dc_reference(wrong, mode)["taps"], DC_TAPS[mode])
            for frequency in (1000.0, 5000.0, 7000.0):
                with self.subTest(mode=mode, frequency=frequency):
                    actual = reference.solve_ac(wrong, mode, frequency)
                    expected, common_return, current = ladder_answer(frequency, mode, dividers_after=True)
                    for got, wanted in zip(actual["taps"], expected):
                        self.assertComplexClose(got, wanted)
                    self.assertComplexClose(actual["return_voltage"], common_return)
                    self.assertComplexClose(actual["input_current"], current, absolute=1.0e-14)
                    nominal = reference.solve_ac(self.network, mode, frequency)
                    self.assertGreater(max(abs(a - b) for a, b in zip(actual["taps"], nominal["taps"])),
                                       1.0e-3)

    def test_termination_load_changes_upstream_but_not_ideal_vibrato_tap_one(self):
        for termination in (7500.0, 30000.0):
            changed = reference.prepare_network(PROFILE, experiment={"termination_ohms": termination})
            for mode in MODES:
                for frequency in (1000.0, 5000.0, 7000.0):
                    with self.subTest(termination=termination, mode=mode, frequency=frequency):
                        actual = reference.solve_ac(changed, mode, frequency)
                        expected, common_return, current = ladder_answer(frequency, mode, termination=termination)
                        for got, wanted in zip(actual["taps"], expected):
                            self.assertComplexClose(got, wanted)
                        self.assertComplexClose(actual["return_voltage"], common_return)
                        self.assertComplexClose(actual["input_current"], current, absolute=1.0e-14)
                        nominal = reference.solve_ac(self.network, mode, frequency)
                        self.assertGreater(abs(actual["taps"][6] - nominal["taps"][6]), 1.0e-5)
                        self.assertGreater(abs(actual["input_current"] - nominal["input_current"]), 1.0e-9)
                        if mode == "vibrato":
                            self.assertComplexClose(actual["taps"][0], complex(68 / 95),
                                                    absolute=1.0e-14, relative=0.0)
                        else:
                            self.assertGreater(abs(actual["taps"][0] - nominal["taps"][0]), 1.0e-5)

    def test_one_observation_sign_reverses_only_its_output(self):
        for selected in ("v1", "v7", "v19"):
            altered = reference.prepare_network(PROFILE, experiment={"reverse_output": selected})
            for mode in MODES:
                for frequency in (1000.0, 5000.0, 7000.0):
                    with self.subTest(output=selected, mode=mode, frequency=frequency):
                        actual = reference.solve_ac(altered, mode, frequency)
                        nominal = reference.solve_ac(self.network, mode, frequency)
                        self.assertEqual(actual["node_voltages"], nominal["node_voltages"])
                        self.assertEqual(actual["input_current"], nominal["input_current"])
                        self.assertEqual(actual["return_voltage"], nominal["return_voltage"])
                        for name, got, base in zip(TAP_IDS, actual["taps"], nominal["taps"]):
                            self.assertEqual(got, -base if name == selected else base)

    def test_return_reference_omits_exactly_one_common_return(self):
        altered = reference.prepare_network(PROFILE, experiment={"output_reference": "return"})
        for mode in MODES:
            for frequency in (1000.0, 5000.0, 7000.0):
                with self.subTest(mode=mode, frequency=frequency):
                    actual = reference.solve_ac(altered, mode, frequency)
                    nominal = reference.solve_ac(self.network, mode, frequency)
                    self.assertEqual(actual["node_voltages"], nominal["node_voltages"])
                    for got, base in zip(actual["taps"], nominal["taps"]):
                        self.assertComplexClose(got, base - nominal["return_voltage"],
                                                absolute=1.0e-14, relative=1.0e-13)
                    if mode == "vibrato":
                        self.assertEqual(actual["taps"], nominal["taps"])
                    else:
                        self.assertGreater(abs(nominal["return_voltage"]), 1.0e-3)

    def test_preparation_is_nonmutating_and_experiment_identity_is_distinct(self):
        before = copy.deepcopy(PROFILE)
        experiment = {"termination_ohms": 7500.0, "reverse_output": "v7"}
        first = reference.prepare_network(PROFILE, experiment=experiment)
        second = reference.prepare_network(PROFILE, experiment=dict(reversed(list(experiment.items()))))
        self.assertEqual(first, second)
        self.assertNotEqual(first.model_id, self.network.model_id)
        self.assertEqual(first.base_model_id, self.network.model_id)
        self.assertFalse(first.nominal)
        self.assertEqual(PROFILE, before)
        self.assertEqual(PROFILE_PATH.read_bytes(), PROFILE_BYTES)
        with self.assertRaises(reference.ReferenceError):
            reference.solve_ac(first, "vibrato", 1000.0, experiment={})

    def test_rejects_invalid_frequency_mode_condition_and_experiments(self):
        for frequency in (None, True, False, "1000", 1000j, math.nan, math.inf, -math.inf,
                          0.0, -1.0, 1.0e-7, 1.0e9 + 1.0, 10 ** 1000):
            with self.subTest(frequency=frequency):
                with self.assertRaises(reference.ReferenceError):
                    reference.solve_ac(self.network, "vibrato", frequency)
        for mode in (None, True, 1, "", "V1", "Chorus", [], {}):
            with self.subTest(mode=mode):
                with self.assertRaises(reference.ReferenceError):
                    reference.solve_ac(self.network, mode, 1000.0)
        for value in (0, 1, None, "yes"):
            with self.assertRaises(reference.ReferenceError):
                reference.solve_ac(self.network, "vibrato", 1000.0, estimate_condition=value)
        experiments = [[], {"unknown": 1}, {"termination_ohms": True},
                       {"termination_ohms": math.nan}, {"termination_ohms": 0},
                       {"divider_attachment": "before"}, {"output_reference": "g"},
                       {"output_sign": "positive"}, {"reverse_output": "v0"},
                       {"reverse_output": "v20"}, {"reverse_output": 7},
                       {"reverse_output": "v7", "output_sign": "reversed"}]
        for experiment in experiments:
            with self.subTest(experiment=experiment):
                with self.assertRaises(reference.ReferenceError):
                    reference.prepare_network(PROFILE, experiment=experiment)
        changed = copy.deepcopy(PROFILE)
        changed["components"][0]["positive"] = "p1"
        with self.assertRaises(ValueError):
            reference.prepare_network(changed, experiment={"termination_ohms": 7500.0})

    def test_report_rejects_invalid_grids_and_mode_selections(self):
        for grid in ([], [20.0] * 1025, [1000.0, 20.0], [20.0, 20.0],
                     [20.0, math.nan], [True], ["20"], [0.0]):
            with self.subTest(grid=repr(grid)[:120]):
                with self.assertRaises(reference.ReferenceError):
                    reference.build_report(PROFILE, frequencies=grid)
        for modes in ([], (), "vibrato", ("vibrato", "vibrato"),
                      ("chorus", "vibrato", "chorus"), ("bad",), (1,)):
            with self.subTest(modes=modes):
                with self.assertRaises(reference.ReferenceError):
                    reference.build_report(PROFILE, frequencies=[1000.0], modes=modes)

    def test_report_scope_condition_optout_and_phase_floor_are_explicit(self):
        report = reference.build_report(PROFILE, frequencies=[20.0, 5000.0, 7000.0, 20000.0],
                                        estimate_condition=False)
        self.assertFalse(report["summary"]["physical_fidelity_established"])
        self.assertFalse(report["summary"]["runtime_comparison_performed"])
        self.assertEqual(report["frequency_grid_id"], "explicit-user-grid")
        self.assertEqual(report["linear_solve"]["condition"], "not computed")
        excluded = 0
        for mode in report["modes"]:
            for response in mode["responses"]:
                self.assertIsNone(response["scaled_condition_inf"])
                self.assertIsNone(response["conditioning_indicator"])
                self.assertIsNone(response["conditioning_limited"])
                for tap in response["taps"]:
                    if tap["magnitude"] < 1.0e-4:
                        excluded += 1
                        self.assertEqual(tap["phase_exclusion_reason"], "magnitude-below-1e-4")
                        self.assertIsNone(tap["unwrapped_phase_radians"])
                        self.assertIsNone(tap["group_delay_seconds"])
        self.assertGreater(excluded, 0)

    def test_cli_success_is_reproducible_and_binds_the_same_input_bytes(self):
        with tempfile.TemporaryDirectory(prefix="scanner-ac-tests-") as directory:
            base = Path(directory)
            source = base / "profile with spaces.json"
            source.write_bytes(PROFILE_BYTES)
            target = base / "response with spaces.json"
            args = ("--input", source, "--output", target,
                    "--frequencies", "20,1000,5000,7000,20000")
            first = self.cli(*args)
            self.assertEqual(first.returncode, 0, first.stderr)
            payload = target.read_bytes()
            second = self.cli(*args)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(target.read_bytes(), payload)
            report = json.loads(payload)
            self.assertEqual(report["input_file_sha256"], hashlib.sha256(PROFILE_BYTES).hexdigest())
            self.assertEqual(report["summary"]["positive_frequency_solutions"], 10)
            self.assertEqual(report["summary"]["tap_transfers"], 190)
            self.assertTrue(report["summary"]["residual_budget_passed"])
            self.assertEqual(source.read_bytes(), PROFILE_BYTES)
            self.assertEqual({p.name for p in base.iterdir()}, {source.name, target.name})

    def test_rejected_cli_calls_preserve_existing_output_and_input(self):
        with tempfile.TemporaryDirectory(prefix="scanner-ac-reject-") as directory:
            base = Path(directory)
            source = base / "source.json"
            source.write_bytes(PROFILE_BYTES)
            target = base / "previous.json"
            sentinel = b"retain the previous complete report\n"
            target.write_bytes(sentinel)
            invalid = [("--frequencies", "20,20"), ("--frequencies", "nan"),
                       ("--frequencies", "0"), ("--frequencies", ""),
                       ("--frequencies", "300,20"), ("--termination-ohms", "nan"),
                       ("--termination-ohms", "0"), ("--mode", "V1"),
                       ("--reverse-output", "v20"),
                       ("--reverse-output", "v7", "--reverse-output-sign")]
            for extra in invalid:
                with self.subTest(arguments=extra):
                    result = self.cli("--input", source, "--output", target, *extra)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(target.read_bytes(), sentinel)
                    self.assertEqual(source.read_bytes(), PROFILE_BYTES)
            result = self.cli("--input", source, "--output", source, "--frequencies", "1000")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(source.read_bytes(), PROFILE_BYTES)
            source.write_text('{"schema_version":1,"schema_version":1}')
            result = self.cli("--input", source, "--output", target, "--frequencies", "1000")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(target.read_bytes(), sentinel)
            self.assertEqual({p.name for p in base.iterdir()}, {source.name, target.name})

    def test_atomic_writer_preserves_previous_report_on_actual_failure_paths(self):
        with tempfile.TemporaryDirectory(prefix="scanner-ac-atomic-") as directory:
            target = Path(directory) / "previous.json"
            sentinel = b"previous complete report\n"
            target.write_bytes(sentinel)
            for malformed in ({"value": math.nan}, {"value": object()},
                              {"value": "x" * (16 * 1024 * 1024)}):
                with self.assertRaises(reference.ReferenceError):
                    reference.write_report(target, malformed)
                self.assertEqual(target.read_bytes(), sentinel)
            with mock.patch.object(reference.os, "replace", side_effect=OSError("injected publication failure")):
                with self.assertRaises(OSError):
                    reference.write_report(target, {"valid": 1})
            self.assertEqual(target.read_bytes(), sentinel)
            self.assertEqual(list(Path(directory).iterdir()), [target])


if __name__ == "__main__":
    unittest.main()
