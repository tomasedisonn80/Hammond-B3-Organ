# Assignment 11 - reproducible native glyph atlas

## Identity and owned result

- Actual assignment: `/root/w02_a11_font_atlas`, standalone wave 2, batch 2.
- Inspected baseline: `2e91750` on `main`; unrelated concurrent work preserved.
- Owned: `apps/standalone/FontData.h`, `tools/generate_standalone_font.py`,
  `assets/standalone/fonts/`, `docs/STANDALONE_FONTS.md`, and this report.
- Added source TTFs, complete font license, source/output manifests and an
  authoring requirement. No core, parameter, state, renderer or CMake changes.
- Integrator owns shared status, assignment ledger, commits and publication.

## Implemented contract

DejaVu Sans Book 2.37 at nominal 32 px and DejaVu Serif Book 2.37 at 40 px each
contain all 95 printable ASCII glyphs. The 512 x 256 atlases preserve grayscale
antialias coverage, two-pixel transparent gutters, baseline bearings and 1/64 px
advances. Dynamic labels compose glyphs at runtime; no complete words are baked.
Byte-pair count/value RLE occupies 28,168 and 36,894 bytes respectively.

The 204,816-byte generated C++20 header exposes `font_data::kSans`, `kSerif`,
`glyph` and checked `decode_alpha`; [the API](../../STANDALONE_FONTS.md) explains
scale, baseline and texture creation. Build/runtime require no Pillow, SDL_ttf,
FreeType or external font file. Unsupported bytes map to `?`; Unicode and
kerning remain outside the ASCII contract. API communicated to the integrator.

Source identity and complete terms are in the
[font source manifest](../../../assets/standalone/fonts/source-manifest.json).
The files were copied unchanged from the supplied local font directory; their
own name tables identify version 2.37. Package-manager identity was unavailable,
which is recorded rather than guessed. The font license comes from the full
`Files: *` section of the supplied copyright file. Its Debian packaging GPL
section is not mislabeled as the font license. Binary packaging must retain
`LICENSE-DejaVu.txt` alongside other notices.

## Executed verification

Working directory: repository root. Python 3.12.14; Pillow 13.0.0; FreeType
2.14.3; Pillow BASIC layout; GCC 14.2.0. Commands executed:

```sh
python3 tools/generate_standalone_font.py
python3 tools/generate_standalone_font.py --check
```

Generation and repeated in-memory regeneration passed with identical header
and manifest bytes. Every source-font/license hash was checked. All 190 glyph
rectangles passed bounds, baseline, advance, nonoverlap, transparent-gutter and
packed-mask equality checks. Both alpha streams decoded exactly to the original
rasterization and contained intermediate coverage values.

An ephemeral C++ probe compiled with `-std=c++20 -O2 -Wall -Wextra -Wpedantic
-Wconversion -Wsign-conversion -Wshadow -Werror -I apps/standalone`, then ran
successfully as `/tmp/hammond-font-atlas-check`. It decoded the actual generated
header, matched independently computed FNV-1a alpha hashes `de1d615a`/`61668e74`,
checked all glyph metrics/ASCII fallback, and rejected wrong destination size,
null streams, odd pairs, zero counts, overflow, short streams and zero extents.
The Python decoder independently rejected odd/zero/overflow/short streams.

Final header SHA-256:
`f1a3121a2707a03a3b2e025c399e68c553ce9498f4b002ec13b18f512e334802`.
Full alpha/RLE identities are in the
[output manifest](../../../assets/standalone/fonts/atlas-manifest.json).

## Remaining integration evidence

Renderer startup must check decoding/texture creation, use white RGB with
decoded alpha, and apply linear filtering and the documented baseline metrics.
Actual window/DPI legibility, label clipping, installed notices and device/UI
qualification require the subsequent renderer and packaging checks. This task
claims reproducible font assets and bounded decoding, not native UI acceptance.
