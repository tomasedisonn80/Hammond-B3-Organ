#!/usr/bin/env python3
"""Exact native/oracle replay for the synthetic causal-contact-grid-v1 model.

Run through CTest, or set HAMMOND_CAUSAL_CONTACT_GRID_PROBE_EXECUTABLE to the
coherently built native probe. Unset, empty, missing or nonexecutable probe
configuration fails setup; native execution must not silently skip. Expected
results come solely from the independent piecewise-path Fraction oracle. This
file never imports or reads the candidate C++ implementation.

``encode_case(case, partitions=None)`` is the reusable, validation-free CGGRID1
wire serializer for this suite and independent CLI rejection tests. The native
probe closes every observation, including truncated causal-prefix observations.
"""

from __future__ import annotations

import copy
from fractions import Fraction
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "tests" / "reference"))
from causal_contact_grid_reference import evaluate_case


TICKS = 65536
FULL = 1 << 48
MAX_SPEED = (1 << 32) - 1
RATES = (44100, 48000, 96000)
MAX_REPORT_BYTES = 2 * 1024 * 1024
RANDOM_SEED = 0xCA05A1


def encode_case(case, partitions=None):
    """Serialize explicit grid values without silently validating/coercing them.

    The caller may deliberately supply invalid values for native CLI tests.
    Default partitioning is one block, or no blocks when frames is zero.
    """
    if partitions is None:
        partitions = [case["frames"]] if case["frames"] else []
    partitions = list(partitions)
    keys, targets = case["keys"], case.get("targets", [])
    lines = [" ".join(map(str, ("CGGRID1", case["sample_rate_hz"], len(keys),
                                 case["frames"], len(targets), len(partitions))))]
    for key in keys:
        fields = [key["press_units_per_tick"], key["release_units_per_tick"]]
        for contact in key["contacts"]:
            fields.extend((contact["off"], contact["on"]))
        lines.append(" ".join(map(str, fields)))
    for command in targets:
        lines.append(" ".join(map(str, (command["tick"], command["key_index"],
                                         command["position"]))))
    if partitions:
        lines.append(" ".join(map(str, partitions)))
    return ("\n".join(lines) + "\n").encode("ascii")


def key_config(press=1, release=1, contacts=None):
    if contacts is None:
        contacts = [(0, 1)] * 9
    return {"press_units_per_tick": press, "release_units_per_tick": release,
            "contacts": [{"off": off, "on": on} for off, on in contacts]}


def target(tick, position, key_index=0):
    return {"tick": tick, "key_index": key_index, "position": position}


def make_case(*commands, frames=1, keys=None, rate=48000):
    return {"sample_rate_hz": rate, "frames": frames,
            "keys": [key_config()] if keys is None else keys,
            "targets": list(commands)}


def exact_time(edge):
    time = edge["time"]
    return Fraction(time["tick"]) + Fraction(time["numerator"], time["denominator"])


def partition_variants(frames):
    if not frames:
        return [()]
    irregular = []
    remaining, index = frames, 0
    pattern = (2, 1, 7, 3, 5)
    while remaining:
        length = min(remaining, pattern[index % len(pattern)])
        irregular.append(length)
        remaining -= length
        index += 1
    # Preserve order while eliminating duplicate partitions of short epochs.
    return list(dict.fromkeys(((frames,), (1,) * frames, tuple(irregular))))


def unique_object(pairs):
    result = {}
    for name, value in pairs:
        if name in result:
            raise ValueError(f"duplicate JSON field: {name}")
        result[name] = value
    return result


class CausalContactGridDifferential(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        configured = os.environ.get("HAMMOND_CAUSAL_CONTACT_GRID_PROBE_EXECUTABLE")
        if not configured:
            raise RuntimeError(
                "native causal-grid probe unavailable: build "
                "hammond_causal_contact_grid_probe and set "
                "HAMMOND_CAUSAL_CONTACT_GRID_PROBE_EXECUTABLE, or run CTest")
        cls.probe = Path(configured).resolve()
        if not cls.probe.is_file() or not os.access(cls.probe, os.X_OK):
            raise RuntimeError(f"configured native causal-grid probe unavailable: {cls.probe}")

    def assert_exact(self, actual, expected, path="report"):
        # Python ordinarily equates True with 1 and 1.0 with 1. The wire contract
        # requires the actual field types as well as every exact scalar value.
        self.assertIs(type(actual), type(expected), f"{path}: field type")
        if isinstance(expected, dict):
            self.assertEqual(set(actual), set(expected), f"{path}: fields")
            for name, value in expected.items():
                self.assert_exact(actual[name], value, f"{path}.{name}")
        elif isinstance(expected, list):
            self.assertEqual(len(actual), len(expected), f"{path}: length")
            for index, (observed, value) in enumerate(zip(actual, expected)):
                self.assert_exact(observed, value, f"{path}[{index}]")
        else:
            self.assertEqual(actual, expected, path)

    def replay(self, case, partitions=None, expected=None):
        if partitions is None:
            partitions = (case["frames"],) if case["frames"] else ()
        partitions = tuple(partitions)
        if expected is None:
            expected = evaluate_case(case, close_observation=True)
        result = subprocess.run([str(self.probe)], input=encode_case(case, partitions),
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                cwd=ROOT, timeout=10, check=False)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        self.assertEqual(result.stderr, b"")
        self.assertLessEqual(len(result.stdout), MAX_REPORT_BYTES)
        self.assertTrue(result.stdout.endswith(b"\n"))

        def reject_noninteger(value):
            raise ValueError(f"noninteger JSON number: {value}")

        try:
            actual = json.loads(result.stdout, object_pairs_hook=unique_object,
                                parse_float=reject_noninteger, parse_constant=reject_noninteger)
        except ValueError as error:
            self.fail(f"native report is not strict integer JSON: {error}")

        edge_times = [exact_time(edge) for edge in expected["edges"]]
        cursor = offset = 0
        blocks = []
        for frames in partitions:
            cursor += frames
            previous = offset
            while offset < len(edge_times) and edge_times[offset] <= cursor * TICKS:
                offset += 1
            blocks.append({"frames": frames, "cursor_frames": cursor,
                           "edges_written": offset - previous})
        self.assertEqual(offset, len(expected["edges"]), "fixture partitions omit edges")
        wanted = {"schema_version": 1, **expected, "blocks": blocks}
        self.assert_exact(actual, wanted)
        return actual

    def replay_partitions(self, case, partitions=None):
        expected = evaluate_case(case, close_observation=True)
        choices = partition_variants(case["frames"]) if partitions is None else partitions
        reports = []
        for blocks in choices:
            try:
                reports.append(self.replay(case, blocks, expected))
            except self.failureException as error:
                raise self.failureException(
                    f"partition blocks={len(blocks)}, first={tuple(blocks[:8])}: {error}"
                ) from error
        for report in reports[1:]:
            self.assert_exact(report["edges"], reports[0]["edges"], "partition.edges")
            self.assert_exact(report["snapshot"], reports[0]["snapshot"], "partition.snapshot")
        return reports[0]

    def test_all_rates_preserve_integer_motion_and_full_padding(self):
        contacts = [(0, 1), (5, 12), (3, 12), (10, 21), (0, 7),
                    (31, 37), (99, 123), (0, TICKS), (TICKS, 2 * TICKS + 1)]
        base = make_case(target(0, 2 * TICKS, 1), target(0, 3 * TICKS),
                         target(4, 19), target(4, 19), target(23, 300000),
                         target(TICKS - 1, 0, 1), target(TICKS, 11),
                         target(2 * TICKS, 3 * TICKS, 1), target(3 * TICKS, 0),
                         target(7 * TICKS, FULL, 1), frames=7,
                         keys=[key_config(7, 11, contacts), key_config(3, 2, contacts)])
        trajectories = []
        for rate in RATES:
            with self.subTest(rate=rate):
                case = {**base, "sample_rate_hz": rate}
                report = self.replay_partitions(case)
                normalized = copy.deepcopy(report["snapshot"])
                normalized["config"]["sample_rate_hz"] = 0
                trajectories.append((report["edges"], normalized))
        self.assertEqual(trajectories[0], trajectories[1])
        self.assertEqual(trajectories[0], trajectories[2])

    def test_integer_near_integer_and_reduced_fractional_arrivals(self):
        for rate in RATES:
            for speed in (1, 2, 3, 6, 65537, MAX_SPEED):
                with self.subTest(rate=rate, speed=speed):
                    ons = [1, max(1, speed - 1), speed, speed + 1, 2 * speed,
                           2 * speed + 1, 3 * speed - 1, 3 * speed, 3 * speed + 1]
                    contacts = [((on - 1) // 2, on) for on in ons]
                    case = make_case(target(0, 3 * speed + 1),
                                     target(4, 3 * speed + 1), target(9, 3 * speed + 1),
                                     target(10, 0), target(20, 0), target(TICKS, 1),
                                     keys=[key_config(speed, max(1, speed - 1), contacts)],
                                     rate=rate)
                    report = self.replay(case)
                    closing = [edge for edge in report["edges"] if edge["closed_after"]]
                    self.assertEqual([exact_time(edge) for edge in closing],
                                     sorted(Fraction(on, speed) for on in ons))
                    self.assertEqual(len(closing), 9)

    def test_distinct_rationals_with_the_same_display_double(self):
        # Key 1 must precede key 0, although converting either whole root to
        # binary64 gives the same value. Denominator cross-products approach 2^64.
        for anchor, frames in ((0, 1), (2048 * TICKS, 2049)):
            for rate in RATES:
                with self.subTest(anchor=anchor, rate=rate):
                    speeds = (MAX_SPEED - 1, MAX_SPEED)
                    roots = [Fraction(anchor + 1) + Fraction(1, speed) for speed in speeds]
                    self.assertNotEqual(roots[0], roots[1])
                    self.assertEqual(float(roots[0]), float(roots[1]))
                    case = make_case(target(anchor, speeds[0] + 2),
                                     target(anchor, speeds[1] + 2, 1), frames=frames,
                                     keys=[key_config(speed, speed, [(0, speed + 1)] * 9)
                                           for speed in speeds], rate=rate)
                    report = self.replay_partitions(case)
                    self.assertEqual([edge["key_index"] for edge in report["edges"]],
                                     [1] * 9 + [0] * 9)
                    self.assertEqual(exact_time(report["edges"][0]), roots[1])
                    self.assertEqual(exact_time(report["edges"][-1]), roots[0])

    def test_equal_time_key_contact_order_and_incoming_reversal_ties(self):
        order = [4, 1, 2, 1, 6, 4, 7, 2, 3]
        keys = [key_config(speed, speed,
                           [((on - 1) * speed, on * speed) for on in order])
                for speed in (3, 6, 9, 12)]
        commands = [target(0, 7 * keys[index]["press_units_per_tick"], index)
                    for index in reversed(range(4))]
        for index in reversed(range(4)):
            commands.extend((target(7, 0, index), target(7, FULL, index),
                             target(7, 0, index)))
        commands.extend(target(2 * TICKS, FULL, index) for index in reversed(range(4)))
        for rate in RATES:
            with self.subTest(rate=rate):
                report = self.replay_partitions(make_case(*commands, frames=2, keys=keys, rate=rate))
                at_reversal = [edge for edge in report["edges"] if exact_time(edge) == 7]
                self.assertEqual([(edge["key_index"], edge["contact_index"], edge["closed_after"])
                                  for edge in at_reversal],
                                 [(index, 6, True) for index in range(4)])
                self.assertEqual(report["snapshot"]["command_count"], len(commands))

    def test_repeated_targets_preserve_original_anchors_during_motion_and_hold(self):
        for destination in (10, FULL):
            contacts = [(0, 10), (TICKS, 3 * TICKS), (TICKS, 6 * TICKS),
                        (1, 3), (4, 7), (0, 1), (0, FULL), (0, 10), (2, 11)]
            commands = [target(tick, destination) for tick in
                        (0, 1, 4, TICKS - 1, TICKS, TICKS + 1, 2 * TICKS, 3 * TICKS)]
            with self.subTest(destination=destination):
                report = self.replay_partitions(make_case(*commands, frames=3,
                                                         keys=[key_config(3, 2, contacts)]))
                state = report["snapshot"]["keys"][0]
                self.assertEqual((state["anchor_tick"], state["anchor_position"]), (0, 0))
                self.assertEqual(state["position"], min(destination, 9 * TICKS))
                self.assertEqual(state["target"], destination)

    def test_endpoint_equality_tied_changes_and_partial_hysteretic_holds(self):
        contacts = [(0, 3 * TICKS), (5 * TICKS, 6 * TICKS), (TICKS, 3 * TICKS),
                    (TICKS, 6 * TICKS), (0, 1), (3 * TICKS, 7 * TICKS),
                    (2 * TICKS, 3 * TICKS), (0, FULL), (TICKS, 6 * TICKS)]
        case = make_case(target(0, FULL), target(TICKS, FULL), target(TICKS, 0),
                         target(TICKS, FULL), target(2 * TICKS, 0),
                         target(2 * TICKS + 1, 3 * TICKS),
                         target(2 * TICKS + 17, 3 * TICKS), target(4 * TICKS, 0),
                         frames=4, keys=[key_config(3, 2, contacts)])
        report = self.replay_partitions(case)
        self.assertEqual(report["snapshot"]["keys"][0]["position"], 3 * TICKS)
        self.assertEqual(report["snapshot"]["keys"][0]["anchor_tick"], 4 * TICKS)
        incoming = [edge for edge in report["edges"] if exact_time(edge) == 2 * TICKS]
        self.assertEqual([edge["contact_index"] for edge in incoming], [1, 3, 8])
        self.assertTrue(all(edge["closed_after"] for edge in incoming))

        hold = make_case(target(0, 15), target(7, 20), target(10, 15), target(13, 15),
                         target(17, 10), target(20, 15), target(25, 20), target(30, 0),
                         target(TICKS, 20), keys=[key_config(3, 5, [(10, 20)] * 9)])
        report = self.replay(hold)
        self.assertEqual([exact_time(edge) for edge in report["edges"][::9]],
                         [Fraction(26, 3), Fraction(18), Fraction(80, 3), Fraction(32)])

    def test_zero_frames_and_endpoint_only_command_limit(self):
        for rate in RATES:
            for count in range(1, 5):
                with self.subTest(rate=rate, key_count=count):
                    keys = [key_config(index + 1, MAX_SPEED - index,
                                       [(0, FULL)] * 9) for index in range(count)]
                    self.replay(make_case(frames=0, keys=keys, rate=rate))
                    commands = [target(0, (0, FULL, 1, FULL - 1)[index % 4], index % count)
                                for index in range(512)]
                    report = self.replay(make_case(*commands, frames=0, keys=keys, rate=rate))
                    self.assertEqual(report["edges"], [])
                    self.assertEqual(report["snapshot"]["command_count"], 512)
                    self.assertTrue(all(state["position"] == 0 and not any(state["closed"])
                                        for state in report["snapshot"]["keys"]))

    def test_maximum_epoch_speeds_positions_and_unreached_far_roots(self):
        contacts = [(0, FULL), (FULL - 1, FULL), (0, 1), (1, 2),
                    (MAX_SPEED - 1, MAX_SPEED), (MAX_SPEED, MAX_SPEED + 1),
                    (FULL // 2 - 1, FULL // 2), (FULL - 2, FULL - 1), (0, FULL)]
        keys = [key_config(1, MAX_SPEED, contacts), key_config(MAX_SPEED, 1, contacts),
                key_config(MAX_SPEED - 1, MAX_SPEED, contacts),
                key_config(65537, 65536, contacts)]
        commands = [target(0, FULL, index) for index in range(4)]
        commands += [target(TICKS, FULL, 1), target(TICKS, 0, 2),
                     target(TICKS, 0, 3), target(TICKS + 1, 0, 1),
                     target(2 * TICKS, FULL // 2, 3), target(4096 * TICKS, FULL, 2)]
        for rate in RATES:
            with self.subTest(rate=rate):
                report = self.replay_partitions(make_case(*commands, frames=4096, keys=keys, rate=rate))
                self.assertEqual(report["snapshot"]["keys"][0]["position"], 4096 * TICKS)
                self.assertFalse(report["snapshot"]["keys"][0]["closed"][0])
                self.assertEqual(report["snapshot"]["keys"][1]["anchor_position"], FULL)

    def test_actual_maximum_edges_and_command_budget_across_partitions(self):
        # Every supplied command starts one one-tick movement, each crossing all
        # nine contacts: 512 * 9 is the contract's exact attainable epoch bound.
        commands = [target(index * TICKS, 1 if index % 2 == 0 else 0)
                    for index in range(512)]
        for rate in RATES:
            with self.subTest(rate=rate):
                report = self.replay_partitions(make_case(*commands, frames=512, rate=rate))
                self.assertEqual(len(report["edges"]), 4608)
                self.assertEqual(report["snapshot"]["command_count"], 512)
                self.assertEqual(report["snapshot"]["edge_count"], 4608)
                self.assertEqual(exact_time(report["edges"][-1]), 511 * TICKS + 1)

        # Closing no-ops consume the same supplied-command budget without
        # rebasing a movement that began at zero or adding an edge.
        commands = [target(index, FULL) for index in range(511)]
        commands.append(target(2 * TICKS, FULL))
        report = self.replay_partitions(make_case(*commands, frames=2))
        self.assertEqual(report["snapshot"]["command_count"], 512)
        self.assertEqual(report["snapshot"]["keys"][0]["anchor_tick"], 0)
        self.assertEqual(len(report["edges"]), 9)

    def test_future_commands_cannot_revise_edges_through_prefix_equality(self):
        contacts = [(0, 3 * TICKS), (TICKS, 6 * TICKS), (0, 6 * TICKS),
                    (2 * TICKS, 3 * TICKS), (0, 1), (4 * TICKS, 9 * TICKS),
                    (0, 6 * TICKS), (TICKS, 3 * TICKS), (0, FULL)]
        keys = [key_config(3, 2, contacts), key_config(3, 5, contacts)]
        earlier = [target(0, FULL, 1), target(0, FULL), target(TICKS, FULL)]
        cursor = 2 * TICKS
        futures = [[], [target(cursor, 0), target(cursor, 0, 1)],
                   [target(cursor, 0, 1), target(cursor, FULL, 1), target(cursor, 0, 1),
                    target(cursor + 1, 0), target(3 * TICKS, FULL), target(5 * TICKS, FULL, 1)]]
        for rate in RATES:
            with self.subTest(rate=rate):
                prefix_case = make_case(*earlier, frames=2, keys=keys, rate=rate)
                prefix = self.replay_partitions(prefix_case)
                # The probe always closes. Explicitly check that this observation
                # represents the pre-closure oracle state except for its phase.
                active = evaluate_case(prefix_case, close_observation=False)
                active["snapshot"]["phase"] = "closed"
                self.assert_exact(prefix["snapshot"], active["snapshot"], "causal.prefix_snapshot")
                for future in futures:
                    with self.subTest(future_commands=len(future)):
                        case = make_case(*(earlier + future), frames=5, keys=keys, rate=rate)
                        report = self.replay_partitions(case, [(5,), (2, 3), (1, 1, 1, 1, 1)])
                        through_cursor = [edge for edge in report["edges"] if exact_time(edge) <= cursor]
                        self.assert_exact(through_cursor, prefix["edges"], "causal.prefix_edges")
                self.assertTrue(any(exact_time(edge) == cursor for edge in prefix["edges"]))

    def test_seeded_mixed_command_replays_with_unsorted_thresholds(self):
        rng = random.Random(RANDOM_SEED)
        speeds = (1, 2, 3, 5, 65535, 65536, 65537, MAX_SPEED - 1, MAX_SPEED)
        for fixture in range(24):
            frames = (2, 3, 7, 13, 31)[fixture % 5]
            end = frames * TICKS
            count = fixture % 4 + 1
            amplitude = (31, TICKS + 17, 16 * TICKS + 1, FULL)[fixture % 4]
            keys = []
            for _ in range(count):
                contacts = []
                for index in range(9):
                    on = (rng.choice(contacts)[1] if contacts and index % 3 == 0
                          else rng.randint(1, amplitude))
                    contacts.append((rng.randrange(on), on))
                rng.shuffle(contacts)
                keys.append(key_config(rng.choice(speeds), rng.choice(speeds), contacts))
            ticks = [0, 0, 1, TICKS - 1, TICKS, TICKS, TICKS + 1, end - 1, end]
            ticks += [rng.randrange(end + 1) for _ in range(35)]
            ticks.sort()
            previous = [0] * count
            commands = []
            for index, tick in enumerate(ticks):
                which = rng.randrange(count)
                contact = rng.choice(keys[which]["contacts"])
                destination = rng.choice((0, amplitude, contact["off"], contact["on"],
                                          previous[which], rng.randrange(amplitude + 1)))
                if index == 0:
                    destination = amplitude
                commands.append(target(tick, destination, which))
                previous[which] = destination
            case = make_case(*commands, frames=frames, keys=keys, rate=RATES[fixture % 3])
            with self.subTest(seed=RANDOM_SEED, fixture=fixture, rate=case["sample_rate_hz"],
                              key_count=count, frames=frames):
                self.replay_partitions(case)


if __name__ == "__main__":
    unittest.main()
