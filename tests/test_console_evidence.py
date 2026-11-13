#!/usr/bin/env python3
"""End-to-end synthetic console acceptance against independent PCM oracles.

CTest supplies HAMMOND_RENDER_EXECUTABLE and HAMMOND_TEST_PROFILE. Missing build
inputs fail, never skip. No implementation envelope recurrence or source PRNG is
copied: closed-form readiness weights a two-basis fit with unknown source phase.
"""

import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import struct
import tempfile
import unittest
import wave


ROOT = Path(__file__).resolve().parents[1]
RATES = (44100, 48000, 96000)
FAST_TAU = (1.5e6 * 4.7e6 / (1.5e6 + 4.7e6)) * 3.3e-7
RECOVERY_TAU = 0.03432
EXPECTED_AMPLITUDE = 0.03 * 1.5
PCM_STEP = 1.0 / 32768.0
# PCM rounding/scaling is bounded by one step. The extra 1e-8 covers the
# float output conversion and supported-build trigonometric/phase arithmetic.
SAMPLE_ERROR = PCM_STEP + 1e-8


def load_tool(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


producer = load_tool("render_fixture")
consumer = load_tool("verify_render")


def prerequisite(name):
    raw = os.environ.get(name)
    if not raw or not Path(raw).is_file():
        raise RuntimeError(
            f"Missing prerequisite {name}: {raw!r}; build hammond_render and "
            "nominal.b3p, then run CTest. Console acceptance was not run.")
    return Path(raw).resolve()


def at(rate, centiseconds):
    # All supported rates are divisible by 100: no rounding of score timestamps.
    return rate // 100 * centiseconds


def legato_score(rate):
    events = ((0, "note_on", 69, 100), (12, "note_on", 76, 100),
              (25, "note_off", 69, 0), (35, "note_off", 76, 0),
              (37, "note_on", 69, 100), (55, "note_off", 69, 0),
              (60, "note_on", 69, 100), (70, "note_on", 69, 100),
              (75, "note_off", 69, 0), (75, "note_on", 69, 100),
              (85, "note_off", 69, 0))
    return "".join(f"{at(rate, time)} {kind} upper {note} {value}\n"
                   for time, kind, note, value in events).encode("ascii")


def weighted_tone_fit(samples, start, stop, frequency, rate, readiness):
    """Fit q[n]*(a*sin(w*n)+b*cos(w*n)) and bound PCM-induced amplitude error.

    The complete 2x2 normal system retains finite-window cross terms. The
    coefficient bounds use the L1 norm of each inverse-system row, so they do
    not assume white quantization noise, an integer period or a known phase.
    """
    rows = []
    xx = yy = xy = xs = ys = 0.0
    for frame in range(start, stop):
        phase = math.tau * frequency * frame / rate
        q = readiness(frame)
        x, y = q * math.sin(phase), q * math.cos(phase)
        sample = samples[frame] * PCM_STEP
        rows.append((x, y))
        xx += x * x
        yy += y * y
        xy += x * y
        xs += x * sample
        ys += y * sample
    determinant = xx * yy - xy * xy
    if not determinant > 0.0:
        raise AssertionError("Singular independent tone-fit window")
    a = (xs * yy - ys * xy) / determinant
    b = (ys * xx - xs * xy) / determinant
    a_bound = SAMPLE_ERROR * sum(abs(yy * x - xy * y) for x, y in rows) / determinant
    b_bound = SAMPLE_ERROR * sum(abs(xx * y - xy * x) for x, y in rows) / determinant
    return math.hypot(a, b), math.hypot(a_bound, b_bound)


class ConsoleEvidenceTests(unittest.TestCase):
    measurements = []
    bundles_rendered = 0

    @classmethod
    def setUpClass(cls):
        cls.renderer = prerequisite("HAMMOND_RENDER_EXECUTABLE")
        cls.compiled = prerequisite("HAMMOND_TEST_PROFILE").read_bytes()
        cls.profile = ROOT / "data/profiles/nominal-unmeasured-v1.json"
        declared = json.loads(cls.profile.read_bytes())
        if declared["profile_id"] != "nominal-unmeasured-v1" or declared["output_gain"]["value"] != 0.03:
            raise RuntimeError("The independent oracle requires the declared nominal profile")
        cls.measurements = []
        cls.bundles_rendered = 0

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="hammond-console-acceptance-")
        self.addCleanup(temporary.cleanup)
        self.work = Path(temporary.name).resolve()
        self.sequence = 0

    def bundle(self, rate, score, frames, contacts="ideal", block=127):
        self.sequence += 1
        source = self.work / f"source-{self.sequence}.events"
        source.write_bytes(score)
        directory = self.work / f"bundle-{self.sequence}"
        manifest = producer.run_fixture(
            renderer=self.renderer, output_dir=directory, profile_json=self.profile,
            events=source, frames=frames, sample_rate=rate, block_size=block,
            seed=179, drawbars="000000000", contacts=contacts, percussion="second",
            percussion_volume="normal", percussion_decay="fast")
        self.assertEqual(manifest["status"], "succeeded", manifest.get("error"))
        type(self).bundles_rendered += 1
        report = consumer.verify_bundle(directory)
        self.assertEqual(report["status"], "verified_retained_bundle")
        self.assertEqual(report["schema_version"], 2)
        self.assertEqual(report["replay"]["status"], "not_performed")
        self.assertEqual(report["evidence_scope"], "synthetic_engineering")
        self.assertEqual(manifest["renderer_metrics"]["render_schema_version"], 2)
        self.assertEqual(manifest["renderer_metrics"]["contact_model"],
                         "ideal-contacts-v1" if contacts == "ideal" else "nominal-linear-travel-v1")
        self.assertEqual(manifest["renderer_metrics"]["percussion_model"], "shared-readiness-v1")
        self.assertEqual((directory / "events.txt").read_bytes(), score)
        self.assertEqual((directory / "profile.b3p").read_bytes(), self.compiled)
        wav_path = directory / "render.wav"
        raw = wav_path.read_bytes()
        self.assertEqual(report["wav_sha256"], hashlib.sha256(raw).hexdigest())
        with wave.open(str(wav_path), "rb") as wav:
            self.assertEqual((wav.getnchannels(), wav.getsampwidth(), wav.getframerate(),
                              wav.getnframes(), wav.getcomptype()), (2, 2, rate, frames, "NONE"))
            pairs = tuple(struct.iter_unpack("<hh", wav.readframes(frames)))
        self.assertEqual(len(pairs), frames)
        self.assertTrue(all(left == right for left, right in pairs))
        self.assertGreater(max(abs(left) for left, _ in pairs), 0)
        self.assertLess(max(abs(left) for left, _ in pairs), 32767)
        return tuple(left for left, _ in pairs), raw

    def check_window(self, samples, rate, label, start, stop, note, readiness):
        # Nominal A4=440, and this isolated second-harmonic route is not folded.
        frequency = 2.0 * 440.0 * 2.0 ** ((note - 69) / 12.0)
        amplitude, bound = weighted_tone_fit(samples, start, stop, frequency, rate, readiness)
        self.assertTrue(math.isfinite(amplitude) and math.isfinite(bound))
        self.assertLess(bound, 0.0002, "Window must remain informative at PCM16 resolution")
        error = abs(amplitude - EXPECTED_AMPLITUDE)
        self.assertLessEqual(error, bound, (rate, label, amplitude, EXPECTED_AMPLITUDE, bound))
        type(self).measurements.append({"rate": rate, "window": label,
                                       "amplitude_error": error, "error_bound": bound})

    def test_legato_recovery_duplicate_and_same_frame_repress_at_three_rates(self):
        for rate in RATES:
            with self.subTest(rate=rate):
                samples, _ = self.bundle(rate, legato_score(rate), at(rate, 90))
                q35 = math.exp(-0.35 / FAST_TAU)
                q37 = 1.0 - (1.0 - q35) * math.exp(-0.02 / RECOVERY_TAU)
                q55 = q37 * math.exp(-0.18 / FAST_TAU)
                q60 = 1.0 - (1.0 - q55) * math.exp(-0.05 / RECOVERY_TAU)
                self.assertLess(q35, q37)
                self.assertLess(q37, q60)
                self.assertLess(q60, 0.9)  # The finite gaps are not full recharge.
                first = lambda n: math.exp(-n / (rate * FAST_TAU))
                after37 = lambda n: q37 * math.exp(-(n - at(rate, 37)) / (rate * FAST_TAU))
                after60 = lambda n: q60 * math.exp(-(n - at(rate, 60)) / (rate * FAST_TAU))
                for label, start, stop, note, q in (
                        ("initial", 3, 11, 69, first),
                        ("joining-note-after-first-release", 26, 34, 76, first),
                        ("20ms-recovery", 38, 46, 69, after37),
                        ("50ms-recovery", 61, 69, 69, after60),
                        ("duplicate-note", 71, 74, 69, after60),
                        ("same-frame-release-press", 76, 84, 69, after60)):
                    self.check_window(samples, rate, label, at(rate, start), at(rate, stop), note, q)
                for start, stop in ((35, 37), (55, 60), (85, 90)):
                    self.assertTrue(all(value == 0 for value in samples[at(rate, start):at(rate, stop)]))

    def test_nominal_harmonic_contacts_precede_detector_and_outlast_release(self):
        for rate in RATES:
            with self.subTest(rate=rate):
                release = at(rate, 10)
                score = f"0 note_on upper 69 100\n{release} note_off upper 69 0\n".encode("ascii")
                samples, _ = self.bundle(rate, score, at(rate, 15), contacts="nominal")
                harmonic_on = math.ceil(0.42 * 0.008 * rate)
                detector_on = math.ceil(0.92 * 0.008 * rate)
                detector_off = release + math.ceil((1.0 - 0.84) * 0.012 * rate)
                harmonic_off = release + math.ceil((1.0 - 0.34) * 0.012 * rate)
                self.assertLess(harmonic_on, detector_on)
                self.assertLess(detector_off, harmonic_off)
                self.assertTrue(all(value == 0 for value in samples[:harmonic_on]))
                self.assertTrue(any(value != 0 for value in samples[harmonic_on:detector_on]))
                self.assertTrue(all(value == 0 for value in samples[harmonic_off:]))
                q_open = math.exp(-(detector_off - detector_on) / (rate * FAST_TAU))
                self.check_window(samples, rate, "harmonic-before-detector", harmonic_on,
                                  detector_on, 69, lambda n: 1.0)
                self.check_window(samples, rate, "nominal-detector-decay", detector_on + at(rate, 1),
                                  release - at(rate, 1), 69,
                                  lambda n: math.exp(-(n - detector_on) / (rate * FAST_TAU)))
                self.check_window(samples, rate, "detector-recovery-before-harmonic-opens",
                                  detector_off, harmonic_off, 69,
                                  lambda n: 1.0 - (1.0 - q_open) *
                                  math.exp(-(n - detector_off) / (rate * RECOVERY_TAU)))

    def test_verified_bundle_pcm_is_exact_across_block_partitions(self):
        for rate in RATES:
            for contacts in ("ideal", "nominal"):
                with self.subTest(rate=rate, contacts=contacts):
                    first, first_wav = self.bundle(rate, legato_score(rate), at(rate, 90),
                                                   contacts=contacts, block=1)
                    second, second_wav = self.bundle(rate, legato_score(rate), at(rate, 90),
                                                     contacts=contacts, block=1024)
                    self.assertEqual(first, second)
                    self.assertEqual(first_wav, second_wav)


if __name__ == "__main__":
    unittest.main()
