#!/usr/bin/env python3
"""Compile a synthetic source-leakage authoring JSON file to B3LEAKAGE1.

The frozen format and numerical rules are in docs/SOURCE_LEAKAGE_CONTRACT.md.
Only the Python standard library is used. Input bytes, rather than reconstructed
JSON, establish authoring provenance. No physical coefficient accuracy is claimed.
"""

from __future__ import annotations

import argparse
from decimal import Decimal, DecimalException
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
from typing import Any


MAX_INPUT_BYTES = 256 * 1024
MAX_OUTPUT_BYTES = 128 * 1024
SOURCE_COUNT = 91
MAX_EDGES = 728
MAX_ROW_EDGES = 8
MODEL = "static-source-leakage-v1"
EVIDENCE_STATUS = "synthetic"
BOUNDARY = "normalized-generator-precontact-v1"
SOURCE_CONTENT = "excludes-leakage"
ATLAS_DOCUMENT = "Hammond_B3_Leslie_Research_Atlas_500pp.pdf"
ATLAS_SHA256 = "4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769"
ATLAS_PAGES = [79, 80, 81, 82, 83, 84]
PROFILE_ID = re.compile(r"synthetic-[a-z0-9][a-z0-9-]*", re.ASCII)
TOP_LEVEL_MEMBERS = {
    "schema_version", "profile_id", "model", "evidence_status",
    "coefficient_origin", "boundary", "units", "source_content", "source_count",
    "algorithm_reference", "description", "edges",
}


class SourceLeakageProfileError(ValueError):
    """The authoring input or requested publication violates the contract."""


def _object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SourceLeakageProfileError(f"duplicate JSON member: {key!r}")
        result[key] = value
    return result


def _nonfinite(token: str) -> None:
    raise SourceLeakageProfileError(f"nonfinite JSON number: {token}")


def _members(value: Any, required: set[str], context: str) -> None:
    if type(value) is not dict:
        raise SourceLeakageProfileError(f"{context} must be an object")
    missing = required - value.keys()
    unknown = value.keys() - required
    if missing or unknown:
        details = []
        if missing:
            details.append("missing " + ", ".join(sorted(missing)))
        if unknown:
            details.append("unknown " + ", ".join(sorted(unknown)))
        raise SourceLeakageProfileError(f"{context}: {'; '.join(details)}")


def _fixed(value: Any, expected: Any, name: str) -> None:
    if type(value) is not type(expected) or value != expected:
        raise SourceLeakageProfileError(f"{name} must be {expected!r}")


def _gain(value: Any, context: str) -> float:
    # Decimal retains nonzero decimal inputs that binary64 would erase. Using
    # json's default float conversion would lose that distinction before checks.
    if type(value) not in (int, Decimal):
        raise SourceLeakageProfileError(f"{context} must be a JSON number")
    try:
        converted = float(value)
    except (OverflowError, ValueError, DecimalException) as error:
        raise SourceLeakageProfileError(f"{context} cannot convert to binary64") from error
    if not math.isfinite(converted):
        raise SourceLeakageProfileError(f"{context} must be finite binary64")
    if converted == 0.0:
        reason = "underflows to zero" if value != 0 else "must be nonzero"
        raise SourceLeakageProfileError(f"{context} {reason}")
    if abs(converted) > 0.25:
        raise SourceLeakageProfileError(f"{context} exceeds absolute gain 0.25")
    return converted


def compile_bytes(raw: bytes) -> tuple[bytes, dict[str, Any]]:
    """Validate exact author bytes and return canonical output and its receipt.

    No filesystem mutation occurs here. Gains and admission sums use binary64;
    source IDs and metadata integers must have JSON integer token spelling.
    """
    if len(raw) > MAX_INPUT_BYTES:
        raise SourceLeakageProfileError("authoring input exceeds 256 KiB")
    if raw.startswith(b"\xef\xbb\xbf"):
        raise SourceLeakageProfileError("UTF-8 BOM is not allowed")
    authoring_sha256 = hashlib.sha256(raw).hexdigest()
    try:
        profile = json.loads(
            raw.decode("utf-8"), object_pairs_hook=_object,
            parse_float=Decimal, parse_constant=_nonfinite,
        )
    except SourceLeakageProfileError:
        raise
    except (UnicodeError, ValueError, DecimalException, RecursionError) as error:
        raise SourceLeakageProfileError("invalid UTF-8 JSON authoring input") from error
    _members(profile, TOP_LEVEL_MEMBERS, "profile")
    for name, expected in (
        ("schema_version", 1), ("model", MODEL),
        ("evidence_status", EVIDENCE_STATUS),
        ("coefficient_origin", "synthetic-fixture"), ("boundary", BOUNDARY),
        ("units", "normalized-amplitude-ratio"),
        ("source_content", SOURCE_CONTENT), ("source_count", SOURCE_COUNT),
    ):
        _fixed(profile[name], expected, name)
    profile_id = profile["profile_id"]
    if (type(profile_id) is not str or not 11 <= len(profile_id) <= 64
            or PROFILE_ID.fullmatch(profile_id) is None):
        raise SourceLeakageProfileError("profile_id must be 11–64 lowercase synthetic-* ASCII characters")
    description = profile["description"]
    if type(description) is not str or not description or len(description) > 512:
        raise SourceLeakageProfileError("description must be a nonempty string of at most 512 characters")
    reference = profile["algorithm_reference"]
    _members(reference, {"document", "sha256", "pdf_pages"}, "algorithm_reference")
    _fixed(reference["document"], ATLAS_DOCUMENT, "algorithm_reference.document")
    _fixed(reference["sha256"], ATLAS_SHA256, "algorithm_reference.sha256")
    pages = reference["pdf_pages"]
    if type(pages) is not list or any(type(page) is not int for page in pages) or pages != ATLAS_PAGES:
        raise SourceLeakageProfileError("algorithm_reference.pdf_pages must be integer pages 79–84 in order")
    authored_edges = profile["edges"]
    if type(authored_edges) is not list or len(authored_edges) > MAX_EDGES:
        raise SourceLeakageProfileError("edges must be an array with at most 728 entries")
    edges: list[tuple[int, int, float]] = []
    seen: set[tuple[int, int]] = set()
    for index, edge in enumerate(authored_edges):
        context = f"edges[{index}]"
        _members(edge, {"source", "destination", "gain"}, context)
        for name in ("source", "destination"):
            if type(edge[name]) is not int or not 1 <= edge[name] <= SOURCE_COUNT:
                raise SourceLeakageProfileError(f"{context}.{name} must be a JSON integer from 1 through 91")
        source, destination = edge["source"], edge["destination"]
        if source == destination:
            raise SourceLeakageProfileError(f"{context} is a self-edge")
        pair = (destination, source)
        if pair in seen:
            raise SourceLeakageProfileError(f"{context} duplicates a destination/source pair")
        seen.add(pair)
        edges.append((destination, source, _gain(edge["gain"], f"{context}.gain")))
    edges.sort(key=lambda edge: (edge[0], edge[1]))
    row_destination = 0
    row_count = 0
    row_sum = 0.0
    maximum_row_sum = 0.0
    for destination, _source, gain in edges:
        if destination != row_destination:
            row_destination, row_count, row_sum = destination, 0, 0.0
        row_count += 1
        if row_count > MAX_ROW_EDGES:
            raise SourceLeakageProfileError(f"destination {destination} has more than 8 incoming edges")
        # Deliberately do not use sum/fsum/Decimal: each canonical addition must
        # round to binary64 independently, matching native preparation.
        row_sum = row_sum + abs(gain)
        if row_sum > 0.5:
            raise SourceLeakageProfileError(f"destination {destination} absolute gain sum exceeds 0.5")
        maximum_row_sum = max(maximum_row_sum, row_sum)
    records = [
        "B3LEAKAGE1", f"model {MODEL}", f"profile_id {profile_id}",
        f"evidence_status {EVIDENCE_STATUS}", f"boundary {BOUNDARY}",
        f"source_content {SOURCE_CONTENT}", f"authoring_sha256 {authoring_sha256}",
        f"source_count {SOURCE_COUNT}", f"edge_count {len(edges)}",
    ]
    records.extend(
        f"edge destination {destination} source {source} gain {gain:.17g}"
        for destination, source, gain in edges
    )
    records.append("end")
    compiled = ("\n".join(records) + "\n").encode("ascii")
    if len(compiled) > MAX_OUTPUT_BYTES:
        raise SourceLeakageProfileError("compiled output exceeds 128 KiB")
    receipt = {
        "schema_version": 1, "status": "compiled", "model": MODEL,
        "profile_id": profile_id, "evidence_status": EVIDENCE_STATUS,
        "boundary": BOUNDARY, "source_content": SOURCE_CONTENT,
        "input_sha256": authoring_sha256,
        "compiled_sha256": hashlib.sha256(compiled).hexdigest(),
        "compiled_bytes": len(compiled), "edge_count": len(edges),
        "maximum_row_absolute_gain_sum": maximum_row_sum,
    }
    return compiled, receipt


def _read_input(path: Path) -> bytes:
    # O_NONBLOCK prevents a path raced to a FIFO from hanging before fstat.
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NONBLOCK", 0))
    with os.fdopen(descriptor, "rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise SourceLeakageProfileError("authoring input must be a regular file")
        raw = stream.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise SourceLeakageProfileError("authoring input exceeds 256 KiB")
    return raw


def _publish_exclusive(path: Path, compiled: bytes) -> None:
    # lexists includes dangling symlinks. The final hard link is atomic and also
    # refuses a target created after this check, unlike replacement/rename.
    if os.path.lexists(path):
        raise SourceLeakageProfileError("output already exists; refusing to replace it")
    with tempfile.TemporaryDirectory(prefix=".b3leakage-", dir=path.parent) as directory:
        candidate = Path(directory) / "compiled"
        with candidate.open("xb") as stream:
            stream.write(compiled)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(candidate, path)
        except FileExistsError as error:
            raise SourceLeakageProfileError("output already exists; refusing to replace it") from error


def compile_profile(input_path: Path, output_path: Path) -> dict[str, Any]:
    """Compile regular-file input and exclusively publish fully validated bytes."""
    compiled, receipt = compile_bytes(_read_input(Path(input_path)))
    _publish_exclusive(Path(output_path), compiled)
    return receipt


class _Once(argparse.Action):
    def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace,
                 values: str, option_string: str | None = None) -> None:
        if getattr(namespace, self.dest, None) is not None:
            parser.error(f"{option_string} may be specified only once")
        setattr(namespace, self.dest, values)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--input", type=Path, required=True, action=_Once)
    parser.add_argument("--output", type=Path, required=True, action=_Once)
    args = parser.parse_args(argv)
    try:
        receipt = compile_profile(args.input, args.output)
    except (SourceLeakageProfileError, OSError) as error:
        print(f"source leakage compilation failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":"), allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
