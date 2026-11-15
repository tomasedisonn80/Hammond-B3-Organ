#!/usr/bin/env python3
"""Admission/resource/publication checks without running the full study."""

from __future__ import annotations

from dataclasses import replace
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import contact_switching_study as study


class StudyAdmission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures = ROOT / "data/contact-switching/reference-v1"
        cls.admission = study.admit_inputs(cls.fixtures)

    def test_fixed_matrix_and_work_admission(self):
        self.assertEqual(len(self.admission.fixtures), 36)
        self.assertEqual(self.admission.fir_products, 159_847_056)
        for fixture in self.admission.fixtures:
            self.assertEqual(len(fixture.indices), 64)
            self.assertEqual(len(set(fixture.indices)), 64)
            self.assertEqual(fixture.document.case.frames, 256)

    def test_modified_missing_or_reselected_fixtures_reject_before_render(self):
        with tempfile.TemporaryDirectory() as temporary:
            copied = Path(temporary) / "fixtures"
            shutil.copytree(self.fixtures, copied)
            first = copied / "F00-44100-v1.json"
            original = first.read_bytes()
            with patch.object(study.candidate, "render", side_effect=AssertionError("must not render")):
                first.write_bytes(original + b" ")
                with self.assertRaisesRegex(ValueError, "frozen fixture differs"):
                    study.admit_inputs(copied)
                first.unlink()
                with self.assertRaises(OSError):
                    study.admit_inputs(copied)
                first.write_bytes(original)
                probes = copied / "probes.json"
                value = json.loads(probes.read_text())
                value["fixtures"][first.name]["indices"][0] = 2
                probes.write_text(json.dumps(value))
                with self.assertRaisesRegex(ValueError, "frozen probes.json differs"):
                    study.admit_inputs(copied)

    def test_new_output_path_is_required_and_inputs_cannot_alias(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            destination = directory / "result.json"
            plans = study.preflight_output(self.admission, destination)
            self.assertFalse(destination.exists())
            self.assertEqual(len(plans), len(self.admission.paths))
            destination.write_bytes(b"previous experiment")
            with self.assertRaisesRegex(ValueError, "already exists"):
                study.preflight_output(self.admission, destination)
            self.assertEqual(destination.read_bytes(), b"previous experiment")
            with self.assertRaises(ValueError):
                study.preflight_output(self.admission, self.fixtures / "manifest.json")
            with self.assertRaises(OSError):
                study.preflight_output(self.admission, directory / "missing" / "result.json")
            with self.assertRaises(ValueError):
                study.preflight_output(self.admission, str(directory) + os.sep)

    def test_alias_and_special_leaf_preservation(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            copied = directory / "fixtures"
            shutil.copytree(self.fixtures, copied)
            admission = study.admit_inputs(copied)
            alias = directory / "alias.json"
            try:
                os.link(copied / "manifest.json", alias)
            except OSError:
                self.skipTest("hardlink creation unavailable on this filesystem")
            with self.assertRaises(ValueError):
                study.preflight_output(admission, alias)
            self.assertEqual(alias.read_bytes(), (copied / "manifest.json").read_bytes())
            alias.unlink()
            try:
                alias.symlink_to(directory / "absent")
            except OSError:
                return  # Hardlink coverage executed; symlink facility is optional.
            with self.assertRaises(ValueError):
                study.preflight_output(admission, alias)
            self.assertTrue(alias.is_symlink())
            alias.unlink()
            if hasattr(os, "mkfifo"):
                os.mkfifo(alias)
                with self.assertRaises(ValueError):
                    study.preflight_output(admission, alias)

    def test_atomic_fsync_link_failure_and_concurrent_destination(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            destination = directory / "report.json"
            plans = study.preflight_output(self.admission, destination)
            for operation in ("fsync", "link"):
                with self.subTest(operation=operation), patch.object(study.os, operation, side_effect=OSError("injected")):
                    with self.assertRaises(OSError):
                        study.atomic_publish(self.admission, plans, b'{"status":"incomplete"}\n')
                self.assertFalse(destination.exists())
                self.assertEqual(list(directory.iterdir()), [])
            destination.write_bytes(b"concurrent report")
            with self.assertRaises(ValueError):
                study.atomic_publish(self.admission, plans, b"{}\n")
            self.assertEqual(destination.read_bytes(), b"concurrent report")
            self.assertEqual(list(directory.iterdir()), [destination])

    def test_last_moment_concurrent_report_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            destination = directory / "report.json"
            plans = study.preflight_output(self.admission, destination)
            original_link = os.link

            def competing_publication(source, target):
                destination.write_bytes(b"concurrent earlier experiment")
                return original_link(source, target)

            with patch.object(study.os, "link", side_effect=competing_publication):
                with self.assertRaises(FileExistsError):
                    study.atomic_publish(self.admission, plans, b'{"status":"passed"}\n')
            self.assertEqual(destination.read_bytes(), b"concurrent earlier experiment")
            self.assertEqual(list(directory.iterdir()), [destination])

    def test_atomic_fresh_publication_removes_owned_temporary_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            destination = directory / "report.json"
            plans = study.preflight_output(self.admission, destination)
            payload = b'{"status":"incomplete"}\n'
            study.atomic_publish(self.admission, plans, payload)
            self.assertEqual(destination.read_bytes(), payload)
            self.assertEqual(list(directory.iterdir()), [destination])

    def test_input_replacement_after_admission_does_not_publish(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            copied = directory / "fixtures"
            shutil.copytree(self.fixtures, copied)
            admission = study.admit_inputs(copied)
            destination = directory / "report.json"
            plans = study.preflight_output(admission, destination)
            source = copied / "F03-48000-v1.json"
            source.write_bytes(source.read_bytes() + b" ")
            with self.assertRaises(ValueError):
                study.atomic_publish(admission, plans, b"{}\n")
            self.assertFalse(destination.exists())
            self.assertFalse(list(directory.glob(".contact-study-*")))

    def test_real_cli_refuses_existing_report_and_duplicate_options(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "preserved.json"
            output.write_bytes(b"retain original evidence")
            command = [sys.executable, "-B", str(ROOT / "tools/contact_switching_study.py"),
                       "--fixtures", str(self.fixtures), "--output", str(output)]
            for extra in ([], ["--output", str(output)], ["--factor", "256"]):
                with self.subTest(extra=extra):
                    result = subprocess.run(command + extra, capture_output=True, timeout=10)
                    self.assertEqual(result.returncode, 2)
                    self.assertEqual(result.stdout, b"")
                    self.assertLess(len(result.stderr), 850)
                    self.assertEqual(output.read_bytes(), b"retain original evidence")

    def test_scaled_metrics_keep_subnormal_and_ineligible_distinct(self):
        tiny = math.nextafter(0.0, 1.0)
        exact = study.metrics((tiny,), (tiny,), tiny)
        self.assertEqual(exact["status"], "eligible")
        self.assertEqual(exact["normalized_reference_rms"], 1.0)
        self.assertEqual(exact["nrmse"], 0.0)
        value = study.metrics((1e-10,), (2e-10,), 1.0)
        decision = study.grade(value, study.LIMITS["oracle_refinement"])
        self.assertEqual(value["status"], "absolute_only")
        self.assertIsNone(value["nrmse"])
        self.assertIsNone(decision["nrmse_pass"])
        self.assertEqual(decision["status"], "pass_absolute_only")
        wrong = study.metrics((0.0,), (tiny,), 0.0)
        self.assertFalse(study.grade(wrong, study.LIMITS["oracle_refinement"])["accepted"])
        with self.assertRaises(ValueError):
            study.metrics((0.0,), (float("nan"),), 1.0)

    def test_full_output_residual_dft_retains_signed_definition_and_bands(self):
        low = (0.0,) * 8
        high = (1.0, -1.0) * 4
        value = study.residual_dft(low, high, 0)
        self.assertEqual(value["time_domain_energy"], 8.0)
        self.assertEqual(value["tail_energy"], 8.0)
        self.assertAlmostEqual(value["dft_energy"], 8.0, places=12)
        self.assertAlmostEqual(value["bands"][2]["energy"], 8.0, places=12)
        self.assertLess(value["bands"][0]["energy"], 1e-25)
        self.assertIn("L256 minus L128", value["definition"])

    def test_bounded_zero_fixture_facts_and_ranges_smoke(self):
        fixture = self.admission.fixtures[0]
        rendered = study.candidate.render(fixture.document.case, 32)
        self.assertTrue(study.facts_check(fixture, rendered)["accepted"])
        self.assertTrue(study.range_check(rendered)["accepted"])
        self.assertEqual(rendered.samples, (0.0,) * 289)

    def test_resource_stop_is_incomplete_not_a_pass(self):
        started = time.perf_counter() - 301
        with patch.object(study.candidate, "render", side_effect=AssertionError("must not render")):
            report = study.run_study(self.admission, started=started)
        payload = study.encode_report(report, started)
        retained = json.loads(payload)
        self.assertEqual(retained["status"], "incomplete")
        self.assertEqual(retained["observations"]["completed_render_count"], 0)
        self.assertEqual(retained["observations"]["report_bytes"], len(payload))
        self.assertIn("elapsed", retained["incomplete_reason"])
        with patch.object(study, "_resident", return_value=(None, "unavailable", "test unavailable")):
            unavailable = study.encode_report(report, time.perf_counter())
        self.assertEqual(json.loads(unavailable)["status"], "incomplete")
        with patch.object(study, "_resident", return_value=(257 * 1024 * 1024, "test", None)):
            with self.assertRaises(study.Incomplete):
                study._guard(time.perf_counter())

    def test_deadline_crossed_inside_final_encoding_cannot_return_a_pass(self):
        # Complete-counter metadata is a small transport fixture, not numerical
        # evidence. The clock crosses 300 only after json.dumps has returned.
        report = {"status": "incomplete", "incomplete_reason": None, "failed_cells": [],
                  "finished_utc": None, "observations": {"completed_fixture_count": 36,
                      "completed_render_count": 144, "report_bytes": 0}}
        calls = iter((299.0, 299.0, 301.0))
        with patch.object(study.time, "perf_counter", side_effect=lambda: next(calls, 301.0)), \
                patch.object(study, "_resident", return_value=(24 * 1024 * 1024, "test", None)):
            payload = study.encode_report(report, 0.0)
        retained = json.loads(payload)
        self.assertEqual(retained["status"], "incomplete")
        self.assertIn("during final report encoding", retained["incomplete_reason"])
        self.assertEqual(retained["observations"]["resource_gate_status"], "incomplete")
        self.assertEqual(retained["observations"]["elapsed_seconds"], 301.0)
        self.assertEqual(retained["observations"]["report_bytes"], len(payload))


if __name__ == "__main__":
    unittest.main()
