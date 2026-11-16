#!/usr/bin/env python3
"""Publish one bounded synthetic contact-grid trajectory certificate."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import signal
import sys
import tempfile
import threading
import time

import contact_grid_conversion as conversion
import contact_switching_io as contact_io


CONVERSION_ID = "fractional-to-contact-grid-rne-v1"
MAX_REFUSAL_BYTES = 8192
MAX_CERTIFICATE_BYTES = 32 * 1024 * 1024
DEADLINE_SECONDS = 30.0
IMPLEMENTATION_FILES = (
    "contact_grid_conversion.py", "convert_contact_grid.py",
    "contact_switching_io.py", "fractional_contact_reference.py",
)


class _CliRefusal(ValueError):
    def __init__(self, code: str, path: str, witness: dict):
        super().__init__(code)
        self.code, self.path, self.witness = code, path, witness


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise ValueError(message)


class _Once(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if getattr(namespace, self.dest, None) is not None:
            raise ValueError(f"{option_string} may occur only once")
        if not values or values == "-":
            raise ValueError(f"{option_string} requires a named file; stdin/stdout is unsupported")
        setattr(namespace, self.dest, values)


@dataclass
class _Publication:
    committed: bool = False


class _DeferredSigint:
    """Finish an acquisition/commit's ownership bookkeeping before interrupting."""
    def __init__(self, publication: _Publication | None = None):
        self.publication = publication
        self.interrupted = False
        self.previous = None
        self.installed = False

    def _defer(self, signum, frame):
        self.interrupted = True

    def __enter__(self):
        # Python dispatches process SIGINT only on the main thread.
        if threading.current_thread() is threading.main_thread():
            self.previous = signal.signal(signal.SIGINT, self._defer)
            self.installed = True
        return self

    def __exit__(self, kind, value, traceback):
        try:
            if self.installed:
                signal.signal(signal.SIGINT, self.previous)
        finally:
            committed = self.publication is not None and self.publication.committed
            if self.interrupted and not committed:
                raise KeyboardInterrupt


def _check_deadline(deadline: float) -> None:
    if time.monotonic() >= deadline:
        raise _CliRefusal("resource", "deadline", {"reason": "30-second cooperative deadline exceeded"})


def _provenance() -> tuple[dict[str, str], str]:
    directory = Path(__file__).resolve().parent
    implementations = {
        "tools/" + name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
        for name in IMPLEMENTATION_FILES
    }
    contract = directory.parent / "docs" / "CONTACT_GRID_CONVERSION_CONTRACT.md"
    return implementations, hashlib.sha256(contract.read_bytes()).hexdigest()


def _recheck_plan(plan: contact_io.OutputPlan) -> None:
    if contact_io.preflight_paths(plan.input_argument, plan.output_argument) != plan:
        raise ValueError("input, output or parent changed after path preflight")


def _replace(temporary: Path, destination: Path, publication: _Publication,
             deadline: float) -> None:
    """Defer SIGINT only through the irrevocable replacement/bookkeeping window.

    A pending interrupt checked before replace aborts without publication. A
    signal delivered during replace cannot cancel that filesystem operation;
    its outcome determines whether the operation committed. On success the
    caller must report success even if SIGINT arrives before handler restoration.
    Python delivers process SIGINT on the main thread, so a non-main-thread
    library invocation needs no handler replacement.
    """
    with _DeferredSigint(publication) as pending:
        _check_deadline(deadline)
        if pending.interrupted:
            raise KeyboardInterrupt
        os.replace(temporary, destination)
        publication.committed = True


def _publish(plan: contact_io.OutputPlan, payload: bytes, *, deadline: float,
             publication: _Publication) -> None:
    # The complete, independently re-encoded payload already exists here.
    _check_deadline(deadline)
    _recheck_plan(plan)
    descriptor = None
    temporary = None
    try:
        with _DeferredSigint():
            descriptor, name = tempfile.mkstemp(prefix=".contact-grid-", suffix=".tmp",
                                                dir=plan.output_path.parent)
            temporary = Path(name)
        stream = os.fdopen(descriptor, "wb")
        descriptor = None  # The stream now owns this descriptor.
        with stream:
            written = stream.write(payload)
            if written != len(payload):
                raise OSError("incomplete certificate write")
            stream.flush()
            os.fsync(stream.fileno())
        _check_deadline(deadline)
        _recheck_plan(plan)
        _replace(temporary, plan.output_path, publication, deadline)
    finally:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass
        if temporary is not None and not publication.committed:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass
            except OSError:
                # A permission/directory failure can also prevent cleanup. Do
                # not hide the original error or unlink any different path.
                pass


def _sanitized(error: BaseException) -> str:
    value = str(error)[:480]
    value = " ".join(value.split())
    return "".join(character if character.isprintable() else "?" for character in value) or type(error).__name__


def _refusal_line(code: str, path: str, witness: dict) -> str:
    def encode(selected_code, selected_path, selected_witness):
        return (json.dumps({"schema_version": 1, "conversion_id": CONVERSION_ID,
                            "status": "refused", "code": selected_code,
                            "path": selected_path, "witness": selected_witness},
                           ensure_ascii=True, allow_nan=False, sort_keys=True,
                           separators=(",", ":")) + "\n")

    try:
        if type(code) is not str or type(path) is not str or type(witness) is not dict:
            raise ValueError("invalid refusal fields")
        result = encode(code, path, witness)
        if len(result.encode("ascii")) <= MAX_REFUSAL_BYTES:
            return result
        reason = "refusal diagnostic exceeds 8192 bytes; exact witness not emitted"
    except (TypeError, ValueError, OverflowError, RecursionError):
        reason = "refusal diagnostic cannot be represented as bounded strict JSON"
    return encode("resource", "diagnostic", {"reason": reason})


def _emit_refusal(code: str, path: str, witness: dict) -> None:
    line = _refusal_line(code, path, witness)
    try:
        sys.stdout.write(line)
        sys.stdout.flush()
    except OSError:
        # No alternate stream may turn the one-line stdout protocol into an
        # unbounded traceback. A closed stdout cannot receive a diagnostic.
        pass


def main(argv: list[str] | None = None) -> int:
    publication = _Publication()
    stage = "arguments"
    try:
        deadline = time.monotonic() + DEADLINE_SECONDS
        parser = _Parser(description=__doc__, allow_abbrev=False, add_help=False)
        parser.add_argument("--input", required=True, action=_Once, metavar="FILE")
        parser.add_argument("--output", required=True, action=_Once, metavar="CERTIFICATE")
        arguments = parser.parse_args(argv)
        _check_deadline(deadline)
        stage = "paths"
        plan = contact_io.preflight_paths(arguments.input, arguments.output)
        stage = "input"
        document = contact_io.load_input(plan.input_path, expected_signature=plan.input_signature)
        stage = "provenance"
        hashes, contract_hash = _provenance()
        _check_deadline(deadline)
        stage = "conversion"
        result = conversion.convert_document(document, deadline=deadline)
        stage = "certificate"
        payload = conversion.encode_certificate(result, implementation_sha256=hashes,
                                                contract_sha256=contract_hash, deadline=deadline)
        if type(payload) is not bytes or len(payload) > MAX_CERTIFICATE_BYTES:
            raise _CliRefusal("certificate", "payload", {"reason": "encoder did not return bounded bytes"})
        _check_deadline(deadline)
        if _provenance() != (hashes, contract_hash):
            raise _CliRefusal("certificate", "provenance", {"reason": "implementation or contract changed during conversion"})
        stage = "publication"
        _publish(plan, payload, deadline=deadline, publication=publication)
        return 0
    except KeyboardInterrupt:
        if publication.committed:
            return 0
        _emit_refusal("interrupted", stage, {"reason": "interrupted before certificate publication"})
        return 130
    except (conversion.ConversionRefusal, _CliRefusal) as error:
        if publication.committed:
            return 0
        _emit_refusal(error.code, error.path, error.witness)
        return 2
    except Exception as error:
        if publication.committed:
            return 0
        code = {"arguments": "argument", "paths": "path", "input": "input"}.get(stage, "operation")
        _emit_refusal(code, stage, {"reason": _sanitized(error), "exception": type(error).__name__[:64]})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
