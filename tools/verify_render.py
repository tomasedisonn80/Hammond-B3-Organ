#!/usr/bin/env python3
"""Independently verify a retained schema-1, schema-2 or schema-3 render bundle.

Public API: verify_bundle(directory_or_manifest) -> JSON-compatible report.
VerificationError/OSError means failure. This consumer never imports the fixture
producer, executes a renderer, or authenticates a build or physical instrument.
Only the supported profile compiler is reused, for its authoring contract.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime
import hashlib
import importlib.util
import io
import json
import math
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import stat
import struct
import sys

MAX_MANIFEST = 256 * 1024
MAX_PROFILE = 256 * 1024
MAX_COMPILED = 128 * 1024
MAX_SCORE = 16 * 1024 * 1024
MAX_LOG = 1024 * 1024
MAX_METRICS = 16 * 1024
MAX_EXECUTABLE = 512 * 1024 * 1024
MAX_TOOL = 1024 * 1024
CHUNK = 64 * 1024
PCM_BOUND = 1 / 32768
TOLERANCE = 1e-12

_spec = importlib.util.spec_from_file_location(
    "hammond_verifier_profile_compiler", Path(__file__).with_name("compile_profile.py"))
assert _spec is not None and _spec.loader is not None
_compiler = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_compiler)


class VerificationError(ValueError):
    """A missing, inconsistent, unsupported, or changed evidence item."""


def _require(condition, message):
    if not condition:
        raise VerificationError(message)


def _object(value, keys, label, optional=()):
    _require(type(value) is dict, f"{label}: expected object")
    _require(set(keys) <= value.keys() <= set(keys) | set(optional),
             f"{label}: missing or unexpected fields")
    return value


def _literal(value, expected, label):
    _require(type(value) is type(expected) and value == expected,
             f"{label}: expected {expected!r}")


def _integer(value, low, high, label):
    _require(type(value) is int and low <= value <= high,
             f"{label}: expected integer in {low}..{high}")
    return value


def _number(value, low, high, label):
    _require(type(value) in (int, float) and math.isfinite(value) and low <= value <= high,
             f"{label}: expected finite number in {low}..{high}")
    return value


def _string(value, label):
    _require(type(value) is str and bool(value) and "\x00" not in value,
             f"{label}: expected nonempty string without NUL")
    return value


def _hash(value, label):
    _require(type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value) is not None,
             f"{label}: expected lowercase SHA-256")


def _absolute(value, label):
    _string(value, label)
    _require(len(value.encode("utf-8")) <= 4096, f"{label}: path exceeds 4096 bytes")
    path = PurePosixPath(value) if value.startswith("/") else PureWindowsPath(value)
    _require(path.is_absolute() and ".." not in path.parts and str(path) == value,
             f"{label}: expected normalized absolute path")
    return path


def _utc(value, label):
    _require(type(value) is str and re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]{1,6})?Z",
        value) is not None, f"{label}: expected ISO 8601 UTC timestamp ending Z")
    try:
        return datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as error:
        raise VerificationError(f"{label}: invalid UTC timestamp") from error


def _json(raw, limit, label):
    """Bound bytes, nesting, nodes and strings; reject duplicate keys and NaN."""
    _require(len(raw) <= limit, f"{label}: JSON exceeds {limit} bytes")

    def pairs(items):
        result = {}
        for key, value in items:
            _require(key not in result, f"{label}: duplicate JSON key {key!r}")
            result[key] = value
        return result

    def integer(token):
        _require(len(token) <= 128, f"{label}: oversized JSON integer")
        return int(token)

    def real(token):
        value = float(token)
        _require(math.isfinite(value), f"{label}: nonfinite JSON number")
        return value

    def constant(token):
        raise VerificationError(f"{label}: forbidden JSON constant {token}")

    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                           parse_int=integer, parse_float=real, parse_constant=constant)
        pending = [(value, 0)]
        count = 0
        while pending:
            item, depth = pending.pop()
            count += 1
            _require(count <= 20000 and depth <= 24, f"{label}: JSON structure exceeds bounds")
            if type(item) is dict:
                _require(len(item) <= 64, f"{label}: object exceeds 64 fields")
                pending.extend((child, depth + 1) for child in item.values())
                pending.extend((key, depth + 1) for key in item)
            elif type(item) is list:
                _require(len(item) <= 1024, f"{label}: array exceeds 1024 items")
                pending.extend((child, depth + 1) for child in item)
            elif type(item) is str:
                _require(len(item) <= 4096, f"{label}: string exceeds 4096 characters")
                item.encode("utf-8")  # Reject escaped unpaired Unicode surrogates.
        return value
    except (UnicodeError, ValueError, RecursionError) as error:
        raise VerificationError(f"{label}: invalid bounded UTF-8 JSON: {error}") from error


def _stamp(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


def _reparse(info):
    # Junctions and other Windows reparse points can redirect directory traversal
    # without appearing as POSIX-style symbolic links in st_mode.
    return bool(getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


class _Reader:
    """Bounded regular-file reads with observed replacement/change detection."""

    def __init__(self):
        self.files = {}
        self.directories = {}

    def directory(self, path):
        for current in (*reversed(path.parents), path):
            info = current.lstat()
            _require(stat.S_ISDIR(info.st_mode) and not _reparse(info),
                     f"directory is not a regular nonsymlink directory: {current}")
            identity = (info.st_dev, info.st_ino)
            _require(current not in self.directories or self.directories[current] == identity,
                     f"directory changed during verification: {current}")
            self.directories[current] = identity

    @contextmanager
    def open(self, path, limit):
        self.directory(path.parent)
        before = path.lstat()
        _require(stat.S_ISREG(before.st_mode) and not _reparse(before),
                 f"expected regular nonsymlink file: {path}")
        _require(0 <= before.st_size <= limit, f"file exceeds {limit} bytes: {path}")
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        flags |= getattr(os, "O_NONBLOCK", 0)
        descriptor = os.open(path, flags)
        with os.fdopen(descriptor, "rb") as stream:
            opened = os.fstat(stream.fileno())
            # Windows path/descriptor metadata can differ by API. Compare each
            # observation with its own later observation, not full cross-API
            # stamps. POSIX additionally exposes comparable device/inode IDs.
            _require(stat.S_ISREG(opened.st_mode) and opened.st_size == before.st_size,
                     f"file type/size changed before reading: {path}")
            if os.name == "posix":
                _require((opened.st_dev, opened.st_ino) == (before.st_dev, before.st_ino),
                         f"file identity changed before reading: {path}")
            yield stream
            _require(_stamp(os.fstat(stream.fileno())) == _stamp(opened),
                     f"file changed while reading: {path}")
        _require(_stamp(path.lstat()) == _stamp(before), f"file changed after reading: {path}")
        self.files[path] = _stamp(before)

    def read(self, path, limit, retain=True):
        digest = hashlib.sha256()
        chunks = [] if retain else None
        count = 0
        with self.open(path, limit) as stream:
            while True:
                chunk = stream.read(min(CHUNK, limit - count + 1))
                if not chunk:
                    break
                count += len(chunk)
                _require(count <= limit, f"file grew past {limit} bytes: {path}")
                digest.update(chunk)
                if chunks is not None:
                    chunks.append(chunk)
        return {"size_bytes": count, "sha256": digest.hexdigest()}, (
            b"".join(chunks) if chunks is not None else None)

    def finish(self):
        for path, identity in self.directories.items():
            info = path.lstat()
            _require(stat.S_ISDIR(info.st_mode) and not _reparse(info) and
                     (info.st_dev, info.st_ino) == identity,
                     f"directory changed during verification: {path}")
        for path, expected in self.files.items():
            _require(_stamp(path.lstat()) == expected, f"file changed during verification: {path}")


def _inventory(directory, expected):
    names = set()
    with os.scandir(directory) as entries:
        for entry in entries:
            _require(entry.name in expected, f"unexpected evidence path: {entry.name}")
            names.add(entry.name)
    _require(names == expected, f"missing evidence paths: {', '.join(sorted(expected - names))}")


def _record(record, filename, limit, label, extra=()):
    _object(record, {"path", "sha256", "size_bytes"} | set(extra), label)
    _literal(record["path"], filename, f"{label}.path")
    _hash(record["sha256"], f"{label}.sha256")
    _integer(record["size_bytes"], 0, limit, f"{label}.size_bytes")


def _matches(record, actual, label):
    for key in ("size_bytes", "sha256"):
        _literal(record[key], actual[key], f"{label}.{key}")


def _events(raw, frames, schema_version, contacts="ideal"):
    """Independent parser of the documented five-field absolute-event grammar."""
    _require(type(contacts) is str and contacts in ("ideal", "nominal"),
             "events: unknown contact model selection")
    _require(len(raw) <= MAX_SCORE and b"\x00" not in raw, "events: oversized file or NUL byte")
    source = io.BytesIO(raw[3:] if raw.startswith(b"\xef\xbb\xbf") else raw)
    count = repeated = 0
    previous = -1
    line_number = 0
    while True:
        line = source.readline(4098)
        if not line:
            break
        line_number += 1
        if line.endswith(b"\n"):
            line = line[:-1]
        label = f"events line {line_number}"
        _require(len(line) <= 4096, f"{label}: exceeds 4096 bytes")
        try:
            text = line.decode("utf-8").strip(" \t\r\n\v\f")
        except UnicodeError as error:
            raise VerificationError(f"{label}: invalid UTF-8") from error
        if not text or text.startswith("#"):
            continue
        tokens = re.split(r"[ \t\r\n\v\f]+", text)
        _require(len(tokens) == 5, f"{label}: expected exactly five fields")
        frame_token, kind, manual, index_token, number_token = tokens
        for token in (frame_token, index_token):
            _require(re.fullmatch(r"[0-9]{1,128}", token) is not None,
                     f"{label}: frame/index must be unsigned decimal integers")
        frame, index = int(frame_token), int(index_token)
        _require(frame <= 2**64 - 1 and index <= 2**64 - 1,
                 f"{label}: frame/index exceeds uint64")
        _require(previous <= frame < frames, f"{label}: unsorted or out-of-range frame")
        _require(manual in ("upper", "lower"), f"{label}: unknown manual")
        _require(len(number_token) <= 128 and re.fullmatch(
            r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?",
            number_token) is not None, f"{label}: invalid decimal event value")
        number = float(number_token)
        significant = re.split(r"[eE]", number_token)[0]
        _require(math.isfinite(number) and not (
            number == 0 and any(character in "123456789" for character in significant)),
            f"{label}: nonfinite or underflowing event value")
        if kind in ("note_on", "note_off"):
            valid = 36 <= index <= 96 and (
                0 <= number <= 127 and number.is_integer() if kind == "note_on" else number == 0)
        elif kind == "key_position" and schema_version >= 2:
            valid = 36 <= index <= 96 and 0 <= number <= 1 and (
                contacts == "nominal" or number in (0, 1))
        elif kind in ("drawbar", "bank_drawbar"):
            valid = index <= (8 if kind == "drawbar" else 17) and 0 <= number <= 8 and number.is_integer()
        elif kind == "expression":
            valid = index == 0 and 0 <= number <= 1
        elif kind == "select_bank":
            valid = index == 0 and number in (0, 1)
        elif kind == "select_preset" and schema_version == 3:
            valid = index == 0 and 0 <= number <= 11 and number.is_integer()
        elif kind in ("all_notes_off", "cancel"):
            valid = index == 0 and number == 0
        elif kind == "percussion" and schema_version >= 2:
            valid = manual == "upper" and index <= 3 and number in (0, 1)
        elif kind in ("pedal_on", "pedal_off") and schema_version == 3:
            valid = manual == "lower" and 1 <= index <= 25 and (
                0 <= number <= 127 and number.is_integer() if kind == "pedal_on" else number == 0)
        elif kind == "pedal_drawbar" and schema_version == 3:
            valid = manual == "lower" and index <= 1 and 0 <= number <= 8 and number.is_integer()
        elif kind == "pedal_all_notes_off" and schema_version == 3:
            valid = manual == "lower" and index == 0 and number == 0
        else:
            valid = False
        _require(valid, f"{label}: unknown event type or invalid payload")
        repeated = repeated + 1 if previous == frame else 1
        previous = frame
        count += 1
        _require(count <= 262144 and repeated <= 1024, f"{label}: event density/count exceeds bounds")
    return count


def _wav(reader, path, frames, rate):
    expected_size = 44 + 4 * frames
    digest = hashlib.sha256()
    peak = sum_squares = count = 0
    with reader.open(path, expected_size) as stream:
        header = stream.read(44)
        _require(len(header) == 44, "WAV: truncated header")
        _require(header[:4] == b"RIFF" and header[8:16] == b"WAVEfmt " and header[36:40] == b"data",
                 "WAV: expected exact RIFF/WAVE fmt/data layout")
        _require(struct.unpack_from("<I", header, 4)[0] == expected_size - 8 and
                 struct.unpack_from("<I", header, 16)[0] == 16 and
                 struct.unpack_from("<I", header, 40)[0] == 4 * frames,
                 "WAV: RIFF/fmt/data sizes disagree with parameters")
        _require(struct.unpack_from("<HHIIHH", header, 20) == (1, 2, rate, rate * 4, 4, 16),
                 "WAV: expected PCM16 stereo with declared rate/byte rate/alignment")
        digest.update(header)
        while count < frames:
            data = stream.read(min(CHUNK, 4 * (frames - count)))
            _require(bool(data) and len(data) % 4 == 0, "WAV: truncated or misaligned samples")
            digest.update(data)
            for left, right in struct.iter_unpack("<hh", data):
                _require(left == right, "WAV: channels differ")
                peak = max(peak, abs(left))
                sum_squares += left * left
            count += len(data) // 4
        _require(not stream.read(1), "WAV: trailing bytes")
    return {"path": "render.wav", "size_bytes": expected_size, "sha256": digest.hexdigest(),
            "frames": count, "sample_rate": rate, "channels": 2, "channels_identical": True,
            "sample_format": "pcm_s16le", "metric_domain": "quantized_pcm16",
            "normalization_divisor": 32768, "pcm_peak_integer": peak,
            "pcm_sum_squares_integer": sum_squares, "pcm_peak": peak / 32768,
            "pcm_rms": math.sqrt(sum_squares / count) / 32768}


def _context(manifest, started, finished):
    tools = _object(manifest["tools"], {"wrapper", "profile_compiler"}, "tools")
    for name, record in tools.items():
        _object(record, {"path", "sha256", "size_bytes"}, f"tools.{name}")
        _absolute(record["path"], f"tools.{name}.path")
        _hash(record["sha256"], f"tools.{name}.sha256")
        _integer(record["size_bytes"], 1, MAX_TOOL, f"tools.{name}.size_bytes")
    git = _object(manifest["git"], {"repository_path", "captured_at_utc", "head", "dirty",
                                  "binary_association"}, "git", {"error"})
    _absolute(git["repository_path"], "git.repository_path")
    captured = _utc(git["captured_at_utc"], "git.captured_at_utc")
    _require(started <= captured <= finished, "git timestamp lies outside the recorded run")
    _literal(git["binary_association"], "not_established", "git.binary_association")
    _require(git["head"] is None or type(git["head"]) is str and
             re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", git["head"]) is not None,
             "git.head: expected null or commit hash")
    _require(git["dirty"] is None or type(git["dirty"]) is bool, "git.dirty: expected null or boolean")
    if git["head"] is None or git["dirty"] is None:
        _require("error" in git, "git: unavailable metadata requires an error")
    if "error" in git:
        _string(git["error"], "git.error")
    environment = _object(manifest["environment"], {
        "python", "python_implementation", "platform", "machine", "byteorder"}, "environment")
    for key, value in environment.items():
        if key == "machine":  # platform.machine() may be empty when unavailable.
            _require(type(value) is str, "environment.machine: expected string")
        else:
            _string(value, f"environment.{key}")
    _require(environment["byteorder"] in ("little", "big"), "environment.byteorder: unsupported value")


def _parameters(value, schema_version):
    keys = {"frames", "sample_rate", "block_size", "seed", "drawbars",
            "note", "event_mode", "event_count", "fail_on_clip"}
    console_choices = {"contacts": ("ideal", "nominal"),
                       "percussion": ("off", "second", "third"),
                       "percussion_volume": ("normal", "soft"),
                       "percussion_decay": ("slow", "fast")}
    if schema_version >= 2:
        keys.update(console_choices)
    if schema_version == 3:
        keys.add("pedal_drawbars")
    parameters = _object(value, keys, "parameters")
    if schema_version >= 2:
        for key, choices in console_choices.items():
            _require(type(parameters[key]) is str and parameters[key] in choices,
                     f"parameters.{key}: unsupported value")
    rate = _integer(parameters["sample_rate"], 44100, 96000, "parameters.sample_rate")
    _require(rate in (44100, 48000, 96000), "parameters.sample_rate: unsupported rate")
    _integer(parameters["frames"], 1, rate * 600, "parameters.frames")
    _integer(parameters["block_size"], 1, 65536, "parameters.block_size")
    _integer(parameters["seed"], 0, 2**64 - 1, "parameters.seed")
    _require(type(parameters["drawbars"]) is str and
             re.fullmatch(r"[0-8]{9}", parameters["drawbars"]) is not None,
             "parameters.drawbars: expected nine digits 0..8")
    if schema_version == 3:
        _require(type(parameters["pedal_drawbars"]) is str and
                 re.fullmatch(r"[0-8]{2}", parameters["pedal_drawbars"]) is not None,
                 "parameters.pedal_drawbars: expected two digits 0..8")
    _literal(parameters["fail_on_clip"], True, "parameters.fail_on_clip")
    _require(parameters["event_mode"] in ("default_note", "file"), "parameters.event_mode: unsupported value")
    if parameters["event_mode"] == "default_note":
        _integer(parameters["note"], 36, 96, "parameters.note")
        _literal(parameters["event_count"], None, "parameters.event_count")
    else:
        _literal(parameters["note"], None, "parameters.note")
        _integer(parameters["event_count"], 0, 262144, "parameters.event_count")
    return parameters


def _invocation(value, parameters, renderer, schema_version):
    invocation = _object(value, {"argv", "returncode", "timed_out", "stdout_truncated",
                                "stderr_truncated", "capture_incomplete", "capture_errors",
                                "stdout", "stderr"}, "invocation")
    _literal(invocation["returncode"], 0, "invocation.returncode")
    for key in ("timed_out", "stdout_truncated", "stderr_truncated", "capture_incomplete"):
        _literal(invocation[key], False, f"invocation.{key}")
    _literal(invocation["capture_errors"], [], "invocation.capture_errors")
    argv = invocation["argv"]
    count = {1: 18, 2: 26, 3: 28}[schema_version]
    _require(type(argv) is list and len(argv) == count and all(type(token) is str for token in argv),
             f"invocation.argv: expected the complete {count}-token producer argument list")
    profile_path = _absolute(argv[2], "invocation.argv profile")
    original_directory = profile_path.parent
    expected = [renderer["path"], "--profile", str(original_directory / "profile.b3p"),
                "--output", str(original_directory / "render.wav"), "--frames", str(parameters["frames"]),
                "--sample-rate", str(parameters["sample_rate"]), "--block-size", str(parameters["block_size"]),
                "--seed", str(parameters["seed"]), "--drawbars", parameters["drawbars"]]
    if schema_version == 3:
        expected += ["--pedal-drawbars", parameters["pedal_drawbars"]]
    if schema_version >= 2:
        expected += ["--contacts", parameters["contacts"], "--percussion", parameters["percussion"],
                     "--percussion-volume", parameters["percussion_volume"],
                     "--percussion-decay", parameters["percussion_decay"]]
    expected += ["--fail-on-clip"]
    expected += (["--events", str(original_directory / "events.txt")] if parameters["event_mode"] == "file"
                 else ["--note", str(parameters["note"])])
    _literal(argv, expected, "invocation.argv")
    return invocation


def _metrics(value, parameters, authoring_hash, schema_version):
    expected = {"status": "ok", "model": "ideal-shared-sine-v1", "evidence_status": "unmeasured",
                "profile_id": "nominal-unmeasured-v1", "authoring_sha256": authoring_hash,
                "channels": 2, "sample_format": "pcm_s16le", "clipped_frames": 0,
                "clipped_channel_samples": 0}
    if schema_version >= 2:
        expected.update({"render_schema_version": schema_version,
                         "contact_model": ("ideal-contacts-v1" if parameters["contacts"] == "ideal"
                                           else "nominal-linear-travel-v1"),
                         "percussion_model": "shared-readiness-v1"})
    if schema_version == 3:
        # Independently frozen documentary hashes: raw and canonical
        # data/pedal-map.json, then review-a-pedal.csv and review-b-pedal.csv.
        # The remaining exact values follow PEDAL_INTEGRATION_CONTRACT.md;
        # matrix rows use Brown, Red, Orange, Yellow and are divided by eight.
        # Do not derive these expectations from producer or renderer metadata.
        expected.update({
            "pedal_map_id": "atlas-derived-b3-c3-pedal-v1",
            "pedal_map_raw_sha256": "58a30850c08933a075cfcec04faeb2cb479f60bd9dda82ace3246552221623bd",
            "pedal_map_canonical_sha256": "7b2631a0c7d55a18f8225d4ee420e472c23b9f2809eec69865474eafce6f5fb2",
            "pedal_reference_a_sha256": "b8177479a5af16f4e6b8759313d90148a1213657c83f8a6e6533422bfa104ca1",
            "pedal_reference_b_sha256": "b8177479a5af16f4e6b8759313d90148a1213657c83f8a6e6533422bfa104ca1",
            "pedal_routing_model": "linear-pedal-bus-reference-v1",
            "pedal_voice_model": "nominal-static-pedal-mixture-v1",
            "pedal_gain_law": "linear-pedal-position-v1",
            "pedal_contact_model": "ideal-eight-contact-pedal-v1",
            "pedal_mixture_matrix": "4,2,1,1;1,4,2,1",
            "pedal_mixture_denominator": 8,
            "pedal_gain_denominator": 8,
            "pedal_weight_policy": "all-200-unit-positive-v1",
        })
    expected.update({key: parameters[key] for key in ("frames", "sample_rate", "block_size", "seed")})
    _object(value, set(expected) | {"peak", "rms"}, "renderer_metrics")
    for key, target in expected.items():
        _literal(value[key], target, f"renderer_metrics.{key}")
    for key in ("peak", "rms"):
        _number(value[key], 0, 1, f"renderer_metrics.{key}")
    _require(value["rms"] <= value["peak"] + TOLERANCE, "renderer_metrics.rms exceeds peak")


def _renderer(reader, record):
    path = _absolute(record["path"], "renderer.path")
    native = isinstance(path, PureWindowsPath) if os.name == "nt" else isinstance(path, PurePosixPath)
    if not native:
        return {"status": "unavailable", "reason": "recorded path belongs to another operating system"}
    try:
        current_path = Path(path)
        # A historical path can be absent beneath a host's symlinked /tmp.
        # Establish availability before inspecting unrelated ancestor aliases;
        # present files still receive every strict reader/type/hash check below.
        current_path.lstat()
        actual, _ = reader.read(current_path, MAX_EXECUTABLE, retain=False)
    except (FileNotFoundError, NotADirectoryError, PermissionError) as error:
        return {"status": "unavailable", "reason": type(error).__name__}
    _literal(actual["sha256"], record["sha256_before"], "current renderer SHA-256")
    _literal(actual["size_bytes"], record["size_bytes"], "current renderer size")
    return {"status": "matched", "sha256": actual["sha256"],
            "executable_permission": os.access(path, os.X_OK)}


def verify_bundle(directory_or_manifest):
    """Verify all retained assertions; unavailable external renderer is explicit.

    A matching current executable is checked, never run. Missing external inputs,
    tools or checkout metadata do not prevent verification of their retained copies.
    No claim is made about producer authentication, build provenance, or replay.
    """
    path = Path(os.path.abspath(os.fspath(directory_or_manifest)))
    directory = path.parent if path.name == "manifest.json" and not stat.S_ISDIR(path.lstat().st_mode) else path
    reader = _Reader()
    reader.directory(directory)
    manifest_identity, raw = reader.read(directory / "manifest.json", MAX_MANIFEST)
    manifest = _json(raw, MAX_MANIFEST, "manifest")
    _object(manifest, {"schema_version", "evidence_scope", "status", "started_at_utc", "finished_at_utc",
                       "parameters", "inputs", "compiled_profile", "renderer", "tools", "git",
                       "environment", "limits", "invocation", "renderer_metrics", "wav",
                       "metric_comparison", "integrity_verified", "error"}, "manifest")
    schema_version = _integer(manifest["schema_version"], 1, 3, "schema_version")
    for key, expected in (("evidence_scope", "synthetic_engineering"),
                          ("status", "succeeded"), ("error", None), ("integrity_verified", True)):
        _literal(manifest[key], expected, key)
    started = _utc(manifest["started_at_utc"], "started_at_utc")
    finished = _utc(manifest["finished_at_utc"], "finished_at_utc")
    _require(started <= finished, "finish precedes start")
    _context(manifest, started, finished)
    parameters = _parameters(manifest["parameters"], schema_version)
    frames, rate = parameters["frames"], parameters["sample_rate"]
    limits = _object(manifest["limits"], {"timeout_seconds", "log_bytes_per_stream", "metrics_json_bytes",
                                        "event_bytes", "executable_bytes", "expected_wav_bytes"}, "limits")
    _integer(limits["timeout_seconds"], 1, 600, "limits.timeout_seconds")
    for key, expected in (("log_bytes_per_stream", MAX_LOG), ("metrics_json_bytes", MAX_METRICS),
                          ("event_bytes", MAX_SCORE), ("executable_bytes", MAX_EXECUTABLE),
                          ("expected_wav_bytes", 44 + frames * 4)):
        _literal(limits[key], expected, f"limits.{key}")
    renderer = _object(manifest["renderer"], {"path", "size_bytes", "sha256_before", "sha256_after"}, "renderer")
    _absolute(renderer["path"], "renderer.path")
    _integer(renderer["size_bytes"], 1, MAX_EXECUTABLE, "renderer.size_bytes")
    _hash(renderer["sha256_before"], "renderer.sha256_before")
    _literal(renderer["sha256_after"], renderer["sha256_before"], "renderer.sha256_after")
    invocation = _invocation(manifest["invocation"], parameters, renderer, schema_version)
    inputs = _object(manifest["inputs"], {"profile_json", "events"}, "inputs")
    names = {"manifest.json", "profile.json", "profile.b3p", "render.wav",
             "renderer.stdout.txt", "renderer.stderr.txt"}
    if parameters["event_mode"] == "file":
        names.add("events.txt")
    else:
        _literal(inputs["events"], None, "inputs.events")
    _inventory(directory, names)
    profile_record = inputs["profile_json"]
    _record(profile_record, "profile.json", MAX_PROFILE, "inputs.profile_json",
            {"source_path", "canonical_authoring_sha256"})
    _absolute(profile_record["source_path"], "inputs.profile_json.source_path")
    _hash(profile_record["canonical_authoring_sha256"], "canonical_authoring_sha256")
    actual, raw = reader.read(directory / "profile.json", MAX_PROFILE)
    _matches(profile_record, actual, "inputs.profile_json")
    profile = _json(raw, MAX_PROFILE, "profile.json")
    try:
        compiled = _compiler.compile_profile(profile).encode("utf-8")
        authoring_hash = _compiler.authoring_sha256(profile)
    except (ValueError, TypeError, RecursionError) as error:
        raise VerificationError(f"profile compilation failed: {error}") from error
    _literal(profile_record["canonical_authoring_sha256"], authoring_hash, "canonical_authoring_sha256")
    _record(manifest["compiled_profile"], "profile.b3p", MAX_COMPILED, "compiled_profile")
    actual, retained_compiled = reader.read(directory / "profile.b3p", MAX_COMPILED)
    _matches(manifest["compiled_profile"], actual, "compiled_profile")
    _require(retained_compiled == compiled, "compiled profile differs from independently recompiled authoring bytes")
    if parameters["event_mode"] == "file":
        _record(inputs["events"], "events.txt", MAX_SCORE, "inputs.events", {"source_path"})
        _absolute(inputs["events"]["source_path"], "inputs.events.source_path")
        actual, raw_events = reader.read(directory / "events.txt", MAX_SCORE)
        _matches(inputs["events"], actual, "inputs.events")
        _literal(parameters["event_count"],
                 _events(raw_events, frames, schema_version, parameters.get("contacts", "ideal")),
                 "parameters.event_count")
    stdout = None
    for name in ("stdout", "stderr"):
        _record(invocation[name], f"renderer.{name}.txt", MAX_LOG, f"invocation.{name}")
        actual, raw_log = reader.read(directory / f"renderer.{name}.txt", MAX_LOG, retain=name == "stdout")
        _matches(invocation[name], actual, f"invocation.{name}")
        if name == "stdout":
            stdout = _json(raw_log, MAX_METRICS, "renderer stdout")
    _metrics(stdout, parameters, authoring_hash, schema_version)
    _metrics(manifest["renderer_metrics"], parameters, authoring_hash, schema_version)
    _require(all(type(stdout[key]) is type(manifest["renderer_metrics"][key]) and
                 stdout[key] == manifest["renderer_metrics"][key] for key in stdout),
             "renderer_metrics differs from actual retained stdout")
    actual_wav = _wav(reader, directory / "render.wav", frames, rate)
    _object(manifest["wav"], set(actual_wav), "wav")
    for key, expected in actual_wav.items():
        if key in ("pcm_peak", "pcm_rms"):
            _number(manifest["wav"][key], 0, 1, f"wav.{key}")
            _require(manifest["wav"][key] == expected, f"wav.{key}: differs from decoded PCM")
        else:
            _literal(manifest["wav"][key], expected, f"wav.{key}")
    comparison = {"absolute_error_bound": PCM_BOUND, "numeric_tolerance": TOLERANCE,
                  "float_metric_domain": "engine_pre_quantization", "pcm_metric_domain": "quantized_pcm16",
                  "within_quantization_bound": True,
                  "basis": "one PCM16 step covers rounding and positive-rail saturation; zero clipped frames required"}
    for name in ("peak", "rms"):
        difference = abs(stdout[name] - actual_wav["pcm_" + name])
        _require(difference <= PCM_BOUND + TOLERANCE, f"{name}: exceeds PCM16 quantization bound")
        comparison[name + "_absolute_difference"] = difference
    _object(manifest["metric_comparison"], set(comparison), "metric_comparison")
    for key, expected in comparison.items():
        _literal(manifest["metric_comparison"][key], expected, f"metric_comparison.{key}")
    external = _renderer(reader, renderer)
    _inventory(directory, names)
    reader.finish()
    return {"status": "verified_retained_bundle", "schema_version": schema_version,
            "evidence_scope": "synthetic_engineering", "manifest": str(directory / "manifest.json"),
            "manifest_sha256": manifest_identity["sha256"], "artifacts_verified": len(names) - 1,
            "frames": frames, "sample_rate": rate, "canonical_authoring_sha256": authoring_hash,
            "wav_sha256": actual_wav["sha256"], "renderer": external,
            "replay": {"status": "not_performed", "renderer_available": external["status"] == "matched",
                       "reason": "verification never executes recorded commands"},
            "provenance": {"authentication": "not_established", "source_build_association": "not_established",
                           "original_inputs_and_tools": "recorded_not_reverified", "physical_fidelity": "not_established"}}


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise VerificationError(f"arguments: {message}")


def main(argv=None):
    parser = _Parser(description=__doc__.split("\n\n")[0], allow_abbrev=False)
    parser.add_argument("bundle", help="result directory or its manifest.json")
    try:
        options = parser.parse_args(argv)
        report = verify_bundle(options.bundle)
    except (VerificationError, OSError, RuntimeError, TypeError) as error:
        print(json.dumps({"status": "failed", "error": str(error)}, sort_keys=True, allow_nan=False))
        return 1
    print(json.dumps(report, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
