# Product interface: reference relation and remaining gaps

**Current review: 15 November 2026, A54.** The eleven actual native product
captures are admitted and the README displays current Play and MIDI images.
The wide Dimensional painter improves footage, cap depth and edited versus
sounding registration. **The user's requested whole-interface 1:1 result
remains unmet.** Gallery admission, exact scoped raster checks and successful
platform jobs do not close that requirement or waive the remaining differences.

A54 personally viewed the original atlas JPEG and all eleven current PNGs.
The [current UI acceptance](../reviews/PRODUCT_UI_ACCEPTANCE.md) lists each
original image and its observations. No new recapture-blocking crop or field
collision was found. This updates the evidence and gap record; the
[paint contract](../PRODUCT_VISUAL_REFINEMENT.md) and
[layout contract](../REFERENCE_REFINEMENT_LAYOUT.md) retain their frozen behavior.

## Current evidence and exact source

| Evidence | Observed result and boundary |
| --- | --- |
| [Original cover/page-409 JPEG](atlas-cover-reference.jpg), 1672×941 | Unaltered embedded concept image, SHA-256 `9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187`; [provenance](atlas-reference.json). Design direction, not measured instrument geometry. |
| [Current eight-view gallery](../../examples/demos/standalone-product-preview-v1/README.md) and [three MIDI views](../../examples/demos/standalone-product-preview-v1/midi-overlay/README.md) | Actual captures at `d556da017ea0a5d4f2d231416782dbc5066e58c2`, tree `a3150fd2489a50a430b02c01eadd5e0c180bc7f9`. They supersede A34's temporary previews as the current gallery. |
| [A41 independent admission](../reviews/PRODUCT_GALLERY_ADMISSION.md) | All eleven PNG/pixel identities, 39 normal plus 18 modal payload entries, 108 production inputs and 13 selected build inputs admitted. Original BMP intermediates are unavailable; retained PNGs match recorded native-pixel hashes. A54 did not repeat this complete hash/state sweep. |
| [Published source receipt](../development/2026-11-15-product-continuation/reports/gallery-publication.json) | `d8c39f7986746eacc991747153c7dbb012bb9a32`, tree `edf67b978f93e8dbea6537ce92d3928c171bc1f3`, includes gallery/README, A42 and test/install repairs. Publication does not retag the d556 captures. |
| [A54 direct visual review](../reviews/PRODUCT_UI_ACCEPTANCE.md) | All twelve original image files inspected; three freeze-critical inputs rehashed below. No rebuild, runtime journey, new capture or physical-display observation. |

Current production identities remain unchanged; A54 rehashed only these three
inputs, not the whole admitted gallery:

| Input | SHA-256 |
| --- | --- |
| `apps/standalone/main.cpp` | `937b837d4ef4317d02ea2862ac34dc95031c73f0f32719b0924de29f4b721027` |
| `apps/standalone/InstrumentView.cpp` | `3687f96db4490e600d6107e6b39d7b7d568bdeb183f16f6aa397535a5f688567` |
| `/workspace/scratch/5b7d983ac078/build-native/apps/standalone/hammond_standalone` | `7ded143b676e9d51a29549dae12184763042a1f12192f72802db7927fa707852` |

The [capture-input build receipt](../development/2026-11-15-product-continuation/reports/capture-qualified-build.json)
records an earlier b9 target build. A41 verified matching production inputs and
binary; its older standalone CMake-rule hash predates later test-only changes.
It is not a complete later build-rule attestation. Gallery frames use Linux
Release, SDL 2.32.10 dummy audio/video, software rendering, equal logical/drawable
dimensions and MIDI backend OFF.

Normal frames retain Upper 60/64, Lower 67 and pedal 3 while editing retained
Upper B 16-foot 7→8; Upper fixed C# and Lower A# remain the sounding routes.
Modal frames show selected/configured **20/100/Inverted**, active calibration
none, MIDI unavailable and Direction focused. Earlier UI owners were released
on modal entry. These final images do not show pending edits, staged/configured
divergence, Apply/reconnect or active hardware; separate functional fixtures
retain their own executed claims.

## What the measurements and platform jobs establish

| Acceptance | Actual result | Limit |
| --- | --- | --- |
| [A23 controlled comparison](../development/2026-11-15-product-continuation/reports/A23-visual-acceptance.json) | 19,712 checks, 110 paired cases and 336,015,828 pixels; zero escaped changes/readout-shadow leaks, 1,296 cap measurements, 8,717 complete literal glyphs and 34 identical compact/Flat/hidden pairs. | Scoped containment across fixed states, extrema, pending/focus, scale and clipping. No whole-reference similarity score or displayed-readability result. |
| [A42 modal material acceptance](../development/2026-11-15-product-continuation/reports/A42-calibration-modal-raster.json) | **1,293/1,293 assertions, 109 frames, 6.63 s** locally: 901 original + 170 header + 222 modal assertions. All 212 clipping differences exactly match literal plates within 38 boundary-crossing glyphs; zero unexplained pixels/literal mismatches. | Original failures and exact final oracle retained. No numeric tolerance or whole-textbox exclusion; no contrast-standard or semantic-accessibility result. |
| [Linux primary audit](../reviews/PRODUCT_LINUX_HOSTED_REVIEW.md) | At d8: native Release **48/48 MIDI ON and 48/48 OFF**, native sanitizers **21/21**; material records retain **1,293 checks / 109 frames**. | Compiled native support and dummy-driver/software fixtures. Original d556 sanitizer build failure remains retained. |
| [Windows primary audit](../reviews/PRODUCT_WINDOWS_HOSTED_REVIEW.md) | At d8: MSVC x64 native Release **48/48**, **1,293 checks / 109 frames**, installed MIDI-ON/WinMM workflow passes. | Dummy runtime; no physical WinMM/display, MinGW or Windows sanitizer result. |
| [macOS primary audit](../reviews/PRODUCT_MACOS_HOSTED_REVIEW.md) | At d8: AppleClang arm64 native Release **48/48**, **1,293 checks / 109 frames**, installed CoreMIDI workflow passes. | Dummy runtime; no native Retina/display/controller or macOS sanitizer result. |
| [Root's later coherent local run](../development/2026-11-15-product-continuation/reports/wave8-full-ctest.txt) | **180/180 in 507.55 s**, after A46/A48 checker/plot repairs over d8. | Separate local inputs from d8's hosted source; no new capture, device or 1:1 result. |

[A27's six paired timing cases](../development/2026-11-15-product-continuation/reports/A27-paint-performance.json)
pass the regression threshold of growth exceeding **both 15% and 2 ms**.
Largest median increase is 1.380 ms / 1.228%. Absolute wide software medians
remain **112.441–113.713 ms**, p95 **127.045–131.616 ms**. These are not 60-fps,
display-response, vsync or audio-deadline results. The separate observer found
no added C++ allocation/free calls in sampled paint paths; its scope excludes
arbitrary C allocation, other threads, GPU resources and leak freedom.

### Header: inherited improvement, already measured

A34 measured original 1672×941 images with warm-light thresholds
`R >= 130`, `G >= 105`, `R >= G`, `B <= 0.9*R`; title region
`[590,10,1080,65]`, subtitle region `[590,65,1100,90]`. A41 repeated this bounded
measurement on admitted current Play. A54 did not rerun it.

| Ink region | Reference box / size | Current native box / size |
| --- | --- | --- |
| Title | `[603,20,1067,53]` / 464×33 | `[602,20,1065,53]` / 463×33 |
| Subtitle | `[650,71,1021,83]` / 371×12 | `[650,71,1020,83]` / 370×12 |

Title footprint and vertical position are already close. Native stroke/highlight
treatment still looks less full than the reference; equal bounds would not
establish equal lettering. The correct **NOMINAL DRY ORGAN** subtitle has
different glyph content. The older
[v3 title-size proposal](../reviews/REFERENCE_REFINEMENT_VISUAL.md) is implemented
and is not an outstanding task.

### Composition: current geometry and remaining spatial differences

Native coordinates are unchanged logical allocations from the
[accepted layout](../REFERENCE_REFINEMENT_LAYOUT.md). Reference coordinates
are A34's retained approximate visual landmarks from the
[source comparison](../reviews/REFERENCE_REFINEMENT_VISUAL.md), not new A54
measurements or physical dimensions.

| Landmark at 1672×941 | Reference | Current native allocation | Remaining difference |
| --- | ---: | ---: | --- |
| Cabinet panel left | x1125 ±2 | x1124.831 | Close column alignment retained. |
| Upper playing-key span | y548–692 ±2 | y542.760–686.880 | About five pixels higher. |
| Lower playing-key span | y720–867 ±3 | y726.880–871.000 | Starts about seven pixels lower. |
| Drawbar-rack span | y267–509 ±2 | y240.920–472.760 | Higher and shorter; larger caps did not change this allocation. |

The app also reserves expression/pedal mixtures, keyboard tools, complete
preset rails, device status and all pedals. At 960×700 and 1280×900, pedals move
below the manuals and the cabinet column is omitted. These are responsive
product arrangements, not matched-size replicas of the single 1672×941 concept.
Changing spans requires a reviewed geometry proposal and shared hit/paint checks.

## Remaining visual and UX gaps

| Area | A54's current observation | Required next evidence or boundary |
| --- | --- | --- |
| Manual racks | Complete footage, 32-pixel wide caps and distinct EDIT BANK/SOUNDING rows are visible. Separate hard-edged black wells and uniform highlights differ from continuous recessed shading in the concept. | Preserve centers, 0/8 separation, complete text and focus in any local material proposal. Rack relocation is a separate geometry change. |
| Manual keys | Full 61-key manuals have narrower keys; repeated top/front transitions and dark accidental edges are more regular than the reference. Minimum Dimensional manuals are shallow; Flat has rectangular boundaries. | Preserve 61+61+25 keys and shared projected quads. Review idle/held/focused endpoints and front contrast before accepting another bevel treatment. |
| Deck, rims and walnut framing | Charcoal plates, narrow brass outlines and repeated straight edges look flatter than the source's broader bevels and varied matte/recess lighting. Lower wood rails differ in emphasis. | Deck/rim lighting remains the clearest bounded material candidate after displayed usability. Freeze regions, work/texture/allocation limits and a fixed-state oracle first. |
| Typography and hierarchy | Header size is close but stroke/highlight differs. Preset legends, footer hints, edit/sounding details, minimum Service evidence rows and MIDI helpers are small. Service bank memories wrap at minimum size. | Assess actual minimum/default-size reading on an identified display/DPI. Fit and no crop do not establish comfortable reading; prioritize observed text failures before decoration. |
| Contrast and state cues | Cyan focus, warm held markers and explicit state words are visible. Muted helper/evidence text sits on dark plates; apparent readability depends on scale. | No current standard-level text/nontext contrast, target-size or low-vision result exists. Assess default, selected, pending, focused, unavailable and error states with textual meaning intact. |
| Utilities, presets and cabinet furniture | Save/Load/Help, Audio/MIDI/Panic/Flat, expression/mixtures, 24 reversed presets and status/pedals occupy areas used differently in the concept. Rotary/Service show read-only model facts. | Preserve real functions and unavailable state. Do not remove controls or add fake scanner, microphone, Stop or speed controls to claim resemblance. These remain recorded 1:1 differences. |
| MIDI dialog | Minimum Dimensional and Flat show 20/100/Inverted, channels/actions and Direction focus. Both helper rows and Close fit; backend unavailable and active calibration none are explicit. | No concept counterpart. Static inactive captures do not prove staged/configured divergence, Apply/reconnect or controller behavior; native-device journeys remain separate from synchronous fixtures. |
| Accessibility and response | Keyboard focus is visible and three-platform software tests pass. The images provide no semantic accessibility or real display/input-response journey. | Specify a platform semantic bridge and actual screen-reader journey. Adopt an absolute response criterion before measuring; retain the ~113 ms software result and avoid a 60-fps claim. |

Atlas pp.409/411/431 separate art direction from incorrect concept counts,
legends and controls; see retained
[A05](../development/2026-11-15-product-continuation/notes/A05-atlas-visual.md) and
[A06](../development/2026-11-15-product-continuation/notes/A06-atlas-product.md)
page reviews. Preserve **147 playing keys = 61 Upper + 61 Lower + 25 pedals**,
**68 ordinary controls including 24 presets**, **71 Play / ten common focus
stops**, and **eleven separate MIDI-modal stops**. Preserve correct `1 3/5'`
footage, **0 at the top / 8 toward the player**, 47 sound parameters,
`B3CONTROLS4` and readers 1–3. These correctness constraints do not waive the
user's 1:1 objective or authorize calling the present result equal.

## Next UI gates

1. **Qualify displayed usability and response on an identified native window.**
   Use frozen production inputs and record OS, backend, display/DPI, logical/
   drawable sizes and build. Inspect 960×700, 1280×900, 1672×941 and Flat. Read
   preset/footage, EDIT/SOUNDING, footer, Service and MIDI helper/error text;
   edit through 0/8, traverse 71/10/11 focus sets in both directions, and resize
   across 1400×820 with held owners. Include off-window release, fresh press and
   deliberate focus loss. Retain actual frames, input/paint timing, final owners
   and numeric shutdown. Declare an absolute response criterion before grading.
   Physical MIDI/audio and accessibility need their own identified observations.
2. **Freeze the next change against those findings.** If small text fails,
   prioritize scoped compact typography/contrast. Otherwise propose one deck/rim
   treatment with fixed-state crops, containment, contrast, allocation and 30/300
   timing checks. Production remains frozen; this review authorizes no painter/
   layout edit or recapture.
3. **Repeat the reference comparison after the accepted change.** Preserve the
   atlas and correct live inventory; capture the changed app at source-bound
   matched sizes/states, admit images independently and update README. Track
   spatial, material and type differences above. No similarity percentage or
   literal 1:1 claim is accepted without a declared comparison and actual result.

The capture/admission/README gate is **complete** for current frozen production.
A54 executed no build, CTest, app, browser or device session. This closes direct
image and documentation acceptance only; displayed usability, accessibility,
physical devices, timing and whole-reference equality remain open product gates.

## Historical A34 inputs — superseded for the current gallery

A34's [original note](../development/2026-11-15-product-continuation/notes/A34-reference-gap-review.md)
preserves its source/time and preview-only scope. It viewed the atlas,
[historical v5 Play](../../examples/demos/standalone-interface-preview-v5/images/play-reference-1672x941.png)
and two temporary previews under `/workspace/scratch/5b7d983ac078/ui-preview/`.
Their identities remain history:

| A34 input | SHA-256 |
| --- | --- |
| Historical v5 Play at `487064d2400b9f39d0ee66ed136a09c9e372379e` | `f5bf973c949b71d900572cffba72d617f1f2e61efb640b3e9ce97f90d2c30a19` |
| Temporary `play.png` | `c727007376ab9067b6c101d852fb2bffdfecf4084e75adf4373138411fd2e21d` |
| Temporary `midi.png` | `2678b686c98d81442d4a77608d877ed2541536320c4c6f18a38c590b5696a401` |
| Temporary `play.json` | `cf28e6d96b1ba25a7eab45ee9f92629cbab86fc5d28198be8c3c9b7765730456` |
| Temporary `midi.json` | `bb6db808550b6b3328c704a56807558c4814eb8ec85280c42e5036290250518a` |

That Play preview used B/B, expression 100%, percussion off and 1/0/0 held;
v5 used Upper fixed C#, Lower A#, expression 75%, percussion on and 2/1/1.
A34 computed no whole-frame score between different states. Its MIDI preview
showed 10/115/Inverted; admitted current frames show 20/100/Inverted. A34's
header regions were identical between its current and v5 frames. These are not
new A54 inspections of temporary files. No historical gallery was changed.
