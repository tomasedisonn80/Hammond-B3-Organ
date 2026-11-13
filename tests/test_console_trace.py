#!/usr/bin/env python3
"""Independent acceptance of the actual bounded nominal console trace CLI."""

from __future__ import annotations

import csv
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import subprocess
import tempfile
import unittest


RATES = (44100, 48000, 96000)
MAX_BYTES = 8 * 1024 * 1024
MAX_SEED = 2**64 - 1
HEADER = (
    "frame,time_seconds,position,target,c0,c1,c2,c3,c4,c5,c6,c7,c8,"
    "companion_position,companion_target,companion_c0,companion_c1,"
    "companion_c2,companion_c3,companion_c4,companion_c5,companion_c6,"
    "companion_c7,companion_c8,readiness,physical_detector,eligible,"
    "routed_detector,percussion_gain,upper_sustain_gain,route_enabled,"
    "selected_bank,percussion_enabled,primary_phase_turns,companion_phase_turns,audio"
).split(",")
METADATA = (
    "hammond_console_trace_schema", "evidence_scope", "source_model",
    "contact_model", "percussion_model", "scenario", "scenario_version",
    "profile_id", "authoring_sha256", "profile_digest_scope", "sample_rate",
    "seed", "frames", "timing", "manual", "primary_midi", "companion_midi",
    "primary_tone_id", "companion_tone_id", "primary_frequency_hz",
    "companion_frequency_hz", "primary_source_peak", "companion_source_peak",
    "profile_output_gain", "initial_percussion", "sustained_drawbars",
    "row_count_limit", "byte_limit",
)
BIT_COLUMNS = tuple(range(4, 13)) + tuple(range(15, 24)) + (25, 26, 27, 30, 31, 32)

# Independently transcribed scenario-version-1 tables from CONSOLE_TRACE.md.
# Their millisecond coordinates are converted with integer floor, never with
# the executable's score builder or its CSV output.
SCENARIOS = {
    "partial": (
        (0, "target", 60, "0.5"), (16, "target", 60, "1"),
        (32, "target", 60, "0.5"), (48, "target", 60, "0.46"),
        (56, "target", 60, "0.4"), (64, "target", 60, "0"),
        (68, "target", 60, "0.55"), (84, "target", 60, "1"),
        (100, "target", 60, "0"), (104, "target", 60, "1"),
        (112, "panic", 0, "0"),
    ),
    "legato": (
        (0, "target", 60, "1"), (16, "target", 67, "1"),
        (32, "target", 60, "0"), (48, "target", 67, "0"),
        (52, "target", 60, "1"), (72, "target", 60, "0"),
        (96, "target", 60, "1"), (112, "panic", 0, "0"),
    ),
    "routing": (
        (0, "target", 60, "1"), (16, "route", 0, "0"),
        (32, "bank", 0, "0"), (48, "bank", 0, "1"),
        (64, "enabled", 0, "0"), (80, "enabled", 0, "1"),
        (96, "target", 60, "0"), (112, "panic", 0, "0"),
    ),
}

# Fixed initial answers for tone IDs 49 and 56. Generated with independent
# arbitrary-precision integer evaluation of the documented SplitMix64 mapping,
# cross-checked at IDs 46/91 against the earlier tonewheel known-answer table.
# This permanent test contains no PRNG recurrence or production-module import.
INITIAL_PHASES = {
    0: (float.fromhex("0x1.dd18575ec687cp-2"), float.fromhex("0x1.3632d795089e2p-1")),
    MAX_SEED: (float.fromhex("0x1.9363ae7301a32p-1"), float.fromhex("0x1.2ce6e8a7e0914p-2")),
}


class TravelOracle:
    """Exact rational positions at absolute frames, with declared hysteresis."""

    def __init__(self, rate):
        self.rate = rate
        self.origin = self.target = Fraction(0)
        self.start = 0
        self.closed = [0] * 9

    def position(self, frame):
        elapsed = Fraction(frame - self.start, self.rate)
        if self.target > self.origin:
            return min(self.target, self.origin + 125 * elapsed)
        return max(self.target, self.origin - Fraction(250, 3) * elapsed)

    def command(self, frame, target):
        value = Fraction(target)
        if value != self.target:
            self.origin = self.position(frame)
            self.start = frame
            self.target = value

    def panic(self, frame):
        self.origin = self.target = Fraction(0)
        self.start = frame
        self.closed = [0] * 9

    def sample(self, frame):
        position = self.position(frame)
        for contact, previous in enumerate(self.closed):
            make = Fraction(12 + 10 * contact, 100)
            release = Fraction(4 + 10 * contact, 100)
            if previous and position <= release:
                self.closed[contact] = 0
            elif not previous and position >= make:
                self.closed[contact] = 1
        return float(position), float(self.target), tuple(self.closed)


class ConsoleTraceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        executable = os.environ.get("HAMMOND_CONSOLE_TRACE_EXECUTABLE")
        profile = os.environ.get("HAMMOND_TEST_PROFILE")
        if not executable or not Path(executable).is_file():
            raise RuntimeError("Build hammond_console_trace and set HAMMOND_CONSOLE_TRACE_EXECUTABLE; trace tests were not run.")
        if not profile or not Path(profile).is_file():
            raise RuntimeError("Set HAMMOND_TEST_PROFILE to the compiled nominal profile; trace tests were not run.")
        cls.executable = str(Path(executable).resolve())
        cls.profile = Path(profile).resolve()
        cls.source = Path(os.environ.get("HAMMOND_SOURCE_DIR", Path(__file__).resolve().parents[1]))
        authoring = json.loads((cls.source / "data/profiles/nominal-unmeasured-v1.json").read_text(encoding="utf-8"))
        cls.authoring_digest = hashlib.sha256(json.dumps(
            authoring, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
            allow_nan=False).encode("utf-8")).hexdigest()
        # Read the retained authoring data independently of trace metadata and
        # compiled-profile helpers; fixed IDs also catch incorrect route lookup.
        if [authoring["manual_map"]["tone_ids"][note - 36][3] for note in (60, 67)] != [49, 56]:
            raise RuntimeError("Nominal second-harmonic route anchors changed; review this acceptance contract.")
        cls.frequencies = tuple(authoring["sources"][tone - 1]["frequency_hz"] for tone in (49, 56))
        cls.peaks = tuple(authoring["sources"][tone - 1]["peak_amplitude"] for tone in (49, 56))
        cls.output_gain = authoring["output_gain"]["value"]
        cls.temp = tempfile.TemporaryDirectory(prefix="hammond-trace-acceptance-")
        cls.addClassCleanup(cls.temp.cleanup)
        cls.directory = Path(cls.temp.name)
        cls.traces = {}
        cls.calls = 0
        cls.maxima = {name: 0.0 for name in ("position", "readiness", "phase", "audio")}
        for scenario in SCENARIOS:
            for rate in RATES:
                output = cls.directory / f"{scenario}-{rate}.csv"
                result = cls.invoke(cls.arguments(output, scenario=scenario, rate=rate))
                if result.returncode or result.stdout or result.stderr or not output.is_file():
                    raise RuntimeError(f"Trace generation failed: {scenario}/{rate}: {result.returncode}, {result.stdout!r}, {result.stderr!r}")
                cls.traces[scenario, rate] = output.read_bytes()

    @classmethod
    def tearDownClass(cls):
        print("console trace observed: " + json.dumps({
            "actual_cli_calls": cls.calls,
            "scenario_rate_traces": len(cls.traces),
            "independent_rows": sum(rate * 120 // 1000 for rate in RATES) * len(SCENARIOS),
            "maximum_absolute_errors": cls.maxima,
        }, sort_keys=True))

    @classmethod
    def arguments(cls, output, scenario="partial", rate=48000, seed=0, profile=None):
        return ["--profile", str(profile or cls.profile), "--scenario", str(scenario),
                "--sample-rate", str(rate), "--seed", str(seed), "--output", str(output)]

    @classmethod
    def invoke(cls, arguments, **kwargs):
        cls.calls += 1
        return subprocess.run([cls.executable, *arguments], capture_output=True,
                              timeout=30, check=False, **kwargs)

    def parse(self, raw, scenario, rate, seed=0, digest=None):
        self.assertLessEqual(len(raw), MAX_BYTES)
        self.assertTrue(raw.endswith(b"\n"))
        self.assertNotIn(b"\r", raw)
        self.assertNotIn(b"\x00", raw)
        lines = raw.decode("ascii").splitlines()
        self.assertEqual(len(lines), 29 + rate * 120 // 1000)
        metadata = {}
        for key, line in zip(METADATA, lines[:28]):
            prefix = f"# {key}="
            self.assertTrue(line.startswith(prefix), line)
            metadata[key] = line[len(prefix):]
        expected = {
            "hammond_console_trace_schema": "1", "evidence_scope": "synthetic_engineering",
            "source_model": "ideal-shared-sine-v1", "contact_model": "nominal-linear-travel-v1",
            "percussion_model": "shared-readiness-v1", "scenario": scenario,
            "scenario_version": "1", "profile_id": "nominal-unmeasured-v1",
            "authoring_sha256": digest or self.authoring_digest,
            "profile_digest_scope": "declared_authoring_not_compiled_hash",
            "sample_rate": str(rate), "seed": str(seed), "frames": str(rate * 120 // 1000),
            "timing": "after_events_before_render_and_advance", "manual": "upper",
            "primary_midi": "60", "companion_midi": "67",
            "primary_tone_id": "49", "companion_tone_id": "56",
            "initial_percussion": "on_second_normal_fast", "sustained_drawbars": "all_zero",
            "row_count_limit": "11520", "byte_limit": str(MAX_BYTES),
        }
        for key, value in expected.items():
            self.assertEqual(metadata[key], value, key)
        for key, value in (
            ("primary_frequency_hz", self.frequencies[0]), ("companion_frequency_hz", self.frequencies[1]),
            ("primary_source_peak", self.peaks[0]), ("companion_source_peak", self.peaks[1]),
            ("profile_output_gain", self.output_gain),
        ):
            self.assertEqual(float(metadata[key]), value, key)
        self.assertEqual(lines[28].split(","), HEADER)
        rows = []
        for frame, fields in enumerate(csv.reader(lines[29:])):
            self.assertEqual(len(fields), 36, frame)
            self.assertEqual(fields[0], str(frame))
            self.assertTrue(all(fields[index] in ("0", "1") for index in BIT_COLUMNS), frame)
            row = tuple(float(value) for value in fields)
            self.assertTrue(all(math.isfinite(value) for value in row), frame)
            self.assertEqual(row[1], frame / rate)
            self.assertEqual(struct.unpack("<f", struct.pack("<f", row[35]))[0], row[35])
            rows.append(row)
        return metadata, rows

    def check_oracle(self, rows, scenario, rate):
        keys = {note: TravelOracle(rate) for note in (60, 67)}
        events = {rate * ms // 1000: (kind, index, value)
                  for ms, kind, index, value in SCENARIOS[scenario]}
        route, bank, enabled = 1, 1, 1
        q_origin, q_start, previous_detector = 1.0, 0, False
        fast_tau = 3.3e-7 / (1 / 1_500_000 + 1 / 4_700_000)
        recovery_tau = (82_000 + 22_000) * 3.3e-7
        initial = INITIAL_PHASES[0]
        for frame, row in enumerate(rows):
            if frame in events:
                kind, index, value = events[frame]
                if kind == "target":
                    keys[index].command(frame, value)
                elif kind == "panic":
                    for key in keys.values():
                        key.panic(frame)
                elif kind == "route":
                    route = int(value)
                elif kind == "bank":
                    bank, route = int(value), 1
                elif kind == "enabled":
                    enabled = int(value)
                else:
                    self.fail("Unknown independent scenario instruction")
            contacts = []
            for note, offset in ((60, 2), (67, 13)):
                position, target, bits = keys[note].sample(frame)
                contacts.append(bits)
                error = abs(row[offset] - position)
                self.maxima["position"] = max(self.maxima["position"], error)
                self.assertLessEqual(error, 3e-14, (scenario, rate, frame, note, "position"))
                self.assertEqual(row[offset + 1], target, (scenario, rate, frame, note, "target"))
                self.assertEqual(row[offset + 2:offset + 11], bits,
                                 (scenario, rate, frame, note, "contacts"))
            physical = bool(contacts[0][8] or contacts[1][8])
            eligible = bool(route and bank == 1 and enabled)
            detector = physical and eligible
            elapsed = (frame - q_start) / rate
            q = (q_origin * math.exp(-elapsed / fast_tau) if previous_detector else
                 1 - (1 - q_origin) * math.exp(-elapsed / recovery_tau))
            if detector != previous_detector:
                q_origin, q_start, previous_detector = q, frame, detector
            q_error = abs(row[24] - q)
            self.maxima["readiness"] = max(self.maxima["readiness"], q_error)
            self.assertLessEqual(q_error, 5e-12, (scenario, rate, frame, "readiness"))
            self.assertEqual(row[25:28], (physical, eligible, detector), (scenario, rate, frame))
            self.assertEqual(row[30:33], (route, bank, enabled), (scenario, rate, frame))
            self.assertLessEqual(abs(row[28] - (1.5 * q if eligible else 0)), 8e-12)
            self.assertEqual(row[29], math.sqrt(0.5) if eligible else 1.0)
            phases = []
            for source, offset in enumerate((33, 34)):
                expected = (initial[source] + frame * self.frequencies[source] / rate) % 1
                circular = abs(row[offset] - expected)
                circular = min(circular, 1 - circular)
                self.maxima["phase"] = max(self.maxima["phase"], circular)
                self.assertTrue(0 <= row[offset] < 1)
                self.assertLessEqual(circular, frame * 2**-51 + 8e-14,
                                     (scenario, rate, frame, source, "phase"))
                phases.append(expected)
            expected_audio = self.output_gain * 1.5 * q * sum(
                bits[3] * peak * math.sin(math.tau * phase)
                for bits, peak, phase in zip(contacts, self.peaks, phases)
            ) if eligible else 0.0
            error = abs(row[35] - expected_audio)
            self.maxima["audio"] = max(self.maxima["audio"], error)
            if expected_audio == 0:
                self.assertEqual(row[35], 0.0, (scenario, rate, frame, "silence"))
            else:
                # One binary32 relative spacing, plus the bounded phase/libm
                # and closed-form-readiness allowance for this 120 ms window.
                self.assertLessEqual(error, 2**-23 * max(abs(expected_audio), 0.001) + 1e-10,
                                     (scenario, rate, frame, "audio"))

    def test_all_scenarios_rates_match_independent_current_sample_oracles(self):
        for (scenario, rate), raw in self.traces.items():
            with self.subTest(scenario=scenario, rate=rate):
                _, rows = self.parse(raw, scenario, rate)
                self.assertEqual(rows[0][33:35], INITIAL_PHASES[0])
                self.check_oracle(rows, scenario, rate)

    def test_partial_holds_detector_separation_and_immediate_panic(self):
        for rate in RATES:
            with self.subTest(rate=rate):
                _, rows = self.parse(self.traces["partial", rate], "partial", rate)
                first, returned = rows[rate * 12 // 1000], rows[rate * 44 // 1000]
                self.assertEqual(first[2:4], (0.5, 0.5))
                self.assertEqual(returned[2:4], (0.5, 0.5))
                self.assertEqual(first[4:13], (1, 1, 1, 1, 0, 0, 0, 0, 0))
                self.assertEqual(returned[4:13], (1, 1, 1, 1, 1, 0, 0, 0, 0))
                partial = rows[rate * 5 // 1000:rate * 15 // 1000]
                self.assertTrue(any(abs(row[35]) > 0.01 for row in partial))
                self.assertTrue(all(row[24] == 1 and row[25] == 0 for row in partial))
                command = rows[rate * 16 // 1000]
                self.assertEqual(command[2:4], (0.5, 1.0))
                panic = rows[rate * 112 // 1000]
                self.assertEqual(panic[2:13], (0.0,) * 11)
                self.assertEqual(panic[35], 0.0)
                self.assertLess(panic[24], 1)
                self.assertGreater(rows[-1][24], panic[24])

    def test_legato_shares_readiness_and_routes_preserve_physical_history(self):
        rate = 48000
        _, legato = self.parse(self.traces["legato", rate], "legato", rate)
        joining = rate * 16 // 1000
        self.assertLess(legato[joining][24], legato[joining - 1][24])
        self.assertLess(legato[rate * 40 // 1000][24], legato[rate * 32 // 1000][24])
        self.assertGreater(legato[rate * 95 // 1000][24], legato[rate * 80 // 1000][24])
        _, routing = self.parse(self.traces["routing", rate], "routing", rate)
        for milliseconds, controls in ((20, (0, 1, 1)), (40, (1, 0, 1)), (68, (1, 1, 0))):
            row = routing[rate * milliseconds // 1000]
            self.assertEqual(row[2:4], (1.0, 1.0))
            self.assertEqual(row[12], 1)
            self.assertEqual(row[25:28], (1, 0, 0))
            self.assertEqual(row[30:33], controls)
            self.assertEqual(row[35], 0)
        self.assertGreater(routing[rate * 47 // 1000][24], routing[rate * 16 // 1000][24])
        self.assertLess(routing[rate * 60 // 1000][24], routing[rate * 48 // 1000][24])

    def test_repeated_exports_locale_and_full_uint64_seed(self):
        with tempfile.TemporaryDirectory(prefix="hammond-trace-replay-") as temporary:
            directory = Path(temporary)
            output = directory / "replay.csv"
            args = self.arguments(output, seed="000")
            pairs = [args[index:index + 2] for index in range(0, len(args), 2)]
            result = self.invoke([value for pair in reversed(pairs) for value in pair],
                                 env=dict(os.environ, LC_ALL="de_DE.UTF-8", LANG="de_DE.UTF-8"))
            self.assertEqual((result.returncode, result.stdout, result.stderr), (0, b"", b""))
            self.assertEqual(output.read_bytes(), self.traces["partial", 48000])
            maximum = directory / "maximum.csv"
            result = self.invoke(self.arguments(maximum, seed=MAX_SEED))
            self.assertEqual((result.returncode, result.stdout, result.stderr), (0, b"", b""))
            _, changed = self.parse(maximum.read_bytes(), "partial", 48000, seed=MAX_SEED)
            _, baseline = self.parse(self.traces["partial", 48000], "partial", 48000)
            self.assertEqual(changed[0][33:35], INITIAL_PHASES[MAX_SEED])
            self.assertTrue(any(left[35] != right[35] for left, right in zip(changed, baseline)))
            self.assertTrue(all(left[:33] == right[:33] for left, right in zip(changed, baseline)))
            self.assertEqual(sorted(path.name for path in directory.iterdir()), ["maximum.csv", "replay.csv"])

    def assert_rejected(self, arguments, directory, before=None):
        before = sorted(path.relative_to(directory).as_posix() for path in directory.rglob("*")) if before is None else before
        result = self.invoke(arguments)
        self.assertNotEqual(result.returncode, 0, arguments)
        self.assertEqual(result.stdout, b"")
        self.assertIn(b"hammond_console_trace:", result.stderr)
        self.assertEqual(sorted(path.relative_to(directory).as_posix() for path in directory.rglob("*")), before)

    def test_help_and_strict_argument_admission_before_output(self):
        help_result = self.invoke(["--help"])
        self.assertEqual((help_result.returncode, help_result.stderr), (0, b""))
        self.assertIn(b"Usage: hammond_console_trace", help_result.stdout)
        self.assertIn(b"120 ms", help_result.stdout)
        with tempfile.TemporaryDirectory(prefix="hammond-trace-arguments-") as temporary:
            directory = Path(temporary)
            base = self.arguments(directory / "invalid.csv")
            invalid = [[], ["--help", "extra"], ["--help", "--help"], ["-h"],
                       base + ["--unknown", "1"], base + ["trailing"], base[:-1]]
            for pair in range(0, len(base), 2):
                invalid.append(base[:pair] + base[pair + 2:])
                invalid.append(base + base[pair:pair + 2])
            for field, values in (
                ("--scenario", ("", "Partial", "other", "x" * 4097)),
                ("--sample-rate", ("0", "48001", "48000.0", "4.8e4", "+48000", "-48000", "nan")),
                ("--seed", ("-1", "+1", "1.0", "1e0", str(MAX_SEED + 1), "0" * 21)),
            ):
                for value in values:
                    arguments = list(base)
                    arguments[arguments.index(field) + 1] = value
                    invalid.append(arguments)
            for arguments in invalid:
                with self.subTest(arguments=arguments[:-1]):
                    self.assert_rejected(arguments, directory)

    def test_profile_and_destination_failures_preserve_existing_bytes(self):
        with tempfile.TemporaryDirectory(prefix="hammond-trace-paths-") as temporary:
            directory = Path(temporary)
            output = directory / "trace.csv"
            bad = directory / "bad.b3p"
            for payload in (b"not a profile\n", b"x" * (128 * 1024 + 1)):
                bad.write_bytes(payload)
                self.assert_rejected(self.arguments(output, profile=bad), directory)
                self.assertEqual(bad.read_bytes(), payload)
            self.assert_rejected(self.arguments(output, profile=directory / "absent.b3p"), directory)
            self.assert_rejected(self.arguments(output, profile=directory), directory)
            self.assert_rejected(self.arguments(directory / "missing" / "trace.csv"), directory)
            self.assert_rejected(self.arguments(directory), directory)
            retained = b"keep this destination byte for byte\n"
            output.write_bytes(retained)
            self.assert_rejected(self.arguments(output), directory)
            self.assertEqual(output.read_bytes(), retained)
            self.assert_rejected(self.arguments(output / "child.csv"), directory)
            original = self.profile.read_bytes()
            copied = directory / "copy.b3p"
            copied.write_bytes(original)
            self.assert_rejected(self.arguments(copied, profile=copied), directory)
            self.assertEqual(copied.read_bytes(), original)
            alias = directory / "profile-alias.b3p"
            os.link(copied, alias)
            self.assert_rejected(self.arguments(alias, profile=copied), directory)
            self.assertEqual(alias.read_bytes(), original)

    def test_engine_preparation_failure_creates_no_temporary_output(self):
        with tempfile.TemporaryDirectory(prefix="hammond-trace-prepare-") as temporary:
            directory = Path(temporary)
            profile = directory / "unsupported.b3p"
            lines = self.profile.read_text(encoding="utf-8").splitlines()
            source_start = lines.index("sources 91") + 1
            for frequency, rate in (("30000", 44100), ("1e-300", 96000)):
                changed = list(lines)
                fields = changed[source_start].split()
                fields[1] = frequency
                changed[source_start] = " ".join(fields)
                profile.write_text("\n".join(changed) + "\n", encoding="utf-8")
                self.assert_rejected(self.arguments(directory / "no.csv", rate=rate, profile=profile), directory)
                self.assertEqual(sorted(path.name for path in directory.iterdir()), ["unsupported.b3p"])

    def test_declared_authoring_digest_is_exported_without_authenticity_claim(self):
        with tempfile.TemporaryDirectory(prefix="hammond-trace-provenance-") as temporary:
            directory = Path(temporary)
            profile = directory / "declared.b3p"
            raw = self.profile.read_text(encoding="utf-8")
            profile.write_text(raw.replace("authoring_sha256 " + self.authoring_digest,
                                           "authoring_sha256 " + "0" * 64), encoding="utf-8")
            output = directory / "declared.csv"
            result = self.invoke(self.arguments(output, profile=profile))
            self.assertEqual((result.returncode, result.stdout, result.stderr), (0, b"", b""))
            metadata, rows = self.parse(output.read_bytes(), "partial", 48000, digest="0" * 64)
            self.assertEqual(metadata["profile_digest_scope"], "declared_authoring_not_compiled_hash")
            _, baseline = self.parse(self.traces["partial", 48000], "partial", 48000)
            self.assertEqual(rows, baseline)

    def test_competing_publications_leave_one_complete_file_and_no_temporary_files(self):
        with tempfile.TemporaryDirectory(prefix="hammond-trace-publication-") as temporary:
            directory = Path(temporary)
            output = directory / "one.csv"
            command = [self.executable, *self.arguments(output)]
            first = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            second = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            type(self).calls += 2
            try:
                first_out, first_error = first.communicate(timeout=30)
                second_out, second_error = second.communicate(timeout=30)
            finally:
                for process in (first, second):
                    if process.poll() is None:
                        process.kill()
                        process.communicate()
            self.assertEqual(sum(code == 0 for code in (first.returncode, second.returncode)), 1)
            self.assertEqual((first_out, second_out), (b"", b""))
            self.assertEqual(sum(bool(error) for error in (first_error, second_error)), 1)
            self.assertEqual(output.read_bytes(), self.traces["partial", 48000])
            self.assertEqual([path.name for path in directory.iterdir()], ["one.csv"])

    def test_help_reports_actual_stdout_write_failure(self):
        with tempfile.TemporaryDirectory(prefix="hammond-trace-help-output-") as temporary:
            path = Path(temporary) / "read-only.bin"
            original = b"unchanged output handle\n"
            path.write_bytes(original)
            with path.open("rb", buffering=0) as output:
                type(self).calls += 1
                result = subprocess.run([self.executable, "--help"], stdout=output,
                                        stderr=subprocess.PIPE, timeout=30, check=False)
            self.assertEqual(path.read_bytes(), original)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(b"Cannot write help output", result.stderr)


if __name__ == "__main__":
    unittest.main()
