# Final independent visual acceptance

**A51 result: partial visual acceptance; literal 1:1 reference equality remains
unmet.** The final gallery visibly contains the repaired title and accidental
legends, complete musical inventory, distinct held/focus treatment and usable
recorded workspace layouts. It supports the README's current visual account,
with the remaining differences and evidence limits below.

## Evidence inspected

Directly viewed the unchanged [1672×941 original concept](../design/atlas-cover-reference.jpg)
and **all eight full v2 PNGs**: reference/default/minimum Play, reference/minimum
Service and Rotary, and minimum Flat. Independent Python/Pillow reads matched
every PNG's file hash, dimensions and decoded pixels, and every diagnostic hash,
to retained provenance. Nine inspected rendering/model/font/constant files match
both capture commit `8673713a484c40e26ac7810c7c4cbc22fa874426` and review HEAD
`cdbb2beaa28bf136f9a8db6213819129514e2ae9`.

The [compact record](../development/2026-11-14-interface-continuation/reports/a51-final-visual-acceptance.json)
retains exact identities, source-derived measurements and per-image observations.
These are saved frames from executable `bd4991a3…dc2`, using dummy SDL audio/video
and software rendering, with logical and drawable dimensions equal. A51 made no
new native launch, capture or build. The broader source/build basis remains in
[A46](INTERFACE_FINAL_GALLERY.md); A49 owns the coherent suite gate.

## Inventory, state and repairs

The four Play/Flat frames retain **61+61 manual keys, 25 pedals and 24 reversed
preset keys**. Each preset octave contains C Cancel, nine fixed choices C#–A,
A# selecting bank A and B selecting bank B. Correct footage, cap colors, nine
visible drawbars per rack, percussion choices, expression and pedal mixtures
remain authoritative over the concept's inaccurate or incomplete controls.

Cyan focus surrounds the Upper B 16-foot drawbar; amber fills/marks distinguish
held keys. Rack captions separate edited bank B from sounding Upper fixed C#
and Lower A#. Saved diagnostics independently retain Upper notes 60/64, Lower 67
and pedal 3, with the live retained-bank edit 7→8, complete desired/applied
agreement and final acknowledgment. All eight final frames have
`controls_pending=false`; **they do not visually qualify a pending selection**.

The title's font-advance center is now x836/640/480 at reference/default/minimum
sizes. Both characters of each accidental appear on separate lines; matching
source specifies nine-unit glyphs in a 20-unit-high label. Minimum D# retains
a ten-unit label width. These repairs are present in current full frames,
consistent with [A34](INTERFACE_PRESET_READABILITY.md), while compact text still
needs physical-display review.

## Concrete remaining differences

Native values below are freshly derived from matching source formulas; concept
landmarks are approximate direct visual readings, not segmented measurements.

| Area | Native versus original |
|---|---|
| Manual depth | Reference upper keys occupy y526.76–635.24: **108.48 units**, against concept ≈548–692, or ≈144 pixels. Default depth is 108; minimum is 52. The shallower rows remain conspicuous. |
| Rack allocation | Native y230.92–456.76 versus concept ≈270–510. The live control row, computer-key toolbar and pedalboard change vertical balance. |
| Cabinet composition | Native panel x1141.642 and art y154 versus concept ≈1125/174. Device/model status replaces conceptual microphone and speed controls; Play hides this column below width 1400. |
| Materials | Charcoal panels are smoother, rims thinner, shadows more uniform and cap lighting less layered than the concept. Walnut decoration does not supply that depth to the live controls. |

Header tools, smaller complete preset octaves and the nominal-output subtitle
also change the composition. Those differences need deliberate design work
without deleting correct controls or presenting unconnected models as active.
No similarity score is assigned.

## Minimum fit, inspector and README

Minimum Play moves Edit A/B into the racks without losing presets. Minimum Flat
keeps the same inventory, notes and focus on rectangular keys/plain panels.
Service visibly fits six cards and 28 rows; its bank memories wrap inside
Retained controls. Unavailable V/rpm and unacquired m remain explicit. Rotary
fits six read-only rows and labels its artwork decorative. No musical-control,
card/header or footer collision was observed in these eight images.

One **low-priority copy defect** is visible in both Service images: Contacts /
routing shows “1 targets” for Lower held and Pedals held. `InspectionModel.cpp`
lines 297–300 supplies constant unit `targets`; `InstrumentView.cpp`
`inspection_value` appends it. Quantities and evidence meaning remain clear.

The [README native UI/UX section](../../README.md#native-interface-and-uiux-design)
accurately uses current v2 captures, records dummy-renderer/source limits,
describes the repairs and preserves the unmet 1:1 gate. Its pending-state feature
description has separate raster evidence; the final gallery alone does not
demonstrate that state. Service/Flat have no exact counterpart in the single
Play concept. No display/DPI, pointer, screen-reader, physical audio, timing or
whole-model qualification follows.

## Ranked bounded follow-ups

1. Qualify compact text at 960×700 and 1400×820 on an actual display in both
   modes; include independently applied, focused and genuinely pending preset
   states with matching desired/applied diagnostics.
2. Review manual/rack/cabinet allocation against the stated landmarks, retaining
   every control and key. Recheck shared geometry at all sizes and breakpoints.
3. Refine one live panel/rack's texture, rim and shadow treatment at a time;
   preserve held/focus contrast and Flat clarity in identified captures.
4. Correct singular held-count wording while preserving counts and observation
   semantics. No product edit belongs in this review.
