#!/usr/bin/env python3
"""Independent canonical source-operation reconstruction, before rim editing.

Consumes original JPEG plus actual pre-rim application PNG. Never consumes a
candidate rim render, a changed-pixel mask, or production drawing helpers.
"""
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

from PIL import Image


def f32(x):
    return struct.unpack("f", struct.pack("f", x))[0]


def mix(a, b, fraction):
    return math.floor(f32(f32(a) + f32(f32(b - a) * f32(fraction))) + 0.5)


def blend(dst, src, alpha):
    # Pinned SDL_draw.h DRAW_MUL; source and destination products separately
    # truncate. Rounded shadow spans use the same integer channel operation.
    return tuple((c * (255 - alpha)) // 255 + (s * alpha) // 255 for c, s in zip(dst, src))


def rounded_contains(x, y, bounds, radius):
    left, top, width, height = bounds
    if not top <= y < top + height:
        return False
    edge = min(y + 0.5 - top, top + height - y - 0.5)
    inset = 0.0 if edge >= radius else radius - math.sqrt(max(0.0, radius * radius - (radius - edge) ** 2))
    return math.ceil(left + inset - 0.5) <= x < math.ceil(left + width - inset - 0.5)


def shadows(x, y):
    # Later reference_panel calls which can reach the canonical 18-row band,
    # in painter order. Other panels/controls begin outside this band.
    count = 0
    for left, top, width, height in ((72, 269, 528, 239), (600, 269, 516, 239),
                                      (1126, 125, 478, 745), (232, 528, 890, 170)):
        for layer in range(5, 0, -1):
            bounds = (left - layer, top + 2 - layer, width + 2 * layer, height + 2 * layer)
            count += rounded_contains(x, y, bounds, 5 + layer)
    return count


def old_row(row):
    value = tuple(mix(a, b, f32(row / 17)) for a, b in zip((111, 64, 34), (54, 28, 17)))
    for stripe in range(2, 18, 3):
        if row == stripe:
            value = blend(value, (18, 8, 4), 15)
        if stripe % 9 == 2 and row == stripe + 1:
            value = blend(value, (223, 154, 86), 25)
    if row == 1:
        value = blend(value, (207, 140, 82), 150)
    if row >= 15:
        value = blend(value, (20, 10, 6), mix(0, 155, (row - 15) / 2))
    if row == 17:
        value = (17, 9, 5)
    return value


def main():
    repo, actual_path, output = map(Path, sys.argv[1:])
    source_path = repo / "docs/design/atlas-cover-reference.jpg"
    source = Image.open(source_path).convert("RGB")
    actual = Image.open(actual_path).convert("RGBA")
    if source.size != (1672, 941) or actual.size != source.size:
        raise ValueError("canonical dimensions required")
    actual_hash = hashlib.sha256(actual_path.read_bytes()).hexdigest()
    expected_old, expected_new = bytearray(), bytearray()
    old_mismatches = 0
    first_old_mismatch = None
    rows = []
    coverage = {}
    roi_shadow_pixels = 0
    for y in range(510, 528):
        before_source_differences = 0
        composed_source_differences = 0
        shadow_pixels = 0
        sums = {"source": [0, 0, 0], "actual_before": [0, 0, 0], "expected_after": [0, 0, 0]}
        for x in range(48, 1122):
            count = shadows(x, y)
            coverage[count] = coverage.get(count, 0) + 1
            shadow_pixels += count > 0
            roi_shadow_pixels += 48 <= x < 1121 and 515 <= y < 525 and count > 0
            before = old_row(y - 510)
            original = source.getpixel((x, y))
            after = original
            for _ in range(count):
                before = blend(before, (0, 0, 0), 16)
                after = blend(after, (0, 0, 0), 16)
            expected_old.extend(before)
            expected_new.extend(after)
            observed = actual.getpixel((x, y))
            if observed != (*before, 255):
                old_mismatches += 1
                if first_old_mismatch is None:
                    first_old_mismatch = {"xy": [x, y], "expected": [*before, 255], "actual": list(observed)}
            before_source_differences += observed != (*original, 255)
            composed_source_differences += after != original
            for name, values in (("source", original), ("actual_before", observed[:3]), ("expected_after", after)):
                for channel in range(3):
                    sums[name][channel] += values[channel]
        rows.append({"y": y, "shadow_pixels": shadow_pixels, "before_source_differences": before_source_differences,
                     "expected_after_source_differences": composed_source_differences,
                     "mean_rgb": {name: [value / 1074 for value in values] for name, values in sums.items()}})
    result = {"protocol": "A31-canonical-rim-shadow-preflight-v1", "actual_before": str(actual_path),
              "actual_before_sha256": actual_hash, "crop": [48, 510, 1074, 18],
              "raw_pixels": 19332, "unoccluded_roi": [48, 515, 1073, 10], "roi_pixels": 10730,
              "roi_shadow_pixels": roi_shadow_pixels, "shadow_layer_histogram": coverage,
              "independent_old_composition_mismatches": old_mismatches, "first_old_mismatch": first_old_mismatch,
              "independent_old_rgb_sha256": hashlib.sha256(expected_old).hexdigest(),
              "predicted_after_rgb_sha256": hashlib.sha256(expected_new).hexdigest(),
              "predicted_after_is_candidate_evidence": False, "rows": rows}
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "rows"}, indent=2))


if __name__ == "__main__":
    main()
