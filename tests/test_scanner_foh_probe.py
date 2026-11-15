#!/usr/bin/env python3
"""FOH native CLI, physical output and original-knot adapter regressions.

These producer checks do not qualify the independent full-grid/process/transient
protocol. They deliberately use literal circuit DC/KCL identities and direct
endpoint replays rather than treating an old trapezoidal result as an oracle.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "data/scanner/atlas-late-b3-nominal-v1.json"
RATES = (44100, 48000, 88200, 96000, 176400, 192000, 352800,
         384000, 705600, 768000, 1536000)
MODES = ("vibrato", "chorus")
NORMAL_CLOCK = ("previous_endpoint_at_minus_one_sample;first_processed_knot_at_zero;"
                "frame_counts_completed_intervals")
TRACE_CLOCK = ("previous_endpoint_at_minus_one_input_knot;first_emitted_knot_at_zero;"
               "frame_counts_completed_internal_intervals")
UINT64_MAX = 2**64 - 1


def csv(values):
    return ",".join(format(value, ".17g") for value in values)


def complex_channels(row):
    return ([complex(*value) for value in row["taps"]]
            + [complex(*row["return_gain"]), 15000 * complex(*row["input_admittance"])])


class ScannerFohProbe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get("HAMMOND_SCANNER_LINE_FOH_PROBE_EXECUTABLE")
        cls.probe = Path(value).resolve() if value else None
        if cls.probe is None or not cls.probe.is_file():
            raise RuntimeError("Build hammond_scanner_line_foh_probe and run through CTest; "
                               "HAMMOND_SCANNER_LINE_FOH_PROBE_EXECUTABLE is required")
        cls.profile_sha = hashlib.sha256(PROFILE.read_bytes()).hexdigest()

    def invoke(self, *arguments, stdin=b"", timeout=45):
        return subprocess.run([str(self.probe), *map(str, arguments)], input=stdin,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              cwd=ROOT, timeout=timeout, check=False)

    def rejected(self, *arguments, stdin=b"", diagnostic=None):
        result = self.invoke(*arguments, stdin=stdin)
        self.assertEqual(result.returncode, 1, result.stderr.decode(errors="replace"))
        self.assertEqual(result.stdout, b"", "failure leaked a partial JSON document")
        self.assertTrue(result.stderr.startswith(b"hammond_scanner_line_foh_probe:"))
        if diagnostic is not None:
            self.assertIn(diagnostic.encode(), result.stderr)
        return result

    def report(self, operation, *arguments, rate=48000, mode="vibrato", stdin=b""):
        result = self.invoke("--operation", operation, "--sample-rate", rate,
                             "--mode", mode, *arguments, stdin=stdin)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        self.assertEqual(result.stderr, b"")
        self.assertTrue(result.stdout.endswith(b"\n"))
        record = json.loads(result.stdout, parse_constant=lambda value: self.fail(value))
        self.assertEqual(record["schema_version"], 1)
        self.assertEqual(record["probe_id"], "scanner-line-foh-probe-v1")
        self.assertEqual(record["model_id"], "atlas-late-b3-nominal-line-v1")
        self.assertEqual(record["realization_id"], "scaled-physical-exponential-foh-scanner-line-v1")
        self.assertEqual(record["preparation_method_id"],
                         "scanner-augmented38-pade13-scaling-squaring-v1")
        self.assertEqual(record["authoring_sha256"], self.profile_sha)
        self.assertEqual(record["evidence_scope"], "synthetic_nominal_engineering")
        self.assertEqual(record["operation"], operation)
        self.assertEqual(record["sample_rate_hz"], rate)
        self.assertEqual(record["mode"], mode)
        self.assertEqual(record["clock_convention"], TRACE_CLOCK if operation == "trace" else NORMAL_CLOCK)
        self.assertEqual(record["input_reconstruction"], "piecewise_linear_between_internal_endpoints")
        self.assertNotIn(b"trapezoidal_endpoint_forcing", result.stdout)
        self.assertNotIn("summary", record)
        self.assertNotIn("passed", record)
        self.assertEqual(len(record["preparation_diagnostics"]), 2)
        for diagnostic in record["preparation_diagnostics"]:
            self.assertEqual(set(diagnostic), {"augmented_norm_one", "squarings",
                                               "normalized_residual", "condition_inf"})
            self.assertIs(type(diagnostic["squarings"]), int)
            self.assertGreaterEqual(diagnostic["squarings"], 0)
            self.assertLessEqual(diagnostic["squarings"], 16)
            self.assertGreater(diagnostic["augmented_norm_one"], 0)
            self.assertLessEqual(math.ldexp(diagnostic["augmented_norm_one"],
                                           -diagnostic["squarings"]), 0.5)
            self.assertLessEqual(diagnostic["normalized_residual"], 1e-9)
            self.assertGreater(diagnostic["condition_inf"], 0)
            self.assertLessEqual(diagnostic["condition_inf"] * 2**-52, 1e-4)
        self.assertEqual(record["preparation_residual"],
                         max(item["normalized_residual"] for item in record["preparation_diagnostics"]))
        self.finite_numbers(record)
        return record

    def finite_numbers(self, item):
        if isinstance(item, dict):
            for value in item.values():
                self.finite_numbers(value)
        elif isinstance(item, list):
            for value in item:
                self.finite_numbers(value)
        elif isinstance(item, (float, int)):
            self.assertTrue(math.isfinite(item))

    def assert_state_close(self, first, second):
        for key, scale in (("capacitor_volts", 1), ("inductor_amps", 10000)):
            self.assertEqual(len(first[key]), 18)
            self.assertEqual(len(second[key]), 18)
            for left, right in zip(first[key], second[key]):
                self.assertLessEqual(abs(left - right) * scale, 1e-9 + 1e-8 * abs(right) * scale)
        self.assertEqual(first["previous_input_volts"], second["previous_input_volts"])

    def test_all_rates_dc_and_signed_boundary_identities(self):
        # At DC every ideal inductor is a short, every capacitor is open and
        # all p nodes are 1 V. These are literal documentary resistor values.
        upper = (27000, 56000, 39000, 33000, 18000, 12000)
        lower = (68000, 150000, 150000, 180000, 180000, 180000)
        conductance = sum((Fraction(1, a + b) for a, b in zip(upper, lower)), Fraction(1, 15000))
        for rate in RATES:
            for mode in MODES:
                with self.subTest(rate=rate, mode=mode):
                    record = self.report("response", "--frequencies", "0,100,997,5000,7000,20000",
                                         rate=rate, mode=mode)
                    self.assertEqual(record["measurement_method"], "prepared_discrete_recurrence_solve")
                    dc_return = (Fraction(0) if mode == "vibrato"
                                 else 22000 * conductance / (1 + 22000 * conductance))
                    dc_current = (1 - dc_return) * conductance
                    expected = ([dc_return + (1 - dc_return) * Fraction(b, a + b)
                                 for a, b in zip(upper, lower)]
                                + [Fraction(1)] * 13 + [dc_return, 15000 * dc_current])
                    for actual, wanted in zip(complex_channels(record["responses"][0]), expected):
                        self.assertLessEqual(abs(actual - float(wanted)), 1e-10 + 1e-9 * abs(wanted))
                    for row in record["responses"]:
                        self.assertEqual(len(row["taps"]), 19)
                        self.assertLessEqual(row["normalized_residual"], 1e-9)
                        self.assertGreater(row["condition_inf"], 0)
                        returned = complex(*row["return_gain"])
                        self.assertLess(abs(complex(*row["taps"][0]) - 68/95 - 27/95 * returned), 1e-12)
                        if mode == "vibrato":
                            self.assertEqual(returned, 0j)
                        else:
                            self.assertLess(abs(complex(*row["input_admittance"]) - returned/22000), 1e-14)

    def test_response_order_repetition_and_count_boundary(self):
        requested = [997, 0, 997, 5000]
        rows = self.report("response", "--frequencies", csv(requested))["responses"]
        self.assertEqual([row["frequency_hz"] for row in rows], requested)
        self.assertEqual(rows[0], rows[2])
        maximum = self.report("response", "--frequencies", ",".join(["0"] * 1024))
        self.assertEqual(len(maximum["responses"]), 1024)
        self.rejected("--operation", "response", "--sample-rate", 48000, "--mode", "vibrato",
                      "--frequencies", ",".join(["0"] * 1025), diagnostic="Too many comma-separated")

    def test_actual_sine_window_metadata_and_recurrence_consistency(self):
        for mode in MODES:
            with self.subTest(mode=mode):
                record = self.report("sine", "--frequency", 997, "--amplitude", 0.125,
                                     "--warmup-frames", 96000, "--measurement-frames", 24001, mode=mode)
                self.assertEqual(record["measurement_method"],
                                 "actual_process_frame_cos_sin_constant_least_squares")
                self.assertEqual(record["startup_convergence_status"], "caller_must_compare_longer_warmup")
                self.assertEqual((record["first_half_frames"], record["second_half_frames"]), (12000, 12001))
                self.assertEqual(record["final_state"]["frames"], 120001)
                self.assertEqual(record["half_window_current_scale_ohms"], 15000)
                self.assertEqual(len(record["fit_residual_rms"]["taps_volts"]), 19)
                response = self.report("response", "--frequencies", 997, mode=mode)["responses"][0]
                for name in ("transfer", "first_half_transfer", "second_half_transfer"):
                    for actual, expected in zip(complex_channels(record[name]), complex_channels(response)):
                        self.assertLessEqual(abs(actual - expected), 1e-8 + 1e-6 * abs(expected))
                last_input = 0.125 * math.cos(math.tau * 997 * 120000 / 48000)
                self.assertAlmostEqual(record["final_state"]["previous_input_volts"], last_input, delta=1e-11)

    def test_short_startup_is_actual_unsettled_processing(self):
        result = self.report("sine", "--frequency", 1000, "--warmup-frames", 0,
                             "--measurement-frames", 240, mode="chorus")
        response = self.report("response", "--frequencies", 1000, mode="chorus")["responses"][0]
        self.assertEqual(result["final_state"]["frames"], 240)
        self.assertGreater(max(abs(a-b) for a, b in zip(complex_channels(result["transfer"]),
                                                       complex_channels(response))), 1e-4)
        self.assertGreater(max(result["fit_residual_rms"]["taps_volts"]), 1e-4)

    def test_trace_default_clock_state_and_physical_observation(self):
        volts = [0.25] + [0.0] * 16 + [-0.5]
        amps = [0.000025] + [0.0] * 16 + [-0.00001]
        for mode in MODES:
            with self.subTest(mode=mode):
                result = self.report("trace", "--capacitor-volts", csv(volts), "--inductor-amps", csv(amps),
                                     "--previous-input", -0.25, "--initial-frame", 17, mode=mode,
                                     stdin=b"0.25\r\n0\n-0.5\n0.125")
                self.assertEqual(result["subdivisions"], 1)
                self.assertEqual(result["input_knot_rate_hz"], 48000)
                self.assertEqual(result["internal_steps"], 4)
                self.assertEqual(result["initial_endpoint_seconds"], -1/48000)
                self.assertEqual(result["initial_observation"]["time_seconds"], -1/48000)
                self.assertEqual(result["initial_observation"]["frame"], 17)
                self.assertEqual(result["initial_state"], {"capacitor_volts": volts, "inductor_amps": amps,
                                                          "previous_input_volts": -0.25, "frames": 17})
                expected_energy = 0.5*(4e-9*volts[0]**2 + 1e-9*volts[-1]**2
                                       + 0.5*amps[0]**2 + 0.5*amps[-1]**2)
                self.assertAlmostEqual(result["initial_observation"]["energy_joules"], expected_energy, delta=1e-24)
                for index, row in enumerate(result["frames"]):
                    self.assertEqual(row["knot_index"], index)
                    self.assertEqual(row["frame"], 18 + index)
                    self.assertEqual(row["state"]["frames"], row["frame"])
                    self.assertEqual(row["state"]["previous_input_volts"], row["input_volts"])
                    self.assertEqual(row["time_seconds"], index/48000)
                    self.assertEqual(len(row["taps_volts"]), 19)
                    self.assertEqual(len(row["state"]["capacitor_volts"]), 18)
                    self.assertEqual(len(row["state"]["inductor_amps"]), 18)

    def test_subdivision_preserves_original_polygon_and_expanded_endpoint_replay(self):
        values = (0.25, 0.0, -0.5, 0.125)
        payload = ("\n".join(map(str, values)) + "\n").encode()
        for mode in MODES:
            reference = None
            for factor in (1, 2, 4, 8, 16):
                with self.subTest(mode=mode, subdivisions=factor):
                    result = self.report("trace", "--subdivisions", factor, "--previous-input", -0.25,
                                         "--initial-frame", 17, rate=48000*factor, mode=mode, stdin=payload)
                    self.assertEqual(result["input_knot_adapter"], "offline_piecewise_linear_knot_subdivision")
                    self.assertEqual(result["input_knot_rate_hz"], 48000)
                    self.assertEqual(result["initial_endpoint_seconds"], -1/48000)
                    self.assertEqual(result["internal_steps"], 4*factor)
                    self.assertEqual(result["initial_observation"]["time_seconds"], -1/48000)
                    for index, row in enumerate(result["frames"]):
                        self.assertEqual(row["frame"], 17 + (index+1)*factor)
                        self.assertEqual(row["time_seconds"], index/48000)
                        self.assertEqual(row["input_volts"], values[index])
                        if reference is not None:
                            self.assert_state_close(row["state"], reference["frames"][index]["state"])
                    if reference is None:
                        reference = result
                    # Use the same internal rate and literal subdivisions as
                    # separate ordinary input knots. This catches repeated j=0,
                    # skipped intervals, wrong initial history and output mixing.
                    endpoints = []
                    previous = -0.25
                    for value in values:
                        endpoints.extend(previous + (value-previous)*j/factor for j in range(1, factor))
                        endpoints.append(value)
                        previous = value
                    expanded = self.report("trace", "--previous-input", -0.25, "--initial-frame", 17,
                                           rate=48000*factor, mode=mode,
                                           stdin=("\n".join(map(str, endpoints))+"\n").encode())
                    for index, row in enumerate(result["frames"]):
                        direct = expanded["frames"][(index+1)*factor-1]
                        for key in ("state", "frame", "taps_volts", "return_volts", "input_current_amps", "energy_joules"):
                            self.assertEqual(row[key], direct[key])

    def test_last_subendpoint_is_exact_supplied_input(self):
        record = self.report("trace", "--subdivisions", 2, "--previous-input", 64, rate=96000,
                             stdin=b"1e-200\n")
        # previous + (current-previous) rounds to zero for this pair. The final
        # endpoint must be assigned directly, preserving the supplied tiny drive.
        self.assertEqual(record["frames"][0]["input_volts"], 1e-200)
        self.assertEqual(record["frames"][0]["state"]["previous_input_volts"], 1e-200)

    def test_trace_counter_admission_counts_internal_steps(self):
        record = self.report("trace", "--subdivisions", 16, "--initial-frame", UINT64_MAX - 32,
                             rate=768000, stdin=b"0\n0\n")
        self.assertEqual(record["frames"][-1]["frame"], UINT64_MAX)
        for start in (UINT64_MAX - 31, UINT64_MAX):
            with self.subTest(start=start):
                self.rejected("--operation", "trace", "--sample-rate", 768000, "--mode", "vibrato",
                              "--subdivisions", 16, "--initial-frame", start, stdin=b"0\n0\n",
                              diagnostic="overflow")

    def test_trace_zero_maximum_knots_and_internal_steps(self):
        result = self.report("trace", "--subdivisions", 16, rate=768000, stdin=b"0\n"*16384)
        self.assertEqual(len(result["frames"]), 16384)
        self.assertEqual(result["internal_steps"], 262144)
        last = result["frames"][-1]
        self.assertEqual(last["frame"], 262144)
        self.assertEqual(last["energy_joules"], 0)
        self.assertEqual(last["state"]["capacitor_volts"], [0]*18)
        self.rejected("--operation", "trace", "--sample-rate", 768000, "--mode", "vibrato",
                      "--subdivisions", 16, stdin=b"0\n"*16385, diagnostic="16384")

    def test_help_is_separate_and_explains_internal_rate(self):
        result = self.invoke("--help")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, b"")
        self.assertIn(b"hammond_scanner_line_foh_probe", result.stdout)
        self.assertIn(b"--subdivisions", result.stdout)
        self.assertIn(b"internal line rate", result.stdout)
        self.rejected("--help", "--operation", "trace")

    def test_argument_admission_is_strict(self):
        base = ["--operation", "response", "--sample-rate", 48000, "--mode", "vibrato"]
        for extra in (("--frequency", 100), ("--amplitude", 1), ("--subdivisions", 1),
                      ("--mode", "chorus"), ("--unknown", 1), ("--frequencies",),
                      ("--frequencies", ""), ("--frequencies", "1,"), ("--frequencies", ",1")):
            with self.subTest(extra=extra):
                self.rejected(*base, *extra)
        for omitted in (0, 2, 4):
            self.rejected(*(base[:omitted] + base[omitted+2:]), "--frequencies", 0)
        # More than 32768 UTF-8 bytes but fewer than 32767 UTF-16 code units:
        # Windows can launch this command and its strict argv adapter rejects
        # it, rather than CreateProcess rejecting the command before our CLI.
        self.rejected(*base, "--frequencies", "é"*16385)
        self.rejected(*base, "--" + "é"*16384, "0")
        self.rejected(*(["--mode", "vibrato"]*14), diagnostic="Too many")

    def test_decimal_rate_mode_and_response_domains(self):
        for value in ("nan", "inf", "-inf", "1e9999", "1e-9999", " 1", "1 ", "0x1p0", "1x", "１"):
            with self.subTest(value=value):
                self.rejected("--operation", "response", "--sample-rate", 48000, "--mode", "vibrato",
                              "--frequencies", value)
        for value in (0, -1, 48001, "48000.0001", "nan"):
            self.rejected("--operation", "response", "--sample-rate", value,
                          "--mode", "vibrato", "--frequencies", 0)
        for value in ("Vibrato", "CHORUS", "rotary", ""):
            self.rejected("--operation", "response", "--sample-rate", 48000,
                          "--mode", value, "--frequencies", 0)
        for value in (-1, 24000, 24001):
            self.rejected("--operation", "response", "--sample-rate", 48000,
                          "--mode", "vibrato", "--frequencies", value)
        signed = self.report("response", "--frequencies", "+0,-0,+9.97e2")
        self.assertEqual([row["frequency_hz"] for row in signed["responses"]], [0, 0, 997])

    def test_sine_bounds_reject_before_output(self):
        base = ["--operation", "sine", "--sample-rate", 48000, "--mode", "vibrato", "--frequency", 1000]
        for extra in (("--amplitude", 0), ("--amplitude", -1), ("--amplitude", 64.01),
                      ("--measurement-frames", 7), ("--measurement-frames", 8),
                      ("--warmup-frames", 16777217), ("--measurement-frames", 16777216),
                      ("--warmup-frames", -1), ("--warmup-frames", "+1"),
                      ("--warmup-frames", "1.0"), ("--warmup-frames", UINT64_MAX+1),
                      ("--subdivisions", 2), ("--previous-input", 0)):
            with self.subTest(extra=extra):
                self.rejected(*base, *extra)
        for frequency in (0, -1, 24000):
            self.rejected(*base[:-1], frequency)

    def test_trace_input_and_option_bounds_before_any_json(self):
        base = ["--operation", "trace", "--sample-rate", 48000, "--mode", "vibrato"]
        for payload in (b"", b"\n", b" \n", b"0\n\n", b"# comment\n", b"0\nNaN\n",
                        b"0\n65\n", b"0\n-64.00001\n", b"0\n1x", b"0\x00\n", b"0\n\x1a\n",
                        b"0"*129+b"\n", b"0"*128+b"\r\n"):
            with self.subTest(payload=payload[:30]):
                self.rejected(*base, stdin=payload)
        for factor in (0, 3, 32, -1, "+2", "2.0", "nan"):
            self.rejected(*base, "--subdivisions", factor, stdin=b"0\n")
        for key, value in (("--previous-input", 64.01), ("--previous-input", "nan"),
                           ("--initial-frame", -1), ("--initial-frame", UINT64_MAX+1),
                           ("--capacitor-volts", "0,0"), ("--inductor-amps", "0,0"),
                           ("--capacitor-volts", csv([65536]+[0]*17)),
                           ("--inductor-amps", csv([2, 2]+[0]*16))):
            self.rejected(*base, key, value, stdin=b"0\n")
        exact = self.report("trace", stdin=b"0"*128+b"\n"+b"0"*127+b"\r\n")
        self.assertEqual(len(exact["frames"]), 2)

    @unittest.skipUnless(os.name == "posix" and Path("/dev/full").exists(),
                         "POSIX failing output stream is unavailable")
    def test_output_stream_failure_is_reported(self):
        with open("/dev/full", "wb") as destination:
            result = subprocess.run([str(self.probe), "--operation", "response", "--sample-rate", "48000",
                                     "--mode", "vibrato", "--frequencies", "0"],
                                    stdout=destination, stderr=subprocess.PIPE, check=False, timeout=45)
        self.assertEqual(result.returncode, 1)
        self.assertIn(b"Cannot write JSON report", result.stderr)


if __name__ == "__main__":
    unittest.main()
