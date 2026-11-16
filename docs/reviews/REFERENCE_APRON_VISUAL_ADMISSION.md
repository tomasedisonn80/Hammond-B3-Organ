# Reference apron visual admission — A32

16 November 2026; actual worker `/root/w06_a32`, wave 6.
**Admitted for the narrow apron visual scope: no new visual blocker observed
in the three required active sizes. Literal whole-interface 1:1 remains unmet.**
Authority: [apron contract](../design/REFERENCE_APRON_CONTRACT.md).

## Observed images and identities

I independently opened the unchanged concept, two genuine baseline PNGs and
three candidate PNGs with the image viewer. Candidate inspection began only
after A31's `CAPTURE_FROZEN` notification. These are actual application
**dummy-SDL software captures**, using dummy video/audio and the software renderer;
the source JPEG is generated concept art, not a screenshot or physical measurement.
No image was edited, composited or recaptured for this review.

The table binds every visual observation below to the exact file bytes.
Candidate images reside in [the frozen gallery](../design/native-gallery-preset-v1/provenance.json).
B1/B2 remain in `../baseline-gallery-v3/images/` relative to the repository root;
their [genuine capture receipt](../development/2026-11-16-preset-library-continuation/reports/baseline-gallery.json)
identifies the original executable and provenance.

| ID | Image | SHA-256 |
| --- | --- | --- |
| S | [Concept, 1672×941](../design/atlas-cover-reference.jpg) | `9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187` |
| B1 | Baseline `play-reference-1672x941.png` | `07000dd0d97478a014c92e140b6666140eef3df33d7adf6f05b3d01e6cb21400` |
| B2 | Baseline `play-minimum-active-1400x820.png` | `99627ffeec4a37fc3aecb36a165dbbc3c25eead4af6f51089efc4f74c0b90f26` |
| C1 | [Reference, 1672×941](../design/native-gallery-preset-v1/images/play-reference-1672x941.png) | `6ac89798b41026533b474bbd523424134873af903a7bd1f9a58d09a583e0923a` |
| C2 | [Minimum active, 1400×820](../design/native-gallery-preset-v1/images/play-minimum-active-1400x820.png) | `e5a8426c5b5065b137303671044d4452f73305c31a4a190736189d5f44111c02` |
| C3 | [Wide, 1920×1080](../design/native-gallery-preset-v1/images/play-wide-1920x1080.png) | `b49e71a5b2b23f69c984b33fd1c11d3f7b7cfcc2b6d83020106cba11745ff621` |

Independent hashing confirms the gallery manifest
`a403767e0863f7aacf4c900ef24e289b582b2e5d0c108b97ecd64cb7fe18115b`
and provenance
`de60b735f3c91dadddaf461bb78d6dd3ad060a922c8e475b1499cdee189d3d2c`.
All three candidate PNG hashes match the manifest; their dimensions and decoded
RGBA hashes match the recorded cases. The actual 4,094,520-byte
application matches before/after identity
`82c6a9ffa056852b80d5505dec19aaec72f83965953d765bbee388cc8b1293c8`.

The unchanged source inventory is
`7d6671ecd79e7f44e0727a7f4399721358b9345f3b00bce9d4af4fa72ad4e810`;
HEAD `54df95fe343d417dd89bb7a91f85e4f51c08dfe7` alone does not identify this
working overlay. Directly hashed `Drawing.cpp`, `Drawing.h` and
`InstrumentView.cpp` match the gallery and the
[independent raster admission](REFERENCE_APRON_RASTER_ADMISSION.md).
The actual JPEG, apron manifest and packed asset also match gallery metadata.
The state file remains
`2490eee50d77e8b23324eaf7d67d1ca65c4670c000e33023fcac6f97d23da558`;
its shared Play replay and source/build/executable before/after identities are
unchanged. All three cases record running audio, current snapshots, no overlay,
two Upper notes, one Lower note and one pedal held. Runtime counters differ;
these gallery frames are not deterministic paired fixtures.

## Visual findings

- **Grain and joins, C1–C3:** irregular dark source grain now appears below and
  beside the footer, replacing B1/B2's regular procedural striping. The thin
  highlighted upper edge remains aligned across the apron. No visible tiling,
  inversion, new tear, exposed hole or protruding halo appears. The straight
  join and dark gap above it remain visible parts of the unchanged surround.
- **Footer, C1–C3:** the opaque black live band keeps status, contextual text,
  `UNSAVED` and the meter distinct from the wood. No grain or source lettering
  crosses the text. C2's two lines are very small but remain distinguishable;
  I observed no new clipping or overlap relative to B2. This does not establish
  comfortable reading on a real display or at another DPI.
- **Baked label, C1–C3:** neither `DESIGN CONCEPT` nor its central ornament is
  visible. This is the intended masked-source treatment, not an assertion that
  the complete source apron has been reproduced.
- **Surround, C1/B1 and C2/B2:** cabinet, cheeks, panels, manuals, presets,
  drawbars and their visible active cues retain their arrangement and appearance.
  This visual judgment adds no whole-frame byte-equality claim. A23's separate
  frozen 25-case receipt supplies exact containment/footer/source-pixel evidence;
  I did not rerun that raster execution.

## Concrete whole-reference differences still open

Comparison of S with C1–C3 retains these visible differences:

1. The top-right preset selector and gear are replaced by application actions;
   the subtitle reads `NOMINAL DRY ORGAN`.
2. Expression and pedal mixtures occupy the concept's vibrato/chorus area.
   Percussion labels and active states also differ.
3. Drawbar tracks, cap bevels, panel texture and shadows remain harder and
   flatter; the live numeric values, focus outline and cap positions differ
   from the illustrated registration.
4. Manuals have denser key spacing and different key-front/perspective shading.
   Reversed preset keyboards, bank buttons and sounding-state labels replace
   the concept's three large selector buttons at each left cheek.
5. Below the cabinet, keyboard routing, runtime notices and the pedalboard
   replace microphone knobs and rotary-speed buttons. The imported cabinet
   image does not make those surrounding regions equal.
6. The live footer interrupts the wood, and the straight lower join/dark gap
   differs from the concept's sculpted lower chassis. Minimum-active top action
   and footer labels have compressed, very small strokes; label spacing and
   illumination across the interface also remain different.

These require separately admitted work that preserves truthful live controls.
Real display/DPI/input, native accessibility, upstream artwork rights and
physical fidelity retain their separate gates. Root owns README integration;
this review changes no production code, navigation or acceptance thresholds.
