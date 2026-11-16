#!/usr/bin/env python3
"""Read-only rim authoring observations; writes only its new JSON receipt."""
from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path
import platform
import subprocess
import zlib

import PIL
from PIL import Image, features


ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).with_suffix(".json")
RECT = (48, 510, 1074, 18)
SOURCE = ROOT / "docs/design/atlas-cover-reference.jpg"
CURRENT = ROOT / "examples/demos/lower-rack-material-v2/images/play-reference-1672x941.png"


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def identity(path: Path) -> dict:
    raw = path.read_bytes()
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": len(raw), "sha256": digest(raw)}


def canonical_gzip(raw: bytes) -> bytes:
    out = io.BytesIO()
    with gzip.GzipFile(fileobj=out, mode="wb", filename="", compresslevel=9, mtime=0) as stream:
        stream.write(raw)
    return out.getvalue()


def row_sums(im: Image.Image, rect: tuple[int, int, int, int]) -> dict:
    x, y, w, h = rect
    rows = []
    for yy in range(y, y + h):
        values = list(im.crop((x, yy, x + w, yy + 1)).getdata())
        rgb = [sum(p[c] for p in values) for c in range(3)]
        yn = [2126 * p[0] + 7152 * p[1] + 722 * p[2] for p in values]
        total = sum(yn)
        rows.append({"y": yy, "rgb_sums": rgb, "y_numerator_sum": total,
                     "y_mean": total / (10000 * w),
                     "row_sse_numerator": w * sum(v * v for v in yn) - total * total,
                     "row_sse_denominator": w * 10000 ** 2})
    return {"rect": list(rect), "rows": rows}


def main() -> None:
    before = SOURCE.read_bytes()
    assert len(before) == 412664
    assert digest(before) == "9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187"
    with Image.open(io.BytesIO(before)) as opened:
        assert opened.format == "JPEG" and opened.size == (1672, 941)
        opened.load()
        reference = opened.convert("RGB")
    assert digest(reference.tobytes()) == "07a7e35a2fd6610d623bbc1da8c995f3f4d95c4b45a0a5c1f41ad1395584bbeb"
    with Image.open(CURRENT) as opened:
        opened.load()
        current = opened.convert("RGB")
    x, y, w, h = RECT
    pixels = reference.crop((x, y, x + w, y + h)).tobytes()
    packed = canonical_gzip(pixels)
    assert packed == canonical_gzip(pixels)
    decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
    decoded = decoder.decompress(packed, len(pixels) + 1)
    assert decoded == pixels and decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail
    assert packed[3:10] == bytes((0, 0, 0, 0, 0, 2, 255))
    selected = [(280, 518, 120, 6), (650, 518, 120, 6), (980, 518, 120, 6)]
    old = [
        "assets/standalone/reference/manifest.json", "tools/compile_reference_art.py",
        "assets/standalone/reference/cabinet.rgb.gz", "assets/standalone/reference/left-wood-cheek.rgb.gz",
        "assets/standalone/reference/right-wood-cheek.rgb.gz", "apps/standalone/Drawing.cpp",
        "apps/standalone/Drawing.h", "apps/standalone/InstrumentView.cpp", "apps/standalone/UiModel.h",
        "apps/standalone/UiModel.cpp", "apps/standalone/FontData.h", "docs/design/atlas-reference.json",
    ]
    a = reference.crop((x, y, x + w, y + h)).tobytes()
    b = current.crop((x, y, x + w, y + h)).tobytes()
    report = {
        "schema": "keyboard-rim-authoring-observations-v1",
        "status": "proposal-inputs-only-no-production-or-native-candidate",
        "cwd": str(ROOT),
        "head_observed": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "source": identity(SOURCE),
        "source_decoded_rgb_sha256": digest(reference.tobytes()),
        "current_capture": identity(CURRENT),
        "current_decoded_rgb_sha256": digest(current.tobytes()),
        "authoring": {"python": platform.python_version(), "pillow": PIL.__version__,
                      "libjpeg_api": features.version("jpg"), "libjpeg_turbo": features.version("libjpeg_turbo"),
                      "zlib_compile": zlib.ZLIB_VERSION, "zlib_runtime": zlib.ZLIB_RUNTIME_VERSION},
        "proposed_asset": {"source_rect": list(RECT), "width": w, "height": h, "pitch": 3*w,
                           "pixel_bytes": len(pixels), "pixel_sha256": digest(pixels),
                           "gzip_bytes": len(packed), "gzip_sha256": digest(packed),
                           "gzip_header_hex": packed[:10].hex(), "round_trip_exact": True,
                           "repeat_gzip_exact": True, "asset_files_written": False},
        "full_band_descriptive": {"pixels": w*h,
                                  "differing_rgb_pixels": sum(a[i:i+3] != b[i:i+3] for i in range(0, len(a), 3)),
                                  "reference_row_profiles": row_sums(reference, RECT),
                                  "current_row_profiles": row_sums(current, RECT)},
        "selected_profile_witnesses": [{"reference": row_sums(reference, rect), "current": row_sums(current, rect)}
                                       for rect in selected],
        "source_join_observations": [
            {"x_range_half_open": [48, 232], "finding": "Furniture and wood cheek shoulder; no caption/tablet."},
            {"x_range_half_open": [232, 1122], "finding": "Polished rim crest and dark recess; no caption/control."},
            {"finding": "The slanted cheek/rim transition crosses the crop near x232; preserve all original pixels, no stitched segments."},
        ],
        "proposed_canonical_unoccluded_exact_roi": [48, 515, 1073, 10],
        "occlusion_source_argument": {
            "rack_bottom": 508, "largest_shadow_bottom_exclusive": 515,
            "upper_manual_top": 528, "largest_shadow_top_inclusive": 525,
            "cabinet_left": 1126, "largest_shadow_left_inclusive": 1121,
            "caution": "This is a source-derived proposal; independent native fixture admission must confirm raster boundaries before paint. Final whole crop may not equal source because retained shadows overdraw it."},
        "preserved_inputs": [identity(ROOT / name) for name in old],
        "limits": ["No production painter, texture, compiler, asset, CMake, build or native candidate changed.",
                   "Current app PNG is an observed gallery input, not this future slice's genuine before executable.",
                   "Full-band differences are descriptive, not a similarity tolerance or whole-interface waiver.",
                   "Source is user-supplied generated concept artwork; physical and publication-rights gates unchanged."]
    }
    assert SOURCE.read_bytes() == before
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"report": OUT.relative_to(ROOT).as_posix(), "asset": report["proposed_asset"],
                      "authoring": report["authoring"], "differing_pixels": report["full_band_descriptive"]["differing_rgb_pixels"]}, indent=2))


if __name__ == "__main__":
    main()
