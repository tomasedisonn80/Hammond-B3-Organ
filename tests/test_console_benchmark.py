#!/usr/bin/env python3
"""Actual bounded benchmark acceptance; no elapsed-time pass threshold."""

from __future__ import annotations

import copy
from fractions import Fraction
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


LEGACY_TOP = set("""block_frames build cases checksum_encoding clock clock_is_steady
clock_tick_seconds hard_realtime_guarantee host_underruns nominal_frame_interval_ns
profile_authoring_sha256_retained profile_id recorded_calls_per_case runtime_machine
sample_rate_hz schema scope seed status timer_overhead_subtracted
timing_threshold_applied warmup_calls_per_case warmup_included_in_timings""".split())
LEGACY_CASE = set("""active_keys call_time_ns end_frame event_offsets_per_call
events_consumed events_per_call final_source_phase_checksum
initial_selected_bank_drawbars name observed_max_interval_fraction
observed_p95_interval_fraction output_connected prepare_status processed_frames
recorded_calls recorded_rejected_calls recorded_status_counts sample_checksum
setup_events_consumed setup_status start_frame warmup_ok_calls""".split())
CONSOLE_TOP = LEGACY_TOP | {"source_model", "contact_model", "percussion_model",
                            "ownership_model", "workload_version"}
CONSOLE_CASE = LEGACY_CASE | set("""timed_api input_event_domain initial_percussion
initial_owner_count start_owner_count final_owner_count max_observed_owner_count
workload_owner_bound start_active_keys final_active_keys physical_events_consumed
warmup_events_consumed warmup_physical_events_consumed primary_key_midi
primary_key_manual recorded_primary_motion_calls recorded_primary_contact_edges
final_primary_position final_primary_target final_readiness""".split())


def reject_constant(value):
    raise ValueError(f"nonfinite JSON token: {value}")


def without_timings(report):
    result = copy.deepcopy(report)
    for case in result["cases"]:
        for key in ("call_time_ns", "observed_p95_interval_fraction",
                    "observed_max_interval_fraction"):
            del case[key]
    return result


def expected_console(name, rate, block, warmup, iterations):
    """Independent rational travel and owner-count schedule at call boundaries."""
    position = Fraction(0)
    contacts = [False] * 9
    result = {"physical": 0, "warmup_physical": 0, "motion": 0,
              "edges": 0, "max_owners": 0}
    for call in range(warmup + iterations):
        owned = name == "owned_input"
        phase = call % (4 if owned else 2)
        target = int(phase != 3 if owned else phase == 0)
        owners = (122, 244, 122, 0)[phase] if owned else 0
        physical = 122 if not owned or phase in (0, 3) else 0
        before = position
        if target > position:
            position = min(Fraction(target), position + Fraction(125 * block, rate))
        elif target < position:
            position = max(Fraction(target), position - Fraction(250 * block, 3 * rate))
        old_contacts = contacts[:]
        for index in range(9):
            if position >= Fraction(12 + 10 * index, 100):
                contacts[index] = True
            elif position <= Fraction(4 + 10 * index, 100):
                contacts[index] = False
        result["max_owners"] = max(result["max_owners"], owners)
        if call < warmup:
            result["warmup_physical"] += physical
            result["start_owners"] = owners
            result["start_active"] = 122 * target
        else:
            result["physical"] += physical
            result["motion"] += before != position
            result["edges"] += sum(a != b for a, b in zip(old_contacts, contacts))
    result.update(position=float(position), target=target, final_owners=owners,
                  final_active=122 * target)
    return result


class ConsoleBenchmarkTests(unittest.TestCase):
    calls = 0
    maximum_position_error = 0.0

    @classmethod
    def setUpClass(cls):
        for variable in ("HAMMOND_BENCHMARK_EXECUTABLE", "HAMMOND_TEST_PROFILE"):
            path = Path(os.environ.get(variable, ""))
            if not path.is_file():
                raise RuntimeError(f"Missing {variable}; build hammond_benchmark and configure CTest")
            setattr(cls, "binary" if variable.endswith("EXECUTABLE") else "profile", path.resolve())

    @classmethod
    def tearDownClass(cls):
        print(f"benchmark CLI calls: {cls.calls}; maximum rational-position error: "
              f"{cls.maximum_position_error:.17g}; no timing threshold applied")

    def invoke(self, arguments, **kwargs):
        type(self).calls += 1
        return subprocess.run([str(self.binary), *arguments], text=True,
                              stderr=subprocess.PIPE, timeout=30, **kwargs)

    def run_report(self, case=None, *, rate=48000, block=384, warmup=1, iterations=7, seed=71):
        arguments = ["--profile", str(self.profile), "--sample-rate", str(rate),
                     "--block-size", str(block), "--warmup", str(warmup),
                     "--iterations", str(iterations), "--seed", str(seed)]
        if case is not None:
            arguments += ["--case", case]
        run = self.invoke(arguments, stdout=subprocess.PIPE)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(run.stderr, "")
        self.assertLess(len(run.stdout), 32768)
        report = json.loads(run.stdout, parse_constant=reject_constant)
        self.assertEqual(report["status"], "ok")
        self.assertFalse(report["hard_realtime_guarantee"])
        self.assertFalse(report["timing_threshold_applied"])
        self.assertFalse(report["timer_overhead_subtracted"])
        self.assertFalse(report["warmup_included_in_timings"])
        self.assertIsNone(report["runtime_machine"])
        self.assertIsNone(report["host_underruns"])
        self.assertIsNone(report["build"]["source_revision"])
        self.assertIsNone(report["build"]["binary_sha256"])
        self.assertEqual(report["sample_rate_hz"], rate)
        self.assertEqual(report["block_frames"], block)
        self.assertEqual(report["seed"], seed)
        self.assertEqual(report["recorded_calls_per_case"], iterations)
        self.assertEqual(report["warmup_calls_per_case"], warmup)
        self.assertAlmostEqual(report["nominal_frame_interval_ns"], block / rate * 1e9,
                               delta=1e-6)
        for row in report["cases"]:
            self.assertEqual(row["recorded_status_counts"], {"ok": iterations})
            self.assertEqual(row["recorded_rejected_calls"], 0)
            self.assertEqual(row["recorded_calls"], iterations)
            self.assertEqual(row["warmup_ok_calls"], warmup)
            self.assertEqual(row["start_frame"], block * warmup)
            self.assertEqual(row["end_frame"], block * (warmup + iterations))
            self.assertEqual(row["processed_frames"], block * iterations)
            self.assertEqual(row["prepare_status"], "ok")
            self.assertEqual(row["setup_status"], "ok")
            self.assertRegex(row["final_source_phase_checksum"], r"^[0-9a-f]{16}$")
            times = row["call_time_ns"]
            self.assertEqual(set(times), {"min", "median", "p95", "max"})
            values = [times[key] for key in ("min", "median", "p95", "max")]
            self.assertTrue(all(math.isfinite(value) and value >= 0 for value in values))
            self.assertEqual(values, sorted(values))
            for key, statistic in (("observed_p95_interval_fraction", "p95"),
                                   ("observed_max_interval_fraction", "max")):
                self.assertAlmostEqual(row[key], times[statistic] / report["nominal_frame_interval_ns"],
                                       delta=1e-9)
        return report

    def check_console(self, report, rate, block, warmup, iterations):
        self.assertEqual(set(report), CONSOLE_TOP)
        self.assertEqual(report["schema"], "hammond-console-benchmark-v1")
        self.assertEqual(report["source_model"], "ideal-shared-sine-v1")
        self.assertEqual(report["contact_model"], "nominal-linear-travel-v1")
        self.assertEqual(report["percussion_model"], "shared-readiness-v1")
        self.assertEqual(report["ownership_model"], "bounded-fifo-note-ownership-v1")
        self.assertEqual(report["workload_version"], 1)
        for row in report["cases"]:
            with self.subTest(case=row["name"], rate=rate, block=block):
                self.assertEqual(set(row), CONSOLE_CASE)
                expected = expected_console(row["name"], rate, block, warmup, iterations)
                owned = row["name"] == "owned_input"
                self.assertEqual(row["timed_api"], "process_owned_notes" if owned else "Engine::process")
                self.assertEqual(row["input_event_domain"], "typed_host_notes" if owned else "physical_key_targets")
                self.assertEqual(row["initial_percussion"], "on_second_normal_fast")
                self.assertEqual(row["active_keys"], 0)
                self.assertEqual(row["initial_owner_count"], 0)
                self.assertEqual(row["setup_events_consumed"], 22)
                self.assertEqual(row["events_per_call"], 122)
                self.assertEqual(row["event_offsets_per_call"], 1)
                self.assertEqual(row["events_consumed"], 122 * iterations)
                self.assertEqual(row["physical_events_consumed"], expected["physical"])
                self.assertEqual(row["warmup_events_consumed"], 122 * warmup)
                self.assertEqual(row["warmup_physical_events_consumed"], expected["warmup_physical"])
                self.assertEqual(row["workload_owner_bound"], 244 if owned else 0)
                self.assertEqual(row["max_observed_owner_count"], expected["max_owners"])
                self.assertEqual(row["start_owner_count"], expected["start_owners"])
                self.assertEqual(row["final_owner_count"], expected["final_owners"])
                self.assertEqual(row["start_active_keys"], expected["start_active"])
                self.assertEqual(row["final_active_keys"], expected["final_active"])
                self.assertEqual(row["primary_key_midi"], 60)
                self.assertEqual(row["primary_key_manual"], "upper")
                self.assertEqual(row["recorded_primary_motion_calls"], expected["motion"])
                self.assertEqual(row["recorded_primary_contact_edges"], expected["edges"])
                self.assertEqual(row["final_primary_target"], expected["target"])
                error = abs(row["final_primary_position"] - expected["position"])
                type(self).maximum_position_error = max(type(self).maximum_position_error, error)
                self.assertLessEqual(error, 2e-14)
                self.assertTrue(0 <= row["final_readiness"] <= 1)
                self.assertTrue(row["output_connected"])
                self.assertRegex(row["sample_checksum"], r"^[0-9a-f]{16}$")
        self.assertEqual(len({row["final_source_phase_checksum"] for row in report["cases"]}), 1)

    def test_legacy_default_and_case_contract_remain_unchanged(self):
        defaults = self.invoke([], stdout=subprocess.PIPE)
        self.assertEqual(defaults.returncode, 0, defaults.stderr)
        self.assertEqual(defaults.stderr, "")
        default_report = json.loads(defaults.stdout, parse_constant=reject_constant)
        self.assertEqual((default_report["sample_rate_hz"], default_report["block_frames"],
                          default_report["warmup_calls_per_case"], default_report["recorded_calls_per_case"],
                          default_report["seed"]), (48000, 64, 16, 128, 0))
        self.assertEqual([row["name"] for row in default_report["cases"]],
                         ["silence", "all_keys", "disconnected", "dense_automation"])
        self.assertEqual(set(default_report), LEGACY_TOP)
        report = self.run_report(block=5, warmup=1, iterations=2)
        explicit = self.run_report("all", block=5, warmup=1, iterations=2)
        self.assertEqual(without_timings(report), without_timings(explicit))
        self.assertEqual(set(report), LEGACY_TOP)
        self.assertEqual(report["schema"], "hammond-benchmark-v1")
        self.assertEqual([row["name"] for row in report["cases"]],
                         ["silence", "all_keys", "disconnected", "dense_automation"])
        for row in report["cases"]:
            self.assertEqual(set(row), LEGACY_CASE)
            silence, dense = row["name"] == "silence", row["name"] == "dense_automation"
            self.assertEqual(row["active_keys"], 0 if silence else 122)
            self.assertEqual(row["setup_events_consumed"], 18 if silence else 140)
            self.assertEqual(row["events_per_call"], 1024 if dense else 0)
            self.assertEqual(row["event_offsets_per_call"], 5 if dense else 0)
            self.assertEqual(row["events_consumed"], 2048 if dense else 0)
            self.assertEqual(row["output_connected"], row["name"] != "disconnected")
        self.assertIsNone(report["cases"][2]["sample_checksum"])
        self.assertEqual(len({row["final_source_phase_checksum"] for row in report["cases"]}), 1)

    def test_console_accounting_and_rational_motion_at_three_rates(self):
        for rate in (44100, 48000, 96000):
            report = self.run_report("console_all", rate=rate)
            self.assertEqual([row["name"] for row in report["cases"]], ["console_motion", "owned_input"])
            self.check_console(report, rate, 384, 1, 7)
            self.assertNotEqual(report["cases"][0]["sample_checksum"], report["cases"][1]["sample_checksum"])

    def test_small_and_maximum_blocks_and_uint64_seed(self):
        for block, warmup, iterations in ((1, 2, 5), (65536, 1, 1)):
            report = self.run_report("console_all", block=block, warmup=warmup,
                                     iterations=iterations, seed=2**64 - 1)
            self.check_console(report, 48000, block, warmup, iterations)

    def test_repeat_and_single_selection_preserve_work_and_sinks(self):
        options = dict(block=128, warmup=3, iterations=5, seed=97531)
        first = self.run_report("console_all", **options)
        second = self.run_report("console_all", **options)
        self.assertEqual(without_timings(first), without_timings(second))
        for index, name in enumerate(("console_motion", "owned_input")):
            one = self.run_report(name, **options)
            expected = without_timings(first)
            expected["cases"] = [expected["cases"][index]]
            self.assertEqual(without_timings(one), expected)

    def test_rejects_invalid_or_excessive_work_before_report(self):
        invalid = [
            ["--case", "console"], ["--case", "console_all", "--case", "owned_input"],
            ["--block-size", "0"], ["--block-size", "65537"], ["--block-size", "-1"],
            ["--sample-rate", "192000"], ["--iterations", "0"], ["--warmup", "0"],
            ["--seed", str(2**64)], ["--seed", "1.0"], ["--unknown", "1"],
            ["--case"], ["--help", "--case", "console_all"],
            ["--profile", "x" * 4097],
            ["--block-size", "65536", "--warmup", "1", "--iterations", "16"],
            ["--warmup", "1", "--iterations", "10000"],
        ]
        for arguments in invalid:
            with self.subTest(arguments=arguments[:2]):
                run = self.invoke(arguments, stdout=subprocess.PIPE)
                self.assertNotEqual(run.returncode, 0)
                self.assertEqual(run.stdout, "")
                self.assertIn("hammond_benchmark:", run.stderr)
        with tempfile.TemporaryDirectory(prefix="hammond benchmark input ") as temporary:
            directory = Path(temporary)
            malformed = directory / "malformed.b3p"
            malformed.write_bytes(b"invalid compiled profile\n")
            for path in (directory, directory / "missing.b3p", malformed):
                run = self.invoke(["--profile", str(path), "--case", "console_all"], stdout=subprocess.PIPE)
                self.assertNotEqual(run.returncode, 0)
                self.assertEqual(run.stdout, "")
                self.assertIn("hammond_benchmark:", run.stderr)

    def test_report_and_help_flush_failures_are_not_success(self):
        with tempfile.TemporaryDirectory(prefix="hammond benchmark stdout ") as temporary:
            sink = Path(temporary) / "readonly-output"
            sentinel = b"keep existing bytes\n"
            sink.write_bytes(sentinel)
            cases = (["--help"], ["--profile", str(self.profile), "--case", "silence",
                                  "--warmup", "1", "--iterations", "1"])
            for arguments in cases:
                with self.subTest(arguments=arguments), sink.open("rb") as output:
                    run = self.invoke(arguments, stdout=output)
                self.assertNotEqual(run.returncode, 0)
                self.assertIn("stdout", run.stderr)
                self.assertEqual(sink.read_bytes(), sentinel)


if __name__ == "__main__":
    unittest.main()
