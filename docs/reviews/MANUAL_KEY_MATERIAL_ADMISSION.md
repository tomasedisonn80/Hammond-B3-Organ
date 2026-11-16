# Manual key material contract and fixture admission

**A11, runtime/interface continuation, 16 November 2026.** The bounded material
recipe and comparison protocol are admitted for implementation after root
preserves the genuine before executable. The root-owned before fixture build and
16-case default CTest passed in **3.93 seconds**. This is fixture qualification,
not acceptance of a rendered candidate. Literal whole-interface **1:1 remains
open and unwaived**.

## Reviewed boundary and source

Reviewed the complete [contract](../design/MANUAL_KEY_MATERIAL_CONTRACT.md),
standing AGENTS.md and full M0–M9 plan, current scope/checkpoint, A05/A06 findings,
A08's observations, the original reference JPEG and typography-stage actual-app
image. Inspected UiModel geometry/identity, the original reference_key and both
call sites, its band/inset/outline/side helpers, Drawing::quad and PixelRaster.
The nearby keyboard-rim fixture supplied only the established transport and
public-state serialization conventions.

The recovered genuine before source is local
79bf34091dda5dc0528cf584891cff3e09657c66, published by root as
f56b0f3b4ac98dd0f4bce289f9509fdad8e03331. Both have exact tree
b4e5526d3b08ca90fce4c3c152db8459ddd6c4e6. The initial 3520c96 baseline
remains historical. The same fixture source must link against the complete
recovered before painter and candidate; preserve their executable, source, build,
state and pixel identities separately. Pre-typography pixels cannot supply a new
whole-frame baseline.

The idle-manual-only branch, unchanged top/front geometry and paint order,
individual source windows/error screens, unchanged held path and cues,
pedal/preset protection and inactive whole-frame requirements are admitted.
The explicit colors are bounded artistic choices, not measured reflectance,
a recovered lighting model or physical calibration. The primitive ceiling is a
source work bound, not a frame deadline.

## Explicit division identity

UiKeyGeometry::note.target already distinguishes UiTarget::Upper, Lower and
Pedals. Its note.value separately identifies a manual MIDI note or one-based
pedal ID. The original private bool manual argument cannot choose the admitted
Upper/Lower ivory and glint recipes.

Replace that private argument with **UiTarget division**, passing
**key.note.target** at both existing call sites. Derive the manual predicate from
division != UiTarget::Pedals and select Upper/Lower constants by the enum.
Do not infer identity from y coordinates, height, focus, held state or incidental
collection position inside the painter. The fixture verifies every active key's
target, pitch, accidental flag, bounds and all quad vertices independently.
No public model or audio-state API change is required.

## Pre-candidate source-order clarification

A11 found that the old natural painter draws the opaque hit outline and then
overlays its rear recess across some top-outline pixels. The specified recipe
removes that recess. Requiring final equality over the entire geometric old
outline would contradict that specified change.

Root accepted and applied an attributed clarification before any candidate:
protect **final visible unchanged opaque outline ink**. The exact rule is:

1. Construct the original hit-outline quads with unchanged geometry/thickness.
2. Subtract that key's later intentionally editable overlays: ivory front
   highlight, rear recess and idle side bands; or ebony inset outline and glint.
3. Apply later opaque key occlusion in original natural-first/accidental-last
   order.
4. Require exact remaining outline RGBA, and separately source-review unchanged
   outline operations, colors and geometry.

This rule comes from original operations, never candidate pixels. Every
subtraction remains inside that original idle key's actual top/front faces.
Held ownership and final cyan/brass cues stay exact. No dilation, keyboard
rectangle, rim/title exception or changed-pixel fit is admitted.

## Frozen fixture and transport

Source:
[test_standalone_manual_key_material_raster.cpp](../../apps/standalone/native_tests/test_standalone_manual_key_material_raster.cpp).
Protocol: **manual-key-material-v1**, schema 1.

~~~sh
../build-native/apps/standalone/test_standalone_manual_key_material_raster --list
../build-native/apps/standalone/test_standalone_manual_key_material_raster
../build-native/apps/standalone/test_standalone_manual_key_material_raster --case 0
~~~

The list returns exactly 16 detailed, zero-based case specifications. No arguments
execute all assertions, two physical clip companions and four canonical/minimum
same-renderer/fresh-renderer repetitions. A selected case 0–15 performs its
geometry/state/cue/clip assertions, then writes one JSON line immediately followed
by exactly width × height × 4 top-down row-major RGBA8 bytes, with no trailer.
Windows stdout is binary; errors go to stderr with nonzero exit.

Root registered this source plus InstrumentView.cpp, linked
hammond_standalone_drawing and hammond_standalone_support, defined SDL_MAIN_HANDLED
and applied hammond_configure_target. The native timeout is 90 seconds, 240 with
sanitizers. There is no alternate material renderer.

| Contract case / CLI index | Logical size | Renderer scale | Physical origin | Fixed state / requirement |
| --- | --- | --- | --- | --- |
| 01 / 0 | 1672×941 | 1,1 | 0,0 | All idle; Upper Edit Bank B focus |
| 02 / 1 | 1400×820 | 1,1 | 0,0 | All idle; same non-key focus |
| 03 / 2 | 1920×820 | 1,1 | 13,17 | Unequal layout; idle |
| 04 / 3 | 1672×941 | 1.5,2 | 13,17 | Idle; full companion for 11/12 |
| 05 / 4 | 1672×941 | 1,1 | 0,0 | Held Upper 12/13, Lower 48/49, pedals 12/13; Upper 13 focus |
| 06 / 5 | 1672×941 | 1,1 | 0,0 | Idle Upper natural 12 focus |
| 07 / 6 | 1672×941 | 1,1 | 0,0 | Idle Upper accidental 13 focus |
| 08 / 7 | 1400×820 | 1,1 | 0,0 | Idle Lower natural 48 focus |
| 09 / 8 | 1400×820 | 1.5,1.5 | 13,17 | Idle Lower accidental 49 focus |
| 10 / 9 | 1672×941 | 1,1 | 0,0 | All 122 manuals held; Lower 48 focus; whole frame equal |
| 11 / 10 | 1672×941 | 1.5,2 | 13,17 | Crossing enabled physical clip |
| 12 / 11 | 1672×941 | 1.5,2 | 13,17 | Enabled empty physical clip; whole frame equal |
| 13 / 12 | 1399×819 | 1,1 | 0,0 | Compact Dimensional Play; whole frame equal |
| 14 / 13 | 1672×941 | 1,1 | 0,0 | Flat Play; whole frame equal |
| 15 / 14 | 1672×941 | 1,1 | 0,0 | Rotary tab focused; whole frame equal |
| 16 / 15 | 1672×941 | 1,1 | 0,0 | Service tab focused; whole frame equal |

Output dimensions are ceil(logical dimension × renderer scale) plus twice the
absolute physical origin. Cases 04/11/12 output **2534×1916**, viewport
**[13,17,2508,1882]**. Case 11 installs viewport-relative physical clip
**[750,1160,465,560]** at renderer scale one: global half-open extent
**[763,1228) × [1177,1737)**, exactly 260,400 pixels. This is canonical
[500,810) × [580,860) under (1.5,2). Case 12 installs **[750,1160,0,0]**,
preserving enabled-empty semantics.

### Frozen nonmaterial inputs and renderer observations

All four retained banks differ:

- Upper A: 8,0,4,1,2,3,4,5,6; Upper B: 8,6,5,4,3,4,2,5,3.
- Lower A: 4,3,2,1,0,1,2,3,4; Lower B: 0,0,8,0,0,0,0,0,0.
- Selected banks Upper B / Lower A; both routes enabled; no fixed registrations.
  Edited banks B/B. Expression 0.625; pedals 3,7; percussion enabled,
  Second/Normal/Slow.
- Frame clock 38400, sample rate 48000, peak 0.125, prepared/running true,
  publication revision 4. Sequence/recovery/overflow/rejection/discard/fault
  counters zero; core status Ok. Only declared held arrays vary.
- Fixed audio metadata, buffer 512, zero clipping, no modal or input gesture,
  no pending controls, empty device choices, unavailable/unopened MIDI.
  Complete public view, applied/desired state, layout and view-info are serialized.

Incoming blend is BLEND, draw color [17,23,31,127]. Every paint must preserve scale,
physical/logical viewport, physical/logical clip, enabled state and blend.
The existing painter changes draw color; the fixture records its outgoing value.
Paired comparison must require that outgoing value to equal the genuine before
execution, rather than falsely asserting restoration to the incoming color.

## Independent support and visible ownership

The oracle reconstructs all 147 active keys from frozen canonical panels,
0.96/0.95/manual projection, 36/36/15 natural counts, accidental placement and
0.62 depth, original front-depth clamp, and separate binary32 x/y scaling.
It calls no production layout, band, inset, outline or raster helper. Every
active key is checked bit-for-bit against the independent vertices before
qualification.

Coverage uses actual original quad pixel centers, binary32 vertices promoted to
binary64 and the frozen half-open row/span rule, intersected with output,
physical viewport and physical clip. No mask derives from an image or candidate
geometry.

Opaque top/front coverage executes in painter order, replacing earlier ownership.
Thus an idle accidental can legitimately cover an earlier held natural's hit
quad while its remaining exposed held face is protected. Natural focus ink
hidden by later accidentals is not demanded. Brass precedes focus; cyan replaces
brass at their actual intersection. This protects exact final visible cues.

**Editable = 4 is the sole permission bit.** OriginalIdleFace = 2 is only a
historical union. Visible held ownership, focus, brass and unchanged outline
coverage remove editability. Complete pedal/preset panels are marked even outside
an enabled clip. Every case has nonzero protected full-frame exterior; the six
whole-equality cases have zero editable pixels.

Mask JSON contains nonoverlapping half-open runs
[y,x_begin,x_end,flags,owner]. Omitted runs are protected zero-flag exterior.
Owners are Upper 0–60, Lower 61–121, pedals 122–146, or −1. Counts cover each
flag, protected exterior, each key's visible/held/cue pixels and each manual's
editable top/front faces. The paired checker independently reconstructs/verifies
these frozen masks and rejects differing metadata.

Default execution requires exact cyan, brass and remaining opaque hit-outline
RGBA. In every manual-focus case, the complete frame cyan set equals the
independent final visible cue mask, including absence of unexpected cyan.
Every held key has a nonempty visible face and brass cue. Both manuals have
nonempty top and front editability in ordinary active idle/mixed cases, including
the crossing clip. All 147 keys remain visible in unclipped active cases.

Case 11 compares **every visible pixel** with its identical full-clip companion
at the same global position. Both clipped cases require exact walnut clear
outside the clip. The enabled empty clip contains only SDL's documented
full-surface clear. A failure may not enlarge the admitted mask.

## Remaining paired and visual admission

Canonical and minimum cases each emit **72 separate per-key observations**:
both manuals, naturals 12/29/48 and accidentals 13/30/49, six source bands.
Each records RGBA sums/count and exact encoded-Y′ numerator/denominator.
Samples use frozen source-face-normalized v and u in [0.35,0.65), verified on
their visible idle original faces. No key or manual pooling hides a failure.
The default before fixture does not assert new material targets on the original
painter.

The independent paired checker must require equal complete model/geometry,
view-info/case specification, renderer metadata and outgoing state/color;
zero changed channels outside Editable; exact held/pedal/preset/outline/cue
pixels; complete cyan-set equality; and declared whole-frame equality. Retain
input/build/executable/source/state/geometry hashes, changed pixels/channels,
maximum deltas, bounding boxes and per-row changes, with lossless failed frames
and differences. Keep all fixed appearance thresholds unchanged.

The contract's individual-key ivory-front improvement, ebony sheen/front criteria,
ivory-top protection, minimum-size ordering, native-size/detail/full-frame visual
reviews and actual running-app canonical/minimum held/focus captures remain
required. No fixture result establishes real display/DPI/input, accessibility,
physical/audio fidelity, signed release or literal whole-interface 1:1.

## Observed verification and limits

Root's first coherent compile found aggregate-initialization errors in the
independent rectangle/right-outline construction. A11 corrected them with
explicit UiPoint constructors; the original failure log remains retained.
Root then reported a successful coherent rebuild and **16-case default CTest
pass in 3.93 seconds** against the genuine before painter. Root owns original
logs, binary retention, build/source receipts and subsequent comparison.

A11 changed only the fixture, this admission and its session note. No painter,
Drawing, UiModel, CMake, core/audio source or other owner's evidence was edited.
