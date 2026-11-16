#!/usr/bin/env python3
"""Read-only image observations for the prospective whole-window plan.

This is an A39 report reproducer, not an admission checker or production test.
It writes JSON only to stdout. No image, contract, source, or gallery is changed.
"""

from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import platform

from PIL import Image, features, __version__ as pillow_version


ROOT = Path(__file__).resolve().parents[4]
GALLERY = ROOT / "examples/demos/upper-rack-material-v1"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_identity(path):
    raw = path.read_bytes()
    return {"path": str(path.relative_to(ROOT)), "bytes": len(raw), "sha256": digest(raw)}


def decode(path):
    with Image.open(path) as image:
        image.load()
        return image.convert("RGB"), image.convert("RGBA")


def comparison(reference, current, box):
    x, y, width, height = box
    edges = (x, y, x + width, y + height)
    left = reference.crop(edges).tobytes()
    right = current.crop(edges).tobytes()
    pixels = width * height
    differing = 0
    sums = [0, 0, 0]
    squared = [0, 0, 0]
    maxima = [0, 0, 0]
    rows = [0] * height
    bounds = [width, height, -1, -1]
    for offset in range(0, len(left), 3):
        values = [abs(left[offset + channel] - right[offset + channel]) for channel in range(3)]
        if any(values):
            differing += 1
            py, px = divmod(offset // 3, width)
            rows[py] += 1
            bounds[0] = min(bounds[0], px)
            bounds[1] = min(bounds[1], py)
            bounds[2] = max(bounds[2], px)
            bounds[3] = max(bounds[3], py)
        for channel, value in enumerate(values):
            sums[channel] += value
            squared[channel] += value * value
            maxima[channel] = max(maxima[channel], value)
    return {
        "box_xywh": list(box),
        "pixels": pixels,
        "equal_rgb_pixels": pixels - differing,
        "different_rgb_pixels": differing,
        "different_fraction": differing / pixels,
        "channel_absolute_error_sums_rgb": sums,
        "channel_squared_error_sums_rgb": squared,
        "channel_absolute_max_rgb": maxima,
        "channel_mean_absolute_error_rgb": [value / pixels for value in sums],
        "channel_root_mean_square_error_rgb": [math.sqrt(value / pixels) for value in squared],
        "difference_box_xywh": None if differing == 0 else [
            bounds[0] + x, bounds[1] + y,
            bounds[2] - bounds[0] + 1, bounds[3] - bounds[1] + 1,
        ],
        "different_pixels_per_row": rows,
    }


def plane_patch(image, box):
    """Exact rational plane fit to encoded Y' numerator using centered axes."""
    x, y, width, height = box
    data = image.crop((x, y, x + width, y + height)).tobytes()
    count = width * height
    total = total2 = xy = yy = x2 = y2 = 0
    for index in range(count):
        row, column = divmod(index, width)
        offset = 3 * index
        value = 2126 * data[offset] + 7152 * data[offset + 1] + 722 * data[offset + 2]
        cx = 2 * column - width + 1
        cy = 2 * row - height + 1
        total += value
        total2 += value * value
        xy += cx * value
        yy += cy * value
        x2 += cx * cx
        y2 += cy * cy
    sse = Fraction(total2) - Fraction(total * total, count) - Fraction(xy * xy, x2) - Fraction(yy * yy, y2)
    mean = Fraction(total, count * 10000)
    return {
        "box_xywh": list(box), "pixels": count,
        "encoded_y_prime_mean": float(mean),
        "encoded_y_prime_plane_residual_population_rms": math.sqrt(float(sse / count)) / 10000,
        "mean_exact": str(mean), "residual_sse_numerator_units_exact": str(sse),
        "sufficient_integer_statistics": {
            "sum_y_numerator": total, "sum_y_numerator_squared": total2,
            "sum_centered_x_times_y_numerator": xy,
            "sum_centered_y_times_y_numerator": yy,
            "sum_centered_x_squared": x2, "sum_centered_y_squared": y2,
        },
    }


def main():
    reference_path = ROOT / "docs/design/atlas-cover-reference.jpg"
    reference, _ = decode(reference_path)
    art_manifest = json.loads((ROOT / "assets/standalone/reference/manifest.json").read_text())
    assert file_identity(reference_path)["sha256"] == art_manifest["source"]["sha256"]
    assert digest(reference.tobytes()) == art_manifest["source"]["decoded_rgb_sha256"]
    provenance = json.loads((GALLERY / "provenance.json").read_text())
    images = []
    current = None
    for case in provenance["cases"]:
        path = GALLERY / case["image"]["path"]
        rgb, rgba = decode(path)
        identity = file_identity(path)
        assert identity["bytes"] == case["image"]["png"]["bytes"]
        assert identity["sha256"] == case["image"]["png"]["sha256"]
        assert digest(rgba.tobytes()) == case["image"]["decoded_sha256"]
        assert rgb.size == (case["width"], case["height"])
        images.append({
            **identity, "size": list(rgb.size),
            "rgb_sha256": digest(rgb.tobytes()), "rgba_sha256": digest(rgba.tobytes()),
            "matches_retained_capture_identity": True,
        })
        if case["name"] == "play-reference-1672x941":
            current = rgb
    assert len(images) == 12
    assert current is not None and current.size == reference.size == (1672, 941)

    # These nine disjoint reporting bands cover the ENTIRE image. They are
    # neither painter permissions nor semantic exemptions. Include every margin.
    regions = {
        "header_and_top_furniture": (0, 0, 1672, 125),
        "performance_left_band": (0, 125, 1126, 144),
        "upper_rack_left_band": (0, 269, 600, 241),
        "lower_rack_band": (600, 269, 526, 241),
        "rack_to_manual_rim_band": (0, 510, 1126, 18),
        "upper_manual_and_presets_band": (0, 528, 1126, 170),
        "lower_manual_and_presets_band": (0, 698, 1126, 189),
        "cabinet_right_band": (1126, 125, 546, 762),
        "footer_and_bottom_furniture": (0, 887, 1672, 54),
    }
    measurements = {name: comparison(reference, current, box) for name, box in regions.items()}
    whole = comparison(reference, current, (0, 0, 1672, 941))
    assert sum(value["pixels"] for value in measurements.values()) == whole["pixels"]
    assert sum(value["different_rgb_pixels"] for value in measurements.values()) == whole["different_rgb_pixels"]
    # Reject a prospective report partition that double-counts or omits pixels.
    coverage = bytearray(1672 * 941)
    for x, y, width, height in regions.values():
        for row in range(y, y + height):
            for column in range(x, x + width):
                coverage[row * 1672 + column] += 1
    assert min(coverage) == max(coverage) == 1
    cabinet = comparison(reference, current, (1132, 174, 466, 397))

    patches = {
        "upper_left_frozen_v1_1": (88, 320, 18, 128),
        "upper_right_frozen_v1_1": (572, 320, 14, 128),
        "lower_left_prospective_observation": (612, 320, 18, 128),
        "lower_right_prospective_observation": (1094, 320, 14, 128),
    }
    patch_results = {name: {"reference": plane_patch(reference, box), "current_gallery": plane_patch(current, box)} for name, box in patches.items()}
    report = {
        "schema_version": 1,
        "worker": "/root/w07_a39",
        "status": "descriptive_observations_only_no_admission",
        "command": "python3 -B docs/development/2026-11-15-streaming-continuation/reports/A39-visual-observations.py",
        "method": {
            "alignment": "Same 1672x941 origin and integer pixel coordinates; no crop, registration, warp, resampling, gamma, ICC, EXIF, exposure or gain adjustment to either input.",
            "comparisons": "Unweighted encoded RGB differences. JPEG has no reference alpha; candidate RGBA hashes remain separate. No SSIM/perceptual score or success threshold is defined.",
            "partition": "All pixels accounted for exactly once. Reporting regions are not edit masks or exclusions. Cabinet ROI is additional, not added twice to the window total.",
            "patches": "Half-open rectangles, encoded Y'=(2126R+7152G+722B)/10000, exact rational least-squares plane, population RMS. New Lower patches are observations for protocol authoring and have no admitted tolerance.",
            "state_limit": "Current gallery is an actual runtime scene, not a frozen-state before/after comparison; held keys, correct gain direction, live values/tools, truthful labels and runtime footer all remain in raw differences.",
            "physical_limit": "Image statistics and decorative artwork supply no display, accessibility, instrument material, audio or physical fidelity result.",
        },
        "decoder": {
            "python": platform.python_version(), "pillow": pillow_version,
            "jpeg_api": features.version_codec("jpg"),
            "libjpeg_turbo": features.version_feature("libjpeg_turbo"),
        },
        "reference": {**file_identity(reference_path), "size": list(reference.size), "rgb_sha256": digest(reference.tobytes())},
        "gallery_images": images,
        "capture_executable_sha256": provenance["executable"]["after"]["sha256"],
        "gallery_provenance": file_identity(GALLERY / "provenance.json"),
        "art_manifest": file_identity(ROOT / "assets/standalone/reference/manifest.json"),
        "complete_window": whole,
        "complete_disjoint_partition": measurements,
        "cabinet_decorative_roi": cabinet,
        "window_without_cabinet_accounting": {
            "pixels": whole["pixels"] - cabinet["pixels"],
            "equal_rgb_pixels": whole["equal_rgb_pixels"] - cabinet["equal_rgb_pixels"],
            "different_rgb_pixels": whole["different_rgb_pixels"] - cabinet["different_rgb_pixels"],
            "cabinet_fraction_of_complete_window": cabinet["pixels"] / whole["pixels"],
            "boundary": "Decomposition only; cabinet stays in the complete-window report and no exterior pixels are excluded from a parity claim.",
        },
        "patch_observations": patch_results,
        "reproducer": file_identity(Path(__file__).resolve()),
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
