# A32 — Independent native gallery acceptance

Actual worker: `/root/w06_a32_gallery_independent`, wave 6. Reviewed the current
scope, complete M0–M9 plan, layout/inspection contracts, atlas chapter 067,
unchanged exact reference and historical v2 provenance. The
[independent report](../reports/A32-gallery-independent.json) retains the results.

## Source and outcome

Accepted the eight retained **native application** views in
`examples/demos/standalone-interface-preview-v3` from published product commit
`2e161dc3a60fc3442051799574feed37bffbfc5c`, tree
`17f8e4d698f903c37bff09deee196ea73e0da108`. The 3,856,304-byte executable is
SHA-256 `97ed35cbf618792155c15106862d8bc5f416b7cf6d073c9e37e94babdf8bc9a9`.
A31 completed capture before A32 changed the producer. Its captured producer
hash remains `17aafb70e87a2fd557317e04802e62a4d935d2f2b93bf65a2df0d688c5a16545`;
the strengthened validator is separately identified in the report.

**552 independent checks passed:** all 39 manifest payload files, eight PNG file
and decoded-pixel hashes, dimensions, diagnostics, exact replay commands and
inputs; 100 captured production files against current and committed bytes; all
111 qualification entries; 13 selected build inputs; executable and selected
configuration identities. Original PDF/JPEG ancestry, three exact decorative
crops and two font atlases also match their generated arrays and executable
bytes. Both historical galleries retain all 41 files unchanged. Capture
provenance, manifests, inputs and pixels were never edited.

## Focused repair and tests

The old validator accepted two explicitly synthetic, in-memory v2 mutations:
wrong painted Upper count and nonzero pointer attempts. Correct replay endpoint
holds did not prove the actual painted counts. `validate` now requires exact
integer Upper/Lower/Pedal counts **2/1/1**, false SDL/UI capture flags and four
integer zero capture counters. Boolean/numeric coercion and missing/extra facts
cannot silently pass.

From the repository root, `python3 -B tests/test_capture_standalone_interface.py
-v` passed **7 methods in 0.034 seconds**: eight retained native positives and
60 synthetic mutation subcases. Mutations change all three final painted copies
together while keeping endpoint holds valid, so the existing equality guard
cannot mask missing checks. No prior producer unit test existed; the new file
uses the existing CMake Python glob. No GUI, native process, build or CTest was
run by A32. The separate read-only audit used Python 3.12, Pillow 13 and PyMuPDF.

## Direct visual review

Viewed the exact 1672×941 reference JPEG and all eight original PNGs without
alteration:

| View | Observation |
|---|---|
| Play reference | Deeper full manuals, separate cabinet/sidebar pedals, visible focus and 2/1/1 held highlights; no observed overlap. |
| Play default | Full controls, preset rails and bottom pedals fit the compact composition. |
| Play minimum | Rack Edit controls, manuals and footer fit; preset legends remain very small. |
| Service reference | Six cards; visible **2 targets / 1 target / 1 target** and distinct sound/edit states. |
| Service minimum | Cards, wrapped bank memories and captions fit; evidence text remains small. |
| Rotary reference | Decorative cabinet and six honest read-only facts remain separate. |
| Rotary minimum | Cabinet aspect, wrapped caption, all facts and footer remain visible. |
| Flat minimum | Plain keys/caps retain values, focus and held highlights without observed clipping. |

**Literal 1:1 reference equality remains unmet.** Title/tool composition,
materials, lighting, bevels, complete musical inventory and truthful status
differ from the Play concept; no separate exact Service/Rotary reference exists.
Next visual work needs measured native comparisons and real display/DPI review.

These acknowledged application frames are separate from A18's real-Session
**rendering harness** pending captures. SDL dummy/software pixels do not qualify
physical devices, pointer capture, deadlines, accessibility, connected cabinet
audio or specimen fidelity. A32 checked retained identities, not an independent
hermetic rebuild. Original BMP bytes were removed after the producer's lossless
conversion; A32 independently checked the retained decoded PNG identities.
