#!/usr/bin/env python3
"""Independent bounded numerical qualification for capture-comparison-v1.

The oracle uses 90-digit Decimal Machin/Taylor arithmetic and complex Horner
polynomials, not the producer's binary64 trigonometric sample loop. Closed-form
Dirichlet/Hann coefficients and exact stored-float rational sums cross-check it.
Tolerances are fixed analytical engineering budgets, not fitted observations.
These fixtures establish no physical uncertainty or instrument fidelity.
"""

from __future__ import annotations

import copy
from decimal import Decimal, localcontext
from fractions import Fraction
from functools import lru_cache
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


PRECISION = 90
UNIT_ROUNDOFF = 2.0 ** -53
ZERO = Decimal(0)
ONE = Decimal(1)


def decimal_value(value):
    if type(value) is float:
        return Decimal.from_float(value)
    return Decimal(value)


def atan_series(value):
    """Alternating series used only after reducing |value| to at most 1/2."""
    term = value
    total = value
    square = value * value
    k = 1
    while True:
        term *= -square
        updated = total + term / (2 * k + 1)
        if updated == total:
            return total
        total = updated
        k += 1


@lru_cache(maxsize=1)
def pi_decimal():
    with localcontext() as context:
        context.prec = PRECISION
        return 16 * atan_series(ONE / 5) - 4 * atan_series(ONE / 239)


def sine_cosine(angle):
    """Decimal range reduction and two independently accumulated Taylor series."""
    with localcontext() as context:
        context.prec = PRECISION
        pi = pi_decimal()
        angle %= 2 * pi
        if angle > pi:
            angle -= 2 * pi
        elif angle < -pi:
            angle += 2 * pi
        square = angle * angle
        sine = sine_term = angle
        cosine = cosine_term = ONE
        k = 1
        while True:
            sine_term *= -square / ((2 * k) * (2 * k + 1))
            cosine_term *= -square / ((2 * k - 1) * (2 * k))
            next_sine = sine + sine_term
            next_cosine = cosine + cosine_term
            if next_sine == sine and next_cosine == cosine:
                return sine, cosine
            sine, cosine = next_sine, next_cosine
            k += 1


def multiply(left, right):
    return (left[0] * right[0] - left[1] * right[1],
            left[0] * right[1] + left[1] * right[0])


def divide(left, right):
    norm = right[0] * right[0] + right[1] * right[1]
    return ((left[0] * right[0] + left[1] * right[1]) / norm,
            (left[1] * right[0] - left[0] * right[1]) / norm)


def power(value, count):
    result = (ONE, ZERO)
    while count:
        if count & 1:
            result = multiply(result, value)
        value = multiply(value, value)
        count //= 2
    return result


def unit_root(frequency, rate, frame=1):
    with localcontext() as context:
        context.prec = PRECISION
        turns = decimal_value(frequency) * frame / decimal_value(rate)
        turns %= ONE
        sine, cosine = sine_cosine(2 * pi_decimal() * turns)
        return cosine, -sine


@lru_cache(maxsize=32)
def weights(count, window):
    if window == "rectangular":
        return (ONE,) * count
    # sin²(pi*n/(N-1)) is an independent expression for symmetric Hann.
    with localcontext() as context:
        context.prec = PRECISION
        interior = []
        for n in range(1, count - 1):
            sine, _ = sine_cosine(pi_decimal() * n / (count - 1))
            interior.append(sine * sine)
        return (ZERO, *interior, ZERO)


def coefficient(samples, frequency, rate, window):
    """Evaluate the weighted polynomial at one Decimal unit-circle point."""
    with localcontext() as context:
        context.prec = PRECISION
        window_values = weights(len(samples), window)
        root = unit_root(frequency, rate)
        total = (ZERO, ZERO)
        for sample, weight in zip(reversed(samples), reversed(window_values)):
            total = multiply(total, root)
            total = (total[0] + decimal_value(sample) * weight, total[1])
        denominator = sum(window_values, ZERO)
        return total[0] / denominator, total[1] / denominator


def geometric_sum(count, frequency, rate):
    """Closed form 1 + z + ... + z^(N-1), without summing sample terms."""
    with localcontext() as context:
        context.prec = PRECISION
        root = unit_root(frequency, rate)
        if root == (ONE, ZERO):
            return Decimal(count), ZERO
        end = power(root, count)
        return divide((1 - end[0], -end[1]), (1 - root[0], -root[1]))


def constant_closed_form(count, frequency, rate, window, amplitude):
    with localcontext() as context:
        context.prec = PRECISION
        result = geometric_sum(count, frequency, rate)
        if window == "rectangular":
            return tuple(part * decimal_value(amplitude) / count for part in result)
        shift = Decimal(rate) / (count - 1)
        lower = geometric_sum(count, decimal_value(frequency) - shift, rate)
        upper = geometric_sum(count, decimal_value(frequency) + shift, rate)
        denominator = Decimal(count - 1) / 2
        return tuple((result[i] / 2 - (lower[i] + upper[i]) / 4)
                     * decimal_value(amplitude) / denominator for i in (0, 1))


def magnitude(value):
    with localcontext() as context:
        context.prec = PRECISION
        return (value[0] * value[0] + value[1] * value[1]).sqrt()


def argument(value):
    """Independent Decimal atan2, with the contract's (-pi,pi] convention."""
    with localcontext() as context:
        context.prec = PRECISION
        real, imag = value
        pi = pi_decimal()
        if real == 0:
            if imag == 0:
                raise ValueError("zero coefficient has no oracle phase")
            return pi / 2 if imag > 0 else -pi / 2
        ratio = abs(imag / real)
        reciprocal = ratio > 1
        if reciprocal:
            ratio = 1 / ratio
        angle = (pi / 4 + atan_series((ratio - 1) / (ratio + 1))
                 if ratio > Decimal("0.5") else atan_series(ratio))
        if reciprocal:
            angle = pi / 2 - angle
        if real < 0:
            angle = pi - angle
        if imag < 0:
            angle = -angle
        return pi if angle == -pi else angle


def component_budget(samples, frequency, rate, window, expected):
    """A priori absolute component allowance; see the retained evidence note.

    Reserve 64u for argument/libm/product/fsum/division errors, scaled by
    maximum phase and weighted L1 magnitude. Hann additionally allows absolute
    weight and normalization errors. The Decimal oracle is much more precise.
    This is an exercised engineering allowance, not a proof for every libm.
    """
    with localcontext() as context:
        context.prec = PRECISION
        window_values = weights(len(samples), window)
        denominator = sum(window_values, ZERO)
        weighted_l1 = float(sum((abs(decimal_value(x)) * w
                                 for x, w in zip(samples, window_values)), ZERO) / denominator)
        phase = 2 * math.pi * abs(float(frequency)) * (len(samples) - 1) / rate
        allowance = 64 * UNIT_ROUNDOFF * (1 + phase) * weighted_l1
        if window == "hann_symmetric":
            # Endpoint weights are defined exactly zero, so exclude endpoints
            # from weight perturbation. Retain denominator perturbation too.
            interior_l1 = float(sum((abs(decimal_value(x)) for x in samples[1:-1]), ZERO) / denominator)
            allowance += 64 * UNIT_ROUNDOFF * (interior_l1 + len(samples) / float(denominator)
                                               * float(magnitude(expected)))
        return allowance + 4 * max(math.ulp(float(part)) for part in expected)


class NumericCase(unittest.TestCase):
    def close(self, actual, expected, allowance):
        self.assertIn(type(actual), (int, float))
        self.assertTrue(math.isfinite(actual))
        self.assertLessEqual(abs(actual - float(expected)), allowance,
                             (actual, float(expected), allowance))

    def check_coefficient(self, actual, expected, allowance):
        self.assertEqual(set(actual), {"real_fs", "imag_fs"})
        self.close(actual["real_fs"], expected[0], allowance)
        self.close(actual["imag_fs"], expected[1], allowance)

    def metric_value(self, metric):
        self.assertIsNone(metric["undefined_reason"])
        self.assertTrue(math.isfinite(metric["value"]))
        return metric["value"]

    def check_phase(self, metric, expected, allowance):
        actual = self.metric_value(metric)
        self.assertGreater(actual, -math.pi)
        self.assertLessEqual(actual, math.pi)
        difference = abs(actual - float(expected))
        self.assertLessEqual(min(difference, abs(2 * math.pi - difference)), allowance)


class IndependentOracleChecks(NumericCase):
    def test_machin_pi_and_taylor_quadrants(self):
        with localcontext() as context:
            context.prec = PRECISION
            known_pi = Decimal("3.141592653589793238462643383279502884197169399375105820974944592307816406286208998628")
            self.assertLess(abs(pi_decimal() - known_pi), Decimal("1e-83"))
            for multiple, expected in [(0, (0, 1)), (1, (1, 0)),
                                       (2, (0, -1)), (3, (-1, 0)), (4, (0, 1))]:
                sine, cosine = sine_cosine(pi_decimal() * multiple / 2)
                self.assertLess(abs(sine - expected[0]), Decimal("1e-85"))
                self.assertLess(abs(cosine - expected[1]), Decimal("1e-85"))
            sine, cosine = sine_cosine(pi_decimal() / 3)
            self.assertLess(abs(sine - Decimal(3).sqrt() / 2), Decimal("1e-85"))
            self.assertLess(abs(cosine - Decimal("0.5")), Decimal("1e-85"))

    def test_horner_oracle_agrees_with_distinct_closed_forms(self):
        for window in ("rectangular", "hann_symmetric"):
            for frequency in (0, 2.0 ** -40, 0.375, 7.625, 15.5):
                with self.subTest(window=window, frequency=frequency):
                    actual = coefficient([1.25] * 17, frequency, 31, window)
                    expected = constant_closed_form(17, frequency, 31, window, 1.25)
                    with localcontext() as context:
                        context.prec = PRECISION
                        for left, right in zip(actual, expected):
                            self.assertLess(abs(left - right), Decimal("1e-65"))


class HighPrecisionCoefficients(NumericCase):
    def check_off_bin_matrix(self, window):
        for count in (7, 18, 65):
            reference = [((n * 37) % 41 - 20) / 16 for n in range(count)]
            candidate = [x * 0.75 + ((n * 11) % 9 - 4) / 32 for n, x in enumerate(reference)]
            frequencies = [0, 2.0 ** -20, 0.375, 3.8125, math.nextafter(31.5, 0), 31.5]
            report = subject.compare_signals([reference], [candidate], 63,
                                             frequencies_hz=frequencies, window=window)
            self.assertEqual(report["analysis"]["frequencies_hz"], frequencies)
            for frequency, row in zip(frequencies, report["channels"][0]["frequencies"]):
                with self.subTest(window=window, count=count, frequency=frequency):
                    errors = []
                    expected = []
                    for name, samples in (("reference", reference), ("candidate", candidate)):
                        result = coefficient(samples, frequency, 63, window)
                        bound = component_budget(samples, frequency, 63, window, result)
                        self.check_coefficient(row[name + "_coefficient"], result, bound)
                        self.close(self.metric_value(row["metrics"][name + "_magnitude_fs"]),
                                   magnitude(result), 2 * bound)
                        errors.append(bound)
                        expected.append(result)
                    with localcontext() as context:
                        context.prec = PRECISION
                        delta = tuple(c - r for r, c in zip(*expected))
                        self.close(self.metric_value(row["metrics"]["complex_abs_error_fs"]),
                                   magnitude(delta), 2 * sum(errors))
            self.assertEqual(report["physical_fidelity"], "not_established")

    def test_rectangular_off_bin_coefficients_use_exact_supplied_frequencies(self):
        self.check_off_bin_matrix("rectangular")

    def test_symmetric_hann_odd_even_off_bin_coefficients(self):
        self.check_off_bin_matrix("hann_symmetric")

    def test_constant_records_match_dirichlet_and_hann_convolution_closed_forms(self):
        for window in ("rectangular", "hann_symmetric"):
            samples = [1.25] * 31
            frequencies = [0, 1e-6, 1.125, 30.25, 63.5]
            rows = subject.compare_signals([samples], [samples], 127,
                                            frequencies_hz=frequencies, window=window)["channels"][0]["frequencies"]
            for frequency, row in zip(frequencies, rows):
                with self.subTest(window=window, frequency=frequency):
                    expected = constant_closed_form(31, frequency, 127, window, 1.25)
                    self.check_coefficient(row["reference_coefficient"], expected,
                                           component_budget(samples, frequency, 127, window, expected))
                    self.assertEqual(row["metrics"]["complex_abs_error_fs"]["value"], 0)

    def test_hann_endpoint_suppression_retains_pointwise_disagreement(self):
        reference, candidate = [0] * 129, [0] * 129
        reference[0], reference[-1] = 1e6, -1e6
        candidate[0], candidate[-1] = -1e6, 1e6
        report = subject.compare_signals([reference], [candidate], 127,
                                         frequencies_hz=[0, 0.375, 31.5, 63.5], window="hann_symmetric")
        channel = report["channels"][0]
        self.assertEqual(channel["metrics"]["max_abs_error_fs"]["value"], 2e6)
        self.assertGreater(channel["metrics"]["rms_error_fs"]["value"], 0)
        for row in channel["frequencies"]:
            self.assertEqual(row["reference_coefficient"], {"real_fs": 0, "imag_fs": 0})
            self.assertEqual(row["candidate_coefficient"], {"real_fs": 0, "imag_fs": 0})
            self.assertEqual(row["phase_mask"], "both_at_or_below_floor")

    def test_actual_maximum_frames_sparse_endpoint_at_high_frequency(self):
        # One frequency, one channel: 262,144 actual spectral terms. This is
        # neither the 16,777,216-term maximum nor a runtime-performance claim.
        count, rate, frequency = 262144, 768000, 383999.9375
        reference, candidate = [0.0] * count, [0.0] * count
        reference[-1], candidate[-2] = 524288.0, 262144.0
        report = subject.compare_signals([reference], [candidate], rate, frequencies_hz=[frequency])
        row = report["channels"][0]["frequencies"][0]
        for name, index, amplitude in (("reference", count - 1, 2), ("candidate", count - 2, 1)):
            root = unit_root(frequency, rate, index)
            with localcontext() as context:
                context.prec = PRECISION
                expected = tuple(part * amplitude for part in root)
            phase = 2 * math.pi * frequency * index / rate
            allowance = 64 * UNIT_ROUNDOFF * (1 + phase) * amplitude + 4 * math.ulp(amplitude)
            self.check_coefficient(row[name + "_coefficient"], expected, allowance)
        self.assertEqual(report["frame_count"], count)
        self.assertEqual(report["channels"][0]["metrics"]["reference_rms_fs"]["value"], 1024)
        self.assertEqual(report["channels"][0]["metrics"]["candidate_rms_fs"]["value"], 512)

    def test_nearby_and_adjacent_binary64_frequencies_are_retained(self):
        frequencies = [0, math.nextafter(0.0, math.inf), 3.125,
                       math.nextafter(3.125, math.inf), 3.125001,
                       math.nextafter(31.5, 0), 31.5]
        samples = [0] * 17
        samples[8] = 1
        rows = subject.compare_signals([samples], [samples], 63,
                                        frequencies_hz=frequencies)["channels"][0]["frequencies"]
        self.assertEqual([row["frequency_hz"] for row in rows], frequencies)
        for frequency, row in zip(frequencies, rows):
            expected = coefficient(samples, frequency, 63, "rectangular")
            self.check_coefficient(row["reference_coefficient"], expected,
                                   component_budget(samples, frequency, 63, "rectangular", expected))
        self.assertNotEqual(rows[2]["reference_coefficient"], rows[4]["reference_coefficient"])
        # Merely adjacent doubles may be below the calculation's roundoff
        # resolution. Their identities must survive; distinct result bits are
        # deliberately not required or treated as a precision guarantee.

    def test_hann_constant_normalization_for_even_and_longer_odd_records(self):
        for count in (4, 32, 257):
            with self.subTest(count=count):
                samples = [-0.375] * count
                row = subject.compare_signals([samples], [samples], 48000,
                                              frequencies_hz=[0], window="hann_symmetric")["channels"][0]["frequencies"][0]
                expected = (Decimal("-0.375"), ZERO)
                self.check_coefficient(row["reference_coefficient"], expected,
                                       component_budget(samples, 0, 48000, "hann_symmetric", expected))


class CancellationAndDynamicRange(NumericCase):
    def test_long_cancellation_preserves_dc_bias_and_dc_coefficient(self):
        tiny = 2.0 ** -40
        reference = [524288.0, tiny, -524288.0] * 99
        candidate = [524288.0, 2 * tiny, -524288.0] * 99
        report = subject.compare_signals([reference], [candidate], 48000, frequencies_hz=[0])
        channel = report["channels"][0]
        for key, values in (("reference_dc_fs", reference), ("candidate_dc_fs", candidate),
                            ("dc_bias_fs", [c - r for r, c in zip(reference, candidate)])):
            exact = float(sum(map(Fraction.from_float, values), Fraction()) / len(values))
            self.assertEqual(channel["metrics"][key]["value"], exact)
        row = channel["frequencies"][0]
        self.assertEqual(row["reference_coefficient"]["real_fs"], float(Fraction.from_float(tiny) / 3))
        self.assertEqual(row["candidate_coefficient"]["real_fs"], float(Fraction.from_float(2 * tiny) / 3))
        sequential = 0.0
        for value in reference:
            sequential += value
        self.assertNotEqual(sequential / len(reference), channel["metrics"]["reference_dc_fs"]["value"])

    def test_rms_error_ratio_and_db_against_decimal_dynamic_range_oracle(self):
        reference = [((n * 17) % 37 - 18) * 16384.0 + 2.0 ** -20 for n in range(257)]
        candidate = [x + ((n * 7) % 5 - 2) * 2.0 ** -10 for n, x in enumerate(reference)]
        point = subject.compare_signals([reference], [candidate], 48000)["channels"][0]["metrics"]
        with localcontext() as context:
            context.prec = PRECISION
            ref, cand = list(map(decimal_value, reference)), list(map(decimal_value, candidate))
            errors = [c - r for r, c in zip(ref, cand)]
            ref_rms = (sum((x * x for x in ref), ZERO) / len(ref)).sqrt()
            cand_rms = (sum((x * x for x in cand), ZERO) / len(cand)).sqrt()
            error_rms = (sum((x * x for x in errors), ZERO) / len(errors)).sqrt()
            expected = {"reference_rms_fs": ref_rms, "candidate_rms_fs": cand_rms,
                        "rms_error_fs": error_rms, "normalized_rms_error": error_rms / ref_rms,
                        "signal_to_error_db": 20 * (ref_rms / error_rms).log10()}
            for key, value in expected.items():
                self.close(self.metric_value(point[key]), value, 32 * UNIT_ROUNDOFF * abs(float(value)))


class PhaseAndMasks(NumericCase):
    def test_lead_and_lag_retain_the_wrap_discontinuity(self):
        delta = 2.0 ** -20
        frequencies = [0.25 - delta, 0.25, 0.25 + delta]
        for reverse in (False, True):
            reference, candidate = [1, 0, 0, 0, 0], [0, 0, 1, 0, 0]
            if reverse:
                reference, candidate = candidate, reference
            rows = subject.compare_signals([reference], [candidate], 1,
                                            frequencies_hz=frequencies)["channels"][0]["frequencies"]
            for frequency, row in zip(frequencies, rows):
                r = coefficient(reference, frequency, 1, "rectangular")
                c = coefficient(candidate, frequency, 1, "rectangular")
                with localcontext() as context:
                    context.prec = PRECISION
                    expected = argument(multiply(c, (r[0], -r[1])))
                self.check_phase(row["metrics"]["phase_error_rad"], expected, 256 * UNIT_ROUNDOFF)
            signs = [math.copysign(1, row["metrics"]["phase_error_rad"]["value"]) for row in (rows[0], rows[2])]
            self.assertEqual(signs, [1, -1] if reverse else [-1, 1])

    def test_arbitrary_off_bin_phases_against_decimal_atan2(self):
        reference = [0.75, -0.125, 0.25, 0.5, -0.375, 0.875, 0.125]
        candidate = [0.25, 0.5, -0.625, 0.25, 0.125, -0.375, 1]
        for window in ("rectangular", "hann_symmetric"):
            frequencies = [0.375, 1.125, 2.625, 3.875]
            rows = subject.compare_signals([reference], [candidate], 8,
                                            frequencies_hz=frequencies, window=window)["channels"][0]["frequencies"]
            for frequency, row in zip(frequencies, rows):
                r = coefficient(reference, frequency, 8, window)
                c = coefficient(candidate, frequency, 8, window)
                r_error = component_budget(reference, frequency, 8, window, r)
                c_error = component_budget(candidate, frequency, 8, window, c)
                bound = 4 * (r_error / float(magnitude(r)) + c_error / float(magnitude(c))) + 64 * UNIT_ROUNDOFF
                with localcontext() as context:
                    context.prec = PRECISION
                    self.check_phase(row["metrics"]["reference_phase_rad"], argument(r), bound)
                    self.check_phase(row["metrics"]["candidate_phase_rad"], argument(c), bound)
                    self.check_phase(row["metrics"]["phase_error_rad"], argument(multiply(c, (r[0], -r[1]))), bound)

    def test_off_bin_polarity_retains_positive_pi(self):
        reference = [0.5, -0.25, 0.75, 0.125, -0.5, 0.25, 0.625]
        for window in ("rectangular", "hann_symmetric"):
            rows = subject.compare_signals([reference], [[-x for x in reference]], 8,
                                            frequencies_hz=[0.375, 1.125, 2.625, 3.875], window=window)["channels"][0]["frequencies"]
            for row in rows:
                self.assertEqual(row["phase_mask"], "none")
                self.assertEqual(row["metrics"]["phase_error_rad"]["value"], math.pi)
                self.assertEqual(row["metrics"]["absolute_phase_error_rad"]["value"], math.pi)

    def test_floor_adjacent_floats_after_exact_impulse_normalization(self):
        floor = 2.0 ** -12
        levels = [math.nextafter(floor, 0), floor, math.nextafter(floor, math.inf)]
        for swap in (False, True):
            for level in levels:
                reference, candidate = [8 * level] + [0] * 7, [16 * floor] + [0] * 7
                if swap:
                    reference, candidate = candidate, reference
                rows = subject.compare_signals([reference], [candidate], 1,
                                                frequencies_hz=[0, 0.125, 0.499999], floor_fs=floor)["channels"][0]["frequencies"]
                expected = ("candidate_at_or_below_floor" if swap else "reference_at_or_below_floor") if level <= floor else "none"
                for row in rows:
                    self.assertEqual(row["phase_mask"], expected)
                    self.assertEqual(row["reference_coefficient"]["real_fs"], 2 * floor if swap else level)
                    self.assertEqual(row["candidate_coefficient"]["real_fs"], level if swap else 2 * floor)
                    self.assertEqual(row["metrics"]["phase_error_rad"]["undefined_reason"], None if expected == "none" else expected)

    def test_hann_floor_mask_does_not_mask_large_unwindowed_error(self):
        floor = 2.0 ** -12
        for level in (math.nextafter(floor, 0), floor, math.nextafter(floor, math.inf)):
            report = subject.compare_signals([[1e6, level, -1e6]], [[-1e6, 2 * floor, 1e6]], 1,
                                             frequencies_hz=[0], floor_fs=floor, window="hann_symmetric")
            channel = report["channels"][0]
            self.assertEqual(channel["metrics"]["max_abs_error_fs"]["value"], 2e6)
            row = channel["frequencies"][0]
            self.assertEqual(row["reference_coefficient"]["real_fs"], level)
            self.assertEqual(row["phase_mask"], "reference_at_or_below_floor" if level <= floor else "none")


class BoundedShapeAndWork(NumericCase):
    def test_maximum_channel_frequency_shape_has_independent_coefficients(self):
        count, rate = 9, 127
        frequencies = [k + 0.125 for k in range(64)]
        reference, candidate = [], []
        for channel in range(16):
            r, c = [0.0] * count, [0.0] * count
            r[channel % count] = (channel + 1) / 32
            c[(channel + 3) % count] = -(channel + 1) / 64
            reference.append(r)
            candidate.append(c)
        report = subject.compare_signals(reference, candidate, rate, frequencies_hz=frequencies)
        self.assertEqual(len(report["channels"]), 16)
        for index, channel in enumerate(report["channels"]):
            self.assertEqual((channel["reference_channel_index"], channel["candidate_channel_index"]), (index, index))
            self.assertEqual([row["frequency_hz"] for row in channel["frequencies"]], frequencies)
            for frequency, row in zip(frequencies, channel["frequencies"]):
                for name, samples in (("reference", reference[index]), ("candidate", candidate[index])):
                    expected = coefficient(samples, frequency, rate, "rectangular")
                    self.check_coefficient(row[name + "_coefficient"], expected,
                                           component_budget(samples, frequency, rate, "rectangular", expected))
        self.assertEqual(json.loads(json.dumps(report, allow_nan=False)), report)
        self.assertEqual(report["physical_fidelity"], "not_established")

    def test_full_scalar_shape_and_spectral_guard_precede_sample_admission(self):
        # Real public-path geometry, but a sentinel rejects before scalar
        # traversal/metrics. Reused lists do not claim an 8M-scalar scan.
        channel = [object()] + [0] * 262143
        channels = [channel] * 16
        with self.assertRaisesRegex(subject.ComparisonError, "selected-frequency work"):
            subject.compare_signals(channels, channels, 128, frequencies_hz=[0, 1, 2, 3, 4])
        with self.assertRaisesRegex(subject.ComparisonError, r"reference_channels\[0\]\[0\]"):
            subject.compare_signals(channels, channels, 128, frequencies_hz=[0, 1, 2, 3])
        self.assertIs(channels[-1][0], channel[0])

    def test_reduced_work_boundary_executes_every_admitted_frequency(self):
        reference = [[(n % 5) / 8 for n in range(31)], [((n * 3) % 7) / 16 for n in range(31)]]
        candidate = [[-x for x in channel] for channel in reference]
        before = copy.deepcopy((reference, candidate))
        with mock.patch.object(subject, "MAX_SPECTRAL_WORK", 186):
            report = subject.compare_signals(reference, candidate, 128, frequencies_hz=[0, 1.5, 10.5])
            self.assertEqual([len(channel["frequencies"]) for channel in report["channels"]], [3, 3])
            with self.assertRaisesRegex(subject.ComparisonError, "selected-frequency work"):
                subject.compare_signals(reference, candidate, 128, frequencies_hz=[0, 1.5, 10.5, 12])
        self.assertEqual((reference, candidate), before)


if __name__ == "__main__":
    unittest.main()
