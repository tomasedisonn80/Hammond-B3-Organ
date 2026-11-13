#!/usr/bin/env python3
"""Bounded, read-only digital-audio inspection under capture-audio-v1.

Every successful inspection hashes the complete original file and a canonical
frame-major sample stream. A window retains only its requested samples; it does
not reduce complete-file admission. No physical provenance is inferred.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import stat
import struct
import sys


MAX_FILE_BYTES = 268435456
MAX_SAMPLE_RATE = 768000
MAX_CHANNELS = 16
MAX_SECONDS = 3600
MAX_CHUNKS = 4096
MAX_DECODED_SAMPLES = 134217728
CHUNK_BYTES = 65536
MAX_WINDOW_FRAMES = 262144
MAX_WINDOW_SAMPLES = 1048576
MAX_WINDOW_SECONDS = 600
MAX_SAMPLE_MAGNITUDE = 1000000.0

INSPECTOR_VERSION = "capture-audio-v1"
DECODED_DIGEST_VERSION = "hammond-capture-decoded-v1"
_DECODED_PREFIX = b"HAMMOND-CAPTURE-DECODED-V1\x00"
_REPARSE_POINT = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)


class AudioError(ValueError):
    """An expected argument, admission, content or filesystem rejection."""

    def __init__(self, code: str, message: str, details: dict | None = None):
        self.code = code
        self.message = message
        self.details = {} if details is None else details
        super().__init__(f"{code}: {message}")


def _fail(code, message, **details):
    raise AudioError(code, message, details)


def _is_reparse(info):
    return bool(getattr(info, "st_file_attributes", 0) & _REPARSE_POINT)


def _identity(info):
    """A nonzero inode supplies identity; its device scope may validly be zero."""
    device = getattr(info, "st_dev", 0)
    inode = getattr(info, "st_ino", 0)
    if inode:
        return device, inode
    return None


def _file_stamp(info):
    # Compare timestamps only within the same API (lstat or fstat).
    return (stat.S_IFMT(info.st_mode), _is_reparse(info),
            getattr(info, "st_dev", 0), getattr(info, "st_ino", 0),
            info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def _parent_stamp(info):
    # Sibling creation can change directory times/size without changing this file.
    return stat.S_IFMT(info.st_mode), _is_reparse(info), _identity(info)


def _require_regular(info):
    if not stat.S_ISREG(info.st_mode) or _is_reparse(info):
        _fail("unsafe_file", "Input must be a regular nonsymlink, non-reparse file")


def _same_identity(left, right):
    left_id, right_id = _identity(left), _identity(right)
    if left_id is not None and right_id is not None and left_id != right_id:
        _fail("file_changed", "Input pathname and descriptor identities disagree")


class _Source:
    """One descriptor and independent before/after filesystem observations."""

    def __init__(self, path):
        self.requested = Path(path).absolute()
        self.path = None
        self.parent = None
        self.requested_before = None
        self.path_before = None
        self.parent_before = None
        self.fd_before = None
        self.stream = None

    def open(self):
        try:
            requested = self.requested.lstat()
        except FileNotFoundError as exc:
            raise AudioError("path_not_found", "Input file or parent does not exist") from exc
        _require_regular(requested)
        self.requested_before = requested
        if requested.st_size > MAX_FILE_BYTES:
            _fail("resource_limit", "Input exceeds the file byte limit")

        self.parent = self.requested.parent.resolve(strict=True)
        self.parent_before = self.parent.lstat()
        if not stat.S_ISDIR(self.parent_before.st_mode) or _is_reparse(self.parent_before):
            _fail("file_changed", "Canonical input parent was replaced")
        self.path = self.parent / self.requested.name
        self.path_before = self.path.lstat()
        _require_regular(self.path_before)
        _same_identity(requested, self.path_before)
        if requested.st_size != self.path_before.st_size:
            _fail("file_changed", "Input size changed during path admission")

        flags = (os.O_RDONLY | getattr(os, "O_BINARY", 0)
                 | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
        descriptor = os.open(self.path, flags)
        try:
            self.stream = os.fdopen(descriptor, "rb", buffering=0)
        except BaseException:
            os.close(descriptor)
            raise
        self.fd_before = os.fstat(self.stream.fileno())
        _require_regular(self.fd_before)
        if self.fd_before.st_size != requested.st_size:
            _fail("file_changed", "Opened input size differs from the admitted size")
        if self.fd_before.st_size > MAX_FILE_BYTES:
            _fail("resource_limit", "Opened input exceeds the file byte limit")
        _same_identity(requested, self.fd_before)
        _same_identity(self.path_before, self.fd_before)
        if not any(_identity(info) for info in
                   (requested, self.path_before, self.fd_before)):
            _fail("identity_unavailable", "Neither pathname nor descriptor provides a usable file identity")

    def verify(self):
        """Observe all available snapshots, giving actual mutation precedence."""
        checks = []
        if self.requested_before is not None:
            checks.append((self.requested.lstat, self.requested_before, _file_stamp))
        if self.path_before is not None:
            checks.append((self.path.lstat, self.path_before, _file_stamp))
        if self.parent_before is not None:
            checks.append((self.parent.lstat, self.parent_before, _parent_stamp))
        if self.fd_before is not None and self.stream is not None:
            checks.append((lambda: os.fstat(self.stream.fileno()), self.fd_before, _file_stamp))
        io_error = None
        changed = False
        for observe, before, stamp in checks:
            try:
                if stamp(observe()) != stamp(before):
                    changed = True
            except (FileNotFoundError, NotADirectoryError):
                changed = True
            except OSError as exc:
                io_error = io_error or exc
        if self.parent is not None:
            try:
                if self.requested.parent.resolve(strict=True) != self.parent:
                    changed = True
            except (FileNotFoundError, NotADirectoryError, RuntimeError):
                changed = True
            except OSError as exc:
                io_error = io_error or exc
        if changed:
            _fail("file_changed", "Input or its parent identity changed during inspection")
        if io_error is not None:
            raise AudioError("io_error", f"Cannot recheck input identity: {io_error}") from io_error

    def close(self):
        if self.stream is not None:
            self.stream.close()


def _arguments(path, raw_format, sample_rate_hz, channel_count, window):
    if not isinstance(path, (str, Path)) or not str(path):
        _fail("invalid_argument", "Input path must be a nonempty string or pathlib.Path")
    try:
        str(path).encode("utf-8")
    except UnicodeError as exc:
        raise AudioError("invalid_argument", "Input path contains an unpaired surrogate") from exc
    if "\x00" in str(path):
        _fail("invalid_argument", "Input path contains a NUL character")
    if raw_format is not None and (type(raw_format) is not str or raw_format != "raw_float32_le"):
        _fail("invalid_argument", "raw_format must be None or raw_float32_le")
    for name, value in (("sample_rate_hz", sample_rate_hz), ("channel_count", channel_count)):
        if value is not None and type(value) is not int:
            _fail("invalid_argument", "Audio geometry arguments must be exact integers", field=name)
    if raw_format is not None and (sample_rate_hz is None or channel_count is None):
        _fail("invalid_argument", "Raw float32 requires explicit sample rate and channel count")
    if window is not None:
        for name, value in zip(("start_frame", "frame_count"), window):
            if type(value) is not int:
                _fail("invalid_argument", "Window arguments must be exact integers", field=name)


def _rate_channels(rate, channels):
    if not 1 <= channels <= MAX_CHANNELS:
        _fail("resource_limit", "Channel count is outside the admitted range", field="channel_count")
    if not 1 <= rate <= MAX_SAMPLE_RATE:
        _fail("resource_limit", "Sample rate is outside the admitted range", field="sample_rate_hz")


def _read_exact(stream, count, offset):
    """Read one bounded region, tolerating legitimate short regular-file reads."""
    if not 0 <= count <= CHUNK_BYTES:
        raise AssertionError("internal read exceeds CHUNK_BYTES")
    payload = stream.read(count)
    if len(payload) == count:
        return payload
    pieces = bytearray(payload)
    while len(pieces) < count:
        part = stream.read(count - len(pieces))
        if not part:
            _fail("malformed_audio", "Input ended before its announced boundary", byte_offset=offset + len(pieces))
        pieces.extend(part)
    return bytes(pieces)


def _geometry(format_name, container, bits, rate, channels, offset, size, chunks):
    _rate_channels(rate, channels)
    block_align = channels * (bits // 8)
    if size == 0 or size % block_align:
        _fail("malformed_audio", "Audio data must contain nonempty complete frames", byte_offset=offset)
    frames = size // block_align
    if frames > rate * MAX_SECONDS:
        _fail("resource_limit", "Audio duration exceeds the admitted limit")
    if frames * channels > MAX_DECODED_SAMPLES:
        _fail("resource_limit", "Audio exceeds the decoded scalar-sample limit")
    return {"format": format_name, "container": container, "bits_per_sample": bits,
            "sample_rate_hz": rate, "channel_count": channels, "frame_count": frames,
            "data_offset_bytes": offset, "data_size_bytes": size, "chunk_count": chunks}


def _scan_wave(stream, size):
    if size == 0:
        _fail("malformed_audio", "Audio file is empty")
    header = _read_exact(stream, min(12, size), 0)
    if header[:4] != b"RIFF":
        _fail("unsupported_format", "Input is not a supported RIFF/WAVE file")
    if len(header) != 12:
        _fail("malformed_audio", "RIFF header is truncated", byte_offset=len(header))
    if header[8:] != b"WAVE":
        _fail("unsupported_format", "RIFF form is not WAVE")
    if struct.unpack_from("<I", header, 4)[0] + 8 != size:
        _fail("malformed_audio", "RIFF size does not equal the complete file size", byte_offset=4)

    position, chunks = 12, 0
    format_info = None
    geometry = None
    fact_frames = None
    while position < size:
        if size - position < 8:
            _fail("malformed_audio", "Final chunk header is partial", byte_offset=position)
        chunks += 1
        if chunks > MAX_CHUNKS:
            _fail("resource_limit", "RIFF chunk count exceeds the admitted limit", byte_offset=position)
        stream.seek(position)
        name, count = struct.unpack("<4sI", _read_exact(stream, 8, position))
        start = position + 8
        end = start + count + (count & 1)
        if end > size or end <= position:
            _fail("malformed_audio", "Chunk payload or required padding exceeds RIFF boundary", byte_offset=position + 4)
        if name == b"fmt ":
            if format_info is not None:
                _fail("malformed_audio", "Duplicate fmt chunk", byte_offset=position)
            if count < 2:
                _fail("malformed_audio", "Format tag is truncated", byte_offset=start)
            tag_bytes = _read_exact(stream, 2, start)
            tag = struct.unpack("<H", tag_bytes)[0]
            if tag not in (1, 3):
                _fail("unsupported_format", "WAV format tag is not supported", byte_offset=start, format_tag=tag)
            if count not in (16, 18):
                _fail("malformed_audio", "Supported fmt payload must be 16 or 18 bytes", byte_offset=position + 4)
            fmt = tag_bytes + _read_exact(stream, count - 2, start + 2)
            _, channels, rate, byte_rate, block_align, bits = struct.unpack_from("<HHIIHH", fmt)
            _rate_channels(rate, channels)
            if byte_rate != rate * block_align:
                _fail("malformed_audio", "WAV byte rate contradicts rate and block alignment", byte_offset=start + 8)
            if block_align != channels * (bits // 8):
                _fail("malformed_audio", "WAV block alignment contradicts channel count and width", byte_offset=start + 12)
            if (tag == 1 and bits not in (16, 24, 32)) or (tag == 3 and bits not in (32, 64)):
                _fail("unsupported_format", "WAV sample storage width is not supported", byte_offset=start + 14, bits_per_sample=bits)
            if count == 18 and struct.unpack_from("<H", fmt, 16)[0] != 0:
                _fail("malformed_audio", "WAV format extension must have cbSize zero", byte_offset=start + 16)
            format_info = (f"wav_{'pcm' if tag == 1 else 'float'}{bits}", bits, rate, channels)
        elif name == b"data":
            if format_info is None:
                _fail("malformed_audio", "Data chunk precedes fmt chunk", byte_offset=position)
            if geometry is not None:
                _fail("malformed_audio", "Duplicate data chunk", byte_offset=position)
            format_name, bits, rate, channels = format_info
            geometry = _geometry(format_name, "RIFF/WAVE", bits, rate, channels, start, count, chunks)
        elif name == b"fact":
            if format_info is None or fact_frames is not None:
                _fail("malformed_audio", "Fact chunk must follow fmt and occur at most once", byte_offset=position)
            if count != 4:
                _fail("malformed_audio", "Fact payload must contain exactly one frame count", byte_offset=position + 4)
            fact_frames = struct.unpack("<I", _read_exact(stream, 4, start))[0]
        elif name == b"slnt":
            _fail("unsupported_format", "Top-level slnt audio sequences are not supported", byte_offset=position)
        elif name == b"LIST":
            if count < 4:
                _fail("malformed_audio", "LIST payload is missing its four-byte list type", byte_offset=position + 4)
            if _read_exact(stream, 4, start) == b"wavl":
                _fail("unsupported_format", "LIST/wavl audio sequences are not supported", byte_offset=start)
        position = end
    if format_info is None or geometry is None:
        _fail("malformed_audio", "RIFF/WAVE requires one fmt chunk and one nonempty data chunk")
    if fact_frames is not None and fact_frames != geometry["frame_count"]:
        _fail("malformed_audio", "Fact frame count contradicts data geometry")
    geometry["chunk_count"] = chunks
    return geometry


def _window_bounds(window, geometry):
    if window is None:
        return
    start, count = window
    if start < 0 or count <= 0 or start + count > geometry["frame_count"]:
        _fail("window_out_of_range", "Requested window is outside the admitted frame geometry")
    if (count > MAX_WINDOW_FRAMES or count * geometry["channel_count"] > MAX_WINDOW_SAMPLES
            or count > geometry["sample_rate_hz"] * MAX_WINDOW_SECONDS):
        _fail("resource_limit", "Requested window exceeds an admitted window limit")


class _Compensated:
    """Constant-storage Neumaier summation, also rescalable for RMS."""

    def __init__(self):
        self.total = 0.0
        self.correction = 0.0

    def add(self, value):
        total = self.total + value
        if abs(self.total) >= abs(value):
            self.correction += (self.total - total) + value
        else:
            self.correction += (value - total) + self.total
        self.total = total

    def scale(self, factor):
        self.total *= factor
        self.correction *= factor

    def value(self):
        return self.total + self.correction


def _finite_zero(value):
    if not math.isfinite(value):
        _fail("sample_out_of_range", "Computed audio statistic is not finite")
    return 0.0 if value == 0.0 else value


class _ChannelStats:
    def __init__(self, pcm_denominator):
        self.denominator = pcm_denominator
        self.peak = 0.0
        self.nonzero = 0
        self.positive_full = self.negative_full = 0
        self.positive_over = self.negative_over = 0
        self.integer_sum = self.integer_squared_sum = 0
        self.float_sum = _Compensated()
        self.scaled_squares = _Compensated()
        self.scale = 0.0

    def add(self, value, code):
        magnitude = abs(value)
        self.peak = max(self.peak, magnitude)
        self.nonzero += value != 0.0
        if self.denominator:
            self.integer_sum += code
            self.integer_squared_sum += code * code
            self.positive_full += code == self.denominator - 1
            self.negative_full += code == -self.denominator
        else:
            self.float_sum.add(value)
            if magnitude:
                if magnitude > self.scale:
                    ratio = self.scale / magnitude
                    self.scaled_squares.scale(ratio * ratio)
                    self.scale = magnitude
                    self.scaled_squares.add(1.0)
                else:
                    ratio = magnitude / self.scale
                    self.scaled_squares.add(ratio * ratio)
            self.positive_full += value == 1.0
            self.negative_full += value == -1.0
            self.positive_over += value > 1.0
            self.negative_over += value < -1.0

    def report(self, index, count):
        if self.denominator:
            dc = self.integer_sum / (count * self.denominator)
            rms = math.sqrt(self.integer_squared_sum / count) / self.denominator
        else:
            dc = self.float_sum.value() / count
            rms = self.scale * math.sqrt(self.scaled_squares.value() / count)
        return {"channel_index": index, "sample_count": count,
                "peak": _finite_zero(self.peak), "rms": _finite_zero(rms), "dc": _finite_zero(dc),
                "nonzero_sample_count": self.nonzero,
                "positive_full_scale_sample_count": self.positive_full,
                "negative_full_scale_sample_count": self.negative_full,
                "full_scale_sample_count": self.positive_full + self.negative_full,
                "positive_over_full_scale_sample_count": self.positive_over,
                "negative_over_full_scale_sample_count": self.negative_over,
                "over_full_scale_sample_count": self.positive_over + self.negative_over}


def _scalars(payload, bits, pcm):
    if pcm and bits == 24:
        for offset in range(0, len(payload), 3):
            code = payload[offset] | (payload[offset + 1] << 8) | (payload[offset + 2] << 16)
            yield code - 0x1000000 if code & 0x800000 else code
    else:
        code = {16: "h", 32: "i"}[bits] if pcm else {32: "f", 64: "d"}[bits]
        for (value,) in struct.iter_unpack("<" + code, payload):
            yield value


def _content_pass(source, geometry, window):
    """Hash every original byte once; decode the contiguous data region in place."""
    stream = source.stream
    size = source.fd_before.st_size
    channels = geometry["channel_count"]
    bits = geometry["bits_per_sample"]
    width = bits // 8
    pcm = geometry["format"].startswith("wav_pcm")
    denominator = 1 << (bits - 1) if pcm else 0
    stats = [_ChannelStats(denominator) for _ in range(channels)]
    samples = [[] for _ in range(channels)] if window is not None else None
    first_scalar = window[0] * channels if window is not None else 0
    last_scalar = (window[0] + window[1]) * channels if window is not None else 0
    byte_digest = hashlib.sha256()
    decoded_digest = hashlib.sha256()
    decoded_digest.update(_DECODED_PREFIX)
    decoded_digest.update(struct.pack("<IIQ", geometry["sample_rate_hz"], channels, geometry["frame_count"]))
    digest_buffer = bytearray(CHUNK_BYTES)
    digest_view = memoryview(digest_buffer)
    digest_used = 0
    position = 0
    stream.seek(0)

    def hash_until(end):
        nonlocal position
        while position < end:
            count = min(CHUNK_BYTES, end - position)
            byte_digest.update(_read_exact(stream, count, position))
            position += count

    hash_until(geometry["data_offset_bytes"])
    data_end = position + geometry["data_size_bytes"]
    block_align = channels * width
    read_size = (CHUNK_BYTES // block_align) * block_align
    scalar_index = 0
    while position < data_end:
        count = min(read_size, data_end - position)
        payload = _read_exact(stream, count, position)
        byte_digest.update(payload)
        for code in _scalars(payload, bits, pcm):
            channel = scalar_index % channels
            value = code / denominator if pcm else code
            if not pcm:
                if not math.isfinite(value):
                    _fail("nonfinite_sample", "Audio contains a nonfinite sample",
                          frame_index=scalar_index // channels, channel_index=channel,
                          byte_offset=geometry["data_offset_bytes"] + scalar_index * width)
                if abs(value) > MAX_SAMPLE_MAGNITUDE:
                    _fail("sample_out_of_range", "Audio sample exceeds the magnitude limit",
                          frame_index=scalar_index // channels, channel_index=channel,
                          byte_offset=geometry["data_offset_bytes"] + scalar_index * width)
            value = 0.0 if value == 0.0 else value
            stats[channel].add(value, code)
            struct.pack_into("<d", digest_buffer, digest_used, value)
            digest_used += 8
            if digest_used == CHUNK_BYTES:
                decoded_digest.update(digest_view)
                digest_used = 0
            if samples is not None and first_scalar <= scalar_index < last_scalar:
                samples[channel].append(value)
            scalar_index += 1
        position += count
    if digest_used:
        decoded_digest.update(digest_view[:digest_used])
    hash_until(size)
    reports = [item.report(index, geometry["frame_count"]) for index, item in enumerate(stats)]
    return byte_digest.hexdigest(), decoded_digest.hexdigest(), reports, samples


def _inspect_source(source, raw_format, sample_rate_hz, channel_count, window):
    for name, value, limit in (("sample_rate_hz", sample_rate_hz, MAX_SAMPLE_RATE),
                               ("channel_count", channel_count, MAX_CHANNELS)):
        if value is not None and not 1 <= value <= limit:
            _fail("resource_limit", "Declared audio geometry is outside the admitted range", field=name)
    if raw_format is not None:
        geometry = _geometry(raw_format, "raw", 32, sample_rate_hz, channel_count,
                             0, source.fd_before.st_size, 0)
    else:
        geometry = _scan_wave(source.stream, source.fd_before.st_size)
        for name, assertion in (("sample_rate_hz", sample_rate_hz), ("channel_count", channel_count)):
            if assertion is not None and assertion != geometry[name]:
                _fail("declaration_mismatch", "WAV header differs from the supplied assertion",
                      field=name, expected=assertion, observed=geometry[name])
    _window_bounds(window, geometry)
    byte_hash, decoded_hash, channels, samples = _content_pass(source, geometry, window)
    report = {"schema_version": 1, "inspector_version": INSPECTOR_VERSION, "status": "inspected",
              "input_path": str(source.path), "size_bytes": source.fd_before.st_size, "sha256": byte_hash,
              "decoded_digest_version": DECODED_DIGEST_VERSION, "decoded_sha256": decoded_hash,
              **geometry,
              "duration_seconds": _finite_zero(geometry["frame_count"] / geometry["sample_rate_hz"]),
              "amplitude_unit": "digital_full_scale", "channels": channels,
              "clipping": {
                  "full_scale_channel_samples": sum(item["full_scale_sample_count"] for item in channels),
                  "over_full_scale_channel_samples": sum(item["over_full_scale_sample_count"] for item in channels),
                  "confirmed_pre_encoding_clipping": None,
                  "pre_encoding_status": "not_inferable_from_samples"},
              "evidence_scope": "decoded-digital-audio-only", "authenticity": "not_established",
              "physical_clock": "not_established", "calibration": "not_established",
              "physical_fidelity": "not_established"}
    if window is None:
        return report
    start, count = window
    return {"schema_version": 1, "window_version": "capture-audio-window-v1", "inspection": report,
            "start_frame": start, "frame_count": count, "end_frame": start + count, "samples": samples}


def _run(path, raw_format, sample_rate_hz, channel_count, window):
    _arguments(path, raw_format, sample_rate_hz, channel_count, window)
    try:
        source = _Source(path)
    except (OSError, ValueError, OverflowError) as exc:
        raise AudioError("io_error", f"Cannot resolve requested input path: {exc}") from exc
    error = None
    result = None
    cancelled = False
    try:
        source.open()
        result = _inspect_source(source, raw_format, sample_rate_hz, channel_count, window)
    except AudioError as exc:
        error = exc
    except (OSError, ValueError, OverflowError) as exc:
        error = AudioError("io_error", f"Cannot inspect input: {exc}")
    except BaseException:
        cancelled = True
        raise
    finally:
        try:
            if not cancelled:
                try:
                    source.verify()
                except AudioError as exc:
                    if error is None or exc.code == "file_changed":
                        error = exc
        finally:
            try:
                source.close()
            except OSError as exc:
                if not cancelled and error is None:
                    error = AudioError("io_error", f"Cannot close input: {exc}")
    if error is not None:
        raise error
    return result


def inspect_audio(path: str | Path, *, raw_format: str | None = None,
                  sample_rate_hz: int | None = None, channel_count: int | None = None) -> dict:
    """Inspect a complete admitted WAV or explicitly described raw float32 file."""
    return _run(path, raw_format, sample_rate_hz, channel_count, None)


def read_audio_window(path: str | Path, start_frame: int, frame_count: int, *,
                      raw_format: str | None = None, sample_rate_hz: int | None = None,
                      channel_count: int | None = None) -> dict:
    """Return a bounded channel-planar window plus complete-file inspection."""
    return _run(path, raw_format, sample_rate_hz, channel_count, (start_frame, frame_count))


class _HelpRequested(Exception):
    pass


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        _fail("invalid_argument", message)

    def exit(self, status=0, message=None):
        if status == 0:
            raise _HelpRequested()
        _fail("invalid_argument", message or "Invalid command line")


def _integer_token(token):
    if not 1 <= len(token) <= 20 or not token.isascii() or not token.isdecimal():
        raise argparse.ArgumentTypeError("expected 1..20 ASCII decimal digits without a sign")
    return int(token)


def _json_line(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = _Parser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--input", required=True, help="regular WAV or explicitly described raw audio file")
    parser.add_argument("--raw-format", choices=("raw_float32_le",))
    parser.add_argument("--sample-rate-hz", type=_integer_token)
    parser.add_argument("--channel-count", type=_integer_token)
    parser.add_argument("--start-frame", type=_integer_token)
    parser.add_argument("--frame-count", type=_integer_token)
    try:
        if argv is not None and (type(argv) is not list or any(type(token) is not str for token in argv)):
            _fail("invalid_argument", "argv must be a list of strings or None")
        args = parser.parse_args(argv)
        if (args.start_frame is None) != (args.frame_count is None):
            _fail("invalid_argument", "--start-frame and --frame-count must appear together")
        options = {"raw_format": args.raw_format, "sample_rate_hz": args.sample_rate_hz,
                   "channel_count": args.channel_count}
        if args.start_frame is None:
            report = inspect_audio(args.input, **options)
        else:
            report = read_audio_window(args.input, args.start_frame, args.frame_count, **options)
        sys.stdout.write(_json_line(report))
        return 0
    except _HelpRequested:
        return 0
    except AudioError as exc:
        sys.stderr.write(_json_line({"error": {"code": exc.code, "message": exc.message, "details": exc.details},
                                     "inspector_version": INSPECTOR_VERSION, "status": "rejected"}))
        return 2 if exc.code == "invalid_argument" else 1


if __name__ == "__main__":
    raise SystemExit(main())
