#!/usr/bin/env python3
"""Export reviewed chapel tap rows as ordinary nominal B3CONTROLS3 auditions.

This offline utility changes no Engine, state schema or physical preset latch.
It uses only the standard library and the public documentary authoring validator.
New control files are published without replacing existing files.
"""

from __future__ import annotations

import argparse
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

from compile_chapel_presets import ChapelCompileError, validate_authoring


CATALOG_FORMAT = "hammond-chapel-catalog-v1"
MAX_CATALOG_BYTES = 64 * 1024
MAX_AUTHORING_BYTES = 64 * 1024
MAX_CONTROL_BYTES = 16 * 1024
MAX_EXPRESSION_CHARACTERS = 64
REVIEW_SHA256 = "dc2a8fd4e9750133c982bb42fd6cc7c12908f011154826035bb623f52d8de694"
REVIEW_BYTES = 466
PRESET_KEYS = ("C#", "D", "D#", "E", "F", "F#", "G", "G#", "A")
AUTHORING_FIELDS = frozenset((
    "schema_version", "model_id", "evidence_class", "applicable_variant", "source",
    "tap_units", "drawbars", "registrations", "limitations",
))


class ChapelControlsError(ValueError):
    """A catalog, selection, control-text or file-publication admission failure."""


def _exact_object(value: Any, fields: set[str] | frozenset[str], label: str) -> None:
    if type(value) is not dict or any(type(key) is not str for key in value):
        raise ChapelControlsError(f"{label}: requires an object with string members")
    if set(value) != fields:
        raise ChapelControlsError(f"{label}: requires exactly {sorted(fields)!r}")


def _hash(value: Any, label: str) -> None:
    if type(value) is not str or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise ChapelControlsError(f"{label}: requires a lowercase SHA-256 string")


def validate_catalog(data: Any) -> dict[str, Any]:
    """Validate semantics/provenance shape and return its authoring view.

    The raw authoring hash/byte count are declared metadata, not authentication
    of absent raw input. The canonical semantic hash is recomputed here.
    """
    _exact_object(data, AUTHORING_FIELDS | {"format", "inputs"}, "catalog")
    if type(data["format"]) is not str or data["format"] != CATALOG_FORMAT:
        raise ChapelControlsError("catalog: unsupported format")
    authoring = {key: data[key] for key in AUTHORING_FIELDS}
    try:
        validate_authoring(authoring)
    except ChapelCompileError as error:
        raise ChapelControlsError(f"catalog semantics: {error}") from error
    inputs = data["inputs"]
    _exact_object(inputs, {"authoring", "review_a", "review_b"}, "catalog.inputs")
    raw = inputs["authoring"]
    _exact_object(raw, {"sha256", "canonical_sha256", "bytes"}, "catalog.inputs.authoring")
    for key in ("sha256", "canonical_sha256"):
        _hash(raw[key], f"catalog.inputs.authoring.{key}")
    if type(raw["bytes"]) is not int or not 1 <= raw["bytes"] <= MAX_AUTHORING_BYTES:
        raise ChapelControlsError("catalog.inputs.authoring.bytes: outside the authoring byte bound")
    canonical = json.dumps(authoring, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=False, allow_nan=False).encode("utf-8")
    if hashlib.sha256(canonical).hexdigest() != raw["canonical_sha256"]:
        raise ChapelControlsError("catalog: canonical authoring hash does not match its semantics")
    for label in ("review_a", "review_b"):
        review = inputs[label]
        _exact_object(review, {"sha256", "bytes"}, f"catalog.inputs.{label}")
        if type(review["sha256"]) is not str or review["sha256"] != REVIEW_SHA256:
            raise ChapelControlsError(f"catalog.inputs.{label}: frozen review hash does not match")
        if type(review["bytes"]) is not int or review["bytes"] != REVIEW_BYTES:
            raise ChapelControlsError(f"catalog.inputs.{label}: frozen review byte count does not match")
    return authoring


def _path(value: str | Path, label: str) -> Path:
    try:
        path = Path(value)
        if "\x00" in str(path):
            raise ValueError("embedded NUL")
        return path
    except (TypeError, ValueError) as error:
        raise ChapelControlsError(f"{label}: invalid filesystem path") from error


def _regular(metadata: os.stat_result) -> bool:
    return stat.S_ISREG(metadata.st_mode) and not (
        getattr(metadata, "st_file_attributes", 0)
        & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    )


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


def _read_catalog(path: Path) -> bytes:
    try:
        selected = path.lstat()
        if not _regular(selected) or not 1 <= selected.st_size <= MAX_CATALOG_BYTES:
            raise ChapelControlsError("catalog requires a nonsymlink regular file of 1..65536 bytes")
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
                raise ChapelControlsError("catalog changed before its bounded read")
            payload = source.read(MAX_CATALOG_BYTES + 1)
            after = os.fstat(source.fileno())
        final_path = path.lstat()
        if (not _regular(after) or not _regular(final_path)
                or _identity(before) != _identity(after)
                or _identity(selected) != _identity(final_path)):
            raise ChapelControlsError("catalog changed during its bounded read")
        if len(payload) != before.st_size or len(payload) > MAX_CATALOG_BYTES:
            raise ChapelControlsError("catalog read was incomplete or oversized")
        return payload
    except OSError as error:
        raise ChapelControlsError(f"cannot read catalog {path}: {error}") from error


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ChapelControlsError(f"catalog: duplicate JSON member {key!r}")
        result[key] = value
    return result


def _reject_number(token: str) -> None:
    raise ChapelControlsError(f"catalog: floating/nonfinite JSON token {token!r} is forbidden")


def load_catalog(path: str | Path) -> dict[str, Any]:
    """Read and validate one bounded stable regular catalog, without writes."""
    payload = _read_catalog(_path(path, "catalog"))
    try:
        data = json.loads(payload.decode("utf-8"), object_pairs_hook=_unique,
                          parse_float=_reject_number, parse_constant=_reject_number)
        validate_catalog(data)
        return data
    except ChapelControlsError:
        raise
    except (UnicodeError, ValueError, RecursionError) as error:
        raise ChapelControlsError(f"invalid catalog JSON: {error}") from error


def expression_value(token: str) -> float:
    """Admit 0, 1, or 0.<digits ending nonzero>, with at most 64 characters."""
    if type(token) is not str or len(token) > MAX_EXPRESSION_CHARACTERS or re.fullmatch(
            r"(?:0|1|0\.[0-9]*[1-9])", token) is None:
        raise ChapelControlsError("expression requires 0, 1, or 0.<digits ending nonzero>, at most 64 characters")
    value = float(token)
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ChapelControlsError("expression is outside finite [0,1]")
    return value


def render_controls(catalog: Any, upper: str = "off", lower: str = "off",
                    bank: str = "A", expression: str = "0.75") -> str:
    """Return canonical control-only text for the explicitly selected audition."""
    authoring = validate_catalog(catalog)
    if type(bank) is not str or bank not in ("A", "B"):
        raise ChapelControlsError("bank must be A or B")
    for manual, key in (("upper", upper), ("lower", lower)):
        if type(key) is not str or key not in (*PRESET_KEYS, "off"):
            raise ChapelControlsError(f"{manual}: unsupported documentary key")
    if upper == "off" and lower == "off":
        raise ChapelControlsError("select at least one upper or lower documentary registration")
    value = expression_value(expression)
    rows = {(row["manual"], row["preset_key"]): row["drawbars"] for row in authoring["registrations"]}
    lines = ["B3CONTROLS3", f"expression {value:.17g}",
             "percussion enabled 0 harmonic second volume normal decay slow", "pedal drawbars 0 0"]
    for manual, key in (("upper", upper), ("lower", lower)):
        enabled = key != "off"
        taps = rows[(manual, key)] if enabled else "000000000"
        lines.append(f"manual {manual} selected {bank} route_enabled {int(enabled)}")
        for selected in ("A", "B"):
            lines.append(f"bank {selected} " + " ".join(taps if selected == bank else "000000000"))
    lines.append("end")
    return "\n".join(lines) + "\n"


def _validate_export_text(text: Any, catalog: dict[str, Any]) -> bytes:
    if type(text) is not str:
        raise ChapelControlsError("control text must be a string returned by render_controls")
    try:
        payload = text.encode("ascii")
    except UnicodeError as error:
        raise ChapelControlsError("control text must be ASCII") from error
    if not 1 <= len(payload) <= MAX_CONTROL_BYTES or "\r" in text or not text.endswith("\n"):
        raise ChapelControlsError("control text must be bounded LF text with a final newline")
    lines = text.splitlines()
    if (text != "\n".join(lines) + "\n" or len(lines) != 11 or lines[0] != "B3CONTROLS3" or lines[-1] != "end" or
            lines[2] != "percussion enabled 0 harmonic second volume normal decay slow" or
            lines[3] != "pedal drawbars 0 0" or not lines[1].startswith("expression ")):
        raise ChapelControlsError("control text does not have the canonical audition layout")
    token = lines[1][len("expression "):]
    try:
        value = float(token)
    except ValueError as error:
        raise ChapelControlsError("invalid serialized expression") from error
    if not math.isfinite(value) or not 0.0 <= value <= 1.0 or token.startswith("-") or format(value, ".17g") != token:
        raise ChapelControlsError("serialized expression must be canonical finite nonnegative [0,1]")
    selections = []
    enabled_parts = 0
    for manual, start in (("upper", 4), ("lower", 7)):
        selection = re.fullmatch(rf"manual {manual} selected ([AB]) route_enabled ([01])", lines[start])
        if selection is None:
            raise ChapelControlsError("invalid canonical manual selection")
        bank, enabled = selection.groups()
        selections.append(bank)
        enabled_parts += int(enabled)
        for index, name in enumerate(("A", "B"), start + 1):
            row = re.fullmatch(rf"bank {name} ([0-8](?: [0-8]){{8}})", lines[index])
            if row is None:
                raise ChapelControlsError("invalid canonical bank row")
            taps = row.group(1).replace(" ", "")
            if enabled == "1" and name == bank:
                if not any(item["manual"] == manual and item["drawbars"] == taps for item in catalog["registrations"]):
                    raise ChapelControlsError("selected bank is not a reviewed documentary registration")
            elif taps != "000000000":
                raise ChapelControlsError("disabled or unselected audition banks must be zero")
    if selections[0] != selections[1] or enabled_parts == 0:
        raise ChapelControlsError("audition needs one common selected bank and at least one enabled part")
    return payload


def write_controls_file(output: str | Path, text: str, catalog_path: str | Path) -> None:
    """Publish complete validated audition text as a new file using a hard link.

    The parent must exist and support same-filesystem hard links. Existing
    destinations, including symlink/reparse leaves, are never replaced.
    """
    destination = _path(output, "output")
    source = _path(catalog_path, "catalog")
    catalog = load_catalog(source)
    payload = _validate_export_text(text, catalog)
    temporary = None
    try:
        try:
            destination.lstat()
        except FileNotFoundError:
            pass
        else:
            raise ChapelControlsError("output already exists; choose a new filename")
        if not destination.parent.is_dir():
            raise ChapelControlsError("output parent must already exist")
        if destination.resolve() == source.resolve(strict=True):
            raise ChapelControlsError("output must not alias its catalog input")
        with tempfile.NamedTemporaryFile(mode="wb", prefix=".chapel-controls-", suffix=".tmp",
                                         dir=destination.parent, delete=False) as sink:
            temporary = Path(sink.name)
            if sink.write(payload) != len(payload):
                raise ChapelControlsError("cannot write complete control text")
            sink.flush()
            os.fsync(sink.fileno())
        # Atomic creation fails if another file appeared after preflight. Never
        # use replace/rename here: an existing user's state must survive.
        os.link(temporary, destination, follow_symlinks=False)
    except (OSError, RuntimeError) as error:
        raise ChapelControlsError(f"cannot publish controls {destination}: {error}") from error
    finally:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError as error:
                raise ChapelControlsError(f"cannot remove temporary controls {temporary}: {error}") from error


class _Once(argparse.Action):
    def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace,
                 values: Any, option_string: str | None = None) -> None:
        if getattr(namespace, self.dest, None) is not None:
            parser.error(f"{option_string}: may be supplied only once")
        setattr(namespace, self.dest, values)


def _path_argument(value: str) -> Path:
    if not value or "\x00" in value:
        raise argparse.ArgumentTypeError("path must not be empty or contain NUL")
    return Path(value)


def _expression_argument(value: str) -> str:
    try:
        expression_value(value)
    except ChapelControlsError as error:
        raise argparse.ArgumentTypeError(str(error)) from error
    return value


def main(argv: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], allow_abbrev=False, add_help=False)
    parser.add_argument("--help", action="store_true", help="show this help; must be used alone")
    parser.add_argument("--catalog", required=True, action=_Once, type=_path_argument, help="validated chapel catalog JSON")
    parser.add_argument("--output", required=True, action=_Once, type=_path_argument, help="new B3CONTROLS3 filename")
    for manual in ("upper", "lower"):
        parser.add_argument("--" + manual, action=_Once, choices=(*PRESET_KEYS, "off"), help="documentary key; default off")
    parser.add_argument("--bank", action=_Once, choices=("A", "B"), help="destination bank; default A")
    parser.add_argument("--expression", action=_Once, type=_expression_argument, help="canonical decimal in [0,1]; default 0.75")
    if "--help" in arguments:
        if arguments != ["--help"]:
            parser.error("--help must be used alone")
        parser.print_help()
        return 0
    args = parser.parse_args(arguments)
    upper, lower = args.upper or "off", args.lower or "off"
    if upper == "off" and lower == "off":
        parser.error("select at least one --upper or --lower registration")
    try:
        catalog = load_catalog(args.catalog)
        text = render_controls(catalog, upper, lower, args.bank or "A", args.expression or "0.75")
        write_controls_file(args.output, text, args.catalog)
    except (ChapelControlsError, OSError) as error:
        print(f"chapel controls error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
