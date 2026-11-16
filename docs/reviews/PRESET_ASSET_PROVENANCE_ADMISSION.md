# Preset asset and provenance admission — A41

16 November 2026; actual worker `/root/w07_a41`, wave 7. **Source bytes,
reproduction and evidence classifications are admitted within this review's
scope.** Two concrete metadata defects were corrected with root-assigned
ownership. Updated actual installation and hosted execution remain root's gates.
Recovery HEAD was `d281d4e3063f44b9eda6b5bc4ea44fc99a6c7f93`; publication was
not independently observed here.

## Exact derivative and reproduction

The [independent audit](../development/2026-11-16-preset-library-continuation/reports/a41-provenance-audit.json)
passes **32 bounded checks**, importing no compiler implementation. One direct
Pillow `load(); convert("RGB")` verification checked all 88,560 apron texels:
32,544 retain exact source RGB/alpha 255; all 56,016 hole texels contain four
zero bytes. Geometry remains 1640×54, pitch 6560, source `(16,887,1640,54)` and
local hole `(32,2,1556,36)`. No resampling, retouching or replacement art occurred.

| Role | Bytes | SHA-256 |
| --- | ---: | --- |
| Original JPEG | 412,664 | `9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187` |
| Apron manifest | 2,416 | `41a8a503a8cef8c1df102599de83f6c2a3cf86c23cb2fbc8eedb18a6e52670d8` |
| Packed apron | 61,162 | `87387e6c0bbd54012f0e0b23560175781a6515483b047822e4b64e4adfaac06c` |
| Raw RGBA | 354,240 | `2646c6fe3fd813ae2907fb04dafacf504309247656860b7161d12ff2f85ded13` |
| Compiler | 14,273 | `13d8fbbeafb482332d7be4909ad8e2338632bd98797813233c84289ca3b57aac` |
| Retained generated header | 2,215,140 | `06ab67289452e17b2254093b12f05f2b5e234323abfa1098e635abf8cf298091` |

The complete decoded JPEG RGB hash remains
`07a7e35a2fd6610d623bbc1da8c995f3f4d95c4b45a0a5c1f41ad1395584bbeb`.
The 21,248,265-byte PDF still hashes to
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
Bounded decompression admits exactly one complete gzip member; independent
in-memory level-9/mtime-zero compression reproduces its bytes. Every parsed
header literal equals the admitted RGBA stream. Observed Python/Pillow/JPEG/zlib
versions match the manifest. No asset or header was regenerated on disk.

Git-object comparison with session base `54df95f` confirms unchanged PDF/JPEG,
`atlas-reference.json`, all historical three-crop package files, old compiler
and `ReferenceArt` enum. PDF object 3/pages 1 and 409 ancestry is inherited from
that unchanged extraction record; this review did not re-extract the PDF.
The source remains a **user-supplied generated concept**, with no photograph,
hardware dimensions or measured material claim.

## Proposed recipe ancestry

The contract, literal JSON and generator retain separate roles. A16's statement
records independent contract transcription without consuming the JSON; source
inspection confirms explicit C++ snapshots and existing serialization/storage,
with `recipes.json` referenced only for path protection. A24's independent
[native admission](STARTER_REGISTRATION_ADMISSION.md) retains eight methods and
122 native invocations. A41 did not rerun or recast that execution as its own.

Fresh static checks match all twelve contract rows and overrides to literal JSON
and all 24 canonical payloads. Every payload still matches the initial generation
receipt; ordered basename/NUL/payload hashing remains
`8618b545b1c04bdf1370478259967125cb63b09a81bbb6748f6990788578de11`.
Contract/JSON/generator hashes remain `f6390633…`, `665e6098…`, `dd93af18…`, with
full values in the audit. Recipes are original **proposed-unmeasured software
settings** for the nominal dry Engine. Selecting existing fixed modes in rows
11–12 creates no factory, artist or measured-recipe attribution. Authorship
statements and independently retained acceptance support this ancestry; hashes
alone cannot prove author independence.

## Retained execution ancestry

The actual genuine-before raster executable still matches `8391cb06…` and its
recorded production inputs match base Git objects. Candidate/unavailable binaries
match the [25-case report](../development/2026-11-16-preset-library-continuation/reports/apron-paired-final.json).
The separate initial application binary and original baseline-gallery provenance
also match their receipts. Original failed build, Unicode-generator, fixture and
gallery logs remain present and individually hashed; later passes do not replace
them. No native raster comparison or capture was rerun.

All **61 gallery payloads and 13 passed capture records** match the frozen
[native gallery](../design/native-gallery-preset-v1/README.md), whose executable
remains `82c6a9ff…`. The original twelve views and appended 1920×1080 view remain
distinct from concept art. Original BMPs are unavailable after recorded lossless
conversion; no fresh BMP comparison is claimed. Source and canonical PNG were
visually inspected. Of 148 recorded source files, only the authorized apron README
license-label correction differs; original source/capture hashes remain intact.

## Corrected classification and installed provenance

The local pinned Pillow 13.0.0 package declares **MIT-CMU**, correcting the apron
README's HPND label. Primary source:
`pillow-13.0.0.dist-info/licenses/LICENSE`, 70,307 bytes, SHA-256
`dda12a98c1979cf3d94df1cff45d27a4cb3f04a60c76f76902ac54cac03ec0ce`;
the audit records its exact local path and package metadata. This changes no
license grant, frozen manifest or pixels. Optional Pillow/NumPy/JPEG/zlib work
stays in authoring/offline verification; no additional third-party package or
runtime decoder is imported into the deliverables.

The original installer embedded the apron but omitted its separate provenance.
The repair appends `reference-apron-manifest.json` and schema-1
`reference_apron`, preserving `reference_art`, configured-hash preflight and
fixed opt-in inventory: **17 files MIDI OFF / 21 ON**. Notices, installed guide
and workflow provenance/exact-payload maps now agree. Removing only A41's workflow
delta in memory exactly reproduces A37's frozen `63562572…` hash.

[Three existing private installer fixtures](../development/2026-11-16-preset-library-continuation/reports/a41-installer-private-fixtures.json)
pass in 3.602 seconds, including missing/empty/changed/nonregular metadata
refusal. Duplicate-key-aware YAML, 20 shell syntax blocks and 11 embedded Python
ASTs pass. Root owns actual reconfiguration, native installation and publication.
Upstream artwork rights, project-license selection, real devices/accessibility,
literal whole-interface 1:1 and physical fidelity remain open.
