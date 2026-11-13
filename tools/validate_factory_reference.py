#!/usr/bin/env python3
"""Check frozen independent Table III readings against identified project data.

Read-only, standard-library tooling; no routing formula supplies reference cells.
Public API: expected_manifest(), load_json(path), parse_transcription(bytes, kind),
validate_manifest(value), validate_reference(root, source_pdf=None).
FactoryReferenceError retains bounded, cell-specific diagnostics on failure.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import stat
import sys


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = "data/references/factory-table-iii.json"
PROFILE_PATH = "data/profiles/nominal-unmeasured-v1.json"
PEDAL_PATH = "data/pedal-map.json"
MAX_JSON_BYTES = 256 * 1024
MAX_CSV_BYTES = 8 * 1024
MAX_SOURCE_BYTES = 16 * 1024 * 1024
MAX_DEPTH = 24
MAX_NODES = 20000
MAX_DIAGNOSTICS = 64
MANUAL_SHA256 = "23ade40234db10d0bf99cd5acf9ee0ff29e4656e847e61409ebe8717f7cb9dc6"
PEDAL_SHA256 = "b8177479a5af16f4e6b8759313d90148a1213657c83f8a6e6533422bfa104ca1"
SOURCE_SHA256 = "ec2ac51f363dcd1ee039f7711acda32fd014e15ad80dcb77ae199545f9130cc9"
PROFILE_RAW_SHA256 = "d17a266ed97cbbd3a2925ebebafafbd6c0e3f84763635732e0a9351d0eab2bff"
PROFILE_CANONICAL_SHA256 = "49791eac8d0b556b0abd2018b8cabc6f240161edab8a9fa0ef97905f2badda83"
PEDAL_RAW_SHA256 = "58a30850c08933a075cfcec04faeb2cb479f60bd9dda82ace3246552221623bd"
PEDAL_CANONICAL_SHA256 = "7b2631a0c7d55a18f8225d4ee420e472c23b9f2809eec69865474eafce6f5fb2"
DRAWBARS = ["16ft", "5_1/3ft", "8ft", "4ft", "2_2/3ft",
            "2ft", "1_3/5ft", "1_1/3ft", "1ft"]
PEDAL_COLUMNS = ["fundamental", "third_contact", "second", "fourth",
                 "sixth", "eighth", "tenth", "twelfth"]
DISCONNECTIONS = [[pedal, "c2"] for pedal in range(8, 13)]


def expected_manifest() -> dict:
    """The immutable v1 attestation contract, without a duplicate numeric table."""
    return {
        "schema_version": 1,
        "reference_id": "factory-table-iii-comparison-v1",
        "kind": "comparison-provenance-manifest",
        "review_date": "2026-11-13",
        "evidence_class": "documented",
        "source": {
            "title": "Hammond Organ Service Manual - Early Models (A,B,C series, B3, A-100, RT, D, G, etc.)",
            "url": "https://medias.audiofanzine.com/files/hammond-service-manual-a-a-100-ba-bc-bcv-bv-b2-b3-c-cv-c2-c2-text-470145.pdf",
            "sha256": SOURCE_SHA256,
            "bytes": 7077593,
            "pdf_pages": 220,
            "page_numbering": "one-based PDF; printed folios recorded separately",
            "factory_edition": None,
            "edition_reason": "Exact factory edition, print date and production revisions are unestablished.",
            "applicable_models": ["B-3", "C-3"],
            "scope_locator": {"pdf_page": 148, "printed_page": "3-69", "region": "opening note"},
            "manual_context_locator": {
                "pdf_page": 154, "printed_page": "3-75",
                "region": "right column, paragraphs 3-15 through 3-19",
            },
            "table_locators": [
                {"kind": "manual", "rows": [1, 36], "pdf_page": 155, "printed_page": "3-76"},
                {"kind": "manual", "rows": [37, 61], "pdf_page": 156, "printed_page": "3-77"},
                {"kind": "pedal", "rows": [1, 25], "pdf_page": 157, "printed_page": "3-78"},
            ],
            "identifier_locator": {
                "pdf_page": 157, "printed_page": "3-78", "region": "footnote below Table III",
            },
            "redistributed_in_repository": False,
            "redistribution_permission": "not-established",
        },
        "readings": [
            {
                "reviewer": f"Agent {agent}", "review": label,
                "note": f"docs/research/FACTORY_REVIEW_{label}.md",
                "method": "direct-image-transcription",
                "frozen_before_other_reading_and_derived_maps": True,
                "manual": {"path": f"data/references/review-{label.lower()}-manual.csv",
                           "bytes": 1852, "sha256": MANUAL_SHA256},
                "pedal": {"path": f"data/references/review-{label.lower()}-pedal.csv",
                          "bytes": 677, "sha256": PEDAL_SHA256},
                "unresolved_cells": [],
            } for label, agent in (("A", 37), ("B", 38))
        ],
        "table_contract": {
            "unit": "dimensionless factory frequency-number identifier",
            "row_id_base": 1, "source_id_bounds": [1, 91],
            "manual_header": ["key"] + [f"d{i}" for i in range(1, 10)],
            "manual_printed_roles": ["subfundamental", "sub-third", "fundamental", "second",
                                     "third", "fourth", "fifth", "sixth", "eighth"],
            "manual_project_columns": DRAWBARS.copy(),
            "manual_shape": [61, 9],
            "pedal_header": ["pedal"] + [f"c{i}" for i in range(1, 9)],
            "pedal_printed_roles": ["fundamental", "third", "second", "fourth",
                                    "sixth", "eighth", "tenth", "twelfth"],
            "pedal_project_columns": PEDAL_COLUMNS.copy(),
            "pedal_shape": [25, 8],
            "empty_csv_meaning": "printed dash; no assignment, represented as JSON null",
            "pedal_disconnections": [cell.copy() for cell in DISCONNECTIONS],
            "physical_contact_sequence_established": False,
        },
        "targets": {
            "manual": {
                "path": PROFILE_PATH, "id": "nominal-unmeasured-v1", "bytes": 19627,
                "raw_sha256": PROFILE_RAW_SHA256, "canonical_sha256": PROFILE_CANONICAL_SHA256,
                "field": "manual_map.tone_ids",
                "authoring_independent_factory_verification": False,
            },
            "pedal": {
                "path": PEDAL_PATH, "id": "atlas-derived-b3-c3-pedal-v1", "bytes": 3267,
                "raw_sha256": PEDAL_RAW_SHA256, "canonical_sha256": PEDAL_CANONICAL_SHA256,
                "field": "rows[].sources",
                "authoring_independent_factory_transcription_status": "missing",
            },
            "canonicalization": "json.dumps(sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode('utf-8'); no final newline; project convention, not RFC8785",
        },
        "comparison": {
            "reviewer": "Agent 39", "status": "exact-match",
            "manual_assignments": 549, "pedal_positions": 200,
            "pedal_connected": 195, "pedal_disconnected": 5,
            "a_b_manual_mismatches": 0, "a_b_pedal_mismatches": 0,
            "each_reading_manual_target_mismatches": 0,
            "each_reading_pedal_target_mismatches": 0,
            "correction_history": [],
        },
        "claim_boundary": {
            "attestation": "Later collateral documentary comparison for these exact target digests.",
            "original_authoring_provenance_changed": False,
            "atlas_companion_recovered": False,
            "measured_specimen": False,
            "frequency_or_gearing_verified": False,
            "amplitude_or_phase_calibrated": False,
            "pedal_audio_verified": False,
            "percussion_verified": False,
            "physical_fidelity_established": False,
            "specimen_identity": None,
            "specimen_continuity": "not-measured",
        },
    }


class FactoryReferenceError(ValueError):
    """Failed validation; diagnostics are bounded independently of input errors."""

    def __init__(self, diagnostics: str | list[str], total: int | None = None):
        self.diagnostics = tuple([diagnostics] if isinstance(diagnostics, str) else diagnostics)
        self.total = len(self.diagnostics) if total is None else total
        suffix = (f"\n{self.total - len(self.diagnostics)} additional diagnostics omitted"
                  if self.total > len(self.diagnostics) else "")
        super().__init__("\n".join(self.diagnostics) + suffix)


class _Issues:
    def __init__(self):
        self.items: list[str] = []
        self.total = 0

    def add(self, message: str) -> None:
        self.total += 1
        if len(self.items) < MAX_DIAGNOSTICS:
            self.items.append(message)

    def finish(self) -> None:
        if self.total:
            raise FactoryReferenceError(self.items, self.total)


def _exact(value: object, expected: object, path: str) -> None:
    if type(value) is not type(expected):
        raise FactoryReferenceError(f"{path}: expected {type(expected).__name__}, got {type(value).__name__}")
    if type(expected) is dict:
        if set(value) != set(expected):
            raise FactoryReferenceError(f"{path}: missing {sorted(set(expected) - set(value))}; "
                                        f"unknown {sorted(set(value) - set(expected))}")
        for key in expected:
            _exact(value[key], expected[key], f"{path}.{key}")
    elif type(expected) is list:
        if len(value) != len(expected):
            raise FactoryReferenceError(f"{path}: expected {len(expected)} entries, got {len(value)}")
        for index, item in enumerate(expected):
            _exact(value[index], item, f"{path}[{index}]")
    elif value != expected:
        raise FactoryReferenceError(f"{path}: expected {expected!r}, got {value!r}")


def validate_manifest(value: object) -> None:
    """Reject changed identities, scope, locators, claims, counts and field types."""
    _exact(value, expected_manifest(), "manifest")


def _read(path: Path, limit: int) -> bytes:
    try:
        if not stat.S_ISREG(path.stat().st_mode):
            raise FactoryReferenceError(f"{path}: must be a regular file")
        with path.open("rb") as source:
            before = os.fstat(source.fileno())
            if not stat.S_ISREG(before.st_mode) or before.st_size > limit:
                raise FactoryReferenceError(f"{path}: must be a regular file of at most {limit} bytes")
            payload = source.read(limit + 1)
            after = os.fstat(source.fileno())
        identity = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        if identity(before) != identity(after) or len(payload) != before.st_size:
            raise FactoryReferenceError(f"{path}: file changed during read")
        if len(payload) > limit:
            raise FactoryReferenceError(f"{path}: exceeds {limit} byte limit")
        return payload
    except OSError as error:
        raise FactoryReferenceError(f"{path}: cannot read: {error}") from error


def _unique(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise FactoryReferenceError(f"JSON: duplicate object name {key!r}")
        result[key] = value
    return result


def _reject_constant(token: str) -> None:
    raise FactoryReferenceError(f"JSON: forbidden nonfinite token {token}")


def _json(payload: bytes) -> object:
    try:
        value = json.loads(payload.decode("utf-8"), object_pairs_hook=_unique,
                           parse_constant=_reject_constant)
        pending = [(value, 0)]
        nodes = 0
        while pending:
            item, depth = pending.pop()
            nodes += 1
            if nodes > MAX_NODES or depth > MAX_DEPTH:
                raise FactoryReferenceError("JSON: structure exceeds depth/node bounds")
            if type(item) is str:
                if len(item) > 4096:
                    raise FactoryReferenceError("JSON: string exceeds 4096 characters")
                item.encode("utf-8")  # Reject escaped unpaired surrogates in values and names.
            if type(item) is float and not math.isfinite(item):
                raise FactoryReferenceError("JSON: nonfinite number")
            if type(item) is dict:
                pending.extend((child, depth + 1) for pair in item.items() for child in pair)
            elif type(item) is list:
                pending.extend((child, depth + 1) for child in item)
        return value
    except (UnicodeError, ValueError, RecursionError) as error:
        if isinstance(error, FactoryReferenceError):
            raise
        raise FactoryReferenceError(f"invalid UTF-8 JSON: {error}") from error


def load_json(path: str | Path) -> object:
    """Read strict JSON within byte, depth, node and string bounds."""
    return _json(_read(Path(path), MAX_JSON_BYTES))


def parse_transcription(payload: bytes, kind: str) -> list[list[int | None]]:
    """Parse exact ordered CSV shapes, decimal IDs and explicit empty positions."""
    if kind not in ("manual", "pedal"):
        raise FactoryReferenceError(f"unknown table kind {kind!r}")
    if len(payload) > MAX_CSV_BYTES:
        raise FactoryReferenceError("CSV: exceeds byte limit")
    if not payload.endswith(b"\n") or b"\r" in payload:
        raise FactoryReferenceError("CSV: requires LF line endings and final LF")
    try:
        records = list(csv.reader(io.StringIO(payload.decode("utf-8")), strict=True))
    except (UnicodeError, csv.Error) as error:
        raise FactoryReferenceError(f"invalid UTF-8 CSV: {error}") from error
    height, width, prefix, row_name = (61, 9, "d", "key") if kind == "manual" else (25, 8, "c", "pedal")
    if len(records) != height + 1:
        raise FactoryReferenceError(f"{kind}: expected {height} data rows, got {len(records) - 1}")
    _exact(records[0], [row_name] + [f"{prefix}{i}" for i in range(1, width + 1)], f"{kind}.header")
    rows = []
    for ordinal, record in enumerate(records[1:], 1):
        if len(record) != width + 1:
            raise FactoryReferenceError(f"{kind} {ordinal}: expected {width + 1} fields, got {len(record)}")
        if record[0] != str(ordinal):
            raise FactoryReferenceError(f"{kind} row {ordinal}: expected ordered ID {ordinal}, got {record[0]!r}")
        row = []
        for column, token in enumerate(record[1:], 1):
            cell = f"{kind} {ordinal}/{prefix}{column}"
            if token == "" and kind == "pedal":
                row.append(None)
            elif not re.fullmatch(r"[1-9][0-9]?", token) or not (13 if kind == "manual" else 1) <= int(token) <= 91:
                raise FactoryReferenceError(f"{cell}: invalid integer source identifier {token!r}")
            else:
                row.append(int(token))
        rows.append(row)
    return rows


def _location(kind: str, row: int, column: int) -> str:
    page, folio = ((155, "3-76") if row <= 36 else (156, "3-77")) if kind == "manual" else (157, "3-78")
    prefix = "d" if kind == "manual" else "c"
    return f"{kind} {row}/{prefix}{column} [Table III, PDF {page}, printed {folio}]"


def _matrix(value: object, kind: str, label: str) -> list:
    height, width = (61, 9) if kind == "manual" else (25, 8)
    if type(value) is not list or len(value) != height:
        raise FactoryReferenceError(f"{label}: expected {height} ordered rows")
    for row_index, row in enumerate(value, 1):
        if type(row) is not list or len(row) != width:
            raise FactoryReferenceError(f"{label}, {kind} {row_index}: expected {width} positions")
        for column, source in enumerate(row, 1):
            if source is None and kind == "pedal":
                continue
            if type(source) is not int or not (13 if kind == "manual" else 1) <= source <= 91:
                raise FactoryReferenceError(f"{label}, {_location(kind, row_index, column)}: "
                                            f"invalid source {source!r} ({type(source).__name__})")
    return value


def _compare(left: list, right: list, kind: str, label: str, issues: _Issues) -> int:
    mismatches = 0
    for row, (left_row, right_row) in enumerate(zip(left, right), 1):
        for column, (a, b) in enumerate(zip(left_row, right_row), 1):
            if type(a) is not type(b) or a != b:
                mismatches += 1
                issues.add(f"{label}: {_location(kind, row, column)}: {a!r} != {b!r}")
    return mismatches


def _nulls(rows: list, label: str, issues: _Issues) -> None:
    for row, values in enumerate(rows, 1):
        for column, value in enumerate(values, 1):
            expected_empty = [row, f"c{column}"] in DISCONNECTIONS
            if (value is None) != expected_empty:
                issues.add(f"{label}: {_location('pedal', row, column)}: "
                           f"expected {'null disconnection' if expected_empty else 'connected integer'}, got {value!r}")


def _hashes(payload: bytes, expected: dict, label: str, issues: _Issues, value: object = None) -> None:
    if len(payload) != expected["bytes"]:
        issues.add(f"{label}: expected {expected['bytes']} raw bytes, got {len(payload)}")
    observed = hashlib.sha256(payload).hexdigest()
    wanted = expected.get("sha256", expected.get("raw_sha256"))
    if observed != wanted:
        issues.add(f"{label}: raw SHA-256 mismatch: expected {wanted}, got {observed}")
    if "canonical_sha256" in expected:
        canonical = json.dumps(value, sort_keys=True, separators=(",", ":"),
                               ensure_ascii=False, allow_nan=False).encode("utf-8")
        digest = hashlib.sha256(canonical).hexdigest()
        if digest != expected["canonical_sha256"]:
            issues.add(f"{label}: canonical SHA-256 mismatch: expected {expected['canonical_sha256']}, got {digest}")


def validate_reference(root: str | Path = ROOT, source_pdf: str | Path | None = None) -> dict:
    """Compare all cells and identities; never modify or silently repair inputs."""
    root = Path(root)
    manifest = load_json(root / MANIFEST_PATH)
    validate_manifest(manifest)
    issues = _Issues()
    readings = {}
    for reading in manifest["readings"]:
        # Review prose is retained for human audit; program checks its presence.
        if not _read(root / reading["note"], MAX_JSON_BYTES).strip():
            raise FactoryReferenceError(f"{reading['note']}: empty review note")
        for kind in ("manual", "pedal"):
            record = reading[kind]
            payload = _read(root / record["path"], MAX_CSV_BYTES)
            _hashes(payload, record, record["path"], issues)
            try:
                rows = parse_transcription(payload, kind)
            except FactoryReferenceError as error:
                issues.add(f"{record['path']}: {error}")
                continue
            readings[reading["review"], kind] = rows
            if kind == "pedal":
                _nulls(rows, record["path"], issues)
    targets = {}
    for kind in ("manual", "pedal"):
        target = manifest["targets"][kind]
        payload = _read(root / target["path"], MAX_JSON_BYTES)
        value = _json(payload)
        _hashes(payload, target, target["path"], issues, value)
        try:
            if kind == "manual":
                _exact(value["profile_id"], target["id"], "profile.profile_id")
                _exact(value["evidence_status"], "unmeasured", "profile.evidence_status")
                _exact(value["manual_map"]["independent_factory_verification"], False,
                       "profile.manual_map.independent_factory_verification")
                _exact(value["manual_map"]["drawbar_order"], DRAWBARS, "profile.manual_map.drawbar_order")
                rows = value["manual_map"]["tone_ids"]
            else:
                _exact(value["map_id"], target["id"], "pedal.map_id")
                _exact(value["columns"], PEDAL_COLUMNS, "pedal.columns")
                _exact(value["provenance"]["independent_factory_transcription_status"], "missing",
                       "pedal.provenance.independent_factory_transcription_status")
                rows = []
                records = value["rows"]
                if type(records) is not list or len(records) != 25:
                    raise FactoryReferenceError("pedal.rows: expected 25 ordered records")
                for ordinal, row in enumerate(records, 1):
                    if type(row) is not dict or set(row) != {"pedal_id", "sources"}:
                        raise FactoryReferenceError(f"pedal.rows[{ordinal - 1}]: invalid record fields")
                    _exact(row["pedal_id"], ordinal, f"pedal.rows[{ordinal - 1}].pedal_id")
                    rows.append(row["sources"])
            targets[kind] = _matrix(rows, kind, target["path"])
            if kind == "pedal":
                _nulls(rows, target["path"], issues)
        except (KeyError, TypeError) as error:
            issues.add(f"{target['path']}: missing or invalid target structure: {error}")
        except FactoryReferenceError as error:
            issues.add(str(error))
    mismatches = {}
    for kind in ("manual", "pedal"):
        if ("A", kind) in readings and ("B", kind) in readings:
            mismatches[f"a_b_{kind}"] = _compare(readings["A", kind], readings["B", kind],
                                                kind, "A versus B", issues)
        for label in ("A", "B"):
            if (label, kind) in readings and kind in targets:
                mismatches[f"{label.lower()}_target_{kind}"] = _compare(
                    readings[label, kind], targets[kind], kind, f"{label} versus target", issues)
    source_status = "not-checked; source PDF not supplied"
    if source_pdf is not None:
        payload = _read(Path(source_pdf), MAX_SOURCE_BYTES)
        _hashes(payload, manifest["source"], "source PDF", issues)
        source_status = "matched raw size and SHA-256"
    issues.finish()
    return {
        "reference_id": manifest["reference_id"], "status": "exact-match",
        "manual_assignments": 549, "pedal_positions": 200,
        "pedal_connected": 195, "pedal_disconnected": 5,
        "pedal_disconnections": [cell.copy() for cell in DISCONNECTIONS],
        "mismatches": mismatches,
        "manual_csv_sha256": MANUAL_SHA256, "pedal_csv_sha256": PEDAL_SHA256,
        "profile_canonical_sha256": PROFILE_CANONICAL_SHA256,
        "pedal_canonical_sha256": PEDAL_CANONICAL_SHA256,
        "source_pdf_sha256": SOURCE_SHA256, "source_pdf_check": source_status,
        "original_authoring_provenance_changed": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root (default: tool's parent)")
    parser.add_argument("--source-pdf", type=Path, help="optional external source scan to verify by raw bytes")
    args = parser.parse_args(argv)
    try:
        result = validate_reference(args.root, args.source_pdf)
    except FactoryReferenceError as error:
        print(f"factory reference error:\n{error}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
