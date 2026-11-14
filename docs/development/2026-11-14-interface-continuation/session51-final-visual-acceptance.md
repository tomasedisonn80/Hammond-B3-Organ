# A51 — independent final visual acceptance

Actual assignment **51/60**, logical wave **9**, worker
`/root/w09_a51_final_visual_comparison`, 14 November 2026.

## Outcome

The [independent review](../../reviews/INTERFACE_FINAL_VISUAL_ACCEPTANCE.md)
accepts the final gallery **partially**: current repaired native rendering,
complete control inventory and recorded minimum-size fit are visible, while
**literal 1:1 reference equality remains unmet**. Directly viewed the unchanged
original JPEG and all eight actual v2 full PNGs with `view_image`. No predecessor
conclusion substituted for inspecting a frame.

The centered title and stacked accidental legends are present. The most material
remaining differences are manual depth, row allocation, panel light/texture and
cabinet/header composition. Fresh source arithmetic gives reference manual key
depth 108.48, default 108 and minimum 52 logical units, versus approximately
144 pixels for the original upper key region. The comparison preserves correct
61+61 keys, 25 pedals and 24 presets, and supplies ranked bounded follow-ups.

Reported a minor visible copy issue to root: both Service images show
“1 targets” for Lower held and Pedals held, from the constant `targets` unit in
`InspectionModel.cpp` lines 297–300 and `inspection_value` in `InstrumentView.cpp`.
Root confirmed it should remain a low-priority follow-up during the coherent
gate. No product change was made.

## Source, actual checks and limits

Working directory: `/workspace/scratch/601951e27dc3/Hammond-B3-Organ`.
Read `AGENTS.md`, the full M0–M9 plan, current scope/checkpoint/status/next steps,
workspace/geometry/inspection contracts, atlas review, A32 comparison, A34
readability result and A46 final gallery. Inspected relevant layout, preset,
header, inspector, key-paint and font-metric source directly.

Review HEAD/tree:
`cdbb2beaa28bf136f9a8db6213819129514e2ae9` /
`b4d71c1f574ab17ba1a3f37b24667c1ff3f9c527`.
Capture HEAD/tree:
`8673713a484c40e26ac7810c7c4cbc22fa874426` /
`e11bd68d6051f663631579ef235325a8775f8133`.
Recorded capture executable SHA-256:
`bd4991a3b45543a01c9ce435da140af848d45f28ff535699397706e5d3925dc2`.
This is the capture's recorded binary, not an A51 build result.

Read-only Python/Pillow checks independently recomputed all eight PNG sizes,
file hashes, RGBA pixel hashes and native diagnostic hashes against provenance
and manifest. All matched. Nine inspected product files matched the gallery
map and `git show` blobs at both named commits. A50 separately owns full asset
tracing; A46's broader 98-file qualification is retained without reclassifying
this review as a new compilation or complete build attestation.

Every retained screenshot record equals its last-painted and pre-shutdown
presentation and identifies a current copied snapshot, requested view/size,
no overlay and no pending controls. Independently checked the complete explicit
desired/applied controls, held Upper 60/64, Lower 67 and pedal 3, pre-edit held
observation with Upper B 16-foot at 7, final edit to 8, acknowledgment, zero
application errors, event counts and later cleared shutdown. All checks passed.
All eight use dummy audio/video/software and 1:1 logical/drawable sizes. These
are saved-diagnostic checks, not another native execution or physical audio pass.

Font advances were read from matching `FontData.h`; layout arithmetic was
recomputed from matching `UiModel.cpp`/`InstrumentView.cpp`, rounded in the
report. Original image landmarks remain approximate visual observations.
No pending-state final PNG exists. No native display/DPI, persistent pointer,
screen-reader, hardware, callback-deadline or whole-model claim is made.

## Owned deliverables and handoff

- `docs/reviews/INTERFACE_FINAL_VISUAL_ACCEPTANCE.md`.
- This individual session note.
- [Compact JSON](reports/a51-final-visual-acceptance.json): original/eight-image
  names, hashes, dimensions, source identities, diagnostic checks, measurements,
  direct visual observations, minor defect and ranked acceptance criteria.

Used only read-only source/JSON/image inspection plus these owned documentation
writes. No build, CTest, application launch, new capture, generated image, asset
mutation, production/README/gallery edit, staging or commit occurred. A49 owns
the native full-suite gate; root owns shared documentation, integration and
publication. README's native visual section accurately describes the observed
v2 product and limits. Root should preserve explicit partial acceptance and
the unmet 1:1 result in the final handoff.
