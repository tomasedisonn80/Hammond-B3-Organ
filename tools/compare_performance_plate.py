#!/usr/bin/env python3
"""Independent P1 numerical and paired preservation acceptance (stdlib only).

Persistent numerical gate, without a historical executable::

  python3 -B tools/compare_performance_plate.py --candidate-only --after FIXTURE

Paired acceptance requires a NEW output directory and explicit reviewed input
identities. See --help. The comparator never builds, retries, changes thresholds,
or selects support from candidate colors/exported masks. Each native stdout and
stderr is retained, including failed/truncated transports, in bounded zlib files.
The report distinguishes the numerical screen from preservation, timing, visual,
physical and whole-interface acceptance. A successful candidate-only exit claims
only the frozen canonical 62-screen gate and its canonical fixture validation.
It admits either the original coherent UiModel source pair or the exact A26
recall-only addition, with whole-block reversal to the original bytes. Paired
mode retains the original pair and genuine baseline admission unchanged.

The font sampler follows the pinned SDL 2.32.10 software COPY implementation;
its geometry and seven-bit linear filter are derived from the public source.
No production P1 field/grain implementation is imported or reproduced here.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import signal
import struct
import subprocess
import sys
import tempfile
import threading
import time
import zlib


PROTOCOL = "performance-plate-p1-v1"
MODEL = "performance-plate-p1-independent-v1"
SESSION = "docs/development/2026-11-16-console-completion"
CONTRACT = "docs/design/PERFORMANCE_PLATE_P1_CONTRACT.md"
AUTHORING = SESSION + "/reports/p1-authoring.json"
ADMISSION = "docs/reviews/PERFORMANCE_PLATE_P1_DESIGN_ADMISSION.md"
BASELINE_ADMISSION = SESSION + "/reports/p1-baseline-patch-admission.json"
FIXTURE = "apps/standalone/native_tests/test_standalone_performance_plate.cpp"
PAINTER = "apps/standalone/InstrumentView.cpp"
FONT = "apps/standalone/FontData.h"
BEFORE_EXE_SHA = "65d0cc74e53faf2d655cba5f6254d5087715c730f22556ec81940195ad18149e"
BEFORE_PAINTER_SHA = "10865a6bad39bc0a254b8b3f4cf6b013bef48770a2b39c7e9f9a70f438d56366"
PINNED = {
    CONTRACT: "20c8839d38229bf24d983eac0baad7381f601c4e6763bbbe556bcdfa6c75ae45",
    AUTHORING: "f25c5c479c6c1ffb304028c8a306a7873f155eec6f6d5f9831ed6e93862290e2",
    ADMISSION: "7968cd304d54c27afe3e64013f9943e9189e613ddf3dd2df9d8284eeda27ae21",
    BASELINE_ADMISSION: "fb3c4bc99d1534222d80f7263a82fef2f883bb584e2c646aae43a7c80c4993ea",
    FIXTURE: "4f1875270af71d08c27372944a4a9c8e4c10b6c31dbeb85b3841b6965915956c",
    FONT: "f1a3121a2707a03a3b2e025c399e68c553ce9498f4b002ec13b18f512e334802",
    "apps/standalone/Drawing.cpp": "666e998cc61a9d501238783c8f2917d9be30db0bac76739f91bc23eb54f34b0a",
    "apps/standalone/UiModel.cpp": "0ecb0c4ee90d98cdb87c6f06b4685d368a7c12b72f9ea66e6c40228a4a855ecd",
    "apps/standalone/UiModel.h": "6d8c0b16ddb6f3059dc14aff41bfc615e37b43c53b2f6e88cc199255a6b674b1",
    "docs/design/atlas-cover-reference.jpg": "9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187",
    "docs/design/native-gallery-ui-delivery-title/images/play-reference-1672x941.png": "1df7d50cda9b61640702a4c4b516be1ae1b7be9879aa6bba0feb06c0bf9e5e60",
}
# Keep PINNED as the genuine original source identities. Only candidate-only
# may admit the exact A26 pair below; paired comparisons retain the old pair.
UI_MODEL_FILES = ("apps/standalone/UiModel.h", "apps/standalone/UiModel.cpp")
RECALL_SOURCE_TRANSITION = "ui-model-recall-controls-a26-v1"
RECALL_SOURCE_PATCH = SESSION + "/reports/UiModel-recall-controls.patch"
RECALL_SOURCE_PATCH_SHA256 = "d4fadc8ae85d9f3dd2aedb6cccc63977fe1c4516dcca47b758a0ec18c7792cf8"
RECALL_SOURCE_SHA256 = {
    "apps/standalone/UiModel.h": "34337e5db254bfbc4e23ee4fadf76ecc8fe792f003bd13ab5b54d0a302b5bb15",
    "apps/standalone/UiModel.cpp": "b4889e0b5d1b6eb0b88b140b8af92815df4bf021158a902994db2c15ed798986",
}
RECALL_SOURCE_INSERTIONS = {
    "apps/standalone/UiModel.h": b"""    // Named-library recall validates and emits one copied whole ControlSnapshot
    // even when unchanged. Unlike legacy file Load, it retains the clean-file
    // reference. Invalid input emits nothing and preserves state. Presentation
    // and held-note owners are preserved; normal submission/observation applies.
    [[nodiscard]] UiActions recall_controls(const ControlSnapshot& controls) noexcept;
""",
    "apps/standalone/UiModel.cpp": b"""UiActions UiModel::recall_controls(const ControlSnapshot& controls) noexcept {
    if (!is_valid_control_snapshot(controls)) return {};
    return publish_controls(view_, saved_controls_, pending_control_sequence_, controls, true);
}

""",
}
SDL_PINNED = {
    "src/render/SDL_render.c": "ae904d0fd11c6122c77d78909538b26694b4d57a9b6b722c51e0417d4709be54",
    "src/render/software/SDL_render_sw.c": "2e3bbc7ab7d6d59310c634d6374eabb60da185d8c7cfc8526baa45318e6d3257",
    "src/video/SDL_surface.c": "e2c324858b829a0afebc0ce04c983178347c24adb08d9738118c06fc39f3bbf5",
    "src/video/SDL_stretch.c": "235f4c58830d1d7f0efc5a6b13f22838eccf04aa1c653f37534af2c6c7356a4b",
}
PATCHES = dict(zip(
    ("TL", "L", "LB", "CL", "DIVL", "CT", "CR", "BL", "BC", "RM", "RB", "RT"),
    ((110, 134, 96, 9), (100, 165, 48, 64), (100, 233, 48, 14),
     (505, 166, 32, 68), (535, 166, 12, 72), (580, 134, 96, 9),
     (576, 169, 12, 69), (98, 250, 112, 6), (580, 250, 128, 6),
     (1074, 165, 16, 70), (944, 242, 40, 12), (988, 134, 96, 9)), strict=True))
MEAN_LIMIT = Fraction(6324946007329, 2837721600000)
RMS_LIMIT = 0.6968632531987865
MAX_HEADER = 2 * 1024 * 1024
MAX_WIDTH, MAX_HEIGHT = 3866, 2194
MAX_PIXELS = MAX_WIDTH * MAX_HEIGHT
MAX_STREAM = MAX_HEADER + 1 + 4 * MAX_PIXELS
MAX_STDERR = 64 * 1024
MAX_REPORT = 16 * 1024 * 1024
MAX_FILES, MAX_STORAGE = 160, 2 * 1024**3
MAX_COMMANDS, MAX_TOTAL_SECONDS, MAX_COMMAND_SECONDS = 70, 1800, 120
MAX_INPUT_BYTES, MAX_DIAGNOSTIC = 512 * 1024**2, 4096
INCOMING = [17, 23, 31, 127]
CYAN = [165, 228, 223, 255]
BRASS, IVORY, DARK = [214, 182, 124, 255], [242, 231, 207, 255], [33, 28, 21, 255]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def identity(path):
    path = Path(path).resolve(strict=True)
    require(path.is_file(), "input is not a regular file: " + str(path))
    require(path.stat().st_size <= MAX_INPUT_BYTES, "input identity file exceeds byte limit")
    digest, length = hashlib.sha256(), 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
            length += len(chunk)
            require(length <= MAX_INPUT_BYTES, "input grew beyond identity byte limit")
    return {"path": str(path), "bytes": length, "sha256": digest.hexdigest()}


def strict_json(data):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON key: " + key)
            result[key] = value
        return result

    def number(text):
        value = float(text)
        require(math.isfinite(value), "nonfinite JSON number")
        return value

    def invalid(text):
        raise ValueError("nonfinite JSON constant: " + text)

    require(len(data) <= MAX_REPORT, "JSON exceeds fixed parser limit")
    return json.loads(data.decode("utf-8") if isinstance(data, bytes) else data,
                      object_pairs_hook=pairs, parse_float=number, parse_constant=invalid)


def json_bytes(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def equal(a, b):
    """Numerical JSON equivalence, with booleans distinct from integer 0/1."""
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return a == b and math.isfinite(a) and math.isfinite(b)
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(equal(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(equal(x, y) for x, y in zip(a, b))
    return a == b


def f32(value):
    return struct.unpack("=f", struct.pack("=f", value))[0]


def add(a, b):
    return f32(a + b)


def sub(a, b):
    return f32(a - b)


def mul(a, b):
    return f32(a * b)


def div(a, b):
    return f32(a / b)


def vector32(actual, expected):
    return (isinstance(actual, list) and len(actual) == len(expected) and
            all(type(a) in (float, int) and math.isfinite(a) and
                struct.pack("=f", a) == struct.pack("=f", b) for a, b in zip(actual, expected)))


def rect_edges(rect):
    x, y, w, h = rect
    return [x, y, x + w, y + h]


def xywh(box):
    x, y, r, b = box
    return [x, y, max(0, r - x), max(0, b - y)]


def intersection(*boxes):
    x, y = max(b[0] for b in boxes), max(b[1] for b in boxes)
    return [x, y, max(x, min(b[2] for b in boxes)), max(y, min(b[3] for b in boxes))]


def area(box):
    return max(0, box[2] - box[0]) * max(0, box[3] - box[1])


def translated(box, origin):
    return [box[0] + origin[0], box[1] + origin[1], box[2] + origin[0], box[3] + origin[1]]


def scale_for(spec):
    sx, sy = div(spec["logical_size"][0], 1672), div(spec["logical_size"][1], 941)
    return [sx, sy, min(sx, sy)]


def mapped(spec, rect):
    sx, sy, _ = scale_for(spec)
    x, y, w, h = rect
    left, top = mul(x, sx), mul(y, sy)
    return [left, top, sub(mul(add(x, w), sx), left), sub(mul(add(y, h), sy), top)]


def panel_inset(spec):
    panel = mapped(spec, [72, 125, 1044, 139])
    sx, sy, _ = scale_for(spec)
    dx, dy = mul(4, sx), mul(4, sy)
    return panel, [add(panel[0], dx), add(panel[1], dy),
                   max(0., sub(panel[2], mul(2, dx))), max(0., sub(panel[3], mul(2, dy)))]


def intrinsic_box(spec):
    _, (x, y, w, h) = panel_inset(spec)
    rx, ry = spec["scale"]
    return [math.ceil(x * rx - .5), math.ceil(y * ry - .5),
            math.ceil((x + w) * rx - .5), math.ceil((y + h) * ry - .5)]


def visible_box(spec):
    result = intersection([0, 0, *spec["output_size"]], rect_edges(spec["viewport_request"]))
    if spec["requested_clip_enabled"]:
        result = intersection(result, translated(rect_edges(spec["clip_request"]), spec["origin"]))
    return result


def support_box(spec):
    if not spec["eligible_p1"]:
        return [0, 0, 0, 0]
    return intersection(translated(intrinsic_box(spec), spec["origin"]), visible_box(spec))


def scenarios():
    """Literal independent contract inventory; no exported geometry is an input."""
    items = []
    for index in range(24):
        s = dict(case=index, id=f"main-{index}", kind="main", source_main=index,
                 logical_size=[1672, 941], scale=[1., 1.], origin=[0, 0],
                 clip_kind="disabled", route="B", expression=.625, pedal_levels=[3, 7],
                 percussion=[True, 0, 0, 0], requested_play_focus=[4, 0, 1, 4],
                 blend=1, workspace=0, presentation=0, resource_crop=False)
        items.append(s)
    for i, wh in enumerate(([1400, 820], [1920, 1080], [1920, 820], [1400, 1080]), 1):
        items[i]["logical_size"] = wh
        items[i]["requested_play_focus"] = [6, 0, 0, i - 1]
        items[i]["percussion"][i - 1] = False if i == 1 else 1
    items[5].update(scale=[1.5, 1.5], origin=[13, 17], expression=0., requested_play_focus=[7, 0, 0, 0])
    items[6].update(scale=[2., 2.], origin=[-13, -17], pedal_levels=[0, 8], requested_play_focus=[5, 0, 0, 0])
    items[7].update(scale=[1.25, .75], origin=[13, -17], blend=0, requested_play_focus=[5, 0, 0, 1])
    items[8]["scale"][0], items[9]["scale"][1] = f32(2.01), f32(2.01)
    for i, (sc, org, edge) in enumerate((([1.5, 1.5], [13, 17], "left"),
                                       ([2., 2.], [-13, 17], "right"),
                                       ([1.25, .75], [-13, -17], "top"),
                                       ([1., 1.], [13, -17], "bottom")), 10):
        items[i].update(scale=sc, origin=org, clip_kind=edge)
    items[14]["clip_kind"], items[15]["clip_kind"] = "empty", "disjoint"
    items[16].update(logical_size=[8192, 8192], scale=[2., 2.], resource_crop=True)
    b = intrinsic_box(items[16])
    items[16]["origin"] = [-b[0], -b[1]]
    for i, wh in enumerate(([1399, 820], [1400, 819], [960, 700], [1280, 900]), 17):
        items[i]["logical_size"] = wh
    items[21]["presentation"], items[22]["workspace"], items[23]["workspace"] = 1, 1, 2
    for i, original in enumerate((10, 11, 12, 13, 15), 24):
        items.append({**items[original], "case": i, "id": f"uncut-{original}",
                      "kind": "uncut-companion", "source_main": original, "clip_kind": "disabled"})
    for i, name, kind in ((29, "repeat-after-all-0", "after-all"), (30, "repeat-fresh-0", "fresh")):
        items.append({**items[0], "case": i, "id": name, "kind": kind})
    for i, name, route in ((31, "upper-applied-A", "A"), (32, "upper-cancelled", "Cancel"), (33, "upper-fixed-D", "D")):
        items.append({**items[0], "case": i, "id": name, "kind": "eligibility-witness", "route": route})
    for s in items:
        w, h = s["logical_size"]
        rx, ry = s["scale"]
        ox, oy = s["origin"]
        vw, vh = math.ceil(mul(w, rx)), math.ceil(mul(h, ry))
        s["viewport_request"] = [ox, oy, vw, vh]
        s["output_size"] = [64, 64] if s["resource_crop"] else [vw + 2 * abs(ox), vh + 2 * abs(oy)]
        s["active_reference"] = s["workspace"] == 0 and s["presentation"] == 0 and 1400 <= w <= 8192 and 820 <= h <= 8192
        s["eligible_p1"] = s["active_reference"] and 0 < rx <= 2 and 0 < ry <= 2
        s["independent_panel"], s["independent_inset"] = panel_inset(s)
        left, top, right, bottom = intrinsic_box(s)
        s["intrinsic_inset"] = [left, top, right - left, bottom - top]
        clips = {"disabled": [0, 0, 0, 0], "left": [left - 2, top - 2, 4, bottom - top + 4],
                 "right": [right - 2, top - 2, 4, bottom - top + 4],
                 "top": [left - 2, top - 2, right - left + 4, 4],
                 "bottom": [left - 2, bottom - 2, right - left + 4, 4],
                 "empty": [left, top, 0, 0], "disjoint": [right + 4, top + 4, 8, 8]}
        s["clip_request"] = clips[s["clip_kind"]]
        s["requested_clip_enabled"] = s["clip_kind"] != "disabled"
        s["clip_space"] = "physical-at-scale-one"
        s["route_index"] = {"B": 11, "A": 10, "Cancel": 0, "D": 2}[s["route"]]
        s.update(lower_route="B", edited_banks=["B", "B"], pending=False, drawbar_level=4)
        s["paired_whole_frame_equality_required"] = not s["eligible_p1"] or s["clip_kind"] in ("empty", "disjoint")
    return items


def parse_frame(payload, index):
    require(len(payload) <= MAX_STREAM, "oversized frame stream")
    end = payload.find(b"\n", 0, MAX_HEADER)
    require(end >= 0 and end + 1 < MAX_HEADER, "missing bounded single-line JSON header")
    header = strict_json(payload[:end])
    require(type(header) is dict and type(header.get("schema")) is int and header["schema"] == 1, "wrong frame schema")
    require(header.get("protocol") == PROTOCOL, "wrong frame protocol")
    require(type(header.get("case")) is int and header["case"] == index, "wrong frame index")
    w, h = header.get("width"), header.get("height")
    require(type(w) is type(h) is int and 0 < w <= MAX_WIDTH and 0 < h <= MAX_HEIGHT, "unbounded frame dimensions")
    require(type(header.get("bytes")) is int and header["bytes"] == w * h * 4, "invalid declared RGBA byte count")
    require(header.get("pixel_format") == "RGBA8" and header.get("row_order") == "top-to-bottom", "wrong pixel packing")
    require(type(header.get("row_stride")) is int and header["row_stride"] == w * 4, "invalid RGBA row stride")
    rgba = payload[end + 1:]
    require(len(rgba) == header["bytes"], "truncated RGBA or forbidden trailing bytes")
    return header, rgba


def patch_measure(rgba, width, height, rect):
    x0, y0, w, h = rect
    require(len(rgba) == width * height * 4 and w > 1 and h > 1 and
            0 <= x0 < x0 + w <= width and 0 <= y0 < y0 + h <= height, "invalid numerical patch")
    rgb, sums = bytearray(), [0, 0, 0]
    zsum = zsq = xz = yz = xx = yy = 0
    for y in range(h):
        dy = 2 * y - (h - 1)
        start = ((y0 + y) * width + x0) * 4
        for x in range(w):
            at = start + x * 4
            r, g, b = rgba[at:at + 3]
            rgb.extend((r, g, b))
            sums[0] += r; sums[1] += g; sums[2] += b
            z = 2126 * r + 7152 * g + 722 * b
            dx = 2 * x - (w - 1)
            zsum += z; zsq += z * z; xz += dx * z; yz += dy * z
            xx += dx * dx; yy += dy * dy
    n = w * h
    residual = (Fraction(zsq) - Fraction(zsum * zsum, n) - Fraction(xz * xz, xx) - Fraction(yz * yz, yy)) / (n * 10**8)
    require(residual >= 0, "negative exact affine residual")
    mean = Fraction(zsum, n * 10000)
    return {"rect": list(rect), "pixels": n, "rgb_sum": sums,
            "rgb_mean": [v / n for v in sums], "luma_numerator_sum": zsum,
            "luma_mean_ratio": [mean.numerator, mean.denominator], "luma_mean": float(mean),
            "plane_sufficient_sums": dict(z_sum=zsum, z_square_sum=zsq, x2_z_sum=xz, y2_z_sum=yz,
                                          x2_square_sum=xx, y2_square_sum=yy),
            "residual_mean_square_ratio": [residual.numerator, residual.denominator],
            "residual_rms": math.sqrt(float(residual)), "decoded_rgb_sha256": sha(rgb)}


def exact_values(record):
    n = record["pixels"]
    require(type(n) is int and n > 0, "invalid sufficient-statistic population")
    s = record["plane_sufficient_sums"]
    require(all(type(v) is int for v in s.values()) and s["x2_square_sum"] > 0 and s["y2_square_sum"] > 0,
            "invalid exact sufficient sums")
    q = (Fraction(s["z_square_sum"]) - Fraction(s["z_sum"]**2, n) -
         Fraction(s["x2_z_sum"]**2, s["x2_square_sum"]) - Fraction(s["y2_z_sum"]**2, s["y2_square_sum"])) / (n * 10**8)
    require(q >= 0 and q == Fraction(*record["residual_mean_square_ratio"]), "contradictory exact residual ratio")
    mean = Fraction(s["z_sum"], n * 10000)
    require(mean == Fraction(*record["luma_mean_ratio"]) and s["z_sum"] == record["luma_numerator_sum"], "contradictory mean")
    require(record["luma_numerator_sum"] == sum(a * b for a, b in zip((2126, 7152, 722), record["rgb_sum"])), "RGB/luma disagreement")
    rms = math.sqrt(float(q))
    require(rms == record["residual_rms"], "incorrect once-converted binary64 residual RMS")
    return mean, [Fraction(v, n) for v in record["rgb_sum"]], rms


def numerical_screens(measures, reference):
    checks, mean_errors, rms_errors = [], [], []
    for name in PATCHES:
        y, rgb, rms = exact_values(measures[name])
        ry, rrgb, rrms = exact_values(reference[name])
        err, rerr = abs(y - ry), abs(rms - rrms)
        mean_errors.append(err); rms_errors.append(rerr)
        values = [("Ymean", err, Fraction(3)), *[(c + "mean", abs(a - b), Fraction(4))
                   for c, a, b in zip("RGB", rgb, rrgb)], ("RMS", rerr, 1.2)]
        for kind, difference, limit in values:
            record = {"id": name + ":" + kind, "difference": float(difference),
                      "limit": float(limit), "pass": difference <= limit}
            if isinstance(difference, Fraction):
                record["difference_ratio"] = [difference.numerator, difference.denominator]
            checks.append(record)
    yerror = sum(mean_errors, Fraction()) / 12
    rmserror = math.fsum(rms_errors) / 12.0
    checks.extend((dict(id="aggregate:Ymean", difference=float(yerror),
                        difference_ratio=[yerror.numerator, yerror.denominator], limit=float(MEAN_LIMIT),
                        limit_ratio=[MEAN_LIMIT.numerator, MEAN_LIMIT.denominator], **{"pass": yerror <= MEAN_LIMIT}),
                   dict(id="aggregate:RMS", difference=rmserror, limit=RMS_LIMIT, **{"pass": rmserror <= RMS_LIMIT})))
    passed = sum(c["pass"] for c in checks)
    return {"checks": checks, "passed": passed, "failed": len(checks) - passed, "total": len(checks),
            "all_passed": passed == 62}


def frozen_references(root):
    report = strict_json((root / AUTHORING).read_bytes())
    require(report["primary_patch_order"] == list(PATCHES), "frozen patch order differs")
    reference, baseline = {}, {}
    for name, rect in PATCHES.items():
        reference[name] = report["patches"][name]["reference"]
        baseline[name] = report["patches"][name]["native_t3_before"]
        for row in (reference[name], baseline[name]):
            require(row["rect"] == list(rect) and row["pixels"] == rect[2] * rect[3], "frozen patch domain differs")
            exact_values(row)
    require(Fraction(*report["frozen_criteria"]["mean_mae_max_ratio"]) == MEAN_LIMIT and
            report["frozen_criteria"]["residual_rms_mae_max"] == RMS_LIMIT, "frozen aggregate limits differ")
    screens = numerical_screens(baseline, reference)
    require((screens["passed"], screens["failed"], screens["total"]) == (28, 34, 62), "historical 28/34 screen count differs")
    for actual, recorded in zip(screens["checks"], report["baseline_numerical_screens"]["checks"], strict=True):
        require(actual["id"] == recorded["id"] and actual["pass"] == recorded["pass"] and actual["limit"] == recorded["limit"],
                "historical screen identity/decision differs")
    return reference, baseline, screens


def font_atlases(path):
    source = Path(path).read_text(encoding="utf-8")
    result = {}
    for name, pixel_height, ascent in (("Sans", 32, 30), ("Serif", 40, 38)):
        block = source.split("k" + name + "Glyphs{{", 1)[1].split("}};", 1)[0]
        rows = re.findall(r"\{(-?\d+(?:,\s*-?\d+){6})\},\s*// ASCII (\d+)", block)
        glyphs = {chr(int(code)): tuple(map(int, fields.split(","))) for fields, code in rows}
        require(set(glyphs) == {chr(c) for c in range(32, 127)}, "incomplete font metrics")
        block = source.split("k" + name + "AlphaRle{{", 1)[1].split("}};", 1)[0]
        encoded = [int(v) for v in re.findall(r"\d+", block)]
        require(len(encoded) % 2 == 0, "incomplete font RLE pair")
        alpha = bytearray()
        for count, value in zip(encoded[::2], encoded[1::2], strict=True):
            require(0 < count <= 255 and 0 <= value <= 255 and len(alpha) + count <= 512 * 256, "invalid font RLE")
            alpha.extend(bytes([value]) * count)
        require(len(alpha) == 512 * 256, "incomplete font RLE output")
        result[name] = dict(glyphs=glyphs, alpha=bytes(alpha), pixel_height=pixel_height, ascent=ascent)
    return result


def text_width(text, size, atlas):
    scale, width = div(size, atlas["pixel_height"]), 0.
    for char in text:
        width = add(width, div(mul(atlas["glyphs"][char][6], scale), 64))
    return width


def text_copies(run, atlas):
    x, top, size = run["text_arguments"]
    scale = div(size, atlas["pixel_height"])
    baseline = add(top, mul(atlas["ascent"], scale))
    result = []
    for char in run["text"]:
        ax, ay, w, h, bx, by, advance = atlas["glyphs"][char]
        if w and h:
            px, py = (2 if mul(w, scale) < 1 else 0), (2 if mul(h, scale) < 1 else 0)
            result.append(([ax - px, ay - py, w + 2 * px, h + 2 * py],
                           [add(x, mul(bx - px, scale)), add(baseline, mul(by - py, scale)),
                            mul(w + 2 * px, scale), mul(h + 2 * py, scale)]))
        x = add(x, div(mul(advance, scale), 64))
    return result


def destination_envelope(spec, rect):
    x, y, w, h = [mul(a, b) for a, b in zip(rect, spec["scale"] * 2)]
    left, top = math.floor(x), math.floor(y)
    return [left + spec["origin"][0], top + spec["origin"][1], math.ceil(x + w) - left, math.ceil(y + h) - top]


def primitive_box(spec, rect, fill):
    x, y, w, h = [math.trunc(mul(a, b)) for a, b in zip(rect, spec["scale"] * 2)]
    x += spec["origin"][0]; y += spec["origin"][1]
    if rect[2] <= 0 or rect[3] <= 0 or (not fill and (w <= 0 or h <= 0)):
        return [x, y, x, y]
    return [x, y, x + max(w, 1), y + max(h, 1)]


def positions_to_spans(positions, width):
    spans = []
    for at in sorted(positions):
        y, x = divmod(at, width)
        if spans and spans[-1][0] == y and spans[-1][2] == x:
            spans[-1][2] += 1
        else:
            spans.append([y, x, x + 1])
    return spans


def spans_for_regions(spec, regions):
    width = spec["output_size"][0]
    positions = set()
    visible = visible_box(spec)
    for region in regions:
        x, y, r, b = intersection(primitive_box(spec, region, True), visible)
        for row in range(y, b):
            positions.update(range(row * width + x, row * width + r))
    return positions_to_spans(positions, width)


def span_count(spans):
    return sum(end - first for _, first, end in spans)


def round_away(value):
    return math.floor(value + .5) if value >= 0 else math.ceil(value - .5)


def sampler_axis(source, destination):
    step = (source << 16) // destination
    first = (step + 1) // 2 - 32768
    result = []
    for i in range(destination):
        fixed = first + i * step
        if fixed < 0:
            result.append((0, 0, 0))
        elif fixed >> 16 > source - 2:
            result.append((source - 1, source - 1, 0))
        else:
            result.append((fixed >> 16, (fixed >> 16) + 1, (fixed >> 9) & 127))
    return result


def glyph_core_positions(spec, source, target, atlas):
    """Opaque COPY cores, including SDL clip-induced source resampling.

    A destination crossing the output first uses a fully scaled intermediate.
    Otherwise SDL_PrivateUpperBlitScaled rounds the clipped source separately.
    The two-stage linear filter rounds vertically, then horizontally, at 7 bits.
    These operations are independent of native export spans and candidate RGB.
    """
    destination = primitive_box(spec, target, False)
    clipped = intersection(destination, visible_box(spec))
    if not area(clipped):
        return set()
    ax, ay, sw, sh = source
    dx, dy, dr, db = destination
    dw, dh = dr - dx, db - dy
    require(0 < dw <= 16384 and 0 < dh <= 16384, "unbounded glyph destination")
    intermediate = destination != intersection(destination, [0, 0, *spec["output_size"]])
    unscaled = (sw, sh) == (dw, dh)
    if unscaled:
        ax += clipped[0] - dx; ay += clipped[1] - dy
        sw, sh = clipped[2] - clipped[0], clipped[3] - clipped[1]
        sample_box = clipped
    elif intermediate:
        sample_box = destination
    else:
        rw, rh = dw / sw, dh / sh
        x0, y0 = ax + (clipped[0] - dx) / rw, ay + (clipped[1] - dy) / rh
        x1, y1 = ax + sw - (dr - clipped[2]) / rw, ay + sh - (db - clipped[3]) / rh
        ax, ay, sw, sh = round_away(x0), round_away(y0), round_away(x1 - x0), round_away(y1 - y0)
        sample_box = clipped
    dw, dh = sample_box[2] - sample_box[0], sample_box[3] - sample_box[1]
    if min(sw, sh, dw, dh) <= 0:
        return set()
    require(0 <= ax < ax + sw <= 512 and 0 <= ay < ay + sh <= 256, "glyph source outside frozen atlas")
    alpha, width, result = atlas["alpha"], spec["output_size"][0], set()
    xx = sampler_axis(sw, dw) if not unscaled else None
    yy = sampler_axis(sh, dh) if not unscaled else None
    for y in range(clipped[1], clipped[3]):
        sy = y - sample_box[1]
        for x in range(clipped[0], clipped[2]):
            sx = x - sample_box[0]
            if unscaled:
                value = alpha[(ay + sy) * 512 + ax + sx]
            else:
                y0, y1, fy = yy[sy]
                x0, x1, fx = xx[sx]
                a = (alpha[(ay + y0) * 512 + ax + x0] * (128 - fy) + alpha[(ay + y1) * 512 + ax + x0] * fy) >> 7
                b = (alpha[(ay + y0) * 512 + ax + x1] * (128 - fy) + alpha[(ay + y1) * 512 + ax + x1] * fy) >> 7
                value = (a * (128 - fx) + b * fx) >> 7
            if value == 255:
                result.add(y * width + x)
    return result


def literal_text(spec, atlases, name, value, box, size, face, color, padding):
    sx, _, factor = scale_for(spec)
    requested, padding = mul(size, factor), mul(padding, sx)
    atlas = atlases[face]
    actual = min(requested, div(box[3], f32(1.2)))
    measured = text_width(value, actual, atlas)
    available = sub(box[2], mul(2, padding))
    if measured > available and measured > 0:
        actual = mul(actual, div(max(f32(.1), available), measured))
    x = add(box[0], div(sub(box[2], text_width(value, actual, atlas)), 2))
    top = add(box[1], div(sub(box[3], mul(actual, f32(1.2))), 2))
    run = dict(id=name, text=value, box=box, requested_size=requested, padding=padding,
               face=face, color=color, text_arguments=[x, top, actual])
    copies = text_copies(run, atlas)
    run["glyph_destinations"] = [destination_envelope(spec, target) for _, target in copies]
    cores = set()
    for source, target in copies:
        cores.update(glyph_core_positions(spec, source, target, atlas))
    run["opaque_spans"] = positions_to_spans(cores, spec["output_size"][0])
    run["opaque_pixels"] = len(cores)
    return run


def performance_controls(spec):
    result = {}
    for i, left in enumerate((164, 418, 256, 337)):
        result[(6, 0, 0, i)] = dict(bounds=mapped(spec, [left, 177, 74, 52]),
                                   label_bounds=mapped(spec, [left - 2, 233, 78, 14]),
                                   value_bounds=mapped(spec, [left + 5, 183, 64, 38]), track=[0., 0., 0., 0.])
    result[(7, 0, 0, 0)] = dict(bounds=mapped(spec, [578, 165, 254, 85]),
                               label_bounds=mapped(spec, [582, 165, 246, 16]),
                               value_bounds=mapped(spec, [582, 232, 246, 16]), track=mapped(spec, [594, 200, 222, 4]))
    for i in range(2):
        left = 850 + 128 * i
        result[(5, 0, 0, i)] = dict(bounds=mapped(spec, [left, 165, 112, 85]),
                                   label_bounds=mapped(spec, [left + 4, 165, 104, 16]),
                                   value_bounds=mapped(spec, [left + 74, 200, 32, 40]),
                                   track=mapped(spec, [left + 41, 193, 4, 43]))
    result[(4, 0, 1, 4)] = dict(bounds=mapped(spec, [328, 309, 46, 197]),
                               label_bounds=mapped(spec, [328, 467, 46, 23]),
                               value_bounds=mapped(spec, [328, 491, 46, 15]), track=mapped(spec, [349, 327, 4, 118]))
    return result


def expected_witnesses(spec, atlases):
    result = dict(full_required=False, opaque_probes=[], text_runs=[],
                  focus=dict(id=[0, 0, 0, 0], bounds=[0, 0, 0, 0], logical_regions=[], color=CYAN,
                             expected_pixels=0, actual_pixels=0, expected_spans=[], actual_spans=[]))
    if not spec["active_reference"]:
        return result
    result["full_required"] = not spec["requested_clip_enabled"] and not spec["resource_crop"]
    sx, sy, factor = scale_for(spec)
    controls = performance_controls(spec)

    def text(name, value, box, size, face, color, padding):
        result["text_runs"].append(literal_text(spec, atlases, name, value, box, size, face, color, padding))

    def probe(name, region):
        spans = spans_for_regions(spec, [region])
        result["opaque_probes"].append(dict(id=name, logical_regions=[region], spans=spans, pixels=span_count(spans)))

    for name, value, nominal, size in (("percussion-heading", "PERCUSSION", [90, 136, 448, 26], 15),
                                      ("expression-heading", "NOMINAL EXPRESSION / PEDAL MIXTURES", [578, 136, 514, 26], 14)):
        box = mapped(spec, nominal)
        text(name, value, box, size, "Serif", BRASS, 3)
        gap = add(div(text_width(value, mul(size, factor), atlases["Serif"]), 2), mul(14, sx))
        middle, y = add(box[0], div(box[2], 2)), add(box[1], div(box[3], 2))
        probe(name + "-rule-left", [add(box[0], mul(9, sx)), y, sub(sub(sub(middle, gap), box[0]), mul(9, sx)), sy])
        probe(name + "-rule-right", [add(middle, gap), y, sub(sub(sub(add(box[0], box[2]), mul(9, sx)), middle), gap), sy])
    upper_b = spec["route"] == "B"
    text("eligibility", "UPPER B ROUTE ACTIVE" if upper_b else "REQUIRES UPPER B", mapped(spec, [90, 248, 448, 14]),
         12, "Sans", [157, 187, 143, 255] if upper_b else [166, 159, 142, 255], 3)
    settings = spec["percussion"]
    values = ["ON" if settings[0] else "OFF", "2ND" if settings[1] == 0 else "3RD",
              "NORM" if settings[2] == 0 else "SOFT", "SLOW" if settings[3] == 0 else "FAST"]
    for i, label in enumerate(("PERC", "HARM", "VOL", "DECAY")):
        g = controls[(6, 0, 0, i)]; b = g["bounds"]
        text(f"percussion-{i}-label", label, g["label_bounds"], 13.5, "Serif", IVORY, 3)
        text(f"percussion-{i}-value", values[i], g["value_bounds"], 20, "Serif", DARK, 3)
        probe(f"percussion-{i}-cap", [add(b[0], mul(12, sx)), add(b[1], mul(44, sy)), mul(50, sx), mul(2, sy)])
    g = controls[(7, 0, 0, 0)]; track = g["track"]
    text("expression-label", "NOMINAL EXPRESSION", g["label_bounds"], 10.5, "Sans", IVORY, 3)
    text("expression-value", str(round_away(spec["expression"] * 100)) + "%", g["value_bounds"], 11.5, "Sans", BRASS, 3)
    handle = add(track[0], mul(f32(spec["expression"]), track[2]))
    probe("expression-track", [add(track[0], mul(100 if spec["expression"] < .5 else 10, sx)), add(track[1], sy), mul(80, sx), sy])
    probe("expression-handle", [sub(handle, mul(3, sx)), sub(track[1], mul(3, sy)), mul(6, sx), mul(6, sy)])
    for i, level in enumerate(spec["pedal_levels"]):
        g = controls[(5, 0, 0, i)]; t = g["track"]
        text(f"pedal-{i}-label", "MIX " + str(i + 1), g["label_bounds"], 11, "Sans", IVORY, 2)
        text(f"pedal-{i}-value", str(level), g["value_bounds"], 13, "Sans", BRASS, 3)
        center, position = add(t[0], div(t[2], 2)), add(t[1], div(mul(t[3], level), 8))
        probe(f"pedal-{i}-track", [sub(center, mul(20, sx)), add(t[1], mul(3, sy)), mul(2, sx), sub(t[3], mul(6, sy))])
        probe(f"pedal-{i}-cap", [sub(center, mul(12, sx)), sub(position, mul(4, sy)), mul(24, sx), mul(3, sy)])
    probe("divider", mapped(spec, [556, 145, 1, 100]))
    p, _ = panel_inset(spec)
    for row, y in enumerate((add(p[1], mul(7, sy)), sub(add(p[1], p[3]), mul(13, sy)))):
        for column, x in enumerate((add(p[0], mul(7, sx)), sub(add(p[0], p[2]), mul(13, sx)))):
            probe(f"screw-{row}-{column}", [add(x, mul(2, sx)), add(y, mul(2, sy)), mul(2, sx), mul(2, sy)])
    focus = spec["requested_play_focus"]
    b = controls[tuple(focus)]["bounds"]
    tx, ty = min(mul(2, sx), div(b[2], 2)), min(mul(2, sy), div(b[3], 2))
    regions = [[b[0], b[1], b[2], ty], [b[0], sub(add(b[1], b[3]), ty), b[2], ty],
               [b[0], add(b[1], ty), tx, sub(b[3], mul(2, ty))],
               [sub(add(b[0], b[2]), tx), add(b[1], ty), tx, sub(b[3], mul(2, ty))]]
    spans = spans_for_regions(spec, regions)
    result["focus"] = dict(id=focus, bounds=b, logical_regions=regions, color=CYAN,
                           expected_pixels=span_count(spans), actual_pixels=span_count(spans),
                           expected_spans=spans, actual_spans=spans)
    require(len(result["opaque_probes"]) == 19 and len(result["text_runs"]) == 17, "independent witness inventory incomplete")
    return result


class Audit:
    """Keep every evaluated failure; structural failures block only dependents."""
    def __init__(self):
        self.checks = 0
        self.failures = []

    def check(self, condition, label, detail=None):
        self.checks += 1
        if not condition:
            record = {"check": label}
            if detail is not None:
                record["detail"] = (detail[:MAX_DIAGNOSTIC] + f" [truncated {len(detail) - MAX_DIAGNOSTIC} characters; raw input retained]"
                                    if isinstance(detail, str) and len(detail) > MAX_DIAGNOSTIC else detail)
            self.failures.append(record)
        return bool(condition)

    def guard(self, label, function):
        try:
            return function()
        except (ValueError, KeyError, TypeError, IndexError, OverflowError, OSError, RecursionError) as error:
            self.check(False, label, f"{type(error).__name__}: {error}")
            return None


FIXED_INFO = dict(audio_running=True, sample_rate=48000, buffer_frames=512,
                  audio_driver="fixed-software-fixture", device_name="fixed copied state",
                  status_message="Frozen performance plate qualification", clipped_samples=0,
                  overlay=0, audio_choices=[], selected_device=0, selected_sample_rate=48000,
                  selected_buffer_frames=512, midi_available=False, midi_open=False, midi_backend="",
                  midi_port="", midi_status="", midi_choices=[], selected_midi_port=0,
                  selected_midi_channels=[1, 2, 3], selected_midi_expression=[0, 127, False],
                  active_midi_expression=[0, 127, False], midi_expression_active=False,
                  midi_reconnect_pending=False, midi_messages=0, inspection=None)
VIEW_KEYS = {"controls", "applied", "edited_banks", "focus", "roving_manual_keys", "roving_pedal_key",
             "keyboard_target", "manual_base_midi", "pedal_octave", "controls_pending", "controls_dirty",
             "text_entry_active", "pointer_captured", "input_recovery", "last_submit_status", "workspace",
             "presentation", "workspace_focus"}
LAYOUT_KEYS = {"width", "height", "show_cabinet", "bank_controls_in_cheeks", "sidebar_pedals", "header",
               "registration_panels", "performance_panel", "keyboard_toolbar", "manual_panels", "pedal_panel",
               "footer", "cabinet_panel", "cabinet_art", "manual_rail_panels", "control_count", "controls",
               "manual_keys", "pedal_keys", "preset_key_panels", "workspace", "presentation", "workspace_panel"}
TRANSFORM_KEYS = {"scale", "viewport", "clip", "logical_viewport", "logical_clip", "clip_enabled", "blend", "draw_color"}
FRAME_EXTRA = {"schema", "protocol", "width", "height", "pixel_format", "row_order", "row_stride",
               "renderer_before", "renderer_after", "model_before", "model_after", "session_before", "session_after",
               "hit_before", "hit_after", "info", "backend", "helper_probe", "witnesses", "checks",
               "visible_clip_pixels", "quiet_clip_pixels", "history_states", "bytes"}


def expected_session(spec):
    controls = dict(drawbars=[[[4] * 9 for _ in range(2)] for _ in range(2)],
                    selected_banks=[0 if spec["route"] == "A" else 1, 1],
                    route_enabled=[0 if spec["route"] == "Cancel" else 1, 1], expression=spec["expression"],
                    percussion=spec["percussion"], pedal_drawbars=spec["pedal_levels"],
                    fixed_registrations=[2 if spec["route"] == "D" else 0, 0])
    return dict(controls=controls, held_keys=[[i == 24 for i in range(61)], [i == 36 for i in range(61)]],
                held_pedals=[i == 12 for i in range(25)], frame_clock=38400, sample_rate=48000, peak=.125,
                prepared=True, running=True, publication_revision=4, resolved_sequence=0, last_applied_sequence=0,
                recovery_count=0, queue_overflows=0, rejected_commands=0, discarded_commands=0, fault_flags=0, last_core_status=0)


def finite_vector(value, length):
    return isinstance(value, list) and len(value) == length and all(type(v) in (int, float) and math.isfinite(v) for v in value)


def integer_vector(value, length):
    return isinstance(value, list) and len(value) == length and all(type(v) is int for v in value)


def validate_transform(spec, record, color=None):
    require(type(record) is dict and set(record) == TRANSFORM_KEYS, "incomplete renderer record")
    require(vector32(record["scale"], spec["scale"]), "renderer scale mismatch")
    for name, field in (("viewport", "viewport_request"), ("clip", "clip_request")):
        require(equal(record[name], spec[field]), "physical " + name + " mismatch")
        logical = [math.floor(v / s) for v, s in zip(spec[field], spec["scale"] * 2)]
        require(equal(record["logical_" + name], logical), "logical " + name + " mismatch")
    require(record["clip_enabled"] is spec["requested_clip_enabled"] and equal(record["blend"], spec["blend"]), "clip enable/blend mismatch")
    require(integer_vector(record["draw_color"], 4) and all(0 <= c <= 255 for c in record["draw_color"]), "invalid draw color")
    if color is not None:
        require(equal(record["draw_color"], color), "incoming/helper color mismatch")


def validate_model(spec, model, session, hits):
    require(type(model) is dict and set(model) == {"view", "layout"}, "incomplete copied model")
    view, layout = model["view"], model["layout"]
    require(set(view) == VIEW_KEYS and set(layout) == LAYOUT_KEYS, "incomplete copied view/layout fields")
    expected = expected_session(spec)
    require(equal(session, expected) and equal(view["applied"], expected), "complete applied session differs from frozen state")
    require(equal(view["controls"], expected["controls"]), "desired controls differ from frozen state")
    focus = spec["requested_play_focus"] if spec["workspace"] == 0 else [20, 0, 0, spec["workspace"]]
    # The fixture focuses a Play body control before its one workspace switch.
    # UiModel::focus_control excludes Workspace tabs from remembered body focus,
    # so an untouched Rotary/Service memory stays None while its tab has focus.
    memory = [spec["requested_play_focus"], [0, 0, 0, 0], [0, 0, 0, 0]]
    expected_view = dict(edited_banks=[1, 1], focus=focus, roving_manual_keys=[24, 24], roving_pedal_key=0,
                         keyboard_target=0, manual_base_midi=60, pedal_octave=0, controls_pending=False,
                         controls_dirty=True, text_entry_active=False, pointer_captured=False, input_recovery=False,
                         last_submit_status=0, workspace=spec["workspace"], presentation=spec["presentation"], workspace_focus=memory)
    for name, value in expected_view.items():
        require(equal(view[name], value), "copied view " + name + " differs")
    require(equal([layout["width"], layout["height"]], spec["logical_size"]), "layout size differs")
    require(equal(layout["workspace"], spec["workspace"]) and equal(layout["presentation"], spec["presentation"]), "layout presentation differs")
    for name in ("show_cabinet", "bank_controls_in_cheeks", "sidebar_pedals"):
        require(type(layout[name]) is bool, "layout flag is not boolean")
    for name in ("header", "performance_panel", "keyboard_toolbar", "pedal_panel", "footer", "cabinet_panel", "cabinet_art", "workspace_panel"):
        require(finite_vector(layout[name], 4), "incomplete rectangle " + name)
    for name in ("registration_panels", "manual_panels", "manual_rail_panels", "preset_key_panels"):
        require(type(layout[name]) is list and len(layout[name]) == 2 and all(finite_vector(r, 4) for r in layout[name]), "incomplete rectangle pair " + name)
    require(type(layout["control_count"]) is int and layout["control_count"] == 68 and len(layout["controls"]) == 68, "68 controls missing")
    controls = {}
    for control in layout["controls"]:
        require(set(control) == {"id", "bounds", "label_bounds", "value_bounds", "track"}, "incomplete control geometry")
        require(integer_vector(control["id"], 4), "invalid control identity")
        require(tuple(control["id"]) not in controls, "duplicate control identity")
        controls[tuple(control["id"])] = control
        for name in ("bounds", "label_bounds", "value_bounds", "track"):
            require(finite_vector(control[name], 4), "invalid control rectangle")
    require(sum(c[0] == 19 for c in controls) == 24, "24 preset controls missing")
    if spec["active_reference"]:
        require(vector32(layout["performance_panel"], panel_inset(spec)[0]), "mapped panel differs")
        for cid, record in performance_controls(spec).items():
            for name, value in record.items():
                require(vector32(controls[cid][name], value), "independent performance/focus geometry differs")
    require(type(layout["manual_keys"]) is list and len(layout["manual_keys"]) == 2 and
            list(map(len, layout["manual_keys"])) == [61, 61] and len(layout["pedal_keys"]) == 25, "147 complete key records missing")
    for keys in [*layout["manual_keys"], layout["pedal_keys"]]:
        for key in keys:
            require(set(key) == {"note", "bounds", "accidental", "hit", "top", "front"}, "incomplete key record")
            require(integer_vector(key["note"], 2) and finite_vector(key["bounds"], 4) and type(key["accidental"]) is bool, "invalid key identity/geometry")
            for name in ("hit", "top", "front"):
                require(type(key[name]) is list and len(key[name]) == 4 and all(finite_vector(p, 2) for p in key[name]), "incomplete key quad")
    require(type(hits) is dict and set(hits) == {"controls", "manual_keys", "pedal_keys"}, "incomplete hit record")
    require(len(hits["controls"]) == 68 and len(hits["manual_keys"]) == 2 and
            list(map(len, hits["manual_keys"])) == [61, 61] and len(hits["pedal_keys"]) == 25, "incomplete hit inventory")
    for records, geometries in [(hits["controls"], layout["controls"]), *zip(hits["manual_keys"], layout["manual_keys"]),
                                (hits["pedal_keys"], layout["pedal_keys"])]:
        for record, geometry in zip(records, geometries, strict=True):
            id_key = "id" if "id" in geometry else "note"
            fields = {id_key, "probes", "visible"} if id_key == "id" else {id_key, "probes"}
            require(set(record) == fields and equal(record[id_key], geometry[id_key]) and len(record["probes"]) == 5, "incomplete/mismatched hit observation")
            if id_key == "id":
                require(type(record["visible"]) is bool, "invalid control visibility")
                b = [f32(v) for v in geometry["bounds"]]
                points = [[add(b[0], mul(b[2], .5)), add(b[1], mul(b[3], .5))],
                          [b[0], b[1]], [add(b[0], b[2]), b[1]], [b[0], add(b[1], b[3])],
                          [add(b[0], b[2]), add(b[1], b[3])]]
            else:
                quad = [[f32(v) for v in p] for p in geometry["hit"]]
                center = [mul(add(add(add(quad[0][i], quad[1][i]), quad[2][i]), quad[3][i]), .25) for i in range(2)]
                points = [center, *quad]
            for probe, point in zip(record["probes"], points, strict=True):
                require(set(probe) == {"point", "hit"} and vector32(probe["point"], point) and integer_vector(probe["hit"], 4), "invalid hit point/result")
    require(sum(r["visible"] for r in hits["controls"]) == (68 if spec["workspace"] == 0 else 10), "workspace visibility count differs")


def difference_regions(before, after, width, height, support):
    require(len(before) == len(after) == width * height * 4, "paired dimensions/bytes differ")
    total, forbidden, samples = 0, 0, []
    for y in range(height):
        row = y * width * 4
        if before[row:row + width * 4] == after[row:row + width * 4]:
            continue
        for x in range(width):
            at = row + x * 4
            if before[at:at + 4] != after[at:at + 4]:
                total += 1
                if not (support[0] <= x < support[2] and support[1] <= y < support[3]):
                    forbidden += 1
                    if len(samples) < 32:
                        samples.append([x, y, list(before[at:at + 4]), list(after[at:at + 4])])
    return {"changed_pixels": total, "forbidden_changed_pixels": forbidden, "first_forbidden_pixels": samples}


def span_differences(before, after, width, spans):
    count = 0
    for y, left, right in spans:
        begin, end = (y * width + left) * 4, (y * width + right) * 4
        if before[begin:end] != after[begin:end]:
            count += sum(before[p:p + 4] != after[p:p + 4] for p in range(begin, end, 4))
    return count


def color_mismatches(rgba, width, spans, color=None):
    count = 0
    expected = bytes(color) if color is not None else None
    for y, left, right in spans:
        begin, end = (y * width + left) * 4, (y * width + right) * 4
        if expected is not None and rgba[begin:end] == expected * (right - left):
            continue
        count += sum(rgba[p:p + 4] != expected if expected is not None else rgba[p + 3] != 255 for p in range(begin, end, 4))
    return count


def cyan_spans(rgba, width):
    # bytes.find is a fast full-frame scan; alignment rejects channel-offset hits.
    positions, start, color = set(), 0, bytes(CYAN)
    while True:
        at = rgba.find(color, start)
        if at < 0:
            return positions_to_spans(positions, width)
        if at % 4 == 0:
            positions.add(at // 4)
        start = at + 1


def clear_mismatches(spec, rgba):
    width, height = spec["output_size"]
    box = visible_box(spec)
    clear = bytes([18, 21, 20, 255] if spec["presentation"] == 1 else [85, 54, 36, 255])
    total = 0
    for y in range(height):
        intervals = [(0, width)] if not box[1] <= y < box[3] else [(0, box[0]), (box[2], width)]
        for left, right in intervals:
            if right <= left:
                continue
            begin, end = (y * width + left) * 4, (y * width + right) * 4
            if rgba[begin:end] != clear * (right - left):
                total += sum(rgba[p:p + 4] != clear for p in range(begin, end, 4))
    return total


def validate_frame(audit, spec, header, rgba, expected, side):
    label = f"{side}:{spec['id']}"
    audit.check(set(header) == set(spec) | FRAME_EXTRA, label + ":complete-header-fields")
    for name, value in spec.items():
        audit.check(equal(header.get(name), value), label + ":scenario:" + name)
    audit.check(equal([header["width"], header["height"]], spec["output_size"]), label + ":output-size")
    audit.check(equal(header["info"], FIXED_INFO), label + ":fixed-info")
    for family in ("model", "session", "hit"):
        audit.check(equal(header[family + "_before"], header[family + "_after"]), label + ":preserved-" + family)
    audit.guard(label + ":copied-model-schema-state-geometry", lambda: validate_model(spec, header["model_before"], header["session_before"], header["hit_before"]))
    for moment in ("before", "after"):
        audit.guard(label + ":renderer-" + moment, lambda moment=moment: validate_transform(spec, header["renderer_" + moment], INCOMING if moment == "before" else None))
    backend = header["backend"]
    audit.check(type(backend) is dict and set(backend) == {"name", "flags", "texture_formats", "maximum_texture_size", "sdl_version", "surface_format"}, label + ":complete-backend")
    audit.check(backend.get("name") == "software" and equal(backend.get("sdl_version"), [2, 32, 10]) and
                type(backend.get("flags")) is int and integer_vector(backend.get("maximum_texture_size"), 2) and
                type(backend.get("texture_formats")) is list and bool(backend["texture_formats"]) and
                all(type(v) is int for v in backend["texture_formats"]) and type(backend.get("surface_format")) is int,
                label + ":pinned-software-backend")
    helper = header["helper_probe"]
    audit.check(type(helper) is dict and set(helper) == {"present", "invoked", "bounds", "composition_scale", "before", "after", "unchanged"}, label + ":complete-helper-record")
    present = side == "after"
    audit.check(helper["present"] is present and helper["invoked"] is (present and spec["eligible_p1"]), label + ":helper-presence-invocation")
    audit.check(vector32(helper["bounds"], panel_inset(spec)[1]) and vector32(helper["composition_scale"], scale_for(spec)), label + ":helper-inputs")
    audit.check(equal(helper["before"], helper["after"]) and helper["unchanged"] is True, label + ":helper-complete-restoration")
    for moment in ("before", "after"):
        audit.guard(label + ":helper-" + moment, lambda moment=moment: validate_transform(spec, helper[moment], INCOMING))
    checks = {name: True for name in ("transform_unchanged", "model_unchanged", "session_unchanged", "hit_unchanged",
                                     "clip_containment", "deterministic_repaint", "inactive_classification", "text_cores_exact",
                                     "opaque_probes_nonempty_when_required", "focus_positions_exact")}
    checks.update(clip_companion_checked=spec["case"] in (10, 11, 12, 13, 15, 24, 25, 26, 27, 28),
                  after_all_repeat_checked=spec["case"] == 29, fresh_repeat_checked=spec["case"] == 30)
    audit.check(equal(header["checks"], checks), label + ":complete-native-assertions")
    audit.check(type(header["history_states"]) is int and header["history_states"] == (32 if spec["case"] == 29 else 0), label + ":history-count")
    audit.check(type(header["visible_clip_pixels"]) is int and header["visible_clip_pixels"] == area(visible_box(spec)), label + ":visible-clip-count")
    audit.check(type(header["quiet_clip_pixels"]) is int and 0 <= header["quiet_clip_pixels"] <= header["width"] * header["height"], label + ":quiet-count-domain")
    audit.check(clear_mismatches(spec, rgba) == 0, label + ":clear-outside-caller")
    audit.check(equal(header["witnesses"], expected), label + ":independent-complete-witness-metadata")
    width = header["width"]
    for probe in expected["opaque_probes"]:
        name = label + ":child:" + probe["id"]
        audit.check(not expected["full_required"] or probe["pixels"] > 0, name + ":nonempty")
        audit.check(color_mismatches(rgba, width, probe["spans"]) == 0, name + ":opaque")
    for run in expected["text_runs"]:
        name = label + ":text:" + run["id"]
        audit.check(not expected["full_required"] or run["opaque_pixels"] > 0, name + ":nonempty")
        audit.check(color_mismatches(rgba, width, run["opaque_spans"], run["color"]) == 0, name + ":literal-core-rgba")
    if spec["active_reference"]:
        focus = expected["focus"]
        audit.check(not expected["full_required"] or focus["expected_pixels"] > 0, label + ":nonempty-focus")
        audit.check(cyan_spans(rgba, width) == focus["expected_spans"], label + ":complete-cyan-positions")


def paired_metadata(header):
    # The genuine baseline has no P1 helper; every other exported field remains
    # comparable, including both complete helper transform/color observations.
    result = dict(header)
    result["helper_probe"] = {k: v for k, v in header["helper_probe"].items() if k not in ("present", "invoked")}
    return result


def compare_pair(audit, spec, before, after, witnesses):
    bh, bp = before; ah, ap = after
    label = spec["id"]
    audit.check(equal(paired_metadata(bh), paired_metadata(ah)), label + ":paired-complete-records")
    box = support_box(spec)
    record = {"case": spec["case"], "id": label, "support": box, "support_pixels": area(box),
              "compared_pixels": len(bp) // 4, "protected_pixels": len(bp) // 4 - area(box),
              "whole_frame_required": spec["paired_whole_frame_equality_required"]}
    diff = difference_regions(bp, ap, *spec["output_size"], box)
    record.update(diff)
    audit.check(diff["forbidden_changed_pixels"] == 0, label + ":outside-independent-support", diff)
    if spec["paired_whole_frame_equality_required"]:
        audit.check(bp == ap, label + ":required-whole-frame-equality", {"changed_pixels": diff["changed_pixels"]})
    for p in witnesses["opaque_probes"]:
        mismatch = span_differences(bp, ap, spec["output_size"][0], p["spans"])
        audit.check(mismatch == 0, label + ":paired-opaque:" + p["id"], {"different_pixels": mismatch})
    for run in witnesses["text_runs"]:
        mismatch = span_differences(bp, ap, spec["output_size"][0], run["opaque_spans"])
        audit.check(mismatch == 0, label + ":paired-text:" + run["id"], {"different_pixels": mismatch})
    if spec["active_reference"]:
        mismatch = span_differences(bp, ap, spec["output_size"][0], witnesses["focus"]["expected_spans"])
        audit.check(mismatch == 0, label + ":paired-focus", {"different_pixels": mismatch})
    return record


def quiet_intersection(spec, witnesses):
    """Only text destination envelopes are excluded from cut/uncut comparison."""
    width = spec["output_size"][0]
    box = support_box(spec)
    glyph_boxes = [rect_edges(r) for run in witnesses["text_runs"] for r in run["glyph_destinations"]]
    spans = []
    for y in range(box[1], box[3]):
        intervals = [[box[0], box[2]]]
        for left, top, right, bottom in glyph_boxes:
            if not top <= y < bottom:
                continue
            remaining = []
            for a, b in intervals:
                if right <= a or left >= b:
                    remaining.append([a, b])
                else:
                    if a < left:
                        remaining.append([a, left])
                    if right < b:
                        remaining.append([right, b])
            intervals = remaining
        spans.extend([y, a, b] for a, b in intervals if b > a)
    require(all(0 <= a < b <= width for _, a, b in spans), "unbounded independent quiet span")
    return spans


def compare_companion(audit, spec, cut, uncut, witnesses, side):
    ch, cp = cut; uh, up = uncut
    label = side + ":clip-companion:" + spec["id"]
    for name in ("width", "height", "model_before", "model_after", "session_before", "session_after",
                 "hit_before", "hit_after", "info", "backend"):
        audit.check(equal(ch[name], uh[name]), label + ":same-" + name)
    for name in ("scale", "viewport", "logical_viewport", "blend"):
        audit.check(equal(ch["renderer_before"][name], uh["renderer_before"][name]), label + ":same-" + name)
    spans = quiet_intersection(spec, witnesses)
    pixels = span_count(spans)
    audit.check(pixels == 0 if spec["clip_kind"] == "disjoint" else pixels > 0, label + ":nonvacuous-quiet-intersection")
    different = span_differences(cp, up, spec["output_size"][0], spans)
    audit.check(different == 0, label + ":quiet-rgba", {"pixels": pixels, "different_pixels": different})
    audit.check(equal(ch["quiet_clip_pixels"], pixels) and equal(uh["quiet_clip_pixels"], pixels), label + ":native-quiet-count")
    return dict(side=side, case=spec["case"], quiet_pixels=pixels, different_pixels=different)


def compare_repeat(audit, anchor, repeat, side, index):
    ah, ap = anchor; rh, rp = repeat
    label = f"{side}:repeat:{index}"
    for name in ("width", "height", "renderer_before", "renderer_after", "model_before", "model_after",
                 "session_before", "session_after", "hit_before", "hit_after", "info", "backend", "helper_probe", "witnesses"):
        audit.check(equal(ah[name], rh[name]), label + ":same-" + name)
    audit.check(ap == rp, label + ":exact-rgba")


class ArtifactStore:
    def __init__(self, directory):
        self.directory = directory
        self.files = 0
        self.bytes = 0

    def write(self, name, data):
        require(Path(name).name == name and self.files < MAX_FILES, "artifact filename/count limit")
        require(self.bytes + len(data) <= MAX_STORAGE, "artifact storage limit")
        with (self.directory / name).open("xb") as stream:
            stream.write(data)
        self.files += 1; self.bytes += len(data)
        return {"path": name, "bytes": len(data), "sha256": sha(data)}

    def compressed(self, name, data):
        result = self.write(name + ".zlib", zlib.compress(data, level=6))
        result.update(raw_bytes=len(data), raw_sha256=sha(data), encoding="zlib")
        return result

    def json(self, name, value):
        data = json_bytes(value)
        require(len(data) <= MAX_REPORT, "report JSON limit")
        return self.write(name, data)

    def load_stdout(self, record):
        artifact = record["stdout"]
        packed = (self.directory / artifact["path"]).read_bytes()
        require(len(packed) == artifact["bytes"] and sha(packed) == artifact["sha256"], "retained stream changed")
        inflater = zlib.decompressobj()
        raw = inflater.decompress(packed, MAX_STREAM + 1)
        require(len(raw) <= MAX_STREAM and inflater.eof and not inflater.unused_data and not inflater.unconsumed_tail,
                "retained stream decompression limit/trailer")
        require(len(raw) == artifact["raw_bytes"] and sha(raw) == artifact["raw_sha256"], "retained raw stream changed")
        return raw


def utc_now():
    return datetime.now(timezone.utc).isoformat()


class Runner:
    def __init__(self, store, timeout, total_seconds):
        self.store = store
        self.timeout = timeout
        self.started = time.monotonic()
        self.deadline = self.started + total_seconds
        self.commands = []

    @staticmethod
    def stop(process):
        try:
            if os.name == "posix":
                os.killpg(process.pid, signal.SIGKILL)
            elif process.poll() is None:
                process.kill()
        except (ProcessLookupError, OSError):
            pass

    def command(self, executable, arguments, name, limit):
        require(len(self.commands) < MAX_COMMANDS, "fixed subprocess count exhausted")
        remaining = self.deadline - time.monotonic()
        require(remaining > 0, "whole-run deadline exhausted; no further process started")
        started, utc = time.monotonic(), utc_now()
        outputs, errors = [bytearray(), bytearray()], []
        record = {"command": [str(executable), *arguments], "utc_started": utc, "name": name,
                  "stdout_limit": limit, "stderr_limit": MAX_STDERR, "timeout_seconds": min(self.timeout, remaining)}
        process = None
        try:
            process = subprocess.Popen(record["command"], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, start_new_session=os.name == "posix")

            def collect(stream, index, cap):
                try:
                    while True:
                        chunk = stream.read(65536)
                        if not chunk:
                            break
                        available = cap - len(outputs[index])
                        outputs[index].extend(chunk[:available])
                        if len(chunk) > available:
                            errors.append(("stdout" if index == 0 else "stderr") + " exceeded byte ceiling; retained prefix only")
                            self.stop(process)
                            break
                except OSError as error:
                    errors.append("pipe read failed: " + str(error))
                finally:
                    stream.close()

            threads = [threading.Thread(target=collect, args=(process.stdout, 0, limit), daemon=True),
                       threading.Thread(target=collect, args=(process.stderr, 1, MAX_STDERR), daemon=True)]
            for thread in threads:
                thread.start()
            try:
                process.wait(timeout=min(self.timeout, remaining))
            except subprocess.TimeoutExpired:
                errors.append("subprocess timeout; no retry")
                self.stop(process)
                process.wait(timeout=5)
            for thread in threads:
                thread.join(timeout=2)
            if any(thread.is_alive() for thread in threads):
                errors.append("inherited output pipe remained open")
                self.stop(process)
                for thread in threads:
                    thread.join(timeout=2)
            require(not any(thread.is_alive() for thread in threads), "bounded pipe collector did not retire")
            record["exit_code"] = process.returncode
            if process.returncode != 0:
                errors.append("nonzero native exit: " + str(process.returncode))
            if outputs[1]:
                errors.append("unexpected native stderr (retained)")
        except (OSError, subprocess.TimeoutExpired, ValueError) as error:
            errors.append(type(error).__name__ + ": " + str(error))
            if process is not None:
                self.stop(process)
            record["exit_code"] = process.poll() if process is not None else None
        record.update(utc_finished=utc_now(), duration_seconds=time.monotonic() - started, errors=errors)
        record["stdout"] = self.store.compressed(name + ".stdout", bytes(outputs[0]))
        record["stderr"] = self.store.compressed(name + ".stderr", bytes(outputs[1]))
        self.commands.append(record)
        return record, bytes(outputs[0])


def validate_inventory(payload, specs):
    require(len(payload) <= MAX_HEADER and payload.endswith(b"\n") and payload.count(b"\n") == 1, "list is not one bounded JSON line")
    value = strict_json(payload)
    expected = dict(schema=1, protocol=PROTOCOL, cases=34, main_cases=24, companions=5, repeats=2, eligibility_witnesses=3,
                    stream="one JSON line then bytes packed RGBA8; no trailer",
                    span_format="[physical output row, first x, exclusive end x]", inventory=specs)
    require(equal(value, expected), "complete 34-case list differs from independent frozen inventory")


def pin_input(inputs, label, path, expected=None):
    item = identity(path)
    inputs[label] = item
    if expected is not None:
        require(re.fullmatch(r"[0-9a-f]{64}", expected) is not None, "expected identity is not a lowercase SHA-256")
        item["expected_sha256"] = expected
        require(item["sha256"] == expected, "reviewed input SHA-256 mismatch: " + label)
    return Path(item["path"])


def admit_ui_model_sources(source_bytes, *, candidate_only):
    """Admit one coherent pair; reverse exact added blocks, never normalize C++."""
    require(type(candidate_only) is bool, "UiModel admission mode must be boolean")
    require(set(source_bytes) == set(UI_MODEL_FILES) and
            all(type(source_bytes[path]) is bytes for path in UI_MODEL_FILES),
            "UiModel admission requires exactly both complete byte sources")
    observed = {path: sha(source_bytes[path]) for path in UI_MODEL_FILES}
    original = {path: PINNED[path] for path in UI_MODEL_FILES}
    admission = dict(variant="original-coherent-pair", candidate_only=candidate_only,
                     original_pinned_sha256=original, observed_sha256=observed,
                     accepted_sha256=dict(original), transition=None,
                     claim="Source admission only; coherent build and runtime acceptance remain separate.")
    if observed == original:
        return admission
    require(candidate_only,
            "paired mode requires original UiModel pair; recall transition is candidate-only")
    require(not any(observed[path] == original[path] for path in UI_MODEL_FILES),
            "mixed original/recall UiModel pair is forbidden")
    reversed_sha256, blocks = {}, {}
    for path in UI_MODEL_FILES:
        block = RECALL_SOURCE_INSERTIONS[path]
        count = source_bytes[path].count(block)
        require(count == 1, "UiModel recall requires one exact complete inserted block: " + path)
        restored = source_bytes[path].replace(block, b"", 1)
        reversed_sha256[path] = sha(restored)
        require(reversed_sha256[path] == original[path],
                "UiModel recall reversal does not reconstruct original bytes: " + path)
        blocks[path] = dict(bytes=len(block), sha256=sha(block), occurrences=count)
    # Reversal alone would admit relocation of an otherwise exact block. The
    # complete new pair also pins insertion placement and every source byte.
    require(observed == RECALL_SOURCE_SHA256,
            "UiModel recall pair does not match exact admitted placement/source identity")
    admission.update(variant="a26-recall-controls-coherent-pair",
                     accepted_sha256=dict(RECALL_SOURCE_SHA256),
                     transition=dict(id=RECALL_SOURCE_TRANSITION, scope="candidate-only",
                                     patch=RECALL_SOURCE_PATCH,
                                     patch_sha256=RECALL_SOURCE_PATCH_SHA256,
                                     inserted_blocks=blocks, reversed_sha256=reversed_sha256,
                                     whole_file_reversal_verified=True))
    return admission


def pin_ui_model_sources(inputs, root, *, candidate_only):
    source_bytes = {}
    for path in UI_MODEL_FILES:
        resolved = pin_input(inputs, path, root / path)
        item = inputs[path]
        with resolved.open("rb") as stream:
            source_bytes[path] = stream.read(item["bytes"] + 1)
        require(len(source_bytes[path]) == item["bytes"] and sha(source_bytes[path]) == item["sha256"],
                "UiModel source changed while reading registered input: " + path)
    admission = admit_ui_model_sources(source_bytes, candidate_only=candidate_only)
    for path in UI_MODEL_FILES:
        inputs[path]["expected_sha256"] = admission["accepted_sha256"][path]
        inputs[path]["original_pinned_sha256"] = PINNED[path]
    if admission["transition"] is not None:
        pin_input(inputs, "ui_model_recall_patch", root / RECALL_SOURCE_PATCH, RECALL_SOURCE_PATCH_SHA256)
    return admission


def check_inputs_unchanged(audit, inputs):
    for label, previous in inputs.items():
        def verify(previous=previous):
            current = identity(previous["path"])
            require(current["bytes"] == previous["bytes"] and current["sha256"] == previous["sha256"], "input changed during run")
        audit.guard("final-input-stability:" + label, verify)


def cli(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--candidate-only", action="store_true", help="only canonical62 screen and canonical fixture checks; no paired/timing/visual claim")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--before", type=Path, help="retained genuine pre-P1 fixture; paired mode")
    parser.add_argument("--after", type=Path, required=True, help="coherent current fixture")
    parser.add_argument("--before-sha256", help="explicit independently reviewed baseline executable SHA-256")
    parser.add_argument("--after-sha256", help="explicit independently reviewed candidate executable SHA-256; required for paired mode")
    parser.add_argument("--before-painter", type=Path, help="retained genuine pre-P1 InstrumentView.cpp")
    parser.add_argument("--after-painter", type=Path, help="candidate InstrumentView.cpp; defaults to root source")
    parser.add_argument("--before-painter-sha256", help="explicit reviewed baseline painter SHA-256")
    parser.add_argument("--after-painter-sha256", help="explicit reviewed candidate painter SHA-256; required for paired mode")
    parser.add_argument("--before-source-id", help="root's source/build receipt or revision identity; paired mode")
    parser.add_argument("--after-source-id", help="root's source/build receipt or revision identity; paired mode")
    parser.add_argument("--sdl-root", type=Path, help="paired mode: pinned SDL 2.32.10 source directory")
    parser.add_argument("--pin", nargs=2, action="append", default=[], metavar=("FILE", "SHA256"), help="additional reviewed build/dependency input identity (repeatable)")
    parser.add_argument("--output", type=Path, help="NEW directory; paired mode requires it; candidate-only otherwise creates a unique temporary directory")
    parser.add_argument("--timeout", type=float, default=60., help="per process seconds, >0 and <=120")
    parser.add_argument("--total-seconds", type=float, default=1200., help="whole-run process-start deadline, >0 and <=1800")
    args = parser.parse_args(argv)
    require(math.isfinite(args.timeout) and 0 < args.timeout <= MAX_COMMAND_SECONDS, "invalid per-process timeout")
    require(math.isfinite(args.total_seconds) and 0 < args.total_seconds <= MAX_TOTAL_SECONDS, "invalid total deadline")
    require(len(args.pin) <= 32, "too many additional input identities")
    if not args.candidate_only:
        for name in ("before", "before_sha256", "after_sha256", "before_painter", "before_painter_sha256",
                     "after_painter_sha256", "before_source_id", "after_source_id", "sdl_root", "output"):
            require(getattr(args, name) is not None, "paired mode requires --" + name.replace("_", "-"))
        require(args.before_sha256 == BEFORE_EXE_SHA and args.before_painter_sha256 == BEFORE_PAINTER_SHA,
                "baseline identity is not the admitted genuine before")
    else:
        require(args.before is None and args.before_painter is None, "candidate-only mode must not receive baseline inputs")
    for label in (args.before_source_id, args.after_source_id):
        if label is not None:
            require(0 < len(label) <= 2048 and not any(c in label for c in "\n\r\0"), "invalid source receipt label")
    return args


def execute(args):
    started = time.monotonic()
    root = args.root.resolve(strict=True)
    if args.output is None:
        output = Path(tempfile.mkdtemp(prefix="p1-frozen62-"))
    else:
        output = args.output.absolute()
        output.mkdir(parents=False, exist_ok=False)
    store, audit = ArtifactStore(output), Audit()
    runner = Runner(store, args.timeout, args.total_seconds)
    report = dict(schema_version=1, model=MODEL, protocol=PROTOCOL,
                  mode="candidate-only-frozen62" if args.candidate_only else "paired-34-and-frozen62",
                  utc_started=utc_now(), cwd=str(Path.cwd()), root=str(root), output=str(output),
                  python=sys.version, platform=platform.platform(),
                  environment={name: os.environ.get(name) for name in
                               ("SDL_VIDEODRIVER", "SDL_AUDIODRIVER", "SDL_RENDER_DRIVER", "SDL_RENDER_SCALE_QUALITY",
                                "LD_LIBRARY_PATH", "LC_ALL", "LANG")},
                  source_labels={"before": args.before_source_id, "after": args.after_source_id},
                  inputs={}, ui_model_source_admission=None, cases=[], companions=[], commands=runner.commands,
                  limits=dict(header_bytes=MAX_HEADER, frame_bytes=MAX_STREAM, stderr_bytes=MAX_STDERR,
                              files=MAX_FILES, storage_bytes=MAX_STORAGE, subprocesses=MAX_COMMANDS,
                              per_process_seconds=args.timeout, total_seconds=args.total_seconds),
                  claims=["Frozen canonical image statistics and explicitly reported native preservation checks only."],
                  unrun_gates=["Frozen eight-process timing batch", "Independent actual full-frame visual admission",
                               "Whole-interface 1:1", "Physical fidelity", "Native device/accessibility/host/release acceptance"])
    frames, retained, witnesses = {}, {}, {}
    try:
        for path, expected in PINNED.items():
            if path not in UI_MODEL_FILES:
                pin_input(report["inputs"], path, root / path, expected)
        report["ui_model_source_admission"] = pin_ui_model_sources(
            report["inputs"], root, candidate_only=args.candidate_only)
        pin_input(report["inputs"], "comparator", Path(__file__))
        after = pin_input(report["inputs"], "after_executable", args.after, args.after_sha256)
        pin_input(report["inputs"], "after_painter", args.after_painter or root / PAINTER, args.after_painter_sha256)
        before = None
        if not args.candidate_only:
            before = pin_input(report["inputs"], "before_executable", args.before, args.before_sha256)
            pin_input(report["inputs"], "before_painter", args.before_painter, args.before_painter_sha256)
            require(before != after, "paired executables must be distinct paths")
            for path, expected in SDL_PINNED.items():
                pin_input(report["inputs"], "SDL/" + path, args.sdl_root / path, expected)
            admission = strict_json((root / BASELINE_ADMISSION).read_bytes())
            require(admission["passed"] is True and admission["fixture_executable_sha256"] == args.before_sha256 and
                    admission["fixture_source_sha256"] == PINNED[FIXTURE] and admission["painter_sha256"] == args.before_painter_sha256,
                    "genuine native patch admission is inconsistent")
        for i, (path, expected) in enumerate(args.pin):
            pin_input(report["inputs"], "additional_" + str(i), Path(path), expected)
        reference, baseline, historical = frozen_references(root)
        report["retained_t3_baseline_screens"] = historical
        atlases = font_atlases(root / FONT)
        specs = scenarios()
        report["support_method"] = "Independent binary32 public panel/inset geometry; ceil(edge*renderer_scale-0.5); translate viewport and intersect output, viewport, physical enabled clip. No candidate/exported mask."
        report["glyph_method"] = "Independent frozen font RLE, literal source-derived text arguments and float32 COPY geometry; SDL2.32.10 clipped source rounding and vertical-then-horizontal seven-bit interpolation. All opaque cores and complete cyan positions."
        sides = [("after", after)] if args.candidate_only else [("before", before), ("after", after)]
        for side, executable in sides:
            result = audit.guard(side + ":list-transport", lambda side=side, executable=executable:
                                 runner.command(executable, ["--list"], side + "-list", MAX_HEADER))
            if result is not None:
                command, payload = result
                audit.check(not command["errors"], side + ":list-execution", command["errors"])
                audit.guard(side + ":frozen-inventory", lambda payload=payload: validate_inventory(payload, specs))
        for spec in specs[:1] if args.candidate_only else specs:
            if time.monotonic() >= runner.deadline:
                audit.check(False, "whole-run-deadline", {"unattempted_indices": list(range(spec["case"], 1 if args.candidate_only else 34))})
                break
            index = spec["case"]
            expected = audit.guard(spec["id"] + ":independent-witness-construction", lambda spec=spec: expected_witnesses(spec, atlases))
            witnesses[index] = expected
            pair = {}
            for side, executable in sides:
                label = f"{side}-{index:02d}"
                result = audit.guard(label + ":transport", lambda executable=executable, index=index, label=label:
                                     runner.command(executable, ["--case", str(index)], label,
                                                    MAX_HEADER + 4 * spec["output_size"][0] * spec["output_size"][1]))
                if result is None:
                    continue
                command, payload = result
                retained[(side, index)] = command
                audit.check(not command["errors"], label + ":execution", command["errors"])
                frame = audit.guard(label + ":parse", lambda payload=payload, index=index: parse_frame(payload, index))
                if frame is None:
                    continue
                pair[side] = frame
                h, rgba = frame
                if not audit.check(equal([h["width"], h["height"]], spec["output_size"]), label + ":frozen-output-domain"):
                    del pair[side]
                    continue
                if expected is not None:
                    audit.guard(label + ":validation", lambda h=h, rgba=rgba, side=side, spec=spec, expected=expected:
                                validate_frame(audit, spec, h, rgba, expected, side))
                if index == 0:
                    measures = {name: patch_measure(rgba, h["width"], h["height"], rect) for name, rect in PATCHES.items()}
                    screens = numerical_screens(measures, reference)
                    report[side + "_canonical"] = dict(rgba_sha256=sha(rgba), patches=measures, numerical_screens=screens)
                    if side == "before":
                        for name in PATCHES:
                            audit.check(measures[name]["decoded_rgb_sha256"] == baseline[name]["decoded_rgb_sha256"], "baseline-native-t3-patch:" + name)
                        audit.check((screens["passed"], screens["failed"], screens["total"]) == (28, 34, 62), "baseline-native-retained-28-pass-34-fail")
                        audit.check([r["pass"] for r in screens["checks"]] == [r["pass"] for r in historical["checks"]], "baseline-native-retained-all-decisions")
                    else:
                        for check in screens["checks"]:
                            audit.check(check["pass"], "frozen62:" + check["id"], check)
                # Keep only the current pair; later relationships reread bounded,
                # hash-checked retained bytes instead of keeping 34 full frames.
                frames[(side, index)] = {"rgba_sha256": sha(rgba), "header_sha256": sha(json_bytes(h))}
            if not args.candidate_only and set(pair) == {"before", "after"} and expected is not None:
                record = audit.guard(spec["id"] + ":paired-comparison", lambda spec=spec, pair=pair, expected=expected:
                                     compare_pair(audit, spec, pair["before"], pair["after"], expected))
                if record is not None:
                    report["cases"].append(record)
            pair.clear()
        report["frame_identities"] = [{"side": side, "case": index, **value} for (side, index), value in frames.items()]
        if not args.candidate_only:
            def load(side, index):
                return parse_frame(store.load_stdout(retained[(side, index)]), index)
            for side, _ in sides:
                for index in (29, 30):
                    audit.guard(f"{side}:repeat-{index}", lambda side=side, index=index: compare_repeat(audit, load(side, 0), load(side, index), side, index))
                for cut, full in ((10, 24), (11, 25), (12, 26), (13, 27), (15, 28)):
                    result = audit.guard(f"{side}:companion-{cut}", lambda side=side, cut=cut, full=full:
                                         compare_companion(audit, specs[cut], load(side, cut), load(side, full), witnesses[cut], side))
                    if result is not None:
                        report["companions"].append(result)
            audit.check(len(report["cases"]) == 34 and len(frames) == 68 and len(report["companions"]) == 10,
                        "complete-paired-34-export-matrix")
        else:
            audit.check(len(frames) == 1 and "after_canonical" in report, "complete-candidate-canonical-screen")
    except (ValueError, OSError, KeyError, TypeError, IndexError, OverflowError, RecursionError) as error:
        audit.check(False, "setup-or-dependent-run-failure", f"{type(error).__name__}: {error}")
    finally:
        check_inputs_unchanged(audit, report["inputs"])
        report.update(utc_finished=utc_now(), duration_seconds=time.monotonic() - started,
                      passed=not audit.failures, checks_evaluated=audit.checks, failures=audit.failures,
                      artifacts_before_report={"files": store.files, "bytes": store.bytes})
        store.json("report.json", report)
    print(json.dumps({"model": MODEL, "mode": report["mode"], "passed": report["passed"],
                      "checks_evaluated": audit.checks, "failed_checks": len(audit.failures),
                      "candidate_screens": report.get("after_canonical", {}).get("numerical_screens", {}),
                      "report": str(output / "report.json")}, allow_nan=False))
    return 0 if report["passed"] else 1


def main(argv=None):
    try:
        return execute(cli(argv))
    except (ValueError, OSError) as error:
        print("P1 comparator setup failed: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
