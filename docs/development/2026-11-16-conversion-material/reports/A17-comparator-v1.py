#!/usr/bin/env python3
"""Independently compare the frozen 66+32 Lower-rack material fixture pairs.

No compilation, source mutation, reconstructed baseline, candidate allowance, or
earlier broad composition mask is used. A fresh output directory receives the
source-derived mask BEFORE the first paired pixel stream, then a complete report.
Any failed pixel/child/metric comparison retains lossless absolute RGBA channel
differences and before/after PNGs. Existing reports are never overwritten.

Example (from the repository):
  python3 -B tools/compare_lower_rack_material.py \
    --before-percussion ../baseline/test_standalone_percussion_raster \
    --after-percussion ../build-native/apps/standalone/test_standalone_percussion_raster \
    --before-lower ../baseline/test_standalone_lower_rack_material_raster \
    --after-lower ../build-native/apps/standalone/test_standalone_lower_rack_material_raster \
    --before-painter ../baseline/InstrumentView.cpp \
    --output-dir /path/to/new-report-directory

Only the named software containment, exact preservation and 35 local image
statistics are graded. Whole-interface 1:1, native display/accessibility, full
surface visual admission and physical fidelity remain separate, open gates.
"""
from __future__ import annotations

import argparse
import datetime as dt
from fractions import Fraction
import hashlib
import io
import json
import math
import os
from pathlib import Path
import platform
import struct
import subprocess
import sys
import time

from PIL import Image, ImageChops, __version__ as PILLOW_VERSION, features


MODEL = "lower-rack-independent-paired-raster-v1"
PROTOCOL = "lower-rack-material-v1"
BASE = "a411268fd498f65c083203137831bf5afed83bd8"
SESSION = "docs/development/2026-11-16-conversion-material"
CONTRACT = "docs/design/LOWER_RACK_MATERIAL_CONTRACT.md"
CONTRACT_SHA = "84e3c95b4844861ffee71217ced99dbdb52bfb3216b44f4d2817c462cadccb91"
BEFORE_PAINTER_SHA = "30ac6cec988ec1834f36456d25d1e53113642071d844d53f81b62b3474cf2c37"
BEFORE_PERCUSSION_SHA = "622fe1c17828cc3a540d18479c85e331852ba68fff739e8a6317ead02dad4ffc"
PERCUSSION_SOURCE = "apps/standalone/native_tests/test_standalone_percussion_raster.cpp"
LOWER_SOURCE = "apps/standalone/native_tests/test_standalone_lower_rack_material_raster.cpp"
REFERENCE_SHA = "9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187"
REFERENCE_RGB_SHA = "07a7e35a2fd6610d623bbc1da8c995f3f4d95c4b45a0a5c1f41ad1395584bbeb"
ORIGINS_SHA = "9851e00a147dd982e8d5eac1136238db6564ca2010512badd75041e2fa54b54e"
CENTERS = (685, 734, 782, 830, 878, 927, 975, 1024, 1074)
PATCHES = {
    "left": (612, 320, 18, 128), "right": (1094, 320, 14, 128),
    "left_top": (612, 298, 18, 14), "right_top": (1094, 298, 14, 14),
    "center_top": (800, 302, 112, 6),
    "left_bottom": (612, 460, 18, 20), "right_bottom": (1094, 460, 14, 20),
    "bottom_interior_left": (704, 492, 12, 8),
    "bottom_interior_middle": (852, 492, 14, 8),
    "bottom_interior_right": (1047, 492, 12, 8),
}
PRIMARY = tuple(PATCHES)[:7]
MAX_ARTIFACT_BYTES = 80 * 1024 * 1024
LOWER_SOURCE_SHA = "281df1de3edce6a91a851d0b5674677646f1741fac1512f474ea7ffda67350e7"
BEFORE_LOWER_SHA = "1ffcd7e3b70b813e7af2cc5986be0659df93ee0c058ad66f329208d7e11c60ac"
MAX_HEADER = 512 * 1024
MAX_PIXELS = 3900 * 2200
LIMITS = (
    "Scoped software preservation and reference-size patch statistics only. "
    "Whole-interface 1:1 remains unmet and unwaived. Full-frame visual admission, "
    "actual application "
    "captures, real display/DPI/input, accessibility and physical/audio fidelity "
    "require separate source-bound evidence. Maximum-geometry resource cases expose "
    "only 64x64 output and therefore have no protected output pixels."
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_identity(path):
    data = path.read_bytes()
    return {"path": str(path.resolve()), "bytes": len(data), "sha256": sha(data)}


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def write_new(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def f32(value):
    """Each explicit call is one IEEE binary32 rounding, independent of C++."""
    return struct.unpack("<f", struct.pack("<f", value))[0]


def bounds(width, height):
    sx, sy = f32(width / 1672), f32(height / 941)
    bx, by = f32(600 * sx), f32(269 * sy)
    bw, bh = f32(f32(1116 * sx) - bx), f32(f32(508 * sy) - by)
    dx, dy = f32(4 * sx), f32(4 * sy)
    inset = [f32(bx + dx), f32(by + dy),
             max(0, f32(bw - f32(2 * dx))), max(0, f32(bh - f32(2 * dy)))]
    return (sx, sy), (bx, by, bw, bh), inset


def mapped(width, height, rectangle):
    sx, sy = f32(width / 1672), f32(height / 941)
    x, y, w, h = rectangle
    left, top = f32(x * sx), f32(y * sy)
    return [left, top, f32(f32(f32(x + w) * sx) - left),
            f32(f32(f32(y + h) * sy) - top)]


def gradient_box(rectangle, scale):
    x, y, w, h = rectangle
    rx, ry = scale
    return [math.ceil(x * rx - .5), math.ceil(y * ry - .5),
            math.ceil((x + w) * rx - .5), math.ceil((y + h) * ry - .5)]


def fill_box(rectangle, scale):
    x, y, w, h = rectangle
    rx, ry = scale
    left, top = math.trunc(f32(x * rx)), math.trunc(f32(y * ry))
    return [left, top, left + max(math.trunc(f32(w * rx)), 1),
            top + max(math.trunc(f32(h * ry)), 1)]


def translate(box, origin):
    x, y = origin
    return [box[0] + x, box[1] + y, box[2] + x, box[3] + y]


def xywh_box(rectangle):
    x, y, w, h = rectangle
    return [x, y, x + w, y + h]


def intersect(*boxes):
    left, top = max(b[0] for b in boxes), max(b[1] for b in boxes)
    right, bottom = min(b[2] for b in boxes), min(b[3] for b in boxes)
    return [left, top, max(left, right), max(top, bottom)]


def area(box):
    return (box[2] - box[0]) * (box[3] - box[1])


def contains(outer, inner):
    return outer[0] <= inner[0] <= inner[2] <= outer[2] and outer[1] <= inner[1] <= inner[3] <= outer[3]


def mix(value):
    value ^= value >> 16
    value = (value * 0x7FEB352D) & 0xffffffff
    value ^= value >> 15
    value = (value * 0x846CA68B) & 0xffffffff
    return value ^ (value >> 16)


def new_origins():
    return [(606 + mix(0xB3160A08 ^ k) % 504,
             275 + mix(0xB3160A08 ^ (k + 1)) % 227)
            for pair in range(2304) for k in (4 * pair, 4 * pair + 2)]


def grain_supports(width, height, scale):
    """Original source lattice and frozen new hash marks; never inspect pixels."""
    (sx, sy), (bx, by, bw, bh), inset = bounds(width, height)
    rows = math.floor(max(0, f32(f32(bh / sy) - 16)))
    columns = math.floor(max(0, f32(f32(bw / sx) - 21)))
    step = max(4, math.ceil(math.sqrt(rows * columns / (3.0 * 2048))))

    def pairs(pitch):
        return (1 + (rows - 2) // pitch if rows > 1 else 0) * (
            1 + (columns - 2) // (pitch * 3) if columns > 1 else 0)

    while pairs(step) > 2048:
        step += 1
    old = []
    for row in range(1, rows, step):
        for column in range(1, columns, step * 3):
            if len(old) >= 4096:
                break
            grain = (row * 1973 + column * 9277) & 0xffffffff
            x = f32(bx + f32(f32(f32(7 + f32(column)) + f32((grain >> 5) % 3)) * sx))
            y = f32(by + f32(f32(7 + f32(row)) * sy))
            old.append(fill_box((x, y, sx, sy), scale))
            old.append(fill_box((f32(x + f32(3 * sx)), f32(y + sy), f32(2 * sx), sy), scale))
    new = [fill_box((f32(x * sx), f32(y * sy), sx, sy), scale) for x, y in new_origins()]
    return old, new, {"old_rows": rows, "old_columns": columns,
                      "old_step": step, "old_pairs": len(old) // 2,
                      "old_rectangle_count": len(old), "new_rectangle_count": len(new)}


def percussion_cases():
    """Literal independent inventory of the immutable existing 66 indices."""
    result = []

    def add(w=1672, h=941, scale=1, values=0, focus=0, route=0,
            pending=False, presentation=0, workspace=0, clip=0):
        offset = 7 if clip else 0
        vw, vh = math.ceil(f32(w * scale)), math.ceil(f32(h * scale))
        physical_clip = [0, 0, 0, 0]
        if clip == 1:
            physical_clip = [math.trunc(f32(n * scale)) for n in (180, 138, 275, 77)]
        elif clip == 2:
            physical_clip = [math.floor(n * scale) for n in (161, 174, 252, 41)]
        result.append({"suite": "percussion", "case": len(result), "logical_size": [w, h],
                       "scale": [scale, scale], "output_size": [vw + 2 * offset, vh + 2 * offset],
                       "viewport": [offset, offset, vw, vh], "clip": physical_clip,
                       "clip_enabled": bool(clip), "active": presentation == workspace == 0 and
                       1400 <= w <= 8192 and 820 <= h <= 8192, "resource_crop": False,
                       "fixture": [w, h, values, focus, route, int(pending), presentation, workspace, clip],
                       "offset": offset, "transform_provenance":
                       "Immutable fixture setup; original stream has no physical getter fields."})

    for value in range(16):
        add(values=value, focus=value % 4, route=value % 4, pending=value % 2 != 0)
    for scale in (1.5, 2):
        add(scale=scale, values=15, focus=3, pending=True)
    for w, h in ((1400, 820), (1920, 1080)):
        for scale in (1, 1.5, 2):
            add(w, h, scale, 9, 1, 1)
    for w, h in ((1399, 820), (1400, 819)):
        for scale in (1, 1.5, 2):
            add(w, h, scale, 6, 2, 2, True)
    for w, h in ((960, 700), (1280, 900)):
        for scale in (1, 2):
            add(w, h, scale, 5, 0, 3)
    for w, h in ((1672, 941), (1920, 1080)):
        for scale in (1, 1.5, 2):
            add(w, h, scale, 10, 3, 0, True, 1)
    for workspace in (1, 2):
        for presentation in (0, 1):
            for scale in (1, 1.5, 2):
                add(scale=scale, values=11, focus=1, route=2,
                    presentation=presentation, workspace=workspace)
    for w, h in ((1400.25, 820.75), (1672.5, 941.25)):
        add(w, h, 1.5, 14, 2)
    for scale in (1, 1.5, 2):
        for clip in (1, 2):
            add(scale=scale, values=13, pending=True, clip=clip)
    for h in (933.25, 933.5):
        for scale in (1, 1.5, 2):
            add(h=h, scale=scale, values=3, focus=2, route=3, pending=True)
    require(len(result) == 66, "original inventory must have 66 indices")
    return result


def lower_cases():
    """Literal 32-state Lower specification, including unequal scale pairs."""
    result = []

    def add(w=1672, h=941, scale=1, level=4, route="B", pending=False,
            held=True, origin=(13, 17), clip_kind="disabled", resource=False,
            scale_y=None):
        rx, ry = scale, scale if scale_y is None else scale_y
        vw, vh = math.ceil(f32(w * rx)), math.ceil(f32(h * ry))
        left, top, right, bottom = gradient_box(bounds(w, h)[2], (rx, ry))
        if resource:
            origin, size = (-left, -top), [64, 64]
        else:
            size = [vw + 2 * origin[0], vh + 2 * origin[1]]
        viewport = [*origin, vw, vh]
        clip = [0, 0, 0, 0]
        logical_clip = None
        if clip_kind.startswith("logical-"):
            logical_clip = {"logical-left": [602, 300, 4, 160],
                            "logical-right": [1110, 300, 4, 160],
                            "logical-top": [618, 271, 474, 4],
                            "logical-bottom": [618, 502, 474, 4],
                            "logical-empty": [604, 273, 0, 0]}[clip_kind]
            clip = [math.floor(n * r) for n, r in zip(logical_clip, (rx, ry, rx, ry), strict=True)]
        elif clip_kind != "disabled":
            clip = {"physical-left": [left - 2, top - 2, 4, bottom - top + 4],
                    "physical-right": [right - 2, top - 2, 4, bottom - top + 4],
                    "physical-top": [left - 2, top - 2, right - left + 4, 4],
                    "physical-bottom": [left - 2, bottom - 2, right - left + 4, 4],
                    "physical-disjoint": [right + 4, top + 4, 8, 8],
                    "physical-empty": [left, top, 0, 0]}[clip_kind]
        if logical_clip is None:
            logical_clip = [math.floor(n / r) for n, r in zip(clip, (rx, ry, rx, ry), strict=True)]
        result.append({"suite": "lower", "case": len(result), "logical_size": [w, h],
                       "scale": [rx, ry], "output_size": size, "viewport": viewport,
                       "logical_viewport": [math.floor(n / r) for n, r in zip(viewport, (rx, ry, rx, ry), strict=True)],
                       "clip": clip, "logical_clip": logical_clip,
                       "clip_enabled": clip_kind != "disabled", "clip_kind": clip_kind,
                       "blend": 0 if clip_kind == "logical-empty" else 1,
                       "active": True, "resource_crop": resource, "level": level,
                       "route": route, "route_index": {"A": 10, "B": 11, "D": 2, "Cancel": 0}[route],
                       "pending": pending, "held": held, "edited_bank": "A" if route == "A" else "B",
                       "focus": [4, 1, 0 if route == "A" else 1, level],
                       "transform_provenance": "Physical/logical getters checked against independent frozen Lower inventory."})

    for w, h, states in ((1672, 941, ((0, "B", False, False), (4, "A", True, True), (8, "D", False, True))),
                         (1400, 820, ((4, "Cancel", True, False), (8, "B", False, False), (0, "A", True, True))),
                         (1920, 1080, ((8, "D", True, True), (0, "Cancel", False, False), (4, "B", True, False)))):
        for scale, state in zip((1, 1.5, 2), states, strict=True):
            add(w, h, scale, *state)
    for edge in ("left", "right", "top", "bottom"):
        for scale in (1, 1.5, 2):
            add(scale=scale, origin=(0, 0) if scale == 1.5 else (13, 17),
                clip_kind=("logical-" if scale == 1.5 else "physical-") + edge)
    for scale, kind in zip((1, 1.5, 2), ("physical-disjoint", "physical-empty", "logical-empty"), strict=True):
        add(scale=scale, clip_kind=kind)
    for scale in (1, 1.5, 2):
        add(8192, 8192, scale, resource=True)
    add(level=0, held=False, origin=(0, 0))
    add(origin=(0, 0))
    add(level=8, route="D", pending=True, origin=(0, 0))
    add(w=1920, h=820)
    add(scale=1.5, scale_y=2, level=8, route="A", pending=True)
    require(len(result) == 32, "supplemental inventory must have 32 indices")
    return result


def declare_case(case):
    result = dict(case)
    width, height = case["output_size"]
    origin = case["viewport"][:2]
    visible = intersect([0, 0, width, height], xywh_box(case["viewport"]))
    if case["clip_enabled"]:
        visible = intersect(visible, translate(xywh_box(case["clip"]), origin))
    result["visible_device_box"] = visible
    result["compared_pixels"] = width * height
    if not case["active"]:
        result.update({"intrinsic_pixels": 0, "expanded_intrinsic_pixels": 0,
                       "visible_intrinsic_pixels": 0, "allowed_pixels": 0,
                       "protected_pixels": width * height, "allowance_box": [0, 0, 0, 0],
                       "whole_frame_equality_required": True, "support": None})
        return result
    logical = case["logical_size"]
    composition_scale, panel, inset = bounds(*logical)
    gradient = gradient_box(inset, case["scale"])
    old, new, support = grain_supports(*logical, case["scale"])
    envelope = [gradient[0] - 1, gradient[1] - 1, gradient[2] + 1, gradient[3] + 1]
    require(all(contains(envelope, box) for box in old + new), "source grain leaves the frozen one-device-pixel envelope")
    # The admitted finite matrix has every grain fill inside the gradient. This
    # explicit support proof reduces the exact UNION to one rectangle. Do not
    # replace a failed assertion with a broader box or learn bounds from pixels.
    require(all(contains(gradient, box) for box in old + new), "declared union needs independent review: grain not inside gradient")
    intrinsic = translate(gradient, origin)
    expanded = translate(envelope, origin)
    allowance = intersect(expanded, visible)
    support.update({"composition_scale_binary32": composition_scale,
                    "panel_binary32": panel, "inset_binary32": inset,
                    "gradient_viewport_relative_box": gradient,
                    "translated_intrinsic_union_box": intrinsic,
                    "expanded_intrinsic_union_box": expanded,
                    "old_ordered_fill_boxes_sha256": sha(canonical_json(old)),
                    "new_ordered_fill_boxes_sha256": sha(canonical_json(new)),
                    "every_grain_inside_gradient": True, "every_support_inside_one_pixel_envelope": True})
    result.update({"support": support, "intrinsic_pixels": area(intrinsic),
                   "expanded_intrinsic_pixels": area(expanded),
                   "visible_intrinsic_pixels": area(intersect(intrinsic, visible)),
                   "allowance_box": allowance, "allowed_pixels": area(allowance),
                   "protected_pixels": width * height - area(allowance),
                   "whole_frame_equality_required": area(allowance) == 0})
    return result


def declare_mask():
    origins = new_origins()
    origin_sha = sha(b"".join(struct.pack("<HH", *origin) for origin in origins))
    require(origin_sha == ORIGINS_SHA and len(set(origins)) == 4501, "frozen new grain origin identity differs")
    cases = [declare_case(case) for case in percussion_cases() + lower_cases()]
    require(sum(c["active"] for c in cases[:66]) == 38, "original active count differs")
    require(sum(c["allowed_pixels"] > 0 for c in cases[:66]) == 32, "original nonempty count differs")
    require(sum(c["allowed_pixels"] > 0 for c in cases[66:]) == 29, "supplemental nonempty count differs")
    require(cases[0]["allowance_box"] == [603, 272, 1113, 505] and
            cases[0]["allowed_pixels"] == 118830 and cases[0]["support"]["old_pairs"] == 1485,
            "canonical independently derived support differs")
    return {"schema": 1, "model_id": MODEL, "protocol": PROTOCOL,
            "stage": "source-derived-declaration-before-paired-streams",
            "declared_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "policy": "Union of actual old gradient/grain and declared new field/grain support; exactly one physical pixel per side, then physical caller/output intersection. No candidate pixels, legacy regions, logical padding or wood-line allowance.",
            "box_convention": "Integer half-open [left,top,right,bottom]; SDL viewport/clip headers use [x,y,width,height].",
            "new_origin_little_endian_uint16_sha256": origin_sha,
            "new_marks": len(origins), "unique_new_origins": len(set(origins)),
            "cases": cases, "limits": LIMITS}


def command(executable, arguments, timeout):
    result = subprocess.run([str(executable), *arguments], capture_output=True, timeout=timeout, check=False)
    require(result.returncode == 0, f"{executable.name} {arguments}: exit {result.returncode}: {result.stderr[:4096]!r}")
    require(not result.stderr, f"unexpected helper stderr: {result.stderr[:4096]!r}")
    return result.stdout


def frame(executable, index, timeout):
    payload = command(executable, ["--case", str(index)], timeout)
    boundary = payload.find(b"\n", 0, MAX_HEADER)
    require(boundary >= 0, "missing bounded JSON frame header")
    header_bytes = payload[:boundary]
    header = json.loads(header_bytes)
    require(isinstance(header, dict) and header.get("schema") == 1 and header.get("case") == index,
            "wrong frame schema/index")
    width, height = header.get("width"), header.get("height")
    require(type(width) is type(height) is int and 0 < width <= 3900 and 0 < height <= 2200 and
            width * height <= MAX_PIXELS, "unbounded frame dimensions")
    pixels = payload[boundary + 1:]
    require(header.get("bytes") == len(pixels) == width * height * 4, "incorrect RGBA byte count/trailing bytes")
    return header, pixels, sha(header_bytes)


def metadata_value_equal(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return a == b
    if type(a) is not type(b):
        return False
    if isinstance(a, list):
        return len(a) == len(b) and all(metadata_value_equal(x, y) for x, y in zip(a, b, strict=True))
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(metadata_value_equal(a[k], b[k]) for k in a)
    return a == b


def metadata_errors(spec, header):
    expected = {"schema": 1, "case": spec["case"], "width": spec["output_size"][0],
                "height": spec["output_size"][1], "bytes": spec["compared_pixels"] * 4}
    if spec["suite"] == "percussion":
        expected.update({"fixture": spec["fixture"], "scale": spec["scale"][0],
                         "offset": spec["offset"], "active": spec["active"]})
    else:
        expected.update({key: spec[key] for key in ("logical_size", "output_size", "scale", "viewport", "clip",
                        "logical_viewport", "logical_clip", "clip_enabled", "blend", "clip_kind", "level", "route",
                        "route_index", "pending", "held", "edited_bank", "focus", "resource_crop")})
        expected["protocol"] = PROTOCOL
    errors = [f"{key}: expected {value!r}, observed {header.get(key)!r}" for key, value in expected.items()
              if not metadata_value_equal(header.get(key), value)]
    if spec["suite"] == "lower":
        try:
            view, layout = header["model"]["view"], header["model"]["layout"]
            applied = view["applied"]
            checks = {"focus": view["focus"] == spec["focus"], "edited bank": view["edited_banks"][1] == spec["focus"][2],
                      "pending": view["controls_pending"] == spec["pending"],
                      "workspace/presentation": view["workspace"] == view["presentation"] == layout["workspace"] == layout["presentation"] == 0,
                      "geometry size": [layout["width"], layout["height"]] == spec["logical_size"],
                      "68 controls": layout["control_count"] == 68,
                      "147 playing keys": sum(map(len, layout["manual_keys"])) + len(layout["pedal_keys"]) == 147,
                      "clock/rate/peak/revision": [applied[k] for k in ("frame_clock", "sample_rate", "peak", "publication_revision")] == [38400, 48000, .125, 4],
                      "prepared/running": applied["prepared"] is applied["running"] is True}
            for name, controls in (("desired", view["controls"]), ("applied", applied["controls"])):
                checks[name + " manual banks"] = controls["drawbars"] == [[[spec["level"]] * 9 for _ in range(2)] for _ in range(2)]
                checks[name + " constants"] = (controls["expression"] == .625 and controls["pedal_drawbars"] == [3, 7] and controls["percussion"] == [True, 0, 0, 0])
            held_keys = [[False] * 61 for _ in range(2)]
            held_keys[0][24] = held_keys[1][36] = spec["held"]
            held_pedals = [False] * 25
            held_pedals[12] = spec["held"]
            checks["held keys/pedals"] = applied["held_keys"] == held_keys and applied["held_pedals"] == held_pedals
            errors.extend("model " + key + " differs from fixture" for key, passed in checks.items() if not passed)
        except (KeyError, TypeError, IndexError) as error:
            errors.append("missing/malformed full model metadata: " + str(error))
    return errors


def difference_images(before, after):
    rgba = ImageChops.difference(before, after)
    channels = rgba.split()
    maximum = ImageChops.lighter(ImageChops.lighter(channels[0], channels[1]),
                                ImageChops.lighter(channels[2], channels[3]))
    changed = maximum.point(lambda value: 255 if value else 0)
    return rgba, channels, maximum, changed


def row_counts(image):
    width, height = image.size
    data = image.tobytes()
    return [data[y * width:(y + 1) * width].count(255) for y in range(height)]


def channel_counts(channels):
    return [sum(channel.histogram()[1:]) for channel in channels]


def protected_children(spec, before, after):
    if spec["suite"] != "lower" or spec["clip_enabled"] or spec["resource_crop"]:
        return {"applicable": False, "passed": True, "probes": []}
    origin, scale = spec["viewport"][:2], spec["scale"]
    probes = []
    for index, center in enumerate(CENTERS):
        for kind, rectangle in (("well", (center - 12, 320, 4, 130)),
                                ("cap", (center - 10, 327 + 118 * spec["level"] / 8 - 10, 20, 12))):
            box = translate(gradient_box(mapped(*spec["logical_size"], rectangle), scale), origin)
            box = [box[0] + 1, box[1] + 1, box[2] - 1, box[3] - 1]
            require(area(box) > 0 and contains([0, 0, *spec["output_size"]], box), "empty/invisible protected child probe")
            old, new = before.crop(box), after.crop(box)
            _, channels, maximum, changed = difference_images(old, new)
            opaque = old.getchannel("A").getextrema() == new.getchannel("A").getextrema() == (255, 255)
            probes.append({"control": index, "kind": kind, "device_box": box, "pixels": area(box),
                           "different_pixels": changed.histogram()[255], "different_channels": sum(channel_counts(channels)),
                           "maximum_channel_delta": maximum.getextrema()[1], "opaque": opaque,
                           "passed": opaque and changed.getbbox() is None})
    focus_rect = mapped(*spec["logical_size"], (CENTERS[spec["level"]] - 23, 309, 46, 197))
    box = translate(gradient_box(focus_rect, scale), origin)
    box = intersect([box[0] - 2, box[1] - 2, box[2] + 2, box[3] + 2], [0, 0, *spec["output_size"]])

    def cyan_mask(image):
        channels = image.crop(box).split()
        mask = channels[0].point(lambda value: 255 if value == 165 else 0)
        for channel, value in zip(channels[1:], (228, 223, 255), strict=True):
            mask = ImageChops.darker(mask, channel.point(lambda actual, target=value: 255 if actual == target else 0))
        return mask

    old, new = cyan_mask(before), cyan_mask(after)
    old_count, new_count = old.histogram()[255], new.histogram()[255]
    focus_differences = ImageChops.difference(old, new).histogram()[255]
    focus = {"device_box": box, "before_pixels": old_count, "after_pixels": new_count,
             "differing_positions": focus_differences, "before_mask_sha256": sha(old.tobytes()),
             "after_mask_sha256": sha(new.tobytes()), "passed": old_count > 0 and new_count > 0 and focus_differences == 0}
    return {"applicable": True, "probes": probes, "focus": focus,
            "passed": all(probe["passed"] for probe in probes) and focus["passed"],
            "literal_glyph_contrast": "Both frozen native binaries run their ordinary32-case strong-glyph/contrast and clip/repeat assertions in this report; paired opaque RGBA/focus equality is independently measured here."}


def patch_statistics(rgb, rectangle, channel=None):
    """Exact orthogonal plane sufficient statistics, independent of authoring receipts."""
    left, top, width, height = rectangle
    denominator = 10000 if channel is None else 1
    pixels = rgb.load()
    total = squared = sum_lx = sum_ly = sum_x2 = sum_y2 = 0
    for y in range(height):
        cy = 2 * y - (height - 1)
        for x in range(width):
            cx = 2 * x - (width - 1)
            pixel = pixels[left + x, top + y]
            value = sum(a * b for a, b in zip(pixel, (2126, 7152, 722), strict=True)) if channel is None else pixel[channel]
            total += value
            squared += value * value
            sum_lx += value * cx
            sum_ly += value * cy
            sum_x2 += cx * cx
            sum_y2 += cy * cy
    count = width * height
    mean = Fraction(total, denominator * count)
    slope_x = Fraction(2 * sum_lx, denominator * sum_x2)
    slope_y = Fraction(2 * sum_ly, denominator * sum_y2)
    sse = (Fraction(squared) - Fraction(total * total, count) -
           Fraction(sum_lx * sum_lx, sum_x2) - Fraction(sum_ly * sum_ly, sum_y2)) / denominator**2
    require(sse >= 0, "negative exact plane residual")
    return {"patch_xywh": list(rectangle), "pixels": count, "channel_denominator": denominator,
            "sum_L": total, "sum_L2": squared, "sum_LX": sum_lx, "sum_LY": sum_ly,
            "sum_X2": sum_x2, "sum_Y2": sum_y2,
            "mean_exact": str(mean), "mean": float(mean),
            "slope_x_exact": str(slope_x), "slope_x": float(slope_x),
            "slope_y_exact": str(slope_y), "slope_y": float(slope_y),
            "residual_sse_exact": str(sse), "residual_sse": float(sse),
            "residual_variance_exact": str(sse / count),
            "residual_rms": math.sqrt(float(sse / count))}


def image_statistics(image):
    rgb = image.convert("RGB")
    patches = {name: {"xywh": list(rectangle), "primary": name in PRIMARY,
                     "Yprime": patch_statistics(rgb, rectangle),
                     "RGB": [patch_statistics(rgb, rectangle, channel) for channel in range(3)]}
               for name, rectangle in PATCHES.items()}
    difference = Fraction(patches["right"]["Yprime"]["mean_exact"]) - Fraction(patches["left"]["Yprime"]["mean_exact"])
    return {"rgb_sha256": sha(rgb.tobytes()), "size": list(rgb.size), "patches": patches,
            "right_minus_left_exact": str(difference), "right_minus_left": float(difference)}


def reference_screens(reference, actual):
    """Original v1 inequalities, including all failures; no corrected patch or waiver."""
    results = []

    def exact_screen(name, ref, candidate, field, maximum):
        exact_error = abs(Fraction(candidate[field + "_exact"]) - Fraction(ref[field + "_exact"]))
        results.append({"name": name, "reference": ref[field], "actual": candidate[field],
                        "absolute_error": float(exact_error), "absolute_error_exact": str(exact_error),
                        "maximum_error": float(maximum), "maximum_error_exact": str(maximum),
                        "passed": exact_error <= maximum})

    for patch in PRIMARY:
        ref, candidate = reference["patches"][patch], actual["patches"][patch]
        exact_screen(patch + "_mean_Yprime", ref["Yprime"], candidate["Yprime"], "mean", Fraction(5, 2))
        for channel, name in enumerate("RGB"):
            exact_screen(patch + "_mean_" + name, ref["RGB"][channel], candidate["RGB"][channel], "mean", Fraction(3))
    for patch in ("left", "right"):
        ref, candidate = reference["patches"][patch]["Yprime"], actual["patches"][patch]["Yprime"]
        error = abs(candidate["residual_rms"] - ref["residual_rms"])
        # Decide the radical inequality exactly, without floating-rounding ties:
        # |sqrt(a)-sqrt(b)| <= c iff a+b-c*c <= 0 or (a+b-c*c)^2 <=4*a*b.
        a, b, c = Fraction(candidate["residual_variance_exact"]), Fraction(ref["residual_variance_exact"]), Fraction(1, 2)
        q = a + b - c*c
        passed = q <= 0 or q*q <= 4*a*b
        results.append({"name": patch + "_residual_rms", "reference": ref["residual_rms"],
                        "actual": candidate["residual_rms"], "absolute_error": error,
                        "maximum_error": .5, "exact_variance_comparison": {"a": str(a), "b": str(b), "q": str(q)},
                        "passed": passed})
        exact_screen(patch + "_slope_x", ref, candidate, "slope_x", Fraction(3, 50))
        exact_screen(patch + "_slope_y", ref, candidate, "slope_y", Fraction(1, 40))
    exact_screen("right_minus_left", reference, actual, "right_minus_left", Fraction(7, 4))
    require(len(results) == 35, "exactly35 frozen inequalities")
    return {"protocol": PROTOCOL, "passed": all(row["passed"] for row in results),
            "passed_inequalities": sum(row["passed"] for row in results),
            "failed_inequalities": [row for row in results if not row["passed"]], "screens": results}


def compare_case(spec, before_frame, after_frame, reference, output):
    old_header, old_bytes, old_header_sha = before_frame
    new_header, new_bytes, new_header_sha = after_frame
    errors = {"before": metadata_errors(spec, old_header), "after": metadata_errors(spec, new_header)}
    metadata_equal = canonical_json(old_header) == canonical_json(new_header)
    require([old_header["width"], old_header["height"]] == [new_header["width"], new_header["height"]] == spec["output_size"],
            "cannot compare mismatched frame dimensions")
    size = tuple(spec["output_size"])
    before = Image.frombuffer("RGBA", size, old_bytes, "raw", "RGBA", 0, 1)
    after = Image.frombuffer("RGBA", size, new_bytes, "raw", "RGBA", 0, 1)
    rgba_diff, channels, maximum, changed = difference_images(before, after)
    escaped = changed.copy()
    outside_maximum = maximum.copy()
    outside_channels = []
    box = spec["allowance_box"]
    if area(box):
        escaped.paste(0, box)
        outside_maximum.paste(0, box)
    for channel in channels:
        outside = channel.copy()
        if area(box):
            outside.paste(0, box)
        outside_channels.append(sum(outside.histogram()[1:]))
    changed_counts, escaped_counts = row_counts(changed), row_counts(escaped)
    result = {"suite": spec["suite"], "case": spec["case"], "logical_size": spec["logical_size"],
              "scale": spec["scale"], "output_size": spec["output_size"], "active": spec["active"],
              "resource_crop": spec["resource_crop"], "clip_enabled": spec["clip_enabled"],
              "compared_pixels": spec["compared_pixels"], "intrinsic_pixels": spec["intrinsic_pixels"],
              "expanded_intrinsic_pixels": spec["expanded_intrinsic_pixels"], "visible_intrinsic_pixels": spec["visible_intrinsic_pixels"],
              "allowed_pixels": spec["allowed_pixels"], "protected_pixels": spec["protected_pixels"],
              "whole_frame_equality_required": spec["whole_frame_equality_required"],
              "before_rgba_sha256": sha(old_bytes), "after_rgba_sha256": sha(new_bytes),
              "before_header_bytes_sha256": old_header_sha, "after_header_bytes_sha256": new_header_sha,
              "before_metadata_sha256": sha(canonical_json(old_header)), "after_metadata_sha256": sha(canonical_json(new_header)),
              "all_metadata_exact": metadata_equal, "ignored_metadata_fields": [], "metadata_errors": errors,
              "different_pixels": sum(changed_counts), "different_channels_by_rgba": channel_counts(channels),
              "maximum_channel_delta": maximum.getextrema()[1], "difference_bounds": changed.getbbox(),
              "per_row_different_pixels": changed_counts, "outside_allowance_pixels": sum(escaped_counts),
              "outside_allowance_channels_by_rgba": outside_channels,
              "outside_allowance_maximum_channel_delta": outside_maximum.getextrema()[1],
              "outside_allowance_bounds": escaped.getbbox(), "per_row_outside_allowance_pixels": escaped_counts,
              "children": protected_children(spec, before, after)}
    result["different_channels"] = sum(result["different_channels_by_rgba"])
    result["outside_allowance_channels"] = sum(outside_channels)
    result["whole_frame_equal"] = result["different_pixels"] == 0
    result["nonvacuous_surface_change"] = spec["allowed_pixels"] == 0 or result["different_pixels"] > 0
    result["passed"] = (metadata_equal and not any(errors.values()) and result["outside_allowance_pixels"] == 0 and
                         result["outside_allowance_channels"] == 0 and result["children"]["passed"] and
                         result["nonvacuous_surface_change"])
    result["preservation_passed"] = result["passed"]
    if (spec["suite"], spec["case"]) in (("percussion", 0), ("lower", 28)):
        for name, image in (("before", before), ("after", after)):
            stats = image_statistics(image)
            result[name + "_statistics"] = stats
            result[name + "_reference_screens"] = reference_screens(reference, stats)
        # Both original before observations are retained as expected failures.
        # Only supplemental case 28 is the candidate numerical admission case.
        if spec["suite"] == "lower":
            result["passed"] &= result["after_reference_screens"]["passed"]
    if not result["passed"]:
        prefix = f"{spec['suite']}-{spec['case']:02d}"
        artifacts = {}
        for label, image in (("before", before), ("after", after), ("absolute-rgba-difference", rgba_diff),
                             ("maximum-channel-difference", maximum), ("outside-allowance-mask", escaped)):
            path = output / (prefix + "-" + label + ".png")
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            payload = buffer.getvalue()
            retained = sum(item.stat().st_size for item in output.iterdir() if item.is_file())
            require(retained + len(payload) <= MAX_ARTIFACT_BYTES,
                    "failure artifact would exceed80MiB output cap; comparison remains failed/incomplete")
            with path.open("xb") as stream:
                stream.write(payload)
            artifacts[label] = file_identity(path)
        # Preserve the exact metadata, not merely a digest, when it fails.
        if not metadata_equal or any(errors.values()):
            path = output / (prefix + "-headers.json")
            write_new(path, {"before": old_header, "after": new_header})
            artifacts["headers"] = file_identity(path)
        result["failure_artifacts"] = artifacts
    return result


def git_bytes(repo, *args):
    return subprocess.check_output(["git", *args], cwd=repo, stderr=subprocess.PIPE)


def identities(args):
    repo = args.repo
    require(file_identity(repo / CONTRACT)["sha256"] == CONTRACT_SHA, "frozen Lower v1 contract differs")
    require(file_identity(args.before_painter)["sha256"] == BEFORE_PAINTER_SHA, "genuine before painter differs")
    require(file_identity(args.before_percussion)["sha256"] == BEFORE_PERCUSSION_SHA, "original 66-case binary differs")
    receipt_bytes = args.baseline_receipt.read_bytes()
    receipt = json.loads(receipt_bytes)
    require(receipt["baseline"] == BASE and receipt["fixture"]["status"] == "passed" and
            receipt["production_painter_unchanged"] is True and receipt["painter_sha256"] == BEFORE_PAINTER_SHA and
            receipt["contract_sha256"] == CONTRACT_SHA, "supplemental before qualification receipt differs")
    require(file_identity(args.before_lower)["sha256"] == receipt["files"]["test_standalone_lower_rack_material_raster"]["sha256"] == BEFORE_LOWER_SHA, "supplemental before binary does not match retained receipt")
    require(file_identity(repo / LOWER_SOURCE)["sha256"] == receipt["files"]["test_standalone_lower_rack_material_raster.cpp"]["sha256"] == LOWER_SOURCE_SHA, "supplemental harness changed after genuine before build")
    require(file_identity(args.reference)["sha256"] == REFERENCE_SHA, "original reference JPEG differs")
    common = ["apps/standalone/" + name for name in ("UiModel.cpp", "UiModel.h", "InstrumentView.h", "Drawing.cpp", "Drawing.h",
              "FontData.h", "InspectionModel.cpp", "InspectionModel.h")] + [PERCUSSION_SOURCE]
    baseline = {}
    current = {}
    for name in common:
        old = git_bytes(repo, "show", f"{BASE}:{name}")
        new = (repo / name).read_bytes()
        require(old == new, "common source/font/art/harness changed: " + name)
        baseline[name] = sha(old)
        current[name] = sha(new)
    baseline["apps/standalone/InstrumentView.cpp"] = BEFORE_PAINTER_SHA
    baseline[LOWER_SOURCE] = receipt["files"]["test_standalone_lower_rack_material_raster.cpp"]["sha256"]
    for name in ("apps/standalone/InstrumentView.cpp", LOWER_SOURCE, CONTRACT,
                 "docs/design/atlas-reference.json", "docs/reviews/LOWER_RACK_MATERIAL_ADMISSION.md"):
        current[name] = file_identity(repo / name)["sha256"]
    binaries = {name: file_identity(getattr(args, name)) for name in
                ("before_percussion", "after_percussion", "before_lower", "after_lower")}
    build = {}
    if args.build_dir:
        for relative in ("CMakeCache.txt", "build.ninja", "apps/standalone/generated/ReferenceArtData.h", "_sdl2/libSDL2.a"):
            path = args.build_dir / relative
            build[relative] = file_identity(path) if path.is_file() else {"missing": True}
    return {"baseline_commit": BASE, "observed_head": git_bytes(repo, "rev-parse", "HEAD").decode().strip(),
            "observed_head_tree": git_bytes(repo, "rev-parse", "HEAD^{tree}").decode().strip(),
            "baseline_source_sha256": baseline, "current_source_sha256": current, "binaries": binaries,
            "baseline_painter": file_identity(args.before_painter), "reference": file_identity(args.reference),
            "supplemental_before_receipt": file_identity(args.baseline_receipt),
            "tool": file_identity(Path(__file__)), "build_inputs": build,
            "source_binding_limit": "Source, protocol and executable hashes plus the retained genuine supplemental before build receipt; hashes alone do not prove coherent candidate compilation. Root retains actual coordinated build evidence."}


def summarize(cases):
    children = [case["children"] for case in cases if case["children"]["applicable"]]
    probes = [probe for child in children for probe in child["probes"]]
    nonempty = [case for case in cases if case["allowed_pixels"] > 0]
    ordinary = [case for case in nonempty if not case["resource_crop"] and not case["clip_enabled"]]
    return {"pairs": len(cases), "passed_pairs": sum(case["passed"] for case in cases), "preservation_passed_pairs": sum(case["preservation_passed"] for case in cases),
            "failed_pairs": sum(not case["passed"] for case in cases),
            "active_pairs": sum(case["active"] for case in cases), "nonempty_allowances": len(nonempty),
            "whole_frame_equality_required": sum(case["whole_frame_equality_required"] for case in cases),
            "required_whole_frames_identical": sum(case["whole_frame_equality_required"] and case["whole_frame_equal"] for case in cases),
            "compared_pixels": sum(case["compared_pixels"] for case in cases),
            "protected_pixels": sum(case["protected_pixels"] for case in cases),
            "different_pixels": sum(case["different_pixels"] for case in cases),
            "different_channels": sum(case["different_channels"] for case in cases),
            "outside_allowance_pixels": sum(case["outside_allowance_pixels"] for case in cases),
            "outside_allowance_channels": sum(case["outside_allowance_channels"] for case in cases),
            "minimum_nonempty_protected_pixels": min((case["protected_pixels"] for case in nonempty), default=None),
            "minimum_full_frame_active_protected_pixels": min((case["protected_pixels"] for case in ordinary), default=None),
            "full_frame_child_cases": len(children), "opaque_child_probes": len(probes),
            "opaque_probe_pixels": sum(probe["pixels"] for probe in probes),
            "minimum_opaque_probe_pixels": min((probe["pixels"] for probe in probes), default=None),
            "cyan_focus_pixels": sum(child["focus"]["after_pixels"] for child in children),
            "minimum_cyan_focus_pixels": min((child["focus"]["after_pixels"] for child in children), default=None)}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    for name in ("before-percussion", "after-percussion", "before-lower", "after-lower", "before-painter"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--baseline-receipt", type=Path)
    parser.add_argument("--build-dir", type=Path, help="optional coordinated build directory for dependency/config identities")
    parser.add_argument("--output-dir", type=Path, required=True, help="new directory; existing paths are refused")
    parser.add_argument("--timeout", type=float, default=45, help="maximum seconds per native invocation")
    args = parser.parse_args()
    started = time.monotonic()
    report = {"schema": 1, "model_id": MODEL, "protocol": PROTOCOL, "status": "incomplete",
              "started_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "cwd": str(Path.cwd()),
              "command": [sys.executable, *sys.argv], "cases": [], "errors": [], "limits": LIMITS}
    try:
        args.repo = args.repo.resolve(strict=True)
        args.reference = (args.reference or args.repo / "docs/design/atlas-cover-reference.jpg").resolve(strict=True)
        args.baseline_receipt = (args.baseline_receipt or args.repo / SESSION / "reports/lower-before-identity.json").resolve(strict=True)
        for name in ("before_percussion", "after_percussion", "before_lower", "after_lower", "before_painter"):
            setattr(args, name, getattr(args, name).resolve(strict=True))
        if args.build_dir:
            args.build_dir = args.build_dir.resolve(strict=True)
        require(math.isfinite(args.timeout) and 0 < args.timeout <= 300, "timeout must be finite, positive and at most 300 seconds")
        require(args.output_dir.parent.is_dir(), "output parent must exist")
        args.output_dir.mkdir(exist_ok=False)
    except (OSError, ValueError) as error:
        print(json.dumps({"status": "setup-error", "error": str(error)}), file=sys.stderr)
        return 2
    try:
        report["identities"] = identities(args)
        inventories = {}
        for suite, count in (("percussion", 66), ("lower", 32)):
            expected = {"schema": 1, "cases": count}
            if suite == "lower":
                expected["protocol"] = PROTOCOL
            for side in ("before", "after"):
                key = side + "_" + suite
                payload = command(getattr(args, key), ["--list"], args.timeout)
                require(json.loads(payload) == expected, key + " inventory differs")
                inventories[key] = {"inventory": json.loads(payload), "stdout_sha256": sha(payload)}
        report["inventories"] = inventories
        mask = declare_mask()
        mask["identities"] = report["identities"]
        mask_path = args.output_dir / "mask.json"
        write_new(mask_path, mask)
        report["mask"] = file_identity(mask_path)
        report["ordinary_lower_invariants"] = {}
        for side in ("before", "after"):
            payload = command(getattr(args, side + "_lower"), [], args.timeout)
            observed = json.loads(payload)
            require(observed.get("status") == "passed" and observed.get("cases") == 32 and observed.get("protocol") == PROTOCOL,
                    side + " ordinary Lower fixture failed")
            require(observed.get("state_restorations") == 51 and observed.get("clip_companions") == 15 and
                    observed.get("opaque_child_probes") == 252 and observed.get("literal_glyphs") == 826 and
                    observed.get("focus_cases") == 14 and observed.get("case_28_repeats") == 2,
                    side + " ordinary Lower fixture coverage changed")
            report["ordinary_lower_invariants"][side] = {"result": observed, "stdout_sha256": sha(payload)}
        report["decoder"] = {"python": platform.python_version(), "platform": platform.platform(),
                             "Pillow": PILLOW_VERSION, "JPEG_API": features.version_codec("jpg"),
                             "libjpeg_turbo": features.version_feature("libjpeg_turbo"),
                             "operation": "Original JPEG decoded directly to RGB; no resizing, gamma transfer or edits."}
        with Image.open(args.reference) as source:
            require(source.size == (1672, 941), "reference dimensions differ")
            reference = image_statistics(source)
        require(reference["rgb_sha256"] == REFERENCE_RGB_SHA, "original decoded RGB identity differs")
        report["reference_statistics"] = reference
        for spec in mask["cases"]:
            try:
                before = frame(getattr(args, "before_" + spec["suite"]), spec["case"], args.timeout)
                after = frame(getattr(args, "after_" + spec["suite"]), spec["case"], args.timeout)
                result = compare_case(spec, before, after, reference, args.output_dir)
                report["cases"].append(result)
                del before, after
            except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
                report["errors"].append({"suite": spec["suite"], "case": spec["case"], "error": str(error)[:4096]})
            require(sum(path.stat().st_size for path in args.output_dir.iterdir() if path.is_file()) < MAX_ARTIFACT_BYTES,
                    "retained artifacts reached80MiB cap; remaining comparisons not executed")
            processed = len(report["cases"]) + len(report["errors"])
            if processed % 8 == 0 or processed == 98:
                print(json.dumps({"processed": processed, "total": 98,
                                  "failed_pairs": sum(not row["passed"] for row in report["cases"]),
                                  "process_errors": len(report["errors"])}), flush=True)
        require(file_identity(mask_path) == report["mask"], "mask changed during comparison")
        require(identities(args) == report["identities"], "source, executable, protocol or build identity changed during comparison")
        report["totals"] = summarize(report["cases"])
        report["suite_totals"] = {suite: summarize([case for case in report["cases"] if case["suite"] == suite])
                                  for suite in ("percussion", "lower")}
        report["status"] = "passed" if len(report["cases"]) == 98 and not report["errors"] and all(case["passed"] for case in report["cases"]) else "failed"
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        report["errors"].append({"error": str(error)[:4096]})
    report["elapsed_seconds"] = time.monotonic() - started
    if "totals" not in report:
        report["totals"] = summarize(report["cases"])
    write_new(args.output_dir / "report.json", report)
    print(json.dumps({"status": report["status"], "output_dir": str(args.output_dir.resolve()),
                      "errors": report["errors"], "totals": report["totals"]}), flush=True)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
