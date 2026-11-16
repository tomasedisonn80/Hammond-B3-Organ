"""Strict admission and transactional reports for the offline contact reference.

The JSON boundary is deliberately separate from the immutable numerical kernel.
No output is opened until the complete input, paths, work bound and finite report
have been admitted. This module does not connect the reference to the Engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import stat
import sys
import tempfile
import time
from typing import NamedTuple

import fractional_contact_reference as kernel


MAX_INPUT_BYTES = 256 * 1024
MAX_JSON_DEPTH = 12
MAX_REPORT_BYTES = 32 * 1024 * 1024
SUITE_ELAPSED_SECONDS = 300
SUITE_PEAK_RESIDENT_BYTES = 256 * 1024 * 1024
IMPLEMENTATION_FILES = (
    "fractional_contact_reference.py",
    "contact_switching_io.py",
    "contact_switching_reference.py",
)
INPUT_FIELDS = frozenset((
    "schema_version", "model_id", "evidence_class", "fixture_id",
    "sample_rate_hz", "frames", "sources", "keys", "targets",
))
REPORT_FIELDS = frozenset((
    "schema_version", "model_id", "evidence_class", "fixture_id",
    "input_sha256", "implementation_sha256", "python_version", "platform",
    "sample_rate_hz", "frames", "factor", "first_frame", "time_offset_seconds",
    "samples", "raw_bound", "output_bound", "work", "caps", "observations",
    "targets", "edges", "final_keys", "filter", "gate_jumps",
))
_IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", re.ASCII)
_SHA256 = re.compile(r"[0-9a-f]{64}", re.ASCII)


class InputDocument(NamedTuple):
    fixture_id: str
    case: kernel.Case
    input_sha256: str
    input_size_bytes: int


@dataclass(frozen=True)
class OutputPlan:
    """Preflight identities, keeping path and descriptor metadata separate."""

    input_argument: Path
    output_argument: Path
    input_path: Path
    output_path: Path
    input_signature: tuple[int, ...]
    input_path_signature: tuple[int, ...]
    output_signature: tuple[int, ...] | None
    parent_identity: tuple[int, int]


def _record(value: object, fields: frozenset[str], label: str) -> dict:
    if type(value) is not dict or set(value) != fields:
        raise ValueError(f"{label} has unknown or missing fields")
    return value


def _array(value: object, low: int, high: int, label: str) -> list:
    if type(value) is not list or not low <= len(value) <= high:
        raise ValueError(f"{label} must be an array with {low}..{high} entries")
    return value


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for name, value in pairs:
        if name in result:
            raise ValueError("duplicate JSON object member")
        result[name] = value
    return result


def _json_integer(token: str) -> int:
    # Every admitted integer is tiny. Bound conversion before Python allocates
    # an arbitrarily large integer, independently of its interpreter digit cap.
    if len(token) > 32:
        raise ValueError("JSON integer exceeds the bounded numeric domain")
    return int(token)


def _json_float(token: str) -> float:
    value = float(token)
    if not math.isfinite(value):
        raise ValueError("JSON numbers must be finite")
    return value if value else 0.0


def _invalid_constant(token: str) -> None:
    raise ValueError("JSON NaN and Infinity are forbidden")


def _check_depth(text: str) -> None:
    """Count containers outside strings before calling the recursive decoder."""
    depth = 0
    in_string = escaped = False
    for character in text:
        if in_string:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
        elif character == '"':
            in_string = True
        elif character in "[{":
            depth += 1
            if depth > MAX_JSON_DEPTH:
                raise ValueError("JSON nesting exceeds 12 containers")
        elif character in "]}":
            depth -= 1
            if depth < 0:
                raise ValueError("invalid JSON container nesting")


def parse_input(data: bytes) -> InputDocument:
    """Admit exact UTF-8 bytes and return canonical immutable kernel inputs."""
    if type(data) is not bytes or len(data) > MAX_INPUT_BYTES:
        raise ValueError("input must be at most 256 KiB of UTF-8 JSON bytes")
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        raise ValueError("input is not valid UTF-8") from None
    _check_depth(text)
    try:
        document = json.loads(text, object_pairs_hook=_unique_object,
                              parse_int=_json_integer, parse_float=_json_float,
                              parse_constant=_invalid_constant)
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid JSON at line {error.lineno}, column {error.colno}") from None
    document = _record(document, INPUT_FIELDS, "input")
    if type(document["schema_version"]) is not int or document["schema_version"] != 1:
        raise ValueError("schema_version must be the integer 1")
    if document["model_id"] != kernel.MODEL_ID or document["evidence_class"] != "synthetic":
        raise ValueError("input must identify fractional-contact-reference-v1 synthetic evidence")
    fixture_id = document["fixture_id"]
    if type(fixture_id) is not str or _IDENTIFIER.fullmatch(fixture_id) is None:
        raise ValueError("fixture_id must be a 1..64 character ASCII identifier")
    sources = []
    for source in _array(document["sources"], 1, 36, "sources"):
        source = _record(source, frozenset(("source_id", "frequency_hz", "amplitude",
                                            "phase_turns")), "source")
        sources.append(kernel.Source(source["source_id"], source["frequency_hz"],
                                     source["amplitude"], source["phase_turns"]))
    keys = []
    for key in _array(document["keys"], 1, 4, "keys"):
        key = _record(key, frozenset(("key_id", "press_seconds", "release_seconds",
                                     "on", "off", "source_ids", "gains")), "key")
        arrays = [tuple(_array(key[name], 9, 9, name))
                  for name in ("on", "off", "source_ids", "gains")]
        keys.append(kernel.Key(key["key_id"], key["press_seconds"],
                               key["release_seconds"], *arrays))
    targets = []
    for target in _array(document["targets"], 0, 512, "targets"):
        target = _record(target, frozenset(("frame", "fraction", "key_id", "target")),
                         "target")
        targets.append(kernel.Target(target["frame"], target["fraction"],
                                     target["key_id"], target["target"]))
    case = kernel.validate_case(kernel.Case(document["sample_rate_hz"], document["frames"],
                                            tuple(sources), tuple(keys), tuple(targets)))
    return InputDocument(fixture_id, case, hashlib.sha256(data).hexdigest(), len(data))


def _signature(information: os.stat_result) -> tuple[int, ...]:
    return (information.st_dev, information.st_ino, information.st_mode,
            information.st_size, information.st_mtime_ns, information.st_ctime_ns)


def _preflight_input_signature(path: Path, information: os.stat_result) -> tuple[int, ...]:
    """Bind the admitted path to a descriptor without mixing metadata APIs.

    Windows CPython 3.12 path stat keeps creation time in st_ctime_ns, while
    fstat exposes change time. Path-derived execute bits may also differ.
    Preserve both full signatures and bridge them using device/inode identity.
    """
    flags = os.O_RDONLY | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_BINARY", 0)
    descriptor = os.open(path, flags)
    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode):
            raise ValueError("input must be a regular file")
        if opened.st_size > MAX_INPUT_BYTES:
            raise ValueError("input exceeds 256 KiB")
        if (not os.path.samestat(information, opened)
                or _signature(os.stat(path)) != _signature(information)):
            raise ValueError("input changed during path preflight")
        return _signature(opened)
    finally:
        os.close(descriptor)


def load_input(path: str | os.PathLike, *,
               expected_signature: tuple[int, ...] | None = None) -> InputDocument:
    """Read a bounded regular file against a descriptor-derived preflight token."""
    information = os.stat(path)
    if not stat.S_ISREG(information.st_mode):
        raise ValueError("input must be a regular file")
    if information.st_size > MAX_INPUT_BYTES:
        raise ValueError("input exceeds 256 KiB")
    flags = os.O_RDONLY | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_BINARY", 0)
    descriptor = os.open(path, flags)
    try:
        source = os.fdopen(descriptor, "rb")
    except BaseException:
        os.close(descriptor)
        raise
    with source:
        before = os.fstat(source.fileno())
        if not stat.S_ISREG(before.st_mode):
            raise ValueError("input must be a regular file")
        if expected_signature is not None and _signature(before) != expected_signature:
            raise ValueError("input changed after path preflight")
        if before.st_size > MAX_INPUT_BYTES:
            raise ValueError("input exceeds 256 KiB")
        data = source.read(MAX_INPUT_BYTES + 1)
        after = os.fstat(source.fileno())
        if _signature(before) != _signature(after):
            raise ValueError("input changed while being read")
    return parse_input(data)


def preflight_paths(input_path: str | os.PathLike,
                    output_path: str | os.PathLike) -> OutputPlan:
    """Admit existing parents and regular types without creating any path.

    Input symlinks and parent-directory symlinks are resolved. An output leaf
    symlink is unsupported: atomic replacement must not silently change whether
    the caller meant the link or its target. All inode aliases are rejected.
    """
    output_text = os.fspath(output_path)
    separators = (os.sep,) if os.altsep is None else (os.sep, os.altsep)
    if not output_text or output_text.endswith(separators):
        raise ValueError("output must name a file, without a trailing directory separator")
    input_argument = Path(input_path).absolute()
    output_argument = Path(output_path).absolute()
    resolved_input = input_argument.resolve(strict=True)
    source_stat = resolved_input.stat()
    if not stat.S_ISREG(source_stat.st_mode):
        raise ValueError("input must be a regular file")
    if source_stat.st_size > MAX_INPUT_BYTES:
        raise ValueError("input exceeds 256 KiB")
    parent = output_argument.parent.resolve(strict=True)
    parent_stat = parent.stat()
    if not stat.S_ISDIR(parent_stat.st_mode):
        raise ValueError("output parent must already be a directory")
    destination = parent / output_argument.name
    if destination == resolved_input:
        raise ValueError("input and output must not alias")
    try:
        destination_stat = destination.lstat()
    except FileNotFoundError:
        destination_stat = None
    if destination_stat is not None:
        try:
            followed = destination.stat()
        except FileNotFoundError:
            followed = destination_stat
        if (source_stat.st_dev, source_stat.st_ino) == (followed.st_dev, followed.st_ino):
            raise ValueError("input and output must not alias, including hardlinks or symlinks")
        if not stat.S_ISREG(destination_stat.st_mode):
            raise ValueError("output must be absent or a regular file, not a symlink or special file")
    return OutputPlan(input_argument, output_argument, resolved_input, destination,
                      _preflight_input_signature(resolved_input, source_stat),
                      _signature(source_stat),
                      _signature(destination_stat) if destination_stat is not None else None,
                      (parent_stat.st_dev, parent_stat.st_ino))


def _recheck_plan(plan: OutputPlan) -> None:
    current = preflight_paths(plan.input_argument, plan.output_argument)
    if current != plan:
        raise ValueError("input, output or parent changed after path preflight")


def implementation_hashes() -> dict[str, str]:
    directory = Path(__file__).resolve().parent
    return {"tools/" + name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
            for name in IMPLEMENTATION_FILES}


def _exact_coordinate(value: Fraction) -> dict[str, str]:
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def _display_coordinate(value: Fraction) -> tuple[int, float]:
    frame = math.floor(value)
    fraction = float(value - frame)
    if fraction == 1.0:
        frame += 1
        fraction = 0.0
    return frame, fraction if fraction else 0.0


def _peak_resident() -> tuple[int | None, str, str | None]:
    try:
        import resource
        raw = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if sys.platform.startswith("linux"):
            scale, units = 1024, "KiB converted to bytes"
        elif sys.platform == "darwin":
            scale, units = 1, "bytes"
        else:
            return None, "unavailable", "ru_maxrss byte units are not established on this platform"
        if not math.isfinite(raw) or raw <= 0:
            return None, "unavailable", "ru_maxrss did not return a positive finite measurement"
        return int(raw * scale), ("resource.getrusage(RUSAGE_SELF).ru_maxrss; " + units
                                 + "; process lifetime peak sampled after report construction"), None
    except (ImportError, AttributeError, OSError, ValueError, OverflowError):
        return None, "unavailable", "resource.getrusage(RUSAGE_SELF).ru_maxrss is unavailable"


def _rounding_allowance(bound: float) -> float:
    # Outward rounding to the least binary64 value incurs less than one ulp.
    # Exact zero needs no allowance; subnormal ulps remain representable.
    return math.ulp(bound) if bound else 0.0


def build_report(document: InputDocument, factor: int, *,
                 started_at: float | None = None,
                 source_hashes: dict[str, str] | None = None) -> dict:
    """Compute one complete finite report, with no output-side filesystem work."""
    started_at = time.perf_counter() if started_at is None else started_at
    if type(started_at) not in (int, float) or not math.isfinite(started_at):
        raise ValueError("started_at must be a finite monotonic-clock value")
    if not isinstance(document, InputDocument):
        raise ValueError("document must be an admitted InputDocument")
    if _IDENTIFIER.fullmatch(document.fixture_id) is None:
        raise ValueError("invalid admitted fixture_id")
    if _SHA256.fullmatch(document.input_sha256) is None:
        raise ValueError("invalid admitted input hash")
    if type(document.input_size_bytes) is not int or not 0 <= document.input_size_bytes <= MAX_INPUT_BYTES:
        raise ValueError("invalid admitted input size")
    case = kernel.validate_case(document.case)
    work = kernel.work_bound(case, factor)
    if work > kernel.MAX_WORK:
        raise ValueError(f"work bound {work} exceeds {kernel.MAX_WORK}")
    initial_hashes = implementation_hashes()
    if source_hashes is not None and source_hashes != initial_hashes:
        raise ValueError("implementation changed before rendering")
    rendered = kernel.render(case, factor)
    metadata = kernel.filter_metadata(factor) if case.frames else None
    sources = {source.source_id: source for source in case.sources}
    edges = []
    left_closed = [[False] * 9 for _ in case.keys]
    for edge in rendered.trajectory.edges:
        key = case.keys[edge.key_index]
        source = sources[key.source_ids9[edge.contact_index]]
        value, slope = kernel.source_value_and_slope(source, case.sample_rate_hz, edge.u)
        multiplier = key.gains9[edge.contact_index] * (1.0 if edge.closed_after else -1.0)
        frame, fraction = _display_coordinate(edge.u)
        edges.append({"exact_u": _exact_coordinate(edge.u), "frame": frame,
                      "fraction": fraction, "key_index": edge.key_index,
                      "contact_index": edge.contact_index, "closed_after": edge.closed_after,
                      "inside_observation": edge.u < case.frames,
                      "value_jump": multiplier * value,
                      "slope_jump_per_second": multiplier * slope})
        # The state immediately before N excludes physical crossings at N.
        if edge.u < case.frames:
            left_closed[edge.key_index][edge.contact_index] = edge.closed_after
    gate_jumps = []
    if case.frames:
        values, slopes = [], []
        for key, closed in zip(case.keys, left_closed):
            for connected, source_id, gain in zip(closed, key.source_ids9, key.gains9):
                if connected:
                    value, slope = kernel.source_value_and_slope(sources[source_id],
                                                                 case.sample_rate_hz, case.frames)
                    values.append(gain * value)
                    slopes.append(gain * slope)
        gate_jumps = [
            {"boundary": "start", "exact_u": _exact_coordinate(Fraction(0)),
             "frame": 0, "fraction": 0.0, "value_jump": 0.0,
             "slope_jump_per_second": 0.0, "limit": "ungated_right_limit"},
            {"boundary": "end", "exact_u": _exact_coordinate(Fraction(case.frames)),
             "frame": case.frames, "fraction": 0.0, "value_jump": -math.fsum(values),
             "slope_jump_per_second": -math.fsum(slopes),
             "limit": "negative_ungated_left_limit"},
        ]
    targets = [{"frame": target.frame, "fraction": target.fraction,
                "key_id": target.key_id, "target": target.target, "input_ordinal": ordinal}
               for ordinal, target in sorted(enumerate(case.targets),
                                             key=lambda row: (row[1].frame, row[1].fraction, row[0]))]
    final_keys = [{"key_id": key.key_id, "position": float(final.position),
                   "target": float(final.target), "closed": list(final.closed9)}
                  for key, final in zip(case.keys, rendered.trajectory.final_keys)]
    taps = 32 * factor + 1 if case.frames else 0
    observations = {
        "elapsed_seconds": 0.0,
        "elapsed_measurement": ("time.perf_counter; preflight/input/render/report construction; "
                                "excludes final serialization and atomic file replacement"),
        "peak_resident_bytes": None,
        "peak_resident_measurement": "unavailable",
        "peak_resident_unavailable_reason": None,
        "input_bytes": document.input_size_bytes, "report_bytes": 0,
        "source_count": len(case.sources), "key_count": len(case.keys),
        "target_count": len(targets), "edge_count": len(edges),
        "sample_count": len(rendered.samples),
        "cell_count": case.frames * factor + 1 if case.frames else 0,
        "cell_count_meaning": "declared centered grid; exact-zero routing bypasses cell allocation",
        "filter_coefficient_count": taps,
        "fir_product_bound": (case.frames + 33) * taps if case.frames else 0,
        "oracle_integrand_evaluations": 0,
        "observed_sample_peak": max((abs(sample) for sample in rendered.samples), default=0.0),
        "raw_bound_rounding": "exact rational sum rounded outward to the least binary64 upper bound",
        "raw_bound_rounding_allowance": _rounding_allowance(rendered.bound),
        "output_bound_meaning": "mathematical ideal bound; not a floating-point headroom gate",
        "sample_time_seconds": "absolute_host_frame / sample_rate_hz",
        "timing_model": "offline centered acausal convolution; no causal runtime latency claim",
        "observation_interval": "[0,frames); exactly zero outside; complete centered filter tails",
        "resource_gate_status": "single invocation only; complete-suite resources not qualified",
    }
    report = {
        "schema_version": 1, "model_id": kernel.MODEL_ID, "evidence_class": "synthetic",
        "fixture_id": document.fixture_id, "input_sha256": document.input_sha256,
        "implementation_sha256": initial_hashes, "python_version": platform.python_version(),
        "platform": platform.platform(), "sample_rate_hz": case.sample_rate_hz,
        "frames": case.frames, "factor": factor, "first_frame": rendered.first_frame,
        "time_offset_seconds": rendered.first_frame / case.sample_rate_hz,
        "samples": list(rendered.samples), "raw_bound": rendered.bound,
        "output_bound": rendered.bound * metadata["absolute_sum"] if metadata else 0.0,
        "work": work,
        "caps": {"input_bytes": MAX_INPUT_BYTES, "json_depth": MAX_JSON_DEPTH,
                 "invocation_work": kernel.MAX_WORK, "suite_elapsed_seconds": SUITE_ELAPSED_SECONDS,
                 "suite_peak_resident_bytes": SUITE_PEAK_RESIDENT_BYTES,
                 "suite_fir_products": 180_000_000, "suite_oracle_integrand_evaluations": 10_000_000,
                 "suite_report_bytes": MAX_REPORT_BYTES},
        "observations": observations, "targets": targets, "edges": edges,
        "final_keys": final_keys, "filter": metadata, "gate_jumps": gate_jumps,
    }
    if implementation_hashes() != initial_hashes:
        raise ValueError("implementation changed while rendering")
    observations["elapsed_seconds"] = time.perf_counter() - started_at
    peak, method, reason = _peak_resident()
    observations["peak_resident_bytes"] = peak
    observations["peak_resident_measurement"] = method
    observations["peak_resident_unavailable_reason"] = reason
    if observations["elapsed_seconds"] < 0 or observations["elapsed_seconds"] > SUITE_ELAPSED_SECONDS:
        raise ValueError("elapsed-time budget exceeded or invalid; invocation incomplete")
    if peak is not None and peak > SUITE_PEAK_RESIDENT_BYTES:
        raise ValueError("resident-memory budget exceeded; invocation incomplete")
    if peak is None:
        observations["resource_gate_status"] = "unavailable memory measurement; resource gate ineligible"
    return _finite_json(report)


def _finite_json(value: object) -> object:
    """Reject unsupported/nonfinite results and canonicalize every signed zero."""
    if value is None or type(value) in (str, bool, int):
        return value
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError("nonfinite report result")
        return value if value else 0.0
    if type(value) is list:
        return [_finite_json(item) for item in value]
    if type(value) is dict and all(type(key) is str for key in value):
        return {key: _finite_json(item) for key, item in value.items()}
    raise ValueError("unsupported report result type")


def encode_report(report: dict) -> bytes:
    """Validate and serialize the whole report before creating a temporary file."""
    _record(report, REPORT_FIELDS, "report")
    admitted = _finite_json(report)
    if type(admitted["observations"]) is not dict:
        raise ValueError("report observations must be an object")
    # The length includes its own decimal field. It reaches a fixed point as
    # soon as that field's digit count stabilizes; the file includes one newline.
    for _ in range(8):
        payload = (json.dumps(admitted, allow_nan=False, ensure_ascii=True,
                              sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        if len(payload) > MAX_REPORT_BYTES:
            raise ValueError("report exceeds the 32 MiB suite storage ceiling")
        if admitted["observations"].get("report_bytes") == len(payload):
            return payload
        admitted["observations"]["report_bytes"] = len(payload)
    raise ValueError("report size did not stabilize")


def atomic_write_report(plan: OutputPlan, report: dict) -> None:
    """Replace one destination only after all validation; preserve it on failure."""
    if not isinstance(plan, OutputPlan):
        raise ValueError("output requires an admitted path plan")
    payload = encode_report(report)
    _recheck_plan(plan)
    temporary = None
    try:
        descriptor, temporary = tempfile.mkstemp(prefix=".contact-switching-", suffix=".tmp",
                                                  dir=plan.output_path.parent)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        _recheck_plan(plan)
        os.replace(temporary, plan.output_path)
        temporary = None
    finally:
        if temporary is not None:
            os.unlink(temporary)

