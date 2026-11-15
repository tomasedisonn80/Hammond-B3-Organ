#!/usr/bin/env python3
"""Independent admission/algebra/CLI checks for the ideal crossover reference."""

from __future__ import annotations

import cmath
import copy
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import crossover_reference as reference  # noqa: E402


REGISTRY = ROOT / "data/crossover/leslie-122-ideal-v1.json"
TOOL = ROOT / "tools/crossover_reference.py"
PROFILE = json.loads(REGISTRY.read_text(encoding="utf-8"))
LOADS = ((16.0, 16.0), (1.0, 1.0), (1024.0, 1024.0),
         (1.0, 1024.0), (1024.0, 1.0), (8.0, 32.0))


def polynomial_answer(frequency: float, rt: float, rw: float) -> tuple[complex, complex, complex]:
    """Literal L/C values and separately reduced transfer polynomials.

    This does not read the producer's schema table, edges, series impedances,
    matrices, or DC routine. Input current follows capacitor and bass-node KCL.
    """
    s = 1j * 2.0 * math.pi * frequency
    treble = s * s * 0.0032 * 7.8e-6 / (1.0 + s * 0.0032 / rt + s * s * 0.0032 * 7.8e-6)
    bass = 1.0 / (1.0 + s * 0.0052 / rw + s * s * 0.0052 * 12.5e-6)
    current = s * 7.8e-6 * (1.0 - treble) + (1.0 / rw + s * 12.5e-6) * bass
    return treble, bass, current


class CrossoverReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.network = reference.load_network(REGISTRY)
        cls.grid = reference.default_frequency_grid()

    def cli(self, *arguments):
        return subprocess.run([sys.executable, str(TOOL), *map(str, arguments)], cwd=ROOT,
                              capture_output=True, text=True, timeout=20, check=False)

    def test_exact_registry_and_source_hashes(self):
        reference.validate_registry(PROFILE)
        raw = REGISTRY.read_bytes()
        self.assertEqual(self.network.registry_bytes_sha256, hashlib.sha256(raw).hexdigest())
        canonical = json.dumps(PROFILE, ensure_ascii=True, sort_keys=True,
                               separators=(",", ":"), allow_nan=False).encode("ascii")
        self.assertEqual(self.network.registry_canonical_sha256, hashlib.sha256(canonical).hexdigest())
        self.assertEqual(PROFILE["source"]["sha256"],
                         "4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769")
        self.assertEqual(PROFILE["source"]["pages"], list(range(271, 277)))
        self.assertEqual(PROFILE["target"]["divider_assembly"], "052803")
        self.assertTrue(self.network.nominal_loads)
        self.assertEqual(len(self.network.components), 6)

    def test_wrong_graph_components_units_and_evidence_are_rejected(self):
        changes = [
            lambda p: p["components"][2].update(id="C16B"),
            lambda p: p["components"][2].update(value=12.5e-6),
            lambda p: p["components"][3].update(nodes=["H", "B"]),
            lambda p: p["components"][0].update(nodes=["H", "A"]),
            lambda p: p["components"][0].update(unit="mH"),
            lambda p: p["components"][0].update(value=3.2),
            lambda p: p["components"][0].update(evidence="measured"),
            lambda p: p["components"].append(copy.deepcopy(p["components"][0])),
            lambda p: p["components"].pop(),
            lambda p: p["components"].reverse(),
            lambda p: p["ideal_loads"][0].update(nodes=["H", "B"]),
            lambda p: p["ideal_loads"][0].update(resistance=8.0),
            lambda p: p["ports"]["treble_voltage"].update(negative_node="B"),
            lambda p: p["unknown_physical_fields"].update(winding_resistance_ohm=0.0),
            lambda p: p["unknown_physical_fields"].update(acoustic_polarity="positive"),
            lambda p: p["simulation_assumptions"].update(physical_measurement_claim=True),
            lambda p: p["source"].update(verification="primary drawings independently verified"),
            lambda p: p["source"].update(sha256="0" * 64),
            lambda p: p["source"]["pages"].pop(),
            lambda p: p["target"].update(divider_assembly="113860"),
            lambda p: p["target"].update(cabinet_family="Leslie 147"),
            lambda p: p["target"].update(specimen_identity="unacquired-as-measured"),
            lambda p: p.update(extra_field=1),
            lambda p: p["numerics"].update(prewarp=True),
            lambda p: p["numerics"].update(max_block_frames=8192),
            lambda p: p["numerics"].pop("limits_are_computational_not_device_ratings"),
        ]
        for index, change in enumerate(changes):
            with self.subTest(mutation=index):
                bad = copy.deepcopy(PROFILE)
                change(bad)
                with self.assertRaises(reference.ReferenceError):
                    reference.validate_registry(bad)

    def test_strict_scalar_types_nonfinite_and_field_location(self):
        for bad_value in (True, "0.0032", None, [], {}, float("nan"), float("inf"), -0.0032):
            with self.subTest(value=bad_value):
                bad = copy.deepcopy(PROFILE)
                bad["components"][0]["value"] = bad_value
                with self.assertRaisesRegex(reference.ReferenceError, r"components\[0\].value"):
                    reference.validate_registry(bad)
        for path, value in (("schema_version", True), ("schema_version", 1.0)):
            bad = copy.deepcopy(PROFILE)
            bad[path] = value
            with self.assertRaises(reference.ReferenceError):
                reference.validate_registry(bad)
        bad = copy.deepcopy(PROFILE)
        bad["simulation_assumptions"]["engine_integration"] = 0
        with self.assertRaisesRegex(reference.ReferenceError, "engine_integration"):
            reference.validate_registry(bad)

    def test_unknown_measurements_remain_null_separate_from_fixture_zeroes(self):
        report = reference.make_report(self.network)
        unknown = report["unknown_physical_fields"]
        self.assertEqual(len(unknown) - 1, 8)
        self.assertTrue(all(value is None for key, value in unknown.items() if key != "reason"))
        self.assertEqual(report["simulation_assumptions"]["source_impedance_ohm"], 0.0)
        self.assertEqual(report["simulation_assumptions"]["inductor_series_resistance_ohm"], 0.0)
        self.assertFalse(report["physical_measurement_claim"])
        self.assertFalse(report["atlas_bytes_verified_by_this_tool"])
        self.assertFalse(report["engine_integration"])
        self.assertIn("not independently inspected", report["source"]["verification"])

    def test_duplicate_json_keys_and_nonfinite_json_are_rejected(self):
        text = REGISTRY.read_text(encoding="utf-8")
        invalid = (
            text.replace('"schema_version": 1,', '"schema_version": 1, "schema_version": 1,', 1),
            text.replace('"reference_node": "B",', '"reference_node": "B", "reference_node": "B",', 1),
            text.replace('"value": 0.0032', '"value": NaN', 1),
            text.replace('"value": 0.0032', '"value": Infinity', 1),
            text.replace('"value": 0.0032', '"value": -Infinity', 1),
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "registry.json"
            for value in invalid:
                path.write_text(value, encoding="utf-8")
                with self.assertRaises(reference.ReferenceError):
                    reference.load_registry(path)
            path.write_bytes(b"\xff")
            with self.assertRaises(reference.ReferenceError):
                reference.load_registry(path)
            for malformed in ("{" , "[" * 2000 + "]" * 2000, "1" * 5000):
                path.write_text(malformed, encoding="utf-8")
                with self.assertRaises(reference.ReferenceError):
                    reference.load_registry(path)
            path.write_bytes(b" " * (reference.MAX_REGISTRY_BYTES + 1))
            with self.assertRaisesRegex(reference.ReferenceError, "exceeds"):
                reference.load_registry(path)

    def test_grid_has_exact_124_requested_and_unique_points(self):
        self.assertEqual(len(self.grid), 124)
        self.assertEqual(len(set(self.grid)), 124)
        self.assertEqual((self.grid[0], self.grid[-1]), (10.0, 20000.0))
        for fixed in (400.0, 800.0, 1600.0):
            self.assertEqual(self.grid.count(fixed), 1)
        geometric = sorted(set(self.grid) - {400.0, 800.0, 1600.0})
        self.assertEqual(len(geometric), 121)
        for index, actual in enumerate(geometric):
            expected = math.exp(math.log(10.0) + index / 120.0 * (math.log(20000.0) - math.log(10.0)))
            self.assertLessEqual(abs(actual / expected - 1.0), 4.0e-15)

    def test_both_methods_against_independent_polynomials_for_all_loads(self):
        largest = 0.0
        comparisons = 0
        for rt, rw in LOADS:
            network = reference.prepare_network(PROFILE, treble_ohms=rt, bass_ohms=rw)
            for frequency in self.grid:
                wanted = polynomial_answer(frequency, rt, rw)
                for producer in (reference.analog_response, reference.nodal_response):
                    answer = producer(network, frequency)
                    for name, expected in zip(("treble_gain", "bass_gain", "input_admittance"), wanted):
                        actual = getattr(answer, name)
                        error = abs(actual - expected) / max(1.0, abs(expected))
                        largest = max(largest, error)
                        comparisons += 1
                        self.assertLessEqual(error, 2.0e-10, (producer.__name__, rt, rw, frequency, name))
        self.assertEqual(comparisons, 4464)
        print(f"crossover polynomial oracle: {comparisons} comparisons; maximum normalized error {largest:.17g}")

    def test_dc_limits_for_each_load_and_potential_orientation(self):
        for rt, rw in LOADS:
            network = reference.prepare_network(PROFILE, treble_ohms=rt, bass_ohms=rw)
            for producer in (reference.analog_response, reference.nodal_response):
                result = producer(network, 0.0)
                self.assertEqual(result.treble_gain, 0.0j)
                self.assertEqual(result.bass_gain, 1.0 + 0.0j)
                self.assertEqual(result.input_admittance, complex(1.0 / rw))
            nodes = dict(reference.nodal_response(network, 0.0).node_voltages)
            self.assertEqual(nodes, {"A": 1.0 + 0.0j, "B": 0.0j, "H": 1.0 + 0.0j, "W": 1.0 + 0.0j})

    def test_near_dc_reactive_current_survives_equipotential_inductor_nodes(self):
        # A19 found a 3.2545e-10 A/V loss of imaginary current at 1e-8 Hz
        # and RW=1 when the nodal solver summed source-inductor voltage drops.
        # The independent reduced polynomial retains that term; a tight
        # relative check of its imaginary part catches cancellation despite
        # the much larger real DC conductance.
        maximum = 0.0
        comparisons = 0
        for rt, rw in LOADS:
            network = reference.prepare_network(PROFILE, treble_ohms=rt, bass_ohms=rw)
            for frequency in (1.0e-12, 1.0e-8, 1.0e-4, 0.1):
                expected = polynomial_answer(frequency, rt, rw)
                nodal = reference.nodal_response(network, frequency)
                analytic = reference.analog_response(network, frequency)
                for name, wanted in zip(("treble_gain", "bass_gain", "input_admittance"), expected):
                    for result in (nodal, analytic):
                        error = abs(getattr(result, name) - wanted) / max(1.0, abs(wanted))
                        maximum = max(maximum, error)
                        comparisons += 1
                        self.assertLessEqual(error, 2.0e-14, (rt, rw, frequency, name))
                self.assertLessEqual(abs(nodal.input_admittance.imag - expected[2].imag),
                                     2.0e-12 * abs(expected[2].imag))
                # Check current orientation at the distinct grounded load
                # branches without subtracting nearly equal source nodes.
                nodes = dict(nodal.node_voltages)
                s = 1j * 2.0 * math.pi * frequency
                ground_return = s * 7.8e-6 * nodes["H"] + (1.0 / rw + s * 12.5e-6) * nodes["W"]
                self.assertLessEqual(abs(nodal.input_admittance - ground_return), 4.0e-16)
        self.assertEqual(comparisons, 144)
        print(f"crossover near-DC oracle: {comparisons} comparisons; maximum normalized error {maximum:.17g}")

    def test_atlas_800_hz_sanity_and_floating_treble_return(self):
        answer = reference.nodal_response(self.network, 800.0)
        self.assertAlmostEqual(20 * math.log10(abs(answer.treble_gain)), -4.60021838, delta=1.0e-7)
        self.assertAlmostEqual(math.degrees(cmath.phase(answer.treble_gain)), 110.173593, delta=1.0e-6)
        self.assertAlmostEqual(20 * math.log10(abs(answer.bass_gain)), -4.88733013, delta=1.0e-7)
        self.assertAlmostEqual(math.degrees(cmath.phase(answer.bass_gain)), -111.463524, delta=1.0e-6)
        self.assertAlmostEqual(abs(1.0 / answer.input_admittance), 23.82990440, delta=1.0e-7)
        nodes = dict(answer.node_voltages)
        self.assertEqual(answer.treble_gain, nodes["A"] - nodes["H"])
        self.assertNotEqual(answer.treble_gain, nodes["H"] - nodes["B"])

    def test_nodal_residual_and_resistor_power_identity(self):
        maximum = 0.0
        for rt, rw in LOADS:
            network = reference.prepare_network(PROFILE, treble_ohms=rt, bass_ohms=rw)
            for frequency in self.grid:
                result = reference.nodal_response(network, frequency)
                self.assertLessEqual(result.normalized_residual, 1.0e-12)
                self.assertGreaterEqual(result.input_admittance.real, 0.0)
                loss = abs(result.treble_gain) ** 2 / rt + abs(result.bass_gain) ** 2 / rw
                error = abs(result.input_admittance.real - loss) / max(1.0, loss)
                maximum = max(maximum, error)
                self.assertLessEqual(error, 2.0e-10)
        print(f"crossover ideal power balance: maximum normalized error {maximum:.17g}")

    def test_warped_frequency_domain_is_not_limited_to_audio_band(self):
        for rate in (44100, 48000, 96000, 192000):
            frequency = rate / math.pi * math.tan(math.pi * 0.49)
            self.assertGreater(frequency, rate / 2.0)
            for actual, expected in zip(
                    (reference.nodal_response(self.network, frequency).treble_gain,
                     reference.nodal_response(self.network, frequency).bass_gain,
                     reference.nodal_response(self.network, frequency).input_admittance),
                    polynomial_answer(frequency, 16.0, 16.0)):
                self.assertLessEqual(abs(actual - expected) / max(1.0, abs(expected)), 2.0e-10)

    def test_invalid_frequencies_and_loads(self):
        for bad in (-1.0, float("nan"), float("inf"), "800", True, 10 ** 1000):
            for producer in (reference.analog_response, reference.nodal_response):
                with self.subTest(value=bad, producer=producer.__name__):
                    with self.assertRaises(reference.ReferenceError):
                        producer(self.network, bad)
        for bad in (0.0, -1.0, 1024.0000001, float("nan"), float("inf"), "16", True, 10 ** 1000):
            for name in ("treble_ohms", "bass_ohms"):
                with self.subTest(value=bad, name=name):
                    with self.assertRaises(reference.ReferenceError):
                        reference.prepare_network(PROFILE, **{name: bad})

    def test_report_is_deterministic_and_scopes_alternative_loads(self):
        first = reference.make_report(self.network)
        second = reference.make_report(self.network)
        self.assertEqual(json.dumps(first, sort_keys=True, allow_nan=False),
                         json.dumps(second, sort_keys=True, allow_nan=False))
        self.assertTrue(first["acceptance"]["passed"])
        self.assertEqual(len(first["responses"]), 124)
        self.assertEqual(first["grid"], {"id": reference.GRID_ID, "requested_count": 124,
                                       "unique_count": 124, "duplicate_count": 0, "dc_is_separate": True})
        self.assertEqual(first["reference_code_sha256"], hashlib.sha256(TOOL.read_bytes()).hexdigest())
        self.assertEqual(first["experiment"]["kind"], "atlas-ideal-resistor-fixture")
        alternate = reference.make_report(reference.load_network(REGISTRY, treble_ohms=8.0, bass_ohms=32.0))
        self.assertEqual(alternate["model_id"], first["model_id"])
        self.assertEqual(alternate["experiment"], {"kind": "alternative-resistor-experiment",
                                               "treble_ohms": 8.0, "bass_ohms": 32.0,
                                               "actual_driver_measurements": False})
        self.assertEqual(alternate["registry_bytes_sha256"], first["registry_bytes_sha256"])
        self.assertNotEqual(alternate["dc"], first["dc"])

    def test_raw_and_canonical_identity_are_distinguished(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "registry.json"
            path.write_text(json.dumps(PROFILE, sort_keys=True), encoding="utf-8")
            changed = reference.load_network(path)
            self.assertEqual(changed.registry_canonical_sha256, self.network.registry_canonical_sha256)
            self.assertNotEqual(changed.registry_bytes_sha256, self.network.registry_bytes_sha256)

    def test_cli_output_is_reproducible_json_with_explicit_experiment(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            result = self.cli("--output", path)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "")
            first = path.read_bytes()
            self.assertLess(len(first), 256 * 1024)
            result = self.cli("--output", path)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(path.read_bytes(), first)
            result = self.cli("--treble-ohms", 1, "--bass-ohms", 1024)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["experiment"]["kind"], "alternative-resistor-experiment")
            self.assertEqual(report["experiment"]["bass_ohms"], 1024.0)
            self.assertEqual(list(Path(directory).iterdir()), [path])

    def test_cli_invalid_inputs_preserve_existing_output_and_input(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "existing.json"
            output.write_text("preserve me\n", encoding="utf-8")
            bad_registry = Path(directory) / "bad.json"
            bad_registry.write_text("{}", encoding="utf-8")
            for args in (("--treble-ohms", "nan"), ("--bass-ohms", "1025"),
                         ("--registry", bad_registry), ("--registry", Path(directory) / "absent.json")):
                result = self.cli(*args, "--output", output)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn("crossover_reference:", result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(output.read_text(encoding="utf-8"), "preserve me\n")
            good_registry = Path(directory) / "good.json"
            good_registry.write_bytes(REGISTRY.read_bytes())
            before = good_registry.read_bytes()
            result = self.cli("--registry", good_registry, "--output", good_registry)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertEqual(good_registry.read_bytes(), before)
            result = self.cli("--output", Path(directory) / "absent" / "report.json")
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
