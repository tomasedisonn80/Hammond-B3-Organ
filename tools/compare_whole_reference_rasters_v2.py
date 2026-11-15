#!/usr/bin/env python3
"""Versioned driver adding reviewed, actual old SDL wood-line raster footprints.

The immutable v1 utility retains its original declaration and failed report.
This driver reuses its framing, identities, atomic output and RGBA accounting,
with an explicit v2 geometry provider. Each source-derived physical line box
gets exactly one device-pixel dilation; no logical parent padding is added.
"""
from __future__ import annotations

from pathlib import Path

import compare_whole_reference_rasters as v1


VERSION = "whole-reference-identical-state-raster-v2"
REVIEW = v1.SESSION + "/reports/A29-mask-extent-review.json"
PRIOR_MASK = v1.SESSION + "/reports/whole-reference-mask-v1.json"
PRIOR_REPORT = v1.SESSION + "/reports/whole-reference-raster-comparison.json"
EXPECTED_V1_TOOL = "97c006ce1ffcd3cd36d0f11ed68d5327bd68d218f9f94923233c57c0858e1637"
EXPECTED_V1_MASK = "7b17af59df15e9d2b3b5c3b744349f61c95788e6a179764736112974b9a982b3"
EXPECTED_V1_REPORT = "31a8efc1a738402a50f6f00f8eb44e65564b9ea7e02115105ce2017408e47528"
EXPECTED_REVIEW = "b6b6d9a783493a652e58213305967169032e06b977c8e8e1a437315ffdddbaec"
original_declaration = v1.declared_case
original_identity = v1.source_identity
original_freeze = v1.freeze
original_rss = v1.peak_rss


def old_cheeks(width, height):
    """Keep original binary32 widths/heights; do not subtract rounded endpoints."""
    f = v1.F32
    w, h = f(width), f(height)
    margin = min(f(72), max(f(48), w * f(.043)))
    content = w - f(2) * margin
    player = content - content * f(.311) - f(10)
    performance = min(f(110), max(f(76), f(76) + f(.12) * (h - f(700))))
    rack = min(f(236), max(f(168), f(168) + f(.24) * (h - f(700)))) + f(6)
    manual_height = (h - f(32) - f(100) - performance - rack - f(28) -
                     f(36) - f(6) * f(10)) / f(2)
    rack_y = f(126) + performance + f(10)
    toolbar_y = rack_y + rack + f(10)
    manual_y = toolbar_y + f(28) + f(10)
    rail_width = min(f(168), max(f(156), player * f(.15)))
    return [(name, margin, manual_y + f(i) * (manual_height + f(10)), rail_width, manual_height)
            for i, name in enumerate(("upper", "lower"))]


def wood_lines(x, y, width, height):
    """The original wood() calls, including secondary grain and boundary lines."""
    f = v1.F32
    right = x + width
    result = []
    for row in range(2, int(height), 3):
        line_y = y + f(row)
        result.append(("grain", x, line_y, right))
        if row % 9 == 2:
            result.append(("bright_grain", x, line_y + f(1), right))
    result.append(("top", x, y + f(1), right))
    result.append(("bottom", x, y + height - f(1), right))
    return result


def physical_line(x, y, right, scale, offset):
    """Pinned SDL 2.32.10 horizontal-line conversion, before any mask dilation."""
    f = v1.F32
    if scale == 1:
        return [offset + int(x), offset + int(y),
                offset + int(right) + 1, offset + int(y) + 1]
    s = f(scale)
    left = offset + int(x * s)
    top = offset + int(y * s)
    width = max(int(((right - x) + f(1)) * s), 1)
    height = max(int(s), 1)
    return [left, top, left + width, top + height]


def declared_case(case):
    result = original_declaration(case)
    if not case["active"]:
        return result
    vl, vt, vr, vb = result["visible_device_box"]
    for name, x, y, width, height in old_cheeks(*case["fixture"][:2]):
        for index, (kind, left, line_y, right) in enumerate(wood_lines(x, y, width, height)):
            box = physical_line(left, line_y, right, case["scale"], case["offset"])
            result["regions"].append({
                "name": f"before:{name}_wood_{index}_{kind}",
                "logical_line": list(map(float, (left, line_y, right, line_y))),
                "primitive_device_box": box,
                "device_box": [max(vl, box[0] - 1), max(vt, box[1] - 1),
                               min(vr, box[2] + 1), min(vb, box[3] + 1)],
                "reason": "Exact source-derived old SDL line raster box, then one device pixel per side; no case/failure-coordinate exception.",
            })
    return result


def source_identity(repo, base):
    result = original_identity(repo, base)
    v1.require(result["tool_sha256"] == EXPECTED_V1_TOOL, "immutable v1 utility differs")
    v1.require(v1.digest(repo / PRIOR_MASK) == EXPECTED_V1_MASK, "original v1 mask differs")
    v1.require(v1.digest(repo / PRIOR_REPORT) == EXPECTED_V1_REPORT, "original failed report differs")
    v1.require(v1.digest(repo / REVIEW) == EXPECTED_REVIEW, "independent extent admission differs")
    result.update({"v2_driver_sha256": v1.digest(Path(__file__)),
                   "v2_extent_review_sha256": v1.digest(repo / REVIEW),
                   "prior_mask_sha256": EXPECTED_V1_MASK,
                   "prior_failed_report_sha256": EXPECTED_V1_REPORT})
    return result


def freeze(args):
    result = original_freeze(args)
    result["policy"] += (" V2 also includes independently reviewed exact physical old wood-line boxes "
                         "for both cheeks in every active case, each expanded by exactly one device pixel.")
    result["correction"] = {
        "basis": REVIEW,
        "prior_failure": PRIOR_REPORT,
        "meaning": "Declared before this v2 rerun after the separately retained v1 failure; not an assertion that no v1 pixels were previously observed.",
        "scope": "All original horizontal wood() strokes in both old preset cheeks and all active cases, with original binary32 widths/heights and pinned SDL line conversion. No new candidate paint or numerical threshold exception.",
        "dilation": "Exactly one physical device pixel after raster-box derivation and before caller clip intersection.",
    }
    result["limits"] += (" The original v1 failure remains immutable. The active whole-composition "
                         "union protects very few unclipped pixels; exact inactive equality is a separate, stronger result.")
    return result


def peak_rss():
    result = original_rss()
    if result["bytes"] is not None:
        result["scope"] = "comparison Python process lifetime; excludes child helper processes"
    return result


def main():
    # These providers are process-local and explicit; the v1 file and all its
    # original evidence remain byte-for-byte unchanged and directly replayable.
    v1.MODEL = VERSION
    v1.declared_case = declared_case
    v1.source_identity = source_identity
    v1.freeze = freeze
    v1.peak_rss = peak_rss
    return v1.main()


if __name__ == "__main__":
    raise SystemExit(main())
