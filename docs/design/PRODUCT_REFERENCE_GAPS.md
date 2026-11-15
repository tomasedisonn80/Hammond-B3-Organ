# Product interface: reference relation and remaining gaps

Review: 15 November 2026, actual product-continuation worker A34. The current
wide Dimensional painter visibly improves footage/readout legibility, manual
cap depth and the distinction between edited and sounding registration. It
retains the earlier header placement, full manuals, cabinet column and sidebar
pedals. **Literal whole-interface 1:1 equality with the concept remains
unmet.** Local raster acceptance and a passed relative paint-cost budget
do not establish that stronger result.

This review updates the evidence status of
[standalone-wide-legibility-v1](../PRODUCT_VISUAL_REFINEMENT.md); it does not
amend its frozen paint behavior or the
[accepted layout](../REFERENCE_REFINEMENT_LAYOUT.md).

## Evidence actually inspected

A34 directly viewed all four original images below, without editing or
resampling them. SHA-256 values identify the image files, not physical fidelity.

| Input | Size | File SHA-256 | Status |
| --- | --- | --- | --- |
| [Atlas cover/page-409 JPEG](atlas-cover-reference.jpg) | 1672×941 | `9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187` | Original embedded concept image; [provenance](atlas-reference.json). |
| [Historical v5 Play](../../examples/demos/standalone-interface-preview-v5/images/play-reference-1672x941.png) | 1672×941 | `f5bf973c949b71d900572cffba72d617f1f2e61efb640b3e9ce97f90d2c30a19` | Admitted historical capture at `487064d2400b9f39d0ee66ed136a09c9e372379e`; [gallery provenance](../../examples/demos/standalone-interface-preview-v5/provenance.json). |
| Integrator preview `ui-preview/play.png` | 1672×941 | `c727007376ab9067b6c101d852fb2bffdfecf4084e75adf4373138411fd2e21d` | Provisional current native Play output, one Upper held target. |
| Integrator preview `ui-preview/midi.png` | 960×700 | `2678b686c98d81442d4a77608d877ed2541536320c4c6f18a38c590b5696a401` | Provisional current native MIDI overlay; unavailable backend, no held target. |

The two preview inputs are under `/workspace/scratch/5b7d983ac078/`, outside
the published galleries. They are intentionally named as review inputs, not
linked as final evidence. A40's planned product gallery is still pending at
this review. Its admission must provide actual retained files and source/state
bindings before this document or README points to it.

The integrator supplied the following capture-input identities; A34 independently
rehashed the actual current files and found exact matches. This is a byte-identity
check, not an independent rebuild or source-to-executable attestation.

| Input | SHA-256 |
| --- | --- |
| `apps/standalone/main.cpp` | `937b837d4ef4317d02ea2862ac34dc95031c73f0f32719b0924de29f4b721027` |
| `apps/standalone/InstrumentView.cpp` | `3687f96db4490e600d6107e6b39d7b7d568bdeb183f16f6aa397535a5f688567` |
| `/workspace/scratch/5b7d983ac078/build-native/apps/standalone/hammond_standalone` | `7ded143b676e9d51a29549dae12184763042a1f12192f72802db7927fa707852` |

The integrator's subsequent
[capture-input build receipt](../development/2026-11-15-product-continuation/reports/capture-qualified-build.json)
records a successful native target build, 108 production-file identities and
the same executable hash at observed source
`b9d352a82ac1afdec70c76ec5b1987785a37762e`, tree
`b3b8b68e4c1f8312d46962924b5096f4ea10c4d2`. It qualifies the stated build inputs;
it does not turn these previews into new captures at that later commit or admit
the pending gallery.

The current `UiModel.cpp/.h`, `Drawing.cpp/.h` and `FontData.h` also match the
input hashes in [A23's report](../development/2026-11-15-product-continuation/reports/A23-visual-acceptance.json).
The preview diagnostics identify SDL 2.32.10, dummy video/audio and software
rendering. Their file hashes are
`cf28e6d96b1ba25a7eab45ee9f92629cbab86fc5d28198be8c3c9b7765730456`
for `play.json`, and
`bb6db808550b6b3328c704a56807558c4814eb8ec85280c42e5036290250518a`
for `midi.json`. No physical screen, MIDI controller or audio device was
qualified by viewing these files.

The v5 and current Play frames have different musical states: v5 shows Upper
fixed C#, Lower A#, expression 75%, percussion on and held targets 2/1/1;
the current preview shows B/B, expression 100%, percussion off and 1/0/0.
Consequently, this review computes no whole-frame before/after change score,
similarity percentage or apparent paint improvement from their differing
drawbar positions, selected presets or held colors. A23's controlled comparisons
own the fixed-state pixel claims.

## What has improved, and what the measurements establish

The current Play preview shows complete footage above both manual racks,
including the correct `1 3/5'`, larger caps at both travel endpoints, distinct
numeric rows below the tracks, and two separate EDIT BANK/SOUNDING rows. The
idle natural tops retain their perspective and have subtle edge lighting;
the stronger held-key marker remains visible. No overlap or crop is apparent
in the two inspected current frames. That observation does not substitute for
the independently executed raster masks or the missing wider capture matrix.

[A23](../development/2026-11-15-product-continuation/notes/A23-visual-acceptance.md)
reports 19,712 checks across 110 paired cases and 336,015,828 pixels: zero escaped
changes, zero numeric-row shadow leaks, 1,296 cap measurements, 8,717 complete
literal glyphs and 34 byte-identical compact/Flat/hidden pairs. It exercises
all nine values, both manuals/banks, fixed/adjustable/Cancel states, pending and
focus cues, fractional dimensions, four output scales and clipped/offset views.
These results support the scoped implementation and preservation rules; they
are not a percentage match to the concept or a general accessibility result.

[A27's six paired timing cases](../development/2026-11-15-product-continuation/reports/A27-paint-performance.json)
pass the declared local regression threshold of growth exceeding **both 15%
and 2 ms**. The largest median increase is 1.380 ms / 1.228%. Current wide
software medians remain **112.441–113.713 ms**, with p95 **127.045–131.616 ms**.
This evidence does not establish 60 fps, native display response, vsync behavior
or audio deadlines. The separate observer saw no added C++ allocation/free calls
in the sampled paint paths; it does not cover arbitrary C allocation, other
threads, GPU resources or leak freedom.

### Header: inherited improvement, independently remeasured

Using the original 1672×941 images, A34 selected warm light pixels with
`R >= 130`, `G >= 105`, `R >= G`, `B <= 0.9*R`. The half-open title region is
`[590,10,1080,65]`, excluding the concept's side rules; the subtitle region is
`[590,65,1100,90]`. Bounding boxes below use pixel coordinates without image
registration, scaling or adjustment for the result.

| Ink region | Reference box / size | Current Play box / size | Historical v5 |
| --- | --- | --- | --- |
| Title | `[603,20,1067,53]` / 464×33 | `[602,20,1065,53]` / 463×33 | Same box and identical pixels to current within the title region. |
| Subtitle | `[650,71,1021,83]` / 371×12 | `[650,71,1020,83]` / 370×12 | Same box and identical pixels to current within the subtitle region. |

The title is already close in footprint and vertical position. The reference
title's highlight and stroke appearance still differ; equal bounds would not
establish equal lettering. The subtitle intentionally reads **NOMINAL DRY ORGAN**,
so its matching visual hierarchy is not matching glyph content. The older
[v3 review](../reviews/REFERENCE_REFINEMENT_VISUAL.md) remains evidence for its
named source: its title-size proposal has already been implemented in the later
header and should not be repeated as unfinished work.

### Composition: retained geometry with explicit differences

Native coordinates below are the accepted logical allocations, checked against
the unchanged current layout inputs and the viewed preview. The reference
coordinates remain approximate visual landmarks from the
[source comparison](../reviews/REFERENCE_REFINEMENT_VISUAL.md),
not a new independent geometry extraction or measured instrument dimensions.

| Landmark at 1672×941 | Reference | Current native allocation | Consequence |
| --- | ---: | ---: | --- |
| Cabinet panel left | x1125 ±2 | x1124.831 | Close column alignment is already retained. |
| Upper playing-key span | y548–692 ±2 | y542.760–686.880 | Nearly the reference depth, about five pixels higher. |
| Lower playing-key span | y720–867 ±3 | y726.880–871.000 | Starts about seven pixels lower. |
| Drawbar-rack span | y267–509 ±2 | y240.920–472.760 | Racks remain higher and shorter; local cap growth does not change this allocation. |

The application reserves space for expression and pedal mixtures, the computer
keyboard toolbar, full preset rails, actual device status and the pedalboard.
Changing these spans requires a separately reviewed geometry contract and shared
hit/paint verification. It is outside this completed paint slice.

## Remaining visual gaps and required distinctions

| Area | Current observed relation to the concept | Action or retained boundary |
| --- | --- | --- |
| Manual racks | The larger caps and readable complete legends improve local hierarchy. Track wells remain separate hard-edged rectangles; the source has more continuous recess shading and softer cap highlights. | A later material candidate may refine local lighting only after a measured proposal, preserving centers, endpoint separation, full text and focus. Do not imitate the concept's incorrect footage or reverse the working travel. |
| Manual keys | Correct full manuals have narrower individual keys than the concept. The top bands are now implemented, but the repeated outlines and top/front transitions still look more uniform. | Preserve 61 keys per manual and the shared projected quads. Assess any future edge/front treatment in matched idle/held/focused states; additional bevel work requires its own containment, contrast and cost evidence. |
| Deck and panel rims | The live charcoal surfaces and thin brass frames read flatter and more regular than the source's softly varied matte deck and broader bevels. | This is the clearest remaining bounded material candidate after the current gallery gate. Compare deterministic fine grain and restrained rim-light transitions in existing interiors; retain text plates and the existing grain/work budgets. No assets or new painter are authorized by this review. |
| Utility and performance rows | Save/Load/Help, Audio/MIDI/Panic/Flat, expression and pedal mixtures occupy areas that the concept uses for a preset selector, gear and scanner tablets. | Preserve working utilities and honest unavailable state. Unsupported scanner, microphone, Stop or cabinet-speed controls must not appear functional to satisfy resemblance. |
| Presets, cabinet and pedals | The source has three tablets beside each manual and mic/speed furniture beneath its cabinet. The app shows 24 reversed preset keys, a status card and all 25 pedals. | These are deliberate differences required by real inventory and current model availability. Cabinet artwork remains decorative; the visible microphones and rotors establish no connected audio model. |
| Small operational text | Wide rack labels are improved; preset legends, sidebar status, keyboard hints and minimum-size modal helper text remain visually small. The active refinement leaves compact/Flat paths unchanged. | Complete glyphs and no crop establish fit, not comfortable reading. Make minimum/default-size native-display usability the next typography gate before adding decoration. |
| MIDI overlay | At 960×700, endpoint fields 10/115 and INVERTED, channel fields, Apply/Disconnect and focus fit visibly. Status says MIDI unavailable and active calibration none (inactive). | This is a separate product dialog without a concept counterpart. The image proves neither a working controller nor a successful Apply/reconnect. Compare configured/selected/active states through their independent functional evidence and new gallery cases. |

The atlas's pp.409/411/431 explicitly separate concept direction from incorrect
counts, legends and controls, as retained by the
[A05](../development/2026-11-15-product-continuation/notes/A05-atlas-visual.md) and
[A06](../development/2026-11-15-product-continuation/notes/A06-atlas-product.md)
page reviews. Preserve **61 Upper + 61 Lower + 25 pedal playing keys = 147**,
**24 presets**, and **68 ordinary controls including those presets**; presets
are not an additional 24 on top of 68. Preserve 71 Play/ten common focus stops,
47 sound parameters, state4/readers 1–3, correct footage and 0-at-top/8-toward-player
drawbar direction. Artwork cannot replace these live controls or their meanings.

## Next UI gates

1. **Admit the current product gallery.** Freeze coherent source, executable,
   dependencies, controls, copied state and per-image diagnostics. Capture actual
   reference/default/minimum Play, Flat, and the separate MIDI overlay; include
   current Rotary/Service views where the gallery claims those workspaces.
   Inspect every original lossless image for complete inventory, footprint,
   readable route/focus/pending cues, and truthful backend/model status. Preserve
   v1–v5 unchanged. Add final gallery links and refresh README only after admission;
   the two previews above do not close this gate.
2. **Qualify displayed usability and response.** On an identified native window
   and display/DPI, read the smallest preset/status/helper text, edit a drawbar
   through 0/8, distinguish EDIT from SOUNDING while pending, traverse focus,
   resize with held owners, use Flat and inspect MIDI calibration states. Record
   actual text/target problems and frame/input observations. Keep unavailable
   hardware explicit. Adopt any absolute response target before grading it;
   A27's relative software budget supplies no interactive frame-rate promise.
3. **Freeze one further material candidate only after those results.** Prioritize
   the deck/rim lighting difference above; leave layout, header placement,
   inventory, state and existing applied-state cues intact. Specify changed
   regions, deterministic work/texture/allocation limits and a fixed-state
   before/after oracle before implementation. Retain independent containment,
   contrast and 30/300 timing checks, followed by fresh current captures. If the
   display review instead finds small-text failures, prioritize a separately
   authorized compact typography treatment over added surface detail.

No new build, application launch, broad test, hardware observation or publication
was performed by A34. This review closes a documentation/evidence-comparison
task; final gallery acceptance, literal image equality, semantic accessibility,
physical MIDI/audio and instrument/cabinet fidelity remain separately evidenced
product gates.
