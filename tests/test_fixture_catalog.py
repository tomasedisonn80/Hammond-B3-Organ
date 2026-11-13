#!/usr/bin/env python3
"""Render and check the checked-in synthetic musical/engineering catalog.

CTest injects HAMMOND_RENDER_EXECUTABLE and HAMMOND_TEST_PROFILE. Direct use:
  python tests/test_fixture_catalog.py --renderer build/hammond_render \
      --profile build/nominal.b3p
Missing build inputs fail clearly; no audio assertion is silently skipped.
Only Python's standard library is used. WAVs live in temporary directories.
"""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import struct
import subprocess
import sys
import tempfile
import unittest
import wave


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "examples" / "fixtures"
CATALOG = FIXTURES / "catalog-v1.json"
RENDERER_OVERRIDE = None
PROFILE_OVERRIDE = None
PCM_STEP = 1.0 / 32768.0
BOUNDS = {
    "fixture_count": 5, "sample_rate": 48000, "max_frames": 192000,
    "max_score_bytes": 16384, "max_events_per_fixture": 128,
    "max_events_at_frame": 32, "max_line_bytes": 256, "max_float_peak": 0.112,
}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f"Non-JSON numeric constant: {value}")


def read_json(raw):
    return json.loads(raw, object_pairs_hook=unique_object,
                      parse_constant=reject_constant)


def required_file(override, environment, candidates, label):
    explicit = override if override is not None else os.environ.get(environment)
    paths = [Path(explicit)] if explicit is not None else candidates
    for path in paths:
        if path.is_file():
            return path.resolve()
    raise RuntimeError(
        f"Missing {label}; checked {', '.join(map(str, paths))}. Build "
        f"hammond_render and nominal.b3p, then set {environment} or pass "
        "--renderer/--profile. Catalog audio assertions were not run."
    )


def fit_tone(samples, span, frequency, rate):
    """Fit a*sin(w*n)+b*cos(w*n) at absolute frames; no source PRNG copy.

    Solve the two-variable least-squares system, retaining cross terms so the
    window need not contain an integer number of periods. For mixtures this
    measures a component with the catalog's finite-window leakage allowance.
    """
    ss = cc = sc = ys = yc = 0.0
    angular_step = math.tau * frequency / rate
    start, end = span
    for frame in range(start, end):
        sine = math.sin(angular_step * frame)
        cosine = math.cos(angular_step * frame)
        value = samples[frame] * PCM_STEP
        ss += sine * sine
        cc += cosine * cosine
        sc += sine * cosine
        ys += value * sine
        yc += value * cosine
    determinant = ss * cc - sc * sc
    if determinant <= 0:
        raise AssertionError("Tone-fit window is singular")
    sine_gain = (ys * cc - yc * sc) / determinant
    cosine_gain = (yc * ss - ys * sc) / determinant
    return sine_gain, cosine_gain


class FixtureCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if CATALOG.stat().st_size > 128 * 1024:
            raise RuntimeError("Fixture catalog exceeds its 128 KiB read bound")
        cls.catalog = read_json(CATALOG.read_text(encoding="utf-8"))
        executable = "hammond_render.exe" if os.name == "nt" else "hammond_render"
        cls.renderer = required_file(
            RENDERER_OVERRIDE, "HAMMOND_RENDER_EXECUTABLE",
            [ROOT / "build" / executable], "renderer executable",
        )
        if not os.access(cls.renderer, os.X_OK):
            raise RuntimeError(f"Renderer is not executable: {cls.renderer}")
        cls.profile = required_file(
            PROFILE_OVERRIDE, "HAMMOND_TEST_PROFILE",
            [cls.renderer.parent / "nominal.b3p", ROOT / "build" / "nominal.b3p"],
            "compiled nominal profile",
        )
        cls.authoring = read_json(
            (ROOT / "data/profiles/nominal-unmeasured-v1.json").read_text(encoding="utf-8")
        )

    def assert_span(self, span, frames):
        self.assertIsInstance(span, list)
        self.assertEqual(len(span), 2)
        self.assertTrue(all(type(value) is int for value in span))
        self.assertLessEqual(0, span[0])
        self.assertLess(span[0], span[1])
        self.assertLessEqual(span[1], frames)

    def fixture_path(self, fixture):
        relative = PurePosixPath(fixture["events"]["path"])
        self.assertFalse(relative.is_absolute())
        self.assertEqual(len(relative.parts), 1, "Event paths must stay inside fixtures/")
        self.assertNotIn("\\", str(relative))
        self.assertEqual(relative.name, fixture["id"] + ".events")
        path = (FIXTURES / relative).resolve(strict=True)
        self.assertEqual(path.parent, FIXTURES.resolve(), "Event path escapes fixtures/")
        self.assertTrue(path.is_file())
        return path

    def validate_score(self, fixture, path):
        raw = path.read_bytes()
        self.assertLessEqual(len(raw), BOUNDS["max_score_bytes"])
        self.assertRegex(fixture["events"]["sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(hashlib.sha256(raw).hexdigest(), fixture["events"]["sha256"])
        text = raw.decode("utf-8")
        self.assertIn(
            f"frames={fixture['frames']} sample_rate={fixture['sample_rate']} "
            f"seed={fixture['seed']} drawbars={fixture['registration']}", text,
        )
        events = []
        for line in text.splitlines():
            self.assertLessEqual(len(line.encode("utf-8")), BOUNDS["max_line_bytes"])
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            fields = stripped.split()
            self.assertEqual(len(fields), 5, line)
            frame, kind, manual, index, value = fields
            self.assertRegex(frame, r"^[0-9]+$")
            self.assertRegex(index, r"^[0-9]+$")
            self.assertRegex(value, r"^[0-9]+(?:\.[0-9]+)?$")
            frame, index, value = int(frame), int(index), float(value)
            self.assertTrue(math.isfinite(value))
            self.assertIn(manual, ("upper", "lower"))
            self.assertLess(frame, fixture["frames"])
            if events:
                self.assertGreaterEqual(frame, events[-1][0], "Score must be ordered")
            if kind == "note_on":
                self.assertTrue(36 <= index <= 96 and 0 <= value <= 127 and value.is_integer())
            elif kind == "note_off":
                self.assertTrue(36 <= index <= 96 and value == 0)
            elif kind in ("drawbar", "bank_drawbar"):
                self.assertLess(index, 9 if kind == "drawbar" else 18)
                self.assertTrue(0 <= value <= 8 and value.is_integer())
            elif kind == "expression":
                self.assertTrue(index == 0 and 0 <= value <= 1)
            elif kind == "select_bank":
                self.assertTrue(index == 0 and value in (0, 1))
            else:
                self.assertIn(kind, ("all_notes_off", "cancel"))
                self.assertTrue(index == 0 and value == 0)
            events.append((frame, kind, manual, index, value))
        self.assertTrue(events)
        self.assertLessEqual(len(events), BOUNDS["max_events_per_fixture"])
        self.assertLessEqual(max(Counter(event[0] for event in events).values()),
                             BOUNDS["max_events_at_frame"])
        return events

    def validate_fixture(self, fixture):
        self.assertRegex(fixture["id"], r"^[a-z][a-z0-9-]+-v1$")
        self.assertTrue(fixture["purpose"].strip())
        self.assertIs(type(fixture["sample_rate"]), int)
        self.assertEqual(fixture["sample_rate"], BOUNDS["sample_rate"])
        self.assertIs(type(fixture["frames"]), int)
        self.assertTrue(0 < fixture["frames"] <= BOUNDS["max_frames"])
        self.assertIs(type(fixture["seed"]), int)
        self.assertTrue(0 <= fixture["seed"] < 2**64)
        self.assertIs(type(fixture["block_size"]), int)
        self.assertTrue(1 <= fixture["block_size"] <= 65536)
        self.assertRegex(fixture["registration"], r"^[0-8]{9}$")
        path = self.fixture_path(fixture)
        self.validate_score(fixture, path)
        expected = fixture["expectations"]
        self.assertEqual(expected["clipped_frames"], 0)
        self.assertTrue(0 < expected["float_peak_max"] <= BOUNDS["max_float_peak"])
        # Every frame is accounted for as audible or exactly silent.
        spans = sorted(expected["silence_spans"] + expected["audible_spans"])
        self.assertTrue(expected["silence_spans"])
        self.assertTrue(expected["audible_spans"])
        position = 0
        for span in spans:
            self.assert_span(span, fixture["frames"])
            self.assertEqual(span[0], position, "Timeline has an overlap or unchecked gap")
            position = span[1]
        self.assertEqual(position, fixture["frames"])
        for route in expected["route_anchors"]:
            self.assertIn(route["manual"], ("upper", "lower"))
            self.assertTrue(36 <= route["midi_note"] <= 96)
            self.assertTrue(0 <= route["drawbar_index"] <= 8)
            self.assertEqual(
                self.authoring["manual_map"]["tone_ids"][route["midi_note"] - 36]
                              [route["drawbar_index"]], route["tone_id"],
            )
        tone_counts = Counter()
        for check in expected["tone_checks"]:
            self.assert_span(check["span"], fixture["frames"])
            tone_id = check["tone_id"]
            self.assertTrue(13 <= tone_id <= 91)
            self.assertEqual(check["frequency_hz"],
                             self.authoring["sources"][tone_id - 1]["frequency_hz"])
            self.assertTrue(0 < check["peak_amplitude"] <= expected["float_peak_max"])
            self.assertTrue(any(a <= check["span"][0] < check["span"][1] <= b
                                for a, b in expected["audible_spans"]))
            tone_counts[tone_id] += 1
        for tone_id in expected["continuous_tone_ids"]:
            self.assertGreaterEqual(tone_counts[tone_id], 2)
        for check in expected["spectrum_checks"]:
            self.assert_span(check["span"], fixture["frames"])
            self.assertTrue(check["tone_peaks"])
            self.assertTrue(any(a <= check["span"][0] < check["span"][1] <= b
                                for a, b in expected["audible_spans"]))
            for tone_id, amplitude in check["tone_peaks"].items():
                self.assertRegex(tone_id, r"^[0-9]+$")
                self.assertTrue(13 <= int(tone_id) <= 91)
                self.assertTrue(0 < amplitude <= expected["float_peak_max"])
        return path

    def test_catalog_paths_hashes_profile_and_score_bounds(self):
        self.assertEqual(self.catalog["schema_version"], 1)
        self.assertEqual(self.catalog["catalog_id"], "nominal-engine-fixtures-v1")
        self.assertEqual(self.catalog["model"], "ideal-shared-sine-v1")
        self.assertEqual(self.catalog["evidence_status"], "synthetic-unmeasured")
        self.assertEqual(self.catalog["catalog_bounds"], BOUNDS)
        self.assertEqual(self.catalog["analysis_tolerances"], {
            "sine_residual_lsb": 1.0, "sine_amplitude_error_lsb": 2.0,
            "normalized_phase_distance": 0.003, "mixed_tone_relative_error": 0.2,
        })
        self.assertGreaterEqual(len(self.catalog["limits"]), 4)
        profile = self.catalog["profile"]
        self.assertEqual(profile["id"], "nominal-unmeasured-v1")
        self.assertEqual(profile["authoring_path"],
                         "data/profiles/nominal-unmeasured-v1.json")
        canonical = json.dumps(self.authoring, sort_keys=True, separators=(",", ":"),
                               ensure_ascii=False, allow_nan=False).encode("utf-8")
        self.assertEqual(hashlib.sha256(canonical).hexdigest(), profile["authoring_sha256"])
        self.assertLessEqual(self.profile.stat().st_size, 128 * 1024)
        self.assertEqual(hashlib.sha256(self.profile.read_bytes()).hexdigest(),
                         profile["compiled_sha256"], "Catalog requires the bound nominal profile")
        fixtures = self.catalog["fixtures"]
        self.assertEqual(len(fixtures), BOUNDS["fixture_count"])
        self.assertEqual(len({fixture["id"] for fixture in fixtures}), len(fixtures))
        paths = set()
        for fixture in fixtures:
            with self.subTest(fixture=fixture["id"]):
                paths.add(self.validate_fixture(fixture))
        self.assertEqual(paths, {path.resolve() for path in FIXTURES.glob("*.events")})
        self.assertFalse(list(FIXTURES.glob("*.wav")), "Generated WAVs do not belong in the catalog")

    def test_render_every_catalog_fixture_and_its_audio_expectations(self):
        tolerances = self.catalog["analysis_tolerances"]
        with tempfile.TemporaryDirectory(prefix="hammond-catalog-") as directory:
            for fixture in self.catalog["fixtures"]:
                with self.subTest(fixture=fixture["id"]):
                    events = self.validate_fixture(fixture)
                    output = Path(directory) / (fixture["id"] + ".wav")
                    command = [str(self.renderer), "--profile", str(self.profile),
                               "--output", str(output), "--events", str(events),
                               "--frames", str(fixture["frames"]),
                               "--sample-rate", str(fixture["sample_rate"]),
                               "--block-size", str(fixture["block_size"]),
                               "--seed", str(fixture["seed"]),
                               "--drawbars", fixture["registration"], "--fail-on-clip"]
                    result = subprocess.run(command, cwd=directory, capture_output=True,
                                            text=True, encoding="utf-8", timeout=30, check=False)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertEqual(result.stderr, "")
                    report = read_json(result.stdout)
                    for key in ("sample_rate", "frames", "seed", "block_size"):
                        self.assertEqual(report[key], fixture[key])
                    self.assertEqual(report["status"], "ok")
                    self.assertEqual(report["model"], self.catalog["model"])
                    self.assertEqual(report["evidence_status"], "unmeasured")
                    self.assertEqual(report["profile_id"], self.catalog["profile"]["id"])
                    self.assertEqual(report["authoring_sha256"],
                                     self.catalog["profile"]["authoring_sha256"])
                    self.assertEqual(report["channels"], 2)
                    self.assertEqual(report["sample_format"], "pcm_s16le")
                    self.assertEqual(report["clipped_frames"], 0)
                    self.assertEqual(report["clipped_channel_samples"], 0)
                    expected = fixture["expectations"]
                    self.assertTrue(0 < report["rms"] <= report["peak"] <= expected["float_peak_max"])
                    with wave.open(str(output), "rb") as wav:
                        self.assertEqual((wav.getnchannels(), wav.getsampwidth(), wav.getframerate(),
                                          wav.getnframes(), wav.getcomptype()),
                                         (2, 2, fixture["sample_rate"], fixture["frames"], "NONE"))
                        pcm = wav.readframes(fixture["frames"])
                    self.assertEqual(len(pcm), fixture["frames"] * 4)
                    interleaved = struct.unpack("<" + "h" * (len(pcm) // 2), pcm)
                    samples = interleaved[::2]
                    self.assertEqual(samples, interleaved[1::2])
                    self.assertNotIn(-32768, samples)
                    self.assertNotIn(32767, samples)
                    pcm_peak = max(map(abs, samples)) * PCM_STEP
                    pcm_rms = math.sqrt(math.fsum(x * x for x in samples) / len(samples)) * PCM_STEP
                    self.assertAlmostEqual(report["peak"], pcm_peak, delta=PCM_STEP)
                    self.assertAlmostEqual(report["rms"], pcm_rms, delta=PCM_STEP)
                    for start, end in expected["silence_spans"]:
                        self.assertFalse(any(samples[start:end]), f"Expected silence in [{start}, {end})")
                    for start, end in expected["audible_spans"]:
                        rms = math.sqrt(math.fsum(x * x for x in samples[start:end]) / (end - start)) * PCM_STEP
                        self.assertGreater(rms, 0.001, f"Expected audible signal in [{start}, {end})")
                    phases = defaultdict(list)
                    for check in expected["tone_checks"]:
                        sine_gain, cosine_gain = fit_tone(samples, check["span"],
                                                         check["frequency_hz"], fixture["sample_rate"])
                        amplitude = math.hypot(sine_gain, cosine_gain)
                        self.assertAlmostEqual(amplitude, check["peak_amplitude"],
                                               delta=tolerances["sine_amplitude_error_lsb"] * PCM_STEP)
                        angular_step = math.tau * check["frequency_hz"] / fixture["sample_rate"]
                        maximum_error = max(abs(samples[n] * PCM_STEP - sine_gain * math.sin(angular_step * n)
                                                - cosine_gain * math.cos(angular_step * n))
                                            for n in range(*check["span"]))
                        self.assertLessEqual(maximum_error, tolerances["sine_residual_lsb"] * PCM_STEP)
                        phases[check["tone_id"]].append((sine_gain / amplitude, cosine_gain / amplitude))
                    for tone_id in expected["continuous_tone_ids"]:
                        first, *following = phases[tone_id]
                        for phase in following:
                            self.assertLessEqual(math.dist(first, phase),
                                                 tolerances["normalized_phase_distance"],
                                                 f"Tone {tone_id} restarted or changed phase")
                    for check in expected["spectrum_checks"]:
                        for tone_id, expected_peak in check["tone_peaks"].items():
                            frequency = self.authoring["sources"][int(tone_id) - 1]["frequency_hz"]
                            sine_gain, cosine_gain = fit_tone(samples, check["span"], frequency,
                                                             fixture["sample_rate"])
                            self.assertAlmostEqual(math.hypot(sine_gain, cosine_gain), expected_peak,
                                                   delta=expected_peak * tolerances["mixed_tone_relative_error"],
                                                   msg=f"Tone {tone_id} component in {check['span']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--renderer", help="Path to an already-built hammond_render")
    parser.add_argument("--profile", help="Path to an already-compiled nominal.b3p")
    arguments, unittest_arguments = parser.parse_known_args()
    RENDERER_OVERRIDE = arguments.renderer
    PROFILE_OVERRIDE = arguments.profile
    unittest.main(argv=[sys.argv[0], *unittest_arguments], verbosity=2)
