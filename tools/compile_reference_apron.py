#!/usr/bin/env python3
"""Verify the frozen reference apron and emit a bounded RGBA8 C++ header.

Ordinary builds use only the Python standard library. Explicit --verify-source
and --extract-to operations additionally require the pinned Pillow authoring
decoder. No source decoding or compression occurs during header compilation.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import stat
import sys
import tempfile
import zlib


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "assets/standalone/reference-apron-v1/manifest.json"
DEFAULT_SOURCE = ROOT / "docs/design/atlas-cover-reference.jpg"
MANIFEST_SHA256 = "41a8a503a8cef8c1df102599de83f6c2a3cf86c23cb2fbc8eedb18a6e52670d8"
SOURCE_SHA256 = "9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187"
DECODED_SOURCE_SHA256 = "07a7e35a2fd6610d623bbc1da8c995f3f4d95c4b45a0a5c1f41ad1395584bbeb"
PIXEL_SHA256 = "2646c6fe3fd813ae2907fb04dafacf504309247656860b7161d12ff2f85ded13"
PACKED_SHA256 = "87387e6c0bbd54012f0e0b23560175781a6515483b047822e4b64e4adfaac06c"
SOURCE_BYTES = 412664
PACKED_BYTES = 61162
WIDTH, HEIGHT, PITCH = 1640, 54, 6560
SOURCE_RECT = (16, 887, WIDTH, HEIGHT)
HOLE_RECT = (32, 2, 1556, 36)
PIXEL_BYTES = PITCH * HEIGHT
OPAQUE_TEXELS, ZERO_TEXELS = 32544, 56016
ASSET_FILE = "apron.rgba.gz"
MAX_MANIFEST_BYTES = 16 * 1024
MAX_SOURCE_BYTES = 512 * 1024
MAX_PACKED_BYTES = 128 * 1024
MAX_PIXEL_BYTES = PIXEL_BYTES
MAX_HEADER_BYTES = 3 * 1024 * 1024


class ReferenceApronError(ValueError):
    """An input, frozen identity, resource bound or output path was refused."""


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def bounded_read(path: Path, maximum: int) -> bytes:
    if not path.is_file():
        raise ReferenceApronError(f"input is not a regular file: {path}")
    with path.open("rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ReferenceApronError(f"input is not a regular file: {path}")
        raw = stream.read(maximum + 1)
    if not raw or len(raw) > maximum:
        raise ReferenceApronError(f"input must contain 1..{maximum} bytes: {path}")
    return raw


def require_identity(raw: bytes, size: int, digest: str, name: str) -> None:
    if len(raw) != size or sha256(raw) != digest:
        raise ReferenceApronError(f"{name} byte count or SHA-256 changed")


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ReferenceApronError(f"duplicate manifest key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ReferenceApronError(f"nonfinite manifest number: {value}")


def _reject_float(value: str) -> None:
    raise ReferenceApronError(f"manifest numbers must be integers: {value}")


def read_manifest(path: Path) -> tuple[dict, bytes]:
    raw = bounded_read(path, MAX_MANIFEST_BYTES)
    if sha256(raw) != MANIFEST_SHA256:
        raise ReferenceApronError("reference apron manifest SHA-256 changed")
    manifest = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object,
                          parse_constant=_reject_constant, parse_float=_reject_float)
    # The byte pin admits every field, including provenance and tool versions.
    # Keep the runtime-facing geometry, paths and pixel identities explicit too.
    if (type(manifest) is not dict
            or set(manifest) != {"schema_version", "identity", "evidence_class", "rights",
                                 "source", "authoring", "pixels", "compression", "asset"}
            or type(manifest.get("schema_version")) is not int
            or manifest["schema_version"] != 1
            or manifest.get("identity") != "standalone-reference-apron-v1"):
        raise ReferenceApronError("unsupported reference apron manifest")
    expected_asset = {
        "name": "reference-apron", "cpp_symbol": "kApron", "file": ASSET_FILE,
        "source_rect": list(SOURCE_RECT), "hole_rect": list(HOLE_RECT),
        "width": WIDTH, "height": HEIGHT, "pitch": PITCH,
        "pixel_bytes": PIXEL_BYTES, "pixel_sha256": PIXEL_SHA256,
        "opaque_texels": OPAQUE_TEXELS, "zero_texels": ZERO_TEXELS,
        "bytes": PACKED_BYTES, "sha256": PACKED_SHA256,
    }
    if manifest.get("asset") != expected_asset:
        raise ReferenceApronError("unsupported apron geometry or pixel identity")
    return manifest, raw


def read_source(path: Path) -> bytes:
    raw = bounded_read(path, MAX_SOURCE_BYTES)
    require_identity(raw, SOURCE_BYTES, SOURCE_SHA256, "source JPEG")
    return raw


def decode_gzip(packed: bytes, expected: int = PIXEL_BYTES) -> bytes:
    if (type(expected) is not int or not 0 < expected <= MAX_PIXEL_BYTES
            or not 0 < len(packed) <= MAX_PACKED_BYTES):
        raise ReferenceApronError("gzip packed or decoded bound is invalid")
    decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
    try:
        pixels = decoder.decompress(packed, expected + 1)
    except zlib.error as exc:
        raise ReferenceApronError(f"invalid gzip pixels: {exc}") from exc
    # eof includes trailer CRC/size validation. Never flush unbounded input;
    # unused_data excludes extra members and any trailing bytes, even zeroes.
    if (len(pixels) != expected or not decoder.eof
            or decoder.unconsumed_tail or decoder.unused_data):
        raise ReferenceApronError("gzip must contain one complete, exactly sized pixel stream")
    return pixels


def read_asset(directory: Path) -> bytes:
    packed = bounded_read(directory / ASSET_FILE, MAX_PACKED_BYTES)
    require_identity(packed, PACKED_BYTES, PACKED_SHA256, ASSET_FILE)
    pixels = decode_gzip(packed)
    require_identity(pixels, PIXEL_BYTES, PIXEL_SHA256, "apron RGBA pixels")
    return pixels


def make_header(pixels: bytes) -> bytes:
    require_identity(pixels, PIXEL_BYTES, PIXEL_SHA256, "header RGBA pixels")
    lines = [
        "// Generated by tools/compile_reference_apron.py; do not edit.",
        "// Decorative source pixels; not an application screenshot or control surface.",
        f"// Source JPEG SHA-256: {SOURCE_SHA256}",
        f"// Manifest SHA-256: {MANIFEST_SHA256}",
        f"// RGBA SHA-256: {PIXEL_SHA256}",
        "#pragma once", "", "#include <cstddef>", "#include <cstdint>", "",
        "namespace hammond::standalone::reference_apron {", "",
        "// RGBA8, top row first, no padding, straight binary alpha.",
        "// Upload as SDL_PIXELFORMAT_RGBA32; blend BLEND and sample Nearest.",
        "struct RgbaImage {", "    int width;", "    int height;", "    int pitch;",
        "    const std::uint8_t* pixels;", "    std::size_t byte_count;", "};", "",
        f"// Source (x, y, w, h): {SOURCE_RECT}; zero RGBA hole: {HOLE_RECT}.",
        "inline constexpr std::uint8_t kApronPixels[] = {",
    ]
    lines.extend("    " + ", ".join(f"0x{byte:02x}" for byte in pixels[start:start + 16]) + ","
                 for start in range(0, len(pixels), 16))
    lines.extend([
        "};", "inline constexpr RgbaImage kApron{",
        f"    {WIDTH}, {HEIGHT}, {PITCH}, kApronPixels, sizeof(kApronPixels)}};",
        f"static_assert(sizeof(kApronPixels) == {PIXEL_BYTES});",
        f"inline constexpr std::size_t kTotalPixelBytes = {PIXEL_BYTES};", "",
        "} // namespace hammond::standalone::reference_apron", "",
    ])
    header = "\n".join(lines).encode("ascii")
    if len(header) > MAX_HEADER_BYTES:
        raise ReferenceApronError("generated header exceeds the build bound")
    return header


def aliases(left: Path, right: Path) -> bool:
    # resolve catches relative/symlink-parent spellings; samefile catches hard
    # links, including aliases with otherwise unrelated resolved path names.
    return (left.resolve() == right.resolve()
            or (left.exists() and right.exists() and left.samefile(right)))


def check_outputs(outputs: list[Path], protected: set[Path]) -> None:
    for index, path in enumerate(outputs):
        if path.is_symlink() or (path.exists() and not path.is_file()):
            raise ReferenceApronError("output must be a regular file, not a symlink or directory")
        if any(aliases(path, source) for source in protected):
            raise ReferenceApronError("output must not alias a compiler input")
        if any(aliases(path, other) for other in outputs[:index]):
            raise ReferenceApronError("outputs must not alias each other")


def write_atomic(path: Path, raw: bytes, protected: set[Path]) -> bool:
    check_outputs([path], protected)
    if path.exists():
        with path.open("rb") as stream:
            if stream.read(len(raw) + 1) == raw:
                return False
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(prefix=".reference-apron-", dir=path.parent,
                                         delete=False) as stream:
            temporary = stream.name
            stream.write(raw)
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            os.unlink(temporary)
    return True


def source_pixels(source: bytes) -> tuple[bytes, dict]:
    require_identity(source, SOURCE_BYTES, SOURCE_SHA256, "source JPEG")
    try:
        import PIL
        from PIL import Image, features
    except ImportError as exc:
        raise ReferenceApronError(
            "source verification/extraction needs Pillow; ordinary header compilation does not") from exc
    versions = {
        "tool": "tools/compile_reference_apron.py", "tool_version": 1,
        "python": platform.python_version(), "pillow": PIL.__version__,
        "libjpeg_api": features.version("jpg"),
        "libjpeg_turbo": features.version("libjpeg_turbo"),
        "zlib_compile": zlib.ZLIB_VERSION, "zlib_runtime": zlib.ZLIB_RUNTIME_VERSION,
    }
    with Image.open(io.BytesIO(source)) as opened:
        if opened.format != "JPEG" or opened.size != (1672, 941):
            raise ReferenceApronError("unexpected source image format or dimensions")
        opened.load()
        rgb = opened.convert("RGB")
    # Mandatory full-image identity: crop equality cannot admit a changed decoder.
    require_identity(rgb.tobytes(), 1672 * 941 * 3, DECODED_SOURCE_SHA256,
                     "decoded source RGB")
    x, y, width, height = SOURCE_RECT
    pixels = bytearray(rgb.crop((x, y, x + width, y + height)).convert("RGBA").tobytes())
    hx, hy, hw, hh = HOLE_RECT
    for row in range(hy, hy + hh):
        start = row * PITCH + hx * 4
        pixels[start:start + hw * 4] = bytes(hw * 4)
    raw = bytes(pixels)
    require_identity(raw, PIXEL_BYTES, PIXEL_SHA256, "masked source crop")
    return raw, versions


def canonical_gzip(pixels: bytes) -> bytes:
    output = io.BytesIO()
    # GzipFile fixes the OS byte to 255 across Python versions.
    with gzip.GzipFile(fileobj=output, mode="wb", filename="", compresslevel=9,
                       mtime=0) as stream:
        stream.write(pixels)
    return output.getvalue()


def run(args: argparse.Namespace) -> str:
    manifest, manifest_bytes = read_manifest(args.input)
    source = read_source(args.source)
    protected = {args.input, args.source, args.input.parent / ASSET_FILE, Path(__file__)}
    if args.extract_to is not None:
        pixels, versions = source_pixels(source)
        if versions != manifest["authoring"]:
            raise ReferenceApronError(f"authoring toolchain differs from the frozen manifest: {versions}")
        packed = canonical_gzip(pixels)
        require_identity(packed, PACKED_BYTES, PACKED_SHA256, "authored gzip")
        outputs = [(args.extract_to / ASSET_FILE, packed),
                   (args.extract_to / "manifest.json", manifest_bytes)]
        # Validate both destinations before writing either, including hard links.
        check_outputs([path for path, _ in outputs], protected)
        for path, raw in outputs:
            write_atomic(path, raw, protected)
        return "Extracted exact masked apron with identical gzip and manifest bytes"
    pixels = read_asset(args.input.parent)
    if args.verify_source:
        authored, versions = source_pixels(source)
        if authored != pixels:
            raise ReferenceApronError("apron bytes differ from the masked original source crop")
        return "Verified exact source/mask equality; decoder " + json.dumps(versions, sort_keys=True)
    if args.output is not None:
        header = make_header(pixels)
        changed = write_atomic(args.output, header, protected)
        return (f"{'Wrote' if changed else 'Unchanged'} RGBA header: {len(header)} bytes; "
                f"SHA-256 {sha256(header)}; {PIXEL_BYTES} RGBA bytes")
    return (f"Verified reference apron and source; {PIXEL_BYTES} RGBA bytes; "
            f"manifest SHA-256 {MANIFEST_SHA256}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_MANIFEST,
                        help="frozen apron manifest; gzip is read from its directory")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE,
                        help="original JPEG, checked without decoding for ordinary builds")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--output", type=Path, help="generated ReferenceApronData.h in the build tree")
    mode.add_argument("--verify-only", action="store_true", help="verify locked inputs using only stdlib")
    mode.add_argument("--verify-source", action="store_true", help="also decode and compare the source; needs Pillow")
    mode.add_argument("--extract-to", type=Path, help="reauthor locked assets in a separate directory; needs Pillow")
    args = parser.parse_args(argv)
    try:
        print(run(args))
    except (ReferenceApronError, OSError, UnicodeError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"Reference apron error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
