#!/usr/bin/env python3
r"""Independently compare the frozen post-T2/pre-T3 title against literal T3.

All 158 genuine same-state pairs are required: 44 typography, 66 percussion,
and 48 typography-clips-v1 frames. The admitted allowance is derived before
native execution from the two old and five new title passes, raw Serif metrics,
assignment-rounded binary32 arithmetic, and SDL 2.32.10 software COPY rules.
No candidate helper, difference-derived mask, dilation, divider or header box
contributes support. The T2 utility is pinned and reused only for bounded
transport, case inventories, model checks, images, and provenance utilities.

Example from the repository root (choose a new output directory):
  python3 -B tools/compare_title_typography.py \
    --before ../t2-native/test_standalone_footage_typography_raster \
    --after ../build-native/apps/standalone/test_standalone_footage_typography_raster \
    --before-percussion ../t2-native/test_standalone_percussion_raster \
    --after-percussion ../build-native/apps/standalone/test_standalone_percussion_raster \
    --before-clips ../t2-native/test_standalone_typography_clips \
    --after-clips ../build-native/apps/standalone/test_standalone_typography_clips \
    --baseline-receipt docs/development/2026-11-16-heading-title-continuation/reports/t3-baseline-identity.json \
    --before-painter ../t2-native/InstrumentView.cpp \
    --build-dir ../build-native --output /tmp/title-t3-report

The original 18 canonical typography states use an integer-translated ROI;
17 additional canonical states have the contract's literal zero origin. All
five encoded-Y' counts/bounds are recorded. The warm-ink predicate is checked
separately; the unchanged native material suite and independent actual-frame
visual admission remain required outside this finite comparison.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path
import platform
import sys
import time

from PIL import Image, __version__ as PILLOW_VERSION

import compare_heading_typography as harness

common = harness.common
f32 = common.f32
require = common.require
identity = harness.identity
sha = harness.sha
read_json = harness.read_json
write_json = harness.write_json
json_bytes = harness.json_bytes

MODEL = "title-independent-paired-raster-v1"
SESSION = "docs/development/2026-11-16-heading-title-continuation"
BASE = "113c29b7b14c8fde0859bc405ef8e4141a131ea6"
CONTRACT = "docs/design/TITLE_T3_CONTRACT.md"
ADMISSION = "docs/reviews/TITLE_T3_ADMISSION.md"
PROTECTED = SESSION + "/reports/a09-compatibility-baseline.json"
PAINTER = "apps/standalone/InstrumentView.cpp"
FONT = "apps/standalone/FontData.h"
REFERENCE = "docs/design/atlas-cover-reference.jpg"
MATERIAL = "apps/standalone/native_tests/test_standalone_material_acceptance.cpp"
MAIN = "apps/standalone/main.cpp"
BEFORE_PAINTER_SHA = "94186192085435a756f9e1854e3aefe807407befa49e1cc978c07968436ca5db"
MAIN_SHA = "89b24fdeae438b77309904d12c32e3e2ae5e964e99968a8656c5b0a710e237c4"
PINNED = {
    CONTRACT: "6e45c095331e4d2a32cb111ebe2be74b7fad3dd7f6fb89a675d68c4a0310cae7",
    ADMISSION: "9ccc570fd333b404a0774b0398d437b534011cd312dfae4468831dc50cf2b425",
    PROTECTED: "7cdfb46aea8c3682b688ef965840af5ff76f46275add323f4aac783fcdbbf2c6",
    FONT: "f1a3121a2707a03a3b2e025c399e68c553ce9498f4b002ec13b18f512e334802",
    REFERENCE: "9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187",
    MATERIAL: "78429c3e9ccc7fb3d469b871a0e8cc6bd50683383c03ffdc837686c30b684fea",
    MAIN: MAIN_SHA,
    harness.FIXTURE: "facc85f516454964ed55e406f95db4046923d7a2441fdf72e65719b3685fec4f",
    harness.PERCUSSION: "a96b3c43d64aee7409249141bc1bd6b0812ca3c906b46c7f41cd8030f5390dc8",
    harness.CLIPS: "d1635b45f7ee395e172f01e50ae44d7815cc8c62e5aa2443f91a6cffdb147672",
    "apps/standalone/Drawing.cpp": "666e998cc61a9d501238783c8f2917d9be30db0bac76739f91bc23eb54f34b0a",
    "apps/standalone/UiModel.cpp": "0ecb0c4ee90d98cdb87c6f06b4685d368a7c12b72f9ea66e6c40228a4a855ecd",
    "apps/standalone/UiModel.h": "6d8c0b16ddb6f3059dc14aff41bfc615e37b43c53b2f6e88cc199255a6b674b1",
    "tools/compare_heading_typography.py": "e809a3e052efa5916e1ce6f20b1ef0a5560fc50b423f0759ba705d0650aaf886",
    "tools/compare_footage_typography.py": "768ad4a5c022038c75414527961d5437bc3990a11d80772ce6fed6fc5a1534a1",
}
REQUIRED_PAIRS = {"typography": 44, "percussion": 66, "clips": 48}
EXECUTABLES = {"typography": "test_standalone_footage_typography_raster",
               "percussion": "test_standalone_percussion_raster",
               "clips": "test_standalone_typography_clips"}
TITLE = "TONEWHEEL ATLAS"
ROI = (590, 14, 490, 46)
THRESHOLDS = (80, 100, 120, 140, 160)
REFERENCE_COUNTS = (5639, 5415, 4991, 4502, 3785)
BEFORE_COUNTS = (4150, 3863, 3601, 3200, 2690)
REFERENCE_BOUNDS_100 = [603, 20, 1067, 53]
BEFORE_BOUNDS_100 = [602, 20, 1065, 53]
MAX_PIXELS = 3900 * 2200
MAX_ERROR_CHARACTERS = 4096


def bounded_errors(errors):
    """Keep failed-input diagnostics bounded independently of header contents."""
    truncated = sum(len(str(error)) for error in errors) > MAX_ERROR_CHARACTERS
    marker = "[remaining diagnostics omitted at the fixed per-pair bound]"
    result, remaining = [], MAX_ERROR_CHARACTERS - (len(marker) if truncated else 0)
    for error in errors:
        if remaining == 0:
            break
        text = str(error)
        result.append(text[:remaining])
        remaining -= len(result[-1])
    if truncated:
        result.append(marker)
    return result


def text_width(text, size, glyphs):
    """Literal Drawing::text_width assignments, from raw atlas advance_64."""
    scale = f32(size / 40)
    width = 0.0
    for char in text:
        width = f32(width + f32(f32(float(glyphs[char][6]) * scale) / 64))
    return width


def title_runs(width, height, glyphs):
    """Frozen layout/control exclusions and contract arguments; no painter read."""
    sx, sy = f32(width / 1672), f32(height / 941)
    font_scale = min(sx, sy)
    # UiModel maps endpoints before subtracting widths; preserve that order.
    workspace_service = common.mapped(width, height, (380, 50, 130, 46))
    save = common.mapped(width, height, (1312, 25, 88, 28))
    title_left = f32(f32(workspace_service[0] + workspace_service[2]) + f32(12 * sx))
    title_right = f32(save[0] - f32(12 * sx))
    middle = f32(836 * sx)
    half_width = max(0.0, min(f32(middle - title_left), f32(title_right - middle)))
    title_left, title_right = f32(middle - half_width), f32(middle + half_width)
    size = f32(42.75 * font_scale)
    natural = text_width(TITLE, size, glyphs)
    available = f32(title_right - title_left)
    if natural > available:
        size = f32(size * f32(available / natural))
    measured = text_width(TITLE, size, glyphs)
    x = min(max(f32(middle - f32(measured / 2)), title_left), max(title_left, f32(title_right - measured)))
    y = f32(11.5 * sy)

    def run(purpose, left, top, rgba):
        return {"purpose": purpose, "text": TITLE, "x": left, "top": top, "size": size, "rgba": list(rgba)}

    shadow = run("cast-shadow", f32(x + sx), f32(y + f32(2 * sy)), (4, 5, 4, 255))
    before = [dict(shadow), run("old-brass-face", x, y, (214, 182, 124, 255))]
    after = [dict(shadow),
             run("lower-dark-bevel", f32(x + font_scale), f32(y + font_scale), (100, 65, 28, 255)),
             run("upper-highlight", x, f32(y - f32(.5 * font_scale)), (255, 231, 184, 255)),
             run("added-stroke-weight", f32(x + font_scale), y, (212, 171, 103, 255)),
             run("main-brass-face", x, y, (226, 192, 135, 255))]
    return {"text": TITLE, "scale_binary32": [sx, sy, font_scale],
            "service_control_binary32": workspace_service, "save_control_binary32": save,
            "title_interval_binary32": [title_left, title_right], "size_binary32": size,
            "natural_width_binary32": natural, "width_binary32": measured,
            "anchor_binary32": [x, y], "before": before, "after": after}


def glyph_copies(run, glyphs):
    """Drawing::text COPY rectangles, independently transcribed for T3."""
    scale = f32(run["size"] / 40)
    baseline = f32(run["top"] + f32(38 * scale))
    pen = run["x"]
    result = []
    for index, char in enumerate(run["text"]):
        ax, ay, width, height, bx, by, advance = glyphs[char]
        if width and height:
            px = 2 if f32(width * scale) < 1 else 0
            py = 2 if f32(height * scale) < 1 else 0
            result.append({"index": index, "character": char,
                           "atlas_xywh": [ax - px, ay - py, width + 2 * px, height + 2 * py],
                           "target_binary32": [f32(pen + f32((bx - px) * scale)),
                                               f32(baseline + f32((by - py) * scale)),
                                               f32((width + 2 * px) * scale),
                                               f32((height + 2 * py) * scale)]})
        pen = f32(pen + f32(f32(float(advance) * scale) / 64))
    return result


def copy_destination(rectangle, scale, origin):
    """SDL software COPY: scale each component, truncate, then add viewport."""
    x, y, width, height = [math.trunc(f32(value * factor)) for value, factor in
                          zip(rectangle, (*scale, *scale), strict=True)]
    x, y = x + origin[0], y + origin[1]
    if rectangle[2] <= 0 or rectangle[3] <= 0 or width <= 0 or height <= 0:
        return [x, y, x, y]
    return [x, y, x + width, y + height]


def declare_case(case, glyphs):
    spec = dict(case)
    width, height = spec["output_size"]
    require(0 < width <= 3900 and 0 < height <= 2200 and width * height <= MAX_PIXELS,
            "declared frame exceeds the fixed domain")
    origin = spec["viewport"][:2]
    visible = common.intersect([0, 0, width, height], common.xywh(spec["viewport"]))
    if spec["clip_enabled"]:
        x, y, w, h = spec["clip"]
        visible = common.intersect(visible, [x + origin[0], y + origin[1],
                                             x + origin[0] + w, y + origin[1] + h])
    spec.update({"visible_device_box": visible, "labels": [], "title": None,
                 "allowed_rectangles": [], "compared_pixels": width * height})
    if spec["active"]:
        title = title_runs(*spec["logical_size"], glyphs)
        for phase, expected in (("before", 28), ("after", 70)):
            copies = 0
            for run in title[phase]:
                run["copies"] = glyph_copies(run, glyphs)
                copies += len(run["copies"])
                for operation in run["copies"]:
                    device = copy_destination(operation["target_binary32"], spec["scale"], origin)
                    clipped = common.intersect(device, visible)
                    operation.update({"device_box": device, "visible_box": clipped})
                    if common.area(clipped):
                        spec["allowed_rectangles"].append(tuple(clipped))
            require(copies == expected, "title glyph COPY inventory differs")
        spec["title"] = title
    spec["allowed_rectangles"] = sorted(set(spec["allowed_rectangles"]))
    mask = common.allowance_mask(spec)
    spec["allowed_pixels"] = mask.histogram()[255]
    spec["protected_pixels"] = width * height - spec["allowed_pixels"]
    spec["allowance_sha256"] = sha(mask.tobytes())
    spec["allowance_bounds"] = list(mask.getbbox()) if mask.getbbox() else None
    spec["whole_frame_equality_required"] = spec["allowed_pixels"] == 0
    return spec


def encoded_y(image, roi=ROI, origin=(0, 0)):
    """Frozen encoded Y' predicate; no hue restriction or resampling."""
    x, y, width, height = roi
    box = (x + origin[0], y + origin[1], x + origin[0] + width, y + origin[1] + height)
    require(box[0] >= 0 and box[1] >= 0 and box[2] <= image.width and box[3] <= image.height,
            "density ROI must be fully present")
    pixels = list(image.crop(box).convert("RGB").getdata())
    records = []
    for threshold in THRESHOLDS:
        count, left, top, right, bottom = 0, width, height, 0, 0
        for index, (r, g, b) in enumerate(pixels):
            if 2126 * r + 7152 * g + 722 * b >= threshold * 10000:
                px, py = index % width, index // width
                count += 1
                left, top, right, bottom = min(left, px), min(top, py), max(right, px + 1), max(bottom, py + 1)
        records.append({"threshold": threshold, "pixels": count,
                        "bounds": [x + left, y + top, x + right, y + bottom] if count else None})
    return records


def canonical_cohort(spec):
    if spec["suite"] == "typography" and spec["case"] < 18:
        return "original-18-integer-translated"
    if ((spec["suite"] == "percussion" and spec["case"] < 16) or
            (spec["suite"] == "clips" and spec["case"] == 46)):
        return "literal-zero-origin"
    return None


def density(spec, before, after):
    cohort = canonical_cohort(spec)
    if cohort is None:
        return {"applicable": False, "passed": True}
    require(spec["logical_size"] == [1672, 941] and spec["scale"] == [1, 1] and
            spec["active"] and not spec["clip_enabled"], "canonical density case drifted")
    origin = spec["viewport"][:2]
    a, b = encoded_y(before, origin=origin), encoded_y(after, origin=origin)
    baseline = [row["pixels"] for row in a] == list(BEFORE_COUNTS) and a[1]["bounds"] == BEFORE_BOUNDS_100
    original_error = abs(REFERENCE_COUNTS[1] - BEFORE_COUNTS[1])
    candidate_error = abs(REFERENCE_COUNTS[1] - b[1]["pixels"])
    # Integer inequality avoids a rounded floating percentage deciding the gate.
    improvement = 5 * candidate_error <= 3 * original_error
    band = 4500 <= b[1]["pixels"] <= 6000
    return {"applicable": True, "cohort": cohort, "roi_xywh": list(ROI), "viewport_origin": origin,
            "bounds_coordinates": "logical canonical coordinates after subtracting integer viewport origin",
            "predicate": "2126*R+7152*G+722*B >= threshold*10000; no hue predicate",
            "before": a, "after": b, "reference_counts": list(REFERENCE_COUNTS),
            "baseline_reproduced": baseline, "primary_band": [4500, 6000], "primary_band_passed": band,
            "original_absolute_count_error": original_error, "candidate_absolute_count_error": candidate_error,
            "error_reduction_fraction": (original_error - candidate_error) / original_error,
            "minimum_error_reduction": .4, "error_reduction_passed": improvement,
            "passed": baseline and band and improvement}


def warm_region(image, roi, origin):
    x, y, width, height = roi
    crop = image.crop((x + origin[0], y + origin[1], x + origin[0] + width, y + origin[1] + height)).convert("RGB")
    points = [(x + index % width, y + index // width) for index, (r, g, b) in enumerate(crop.getdata())
              if r >= 130 and g >= 105 and r >= g and 10 * b <= 9 * r]
    bounds = ([min(p[0] for p in points), min(p[1] for p in points),
               max(p[0] for p in points) + 1, max(p[1] for p in points) + 1] if points else None)
    columns = {p[0] for p in points}
    letters = sum(column - 1 not in columns for column in columns)
    header = (72, 10, 1528, 102)
    controls = [(100 + 140 * index, 50, 130, 46) for index in range(3)]
    controls += [(1312 + 97 * (index % 3), 25 + 36 * (index // 3), 88, 28) for index in range(6)]
    controls += [(1228, 78, 70, 24)]

    def inside(point, rect):
        return rect[0] <= point[0] < rect[0] + rect[2] and rect[1] <= point[1] < rect[1] + rect[3]

    return {"pixels": len(points), "bounds": bounds, "column_groups": letters,
            "outside_header": sum(not inside(point, header) for point in points),
            "on_controls": sum(inside(point, control) for point in points for control in controls)}


def warm_geometry(spec, image):
    if canonical_cohort(spec) is None:
        return {"applicable": False, "passed": True}
    title = warm_region(image, (576, 16, 520, 46), spec["viewport"][:2])
    caption = warm_region(image, (616, 64, 440, 24), spec["viewport"][:2])
    t, c = title["bounds"], caption["bounds"]
    title_ok = bool(t) and title["pixels"] > 1000 and abs(t[2] - t[0] - 464) <= 3 and abs(t[3] - t[1] - 33) <= 1 and abs(t[1] - 20) <= 1 and abs((t[0] + t[2]) / 2 - 835) <= 2
    caption_ok = bool(c) and caption["pixels"] > 300 and abs(c[2] - c[0] - 371) <= 4 and abs(c[3] - c[1] - 12) <= 1 and abs(c[1] - 71) <= 1 and abs((c[0] + c[2]) / 2 - 835.5) <= 2
    separation = bool(t and c) and t[3] < c[1] and c[2] <= 1218
    containment = all(record["outside_header"] == record["on_controls"] == 0 for record in (title, caption))
    return {"applicable": True, "predicate": "R>=130,G>=105,R>=G,10*B<=9*R",
            "title": title, "caption": caption, "title_geometry_passed": title_ok,
            "caption_geometry_passed": caption_ok, "caption_letters_passed": caption["column_groups"] == 15,
            "containment_passed": containment, "separation_passed": separation,
            "passed": title_ok and caption_ok and separation and containment and caption["column_groups"] == 15,
            "scope": "Canonical warm-ink checks only; unchanged native material suite remains separately required."}


def metadata_errors(spec, header):
    errors = harness.metadata_errors(spec, header)
    if spec["suite"] != "typography":
        return errors
    try:
        model = header["model"]
        require(set(model) == {"view", "layout"}, "complete model sections")
        view, layout = model["view"], model["layout"]
        require(set(view) == set("controls applied edited_banks focus roving_manual_keys roving_pedal_key keyboard_target manual_base_midi pedal_octave controls_pending controls_dirty text_entry_active pointer_captured input_recovery last_submit_status workspace presentation workspace_focus".split()), "complete view fields")
        require(set(layout) == set("width height show_cabinet bank_controls_in_cheeks sidebar_pedals header registration_panels performance_panel keyboard_toolbar manual_panels pedal_panel footer cabinet_panel cabinet_art manual_rail_panels control_count controls manual_keys pedal_keys preset_key_panels workspace presentation workspace_panel".split()), "complete layout fields")
        for control in layout["controls"]:
            require(set(control) == {"id", "bounds", "label_bounds", "value_bounds", "track"}, "complete control geometry")
        for keys in [*layout["manual_keys"], layout["pedal_keys"]]:
            for key in keys:
                require(set(key) == {"note", "bounds", "accidental", "hit", "top", "front"}, "complete key geometry")
        applied = view["applied"]
        counters = set("resolved_sequence last_applied_sequence recovery_count queue_overflows rejected_commands discarded_commands fault_flags last_core_status".split())
        require(set(applied) == counters | {"controls", "held_keys", "held_pedals", "frame_clock", "sample_rate", "peak", "prepared", "running", "publication_revision"}, "complete copied session")
        require(all(type(applied[key]) is int and applied[key] == 0 for key in counters), "unchanged session counters")
        for desired, controls in ((True, view["controls"]), (False, applied["controls"])):
            require(common.typed_equal(controls, harness.clip_controls(spec, desired=desired)), "complete desired/applied controls")
    except (ValueError, KeyError, IndexError, TypeError) as error:
        errors.append("missing/malformed complete typography model: " + str(error))
    return errors


def compare_pair(spec, old, new, timeout, artifacts):
    ah, ar, ahash = harness.frame(old, spec["case"], timeout)
    bh, br, bhash = harness.frame(new, spec["case"], timeout)
    errors = ["before " + error for error in metadata_errors(spec, ah)]
    errors.extend("after " + error for error in metadata_errors(spec, bh))
    metadata_equal = common.typed_equal(ah, bh)
    if not metadata_equal:
        errors.append("complete before/after metadata/state/geometry differ")
    require([ah["width"], ah["height"]] == [bh["width"], bh["height"]] == spec["output_size"],
            "frame dimensions disagree with frozen declaration")
    before = Image.frombytes("RGBA", tuple(spec["output_size"]), ar)
    after = Image.frombytes("RGBA", tuple(spec["output_size"]), br)
    mask = common.allowance_mask(spec)
    require(sha(mask.tobytes()) == spec["allowance_sha256"], "frozen allowance identity changed")
    metrics, (_, _, outside) = common.difference_metrics(before, after, mask)
    counts = density(spec, before, after)
    warm = {"before": warm_geometry(spec, before), "after": warm_geometry(spec, after)}
    clip = {"before": harness.caller_clip_preserved(spec, before), "after": harness.caller_clip_preserved(spec, after)}
    exact = not spec["whole_frame_equality_required"] or ar == br
    result = {"suite": spec["suite"], "case": spec["case"], "active": spec["active"],
              "metadata_errors": bounded_errors(errors), "metadata_error_count": len(errors),
              "metadata_equal": metadata_equal,
              "complete_model_available": spec["suite"] in ("typography", "clips"),
              "before_header_sha256": ahash, "after_header_sha256": bhash,
              "before_rgba_sha256": sha(ar), "after_rgba_sha256": sha(br),
              "before_model_sha256": sha(json_bytes(ah["model"])) if "model" in ah else None,
              "after_model_sha256": sha(json_bytes(bh["model"])) if "model" in bh else None,
              "allowance_sha256": spec["allowance_sha256"], "allowed_pixels": spec["allowed_pixels"],
              "protected_pixels": spec["protected_pixels"], "metrics": metrics, "density": counts,
              "warm_geometry": warm, "caller_clip_preservation": clip,
              "whole_frame_equality_required": spec["whole_frame_equality_required"],
              "whole_frame_equality_passed": exact,
              "passed": not errors and metrics["passed"] and exact and counts["passed"] and
                        all(item["passed"] for item in [*warm.values(), *clip.values()])}
    if not result["passed"]:
        result["artifacts"] = artifacts.save(f"{spec['suite']}-{spec['case']:03d}",
                                              (("before", before), ("after", after), ("outside", outside)))
    return result


def baseline_inputs(root, receipt_path, before_painter, suites, source_files):
    receipt_identity = identity(receipt_path)
    require(receipt_identity["bytes"] <= harness.MAX_HEADER, "baseline receipt exceeds fixed bound")
    receipt = read_json(receipt_path.read_bytes())
    sources = receipt.get("source_sha256", {})
    require(receipt.get("base_commit") == BASE and sources.get(PAINTER) == BEFORE_PAINTER_SHA and
            sources.get(MAIN) == MAIN_SHA, "not the accepted post-T2/replay-repaired pre-T3 source")
    require(before_painter["sha256"] == BEFORE_PAINTER_SHA, "frozen pre-T3 painter differs")
    inventory = read_json((root / PROTECTED).read_bytes())
    protected = {name: record for group in inventory["groups"].values() for name, record in group["files"].items()}
    require(len(protected) == 213 and PAINTER not in protected, "protected inventory differs")
    for name, original in protected.items():
        current = identity(root / name)
        expected = MAIN_SHA if name == MAIN else original["sha256"]
        require(current["sha256"] == sources.get(name) == expected, "protected pre/post-T3 input differs: " + name)
        if name != MAIN:
            require(current["bytes"] == original["bytes"], "protected byte count differs: " + name)
        source_files[name] = current
    binaries = {}
    for suite, old, new, _ in suites:
        require(old != new, "before/after executables must be distinct files")
        pair = {"before": identity(old), "after": identity(new)}
        expected = receipt.get("files", {}).get(EXECUTABLES[suite], {})
        require(all(pair["before"][key] == expected.get(key) for key in ("sha256", "bytes")),
                "genuine pre-T3 executable receipt mismatch: " + suite)
        binaries[suite] = pair
    # The app is retained as an actual-build identity; this tool executes fixtures.
    suffix = ".exe" if suites[0][1].suffix == ".exe" else ""
    app = identity(suites[0][1].parent / ("hammond_standalone" + suffix))
    expected = receipt.get("files", {}).get("hammond_standalone", {})
    require(all(app[key] == expected.get(key) for key in ("sha256", "bytes")), "genuine baseline app receipt mismatch")
    return {"receipt": receipt_identity, "before_painter": before_painter, "baseline_app": app,
            "binaries": binaries, "protected_count": len(protected),
            "main_repair": "Identical accepted 89b24f source on both T3 sides; separate exception to original session baseline."}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--before", required=True, type=Path, help="genuine post-T2/pre-T3 44-case fixture")
    parser.add_argument("--after", required=True, type=Path)
    for suite in ("percussion", "clips"):
        parser.add_argument("--before-" + suite, required=True, type=Path)
        parser.add_argument("--after-" + suite, required=True, type=Path)
    parser.add_argument("--baseline-receipt", type=Path)
    parser.add_argument("--before-painter", type=Path)
    parser.add_argument("--source-root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--build-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path, help="new directory; existing evidence is never overwritten")
    parser.add_argument("--timeout", type=float, default=60)
    parser.add_argument("--failure-png-budget-mib", type=int, default=32)
    args = parser.parse_args()
    require(0 < args.timeout <= 120, "timeout must be in (0,120] seconds")
    require(0 <= args.failure_png_budget_mib <= 64, "failure PNG budget must be 0..64 MiB")
    root, build_dir = args.source_root.resolve(strict=True), args.build_dir.resolve(strict=True)
    before, after = args.before.resolve(strict=True), args.after.resolve(strict=True)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    artifacts = harness.FailureArtifacts(output, args.failure_png_budget_mib * 1024 * 1024)
    report = {"schema": 1, "model": MODEL, "status": "failed", "results": [], "failures": [],
              "coverage": {"required_suites": REQUIRED_PAIRS, "required_pairs": 158,
                           "full_t3_matrix_complete": False, "inputs_unchanged": False},
              "separate_gates": {"native_material_acceptance": "Required separately at coherent candidate source; not run here.",
                                 "actual_frame_visual_admission": "Required separately with actual full reference/before/after images.",
                                 "literal_five_pass_implementation_review": "Required separately; candidate helper is not an oracle."},
              "limitations": ["Finite software raster evidence does not establish whole-interface 1:1, real display/DPI, accessibility, audio fidelity or release qualification.",
                              "Only typography and clips expose complete model/state; 66 percussion pairs expose limited metadata.",
                              "Maximum-size fixtures are 64x64 rack crops with no visible title; they prove exact crop preservation, not maximum-window title rendering or containment.",
                              "Canonical Y' density and warm-ink geometry are separate predicates; 24 complete and 16 clipped native material header cases remain separately required.",
                              "Clipped pairs use each actual SDL copy result; no uncut resampling is used as a clipped-pixel oracle."]}
    try:
        source_files = {name: identity(root / name) for name in PINNED}
        require(all(source_files[name]["sha256"] == digest for name, digest in PINNED.items()),
                "pinned contract, review, glyph/layout, protocol, inventory or utility source differs")
        require(Path(harness.__file__).resolve() == root / "tools/compare_heading_typography.py" and
                Path(common.__file__).resolve() == root / "tools/compare_footage_typography.py", "utility imported from wrong source root")
        source_files[PAINTER] = identity(root / PAINTER)
        source_files["tools/compare_title_typography.py"] = identity(Path(__file__))
        suites = [("typography", before, after, common.typography_cases()),
                  ("percussion", args.before_percussion.resolve(strict=True), args.after_percussion.resolve(strict=True), common.percussion_cases()),
                  ("clips", args.before_clips.resolve(strict=True), args.after_clips.resolve(strict=True), harness.clip_cases())]
        before_painter = identity(args.before_painter or before.parent / "InstrumentView.cpp")
        receipt_path = (args.baseline_receipt or root / SESSION / "reports/t3-baseline-identity.json").resolve(strict=True)
        baseline = baseline_inputs(root, receipt_path, before_painter, suites, source_files)
        build = harness.build_identities(build_dir)
        for suite, _, new, _ in suites:
            name = EXECUTABLES[suite]
            require(new == (build_dir / "apps/standalone" / new.name).resolve(strict=True), "candidate fixture is outside declared build")
            target_dir = build_dir / "apps/standalone/CMakeFiles" / (name + ".dir")
            build["files"].extend(identity(target_dir / path) for path in
                                  ("flags.make", "link.txt", "InstrumentView.cpp.o", "native_tests/" + name + ".cpp.o"))
        suffix = ".exe" if after.suffix == ".exe" else ""
        build["files"].append(identity(build_dir / "apps/standalone" / ("hammond_standalone" + suffix)))
        glyphs = common.font_metrics(root / FONT)
        reference = encoded_y(Image.open(root / REFERENCE).convert("RGB"))
        require([row["pixels"] for row in reference] == list(REFERENCE_COUNTS) and
                reference[1]["bounds"] == REFERENCE_BOUNDS_100, "reference decode differs from frozen admission")
        cases = [declare_case(case, glyphs) for _, _, _, inventory in suites for case in inventory]
        canonical = next(case for case in cases if case["suite"] == "clips" and case["case"] == 46)
        require(canonical["allowed_pixels"] == 14102 and canonical["allowance_bounds"] == [602, 19, 1067, 55],
                "canonical independently admitted COPY union differs")
        declaration = {"schema": 1, "model": MODEL, "contract_sha256": PINNED[CONTRACT],
                       "method": "Exact binary32 old-two/new-five title glyph COPY union, then physical target/viewport/enabled-clip intersection. No other allowance.",
                       "font_sha256": PINNED[FONT], "old_copies": 28, "new_copies": 70, "added_copies": 42,
                       "cases": cases}
        declared = write_json(output / "mask-declaration.json", declaration)
        report["inputs"] = {"sources": source_files, "baseline": baseline, "build": build,
                            "python": platform.python_version(), "platform": platform.platform(), "pillow": PILLOW_VERSION,
                            "reference_observations": reference, "mask_declaration": declared}
        write_json(output / "input-identities.json", report["inputs"])
        # Frozen declarations and source/binary receipts exist before native calls.
        inventories = {}
        for suite, old, new, inventory in suites:
            inventories[suite] = {"before": harness.check_inventory(suite, old, inventory, args.timeout),
                                  "after": harness.check_inventory(suite, new, inventory, args.timeout)}
            require(common.typed_equal(inventories[suite]["before"]["record"], inventories[suite]["after"]["record"]),
                    "before/after fixture inventory differs")
        write_json(output / "fixture-inventories.json", inventories)
        clip_specs = [case for case in cases if case["suite"] == "clips"]
        clip_assertions = {phase: harness.check_clip_assertions(executable, clip_specs, args.timeout)
                           for phase, executable in zip(("before", "after"), suites[2][1:3], strict=True)}
        write_json(output / "clip-fixture-assertions.json", clip_assertions)
        report["clip_fixture_assertions"] = clip_assertions
        pairs = {suite: (old, new) for suite, old, new, _ in suites}
        for spec in cases:
            try:
                result = compare_pair(spec, *pairs[spec["suite"]], args.timeout, artifacts)
            except (ValueError, OSError, KeyError, TypeError, IndexError) as error:
                result = {"suite": spec["suite"], "case": spec["case"], "passed": False,
                          "error": str(error)[:MAX_ERROR_CHARACTERS]}
            report["results"].append(result)
            print(f"{spec['suite']} {spec['case']:02d}: {'passed' if result['passed'] else 'FAILED'}", flush=True)
        results = report["results"]
        density_results = [item["density"] for item in results if item.get("density", {}).get("applicable")]
        coverage = report["coverage"]
        coverage.update({"declared_pairs": len(cases), "attempted_pairs": len(results),
                         "completed_pairs": sum("metrics" in item for item in results),
                         "complete_model_pairs": sum(item.get("complete_model_available", False) for item in results),
                         "canonical_original_18_density_pairs": sum(item["cohort"] == "original-18-integer-translated" for item in density_results),
                         "canonical_zero_origin_density_pairs": sum(item["cohort"] == "literal-zero-origin" for item in density_results),
                         "canonical_warm_geometry_pairs": sum(item.get("warm_geometry", {}).get("after", {}).get("applicable", False) for item in results),
                         "inactive_pairs": sum(not case["active"] for case in cases),
                         "whole_frame_exact_pairs": sum(case["whole_frame_equality_required"] for case in cases),
                         "partial_title_clip_pairs": sum(case["region"] == "title" and case["clip_kind"] in ("left", "right", "top", "bottom") for case in clip_specs),
                         "rack_heading_preservation_clip_pairs": sum(case["region"] in ("upper", "lower") and case["clip_kind"] in ("left", "right", "top", "bottom", "left-rule", "right-rule") for case in clip_specs),
                         "empty_or_disjoint_clip_pairs": sum(case["clip_kind"].startswith("empty") or case["clip_kind"] == "disjoint" for case in clip_specs),
                         "clip_assertion_runs_passed": sum(item["passed"] for item in clip_assertions.values()),
                         "protected_inputs": baseline["protected_count"],
                         "compared_pixels": sum(case["compared_pixels"] for case in cases),
                         "allowed_pixels": sum(case["allowed_pixels"] for case in cases),
                         "changed_pixels": sum(item.get("metrics", {}).get("different_pixels", 0) for item in results),
                         "outside_pixels": sum(item.get("metrics", {}).get("outside_pixels", 0) for item in results)})
        watched = [*source_files.values(), before_painter, baseline["receipt"], baseline["baseline_app"],
                   *build["files"], *(value for pair in baseline["binaries"].values() for value in pair.values())]
        drift = [item["path"] for item in watched if identity(item["path"]) != item]
        require(not drift, "inputs changed during comparison: " + ", ".join(drift))
        coverage["inputs_unchanged"] = True
        expected_pairs = {(suite, index) for suite, count in REQUIRED_PAIRS.items() for index in range(count)}
        coverage["full_t3_matrix_complete"] = (all(item["passed"] for item in results) and
            len(results) == len(expected_pairs) == coverage["completed_pairs"] == 158 and
            {(item["suite"], item["case"]) for item in results} == expected_pairs and
            coverage["complete_model_pairs"] == 92 and coverage["canonical_original_18_density_pairs"] == 18 and
            coverage["canonical_zero_origin_density_pairs"] == 17 and coverage["canonical_warm_geometry_pairs"] == 35 and
            coverage["partial_title_clip_pairs"] == 8 and coverage["rack_heading_preservation_clip_pairs"] == 24 and
            coverage["empty_or_disjoint_clip_pairs"] == 8 and coverage["clip_assertion_runs_passed"] == 2)
        report["status"] = "passed" if coverage["full_t3_matrix_complete"] else "failed"
    except (ValueError, OSError, KeyError, TypeError, IndexError) as error:
        report["failures"].append(str(error))
    report["elapsed_seconds"] = round(time.monotonic() - started, 3)
    report["failure_png_bytes"] = artifacts.used
    report["storage_bounds"] = {"failure_png_budget_bytes": artifacts.limit, "per_json_max_bytes": harness.MAX_JSON_BYTES,
                                "json_file_count_max": 5, "raw_frames_retained": 0,
                                "per_process_stdout_max_bytes": harness.MAX_FRAME,
                                "per_process_stderr_max_bytes": harness.MAX_STDERR,
                                "per_process_timeout_seconds": args.timeout,
                                "native_invocations_max": 324,
                                "per_pair_diagnostic_character_bound": MAX_ERROR_CHARACTERS,
                                "processes_in_parallel": 1}
    write_json(output / "report.json", report)
    print(json_bytes({"status": report["status"], "pairs": len(report["results"]),
                      "failures": report["failures"], "report": str(output / "report.json")}).decode().strip(), flush=True)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError) as error:
        print("title comparison: " + str(error), file=sys.stderr)
        sys.exit(1)
