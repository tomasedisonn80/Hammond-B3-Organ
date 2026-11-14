# A05 - Complete atlas architecture, product and interface reading

## Assignment and observed source

Actual worker: `/root/w01_a05_atlas_architecture`. Wave 1 of the newly requested
`2026-11-14-midi-ui` session. This assignment owns this note only; it neither
recounts an earlier reader nor qualifies runtime work performed by another agent.

I freshly read **every extracted word on PDF pages 337-420 inclusive**, comprising
84 pages and all of chapters 055-068. Six complete, nontruncated final batches
covered 337-350, 351-364, 365-378, 379-392, 393-406 and 407-420. An initial combined
tool response truncated part of 337-350; I reread that entire range in a separate
complete output before continuing. I also rendered and visually inspected PDF
pages **409 and 415**, viewed the separately extracted cover concept at its full
1672-by-941 resolution, and compared it with the retained native chapel view.
This is full assigned text coverage and selected image inspection, not a claim
to have independently verified every cited external publication or every figure.

| Source or observation | Exact identity |
| --- | --- |
| [Unchanged source PDF](../../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf) | 21,248,265 bytes; SHA-256 `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769` |
| Complete assigned text, concatenated in ascending page order | 219,580 Unicode characters; 220,115 UTF-8 bytes; SHA-256 `53335771fc1131a2a123fc2b0281022928ece1764a137907e9f070d310e107ae` |
| [Extracted cover/page-409 reference](../../design/atlas-cover-reference.jpg) | 412,664 bytes; SHA-256 `9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187` |
| Observed checkout HEAD | `0f7b90037e51e101d8fa0bfe31af40209d751659` |
| Observed worktree | New MIDI/UI scope, design reference and current-session notes were untracked; I preserved them. |

The text was the parent's `pdftotext -layout` extraction, split on page form
feeds into `page-NNN.txt`. I independently hashed the actual PDF and reference
image, and hashed the concatenated assigned text. Visual rendering used Poppler
`pdftoppm -f 409 -l 409 -scale-to 1400 -png -singlefile` and the corresponding
415 command. Rendered inspection files remain temporary outside the repository.

I read the standing [agent rules](../../../AGENTS.md) and current
[MIDI/UI scope](../../MIDI_UI_SCOPE.md), the full [plan](../../PLAN.md), existing
[atlas consolidation](../../research/ATLAS_REVIEW.md), current standalone handoff
and status context, newest development-log entry, and the actual
[Session declaration](../../../apps/standalone/Session.h) and
[adopted parameter contract](../../PARAMETERS.md) relevant to this assignment.
The atlas's historical companion executions are source claims; they are not new
test runs in this checkout.

## Result for the selected development phase

The proposed external-MIDI adapter and native visual refinement are appropriate
independent **M9 product work** against the existing nominal dry core. Chapters
062-064 deliberately separate framework-independent audio processing from
device/host conversion, display and asset preparation. Their requirements do not
require inventing a completed scanner, AO-28, physical Leslie or calibrated model
before useful input/UI work can proceed.

They also do not permit those product improvements to clear M3-M8 physical gates.
The source demands boundary-specific measurements, upstream-first calibration,
independent uncertainty and held-out results. It explicitly separates waveform
similarity, functional behavior, usable controls and measured hardware fidelity.
The new session must retain that distinction in its README and screenshots.

The highest-priority implementation constraints are:

1. Keep the **existing 45 adopted controls and normalization laws** authoritative.
   The atlas's 62 proposed IDs are a different, missing companion contract and
   conflict with portions of the repository's current numeric namespace.
2. Preserve **one Session producer**, a bounded backend inbox, explicit ordering,
   scoped recovery, joined shutdown and clearly stated callback-boundary timing.
3. Keep **external and UI note ownership independent**. Focus loss, editor close,
   tab changes and pointer cancellation must not release controller-held notes.
4. Treat the cover as the exact **appearance reference**, while keeping control
   labels, musical inventory, states and unavailable features truthful.
5. Retain actual native screenshots and concrete visual differences. A concept
   render, source-asset hash or attractive screenshot is not a pixel-equivalence
   result, working audio proof or native accessibility result.

## Chapter-by-chapter findings from the full reading

### Chapter 055, pages 337-342: speaker nonlinearities

The identified historical driver stock numbers and nominal 16-ohm labels do not
supply complex impedance, mechanical parameters or a thermal model (p337).
Diaphragm motion belongs to the stationary drivers; rotor angle belongs to the
rotating acoustic structures. Published loudspeaker mechanisms may motivate a
model, but their fitted example values cannot become specimen-specific Leslie
constants.

The electromechanical derivation on p338 couples electrical and mechanical signs
through magnetic coenergy. Displacement-dependent inductance contributes to both
voltage and force. Air mass and acoustic loading must each have one owner.
Page 339 gives thermal memory its own units, positive capacities/conductances,
elapsed-time schedule and retained cooling state; it also flags a tenfold copper
coefficient discrepancy in a cited source. Preset changes and note releases must
not reset thermal history.

Page 340 places amplifier, crossover and driver loading in a coupled solve and
requires a bounded solver and explicit convergence fallback. Thermal update
boundaries must follow elapsed samples, not callback counts. Pages 341-342 require
calibrated electrical, acoustic and possibly displacement evidence, followed by
separate linear, numerical, nonlinear, thermal and integrated gates. The printed
1024-state algebra fixture establishes only its stated instantaneous identity.

**M9 implication:** cabinet artwork cannot imply that these mechanisms run in the
dry app. A service view may identify the missing subsystem and its source basis;
it must not fabricate driver temperature, acoustic output or distortion telemetry.

### Chapter 056, pages 343-348: Leslie validation

A fidelity result names a cabinet, fitted parts, configuration, electrical port,
microphone scene and operating domain (p343). The cited Model 600 and 122A
experiments are contextual methods, not this project's reference recordings.
Changing driver connection, panel state or a fixture changes the observed load
and must remain in the record (p344).

Stationary angular transfer captures preserve complex phase, absolute gain,
arrival time and raw data; interpolation needs withheld angles (p345). Dynamic
tests retain input, microphone channels and independently measured horn/drum
trajectories on a qualified common timebase (p346). Near-null acoustic phase
excursions cannot be used as unqualified mechanical acceleration estimates.

Page 347 requires predeclared budgets based on measurable uncertainty, distinct
per-condition failures and explicit inconclusive results. Flexible alignment or
time warping cannot erase the delay being tested. Page 348 freezes the model and
dataset before final musical/listening evaluation, with independent session or
configuration splits. Failure to detect a difference is not proof of identity.

**M9 implication:** visible cabinet geometry and microphones are an illustration
until linked to implemented, qualified renderers. Keep numerical state, physical
evidence and visual presentation as separate claims.

### Chapter 057, pages 349-354: physical acquisition

The campaign begins with actual specimen/revision identities, permissions,
configuration photographs, qualified access and an external-output pilot
(p349). AI can prepare and validate scripts but cannot invent inaccessible-node
measurements. The G-G historical service boundary is specifically not a raw
pickup measurement (p350).

Complete channel calibration includes scale, frequency response, clipping,
noise, skew and a clock record; shared recording time does not by itself prove
absolute clock accuracy (p351). Source phases, attacks and releases, repeated
gestures, percussion recovery and scanner state need a structured acquisition
matrix (p352). Stationary identification and moving-system evidence have
different interpretations (p353). Raw hashes, controls, splits, rights and failed
or ambiguous runs survive in the released dataset (p354).

**MIDI implication:** an incoming velocity is a nominal control gesture, not a
measured trajectory. Hardware MIDI-clock observations are also not a physical
audio-clock calibration. Device timing and model fidelity need separate reports.

### Chapter 058, pages 355-360: data and provenance

The proposed capture/profile schemas distinguish recorded bytes, interpretation,
fitted parameters and compiled runtime representation (p355). Unknown scalars
are null with reasons, not zero or unity; physical values carry units, evidence,
provenance and uncertainty (p356). Source numbers 1-91 are not MIDI notes,
physical terminals or array offsets. A registry of component values is not a
connected AO-28 netlist, and duplicated effect ownership must be rejected (p357).

Strict parsing, reference resolution, actual-byte/hash/header checks and
off-thread compilation precede publication (p358). Sorted JSON is not asserted
to be JCS. Derivatives preserve parent identity, transform recipe, permission
scope and acquisition-group membership (p359). The printed schema validation
record on p360 is expressly limited metadata evidence; missing companion tools
are not recovered by citing its test count.

**UI implication:** any source artwork reused for decoration needs its original
identity and derivation record. Cosmetic assets, dynamic labels and interactive
state remain distinct. A screenshot file alone does not record which executable
and controls produced it.

### Chapter 059, pages 361-366: fitting and inference

The toy gain ambiguity on p361 illustrates why output-only similarity cannot
identify all internal parameters. Page 362 requires topology, polarity, mapping
and calibration first, then fitting outwards from known boundaries. Cabinet EQ
cannot repair a wrong source map or scanner polarity.

The objective on p363 separates physical units, calibrated residuals, covariance,
priors, heuristic weights and robust-loss assumptions. Page 364 limits nuisance
corrections to supported shared gain/offset/clock or initial-state corrections;
independent note-by-note alignment hides model errors. Numerical convergence is
not parameter evidence (p365). Complete-take/session splits, independent final
tests and boundary-specific residuals survive in the release report (p366).

**M9 implication:** no invented percentage of authenticity belongs in the player
or service interface. Preserve explicit nominal labels and named missing inputs.

### Chapter 060, pages 367-372: independent regression

The printed documentary checks have narrower scope than audio, host or physical
validation (pp367-368). The proposed corpus uses canonical absolute event times,
initial state, profiles and named intermediate observations. Shared sources,
legato percussion, partial releases, same-time event permutations, Cancel and
scanner changes expose important state interactions (p369).

Page 370 requires timing independent of callback partition: an event at a boundary
is applied once, zero-frame flushes advance no time, and randomness cannot depend
on callback number. Across-rate comparisons need physical-time alignment and
declared tolerances, not bitwise equality across different sample grids. Page 371
requires independent signal/circuit/acoustic oracles and constrained corrections.
Page 372 names the actual source/toolchain/stimulus/partition and first divergence
in each failure artifact. Pass, fail, inconclusive and not-run remain distinct.

**MIDI implication:** test arrival-order and equal-time ordering explicitly,
including off/on versus on/off. A native pipeline test should compare the same
admitted event sequence with a direct Session reference and inspect both controls
and note ownership. Do not call callback-boundary delivery sample-accurate.

### Chapter 061, pages 373-378: listening and claim scope

The source separates similarity, discrimination, equivalence and preference;
none is a percentage of physical authenticity (p373). MIDI-controller gesture
evaluation is a separate experiment from reference-hardware audio comparison
(p374). Fixed justified gain preparation is distinct from per-excerpt
normalization, which can erase the control behavior under evaluation (p375).

Auditory training, instrument experience and usability expertise are separate
participant roles, and blinding has explicit limits (p376). Effect sizes,
equivalence margins, repeated-observation dependencies and failure/inconclusive
rules must be chosen before outcomes are known (p377). The final study needs
actual captures, participants, raw responses, locked build/stimuli and a complete
analysis record (p378); this atlas chapter contains a plan, not such a study.

**UI implication:** user-interface appeal and musical usability can be evaluated
without declaring acoustic equivalence. Retain separate future gates for actual
controller feel, real-device latency, musician tasks and blinded listening.

### Chapter 062, pages 379-384: bounded work, queues and lifetime

One serialized audio context owns mutable DSP state and elapsed render time
(p379). UI frames or a second receiver cannot create an additional clock.
Callback duration divided by N/Fs is an observation, not round-trip latency or
a guarantee of an exclusive processing deadline.

Page 380 directly constrains the planned MIDI transport:

- Use fixed-capacity, trivial records and verify target atomic properties.
- A single-producer/single-consumer queue may have only one producer; merge
  independent producers outside the audio context or provide distinct queues.
- Freeze capacities, maximum admitted density and bounded work before coding.
- Preserve timestamp and tie order; coalesce only suitable untimed idempotent
  UI requests, never note transitions or sample-positioned automation.
- Overflow faults the event epoch, releases its owned contacts at the defined
  boundary and reports the discontinuity. It is not a successful render with
  inconvenient note-offs silently dropped.
- Diagnostic loss may be counted, but telemetry must never stall audio.

Prepared-resource publication requires a lifetime/retirement protocol; final
reference-count destruction on audio is still destruction (p381). Arithmetic
counts and SIMD lane counts are not performance results (p382). Page 383 calls
for actual bounded telemetry, cold and steady paths, GUI contention, full timer
and machine identity, and separate sanitizer/performance evidence. Page 384's
timing target is an initial proposal, not an already established device result.

**Recommended adapter acceptance:** deliberately fill ingress and Session queues,
interleave UI/device holds, disconnect during a held chord, restart repeatedly,
delay the consumer and exercise shutdown with callbacks in flight. Retain the
exact scope of any measured allocation or concurrency result.

### Chapter 063, pages 385-390: one engine, explicit timing

The wrapper owns SDK objects, buses and conversion; the shared engine owns the
same musical graph for offline, VST3 and standalone uses (p385). Physical coupling
determines solver boundaries; convenience does not prove circuit independence.
Profile compilation preserves units, identities, ports and unresolved inputs,
selecting a named nominal surrogate where justified (p386).

The proposed render counter is monotonic and independent of transport. Positive
blocks own half-open intervals; offset-N events carry into the next block, and
equal-time records use stable sequence order (p387). Zero-frame flush commits
targets without advancing history. Positive disconnected-output calls still
advance time. Curve reconstruction and physical smoothing are separate owners.

Publication transfers prepared ownership and uses generations and retirement;
shutdown establishes quiescence before freeing storage (p388). Musical state is
separate from transient histories, clocks and optional exact checkpoints (p389).
The original header's nineteen static assertions establish only their narrow
type/syntax contract, not runtime or host acceptance (p390).

**Current repository application:** `Session.h` reserves channel 0 for UI and
accepts only offset-zero musical commands through one main-thread producer.
The new scope's three selected wire-channel routes map to internal channels
1/2/3, retaining UI channel 0. This is a declared limited routing design, not
simultaneous sixteen-channel multi-device support. State-file and core changes
are unnecessary for that bounded adapter.

### Chapter 064, pages 391-396: thin host/device adapters

Dependencies, SDK revisions and notices are pinned independently; the atlas's
JUCE candidate is not a mandatory engine framework (p391). Device enumeration,
timestamp conversion and recovery belong to the standalone adapter. Separate
note owners survive repeated pitches and independent sources; velocity must not
silently become piano-style sustained loudness (p392).

Stable control identity, curve timing and explicit tie order remain mandatory
(p393). Musical controls, machine-specific setup and editor state are different
domains; replacement is prepared outside audio and activated at its declared
boundary (p394). Silence follows actual output, and suspended callbacks do not
automatically advance modeled time (p395).

Page 396's concrete standalone gate includes disconnect/reconnect, rate change,
MIDI loss and stuck-note recovery. Timestamp-to-audio-clock conversion and late
events must have a documented policy; a thread-safe collector is not thereby
lock-free or deadline-qualified. SDK, DAW, offline and physical-device reports
remain separate, each with named versions and configurations.

**Next-phase requirement:** retain RtMidi delta/arrival information for diagnostics
only under the current Session boundary contract unless a separately reviewed
scheduler is implemented. Define malformed/nonfinite/out-of-order timestamp
handling explicitly; never silently promote receipt time to acoustic onset time.

### Chapter 065, pages 397-402: compatibility and gesture identity

The atlas's 62-entry registry, continuous drawbar law and proposed numeric ranges
are explicitly proposals (p397). They are not the current 45-control repository
contract. Page 398 describes an enum conversion different from the current
frozen nominal bridge, so copying that formula would alter existing automation.

Each gesture retains the original parameter/manual/bank until it closes; hiding
the bank must not hide its parameter from host automation (p399). Native curve
position and previous-block anchoring remain separate from scalar current values
and smoothing (p400). Wired preset selection, complete control recall, specimen
profile, editor state and full render checkpoint have different scopes (p401).
Static metadata checks do not replace executable wrapper and compatibility
qualification (p402).

**Implementation rule:** use the existing `ParameterBridge` for MIDI CC conversion,
preserve both inactive and sounding banks, and state whether each hardware control
targets a fixed bank or a selected route. Avoid a hidden dependence on which bank
the player happens to be editing. No current IDs or saved formats need changing
for the selected MIDI/UI work.

### Chapter 066, pages 403-408: qualification and packaging

The product envelope and native lanes remain proposed until actually executed
(p403). Every release joins compiler/dependency/profile identity, notices and
runtime support. Core tests remain headless, and adapter builds share the same
engine (p404). Platform signature, universal-slice and notarization evidence is
distinct from source or audio correctness (p405).

Windows/Linux packaging preserves whole bundles, resources and user data, and
tests actual backends, Unicode/space paths, missing optional dependencies and
non-admin use (p406). Installed-product gates include MIDI reconnect, unavailable
saved devices, state upgrades, UI scaling and concurrent audio (p407). Final
artifact hashes are recomputed after packaging; a missing platform is not
qualified by another platform's successful build (p408).

**MIDI packaging implication:** optional backend-off builds must remain usable,
backend-on configuration must verify the locked source and required OS libraries,
and installed binaries must report capability honestly. A dummy/no-device test
may qualify error handling but cannot qualify a controller or physical timing.

### Chapter 067, pages 409-414: sculpted reference and truthful controls

Page 409 is the exact cover art reused inside the design chapter. The observed
image supplies the overall arrangement: heavy walnut cheeks and lower rail,
charcoal/brass header, PLAY/ROTARY/SERVICE navigation, top percussion/scanner
strip, adjacent upper/lower drawbar groups, two stacked manuals beneath and a
right cabinet/microphone region. It is explicitly AI-generated atmosphere with
proposed proportions; its key count, labels and control values are not engineering
authority.

The required four retained banks, independent editor/sounding identity,
routing-only Cancel and separate pedal/percussion/scanner controls are textual
semantics on p410. The source describes 61 playing and twelve reversed preset
keys per manual plus 25 pedals, but the current app only implements its admitted
subset. Visual references do not automatically implement fixed presets.

Page 411 requires separately layered geometry, finish, semantic text and state.
At zero the drawbar cap is near the upper edge; eight extends toward the player.
The concept's printed numbers do not override that direction. Dynamic legends
must not become frozen raster artwork. Serif titles, readable sans settings,
brass `#D6B67C`, charcoal `#242725`, ivory `#F2E7CF` and cyan `#A5E4DF` focus are
declared design choices, not measured material properties.

Page 412 preserves captured gesture IDs and independent pointer/computer-key
owners through focus and view changes. Page 413 treats cabinet motion as optional
illustration, forbids fake measurements and distinguishes available versus
unmeasured service data. Baseline 122 commands are Chorale/Tremolo; a Stop action
requires its own accessory/extension profile despite the cover's STOP button.
Page 414 asks for actual screenshots and interaction evidence at declared sizes,
with decoration off audio and frame stalls unable to change a pending release.

**Visual acceptance implication:** reproduce appearance where it improves the
reference match, but do not reproduce false control legends, frozen state,
unsupported active scanner/rotary controls or an invented meter. Exact visual
equivalence has not been measured by this reading.

### Chapter 068, pages 415-420: player tasks and ownership

The visually inspected p415 is a **control-placement study**, not a browser
screenshot or the cover reference. It shows all four banks as an explanatory
inventory, whereas the actual player proposal allows one editor per manual and
an inactive-bank summary. PLAY/ROTARY/SERVICE are views over one instrument state;
changing a view must not recall sound. Pedals and input routing may use drawers.

Page 416 separates editorBank and soundingRoute and keeps modern file recall
separate from physical preset commands. Page 417 gives the precise rule needed
for external MIDI integration: every UI press retains its original identity;
closing/deactivating the editor releases only UI-owned notes, leaving external
MIDI owners intact. Glissando releases its own old key before the next press;
resize changes geometry rather than pitch or ownership.

Page 418 keeps a percussion switch's stored state visible while explaining
upper-B eligibility and the 1-foot suppression without overwriting its drawbar.
Expression travel and software output gain are different quantities. The current
nominal expression surrogate must keep its current honest label and meaning.

Page 419 separates command state from each rotor's evolution and microphone
editing from phase. Geometry bounds alone are not acoustic clearance evidence.
Page 420 requests actual musical-task traces: inactive-bank preparation, changing
banks mid-drag, Cancel under a held chord, off-window release, restoration and
operation without animation. Keyboard/assistive tasks are assessed independently
of mouse usability and audio fidelity.

## Concrete recommendations to implementation owners

### MIDI contract to freeze

| Contract decision | Recommended explicit behavior or evidence |
| --- | --- |
| Connection scope | One selected backend port; three distinct configurable wire channels 1-16, defaulting upper/lower/pedals to 1/2/3. Reject duplicate/invalid route configuration. Other wire channels are ignored with a diagnostic count. |
| Internal ownership | Map the configured routes to channels 1/2/3, never UI channel 0. Preserve original admitted target until release. Disconnect releases the device scope only. |
| Repeated pitches | Specify identified duplicate-On and matching-Off policy. Cover velocity-zero release, repeated On, unknown Off and cross-source overlap; no implicit sustained velocity gain. |
| Time | Preserve admitted arrival order and deterministic ties. Declare callback-boundary application, malformed/late timestamp handling and absence of a hardware-latency guarantee. |
| Overflow | Ingress overflow invalidates the device epoch and triggers bounded scoped release; do not process stale queued note-ons after recovery. Existing Session overflow retains its documented global emergency policy. |
| Main-loop serialization | Backend callback writes only the bounded ingress channel. The main/UI owner remains the sole `Session::post` caller. |
| Controls | Freeze exact supported CCs, destination bank/route, conversion via the adopted bridge and policy for CC120/121/123, sustain, program change, pitch bend, realtime and SysEx. Unsupported messages are explicit. |
| Desired UI control merge | The current UI posts whole snapshots. Reconcile each admitted MIDI control into the same desired control state before subsequent UI posts; otherwise a later unrelated UI gesture can restore stale values and undo the MIDI change. Preserve submission order and applied/pending acknowledgment. |
| Shutdown/restart | Quiesce/join the backend before queue reset or destruction. Audio restart, disconnect, selection change and app exit each have a documented owner-release/epoch policy. |
| Saved setup | Machine-specific port choices and routing do not enter `B3CONTROLS3` unless a separate versioned design explicitly adds them. |

These recommendations do not authorize changing the current core controls or
claim that the implementation already exists. Their final frozen behavior belongs
in the implementation contract and must be checked against actual source.

### Reference-oriented native UI work

1. Place the exact source reference alongside an actual native capture, naming
   both identities and the current musical state. Keep the old native view as
   dated historical evidence.
2. Reproduce the cover's header/deck/manual/right-cabinet proportions and material
   depth, including thick walnut rails, narrow brass highlights, recessed panel
   seams, raised tablets, cap shafts and key fronts.
3. Draw all stateful text, highlights, cap positions, focus and held keys from the
   real copied model. Source art may decorate noninteractive surfaces, but it must
   not masquerade as a rendered control surface.
4. Retain 61+61 actual playing-key geometry and 25 pedal targets. Keep implemented
   pedal controls and EDIT/SOUNDING distinctions discoverable even where they are
   absent or inaccurate in the generated cover.
5. Mark unavailable scanner/rotary processing clearly. A static cabinet image is
   a reference illustration; it has no measured RPM, mic-response or audio claim.
6. Verify minimum/reference/wide sizes, label visibility, active hit geometry,
   focus, off-window release, bank-change gesture closure and UI/MIDI overlap.
   Keep any pixel comparison's crop, scale and tolerances explicit.
7. Record residual differences without inventing a similarity percentage. Native
   semantic accessibility, physical display/device qualification, photoreal 3D
   geometry and measured audio remain distinct completion gates.

## Completion and limits

This assignment completed source reading, source/hash verification, selected
image inspection, current-contract inspection and this substantive handoff. It
did **not** modify shared production code, run the synthesizer, execute adapter
tests, claim a visual-equivalence pass, acquire hardware recordings, commit or
push. The integrating agent owns actual implementation, independent qualification,
shared status updates, assignment acceptance and guarded publication.
