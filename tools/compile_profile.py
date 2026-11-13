#!/usr/bin/env python3
"""Validate and compile the explicitly unmeasured version-1 organ profile.

This is a semantic validator for one named project model, not a generic JSON
Schema implementation. All parsing and writing belongs outside audio processing.
Canonical authoring bytes use json.dumps(sort_keys=True, separators=(",", ":"),
ensure_ascii=False, allow_nan=False).encode("utf-8"), with no final newline.
This project convention is not RFC 8785. Compiled text uses round-trip Python
binary64 decimal representations and one final LF, independent of the locale.

Public API: load_profile(path), validate_profile(dict), canonical_json(dict),
authoring_sha256(dict), compile_profile(dict). Validation never changes its input.
All rejected input raises ProfileError (a ValueError subclass).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import tempfile
from typing import Any


SCHEMA_VERSION = 1
MODEL_VERSION = 1
PROFILE_ID = "nominal-unmeasured-v1"
MODEL = "ideal-shared-sine-v1"
ATLAS_ID = "research-atlas-2026-11-12"
ATLAS_PATH = "Hammond_B3_Leslie_Research_Atlas_500pp.pdf"
ATLAS_SHA256 = "4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769"
MAX_INPUT_BYTES = 256 * 1024
MAX_OUTPUT_BYTES = 128 * 1024
MAX_DEPTH = 24
MAX_NODES = 20000
MAX_STRING_LENGTH = 4096
DRAWBAR_OFFSETS = (0, 19, 12, 24, 31, 36, 40, 43, 48)
DRAWBAR_ORDER = ("16ft", "5_1/3ft", "8ft", "4ft", "2_2/3ft", "2ft", "1_3/5ft", "1_1/3ft", "1ft")
EVIDENCE_CLASSES = frozenset(("documented", "measured", "derived", "proposed", "unknown"))
EVIDENCE_KEYS = frozenset(("evidence_class", "applicable_variant", "source_locator",
                           "uncertainty", "acquisition_reference", "reason"))
MODEL_BOUNDARIES = {
    "waveform": "normalized-synthetic-sine",
    "contacts": "ideal-simultaneous-make-break-v1",
    "physical_pickup_voltage": "not-modeled",
    "pickup_harmonics_and_loading": "not-modeled",
    "leakage": "not-modeled",
    "pedals": "not-modeled",
    "percussion": "not-modeled",
    "scanner": "not-modeled",
    "ao28": "not-modeled",
    "leslie": "not-modeled",
}


class ProfileError(ValueError):
    """An actionable authoring, semantic, or file-operation failure."""


def _fail(path: str, message: str) -> None:
    raise ProfileError(f"{path}: {message}")


def _object(value: Any, keys: set[str] | frozenset[str], path: str) -> dict:
    if type(value) is not dict:
        _fail(path, "must be an object")
    unknown = set(value) - keys
    missing = keys - set(value)
    if unknown:
        _fail(path, f"unknown field(s): {', '.join(sorted(unknown))}")
    if missing:
        _fail(path, f"missing field(s): {', '.join(sorted(missing))}")
    return value


def _array(value: Any, length: int, path: str) -> list:
    if type(value) is not list or len(value) != length:
        _fail(path, f"must be an array containing exactly {length} entries")
    return value


def _string(value: Any, path: str) -> str:
    if type(value) is not str or not value.strip():
        _fail(path, "must be a nonempty string")
    return value


def _constant(value: Any, expected: Any, path: str) -> None:
    # bool is an int subclass; equality alone would wrongly accept True as 1.
    if type(value) is not type(expected) or value != expected:
        _fail(path, f"must be {expected!r} for this named baseline")


def _integer(value: Any, low: int, high: int, path: str) -> int:
    if type(value) is not int:
        _fail(path, "must be an integer; booleans are not numbers")
    if not low <= value <= high:
        _fail(path, f"must be in [{low}, {high}]")
    return value


def _number(value: Any, low: float, high: float, path: str) -> float:
    if type(value) not in (int, float):
        _fail(path, "must be a finite number; booleans are not numbers")
    try:
        finite = math.isfinite(value)
    except OverflowError:
        finite = False
    if not finite:
        _fail(path, "must be finite")
    if not low <= value <= high:
        _fail(path, f"must be in [{low}, {high}]")
    return float(value)


def _nominal_number(value: Any, expected: float, low: float, high: float, path: str) -> None:
    actual = _number(value, low, high, path)
    if actual != expected:
        _fail(path, f"does not match nominal equation/value (expected {expected!r})")


def nominal_frequency(tone_id: int) -> float:
    """The version-1 binary64 12-TET engineering equation; not factory gearing."""
    return 440.0 * 2.0 ** ((tone_id - 46) / 12.0)


def nominal_drawbar_gain(position: int) -> float:
    return 0.0 if position == 0 else 10.0 ** (3.0 * (position - 8) / 20.0)


def nominal_manual_row(key: int) -> list[int]:
    row = []
    for drawbar, offset in enumerate(DRAWBAR_OFFSETS):
        tone = key + offset
        if drawbar == 0 and key <= 12:
            tone += 12
        while tone > 91:
            tone -= 12
        row.append(tone)
    return row


def _tree_bounds(value: Any) -> None:
    """Bound imported Python objects too, and reject non-JSON scalar types."""
    count = 0

    def visit(item: Any, depth: int, path: str) -> None:
        nonlocal count
        count += 1
        if count > MAX_NODES:
            _fail(path, f"exceeds {MAX_NODES} JSON values")
        if depth > MAX_DEPTH:
            _fail(path, f"exceeds maximum nesting depth {MAX_DEPTH}")
        if type(item) is dict:
            if len(item) > 64:
                _fail(path, "object exceeds 64 fields")
            for key, child in item.items():
                if type(key) is not str:
                    _fail(path, "object names must be strings")
                visit(key, depth + 1, f"{path}.<name>")
                visit(child, depth + 1, f"{path}.{key}")
        elif type(item) is list:
            if len(item) > 1024:
                _fail(path, "array exceeds 1024 entries")
            for index, child in enumerate(item):
                visit(child, depth + 1, f"{path}[{index}]")
        elif type(item) is str:
            if len(item) > MAX_STRING_LENGTH:
                _fail(path, f"string exceeds {MAX_STRING_LENGTH} characters")
            try:
                item.encode("utf-8")
            except UnicodeEncodeError:
                _fail(path, "contains an invalid Unicode surrogate")
        elif type(item) in (int, float):
            try:
                finite = math.isfinite(item)
            except OverflowError:
                finite = False
            if not finite:
                _fail(path, "numbers must be finite and representable as binary64")
        elif item is not None and type(item) is not bool:
            _fail(path, f"unsupported JSON value type {type(item).__name__}")

    visit(value, 0, "profile")


def _evidence(record: dict, evidence_class: str, pages: tuple[int, ...], path: str) -> None:
    value = _string(record["evidence_class"], f"{path}.evidence_class")
    if value not in EVIDENCE_CLASSES:
        _fail(f"{path}.evidence_class", "unknown evidence class")
    if value == "measured" and record["acquisition_reference"] is None:
        _fail(path, "measured evidence requires an acquisition reference")
    _constant(value, evidence_class, f"{path}.evidence_class")
    _constant(record["applicable_variant"], PROFILE_ID, f"{path}.applicable_variant")
    _constant(record["uncertainty"], None, f"{path}.uncertainty")
    _constant(record["acquisition_reference"], None, f"{path}.acquisition_reference")
    _string(record["reason"], f"{path}.reason")
    locator = _object(record["source_locator"], {"document_id", "pdf_pages"}, f"{path}.source_locator")
    _constant(locator["document_id"], ATLAS_ID, f"{path}.source_locator.document_id")
    page_list = _array(locator["pdf_pages"], len(pages), f"{path}.source_locator.pdf_pages")
    for index, page in enumerate(page_list):
        _integer(page, 1, 500, f"{path}.source_locator.pdf_pages[{index}]")
    if sorted(page_list) != list(pages):
        _fail(f"{path}.source_locator.pdf_pages", f"must locate atlas PDF pages {list(pages)}")


def validate_profile(profile: dict) -> None:
    """Validate the entire supported authoring model without changing it.

    Required keys are exact at every level. Numeric values must reproduce the
    named nominal equations at binary64 precision; arbitrary tuning, output gain,
    amplitude, phases, or routing require a future distinct model/profile version.
    """
    _tree_bounds(profile)
    _object(profile, {
        "schema_version", "profile_id", "model_version", "model", "evidence_status",
        "source_document", "reference", "frequency_model", "source_fields", "sources",
        "manual_map", "drawbar_gains", "output_gain", "model_boundaries",
    }, "profile")
    for field, expected in (("schema_version", SCHEMA_VERSION), ("model_version", MODEL_VERSION),
                            ("profile_id", PROFILE_ID), ("model", MODEL),
                            ("evidence_status", "unmeasured")):
        _constant(profile[field], expected, field)

    document = _object(profile["source_document"],
                       {"id", "path", "sha256", "edition", "page_numbering", "evidence_class"},
                       "source_document")
    for field, expected in (("id", ATLAS_ID), ("path", ATLAS_PATH), ("sha256", ATLAS_SHA256),
                            ("edition", "2026-11-12"), ("page_numbering", "one_based_pdf"),
                            ("evidence_class", "documented")):
        _constant(document[field], expected, f"source_document.{field}")

    reference = _object(profile["reference"], {"target_instrument", "specimen_id", "ao28_revision", "measurements"}, "reference")
    _constant(reference["target_instrument"], "Hammond B-3", "reference.target_instrument")
    for field in ("specimen_id", "ao28_revision", "measurements"):
        path = f"reference.{field}"
        record = _object(reference[field], EVIDENCE_KEYS | {"value"}, path)
        _constant(record["value"], None, f"{path}.value")
        _evidence(record, "unknown", (2, 3, 13, 14, 15, 16, 17, 18), path)

    frequency = _object(profile["frequency_model"], EVIDENCE_KEYS | {"id", "formula", "a4_hz", "anchor_tone_id", "unit"}, "frequency_model")
    _constant(frequency["id"], "12tet-a4-440-v1", "frequency_model.id")
    _constant(frequency["formula"], "440 * 2**((tone_id - 46) / 12)", "frequency_model.formula")
    _constant(frequency["unit"], "Hz", "frequency_model.unit")
    _nominal_number(frequency["a4_hz"], 440.0, 1.0, 20000.0, "frequency_model.a4_hz")
    _constant(frequency["anchor_tone_id"], 46, "frequency_model.anchor_tone_id")
    _evidence(frequency, "proposed", (61, 62, 63, 64, 65, 66, 94, 98), "frequency_model")

    field_metadata = _object(profile["source_fields"], {"frequency_hz", "peak_amplitude", "base_phase_turns"}, "source_fields")
    for field, unit, evidence, pages in (
        ("frequency_hz", "Hz", "derived", (61, 62, 63, 64, 65, 66, 94, 98)),
        ("peak_amplitude", "normalized_peak", "proposed", (67, 68, 69, 70, 91, 92, 93, 94)),
        ("base_phase_turns", "turns", "proposed", (63, 64, 65, 66, 87, 88, 89, 90)),
    ):
        path = f"source_fields.{field}"
        record = _object(field_metadata[field], EVIDENCE_KEYS | {"unit"}, path)
        _constant(record["unit"], unit, f"{path}.unit")
        _evidence(record, evidence, pages, path)

    sources = _array(profile["sources"], 91, "sources")
    for index, entry in enumerate(sources):
        path = f"sources[{index}]"
        source = _object(entry, {"tone_id", "frequency_hz", "peak_amplitude", "base_phase_turns"}, path)
        tone = _integer(source["tone_id"], 1, 91, f"{path}.tone_id")
        if tone != index + 1:
            _fail(f"{path}.tone_id", f"expected unique ordered tone ID {index + 1}")
        _nominal_number(source["frequency_hz"], nominal_frequency(tone), 1.0, 22049.0, f"{path}.frequency_hz")
        _nominal_number(source["peak_amplitude"], 1.0, 0.0, 1.0, f"{path}.peak_amplitude")
        _nominal_number(source["base_phase_turns"], 0.0, 0.0, math.nextafter(1.0, 0.0), f"{path}.base_phase_turns")

    mapping = _object(profile["manual_map"], EVIDENCE_KEYS | {
        "algorithm", "key_domain", "tone_domain", "drawbar_order", "offsets",
        "independent_factory_verification", "tone_ids",
    }, "manual_map")
    for field, expected in (("algorithm", "atlas-manual-foldback-v1"),
                            ("key_domain", "one_based_playing_key_1_61"),
                            ("tone_domain", "one_based_tone_id_1_91"),
                            ("independent_factory_verification", False)):
        _constant(mapping[field], expected, f"manual_map.{field}")
    for field, expected in (("drawbar_order", DRAWBAR_ORDER), ("offsets", DRAWBAR_OFFSETS)):
        values = _array(mapping[field], 9, f"manual_map.{field}")
        for index, value in enumerate(values):
            _constant(value, expected[index], f"manual_map.{field}[{index}]")
    _evidence(mapping, "derived", (98, 99, 102), "manual_map")
    rows = _array(mapping["tone_ids"], 61, "manual_map.tone_ids")
    for index, row in enumerate(rows):
        path = f"manual_map.tone_ids[{index}]"
        _array(row, 9, path)
        for drawbar, tone in enumerate(row):
            _integer(tone, 13, 91, f"{path}[{drawbar}]")
        if row != nominal_manual_row(index + 1):
            _fail(path, f"does not match atlas foldback for playing key {index + 1}")

    gains = _object(profile["drawbar_gains"], EVIDENCE_KEYS | {"model", "unit", "values"}, "drawbar_gains")
    _constant(gains["model"], "nominal-3db-steps-v1", "drawbar_gains.model")
    _constant(gains["unit"], "dimensionless", "drawbar_gains.unit")
    _evidence(gains, "proposed", (109, 110, 111, 112, 113, 114), "drawbar_gains")
    for position, gain in enumerate(_array(gains["values"], 9, "drawbar_gains.values")):
        _nominal_number(gain, nominal_drawbar_gain(position), 0.0, 1.0, f"drawbar_gains.values[{position}]")

    output = _object(profile["output_gain"], EVIDENCE_KEYS | {"value", "unit"}, "output_gain")
    _constant(output["unit"], "dimensionless", "output_gain.unit")
    _evidence(output, "proposed", (109, 110, 111, 112, 113, 114), "output_gain")
    _nominal_number(output["value"], 0.03, 0.0, 1.0, "output_gain.value")

    boundaries = _object(profile["model_boundaries"], set(MODEL_BOUNDARIES), "model_boundaries")
    for field, expected in MODEL_BOUNDARIES.items():
        _constant(boundaries[field], expected, f"model_boundaries.{field}")
    if len(_canonical_bytes(profile)) > MAX_INPUT_BYTES:
        _fail("profile", f"canonical representation exceeds {MAX_INPUT_BYTES} bytes")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ProfileError(f"duplicate JSON object key {key!r}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ProfileError(f"nonfinite JSON number {value!r} is forbidden")


def load_profile(path: str | os.PathLike[str]) -> dict:
    """Read at most MAX_INPUT_BYTES UTF-8 bytes and return a validated profile."""
    try:
        with Path(path).open("rb") as source:
            raw = source.read(MAX_INPUT_BYTES + 1)
    except (OSError, ValueError) as error:
        raise ProfileError(f"cannot read input {path}: {error}") from error
    if len(raw) > MAX_INPUT_BYTES:
        raise ProfileError(f"input exceeds {MAX_INPUT_BYTES} byte limit")
    try:
        profile = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object,
                             parse_constant=_reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError, ValueError) as error:
        if isinstance(error, ProfileError):
            raise
        raise ProfileError(f"invalid UTF-8 JSON: {error}") from error
    validate_profile(profile)
    return profile


def _canonical_bytes(profile: dict) -> bytes:
    return json.dumps(profile, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def canonical_json(profile: dict) -> bytes:
    """Return validated canonical authoring bytes under this project's convention."""
    validate_profile(profile)
    return _canonical_bytes(profile)


def authoring_sha256(profile: dict) -> str:
    """The lowercase SHA-256 of canonical authoring bytes, including metadata."""
    return hashlib.sha256(canonical_json(profile)).hexdigest()


def _decimal(value: int | float) -> str:
    return repr(float(value))


def compile_profile(profile: dict) -> str:
    """Return a complete validated .b3p string; no I/O and no input mutation."""
    validate_profile(profile)
    digest = hashlib.sha256(_canonical_bytes(profile)).hexdigest()
    lines = [
        "B3PROFILE 1",
        f"profile_id {PROFILE_ID}",
        f"authoring_sha256 {digest}",
        f"output_gain {_decimal(profile['output_gain']['value'])}",
        "drawbar_gains " + " ".join(_decimal(value) for value in profile["drawbar_gains"]["values"]),
        "sources 91",
    ]
    for source in profile["sources"]:
        lines.append(f"{source['tone_id']} " + " ".join(_decimal(source[field]) for field in
                     ("frequency_hz", "peak_amplitude", "base_phase_turns")))
    lines.append("manual_map 61 9")
    lines.extend(" ".join(str(tone) for tone in row) for row in profile["manual_map"]["tone_ids"])
    lines.append("end")
    result = "\n".join(lines) + "\n"
    if len(result.encode("utf-8")) > MAX_OUTPUT_BYTES:
        raise ProfileError(f"compiled output exceeds {MAX_OUTPUT_BYTES} byte limit")
    return result


def _atomic_write(path: Path, payload: bytes) -> None:
    """Replace only after a fully written, flushed temporary sibling is ready."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", prefix=f".{path.name}.", suffix=".tmp",
                                         dir=path.parent, delete=False) as target:
            temporary = Path(target.name)
            target.write(payload)
            target.flush()
            os.fsync(target.fileno())
        os.replace(temporary, path)
        temporary = None
    except OSError as error:
        raise ProfileError(f"cannot write output {path}: {error}") from error
    finally:
        if temporary is not None:
            try:
                temporary.unlink()
            except OSError:
                pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--input", required=True, type=Path, help="UTF-8 authoring JSON")
    parser.add_argument("--output", type=Path, help="compiled .b3p file (required unless --check)")
    parser.add_argument("--check", action="store_true", help="validate without writing; if --output is supplied, require identical existing bytes")
    args = parser.parse_args(argv)
    if not args.check and args.output is None:
        parser.error("--output is required unless --check is specified")
    try:
        if args.output is not None:
            if args.input.resolve() == args.output.resolve():
                raise ProfileError("input and output paths must be different")
            if args.output.exists() and os.path.samefile(args.input, args.output):
                raise ProfileError("input and output must not refer to the same file")
        profile = load_profile(args.input)
        compiled = compile_profile(profile).encode("utf-8")
        digest = hashlib.sha256(_canonical_bytes(profile)).hexdigest()
        if args.check and args.output is not None:
            with args.output.open("rb") as output:
                existing = output.read(MAX_OUTPUT_BYTES + 1)
            if existing != compiled:
                raise ProfileError(f"compiled output {args.output} is stale or different")
        elif not args.check:
            _atomic_write(args.output, compiled)
        action = "checked" if args.check else "compiled"
        print(f"{action} {PROFILE_ID}; authoring_sha256 {digest}")
    except (ProfileError, OSError, RuntimeError) as error:
        print(f"profile error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
