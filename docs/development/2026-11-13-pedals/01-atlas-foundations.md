# Assignment 01: atlas foundations and shared-source constraints

Owner: /root/w01_a01_atlas_foundations

Wave: 01. Session: 2026-11-13 pedal continuation. This is a new assignment;
earlier atlas readers and their results are not counted again.

## Scope and actual coverage

Read every page of the assigned **one-based PDF range 1-84**, including front
matter and chapters 001-012. The provided `pdftotext -layout` extraction was read
in six untruncated chunks: 1-14, 15-28, 29-42, 43-56, 57-70 and 71-84. It contains
25,183 whitespace-separated words. Selected rendered-page inspections cover
pages **4, 49, 51, 62, 73 and 80**. This is complete assigned text coverage plus
selected visual review; it is not a claim that every original external drawing,
photograph or cited publication was independently acquired or verified.

The preserved [atlas](../../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf) hash
observed with `sha256sum` was
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
The supplied extracted range hash was
`898f91d49ce7f175b4c869246493c8bf8247f60ea455f873a2695ad8f9804efe`.

Code inspection used commit `b4fc61ccfcc59724f14fb0cee947ed7bb7142075`, tree
`6cf1012906aa853e422bdfd06d4451bbda6e7757`, with the worktree clean when observed
before writing this note. Read standing instructions, current status/next steps,
the current handoff and latest development-log entry, the project plan, atlas
review/errata and the preceding continuation record. Historical validation
claims in those documents are inherited records, not tests rerun by this worker.

| Assigned pages | Content actually read | Consequence for implementation |
| --- | --- | --- |
| 1-12 | Scope, evidence classes, source/visual limits, complete contents and M0-M9 order | Agent waves, research waves and product milestones are three different counts. |
| 13-18 | Reference configuration and bounded fidelity claims | Keep nominal development independent of physical specimen admission. |
| 19-24 | Factory drawing locators, revision selection and transcription workflow | A clear redraw or component list does not establish a reviewed circuit graph. |
| 25-30 | Patent applicability and subsystem responsibility | Shared sources are mandatory; patent embodiments do not supply production constants automatically. |
| 31-36 | Cabinet/appearance hierarchy and visual evidence | Artistic geometry cannot supply pedal dimensions or calibrated circuit values. |
| 37-42 | Independent contact states, trajectories and validation | Routing, motion and electrical response need separate owners; ordinary MIDI motion is a declared surrogate. |
| 43-48 | Generator structure, mechanical relations and persistent state | Do not add oscillators for pedals, balancing blanks, keys or repeated routes. |
| 49-54 | All drawbars, preset routing, switch truth tables and continuous contact | Retain two pedal controls separately and preserve the Great/pedal branch identity. |
| 55-60 | Cabinet families, driver/rotor ownership and profiles | Later Leslie work must not collapse electrical variants or horn/drum histories. |
| 61-66 | Tone identity, frequency conventions, phase and source validation | Pedal identity is distinct from source ID, storage index, terminal and MIDI pitch. |
| 67-72 | Pickup boundaries, normalized/measured modes and alias policy | The existing sine field is a valid named engineering basis, not calibrated pedal spectra. |
| 73-78 | Generator filters, revision applicability, loaded response and tests | Do not infer a pedal reactor or loaded transfer from nominal capacitor groups. |
| 79-84 | Leakage topology, shared-source coupling and identifiability | Repeated source routes are coherent branches; no normalization or arbitrary noise may hide wiring errors. |

## Project intent established by these pages

The atlas proposes a framework-independent engine for a vintage B-3 with an
identified AO-28 revision and a vintage Leslie 122, ultimately exposed as a VST3
instrument and standalone application with an accessible dimensional interface.
It distinguishes functional correspondence, measured specimen correspondence,
visual correspondence and release readiness (pp. 2-5, 12-18). It explicitly
reports that its research acquired no physical instrument measurements (p. 2).
The research alone therefore cannot establish a measured one-to-one recreation.

The dependency sequence is reference/data contracts, deterministic engine,
shared generator, console behavior, scanner, organ electronics, Leslie
electronics, rotary acoustics, calibration and product qualification (p. 5).
The current prepared pedal-kernel task is a dependency-ready part of console
work. A passing routing kernel cannot close the remaining console mechanisms,
scanner, physical calibration or product milestones.

## Pedal requirements that must survive the next implementation

### Preserve one persistent source field

Pages 4, 26, 46, 63-64, 66, 70 and 82 repeatedly require each generator source
to be evaluated once and shared by every downstream route selecting it. Notes
and controls change connectivity, never oscillator ownership or phase. Silence,
unconnected output, preset cancellation and block boundaries must leave source
time advancing normally. Rate changes must preserve accumulated phase.

The inspected code already provides this boundary:

- `TonewheelBank::process_frame` emits the current phase's 91 source samples and
  advances each source exactly once. It has no key API.
- `Engine::process` calls that function once per rendered frame into
  `source_samples`, even when output is disconnected.
- Manual and percussion sums consume that same array. Expression and profile
  output gain are applied after those sums.

Integrate future pedal processing by consuming this array. A second source bank,
another Engine render or note-created oscillators would violate the contract.
The atlas's illustrative pseudocode sometimes advances phase before evaluation
(p. 64); the repository explicitly emits then advances. Keep the repository's
existing time origin and tests consistent rather than changing it to match an
illustrative ordering.

### Keep the identifier domains separate

Pages 43 and 61 distinguish electrical tone number, source storage, physical
shaft/compartment/pickup/terminal and MIDI reference. The explicit nominal source
anchor is `MIDI = tone_id + 23`; it is not a pedal-controller mapping. Pages
61-66 require independent source anchor tests rather than trusting copied
formulas or octave labels.

Current `Types.h` uses one-based `ToneId` 1-91, zero-based source storage,
`Manual::Upper`/`Lower` values 0/1 and manual MIDI notes 36-96. A pedal identifier
must have its own domain and checked conversion. Do not extend the manual enum
or derive a pedal MIDI octave from source frequency. Existing event values 0-9
must remain stable when new event types are appended.

### Preserve two pedal controls and the lower path

The page 49 table and accompanying acceptance condition explicitly distinguish
**36 retained manual settings plus two retained pedal settings**. All four
manual banks remain independently editable. The listed nine harmonic ratios
describe manual drawbar functions, not an electrical pedal-mixture matrix.
Therefore two pedal controls should eventually be independently retained, but
their four-bus transfer must be separately named and justified. The atlas does
not authorize silently copying the manual gain law into a physical pedal model.

Page 51's truth table assigns pedals to the **Great-enabled scanner branch**.
Upper-B percussion is separately eligible only through Swell, B selection and
percussion On. Preserve a distinct pedal/lower contribution before common
expression/output scaling, so a future scanner can implement that topology.
Pedal contacts must not feed the upper ninth-contact detector or acquire its
percussion sustain mask. Great/manual Cancel must remain a manual-routing action
and must not destroy independent pedal state.

The inspected `ControlSnapshot` contains manual banks, selectors, route enables,
expression and percussion settings, but no pedal controls. It deliberately
excludes held keys, phases and time. When adding pedal controls, migrate older
saved formats explicitly to muted pedal settings, preserve older semantic IDs,
and continue excluding held pedal/contact histories from ordinary snapshots.

### Keep contact identity separate from voicing

Pages 37-42 establish separate mechanical motion, independent electrical
contacts, source routing and visual state. The nine-contact manual model is not
evidence for pedal contact timing. Page 52 also warns that printed 0-8 drawbar
markings do not define an isolated-detent electrical model; continuous-contact
construction does not determine an amplitude interpolation curve.

For the selected routing checkpoint, retain all pedal contact positions,
including inaudible disconnections and repeated-source branches. Use explicit
dimensionless reference weights with documented bounds. A later travel,
reactor/loading, drawbar-mixture or continuous-motion model needs its own
identity, parameters, units, assumptions and replacement path.

### Do not convert nominal sources into physical calibration claims

The page 62 rational frequency table is explicitly derived from a pinned
setBfree implementation, not a newly verified B-3 production gear inventory.
The existing 12-TET sine profile should retain its current nominal identity;
adding pedals is no reason to silently replace it. Gear relationships, pickup
phase offsets and absolute voltage remain separate evidence tasks (pp. 61-72).

Generator filter families on p. 73 and the bulletin revision on p. 74 identify
documentary configurations, not enough information for a loaded pedal voicing
model. Pages 67-78 require a declared electrical observation boundary and warn
against applying a measured filter twice. Pages 79-84 likewise disallow a
generic leakage layer that duplicates contamination already in a measured
terminal waveform. The first pedal kernel can legitimately route normalized
synthetic source frames while these physical quantities remain unknown.

## Required independent evidence for the selected scope

These are recommendations, **not checks executed by this assignment**:

1. Compare every admitted pedal/contact route against both independently retained
   factory CSV readings, including disconnections and repeated source numbers.
2. Test every contact separately with source-basis frames and rational weights;
   retain repeated branches until after their separate weighted contributions.
3. Compare a straightforward independently indexed four-bus sum with the native
   kernel using fixed, declared rounding bounds. No polyphony normalization.
4. Feed one actual TonewheelBank source array to both a manual reference and pedal
   kernel. Verify additive coherence, same source phases after silence/control
   edits and phase-preserving rate changes.
5. Verify whole-batch rejection preserves contacts and destination output;
   cover invalid IDs, null routes, non-finite/out-of-bound weights/samples,
   unprepared use, bounded maximum occupancy and equal-time edit ordering.
6. At Engine integration, retain no-pedal legacy audio and separately test pedal
   survival through lower Cancel, upper percussion independence, same-frame
   controls, zero-frame flushes, disconnected rendering and state migrations.
7. Measure allocation/deallocation calls in the new enabled runtime path and
   record the tested workload. A bounded loop or offline timing is not proof of
   real audio-device deadlines.

## Visual observations and actual commands

Rendered selected pages using the equivalent of:

```sh
pdftoppm -f 51 -l 51 -scale-to 1400 -singlefile -png \
  Hammond_B3_Leslie_Research_Atlas_500pp.pdf /temporary-review/page-51
```

All six PNGs were opened with the image inspection tool. Page 4 visibly labels
its flow as a conceptual responsibility map, not a circuit. Page 49 confirms
the 36+2 retained-control distinction. Page 51 confirms the Great/pedal routing
truth table. Page 62 labels its frequency illustration and ratios as derived
reference material. Page 73 confirms the four filter families and explicit unit
conversions. Page 80 labels its 12-source coupling matrix as hypothetical;
it must not be copied as physical adjacency or gain data. Rendered review PNGs
are temporary inspection products and are not added to the repository.

Actual read-only command families were `cat`/bounded `sed` for repository
instructions and contracts, six Python slices of the extracted range, `rg -n -C`
for the Engine source-frame boundary, `pdftoppm`, `sha256sum`, `git status` and
`git rev-parse`. No native build, DSP test, external-source retrieval, hardware
capture, commit or push was performed by this worker. Only this evidence note
was written. Root owns shared status, integration, actual test execution and
publication.

## Missing evidence and handoff

This assigned range provides no physical pedal-controller octave, calibrated
pedal drawbar transfer, reactor/load parameters, low-wheel spectra, contact
trajectories or specimen measurements. It also does not recover the atlas's
absent companion files. Continue the typed 25-by-8 routing/reference kernel
specified in [M3_NEXT_GATE.md](../../M3_NEXT_GATE.md), then define and qualify
the named nominal integration separately. Preserve the above boundaries in
metadata, tests and the next handoff.
