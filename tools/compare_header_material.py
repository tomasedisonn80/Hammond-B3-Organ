#!/usr/bin/env python3
r"""Independent bounded H1 preservation and 103-screen comparison.

Freeze this tool and the 48-case native fixture before H1 painting. The current
fixture admits only the exact reversible source corrections below;
its case values match the original baseline, while its source bytes differ.
The support is the independently enumerated union of Original gradient/grain
and H1 field/grain operations. Candidate colors, helpers and differences never
select an allowed pixel. All 48 main pairs, 16 uncut companion pairs, history
and fresh-renderer repeats, complete model/renderer records, opaque children,
rules and independent live-glyph cores are mandatory. The unchanged native T3
material gate is also executed. Numerical and actual-frame visual admission
remain distinct from successful transport/preservation execution.

Example (new output directory; do not configure/build while running):
  python3 -B tools/compare_header_material.py \
    --before ../pre-header-native/test_standalone_header_material \
    --after ../build-native/apps/standalone/test_standalone_header_material \
    --before-painter ../pre-header-native/InstrumentView.cpp \
    --baseline-receipt docs/development/2026-11-16-ui-delivery/reports/h1-baseline-identity.json \
    --baseline-receipt-sha256 "$h1_baseline_receipt_sha256" \
    --fixture-baseline-receipt docs/development/2026-11-16-ui-delivery/reports/h1-fixture-baseline-identity.json \
    --build-dir ../build-native --output /tmp/h1-comparison

Set h1_baseline_receipt_sha256 to the independently reviewed, root-frozen SHA-256
of this session's genuine pre-H1 receipt before starting the native comparison.
It is mandatory for native runs, has no default, and also binds the fixture
supplement. Do not derive the expected digest from a mutable receipt at run time.

Add --baseline-only before any H1 painter edit. That mode requires the current
painter to equal the genuine accepted T3 baseline, whole-frame equality of all
pairs, and exactly the preserved 44 passing / 59 failing numerical screens.
Its successful exit demonstrates the frozen baseline, never H1 acceptance.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import math
from pathlib import Path
import platform
import re
import shlex
import struct
import sys
import time

from PIL import Image, ImageChops, ImageDraw, __version__ as PILLOW_VERSION, features

import compare_heading_typography as transport
import compare_title_typography as typography

common = transport.common
f32, require = common.f32, common.require
identity, sha = transport.identity, transport.sha
read_json, write_json, json_bytes = transport.read_json, transport.write_json, transport.json_bytes
intersect, area, xywh = common.intersect, common.area, common.xywh

MODEL = "header-material-independent-paired-v1"
PROTOCOL = "header-material-h1-v1"
SESSION = "docs/development/2026-11-16-heading-title-continuation"
CONTRACT = "docs/design/HEADER_MATERIAL_H1_CONTRACT.md"
ADMISSION = "docs/reviews/HEADER_MATERIAL_H1_ADMISSION.md"
OBSERVATIONS = SESSION + "/reports/a22-header-observations.json"
BASELINE = "docs/development/2026-11-16-ui-delivery/reports/h1-baseline-identity.json"
PROTECTED = SESSION + "/reports/a09-compatibility-baseline.json"
PAINTER = "apps/standalone/InstrumentView.cpp"
FONT = "apps/standalone/FontData.h"
FIXTURE = "apps/standalone/native_tests/test_standalone_header_material.cpp"
EXECUTABLE = "test_standalone_header_material"
BEFORE_PAINTER_SHA = "10865a6bad39bc0a254b8b3f4cf6b013bef48770a2b39c7e9f9a70f438d56366"
BASE_COMMIT = "6047723b595259de355c74342e48a8ae2ee1e228"
# PINNED[FIXTURE] remains the historical baseline. Current source must pass
# fixture_portability_transition; replacing a hash alone cannot admit an edit.
PORTABLE_FIXTURE_SHA = "1e5ced9f7644506863a514ee06b452601b3861ab2e581c6dff7e67c5cf7c275d"
CAST_FIXTURE_SHA = "96149cf482ad0a57512257a519b89198113f21b06c33b073b2861e13349d1809"
HELPER_ELSE_FIXTURE_SHA = "86acc068fa23826fb39f245f9327e919c076660f315bed5d57f63e586d6d3ac6"
INDEXED_ARRAY_FIXTURE_SHA = "8c8226b04931569cdbff78cddcfd6241fd334c1f15c764a04d016d958bc912aa"
BASELINE_COMPARATOR_SHA = "ff3e9015364c1a773bfb8ea90a0138eb9df5f2b03075e49dc8ea4457b76b5760"
PINNED = {
    CONTRACT: "07d64498a14431b64742d79e7fbe4d2ac71d77fe51d09f71c638f52594fd9282",
    ADMISSION: "c2e7a216a11d7065262702aaee8f7ec766171a4571cc51c2f9bf7edd021cd6e5",
    OBSERVATIONS: "8f591b6d80bb6934a955ac2eb4b0005b78c4c164434510bc7125b4c511856c7b",
    PROTECTED: "7cdfb46aea8c3682b688ef965840af5ff76f46275add323f4aac783fcdbbf2c6",
    FONT: "f1a3121a2707a03a3b2e025c399e68c553ce9498f4b002ec13b18f512e334802",
    FIXTURE: "a6b65d06067d8941e44ef8680f309433a3c82ce1d6bd54d6f3f5bf8d4bde82d2",
    "tools/compare_heading_typography.py": "e809a3e052efa5916e1ce6f20b1ef0a5560fc50b423f0759ba705d0650aaf886",
    "tools/compare_footage_typography.py": "768ad4a5c022038c75414527961d5437bc3990a11d80772ce6fed6fc5a1534a1",
    "tools/compare_title_typography.py": "a3e6d7f6dcb6b11b1281b69c866e2b044f76eacffc05b5375b4936c77650704c",
    **{key: value for key, value in typography.PINNED.items() if key not in
       ("tools/compare_heading_typography.py", "tools/compare_footage_typography.py")},
}
SDL_EXTRA = {
    "src/video/SDL_surface.c": "e2c324858b829a0afebc0ce04c983178347c24adb08d9738118c06fc39f3bbf5",
    "src/video/SDL_stretch.c": "235f4c58830d1d7f0efc5a6b13f22838eccf04aa1c653f37534af2c6c7356a4b",
}
MAX_PIXELS = 3900 * 2200
MAX_FRAME = transport.MAX_HEADER + 1 + 4 * MAX_PIXELS
MAX_DIAGNOSTICS = 4096
MAX_TOTAL_SECONDS = 1800
PRIMARY = ("L", "TL", "TM", "TR", "CLT", "CL", "CR", "RT", "RU", "RF",
           "CM1", "CM2", "CM3", "BL", "BC1", "BC2", "BC3", "BR")
PATCHES = dict(zip(PRIMARY, ((86, 24, 8, 64), (112, 20, 96, 20), (264, 20, 96, 20),
    (420, 20, 80, 20), (530, 20, 48, 16), (530, 50, 48, 44), (1100, 50, 96, 44),
    (1130, 18, 64, 16), (1240, 18, 72, 16), (1440, 16, 128, 6), (620, 60, 96, 6),
    (780, 60, 96, 6), (940, 60, 96, 6), (534, 96, 60, 8), (650, 92, 96, 10),
    (790, 92, 96, 10), (930, 92, 96, 10), (1100, 96, 96, 8)), strict=True))
WITNESSES = {"CT1": (620, 15, 96, 4), "CT2": (780, 15, 96, 4), "CT3": (940, 15, 96, 4),
             "LE": (86, 16, 8, 8), "RE": (1580, 16, 8, 8),
             "BR2": (1330, 100, 96, 6), "RBR": (1480, 100, 96, 6)}
EXCLUSIONS = ((96, 44, 516, 100), (590, 14, 1082, 60), (638, 66, 1038, 88),
              (524, 37, 583, 44), (1090, 37, 1208, 44), (1322, 20, 1415, 41),
              (1223, 39, 1531, 100), (1533, 39, 1599, 100), (1312, 25, 1594, 89),
              (1228, 78, 1298, 102))
HEADER_CONTROLS = [
    {"id": [20, 0, 0, i], "rect": (100 + 140 * i, 50, 130, 46), "label": label}
    for i, label in enumerate(("PLAY", "ROTARY", "SERVICE"))]
HEADER_CONTROLS += [
    {"id": [kind, 0, 0, 0], "rect": (1312 + 97 * (i % 3), 25 + 36 * (i // 3), 88, 28), "label": label}
    for i, (kind, label) in enumerate(((11, "SAVE"), (12, "LOAD"), (14, "HELP"),
                                     (13, "AUDIO"), (18, "MIDI"), (15, "PANIC")))]
HEADER_CONTROLS += [{"id": [21, 0, 0, 0], "rect": (1228, 78, 70, 24), "label": "FLAT"}]


def header_geometry(width, height):
    sx, sy = f32(width / 1672), f32(height / 941)
    bx, by = f32(72 * sx), f32(10 * sy)
    bw, bh = f32(f32(1600 * sx) - bx), f32(f32(112 * sy) - by)
    dx, dy = f32(4 * sx), f32(4 * sy)
    inset = [f32(bx + dx), f32(by + dy), max(0., f32(bw - f32(2 * dx))), max(0., f32(bh - f32(2 * dy)))]
    return (sx, sy), (bx, by, bw, bh), inset


def gradient_box(rect, scale):
    x, y, w, h = rect
    rx, ry = scale
    return [math.ceil(x * rx - .5), math.ceil(y * ry - .5),
            math.ceil((x + w) * rx - .5), math.ceil((y + h) * ry - .5)]


def fill_box(rect, scale):
    x, y, w, h = [math.trunc(f32(v * s)) for v, s in zip(rect, (*scale, *scale), strict=True)]
    return [x, y, x + max(w, 1), y + max(h, 1)]


def translate(box, origin):
    return [box[0] + origin[0], box[1] + origin[1], box[2] + origin[0], box[3] + origin[1]]


def mix32(z):
    z ^= z >> 16
    z = (z * 0x7FEB352D) & 0xffffffff
    z ^= z >> 15
    z = (z * 0x846CA68B) & 0xffffffff
    return z ^ (z >> 16)


def new_grain_origins():
    result = [(78 + mix32(0xB3A02211 ^ k) % 1516,
               16 + mix32(0xB3A02211 ^ (k + 1)) % 90)
              for i in range(8192) for k in (4 * i, 4 * i + 2)]
    require(len(result) == 16384 and len(set(result)) == 15438 and
            sha(b"".join(struct.pack("<HH", *p) for p in result)) ==
            "afd3639f16f5ae4ce396ea0a91d7bb4192cb0c7cc6139daa2ee0eb45a1f6a0e6",
            "independent H1 grain origins differ from admission")
    return result


def old_grain_rectangles(panel, composition):
    bx, by, bw, bh = panel
    sx, sy = composition
    rows = math.floor(max(0., f32(f32(bh / sy) - 16)))
    columns = math.floor(max(0., f32(f32(bw / sx) - 21)))
    step = max(4, math.ceil(math.sqrt(rows * columns / (3. * 2048))))
    def pairs(pitch):
        return ((rows - 2) // pitch + 1 if rows > 1 else 0) * ((columns - 2) // (pitch * 3) + 1 if columns > 1 else 0)
    while pairs(step) > 2048:
        step += 1
    result = []
    for row in range(1, rows, step):
        for column in range(1, columns, step * 3):
            if len(result) == 4096:
                break
            grain = (row * 1973 + column * 9277) & 0xffffffff
            x = f32(bx + f32(f32(f32(7 + column) + ((grain >> 5) % 3)) * sx))
            y = f32(by + f32(f32(7 + row) * sy))
            result.extend(([x, y, sx, sy], [f32(x + f32(3 * sx)), f32(y + sy), f32(2 * sx), sy]))
    require(len(result) <= 4096, "Original grain bound exceeded")
    return result


def case_matrix():
    result = []
    def add(width=1672, height=941, rx=1, ry=None, origin=(13, 17), level=4,
            route="B", pending_route="None", held=True, focus=(11, 0, 0, 0),
            workspace=0, presentation=0, blend=1, clip_kind="disabled", resource=False):
        rx, ry = f32(rx), f32(rx if ry is None else ry)
        _, _, inset = header_geometry(width, height)
        l, t, r, b = gradient_box(inset, (rx, ry))
        if resource:
            origin = (-l, -t)
        viewport = [*origin, math.ceil(f32(width * rx)), math.ceil(f32(height * ry))]
        output = [64, 64] if resource else [viewport[2] + 2 * abs(origin[0]), viewport[3] + 2 * abs(origin[1])]
        space, request = "physical", [0, 0, 0, 0]
        if clip_kind in ("left", "right", "top", "bottom"):
            if rx == ry == 1.5:
                space = "logical"
                request = list({"left": (74, 24, 4, 72), "right": (1594, 24, 4, 72),
                                "top": (90, 12, 1490, 4), "bottom": (90, 106, 1490, 4)}[clip_kind])
            else:
                request = list({"left": (l-2, t-2, 4, b-t+4), "right": (r-2, t-2, 4, b-t+4),
                                "top": (l-2, t-2, r-l+4, 4), "bottom": (l-2, b-2, r-l+4, 4)}[clip_kind])
        elif clip_kind == "disjoint":
            request = [r+4, t+4, 8, 8]
        elif clip_kind == "zero-physical":
            request = [l, t, 0, 0]
        elif clip_kind == "zero-logical":
            space, request = "logical", [76, 14, 0, 0]
        elif clip_kind == "top-left":
            request = [l-2, t-2, 8, 8]
        stored = [v * (s if space == "logical" else 1) for v, s in zip(request, (rx, ry, rx, ry), strict=True)]
        active = workspace == presentation == 0 and 1400 <= width <= 8192 and 820 <= height <= 8192
        result.append({"case": len(result), "logical_size": [width, height], "output_size": output,
            "scale": [rx, ry], "origin": list(origin), "viewport": viewport,
            "logical_viewport": [math.floor(v / s) for v, s in zip(viewport, (rx, ry, rx, ry), strict=True)],
            "clip": [math.floor(v) for v in stored],
            "logical_clip": [math.floor(v / s) for v, s in zip(stored, (rx, ry, rx, ry), strict=True)],
            "clip_kind": clip_kind, "clip_space": space, "clip_request": request,
            "clip_enabled": clip_kind != "disabled", "level": level, "route": route,
            "route_index": {"Cancel": 0, "D": 2, "A": 10, "B": 11}[route],
            "pending_route": pending_route, "pending_route_index": {"None": -1, "A": 10, "B": 11}[pending_route],
            "pending": pending_route != "None", "held": held,
            "edited_bank": "A" if route == "A" else "B", "focus": list(focus),
            "blend": blend, "workspace": workspace, "presentation": presentation,
            "active_reference": active, "eligible_h1": active and 0 < rx <= 2 and 0 < ry <= 2,
            "resource_crop": resource, "variant": "main"})
    for width, height in ((1672, 941), (1400, 820), (1920, 1080)):
        for i, scale in enumerate((1, 1.5, 2)):
            add(width, height, scale, level=4*i, route=("B", "A", "D")[i],
                pending_route="B" if i == 1 else "None", held=i != 0,
                focus=((11,0,0,0),(14,0,0,0),(21,0,0,0))[i])
    for width, height in ((1920, 820), (1400, 1080)):
        for scale in (.75, 1.25):
            add(width, height, scale, origin=(0, 0))
    add(1672.5, 941.25, 1.5, 2)
    add(rx=1.25, ry=.75, origin=(-13, -17))
    for edge in ("left", "right", "top", "bottom"):
        for scale in (1, 1.5, 2):
            add(rx=scale, clip_kind=edge)
    for clip_kind in ("disjoint", "zero-physical", "zero-logical"):
        add(clip_kind=clip_kind, blend=0 if clip_kind == "zero-logical" else 1)
    for scale in (1, 1.5, 2):
        add(8192, 8192, scale, resource=True)
    add(rx=2.01, ry=1, origin=(0,0))
    add(rx=1, ry=2.01, origin=(0,0))
    add(origin=(0,0), blend=0)
    for width, height in ((1399,820), (1400,819), (960,700), (1280,900)):
        add(width, height, 1.5)
    add(origin=(0,0), presentation=1)
    add(origin=(0,0), workspace=1)
    add(origin=(0,0), workspace=2)
    add(1400,820,origin=(0,0),presentation=1)
    add(origin=(0,0),level=0,route="Cancel",pending_route="A",held=False,focus=(14,0,0,0))
    add(origin=(0,0),level=8,route="D",pending_route="B",focus=(21,0,0,0))
    add(origin=(0,0),focus=(4,0,1,4))
    add(rx=1.25, origin=(-13,-17),clip_kind="top-left")
    require(len(result) == 48 and sum(c["clip_enabled"] for c in result) == 16, "literal H1 matrix changed")
    require(sum(math.prod(c["output_size"]) for c in result) == 131641918, "frozen output-pixel total changed")
    return result


def companion(spec):
    return {**spec, "clip": [0,0,0,0], "logical_clip": [0,0,0,0], "clip_enabled": False,
            "variant": "uncut"}


def visible_box(spec):
    box = intersect([0, 0, *spec["output_size"]], xywh(spec["viewport"]))
    if spec["clip_enabled"]:
        box = intersect(box, translate(xywh(spec["clip"]), spec["origin"]))
    return box


def declare_case(case, origins):
    spec = dict(case)
    width, height = spec["output_size"]
    require(0 < width <= 3900 and 0 < height <= 2200 and width * height <= MAX_PIXELS,
            "declared output exceeds the finite allocation bound")
    visible = visible_box(spec)
    composition, panel, inset = header_geometry(*spec["logical_size"])
    field = gradient_box(inset, spec["scale"])
    clipped_field = intersect(translate(field, spec["origin"]), visible)
    rectangles, extras, old_count = [], [], 0
    origin_hash = hashlib.sha256()
    if spec["eligible_h1"]:
        # The actual 257 boundaries form this exact old-gradient/new-field
        # interval. Verify the partition independently; retain no color model.
        edges = [math.ceil((inset[0] + inset[2] * j / 257.) * spec["scale"][0] - .5) for j in range(258)]
        require(edges[0] == field[0] and edges[-1] == field[2] and
                all(a <= b for a,b in zip(edges, edges[1:])), "field columns do not partition old gradient")
        if area(clipped_field):
            rectangles.append(clipped_field)
        old = old_grain_rectangles(panel, composition)
        old_count = len(old) // 2
        require(old_count == 1717, "frozen Original header grain-pair count differs")
        sx, sy = composition
        new = ([f32(cx * sx), f32(cy * sy), sx, sy] for cx, cy in origins)
        for rect in (*old, *new):
            intrinsic = fill_box(rect, spec["scale"])
            origin_hash.update(struct.pack("<4q", *intrinsic))
            cropped = intersect(translate(intrinsic, spec["origin"]), visible)
            if area(cropped) and not (clipped_field[0] <= cropped[0] and clipped_field[1] <= cropped[1]
                                     and cropped[2] <= clipped_field[2] and cropped[3] <= clipped_field[3]):
                extras.append(cropped)
        rectangles.extend(extras)
    spec.update({"visible_device_box": visible, "header_binary32": list(panel), "inset_binary32": inset,
                 "intrinsic_field_box": field, "allowed_rectangles": sorted(set(map(tuple, rectangles))),
                 "old_grain_pairs": old_count, "new_grain_marks": 16384 if spec["eligible_h1"] else 0,
                 "ordered_grain_device_boxes_sha256": origin_hash.hexdigest(),
                 "grain_rectangles_not_contained_by_field": len(extras), "compared_pixels": width*height})
    mask = common.allowance_mask(spec)
    spec.update({"allowed_pixels": mask.histogram()[255], "protected_pixels": width*height-mask.histogram()[255],
                 "allowance_sha256": sha(mask.tobytes()), "allowance_bounds": list(mask.getbbox()) if mask.getbbox() else None,
                 "whole_frame_equality_required": not mask.getbbox()})
    return spec


def plane(values, width, height, denominator):
    """Exact doubled centered moments, rational plane/SSE, one binary64 sqrt."""
    count = width * height
    require(len(values) == count and width > 1 and height > 1, "nonrectangular statistical patch")
    xs = [2*x-width+1 for x in range(width)]
    ys = [2*y-height+1 for y in range(height)]
    total, squares = sum(values), sum(v*v for v in values)
    xx, yy = height * sum(x*x for x in xs), width * sum(y*y for y in ys)
    xz = sum(xs[i % width] * v for i,v in enumerate(values))
    yz = sum(ys[i // width] * v for i,v in enumerate(values))
    mean = Fraction(total, count * denominator)
    dx, dy = Fraction(2*xz, xx*denominator), Fraction(2*yz, yy*denominator)
    sse = (Fraction(squares) - Fraction(total*total,count) - Fraction(xz*xz,xx) - Fraction(yz*yz,yy)) / denominator**2
    require(sse >= 0, "negative exact plane residual")
    return {"mean": float(mean), "mean_exact": str(mean), "dx_per_pixel": float(dx), "dx_per_pixel_exact": str(dx),
            "dy_per_pixel": float(dy), "dy_per_pixel_exact": str(dy), "residual_sse_exact": str(sse),
            "plane_residual_population_rms": math.sqrt(float(sse/count)),
            "sufficient_integer_statistics": {"count": count, "denominator": denominator, "sum": total,
              "sum_squared": squares, "sum_x2_squared": xx, "sum_y2_squared": yy,
              "sum_x2_times_value": xz, "sum_y2_times_value": yz}}


def measurements(image):
    require(image.size == (1672,941), "statistics require the literal canonical frame")
    image = image.convert("RGB")
    result = {}
    for name, rect in {**PATCHES, **WITNESSES}.items():
        patch = image.crop(xywh(rect))
        pixels = list(patch.get_flattened_data())
        planes = {channel: plane([p[i] for p in pixels], rect[2], rect[3], 1)
                  for i,channel in enumerate("RGB")}
        result[name] = {"box_xywh_half_open": list(rect), "decoded_patch_rgb_sha256": sha(patch.tobytes()),
                        "encoded_rgb": planes,
                        "encoded_y_prime": plane([2126*r+7152*g+722*b for r,g,b in pixels], rect[2], rect[3],10000)}
    return result


def grid_measurements(image):
    image = image.convert("RGB")
    pixels = image.load()
    result = []
    xx, yy = (84,340,596,852,1108,1364,1588), (18,40,60,84,104)
    for y0,y1 in zip(yy,yy[1:]):
        for x0,x1 in zip(xx,xx[1:]):
            sums, count = [0,0,0], 0
            for y in range(y0,y1):
                for x in range(x0,x1):
                    if any(a <= x < c and b <= y < d for a,b,c,d in EXCLUSIONS):
                        continue
                    count += 1
                    for i,value in enumerate(pixels[x,y]):
                        sums[i] += value
            result.append({"box_xyxy_half_open": [x0,y0,x1,y1], "count": count,
                           "rgb_sums": sums, "rgb_means_exact": [str(Fraction(v,count)) for v in sums] if count else None,
                           "Y_mean_exact": str(Fraction(2126*sums[0]+7152*sums[1]+722*sums[2],10000*count)) if count else None})
    require(len(result) == 24 and sum(row["count"] for row in result) == 48409, "frozen descriptive grid coverage differs")
    return result


def numerical_screens(reference, candidate):
    """Literal 90+8+3+2 criteria; no threshold is loaded from candidate data."""
    results = []
    def exact(name, value, limit):
        results.append({"name": name, "error_exact": str(value), "error": float(value),
                        "limit_exact": str(limit), "limit": float(limit), "passed": value <= limit})
    def approximate(name, value, limit):
        results.append({"name": name, "error": value, "error_hex": value.hex(),
                        "limit": limit, "limit_hex": limit.hex(), "passed": value <= limit})
    def mean(data, name, channel="Y"):
        record = data[name]["encoded_y_prime"] if channel == "Y" else data[name]["encoded_rgb"][channel]
        return Fraction(record["mean_exact"])
    def rms(data,name):
        record = data[name]["encoded_y_prime"]
        return math.sqrt(float(Fraction(record["residual_sse_exact"]) / math.prod(PATCHES[name][2:])))
    for name in PRIMARY:
        exact(name+":mean:Y", abs(mean(candidate,name)-mean(reference,name)), Fraction(3))
        for channel in "RGB":
            exact(name+":mean:"+channel, abs(mean(candidate,name,channel)-mean(reference,name,channel)), Fraction(4))
        approximate(name+":rms:Y", abs(rms(candidate,name)-rms(reference,name)), 1.2)
    for name,limit in (("L","3/40"),("TL","3/20"),("TM","3/20"),("TR","3/20"),
                       ("CL","3/40"),("CR","3/40"),("RT","1/5"),("RF","1/5")):
        exact(name+":vertical:Y", abs(Fraction(candidate[name]["encoded_y_prime"]["dy_per_pixel_exact"])-
               Fraction(reference[name]["encoded_y_prime"]["dy_per_pixel_exact"])), Fraction(limit))
    for a,b,limit in (("TM","TL","2"),("CR","CL","5/4"),("BR","BC2","7/4")):
        exact(a+"-minus-"+b, abs((mean(candidate,a)-mean(candidate,b))-(mean(reference,a)-mean(reference,b))), Fraction(limit))
    mean_mae = sum((abs(mean(candidate,n)-mean(reference,n)) for n in PRIMARY), Fraction(0))/18
    # Revision 1.1: fsum of the 18 individually rounded binary64 errors, then
    # exactly one division by 18.0. Ordinary sum is deliberately not used.
    rms_mae = math.fsum(abs(rms(candidate,n)-rms(reference,n)) for n in PRIMARY)/18.0
    exact("equal_patch_mean_Y_MAE",mean_mae,Fraction(846310429693,456192000000))
    approximate("equal_patch_RMS_Y_MAE",rms_mae,0.8336586440740232)
    require(len(results) == 103, "frozen numerical criterion count differs")
    return {"inequality_count": 103, "passed_count": sum(r["passed"] for r in results),
            "failed_count": sum(not r["passed"] for r in results), "passed": all(r["passed"] for r in results),
            "mean_error_exact": str(mean_mae), "rms_error": rms_mae, "rms_error_hex": rms_mae.hex(),
            "RMS_aggregation": "binary64 sqrt of exact SSE/N, binary64 abs, math.fsum in primary order, /18.0",
            "results": results}


def original_observations(root):
    report = read_json((root/OBSERVATIONS).read_bytes())
    require(report["primary_patch_order"] == list(PRIMARY) and
            report["primary_rectangles"] == {k:list(v) for k,v in PATCHES.items()} and
            report["descriptive_witness_rectangles"] == {k:list(v) for k,v in WITNESSES.items()},
            "original patch identities differ")
    require(PILLOW_VERSION == "13.0.0" and features.version_feature("libjpeg_turbo") == "3.2.0",
            "frozen original-image decoder must be Pillow13.0.0/libjpeg-turbo3.2.0")
    decoded = {}
    for name,item in report["images"].items():
        source = identity(root/item["path"])
        require(all(source[k] == item[k] for k in ("bytes","sha256")), "original image identity differs: "+name)
        image = Image.open(source["path"]).convert("RGB")
        require(list(image.size) == item["size"] and sha(image.tobytes()) == item["decoded_rgb_sha256"],
                "original decoded RGB identity differs: "+name)
        if name in ("reference","t2_canonical"):
            decoded[name] = image
    measured = {name: measurements(image) for name,image in decoded.items()}
    for name,data in measured.items():
        for patch,item in data.items():
            require(common.typed_equal(item,report["measurements"][patch][name]),
                    "original exact plane/RMS/pixel observations differ: "+name+"/"+patch)
    require([row["box"] for row in report["whole_header_grid"]["exclusions_xyxy"]] == list(map(list,EXCLUSIONS)),
            "descriptive grid exclusions changed")
    grids = {name:grid_measurements(image) for name,image in decoded.items()}
    for name,grid in grids.items():
        for row,original in zip(grid,report["whole_header_grid"]["cells"],strict=True):
            require(row == {"box_xyxy_half_open":original["box_xyxy_half_open"],"count":original["count"],**original[name]},
                    "original descriptive grid differs")
    before = numerical_screens(measured["reference"],measured["t2_canonical"])
    require((before["passed_count"],before["failed_count"],before["mean_error_exact"],before["rms_error"]) ==
            (44,59,"846310429693/228096000000",1.6673172881480465), "original 44/59 screens or exact aggregates changed")
    expected = report["prospective_criteria"]["before_gates"]
    require(len(expected) == 103, "missing original thresholds")
    for observed,old in zip(before["results"],expected,strict=True):
        require(observed["passed"] is old["t2_pass"], "original numerical outcome differs")
        if "limit_exact" in old:
            require(observed["limit_exact"] == old["limit_exact"] and observed["error_exact"] == old["t2_error_exact"],
                    "original exact criterion or error differs")
        else:
            require(observed["limit"] == old["limit"] and observed["error"] == old["t2_error"],
                    "original floating criterion or error differs")
    return {"scalar_planes_reproduced":200,"patches":measured,"whole_header_grid":grids,
            "original_t2_screens":before,"original_report_sha256":PINNED[OBSERVATIONS]}, measured["reference"]


def font_atlases(path):
    text = Path(path).read_text()
    require(identity(path)["sha256"] == PINNED[FONT], "font identity changed")
    result = {}
    for name,pixel_height,ascent in (("Sans",32,30),("Serif",40,38)):
        block = text.split("k"+name+"Glyphs{{",1)[1].split("}};",1)[0]
        entries = re.findall(r"\{(-?\d+(?:,\s*-?\d+){6})\},\s*// ASCII (\d+)",block)
        glyphs = {chr(int(code)):tuple(map(int,fields.split(","))) for fields,code in entries}
        require(len(glyphs) == 95, "complete raw font glyph inventory missing")
        encoded = [int(v) for v in re.findall(r"\d+",text.split("k"+name+"AlphaRle{{",1)[1].split("}};",1)[0])]
        require(len(encoded)%2 == 0, "malformed font coverage RLE")
        data = bytearray()
        for count,value in zip(encoded[::2],encoded[1::2],strict=True):
            require(0<count<=255 and 0<=value<=255 and len(data)+count<=512*256,"unbounded font RLE")
            data.extend(bytes([value])*count)
        require(len(data)==512*256,"incomplete raw atlas coverage")
        result[name] = {"glyphs":glyphs,"alpha":bytes(data),"pixel_height":pixel_height,"ascent":ascent,
                        "alpha_sha256":sha(data)}
    return result


def text_width(text,size,atlas):
    scale = f32(size/atlas["pixel_height"])
    width = 0.
    for char in text:
        width = f32(width+f32(f32(atlas["glyphs"][char][6]*scale)/64))
    return width


def text_copies(run,atlas):
    scale = f32(run["size"]/atlas["pixel_height"])
    baseline = f32(run["top"]+f32(atlas["ascent"]*scale))
    pen, result = run["x"], []
    for index,char in enumerate(run["text"]):
        ax,ay,w,h,bx,by,advance = atlas["glyphs"][char]
        if w and h:
            px,py = (2 if f32(w*scale)<1 else 0),(2 if f32(h*scale)<1 else 0)
            result.append({"index":index,"character":char,"atlas_xywh":[ax-px,ay-py,w+2*px,h+2*py],
                "target_binary32":[f32(pen+f32((bx-px)*scale)),f32(baseline+f32((by-py)*scale)),
                                   f32((w+2*px)*scale),f32((h+2*py)*scale)]})
        pen = f32(pen+f32(f32(advance*scale)/64))
    return result


def header_text_runs(spec,atlases):
    width,height = spec["logical_size"]
    title = typography.title_runs(width,height,atlases["Serif"]["glyphs"])
    runs = [{**r,"face":"Serif","group":"title"} for r in title["after"]]
    sx,sy,f = title["scale_binary32"]
    left,right = title["title_interval_binary32"]
    middle,flat_left = f32(836*sx),f32(1228*sx)
    half = max(0., min(f32(middle-left),f32(min(right,f32(flat_left-f32(10*sx)))-middle)))
    span = min(f32(374*sx),f32(2*half))
    size = f32(17*f)
    text = "NOMINAL DRY ORGAN"
    natural = text_width(text,size,atlases["Sans"])
    gaps = len(text)-1
    tracking = max(0.,f32(f32(span-natural)/gaps))
    if natural > span:
        size = f32(size*f32(span/natural))
        natural = text_width(text,size,atlases["Sans"])
    cursor = f32(middle-f32(f32(natural+f32(gaps*tracking))/2))
    for i,char in enumerate(text):
        runs.append({"purpose":"caption-"+str(i),"text":char,"x":cursor,"top":f32(67.5*sy),
                     "size":size,"rgba":[214,182,124,255],"face":"Sans","group":"caption"})
        cursor = f32(cursor+f32(text_width(char,size,atlases["Sans"])+tracking))
    for run in runs:
        run["copies"] = text_copies(run,atlases[run["face"]])
    require(sum(len(r["copies"]) for r in runs if r["group"]=="title")==70 and
            sum(len(r["copies"]) for r in runs if r["group"]=="caption")==15,
            "literal T3/title-caption glyph-copy inventory differs")
    return runs


def round_away(value):
    return math.floor(value+.5) if value>=0 else math.ceil(value-.5)


def scaler_axis(source,destination):
    step = (source<<16)//destination
    start = (step+1)//2-32768
    result = []
    for i in range(destination):
        fp = start+i*step
        if fp<0:
            result.append((0,0,0))
        elif fp>>16 > source-2:
            result.append((source-1,source-1,0))
        else:
            result.append((fp>>16,(fp>>16)+1,(fp>>9)&127))
    return result


def copy_alpha(operation,atlas,spec):
    """Independent SDL software linear COPY including clip-induced resampling.

    SDL_surface.c rounds clipped source and destination rectangles separately;
    SDL_stretch.c uses a 16-bit step and 7-bit bilinear weights, vertical first.
    A target crossing the physical output is first scaled to an intermediate
    surface (SDL_render_sw.c), so that path clips after its full resampling.
    """
    destination = typography.copy_destination(operation["target_binary32"],spec["scale"],spec["origin"])
    clipped = intersect(destination,spec["visible_device_box"])
    if not area(clipped):
        return destination, clipped, None
    ax,ay,sw,sh = operation["atlas_xywh"]
    dx,dy,dr,db = destination
    dw,dh = dr-dx,db-dy
    require(0<dw<=MAX_PIXELS and 0<dh<=2200,"invalid glyph destination")
    full_target = [0,0,*spec["output_size"]]
    intermediate = destination != intersect(destination,full_target)
    unscaled = sw==dw and sh==dh
    if unscaled:
        ax += clipped[0]-dx
        ay += clipped[1]-dy
        sw,sh = clipped[2]-clipped[0],clipped[3]-clipped[1]
        sample_destination = clipped
    elif intermediate:
        sample_destination = destination
    else:
        rw,rh = dw/sw,dh/sh
        source_x0,source_y0 = ax+(clipped[0]-dx)/rw,ay+(clipped[1]-dy)/rh
        source_x1,source_y1 = ax+sw-(dr-clipped[2])/rw,ay+sh-(db-clipped[3])/rh
        ax,ay,sw,sh = round_away(source_x0),round_away(source_y0),round_away(source_x1-source_x0),round_away(source_y1-source_y0)
        sample_destination = clipped
    dw,dh = sample_destination[2]-sample_destination[0],sample_destination[3]-sample_destination[1]
    if sw<=0 or sh<=0 or dw<=0 or dh<=0:
        return destination,clipped,None
    require(0<=ax and 0<=ay and ax+sw<=512 and ay+sh<=256,"clipped source atlas bounds differ")
    alpha = atlas["alpha"]
    out = bytearray(dw*dh)
    if unscaled:
        for y in range(dh):
            out[y*dw:(y+1)*dw] = alpha[(ay+y)*512+ax:(ay+y)*512+ax+dw]
    else:
        xx,yy = scaler_axis(sw,dw),scaler_axis(sh,dh)
        for y,(y0,y1,fy) in enumerate(yy):
            for x,(x0,x1,fx) in enumerate(xx):
                a = (alpha[(ay+y0)*512+ax+x0]*(128-fy)+alpha[(ay+y1)*512+ax+x0]*fy)>>7
                b = (alpha[(ay+y0)*512+ax+x1]*(128-fy)+alpha[(ay+y1)*512+ax+x1]*fy)>>7
                out[y*dw+x] = (a*(128-fx)+b*fx)>>7
    image = Image.frombytes("L",(dw,dh),bytes(out))
    if intermediate and not unscaled:
        image = image.crop([clipped[0]-dx,clipped[1]-dy,clipped[2]-dx,clipped[3]-dy])
    return destination,clipped,image


def blank_mask(spec):
    return Image.new("L",tuple(spec["output_size"]),0)


def paint_mask_rectangle(mask,box):
    if area(box):
        ImageDraw.Draw(mask).rectangle((box[0],box[1],box[2]-1,box[3]-1),fill=255)


def merge_local_mask(mask,local,box):
    if local is not None and area(box):
        mask.paste(ImageChops.lighter(mask.crop(box),local),box)


def mask_facts(mask):
    return {"pixels":mask.histogram()[255],"sha256":sha(mask.tobytes()),
            "bounds":list(mask.getbbox()) if mask.getbbox() else None}


def opaque_control_surface(control,spec):
    sx,sy = header_geometry(*spec["logical_size"])[0]
    x,y,w,h = common.mapped(*spec["logical_size"],control["rect"])
    selected = control["id"] == [20,0,0,0]
    recess = sy if selected else 0.
    cx,cy = f32(x+f32(4*sx)), f32(f32(y+f32(3*sy))+recess)
    cw,ch = f32(w-f32(10*sx)), f32(f32(h-f32(8*sy))-recess)
    front = f32(min(5.,max(3.,f32(f32(h/sy)*f32(.12))))*sy)
    surface = [f32(cx+sx),f32(cy+sy),f32(cw-f32(2*sx)),f32(f32(ch-front)-sy)]
    box = translate(gradient_box(surface,spec["scale"]),spec["origin"])
    # Erode the source primitive's opaque device coverage by exactly one pixel
    # before clipping. No candidate pixels or child bounding-box padding.
    eroded = [box[0]+1,box[1]+1,max(box[0]+1,box[2]-1),max(box[1]+1,box[3]-1)]
    return surface,intersect(eroded,spec["visible_device_box"])


def focus_boxes(control,spec):
    sx,sy = header_geometry(*spec["logical_size"])[0]
    x,y,w,h = common.mapped(*spec["logical_size"],control["rect"])
    tx,ty = min(f32(2*sx),f32(w/2)),min(f32(2*sy),f32(h/2))
    rects = ([x,y,w,ty],[x,f32(f32(y+h)-ty),w,ty],
             [x,f32(y+ty),tx,f32(h-f32(2*ty))],
             [f32(f32(x+w)-tx),f32(y+ty),tx,f32(h-f32(2*ty))])
    return [intersect(translate(fill_box(rect,spec["scale"]),spec["origin"]),spec["visible_device_box"]) for rect in rects]


def child_oracles(spec,atlases):
    core,support,focus,header = (blank_mask(spec) for _ in range(4))
    controls, rules, glyphs, final_cores = [],[],[],[]
    if not spec["active_reference"]:
        return {"core":core,"support":support,"focus":focus,"header":header,
                "controls":controls,"rules":rules,"glyphs":glyphs,"final_cores":final_cores}
    paint_mask_rectangle(header,intersect(translate(gradient_box(spec["header_binary32"],spec["scale"]),spec["origin"]),spec["visible_device_box"]))
    for control in HEADER_CONTROLS:
        surface,box = opaque_control_surface(control,spec)
        controls.append({"id":control["id"],"label":control["label"],"surface_binary32":surface,"probe_box":box,"pixels":area(box)})
        if control["id"]==spec["focus"]:
            for border in focus_boxes(control,spec):
                paint_mask_rectangle(focus,border)
    for rect in ((528,40,50,1),(1094,40,108,1)):
        box = intersect(translate(fill_box(common.mapped(*spec["logical_size"],rect),spec["scale"]),spec["origin"]),spec["visible_device_box"])
        rules.append({"canonical_rect":list(rect),"box":box,"pixels":area(box),"rgba":[91,78,59,255]})
    for run in header_text_runs(spec,atlases):
        for operation in run["copies"]:
            destination,box,alpha = copy_alpha(operation,atlases[run["face"]],spec)
            paint_mask_rectangle(support,intersect(destination,spec["visible_device_box"]))
            opaque = alpha.point(lambda v:255 if v==255 else 0) if alpha is not None else None
            merge_local_mask(core,opaque,box)
            if run["purpose"]=="main-brass-face" or run["group"]=="caption":
                strong = alpha.point(lambda v:255 if v>=192 else 0) if alpha is not None else None
                glyphs.append({"group":run["group"],"purpose":run["purpose"],"character":operation["character"],
                    "index":operation["index"],"destination":destination,"visible_box":box,
                    "complete":destination==box,"strong_pixels":strong.histogram()[255] if strong else 0,
                    "opaque_pixels":opaque.histogram()[255] if opaque else 0,
                    "strong_sha256":sha(strong.tobytes()) if strong else None,"strong_mask":strong})
                final_cores.append((box,opaque,run["rgba"]))
    return {"core":core,"support":support,"focus":focus,"header":header,
            "controls":controls,"rules":rules,"glyphs":glyphs,"final_cores":final_cores}


def child_declaration(spec,atlases):
    oracle = child_oracles(spec,atlases)
    return {"applicable":spec["active_reference"],"opaque_core":mask_facts(oracle["core"]),
            "glyph_copy_support":mask_facts(oracle["support"]),"focus":mask_facts(oracle["focus"]),
            "controls":oracle["controls"],"rules":oracle["rules"],
            "glyphs":[{k:v for k,v in g.items() if k!="strong_mask"} for g in oracle["glyphs"]]}


def different_under_mask(before,after,mask):
    rgba = ImageChops.difference(before,after)
    maximum = rgba.getchannel(0)
    for i in (1,2,3):
        maximum = ImageChops.lighter(maximum,rgba.getchannel(i))
    differences = ImageChops.darker(maximum.point(lambda v:255 if v else 0),mask)
    return differences.histogram()[255]


def literal_mask_errors(image,box,mask,color):
    if mask is None or not mask.getbbox():
        return 0
    return different_under_mask(image.crop(box),Image.new("RGBA",mask.size,tuple(color)),mask)


def is_warm(pixel):
    r,g,b,_ = pixel
    # Retain the existing T3 RGB warm-ink predicate. NONE-blend Original grain
    # can leave nonopaque background alpha under an antialiased glyph edge;
    # opaque-core RGBA equality is checked separately and without relaxation.
    return r>=130 and g>=105 and r>=g and 10*b<=9*r


def child_checks(spec,before,after,atlases):
    if not spec["active_reference"]:
        return {"applicable":False,"passed":True,"reason":"inactive layout requires exact whole frame"}
    oracle = child_oracles(spec,atlases)
    expected = spec["children"]
    require(mask_facts(oracle["core"])==expected["opaque_core"] and
            mask_facts(oracle["focus"])==expected["focus"] and
            mask_facts(oracle["support"])==expected["glyph_copy_support"],"frozen independent child masks changed")
    controls=[]
    full = not spec["clip_enabled"] and not spec["resource_crop"]
    for control in oracle["controls"]:
        box = control["probe_box"]
        nonempty = not full or control["pixels"]>0
        exact = not area(box) or before.crop(box).tobytes()==after.crop(box).tobytes()
        controls.append({**control,"nonempty_required":full,"nonempty_passed":nonempty,"rgba_equal":exact,
                         "passed":nonempty and exact})
    rules=[]
    for rule in oracle["rules"]:
        box=rule["box"]
        exact=not area(box) or (before.crop(box).getextrema()==after.crop(box).getextrema()==
                              tuple((v,v) for v in rule["rgba"]))
        rules.append({**rule,"nonempty_required":full,"passed":exact and (not full or area(box)>0)})
    core_differences=different_under_mask(before,after,oracle["core"])
    literal_errors={phase:sum(literal_mask_errors(image,box,mask,color) for box,mask,color in oracle["final_cores"])
                    for phase,image in (("before",before),("after",after))}
    glyphs=[]
    for glyph in oracle["glyphs"]:
        box,mask=glyph["visible_box"],glyph["strong_mask"]
        missing={}
        for phase,image in (("before",before),("after",after)):
            missing[phase]=0
            if mask is not None:
                pixels=image.crop(box).get_flattened_data()
                missing[phase]=sum(value==255 and not is_warm(pixel) for value,pixel in zip(mask.get_flattened_data(),pixels,strict=True))
        require_nonempty=full or glyph["complete"]
        # Invisible/cut glyphs are explicitly uncredited. Complete glyphs must
        # have independently predicted strong coverage; every such pixel is checked.
        passed=not any(missing.values()) and (not require_nonempty or glyph["strong_pixels"]>0)
        glyphs.append({**{k:v for k,v in glyph.items() if k!="strong_mask"},"missing_strong_pixels":missing,
                       "nonempty_required":require_nonempty,"passed":passed})
    focus={}
    for phase,image in (("before",before),("after",after)):
        actual=ImageChops.darker(common.cyan_mask(image),oracle["header"])
        focus[phase]={**mask_facts(actual),"different_positions":ImageChops.difference(actual,oracle["focus"]).histogram()[255]}
    focus_pass=all(item["different_positions"]==0 for item in focus.values())
    full_coverage=not full or (len(controls)==10 and len(rules)==2 and len(glyphs)==29 and
                             all(g["strong_pixels"]>0 for g in glyphs) and expected["opaque_core"]["pixels"]>0)
    return {"applicable":True,"controls":controls,"rules":rules,"glyphs":glyphs,
            "opaque_glyph_core":{**expected["opaque_core"],"different_pixels":core_differences,
                                  "literal_final_ink_mismatches":literal_errors},
            "cyan_focus":{**focus,"expected":expected["focus"],"passed":focus_pass},
            "complete_visible_coverage_required":full,"complete_visible_coverage_passed":full_coverage,
            "passed":full_coverage and core_differences==0 and not any(literal_errors.values()) and focus_pass and
                     all(c["passed"] for c in [*controls,*rules,*glyphs])}


def canonical_typography(spec,image):
    applicable=(spec["active_reference"] and spec["logical_size"]==[1672,941] and spec["scale"]==[1,1]
                and not spec["clip_enabled"] and not spec["resource_crop"])
    if not applicable:
        return {"applicable":False,"passed":True,"scope":"Complete original geometry matrix is required through native material acceptance."}
    observations=typography.encoded_y(image,origin=spec["origin"])
    count=observations[1]["pixels"]
    original_error=5415-3863
    count_pass=4500<=count<=6000 and 5*abs(count-5415)<=3*original_error
    warm=typography.warm_geometry({**spec,"suite":"clips","case":46,"viewport":spec["viewport"]},image)
    # Every original T3 canonical warm-ROI cohort uses BLEND: typography0..17,
    # percussion0..15 and clips46. Original panel grain under NONE directly
    # writes bright RGB with low alpha, so this RGB-only whole-ROI predicate
    # also counts material marks. Retain its raw observations without extending
    # the old BLEND geometry gate to NONE. The density gate above and every
    # independent glyph/core/control/rule/focus check still apply to NONE.
    warm_required=spec["blend"]==1
    return {"applicable":True,"encoded_Y_counts":observations,"primary_band":[4500,6000],
            "minimum_original_count_error_reduction":.4,"count_passed":count_pass,"warm_geometry":warm,
            "warm_geometry_required":warm_required,
            "warm_geometry_scope":"Original T3 absolute warm-ROI geometry gates use BLEND; NONE raw observations are retained and are not a geometry acceptance gate.",
            "passed":count_pass and (not warm_required or warm["passed"])}


def caller_clip_checks(spec,image):
    background=(18,21,20,255) if spec["presentation"]==1 else (85,54,36,255)
    width,height=spec["output_size"]
    l,t,r,b=spec["visible_device_box"]
    boxes=([(0,0,width,height)] if not area(spec["visible_device_box"]) else
           [(0,0,width,t),(0,b,width,height),(0,t,l,b),(r,t,width,b)])
    ok=all(image.crop(box).getextrema()==tuple((v,v) for v in background) for box in boxes if area(box))
    return {"protected_caller_pixels":width*height-area(spec["visible_device_box"]),"clear_rgba":list(background),"passed":ok}


def quiet_companion_check(spec,clipped,uncut,atlases):
    """Check material restriction exactly; never treat clipped glyphs as crops.

    Independent glyph-copy destinations and all ten live-control rectangles
    are excluded from this quiet-material check. Their cores/opaque surfaces
    and exact focus are separately mandatory. No candidate classification.
    """
    mask=common.allowance_mask(spec)
    oracle=child_oracles(spec,atlases)
    mask=ImageChops.subtract(mask,oracle["support"])
    for control in HEADER_CONTROLS:
        box=intersect(translate(gradient_box(common.mapped(*spec["logical_size"],control["rect"]),spec["scale"]),spec["origin"]),spec["visible_device_box"])
        if area(box):
            ImageDraw.Draw(mask).rectangle((box[0],box[1],box[2]-1,box[3]-1),fill=0)
    different=different_under_mask(clipped,uncut,mask)
    return {**mask_facts(mask),"different_pixels":different,"passed":different==0,
            "no_visible_material":not bool(mask.getbbox())}


SCENARIO_KEYS = ("case logical_size output_size scale origin clip_kind clip_space clip_request "
                 "level route route_index pending pending_route pending_route_index held edited_bank "
                 "focus blend workspace presentation active_reference eligible_h1 resource_crop").split()
VIEW_KEYS = set(("controls applied edited_banks focus roving_manual_keys roving_pedal_key keyboard_target "
                "manual_base_midi pedal_octave controls_pending controls_dirty text_entry_active pointer_captured "
                "input_recovery last_submit_status workspace presentation workspace_focus").split())
LAYOUT_KEYS = set(("width height show_cabinet bank_controls_in_cheeks sidebar_pedals header registration_panels "
                  "performance_panel keyboard_toolbar manual_panels pedal_panel footer cabinet_panel cabinet_art "
                  "manual_rail_panels control_count controls manual_keys pedal_keys preset_key_panels workspace "
                  "presentation workspace_panel").split())
COUNTERS = set(("resolved_sequence last_applied_sequence recovery_count queue_overflows rejected_commands "
                "discarded_commands fault_flags last_core_status").split())
SESSION_KEYS = COUNTERS | set("controls held_keys held_pedals frame_clock sample_rate peak prepared running publication_revision".split())
TRANSFORM_KEYS = set("scale viewport clip logical_viewport logical_clip clip_enabled blend draw_color".split())
FIXED_INFO = {"audio_running":True,"sample_rate":48000,"buffer_frames":512,"audio_driver":"fixed-software-fixture",
    "device_name":"fixed copied state","status_message":"Frozen header material qualification","clipped_samples":0,
    "overlay":0,"audio_choices":[],"selected_device":0,"selected_sample_rate":48000,"selected_buffer_frames":512,
    "midi_available":False,"midi_open":False,"midi_backend":"","midi_port":"","midi_status":"","midi_choices":[],
    "selected_midi_port":0,"selected_midi_channels":[1,2,3],"selected_midi_expression":[0,127,False],
    "active_midi_expression":[0,127,False],"midi_expression_active":False,"midi_reconnect_pending":False,
    "midi_messages":0,"inspection":None}


def scenario(spec):
    result={key:spec[key] for key in SCENARIO_KEYS}
    result.update({"requested_clip_enabled":spec["clip_kind"]!="disabled","lower_route":"B","lower_edited_bank":"B"})
    return result


def scenario_errors(spec,record):
    errors=[]
    for key,value in scenario(spec).items():
        equal=(common.float_vector_equal(record.get(key),value) if key in ("logical_size","scale") else
               common.typed_equal(record.get(key),value))
        if not equal:
            errors.append("scenario "+key+" differs")
    return errors


def expected_controls(spec,desired=False):
    route=spec["route"]
    upper=0 if route=="A" else 1
    result={"drawbars":[[[spec["level"]]*9 for _ in range(2)] for _ in range(2)],
            "selected_banks":[upper,1],"route_enabled":[int(route!="Cancel"),1],
            "fixed_registrations":[2 if route=="D" else 0,0],"expression":.625,
            "pedal_drawbars":[3,7],"percussion":[True,0,0,0]}
    if desired and spec["pending"]:
        result["selected_banks"][0]=0 if spec["pending_route"]=="A" else 1
        result["route_enabled"][0]=1
        result["fixed_registrations"][0]=0
    return result


def validate_model(spec,model,session,hit):
    require(type(model) is dict and set(model)=={"view","layout"},"missing complete model sections")
    view,layout=model["view"],model["layout"]
    require(set(view)==VIEW_KEYS and set(layout)==LAYOUT_KEYS,"missing complete public view/layout members")
    require(common.typed_equal(view["controls"],expected_controls(spec,True)) and
            common.typed_equal(session["controls"],expected_controls(spec)),"complete desired/applied controls differ")
    require(set(session)==SESSION_KEYS and common.typed_equal(view["applied"],session),"complete copied session differs")
    require(all(type(session[k]) is int and session[k]==0 for k in COUNTERS),"session counters changed")
    require([session[k] for k in ("frame_clock","sample_rate","peak","publication_revision")]==[38400,48000,.125,4]
            and session["prepared"] is session["running"] is True,"copied clock/rate/peak/revision/prepared/running differ")
    held=[[False]*61 for _ in range(2)]
    pedals=[False]*25
    held[0][24]=held[1][36]=pedals[12]=spec["held"]
    require(common.typed_equal(session["held_keys"],held) and common.typed_equal(session["held_pedals"],pedals),"held-note snapshot differs")
    require(view["edited_banks"]==[0 if spec["edited_bank"]=="A" else 1,1] and
            common.typed_equal(view["focus"],spec["focus"]) and view["controls_pending"] is spec["pending"],
            "focus/edited banks/pending differs")
    require(view["workspace"]==layout["workspace"]==spec["workspace"] and
            view["presentation"]==layout["presentation"]==spec["presentation"] and
            common.float_vector_equal([layout["width"],layout["height"]],spec["logical_size"]),"layout selection/size differs")
    require(type(layout["controls"]) is list and len(layout["controls"])==68,"complete 68 control slots missing")
    for control in layout["controls"]:
        require(set(control)=={"id","bounds","label_bounds","value_bounds","track"},"incomplete control geometry")
        require(type(control["id"]) is list and len(control["id"])==4,"malformed control identity")
        for key in ("bounds","label_bounds","value_bounds","track"):
            require(type(control[key]) is list and len(control[key])==4 and all(type(v) in (int,float) and math.isfinite(v) for v in control[key]),"malformed control rectangle")
    require(list(map(len,layout["manual_keys"]))==[61,61] and len(layout["pedal_keys"])==25,"complete 147 key slots missing")
    for keys in [*layout["manual_keys"],layout["pedal_keys"]]:
        for key in keys:
            require(set(key)=={"note","bounds","accidental","hit","top","front"},"incomplete key geometry")
            for name in ("hit","top","front"):
                require(type(key[name]) is list and len(key[name])==4 and all(len(p)==2 for p in key[name]),"incomplete key quad")
    if spec["workspace"]==0:
        require(layout["control_count"]==68 and sum(c["id"][0]==19 for c in layout["controls"])==24,
                "68 Play controls / 24 presets changed")
    if spec["active_reference"]:
        require(common.float_vector_equal(layout["header"],spec["header_binary32"]),"independent mapped header differs")
        controls={tuple(c["id"]):c for c in layout["controls"]}
        for expected in HEADER_CONTROLS:
            record=controls[tuple(expected["id"])]
            require(common.float_vector_equal(record["bounds"],common.mapped(*spec["logical_size"],expected["rect"])),
                    "independent live-header control geometry differs")
    require(type(hit) is dict and set(hit)=={"controls","manual_keys","pedal_keys"},"complete hit records missing")
    require(len(hit["controls"])==68 and list(map(len,hit["manual_keys"]))==[61,61] and len(hit["pedal_keys"])==25,
            "complete hit-probe inventory missing")
    for probes,geometry in [(hit["controls"],layout["controls"]),
                            *zip(hit["manual_keys"],layout["manual_keys"],strict=True),(hit["pedal_keys"],layout["pedal_keys"])]:
        for record,item in zip(probes,geometry,strict=True):
            field="id" if "id" in item else "note"
            keys={field,"probes","visible"} if field=="id" else {field,"probes"}
            require(set(record)==keys and common.typed_equal(record[field],item[field]) and len(record["probes"])==5,
                    "incomplete or contradictory hit probes")
            for probe in record["probes"]:
                require(set(probe)=={"point","hit"} and len(probe["point"])==2 and len(probe["hit"])==4,
                        "malformed hit observation")


def validate_transform(spec,record,color=None):
    require(type(record) is dict and set(record)==TRANSFORM_KEYS,"complete renderer fields missing")
    require(common.float_vector_equal(record["scale"],spec["scale"]),"renderer scale differs")
    for key in ("viewport","clip","logical_viewport","logical_clip","clip_enabled","blend"):
        require(common.typed_equal(record[key],spec[key]),"renderer "+key+" differs")
    require(type(record["draw_color"]) is list and len(record["draw_color"])==4 and
            all(type(v) is int and 0<=v<=255 for v in record["draw_color"]),"renderer draw color missing")
    if color is not None:
        require(record["draw_color"]==color,"incoming/helper draw color differs")


def metadata_errors(spec,header,phase,baseline_only=False):
    errors=scenario_errors(spec,header)
    try:
        require(header["schema"]==1 and header["protocol"]==PROTOCOL and header["variant"]==spec["variant"],"wrong protocol/schema/variant")
        require([header["width"],header["height"]]==spec["output_size"] and header["bytes"]==spec["compared_pixels"]*4,
                "declared output/byte count differs")
        for key in ("viewport","clip","logical_viewport","logical_clip","clip_enabled"):
            require(common.typed_equal(header[key],spec[key]),"actual "+key+" differs")
        require(header["visible_clip_pixels"]==area(spec["visible_device_box"]),"visible caller pixel count differs")
        validate_transform(spec,header["renderer_before"],[17,23,31,127])
        validate_transform(spec,header["renderer_after"])
        require(common.typed_equal(header["info"],FIXED_INFO),"fixed complete information record differs")
        for name in ("model","session","hit"):
            require(common.typed_equal(header[name+"_before"],header[name+"_after"]),"paint changed complete "+name)
        validate_model(spec,header["model_before"],header["session_before"],header["hit_before"])
        backend=header["backend"]
        require(set(backend)=={"name","flags","texture_formats","maximum_texture_size","sdl_version","surface_format"} and
                backend["name"]=="software" and backend["sdl_version"]==[2,32,10] and
                type(backend["texture_formats"]) is list and len(backend["texture_formats"])>0,"wrong/missing SDL software backend identity")
        helper=header["helper_probe"]
        require(set(helper)=={"present","invoked","bounds","composition_scale","before","after","unchanged"},
                "complete independent helper probe missing")
        present=phase=="after" and not baseline_only
        require(helper["present"] is present and helper["invoked"] is (present and spec["eligible_h1"]),
                "helper availability/invocation differs from baseline/candidate boundary")
        require(common.float_vector_equal(helper["bounds"],spec["inset_binary32"]),"helper probe did not use independent full inset")
        sx,sy=header_geometry(*spec["logical_size"])[0]
        require(common.float_vector_equal(helper["composition_scale"],[sx,sy,min(sx,sy)]),"helper probe composition scale differs")
        validate_transform(spec,helper["before"],[17,23,31,127])
        validate_transform(spec,helper["after"],[17,23,31,127])
        require(common.typed_equal(helper["before"],helper["after"]) and helper["unchanged"] is True,
                "direct helper failed complete transform/color preservation")
        checks={key:True for key in ("transform_unchanged","model_unchanged","session_unchanged","hit_unchanged",
                                     "clip_containment","deterministic_repaint","inactive_classification")}
        checks.update({"clip_companion_checked":spec["clip_enabled"] and spec["variant"]=="main",
                       "after_all_repeat_checked":spec["variant"]=="after-all","fresh_repeat_checked":spec["variant"]=="fresh"})
        require(common.typed_equal(header["checks"],checks),"fixture preservation checks missing or contradictory")
        require(type(header["history_states"]) is int and header["history_states"]==(48 if spec["variant"]=="after-all" else 0),
                "history variant did not observe all 48 states")
        require(type(header["quiet_clip_pixels"]) is int and 0<=header["quiet_clip_pixels"]<=spec["compared_pixels"],
                "invalid native quiet clip observation")
        fields=set(scenario(spec))|{"schema","protocol","variant","width","height","bytes","viewport","clip",
            "logical_viewport","logical_clip","clip_enabled","renderer_before","renderer_after","model_before","model_after",
            "session_before","session_after","hit_before","hit_after","info","backend","helper_probe","checks",
            "visible_clip_pixels","quiet_clip_pixels","history_states"}
        require(set(header)==fields,"missing or unexpected full stream fields")
    except (ValueError,KeyError,IndexError,TypeError) as error:
        errors.append(str(error))
    return errors


def paired_metadata(record):
    # These are the only intentionally phase-dependent fields: the baseline
    # predates the private helper. Its complete probe states still must match.
    result={**record,"helper_probe":dict(record["helper_probe"])}
    result["helper_probe"].pop("present")
    result["helper_probe"].pop("invoked")
    return result


def parse_frame(payload,spec):
    end=payload.find(b"\n",0,transport.MAX_HEADER)
    require(end>=0,"missing bounded JSON-line frame header")
    header=read_json(payload[:end])
    require(type(header) is dict and type(header.get("schema")) is int and header["schema"]==1 and
            type(header.get("case")) is int and header["case"]==spec["case"],"wrong frame schema/case")
    width,height=header.get("width"),header.get("height")
    require(type(width) is type(height) is int and 0<width<=3900 and 0<height<=2200 and width*height<=MAX_PIXELS and
            [width,height]==spec["output_size"],"frame dimensions exceed declaration/bound")
    raw=payload[end+1:]
    require(type(header.get("bytes")) is int and len(raw)==header["bytes"]==width*height*4,
            "missing, extra or contradictory RGBA bytes")
    return header,raw,sha(payload[:end])


def read_frame(executable,spec,runner):
    args=["--case",str(spec["case"])]
    if spec["variant"]!="main":
        args.append("--"+spec["variant"])
    return parse_frame(runner(executable,args,MAX_FRAME),spec)


def inventory(executable,cases,runner):
    payload=runner(executable,["--list"],transport.MAX_HEADER)
    record=read_json(payload)
    require(type(record) is dict and set(record)=={"schema","protocol","cases","inventory"} and
            record["schema"]==1 and record["protocol"]==PROTOCOL and record["cases"]==48 and
            type(record["inventory"]) is list and len(record["inventory"])==48,"incomplete H1 inventory")
    for spec,row in zip(cases,record["inventory"],strict=True):
        require(type(row) is dict and set(row)==set(scenario(spec)) and not scenario_errors(spec,row),
                "missing/duplicate/reordered/contradictory H1 inventory case "+str(spec["case"]))
    return {"record":record,"sha256":sha(payload),"passed":True}


def fixture_portability_transition(root):
    current=(root/FIXTURE).read_bytes()
    current_sha=sha(current)
    line_source=current
    line_source_sha=current_sha
    indexed_array=current_sha==INDEXED_ARRAY_FIXTURE_SHA
    if indexed_array:
        original_array=(
            b'template <typename Range, typename Writer>\n'
            b'void array(std::ostream& out, const Range& values, Writer write) {\n'
            b"    out << '[';\n"
            b'    bool first = true;\n'
            b'    for (const auto& value : values) {\n'
            b"        if (!first) out << ',';\n"
            b'        first = false;\n'
            b'        write(out, value);\n'
            b'    }\n'
            b"    out << ']';\n"
            b'}\n'
        )
        indexed_array_source=(
            b'template <typename Range, typename Writer>\n'
            b'void array(std::ostream& out, const Range& values, Writer write) {\n'
            b"    out << '[';\n"
            b'    for (std::size_t index = 0; index < values.size(); ++index) {\n'
            b"        if (index != 0) out << ',';\n"
            b'        write(out, values[index]);\n'
            b'    }\n'
            b"    out << ']';\n"
            b'}\n'
        )
        require(current.count(indexed_array_source)==1 and original_array not in current,
                "fixture does not contain exactly the reviewed indexed array repair")
        line_source=current.replace(indexed_array_source,original_array,1)
        require(sha(line_source)==HELPER_ELSE_FIXTURE_SHA,
                "reversing the indexed array repair does not reproduce the reviewed constexpr-else fixture")
        line_source_sha=HELPER_ELSE_FIXTURE_SHA
    helper_else=line_source_sha==HELPER_ELSE_FIXTURE_SHA
    if helper_else:
        original_helper=(b"    if constexpr (h1_fixture_helper_present<Drawer>) {\n"
            b"        reference_header_h1_material(drawing, bounds, scale);\n"
            b"        return true;\n    }\n    return false;\n")
        corrected_helper=(b"    if constexpr (h1_fixture_helper_present<Drawer>) {\n"
            b"        reference_header_h1_material(drawing, bounds, scale);\n"
            b"        return true;\n    } else {\n        return false;\n    }\n")
        require(line_source.count(corrected_helper)==1 and original_helper not in line_source,
                "fixture does not contain exactly the reviewed constexpr else repair")
        line_source=line_source.replace(corrected_helper,original_helper,1)
        require(sha(line_source)==CAST_FIXTURE_SHA,
                "reversing the constexpr else repair does not reproduce the reviewed cast fixture")
        line_source_sha=CAST_FIXTURE_SHA
    original_line=b"            c.width = shape == 0 ? 1920 : 1400; c.height = shape == 0 ? 820 : 1080;\n"
    repairs={
        PORTABLE_FIXTURE_SHA:("float-literals",
            b"            c.width = shape == 0 ? 1920.0F : 1400.0F; c.height = shape == 0 ? 820.0F : 1080.0F;\n"),
        CAST_FIXTURE_SHA:("explicit-float-casts",
            b"            c.width = static_cast<float>(shape == 0 ? 1920 : 1400); c.height = static_cast<float>(shape == 0 ? 820 : 1080);\n"),
    }
    require(line_source_sha in repairs,"corrected fixture source differs from current pin")
    repair,corrected_line=repairs[line_source_sha]
    require(line_source.splitlines(keepends=True).count(corrected_line)==1 and original_line not in line_source and
            all(line not in line_source for name,line in repairs.values() if name!=repair),
            "fixture does not contain exactly the reviewed MSVC source repair")
    require(sha(line_source.replace(corrected_line,original_line,1))==PINNED[FIXTURE],
            "reversing the sole source repair does not reproduce the genuine baseline fixture")
    result={"baseline_fixture_sha256":PINNED[FIXTURE],"current_fixture_sha256":current_sha,
            "current_fixture_repair":repair,
            "reviewed_current_fixture_sha256":{name:digest for digest,(name,line) in repairs.items()},
            "baseline_comparator_sha256":BASELINE_COMPARATOR_SHA,"exact_single_line_reversal":True,
            "case_values_preserved":True,"source_bytes_identical":False,
            "method":"Four exactly representable dimensions use one of two reviewed complete-line repairs: float literals or explicit float casts; reversing the sole complete source line reproduces the original pinned fixture SHA-256."}
    if helper_else:
        result.update({"current_fixture_repair":"explicit-float-casts-and-constexpr-else",
            "exact_single_line_reversal":False,"exact_helper_branch_reversal":True,
            "intermediate_fixture_sha256":CAST_FIXTURE_SHA,
            "method":"The exact reviewed constexpr-else block reverses to the pinned cast fixture; reversing that fixture's sole complete dimension line reproduces the genuine original fixture SHA-256. Both helper branches and every case value are preserved."})
        result["reviewed_current_fixture_sha256"]["explicit-float-casts-and-constexpr-else"]=HELPER_ELSE_FIXTURE_SHA
    if indexed_array:
        result.update({"current_fixture_repair":"explicit-float-casts-and-constexpr-else-and-indexed-array",
            "exact_indexed_array_reversal":True,
            "indexed_array_reversed_fixture_sha256":HELPER_ELSE_FIXTURE_SHA,
            "method":"The exact reviewed indexed array helper reverses to the pinned constexpr-else fixture; that exact branch reverses to the pinned cast fixture, whose sole dimension line reproduces the genuine original fixture SHA-256. Element writers, complete case values and every historical pin remain preserved."})
        result["reviewed_current_fixture_sha256"]["explicit-float-casts-and-constexpr-else-and-indexed-array"]=INDEXED_ARRAY_FIXTURE_SHA
    return result


def baseline_inputs(root,receipt_path,receipt_sha256,supplement_path,before,after,before_painter,source_files,baseline_only):
    require(type(receipt_sha256) is str and re.fullmatch(r"[0-9a-f]{64}",receipt_sha256) is not None,
            "baseline-receipt-sha256 must be the root-frozen 64-character lowercase hexadecimal digest")
    receipt_id=identity(receipt_path)
    require(receipt_id["sha256"]==receipt_sha256 and receipt_id["bytes"]<=transport.MAX_HEADER,"genuine H1 base receipt identity differs")
    receipt=read_json(receipt_path.read_bytes())
    sources=receipt["source_sha256"]
    require(receipt["schema"]==1 and receipt["base_commit"]==BASE_COMMIT and len(sources)==229 and
            sources[PAINTER]==BEFORE_PAINTER_SHA and before_painter["sha256"]==BEFORE_PAINTER_SHA,
            "not the genuine accepted T3 revision2 pre-H1 source")
    require(not baseline_only or source_files[PAINTER]["sha256"]==BEFORE_PAINTER_SHA,
            "baseline-only is forbidden after any painter change")
    original=read_json((root/PROTECTED).read_bytes())
    protected={name:row for group in original["groups"].values() for name,row in group["files"].items()}
    require(len(protected)==213 and PAINTER not in protected and receipt["protected_count"]==213,
            "protected source inventory count changed")
    for name,digest in sources.items():
        if name==PAINTER:
            continue
        current=identity(root/name)
        require(current["sha256"]==digest,"protected pre/post-H1 source differs: "+name)
        if name in protected and name!=typography.MAIN:
            require(current["sha256"]==protected[name]["sha256"] and current["bytes"]==protected[name]["bytes"],
                    "original protected source differs: "+name)
        source_files[name]=current
    require(set(protected)<=set(sources),"baseline omitted a protected source")
    app=identity(before.parent/("hammond_standalone.exe" if before.suffix==".exe" else "hammond_standalone"))
    require(all(app[k]==receipt["files"]["hammond_standalone"][k] for k in ("bytes","sha256")),"genuine baseline app bytes changed")
    supplement_id=identity(supplement_path)
    require(supplement_id["bytes"]<=transport.MAX_HEADER,"H1 fixture supplement exceeds finite bound")
    supplement=read_json(supplement_path.read_bytes())
    require(supplement["schema"]==1 and supplement["protocol"]==PROTOCOL and
            supplement["base_receipt_sha256"]==receipt_sha256,"supplement is not bound to genuine accepted T3 receipt")
    transition=fixture_portability_transition(root)
    require(source_files[FIXTURE]["sha256"]==transition["current_fixture_sha256"],
            "current fixture identity differs from corrected source pin")
    require(supplement["source_sha256"].get(PAINTER)==BEFORE_PAINTER_SHA and
            supplement["source_sha256"].get(FIXTURE)==PINNED[FIXTURE] and
            supplement["source_sha256"].get("tools/compare_header_material.py")==BASELINE_COMPARATOR_SHA,
            "baseline supplement does not name the exact original fixture, comparator and before painter")
    binaries={"before":identity(before),"after":identity(after)}
    require(before!=after and common.typed_equal(binaries["before"],supplement["binary"]),
            "genuine frozen H1 executable differs or both paths are the same")
    inputs=supplement["inputs"]
    require(type(inputs) is list and inputs and len(inputs)<=64,"complete bounded baseline build inputs missing")
    for item in [*inputs,supplement["object"]]:
        require(type(item) is dict and identity(item["path"])==item,"retained baseline build input changed")
    input_hashes={row["sha256"] for row in inputs}
    require({BEFORE_PAINTER_SHA,PINNED[FIXTURE]}<=input_hashes,
            "supplement omits frozen painter or genuine original fixture input bytes")
    require(type(supplement["commands"]) is list and len(supplement["commands"])==2 and
            all(type(command) in (str,list) and command for command in supplement["commands"]),
            "frozen fixture compile/link ancestry missing")
    return {"receipt":receipt_id,"expected_receipt_sha256":receipt_sha256,"supplement":supplement_id,"baseline_app":app,"before_painter":before_painter,
            "binaries":binaries,"protected_count":213,"source_count":229,"retained_build_inputs":[*inputs,supplement["object"]],
            "commands":supplement["commands"],"fixture_portability_transition":transition,
            "method":"Real pre-H1 executable from the original fixture and genuine accepted T3 painter; the current fixture has only one of the two exact reviewed value-preserving MSVC source repairs, not identical source bytes; no candidate before switch."}


def candidate_build_inputs(root,build_dir,after):
    suffix=".exe" if after.suffix==".exe" else ""
    standalone=(build_dir/"apps/standalone").resolve(strict=True)
    require(after==(standalone/(EXECUTABLE+suffix)).resolve(strict=True),"candidate fixture outside declared matching build")
    build=transport.build_identities(build_dir)
    cache=(build_dir/"CMakeCache.txt").read_text().splitlines()
    roots=[line.partition("=")[2] for line in cache if line.startswith("CMAKE_HOME_DIRECTORY:INTERNAL=")]
    require(len(roots)==1 and Path(roots[0]).resolve(strict=True)==root,"candidate build configured from a different source root")
    sdl=Path(build["configuration"]["HAMMOND_SDL2_ROOT"])
    for name,digest in SDL_EXTRA.items():
        item=identity(sdl/name)
        require(item["sha256"]==digest,"pinned independent SDL glyph sampling source differs")
        build["files"].append(item)
    target=standalone/"CMakeFiles"/(EXECUTABLE+".dir")
    obj=(target/"native_tests"/(EXECUTABLE+".cpp.o")).resolve(strict=True)
    commands=read_json((build_dir/"compile_commands.json").read_bytes())
    rows=[row for row in commands if type(row.get("output")) is str and (build_dir/row["output"]).resolve()==obj]
    require(len(rows)==1,"candidate fixture object lacks unique compile-command identity")
    row=rows[0]
    directory=Path(row["directory"]).resolve(strict=True)
    tokens=row.get("arguments") or shlex.split(row["command"])
    require(directory==standalone and (directory/row["file"]).resolve(strict=True)==root/FIXTURE and
            tokens.count("-c")==tokens.count("-o")==1 and
            (directory/tokens[tokens.index("-c")+1]).resolve(strict=True)==root/FIXTURE and
            (directory/tokens[tokens.index("-o")+1]).resolve(strict=True)==obj,
            "candidate command does not compile frozen fixture source/object")
    links=shlex.split((target/"link.txt").read_text())
    libraries=[standalone/"libhammond_standalone_drawing.a",standalone/"libhammond_standalone_support.a",
               build_dir/"libhammond_core.a",build_dir/"_sdl2/libSDL2.a"]
    linked={(standalone/t).resolve() for t in links if t and not t.startswith("-")}
    require(links.count("-o")==1 and (standalone/links[links.index("-o")+1]).resolve(strict=True)==after and
            all(p.resolve(strict=True) in linked for p in [obj,*libraries]),"candidate link omits required source object/library")
    require(not (target/"InstrumentView.cpp.o").exists(),"included real painter must not also be compiled separately in H1 fixture")
    require(obj.stat().st_mtime_ns>=max((root/FIXTURE).stat().st_mtime_ns,(root/PAINTER).stat().st_mtime_ns) and
            after.stat().st_mtime_ns>=max(p.stat().st_mtime_ns for p in [obj,*libraries]),
            "candidate object/executable predates a current declared input; rebuild coherently")
    dep=target/"native_tests"/(EXECUTABLE+".cpp.o.d")
    dependencies=shlex.split(dep.read_text().replace("\\\n",""))
    require(root/PAINTER in {(directory/token).resolve() for token in dependencies if not token.endswith(":")},
            "actual included painter dependency missing")
    build["files"].extend(identity(p) for p in [obj,dep,target/"flags.make",target/"link.txt",target/"DependInfo.cmake",*libraries])
    build["fixture_compile_command"]=row
    material=(standalone/(typography.MATERIAL_EXECUTABLE+suffix)).resolve(strict=True)
    material_inputs=typography.material_build_inputs(root,build_dir,material,suffix)
    build["files"].extend(material_inputs["files"])
    return build,material,material_inputs


def compare_images(spec,ah,ar,ahash,bh,br,bhash,atlases,artifacts,baseline_only):
    errors=["before "+e for e in metadata_errors(spec,ah,"before",baseline_only)]
    errors.extend("after "+e for e in metadata_errors(spec,bh,"after",baseline_only))
    metadata_equal=common.typed_equal(paired_metadata(ah),paired_metadata(bh))
    if not metadata_equal:
        errors.append("complete paired metadata/model/session/hit/renderer records differ")
    before=Image.frombytes("RGBA",tuple(spec["output_size"]),ar)
    after=Image.frombytes("RGBA",tuple(spec["output_size"]),br)
    mask=common.allowance_mask(spec)
    require(sha(mask.tobytes())==spec["allowance_sha256"],"pre-execution support declaration changed")
    metrics,(rgba,maximum,outside)=common.difference_metrics(before,after,mask)
    changed=maximum.point(lambda v:255 if v else 0)
    metrics["difference_box"]=list(changed.getbbox()) if changed.getbbox() else None
    metrics["per_row_different_pixels"]=[changed.crop((0,y,changed.width,y+1)).histogram()[255] for y in range(changed.height)]
    metrics["per_row_outside_pixels"]=[outside.crop((0,y,outside.width,y+1)).histogram()[255] for y in range(outside.height)]
    exact_required=baseline_only or spec["whole_frame_equality_required"]
    exact=not exact_required or ar==br
    children=child_checks(spec,before,after,atlases)
    text={phase:canonical_typography(spec,image) for phase,image in (("before",before),("after",after))}
    clip={phase:caller_clip_checks(spec,image) for phase,image in (("before",before),("after",after))}
    result={"case":spec["case"],"variant":spec["variant"],"active_reference":spec["active_reference"],
        "eligible_h1":spec["eligible_h1"],"metadata_equal":metadata_equal,"metadata_error_count":len(errors),
        "metadata_errors":typography.bounded_errors(errors),"before_header_sha256":ahash,"after_header_sha256":bhash,
        "before_rgba_sha256":sha(ar),"after_rgba_sha256":sha(br),"allowed_pixels":spec["allowed_pixels"],
        "protected_pixels":spec["protected_pixels"],"allowance_sha256":spec["allowance_sha256"],"metrics":metrics,
        "complete_before_model_sha256":sha(json_bytes(ah["model_before"])),
        "complete_after_model_sha256":sha(json_bytes(bh["model_before"])),
        "whole_frame_equality_required":exact_required,"whole_frame_equality_passed":exact,
        "children":children,"typography":text,"caller_clip_preservation":clip,
        "passed":not errors and metadata_equal and metrics["passed"] and exact and children["passed"] and
                 all(r["passed"] for r in [*text.values(),*clip.values()])}
    if not result["passed"]:
        result["artifacts"]=artifacts.save(f"h1-{spec['case']:02d}-{spec['variant']}",
            (("absolute-rgba-difference",rgba),("outside",outside),("before",before),("after",after)))
    return result,before,after


def normalized_repeat_header(header):
    result={key:value for key,value in header.items() if key not in ("variant","history_states")}
    result["checks"]={key:value for key,value in header["checks"].items() if key not in
                       ("clip_companion_checked","after_all_repeat_checked","fresh_repeat_checked")}
    return result


def fixture_assertions(executable,cases,runner,phase,baseline_only):
    payload=runner(executable,[],transport.MAX_HEADER)
    record=read_json(payload)
    present=phase=="after" and not baseline_only
    expected={"schema":1,"protocol":PROTOCOL,"status":"passed","cases":48,"paintings":163,
              "clipped_cases":16,"empty_cases":2,"inactive_cases":8,"deterministic_repaints":48,
              "clip_companions":16,"history_states":48,"history_repaints":1,"fresh_repaints":1,
              "helper_present":present,"helper_probes":95 if present else 0,
              "protected_pixels":sum(c["compared_pixels"]-area(c["visible_device_box"]) for c in cases),
              "quiet_clip_pixels":sum(c["allowed_pixels"] for c in cases if c["clip_enabled"]),
              "backend":"SDL software surface; copied state; no audio/window"}
    require(type(record) is dict and set(record)==set(expected)|{"checks"} and
            all(common.typed_equal(record.get(k),v) for k,v in expected.items()) and
            type(record["checks"]) is int and record["checks"]>0,"complete fixture default summary differs from frozen literal counts")
    return {"record":record,"sha256":sha(payload),"passed":True}


class Runner:
    def __init__(self,timeout):
        self.timeout=timeout
        self.started=time.monotonic()
        self.invocations=0

    def __call__(self,executable,args,limit):
        require(self.invocations<137,"fixed native invocation bound exceeded")
        remaining=MAX_TOTAL_SECONDS-(time.monotonic()-self.started)
        require(remaining>0,"fixed total runtime bound exceeded")
        self.invocations+=1
        return transport.command(executable,args,min(self.timeout,remaining),limit)


def freeze_declarations(root):
    atlases=font_atlases(root/FONT)
    origins=new_grain_origins()
    cases=[declare_case(case,origins) for case in case_matrix()]
    uncut=[declare_case(companion(case),origins) for case in case_matrix() if case["clip_enabled"]]
    require(cases[46]["allowed_pixels"]==142880 and cases[46]["protected_pixels"]==1430472 and
            cases[46]["allowance_bounds"]==[76,14,1596,108],"canonical exact support differs from admitted H1")
    require([c["case"] for c in cases if c["whole_frame_equality_required"]]==[27,28,29,33,34,36,37,38,39,40,41,42,43],
            "13 exact empty/inactive/excluded cases differ")
    require(all(cases[i]["allowed_pixels"]==4096 and cases[i]["protected_pixels"]==0 and
                cases[i]["output_size"]==[64,64] for i in (30,31,32)),"maximum logical geometry must retain bounded 64-square crops")
    for spec in [*cases,*uncut]:
        spec["children"]=child_declaration(spec,atlases)
    declaration={"schema":1,"model":MODEL,"protocol":PROTOCOL,"contract_sha256":PINNED[CONTRACT],
        "source_before_painter_sha256":BEFORE_PAINTER_SHA,"support_method":"Exact independent operation union: old gradient + all old grain + 257-column new field + all16384 new grain rectangles, then actual declared output/viewport/enabled clip intersections; no dilation or candidate pixels.",
        "grain_origins_sha256":"afd3639f16f5ae4ce396ea0a91d7bb4192cb0c7cc6139daa2ee0eb45a1f6a0e6",
        "font_alpha_sha256":{name:atlas["alpha_sha256"] for name,atlas in atlases.items()},
        "glyph_method":"Independent raw FontData RLE, frozen T3 and caption arguments, binary32 Drawing COPY geometry, pinned SDL clipped source/destination rounding and7-bit bilinear sampling; all opaque coverage and every final strong alpha>=192 pixel are checked.",
        "cases":cases,"uncut_companions":uncut,"repeats":[{"case":46,"variant":v} for v in ("after-all","fresh")]}
    return declaration,cases,uncut,atlases


def static_checks(root):
    transition=fixture_portability_transition(root)
    for name,digest in PINNED.items():
        expected=transition["current_fixture_sha256"] if name==FIXTURE else digest
        require(identity(root/name)["sha256"]==expected,"pinned source differs: "+name)
    original,_=original_observations(root)
    declaration,cases,uncut,atlases=freeze_declarations(root)
    # Parser refusal probes operate on tiny synthetic byte packets, not native
    # pixels or simulated H1 colors. They establish fail-closed transport only.
    spec={"case":0,"output_size":[1,1]}
    good=b'{"schema":1,"case":0,"width":1,"height":1,"bytes":4}\n'+bytes(4)
    parse_frame(good,spec)
    invalid=[good[:-1],good+b"x",good.replace(b'"case":0',b'"case":1'),
             good.replace(b'"case":0',b'"case":0,"case":0'),
             good.replace(b'"width":1',b'"width":8192'),
             good.replace(b'"schema":1',b'"schema":true'),
             good.replace(b'"bytes":4',b'"bytes":NaN')]
    rejected=0
    for packet in invalid:
        try:
            parse_frame(packet,spec)
        except (ValueError,TypeError,KeyError):
            rejected+=1
    require(rejected==len(invalid),"malformed-frame parser did not fail closed")
    return {"status":"static-checks-passed","native_executions":0,"candidate_colors_evaluated":0,
            "fixture_portability_transition":transition,
            "original_scalar_planes":original["scalar_planes_reproduced"],"original_grid_cells_per_image":24,
            "original_numerical_passed":44,"original_numerical_failed":59,"main_cases":len(cases),
            "uncut_companions":len(uncut),"main_output_pixels":sum(c["compared_pixels"] for c in cases),
            "empty_allowance_cases":13,"canonical_support_pixels":cases[46]["allowed_pixels"],
            "canonical_support_box":cases[46]["allowance_bounds"],"resource_outputs":[c["output_size"] for c in cases[30:33]],
            "parser_negative_cases_rejected":rejected,"declaration_sha256":sha(json_bytes(declaration)),
            "limits":"Static arithmetic/parser/source checks only; no native preservation, H1 numerical acceptance, actual-frame visual or whole-interface claim."}


def main():
    parser=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--before",type=Path)
    parser.add_argument("--after",type=Path)
    parser.add_argument("--before-painter",type=Path)
    parser.add_argument("--baseline-receipt",type=Path)
    parser.add_argument("--baseline-receipt-sha256",help="mandatory for native comparison: independently reviewed root-frozen pre-H1 receipt SHA-256")
    parser.add_argument("--fixture-baseline-receipt",type=Path)
    parser.add_argument("--build-dir",type=Path)
    parser.add_argument("--source-root",type=Path,default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--output",type=Path,help="new directory; original evidence is never overwritten")
    parser.add_argument("--baseline-only",action="store_true",help="demonstrate genuine pre-H1 baseline and retain expected44/59numerical outcomes")
    parser.add_argument("--static-check",action="store_true",help="only source/arithmetic/parser checks; no executable invocation and no output files")
    parser.add_argument("--timeout",type=float,default=60)
    parser.add_argument("--failure-png-budget-mib",type=int,default=64)
    args=parser.parse_args()
    root=args.source_root.resolve(strict=True)
    if args.static_check:
        print(json_bytes(static_checks(root)).decode().strip(),flush=True)
        return 0
    require(all(getattr(args,k) is not None for k in ("before","after","build_dir","output","fixture_baseline_receipt","baseline_receipt_sha256")),
            "before,after,build-dir,output,fixture-baseline-receipt and baseline-receipt-sha256 are mandatory for native comparison")
    require(re.fullmatch(r"[0-9a-f]{64}",args.baseline_receipt_sha256) is not None,
            "baseline-receipt-sha256 must be the root-frozen 64-character lowercase hexadecimal digest")
    require(0<args.timeout<=120 and 8<=args.failure_png_budget_mib<=64,"fixed timeout/storage domain exceeded")
    output=args.output.resolve()
    output.mkdir(parents=True,exist_ok=False)
    started=time.monotonic()
    artifacts=transport.FailureArtifacts(output,args.failure_png_budget_mib*1024*1024)
    runner=Runner(args.timeout)
    report={"schema":1,"model":MODEL,"protocol":PROTOCOL,"status":"failed","mode":"baseline-only" if args.baseline_only else "candidate",
        "results":[],"repeats":[],"failures":[],"execution_passed":False,"numerical_screens_passed":False,
        "complete_tool_acceptance":False,"baseline_demonstrated":False,
        "coverage":{"required_main_pairs":48,"required_companion_pairs":16,"required_repeats_per_side":2,
                    "inputs_unchanged":False,"matrix_complete":False},
        "separate_gates":{"source_review":"Required: only admitted private helper/selector/header inset selection; all child arguments/order and other painters preserved.",
            "visual_admission":"Required separately: actual whole-header and complete application frames against unchanged reference and genuine immediately-before accepted app.",
            "timing":"Required separately: representative source-bound before/after timing and no visible performance regression."},
        "limitations":["Successful execution/preservation is separate from all103numerical inequalities; baseline demonstration retains44pass/59fail and never accepts H1.",
            "Resource cases30..32 allocate only64x64 output and have no protected exterior; no whole8192frame is allocated or claimed.",
            "Antialiased glyph edges blend over changed material; exact paired preservation covers independently reconstructed opaque cores, with complete strong-glyph coverage and unchanged T3 gates.",
            "Finite software evidence does not establish literal whole-interface1:1, real display/DPI/input, native accessibility, physical fidelity, callback deadlines or platform/release acceptance."]}
    try:
        require(Path(transport.__file__).resolve()==root/"tools/compare_heading_typography.py" and
                Path(typography.__file__).resolve()==root/"tools/compare_title_typography.py" and
                Path(common.__file__).resolve()==root/"tools/compare_footage_typography.py","pinned utility imported from wrong checkout")
        source_files={name:identity(root/name) for name in PINNED}
        transition=fixture_portability_transition(root)
        require(all(source_files[name]["sha256"]==(transition["current_fixture_sha256"] if name==FIXTURE else digest)
                    for name,digest in PINNED.items()),"pinned contract/review/font/fixture/transport changed")
        for name in (PAINTER,"tools/compare_header_material.py","CMakeLists.txt","apps/standalone/CMakeLists.txt"):
            source_files[name]=identity(root/name)
        observation_source=read_json((root/OBSERVATIONS).read_bytes())
        for item in observation_source["images"].values():
            source_files[item["path"]]=identity(root/item["path"])
        original,reference=original_observations(root)
        write_json(output/"original-observations.json",original)
        declaration,cases,uncut,atlases=freeze_declarations(root)
        declaration_identity=write_json(output/"support-declaration.json",declaration)
        before,after=args.before.resolve(strict=True),args.after.resolve(strict=True)
        before_painter=identity(args.before_painter or before.parent/"InstrumentView.cpp")
        baseline=baseline_inputs(root,(args.baseline_receipt or root/BASELINE).resolve(strict=True),
            args.baseline_receipt_sha256,args.fixture_baseline_receipt.resolve(strict=True),before,after,before_painter,source_files,args.baseline_only)
        build,material,material_inputs=candidate_build_inputs(root,args.build_dir.resolve(strict=True),after)
        report["inputs"]={"sources":source_files,"baseline":baseline,"build":build,"material":material_inputs,
                          "support_declaration":declaration_identity,"python":platform.python_version(),
                          "pillow":PILLOW_VERSION,"libjpeg_turbo":features.version_feature("libjpeg_turbo")}
        write_json(output/"input-identities.json",report["inputs"])
        # All declarations/identities above are written before the first native
        # call. An invalid existing material/T3 geometry result cannot be hidden
        # behind a successful H1 canonical statistic or a working transport.
        material_payload=runner(material,[],transport.MAX_HEADER)
        material_record=read_json(material_payload)
        typography.validate_material_summary(material_record)
        report["native_material_acceptance"]={"passed":True,"record":material_record,"sha256":sha(material_payload)}
        print("unchanged native material1317 gate: passed",flush=True)
        inventories={phase:inventory(executable,cases,runner) for phase,executable in (("before",before),("after",after))}
        require(common.typed_equal(inventories["before"]["record"],inventories["after"]["record"]),"paired48-case inventories differ")
        assertions={phase:fixture_assertions(executable,cases,runner,phase,args.baseline_only)
                    for phase,executable in (("before",before),("after",after))}
        report["fixture_assertions"]=assertions
        write_json(output/"fixture-receipts.json",{"inventories":inventories,"assertions":assertions})
        companions={c["case"]:c for c in uncut}
        original46={}
        numerical=None
        for spec in cases:
            try:
                ah,ar,ahash=read_frame(before,spec,runner)
                bh,br,bhash=read_frame(after,spec,runner)
                result,a,b=compare_images(spec,ah,ar,ahash,bh,br,bhash,atlases,artifacts,args.baseline_only)
                if spec["case"]==46:
                    old_stats,new_stats=measurements(a),measurements(b)
                    baseline_equal=all(old_stats[name]["decoded_patch_rgb_sha256"]==
                        original["patches"]["t2_canonical"][name]["decoded_patch_rgb_sha256"] for name in PRIMARY)
                    before_screens,after_screens=numerical_screens(reference,old_stats),numerical_screens(reference,new_stats)
                    baseline_reproduced=baseline_equal and before_screens["passed_count"]==44 and before_screens["failed_count"]==59
                    if not baseline_reproduced:
                        result["passed"]=False
                    numerical={"canonical_case":46,"primary_patch_order":list(PRIMARY),"primary_RGB_matches_genuine_T2":baseline_equal,
                        "baseline_reproduced":baseline_reproduced,"before":{"measurements":old_stats,"grid":grid_measurements(a),"screens":before_screens},
                        "after":{"measurements":new_stats,"grid":grid_measurements(b),"screens":after_screens},
                        "before_and_after_scalar_planes":200,"original_scalar_planes_retained":200,"descriptive_witnesses":list(WITNESSES)}
                    write_json(output/"numerical-screens.json",numerical)
                    report["numerical_summary"]={"baseline_reproduced":baseline_reproduced,"before_passed":before_screens["passed_count"],
                        "before_failed":before_screens["failed_count"],"after_passed":after_screens["passed_count"],
                        "after_failed":after_screens["failed_count"],"after_mean_error_exact":after_screens["mean_error_exact"],
                        "after_RMS_error":after_screens["rms_error"],"after_RMS_error_hex":after_screens["rms_error_hex"]}
                    original46={"before":(ah,sha(ar)),"after":(bh,sha(br))}
                    if not after_screens["passed"]:
                        result["numerical_failure_artifacts"]=artifacts.save("h1-46-numerical",(("before-header",a.crop((72,10,1600,112))),
                            ("after-header",b.crop((72,10,1600,112))),("absolute-header-difference",ImageChops.difference(a,b).crop((72,10,1600,112)))))
                if spec["clip_enabled"]:
                    full=companions[spec["case"]]
                    fh,fr,fhash=read_frame(before,full,runner)
                    gh,gr,ghash=read_frame(after,full,runner)
                    companion_result,fa,fb=compare_images(full,fh,fr,fhash,gh,gr,ghash,atlases,artifacts,args.baseline_only)
                    quiet={"before":quiet_companion_check(spec,a,fa,atlases),"after":quiet_companion_check(spec,b,fb,atlases)}
                    model_exact=all(common.typed_equal(main[key],uncut_header[key]) for main,uncut_header in ((ah,fh),(bh,gh))
                        for key in ("model_before","model_after","session_before","session_after","hit_before","hit_after","info","backend"))
                    result["uncut_restriction"]={"quiet":quiet,"identical_complete_model":model_exact,
                        "passed":model_exact and all(q["passed"] for q in quiet.values())}
                    result["passed"]=result["passed"] and result["uncut_restriction"]["passed"]
                    report["results"].append(companion_result)
                    del fa,fb,fr,gr
                report["results"].append(result)
                print(f"H1case{spec['case']:02d}: {'passed' if result['passed'] else 'FAILED'} preservation",flush=True)
                del a,b,ar,br
            except (ValueError,OSError,KeyError,IndexError,TypeError) as error:
                report["results"].append({"case":spec["case"],"variant":"main","passed":False,"error":str(error)[:MAX_DIAGNOSTICS]})
                print(f"H1case{spec['case']:02d}: FAILED {str(error)[:200]}",flush=True)
        require(set(original46)=={"before","after"},"canonical46 original records absent; repeats cannot be credited")
        for phase,executable in (("before",before),("after",after)):
            for variant in ("after-all","fresh"):
                spec={**cases[46],"variant":variant}
                header,raw,header_sha=read_frame(executable,spec,runner)
                errors=metadata_errors(spec,header,phase,args.baseline_only)
                original_header,original_rgba_sha=original46[phase]
                equal=sha(raw)==original_rgba_sha and common.typed_equal(normalized_repeat_header(header),normalized_repeat_header(original_header))
                report["repeats"].append({"case":46,"phase":phase,"variant":variant,"header_sha256":header_sha,"rgba_sha256":sha(raw),
                    "metadata_errors":typography.bounded_errors(errors),"exact_rgba_and_complete_state":equal,"passed":not errors and equal})
        watched=[*source_files.values(),before_painter,baseline["receipt"],baseline["supplement"],baseline["baseline_app"],
                 *baseline["binaries"].values(),*baseline["retained_build_inputs"],*build["files"]]
        drift=[item["path"] for item in watched if identity(item["path"])!=item]
        require(not drift,"inputs changed during H1 comparison: "+", ".join(drift))
        report["coverage"]["inputs_unchanged"]=True
        required={(c["case"],c["variant"]) for c in [*cases,*uncut]}
        actual=[(r["case"],r["variant"]) for r in report["results"]]
        complete=len(actual)==len(required)==64 and set(actual)==required and all(r["passed"] for r in report["results"])
        repeats_complete=len(report["repeats"])==4 and all(r["passed"] for r in report["repeats"])
        report["coverage"].update({"matrix_complete":complete,"main_pairs_completed":sum(r["variant"]=="main" and "metrics" in r for r in report["results"]),
            "companion_pairs_completed":sum(r["variant"]=="uncut" and "metrics" in r for r in report["results"]),
            "repeats_complete":repeats_complete,"protected_sources":213,"baseline_source_map":229,
            "main_compared_pixels":sum(c["compared_pixels"] for c in cases),
            "companion_compared_pixels":sum(c["compared_pixels"] for c in uncut),
            "outside_changed_pixels":sum(r.get("metrics",{}).get("outside_pixels",0) for r in report["results"])})
        report["execution_passed"]=complete and repeats_complete and numerical is not None and numerical["baseline_reproduced"]
        report["numerical_screens_passed"]=numerical is not None and numerical["after"]["screens"]["passed"]
        if args.baseline_only:
            report["baseline_demonstrated"]=report["execution_passed"] and (numerical["after"]["screens"]["passed_count"],
                numerical["after"]["screens"]["failed_count"])==(44,59)
            report["status"]="baseline-demonstrated" if report["baseline_demonstrated"] else "failed"
        else:
            report["complete_tool_acceptance"]=report["execution_passed"] and report["numerical_screens_passed"]
            report["status"]="passed" if report["complete_tool_acceptance"] else "failed"
    except (ValueError,OSError,KeyError,IndexError,TypeError) as error:
        report["failures"].append(str(error)[:MAX_DIAGNOSTICS])
    report["elapsed_seconds"]=round(time.monotonic()-started,3)
    report["failure_png_bytes"]=artifacts.used
    report["storage_bounds"]={"per_process_stdout_bytes":MAX_FRAME,"per_process_stderr_bytes":transport.MAX_STDERR,
        "per_json_bytes":transport.MAX_JSON_BYTES,"json_files_max":7,"failure_png_bytes":artifacts.limit,
        "raw_frames_retained":0,"maximum_output_pixels":MAX_PIXELS,"maximum_native_invocations":137,
        "actual_native_invocations":runner.invocations,"per_native_timeout_seconds":args.timeout,
        "total_native_wall_deadline_seconds":MAX_TOTAL_SECONDS,"concurrent_native_processes":1}
    write_json(output/"report.json",report)
    print(json_bytes({"status":report["status"],"execution_passed":report["execution_passed"],
        "numerical_screens_passed":report["numerical_screens_passed"],"complete_tool_acceptance":report["complete_tool_acceptance"],
        "baseline_demonstrated":report["baseline_demonstrated"],"failures":report["failures"],"report":str(output/"report.json")}).decode().strip(),flush=True)
    return 0 if report["status"] in ("passed","baseline-demonstrated") else 1


if __name__=="__main__":
    try:
        sys.exit(main())
    except (ValueError,OSError) as error:
        print("header comparison: "+str(error),file=sys.stderr)
        sys.exit(1)


