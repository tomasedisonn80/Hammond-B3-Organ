# Reference apron asset/compiler admission — A22

16 November 2026. **Admitted for the exact source, mask and offline compiler
scope; no required correction found.** This review qualifies A15's frozen bytes
under the [contract](../design/REFERENCE_APRON_CONTRACT.md), SHA-256
`c07c08895d8f985a95c34630ddc19c51ed1a3d3771cac4918a614de90bc879d0`.
Base HEAD is `54df95fe343d417dd89bb7a91f85e4f51c08dfe7`; the working tree contains
other workers' changes. Production, assets and frozen native fixtures were untouched.

## Independent source and byte admission

A separate 7,043-byte verifier imported no compiler code. It opened the original
JPEG directly with Pillow, called `load()` and `convert("RGB")`, checked the
complete decoded image identity, and compared all **88,560 texels** using Pillow
pixel access at `(x+16,y+887)`. All **32,544** texels outside crop-local
`[32,1588) × [2,38)` have exact source RGB and alpha 255; all **56,016** inside
have four zero bytes. There was no transpose, resampling, ICC transform or
retouching. Dimensions are 1640×54, pitch 6560, top-down RGBA8.

| Identity | Bytes | SHA-256 |
| --- | ---: | --- |
| Original JPEG | 412,664 | `9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187` |
| Full decoded RGB | 4,720,056 | `07a7e35a2fd6610d623bbc1da8c995f3f4d95c4b45a0a5c1f41ad1395584bbeb` |
| Apron manifest | 2,416 | `41a8a503a8cef8c1df102599de83f6c2a3cf86c23cb2fbc8eedb18a6e52670d8` |
| Packed apron | 61,162 | `87387e6c0bbd54012f0e0b23560175781a6515483b047822e4b64e4adfaac06c` |
| Raw RGBA | 354,240 | `2646c6fe3fd813ae2907fb04dafacf504309247656860b7161d12ff2f85ded13` |
| Generated header | 2,215,140 | `06ab67289452e17b2254093b12f05f2b5e234323abfa1098e635abf8cf298091` |
| Apron compiler | 14,273 | `13d8fbbeafb482332d7be4909ad8e2338632bd98797813233c84289ca3b57aac` |
| Author tests | 17,377 | `d9051556d3dc64c473f0cd489825dd95c66b0a696efe21f2693d02115dded14c` |

Independent level-9 gzip regeneration exactly reproduces the packed stream:
one complete member, mtime zero, empty filename, OS byte 255. Observed authoring
versions exactly match the manifest: Python 3.12.14, Pillow 13.0.0, libjpeg API
6.2, libjpeg-turbo 3.2.0, compile/runtime zlib 1.3.2. Optional requirements pin
Pillow; extraction additionally enforces the full toolchain and packed-byte pins.
Source verification enforces complete decoded RGB/pixel identity and reports
its actual versions.

## Compiler audit and execution

Manifest/source/packed reads are bounded to 16/512/128 KiB respectively. Frozen
manifest, source and packed identities precede decompression; raw identity
precedes header generation. `zlib.decompressobj` limits expansion to 354,241
bytes and requires exactly 354,240, valid EOF/CRC/size, and empty unconsumed and
unused tails. Truncation, excess output, extra members and trailing data fail.
The header has a 3 MiB bound.

Output preflight protects manifest, source, packed input and compiler: normalized
paths, symlink parents and hard links are checked; output symlinks/directories
are refused. Both extraction destinations and their mutual aliases are checked
before either write. Header replacement closes a same-directory temporary file
before `os.replace`, cleans it on failure, and preserves equal bytes/timestamps.
The author suite exercises refusal preservation and injected replacement failure.

From `/workspace/scratch/3edffb787db3/Hammond-B3-Organ`, the exact commands were:

```sh
TMPDIR=/workspace/scratch/3edffb787db3/a22-apron/tmp python3 -B -m unittest discover -s tests -p test_reference_apron_art.py -v > ../a22-apron/author-suite.log 2>&1
python3 -B ../a22-apron/verify.py > ../a22-apron/independent-verification.log 2>&1
```

The author suite passed **25/25 in 3.269 s**, without skips, on its sole run.
The independent command passed and records four successful compiler subprocesses
with `-B -S`: verify-only, two separate header outputs, and repeat of the first.
Every parsed header byte matches the admitted RGBA stream; both outputs match,
and repetition preserves the deliberately fixed timestamp. CMake's inspected
custom command uses the ordinary `--output` path; Pillow is imported only in
explicit author modes. No configure, native build or duplicate corruption sweep ran.

## Preserved provenance and historical resources

Direct byte comparison against the base commit confirms the JPEG, original
`atlas-reference.json`, every file under `assets/standalone/reference/`, old
compiler and `ReferenceArt` enum unchanged. Historical packed hashes remain:

| Resource | SHA-256 |
| --- | --- |
| Cabinet | `4011a2d6be00dc491303dbd0e7c03ebb187ec2d7f288bc9a79ea47dc2e486c3e` |
| Left cheek | `1aa1e326b10e6dc6e02bfeb8229ade9842e6073cc75730dd260ced49d8225bc4` |
| Right cheek | `53f2e03f2cb9858a7d4f9c9c8198188d16d5f32376a521f00eeb067c049ef1f6` |

The independently hashed 21,248,265-byte PDF remains
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
The source remains the user-supplied generated design concept, with its existing
upstream publication-rights gate open. This review does not re-extract the PDF
image object or independently clear rights.

Scratch evidence in `../a22-apron/`: `verify.py` SHA-256
`8b58fbe1e0b1f0b2b44d971f811af38c28b9c497900648428007565719d4ae62`;
`independent-verification.json`
`18ef68b7a3bab6f5f6d2289a5dd34ecc3c881124243f84eb59aeaa2570bd0e86`;
`author-suite.log`
`40627e2a74f5c4353572e08dcffd652b06f9bccb9c2793685bf74acda54c9848`.
The JSON retains exact subprocess arguments, input identities and historical
comparison results; root can archive these small original records.

## Remaining limits

Header atomic visibility is supported; crash durability and adversarial concurrent
path mutation were not tested. Extraction performs two individually atomic
replacements, without promising a two-file transaction. Native texture, paired
raster, fallback and gallery admission belong to their separate owners; real
display/DPI/input/accessibility, whole-interface 1:1 and physical fidelity remain
separate gates. No uncovered defect warranted a new repository test.
