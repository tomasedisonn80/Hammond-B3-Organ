#!/usr/bin/env python3
"""Independent acceptance of the frozen capture-comparison-v1 metric contract.

Expected values come from literal algebra, exact rational sums and separately
expressed complex-exponential sums. Producer helpers are never numerical oracles.
Policy evaluation and maximum-work performance are separate acceptance scopes.
"""

from __future__ import annotations

import cmath
import copy
from decimal import Decimal
from fractions import Fraction
import json
import math
from pathlib import Path
import sys
import unittest
from unittest import mock

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import compare_capture as subject


ABS_TOL = 2e-13
REL_TOL = 2e-13
POINT_UNITS = {
    "reference_dc_fs": "FS", "candidate_dc_fs": "FS", "dc_bias_fs": "FS",
    "absolute_dc_bias_fs": "FS", "reference_rms_fs": "FS",
    "candidate_rms_fs": "FS", "rms_error_fs": "FS", "max_abs_error_fs": "FS",
    "normalized_rms_error": "ratio", "signal_to_error_db": "dB",
}
FREQUENCY_UNITS = {
    "reference_magnitude_fs": "FS", "candidate_magnitude_fs": "FS",
    "complex_abs_error_fs": "FS", "normalized_complex_error": "ratio",
    "reference_phase_rad": "rad", "candidate_phase_rad": "rad",
    "phase_error_rad": "rad", "absolute_phase_error_rad": "rad",
}


def known(value, unit):
    return {"value": value, "unit": unit, "undefined_reason": None}


def absent(reason, unit):
    return {"value": None, "unit": unit, "undefined_reason": reason}


def coefficient_oracle(samples, frequency, rate, weights=None):
    """Short-vector complex exponential oracle with separate summation order."""
    if weights is None:
        weights = [1] * len(samples)
    total = sum(weight * sample * cmath.exp(-2j * math.pi * frequency * n / rate)
                for n, (weight, sample) in enumerate(zip(weights, samples)))
    return total / sum(weights)


def literal_report():
    """A fully hand-specified section-5 report; never calls the producer."""
    return {
        "schema_version": 1,
        "metric_contract": "capture-comparison-v1",
        "sample_rate_hz": 4,
        "channel_count": 1,
        "frame_count": 4,
        "analysis": {
            "pairing": "index", "frame_start": 0, "frame_stop": 4,
            "window": "rectangular", "floor_fs": 1e-12,
            "frequencies_hz": [1], "dft_normalization": "weighted_mean",
            "transform": "none",
        },
        "channels": [{
            "reference_channel_index": 0, "candidate_channel_index": 0,
            "metrics": {
                "reference_dc_fs": known(0.0, "FS"),
                "candidate_dc_fs": known(0.0, "FS"),
                "dc_bias_fs": known(0.0, "FS"),
                "absolute_dc_bias_fs": known(0.0, "FS"),
                "reference_rms_fs": known(math.sqrt(0.5), "FS"),
                "candidate_rms_fs": known(math.sqrt(0.5), "FS"),
                "rms_error_fs": known(1.0, "FS"),
                "max_abs_error_fs": known(1.0, "FS"),
                "normalized_rms_error": known(math.sqrt(2), "ratio"),
                "signal_to_error_db": known(-10 * math.log10(2), "dB"),
            },
            "frequencies": [{
                "frequency_hz": 1,
                "reference_coefficient": {"real_fs": 0.0, "imag_fs": -0.5},
                "candidate_coefficient": {"real_fs": 0.5, "imag_fs": 0.0},
                "metrics": {
                    "reference_magnitude_fs": known(0.5, "FS"),
                    "candidate_magnitude_fs": known(0.5, "FS"),
                    "complex_abs_error_fs": known(math.sqrt(0.5), "FS"),
                    "normalized_complex_error": known(math.sqrt(2), "ratio"),
                    "reference_phase_rad": known(-math.pi / 2, "rad"),
                    "candidate_phase_rad": known(0.0, "rad"),
                    "phase_error_rad": known(math.pi / 2, "rad"),
                    "absolute_phase_error_rad": known(math.pi / 2, "rad"),
                },
                "phase_mask": "none",
            }],
        }],
        "physical_fidelity": "not_established",
    }


def silent_literal_report():
    report = literal_report()
    point = report["channels"][0]["metrics"]
    for key, unit in POINT_UNITS.items():
        point[key] = (absent("reference_at_or_below_floor", unit)
                      if key in ("normalized_rms_error", "signal_to_error_db")
                      else known(0.0, unit))
    row = report["channels"][0]["frequencies"][0]
    row["reference_coefficient"] = {"real_fs": 0.0, "imag_fs": 0.0}
    row["candidate_coefficient"] = {"real_fs": 0.0, "imag_fs": 0.0}
    row["metrics"] = {
        "reference_magnitude_fs": known(0.0, "FS"),
        "candidate_magnitude_fs": known(0.0, "FS"),
        "complex_abs_error_fs": known(0.0, "FS"),
        "normalized_complex_error": absent("reference_at_or_below_floor", "ratio"),
        "reference_phase_rad": absent("reference_at_or_below_floor", "rad"),
        "candidate_phase_rad": absent("candidate_at_or_below_floor", "rad"),
        "phase_error_rad": absent("both_at_or_below_floor", "rad"),
        "absolute_phase_error_rad": absent("both_at_or_below_floor", "rad"),
    }
    row["phase_mask"] = "both_at_or_below_floor"
    return report


class MetricCase(unittest.TestCase):
    def close(self, observed, expected, *, absolute=ABS_TOL, relative=REL_TOL):
        self.assertIn(type(observed), (int, float))
        self.assertTrue(math.isfinite(observed))
        self.assertTrue(math.isclose(observed, expected, abs_tol=absolute,
                                     rel_tol=relative), (observed, expected))

    def metric(self, actual, value, unit, reason=None):
        self.assertEqual(set(actual), {"value", "unit", "undefined_reason"})
        self.assertEqual(actual["unit"], unit)
        self.assertEqual(actual["undefined_reason"], reason)
        if value is None:
            self.assertIsNone(actual["value"])
        else:
            self.close(actual["value"], value)

    def rejection(self, *args, **kwargs):
        with self.assertRaises(subject.ComparisonError):
            subject.compare_signals(*args, **kwargs)

    def reject_report(self, report):
        with self.assertRaises(subject.ComparisonError):
            subject.validate_comparison_report(report)


class PointwiseAcceptance(MetricCase):
    def test_nine_literal_contract_vectors(self):
        # Columns are the exact ten section-3 entries in their contract order.
        cases = [
            ("silence", [0, 0, 0, 0], [0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, None, None], "reference_at_or_below_floor"),
            ("silent_reference", [0, 0, 0, 0], [1, 1, 1, 1],
             [0, 1, 1, 1, 0, 1, 1, 1, None, None], "reference_at_or_below_floor"),
            ("identical", [1, -1, 1, -1], [1, -1, 1, -1],
             [0, 0, 0, 0, 1, 1, 0, 0, 0, None], "zero_error"),
            ("muted", [1, -1, 1, -1], [0, 0, 0, 0],
             [0, 0, 0, 0, 1, 0, 1, 1, 1, 0], None),
            ("gain_two", [1, -1, 1, -1], [2, -2, 2, -2],
             [0, 0, 0, 0, 1, 2, 1, 1, 1, 0], None),
            ("quarter_bias", [1, -1, 1, -1], [1.25, -0.75, 1.25, -0.75],
             [0, 0.25, 0.25, 0.25, 1, math.sqrt(17)/4, 0.25, 0.25,
              0.25, 20*math.log10(4)], None),
            ("polarity", [1, -1, 1, -1], [-1, 1, -1, 1],
             [0, 0, 0, 0, 1, 1, 2, 2, 2, 20*math.log10(0.5)], None),
            ("one_frame_delay", [1, 0, 0, 0], [0, 1, 0, 0],
             [0.25, 0.25, 0, 0, 0.5, 0.5, 1/math.sqrt(2), 1,
              math.sqrt(2), -10*math.log10(2)], None),
            ("quadrature", [0, 1, 0, -1], [1, 0, -1, 0],
             [0, 0, 0, 0, math.sqrt(0.5), math.sqrt(0.5), 1, 1,
              math.sqrt(2), -10*math.log10(2)], None),
        ]
        for name, reference, candidate, expected, db_reason in cases:
            with self.subTest(name=name):
                report = subject.compare_signals([reference], [candidate], 4)
                metrics = report["channels"][0]["metrics"]
                self.assertEqual(set(metrics), set(POINT_UNITS))
                for (key, unit), value in zip(POINT_UNITS.items(), expected):
                    reason = ("reference_at_or_below_floor"
                              if key == "normalized_rms_error" and value is None
                              else db_reason if key == "signal_to_error_db" else None)
                    self.metric(metrics[key], value, unit, reason)
                    if value is not None and (value == 0 or key in (
                            "reference_dc_fs", "candidate_dc_fs", "dc_bias_fs",
                            "absolute_dc_bias_fs", "max_abs_error_fs")):
                        # These literal cases use exactly representable sums
                        # and differences; transcendental allowances do not
                        # relax their exact algebra or any exact zero.
                        self.assertEqual(metrics[key]["value"], value)

    def test_negative_dc_and_rms_include_constant_level(self):
        point = subject.compare_signals([[-3, -3, -3]], [[-5, -5, -5]], 7)["channels"][0]["metrics"]
        for key, value in {"reference_dc_fs": -3, "candidate_dc_fs": -5,
                           "dc_bias_fs": -2, "absolute_dc_bias_fs": 2,
                           "reference_rms_fs": 3, "candidate_rms_fs": 5,
                           "rms_error_fs": 2, "normalized_rms_error": 2/3}.items():
            self.metric(point[key], value, POINT_UNITS[key])

    def test_pairing_preserves_two_channel_order_and_bias_sign(self):
        report = subject.compare_signals([[1, 1], [4, 4]], [[3, 3], [1, 1]], 48000)
        self.assertEqual(report["channel_count"], 2)
        for index, bias in enumerate((2, -3)):
            row = report["channels"][index]
            self.assertEqual((row["reference_channel_index"], row["candidate_channel_index"]), (index, index))
            self.metric(row["metrics"]["dc_bias_fs"], bias, "FS")
            self.metric(row["metrics"]["absolute_dc_bias_fs"], abs(bias), "FS")

    def test_preserves_every_supplied_frame_including_edges(self):
        report = subject.compare_signals([[0] * 9], [[1] + [0] * 7 + [-1]], 9)
        point = report["channels"][0]["metrics"]
        self.metric(point["rms_error_fs"], math.sqrt(2)/3, "FS")
        self.metric(point["max_abs_error_fs"], 1, "FS")
        self.assertEqual(report["analysis"]["frame_start"], 0)
        self.assertEqual(report["analysis"]["frame_stop"], 9)

    def test_pointwise_values_do_not_depend_on_spectral_window(self):
        ref, cand = [[7, 1, -3, 4, 9]], [[-7, 2, -2, 3, -9]]
        reports = [subject.compare_signals(ref, cand, 12, frequencies_hz=[0, 1.5, 6], window=window)
                   for window in ("rectangular", "hann_symmetric")]
        self.assertEqual(reports[0]["channels"][0]["metrics"], reports[1]["channels"][0]["metrics"])

    def test_compensated_dc_against_exact_stored_float_rational_sum(self):
        samples = [1e6, 1e-11, -1e6]
        exact_dc = float(sum(map(Fraction.from_float, samples), Fraction()) / 3)
        report = subject.compare_signals([samples], [samples], 48000)
        observed = report["channels"][0]["metrics"]["reference_dc_fs"]["value"]
        self.close(observed, exact_dc, absolute=1e-27, relative=2e-15)
        # Built-in sum may itself compensate on supported Python versions.
        # Spell out a naive left fold to make this negative control portable.
        naive_dc = ((samples[0] + samples[1]) + samples[2]) / 3
        self.assertNotEqual(observed, naive_dc)

    def test_floor_precedence_uses_inclusive_reference_and_error_boundaries(self):
        cases = [(0, 0, "reference_at_or_below_floor"),
                 (0.25, 0.25, "reference_at_or_below_floor"),
                 (1, 1, "zero_error"),
                 (1, 1.25, "error_at_or_below_floor"),
                 (1, 1.125, "error_at_or_below_floor")]
        for reference, candidate, reason in cases:
            with self.subTest(reference=reference, candidate=candidate):
                point = subject.compare_signals([[reference]], [[candidate]], 1, floor_fs=0.25)["channels"][0]["metrics"]
                self.metric(point["signal_to_error_db"], None, "dB", reason)
                if reference <= 0.25:
                    self.metric(point["normalized_rms_error"], None, "ratio", "reference_at_or_below_floor")
                else:
                    self.metric(point["normalized_rms_error"], abs(candidate-reference)/reference, "ratio")

    def test_amplitude_rate_and_floor_endpoints_are_inclusive(self):
        for rate in (1, 768000):
            for floor in (1e-12, 1e6):
                with self.subTest(rate=rate, floor=floor):
                    report = subject.compare_signals([[-1000000, 1000000]], [[1000000, -1000000]], rate, floor_fs=floor)
                    self.metric(report["channels"][0]["metrics"]["rms_error_fs"], 2e6, "FS")
                    self.assertEqual(report["sample_rate_hz"], rate)

    def test_near_floor_large_ratios_are_valid_finite_report_values(self):
        reference = math.nextafter(1e-12, math.inf)
        report = subject.compare_signals([[reference]], [[1e6]], 1, frequencies_hz=[0])
        expected = (1e6-reference)/reference
        self.assertGreater(expected, 1e12)
        point = report["channels"][0]["metrics"]
        spectral = report["channels"][0]["frequencies"][0]["metrics"]
        self.metric(point["normalized_rms_error"], expected, "ratio")
        self.metric(spectral["normalized_complex_error"], expected, "ratio")
        subject.validate_comparison_report(report)
        self.assertEqual(json.loads(json.dumps(report, allow_nan=False)), report)

    def test_tuple_input_nonmutation_and_returned_container_independence(self):
        reference = [[1, -2, 3], [4, -5, 6]]
        candidate = [[2, -1, 4], [3, -6, 5]]
        frequencies = [0, 1]
        before = copy.deepcopy((reference, candidate, frequencies))
        report = subject.compare_signals(reference, candidate, 8, frequencies_hz=frequencies)
        tuples = subject.compare_signals(tuple(map(tuple, reference)), tuple(map(tuple, candidate)), 8, frequencies_hz=tuple(frequencies))
        self.assertEqual(report, tuples)
        report["analysis"]["frequencies_hz"].append(3)
        report["channels"][0]["metrics"]["reference_dc_fs"]["value"] = 99
        self.assertEqual((reference, candidate, frequencies), before)
        self.assertEqual(tuples["analysis"]["frequencies_hz"], [0, 1])

    def test_repeated_calls_are_deterministic_and_have_exact_metadata(self):
        ref, cand = [[0, 1, 0, -1]], [[1, 0, -1, 0]]
        reports = [subject.compare_signals(ref, cand, 4, frequencies_hz=[0, 1, 2]) for _ in range(2)]
        self.assertEqual(reports[0], reports[1])
        self.assertEqual(json.dumps(reports[0], allow_nan=False), json.dumps(reports[1], allow_nan=False))
        self.assertEqual(set(reports[0]), {"schema_version", "metric_contract", "sample_rate_hz", "channel_count", "frame_count", "analysis", "channels", "physical_fidelity"})
        self.assertEqual(reports[0]["analysis"], {"pairing": "index", "frame_start": 0, "frame_stop": 4, "window": "rectangular", "floor_fs": 1e-12, "frequencies_hz": [0, 1, 2], "dft_normalization": "weighted_mean", "transform": "none"})
        self.assertEqual(reports[0]["physical_fidelity"], "not_established")


class SpectralAcceptance(MetricCase):
    def coefficient(self, report, expected):
        self.assertEqual(set(report), {"real_fs", "imag_fs"})
        self.close(report["real_fs"], expected.real)
        self.close(report["imag_fs"], expected.imag)

    def test_literal_sine_cosine_coefficients_and_all_eight_metrics(self):
        report = subject.compare_signals([[0, 1, 0, -1]], [[1, 0, -1, 0]], 4, frequencies_hz=[1])
        row = report["channels"][0]["frequencies"][0]
        expected = literal_report()["channels"][0]["frequencies"][0]
        self.coefficient(row["reference_coefficient"], -0.5j)
        self.coefficient(row["candidate_coefficient"], 0.5+0j)
        self.assertEqual(set(row["metrics"]), set(FREQUENCY_UNITS))
        for key, metric in expected["metrics"].items():
            self.metric(row["metrics"][key], metric["value"], metric["unit"])
        self.assertEqual(row["phase_mask"], "none")

    def test_signed_constant_dc_under_both_windows(self):
        for window in ("rectangular", "hann_symmetric"):
            with self.subTest(window=window):
                row = subject.compare_signals([[-3]*5], [[-0.5]*5], 17, frequencies_hz=[0], window=window)["channels"][0]["frequencies"][0]
                self.coefficient(row["reference_coefficient"], -3+0j)
                self.coefficient(row["candidate_coefficient"], -0.5+0j)
                self.metric(row["metrics"]["reference_phase_rad"], math.pi, "rad")
                self.metric(row["metrics"]["complex_abs_error_fs"], 2.5, "FS")

    def test_nyquist_is_not_doubled(self):
        row = subject.compare_signals([[1, -1, 1, -1]], [[2, -2, 2, -2]], 4, frequencies_hz=[2])["channels"][0]["frequencies"][0]
        self.coefficient(row["reference_coefficient"], 1+0j)
        self.coefficient(row["candidate_coefficient"], 2+0j)
        self.metric(row["metrics"]["normalized_complex_error"], 1, "ratio")

    def test_off_bin_coefficients_against_separate_complex_exponential_sum(self):
        refs = [[0.25, -0.5, 1.5, -2, 3.25, 0.75, -1], [2, 0, -3, 1, 4, -0.25, 0.5]]
        cands = [[1, -1, 1, -1, 1, -1, 1], [-2, 1, -4, 2, 3, 0.25, -0.5]]
        frequencies = [0, 0.375, 2.75, 6.5]
        for window in ("rectangular", "hann_symmetric"):
            weights = ([1]*7 if window == "rectangular" else
                       [0, 0.25, 0.75, 1, 0.75, 0.25, 0])
            report = subject.compare_signals(refs, cands, 13, frequencies_hz=frequencies, window=window)
            for channel, (reference, candidate) in enumerate(zip(refs, cands)):
                for index, frequency in enumerate(frequencies):
                    with self.subTest(window=window, channel=channel, frequency=frequency):
                        row = report["channels"][channel]["frequencies"][index]
                        expected_ref = coefficient_oracle(reference, frequency, 13, weights)
                        expected_cand = coefficient_oracle(candidate, frequency, 13, weights)
                        self.coefficient(row["reference_coefficient"], expected_ref)
                        self.coefficient(row["candidate_coefficient"], expected_cand)
                        self.metric(row["metrics"]["complex_abs_error_fs"], abs(expected_cand-expected_ref), "FS")

    def test_three_frame_hann_has_zero_edges_and_original_phase_origin(self):
        row = subject.compare_signals([[1e6, 2, -1e6]], [[-1e6, 3, 1e6]], 4, frequencies_hz=[1], window="hann_symmetric")["channels"][0]["frequencies"][0]
        self.coefficient(row["reference_coefficient"], -2j)
        self.coefficient(row["candidate_coefficient"], -3j)
        self.metric(row["metrics"]["complex_abs_error_fs"], 1, "FS")

    def test_five_frame_hann_normalizes_by_actual_weight_sum(self):
        row = subject.compare_signals([[100, 2, 4, 6, -100]], [[-100, 1, 2, 3, 100]], 8, frequencies_hz=[0], window="hann_symmetric")["channels"][0]["frequencies"][0]
        self.coefficient(row["reference_coefficient"], 4+0j)
        self.coefficient(row["candidate_coefficient"], 2+0j)

    def test_phase_masks_preserve_one_sided_errors_and_floor_equality(self):
        cases = [(0.25, 0.125, "both_at_or_below_floor"),
                 (0.25, 1, "reference_at_or_below_floor"),
                 (1, 0.25, "candidate_at_or_below_floor")]
        for reference, candidate, mask in cases:
            with self.subTest(reference=reference, candidate=candidate):
                row = subject.compare_signals([[reference]], [[candidate]], 1, frequencies_hz=[0], floor_fs=0.25)["channels"][0]["frequencies"][0]
                self.assertEqual(row["phase_mask"], mask)
                self.metric(row["metrics"]["phase_error_rad"], None, "rad", mask)
                self.metric(row["metrics"]["absolute_phase_error_rad"], None, "rad", mask)
                self.metric(row["metrics"]["complex_abs_error_fs"], abs(candidate-reference), "FS")
                reason = "reference_at_or_below_floor" if reference <= 0.25 else None
                self.metric(row["metrics"]["normalized_complex_error"], None if reason else abs(candidate-reference)/reference, "ratio", reason)

    def test_polarity_maps_phase_to_positive_pi_and_lag_stays_negative(self):
        polarity = subject.compare_signals([[1]], [[-1]], 1, frequencies_hz=[0])["channels"][0]["frequencies"][0]
        self.metric(polarity["metrics"]["phase_error_rad"], math.pi, "rad")
        lag = subject.compare_signals([[1, 0, -1, 0]], [[0, 1, 0, -1]], 4, frequencies_hz=[1])["channels"][0]["frequencies"][0]
        self.metric(lag["metrics"]["phase_error_rad"], -math.pi/2, "rad")

    def test_all_masked_frequency_rows_and_absolute_metrics_are_retained(self):
        report = subject.compare_signals([[0]*4], [[0]*4], 4, frequencies_hz=[0, 0.25, 1, 2])
        rows = report["channels"][0]["frequencies"]
        self.assertEqual([row["frequency_hz"] for row in rows], [0, 0.25, 1, 2])
        for row in rows:
            self.assertEqual(row["phase_mask"], "both_at_or_below_floor")
            self.assertEqual(set(row["metrics"]), set(FREQUENCY_UNITS))
            self.metric(row["metrics"]["complex_abs_error_fs"], 0, "FS")

    def test_empty_frequency_list_performs_no_trigonometric_work(self):
        with mock.patch.object(math, "cos", side_effect=AssertionError("unexpected cosine")), mock.patch.object(math, "sin", side_effect=AssertionError("unexpected sine")):
            report = subject.compare_signals([[1, 2, 3]], [[2, 3, 4]], 3, frequencies_hz=[], window="hann_symmetric")
        self.assertEqual(report["channels"][0]["frequencies"], [])
        self.assertEqual(set(report["channels"][0]["metrics"]), set(POINT_UNITS))

    def test_maximum_channel_and_frequency_report_shape(self):
        report = subject.compare_signals([[1, 0, -1]]*16, [[1, 0, -1]]*16, 128, frequencies_hz=list(range(64)))
        self.assertEqual(len(report["channels"]), 16)
        for index, channel in enumerate(report["channels"]):
            self.assertEqual(channel["reference_channel_index"], index)
            self.assertEqual(len(channel["frequencies"]), 64)
        subject.validate_comparison_report(report)


class InputAdmission(MetricCase):
    def test_outer_and_channel_container_types_are_exact(self):
        class ListSubclass(list):
            pass
        class TupleSubclass(tuple):
            pass
        bad = [None, 1, {}, "1", b"1", iter([[1]]), ListSubclass([[1]]), TupleSubclass(((1,),))]
        for value in bad:
            with self.subTest(kind=type(value).__name__):
                self.rejection(value, [[1]], 1)
                self.rejection([[1]], value, 1)
        for value in (None, {}, "1", b"1", iter([1]), ListSubclass([1]), TupleSubclass((1,))):
            with self.subTest(channel_kind=type(value).__name__):
                self.rejection([value], [[1]], 1)
                self.rejection([[1]], [value], 1)

    def test_dimension_zero_mismatch_and_limits(self):
        cases = [([], []), ([[]], [[]]), ([[1]], [[1], [1]]),
                 ([[1, 2]], [[1]]), ([[1], [2, 3]], [[1], [2]]),
                 ([[1]]*17, [[1]]*17), ([[0]*262145], [[0]*262145])]
        for reference, candidate in cases:
            with self.subTest(channels=(len(reference), len(candidate))):
                self.rejection(reference, candidate, 48000)

    def test_scalar_types_nonfinite_and_amplitude_excess(self):
        class IntSubclass(int):
            pass
        class FloatSubclass(float):
            pass
        bad = [True, False, None, "1", 1j, Decimal("1"), Fraction(1, 2),
               IntSubclass(1), FloatSubclass(1), math.nan, math.inf, -math.inf,
               1000001, -1000001, math.nextafter(1e6, math.inf),
               math.nextafter(-1e6, -math.inf), 10**400]
        for value in bad:
            with self.subTest(value_type=type(value).__name__, value=repr(value)):
                self.rejection([[value]], [[0]], 1)
                self.rejection([[0]], [[value]], 1)

    def test_rate_requires_exact_bounded_integer(self):
        for value in (True, False, 1.0, 0, -1, 768001, 10**400, None, "48000", math.inf):
            with self.subTest(rate=repr(value)):
                self.rejection([[1]], [[1]], value)

    def test_floor_requires_exact_finite_bounded_number(self):
        for value in (True, False, None, "0.1", Decimal("0.1"), math.nan,
                      math.inf, -1, 0, math.nextafter(1e-12, 0), math.nextafter(1e6, math.inf), 10**400):
            with self.subTest(floor=repr(value)):
                self.rejection([[1]], [[1]], 1, floor_fs=value)

    def test_frequency_container_count_order_type_and_nyquist(self):
        bad = [None, {}, "1", iter([1]), [True], [False], [None], ["1"],
               [Decimal("1")], [math.nan], [math.inf], [-1], [2.50001],
               [0, 0], [1, 1.0], [1, 0], list(range(65))]
        for value in bad:
            with self.subTest(frequencies=repr(value)):
                self.rejection([[1]], [[1]], 5, frequencies_hz=value)
        report = subject.compare_signals([[1]], [[1]], 5, frequencies_hz=[0, 2.5])
        self.assertEqual(report["analysis"]["frequencies_hz"], [0, 2.5])

    def test_window_names_types_and_hann_minimum(self):
        class StringSubclass(str):
            pass
        for value in (None, True, 1, "hann", "Rectangular", "rectangular ", StringSubclass("rectangular")):
            with self.subTest(window=repr(value)):
                self.rejection([[1, 2, 3]], [[1, 2, 3]], 3, window=value)
        for count in (1, 2):
            self.rejection([[1]*count], [[1]*count], 3, window="hann_symmetric")

    def test_all_samples_are_admitted_before_spectral_work(self):
        reference = [[0, 1, 0], [0, 1, 0]]
        candidate = [[0, 1, 0], [0, 1, math.nan]]
        before_first = copy.deepcopy((reference, candidate[0]))
        with mock.patch.object(math, "cos", side_effect=AssertionError("premature spectral work")):
            self.rejection(reference, candidate, 4, frequencies_hz=[1])
        self.assertEqual((reference, candidate[0]), before_first)
        self.assertTrue(math.isnan(candidate[1][-1]))

    def test_spectral_work_limit_exact_admission_and_excess_preflight(self):
        # Stop at the first trigonometric call. This checks actual public-path
        # admission at C*N*K = 2*262144*32, not maximum-work runtime performance.
        class SpectralEntered(RuntimeError):
            pass
        channels = [[0]*262144]*2
        with mock.patch.object(math, "cos", side_effect=SpectralEntered) as cosine:
            self.rejection(channels, channels, 128, frequencies_hz=list(range(33)))
            cosine.assert_not_called()
            with self.assertRaises(SpectralEntered):
                subject.compare_signals(channels, channels, 128, frequencies_hz=list(range(32)))
            cosine.assert_called_once()
        self.assertEqual(channels[0][0], 0)
        self.assertEqual(channels[-1][-1], 0)


class ReportAdmission(MetricCase):
    def test_independently_constructed_known_and_silent_reports_are_accepted(self):
        for report in (literal_report(), silent_literal_report()):
            before = copy.deepcopy(report)
            self.assertIsNone(subject.validate_comparison_report(report))
            self.assertEqual(report, before)

    def test_unknown_and_missing_fields_at_every_object_level(self):
        paths = [(), ("analysis",), ("channels", 0),
                 ("channels", 0, "metrics"),
                 ("channels", 0, "metrics", "rms_error_fs"),
                 ("channels", 0, "frequencies", 0),
                 ("channels", 0, "frequencies", 0, "reference_coefficient"),
                 ("channels", 0, "frequencies", 0, "metrics"),
                 ("channels", 0, "frequencies", 0, "metrics", "phase_error_rad")]
        for path in paths:
            for operation in ("extra", "missing"):
                with self.subTest(path=path, operation=operation):
                    report = literal_report()
                    target = report
                    for component in path:
                        target = target[component]
                    if operation == "extra":
                        target["unexpected"] = None
                    else:
                        del target[next(iter(target))]
                    self.reject_report(report)

    def test_constants_exact_integers_and_geometry_are_enforced(self):
        changes = [(("schema_version",), True), (("schema_version",), 1.0),
                   (("metric_contract",), "capture-comparison-v2"),
                   (("physical_fidelity",), "pass"),
                   (("sample_rate_hz",), True), (("sample_rate_hz",), 4.0),
                   (("channel_count",), 2), (("frame_count",), 0),
                   (("frame_count",), 262145),
                   (("analysis", "pairing"), "mixed"),
                   (("analysis", "frame_start"), False),
                   (("analysis", "frame_start"), 1),
                   (("analysis", "frame_stop"), 3),
                   (("analysis", "frame_stop"), 4.0),
                   (("analysis", "window"), "hann"),
                   (("analysis", "dft_normalization"), "rms"),
                   (("analysis", "transform"), "gain_fit")]
        for path, value in changes:
            with self.subTest(path=path, value=value):
                report = literal_report()
                target = report
                for component in path[:-1]:
                    target = target[component]
                target[path[-1]] = value
                self.reject_report(report)

    def test_metric_units_values_and_known_null_rules(self):
        for spectral, units in ((False, POINT_UNITS), (True, FREQUENCY_UNITS)):
            for key in units:
                for field, value in (("unit", "wrong"), ("value", None),
                                     ("value", True), ("value", math.nan),
                                     ("value", math.inf), ("undefined_reason", "invented")):
                    with self.subTest(spectral=spectral, metric=key, field=field, value=repr(value)):
                        report = literal_report()
                        channel = report["channels"][0]
                        metrics = channel["frequencies"][0]["metrics"] if spectral else channel["metrics"]
                        metrics[key][field] = value
                        self.reject_report(report)

    def test_nonnegative_quantities_reject_negative_values(self):
        point_keys = set(POINT_UNITS)-{"reference_dc_fs", "candidate_dc_fs", "dc_bias_fs", "signal_to_error_db"}
        frequency_keys = {"reference_magnitude_fs", "candidate_magnitude_fs", "complex_abs_error_fs", "normalized_complex_error", "absolute_phase_error_rad"}
        for spectral, keys in ((False, point_keys), (True, frequency_keys)):
            for key in keys:
                with self.subTest(spectral=spectral, metric=key):
                    report = literal_report()
                    row = report["channels"][0]
                    metrics = row["frequencies"][0]["metrics"] if spectral else row["metrics"]
                    metrics[key]["value"] = -0.125
                    self.reject_report(report)

    def test_phase_range_rejects_negative_pi_and_accepts_positive_pi(self):
        for key in ("reference_phase_rad", "candidate_phase_rad", "phase_error_rad"):
            for value in (-math.pi, math.nextafter(math.pi, math.inf)):
                with self.subTest(metric=key, value=value):
                    report = literal_report()
                    report["channels"][0]["frequencies"][0]["metrics"][key]["value"] = value
                    self.reject_report(report)
            report = literal_report()
            report["channels"][0]["frequencies"][0]["metrics"][key]["value"] = math.pi
            subject.validate_comparison_report(report)
        for value in (-0.1, math.nextafter(math.pi, math.inf)):
            report = literal_report()
            report["channels"][0]["frequencies"][0]["metrics"]["absolute_phase_error_rad"]["value"] = value
            self.reject_report(report)

    def test_channel_pairing_frequency_order_and_coverage_are_exact(self):
        mutations = [lambda r: r["channels"][0].update(reference_channel_index=True),
                     lambda r: r["channels"][0].update(candidate_channel_index=1),
                     lambda r: r["channels"][0].update(frequencies=[]),
                     lambda r: r["channels"][0]["frequencies"].append(copy.deepcopy(r["channels"][0]["frequencies"][0])),
                     lambda r: r["channels"][0]["frequencies"][0].update(frequency_hz=0),
                     lambda r: r["channels"][0]["frequencies"][0].update(frequency_hz=True),
                     lambda r: r["analysis"].update(frequencies_hz=[1, 1]),
                     lambda r: r["analysis"].update(frequencies_hz=[2, 1]),
                     lambda r: r.update(channels=tuple(r["channels"])),
                     lambda r: r["analysis"].update(frequencies_hz=(1,))]
        for index, mutate in enumerate(mutations):
            with self.subTest(mutation=index):
                report = literal_report()
                mutate(report)
                self.reject_report(report)

    def test_null_reasons_and_phase_masks_must_match_floor_conditions(self):
        mutations = [lambda r: r["channels"][0]["metrics"]["normalized_rms_error"].update(value=0, undefined_reason=None),
                     lambda r: r["channels"][0]["metrics"]["signal_to_error_db"].update(undefined_reason="zero_error"),
                     lambda r: r["channels"][0]["frequencies"][0].update(phase_mask="none"),
                     lambda r: r["channels"][0]["frequencies"][0]["metrics"]["phase_error_rad"].update(undefined_reason="reference_at_or_below_floor"),
                     lambda r: r["channels"][0]["frequencies"][0]["metrics"]["candidate_phase_rad"].update(undefined_reason="reference_at_or_below_floor"),
                     lambda r: r["channels"][0]["frequencies"][0]["metrics"]["complex_abs_error_fs"].update(value=None, undefined_reason="both_at_or_below_floor")]
        for index, mutate in enumerate(mutations):
            with self.subTest(mutation=index):
                report = silent_literal_report()
                mutate(report)
                self.reject_report(report)

    def test_report_traversal_guards_cycles_depth_members_nodes_and_types(self):
        cycle = {}
        cycle["cycle"] = cycle
        deep = 0
        for _ in range(14):
            deep = [deep]
        reports = [cycle, deep, [None]*4097, [[None]*4096 for _ in range(17)],
                   {1: "bad-key"}, {"unsafe": {1, 2}}, {"unsafe": b"bytes"},
                   {"unsafe": (1, 2)}, {"unsafe": object()},
                   {"unsafe": "\ud800"}, {"unsafe": 10**400}]
        for index, report in enumerate(reports):
            with self.subTest(case=index):
                self.reject_report(report)

    def test_report_number_bound_accepts_two_e18_but_rejects_next_float(self):
        # Admission is structural; this deliberately does not claim these edited
        # diagnostic values were computed from any underlying signal.
        for key in ("normalized_rms_error", "rms_error_fs"):
            report = literal_report()
            report["channels"][0]["metrics"][key]["value"] = 2e18
            subject.validate_comparison_report(report)
            report["channels"][0]["metrics"][key]["value"] = math.nextafter(2e18, math.inf)
            self.reject_report(report)
        report = literal_report()
        report["channels"][0]["frequencies"][0]["reference_coefficient"]["imag_fs"] = math.nan
        self.reject_report(report)

    def test_rejected_report_is_not_mutated(self):
        report = literal_report()
        report["channels"][0]["metrics"]["rms_error_fs"]["unit"] = "V"
        before = copy.deepcopy(report)
        self.reject_report(report)
        self.assertEqual(report, before)


if __name__ == "__main__":
    unittest.main()
