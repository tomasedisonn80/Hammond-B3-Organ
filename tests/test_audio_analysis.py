#!/usr/bin/env python3
"""Independent PCM fixtures plus a required, separate real-render integration case.

Set HAMMOND_RENDER_EXECUTABLE and HAMMOND_TEST_PROFILE for non-default builds.
Missing renderer/profile inputs fail the integration class; they never skip it.
"""

import io
import json
import math
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
import wave


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from analyze_wav import AnalysisError, analyze_wav  # noqa: E402

ANALYZER = ROOT / "tools" / "analyze_wav.py"
PCM_STEP = 1 / 32768


def pcm_bytes(frames, channels=1, rate=48000):
    """Fixtures use Python's WAV writer, never the producer or analyzer encoder."""
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as output:
        output.setnchannels(channels)
        output.setsampwidth(2)
        output.setframerate(rate)
        output.writeframes(b"".join(struct.pack("<" + "h" * channels, *frame)
                                   for frame in frames))
    return buffer.getvalue()


def riff(chunks):
    contents = b"WAVE" + b"".join(
        kind + struct.pack("<I", len(body)) + body + (b"\x00" if len(body) & 1 else b"")
        for kind, body in chunks)
    return b"RIFF" + struct.pack("<I", len(contents)) + contents


class PCMFixtureTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="hammond-pcm-analysis-")
        self.addCleanup(directory.cleanup)
        self.work = Path(directory.name)
        self.path = self.work / "independent fixture.wav"

    def fixture(self, frames, channels=1, rate=48000):
        self.path.write_bytes(pcm_bytes(frames, channels, rate))
        return self.path

    def reject(self, data):
        self.path.write_bytes(data)
        with self.assertRaises(AnalysisError):
            analyze_wav(self.path)
        self.assertEqual(self.path.read_bytes(), data)

    def test_silence_and_inconclusive_frequency(self):
        self.fixture([(0, 0)] * 257, channels=2)
        report = analyze_wav(self.path, expected_frequency=440)
        self.assertEqual(report["stereo"],
                         {"applicable": True, "identical": True, "differing_frames": 0})
        self.assertEqual(report["amplitude"]["unit"], "normalized_pcm")
        for channel in report["channels"]:
            for key in ("peak", "rms", "dc", "nonzero_sample_count", "full_scale_sample_count"):
                self.assertEqual(channel[key], 0, key)
            self.assertEqual(channel["sample_count"], 257)
            estimate = channel["frequency_estimate"]
            self.assertEqual(estimate["status"], "insufficient_crossings")
            self.assertIsNone(estimate["candidate_frequency_hz"])

    def test_dc_metrics_and_no_calibration_or_clipping_inference(self):
        self.fixture([(8192,)] * 19)
        original = self.path.read_bytes()
        report = analyze_wav(self.path, expected_frequency=100)
        channel = report["channels"][0]
        self.assertEqual([channel[key] for key in ("peak", "rms", "dc")], [0.25] * 3)
        self.assertEqual(channel["nonzero_sample_count"], 19)
        self.assertEqual(report["stereo"]["applicable"], False)
        self.assertIsNone(report["stereo"]["identical"])
        self.assertIsNone(report["clipping"]["confirmed_pre_quantization_clipping"])
        self.assertIn("not volts or pascals", report["amplitude"]["calibration"])
        self.assertEqual(self.path.read_bytes(), original)

    def test_independent_sine_quantization_bounds_and_crossings(self):
        samples = [round(0.4 * 32768 * math.sin(2 * math.pi * 440 * i / 48000))
                   for i in range(48000)]
        self.fixture([(sample,) for sample in samples])
        report = analyze_wav(self.path, expected_frequency=440)
        channel = report["channels"][0]
        self.assertAlmostEqual(channel["peak"], 0.4, delta=PCM_STEP / 2)
        self.assertAlmostEqual(channel["rms"], 0.4 / math.sqrt(2), delta=PCM_STEP / 2)
        self.assertAlmostEqual(channel["dc"], 0, delta=PCM_STEP / 2)
        frequency = channel["frequency_estimate"]
        self.assertEqual(frequency["status"], "estimated_under_fixture_assumption")
        self.assertAlmostEqual(frequency["candidate_frequency_hz"], 440, delta=0.005)
        self.assertGreater(frequency["complete_periods"], 430)
        self.assertEqual(channel["full_scale_sample_count"], 0)

    def test_inverted_channels_and_crossings_across_stream_blocks(self):
        samples = [round(12000 * math.sin(2 * math.pi * 440 * i / 48000 + 0.13))
                   for i in range(10003)]
        self.fixture([(sample, -sample) for sample in samples], channels=2)
        report = analyze_wav(self.path, expected_frequency=440)
        self.assertFalse(report["stereo"]["identical"])
        self.assertEqual(report["stereo"]["differing_frames"], sum(value != 0 for value in samples))
        left, right = report["channels"]
        self.assertEqual(left["peak"], right["peak"])
        self.assertEqual(left["rms"], right["rms"])
        self.assertEqual(left["dc"], -right["dc"])
        for channel in (left, right):
            self.assertAlmostEqual(channel["frequency_estimate"]["candidate_frequency_hz"],
                                   440, delta=0.005)

    def test_full_scale_codes_are_not_confirmed_clipping(self):
        values = [-32768, 32767, 0, -32768, 32767]
        self.fixture([(sample,) for sample in values])
        report = analyze_wav(self.path)
        channel = report["channels"][0]
        self.assertEqual(channel["peak"], 1)
        self.assertEqual(channel["dc"], -2 / (5 * 32768))
        self.assertEqual(channel["rms"], math.sqrt(sum(x * x for x in values) / 5) / 32768)
        self.assertEqual(channel["full_scale_sample_count"], 4)
        self.assertEqual(channel["positive_full_scale_sample_count"], 2)
        self.assertEqual(channel["negative_full_scale_sample_count"], 2)
        self.assertEqual(report["clipping"]["full_scale_channel_samples"], 4)
        self.assertIsNone(report["clipping"]["confirmed_pre_quantization_clipping"])
        self.assertEqual(report["clipping"]["pre_quantization_status"], "not_inferable_from_pcm16")
        self.assertIsNone(channel["frequency_estimate"])

    def test_window_is_half_open_and_stereo_comparison_uses_only_window(self):
        self.fixture([(100, -100)] * 5 + [(8192, 8192)] * 11 + [(32767, 0)] * 7, channels=2)
        report = analyze_wav(self.path, start_frame=5, end_frame=16)
        self.assertEqual(report["format"]["total_frames"], 23)
        self.assertEqual(report["window"]["frames"], 11)
        self.assertEqual(report["window"]["start_frame"], 5)
        self.assertEqual(report["window"]["end_frame"], 16)
        self.assertTrue(report["stereo"]["identical"])
        self.assertEqual(report["channels"][0]["rms"], 0.25)
        self.assertEqual(report["clipping"]["full_scale_channel_samples"], 0)

    def test_frequency_ambiguity_for_zero_plateaus_and_declared_mismatch(self):
        # Each repeating period has three exact zeros between negative and positive.
        self.fixture([(-100,), (0,), (0,), (0,), (100,), (100,), (0,), (-100,)] * 10,
                     rate=8000)
        report = analyze_wav(self.path, expected_frequency=400)
        estimate = report["channels"][0]["frequency_estimate"]
        self.assertEqual(estimate["status"], "ambiguous")
        self.assertEqual(estimate["candidate_frequency_hz"], 1000)
        self.assertIn("multiple_zero_samples_at_a_rising_crossing", estimate["ambiguity_flags"])
        self.assertIn("crossing_rate_differs_from_expected_by_over_1_percent",
                      estimate["ambiguity_flags"])

    def test_multichannel_metrics_and_no_stereo_claim(self):
        self.fixture([(100, -200, 0)] * 31, channels=3)
        report = analyze_wav(self.path)
        self.assertEqual(len(report["channels"]), 3)
        self.assertEqual(report["channels"][1]["dc"], -200 / 32768)
        self.assertFalse(report["stereo"]["applicable"])
        self.assertIsNone(report["stereo"]["differing_frames"])

    def test_ancillary_padding_and_empty_pcm_extension(self):
        original = pcm_bytes([(123,)] * 5)
        fmt = original[20:36]
        self.path.write_bytes(riff([(b"JUNK", b"abc"), (b"fmt ", fmt + b"\x00\x00"),
                                    (b"data", original[44:]), (b"LIST", b"x")]))
        self.assertEqual(analyze_wav(self.path)["channels"][0]["peak"], 123 / 32768)

    def test_truncation_sizes_and_partial_frames_rejected(self):
        valid = pcm_bytes([(10, 20)] * 13, channels=2)
        for length in (0, 8, 12, 20, 35, 43, len(valid) - 1):
            with self.subTest(truncated_to=length):
                self.reject(valid[:length])
        for claimed in (0, len(valid) - 9, len(valid), 0xFFFFFFFF):
            broken = bytearray(valid)
            struct.pack_into("<I", broken, 4, claimed)
            with self.subTest(riff_size=claimed):
                self.reject(broken)
        self.reject(riff([(b"fmt ", valid[20:36]), (b"data", b"\x00\x00\x00")]))
        # Truncation outside a requested window must still be rejected.
        self.path.write_bytes(valid[:-4])
        with self.assertRaises(AnalysisError):
            analyze_wav(self.path, end_frame=1)

    def test_unsupported_and_inconsistent_format_fields_rejected(self):
        valid = pcm_bytes([(1, 2)] * 3, channels=2)
        mutations = [(0, "4s", b"RIFX"), (8, "4s", b"NOPE"),
                     (20, "H", 3), (20, "H", 0xFFFE), (22, "H", 0), (22, "H", 9),
                     (24, "I", 0), (24, "I", 192001), (28, "I", 1),
                     (32, "H", 2), (34, "H", 8), (34, "H", 32)]
        for offset, kind, value in mutations:
            with self.subTest(offset=offset, value=value):
                broken = bytearray(valid)
                struct.pack_into("<" + kind, broken, offset, value)
                self.reject(broken)
        # IEEE float payload includes NaN, but is rejected as unsupported format.
        floating_fmt = struct.pack("<HHIIHH", 3, 1, 48000, 192000, 4, 32)
        self.reject(riff([(b"fmt ", floating_fmt), (b"data", struct.pack("<f", math.nan))]))

    def test_duplicate_missing_disordered_and_oversized_chunks_rejected(self):
        valid = pcm_bytes([(1,)] * 3)
        fmt, data = (b"fmt ", valid[20:36]), (b"data", valid[44:])
        cases = [[fmt, fmt, data], [fmt, data, data], [data, fmt], [fmt],
                 [(b"JUNK", b"a" * 40)], [fmt, (b"data", b"")],
                 [(b"fmt ", fmt[1] + b"\x01\x00"), data],
                 [(b"fmt ", fmt[1] + b"\x00" * 24), data],
                 [fmt, data] + [(b"JUNK", b"")] * 1023]
        for index, chunks in enumerate(cases):
            with self.subTest(case=index):
                self.reject(riff(chunks))
        broken = bytearray(valid)
        struct.pack_into("<I", broken, 40, 0xFFFFFFFF)
        self.reject(broken)

    def test_file_duration_and_numeric_limits_rejected(self):
        self.fixture([(1,)] * 601, rate=1)
        with self.assertRaisesRegex(AnalysisError, "duration"):
            analyze_wav(self.path)
        with self.path.open("wb") as stream:
            stream.truncate(256 * 1024 * 1024 + 1)
        with self.assertRaisesRegex(AnalysisError, "File size"):
            analyze_wav(self.path)
        self.fixture([(1,)] * 100)
        invalid = [{"start_frame": -1}, {"start_frame": True}, {"start_frame": 1.0},
                   {"start_frame": 100}, {"end_frame": 101}, {"end_frame": 0},
                   {"start_frame": 40, "end_frame": 39}, {"end_frame": 10 ** 100},
                   *({"expected_frequency": x} for x in
                     (math.nan, math.inf, -math.inf, 0, -1, 24000, True, "440", 10 ** 1000))]
        for arguments in invalid:
            with self.subTest(arguments=arguments), self.assertRaises(AnalysisError):
                analyze_wav(self.path, **arguments)

    def test_cli_json_and_strict_numeric_rejection_preserve_source(self):
        self.fixture([(123, 123)] * 30, channels=2)
        original = self.path.read_bytes()
        command = [sys.executable, str(ANALYZER), "--input", str(self.path)]
        result = subprocess.run(command + ["--start-frame", "2", "--end-frame", "22",
                                          "--expected-frequency", "440"],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout, parse_constant=lambda value: self.fail(value))
        self.assertEqual(report["window"]["frames"], 20)
        self.assertEqual(report["frequency"]["expected_frequency_hz"], 440)
        for flag, token in [("--start-frame", "-1"), ("--start-frame", "1.5"),
                            ("--end-frame", "999999999999999999999999"),
                            *( ("--expected-frequency", x) for x in
                               ("nan", "inf", "1e999", "0", "24000", "1_000"))]:
            with self.subTest(flag=flag, token=token):
                rejected = subprocess.run(command + [flag, token], capture_output=True,
                                          text=True, timeout=10)
                self.assertEqual(rejected.returncode, 2)
                self.assertEqual(rejected.stdout, "")
                self.assertTrue(rejected.stderr)
        self.assertEqual(self.path.read_bytes(), original)


def required_path(environment_name, default):
    path = Path(os.environ.get(environment_name, default))
    if not path.is_file():
        raise RuntimeError(f"Missing {environment_name}: {path}. Build hammond_render and "
                           "nominal.b3p or set the explicit environment paths; integration not run.")
    return path.resolve()


class RealRendererIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        name = "hammond_render.exe" if os.name == "nt" else "hammond_render"
        cls.renderer = required_path("HAMMOND_RENDER_EXECUTABLE", ROOT / "build" / name)
        if not os.access(cls.renderer, os.X_OK):
            raise RuntimeError(f"Renderer is not executable: {cls.renderer}")
        cls.profile = required_path("HAMMOND_TEST_PROFILE", cls.renderer.parent / "nominal.b3p")

    def test_actual_cpp_a4_fixture_with_pcm_quantization_tolerances(self):
        with tempfile.TemporaryDirectory(prefix="hammond-analysis-render-") as temporary:
            output = Path(temporary) / "real A4.wav"
            command = [str(self.renderer), "--profile", str(self.profile), "--output", str(output),
                       "--sample-rate", "48000", "--block-size", "127", "--frames", "48000",
                       "--seed", "0", "--drawbars", "008000000", "--note", "69", "--fail-on-clip"]
            result = subprocess.run(command, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            producer = json.loads(result.stdout, parse_constant=lambda value: self.fail(value))
            full = analyze_wav(output)
            # This fixture has ample PCM headroom: nearest rounding contributes
            # <= half a PCM step, inherited by the RMS norm and absolute peak.
            self.assertEqual(producer["clipped_frames"], 0)
            self.assertAlmostEqual(full["channels"][0]["peak"], producer["peak"],
                                   delta=PCM_STEP / 2 + 1e-12)
            self.assertAlmostEqual(full["channels"][0]["rms"], producer["rms"],
                                   delta=PCM_STEP / 2 + 1e-12)
            # 4800..28800 is 220 complete nominal cycles, before note-off at 36000.
            report = analyze_wav(output, start_frame=4800, end_frame=28800, expected_frequency=440)
            self.assertEqual(report["format"]["total_frames"], 48000)
            self.assertTrue(report["stereo"]["identical"])
            channel = report["channels"][0]
            self.assertEqual(channel["full_scale_sample_count"], 0)
            self.assertGreater(channel["nonzero_sample_count"], 23760)
            self.assertAlmostEqual(channel["peak"], 0.03, delta=PCM_STEP)
            self.assertAlmostEqual(channel["rms"], 0.03 / math.sqrt(2),
                                   delta=PCM_STEP / 2 + 1e-7)
            self.assertAlmostEqual(channel["dc"], 0, delta=PCM_STEP / 2 + 1e-7)
            frequency = channel["frequency_estimate"]
            self.assertEqual(frequency["status"], "estimated_under_fixture_assumption")
            # At amplitude .03, half a code moves a 440-Hz crossing about .009
            # frame. Two endpoints over ~0.5 s contribute ~0.00034 Hz; .005 Hz
            # also covers sine interpolation and the core's float samples.
            self.assertAlmostEqual(frequency["candidate_frequency_hz"], 440, delta=0.005)


if __name__ == "__main__":
    unittest.main()
