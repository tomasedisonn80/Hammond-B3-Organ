#!/usr/bin/env python3
"""A22 independent, bounded Lower sampling audit. No project helper imports.

Read source/metrics, capture only native case 28 from each existing binary,
derive foreground/support before looking at pixels, and retain every v1/v2
comparison. No build, painter mutation, or whole-matrix qualification.
"""
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json
import math
import re
import struct
import subprocess
import sys

from PIL import Image, __version__ as pillow_version

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).with_name("A22-independent-sampling.json")
REPORTS = Path(__file__).parent
AMENDMENT = "docs/design/LOWER_RACK_MATERIAL_V2_AMENDMENT.md"
EXPECTED = {
    AMENDMENT: "b2ebad8944a31ac6e631f457507017dfac1c6191c721fb961c7adafe9b659695",
    "docs/design/LOWER_RACK_MATERIAL_CONTRACT.md": "84e3c95b4844861ffee71217ced99dbdb52bfb3216b44f4d2817c462cadccb91",
    "docs/reviews/LOWER_RACK_MATERIAL_ADMISSION.md": "504266fdee1481bb410f51f4f954d49ad04040c159cafd3f7696fc65be082c10",
    "apps/standalone/InstrumentView.cpp": "45b710a9c207f456701732f55ec1086487d63bdb9a8b6ed995f4de12cd5bdb10",
    "apps/standalone/UiModel.cpp": "0ecb0c4ee90d98cdb87c6f06b4685d368a7c12b72f9ea66e6c40228a4a855ecd",
    "apps/standalone/UiModel.h": "6d8c0b16ddb6f3059dc14aff41bfc615e37b43c53b2f6e88cc199255a6b674b1",
    "apps/standalone/Drawing.cpp": "9b788234405964f6675ab43428735e425b460c8045f2c6eb064c9e19b40a0a5f",
    "apps/standalone/Drawing.h": "749e718436e61ad4a13a28e167c4b07e4dd789adf213a6229a503fc1f2bcf188",
    "apps/standalone/FontData.h": "f1a3121a2707a03a3b2e025c399e68c553ce9498f4b002ec13b18f512e334802",
    "../baseline/InstrumentView.cpp": "30ac6cec988ec1834f36456d25d1e53113642071d844d53f81b62b3474cf2c37",
    "apps/standalone/native_tests/test_standalone_lower_rack_material_raster.cpp": "281df1de3edce6a91a851d0b5674677646f1741fac1512f474ea7ffda67350e7",
    "../baseline/test_standalone_lower_rack_material_raster": "1ffcd7e3b70b813e7af2cc5986be0659df93ee0c058ad66f329208d7e11c60ac",
    "../build-native/apps/standalone/test_standalone_lower_rack_material_raster": "9206d10ee6b85f6f166a70dd3f01d2536f99560fac369de177d226dd619da3a5",
    "docs/design/atlas-cover-reference.jpg": "9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187",
    "tools/compare_lower_rack_material.py": "2c21521211555adc1076c258a8c1659549ad7f1c0f2bccdc2ce160fa6485554f",
    "docs/development/2026-11-16-conversion-material/reports/A17-v1-comparison/report.json": "1db2294e250a36aa73d0a354b264656eff3d1e5f292628bc2c7c28e560b623ed",
    "docs/development/2026-11-16-conversion-material/reports/A17-v1-comparison/mask.json": "dc8bf9cfb0e10251dfc6ec6d7aa02f8d478c79f9d04ed9f1f722ff8adfd8855a",
}
PATCHES = {
    "left": (612, 320, 18, 128), "right": (1094, 320, 14, 128),
    "left_top": (612, 298, 18, 14), "right_top": (1094, 298, 14, 14),
    "center_top": (800, 302, 112, 6), "left_bottom": (612, 460, 18, 20),
    "right_bottom": (1094, 460, 14, 20),
    "bottom_interior_left": (704, 492, 12, 8),
    "bottom_interior_middle": (852, 492, 14, 8),
    "bottom_interior_right": (1047, 492, 12, 8),
}
CORRECTED = dict(PATCHES)
for name in ("right", "right_top", "right_bottom"):
    x, y, w, h = CORRECTED[name]
    CORRECTED[name] = (x + 1, y, w - 1, h)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def identities():
    result = {p: digest((ROOT / p).read_bytes()) for p in EXPECTED}
    assert result == EXPECTED, "Audited frozen inputs changed"
    return result


def box(rect):
    x, y, w, h = rect
    return (x, y, x + w, y + h)


def overlap(a, b):
    return max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[1], b[1]))


def f32(value):
    return struct.unpack("f", struct.pack("f", value))[0]


def function_slice(text, name):
    start = text.index("void " + name + "(")
    begin = text.index("{", start)
    depth = 1
    end = begin + 1
    while depth:
        depth += (text[end] == "{") - (text[end] == "}")
        end += 1
    return text[start:end]


def source_geometry():
    current = (ROOT / "apps/standalone/InstrumentView.cpp").read_text()
    previous = (ROOT / "../baseline/InstrumentView.cpp").read_text()
    conserved = {}
    for name in ("centered", "reference_outline", "reference_screw", "reference_heading", "reference_drawbar", "reference_controls"):
        a, b = function_slice(current, name), function_slice(previous, name)
        assert a == b, name
        conserved[name] = digest(a.encode())
    model = (ROOT / "apps/standalone/UiModel.cpp").read_text()
    centers_text = model.split("kReferenceDrawbarCenters{{", 1)[1].split("}}};", 1)[0]
    centers = [int(float(v)) for v in re.findall(r"([0-9]+\.0)F", centers_text)][9:]
    assert centers == [685, 734, 782, 830, 878, 927, 975, 1024, 1074]
    slots = [box((c - 21, 327 - 16, 42, 118 + 32)) for c in centers]
    border = (slots[-1][2] - 1, slots[-1][1], slots[-1][2], slots[-1][3])
    assert border == (1094, 311, 1095, 461)
    # reference_outline on Lower index4 bounds(855,309,46,197), thickness2.
    focus = [(855, 309, 901, 311), (855, 504, 901, 506),
             (855, 311, 857, 504), (899, 311, 901, 504)]
    font = (ROOT / "apps/standalone/FontData.h").read_text()
    atlases = {}
    for face in ("Sans", "Serif"):
        section = font.split("k" + face + "Glyphs{{", 1)[1].split("}};", 1)[0]
        glyphs = {}
        for row, code in re.findall(r"\{([^}]+)\}, // ASCII (\d+)", section):
            glyphs[int(code)] = tuple(map(int, row.split(",")))
        metadata = re.search(r"Atlas k" + face + r"\{\s*([\d,\s]+),\s*k" + face, font).group(1)
        atlases[face] = (tuple(map(int, metadata.split(","))), glyphs)
        assert len(glyphs) == 95
    glyph_boxes = []

    def text_support(label, bounds, initial_size, face, padding, owner):
        (aw, ah, ph, ascent, descent), glyphs = atlases[face]
        x, y, w, h = map(f32, bounds)
        size = min(f32(initial_size), f32(h / f32(1.2)))

        def width(size):
            scale, total = f32(size / ph), 0.0
            for letter in label:
                total = f32(total + f32(f32(glyphs[ord(letter)][6] * scale) / 64))
            return total

        available = f32(w - f32(2 * padding))
        if width(size) > available:
            size = f32(size * f32(max(f32(.1), available) / width(size)))
        pen = f32(x + f32(f32(w - width(size)) / 2))
        top = f32(y + f32(f32(h - f32(size * f32(1.2))) / 2))
        scale = f32(size / ph)
        baseline = f32(top + f32(ascent * scale))
        for index, letter in enumerate(label):
            gx, gy, gw, gh, bx, by, advance = glyphs[ord(letter)]
            if gw and gh:
                px, py = (2 if f32(gw * scale) < 1 else 0), (2 if f32(gh * scale) < 1 else 0)
                tx, ty = f32(pen + f32((bx - px) * scale)), f32(baseline + f32((by - py) * scale))
                tw, th = f32((gw + 2 * px) * scale), f32((gh + 2 * py) * scale)
                # Conservative full destination quad plus one pixel on every side;
                # no inference from whether candidate ink happens to be dark.
                guarded = (math.floor(tx) - 1, math.floor(ty) - 1,
                           math.ceil(f32(tx + tw)) + 1, math.ceil(f32(ty + th)) + 1)
                glyph_boxes.append({"owner": owner, "character": letter, "index": index,
                                    "target_xywh": [tx, ty, tw, th], "guarded_box": guarded})
            pen = f32(pen + f32(f32(advance * scale) / 64))

    text_support("LOWER MANUAL DRAWBARS", (616, 277, 484, 27), 16, "Serif", 3, "heading")
    labels = (ROOT / "apps/standalone/UiModel.h").read_text().split("kUiFootageLabels{", 1)[1].split("};", 1)[0]
    labels = re.findall(r'"([^"]+)"', labels)
    for i, c in enumerate(centers):
        text_support(labels[i], (c - 23, 467, 46, 23), 19, "Serif", 2, f"footage{i}")
        text_support("4", (c - 23, 491, 46, 15), 12, "Sans", 3, f"value{i}")
    for tick in range(9):
        text_support(str(tick), (638, 327 + 118 * tick / 8 - 7, 15, 14), 12, "Sans", 0, f"guide{tick}")
    # Other Lower foreground excludes these samples by these source envelopes:
    # heading rules y290..292; screws within 8x8; narrow four edge rules.
    decorations = [(616, 290, 1100, 292)]
    decorations += [box((x - 1, y - 1, 8, 8)) for x in (607, 1103) for y in (276, 495)]
    decorations += [box(v) for v in ((607, 272, 502, 1), (603, 276, 1, 225),
                                    (607, 505, 502, 1), (1113, 276, 1, 225))]
    patch_geometry = {}
    for name, rect in CORRECTED.items():
        b = box(rect)
        data = {"v1_border_pixels": overlap(box(PATCHES[name]), border),
                "v2_border_pixels": overlap(b, border),
                "slot_pixels": sum(overlap(b, s) for s in slots),
                "focus_pixels": sum(overlap(b, s) for s in focus),
                "guarded_glyph_intersections": [g for g in glyph_boxes if overlap(b, g["guarded_box"])],
                "decoration_intersections": [d for d in decorations if overlap(b, d)]}
        patch_geometry[name] = data
        assert not data["slot_pixels"] and not data["guarded_glyph_intersections"] and not data["decoration_intersections"], name
        assert data["focus_pixels"] == (16 if name == "bottom_interior_middle" else 0), name
    assert [patch_geometry[n]["v1_border_pixels"] for n in ("right", "right_top", "right_bottom")] == [128, 1, 1]
    # Source-derived canonical support. Old lattice fully enumerated; new mark
    # modulo bounds prove every 1x1 mark lies within this gradient union.
    old_rects = []
    rows, columns = 239 - 16, 516 - 21
    step = max(4, math.ceil(math.sqrt(rows * columns / (3 * 2048))))
    assert step == 5
    for row in range(1, rows, step):
        for column in range(1, columns, step * 3):
            grain = row * 1973 + column * 9277
            x, y = 600 + 7 + column + ((grain >> 5) % 3), 269 + 7 + row
            old_rects.extend([box((x, y, 1, 1)), box((x + 3, y + 1, 2, 1))])
    intrinsic = (604, 273, 1112, 504)
    assert len(old_rects) == 2970
    assert all(intrinsic[0] <= b[0] and b[2] <= intrinsic[2] and intrinsic[1] <= b[1] and b[3] <= intrinsic[3] for b in old_rects)
    return {"unchanged_function_hashes": conserved, "centers": centers,
            "slots": slots, "border_box": border, "focus_boxes": focus,
            "patches": patch_geometry, "guarded_glyph_boxes": glyph_boxes,
            "source_support": {"old_pairs": len(old_rects) // 2, "new_marks": 4608,
                "new_modulo_envelope": [606, 275, 1110, 502],
                "intrinsic_union_box": intrinsic, "intrinsic_pixels": 508 * 231,
                "expanded_box": [603, 272, 1113, 505], "expanded_pixels": 510 * 233}}


def capture(relative):
    result = subprocess.run([str(ROOT / relative), "--case", "28"], cwd=ROOT, capture_output=True, timeout=30, check=True)
    header_bytes, rgba = result.stdout.split(b"\n", 1)
    header = json.loads(header_bytes)
    assert header["schema"] == 1 and header["case"] == 28 and header["protocol"] == "lower-rack-material-v1"
    assert header["width"] == 1672 and header["height"] == 941 and len(rgba) == 1672 * 941 * 4
    assert header["scale"] == [1, 1] and header["viewport"] == [0, 0, 1672, 941] and not header["clip_enabled"]
    assert header["level"] == 4 and header["route"] == "B" and header["focus"] == [4, 1, 1, 4]
    assert not header["pending"] and header["held"]
    return header_bytes, header, rgba, Image.frombytes("RGBA", (1672, 941), rgba)


def statistics(image, rect):
    x, y, w, h = rect
    pixels = list(image.crop((x, y, x + w, y + h)).convert("RGB").getdata())
    values = [Q(2126 * r + 7152 * g + 722 * b, 10000) for r, g, b in pixels]
    n = len(values)
    mean = sum(values) / n
    xs = [Q(2 * (i % w) - w + 1, 2) for i in range(n)]
    ys = [Q(2 * (i // w) - h + 1, 2) for i in range(n)]
    slope_x = sum(x * z for x, z in zip(xs, values)) / sum(x * x for x in xs)
    slope_y = sum(y * z for y, z in zip(ys, values)) / sum(y * y for y in ys)
    # Independently evaluate every fitted residual, not a borrowed SSE routine.
    variance = sum((z - mean - slope_x * x - slope_y * y) ** 2 for x, y, z in zip(xs, ys, values)) / n
    return {"xywh": rect, "pixels": n, "mean_Yprime": mean,
            "mean_RGB": [Q(sum(p[c] for p in pixels), n) for c in range(3)],
            "slope_x": slope_x, "slope_y": slope_y, "residual_variance": variance,
            "residual_rms_display": math.sqrt(float(variance))}


def screens(actual, reference):
    rows = []

    def append(name, value, target, limit):
        rows.append({"name": name, "actual": value, "reference": target,
                     "absolute_error": abs(value - target), "limit": limit, "passed": abs(value - target) <= limit})

    for name in list(PATCHES)[:7]:
        append(name + "_mean_Yprime", actual[name]["mean_Yprime"], reference[name]["mean_Yprime"], Q(5, 2))
        for i, channel in enumerate("RGB"):
            append(name + "_mean_" + channel, actual[name]["mean_RGB"][i], reference[name]["mean_RGB"][i], Q(3))
    for name in ("left", "right"):
        a, b, limit = actual[name]["residual_variance"], reference[name]["residual_variance"], Q(1, 2)
        z = a + b - limit ** 2
        rows.append({"name": name + "_residual_rms", "actual_variance": a,
                     "reference_variance": b, "limit": limit,
                     "absolute_error_display": abs(math.sqrt(float(a)) - math.sqrt(float(b))),
                     "passed": z <= 0 or z ** 2 <= 4 * a * b})
        append(name + "_slope_x", actual[name]["slope_x"], reference[name]["slope_x"], Q(3, 50))
        append(name + "_slope_y", actual[name]["slope_y"], reference[name]["slope_y"], Q(1, 40))
    append("right_minus_left", actual["right"]["mean_Yprime"] - actual["left"]["mean_Yprime"],
           reference["right"]["mean_Yprime"] - reference["left"]["mean_Yprime"], Q(7, 4))
    assert len(rows) == 35
    return {"passes": sum(r["passed"] for r in rows), "failures": [r["name"] for r in rows if not r["passed"]], "all_35_outcomes": rows}


def main():
    before_ids = identities()
    geometry = source_geometry()  # Complete before obtaining either pixel stream.
    old = capture("../baseline/test_standalone_lower_rack_material_raster")
    new = capture("../build-native/apps/standalone/test_standalone_lower_rack_material_raster")
    assert old[0] == new[0], "Complete header bytes must be identical"
    reference = Image.open(ROOT / "docs/design/atlas-cover-reference.jpg").convert("RGB")
    assert reference.size == (1672, 941)
    assert digest(reference.tobytes()) == "07a7e35a2fd6610d623bbc1da8c995f3f4d95c4b45a0a5c1f41ad1395584bbeb"
    guards = {}
    for name, coords, expected in (
        ("entire_excluded_border", [(1094, y) for y in range(311, 461)], (36, 34, 30, 255)),
        ("descriptive_middle_focus", [(x, y) for x in (855, 856) for y in range(492, 500)], (165, 228, 223, 255)),
    ):
        assert all(old[3].getpixel(p) == new[3].getpixel(p) == expected for p in coords), name
        guards[name] = {"pixels": len(coords), "rgba": expected, "before_after_exact": True,
                        "expected_source_color_exact": True, "coordinates": coords}
    versioned = {}
    for version, rects in (("v1", PATCHES), ("v2", CORRECTED)):
        measurements = {label: {name: statistics(im, rect) for name, rect in rects.items()}
                        for label, im in (("reference", reference), ("before", old[3]), ("candidate", new[3]))}
        versioned[version] = {"measurements": measurements,
                             "before": screens(measurements["before"], measurements["reference"]),
                             "candidate": screens(measurements["candidate"], measurements["reference"])}
    assert versioned["v1"]["candidate"]["failures"] == ["right_residual_rms", "right_slope_x"]
    assert versioned["v1"]["before"]["passes"] == 7 and versioned["v1"]["candidate"]["passes"] == 33
    assert versioned["v2"]["before"]["passes"] == 6 and versioned["v2"]["candidate"]["passes"] == 35
    different = outside = 0
    for i in range(0, len(old[2]), 4):
        if old[2][i:i+4] != new[2][i:i+4]:
            different += 1
            y, x = divmod(i // 4, 1672)
            outside += not (603 <= x < 1113 and 272 <= y < 505)
    assert outside == 0
    # Inspect retained original data only after the independent computations.
    a17 = json.loads((REPORTS / "A17-v1-comparison/report.json").read_text())
    c28 = next(c for c in a17["cases"] if c["suite"] == "lower" and c["case"] == 28)
    assert a17["status"] == "failed" and c28["passed"] is False and c28["preservation_passed"] is True
    assert a17["totals"]["preservation_passed_pairs"] == 98 and a17["totals"]["failed_pairs"] == 1
    assert all(c["preservation_passed"] for c in a17["cases"])
    assert c28["before_rgba_sha256"] == digest(old[2]) and c28["after_rgba_sha256"] == digest(new[2])
    failure_artifacts = {}
    for label, artifact in c28["failure_artifacts"].items():
        payload = Path(artifact["path"]).read_bytes()
        assert len(payload) == artifact["bytes"] and digest(payload) == artifact["sha256"], label
        failure_artifacts[label] = artifact
    comparisons = 0
    for ours, theirs in (("before", "before"), ("candidate", "after")):
        for name, stats in versioned["v1"]["measurements"][ours].items():
            frozen = c28[theirs + "_statistics"]["patches"][name]
            for mine, key in (("mean_Yprime", "mean_exact"), ("slope_x", "slope_x_exact"),
                              ("slope_y", "slope_y_exact"), ("residual_variance", "residual_variance_exact")):
                assert stats[mine] == Q(frozen["Yprime"][key]); comparisons += 1
            for channel in range(3):
                assert stats["mean_RGB"][channel] == Q(frozen["RGB"][channel]["mean_exact"]); comparisons += 1
        own_outcomes = [r["passed"] for r in versioned["v1"][ours]["all_35_outcomes"]]
        assert own_outcomes == [r["passed"] for r in c28[theirs + "_reference_screens"]["screens"]]
    masks = json.loads((REPORTS / "A17-v1-comparison/mask.json").read_text())
    mask28 = next(c for c in masks["cases"] if c["suite"] == "lower" and c["case"] == 28)
    assert mask28["support"]["translated_intrinsic_union_box"] == list(geometry["source_support"]["intrinsic_union_box"])
    assert mask28["support"]["expanded_intrinsic_union_box"] == geometry["source_support"]["expanded_box"]
    after_ids = identities()
    assert before_ids == after_ids
    result = {"schema": 1, "worker": "A22", "scope": "Independent exact-hash protocol admission; canonical case28 only; no full98 rerun or full1:1 claim",
              "status": "passed", "cwd": str(ROOT), "python": sys.version, "pillow": pillow_version,
              "script_sha256": digest(Path(__file__).read_bytes()), "identities_before_and_after": before_ids,
              "source_geometry": geometry, "complete_metadata_bytes_equal": True,
              "native": {"before_rgba_sha256": digest(old[2]), "candidate_rgba_sha256": digest(new[2]),
                         "header_sha256": digest(old[0]), "different_pixels": different, "outside_allowance_pixels": outside},
              "foreground_guards": guards, "versioned_statistics_and_outcomes": versioned,
              "original_a17_exact_statistics_matches": comparisons,
              "original_a17_failure_artifacts_verified": failure_artifacts,
              "retained_a17_status": a17["status"], "retained_a17_totals": a17["totals"],
              "missing_gates": ["A24 versioned checker implementation/adversarial checks", "Root integrated acceptance of unchanged98-pair evidence with new protocol report", "Whole-interface1:1", "Real-display/DPI/accessibility journeys", "Hosted and platform/device qualification"]}
    OUT.write_text(json.dumps(result, indent=2, default=lambda v: str(v) if isinstance(v, Q) else v) + "\n")
    print(json.dumps({"report": str(OUT.relative_to(ROOT)), "sha256": digest(OUT.read_bytes()),
                      "v1_before": 7, "v1_candidate": 33, "v2_before": 6, "v2_candidate": 35,
                      "border_guard": 150, "focus_guard": 16, "original_exact_matches": comparisons,
                      "outside_allowance_pixels": outside}))


if __name__ == "__main__":
    main()
