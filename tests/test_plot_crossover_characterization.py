#!/usr/bin/env python3
"""Admission regressions using retained evidence, without native sweeps or plots."""

from __future__ import annotations

import contextlib
import copy
import io
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import plot_crossover_characterization as plotter


class CrossoverPlotAdmission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.retained = json.loads(plotter.DEFAULT_REPORT.read_text(encoding="utf-8"))

    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="crossover-plot-admission-")
        self.addCleanup(directory.cleanup)
        self.directory = Path(directory.name)
        self.report_path = self.directory / "report.json"

    def write(self, report):
        self.report_path.write_text(json.dumps(report, allow_nan=False), encoding="utf-8")
        return self.report_path

    def reject(self, change):
        report = copy.deepcopy(self.retained)
        change(report)
        with self.assertRaises(ValueError):
            plotter.observations(self.write(report))

    def test_retained_report_and_reordered_complete_experiments_are_admitted(self):
        for reorder in (False, True):
            with self.subTest(reorder=reorder):
                report = copy.deepcopy(self.retained)
                if reorder:
                    report["response_groups"].reverse()
                    report["sine_groups"].reverse()
                selected, metadata = plotter.observations(self.write(report))
                self.assertEqual(set(selected), {44100, 48000, 96000, 192000})
                self.assertEqual(sum(map(len, selected.values())), 24)
                self.assertEqual(metadata["binary_sha256"], self.retained["binary_sha256"])
                self.assertEqual(metadata["source_sha256"], self.retained["source_sha256"])
                self.assertEqual(metadata["acceptance_report_sha256"], plotter.digest(self.report_path))
                bass = selected[44100][-1]["ports"]["bass_gain"]
                self.assertAlmostEqual(bass["absolute_complex_error"], 0.0009316571096197035)
                treble = selected[44100][-1]["ports"]["treble_gain"]
                self.assertGreater(treble["absolute_complex_error"], treble["normalized_complex_error"])

    def test_original_missing_sources_null_binary_and_over_budget_regressions(self):
        changes = (
            lambda r: r.update(source_sha256={key: value for key, value in r["source_sha256"].items()
                                              if key in ("tools/crossover_reference.py",
                                                         "data/crossover/leslie-122-ideal-v1.json")}),
            lambda r: r.update(binary_sha256=None),
            lambda r: r.update(maximum_warped_response_error=1.0),
        )
        for index, change in enumerate(changes):
            with self.subTest(original_mutation=index):
                self.reject(change)

    def test_source_set_and_hashes_cannot_be_omitted_extended_or_stale(self):
        for name in self.retained["source_sha256"]:
            with self.subTest(missing=name):
                self.reject(lambda r: r["source_sha256"].pop(name))
            with self.subTest(stale=name):
                self.reject(lambda r: r["source_sha256"].update({name: "0" * 64}))
        for name in ("README.md", "../outside", "/absolute"):
            with self.subTest(extra=name):
                self.reject(lambda r: r["source_sha256"].update({name: "0" * 64}))
        for bad in (None, True, 123, "", "a" * 63, "a" * 65, "A" * 64, "z" * 64):
            with self.subTest(binary=bad):
                self.reject(lambda r: r.update(binary_sha256=bad))

    def test_success_and_research_claims_require_strict_types(self):
        for name, bad in (("schema_version", True), ("schema_version", 1.0),
                          ("passed", 1), ("passed", False), ("failures", 1),
                          ("failures", False), ("errors", -1), ("errors", False),
                          ("tests_run", 0), ("tests_run", 3.0),
                          ("engine_integration", 0), ("physical_measurement_claim", True),
                          ("same_hz_status", "accepted"), ("provenance_boundary", "authenticated"),
                          ("platform", None), ("python", "")):
            with self.subTest(field=name, value=bad):
                self.reject(lambda r: r.update({name: bad}))

    def test_limits_are_frozen_and_summaries_match_the_group_maxima(self):
        for name in ("warped_response", "settled_sine"):
            with self.subTest(limit=name):
                self.reject(lambda r: r["limits"].update({name: r["limits"][name] * 2}))
        summaries = ("maximum_warped_response_error", "maximum_warped_sine_error",
                     "maximum_independent_sine_tail_gain_bound", "maximum_half_window_gain_difference")
        for name in summaries:
            with self.subTest(summary=name):
                self.reject(lambda r: r.update({name: r[name] / 2.0}))
        for name, bad in (("maximum_response_residual", 1.01e-12),
                          ("maximum_warped_response_error", -1.0),
                          ("maximum_warped_sine_error", True)):
            with self.subTest(field=name):
                self.reject(lambda r: r.update({name: bad}))
        self.reject(lambda r: r["response_groups"][1]["maximum_warped_normalized_errors"].update(
            treble_gain=math.nextafter(2.0e-10, math.inf)))
        self.reject(lambda r: r["sine_groups"][1].update(
            maximum_warped_normalized_error=math.nextafter(2.0e-8, math.inf)))

    def test_exact_error_budgets_are_inclusive_without_relaxing_them(self):
        report = copy.deepcopy(self.retained)
        report["maximum_warped_response_error"] = 2.0e-10
        report["response_groups"][0]["maximum_warped_normalized_errors"]["treble_gain"] = 2.0e-10
        report["maximum_response_residual"] = 1.0e-12
        for summary, field, limit in (
                ("maximum_warped_sine_error", "maximum_warped_normalized_error", 2.0e-8),
                ("maximum_independent_sine_tail_gain_bound", "independent_all_fit_tail_bound", 2.0e-10),
                ("maximum_half_window_gain_difference", "half_window_max_difference", 2.0e-8)):
            report[summary] = limit
            report["sine_groups"][0][field] = limit
        selected, _ = plotter.observations(self.write(report))
        self.assertEqual(sum(map(len, selected.values())), 24)

    def test_experiment_family_and_counts_must_be_complete(self):
        changes = (
            lambda r: r["response_groups"].pop(),
            lambda r: r["response_groups"].__setitem__(1, copy.deepcopy(r["response_groups"][0])),
            lambda r: r["response_groups"][0].update(sample_rate_hz=176400),
            lambda r: r["response_groups"][0].update(treble_ohms=True),
            lambda r: r["response_groups"][0].update(bass_ohms=1),
            lambda r: r["response_groups"][0].update(frequencies=130.0),
            lambda r: r["sine_groups"].pop(),
            lambda r: r["sine_groups"].__setitem__(1, copy.deepcopy(r["sine_groups"][0])),
            lambda r: r["sine_groups"][0].update(frequency_hz=0),
            lambda r: r["sine_groups"][0].update(sample_rate_hz=44100.0),
        )
        for index, change in enumerate(changes):
            with self.subTest(group_mutation=index):
                self.reject(change)
        for name, value in (("response_port_comparisons", 9361), ("sine_port_comparisons", 863),
                            ("subprocesses", 152), ("response_port_comparisons", 9360.0)):
            with self.subTest(count=name):
                self.reject(lambda r: r.update({name: value}))

    def test_sine_decay_and_warmup_must_be_bounded(self):
        for field, value in (("independent_largest_pole_modulus", 0.0),
                             ("independent_largest_pole_modulus", 1.0),
                             ("warmup_frames", True), ("warmup_frames", -1),
                             ("warmup_frames", 2_000_001),
                             ("independent_all_fit_tail_bound", 2.01e-10),
                             ("half_window_max_difference", 2.01e-8)):
            with self.subTest(field=field, value=value):
                self.reject(lambda r: r["sine_groups"][0].update({field: value}))

    def test_nominal_metrics_must_match_shapes_maxima_and_complex_error(self):
        changes = (
            lambda r: r["response_groups"][0]["nominal_same_hz_points"].pop(),
            lambda r: r["response_groups"][1]["nominal_same_hz_points"].append(
                copy.deepcopy(r["response_groups"][0]["nominal_same_hz_points"][0])),
            lambda r: r["response_groups"][0]["nominal_same_hz_points"][0].update(frequency_hz=401),
            lambda r: r["response_groups"][0]["nominal_same_hz_points"][0]["same_hz_errors"].pop("bass_gain"),
            lambda r: r["response_groups"][0]["nominal_same_hz_points"][0]["same_hz_errors"]["bass_gain"].update(
                normalized_complex_error=-1.0),
            lambda r: r["response_groups"][0]["nominal_same_hz_points"][0]["same_hz_errors"]["bass_gain"].update(
                magnitude_error_db=0.1),
            lambda r: r["response_groups"][0]["same_hz_10_to_20000_maximum_absolute_errors"]["bass_gain"].update(
                magnitude_error_db=0.0),
            lambda r: r["response_groups"][0]["nominal_same_hz_points"][0]["same_hz_errors"]["bass_gain"].update(
                phase_error_degrees=181),
        )
        for index, change in enumerate(changes):
            with self.subTest(metric_mutation=index):
                self.reject(change)

    def test_malformed_json_and_nonfinite_values_are_rejected(self):
        text = json.dumps(self.retained)
        for raw in ("[]", "null", "{", '["nested"]',
                    text.replace('"schema_version": 1', '"schema_version": 1, "schema_version": 1', 1),
                    text.replace('"maximum_response_residual": 1.7554167342883506e-16',
                                 '"maximum_response_residual": 1e999', 1),
                    text.replace('"maximum_response_residual": 1.7554167342883506e-16',
                                 '"maximum_response_residual": NaN', 1)):
            with self.subTest(raw=raw[:70]):
                self.report_path.write_text(raw, encoding="utf-8")
                with self.assertRaises(ValueError):
                    plotter.observations(self.report_path)
        self.reject(lambda r: r.update(unknown_field=1))
        self.reject(lambda r: r.pop("maximum_response_residual"))
        self.report_path.write_bytes(b" " * (1024 * 1024 + 1))
        with self.assertRaisesRegex(ValueError, "1 MiB"):
            plotter.observations(self.report_path)

    def test_cli_refusals_precede_plotting_and_preserve_existing_output(self):
        for existing in (False, True):
            with self.subTest(existing=existing):
                report = copy.deepcopy(self.retained)
                report["binary_sha256"] = None
                output = self.directory / "figure.png"
                if existing:
                    output.write_bytes(b"existing output sentinel")
                args = ["plot_crossover_characterization.py", "--acceptance-report", str(self.write(report)),
                        "--output", str(output)]
                stdout, stderr = io.StringIO(), io.StringIO()
                with mock.patch.object(sys, "argv", args), mock.patch.object(plotter, "plot") as render:
                    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                        self.assertEqual(plotter.main(), 2)
                    render.assert_not_called()
                self.assertEqual(stdout.getvalue(), "")
                self.assertTrue(stderr.getvalue().startswith("plot_crossover_characterization: "))
                if existing:
                    self.assertEqual(output.read_bytes(), b"existing output sentinel")
                else:
                    self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
