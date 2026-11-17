# Heading, title and header compatibility review

**A38, 17 November 2026: source compatibility preserved within this review's
scope.** No unadmitted musical, saved-state, parameter or plugin-identity change
was found. The intentional UI-replay diagnostic extension is described below.
This is not H1 final acceptance, executed ABI qualification or product release.

Reviewed original base `113c29b7b14c8fde0859bc405ef8e4141a131ea6`, published T2
HEAD `6047723b595259de355c74342e48a8ae2ee1e228`, and current T3r2/H1 painter
`0bf731a692b7cb7c88c200afea86f4ca14239f20a7000f06be484f2a11ebc20d`.
The current application is
`bfe8e36d16f4c5fd15009f2fc4707c06c93388f40870dc9f84696d3367447e7b`.
The [bounded independent receipt](../development/2026-11-16-heading-title-continuation/reports/a38-compatibility.json)
contains exact source/report identities, comparison methods and remaining gates.
A38 performed read-only source, Git-object, report and binary checks; no build,
native execution, remote operation, production edit or publication occurred.

## Protected inventory reproduced

All 213 path/hash/length entries in the original
[A09 inventory](../development/2026-11-16-heading-title-continuation/reports/a09-compatibility-baseline.json)
were independently compared with original Git blobs, then current files.

| Protected group | Files | Original base to current |
| --- | ---: | --- |
| Core headers / sources | 31 / 30 | All identical |
| Plugin files | 20 | All identical |
| Authoring and data | 98 | All identical |
| Assets | 16 | All identical |
| Standalone state/drawing/application | 15 | Only admitted `main.cpp` differs |
| Atlas and reference inputs | 3 | All identical |

The genuine post-T2, T3r2, pre-H1 and H1 candidate receipts have exactly the same
213-path set; **all 213 current hashes match each receipt**. `main.cpp` became
`89b24fdeae438b77309904d12c32e3e2ae5e964e99968a8656c5b0a710e237c4`
in T2 and remains identical through T3/H1. Its original-base exception does not
authorize another main-thread, callback or core change. A38 also rehashed all
4 original, 5 post-T2, 6 pre-H1 and 7 current application/fixture/benchmark
binaries named by their receipts; none mismatched. These checks confirm retained
identities and do not independently reconstruct the builds.

## Preserved meanings, beyond file hashes

| Boundary | Inspected source argument |
| --- | --- |
| **91 shared free-running sources** | `Types.h` fixes 91. `Engine::process` obtains one shared source frame before checking output presence; `TonewheelBank::process_frame` emits and advances every source once. Notes change contact targets and ownership, never oscillator phase. Positive velocity chooses target one, not gain. Coherent coefficient sums retain their existing arithmetic without polyphony normalization. |
| **47 parameters** | Independently parsed all 47 native descriptors and matched JSON ID, path, kind, unit, maximum, default, steps, event, manual and index. All agree. The complete registry and threshold/conversion sources are unchanged. Canonical old-45 digest remains `13ba488bec90154c960c3fd700dc4a774aff5664caf5d68472821493f22d1cad`; the report also records the complete 47-record digest. |
| **Mapping and state** | Profile, pedal map, registration catalog and reference routing files remain exact. `ControlStateIO` still writes `B3CONTROLS4`, accepts readers 1–4, validates the fixed catalog, and commits a fresh candidate only after complete validation. Legacy readers 1–3 retain their migration defaults. Four banks, selected banks, retained fixed modes and route bits remain distinct; held notes, source/contact/percussion histories, clocks and UI presentation are excluded from saved controls. |
| **Plugin identity / public interface** | All plugin files and core headers remain exact. Processor ID is `19F9ADC0-533F42B4-B96BD51D-6547E838`; controller ID is `0DEE76AB-26BC475A-BF64F138-C89FB0E0`. No public control/state/automation or class-ID source change is introduced. This is not a new DAW/host or binary-ABI run. |
| **Nominal dry Engine** | Existing shared-source/manual/percussion/pedal mixing and expression output remain exact. H1 introduces no scanner, complete AO-28 or Leslie audio route. The unchanged inspection model still labels these complete paths unconnected. |
| **Controls and focus** | Unchanged `UiModel` owns shared hit/paint geometry: 68 control slots including 24 presets, separate 61+61+25 playing keys, and four retained banks. Play has 68 visible controls plus three roving key stops = 71; Rotary/Service retain ten common stops. The unchanged MIDI modal count is eleven. Stored slots are not all visible in other workspaces. |

The native parameter groups remain 36 manual drawbars (default zero, positions
0–8), expression (default one, normalized linear-gain surrogate), two remembered
bank selectors (default B), four percussion switches (Off/Second/Normal/Slow),
two pedal mixtures (default zero), and two exclusive preset selectors (default
B/index 11). No typography or material selector becomes a sound parameter.

## Actual changed production and supporting files

The only changed compiled application source files since the original base are
`apps/standalone/InstrumentView.cpp` and the separately admitted
`apps/standalone/main.cpp`.

The painter adds the T2 private rack-heading helper and its two call sites;
the T3 five live-title passes with the admitted `0.125F` highlight; and H1's
private inset-field/grain helper, `HeaderH1` selector and renderer-domain
fallback. These private helpers operate on `Drawing` and immutable layout
inputs. A38 independently extracted and compared the Upper/Lower material
helpers, T2 rack helper and other heading helper with genuine pre-H1 source:
all are exact. Normalizing the one header material-selector argument makes
the entire `reference_header` body identical to accepted T3r2. Its title,
caption, rules and child call arguments/order are therefore unchanged by H1.
The initial H1 grain-cull rejection and its independently admitted one-line
deletion remain recorded separately.

`tools/capture_standalone_interface.py` adds an optional two-view aspect
extension while preserving the thirteen-view default. The three comparison
tools are offline verification utilities. Standalone CMake changes at this
snapshot register tests; production core/plugin dependencies are unchanged.
Native/test changes add fixtures, strict replay fields, narrowly transitioned
heading oracles and capture checks. A37/A39's concurrent new regressions and
root's eventual integration are not accepted by this review.

## Replay diagnostic exception and A31 timeout

A38 read [A15](../development/2026-11-16-heading-title-continuation/notes/A15.md),
[A20's admission](REPLAY_UI_HISTORY_ADMISSION.md) and the actual base/current
diff. The 512-entry UI history reserves only for an input script and records
on the application thread. Adjacent overlay/focus pairs are compared before
capacity, so an unchanged pair consumes nothing even at capacity; later revisits
remain ordered. A distinct pair at 512 sets sticky truncation/fatal flags, stops
the loop and appends nothing. Existing completion, success and exit checks fail
closed. Pointer opening is retained before another event can advance focus.

The original guarded musical-observation suffix is byte-identical; A38
reproduced A20's exact digest
`43a0234454ff6204fca949cbabeaf0e92089b156062fb84059252d734ed4b4be`.
`replay_acknowledged()` is also byte-identical. AudioDevice, Session, parser,
Engine, state and publication implementations retain their original bytes.
Normal operation and MIDI-only replay do not reserve or record the UI trace.
This source argument is not new callback allocation/deadline evidence.

The UI-replay object intentionally gains `ui_observation_capacity`,
`ui_observations_truncated` and `ui_observations` under diagnostics schema 3.
Repository exact-key consumers require the new exact types; Boolean values
cannot substitute for integers. **An external exact-key UI-replay consumer must
accept these additive members.** Unchanged diagnostic-object shape is not claimed.
The original eleven-focus assertion remains exact on the appropriate UI history;
new immediate keyboard/pointer and maximum-256-event regressions preserve
startup restoration and literal musical-state checks. The 512/513 transition
boundary remains source-reviewed, not executed; the parser's 256-event budget
was not relaxed.

A31's `tests/test_render_controls_admission.py` change is test-only. Independently
normalizing its single post-`SIGCONT` `communicate(timeout=45)` back to 15 makes
the entire module AST identical to published T2. All correctness assertions,
1.2-million-frame/block-one workload and 90-second CTest limit remain unchanged.
The original timeout and local LSan runtime fatal remain retained; the local
no-LSan pass is not leak qualification.

## Existing executed evidence inspected

These are root-owned observations, not reruns by A38. Exact report/source hashes
are retained in the independent receipt.

| Evidence | Observed result and boundary |
| --- | --- |
| T2 paired report `db18227d…` | 158/158 pairs, 92 complete-model pairs, 74 required exact frames; all case metadata equal, zero forbidden changes. Accepted T2 painter `94186192…`. |
| T3r2 paired report `efcf5fb6…` | 158/158 pairs, 92 complete-model pairs, 90 exact frames, all 213 protected inputs and zero outside changes. Material 1,317/1,317; separate density 18/18. Accepted painter `10865a6b…`. |
| H1 candidate paired report `058cfb0b…` | 48 main + 16 companion pairs, required repeats complete, all metadata equal and zero exterior changes; 103/103 screens, candidate 10,542 fixture checks including 95 helper probes, and native material 1,317/1,317. This is numerical evidence at the pinned candidate, not final visual/resource acceptance. |
| Replay / calibration | Root's 23-method CLI target passes in 22.83 s; rebuilt calibration plus Upper/Lower/clip targets pass 4/4. Original baseline and stale-probe failures are retained. |
| T3 affected integration | Five native targets pass, 56.22 s. The original T3v1 geometric rejection remains distinct. |
| A31 changed-suite verification | Five methods / 45 CLI invocations pass in Release 4.253 s and local ASan/UBSan 20.095 s with documented `detect_leaks=0`; changed-source hosted leak checks remain separate. |

## Remaining gates

Root owns H1 timing/full-frame visual acceptance, final coherent qualification,
publication and exact-source hosted results. This review closes no real-device,
display/DPI/input, native accessibility, callback deadline/retirement, DAW,
physical-fidelity or signed-distribution gate. **Literal whole-interface 1:1
remains unmet and unwaived.** Source preservation and UI compatibility do not
establish M9 product release, and published T2 platform results cannot qualify
unpublished T3/H1 changes.
