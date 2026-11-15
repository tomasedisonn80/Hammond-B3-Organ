# Percussion reference refinement contract

**Version 1, 15 November 2026.** Implementation candidate for independent
review; this document does not report an implementation or acceptance pass.
Source basis is atlas pp. 409–418, 431 and 435, the unchanged
[cover/page-409 reference](design/atlas-cover-reference.jpg), and the
[A05 complete reading and visual review](development/2026-11-15-audio-continuation/notes/A05.md).
The reference SHA-256 is
`9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187`.

## Scope and invariant identities

Refine only the four percussion tablets, their legends and percussion eligibility
text inside the existing performance subsection. The active predicate is **Play,
Dimensional, logical width >= 1400 and height >= 820**. It is equivalent to
Play plus `layout.sidebar_pedals` plus Dimensional in the current layout.
Outside this predicate, preserve existing geometry, insertion order, paint and
behavior exactly. The predicate must be identical in layout and painting.

Do not change the performance panel, divider, other panels, racks, playing keys,
header, expression or pedal mixtures. Reuse existing tablet materials without
changing the shared `button` painter. No new image asset or sound parameter is
needed. Preserve all 47 parameter meanings, `B3CONTROLS4` and older readers,
68 ordinary controls, 147 playing keys, retained/applied state and note ownership.

| Active visual slot, left to right | Stable percussion index | Parameter ID | Exterior legend | Displayed value |
| --- | ---: | ---: | --- | --- |
| 0 | 0 | `0x3000` | PERC | ON / OFF |
| 1 | 2 | `0x3002` | VOL | NORM / SOFT |
| 2 | 3 | `0x3003` | DECAY | SLOW / FAST |
| 3 | 1 | `0x3001` | HARM | 2ND / 3RD |

All IDs retain canonical `Manual::Upper` and unused `DrawbarBank::A`. Visual
order **[0, 2, 3, 1]** is presentation only. The reference's NORM under DECAY
and FAST under HARM are erroneous domains and are corrected by this table.

## Geometry owned by the layout

All quantities are logical window units. `P` is the unchanged performance
rectangle; `G = 0.46 * P.width` is its unchanged percussion subsection width.
Use binary32 layout arithmetic as elsewhere; do not round to integers until
drawing. For the active predicate define:

```text
s = clamp(G / 480, 0.80, 1.25)
w = 74 * s
h = min(48, P.height - 43)
x0 = P.x + 0.535 * G - 164 * s
y0 = P.y + 24
slot offsets = [0, 92, 173, 254] * s
```

For each visual slot, with `x = x0 + offset`, store:

| Geometry field | Rectangle `(x, y, width, height)` |
| --- | --- |
| `bounds` | `(x, y0, w, h)` |
| `value_bounds` | `(x + 5, y0 + 5, w - 10, h - 12)` |
| `label_bounds` | `(x - 2, y0 + h + 2, w + 4, 13)` |
| `track` | Empty |

Here “tablet” means the complete outer bezel/hit rectangle; its ivory face is
inset by the existing material painter. The group span is `328*s`, with gaps
`18*s`, `7*s`, `7*s`. The modest rightward group offset follows the reference's
composition. The `480` normalizer and scale limits are layout choices, not
physical dimensions or measurements. The height formula leaves four units below
the exterior legend at the shortest admitted active strip.

The current parent layout gives these useful independent check points:

| Window | Outer tablet width/height | Left edges by visual slot | Top |
| --- | --- | --- | ---: |
| 1400×820 | 61.8141 / 47.4 | 137.7182, 214.5682, 282.2296, 349.8910 | 150 |
| 1672×941 | 73.9615 / 48 | 164.6477, 256.5998, 337.5577, 418.5156 | 150 |
| 1920×1080 | 86.0690 / 48 | 179.9352, 286.9399, 381.1506, 475.3612 | 150 |

These are authored calculations, not observed application output. Independent
geometry checks may use 0.002 logical-unit tolerance for float rounding. All
rectangles must be finite, positive, within the percussion subsection, and
disjoint from neighboring control hit regions. Preserve transactional layout
rejection for invalid dimensions, banks, workspace or presentation. No second
paint-only rectangle or enlarged caption hit target is allowed.

## Paint and eligibility

Paint the existing ivory/selected-amber tablet into `bounds`, with no baked text.
Center only the live value in `value_bounds`: Serif, requested size 17,
opaque RGB `(33, 28, 21)`. Center the exterior legend in `label_bounds`: Serif,
requested size 10.5, opaque `kUiIvory`. Use the existing fitted `centered` helper;
font pixels and cap material are separate. Only enabled PERC gets the existing
selected-amber treatment. Stored ON stays ON even when its sounding route is
ineligible. The existing two-unit cyan focus outline remains over `bounds`.

Values and the PERC selected state come from `view.controls`. Eligibility comes
from the copied **applied** upper route: enabled route, no fixed registration,
selected bank B. This is route eligibility, independent of the stored percussion
enable switch. Preserve existing pending-control cues and footer descriptions.

For this active branch only, a separate eligibility line is allowed when
`P.height >= 104`. Keep the existing heading rectangle
`(P.x+17, P.y+3, G-34, 18)` and size 13.5 with text PERCUSSION. Place the line
in `(P.x+12, P.y+P.height-16, G-24, 11)`, requested Sans size 9, using existing
green/muted colors and **UPPER B ROUTE ACTIVE / REQUIRES UPPER B** text.
For a shorter active strip, omit that line and use the existing combined
heading text **PERCUSSION / UPPER B ACTIVE** or
**PERCUSSION / REQUIRES UPPER B** at requested size 10.5. The inactive branch
retains its existing 92-unit eligibility threshold and original coordinates.

## Input and focus

Insert the four active `UiControlGeometry` records in visual order, preserving
their stable IDs; existing Tab/Shift+Tab traversal therefore follows that order
without a second focus map. The predecessor/successor controls and total focus
stop count remain unchanged. Inactive order remains [0, 1, 2, 3]. Resize or
presentation changes preserve the semantic focused ID, even when its ordinal
moves. Existing workspace focus memory and held-note release ownership continue.

Pointer hits use the existing left/top-inclusive, right/bottom-exclusive
`bounds`. Exterior legends, group gaps and eligibility text are not controls.
A press toggles only its stable parameter once; repeat/down suppression and
release behavior stay unchanged. Space/Enter activate the focused tablet;
arrows/Home/End retain the existing no-op behavior for percussion. Tab is
navigation only and must not emit a musical edit or a note event.

## Required acceptance

1. **Geometry and targeting:** independently measure the three cases above,
   threshold neighbors 1399×820 and 1400×819, fractional valid sizes and the
   maximum supported dimension. Verify IDs/domains, all center/edge/gap/legend
   hits, nonoverlap and rejected-input preservation. Tests must address intended
   targets and invariants, not merely copy the implementation's equations.
2. **Musical interactions:** exercise every toggle value and every focus slot,
   forward/reverse Tab including wrap, Space/Enter, repeated Down, resize and
   Flat/Play/Rotary/Service round trips. Cover upper A, upper B, fixed preset,
   cancel, pending versus applied routing and held UI/MIDI notes. Only the
   intended control may change; audio-state formats and note ownership remain
   compatible. Preserve the stored-enabled-but-ineligible display.
3. **Paired raster containment:** compare baseline/candidate with identical
   view state, renderer, fonts, logical/drawable sizes and clipping. Active
   differences must be contained in the union of old/new percussion tablets,
   legends, focus ink and old/new heading/eligibility regions, allowing at most
   one outward device pixel for raster rounding. Require exact equality outside
   that union, including the divider, expression and mixtures. Require complete
   equality for inactive compact/Flat and hidden Rotary/Service bodies. Cover
   on/off, all value combinations, focus, threshold sizes, 1672×941, 1920×1080,
   1×/1.5×/2× drawable scale and boundary-crossing clips.
4. **Actual application evidence:** capture the changed application at reference,
   default, minimum and Flat sizes. Retain source, executable, replay, state and
   decoded-pixel identities; independently inspect the original JPEG and actual
   new frames. The integrator updates README with these captures and the
   measured remaining differences. No concept image may stand in for app output.

The original reference tablets start near y177; this constrained candidate
starts at y150 in the unchanged current strip. Horizontal grouping, proportion
and value/legend hierarchy can improve, but that approximately 27-unit vertical
residual remains. Later exact vertical alignment requires a coordinated change
to performance-strip height and rack/manual allocation, owned and qualified
separately. The user's literal whole-interface 1:1 objective remains **unmet and
unwaived**. This scoped contract also does not establish native semantic
accessibility, physical-device usability, frame rate or audio fidelity.
