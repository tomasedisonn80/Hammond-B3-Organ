#!/usr/bin/env python3
"""Compare genuine pre-T1 and admitted T1 native frames inside glyph-only support.

The fixed 66 percussion and 44 typography cases are declared independently.
Old and new glyph-copy rectangles come from pinned font metrics, binary32 layout,
the admitted run contract, unchanged Drawing arithmetic, and SDL's software COPY
destination conversion. No candidate helper, changed-pixel-derived mask, whole
label box or earlier material allowance is imported. A new output directory is
required; its declared mask precedes native execution. Failed pairs retain PNGs.

Example from the repository root:
  python3 -B tools/compare_footage_typography.py \
    --before-percussion ../baseline-lower/test_standalone_percussion_raster \
    --after-percussion ../build-native/apps/standalone/test_standalone_percussion_raster \
    --before-typography ../baseline-lower/test_standalone_footage_typography_raster \
    --after-typography ../build-native/apps/standalone/test_standalone_footage_typography_raster \
    --before-painter ../baseline-lower/InstrumentView.cpp \
    --baseline-receipt docs/development/2026-11-16-conversion-material/reports/typography-before-identity.json \
    --build-dir ../build-native --output-dir /path/to/new-report-directory

This qualifies a finite software preservation transition, not whole-interface
1:1, native display/DPI/accessibility, physical fidelity or audio behavior.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import platform
import re
import struct
import subprocess
import sys
import time

from PIL import Image, ImageChops, ImageDraw, __version__ as PILLOW_VERSION

MODEL = "footage-independent-paired-raster-v1"
PROTOCOL = "footage-typography-v1"
BASE = "a411268fd498f65c083203137831bf5afed83bd8"
SESSION = "docs/development/2026-11-16-conversion-material"
CONTRACT = "docs/design/FOOTAGE_TYPOGRAPHY_CONTRACT.md"
CONTRACT_SHA = "e000682c74c3ef488cf89dd60396a3d129f8c525cf41a049334cc62030cb3f8a"
ADMISSION = "docs/reviews/FOOTAGE_TYPOGRAPHY_ADMISSION.md"
ADMISSION_SHA = "a9c5c3bf7274c628dafc9ce92dc602ed60c203fd79b0bc784e74e84392c80d3d"
FONT = "apps/standalone/FontData.h"
FONT_SHA = "f1a3121a2707a03a3b2e025c399e68c553ce9498f4b002ec13b18f512e334802"
FIXTURE = "apps/standalone/native_tests/test_standalone_footage_typography_raster.cpp"
FIXTURE_SHA = "facc85f516454964ed55e406f95db4046923d7a2441fdf72e65719b3685fec4f"
PERCUSSION = "apps/standalone/native_tests/test_standalone_percussion_raster.cpp"
BEFORE_PAINTER_SHA = "45b710a9c207f456701732f55ec1086487d63bdb9a8b6ed995f4de12cd5bdb10"
BEFORE_PERCUSSION_SHA = "2bb6c0b613a63588575295e80108341e3eaf37b3b2897c3aa7c762bb3f58a051"
BEFORE_TYPOGRAPHY_SHA = "3e8fcd80bc1715a124fd4a506d31a35ac6abde2a4d4a34c35f95e856c62c924c"
BASELINE_RECEIPT_SHA = "b00c5852a862c730c4d84c5008d8d930f00342e0eb4030f90ce936c7e1aa17e2"
LABELS = ("16'", "5 1/3'", "8'", "4'", "2 2/3'", "2'", "1 3/5'", "1 1/3'", "1'")
CENTERS = ((158, 206, 254, 302, 351, 400, 449, 498, 548),
           (685, 734, 782, 830, 878, 927, 975, 1024, 1074))
MAX_HEADER = 512 * 1024
MAX_PIXELS = 3900 * 2200
MAX_ARTIFACT_BYTES = 80 * 1024 * 1024
PATCHES = {
    "upper_left": (88, 320, 18, 128), "upper_right": (572, 320, 14, 128),
    "lower_left": (612, 320, 18, 128), "lower_right_v2": (1095, 320, 13, 128),
    "lower_left_top": (612, 298, 18, 14), "lower_right_top_v2": (1095, 298, 13, 14),
    "lower_center_top": (800, 302, 112, 6),
    "lower_left_bottom": (612, 460, 18, 20), "lower_right_bottom_v2": (1095, 460, 13, 20),
    "lower_bottom_left": (704, 492, 12, 8), "lower_bottom_middle": (852, 492, 14, 8),
    "lower_bottom_right": (1047, 492, 12, 8),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical_json(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def file_identity(path):
    data = Path(path).read_bytes()
    return {"path": str(Path(path).resolve()), "bytes": len(data), "sha256": sha(data)}


def write_new(path, value):
    data = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    with Path(path).open("xb") as stream:
        stream.write(data)


def f32(value):
    return struct.unpack("<f", struct.pack("<f", value))[0]


def f32_equal(a, b):
    return (type(a) in (int, float) and type(b) in (int, float) and
            math.isfinite(a) and math.isfinite(b) and struct.pack("<f", a) == struct.pack("<f", b))


def typed_equal(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    if type(a) in (int, float) and type(b) in (int, float):
        return a == b
    if type(a) is not type(b):
        return False
    if isinstance(a, list):
        return len(a) == len(b) and all(typed_equal(x, y) for x, y in zip(a, b, strict=True))
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(typed_equal(a[k], b[k]) for k in a)
    return a == b


def float_vector_equal(a, b):
    return isinstance(a, list) and len(a) == len(b) and all(f32_equal(x, y) for x, y in zip(a, b, strict=True))


def mapped(width, height, rectangle):
    sx, sy = f32(width / 1672), f32(height / 941)
    x, y, w, h = rectangle
    left, top = f32(x * sx), f32(y * sy)
    return [left, top, f32(f32(f32(x + w) * sx) - left),
            f32(f32(f32(y + h) * sy) - top)]


def intersect(*boxes):
    left, top = max(b[0] for b in boxes), max(b[1] for b in boxes)
    right, bottom = min(b[2] for b in boxes), min(b[3] for b in boxes)
    return [left, top, max(left, right), max(top, bottom)]


def xywh(rectangle):
    x, y, w, h = rectangle
    return [x, y, x + w, y + h]


def area(box):
    return (box[2] - box[0]) * (box[3] - box[1])


def font_metrics(path):
    raw = Path(path).read_bytes()
    require(sha(raw) == FONT_SHA, "unchanged Serif atlas identity differs")
    block = raw.decode().split("kSerifGlyphs{{", 1)[1].split("}};", 1)[0]
    entries = re.findall(r"\{(-?\d+(?:,\s*-?\d+){6})\},\s*// ASCII (\d+)", block)
    require(len(entries) == 95, "Serif glyph inventory differs")
    glyphs = {chr(int(code)): tuple(int(v) for v in fields.split(",")) for fields, code in entries}
    require(set(glyphs) == {chr(i) for i in range(32, 127)}, "Serif codepoints differ")
    return glyphs


def advance(text, size, glyphs):
    scale = f32(size / 40)
    value = 0.0
    for char in text:
        value = f32(value + f32(f32(glyphs[char][6] * scale) / 64))
    return value


def runs(text, box, sx, sy, glyphs, after):
    """Independent contract evaluation; no painter/fixture helper is imported."""
    x, y, w, h = box
    font_scale = min(sx, sy)
    if not after:
        size = min(f32(19 * font_scale), f32(h / f32(1.2)))
        width = advance(text, size, glyphs)
        available = f32(w - f32(2 * f32(2 * sx)))
        if width > available and width > 0:
            size = f32(size * f32(max(f32(.1), available) / width))
        left = f32(x + f32(f32(w - advance(text, size, glyphs)) / 2))
        top = f32(y + f32(f32(h - f32(size * f32(1.2))) / 2))
        return [{"text": text, "x": left, "top": top, "size": size, "requested_baseline": None}]
    mixed = len(text) == 6
    segments = [(text, 20.5, 21.5)] if not mixed else [
        (text[0], 20.5, 21.5), (text[2], 13, 15.5),
        (text[3], 16, 19.5), (text[4], 13, 21.5), (text[5], 20.5, 21.5)]
    sizes = [f32(nominal * font_scale) for _, nominal, _ in segments]
    widths = [advance(segment[0], size, glyphs) for segment, size in zip(segments, sizes, strict=True)]
    gap = f32(.5 * sx)
    width = 0.0
    for i, item in enumerate(widths):
        width = f32(width + item)
        if mixed and i in (0, 3):
            width = f32(width + gap)
    cursor = f32(x + f32(f32(w - width) / 2))
    result = []
    for i, ((segment, _, offset), size, item) in enumerate(zip(segments, sizes, widths, strict=True)):
        baseline = f32(y + f32(offset * sy))
        top = f32(baseline - f32(f32(38 * size) / 40))
        result.append({"text": segment, "x": cursor, "top": top, "size": size,
                       "requested_baseline": baseline})
        cursor = f32(cursor + item)
        if mixed and i in (0, 3):
            cursor = f32(cursor + gap)
    return result


def glyph_quads(run, glyphs):
    scale = f32(run["size"] / 40)
    baseline = f32(run["top"] + f32(38 * scale))
    cursor = run["x"]
    result = []
    for char in run["text"]:
        ax, ay, w, h, bx, by, adv = glyphs[char]
        if w and h:
            px = 2 if f32(w * scale) < 1 else 0
            py = 2 if f32(h * scale) < 1 else 0
            target = [f32(cursor + f32((bx - px) * scale)),
                      f32(baseline + f32((by - py) * scale)),
                      f32((w + 2 * px) * scale), f32((h + 2 * py) * scale)]
            requested = run["requested_baseline"]
            ideal_target = list(target)
            if requested is not None:
                ideal_target[1] = f32(requested + f32((by - py) * scale))
            result.append({"character": char, "atlas": [ax - px, ay - py, w + 2 * px, h + 2 * py],
                           "target_binary32": target, "requested_target_binary32": ideal_target,
                           "actual_baseline": baseline, "requested_baseline": requested,
                           "gutter": [px, py]})
        cursor = f32(cursor + f32(f32(adv * scale) / 64))
    return result


def device_box(quad, scale, origin):
    # SDL_RenderCopyF multiplies each coordinate/extent independently by the
    # renderer scale. SW_QueueCopy truncates each binary32 value to int; the
    # viewport offset is added afterwards. Zero extents paint no pixels.
    x, y, w, h = [math.trunc(f32(v * s)) for v, s in zip(quad, (*scale, *scale), strict=True)]
    return [x + origin[0], y + origin[1], x + origin[0] + max(w, 0), y + origin[1] + max(h, 0)]


def percussion_cases():
    """Existing immutable fixture's literal 66-index inventory, not its masks."""
    result = []
    def add(w=1672, h=941, scale=1, values=0, focus=0, route=0,
            pending=False, presentation=0, workspace=0, clip=0):
        offset = 7 if clip else 0
        vw, vh = math.ceil(f32(w * scale)), math.ceil(f32(h * scale))
        physical = [0, 0, 0, 0]
        if clip == 1:
            physical = [math.trunc(f32(n * scale)) for n in (180, 138, 275, 77)]
        elif clip == 2:
            physical = [math.floor(n * scale) for n in (161, 174, 252, 41)]
        result.append({"suite": "percussion", "case": len(result), "logical_size": [w, h],
                       "scale": [scale, scale], "output_size": [vw + 2 * offset, vh + 2 * offset],
                       "viewport": [offset, offset, vw, vh], "clip": physical,
                       "clip_enabled": bool(clip), "active": presentation == workspace == 0 and
                       1400 <= w <= 8192 and 820 <= h <= 8192, "resource_crop": False,
                       "fixture": [w, h, values, focus, route, int(pending), presentation, workspace, clip],
                       "offset": offset})
    for value in range(16):
        add(values=value, focus=value % 4, route=value % 4, pending=value % 2 != 0)
    for scale in (1.5, 2):
        add(scale=scale, values=15, focus=3, pending=True)
    for w, h in ((1400, 820), (1920, 1080)):
        for scale in (1, 1.5, 2): add(w, h, scale, 9, 1, 1)
    for w, h in ((1399, 820), (1400, 819)):
        for scale in (1, 1.5, 2): add(w, h, scale, 6, 2, 2, True)
    for w, h in ((960, 700), (1280, 900)):
        for scale in (1, 2): add(w, h, scale, 5, 0, 3)
    for w, h in ((1672, 941), (1920, 1080)):
        for scale in (1, 1.5, 2): add(w, h, scale, 10, 3, 0, True, 1)
    for workspace in (1, 2):
        for presentation in (0, 1):
            for scale in (1, 1.5, 2):
                add(scale=scale, values=11, focus=1, route=2, presentation=presentation, workspace=workspace)
    for w, h in ((1400.25, 820.75), (1672.5, 941.25)): add(w, h, 1.5, 14, 2)
    for scale in (1, 1.5, 2):
        for clip in (1, 2): add(scale=scale, values=13, pending=True, clip=clip)
    for h in (933.25, 933.5):
        for scale in (1, 1.5, 2): add(h=h, scale=scale, values=3, focus=2, route=3, pending=True)
    require(len(result) == 66, "percussion inventory must remain 66")
    return result


def typography_cases():
    result = []
    def add(w=1672, h=941, rx=1, ry=1, level=4, route="B", pending=False,
            held=True, origin=(13, 17), clip_kind="disabled", resource=False,
            focus_manual=0, focus_index=1, workspace=0, presentation=0):
        vw, vh = math.ceil(f32(w * rx)), math.ceil(f32(h * ry))
        if resource:
            label = mapped(w, h, (183, 467, 46, 23))
            origin = (-math.floor(f32(label[0] * rx)), -math.floor(f32(label[1] * ry)))
            output = [64, 64]
        else:
            output = [vw + 2 * abs(origin[0]), vh + 2 * abs(origin[1])]
        clips = {"left": [190, 469, 4, 23], "right": [219, 469, 4, 23],
                 "top": [183, 475, 46, 3], "bottom": [183, 485, 46, 3],
                 "disjoint": [1150, 300, 8, 8], "empty": [183, 467, 0, 0]}
        selected = clips.get(clip_kind.split("-")[-1], [0, 0, 0, 0])
        logical = clip_kind.startswith("logical-")
        physical = [math.floor(n * r) for n, r in zip(selected, (rx, ry, rx, ry), strict=True)] if logical else selected
        logical_clip = selected if logical else [math.floor(n / r) for n, r in zip(physical, (rx, ry, rx, ry), strict=True)]
        viewport = [*origin, vw, vh]
        bank = 0 if route == "A" else 1
        result.append({"suite": "typography", "case": len(result), "logical_size": [w, h],
                       "scale": [rx, ry], "output_size": output, "viewport": viewport,
                       "logical_viewport": [math.floor(n / r) for n, r in zip(viewport, (rx, ry, rx, ry), strict=True)],
                       "clip": physical, "logical_clip": logical_clip, "clip_enabled": clip_kind != "disabled",
                       "clip_kind": clip_kind, "blend": 0 if clip_kind == "logical-empty" else 1,
                       "active": workspace == presentation == 0 and 1400 <= w <= 8192 and 820 <= h <= 8192,
                       "resource_crop": resource, "level": level, "route": route,
                       "route_index": 10 + bank, "edited_bank": route, "pending": pending, "held": held,
                       "focus_manual": focus_manual, "focus_index": focus_index,
                       "focus": [4, focus_manual, bank, focus_index], "workspace": workspace, "presentation": presentation})
    for manual in (0, 1):
        for index in range(9):
            add(level=4 * (index % 3), route="A" if index % 2 == 0 else "B",
                pending=index % 3 == 1, held=index % 3 != 0, focus_manual=manual, focus_index=index)
    for w, h in ((1400, 820), (1920, 1080), (1920, 820), (1400, 1080)): add(w, h)
    add(1672.5, 941.25, 1.25, 1.25)
    add(rx=.75, ry=.75, origin=(-11, -7))
    add(rx=1.25, ry=1.25, origin=(29, 31))
    add(rx=1.5, ry=2)
    for logical in (False, True):
        for edge in ("left", "right", "top", "bottom"):
            scale = 1.25 if logical else 1
            add(rx=scale, ry=scale, clip_kind=("logical-glyph-" if logical else "physical-glyph-") + edge)
    add(clip_kind="physical-disjoint")
    add(clip_kind="physical-empty")
    add(rx=1.25, ry=1.25, clip_kind="logical-empty")
    add(presentation=1)
    add(workspace=1)
    add(workspace=2)
    add(w=struct.unpack("<f", struct.pack("<I", struct.unpack("<I", struct.pack("<f", 1400))[0] - 1))[0])
    add(h=struct.unpack("<f", struct.pack("<I", struct.unpack("<I", struct.pack("<f", 820))[0] - 1))[0])
    add(8192, 8192, resource=True, origin=(0, 0))
    add(8192, 8192, 1.5, 2, resource=True, origin=(0, 0))
    require(len(result) == 44, "typography inventory must remain 44")
    return result


def allowance_mask(spec):
    image = Image.new("L", tuple(spec["output_size"]), 0)
    draw = ImageDraw.Draw(image)
    for box in spec["allowed_rectangles"]:
        if area(box): draw.rectangle((box[0], box[1], box[2] - 1, box[3] - 1), fill=255)
    return image


def declare_case(case, glyphs):
    result = dict(case)
    width, height = case["output_size"]
    origin = case["viewport"][:2]
    visible = intersect([0, 0, width, height], xywh(case["viewport"]))
    if case["clip_enabled"]:
        clip = xywh(case["clip"])
        visible = intersect(visible, [clip[0] + origin[0], clip[1] + origin[1], clip[2] + origin[0], clip[3] + origin[1]])
    result.update({"visible_device_box": visible, "labels": [], "allowed_rectangles": [],
                   "compared_pixels": width * height})
    if case["active"]:
        w, h = case["logical_size"]
        sx, sy = f32(w / 1672), f32(h / 941)
        for manual, centers in enumerate(CENTERS):
            for index, (center, text) in enumerate(zip(centers, LABELS, strict=True)):
                box = mapped(w, h, (center - 23, 467, 46, 23))
                record = {"manual": manual, "index": index, "text": text, "label_box_binary32": box}
                for after, name in ((False, "before"), (True, "after")):
                    copies = []
                    for run in runs(text, box, sx, sy, glyphs, after):
                        for quad in glyph_quads(run, glyphs):
                            actual = device_box(quad["target_binary32"], case["scale"], origin)
                            requested = device_box(quad["requested_target_binary32"], case["scale"], origin)
                            quad["device_copy_box"] = actual
                            quad["requested_device_copy_box"] = requested
                            quad["visible_copy_box"] = intersect(actual, visible)
                            for source_box in (actual, requested):
                                if area(source_box):
                                    expanded = [source_box[0] - 1, source_box[1] - 1, source_box[2] + 1, source_box[3] + 1]
                                    clipped = intersect(expanded, visible)
                                    if area(clipped): result["allowed_rectangles"].append(clipped)
                            copies.append(quad)
                    record[name] = copies
                result["labels"].append(record)
    result["allowed_rectangles"] = sorted(set(map(tuple, result["allowed_rectangles"])))
    mask = allowance_mask(result)
    result["allowed_pixels"] = mask.histogram()[255]
    result["protected_pixels"] = width * height - result["allowed_pixels"]
    result["allowance_sha256"] = sha(mask.tobytes())
    result["whole_frame_equality_required"] = result["allowed_pixels"] == 0
    return result


def declare_mask(glyphs):
    cases = [declare_case(case, glyphs) for case in percussion_cases() + typography_cases()]
    require(len(cases) == 110, "exact 110 declared pairs")
    require(all(c["whole_frame_equality_required"] for c in cases if c["suite"] == "typography" and 34 <= c["case"] <= 41),
            "disjoint/empty/inactive typography cases must have empty allowance")
    return {"schema": 1, "model": MODEL, "protocol": PROTOCOL, "contract_sha256": CONTRACT_SHA,
            "font_sha256": FONT_SHA, "fixture_sha256": FIXTURE_SHA,
            "method": "Union of independently derived old/new glyph COPY destination rectangles, requested/actual baseline variants, at most one device pixel around each; intersect caller viewport, clip and output. No whole label/panel rectangle.",
            "cases": cases}


def command(executable, arguments, timeout):
    completed = subprocess.run([str(executable), *arguments], capture_output=True, timeout=timeout, check=False)
    require(completed.returncode == 0, f"{executable.name} {arguments}: exit {completed.returncode}: {completed.stderr[:4096]!r}")
    require(not completed.stderr, f"unexpected helper stderr: {completed.stderr[:4096]!r}")
    return completed.stdout


def frame(executable, index, timeout):
    payload = command(executable, ["--case", str(index)], timeout)
    end = payload.find(b"\n", 0, MAX_HEADER)
    require(end >= 0, "missing bounded JSON header")
    header = json.loads(payload[:end])
    require(type(header) is dict and header.get("schema") == 1 and header.get("case") == index, "wrong frame identity")
    w, h = header.get("width"), header.get("height")
    require(type(w) is type(h) is int and 0 < w <= 3900 and 0 < h <= 2200 and w * h <= MAX_PIXELS, "unbounded frame")
    raw = payload[end + 1:]
    require(len(raw) == header.get("bytes") == w * h * 4, "incorrect RGBA byte count")
    return header, raw, sha(payload[:end])


def metadata_errors(spec, header):
    expected = {"schema": 1, "case": spec["case"], "width": spec["output_size"][0],
                "height": spec["output_size"][1], "bytes": spec["compared_pixels"] * 4}
    if spec["suite"] == "percussion":
        expected.update({"fixture": spec["fixture"], "scale": spec["scale"][0], "offset": spec["offset"], "active": spec["active"]})
    else:
        expected.update({key: spec[key] for key in ("output_size", "scale", "viewport", "clip", "logical_viewport", "logical_clip",
                         "clip_enabled", "clip_kind", "blend", "level", "route", "route_index", "edited_bank", "pending", "held",
                         "workspace", "presentation", "resource_crop")})
        expected.update({"protocol": PROTOCOL, "active_typography": spec["active"]})
        if spec["workspace"] == 0: expected["focus"] = spec["focus"]
    errors = [f"{key}: expected {value!r}, observed {header.get(key)!r}" for key, value in expected.items()
              if not typed_equal(header.get(key), value)]
    if spec["suite"] == "typography":
        if not float_vector_equal(header.get("logical_size"), spec["logical_size"]): errors.append("binary32 logical size differs")
        try:
            view, layout = header["model"]["view"], header["model"]["layout"]
            applied = view["applied"]
            checks = {"focus": view["focus"] == header["focus"],
                      "both edited banks": view["edited_banks"] == [spec["route_index"] - 10] * 2,
                      "pending": view["controls_pending"] is spec["pending"],
                      "workspace": view["workspace"] == layout["workspace"] == spec["workspace"],
                      "presentation": view["presentation"] == layout["presentation"] == spec["presentation"],
                      "layout dimensions": float_vector_equal([layout["width"], layout["height"]], spec["logical_size"]),
                      "clock/rate/peak/revision": [applied[k] for k in ("frame_clock", "sample_rate", "peak", "publication_revision")] == [38400, 48000, .125, 4],
                      "prepared/running": applied["prepared"] is applied["running"] is True}
            for name, controls in (("desired", view["controls"]), ("applied", applied["controls"])):
                checks[name + " banks"] = controls["drawbars"] == [[[spec["level"]] * 9 for _ in range(2)] for _ in range(2)]
                checks[name + " constants"] = controls["expression"] == .625 and controls["pedal_drawbars"] == [3, 7] and controls["percussion"] == [True, 0, 0, 0]
            held_keys, held_pedals = [[False] * 61 for _ in range(2)], [False] * 25
            held_keys[0][24] = held_keys[1][36] = held_pedals[12] = spec["held"]
            checks["held notes"] = applied["held_keys"] == held_keys and applied["held_pedals"] == held_pedals
            if spec["workspace"] == 0:
                checks["68 controls"] = layout["control_count"] == 68
                checks["147 keys"] = sum(map(len, layout["manual_keys"])) + len(layout["pedal_keys"]) == 147
                checks["24 presets"] = sum(c["id"][0] == 19 for c in layout["controls"]) == 24
            if spec["active"]:
                controls = {tuple(c["id"]): c for c in layout["controls"]}
                for label in spec["labels"]:
                    identity = (4, label["manual"], spec["route_index"] - 10, label["index"])
                    control = controls[identity]
                    center = CENTERS[label["manual"]][label["index"]]
                    for name, rect in (("label_bounds", (center - 23, 467, 46, 23)),
                                       ("value_bounds", (center - 23, 491, 46, 15)), ("bounds", (center - 23, 309, 46, 197))):
                        checks[f"{identity} {name}"] = float_vector_equal(control[name], mapped(*spec["logical_size"], rect))
            errors.extend("model " + name + " differs" for name, ok in checks.items() if not ok)
        except (KeyError, IndexError, TypeError) as error:
            errors.append("missing/malformed complete model: " + str(error))
    return errors


def differences(before, after):
    rgba = ImageChops.difference(before, after)
    channels = rgba.split()
    maximum = ImageChops.lighter(ImageChops.lighter(channels[0], channels[1]), ImageChops.lighter(channels[2], channels[3]))
    changed = maximum.point(lambda value: 255 if value else 0)
    return rgba, channels, maximum, changed


def difference_metrics(before, after, mask):
    rgba, channels, maximum, changed = differences(before, after)
    outside = ImageChops.darker(changed, ImageChops.invert(mask))
    protected_channels = [ImageChops.darker(channel.point(lambda v: 255 if v else 0), ImageChops.invert(mask)) for channel in channels]
    return {"different_pixels": changed.histogram()[255], "different_channels": sum(sum(c.histogram()[1:]) for c in channels),
            "maximum_channel_delta": maximum.getextrema()[1], "outside_pixels": outside.histogram()[255],
            "outside_channels": sum(c.histogram()[255] for c in protected_channels),
            "outside_box": outside.getbbox(), "passed": outside.getbbox() is None}, (rgba, maximum, outside)


def cyan_mask(image):
    channels = image.split()
    result = channels[0].point(lambda v: 255 if v == 165 else 0)
    for channel, target in zip(channels[1:], (228, 223, 255), strict=True):
        result = ImageChops.darker(result, channel.point(lambda v, t=target: 255 if v == t else 0))
    return result


def focus_equality(spec, before, after):
    a, b = cyan_mask(before), cyan_mask(after)
    count_a, count_b = a.histogram()[255], b.histogram()[255]
    delta = ImageChops.difference(a, b).histogram()[255]
    require_nonempty = spec["suite"] == "typography" and spec["case"] < 26
    return {"before_pixels": count_a, "after_pixels": count_b, "different_positions": delta,
            "before_sha256": sha(a.tobytes()), "after_sha256": sha(b.tobytes()),
            "nonempty_required": require_nonempty, "passed": delta == 0 and (not require_nonempty or count_a > 0)}


def label_observations(spec, image, phase):
    records = []
    full_required = spec["suite"] == "typography" and spec["case"] < 26
    for label in spec["labels"]:
        glyph_records, all_pixels = [], set()
        for copy in label[phase]:
            box = copy["visible_copy_box"]
            strong = []
            for y in range(box[1], box[3]):
                for x in range(box[0], box[2]):
                    r, g, b, a = image.getpixel((x, y))
                    if a == 255 and 2126 * r + 7152 * g + 722 * b > 1000000:
                        strong.append((x, y))
            all_pixels.update(strong)
            glyph_records.append({"character": copy["character"], "visible_copy_box": box,
                                  "opaque_bright_pixels": len(strong),
                                  "passed": bool(strong) if full_required else True})
        ink_box = None if not all_pixels else [min(x for x, _ in all_pixels), min(y for _, y in all_pixels),
                                              max(x for x, _ in all_pixels) + 1, max(y for _, y in all_pixels) + 1]
        records.append({"manual": label["manual"], "index": label["index"], "text": label["text"],
                        "opaque_bright_pixels": len(all_pixels), "ink_box": ink_box, "glyphs": glyph_records,
                        "nonempty_glyphs_required": full_required, "passed": all(g["passed"] for g in glyph_records)})
    return records


def material_statistics(rgb):
    width, height = rgb.size
    values = [2126 * r + 7152 * g + 722 * b for r, g, b in rgb.getdata()]
    count = len(values)
    mean = Fraction(sum(values), count * 10000)
    variance = Fraction(sum(v * v for v in values), count * 10000**2) - mean * mean
    xx = [2 * x - width + 1 for _ in range(height) for x in range(width)]
    yy = [2 * y - height + 1 for y in range(height) for _ in range(width)]
    slopes = [Fraction(2 * sum(v * q for v, q in zip(values, axis, strict=True)), 10000 * sum(q * q for q in axis)) for axis in (xx, yy)]
    return {"pixels": count, "encoded_luma_mean_exact": str(mean), "rms_squared_exact": str(variance),
            "horizontal_least_squares_slope_exact": str(slopes[0]), "vertical_least_squares_slope_exact": str(slopes[1])}


def material_equality(spec, before, after):
    if spec["suite"] != "typography" or spec["case"] != 0:
        return {"applicable": False, "passed": True}
    ox, oy = spec["viewport"][:2]
    records = []
    for name, rectangle in PATCHES.items():
        x, y, w, h = rectangle
        box = [x + ox, y + oy, x + ox + w, y + oy + h]
        a, b = before.crop(box).convert("RGB"), after.crop(box).convert("RGB")
        old, new = a.tobytes(), b.tobytes()
        old_stats, new_stats = material_statistics(a), material_statistics(b)
        records.append({"name": name, "canonical_xywh": rectangle, "before_rgb_sha256": sha(old), "after_rgb_sha256": sha(new),
                        "before_statistics": old_stats, "after_statistics": new_stats,
                        "passed": old == new and old_stats == new_stats})
    return {"applicable": True, "comparison": "Exact same-state pre/post T1 RGB and statistics; no new reference thresholds or v1 reinterpretation.",
            "patches": records, "passed": all(r["passed"] for r in records)}


def compare_case(spec, before_frame, after_frame, output):
    old_header, old_raw, old_header_sha = before_frame
    new_header, new_raw, new_header_sha = after_frame
    errors = metadata_errors(spec, old_header) + metadata_errors(spec, new_header)
    if not typed_equal(old_header, new_header): errors.append("complete before/after metadata differs")
    before = Image.frombytes("RGBA", tuple(spec["output_size"]), old_raw)
    after = Image.frombytes("RGBA", tuple(spec["output_size"]), new_raw)
    mask = allowance_mask(spec)
    require(sha(mask.tobytes()) == spec["allowance_sha256"], "declared glyph allowance changed")
    delta, images = difference_metrics(before, after, mask)
    focus = focus_equality(spec, before, after)
    labels_before, labels_after = label_observations(spec, before, "before"), label_observations(spec, after, "after")
    material = material_equality(spec, before, after)
    passed = not errors and delta["passed"] and focus["passed"] and material["passed"] and all(r["passed"] for r in labels_before + labels_after)
    artifacts = []
    if not passed:
        for suffix, image in (("before", before), ("after", after), ("absolute-rgba-difference", images[0]),
                              ("maximum-channel-difference", images[1]), ("outside-allowance-mask", images[2])):
            path = output / f"{spec['suite']}-{spec['case']:02d}-{suffix}.png"
            require(not path.exists(), "failure artifact already exists")
            image.save(path)
            artifacts.append(file_identity(path))
    return {"suite": spec["suite"], "case": spec["case"], "passed": passed, "metadata_errors": errors,
            "before_header_sha256": old_header_sha, "after_header_sha256": new_header_sha,
            "before_rgba_sha256": sha(old_raw), "after_rgba_sha256": sha(new_raw),
            "compared_pixels": spec["compared_pixels"], "allowed_pixels": spec["allowed_pixels"],
            "protected_pixels": spec["protected_pixels"], "whole_frame_equality_required": spec["whole_frame_equality_required"],
            "difference": delta, "cyan_focus": focus, "labels_before": labels_before, "labels_after": labels_after,
            "material_preservation": material, "failure_artifacts": artifacts}


def git_bytes(repo, *arguments):
    return subprocess.check_output(["git", *arguments], cwd=repo, stderr=subprocess.PIPE)


def identities(args):
    repo = args.repo
    require(file_identity(repo / CONTRACT)["sha256"] == CONTRACT_SHA, "admitted T1 contract changed")
    require(file_identity(repo / ADMISSION)["sha256"] == ADMISSION_SHA, "independent T1 admission changed")
    require(file_identity(repo / FIXTURE)["sha256"] == FIXTURE_SHA, "genuine before/candidate fixture changed")
    require(file_identity(args.before_painter)["sha256"] == BEFORE_PAINTER_SHA, "accepted Lower before painter differs")
    require(file_identity(args.before_percussion)["sha256"] == BEFORE_PERCUSSION_SHA, "accepted Lower percussion binary differs")
    require(file_identity(args.before_typography)["sha256"] == BEFORE_TYPOGRAPHY_SHA, "genuine pre-T1 typography binary differs")
    require(file_identity(args.baseline_receipt)["sha256"] == BASELINE_RECEIPT_SHA, "genuine pre-T1 qualification receipt changed")
    receipt = json.loads(args.baseline_receipt.read_bytes())
    require(receipt["status"] == "passed" and receipt["painter_sha256"] == BEFORE_PAINTER_SHA and
            receipt["contract_sha256"] == CONTRACT_SHA, "passing genuine pre-T1 receipt required")
    require(receipt["result"]["status"] == "passed" and receipt["result"]["cases"] == 44 and
            receipt["result"]["expected_typography"] == "before-centered", "before assertion mode/result differs")
    require(receipt["files"][Path(FIXTURE).name]["sha256"] == FIXTURE_SHA, "receipt fixture differs")
    require(receipt["files"]["test_standalone_footage_typography_raster"]["sha256"] == file_identity(args.before_typography)["sha256"], "before fixture executable differs from build receipt")
    common = ["apps/standalone/" + name for name in ("UiModel.cpp", "UiModel.h", "InstrumentView.h", "Drawing.cpp", "Drawing.h",
              "FontData.h", "InspectionModel.cpp", "InspectionModel.h")] + [PERCUSSION, "tools/compile_reference_art.py", "assets/standalone/reference/manifest.json"]
    current = {}
    for name in common:
        original = git_bytes(repo, "show", BASE + ":" + name)
        require(original == (repo / name).read_bytes(), "unchanged common source differs: " + name)
        current[name] = sha(original)
    for name in ("apps/standalone/InstrumentView.cpp", FIXTURE, CONTRACT, ADMISSION):
        current[name] = file_identity(repo / name)["sha256"]
    binaries = {name: file_identity(getattr(args, name)) for name in ("before_percussion", "after_percussion", "before_typography", "after_typography")}
    build = {}
    if args.build_dir:
        for name in ("CMakeCache.txt", "build.ninja", "apps/standalone/generated/ReferenceArtData.h", "_sdl2/libSDL2.a"):
            path = args.build_dir / name
            build[name] = file_identity(path) if path.is_file() else {"missing": True}
    return {"observed_head": git_bytes(repo, "rev-parse", "HEAD").decode().strip(),
            "observed_head_tree": git_bytes(repo, "rev-parse", "HEAD^{tree}").decode().strip(),
            "accepted_before_painter": file_identity(args.before_painter), "source_sha256": current,
            "binaries": binaries, "baseline_receipt": file_identity(args.baseline_receipt),
            "tool": file_identity(Path(__file__)), "build_inputs": build,
            "limit": "Hashes bind exact inputs; root's retained coherent build evidence establishes compilation. No reconstructed before painter is executed."}


def native_invariants(args):
    result = {}
    for name, arguments, count in (("before_percussion", [], 66), ("after_percussion", [], 66),
                                   ("before_typography", ["--before"], 44), ("after_typography", [], 44)):
        raw = command(getattr(args, name), arguments, max(args.timeout, 90))
        record = json.loads(raw)
        require(record.get("cases") == count and record.get("status") == "passed", "native complete invariant run failed: " + name)
        if "typography" in name:
            expected = "before-centered" if name.startswith("before") else "admitted-runs"
            require(record.get("protocol") == PROTOCOL and record.get("expected_typography") == expected, "wrong native type assertion mode")
            require(record.get("focus_cases") == 26 and record.get("opaque_child_probes") == 936 and
                    record.get("case_1_repeats") == 2 and record.get("clip_companions") == 11 and
                    record.get("literal_glyphs", 0) >= 2080, "native complete glyph/focus/clip inventory differs")
        result[name] = {"arguments": arguments, "stdout_sha256": sha(raw), "record": record}
    return result


def summarize(results):
    return {"pairs": len(results), "passed_pairs": sum(r["passed"] for r in results),
            "compared_pixels": sum(r["compared_pixels"] for r in results), "protected_pixels": sum(r["protected_pixels"] for r in results),
            "changed_pixels": sum(r["difference"]["different_pixels"] for r in results),
            "outside_pixels": sum(r["difference"]["outside_pixels"] for r in results),
            "outside_channels": sum(r["difference"]["outside_channels"] for r in results),
            "required_exact_frames": sum(r["whole_frame_equality_required"] for r in results),
            "passed_exact_frames": sum(r["whole_frame_equality_required"] and r["difference"]["different_pixels"] == 0 for r in results),
            "cyan_focus_pixels": sum(r["cyan_focus"]["after_pixels"] for r in results),
            "material_patches": sum(len(r["material_preservation"].get("patches", [])) for r in results),
            "failure_cases": [[r["suite"], r["case"]] for r in results if not r["passed"]]}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    for name in ("before-percussion", "after-percussion", "before-typography", "after-typography", "before-painter", "baseline-receipt"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--build-dir", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=45)
    args = parser.parse_args()
    start = time.monotonic()
    require(0 < args.timeout <= 120 and math.isfinite(args.timeout), "invalid bounded per-process timeout")
    require(not args.output_dir.exists(), "existing output directory refused")
    initial = identities(args)
    mask = declare_mask(font_metrics(args.repo / FONT))
    args.output_dir.mkdir(parents=True, exist_ok=False)
    write_new(args.output_dir / "mask.json", mask)
    report = {"schema": 1, "model": MODEL, "protocol": PROTOCOL, "status": "incomplete", "identities": initial,
              "mask": file_identity(args.output_dir / "mask.json"), "native_invariants": {}, "cases": [],
              "runtime": {"python": platform.python_version(), "platform": platform.platform(), "pillow": PILLOW_VERSION},
              "limits": "Finite glyph-only software comparison; native strong-glyph checks and exact foreground/state guards. Resource crops have only 64x64 output. Source statistics preserve accepted materials but do not grade reference parity. Full visual review, actual display/DPI/accessibility, whole-interface1:1 and physical/audio gates remain separate."}
    try:
        report["native_invariants"] = native_invariants(args)
        for spec in mask["cases"]:
            before = getattr(args, "before_" + spec["suite"])
            after = getattr(args, "after_" + spec["suite"])
            result = compare_case(spec, frame(before, spec["case"], args.timeout), frame(after, spec["case"], args.timeout), args.output_dir)
            report["cases"].append(result)
            retained = sum(p.stat().st_size for p in args.output_dir.rglob("*") if p.is_file())
            require(retained <= MAX_ARTIFACT_BYTES, "retained output exceeds 80 MiB cap")
        final = identities(args)
        report["identities_unchanged"] = typed_equal(initial, final)
        report["summary"] = summarize(report["cases"])
        report["status"] = "passed" if report["identities_unchanged"] and all(r["passed"] for r in report["cases"]) else "failed"
    except Exception as error:
        report["status"] = "failed"
        report["error"] = {"type": type(error).__name__, "message": str(error)}
        report["summary"] = summarize(report["cases"])
    report["seconds"] = time.monotonic() - start
    write_new(args.output_dir / "report.json", report)
    retained = sum(p.stat().st_size for p in args.output_dir.rglob("*") if p.is_file())
    require(retained <= MAX_ARTIFACT_BYTES, "final retained output exceeds 80 MiB cap")
    print(json.dumps({"status": report["status"], "summary": report["summary"], "seconds": report["seconds"],
                      "report": str(args.output_dir / "report.json"), "retained_bytes": retained}, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print("Typography comparison refused: " + str(error), file=sys.stderr)
        raise SystemExit(2)
