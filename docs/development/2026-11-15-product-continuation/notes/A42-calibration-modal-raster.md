# A42 — calibration modal raster acceptance

Actual worker `/root/w07_a42_calibration_modal_raster`, wave 7. Read active
instructions/checkpoint, M0–M9 plan, MIDI operating guide, visual contracts and
actual overlay/layout/focus source. Extended only the existing registered
`test_standalone_material_acceptance.cpp`; no production, CMake, asset or
timeout changes. Root exclusively built and executed the shared target.

The original **901 material + 170 header assertions** and thresholds remain.
Added **222 assertions / 21 paint frames** across minimum Dimensional,
minimum Flat, 1672×941 Dimensional with fractional modal origin, and offset
1.25× Flat. Independent literal anchors check all eleven targets, minimum
size, containment and separation. Ninety-six complete glyph-region comparisons
check calibration labels, selected values, active values and validation text.
Changes must remain in their allocated controls/rows. Eight focus checks cover
all three calibration controls; two invalid and two long-name/backend/status
cases preserve neighboring content. The caller clip cuts through controls,
text and focus. Application focus traversal remains the separate native CLI
gate; this fixture composes the actual public Drawing focus primitive.

Root's first run failed **1/1293** in **6.83 s**: universal full/cut pixel
identity was too strong for partially clipped font textures. The diagnostic
rerun preserved that assertion and identified **212 differing pixels**.
Pinned SDL 2.32.10 rounds clipped source/destination rectangles before scaling.
With root approval, the final oracle identifies only individual glyph
rectangles crossing the clip boundary. Both full and clipped pixels must
exactly match separate literal text plates there, including their exact
difference set. Complete glyphs, nontext, focus and outside-clip checks remain
exact; no numeric tolerance or whole-textbox exclusion was added.

Final root CTest passed **1293/1293**, **109 total paint frames**, in **6.63 s**.
All 212 differences belong to **38 intersected glyphs**; unexplained and literal
mismatches are both **zero**. Strict GCC syntax and `git diff --check` passed.
The existing 60-second timeout remains. Hosted sanitizer evidence is separate.

[Receipt](../reports/A42-calibration-modal-raster.json) retains commands,
source/executable/font/SDL identities, all three attempts and detailed glyph
rectangles. The [initial-source patch](../reports/A42-first-failure.patch) was
reconstructed by reversing diagnostics and verified against its original hash.
Final fixture SHA-256: `439d50f5990025fa09350283cb63f0bbb15ce0a526c561e742b6f5365b91a9c8`.
Painter `3687f96d…` and application `7ded143b…` remain unchanged.

Software raster acceptance does not establish physical display/MIDI/audio,
contrast-standard compliance, semantic accessibility or literal 1:1 fidelity.
