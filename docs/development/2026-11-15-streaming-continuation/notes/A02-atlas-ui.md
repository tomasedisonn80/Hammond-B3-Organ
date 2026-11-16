# A02 - atlas pages 085-168 and current UI audit

Agent: `/root/w01_a02`. Wave 1. Date: 15 November 2026.
Read-only production audit; this note is the only edited path. No build, test,
capture, source modification or publication was performed by this worker.

## Source and complete reading coverage

Inspected checkout: `/workspace/scratch/177e78b1ac09/Hammond-B3-Organ`.
Observed HEAD: `4aac394cde4da40906b615573a8779aee2d9a37a`.
Read the entire `AGENTS.md` and `docs/PLAN.md`, including the historical
preservation instructions and current M0-M9 dependency table. Current UI recovery
also used `README.md`'s Native interface and UI/UX section,
`docs/NEXT_STEPS.md`, `docs/reviews/WHOLE_REFERENCE_GALLERY_ADMISSION.md`,
`docs/REFERENCE_REFINEMENT_MATERIALS.md`, and the active canonical paint helpers
in `apps/standalone/InstrumentView.cpp`.

The full assigned text extraction `/workspace/scratch/177e78b1ac09/atlas-085-168.txt`
was read continuously, with no omitted page or omitted line: lines 1-260,
261-1000, 1001-1740, 1741-2480, 2481-3220, 3221-3960, 3961-4700,
and 4701-4918. It contains 214,516 bytes and all 84 numbered pages.
SHA-256: `62f2426d7650c7b60676b61091b0dbfc56b628f0a6aa266210ad8e793aae5857`.
This is full textual coverage, not a claim that every illustration on these
pages was independently visually inspected or every external citation verified.

| Pages | Content read and consequence for development |
| --- | --- |
| 085-090 | Mechanical residuals: distinguish angular timing, transverse pickup gap, hum, scanner and Leslie motion. Shared drive/shaft/source phase persists during silence and note changes. Modulation depths and specimen correlations remain unmeasured. |
| 091-096 | Calibration schema: observations, model profiles, compiled banks and playback histories are distinct. IDs, units, null unknowns, waveform observation boundaries, revision conflicts and original bytes remain explicit. Invalid loading must retain the prior valid state. |
| 097-102 | All 549 manual routes and foldback: key/tone/terminal/storage identities are distinct. Repeated upper folding and independent pedal mapping are mandatory. Colliding source IDs share waveform phase while contacts retain independent history. |
| 103-108 | Shared source field and lifecycle: evaluate 91 sources once per common instant; note/preset changes do not reset phase. Sample-rate preparation preserves phase under its declared policy. Zero-sample calls do not advance time. Oracle, bandwidth, runtime cost and hardware accuracy require separate evidence. |
| 109-114 | Drawbars and mixing: 0 is silent, 8 is full; nominal 3 dB gains are not measured tap laws. Coherent branches sum amplitudes, with no polyphony normalization. Preserve loaded branches, inactive banks, transformer ownership and linear baseline. |
| 115-120 | Contact timing and click: nine histories per key, shared gesture causes, separate make/break behavior, fractional edge time, stable ties and sustained-gain independence from velocity. Resolve switching before bandwidth reduction, retain correction/filter tails across blocks, and measure latency and cost. |
| 121-126 | Preset latches and matrices: Cancel releases registration without resetting notes/phases; A#/B exposes retained banks. Physical multi-latch behavior is separate from ordinary exclusive selection. Upper-B percussion interlock follows topology/history. User patches and exact runtime checkpoints have different meanings. |
| 127-132 | Shared percussion trigger: detector follows the upper 1-foot keying contact, not audible gain or a per-note envelope. Duplicate owners, zero-time off/on and preset transitions preserve elapsed-time history and declared ownership semantics. |
| 133-138 | Percussion circuit: revision-qualified AO-28 parts, shared selected-harmonic source, sustained return, normal attenuation, fast bias and decay have distinct owners. Isolated RC products are not audible decay measurements. |
| 139-144 | Pedals: 25 notes, eight contact positions, four buses and two mixtures consume the same source field. Preserve 195 connected entries and five nulls, independent repeated-source contacts, and explicit reactor/load/spectrum unknowns. |
| 145-150 | Expression: controller calibration, mechanical travel, capacitive electrical transfer and monitoring gain are separate. Preserve history during gestures; moving capacitance includes a charge derivative term. No downstream EQ or gain may duplicate the same physical network. |
| 151-156 | Console/MIDI state: one applied audio-owned state, input-origin ownership, saved release destinations, deterministic tie rules, distinct channel-mode semantics, and separate patch/checkpoint files. UI snapshots remain read-only observations. |
| 157-162 | Scanner line: 18L/18C/19 output topology, SI units, common-return loading, independent AC/runtime solvers and persistent energy states. Same-Hz response and physical agreement are independent gates. |
| 163-168 | Scanner rotor: 16 physical positions, nine terminals and 19 ladder outputs are distinct. Capacitive overlap is continuous, brushes are a separate output mechanism, and phase runs through silence/bypass. The printed p166 `order` literal contains only 15 entries despite the stated 16-position loop; retain the existing documented erratum rather than copying this pseudocode. |

### Immediate M3 implications

Pages 116-118 require phase to be evaluated at fractional contact edges, including
the derivative discontinuity when an edge falls at a source zero crossing.
An amplitude-step-only correction is insufficient evidence. Independent histories
must remain separate even when several contacts address one folded source.
Preallocated events, persistent filter/correction tails and explicit overflow are
required before a candidate is called streaming.

Page 120 proposes normalized RMS error at most `1e-4` against a converged
high-rate reference after fixing gain and latency. This is a project numerical
target, not a manufacturer specification or a result already obtained. Existing
64-probe admission cannot establish a complete-window grade. Page 119's
synchronized gesture/contact/phase/dry acquisitions remain the physical gate.
Keep the nominal Engine and original ContactBank baseline intact while qualifying
the new standalone streaming module.

## Actual reference and current screenshot inspection

Viewed both complete 1672x941 images with the image viewer, without retouching,
registration or generating a replacement image:

| Image | SHA-256 |
| --- | --- |
| `docs/design/atlas-cover-reference.jpg` | `9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187` |
| `examples/demos/whole-reference-layout-v1/images/play-reference-1672x941.png` | `f554c348a4dc63901726d8e297c0808ee942052a40babccf2333ef8111be3eae` |

The current screenshot already restores the broad composition: performance band,
adjacent drawbar racks, two full manuals and cabinet. The main title placement is
close. The cabinet artwork is already the exact admitted decorative crop; it is
not the useful next paint target. The screenshot is a retained source-bound run,
not a new execution by A02.

Concrete remaining visual differences, observed directly:

1. The procedural walnut rails and cheeks behind preset controls show straight
   horizontal striping and flat brown slabs. The reference has varied grain,
   rounded highlights and stronger dark undersides. Its reference cheek crops
   are already present at the outer edges; those should remain unchanged.
2. Charcoal panel faces, rack recesses and rims look flatter and more uniformly
   lit than the reference. Existing gradients and grain are present, but their
   limited directional variation leaves a visibly different material.
3. Natural-key fronts and accidental/cap bevels have harder, thinner edge
   treatment and less depth than the source image. Hit silhouettes, correct
   note counts and existing held/focus ink must remain intact.
4. Section headings are densely set compared with the reference's visibly
   spaced capitals. `reference_heading` uses ordinary serif text without
   tracking; the title's truthful subtitle already implements bounded tracking
   locally. Small status and preset labels are also materially denser, partly
   because the application exposes a larger truthful live inventory.

These observations agree with the existing independent gallery admission.
Literal whole-interface equality remains unmet. The concept contains incorrect
footages, inverted drawbar scale and illustrative/nonfunctional controls; correct
live functions must not be erased to obtain a misleading pixel-equality score.

## Recommended bounded M9 implementation

Take a canonical-only material and heading refinement under a frozen scope.
Production ownership should be limited to the `reference_*` helpers in
`InstrumentView.cpp`; keep the inactive/compact/Flat/Rotary/Service branches and
all model/hit geometry unchanged. Do not duplicate the entire reference image
over live controls or change musical state to mimic the concept.

The most isolated first step is tracked section headings plus revised walnut
rails: add bounded character advance and safe fitting for current truthful
strings, measure matching heading ink at reference size, and use deterministic
bounded local grain and upper-left illumination on exposed rails. Reuse the
existing prepared fonts and primitive drawing; introduce no new dependencies,
font assets or audio-thread work. If panel/key treatment is included, declare
those surfaces and their independent acceptance before changing them.

Acceptance should include genuine same-state old/new native frames at 1672x941
and 1400x820, complete unchanged frames for inactive layouts, output scales
1/1.25/1.5/2, clipping/viewport checks, and the full live control/focus/held-note
inventory. Preserve source, executable, state and pixel hashes. Compare declared
material/text regions against the original and report residuals; containment is
not visual equality. Retain earlier galleries and failed comparisons unchanged.

Useful existing gates to build and run coherently are
`test_standalone_material_acceptance`, `test_standalone_waveform_material`,
`test_standalone_product_visual`, `test_standalone_percussion_raster`,
`test_standalone_scaled_view`, `test_standalone_preset_raster`,
`test_standalone_workspace_raster` and `test_standalone_inspection_raster`, plus
app/input/workspace replay tests for any interaction change. Use
`ctest --test-dir <root-owned-build> --output-on-failure --no-tests=error -R
'test_standalone_(material_acceptance|waveform_material|product_visual|percussion_raster|scaled_view|preset_raster|workspace_raster|inspection_raster)'`
only after root has built that coherent source. Reuse the existing paint
benchmark's warmup/timing protocol if changing draw cost substantially; no
benchmark was run by this worker.

Root then captures the changed application, obtains independent admission,
updates README's actual UI screenshot and remaining-differences text, and records
the exact setup/status/next work before nonforced publication. This audit does
not close physical display, device, accessibility, callback deadline, measured
audio or literal 1:1 gates.
