#!/usr/bin/env python3
"""Independent native scanner AC/process regression and evidence failure tests."""
from __future__ import annotations

import copy
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
import qualify_scanner_ac as qualification  # noqa: E402

PROFILE = ROOT / "data/scanner/atlas-late-b3-nominal-v1.json"
SMALL_GRID = (20.0, 100.0, 997.0, 5000.0, 7000.0, 20000.0)


class ScannerNativeAC(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get("HAMMOND_SCANNER_LINE_PROBE_EXECUTABLE")
        cls.probe = Path(value).resolve() if value else None
        if cls.probe is None or not cls.probe.is_file():
            raise RuntimeError("Build hammond_scanner_line_probe, then run through CTest; "
                               "HAMMOND_SCANNER_LINE_PROBE_EXECUTABLE is required")
        cls.report = qualification.qualify(cls.probe, multipliers=(1,), frequencies=SMALL_GRID)
        cls.profile_sha = hashlib.sha256(PROFILE.read_bytes()).hexdigest()

    def small_report(self, **kwargs):
        return qualification.qualify(self.probe, host_rates=(48000,), multipliers=(1,),
                                     modes=("chorus",), frequencies=(997.0,), include_process=False, **kwargs)

    def test_frozen_grid_and_contract_are_explicit(self):
        geometric = [round(20 * 1000 ** (j / 120), 12) for j in range(121)]
        geometric[0], geometric[-1] = 20, 20000
        expected = tuple(sorted(set(geometric) | set(range(5000, 9001, 25))))
        self.assertEqual(qualification.frequency_grid(), expected)
        self.assertEqual(len(expected), 282)
        self.assertEqual(self.report["contract_sha256"],
                         "3999a3a409d397401e135e8285704092bad130911468802370bf6da404d58ff9")
        self.assertFalse(self.report["scope"]["stationary_full_contract_grid"])
        self.assertTrue(self.report["source_snapshot_verified_unchanged"])
        self.assertFalse(self.report["scope"]["physical_fidelity_established"])

    def test_warp_matched_three_host_rates_and_exact_dc(self):
        self.assertEqual(self.report["summary"]["G3_stationary_status"], "passed")
        self.assertEqual(len(self.report["stationary_cases"]), 6)
        for case in self.report["stationary_cases"]:
            values = [complex(*value) for value in case["dc"]["native"]]
            if case["mode"] == "vibrato":
                expected_first = Fraction(68, 95)
                expected_return = Fraction(0)
                expected_current = Fraction(9455738267, 92438660160000)
            else:
                expected_first = Fraction(12463311899, 13657495547)
                expected_return = Fraction(9455738267, 13657495547)
                expected_current = Fraction(9455738267, 300464902034000)
            self.assertLess(abs(values[0] - float(expected_first)), 1e-10)
            for value in values[6:19]:
                self.assertLess(abs(value - 1), 1e-10)
            self.assertLess(abs(values[19] - float(expected_return)), 1e-10)
            self.assertLess(abs(values[20] - 15000 * float(expected_current)), 1e-10)
            for row in case["responses"]:
                self.assertFalse(row["G3_warp_matched"]["failed_channels"])
                self.assertLessEqual(max(row["G3_warp_matched"]["error_over_limit"]), 1)
                self.assertLessEqual(row["solve"]["native_normalized_residual"], 1e-9)

    def test_independent_boundary_kcl_and_ideal_first_divider(self):
        # The ideal p0 drive fixes vibrato's first resistive divider at every
        # frequency. Chorus KCL makes input current equal r/22000. These
        # identities do not use the production or reference tap helpers.
        for case in self.report["stationary_cases"]:
            for row in case["responses"]:
                native = [complex(*value) for value in row["native"]]
                r = native[19]
                expected_first = 68 / 95 + (27 / 95) * r
                self.assertLess(abs(native[0] - expected_first), 1e-10)
                if case["mode"] == "vibrato":
                    self.assertEqual(r, 0j)
                else:
                    self.assertLess(abs(native[20] / 15000 - r / 22000), 1e-13)

    def test_same_hertz_failure_is_retained_without_clearing_g3(self):
        summary = self.report["summary"]
        self.assertEqual(summary["G3_stationary_status"], "passed")
        self.assertEqual(summary["G5_same_hertz_status"], "failed")
        self.assertGreater(summary["G5_same_hertz_failed_taps_distinct_rate_cases"], 0)
        for case in self.report["stationary_cases"]:
            self.assertEqual(len(case["responses"]), len(SMALL_GRID))
            self.assertTrue(any(row["G5_same_hertz_taps"]["failed_channels"] for row in case["responses"]))
            self.assertFalse(case["responses"][0]["G5_same_hertz_taps"]["failed_channels"])

    def test_actual_processing_settles_without_phase_or_gain_fit(self):
        self.assertEqual(self.report["summary"]["G3_process_status"], "passed")
        self.assertEqual(self.report["summary"]["process_carrier_cases"], 24)
        for case in self.report["process_cases"]:
            self.assertTrue(case["settled"])
            self.assertEqual(case["status"], "passed")
            self.assertGreaterEqual(len(case["measurements"]), 2)
            self.assertLessEqual(len(case["measurements"]), 4)
            self.assertEqual(case["accepted_measurement_index"], len(case["measurements"]) - 1)
            final = case["measurements"][-1]
            self.assertFalse(final["G3_warp_matched"]["failed_channels"])
            self.assertFalse(final["half_window_convergence"]["failed_channels"])
            self.assertFalse(case["startup_convergence"]["failed_channels"])
            self.assertEqual(len(final["fit_residual_rms"]["taps_volts"]), 19)

    def test_sign_mutation_cannot_pass_the_oracle(self):
        actual_runner = qualification.run_probe

        def reversed_tap(*args, **kwargs):
            record = actual_runner(*args, **kwargs)
            for row in record["responses"]:
                row["taps"][6] = [-value for value in row["taps"][6]]
            return record

        with mock.patch.object(qualification, "run_probe", side_effect=reversed_tap):
            report = self.small_report()
        self.assertEqual(report["summary"]["G3_stationary_status"], "failed")
        self.assertIn("v7", report["stationary_cases"][0]["responses"][0]["G3_warp_matched"]["failed_channels"])
        self.assertEqual(report["summary"]["G3_process_status"], "not_run")

    def test_residual_and_condition_flags_remain_failed_or_inconclusive(self):
        actual_runner = qualification.run_probe
        for field, value, expected in (("normalized_residual", 2e-9, "failed"),
                                       ("condition_inf", 1e15, "inconclusive")):
            def changed_diagnostic(*args, **kwargs):
                record = actual_runner(*args, **kwargs)
                record["responses"][1][field] = value
                return record

            with self.subTest(field=field), mock.patch.object(qualification, "run_probe", side_effect=changed_diagnostic):
                report = self.small_report()
                self.assertEqual(report["summary"]["G3_stationary_status"], expected)
                self.assertNotEqual(report["summary"]["G5_same_hertz_status"], "passed")

    def test_null_phase_gap_is_not_bridged(self):
        frequencies = (100.0, 200.0, 300.0, 400.0, 500.0)
        # Two eligible segments, both crossing principal phase boundaries, with
        # a gap between them. Independent segment origins must remain intact.
        values = [complex(math.cos(p), math.sin(p)) for p in (3.0, -3.0, 0.0, -2.9, 2.9)]
        values[2] = 1e-5 + 0j
        native = [tuple(value for _ in range(19)) for value in values]
        phases = qualification.phase_diagnostics(frequencies, native, native)
        for row in phases:
            self.assertEqual(row["native_phase_rad"][0], 3.0)
            self.assertAlmostEqual(row["native_phase_rad"][1], math.tau - 3.0)
            self.assertIsNone(row["native_phase_rad"][2])
            self.assertIsNone(row["native_group_delay_s"][2])
            self.assertAlmostEqual(row["native_phase_rad"][3], -2.9)
            self.assertAlmostEqual(row["native_phase_rad"][4], 2.9 - math.tau)
            self.assertEqual(len(row["exclusions"]), 1)
            self.assertLess(row["native_group_delay_s"][0], 0)
            self.assertGreater(row["native_group_delay_s"][3], 0)

    def test_probe_identity_shape_clock_and_nonfinite_rejection(self):
        valid = qualification.run_probe(self.probe, "response", 48000, "chorus",
                                        ["--frequencies", "997"], self.profile_sha)
        invalid_records = []
        for field, value in (("mode", "vibrato"), ("sample_rate_hz", 44100), ("authoring_sha256", "0" * 64),
                             ("clock_convention", "first sample at t=1"), ("operation", "sine"),
                             ("measurement_method", "actual_process_frame_endpoint_trace"),
                             ("preparation_residual", 1e-5)):
            bad = copy.deepcopy(valid)
            bad[field] = value
            invalid_records.append(bad)
        for record in invalid_records:
            result = subprocess.CompletedProcess([], 0, json.dumps(record).encode(), b"")
            with mock.patch.object(qualification.subprocess, "run", return_value=result):
                with self.assertRaises(qualification.QualificationError):
                    qualification.run_probe(self.probe, "response", 48000, "chorus", [], self.profile_sha)
        with self.assertRaises(qualification.QualificationError):
            qualification._vectors({"taps": [[0, 0]] * 18})
        for bad in (float("nan"), float("inf"), True):
            record = copy.deepcopy(valid["responses"][0])
            record["taps"][0][1] = bad
            with self.assertRaises(qualification.QualificationError):
                qualification._vectors(record)
        for payload in (b'{"x":1,"x":2}', b'{"x":NaN}', b'[]'):
            with mock.patch.object(qualification.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, payload, b"")):
                with self.assertRaises(qualification.QualificationError):
                    qualification.run_probe(self.probe, "response", 48000, "chorus", [], self.profile_sha)

    def test_input_mutation_during_qualification_rejects_the_result(self):
        actual_snapshot = qualification.source_snapshot(ROOT, PROFILE, self.probe)
        changed = copy.deepcopy(actual_snapshot)
        changed["files_sha256"]["src/ScannerLine.cpp"] = "0" * 64
        with mock.patch.object(qualification, "source_snapshot", side_effect=[actual_snapshot, changed]):
            with self.assertRaisesRegex(qualification.QualificationError, "changed during"):
                self.small_report()

    def test_output_is_atomic_and_protects_sources_aliases_and_old_report(self):
        with tempfile.TemporaryDirectory(prefix="scanner AC output ") as temporary:
            work = Path(temporary)
            output = work / "result.json"
            output.write_bytes(b"old report\n")
            before = output.read_bytes()
            for report in ({"bad": float("nan")}, {"bad": object()}):
                with self.assertRaises(qualification.QualificationError):
                    qualification.write_report(output, report)
                self.assertEqual(output.read_bytes(), before)
            with mock.patch.object(qualification.os, "replace", side_effect=OSError("injected failure")):
                with self.assertRaises(OSError):
                    qualification.write_report(output, {"complete": True})
            self.assertEqual(output.read_bytes(), before)
            self.assertEqual(sorted(path.name for path in work.iterdir()), ["result.json"])
            with self.assertRaises(qualification.QualificationError):
                qualification.write_report(output, {}, protected=(output,))
            alias = work / "alias.json"
            os.link(output, alias)
            with self.assertRaises(qualification.QualificationError):
                qualification.write_report(alias, {}, protected=(output,))
            self.assertEqual(output.read_bytes(), before)
            with self.assertRaises(qualification.QualificationError):
                qualification.write_report(work, {})
            qualification.write_report(output, {"complete": True})
            self.assertEqual(json.loads(output.read_text()), {"complete": True})

    def test_invalid_cli_preserves_existing_destination(self):
        with tempfile.TemporaryDirectory(prefix="scanner AC CLI ") as temporary:
            output = Path(temporary) / "existing.json"
            output.write_bytes(b"keep me\n")
            result = subprocess.run([sys.executable, str(ROOT / "tools/qualify_scanner_ac.py"),
                                     "--probe", str(self.probe), "--host-rates", "48001",
                                     "--output", str(output)], capture_output=True, timeout=30, check=False)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(output.read_bytes(), b"keep me\n")
            self.assertIn(b"unsupported host rates", result.stderr)

    def test_rejects_invalid_grid_selection_without_silent_sorting(self):
        for frequencies in ((), (997.0, 100.0), (997.0, 997.0), (True,), (float("nan"),), (20001.0,)):
            with self.subTest(frequencies=frequencies), self.assertRaises(qualification.QualificationError):
                qualification.qualify(self.probe, frequencies=frequencies, include_process=False)
        for kwargs in ({"host_rates": (48000, 48000)}, {"multipliers": (3,)},
                       {"modes": ("Chorus",)}, {"include_process": 1}):
            with self.subTest(kwargs=kwargs), self.assertRaises(qualification.QualificationError):
                qualification.qualify(self.probe, frequencies=(997.0,), **kwargs)


if __name__ == "__main__":
    unittest.main()
