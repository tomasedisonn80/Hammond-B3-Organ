# Final interface provenance review

Actual assignment **A50/60**, wave 9, `/root/w09_a50_provenance_assets`,
14 November 2026. Compared the working gallery with published
`cdbb2beaa28bf136f9a8db6213819129514e2ae9` and its product predecessor
`8673713a484c40e26ac7810c7c4cbc22fa874426`.

**Result: visual/source integrity verified, with one explicitly reconciled
report-reference discrepancy.** No source, asset, capture or historical report
was changed. The [machine audit](../development/2026-11-14-interface-continuation/reports/a50-provenance-audit.json)
retains exact hashes, compared paths, eight decoded image identities and limits.

## Source and asset ancestry

The original PDF remains 21,248,265 bytes, 500 pages, SHA-256
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
Pages 1 and 409 both reference image object 3. Reading its embedded JPEG stream
produced bytes identical to the retained 412,664-byte reference, SHA-256
`9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187`.
All **15** A12 `source_provenance`/`retained_assets` entries match their recorded
hashes, the session baseline and the published commit. This includes the PDF,
reference/source manifests, font inputs/notices and compressed artwork.

The [complete atlas review](../research/INTERFACE_ATLAS_REVIEW.md) retains six
disjoint readings covering pages 1–500 and their selected visual inspections.
A50 inspected that consolidation and its product-review records; this is not a
seventh independent full-PDF reading or verification of absent companion files.

The three [decorative crops](../../assets/standalone/reference/manifest.json)
match the source JPEG at their exact integer rectangles: cabinet
`(1132,174,466,397)`, left edge `(0,0,24,941)`, right edge
`(1604,0,68,941)`. Compressed hashes, expanded RGB hashes, decoded source crops
and generated C++ arrays agree. All three byte arrays occur in the exact gallery
executable. `CMakeLists.txt` generates the admitted header;
[`Drawing.cpp`](../../apps/standalone/Drawing.cpp) uploads its RGB24 textures;
[`InstrumentView.cpp`](../../apps/standalone/InstrumentView.cpp) uses the cabinet
in Play/Rotary and wood edges in dimensional presentation. These are decorative
pixels; copied live state supplies controls, text, focus and held indications.

Both DejaVu 2.37 inputs match their [source manifest](../../assets/standalone/fonts/source-manifest.json).
The generated header and both RLE/decoded-alpha hashes match the
[font manifest](../../assets/standalone/fonts/atlas-manifest.json); both RLE
arrays occur in the executable. Drawing selects Sans/Serif glyphs for dynamic
text. The complete retained font notice matches the header and both final
package inventories. Existing [notices](../../THIRD_PARTY_NOTICES.md) and
[source-rights record](../research/RIGHTS_AND_SOURCES.md) retain their stated
limits; this review supplies no new rights conclusion.

## Capture and build evidence boundaries

The executable remains 3,707,640 bytes, SHA-256
`bd4991a3b45543a01c9ce435da140af848d45f28ff535699397706e5d3925dc2`.
The scopes remain distinct:

| Evidence | Verified scope |
|---|---|
| Ten admitted source files | Required renderer/model/main/reference subset |
| 98 observed product files | Equal A44, capture snapshots and both named commits |
| 13 selected build files | Equal retained before/after maps; generated art header independently read |

These observations do not establish a complete compiler/dependency graph or
independent source-to-binary rebuild. Later CI, CTest-budget and documentary
changes are outside the captured product inventory.

At A50 inspection, both galleries retain valid **39-file** payload manifests.
All **41 v1 files**, including its manifest and README, equal published bytes;
all **41 v2 files** match A46's final inventory. Eight PNG file hashes, RGBA hashes and dimensions
match provenance. Each associated diagnostic agrees with its requested view,
image size, painted/pre-shutdown state and applied replay controls. Records
identify dummy audio/video, software rendering and no selected MIDI input.
Original BMPs were already removed after producer verification; A50 independently
checked retained PNGs, without repeating that original BMP comparison.

## Reconciled report-reference discrepancy

Of **45** targeted report-hash edges, **42** match directly. Three references
in A46 preflight, qualification and its gallery copy point to the same earlier
A44 result identity: 3,486 bytes / `738ac497…`. The published final file is
3,509 bytes / `33205597…`; A45 correctly pins the latter.

The [additive reconciliation](../development/2026-11-14-interface-continuation/reports/a50-a46-a44-edge-reconciliation.json)
reproduces the earlier hash exactly by renaming only `runtime_packages` to
`packages` and `build_install_drift_during_runtime` to `build_install_drift`.
Every value is identical under those mappings. The
[derived reconstruction](../development/2026-11-14-interface-continuation/reports/a50-reconstructed-a44-at-capture.json)
is explicitly reconstructed, not an independently archived original. Ordinary
JSON serialization changes alone do not explain the discrepancy. Its timing
and author are not inferred. Product, binary, guide and package semantics agree.

Root should add the [prepared gallery note](../development/2026-11-14-interface-continuation/reports/a50-gallery-addendum-proposal.md)
while preserving all original capture records and manifests. The targeted
**233 local document links** resolve. A41's original timeouts/local leak blocker,
A43's static-only scope, A44's guide-only refresh and A45's historical v1 scope
remain separate observations. No new native test, capture, literal reference
match, real-display acceptance or complete-build attestation is claimed.
