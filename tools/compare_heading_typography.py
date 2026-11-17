#!/usr/bin/env python3
r"""Bounded independent T2 comparison of genuine before/after SDL RGBA streams.

The support is frozen before either executable runs: exact old/new Serif COPY
destinations plus exact old/new divider FILL destinations, intersected with the
declared output, physical viewport and enabled clip. No dilation, changed-pixel
mask, candidate painter helper, or whole heading/panel rectangle is admitted.

Example (repository root; use a new output directory):
  python3 -B tools/compare_heading_typography.py \
    --before ../baseline-native/test_standalone_footage_typography_raster \
    --after ../build-native/apps/standalone/test_standalone_footage_typography_raster \
    --build-dir ../build-native --output /tmp/heading-t2-report

Optional --before-percussion/--after-percussion add the original 66 cases.
Optional --before-clips/--after-clips add the separately pinned 48-case
typography-clips-v1 fixture. Its baseline is newly built from the same fixture
and frozen original painter, not an earlier pre-edit executable or capture.
The complete finite raster matrix requires all 158 pairs, the original 18
placement checks, and both clip-fixture assertion runs to pass without input
drift. Visual admission, integration, whole-interface 1:1 and T3 remain separate.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import platform
import re
import subprocess
import sys
import threading
import time

from PIL import Image, __version__ as PILLOW_VERSION

# Only pinned font/float/layout/protocol utilities are reused. In particular,
# legacy.declare_case(), declare_mask(), runs(), and their dilated masks are not.
import compare_footage_typography as common

MODEL = "rack-heading-independent-paired-raster-v1"
SESSION = "docs/development/2026-11-16-heading-title-continuation"
CONTRACT = "docs/design/RACK_HEADING_T2_CONTRACT.md"
ADMISSION = "docs/reviews/RACK_HEADING_T2_ADMISSION.md"
PAINTER = "apps/standalone/InstrumentView.cpp"
FONT = "apps/standalone/FontData.h"
REFERENCE = "docs/design/atlas-cover-reference.jpg"
FIXTURE = "apps/standalone/native_tests/test_standalone_footage_typography_raster.cpp"
PERCUSSION = "apps/standalone/native_tests/test_standalone_percussion_raster.cpp"
CLIPS = "apps/standalone/native_tests/test_standalone_typography_clips.cpp"
CLIP_PROTOCOL = "typography-clips-v1"
CLIP_BASELINE_METHOD = ("New identical 48-case fixture linked against frozen original pre-T2 painter "
                        "and unchanged current support libraries; not an earlier pre-edit executable")
REQUIRED_PAIRS = {"typography": 44, "percussion": 66, "clips": 48}
BASE = "113c29b7b14c8fde0859bc405ef8e4141a131ea6"
BEFORE_PAINTER_SHA = "63bede9eb5fccde155d6d6ddfbbcbfa7566ab06dcf2726d92b84bc7ad0e72a77"
PINNED = {
    CONTRACT: "e7074c5fc0f930ace34317d54bcb0c9c0741d07d4c7ef174158635c71ad2dcef",
    ADMISSION: "7ea7d167ed032d0602e8a5a432086208dc0727c38653370d294af9623ce85db4",
    FONT: "f1a3121a2707a03a3b2e025c399e68c553ce9498f4b002ec13b18f512e334802",
    REFERENCE: "9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187",
    FIXTURE: "facc85f516454964ed55e406f95db4046923d7a2441fdf72e65719b3685fec4f",
    PERCUSSION: "a96b3c43d64aee7409249141bc1bd6b0812ca3c906b46c7f41cd8030f5390dc8",
    CLIPS: "d1635b45f7ee395e172f01e50ae44d7815cc8c62e5aa2443f91a6cffdb147672",
    "apps/standalone/Drawing.cpp": "666e998cc61a9d501238783c8f2917d9be30db0bac76739f91bc23eb54f34b0a",
    "apps/standalone/UiModel.cpp": "0ecb0c4ee90d98cdb87c6f06b4685d368a7c12b72f9ea66e6c40228a4a855ecd",
    "apps/standalone/UiModel.h": "6d8c0b16ddb6f3059dc14aff41bfc615e37b43c53b2f6e88cc199255a6b674b1",
    "apps/standalone/Session.h": "dc729465578ed02a8cb0640d07de679be33d731cdece947a09bce736bc84c929",
    "src/ControlState.cpp": "9026aa0338b905a005912e4c7734eedd36cbf204ae43fa4631bdc5aadaa86a5d",
    "include/hammond/ControlState.h": "aab82b082f9cf77dadf763148cade9eae04f6f7df68b302b1832f21f78034856",
    "include/hammond/FixedRegistration.h": "4548240ce25f5200442bfe4607ba755feee822a91c8b1a97af9bf7837e3634a0",
    "tools/compare_footage_typography.py": "768ad4a5c022038c75414527961d5437bc3990a11d80772ce6fed6fc5a1534a1",
}
SDL_PINNED = {
    "include/SDL_version.h": "ee97570d0d6507b4687076336c07fd4a7fa1f5e7986c9b61893a279950febce8",
    "src/render/SDL_render.c": "ae904d0fd11c6122c77d78909538b26694b4d57a9b6b722c51e0417d4709be54",
    "src/render/software/SDL_render_sw.c": "2e3bbc7ab7d6d59310c634d6374eabb60da185d8c7cfc8526baa45318e6d3257",
}
HEADINGS = (
    {"name": "upper", "text": "UPPER MANUAL DRAWBARS", "rack": (72, 269, 528, 239),
     "center": 360, "tracking": 1.5, "outer": (140, 564), "roi": (210, 278, 300, 25),
     "reference_bounds": (223, 285, 496, 297), "reference_pixels": 726},
    {"name": "lower", "text": "LOWER MANUAL DRAWBARS", "rack": (600, 269, 516, 239),
     "center": 875.5, "tracking": 1.7, "outer": (662, 1083), "roi": (720, 278, 308, 25),
     "reference_bounds": (734, 285, 1017, 297), "reference_pixels": 734},
)
MAX_HEADER = 512 * 1024
MAX_PIXELS = 3900 * 2200
MAX_FRAME = MAX_HEADER + 1 + MAX_PIXELS * 4
MAX_STDERR = 64 * 1024
MAX_ARTIFACT_BYTES = 64 * 1024 * 1024
MAX_JSON_BYTES = 12 * 1024 * 1024
f32 = common.f32
require = common.require


def sha(data):
    return hashlib.sha256(data).hexdigest()


def identity(path):
    path = Path(path).resolve(strict=True)
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
            size += len(chunk)
    return {"path": str(path), "bytes": size, "sha256": digest.hexdigest()}


def json_bytes(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def read_json(data):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON key: " + key)
            result[key] = value
        return result
    def invalid(value):
        raise ValueError("nonfinite JSON value: " + value)
    def finite_float(value):
        number = float(value)
        require(math.isfinite(number), "nonfinite JSON number")
        return number
    return json.loads(data, object_pairs_hook=pairs, parse_constant=invalid, parse_float=finite_float)


def write_json(path, value):
    data = json_bytes(value)
    require(len(data) <= MAX_JSON_BYTES, "JSON report exceeded fixed storage bound")
    with Path(path).open("xb") as stream:
        stream.write(data)
    return {"path": Path(path).name, "bytes": len(data), "sha256": sha(data)}


def command(executable, arguments, timeout, limit):
    """Bound both pipes while reading, rather than capping after capture_output."""
    process = subprocess.Popen([str(executable), *arguments], stdin=subprocess.DEVNULL,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    outputs = [bytearray(), bytearray()]
    failures = []

    def collect(stream, index, cap):
        try:
            while True:
                chunk = stream.read(65536)
                if not chunk:
                    break
                if len(outputs[index]) + len(chunk) > cap:
                    failures.append("stdout" if index == 0 else "stderr")
                    process.kill()
                    break
                outputs[index].extend(chunk)
        except OSError as error:
            failures.append(str(error))
        finally:
            stream.close()

    threads = [threading.Thread(target=collect, args=(process.stdout, 0, limit), daemon=True),
               threading.Thread(target=collect, args=(process.stderr, 1, MAX_STDERR), daemon=True)]
    for thread in threads:
        thread.start()
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
        failures.append("timeout")
    finally:
        for thread in threads:
            thread.join(timeout=5)
    require(not any(t.is_alive() for t in threads), "fixture left an open output pipe")
    require(not failures, "bounded fixture execution failed: " + ", ".join(failures))
    require(process.returncode == 0, f"{Path(executable).name} {arguments}: exit {process.returncode}; {bytes(outputs[1][:4096])!r}")
    require(not outputs[1], f"unexpected fixture stderr: {bytes(outputs[1][:4096])!r}")
    return bytes(outputs[0])


def frame(executable, index, timeout):
    payload = command(executable, ["--case", str(index)], timeout, MAX_FRAME)
    end = payload.find(b"\n", 0, MAX_HEADER)
    require(end >= 0, "missing bounded frame JSON header")
    header = read_json(payload[:end])
    require(type(header) is dict and type(header.get("schema")) is int and header["schema"] == 1,
            "invalid frame schema")
    require(type(header.get("case")) is int and header["case"] == index, "wrong frame case")
    w, h = header.get("width"), header.get("height")
    require(type(w) is type(h) is int and 0 < w <= 3900 and 0 < h <= 2200 and w * h <= MAX_PIXELS,
            "frame dimensions exceed fixed bound")
    raw = payload[end + 1:]
    require(type(header.get("bytes")) is int and len(raw) == header["bytes"] == w * h * 4,
            "invalid raw RGBA byte count")
    return header, raw, sha(payload[:end])


def clip_cases():
    """Literal pinned 48-case source inventory; no fixture output supplies support."""
    cuts = (
        ("upper", "left", (279, 278, 301, 28)),
        ("upper", "right", (130, 278, 294, 28)),
        ("upper", "top", (130, 290, 450, 16)),
        ("upper", "bottom", (130, 278, 450, 16)),
        ("lower", "left", (799, 278, 301, 28)),
        ("lower", "right", (650, 278, 294, 28)),
        ("lower", "top", (650, 290, 450, 16)),
        ("lower", "bottom", (650, 278, 450, 16)),
        ("title", "left", (675, 14, 405, 46)),
        ("title", "right", (590, 14, 390, 46)),
        ("title", "top", (590, 31, 490, 29)),
        ("title", "bottom", (590, 14, 490, 25)),
        ("upper", "left-rule", (170, 288, 20, 7)),
        ("upper", "right-rule", (540, 288, 20, 7)),
        ("lower", "left-rule", (690, 288, 20, 7)),
        ("lower", "right-rule", (1060, 288, 20, 7)),
    )
    empty = (("upper", "empty-width", (279, 278, 0, 28)),
             ("lower", "empty-height", (799, 278, 301, 0)),
             ("title", "empty-both", (675, 14, 0, 0)))
    result = []

    def add(width=1672, height=941, scale=1, region="scene", kind="disabled",
            request=(0, 0, 0, 0), logical=False, workspace=0, presentation=0,
            canonical_origin=False):
        index = len(result)
        origin = [0, 0] if canonical_origin else ([13, 17] if index % 2 == 0 else [-11, -7])
        viewport = [*origin, math.ceil(f32(width * scale)), math.ceil(f32(height * scale))]
        output = [viewport[2] + 2 * abs(origin[0]), viewport[3] + 2 * abs(origin[1])]
        require(0 < output[0] <= 2160 and 0 < output[1] <= 1240, "clip fixture output bound")
        # SDL stores clip coordinates as binary64 products, then floor()s on
        # query/queue. Query logical clips from the original stored product,
        # not by dividing the already floored physical integer rectangle.
        stored_clip = [n * (scale if logical else 1) for n in request]
        physical_clip = [math.floor(n) for n in stored_clip]
        logical_clip = [math.floor(n / scale) for n in stored_clip]
        route, route_index = (("A", 10), ("B", 11), ("D", 2), ("Cancel", 0))[index % 4]
        bank = 0 if route == "A" else 1
        result.append({"suite": "clips", "case": index, "logical_size": [width, height],
                       "output_size": output, "scale": [scale, scale], "origin": origin,
                       "viewport": viewport, "logical_viewport": [math.floor(n / scale) for n in viewport],
                       "clip": physical_clip, "logical_clip": logical_clip,
                       "clip_enabled": kind != "disabled", "clip_space": "logical" if logical else "physical",
                       "clip_request": list(request), "clip_kind": kind, "region": region,
                       "level": (index % 3) * 4, "route": route, "route_index": route_index,
                       "edited_bank": "A" if bank == 0 else "B", "edited_bank_index": bank,
                       "pending": index % 3 == 1, "held": index % 3 != 0,
                       "focus_manual": index % 2, "focus_index": index % 9,
                       "focus": [4, index % 2, bank, index % 9], "blend": 1 if index % 2 == 0 else 0,
                       "workspace": workspace, "presentation": presentation, "resource_crop": False,
                       "active": workspace == presentation == 0 and 1400 <= width <= 8192 and 820 <= height <= 8192})

    for scale in (1, 1.25):
        for region, kind, request in cuts:
            add(scale=scale, region=region, kind=kind, request=request, logical=scale != 1)
    for scale in (1, 1.25):
        for region, kind, request in empty:
            add(scale=scale, region=region, kind=kind, request=request, logical=scale != 1)
    for scale in (1, 1.25):
        add(scale=scale, kind="disjoint", request=(1690, 955, 8, 8), logical=scale != 1)
    add(presentation=1)
    add(workspace=1)
    add(workspace=2, scale=1.25)
    add(width=960, height=700)
    add(width=1399.9998779296875, scale=1.25)  # nextafterf(1400, 0)
    add(height=819.99993896484375)             # nextafterf(820, 0)
    add(canonical_origin=True)
    add(scale=1.25)
    require(len(result) == 48, "clip inventory must remain 48")
    return result


def clip_scenario(spec):
    keys = ("case", "output_size", "scale", "origin", "region", "clip_kind", "clip_space",
            "clip_request", "level", "route", "route_index", "pending", "held", "edited_bank",
            "focus_manual", "focus_index", "blend", "clip_enabled", "workspace", "presentation", "resource_crop")
    return {**{key: spec[key] for key in keys}, "active_typography": spec["active"]}


def clip_controls(spec, desired=False):
    # ControlSnapshot defaults remember B; D and Cancel preserve that bank.
    bank = 0 if spec["route"] == "A" else 1
    result = {"drawbars": [[[spec["level"]] * 9 for _ in range(2)] for _ in range(2)],
              "selected_banks": [bank, bank], "route_enabled": [int(spec["route"] != "Cancel")] * 2,
              "fixed_registrations": [2 if spec["route"] == "D" else 0] * 2,
              "expression": .625, "pedal_drawbars": [3, 7], "percussion": [True, 0, 0, 0]}
    if desired and spec["pending"]:
        manual = spec["focus_manual"]
        result["selected_banks"][manual] = 0 if spec["route"] == "B" else 1
        result["route_enabled"][manual] = 1
        result["fixed_registrations"][manual] = 0
    return result


def clip_metadata_errors(spec, header):
    expected = {**clip_scenario(spec), "schema": 1, "protocol": CLIP_PROTOCOL,
                "width": spec["output_size"][0], "height": spec["output_size"][1],
                "bytes": spec["compared_pixels"] * 4,
                **{key: spec[key] for key in ("viewport", "clip", "logical_viewport", "logical_clip")},
                "visible_clip_pixels": common.area(spec["visible_device_box"]),
                "checks": {key: True for key in ("transform_unchanged", "model_unchanged", "session_unchanged",
                           "finite_clip", "clip_containment", "deterministic_repaint", "inactive_classification")}}
    errors = [f"{key}: expected {value!r}, observed {header.get(key)!r}" for key, value in expected.items()
              if not common.typed_equal(header.get(key), value)]
    if not common.float_vector_equal(header.get("logical_size"), spec["logical_size"]):
        errors.append("binary32 logical size differs")
    try:
        require(set(header) == set(expected) | {"logical_size", "focus", "model"}, "complete clip header fields")
        model = header["model"]
        require(set(model) == {"view", "layout"}, "complete model sections")
        view, layout = model["view"], model["layout"]
        require(set(view) == set("controls applied edited_banks focus roving_manual_keys roving_pedal_key keyboard_target "
                "manual_base_midi pedal_octave controls_pending controls_dirty text_entry_active pointer_captured "
                "input_recovery last_submit_status workspace presentation workspace_focus".split()), "complete view fields")
        require(set(layout) == set("width height show_cabinet bank_controls_in_cheeks sidebar_pedals header registration_panels "
                "performance_panel keyboard_toolbar manual_panels pedal_panel footer cabinet_panel cabinet_art manual_rail_panels "
                "control_count controls manual_keys pedal_keys preset_key_panels workspace presentation workspace_panel".split()),
                "complete layout fields")
        applied = view["applied"]
        checks = {"header focus": common.typed_equal(view["focus"], header["focus"]),
                  "edited banks": view["edited_banks"] == [spec["edited_bank_index"]] * 2,
                  "pending": view["controls_pending"] is spec["pending"],
                  "desired controls": common.typed_equal(view["controls"], clip_controls(spec, desired=True)),
                  "applied controls": common.typed_equal(applied["controls"], clip_controls(spec)),
                  "workspace": view["workspace"] == layout["workspace"] == spec["workspace"],
                  "presentation": view["presentation"] == layout["presentation"] == spec["presentation"],
                  "logical dimensions": common.float_vector_equal([layout["width"], layout["height"]], spec["logical_size"]),
                  "clock/rate/peak/revision": [applied[k] for k in ("frame_clock", "sample_rate", "peak", "publication_revision")] == [38400, 48000, .125, 4],
                  "prepared/running": applied["prepared"] is applied["running"] is True}
        held_keys, held_pedals = [[False] * 61 for _ in range(2)], [False] * 25
        held_keys[0][24] = held_keys[1][36] = held_pedals[12] = spec["held"]
        checks["held notes"] = common.typed_equal(applied["held_keys"], held_keys) and common.typed_equal(applied["held_pedals"], held_pedals)
        counters = ("resolved_sequence", "last_applied_sequence", "recovery_count", "queue_overflows",
                    "rejected_commands", "discarded_commands", "fault_flags", "last_core_status")
        checks["session counters"] = all(type(applied[k]) is int and applied[k] == 0 for k in counters)
        checks["complete session"] = set(applied) == set(counters) | {"controls", "held_keys", "held_pedals", "frame_clock",
                                      "sample_rate", "peak", "prepared", "running", "publication_revision"}
        if spec["workspace"] == 0:
            checks["declared focus"] = common.typed_equal(header["focus"], spec["focus"])
            checks["68 controls"] = layout["control_count"] == 68
            checks["147 keys"] = list(map(len, layout["manual_keys"])) == [61, 61] and len(layout["pedal_keys"]) == 25
            checks["24 presets"] = sum(c["id"][0] == 19 for c in layout["controls"]) == 24
        for control in layout["controls"]:
            require(set(control) == {"id", "bounds", "label_bounds", "value_bounds", "track"}, "complete control geometry")
        for keys in [*layout["manual_keys"], layout["pedal_keys"]]:
            for key in keys:
                require(set(key) == {"note", "bounds", "accidental", "hit", "top", "front"}, "complete key geometry")
        errors.extend("model " + name + " differs" for name, ok in checks.items() if not ok)
    except (ValueError, KeyError, IndexError, TypeError) as error:
        errors.append("missing/malformed complete clip model: " + str(error))
    return errors


def metadata_errors(spec, header):
    return clip_metadata_errors(spec, header) if spec["suite"] == "clips" else common.metadata_errors(spec, header)


def old_and_new_runs(heading, width, height, glyphs):
    sx, sy = f32(width / 1672), f32(height / 941)
    font_scale = min(sx, sy)
    rack = common.mapped(width, height, heading["rack"])
    box = [f32(rack[0] + f32(16 * sx)), f32(rack[1] + f32(8 * sy)),
           f32(rack[2] - f32(32 * sx)), f32(27 * sy)]
    x, y, w, h = box
    text = heading["text"]
    size = f32(16 * font_scale)
    old_size = min(size, f32(h / f32(1.2)))
    padding = f32(3 * sx)
    fit_width = f32(w - f32(2 * padding))
    natural = common.advance(text, old_size, glyphs)
    if natural > fit_width and natural > 0:
        old_size = f32(old_size * f32(max(f32(.1), fit_width) / natural))
    old_left = f32(x + f32(f32(w - common.advance(text, old_size, glyphs)) / 2))
    old_top = f32(y + f32(f32(h - f32(old_size * f32(1.2))) / 2))
    old = [{"text": text, "x": old_left, "top": old_top, "size": old_size}]
    middle = f32(x + f32(w / 2))
    half_gap = f32(f32(common.advance(text, size, glyphs) / 2) + f32(14 * sx))
    old_rules = []
    if half_gap < f32(f32(w / 2) - f32(16 * sx)):
        line_y = f32(y + f32(h / 2))
        old_rules = [
            [f32(x + f32(9 * sx)), line_y,
             f32(f32(f32(middle - half_gap) - x) - f32(9 * sx)), sy],
            [f32(middle + half_gap), line_y,
             f32(f32(f32(f32(x + w) - f32(9 * sx)) - middle) - half_gap), sy],
        ]
    # The literal itself is binary32 (not Python's binary64 1.7) before '*'.
    tracking = f32(f32(heading["tracking"]) * sx)
    advances = [common.advance(char, size, glyphs) for char in text]
    natural = 0.0
    for value in advances:
        natural = f32(natural + value)
    run_width = f32(natural + f32(tracking * (len(text) - 1)))
    center = f32(heading["center"] * sx)
    left = f32(center - f32(run_width / 2))
    top = f32(f32(y + f32(f32(h - f32(size * f32(1.2))) / 2)) + sy)
    cursor = left
    new = []
    for char, value in zip(text, advances, strict=True):
        new.append({"text": char, "x": cursor, "top": top, "size": size})
        cursor = f32(cursor + f32(value + tracking))
    outer_left, outer_right = [f32(value * sx) for value in heading["outer"]]
    inner_left = f32(left - f32(16 * sx))
    inner_right = f32(f32(center + f32(run_width / 2)) + f32(16 * sx))
    new_rules = [[outer_left, f32(292 * sy), f32(inner_left - outer_left), sy],
                 [inner_right, f32(292 * sy), f32(outer_right - inner_right), sy]]
    return {"name": heading["name"], "text": text, "heading_box_binary32": box,
            "new_natural_width": natural, "new_run_width": run_width, "new_left": left,
            "new_top": top, "tracking": tracking,
            "before": {"runs": old, "rules": old_rules},
            "after": {"runs": new, "rules": new_rules}}


def glyph_copies(run, glyphs):
    """Literal Drawing::text arithmetic, independent of production heading code."""
    q = f32(run["size"] / 40)
    baseline = f32(run["top"] + f32(38 * q))
    cursor = run["x"]
    result = []
    for char in run["text"]:
        ax, ay, w, h, bx, by, advance = glyphs[char]
        if w and h:
            px, py = (2 if f32(w * q) < 1 else 0), (2 if f32(h * q) < 1 else 0)
            result.append({"character": char, "atlas": [ax - px, ay - py, w + 2 * px, h + 2 * py],
                           "target_binary32": [f32(cursor + f32((bx - px) * q)),
                                               f32(baseline + f32((by - py) * q)),
                                               f32((w + 2 * px) * q), f32((h + 2 * py) * q)]})
        cursor = f32(cursor + f32(f32(advance * q) / 64))
    return result


def destination(rectangle, scale, origin, fill=False):
    if rectangle[2] <= 0 or rectangle[3] <= 0:
        return [origin[0], origin[1], origin[0], origin[1]]
    x, y, w, h = [math.trunc(f32(value * factor)) for value, factor in
                  zip(rectangle, (*scale, *scale), strict=True)]
    minimum = 1 if fill else 0
    return [x + origin[0], y + origin[1], x + origin[0] + max(w, minimum),
            y + origin[1] + max(h, minimum)]


def declare_case(case, glyphs):
    spec = dict(case)
    width, height = spec["output_size"]
    require(0 < width <= 3900 and 0 < height <= 2200 and width * height <= MAX_PIXELS,
            "declared case exceeds bounded frame domain")
    origin = spec["viewport"][:2]
    visible = common.intersect([0, 0, width, height], common.xywh(spec["viewport"]))
    if spec["clip_enabled"]:
        x, y, w, h = spec["clip"]
        visible = common.intersect(visible, [x + origin[0], y + origin[1],
                                             x + origin[0] + w, y + origin[1] + h])
    spec.update({"visible_device_box": visible, "headings": [], "labels": [],
                 "allowed_rectangles": [], "compared_pixels": width * height})
    if spec["active"]:
        for heading in HEADINGS:
            record = old_and_new_runs(heading, *spec["logical_size"], glyphs)
            for phase in ("before", "after"):
                copies = [copy for run in record[phase]["runs"] for copy in glyph_copies(run, glyphs)]
                rules = [{"target_binary32": rect} for rect in record[phase]["rules"]]
                for fill, operations in ((False, copies), (True, rules)):
                    for operation in operations:
                        device = destination(operation["target_binary32"], spec["scale"], origin, fill)
                        clipped = common.intersect(device, visible)
                        operation.update({"device_box": device, "visible_box": clipped})
                        if common.area(clipped):
                            spec["allowed_rectangles"].append(tuple(clipped))
                record[phase] = {"copies": copies, "rules": rules}
            spec["headings"].append(record)
    spec["allowed_rectangles"] = sorted(set(spec["allowed_rectangles"]))
    mask = common.allowance_mask(spec)
    spec["allowed_pixels"] = mask.histogram()[255]
    spec["protected_pixels"] = width * height - spec["allowed_pixels"]
    spec["allowance_sha256"] = sha(mask.tobytes())
    spec["whole_frame_equality_required"] = spec["allowed_pixels"] == 0
    return spec


def warm_ink(image, heading, origin=(0, 0)):
    x, y, w, h = heading["roi"]
    points = []
    crop = image.crop((x + origin[0], y + origin[1], x + origin[0] + w, y + origin[1] + h)).convert("RGB")
    for index, (r, g, b) in enumerate(crop.getdata()):
        if r >= g >= b and 2126 * r + 7152 * g + 722 * b >= 1600000:
            points.append((x + index % w, y + index // w))
    bounds = None if not points else [min(p[0] for p in points), min(p[1] for p in points),
                                      max(p[0] for p in points) + 1, max(p[1] for p in points) + 1]
    return {"bounds": bounds, "pixels": len(points)}


def placements(spec, before, after):
    if spec["suite"] != "typography" or spec["case"] >= 18:
        return {"applicable": False, "passed": True}
    records = []
    for heading in HEADINGS:
        a, b = warm_ink(before, heading, spec["viewport"][:2]), warm_ink(after, heading, spec["viewport"][:2])
        reference = list(heading["reference_bounds"])
        old_error = None if a["bounds"] is None else sum(abs(x - y) for x, y in zip(a["bounds"], reference, strict=True))
        errors = None if b["bounds"] is None else [abs(x - y) for x, y in zip(b["bounds"], reference, strict=True)]
        width_error = None if b["bounds"] is None else abs((b["bounds"][2] - b["bounds"][0]) - (reference[2] - reference[0]))
        passed = old_error is not None and errors is not None and max(errors) <= 2 and sum(errors) * 2 <= old_error and width_error <= 3
        records.append({"heading": heading["name"], "roi_xywh": heading["roi"], "reference": reference,
                        "before": a, "after": b, "before_l1_bound_error": old_error,
                        "after_bound_errors": errors, "after_width_error": width_error, "passed": passed})
    return {"applicable": True, "headings": records, "passed": all(r["passed"] for r in records)}


def check_inventory(suite, executable, cases, timeout):
    payload = command(executable, ["--list"], timeout, MAX_HEADER)
    record = read_json(payload)
    require(type(record) is dict and type(record.get("schema")) is int and record["schema"] == 1
            and type(record.get("cases")) is int and record["cases"] == len(cases), "fixture list identity differs")
    if suite in ("typography", "clips"):
        require(record.get("protocol") == (CLIP_PROTOCOL if suite == "clips" else "footage-typography-v1"),
                "wrong typography protocol")
        inventory = record.get("inventory")
        require(isinstance(inventory, list) and len(inventory) == len(cases), "missing complete typography inventory")
        for item, spec in zip(inventory, cases, strict=True):
            require(type(item) is dict, "malformed inventory item")
            if suite == "clips":
                expected = clip_scenario(spec)
                require(set(item) == set(expected) | {"logical_size"}, "complete clip inventory fields")
            else:
                expected = {key: spec[key] for key in ("case", "scale", "level", "route", "pending", "held",
                            "focus_manual", "focus_index", "clip_kind", "resource_crop", "workspace", "presentation")}
                expected.update({"origin": spec["viewport"][:2], "active_typography": spec["active"]})
            # The resource inventory reports its configured (zero) origin;
            # the frame reports the independently derived crop translation.
            if spec["resource_crop"]:
                expected["origin"] = [0, 0]
            require(all(common.typed_equal(item.get(key), value) for key, value in expected.items())
                    and common.float_vector_equal(item.get("logical_size"), spec["logical_size"]),
                    f"inventory differs at {suite} case {spec['case']}")
    return {"record": record, "sha256": sha(payload)}


def check_clip_assertions(executable, cases, timeout):
    """Default mode adds history/fresh-renderer tests absent from --case mode."""
    payload = command(executable, [], timeout, MAX_HEADER)
    record = read_json(payload)
    expected = {"schema": 1, "protocol": CLIP_PROTOCOL, "status": "passed", "cases": 48,
                "paintings": 99, "clipped_cases": 40, "empty_or_disjoint_cases": 8, "inactive_cases": 6,
                "protected_pixels": sum(c["compared_pixels"] - common.area(c["visible_device_box"]) for c in cases),
                "deterministic_repaints": 48, "history_repaints": 2,
                "backend": "SDL software surface; copied state; no audio/window"}
    require(type(record) is dict and set(record) == set(expected) | {"checks"}, "clip assertion report fields differ")
    require(all(common.typed_equal(record.get(key), value) for key, value in expected.items()),
            "clip assertion count/result differs from literal fixture")
    require(type(record["checks"]) is int and record["checks"] > 0, "clip fixture assertion count missing")
    return {"record": record, "sha256": sha(payload), "passed": True}


def clip_baseline_identity(path, binary, before_painter, source_files):
    receipt_identity = identity(path)
    require(receipt_identity["bytes"] <= MAX_HEADER, "clip baseline receipt exceeds bound")
    receipt = read_json(Path(path).read_bytes())
    require(receipt.get("schema") == 1 and receipt.get("base_commit") == BASE and
            receipt.get("status") == "built" and receipt.get("method") == CLIP_BASELINE_METHOD,
            "clip baseline must identify a new same-fixture build with the frozen painter")
    require(receipt.get("source_sha256") == {PAINTER: BEFORE_PAINTER_SHA, CLIPS: PINNED[CLIPS]},
            "clip baseline source identities differ")
    require(common.typed_equal(receipt.get("binary"), binary), "new clip baseline executable identity differs")
    retained = receipt.get("inputs")
    require(type(retained) is list and retained, "missing retained clip baseline build inputs")
    records = [*retained, receipt["object"]]
    for record in records:
        require(type(record) is dict and identity(record["path"]) == record,
                "retained clip baseline input changed")
    paths = {record["path"] for record in retained}
    require(before_painter["path"] in paths and source_files[CLIPS]["path"] in paths,
            "clip baseline build does not bind both painter and identical fixture source")
    require(type(receipt.get("commands")) is list and len(receipt["commands"]) == 2,
            "missing compile/link ancestry for newly built clip baseline")
    return {"receipt": receipt_identity, "method": CLIP_BASELINE_METHOD,
            "earlier_pre_edit_executable": False, "retained_build_inputs": records,
            "commands": receipt["commands"], "link_workdir": receipt["link_workdir"]}


def build_identities(build_dir):
    cache = build_dir / "CMakeCache.txt"
    require(cache.is_file(), "build identity requires CMakeCache.txt (supply --build-dir)")
    entries = {}
    for line in cache.read_text().splitlines():
        match = re.match(r"([^:#/][^:]*):[^=]+=(.*)$", line)
        if match:
            entries[match[1]] = match[2]
    compiler = Path(entries.get("CMAKE_CXX_COMPILER", ""))
    sdl = Path(entries.get("HAMMOND_SDL2_ROOT", ""))
    require(compiler.is_file() and sdl.is_dir(), "missing compiler/SDL build identity")
    require(all(identity(sdl / name)["sha256"] == expected for name, expected in SDL_PINNED.items()),
            "SDL software COPY/FILL/version sources differ from the admitted path")
    paths = [cache, compiler, build_dir / "_sdl2/libSDL2.a", *(sdl / name for name in SDL_PINNED)]
    for name in ("build.ninja", "compile_commands.json"):
        if (build_dir / name).is_file():
            paths.append(build_dir / name)
    return {"files": [identity(path) for path in paths],
            "configuration": {key: entries[key] for key in sorted(entries) if key in
                              ("CMAKE_BUILD_TYPE", "CMAKE_CXX_COMPILER", "CMAKE_CXX_FLAGS",
                               "CMAKE_CXX_FLAGS_RELEASE", "HAMMOND_SDL2_ROOT", "SDL_SHARED", "SDL_STATIC")}}


class FailureArtifacts:
    def __init__(self, directory, limit):
        self.directory, self.limit, self.used = directory, limit, 0

    def save(self, stem, images):
        records = []
        for name, image in images:
            buffer = io.BytesIO()
            image.save(buffer, format="PNG", optimize=False, compress_level=6)
            data = buffer.getvalue()
            if self.used + len(data) > self.limit:
                records.append({"name": name, "retained": False, "reason": "failure PNG budget exhausted"})
                continue
            filename = stem + "-" + name + ".png"
            with (self.directory / filename).open("xb") as stream:
                stream.write(data)
            self.used += len(data)
            records.append({"name": name, "retained": True, "path": filename, "bytes": len(data), "sha256": sha(data)})
        return records


def caller_clip_preserved(spec, image):
    if spec["suite"] != "clips":
        return {"applicable": False, "passed": True}
    background = (18, 21, 20, 255) if spec["presentation"] == 1 else (85, 54, 36, 255)
    width, height = spec["output_size"]
    left, top, right, bottom = spec["visible_device_box"]
    regions = ([(0, 0, width, height)] if common.area(spec["visible_device_box"]) == 0 else
               [(0, 0, width, top), (0, bottom, width, height),
                (0, top, left, bottom), (right, top, width, bottom)])
    passed = all(image.crop(box).getextrema() == tuple((value, value) for value in background)
                 for box in regions if common.area(box))
    return {"applicable": True, "outside_visible_pixels": width * height - common.area(spec["visible_device_box"]),
            "whole_target_clear_rgba": background, "passed": passed}


def compare_pair(spec, before_executable, after_executable, timeout, artifacts):
    ah, ar, ahash = frame(before_executable, spec["case"], timeout)
    bh, br, bhash = frame(after_executable, spec["case"], timeout)
    errors = ["before " + error for error in metadata_errors(spec, ah)]
    errors.extend("after " + error for error in metadata_errors(spec, bh))
    if not common.typed_equal(ah, bh):
        errors.append("complete before/after metadata/state/geometry differ")
    require([ah["width"], ah["height"]] == [bh["width"], bh["height"]] == spec["output_size"],
            "frame dimensions disagree with frozen declaration")
    before = Image.frombytes("RGBA", tuple(spec["output_size"]), ar)
    after = Image.frombytes("RGBA", tuple(spec["output_size"]), br)
    mask = common.allowance_mask(spec)
    require(sha(mask.tobytes()) == spec["allowance_sha256"], "frozen mask identity changed")
    metrics, (_, _, outside) = common.difference_metrics(before, after, mask)
    placement = placements(spec, before, after)
    clip_preservation = {"before": caller_clip_preserved(spec, before), "after": caller_clip_preserved(spec, after)}
    exact = not spec["whole_frame_equality_required"] or ar == br
    record = {"suite": spec["suite"], "case": spec["case"], "active": spec["active"],
              "metadata_errors": errors, "complete_model_available": spec["suite"] in ("typography", "clips"),
              "metadata_equal": common.typed_equal(ah, bh),
              "before_header_sha256": ahash, "after_header_sha256": bhash,
              "before_rgba_sha256": sha(ar), "after_rgba_sha256": sha(br),
              "before_model_sha256": sha(json_bytes(ah["model"])) if "model" in ah else None,
              "after_model_sha256": sha(json_bytes(bh["model"])) if "model" in bh else None,
              "allowance_sha256": spec["allowance_sha256"], "allowed_pixels": spec["allowed_pixels"],
              "protected_pixels": spec["protected_pixels"], "metrics": metrics, "placement": placement,
              "caller_clip_preservation": clip_preservation,
              "whole_frame_equality_required": spec["whole_frame_equality_required"],
              "whole_frame_equality_passed": exact,
              "passed": not errors and metrics["passed"] and exact and placement["passed"] and
                        all(item["passed"] for item in clip_preservation.values())}
    if not record["passed"]:
        record["artifacts"] = artifacts.save(f"{spec['suite']}-{spec['case']:03d}",
                                              (("before", before), ("after", after), ("outside", outside)))
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--before", required=True, type=Path, help="genuine frozen pre-T2 44-case executable")
    parser.add_argument("--after", required=True, type=Path, help="candidate 44-case executable")
    parser.add_argument("--output", required=True, type=Path, help="new directory; existing evidence is never overwritten")
    parser.add_argument("--before-percussion", type=Path)
    parser.add_argument("--after-percussion", type=Path)
    parser.add_argument("--before-clips", type=Path, help="new 48-case fixture built with frozen pre-T2 painter")
    parser.add_argument("--after-clips", type=Path, help="same 48-case fixture built with candidate painter")
    parser.add_argument("--clip-baseline-receipt", type=Path, help="separate receipt for newly built frozen-painter fixture")
    parser.add_argument("--before-painter", type=Path)
    parser.add_argument("--baseline-receipt", type=Path)
    parser.add_argument("--source-root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--build-dir", type=Path)
    parser.add_argument("--timeout", type=float, default=60)
    parser.add_argument("--failure-png-budget-mib", type=int, default=32)
    args = parser.parse_args()
    require(0 < args.timeout <= 120, "timeout must be in (0,120] seconds")
    require(0 <= args.failure_png_budget_mib <= MAX_ARTIFACT_BYTES // (1024 * 1024), "failure PNG budget must be 0..64 MiB")
    require(bool(args.before_percussion) == bool(args.after_percussion), "supply both percussion executable paths")
    require(bool(args.before_clips) == bool(args.after_clips), "supply both clip executable paths")
    require(not args.clip_baseline_receipt or args.before_clips, "clip receipt requires paired clip executable paths")
    root = args.source_root.resolve(strict=True)
    before, after = args.before.resolve(strict=True), args.after.resolve(strict=True)
    require(before != after, "before and after must be distinct files")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    report = {"schema": 1, "model": MODEL, "status": "failed", "results": [], "failures": [],
              "coverage": {"required_pairs": sum(REQUIRED_PAIRS.values()), "required_suites": REQUIRED_PAIRS,
                           "full_t2_matrix_complete": False, "inputs_unchanged": False},
              "limitations": ["Finite SDL software evidence; whole-interface 1:1 remains unclaimed.",
                              "Full matrix completion is finite raster coverage, not visual or integration admission, T3 acceptance or whole-interface 1:1.",
                              "Full model/state records are checked in 44 typography and any selected 48 clip cases; percussion exposes limited metadata.",
                              "Maximum-dimension typography cases remain resource crops, not maximum-size whole-frame containment."]}
    if not args.before_clips:
        report["limitations"].append("The 48 partial/empty/inactive clip cases and their assertion runs were not selected.")
    started = time.monotonic()
    artifacts = FailureArtifacts(output, args.failure_png_budget_mib * 1024 * 1024)
    try:
        source_files = {name: identity(root / name) for name in PINNED}
        require(all(source_files[name]["sha256"] == digest for name, digest in PINNED.items()),
                "pinned font, layout, protocol, utility, reference, or contract/admission source differs")
        source_files[PAINTER] = identity(root / PAINTER)
        source_files["tools/compare_heading_typography.py"] = identity(Path(__file__))
        before_painter = identity(args.before_painter or before.parent / "InstrumentView.cpp")
        require(before_painter["sha256"] == BEFORE_PAINTER_SHA, "not the admitted pre-T2 painter")
        receipt_path = args.baseline_receipt or root / SESSION / "reports/baseline-identity.json"
        receipt_identity = identity(receipt_path)
        require(receipt_identity["bytes"] <= MAX_HEADER, "baseline receipt exceeds bound")
        receipt = read_json(receipt_path.read_bytes())
        require(receipt.get("base_commit") == BASE and receipt.get("source_sha256", {}).get(PAINTER) == BEFORE_PAINTER_SHA,
                "baseline source receipt differs")
        suites = [("typography", before, after, common.typography_cases())]
        if args.before_percussion:
            suites.append(("percussion", args.before_percussion.resolve(strict=True),
                           args.after_percussion.resolve(strict=True), common.percussion_cases()))
        if args.before_clips:
            suites.append(("clips", args.before_clips.resolve(strict=True),
                           args.after_clips.resolve(strict=True), clip_cases()))
        binary_files = {}
        clip_provenance = None
        for suite, old, new, _ in suites:
            require(old != new, "each before/after pair must name distinct files")
            binary_files[suite] = {"before": identity(old), "after": identity(new)}
            if suite == "clips":
                clip_receipt_path = args.clip_baseline_receipt or root / SESSION / "reports/frozen-clip-baseline.json"
                clip_provenance = clip_baseline_identity(clip_receipt_path, binary_files[suite]["before"], before_painter, source_files)
                continue
            expected_name = "test_standalone_footage_typography_raster" if suite == "typography" else "test_standalone_percussion_raster"
            expected = receipt.get("files", {}).get(expected_name, {})
            require(binary_files[suite]["before"]["sha256"] == expected.get("sha256")
                    and binary_files[suite]["before"]["bytes"] == expected.get("bytes"), "genuine baseline executable receipt mismatch")
        build_dir = (args.build_dir or after.parent.parent.parent).resolve(strict=True)
        build = build_identities(build_dir)
        if args.after_clips:
            target_dir = build_dir / "apps/standalone/CMakeFiles/test_standalone_typography_clips.dir"
            build["files"].extend(identity(target_dir / name) for name in
                                  ("flags.make", "link.txt", "native_tests/test_standalone_typography_clips.cpp.o", "InstrumentView.cpp.o"))
        glyphs = common.font_metrics(root / FONT)
        reference = Image.open(root / REFERENCE).convert("RGB")
        observations = []
        for heading in HEADINGS:
            observation = warm_ink(reference, heading)
            require(observation == {"bounds": list(heading["reference_bounds"]), "pixels": heading["reference_pixels"]},
                    "reference decode/measurement differs from frozen admission")
            observations.append({"name": heading["name"], **observation})
        cases = [declare_case(case, glyphs) for _, _, _, inventory in suites for case in inventory]
        declaration = {"schema": 1, "model": MODEL, "contract_sha256": PINNED[CONTRACT], "font_sha256": PINNED[FONT],
                       "method": "Exact binary32 old/new glyph COPY and divider FILL union; no dilation; output/viewport/enabled-clip intersection.",
                       "cases": cases}
        declared = write_json(output / "mask-declaration.json", declaration)
        report["inputs"] = {"sources": source_files, "before_painter": before_painter,
                            "baseline_receipt": receipt_identity, "binaries": binary_files,
                            "clip_baseline": clip_provenance,
                            "build": build, "python": platform.python_version(), "platform": platform.platform(),
                            "pillow": PILLOW_VERSION, "reference_observations": observations,
                            "mask_declaration": declared}
        write_json(output / "input-identities.json", report["inputs"])
        # The support and input receipt above exist before the first native call.
        inventories = {}
        for suite, old, new, inventory in suites:
            inventories[suite] = {"before": check_inventory(suite, old, inventory, args.timeout),
                                  "after": check_inventory(suite, new, inventory, args.timeout)}
            require(common.typed_equal(inventories[suite]["before"]["record"], inventories[suite]["after"]["record"]),
                    "before/after inventory mismatch")
        write_json(output / "fixture-inventories.json", inventories)
        clip_tests = {}
        if args.before_clips:
            clip_specs = [case for case in cases if case["suite"] == "clips"]
            clip_pair = next((old, new) for suite, old, new, _ in suites if suite == "clips")
            clip_tests = {phase: check_clip_assertions(executable, clip_specs, args.timeout)
                          for phase, executable in zip(("before", "after"), clip_pair, strict=True)}
            write_json(output / "clip-fixture-assertions.json", clip_tests)
        report["clip_fixture_assertions"] = clip_tests
        pairs = {suite: (old, new) for suite, old, new, _ in suites}
        for spec in cases:
            try:
                result = compare_pair(spec, *pairs[spec["suite"]], args.timeout, artifacts)
            except (ValueError, OSError, KeyError, TypeError, IndexError) as error:
                result = {"suite": spec["suite"], "case": spec["case"], "passed": False, "error": str(error)}
            report["results"].append(result)
            print(f"{spec['suite']} {spec['case']:02d}: {'passed' if result['passed'] else 'FAILED'}", flush=True)
        watched = [*source_files.values(), before_painter, receipt_identity, *build["files"],
                   *(value for pair in binary_files.values() for value in pair.values())]
        if clip_provenance:
            watched.extend([clip_provenance["receipt"], *clip_provenance["retained_build_inputs"]])
        report["coverage"].update({"declared_pairs": len(cases), "attempted_pairs": len(report["results"]),
                                  "completed_pairs": sum("metrics" in item for item in report["results"]),
                                  "complete_model_pairs": sum(item.get("complete_model_available", False) for item in report["results"]),
                                  "typography_complete_model_pairs": sum(item["suite"] == "typography" and item.get("complete_model_available", False) for item in report["results"]),
                                  "percussion_pairs": 66 if args.before_percussion else 0,
                                  "clip_complete_model_pairs": sum(item["suite"] == "clips" and item.get("complete_model_available", False) for item in report["results"]),
                                  "canonical_placement_pairs": sum(item.get("placement", {}).get("applicable", False) for item in report["results"]),
                                  "inactive_pairs": sum(not case["active"] for case in cases),
                                  "whole_frame_exact_pairs": sum(case["whole_frame_equality_required"] for case in cases),
                                  "partial_heading_clip_cases": 24 if args.before_clips else 0,
                                  "partial_heading_glyph_clip_cases": 16 if args.before_clips else 0,
                                  "partial_heading_rule_clip_cases": 8 if args.before_clips else 0,
                                  "title_preservation_clip_cases": 8 if args.before_clips else 0,
                                  "empty_or_disjoint_clip_cases": 8 if args.before_clips else 0,
                                  "clip_assertion_runs_passed": sum(item["passed"] for item in clip_tests.values()),
                                  "compact_960x700_covered": bool(args.before_percussion or args.before_clips)})
        drift = [item["path"] for item in watched if identity(item["path"]) != item]
        require(not drift, "inputs changed during comparison: " + ", ".join(drift))
        report["status"] = "passed" if all(item["passed"] for item in report["results"]) else "failed"
        expected_pairs = {(suite, index) for suite, count in REQUIRED_PAIRS.items() for index in range(count)}
        observed_pairs = {(item["suite"], item["case"]) for item in report["results"]}
        report["coverage"]["inputs_unchanged"] = True
        report["coverage"]["full_t2_matrix_complete"] = (
            report["status"] == "passed" and len(report["results"]) == len(expected_pairs) == 158 and
            observed_pairs == expected_pairs and report["coverage"]["completed_pairs"] == 158 and
            report["coverage"]["canonical_placement_pairs"] == 18 and
            report["coverage"]["complete_model_pairs"] == 92 and
            report["coverage"]["clip_assertion_runs_passed"] == 2)
    except (ValueError, OSError, KeyError, TypeError, IndexError) as error:
        report["failures"].append(str(error))
    report["elapsed_seconds"] = round(time.monotonic() - started, 3)
    report["failure_png_bytes"] = artifacts.used
    report["storage_bounds"] = {"failure_png_budget_bytes": artifacts.limit,
                                "per_json_max_bytes": MAX_JSON_BYTES, "raw_frames_retained": 0,
                                "per_process_stdout_max_bytes": MAX_FRAME, "per_process_stderr_max_bytes": MAX_STDERR}
    write_json(output / "report.json", report)
    print(json.dumps({"status": report["status"], "pairs": len(report["results"]),
                      "failures": report["failures"], "report": str(output / "report.json")}), flush=True)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError) as error:
        print("heading comparison: " + str(error), file=sys.stderr)
        sys.exit(1)
