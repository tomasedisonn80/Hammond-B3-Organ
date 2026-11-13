#!/usr/bin/env python3
"""Independent regression qualification of the offline nominal rotary oracle.

Expectations use ODE balance, complementary solutions, independent RK4 integration,
constructed emission-time geometry and derivative convergence. No native rotary
implementation or author self-test is used as an oracle. This suite does not
qualify interpolation, audio aliasing, real-time execution or a physical cabinet.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from decimal import Context, Decimal, Inexact, ROUND_UP, Rounded, localcontext
import hashlib
import json
import math
import os
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import rotary_reference as ref
from validate_rotary_profile import load_profile, normalized_profile

D = Decimal
ORACLE_CONTEXT = Context(prec=120, Emin=-999999999, Emax=999999999)
PROFILE = ROOT / "data/rotary/nominal-research-v1.json"
SCRIPT = ROOT / "tools/rotary_reference.py"


def constant_timeline(speed=0, direction=1, phase=0):
    return ref.RotorTimeline(ref.MotionProfile(speed, speed, "0.4", "0.7", direction),
                             phase, speed)


def rk4_motion(speed, angle, target, tau, direction, duration, steps):
    """Integrate the two first-order ODEs; no closed-form exponential solution."""
    step = duration / steps

    def slope(w):
        return (target - w) / tau, direction * w

    for _ in range(steps):
        a, b = slope(speed)
        c, d = slope(speed + step * a / 2)
        e, f = slope(speed + step * c / 2)
        g, h = slope(speed + step * e)
        speed += step * (a + 2 * c + 2 * e + g) / 6
        angle += step * (b + 2 * d + 2 * f + h) / 6
    return speed, angle


class DecimalAssertions(unittest.TestCase):
    def assert_decimal_close(self, actual, expected, absolute="1e-68", relative="1e-74"):
        with localcontext(ORACLE_CONTEXT):
            error = abs(D(actual) - D(expected))
            bound = D(absolute) + D(relative) * abs(D(expected))
        self.assertLessEqual(error, bound, f"{actual} differs from {expected} by {error}")


class MotionTests(DecimalAssertions):
    def test_constant_speed_zero_motion_and_both_directions(self):
        with localcontext(ORACLE_CONTEXT):
            for direction in (-1, 1):
                for speed in (0, 4, 200):
                    initial = ref.MotionState("0.7", speed)
                    for elapsed in (D(0), D("1e-12"), D(2), D(86400)):
                        with self.subTest(direction=direction, speed=speed, elapsed=elapsed):
                            state = ref.evaluate_segment(initial, speed, "0.001", direction, elapsed)
                            self.assertEqual(state.speed_rad_s, speed)
                            self.assert_decimal_close(state.angle_rad, D("0.7") + direction * speed * elapsed)
                            if not elapsed:
                                self.assertIs(state, initial)

    def test_half_life_has_half_the_speed_difference(self):
        # At one half-life, the decaying speed difference is halved. Integrating
        # the ODE gives displacement = target*h + tau*(initial-final speed).
        with localcontext(ORACLE_CONTEXT):
            for tau in map(D, ("0.001", "0.01", "0.1", "1", "10", "60")):
                elapsed = tau * D(2).ln()
                for initial_speed, target in ((0, 38), (38, 0), (200, 4)):
                    for direction in (-1, 1):
                        expected_speed = D(initial_speed + target) / 2
                        expected_angle = D("0.9") + direction * (
                            target * elapsed + tau * (initial_speed - expected_speed))
                        state = ref.evaluate_segment(ref.MotionState("0.9", initial_speed),
                                                     target, tau, direction, elapsed)
                        self.assert_decimal_close(state.speed_rad_s, expected_speed)
                        self.assert_decimal_close(state.angle_rad, expected_angle)

    def test_integrated_ode_balance_and_complementary_trajectories(self):
        with localcontext(ORACLE_CONTEXT):
            for tau in map(D, ("0.001", "0.1", "1", "60")):
                for z in map(D, ("1e-12", "1e-6", "0.01", "0.5", "1", "10", "100")):
                    elapsed = tau * z
                    up = ref.evaluate_segment(ref.MotionState(0, 0), 38, tau, 1, elapsed)
                    down = ref.evaluate_segment(ref.MotionState(0, 38), 0, tau, 1, elapsed)
                    self.assert_decimal_close(up.speed_rad_s + down.speed_rad_s, 38)
                    self.assert_decimal_close(up.angle_rad + down.angle_rad, 38 * elapsed)
                    self.assert_decimal_close(up.angle_rad,
                                              38 * elapsed - tau * up.speed_rad_s,
                                              absolute="1e-65")
                    self.assert_decimal_close(down.angle_rad,
                                              tau * (38 - down.speed_rad_s),
                                              absolute="1e-65")

    def test_tiny_start_from_rest_retains_quadratic_displacement(self):
        # Taylor remainder bounds, independent of the reference's exp/remainder
        # helper: 1-z/3 <= angle/(target*h*h/(2*tau)) <= 1 for 0<z<1.
        with localcontext(ORACLE_CONTEXT):
            tau, target = D("0.45"), D(38)
            for exponent in (6, 12, 30, 60, 100):
                elapsed = D(10) ** -exponent
                state = ref.evaluate_segment(ref.MotionState(0, 0), target, tau, -1, elapsed)
                self.assertGreater(state.speed_rad_s, 0)
                self.assertLess(state.angle_rad, 0)
                ratio = -state.angle_rad / (target * elapsed * elapsed / (2 * tau))
                self.assertGreaterEqual(ratio, 1 - elapsed / (3 * tau) - D("1e-75"))
                self.assertLessEqual(ratio, 1 + D("1e-75"))

    def test_long_decay_retains_nonzero_tail_and_finite_distance(self):
        with localcontext(ORACLE_CONTEXT):
            state = ref.evaluate_segment(ref.MotionState(0, 38), 0, 1, 1, 1000)
            self.assertGreater(state.speed_rad_s, 0)
            # Rescaling the surviving tail tests underflow/cancellation; the
            # independent context has 40 guard digits beyond the implementation.
            self.assert_decimal_close(state.speed_rad_s * D(1000).exp(), 38)
            self.assert_decimal_close(state.angle_rad, 38)

    def test_full_epoch_decay_remains_in_the_admitted_reference_domain(self):
        # The log of the tail is the integrated logarithmic decay rate. This
        # admits a compact Decimal exponent; no enormous decimal string is built.
        with localcontext(ORACLE_CONTEXT):
            state = ref.evaluate_segment(ref.MotionState(0, 38), 0, ".001", 1, 86400)
            self.assertGreater(state.speed_rad_s, 0)
            self.assert_decimal_close(state.speed_rad_s.ln(), D(38).ln() - D(86400000))
            self.assert_decimal_close(state.angle_rad, D(".038"))

    def test_independent_rk4_solution_converges_at_fourth_order(self):
        reference = ref.evaluate_segment(ref.MotionState("0.9", 55), 4, "0.41", -1, "0.73")
        expected = float(reference.speed_rad_s), float(reference.angle_rad)
        errors = []
        for steps in (32, 64, 128):
            measured = rk4_motion(55.0, 0.9, 4.0, 0.41, -1, 0.73, steps)
            errors.append(max(abs(a - b) for a, b in zip(measured, expected)))
        self.assertLess(errors[-1], 1e-7)
        for coarse, fine in zip(errors, errors[1:]):
            self.assertGreater(coarse / fine, 14)
            self.assertLess(coarse / fine, 18)

    def test_thousand_subdivisions_preserve_the_motion_semigroup(self):
        rng = random.Random(20261113)
        with localcontext(ORACLE_CONTEXT):
            intervals = [D(rng.randrange(1, 60000)) / 1000000 for _ in range(1000)]
            initial = ref.MotionState("1.25", 0)
            state = initial
            for interval in intervals:
                state = ref.evaluate_segment(state, 38, "0.45", -1, interval)
            whole = ref.evaluate_segment(initial, 38, "0.45", -1, sum(intervals))
            self.assert_decimal_close(state.speed_rad_s, whole.speed_rad_s)
            self.assert_decimal_close(state.angle_rad, whole.angle_rad)

    def test_negative_history_and_zero_time_command(self):
        with localcontext(ORACLE_CONTEXT):
            for direction in (-1, 1):
                timeline = ref.RotorTimeline(ref.MotionProfile(4, 38, "0.4", "0.7", direction),
                                             "0.3", 20, events=[ref.CommandEvent(0, "tremolo")])
                for time in (D("-86400"), D("-0.05"), D("-1e-20")):
                    state = timeline.state_at(time)
                    self.assertEqual(state.speed_rad_s, 20)
                    self.assert_decimal_close(state.angle_rad, D("0.3") + direction * 20 * time)
                    self.assertEqual(timeline.command_at(time), "chorale")
                self.assertEqual(timeline.command_at(0), "tremolo")
                self.assertEqual(timeline.state_at(0), timeline.initial)

    def test_tied_and_redundant_events_preserve_the_anchor(self):
        profile = ref.MotionProfile(4, 38, "0.4", "0.7", 1)
        simple = [("0.25", "tremolo"), ("0.75", "chorale")]
        redundant = [("0", "chorale"), ("0.1", "chorale"), ("0.25", "tremolo"),
                     ("0.25", "tremolo"), ("0.5", "tremolo"), ("0.75", "tremolo"),
                     ("0.75", "chorale"), ("0.75", "tremolo"), ("0.75", "chorale"),
                     ("0.9", "chorale")]
        histories = [ref.RotorTimeline(profile, 0, 4, events=[ref.CommandEvent(*e) for e in rows])
                     for rows in (simple, redundant)]
        self.assertEqual(histories[0].segments, histories[1].segments)
        self.assertEqual(len(histories[1].segments), 3)
        for time in ("-0.1", "0", "0.25", "0.4", "0.75", "2", "86400"):
            self.assertEqual(histories[0].state_at(time), histories[1].state_at(time))

    def test_reversals_choose_tau_from_target_minus_current_speed(self):
        profile = ref.MotionProfile(4, 38, "0.04", "0.2", 1)
        events = [ref.CommandEvent(t, c) for t, c in
                  (("0.01", "tremolo"), ("0.02", "chorale"), ("1", "tremolo"))]
        timeline = ref.RotorTimeline(profile, 0, 100, events=events)
        self.assertEqual([s.tau_s for s in timeline.segments],
                         list(map(D, ("0.2", "0.2", "0.2", "0.04"))))
        with localcontext(ORACLE_CONTEXT):
            epsilon = D("1e-20")
            for event in events:
                before, at, after = [timeline.state_at(event.time_s + d)
                                     for d in (-epsilon, D(0), epsilon)]
                self.assertLess(abs(before.angle_rad - at.angle_rad), D("2e-18"))
                self.assertLess(abs(after.angle_rad - at.angle_rad), D("2e-18"))
                self.assertLess(abs(after.speed_rad_s - before.speed_rad_s), D("1e-16"))

    def test_large_turn_count_and_exact_frame_time(self):
        with localcontext(ORACLE_CONTEXT):
            for turns in (-(2**63), 2**63 - 1):
                timeline = ref.RotorTimeline(ref.MotionProfile(0, 0, 1, 1, -1),
                                             "0.125", 0, initial_turns=turns)
                phase, returned_turns = timeline.state_at(86400).wrapped()
                self.assertEqual(returned_turns, turns)
                self.assert_decimal_close(phase, D("0.125"), absolute="1e-59")
            for rate in ref.SUPPORTED_RATES:
                boundary = 86400 * rate
                self.assertEqual(ref.frame_time(boundary, rate), D(86400))
                self.assert_decimal_close(ref.frame_time(boundary - 1, rate),
                                          D(86400) - D(1) / rate)

    def test_private_decimal_context_covers_complete_public_evaluation(self):
        def snapshot():
            profile = ref.MotionProfile("4.1", "38.2", "0.43", "0.79", -1)
            timeline = ref.RotorTimeline(profile, "0.2", "4.3",
                                         events=[ref.CommandEvent("0.0123", "tremolo")])
            path = ref.solve_retarded_path(timeline, ref.CircularGeometry((0, 0, 0), "0.18"),
                                          ("0.7", "1.2", "0.3"), "0.125")
            return (ref.decimal_value(0.1), ref.frame_time(123456789, 44100),
                    timeline.state_at("-0.1").as_dict(), timeline.state_at("86400").as_dict(),
                    path.as_dict())
        expected = snapshot()
        with localcontext() as context:
            context.prec, context.rounding = 1, ROUND_UP
            context.Emin, context.Emax = -9, 9
            context.traps[Inexact] = context.traps[Rounded] = True
            flags = context.flags.copy()
            actual = snapshot()
            self.assertEqual(context.flags, flags)
        self.assertEqual(actual, expected)

    def test_malformed_scalar_motion_and_history_inputs_reject(self):
        for value in (True, " 1", "1_0", "nan", "Infinity", "", float("nan"), D("Infinity"), "1e1000001"):
            with self.subTest(value=value), self.assertRaises(ref.ReferenceError):
                ref.decimal_value(value)
        for direction in (0, True, 1.0, 2):
            with self.assertRaises(ref.ReferenceError):
                ref.MotionProfile(4, 38, 1, 1, direction)
        for args in ((40, 38, 1, 1, 1), (4, 38, 0, 1, 1), (4, 201, 1, 1, 1)):
            with self.assertRaises(ref.ReferenceError):
                ref.MotionProfile(*args)
        profile = ref.MotionProfile(4, 38, 1, 1, 1)
        for events in ([ref.CommandEvent(2, "chorale"), ref.CommandEvent(1, "tremolo")], [object()]):
            with self.assertRaises(ref.ReferenceError):
                ref.RotorTimeline(profile, 0, 4, events=events)
        for phase in ("-0.1", ref.TWO_PI):
            with self.assertRaises(ref.ReferenceError):
                ref.RotorTimeline(profile, phase, 4)
        for frame, rate in ((True, 48000), (0, True), (0, 32000), (48000 * 86400 + 1, 48000)):
            with self.assertRaises(ref.ReferenceError):
                ref.frame_time(frame, rate)


class PathTests(DecimalAssertions):
    def test_cardinal_positions_velocities_and_incoming_bearing(self):
        geometry = ref.CircularGeometry((1, 2, 3), "0.2")
        with localcontext(ORACLE_CONTEXT):
            phases = (D(0), ref.TWO_PI / 4, ref.TWO_PI / 2, 3 * ref.TWO_PI / 4)
        expected = (((1.2, 2, 3), (0, .6, 0)), ((1, 2.2, 3), (-.6, 0, 0)),
                    ((.8, 2, 3), (0, -.6, 0)), ((1, 1.8, 3), (.6, 0, 0)))
        for phase, (position, velocity) in zip(phases, expected):
            for direction in (-1, 1):
                actual_p, actual_v = ref.circular_state(geometry, ref.MotionState(phase, 3), direction)
                for actual, wanted in zip(actual_p, position):
                    self.assertAlmostEqual(actual, wanted, delta=3e-16)
                for actual, wanted in zip(actual_v, velocity):
                    self.assertAlmostEqual(actual, direction * wanted, delta=3e-16)
        self.assertEqual(ref.microphone_incidence((0, -1, 0), (0, 1, 0)), 1)
        self.assertEqual(ref.microphone_incidence((0, 1, 0), (0, 1, 0)), -1)
        self.assertEqual(ref.microphone_incidence((1, 0, 0), (0, 1, 0)), 0)
        with self.assertRaises(ref.ReferenceError):
            ref.microphone_incidence((0, 2, 0), (0, 1, 0))

    def test_static_three_four_five_geometry_delay_and_gain(self):
        geometry, timeline = ref.CircularGeometry((1, 2, 3), 0), constant_timeline(38)
        for c in (300, 343, 380):
            for observation in ("-0.25", "0", "86400"):
                path = ref.solve_retarded_path(timeline, geometry, (4, 6, 3), observation, c, "2.5")
                self.assertEqual(path.distance_m, 5)
                self.assertEqual(path.doppler_ratio, 1)
                self.assertEqual(path.pressure_gain, .5)
                self.assertAlmostEqual(path.delay_s, 5 / c, delta=1e-14)
                with localcontext(ORACLE_CONTEXT):
                    expected_emission = D(observation) - D.from_float(path.delay_s)
                self.assert_decimal_close(path.emission_time_s, expected_emission)
                self.assertLessEqual(abs(path.residual_s), ref.REFERENCE_RESIDUAL_S)

    def test_on_axis_motion_has_constant_distance_and_no_doppler(self):
        timeline = ref.RotorTimeline(ref.MotionProfile(4, 38, ".45", ".8", -1), 0, 4,
                                     events=[ref.CommandEvent(".03", "tremolo")])
        geometry = ref.CircularGeometry((0, 0, ".8"), ".18")
        for observation in ("-.5", "0", ".123", "100", "86400"):
            path = ref.solve_retarded_path(timeline, geometry, (0, 0, "1.04"), observation)
            self.assertAlmostEqual(path.distance_m, .3, delta=1e-15)
            self.assertAlmostEqual(path.delay_s, .3 / 343, delta=1e-14)
            self.assertAlmostEqual(path.doppler_ratio, 1, delta=2e-16)

    def test_near_and_far_endpoints_require_negative_cosine_term(self):
        geometry = ref.CircularGeometry((0, 0, 0), ".2")
        with localcontext(ORACLE_CONTEXT):
            opposite = ref.TWO_PI / 2
        for phase, distance in ((0, 1.0), (opposite, 1.4)):
            path = ref.solve_retarded_path(constant_timeline(0, phase=phase), geometry, ("1.2", 0, 0), 0)
            self.assertAlmostEqual(path.distance_m, distance, delta=3e-16)
            self.assertAlmostEqual(path.delay_s, distance / 343, delta=1e-14)
        near, far = ref.distance_bounds(geometry, ("1.2", 0, 0))
        self.assertAlmostEqual(near, 1.0, delta=3e-16)
        self.assertAlmostEqual(far, 1.4, delta=3e-16)

    def test_constructed_emission_at_tangent_reaches_both_mach_limits(self):
        # At e=0 the source is (1,0,0), the receiver is (1,1,0),
        # and velocity is (0,+/-75,0). The known flight time is 1/300.
        with localcontext(ORACLE_CONTEXT):
            observation = D(1) / 300
        for direction, ratio in ((1, 4 / 3), (-1, .8)):
            path = ref.solve_retarded_path(constant_timeline(75, direction),
                                          ref.CircularGeometry((0, 0, 0), 1), (1, 1, 0),
                                          observation, 300, residual_tolerance_s=1e-16)
            self.assertAlmostEqual(float(path.emission_time_s), 0, delta=1.4e-16)
            self.assertAlmostEqual(path.distance_m, 1, delta=2e-14)
            self.assertAlmostEqual(path.doppler_ratio, ratio, delta=3e-15)
            self.assertAlmostEqual(path.pressure_gain, 1, delta=2e-14)

    def test_constructed_quarter_turn_emission_recovers_known_time(self):
        with localcontext(ORACLE_CONTEXT):
            speed = 2 * ref.TWO_PI
            emission = D(".125")
            observation = emission + D(1) / 343
        path = ref.solve_retarded_path(constant_timeline(speed),
                                      ref.CircularGeometry((0, 0, 0), ".2"), (1, ".2", 0),
                                      observation, residual_tolerance_s=1e-16)
        self.assertAlmostEqual(float(path.emission_time_s), .125, delta=1.4e-16)
        self.assertAlmostEqual(path.distance_m, 1, delta=2e-15)
        self.assertAlmostEqual(path.doppler_ratio, 1 / (1 + .2 * float(speed) / 343), delta=2e-15)

    def test_mirror_rotation_and_translation_preserve_propagation(self):
        positive, negative = constant_timeline(38, 1), constant_timeline(38, -1)
        scene = ref.CircularGeometry((0, 0, 0), ".18")
        reference = ref.solve_retarded_path(positive, scene, (.7, 1.2, .3), ".123")
        mirrored = ref.solve_retarded_path(negative, scene, (.7, -1.2, .3), ".123")
        translated = ref.solve_retarded_path(positive, ref.CircularGeometry((2, -1, .5), ".18"),
                                            (2.7, .2, .8), ".123")
        for result in (mirrored, translated):
            self.assertAlmostEqual(result.delay_s, reference.delay_s, delta=2e-14)
            self.assertAlmostEqual(result.distance_m, reference.distance_m, delta=2e-12)
            self.assertAlmostEqual(result.doppler_ratio, reference.doppler_ratio, delta=2e-13)

    def test_receiver_after_command_uses_emission_before_command(self):
        profile = ref.MotionProfile(4, 38, ".45", ".8", 1)
        changed = ref.RotorTimeline(profile, 0, 4, events=[ref.CommandEvent(".1", "tremolo")])
        unchanged = ref.RotorTimeline(profile, 0, 4)
        args = (ref.CircularGeometry((0, 0, 0), ".18"), (0, 1.2, 0), ".1001")
        actual, expected = (ref.solve_retarded_path(timeline, *args) for timeline in (changed, unchanged))
        self.assertLess(actual.emission_time_s, D(".1"))
        self.assertGreater(changed.state_at(".1001").speed_rad_s, 4)
        self.assertEqual(actual, expected)

    def test_startup_path_uses_constant_negative_time_history(self):
        profile = ref.MotionProfile(4, 38, ".45", ".8", -1)
        changed = ref.RotorTimeline(profile, ".4", 4, "tremolo")
        unchanged = ref.RotorTimeline(profile, ".4", 4, "chorale")
        args = (ref.CircularGeometry((0, 0, 0), ".18"), (0, 1.2, 0), ".001")
        actual, expected = (ref.solve_retarded_path(timeline, *args) for timeline in (changed, unchanged))
        self.assertLess(actual.emission_time_s, 0)
        self.assertGreater(changed.state_at(".001").speed_rad_s, 4)
        self.assertEqual(actual, expected)

    def test_doppler_ratio_agrees_with_converging_emission_time_derivative(self):
        geometry, microphone = ref.CircularGeometry((0, 0, 0), ".2"), (1.1, .7, .4)
        with localcontext(ORACLE_CONTEXT):
            time = D(".057")
            for direction in (-1, 1):
                timeline = constant_timeline(38, direction, ".4")

                def query(t):
                    return ref.solve_retarded_path(timeline, geometry, microphone, t,
                                                  residual_tolerance_s=1e-16)

                center = query(time)
                errors = []
                for step in map(D, (".0001", ".00005", ".000025", ".0000125")):
                    derivative = (query(time + step).emission_time_s -
                                  query(time - step).emission_time_s) / (2 * step)
                    errors.append(abs(float(derivative) - center.doppler_ratio))
                self.assertLess(errors[-1], 2e-8)
                for coarse, fine in zip(errors, errors[1:]):
                    self.assertGreater(coarse / fine, 3.5)
                    self.assertLess(coarse / fine, 4.5)

    def test_bisection_reports_budget_failure_and_rejects_invalid_envelopes(self):
        timeline, geometry = constant_timeline(38), ref.CircularGeometry((0, 0, 0), ".2")
        with self.assertRaisesRegex(ref.ReferenceError, "residual/causality"):
            ref.solve_retarded_path(timeline, geometry, (1.2, .5, 0), ".123", max_iterations=1)
        for microphone in ((.2, 0, 0), (.219, 0, 0), (10, 10, 10)):
            # The last geometry uses the opposite corner to exceed 20 m.
            selected = ref.CircularGeometry((-10, -10, -10), ".2") if microphone == (10, 10, 10) else geometry
            with self.assertRaises(ref.ReferenceError):
                ref.solve_retarded_path(timeline, selected, microphone, 0)
        with self.assertRaises(ref.ReferenceError):
            ref.solve_retarded_path(constant_timeline(math.nextafter(75, math.inf)),
                                    ref.CircularGeometry((0, 0, 0), 1), (1, 1, 0), 0, 300)
        for options in ({"max_iterations": 0}, {"max_iterations": 97}, {"max_iterations": True},
                        {"residual_tolerance_s": 0}, {"residual_tolerance_s": float("nan")},
                        {"residual_tolerance_s": True}):
            with self.assertRaises(ref.ReferenceError):
                ref.solve_retarded_path(timeline, geometry, (1, 1, 0), 0, **options)

    def test_causal_monotone_emission_and_finite_serialized_paths(self):
        timeline = ref.RotorTimeline(ref.MotionProfile(4, 38, ".01", ".1", -1), ".4", 4,
                                     events=[ref.CommandEvent(".02", "tremolo"), ref.CommandEvent(".07", "chorale")])
        geometry, previous = ref.CircularGeometry((0, 0, 0), ".18"), None
        for index in range(21):
            time = ref.frame_time(index * 240, 48000)
            path = ref.solve_retarded_path(timeline, geometry, (.7, 1.2, .3), time)
            self.assertLess(path.emission_time_s, time)
            if previous is not None:
                self.assertGreater(path.emission_time_s, previous)
            previous = path.emission_time_s
            self.assertLessEqual(abs(path.residual_s), 1e-14)
            self.assertLessEqual(path.iterations, 96)
            self.assertLessEqual(.75, path.derivative)
            self.assertLessEqual(path.derivative, 1.25)
            self.assertGreaterEqual(path.bracket_width_s, 0)
            json.dumps(path.as_dict(), allow_nan=False)


class SceneAndCliTests(DecimalAssertions):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory(prefix="hammond-rotary-reference-test-")
        self.addCleanup(self.scratch.cleanup)
        self.directory = Path(self.scratch.name)

    def cli(self, *arguments, profile=PROFILE, expected_status="complete"):
        command = [sys.executable, "-B", str(SCRIPT)]
        if profile is not None:
            command += ["--profile", str(profile)]
        command += list(arguments)
        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        environment.pop("PYTHONPATH", None)
        before = {p.relative_to(self.directory) for p in self.directory.rglob("*")}
        result = subprocess.run(command, cwd=self.directory, env=environment, text=True,
                                capture_output=True, timeout=15, check=False)
        self.assertEqual(result.returncode, 0 if expected_status == "complete" else 2, result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], expected_status)
        self.assertEqual(before, {p.relative_to(self.directory) for p in self.directory.rglob("*")})
        return payload

    def test_scene_is_immutable_and_horn_drum_histories_are_independent(self):
        normalized = normalized_profile(load_profile(PROFILE))
        scene = ref.scene_from_normalized(normalized,
            {"horn": (ref.CommandEvent(0, "tremolo"),), "drum": ()})
        self.assertGreater(scene.timelines["horn"].state_at(1).speed_rad_s,
                           scene.timelines["horn"].initial.speed_rad_s)
        self.assertEqual(scene.timelines["drum"].state_at(1).speed_rad_s,
                         scene.timelines["drum"].initial.speed_rad_s)
        original_radius = scene.geometries["horn"].radius_m
        normalized["rotors"]["horn"]["radius_m"] = .9
        self.assertEqual(scene.geometries["horn"].radius_m, original_radius)
        with self.assertRaises(TypeError):
            scene.timelines["horn"] = scene.timelines["drum"]
        with self.assertRaises(FrozenInstanceError):
            scene.geometries["horn"].radius_m = .9
        with self.assertRaises(ref.ReferenceError):
            ref.scene_from_normalized(normalized, {"horn": ()})
        normalized["model_id"] = "different-model"
        with self.assertRaises(ref.ReferenceError):
            ref.scene_from_normalized(normalized)

    def test_cli_records_exact_input_digests_boundaries_and_query_times(self):
        events = self.directory / "events.json"
        event_bytes = b'{"schema_version":1,"events":[{"frame":0,"rotor":"horn","command":"tremolo"}]}'
        events.write_bytes(event_bytes)
        payload = self.cli("--events", str(events), "--paths", "--sample-rate", "48000",
                           "--start-frame", "23999", "--frames", "3")
        self.assertEqual(payload["reference_id"], "decimal-motion-cartesian-bisection-rotary-reference-v1")
        self.assertEqual(payload["model_id"], "nominal-effective-mouth-rotary-v1")
        self.assertEqual(payload["contract_id"], "rotary-numerics-v1")
        self.assertEqual(payload["profile_file_sha256"], hashlib.sha256(PROFILE.read_bytes()).hexdigest())
        self.assertEqual(payload["event_file_sha256"], hashlib.sha256(event_bytes).hexdigest())
        self.assertEqual(payload["physical_status"], "unmeasured")
        self.assertFalse(payload["algorithmic_latency_applied"])
        self.assertEqual(payload["path_geometry_precision"], "binary64")
        self.assertEqual(payload["motion_precision_digits"], 80)
        for frame, row in zip(range(23999, 24002), payload["queries"]):
            self.assertEqual(D(row["observation_time_s"]), ref.frame_time(frame, 48000))
            self.assertEqual(set(row["paths"]), {"horn:left", "horn:right", "drum:left", "drum:right"})
            self.assertEqual(set(row["states"]), {"horn", "drum"})
        exact = self.cli("--time", "0", "--time", "0.0000000000000000000000001")
        self.assertEqual(D(exact["queries"][1]["observation_time_s"]), D("1e-25"))

    def test_cli_digest_changes_with_file_bytes_without_changing_the_scene(self):
        reformatted = self.directory / "reformatted.json"
        reformatted.write_text(json.dumps(json.loads(PROFILE.read_text()), separators=(",", ":")), encoding="utf-8")
        original, compact = self.cli("--time", ".125", "--paths"), self.cli("--time", ".125", "--paths", profile=reformatted)
        self.assertNotEqual(original["profile_file_sha256"], compact["profile_file_sha256"])
        self.assertEqual(compact["profile_file_sha256"], hashlib.sha256(reformatted.read_bytes()).hexdigest())
        self.assertEqual(original["queries"], compact["queries"])

    def test_event_loader_preserves_ties_and_rejects_strict_json_errors(self):
        events = self.directory / "events.json"
        rows = [{"frame": 0, "rotor": "horn", "command": command} for command in ("tremolo", "chorale", "tremolo")]
        good = {"schema_version": 1, "events": rows}
        events.write_text(json.dumps(good), encoding="utf-8")
        loaded, digest = ref.load_events(events, 48000)
        self.assertEqual([event.command for event in loaded["horn"]], [row["command"] for row in rows])
        self.assertEqual(loaded["drum"], ())
        self.assertEqual(digest, hashlib.sha256(events.read_bytes()).hexdigest())
        invalid_bytes = [b"", b"\xff", b'{"schema_version":1,"schema_version":1,"events":[]}',
                         b'{"schema_version":NaN,"events":[]}',
                         b'{"schema_version":1,"events":[{"frame":0,"frame":1,"rotor":"horn","command":"chorale"}]}']
        invalid_objects = [{"schema_version": True, "events": []}, {"schema_version": 1, "events": {}},
                           {"schema_version": 1, "events": [], "extra": 1}]
        for field, value in (("frame", True), ("frame", 1.0), ("frame", -1), ("frame", 4147200001),
                             ("rotor", "both"), ("rotor", []), ("command", "stop"), ("extra", 0)):
            row = dict(rows[0])
            row[field] = value
            invalid_objects.append({"schema_version": 1, "events": [row]})
        invalid_objects.append({"schema_version": 1, "events": [dict(rows[0], frame=2), dict(rows[0], frame=1)]})
        invalid_objects.append({"schema_version": 1, "events": rows * 1366})
        for data in invalid_bytes + [json.dumps(obj).encode() for obj in invalid_objects]:
            with self.subTest(data=data[:100]):
                events.write_bytes(data)
                with self.assertRaises(ref.ReferenceError):
                    ref.load_events(events, 48000)
        events.write_text('{"schema_version":1,"events":[]}', encoding="utf-8")
        with self.assertRaises(ref.ReferenceError):
            ref.load_events(events, True)
        with events.open("wb") as stream:
            stream.truncate(ref.MAX_EVENT_BYTES + 1)
        with self.assertRaises(ref.ReferenceError):
            ref.load_events(events, 48000)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "regular-file admission check requires POSIX FIFO")
    def test_event_loader_rejects_nonregular_file_without_waiting(self):
        fifo = self.directory / "events.fifo"
        os.mkfifo(fifo)
        # O_NONBLOCK admission must reject before any blocking read.
        self.cli("--events", str(fifo), expected_status="rejected")

    def test_cli_errors_are_json_rejections_and_leave_no_output_files(self):
        bad_events = self.directory / "bad-events.json"
        bad_events.write_text('{"schema_version":1,"events":[{"frame":true,"rotor":"horn","command":"chorale"}]}', encoding="utf-8")
        cases = (("--time", "NaN"), ("--time", " 1"), ("--time", "1_0"), ("--time", "86400.1"),
                 ("--sample-rate", "32000"), ("--time", "0", "--frames", "1"), ("--step", "0"),
                 ("--frames", "0"), ("--start-frame", "-48001"),
                 ("--start-frame", "4147200000", "--frames", "2"),
                 ("--events", str(self.directory / "absent.json")), ("--events", str(bad_events)), ("--unknown",))
        for arguments in cases:
            with self.subTest(arguments=arguments):
                payload = self.cli(*arguments, expected_status="rejected")
                self.assertIsInstance(payload["error"], str)
                self.assertNotIn("queries", payload)
        self.cli(profile=None, expected_status="rejected")
        bad_profile = self.directory / "bad-profile.json"
        bad_profile.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
        self.cli(profile=bad_profile, expected_status="rejected")

    def test_reference_import_uses_no_production_or_profile_numerical_code(self):
        code = "\n".join((
            "import importlib.util, json, pathlib, sys",
            f"path = pathlib.Path({str(SCRIPT)!r})",
            "spec = importlib.util.spec_from_file_location('isolated_reference', path)",
            "module = importlib.util.module_from_spec(spec)",
            "sys.modules[spec.name] = module",
            "spec.loader.exec_module(module)",
            "module.evaluate_segment(module.MotionState(0, 0), 38, '.45', 1, '.1')",
            "root = path.parent.parent",
            "local = {name: str(pathlib.Path(m.__file__).resolve()) for name, m in tuple(sys.modules.items()) if getattr(m, '__file__', None) and pathlib.Path(m.__file__).resolve().is_relative_to(root)}",
            "print(json.dumps(local, sort_keys=True))"))
        result = subprocess.run([sys.executable, "-I", "-B", "-c", code], cwd=self.directory,
                                capture_output=True, text=True, timeout=15, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(json.loads(result.stdout), {"isolated_reference": str(SCRIPT)})
        self.assertEqual(list(self.directory.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
