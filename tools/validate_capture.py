#!/usr/bin/env python3
"""Validate the project's proposed v1 acquisition metadata, not physical truth.

Public API: load_capture(path), validate_capture(value), and the explicit
check_capture_files(value, base_dir). Rejections raise CaptureError. This stdlib
tool reads no audio headers and never turns byte integrity into calibration.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import stat
import sys


MAX_INPUT_BYTES = 64 * 1024
MAX_NODES = 4096
MAX_DEPTH = 16
MAX_TEXT = 2048
MAX_NUMBER = 1e12
MAX_FILES = 32
MAX_PARENTS = 16
MAX_FILE_BYTES = 256 * 1024 * 1024
MAX_TOTAL_FILE_BYTES = 512 * 1024 * 1024
CHUNK_BYTES = 64 * 1024
FORMATS = {"wav_pcm16", "wav_pcm24", "wav_pcm32", "wav_float32",
           "wav_float64", "flac_pcm16", "flac_pcm24", "raw_float32_le"}
BOUNDARY_UNITS = {
    "pickup_unloaded": "V/FS", "generator_loaded_terminal": "V/FS",
    "preamp_GG": "V/FS", "electrical_voltage": "V/FS",
    "electrical_current": "A/FS", "acoustic_microphone": "Pa/FS",
    "synthetic": None,
}
ID_RE = re.compile(r"[a-z][a-z0-9_-]{0,63}")
UTC_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]{1,6})?Z")
DEVICE_RE = re.compile(r"(?:con|prn|aux|nul|com[1-9]|lpt[1-9])", re.IGNORECASE)


class CaptureError(ValueError):
    """An invalid declaration or failed explicit artifact integrity check."""


def _require(condition: bool, label: str, message: str) -> None:
    if not condition:
        raise CaptureError(f"{label}: {message}")


def _keys(value: object, fields: set[str], label: str) -> None:
    _require(type(value) is dict and set(value) == fields, label,
             f"expected exactly these keys: {', '.join(sorted(fields))}")


def _text(value: object, label: str) -> str:
    _require(type(value) is str and 0 < len(value) <= MAX_TEXT and bool(value.strip()),
             label, f"expected nonblank text of at most {MAX_TEXT} characters")
    _require(not any(ord(char) < 32 or 127 <= ord(char) <= 159 for char in value),
             label, "control characters are forbidden")
    try:
        value.encode("utf-8")
    except UnicodeError as error:
        raise CaptureError(f"{label}: unpaired Unicode surrogate") from error
    return value


def _id(value: object, label: str) -> str:
    _require(type(value) is str and ID_RE.fullmatch(value) is not None,
             label, "expected ID matching [a-z][a-z0-9_-]{0,63}")
    return value


def _literal(value: object, expected: object, label: str) -> None:
    _require(type(value) is type(expected) and value == expected,
             label, f"expected {expected!r}")


def _enum(value: object, choices: set[str], label: str) -> str:
    _require(type(value) is str and value in choices, label,
             f"expected one of {', '.join(sorted(choices))}")
    return value


def _integer(value: object, low: int, high: int, label: str) -> int:
    _require(type(value) is int and low <= value <= high, label,
             f"expected integer in {low}..{high}")
    return value


def _number(value: object, label: str, *, positive: bool = False,
            high: float = MAX_NUMBER) -> int | float:
    _require(type(value) in (int, float) and 0 <= value <= high and math.isfinite(value),
             label, f"expected finite nonnegative number <= {high}")
    _require(not positive or value > 0, label, "expected a positive number")
    return value


def _array(value: object, limit: int, label: str) -> list:
    _require(type(value) is list and len(value) <= limit, label,
             f"expected array of at most {limit} entries")
    return value


def _known(value: object, check, label: str):
    _keys(value, {"value", "unknown_reason"}, label)
    if value["value"] is None:
        _text(value["unknown_reason"], f"{label}.unknown_reason")
    else:
        check(value["value"], f"{label}.value")
        _literal(value["unknown_reason"], None, f"{label}.unknown_reason")
    return value["value"]


def _utc(value: object, label: str) -> None:
    _require(type(value) is str and UTC_RE.fullmatch(value) is not None,
             label, "expected UTC YYYY-MM-DDTHH:MM:SS[.ffffff]Z")
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as error:
        raise CaptureError(f"{label}: invalid calendar timestamp") from error


def _guard(value: object) -> None:
    """Bound direct API values as well as parsed JSON, without recursion."""
    pending = [(value, 0)]
    nodes = 0
    while pending:
        item, depth = pending.pop()
        nodes += 1
        _require(nodes <= MAX_NODES, "capture", "too many JSON value nodes")
        if type(item) in (dict, list):
            _require(depth <= MAX_DEPTH and len(item) <= MAX_NODES,
                     "capture", "JSON nesting or container size exceeds limit")
            _require(nodes + len(pending) + len(item) <= MAX_NODES,
                     "capture", "too many JSON value nodes")
            if type(item) is dict:
                for key in item:
                    _text(key, "JSON key")
                children = item.values()
            else:
                children = item
            pending.extend((child, depth + 1) for child in children)
        elif type(item) is str:
            _text(item, "JSON string")
        elif type(item) in (int, float):
            _require(-MAX_NUMBER <= item <= MAX_NUMBER and math.isfinite(item),
                     "JSON number", "must be finite with magnitude <= 1e12")
        else:
            _require(item is None or type(item) is bool,
                     "capture", "unsupported non-JSON value type")


def _calibration(value: object, unit: str | None, record: dict, label: str,
                 *, clock: bool = False) -> None:
    _keys(value, {"status", "value", "unit", "standard_uncertainty", "evidence",
                  "unknown_reason"}, label)
    status = _enum(value["status"], {"calibrated", "uncalibrated", "not_applicable"},
                   f"{label}.status")
    _literal(value["unit"], unit, f"{label}.unit")
    if record["capture_kind"] == "synthetic":
        _literal(status, "not_applicable", f"{label}.status")
    else:
        _require(status != "not_applicable", label,
                 "hardware calibration must be calibrated or explicitly uncalibrated")
    if status == "calibrated":
        _require(record["status"] == "recorded" and unit is not None, label,
                 "calibrated declaration needs recorded hardware and a known boundary/unit")
        _number(value["value"], f"{label}.value", positive=True,
                high=768000 if clock else MAX_NUMBER)
        _number(value["standard_uncertainty"], f"{label}.standard_uncertainty")
        _text(value["evidence"], f"{label}.evidence")
        _literal(value["unknown_reason"], None, f"{label}.unknown_reason")
    else:
        for key in ("value", "standard_uncertainty", "evidence"):
            _literal(value[key], None, f"{label}.{key}")
        _text(value["unknown_reason"], f"{label}.unknown_reason")


def _artifact_path(value: object, label: str) -> str:
    _text(value, label)
    _require(len(value) <= 240, label, "path exceeds 240 characters")
    parts = value.split("/")
    _require(1 <= len(parts) <= 8, label, "path exceeds eight components")
    for part in parts:
        _require(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", part) is not None
                 and not part.endswith(".")
                 and DEVICE_RE.fullmatch(part.split(".", 1)[0]) is None,
                 label, "expected confined portable relative path without device names")
    return value


def _files(value: object, recorded: bool) -> None:
    files = _array(value, MAX_FILES, "files")
    if not recorded:
        _require(not files, "files", "planned records cannot declare acquired artifacts")
    by_id = {}
    paths = set()
    total = 0
    for index, item in enumerate(files):
        label = f"files[{index}]"
        _keys(item, {"file_id", "kind", "path", "size_bytes", "sha256", "parents",
                     "derivation"}, label)
        ident = _id(item["file_id"], f"{label}.file_id")
        _require(ident not in by_id, label, "duplicate file ID")
        by_id[ident] = item
        kind = _enum(item["kind"], {"raw", "derived", "support"}, f"{label}.kind")
        path = _artifact_path(item["path"], f"{label}.path").casefold()
        _require(path not in paths, label, "duplicate file path (case-insensitive)")
        paths.add(path)
        total += _integer(item["size_bytes"], 1, MAX_FILE_BYTES, f"{label}.size_bytes")
        _require(total <= MAX_TOTAL_FILE_BYTES, "files", "aggregate byte limit exceeded")
        _require(type(item["sha256"]) is str and
                 re.fullmatch(r"[0-9a-f]{64}", item["sha256"]) is not None,
                 f"{label}.sha256", "expected lowercase SHA-256")
        parents = _array(item["parents"], MAX_PARENTS, f"{label}.parents")
        for parent in parents:
            _id(parent, f"{label}.parents")
        _require(len(set(parents)) == len(parents), label, "duplicate parent reference")
        if kind == "derived":
            _require(bool(parents), label, "derived file needs a parent")
            _keys(item["derivation"], {"operation", "tool", "tool_version", "parameters"},
                  f"{label}.derivation")
            for key, text in item["derivation"].items():
                _text(text, f"{label}.derivation.{key}")
        else:
            _require(not parents, label, "raw/support files cannot declare parents")
            _literal(item["derivation"], None, f"{label}.derivation")
    _require(not recorded or any(item["kind"] == "raw" for item in files),
             "files", "recorded record needs at least one raw file")
    visiting, done = set(), {}

    def visit(ident: str) -> bool:
        _require(ident in by_id, "files.parents", f"unresolved parent {ident!r}")
        _require(ident not in visiting, "files.parents", "derivation cycle or self-reference")
        if ident in done:
            return done[ident]
        visiting.add(ident)
        item = by_id[ident]
        raw_ancestor = item["kind"] == "raw"
        for parent in item["parents"]:
            # Visit every branch, even after finding a raw ancestor.
            raw_ancestor = visit(parent) or raw_ancestor
        visiting.remove(ident)
        _require(item["kind"] != "derived" or raw_ancestor, "files.parents",
                 "derived file must reach a raw ancestor")
        done[ident] = raw_ancestor
        return raw_ancestor

    for ident in by_id:
        visit(ident)


def validate_capture(value: object) -> None:
    """Validate bounded exact fields and local semantics; never read artifacts."""
    _guard(value)
    _keys(value, {"schema_version", "contract_origin", "capture_id", "status",
                  "status_reason", "capture_kind", "specimen", "acquisition", "digital",
                  "physical_clock", "stimulus", "signal_path", "files", "partition", "rights"},
          "capture")
    _literal(value["schema_version"], 1, "schema_version")
    _literal(value["contract_origin"], "project-proposed-v1", "contract_origin")
    _id(value["capture_id"], "capture_id")
    status = _enum(value["status"], {"planned", "recorded"}, "status")
    kind = _enum(value["capture_kind"], {"hardware", "synthetic"}, "capture_kind")
    recorded = status == "recorded"
    if recorded:
        _literal(value["status_reason"], None, "status_reason")
    else:
        _text(value["status_reason"], "status_reason")
    specimen = value["specimen"]
    _keys(specimen, {"specimen_id", "variant", "revision", "identity_evidence"}, "specimen")
    for key, entry in specimen.items():
        result = _known(entry, _id if key == "specimen_id" else _text, f"specimen.{key}")
        if key == "specimen_id" and kind == "synthetic":
            _literal(result, None, "specimen.specimen_id.value")
    acquisition = value["acquisition"]
    _keys(acquisition, {"started_at_utc", "operator_id", "session_id"}, "acquisition")
    for key, entry in acquisition.items():
        result = _known(entry, _utc if key == "started_at_utc" else _id, f"acquisition.{key}")
        _require(not recorded or result is not None, f"acquisition.{key}",
                 "recorded capture requires a known declaration")
        if not recorded and key == "started_at_utc":
            _literal(result, None, f"acquisition.{key}.value")
    digital = value["digital"]
    _keys(digital, {"format", "sample_rate_hz", "channel_count", "channels"}, "digital")
    checks = {
        "format": lambda item, label: _enum(item, FORMATS, label),
        "sample_rate_hz": lambda item, label: _integer(item, 1, 768000, label),
        "channel_count": lambda item, label: _integer(item, 1, 16, label),
    }
    for key, check in checks.items():
        result = _known(digital[key], check, f"digital.{key}")
        _require(not recorded or result is not None, f"digital.{key}",
                 "recorded capture requires a known declaration")
    channels = _array(digital["channels"], 16, "digital.channels")
    count = digital["channel_count"]["value"]
    _require(len(channels) == (0 if count is None else count), "digital.channels",
             "channel list must agree with declared count; unknown count requires empty list")
    channel_ids = set()
    for index, channel in enumerate(channels):
        label = f"digital.channels[{index}]"
        _keys(channel, {"channel_id", "index", "boundary", "port_reference", "calibration"}, label)
        ident = _id(channel["channel_id"], f"{label}.channel_id")
        _require(ident not in channel_ids, label, "duplicate channel ID")
        channel_ids.add(ident)
        _literal(channel["index"], index, f"{label}.index")
        boundary = _known(channel["boundary"],
                          lambda item, path: _enum(item, set(BOUNDARY_UNITS), path),
                          f"{label}.boundary")
        _require((kind == "synthetic" and boundary == "synthetic") or
                 (kind == "hardware" and boundary != "synthetic"),
                 f"{label}.boundary", "boundary must agree with hardware/synthetic capture kind")
        _known(channel["port_reference"], _text, f"{label}.port_reference")
        _calibration(channel["calibration"], BOUNDARY_UNITS.get(boundary), value,
                     f"{label}.calibration")
    _calibration(value["physical_clock"], "Hz" if kind == "hardware" else None,
                 value, "physical_clock", clock=True)
    for name, fields in (("stimulus", {"description", "controls", "conditions", "synchronization"}),
                         ("signal_path", {"description", "bypass", "loading"})):
        _keys(value[name], fields, name)
        for key, entry in value[name].items():
            _known(entry, _text, f"{name}.{key}")
    _known(value["rights"], _text, "rights")
    partition = value["partition"]
    _keys(partition, {"role", "group_id", "rationale"}, "partition")
    role = _enum(partition["role"], {"fit", "held_out", "unassigned"}, "partition.role")
    group = _known(partition["group_id"], _id, "partition.group_id")
    _require(not recorded and role == "unassigned" or group is not None,
             "partition.group_id", "recorded or assigned-role record needs a known group ID")
    _text(partition["rationale"], "partition.rationale")
    _files(value["files"], recorded)


def _pairs(items: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in items:
        _require(key not in result, "JSON", f"duplicate key {key!r}")
        result[key] = value
    return result


def _parse_number(token: str, integer: bool):
    _require(len(token) <= 64, "JSON", "numeric token exceeds 64 characters")
    value = int(token) if integer else float(token)
    _require(-MAX_NUMBER <= value <= MAX_NUMBER and math.isfinite(value),
             "JSON", "number must be finite with magnitude <= 1e12")
    return value


def _constant(token: str) -> None:
    raise CaptureError(f"JSON: forbidden nonfinite constant {token}")


def load_capture(path: str | Path) -> dict:
    """Read <=64 KiB of strict UTF-8 JSON and validate, without artifact access."""
    try:
        path = Path(path)
        _require(stat.S_ISREG(path.lstat().st_mode), "JSON", "manifest must be a regular nonsymlink file")
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NONBLOCK", 0)
        flags |= getattr(os, "O_NOFOLLOW", 0)
        with os.fdopen(os.open(path, flags), "rb") as source:
            _require(stat.S_ISREG(os.fstat(source.fileno()).st_mode), "JSON", "manifest is not regular")
            payload = source.read(MAX_INPUT_BYTES + 1)
        _require(len(payload) <= MAX_INPUT_BYTES, "JSON", "input exceeds 65536 bytes")
        value = json.loads(payload.decode("utf-8"), object_pairs_hook=_pairs,
                           parse_int=lambda token: _parse_number(token, True),
                           parse_float=lambda token: _parse_number(token, False),
                           parse_constant=_constant)
    except CaptureError:
        raise
    except (OSError, UnicodeError, ValueError, RecursionError) as error:
        raise CaptureError(f"cannot load capture {path}: {error}") from error
    validate_capture(value)
    return value


def _snapshot(path: Path, *, directory: bool) -> os.stat_result:
    info = path.lstat()
    _require(stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode),
             str(path), "expected a nonsymlink directory" if directory else "expected a regular nonsymlink file")
    _require(not (getattr(info, "st_file_attributes", 0) &
                  getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)),
             str(path), "Windows reparse points are not permitted in artifact paths")
    return info


def _identity(info: os.stat_result) -> tuple:
    return info.st_dev, info.st_ino


def _stable(info: os.stat_result) -> tuple:
    return info.st_dev, info.st_ino, info.st_mode, info.st_size, info.st_mtime_ns, info.st_ctime_ns


def _open_artifact(root: Path, parts: list[str], directories: list[tuple[Path, os.stat_result]]) -> int:
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NONBLOCK", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    if os.name != "posix" or os.open not in os.supports_dir_fd:
        return os.open(root.joinpath(*parts), flags)
    # On POSIX, bind each parent directory by descriptor; do not follow an
    # intermediate symlink introduced between the path checks and the open.
    directory_flags = flags | os.O_DIRECTORY
    descriptor = os.open(root, directory_flags)
    try:
        for index, (_, expected) in enumerate(directories):
            _require(_identity(os.fstat(descriptor)) == _identity(expected),
                     str(root), "artifact directory replaced while opening")
            if index < len(parts) - 1:
                child = os.open(parts[index], directory_flags, dir_fd=descriptor)
                os.close(descriptor)
                descriptor = child
        return os.open(parts[-1], flags, dir_fd=descriptor)
    finally:
        os.close(descriptor)


def check_capture_files(value: object, base_dir: str | Path) -> dict:
    """Explicitly stream recorded artifacts; verify bytes, not audio or provenance."""
    validate_capture(value)
    _require(value["status"] == "recorded", "files", "file checking requires a recorded record")
    checked_bytes = 0
    seen_files = set()
    try:
        selected_root = Path(os.path.abspath(base_dir))
        selected_info = _snapshot(selected_root, directory=True)
        # Canonicalize ancestors above the chosen nonsymlink root. macOS /var,
        # for example, is commonly an OS alias for /private/var.
        root = selected_root.resolve(strict=True)
        _require(_identity(selected_info) == _identity(_snapshot(root, directory=True)),
                 str(selected_root), "artifact root changed while resolving")
        for item in value["files"]:
            parts = item["path"].split("/")
            target = root.joinpath(*parts)
            chain = [root]
            parent = root
            for component in parts[:-1]:
                parent /= component
                chain.append(parent)
            before_dirs = [(directory, _snapshot(directory, directory=True)) for directory in chain]
            before_path = _snapshot(target, directory=False)
            _require(before_path.st_size == item["size_bytes"], item["path"], "declared size mismatch")
            with os.fdopen(_open_artifact(root, parts, before_dirs), "rb") as source:
                before_fd = os.fstat(source.fileno())
                _require(stat.S_ISREG(before_fd.st_mode) and before_fd.st_size == item["size_bytes"],
                         item["path"], "opened file type/size mismatch")
                # Cross-API timestamps are not portable. Bind dev/inode on POSIX;
                # compare timestamps only within the same API before/after.
                if os.name == "posix":
                    _require(_identity(before_fd) == _identity(before_path), item["path"], "file replaced while opening")
                identity_info = before_fd if before_fd.st_ino else before_path
                _require(bool(identity_info.st_ino), item["path"],
                         "file identity unavailable; cannot exclude hardlink aliases")
                identity = _identity(identity_info)
                _require(identity not in seen_files, item["path"], "hardlink alias duplicates a file identity")
                seen_files.add(identity)
                digest = hashlib.sha256()
                count = 0
                while count <= item["size_bytes"]:
                    block = source.read(min(CHUNK_BYTES, item["size_bytes"] + 1 - count))
                    if not block:
                        break
                    count += len(block)
                    digest.update(block)
                _require(count == item["size_bytes"], item["path"], "stream size mismatch")
                _require(_stable(before_fd) == _stable(os.fstat(source.fileno())),
                         item["path"], "file changed during hashing")
            _require(_stable(before_path) == _stable(_snapshot(target, directory=False)),
                     item["path"], "file changed during hashing")
            for directory, before in before_dirs:
                after = _snapshot(directory, directory=True)
                _require(_identity(before) == _identity(after), str(directory), "directory replaced during hashing")
            _require(digest.hexdigest() == item["sha256"], item["path"], "SHA-256 mismatch")
            checked_bytes += count
        _require(_identity(selected_info) == _identity(_snapshot(selected_root, directory=True)),
                 str(selected_root), "selected artifact root changed during hashing")
    except CaptureError:
        raise
    except (OSError, ValueError, OverflowError) as error:
        raise CaptureError(f"cannot check capture files: {error}") from error
    return {"capture_id": value["capture_id"], "status": "verified", "files_checked": len(value["files"]),
            "bytes_checked": checked_bytes, "scope": "declared-byte-integrity-only",
            "authenticity": "not_established", "calibration": "not_established",
            "physical_fidelity": "not_established"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--input", required=True, type=Path, help="capture metadata JSON")
    parser.add_argument("--check-files", action="store_true", help="explicitly verify recorded artifact bytes")
    parser.add_argument("--artifact-root", type=Path, help="artifact root (default: manifest parent)")
    args = parser.parse_args(argv)
    if args.artifact_root is not None and not args.check_files:
        parser.error("--artifact-root requires --check-files")
    try:
        value = load_capture(args.input)
        report = check_capture_files(value, args.artifact_root or args.input.parent) if args.check_files else None
    except CaptureError as error:
        print(f"capture error: {error}", file=sys.stderr)
        return 1
    print(json.dumps({"capture_id": value["capture_id"], "record_status": value["status"],
                      "structural_validation": "pass", "file_check": report,
                      "authenticity": "not_established", "calibration": "not_established",
                      "physical_fidelity": "not_established"}, sort_keys=True, allow_nan=False))
    return 0


# Keep this executable boundary local so the original validator remains a
# standalone stdlib-only script, without a capture_common runtime dependency.
def _cli_exit(entrypoint, diagnostic) -> int:
    """Finish a real CLI's buffered delivery before choosing its process status.

    Call only at the executable boundary, not around imported API operations.
    A failed original standard stream is closed so interpreter finalization
    cannot replace the intended exit with 120 by retrying its buffered bytes.
    Custom streams and healthy original streams remain owned by their caller.
    """
    originals = {name: (getattr(sys, name), getattr(sys, f"__{name}__"))
                 for name in ("stdout", "stderr")}
    cleanup_failures = []

    def retire(name, stream, primary):
        selected, original = originals[name]
        if (stream is not selected or stream is not original
                or stream is not getattr(sys, name)
                or stream is not getattr(sys, f"__{name}__")
                or type(stream) is not io.TextIOWrapper):
            return
        try:
            if stream.fileno() != {"stdout": 1, "stderr": 2}[name]:
                return
            try:
                stream.close()
            except OSError as cleanup:
                # TextIOWrapper still closes its buffer when its flush repeats
                # the same pipe failure. Keep a distinct cleanup failure visible.
                if not stream.closed or cleanup.errno != primary.errno:
                    cleanup_failures.append(f"{name} close failed: {cleanup}")
            if not stream.closed:
                cleanup_failures.append(f"{name} remained open after delivery failure")
        except OSError as cleanup:
            cleanup_failures.append(f"{name} retirement failed: {cleanup}")

    caught = None
    try:
        status = entrypoint()
    except SystemExit as error:
        if error.code is not None and type(error.code) is not int:
            raise
        status = 0 if error.code is None else error.code
    except OSError as error:
        # Expected input errors are handled by each CLI before this boundary.
        # Do not intercept cancellation or unrelated programming exceptions.
        caught = error
        status = 1

    failures = []
    for name in ("stdout", "stderr"):
        stream = getattr(sys, name)
        if stream is None:
            continue
        try:
            stream.flush()
        except OSError as error:
            failures.append((name, error))
            retire(name, stream, error)
    if caught is None and not failures:
        return status

    error = caught if caught is not None else failures[0][1]
    # A CLI that already returned 1 has emitted its contextual diagnostic.
    # Do not duplicate it merely because final flushing observes the same error.
    if not any(name == "stderr" for name, _ in failures) and (
            caught is not None or status != 1 or cleanup_failures):
        message = str(error)
        if cleanup_failures:
            message += "; " + "; ".join(cleanup_failures)
        try:
            diagnostic(message)
            sys.stderr.flush()
        except OSError as delivery:
            retire("stderr", sys.stderr, delivery)
    return 1


if __name__ == "__main__":
    raise SystemExit(_cli_exit(main, lambda message: print(
        f"capture error: standard-stream delivery failed: {message}", file=sys.stderr)))
