#!/usr/bin/env python3
"""Persistent T3 density gate against an already-built native raster fixture.

Run with --executable PATH_TO_test_standalone_footage_typography_raster.
Only the 18 frozen canonical states are requested, one process/frame at a time.
The fixture independently asserts complete model/session and renderer-state
preservation before emitting its JSON header and RGBA bytes. This reader checks
that protocol and the declared copied states, then applies the original T3
encoded-Y' predicate without Pillow, image files, resampling or a hue filter.

The constants come from TITLE_T3_CONTRACT.md and the pinned fixture source;
neither production pixels nor reported dimensions define expected density.
This supplements the unchanged native geometry and paired-support gates.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import threading


FIXTURE_SHA256 = "facc85f516454964ed55e406f95db4046923d7a2441fdf72e65719b3685fec4f"
PROTOCOL = "footage-typography-v1"
CASE_COUNT = 18
LOGICAL_SIZE = [1672, 941]
ORIGIN = [13, 17]
OUTPUT_SIZE = [1698, 975]
VIEWPORT = [13, 17, 1672, 941]
ROI = [590, 14, 490, 46]
THRESHOLDS = (80, 100, 120, 140, 160)
REFERENCE_COUNTS = (5639, 5415, 4991, 4502, 3785)
BASELINE_COUNTS = (4150, 3863, 3601, 3200, 2690)
PRIMARY_BAND = (4500, 6000)
FRAME_BYTES = OUTPUT_SIZE[0] * OUTPUT_SIZE[1] * 4
MAX_HEADER_BYTES = 512 * 1024
MAX_STDOUT_BYTES = MAX_HEADER_BYTES + 1 + FRAME_BYTES
MAX_STDERR_BYTES = 64 * 1024
READ_BYTES = 64 * 1024
PROCESS_TIMEOUT_SECONDS = 20
CLEANUP_TIMEOUT_SECONDS = 5
MAX_ERROR_CHARACTERS = 4096


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(READ_BYTES), b""):
            digest.update(chunk)
    return digest.hexdigest()


def typed_equal(actual, expected):
    if type(actual) is not type(expected):
        return False
    if isinstance(expected, dict):
        return actual.keys() == expected.keys() and all(
            typed_equal(actual[key], value) for key, value in expected.items())
    if isinstance(expected, list):
        return len(actual) == len(expected) and all(
            typed_equal(left, right) for left, right in zip(actual, expected))
    return actual == expected


def unique_members(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON member")
        result[key] = value
    return result


def invalid_constant(value):
    raise ValueError("non-JSON numeric token: " + value)


def capture_frame(executable, index):
    """Bound both pipe buffers during capture, including unsuccessful children."""
    process = subprocess.Popen(
        [str(executable), "--case", str(index)], stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    outputs = [bytearray(), bytearray()]
    failures = []

    def kill():
        try:
            process.kill()
        except OSError:
            pass  # The other reader or the process may already have ended it.

    def collect(stream, channel, cap):
        try:
            while True:
                chunk = stream.read(READ_BYTES)
                if not chunk:
                    break
                if len(outputs[channel]) + len(chunk) > cap:
                    failures.append(("stdout" if channel == 0 else "stderr") + " exceeded byte bound")
                    kill()
                    break
                outputs[channel].extend(chunk)
        except OSError as error:
            failures.append(str(error)[:MAX_ERROR_CHARACTERS])
            kill()
        finally:
            stream.close()

    readers = [
        threading.Thread(target=collect, args=(process.stdout, 0, MAX_STDOUT_BYTES), daemon=True),
        threading.Thread(target=collect, args=(process.stderr, 1, MAX_STDERR_BYTES), daemon=True),
    ]
    for reader in readers:
        reader.start()
    try:
        process.wait(timeout=PROCESS_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        failures.append("native fixture exceeded 20-second timeout")
        kill()
        try:
            process.wait(timeout=CLEANUP_TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired:
            failures.append("native fixture did not exit within bounded cleanup")
    finally:
        for reader in readers:
            reader.join(timeout=CLEANUP_TIMEOUT_SECONDS)
    require(not any(reader.is_alive() for reader in readers), "native fixture left an open pipe")
    require(not failures, "; ".join(failures)[:MAX_ERROR_CHARACTERS])
    diagnostic = outputs[1][:MAX_ERROR_CHARACTERS].decode("utf-8", errors="replace")
    require(process.returncode == 0, f"native fixture case {index} exited {process.returncode}: {diagnostic}")
    require(not outputs[1], "unexpected native fixture stderr: " + diagnostic)
    # Return the sole retained frame buffer, without an additional whole-frame copy.
    return outputs[0]


def expected_header(index):
    manual, drawbar = divmod(index, 9)
    bank = drawbar % 2
    return {
        "schema": 1, "protocol": PROTOCOL, "case": index,
        "logical_size": LOGICAL_SIZE, "width": OUTPUT_SIZE[0], "height": OUTPUT_SIZE[1],
        "output_size": OUTPUT_SIZE, "scale": [1, 1], "viewport": VIEWPORT,
        "clip": [0, 0, 0, 0], "logical_viewport": VIEWPORT, "logical_clip": [0, 0, 0, 0],
        "clip_enabled": False, "blend": 1, "clip_kind": "disabled",
        "level": (drawbar % 3) * 4, "route": "B" if bank else "A", "route_index": 10 + bank,
        "pending": drawbar % 3 == 1, "held": drawbar % 3 != 0, "edited_bank": "B" if bank else "A",
        "focus": [4, manual, bank, drawbar], "resource_crop": False, "active_typography": True,
        "workspace": 0, "presentation": 0, "bytes": FRAME_BYTES,
    }


def expected_controls(spec, desired):
    bank = spec["route_index"] - 10
    selected = [bank, bank]
    if desired and spec["pending"]:
        selected[spec["focus"][1]] = 1 - bank
    return {
        "drawbars": [[[spec["level"]] * 9 for _ in range(2)] for _ in range(2)],
        "selected_banks": selected, "route_enabled": [1, 1], "expression": .625,
        "percussion": [True, 0, 0, 0], "pedal_drawbars": [3, 7], "fixed_registrations": [0, 0],
    }


def validate_model(model, spec):
    require(type(model) is dict and set(model) == {"view", "layout"}, "complete native model sections required")
    view, layout = model["view"], model["layout"]
    require(type(view) is dict and set(view) == set(
        "controls applied edited_banks focus roving_manual_keys roving_pedal_key keyboard_target manual_base_midi "
        "pedal_octave controls_pending controls_dirty text_entry_active pointer_captured input_recovery "
        "last_submit_status workspace presentation workspace_focus".split()), "complete copied view fields required")
    require(type(layout) is dict and set(layout) == set(
        "width height show_cabinet bank_controls_in_cheeks sidebar_pedals header registration_panels performance_panel "
        "keyboard_toolbar manual_panels pedal_panel footer cabinet_panel cabinet_art manual_rail_panels control_count "
        "controls manual_keys pedal_keys preset_key_panels workspace presentation workspace_panel".split()),
        "complete copied layout fields required")
    for key, expected in {
        "controls": expected_controls(spec, True), "focus": spec["focus"],
        "edited_banks": [spec["route_index"] - 10] * 2, "controls_pending": spec["pending"],
        "workspace": 0, "presentation": 0,
    }.items():
        require(typed_equal(view[key], expected), "copied view " + key + " differs")
    held_keys, held_pedals = [[False] * 61 for _ in range(2)], [False] * 25
    held_keys[0][24] = held_keys[1][36] = held_pedals[12] = spec["held"]
    session = {
        "controls": expected_controls(spec, False), "held_keys": held_keys, "held_pedals": held_pedals,
        "frame_clock": 38400, "sample_rate": 48000, "peak": .125, "prepared": True, "running": True,
        "publication_revision": 4,
    }
    session.update(dict.fromkeys(("resolved_sequence", "last_applied_sequence", "recovery_count", "queue_overflows",
                                  "rejected_commands", "discarded_commands", "fault_flags", "last_core_status"), 0))
    require(typed_equal(view["applied"], session), "complete applied session differs")
    for key, expected in {"width": 1672, "height": 941, "workspace": 0, "presentation": 0, "control_count": 68}.items():
        require(typed_equal(layout[key], expected), "copied layout " + key + " differs")
    controls = layout["controls"]
    require(type(controls) is list and len(controls) == 68, "all 68 control geometries required")
    for control in controls:
        require(type(control) is dict and set(control) == {"id", "bounds", "label_bounds", "value_bounds", "track"},
                "complete control geometry required")
        require(type(control["id"]) is list and len(control["id"]) == 4 and
                all(type(value) is int for value in control["id"]), "invalid control identity")
    require(len({tuple(control["id"]) for control in controls}) == 68, "duplicate control identity")
    require(sum(control["id"][0] == 19 for control in controls) == 24, "all 24 preset controls required")
    manuals, pedals = layout["manual_keys"], layout["pedal_keys"]
    require(type(manuals) is list and len(manuals) == 2 and
            all(type(keys) is list and len(keys) == 61 for keys in manuals) and
            type(pedals) is list and len(pedals) == 25, "all 147 playing-key geometries required")
    for keys in [*manuals, pedals]:
        for key in keys:
            require(type(key) is dict and set(key) == {"note", "bounds", "accidental", "hit", "top", "front"},
                    "complete playing-key geometry required")


def parse_frame(payload, index):
    end = payload.find(b"\n", 0, MAX_HEADER_BYTES + 1)
    require(0 < end <= MAX_HEADER_BYTES, "missing bounded JSON frame header")
    header = json.loads(payload[:end].decode("utf-8"), object_pairs_hook=unique_members,
                        parse_constant=invalid_constant)
    expected = expected_header(index)
    require(type(header) is dict and set(header) == set(expected) | {"model"}, "complete native protocol fields required")
    for key, value in expected.items():
        require(typed_equal(header[key], value), "native protocol " + key + " differs from frozen fixture")
    validate_model(header["model"], expected)
    require(len(payload) - end - 1 == FRAME_BYTES, "raw RGBA length differs from fixed canonical frame")
    return memoryview(payload)[end + 1:]


def density(raw):
    """Count RGB only, using exact integer Y' and a fixed translated ROI."""
    require(len(raw) == FRAME_BYTES, "density requires the complete fixed RGBA frame")
    x, y, width, height = ROI
    counts = [0] * len(THRESHOLDS)
    bounds = [[x + width, y + height, x, y] for _ in THRESHOLDS]
    for row in range(height):
        start = ((y + ORIGIN[1] + row) * OUTPUT_SIZE[0] + x + ORIGIN[0]) * 4
        for column in range(width):
            at = start + column * 4
            weighted = 2126 * raw[at] + 7152 * raw[at + 1] + 722 * raw[at + 2]
            for index, threshold in enumerate(THRESHOLDS):
                if weighted < threshold * 10000:
                    break
                counts[index] += 1
                box = bounds[index]
                box[0], box[1] = min(box[0], x + column), min(box[1], y + row)
                box[2], box[3] = max(box[2], x + column + 1), max(box[3], y + row + 1)
    primary = counts[1]
    original_error = abs(REFERENCE_COUNTS[1] - BASELINE_COUNTS[1])
    candidate_error = abs(REFERENCE_COUNTS[1] - primary)
    band = PRIMARY_BAND[0] <= primary <= PRIMARY_BAND[1]
    improvement = 5 * candidate_error <= 3 * original_error
    return {
        "thresholds": [{"threshold": threshold, "pixels": count, "bounds": box if count else None}
                       for threshold, count, box in zip(THRESHOLDS, counts, bounds)],
        "primary_band_passed": band, "original_absolute_count_error": original_error,
        "candidate_absolute_count_error": candidate_error,
        "error_reduction_fraction": (original_error - candidate_error) / original_error,
        "error_reduction_passed": improvement, "passed": band and improvement,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path, required=True, help="already-built native footage raster fixture")
    args = parser.parse_args()
    report = {
        "schema": 1, "test": "standalone-title-density-v1", "status": "failed", "required_cases": CASE_COUNT,
        "native_protocol": PROTOCOL, "fixture_source_sha256": FIXTURE_SHA256,
        "logical_size": LOGICAL_SIZE, "output_size": OUTPUT_SIZE, "viewport_origin": ORIGIN, "roi_xywh": ROI,
        "bounds_coordinates": "canonical half-open bounds, with integer viewport origin subtracted",
        "predicate": "2126*R+7152*G+722*B >= threshold*10000; no hue or alpha predicate",
        "reference_counts": list(REFERENCE_COUNTS), "pre_T3_baseline_counts": list(BASELINE_COUNTS),
        "primary_band": list(PRIMARY_BAND), "minimum_error_reduction": .4,
        "resources": {"one_frame_at_a_time": True, "process_timeout_seconds": PROCESS_TIMEOUT_SECONDS,
                      "stdout_max_bytes": MAX_STDOUT_BYTES, "stderr_max_bytes": MAX_STDERR_BYTES,
                      "images_persisted": 0}, "cases": [],
    }
    try:
        fixture = Path(__file__).with_name("test_standalone_footage_typography_raster.cpp")
        require(sha256_file(fixture) == FIXTURE_SHA256, "native fixture source no longer matches the frozen protocol")
        executable = args.executable.resolve(strict=True)
        require(executable.is_file() and os.access(executable, os.X_OK), "native fixture is not executable")
        report["executable_sha256"] = sha256_file(executable)
        for index in range(CASE_COUNT):
            payload = capture_frame(executable, index)
            raw = parse_frame(payload, index)
            report["cases"].append({"case": index, **density(raw)})
            del raw, payload
        require(sha256_file(executable) == report["executable_sha256"], "native executable changed during the test")
        require(sha256_file(fixture) == FIXTURE_SHA256, "fixture source changed during the test")
        if all(case["passed"] for case in report["cases"]):
            report["status"] = "passed"
    except (OSError, ValueError, KeyError, TypeError, IndexError, RecursionError) as error:
        report["error"] = str(error)[:MAX_ERROR_CHARACTERS]
    print(json.dumps(report, indent=2, allow_nan=False), flush=True)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
