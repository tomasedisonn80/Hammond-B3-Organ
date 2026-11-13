#!/usr/bin/env python3
"""Validate the documentary, atlas-derived pedal map; never write or enable audio.

Public API: load_pedal_map(path), validate_pedal_map(value). Rejected data raises
PedalMapError. Validation never changes its argument. Only the Python stdlib is
required; parsing, provenance checks and file access belong outside processing.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


MAX_INPUT_BYTES = 32 * 1024
METADATA = {
    "schema_version": 1,
    "map_id": "atlas-derived-b3-c3-pedal-v1",
    "provenance": {
        "evidence_class": "derived",
        "applicable_variant": "B-3/C-3 factory pedal wiring represented in atlas chapter 022",
        "source_document": {
            "path": "Hammond_B3_Leslie_Research_Atlas_500pp.pdf",
            "sha256": "4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769",
            "edition": "2026-11-12",
            "pages": [139, 140, 141, 142, 143, 144],
            "page_numbering": "one-based PDF and printed atlas pages",
        },
        "source_reference": "S022-01: Hammond Organ Service Manual, original console models",
        "derivation": "atlas-p140-piecewise-rule",
        "mapping_page": 140,
        "printed_reference_pedals": [1, 7, 8, 13, 25],
        "bus_membership_page": 140,
        "bus_membership_evidence_class": "documented",
        "companion_table_status": "not-supplied",
        "independent_factory_transcription_status": "missing",
        "specimen_continuity_status": "not-measured",
        "specimen_identity": None,
        "uncertainty": "Independent original Table III transcription and specimen continuity checks remain open.",
    },
    "indexing": {
        "pedal_id_base": 1,
        "column_index_base": 0,
        "source_id_base": 1,
        "source_id_bounds": [1, 91],
        "null_meaning": "no-connection",
    },
    "columns": ["fundamental", "third_contact", "second", "fourth", "sixth", "eighth", "tenth", "twelfth"],
    "bus_columns": {"brown": [0, 1], "red": [2, 3], "orange": [4, 5], "yellow": [6, 7]},
    "counts": {"pedals": 25, "columns": 8, "positions": 200, "connected": 195, "disconnected": 5},
}


class PedalMapError(ValueError):
    """Invalid or unreadable documentary pedal data."""


def _fail(path: str, message: str) -> None:
    raise PedalMapError(f"{path}: {message}")


def _keys(value: object, expected: set, path: str) -> None:
    if type(value) is not dict or set(value) != expected:
        _fail(path, f"must be an object with exactly these fields: {', '.join(sorted(expected))}")


def _exact(value: object, expected: object, path: str) -> None:
    # Equality alone accepts True as 1 and 1.0 as an integer ID.
    if type(value) is not type(expected):
        _fail(path, f"must have type {type(expected).__name__}")
    if type(expected) is dict:
        _keys(value, set(expected), path)
        for key, item in expected.items():
            _exact(value[key], item, f"{path}.{key}")
    elif type(expected) is list:
        if len(value) != len(expected):
            _fail(path, f"must contain exactly {len(expected)} entries")
        for index, item in enumerate(expected):
            _exact(value[index], item, f"{path}[{index}]")
    elif value != expected:
        _fail(path, f"must be {expected!r} for this versioned reconstruction")


def validate_pedal_map(value: object) -> None:
    """Check exact metadata, all 200 positions, IDs and exceptions without mutation."""
    _keys(value, set(METADATA) | {"rows"}, "pedal_map")
    for key, expected in METADATA.items():
        _exact(value[key], expected, key)
    rows = value["rows"]
    if type(rows) is not list or len(rows) != 25:
        _fail("rows", "must contain exactly 25 ordered pedal records")
    connected = 0
    for index, row in enumerate(rows):
        path = f"rows[{index}]"
        _keys(row, {"pedal_id", "sources"}, path)
        pedal = index + 1
        _exact(row["pedal_id"], pedal, f"{path}.pedal_id")
        sources = row["sources"]
        if type(sources) is not list or len(sources) != 8:
            _fail(f"{path}.sources", "must contain eight distinct contact positions")
        third = pedal + 12 if pedal <= 7 else None if pedal <= 12 else pedal + 19
        expected = [pedal, third, pedal + 12, pedal + 24, pedal + 31,
                    pedal + 36, pedal + 40, pedal + 43]
        for column, source in enumerate(sources):
            cell = f"{path}.sources[{column}]"
            if source is not None:
                if type(source) is not int or not 1 <= source <= 91:
                    _fail(cell, "must be an integer source ID in 1..91 or null for no connection")
                connected += 1
            _exact(source, expected[column], cell)
    if connected != 195 or 200 - connected != 5:
        _fail("rows", "must retain 195 connections and five disconnections")


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            _fail("JSON", f"duplicate object name {key!r}")
        result[key] = value
    return result


def _reject_number(token: str) -> None:
    _fail("JSON", f"non-integer or nonfinite numeric token {token!r} is forbidden")


def load_pedal_map(path: str | Path) -> dict:
    """Read at most 32 KiB of strict UTF-8 JSON and validate the complete map."""
    try:
        with Path(path).open("rb") as source:
            payload = source.read(MAX_INPUT_BYTES + 1)
    except OSError as error:
        raise PedalMapError(f"cannot read {path}: {error}") from error
    if len(payload) > MAX_INPUT_BYTES:
        _fail("JSON", f"input exceeds {MAX_INPUT_BYTES} byte limit")
    try:
        value = json.loads(payload.decode("utf-8"), object_pairs_hook=_unique_object,
                           parse_constant=_reject_number, parse_float=_reject_number)
    except PedalMapError:
        raise
    except (UnicodeError, ValueError, RecursionError) as error:
        raise PedalMapError(f"invalid UTF-8 JSON: {error}") from error
    validate_pedal_map(value)
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--input", required=True, type=Path, help="documentary pedal-map JSON")
    args = parser.parse_args(argv)
    try:
        load_pedal_map(args.input)
    except PedalMapError as error:
        print(f"pedal map error: {error}", file=sys.stderr)
        return 1
    print(f"checked {METADATA['map_id']}: 25 pedals, 200 positions, 195 connected, 5 disconnected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
