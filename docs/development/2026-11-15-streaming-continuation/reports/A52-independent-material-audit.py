#!/usr/bin/env python3
"""Independent documentary arithmetic; no app, painter, image or acceptance edit."""
from __future__ import annotations

from fractions import Fraction as Q
import hashlib
import json
import math
from pathlib import Path
import platform
import re
import struct
import subprocess

from PIL import Image, features, __version__ as pillow_version

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
GALLERY = ROOT / "examples/demos/upper-rack-material-v1"
REFERENCE = ROOT / "docs/design/atlas-cover-reference.jpg"
WEIGHTS = (2126, 7152, 722)
LOWER = {"left": (612, 320, 18, 128), "right": (1094, 320, 14, 128)}
WOOD = {"rim_left": (280, 518, 120, 6), "rim_middle": (650, 518, 120, 6),
        "rim_right": (980, 518, 120, 6), "plinth_left": (240, 928, 160, 8),
        "plinth_middle": (748, 928, 176, 8), "plinth_right": (1170, 928, 160, 8)}
# Additional descriptive witnesses, chosen before their values were evaluated.
# They are not accepted quiet/scoring patches; border/heading influence must be
# annotated by a future independent protocol owner before any such use.
WITNESSES = {"left_top": (612, 298, 18, 14), "right_top": (1094, 298, 14, 14),
             "center_top": (800, 302, 112, 6),
             "left_bottom": (612, 460, 18, 20), "right_bottom": (1094, 460, 14, 20)}
LABELS = ("16'", "5 1/3'", "8'", "4'", "2 2/3'", "2'", "1 3/5'", "1 1/3'", "1'")


def digest(path):
    raw = path.read_bytes()
    try:
        name = path.relative_to(ROOT).as_posix()
    except ValueError:
        name = str(path)
    return {"path": name, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def record(value):
    return {"exact": str(value), "value": float(value)}


def solve(matrix, target):
    """Exact uncentered Gaussian elimination, independent of A39/A41 helpers."""
    a = [[Q(v) for v in row] + [Q(b)] for row, b in zip(matrix, target)]
    for col in range(len(a)):
        pivot = next(r for r in range(col, len(a)) if a[r][col])
        a[col], a[pivot] = a[pivot], a[col]
        divisor = a[col][col]
        a[col] = [v / divisor for v in a[col]]
        for r in range(len(a)):
            if r != col:
                multiple = a[r][col]
                a[r] = [v - multiple * z for v, z in zip(a[r], a[col])]
    return [row[-1] for row in a]


def scalar_patch(image, box, channel=None):
    x0, y0, w, h = box
    matrix = [[0] * 3 for _ in range(3)]
    target, square_sum = [0] * 3, 0
    denominator = 10000 if channel is None else 1
    for y in range(h):
        for x in range(w):
            rgb = image.getpixel((x0 + x, y0 + y))
            z = sum(a * b for a, b in zip(rgb, WEIGHTS)) if channel is None else rgb[channel]
            basis = (1, x, y)
            square_sum += z * z
            for i in range(3):
                target[i] += basis[i] * z
                for j in range(3):
                    matrix[i][j] += basis[i] * basis[j]
    beta = solve(matrix, target)
    sse = (Q(square_sum) - sum(b * t for b, t in zip(beta, target))) / denominator**2
    return {"box_xywh_half_open": list(box), "normal_matrix": matrix,
            "normal_target_integer": target, "sum_squares_integer": square_sum,
            "denominator": denominator, "mean": record(Q(target[0], w * h * denominator)),
            "local_plane": [record(v / denominator) for v in beta],
            "sse": record(sse), "population_rms": math.sqrt(float(sse / (w * h)))}


def row_patch(image, box):
    x, y, w, h = box
    rows = []
    sse = Q(0)
    for yy in range(y, y + h):
        values = [sum(a * b for a, b in zip(image.getpixel((xx, yy)), WEIGHTS))
                  for xx in range(x, x + w)]
        total, square = sum(values), sum(v * v for v in values)
        rows.append({"y": yy, "sum_integer": total, "sum_squares_integer": square,
                     "mean": record(Q(total, w * 10000))})
        sse += Q(square) - Q(total * total, w)
    return {"box_xywh_half_open": list(box), "rows": rows,
            "mean": record(sum(Q(row["mean"]["exact"]) for row in rows) / h),
            "horizontal_residual_sse": record(sse / 10000**2),
            "horizontal_population_rms": math.sqrt(float(sse / (w * h))) / 10000}


def bilinear(left, right):
    matrix, target = [], []
    for patch in (left, right):
        x, y, w, h = patch["box_xywh_half_open"]
        u, v = Q(2 * x + w - 2 * 604, 2 * 508), Q(2 * y + h - 2 * 273, 2 * 231)
        matrix += [[1, u, v, u * v], [0, 0, Q(1, 231), u / 231]]
        target += [Q(patch["mean"]["exact"]), Q(patch["local_plane"][2]["exact"])]
    return solve(matrix, target)


def bilinear_mean(beta, box):
    x, y, w, h = box
    u, v = Q(2 * x + w - 2 * 604, 2 * 508), Q(2 * y + h - 2 * 273, 2 * 231)
    return sum(a * b for a, b in zip(beta, (1, u, v, u * v)))


def threshold_ink(image, box, threshold=100, warm=True):
    x, y, w, h = box
    points = [(xx, yy) for yy in range(y, y + h) for xx in range(x, x + w)
              if (lambda p: (not warm or p[0] >= p[1] >= p[2]) and
                  sum(a * b for a, b in zip(p, WEIGHTS)) >= 10000 * threshold)(image.getpixel((xx, yy)))]
    return {"roi_xywh": list(box), "threshold": threshold, "warm_ink": warm,
            "pixels": len(points), "bounds_xyxy_half_open":
            [min(p[0] for p in points), min(p[1] for p in points),
             max(p[0] for p in points) + 1, max(p[1] for p in points) + 1] if points else None}


def f32(value):
    return struct.unpack("f", struct.pack("f", value))[0]


def lower_support(width, height, rx, ry):
    sx, sy = f32(width / 1672), f32(height / 941)
    bx, by = f32(600 * sx), f32(269 * sy)
    bw, bh = f32(f32(1116 * sx) - bx), f32(f32(508 * sy) - by)
    ix, iy = f32(bx + f32(4 * sx)), f32(by + f32(4 * sy))
    iw, ih = f32(bw - f32(2 * f32(4 * sx))), f32(bh - f32(2 * f32(4 * sy)))
    gradient = [math.ceil(ix * rx - .5), math.ceil(iy * ry - .5),
                math.ceil((ix + iw) * rx - .5), math.ceil((iy + ih) * ry - .5)]
    rows, columns = math.floor(f32(f32(bh / sy) - 16)), math.floor(f32(f32(bw / sx) - 21))
    step = max(4, math.ceil(math.sqrt(rows * columns / (3 * 2048))))
    def pairs(p):
        return (((rows - 2) // p + 1) if rows > 1 else 0) * (((columns - 2) // (3 * p) + 1) if columns > 1 else 0)
    while pairs(step) > 2048:
        step += 1
    marks = []
    for row in range(1, rows, step):
        for column in range(1, columns, 3 * step):
            grain = (row * 1973 + column * 9277) & 0xFFFFFFFF
            x = f32(bx + f32(f32(f32(7 + float(column)) + float((grain >> 5) % 3)) * sx))
            y = f32(by + f32(f32(7 + float(row)) * sy))
            for mx, my, mw, mh in ((x, y, sx, sy),
                                    (f32(x + f32(3 * sx)), f32(y + sy), f32(2 * sx), sy)):
                l, t = math.trunc(f32(mx * rx)), math.trunc(f32(my * ry))
                marks.append([l, t, l + max(math.trunc(f32(mw * rx)), 1),
                               t + max(math.trunc(f32(mh * ry)), 1)])
    contained = all(gradient[0] <= m[0] < m[2] <= gradient[2] and
                    gradient[1] <= m[1] < m[3] <= gradient[3] for m in marks)
    intrinsic = [min([gradient[0]] + [m[0] for m in marks]),
                 min([gradient[1]] + [m[1] for m in marks]),
                 max([gradient[2]] + [m[2] for m in marks]),
                 max([gradient[3]] + [m[3] for m in marks])]
    expanded = [intrinsic[0] - 1, intrinsic[1] - 1, intrinsic[2] + 1, intrinsic[3] + 1]
    return {"logical_size": [width, height], "renderer_scale": [rx, ry],
            "mapped_panel": [bx, by, bw, bh], "mapped_inset": [ix, iy, iw, ih],
            "current_gradient_xyxy": gradient, "current_grain_pairs": len(marks) // 2,
            "all_current_grain_inside_gradient": contained,
            "current_support_one_pixel_expansion_xyxy": expanded,
            "current_support_one_pixel_expansion_area": (expanded[2] - expanded[0]) * (expanded[3] - expanded[1]),
            "candidate_support_status": "NOT_DEFINED; these are old-support calculations, not an admitted future mask"}


def main():
    reference = Image.open(REFERENCE).convert("RGB")
    current = Image.open(GALLERY / "images/play-reference-1672x941.png").convert("RGB")
    assert reference.size == current.size == (1672, 941)
    images = {"reference": reference, "current": current}
    provenance = json.loads((GALLERY / "provenance.json").read_text())
    gallery_checks = []
    for case in provenance["cases"]:
        item = case["image"]
        p = GALLERY / item["path"]
        decoded = Image.open(p).convert("RGBA")
        identity = digest(p)
        decoded_hash = hashlib.sha256(decoded.tobytes()).hexdigest()
        assert identity["bytes"] == item["png"]["bytes"] and identity["sha256"] == item["png"]["sha256"]
        assert decoded.size == (item["width"], item["height"]) and decoded_hash == item["decoded_sha256"]
        gallery_checks.append({**identity, "size": list(decoded.size), "rgba_sha256": decoded_hash})
    production_changes = []
    for relative, expected in provenance["source"]["files"].items():
        observed = digest(ROOT / relative)
        if any(observed[k] != expected[k] for k in ("bytes", "sha256")):
            production_changes.append({"observed": observed, "expected": expected})
    assert not production_changes
    exe = digest(Path(provenance["executable"]["path"]))
    assert exe["sha256"] == provenance["executable"]["before"]["sha256"]
    lower = {name: {source: {channel: scalar_patch(image, box, None if channel == "Y_prime" else "RGB".index(channel))
                            for channel in ("Y_prime", "R", "G", "B")}
                    for source, image in images.items()} for name, box in LOWER.items()}
    fields = {channel: bilinear(lower["left"]["reference"][channel], lower["right"]["reference"][channel])
              for channel in ("Y_prime", "R", "G", "B")}
    midpoint_dx = (fields["Y_prime"][1] + fields["Y_prime"][3] * Q(111, 231)) / 508
    lateral = {"initialization_dx_at_both_strip_midpoints": record(midpoint_dx),
               "reference_local_plane_dx": {side: lower[side]["reference"]["Y_prime"]["local_plane"][1]
                                            for side in LOWER},
               "interpretation": "The four constraints do not include either measured local lateral slope; bilinear dx is independent of u at fixed v."}
    witnesses = {}
    for name, box in WITNESSES.items():
        patch = scalar_patch(reference, box)
        prediction = bilinear_mean(fields["Y_prime"], box)
        witnesses[name] = {"reference": patch, "initialization_mean": record(prediction),
                           "reference_minus_initialization_mean": record(Q(patch["mean"]["exact"]) - prediction),
                           "status": "Exploratory boundary/interior witnesses; no quiet-patch admission or threshold"}
    wood = {name: {source: row_patch(image, box) for source, image in images.items()} for name, box in WOOD.items()}
    text = (ROOT / "apps/standalone/FontData.h").read_text()
    section = text.split("kSerifGlyphs{{", 1)[1].split("}};", 1)[0]
    glyphs = {int(code): tuple(map(int, values.split(","))) for values, code in
              re.findall(r"\{([^{}]+)\}, // ASCII (\d+)", section)}
    assert set(glyphs) == set(range(32, 127))
    def advance(label, size):
        return Q(sum(glyphs[ord(ch)][6] for ch in label), 64 * 40) * size
    font = []
    for label in LABELS:
        fitted = min(Q(19), Q(23) / Q(6, 5))
        if advance(label, fitted) > 42:
            fitted *= 42 / advance(label, fitted)
        baseline = Q(467) + (23 - fitted * Q(6, 5)) / 2 + Q(38, 40) * fitted
        if " " in label:
            whole, fraction = label[:-1].split(" ")
            numerator, denominator = fraction.split("/")
            parts = [(whole, Q(41, 2), Q(977, 2)), (numerator, Q(13), Q(965, 2)),
                     ("/", Q(16), Q(973, 2)), (denominator, Q(13), Q(977, 2)),
                     ("'", Q(41, 2), Q(977, 2))]
            gaps = [Q(1, 2), 0, 0, Q(1, 2), 0]
        else:
            parts, gaps = [(label, Q(41, 2), Q(977, 2))], [0]
        total = sum(advance(p[0], p[1]) + gap for p, gap in zip(parts, gaps))
        cursor, quads = -total / 2, []
        for (part, size, base), gap in zip(parts, gaps):
            for ch in part:
                _, _, w, h, bx, by, _ = glyphs[ord(ch)]
                quads.append({"glyph": ch, "size": record(size), "baseline": record(base),
                              "x_from_center": record(cursor),
                              "logical_target_xywh": [record(cursor + bx * size / 40), record(base + by * size / 40),
                                                       record(w * size / 40), record(h * size / 40)]})
                cursor += advance(ch, size)
            cursor += gap
        font.append({"label": label, "current_fitted_size": record(fitted), "current_baseline": record(baseline),
                     "candidate_sequential_run_width": record(total), "candidate_ideal_quads": quads,
                     "candidate_status": "Nominal sequential interpretation only; no raster run or accepted support"})
    footage_boxes = {"16'": (135, 466, 47, 25), "8'": (235, 466, 40, 25), "4'": (282, 466, 40, 25),
                     "2'": (383, 466, 36, 25), "1'": (534, 466, 33, 25)}
    footage_ink = {label: {source: threshold_ink(image, box) for source, image in images.items()}
                   for label, box in footage_boxes.items()}
    heading_ink = {name: {source: threshold_ink(image, box, 160) for source, image in images.items()}
                   for name, box in {"upper": (204, 278, 307, 25), "lower": (724, 278, 310, 25)}.items()}
    title_ink = {source: threshold_ink(image, (590, 14, 490, 46), 100, False) for source, image in images.items()}
    scaling_examples = []
    for width, height in ((1400, 820), (1920, 1080), (1920, 820), (8192, 820)):
        sx, sy = Q(width, 1672), Q(height, 941)
        f = min(sx, sy)
        scaling_examples.append({"logical_size": [width, height], "sx": record(sx), "sy": record(sy),
            "f": record(f), "sum_scaled_advances_plus_two_scaled_half_gaps": record(Q(399, 10) * f + sx),
            "canonical_width_times_sx": record(Q(409, 10) * sx),
            "fraction_nominal_size": record(13 * f),
            "interpretation": "Illustrates an unresolved proposal scaling rule, not observed candidate rendering."})
    differences, equal_cabinet, row_counts = 0, 0, []
    for y in range(941):
        row = 0
        for x in range(1672):
            equal = reference.getpixel((x, y)) == current.getpixel((x, y))
            row += not equal
            if 1132 <= x < 1598 and 174 <= y < 571:
                equal_cabinet += equal
        differences += row
        row_counts.append(row)
    a41 = json.loads((HERE / "A41-material-type-observations.json").read_text())
    comparisons = []
    for side in LOWER:
        for source in images:
            for channel in ("Y_prime", "R", "G", "B"):
                got = lower[side][source][channel]
                previous = a41["lower"][side][source]
                old = previous["encoded_y_prime"] if channel == "Y_prime" else previous["encoded_rgb"][channel]
                assert Q(got["mean"]["exact"]) == Q(old["mean_exact"])
                assert Q(got["sse"]["exact"]) == Q(old["residual_sse_exact"])
                assert Q(got["local_plane"][2]["exact"]) == Q(old["dy_per_pixel_exact"])
                comparisons.append(f"{side}/{source}/{channel}: exact mean, SSE and vertical slope agree")
    for channel, beta in fields.items():
        for key, value in zip("abcd", beta):
            assert value == Q(a41["lower_bilinear_initialization"][channel]["coefficients"][key]["exact"])
    for name in WOOD:
        for source in images:
            got, old = wood[name][source], a41["wood"][name][source]
            assert Q(got["mean"]["exact"]) == Q(old["mean_exact"])
            assert [row["mean"]["exact"] for row in got["rows"]] == old["row_means_exact"]
            assert Q(got["horizontal_residual_sse"]["exact"]) == Q(old["horizontal_residual_sse_numerator_units_exact"]) / 10000**2
    for label in footage_boxes:
        for source in images:
            old = a41["footage_pixels"][label][source]["screens"][0]
            assert footage_ink[label][source]["pixels"] == old["pixels"]
            assert footage_ink[label][source]["bounds_xyxy_half_open"] == old["bounds_xyxy_half_open"]
    for heading in heading_ink:
        for source in images:
            old = a41["rack_heading_pixels"][heading][source]["screens"][0]
            assert heading_ink[heading][source]["pixels"] == old["pixels"]
            assert heading_ink[heading][source]["bounds_xyxy_half_open"] == old["bounds_xyxy_half_open"]
    for source in images:
        old = next(item for item in a41["title"][source]["screens"] if item["encoded_y_prime_threshold"] == 100)
        assert title_ink[source]["pixels"] == old["pixels"]
        assert title_ink[source]["bounds_xyxy_half_open"] == old["bounds_xyxy_half_open"]
    assert differences == 1385301 and equal_cabinet == 185002
    paths = ["docs/design/WHOLE_WINDOW_REFERENCE_NEXT.md", "docs/design/REFERENCE_MATERIAL_TYPE_NEXT.md",
             "docs/design/UPPER_RACK_MATERIAL_CONTRACT.md", "docs/WHOLE_REFERENCE_LAYOUT_CONTRACT.md",
             "apps/standalone/InstrumentView.cpp", "apps/standalone/Drawing.cpp", "apps/standalone/Drawing.h",
             "apps/standalone/UiModel.cpp", "apps/standalone/UiModel.h", "apps/standalone/FontData.h",
             "assets/standalone/fonts/DejaVuSans.ttf", "assets/standalone/fonts/DejaVuSerif.ttf",
             "assets/standalone/fonts/LICENSE-DejaVu.txt", "assets/standalone/reference/manifest.json",
             "docs/design/atlas-reference.json", "docs/reviews/UPPER_RACK_COMPARISON_ADMISSION.md",
             "docs/reviews/UPPER_RACK_GALLERY_ADMISSION.md", "docs/reviews/UPPER_RACK_PAINTER_REVIEW.md"]
    report = {"schema_version": 1, "worker": "/root/w09_a52", "status": "INDEPENDENT_PROPOSAL_REVIEW_NO_NEW_VISUAL_ADMISSION",
              "cwd": str(ROOT), "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "reproducer": digest(Path(__file__)), "inputs": [digest(ROOT / p) for p in paths],
              "decoder": {"python": platform.python_version(), "pillow": pillow_version,
                          "jpeg": features.version_codec("jpg"), "libjpeg_turbo": features.version_feature("libjpeg_turbo")},
              "reference": {**digest(REFERENCE), "rgb_sha256": hashlib.sha256(reference.tobytes()).hexdigest()},
              "current_rgb_sha256": hashlib.sha256(current.tobytes()).hexdigest(),
              "pinned_sdl_source": [digest(Path("/workspace/scratch/ade21b726509/SDL2") / p) for p in
                                    ("src/render/SDL_render.c", "src/render/software/SDL_render_sw.c")],
              "gallery_provenance": digest(GALLERY / "provenance.json"),
              "all_twelve_images": gallery_checks, "production_inventory_matches": len(provenance["source"]["files"]),
              "production_changes": production_changes, "observed_retained_executable": exe,
              "whole_window_descriptive_only": {"pixels": 1672 * 941, "different_rgb_pixels": differences,
                  "equal_rgb_pixels": 1672 * 941 - differences, "cabinet_equal_pixels": equal_cabinet,
                  "outside_cabinet_equal_pixels": 1672 * 941 - differences - equal_cabinet,
                  "row_difference_counts": row_counts, "interpretation": "State-sensitive complete raw counts, not a perceptual grade or material failure"},
              "lower": lower, "bilinear_coefficients": {c: {k: record(v) for k, v in zip("abcd", beta)} for c, beta in fields.items()},
              "bilinear_lateral_limitation": lateral,
              "exploratory_witnesses": witnesses, "wood": wood, "footage": font, "footage_ink": footage_ink,
              "heading_ink": heading_ink, "title_ink_threshold_100": title_ink,
              "candidate_fraction_scaling_examples": scaling_examples,
              "candidate_type_nominal_work": {"manual_footage_labels": 18, "nonempty_glyph_copies": 62,
                  "drawing_text_calls_if_each_fraction_component_is_one_call": 50,
                  "interpretation": "Nominal sequential-layout source count only; not native timing/allocation instrumentation."},
              "lower_current_source_support": [lower_support(w, h, rx, ry) for w, h, rx, ry in
                  [(1672, 941, 1, 1), (1400, 820, 1, 1), (1920, 1080, 1.5, 1.5),
                   (1672.5, 941.5, 1.5, 1.5), (8192, 8192, 2, 2), (1672, 941, 1.25, 1.75)]],
              "reproduction_checks": comparisons,
              "limits": ["No native painter, fixture, build, recapture or broad test executed.",
                  "No original report, gallery, art, shared proposal or frozen contract changed.",
                  "Bilinear coefficients solve two strip means/slopes; no interior/corner field or grain admission follows.",
                  "Rim and candidate text remain unrendered and lack independently admitted support, budgets and tolerances.",
                  "Direct visual inspection is an A52 human-readable review observation; hashes cannot prove visual quality.",
                  "Literal whole-interface 1:1 remains unmet and unwaived; real display/DPI/accessibility and physical fidelity remain open."]}
    destination = HERE / "A52-independent-material-audit.json"
    destination.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"report": digest(destination), "lower_Y": {side: {source: [lower[side][source]["Y_prime"]["mean"]["value"], lower[side][source]["Y_prime"]["population_rms"]] for source in images} for side in LOWER},
                      "witness_residuals": {k: v["reference_minus_initialization_mean"]["value"] for k, v in witnesses.items()},
                      "production_inputs_match": len(provenance["source"]["files"]), "different_rgb_pixels": differences,
                      "canonical_old_support": report["lower_current_source_support"][0]}, sort_keys=True))


if __name__ == "__main__":
    main()
