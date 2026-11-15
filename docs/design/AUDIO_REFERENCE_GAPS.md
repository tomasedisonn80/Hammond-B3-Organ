# Audio continuation: reference comparison and remaining UI gaps

**A29 independent review, 15 November 2026. The literal whole-interface 1:1
objective remains unmet and unwaived.** The current percussion change improves
a specific part of the wide Dimensional Play view. It does not close the larger
composition, material or functional-content differences below.

This review directly inspected the [original 1672×941 reference](atlas-cover-reference.jpg),
the [previous actual wide view](../../examples/demos/standalone-product-preview-v1/images/play-reference-1672x941.png),
all [eight current application frames](../../examples/demos/standalone-audio-preview-v1/README.md)
and the [three additional live percussion states](../../examples/demos/standalone-audio-preview-v1/percussion-states/README.md).
The [independent admission](../reviews/AUDIO_GALLERY_ADMISSION.md) and
[machine-readable review](../development/2026-11-15-audio-continuation/reports/A29-visual-review.json)
record identities, state checks and evidence limits. The reference is artwork;
the application figures are actual native captures. Neither is substituted for
the other.

## What improved, and what matches only in a limited sense

| Comparison | Demonstrated finding | Remaining limit |
| --- | --- | --- |
| Wide percussion grouping | The previous wide app used broad tablets with labels inside. The current app uses narrower, taller bodies, larger live values and exterior PERC / VOL / DECAY / HARM legends. Their horizontal grouping approaches the reference. | This is a visual improvement over the earlier app, not an exact body/face/material match to the concept. |
| Textual identity | TONEWHEEL ATLAS, Play / Rotary / Service and the four exterior percussion legends correspond to the reference's words. | Letterforms, size, spacing, embossing and positions differ. Matching words do not establish matching pixels. |
| Correct value domains | Current wide order is ON/OFF, NORM/SOFT, SLOW/FAST, 2ND/3RD, attached to PERC, VOL, DECAY, HARM respectively. Both values in each domain are visible across the added captures. | The reference's NORM under DECAY and FAST under HARM are concept errors. They must not become behavior or acceptance requirements. |
| Wood and cabinet art | The walnut cheeks and cabinet visibly carry the reference artwork; its source crops are recorded in the [art manifest](../../assets/standalone/reference/manifest.json). | Source-derived decorative pixels do not qualify panel layout, working controls or Leslie audio. |
| Capture identities and size | The original and current reference frames are both 1672×941; retained PNG and decoded-pixel hashes match their receipts. | Equal dimensions and functional inventory counts provide no whole-frame visual-equality result. No application panel is admitted here as pixel-identical to the reference. |

The changed branch is Play + Dimensional + width ≥1400 and height ≥820. The
frozen [percussion contract](../PERCUSSION_REFERENCE_CONTRACT.md) keeps the
performance panel, divider, expression, pedal mixtures, racks, keys and header
in place. The current [actual reference-size frame](../../examples/demos/standalone-audio-preview-v1/images/play-reference-1672x941.png)
therefore still has the surrounding differences that were present before this
bounded refinement.

## Vertical and face measurements

Coordinates below use the full, unscaled 1672×941 source images. Rectangles are
left/top inclusive and right/bottom exclusive. The approximate reference bezel
landmark is a visual reading of a shaded JPEG edge; it is not a hit rectangle.

| Quantity | Original reference | Current application | Interpretation |
| --- | --- | --- | --- |
| PERC outer/body top | Approximately y177, with about ±2 px visual edge uncertainty | Contracted y150; native focused cap outlines also begin at y150 | The familiar approximately 27-pixel vertical residual remains. At these 1× captures, logical and drawable units agree. |
| Selected PERC bright connected component | `(168,179)`–`(232,226)`, 64×47 px; 2,560 qualifying pixels | `(169,154)`–`(233,192)`, 64×38 px; 2,032 qualifying pixels | A fixed brightness probe finds a 25-pixel face-top offset and different face-height/color distribution. This measures bright pixels, not the outer body. |
| Selected PERC upper-face sample | Mean RGB `(250.68,220.87,170.50)` in `(176,184)`–`(224,190)` | Mean RGB `(248.17,217.67,161.33)` in `(177,159)`–`(225,165)` | These small text-free bands are already fairly close in mean color. They do not measure all shading, texture or perceived depth. |

The brightness probe selects RGB channels ≥`(160,140,95)` independently, then
takes the largest four-connected component inside reference ROI
`(155,165)`–`(242,235)` and current ROI `(155,140)`–`(244,210)`. It is intentionally
reported separately from the [73.9615×48 logical outer-body contract](../PERCUSSION_REFERENCE_CONTRACT.md).
Threshold choice, JPEG shading and the material's inner inset affect this
probe. The 27-pixel bezel estimate and 25-pixel bright-face offset refer to
different landmarks. **The 64×47 and 64×38 measurements must never be used as hit geometry or
as an exact required face size.** Translating the current row downward alone
would leave its face, border, gradient and text treatment visibly different.

## Whole-frame differences still visible

| Area | Reference composition | Current actual composition | Work still needed |
| --- | --- | --- | --- |
| Performance band | Taller band with percussion at about y177 and a six-tablet vibrato/chorus group on the right | Shallower band with percussion at y150, nominal expression and two pedal-mixture controls on the right | Coordinate band height, control placement and real capability presentation. Preserve working expression/mixture access and truthful scanner status. |
| Drawbar racks | Titles above relatively open rails; footage captions below the rails and a left-side scale | Racks begin higher; footage is above, numeric positions below, and EDIT BANK / SOUNDING captions occupy separate space | Reconcile vertical allocation, labeling and live bank-state cues while preserving the correct harmonic footage and drawbar direction. |
| Manuals and preset cheeks | Large wooden cheek assemblies with three illustrative BASS / LOWER / UPPER switches; deeper key fronts and warmer contact shadows | A target/octave toolbar, real reversed preset keyboards, edit-bank buttons, two complete playing manuals and a pedalboard | Preserve real preset/note ownership and reachability while redesigning projection, framing and surrounding allocations. Three illustrated switches cannot replace the real preset controls. |
| Header | Large lit navigation, preset selector labeled Studio 122, gear icon, VIRTUAL ORGAN CONCEPT subtitle | Smaller navigation, Save / Load / Help / Audio / MIDI / Panic, Flat toggle and NOMINAL DRY ORGAN subtitle | Design a complete header arrangement that retains the implemented controls and current product truth. The concept's preset widget is not evidence of that feature being connected. |
| Cabinet column | Image above microphone knobs and Stop / Slow / Fast controls | Decorative cabinet image above explicit disconnected-rotary/device status, with the pedalboard below | Coordinate layout with the rotary owner and actual integration. Any future controls need real semantics and verified behavior. |
| Material and type | Soft lighting, broad worn metal/wood transitions, sculpted tablet edges and strong engraved/embossed title treatment | More regular rectangular outlines, crisp linear gradients, simpler bevels and smaller fitted captions | Review material profiles, border weight, corner transitions, type and shadow treatment using native output. A reference crop cannot replace live text or interactive geometry. |
| Default/minimum/Flat views | The supplied concept is a single wide composition | Responsive Play views, a deliberate Flat view, and separate Rotary/Service information layouts | Continue explicit responsive design and native readability checks. The single reference does not supply exact compact/Flat or hidden-workspace targets. |

The [Cancel frame](../../examples/demos/standalone-audio-preview-v1/percussion-states/images/cancel-stored-on.png)
correctly shows stored amber ON with REQUIRES UPPER B and a cancelled applied
Upper route. Its combined heading has **zero differing pixels** from the
[Fixed D frame](../../examples/demos/standalone-audio-preview-v1/percussion-states/images/fixed-d-off.png)
within `(62,126)`–`(460,150)`. The apparent difference in a scaled preview is not
evidence of a Cancel-specific glyph defect. Small combined-heading and minimum
Service text remain readability considerations for a real display review.

## Next design decisions

An **active-percussion-only material treatment inside the frozen cap bounds**
is a plausible smaller next experiment. A dedicated treatment could soften the
rigid inner outline/front-band transition and improve the highlight falloff and
corner treatment while retaining live values, exterior legends, focus and hit
regions. Version 1 explicitly requires reuse of the shared button painter, so
this needs a new bounded design decision before implementation. Editing the
shared painter would also affect other owners' controls.

That experiment should compare actual old/new cap output, use declared
text-free material sample regions and preserved source identities, and verify
unchanged pixels outside the active cap bodies under identical state. Include
selected/unselected, all values, focus, 1400/1672/1920 widths and fractional
drawable scales. A useful color or bevel improvement must be demonstrated;
the current upper-face sample is already relatively close in mean RGB. The
current 48-unit outer body leaves almost no room for the observed 47-pixel
bright span plus surrounding border/shadow clearance; an exact reference
material match cannot be assumed inside that frozen allocation. This option does not resolve
the vertical offset or whole-frame arrangement.

The **required larger next step** is a coordinated 1672×941 layout contract for
performance-band height, rack/manual allocation, header and cabinet column.
Record reference landmarks with their measurement uncertainty, then allocate
space for real retained/applied state and functional controls. Moving only the
tablets down about 27 units would push their exterior captions beyond the
present band; the parent allocations have to move together. Preserve the 47
parameter meanings, 68 ordinary controls, 147 playing keys, release ownership
and all supported responsive paths. Keep incorrect concept domains and
unconnected capabilities out of the functional specification.

For either scope, qualify geometry, input, focused/held states, identical-state
pixel containment and newly captured native frames independently. The present
receipts remain evidence for their exact source hashes. A changed implementation
needs new receipts, and its final publication must identify the committed code
that matches them. Full visual equality requires a separate whole-frame review;
it cannot be inferred from the scoped material or percussion checks.
