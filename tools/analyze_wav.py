#!/usr/bin/env python3
"""Independent, bounded, read-only PCM16 statistics for engineering fixtures.

No producer metrics or DSP code are imported. Amplitude is signed PCM / 32768,
not volts or pascals. A crossing-rate estimate is not general pitch recognition.
"""

import argparse
import json
import math
import os
from pathlib import Path
import re
import stat
import struct
import sys


MAX_FILE_BYTES = 256 * 1024 * 1024
MAX_CHUNKS = 1024
MAX_CHANNELS = 8
MAX_SAMPLE_RATE = 192000
MAX_SECONDS = 600
BLOCK_FRAMES = 4096
PCM_DIVISOR = 32768


class AnalysisError(ValueError):
    """Unsupported, malformed, changing, or out-of-range input."""


def _read_exact(stream, size):
    data = stream.read(size)
    if len(data) != size:
        raise AnalysisError("Truncated WAV header or frame data")
    return data


def _header(stream, file_size):
    if not 44 <= file_size <= MAX_FILE_BYTES:
        raise AnalysisError(f"File size must be in 44..{MAX_FILE_BYTES} bytes")
    riff, declared_size, wave = struct.unpack("<4sI4s", _read_exact(stream, 12))
    if riff != b"RIFF" or wave != b"WAVE":
        raise AnalysisError("Only little-endian RIFF/WAVE is supported")
    if declared_size + 8 != file_size:
        raise AnalysisError("RIFF size disagrees with actual file size")
    audio_format = None
    data_region = None
    chunks = 0
    while stream.tell() < file_size:
        chunks += 1
        if chunks > MAX_CHUNKS:
            raise AnalysisError(f"WAV exceeds {MAX_CHUNKS} chunks")
        if file_size - stream.tell() < 8:
            raise AnalysisError("Truncated chunk header")
        kind, size = struct.unpack("<4sI", _read_exact(stream, 8))
        payload = stream.tell()
        padded_end = payload + size + (size & 1)
        if padded_end > file_size:
            raise AnalysisError("Chunk or required padding exceeds the RIFF boundary")
        if kind == b"fmt ":
            if audio_format is not None or size not in (16, 18):
                raise AnalysisError("Require one PCM fmt chunk of 16 or 18 bytes")
            fields = struct.unpack("<HHIIHH", _read_exact(stream, 16))
            encoding, channels, rate, byte_rate, alignment, bits = fields
            if size == 18 and _read_exact(stream, 2) != b"\x00\x00":
                raise AnalysisError("PCM fmt extension must be empty")
            if encoding != 1 or bits != 16:
                raise AnalysisError("Only signed 16-bit integer PCM is supported")
            if not 1 <= channels <= MAX_CHANNELS:
                raise AnalysisError(f"Channel count must be in 1..{MAX_CHANNELS}")
            if not 1 <= rate <= MAX_SAMPLE_RATE:
                raise AnalysisError(f"Sample rate must be in 1..{MAX_SAMPLE_RATE} Hz")
            if alignment != channels * 2 or byte_rate != rate * alignment:
                raise AnalysisError("PCM block alignment or byte rate is inconsistent")
            audio_format = (channels, rate, alignment)
        elif kind == b"data":
            if audio_format is None or data_region is not None:
                raise AnalysisError("Require one data chunk after the fmt chunk")
            channels, rate, alignment = audio_format
            if size == 0 or size % alignment:
                raise AnalysisError("Data must contain nonempty, complete PCM frames")
            frames = size // alignment
            if frames > rate * MAX_SECONDS:
                raise AnalysisError(f"Audio duration exceeds {MAX_SECONDS} seconds")
            data_region = (payload, frames)
        # Unknown ancillary chunks are bounded and skipped, never allocated.
        stream.seek(padded_end)
    if audio_format is None or data_region is None:
        raise AnalysisError("WAV requires both fmt and data chunks")
    return (*audio_format, *data_region)


class _Crossings:
    """Constant-space rising crossings; no crossing uses samples outside a window."""

    def __init__(self):
        self.previous = None
        self.zero_start = None
        self.zero_count = 0
        self.plateaus = 0
        self.count = 0
        self.first = None
        self.last = None
        self.minimum_period = None
        self.maximum_period = None

    def add(self, value, frame):
        crossing = None
        if value == 0:
            if self.previous is not None and self.previous < 0:
                self.zero_start = frame
                self.zero_count = 1
            elif self.zero_start is not None:
                self.zero_count += 1
        elif value > 0:
            if self.previous is not None and self.previous < 0:
                crossing = frame - 1 - self.previous / (value - self.previous)
            elif self.zero_start is not None:
                crossing = float(self.zero_start)
                self.plateaus += self.zero_count > 1
            self.zero_start = None
        else:
            self.zero_start = None
        self.previous = value
        if crossing is None:
            return
        if self.last is not None:
            period = crossing - self.last
            self.minimum_period = period if self.minimum_period is None else min(
                self.minimum_period, period)
            self.maximum_period = period if self.maximum_period is None else max(
                self.maximum_period, period)
        else:
            self.first = crossing
        self.last = crossing
        self.count += 1

    def report(self, rate, expected, peak, dc):
        estimate = None
        mean_period = None
        spread = None
        flags = []
        if self.count < 3:
            flags.append("fewer_than_three_rising_crossings")
        else:
            mean_period = (self.last - self.first) / (self.count - 1)
            estimate = rate / mean_period
            spread = (self.maximum_period - self.minimum_period) / mean_period
            if spread > 0.01:
                flags.append("period_spread_exceeds_1_percent")
            if abs(estimate - expected) > expected * 0.01:
                flags.append("crossing_rate_differs_from_expected_by_over_1_percent")
        if self.plateaus:
            flags.append("multiple_zero_samples_at_a_rising_crossing")
        if expected > rate / 8:
            flags.append("fewer_than_eight_samples_per_expected_period")
        if peak * PCM_DIVISOR < 32:
            flags.append("peak_below_32_pcm_codes")
        if abs(dc) > peak * 0.1:
            flags.append("absolute_dc_exceeds_10_percent_of_peak")
        return {
            "status": ("insufficient_crossings" if estimate is None else
                       "ambiguous" if flags else "estimated_under_fixture_assumption"),
            "candidate_frequency_hz": estimate,
            "error_hz": None if estimate is None else estimate - expected,
            "error_cents": None if estimate is None else
                1200 * (math.log2(estimate) - math.log2(expected)),
            "rising_crossings": self.count,
            "complete_periods": max(0, self.count - 1),
            "first_crossing_frame": self.first,
            "last_crossing_frame": self.last,
            "mean_period_frames": mean_period,
            "minimum_period_frames": self.minimum_period,
            "maximum_period_frames": self.maximum_period,
            "period_spread_fraction": spread,
            "zero_plateau_crossings": self.plateaus,
            "ambiguity_flags": flags,
        }


def _frame_number(value, name):
    if type(value) is not int or not 0 <= value <= MAX_SAMPLE_RATE * MAX_SECONDS:
        raise AnalysisError(f"{name} must be a bounded nonnegative integer")
    return value


def analyze_wav(path, *, start_frame=0, end_frame=None, expected_frequency=None):
    """Return a JSON-compatible report; raise AnalysisError/OSError on rejection.

    Frame intervals are [start_frame, end_frame). expected_frequency declares a
    steady monophonic fixture; it does not establish that the input is one.
    """
    start_frame = _frame_number(start_frame, "start_frame")
    if end_frame is not None:
        end_frame = _frame_number(end_frame, "end_frame")
    if expected_frequency is not None:
        if type(expected_frequency) not in (int, float):
            raise AnalysisError("Expected frequency must be a finite positive number")
        try:
            expected_frequency = float(expected_frequency)
        except OverflowError as error:
            raise AnalysisError("Expected frequency is out of range") from error
        if not math.isfinite(expected_frequency) or expected_frequency <= 0:
            raise AnalysisError("Expected frequency must be finite and positive")
    path = Path(path)
    # O_NONBLOCK avoids waiting on a FIFO before its descriptor can be rejected.
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NONBLOCK", 0)
    with os.fdopen(os.open(path, flags), "rb") as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode):
            raise AnalysisError("Input must be a regular file")
        channels, rate, alignment, offset, total_frames = _header(stream, before.st_size)
        end_frame = total_frames if end_frame is None else end_frame
        if not 0 <= start_frame < end_frame <= total_frames:
            raise AnalysisError("Window must satisfy 0 <= start < end <= total frames")
        if expected_frequency is not None and expected_frequency >= rate / 2:
            raise AnalysisError("Expected frequency must be strictly below Nyquist")
        count = end_frame - start_frame
        sums = [0] * channels
        squares = [0] * channels
        peaks = [0] * channels
        nonzero = [0] * channels
        positive_full = [0] * channels
        negative_full = [0] * channels
        crossings = [_Crossings() for _ in range(channels)] if expected_frequency else None
        unequal_frames = 0
        stream.seek(offset + start_frame * alignment)
        unpacker = struct.Struct("<" + "h" * channels)
        cursor = start_frame
        while cursor < end_frame:
            block_frames = min(BLOCK_FRAMES, end_frame - cursor)
            block = _read_exact(stream, block_frames * alignment)
            for values in unpacker.iter_unpack(block):
                if channels == 2:
                    unequal_frames += values[0] != values[1]
                for channel, value in enumerate(values):
                    sums[channel] += value
                    squares[channel] += value * value
                    peaks[channel] = max(peaks[channel], abs(value))
                    nonzero[channel] += value != 0
                    positive_full[channel] += value == 32767
                    negative_full[channel] += value == -32768
                    if crossings is not None:
                        crossings[channel].add(value, cursor)
                cursor += 1
        after = os.fstat(stream.fileno())
        if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (
                after.st_size, after.st_mtime_ns, after.st_ctime_ns):
            raise AnalysisError("Input changed during analysis")
    measurements = []
    for channel in range(channels):
        peak = peaks[channel] / PCM_DIVISOR
        dc = sums[channel] / count / PCM_DIVISOR
        measurements.append({
            "channel_index": channel,
            "sample_count": count,
            "peak": peak,
            "rms": math.sqrt(squares[channel] / count) / PCM_DIVISOR,
            "dc": dc,
            "nonzero_sample_count": nonzero[channel],
            "full_scale_sample_count": positive_full[channel] + negative_full[channel],
            "positive_full_scale_sample_count": positive_full[channel],
            "negative_full_scale_sample_count": negative_full[channel],
            "frequency_estimate": None if crossings is None else
                crossings[channel].report(rate, expected_frequency, peak, dc),
        })
    return {
        "analyzer_version": "pcm16-engineering-v1",
        "input_path": str(path.resolve()),
        "evidence_scope": "PCM file statistics; no physical calibration or fidelity claim",
        "format": {"container": "RIFF/WAVE", "sample_format": "pcm_s16le",
                   "sample_rate_hz": rate, "channels": channels, "total_frames": total_frames},
        "amplitude": {"unit": "normalized_pcm", "divisor": PCM_DIVISOR,
                      "minimum": -1.0, "maximum": 32767 / PCM_DIVISOR,
                      "calibration": "none; not volts or pascals"},
        "window": {"start_frame": start_frame, "end_frame": end_frame,
                   "frames": count, "duration_seconds": count / rate},
        "channels": measurements,
        "stereo": {"applicable": channels == 2,
                   "identical": unequal_frames == 0 if channels == 2 else None,
                   "differing_frames": unequal_frames if channels == 2 else None},
        "clipping": {
            "full_scale_definition": "PCM code -32768 or 32767",
            "full_scale_channel_samples": sum(positive_full) + sum(negative_full),
            "confirmed_pre_quantization_clipping": None,
            "pre_quantization_status": "not_inferable_from_pcm16",
        },
        "frequency": {
            "expected_frequency_hz": expected_frequency,
            "method": "linearly interpolated rising zero crossings; mean complete period",
            "fixture_assumption": "caller-declared steady monophonic signal" if crossings else None,
            "limits": [
                "Crossing rate is not general pitch recognition or proof of a fundamental.",
                "Harmonics, mixtures, DC, noise, transients and aliasing can mislead this method.",
                "At least three rising crossings wholly inside the window are required.",
                "Zero plateaus use their first zero and are flagged as ambiguous.",
                "Ambiguity thresholds are engineering diagnostics, not calibrated uncertainty.",
                "Frequency uses the WAV header clock; no physical clock calibration is implied.",
            ],
        },
    }


def _unsigned_argument(token):
    if len(token) > 12 or re.fullmatch(r"[0-9]+", token) is None:
        raise argparse.ArgumentTypeError("Require a bounded unsigned decimal integer")
    try:
        return _frame_number(int(token), "frame")
    except AnalysisError as error:
        raise argparse.ArgumentTypeError(str(error)) from error


def _frequency_argument(token):
    if len(token) > 128 or re.fullmatch(
            r"[+]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?", token) is None:
        raise argparse.ArgumentTypeError("Require a finite positive decimal frequency")
    value = float(token)
    if not math.isfinite(value) or value <= 0:
        raise argparse.ArgumentTypeError("Require a finite positive decimal frequency")
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--input", type=Path, required=True, help="Read-only PCM16 WAV input")
    parser.add_argument("--start-frame", type=_unsigned_argument, default=0)
    parser.add_argument("--end-frame", type=_unsigned_argument, help="Exclusive frame bound")
    parser.add_argument("--expected-frequency", type=_frequency_argument,
                        help="Hz; declares a steady monophonic engineering fixture")
    args = parser.parse_args(argv)
    try:
        report = analyze_wav(args.input, start_frame=args.start_frame,
                             end_frame=args.end_frame, expected_frequency=args.expected_frequency)
        serialized = json.dumps(report, allow_nan=False, indent=2, sort_keys=True)
    except (AnalysisError, OSError) as error:
        parser.exit(2, f"analyze_wav: {error}\n")
    print(serialized)
    return 0


if __name__ == "__main__":
    sys.exit(main())
