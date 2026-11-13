#!/usr/bin/env python3
"""Admit the named atlas scanner graph and emit deterministic SI JSON or C++.

This is an offline compiler for one documentary nominal fixture, not a general
circuit authoring format or a measured instrument profile. Unknown physical
values remain null; ideal boundaries are explicit approximations.

Public API: load_profile(path) -> validated authoring dict;
load_profile_with_digest(path) -> (validated dict, SHA-256 of the same bytes);
validate_profile(dict) -> the same dict, without mutation;
normalized_profile(dict) -> independent SI representation;
compile_profile(path, output_format="json") -> output text.
Failures raise ScannerProfileError. CLI output is published atomically only
after complete admission; rejected inputs preserve any previous destination.
"""

from __future__ import annotations

import argparse
import copy
from decimal import Decimal, InvalidOperation, localcontext
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import sys
import tempfile


MAX_INPUT_BYTES = 256 * 1024
MAX_OUTPUT_BYTES = 256 * 1024
MAX_STRING_LENGTH = 512
MAX_DEPTH = 12
MAX_VALUES = 4096
MODEL_ID = "atlas-late-b3-nominal-line-v1"
ATLAS_SHA256 = "4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769"
ATLAS_PATH = "Hammond_B3_Leslie_Research_Atlas_500pp.pdf"
NODES = ("g", *(f"p{k}" for k in range(19)), "r", *(f"d{k}" for k in range(1, 7)))
UPPER = ("27", "56", "39", "33", "18", "12")
LOWER = (("68", "kOhm"), ("0.15", "MOhm"), ("0.15", "MOhm"),
         ("0.18", "MOhm"), ("0.18", "MOhm"), ("0.18", "MOhm"))
SI_UNITS = {"L": "H", "C": "F", "R": "ohm"}
UNIT_SCALES = {"mH": "0.001", "uF": "0.000001", "kOhm": "1000", "MOhm": "1000000"}
COMPONENT_SOURCE = {"pages": [157, 158], "evidence_class": "documentary-nominal",
                    "uncertainty": "not-supplied"}
ASSUMPTION_IDS = ("ideal-coils", "ideal-drive", "unloaded-tap-observation")
UNKNOWN_UNITS = {
    "winding-resistance": "ohm", "mutual-inductance": "H", "stray-capacitance": "F",
    "drive-impedance": "ohm", "receiver-loading": "ohm",
    "scanner-coupling-capacitance": "F", "normalized-signal-scale": "V",
    "specimen-revision": "identifier",
}


class ScannerProfileError(ValueError):
    """The source is not the admitted bounded nominal scanner fixture."""


def expected_components() -> list[dict]:
    """The fixed reviewed identity; independent tests must use their own edges."""
    result = []

    def add(name: str, kind: str, positive: str, negative: str,
            magnitude: str, unit: str) -> None:
        result.append({"id": name, "kind": kind, "positive": positive,
                       "negative": negative,
                       "value": {"magnitude": magnitude, "unit": unit,
                                 "printed": f"{magnitude} {unit}"},
                       "source": copy.deepcopy(COMPONENT_SOURCE)})

    for k in range(1, 19):
        add(f"L{k}", "L", f"p{k - 1}", f"p{k}", "500", "mH")
    for k in range(1, 19):
        add(f"C{k}", "C", f"p{k}", "r", "0.001" if k == 18 else "0.004", "uF")
    for k in range(1, 7):
        add(f"R{k}+", "R", f"p{k - 1}", f"d{k}", UPPER[k - 1], "kOhm")
        add(f"R{k}-", "R", f"d{k}", "r", *LOWER[k - 1])
    add("Rc", "R", "r", "g", "22", "kOhm")
    add("Rt", "R", "p18", "r", "15", "kOhm")
    return result


def expected_outputs() -> list[dict]:
    return [{"id": f"v{k}", "positive": f"d{k}" if k <= 6 else f"p{k - 1}",
             "negative": "g", "source_pages": [158]} for k in range(1, 20)]


def _keys(value: object, expected: set[str], label: str) -> dict:
    if type(value) is not dict or set(value) != expected:
        raise ScannerProfileError(f"{label}: expected exactly {sorted(expected)}")
    return value


def _bounded(value: object) -> None:
    count = 0
    active: set[int] = set()

    def visit(item: object, depth: int) -> None:
        nonlocal count
        count += 1
        if count > MAX_VALUES or depth > MAX_DEPTH:
            raise ScannerProfileError("profile exceeds nesting/value-count bounds")
        if type(item) is str:
            if len(item) > MAX_STRING_LENGTH or any(ord(c) < 32 for c in item):
                raise ScannerProfileError("profile contains an oversized or control-character string")
        elif type(item) is int:
            if not -1_000_000 <= item <= 1_000_000:
                raise ScannerProfileError("profile integer exceeds bounds")
        elif type(item) is float:
            if not math.isfinite(item):
                raise ScannerProfileError("profile contains a nonfinite number")
            raise ScannerProfileError("authoring numbers must be integer metadata or decimal strings")
        elif item is None:
            return
        elif type(item) in (list, dict):
            identity = id(item)
            if identity in active or len(item) > 128:
                raise ScannerProfileError("profile contains a cycle or oversized collection")
            active.add(identity)
            if type(item) is dict:
                for key, child in item.items():
                    if type(key) is not str:
                        raise ScannerProfileError("profile object keys must be strings")
                    visit(key, depth + 1)
                    visit(child, depth + 1)
            else:
                for child in item:
                    visit(child, depth + 1)
            active.remove(identity)
        else:
            # bool must not satisfy an integer field; no authoring field is boolean.
            raise ScannerProfileError(f"unsupported authoring type {type(item).__name__}")

    visit(value, 0)


def _records(value: object, count: int, label: str) -> dict[str, dict]:
    if type(value) is not list or len(value) != count:
        raise ScannerProfileError(f"{label}: expected exactly {count} records")
    result = {}
    for record in value:
        if type(record) is not dict or type(record.get("id")) is not str:
            raise ScannerProfileError(f"{label}: every record needs a string id")
        name = record["id"]
        if name in result:
            raise ScannerProfileError(f"{label}: duplicate id {name!r}")
        result[name] = record
    return result


def validate_profile(profile: dict) -> dict:
    """Validate the complete named graph; return the original without changing it."""
    _bounded(profile)
    _keys(profile, {"schema_version", "model_id", "evidence_class", "variant", "source",
                    "ground", "nodes", "components", "outputs", "drive", "return_switch",
                    "assumptions", "unknowns"}, "profile")
    if type(profile["schema_version"]) is not int or profile["schema_version"] != 1:
        raise ScannerProfileError("schema_version must be integer 1")
    if (profile["model_id"] != MODEL_ID or profile["evidence_class"] != "documentary-reconstruction"
            or profile["variant"] != "atlas-late-b3-paper-model"):
        raise ScannerProfileError("model identity/evidence class/variant differs from this fixture")
    source = _keys(profile["source"], {"document", "sha256", "values_pages", "topology_pages"}, "source")
    if source != {"document": ATLAS_PATH, "sha256": ATLAS_SHA256,
                  "values_pages": [157], "topology_pages": [158, 175, 182]}:
        raise ScannerProfileError("source must retain the exact atlas identity and locators")
    if (profile["ground"] != "g" or type(profile["nodes"]) is not list
            or len(profile["nodes"]) != 27 or any(type(n) is not str for n in profile["nodes"])
            or set(profile["nodes"]) != set(NODES)):
        raise ScannerProfileError("nodes must contain the 27 distinct reviewed nodes and datum g")
    components = _records(profile["components"], 50, "components")
    expected = expected_components()
    if set(components) != {item["id"] for item in expected}:
        raise ScannerProfileError("component identities differ from 18 L, 18 C and 14 R")
    for wanted in expected:
        actual = _keys(components[wanted["id"]], set(wanted), f"component {wanted['id']}")
        value = _keys(actual["value"], {"magnitude", "unit", "printed"}, f"{wanted['id']} value")
        if (type(value["magnitude"]) is not str
                or re.fullmatch(r"(?:0|[1-9][0-9]{0,6})(?:\.[0-9]{1,9})?", value["magnitude"]) is None):
            raise ScannerProfileError(f"{wanted['id']}: magnitude must be a bounded decimal string")
        try:
            number = Decimal(value["magnitude"])
        except InvalidOperation as error:
            raise ScannerProfileError(f"{wanted['id']}: invalid decimal") from error
        if not number.is_finite() or number <= 0:
            raise ScannerProfileError(f"{wanted['id']}: magnitude must be finite and positive")
        _keys(actual["source"], set(COMPONENT_SOURCE), f"{wanted['id']} source")
        if actual != wanted:
            raise ScannerProfileError(f"{wanted['id']}: endpoint, kind, printed value/unit or source differs")
    outputs = _records(profile["outputs"], 19, "outputs")
    if set(outputs) != {f"v{k}" for k in range(1, 20)}:
        raise ScannerProfileError("output identities must be v1 through v19")
    for wanted in expected_outputs():
        if outputs[wanted["id"]] != wanted:
            raise ScannerProfileError(f"{wanted['id']}: expected the reviewed ground-referenced signed tap")
    if profile["drive"] != {"id": "Vin", "kind": "ideal-voltage-source", "positive": "p0",
                             "negative": "g", "quantity": "volts"}:
        raise ScannerProfileError("drive must be the separate ideal Vin boundary from p0 to g")
    if profile["return_switch"] != {"id": "Sreturn", "positive": "r", "negative": "g",
                                     "states": {"vibrato": "closed", "chorus": "open"},
                                     "closed_model": "node-contraction"}:
        raise ScannerProfileError("return switch must constrain r=g in vibrato and open in chorus")
    assumptions = _records(profile["assumptions"], 3, "assumptions")
    if set(assumptions) != set(ASSUMPTION_IDS):
        raise ScannerProfileError("the three named ideal boundary assumptions are required")
    for name, item in assumptions.items():
        _keys(item, {"id", "status", "description", "source_pages", "replacement"}, f"assumption {name}")
        if (item["status"] != "ideal-approximation" or item["source_pages"] != [158, 161, 165]
                or not _text(item["description"]) or not _text(item["replacement"])):
            raise ScannerProfileError(f"assumption {name}: explicit approximation and replacement required")
    unknowns = _records(profile["unknowns"], len(UNKNOWN_UNITS), "unknowns")
    if set(unknowns) != set(UNKNOWN_UNITS):
        raise ScannerProfileError("all eight unresolved physical quantities must remain explicit")
    for name, item in unknowns.items():
        _keys(item, {"id", "status", "value", "unit", "reason", "acquisition"}, f"unknown {name}")
        if (item["status"] != "unknown" or item["value"] is not None
                or item["unit"] != UNKNOWN_UNITS[name]
                or not _text(item["reason"]) or not _text(item["acquisition"])):
            raise ScannerProfileError(f"unknown {name}: null value, units, reason and acquisition are required")
    return profile


def _text(value: object) -> bool:
    return type(value) is str and bool(value.strip()) and len(value) <= MAX_STRING_LENGTH


def _unique(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ScannerProfileError(f"duplicate JSON object key {key!r}")
        result[key] = value
    return result


def _reject_constant(token: str) -> None:
    raise ScannerProfileError(f"nonfinite JSON token {token!r}")


def _read(path: Path) -> bytes:
    descriptor = None
    try:
        # Nonblocking open avoids waiting on a FIFO substituted before fstat.
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NONBLOCK", 0))
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_INPUT_BYTES:
            raise ScannerProfileError(f"input must be a regular file <= {MAX_INPUT_BYTES} bytes")
        with os.fdopen(descriptor, "rb") as stream:
            descriptor = None
            payload = stream.read(MAX_INPUT_BYTES + 1)
            after = os.fstat(stream.fileno())
        identity = lambda item: (item.st_dev, item.st_ino, item.st_size, item.st_mtime_ns, item.st_ctime_ns)
        if identity(before) != identity(after) or len(payload) != before.st_size:
            raise ScannerProfileError("input changed during bounded read")
        if len(payload) > MAX_INPUT_BYTES:
            raise ScannerProfileError("input exceeds byte bound")
        return payload
    except (OSError, ValueError) as error:
        raise ScannerProfileError(f"cannot read scanner profile: {error}") from error
    finally:
        if descriptor is not None:
            os.close(descriptor)


def _parse(payload: bytes) -> dict:
    try:
        profile = json.loads(payload.decode("utf-8"), object_pairs_hook=_unique,
                             parse_constant=_reject_constant)
        return validate_profile(profile)
    except ScannerProfileError:
        raise
    except (UnicodeError, ValueError, RecursionError) as error:
        raise ScannerProfileError(f"invalid bounded UTF-8 JSON: {error}") from error


def load_profile(path: str | Path) -> dict:
    return _parse(_read(Path(path)))


def load_profile_with_digest(path: str | Path) -> tuple[dict, str]:
    payload = _read(Path(path))
    return _parse(payload), hashlib.sha256(payload).hexdigest()


def normalized_profile(profile: dict) -> dict:
    """Convert each admitted printed value once; preserve its printed provenance."""
    validate_profile(profile)
    result = copy.deepcopy(profile)
    result["representation"] = "scanner-line-si-v1"
    result["nodes"] = list(NODES)
    indexed = {item["id"]: item for item in result["components"]}
    result["components"] = [indexed[item["id"]] for item in expected_components()]
    outputs = {item["id"]: item for item in result["outputs"]}
    result["outputs"] = [outputs[f"v{k}"] for k in range(1, 20)]
    result["assumptions"].sort(key=lambda item: ASSUMPTION_IDS.index(item["id"]))
    result["unknowns"].sort(key=lambda item: tuple(UNKNOWN_UNITS).index(item["id"]))
    with localcontext() as context:
        context.prec = 40
        for item in result["components"]:
            value = item["value"]
            si = float(Decimal(value["magnitude"]) * Decimal(UNIT_SCALES[value["unit"]]))
            item["value"] = {"si_value": si, "si_unit": SI_UNITS[item["kind"]],
                             "printed": value["printed"], "printed_unit": value["unit"],
                             "printed_magnitude": value["magnitude"]}
    return result


def _header(profile: dict, authoring_sha256: str) -> str:
    components = {item["id"]: item["value"]["si_value"] for item in profile["components"]}

    def array(name: str, names: list[str]) -> str:
        values = ", ".join(repr(components[key]) for key in names)
        return f"inline constexpr std::array<double, {len(names)}> {name}{{{values}}};\n"

    return ("// Generated by compile_scanner_line.py. Do not edit.\n"
            "// Documentary nominal graph; no measured-hardware claim.\n#pragma once\n\n"
            "#include <array>\n#include <string_view>\n\nnamespace hammond::scanner_generated {\n\n"
            f"inline constexpr std::string_view kModelId = {json.dumps(MODEL_ID)};\n"
            f"inline constexpr std::string_view kAuthoringSha256 = {json.dumps(authoring_sha256)};\n"
            + array("kInductancesH", [f"L{k}" for k in range(1, 19)])
            + array("kCapacitancesF", [f"C{k}" for k in range(1, 19)])
            + array("kDividerUpperOhms", [f"R{k}+" for k in range(1, 7)])
            + array("kDividerLowerOhms", [f"R{k}-" for k in range(1, 7)])
            + f"inline constexpr double kReturnOhms = {components['Rc']!r};\n"
            + f"inline constexpr double kTerminationOhms = {components['Rt']!r};\n\n"
            + "} // namespace hammond::scanner_generated\n")


def compile_profile(path: str | Path, output_format: str = "json") -> str:
    if output_format not in ("json", "header"):
        raise ScannerProfileError("output format must be json or header")
    profile, digest = load_profile_with_digest(path)
    normalized = normalized_profile(profile)
    if output_format == "header":
        return _header(normalized, digest)
    normalized["authoring_sha256"] = digest
    return json.dumps(normalized, ensure_ascii=True, allow_nan=False, indent=2) + "\n"


def write_output(path: str | Path, text: str, input_path: str | Path) -> None:
    """Atomically replace a regular output; never overwrite/alias the source."""
    target, source = Path(path), Path(input_path)
    temporary = None
    try:
        payload = text.encode("utf-8")
        if len(payload) > MAX_OUTPUT_BYTES:
            raise ScannerProfileError("compiled output exceeds byte bound")
        if target.resolve() == source.resolve():
            raise ScannerProfileError("output must not replace its authoring input")
        if target.exists() or target.is_symlink():
            if not stat.S_ISREG(target.lstat().st_mode) or os.path.samefile(target, source):
                raise ScannerProfileError("output must be a separate regular file, not a link or input alias")
        descriptor, name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=target.parent)
        temporary = Path(name)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
        temporary = None
    except ScannerProfileError:
        raise
    except (OSError, UnicodeError, RuntimeError, ValueError) as error:
        raise ScannerProfileError(f"cannot publish scanner output: {error}") from error
    finally:
        if temporary is not None:
            try:
                temporary.unlink()
            except OSError:
                pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--format", choices=("json", "header"), default="json")
    args = parser.parse_args(argv)
    try:
        text = compile_profile(args.input, args.format)
        write_output(args.output, text, args.input)
        return 0
    except ScannerProfileError as error:
        print(f"scanner profile rejected: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
