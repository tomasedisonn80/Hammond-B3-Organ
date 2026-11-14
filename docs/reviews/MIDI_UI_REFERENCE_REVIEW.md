# A21 — Independent native reference and visual acceptance review

Date: 2026-11-14. Actual worker: `/root/w04_a21_visual_acceptance`, MIDI/UI
wave 4, assignment 21. This review covers the A17 native captures and their
identified renderer/layout source. It does not qualify a later build.

## Decision

The captured application implements the reference's recognizable arrangement:
walnut sides, dark panels with brass edges, neighboring drawbar racks, stacked
manuals, and a cabinet at the right when there is room. All 46 ordinary player
controls have independent dynamic paint and shared hit geometry; the observed
key inventory is 61 + 61 manual keys and 25 pedals. The cabinet caption and
unavailable-processing labels are truthful and must be retained.

**The text-legibility gate remains open.** At the minimum size, parts of the
MIDI refresh instructions, keyboard help and footer disappear in the actual
raster. The narrow-glyph failure has a specific source and pixel explanation
below. This is not merely a preference for larger type.

**The one-to-one appearance goal is not met.** Comparison with the exact source
shows different panel proportions, materials, key perspective, typography and
lower-right content. Some differences deliberately correct the concept's
engineering mistakes or expose real controls. Passing the layout contract does
not establish photographic or pixel identity.

## Evidence and identity

Read the [layout contract](../REFERENCE_UI_DESIGN.md),
[asset contract](../REFERENCE_ART_ASSETS.md),
[A17 rendering/capture record](../development/2026-11-14-midi-ui/17-reference-renderer.md)
and relevant source. Opened the original
[1672 × 941 reference JPEG](../design/atlas-cover-reference.jpg) and all four
actual native PNGs with the image viewer. The JPEG SHA-256 is
`9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187`.
It is generated concept art retained from the atlas, not a photographed
instrument or an application screenshot.

The reviewed capture directory is
`/workspace/scratch/cd4bd06ce68f/a17-render-checks/`; its
`capture-record.json` retains full commands, source and binary hashes, both
dummy driver selections, exit codes and original diagnostics. A28 owns durable
capture-bundle publication. These names and hashes identify the evidence until
that bundle supplies repository links.

| Actual image | PNG SHA-256 | Recorded result |
|---|---|---|
| `native-1672x941.png` | `87ce06e8b791cb6041a87c7d4ae211a4f6a46daaa6054f2ff949b75178036755` | 800 ms smoke, exit 0; held note and release observed |
| `native-1280x900.png` | `0460093e4b216a50bfcc856a8d48f56678e7628cd131f3a0b189461cae5543d6` | 800 ms smoke, exit 0; held note and release observed |
| `native-960x700.png` | `bf722384d52ed70e71d8f246a51eee75bd056e6fc312db90543ec4071451f503` | 800 ms smoke, exit 0; held note and release observed |
| `native-960x700-midi.png` | `668263c830ce88e135257f7781fe6f2407edfa0ae94fd0ca3e6eaa3f741ba352` | Error-state capture; replay exit 1, **not passed** |

A21 independently rehashed all four PNGs and decoded RGBA arrays; each matched
the record and advertised dimensions. The current seven recorded
`Drawing`/`InstrumentView`/`UiModel`/`main` source files, reference JPEG and art
manifest also matched the recorded hashes when inspected. The binary rehash
matched `072f52ad299592f997af2aaeb2a140a3417e4a77542dd6afbfbae9fd4a60eb4b`.
Checkout HEAD was `7b36cfac2565397191b3df5e07112611e7f1b0e1`, with concurrent
uncommitted MIDI/UI work; HEAD alone does not identify these native pixels.

The diagnostics identify SDL 2.32.10, the software renderer, matching logical
and drawable dimensions, and dummy video/audio. The MIDI error is the missing
ALSA sequencer, `MidiInAlsa::initialize: error creating ALSA sequencer client
object.` All 18 modal replay events were delivered and the final acknowledgment
was observed, but `replay.passed` is false and the application records two
errors. The earlier rejected replay `M` key remains an independent recorded
failure. No physical audio, MIDI controller, display or latency pass follows.

## Composition, proportions and materials

The following native measurements come from the matching shared layout source,
cross-checked against the visible boundaries. They are logical units at the
observed 1:1 drawable scale, with fractional raster edges rounded by SDL.

| Region | 1672 × 941 | 1280 × 900 | 960 × 700 |
|---|---|---|---|
| Player width | 1059.75 | 1248 | 928 |
| Drawbar row top / height | 230.92 / 225.84 | 214 / 216 | 190 / 168 |
| Upper manual panel `(x,y,w,h)` | `(237.90,504.76,893.75,138.48)` | `(180,474,1084,138)` | `(16,402,928,82)` |
| Lower manual panel top | 653.24 | 620 | 492 |
| One natural playing key, width × height | 24.38 × 108.48 | 29.67 × 108 | 25.33 × 52 |
| One accidental playing key, width × height | 14.63 × 67.26 | 17.80 × 66.96 | 15.20 × 32.24 |
| Pedal panel top / height | 801.72 / 77.28 | 766 / 74 | 582 / 58 |
| Footer top / height | 889 / 36 | 848 / 36 | 648 / 36 |
| Cabinet / manual bank cheeks | Both visible | Cabinet absent; cheeks visible | Both absent; bank buttons in racks |

At reference size, the cabinet art uses destination
`(1153.64,154,434.46,370.13)`, versus its exact source crop
`(1132,174,466,397)`: a uniform 0.9323 scale, approximately 21.64 units right
and 20 units up. Its 466:397 aspect is preserved. The original lower-right
microphone knobs and rotary-speed tablets are absent; the app uses that area
for `CABINET REFERENCE`, `ROTARY AUDIO NOT CONNECTED`, and factual device status.
Those substitutions are required by the current model boundary.

The source's upper manual occupies approximately y=530–697 and lower manual
y=710–869, with perspective key fronts. Native panels start around y=505 and
653 and are shorter, leaving an actual pedalboard at y=802. The source contains
no corresponding visible 25-pedal row. Moving the app's lower manual down to
imitate the image would consume that required playing surface. Its rectangular
key planes also intentionally preserve tested hit geometry rather than copying
the concept's perspective and inaccurate key inventory.

The remaining material differences are visible even at matched 1672 × 941
size. The source has irregular wood grain, rounded polished edges, shaded
metal and more substantial key/tablet depth. Native metal is a smooth vertical
gradient with narrow outlines; caps and key fronts use small, regular bands.
The original left 24-pixel decorative strip is expanded to 71.90 units,
approximately **3.00× horizontally**, while the right 68-pixel strip expands
only **1.06×**. This makes the left grain/edge conspicuously broader. The thin
procedural lower rail also differs from the source's large curved wooden base.
These are real residuals, not evidence of a broken control layout.

The serif title and brass headings retain the source's visual hierarchy, but
the DejaVu face, compact tracking, smaller secondary captions and repeated
thin panel borders differ from the concept. Preserve `NOMINAL DRY ORGAN`;
replacing it with the source's promotional subtitle would remove useful scope
information. The unconnected cabinet photograph remains more detailed than
the procedural interactive surface, so the combined view is not yet a uniform
photoreal treatment.

## Dynamic controls and corrected musical information

`paint_controls` iterates every entry of `layout.controls`; it has no image
replacement for any control. `paint_instrument` paints all manual/pedal keys
from their shared rectangles and the copied applied held state. Selection and
cyan focus are separate paint. This is a source-to-render inventory check,
not a claim that A21 independently activated every action at runtime.

| Interactive family | Count | Reviewed dynamic source |
|---|---:|---|
| SAVE, LOAD, HELP, AUDIO, MIDI, PANIC | 6 | Shared control IDs, live actions and focus; separately painted labels/tablets |
| EDIT A/B, PLAY A/B, CANCEL for each manual | 10 | Edited bank uses desired UI identity; sounding bank/Cancel use acknowledged applied route |
| Visible manual drawbars | 18 | Current editor bank values, corrected footage, cap position, numeric value and focus |
| Percussion tablets | 4 | Enabled, harmonic, volume and decay values from the copied controls |
| Nominal expression and pedal mixtures | 3 | Actual expression and two mixture values, tracks, caps/readouts and focus |
| Keyboard target and octave controls | 5 | Three target states, two octave actions and current octave caption |
| **Ordinary player controls** | **46** | Shared paint/hit geometry; separate from the 45 public parameters |
| Upper / lower playing keys | 61 + 61 | Applied held state and roving focus; natural paint first, accidental hit precedence |
| Pedals | 25 | Applied held state and roving focus; no decorative substitute |

A pixel scan independently counted the visible light spans below accidentals
and dark accidental spans near their tops. Each of the three player images
contains **36 light + 25 dark spans per manual, and 15 light + 10 dark spans
for pedals**. The scan classified red-channel values above/below 100 inside
the known playing rectangle and excluded runs shorter than four pixels to
avoid key dividers. For the minimum image the natural/accidental scan rows
were upper y=467/427, lower y=557/517 and pedals y=627/607, x=24–935.
The source key generator independently confirms the same inventory and
61-note MIDI 36–96 / 25 one-based pedal identities.

The actual footage sequence remains `16'`, `5 1/3'`, `8'`, `4'`, `2 2/3'`,
`2'`, `1 3/5'`, `1 1/3'`, `1'`. Zero caps are at the upper/inward end and
eight at the lower/outward end. Do not restore the concept's incorrect
footages, reversed drawbar numbers, BASS/LOWER/UPPER selectors or key counts
to make an image comparison superficially closer. Keep EDIT distinct from
SOUNDING, Cancel distinct from Panic, and the two mixtures labeled nominal.

Only the three admitted decorative regions are uploaded as reference art.
The source cabinet crop excludes heading/knobs/speed buttons; the left 24-pixel
and right 68-pixel strips exclude control legends. Neither the rejected
72-pixel left crop with BASS fragments nor the DESIGN CONCEPT lower rail is
drawn. The cabinet status card adds no input targets. No baked interactive
control was found in the reviewed paint path or captures.

## MIDI modal order, geometry and truthful state

At minimum size, the shared panel is `(110,90,740,520)` and all eight controls
fit inside it. `main.cpp::modal_rectangles`, `selected_midi_channel`,
`activate_modal`, pointer hit testing, Tab/Shift+Tab and the final focus outline
agree with `midi_overlay_layout` and the renderer's fields:

| Focus index | Visible control | Minimum rectangle `(x,y,w,h)` | Activation |
|---:|---|---|---|
| 0 | Previous port | `(138,203,40,42)` | Previous selection |
| 1 | Next port | `(782,203,40,42)` | Next selection |
| 2 | Upper channel | `(138,329,212,38)` | Channel adjustment |
| 3 | Lower channel | `(374,329,212,38)` | Channel adjustment |
| 4 | Pedal channel | `(610,329,212,38)` | Channel adjustment |
| 5 | APPLY / CONNECT | `(138,514,252,40)` | Submit selected port/route |
| 6 | DISCONNECT | `(406,514,188,40)` | Retire MIDI ownership |
| 7 | CLOSE | `(738,114,84,32)` | Close overlay |

Forward/reverse focus wraps modulo eight. Enter/Space activates; Left/Down
decrement and Right/Up increment selected values; Home/End select endpoints;
Escape closes. Pointer hit testing chooses the same index before activation.
Opening the modal starts at index 0. The retained replay advances through
indices 1, 2, 3, 4 and 5, changes the displayed channels to 2/3/4, and visibly
ends with the cyan outline on Apply. It does **not** activate Apply: recorded
active routing remains 1/2/3 and no MIDI device is connected. Selected values
must not be presented as evidence of an applied connection.

The error wraps within the 684 × 83 status region; it does not overwrite the
channel or action buttons. Port names use a bounded 77-unit region and visible
ellipsis on overflow. The actual error wording remains available and legible
at 11.5-unit text. All main controls are dimmed under the overlay, while the
modal focus is painted last and remains distinct from the gold Apply state.

Two documented interaction residuals remain: there is no explicit Refresh
control despite the design contract, and long exact port names can be elided
under the `INPUT PORT / EXACT NAME` heading. Close/reopen and `--list-midi` are
the current workarounds. ASCII-only font coverage is a separate known limit
for non-ASCII port identities. These limits must not be described as completed
in-modal refresh/full-name inspection.

## P1 — Missing thin glyphs in actual minimum text

This failure was inspected in the original PNG and in nearest-neighbor 3×
inspection crops; enlargement does not recover the missing ink. The
unmodified capture remains the evidence.

| Text region in 960 × 700 | Requested size | Observed defect |
|---|---:|---|
| MIDI refresh instruction, top y=274 | 10.5 | `Close` loses its `l`; `Full` loses its `ll`; several glyphs and hyphens in `--list-midi` vanish |
| MIDI keyboard help, top y=585 | 10.5 | Narrow letters vanish in words such as `selects`, `control` and `closes` |
| Player footer second line, top y=669 | 9.5 | The undimmed registration message loses thin letters in `audition`, `registration` and `Pedals` |

The embedded Sans atlas is rasterized at 32 pixels. Its `l` and `i` glyphs
have three-pixel ink widths; `-` has a three-pixel ink height. At size 10.5,
the corresponding destination extent is `3 × 10.5 / 32 = 0.984375`; at
9.5 it is `0.890625`. `Drawing::text` sends the tightly cropped ink rectangle
directly to `SDL_RenderCopyF`. In this software-renderer capture those
subpixel rectangles disappear. For example, the expected `l` in `Close` has
destination `(146.203,275.969,0.984,7.875)`; its inspected pixel box contains
only panel background, with maximum red value 36, rather than the muted text
color's red value 166. The full source string exists: this is raster loss,
not an omitted character in the help copy.

`make_font` already requests `SDL_ScaleModeLinear`, so recommending that flag
alone does not repair the failure. The same drawing path serves small footer,
bank-state and service-card captions at every window size; the minimum modal
is the clearest reproduced case, not the only text that needs review.

## Prioritized tasks for A29 and integration

### 1. Repair narrow-glyph raster coverage before visual acceptance

Use the existing atlas's **two transparent padding pixels** around each ink
rectangle. Include those pixels in the copied source rectangle and offset the
destination bearing by the same scaled padding, preserving `advance_64` and
the intended text width. This gives narrow ink a nonzero raster destination
without regenerating font assets or inflating glyph advances. Source bounds
must stay inside the guaranteed atlas padding. Prepared size-specific glyphs
are another valid implementation, but a new font/dependency is unnecessary
for this identified defect.

Acceptance must include a real SDL drawing test, using the software renderer
and a known background, rendering **`l`, `i` and `-` individually at 9, 9.5
and 10.5 pixels**. Every glyph must produce nonzero ink; checking only the
combined width or a nonblank sentence would miss the failure. Preserve width
metrics, wrapping and elision. Reinspect the exact minimum modal instructions,
the undimmed footer, the focused Apply border and corrected drawbar labels in
a new source-identified native capture. A shared drawing change also requires
a focused visual comparison of the other two required sizes so previously
readable headings, values and captions are not degraded.

### 2. Close the concrete MIDI affordance gaps with the application owner

Implement the contracted explicit Refresh through the same shared layout,
pointer order and keyboard order; do not paint a button without an action.
Refresh must enumerate without implicitly connecting or altering held-note
ownership. Provide in-modal access to an elided port identity, or accurately
label the displayed name as abbreviated and retain the exact-name limitation.
If controls are added, update the focus count and every index-dependent
activation together. Acceptance needs pointer and Tab/Shift+Tab traversal,
refresh after enumeration changes, and a long-name case whose identity remains
inspectable. No successful physical enumeration can be inferred from the
current ALSA error frame.

### 3. Refine material fidelity within the existing musical geometry

The first bounded material target is the approximately threefold horizontal
stretch of the admitted left wood strip. Retain its control-free source
boundary; use an aspect-preserving placement with a procedural continuation
or another independently inspected text-free region rather than reinstating
the rejected BASS crop. Next, compare the wide drawbar caps and manual fronts
with the source and strengthen their top/front separation inside the existing
hit rectangles. Treat the smooth metal and thin lower rail as remaining
appearance work, not completed source matching. Retain a matched-size
before/after capture and report which of these residuals actually changed.
Do not sacrifice text contrast, 61 + 61 + 25 geometry, the nominal captions
or the factual cabinet card to imitate source pixels.

### 4. Retain the remaining native integration gates

The three static sizes show the expected cabinet/cheek relocation and no
observed control overlap. They do not execute a resize while a gesture or
mixed UI/MIDI notes are held. A15's separately identified headless geometry
and ownership checks are useful evidence, but native 1399/1400-width and
819/820-height transitions, modal return, captured-drag release and renderer
recovery remain distinct capture/interaction work. Coordinate those gates
with their assigned owners rather than relabeling these static images as
transition tests. Actual Help/Audio modal interaction, non-ASCII/full-name
inspection, native screen readers and physical devices also remain outside
this bounded review.

A21 performed no new application run, production edit, source-image edit,
commit or shared-status edit. Independent work here was image inspection,
source/action mapping, byte/pixel identity verification and the stated pixel
measurements. The original failed MIDI replay and all appearance residuals
remain visible.
