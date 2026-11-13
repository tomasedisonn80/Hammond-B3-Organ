# Assignment 05: atlas calibration, runtime, host and product requirements

Owner: /root/w01_a05_atlas_product

Wave: 01. Session: 2026-11-13 pedal development. This is a newly dispatched
assignment; earlier readers and earlier executed results are not recounted.

## Coverage and inspected revision

Read **every one-based PDF page 337-420**, covering chapters 055-068. The
provided `pdftotext -layout` extraction was read in seven untruncated chunks:
337-348, 349-360, 361-372, 373-384, 385-396, 397-408 and 409-420.
It contains 25,955 whitespace-separated words. Selected rendered-page visual
inspections cover **338, 357, 381, 392, 399 and 415**. This is complete assigned
text coverage plus selected visual inspection, not independent verification of
every cited external source or every figure.

The preserved [atlas](../../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf) is
21,248,265 bytes, SHA-256
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
The assigned extracted range has SHA-256
`224379375e550a61c346afe4c94d31e900ead0cc96e5138920d47821589bed4c`.

Code inspection used baseline commit
`b4fc61ccfcc59724f14fb0cee947ed7bb7142075`. The working tree also contained the
integrator's in-progress status/instruction updates and this session's review
notes. Those changes were preserved. Read `AGENTS.md`, current status and next
steps, latest development-log entry, the project plan, the current operational
handoff's baseline/architecture sections, and the new session ledger. The
inherited atlas-review and project entry-point context informed navigation.

| Pages | Content actually read | Consequence for this project |
| --- | --- | --- |
| 337-342 | Driver identity, reciprocal electromechanical equations, thermal state, coupled loading and mathematical fixture limits | Keep downstream driver/cabinet behavior out of a pedal-routing claim; physical coefficients remain unresolved. |
| 343-348 | Cabinet reference identity, boundary acquisition, static/moving comparison, uncertainty and final release evidence | Neither an attractive render nor a synthetic oracle establishes measured cabinet fidelity. |
| 349-354 | Acquisition charter, named electrical ports, calibration/timebase, organ/Leslie capture matrices and dataset release | Obtain boundary-specific physical evidence; keep source phase and full gesture histories. |
| 355-360 | Capture/profile contracts, strict import, asset hashes, effect ownership, ancestry and absent companion checks | Preserve unknowns; compile data outside processing; structural validity is distinct from physical admission. |
| 361-366 | Identifiability, upstream-first fitting, physically scaled objectives, permitted alignment and frozen holdouts | A nominal pedal transfer must not masquerade as identified reactor/component values. |
| 367-372 | Documentary versus engine tests, independent oracles, musical adversaries, timing and failure artifacts | Add source-sharing, ordering, partition and state tests at a named boundary. |
| 373-378 | Similarity/discrimination/equivalence/preference, stimulus preparation, blinding and statistical protocol | No single percentage of authenticity and no inherited listening pass. |
| 379-384 | Clock ownership, bounded queues, preparation/reclamation, workload accounting and actual callback qualification | Fixed storage and finite loops need executed allocation checks; offline timing does not establish device deadlines. |
| 385-390 | Framework-independent graph, explicit ports, half-open timing, control state, lifecycle and limited header checks | Reuse one core and one source timeline; separate controls from transient history and SDK objects. |
| 391-396 | Wrapper dependencies, buses, note ownership, automation, state, silence and device qualification | Typed input is useful preparation, but remains separate from an actual VST3/device implementation. |
| 397-402 | Permanent parameter identities, normalized laws, gesture binding, migration and compatibility gates | Preserve current repository identities/laws instead of replacing them with the atlas's different proposed registry. |
| 403-408 | Native build lanes, bundle staging, signatures, installation, upgrades and release records | Qualify the exact artifact and advertised environment; build success alone is not release support. |
| 409-414 | Walnut/charcoal art direction, control inventory, retained-bank behavior, gestures, service views and UI gates | The future UI observes engine state; art and prototype claims do not supply working audio. |
| 415-420 | Player workflows, input/focus ownership, control interlocks, rotary editing and task acceptance | View changes and editor closure must not change external ownership or audio time. |

## Immediate pedal implementation requirements

### Preserve the implemented compatibility contract

The atlas's pp. 397-402 describe an absent **62-parameter proposal**, not the
repository's current implementation. The inspected `data/parameter-registry.json`
has 43 records, schema 2 and model `exclusive-ab-percussion-console-v2`.
`ParameterBridge.h/.cpp` compile this internal subset without callback JSON.

There are material differences, so a literal import would break compatibility:

- Current expression ID `8192` (`0x2000`) means a finite normalized linear-gain
  surrogate. It is not physical expression travel and must not become a
  percussion control or a newly loaded expression circuit under the same ID.
- Current manual drawbars are discrete 0-8 controls. Their fixed thresholds are
  `0.0625, 0.1875, ... 0.9375`, selecting the upper step at an exact midpoint.
  Atlas p. 398 proposes continuous drawbar travel and a different general
  discrete conversion. Neither change may be silently applied to existing IDs.
- Current manual bank IDs use their own retained numerical layout. The atlas's
  proposed bank ranges are not an authority to renumber those records.
- Pedal IDs `0x1400` and `0x1401`, proposed on p. 397, are currently unused.
  They are possible new identities, not a requirement to adopt them or proof of
  any host export. Whatever IDs are selected need a versioned registry and
  cross-language descriptor checks while preserving all 43 earlier meanings.

The pedal controls should have an explicit unit, bounds, default, normalized
law and nominal transfer owner. Pages 389, 393, 397 and 410 require two retained
pedal drawbars independent of all four manual banks. Neither the table nor a
footage label establishes a calibrated four-bus/two-output electrical mixture.

### Compile routing, preserve missing information, label the surrogate

Pages 357-358 and 386 require strict offline import, complete identity domains,
asset verification and declared effect ownership. Preserve all disconnected
pedal positions rather than inventing source zero. A schema-valid unknown
profile is not executable until the selected algorithm's dependencies are known
or an explicitly named surrogate supplies a different, bounded model.

For the selected nominal pedal gate, preserve the documentary routing digest
separately from the proposed transfer coefficients. A dimensionless reference
matrix can be an honest engineering input. It cannot establish reactor
inductance, source impedance, gain in volts, driver/cabinet response or actual
specimen tone. Unknown physical quantities remain unknown rather than zero or
unity. Pages 350, 355, 361 and 386 specifically prohibit treating historical
G-G service readings as pickup/oscillator amplitudes.

Keep one source-frame consumer for pedals. Releasing notes, cancelling a manual,
muting the output, changing an editor view or subdividing a block must not
restart or independently advance the source field (pp. 369-370, 379, 382,
387, 395 and 414). Great's future scanner branch includes lower manual and
pedals; upper-B percussion eligibility stays separate (pp. 398, 410 and 418).

### Make ownership transactional across input and Engine

Pages 392 and 417 require independent origins/presses to retain ownership, so
one release cannot cancel another still-held input. Physical preset gestures,
host program changes and software panic are distinct operations. MIDI velocity
must not quietly become sustained piano-style amplitude.

The inspected current `NoteOwnership` already has useful semantics to retain:

- Two manual-only buses, 16 channels and a bounded 256-owner array.
- First physical owner emits On and final owner emits Off.
- Repeated anonymous owners release FIFO; identified duplicate On is
  idempotent, and conflicting pitch reuse rejects.
- Owners retain their original manual after future bus-route changes.
- Channel AllNotesOff releases only that channel's ownership, rather than
  issuing an Engine-wide panic that would release other owners.
- Translation uses fixed candidate/output arrays, with whole-call validation
  before live state or destination output changes.

`process_owned_notes` then sends the candidate's physical events to Engine and
commits ownership only after Engine succeeds. Pedal support must preserve this
transaction across both manual and pedal state. Do not add a third value to
`Manual` or infer pedal MIDI/octave mapping from source pitch. A new typed pedal
destination or separate bounded pedal owner requires an explicit controller
mapping and release policy. One coordinated authority must own each physical
key/pedal; direct contact edits cannot silently bypass that authority.

For future editor input, capture the original note on press and release that
record even if focus, bank or zoom has changed. Editor closure releases UI-owned
notes only; external MIDI holds survive. These are concrete future adapter
acceptance cases, not behaviors established by the current manual-only adapter.

### Preserve time and separate snapshots from DSP checkpoints

Pages 370, 387, 393 and 400 require half-open positive blocks, explicit stable
same-offset order and zero-frame control flushes that advance no DSP state.
Positive disconnected-output processing still advances the declared timeline.
Preflight malformed offsets, overflow and capacities before mutation. Boundary
offset-N delivery is an adapter ownership rule, not permission to process an
event one sample early.

An appended pedal event must not change existing event numbers or manual
semantics. New tests should cover equal-time pedal On/Off/control permutations,
event-at-boundary delivery, zero-frame changes and regular/irregular partitions.
The present scalar parameter bridge does not reconstruct native host curves;
its existence cannot close the VST3 piecewise-linear-automation gate.

Pages 389, 394 and 401 separate musical controls from exact render checkpoints.
Add pedal drawbars to a new control-state version and migrate old versions
explicitly to muted pedals. Loading an old document must not retain unrelated
preexisting pedal settings from the destination. Snapshot restore must preserve
held pedal ownership, contacts, source phases, percussion readiness and the
render clock. Fresh construction/reprepare starts with a coordinated empty
ownership state. Reading live mutable state concurrently still needs a real
transfer protocol; this session need not pretend that stopped/same-thread APIs
provide one.

## Independent acceptance recommended for the new scope

These are proposed checks for the implementing workers, not tests run by this
reviewer:

1. Compare all 200 admitted native route cells against the independent retained
   documentary readings, including every disconnection and repeated branch.
2. Use independent source-basis and rational-weight sums to validate the chosen
   reference transfer. Preserve source phase across isolated, paired and
   manual/pedal unison cases; do not normalize each registration independently.
3. Retain current manual-only bytes where arithmetic is intentionally unchanged.
   Across supported rates, compare physical-time behavior with declared
   tolerances rather than demanding equality of different sampling grids.
4. Exercise all pedal keys, two retained drawbars, same-time event permutations,
   lower Cancel with held pedals, upper-percussion independence, old-state
   migration, ownership overlap/remapping and rejection atomicity.
5. Instrument allocation and deallocation in the actual enabled runtime path,
   including maximum occupancy and rejection paths. Keep workload timing,
   allocation correctness and real device/host deadlines as separate reports.
6. Retain source/model/map/build identity, input events, sample rate, partitions,
   seed, initial state, independent metrics and failure traces with each example.
   Pass, failure, not-run and inconclusive are different outcomes (pp. 367-372).

The atlas's example rates, block sizes, 30-minute run and 0.40D budget are
proposals (pp. 370, 384), not automatically current support requirements or
observed performance. State the actual supported domain and measured workload.
Likewise, its historical companion fixture counts are not local execution results.

## Subsequent development priorities and evidence dependencies

### Physical calibration

Pages 349-366 prescribe specimen identity and approved ports, calibrated gain,
load and clock, preserved raw bytes, boundary observations and upstream-first
fitting. Acquire generator/contact/routing and dry organ evidence before trying
to correct disagreement through cabinet equalization. Fit electrical stages
jointly where their impedances couple them. An output-only match may identify an
effective product of gains without identifying the individual physical gains.

Freeze splits by complete physical take/session/gesture ancestry; synchronized
channels and derivatives inherit their parent's group. Neighboring windows are
not independent final holdouts. Pilot measurements establish useful uncertainty
and budgets before final evaluation. Missing resolution is inconclusive, not a
pass obtained by enlarging uncertainty. No physical capture, fitted model or
listening experiment is established by this assigned atlas range.

### Host and device product

The next host-oriented steps after a stable core are a reviewed input/control
contract, a minimal headless VST3 adapter and actual standalone device handling
(pp. 385, 392, 396). Choose and pin the wrapper/SDK with its exact notices before
adding it. The atlas reports then-current SDK/JUCE versions and licenses on
pp. 391/403; this reading did not independently verify those external sources,
and it does not select a distribution license.

Qualify real buses, zero/variable blocks, headless operation, native automation,
state migration, nullable/inactive buffers, latency/tails/silence, MIDI echo and
device-loss/reconnect behavior. No-callback suspension follows a declared freeze
policy, not assumed wall-clock catch-up. One shared engine serves offline,
plugin and device wrappers; a second wrapper must not reproduce the sound logic.

A native build, SDK validator, clean-machine install, actual DAW session and
physical-fidelity comparison each establish different things. Preserve precise
tested commit/artifact/platform/configuration and unknown lanes. Packaging,
signing/notarization, upgrade and user-data recovery need actual artifact evidence
before release support is claimed (pp. 403-408).

### User interface

Pages 409-420 propose walnut/charcoal/brass styling, editable text and semantic
controls, player/rotary/service workspaces, reduced motion and a clear flat
alternative. Count 61+61 playing keys, 12+12 preset keys, 25 pedals and 38
retained drawbar settings separately. Editing an inactive bank does not select
its sound; changing views never recalls a registration.

Gestures retain their original semantic identity until explicitly closed,
including bank changes, lost capture and teardown. Parameter playback updates
the display without creating another edit gesture. Explain ineligible percussion
without moving stored controls or deleting contact state. Show physical travel
and software gain as different meanings; the current linear-expression
surrogate must remain labeled until a separately versioned physical model exists.

Artwork and the absent HTML prototype supply design intent, not a working native
editor or a dimensional hardware drawing. The atlas explicitly labels p. 415's
layout study as neither a browser screenshot nor audio. Future visual tests need
observed layouts, keyboard/focus/assistive-technology operation, note-owner
recovery and audio invariance while the editor is absent, resized or stalled.

## Visual observations and actual operations

Rendered each selected page with `pdftoppm -f PAGE -l PAGE -scale-to 1400
-singlefile -png`, then opened all six PNGs through the image-inspection tool.
Temporary images stay outside the repository.

- **338:** inspected both coupled-domain equations and the responsibility
  diagram; the caption does not claim measured driver parameters. Preserve
  electrical and mechanical inductance-derivative terms together.
- **357:** verified that waveform boundary, named ports, effect ownership and
  graph/mapping assets converge on an offline compiler. The diagram explicitly
  marks compilation as a proposal, not a supplied engine.
- **381:** verified preparation/activation/retirement ownership and the warning
  against reclaiming storage while referenced. Arrows describe lifetime, not
  physical circuit connectivity.
- **392:** inspected the host/standalone/editor diagram and its caption. The
  prose defines separate adapters feeding one timestamped contract; the visual
  sequence is not a mandate to route host events through a standalone MIDI clock.
- **399:** verified captured-ID updates, deliberate gesture closure and later
  rebinding; one gesture cannot transfer to a newly visible bank.
- **415:** inspected the complete control-placement study, retained/routed bank
  labels, separate manuals/preset octaves and explicit no-audio/layout-study
  caption. It supports semantic inventory, not browser or audio qualification.

Actual operations were bounded `cat`/`sed` source reads, seven Python page-range
reads, `pdftoppm` and image inspection, `git status`/`rev-parse`, and Python
byte hashes/registry inspection. No native build, DSP test, host/device run,
external-source retrieval, physical capture, listening study, commit or push was
performed by this worker. The only repository file written is this note.
The integrator owns integration, shared status and publication.

Continue the scoped [next pedal gate](../../M3_NEXT_GATE.md), then qualify its
explicit nominal integration. Preserve the compatibility and evidence boundaries
above in code, metadata, tests and the next operational handoff.
