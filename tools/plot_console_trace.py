#!/usr/bin/env python3
"""Validate a nominal console CSV and publish a bounded standalone SVG.

Only the Python standard library is used. Validation covers schema, declarations,
domains, time and simple routing relationships, not DSP replay or authenticity.
"""

from __future__ import annotations

import hashlib
import html
import json
import math
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
from types import MappingProxyType
from typing import Mapping, NamedTuple, Sequence


MAX_TRACE_BYTES = 8 * 1024 * 1024
MAX_SVG_BYTES = 1024 * 1024
MAX_ROWS = 11520
METADATA_KEYS = (
    "hammond_console_trace_schema", "evidence_scope", "source_model", "contact_model",
    "percussion_model", "scenario", "scenario_version", "profile_id", "authoring_sha256",
    "profile_digest_scope", "sample_rate", "seed", "frames", "timing", "manual",
    "primary_midi", "companion_midi", "primary_tone_id", "companion_tone_id",
    "primary_frequency_hz", "companion_frequency_hz", "primary_source_peak",
    "companion_source_peak", "profile_output_gain", "initial_percussion",
    "sustained_drawbars", "row_count_limit", "byte_limit",
)
COLUMNS = (
    "frame", "time_seconds", "position", "target", "c0", "c1", "c2", "c3", "c4",
    "c5", "c6", "c7", "c8", "companion_position", "companion_target",
    "companion_c0", "companion_c1", "companion_c2", "companion_c3", "companion_c4",
    "companion_c5", "companion_c6", "companion_c7", "companion_c8", "readiness",
    "physical_detector", "eligible", "routed_detector", "percussion_gain",
    "upper_sustain_gain", "route_enabled", "selected_bank", "percussion_enabled",
    "primary_phase_turns", "companion_phase_turns", "audio",
)
INDEX = {name: index for index, name in enumerate(COLUMNS)}
BIT_COLUMNS = tuple(range(4, 13)) + tuple(range(15, 24)) + (25, 26, 27, 30, 31, 32)
UNIT_COLUMNS = (2, 3, 13, 14, 24, 29)
DECIMAL = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\Z")
UNSIGNED = re.compile(r"(?:0|[1-9][0-9]*)\Z")
LEFT, WIDTH, DURATION_MS = 130.0, 1010, 120.0
TEAL, ORANGE, PURPLE, INK = "#0d7c86", "#b56b24", "#6950a1", "#16323c"


class PlotError(ValueError):
    """The input or requested publication does not meet the plotting contract."""


class Trace(NamedTuple):
    metadata: Mapping[str, str]
    rows: tuple[tuple[float, ...], ...]
    sha256: str


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PlotError(message)


def _integer(token: str, low: int, high: int, label: str) -> int:
    _require(len(token) <= 20 and UNSIGNED.fullmatch(token) is not None,
             f"{label}: expected canonical unsigned integer")
    value = int(token)
    _require(low <= value <= high, f"{label}: out of range")
    return value


def _number(token: str, label: str) -> float:
    _require(len(token) <= 64 and DECIMAL.fullmatch(token) is not None,
             f"{label}: expected bounded decimal number")
    value = float(token)
    mantissa = re.split("[eE]", token)[0]
    _require(math.isfinite(value) and not (
        value == 0.0 and any(char in "123456789" for char in mantissa)),
        f"{label}: nonfinite or underflowing value")
    return value


def _metadata(lines: Sequence[str]) -> tuple[Mapping[str, str], int, int]:
    metadata = {}
    for key, line in zip(METADATA_KEYS, lines):
        prefix = f"# {key}="
        _require(line.startswith(prefix), f"metadata: expected {key} in schema order")
        value = line[len(prefix):]
        _require(0 < len(value) <= 128, f"metadata: invalid {key} length")
        metadata[key] = value
    fixed = {
        "hammond_console_trace_schema": "1", "evidence_scope": "synthetic_engineering",
        "source_model": "ideal-shared-sine-v1", "contact_model": "nominal-linear-travel-v1",
        "percussion_model": "shared-readiness-v1", "scenario_version": "1",
        "profile_id": "nominal-unmeasured-v1",
        "profile_digest_scope": "declared_authoring_not_compiled_hash",
        "timing": "after_events_before_render_and_advance", "manual": "upper",
        "primary_midi": "60", "companion_midi": "67",
        "initial_percussion": "on_second_normal_fast", "sustained_drawbars": "all_zero",
        "row_count_limit": "11520", "byte_limit": "8388608",
    }
    for key, expected in fixed.items():
        _require(metadata[key] == expected, f"metadata: unsupported {key}")
    _require(metadata["scenario"] in ("partial", "legato", "routing"),
             "metadata: unsupported scenario")
    _require(re.fullmatch(r"[0-9a-f]{64}", metadata["authoring_sha256"]) is not None,
             "metadata: invalid declared authoring digest")
    rate = _integer(metadata["sample_rate"], 44100, 96000, "sample_rate")
    _require(rate in (44100, 48000, 96000), "metadata: unsupported sample rate")
    _integer(metadata["seed"], 0, 2**64 - 1, "seed")
    frames = _integer(metadata["frames"], 1, MAX_ROWS, "frames")
    _require(frames == rate * 120 // 1000, "metadata: scenario must last 120 ms")
    for prefix in ("primary", "companion"):
        _integer(metadata[f"{prefix}_tone_id"], 13, 91, f"{prefix}_tone_id")
        frequency = _number(metadata[f"{prefix}_frequency_hz"], f"{prefix}_frequency_hz")
        _require(2**-53 <= frequency / rate < 0.5, "metadata: unsupported source increment")
        peak = _number(metadata[f"{prefix}_source_peak"], f"{prefix}_source_peak")
        _require(0 <= peak <= 1, "metadata: source peak outside [0,1]")
    gain = _number(metadata["profile_output_gain"], "profile_output_gain")
    _require(0 <= gain <= 1, "metadata: output gain outside [0,1]")
    return MappingProxyType(metadata), rate, frames


def parse_trace(raw: bytes) -> Trace:
    """Validate the exact schema-1 representation; retain a hash of its bytes."""
    _require(type(raw) is bytes and 0 < len(raw) <= MAX_TRACE_BYTES,
             "trace must be nonempty bytes, at most 8 MiB")
    _require(raw.endswith(b"\n") and b"\r" not in raw and b"\x00" not in raw,
             "trace must use LF endings, a final LF and no NUL bytes")
    try:
        lines = raw.decode("ascii").split("\n")[:-1]
    except UnicodeError as error:
        raise PlotError("trace must use the schema's ASCII-compatible fields") from error
    _require(len(lines) >= 30, "trace is missing metadata, header or rows")
    metadata, rate, frames = _metadata(lines[:28])
    _require(lines[28] == ",".join(COLUMNS), "CSV header differs from schema 1")
    _require(len(lines) == 29 + frames, "CSV row count differs from declared frames")
    rows = []
    for frame, line in enumerate(lines[29:]):
        _require(len(line) <= 4096, f"frame {frame}: row exceeds 4096 bytes")
        fields = line.split(",")
        _require(len(fields) == 36, f"frame {frame}: expected 36 fields")
        _require(fields[0] == str(frame), f"frame {frame}: noncontiguous frame index")
        values = tuple(_number(token, f"frame {frame} {column}")
                       for token, column in zip(fields, COLUMNS))
        expected_time = frame / rate
        _require(abs(values[1] - expected_time) <= max(1e-15, 4 * math.ulp(expected_time)),
                 f"frame {frame}: time differs from frame/sample_rate")
        for index in BIT_COLUMNS:
            _require(fields[index] in ("0", "1"), f"frame {frame}: invalid {COLUMNS[index]} bit")
        for index in UNIT_COLUMNS:
            _require(0 <= values[index] <= 1, f"frame {frame}: {COLUMNS[index]} outside [0,1]")
        _require(0 <= values[28] <= 1.5, f"frame {frame}: percussion gain outside [0,1.5]")
        _require(0 <= values[33] < 1 and 0 <= values[34] < 1,
                 f"frame {frame}: phase outside [0,1)")
        # Two physical branches, each peak <=1, output gain <=1 and percussion
        # gain <=1.5. Float output is deliberately not constrained to PCM full scale.
        _require(abs(values[35]) <= 3, f"frame {frame}: audio exceeds two-branch bound")
        physical = int(bool(values[12] or values[23]))
        eligible = int(bool(values[30] and values[31] and values[32]))
        _require(values[25] == physical and values[26] == eligible and
                 values[27] == physical * eligible,
                 f"frame {frame}: detector/eligibility relationships disagree")
        rows.append(values)
    return Trace(metadata, tuple(rows), hashlib.sha256(raw).hexdigest())


def load_trace(path: str | os.PathLike[str]) -> Trace:
    """Read an existing regular file with an independent byte cap."""
    source = Path(path)
    _require(source.is_file(), "input must be an existing regular file")
    with source.open("rb") as stream:
        details = os.fstat(stream.fileno())
        _require(stat.S_ISREG(details.st_mode) and details.st_size <= MAX_TRACE_BYTES,
                 "input must be a regular file no larger than 8 MiB")
        raw = stream.read(MAX_TRACE_BYTES + 1)
    return parse_trace(raw)


def _f(value: float) -> str:
    return format(value, ".3f").rstrip("0").rstrip(".") or "0"


def _text(x: float, y: float, value: str, style: str = "label", anchor: str = "start") -> str:
    return (f'<text x="{_f(x)}" y="{_f(y)}" class="{style}" text-anchor="{anchor}">'
            f'{html.escape(value, quote=True)}</text>')


def _x(frame: float, frames: int) -> float:
    return LEFT + frame * WIDTH / frames


def _y(value: float, top: float, height: float, low: float = 0, high: float = 1) -> float:
    return top + height * (high - value) / (high - low)


def _bins(count: int):
    for column in range(min(WIDTH, count)):
        yield column * count // min(WIDTH, count), (column + 1) * count // min(WIDTH, count)


def _trajectory(trace: Trace, column: str, top: float, height: float) -> str:
    """Keep first/min/max/last observations in every horizontal time bin."""
    index = INDEX[column]
    points = []
    for first, end in _bins(len(trace.rows)):
        choices = {first, end - 1,
                   min(range(first, end), key=lambda i: trace.rows[i][index]),
                   max(range(first, end), key=lambda i: trace.rows[i][index])}
        for frame in sorted(choices):
            points.append(f'{_f(_x(frame, len(trace.rows)))},{_f(_y(trace.rows[frame][index], top, height))}')
    return " ".join(points)


def _steps(trace: Trace, column: str, top: float, height: float) -> str:
    """Retain every recorded target transition, including its exact frame."""
    index = INDEX[column]
    previous = trace.rows[0][index]
    pieces = [f'M{_f(LEFT)},{_f(_y(previous, top, height))}']
    for frame, row in enumerate(trace.rows[1:], 1):
        if row[index] != previous:
            previous = row[index]
            pieces.append(f'H{_f(_x(frame, len(trace.rows)))}V{_f(_y(previous, top, height))}')
    pieces.append(f'H{_f(LEFT + WIDTH)}')
    return "".join(pieces)


def _closed_intervals(trace: Trace, column: str, y: float) -> str:
    """Exact sample-grid on intervals; the final sample occupies one interval."""
    index = INDEX[column]
    start = None
    parts = []
    for frame in range(len(trace.rows) + 1):
        closed = frame < len(trace.rows) and trace.rows[frame][index] == 1
        if closed and start is None:
            start = frame
        elif not closed and start is not None:
            parts.append(f'M{_f(_x(start, len(trace.rows)))},{_f(y)}H{_f(_x(frame, len(trace.rows)))}')
            start = None
    return "".join(parts)


def _audio_range(trace: Trace, top: float, height: float, scale: float) -> str:
    parts = []
    for first, end in _bins(len(trace.rows)):
        samples = [row[35] for row in trace.rows[first:end]]
        center = _x((first + end - 1) / 2, len(trace.rows))
        parts.append(f'M{_f(center)},{_f(_y(max(samples), top, height, -scale, scale))}'
                     f'V{_f(_y(min(samples), top, height, -scale, scale))}')
    return "".join(parts)


def _amplitude_scale(peak: float) -> float:
    if peak == 0:
        return 1.0
    power = 10 ** math.floor(math.log10(peak))
    return next(factor * power for factor in (1, 2, 5, 10) if factor * power >= peak)


def render_svg(trace: Trace) -> bytes:
    """Draw validated observations without external fonts, images or scripts."""
    metadata, rows, digest = trace
    output, length = [], 0

    def add(part: str) -> None:
        nonlocal length
        length += len(part.encode("utf-8")) + 1
        _require(length <= MAX_SVG_BYTES, "plot exceeds 1 MiB; too many exact transitions")
        output.append(part)

    def panel(y: float, height: float) -> None:
        add(f'<rect x="24" y="{_f(y)}" width="1152" height="{_f(height)}" rx="12" class="panel"/>')

    def grid(top: float, height: float, low: float = 0, high: float = 1,
             labels: bool = True) -> None:
        for millisecond in range(0, 121, 20):
            x = LEFT + WIDTH * millisecond / DURATION_MS
            add(f'<path d="M{_f(x)},{_f(top)}V{_f(top+height)}" class="grid"/>')
        for value in (low, (low + high) / 2, high):
            y = _y(value, top, height, low, high)
            add(f'<path d="M{_f(LEFT)},{_f(y)}H{_f(LEFT+WIDTH)}" class="grid"/>')
            if labels:
                add(_text(116, y + 4, f"{value:.3g}", "axis", "end"))

    title = f"Nominal console · {metadata['scenario'].capitalize()}"
    description = (
        "Synthetic engineering trace of an unmeasured nominal organ model. Four time-aligned views "
        "show key position and target, shared percussion readiness and detector state, nine contacts "
        "for each tracked key, and per-bin audio minima and maxima. Contact and target changes retain "
        "their recorded sample boundaries; trajectory curves connect retained observations. "
        "Structural validation does not establish DSP correctness or physical authenticity."
    )
    add('<?xml version="1.0" encoding="UTF-8"?>')
    add('<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1150" '
        'viewBox="0 0 1200 1150" role="img" aria-labelledby="plot-title plot-desc">')
    add(f'<title id="plot-title">{html.escape(title, quote=True)}</title>')
    add(f'<desc id="plot-desc">{html.escape(description, quote=True)}</desc>')
    provenance = {"plot_schema_version": 1, "trace_schema_version": 1,
                  "trace_sha256": digest, "scenario": metadata["scenario"],
                  "scenario_version": 1, "sample_rate": metadata["sample_rate"],
                  "seed": metadata["seed"], "frames": len(rows),
                  "scope": "synthetic_engineering", "verification": "structure_domains_and_routing_only",
                  "trajectory_reduction": "first_min_max_last_per_time_bin",
                  "audio_reduction": "min_max_per_time_bin", "time_bins": min(WIDTH, len(rows)),
                  "contact_target_reduction": "none", "coordinate_precision_pixels": 0.001,
                  "declared_authoring_sha256": metadata["authoring_sha256"]}
    add('<metadata id="plot-provenance">' + html.escape(json.dumps(provenance, sort_keys=True), quote=True) + '</metadata>')
    add('<style>text{font-family:DejaVu Sans,Arial,sans-serif;fill:#16323c} '
        '.title{font-size:29px;font-weight:700}.section{font-size:18px;font-weight:700}'
        '.label{font-size:13px}.axis{font-size:11px;fill:#52666d}.small{font-size:11px;fill:#52666d}'
        '.mono{font-family:DejaVu Sans Mono,monospace;font-size:11px;fill:#52666d}'
        '.panel{fill:#fff;stroke:#dbe2df}.grid{fill:none;stroke:#e1e8e5;stroke-width:1}'
        '.curve{fill:none;stroke-width:2;stroke-linejoin:round;stroke-linecap:round}'
        '.target{fill:none;stroke-width:1.3;stroke-dasharray:5 4;opacity:.7}'
        '</style>')
    add('<rect width="1200" height="1150" fill="#f5f6f2"/>')
    add(_text(32, 49, title, "title"))
    add(_text(33, 76, "Synthetic engineering · nominal and unmeasured", "label"))
    info = (f"{int(metadata['sample_rate']):,} Hz  ·  seed {metadata['seed']}  ·  "
            f"{len(rows):,} frames  ·  120 ms  ·  trace schema 1 / scenario 1")
    add(_text(33, 100, info, "label"))
    add(_text(33, 122, "Rows describe state after events, before the same sample is rendered and advanced.", "small"))

    panel(140, 201)
    add(_text(42, 166, "Key travel", "section"))
    add(_text(176, 166, "normalized position; dashed lines show targets", "small"))
    add(_text(797, 166, "Primary · MIDI 60", "small"))
    add(f'<path d="M769,162H789" stroke="{TEAL}" stroke-width="3"/>')
    add(_text(992, 166, "Companion · MIDI 67", "small"))
    add(f'<path d="M964,162H984" stroke="{ORANGE}" stroke-width="3"/>')
    grid(184, 140)
    for prefix, color in (("", TEAL), ("companion_", ORANGE)):
        name = "primary" if not prefix else "companion"
        add(f'<path id="{name}-target" d="{_steps(trace, prefix + "target", 184, 140)}" '
            f'class="target" stroke="{color}"/>')
        add(f'<polyline id="{name}-position" points="{_trajectory(trace, prefix + "position", 184, 140)}" '
            f'class="curve" stroke="{color}"/>')

    panel(353, 203)
    add(_text(42, 379, "Shared percussion", "section"))
    add(_text(260, 379, "readiness q; detector bars retain every recorded transition", "small"))
    grid(393, 100)
    add(f'<polyline id="readiness" points="{_trajectory(trace, "readiness", 393, 100)}" '
        f'class="curve" stroke="{PURPLE}"/>')
    for column, y, opacity, label in (("physical_detector", 517, ".45", "Physical"),
                                      ("routed_detector", 539, "1", "Routed")):
        add(_text(116, y + 4, label, "axis", "end"))
        add(f'<path d="M130,{y}H1140" stroke="#eef0ef" stroke-width="8"/>')
        add(f'<path id="{column.replace("_", "-")}" d="{_closed_intervals(trace, column, y)}" '
            f'fill="none" stroke="{PURPLE}" stroke-width="8" opacity="{opacity}"/>')

    panel(568, 271)
    add(_text(42, 595, "Contact closures", "section"))
    add(_text(247, 595, "solid = closed · c8 is the physical percussion detector", "small"))
    for prefix, top, color, label in (("", 620, TEAL, "MIDI 60"),
                                      ("companion_", 735, ORANGE, "MIDI 67")):
        add(_text(42, top + 4, label, "small"))
        for contact in range(9):
            y = top + contact * 11
            add(_text(116, y + 4, f"c{contact}", "axis", "end"))
            add(f'<path d="M130,{y}H1140" stroke="#edf1ef" stroke-width="7"/>')
            name = "primary" if not prefix else "companion"
            add(f'<path id="{name}-c{contact}" d="{_closed_intervals(trace, prefix + "c" + str(contact), y)}" '
                f'fill="none" stroke="{color}" stroke-width="7"/>')
    for millisecond in range(0, 121, 20):
        x = LEFT + WIDTH * millisecond / DURATION_MS
        add(f'<path d="M{_f(x)},609V830" class="grid" opacity=".55"/>')

    panel(851, 194)
    peak = max(abs(row[35]) for row in rows)
    scale = _amplitude_scale(peak)
    add(_text(42, 878, "Audio", "section"))
    add(_text(118, 878, f"normalized float · peak {peak:.6g} · each stroke is a time-bin min/max range", "small"))
    grid(895, 116, -scale, scale)
    add(f'<path id="audio-envelope" d="{_audio_range(trace, 895, 116, scale)}" '
        f'fill="none" stroke="{INK}" stroke-width="1.1" data-bins="{min(WIDTH, len(rows))}"/>')
    for millisecond in range(0, 121, 20):
        x = LEFT + WIDTH * millisecond / DURATION_MS
        add(_text(x, 1030, str(millisecond), "axis", "middle"))
    add(_text(635, 1065, "Time (ms)", "label", "middle"))
    add(_text(33, 1089, "Trajectories retain first/min/max/last samples per time bin. Contact and target changes are not downsampled.", "small"))
    add(_text(33, 1108, "Validation: structure, domains and routing relations. No DSP replay, hardware authentication or calibration.", "small"))
    add(_text(33, 1131, "Trace SHA-256: " + digest, "mono"))
    add('</svg>')
    return ("\n".join(output) + "\n").encode("utf-8")


def _destination(path: str | os.PathLike[str]) -> Path:
    destination = Path(path)
    _require(not os.path.lexists(destination), "output already exists; it will not be replaced")
    parent = destination.parent.resolve(strict=True)
    _require(parent.is_dir() and destination.name not in ("", ".", ".."),
             "output parent must be an existing directory")
    return parent / destination.name


def write_plot(input_path: str | os.PathLike[str], output_path: str | os.PathLike[str]) -> None:
    """Preflight and render completely, then atomically publish without clobbering."""
    destination = _destination(output_path)
    trace = load_trace(input_path)
    svg = render_svg(trace)
    with tempfile.TemporaryDirectory(prefix=".hammond-plot-", dir=destination.parent) as directory:
        temporary = Path(directory) / "plot.svg"
        with temporary.open("xb") as stream:
            _require(stream.write(svg) == len(svg), "could not write the complete plot")
            stream.flush()
        os.link(temporary, destination)


HELP = """Usage: plot_console_trace.py --input TRACE.csv --output PLOT.svg
       plot_console_trace.py --help

Validate a schema-1 nominal console trace and draw a standalone SVG.
Input <=8 MiB /11520 rows; output <=1 MiB. Both parents must already exist.
Output is published by hard link without replacing files or symlinks.
Structural validation does not establish DSP replay or physical authenticity.
"""


def main(arguments: Sequence[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if arguments is None else arguments)
    try:
        if arguments == ["--help"]:
            print(HELP, end="")
            return 0
        _require(len(arguments) == 4, "expected exactly --input TRACE.csv --output PLOT.svg")
        options = {}
        for flag, value in zip(arguments[::2], arguments[1::2]):
            _require(flag in ("--input", "--output") and flag not in options,
                     "unknown or repeated option")
            _require(0 < len(value) <= 4096 and "\x00" not in value, "invalid path argument")
            options[flag] = value
        _require(set(options) == {"--input", "--output"}, "both input and output are required")
        write_plot(options["--input"], options["--output"])
        return 0
    except (PlotError, OSError, ValueError) as error:
        print(f"plot_console_trace: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
