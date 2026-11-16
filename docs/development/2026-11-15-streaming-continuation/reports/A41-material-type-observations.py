#!/usr/bin/env python3
"""Descriptive A41 image/font observations; no painter or acceptance grade."""
from __future__ import annotations

import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
import platform
import re

from PIL import Image, features, __version__ as pillow_version


ROOT = Path(__file__).resolve().parents[4]
REPORT = Path(__file__).with_suffix(".json")
REFERENCE = "docs/design/atlas-cover-reference.jpg"
CURRENT = "examples/demos/upper-rack-material-v1/images/play-reference-1672x941.png"
LOWER = {"left": (612, 320, 18, 128), "right": (1094, 320, 14, 128)}
WOOD = {
    "rim_left": (280, 518, 120, 6),
    "rim_middle": (650, 518, 120, 6),
    "rim_right": (980, 518, 120, 6),
    "plinth_left": (240, 928, 160, 8),
    "plinth_middle": (748, 928, 176, 8),
    "plinth_right": (1170, 928, 160, 8),
}
FOOTAGE = ["16'", "5 1/3'", "8'", "4'", "2 2/3'", "2'", "1 3/5'", "1 1/3'", "1'"]


def identity(relative):
    data = (ROOT / relative).read_bytes()
    return {"path": relative, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def y_numerator(rgb):
    return 2126 * rgb[0] + 7152 * rgb[1] + 722 * rgb[2]


def scalar_plane(values, width, height, denominator=1):
    n = width * height
    sxz = syz = sxx = syy = total = squares = 0
    for row in range(height):
        yy = 2 * row - height + 1
        for column in range(width):
            xx = 2 * column - width + 1
            value = values[row * width + column]
            sxz += xx * value
            syz += yy * value
            sxx += xx * xx
            syy += yy * yy
            total += value
            squares += value * value
    mean = Fraction(total, n * denominator)
    dx = Fraction(2 * sxz, sxx * denominator)
    dy = Fraction(2 * syz, syy * denominator)
    sse = (Fraction(squares) - Fraction(total * total, n)
           - Fraction(sxz * sxz, sxx) - Fraction(syz * syz, syy)) / denominator**2
    return {
        "mean": float(mean), "mean_exact": str(mean),
        "dx_per_pixel": float(dx), "dx_per_pixel_exact": str(dx),
        "dy_per_pixel": float(dy), "dy_per_pixel_exact": str(dy),
        "plane_residual_population_rms": math.sqrt(float(sse / n)),
        "residual_sse_exact": str(sse),
        "sufficient_integer_statistics": {
            "count": n, "denominator": denominator, "sum": total, "sum_squared": squares,
            "sum_x2_times_value": sxz, "sum_y2_times_value": syz,
            "sum_x2_squared": sxx, "sum_y2_squared": syy,
        },
    }


def patch(image, box):
    x, y, width, height = box
    pixels = list(image.crop((x, y, x + width, y + height)).get_flattened_data())
    return {
        "box_xywh_half_open": list(box),
        "encoded_y_prime": scalar_plane([y_numerator(p) for p in pixels], width, height, 10000),
        "encoded_rgb": {
            channel: scalar_plane([p[i] for p in pixels], width, height)
            for i, channel in enumerate("RGB")
        },
    }


def wood(image, box):
    x, y, width, height = box
    rows = [[y_numerator(image.getpixel((xx, yy))) for xx in range(x, x + width)]
            for yy in range(y, y + height)]
    row_means = [Fraction(sum(row), width * 10000) for row in rows]
    sse = sum(Fraction(sum(v * v for v in row)) - Fraction(sum(row)**2, width) for row in rows)
    return {
        "box_xywh_half_open": list(box),
        "mean": float(sum(row_means) / height),
        "mean_exact": str(sum(row_means) / height),
        "row_means_y_prime": [float(v) for v in row_means],
        "row_means_exact": [str(v) for v in row_means],
        "horizontal_row_residual_population_rms": math.sqrt(float(sse / (width * height))) / 10000,
        "horizontal_residual_sse_numerator_units_exact": str(sse),
    }


def ink(image, box, thresholds, require_warm=False):
    x, y, width, height = box
    out = []
    for threshold in thresholds:
        points = []
        for yy in range(y, y + height):
            for xx in range(x, x + width):
                pixel = image.getpixel((xx, yy))
                if y_numerator(pixel) >= threshold * 10000 and (
                        not require_warm or pixel[0] >= pixel[1] >= pixel[2]):
                    points.append((xx, yy))
        out.append({"encoded_y_prime_threshold": threshold, "pixels": len(points),
                    "bounds_xyxy_half_open": [min(p[0] for p in points), min(p[1] for p in points),
                                               max(p[0] for p in points) + 1, max(p[1] for p in points) + 1]
                    if points else None})
    return {"box_xywh_half_open": list(box), "require_R_ge_G_ge_B": require_warm, "screens": out}


def lower_bilinear_initialization(left, right):
    # Independent interpolation of two measured means and their vertical slopes.
    # Pixel centers; u=(x+.5-604)/508 and v=(y+.5-273)/231.
    ul, ur, vm = Fraction(17, 508), Fraction(497, 508), Fraction(111, 231)
    ml, mr = Fraction(left["mean_exact"]), Fraction(right["mean_exact"])
    cl = 231 * Fraction(left["dy_per_pixel_exact"])
    cr = 231 * Fraction(right["dy_per_pixel_exact"])
    d = (cr - cl) / (ur - ul)
    c = cl - d * ul
    b = (mr - ml) / (ur - ul) - d * vm
    a = ml - b * ul - c * vm - d * ul * vm
    return {"form": "a + b*u + c*v + d*u*v",
            "coefficients": {key: {"value": float(value), "exact": str(value)}
                             for key, value in zip("abcd", (a, b, c, d))},
            "corner_values": [float(a), float(a + b), float(a + c), float(a + b + c + d)]}


def main():
    images = {}
    image_ids = {}
    for label, relative in (("reference", REFERENCE), ("current", CURRENT)):
        with Image.open(ROOT / relative) as opened:
            opened.load()
            image = opened.convert("RGB")
        if image.size != (1672, 941):
            raise ValueError("Observation coordinates require unchanged 1672x941 images")
        images[label] = image
        image_ids[label] = {**identity(relative), "size": list(image.size),
                            "rgb_sha256": hashlib.sha256(image.tobytes()).hexdigest()}
    lower = {name: {label: patch(image, box) for label, image in images.items()}
             for name, box in LOWER.items()}
    field = {}
    for channel in ("Y_prime", "R", "G", "B"):
        def read(side):
            p = lower[side]["reference"]
            return p["encoded_y_prime"] if channel == "Y_prime" else p["encoded_rgb"][channel]
        field[channel] = lower_bilinear_initialization(read("left"), read("right"))
    header = (ROOT / "apps/standalone/FontData.h").read_text()
    serif = header.split("kSerifGlyphs{{", 1)[1].split("}};", 1)[0]
    glyphs = {int(code): tuple(map(int, values.split(",")))
              for values, code in re.findall(r"\{([^{}]+)\}, // ASCII (\d+)", serif)}
    if set(glyphs) != set(range(32, 127)):
        raise ValueError("Unexpected existing font coverage")
    footage = []
    for label in FOOTAGE:
        advance = Fraction(sum(glyphs[ord(c)][6] for c in label), 64)
        size = min(Fraction(19), Fraction(42 * 40, 1) / advance)
        top = Fraction(467) + (23 - size * Fraction(6, 5)) / 2
        baseline = top + 38 * size / 40
        footage.append({"label": label, "advance_at_40_px": float(advance),
                        "fitted_size": float(size), "logical_top": float(top),
                        "logical_baseline": float(baseline),
                        "label_bounds_relative": [-23, 467, 46, 23]})
    inputs = ["apps/standalone/InstrumentView.cpp", "apps/standalone/Drawing.cpp",
              "apps/standalone/Drawing.h", "apps/standalone/UiModel.cpp", "apps/standalone/UiModel.h",
              "apps/standalone/FontData.h", "assets/standalone/fonts/source-manifest.json",
              "assets/standalone/fonts/atlas-manifest.json", "assets/standalone/fonts/DejaVuSans.ttf",
              "assets/standalone/fonts/DejaVuSerif.ttf", "assets/standalone/fonts/LICENSE-DejaVu.txt",
              "assets/standalone/reference/manifest.json", "tools/compile_reference_art.py",
              "tools/generate_standalone_font.py", "examples/demos/upper-rack-material-v1/provenance.json"]
    report = {
        "schema_version": 1, "worker": "/root/w07_a41",
        "status": "PROPOSAL_INPUTS_ONLY_NO_ADMISSION_OR_PRODUCTION_EDIT",
        "reproducer": identity(Path(__file__).relative_to(ROOT).as_posix()),
        "decoder": {"python": platform.python_version(), "pillow": pillow_version,
                    "libjpeg_turbo": features.version_feature("libjpeg_turbo"),
                    "jpeg_api": features.version_codec("jpg")},
        "method": {"pixels": "Original decoded RGB, no resampling/registration/gamma/ICC/EXIF/gain edits.",
                   "Y_prime": "(2126R+7152G+722B)/10000 on encoded 0..255 channels; not physical luminance.",
                   "plane": "Exact Fraction sufficient statistics, x2=2*column-width+1, y2=2*row-height+1; population residual RMS.",
                   "wood": "Remove each complete row mean, then population RMS; spatial variation only, not a material/fidelity grade.",
                   "type": "Thresholds are descriptive sensitivity probes; not glyph identity, edit masks, frozen tolerance or parity grade.",
                   "field": "Unrendered Lower-only initialization from two reference quiet strips. Extrapolated interior/corners need independent review; no rounding/grain candidate is admitted.",
                   "font_geometry": "Exact arithmetic reconstruction of current centered()/text_width()/text() nominal metrics; actual SDL pixel extents remain separate."},
        "images": image_ids, "source_inputs": [identity(p) for p in inputs],
        "lower": lower, "lower_bilinear_initialization": field,
        "lower_reference_right_minus_left": float(Fraction(lower["right"]["reference"]["encoded_y_prime"]["mean_exact"])
                                                    - Fraction(lower["left"]["reference"]["encoded_y_prime"]["mean_exact"])),
        "wood": {name: {label: wood(image, box) for label, image in images.items()} for name, box in WOOD.items()},
        "title": {label: ink(image, (590, 14, 490, 46), (80, 100, 120, 140, 160)) for label, image in images.items()},
        "rack_heading_pixels": {
            heading: {label: ink(image, box, (160,), True) for label, image in images.items()}
            for heading, box in {"upper": (204, 278, 307, 25), "lower": (724, 278, 310, 25)}.items()
        },
        "footage_current_logical_geometry": footage,
        "footage_pixels": {label: {source: ink(image, box, (100,), True) for source, image in images.items()}
                           for label, box in {"16'": (135, 466, 47, 25), "8'": (235, 466, 40, 25),
                                              "4'": (282, 466, 40, 25), "2'": (383, 466, 36, 25),
                                              "1'": (534, 466, 33, 25)}.items()},
        "runtime_limit": "Current PNG is an actual runtime gallery, not a deterministic before/after fixture. This worker ran no app, build or broad test.",
    }
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"report": REPORT.relative_to(ROOT).as_posix(),
                      "sha256": hashlib.sha256(REPORT.read_bytes()).hexdigest(),
                      "lower_Y_bilinear": field["Y_prime"]["coefficients"],
                      "lower_RGB_bilinear": {c: field[c]["coefficients"] for c in "RGB"}}, sort_keys=True))


if __name__ == "__main__":
    main()
