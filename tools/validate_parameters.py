#!/usr/bin/env python3
"""Strict, standard-library validator for the proposed internal console registry.

This checks one named 43-parameter engineering model, not VST3 exports or the
absent atlas companion. File parsing, validation and conversion run off the
audio thread. Validation never modifies its argument. Public functions reject
malformed input with ParameterError (a ValueError subclass).
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
from typing import Any


SCHEMA_VERSION = 2
MODEL = "exclusive-ab-percussion-console-v2"
SCOPE = "implemented-console-subset"
STATUS = "proposed-internal"
PARAMETER_COUNT = 43
UINT32_MAX = (1 << 32) - 1
MAX_INPUT_BYTES = 256 * 1024
DEFAULT_REGISTRY_PATH = Path(__file__).resolve().parents[1] / "data" / "parameter-registry.json"
FOOTAGES = ("16ft", "5_1/3ft", "8ft", "4ft", "2_2/3ft", "2ft", "1_3/5ft", "1_1/3ft", "1ft")
BANK_BASES = (("upper", "A", 4096), ("upper", "B", 4112),
              ("lower", "A", 4128), ("lower", "B", 4144))
PROVENANCE = {
    "evidence_class": "proposed",
    "applicable_variant": "nominal B-3/AO-28 console engineering subset",
    "atlas_file": "Hammond_B3_Leslie_Research_Atlas_500pp.pdf",
    "atlas_pages": [127, 128, 134, 389, 397, 398, 399, 400, 401, 402, 418],
    "implementation_sources": ["docs/CONSOLE_EXTENSION.md", "docs/CONSOLE_DYNAMICS.md",
                               "include/hammond/ControlState.h", "include/hammond/Percussion.h",
                               "include/hammond/Types.h"],
    "companion_recovered": False,
    "host_exports_verified": False,
    "native_host_curves_implemented": False,
    "uncertainty": None,
    "reason": "Retains all 39 original internal console records unchanged and adds four independent percussion settings. "
              "IDs, binary defaults and conversions are internal engineering choices, not manufacturer calibration. "
              "The absent 62-entry atlas companion was not recovered; no hardware calibration or host mapping is claimed.",
}
ROOT_KEYS = frozenset(("schema_version", "model", "scope", "status", "provenance", "parameters"))
PARAMETER_KEYS = frozenset(("id", "path", "label", "kind", "unit", "minimum", "maximum",
                            "default", "step_count", "normalized", "engine_event",
                            "evidence_class", "source_pages"))
NORMALIZED_KEYS = frozenset(("minimum", "maximum", "default", "to_plain", "to_normalized", "meaning"))
EVENT_KEYS = frozenset(("type", "manual", "index"))


class ParameterError(ValueError):
    """Invalid registry metadata, ID, control value or input file."""


def _fail(path: str, message: str) -> None:
    raise ParameterError(f"{path}: {message}")


def _object(value: Any, keys: frozenset[str], path: str) -> dict:
    if type(value) is not dict:
        _fail(path, "must be an object")
    if any(type(key) is not str for key in value):
        _fail(path, "object keys must be strings")
    unknown, missing = set(value) - keys, keys - set(value)
    if unknown:
        _fail(path, f"unknown field(s): {', '.join(sorted(unknown))}")
    if missing:
        _fail(path, f"missing field(s): {', '.join(sorted(missing))}")
    return value


def _integer(value: Any, low: int, high: int, path: str) -> int:
    if type(value) is not int or not low <= value <= high:
        _fail(path, f"must be an integer in [{low}, {high}]; booleans are not integers")
    return value


def _number(value: Any, path: str) -> float:
    if type(value) not in (int, float):
        _fail(path, "must be a finite number; booleans are not numbers")
    try:
        finite = math.isfinite(value)
    except OverflowError:
        finite = False
    if not finite:
        _fail(path, "must be finite")
    return float(value)


def _matches(value: Any, expected: Any, path: str) -> None:
    """Freeze this version's metadata, including types and all nested keys."""
    if type(expected) is dict:
        _object(value, frozenset(expected), path)
        for key, child in expected.items():
            _matches(value[key], child, f"{path}.{key}")
    elif type(expected) is list:
        if type(value) is not list or len(value) != len(expected):
            _fail(path, f"must contain exactly {len(expected)} entries")
        for index, child in enumerate(expected):
            _matches(value[index], child, f"{path}[{index}]")
    elif type(value) is not type(expected) or value != expected:
        _fail(path, f"must be {expected!r} for {MODEL}")


def _specifications() -> dict[int, dict]:
    """Known internal identities; unrelated to array order or a visible bank."""
    result = {}

    def add(identifier, path, label, kind, unit, maximum, default, steps, meaning, target, pages):
        result[identifier] = {
            "id": identifier, "path": path, "label": label, "kind": kind, "unit": unit,
            "minimum": 0, "maximum": maximum, "default": default, "step_count": steps,
            "normalized": {
                "minimum": 0.0, "maximum": 1.0, "default": default / maximum,
                "to_plain": ("floor(u * 8 + 0.5)" if kind == "drawbar_position" else
                             "floor(u + 0.5)" if kind in ("bank_selector", "percussion_switch") else "u"),
                "to_normalized": "x / 8" if kind == "drawbar_position" else "x",
                "meaning": meaning,
            },
            "engine_event": target, "evidence_class": "proposed", "source_pages": pages,
        }

    for manual, bank, base in BANK_BASES:
        for index, footage in enumerate(FOOTAGES):
            add(base + index, f"manual.{manual}.bank.{bank}.drawbar.{footage}",
                f"{manual.title()} {bank} {footage}", "drawbar_position", "drawbar-position",
                8, 0, 8, "position-fraction-not-amplitude",
                {"type": "bank_drawbar", "manual": manual, "index": (9 if bank == "B" else 0) + index},
                [397, 398, 399, 401, 402])
    add(8192, "global.expression", "Global expression", "expression",
        "normalized-linear-gain-surrogate", 1, 1, 0, "linear-gain-surrogate-not-physical-travel",
        {"type": "expression", "manual": "upper", "index": 0}, [398, 400, 402])
    for manual, identifier in (("upper", 8208), ("lower", 8209)):
        add(identifier, f"manual.{manual}.selected_bank", f"{manual.title()} selected bank",
            "bank_selector", "bank-index-0=A-1=B", 1, 1, 1, "bank-index-fraction",
            {"type": "select_bank", "manual": manual, "index": 0}, [389, 397, 401, 402])
    for index, (setting, choices) in enumerate((
            ("enabled", "0=off-1=on"), ("harmonic", "0=second-1=third"),
            ("volume", "0=normal-1=soft"), ("decay", "0=slow-1=fast"))):
        add(12288 + index, f"percussion.{setting}", f"Percussion {setting}",
            "percussion_switch", f"{setting}-index-{choices}", 1, 0, 1,
            "percussion-setting-index-fraction",
            {"type": "percussion", "manual": "upper", "index": index},
            [127, 128, 134, 397, 398, 401, 402, 418])
    return result


_EXPECTED = _specifications()


def _validate_parameter(parameter: Any, path: str) -> None:
    _object(parameter, PARAMETER_KEYS, path)
    identifier = _integer(parameter["id"], 0, UINT32_MAX, f"{path}.id")
    if identifier not in _EXPECTED:
        _fail(f"{path}.id", "not a defined ID in this console subset")
    minimum = _number(parameter["minimum"], f"{path}.minimum")
    maximum = _number(parameter["maximum"], f"{path}.maximum")
    default = _number(parameter["default"], f"{path}.default")
    if not minimum < maximum or not minimum <= default <= maximum:
        _fail(path, "requires minimum < maximum and a default inside the domain")
    _integer(parameter["step_count"], 0, UINT32_MAX, f"{path}.step_count")
    normalized = _object(parameter["normalized"], NORMALIZED_KEYS, f"{path}.normalized")
    for key in ("minimum", "maximum", "default"):
        value = _number(normalized[key], f"{path}.normalized.{key}")
        if not 0.0 <= value <= 1.0:
            _fail(f"{path}.normalized.{key}", "must be in [0, 1]")
    target = _object(parameter["engine_event"], EVENT_KEYS, f"{path}.engine_event")
    _integer(target["index"], 0, 255, f"{path}.engine_event.index")
    # This freezes ranges/defaults, the permanent bank target, units, provenance
    # and the conversion meaning. A gain law cannot replace drawbar position.
    _matches(parameter, _EXPECTED[identifier], path)


def validate_registry(registry: Any) -> None:
    """Validate only the version-2 subset without changes; record order is free.

    Version-1 registry documents are intentionally rejected. Their 39 parameter
    records retain their exact identity and meaning within this extended model;
    registry metadata is not the separately migrated B3CONTROLS save format.
    """
    _object(registry, ROOT_KEYS, "registry")
    for key, expected in (("schema_version", SCHEMA_VERSION), ("model", MODEL),
                          ("scope", SCOPE), ("status", STATUS)):
        _matches(registry[key], expected, f"registry.{key}")
    _matches(registry["provenance"], PROVENANCE, "registry.provenance")
    parameters = registry["parameters"]
    if type(parameters) is not list or len(parameters) != PARAMETER_COUNT:
        _fail("registry.parameters", f"must contain exactly {PARAMETER_COUNT} records")
    ids, paths, targets = set(), set(), set()
    for index, parameter in enumerate(parameters):
        path = f"registry.parameters[{index}]"
        _validate_parameter(parameter, path)
        identifier, semantic_path = parameter["id"], parameter["path"]
        event = parameter["engine_event"]
        target = (event["type"], event["manual"], event["index"])
        if identifier in ids or semantic_path in paths or target in targets:
            _fail(path, "duplicate parameter ID, semantic path or engine target")
        ids.add(identifier)
        paths.add(semantic_path)
        targets.add(target)
    if ids != set(_EXPECTED):
        _fail("registry.parameters", "must contain every required console identity exactly once")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            _fail("JSON", f"duplicate key {key!r}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    _fail("JSON", f"nonfinite constant {value!r} is forbidden")


def load_registry(path: str | Path = DEFAULT_REGISTRY_PATH) -> dict:
    """Read bounded UTF-8 JSON, reject duplicate keys, then validate fully."""
    try:
        with Path(path).open("rb") as source:
            payload = source.read(MAX_INPUT_BYTES + 1)
        if len(payload) > MAX_INPUT_BYTES:
            _fail("registry file", f"exceeds {MAX_INPUT_BYTES} bytes")
        registry = json.loads(payload.decode("utf-8"), object_pairs_hook=_unique_object,
                              parse_constant=_reject_constant)
        validate_registry(registry)
        return registry
    except ParameterError:
        raise
    except (OSError, UnicodeError, ValueError, RecursionError) as error:
        raise ParameterError(f"registry file: {error}") from error


def normalized_to_value(parameter: dict, normalized: float) -> int | float:
    """Convert a finite normalized scalar; reject instead of clipping.

    Discrete rounding is exact for the supplied binary64 value. Integer-ratio
    arithmetic avoids rounding a float immediately below a half-step upward
    during an intermediate floating-point addition of 0.5.
    """
    _validate_parameter(parameter, "parameter")
    value = _number(normalized, "normalized")
    if not 0.0 <= value <= 1.0:
        _fail("normalized", "must be in [0, 1]")
    steps = parameter["step_count"]
    if steps:
        numerator, denominator = value.as_integer_ratio()
        return (2 * numerator * steps + denominator) // (2 * denominator)
    return value


def value_to_normalized(parameter: dict, value: int | float) -> float:
    """Encode a valid plain value; discrete inputs must be integer-valued."""
    _validate_parameter(parameter, "parameter")
    plain = _number(value, "value")
    minimum, maximum = parameter["minimum"], parameter["maximum"]
    if not minimum <= plain <= maximum:
        _fail("value", f"must be in [{minimum}, {maximum}]")
    if parameter["step_count"] and not plain.is_integer():
        _fail("value", "must be an integer-valued discrete control")
    return (plain - minimum) / (maximum - minimum)


def normalized_to_event(registry: dict, parameter_id: int, normalized: float) -> dict:
    """Return an untimed event payload with a permanent target, without dispatch.

    No selected/visible bank is an input. The caller owns event timing; this
    scalar helper does not implement sample-accurate native automation curves.
    """
    validate_registry(registry)
    identifier = _integer(parameter_id, 0, UINT32_MAX, "parameter_id")
    for parameter in registry["parameters"]:
        if parameter["id"] == identifier:
            return {**parameter["engine_event"], "value": normalized_to_value(parameter, normalized)}
    _fail("parameter_id", "not a defined ID in this console subset")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("registry", nargs="?", type=Path, default=DEFAULT_REGISTRY_PATH)
    args = parser.parse_args(argv)
    try:
        load_registry(args.registry)
    except ParameterError as error:
        print(f"parameter registry validation failed: {error}", file=sys.stderr)
        return 1
    print(f"Validated {PARAMETER_COUNT} proposed internal parameters for {MODEL}; host mapping remains pending.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
