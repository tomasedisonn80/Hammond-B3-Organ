#!/usr/bin/env python3
"""Report capture-v1 declaration gaps without inspecting artifacts or physical truth.

The exact report and admission contract is docs/CAPTURE_READINESS.md. A complete
declaration is not evidence of acquisition, calibration, permission or fidelity.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import capture_common as common
import validate_capture as capture


CONTRACT_ORIGIN = "project-proposed-capture-readiness-v1"
MAX_INPUT_BYTES = 65536
MAX_INPUT_NODES = 4096
MAX_INPUT_DEPTH = 16
MAX_REPORT_BYTES = 1048576
MAX_REPORT_NODES = 16384
MAX_REPORT_DEPTH = 24
MAX_NUMBER = 1e12

# Order and literal missing-action text are part of the independent contract.
_CHECKS = (
    ("specimen.specimen_id", "specimen", "S",
     "Record the actual hardware specimen identifier after identity review."),
    ("specimen.variant", "specimen", "K",
     "Record the hardware variant or the synthetic model identity."),
    ("specimen.revision", "specimen", "K",
     "Record the applicable hardware revision or synthetic code/model revision."),
    ("specimen.identity_evidence", "specimen", "K",
     "Locate retained evidence for the declared subject and configuration identity."),
    ("acquisition.started_at_utc", "acquisition", "K",
     "Record the actual acquisition start time only after acquisition occurs."),
    ("acquisition.operator_id", "acquisition", "K",
     "Assign or record a stable operator identifier."),
    ("acquisition.session_id", "acquisition", "K",
     "Assign or record the acquisition session identifier."),
    ("digital.format", "digital", "K",
     "Declare the raw acquisition format and later check the actual stream."),
    ("digital.sample_rate_hz", "digital", "K",
     "Declare the raw digital sample rate without substituting it for physical clock calibration."),
    ("digital.channel_count", "digital", "K",
     "Declare the raw channel count and ordered channel map."),
    ("physical_clock", "clock", "C",
     "Obtain and review physical clock calibration evidence for the actual acquisition setup."),
    ("stimulus.description", "stimulus", "K",
     "Describe the intended or observed stimulus and retain its schedule."),
    ("stimulus.controls", "stimulus", "K",
     "Declare the control settings and complete gesture/state history."),
    ("stimulus.conditions", "stimulus", "K",
     "Declare the relevant operating conditions with units and unresolved quantities."),
    ("stimulus.synchronization", "stimulus", "K",
     "Describe synchronization and its evidence without inferring it from a shared group."),
    ("signal_path.description", "signal_path", "K",
     "Describe the connected path and separately identify its equipment or synthetic stages."),
    ("signal_path.bypass", "signal_path", "K",
     "Declare the bypass states applicable to this signal path."),
    ("signal_path.loading", "signal_path", "K",
     "Declare connected loads or an explicit synthetic context without inferring physical impedance."),
    ("rights", "rights", "K",
     "Locate separate store, analyze, derive-model and redistribute decisions for review."),
    ("partition.role", "partition", "P",
     "Assign the intended analysis role after whole-group and purpose review."),
    ("partition.group_id", "partition", "K",
     "Declare the complete related acquisition group before analysis."),
)

_CHANNEL_CHECKS = (
    ("boundary", "K",
     "Identify the channel signal boundary without changing its physical meaning."),
    ("port_reference", "K",
     "Declare the channel port, polarity/reference or microphone identity and pose."),
    ("calibration", "C",
     "Obtain and review channel scale and uncertainty evidence at the declared boundary."),
)

_CLAIMS = (
    "artifact_integrity", "audio_content", "authenticity", "calibration",
    "permissions", "corpus_independence", "physical_fidelity",
)


class ReadinessError(ValueError):
    """A contextual admission, report or command failure with a stable code."""

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


def _check(path: str, category: str, rule: str, missing_action: str,
           entry, manifest: dict) -> dict:
    reason = None
    if rule == "S" and manifest["capture_kind"] == "synthetic":
        state = "not_applicable"
        reason = entry["unknown_reason"]
    elif rule == "C":
        state = {"calibrated": "declared", "uncalibrated": "missing",
                 "not_applicable": "not_applicable"}[entry["status"]]
        if state != "declared":
            reason = entry["unknown_reason"]
    elif rule == "P":
        state = "missing" if entry == "unassigned" else "declared"
        if state == "missing":
            reason = manifest["partition"]["rationale"]
    else:
        state = "missing" if entry["value"] is None else "declared"
        if state == "missing":
            reason = entry["unknown_reason"]
    return {"path": path, "category": category, "state": state,
            "reason": reason,
            "action": missing_action if state == "missing" else None}


def _report_bytes(report: dict) -> bytes:
    try:
        common.validate_json_value(report, max_nodes=MAX_REPORT_NODES,
                                   max_depth=MAX_REPORT_DEPTH,
                                   max_number=MAX_NUMBER)
        payload = common.canonical_json_bytes(report)
        if len(payload) > MAX_REPORT_BYTES:
            raise common.DataError("canonical report exceeds 1048576 bytes")
        return payload
    except common.DataError as error:
        raise ReadinessError("report_limit", str(error)) from error


def inspect_readiness(path: str | Path) -> dict:
    """Read one v1 manifest and report declarations; never open its artifacts."""
    if not ((type(path) is str and path != "") or isinstance(path, Path)):
        raise ReadinessError("invalid_argument", "path must be a nonempty str or pathlib.Path")
    try:
        manifest, identity = common.read_json(
            path, max_bytes=MAX_INPUT_BYTES, max_nodes=MAX_INPUT_NODES,
            max_depth=MAX_INPUT_DEPTH, max_number=MAX_NUMBER)
    except common.DataError as error:
        raise ReadinessError("input_error", str(error)) from error
    try:
        capture.validate_capture(manifest)
    except capture.CaptureError as error:
        raise ReadinessError("invalid_manifest", str(error)) from error

    checks = []
    for field_path, category, rule, action in _CHECKS:
        entry = manifest
        for component in field_path.split("."):
            entry = entry[component]
        checks.append(_check(field_path, category, rule, action, entry, manifest))
    for index, channel in enumerate(manifest["digital"]["channels"]):
        for field, rule, action in _CHANNEL_CHECKS:
            field_path = f"digital.channels[{index}].{field}"
            checks.append(_check(field_path, "channel", rule, action,
                                 channel[field], manifest))
    summary = {"total": len(checks), "declared": 0, "missing": 0, "not_applicable": 0}
    for check in checks:
        summary[check["state"]] += 1
    if manifest["status"] == "planned":
        status = "planned"
    elif summary["missing"]:
        status = "declarations_incomplete"
    else:
        status = "declarations_complete"
    report = {
        "schema_version": 1, "contract_origin": CONTRACT_ORIGIN,
        "scope": "declared-metadata-only", "capture_id": manifest["capture_id"],
        "capture_kind": manifest["capture_kind"], "record_status": manifest["status"],
        "status": status, "input": identity, "manifest": manifest,
        "calibration_context": "raw_acquisition_only", "checks": checks,
        "summary": summary, "claims": {claim: "not_established" for claim in _CLAIMS},
    }
    _report_bytes(report)
    return report


class _HelpRequested(Exception):
    pass


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise ReadinessError("invalid_argument", message)

    def exit(self, status=0, message=None):
        if status == 0:
            raise _HelpRequested()
        raise ReadinessError("invalid_argument", message or "argument parsing failed")

    def _print_message(self, message, file=None):
        if message:
            _write_utf8(file or sys.stdout, message.encode("utf-8"), label="help")


class _Once(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if getattr(namespace, self.dest, None) is not None:
            parser.error(f"{option_string} may occur at most once")
        if not values:
            parser.error(f"{option_string} requires a nonempty value")
        setattr(namespace, self.dest, values)


def _write_utf8(stream, payload: bytes, *, label: str) -> None:
    try:
        binary = getattr(stream, "buffer", None)
        if binary is not None:
            count = binary.write(payload)
            if count != len(payload):
                raise OSError("incomplete standard-stream byte write")
            binary.flush()
        else:
            value = payload.decode("utf-8")
            count = stream.write(value)
            if count != len(value):
                raise OSError("incomplete standard-stream text write")
            stream.flush()
    except (OSError, UnicodeError, ValueError, TypeError) as error:
        raise ReadinessError("stream_error", f"{label} delivery failed: {error}") from error


def main(argv: list[str] | None = None) -> int:
    parser = _Parser(prog="capture_readiness.py", allow_abbrev=False,
                     description="Report capture-v1 declaration gaps; no physical qualification.")
    parser.add_argument("--input", required=True, action=_Once, help="capture v1 manifest")
    parser.add_argument("--output", action=_Once, help="new report path; never replaces an existing path")
    try:
        if argv is not None and (type(argv) is not list or
                                 any(type(token) is not str for token in argv)):
            raise ReadinessError("invalid_argument", "argv must be a list of strings or None")
        args = parser.parse_args(argv)
        report = inspect_readiness(args.input)
        payload = _report_bytes(report)
        if args.output is not None:
            try:
                common.write_json_new(args.output, report)
            except common.DataError as error:
                raise ReadinessError("output_error", str(error)) from error
        _write_utf8(sys.stdout, payload, label="stdout")
        return 0 if report["status"] == "declarations_complete" else 3
    except _HelpRequested:
        return 0
    except ReadinessError as error:
        failure = {"schema_version": 1, "contract_origin": CONTRACT_ORIGIN,
                   "status": "rejected",
                   "error": {"code": error.code, "message": error.message}}
        try:
            _write_utf8(sys.stderr, common.canonical_json_bytes(failure), label="stderr")
        except ReadinessError:
            pass
        return 2 if error.code == "invalid_argument" else 1


if __name__ == "__main__":
    def _delivery_error(message):
        failure = {"schema_version": 1, "contract_origin": CONTRACT_ORIGIN,
                   "status": "rejected", "error": {"code": "stream_error",
                   "message": f"standard-stream delivery failed: {message}"}}
        _write_utf8(sys.stderr, common.canonical_json_bytes(failure), label="stderr")

    raise SystemExit(common._cli_exit(main, _delivery_error))
