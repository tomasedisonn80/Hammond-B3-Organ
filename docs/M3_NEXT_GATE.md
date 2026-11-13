# M3 pedal gates: routing and playable integration

**Routing checkpoint implemented and locally qualified:** the [runtime contract](PEDAL_RUNTIME_CONTRACT.md) and new session notes 07–12 retain its code and independent checks. All 51 Release suites passed on frozen tree `81b1c30436a239d8c04ffcd1ec658d356eb81acc`. The next task is the [adopted playable integration](PEDAL_INTEGRATION_CONTRACT.md); full M3 remains open.

The original routing acceptance plan below is preserved as the basis for those checks. Its task wording describes the now-implemented first checkpoint.

**Routing task:** implement a fixed-storage pedal routing kernel that
consumes the existing 91-source frame and returns four normalized bus excitations.
Use the already corroborated 25-by-8 map. Declare the initial model
`linear-pedal-bus-reference-v1`; this is a proposed engineering identity, not an
existing implementation or a measured pedal voice.

The first checkpoint ends at those four buses. It supplies working routing,
independent contact state and shared-phase tests without guessing the missing
reactor, drawbar mixture or low-wheel spectra. Engine events, two playable pedal
drawbars, persistence and host routing follow the separate integration gate below.
**Neither checkpoint alone completes M3.** The dependency order comes from
[atlas pp. 139–144](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=139) and
[p. 447](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=447).

## Why this task is ready

The current console has independent manual contacts and partial key targets,
retained A/B banks, shared upper-B percussion, saved controls, typed input and
parameter adapters, and phase-preserving rate changes. Its remaining M3 work has
different dependencies:

| Remaining work | Useful work available now | Dependency that remains open |
| --- | --- | --- |
| Runtime pedals | Admit all 200 mapped positions; implement independent connections and coherent four-bus excitation using the shared sources. This is the selected next slice. | Physical mixture, reactor/loading and complex low-wheel spectra; later public event/control integration. Atlas pp. 139–144. |
| Physical preset latching | Represent exclusive selection, Cancel and retained latch masks; reconstruct an explicitly optional fixed-registration profile. | The p. 122 chapel table needs its stated independent review; it is not universal specimen wiring. Multiple latched routes need a declared branch/loading model, not summed registration vectors. Atlas pp. 121–126. |
| Continuous drawbars and switching bandwidth | Implement a separately named travel surrogate or a converged switching reference while retaining the existing discrete/ideal modes. | Contact overlap, make/break timing, bounce and loading require identified models; bandwidth reduction must follow switching at the chosen time resolution. Atlas pp. 109–120. |
| Loaded expression | Define replaceable ports, units and a provisional bounded transfer. | Coupled capacitances, feedback and AO-28 connectivity are needed for the physical response. The existing scalar remains a named approximation. Atlas pp. 145–150, 488. |

Pedal routing has a complete local identity oracle and can be tested independently
of these unresolved physical quantities. The atlas explicitly permits a pure
linear fixture for the routing/coherence comparison on
[p. 144](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=144). This choice does
not prevent separately scoped preset, bandwidth or acquisition work.

## Exact inputs and identity boundaries

Read [PEDAL_ROUTING.md](PEDAL_ROUTING.md), [FACTORY_REFERENCE.md](FACTORY_REFERENCE.md),
[M3_ACCEPTANCE_CONTRACT.md](M3_ACCEPTANCE_CONTRACT.md) and the actual inputs:

| Input | What it establishes |
| --- | --- |
| [`data/pedal-map.json`](../data/pedal-map.json) | Map `atlas-derived-b3-c3-pedal-v1`: 25 one-based pedal IDs, eight ordered contact columns, four bus memberships and explicit null connections. Raw SHA-256 `58a30850c08933a075cfcec04faeb2cb479f60bd9dda82ace3246552221623bd`. |
| [`review-a-pedal.csv`](../data/references/review-a-pedal.csv) and [`review-b-pedal.csv`](../data/references/review-b-pedal.csv) | Two retained independent factory-image transcriptions, each 677 bytes with SHA-256 `b8177479a5af16f4e6b8759313d90148a1213657c83f8a6e6533422bfa104ca1`. Compare every cell, including blanks. |
| [`factory-table-iii.json`](../data/references/factory-table-iii.json) | Later comparison attestation. Preserve it alongside the earlier map provenance; do not rewrite the map's historical `independent_factory_transcription_status` or its hashes. |
| [`TonewheelBank.h`](../include/hammond/TonewheelBank.h), [`Profile.h`](../include/hammond/Profile.h), [`Engine.cpp`](../src/Engine.cpp) | The value-owned source profile and single `process_frame(source_samples)` call shared by all existing branches. Sources are currently nominal normalized sines. |

All page locators here are one-based PDF pages and match the printed atlas pages.
The source atlas SHA-256 is
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.

The map contains **200 positions, 195 connected and five disconnected**. For
one-based pedal `p`, its eight source entries are
`[p, third(p), p+12, p+24, p+31, p+36, p+40, p+43]`, where `third(p)` is `p+12`
for 1–7, disconnected for 8–12, and `p+19` for 13–25. The implementation oracle
must compare against the retained CSV cells, not merely repeat this formula.

| Contact columns, zero-based | Bus identity | Identity requirement |
| --- | --- | --- |
| 0, 1 | Brown | Column 1 is disconnected on pedals 8–12. |
| 2, 3 | Red | Column 2 repeats column 1's source on pedals 1–7, through a separate branch. |
| 4, 5 | Orange | Preserve both contact positions. |
| 6, 7 | Yellow | Preserve both contact positions. |

These bus names come from the atlas diagram; the factory source-number comparison
does not independently establish loom colors, temporal contact order, conductance
or mixture gain. Connected source IDs are 1–68 in this map, within the global
1–91 domain. Use a tagged connection or `optional<ToneId>`: disconnected is not
source 0 and must never become source 1 through an index conversion. Pedal ID,
contact column, tone source ID, physical terminal and MIDI pitch remain distinct.
There is **no pedal MIDI/octave mapping in this input**. Do not infer one from
source pitches, reuse manual foldback, or extend `Manual` to a third value.
See [atlas p. 140](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=140).

## First checkpoint: contract and working kernel

The names below are **proposed files/APIs to create**, not existing capabilities.
Complete these steps in order; the first is small enough to review before DSP work.

1. **Freeze the typed boundary and executable admission fixture.** Add
   `docs/PEDAL_RUNTIME_CONTRACT.md`, `include/hammond/PedalRouting.h` and a focused
   `tests/test_pedal_routing.cpp`. Define validated one-based `PedalId` (1–25),
   contact index (0–7), four distinct `PedalBus` values, a 25-by-8 tagged route
   definition and 200 separate binary connection states. Specify atomic failure
   and initial open contacts. The admission test must accept the exact map and
   reject malformed IDs, missing positions and incorrect bus membership. Do not
   add guessed physical travel thresholds or reuse the manual 8/12 ms trajectory.

2. **Compile the existing data outside processing.** Add an offline
   `tools/compile_pedal_routing.py` that uses the strict pedal-map validator and
   emits a build-directory C++ table with map identity, raw/canonical hashes and
   the separate factory-comparison identity. Wire its dependencies explicitly in
   CMake. Python is already a required build dependency. The generated table is
   a routing input, not a modified `B3PROFILE1` or a physical parameter profile.
   Cross-check the resulting native table against both CSVs in a test; comparing
   only the compiler's input and output is insufficient.

3. **Implement `PedalBusKernel` in `src/PedalRouting.cpp`.** Its `prepare` copies
   validated routes and an explicit fixed-size reference-weight array. The
   caller must supply the named dimensionless fixture weights; there is no
   implicit factory mixture. For this reference contract, require finite weights
   in `[-1,1]` and source samples in `[-1,1]`. These are engineering normalization
   bounds, compatible with the current source amplitudes, not measured resistor
   or voltage values. A failed prepare preserves the previous prepared state.

4. **Add bounded contact edits and rendering.** `apply_contacts` accepts at most
   200 typed contact edits, preflights the complete batch and then applies it in
   supplied order; repeated edits have the last supplied state. Empty edits are
   a no-op. `render_frame` consumes one `array<double,91>` by const reference and
   returns one `array<double,4>`. For each connected, closed branch, accumulate
   `weight * source[tone_id - 1]` into its assigned bus. Retain all 200 contact
   states, including the five inaudible positions. Reject invalid input without
   changing state or destination. No source ownership, time advance, heap,
   parsing, locks, logging or unbounded iteration belongs in these methods.

5. **Retain the simple scalar reference and prove the invariants below.** At
   most 200 branches are examined per frame; each bus has at most 50 positions,
   so the normalized reference has a finite absolute output bound of 50 per bus.
   Keep branch identity before accumulation. No polyphony normalization, limiter,
   artificial release envelope, monophonic policy or guessed four-bus audio mixture
   belongs in this checkpoint. Unit/rational test weights are test stimuli,
   never measurements or default physical parameters.

6. **Qualify and hand off the exact implementation.** Add the focused native and
   independent data comparison tests to CTest, exercise allocation instrumentation
   and maximum occupancy, and run the existing regression gates against the
   coherent source/header tree. Document the actual model, data and binary/source
   identities, results, remaining limitations and next integration step. The
   integrating agent updates shared status and publishes according to
   [AGENTS.md](../AGENTS.md); a worker reports its scoped changes first.

No new file parser or musical snapshot version is needed for this first kernel.
Generated routing data stays separate from the reference weights supplied by the
test/harness. Physical resistance, inductance, loss, transfer functions and
uncertainty remain absent or explicitly unknown in their own future profile.

### Acceptance for the first checkpoint

| Gate | Required observable result |
| --- | --- |
| Complete mapping | Native data agrees with both CSVs at all 200 positions. Explicit fixtures cover pedals 1, 7, 8, 12, 13 and 25, both exceptional boundaries, five tagged disconnections, and source IDs 0/92 rejecting. |
| Independent branches | Toggle each of the 200 positions separately. The seven repeated source pairs contribute independently to Brown and Red; distinct rational weights expose accidental deduplication or wrong bus assignment. Closing a disconnected position leaves all four outputs unchanged. |
| Linear oracle | Inject source-basis frames and mixed frames; compare against an independently indexed scalar sum. Binary-exact rational fixtures must agree exactly; ordinary floating fixtures use a declared rounding bound based on at most 50 contributions, fixed before the run. |
| Shared source and phase | In a harness, call `TonewheelBank::process_frame` once per model frame and give that same array to manual-reference and pedal branches. Their linear combined contribution equals the sum of isolated contributions. All 91 source histories agree with an otherwise identical source-only run through contact edits, silence and unused pedal outputs. This proves the harness contract; actual Engine integration is the next gate. |
| Lifecycle and atomicity | Unprepared use, invalid definitions/weights/source frames, invalid pedal/contact IDs and batches over 200 reject without partial mutation. Partition the same contact schedule into fixed and irregular blocks. Zero-frame control application advances no source; a phase-preserving source-rate change leaves pedal connection state intact. |
| Bounded work | All 25 pedals and 200 positions may be active. Record no allocations/deallocations in enabled runtime paths and the measured maximum-workload result. A fixed loop bound or a fast offline run alone does not establish a device callback deadline. |

These checks close a **routing/reference-kernel software gate**. They produce no
claim about pedal loudness, timbre, octave conventions of a controller, physical
contact timing, reactor response or a complete playable pedal division.

## Following checkpoint: playable nominal pedal integration

After the kernel is accepted, the next implementation contract must settle an
explicit named four-input/two-output transfer and how the two pedal drawbars
select it. A documentary map alone cannot supply those coefficients. A useful
nominal transfer may be authored with stated assumptions, units, limits and
regression identity; it must not silently inherit manual drawbar gains, patent
harmonic strengths or zero-valued unknown electrical components. A loaded model
instead requires the reference network on
[atlas p. 142](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=142), independent
solve comparisons and preserved reactive state. Do not assume two independent
drawbar axes if the selected network couples them.

The public integration gate then requires all of the following:

- **One source frame and an explicit lower path.** Integrate at the existing
  per-frame source array in `Engine::process`; never call a second generator or
  render the Engine twice. Preserve a distinct pedal/lower-path contribution
  before the current common expression/output scaling. Lower-manual Cancel
  affects its manual route and leaves independently held pedals intact. Pedals
  cannot enter the upper ninth-contact percussion detector or its sustain mask.
  The future Great/scanner path must retain that division identity.
- **Typed events and ownership.** Preserve existing `EventType` numeric values
  0–9, `Manual` values 0–1, stable same-offset order, whole-call preflight and
  non-advancing zero-frame flushes. Introduce explicit pedal identity instead of
  overloading manual MIDI 36–96. Current `NoteOwnership` destinations and its two
  input buses are manual-only; a new controller mapping/bus policy needs its own
  reviewed contract. Owners commit only after the corresponding physical event
  batch is accepted. All played pedals can contribute.
- **Controls and compatibility.** Preserve all 43 current internal IDs and
  their laws; in particular, expression ID `0x2000` retains its present meaning.
  Append any pedal IDs through a new registry version with cross-language checks.
  Before adding retained pedal controls, specify a new saved-control version and
  migrate both `B3CONTROLS1` and `B3CONTROLS2` explicitly to muted pedal controls.
  Old document loading must not inherit unrelated destination values. Ordinary
  snapshots still exclude held pedals, owners, contact histories, phases,
  percussion readiness and elapsed time. Live control restore must preserve
  those running histories; fresh construction starts with no held pedals.
- **Actual integration evidence.** Test manual/pedal shared-source collisions,
  lower Cancel/reselection during held pedals, upper percussion independence,
  same-frame changes, all pedal notes, muted-to-audible transitions, rejected
  batches, disconnected output, rate changes and migration. Retain exact legacy
  ideal/Off audio for scenarios without pedal contributions. Extend offline
  evidence and diagnostics with explicit division/model identities before
  presenting a playable pedal example as accepted.

The relevant existing boundaries are [Engine.h](../include/hammond/Engine.h),
[Types.h](../include/hammond/Types.h), [NOTE_OWNERSHIP.md](NOTE_OWNERSHIP.md),
[PARAMETER_BRIDGE.md](PARAMETER_BRIDGE.md),
[CONTROL_STATE_FORMAT.md](CONTROL_STATE_FORMAT.md) and
[SAMPLE_RATE_LIFECYCLE.md](SAMPLE_RATE_LIFECYCLE.md). Atlas
[pp. 121–126](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=121),
[139–144](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=139) and
[148–150](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=148) establish the
Cancel, routing, source-history and common-expression constraints.

## What remains after pedal software acceptance

Nominal M3 software closure still requires declared, tested behavior for physical
preset latch state and fixed registrations, continuous drawbar travel, switching
bandwidth, and a named, tested expression transfer with a replacement boundary
for the loaded model. Tests must cover their
interactions with contacts, retained controls, percussion, pedals and source
history. A provisional M3 implementation may precede a complete AO-28 model;
this is the ordering on [p. 447](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=447),
not permission to classify a surrogate as physically admitted.

Physical pedal admission separately needs an identified applicable specimen,
verified continuity, calibrated boundary/load/phase records, low-wheel harmonic
spectra, the reactor and loss/contact/transformer parameters or identified loaded
transfers, and held-out isolated/paired/manual-unison captures. Intrinsic low-wheel
partials follow their wheel phase; borrowed generator branches keep their own
source phases. Add bandwidth control before those complex spectra are rendered.
The capture matrix on [p. 143](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=143)
is a proposed experiment, not an acquired dataset. Use the independent linear or
loaded-network oracle appropriate to the claimed model, and freeze physical
acceptance bounds with uncertainty before final holdouts
([pp. 141–144](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=141),
[484](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=484)).

| Later milestone | Dependency and acceptance boundary | Atlas locator |
| --- | --- | --- |
| M4 scanner | Reviewed 18-section/19-output network, signed ground/return conventions, depth routing and traversal; independent loaded AC/numerical oracle; chorus return counted once. Resolve the recorded traversal and WDF errata before implementation claims. Numerical work may proceed alongside M3 after source/port boundaries freeze. | [447](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=447), [465](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=465), [ERRATA.md](research/ERRATA.md) |
| M5 AO-28 and direct organ | Select and qualify the upper Figure 24 branch; build reviewed pin-to-node connectivity before a component solver. The 124-value registry is not a netlist. Resolve solid-network R62, expression law and required transformer/valve/load parameters; compare operating point, loaded AC and transients, then identified dry G–G captures. Retain coupled feedback and avoid duplicated expression/loading. | [448](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=448), [488](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=488), [145–150](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=145) |
| M6 Leslie electronics | Qualify the selected 122 circuit and coupling after the dry-organ boundary. Keep 147 separate; retain floating treble A–H and bass W–B crossover ports and actual driver loading. | [448](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=448) |
| M7 rotary acoustics | Independent horn/drum trajectories and causal per-path retarded time; one owner each for propagation, directivity and room response. Keep stationary reverb separate. | [449](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=449) |
| M8 calibration | Acquisition begins earlier and fitting proceeds upstream first. Preserve whole-take/gesture/session holdouts, uncertainty, identified boundaries and predeclared acceptance rules. An inconclusive comparison is not a pass. | [445](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=445), [449](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=449), [484](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=484) |
| M9 host, interface and release | An early host smoke test can proceed after M1/M2. Product closure requires actual VST3/device binaries, exported identity/state/lifecycle checks, bounded publication and retirement, measured callbacks, real host/device and accessibility tests, pinned dependencies, rights and packaging. A header or offline renderer does not close this gate. | [450](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=450), [485](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=485) |

For the actual reading, data checks and limits behind this plan, see the
[assignment 50 evidence note](development/2026-11-13-continuation/50-next-m3-gate.md).
