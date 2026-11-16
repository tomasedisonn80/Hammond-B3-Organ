#!/usr/bin/env python3
"""Bounded A50 proposal audit: coefficients, indices and exact rational examples.

No audio render, trajectory execution, quadrature, native build or broad test.
Candidate coefficients are inspected and compared with the published equation;
this is not the independent full-window audio oracle required for admission.
"""

import ast
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import platform
import struct
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).with_suffix(".json")
BASE = "af2b74760ee195c9497b314a1a29172f5238dd44"
L, H, TICKS = 256, 16, 65536
INPUTS = (
    "docs/research/CAUSAL_CONTACT_AUDIO_NEXT.md",
    "docs/CAUSAL_CONTACT_GRID_CONTRACT.md",
    "docs/FRACTIONAL_CONTACT_REFERENCE.md",
    "docs/CONTACT_SWITCHING_VALIDATION.md",
    "docs/CONTACT_STREAMING_NEXT_DESIGN.md",
    "include/hammond/research/CausalContactGrid.h",
    "src/research/CausalContactGrid.cpp",
    "tools/fractional_contact_reference.py",
    "tools/contact_switching_io.py",
    "tools/contact_switching_oracle.py",
    "docs/development/2026-11-15-streaming-continuation/reports/A38-audio-index-audit.json",
)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.check_output(("git", *args), cwd=ROOT)


def fraction_record(value):
    return {
        "numerator": str(value.numerator),
        "denominator": str(value.denominator),
        "numerator_bits": abs(value.numerator).bit_length(),
        "denominator_bits": value.denominator.bit_length(),
        "binary64_hex": float(value).hex(),
    }


def interval_record(a, b):
    assert a < b
    return {
        "a": fraction_record(a), "b": fraction_record(b),
        "width": fraction_record(b - a),
        "midpoint": fraction_record((a + b) / 2),
        "same_binary64_endpoints": float(a) == float(b),
        "rounded_endpoint_difference": float(b) - float(a),
    }


before = {path: digest((ROOT / path).read_bytes()) for path in INPUTS}
spec = importlib.util.spec_from_file_location(
    "a50_inspected_reference", ROOT / "tools/fractional_contact_reference.py")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
normalizer, coefficients = module.filter_coefficients(L)

# Direct evaluation of the documented equation, without candidate helpers.
# At L256 only r=0 reaches the small-argument branch, whose value is exactly 1.
independent_raw = []
for r in range(-H * L, H * L + 1):
    v = r / L
    if abs(v) >= H:
        value = 0.0
    else:
        angle = math.pi * (0.9 * v)
        sinc = 1.0 if angle == 0.0 else math.sin(angle) / angle
        window = (0.42 + 0.5 * math.cos(math.pi * v / H)
                  + 0.08 * math.cos(math.tau * v / H))
        value = 0.9 * sinc * window
    independent_raw.append(value)
independent_z = math.fsum(independent_raw)
independent_coefficients = tuple(value / independent_z if value else 0.0
                                 for value in independent_raw)
assert independent_coefficients == coefficients
assert len(coefficients) == 8193
assert coefficients == coefficients[::-1]
assert struct.pack(">d", coefficients[0]) == b"\0" * 8
assert struct.pack(">d", coefficients[-1]) == b"\0" * 8
assert abs(math.fsum(coefficients) - 1.0) <= 2e-14

# Check all proposed nonempty lengths and every stored host output position.
# Only index arithmetic is evaluated; no cells or audio samples are rendered.
checked_positions = 0
for frames in range(1, 257):
    process = tuple(range(frames))
    drain = tuple(range(frames, frames + 33))
    shifted = tuple(m - H for m in process + drain)
    assert shifted == tuple(range(-H, frames + H + 1))
    assert len(drain) == 33 and len(shifted) == frames + 33
    for m in process + drain:
        first = max(0, (m - 32) * L)
        last = min(frames * L, m * L)
        for j in {first, last, min(last, first + 1), max(first, last - 1)}:
            assert (m - H) * L - j + H * L == m * L - j
            assert 0 <= m * L - j <= 32 * L
        lo = max(0, (m - 32) * L + 1)
        hi = min(frames * L, m * L - 1)
        if lo <= hi:
            assert 2 * hi + 1 < 2 * L * m
            assert 1 <= m * L - hi <= m * L - lo < 32 * L
        if m in (0, frames + 32):
            assert first == last
            assert coefficients[m * L - first] == 0.0
        checked_positions += 1

rows = []
for frames in (0, 1, 2, 31, 32, 33, 255, 256):
    rows.append({
        "frames": frames,
        "process_m": [0, frames - 1] if frames else None,
        "drain_m": [frames, frames + 32] if frames else None,
        "reference_n": [-H, frames + H] if frames else None,
        "sample_count": frames + 33 if frames else 0,
    })
for j in (0, 1, 255 * L, 256 * L):
    assert Fraction(2 * j - 1, 2 * L) * TICKS == 256 * j - 128
    assert Fraction(2 * j + 1, 2 * L) * TICKS == 256 * j + 128

# Both examples can be realized by one key using separate press/release speeds.
# They expose exact-width/midpoint needs beyond the grid's uint64 comparator.
d1, d2 = 2**32 - 1, 2**32 - 2
t = 255 * TICKS - 1
a = (Fraction(t) + Fraction(d1 - 1, d1)) / TICKS
b = (Fraction(t + 1) + Fraction(1, d2)) / TICKS
thin = interval_record(a, b)
assert thin["same_binary64_endpoints"]
assert thin["width"]["denominator_bits"] > 64
cell = 256 * L - 1
t = 256 * cell - 128
a = (Fraction(t) + Fraction(1, d1)) / TICKS
b = (Fraction(t + 255) + Fraction(1, d2)) / TICKS
wide = interval_record(a, b)
assert Fraction(2 * cell - 1, 2 * L) < a < b < Fraction(2 * cell + 1, 2 * L)
assert wide["width"]["numerator_bits"] > 64
assert wide["midpoint"]["numerator_bits"] > 64

# Constructive burst count, from the affine grid equation without grid code:
# four keys, all contacts off=0/on=1, both speeds UINT32_MAX; command all keys
# to 1 at even ticks and 0 at odd ticks 0..127. Every leg arrives after 1/s.
# All 4608 edges and 2304 connected pieces fit in the gated half of cell zero.
burst_roots = tuple(Fraction(tick) + Fraction(1, d1) for tick in range(128))
assert all(0 < root < 128 for root in burst_roots)
burst_widths = tuple(burst_roots[i + 1] - burst_roots[i]
                     for i in range(0, 128, 2))
assert all(width == 1 for width in burst_widths)
burst_commands, burst_edges, burst_pieces = 4 * 128, 36 * 128, 36 * len(burst_widths)
assert (burst_commands, burst_edges, burst_pieces) == (512, 4608, 2304)

# Bounded sine-integral example: identical mathematics need not have identical
# binary64 results when an implementation adds a callback-dependent split.
def analytic(a, b, frequency, phase):
    width = b - a
    x = math.pi * (frequency * float(width))
    sinc = 1.0 if x == 0.0 else math.sin(x) / x
    return (float(width * L)
            * math.sin(math.tau * (phase + frequency * float((a + b) / 2)))
            * sinc)


split_example = None
split_candidates = 0
for center in (1, 17, 255):
    for frequency in (0.1, 0.4, 0.45):
        for phase in (0.137, 0.25):
            split_candidates += 1
            a = Fraction(center) - Fraction(1, 2 * L)
            b = Fraction(center) + Fraction(1, 2 * L)
            whole = analytic(a, b, frequency, phase)
            pieces = math.fsum((analytic(a, Fraction(center), frequency, phase),
                               analytic(Fraction(center), b, frequency, phase)))
            if whole != pieces and split_example is None:
                split_example = {
                    "center": center, "frequency_cycles_per_frame": frequency,
                    "phase_turns": phase, "whole_hex": whole.hex(),
                    "split_hex": pieces.hex(), "difference": pieces - whole,
                }
assert split_example is not None
small = 2.0**-54
assert math.fsum((1.0, small, -1.0)) == small
assert math.fsum((math.fsum((1.0, small)), -1.0)) == 0.0
subnormal = float.fromhex("0x0.0000000000001p-1022")
exact_product = Fraction.from_float(subnormal)**2
assert exact_product > 0 and subnormal * subnormal == 0.0
assert math.nextafter(float(exact_product), math.inf) == subnormal

work = []
for frames in (256, 4096):
    terms = {
        "tap_products_ceiling": (frames + 33) * (32 * L + 1),
        "cell_route_ceiling": (frames * L + 1) * 36,
        "command_term": 18 * 512,
        "coefficient_term": 32 * L + 1,
    }
    work.append({"frames": frames, "terms": terms, "W": sum(terms.values()),
                 "within_original_20_million": sum(terms.values()) <= 20_000_000})
assert work[0]["W"] == 4_744_518 and work[1]["W"] == 71_595_078
duration_examples = []
for rate in (44100, 48000, 96000):
    for speed in (1, 1_000_000, d1):
        duration = Fraction(2**32, rate * speed)
        assert duration.denominator & (duration.denominator - 1)
        assert Fraction.from_float(float(duration)) != duration
        duration_examples.append({"rate": rate, "speed": speed,
                                  "seconds": fraction_record(duration),
                                  "within_offline_duration_range":
                                  Fraction(1, 10000) <= duration <= 1})

# Independent lineage check: A45 changes filesystem identity, not parser/math.
io_current = (ROOT / "tools/contact_switching_io.py").read_text()
io_published = git("show", BASE + ":tools/contact_switching_io.py").decode()
parser_names = ("_record", "_array", "_unique_object", "_json_integer",
                "_json_float", "_invalid_constant", "_check_depth", "parse_input")


def parser_segments(source):
    return {node.name: ast.get_source_segment(source, node)
            for node in ast.parse(source).body
            if isinstance(node, ast.FunctionDef) and node.name in parser_names}


old_parser, current_parser = parser_segments(io_published), parser_segments(io_current)
assert old_parser == current_parser and len(current_parser) == len(parser_names)
math_path = "tools/fractional_contact_reference.py"
assert git("show", BASE + ":" + math_path) == (ROOT / math_path).read_bytes()
after = {path: digest((ROOT / path).read_bytes()) for path in INPUTS}
assert before == after
report = {
    "worker": "/root/w09_a50", "wave": 9,
    "status": "independent bounded proposal checks passed; audio contract remains unadmitted",
    "observed_utc": datetime.now(timezone.utc).isoformat(),
    "head": git("rev-parse", "HEAD").decode().strip(),
    "head_tree": git("rev-parse", "HEAD^{tree}").decode().strip(),
    "cwd": str(ROOT), "python": sys.version, "platform": platform.platform(),
    "command": "python3 -B docs/development/2026-11-15-streaming-continuation/reports/A50-audio-contract-audit.py",
    "script_sha256": digest(Path(__file__).read_bytes()),
    "input_sha256": before, "inputs_unchanged_through_check": before == after,
    "filter": {
        "L": L, "H": H, "beta": 0.45, "count": len(coefficients),
        "normalizer": normalizer, "sum": math.fsum(coefficients),
        "absolute_sum": math.fsum(map(abs, coefficients)),
        "coefficient_sha256": digest(b"".join(struct.pack(">d", x) for x in coefficients)),
        "positive_zero_endpoints": True, "exact_mirrored_symmetry": True,
        "independent_equation_coefficients_byte_equal": True,
    },
    "indices": {
        "nonempty_lengths_checked": 256, "output_positions_checked": checked_positions,
        "coefficient_index": "m*L-j", "reference_index": "n=m-16",
        "potential_nonzero_j": "(m-32)*L+1 .. m*L-1, clipped to 0..N*L",
        "newest_cell_ends_before_output_by_frames": "1/512",
        "D15_newest_cell_end_after_output_by_frames": "511/512",
        "phase_zero_decimation": True, "rows": rows,
        "early_coefficient_witness_c255": coefficients[L - 1],
        "gate_cell0_interval": ["0", "1/512"],
        "gate_cellNL_interval": ["N-1/512", "N"],
    },
    "arithmetic": {
        "same_display_actual_route": {
            "press_speed": d1, "release_speed": d2,
            "press_tick": 255 * TICKS - 1, "release_tick": 255 * TICKS,
            "on": d1 - 1, "off": d1 - 2,
            "press_target": d1 - 1, "release_target": 0, **thin,
        },
        "wide_single_cell_actual_route": {
            "cell": cell, "press_speed": d1, "release_speed": d2,
            "press_tick": t, "release_tick": t + 255,
            "on": 1, "off": 0, "press_target": 1, "release_target": 0, **wide,
        },
        "sine_integral_split_candidates_checked": split_candidates,
        "callback_split_rounding_witness": split_example,
        "signed_piece_witness": {"single_fsum": small, "pre_rounded_partial_fsum": 0.0},
        "underflowing_route_product": {
            "exact_nonzero": True, "binary64_product": 0.0,
            "outward_bound_hex": subnormal.hex(),
            "exact_product_denominator_bits": exact_product.denominator.bit_length(),
        },
    },
    "resource_algebra": {
        "work_rows": work, "ring_cells": 32 * L + 2,
        "single_ring_binary64_bytes": (32 * L + 2) * 8,
        "coefficients_binary64_bytes": (32 * L + 1) * 8,
        "illustrative_two_rings_coefficients_256_outputs_bytes":
        (2 * (32 * L + 2) + (32 * L + 1) + 256) * 8,
        "illustrative_total_excludes": "grid state, exact arithmetic, pieces, edges, metadata, ABI and stack",
        "work_counts_are_offline_planning_bounds_not_callback_limits": True,
        "constructive_single_cell_burst": {
            "frames": 1, "keys": 4, "contacts_per_key": 9,
            "off": 0, "on": 1, "both_speeds": d1,
            "commands": "all keys to 1 at even ticks, 0 at odd ticks, ticks 0..127",
            "command_count": burst_commands, "edge_count": burst_edges,
            "connected_pieces": burst_pieces, "cell_index": 0,
            "all_roots_strictly_inside_cell0_positive_half": True,
            "derivation_only_no_native_or_audio_execution": True,
        },
    },
    "exact_speed_duration_examples": duration_examples,
    "A45_lineage": {
        "published_commit": BASE,
        "published_io_sha256": digest(io_published.encode()),
        "current_io_sha256": digest(io_current.encode()),
        "parser_source_segments_unchanged": list(parser_names),
        "numeric_module_byte_equal_to_published": True,
        "old_reports_not_rebound": True,
    },
    "not_run": ["audio renderer", "native grid execution", "continuous quadrature",
                "full study", "native build", "broad tests", "deadline or platform qualification"],
}
OUT.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"status": report["status"], "report": str(OUT.relative_to(ROOT)),
                  "report_sha256": digest(OUT.read_bytes()),
                  "output_positions_checked": checked_positions,
                  "thin_width_denominator_bits": thin["width"]["denominator_bits"],
                  "wide_width_numerator_bits": wide["width"]["numerator_bits"],
                  "wide_midpoint_numerator_bits": wide["midpoint"]["numerator_bits"]}, indent=2))
