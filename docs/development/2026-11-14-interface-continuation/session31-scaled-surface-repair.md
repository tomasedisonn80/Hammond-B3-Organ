# A31 — fractional-scale filled surfaces

Actual assignment `/root/w06_a31_scaled_surface_repair`, wave 6. Read the standing
instructions, complete plan, current scope/checkpoint, three interface contracts,
atlas interface material/scale pages and A28's actual failed images/audit. Root
released the frozen source only after pinning its initial coherent UI checkpoint.
A31 changed only `Drawing.cpp` and the existing native drawing regression; no
header, CMake, InstrumentView, model, audio or asset edit and no staging/commit.

The [review](../../reviews/INTERFACE_SCALED_SURFACE_REPAIR.md) and
[structured result](reports/a31-scaled-surface-repair.json) retain commands,
source/build identities, first failures, proof hashes and limits. Logical-height
strips were truncated by SDL software at 1.5×: the independent original probe
missed 252/756 opaque interior pixels for both gradient and rounded fills. The
repair samples clipped physical pixel centers through the existing raster
helper, preserving scale/physical viewport/clip and integer-aligned scale-one
gradient colors. The new oracle also found one-pixel spans dropped by SDL's
blended coincident-endpoint line; those spans now use an explicit point. The
first rebuilt 4/5 gate and its 48 thin-span failures remain preserved.

Final Drawing SHA-256:
`9b788234405964f6675ab43428735e425b460c8045f2c6eb064c9e19b40a0a5f`.
Final app SHA-256:
`968938196bcf291270e1b1e32e36f08535281a959fb47ea731a216c56486d270`.
All 17 relevant source hashes stayed unchanged through the final strict Release
build and **5/5 affected suites, 40.70 seconds**. New coverage includes 298
whole-target checks/18,309,120 pixels, independent circle masks, alpha single
coverage, literal gradient stops, six transforms, physical clips and bounded
invalid/huge cases. Existing glyph, quad, 150-frame workspace, 168-frame scaled
view and preset gates pass. The original probe now misses zero pixels at
1×/1.5×/2×.

Opened and inspected the final injected native
[Play](reports/a31-injected-renderer-play-960x700-at-1p5.png) and
[Service](reports/a31-injected-renderer-service-960x700-at-1p5.png) PNGs. Horizontal
surface gaps are absent; the same 28,500-pixel Service patch contains zero clear
pixels versus A28's 9,500. Lossless proofs total 590,550 bytes and retain original
BMP/decoded/PNG hashes; redundant A31 BMPs were removed. These are actual
`paint_instrument` software frames with injected state, not application or
physical-device screenshots. The original A28 failing images remain.

Build-native/CPU were released to root and A35. Root owns application-gallery
refresh, shared status and publication. A34's tiny preset labels, native display
and GPU/DPI behavior, screen-reader access, physical devices, timing and literal
atlas/physical sound fidelity remain separate gates. No broad performance or
fidelity claim follows from this surface repair.
