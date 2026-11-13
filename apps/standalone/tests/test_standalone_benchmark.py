#!/usr/bin/env python3
"""Standalone benchmark CLI and accounting acceptance, without speed thresholds."""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest


TOP_KEYS = set("""schema status scope workload workload_version sample_rate_hz
buffer_frames iterations warmup seed initial_frame nominal_callback_period_ns
session_model source_model build profile stages snapshots timing audio claims""".split())
STAGE_KEYS = set("""post_attempts accepted_commands applied_commands discarded_commands
queue_full_posts recovery_pending_posts recoveries positive_render_calls
zero_frame_render_calls rendered_frames start_frame end_frame
start_resolved_sequence end_resolved_sequence""".split())
SNAPSHOT_KEYS = set("""prepared running sample_rate_hz frame_clock peak publication_revision
resolved_sequence last_applied_sequence recovery_count queue_overflows
rejected_commands discarded_commands fault_flags last_core_status held_upper_midi
held_lower_midi held_pedal_ids controls""".split())
BUILD_KEYS = set("""configuration compiler_id compiler_version target_system target_processor
source_manifest_sha256 cplusplus ndebug project_sanitizers_enabled sanitizer_scope""".split())
TIMING_KEYS = set("""clock clock_is_steady clock_tick_seconds warmup_included
timer_overhead_subtracted samples_ns render_ns callback_period_ratio
observed_calls_above_period measured_loop_elapsed_ns clock_pair_calibration""".split())
DISTRIBUTION_KEYS = ("minimum", "median", "p95", "p99", "maximum")

# Literal musical/count contracts, independent of the benchmark implementation.
# Columns: setup commands, accepted/applied/discarded per positive callback,
#          failed overflow/pending probes and outside-timer rearm flushes.
WORK = {
    "silence": (0, 0, 0, 0, 0, 0, 0),
    "performance": (7, 0, 0, 0, 0, 0, 0),
    "dense": (7, 256, 256, 0, 0, 0, 0),
    "recovery": (1, 262, 6, 256, 1, 1, 1),
}
DEFAULT_CONTROLS = {
    "upper_a": [0] * 9, "upper_b": [0] * 9,
    "lower_a": [0] * 9, "lower_b": [0] * 9,
    "selected_banks": [1, 1], "route_enabled": [True, True],
    "pedal_drawbars": [0, 0], "expression": 1.0,
    "percussion": {"enabled": False, "harmonic": 0, "volume": 0, "decay": 0},
}
PERFORMANCE_CONTROLS = {
    "upper_a": [0] * 9, "upper_b": [8, 8, 8, 0, 0, 0, 0, 0, 0],
    "lower_a": [0] * 9, "lower_b": [0, 0, 8, 8, 0, 0, 0, 0, 0],
    "selected_banks": [1, 1], "route_enabled": [True, True],
    "pedal_drawbars": [8, 5], "expression": 0.75,
    "percussion": {"enabled": True, "harmonic": 1, "volume": 1, "decay": 1},
}


def reject_nonfinite(token):
    raise ValueError(f"nonfinite JSON constant: {token}")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def fnv1a64(data):
    value = 14695981039346656037
    for byte in data:
        value = ((value ^ byte) * 1099511628211) % (1 << 64)
    return f"{value:016x}"


class StandaloneBenchmarkTests(unittest.TestCase):
    calls = 0

    @classmethod
    def setUpClass(cls):
        for variable, attribute in (
                ("HAMMOND_STANDALONE_BENCHMARK_EXECUTABLE", "binary"),
                ("HAMMOND_TEST_PROFILE", "profile")):
            value = os.environ.get(variable)
            if not value or not Path(value).is_file():
                raise RuntimeError(
                    f"{variable} must name an existing file; build "
                    "hammond_standalone_benchmark and hammond_profile first")
            setattr(cls, attribute, Path(value).resolve())
        cls.profile_bytes = cls.profile.read_bytes()
        cls.profile_sha256 = hashlib.sha256(cls.profile_bytes).hexdigest()

    @classmethod
    def tearDownClass(cls):
        print(f"standalone benchmark CLI calls: {cls.calls}; "
              "no elapsed-time correctness threshold applied")

    def invoke(self, arguments, *, output=subprocess.PIPE, cwd=None):
        type(self).calls += 1
        environment = os.environ.copy()
        # An SDK-free tool must not need a working SDL audio/video driver.
        environment.update(SDL_AUDIODRIVER="hammond_acceptance_missing_driver",
                           SDL_VIDEODRIVER="hammond_acceptance_missing_driver")
        return subprocess.run(
            [str(self.binary), *map(str, arguments)], stdout=output,
            stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="strict",
            env=environment, cwd=cwd, timeout=20, check=False)

    def assert_rejected(self, arguments, *, cwd=None):
        run = self.invoke(arguments, cwd=cwd)
        self.assertNotEqual(run.returncode, 0, arguments)
        self.assertEqual(run.stdout, "", "a failed run must not emit success metrics")
        self.assertTrue(run.stderr.strip(), "failure must have an off-callback diagnostic")
        return run

    def assert_number(self, value, *, minimum=0):
        self.assertIn(type(value), (int, float), f"expected JSON number, got {value!r}")
        self.assertTrue(math.isfinite(value), f"nonfinite value: {value!r}")
        self.assertGreaterEqual(value, minimum)

    def assert_typed_equal(self, actual, expected):
        """Equality must not permit True to stand in for a count or an enum."""
        if isinstance(expected, dict):
            self.assertIs(type(actual), dict)
            self.assertEqual(set(actual), set(expected))
            for key in expected:
                self.assert_typed_equal(actual[key], expected[key])
        elif isinstance(expected, list):
            self.assertIs(type(actual), list)
            self.assertEqual(len(actual), len(expected))
            for value, wanted in zip(actual, expected):
                self.assert_typed_equal(value, wanted)
        elif isinstance(expected, float):
            self.assert_number(actual)
            self.assertEqual(actual, expected)
        else:
            self.assertIs(type(actual), type(expected))
            self.assertEqual(actual, expected)

    def run_report(self, *, workload="performance", rate=48000, block=128,
                   warmup=0, iterations=100, profile=None, cwd=None, defaults=False):
        profile = self.profile if profile is None else profile
        arguments = ["--profile", profile]
        if not defaults:
            arguments += ["--sample-rate", rate, "--buffer-frames", block,
                          "--iterations", iterations, "--warmup", warmup,
                          "--workload", workload]
        run = self.invoke(arguments, cwd=cwd)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(run.stderr, "")
        self.assertLess(len(run.stdout), 1 << 20)
        report = json.loads(run.stdout, parse_constant=reject_nonfinite,
                            object_pairs_hook=unique_object)
        self.assertIs(type(report), dict)
        self.assertEqual(set(report), TOP_KEYS)
        expected_top = {
            "schema": "hammond-standalone-benchmark-v1", "status": "ok",
            "scope": "offline observed wall-clock intervals around actual Session::render",
            "workload": workload, "workload_version": 1, "sample_rate_hz": rate,
            "buffer_frames": block, "iterations": iterations, "warmup": warmup,
            "seed": 0, "initial_frame": 0,
            "session_model": "standalone-callback-boundary-session-v1",
            "source_model": "ideal-shared-sine-v1",
        }
        for key, value in expected_top.items():
            self.assert_typed_equal(report[key], value)
        # This is the declared period, never a maximum allowed render duration.
        self.assert_number(report["nominal_callback_period_ns"])
        self.assertEqual(report["nominal_callback_period_ns"], block * 1_000_000_000 / rate)
        self.check_build_shape(report["build"])
        self.check_profile(report["profile"], Path(profile).read_bytes())
        self.check_stages_and_snapshots(report, workload, rate, block, warmup, iterations)
        self.check_timing(report["timing"], iterations, report["nominal_callback_period_ns"])
        self.check_audio(report["audio"], workload, block, iterations)
        self.assert_typed_equal(report["claims"], {
            "hard_realtime": False, "device_deadline_pass": None,
            "device_underruns": None, "device_latency_seconds": None,
            "timing_threshold_applied": False,
        })
        return report

    def check_build_shape(self, build):
        self.assertIs(type(build), dict)
        self.assertEqual(set(build), BUILD_KEYS)
        for field in ("configuration", "compiler_id", "compiler_version",
                      "target_system", "target_processor"):
            self.assertIs(type(build[field]), str)
            self.assertTrue(build[field], f"missing build identity: {field}")
        self.assertRegex(build["source_manifest_sha256"], r"^[0-9a-f]{64}$")
        self.assertIs(type(build["cplusplus"]), int)
        self.assertGreaterEqual(build["cplusplus"], 202002)
        for field in ("ndebug", "project_sanitizers_enabled"):
            self.assertIs(type(build[field]), bool)
        self.assertEqual(build["sanitizer_scope"],
                         "project option; externally injected flags are not detected")

    def check_profile(self, profile, payload):
        authoring = re.search(rb"(?:^|\s)authoring_sha256 ([0-9a-f]{64})(?:\s|$)", payload)
        self.assertIsNotNone(authoring, "test profile must carry its authoring digest")
        self.assert_typed_equal(profile, {
            "id": "nominal-unmeasured-v1",
            "authoring_sha256_retained": authoring.group(1).decode("ascii"),
            "compiled_bytes": len(payload), "compiled_fnv1a64": fnv1a64(payload),
        })

    def check_stages_and_snapshots(self, report, workload, rate, block, warmup, iterations):
        setup, accepted, applied, discarded, full, pending, rearm = WORK[workload]
        stages = report["stages"]
        self.assertIs(type(stages), dict)
        self.assertEqual(set(stages), {"setup", "warmup", "measured"})
        expected_setup = dict.fromkeys(STAGE_KEYS, 0)
        expected_setup.update(post_attempts=setup, accepted_commands=setup,
                              applied_commands=setup, zero_frame_render_calls=1,
                              end_resolved_sequence=setup)
        self.assert_typed_equal(stages["setup"], expected_setup)
        for name, count, earlier in (("warmup", warmup, 0),
                                     ("measured", iterations, warmup)):
            self.assert_typed_equal(stages[name], {
                "post_attempts": (accepted + full + pending) * count,
                "accepted_commands": accepted * count,
                "applied_commands": applied * count,
                "discarded_commands": discarded * count,
                "queue_full_posts": full * count, "recovery_pending_posts": pending * count,
                "recoveries": full * count, "positive_render_calls": count,
                "zero_frame_render_calls": rearm * count, "rendered_frames": block * count,
                "start_frame": block * earlier, "end_frame": block * (earlier + count),
                "start_resolved_sequence": setup + accepted * earlier,
                "end_resolved_sequence": setup + accepted * (earlier + count),
            })
        snapshots = report["snapshots"]
        self.assertIs(type(snapshots), dict)
        self.assertEqual(set(snapshots),
                         {"after_setup", "after_warmup", "after_measurement", "after_stop"})
        previous_revision = 0
        for name, cycles in (("after_setup", 0), ("after_warmup", warmup),
                             ("after_measurement", warmup + iterations),
                             ("after_stop", warmup + iterations)):
            snapshot = snapshots[name]
            self.assertIs(type(snapshot), dict)
            self.assertEqual(set(snapshot), SNAPSHOT_KEYS)
            stopped = name == "after_stop"
            holds = workload in ("performance", "dense") and not stopped
            recovered = workload == "recovery" and cycles > 0
            expected = {
                "prepared": True, "running": not stopped, "sample_rate_hz": rate,
                "frame_clock": block * cycles,
                "resolved_sequence": setup + accepted * cycles,
                "last_applied_sequence": setup + accepted * cycles - (256 if recovered else 0),
                "recovery_count": full * cycles, "queue_overflows": full * cycles,
                "rejected_commands": 0, "discarded_commands": discarded * cycles,
                "fault_flags": 1 if recovered else 0, "last_core_status": "ok",
                "held_upper_midi": [60, 64, 67] if holds else [],
                "held_lower_midi": [48, 55] if holds else [],
                "held_pedal_ids": [1] if holds else [],
                "controls": DEFAULT_CONTROLS if workload == "silence" else PERFORMANCE_CONTROLS,
            }
            for field, value in expected.items():
                self.assert_typed_equal(snapshot[field], value)
            revision = snapshot["publication_revision"]
            self.assertIs(type(revision), int)
            self.assertGreater(revision, 0)
            self.assertEqual(revision % 2, 0)
            self.assertGreaterEqual(revision, previous_revision)
            if name != "after_warmup" or warmup:
                self.assertGreater(revision, previous_revision)
            previous_revision = revision
            self.assert_number(snapshot["peak"])
            if holds and cycles:
                self.assertGreater(snapshot["peak"], 0)
            else:
                self.assertEqual(snapshot["peak"], 0)
        if not warmup:
            self.assertEqual(snapshots["after_setup"], snapshots["after_warmup"])
        for left, right in (("setup", "warmup"), ("warmup", "measured")):
            self.assertEqual(stages[left]["end_frame"], stages[right]["start_frame"])
            self.assertEqual(stages[left]["end_resolved_sequence"],
                             stages[right]["start_resolved_sequence"])

    def check_distribution(self, values, *, samples=None, count=None, total=True):
        self.assertIs(type(values), dict)
        self.assertEqual(set(values), set(DISTRIBUTION_KEYS) | ({"total"} if total else set()))
        ordered = [values[key] for key in DISTRIBUTION_KEYS]
        for value in values.values():
            self.assert_number(value)
        self.assertEqual(ordered, sorted(ordered))
        if samples is not None:
            self.assertEqual(values["minimum"], min(samples))
            self.assertEqual(values["maximum"], max(samples))
            self.assertTrue(math.isclose(values["total"], math.fsum(samples),
                                         rel_tol=1e-12, abs_tol=1e-6))
            # Empirical rank inequalities validate labels without reimplementing
            # sorting/interpolation or comparing against any speed expectation.
            self.assertLessEqual(sum(value < values["median"] for value in samples), len(samples) / 2)
            self.assertLessEqual(sum(value > values["median"] for value in samples), len(samples) / 2)
            for label, percentile in (("p95", 95), ("p99", 99)):
                below = sum(value < values[label] for value in samples)
                through = sum(value <= values[label] for value in samples)
                self.assertLess(100 * below, percentile * len(samples))
                self.assertGreaterEqual(100 * through, percentile * len(samples))
        if total and count is not None:
            tolerance = max(1e-6, values["total"] * 1e-12)
            self.assertGreaterEqual(values["total"] + tolerance, values["minimum"] * count)
            self.assertLessEqual(values["total"] - tolerance, values["maximum"] * count)

    def check_timing(self, timing, iterations, period):
        self.assertIs(type(timing), dict)
        self.assertEqual(set(timing), TIMING_KEYS)
        self.assert_typed_equal(timing["clock"], "std::chrono::steady_clock")
        for field, value in (("clock_is_steady", True), ("warmup_included", False),
                             ("timer_overhead_subtracted", False)):
            self.assert_typed_equal(timing[field], value)
        self.assert_number(timing["clock_tick_seconds"])
        self.assertGreater(timing["clock_tick_seconds"], 0)
        samples = timing["samples_ns"]
        self.assertIs(type(samples), list)
        self.assertEqual(len(samples), iterations)
        for value in samples:
            self.assert_number(value)
        self.check_distribution(timing["render_ns"], samples=samples, count=iterations)
        self.check_distribution(timing["callback_period_ratio"], total=False)
        for field in DISTRIBUTION_KEYS:
            self.assertTrue(math.isclose(timing["callback_period_ratio"][field],
                                         timing["render_ns"][field] / period,
                                         rel_tol=1e-12, abs_tol=1e-15))
        self.assert_typed_equal(timing["observed_calls_above_period"],
                                sum(value > period for value in samples))
        self.assert_number(timing["measured_loop_elapsed_ns"])
        self.assertGreaterEqual(timing["measured_loop_elapsed_ns"] + 1e-6,
                                timing["render_ns"]["total"])
        calibration = timing["clock_pair_calibration"]
        self.assertIs(type(calibration), dict)
        self.assertEqual(set(calibration), {"iterations", "ns"})
        self.assert_typed_equal(calibration["iterations"], 1000)
        self.check_distribution(calibration["ns"], count=1000)

    def check_audio(self, audio, workload, block, iterations):
        self.assertIs(type(audio), dict)
        self.assertEqual(set(audio), {"measured_stereo_fnv1a64", "sample_encoding",
                                     "measured_stereo_samples", "all_samples_finite",
                                     "channels_bit_identical", "measured_peak_max"})
        self.assertRegex(audio["measured_stereo_fnv1a64"], r"^[0-9a-f]{16}$")
        self.assert_typed_equal(audio["sample_encoding"],
                                "native float32 object bytes; same-build diagnostic sink")
        self.assert_typed_equal(audio["measured_stereo_samples"], 2 * block * iterations)
        self.assert_typed_equal(audio["all_samples_finite"], True)
        self.assert_typed_equal(audio["channels_bit_identical"], True)
        self.assert_number(audio["measured_peak_max"])
        if workload in ("silence", "recovery"):
            self.assertEqual(audio["measured_peak_max"], 0)
            # Each zero byte applies only the FNV multiply; this independent
            # closed form verifies the diagnostic sink contains silent float32.
            quiet_hash = (14695981039346656037 *
                          pow(1099511628211, 8 * block * iterations, 1 << 64)) % (1 << 64)
            self.assertEqual(audio["measured_stereo_fnv1a64"], f"{quiet_hash:016x}")
        else:
            self.assertGreater(audio["measured_peak_max"], 0)

    def test_defaults_and_exact_source_profile_identity(self):
        report = self.run_report(defaults=True, block=512, warmup=16, iterations=500)
        manifest_name = os.environ.get("HAMMOND_STANDALONE_BENCHMARK_SOURCE_MANIFEST", "")
        source_name = os.environ.get("HAMMOND_SOURCE_DIR", "")
        self.assertTrue(manifest_name and Path(manifest_name).is_file(),
                        "CMake must supply HAMMOND_STANDALONE_BENCHMARK_SOURCE_MANIFEST")
        self.assertTrue(source_name and Path(source_name).is_dir(),
                        "CMake must supply HAMMOND_SOURCE_DIR")
        manifest = json.loads(Path(manifest_name).read_text(encoding="utf-8"),
                              parse_constant=reject_nonfinite, object_pairs_hook=unique_object)
        self.assertEqual(set(manifest), {"schema_version", "entries", "source_manifest_sha256"})
        self.assert_typed_equal(manifest["schema_version"], 1)
        entries = manifest["entries"]
        self.assertIs(type(entries), list)
        self.assertTrue(entries)
        paths, records = [], []
        for entry in entries:
            self.assertEqual(set(entry), {"path", "sha256"})
            self.assertIs(type(entry["path"]), str)
            path = entry["path"]
            self.assertFalse(Path(path).is_absolute())
            self.assertNotIn("\\", path)
            self.assertFalse({"", ".", ".."} & set(path.split("/")))
            self.assertRegex(entry["sha256"], r"^[0-9a-f]{64}$")
            actual = hashlib.sha256((Path(source_name) / path).read_bytes()).hexdigest()
            self.assertEqual(entry["sha256"], actual, path)
            paths.append(path)
            records.append(f"{path}:{actual}\n")
        self.assertEqual(paths, sorted(set(paths)))
        self.assertTrue({"apps/standalone/Session.h", "apps/standalone/Session.cpp",
                         "apps/standalone/benchmark.cpp", "tools/CliArguments.h",
                         "src/Engine.cpp", "include/hammond/Engine.h"} <= set(paths))
        fingerprint = hashlib.sha256("".join(records).encode("utf-8")).hexdigest()
        self.assertEqual(manifest["source_manifest_sha256"], fingerprint)
        self.assertEqual(report["build"]["source_manifest_sha256"], fingerprint)
        for field in ("configuration", "compiler_id", "compiler_version",
                      "target_system", "target_processor"):
            variable = "HAMMOND_STANDALONE_BENCHMARK_EXPECTED_" + field.upper()
            self.assertIn(variable, os.environ, f"CMake must supply {variable}")
            self.assert_typed_equal(report["build"][field], os.environ[variable])
        self.assertEqual(hashlib.sha256(self.profile.read_bytes()).hexdigest(), self.profile_sha256)

    def test_supported_rates_buffer_choices_and_zero_warmup(self):
        cases = [(rate, block) for rate in (44100, 48000, 96000) for block in (128, 2048)]
        cases += [(48000, block) for block in (256, 512, 1024)]
        for rate, block in cases:
            with self.subTest(rate=rate, block=block):
                self.run_report(workload="silence", rate=rate, block=block)

    def test_literal_workloads_and_separate_warmup_accounting(self):
        for warmup in (0, 3):
            reports = {}
            for workload in ("performance", "dense", "recovery"):
                with self.subTest(workload=workload, warmup=warmup):
                    reports[workload] = self.run_report(workload=workload, warmup=warmup)
            # Dense zero-time expression pairs end at the performance value;
            # they must not alter the positive-frame musical sample timeline.
            self.assertEqual(reports["performance"]["audio"], reports["dense"]["audio"])

    def test_unicode_space_profile_path_and_nyquist_failure_preservation(self):
        with tempfile.TemporaryDirectory(prefix="hammond benchmark 音 é ") as temporary:
            directory = Path(temporary)
            profile = directory / "copied profile 音 ♫ é.b3p"
            profile.write_bytes(self.profile_bytes)
            self.run_report(workload="silence", profile=profile, cwd=directory)
            self.assertEqual(profile.read_bytes(), self.profile_bytes)
            # One otherwise valid source above 48k/2 but below 96k/2 proves
            # selected-rate admission, not merely malformed-text rejection.
            text = self.profile_bytes.decode("utf-8")
            changed, replacements = re.subn(r"(?m)^91\s+\S+\s+(\S+)\s+(\S+)$",
                                             r"91 30000 \1 \2", text)
            self.assertEqual(replacements, 1)
            rate_limited = directory / "valid only at 96000.b3p"
            payload = changed.encode("utf-8")
            rate_limited.write_bytes(payload)
            self.run_report(workload="silence", rate=96000, profile=rate_limited, cwd=directory)
            for rate in (44100, 48000):
                with self.subTest(rejected_rate=rate):
                    self.assert_rejected(["--profile", rate_limited, "--sample-rate", rate,
                                          "--iterations", "100"], cwd=directory)
                    self.assertEqual(rate_limited.read_bytes(), payload)
            self.assertEqual({entry.name for entry in directory.iterdir()},
                             {profile.name, rate_limited.name})

    def test_stdout_and_help_write_failure_preserve_sink(self):
        with tempfile.TemporaryDirectory(prefix="hammond benchmark stdout ") as temporary:
            sink = Path(temporary) / "read-only-handle.json"
            sentinel = b"preserve existing bytes\n"
            sink.write_bytes(sentinel)
            for arguments in (["--help"], ["--profile", self.profile, "--iterations", "100",
                                          "--buffer-frames", "128", "--warmup", "0",
                                          "--workload", "silence"]):
                with self.subTest(arguments=arguments), sink.open("rb") as output:
                    run = self.invoke(arguments, output=output, cwd=temporary)
                self.assertNotEqual(run.returncode, 0)
                self.assertIn("stdout", run.stderr.lower())
                self.assertEqual(sink.read_bytes(), sentinel)

    def test_help_is_standalone_and_does_not_need_profile(self):
        run = self.invoke(["--help"])
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(run.stderr, "")
        for option in ("--profile", "--sample-rate", "--buffer-frames", "--iterations",
                       "--warmup", "--workload"):
            self.assertIn(option, run.stdout)
        self.assertNotIn("--output", run.stdout)
        for arguments in (["--help", "--help"], ["--help", "--profile", self.profile],
                          ["--profile", self.profile, "--help"]):
            with self.subTest(arguments=arguments):
                self.assert_rejected(arguments)

    def test_missing_unknown_duplicate_and_partial_cli_rejection(self):
        base = ["--profile", self.profile]
        for arguments in ([], ["--workload", "silence"], ["--unknown"],
                          ["--profile", ""], ["--profile", "x" * 4097],
                          [*base, "unexpected"], [*base, "--workload", "all"],
                          [*base, "--sample-rate=48000"]):
            with self.subTest(arguments=arguments):
                self.assert_rejected(arguments)
        for option, value in (("--profile", self.profile), ("--sample-rate", "48000"),
                              ("--buffer-frames", "128"), ("--iterations", "100"),
                              ("--warmup", "0"), ("--workload", "silence")):
            with self.subTest(option=option, failure="missing value"):
                self.assert_rejected([option])
            prefix = [] if option == "--profile" else base
            with self.subTest(option=option, failure="duplicate option"):
                self.assert_rejected([*prefix, option, value, option, value])
        with tempfile.TemporaryDirectory(prefix="hammond benchmark rejected output ") as temporary:
            destination = Path(temporary) / "preserve.json"
            sentinel = b"existing output is not owned by this CLI\n"
            destination.write_bytes(sentinel)
            self.assert_rejected([*base, "--output", destination], cwd=temporary)
            self.assertEqual(destination.read_bytes(), sentinel)
            self.assertEqual(list(Path(temporary).iterdir()), [destination])

    def test_numeric_grammar_overflow_and_ranges(self):
        base = ["--profile", self.profile]
        invalid = {
            "--sample-rate": ("0", "44099", "48001", "192000", "48000x", "4.8e4"),
            "--buffer-frames": ("0", "127", "129", "2049", "65536", "128.0"),
            "--iterations": ("0", "99", "5001", "100.0", "100x"),
            "--warmup": ("-1", "1001", "0.0", "1x"),
        }
        malformed = ("", "+1", "-0", " 100", "100 ", "NaN", "inf",
                     "18446744073709551616", "9" * 4097)
        for option, values in invalid.items():
            for value in (*values, *malformed):
                with self.subTest(option=option, value=value[:48]):
                    self.assert_rejected([*base, option, value])

    def test_invalid_profile_inputs_preserve_private_fixtures(self):
        with tempfile.TemporaryDirectory(prefix="hammond benchmark profiles ") as temporary:
            directory = Path(temporary)
            bad_payloads = {
                "empty.b3p": b"",
                "corrupt.b3p": b"not a compiled Hammond profile\n",
                "truncated.b3p": self.profile_bytes[:len(self.profile_bytes) // 2],
                "trailing.b3p": self.profile_bytes + b"unexpected trailing token\n",
                "oversized.b3p": self.profile_bytes + b" " * (131073 - len(self.profile_bytes)),
            }
            self.assertLessEqual(len(self.profile_bytes), 131072)
            for name, payload in bad_payloads.items():
                path = directory / name
                path.write_bytes(payload)
                with self.subTest(profile=name):
                    self.assert_rejected(["--profile", path, "--iterations", "100"], cwd=directory)
                    self.assertEqual(path.read_bytes(), payload)
            for path in (directory, directory / "absent.b3p"):
                with self.subTest(profile=path):
                    self.assert_rejected(["--profile", path], cwd=directory)
            self.assertEqual({entry.name for entry in directory.iterdir()}, set(bad_payloads))
        self.assertEqual(self.profile.read_bytes(), self.profile_bytes)


if __name__ == "__main__":
    unittest.main()
