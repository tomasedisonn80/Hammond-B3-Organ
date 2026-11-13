#!/usr/bin/env python3
"""Retain reproducible, explicitly synthetic offline-render evidence (stdlib only).

Public API: run_fixture(**options), sha256_file(path, max_bytes),
inspect_wav(path, *, frames, sample_rate), validate_events(raw, frames, contacts="ideal").
A preflight error raises FixtureError/OSError without creating an output directory.
After directory creation, run_fixture returns a manifest whose status MUST be
checked: only 'succeeded' is success. No hardware-fidelity claim is made.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import platform
import re
import signal
import stat
import struct
import subprocess
import sys
import threading
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROFILE = ROOT / "data/profiles/nominal-unmeasured-v1.json"
SCHEMA_VERSION = 3
CONTACT_MODELS = {"ideal": "ideal-contacts-v1", "nominal": "nominal-linear-travel-v1"}
# Frozen from data/pedal-map.json, the two retained factory CSVs, and
# docs/PEDAL_INTEGRATION_CONTRACT.md. These identify documentary routing and an
# explicitly nominal rational transfer; they do not establish measured voicing.
# The independent consumer carries its own expectations and never imports us.
PEDAL_METRICS_V3 = {
    "pedal_routing_model": "linear-pedal-bus-reference-v1",
    "pedal_voice_model": "nominal-static-pedal-mixture-v1",
    "pedal_gain_law": "linear-pedal-position-v1",
    "pedal_contact_model": "ideal-eight-contact-pedal-v1",
    "pedal_map_id": "atlas-derived-b3-c3-pedal-v1",
    "pedal_map_raw_sha256": "58a30850c08933a075cfcec04faeb2cb479f60bd9dda82ace3246552221623bd",
    "pedal_map_canonical_sha256": "7b2631a0c7d55a18f8225d4ee420e472c23b9f2809eec69865474eafce6f5fb2",
    "pedal_reference_a_sha256": "b8177479a5af16f4e6b8759313d90148a1213657c83f8a6e6533422bfa104ca1",
    "pedal_reference_b_sha256": "b8177479a5af16f4e6b8759313d90148a1213657c83f8a6e6533422bfa104ca1",
    "pedal_mixture_matrix": "4,2,1,1;1,4,2,1",
    "pedal_mixture_denominator": 8,
    "pedal_gain_denominator": 8,
    "pedal_weight_policy": "all-200-unit-positive-v1",
}
MAX_EXECUTABLE_BYTES = 512 * 1024 * 1024
MAX_SCORE_BYTES = 16 * 1024 * 1024
MAX_LOG_BYTES = 1024 * 1024
MAX_METRICS_BYTES = 16 * 1024
MAX_TOOL_BYTES = 1024 * 1024
DEFAULT_TIMEOUT_SECONDS = 120
PCM_ERROR_BOUND = 1.0 / 32768.0
CHUNK_BYTES = 64 * 1024

_spec = importlib.util.spec_from_file_location(
    "hammond_fixture_profile_compiler", Path(__file__).with_name("compile_profile.py"))
assert _spec is not None and _spec.loader is not None
profile_compiler = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(profile_compiler)


class FixtureError(ValueError):
    """Invalid input or an incomplete/untrustworthy evidence run."""


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _unique_object(pairs: list) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise FixtureError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _finite_json_number(token: str) -> float:
    value = float(token)
    if not math.isfinite(value):
        raise FixtureError(f"nonfinite JSON number: {token}")
    return value


def _reject_constant(token: str) -> None:
    raise FixtureError(f"non-JSON numeric constant: {token}")


def _json(raw: bytes) -> Any:
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object,
                          parse_float=_finite_json_number, parse_constant=_reject_constant)
    except (UnicodeError, ValueError, RecursionError) as error:
        raise FixtureError(f"invalid UTF-8 JSON: {error}") from error


def _stamp(value: os.stat_result) -> tuple:
    return (value.st_dev, value.st_ino, value.st_mode, value.st_size,
            value.st_mtime_ns, value.st_ctime_ns)


def _check_opened_file(path: Path, by_path: os.stat_result, by_fd: os.stat_result) -> None:
    # Windows stat/fstat timestamps can have different meanings (notably ctime).
    # Compare full stamps only within each API, before and after reading. POSIX
    # additionally gives comparable device/inode identities across the APIs.
    if not stat.S_ISREG(by_fd.st_mode) or by_fd.st_size != by_path.st_size:
        raise FixtureError(f"file type/size changed before reading: {path}")
    if os.name == "posix" and (by_fd.st_dev, by_fd.st_ino) != (by_path.st_dev, by_path.st_ino):
        raise FixtureError(f"file identity changed before reading: {path}")


def _read_file(path: Path, limit: int, *, retain: bool = False) -> tuple[dict, bytes | None]:
    """Hash in bounded chunks and reject files replaced/changed while reading."""
    before_path = path.lstat()
    if not stat.S_ISREG(before_path.st_mode) or not 0 <= before_path.st_size <= limit:
        raise FixtureError(f"expected a regular file no larger than {limit} bytes: {path}")
    digest = hashlib.sha256()
    saved = bytearray() if retain else None
    count = 0
    with path.open("rb") as source:
        before = os.fstat(source.fileno())
        _check_opened_file(path, before_path, before)
        while True:
            chunk = source.read(min(CHUNK_BYTES, limit - count + 1))
            if not chunk:
                break
            count += len(chunk)
            if count > limit:
                raise FixtureError(f"file exceeds {limit} byte limit: {path}")
            digest.update(chunk)
            if saved is not None:
                saved.extend(chunk)
        after = os.fstat(source.fileno())
    if (_stamp(before) != _stamp(after) or count != before.st_size
            or _stamp(before_path) != _stamp(path.lstat())):
        raise FixtureError(f"file changed while reading: {path}")
    return {"sha256": digest.hexdigest(), "size_bytes": count}, (
        bytes(saved) if saved is not None else None)


def sha256_file(path: str | os.PathLike[str], max_bytes: int) -> dict:
    """Return {'sha256': lowercase hex, 'size_bytes': int}; no unbounded reads."""
    return _read_file(Path(path), max_bytes)[0]


def _input_path(value: str | os.PathLike[str], label: str) -> Path:
    try:
        path = Path(value).resolve(strict=True)
        if len(os.fsencode(path)) > 4096:
            raise FixtureError(f"{label} path exceeds 4096 bytes")
        if not path.is_file():
            raise FixtureError(f"{label} must be a regular file: {path}")
        return path
    except (OSError, ValueError, RuntimeError) as error:
        raise FixtureError(f"cannot use {label}: {error}") from error


def _unsigned(token: str) -> int:
    if not re.fullmatch(r"[0-9]{1,128}", token):
        raise FixtureError("expected an unsigned decimal integer (at most 128 digits)")
    value = int(token)
    if value > 2**64 - 1:
        raise FixtureError("unsigned decimal integer exceeds uint64")
    return value


def _event_number(token: str) -> float:
    if len(token) > 128 or not re.fullmatch(
            r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?", token):
        raise FixtureError("event value must be a finite decimal number")
    value = float(token)
    mantissa = re.split("[eE]", token)[0]
    if not math.isfinite(value) or (value == 0 and any(c in "123456789" for c in mantissa)):
        raise FixtureError("event value is nonfinite or outside binary64 range")
    return value


def validate_events(raw: bytes, frames: int, contacts: str = "ideal") -> int:
    """Preflight the current event grammar against the selected contact model."""
    if type(contacts) is not str or contacts not in ("ideal", "nominal"):
        raise FixtureError("contacts must be ideal or nominal")
    if len(raw) > MAX_SCORE_BYTES or b"\x00" in raw:
        raise FixtureError("events exceed 16 MiB or contain a NUL byte")
    source = io.BytesIO(raw)
    if raw.startswith(b"\xef\xbb\xbf"):
        source.seek(3)
    previous = -1
    same_frame = count = line_number = 0
    while True:
        line = source.readline(4098)
        if not line:
            break
        line_number += 1
        try:
            if line.endswith(b"\n"):
                line = line[:-1]
            if len(line) > 4096:
                raise FixtureError("event line exceeds 4096 bytes")
            text = line.decode("utf-8").strip(" \t\r\n\f\v")
            if not text or text.startswith("#"):
                continue
            fields = re.split(r"[ \t\r\n\f\v]+", text)
            if len(fields) != 5:
                raise FixtureError("expected exactly five event fields")
            frame_text, kind, manual, index_text, value_text = fields
            frame, index, value = _unsigned(frame_text), _unsigned(index_text), _event_number(value_text)
            if frame >= frames or frame < previous:
                raise FixtureError("event frames must be sorted and lie in [0,total_frames)")
            if manual not in ("upper", "lower"):
                raise FixtureError("event manual must be upper or lower")
            valid = {
                "note_on": 36 <= index <= 96 and 0 <= value <= 127 and value.is_integer(),
                "note_off": 36 <= index <= 96 and value == 0,
                "key_position": 36 <= index <= 96 and 0 <= value <= 1 and
                    (contacts == "nominal" or value in (0, 1)),
                "drawbar": index <= 8 and 0 <= value <= 8 and value.is_integer(),
                "expression": index == 0 and 0 <= value <= 1,
                "all_notes_off": index == 0 and value == 0,
                "bank_drawbar": index <= 17 and 0 <= value <= 8 and value.is_integer(),
                "select_bank": index == 0 and value in (0, 1),
                "cancel": index == 0 and value == 0,
                "percussion": manual == "upper" and index <= 3 and value in (0, 1),
                "pedal_on": manual == "lower" and 1 <= index <= 25 and
                    0 <= value <= 127 and value.is_integer(),
                "pedal_off": manual == "lower" and 1 <= index <= 25 and value == 0,
                "pedal_drawbar": manual == "lower" and index <= 1 and
                    0 <= value <= 8 and value.is_integer(),
                "pedal_all_notes_off": manual == "lower" and index == 0 and value == 0,
            }
            if not valid.get(kind, False):
                raise FixtureError(f"unknown event type or invalid payload: {kind}")
            count += 1
            same_frame = same_frame + 1 if frame == previous else 1
            previous = frame
            if count > 262144 or same_frame > 1024:
                raise FixtureError("events exceed 262144 total or 1024 at one frame")
        except (ValueError, UnicodeError) as error:
            raise FixtureError(f"events line {line_number}: {error}") from error
    return count


def _integer(value: int, low: int, high: int, label: str) -> None:
    if type(value) is not int or not low <= value <= high:
        raise FixtureError(f"{label} must be an integer in {low}..{high}")


def _terminate(process: subprocess.Popen) -> None:
    try:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
    except ProcessLookupError:
        pass


def _invoke(argv: list[str], cwd: Path, timeout: float) -> tuple[dict, bytes, bytes]:
    """Bound retained logs and wall time; no shell or stdin interaction."""
    process = subprocess.Popen(argv, cwd=cwd, stdin=subprocess.DEVNULL,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               start_new_session=(os.name == "posix"))
    buffers = [bytearray(), bytearray()]
    truncated = [False, False]
    read_errors = []

    def collect(pipe: Any, slot: int) -> None:
        try:
            with pipe:
                while True:
                    chunk = pipe.read(CHUNK_BYTES)
                    if not chunk:
                        return
                    available = MAX_LOG_BYTES - len(buffers[slot])
                    buffers[slot].extend(chunk[:available])
                    if len(chunk) > available:
                        truncated[slot] = True
                        _terminate(process)
                        return
        except OSError as error:
            read_errors.append(str(error))
            _terminate(process)

    readers = [threading.Thread(target=collect, args=(pipe, slot), daemon=True)
               for slot, pipe in enumerate((process.stdout, process.stderr))]
    for reader in readers:
        reader.start()
    timed_out = False
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        _terminate(process)
        process.wait(timeout=5)
    except BaseException:
        _terminate(process)
        process.wait(timeout=5)
        raise
    for reader in readers:
        reader.join(timeout=1)
    incomplete = any(reader.is_alive() for reader in readers)
    if incomplete:
        _terminate(process)
        for reader in readers:
            reader.join(timeout=1)
    return ({"returncode": process.returncode, "timed_out": timed_out,
             "stdout_truncated": truncated[0], "stderr_truncated": truncated[1],
             "capture_incomplete": incomplete, "capture_errors": read_errors},
            bytes(buffers[0]), bytes(buffers[1]))


def _git_context() -> dict:
    result = {"repository_path": str(ROOT), "captured_at_utc": _utc(),
              "head": None, "dirty": None, "binary_association": "not_established"}
    try:
        info, head, _ = _invoke(["git", "-C", str(ROOT), "rev-parse", "HEAD"], ROOT, 5)
        if (info["returncode"] != 0 or info["timed_out"] or info["capture_incomplete"]
                or info["capture_errors"] or not re.fullmatch(rb"[0-9a-f]{40,64}\n", head)):
            raise FixtureError("git HEAD unavailable")
        result["head"] = head.decode("ascii").strip()
        info, status_text, _ = _invoke(
            ["git", "-C", str(ROOT), "status", "--porcelain=v1", "--untracked-files=normal"], ROOT, 5)
        if (info["returncode"] != 0 or info["timed_out"] or info["stdout_truncated"]
                or info["stderr_truncated"] or info["capture_incomplete"] or info["capture_errors"]):
            raise FixtureError("git dirty status unavailable")
        result["dirty"] = bool(status_text)
    except (OSError, FixtureError, subprocess.SubprocessError) as error:
        result["error"] = str(error)
    return result


def inspect_wav(path: str | os.PathLike[str], *, frames: int, sample_rate: int) -> dict:
    """Stream the renderer's exact 44-byte RIFF/PCM16 format and both channels."""
    path = Path(path)
    expected_size = 44 + frames * 4
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_size != expected_size:
        raise FixtureError("WAV must be a regular file of exactly 44 + frames*4 bytes")
    digest = hashlib.sha256()
    peak = squares = counted = 0
    with path.open("rb") as source:
        opened = os.fstat(source.fileno())
        _check_opened_file(path, before, opened)
        header = source.read(44)
        expected = (b"RIFF", expected_size - 8, b"WAVE", b"fmt ", 16, 1, 2,
                    sample_rate, sample_rate * 4, 4, 16, b"data", frames * 4)
        if len(header) != 44 or struct.unpack("<4sI4s4sIHHIIHH4sI", header) != expected:
            raise FixtureError("WAV header does not match requested RIFF PCM16 stereo/rate/count")
        digest.update(header)
        while counted < frames:
            chunk = source.read(min(CHUNK_BYTES, (frames - counted) * 4))
            if not chunk or len(chunk) % 4:
                raise FixtureError("WAV data is truncated or frame-misaligned")
            digest.update(chunk)
            for left, right in struct.iter_unpack("<hh", chunk):
                if left != right:
                    raise FixtureError("dry WAV channels are not identical")
                peak = max(peak, abs(left))
                squares += left * left
            counted += len(chunk) // 4
        if source.read(1) or _stamp(os.fstat(source.fileno())) != _stamp(opened):
            raise FixtureError("WAV changed or has trailing bytes")
    if _stamp(path.lstat()) != _stamp(before):
        raise FixtureError("WAV changed during verification")
    return {"path": path.name, "sha256": digest.hexdigest(), "size_bytes": expected_size,
            "sample_format": "pcm_s16le", "sample_rate": sample_rate, "frames": counted,
            "channels": 2, "channels_identical": True, "normalization_divisor": 32768,
            "pcm_peak_integer": peak, "pcm_sum_squares_integer": squares,
            "pcm_peak": peak / 32768.0, "pcm_rms": math.sqrt(squares / counted) / 32768.0,
            "metric_domain": "quantized_pcm16"}


def _artifact(path: str, raw: bytes, **extra: Any) -> dict:
    return {"path": path, "size_bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(), **extra}


def _write_new(path: Path, raw: bytes) -> None:
    with path.open("xb") as output:
        output.write(raw)


def _manifest_write(directory: Path, manifest: dict) -> None:
    raw = (json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")
    pending = directory / "manifest.pending.json"
    _write_new(pending, raw)
    os.replace(pending, directory / "manifest.json")


def _validate_metrics(metrics: dict, parameters: dict, authoring_digest: str) -> None:
    expected = {"status": "ok", "model": profile_compiler.MODEL, "evidence_status": "unmeasured",
                "render_schema_version": 3, "contact_model": CONTACT_MODELS[parameters["contacts"]],
                "percussion_model": "shared-readiness-v1",
                "profile_id": profile_compiler.PROFILE_ID, "authoring_sha256": authoring_digest,
                "sample_rate": parameters["sample_rate"], "block_size": parameters["block_size"],
                "frames": parameters["frames"], "seed": parameters["seed"], "channels": 2,
                "sample_format": "pcm_s16le", "clipped_frames": 0, "clipped_channel_samples": 0}
    expected.update(PEDAL_METRICS_V3)
    if set(metrics) != set(expected) | {"peak", "rms"}:
        raise FixtureError("renderer JSON fields differ from the supported metrics contract")
    for key, value in expected.items():
        if type(metrics[key]) is not type(value) or metrics[key] != value:
            raise FixtureError(f"renderer JSON {key} differs from requested/validated value")
    for key in ("peak", "rms"):
        value = metrics[key]
        if type(value) not in (float, int) or not math.isfinite(value) or not 0 <= value <= 1:
            raise FixtureError(f"renderer JSON {key} must be finite and in 0..1 without clipping")
    if metrics["rms"] > metrics["peak"] + 1e-12:
        raise FixtureError("renderer RMS exceeds peak")


def run_fixture(*, renderer: str | os.PathLike[str], output_dir: str | os.PathLike[str],
                profile_json: str | os.PathLike[str] = DEFAULT_PROFILE,
                events: str | os.PathLike[str] | None = None, frames: int | None = None,
                sample_rate: int = 48000, block_size: int = 64, seed: int = 0,
                drawbars: str = "888000000", note: int | None = None,
                pedal_drawbars: str = "00",
                contacts: str = "ideal", percussion: str = "off",
                percussion_volume: str = "normal", percussion_decay: str = "slow",
                timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> dict:
    """Create a NEW evidence directory. Check returned status; failures are retained."""
    _integer(sample_rate, 44100, 96000, "sample_rate")
    if sample_rate not in (44100, 48000, 96000):
        raise FixtureError("sample_rate must be 44100, 48000 or 96000 Hz")
    frames = sample_rate * 4 if frames is None else frames
    _integer(frames, 1, sample_rate * 600, "frames")
    _integer(block_size, 1, 65536, "block_size")
    _integer(seed, 0, 2**64 - 1, "seed")
    _integer(timeout_seconds, 1, 600, "timeout_seconds")
    if type(drawbars) is not str or not re.fullmatch(r"[0-8]{9}", drawbars):
        raise FixtureError("drawbars must contain exactly nine ASCII digits 0..8")
    if type(pedal_drawbars) is not str or not re.fullmatch(r"[0-8]{2}", pedal_drawbars):
        raise FixtureError("pedal_drawbars must contain exactly two ASCII digits 0..8")
    for label, value, choices in (
            ("contacts", contacts, ("ideal", "nominal")),
            ("percussion", percussion, ("off", "second", "third")),
            ("percussion_volume", percussion_volume, ("normal", "soft")),
            ("percussion_decay", percussion_decay, ("slow", "fast"))):
        if type(value) is not str or value not in choices:
            raise FixtureError(f"{label} must be one of {', '.join(choices)}")
    if events is not None and note is not None:
        raise FixtureError("explicit note is incompatible with events")
    if note is not None:
        _integer(note, 36, 96, "note")
    note = (60 if note is None else note) if events is None else None
    directory = Path(os.path.abspath(os.fspath(output_dir)))
    if os.path.lexists(directory):
        raise FixtureError(f"output directory already exists; never overwrite: {directory}")
    if not directory.parent.is_dir():
        raise FixtureError("output directory parent must already exist")
    directory = directory.parent.resolve() / directory.name
    if len(os.fsencode(directory / "renderer.stderr.txt")) > 4096:
        raise FixtureError("output path exceeds 4096 bytes")
    renderer_path = _input_path(renderer, "renderer")
    if not os.access(renderer_path, os.X_OK):
        raise FixtureError(f"renderer is not executable: {renderer_path}")
    renderer_hash = sha256_file(renderer_path, MAX_EXECUTABLE_BYTES)
    authoring_path = _input_path(profile_json, "profile JSON")
    profile_hash, raw_profile = _read_file(authoring_path, profile_compiler.MAX_INPUT_BYTES, retain=True)
    assert raw_profile is not None
    try:
        profile = _json(raw_profile)
        compiled = profile_compiler.compile_profile(profile).encode("utf-8")
        canonical_digest = profile_compiler.authoring_sha256(profile)
    except (ValueError, TypeError, RecursionError) as error:
        raise FixtureError(f"profile compilation failed: {error}") from error
    raw_events = None
    event_path = None
    event_count = None
    if events is not None:
        event_path = _input_path(events, "events")
        _, raw_events = _read_file(event_path, MAX_SCORE_BYTES, retain=True)
        assert raw_events is not None
        event_count = validate_events(raw_events, frames, contacts)
    tools_identity = {}
    for name, path in (("wrapper", Path(__file__).resolve()),
                       ("profile_compiler", Path(profile_compiler.__file__).resolve())):
        tools_identity[name] = {"path": str(path), **sha256_file(path, MAX_TOOL_BYTES)}
    parameters = {"frames": frames, "sample_rate": sample_rate, "block_size": block_size,
                  "seed": seed, "drawbars": drawbars, "pedal_drawbars": pedal_drawbars, "note": note,
                  "contacts": contacts, "percussion": percussion,
                  "percussion_volume": percussion_volume, "percussion_decay": percussion_decay,
                  "event_mode": "file" if events is not None else "default_note",
                  "event_count": event_count, "fail_on_clip": True}
    manifest = {
        "schema_version": SCHEMA_VERSION, "evidence_scope": "synthetic_engineering",
        "status": "incomplete", "started_at_utc": _utc(), "finished_at_utc": None,
        "parameters": parameters,
        "inputs": {"profile_json": {"path": "profile.json", "source_path": str(authoring_path),
                                     **profile_hash, "canonical_authoring_sha256": canonical_digest},
                   "events": _artifact("events.txt", raw_events, source_path=str(event_path))
                   if raw_events is not None else None},
        "compiled_profile": _artifact("profile.b3p", compiled),
        "renderer": {"path": str(renderer_path), "size_bytes": renderer_hash["size_bytes"],
                     "sha256_before": renderer_hash["sha256"], "sha256_after": None},
        "tools": tools_identity, "git": _git_context(),
        "environment": {"python": sys.version, "python_implementation": platform.python_implementation(),
                        "platform": platform.platform(), "machine": platform.machine(),
                        "byteorder": sys.byteorder},
        "limits": {"timeout_seconds": timeout_seconds, "log_bytes_per_stream": MAX_LOG_BYTES,
                   "metrics_json_bytes": MAX_METRICS_BYTES,
                   "event_bytes": MAX_SCORE_BYTES, "executable_bytes": MAX_EXECUTABLE_BYTES,
                   "expected_wav_bytes": 44 + frames * 4},
        "invocation": {"argv": [], "returncode": None, "timed_out": False,
                       "stdout": None, "stderr": None},
        "renderer_metrics": None, "wav": None, "metric_comparison": None,
        "integrity_verified": False, "error": None,
    }
    # mkdir is the exclusive ownership operation. Never catch/reuse an existing dir.
    directory.mkdir()
    _manifest_write(directory, manifest)
    stage = "copy_inputs"
    try:
        _write_new(directory / "profile.json", raw_profile)
        _write_new(directory / "profile.b3p", compiled)
        if raw_events is not None:
            _write_new(directory / "events.txt", raw_events)
        argv = [str(renderer_path), "--profile", str(directory / "profile.b3p"),
                "--output", str(directory / "render.wav"), "--frames", str(frames),
                "--sample-rate", str(sample_rate), "--block-size", str(block_size),
                "--seed", str(seed), "--drawbars", drawbars,
                "--pedal-drawbars", pedal_drawbars,
                "--contacts", contacts, "--percussion", percussion,
                "--percussion-volume", percussion_volume, "--percussion-decay", percussion_decay,
                "--fail-on-clip"]
        argv += ["--events", str(directory / "events.txt")] if events is not None else ["--note", str(note)]
        manifest["invocation"]["argv"] = argv
        stage = "renderer"
        result, stdout, stderr = _invoke(argv, directory, timeout_seconds)
        manifest["invocation"].update(result)
        for name, raw in (("stdout", stdout), ("stderr", stderr)):
            filename = f"renderer.{name}.txt"
            _write_new(directory / filename, raw)
            manifest["invocation"][name] = _artifact(filename, raw)
        if stdout.strip():
            try:
                if len(stdout) > MAX_METRICS_BYTES:
                    raise FixtureError("renderer metrics JSON exceeds 16 KiB")
                metrics = _json(stdout)
                if (type(metrics) is not dict or len(metrics) > 64 or any(
                        type(value) not in (str, int, float, bool, type(None))
                        for value in metrics.values())):
                    raise FixtureError("renderer JSON must be a flat object of at most 64 scalar fields")
                manifest["renderer_metrics"] = metrics
            except FixtureError as error:
                manifest["metrics_parse_error"] = str(error)
        stage = "integrity"
        after = sha256_file(renderer_path, MAX_EXECUTABLE_BYTES)
        manifest["renderer"]["sha256_after"] = after["sha256"]
        if after != renderer_hash:
            raise FixtureError("renderer executable changed during the run")
        checks = [(authoring_path, profile_hash, profile_compiler.MAX_INPUT_BYTES),
                  (directory / "profile.json", profile_hash, profile_compiler.MAX_INPUT_BYTES),
                  (directory / "profile.b3p", _artifact("", compiled), profile_compiler.MAX_OUTPUT_BYTES)]
        if raw_events is not None:
            checks += [(event_path, manifest["inputs"]["events"], MAX_SCORE_BYTES),
                       (directory / "events.txt", manifest["inputs"]["events"], MAX_SCORE_BYTES)]
        checks += [(Path(record["path"]), record, MAX_TOOL_BYTES) for record in tools_identity.values()]
        for path, expected, limit in checks:
            actual = sha256_file(path, limit)
            if any(actual[key] != expected[key] for key in ("sha256", "size_bytes")):
                raise FixtureError(f"input/tool bytes changed during the run: {path}")
        manifest["integrity_verified"] = True
        stage = "renderer"
        if result["timed_out"]:
            raise FixtureError(f"renderer exceeded {timeout_seconds} second timeout")
        if result["stdout_truncated"] or result["stderr_truncated"] or result["capture_incomplete"] or result["capture_errors"]:
            raise FixtureError("renderer log limit exceeded or output capture incomplete")
        if result["returncode"] != 0:
            raise FixtureError(f"renderer exited with status {result['returncode']}; inspect retained stderr")
        stage = "metrics"
        if manifest["renderer_metrics"] is None:
            raise FixtureError("renderer did not emit a valid JSON metrics object")
        _validate_metrics(manifest["renderer_metrics"], parameters, canonical_digest)
        stage = "wav"
        wav = inspect_wav(directory / "render.wav", frames=frames, sample_rate=sample_rate)
        peak_difference = abs(wav["pcm_peak"] - manifest["renderer_metrics"]["peak"])
        rms_difference = abs(wav["pcm_rms"] - manifest["renderer_metrics"]["rms"])
        within = max(peak_difference, rms_difference) <= PCM_ERROR_BOUND + 1e-12
        manifest["metric_comparison"] = {
            "float_metric_domain": "engine_pre_quantization", "pcm_metric_domain": "quantized_pcm16",
            "absolute_error_bound": PCM_ERROR_BOUND, "numeric_tolerance": 1e-12,
            "peak_absolute_difference": peak_difference, "rms_absolute_difference": rms_difference,
            "within_quantization_bound": within,
            "basis": "one PCM16 step covers rounding and positive-rail saturation; zero clipped frames required",
        }
        if not within:
            raise FixtureError("WAV and float metrics differ beyond the PCM16 quantization bound")
        manifest["wav"] = wav
        manifest["status"] = "succeeded"
    except Exception as error:
        manifest["status"] = "failed"
        manifest["error"] = {"stage": stage, "message": str(error)}
    finally:
        manifest["finished_at_utc"] = _utc()
        _manifest_write(directory, manifest)
    return manifest


class _Once(argparse.Action):
    def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace,
                 values: Any, option_string: str | None = None) -> None:
        seen = getattr(namespace, "_seen", set())
        if self.dest in seen:
            parser.error(f"duplicate argument: {option_string}")
        seen.add(self.dest)
        namespace._seen = seen
        setattr(namespace, self.dest, values)


def _cli_integer(token: str) -> int:
    try:
        return _unsigned(token)
    except FixtureError as error:
        raise argparse.ArgumentTypeError(str(error)) from error


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--renderer", required=True, action=_Once)
    parser.add_argument("--profile-json", default=str(DEFAULT_PROFILE), action=_Once)
    parser.add_argument("--output-dir", required=True, action=_Once)
    score = parser.add_mutually_exclusive_group()
    score.add_argument("--events", action=_Once)
    score.add_argument("--note", type=_cli_integer, action=_Once)
    for name, default in (("frames", None), ("sample-rate", 48000), ("block-size", 64),
                          ("seed", 0), ("timeout-seconds", DEFAULT_TIMEOUT_SECONDS)):
        parser.add_argument(f"--{name}", type=_cli_integer, default=default, action=_Once)
    parser.add_argument("--drawbars", default="888000000", action=_Once)
    parser.add_argument("--pedal-drawbars", default="00", action=_Once)
    for name, default, choices in (
            ("contacts", "ideal", ("ideal", "nominal")),
            ("percussion", "off", ("off", "second", "third")),
            ("percussion-volume", "normal", ("normal", "soft")),
            ("percussion-decay", "slow", ("slow", "fast"))):
        parser.add_argument(f"--{name}", default=default, choices=choices, action=_Once)
    options = vars(parser.parse_args(argv))
    options.pop("_seen", None)
    try:
        manifest = run_fixture(**options)
    except (OSError, ValueError, RuntimeError) as error:
        print(f"render_fixture: {error}", file=sys.stderr)
        return 1
    if manifest["status"] != "succeeded":
        print(f"render_fixture: failed: {manifest['error']}; evidence retained in {options['output_dir']}",
              file=sys.stderr)
        return 1
    print(json.dumps({"status": manifest["status"], "evidence_scope": manifest["evidence_scope"],
                      "manifest": str(Path(options["output_dir"]).absolute() / "manifest.json")},
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
