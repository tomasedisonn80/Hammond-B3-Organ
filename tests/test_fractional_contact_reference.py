"""Independent known-answer checks for the offline contact reference.

The expected trajectories below use exact hand-chosen binary fractions. The
small discrete convolution oracle derives cell integrals and weights directly
from the frozen equations; it imports no candidate numerical helper. This is
not the separately required 36-fixture continuous-quadrature admission study.
"""

from __future__ import annotations

from fractions import Fraction as Q
import math
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import fractional_contact_reference as candidate


RATE = 48000
PRESS = 1 / 2048  # Full travel is exactly 375/16 host frames.
RELEASE = 1 / 1024  # Full travel is exactly 375/8 host frames.


def key(name="A", *, on=(0.5,) * 9, off=(0.375,) * 9,
        gains=(1.0,) + (0.0,) * 8, press=PRESS, release=RELEASE):
    return candidate.Key(name, press, release, on, off, (7,) * 9, gains)


def command(u, target, name="A"):
    """Convert only exactly representable coordinates chosen by these tests."""
    frame = math.floor(u)
    fraction = float(u - frame)
    assert Q(frame) + Q.from_float(fraction) == u
    return candidate.Target(frame, fraction, name, target)


def case(*, frames=48, keys=None, targets=None, source=None):
    return candidate.Case(
        RATE, frames,
        (source or candidate.Source(7, 0.0, 1.0, 0.25),),
        keys or (key(),),
        targets if targets is not None else (command(Q(0), 1.0),),
    )


def independent_weights(factor):
    """Full signed-index formula, without candidate symmetry/cache helpers."""
    values = []
    for index in range(-16 * factor, 16 * factor + 1):
        v = index / factor
        if abs(v) == 16:
            values.append(0.0)
            continue
        angle = 0.9 * math.pi * v
        sinc = 1.0 if index == 0 else math.sin(angle) / angle
        window = 0.42 + 0.5 * math.cos(math.pi * v / 16)
        window += 0.08 * math.cos(math.pi * v / 8)
        values.append(0.9 * sinc * window)
    total = math.fsum(values)
    return tuple(value / total for value in values)


def independent_rectangle_samples(frames, factor, intervals):
    """Exact DC interval lengths precede the independently computed FIR."""
    cells = []
    for index in range(frames * factor + 1):
        left, right = Q(2 * index - 1, 2 * factor), Q(2 * index + 1, 2 * factor)
        pieces = [float(max(Q(0), min(right, stop) - max(left, start)) * factor) * gain
                  for start, stop, gain in intervals]
        cells.append(math.fsum(pieces))
    weights = independent_weights(factor)
    radius = 16 * factor
    result = []
    for n in range(-16, frames + 17):
        low = max(0, n * factor - radius)
        high = min(len(cells) - 1, n * factor + radius)
        result.append(math.fsum(cells[j] * weights[n * factor - j + radius]
                                for j in range(low, high + 1)))
    return tuple(result)


class FractionalContactKnownAnswers(unittest.TestCase):
    def test_exact_half_travel_make_release_and_holds(self):
        fixture = case(targets=(command(Q(0), 0.5), command(Q(16), 0.0)))
        trajectory = candidate.build_trajectory(fixture)
        expected = tuple((Q(375, 32), 0, i, True) for i in range(9))
        expected += tuple((Q(1399, 64), 0, i, False) for i in range(9))
        self.assertEqual(trajectory.edges, expected)
        self.assertEqual(trajectory.final_keys, ((Q(0), Q(0), (False,) * 9),))
        self.assertEqual(trajectory.segments, (
            (0, Q(0), Q(375, 32), Q(0), Q(16, 375), Q(1, 2)),
            (0, Q(375, 32), Q(16), Q(1, 2), Q(0), Q(1, 2)),
            (0, Q(16), Q(631, 16), Q(1, 2), Q(-8, 375), Q(0)),
            (0, Q(631, 16), Q(48), Q(0), Q(0), Q(0)),
        ))

    def test_incoming_equality_precedes_stable_no_time_commands(self):
        tie = Q(375, 32)
        fixture = case(frames=20, keys=(key("A"), key("B")), targets=(
            command(Q(0), 1.0, "A"), command(Q(0), 1.0, "B"),
            command(tie, 0.0, "A"), command(tie, 1.0, "A"),
            command(tie, 1.0, "B"), command(tie, 0.0, "B"),
        ))
        trajectory = candidate.build_trajectory(fixture)
        expected = tuple((tie, k, i, True) for k in range(2) for i in range(9))
        expected += tuple((Q(1125, 64), 1, i, False) for i in range(9))
        self.assertEqual(trajectory.edges, expected)
        self.assertEqual(trajectory.final_keys[0], (Q(64, 75), Q(1), (True,) * 9))
        self.assertEqual(trajectory.final_keys[1], (Q(97, 300), Q(0), (False,) * 9))

    def test_repeated_target_does_not_rebase_moving_or_held_segments(self):
        original = case(targets=(command(Q(0), 0.75), command(Q(32), 0.0)))
        repeated = original._replace(targets=(
            command(Q(0), 0.75), command(Q(2), 0.75), command(Q(10), 0.75),
            command(Q(24), 0.75), command(Q(32), 0.0), command(Q(38), 0.0),
        ))
        self.assertEqual(candidate.build_trajectory(original),
                         candidate.build_trajectory(repeated))

    def test_same_partial_hold_retains_direction_history(self):
        on = (0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.8125, 0.875, 0.9375)
        off = tuple(value - 0.125 for value in on)
        k = key(on=on, off=off)
        below = case(frames=80, keys=(k,), targets=(command(Q(0), 0.5625),))
        above = below._replace(targets=(command(Q(0), 1.0), command(Q(32), 0.5625)))
        lower_state = candidate.build_trajectory(below).final_keys[0]
        upper_state = candidate.build_trajectory(above).final_keys[0]
        self.assertEqual(lower_state, (Q(9, 16), Q(9, 16), (True,) * 4 + (False,) * 5))
        self.assertEqual(upper_state, (Q(9, 16), Q(9, 16), (True,) * 5 + (False,) * 4))

    def test_clipped_arrival_does_not_replace_full_velocity_root(self):
        trajectory = candidate.build_trajectory(case(targets=(command(Q(0), 0.51),)))
        arrival = Q(375, 16) * Q.from_float(0.51)
        self.assertEqual(math.floor(arrival), 11)
        self.assertEqual(trajectory.segments[0].u1, arrival)
        self.assertEqual(trajectory.segments[0].velocity_per_host_frame, Q(16, 375))
        self.assertEqual(tuple(edge.u for edge in trajectory.edges), (Q(375, 32),) * 9)
        self.assertEqual(trajectory.final_keys[0].position, Q.from_float(0.51))

    def test_unsorted_equal_thresholds_keep_independent_muted_contacts(self):
        on = (0.75, 0.25, 0.5, 0.25, 0.875, 0.5, 0.125, 0.75, 1.0)
        k = key(on=on, off=tuple(value / 2 for value in on), gains=(0.0,) * 9)
        trajectory = candidate.build_trajectory(case(keys=(k,)))
        expected = sorted((Q.from_float(value) * Q(375, 16), 0, i, True)
                          for i, value in enumerate(on))
        self.assertEqual(trajectory.edges, tuple(expected))
        self.assertEqual(trajectory.final_keys[0].closed9, (True,) * 9)

    def test_distinct_exact_roots_with_one_display_keep_tiny_interval(self):
        k = key(press=1 / 256, release=1 / 512,
                on=(1.0,) * 9, off=(math.nextafter(1.0, 0.0),) * 9)
        start = Q(375, 2)
        stop = start + Q(375, 2**55)
        fixture = case(frames=188, keys=(k,), targets=(
            command(Q(0), 1.0), command(start, 0.0),
        ))
        rendered = candidate.render(fixture, 32)
        self.assertGreater(stop, start)
        self.assertEqual(float(start), float(stop))
        self.assertEqual(rendered.trajectory.edges,
                         tuple((start, 0, i, True) for i in range(9))
                         + tuple((stop, 0, i, False) for i in range(9)))
        # Both boundaries lie in the cell centered at 187.5. This sample
        # depends on its nonzero exact width even though float endpoints agree.
        expected = float((stop - start) * 32) * independent_weights(32)[16 * 32 - 16]
        actual = candidate.read_samples(rendered, 187, 1)[0]
        self.assertGreater(actual, 0.0)
        self.assertAlmostEqual(actual / expected, 1.0, delta=2e-14)

    def test_empty_flush_applies_last_target_without_motion_or_filter(self):
        fixture = case(frames=0, targets=(command(Q(0), 1.0), command(Q(0), 0.25)))
        with patch.object(candidate, "_filter_coefficients", side_effect=AssertionError("filter used")), \
                patch.object(candidate, "_cells", side_effect=AssertionError("cells used")):
            rendered = candidate.render(fixture, 256)
        self.assertEqual(rendered.trajectory, ((), (), ((Q(0), Q(1, 4), (False,) * 9),)))
        self.assertEqual((rendered.first_frame, rendered.samples, rendered.bound, rendered.work),
                         (0, (), 1.0, 13))
        self.assertEqual(candidate.read_samples(rendered, 0, 0), ())
        with self.assertRaises(ValueError):
            candidate.read_samples(rendered, 0, 1)

    def test_endpoint_edge_then_command_changes_target_but_not_contact(self):
        # P=1/256 gives full travel 187.5; shifting onset .5 makes arrival N=188.
        fixture = case(frames=188, keys=(key(press=1 / 256, on=(1.0,) * 9),),
                       targets=(command(Q(1, 2), 1.0), command(Q(188), 0.0)))
        rendered = candidate.render(fixture, 32)
        self.assertEqual(rendered.trajectory.edges,
                         tuple((Q(188), 0, i, True) for i in range(9)))
        self.assertEqual(rendered.trajectory.final_keys[0], (Q(1), Q(0), (True,) * 9))
        self.assertEqual(rendered.samples, (0.0,) * 221)

    def test_dc_fractional_switching_and_entire_observation_tail(self):
        fixture = case(targets=(command(Q(0), 1.0), command(Q(48), 0.0)))
        rendered = candidate.render(fixture, 32)
        expected = independent_rectangle_samples(48, 32, ((Q(375, 32), Q(48), 1.0),))
        self.assertEqual((rendered.first_frame, len(rendered.samples)), (-16, 81))
        self.assertLessEqual(max(abs(a - b) for a, b in zip(rendered.samples, expected)), 2e-14)
        self.assertEqual((rendered.samples[0], rendered.samples[-1]), (0.0, 0.0))
        self.assertEqual(candidate.read_samples(rendered, -5, 1), (0.0,))
        self.assertNotEqual(candidate.read_samples(rendered, -4, 1), (0.0,))
        self.assertNotEqual(candidate.read_samples(rendered, 49, 1), (0.0,))
        self.assertAlmostEqual(candidate.read_samples(rendered, 30, 1)[0], 1.0, delta=2e-14)
        self.assertEqual(rendered.trajectory.final_keys[0], (Q(1), Q(0), (True,) * 9))

    def test_signed_shared_routes_preserve_small_surviving_signal(self):
        tiny = 2.0**-80
        fixture = case(frames=64, keys=(key(gains=(1.0, tiny, -1.0) + (0.0,) * 6),))
        rendered = candidate.render(fixture, 32)
        expected = independent_rectangle_samples(64, 32, ((Q(375, 32), Q(64), tiny),))
        self.assertLessEqual(max(abs(a - b) / tiny for a, b in zip(rendered.samples, expected)), 2e-14)
        self.assertAlmostEqual(candidate.read_samples(rendered, 40, 1)[0] / tiny, 1.0, delta=2e-14)
        self.assertEqual(len(rendered.trajectory.edges), 9)

    def test_sine_integral_known_antiderivatives_and_absolute_phase(self):
        source = candidate.Source(7, 6000.0, 0.75, 0.0)
        self.assertAlmostEqual(candidate.sine_integral(source, RATE, 0, 2), 3 / math.pi, delta=2e-15)
        self.assertAlmostEqual(candidate.sine_integral(source, RATE, 1, 3),
                               3 * math.sqrt(2) / math.pi, delta=2e-15)
        self.assertAlmostEqual(candidate.sine_integral(source, RATE, 0, 8), 0.0, delta=2e-15)
        self.assertEqual(candidate.sine_integral(source, RATE, Q(7, 4), Q(7, 4)), 0.0)
        value, slope = candidate.source_value_and_slope(source, RATE, 8)
        self.assertAlmostEqual(value, 0.0, delta=2e-15)
        self.assertAlmostEqual(slope / (0.75 * 12000 * math.pi), 1.0, delta=2e-15)
        dc = candidate.Source(7, 0.0, 0.5, 0.25)
        a, b = Q(375, 2), Q(375, 2) + Q(1, 2**60)
        self.assertEqual(float(a), float(b))
        self.assertEqual(candidate.sine_integral(dc, RATE, a, b), 2.0**-61)

    def test_late_note_uses_common_source_origin(self):
        # A delay of four host frames is half the eight-frame source period.
        source = candidate.Source(7, 6000.0, 0.75, 0.125)
        first = case(frames=48, source=source)
        late = first._replace(frames=52, targets=(command(Q(4), 1.0),))
        a, b = candidate.render(first, 32), candidate.render(late, 32)
        # The observation gates are shifted by the same four frames. A source
        # restarted on note entry would produce the same sign, not its opposite.
        shifted = candidate.read_samples(b, -12, len(a.samples))
        self.assertLessEqual(max(abs(x + y) for x, y in zip(a.samples, shifted)), 2e-14)

    def test_mute_retains_trajectory_with_exact_zero_audio(self):
        fixture = case(keys=(key(gains=(0.0,) * 9),))
        rendered = candidate.render(fixture, 64)
        self.assertEqual(rendered.bound, 0.0)
        self.assertEqual(rendered.samples, (0.0,) * 81)
        self.assertEqual(len(rendered.trajectory.edges), 9)
        self.assertEqual(rendered.trajectory.final_keys[0].closed9, (True,) * 9)

    def test_complete_immutable_range_reads_preserve_tails(self):
        rendered = candidate.render(case(), 32)
        before = repr(rendered)
        for width in (1, 7, 64, len(rendered.samples)):
            pieces = []
            for offset in range(0, len(rendered.samples), width):
                pieces.extend(candidate.read_samples(rendered, -16 + offset,
                                                      min(width, len(rendered.samples) - offset)))
            self.assertEqual(tuple(pieces), rendered.samples)
        cuts = (-16, -4, 0, 11, 12, 47, 48, 49, 65)
        pieces = tuple(value for lo, hi in zip(cuts, cuts[1:])
                       for value in candidate.read_samples(rendered, lo, hi - lo))
        self.assertEqual(pieces, rendered.samples)
        self.assertEqual(candidate.read_samples(rendered, -16, 0), ())
        self.assertEqual(candidate.read_samples(rendered, 65, 0), ())
        self.assertEqual(repr(rendered), before)
        with self.assertRaises(TypeError):
            rendered.samples[0] = 1.0
        with self.assertRaises(AttributeError):
            rendered.first_frame = 0
        for start, count in ((-17, 0), (65, 1), (-16, 82), (True, 0), (-16, False)):
            with self.subTest(start=start, count=count), self.assertRaises(ValueError):
                candidate.read_samples(rendered, start, count)

    def test_kernel_rejects_mutable_and_colliding_times_at_both_entries(self):
        ordinary = case()
        colliding = (command(Q(1), 1.0), candidate.Target(1, 2.0**-54, "A", 0.0))
        nearby = (candidate.Target(1, 0.5, "A", 1.0),
                  candidate.Target(1, math.nextafter(0.5, 1.0), "A", 0.0))
        invalid = (
            list(ordinary), ordinary._replace(keys=list(ordinary.keys)),
            ordinary._replace(frames=True), ordinary._replace(targets=colliding),
            ordinary._replace(targets=nearby),
        )
        for fixture in invalid:
            for entry in (candidate.build_trajectory, lambda value: candidate.render(value, 32)):
                with self.subTest(fixture=repr(fixture)[:70], entry=entry), self.assertRaises(ValueError):
                    entry(fixture)

    def test_work_rejection_precedes_numerical_allocation(self):
        fixture = case(frames=4096)
        with patch.object(candidate, "_build_trajectory", side_effect=AssertionError("trajectory used")), \
                patch.object(candidate, "_filter_coefficients", side_effect=AssertionError("filter used")), \
                patch.object(candidate, "_cells", side_effect=AssertionError("cells used")):
            with self.assertRaisesRegex(ValueError, "work bound"):
                candidate.render(fixture, 256)


if __name__ == "__main__":
    unittest.main()
