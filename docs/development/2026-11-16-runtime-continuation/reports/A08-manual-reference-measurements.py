#!/usr/bin/env python3
"""Pre-candidate material observations; not a whole-image parity comparator.

Run from any cwd. Reads unchanged reference and historical actual-app pixels,
then writes this script's sibling JSON. Never builds or renders a candidate.
Reference patches were selected by direct image inspection before this report.
"""
import hashlib
import json
import math
from pathlib import Path
import platform
import struct

from PIL import Image, __version__ as pillow_version


ROOT = Path(__file__).resolve().parents[4]
REFERENCE = ROOT / "docs/design/atlas-cover-reference.jpg"
GALLERY = ROOT / "examples/demos/lower-rack-material-v2/images/play-reference-1672x941.png"
EXPECTED = {
    REFERENCE: "9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187",
    GALLERY: "053dcd23028e865b3899d95ed10bb0172ec20929a67ad13559bca40e9fd1f74a",
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def f32(value):
    return struct.unpack("f", struct.pack("f", value))[0]


def statistics(pixels):
    n = len(pixels)
    assert n
    sums = [sum(p[c] for p in pixels) for c in range(3)]
    weighted_sum = 2126 * sums[0] + 7152 * sums[1] + 722 * sums[2]
    return {
        "pixels": n,
        "rgb_sum": sums,
        "mean_rgb": [v / n for v in sums],
        "Y_prime_numerator": weighted_sum,
        "Y_prime_denominator": 10000 * n,
        "mean_Y_prime": weighted_sum / (10000 * n),
        "pixel_sha256": sha(bytes(v for p in pixels for v in p)),
    }


def image_identity(path, image):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path.read_bytes()),
            "width": image.width, "height": image.height,
            "decoded_rgb_sha256": sha(image.tobytes())}


def rectangle_pixels(image, box):
    x, y, w, h = box
    return [image.getpixel((xx, yy)) for yy in range(y, y + h)
            for xx in range(x, x + w)]


def key_geometry(manual, index):
    # Independent transcription of the unchanged canonical layout equations.
    # Used only to locate historical gallery samples, not for paint/support.
    px, py, pw, ph, back = ((232., 528., 890., 170., .96) if manual == "upper"
                           else (224., 698., 898., 172., .95))
    left, top, width, height = px + 8., py + 20., pw - 16., ph - 28.

    def project(u, v):
        d = 1. - (1. - back) * v
        return (f32(left + width / 2. + width * back * (u - .5) / d),
                f32(top + height * back * v / d))

    accidental = index % 12 in (1, 3, 6, 8, 10)
    natural = sum(i % 12 not in (1, 3, 6, 8, 10) for i in range(index))
    if accidental:
        u0, u1, end = (natural - .30) / 36., (natural + .30) / 36., .62
    else:
        u0, u1, end = natural / 36., (natural + 1) / 36., 1.
    q = [project(u0, 0.), project(u1, 0.), project(u1, end), project(u0, end)]
    depth = f32(q[3][1] - q[0][1])
    front_depth = min(18., max(6., f32(depth * f32(.14))))
    split_y = f32(q[3][1] - front_depth)
    fraction = f32(f32(split_y - q[0][1]) / depth)

    def split(a, b):
        return (f32(q[a][0] + f32(f32(q[b][0] - q[a][0]) * fraction)), split_y)

    split_left, split_right = split(0, 3), split(1, 2)
    return {"top": [q[0], q[1], split_right, split_left],
            "front": [split_left, split_right, q[2], q[3]]}


def normalized_pixels(image, quad, u0, u1, v0, v1):
    y0, y1 = quad[0][1], quad[3][1]
    pixels = []
    positions = []
    for y in range(math.floor(y0), math.ceil(y1)):
        v = (y + .5 - y0) / (y1 - y0)
        if not v0 <= v < v1:
            continue
        left = quad[0][0] + (quad[3][0] - quad[0][0]) * v
        right = quad[1][0] + (quad[2][0] - quad[1][0]) * v
        for x in range(math.floor(left), math.ceil(right)):
            u = (x + .5 - left) / (right - left)
            if u0 <= u < u1:
                pixels.append(image.getpixel((x, y)))
                positions.append((x, y))
    assert pixels
    return pixels, [min(p[0] for p in positions), min(p[1] for p in positions),
                    max(p[0] for p in positions) + 1, max(p[1] for p in positions) + 1]


def main():
    for path, digest in EXPECTED.items():
        assert sha(path.read_bytes()) == digest, f"Frozen input changed: {path}"
    reference = Image.open(REFERENCE).convert("RGB")
    gallery = Image.open(GALLERY).convert("RGB")
    assert reference.size == gallery.size == (1672, 941)
    records = []
    for manual in ("upper", "lower"):
        lower = manual == "lower"
        for material in ("ivory", "ebony"):
            if material == "ivory":
                xs, width = [544, 566, 599], 6
                y_shift = 174 if lower else 0
                top_range = (718, 844) if lower else (548, 670)
                front_range = (844, 864) if lower else (670, 690)
                bands = [("back", "top", 562, 568), ("middle", "top", 607, 613),
                         ("nose", "top", 651, 657), ("shoulder", "top", 666, 669),
                         ("front_high", "front", 674, 679),
                         ("front_low", "front", 682, 687)]
                indices = [12, 29, 48]
            else:
                xs, width = ([529, 584, 622] if lower else [529, 585, 620]), 5
                y_shift = 173 if lower else 0
                top_range = (718, 779) if lower else (548, 606)
                front_range = (779, 798) if lower else (606, 625)
                bands = [("back", "top", 557, 562), ("middle", "top", 575, 580),
                         ("nose", "top", 595, 600), ("shoulder", "top", 603, 605),
                         ("front_high", "front", 609, 614),
                         ("front_low", "front", 617, 622)]
                indices = [13, 30, 49]
            for band, face, start, end in bands:
                y0, y1 = start + y_shift, end + y_shift
                extent = top_range if face == "top" else front_range
                v0, v1 = (y0 - extent[0]) / (extent[1] - extent[0]), (y1 - extent[0]) / (extent[1] - extent[0])
                boxes = [(x, y0, width, y1 - y0) for x in xs]
                ref_pixels = [p for box in boxes for p in rectangle_pixels(reference, box)]
                historical = []
                for index in indices:
                    q = key_geometry(manual, index)[face]
                    pixels, bounds = normalized_pixels(gallery, q, .35, .65, v0, v1)
                    historical.append({"key_index": index, "pixel_bounds_xyxy": bounds,
                                       **statistics(pixels)})
                records.append({"manual": manual, "material": material, "band": band,
                                "face": face, "reference_boxes_xywh": boxes,
                                "reference_face_y_extent": list(extent),
                                "app_normalized_window": {"u": [.35, .65], "v": [v0, v1]},
                                "reference": statistics(ref_pixels),
                                "historical_gallery_keys": historical,
                                "historical_gallery_equal_weight_mean_Y_prime":
                                    sum(p["mean_Y_prime"] for p in historical) / len(historical)})
    report = {
        "schema": 1,
        "identity": "manual-key-material-v1-pre-candidate-observations",
        "evidence_class": "Uncalibrated design-concept RGB statistics and historical actual-app pixels",
        "scope": "Frozen quiet patches; not full-frame equality or current-source candidate acceptance",
        "source_transition": {"initial_session_commit": "3520c96adcdcf4ce4bcb860082354bf0050a89c3",
                              "contract_stage_commit": "79bf34091dda5dc0528cf584891cff3e09657c66",
                              "reason": "Root integrated footage typography; reference_key remained unchanged"},
        "reference": image_identity(REFERENCE, reference),
        "historical_gallery": {**image_identity(GALLERY, gallery),
                               "executable_sha256": "131b86779e52776ebab6ee73ec46341b7eeac7888f4df2d1b37cce62ad402da9",
                               "limitations": "Historical Lower-stage capture, before typography; selected keys are idle; not a new run"},
        "decoder": {"python": platform.python_version(), "Pillow": pillow_version},
        "statistic": "Y_prime=(2126R+7152G+722B)/10000 in encoded 8-bit RGB; not physical luminance",
        "sampling": "Reference boxes use integer coordinates, half-open bounds, no resampling. App pixel centers use independently transcribed canonical quads and normalized windows; no image registration, threshold masking or fitted gain.",
        "reference_extent_warning": "Face y extents are visual registration choices for material coordinates, not corrected or calibrated key geometry.",
        "records": records,
    }
    destination = Path(__file__).with_suffix(".json")
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {destination.relative_to(ROOT)}: {len(records)} reference groups, "
          f"{sum(len(r['reference_boxes_xywh']) for r in records)} fixed patches")
    for record in records:
        print(f"{record['manual']:5s} {record['material']:5s} {record['band']:10s} "
              f"reference Y'={record['reference']['mean_Y_prime']:.6f}; "
              f"historical gallery={record['historical_gallery_equal_weight_mean_Y_prime']:.6f}")


if __name__ == "__main__":
    main()
