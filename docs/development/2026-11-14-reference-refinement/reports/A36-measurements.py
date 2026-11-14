"""Read-only measurements of the retained reference and native v3 images.

Run with the qualified Pillow 13.0.0 environment; JSON goes to stdout only.
The geometric reference landmarks are visual estimates, not hardware data.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

from PIL import Image, __version__ as pillow_version

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[4]
GALLERY = ROOT / "examples/demos/standalone-interface-preview-v3"
REFERENCE = ROOT / "docs/design/atlas-cover-reference.jpg"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ink(path, roi):
    image = Image.open(path).convert("RGB")
    points = []
    for y in range(roi[1], roi[3]):
        for x in range(roi[0], roi[2]):
            r, g, b = image.getpixel((x, y))
            if r >= 130 and g >= 105 and r >= g and b <= 0.9 * r:
                points.append((x, y))
    box = [min(x for x, _ in points), min(y for _, y in points),
           max(x for x, _ in points) + 1, max(y for _, y in points) + 1]
    return {"roi_half_open": roi, "bbox_half_open": box, "ink_pixels": len(points),
            "width": box[2] - box[0], "height": box[3] - box[1],
            "normalized_bbox": [box[0] / image.width, box[1] / image.height,
                                box[2] / image.width, box[3] / image.height]}


def glyph_metrics(face, value, size):
    source = (ROOT / "apps/standalone/FontData.h").read_text()
    body = source.split("k" + face + "Glyphs{{", 1)[1].split("}};", 1)[0]
    glyphs = {int(code): tuple(map(int, fields.split(",")))
              for fields, code in re.findall(r"\{([^}]+)\}, // ASCII (\d+)", body)}
    nominal, ascent = (40, 38) if face == "Serif" else (32, 30)
    scale, advance, boxes = size / nominal, 0.0, []
    for char in value:
        _, _, width, height, bx, by, step = glyphs[ord(char)]
        if width and height:
            boxes.append((advance + bx * scale, (ascent + by) * scale,
                          advance + (bx + width) * scale, (ascent + by + height) * scale))
        advance += step * scale / 64
    return {"face": face, "text": value, "characters": len(value), "size": size,
            "advance": advance,
            "ink_rectangle_from_pen": [min(b[0] for b in boxes), min(b[1] for b in boxes),
                                       max(b[2] for b in boxes), max(b[3] for b in boxes)]}


qualified = json.loads((GALLERY / "inputs/source-qualification.json").read_text())
paths = [REFERENCE, *sorted((GALLERY / "images").glob("*.png"))]
images = {}
for path in paths:
    with Image.open(path) as image:
        images[path.relative_to(ROOT).as_posix()] = {
            "bytes": path.stat().st_size, "sha256": sha(path),
            "dimensions": list(image.size),
            "decoded_rgba8_sha256": hashlib.sha256(image.convert("RGBA").tobytes()).hexdigest()}

sources = {}
for relative in ["apps/standalone/InstrumentView.cpp", "apps/standalone/UiModel.cpp",
                 "apps/standalone/Drawing.cpp", "apps/standalone/FontData.h"]:
    digest = sha(ROOT / relative)
    committed = subprocess.check_output(["git", "show", qualified["published_commit"] + ":" + relative], cwd=ROOT)
    sources[relative] = {"sha256": digest,
                         "matches_capture": digest == qualified["source_sha256"][relative],
                         "matches_published": digest == hashlib.sha256(committed).hexdigest()}
assert all(v["matches_capture"] and v["matches_published"] for v in sources.values())

title_roi = [595, 10, 1081, 65]
titles = {"reference": ink(REFERENCE, title_roi)}
for name in ["play-reference-1672x941", "rotary-reference-1672x941", "service-reference-1672x941"]:
    titles[name] = ink(GALLERY / "images" / (name + ".png"), title_roi)

anchors = [
    ("Cabinet panel left x", "x", 1125, 2, 1124.831312),
    ("Upper key top y", "y", 548, 2, 542.76),
    ("Upper key bottom y", "y", 692, 2, 686.88),
    ("Lower key top y", "y", 720, 3, 726.88),
    ("Lower key bottom y", "y", 867, 3, 871.0),
    ("Drawbar rack top y", "y", 267, 2, 240.92),
    ("Drawbar rack bottom y", "y", 509, 2, 472.76),
]
landmarks = []
for name, axis, reference, uncertainty, native in anchors:
    extent = 1672 if axis == "x" else 941
    landmarks.append({"name": name, "axis": axis, "reference_visual_estimate": reference,
                      "reference_uncertainty_px": uncertainty, "native_logical_allocation": native,
                      "reference_normalized": reference / extent, "native_normalized": native / extent,
                      "native_minus_reference_px": native - reference})

report = {
    "schema_version": 1, "assignment": "A36", "reviewer": "/root/w06_a36_reference_visual_review",
    "published_product_commit": qualified["published_commit"],
    "published_product_tree": qualified["published_tree"],
    "qualified_executable_sha256": qualified["binary_sha256"],
    "pillow": pillow_version, "images": images, "selected_source_identity": sources,
    "mask": "Within named half-open ROI, R>=130 and G>=105 and R>=G and B<=0.9*R; no resampling or registration.",
    "titles": titles,
    "subtitles": {"reference": ink(REFERENCE, [600, 60, 1100, 90]),
                  "native": ink(GALLERY / "images/play-reference-1672x941.png", [650, 82, 1040, 106])},
    "landmarks": landmarks,
    "landmark_method": "Reference landmarks are direct visual pixel-coordinate estimates with stated uncertainty. Native values are the reviewed layout's logical allocations, cross-checked against the original capture. Neither is measured hardware geometry.",
    "cabinet_crop": {"source_rect_xywh": [1132, 174, 466, 397],
                     "native_logical_rect_xywh": [1132.831312, 174, 459.272688, 391.268792],
                     "native_source_scale": 459.272688 / 466,
                     "source": "assets/standalone/reference/manifest.json"},
    "header_proposal": {
        "condition": "layout.sidebar_pedals && layout.presentation == UiPresentation::Dimensional",
        "title": {"text": "TONEWHEEL ATLAS", "font_size": 42.75, "top": "layout.header.y - 4.5",
                  "fit": "Retain the existing symmetric title safe interval and fitted size/advance; no control geometry changes.",
                  "metrics": glyph_metrics("Serif", "TONEWHEEL ATLAS", 42.75),
                  "reference_pixel_target": "ink width464±3,height33±1,top20±1,visual center835±2 at1672×941"},
        "subtitle": {"text": "NOMINAL DRY ORGAN", "font_size": 17.0,
                     "top": "layout.header.y + 51.5", "face": "Sans", "color": "kUiBrass",
                     "desired_advance": 374.0,
                     "tracking": "(374 - drawing.text_width(text,17,Sans))/(17-1); clamp to available symmetric safe width and preserve all glyphs.",
                     "metrics": glyph_metrics("Sans", "NOMINAL DRY ORGAN", 17.0),
                     "reference_pixel_target": "ink width371±4,height12±1,top71±1,visual center835.5±2 at1672×941"},
        "status": "Calculated candidate only. Requires actual raster/timing qualification; no implementation or pass is claimed."},
    "visual_review": {
        "views_inspected": 8, "source_reference_inspected": True,
        "visible_crop_or_overlap_defect": False,
        "notes": {
            "reference_play": "Complete deeper manuals, disjoint cabinet/pedals, live held/focus/registration distinctions; title and subtitle still undersized/lower than reference.",
            "default_play": "Cabinet omitted, complete keyboards/pedals and four banks retained; no clipped visible footer/status row.",
            "minimum_play": "Complete controls and compact bank controls; preset legends remain tiny and need real display/DPI usability review.",
            "minimum_flat": "Plain panels and rectangular keyboards; held markers and focus remain distinguishable.",
            "both_service": "Six cards and28 rows visibly fit; correct singular1 target; current/unavailable/not-acquired values remain explicit.",
            "both_rotary": "Cabinet decorative/read-only labels fit; unavailable speeds, unacquired geometry and unmodeled brake do not imply connected audio."}},
    "limits": [
        "Visual inspection is not native input, accessibility, display/DPI, physical sound or deadline qualification.",
        "The generated concept has a different visible control inventory. Literal image equality is incompatible with displaying this complete working inventory in the same image.",
        "No image was edited, cropped, resampled, generated or overwritten; no app, shared build, CTest or GUI ran in A36.",
        "Pixel masks measure the retained decoded images, not glyph semantics or perceptual equivalence. Font metric rectangles are calculated, not a rendered candidate."
    ]}
print(json.dumps(report, indent=2) + "\n", end="")
