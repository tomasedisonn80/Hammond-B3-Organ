# A01 - Atlas pages 001-084 and continuation governance

Actual worker: `/root/w01_a01`. Wave 1, assignment A01, 15 November 2026.
Owned deliverable: this note only. No production edits, build, test suite,
capture, commit or publication was performed by this worker.

## Complete reading and identities

Read every line of the supplied page-marked extraction for PDF pages **1-84**,
including front matter and chapters 1-12. Sequential reads covered lines
1-360, 361-1060, 1061-1760, 1761-2460, 2461-3160, 3161-3860,
3861-4560 and 4561-4929 without truncated output. A separate marker check
found exactly the consecutive pages 1 through 84. This is complete textual
coverage of the assigned range; it is not a claim to have independently
inspected every source image or every external work cited by the atlas.

| Input | Identity |
| --- | --- |
| Original source PDF | `Hammond_B3_Leslie_Research_Atlas_500pp.pdf`; SHA-256 `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769` |
| Scratch extraction | `/workspace/scratch/177e78b1ac09/atlas-001-084.txt`; 210,181 bytes; 4,929 lines; SHA-256 `8bf339a7c9d83d0f83c2c7331521da7ac968c7e0ae6682b1c0aec7e09a743583` |
| Observed checkout | `/workspace/scratch/177e78b1ac09/Hammond-B3-Organ` |
| Observed initial HEAD | `4aac394cde4da40906b615573a8779aee2d9a37a` |
| Observed initial tree | `3605c9ce098a052afc10b2969fefe31e15644fe9` |

The initial `git status --short --branch` showed only `main...origin/main`;
the cached tracking identity is not a new remote or CI query. The initial commit
subject is `Implement fractional contact reference and canonical wide Play composition`.

Also read all of `AGENTS.md`, `docs/PLAN.md`, `docs/NEXT_STEPS.md` and
`docs/SESSION_HANDOFF.md`; recovered current portions of README, STATUS,
DEVELOPMENT_LOG and PRODUCT_HANDOFF; read the prior execution entry/checkpoint,
its actual ledger structure/counts, the causal-streaming proposal and review,
and the next-material proposal and A41 review note. Historical SESSION_HANDOFF
inventory is explicitly superseded and must not drive new implementation choices.

## Requirements recovered from pages 1-84

| Pages | Consequence for current development |
| --- | --- |
| **1-12** | The atlas is a research/specification package, not a measured instrument or completed engine. Baseline is vintage B-3/AO-28 plus Leslie 122; other revisions/variants need separate identities. Preserve documented/measured/derived/proposed/unknown distinctions. M0-M9 implementation milestones differ from the ten research waves and this session's agent waves. Keep allocation, file work, logging and rendering outside the audio callback. |
| **13-18: reference contract** | Functional, specimen/audio and visual correspondence have independent acceptance. A profile binds assembly, condition, acquisition chain, source units, uncertainty and immutable revision. Missing physical inputs remain unknown. Offline diagnostics/render identity and held-out evaluation precede a calibrated claim. No authenticity percentage follows from a build or screenshot. |
| **19-24: documentary evidence** | Select exact drawing/assembly revision before modeling. Retain both printed and one-based PDF page locators, hashes and literal markings. Transcribe nodes before values; unresolved junctions are not guessed. Later redraws and duplicate-host scans are not independent factory evidence. Rights and circuit fidelity are separate gates. |
| **25-30: patents** | Patents explain mechanisms without proving production applicability. Shared source phase, explicit source/contact/routing layers and independently rotating acoustic paths are core architectural requirements. Do not mix alternate percussion embodiments or import a patent's scanner section count into another production line. |
| **31-36: cabinet/appearance** | Measured geometry and attractive shading are distinct. Keep units, endpoints, source attribution and transformation recipes. Retouched assets cannot supply dimensions. A read-only UI snapshot, stable control IDs and a flat alternative prevent presentation changes from altering sound state. Neutral technical and final lighting need separate review. |
| **37-42: manual mechanism** | Two manuals have 61 playing keys each, with nine independent contacts per key: 549 per manual. Continuous key/pusher motion, contact thresholds, hysteresis, release/repress and source mapping have separate histories. Ordinary MIDI initiates a declared synthetic trajectory; it does not recover finger motion. Preserve fractional crossings, block-invariant event timing and incomplete-return state. UI frames cannot clock audio. The cited 9 mm travel belongs to a serviced 1967 C-3 specimen, not a universal B-3 tolerance. |
| **43-48: generator mechanics** | Distinguish electrical source, shaft and compartment identities. The documented assembly has 91 active sources and five balancing blanks in 96 disk positions; blanks are not audio oscillators. Source phases continue through silence, note changes and block boundaries. A common shaft implies tooth-count phase relationships, not independent per-note flutter. Dynamic coefficients remain unmeasured without acquisition. |
| **49-54: controls/presets** | Retain four independent nine-drawbar manual banks and two pedal drawbars. Correct footage/color/semantic IDs matter more than decoration. C cancels routing; C#-A select fixed registrations; A#/B select left/right banks, with upper B percussion eligibility. The physical optional multilatch model is distinct from the initial exclusive selector. Global/percussion Soft controls differ. Continuous-contact hardware does not prove a linear gain law. Inactive-bank edits, sustained-note selector changes, Cancel and restoration require behavioral evidence. |
| **55-60: Leslie family** | 122 and 147 have distinct electrical/input profiles; modern servo cabinets and shorter cabinets are separate targets. Stationary drivers, rotating horn/drum channels and microphone/room geometry must not be conflated. Do not create measured geometry from the retouched isometric image or implicitly add reverb to the baseline. |
| **61-66: frequency/phase** | Source IDs, terminal positions, storage indices and MIDI notes differ. The nominal indexing anchors are tone 1/MIDI 24 and tone 46/MIDI 69; the chapter's 12-TET reference uses `440 * 2^((w-46)/12)`. Gearing, 12-TET and measured profiles are separate. Shared sources must remain correlated across routes and silence. Phases integrate frequency rather than restart at note-on or host boundaries. |
| **67-72: pickups** | Separate magnetic geometry, induced source voltage and loaded terminal voltage. Nominal sinusoid, calibrated terminal coefficients and flux-linkage models have different evidence requirements. Retain absolute/normalized units, common phase, bandwidth policy and load boundaries. Do not filter an already filtered terminal capture twice. |
| **73-78: source filters** | Preserve early versus bulletin revisions and original units (`mf/mfd` here means microfarads). Fixed-load steady harmonic precomputation is valid only under its declared assumptions; switching loads/startup need their own stateful model. Numeric tolerances in the atlas are proposals, not hardware measurements or already achieved results. |
| **79-84: leakage** | Leakage has an explicit injection boundary and sparse physical/empirical topology. Pitch adjacency is not physical adjacency. Preserve source phase, polarity and coherent addition; do not normalize away a real level change or duplicate leakage already present in captures. Dense/sparse equality and allocation/bounded-state checks are engineering gates; no complete measured 91-source matrix is supplied. |

## Current phase and stale-routing finding

This checkout already contains the bounded M3 offline fractional-contact
reference and M9 canonical wide Dimensional Play composition. They are not new
tasks to repeat. The retained prior execution evidence says 36 fixtures x four
factors, 144 renders and a 203/203 coherent local CTest pass. This worker did not
rerun those experiments or promote their source-specific receipts to later code.

The prior execution checkpoint and ledger are newer than shared STATUS text:
the ledger has **45 records: 42 accepted and three dispatched**, while shared
text still reports 42 dispatched. Its checkpoint also says publication is
pending, although this fresh checkout's published commit subject already records
the implementation. Root should reconcile those historical observations with
fresh remote/CI evidence while retaining their original dates and failures.
Do not finish another session's worker count using this session's workers.

Current protected identities are **91 shared free-running sources**, **47 sound
parameter meanings**, **B3CONTROLS4 with readers 1-3**, the nominal default dry
Engine, musical ownership and existing UI controls. Earlier historical parameter
counts or state-migration proposals do not supersede these identities.

## Recommended dependency-ready scope

### M3: bounded arithmetic and trajectory spike

The most concrete next audio-engineering task is already proposed in
`docs/CONTACT_STREAMING_NEXT_DESIGN.md` and reviewed in
`docs/reviews/CONTACT_STREAMING_DESIGN_REVIEW.md`. Freeze a new isolated C++20
representation/trajectory contract before coding the filter or touching Engine.
The existing offline reference is finite and acausal; splitting its ranges does
not create streaming processing.

The new contract must prove fixed-capacity arithmetic/intermediate bounds,
including binary64 subnormals; retain command-coordinate collision identity
across callbacks; preserve exact roots/ties and independent contact history;
freeze partition-independent accumulation and complete transactional rollback;
and distinguish syntax maxima from admitted work. The earlier review computes
71,595,078 conservative operations for the largest L256/N4096/K4/M512 case,
above the existing 20-million work cap. Ordinary 64/128-bit rational pairs do
not cover the full proposed binary64 domain without a reviewed alternative.

The reviewed scheduling derivation supports D=16 for a later filter and N+33
outputs for a nonempty finite observation, including 33 drainage samples.
That derivation is not filter implementation or callback qualification.
Independent trajectory fixtures, adversarial equal-display/distinct-root cases,
failure/continuation and partition tests should admit the spike first. A new
full-window continuous oracle, justified tolerances and resource budget remain
separate prerequisites for an all-sample audio grade and later Engine/VST3 work.

### M9: first measured material refinement

`docs/design/WHOLE_REFERENCE_MATERIAL_NEXT.md` already ranks the visible gaps.
Its first concrete candidate is only the Upper-rack inner metal, canonical
rectangle `(76,273,520,231)`, leaving children, other panels and semantics intact.
The A41 review accepts protocol authoring, not production code or a tolerance
pass. Freeze a physical pixel mask from renderer rules before editing, retain
unrounded patch targets, bound deterministic grain and restore renderer state.

Required evidence is genuine same-state before/after native captures across
reference/minimum/wide sizes, scales, offsets, clipping and control states;
narrow containment and exact inactive output; live geometry/focus/ownership
regressions; independent full-frame material review; and updated actual README
screenshots with source/executable/state/pixel identities. The earlier broad
composition mask protects as few as 34 active pixels and cannot qualify this
narrow material change. Material improvement is not literal whole-interface 1:1.

## Blocking dependencies and durable workflow

Physical contact/geometry/pickup/driver calibration still lacks identified
specimens, synchronized qualified captures and untouched held-outs. Native
display/DPI/device/accessibility and DAW/release results require actual runs.
Scanner G5 same-Hz failure, separate ScannerLineFoh/library, same-Hz crossover,
MIDI retirement and R4/R5/R6 tracks retain their recorded owners/gates. New
engineering can proceed without falsely closing any of these dependencies.

Root owns shared documentation, the one coordinated build, staging and
publication. Record sixty genuinely distinct new workers in ten six-worker
waves; checkpoint each wave and keep artifacts bounded. Read fresh remote
advances, integrate compatible changes, publish accepted work to main without
force under the existing authorization, then verify exact remote commit/tree
and current-source CI. Update setup, status, next steps, development log,
README UI evidence and permanent agent routing. Never replace another session's
unfinished checkout or count historical workers as new participation.

## Verification performed by A01

Executed read-only text/source inspection, initial Git status/HEAD/tree queries,
PDF and extraction SHA-256, exact extract page-marker coverage and prior-ledger
counts. Only this assigned Markdown note was written. No numerical experiment,
build, runtime test, hosted CI query, visual capture or physical measurement is
claimed by this note. Root owns acceptance and publication.
