#!/usr/bin/env python3
"""Hand-derived self-tests for the independent integer-grid rational oracle."""

from __future__ import annotations

import copy
from fractions import Fraction
import json
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent / "reference"))
import causal_contact_grid_reference as reference


def key(press=1, release=1, off=0, on=1):
    return {"press_units_per_tick": press, "release_units_per_tick": release,
            "contacts": [{"off": off, "on": on} for _ in range(9)]}


def command(tick, position, key_index=0):
    return {"tick": tick, "key_index": key_index, "position": position}


def case(*targets, frames=1, keys=None, rate=48000):
    return {"sample_rate_hz": rate, "frames": frames,
            "keys": [key()] if keys is None else keys, "targets": list(targets)}


def edge(tick, contact_index, closed_after=True, *, numerator=0,
         denominator=1, key_index=0):
    return {"time": {"tick": tick, "numerator": numerator,
                     "denominator": denominator},
            "key_index": key_index, "contact_index": contact_index,
            "closed_after": closed_after}


class ContactGridReferenceTests(unittest.TestCase):
    def test_zero_frames_closes_without_travel_and_counts_endpoint_ties(self):
        actual = reference.evaluate_case(case(
            command(0, 10), command(0, 10), command(0, 0), command(0, 20), frames=0))
        self.assertEqual(actual["model_id"], "causal-contact-grid-v1")
        self.assertEqual(actual["edges"], [])
        state = actual["snapshot"]
        self.assertEqual((state["phase"], state["cursor_frames"],
                          state["command_count"], state["edge_count"]), ("closed", 0, 4, 0))
        self.assertEqual(state["keys"][0], {
            "position": 0, "target": 20, "anchor_position": 0,
            "anchor_tick": 0, "closed": [False] * 9})
        ready = reference.evaluate_case(case(frames=0), close_observation=False)
        self.assertEqual(ready["snapshot"]["phase"], "ready")
        self.assertEqual(ready["snapshot"]["command_count"], 0)

    def test_fractional_arrival_hold_and_asymmetric_release(self):
        # Rise 0 -> 10 at speed 3; on=10 is reached at 3+1/3.
        # Hold until 5, then fall at speed 2; off=1 is reached at 9+1/2.
        actual = reference.evaluate_case(case(command(0, 10), command(5, 0),
                                             keys=[key(3, 2, 1, 10)]))
        expected = [edge(3, i, numerator=1, denominator=3) for i in range(9)]
        expected += [edge(9, i, False, numerator=1, denominator=2) for i in range(9)]
        self.assertEqual(actual["edges"], expected)
        self.assertEqual(actual["snapshot"]["keys"][0], {
            "position": 0, "target": 0, "anchor_position": 10,
            "anchor_tick": 5, "closed": [False] * 9})
        self.assertEqual(actual["snapshot"]["edge_count"], 18)

    def test_repeated_unsorted_thresholds_and_partial_arrival(self):
        configuration = key(press=3)
        for contact, on in zip(configuration["contacts"], [6, 3, 6, 1, 9, 3, 12, 15, 9]):
            contact["on"] = on
        actual = reference.evaluate_case(case(command(0, 9), keys=[configuration]))
        self.assertEqual(actual["edges"], [
            edge(0, 3, numerator=1, denominator=3), edge(1, 1), edge(1, 5),
            edge(2, 0), edge(2, 2), edge(3, 4), edge(3, 8)])
        self.assertEqual(actual["snapshot"]["keys"][0]["closed"],
                         [True, True, True, True, True, True, False, False, True])

    def test_equal_roots_are_sorted_by_key_then_contact(self):
        # Caller command order is deliberately the opposite of equal-edge order.
        actual = reference.evaluate_case(case(command(0, 1, 1), command(0, 1, 0),
                                             keys=[key(), key()]))
        self.assertEqual(actual["edges"],
                         [edge(1, i, key_index=k) for k in range(2) for i in range(9)])

    def test_incoming_command_and_reversal_equality(self):
        for incoming_target in (3, 10):
            with self.subTest(incoming_target=incoming_target):
                actual = reference.evaluate_case(case(
                    command(0, incoming_target), command(3, 0), keys=[key(off=1, on=3)]))
                self.assertEqual(actual["edges"],
                                 [edge(3, i) for i in range(9)] +
                                 [edge(5, i, False) for i in range(9)])
                self.assertEqual(actual["snapshot"]["keys"][0]["anchor_position"], 3)

    def test_endpoint_edge_precedes_closure_and_closure_does_not_release(self):
        configuration = key(off=32768, on=65536)
        actual = reference.evaluate_case(case(command(0, 131072), command(65536, 0),
                                             keys=[configuration]))
        self.assertEqual(actual["edges"], [edge(65536, i) for i in range(9)])
        self.assertEqual(actual["snapshot"]["keys"][0], {
            "position": 65536, "target": 0, "anchor_position": 65536,
            "anchor_tick": 65536, "closed": [True] * 9})
        extended = reference.evaluate_case(case(command(0, 131072), command(65536, 0),
                                               frames=2, keys=[configuration]))
        self.assertEqual(extended["edges"], [edge(65536, i) for i in range(9)] +
                         [edge(98304, i, False) for i in range(9)])

    def test_partial_holds_keep_independent_hysteresis(self):
        # Target 3 first holds below on=4 while open; after reaching 6 it holds
        # at the same 3 while closed because off=2 has not been reached.
        actual = reference.evaluate_case(case(
            command(0, 3), command(10, 6), command(20, 3), command(30, 0),
            keys=[key(off=2, on=4)]))
        self.assertEqual(actual["edges"], [edge(11, i) for i in range(9)] +
                         [edge(31, i, False) for i in range(9)])

    def test_noop_preserves_anchor_and_tied_changes_reanchor(self):
        simple = case(command(0, 100), command(3, 100), keys=[key(on=50)])
        unchanged = reference.evaluate_case(simple)
        self.assertEqual((unchanged["snapshot"]["keys"][0]["anchor_tick"],
                          unchanged["snapshot"]["keys"][0]["anchor_position"]), (0, 0))
        changed = reference.evaluate_case(case(
            command(0, 100), command(3, 100), command(3, 0), command(3, 100),
            keys=[key(on=50)]))
        self.assertEqual(changed["edges"], unchanged["edges"])
        self.assertEqual((changed["snapshot"]["keys"][0]["anchor_tick"],
                          changed["snapshot"]["keys"][0]["anchor_position"]), (3, 3))
        self.assertEqual(changed["snapshot"]["command_count"], 4)
        stopped = reference.evaluate_case(case(command(0, 100), command(3, 3),
                                               keys=[key(on=50)]))
        self.assertEqual(stopped["edges"], [])
        self.assertEqual(stopped["snapshot"]["keys"][0]["position"], 3)

    def test_close_distinct_roots_do_not_collapse_to_display_time(self):
        start, maximum = 200000000, (1 << 32) - 1
        actual = reference.evaluate_case(case(
            command(start, 1, 0), command(start, 1, 1), frames=4096,
            keys=[key(press=maximum - 1), key(press=maximum)]))
        # The later root's smaller key index must not win the comparison.
        expected = [edge(start, i, numerator=1, denominator=maximum, key_index=1)
                    for i in range(9)]
        expected += [edge(start, i, numerator=1, denominator=maximum - 1, key_index=0)
                     for i in range(9)]
        self.assertEqual(actual["edges"], expected)
        first = Fraction(start) + Fraction(1, maximum)
        second = Fraction(start) + Fraction(1, maximum - 1)
        self.assertLess(first, second)
        self.assertEqual(float(first), float(second))

    def test_extreme_speed_full_travel_and_reduced_fraction(self):
        full, maximum = 1 << 48, (1 << 32) - 1
        actual = reference.evaluate_case(case(command(0, full), frames=2,
                                             keys=[key(maximum, maximum, 0, full)]))
        # 2^48 = (2^32-1)*65536 + 65536; gcd(65536, 2^32-1) = 1.
        self.assertEqual(actual["edges"],
                         [edge(65536, i, numerator=65536, denominator=maximum)
                          for i in range(9)])
        self.assertEqual(actual["snapshot"]["keys"][0]["position"], full)
        returned = reference.evaluate_case(case(command(0, full), command(131072, 0),
                                                frames=4,
                                                keys=[key(maximum, maximum, 0, full)]))
        self.assertEqual(returned["edges"], actual["edges"] +
                         [edge(196608, i, False, numerator=65536, denominator=maximum)
                          for i in range(9)])
        self.assertEqual(returned["snapshot"]["keys"][0]["position"], 0)
        reduced = reference.evaluate_case(case(command(0, 4), keys=[key(6, 1, 0, 4)]))
        self.assertEqual(reduced["edges"],
                         [edge(0, i, numerator=2, denominator=3) for i in range(9)])

    def test_unreached_future_root_and_last_epoch_tick(self):
        future = (1 << 32) + 1
        actual = reference.evaluate_case(case(command(0, future),
                                             keys=[key(off=1 << 32, on=future)]))
        self.assertEqual(actual["edges"], [])
        self.assertEqual(actual["snapshot"]["keys"][0]["position"], 65536)
        end = 1 << 28
        last = reference.evaluate_case(case(command(0, end), frames=4096,
                                            keys=[key(off=end - 1, on=end)]))
        self.assertEqual(last["edges"], [edge(end, i) for i in range(9)])

    def test_three_rates_share_tick_trajectory(self):
        outputs = []
        for rate in (44100, 48000, 96000):
            value = reference.evaluate_case(case(command(0, 10), command(5, 0),
                                                 keys=[key(3, 2, 1, 4)], rate=rate))
            self.assertEqual(value["snapshot"]["config"]["sample_rate_hz"], rate)
            value["snapshot"]["config"]["sample_rate_hz"] = 0
            outputs.append(value)
        self.assertEqual(outputs[0], outputs[1])
        self.assertEqual(outputs[1], outputs[2])

    def test_maximum_commands_and_edges_have_hand_derived_order(self):
        keys = [key() for _ in range(4)]
        for k, configuration in enumerate(keys):
            configuration["contacts"] = [{"off": 1 + 9 * k + c, "on": 100 - 9 * k - c}
                                          for c in range(9)]
        targets = [command(128 * j, 128 if j % 2 == 0 else 0, k)
                   for j in range(128) for k in range(4)]
        actual = reference.evaluate_case(case(*targets, keys=keys))
        expected = []
        for j in range(128):
            for flat in range(35, -1, -1):
                # On press x=t-start; on release x=128-(t-start).
                tick = 128 * j + (100 - flat if j % 2 == 0 else 127 - flat)
                expected.append(edge(tick, flat % 9, j % 2 == 0, key_index=flat // 9))
        self.assertEqual(actual["edges"], expected)
        self.assertEqual((actual["snapshot"]["command_count"],
                          actual["snapshot"]["edge_count"]), (512, 4608))
        for state in actual["snapshot"]["keys"]:
            self.assertEqual(state, {"position": 0, "target": 0, "anchor_position": 128,
                                     "anchor_tick": 16256, "closed": [False] * 9})

    def test_prefix_excludes_future_commands_and_retains_endpoint_edge(self):
        configuration = key(off=32768, on=65536)
        prefix = reference.evaluate_case(case(command(0, 131072), keys=[configuration]),
                                         close_observation=False)
        self.assertEqual(prefix["snapshot"]["phase"], "active")
        self.assertEqual(prefix["snapshot"]["keys"][0]["target"], 131072)
        future = reference.evaluate_case(case(
            command(0, 131072), command(65536, 0), command(65537, 131072),
            keys=[configuration], frames=2))
        early = [item for item in future["edges"] if item["time"]["tick"] <= 65536]
        self.assertEqual(prefix["edges"], early)

    def test_canonical_padding_and_json_output_do_not_alias_input(self):
        source = case(command(0, 2))
        source["fixture_id"] = "metadata-is-allowed"
        original = copy.deepcopy(source)
        actual = reference.evaluate_case(source)
        self.assertEqual(source, original)
        self.assertEqual(json.loads(json.dumps(actual)), actual)
        state = actual["snapshot"]
        self.assertEqual(state["config"]["key_count"], 1)
        self.assertEqual(len(state["keys"]), 4)
        self.assertEqual(len(state["config"]["keys"]), 4)
        for k in range(1, 4):
            self.assertEqual(state["keys"][k], {
                "position": 0, "target": 0, "anchor_position": 0,
                "anchor_tick": 0, "closed": [False] * 9})
            self.assertEqual(state["config"]["keys"][k], {
                "press_units_per_tick": 0, "release_units_per_tick": 0,
                "contacts": [{"off": 0, "on": 0} for _ in range(9)]})
        state["config"]["keys"][0]["contacts"][0]["on"] = 99
        state["keys"][1]["closed"][0] = True
        self.assertFalse(state["keys"][2]["closed"][0])
        self.assertEqual(source, original)
        self.assertEqual(reference.evaluate_case(source), reference.evaluate_case(original))

    def test_invalid_integer_domains_reject_bools_and_nonintegers(self):
        mutations = [
            (("sample_rate_hz",), value) for value in (True, 48000.0, 44099)
        ] + [
            (("frames",), value) for value in (-1, 4097, False, 1.0)
        ] + [
            (("keys", 0, name), value)
            for name in ("press_units_per_tick", "release_units_per_tick")
            for value in (0, (1 << 32), -1, True, 1.0)
        ] + [
            (("keys", 0, "contacts", 0, name), value)
            for name in ("off", "on") for value in (-1, (1 << 48) + 1, False, 1.0)
        ] + [
            (("targets", 0, name), value)
            for name, values in (("tick", (-1, 65537, True, 0.0)),
                                 ("key_index", (-1, 1, False, 0.0)),
                                 ("position", (-1, (1 << 48) + 1, True, 1.0)))
            for value in values
        ]
        for path, value in mutations:
            with self.subTest(path=path, value=value):
                source = case(command(0, 1))
                destination = source
                for component in path[:-1]:
                    destination = destination[component]
                destination[path[-1]] = value
                original = copy.deepcopy(source)
                with self.assertRaises(reference.OracleInputError):
                    reference.evaluate_case(source)
                self.assertEqual(source, original)

    def test_shape_threshold_count_order_and_endpoint_rejections(self):
        invalid = [None, {}, case(keys=[]), case(keys=[key()] * 5),
                   case(*[command(0, 0)] * 513), case(command(2, 1), command(1, 0))]
        for contacts in ([], [{"off": 0, "on": 1}] * 8,
                         [{"off": 0, "on": 1}] * 10,
                         [{"off": 1, "on": 1}] * 9,
                         [{"off": 2, "on": 1}] * 9):
            malformed = case()
            malformed["keys"][0]["contacts"] = contacts
            invalid.append(malformed)
        for malformed in invalid:
            with self.subTest(case=malformed):
                with self.assertRaises(reference.OracleInputError):
                    reference.evaluate_case(malformed)
        for source in (case(command(65536, 1)), case(command(0, 1), frames=0)):
            with self.assertRaises(reference.OracleInputError):
                reference.evaluate_case(source, close_observation=False)
        with self.assertRaises(reference.OracleInputError):
            reference.evaluate_case(case(), close_observation=1)
        missing_targets = case()
        del missing_targets["targets"]
        self.assertEqual(reference.evaluate_case(missing_targets)["edges"], [])

    def test_late_invalid_domain_precedes_earlier_order_violation(self):
        source = case(command(2, 1), command(1, 0), command(3, (1 << 48) + 1))
        with self.assertRaises(reference.OracleInputError) as caught:
            reference.evaluate_case(source)
        self.assertEqual(caught.exception.path, "targets[2].position")
        self.assertIn("targets[2].position", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
