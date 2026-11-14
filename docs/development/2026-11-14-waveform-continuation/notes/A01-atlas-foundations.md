# A01 — Atlas foundations, pages 1–84

## Assignment and exact evidence

- Session: `2026-11-14-waveform-continuation`, wave 1, A01; actual worker `/root/w01_a01_atlas_foundations`.
- Owned deliverable: this note only. No product/shared-document changes, build, test execution, commit or publication.
- Inspected starting HEAD: `2e161dc3a60fc3442051799574feed37bffbfc5c`; tree `17f8e4d698f903c37bff09deee196ea73e0da108`. Initial working tree was clean; read-only `git ls-remote origin refs/heads/main` returned the same HEAD.
- Source: `Hammond_B3_Leslie_Research_Atlas_500pp.pdf`, evidence edition 12 November 2026; **500 pages, 21,248,265 bytes**.
- Independently computed PDF SHA-256: `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
- Assigned text: `/workspace/scratch/e3cacb90cc81/atlas-text/part-1-1-84.txt`; **4,929 lines, 210,517 bytes**; SHA-256 `00e1b5d152c846045b9f83d2cbf1045f525dd4b79aba77422bd65196016a920a`.

## Actual coverage and setup

**Every word of the supplied text for one-based PDF pages 1–84 was read**, covering front matter and all of chapters 001–012. Eleven sequential, non-truncated `sed -n` outputs covered inclusive lines:
`1–450`, `451–900`, `901–1350`, `1351–1800`, `1801–2250`, `2251–2700`, `2701–3150`, `3151–3600`, `3601–4050`, `4051–4500`, `4501–4929`.
An independent Python marker check found exactly pages 1 through 84 in order. Searches, earlier workers and summaries did not replace this reading.

Selected PDF pages **1, 4, 49, 55, 57 and 58** were actually rendered and viewed after reading the PDF skill. This is complete assigned **textual** coverage and selected **visual** coverage, not every figure, the remaining 416 pages, external sources, or a current-app pixel comparison.

`AGENTS.md` and the complete `docs/PLAN.md` were read first. Contextual reading covered README, STATUS, NEXT_STEPS, ATLAS_REVIEW, the latest development-log entry, REFERENCE_REFINEMENT_SCOPE, its checkpoint and ROTARY_PROPAGATION. The earlier reference-refinement session and its workers remain distinct history.

| Visually inspected page | Concrete observation and limit |
| --- | --- |
| 1 | Walnut cheeks/rail, charcoal panels, brass lettering/trim, three workspace tabs, adjacent racks, two manuals and right cabinet composition. The caption makes engineering controls authoritative. |
| 4 | Two-row responsibility map; its caption explicitly says actual branches/coupling require selected circuits and measurements. It is not factory connectivity. |
| 49 | Exact footage/cap table and stage-lit drawbar photograph. The image supports shape/context, not calibrated color. |
| 55 | Cabinet-family table and P020 caption explicitly mark the pictured isometric cabinet retouched/transformed and excluded from geometry evidence. |
| 57 | Horn component photo supports visible construction, not calibrated dimensions or a serial-qualified 122. |
| 58 | Lower-deflector photo and separate display/geometry evidence classes; same specimen/dimensional limitations. |

## Product scope and source limits

The target is a defined **vintage electromechanical B-3, identified AO-28 revision and vintage Leslie 122**, serving an inspectable engine, VST3 and standalone product. Modern digital B-3, Leslie 147, mains-region variants, short cabinets and modified specimens need separate identities and applicable evidence (pp. 2–5, 13–18, 55–60).

The atlas expressly reports **no newly measured instrument, completed audio engine, plugin binary, captured reference dataset or demonstrated 1:1 fidelity** in its original research package (p. 2). Later repository implementations have their own evidence. Referenced chapter JSON, source catalogs and other companions are not recovered by authoring similar data; ATLAS_REVIEW records their baseline absence.

Functional, specimen-audio and visual correspondence are separate results (p. 13). Behavior, audio, interface and deployment need separate reports. A bounded fidelity claim names specimen, profile revision, controls, signal boundary/levels, geometry, operating conditions, tolerances and uncertainty; repeatability and held-out captures establish scope (p. 18). Page reading, attractive imagery and synthetic numerical passes cannot substitute for those results (pp. 5, 18, 36, 72).

Every physical value retains **documented/measured/derived/proposed/unknown** classification, unit, source locator, applicability, conditions, uncertainty and revision. A measured tag requires an acquisition record; unknown is not zero. Immutable specimen identity stays separate from mutable performance controls (pp. 2–3, 12, 14–16, 21–24).

Source controls matter: 1995 redraws remain later redraws; alternate hosts are not independent factory witnesses; the atlas did not visually verify the AO-28 underside GIF; US2828659 remained an unresolved retrieval candidate (pp. 19–24, 30). Public access does not establish redistribution rights. The cited 319-callout inventory and companion results are source claims, not assets or tests newly acquired by A01 (pp. 24, 30, 36, 60).

## M0–M9 implications

This follows atlas p. 5 and the complete repository plan. Research waves, implementation milestones and requested worker waves have different meanings.

| Milestone | Implication for this continuation |
| --- | --- |
| M0 — reference | Preserve hashes, variant/profile identities, units and acquisition queue. Nominal geometry/speed cannot become specimen measurements. |
| M1 — skeleton | Prepared deterministic core, timestamped events and offline observations; allocation, files, locks, logging and rendering stay outside processing. |
| M2 — generator | Preserve 91 shared free-running sources, distinct source/terminal/MIDI/storage identities and phase through silence. Physical tuning/waves/offsets/leakage remain open. |
| M3 — console | Preserve independent banks, contacts, fixed routes, Cancel, percussion eligibility/history and expression. Nominal gestures/gains do not close mechanical/loading gates. |
| M4 — scanner | Verified LC/switch/loading topology, one history and six modes need independent numerics and captures. The recorded G5 failure remains a separate gate. |
| M5 — organ electronics | Connected revision-correct AO-28, loading/transformers/operating points and dry-organ validation precede cabinet fitting. |
| M6 — cabinet electronics | Separate 122/147 profiles and explicit crossover/driver loading. The documented nominal 800 Hz network is not a complete calibrated electrical model. |
| M7 — rotary | R4 can qualify nominal independent-input waveform history and causal paths; measured motion, directivity, cabinet, microphones and room remain distinct. |
| M8 — calibration | Identified immutable captures, repeatability, uncertainty, training/held-out separation and residuals are required; synthetic fixtures qualify algorithms only. |
| M9 — product | Live controls and copied state, resize/keyboard/Flat operation and actual captures; host/device/accessibility/deadline/rights/release evidence remains separate. |

## Rotary R4: actionable constraints

**Keep declared radiation boundaries.** Page 4 separates direct-organ and miked-cabinet validation. Pages 55–60 separate stationary transducers, moving acoustic parts, electrical loading and radiation/propagation; coupled loading must not disappear inside a convenient block chain. Horn/drum retain independent states; changing horn speed does not change drum speed unless a command targets both (p. 60).

**Do not duplicate Doppler.** Page 29 assigns changing distance to path delay and frequency-dependent radiation to directivity. Its `tau=r/c` and observed-frequency approximation are educational checks, not a complete rotating-horn solver. R4 should use qualified R3 retarded-time results, not replace them with that approximation or add an arbitrary pitch LFO.

The inspected `docs/ROTARY_PROPAGATION.md` calls R2/R3 nominal, unmeasured diagnostics/emission-position primitives, with no delayed audio or Engine insertion. Its R4 handoff requires the following; these are **repository requirements, not constants extracted from pp. 1–84 or tests executed by A01**:

1. Prepared bounded motion retention and separate double horn/drum waveform histories; capacity `ceil(Fs*rmax/c)+2+4`, within 16,384 frames. The 4,097-segment fixture is not an unlimited event queue.
2. Write sample `n`, observe at `n-2`, solve four paths, read cubic support `k-1,k,k+1,k+2` at emission time. Negative audio is zero; future support is never invented. Apply declared distance gain and signed Horn-then-Drum summation without hidden clipping/normalization.
3. Admit inputs/buffers/events/timeline before mutation; preserve state, histories, diagnostics and caller audio on whole-call failure, with zero events consumed. Retain tie order, offset-N/zero-frame semantics, reset/rate-change and tail-flush contracts.
4. Execute frozen support/polynomial/static-delay and independent same-cubic parity tests at every rate, partition-identical audio/state, nonzero-history rejection, separate-input/stereo and every stopped-rate-pair checks.

Consult the frozen numerical contract before implementation. **R5 audible reconstruction/filtering/alias policy and R6 runtime/Engine/host/device integration remain separate.** Preserve dry Engine output, all 47 parameter meanings, state4/readers 1–3 and transient histories/ownership.

Effect ownership is a general source requirement: post-filter terminal captures must not receive the same filter again (pp. 67–76); captured leakage must not gain a duplicate generic layer (pp. 79–84). Rotary inputs must declare whether crossover, driver, horn transit, directivity, cabinet, microphone or room response is already represented. Synthetic R4 inputs acquire none of these by being labeled Leslie inputs.

## UI matching constraints

The p. 1 image establishes art direction; its decorative labels and rotor/microphone controls do not authorize incorrect semantics or imply connected cabinet audio. A01 did not compare a new native screenshot or close literal reference equality.

| Source pages | Requirement for live UI/refinement |
| --- | --- |
| 31–36 | Geometry ledger, defined specimen/capture state, scaled views, endpoints/uncertainty and landmark residuals. The stated B-3 footprint includes bench/pedalboard; it is not a console-only box. |
| 6, 33, 35, 55–58 | P005/P020 retouched regions cannot establish geometry. Separate permission to display from permission to support geometry. Component photos lack calibrated dimensions and exact 122 identity. |
| 33, 49, 53 | Separate appearance from material identity. Stage lighting is not calibrated color; preserve source/derivative provenance and avoid unsupported substrate claims. |
| 34, 40, 42, 52, 54 | Read-only snapshots; camera/visibility/render stalls/animation cannot alter audio or serialized sound state. Perspective and Flat retain semantic identities and input ownership. |
| 49–50, 54 | Four independent nine-drawbar banks plus two pedal settings; fixed routes remain sounding while inactive banks are edited. Correct footages and sounded/applied state precede decoration. |
| 50–51 | C Cancel, C#–A fixed, A# left bank and B right bank; only enabled upper B admits percussion. Modern snapshots and optional physical multi-latch behavior stay explicit separate models. |
| 51–52 | Four percussion meanings, overall versus percussion volume and shared scanner routing remain distinct. Continuous contacts do not establish discrete detents or a measured linear travel/gain law. |

## Missing physical data and useful acquisition locators

| Missing input | Required next evidence / blocked claim |
| --- | --- |
| Specimen/revision | Serials, assembly codes, restoration/replacements, AO-28/scanner/generator identity, cabinet/chassis/driver identity and permissions (pp. 3, 13–17, 55–60). Blocks specimen correspondence. |
| Rotary geometry/motion | Separate synchronized horn/drum angle/speed and command traces; rotor centers/mouth geometry, cabinet openings, microphone poses, room and specimen-state revision (pp. 29, 57–60). Blocks calibrated M7. |
| Electrical/waveform boundaries | Identified routes, calibration/load, direct versus microphone and pre/post-filter captures, common phase clock, repeatability and held-out data (pp. 17, 65, 67–78, 83). |
| Console geometry/contacts | Scaled same-specimen views, pivots/travel and per-contact closure/release/bounce with aligned clocks; loaded contacts/drawbars (pp. 31–42, 52–54). Approximately 9 mm travel is one 1967 C-3 observation, not a universal B-3 value. |
| Generator physical profile | Production gearing, phases/waveforms/levels, impedances/loss/coupling, residual topology and identifiable dynamics (pp. 43–48, 61–84). No complete measured 91-source leakage matrix is supplied. |
| Documentary connectivity | Independent exact-sheet/junction/value review. Atlas p. 20 locates factory 220-page-scan system schematic at PDF 91/printed 3-12, preamp at 129/3-50, construction at 170/5-1, tooth plate at 171/5-2 and manual breakdown at 192/6-9. |

Next dependency-ready software work: reviewed nominal **R4 renderer plus independent frozen-contract acceptance**, while physical acquisition remains explicit. UI work needs actual new native captures and reference comparison with residual differences stated. Neither closes physical M5–M8, native accessibility or full M9 release.

## Verification and outcome

Executed reading/identity commands used `sed`, `cat`, `wc`, `sha256sum`, `git status --short`, `git rev-parse`, read-only `git ls-remote`, `pdfinfo` and a Python page-marker assertion. No builds or product tests ran.
Selected visuals used `pdftoppm -f PAGE -singlefile -r 96 -png SOURCE PREFIX`, then `view_image`, for pages 1/4/49/55/57/58. Temporary PNGs are outside the repo at `/workspace/scratch/e3cacb90cc81/tmp/pdfs/a01-atlas/`.
Outcome: complete assigned text, six actual original-page visual inspections, unchanged PDF identity, explicit physical gaps and a scoped R4/UI handoff. Earlier tests and workers were not recounted as this assignment's execution.
