# Assignment 05 - full atlas product and interface review

## Identity, ownership and executed scope

- Actual assignment: `/root/w01_a05_atlas_product`, wave 1, second batch of the
  new sixty-assignment next-phases session. Earlier sessions are not counted.
- Checkout: `ba0d9c9c75bd7a39152470f9f7ddb82287cb01b1`; committed tree
  `51fd7b24d2f373a693ced8dbde0fba762a3cc434` at inspection. Other workers' new
  session notes were present and were preserved.
- Owned file: this note only. No production source, shared status, dependency,
  historical report, commit or remote reference was changed.
- Source: [preserved atlas](../../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf),
  PDF pages **337-420 inclusive**, all 84 pages, read freshly in full.
- Verified original PDF SHA-256:
  `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
- Actual page images rendered and visually inspected: **409, 411 and 415**.
  This is full assigned text coverage and selected visual coverage, not an
  independent verification of every cited external source or every figure.
- Read repository standing instructions, current README/status/next steps and
  the current `ParameterBridge.cpp` to distinguish atlas proposals from the
  real forty-five-control implementation.

## Full page coverage and implications

| Chapter / PDF pages | Content read and retained implication |
| --- | --- |
| 055 / 337-342 | Stationary drivers, reciprocal electrical/mechanical signs, thermal memory and coupled amplifier/crossover loading. Generic distortion or a warm sound does not identify a Leslie driver. Unknown driver curves and measured quantities remain unresolved. |
| 056 / 343-348 | A fidelity result names a cabinet, revision, load and microphone scene. Separate stationary and rotating tests, preserve calibrated timing and holdouts, and distinguish failed or inconclusive results. |
| 057 / 349-354 | Acquisition needs specimen identity, permission, qualified boundaries, calibration and immutable raw data. Table V is a G-G service observation, not a raw pickup amplitude. No acquisition is asserted by the chapter. |
| 058 / 355-360 | Strict data admission and actual asset hashes precede off-thread compilation. Profiles preserve unknowns, units, waveform boundaries and effect ownership. Printed companion-validator successes are atlas source claims, not tests executed in this repository. |
| 059 / 361-366 | Fit identifiable boundaries upstream first; preserve gain/time calibration, phase history and held-out takes. Optimizer termination and fit quality are distinct from physical fidelity. |
| 060 / 367-372 | Canonical absolute event stimuli, separate evidence levels, stage-local oracles, stable ties, block partition invariance and wrapper comparisons. GUI appearance cannot be an audio oracle. |
| 061 / 373-378 | Similarity, discrimination, equivalence and preference are separate questions. No user panel or listening-fidelity result exists merely because a protocol is written. |
| 062 / 379-384 | One audio owner; bounded queues and callbacks; explicit overflow recovery; off-thread preparation/reclamation; measured timing, allocation and contention scope. Numerical work counts are not CPU benchmarks. |
| 063 / 385-390 | The same framework-independent engine serves offline, VST3 and standalone. Half-open timing, zero-frame flush, disconnected positive calls, safe ownership, persistent controls and exact DSP checkpoints have different contracts. |
| 064 / 391-396 | Thin wrappers own devices, event conversion and lifecycle. Standalone output-only operation, real device reconfiguration/recovery and retained state need actual execution. Framework choice is optional; exact dependency versions and terms must be recorded. |
| 065 / 397-402 | Stable parameter identities and laws, independent retained banks, captured drag identity and explicit migration. The atlas's proposed 62-control registry is not this repository's implemented registry. |
| 066 / 403-408 | Platform builds, installed artifacts, signing, real devices, upgrades and model fidelity are separate gates. A nominal initial instrument is allowed when its model scope is visible. |
| 067 / 409-414 | Walnut/charcoal/brass direction; semantic labels separate from decoration; bank editing independent of routing; real ownership and snapshot-driven rendering; selected visuals require execution. |
| 068 / 415-420 | Performer tasks determine layout. Keep manuals together, distinguish edited/sounding registration, preserve note ownership through focus and resize, retain inactive percussion positions, and test actual keyboard/mouse workflows. |

## Decision: standalone is a valid independent next slice

Pages 385 and 391-396 call for thin adapters around the same engine. The
repository already has the headless engine and VST3 prototype that page 396
places before standalone device handling and the editor. An optional SDL2
standalone can therefore advance M9 engineering while the other checkout
continues scanner work. SDL2 is the integrator's selected implementation
dependency, **not a framework selected by the atlas**.

Keep the current core, parameter meanings and state formats authoritative. The
standalone must expose the existing nominal dry model and report which output
backend is active. Page 408 permits a nominal initial release with a visible
scope; it does not waive device, packaging or physical-evidence requirements.
This assignment has not inspected the selected SDL2 release's API or license;
the dependency owner must retain that independent review and exact revision.

## Concrete native visual design

Use the prose and semantic inventory as authority. The actual image on page 409
is an AI art-direction image: it has erroneous/ambiguous labels and key counts,
and includes a Stop control although the baseline prose requires a separately
identified stop extension. Reproduce its material treatment, not its control
mistakes. Page 415 is a deliberate flat control-placement drawing, explicitly
not an executed screenshot. It shows four bank summaries and two complete
manual layouts and is a useful information hierarchy reference.

| Native surface | Implementable direction and source |
| --- | --- |
| Frame and title | Warm walnut side cheeks and border; restrained serif title if an admitted font is available; geometry and finish remain original illustration. Use shallow recesses and narrow edge highlights, not perspective that shrinks targets (409, 411, 420). |
| Main deck | Low-glare charcoal `#242725`, ivory `#F2E7CF` text/controls and brass `#D6B67C` highlights. Dark green service/inspection surfaces distinguish a secondary workspace without implying signal magnitude (409, 411). |
| Focus | Highly visible `#A5E4DF` focus outline with an explicit geometric border; do not communicate held, focused, selected and unavailable states only through color (411-412, 417). |
| Registration strip | Show upper/lower SOUNDING route and EDIT bank separately, plus unsaved-control state. Device/backend state and nominal-model identity must remain readable (410, 415-416). |
| Drawbars | Nine editable drawbars per manual with independent A/B editor selection, plus an inactive-bank summary. Cap, shaft, recessed track, markings, readout and hit target are separate layers. Larger values extend toward the player/downward in this view (410-412). |
| Manuals | Two 61-playing-key manuals together. Count playing keys separately from any reversed preset octave. Preserve note identity when the window scales. Use a full-range overview and optional enlarged range if necessary (410, 415, 417). |
| Pedals | Expandable 25-key drawer and two independent existing nominal pedal controls. Opening the drawer changes no routing (410, 415, 417). |
| Performance controls | Existing four percussion controls and expression remain immediately reachable. Show upper-B percussion eligibility without rewriting retained switch positions (410, 418). |
| Secondary controls | Save/load controls and device settings are separate from vintage route selection. Service information can show model identity and unimplemented stages. Omit inactive decorative knobs that suggest implemented processing (413, 416, 418). |
| Motion and simple display | No animation is required for the dry prototype. A quiet/flat appearance can reduce shadows while preserving target geometry and functions. Rendering consumes snapshots and never advances audio state (411, 413-415, 420). |

The atlas suggests layouts at 1440x1000 and 900x900 plus small-window/zoom
inspection (414). Native acceptance should name the sizes actually supported,
including the minimum size and high-DPI scale. Do not claim either proposed
layout passed until the actual application was rendered and inspected there.

## Adapt the atlas honestly to the current engine

The atlas is the long-term plan; the current runtime has a smaller, deliberately
different contract. Do not expand or change a stable public law to match a
picture during this standalone session.

| Atlas aspiration | Current runtime and required presentation |
| --- | --- |
| 62 proposed control parameters (397, 401) | Keep the existing 45 descriptors and their actual numeric IDs/semantic paths. The atlas's proposed ID ranges are not a migration instruction. |
| Continuous physical drawbar travel (393, 397-398, 411) | Current drawbars have nine discrete positions, 0-8, with `step_count=8`. Render and edit those actual positions. Mark continuous-contact physical modeling as future work rather than claiming a continuous conductance model. |
| Mechanical expression travel (398, 418) | Current `global.expression` is explicitly a normalized linear-gain surrogate. Call it nominal expression/gain, not a measured physical pedal law. |
| Two historical pedal footage controls (397, 410) | Current sound model has two explicitly nominal mixtures. Preserve their registry names and scope instead of advertising calibrated 16-foot/8-foot responses. |
| Twelve reversed preset keys per manual (410, 415) | Core supports A/B selection and routing-only Cancel; fixed chapel presets are still pending. Render only functional actions, or clearly disable/document the remaining fixed keys. Never map them to arbitrary new registrations. |
| Scanner and rotary controls (398, 410, 413, 419) | They are not active in the dry Engine at this baseline. Report unavailable stages in service information; a decorative cabinet or dormant selector must not imply they are heard. |
| Full native accessibility | Keyboard reachability and visible focus are implementable now. A custom SDL drawing alone does not establish a native accessibility tree, screen-reader support or assistive-technology acceptance (415, 420). |

## Input and gesture contracts to freeze before code

1. **Editor bank is not sounding bank.** Preparing upper A while upper B sounds
   changes only A's retained values. Selecting A changes routing. Show both
   identities at once (410, 416).
2. **A drag captures its identity.** On press, capture manual, bank, drawbar,
   starting value and gesture token. Every update targets that identity. Finish
   the old gesture on bank change, lost capture, view change or destruction;
   require a new press for the newly visible control (399, 412, 416).
3. **Notes have owners.** Pointer and computer-key presses retain original note
   identities. Focus movement cannot retarget a later release. A pointer
   glissando releases its own previous note before pressing its next; one owner
   cannot release another owner's hold (392, 412, 417).
4. **Recovery is explicit.** Off-window release, capture loss and window
   deactivation clear the appropriate UI ownership. Panic is distinct from
   preset Cancel. Cancel changes routing without releasing physically held
   notes or resetting source phase (389, 401, 417).
5. **Keyboard-only operation is real input.** Arrow navigation, a visible
   focused key, limits via Home/End, button activation and a documented step
   direction are required. Performance shortcuts must not steal text entry
   when a text field is active (412, 417-418).
6. **A control snapshot is not a checkpoint.** Saving excludes transient held
   notes, oscillator phases and envelope history. Loading validates off-thread
   and applies coherently; devices/window geometry are machine/editor state,
   separate from musical controls (389, 394, 396, 401).

## Audio ownership, callback and device contract

- One serialized audio context owns Engine, note ledgers and the sample clock.
  UI rendering, resize, file dialogs and snapshot serialization do not access
  their mutable histories directly (379, 385, 388-389).
- Fixed-size event records, bounded queue capacity, bounded examination per
  callback and verified lock-free target atomics must be explicit. An SPSC queue
  cannot accept a second producer without a different design (380).
- Untimed idempotent UI controls may coalesce if their declared semantics allow
  it. Musical releases cannot silently disappear. Queue-full recovery must
  invalidate the faulty event epoch, release its owned contacts at a defined
  boundary and report a fault while preserving autonomous source time (380).
- Allocate/prepare, parse/load/save, destroy resources, log and handle devices
  outside the callback. A `noexcept` declaration is not an allocation or bounded
  work audit. Quiesce callbacks before device reprepare and shutdown (381, 388,
  394, 396).
- Specify UI event timestamps, stable tie order and late-event policy. Preserve
  half-open ownership and zero-frame semantics. Internal slicing must not
  duplicate events or change source time (370, 387, 393).
- Open output audio only; microphone input is not required for this instrument.
  Retain obtained rate/format/channels/buffer size, validate against actual core
  support and explicitly reprepare at a stopped rate change (396).
- Distinguish active silent processing from suspended callbacks. Positive
  processed frames advance source phase; absent callbacks do not justify
  wall-clock catch-up (389, 395).
- Playback/device recovery, unavailable saved device, device removal, reopen,
  MIDI loss and safe teardown need their own observed tests (396, 407). A first
  standalone can state narrower support while these gates remain open.

## Concrete acceptance matrix for the selected slice

| Gate | Evidence required from implementation workers |
| --- | --- |
| Core agreement | Same admitted event fixture and initial profile through standalone adapter and headless Engine; compare audio and final controls at fixed rate under irregular callback partitions. |
| Current control inventory | Enumerate every current descriptor, all four retained banks, two nominal pedal controls, 61+61 playing-key IDs and 25 pedal IDs; unsupported features are not enabled accidentally. |
| Routing and interaction | Inactive-bank edit, bank change mid-drag, Cancel while held, repeated presses, coincident owners, focus movement during hold, off-window release, resize and snapshot restore retain the declared state. |
| Queue pressure | Force capacity exhaustion, identify its fault and recovery, prove no stranded UI-owned note, bounded work and no fabricated successful render. |
| Thread/lifetime | Exercise concurrent UI/control activity and callback processing, repeated start/stop/reopen, load/save while held, and shutdown while callbacks can be active; use appropriate race/allocation instrumentation. |
| Actual native picture | Render the executable at declared window sizes/scales, inspect text/control clipping and key counts, and retain screenshots with artifact/revision identity. A rendering helper or concept image alone is insufficient. |
| Backend execution | Retain actual selected driver, obtained format, rates and callback activity. A dummy-backend run can prove application/callback wiring; it does not prove audible output, physical device reliability or round-trip latency. |
| Performance | Record named system/build, actual callback workload and timing distribution. `N/Fs` is a nominal processing interval, not round-trip latency. Missing underrun telemetry remains unavailable (379, 383-384). |
| Packaging | Test the actual installed artifact and resource notices; relocate it without build-tree resources. Separate build/test success from signing, hardware support and clean-machine distribution. |
| Accessibility | Record actual keyboard/focus behavior and supported scaling. Screen-reader/platform accessibility remains not-run until an actual implementation and user-agent test establishes it. |

No implementation acceptance result is asserted by this review. The current
task was source reading and requirements extraction only. The unchanged dry
model, M3 physical gaps, unresolved audible scanner policy, AO-28/Leslie
connectivity, capture/calibration and release evidence all remain separate.

## Reproduction and next handoff

Working directory for the following commands was
`/workspace/scratch/5ba97739b54c/Hammond-B3-Organ`.

- Read `AGENTS.md`, current status/navigation and parameter source with `cat`
  and `sed`; inspected `git status --short` and `git rev-parse HEAD HEAD^{tree}`.
- Read `/workspace/scratch/5ba97739b54c/atlas/part5.txt` in contiguous line
  ranges `1-400`, `401-850`, `851-1300`, `1301-1750`, `1751-2200`,
  `2201-2650`, `2651-3100`, `3101-3550`, `3551-4000`, `4001-4450`, and
  `4451-5025`. Outputs were bounded and not truncated.
- Verified the PDF with `sha256sum Hammond_B3_Leslie_Research_Atlas_500pp.pdf`.
- Rendered each selected image with
  `pdftoppm -f PAGE -l PAGE -singlefile -scale-to 1400 -png INPUT OUTPUT`
  for pages 409, 411 and 415, then inspected each actual image. Images remain
  scratch review inputs, not redistributed source artwork.

The next owners should freeze the standalone event/queue/device contract,
review the exact SDL2 dependency and build path, then implement the native
workspace against the existing registry. Independent reviewers should execute
the matrix above and record failures before any broader M9 completion claim.
