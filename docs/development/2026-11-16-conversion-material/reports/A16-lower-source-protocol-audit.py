#!/usr/bin/env python3
"""Independent Lower source/sampling audit; v2 authoring, never acceptance."""
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
AMENDMENT_SHA = "b2ebad8944a31ac6e631f457507017dfac1c6191c721fb961c7adafe9b659695"
PAINTER_SHA = "45b710a9c207f456701732f55ec1086487d63bdb9a8b6ed995f4de12cd5bdb10"
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
CENTERS = (685, 734, 782, 830, 878, 927, 975, 1024, 1074)
FOOTAGES = ("16'", "5 1/3'", "8'", "4'", "2 2/3'", "2'", "1 3/5'", "1 1/3'", "1'")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def identity(path):
    data = path.read_bytes()
    return {"path": str(path), "bytes": len(data), "sha256": sha(data)}


def rational(value):
    return {"n": str(value.numerator), "d": str(value.denominator), "value": float(value)}


def decode(value):
    return Q(int(value["n"]), int(value["d"]))


def fit(image, rectangle, channel):
    """Raw-coordinate exact normal equations; no prior author/audit helper."""
    x0, y0, w, h = rectangle
    gram = [[0] * 3 for _ in range(3)]
    rhs = [0] * 3
    sum_squares = 0
    denominator = 10000 if channel == "Y" else 1
    for y in range(h):
        for x in range(w):
            pixel = image.getpixel((x0 + x, y0 + y))
            z = sum(a * b for a, b in zip(pixel[:3], (2126, 7152, 722))) if channel == "Y" else pixel[channel]
            basis = (1, x, y)
            sum_squares += z * z
            for i in range(3):
                rhs[i] += basis[i] * z
                for j in range(3):
                    gram[i][j] += basis[i] * basis[j]
    aug = [[Q(v) for v in row] + [Q(rhs[i], denominator)] for i, row in enumerate(gram)]
    for j in range(3):
        divisor = aug[j][j]
        assert divisor
        aug[j] = [v / divisor for v in aug[j]]
        for i in range(3):
            if i != j:
                multiplier = aug[i][j]
                aug[i] = [a - multiplier * b for a, b in zip(aug[i], aug[j])]
    beta = [row[-1] for row in aug]
    sse = Q(sum_squares, denominator * denominator) - sum(b * Q(v, denominator) for b, v in zip(beta, rhs))
    return {"mean": rational(Q(rhs[0], w * h * denominator)), "slope_x": rational(beta[1]),
            "slope_y": rational(beta[2]), "residual_variance": rational(sse / (w * h)),
            "rms": math.sqrt(float(sse / (w * h))),
            "raw": {"gram": gram, "rhs": rhs, "sum_squares": sum_squares, "denominator": denominator}}


def measurements(image, patches):
    return {name: {"rectangle": rectangle, "Y": fit(image, rectangle, "Y"),
                   "RGB": [fit(image, rectangle, channel) for channel in range(3)]}
            for name, rectangle in patches.items()}


def screens(reference, actual):
    result = []

    def add(name, error, limit):
        exact = isinstance(error, Q)
        result.append({"name": name, "signed_error": rational(error) if exact else error,
                       "absolute_limit": rational(limit) if isinstance(limit, Q) else limit,
                       "passed": abs(error) <= limit})

    for name in PRIMARY:
        add(name + ".Y.mean", decode(actual[name]["Y"]["mean"]) - decode(reference[name]["Y"]["mean"]), Q(5, 2))
        for c in range(3):
            add(name + f".RGB{c}.mean", decode(actual[name]["RGB"][c]["mean"]) - decode(reference[name]["RGB"][c]["mean"]), Q(3))
    for name in ("left", "right"):
        add(name + ".Y.rms", actual[name]["Y"]["rms"] - reference[name]["Y"]["rms"], 0.5)
        a = decode(actual[name]["Y"]["residual_variance"])
        b = decode(reference[name]["Y"]["residual_variance"])
        difference = a + b - Q(1, 4)
        result[-1]["passed"] = difference <= 0 or difference * difference <= 4 * a * b
        result[-1]["comparison_method"] = "Exact variance inequality for abs(sqrt(a)-sqrt(b)) <= 1/2; displayed error only is binary64"
        for metric, limit in (("slope_x", Q(3, 50)), ("slope_y", Q(1, 40))):
            add(name + ".Y." + metric, decode(actual[name]["Y"][metric]) - decode(reference[name]["Y"][metric]), limit)
    def lateral(m):
        return decode(m["right"]["Y"]["mean"]) - decode(m["left"]["Y"]["mean"])
    add("right_minus_left.Y.mean", lateral(actual) - lateral(reference), Q(7, 4))
    assert len(result) == 35
    return {"passed": sum(r["passed"] for r in result), "failed": sum(not r["passed"] for r in result), "comparisons": result}


def native_frame(executable):
    process = subprocess.run([str(executable), "--case", "28"], check=True,
                             capture_output=True, timeout=30)
    header, pixels = process.stdout.split(b"\n", 1)
    metadata = json.loads(header)
    assert len(pixels) == metadata["width"] * metadata["height"] * 4
    assert (metadata["width"], metadata["height"]) == (1672, 941)
    return Image.frombytes("RGBA", (1672, 941), pixels), {
        "executable": identity(executable), "command": [str(executable), "--case", "28"],
        "metadata": metadata, "rgba_sha256": sha(pixels), "stderr": process.stderr.decode("utf-8")}


def points(rectangle):
    x, y, w, h = rectangle
    return {(xx, yy) for yy in range(y, y + h) for xx in range(x, x + w)}


def f32(value):
    return struct.unpack("<f", struct.pack("<f", value))[0]


def font_geometry(text, box, size, face, padding, font_text):
    chunk = font_text.split(f"k{face}Glyphs{{{{", 1)[1].split("}};", 1)[0]
    glyphs = [tuple(map(int, row.split(","))) for row in re.findall(r"\{([\d, -]+)\}", chunk)]
    assert len(glyphs) == 95
    height, ascent = (32, 30) if face == "Sans" else (40, 38)
    def width(size):
        scale = f32(size / height)
        total = 0.0
        for character in text:
            total = f32(total + f32(f32(glyphs[ord(character) - 32][6] * scale) / 64))
        return total
    size = min(size, f32(box[3] / f32(1.2)))
    if width(size) > f32(box[2] - 2 * padding):
        size = f32(size * f32(max(0.1, f32(box[2] - 2 * padding)) / width(size)))
    scale = f32(size / height)
    x = f32(box[0] + f32(f32(box[2] - width(size)) / 2))
    top = f32(box[1] + f32(f32(box[3] - f32(size * f32(1.2))) / 2))
    baseline = f32(top + f32(ascent * scale))
    boxes = []
    for character in text:
        _, _, w, h, bx, by, advance = glyphs[ord(character) - 32]
        if w and h:
            px, py = (2 if f32(w * scale) < 1 else 0), (2 if f32(h * scale) < 1 else 0)
            xx, yy = f32(x + f32((bx - px) * scale)), f32(baseline + f32((by - py) * scale))
            ww, hh = f32((w + 2 * px) * scale), f32((h + 2 * py) * scale)
            # Conservative one-pixel guard around floating target support.
            boxes.append((math.floor(xx) - 1, math.floor(yy) - 1,
                          math.ceil(xx + ww) - math.floor(xx) + 2,
                          math.ceil(yy + hh) - math.floor(yy) + 2))
        x = f32(x + f32(f32(advance * scale) / 64))
    return boxes


def main():
    amendment = ROOT / "docs/design/LOWER_RACK_MATERIAL_V2_AMENDMENT.md"
    painter = ROOT / "apps/standalone/InstrumentView.cpp"
    assert sha(amendment.read_bytes()) == AMENDMENT_SHA
    assert sha(painter.read_bytes()) == PAINTER_SHA
    baseline_painter = ROOT.parent / "baseline/InstrumentView.cpp"
    old, new = baseline_painter.read_text(), painter.read_text()
    slices = (
        ("Upper mechanical/field helpers", "// The v1.1 material arithmetic", "void reference_panel", "// Lower v1 has"),
        ("Existing wood/heading/drawbar bodies", "void reference_wood", "[[nodiscard]] UiQuad reference_inset_quad", None),
        ("Controls and header", "void reference_controls", "void paint_reference_composition", None),
    )
    equality = []
    for name, start, old_end, new_end in slices:
        a = old.split(start, 1)[1].split(old_end, 1)[0]
        b = new.split(start, 1)[1].split(new_end or old_end, 1)[0]
        assert a == b
        equality.append({"slice": name, "bytes": len(a.encode()), "sha256": sha(a.encode()), "equal": True})
    baseline_id = json.loads((HERE / "baseline-identity.json").read_text())
    stable = ["apps/standalone/UiModel.cpp", "apps/standalone/UiModel.h", "apps/standalone/Drawing.cpp",
              "apps/standalone/Drawing.h", "apps/standalone/FontData.h",
              "assets/standalone/reference/manifest.json", "assets/standalone/reference/left-wood-cheek.rgb.gz",
              "assets/standalone/reference/right-wood-cheek.rgb.gz", "assets/standalone/reference/cabinet.rgb.gz"]
    stable_results = []
    for name in stable:
        actual = sha((ROOT / name).read_bytes())
        assert actual == baseline_id["inputs"][name]
        stable_results.append({"path": name, "sha256": actual, "matches_genuine_baseline": True})

    v2 = dict(PATCHES)
    for name in ("right", "right_top", "right_bottom"):
        x, y, w, h = PATCHES[name]
        v2[name] = (x + 1, y, w - 1, h)
    font_text = (ROOT / "apps/standalone/FontData.h").read_text()
    glyph_boxes = font_geometry("LOWER MANUAL DRAWBARS", (616, 277, 484, 27), 16, "Serif", 3, font_text)
    for center, label in zip(CENTERS, FOOTAGES):
        glyph_boxes.extend(font_geometry(label, (center - 23, 467, 46, 23), 19, "Serif", 2, font_text))
        glyph_boxes.extend(font_geometry("4", (center - 23, 491, 46, 15), 12, "Sans", 3, font_text))
    glyph_points = set().union(*(points(box) for box in glyph_boxes))
    slot_points = set().union(*(points((c - 21, 311, 42, 150)) for c in CENTERS))
    focus_points = points((855, 309, 46, 2)) | points((855, 504, 46, 2)) | points((855, 311, 2, 193)) | points((899, 311, 2, 193))
    border_points = points((1094, 311, 1, 150))
    audit = []
    for name, rectangle in PATCHES.items():
        p, corrected = points(rectangle), points(v2[name])
        audit.append({"patch": name, "v1_rectangle": rectangle, "v2_rectangle": v2[name],
                      "v1_slot_pixels": len(p & slot_points), "v2_slot_pixels": len(corrected & slot_points),
                      "v1_right_border_pixels": len(p & border_points), "focus_pixels": len(p & focus_points),
                      "conservative_glyph_support_pixels": len(p & glyph_points)})
    assert all(row["v2_slot_pixels"] == 0 for row in audit)
    assert all(row["conservative_glyph_support_pixels"] == 0 for row in audit)
    assert [r["focus_pixels"] for r in audit] == [0] * 8 + [16, 0]

    reference_path = ROOT / "docs/design/atlas-cover-reference.jpg"
    reference = Image.open(reference_path).convert("RGB")
    before, before_receipt = native_frame(ROOT.parent / "baseline/test_standalone_lower_rack_material_raster")
    candidate, candidate_receipt = native_frame(ROOT.parent / "build-native/apps/standalone/test_standalone_lower_rack_material_raster")
    assert before_receipt["metadata"] == candidate_receipt["metadata"]
    expected_focus = (165, 228, 223, 255)
    for p in border_points:
        assert before.getpixel(p) == candidate.getpixel(p) == (36, 34, 30, 255)
    middle_focus = focus_points & points(PATCHES["bottom_interior_middle"])
    for p in middle_focus:
        assert before.getpixel(p) == candidate.getpixel(p) == expected_focus

    measurements_by_version = {}
    for version, patches in (("v1_frozen", PATCHES), ("v2_proposed", v2)):
        stats = {"reference": measurements(reference, patches),
                 "genuine_before": measurements(before, patches), "candidate": measurements(candidate, patches)}
        measurements_by_version[version] = {"measurements": stats,
            "screens": {name: screens(stats["reference"], stats[name]) for name in ("genuine_before", "candidate")}}
    preview = ROOT.parent / "lower-preview/play-1672x941.png"
    preview_image = Image.open(preview).convert("RGB")
    report = {
        "schema": 1, "scope": "Independent source/geometry and retained v1 failure; proposed v2 authoring only, not candidate acceptance",
        "cwd": str(ROOT), "command": ["python3", "-B", str(Path(__file__).relative_to(ROOT))],
        "decoder": {"python": platform.python_version(), "pillow": pillow_version,
                    "libjpeg_turbo": features.version_feature("libjpeg_turbo"), "operation": "RGB decode only"},
        "sources": [identity(p) for p in (Path(__file__), amendment, painter, baseline_painter, reference_path, preview)],
        "unchanged_source_slices": equality, "unchanged_source_files": stable_results,
        "patch_geometry_audit": audit, "glyph_support_method": "Existing ASCII advances/bearings independently evaluated in binary32; conservative floating target envelope plus one pixel each side",
        "protected_border": {"xywh": [1094, 311, 1, 150], "pixels": 150, "exact_rgba": [36, 34, 30, 255], "unchanged": True},
        "protected_middle_witness_focus": {"xywh": [855, 492, 2, 8], "pixels": 16, "exact_rgba": list(expected_focus), "unchanged": True},
        "native_inputs": {"before": before_receipt, "candidate": candidate_receipt},
        "reference_decoded_rgb_sha256": sha(reference.tobytes()),
        "versions": measurements_by_version,
        "actual_preview_descriptive_only": {"file": identity(preview), "rgb_sha256": sha(preview_image.tobytes()),
            "bottom_witnesses": measurements(preview_image, {k: v for k, v in PATCHES.items() if k.startswith("bottom_interior")})},
        "limits": "No build, candidate source edit, 98-pair acceptance, new threshold, native-display journey, audio or whole-interface parity claim. V2 requires independent admission."}
    destination = HERE / "A16-lower-source-protocol-audit.json"
    destination.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"report": str(destination.relative_to(ROOT)), "versions": {
        version: {name: {"passed": data["passed"], "failed": data["failed"]} for name, data in result["screens"].items()}
        for version, result in measurements_by_version.items()}, "patch_geometry_audit": audit}, indent=2))


if __name__ == "__main__":
    main()
