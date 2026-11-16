# Reference apron v1

This independent decorative package implements the exact crop and mask in
[the admitted contract](../../../docs/design/REFERENCE_APRON_CONTRACT.md).
It does not change the historical three-image reference package. Its source is
the unchanged embedded JPEG object 3 on atlas pages 1 and 409. The artwork is a
user-supplied generated design concept, not an application capture or measured
physical geometry. Existing upstream publication-rights clearance remains open;
no external artwork is acquired by this package.

The source rectangle `(16, 887, 1640, 54)` becomes top-down RGBA8 with pitch 6560.
Within the half-open crop-local hole `(32, 2, 1556, 36)`, all four bytes are zero.
The remaining 32,544 texels preserve the original RGB and use alpha 255. The hole
contains 56,016 zero texels, including hidden RGB; no baked lettering is retained
there. The raw stream is exactly 354,240 bytes. The manifest pins the complete
source and decoded RGB hashes, crop/mask, compressor/decoder versions and rights.

| Data | Bytes | SHA-256 |
| --- | ---: | --- |
| `apron.rgba.gz` | 61,162 | `87387e6c0bbd54012f0e0b23560175781a6515483b047822e4b64e4adfaac06c` |
| Decoded RGBA8 | 354,240 | `2646c6fe3fd813ae2907fb04dafacf504309247656860b7161d12ff2f85ded13` |
| `manifest.json` | 2,416 | `41a8a503a8cef8c1df102599de83f6c2a3cf86c23cb2fbc8eedb18a6e52670d8` |

## Ordinary build

From the repository root, Python's standard library is sufficient:

```sh
python3 -B tools/compile_reference_apron.py --verify-only
python3 -B tools/compile_reference_apron.py --output /tmp/ReferenceApronData.h
```

The generated header exposes `hammond::standalone::reference_apron::RgbaImage`
with `width`, `height`, `pitch`, `pixels`, and `byte_count`, plus `kApron`,
`kApronPixels` and `kTotalPixelBytes`. Runtime upload uses RGBA32, straight-alpha
blending and nearest sampling under the separate Drawing contract. The header
contains the pixels; runtime requires no asset files or JPEG decoder.

Compilation checks frozen manifest/source/packed/raw identities, bounded one-member
gzip decoding and output aliases before atomic replacement. Equal output bytes
leave the existing header and timestamp unchanged. A new file needs its own
independent source/mask review and identity freeze; editing the manifest alone
cannot admit a replacement asset.

## Explicit authoring and source verification

Install `requirements-authoring.txt` only for these optional commands:

```sh
python3 -B tools/compile_reference_apron.py --verify-source
python3 -B tools/compile_reference_apron.py --extract-to /tmp/reference-apron-reverified
```

Both require the full decoded source RGB hash before cropping. Verification
reports the actual decoder versions and requires exact pixels; extraction also
requires every authoring version to match the frozen manifest and the canonical
gzip bytes to match exactly. Original authoring used Python 3.12.14, Pillow
13.0.0 (HPND), libjpeg API 6.2 / libjpeg-turbo 3.2.0 (IJG/BSD-3-Clause/zlib), and
zlib 1.3.2 (zlib license). These optional tools are not bundled runtime dependencies.
The gzip uses level 9, mtime 0, empty filename, OS byte 255 and one member.

These commands qualify asset bytes and authoring reproducibility. They do not
establish native raster behavior, whole-interface equality or rights clearance.
