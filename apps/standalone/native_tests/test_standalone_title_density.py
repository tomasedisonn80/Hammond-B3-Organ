#!/usr/bin/env python3
"""Persistent T3 density gate against an already-built native raster fixture.

Run with --executable PATH_TO_test_standalone_footage_typography_raster.
The exact 44-case native inventory is checked before requesting the 18 frozen
canonical states, one process/frame at a time. The other 26 cases remain the
responsibility of the separate paired-support and geometry gates; the canonical
density band does not apply to resized, clipped or inactive frames.
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
import math
import os
from pathlib import Path
import subprocess
import sys
import threading


FIXTURE_SHA256 = "9e3a8fb643194e8ce4dcefb8059e82fef2b0140183c9175449098bf8941a2ecb"
PROTOCOL = "footage-typography-v1"
CASE_COUNT = 18
FIXTURE_CASE_COUNT = 44
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
MAX_INVENTORY_BYTES = 64 * 1024
MAX_STDOUT_BYTES = MAX_HEADER_BYTES + 1 + FRAME_BYTES
MAX_STDERR_BYTES = 64 * 1024
READ_BYTES = 64 * 1024
PROCESS_TIMEOUT_SECONDS = 20
CLEANUP_TIMEOUT_SECONDS = 5
MAX_ERROR_CHARACTERS = 4096
MAX_JSON_DEPTH = 16
MAX_NUMBER_CHARACTERS = 64


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


def bounded_integer(value):
    require(len(value) <= MAX_NUMBER_CHARACTERS, "JSON integer token exceeded bound")
    return int(value)


def finite_float(value):
    require(len(value) <= MAX_NUMBER_CHARACTERS, "JSON float token exceeded bound")
    result = float(value)
    require(math.isfinite(result), "nonfinite JSON number")
    return result


def bounded_json(payload, maximum):
    require(0 < len(payload) <= maximum, "JSON payload exceeded byte bound")
    value = payload.decode("utf-8")
    # Reject excessive nesting before json.loads creates a recursive object tree.
    # Brackets and escaped quotes inside strings do not contribute to depth.
    depth, quoted, escaped = 0, False, False
    for character in value:
        if quoted:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                quoted = False
        elif character == '"':
            quoted = True
        elif character in "[{":
            depth += 1
            require(depth <= MAX_JSON_DEPTH, "JSON nesting exceeded bound")
        elif character in "]}":
            depth -= 1
    return json.loads(value, object_pairs_hook=unique_members,
                      parse_constant=invalid_constant, parse_int=bounded_integer,
                      parse_float=finite_float)


def capture_command(executable, arguments, stdout_maximum):
    """Bound both pipe buffers during capture, including unsuccessful children."""
    process = subprocess.Popen(
        [str(executable), *arguments], stdin=subprocess.DEVNULL,
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
        threading.Thread(target=collect, args=(process.stdout, 0, stdout_maximum), daemon=True),
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
    require(process.returncode == 0, f"native fixture {' '.join(arguments)} exited {process.returncode}: {diagnostic}")
    require(not outputs[1], "unexpected native fixture stderr: " + diagnostic)
    # Return the sole retained frame buffer, without an additional whole-frame copy.
    return outputs[0]


def capture_frame(executable, index):
    require(type(index) is int and 0 <= index < CASE_COUNT, "canonical case index required")
    return capture_command(executable, ["--case", str(index)], MAX_STDOUT_BYTES)


def expected_inventory():
    """Declare all native --list rows from the pinned C++ cases(), not its output."""
    rows = []

    def add(**changes):
        row = {
            "case": len(rows), "logical_size": [1672, 941], "scale": [1, 1],
            "origin": [13, 17], "level": 4, "route": "B", "pending": False, "held": True,
            "focus_manual": 0, "focus_index": 1, "clip_kind": "disabled", "resource_crop": False,
            "workspace": 0, "presentation": 0, "active_typography": True,
        }
        row.update(changes)
        rows.append(row)

    for manual in range(2):
        for drawbar in range(9):
            add(level=(drawbar % 3) * 4, route="B" if drawbar % 2 else "A",
                pending=drawbar % 3 == 1, held=drawbar % 3 != 0,
                focus_manual=manual, focus_index=drawbar)
    for size, scale, origin in (
        ([1400, 820], [1, 1], [13, 17]),
        ([1920, 1080], [1, 1], [13, 17]),
        ([1920, 820], [1, 1], [13, 17]),
        ([1400, 1080], [1, 1], [13, 17]),
        ([1672.5, 941.25], [1.25, 1.25], [13, 17]),
        ([1672, 941], [.75, .75], [-11, -7]),
        ([1672, 941], [1.25, 1.25], [29, 31]),
        ([1672, 941], [1.5, 2], [13, 17]),
    ):
        add(logical_size=size, scale=scale, origin=origin)
    for logical in (False, True):
        for edge in ("left", "right", "top", "bottom"):
            add(scale=[1.25, 1.25] if logical else [1, 1],
                clip_kind=("logical" if logical else "physical") + "-glyph-" + edge)
    add(clip_kind="physical-disjoint")
    add(clip_kind="physical-empty")
    add(clip_kind="logical-empty", scale=[1.25, 1.25])
    add(presentation=1, active_typography=False)
    add(workspace=1, active_typography=False)
    add(workspace=2, active_typography=False)
    # These are nextafter(binary32(1400/820), 0) serialized with max_digits10=9,
    # exactly as the frozen native protocol emits them; no tolerance is used.
    add(logical_size=[1399.99988, 941], active_typography=False)
    add(logical_size=[1672, 819.999939], active_typography=False)
    add(logical_size=[8192, 8192], origin=[0, 0], resource_crop=True)
    add(logical_size=[8192, 8192], scale=[1.5, 2], origin=[0, 0], resource_crop=True)
    require(len(rows) == FIXTURE_CASE_COUNT, "incorrect declared native inventory")
    return {"schema": 1, "protocol": PROTOCOL, "cases": FIXTURE_CASE_COUNT, "inventory": rows}


def parse_inventory(payload):
    inventory = bounded_json(payload, MAX_INVENTORY_BYTES)
    require(typed_equal(inventory, expected_inventory()), "native 44-case inventory differs from frozen fixture")
    return {"case_count": FIXTURE_CASE_COUNT, "validated": True,
            "payload_sha256": hashlib.sha256(payload).hexdigest()}


def expected_header(index):
    require(type(index) is int and 0 <= index < CASE_COUNT, "canonical case index required")
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


def number_vector(value, length, name):
    require(type(value) is list and len(value) == length and
            all(type(item) in (int, float) and math.isfinite(item) for item in value),
            "invalid finite numeric vector: " + name)


def integer_vector(value, length, lower, upper, name):
    require(type(value) is list and len(value) == length and
            all(type(item) is int and lower <= item <= upper for item in value),
            "invalid integer vector: " + name)


def control_identity(value):
    integer_vector(value, 4, 0, 255, "control identity")
    require(value[0] <= 21 and value[1] <= 1 and value[2] <= 1, "invalid control identity fields")


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
    integer_vector(view["roving_manual_keys"], 2, 0, 60, "roving manual keys")
    for key, lower, upper in (("roving_pedal_key", 0, 24), ("keyboard_target", 0, 2),
                              ("manual_base_midi", 36, 84), ("pedal_octave", 0, 2),
                              ("last_submit_status", 0, 255)):
        require(type(view[key]) is int and lower <= view[key] <= upper, "invalid copied view " + key)
    require(view["manual_base_midi"] % 12 == 0, "invalid copied manual base MIDI")
    for key in ("controls_dirty", "text_entry_active", "pointer_captured", "input_recovery"):
        require(type(view[key]) is bool, "invalid copied view flag " + key)
    require(type(view["workspace_focus"]) is list and len(view["workspace_focus"]) == 3,
            "all workspace focus identities required")
    for identity in view["workspace_focus"]:
        control_identity(identity)
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
    for key in ("show_cabinet", "bank_controls_in_cheeks", "sidebar_pedals"):
        require(type(layout[key]) is bool, "invalid copied layout flag " + key)
    for key in ("header", "performance_panel", "keyboard_toolbar", "pedal_panel", "footer",
                "cabinet_panel", "cabinet_art", "workspace_panel"):
        number_vector(layout[key], 4, key)
    for key in ("registration_panels", "manual_panels", "manual_rail_panels", "preset_key_panels"):
        require(type(layout[key]) is list and len(layout[key]) == 2, "both copied layout panels required: " + key)
        for rectangle in layout[key]:
            number_vector(rectangle, 4, key)
    controls = layout["controls"]
    require(type(controls) is list and len(controls) == 68, "all 68 control geometries required")
    for control in controls:
        require(type(control) is dict and set(control) == {"id", "bounds", "label_bounds", "value_bounds", "track"},
                "complete control geometry required")
        control_identity(control["id"])
        for name in ("bounds", "label_bounds", "value_bounds", "track"):
            number_vector(control[name], 4, "control " + name)
    require(len({tuple(control["id"]) for control in controls}) == 68, "duplicate control identity")
    require(sum(control["id"][0] == 19 for control in controls) == 24, "all 24 preset controls required")
    require({tuple(control["id"]) for control in controls if control["id"][0] == 19} ==
            {(19, manual, 0, index) for manual in range(2) for index in range(12)},
            "complete preset identities required")
    require({tuple(control["id"]) for control in controls if control["id"][0] == 4} ==
            {(4, manual, spec["route_index"] - 10, index) for manual in range(2) for index in range(9)},
            "complete visible drawbar identities required")
    manuals, pedals = layout["manual_keys"], layout["pedal_keys"]
    require(type(manuals) is list and len(manuals) == 2 and
            all(type(keys) is list and len(keys) == 61 for keys in manuals) and
            type(pedals) is list and len(pedals) == 25, "all 147 playing-key geometries required")
    for target, keys in enumerate([*manuals, pedals]):
        for index, key in enumerate(keys):
            require(type(key) is dict and set(key) == {"note", "bounds", "accidental", "hit", "top", "front"},
                    "complete playing-key geometry required")
            require(typed_equal(key["note"], [target, index + (1 if target == 2 else 36)]),
                    "playing-key note identity differs")
            require(type(key["accidental"]) is bool, "invalid playing-key accidental flag")
            number_vector(key["bounds"], 4, "playing-key bounds")
            for name in ("hit", "top", "front"):
                require(type(key[name]) is list and len(key[name]) == 4, "four playing-key vertices required")
                for point in key[name]:
                    number_vector(point, 2, "playing-key " + name)


def parse_frame(payload, index):
    require(len(payload) <= MAX_STDOUT_BYTES, "native frame exceeded byte bound")
    end = payload.find(b"\n", 0, MAX_HEADER_BYTES + 1)
    require(0 < end <= MAX_HEADER_BYTES, "missing bounded JSON frame header")
    header = bounded_json(payload[:end], MAX_HEADER_BYTES)
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
        "native_protocol": PROTOCOL, "native_fixture_cases": FIXTURE_CASE_COUNT, "fixture_source_sha256": FIXTURE_SHA256,
        "logical_size": LOGICAL_SIZE, "output_size": OUTPUT_SIZE, "viewport_origin": ORIGIN, "roi_xywh": ROI,
        "bounds_coordinates": "canonical half-open bounds, with integer viewport origin subtracted",
        "predicate": "2126*R+7152*G+722*B >= threshold*10000; no hue or alpha predicate",
        "reference_counts": list(REFERENCE_COUNTS), "pre_T3_baseline_counts": list(BASELINE_COUNTS),
        "primary_band": list(PRIMARY_BAND), "minimum_error_reduction": .4,
        "resources": {"one_frame_at_a_time": True, "process_timeout_seconds": PROCESS_TIMEOUT_SECONDS,
                      "stdout_max_bytes": MAX_STDOUT_BYTES, "stderr_max_bytes": MAX_STDERR_BYTES,
                      "inventory_max_bytes": MAX_INVENTORY_BYTES, "json_max_depth": MAX_JSON_DEPTH,
                      "number_token_max_characters": MAX_NUMBER_CHARACTERS,
                      "images_persisted": 0}, "cases": [],
    }
    try:
        fixture = Path(__file__).with_name("test_standalone_footage_typography_raster.cpp")
        require(sha256_file(fixture) == FIXTURE_SHA256, "native fixture source no longer matches the frozen protocol")
        executable = args.executable.resolve(strict=True)
        require(executable.is_file() and os.access(executable, os.X_OK), "native fixture is not executable")
        report["executable_sha256"] = sha256_file(executable)
        report["inventory"] = parse_inventory(capture_command(executable, ["--list"], MAX_INVENTORY_BYTES))
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
