# Native reference-player layout

Contract identity: **`standalone-reference-player-layout-v1`**. This is the
implementation contract for the MIDI/UI session, not an executed visual pass.
The [scope](MIDI_UI_SCOPE.md), [existing interaction contract](STANDALONE_UI.md)
and [source review](research/MIDI_UI_ATLAS_REVIEW.md) retain musical semantics.

The exact appearance source is the [1672 × 941 atlas cover](design/atlas-cover-reference.jpg),
with its [source identity](design/atlas-reference.json). Use its walnut cheeks,
charcoal metal, brass highlights, raised tablets, adjacent drawbar racks, stacked
manuals and right cabinet composition. All controls, values, keys and focus are
drawn from the real copied model. Decorative source pixels cannot replace them.

## Retained behavior and small API changes

Keep the 45 core parameters and `B3CONTROLS3` unchanged. Retain 36 manual drawbar
values, two pedal values, 18 visible manual editors, 61 playing keys per manual
and 25 pedals. EDIT and SOUNDING remain separate. Cancel changes one route;
Panic releases notes. Keep all current pointer, keyboard, note-ownership,
submission/acknowledgment and original-gesture rules.

The header contains the existing SAVE, LOAD, HELP, AUDIO and PANIC actions plus
one new MIDI settings action: **46 ordinary UI controls**, within the existing
64-slot capacity, plus the separate 147 playing-key geometries. This UI count
is not the core parameter count. Append `MidiSettings` to the private UI control
and app-request enums; do not insert or change public parameter identities.
No new PLAY/ROTARY/SERVICE tab machinery is required for this slice.

Keep the default 1280 × 900 window. Capture the reference comparison explicitly
at 1672 × 941. Add these main-thread-only fields to `UiLayout`:

| Field | Meaning |
|---|---|
| `bool show_cabinet` | Width is at least 1400 logical units. |
| `bool bank_controls_in_cheeks` | Height is at least 820 logical units. |
| `UiRect cabinet_panel` | Complete right illustration/status region; empty when hidden. |
| `UiRect cabinet_art` | Aspect-preserving cabinet-only decoration inside that region. |
| `std::array<UiRect, 2> manual_rail_panels` | Left bank-control cheeks; empty in the short layout. |

Existing `registration_panels`, `performance_panel`, `manual_panels`,
`pedal_panel`, `keyboard_toolbar`, `footer`, control and key arrays remain the
single source of paint and hit geometry. An empty decorative rectangle is never
an input target. The renderer must not independently recreate control bounds.

## Shared layout algorithm

Use finite admitted logical window dimensions `W,H`. Preserve the current
960 × 700 minimum and 8192 maximum. `clamp(v,a,b)` includes both endpoints.

```text
wide  = W >= 1400
dense = H < 820
m = wide ? clamp(W * 0.043, 48, 72) : 16
g = (dense || !wide) ? 8 : 10
C = W - 2*m
cabinetW = wide ? 0.30*C : 0
leftW = wide ? C - cabinetW - g : C

headerH = (dense || !wide) ? 82 : 90
performanceH = clamp(76 + 0.12*(H-700), 76, 110)
drawbarH = clamp(168 + 0.24*(H-700), 168, 236)
toolbarH = 28
pedalH = clamp(58 + 0.08*(H-700), 58, 86)
footerH = 36
manualH = (H - 32 - headerH - performanceH - drawbarH
           - toolbarH - pedalH - footerH - 7*g) / 2
```

Stack these eight rows from `y=16`, inserting `g` between rows: header,
performance, drawbars, keyboard toolbar, upper manual, lower manual, pedals,
footer. The final footer ends at `H-16`. Header and footer span `C`; the six
intermediate rows span `leftW`. The cabinet occupies the region at
`x=m+leftW+g`, from the performance row's top through the pedal row's bottom.

Both drawbar panels have width `(leftW-g)/2`. The first begins at `m`; the
second begins one panel width plus `g` later. Each panel remains bound to its
manual and current editor bank. Column width is `(panel.width-24)/9`.

When `H>=820`, `railW=clamp(0.15*leftW,112,156)`. Each manual row has a cheek
`{m,y,railW,manualH}` and a keyboard panel
`{m+railW+g,y,leftW-railW-g,manualH}`. Put the five existing manual bank controls
in that cheek: EDIT A/B on one row, PLAY A/B on the next, full-width CANCEL on
the third. Use 24-unit button heights, 4-unit row gaps, 8-unit side insets and
the first button row at `y+22`; all three rows end at `y+102`. Show the manual
identity above them. Keep the authoritative SOUNDING/CANCELLED label in the
corresponding drawbar panel's header, independently of the edited bank.

When `H<820`, omit both cheeks and use full-width keyboard panels. Place the
same five bank controls in a row at `drawbar_panel.y+28`, height 26, side insets
12 and four 4-unit gaps. This preserves readable controls before reducing key
or label size. The bank controls are relocated, never duplicated or hidden.

Reuse the existing musical key generator: 36 naturals and 25 accidentals per
manual; 15 naturals and 10 accidentals for pedals. Natural keys paint before
accidentals, while accidentals win hit testing. Keep the existing inset/title
space and derive every key from its panel. Do not reproduce the concept's
inconsistent playing-key count or add decorative playable preset keys.

### Reference coordinates

Rounded values below are review aids. Keep unrounded geometry in the layout;
do not copy this table into a second renderer-specific coordinate system.

| Region at 1672 × 941 | x | y | width | height |
|---|---:|---:|---:|---:|
| Header | 71.90 | 16.00 | 1528.21 | 90.00 |
| Performance | 71.90 | 116.00 | 1059.75 | 104.92 |
| Upper drawbars | 71.90 | 230.92 | 524.87 | 225.84 |
| Lower drawbars | 606.77 | 230.92 | 524.87 | 225.84 |
| Upper keyboard | 237.90 | 504.76 | 893.75 | 138.48 |
| Lower keyboard | 237.90 | 653.24 | 893.75 | 138.48 |
| Pedalboard | 71.90 | 801.72 | 1059.75 | 77.28 |
| Cabinet/status | 1141.64 | 116.00 | 458.46 | 763.00 |
| Footer | 71.90 | 889.00 | 1528.21 | 36.00 |

At 960 × 700, horizontal margin is 16, `leftW=928`, cabinet and cheeks are
absent, and row tops/heights are: header `16/82`, performance `106/76`,
drawbars `190/168`, toolbar `366/28`, upper `402/82`, lower `492/82`,
pedals `582/58`, footer `648/36`. Full key range and all controls remain visible.
At the unchanged 1280 × 900 default, the cabinet is absent and cheeks remain;
manual rows are `474/138` and `620/138`. Width 1399 versus 1400 is a deliberate
composition breakpoint; a resize closes the current parameter drag but does
not alter controls, held notes, focus identity or octave.

## Header and performance placement

Use three source-styled left tablets for SAVE, LOAD, HELP, and three right
tablets for AUDIO, MIDI, PANIC. At wide sizes use left widths 112 and right
widths 90, with 8-unit gaps; at narrower sizes use widths 72 and 6-unit gaps.
They remain the existing actions plus MIDI, rather than fictitious sound views.
Keep their full paint/hit rectangles in `layout.controls`.

Center `TONEWHEEL ATLAS` between the groups in the existing serif face. Use
40-unit text at wide sizes and 28 at narrower sizes, measuring actual glyph
width before placement. The secondary line is `NOMINAL DRY ORGAN`, retaining
the actual model boundary. Keep at least 16 units between title and actions.
Wide buttons begin at `header.y+30`, height 42; narrower buttons begin at
`header.y+34`, height 32. Do not scale the title and all controls as one bitmap.

The performance strip has two recessed groups. The left 46 percent contains
the four actual percussion tablets, with their own labels and values. The
remaining region contains nominal expression plus both nominal pedal mixtures.
This replaces the source's unavailable vibrato/chorus buttons with working
controls, and is an intentional visual difference. Do not paint selectable
V1–V3/C1–C3 controls before the audio integration exists.

Keep expression's existing horizontal interaction and the mixtures' vertical
drawbar interaction. Share `track`, `label_bounds` and `value_bounds` with input.
Percussion controls occupy four evenly spaced columns with 8-unit gaps, side
insets 12, and 42-unit tablet height beginning at `performance.y+24`. Their
labels and enum values occupy separate lines. Put eligibility in the group
heading at short heights; taller strips may use a separate line below tablets.
Never overlap the minimum strip's lower edge with that explanation.

In the right group, give expression 46 percent of the available width and split
the remainder between the two mixtures with the same gap. Keep at least 24
units of mixture track travel at the minimum height and keyboard adjustment
available. Use `MIX 1`, `MIX 2` and `NOMINAL EXPRESSION` labels; no claim of
calibrated historical pedal footage or mechanical expression is added.

## Materials and dynamic control drawing

Retain source-inspired color roles: charcoal `#242725`, ivory `#F2E7CF`, brass
`#D6B67C`, cyan focus `#A5E4DF`, plus warm walnut. These are appearance choices.
The existing `Drawing` primitives can produce the functional surface; optional
art belongs to its own prepared texture and lifetime.

| Surface | Concrete drawing recipe |
|---|---|
| Frame | Wide walnut cheeks and lower rail, narrow warm highlights, darker inner lip. Use only verified decorative image regions or a procedural fallback. |
| Metal panel | Charcoal base, 2–3-unit dark recess, restrained 1-unit brass/gray upper edge, small screw recesses. Keep highlights away from legends. |
| Tablets | Dark outer bezel, lower shadow, ivory or charcoal cap, upper bevel, readable separately drawn state. Selected shape/highlight differs from focus. |
| Drawbar | Recessed slot, thin vertical shaft, shadow, 24–28-unit raised cap, upper highlight and darker front edge. Cap width is at most 34 and at most column width minus 8. |
| Keys | Ivory/black top plane, darker front face and divider, small raised lip. Paint all state inside the shared rectangular key region; do not introduce an untested perspective hit transform. |

Drawbar zero is at the top/inward end and eight at the bottom/outward end.
Use the real integer value and adopted parameter conversion. The source image's
reversed numbers and wrong footages are corrected. In tall racks, put footage
legends above tracks and numeric values below; in short racks, reserve the bank
button row first and preserve separate label/value regions. Cap colors in
footage order remain brown, brown, ivory, ivory, dark, ivory, dark, dark, ivory.
Every caption, value, cap position, held key, dirty/pending indication and focus
ring is dynamic. Do not sample these elements from the concept image.

## Decorative asset boundary and service card

The full original JPEG is 1672 × 941. These source rectangles are the approved
starting regions for an independently verified asset pipeline:

| Decoration | Original pixel rectangle `(x,y,w,h)` | Boundary |
|---|---|---|
| Cabinet and microphones | `(1132,174,466,397)` | Excludes cabinet heading and all microphone/speed controls. |
| Left wood cheek | `(0,0,24,941)` | Visually verified outer wood/edge only; no control legends. |
| Right wood cheek | `(1604,0,68,941)` | Wood/edge only; no control legends. |

The originally proposed `(0,0,72,941)` left crop includes fragments of both
`BASS` tablets and their labels. Exact crop inspection rejected it; only its
control-free outer 24-pixel strip is admitted. The source/crop/pixel identities
and rejected region are retained by the [asset pipeline](REFERENCE_ART_ASSETS.md).

The lower rail includes baked `DESIGN CONCEPT` text. Do not stretch or tile the
whole rail into the application footer. Prefer a procedural wood rail or a
separately inspected text-free sample. Asset authoring must record exact crop,
color conversion, pixel identity, decoder/tool identity and delivered bytes.
Source-image extraction is not an application capture.

Inside the cabinet panel, reserve a 30-unit dynamic header. Put artwork at
`panel.x+12,panel.y+38`, with width `panel.width-24` and height
`width*397/466`. Preserve its aspect ratio. `cabinet_art` stores this destination.
Below it, show `CABINET REFERENCE — AUDIO NOT CONNECTED`, then a factual service
card using copied application state: actual audio running/stopped state and
configuration, MIDI connection/route status, and scanner/rotary unavailable.
No faux RPM, microphone distance, rotor animation, waveform, temperature or
authenticity percentage is displayed.

The service card is read-only, so it adds no hidden control IDs. MIDI entry and
brief connection state remain available in the header/footer when this entire
right region collapses. A decoration decode/upload failure uses the fully usable
procedural player surface; it cannot prevent playing, saving or Panic. Texture
creation, disposal and file/image processing stay off the audio callback.

## MIDI settings and copied presentation state

The MIDI button opens a native settings overlay through `UiAppRequest`; merely
opening it changes no audio route or controller ownership. The app owns a
single shared `MidiOverlayLayout` for its paint, pointer and keyboard focus.
Reuse the current modal size discipline: a centered panel no larger than
740 × 520 at the minimum window. Provide port selection, explicit Refresh,
Connect/Disconnect, three wire-channel choices and Close. Apply only an admitted
distinct 1–16 channel triple, under the MIDI contract's stop/release/reopen rules.

Show unavailable, disconnected, connecting, connected and faulted states from
the backend's copied status; do not infer connection from a selected row. Keep
exact port identity available even if the player view abbreviates it. Source
names/errors must be clipped or wrapped to their panel, never drawn over controls.
All controls remain reachable by Tab/Shift+Tab with visible focus and keyboard
activation. Existing Help and audio behavior remain intact.

Add copied MIDI display fields to `InstrumentViewInfo` as needed. Refactor its
construction to named field assignments if new fields would make the current
positional aggregate fragile. Neither renderer nor assistive UI reads a live
backend or Engine. Native screen-reader semantics remain a separate feature gate.

## Acceptance and remaining reference differences

The implementation needs actual captures at 1672 × 941, unchanged default
1280 × 900, and minimum 960 × 700. Also execute the 1399/1400 width and 819/820
height transitions with held UI/MIDI notes and a captured drawbar gesture.
Check all 46 control identities, both manuals, all pedals, label bounds,
inactive-bank edits, mixed note ownership, focus, modal return and off-window
release. Update old hardcoded pixel locations and the old 45-UI-control
expectation against independently reviewed geometry, rather than weakening them.

Retain native source/binary/dependency identities, controls, renderer, dimensions
and capture commands. The README must label source art separately from actual
application screenshots. Compare region placement, material treatment, cap/key
depth and typography; list intentional corrections and remaining discrepancies.

This contract deliberately differs from the concept's exact navigation text,
unavailable scanner/speed/microphone controls, inaccurate legends/key inventory,
static preset text and missing visible pedals. It uses rectangular playable
geometry instead of a perspective camera. Therefore implementation of this
contract alone is **not a pixel-identical or one-to-one visual pass**. Photoreal
rendering, accessibility, physical display/controller operation and measured
sound fidelity retain separate acceptance evidence.
