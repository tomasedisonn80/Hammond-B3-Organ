#!/usr/bin/env python3
"""Independent sample/format acceptance for capture-audio-v1.

Fixtures use literal bytes and this test's small RIFF writer. Expected samples,
counts and digests never call a production parser, statistic or digest helper.
Deep malformed/resource/filesystem acceptance belongs to a separate suite.
"""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from decimal import Decimal, localcontext
import hashlib
import io
import json
import math
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from capture_audio import (  # noqa: E402
    AudioError, inspect_audio, main, read_audio_window,
)
import capture_audio  # noqa: E402


A_HEX = (
    "524946463400000057415645666d7420100000000100020080bb000000ee020004001000"
    "646174611000000000000020004000e000c00060000000a0"
)
A_BYTES = bytes.fromhex(A_HEX)
A_FRAMES = [(0.0, 0.25), (0.5, -0.25), (-0.5, 0.75), (0.0, -0.75)]
A_FILE_SHA = "5b56dc77fda85da22f9346b0d250c56bdf467a0d073bb07663db4f07702ed9ac"
A_DECODED_SHA = "6b650fe3f66cfaec1d3ad75b2a91716b3a1868a7a2d3d1b0cc9ebb1b4f641d55"
A_44100_SHA = "fe1772f596b6b7c4ff1a09704ebf59e791330e01f5a76143b364aea2b4551449"
A_SWAPPED_SHA = "9d3372f8b3fcad782a640c25d7cff8c3696bed39b36feafc7b1f4b6de4a52df8"
A_MONO_SHA = "1c109115de62460b2e716478bed19d044a6ccaebd18859b53083cb57792c3d81"
C_BYTES = bytes.fromhex(
    "00000000000000800000803f000080bf0000a03f0000c0bf0000003f000080be"
)
C_VALUES = [0.0, -0.0, 1.0, -1.0, 1.25, -1.5, 0.5, -0.25]
C_FILE_SHA = "a537928ab210bdc28f972326557be866963cf75a254529433785b1c100814f46"
C_DECODED_SHA = "6125d66e14d8eba940491f56e21d047b507f10e75841605658432fc8c08cbb57"

REPORT_FIELDS = {
    "schema_version", "inspector_version", "status", "input_path", "size_bytes",
    "sha256", "decoded_digest_version", "decoded_sha256", "format", "container",
    "bits_per_sample", "sample_rate_hz", "channel_count", "frame_count",
    "duration_seconds", "data_offset_bytes", "data_size_bytes", "chunk_count",
    "amplitude_unit", "channels", "clipping", "evidence_scope", "authenticity",
    "physical_clock", "calibration", "physical_fidelity",
}
CHANNEL_FIELDS = {
    "channel_index", "sample_count", "peak", "rms", "dc", "nonzero_sample_count",
    "positive_full_scale_sample_count", "negative_full_scale_sample_count",
    "full_scale_sample_count", "positive_over_full_scale_sample_count",
    "negative_over_full_scale_sample_count", "over_full_scale_sample_count",
}
WINDOW_FIELDS = {
    "schema_version", "window_version", "inspection", "start_frame",
    "frame_count", "end_frame", "samples",
}


def chunk(name, payload, pad=b"\x00"):
    """Independent small-fixture RIFF encoder, including caller-selected pad."""
    assert type(name) is bytes and len(name) == 4
    return name + len(payload).to_bytes(4, "little") + payload + (pad if len(payload) % 2 else b"")


def riff(chunks):
    body = b"WAVE" + b"".join(chunks)
    return b"RIFF" + len(body).to_bytes(4, "little") + body


def fmt(width, channels=1, rate=48000, *, floating=False, extended=False):
    alignment = channels * width // 8
    result = struct.pack("<HHIIHH", 3 if floating else 1, channels,
                         rate, rate * alignment, alignment, width)
    return result + (b"\x00\x00" if extended else b"")


def wave(payload, width, channels=1, rate=48000, *, floating=False,
         extended=False, before=(), after=(), data_pad=b"\x00"):
    return riff([chunk(b"fmt ", fmt(width, channels, rate, floating=floating,
                                   extended=extended)), *before,
                 chunk(b"data", payload, data_pad), *after])


def pcm_payload(frames, width):
    scale = 1 << (width - 1)
    return b"".join(int(value * scale).to_bytes(width // 8, "little", signed=True)
                    for frame in frames for value in frame)


def float_payload(frames, width):
    format_string = "<f" if width == 32 else "<d"
    return b"".join(struct.pack(format_string, value) for frame in frames for value in frame)


def decoded_oracle(frames, rate=48000):
    """Literal contract byte construction, independent of production helpers."""
    channel_count = len(frames[0])
    preamble = (b"HAMMOND-CAPTURE-DECODED-V1\x00"
                + rate.to_bytes(4, "little")
                + channel_count.to_bytes(4, "little")
                + len(frames).to_bytes(8, "little"))
    samples = b"".join(struct.pack("<d", 0.0 if value == 0 else value)
                       for frame in frames for value in frame)
    return hashlib.sha256(preamble + samples).hexdigest()


def decimal_stats(values):
    with localcontext() as context:
        context.prec = 120
        exact = [Decimal.from_float(float(value)) for value in values]
        count = Decimal(len(exact))
        dc = sum(exact, Decimal(0)) / count
        rms = (sum((value * value for value in exact), Decimal(0)) / count).sqrt()
        return float(dc), float(rms)


class AudioAcceptance(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="capture-audio-acceptance-")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)

    def write(self, content, name="capture.wav"):
        path = self.directory / name
        path.write_bytes(content)
        return path

    def assert_error(self, code, operation, *args, **kwargs):
        with self.assertRaises(AudioError) as caught:
            operation(*args, **kwargs)
        error = caught.exception
        self.assertIsInstance(error, ValueError)
        self.assertEqual(error.code, code)
        self.assertIs(type(error.message), str)
        self.assertTrue(error.message.strip())
        self.assertIs(type(error.details), dict)
        self.assertIn(code, str(error))
        self.assertIn(error.message, str(error))
        json.dumps(error.details, allow_nan=False)
        return error

    def assert_close(self, observed, expected):
        self.assertLessEqual(abs(observed - expected), max(2e-12, 2e-12 * abs(expected)))

    def assert_channel(self, observed, values, *, index=0, pcm_width=None):
        self.assertEqual(set(observed), CHANNEL_FIELDS)
        self.assertEqual(observed["channel_index"], index)
        self.assertEqual(observed["sample_count"], len(values))
        self.assertEqual(observed["peak"], max(abs(value) for value in values))
        dc, rms = decimal_stats(values)
        self.assert_close(observed["dc"], dc)
        self.assert_close(observed["rms"], rms)
        positive_endpoint = 1.0 if pcm_width is None else 1.0 - 2.0 ** (1 - pcm_width)
        positive_full = sum(value == positive_endpoint for value in values)
        negative_full = sum(value == -1.0 for value in values)
        positive_over = 0 if pcm_width else sum(value > 1.0 for value in values)
        negative_over = 0 if pcm_width else sum(value < -1.0 for value in values)
        expected_counts = {
            "nonzero_sample_count": sum(value != 0.0 for value in values),
            "positive_full_scale_sample_count": positive_full,
            "negative_full_scale_sample_count": negative_full,
            "full_scale_sample_count": positive_full + negative_full,
            "positive_over_full_scale_sample_count": positive_over,
            "negative_over_full_scale_sample_count": negative_over,
            "over_full_scale_sample_count": positive_over + negative_over,
        }
        for name, expected in expected_counts.items():
            self.assertIs(type(observed[name]), int)
            self.assertEqual(observed[name], expected, name)

    def assert_report(self, report, path, frames, *, format_name, bits, rate=48000):
        self.assertEqual(set(report), REPORT_FIELDS)
        self.assertEqual(report["schema_version"], 1)
        self.assertIs(type(report["schema_version"]), int)
        self.assertEqual(report["inspector_version"], "capture-audio-v1")
        self.assertEqual(report["status"], "inspected")
        self.assertEqual(report["input_path"], str(path.parent.resolve() / path.name))
        self.assertEqual(report["size_bytes"], len(path.read_bytes()))
        self.assertEqual(report["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
        self.assertEqual(report["decoded_digest_version"], "hammond-capture-decoded-v1")
        self.assertEqual(report["decoded_sha256"], decoded_oracle(frames, rate))
        self.assertEqual(report["format"], format_name)
        self.assertEqual(report["container"], "raw" if format_name == "raw_float32_le" else "RIFF/WAVE")
        self.assertEqual(report["bits_per_sample"], bits)
        self.assertEqual(report["sample_rate_hz"], rate)
        self.assertEqual(report["channel_count"], len(frames[0]))
        self.assertEqual(report["frame_count"], len(frames))
        self.assertEqual(report["duration_seconds"], len(frames) / rate)
        self.assertEqual(report["data_size_bytes"], len(frames) * len(frames[0]) * bits // 8)
        self.assertEqual(report["amplitude_unit"], "digital_full_scale")
        self.assertEqual(report["evidence_scope"], "decoded-digital-audio-only")
        for field in ("authenticity", "physical_clock", "calibration", "physical_fidelity"):
            self.assertEqual(report[field], "not_established")
        self.assertEqual(len(report["channels"]), len(frames[0]))
        for channel, observed in enumerate(report["channels"]):
            self.assert_channel(observed, [frame[channel] for frame in frames], index=channel,
                                pcm_width=bits if format_name.startswith("wav_pcm") else None)
        clipping = report["clipping"]
        self.assertEqual(set(clipping), {"full_scale_channel_samples", "over_full_scale_channel_samples",
                                         "confirmed_pre_encoding_clipping", "pre_encoding_status"})
        self.assertEqual(clipping["full_scale_channel_samples"],
                         sum(row["full_scale_sample_count"] for row in report["channels"]))
        self.assertEqual(clipping["over_full_scale_channel_samples"],
                         sum(row["over_full_scale_sample_count"] for row in report["channels"]))
        self.assertIsNone(clipping["confirmed_pre_encoding_clipping"])
        self.assertEqual(clipping["pre_encoding_status"], "not_inferable_from_samples")
        # Strict JSON serialization must succeed without a default conversion.
        json.dumps(report, allow_nan=False)

    def run_cli(self, *arguments):
        return subprocess.run([sys.executable, "-B", str(ROOT / "tools" / "capture_audio.py"),
                               *map(str, arguments)], cwd=self.directory,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)

    def test_literal_a_full_report_and_two_literal_hashes(self):
        self.assertEqual(len(A_BYTES), 60)
        self.assertEqual(hashlib.sha256(A_BYTES).hexdigest(), A_FILE_SHA)
        self.assertEqual(decoded_oracle(A_FRAMES), A_DECODED_SHA)
        path = self.write(A_BYTES)
        report = inspect_audio(path)
        self.assert_report(report, path, A_FRAMES, format_name="wav_pcm16", bits=16)
        self.assertEqual(report["sha256"], A_FILE_SHA)
        self.assertEqual(report["decoded_sha256"], A_DECODED_SHA)
        self.assertEqual((report["data_offset_bytes"], report["data_size_bytes"], report["chunk_count"]),
                         (44, 16, 2))

    def test_literal_a_independent_rms_and_counts(self):
        channels = inspect_audio(self.write(A_BYTES))["channels"]
        self.assertEqual(channels[0]["peak"], 0.5)
        self.assertEqual(channels[1]["peak"], 0.75)
        self.assert_close(channels[0]["rms"], math.sqrt(1 / 8))
        self.assert_close(channels[1]["rms"], math.sqrt(5 / 16))
        self.assertEqual([item["dc"] for item in channels], [0.0, 0.0])
        self.assertEqual([item["nonzero_sample_count"] for item in channels], [2, 4])
        self.assertEqual([item["full_scale_sample_count"] for item in channels], [0, 0])

    def test_same_samples_match_all_six_encodings(self):
        byte_hashes = set()
        for floating, width in ((False, 16), (False, 24), (False, 32), (True, 32), (True, 64)):
            token = f"wav_{'float' if floating else 'pcm'}{width}"
            with self.subTest(token=token):
                data = float_payload(A_FRAMES, width) if floating else pcm_payload(A_FRAMES, width)
                path = self.write(wave(data, width, 2, floating=floating), token + ".wav")
                report = inspect_audio(path)
                self.assert_report(report, path, A_FRAMES, format_name=token, bits=width)
                self.assertEqual(report["decoded_sha256"], A_DECODED_SHA)
                byte_hashes.add(report["sha256"])
        path = self.write(float_payload(A_FRAMES, 32), "stream.f32")
        report = inspect_audio(path, raw_format="raw_float32_le", sample_rate_hz=48000, channel_count=2)
        self.assert_report(report, path, A_FRAMES, format_name="raw_float32_le", bits=32)
        self.assertEqual(report["decoded_sha256"], A_DECODED_SHA)
        self.assertEqual((report["data_offset_bytes"], report["chunk_count"]), (0, 0))
        byte_hashes.add(report["sha256"])
        self.assertEqual(len(byte_hashes), 6)

    def test_rate_changes_the_printed_decoded_identity(self):
        path = self.write(wave(pcm_payload(A_FRAMES, 16), 16, 2, 44100))
        report = inspect_audio(path)
        self.assertEqual(report["decoded_sha256"], A_44100_SHA)
        self.assertEqual(decoded_oracle(A_FRAMES, 44100), A_44100_SHA)
        self.assertNotEqual(report["decoded_sha256"], A_DECODED_SHA)

    def test_channel_swap_changes_the_printed_decoded_identity(self):
        frames = [(right, left) for left, right in A_FRAMES]
        path = self.write(wave(pcm_payload(frames, 16), 16, 2))
        report = inspect_audio(path)
        self.assertEqual(report["decoded_sha256"], A_SWAPPED_SHA)
        self.assertEqual(decoded_oracle(frames), A_SWAPPED_SHA)
        self.assertNotEqual(report["decoded_sha256"], A_DECODED_SHA)

    def test_mono_geometry_changes_the_printed_decoded_identity(self):
        frames = [(value,) for frame in A_FRAMES for value in frame]
        path = self.write(wave(pcm_payload(frames, 16), 16))
        report = inspect_audio(path)
        self.assertEqual(report["decoded_sha256"], A_MONO_SHA)
        self.assertEqual(decoded_oracle(frames), A_MONO_SHA)
        self.assertEqual((report["channel_count"], report["frame_count"]), (1, 8))

    def test_pcm_edge_codes_and_one_lsb_are_exact_at_each_width(self):
        data = {16: "0080ffff00000100ff7f", 24: "000080ffffff000000010000ffff7f",
                32: "00000080ffffffff0000000001000000ffffff7f"}
        identities = set()
        for width, hex_data in data.items():
            with self.subTest(width=width):
                q = 1 << (width - 1)
                expected = [-1.0, -1 / q, 0.0, 1 / q, (q - 1) / q]
                path = self.write(wave(bytes.fromhex(hex_data), width), f"edge-{width}.wav")
                result = read_audio_window(path, 0, 5)
                self.assertEqual(result["samples"], [expected])
                self.assert_channel(result["inspection"]["channels"][0], expected, pcm_width=width)
                self.assertEqual(result["inspection"]["channels"][0]["dc"], -1 / (5 * q))
                self.assert_close(result["inspection"]["channels"][0]["rms"],
                                  math.sqrt((2 * q * q - 2 * q + 3) / 5) / q)
                self.assertEqual(result["inspection"]["data_size_bytes"], 5 * width // 8)
                identities.add(result["inspection"]["decoded_sha256"])
        self.assertEqual(len(identities), 3)

    def test_pcm24_pad_is_outside_samples_and_in_byte_identity(self):
        data = bytes.fromhex("000080ffffff000000010000ffff7f")
        left = self.write(wave(data, 24, data_pad=b"\x00"), "pad-zero.wav")
        right = self.write(wave(data, 24, data_pad=b"\xA5"), "pad-other.wav")
        a, b = inspect_audio(left), inspect_audio(right)
        self.assertEqual(a["data_size_bytes"], 15)
        self.assertEqual(a["frame_count"], 5)
        self.assertEqual(a["decoded_sha256"], b["decoded_sha256"])
        self.assertEqual(a["channels"], b["channels"])
        self.assertNotEqual(a["sha256"], b["sha256"])

    def test_float32_is_widened_exactly_and_float64_is_not_narrowed(self):
        stored32 = [0.1, -0.1, 1.0 + 2 ** -23, -(1.0 + 2 ** -23)]
        expected32 = [struct.unpack("<f", struct.pack("<f", value))[0] for value in stored32]
        path32 = self.write(wave(float_payload([(v,) for v in stored32], 32), 32, floating=True), "binary32.wav")
        self.assertEqual(read_audio_window(path32, 0, 4)["samples"], [expected32])
        stored64 = [0.1, -0.1, 1.0 + 2 ** -40, -(1.0 + 2 ** -40)]
        path64 = self.write(wave(float_payload([(v,) for v in stored64], 64), 64, floating=True), "binary64.wav")
        actual64 = read_audio_window(path64, 0, 4)
        self.assertEqual(actual64["samples"], [stored64])
        self.assertNotEqual(actual64["inspection"]["decoded_sha256"], inspect_audio(path32)["decoded_sha256"])

    def test_literal_c_hashes_endpoints_headroom_and_stats(self):
        self.assertEqual(hashlib.sha256(C_BYTES).hexdigest(), C_FILE_SHA)
        path = self.write(C_BYTES, "literal.f32")
        report = inspect_audio(path, raw_format="raw_float32_le", sample_rate_hz=48000, channel_count=1)
        self.assert_report(report, path, [(v,) for v in C_VALUES], format_name="raw_float32_le", bits=32)
        self.assertEqual(report["sha256"], C_FILE_SHA)
        self.assertEqual(report["decoded_sha256"], C_DECODED_SHA)
        self.assertEqual(report["channels"][0]["rms"], 0.875)
        self.assertEqual(report["clipping"]["full_scale_channel_samples"], 2)
        self.assertEqual(report["clipping"]["over_full_scale_channel_samples"], 2)
        self.assertIsNone(report["clipping"]["confirmed_pre_encoding_clipping"])

    def test_signed_zero_changes_bytes_but_not_decoded_identity(self):
        negative = self.write(C_BYTES, "minus-zero.f32")
        positive_bytes = C_BYTES[:4] + b"\x00" * 4 + C_BYTES[8:]
        positive = self.write(positive_bytes, "plus-zero.f32")
        options = {"raw_format": "raw_float32_le", "sample_rate_hz": 48000, "channel_count": 1}
        a, b = read_audio_window(negative, 0, 8, **options), read_audio_window(positive, 0, 8, **options)
        self.assertEqual(a["inspection"]["decoded_sha256"], C_DECODED_SHA)
        self.assertEqual(b["inspection"]["decoded_sha256"], C_DECODED_SHA)
        self.assertNotEqual(a["inspection"]["sha256"], b["inspection"]["sha256"])
        self.assertEqual(a["samples"], b["samples"])
        for value in a["samples"][0][:2]:
            self.assertEqual(struct.pack("<d", value), b"\x00" * 8)

    def test_float_wrappers_share_literal_c_decoded_identity(self):
        for width in (32, 64):
            with self.subTest(width=width):
                frames = [(value,) for value in C_VALUES]
                path = self.write(wave(float_payload(frames, width), width, floating=True), f"c-{width}.wav")
                report = inspect_audio(path)
                self.assert_report(report, path, frames, format_name=f"wav_float{width}", bits=width)
                self.assertEqual(report["decoded_sha256"], C_DECODED_SHA)

    def test_silence_has_positive_zero_stats_and_no_counts(self):
        for width, floating in ((16, False), (24, False), (32, False), (32, True), (64, True)):
            with self.subTest(width=width, floating=floating):
                frames = [(-0.0, 0.0), (0.0, -0.0)]
                data = float_payload(frames, width) if floating else pcm_payload(frames, width)
                result = read_audio_window(self.write(wave(data, width, 2, floating=floating)), 0, 2)
                for channel in result["inspection"]["channels"]:
                    for field in ("peak", "rms", "dc"):
                        self.assertEqual(struct.pack("<d", channel[field]), b"\x00" * 8)
                    self.assertEqual(channel["nonzero_sample_count"], 0)
                    self.assertEqual(channel["full_scale_sample_count"], 0)
                    self.assertEqual(channel["over_full_scale_sample_count"], 0)
                for values in result["samples"]:
                    self.assertTrue(all(struct.pack("<d", value) == b"\x00" * 8 for value in values))

    def test_least_binary64_subnormal_survives_rms_and_dc(self):
        tiny = float.fromhex("0x0.0000000000001p-1022")
        path = self.write(wave(bytes.fromhex("0100000000000000") * 4, 64, floating=True))
        result = read_audio_window(path, 0, 4)
        self.assertEqual(result["samples"], [[tiny] * 4])
        observed = result["inspection"]["channels"][0]
        for field in ("peak", "rms", "dc"):
            self.assertEqual(observed[field], tiny, field)
        self.assertEqual(observed["nonzero_sample_count"], 4)
        self.assertEqual(result["inspection"]["decoded_sha256"], decoded_oracle([(tiny,)] * 4))

    def test_binary32_subnormal_is_not_flushed_or_narrowed(self):
        tiny = 2.0 ** -149
        path = self.write(wave(bytes.fromhex("01000000") * 4, 32, floating=True))
        result = read_audio_window(path, 0, 4)
        self.assertEqual(result["samples"], [[tiny] * 4])
        for field in ("peak", "rms", "dc"):
            self.assertEqual(result["inspection"]["channels"][0][field], tiny)

    def test_float64_cancellation_uses_exact_stored_decimal_oracle(self):
        values = [1e6, 1e-9, -1e6, 1e-9]
        path = self.write(wave(float_payload([(v,) for v in values], 64), 64, floating=True))
        channel = inspect_audio(path)["channels"][0]
        dc, rms = decimal_stats(values)
        self.assert_close(channel["dc"], dc)
        self.assert_close(channel["rms"], rms)
        # Use an explicit loop: Python 3.12's built-in sum already improves
        # floating-point accumulation and is not a naive control calculation.
        naive_total = 0.0
        for value in values:
            naive_total += value
        self.assertGreater(abs(naive_total / len(values) - dc), 2e-12)

    def test_mixed_float_magnitudes_match_decimal_statistics(self):
        values = [1e6, 1e-6, -1e5, 2 ** -100, -2 ** -100, 3.5, -17.0, 0.0] * 37
        path = self.write(wave(float_payload([(v,) for v in values], 64), 64, floating=True))
        self.assert_channel(inspect_audio(path)["channels"][0], values)

    def test_channels_are_not_folded_or_averaged(self):
        frames = [(0.5, -0.5, 0.25), (-0.5, 0.5, 0.25), (0.0, 0.0, 0.25)]
        path = self.write(wave(float_payload(frames, 64), 64, 3, floating=True))
        report = inspect_audio(path)
        self.assert_report(report, path, frames, format_name="wav_float64", bits=64)
        self.assertEqual(report["channels"][2]["dc"], 0.25)
        self.assertGreater(report["channels"][0]["rms"], 0.0)
        self.assertEqual(read_audio_window(path, 0, 3)["samples"], [list(v) for v in zip(*frames)])

    def test_sixteen_channel_order_and_rate_endpoints(self):
        frames = [tuple((channel - 8) / 16 for channel in range(16)),
                  tuple((7 - channel) / 16 for channel in range(16))]
        for rate in (1, 768000):
            with self.subTest(rate=rate):
                path = self.write(wave(pcm_payload(frames, 24), 24, 16, rate), f"rate-{rate}.wav")
                report = inspect_audio(path)
                self.assert_report(report, path, frames, format_name="wav_pcm24", bits=24, rate=rate)
                self.assertEqual(read_audio_window(path, 0, 2)["samples"], [list(v) for v in zip(*frames)])

    def test_literal_window_has_exact_shape_order_and_complete_report(self):
        path = self.write(A_BYTES)
        result = read_audio_window(path, 1, 2)
        self.assertEqual(set(result), WINDOW_FIELDS)
        self.assertEqual(result["schema_version"], 1)
        self.assertEqual(result["window_version"], "capture-audio-window-v1")
        self.assertEqual((result["start_frame"], result["frame_count"], result["end_frame"]), (1, 2, 3))
        self.assertEqual(result["samples"], [[0.5, -0.5], [-0.25, 0.75]])
        self.assertEqual(result["inspection"], inspect_audio(path))

    def test_first_last_and_whole_windows_have_no_padding_or_shift(self):
        path = self.write(A_BYTES)
        self.assertEqual(read_audio_window(path, 0, 1)["samples"], [[0.0], [0.25]])
        self.assertEqual(read_audio_window(path, 3, 1)["samples"], [[0.0], [-0.75]])
        self.assertEqual(read_audio_window(path, 0, 4)["samples"], [[0.0, 0.5, -0.5, 0.0], [0.25, -0.25, 0.75, -0.75]])

    def test_returned_windows_are_independent_values_and_source_is_preserved(self):
        path = self.write(A_BYTES)
        first = read_audio_window(path, 1, 2)
        first["samples"][0][0] = 99.0
        first["inspection"]["channels"][0]["peak"] = 99.0
        second = read_audio_window(path, 1, 2)
        self.assertEqual(second["samples"], [[0.5, -0.5], [-0.25, 0.75]])
        self.assertEqual(second["inspection"]["channels"][0]["peak"], 0.5)
        self.assertEqual(path.read_bytes(), A_BYTES)

    def test_ancillary_chunks_and_padding_only_change_byte_identity(self):
        payload = pcm_payload(A_FRAMES, 16)
        examples = [
            wave(payload, 16, 2, before=[chunk(b"JUNK", b"abc", b"\x7F")]),
            wave(payload, 16, 2, after=[chunk(b"JUNK", b"abc", b"\x81")]),
            wave(payload, 16, 2, before=[chunk(b"LIST", b"INFO")],
                 after=[chunk(b"BEXT", b"opaque\x00metadata")]),
            riff([chunk(b"JUNK", b"before-fmt"), chunk(b"fmt ", fmt(16, 2)),
                  chunk(b"data", payload)]),
        ]
        for index, content in enumerate(examples):
            with self.subTest(index=index):
                path = self.write(content, f"ancillary-{index}.wav")
                report = inspect_audio(path)
                self.assertEqual(report["decoded_sha256"], A_DECODED_SHA)
                self.assertEqual(report["sha256"], hashlib.sha256(content).hexdigest())
                self.assertNotEqual(report["sha256"], A_FILE_SHA)
                self.assertEqual(report["channels"], inspect_audio(self.write(A_BYTES, "minimal.wav"))["channels"])

    def test_zero_extension_fmt_and_optional_fact_before_or_after_data(self):
        frames = A_FRAMES
        for floating, width in ((False, 16), (True, 32), (True, 64)):
            for fact_position in ("absent", "before", "after"):
                with self.subTest(floating=floating, width=width, fact=fact_position):
                    payload = float_payload(frames, width) if floating else pcm_payload(frames, width)
                    fact = chunk(b"fact", struct.pack("<I", len(frames)))
                    content = wave(payload, width, 2, floating=floating, extended=True,
                                   before=[fact] if fact_position == "before" else [],
                                   after=[fact] if fact_position == "after" else [])
                    report = inspect_audio(self.write(content))
                    self.assertEqual(report["decoded_sha256"], A_DECODED_SHA)
                    self.assertEqual(report["chunk_count"], 2 if fact_position == "absent" else 3)

    def test_nonstandard_filename_does_not_override_observed_format(self):
        for filename in ("capture.txt", "capture.flac", "no-extension", "Åudio-音.wav"):
            with self.subTest(filename=filename):
                report = inspect_audio(self.write(A_BYTES, filename))
                self.assertEqual(report["format"], "wav_pcm16")
                self.assertEqual(report["decoded_sha256"], A_DECODED_SHA)

    def test_relocation_preserves_content_identities_only_path_changes(self):
        left, right = self.write(A_BYTES, "left.wav"), self.write(A_BYTES, "right.wav")
        a, b = inspect_audio(left), inspect_audio(right)
        self.assertNotEqual(a["input_path"], b["input_path"])
        a.pop("input_path")
        b.pop("input_path")
        self.assertEqual(a, b)

    def test_wav_geometry_assertions_are_exact_assertions(self):
        path = self.write(A_BYTES)
        self.assertEqual(inspect_audio(path, sample_rate_hz=48000, channel_count=2), inspect_audio(path))
        self.assert_error("declaration_mismatch", inspect_audio, path, sample_rate_hz=44100)
        self.assert_error("declaration_mismatch", inspect_audio, path, channel_count=1)
        self.assertEqual(path.read_bytes(), A_BYTES)

    def test_raw_selector_and_both_geometry_values_are_required(self):
        path = self.write(C_BYTES, "raw.f32")
        self.assert_error("unsupported_format", inspect_audio, path)
        for options in ({}, {"sample_rate_hz": 48000}, {"channel_count": 1}):
            with self.subTest(options=options):
                self.assert_error("invalid_argument", inspect_audio, path, raw_format="raw_float32_le", **options)
        self.assert_error("invalid_argument", inspect_audio, path, raw_format="wav_float32", sample_rate_hz=48000, channel_count=1)

    def test_raw_geometry_is_a_declaration_not_inferred_hardware_fact(self):
        path = self.write(C_BYTES, "raw.f32")
        options = {"raw_format": "raw_float32_le", "sample_rate_hz": 44100, "channel_count": 2}
        result = read_audio_window(path, 0, 4, **options)
        frames = list(zip(C_VALUES[::2], C_VALUES[1::2]))
        self.assertEqual(result["samples"], [C_VALUES[::2], C_VALUES[1::2]])
        self.assert_report(result["inspection"], path, frames, format_name="raw_float32_le", bits=32, rate=44100)
        self.assertNotEqual(result["inspection"]["decoded_sha256"], C_DECODED_SHA)

    def test_explicit_raw_selector_does_not_guess_riff_signature(self):
        value = struct.unpack("<f", b"RIFF")[0]
        self.assertTrue(math.isfinite(value) and abs(value) <= 1e6)
        path = self.write(b"RIFF", "signature.wav")
        result = read_audio_window(path, 0, 1, raw_format="raw_float32_le", sample_rate_hz=48000, channel_count=1)
        self.assertEqual(result["samples"], [[value]])
        self.assertEqual(result["inspection"]["format"], "raw_float32_le")

    def test_nonfinite_float32_before_inside_after_window_rejects_entire_call(self):
        for encoded in ("0000c07f", "0000807f", "000080ff"):
            for bad_frame in (0, 2, 4):
                with self.subTest(encoded=encoded, bad_frame=bad_frame):
                    data = bytearray(struct.pack("<5f", 0.0, 0.25, 0.5, 0.25, 0.0))
                    data[4 * bad_frame:4 * bad_frame + 4] = bytes.fromhex(encoded)
                    path = self.write(wave(bytes(data), 32, floating=True))
                    error = self.assert_error("nonfinite_sample", read_audio_window, path, 1, 3)
                    self.assertEqual(error.details["frame_index"], bad_frame)
                    self.assertEqual(error.details["channel_index"], 0)

    def test_nonfinite_float64_and_raw_also_fail_complete_stream(self):
        for value in (math.nan, math.inf, -math.inf):
            with self.subTest(value=value):
                path64 = self.write(wave(struct.pack("<3d", 0.25, 0.5, value), 64, floating=True))
                self.assert_error("nonfinite_sample", read_audio_window, path64, 0, 1)
                raw = self.write(struct.pack("<3f", value, 0.25, 0.5), "bad.f32")
                self.assert_error("nonfinite_sample", read_audio_window, raw, 1, 1,
                                  raw_format="raw_float32_le", sample_rate_hz=48000, channel_count=1)

    def test_first_bad_scalar_is_reported_in_frame_major_order(self):
        frames = [(0.0, 0.0), (math.inf, math.nan), (math.nan, 0.0)]
        path = self.write(wave(float_payload(frames, 32), 32, 2, floating=True))
        error = self.assert_error("nonfinite_sample", inspect_audio, path)
        self.assertEqual(error.details["frame_index"], 1)
        self.assertEqual(error.details["channel_index"], 0)
        self.assertEqual(error.details["byte_offset"], 44 + 8)

    def test_inclusive_magnitude_limit_and_adjacent_values(self):
        for width in (32, 64):
            with self.subTest(width=width):
                path = self.write(wave(float_payload([(1e6,), (-1e6,)], width), width, floating=True))
                report = inspect_audio(path)
                self.assertEqual(report["channels"][0]["peak"], 1e6)
                self.assertEqual(report["channels"][0]["rms"], 1e6)
                self.assertEqual(report["channels"][0]["dc"], 0.0)
                self.assertEqual(report["clipping"]["over_full_scale_channel_samples"], 2)
                excessive = 1000000.0625 if width == 32 else math.nextafter(1e6, math.inf)
                for sign in (-1, 1):
                    path = self.write(wave(float_payload([(0.0,), (sign * excessive,)], width), width, floating=True))
                    self.assert_error("sample_out_of_range", read_audio_window, path, 0, 1)

    def test_integer_argument_types_and_window_geometry_are_not_coerced(self):
        path = self.write(A_BYTES)
        for value in (True, False, 1.0, "1"):
            with self.subTest(value=value):
                self.assert_error("invalid_argument", read_audio_window, path, value, 1)
                self.assert_error("invalid_argument", read_audio_window, path, 0, value)
                self.assert_error("invalid_argument", inspect_audio, path, sample_rate_hz=value)
                self.assert_error("invalid_argument", inspect_audio, path, channel_count=value)
        for start, count in ((-1, 1), (0, 0), (0, -1), (4, 1), (3, 2)):
            with self.subTest(start=start, count=count):
                self.assert_error("window_out_of_range", read_audio_window, path, start, count)

    def test_medium_pcm24_stream_preserves_frame_and_channel_order(self):
        # 90,000 data bytes cross the decoder's 65,536-byte I/O boundary.
        frames = [((i % 17 - 8) / 16, (i % 31 - 15) / 32, (i % 13 - 6) / 8)
                  for i in range(10000)]
        content = wave(pcm_payload(frames, 24), 24, 3)
        path = self.write(content)
        result = read_audio_window(path, 7278, 8)
        self.assertEqual(result["samples"], [list(v) for v in zip(*frames[7278:7286])])
        self.assertEqual(result["inspection"]["sha256"], hashlib.sha256(content).hexdigest())
        self.assertEqual(result["inspection"]["decoded_sha256"], decoded_oracle(frames))
        for index, channel in enumerate(result["inspection"]["channels"]):
            self.assert_channel(channel, [frame[index] for frame in frames], index=index, pcm_width=24)

    def test_cli_success_is_exact_canonical_json_from_foreign_cwd(self):
        path = self.write(A_BYTES, "Åudio-音.wav")
        first = self.run_cli("--input", path)
        second = self.run_cli("--input", path)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stderr, b"")
        self.assertEqual(first.stdout, second.stdout)
        report = json.loads(first.stdout)
        self.assertEqual(report, inspect_audio(path))
        expected = (json.dumps(report, sort_keys=True, separators=(",", ":"),
                               ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")
        self.assertEqual(first.stdout, expected)
        self.assertTrue(first.stdout.isascii())
        self.assertEqual(path.read_bytes(), A_BYTES)

    def test_cli_raw_and_window_match_public_api(self):
        path = self.write(C_BYTES, "stream.f32")
        result = self.run_cli("--input", path, "--raw-format", "raw_float32_le",
                              "--sample-rate-hz", 48000, "--channel-count", 1,
                              "--start-frame", 2, "--frame-count", 4)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, b"")
        self.assertEqual(json.loads(result.stdout), read_audio_window(path, 2, 4,
                         raw_format="raw_float32_le", sample_rate_hz=48000, channel_count=1))

    def test_cli_errors_have_stable_envelope_and_empty_stdout(self):
        path = self.write(A_BYTES)
        cases = [(("--input", path, "--start-frame", "1"), 2, "invalid_argument"),
                 (("--input", path, "--frame-count", "1e1", "--start-frame", "0"), 2, "invalid_argument"),
                 (("--input", path, "--sample-rate-hz", "44100"), 1, "declaration_mismatch"),
                 (("--input", self.directory / "absent.wav"), 1, "path_not_found")]
        for arguments, status, code in cases:
            with self.subTest(arguments=arguments):
                result = self.run_cli(*arguments)
                self.assertEqual(result.returncode, status)
                self.assertEqual(result.stdout, b"")
                error = json.loads(result.stderr)
                self.assertEqual(set(error), {"error", "inspector_version", "status"})
                self.assertEqual(error["status"], "rejected")
                self.assertEqual(error["inspector_version"], "capture-audio-v1")
                self.assertEqual(set(error["error"]), {"code", "details", "message"})
                self.assertEqual(error["error"]["code"], code)
                self.assertEqual(result.stderr, (json.dumps(error, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8"))

    def test_main_returns_status_and_help_without_system_exit(self):
        path = self.write(A_BYTES)
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = main(["--input", str(path)])
        self.assertEqual(status, 0)
        self.assertEqual(stderr.getvalue(), "")
        self.assertEqual(json.loads(stdout.getvalue())["decoded_sha256"], A_DECODED_SHA)
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = main(["--help"])
        self.assertEqual(status, 0)
        self.assertIn("--input", stdout.getvalue())
        self.assertEqual(stderr.getvalue(), "")

    def test_public_resource_constants_match_frozen_contract(self):
        expected = {"MAX_FILE_BYTES": 268435456, "MAX_SAMPLE_RATE": 768000,
                    "MAX_CHANNELS": 16, "MAX_SECONDS": 3600, "MAX_CHUNKS": 4096,
                    "MAX_DECODED_SAMPLES": 134217728, "CHUNK_BYTES": 65536,
                    "MAX_WINDOW_FRAMES": 262144, "MAX_WINDOW_SAMPLES": 1048576,
                    "MAX_WINDOW_SECONDS": 600, "MAX_SAMPLE_MAGNITUDE": 1000000.0}
        for name, value in expected.items():
            with self.subTest(name=name):
                self.assertEqual(getattr(capture_audio, name), value)
                self.assertIs(type(getattr(capture_audio, name)), type(value))


if __name__ == "__main__":
    unittest.main()
