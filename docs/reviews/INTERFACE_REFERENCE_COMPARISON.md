# Original reference versus actual native interface

**A32 result: literal 1:1 reference fidelity is not met.** The native instrument
recognizably follows the walnut, charcoal, brass, ivory-tablet and adjacent-rack
composition, but its header alignment, panel proportions, keyboard depth and
surface lighting visibly differ. Correct live controls are necessary; they do
not turn those differences into a visual pass. This is an independent comparison
under the [explicit scope](../INTERFACE_CONTINUATION_SCOPE.md), not a revised target.

## Compared evidence and limits

Inspected the unchanged [1672×941 original JPEG](../design/atlas-cover-reference.jpg)
and **all eight actual native gallery PNGs**, especially
[reference-size Play](../../examples/demos/standalone-interface-preview-v1/images/play-reference-1672x941.png),
[minimum Service](../../examples/demos/standalone-interface-preview-v1/images/service-minimum-960x700.png)
and [minimum Flat](../../examples/demos/standalone-interface-preview-v1/images/flat-minimum-960x700.png).
The [compact record](../development/2026-11-14-interface-continuation/reports/a32-reference-comparison.json)
retains exact hashes for the original and every inspected PNG, diagnostic checks,
source identities and coordinate methods. All eight PNG file hashes, decoded
pixel hashes and diagnostic hashes match the retained capture provenance.

These are the A22 gallery's **pre-A28 A20-renderer captures**, from executable
`005db1e2006bd1929e07dff3acaa40a5a6e6fa60a2bc8f07eb992d972b04b364`,
using SDL dummy audio/video and software rendering. Published HEAD `5d81199`
alone does not identify that overlay. This review neither rebuilds it nor
qualifies the current binary. A28's clip repair and subsequent A31/A34 changes
need new source-qualified captures. No similarity score is invented.

## Visual findings

At the reference size, the native inner left edge, x≈71.896, follows the source's
x≈70 boundary well. The source's broadly centered title is displaced right in
the application: its allocation center is x869 against the window midpoint x836.
Live Save/Load/Help, Audio/MIDI/Panic and Flat account for a different header
composition from the concept's preset selector; their functionality must remain.

The current shallow brass borders, grain, screws and cap highlights improve
separation, but the center panels still look more uniform than the original's
wide bevels, shadowed recesses and directional sheen. The manuals have genuine
sloping silhouettes and distinct fronts. Their native key extent is only
108.48 units high, with a 15.187-unit natural front, against the original upper
key region's approximately 144 pixels. This remains a conspicuous depth and
row-height difference. The [geometry contract](../INTERFACE_GEOMETRY_CONTRACT.md)
explicitly preserved panel allocation; material tuning alone cannot close it.

The native drawbars correctly retain **16′, 5⅓′, 8′, 4′, 2⅔′, 2′, 1⅗′, 1⅓′, 1′**
with **brown/brown/ivory/ivory/black/ivory/black/black/ivory** caps and live 0–8
values. Two complete 61-key manuals, 24 reversed presets and 25 pedals remain
visible. The concept's erroneous legends, colors and shorter playing inventory
must not replace these [verified contracts](../INTERFACE_WORKSPACE_CONTRACT.md).
Likewise, the verified percussion choices, expression and nominal pedal mixtures
cannot become decorative vibrato tablets with no connected sound path.

The cabinet uses actual source decoration, yet its frame starts around x1141.642
and its art at y154, versus source landmarks near x1125/y174. Below it, truthful
device/model information replaces microphone and speed controls. Rotary explicitly
labels the art decorative and the audio disconnected; Service retains unavailable
V/rpm and unacquired microphone geometry. These are required
[inspection truths](../INTERFACE_INSPECTION_CONTRACT.md), not aesthetic defects.

At 960×700 and 1280×900, Play appropriately hides the cabinet and expands the
player column. All six minimum Service cards remain visibly contained, though
their small text is dense. Minimum Flat clearly removes perspective and ornamental
depth while retaining controls. Neither Service nor Flat has an exact counterpart
in the supplied Play concept, so their usability cannot establish its 1:1 match.

Cyan focus is distinct from ivory selection; amber held keys and the `UNSAVED`
footer are visible. Diagnostics associate these frames with Upper 60/64, Lower
67 and pedal 3, after the real retained-drawbar edit. **Every frame is acknowledged,
with `controls_pending=false`**; pending-versus-applied appearance is not visually
qualified by this gallery.

## Prioritized residuals

Coordinates are original image pixels or native logical units, as identified;
reference landmarks are approximate visual observations.

| Priority / owner | Concrete residual | Bounded correction and acceptance |
| --- | --- | --- |
| P1 / A34 | Minimum Upper D# label `[59,443.240002,10,11]` shrinks to **6.153846** units; its ink envelope is only 9.038464×4.423065. Both minimum modes show the problem. | Use legible cap text or a visible preset legend; stacked letter/# is a candidate. Preserve all 24 IDs, hit ownership and semantic footer. Inspect minimum and 1400×820 in both modes. [A27 measurements](INTERFACE_RESPONSIVE_AUDIT.md). |
| P1 / A31 | A28 separately found missing rows at 150% in dimensional gradients/rounded surfaces. The 1× gallery cannot certify that repair. | Close the surface-coverage defect and inspect the new full-view raster evidence. [A28 finding](INTERFACE_SCALE_TEXT_AUDIT.md). |
| P2 / A34 if assigned | Reference-size title is approximately **33 pixels right** of the intended center. | Center on the window midpoint while preserving existing fit/clamp and all ten header actions; verify minimum/reference text clearance. |
| P2 / later visual gate | Native racks occupy y230.92–456.76 versus source ≈270–510; upper keys y526.76–635.24 versus ≈548–692. Materials remain simpler. | Review panel allocation and continuous bevel/front/track lighting separately, retaining complete inventory and shared input geometry. |

This slice can close the preset-label and fractional-surface defects, and the
bounded title offset if assigned. Follow with a current identified gallery and
an explicit pending/applied fixture. Larger composition/material differences
remain open until an independent comparison actually closes them; no physical
display, accessibility, timing or instrument-fidelity claim follows here.
