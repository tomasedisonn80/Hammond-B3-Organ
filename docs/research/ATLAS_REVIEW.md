# Atlas review and engineering evidence boundaries

The complete 500-page atlas has been reviewed across the six retained assignments
below. It supports a staged, inspectable B-3/AO-28 and Leslie implementation; it
does not supply newly acquired reference-instrument measurements (atlas p. 2).
This document consolidates navigation and decisions. Detailed findings remain in
the review notes; actual implementation and executed-test status belong in
[STATUS.md](../STATUS.md) and [DEVELOPMENT_LOG.md](../DEVELOPMENT_LOG.md).

## Source identity and navigation

- Source: [`Hammond_B3_Leslie_Research_Atlas_500pp.pdf`](../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf),
  evidence edition 12 November 2026; 21,248,265 bytes; 500 pages.
- SHA-256: `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
- [Source manifest](source-manifest.json) preserves the source identity and baseline
  absence of companions. The PDF remains unchanged.
- [Chapter index](chapter-index.json) transcribes all 80 titles and starts from
  contents pp. 7-11. Each chapter spans six pages: chapters 001-080 occupy pp. 13-492;
  front matter occupies pp. 1-12 and the source directory pp. 493-500.
- Citations here use one-based PDF page numbers, which match printed atlas pages.
  Page numbers inside cited service manuals refer to those separate documents.
- Read [ERRATA.md](ERRATA.md) before implementing flagged formulas or diagrams;
  [RIGHTS_AND_SOURCES.md](RIGHTS_AND_SOURCES.md) records discovery and reuse limits.

## Complete review coverage

| Retained review | Inclusive PDF pages | Count | Scope |
| --- | --- | ---: | --- |
| [01](../development/agent-notes/01-atlas-pages-001-084.md) | 1-84 | 84 | Front matter; chapters 001-012 |
| [02](../development/agent-notes/02-atlas-pages-085-168.md) | 85-168 | 84 | Chapters 013-026 |
| [03](../development/agent-notes/03-atlas-pages-169-252.md) | 169-252 | 84 | Chapters 027-040 |
| [04](../development/agent-notes/04-atlas-pages-253-336.md) | 253-336 | 84 | Chapters 041-054 |
| [05](../development/agent-notes/05-atlas-pages-337-420.md) | 337-420 | 84 | Chapters 055-068 |
| [06](../development/agent-notes/06-atlas-pages-421-500.md) | 421-500 | 80 | Chapters 069-080; source directory |
| **Total** | **1-500, contiguous and disjoint** | **500** | **12 + 80 × 6 + 8 pages** |

Each note records complete assigned text reading and selected visual inspections.
That is full page coverage, not an assertion that every figure or underlying
external source was independently verified. This consolidation checked the
contents and selected errata pages; it inherits the six reviewers' retained
coverage records rather than claiming a seventh independent full-PDF reading.

## Complete product goal and implementation order

The objective is one framework-independent engine serving an offline renderer,
VST3 and standalone product, with faithful control behavior, a calibrated organ
and cabinet model, and the accessible dimensional interface described on pp.
409-444. Vintage B-3/AO-28 plus Leslie 122 is the baseline; Leslie 147, regional
power variants, modern instruments and accessories require separate profiles
(pp. 13-18, 55-60, 253-264).

The atlas's ten research waves organize its chapters. Its implementation sequence
is **M0-M9**, and the development session's agent waves are a third organization.
Neither chapter coverage nor completed agent assignments establishes product
completion (pp. 5, 445-456, 481-492). [PLAN.md](../PLAN.md) owns the detailed plan.

| Milestone | Engineering goal | Evidence needed for the associated physical/product claim |
| --- | --- | --- |
| M0 | Reference/profile identity, units, provenance, explicit unknowns and acquisition queue | Identified specimen, revisions, condition and permissions (pp. 13-24, 445) |
| M1 | Prepared core, bounded timestamped events, deterministic offline render and diagnostics | Executed timing, failure, lifetime and callback checks; no hardware claim follows (pp. 385-390, 446) |
| M2 | 91 shared free-running sources and explicit source/contact maps | Independent factory map, gearing, pickup waves/levels/phases/loading and leakage (pp. 61-108, 446) |
| M3 | Contacts, retained banks, presets, pedals, shared percussion and expression | Measured gestures, loading, envelope/recharge and expression responses (pp. 109-156, 447) |
| M4 | One scanner history, six modes, reviewed LC topology and numerical realization | Independent loaded AC/transient reference plus specimen scanner captures (pp. 157-192, 447, 465) |
| M5 | Connected AO-28 graph, loaded linear reference, nonlinear devices and dry output | Revision-specific connectivity, transformers, operating points and dry G-G validation (pp. 193-252, 448, 488) |
| M6 | Separate 122/147 electronics, transformer, crossover and coupled driver load | Signed voltage/current ports, driver impedances and cabinet-revision measurements (pp. 253-276, 337-342, 448) |
| M7 | Independent horn/drum motion, moving paths, directivity, cabinet and microphone scene | Synchronized angles, trajectories, geometry and complex acoustic responses (pp. 277-336, 449) |
| M8 | Immutable acquisition ancestry, upstream-first fitting and held-out evaluation | Calibrated captures, predeclared tolerances, uncertainty and listening evidence (pp. 343-378, 449, 484) |
| M9 | VST3/standalone, automation/state, accessible UI, packaging and release | Actual hosts/devices, native accessibility, deadlines, dependency rights and platform qualification (pp. 391-444, 450, 485) |

Validate the dry organ before fitting Leslie or room effects (pp. 247-252,
362, 448). Early adapter experiments and UI prototypes may proceed against stable
contracts; they do not close M9.

## What the current engineering scope means

[IMPLEMENTATION_CONTRACT.md](../IMPLEMENTATION_CONTRACT.md) selects an initial
M0-M2 foundation with explicitly nominal dry routing. Its named unmeasured model
uses 12-TET, ideal sines, proposed initial phases, normalized amplitudes and ideal
contacts; these choices enable repeatable engineering without fabricating a
specimen. Source IDs, physical terminals, MIDI notes and array indices remain
different domains (pp. 61-66, 91-108, 385-390).

The manual map can be reconstructed from the algorithm on pp. 98-99 and checked
against six printed rows on p. 102. This is **reconstructed data, not recovered
companion data**. Algorithm consistency is not an independent transcription of
all 549 factory-table cells. The same distinction applies to reconstructed pedal
rules (p. 140), schemas, circuit graphs, mission text and reference implementations.
Factory Table V values are G-G service observations, not oscillator amplitudes
(pp. 92-93, 350).

Evidence classes (`documented`, `measured`, `derived`, `proposed`, `unknown`) describe
inputs. Execution outcomes (`pass`, `failed`, `blocked`, `not_run`, `inconclusive`)
describe tests. Neither substitutes for the other. Retain code/profile/data
identities, setup, criterion, observed result and reviewer for every acceptance
claim; preserve failures and invalidate affected claims after changes (pp.
355-360, 372, 481-486). Historical companion results printed in the atlas are
source claims, not tests run in this repository.

## Missing inputs: what they block and what can proceed

| Missing or unresolved evidence | Blocks | Work that can proceed with an explicit scope |
| --- | --- | --- |
| Original chapter JSON, source catalog, mission/header, reference scripts and acceptance reports | Claims of recovery, exact companion reproduction or inherited test passes | Versioned reconstructions and independently executed tests (pp. 451-456, 481-492) |
| Specimen serial, AO-28 revision, condition and actual cabinet identity | Specimen-specific fidelity and applicability of nominal values | Profile schema, documentary variant separation and acquisition planning (pp. 13-18, 223-228) |
| Independently transcribed factory map and complete geared-frequency evidence | Full factory-table conformity and historical tuning claims | Atlas-derived routing and named 12-TET source tests (pp. 61-66, 97-108) |
| Pickup, contact, bus/loading, percussion and expression captures | Measured console response, click, source level/phase and control dynamics | Named ideal/nominal behavior, state and ownership tests (pp. 67-96, 109-156) |
| Reviewed scanner graph, source-equation resolution and reference captures | Qualified scanner circuit and hardware match | Reconstruct graph, derive equations, compare independent numerical solvers (pp. 157-192, 465) |
| Complete AO-28 connectivity, active values, transformer/load and operating-point evidence | Circuit-complete M5 numerical export and calibrated dry-organ response | Inventory/source reconciliation and branch contracts (pp. 235-240, 458, 488) |
| Leslie electrical, rotor, radiation, geometry and room measurements | Calibrated M6-M7 cabinet/scene claims | Separate variant contracts and synthetic electrical/motion/acoustic oracles (pp. 253-348) |
| Immutable target captures, group splits, uncertainty and listening trials | M8 held-out physical/perceptual acceptance | Acquisition schemas and evaluation tooling; synthetic fixtures stay synthetic (pp. 349-378) |
| Actual hosts, devices, native UI/assets, rights records and platform artifacts | M9 playable-product, accessibility, distribution and signed-release claims | Stable parameter/state contracts and scoped prototypes (pp. 391-444, 469-486) |

Every modeled effect has one owner: loaded pickup filtering, shared nonlinear
stages, chorus return, propagation, cabinet, microphone and room contributions
must not be counted twice (pp. 171, 241-246, 305, 325-336). Preparation, allocation,
destruction, file access and UI work remain outside audio processing (pp. 379-390,
453). Source phase advances independently of notes, silence and UI; horn and drum
retain separate clocks and histories when implemented (pp. 103-108, 319-324).

The next dependency-ready engineering task and current verification record are
maintained in [NEXT_STEPS.md](../NEXT_STEPS.md) and [STATUS.md](../STATUS.md).
