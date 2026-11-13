#!/usr/bin/env python3
"""Build the committed standalone ASCII atlases; Pillow is authoring-only."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sys

try:
    import PIL
    from PIL import Image, ImageDraw, ImageFont, features
except ImportError as error:
    raise SystemExit("Font authoring needs the pinned Pillow in assets/standalone/fonts/requirements-authoring.txt") from error


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets/standalone/fonts"
HEADER = ROOT / "apps/standalone/FontData.h"
MANIFEST = ASSETS / "atlas-manifest.json"
FIRST, LAST = 32, 126
ATLAS_WIDTH = 512
PADDING = 2


@dataclass(frozen=True)
class Glyph:
    x: int
    y: int
    width: int
    height: int
    bearing_x: int
    bearing_y: int
    advance_64: int


@dataclass
class Atlas:
    name: str
    width: int
    height: int
    pixel_height: int
    ascent: int
    descent: int
    glyphs: list[Glyph]
    alpha: bytes
    rle: bytes


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encode_rle(alpha: bytes) -> bytes:
    encoded = bytearray()
    for value in alpha:
        if encoded and encoded[-1] == value and encoded[-2] < 255:
            encoded[-2] += 1
        else:
            encoded.extend((1, value))
    return bytes(encoded)


def decode_rle(encoded: bytes, expected: int) -> bytes:
    if len(encoded) % 2:
        raise ValueError("Incomplete alpha RLE pair")
    decoded = bytearray()
    for i in range(0, len(encoded), 2):
        count, value = encoded[i : i + 2]
        if count == 0 or count > expected - len(decoded):
            raise ValueError("Invalid alpha RLE run")
        decoded.extend(bytes((value,)) * count)
    if len(decoded) != expected:
        raise ValueError("Incorrect decoded alpha size")
    return bytes(decoded)


def render_atlas(source: dict) -> Atlas:
    font_path = ASSETS / source["file"]
    contents = font_path.read_bytes()
    if len(contents) != source["bytes"] or sha256(contents) != source["sha256"]:
        raise ValueError(f"Source font identity changed: {source['file']}")
    size = source["pixel_height"]
    font = ImageFont.truetype(str(font_path), size, layout_engine=ImageFont.Layout.BASIC)
    if font.getname() != (source["family"], source["style"]):
        raise ValueError(f"Source font name changed: {source['file']}")
    glyphs, images = [], []
    x, y, row_height = PADDING, PADDING, 0
    for codepoint in range(FIRST, LAST + 1):
        char = chr(codepoint)
        left, top, right, bottom = font.getbbox(char, anchor="ls")
        mask = Image.new("L", (max(1, right - left), max(1, bottom - top)), 0)
        ImageDraw.Draw(mask).text((-left, -top), char, font=font, fill=255, anchor="ls")
        ink = mask.getbbox()
        advance = round(font.getlength(char) * 64)
        if ink is None:
            glyphs.append(Glyph(0, 0, 0, 0, 0, 0, advance))
            images.append(None)
            continue
        mask = mask.crop(ink)
        left, top = left + ink[0], top + ink[1]
        width, height = mask.size
        if x + width + PADDING > ATLAS_WIDTH:
            x, y, row_height = PADDING, y + row_height + 2 * PADDING, 0
        glyphs.append(Glyph(x, y, width, height, left, top, advance))
        images.append(mask)
        x += width + 2 * PADDING
        row_height = max(row_height, height)
    used_height = y + row_height + PADDING
    atlas_height = 1 << (used_height - 1).bit_length()
    image = Image.new("L", (ATLAS_WIDTH, atlas_height), 0)
    for glyph, mask in zip(glyphs, images):
        if mask is not None:
            image.paste(mask, (glyph.x, glyph.y))
    alpha = image.tobytes()
    atlas = Atlas(source["role"].capitalize(), ATLAS_WIDTH, atlas_height, size,
                  *font.getmetrics(), glyphs, alpha, encode_rle(alpha))
    validate_atlas(atlas, images)
    return atlas


def validate_atlas(atlas: Atlas, images: list) -> None:
    if decode_rle(atlas.rle, atlas.width * atlas.height) != atlas.alpha:
        raise ValueError("Alpha RLE does not round-trip")
    if len(atlas.glyphs) != LAST - FIRST + 1 or not any(0 < a < 255 for a in atlas.alpha):
        raise ValueError("Missing ASCII glyphs or antialias coverage")
    occupied = set()
    for codepoint, glyph, mask in zip(range(FIRST, LAST + 1), atlas.glyphs, images):
        if not 0 < glyph.advance_64 <= 65535:
            raise ValueError(f"Invalid advance for ASCII {codepoint}")
        if mask is None:
            if codepoint != 32 or glyph.width or glyph.height:
                raise ValueError("Only ASCII space may have an empty glyph")
            continue
        if not (PADDING <= glyph.x and PADDING <= glyph.y and
                glyph.x + glyph.width + PADDING <= atlas.width and
                glyph.y + glyph.height + PADDING <= atlas.height and
                -atlas.ascent <= glyph.bearing_y and
                glyph.bearing_y + glyph.height <= atlas.descent):
            raise ValueError(f"Glyph bounds invalid for ASCII {codepoint}")
        rows = []
        for y in range(glyph.y - PADDING, glyph.y + glyph.height + PADDING):
            for x in range(glyph.x - PADDING, glyph.x + glyph.width + PADDING):
                inside = glyph.x <= x < glyph.x + glyph.width and glyph.y <= y < glyph.y + glyph.height
                index = y * atlas.width + x
                if inside:
                    if index in occupied:
                        raise ValueError("Overlapping glyph rectangles")
                    occupied.add(index)
                    rows.append(atlas.alpha[index])
                elif atlas.alpha[index] != 0:
                    raise ValueError("Nontransparent glyph gutter")
        if bytes(rows) != mask.tobytes():
            raise ValueError("Packed glyph differs from rasterized glyph")


def header_bytes(atlases: list[Atlas], license_text: str) -> bytes:
    lines = ["#pragma once", "", "// Generated by tools/generate_standalone_font.py; do not edit.",
             "// DejaVu 2.37 glyph coverage: printable ASCII 32..126 only.",
             "// Original font copyright, trademark and complete permission notice:"]
    lines += ["// " + line if line else "//" for line in license_text.splitlines()]
    lines += ["", "#include <array>", "#include <cstddef>", "#include <cstdint>", "#include <span>", "",
              "namespace hammond::standalone::font_data {", "",
              "inline constexpr unsigned char kFirstCodepoint = 32;",
              "inline constexpr unsigned char kLastCodepoint = 126;",
              "inline constexpr std::size_t kGlyphCount = 95;", "",
              "struct Glyph {",
              "    std::uint16_t x, y, width, height;",
              "    std::int16_t bearing_x, bearing_y; // From pen x and baseline y.",
              "    std::uint16_t advance_64; // Advance in 1/64 nominal pixels.",
              "};", "", "struct Atlas {",
              "    std::uint16_t width, height, pixel_height, ascent, descent;",
              "    std::span<const Glyph, kGlyphCount> glyphs;",
              "    const std::uint8_t* alpha_rle; // Consecutive {count, alpha} byte pairs.",
              "    std::size_t alpha_rle_size;", "};", ""]
    for atlas in atlases:
        lines.append(f"inline constexpr std::array<Glyph, kGlyphCount> k{atlas.name}Glyphs{{{{")
        for i, glyph in enumerate(atlas.glyphs, FIRST):
            values = (glyph.x, glyph.y, glyph.width, glyph.height, glyph.bearing_x,
                      glyph.bearing_y, glyph.advance_64)
            lines.append("    {" + ", ".join(str(v) for v in values) + "}, // ASCII " + str(i))
        lines += ["}};", "", f"inline constexpr std::array<std::uint8_t, {len(atlas.rle)}> k{atlas.name}AlphaRle{{{{"]
        for offset in range(0, len(atlas.rle), 24):
            lines.append("    " + ",".join(str(v) for v in atlas.rle[offset:offset + 24]) + ",")
        lines += ["}};", "", f"inline constexpr Atlas k{atlas.name}{{",
                  f"    {atlas.width}, {atlas.height}, {atlas.pixel_height}, {atlas.ascent}, {atlas.descent},",
                  f"    k{atlas.name}Glyphs, k{atlas.name}AlphaRle.data(), k{atlas.name}AlphaRle.size()}};", ""]
    lines += ["// Unsupported bytes use '?'. UTF-8 shaping, kerning and line breaks belong to callers.",
              "[[nodiscard]] inline constexpr const Glyph& glyph(",
              "    const Atlas& atlas, unsigned char codepoint) noexcept {",
              "    if (codepoint < kFirstCodepoint || codepoint > kLastCodepoint) codepoint = '?';",
              "    return atlas.glyphs[static_cast<std::size_t>(codepoint - kFirstCodepoint)];", "}", "",
              "// Decode at startup on the main thread. Destination must be exactly width*height.",
              "// Malformed streams return false; destination may then be partially written.",
              "[[nodiscard]] inline bool decode_alpha(",
              "    const Atlas& atlas, std::span<std::uint8_t> destination) noexcept {",
              "    const auto expected = static_cast<std::size_t>(atlas.width) * atlas.height;",
              "    if (expected == 0 || destination.size() != expected || atlas.alpha_rle == nullptr ||",
              "        atlas.alpha_rle_size % 2 != 0) return false;",
              "    std::size_t offset = 0;",
              "    for (std::size_t i = 0; i < atlas.alpha_rle_size; i += 2) {",
              "        const std::size_t count = atlas.alpha_rle[i];",
              "        if (count == 0 || count > expected - offset) return false;",
              "        for (std::size_t j = 0; j < count; ++j) {",
              "            destination[offset++] = atlas.alpha_rle[i + 1];",
              "        }", "    }", "    return offset == expected;", "}", "",
              "} // namespace hammond::standalone::font_data", ""]
    return "\n".join(lines).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Regenerate in memory, validate and compare committed bytes without writing")
    args = parser.parse_args()
    source = json.loads((ASSETS / "source-manifest.json").read_text(encoding="utf-8"))
    rasterizer = {"pillow": PIL.__version__, "freetype": features.version_module("freetype2"), "layout_engine": "BASIC"}
    if rasterizer != source["rasterizer"]:
        raise ValueError(f"Rasterizer identity mismatch: expected {source['rasterizer']}, found {rasterizer}")
    license_bytes = (ASSETS / source["license"]["file"]).read_bytes()
    if sha256(license_bytes) != source["license"]["sha256"]:
        raise ValueError("Font license identity changed")
    atlases = [render_atlas(font) for font in source["fonts"]]
    header = header_bytes(atlases, license_bytes.decode("utf-8"))
    if len(header) >= 1_000_000:
        raise ValueError("Generated header exceeds the 1 MB text budget")
    manifest = {"schema": 1, "generator": "tools/generate_standalone_font.py", "rasterizer": rasterizer,
                "source_manifest_sha256": sha256((ASSETS / "source-manifest.json").read_bytes()),
                "coverage": {"first": FIRST, "last": LAST, "glyphs_per_atlas": LAST - FIRST + 1},
                "rasterization": {"mode": "L", "anchor": "ls", "padding_pixels": PADDING, "packing": "ASCII-order shelves, power-of-two height", "rle": "uint8 count (1..255), uint8 alpha; row-major"},
                "header": {"file": str(HEADER.relative_to(ROOT)), "bytes": len(header), "sha256": sha256(header)},
                "atlases": [{"name": atlas.name, "width": atlas.width, "height": atlas.height,
                             "pixel_height": atlas.pixel_height, "ascent": atlas.ascent,
                             "descent": atlas.descent, "alpha_bytes": len(atlas.alpha),
                             "alpha_sha256": sha256(atlas.alpha), "rle_bytes": len(atlas.rle),
                             "rle_sha256": sha256(atlas.rle)} for atlas in atlases]}
    outputs = [(HEADER, header), (MANIFEST, (json.dumps(manifest, indent=2) + "\n").encode("utf-8"))]
    for path, data in outputs:
        if args.check:
            if not path.is_file() or path.read_bytes() != data:
                raise ValueError(f"Generated bytes differ: {path.relative_to(ROOT)}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    for atlas in atlases:
        print(f"{atlas.name}: {len(atlas.glyphs)} glyphs, {atlas.width}x{atlas.height}, {len(atlas.rle)} RLE bytes; bounds/gutters/alpha round-trip passed")
    print(f"{'Verified identical' if args.check else 'Generated'} {len(header)} header bytes; SHA-256 {sha256(header)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError) as error:
        print(f"font generation failed: {error}", file=sys.stderr)
        sys.exit(1)
