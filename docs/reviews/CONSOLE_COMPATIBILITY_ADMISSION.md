# Console compatibility — independent source admission

**A43, `/root/w08_a43`, wave 8, 17 November 2026 UTC: ADMIT the inspected
local overlay's compatibility with starting commit
`9d60dbf462a90fe422fd4e69757fe202264acb7c`.** No blocking compatibility change
was found. This is a source/evidence review; root retains integration,
acceptance and publication. Newly advanced remote source and any subsequent
merge are outside this admission.

## Exact comparison and changes

The [compact audit](../development/2026-11-16-console-completion/reports/A43-compatibility.json)
records complete hashes, Git blob identities, commands, source reversals and
retained evidence. HEAD was the starting commit, tree
`6bfdb87625ea7626e1b7c30ce9e78bad622a5978`; the index had no changes.
I read the complete standing instructions, M0–M9 plan, current console records,
relevant admissions and complete new LibraryModel source. I compared actual
Git blobs with working bytes and inspected the full changed-path inventory,
including untracked source; a clean protected `git diff` alone was not the check.

All **81 tracked files under `include/`, `src/` and `plugins/` are byte-identical**
to the start, with no new untracked file in those domains. All **160** hashes in
[baseline-source.json](../development/2026-11-16-console-completion/reports/baseline-source.json)
match their actual starting blobs; **156 remain unchanged**. The four changed
entries are `InstrumentView.cpp`, the UiModel pair and the header-material test.
Registry JSON, nominal profile, fixed-registration catalog, root CMake,
Session, StateFiles, RegistrationLibrary, input/ownership adapters and
`main.cpp` also remain unchanged.

The production additions are the copied LibraryModel pair, five added lines in
each UiModel file, and the private P1 paint function/selector. Independent
in-memory removal of the exact helper blocks restores both whole original
UiModel files. Removing only the P1 function, enum member, scale guard,
selector branch and performance-panel call replacement restores the complete
original painter. Reversing the single header-test line restores its original
source; its four dimensions merely use exactly representable float literals.
No source was changed to perform these reversals.

| Current production input | SHA-256 |
| --- | --- |
| `LibraryModel.h` | `4ea94b611e4fdc27ea48c6bad47ddf9ed99761f2e12ae264b7482ac8d3b093e2` |
| `LibraryModel.cpp` | `ae5348c731b0559a6816b75cc190622918ca89d1fe938dd56445d51591904b98` |
| `UiModel.h` | `34337e5db254bfbc4e23ee4fadf76ecc8fe792f003bd13ab5b54d0a302b5bb15` |
| `UiModel.cpp` | `b4889e0b5d1b6eb0b88b140b8af92815df4bf021158a902994db2c15ed798986` |
| `InstrumentView.cpp` | `8ca5c05138ed4cd12fe8ef416ea35a3d78a8a3c4915645f53d8c0c0df2fcf927` |

Other changed/new execution inputs are tests, explicit replay scaling and finite
JSON admission, comparators, the Flat capture witness, standalone CMake and CI
wiring. They add qualification paths; they introduce no hidden Engine,
parameter, state, UUID or live effect change.

## Preserved musical and state boundary

| Boundary | Independently inspected conclusion |
| --- | --- |
| **47 parameters** | All 47 compiled descriptors match the JSON projection for ID, path, kind, unit, minimum/maximum, default, steps and event/manual/index. Both complete sources match baseline. Expression, discrete thresholds, preset normalization and signed-zero laws are unchanged. |
| **Saved controls** | Writer remains `B3CONTROLS4`, with readers 1–3 retained. Catalog identity and prior migration defaults are unchanged. No held notes, contacts, phases, processing clock or percussion readiness enters saved controls. |
| **91 shared sources / dry Engine** | `TonewheelBank` and Engine processing remain unchanged: one shared source frame advances through silence and absent output; controls restore only validated values and dirty coefficients. No scanner/AO-28/Leslie/rotary connection was added. |
| **UUIDs and ownership** | Both plugin class IDs and all plugin sources are identical. NoteOwnership, PedalNoteOwnership, Session, contacts and percussion history code are identical. This is no new binary ABI or host-execution claim. |
| **Inventory and presentation** | Four banks, 61 Upper + 61 Lower + 25 pedal playing keys, 24 presets and 68 control records including presets remain. Exact UiModel reversal preserves every preexisting layout, hit, focus and input method. P1 changes only its reviewed plate interior. |

The helper follows one complete-command route:
`LibraryRecallIntent.expected_controls` → `UiModel::recall_controls` → existing
forced `publish_controls` → one `SessionCommand{ControlSnapshot}` →
`Session::post/apply` → `Engine::restore_controls` → `ControlState::restore`.
Invalid input returns before mutation. Equal valid values still emit exactly
one snapshot. Only desired/pending/dirty bookkeeping changes; the cleared
sequence is the pending **control** sequence. The saved-file baseline, held
owners, gestures, source phases and percussion history are not reset. Existing
submission-failure recovery remains unchanged.

The complete new LibraryModel stores owned copies and returns intents. It has
no live Session/Engine handle, post/read operation, filesystem/SDL/clock call or
audio callback. Its PIMPL and copied views may allocate on the required main
thread. The unchanged scope merge keeps explicit latest desired expression for
Registration and saved expression for Performance. Named references and legacy
file cleanliness remain independent. Neither `main.cpp` nor the painter/P1
fixture invokes the helper: native browser/main integration is still absent.

## Existing execution evidence and its limits

I read the original detailed logs, inspected the real harness routes and
rehash-checked their current source identities. **A43 ran no build, executable,
test, benchmark, capture or nested agent.**

| Retained evidence | Result and concrete boundary |
| --- | --- |
| [A19 real Session](../development/2026-11-16-console-completion/reports/library-session-ctest-detail.log) | 12 groups / 42,634 assertions; 696 real snapshots, 150 renders, 6,252 bit-exact paired stereo samples, 10,101 source-phase checks and 60 percussion-history checks. Two Sessions and an independently driven physical-event Engine cover 44.1/48/96 kHz, equal/changed/muted recall and original overlapping releases. Hidden Session phases are not read directly. |
| [A28 combined roundtrip](../development/2026-11-16-console-completion/reports/library-integrated-ctest-detail.log) | Four groups / 1,489 checks; 138 real snapshots, 20 renders, 24 actual posts reported once to each model and seven real storage/authorization calls. Covers the whole helper route, both scopes, retained legacy baseline/owners, post-Start proof, superseded Save and a late no-replace collision. This is a manually rendered SDK-free harness. |
| [Coherent integrated run](../development/2026-11-16-console-completion/reports/integrated-first-ctest-result.json) | **246/247**, with every other registered gate passing, including all five library suites and the current candidate-only P1 numerical gate. The sole retained failure is the A33 note's report link during concurrent authoring. Its report now exists; the original full run remains failed. Root still owes a separate affected document gate. |

The five-library receipt's 13 source hashes all match current files. A27 uses
synthetic UiModel observations; A20 uses real storage with synthetic control
proof. Those differ from A19/A28's real Session evidence.

The [P1 paired-v2 result](../development/2026-11-16-console-completion/reports/p1-paired-v2/report.json)
retains 34 pairs, 70 processes, 74,008,097 compared pixels, zero forbidden changes
and all 62 candidate screens passing. Its original focus-oracle failure remains
separate. Paired and [timing evidence](../development/2026-11-16-console-completion/reports/p1-timing-summary.json)
bind the original **pre-helper** inputs; exact reversal does not convert them
into post-helper executions. The 2,400-sample timing batch had no investigation
signal and passed its cross-witness gate, but establishes no equivalence or
audio/display deadline. The [candidate-only transition](P1_RECALL_SOURCE_TRANSITION_ADMISSION.md)
explicitly refuses the helper pair in historical paired mode.

## Rebuilt application and remaining acceptance

The original application `010d43dc…`, P1 pre-helper application `7b812bbb…` and
integrated application **`7f8996cd…`** are different binaries. Unchanged core
source does not mean an unchanged executable. Root's
[coherent build qualification](../development/2026-11-16-console-completion/reports/integrated-application-qualification.json)
has **150/150 matching current source hashes**. Its Linux Release configuration
uses GCC 14.2 and SDL 2.32.10 with MIDI/VST3 off. The
[final capture receipt](../development/2026-11-16-console-completion/reports/integrated-capture-result.json)
records **15/15** views from the new application, explicit scale 3 and unchanged
recorded inputs; I independently rehashed all 69 gallery-manifest entries.
Binary digests/build ancestry come from root's retained receipts; I did not
rehash binaries outside this checkout or perform a new visual admission.

Root must review any reconciled source and qualify its affected boundaries,
finish document integrity and verify exact remote publication/hosted results.
The [native integration plan](../design/LIBRARY_NATIVE_INTEGRATION_NEXT.md)
still requires model-owned Save availability, post-Start proof, all submission
and lifecycle hooks, browser gesture/modal routing and original releases.
Real display/DPI/audio/MIDI devices, native accessibility, callback retirement/deadlines, actual host/platform/sanitizer gates,
physical AO-28/scanner/Leslie calibration, rights and signed release remain
separate. **Literal whole-interface 1:1 remains unmet and unwaived.**
