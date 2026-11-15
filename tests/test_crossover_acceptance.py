#!/usr/bin/env python3
"""Independent native crossover qualification against registry-stamped nodal KCL.

Requires HAMMOND_CROSSOVER_PROBE_EXECUTABLE; absence is an error, never a skip.
The probe reports public-API results. This test derives its oracle from physical
edges and bounds startup with the two branch polynomials, without copying the
native state matrix or using native response() as a processing oracle.
An optional HAMMOND_CROSSOVER_ACCEPTANCE_REPORT path retains compact evidence.
"""

from __future__ import annotations

import cmath
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import crossover_reference as reference


PORTS = ("treble_gain", "bass_gain", "input_admittance")
RATES = (44100, 48000, 96000, 192000)
LOADS = ((16.0, 16.0), (1.0, 1.0), (1024.0, 1024.0),
         (1.0, 1024.0), (1024.0, 1.0), (8.0, 32.0))
RESPONSE_LIMIT = 2.0e-10
SINE_LIMIT = 2.0e-8
TAIL_TARGET = 1.0e-11
MAX_STDOUT = 2 * 1024 * 1024
SOURCE_PATHS = (
    "tools/crossover_probe.cpp", "tools/crossover_reference.py",
    "tests/test_crossover_acceptance.py", "include/hammond/LeslieCrossover.h",
    "src/LeslieCrossover.cpp", "data/crossover/leslie-122-ideal-v1.json",
)


def identity(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON member: {key}")
        result[key] = value
    return result


def reject_constant(token: str) -> None:
    raise ValueError(f"Nonfinite JSON token: {token}")


def finite_tree(value: object) -> None:
    if type(value) is float and not math.isfinite(value):
        raise ValueError("Nonfinite numeric JSON value")
    if isinstance(value, dict):
        for child in value.values():
            finite_tree(child)
    if isinstance(value, list):
        for child in value:
            finite_tree(child)


def read_ports(value: dict) -> dict[str, complex]:
    if set(value) != set(PORTS):
        raise ValueError("Unexpected electrical port keys")
    result = {}
    for name in PORTS:
        parts = value[name]
        if set(parts) != {"real", "imag"} or any(type(v) not in (float, int) for v in parts.values()):
            raise ValueError("Invalid complex electrical port")
        result[name] = complex(parts["real"], parts["imag"])
    return result


def warp(rate: float, frequency: float) -> float:
    return rate / math.pi * math.tan(math.pi * frequency / rate)


def circuit_tail(network: reference.Network, rate: int, frequency: float
                 ) -> tuple[int, float, float]:
    """Return warmup, absolute unit-gain tail bound, and largest pole modulus.

    Each physical branch has C*v'' + v'/R + v/L = 0 in its homogeneous
    capacitor voltage. Solve that scalar polynomial, then map each continuous
    pole by trapezoidal integration. This is independent of the native 4x4
    realization. Initial error is minus the nodal steady state's imaginary part
    because the probe starts sin(0)=0 with all four physical states zero.

    For source current, the treble homogeneous contribution is C16A*vH';
    the bass contribution is C16B*vW' + vW/RW. Absolute modal coefficients
    therefore bound all three observed SI quantities without cancellation.
    """
    values = {element.id: element.value for element in network.components}
    omega = math.tau * warp(rate, frequency)
    steady = reference.nodal_response(network, omega / math.tau)
    nodes = dict(steady.node_voltages)
    terms: dict[str, list[tuple[float, float]]] = {name: [] for name in PORTS}
    for capacitor, inductor, resistance, node, output in (
        ("C16A", "L2", network.treble_ohms, "H", "treble_gain"),
        ("C16B", "L3", network.bass_ohms, "W", "bass_gain"),
    ):
        c, inductance = values[capacitor], values[inductor]
        damping = 1.0 / (resistance * c)
        radical = cmath.sqrt(complex(damping * damping - 4.0 / (inductance * c)))
        poles = ((-damping + radical) / 2.0, (-damping - radical) / 2.0)
        if abs(poles[0] - poles[1]) <= 1.0e-10 * max(abs(poles[0]), abs(poles[1])):
            raise ValueError("Selected acceptance load is too close to a repeated branch pole")
        voltage = nodes[node]
        current = (1.0 - voltage) / complex(0.0, omega * inductance)
        v0, i0 = -voltage.imag, -current.imag
        derivative0 = (i0 - v0 / resistance) / c
        coefficients = ((derivative0 - poles[1] * v0) / (poles[0] - poles[1]),
                        (poles[0] * v0 - derivative0) / (poles[0] - poles[1]))
        for pole, coefficient in zip(poles, coefficients):
            z = (1.0 + pole / (2.0 * rate)) / (1.0 - pole / (2.0 * rate))
            rho = abs(z)
            if not 0.0 < rho < 1.0:
                raise ValueError("Independent branch pole is not strictly decaying")
            terms[output].append((abs(coefficient), rho))
            multiplier = c * pole if node == "H" else c * pole + 1.0 / resistance
            terms["input_admittance"].append((abs(multiplier * coefficient), rho))
    largest_modulus = max(rho for values_ in terms.values() for _, rho in values_)
    total_coefficient = max(sum(magnitude for magnitude, _ in values_) for values_ in terms.values())
    warmup = max(0, math.ceil(math.log(TAIL_TARGET / max(TAIL_TARGET, total_coefficient))
                             / math.log(largest_modulus))) + 2
    bound = max(sum(magnitude * rho ** warmup for magnitude, rho in values_)
                for values_ in terms.values())
    if warmup > 2_000_000 or bound > TAIL_TARGET:
        raise ValueError("Independent settling budget exceeded")
    return warmup, bound, largest_modulus


class CrossoverAcceptance(unittest.TestCase):
    processes = 0
    response_comparisons = 0
    sine_comparisons = 0
    maximum_response_error = 0.0
    maximum_sine_error = 0.0
    maximum_response_residual = 0.0
    maximum_tail_gain_bound = 0.0
    maximum_half_window_difference = 0.0
    response_groups: list[dict] = []
    sine_groups: list[dict] = []

    @classmethod
    def setUpClass(cls) -> None:
        configured = os.environ.get("HAMMOND_CROSSOVER_PROBE_EXECUTABLE")
        if not configured:
            raise RuntimeError("HAMMOND_CROSSOVER_PROBE_EXECUTABLE is required; build hammond_crossover_probe")
        cls.executable = Path(configured).resolve(strict=True)
        if not cls.executable.is_file() or not os.access(cls.executable, os.X_OK):
            raise RuntimeError("Configured crossover probe must be an executable file")
        cls.binary_sha256 = identity(cls.executable)
        cls.source_sha256 = {name: identity(ROOT / name) for name in SOURCE_PATHS}
        print("Crossover probe SHA-256: " + cls.binary_sha256, flush=True)

    @classmethod
    def tearDownClass(cls) -> None:
        if identity(cls.executable) != cls.binary_sha256 or any(
                identity(ROOT / name) != digest for name, digest in cls.source_sha256.items()):
            raise RuntimeError("Qualified binary or relevant source changed during acceptance")

    def run_probe(self, arguments: list[str], success: bool = True) -> dict | subprocess.CompletedProcess:
        self.__class__.processes += 1
        try:
            process = subprocess.run([str(self.executable), *arguments], stdin=subprocess.DEVNULL,
                                     capture_output=True, text=True, encoding="utf-8", errors="strict",
                                     timeout=20, check=False)
        except subprocess.TimeoutExpired as error:
            self.fail(f"Bounded crossover probe timed out: {error}")
        self.assertLessEqual(len(process.stdout.encode()), MAX_STDOUT)
        if not success:
            self.assertEqual(process.returncode, 2, process.stderr)
            self.assertEqual(process.stdout, "", "Refusal must not emit partial successful JSON")
            self.assertTrue(process.stderr.startswith("crossover_probe: "))
            return process
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(process.stderr, "")
        report = json.loads(process.stdout, object_pairs_hook=unique_object, parse_constant=reject_constant)
        finite_tree(report)
        self.assertEqual(report["schema_version"], 1)
        self.assertEqual(report["probe_id"], "leslie-crossover-public-api-probe-v1")
        self.assertEqual(report["model_id"], "atlas-leslie-122-ideal-crossover-v1")
        self.assertEqual(report["realization_id"], "physical-trapezoidal-leslie-crossover-v1")
        self.assertIs(report["physical_measurement_claim"], False)
        self.assertIs(report["engine_integration"], False)
        self.assertLessEqual(report["preparation_residual"], 1.0e-12)
        return report

    @staticmethod
    def base(operation: str, rate: int, loads: tuple[float, float]) -> list[str]:
        return ["--operation", operation, "--sample-rate", str(rate),
                "--treble-ohms", str(loads[0]), "--bass-ohms", str(loads[1])]

    def test_native_response_against_nodal_ac_and_same_hz_characterization(self) -> None:
        nominal_points = {400.0, 800.0, 1600.0, 5000.0, 10000.0, 20000.0}
        for rate in RATES:
            frequencies = sorted(set(reference.default_frequency_grid()) | nominal_points |
                                 {0.0, 1.0e-8, rate * 0.499999, math.nextafter(rate / 2.0, 0.0)})
            for loads in LOADS:
                with self.subTest(rate=rate, loads=loads):
                    network = reference.load_network(treble_ohms=loads[0], bass_ohms=loads[1])
                    report = self.run_probe(self.base("response", rate, loads) +
                                            ["--frequencies", ",".join(format(f, ".17g") for f in frequencies)])
                    self.assertEqual(report["operation"], "response")
                    self.assertEqual(report["sample_rate_hz"], rate)
                    self.assertEqual(report["loads"], {"treble_ohms": loads[0], "bass_ohms": loads[1]})
                    self.assertEqual(len(report["responses"]), len(frequencies))
                    maxima = {name: 0.0 for name in PORTS}
                    same_hz = {name: {"normalized_complex_error": 0.0, "magnitude_error_db": 0.0,
                                     "phase_error_degrees": 0.0} for name in PORTS}
                    point_rows = []
                    for frequency, row in zip(frequencies, report["responses"]):
                        self.assertEqual(row["frequency_hz"], frequency)
                        self.assertLessEqual(row["normalized_residual"], 1.0e-12)
                        self.__class__.maximum_response_residual = max(
                            self.maximum_response_residual, row["normalized_residual"])
                        observed = read_ports(row["transfer"])
                        expected = reference.nodal_response(network, warp(rate, frequency))
                        ordinary = reference.nodal_response(network, frequency)
                        details = {}
                        for name in PORTS:
                            error = reference.normalized_error(observed[name], getattr(expected, name))
                            maxima[name] = max(maxima[name], error)
                            self.__class__.response_comparisons += 1
                            self.__class__.maximum_response_error = max(self.maximum_response_error, error)
                            self.assertLessEqual(error, RESPONSE_LIMIT, f"{rate=} {loads=} {frequency=} {name=}")
                            if frequency == 0.0:
                                self.assertEqual(observed[name], getattr(expected, name))
                            if 10.0 <= frequency <= 20000.0:
                                same = getattr(ordinary, name)
                                ratio = observed[name] / same
                                detail = {"normalized_complex_error": reference.normalized_error(observed[name], same),
                                          "magnitude_error_db": 20.0 * math.log10(abs(ratio)),
                                          "phase_error_degrees": math.degrees(cmath.phase(ratio))}
                                details[name] = detail
                                for metric, value in detail.items():
                                    same_hz[name][metric] = max(same_hz[name][metric], abs(value))
                        if loads == (16.0, 16.0) and frequency in nominal_points:
                            point_rows.append({"frequency_hz": frequency, "same_hz_errors": details})
                    self.__class__.response_groups.append({
                        "sample_rate_hz": rate, "treble_ohms": loads[0], "bass_ohms": loads[1],
                        "frequencies": len(frequencies), "maximum_warped_normalized_errors": maxima,
                        "same_hz_10_to_20000_maximum_absolute_errors": same_hz,
                        "nominal_same_hz_points": point_rows,
                    })

    def test_processed_sine_has_independently_bounded_startup(self) -> None:
        for rate in RATES:
            for loads in LOADS:
                network = reference.load_network(treble_ohms=loads[0], bass_ohms=loads[1])
                for frequency in (400.125, 800.0, 1600.375, 0.43 * rate):
                    with self.subTest(rate=rate, loads=loads, frequency=frequency):
                        warmup, tail, rho = circuit_tail(network, rate, frequency)
                        report = self.run_probe(self.base("sine", rate, loads) +
                            ["--frequency", format(frequency, ".17g"), "--warmup-frames", str(warmup),
                             "--measurement-frames", "8192", "--amplitude", "0.125"])
                        self.assertEqual(report["completed_frames"], warmup + 8192)
                        self.assertEqual(report["frequency_hz"], frequency)
                        self.assertEqual(report["warmup_frames"], warmup)
                        self.assertEqual(report["measurement_frames"], 8192)
                        amplification = max(report[name] for name in (
                            "fit_error_amplification_bound", "first_half_error_amplification_bound",
                            "second_half_error_amplification_bound"))
                        self.assertLess(amplification, 8.0)
                        # The bound is for unit-amplitude startup. Amplitude
                        # cancels on both the experiment and fitted gain.
                        fitted_tail_bound = tail * amplification
                        self.assertLessEqual(fitted_tail_bound, SINE_LIMIT / 100.0)
                        self.__class__.maximum_tail_gain_bound = max(self.maximum_tail_gain_bound, fitted_tail_bound)
                        self.assertLessEqual(report["half_window_max_difference"], SINE_LIMIT)
                        self.__class__.maximum_half_window_difference = max(
                            self.maximum_half_window_difference, report["half_window_max_difference"])
                        expected = reference.nodal_response(network, warp(rate, frequency))
                        maximum_error = 0.0
                        for fit_name in ("transfer", "first_half_transfer", "second_half_transfer"):
                            observed = read_ports(report[fit_name])
                            for name in PORTS:
                                error = reference.normalized_error(observed[name], getattr(expected, name))
                                self.__class__.sine_comparisons += 1
                                maximum_error = max(maximum_error, error)
                                self.__class__.maximum_sine_error = max(self.maximum_sine_error, error)
                                self.assertLessEqual(error, SINE_LIMIT,
                                                     f"{rate=} {loads=} {frequency=} {fit_name=} {name=}")
                        self.__class__.sine_groups.append({
                            "sample_rate_hz": rate, "treble_ohms": loads[0], "bass_ohms": loads[1],
                            "frequency_hz": frequency, "warmup_frames": warmup,
                            "independent_largest_pole_modulus": rho,
                            "independent_all_fit_tail_bound": fitted_tail_bound,
                            "maximum_warped_normalized_error": maximum_error,
                            "half_window_max_difference": report["half_window_max_difference"],
                        })

    def test_probe_rejects_bad_or_unbounded_experiments_without_partial_json(self) -> None:
        response = ["--operation", "response", "--sample-rate", "48000"]
        sine = ["--operation", "sine", "--sample-rate", "48000", "--frequency", "800"]
        invalid = [
            [], ["--operation", "response"], ["--sample-rate", "48000"],
            ["--operation", "trace", "--sample-rate", "48000"],
            ["--operation", "response", "--sample-rate", "32000", "--frequencies", "800"],
            response, response + ["--frequencies"], response + ["--frequencies", ""],
            response + ["--frequencies", "0,"], response + ["--frequencies", "0,,800"],
            response + ["--frequencies", ",".join(["1"] * 513)],
            response + ["--frequencies", "-1"], response + ["--frequencies", "24000"],
            response + ["--frequencies", "NaN"], response + ["--frequencies", "1e999"],
            response + ["--frequencies", "800tail"], response + ["--frequencies", "0x10"],
            response + ["--frequencies", "800", "--sample-rate", "48000"],
            response + ["--frequencies", "800", "--frequency", "800"],
            response + ["--frequencies", "800", "--treble-ohms", "0"],
            response + ["--frequencies", "800", "--bass-ohms", "1024.000001"],
            response + ["--frequencies", "800", "--unknown", "1"],
            sine + ["--amplitude", "0"], sine + ["--amplitude", "64.0001"],
            sine + ["--warmup-frames", "-1"], sine + ["--measurement-frames", "8.0"],
            sine + ["--measurement-frames", "7"], sine + ["--measurement-frames", "16777217"],
            sine + ["--warmup-frames", "18446744073709551615"],
            sine + ["--measurement-frames", "18446744073709551616"],
            sine + ["--frequencies", "800"],
            ["--operation", "sine", "--sample-rate", "48000", "--frequency", "0"],
            ["--operation", "sine", "--sample-rate", "48000", "--frequency", "1e-20",
             "--warmup-frames", "0", "--measurement-frames", "8"],
        ]
        for arguments in invalid:
            with self.subTest(arguments=arguments[:8]):
                self.run_probe(arguments, success=False)


def write_report(result: unittest.TestResult) -> dict:
    suite = CrossoverAcceptance
    report = {
        "schema_version": 1, "acceptance_id": "leslie-crossover-native-nodal-acceptance-v1",
        "passed": result.wasSuccessful(), "tests_run": result.testsRun,
        "failures": len(result.failures), "errors": len(result.errors),
        "platform": platform.platform(), "python": platform.python_version(),
        "binary_sha256": getattr(suite, "binary_sha256", None),
        "source_sha256": getattr(suite, "source_sha256", {}),
        "provenance_boundary": "Observed immutable inputs, not an independent compiler/source-to-binary attestation",
        "subprocesses": suite.processes, "response_port_comparisons": suite.response_comparisons,
        "sine_port_comparisons": suite.sine_comparisons,
        "maximum_warped_response_error": suite.maximum_response_error,
        "maximum_warped_sine_error": suite.maximum_sine_error,
        "maximum_response_residual": suite.maximum_response_residual,
        "maximum_independent_sine_tail_gain_bound": suite.maximum_tail_gain_bound,
        "maximum_half_window_gain_difference": suite.maximum_half_window_difference,
        "limits": {"warped_response": RESPONSE_LIMIT, "settled_sine": SINE_LIMIT},
        "same_hz_status": "characterized only; no audible acceptance threshold or physical fidelity claim",
        "physical_measurement_claim": False, "engine_integration": False,
        "response_groups": suite.response_groups, "sine_groups": suite.sine_groups,
    }
    configured = os.environ.get("HAMMOND_CROSSOVER_ACCEPTANCE_REPORT")
    if configured:
        path = Path(configured).resolve()
        protected = {ROOT / name for name in SOURCE_PATHS}
        protected.add(getattr(suite, "executable", ROOT))
        if path in protected:
            raise ValueError("Acceptance report must not replace an input")
        text = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=".crossover-acceptance-", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(text)
        try:
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)
    return report


if __name__ == "__main__":
    completed = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(CrossoverAcceptance))
    evidence = write_report(completed)
    print(json.dumps({key: value for key, value in evidence.items()
                      if key not in ("source_sha256", "response_groups", "sine_groups")}, sort_keys=True, allow_nan=False))
    raise SystemExit(0 if completed.wasSuccessful() else 1)
