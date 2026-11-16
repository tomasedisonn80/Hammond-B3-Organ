#!/usr/bin/env python3
"""Pre-edit independent matrix/source-support declaration; consumes no frames."""
import json
import math
from pathlib import Path
import struct
import sys


def f(x):
    return struct.unpack("f", struct.pack("f", x))[0]


def operations(width, height, sx, sy):
    wx, wy = f(width / 1672), f(height / 941)
    left, top = f(48 * wx), f(510 * wy)
    rw, rh = f(f(1122 * wx) - left), f(f(528 * wy) - top)
    result = []

    def fill(name, y, h):
        result.append({"kind": "fill", "name": name,
                       "box": [int(f(left * sx)), int(f(y * sy)),
                               max(1, int(f(rw * sx))), max(1, int(f(h * sy)))]})

    def gradient(name, y, h):
        x0, y0 = math.ceil(left * sx - .5), math.ceil(y * sy - .5)
        result.append({"kind": "gradient", "name": name,
                       "box": [x0, y0, math.ceil((left + rw) * sx - .5) - x0,
                               math.ceil((y + h) * sy - .5) - y0]})

    gradient("base", top, rh)
    for row in range(2, int(f(rh / wy)), 3):
        y = f(top + f(row * wy))
        fill(f"stripe-{row}", y, wy)
        if row % 9 == 2:
            fill(f"grain-highlight-{row}", f(y + wy), wy)
    fill("crest", f(top + wy), wy)
    underside = min(f(3 * wy), rh)
    gradient("underside", f(f(top + rh) - underside), underside)
    fill("bottom", f(f(top + rh) - wy), wy)
    copy = [int(f(left * sx)), int(f(top * sy)), int(f(rw * sx)), int(f(rh * sy))]
    result.append({"kind": "copy", "name": "keyboard-rim", "box": copy})
    x0 = min(op["box"][0] for op in result)
    y0 = min(op["box"][1] for op in result)
    x1 = max(op["box"][0] + op["box"][2] for op in result)
    y1 = max(op["box"][1] + op["box"][3] for op in result)
    return [left, top, rw, rh], result, [x0, y0, x1 - x0, y1 - y0]


def main():
    rows = []

    def add(width=1672, height=941, scale=(1, 1), level=4, route="B", pending=False,
            held=True, origin=(13, 17), clip="disabled", resource=False, manual="Lower"):
        rows.append(dict(logical_size=[width, height], scale=list(scale), level=level, route=route,
                         pending=pending, held=held, origin=list(origin), clip_kind=clip,
                         resource_crop=resource, focus_manual=manual, focus_index=level,
                         edited_bank="A" if route == "A" else "B"))

    levels = [0, 4, 8, 4, 8, 0, 8, 0, 4]
    routes = ["B", "A", "D", "Cancel", "B", "A", "D", "Cancel", "B"]
    pendings = [False, True, False, True, False, True, True, False, True]
    helds = [False, True, True, False, False, True, True, False, False]
    for i, (w, h, scale) in enumerate((w, h, scale) for w, h in ((1672, 941), (1400, 820), (1920, 1080))
                                     for scale in (1, 1.5, 2)):
        add(w, h, (scale, scale), levels[i], routes[i], pendings[i], helds[i],
            manual="Upper" if i % 2 == 0 else "Lower")
    for edge in ("left", "right", "top", "bottom"):
        for scale in (1, 1.5, 2):
            add(scale=(scale, scale), origin=(0, 0) if scale == 1.5 else (13, 17),
                clip=("logical-" if scale == 1.5 else "physical-") + edge, manual="Upper")
    add(clip="physical-disjoint")
    add(scale=(1.5, 1.5), clip="physical-empty")
    add(scale=(2, 2), clip="logical-empty")
    for scale in (1, 1.5, 2):
        add(8192, 8192, (scale, scale), origin=(0, 0), resource=True)
    add(origin=(0, 0), manual="Upper")
    add(origin=(0, 0), manual="Lower")
    add(1672.25, 941.5, (1.25, .75), 8, "A", True, True, (-7, 11), manual="Upper")
    add(1920, 820)
    add(1400, 1080, (1.5, 2), 8, "A", True, True, manual="Upper")
    for i, row in enumerate(rows):
        row["case"] = i
        w, h = row["logical_size"]
        sx, sy = row["scale"]
        logical, ops, box = operations(w, h, sx, sy)
        x, y, bw, bh = box
        vw, vh = math.ceil(f(w * sx)), math.ceil(f(h * sy))
        ox, oy = row["origin"]
        if row["resource_crop"]:
            ox, oy = 32 - x - bw // 2, 32 - y - bh // 2
            output = [64, 64]
        else:
            output = [vw + 2 * abs(ox), vh + 2 * abs(oy)]
        vp = [ox, oy, vw, vh]
        clips = {"disabled": [0, 0, 0, 0], "physical-left": [x-2, y-2, 4, bh+4],
                 "physical-right": [x+bw-2, y-2, 4, bh+4], "physical-top": [x-2, y-2, bw+4, 4],
                 "physical-bottom": [x-2, y+bh-2, bw+4, 4],
                 "physical-disjoint": [x+bw+4, y+bh+4, 8, 8], "physical-empty": [x, y, 0, 0],
                 "logical-left": [46, 508, 4, 22], "logical-right": [1120, 508, 4, 22],
                 "logical-top": [46, 508, 1078, 4], "logical-bottom": [46, 526, 1078, 4],
                 "logical-empty": [48, 510, 0, 0]}
        clip = clips[row["clip_kind"]]
        if row["clip_kind"].startswith("logical-"):
            clip = [int(v * scale) for v, scale in zip(clip, [sx, sy, sx, sy])]
        row.update(mapped_logical_rim=logical, source_operations=ops, intrinsic_union=box,
                   physical_viewport=vp, logical_viewport=[math.floor(v / s) for v, s in zip(vp, [sx, sy, sx, sy])],
                   physical_clip=clip, logical_clip=[math.floor(v / s) for v, s in zip(clip, [sx, sy, sx, sy])],
                   clip_enabled=row["clip_kind"] != "disabled", blend=0 if row["clip_kind"] == "logical-empty" else 1,
                   output_size=output, bytes=4 * output[0] * output[1])
    assert len(rows) == 32 and rows[27]["intrinsic_union"] == [48, 510, 1074, 18]
    result = {"schema": 1, "protocol": "keyboard-rim-art-v1.1", "cases": rows,
              "source_derived_only": True, "candidate_frames_consumed": 0,
              "canonical_intrinsic_pixels": 19332, "canonical_one_pixel_envelope_pixels": 21520,
              "structural_counters": {"cases": 32, "state_restorations": 53, "clip_companions": 15,
                                      "opaque_child_probes": 84, "focus_cases": 14, "same_and_fresh_repeats": 4}}
    Path(sys.argv[1]).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"cases": len(rows), "all_case_pixels": sum(r["bytes"] // 4 for r in rows),
                      "case29": {k: rows[29][k] for k in ("output_size", "physical_viewport", "intrinsic_union")}}))


if __name__ == "__main__":
    main()
