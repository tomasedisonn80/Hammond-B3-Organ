# A05 — Atlas pp. 337–420 and concrete interface refinement

## Assignment and observed source

- Actual worker: `/root/w01_a05_atlas_interface`, wave 1, A05 of this new reference-refinement session.
- Owned path: this note only. No production edits, build execution, commits, pushes, or child dispatches.
- Inspected repository HEAD: `8bd999efc13e309b932e6ac41d72ceb7b9b80a5f`; tree `c37da16cedbb91573476a44bd4eafe5a5e30134a`. Initial `git status --short` showed the new session directory as untracked. No claim of fresh remote alignment is made.
- Read `AGENTS.md`, current top status/next steps, current recovery handoff/checkpoint, the full `docs/PLAN.md`, interface continuation scope, and geometry contract. Also inspected the relevant existing implementation in `UiModel.cpp` and `InstrumentView.cpp`, the reference provenance, and current README/current evidence descriptions. Earlier source-specific acceptance is context, not newly executed acceptance.

**Recommendation:** use the existing wide cabinet column to host the complete live 25-key pedalboard below its artwork. Compact its current device-status area, recover the old bottom pedal row for the two complete manuals, and allocate enough of that recovered height to make their visible key extent approximately 144 pixels at 1672×941. Keep the current compact arrangement at smaller sizes. This changes the composition substantially while retaining all control identities, note ownership, and the existing shared geometry mechanism.

## Complete assigned page coverage

I read all **84 pages, 337–420 inclusive**, from `/workspace/scratch/1bb6ee17ad7e/atlas-text/part5-337-420.txt`, in seven bounded, untruncated 12-page outputs:

| Read chunk | Inclusive pages | Pages |
|---|---|---:|
| 1 | 337–348 | 12 |
| 2 | 349–360 | 12 |
| 3 | 361–372 | 12 |
| 4 | 373–384 | 12 |
| 5 | 385–396 | 12 |
| 6 | 397–408 | 12 |
| 7 | 409–420 | 12 |
| Total | 337–420, no gaps or overlaps | 84 |

Text input: **222,382 bytes**, SHA-256 `1efc248b77fba885a5b727bea839edd4b6bbf98faf34231e4a172e106dec4671`. These are complete extracted-page readings, not an independent verification of every cited external document or every PDF figure. The retained atlas source identity is SHA-256 `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769` according to the repository source/reference manifest.

| Chapter / pages read | Finding and consequence for this session |
|---|---|
| 055 / 337–342 | Driver identity and nominal impedance do not establish nonlinear parameters; coupled electrical/mechanical/thermal state needs measurements and separate numerical gates. Do not decorate the cabinet with invented driver telemetry or suggest this UI work connects its model. |
| 056 / 343–348 | A fidelity result names a specimen, boundary, scene, trajectory, and uncertainty. Static response, motion, and listening are separate gates. Visual matching must not become an acoustic claim. |
| 057 / 349–354 | Physical acquisition remains an explicit campaign with qualified boundaries, clocks, permissions, and immutable raw records. An attractive UI supplies none of those inputs. |
| 058 / 355–360 | Preserve unknown values as unknown; schema checks do not prove physical truth. Original bytes, interpretation, runtime representation, and evidence ownership remain distinct. |
| 059 / 361–366 | Fit identified boundaries outward; numerical termination is not parameter evidence. Do not let a cabinet visualization imply calibrated microphone geometry or a completed downstream model. |
| 060 / 367–372 | Documentary, mathematical, engine, host, and physical evidence have distinct oracles. Shared phase, Cancel-under-hold, callback partitioning, and exact stimulus histories remain protected. Page 372 specifically rejects a single “1:1” score combining evidence levels. |
| 061 / 373–378 | Similarity, discrimination, equivalence, and preference are different questions. Workflow/appearance testing belongs to usability and is separate from blinded audio comparisons. |
| 062 / 379–384 | The audio execution context owns time; UI consumes snapshots. GUI load cannot advance or reset generator/rotor state. No cost or real-time pass follows from calculated work or appearance. |
| 063 / 385–390 | Keep core and wrappers separate, preserve physical ports and all retained banks, distinguish ordinary controls from DSP checkpoints, and keep lifecycle work outside audio. |
| 064 / 391–396 | Permanent parameter identity, captured gesture ownership, control/editor-state separation, and source-specific host/device qualification remain required. Wrapper proposals do not supersede this repository's implemented contracts. |
| 065 / 397–402 | Its 62-entry registry is an atlas proposal, not this product's released 47-parameter contract. Preserve current approved IDs and state4/readers 1–3; do not append scanner/mic/rotary parameters as part of visual refinement. |
| 066 / 403–408 | Installed artifacts, source hashes, native platform observations, licensing, and physical evidence are separate release attachments. A new screenshot is neither a package qualification nor hardware fidelity evidence. |
| 067 / 409–414 | The art is atmosphere; its key counts and legends are not engineering authority. Recessed charcoal, walnut, brass, key fronts, independent text, 61+61 playing keys, 12+12 presets, 25 pedals, bank independence, Flat, and truthful inspection are the governing design requirements. |
| 068 / 415–420 | Build around player tasks, retain independent edit/sounding identities, use persistent ownership through resize/view changes, expose interlocks truthfully, and validate actual musical tasks. A pedal drawer is an explicit atlas layout proposal; a permanent miniature floor reproduction is not required. |

## Exact images directly inspected

Both images were opened with `view_image` and visually compared at their supplied 1672×941 dimensions:

| Input | Exact identity | Interpretation |
|---|---|---|
| `docs/design/atlas-cover-reference.jpg` | 412,664 bytes; SHA-256 `9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187` | Original embedded cover/page-409 JPEG stream; generated concept art. |
| `examples/demos/standalone-interface-preview-v2/images/play-reference-1672x941.png` | 643,593 bytes; SHA-256 `27c1a877ac458dc6775e7fb80f3edadf7b0508f923a5ef8d6cfb5095115847cd` | Actual retained native application capture. Its gallery owns executable/driver provenance; I did not rerender it. |

The native capture already has the important recognizable composition: walnut perimeter, dark deck, brass title/headings, ivory tablets, adjacent racks, two manual silhouettes and the same cabinet crop. The strongest remaining defect is the vertical allocation of useful space. A large lower-right status region duplicates several footer/modal facts while a separate full-width pedal row removes depth from both manuals. The source artwork has deeper manuals and no live pedal row. Copying its shorter keyboards, placeholder controls, or inaccurate legends would violate the atlas's explicit instructions (pp. 409–410, 414–415).

## Measurable baseline

Native coordinates below are computed directly from the inspected `make_ui_layout` and `make_keys` formulas at 1672×941. Reference landmarks are approximate visual observations, consistent with the existing geometry contract; they are not a new segmentation or pixel-equality test.

| Landmark | Current native geometry | Reference observation / implication |
|---|---:|---|
| Left deck margin | 71.896 px | Approximately 70 px; already close. |
| Header | y16–106, height 90 | Reference header also occupies approximately the first 110 px. |
| Performance panel | y116–220.920, height 104.920 | Concept percussion/scanner panel reaches approximately y262; current live inventory differs. |
| Drawbar rack | y230.920–456.760, height 225.840 | Reference approximately y270–510. Main rows currently sit high. |
| Computer-key toolbar | y466.760–494.760, height 28 | A real product control strip absent from the concept; it must remain operable. |
| Upper manual panel | y504.760–643.240, height 138.480 | Actual key inset consumes 30 px of panel height. |
| Upper visible keys | y526.760–635.240, depth **108.480** | Reference approximately y548–692, depth **144**. Current extent is about 24.7% shallower. |
| Lower visible keys | y675.240–783.720, depth **108.480** | Reference lower manual occupies roughly y720–867; the current lower manual ends too early. |
| Pedal panel | y801.720–879, height **77.280** | Removing this row from the left column recovers **87.280 px**, including its preceding 10 px gap. |
| Footer | y889–925, height 36 | Can remain anchored unchanged. |
| Cabinet panel | x1141.642, width 458.462 | Reference column begins about x1125. |
| Cabinet art | x1153.642, y154, width 434.462, height about 370.561 | Source crop ratio is 466:397. Reference art begins around y174; current art is approximately 20 px high. |
| Existing manual front span | x248.858–1123.642 | Back width ratio 0.94 already produces the intended sloping sides. Rewriting this projection is unnecessary for the main improvement. |

At the reference size, the current cabinet status card is about 279 px tall: art bottom near y524.56, status top near y585.56, status bottom y865. That is enough to accommodate a meaningful pedal surface plus concise status. Existing `paint_cabinet` already has an expanded versus compact status treatment, so this is a concrete reuse opportunity rather than a proposed new subsystem.

## Recommended wide layout contract

### 1. Relocate the complete pedalboard, without adding a drawer interaction

Use a presentation-only wide arrangement when the cabinet is shown and sufficient height exists. The existing **width 1400** and **height 820** breakpoints are a reasonable initial contract boundary: keep the current layout below either condition, and test both edges explicitly. This is a recommendation for the next reviewed contract, not an already accepted change.

In the wide arrangement, put the existing `layout.pedal_panel` below the cabinet artwork/caption, inside the right column. At 1672×941 a practical first allocation is approximately **104 px high** and **434 px wide** with a 12 px side inset. `make_keys` then gives approximately **74 px natural-key depth**, **27.9 px natural width**, and **16.7 px accidental width**. Those are useful live key targets; all 25 pedal indices remain present. Keep both existing pedal mixture controls in the top performance panel so no retained control moves semantically.

At the reference size, an approximate vertical arrangement is cabinet art y174–544.6, the two honest cabinet captions below it, pedal panel around y610–714, and a compact status card around y728–865. Preserve `ROTARY AUDIO NOT CONNECTED`, live audio/MIDI connection facts, and the footer's recovery/pending/focus messages. Detailed device names and errors remain available through the existing Audio/MIDI interfaces and Service context. Derive all bounds in `UiModel`; do not independently invent positions in paint code.

At short/wide sizes, constrain the cabinet artwork from the remaining space before reducing live key/control areas. Keep its aspect ratio. The current minimum/default arrangement remains the conservative fallback; do not force the reference composition into 960×700 or eliminate keys to achieve it.

### 2. Spend recovered height deliberately

Moving the pedal row recovers **87.28 px** at 1672×941. Simply splitting all of it gives key depths of **152.12 px**, a clear improvement but slightly deeper than the approximate 144 px reference. A stronger measured allocation is:

- Add **16.24 px** to the reference-size performance region or its explicitly reviewed adjacent spacing.
- Give **35.52 px** to each manual panel.
- Retain the toolbar, rack height, outer margin, footer, preset inventory, and current shared key projection.

For the version that puts the extra 16.24 px in the performance panel, the proposed reference coordinates become:

| Left-column region | Proposed reference bounds |
|---|---:|
| Performance panel | y116–237.16 |
| Drawbar racks | y247.16–473 |
| Computer-key toolbar | y483–511 |
| Upper manual panel / visible keys | y521–695 / **y543–687** |
| Lower manual panel / visible keys | y705–879 / **y727–871** |
| Footer | y889–925, unchanged |

Both manuals now have **144 px visible key depth**. This closes the largest quantified visual gap without changing the key projection, musical counts, or control identities. The figures are a proposed geometry budget, not post-change measured output. A smooth size-dependent budget should preserve these reference targets while maintaining positive geometry across the admitted size range.

This does not match every row of the concept. The actual toolbar and truthful top controls still require space. A later, separately reviewed relocation of the toolbar into two rows in the cabinet column could place the rack/manual boundaries still closer to the reference, but it is unnecessary for the initial high-value pedal relocation and adds more input-layout risk.

### 3. Preserve interaction and Flat semantics

The branch changes geometry only. Preserve **47 sound parameters**, `B3CONTROLS4`, readers 1–3, four retained manual banks, **68 ordinary UI records including 24 presets**, **147 playing keys**, **71 Play focus stops**, and the ten common stops. The atlas's proposed 62-parameter registry does not authorize a product migration (pp. 397–402).

Reuse `make_keys` for the relocated pedal panel, `UiKeyGeometry.hit/top/front` for rendering, and `ui_hit_test` for input. A pointer-up or computer-key-up must resolve its original captured owner even if resize crosses the branch and moves the pedalboard. Hidden Play controls must remain inactive in Rotary/Service. Preserve accidental precedence, semantic focus and all original note IDs. These are direct requirements of pp. 399, 412, 415–417, 420.

Flat continues to remove perspective/front faces/grain/heavy shading while exposing the same inventory and actions. At minimum size it retains the current compact composition. At wide size, if the relocation is shared by Flat and Dimensional modes, both must use the same presentation-layout decision; F7 must not emit a musical command or change note ownership. Do not turn the new placement into a saved sound parameter.

## Concrete code slices and principal risks

| Slice | Existing location / action | Risk to close |
|---|---|---|
| Wide row budget and sidebar rectangles | `apps/standalone/UiModel.cpp`, `make_ui_layout`; retain existing fixed control/key arrays and IDs. Compute the wide branch, left manual budget, relocated `pedal_panel`, and bounded cabinet art/status rectangles. Add presentation-only geometry fields to `UiModel.h` only where needed for one shared source of bounds. | Negative/overlapping regions at 1400×820 and extreme short/wide sizes; unintended change to compact/reference counts. |
| Paint order | `apps/standalone/InstrumentView.cpp`, `paint_instrument` and `paint_cabinet`. Current code paints pedals **before** `paint_cabinet`; a relocated pedalboard inside that panel would be overpainted. Paint cabinet background/art/status before its live pedal keys, or split background and contents explicitly. | An invisible but hittable pedalboard, or a status rectangle painting over keys. This is mandatory, not cosmetic. |
| Compact status | `paint_cabinet`; derive status bounds from shared layout, retain honest connection states, and use bounded `text_line`/`wrapped`. Current expanded branch assumes roughly 255 px. | Truncated recovery/error information, overlapping captions, invented live rotary behavior. |
| Existing keys and focus | `UiModel.cpp::make_keys`, `ui_hit_test`; `InstrumentView.cpp::paint_key`. Keep their current geometry and semantic ownership; only feed new panel rectangles. | A second independent coordinate system, lost original release, wrong accidental precedence. |
| Dimensional materials after layout | `InstrumentView.cpp::panel`, `wood`, `drawbar`, `paint_key`, `button`; existing `Drawing` primitives. Use the now-deeper key faces and coherent panel light direction; maintain low-noise Flat output. | Material overlays that cover labels/focus or make the hit silhouette disagree with paint. |
| Accepted evidence and gallery | Existing projection/workspace/scaled-view/raster/replay suites, then native gallery tool and actual captures. Integrator owns contract/status/README changes. | Reusing old pixel/executable evidence for changed geometry, or claiming a reference match from an unobserved build. |

Material refinement remains useful **after** the geometry change: the current procedural panel grain is extremely restrained, and the wood/key/deck lighting is simpler than the concept. The concrete next work is a coherent top-left light direction, narrow raised panel lips, dark keyboard-bed recesses, and key-front edge highlights that remain within the shared quads. Do not simply add stronger shadows everywhere. Existing `panel` and `paint_key` already provide the needed layers; no whole-interface background bitmap or new GPU renderer is required (atlas pp. 409, 411, 414).

## Acceptance evidence needed for this proposal

1. **Independent numeric layout check:** exact reference-size row depths and bounds from the new reviewed contract; 24 unique presets, 147 unique playing keys, 68 ordinary controls and unchanged focus counts. Check minimum/default/reference, 1399/1400 width, 819/820 height, and the existing extreme-size coverage. Retain explicit independent expected coordinates rather than calling the production helper to manufacture an oracle.
2. **Interaction check:** expose natural/accidental/front-face pedal centers at the new location, then hold a pedal/manual and a bank edit through resize and workspace/Flat changes. Release against original ownership. New hits at former pedal positions must resolve only the current visible geometry, never stale pedal IDs; hidden Play controls remain inactive. Verify no sound commands caused solely by layout changes. The changed geometry does not itself close physical pointer-capture qualification.
3. **State/audio preservation:** same 47 IDs and saved bytes; held ownership and applied controls survive the transitions. Reuse the existing meaningful continuity/replay gates for changed paths. No source-phase/percussion/model changes are in scope.
4. **Native raster check:** the sidebar pedalboard is actually visible after all cabinet painting; all 25 keys and focus/held states are legible; both manuals measure about 144 px at the proposed reference arrangement. Capture Flat and the minimum layout as well as reference Dimensional output. Compare actual output with the exact source, retaining separate semantic deviations and measured residuals.
5. **Truthful comparison:** retain the incorrect/truncated concept controls as a documented reason for semantic differences. No scanner selector, microphone-position dial, rotor-speed animation, or Stop button should become a functioning-looking control until its approved model/parameter contract exists (atlas pp. 409–413, 418–419).

## Outcome and limits

The full assigned text coverage and both exact image inspections are complete. The layout recommendation is implementable with the current SDL renderer and existing fixed-size UI model. The largest identified implementation trap is cabinet paint order after relocating the pedals; the largest acceptance risk is preserving original pointer/key release ownership across the responsive branch.

No production change or acceptance test was executed by A05. The proposed 144 px geometry and sidebar coordinates are design calculations for the next contract, not a new screenshot or pass. Literal pixel equality remains unattained and cannot be claimed by copying the concept's incorrect musical inventory. Physical audio/MIDI, native accessibility, scanner/AO-28/Leslie integration, calibrated acoustics and release rights remain their separate existing gates.
