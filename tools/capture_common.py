#!/usr/bin/env python3
"""Bounded JSON input and non-replacing output for offline capture tools.

These primitives establish byte/JSON properties, never physical provenance.
Relative artifact confinement belongs to each caller's declared root contract.
Keep source files quiescent: portable checks are not a concurrent-filesystem sandbox.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import stat
import tempfile


class DataError(ValueError):
    """Malformed, changing, unsupported or unsafe offline data."""


def _regular(path: Path):
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or (
        getattr(info, "st_file_attributes", 0)
        & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    ):
        raise DataError("input must be a regular nonsymlink, non-reparse file")
    return info


def _stamp(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


def read_bytes(path: str | Path, *, max_bytes: int = 1048576) -> bytes:
    """Read one bounded regular file and detect observed identity/content changes."""
    if type(max_bytes) is not int or not 1 <= max_bytes <= 16777216:
        raise DataError("max_bytes must be an integer in 1..16777216")
    try:
        selected = Path(path)
        before_path = _regular(selected)
        if before_path.st_size > max_bytes:
            raise DataError("input exceeds byte limit")
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
        flags |= getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(selected, flags)
        try:
            stream = os.fdopen(descriptor, "rb")
        except BaseException:
            os.close(descriptor)
            raise
        with stream:
            before_fd = os.fstat(stream.fileno())
            if not stat.S_ISREG(before_fd.st_mode) or before_fd.st_size > max_bytes:
                raise DataError("opened input is not a bounded regular file")
            if os.name == "posix" and (before_fd.st_dev, before_fd.st_ino) != (
                before_path.st_dev, before_path.st_ino
            ):
                raise DataError("input replaced while opening")
            payload = stream.read(max_bytes + 1)
            if len(payload) > max_bytes or len(payload) != before_fd.st_size:
                raise DataError("input size changed or exceeds byte limit")
            if _stamp(before_fd) != _stamp(os.fstat(stream.fileno())):
                raise DataError("input changed while reading")
        if _stamp(before_path) != _stamp(_regular(selected)):
            raise DataError("input path changed while reading")
        return payload
    except DataError:
        raise
    except (OSError, ValueError, TypeError, OverflowError) as exc:
        raise DataError(f"cannot read input: {exc}") from exc


def validate_json_value(value, *, max_nodes=65536, max_depth=32,
                        max_number=1e12) -> None:
    """Bound direct values as well as decoded JSON; reject non-JSON Python types."""
    if (type(max_nodes) is not int or not 1 <= max_nodes <= 1048576
            or type(max_depth) is not int or not 0 <= max_depth <= 128
            or type(max_number) not in (int, float)
            or not 0 < max_number <= 1e100 or not math.isfinite(max_number)):
        raise DataError("invalid JSON resource limits")
    pending = [(value, 0)]
    count = 0
    while pending:
        item, depth = pending.pop()
        count += 1
        if count > max_nodes:
            raise DataError("JSON value-node limit exceeded")
        if type(item) in (dict, list):
            if depth > max_depth or count + len(pending) + len(item) > max_nodes:
                raise DataError("JSON nesting or value-node limit exceeded")
            if type(item) is dict:
                for key in item:
                    if type(key) is not str:
                        raise DataError("JSON object keys must be strings")
                    try:
                        key.encode("utf-8")
                    except UnicodeError as exc:
                        raise DataError("invalid Unicode in JSON key") from exc
                children = item.values()
            else:
                children = item
            pending.extend((child, depth + 1) for child in children)
        elif type(item) is str:
            try:
                item.encode("utf-8")
            except UnicodeError as exc:
                raise DataError("invalid Unicode in JSON string") from exc
        elif type(item) in (int, float):
            if not -max_number <= item <= max_number or not math.isfinite(item):
                raise DataError("JSON number is nonfinite or outside the declared bound")
        elif item is not None and type(item) is not bool:
            raise DataError("unsupported non-JSON value type")


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise DataError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def _number(token, integer):
    if len(token) > 64:
        raise DataError("numeric token exceeds 64 characters")
    value = int(token) if integer else float(token)
    if not -1e100 <= value <= 1e100 or not math.isfinite(value):
        raise DataError("nonfinite or excessive JSON number")
    return value


def _constant(token):
    raise DataError(f"nonfinite JSON constant: {token}")


def parse_json_bytes(payload: bytes, *, max_bytes=1048576, max_nodes=65536,
                     max_depth=32, max_number=1e12):
    """Parse bounded exact UTF-8 bytes; callers retain those bytes for identity."""
    if (type(payload) is not bytes or type(max_bytes) is not int
            or not 1 <= max_bytes <= 16777216 or len(payload) > max_bytes):
        raise DataError("JSON bytes or byte limit are invalid")
    try:
        value = json.loads(payload.decode("utf-8"), object_pairs_hook=_pairs,
                           parse_int=lambda token: _number(token, True),
                           parse_float=lambda token: _number(token, False),
                           parse_constant=_constant)
    except DataError:
        raise
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise DataError(f"invalid UTF-8 JSON: {exc}") from exc
    validate_json_value(value, max_nodes=max_nodes, max_depth=max_depth,
                        max_number=max_number)
    return value


def read_json(path: str | Path, *, max_bytes=1048576, max_nodes=65536,
              max_depth=32, max_number=1e12):
    """Return (value, {sha256, size_bytes}) for exactly the bytes parsed."""
    payload = read_bytes(path, max_bytes=max_bytes)
    value = parse_json_bytes(payload, max_bytes=max_bytes, max_nodes=max_nodes,
                             max_depth=max_depth, max_number=max_number)
    return value, {"sha256": hashlib.sha256(payload).hexdigest(),
                   "size_bytes": len(payload)}


def canonical_json_bytes(value) -> bytes:
    """Stable UTF-8 JSON for report artifacts; this is not a signature format."""
    validate_json_value(value, max_nodes=1048576, max_depth=128, max_number=1e100)
    try:
        return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False,
                           allow_nan=False) + "\n").encode("utf-8")
    except (ValueError, TypeError, UnicodeError, RecursionError) as exc:
        raise DataError(f"cannot serialize JSON: {exc}") from exc


def write_json_new(path: str | Path, value) -> dict:
    """Publish one complete new JSON file, preserving any existing destination.

    Uses a same-directory temporary file and a non-replacing hard-link operation.
    The parent must exist and the filesystem must support hard links. No directory
    creation or existing-file replacement is performed. Crash recovery is separate.
    """
    payload = canonical_json_bytes(value)
    temporary = None
    primary_error = None
    published = False
    try:
        target = Path(path)
        descriptor, name = tempfile.mkstemp(prefix=".capture-json-", dir=target.parent)
        temporary = Path(name)
        try:
            stream = os.fdopen(descriptor, "wb")
        except BaseException:
            os.close(descriptor)
            raise
        with stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, target)
        published = True
    except (OSError, ValueError, TypeError, OverflowError) as exc:
        primary_error = exc
    finally:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError as cleanup_error:
                if primary_error is not None:
                    raise DataError(
                        f"cannot publish new JSON file: {primary_error}; "
                        f"temporary cleanup also failed: {cleanup_error}"
                    ) from primary_error
                if published:
                    raise DataError(
                        "new JSON file was published and remains complete; "
                        f"temporary cleanup failed: {cleanup_error}"
                    ) from cleanup_error
                raise DataError(f"temporary cleanup failed: {cleanup_error}") from cleanup_error
    if primary_error is not None:
        raise DataError(f"cannot publish new JSON file: {primary_error}") from primary_error
    return {"sha256": hashlib.sha256(payload).hexdigest(), "size_bytes": len(payload)}
