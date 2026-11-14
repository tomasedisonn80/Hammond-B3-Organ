# Exact decorative reference assets

Contract: **`standalone-reference-decoration-v1`**. These are exact decorative
crops of the [retained atlas JPEG](design/atlas-reference.json), not application
screenshots or interactive controls. The native renderer continues to draw all
controls, text, values, keys and focus from its copied model under the
[layout contract](REFERENCE_UI_DESIGN.md).

## Source and admitted regions

Original JPEG: 1672 × 941, 412,664 bytes, SHA-256
`9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187`.
It is the unchanged image object from atlas pages 1/409. The
[manifest](../assets/standalone/reference/manifest.json) retains the PDF identity,
source identity, complete decoded-source identity, decoder versions, crop
rectangles, pixel hashes, delivered byte hashes and evidence/rights boundaries.
No external artwork was acquired. The existing project publication-rights gate
is unchanged.

| Asset / generated descriptor | Exact source `(x,y,w,h)` | RGB bytes | Gzip bytes |
| --- | --- | ---: | ---: |
| Cabinet / `kCabinet` | `(1132,174,466,397)` | 555,006 | 369,409 |
| Left cheek / `kLeftWoodCheek` | `(0,0,24,941)` | 67,752 | 52,070 |
| Right cheek / `kRightWoodCheek` | `(1604,0,68,941)` | 191,964 | 142,330 |
| Total | Three separate images | 814,722 | 563,809 |

Exact crop inspection found that the originally proposed 72-pixel left strip
included portions of both `BASS` tablets and their legends. That region is
explicitly rejected in the manifest. Its control-free outer 24-pixel strip is
used instead; its pixels are unchanged. The cabinet excludes its heading,
microphone knobs and speed tablets. The right cheek contains wood/edge only.
The lower rail, with baked `DESIGN CONCEPT` text, is not an asset.

Pillow 13.0.0 with libjpeg-turbo 3.2.0 (JPEG API 6.2) decoded the supplied JPEG
using `Image.open`, `load()` and `convert("RGB")`. There is no ICC transform,
EXIF transpose, resampling, retouching, compositing or color adjustment. Each
crop stores eight-bit interleaved RGB, top row first, with no row padding.
Gzip uses level 9, one member, timestamp zero, no filename and OS byte 255;
Python 3.12.14 and zlib 1.3.2 authored these bytes. All versions are retained.

## Normal build: standard library only

Run from the repository root:

```sh
python3 -S tools/compile_reference_art.py --verify-only
python3 -S tools/compile_reference_art.py \
  --input assets/standalone/reference/manifest.json \
  --source docs/design/atlas-cover-reference.jpg \
  --output build/generated/ReferenceArtData.h
```

The compiler reads the JPEG only to verify its original bytes; it does not
decode JPEG during normal builds. It admits the frozen manifest, compressed
identities, exact expanded sizes and RGB hashes before changing the destination.
The complete manifest hash is pinned in the compiler, so editing a blob and
its advertised hash together is rejected. Gzip decompression has an explicit
output bound and rejects incomplete streams, extra bytes and extra members.
Input aliases and symlink output files are rejected. Successful output uses
atomic replacement; a byte-identical header keeps its existing timestamp.

The three raw arrays occupy 814,722 bytes in the C++ image. Their generated
header is 5,093,899 bytes because it spells the bytes as hexadecimal constants;
it belongs in the build tree and is not checked in. Normal builds need no
Pillow, runtime image decoder, new C++ compression dependency or network access.
Python 3.10+ satisfies this compiler's standard-library requirements.

The standalone integration owner should generate
`${CMAKE_CURRENT_BINARY_DIR}/generated/ReferenceArtData.h`, add that output to
`hammond_standalone` sources, and use the existing generated include directory.
The custom command must depend on:

- `tools/compile_reference_art.py`
- `assets/standalone/reference/manifest.json`
- All three `assets/standalone/reference/*.rgb.gz` files
- `docs/design/atlas-cover-reference.jpg`

These dependencies make any source/asset change rerun admission. CMake and the
renderer are deliberately outside this asset assignment; their integration and
native-capture acceptance are separate work.

## Native texture API

The generated header has no SDL dependency. It defines
`hammond::standalone::reference_art::RgbImage` with `int width`, `height`,
`pitch`, `const std::uint8_t* pixels`, and `std::size_t byte_count`, and the
three `inline constexpr` descriptors named above. Pixel arrays have static
lifetime. Their channels are independent of host endianness.

The renderer can prepare each texture with this ordinary SDL2 sequence:

```cpp
#include "ReferenceArtData.h"

const auto& art = hammond::standalone::reference_art::kCabinet;
SDL_Texture* texture = SDL_CreateTexture(
    renderer, SDL_PIXELFORMAT_RGB24, SDL_TEXTUREACCESS_STATIC,
    art.width, art.height);
if (texture && SDL_UpdateTexture(texture, nullptr, art.pixels, art.pitch) != 0) {
    SDL_DestroyTexture(texture);
    texture = nullptr;
}
```

Prepare/upload, renderer-reset recovery and destruction belong to the main/UI
thread. Keep textures for reuse between frames and destroy them with the
owning renderer. On failure, use the procedural decorative fallback and keep
all instrument actions usable. No asset operation belongs in audio processing.
Place the cabinet only in `layout.cabinet_art` with the original 466:397 aspect
ratio; it remains explicitly labeled as an unconnected cabinet reference.
Decorative assets introduce no control IDs or hit targets.

## Optional authoring and source comparison

The [authoring requirements](../assets/standalone/reference/requirements-authoring.txt)
are separate from build requirements. A decoder with different output is
rejected by the frozen full-image and crop pixel hashes. Exact re-extraction
also requires the recorded authoring toolchain and identical gzip identities.
Use a separate output directory so the admitted inputs remain untouched:

```sh
python3 tools/compile_reference_art.py --verify-source
python3 tools/compile_reference_art.py --extract-to build/reference-reauthored
```

`--verify-source` compares every decompressed asset byte directly with its
original source crop and reports the actual decoder. `--extract-to` decodes
the source again and writes identical blobs plus the frozen manifest. A future
intentional asset change requires a reviewed source/crop/pixel manifest and an
explicit compiler-lock update; the tool has no automatic acceptance switch.

The [A11 execution note](development/2026-11-14-midi-ui/11-reference-assets.md)
records exact pixel comparison, repeat extraction, malformed-input rejection
and compiled C++ byte transport. This verifies asset integrity only. Native
composition, texture failure recovery and the final reference comparison still
require actual application execution and screenshots.
