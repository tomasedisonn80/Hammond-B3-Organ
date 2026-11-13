#!/usr/bin/env python3
"""Independent malformed/resource/filesystem acceptance for capture-audio-v1.

Tiny encoded fixtures and expected failure positions follow the frozen contract.
OS/stream hooks inject observable failures; no producer parser supplies an oracle.
Large boundary probes explicitly distinguish admission from complete decoding.
"""

from __future__ import annotations

from contextlib import contextmanager, redirect_stderr, redirect_stdout
import errno
import hashlib
import io
import json
import math
import os
from pathlib import Path
import socket
import stat
import struct
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import capture_audio as audio

# These independently authored fixture encoders are not production helpers.
from test_capture_audio import chunk, fmt, riff, wave

REAL_FDOPEN = os.fdopen
REAL_FSTAT = os.fstat
REAL_LSTAT = Path.lstat
REAL_SHA256 = hashlib.sha256
TOOL = ROOT / "tools" / "capture_audio.py"


def pcm(values=(0, 8192, -16384, 0), *, channels=1, rate=48000):
    return wave(struct.pack("<" + "h" * len(values), *values), 16, channels, rate)


def changed_info(info, **changes):
    fields = {name: getattr(info, name) for name in dir(info) if name.startswith("st_")}
    fields.update(changes)
    return SimpleNamespace(**fields)


class StreamProbe:
    """A real owned FileIO with bounded-read observations and explicit faults."""

    def __init__(self, raw, *, cap=None, on_read=None, read_error=None,
                 seek_error=None, close_error=None, early_eof=False):
        self.raw = raw
        self.descriptor = raw.fileno()
        self.cap = cap
        self.on_read = on_read
        self.read_error = read_error
        self.seek_error = seek_error
        self.close_error = close_error
        self.early_eof = early_eof
        self.reads = []
        self.returned_bytes = 0
        self.seeks = []
        self.close_calls = 0

    def fileno(self):
        return self.raw.fileno()

    def read(self, count=-1):
        self.reads.append(count)
        if count < 0 or count > 65536:
            raise AssertionError(f"unbounded read request: {count}")
        if self.read_error is not None:
            raise self.read_error
        if self.early_eof:
            return b""
        payload = self.raw.read(min(count, self.cap) if self.cap is not None else count)
        self.returned_bytes += len(payload)
        if self.on_read is not None:
            self.on_read(self, count, payload)
        return payload

    def seek(self, offset, whence=0):
        self.seeks.append((offset, whence))
        if self.seek_error is not None:
            raise self.seek_error
        return self.raw.seek(offset, whence)

    def close(self):
        self.close_calls += 1
        self.raw.close()
        if self.close_error is not None:
            raise self.close_error


class AdmissionCase(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="capture-audio-admission-")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)

    def write(self, payload, name="capture.wav"):
        path = self.directory / name
        path.write_bytes(payload)
        return path

    def reject(self, code, function, *args, **kwargs):
        with self.assertRaises(audio.AudioError) as caught:
            function(*args, **kwargs)
        error = caught.exception
        self.assertEqual(error.code, code)
        self.assertIs(type(error.message), str)
        self.assertTrue(error.message.strip())
        self.assertIs(type(error.details), dict)
        json.dumps(error.details, allow_nan=False)
        self.assertIn(code, str(error))
        return error

    def reject_bytes(self, payload, code="malformed_audio", **kwargs):
        return self.reject(code, audio.inspect_audio, self.write(payload), **kwargs)

    @contextmanager
    def probe(self, **options):
        probes = []

        def factory(descriptor, *args, **kwargs):
            item = StreamProbe(REAL_FDOPEN(descriptor, *args, **kwargs), **options)
            probes.append(item)
            return item

        try:
            with mock.patch.object(audio.os, "fdopen", side_effect=factory):
                yield probes
        finally:
            for item in probes:
                closed = item.raw.closed
                if not closed:
                    item.raw.close()
                self.assertTrue(closed, "owned descriptor was not closed")
                self.assertEqual(item.close_calls, 1)
                with self.assertRaises(OSError) as caught:
                    REAL_FSTAT(item.descriptor)
                self.assertEqual(caught.exception.errno, errno.EBADF)

    def symlink(self, target, link, *, directory=False):
        try:
            link.symlink_to(target, target_is_directory=directory)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"native symlink creation unavailable: {error}")

    def hardlink(self, target, link):
        try:
            os.link(target, link)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"native hardlink creation unavailable: {error}")

    def cli_error(self, args, expected_status, code):
        result = subprocess.run([sys.executable, "-B", str(TOOL), *args],
                                capture_output=True, timeout=15, cwd=self.directory)
        self.assertEqual(result.returncode, expected_status, result.stderr)
        self.assertEqual(result.stdout, b"")
        payload = json.loads(result.stderr)
        self.assertEqual(set(payload), {"error", "inspector_version", "status"})
        self.assertEqual(payload["status"], "rejected")
        self.assertEqual(payload["inspector_version"], "capture-audio-v1")
        self.assertEqual(set(payload["error"]), {"code", "message", "details"})
        self.assertEqual(payload["error"]["code"], code)
        expected = (json.dumps(payload, sort_keys=True, separators=(",", ":"),
                               ensure_ascii=True, allow_nan=False) + "\n").encode()
        self.assertEqual(result.stderr, expected)
        return payload


class RiffAdmission(AdmissionCase):
    def test_empty_and_recognized_truncated_riff_headers(self):
        self.reject_bytes(b"")
        for length in range(4, 12):
            with self.subTest(length=length):
                self.reject_bytes((b"RIFF" + b"\0" * 4 + b"WAVE")[:length])

    def test_unrecognized_and_explicitly_unsupported_containers(self):
        for payload in (b"RI", b"not audio", b"fLaC" + b"\0" * 20,
                        b"RIFX" + b"\0" * 4 + b"WAVE",
                        b"RF64" + b"\0" * 4 + b"WAVE",
                        b"BW64" + b"\0" * 4 + b"WAVE",
                        b"riff" + b"\0" * 36,
                        b"RIFF" + struct.pack("<I", 4) + b"AVI "):
            with self.subTest(payload=payload[:12]):
                self.reject_bytes(payload, "unsupported_format")

    def test_riff_size_requires_exact_complete_file(self):
        good = pcm()
        for declared in (0, len(good) - 9, len(good) - 7, 0xFFFFFFFF):
            with self.subTest(declared=declared):
                bad = good[:4] + struct.pack("<I", declared) + good[8:]
                error = self.reject_bytes(bad)
                self.assertEqual(error.details["byte_offset"], 4)
        self.reject_bytes(good + b"trailer")
        self.reject_bytes(good[:-1])

    def test_chunk_payload_boundary_padding_and_final_partial_header(self):
        prefix = chunk(b"fmt ", fmt(16)) + chunk(b"data", b"\0\0")
        for tail in (b"x", b"JUNK\0\0\0", b"JUNK" + struct.pack("<I", 0xFFFFFFFF),
                     b"JUNK" + struct.pack("<I", 3) + b"ab",
                     b"JUNK" + struct.pack("<I", 1) + b"x"):
            with self.subTest(tail=tail):
                self.reject_bytes(riff([prefix, tail]))
        # Three-byte PCM data is a complete frame, but its outer pad is absent.
        self.reject_bytes(riff([chunk(b"fmt ", fmt(24)), b"data\x03\0\0\0\0\0\0"]))

    def test_missing_duplicate_and_disordered_format_data_chunks(self):
        form, data = chunk(b"fmt ", fmt(16)), chunk(b"data", b"\0\0")
        for parts in ([], [form], [data], [data, form], [form, form, data],
                      [form, data, form], [form, data, data]):
            with self.subTest(parts=parts):
                self.reject_bytes(riff(parts))

    def test_empty_and_partial_frame_data(self):
        for bits, channels, payload in ((16, 1, b""), (16, 1, b"x"),
                                       (24, 2, b"\0" * 3), (32, 3, b"\0" * 8)):
            with self.subTest(bits=bits, channels=channels):
                self.reject_bytes(wave(payload, bits, channels))

    def test_supported_format_payload_sizes_and_zero_extension(self):
        base = fmt(16)
        for payload in (b"", b"\x01", base[:14], base + b"\0",
                        base + b"\x01\0", base + b"\0\0\0\0"):
            with self.subTest(size=len(payload)):
                self.reject_bytes(riff([chunk(b"fmt ", payload), chunk(b"data", b"\0\0")]))
        report = audio.inspect_audio(self.write(wave(b"\0\0", 16, extended=True)))
        self.assertEqual(report["frame_count"], 1)

    def test_unsupported_tags_keep_priority_over_extension_layout(self):
        for tag in (2, 6, 7, 0xFFFE, 0xFFFF):
            for size in (2, 16, 18, 40):
                with self.subTest(tag=tag, size=size):
                    payload = struct.pack("<H", tag) + b"\0" * (size - 2)
                    error = self.reject_bytes(riff([chunk(b"fmt ", payload),
                                                   chunk(b"data", b"\0\0")]),
                                              "unsupported_format")
                    self.assertEqual(error.details["byte_offset"], 20)
                    self.assertEqual(error.details["format_tag"], tag)

    def test_unsupported_storage_width_with_consistent_earlier_fields(self):
        for tag, bits in ((1, 8), (1, 64), (3, 16), (3, 24)):
            with self.subTest(tag=tag, bits=bits):
                alignment = bits // 8
                form = struct.pack("<HHIIHH", tag, 1, 48000, 48000 * alignment,
                                   alignment, bits)
                error = self.reject_bytes(riff([chunk(b"fmt ", form),
                                               chunk(b"data", b"\0" * alignment)]),
                                          "unsupported_format")
                self.assertEqual(error.details["byte_offset"], 34)

    def test_byte_rate_and_block_alignment_contradictions(self):
        cases = ((struct.pack("<HHIIHH", 1, 1, 48000, 0, 2, 16), 28),
                 (struct.pack("<HHIIHH", 1, 2, 48000, 96000, 2, 16), 32))
        for form, offset in cases:
            with self.subTest(offset=offset):
                error = self.reject_bytes(riff([chunk(b"fmt ", form),
                                               chunk(b"data", b"\0" * 4)]))
                self.assertEqual(error.details["byte_offset"], offset)

    def test_earlier_malformed_fields_precede_unsupported_width(self):
        # Regression: original producer reported unsupported bits at byte 34,
        # despite contradictory byte_rate at byte 28 under frozen section 10.
        cases = ((struct.pack("<HHIIHH", 1, 1, 48000, 0, 1, 8), 28),
                 (struct.pack("<HHIIHH", 1, 1, 48000, 0, 0, 8), 32))
        for form, offset in cases:
            with self.subTest(offset=offset):
                error = self.reject_bytes(riff([chunk(b"fmt ", form), chunk(b"data", b"\0")]))
                self.assertEqual(error.details["byte_offset"], offset)

    def test_fact_requires_format_exact_size_one_occurrence_and_frame_agreement(self):
        form, data = chunk(b"fmt ", fmt(16)), chunk(b"data", b"\0\0")
        good_fact = chunk(b"fact", struct.pack("<I", 1))
        cases = ([good_fact, form, data], [form, good_fact, good_fact, data],
                 [form, data, good_fact, good_fact],
                 [form, chunk(b"fact", b"\0" * 3), data],
                 [form, data, chunk(b"fact", b"\0" * 8)],
                 [form, chunk(b"fact", struct.pack("<I", 2)), data],
                 [form, data, chunk(b"fact", struct.pack("<I", 0))])
        for parts in cases:
            with self.subTest(parts=parts):
                self.reject_bytes(riff(parts))

    def test_alternate_audio_sequences_and_incomplete_list_reject(self):
        for ancillary, code in ((chunk(b"slnt", b"\0" * 4), "unsupported_format"),
                                (chunk(b"LIST", b"wavl"), "unsupported_format"),
                                (chunk(b"LIST", b""), "malformed_audio"),
                                (chunk(b"LIST", b"abc"), "malformed_audio")):
            for before in (True, False):
                with self.subTest(ancillary=ancillary[:8], before=before):
                    self.reject_bytes(wave(b"\0\0", 16,
                                           before=(ancillary,) if before else (),
                                           after=() if before else (ancillary,)), code)

    def test_entire_chunk_sequence_admitted_before_window_or_sample_content(self):
        nan = struct.pack("<f", math.nan)
        bad = wave(nan, 32, floating=True, after=(b"x",))
        path = self.write(bad)
        self.reject("malformed_audio", audio.read_audio_window, path, 0, 1)
        self.reject("malformed_audio", audio.read_audio_window, path, 999, 1)

    def test_raw_zero_and_incomplete_interleaved_frames(self):
        for payload, channels in ((b"", 1), (b"\0", 1), (b"\0" * 4, 2),
                                  (b"\0" * 11, 3)):
            with self.subTest(length=len(payload), channels=channels):
                self.reject_bytes(payload, raw_format="raw_float32_le",
                                  sample_rate_hz=48000, channel_count=channels)

    def test_argument_file_header_assertion_window_and_content_phase_order(self):
        missing = self.directory / "missing.wav"
        self.reject("invalid_argument", audio.inspect_audio, missing, channel_count=True)
        self.reject("path_not_found", audio.inspect_audio, missing, channel_count=17)
        invalid = self.write(b"not wave")
        self.reject("unsupported_format", audio.inspect_audio, invalid, sample_rate_hz=44100)
        bad = self.write(wave(struct.pack("<f", math.nan), 32, floating=True))
        self.reject("declaration_mismatch", audio.read_audio_window, bad, 999, 1,
                    sample_rate_hz=44100)
        self.reject("window_out_of_range", audio.read_audio_window, bad, 999, 1)
        self.reject("nonfinite_sample", audio.read_audio_window, bad, 0, 1)


class ResourceAdmission(AdmissionCase):
    def test_rate_and_channel_adjacent_limits_reject_before_samples(self):
        for channels, rate in ((0, 48000), (17, 48000), (1, 0), (1, 768001)):
            with self.subTest(channels=channels, rate=rate):
                alignment = channels * 2
                form = struct.pack("<HHIIHH", 1, channels, rate, rate * alignment,
                                   alignment, 16)
                self.reject_bytes(riff([chunk(b"fmt ", form), chunk(b"data", b"\0\0")]),
                                  "resource_limit")
        path = self.write(pcm())
        for field, values in (("channel_count", (-1, 0, 17)),
                              ("sample_rate_hz", (-1, 0, 768001))):
            for value in values:
                with self.subTest(field=field, value=value):
                    self.reject("resource_limit", audio.inspect_audio, path, **{field: value})

    def test_actual_duration_boundary_at_one_hertz(self):
        path = self.write(wave(b"\0\0" * 3600, 16, rate=1))
        self.assertEqual(audio.inspect_audio(path)["frame_count"], 3600)
        self.reject_bytes(wave(b"\0\0" * 3601, 16, rate=1), "resource_limit")

    def test_actual_4096_chunk_boundary_and_one_more(self):
        empty = chunk(b"JUNK", b"")
        path = self.write(wave(b"\0\0", 16, before=(empty,) * 4094))
        self.assertEqual(audio.inspect_audio(path)["chunk_count"], 4096)
        self.reject_bytes(wave(b"\0\0", 16, before=(empty,) * 4095), "resource_limit")

    def test_actual_sparse_oversize_rejects_before_opening_or_reading(self):
        path = self.directory / "oversized.wav"
        with path.open("wb") as output:
            output.truncate(268435457)
        with mock.patch.object(audio.os, "open", side_effect=AssertionError("oversized file opened")):
            self.reject("resource_limit", audio.inspect_audio, path)

    def test_file_byte_limit_inclusive_admission_without_claiming_full_scan(self):
        path = self.directory / "maximum-unrecognized.wav"
        with path.open("wb") as output:
            output.truncate(268435456)
        with self.probe() as probes:
            self.reject("unsupported_format", audio.inspect_audio, path)
        self.assertEqual(sum(probes[0].reads), 12)
        # Separately exercise inclusive success under an explicitly reduced bound.
        small = self.write(pcm())
        with mock.patch.object(audio, "MAX_FILE_BYTES", len(pcm())):
            self.assertEqual(audio.inspect_audio(small)["size_bytes"], len(pcm()))

    def test_actual_window_duration_600_and_601_seconds(self):
        path = self.write(wave(b"\0\0" * 601, 16, rate=1))
        result = audio.read_audio_window(path, 0, 600)
        self.assertEqual(len(result["samples"][0]), 600)
        self.reject("resource_limit", audio.read_audio_window, path, 0, 601)

    def test_actual_window_frame_limit_and_adjacent_excess(self):
        path = self.write(wave(b"\0\0" * 262145, 16))
        result = audio.read_audio_window(path, 1, 262144)
        self.assertEqual(result["frame_count"], 262144)
        self.assertEqual(len(result["samples"][0]), 262144)
        with mock.patch.object(audio.hashlib, "sha256", side_effect=AssertionError("late window bound")):
            self.reject("resource_limit", audio.read_audio_window, path, 0, 262145)

    def test_actual_window_scalar_limit_and_adjacent_excess(self):
        path = self.write(wave(b"\0\0" * (16 * 65537), 16, channels=16))
        result = audio.read_audio_window(path, 1, 65536)
        self.assertEqual([len(values) for values in result["samples"]], [65536] * 16)
        self.assertEqual(sum(map(len, result["samples"])), 1048576)
        with mock.patch.object(audio.hashlib, "sha256", side_effect=AssertionError("late scalar bound")):
            self.reject("resource_limit", audio.read_audio_window, path, 0, 65537)

    def test_scalar_work_preflight_with_explicit_reduced_bound(self):
        with mock.patch.object(audio, "MAX_DECODED_SAMPLES", 6):
            path = self.write(pcm((0,) * 6, channels=3))
            self.assertEqual(audio.inspect_audio(path)["frame_count"], 2)
            path = self.write(pcm((0,) * 7))
            with mock.patch.object(audio.hashlib, "sha256", side_effect=AssertionError("late work bound")):
                self.reject("resource_limit", audio.inspect_audio, path)

    def test_read_and_digest_updates_are_bounded_and_bind_one_descriptor(self):
        frames = 12000
        data = (b"\0\0\0" + b"\0\0\x20" + b"\0\0\xe0") * frames
        payload = wave(data, 24, channels=3, before=(chunk(b"JUNK", b"x" * 70001),))
        path = self.write(payload)
        original = REAL_SHA256(payload).hexdigest()
        canonical = (b"HAMMOND-CAPTURE-DECODED-V1\0" + struct.pack("<IIQ", 48000, 3, frames)
                     + struct.pack("<3d", 0, 0.25, -0.25) * frames)
        expected = REAL_SHA256(canonical).hexdigest()
        updates = []

        class Digest:
            def __init__(self):
                self.actual = REAL_SHA256()

            def update(self, value):
                updates.append(len(value))
                self.actual.update(value)

            def hexdigest(self):
                return self.actual.hexdigest()

        with self.probe() as probes, mock.patch.object(audio.hashlib, "sha256", side_effect=Digest):
            report = audio.read_audio_window(path, 7280, 3)
        self.assertEqual(len(probes), 1)
        self.assertTrue(probes[0].reads)
        self.assertTrue(all(0 <= count <= 65536 for count in probes[0].reads))
        self.assertLessEqual(probes[0].returned_bytes, 2 * len(payload) + 32 * 3)
        self.assertTrue(updates and max(updates) <= 65536)
        self.assertEqual(report["inspection"]["sha256"], original)
        self.assertEqual(report["inspection"]["decoded_sha256"], expected)
        self.assertEqual(report["samples"], [[0.0] * 3, [0.25] * 3, [-0.25] * 3])

    def test_legitimate_short_reads_preserve_all_bytes(self):
        payload = pcm(tuple(range(-100, 100)))
        path = self.write(payload)
        with self.probe(cap=3) as probes:
            report = audio.inspect_audio(path)
        self.assertEqual(report["sha256"], REAL_SHA256(payload).hexdigest())
        self.assertEqual(report["frame_count"], 200)
        self.assertGreater(len(probes[0].reads), 100)


class FilesystemAdmission(AdmissionCase):
    def test_missing_leaf_and_missing_parent_are_typed(self):
        for path in (self.directory / "missing.wav", self.directory / "absent" / "capture.wav"):
            with self.subTest(path=path):
                self.reject("path_not_found", audio.inspect_audio, path)

    def test_directory_leaf_is_rejected_before_open(self):
        with mock.patch.object(audio.os, "open", side_effect=AssertionError("directory opened")):
            self.reject("unsafe_file", audio.inspect_audio, self.directory)

    def test_real_fifo_is_rejected_without_blocking(self):
        if not hasattr(os, "mkfifo"):
            self.skipTest("native FIFO creation is unavailable")
        path = self.directory / "capture.fifo"
        try:
            os.mkfifo(path)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"native FIFO creation unavailable: {error}")
        with mock.patch.object(audio.os, "open", side_effect=AssertionError("FIFO opened")):
            self.reject("unsafe_file", audio.inspect_audio, path)

    def test_real_unix_socket_is_rejected_before_open(self):
        if not hasattr(socket, "AF_UNIX"):
            self.skipTest("native Unix-domain socket is unavailable")
        path = self.directory / "capture.sock"
        try:
            server = socket.socket(socket.AF_UNIX)
            self.addCleanup(server.close)
            server.bind(str(path))
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"native Unix-domain socket creation/bind unavailable: {error}")
        with mock.patch.object(audio.os, "open", side_effect=AssertionError("socket opened")):
            self.reject("unsafe_file", audio.inspect_audio, path)

    def test_injected_nonregular_leaf_modes_reject_before_open(self):
        path = self.write(pcm())
        for mode in (stat.S_IFSOCK, stat.S_IFIFO, stat.S_IFCHR, stat.S_IFBLK):
            with self.subTest(mode=mode):
                def nonregular(selected):
                    info = REAL_LSTAT(selected)
                    return changed_info(info, st_mode=mode | 0o600) if selected == path else info

                with mock.patch.object(Path, "lstat", nonregular), \
                     mock.patch.object(audio.os, "open", side_effect=AssertionError("special leaf opened")):
                    self.reject("unsafe_file", audio.inspect_audio, path)

    def test_native_character_device_is_rejected_before_open(self):
        path = Path("/dev/null")
        if not path.exists() or not stat.S_ISCHR(path.stat().st_mode):
            self.skipTest("native /dev/null character-device fixture is unavailable")
        with mock.patch.object(audio.os, "open", side_effect=AssertionError("device opened")):
            self.reject("unsafe_file", audio.inspect_audio, path)

    def test_real_leaf_symlink_and_dangling_link_reject(self):
        real = self.write(pcm())
        for index, target in enumerate((real, self.directory / "absent.wav")):
            link = self.directory / f"alias-{index}.wav"
            self.symlink(target, link)
            with mock.patch.object(audio.os, "open", side_effect=AssertionError("leaf link opened")):
                self.reject("unsafe_file", audio.inspect_audio, link)

    def test_direct_parent_alias_is_allowed_and_canonicalized(self):
        real = self.directory / "real"
        real.mkdir()
        path = real / "capture.wav"
        path.write_bytes(pcm())
        alias = self.directory / "alias"
        self.symlink(real, alias, directory=True)
        report = audio.inspect_audio(alias / path.name)
        self.assertEqual(report["input_path"], str(path.resolve()))
        self.assertEqual(report["sha256"], REAL_SHA256(pcm()).hexdigest())

    def test_regular_hardlink_is_permitted_without_independence_claim(self):
        path = self.write(pcm())
        link = self.directory / "second.wav"
        self.hardlink(path, link)
        report = audio.inspect_audio(link)
        self.assertEqual(report["sha256"], REAL_SHA256(pcm()).hexdigest())
        self.assertEqual(report["authenticity"], "not_established")

    def test_native_windows_reparse_fixture(self):
        if os.name != "nt":
            self.skipTest("real Windows reparse admission requires a native Windows runner")
        path = self.write(pcm())
        link = self.directory / "native-reparse.wav"
        self.symlink(path, link)
        info = link.lstat()
        self.assertTrue(info.st_file_attributes & 0x400)
        self.reject("unsafe_file", audio.inspect_audio, link)

    def test_injected_reparse_flags_on_path_and_descriptor_reject(self):
        path = self.write(pcm())

        def path_reparse(selected):
            info = REAL_LSTAT(selected)
            return changed_info(info, st_file_attributes=0x400) if selected == path else info

        with mock.patch.object(Path, "lstat", path_reparse):
            self.reject("unsafe_file", audio.inspect_audio, path)
        with self.probe(), mock.patch.object(audio.os, "fstat", side_effect=lambda fd:
                                             changed_info(REAL_FSTAT(fd), st_file_attributes=0x400)):
            self.reject("unsafe_file", audio.inspect_audio, path)

    def test_no_usable_path_or_descriptor_identity_rejects_and_closes(self):
        path = self.write(pcm())

        def no_path_id(selected):
            return changed_info(REAL_LSTAT(selected), st_dev=0, st_ino=0)

        with self.probe(), mock.patch.object(Path, "lstat", no_path_id), \
             mock.patch.object(audio.os, "fstat", side_effect=lambda fd:
                               changed_info(REAL_FSTAT(fd), st_dev=0, st_ino=0)):
            self.reject("identity_unavailable", audio.inspect_audio, path)

    def test_single_api_identity_fallback_and_zero_device_are_admitted(self):
        path = self.write(pcm())
        for path_zero, fd_zero, zero_device in ((True, False, False), (False, True, False),
                                               (False, False, True)):
            with self.subTest(path_zero=path_zero, fd_zero=fd_zero, zero_device=zero_device):
                def path_info(selected):
                    info = REAL_LSTAT(selected)
                    return changed_info(info, st_dev=0 if zero_device or path_zero else info.st_dev,
                                        st_ino=0 if path_zero else info.st_ino)

                def fd_info(fd):
                    info = REAL_FSTAT(fd)
                    return changed_info(info, st_dev=0 if zero_device or fd_zero else info.st_dev,
                                        st_ino=0 if fd_zero else info.st_ino)

                with mock.patch.object(Path, "lstat", path_info), mock.patch.object(audio.os, "fstat", side_effect=fd_info):
                    self.assertEqual(audio.inspect_audio(path)["sha256"], REAL_SHA256(pcm()).hexdigest())

    def test_path_and_fd_timestamp_differences_are_not_cross_compared(self):
        path = self.write(pcm())

        def distinct_times(fd):
            info = REAL_FSTAT(fd)
            return changed_info(info, st_mtime_ns=info.st_mtime_ns + 1000000000,
                                st_ctime_ns=info.st_ctime_ns + 2000000000)

        with mock.patch.object(audio.os, "fstat", side_effect=distinct_times):
            self.assertEqual(audio.inspect_audio(path)["frame_count"], 4)

    def test_path_descriptor_identity_and_size_disagreement_reject(self):
        path = self.write(pcm())
        for field in ("st_ino", "st_size"):
            with self.subTest(field=field):
                def disagree(fd):
                    info = REAL_FSTAT(fd)
                    return changed_info(info, **{field: getattr(info, field) + 1})

                with self.probe(), mock.patch.object(audio.os, "fstat", side_effect=disagree):
                    self.reject("file_changed", audio.inspect_audio, path)

    def test_opened_descriptor_must_still_be_regular(self):
        path = self.write(pcm())
        with self.probe(), mock.patch.object(audio.os, "fstat", side_effect=lambda fd:
                changed_info(REAL_FSTAT(fd), st_mode=stat.S_IFIFO | 0o600)):
            self.reject("unsafe_file", audio.inspect_audio, path)

    def test_fdopen_error_and_cancellation_close_transferred_descriptor(self):
        path = self.write(pcm())
        for failure in (OSError("injected fdopen failure"), KeyboardInterrupt()):
            with self.subTest(failure=type(failure).__name__):
                descriptors = []

                def reject_fdopen(fd, *args, **kwargs):
                    descriptors.append(fd)
                    raise failure

                with mock.patch.object(audio.os, "fdopen", side_effect=reject_fdopen):
                    if isinstance(failure, KeyboardInterrupt):
                        with self.assertRaises(KeyboardInterrupt):
                            audio.inspect_audio(path)
                    else:
                        self.reject("io_error", audio.inspect_audio, path)
                self.assertEqual(len(descriptors), 1)
                with self.assertRaises(OSError) as caught:
                    REAL_FSTAT(descriptors[0])
                self.assertEqual(caught.exception.errno, errno.EBADF)

    def test_open_initial_fstat_read_seek_and_close_errors_are_typed(self):
        path = self.write(pcm())
        with mock.patch.object(audio.os, "open", side_effect=PermissionError("injected denied open")):
            self.reject("io_error", audio.inspect_audio, path)
        with self.probe(), mock.patch.object(audio.os, "fstat", side_effect=OSError("injected initial stat failure")):
            self.reject("io_error", audio.inspect_audio, path)
        for option in ("read_error", "seek_error", "close_error"):
            with self.subTest(option=option), self.probe(**{option: OSError("injected " + option)}):
                self.reject("io_error", audio.inspect_audio, path)

    def test_short_unannounced_eof_is_malformed_and_closes(self):
        path = self.write(pcm())
        with self.probe(early_eof=True):
            self.reject("malformed_audio", audio.inspect_audio, path)

    def test_streaming_cancellation_propagates_and_closes(self):
        path = self.write(pcm())
        with self.probe(read_error=KeyboardInterrupt()):
            with self.assertRaises(KeyboardInterrupt):
                audio.inspect_audio(path)

    def test_path_resolution_and_initial_metadata_io_errors_are_typed(self):
        with mock.patch.object(audio.os, "getcwd", side_effect=OSError("injected unavailable cwd")):
            self.reject("io_error", audio.inspect_audio, "capture.wav")
        path = self.write(pcm())
        with mock.patch.object(Path, "lstat", side_effect=PermissionError("injected denied metadata")):
            self.reject("io_error", audio.inspect_audio, path)
        with mock.patch.object(Path, "resolve", side_effect=OSError("injected resolve failure")):
            self.reject("io_error", audio.inspect_audio, path)

    def test_recheck_io_failure_is_typed_without_overwriting_primary_failure(self):
        path = self.write(pcm())
        for payload, expected in ((pcm(), "io_error"), (b"not wave", "unsupported_format")):
            with self.subTest(expected=expected):
                path.write_bytes(payload)
                calls = 0

                def stat_then_fail(fd):
                    nonlocal calls
                    calls += 1
                    if calls >= 2:
                        raise PermissionError("injected final stat failure")
                    return REAL_FSTAT(fd)

                with self.probe(), mock.patch.object(audio.os, "fstat", side_effect=stat_then_fail):
                    self.reject(expected, audio.inspect_audio, path)

    def test_primary_decode_error_survives_close_error(self):
        path = self.write(wave(struct.pack("<f", math.nan), 32, floating=True))
        with self.probe(close_error=OSError("injected close failure after real close")):
            self.reject("nonfinite_sample", audio.inspect_audio, path)

    def test_observed_descriptor_changes_reject_each_same_api_stamp_field(self):
        path = self.write(pcm())
        fields = ("st_ino", "st_dev", "st_size", "st_mtime_ns", "st_ctime_ns", "st_mode")
        for field in fields:
            with self.subTest(field=field):
                calls = 0

                def mutate_fd(fd):
                    nonlocal calls
                    calls += 1
                    info = REAL_FSTAT(fd)
                    if calls < 2:
                        return info
                    changed = (stat.S_IFIFO | 0o600) if field == "st_mode" else getattr(info, field) + 1
                    return changed_info(info, **{field: changed})

                with self.probe(), mock.patch.object(audio.os, "fstat", side_effect=mutate_fd):
                    self.reject("file_changed", audio.inspect_audio, path)

    def test_canonical_parent_identity_is_rechecked_without_timestamp_false_positive(self):
        path = self.write(pcm())
        for identity_change in (False, True):
            with self.subTest(identity_change=identity_change):
                read_started = False

                def read_hook(*unused):
                    nonlocal read_started
                    read_started = True

                def parent_info(selected):
                    info = REAL_LSTAT(selected)
                    if selected == path.parent and read_started:
                        fields = {"st_ino": info.st_ino + 1} if identity_change else {
                            "st_mtime_ns": info.st_mtime_ns + 1,
                            "st_ctime_ns": info.st_ctime_ns + 1, "st_size": info.st_size + 1}
                        return changed_info(info, **fields)
                    return info

                with self.probe(on_read=read_hook), mock.patch.object(Path, "lstat", parent_info):
                    if identity_change:
                        self.reject("file_changed", audio.inspect_audio, path)
                    else:
                        self.assertEqual(audio.inspect_audio(path)["frame_count"], 4)

    def test_real_timestamp_change_overrides_content_error(self):
        for payload in (pcm(), wave(struct.pack("<f", math.nan), 32, floating=True)):
            with self.subTest(nonfinite=payload != pcm()):
                path = self.write(payload)
                before = path.stat()
                changed = False

                def touch(*unused):
                    nonlocal changed
                    if not changed:
                        os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns + 5000000000))
                        changed = True

                with self.probe(on_read=touch):
                    self.reject("file_changed", audio.inspect_audio, path)
                self.assertEqual(path.read_bytes(), payload)

    def test_real_same_size_replacement_is_detected(self):
        if os.name == "nt":
            self.skipTest("open-file replacement fixture uses POSIX rename semantics")
        path = self.write(pcm())
        replacement = self.write(pcm((1, 2, 3, 4)), "replacement.wav")
        replaced = False

        def replace(*unused):
            nonlocal replaced
            if not replaced:
                os.replace(replacement, path)
                replaced = True

        with self.probe(on_read=replace):
            self.reject("file_changed", audio.inspect_audio, path)

    def test_real_source_removal_is_detected_and_descriptor_closed(self):
        if os.name == "nt":
            self.skipTest("open-file unlink fixture uses POSIX unlink semantics")
        path = self.write(pcm())
        removed = False

        def remove(*unused):
            nonlocal removed
            if not removed:
                path.unlink()
                removed = True

        with self.probe(on_read=remove):
            self.reject("file_changed", audio.inspect_audio, path)

    def test_retargeted_parent_alias_rejects_even_with_same_child_inode(self):
        first, second = self.directory / "first", self.directory / "second"
        first.mkdir()
        second.mkdir()
        path = first / "capture.wav"
        path.write_bytes(pcm())
        self.hardlink(path, second / path.name)
        alias = self.directory / "parent-alias"
        self.symlink(first, alias, directory=True)
        changed = False

        def retarget(*unused):
            nonlocal changed
            if not changed:
                alias.unlink()
                alias.symlink_to(second, target_is_directory=True)
                changed = True

        with self.probe(on_read=retarget):
            self.reject("file_changed", audio.inspect_audio, alias / path.name)

    def test_requested_leaf_snapshot_is_independent_of_canonical_snapshot(self):
        real = self.directory / "real"
        real.mkdir()
        path = real / "capture.wav"
        path.write_bytes(pcm())
        alias = self.directory / "alias"
        self.symlink(real, alias, directory=True)
        requested = alias / path.name
        read_started = False

        def read_hook(*unused):
            nonlocal read_started
            read_started = True

        def requested_info(selected):
            info = REAL_LSTAT(selected)
            return changed_info(info, st_mtime_ns=info.st_mtime_ns + 1) if selected == requested and read_started else info

        with self.probe(on_read=read_hook), mock.patch.object(Path, "lstat", requested_info):
            self.reject("file_changed", audio.inspect_audio, requested)


class CommandLineAdmission(AdmissionCase):
    def test_integer_cli_grammar_rejects_non_ascii_signs_whitespace_and_long_tokens(self):
        path = self.write(pcm())
        for token in ("-1", "+1", " 1", "1 ", "1.0", "1e1", "1_0", "١", "１２", "", "9" * 21):
            with self.subTest(token=token):
                self.cli_error(["--input", str(path), "--start-frame", token, "--frame-count", "1"],
                               2, "invalid_argument")
        self.cli_error(["--input", str(path), "--start-frame", "9" * 20, "--frame-count", "1"],
                       1, "window_out_of_range")

    def test_unknown_abbreviated_output_and_unpaired_options_create_no_file(self):
        path = self.write(pcm())
        target = self.directory / "must-not-exist.json"
        for extra in (["--out", str(target)], ["--output", str(target)], ["--inp", str(path)],
                      ["--start-frame", "0"], ["--frame-count", "1"],
                      ["--raw-format", "wav_pcm16"]):
            with self.subTest(extra=extra):
                self.cli_error(["--input", str(path), *extra], 2, "invalid_argument")
        self.assertFalse(target.exists())

    def test_cli_admission_errors_are_complete_finite_json_without_stdout(self):
        cases = ((b"not wave", "unsupported_format"), (pcm()[:-1], "malformed_audio"),
                 (wave(struct.pack("<f", math.nan), 32, floating=True), "nonfinite_sample"),
                 (wave(struct.pack("<d", 1000001.0), 64, floating=True), "sample_out_of_range"))
        for payload, code in cases:
            with self.subTest(code=code):
                path = self.write(payload)
                self.cli_error(["--input", str(path)], 1, code)
                self.assertEqual(path.read_bytes(), payload)
        self.cli_error(["--input", str(self.directory / "missing.wav")], 1, "path_not_found")

    def test_main_wrong_argv_types_and_invalid_paths_return_usage_error(self):
        class Token(str):
            pass

        for argv in ((), "--help", [None], [True], [Token("--help")],
                     ["--input", "bad\0name"], ["--input", "bad\ud800name"]):
            with self.subTest(argv=repr(argv)), redirect_stdout(io.StringIO()) as out, \
                 redirect_stderr(io.StringIO()) as error:
                self.assertEqual(audio.main(argv), 2)
                self.assertEqual(out.getvalue(), "")
                self.assertEqual(json.loads(error.getvalue())["error"]["code"], "invalid_argument")

    def test_api_bad_path_objects_and_invalid_raw_selectors_fail_before_io(self):
        for path in (None, b"capture.wav", 1, True, "", "bad\0name", "bad\ud800name", io.BytesIO()):
            with self.subTest(path=repr(path)), mock.patch.object(audio.os, "open", side_effect=AssertionError("invalid path opened")):
                self.reject("invalid_argument", audio.inspect_audio, path)
        path = self.write(pcm())
        for selector in (False, 1, "wav_pcm16", "raw_float64_le", []):
            with self.subTest(selector=repr(selector)):
                self.reject("invalid_argument", audio.inspect_audio, path, raw_format=selector)


if __name__ == "__main__":
    unittest.main()
