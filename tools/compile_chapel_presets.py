#!/usr/bin/env python3
"""Admit the independently transcribed atlas chapel matrix as deterministic JSON.

This offline documentary catalog changes no Engine, parameter, state or latch.
compile_chapel_presets(input_path, review_a_path, review_b_path) returns UTF-8
JSON text; write_compiled_catalog(output, text, inputs) atomically publishes text
returned by that compiler. Failures raise ChapelCompileError. The destination's
parent must already exist. Ordinary failure preserves inputs and prior output;
concurrent hostile filesystem mutation and power-loss durability are not promised.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
from typing import Any


MODEL_ID = "atlas-chapel-nominal-v1"
CATALOG_FORMAT = "hammond-chapel-catalog-v1"
SCHEMA_VERSION = 1
MAX_AUTHORING_BYTES = 64 * 1024
MAX_REVIEW_BYTES = 16 * 1024
MAX_OUTPUT_BYTES = 64 * 1024
ATLAS_SHA256 = "4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769"
REVIEW_SHA256 = "dc2a8fd4e9750133c982bb42fd6cc7c12908f011154826035bb623f52d8de694"
REVIEW_HEADER = ("manual", "preset_key", "preset_name", "drawbars", "page")
PRESET_KEYS = ("C#", "D", "D#", "E", "F", "F#", "G", "G#", "A")
FOOTAGES_FT = ("16", "5 1/3", "8", "4", "2 2/3", "2", "1 3/5", "1 1/3", "1")
LEAD_COLORS = ("brown", "red", "orange", "yellow", "green", "blue", "violet", "gray", "white")
UPPER_TAPS = (
    "005320000", "004432000", "008740000", "004544222", "005403000",
    "004675300", "005644320", "006876540", "327645222",
)
LOWER_TAPS = (
    "004545440", "004423220", "007373430", "004544220", "006644322",
    "005642200", "006845433", "008030000", "427866244",
)


class ChapelCompileError(ValueError):
    """A source-admission, bounded-file or atomic-publication failure."""


def _authoring_spec() -> dict[str, Any]:
    """The one admitted documentary model; no measured values are synthesized."""
    return {
        "schema_version": SCHEMA_VERSION,
        "model_id": MODEL_ID,
        "evidence_class": "documentary-reconstruction",
        "applicable_variant": "atlas-approved-chapel-arrangement",
        "source": {
            "document": "Hammond_B3_Leslie_Research_Atlas_500pp.pdf",
            "sha256": ATLAS_SHA256,
            "page": 122,
            "primary_reference": {
                "citation": "S019-01",
                "table": "Table IV",
                "printed_page": "4-1",
                "status": "not-independently-verified",
            },
        },
        "tap_units": "discrete-transformer-tap-index",
        "drawbars": [
            {"position": index + 1, "footage_ft": footage, "lead_color": color}
            for index, (footage, color) in enumerate(zip(FOOTAGES_FT, LEAD_COLORS))
        ],
        "registrations": [
            {"manual": manual, "preset_key": key, "preset_name": None,
             "drawbars": taps, "source_page": 122}
            for manual, rows in (("upper", UPPER_TAPS), ("lower", LOWER_TAPS))
            for key, taps in zip(PRESET_KEYS, rows)
        ],
        "limitations": {
            "registration_names": "not-published-in-atlas-table",
            "specimen_wiring": "unverified",
            "loaded_tap_gains": "unmeasured-not-modeled",
            "physical_latch": "not-modeled",
            "percussion_interlock": "not-modeled",
        },
    }


def _expect(actual: Any, expected: Any, location: str) -> None:
    # Exact scalar types matter: bool and float must not stand in for integers.
    if type(actual) is not type(expected):
        raise ChapelCompileError(f"{location}: expected {type(expected).__name__}")
    if type(expected) is dict:
        if any(type(name) is not str for name in actual):
            raise ChapelCompileError(f"{location}: object member names must be strings")
        missing = set(expected) - set(actual)
        extra = set(actual) - set(expected)
        if missing or extra:
            raise ChapelCompileError(
                f"{location}: missing fields {sorted(missing)!r}; unknown fields {sorted(extra)!r}")
        for name, value in expected.items():
            _expect(actual[name], value, f"{location}.{name}")
    elif type(expected) is list:
        if len(actual) != len(expected):
            raise ChapelCompileError(f"{location}: expected exactly {len(expected)} ordered entries")
        for index, (value, target) in enumerate(zip(actual, expected)):
            _expect(value, target, f"{location}[{index}]")
    elif actual != expected:
        raise ChapelCompileError(f"{location}: must equal {expected!r} for {MODEL_ID}")


def validate_authoring(data: Any) -> None:
    """Validate exact fields, types, order, 162 taps, identities and limitations."""
    _expect(data, _authoring_spec(), "authoring")


def _identity(metadata: os.stat_result) -> tuple[int, int, int, int, int]:
    return (metadata.st_dev, metadata.st_ino, metadata.st_size,
            metadata.st_mtime_ns, metadata.st_ctime_ns)


def _same_opened_file(selected: os.stat_result, opened: os.stat_result) -> bool:
    # Windows Python can expose creation time through lstat but change time
    # through fstat. Keep ctime checks within each API; all other fields, and
    # POSIX cross-API ctime, must still agree exactly.
    path_stamp, descriptor_stamp = _identity(selected), _identity(opened)
    return path_stamp[:4] == descriptor_stamp[:4] and (
        os.name == "nt" or path_stamp[4] == descriptor_stamp[4])


def _regular(metadata: os.stat_result) -> bool:
    return stat.S_ISREG(metadata.st_mode) and not (
        getattr(metadata, "st_file_attributes", 0)
        & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    )


def _read(path: Path, limit: int) -> bytes:
    """Read one stable nonsymlink regular file; bound bytes and FIFO admission."""
    try:
        selected = path.lstat()
        if not _regular(selected) or selected.st_size > limit:
            raise ChapelCompileError(f"{path}: requires a nonsymlink regular file of at most {limit} bytes")
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NONBLOCK", 0)
        flags |= getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(path, flags)
        try:
            source = os.fdopen(descriptor, "rb")
        except BaseException:
            os.close(descriptor)
            raise
        with source:
            before = os.fstat(source.fileno())
            if not _regular(before) or not _same_opened_file(selected, before):
                raise ChapelCompileError(f"{path}: input changed before read")
            payload = source.read(limit + 1)
            after = os.fstat(source.fileno())
        final_path = path.lstat()
        if (not _regular(after) or not _regular(final_path)
                or _identity(before) != _identity(after)
                or _identity(selected) != _identity(final_path)):
            raise ChapelCompileError(f"{path}: input changed during read")
        if len(payload) != before.st_size or len(payload) > limit:
            raise ChapelCompileError(f"{path}: incomplete or oversized bounded read")
        return payload
    except OSError as error:
        raise ChapelCompileError(f"{path}: cannot read: {error}") from error


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ChapelCompileError(f"JSON: duplicate member {key!r}")
        result[key] = value
    return result


def _reject_number(token: str) -> None:
    raise ChapelCompileError(f"JSON: floating-point/nonfinite token {token!r} is forbidden")


def _parse_json(payload: bytes) -> Any:
    try:
        return json.loads(payload.decode("utf-8"), object_pairs_hook=_unique,
                          parse_float=_reject_number, parse_constant=_reject_number)
    except ChapelCompileError:
        raise
    except (UnicodeError, ValueError, RecursionError) as error:
        raise ChapelCompileError(f"invalid bounded UTF-8 JSON: {error}") from error


def parse_review(payload: bytes, label: str) -> list[dict[str, Any]]:
    """Validate a complete ordered reading; names absent in the source stay null."""
    if type(payload) is not bytes or len(payload) > MAX_REVIEW_BYTES:
        raise ChapelCompileError(f"review {label}: requires at most {MAX_REVIEW_BYTES} bytes")
    try:
        rows = list(csv.reader(io.StringIO(payload.decode("utf-8"), newline=""), strict=True))
    except (UnicodeError, csv.Error) as error:
        raise ChapelCompileError(f"review {label}: invalid UTF-8 CSV: {error}") from error
    if not rows or rows[0] != list(REVIEW_HEADER) or len(rows) != 19:
        raise ChapelCompileError(f"review {label}: requires the exact header and 18 ordered rows")
    result = []
    for index, row in enumerate(rows[1:]):
        location = f"review {label} row {index + 1}"
        if len(row) != 5:
            raise ChapelCompileError(f"{location}: requires exactly five columns")
        manual, key, name, taps, page = row
        if manual != ("upper" if index < 9 else "lower") or key != PRESET_KEYS[index % 9]:
            raise ChapelCompileError(f"{location}: wrong or duplicated ordered manual/key")
        if name != "" or page != "122" or re.fullmatch(r"[0-8]{9}", taps) is None:
            raise ChapelCompileError(f"{location}: requires an absent name, page 122 and nine ASCII tap digits 0-8")
        result.append({"manual": manual, "preset_key": key, "preset_name": None,
                       "drawbars": taps, "source_page": 122})
    return result


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def compile_chapel_presets(input_path: str | Path, review_a_path: str | Path,
                           review_b_path: str | Path) -> str:
    """Return a validated deterministic catalog; no output side effect occurs."""
    paths = tuple(Path(path) for path in (input_path, review_a_path, review_b_path))
    payloads = tuple(_read(path, limit) for path, limit in
                     zip(paths, (MAX_AUTHORING_BYTES, MAX_REVIEW_BYTES, MAX_REVIEW_BYTES)))
    try:
        for first in range(len(paths)):
            for second in range(first + 1, len(paths)):
                if paths[first].samefile(paths[second]):
                    raise ChapelCompileError("authoring and both review inputs must be distinct files")
    except OSError as error:
        raise ChapelCompileError(f"cannot compare compiler input identities: {error}") from error
    authoring = _parse_json(payloads[0])
    validate_authoring(authoring)
    for label, payload in zip(("A", "B"), payloads[1:]):
        reading = parse_review(payload, label)
        _expect(reading, authoring["registrations"], f"review {label}.registrations")
        if _sha256(payload) != REVIEW_SHA256:
            raise ChapelCompileError(f"review {label}: raw SHA-256 differs from the frozen independent reading")
    canonical = json.dumps(authoring, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=False, allow_nan=False).encode("utf-8")
    catalog = dict(authoring)
    catalog["format"] = CATALOG_FORMAT
    catalog["inputs"] = {
        "authoring": {"sha256": _sha256(payloads[0]), "canonical_sha256": _sha256(canonical),
                      "bytes": len(payloads[0])},
        "review_a": {"sha256": _sha256(payloads[1]), "bytes": len(payloads[1])},
        "review_b": {"sha256": _sha256(payloads[2]), "bytes": len(payloads[2])},
    }
    text = json.dumps(catalog, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    if len(text.encode("utf-8")) > MAX_OUTPUT_BYTES:
        raise ChapelCompileError("compiled catalog exceeds its byte bound")
    return text


def write_compiled_catalog(output: str | Path, text: str,
                           inputs: tuple[str | Path, ...]) -> None:
    """Publish compiler-returned text atomically in an existing parent directory."""
    output = Path(output)
    temporary = None
    try:
        if type(text) is not str:
            raise ChapelCompileError("compiled catalog text must be a string")
        if len(inputs) != 3:
            raise ChapelCompileError("publication requires all three compiler input paths")
        payload = text.encode("utf-8")
        if not payload or len(payload) > MAX_OUTPUT_BYTES:
            raise ChapelCompileError(f"catalog requires 1..{MAX_OUTPUT_BYTES} UTF-8 bytes")
        try:
            existing = output.lstat()
        except FileNotFoundError:
            existing = None
        if existing is not None and not _regular(existing):
            raise ChapelCompileError("output must be a nonsymlink regular file or a new filename")
        if not output.parent.is_dir():
            raise ChapelCompileError("output parent must already be an existing directory")
        destination = output.resolve()
        for source_value in inputs:
            source = Path(source_value)
            if destination == source.resolve(strict=True) or (
                existing is not None and output.samefile(source)
            ):
                raise ChapelCompileError("output must not alias any compiler input")
        with tempfile.NamedTemporaryFile(mode="wb", prefix=".chapel-catalog-", suffix=".tmp",
                                         dir=output.parent, delete=False) as sink:
            temporary = Path(sink.name)
            if sink.write(payload) != len(payload):
                raise ChapelCompileError("cannot write complete catalog")
            sink.flush()
            os.fsync(sink.fileno())
        os.replace(temporary, output)
        temporary = None
    except (OSError, UnicodeError, RuntimeError) as error:
        raise ChapelCompileError(f"cannot publish catalog {output}: {error}") from error
    finally:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError as error:
                raise ChapelCompileError(f"cannot clean temporary catalog {temporary}: {error}") from error


class _Once(argparse.Action):
    def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace,
                 values: Any, option_string: str | None = None) -> None:
        if getattr(namespace, self.dest, None) is not None:
            parser.error(f"{option_string}: may be supplied only once")
        setattr(namespace, self.dest, values)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], allow_abbrev=False)
    for name, description in (
        ("input", "documentary authoring JSON"), ("review-a", "frozen independent reading A CSV"),
        ("review-b", "frozen independent reading B CSV"), ("output", "generated catalog JSON"),
    ):
        parser.add_argument("--" + name, required=True, action=_Once, type=Path, help=description)
    args = parser.parse_args(argv)
    try:
        inputs = (args.input, args.review_a, args.review_b)
        text = compile_chapel_presets(*inputs)
        write_compiled_catalog(args.output, text, inputs)
    except (ChapelCompileError, OSError) as error:
        print(f"chapel compile error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
