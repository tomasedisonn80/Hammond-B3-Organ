#!/usr/bin/env python3
"""Compile the corroborated pedal map into a deterministic, build-only C++ table.

This is an offline authoring operation, not an audio callback or a physical
voicing model. All four inputs are read once within explicit byte bounds. The
map's original provenance is preserved alongside the later documentary factory
comparison. No formula supplies the independent CSV cells.

Public API: compile_pedal_routing(input_path, reference_path, review_a_path,
review_b_path) -> str, write_compiled_header(output, text, inputs). Failures raise
PedalCompileError. Rejected inputs and publication failures preserve prior output;
a later CLI summary-delivery failure does not roll back a published header.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import tempfile

import validate_factory_reference as factory
import validate_pedal_map as pedal_map


MAX_MAP_BYTES = pedal_map.MAX_INPUT_BYTES
MAX_REFERENCE_BYTES = factory.MAX_JSON_BYTES
MAX_REVIEW_BYTES = factory.MAX_CSV_BYTES
MAX_OUTPUT_BYTES = 64 * 1024
BUS_NAMES = ("Brown", "Red", "Orange", "Yellow")


class PedalCompileError(ValueError):
    """A bounded input, documentary comparison, or output-publication failure."""


def _read(path: Path, limit: int) -> bytes:
    """Read a stable regular file without an unbounded read or FIFO wait."""
    try:
        if not stat.S_ISREG(path.stat().st_mode):
            raise PedalCompileError(f"{path}: must be a regular file")
        with path.open("rb") as source:
            before = os.fstat(source.fileno())
            if not stat.S_ISREG(before.st_mode) or before.st_size > limit:
                raise PedalCompileError(f"{path}: must be a regular file of at most {limit} bytes")
            payload = source.read(limit + 1)
            after = os.fstat(source.fileno())
        identity = lambda value: (value.st_dev, value.st_ino, value.st_size,
                                  value.st_mtime_ns, value.st_ctime_ns)
        if identity(before) != identity(after) or len(payload) != before.st_size:
            raise PedalCompileError(f"{path}: file changed during read")
        if len(payload) > limit:
            raise PedalCompileError(f"{path}: exceeds {limit} byte limit")
        return payload
    except OSError as error:
        raise PedalCompileError(f"{path}: cannot read: {error}") from error


def _unique(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise PedalCompileError(f"JSON: duplicate object name {key!r}")
        result[key] = value
    return result


def _reject_number(token: str) -> None:
    raise PedalCompileError(f"JSON: non-integer or nonfinite token {token!r} is forbidden")


def _json(payload: bytes) -> object:
    try:
        return json.loads(payload.decode("utf-8"), object_pairs_hook=_unique,
                          parse_constant=_reject_number, parse_float=_reject_number)
    except PedalCompileError:
        raise
    except (UnicodeError, ValueError, RecursionError) as error:
        raise PedalCompileError(f"invalid UTF-8 JSON: {error}") from error


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _check_bytes(payload: bytes, expected: dict, label: str) -> str:
    if len(payload) != expected["bytes"]:
        raise PedalCompileError(f"{label}: expected {expected['bytes']} raw bytes, got {len(payload)}")
    digest = _sha256(payload)
    if digest != expected.get("sha256", expected.get("raw_sha256")):
        raise PedalCompileError(f"{label}: raw SHA-256 disagrees with frozen factory comparison")
    return digest


def compile_pedal_routing(input_path: str | Path, reference_path: str | Path,
                          review_a_path: str | Path, review_b_path: str | Path) -> str:
    """Validate every source and return an explicit 200-position native table.

    Map and CSV raw bytes must match the immutable v1 comparison. JSON object
    order in the reference manifest may vary; its exact semantic contract is
    still enforced and its actual raw digest is retained separately.
    """
    map_bytes = _read(Path(input_path), MAX_MAP_BYTES)
    reference_bytes = _read(Path(reference_path), MAX_REFERENCE_BYTES)
    review_bytes = (_read(Path(review_a_path), MAX_REVIEW_BYTES),
                    _read(Path(review_b_path), MAX_REVIEW_BYTES))
    data = _json(map_bytes)
    reference = _json(reference_bytes)
    try:
        pedal_map.validate_pedal_map(data)
        factory.validate_manifest(reference)
        readings = tuple(factory.parse_transcription(payload, "pedal")
                         for payload in review_bytes)
    except (pedal_map.PedalMapError, factory.FactoryReferenceError) as error:
        raise PedalCompileError(str(error)) from error

    # Compare all retained CSV cells explicitly, before checking raw identities,
    # to preserve useful location diagnostics for a changed documentary reading.
    for label, reading in zip(("A", "B"), readings):
        for row_index, (row, expected) in enumerate(zip(data["rows"], reading), 1):
            for column, (source, recorded) in enumerate(zip(row["sources"], expected), 1):
                if source != recorded or type(source) is not type(recorded):
                    raise PedalCompileError(
                        f"review {label}: pedal {row_index}/c{column}: "
                        f"map source {source!r} disagrees with CSV {recorded!r}")

    target = reference["targets"]["pedal"]
    map_raw = _check_bytes(map_bytes, target, "pedal map")
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=False, allow_nan=False).encode("utf-8")
    map_canonical = _sha256(canonical)
    if map_canonical != target["canonical_sha256"]:
        raise PedalCompileError("pedal map: canonical SHA-256 disagrees with factory comparison")
    review_hashes = tuple(_check_bytes(payload, record["pedal"], f"review {record['review']}")
                          for payload, record in zip(review_bytes, reference["readings"]))

    identifiers = (
        ("kPedalMapId", data["map_id"]),
        ("kPedalMapRawSha256", map_raw),
        ("kPedalMapCanonicalSha256", map_canonical),
        ("kFactoryComparisonId", reference["reference_id"]),
        ("kFactoryComparisonRawSha256", _sha256(reference_bytes)),
        ("kPedalReviewASha256", review_hashes[0]),
        ("kPedalReviewBSha256", review_hashes[1]),
    )
    lines = [
        "// Generated by compile_pedal_routing.py. Do not edit.",
        "// Documentary routing only; no measured voicing, weights or MIDI mapping.",
        "#pragma once", "", '#include "hammond/PedalRouting.h"',
        "#include <string_view>", "", "namespace hammond::generated {", "",
    ]
    for name, value in identifiers:
        lines.append(f"inline constexpr std::string_view {name} = {json.dumps(value)};")
    lines.extend(("", "inline constexpr PedalRouteDefinition kPedalRoutes{{"))
    for row in data["rows"]:
        pedal = row["pedal_id"]
        for column, source in enumerate(row["sources"]):
            tone = "std::nullopt" if source is None else f"ToneId{{{source}}}"
            lines.append(f"    PedalRoute{{PedalId{{{pedal}}}, {column}, "
                         f"PedalBus::{BUS_NAMES[column // 2]}, {tone}}},")
    lines.extend(("}};", "", "static_assert(kPedalRoutes.size() == kPedalCount * kPedalContactCount);",
                  "", "} // namespace hammond::generated", ""))
    result = "\n".join(lines)
    if len(result.encode("utf-8")) > MAX_OUTPUT_BYTES:
        raise PedalCompileError("generated header exceeds its fixed byte bound")
    return result


def write_compiled_header(output: str | Path, text: str,
                          inputs: tuple[str | Path, ...]) -> None:
    """Atomically publish validated generated bytes, never overwrite an input."""
    output = Path(output)
    try:
        destination = output.resolve()
        for input_path in inputs:
            source = Path(input_path)
            if destination == source.resolve() or (output.exists() and output.samefile(source)):
                raise PedalCompileError("output must not alias any compiler input")
        payload = text.encode("utf-8")
        if len(payload) > MAX_OUTPUT_BYTES:
            raise PedalCompileError("generated header exceeds its fixed byte bound")
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="wb", prefix=f".{output.name}.",
                                             suffix=".tmp", dir=output.parent,
                                             delete=False) as sink:
                temporary = Path(sink.name)
                sink.write(payload)
                sink.flush()
                os.fsync(sink.fileno())
            os.replace(temporary, output)
            temporary = None
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
    except (OSError, UnicodeError, RuntimeError) as error:
        raise PedalCompileError(f"cannot publish generated header {output}: {error}") from error


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--input", required=True, type=Path, help="unchanged documentary pedal-map JSON")
    parser.add_argument("--reference", required=True, type=Path, help="factory Table III comparison manifest")
    parser.add_argument("--review-a", required=True, type=Path, help="frozen review A pedal CSV")
    parser.add_argument("--review-b", required=True, type=Path, help="frozen review B pedal CSV")
    parser.add_argument("--output", required=True, type=Path, help="generated build-directory C++ header")
    args = parser.parse_args(argv)
    try:
        inputs = (args.input, args.reference, args.review_a, args.review_b)
        text = compile_pedal_routing(*inputs)
        write_compiled_header(args.output, text, inputs)
        print("compiled atlas-derived-b3-c3-pedal-v1: 200 positions, 195 connected, 5 disconnected")
        sys.stdout.flush()
    except (PedalCompileError, OSError) as error:
        print(f"pedal compile error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
