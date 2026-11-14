# Fixed-registration core lifecycle acceptance

Reviewer: **A19**, `/root/w04_a19_core_lifecycle_review`, wave 4,
2026-11-14 UTC. Contract: `exclusive-fixed-registration-v1` and
`exclusive-fixed-registration-core-v1`.

## Decision and scope

**Pass for the reviewed core lifecycle slice. No production defect was found.**
The new regression demonstrates that active fixed selections and fixed choices
remembered behind Cancel survive supported sample-rate changes and live
saved-control restoration. It checks the continuing source, contact, percussion
and pedal histories, the subsequent audio, and the distinction between current
controls and the last sample actually rendered.

This is independent acceptance after the accepted A13/A14 core prerequisites.
It adds `tests/test_fixed_registration_lifecycle.cpp`; it does not repeat A14's
exhaustive static selector/row suite or present that worker's runs as A19 runs.
A15's stable `ControlStateIO` is included to exercise actual state4 round trips.
The host and UI consumers were still changing in separately owned files, so the
executed build uses a frozen copy of only the necessary core/I/O sources and
their transitive headers. No older core library was linked to current headers.

The repository HEAD was `352a398e4f004467c2dab081168be3d8b5206ea9`.
That commit contains documentation and an unrelated native unused-constant
correction; **the tested fixed-registration implementation is the uncommitted
overlay**, identified by hashes in the [A19 execution record](../development/2026-11-14-preset-continuation/19-core-lifecycle-review.md).
The commit alone does not identify the tested production code.

## Source audit

The review read `AGENTS.md`, the project plan/current continuation context,
the frozen selection/core contracts, the saved-control grammar, A13/A14's actual
reports, A15's state-migration record, and the relevant implementation and tests.
The independent reference rows are the source-read literals in
`tests/PresetTestOracle.h`; the new audio oracle calls neither the production
fixed-row lookup nor its generated table.

| Audited boundary | Source finding | Executed qualification in this review |
| --- | --- | --- |
| Immutable row access | `FixedRegistration.cpp` checks both typed domains before indexing immutable generated storage. The public API returns copies and program-lifetime views; there is no lazy initialization or mutable catalog. | Literal-row bank references exercise all eighteen rows through lifecycle sequences. Exhaustive invalid lookup and generator admission remain A13's separate evidence. |
| Retained versus active controls | `ControlState.cpp` stores fixed memory independently of the retained bank and route bit. Complete validation precedes restoration, including invalid fields hidden behind Cancel. | Actual state4 round trips, selected-preset queries, retained-bank queries, both route masks and hidden-invalid restore rejection. |
| Event/cache integration | Fixed/bank/Cancel events change routing facts without calling source/contact/percussion preparation. Existing bank selection notices a non-None fixed mode. Both audio and diagnostics share the upper-B eligibility predicate. | The review inspected all new dispatch/preflight branches. Its new execution focuses on restored fixed states, rate transitions and later legacy bank return; A14 retains the exhaustive selector-event evidence. |
| Sample-rate boundary | `Engine::reconfigure_sample_rate` validates owned profile/module candidates before installation. It leaves controls, routing caches, held state, source phases, readiness and clock intact. | All nine ordered supported-rate pairs in both contact modes, including same-rate no-ops, active/cancelled memories, independent future phase/contact/readiness calculations and deeper profile rejection. |
| Live restoration | `restore_controls` validates a complete control candidate, then marks routing dirty. It does not load a DSP checkpoint or call prepare/panic. | Moving attack/release/partial holds, old saved controls loaded after history has advanced, and identical-control save/load compared with an untouched engine's exact future continuation. |
| Diagnostic meaning | Percussion eligibility is derived from current controls even before coefficient rebuilding. `last_pedal_frame` describes an actual previous sample and is unchanged by restore/rate calls. | Immediate eligibility/gain/sustain checks, complete historical pedal-record equality, explicit old rate/positions before rendering, and current frame/rate/positions after connected or disconnected rendering. |

No production change was needed. Source inspection supports the absence of new
allocation, locking or file access in the fixed-row/control/audio path, but this
review does **not** claim a measured callback-allocation result. State text I/O
remains an allocating stopped/control-thread operation.

## Regression design and observed results

GCC 14.2.0 compiled ten frozen core/I/O translation units and the new test with
C++20, `-O2`, the complete repository warning set and `-Werror`. The final test
completed with exit **0** in **0.830 seconds** and emitted no stderr. The first
strict build/run also passed; the final revision adds the untouched-continuation
check and an observed clean-cache boundary for rejection fixtures. There was no
failed compilation or runtime result in this assignment.

### Successful rate and restore sequences

The **72 scenarios** are the Cartesian product of nine ordered rate pairs
(44.1, 48 and 96 kHz), two contact modes (Ideal and LinearTravel), and four
upper/lower route masks. Initial fixed rows rotate with the ordered rate pair,
covering all nine rows on each manual; a later restore chooses different rows.
This is a lifecycle matrix, not an exhaustive row × rate-pair matrix.

Each subject and reference engine is independently prepared with the same seed
and profile. Both first run held folded chords and three pedals, allowing upper
B percussion readiness to decay. The travel fixtures then start new attacks,
release other keys and command explicit partial positions while a high upper
key keeps the physical detector closed. Every per-key travel duration and
threshold is explicitly supplied by the test's unmeasured engineering fixture.

The subject restores fixed controls. The reference uses literal page-122 digits
in bank A, with no fixed mode; it keeps percussion On, so upper bank A supplies
the same ineligible recovery without fixed-mode logic. Both continue through:

1. A state4 serialize/parse/restore and a rate change before the next render.
2. One connected frame, then 79 disconnected subject frames against a connected
   reference, with matching complete histories.
3. An identical-controls state4 round trip whose next 113 frames, legacy bank
   return, and following 97 frames equal an untouched subject copy bit for bit.
4. A different saved fixed/Cancel choice, remembered banks, expression, pedal
   positions and percussion settings restored during continuing travel.
5. A return rate change and 131 frames, followed by loading the earlier saved
   controls after the histories have advanced, then another 43 frames.
6. A restore to upper B and 193 frames of continued percussion decay using the
   recovered readiness, with no synthesized reset or recovery time.

All no-time boundaries compare every source phase, all 122 manual targets and
contact snapshots, held-key counts, all 25 held pedals, all 200 pedal contacts,
readiness, frame clock and the complete last pedal frame. A rate change permits
only the installed current rate to differ. A control restore permits only
musical controls and their derived current routing diagnostics to differ.

| Final measured check | Count | Meaning |
| --- | ---: | --- |
| Lifecycle scenarios | 72 | Nine ordered rate pairs × two contact modes × four route masks. |
| Preserved engine rate boundaries | 288 | 144 subject calls and 144 reference calls; includes 96 same-rate no-ops across both engines. |
| Live restore calls | 740 | Immediate history checks, including cold-load and rejection-fixture setup. |
| State4 round trips | 308 | Actual serializer/parser calls with exact musical-control and canonical-byte equality. |
| Cold loads | 72 | Fresh engines retain no held keys/pedals, readiness one and their own initial phase/clock; first output is silent. |
| Exact audio comparisons | 80,256 frames | 26,496 bank-reference frames, 15,120 identical-restore continuation frames and 38,640 rejection-continuation frames. |
| Independent phase calculations | 32,760 | Long-double elapsed-seconds advance of all 91 observed starting phases; circular absolute budget `8e-12` turns. |
| Independent contact-position calculations | 43,920 | Monotone travel from observed starting position, explicit seconds/durations and target clamp; absolute budget `3e-13`. |
| Independent contact-bit checks | 395,280 | Explicit threshold/hysteresis resolution against each key's literal test profile. |
| Independent readiness calculations | 360 | Closed-form exponential recovery or decay over actual segment seconds; absolute budget `2e-12`. |
| Full observed snapshots | 5,412 | Immediate preservation and later continuation, with current diagnostics kept separate from the historical pedal record. |

The phase/contact/readiness equations supplement the bank comparison: a defect
shared by both engines' rate migration cannot pass merely because the two
engines agree. The no-op save/load comparison also covers hidden future contact
segment bookkeeping that is not exposed by `ContactKeySnapshot` alone.

### Rejected operations and future continuation

**100 rejected rate changes** and **84 rejected whole-control restores** preserve
the complete immediately visible state and then match an untouched engine's
next 113 samples, explicit return to retained banks, and following 97 samples.
The future comparison includes complete snapshots and exact float bit patterns.

The fixtures cover all three installed rates, enabled upper fixed and
Cancel-held fixed memory, and both just-restored dirty routing and rendered
routing with an observed no-contact-change final frame. The latter ensures that
the clean-cache claim follows the actual source's invalidation condition.
InvalidSpec requests include zero, negative, unsupported, NaN, infinity and a
representable value adjacent to a supported rate. InvalidProfile cases exercise
a source crossing Nyquist and a source dropping below the supported phase
increment floor at an otherwise supported target rate.

Rejected restores include invalid fixed values 10 and 255 behind disabled
routes, an invalid hidden retained bank, a position of 9 in an inactive bank,
invalid percussion decay while fixed routing excludes percussion, a pedal
position of 9 and NaN expression. These checks expose partial mutation of any
candidate field and loss of a previously dirty coefficient rebuild.

## Integration handoff and limits

The existing CMake `tests/test_*.cpp` glob discovers the new test; no CMake file
was changed. Root should include it in the next coherent full-tree build after
the separately owned consumers are ready. The [execution record](../development/2026-11-14-preset-continuation/19-core-lifecycle-review.md)
contains exact compile commands and all frozen input hashes.

This assignment ran **one newly built direct C++ regression executable**, not a
CTest suite or full product build. It did not rerun A13/A14/A15's complete suites,
test host/parameter/UI/atomic-publication adapters, measure callback allocation,
run sanitizers, qualify a device/DAW/platform package, or observe hosted CI.
The successful sequences keep one upper physical detector contact closed;
detector-edge qualification remains the distinct existing core/contact evidence.

The fixed digits remain documentary tap indices from the atlas, with the
existing nominal gain law. Physical simultaneous latching, contact/loading
networks, specimen gain measurement, unacquired underlying factory Table IV,
held-key hardware B transitions and scanner/AO-28/Leslie fidelity remain outside
this acceptance. No baseline build, source catalog/PDF, another worker's file,
shared status document, Git ref or published revision was modified.
