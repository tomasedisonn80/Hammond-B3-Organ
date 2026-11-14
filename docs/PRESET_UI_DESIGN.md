# Native preset-key interface contract

Design identity: **`native-preset-keys-v1`**. This is A09's wave-2 implementation
contract for review and freeze by the integrator. It extends
[PRESET_SELECTION_CONTRACT.md](PRESET_SELECTION_CONTRACT.md) and the existing
[reference layout](REFERENCE_UI_DESIGN.md). A design calculation is not a native
execution result; the required implementation and capture gates appear below.

## Source and intended player behavior

The [unchanged atlas](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf), pp. 410,
414–418 and 440, requires **61 playing keys and twelve reversed preset keys per
manual**, four retained nine-drawbar banks and 25 separate pedals. Page 440
separates editing, sounding registration and held-note ownership. The complete
source review is retained in [A05](development/2026-11-14-preset-continuation/05-atlas-product.md).

The exact [cover/page-409 JPEG](design/atlas-cover-reference.jpg) is the material
and composition target. Its SHA-256 is
`9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187`.
The previously retained [1672×941 native capture](../examples/demos/standalone-midi-ui-v1/images/reference-1672x941.png),
SHA-256 `239a38c6f47079e442c4ecb0c62c8e38c81d032153be93d892bc854966835fc7`,
is the comparison baseline, not a capture of this proposed change. The PDF's
SHA-256 remains
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.

Each manual gets one C–B reversed octave on its left cheek. It replaces that
manual's PLAY A, PLAY B and CANCEL buttons. EDIT A and EDIT B remain separate
actions. Selecting a preset changes routing; it does not overwrite an editable
bank, play a note, release a held note, change the keyboard target, or move the
other manual's controls. Existing SAVE/LOAD remain explicit whole-control actions.

| Key label | Selector value | Action and visible meaning |
|---|---:|---|
| C | 0 | Momentary Cancel; disable this manual's route while retaining its remembered fixed choice and bank. |
| C#, D, D#, E, F, F#, G, G#, A | 1–9 | Select the corresponding fixed row for this manual from `atlas-chapel-nominal-v1`. |
| A# | 10 | Sound retained adjustable bank A. |
| B | 11 | Sound retained adjustable bank B. |

**Fixed A and adjustable A# / bank A are different identities.** Labels use
pitch names on the small keys; Help and the focused-control description explain
the full action, for example `Upper preset A#: adjustable bank A` or
`Lower preset A: fixed registration`. The documentary rows have no invented
historical voice names. EDIT A/B retains the repository's bank nomenclature.

## Public UI identity and bounded inventory

Append **`UiControlKind::PresetKey = 19`** after `MidiSettings = 18`; preserve all
earlier enum values. Its canonical `UiControlId` is:

```cpp
{UiControlKind::PresetKey, manual, DrawbarBank::A, preset_index}
```

`manual` must be Upper or Lower. `bank` is the canonical, unused A field; it
does not encode the chosen adjustable bank. `index` is the exact selector
integer 0 through 11 in the table above, not a MIDI note or a control-array
offset. Reject invalid manual, noncanonical bank or index outside this range
without mutation. The twelve keys of one manual map to its single selector
parameter: upper 20480, lower 20481. Parameter conversion follows the separately
frozen [state/parameter contract](PRESET_STATE_PARAMETER_CONTRACT.md).

`SoundingBank` and `CancelManual` may remain valid semantic compatibility
actions, but have **no visible geometry or Tab entries** in the new layout.
PresetKey is never included in `is_playing_control`, note conversion, note-owner
allocation, playing-key glissando, or the 147 playing-key geometry records.

| Ordinary-control group | Count |
|---|---:|
| Save, Load, Help, Audio, MIDI, Panic | 6 |
| EDIT A/B, two manuals | 4 |
| Reversed preset keys, two manuals | 24 |
| Visible manual drawbars, two manuals | 18 |
| Percussion tablets | 4 |
| Expression | 1 |
| Pedal-mixture drawbars | 2 |
| Computer keyboard target | 3 |
| Octave down/up | 2 |
| **Total** | **64** |

This is exactly the existing bound: **46 − 6 + 24 = 64**. Keep
`kUiMaxControls = 64`; there is no overflow slot or hidden duplicate route
button. Independently retain all 61 Upper, 61 Lower and 25 Pedal playing keys.

## One layout for drawing, input and focus

All dimensions below are logical window units. Keep the admitted range
960≤W≤8192 and 700≤H≤8192, default **1280×900**, and reference capture
**1672×941**. Rectangles use the existing half-open containment convention.
Generate a complete candidate layout, validate it, then replace the old layout;
invalid dimensions leave the old layout and state untouched.

### Existing rows and responsive thresholds

Retain the existing row-height algorithm so this change does not also redesign
the performance strip, drawbar ranges, pedals, footer or cabinet:

```text
wide = W >= 1400
tall = H >= 820
margin = wide ? clamp(0.043*W, 48, 72) : 16
gap = (!tall || !wide) ? 8 : 10
content_width = W - 2*margin
cabinet_width = wide ? 0.30*content_width : 0
player_width = wide ? content_width - cabinet_width - gap : content_width
header_height = (!tall || !wide) ? 82 : 90
performance_height = clamp(76 + 0.12*(H-700), 76, 110)
rack_height = clamp(168 + 0.24*(H-700), 168, 236)
pedal_height = clamp(58 + 0.08*(H-700), 58, 86)
toolbar_height = 28
footer_height = 36
manual_height = (H - 32 - header_height - performance_height - rack_height
                 - toolbar_height - pedal_height - footer_height - 7*gap)/2
```

Stack header, performance, racks, keyboard toolbar, Upper manual, Lower manual,
pedals and footer from y=16, with the existing gaps. The footer ends at H−16.
At W=1399 the cabinet is absent; at W=1400 it appears using the existing
proportions and aspect-preserving artwork rule. No preset or playing key is
conditionally omitted at that transition.

`bank_controls_in_cheeks = tall` now means **EDIT button placement only**.
Both preset cheeks exist below and above H=820. At H=819 the EDIT buttons are
above their drawbars; at H=820 those same identities move into their manual
cheeks. Reflow does not select a bank, clear a fixed route, drop focus or release
an independently held note. Preserve the existing resize behavior that ends an
active parameter drag without changing its last admitted value.

### Cheeks, EDIT buttons and preset octave

Replace the old conditional 112–156 cheek with:

```text
rail_width = clamp(0.15*player_width, 156, 168)
rail = {margin, manual_y, rail_width, manual_height}
manual_panel = {margin + rail_width + gap, manual_y,
                player_width - rail_width - gap, manual_height}
preset_panel = {rail.x + 8, rail.y + (tall ? 54 : 22),
                rail.width - 16, rail.height - (tall ? 62 : 30)}
```

Store both `manual_rail_panels` unconditionally and append
`preset_key_panels[2]` to `UiLayout`. The latter is the shared bounding rectangle
for generation and painting, not an independently positioned renderer region.
The 156-unit minimum gives the narrowest ivory accidental a 12-unit width.

For tall layouts, the two EDIT buttons occupy y=rail.y+22, height24, inset8,
gap4, and width `(rail.width−20)/2`. For compact layouts, place them at
y=rack.y+28, height26, beginning x=rack.x+12 with gap4 and each width
`min(76, (rack.width−28)/2)`. Preserve the compact drawbar label top of60;
the tall drawbar label top remains32. The manual title stays in the cheek's
y+3 to y+20 heading strip. Remove the old `61 PLAYING KEYS` cheek annotation
at y+109 because the new octave occupies that area. Key counts belong in Help
or the existing manual/pedal headings.

Preset geometry is generated in increasing semitone order C through B. Natural
indices are **0,2,4,5,7,9,11**; accidentals are **1,3,6,8,10**. There are seven
dark naturals and five short ivory accidentals. For preset panel P:

```text
natural_width = P.width / 7
natural n: left = P.x + P.width*n/7
           right = P.x + P.width*(n+1)/7
           bounds = {left, P.y, right-left, P.height}
accidental following n naturals:
           bounds = {P.x + n*natural_width - 0.30*natural_width, P.y,
                     0.60*natural_width, 0.62*P.height}
```

Derive both natural edges from their ordinal to avoid accumulated gaps. Each
key has one `UiControlGeometry`. Its `bounds` is the rectangle above, and
`value_bounds`/`track` are empty. Natural labels retain
`label_bounds = {x+1, y+height−13, width−2, 11}` and their centered 9-unit
single letter. The interface continuation's A34 readability correction gives
accidentals `label_bounds = {x+1, y+height−22, width−2, 20}`. Center the canonical
pitch letter and `#` separately at 9-unit Sans in 11-unit line boxes, with
the second line beginning nine units below the first. Both glyphs fit the
minimum ten-unit label width without shrinking; the glyph ink does not overlap.
Keep the complete pitch name in semantic selection and focus captions. Labels
remain inside their original keys, with unchanged hit bounds and selection.
Actual minimum-size and 1400×820 raster inspection is required in both modes,
including the clipped focus stroke above the taller accidental label region.

Keep existing playing-key generation: its own panel has left inset8, top22,
width−16 and height−30; 36 naturals and 25 accidentals per manual. Presets and
playing keys have disjoint regions. Pedal geometry remains unchanged.

### Arithmetic acceptance anchors

The following values are calculated from these formulas, rounded for display.
They are expectations for an implementation test, not observed native pixels.

| Window | Cabinet / EDIT placement | Player width | Cheek width | Manual height | Preset height | Preset natural / accidental width |
|---|---|---:|---:|---:|---:|---:|
| 960×700 | Hidden / rack | 928.000 | 156.000 | 82.000 | 52.000 | 20.000 / 12.000 |
| 1280×900 | Hidden / cheek | 1248.000 | 168.000 | 138.000 | 76.000 | 21.714 / 13.029 |
| 1672×941 | Visible / cheek | 1059.746 | 158.962 | 138.480 | 76.480 | 20.423 / 12.254 |
| 1399×819 | Hidden / rack | 1367.000 | 168.000 | 115.320 | 85.320 | 21.714 / 13.029 |
| 1400×819 | Visible / rack | 887.720 | 156.000 | 115.320 | 85.320 | 20.000 / 12.000 |
| 1399×820 | Hidden / cheek | 1367.000 | 168.000 | 115.600 | 53.600 | 21.714 / 13.029 |
| 1400×820 | Visible / cheek | 885.720 | 156.000 | 104.600 | 42.600 | 20.000 / 12.000 |

The joint width/height transition is deliberately included: at 1400×820 the
wide header and larger gaps reduce manual height by 11 relative to 1399×820.
The shortest preset accidental is still 26.412 units high. That remains a
small desktop target; this contract makes no touch-target or accessibility
conformance claim. Keyboard activation must be complete.

### Paint and hit order

Keep control-array order semantic: the six header controls, then each manual's
EDIT A, EDIT B, twelve preset keys in pitch order and nine drawbars, followed
by the existing performance/toolbar groups. Rendering and hit testing must not
depend on that insertion order for overlapping keyboard rectangles.

Paint all preset naturals first, all preset accidentals second, then the focus
indicator. Test preset accidentals before naturals for pointer hits. Existing
playing-key accidental-first hit testing remains. Other controls are disjoint;
do not allow a natural's full rectangle to steal an overlapping ivory key.
Check exact boundaries as well as centers, using the half-open rule.

The focused preset's outline derives from its same bounds. For an accidental,
use inset2. For a natural, use the exposed lower portion beginning
`y + 0.62*height + 2`, with x+2, width−4 and height `0.38*height−4`.
This keeps a last-painted natural focus ring from crossing an overlapping
accidental. Use a dark outer edge and light inner edge so focus remains visible
on either material. Material shadows may overlap cosmetically, but never expand
the hit region or create another interactive identity.

## Applied state, edited bank and command feedback

All sounding highlights and route captions derive from the copied
`view.applied.controls` snapshot through the checked effective-selection helper
in [PRESET_CORE_API.md](PRESET_CORE_API.md). The renderer does not read Engine.
Drawbars continue displaying `view.controls` for the separately selected
`view.edited_banks[manual]`; a pending drag can remain responsive without being
presented as an applied sounding route.

| State | Required visible result |
|---|---|
| Applied fixed C# | C# has the selected/depressed treatment; rack caption `EDIT B / SOUNDING FIXED C#` when B is being edited. |
| Applied adjustable A# | A# has the selected treatment; caption `EDIT B / SOUNDING A#` when B is being edited. Help identifies A# as bank A. |
| Applied adjustable B | B has the selected treatment; caption names sounding B independently of EDIT A/B. |
| Applied Cancel | No preset key is latched. Caption says `EDIT A / CANCELLED` or `EDIT B / CANCELLED`. Remembered fixed/bank fields stay intact. |
| Different desired selection awaiting acknowledgment | Keep the applied key selected. Give only the desired target a thin amber request outline and show `PRESET … PENDING` in status. C can have that request outline but never a latched/depressed state. |
| Rejected submission or recovery | Clear the request outline, restore desired state from the latest applied snapshot under the existing model contract, and retain visible rejection/recovery status. Do not invent a successful selection. |

Use a slight face recess plus a warm top accent for an applied selection. Focus
is the separate two-tone outline; pending is a thin amber outline. Neither
color alone nor a single shared `selected` Boolean represents all three states.
Do not retain the old Cancel button rule that paints route-disabled as selected.
An optional press animation for C must depend only on an active pointer/key
gesture and clear on release, cancellation, focus loss or resize; always-raised
C is acceptable for this first native implementation. The route status remains
visible after the momentary action.

Keep the rack's applied-state caption and separate EDIT identity visible at all
three target sizes. Fit measured dynamic text inside the existing state region;
use the compact `EDIT B / FIXED C#` only if the full caption cannot fit at the
minimum font, and retain the full phrase in focused-control status. Pending
details go in the footer/status, not in a clipped extension of the rack title.

Upper percussion eligibility is **route enabled, no fixed registration and
retained bank B**, in addition to its stored enabled choice for sound. Keep
all four stored tablet settings displayed while ineligible. Show `REQUIRES
UPPER B` rather than moving a drawbar or changing the stored percussion choices.
The remembered B field alone must not make a fixed registration look eligible.

## Pointer and keyboard interaction

A primary pointer-down on a preset focuses and activates that semantic key
once. It creates a candidate copied control state via `select_preset` and
publishes the existing bounded control command. Pointer-up does not undo the
selection or release a note. Moving with the pointer held does not glissando
through presets or playing keys. No timer, callback allocation or DSP access
is introduced. Invalid IDs are rejected before mutation.

Preset activation does not acquire the playing-key pointer capture. A later
capture-loss notification clears any optional pressed-key visual but neither
reverts the accepted selection nor submits another selector command. Existing
global focus-loss cleanup for independently held UI notes retains its own
meaning; preset controls introduce no owner for that cleanup to release.

Space and Enter activate a focused preset once on key-down; repeated key-downs
are suppressed. Their release does not enqueue a Note Off. Ordinary computer
playing keys and F1/F2/F3 retain their existing independent meanings. Do not
assign the letter C or A to a preset shortcut that conflicts with playing.

| Navigation | Result while a preset key has focus |
|---|---|
| Left / Right | Move one semitone within 0–11, clamped at either end; no sound change. |
| Home / End | Focus C / B of the same manual; no sound change. |
| Up / Down | Focus the same index on Upper / Lower respectively; stay put at the outer edge. |
| Tab / Shift+Tab | Traverse ordinary controls in semantic order, including all 24 presets, then the existing three roving playing-key groups. |
| Space / Enter | Activate the focused key using the selector command. |

The bounded existing Tab array accommodates **64+3=67** stops without resizing
its capacity. Preset navigation does not alter the roving playing-key indices.
Resizing, a remote control update or EDIT-bank change keeps a focused PresetKey
identified by manual/index, never by its previous coordinates. Escape retains
its existing UI-note release behavior; it is not a preset undo command.

Keyboard operation and visible focus are acceptance requirements. A future
native accessibility bridge should expose C as a button and the eleven routed
choices as one exclusive selection group per manual, with full names, applied
selected state and pending/error status announcements. The current SDL canvas
does not acquire screen-reader semantics merely by painting those names. Actual
assistive-technology qualification remains a separate M9 gate.

## Native material and depth refinement

The reference has deeper black sockets, narrow metallic drawbar stems, thicker
cap fronts, stronger key fronts and warmer ivory than the retained application
capture. Make the following bounded changes in actual native drawing while
keeping labels, state and geometry live:

| Surface | Implementable treatment |
|---|---|
| Charcoal deck | Shift the visibly olive panel gradient toward neutral warm charcoal; retain a thin brass outer edge, dark inner lip and restrained top highlight. Avoid bright flat outlines around every inset. |
| EDIT and header tablets | Paint socket, 2–3-unit down/right shadow, beveled cap and separate 3–5-unit front face, then dynamic text. Keep every layer inside the existing ordinary-control bounds. |
| Drawbars | Use a 3–4-unit metallic stem with one narrow highlight inside the existing track; deepen the cap's lower face and under-cap shadow. Preserve correct footage, brown/ivory/black order and zero-top/eight-bottom travel. |
| Playing keys | Increase natural front-face height to `clamp(0.16*height, 6, 16)`; strengthen the fallboard shadow and accidental side bevel. Preserve the existing key rectangles and all 147 playing identities. |
| Reversed preset keys | Reuse the same depth language with dark naturals and ivory accidentals. The fixed/bank selection recess and labels are painted from actual state. C does not receive a latched recess. |
| Walnut and cabinet | Preserve the approved wood-cheek and cabinet crops and their provenance. Add frame depth through native drawing; retain factual device/signal status below the cabinet. |

Use existing Drawing primitives and prepared assets. Any future extra texture
needs its own recorded source/rights, preparation and lifetime outside audio.
Do not use a stretched image of the whole source panel to impersonate live
controls. Do not add rotary speed, microphone or scanner controls until their
actions are implemented. Correct source-art legends and key inventory remain
intentional semantic differences.

Rectangular manuals still differ from the source's perspective. A later true
perspective pass needs shared transformed hit/paint/focus geometry and new
edge tests. This refinement improves native materials inside qualified regions;
it does not establish literal 1:1 equivalence. Permanent visible pedals, the
computer-key toolbar, working utility actions and factual cabinet status also
remain visible differences to document beside actual captures.

## Implementation and independent acceptance handoff

1. **UiModel owner:** append the enum and preset rectangles; replace only the
   six visible route buttons; implement checked IDs, shared geometry,
   accidental-first hits, parameter/action conversion and navigation. Confirm
   64 ordinary identities and 147 separate playing identities at every size.
2. **Renderer owner:** paint both cheeks at every height, reverse the new key
   materials, order the passes explicitly, show applied/edited/pending/focus
   independently, correct fixed-route percussion eligibility, and update Help.
   Remove the obsolete cheek key-count annotation.
3. **Behavior acceptance:** exercise all 24 preset identities by pointer and
   keyboard; check sharp-key overlap boundaries, invalid IDs, repeated input,
   Tab count, focus retention and every responsive transition. Hold independent
   UI/MIDI notes through fixed→bank→Cancel→fixed changes, rejected commands,
   inactive editing and resize; preserve note owners and other divisions.
4. **Native visual acceptance:** capture actual 1672×941, 1280×900 and 960×700
   windows, plus the 1399/1400 and 819/820 cross-product. Include an applied fixed
   route, adjustable route, Cancel, visible focus, pending/rejected feedback and
   ineligible stored percussion. Inspect every label and the shortest preset
   accidental. A geometry test alone cannot establish readable raster output.
5. **Integrator:** retain exact source/executable/dependency and capture
   identities, observed results and remaining visual differences; update README,
   operating guidance, status and next steps. Preserve old galleries and source
   art. Follow the standing publication instructions in [AGENTS.md](../AGENTS.md).

No native screenshot, sound, hardware, pixel-equality or assistive-technology
pass is claimed by this contract. The [A09 evidence note](development/2026-11-14-preset-continuation/09-ui-contract.md)
records the source inspection and independent arithmetic actually performed.
