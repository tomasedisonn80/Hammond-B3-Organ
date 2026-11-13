#!/usr/bin/env python3
"""Validate a nominal pedal CSV and publish a bounded standalone SVG.

Only the Python standard library is used. This checks structure, domains and
simple nominal state/algebra relations, not a source simulation or authenticity.
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
MAX_LINE_BYTES = 4096
METADATA_KEYS = (
    "hammond_pedal_trace_schema", "evidence_scope", "source_model", "manual_contact_model",
    "pedal_contact_model", "pedal_routing_model", "pedal_voice_model", "pedal_gain_law",
    "pedal_map_id", "pedal_map_raw_sha256", "pedal_map_canonical_sha256",
    "pedal_reference_a_sha256", "pedal_reference_b_sha256", "mixture_matrix",
    "pedal_position_gains", "pedal_weight_policy", "signal_units", "scenario", "scenario_version",
    "profile_id", "authoring_sha256", "profile_digest_scope", "sample_rate", "seed", "frames",
    "timing", "contact_bits_order", "pedal_targets_order", "manual_midi", "manual_drawbar_index",
    "tracked_tone_id", "tracked_frequency_hz", "tracked_source_peak", "profile_output_gain",
    "percussion", "row_count_limit", "byte_limit",
)
COLUMNS = (
    "frame", "sample_rate", "time_seconds", "pedal_position_0", "pedal_position_1",
    "brown", "red", "orange", "yellow", "mixture_0", "mixture_1", "pedal_output", "audio",
    "expression", "active_pedals", "pedal_targets", "contact_bits", "upper_down", "lower_down",
    "upper_route", "lower_route", "upper_bank", "lower_bank", "upper_drawbar", "lower_drawbar",
    "source_phase_before", "clock_after",
)
DECIMAL = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\Z")
UNSIGNED = re.compile(r"(?:0|[1-9][0-9]*)\Z")
LEFT, WIDTH, TIME_BINS, HEIGHT = 140.0, 1000.0, 1000, 1535
BUS_COLORS = ("#795536", "#b63c48", "#d16f22", "#9a7c0a")
MIX_COLORS = ("#087f8c", "#8154a0", "#173d50")


class PlotError(ValueError):
    """The input or publication does not meet the plotting contract."""


class Row(NamedTuple):
    frame: int
    sample_rate: int
    time_seconds: float
    pedal_position_0: int
    pedal_position_1: int
    brown: float
    red: float
    orange: float
    yellow: float
    mixture_0: float
    mixture_1: float
    pedal_output: float
    audio: float
    expression: float
    active_pedals: int
    pedal_targets: str
    contact_bits: str
    upper_down: int
    lower_down: int
    upper_route: int
    lower_route: int
    upper_bank: int
    lower_bank: int
    upper_drawbar: int
    lower_drawbar: int
    source_phase_before: float
    clock_after: int


class Trace(NamedTuple):
    metadata: Mapping[str, str]
    rows: tuple[Row, ...]
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
        "hammond_pedal_trace_schema": "1", "evidence_scope": "synthetic_engineering",
        "source_model": "ideal-shared-sine-v1", "manual_contact_model": "ideal-contacts-v1",
        "pedal_contact_model": "ideal-eight-contact-pedal-v1",
        "pedal_routing_model": "linear-pedal-bus-reference-v1",
        "pedal_voice_model": "nominal-static-pedal-mixture-v1",
        "pedal_gain_law": "linear-pedal-position-v1",
        "pedal_map_id": "atlas-derived-b3-c3-pedal-v1",
        "pedal_map_raw_sha256": "58a30850c08933a075cfcec04faeb2cb479f60bd9dda82ace3246552221623bd",
        "pedal_map_canonical_sha256": "7b2631a0c7d55a18f8225d4ee420e472c23b9f2809eec69865474eafce6f5fb2",
        "pedal_reference_a_sha256": "b8177479a5af16f4e6b8759313d90148a1213657c83f8a6e6533422bfa104ca1",
        "pedal_reference_b_sha256": "b8177479a5af16f4e6b8759313d90148a1213657c83f8a6e6533422bfa104ca1",
        "mixture_matrix": "0.5,0.25,0.125,0.125;0.125,0.5,0.25,0.125",
        "pedal_position_gains": "0,0.125,0.25,0.375,0.5,0.625,0.75,0.875,1",
        "pedal_weight_policy": "all-200-unit-positive-v1",
        "signal_units": "dimensionless_source_normalized", "scenario_version": "1",
        "profile_id": "nominal-unmeasured-v1",
        "profile_digest_scope": "declared_authoring_not_compiled_hash",
        "timing": "events_then_pre_render_state_then_one_render_then_historical_record",
        "contact_bits_order": "pedal_1_to_25_each_contact_0_to_7",
        "pedal_targets_order": "pedal_1_to_25", "manual_midi": "48",
        "manual_drawbar_index": "2", "tracked_tone_id": "25", "percussion": "off",
        "row_count_limit": "11520", "byte_limit": "8388608",
    }
    for key, expected in fixed.items():
        _require(metadata[key] == expected, f"metadata: unsupported {key}")
    _require(metadata["scenario"] in ("unmute", "overlap", "routing"),
             "metadata: unsupported scenario")
    _require(re.fullmatch(r"[0-9a-f]{64}", metadata["authoring_sha256"]) is not None,
             "metadata: invalid declared authoring digest")
    rate = _integer(metadata["sample_rate"], 44100, 96000, "sample_rate")
    _require(rate in (44100, 48000, 96000), "metadata: unsupported sample rate")
    _integer(metadata["seed"], 0, 2**64 - 1, "seed")
    frames = _integer(metadata["frames"], 1, MAX_ROWS, "frames")
    _require(frames == rate * 120 // 1000, "metadata: scenario must last 120 ms")
    frequency = _number(metadata["tracked_frequency_hz"], "tracked_frequency_hz")
    _require(2**-53 <= frequency / rate < 0.5, "metadata: unsupported source increment")
    for key in ("tracked_source_peak", "profile_output_gain"):
        value = _number(metadata[key], key)
        _require(0 <= value <= 1, f"metadata: {key} outside [0,1]")
    return MappingProxyType(metadata), rate, frames


def parse_trace(raw: bytes) -> Trace:
    """Accept the exact supported schema and retain SHA-256 of the original bytes."""
    _require(type(raw) is bytes and 0 < len(raw) <= MAX_TRACE_BYTES,
             "trace must be nonempty bytes, at most 8 MiB")
    _require(raw.endswith(b"\n") and b"\r" not in raw and b"\x00" not in raw,
             "trace must use LF endings, a final LF and no NUL bytes")
    try:
        lines = raw.decode("ascii").split("\n")[:-1]
    except UnicodeError as error:
        raise PlotError("trace must use the schema's ASCII-compatible fields") from error
    _require(len(lines) >= 39, "trace is missing metadata, header or rows")
    _require(all(len(line) <= MAX_LINE_BYTES for line in lines), "trace line exceeds 4096 bytes")
    metadata, rate, frames = _metadata(lines[:37])
    _require(lines[37] == ",".join(COLUMNS), "CSV header differs from schema 1")
    _require(len(lines) == 38 + frames, "CSV row count differs from declared frames")
    rows = []
    integers = {0: (0, frames - 1), 1: (rate, rate), 3: (0, 8), 4: (0, 8),
                14: (0, 25), 17: (0, 1), 18: (0, 1), 19: (0, 1), 20: (0, 1),
                21: (0, 1), 22: (0, 1), 23: (0, 8), 24: (0, 8), 26: (1, frames)}
    for frame, line in enumerate(lines[38:]):
        fields = line.split(",")
        _require(len(fields) == 27, f"frame {frame}: expected 27 fields")
        values = []
        for index, (name, token) in enumerate(zip(COLUMNS, fields)):
            label = f"frame {frame} {name}"
            if index in (15, 16):
                count = 25 if index == 15 else 200
                _require(len(token) == count and all(bit in "01" for bit in token),
                         f"{label}: expected exactly {count} bits")
                values.append(token)
            elif index in integers:
                values.append(_integer(token, *integers[index], label))
            else:
                values.append(_number(token, label))
        row = Row(*values)
        _require(row.frame == frame and row.clock_after == frame + 1,
                 f"frame {frame}: noncontiguous frame or next clock")
        expected_time = frame / rate
        _require(abs(row.time_seconds - expected_time) <= max(1e-15, 4 * math.ulp(expected_time)),
                 f"frame {frame}: time differs from frame/sample_rate")
        _require(0 <= row.expression <= 1 and 0 <= row.source_phase_before < 1,
                 f"frame {frame}: expression or phase outside supported domain")
        _require(row.active_pedals == row.pedal_targets.count("1"),
                 f"frame {frame}: held count disagrees with pedal targets")
        _require(row.contact_bits == "".join(bit * 8 for bit in row.pedal_targets),
                 f"frame {frame}: ideal contacts disagree with pedal targets")
        _require(all(abs(value) <= 50 for value in row[5:11]) and
                 abs(row.pedal_output) <= 100 and abs(row.audio) <= 102,
                 f"frame {frame}: signal exceeds the admitted nominal bound")
        # Algebraic consistency of recorded fields, not a re-render of sources.
        mix0 = (4 * row.brown + 2 * row.red + row.orange + row.yellow) / 8
        mix1 = (row.brown + 4 * row.red + 2 * row.orange + row.yellow) / 8
        pedal = (row.mixture_0 * row.pedal_position_0 +
                 row.mixture_1 * row.pedal_position_1) / 8
        _require(abs(row.mixture_0 - mix0) <= 2e-12 and
                 abs(row.mixture_1 - mix1) <= 2e-12 and
                 abs(row.pedal_output - pedal) <= 4e-12,
                 f"frame {frame}: recorded mixtures or pedal gain disagree")
        rows.append(row)
    return Trace(metadata, tuple(rows), hashlib.sha256(raw).hexdigest())


def load_trace(path: str | os.PathLike[str]) -> Trace:
    """Read a bounded regular file. Inputs are expected to be quiescent."""
    source = Path(path)
    _require(source.is_file(), "input must be an existing regular file")
    with source.open("rb") as stream:
        details = os.fstat(stream.fileno())
        _require(stat.S_ISREG(details.st_mode) and 0 <= details.st_size <= MAX_TRACE_BYTES,
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


def _y(value: float, top: float, height: float, low: float, high: float) -> float:
    return top + height * (high - value) / (high - low)


def _bins(count: int):
    bins = min(TIME_BINS, count)
    for index in range(bins):
        yield index * count // bins, (index + 1) * count // bins


def envelope_ranges(trace: Trace, column: str) -> tuple[tuple[int, int, float, float], ...]:
    """Retain every bin's actual minimum and maximum, including one-sample spikes."""
    ranges = []
    for first, end in _bins(len(trace.rows)):
        observed = [getattr(row, column) for row in trace.rows[first:end]]
        ranges.append((first, end, min(observed), max(observed)))
    return tuple(ranges)


def closed_intervals(values: Sequence[int]) -> tuple[tuple[int, int], ...]:
    """Return every closed sample interval [first,end), without decimation."""
    start = None
    intervals = []
    for frame in range(len(values) + 1):
        closed = frame < len(values) and values[frame] == 1
        if closed and start is None:
            start = frame
        elif not closed and start is not None:
            intervals.append((start, frame))
            start = None
    return tuple(intervals)


def _steps(trace: Trace, column: str, top: float, height: float) -> str:
    previous = getattr(trace.rows[0], column)
    pieces = [f'M{_f(LEFT)},{_f(_y(previous, top, height, 0, 8))}']
    for frame, row in enumerate(trace.rows[1:], 1):
        value = getattr(row, column)
        if value != previous:
            pieces.append(f'H{_f(_x(frame, len(trace.rows)))}V{_f(_y(value, top, height, 0, 8))}')
            previous = value
    pieces.append(f'H{_f(LEFT + WIDTH)}')
    return "".join(pieces)


def _scale(peak: float) -> float:
    if peak == 0:
        return 1.0
    # Preserve subnormal peaks without 10**-324 underflowing to zero.
    power = 10 ** max(-323, math.floor(math.log10(peak)))
    return next(factor * power for factor in (1, 2, 5, 10) if factor * power >= peak)


def render_svg(trace: Trace) -> bytes:
    """Draw validated rows; no external images, scripts, fonts or network links."""
    metadata, rows, digest = trace
    output, length = [], 0

    def add(part: str) -> None:
        nonlocal length
        length += len(part.encode("utf-8")) + 1
        _require(length <= MAX_SVG_BYTES, "plot exceeds 1 MiB; exact transitions are too complex")
        output.append(part)

    def panel(top: float, height: float) -> None:
        add(f'<rect x="24" y="{_f(top)}" width="1152" height="{_f(height)}" rx="12" class="panel"/>')

    def grid(top: float, height: float, low: float, high: float) -> None:
        for ms in range(0, 121, 20):
            x = LEFT + WIDTH * ms / 120
            add(f'<path d="M{_f(x)},{_f(top)}V{_f(top+height)}" class="grid"/>')
        for value in (low, (low + high) / 2, high):
            y = _y(value, top, height, low, high)
            add(f'<path d="M{_f(LEFT)},{_f(y)}H{_f(LEFT+WIDTH)}" class="grid"/>')
            add(_text(126, y + 4, f"{value:.3g}", "axis", "end"))

    def legend(x: float, y: float, label: str, color: str) -> None:
        add(f'<path d="M{_f(x)},{_f(y-4)}h22" stroke="{color}" stroke-width="3"/>')
        add(_text(x + 30, y, label, "small"))

    def signal(column: str, top: float, height: float, scale: float, color: str) -> None:
        pieces = []
        for first, end, low, high in envelope_ranges(trace, column):
            center = _x((first + end - 1) / 2, len(rows))
            pieces.append(f'M{_f(center)},{_f(_y(high, top, height, -scale, scale))}'
                          f'V{_f(_y(low, top, height, -scale, scale))}')
        add(f'<path id="{column.replace("_", "-")}-envelope" d="{"".join(pieces)}" '
            f'fill="none" stroke="{color}" stroke-width="1.1" opacity=".85" '
            f'data-bins="{min(TIME_BINS, len(rows))}"/>')

    def lane(values: Sequence[int], y: float, identifier: str, color: str) -> None:
        add(f'<path d="M{_f(LEFT)},{_f(y)}H{_f(LEFT+WIDTH)}" stroke="#edf1ee" stroke-width="7"/>')
        pieces = [f'M{_f(_x(first, len(rows)))},{_f(y)}H{_f(_x(end, len(rows)))}'
                  for first, end in closed_intervals(values)]
        add(f'<path id="{identifier}" d="{"".join(pieces)}" fill="none" '
            f'stroke="{color}" stroke-width="7"/>')

    title = f"Nominal pedals · {metadata['scenario'].capitalize()}"
    description = (
        "Synthetic engineering observations of an unmeasured nominal organ model. Five aligned "
        "views show two drawbar positions, four pedal buses, two pre-control mixtures and pedal "
        "output, all 25 pedal target/contact groups and independent manual routing, then final "
        "normalized audio. Every grouped contact bit is checked. State transitions retain exact "
        "sample boundaries; signal strokes retain each time bin's observed extrema. This is not "
        "a measured instrument, source replay, phase-continuity proof or acoustic calibration."
    )
    add('<?xml version="1.0" encoding="UTF-8"?>')
    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{HEIGHT}" '
        f'viewBox="0 0 1200 {HEIGHT}" role="img" aria-labelledby="plot-title plot-desc">')
    add(f'<title id="plot-title">{html.escape(title, quote=True)}</title>')
    add(f'<desc id="plot-desc">{html.escape(description, quote=True)}</desc>')
    provenance = {
        "plot_schema_version": 1, "trace_schema_version": 1, "trace_sha256": digest,
        "scenario": metadata["scenario"], "scenario_version": 1, "sample_rate": int(metadata["sample_rate"]),
        "seed": metadata["seed"], "frames": len(rows), "scope": "synthetic_engineering",
        "verification": "structure_domains_ideal_contacts_and_recorded_mixture_algebra_only",
        "signal_reduction": "min_max_per_time_bin", "time_bins": min(TIME_BINS, len(rows)),
        "state_transition_reduction": "none", "contact_bits_checked": 200,
        "contact_lane_grouping": "each_pedal_target_equals_all_eight_checked_contact_bits",
        "coordinate_precision_pixels": 0.001, "declared_profile_id": metadata["profile_id"],
        "declared_authoring_sha256": metadata["authoring_sha256"],
        "declared_map_sha256": metadata["pedal_map_raw_sha256"],
        "source_phase_plot": "omitted_original_values_remain_in_csv",
        "source_metadata": dict(metadata),
    }
    add('<metadata id="plot-provenance">' + html.escape(json.dumps(provenance, sort_keys=True), quote=True) + '</metadata>')
    add('<style>text{font-family:DejaVu Sans,Arial,sans-serif;fill:#183c45}'
        '.title{font-size:29px;font-weight:700}.section{font-size:18px;font-weight:700}'
        '.label{font-size:13px}.small{font-size:11px;fill:#4d666d}'
        '.axis{font-size:10px;fill:#4d666d}.mono{font-family:DejaVu Sans Mono,monospace;font-size:11px}'
        '.panel{fill:#fff;stroke:#dbe3de}.grid{fill:none;stroke:#e1e8e4;stroke-width:1}'
        '.steps{fill:none;stroke-width:2.4;stroke-linejoin:round}</style>')
    add(f'<rect width="1200" height="{HEIGHT}" fill="#f5f6f2"/>')
    add(_text(32, 49, title, "title"))
    add(_text(33, 76, "Synthetic engineering · nominal and unmeasured · dimensionless signals", "label"))
    add(_text(33, 100, f"{int(metadata['sample_rate']):,} Hz · seed {metadata['seed']} · "
              f"{len(rows):,} frames · 120 ms · trace schema 1 / scenario 1", "label"))
    add(_text(33, 122, "Each row pairs post-event controls and contacts with the same rendered sample; source phase is retained in the CSV.", "small"))

    panel(140, 160)
    add(_text(42, 167, "Pedal registration", "section"))
    add(_text(244, 167, "positions 0–8; every change retained", "small"))
    legend(740, 167, "Mixture 1", MIX_COLORS[0])
    legend(940, 167, "Mixture 2", MIX_COLORS[1])
    grid(187, 91, 0, 8)
    for index, color in enumerate(MIX_COLORS[:2]):
        add(f'<path id="pedal-position-{index}" d="{_steps(trace, "pedal_position_"+str(index), 187, 91)}" '
            f'class="steps" stroke="{color}"/>')

    panel(312, 188)
    add(_text(42, 339, "Four bus excitations", "section"))
    for x, name, color in zip((620, 750, 880, 1010), ("Brown", "Red", "Orange", "Yellow"), BUS_COLORS):
        legend(x, 339, name, color)
    scale = _scale(max(abs(value) for row in rows for value in row[5:9]))
    grid(360, 116, -scale, scale)
    for name, color in zip(("brown", "red", "orange", "yellow"), BUS_COLORS):
        signal(name, 360, 116, scale, color)

    panel(512, 198)
    add(_text(42, 539, "Mixtures and pedal output", "section"))
    for x, label, color in zip((620, 800, 980), ("Mixture 1 (pre)", "Mixture 2 (pre)", "Pedal P"), MIX_COLORS):
        legend(x, 539, label, color)
    scale = _scale(max(abs(value) for row in rows for value in row[9:12]))
    grid(560, 125, -scale, scale)
    for name, color in zip(("mixture_0", "mixture_1", "pedal_output"), MIX_COLORS):
        signal(name, 560, 125, scale, color)

    panel(722, 498)
    add(_text(42, 749, "Targets, contacts and manual independence", "section"))
    add(_text(560, 749, "solid = held target and all 8 closed ideal contacts", "small"))
    for pedal in range(25):
        y = 772 + 12 * pedal
        label = f"P{pedal+1:02d}" + (" *" if 7 <= pedal <= 11 else "")
        add(_text(126, y + 3.5, label, "axis", "end"))
        lane(tuple(int(row.pedal_targets[pedal]) for row in rows), y,
             f"pedal-{pedal+1:02d}-contacts", "#698e82" if 7 <= pedal <= 11 else "#2f726d")
    for name, y, label, color in (
        ("upper_down", 1086, "Upper key", "#4468a4"), ("lower_down", 1108, "Lower key", "#9b5b8a"),
        ("upper_route", 1130, "Upper route", "#4468a4"), ("lower_route", 1152, "Lower route", "#9b5b8a")):
        add(_text(126, y + 4, label, "axis", "end"))
        lane(tuple(getattr(row, name) for row in rows), y, name.replace("_", "-"), color)
    for ms in range(0, 121, 20):
        x = LEFT + WIDTH * ms / 120
        add(f'<path d="M{_f(x)},764V1160" class="grid" opacity=".65"/>')
    add(_text(42, 1181, "* P08–P12 include disconnected c1. Its physical contact bit is checked and stays visible within the eight-contact group.", "small"))
    add(_text(42, 1201, "Contact grouping is valid only for the declared ideal model. Cancel and division panics retain their separate lanes.", "small"))

    panel(1232, 208)
    peak = max(abs(row.audio) for row in rows)
    scale = _scale(peak)
    add(_text(42, 1259, "Final audio", "section"))
    add(_text(190, 1259, f"normalized float · peak {peak:.6g} · strokes show observed bin extrema, not an interpolated waveform", "small"))
    grid(1282, 110, -scale, scale)
    signal("audio", 1282, 110, scale, "#173d50")
    for ms in range(0, 121, 20):
        add(_text(LEFT + WIDTH * ms / 120, 1413, str(ms), "axis", "middle"))
    add(_text(640, 1460, "Time (ms)", "label", "middle"))
    add(_text(33, 1481, "Signal extrema retained in at most 1000 bins. State transitions are not downsampled. Coordinates round to 0.001 px.", "small"))
    add(_text(33, 1501, "Validation covers structure and stated field relations. No source replay, instrument authentication or physical calibration.", "small"))
    add(_text(33, 1523, "Trace SHA-256: " + digest, "mono"))
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
    """Validate/render fully, then publish a complete file without replacing a path."""
    destination = _destination(output_path)
    svg = render_svg(load_trace(input_path))
    with tempfile.TemporaryDirectory(prefix=".hammond-pedal-plot-", dir=destination.parent) as directory:
        temporary = Path(directory) / "plot.svg"
        with temporary.open("xb") as stream:
            _require(stream.write(svg) == len(svg), "could not write the complete plot")
            stream.flush()
        os.link(temporary, destination)


HELP = """Usage: plot_pedal_trace.py --input TRACE.csv --output PLOT.svg
       plot_pedal_trace.py --help

Validate a schema-1 nominal pedal trace and draw a standalone SVG.
Input <=8 MiB /11520 rows; output <=1 MiB. Both parents must already exist.
Signal extrema are retained in <=1000 bins; state transitions are not reduced.
Output is published by hard link without replacing files or symlinks.
Structural/algebra checks do not establish DSP replay or physical authenticity.
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
            _require(0 < len(value.encode("utf-8")) <= 4096 and "\x00" not in value,
                     "invalid path argument")
            options[flag] = value
        _require(set(options) == {"--input", "--output"}, "both input and output are required")
        write_plot(options["--input"], options["--output"])
        return 0
    except (PlotError, OSError, ValueError, UnicodeError) as error:
        print(f"plot_pedal_trace: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
