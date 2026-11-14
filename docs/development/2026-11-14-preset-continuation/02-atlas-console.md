# A02: complete atlas reading, pages 85-168

Assignment identity: `/root/w01_a02_atlas_console`. Session: the separately
requested 2026-11-14 preset continuation. Scope: a full source reading and
contract recommendations; no production code, source data, Git history or other
worker's files were changed by this assignment.

## Source and executed reading

The unchanged `Hammond_B3_Leslie_Research_Atlas_500pp.pdf` has 500 pages,
21,248,265 bytes and SHA-256
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
The inspected checkout was `b79086f6bb0c42b97130c721c5c73c7c97a13887`.

Read **all 84 pages, 85 through 168 inclusive**, using Poppler `pdftotext`
25.03.0, in these complete, untruncated extraction ranges: 85-94, 95-104,
105-114, 115-126, 127-136, 137-146, 147-156 and 157-168. Reading included
equations, tables, source notes, proposed acceptance gates and limitations.
Rendered original pages 122 and 123 with `pdftoppm -scale-to 1600 -png` and
visually inspected the complete preset table, reverse-color console photograph
and preset wiring photograph. This is a fresh visual cross-check of the atlas,
not an independent acquisition of the factory manual cited by the atlas.

Reproducible extraction command, from the repository root:

```sh
pdftotext -f 85 -l 168 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
```

Its complete output has 84 form-feed page terminators, 212,767 bytes and SHA-256
`f25702a260670151dac0bc27916ca9b68592212b9970cae8257a671351f15c53`.
These counts identify the reviewed text; they are not substitutes for reading.

Also reviewed `AGENTS.md`, `docs/NEXT_STEPS.md`,
`docs/CHAPEL_PRESETS_CATALOG.md`, `docs/CHAPEL_CONTROLS.md`,
`docs/CHAPEL_PRESETS_ACCEPTANCE.md`, both prior chapel source review notes,
the complete authoring catalog, and current `ControlState.h`, `Types.h`,
`ConsoleModel.h` and `Percussion.cpp`. The catalog compiler and existing audition
exporter are documented preparation tools; the latter copies a row into an
ordinary retained bank and is not a runtime fixed-registration selector.

## Coverage and implications

| Pages | Subject actually read | Consequence for the continuation |
| --- | --- | --- |
| 85-90 | Mechanical irregularity, shared drive/shaft residuals, startup, measurement and numerical gates | Changing registration must never restart a generator, reseed a residual or change elapsed-time advancement. Factory forcing rates are not calibrated modulation depths. |
| 91-96 | Observation/profile/runtime separation, strict IDs/units, source boundaries, revision provenance and preparation | Compile validated immutable registration data outside processing; keep documentary values distinct from measured source amplitudes and circuit parameters. A bad replacement must preserve previous valid state. |
| 97-102 | Literal 61-by-9 manual wiring, repeated foldback, source collisions, specimen checks | Fixed registration selects taps on the existing nine buses. It must not remap notes or create sources. Equal source IDs remain coherent while contacts remain independently owned. |
| 103-108 | One shared generator field, scalar reference, lifecycle, bounded processing, bandwidth and acceptance | Phase advances through silence and route changes. Offset events apply on the declared sample timeline; zero-sample calls must not advance phase. Callback work stays bounded and allocation-free. |
| 109-114 | Drawbar direction, tapped transformer topology, nominal 3 dB reference, loading and acceptance | Tap 0 is mute, tap 8 full. Tap digits use the existing declared gain law, not digit/8 amplitude. Inactive banks retain their values and cannot leak into the selected fixed route. |
| 115-120 | Nine contact histories, gesture/click generation, fractional timing, bandwidth and acquisition | Do not synthesize note retriggers when a preset is selected. A route switch does not replace contact state, add a noise click or prove high-rate contact fidelity. |
| 121-126 | Preset cradle, full chapel table, nine-bus topology, B interlock, acquisition and persistence | These are the primary sources for the bounded exclusive-selector contract below. |
| 127-132 | Shared percussion detector/readiness, 1-foot contact, ownership, equal-time events and evidence gates | Percussion remains one upper-manual process with retained history. Routing, note ownership and control-circuit readiness are separate observables. |
| 133-138 | AO-28 percussion revision, borrowed harmonic, compensation, RC surrogate and qualification | Only routed upper B applies its percussion mask/compensation. Fixed routes bypass that eligibility without resetting shared readiness. Circuit response remains nominal. |
| 139-144 | Pedal contacts/mixtures, shared sources, exceptional wiring, network and acquisition | Manual Cancel/preset changes preserve pedal ownership, its two settings and shared source state. Manual selection is not a pedal program change. |
| 145-150 | Capacitive expression network, controller mapping, coupling/feedback and measurement | A reverse-key selection must not recall expression or change the expression model. The current scalar expression remains a separate declared surrogate. |
| 151-156 | Canonical commands, ownership, sample timeline, transport/power separation, patch/checkpoint distinction and panic | Persist controls separately from transient histories; preserve stable same-offset ordering and whole-call rejection. UI views report applied state rather than mutating DSP directly. |
| 157-162 | Loaded scanner line, 18 L/18 C/19 outputs, common return, independent numerical solvers and unknowns | The selector continuation does not integrate or qualify the scanner. Keep its separate numerical/physical gates unchanged. |
| 163-168 | 16 scanner stators, nine terminal voltages, overlap approximation, phase and acquisition | Preset selection also must not create a scanner reset later. Physical geometry/rate and proposed weights remain distinct evidence. |

## Fixed-registration semantics to implement

The atlas explicitly permits an exclusive normal-playing abstraction while
reserving simultaneous physical latches for a separate model (p121). Therefore
the proposed slice can be implemented now without claiming a physical cradle or
loaded switching circuit.

| User action | Required normal-mode behavior | Atlas basis |
| --- | --- | --- |
| C# through A | Select exactly one of nine immutable fixed routes on that manual. Keep both adjustable banks intact. | pp121-123, 126 |
| A# | Reconnect the already retained left adjustable bank. The repository calls this bank A; make that UI alias explicit. | pp121, 126, 153 |
| B | Reconnect the already retained right adjustable bank. Upper B can be eligible for percussion; lower B cannot enable upper percussion. | pp121, 124, 127, 134 |
| C / Cancel | Disconnect that manual's registration route. Keep notes, contacts, source phase, the other manual and pedals intact. C has no electrical contacts and returns immediately; it must not look permanently latched. | pp121, 125, 151, 153 |
| Release a selected reverse key | Selection persists. Do not treat it as ordinary Note Off. | p121 |
| Edit an inactive A/B bank | Retain the edited positions without affecting the sounding fixed registration or selecting/reconnecting a bank. | pp114, 126, 153 |
| Select while notes are held | Change connectivity at the declared sample, preserving the existing source/contact/percussion histories. No artificial note retrigger or implicit program-wide recall. | pp105, 124, 126, 153, 156 |

Do not conflate the fixed key **A** with adjustable **A#**, which this codebase
currently names drawbar bank **A**. An enum or discriminated type should distinguish
these meanings independently of display text. A stable API can retain the old
bank-selection operations while adding a separate typed fixed selector; using a
single integer with undocumented overloaded meaning would invite a migration bug.

The same atlas reports simultaneous depression can latch multiple physical keys.
This proposed normal-mode selector deliberately has no such claim. A later
physical mode must retain contact branches and solve loading; summing two
independent preset renders is not adequate (pp121, 123).

## Exact admitted chapel matrix

The complete rendered page-122 table agrees with the existing authoring data at
all 18 rows and 162 tap positions. An independent literal comparison was executed
after visual inspection; every manual/key/string matched, every name remained
`null`, and every source page remained 122. The authoring file SHA-256 is
`c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf`.

| Fixed key | Upper taps | Lower taps |
| --- | --- | --- |
| C# | `005320000` | `004545440` |
| D | `004432000` | `004423220` |
| D# | `008740000` | `007373430` |
| E | `004544222` | `004544220` |
| F | `005403000` | `006644322` |
| F# | `004675300` | `005642200` |
| G | `005644320` | `006845433` |
| G# | `006876540` | `008030000` |
| A | `327645222` | `427866244` |

Ordered footage is `16`, `5 1/3`, `8`, `4`, `2 2/3`, `2`, `1 3/5`,
`1 1/3`, `1` feet. The printed lead-color order is brown, red, orange,
yellow, green, blue, violet, gray, white. These are documented tap connections,
not linear amplitudes or measurements. Sixteen strings begin with zero; retaining
them as nine-character strings avoids loss of meaning.

The atlas publishes no descriptive registration names. Use truthful labels such
as `Upper C#` and the tap string, not invented historical names. Its cited factory
Table IV, printed p4-1, remains independently unverified in this assignment.
The approved chapel arrangement is not a universal surviving B-3 wiring claim.
Keep `atlas-chapel-nominal-v1` and the existing documentary status unchanged.

## Percussion and ordering contract

Upper B eligibility must be resolved from the actual selected route, not merely
the last remembered bank or visible percussion tablet (pp124, 127, 134). A fixed
route can remember bank B for future editing without being eligible for upper-B
percussion. This is a specific hazard in extending the current
`selected_banks`/`route_enabled` pair.

The percussion detector uses the **eighth harmonic, the 1-foot path**, which is
drawbar index 8 in zero-based storage; it is not the eighth physical drawbar
(p128). A muted 1-foot drawbar does not erase its physical keying contact. Upper
B percussion masks that sustained 1-foot contribution and applies the existing
normal-mode upper compensation only at the eligible routing boundary (p134).

Keep readiness continuously owned by the existing percussion subsystem. Exiting
B disconnects the declared detector path and permits the chosen nominal model's
time evolution; re-entry must consume its remaining state. Do not set readiness
to 0 or 1 on selection. A zero-duration B-to-fixed-to-B sequence advances no
recovery time. Adding a held note enters the existing shared envelope without an
independent attack (pp124, 128-132, 135-136).

The atlas's nominal continuous-readiness surrogate and actual circuit transitions
are separate evidence levels. Existing `Percussion.cpp` advances readiness only
through `advance_frame`; preserve that numerical family unless the scope
explicitly changes it. Tests can qualify deterministic routing/history, not the
unacquired electrical charging response during real B transitions.

At equal event offsets, preserve the repository's declared stable input order.
Host adapters need an explicit routing-versus-note tie rule because automation
and notes arrive in separate containers; the atlas proposes routing first and
then stable note order (p153). Document the chosen adapter rule and test it;
do not silently reorder direct core events whose current API preserves order.

## Persistence and acceptance recommendations

Specify append-only parameter IDs and an explicit state-version migration before
changing the shared snapshot, as required by the repository's current next-step
contract. Do not repurpose old bank-selector IDs or alter old A/B/Cancel meaning.
All four banks, two manual route choices, independent pedal controls, expression
and percussion settings must round-trip. Legacy files must migrate to their
original A/B/Cancel behavior with fixed registration unselected.

Bind fixed selection to the immutable named matrix and its identity; the atlas
requires panel/profile identity and content hash so an updated library cannot
silently change a restored project (pp126, 155). An implementation supporting
only this frozen matrix can encode a versioned fixed profile identity and reject
unknown identities without introducing mutable panel editing or arbitrary
runtime file loading.

Ordinary saved settings contain no note owners, contacts, source phase or
percussion charge. Cold restore starts without held keys; an existing supported
live-load path retains its explicitly documented ownership/history policy. A
registration selection is narrower than full program recall: it cannot reset
expression, scanner, Leslie, input mappings or model profiles (pp126, 155).

Required meaningful acceptance should include:

1. All 18 fixed rows equal independently initialized equivalent banks under the
   same continuing source state with percussion disabled; include foldback
   collisions and held chords.
2. Both inactive banks survive fixed selection and edits, returning correctly
   on A#/B; fixed key A and adjustable A# never alias.
3. Cancel/reselect with held manual/pedal owners preserves every unrelated
   division and phase trajectory. Cancel's view returns to rest.
4. B-to-fixed-to-B at different held/released durations retains readiness;
   same-offset transitions create no elapsed recharge. Lower selections cannot
   enable or reset upper percussion.
5. Direct and host event ordering, zero-sample control flushes, different block
   partitions, supported rates and malformed-call rollback preserve the declared
   contract; finite state and zero forbidden callback allocation are measured.
6. Every retained state version migrates, all new persistent fields round-trip,
   invalid enum/profile/state inputs reject transactionally, and saved controls
   never resurrect held keys.
7. Actual native UI captures and interaction replay demonstrate selected-route
   feedback, independent bank editing, correct labels and momentary Cancel.
   Reference comparison must distinguish functioning screenshots from source art.

Still open after a successful software implementation: independent factory
Table IV acquisition, specimen wiring, contact/latch timing, simultaneous
latches, impedance/loading, measured tap gains and B-transition captures.
The scanner's failed same-hertz gate and M5/M6 electrical dependencies remain
separate and unchanged. This assignment makes no runtime test, hardware
measurement, full-project completion or literal UI-equality claim.
