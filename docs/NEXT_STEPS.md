# Next steps

<!-- console-next-current:start -->
<a id="current-console-continuation--16-november-2026"></a>
## Current console continuation — 17 November 2026

Read the full [M0–M9 plan](PLAN.md), [standing instructions](../AGENTS.md),
[handoff](CONSOLE_COMPLETION_HANDOFF.md), [setup](CONSOLE_SETUP_AND_HANDOFF.md),
[live checkpoint](development/2026-11-16-console-completion/CHECKPOINT.md),
[actual ledger](development/2026-11-16-console-completion/assignments.json) and
[root queue](development/2026-11-16-console-completion/ROOT_NEXT_QUEUE.md).
Root owns integration, the one `../build-native`, acceptance and publication in
`/workspace/scratch/21cce69f7784/Hammond-B3-Organ`. Confirm current ownership,
HEAD/tree/index/dirty files and fresh remote before acting; other workspaces and
older dated entries below remain read-only/historical.

### 1. Recover the completed source and qualification

<!-- console-final-publication:start -->
The [verified combined implementation publication](development/2026-11-16-console-completion/reports/combined-indexed-publication.json)
is `523c1979334b0fbb624ce120128a0b8ada078383`, tree
`893441fe87859b9dbad81a5d81a453f7c96030f8`, with ordered parents
`8189a49eacab5d4e6ce6c178862e83b03bdec437` and
`54859886268ce83c36f359c43327f7c72a77ae82`. Guarded nonforced publication and
independent API/Git verification preserve both histories and verify the full
7,911-file tree, all 587 qualified source inputs and 12 reviewed Markdown inputs.
The [independent combined admission](development/2026-11-16-console-completion/reports/A59-copied-state-followup/combined-admission.json)
and [root review](development/2026-11-16-console-completion/reports/combined-indexed-root-admission.json)
retain the exact local qualification: **71/71 P1 and 41/41 header source methods**,
**3/3 native reader CTests**, and **1/1 repository-integrity CTest (41 methods)**.
All 96 published source-test bodies remain unchanged. Five Python files differ
from `5485988`; the other 582 inputs, all C++ fixtures, production application,
workflows, criteria and deadlines remain unchanged. Published comparator schemas,
strict original/active reader identities and bounded failure diagnostics are retained.

<!-- console-final-ci:start -->
**All sixteen hosted jobs pass at source `523c197`, attempt one, with no cancellations
or retries.** The [complete source-specific CI record](development/2026-11-16-console-completion/reports/final-ci-complete.json)
binds root's independent API observation and the three retained admissions:

| Workflow | Actual result at `523c197` | Independent evidence |
| --- | --- | --- |
| [Core 44043394024](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44043394024) | 6/6 jobs; five 209/209 CTest families plus full R4 | [A56 Core admission](development/2026-11-16-console-completion/reports/A56-final-hosted/README.md) |
| [Native 44043394005](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44043394005) | 6/6 jobs; five 78/78 families and strict 41/41, totaling 431/431 instances | [A57 Native admission](development/2026-11-16-console-completion/reports/A57-final-hosted/admission.md) |
| [VST3 44043394002](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44043394002) | 4/4 jobs; 29/29 CTests and 47 actual-module validator passes on every platform | [A58 VST3 admission](reviews/CONSOLE_FINAL_VST3_HOSTED_ADMISSION.md) |

Windows actually runs 45 capture, 41 header and 71 P1 source methods, then reaches
all 18 title cases, 103 H1 inequalities and 191 P1 checks/62 screens successfully.
Strict native evidence verifies 41 tests, 37 executables and 63 source inputs with
ASan/UBSan/leaks and unchanged deadlines. Optional internal Python subcase skips,
including the Windows FIFO case, remain disclosed in the full receipts; no CTest
is skipped or disabled. These results qualify this exact implementation source.
The same reviewers add no worker credit, and all earlier failures remain intact.
<!-- console-final-ci:end -->

The preceding indexed source `5485988` has [16/16 successful hosted jobs](development/2026-11-16-console-completion/reports/indexed-remote-ci-complete.json),
including Windows native 78/78 and strict sanitizer 41/41. Its
[complete Native admission](development/2026-11-16-console-completion/reports/A57-indexed-hosted/admission.md)
preserves actual title 18/H1 103/P1 191+62 outcomes, full logs, package checks and
instrumentation. The earlier seven-test local qualification and complete Linux
stream equality remain separate source-bound observations. Original cf87/d2ed
failures are retained; the exact MSVC mechanism and d2ed P1 non-screen failure
identity remain unproven. Later closure documentation retains these source identities;
the [live checkpoint](development/2026-11-16-console-completion/CHECKPOINT.md) records current publication and next work.
<!-- console-final-publication:end -->

First console source [cf87a587](development/2026-11-16-console-completion/reports/implementation-publication.json)
is already published and independently verified. All sixteen attempt-one jobs
are terminal: Core 5/6, native 5/6 and VST3 4/4 succeed. Preserve the original
Windows Core 207/209 path-fixture failures and native P1 C4702/C2220 failure
with zero acceptance execution. Their complete [Core](reviews/CONSOLE_CORE_HOSTED_ADMISSION.md),
[native](reviews/CONSOLE_NATIVE_HOSTED_ADMISSION.md) and
[VST3](reviews/CONSOLE_VST3_HOSTED_ADMISSION.md) reviews are separate source-bound evidence.

The [five-file repair admission](reviews/CONSOLE_WINDOWS_REPAIR_ADMISSION.md)
and [local qualification](development/2026-11-16-console-completion/reports/windows-repair-local-qualification.json)
are complete: one source-only run each at 54/54, 45/45 and 24/24, plus 3/3 affected
CTests with unchanged Linux fixture/application. Do not repeat them to create a
green aggregate. The verified repair receipt already binds the exact five-file
identities and all 587 inputs; do not republish that completed stage. The same
A56/A57/A58 reviewers inspect every new-source family and retain separate receipts.
Their follow-ups create no new worker credit.

The d2ed03b and `5485988` outcomes remain separate history. The final `523c197`
source now has all sixteen hosted families independently reviewed and successful;
no unchanged-source retry or relaxed oracle was used. All sixty workers are
accepted, six per wave, with strict note-hash closure. Preserve the original
246/247 full failure and later source-specific qualifications without rewriting
or transferring their results. Final closure records update documentation and
retained evidence while preserving all 587 qualified source identities.

Before new implementation, recover the actual current HEAD/index/remote and the
[final handoff](CONSOLE_COMPLETION_HANDOFF.md). Do not repeat completed local or
hosted gates solely for worker accounting. New source changes need affected
qualification; documentation changes need their own integrity check. Wait for
any active same-ref CI before another push so it is not cancelled by concurrency.

### 2. Implement native library integration in dependency order

The [native plan](design/LIBRARY_NATIVE_INTEGRATION_NEXT.md) provides the exact
hook map and acceptance cases; the [LibraryModel guide](LIBRARY_MODEL_GUIDE.md)
describes the existing foundation. Recover native/browser owners before overlap.

| Next owner / files | Concrete deliverable and acceptance boundary |
| --- | --- |
| Model/API owner: `LibraryModel.h/.cpp` and design/tests | Independently admit a read-only Save-availability projection carrying basis/revision/sequence and reason. `controls_pending == false`, cached/default state and a pre-Start queued restore cannot prove availability. |
| Input owner: `UiModel.h/.cpp` | Browser gate, parameter-gesture closure and validated focus restoration; preserve original real keyboard/Space/pointer Up ownership, suppress held repeats, and close no note by synthetic release. SDK-free input tests precede main wiring. |
| Adapter owner: `main.cpp` | Freeze real post-Start intention/proof; report every actual submission or disabled-gate result exactly once; centralize Prepare/Start/Stop, fresh observations and synchronous create-only effects with fresh final authorization and exactly-once completion. Preserve ordinary MIDI/recovery policies and the legacy saved baseline. |
| Browser/view owner: new model/view and assigned painter paths | Consume copied LibraryView, own focus/caret/scroll only, reconcile current H1/title support and add actual root/Refresh/Recall/Save routing without duplicating receipt authority. |
| Independent acceptance / root | Actual startup/restart/stopped-Load, held-input/modal, pending-CC11/both-scope, timeout/recovery, collision/protected-path and warning journeys; full-frame/input review, affected coherent regression/sanitizers and exact-source Linux/Windows/macOS evidence. |

Native browser/main wiring and `--library` remain absent until those actual
changes and journeys are admitted. The five current harnesses supply foundation
evidence only. Update README from newly admitted actual captures after UI changes.

### 3. Preserve the full plan and separate product exits

The current [combined gallery](design/native-gallery-console-combined/manifest.json)
and its [all-frame admission](reviews/CONSOLE_COMBINED_GALLERY_ADMISSION.md) remain
unchanged. Historical paired/timing results retain their exact sources; H1/P1
support separation is bounded, with a documented tiny-scale alias. Recover all
[owners](PLAN.md#current-ownership-and-source) before contact/audio, scanner,
crossover, R4/R5/R6 or accessibility work. Preserve 47 parameters, state4/readers
1–3, 91 sources, UUIDs, 147 keys, 24 presets, four banks, 68 controls and the nominal
dry Engine. The [500-page/M0–M9 crosswalk](reviews/CONSOLE_ATLAS_CROSSWALK.md)
retains physical acquisition, M5/M6 graphs and dry validation, real device/DAW/
display/DPI, callback lifetime/deadlines, rights and signed-release gates.
**Literal whole-interface 1:1 remains unmet and unwaived.**

<!-- console-next-current:end -->

> The following heading/header entries retain the published track's original
> workspace, source identities and observations. They do not assign this checkout.
<!-- heading-title-next-current:start -->
## Current heading, title and header continuation — 17 November 2026

Recover the complete [M0–M9 plan](PLAN.md), [agent instructions](../AGENTS.md),
[current session](development/2026-11-16-heading-title-continuation/README.md),
[checkpoint](development/2026-11-16-heading-title-continuation/CHECKPOINT.md) and
[actual ledger](development/2026-11-16-heading-title-continuation/assignments.json)
before assigning work. Root owns this checkout's shared integration, native
build, acceptance and publication. Use [current setup](STATUS.md#current-workspace-and-setup),
not a historical workspace or another owner's build. Check live HEAD, index,
worktree and remote state; preserve unpublished overlays and declared ownership.

T2 rack headings and T3 title revision 2 are implemented and accepted within
their frozen scopes. H1 has complete numerical, actual-frame visual and
representative software timing evidence; its permanent regressions are integrated.
These are no longer unimplemented proposals. Use the current
[status](STATUS.md#current-heading-title-and-header-continuation--17-november-2026)
and stage receipts for exact results. The following sequence is dependency
ordered: consult root's current checkpoint and skip gates already completed at
the same qualified source rather than repeating historical work.

All **60 distinct workers were dispatched in ten waves of six;
60 deliveries are accepted**.
All ten waves have six accepted deliveries.
Follow-ups retain their original worker identities and create no additional credit.
The [executed strict record check](development/2026-11-16-heading-title-continuation/reports/helper-worker-strict.json)
passes with zero pending workers/errors; it verifies record consistency only.
Current `main.cpp`/app remain `0c02c619…` / `1fa2a247…`, with painter `0bf731a6…`.
The [two installed captures](design/native-heading-final/README.md) use that
application; the historical fifteen-view gallery retains `bfe8e36d…`.
The [qualified-final local run](development/2026-11-16-heading-title-continuation/reports/qualified-final-coherent-results.json)
remains **240/242**, with exactly three separate unchanged diagnostics passing.

The [current verified publication](development/2026-11-16-heading-title-continuation/reports/hosted-repair-publication.json) is
`03c70c103a4a0dd72b323529416b909c19a4e139`, tree
`f639acf69061a4b66a0bd3d2219b1ed890e74e42`, with sole parent
`fba1911259346bfc6fd3ba7ec78b5cf6c4d1a6b2`. Root's guarded, nonforced update
and independent API/Git checks verify the exact commit, tree, parent and contents.
This is the published three-input repair, separate from the next locally
qualified helper correction, which is not yet published.

The [complete published-source matrix](development/2026-11-16-heading-title-continuation/reports/hosted-repair-ci-complete.json)
contains **14 successes and two failures**, with all sixteen attempt-one jobs
terminal and **no cancellations**. **Core 6/6 and VST3 4/4 pass**. Standalone's
Linux MIDI OFF/ON and ARM macOS normal jobs succeed; its Linux ASan/UBSan/leaks
job executes and passes **34/34 gates**. Windows job `133832484867` fails
C4702 at fixture line 49 under unchanged `/W4 /WX`. Intel macOS job
`133832484811` completes **67/68**, with preset raster timing out at **30.05
seconds** under its unchanged **30-second** guard; post-acceptance source/
dependency verification and relocated executable packaging remain skipped.
The [independent Intel review](development/2026-11-16-heading-title-continuation/reports/a52-repair-core-hosted/intel-standalone-independent-review.json)
and [root publication admission](development/2026-11-16-heading-title-continuation/reports/helper-publication-admission.json)
are complete. They retain that failed gate, its full workload and unchanged
guard, and permit only the separately qualified Windows helper publication
with complete evidence and current documentation. The timeout supplies no
completed counters or measured remaining runtime; no timing fix, specific
cause or repeated stability is claimed. No local or CI retry is admitted.

The [original source publication](development/2026-11-16-heading-title-continuation/reports/source-publication.json) is
`fba1911259346bfc6fd3ba7ec78b5cf6c4d1a6b2`, tree
`b62f212300d75633346ab8fc5ffdd722255fe00a`, with parents
`9d60dbf462a90fe422fd4e69757fe202264acb7c` and
`835755a9069c25ce55bc2c231547458b4b3ffce4`. The guarded, nonforced
update and independent API/Git verification preserve both histories and verify
the exact contents. This published tree equals local authored merge `07aafd218…`.

The [original hosted record](development/2026-11-16-heading-title-continuation/reports/source-ci-complete.json) is
Core 6/6 and VST3 4/4 successful; standalone has four normal 68/68 successes,
one Windows fixture compile failure and one sanitizer cancellation after 30/34
selected passes. The cancellation's originating cause is unproven. The
[first Windows casts/hash correction](development/2026-11-16-heading-title-continuation/reports/windows-header-local-qualification.json)
and the separate 35-minute sanitizer job budget entered published `03c70c1`.
Both original receipts stay intact.

The [next two-file helper correction](development/2026-11-16-heading-title-continuation/reports/windows-helper-local-qualification.json)
is implemented and locally qualified. It moves the same false return into an
explicit `else` for the dependent `if constexpr` helper predicate and updates
the one active fixture-hash literal. Both existing affected CTests pass
**2/2 in 38.725693459 seconds**, with an identical Linux fixture binary, all
48 actual cases, the exact **10,542-check/163-painting** default result and
**103/103** canonical criteria. Complete statistics differ only in the two
recorded source identities; canonical pixels and historical comparators are
unchanged. Both helper-present and helper-absent specializations are preserved
by independent source/instantiation review; **no new helper-absent runtime
execution is claimed**.

Relative to published `03c70c1`, exactly **two of 475 inputs change and 473
remain unchanged**. Relative to original `fba1911`, the total is still **three
changed and 472 unchanged**. Production app `1fa2a247…`, `main.cpp`
`0c02c619…`, painter `0bf731a6…`, and the already-published **35-minute**
sanitizer job allowance remain unchanged. Every test/child bound, workload,
instrumented input and leak policy is preserved. **The next helper-source
publication and all of its exact-source hosted results remain pending; no
publication SHA is recorded for it.** Local Linux equivalence is not MSVC
compilation or execution evidence. The [independent Intel review](development/2026-11-16-heading-title-continuation/reports/a52-repair-core-hosted/intel-standalone-independent-review.json)
and [root publication admission](development/2026-11-16-heading-title-continuation/reports/helper-publication-admission.json)
permit publishing only this separately qualified helper pair with complete
evidence and current documentation. The preset raster retains its failed
Intel result, unchanged 30-second guard and full workload; the helper pair
is not admitted as a timing fix.

### 1. Complete the current source's integration and delivery gates

1. **Preserve exact previous evidence.** Keep the failed local 240/242 run,
   three unchanged isolated diagnostics, all original `fba1911` attempts,
   published `03c70c1` results and both Windows failures immutable. Staffing
   and strict sixty-record closure are complete; accepted notes stay frozen.
2. **Apply the completed Intel review and root publication admission.**
   The [independent review](development/2026-11-16-heading-title-continuation/reports/a52-repair-core-hosted/intel-standalone-independent-review.json)
   and [root disposition](development/2026-11-16-heading-title-continuation/reports/helper-publication-admission.json) preserve
   the Intel **67/68** result and preset timeout at **30.05 seconds** under the
   unchanged **30-second** guard. All 256 paints/272 readbacks and assertions
   remain intact. No completed counters or remaining-work duration were
   observed; no timing fix or specific cause is claimed. Publish only the
   separately qualified Windows helper pair with evidence/current documents.
   No local or CI retry, timeout/oracle change or broader repair is admitted.
3. **Root publishes and qualifies the next two-file helper source.**
   Preserve the 473 unchanged inputs relative to `03c70c1`, production app,
   both helper specializations, historical comparators, all bounds and
   sanitizer/leak policy. Use a fresh expected remote head, no force and
   independent exact commit/tree/parent/content verification. Publication
   and all next-source CI are pending; no SHA or MSVC success is assumed.
4. **The same A52–A54 observe all sixteen new-source families, then root
   publishes final recovery.** Bind actual runners, toolchains, tests,
   complete logs and artifacts to that new source, especially Windows
   fixture compilation. Earlier passes cannot be silently transferred.
   Wait for all jobs before another same-ref push. Preserve failed outcomes
   and use separate follow-up receipts without adding worker credit.
   Root commits/pushes accepted final evidence and current documentation,
   verifies remote contents and records concrete remaining work.

The [original local publication admission](reviews/HEADING_HEADER_LOCAL_PUBLICATION_ADMISSION.md)
retains the qualified-final **240/242** and three passing diagnostics. The
original and published `03c70c1` trees retain their own results. The next helper
publication and its exact-source qualification remain pending. Current captures
keep their actual app identity,
and historical H1 comparator pins remain binding under the
[reconciliation instructions](reviews/CONCURRENT_UI_DELIVERY_RECONCILIATION.md).

The root-owned recovery build uses the commands below from the current checkout.
They operate only the already configured local dummy-SDL build; normal desktop
and platform setup remains in [README](../README.md#build-and-launch-the-native-application).

```sh
/workspace/scratch/3edffb787db3/build-tools/cmake/data/bin/cmake --build ../build-native --parallel 2
/workspace/scratch/3edffb787db3/build-tools/cmake/data/bin/ctest --test-dir ../build-native --output-on-failure --no-tests=error --parallel 2
```

The complete run and three bounded diagnostics are finished. These commands
remain recovery instructions, not an invitation to repeat the full suite for
a green aggregate. Root owns any separately admitted next native action;
inspect the live checkpoint before configuration, build or execution.

### 2. Continue the reference interface from accepted H1

Start with the original [atlas reference](design/atlas-reference.json), actual
[H1 gallery provenance](design/native-gallery-header-h1-v1/provenance.json),
[visual residuals](reviews/HEADER_MATERIAL_H1_VISUAL.md#residuals-and-handoff) and
the [ownership map](PLAN.md#current-ownership-and-source). Root must reconcile
the manual/rim/cap, concurrent UI-delivery and native browser/semantic owners
before assigning another shared-painter or interaction change.

| Next bounded work | Inputs and acceptance before promotion |
| --- | --- |
| Remaining material and typography differences | Choose one owned surface or live-label scope: manual/rim/shadow geometry, cap/recess lighting, small utility lettering or another panel. Freeze reference observations, literal arithmetic, support, resource limits and rejection criteria before implementation. Preserve accepted T2/T3/H1 and genuine same-state baseline binaries. |
| Whole-interface composition | Define a complete reference/source/state/dimension comparison that preserves truthful controls and engineering inventory. The illustrated preset/vibrato/microphone arrangement cannot justify hiding live controls or implying connected models. Review full application frames, not only favorable crops. |
| Real native use | Execute the [display/device journey](reviews/REFERENCE_REFINEMENT_NATIVE_INPUT.md#concrete-next-actual-displaydevice-journey) on identified OS/backend/display/DPI/audio/MIDI hardware: both resize/navigation directions, pre-held notes, off-window release/fresh press, focus loss, modal cleanup, Save/Load and joined shutdown. Retain actual frames, diagnostics and numeric exits. |
| Native accessibility | Recover the existing semantic owner, freeze the platform bridge's names/roles/values/actions and status announcements, then execute screen-reader and keyboard journeys including pending/applied controls, modal/numeric entry, reduced motion and Flat. A copied semantic inventory or screenshot contrast is not an OS provider result. |

Every visual slice still needs genuine before/after app/fixture identities,
canonical, minimum-active, unequal-aspect, compact, Flat and supported-scale
coverage; exact inactive paths; zero changes beyond admitted support; preserved
state, input and focus; independent whole-frame review; and an actual README
capture refresh. Keep 68 controls including 24 presets, 147 playing keys, four
banks and honest unconnected-model labels. **Literal whole-interface 1:1 remains
unmet and unwaived.** The header's 103 passing patch criteria do not close it.

### 3. Preserve dependent engineering and acquisition work

| Area and owner recovery | Concrete prerequisite and remaining exit |
| --- | --- |
| M3 contact/audio, runtime and conversion owners | Recover the accepted finite conversion/audio contracts before extending full-organ or indefinite capacity. Independently specify absolute scheduling, partition/reset/drain behavior, history publication and retirement, default-PCM preservation, callback work and deadline evidence before Engine/adapter integration. Acquire identified synchronized contact/source/dry captures for physical bounce, resistance, loading and timing. |
| M4 scanner / ScannerLineFoh owner | Preserve the original G5 same-Hz failure and each realization's own frozen gates. Verify revision-specific loaded connectivity, independent AC/transient/mode transitions, stability and actual scanner captures before any live connection. |
| M5 organ electronics | Independently trace the complete identified AO-28 graph, transformer/loading and operating-point inputs. Validate the whole dry G–G boundary, nonlinear convergence and alias behavior before fitting a cabinet downstream. Missing values remain explicit unknowns. |
| M6–M7 Leslie, crossover/fidelity and waveform owners | Keep 122/147 variants separate; acquire amplifier/transformer/crossover/driver loading and electrical captures. Preserve one owner per effect and separate horn/drum radiation. R4 acceptance stays with its owner; R5 audible policy and R6 runtime/Engine integration remain separate. |
| M8 calibration | Follow [A1–A6 acquisition](CALIBRATION_NEXT_ACQUISITION.md): specimen/revision, permissions, calibrated chain/clock, immutable raw files, uncertainty and frozen held-out groups precede fitting. A synthetic audition or schema pass is not an acquired measurement. |
| M9 product release | Execute actual platform/DAW/device journeys, native accessibility and callback deadline/retirement gates. Complete [rights](DEPENDENCIES_AND_RIGHTS.md), packaging and [signed distribution](RELEASE_READINESS.md) independently of numerical/UI passes. |

Preserve the nominal dry Engine, 91 shared free-running sources, 47 parameter
identities, state4/readers 1–3, plugin UUIDs and existing musical histories.
Recover the [native-close review](reviews/PRODUCT_NATIVE_RECOVERY_REVIEW.md)
before below-RtMidi fault injection or checked-close work; a source-proven risk
is not an observed hardware failure, and synchronous fixtures do not establish
OS callback retirement.

### Validate this session's actual records

This request's [ledger](development/2026-11-16-heading-title-continuation/assignments.json)
and checker belong to the heading/title/header continuation. From the repository
root:

```sh
python3 -B docs/development/2026-11-16-heading-title-continuation/check_session.py
python3 -B docs/development/2026-11-16-heading-title-continuation/check_session.py --strict
```

The current checker has **no `--repo` option**. Progress mode permits truthful
unfinished assignments; strict closure requires all sixty accepted distinct
records and substantive matching notes in ten six-worker waves. It validates
record consistency, not external dispatch, product quality, publication, CI or
fidelity. Planned slots, earlier sessions and follow-ups never count as new
workers. Preserve the actual result only after execution; no closure is implied
by this command example.

Checkpoint after every wave and before long operations/context changes: current
source and dependencies, exclusive paths, actual outcomes and retained failures,
resource use and concrete next inputs/acceptance. Root publishes accepted
authorized work, independently verifies it, and updates the handoff without
requesting renewed permission for this scope. Preserve original evidence and
other workspaces; remove only owned reproducible intermediates when needed.
<!-- heading-title-next-current:end -->

<!-- preset-library-next:start -->
## Retained portable registration/apron continuation — 16 November 2026

This section preserves that session's dated state and proposals. The current
sequence above supersedes its former next-task and workspace routing; its
original failures, source-specific passes and separate owners remain intact.

Resume this [session](development/2026-11-16-preset-library-continuation/README.md),
[checkpoint](development/2026-11-16-preset-library-continuation/CHECKPOINT.md),
[actual ledger](development/2026-11-16-preset-library-continuation/assignments.json)
and [integration decisions](development/2026-11-16-preset-library-continuation/ROOT_DECISIONS.md).
The sole writable checkout is `/workspace/scratch/3edffb787db3/Hammond-B3-Organ`;
root coordinates `../build-native`. This opening governs this continuation;
older instructions below retain their dated evidence and separate owners.
The [atlas crosswalk](reviews/ATLAS_DELIVERY_CROSSWALK.md) preserves every
[M0–M9 exit](PLAN.md#milestones-and-exit-evidence). No milestone is declared complete.

### Delivered scope and current qualification

Completed bounded work includes the headless inspection/import/materialization
CLI, renderer `--controls`, twelve proposed-unmeasured recipes in 24 canonical
files, explicit copy-only installation and independent first-use/installed
journeys. Registration materialization preserves supplied current expression;
Performance restores saved expression. Generic Load and rendering restore the
complete file regardless of suffix. The [operator guide](REGISTRATION_GUIDE.md),
[installed admission](reviews/INSTALLED_REGISTRATION_RENDER_ADMISSION.md) and
[native Load admission](reviews/STARTER_NATIVE_LOAD_ADMISSION.md) state the limits.
The CLI and admitted T1 footage typography are implemented, not next proposals.

The [masked apron](reviews/REFERENCE_APRON_RASTER_ADMISSION.md) has 25 paired
cases, 61,780,011 checked pixels, zero forbidden/footer changes and exact
creation-failure fallbacks. Canonical 1672×941 alone has 32,544 exact exposed
source pixels; resizing uses the frozen mapping. The [thirteen-view gallery](design/native-gallery-preset-v1/README.md)
and [whole-interface residuals](reviews/WHOLE_INTERFACE_DELIVERY_ADMISSION.md)
remain the current visual inputs. **Literal whole-interface 1:1 remains unmet
and unwaived.**

### 1. Finish exact-source platform and publication acceptance

The [first verified publication](development/2026-11-16-preset-library-continuation/reports/first-publication.json)
is `20739f6280b95e567e84615d5c5aee443fc3b93d`. Reviewed local follow-up
`503ed724eaeb3c31eae3c6f31b31cc9a2acd9eb3`, tree
`201e38b05901fa30e3d053b9c245829818a5b52e`, is published as
[`cc6be852d616ec5887485e3fccc39ddb1db22006`](development/2026-11-16-preset-library-continuation/reports/followup-publication.json)
with independently verified identical tree and sole parent. Provider commit
metadata differs. The retained
[full local run](development/2026-11-16-preset-library-continuation/reports/w07-integrated-qualification.json)
is **234/235**: copied audition-report links failed, then the focused integrity
repair passed. The [Windows requested-spelling guard](reviews/WINDOWS_REGISTRATION_PATH_ADMISSION.md)
has **six affected Linux passes** and identical Linux binaries. Those facts
do not execute its conditional Windows body or replace the original failures.
The [final first-head observation](development/2026-11-16-preset-library-continuation/reports/first-ci-final-observation.json)
records **six successes, four failures** (report links and Windows ambiguity),
and **three macOS cancellations** with `runner_id: 0` and no steps. It establishes
neither macOS execution nor the cancellation cause.

The [final repaired-source admission](reviews/PRESET_FINAL_HOSTED_ADMISSION.md)
now observes ten successful Linux/Windows jobs: Windows core 202/202, native
61/61 and actual Unicode-checkout generation, plus 28/28 Linux native sanitizer
gates. Three macOS jobs again ended cancelled with no runner or steps; all three
workflow aggregates report failure. The next platform action is actual macOS
execution at the intended source, followed by complete-matrix verification.
Do not infer a cancellation cause or replace absent execution with earlier passes.

Root must preserve concurrent advances, publish accepted paths with a fresh
expected parent and no force, then independently verify remote commit/tree/parent
and contents. Observe every required [13-job matrix](reviews/REGISTRATION_CI_ADMISSION.md)
outcome at that exact source, including Windows raw-path/Unicode-generator
execution, macOS, native sanitizers and VST3. Keep queued/unacquired, cancelled
and failed jobs distinct; stop the platform claim on any missing or failing
required result. Rebuild changed coherent inputs before affected tests. For a
justified full local qualification, root uses:

```sh
cmake --build ../build-native --config Release --parallel 3
ctest --test-dir ../build-native -C Release --output-on-failure --no-tests=error --parallel 3
```

### 2. Carry documented installed use into real native journeys

Use [guide sections 2–7](REGISTRATION_GUIDE.md#2-inspect-and-import-selected-recipes)
with a fresh destination, explicit RegistrationTools/StarterRegistrations
installation and OfflineTools when rendering. Confirm exact 2+26 payloads,
relocation, read-only inspection, collision refusal, scope-correct expression,
full-state restoration and score precedence against the retained independent
admissions. Preserve conservative Unicode refusal: put library/current inputs
beneath ASCII `inputs/` and destinations beneath `outputs/`; never weaken alias
protection to make a journey pass. A late copy/report failure needs inspection
of committed/partial output before retry.

Next execute [native display/device journeys](design/NATIVE_ACCESSIBILITY_JOURNEY_NEXT.md)
on identified OS/backend/display/DPI/audio/MIDI hardware: pre-held notes,
bidirectional resize/navigation, off-window release/fresh press, focus loss,
modal cleanup, Save/Load and joined shutdown. Retain actual frames, diagnostics
and numeric exits. Dummy SDL and Linux relocation establish their recorded
software scopes only. Stop any broader claim without actual platform evidence.

### 3. Propose T2, then separately T3

Root first checks owner ledgers and assigns exclusive shared-painter paths.
Use the [material/type authoring inputs](design/REFERENCE_MATERIAL_TYPE_NEXT.md)
and current residual review, preserving original art, T1 and current baseline
binaries. **T2 changes only the two rack headings' tracking/baseline** and their
measured side-rule gaps. Independently freeze glyph bearings, anchors, support
and criteria before painting; no global font/helper change is implied.
**T3 separately studies title weight/highlight/shadow**, preserving its layout
anchors, truthful subtitle and live utilities. Freeze every offset, alpha/color
and support union; any new font needs pinned provenance and rights.

Each slice requires genuine same-state before/after binaries, reference,
minimum-active, compact, Flat and supported-scale comparisons, exact inactive
frames, zero changes outside admitted support, preserved focus/input/state,
independent full-frame visual admission and updated actual README captures.
Stop on missing baseline, unsupported masks, clipping or illegibility. Only
after separate admission should a header/performance material slice proceed.
Apron pixels, small crops and type improvements cannot close whole-interface 1:1.

### 4. Preserve dependent engineering and release work

Recover [existing owners](../AGENTS.md#ownership): next-phase retains
ScannerLineFoh/LibraryModel/browser/native integration; runtime/conversion retain
contact/audio/manual/rim work; accessibility retains numeric/semantic/cap work;
audio/playable retain leakage/harmonic sources; fidelity retains crossover/MIDI
retirement; waveform retains R4. Check their checkpoints before overlap.
M4 needs revision-correct loaded topology, independent same-Hz/transient/mode
acceptance and actual scanner captures, retaining G5 failure. M5 needs a reviewed
complete AO-28 graph, transformer/loading/operating-point inputs and complete
dry G–G validation before cabinet fitting. M6 keeps 122/147 separate and needs
coupled amplifier/crossover/driver loads, polarity, AC/nonlinear stability and
electrical captures. R5 policy/R6 integration retain separate gates.

Follow [A1–A6 acquisition](CALIBRATION_NEXT_ACQUISITION.md): identified specimen,
permissions, calibrated chain/clock, immutable originals, uncertainty and frozen
held-out groups precede fitting. Synthetic auditions close no physical gate.
Preserve 91 sources, 47 parameters, state4/readers 1–3, four banks, 147 keys,
24 presets and nominal dry Engine. Native semantic/screen-reader journeys,
callback deadlines/retirement, real DAW use, [rights](DEPENDENCIES_AND_RIGHTS.md)
and [qualified signed distribution](RELEASE_READINESS.md) remain open.

### Record and recovery stop conditions

Retain genuine baseline binaries and original failures/auditions/gallery
identities under the [recovery admission](reviews/PRESET_RESOURCE_RECOVERY_ADMISSION.md).
From the repository root, progress validation is:

```sh
python3 -B docs/development/2026-11-16-preset-library-continuation/check_session.py
```

All ten groups now have six accepted distinct new workers and matching notes;
the [strict result](development/2026-11-16-preset-library-continuation/reports/final-session-validation.json)
passes with zero errors. Record validation establishes consistency, not external
participation or product quality. Future sessions must recover the actual
containing commit and fresh remote state, inspect their own checkout, and retain
source-specific hosted outcomes. Missing macOS execution and product gates remain
separate from this completed staffing record.
<!-- preset-library-next:end -->

## Retained dated session history and owner routes

The following text is preserved as earlier-session history. Its words “current”
and “next” refer to those dated sources; completed CLI/T1/conversion/material
work is not reassigned by these older proposals. Recover each owner's live
checkpoint before continuing its unfinished scope.

## Runtime and interface continuation — 16 November 2026

Resume the [current checkpoint](development/2026-11-16-runtime-continuation/CHECKPOINT.md) and [actual ledger](development/2026-11-16-runtime-continuation/assignments.json), then read the [selected scope](development/2026-11-16-runtime-continuation/SCOPE.md). Finish independent admission of the [causal audio contract](CAUSAL_CONTACT_AUDIO_CONTRACT.md), [validation inputs](CAUSAL_CONTACT_AUDIO_VALIDATION.md) and [manual materials](design/MANUAL_KEY_MATERIAL_CONTRACT.md). Retain the new genuine-before fixture before any painter edit. Implement the admitted fixed-storage audio wrapper and isolated idle-manual branch; independent numerical, lifecycle, resource and visual reviews follow. Root owns coherent builds, shared navigation and non-force publication. Earlier next-task proposals below remain historical where superseded.

## Earlier conversion/material continuation — 16 November 2026

This session's source is `/workspace/scratch/0d55e62af118/Hammond-B3-Organ`; root coordinates `../build-native`. The [current handoff](CONVERSION_MATERIAL_HANDOFF.md), [checkpoint](development/2026-11-16-conversion-material/CHECKPOINT.md) and [actual ledger](development/2026-11-16-conversion-material/assignments.json) supersede the earlier session's workspace and next-task pointers below. This request requires **60 new workers in ten waves**; its own ledger records actual progress. Earlier sixty-worker closures do not count again.

The first four waves are published as **`3520c96adcdcf4ce4bcb860082354bf0050a89c3`**, exact tree `1013bbd914a0957ca2c164ef02ca5410a8dcde6b`, with nonforced expected-head publication and independent Git fetch. They deliver explicit certified fractional-to-grid conversion, a separate five-file installer and accepted Lower material. [Publication receipt](development/2026-11-16-conversion-material/reports/wave04-publication.json). Completed first hosted matrix: **11/13 jobs pass**. macOS core fails two test-only path assumptions and Windows core fails the same unresolved-parent comparison. All five native standalone and all three native VST3 jobs pass. [Initial and completed evidence](development/2026-11-16-conversion-material/reports/wave04-hosted-complete.json) and the [raw macOS log](development/2026-11-16-conversion-material/reports/hosted-3520c96-macos-core.log) are retained. A33 has repaired the test path assumptions, with 46 local methods passing; exact repaired hosted results remain pending. Waves 5–6 add operating/install acceptance and **admitted T1 manual-label typography**, with 110 paired frames and three actual-size visual reviews. The initial coherent run passes 218/219; the sole old-font product expectation was precisely transitioned and rebuilt, and its fresh 76-case test passes. [Composite qualification](development/2026-11-16-conversion-material/reports/rim-before-qualified.json) retains this exact sequence rather than claiming a second full run.

The [operating guide](CONTACT_GRID_CONVERSION_GUIDE.md) explains real conversion/refusal commands and certificate limits. The [actual T1 gallery](../examples/demos/footage-typography-v1/README.md) shows the latest admitted UI stage. The original Lower v1 sampling failure is preserved; independently admitted v2 passes 98 pairs and 35 inequalities. Literal whole-interface 1:1, physical calibration, native accessibility and live contact audio remain open. All M0–M9 exit criteria and musical identities remain binding.

### Retained earlier-session record

The dated streaming-session qualification, workspace and future assignments below are retained history. Use the active handoff above for this session's setup and current work; do not treat the older converter/Lower proposals as still unimplemented.

**Code qualification update, 16 November 2026:** implementation `af2b747` and the
Windows I/O repair `2f57723` are published and independently fetched. All **13
hosted jobs pass at `2f57723`**, as recorded in the
[completed platform receipt](development/2026-11-15-streaming-continuation/reports/hosted-2f57723-complete.json).
The original `af2b747` Windows failure remains separate. Local qualification is
[210/210 in 191.90 seconds](development/2026-11-15-streaming-continuation/reports/final-coherent-qualification.json),
then the [sole EOF cleanup](development/2026-11-15-streaming-continuation/reports/publication-source-qualification.json),
then [3/3 affected I/O suites](development/2026-11-15-streaming-continuation/reports/windows-repair-qualification.json).
Earlier receipts keep their original inputs and timings. The
[session checkpoint](development/2026-11-15-streaming-continuation/CHECKPOINT.md)
records completed worker closure and source-qualified publication history.
[All 60 accepted records pass strict validation](development/2026-11-15-streaming-continuation/reports/streaming-session-strict.json).
Code qualification does not close physical, whole-interface 1:1, device or accessibility gates.

## Continue from the completed streaming/material scope

The [active scope](development/2026-11-15-streaming-continuation/SCOPE.md)
delivers the isolated `causal-contact-grid-v1` trajectory and the Upper-rack
inner-metal material change. Its [coherent local qualification](development/2026-11-15-streaming-continuation/reports/coherent-qualification.json)
rebuilt **131 steps** and passed **210/210 CTests in 191.89 seconds**, with all
505 recorded code/test/tool/data inputs unchanged. Independent trajectory,
lifecycle, resource, comparison, gallery and compatibility evidence is retained
in [current status](STATUS.md#current-tested-evidence-and-limits).

The initial base is `4aac394cde4da40906b615573a8779aee2d9a37a`;
implementation `af2b747` and repaired code `2f57723` are published. All 13
required hosted jobs pass at `2f57723`. The original initial Windows failure,
repair and new passing observations retain separate records. All sixty scoped
worker deliveries are accepted, and strict record closure passes; the
[actual ledger](development/2026-11-15-streaming-continuation/assignments.json)
and [checkpoint](development/2026-11-15-streaming-continuation/CHECKPOINT.md)
retain accepted counts and publication recovery. The [closure handoff](STREAMING_CONTINUATION_CLOSURE.md)
collects the outcome and next boundaries. Earlier sessions and followups do not
count toward this request.

The continuation and publication sequence is:

1. Preserve the qualified production inputs, genuine baseline binaries, frozen
   protocols, original failures and independent admissions. Resolve only concrete
   findings; later production/build/test edits require affected requalification,
   while prose/ledger edits require their integrity checks.
2. Preserve the completed sixty-worker strict receipt and every accepted note.
   For new work, record its own actual assignments, substantive review and source
   acceptance without reusing this worker credit. Record consistency alone
   establishes neither work quality, implementation, physical nor external-dispatch
   acceptance.
3. Inspect fresh remote advances and reconcile compatible work while preserving
   other owners' source, index, builds and evidence. Commit reviewable accepted
   paths and push to `main` with a fresh expected head, without force.
4. Independently fetch and verify exact remote commit/tree/parent and intended
   contents, then observe the required hosted jobs at that source. Record
   queued/unacquired, failed, cancelled and successful outcomes accurately.
   A workflow dispatch or older hosted pass is not current-source qualification.

These are already authorized project operations owned by root. The earlier
execution workspace's authentication observations are historical; inspect the
actual current publication path instead of assuming that its access state
applies here.

## Resume this workspace and its delivered tools

Writable source is **`/workspace/scratch/177e78b1ac09/Hammond-B3-Organ`**; the
single coordinated Release build is
**`/workspace/scratch/177e78b1ac09/build-native`**. SDL 2.32.10 at
`/workspace/scratch/ade21b726509/SDL2` is a **read-only dependency**. That other
workspace's checkout, index and build remain outside this session's ownership.

[Current workspace and setup](STATUS.md#current-workspace-and-setup) contains
the exact dependency verification and CMake configuration. This local build is
Ninja Release with testing/standalone ON, MIDI/VST3/sanitizers OFF and native
X11/Wayland/ALSA/PulseAudio/JACK backends disabled. To reproduce its completed
qualification after recovering the configuration, root uses:

```sh
cmake --build ../build-native --config Release --parallel 3
ctest --test-dir ../build-native -C Release --output-on-failure --no-tests=error --parallel 3
```

The 210-test result already qualifies its frozen inputs. Regenerate CMake before
building if test discovery or configuration changes; never test changed headers
against stale objects. Do not broaden testing without a concrete remaining risk.
For ordinary physical desktop use, follow the separate
[normal build-and-launch recipe](../README.md#build-and-launch-the-native-application)
and [platform/MIDI setup](MIDI_EXPRESSION_GUIDE.md#build-the-native-application),
with native backends enabled in a distinct clean configuration. Launch at
1672×941 for wide Dimensional Play; the default 1280×900 is compact. Dummy-SDL
recovery does not qualify a real display, controller, audio device or callback.

The [causal-grid developer guide](CAUSAL_CONTACT_GRID_GUIDE.md) gives a complete
native probe example, bounded CGGRID1 wire format, API lifecycle and focused
checks. Its probe is `../build-native/hammond_causal_contact_grid_probe`.
The inherited [offline reference guide](CONTACT_SWITCHING_GUIDE.md) and
[48-file installation guide](CONTACT_REFERENCE_INSTALL.md) retain their original
numerical-study bindings. The later [Windows I/O repair](reviews/CONTACT_REFERENCE_WINDOWS_REPAIR_ADMISSION.md)
changes only the I/O wrapper within that component; all 48 names, other 47 file
hashes and install rules remain unchanged. The grid/probe is not added to it.
Use fresh report destinations and preserve the prior 36×4 study's numerical
evidence. The current actual-app gallery is
[upper-rack-material-v1](../examples/demos/upper-rack-material-v1/README.md);
the [whole-reference gallery](../examples/demos/whole-reference-layout-v1/README.md)
is the genuine prior baseline.

## Next engineering assignments

The isolated integer-grid trajectory and narrow Upper finish are implemented
and tested; repeating those tasks would not advance the remaining gates.
Root must first assign exclusive paths to each next owner and check the existing
ledgers. The next implementation owners/modules remain future assignments. Six written
proposals and five independent reviews now supply their starting points; their
reviewed calculations are not admitted implementation contracts.

### Reviewed next proposals and decisions

These six planning documents and five independent reviews are completed work.
Their next implementation contracts are **not yet admitted**. Assign exclusive
paths before continuing; retain all original failures and the unchanged default
Engine.

| Next boundary | Starting proposal and independent review | Next decision before implementation |
| --- | --- | --- |
| Integer conversion | [Conversion proposal](research/CONTACT_GRID_CONVERSION_NEXT.md) · [A49 review](reviews/CONTACT_GRID_CONVERSION_NEXT_REVIEW.md) | Freeze rounding, collisions, exact event correspondence including command ties, position/root error budgets and strict atomic certificates. F09 loses an edge/command equality; scalar rounding bounds alone cannot certify topology or audio. |
| Isolated causal audio | [Audio proposal](research/CAUSAL_CONTACT_AUDIO_NEXT.md) · [A50 review](reviews/CAUSAL_CONTACT_AUDIO_NEXT_REVIEW.md) | Resolve portable wider-rational clipping, deterministic bounded sums, grid/audio stage-and-commit, phase origin/reset and independent full-window grading. D=16 and N+33 indexing are supported derivations; initial N≤256 and `1e-4` tolerances remain prospective. The accepted trajectory still permits 4096 frames. |
| Continuing/full-organ capacity | [Capacity proposal](research/CAUSAL_CONTACT_CAPACITY_NEXT.md) · [A51 review](reviews/CAUSAL_CONTACT_CAPACITY_NEXT_REVIEW.md) | Define one input authority, post-expansion quotas, panic semantics, nonsealing boundaries, common rollback and complete callback storage/work. Keep 122×9 manual histories separate from 25×8 pedal bits; the illustrative subtotal is not a complete memory/deadline proof. |
| Whole-window materials/type | [Whole-window plan](design/WHOLE_WINDOW_REFERENCE_NEXT.md) · [Material/type slices](design/REFERENCE_MATERIAL_TYPE_NEXT.md) · [A52 review](reviews/REFERENCE_MATERIAL_NEXT_REVIEW.md) | First author and independently admit Lower L1's own field/grain arithmetic, measurements, genuine current baseline, support and criteria. A mean-fitting bilinear field fails local horizontal slopes. Wood W1 and fraction T1 need separate geometry/scaling decisions; Upper masks/tolerances cannot transfer. |
| Actual native use/accessibility | [Journey proposal](design/NATIVE_ACCESSIBILITY_JOURNEY_NEXT.md) · [A53 review](reviews/NATIVE_ACCESSIBILITY_JOURNEY_NEXT_REVIEW.md) | Run an identified native D1/J1 and percussion P1, genuinely pre-held J2/J3, modal cleanup and healthy-close journey. Observe S0 then admit one native semantic-provider contract. Different percussion Tab ordinals are not a proven focus-identity bug. Reduced-motion preference and numeric text editing remain absent. |

The next visual action is Lower L1 protocol authoring. The next contact actions
are explicit conversion and isolated-audio contracts, with independent numerical
and resource acceptance. Physical [A1–A6 acquisition](CALIBRATION_NEXT_ACQUISITION.md),
M5 dry validation before downstream fitting, actual devices/DAWs, semantic
accessibility and literal whole-interface 1:1 remain independent requirements.

### M3: conversion policy and causal audio

1. **Conversion/design owner — a separately named input converter and contract.**
   Use the [grid contract](CAUSAL_CONTACT_GRID_CONTRACT.md), its
   [independent admission](reviews/CAUSAL_CONTACT_GRID_ADMISSION.md),
   [implementation review](reviews/CAUSAL_CONTACT_GRID_IMPLEMENTATION_REVIEW.md),
   [offline model](FRACTIONAL_CONTACT_REFERENCE.md) and
   [earlier streaming review](reviews/CONTACT_STREAMING_DESIGN_REVIEW.md).
   Freeze how source time, travel, thresholds and speeds enter the integer
   domain: units, rounding, out-of-domain rejection, collisions, stable caller
   order and state retained across calls. Study quantization error and changes
   to threshold/crossing topology, including adjacent commands, tied/reversed
   targets, tiny/subnormal inputs and distinct exact times sharing a binary64
   display. No implicit clamp or conversion may silently redefine v1.
   Acceptance requires independent fixtures and declared error/topology limits
   before the converter is called equivalent to any reference subset.
2. **Audio-stage owner — proposed `include/hammond/research/ContactStream.h` and
   an isolated implementation/tests.** Those paths are prospective. Preserve
   `CausalContactGrid` and the frozen reference as identified inputs. Admit the
   signal, accumulation, lifecycle and work contract before code. The
   [D=16 proposal](CONTACT_STREAMING_NEXT_DESIGN.md) uses
   `z[m]=y_L[m−16]`: emit before integrating `[m,m+1)`, evaluate shared sources
   from absolute **input** time, and retain unfinished centered cells and their
   deterministic sums across every callback boundary. Declare ring retention/
   eviction, equality ordering and complete rollback of cells, cursor, history
   and output. The trajectory itself implements none of this filtering.
3. **Independent numerical owner — a new full-window oracle/protocol.**
   Preserve the existing `tools/contact_switching_oracle.py`, frozen fixture/
   probe set and original [results](CONTACT_SWITCHING_RESULTS.md). Independently
   reconstruct all **289 samples of every retained fixture**, including tails,
   under a separately admitted resource budget. Existing all-sample high-rate
   convergence and 64-probe continuous admission do not supply this missing
   full-window grade. Justify and freeze tolerances before inspecting candidate
   errors; the proposal's atlas `1e-4` limits are still unadmitted. Permit only
   declared D=16 alignment, with no fitted gain/delay or trimmed tails. Retain
   exact events, all arrays/refinements, scaled error/silence cases, response
   checks, failures and source/fixture/toolchain identities.
4. **Lifecycle/resource owner — actual filtered output and complete drainage.**
   Freeze nonempty N processing outputs plus **33 drain samples**, giving
   **N+33 outputs** for reference indices −16 through N+16; retain both endpoint
   zeros and the **N=0 empty exception**. At closure, preserve the already
   integrated left portion of the straddling cell and fill only its remaining
   portion with zero. Distinguish incoming equality edges, endpoint commands,
   the final trajectory snapshot and the raw-gate jump. Physical note release
   continues travel/source/filter evolution and never closes that gate.
   Test one-frame/irregular/maximum partitions, future-command causality,
   cancellation, partial/empty drains, repeated/invalid closure, late rejection,
   short-output retry and continued processing after failure. Reject active
   rate changes; specify stopped drain/reset/phase-origin policy. Measure actual
   prepared storage, allocation scope, bounded work and platform callback
   distributions against predeclared deadline/headroom criteria.

The current **four-key, 4096-frame, 512-command** epoch is deliberately finite.
The [resource admission](reviews/CAUSAL_CONTACT_GRID_RESOURCE_ADMISSION.md)
bounds that model; it supplies neither indefinite full-organ capacity nor an
audio deadline. A separate capacity owner must review clock/counter horizons,
event storage, full manual/pedal ownership and continued phase/history before
extending it. Only after the filtered numerical/lifecycle/resource gates should
an integration owner propose changes to `ContactBank`, `Engine`, standalone or
VST3: explicit scheduling/latency reporting, ownership and callback retirement,
plus unchanged-default PCM evidence. Preserve all 91 sources, 47 parameters,
state4/readers 1–3 and plugin identities. Physical bounce, resistance, tap
loading and specimen timing still require synchronized identified travel,
contact/source/dry captures and held-out evaluation.

### M9: subsequent materials, typography and actual display

| Proposed owner and modules | Inputs and bounded next work | Required acceptance |
| --- | --- | --- |
| Material owner: separately assigned `apps/standalone/InstrumentView.cpp` region | Use the current `c29495e9…` app, [Upper comparison admission](reviews/UPPER_RACK_COMPARISON_ADMISSION.md), [actual gallery admission](reviews/UPPER_RACK_GALLERY_ADMISSION.md) and original atlas cover/page 409. Choose and freeze the next Lower-rack/casework illumination or key/cap bevel/shadow scope; keep the already admitted Upper field as its baseline. | New independently admitted support/metrics, genuine same-state old/new binaries, full-frame review, source/executable/state/pixel bindings and preserved geometry/child order/inactive paths. Do not enlarge the frozen Upper mask to grade another surface. |
| Typography owner: separately assigned label/font/drawing paths | Measure the remaining small labels, density and readable live status against the original reference and current captures. Specify one coherent type/spacing change with explicit inventory and focus constraints before editing shared drawing code. | Actual app captures at reference, minimum-active, compact, Flat and supported scales; independent glyph/clip/contrast checks; all 147 keys, 24 presets, four banks and 68 controls remain truthful and operable. Decorative illustration labels cannot replace live semantics. |
| Display/input owner: normal native backend build and identified hardware | Execute the [concrete display/device journey](reviews/REFERENCE_REFINEMENT_NATIVE_INPUT.md#concrete-next-actual-displaydevice-journey): both resize/navigation directions, held owners, off-window release/fresh press, focus loss, keyboard use and joined shutdown. | OS/backend/display/DPI/device identities, actual step frames, input/diagnostic records and numeric exit status; assess label/focus usability at the observed scale. Dummy SDL provides no substitute for this evidence. |
| Accessibility owner: one platform's native semantic bridge | Freeze names, roles, values, actions, status announcements, focus order, keyboard behavior and reduced-motion/Flat handling from the current live inventory. | Actual screen-reader and keyboard journeys on the identified OS, including pending/applied controls and modal/numeric-entry exit behavior; semantic accessibility is separate from screenshot contrast. |

The current 96-pair/five-screen material result and twelve admitted app captures
close their declared software scopes only. **Literal whole-interface 1:1 remains
unmet and unwaived.** A whole-interface comparison needs its own complete
reference/source/state/dimension criteria; a protected crop, patch statistic or
decorative cabinet equality cannot close it.

### Validate the historical streaming records

Use only this streaming session's
[actual assignments](development/2026-11-15-streaming-continuation/assignments.json).
The [retained strict result](development/2026-11-15-streaming-continuation/reports/streaming-session-strict.json)
passes for sixty distinct accepted records in ten six-worker waves, with all
substantive note hashes matching. Revalidate these records with the matching
checker; preserve their scoped acceptance. A planned slot, old session or repeated
followup is not another worker, and this result cannot close a future session.

```sh
# Progress is valid while the actual ledger is still incomplete.
python3 -B docs/development/2026-11-15-streaming-continuation/reports/check_streaming_session.py --repo .
# Strict closure requires all 60 accepted records and matching substantive notes.
python3 -B docs/development/2026-11-15-streaming-continuation/reports/check_streaming_session.py --repo . --strict
# Separate repository/archive integrity, with its own scope.
python3 -B tools/check_repository.py --json
```

The [independent record-checker review](reviews/STREAMING_SESSION_RECORD_ADMISSION.md)
admits structural ledger/note consistency only. It does not prove historical
external dispatch/concurrency, semantic work quality, publication or product
fidelity. The repository checker is a separate source/archive integrity check,
not a worker-count attestation. Root's documentary link audit is retained
separately. Older `check_product_session.py`, `check_continuation.py` and other
session checkers remain bound to their own schemas/ledgers; do not repurpose
older passing results to close this one.

### Historical execution handoff — 15 November 2026

The prior [execution receipt](development/2026-11-15-execution-continuation/reports/coherent-qualification.json)
records **203/203 CTests in 191.37 s**, its installed 36×4 offline contact study
and canonical wide composition. Its dated handoff stated that worker closure,
publication and current-source hosted CI were pending, and proposed causal
streaming/material work next. Those are preserved historical observations,
not current streaming-session tasks or claims that its owner later completed
them. Consult that [owner's checkpoint](development/2026-11-15-execution-continuation/CHECKPOINT.md)
for later outcomes. [STATUS](STATUS.md#earlier-execution-continuation-snapshot--15-november-2026)
retains the source, original results and then-current workspace/setup.

Likewise, the earlier product session's
[strict record result](development/2026-11-15-product-continuation/reports/product-session-strict.json)
and thirteen successful hosted jobs at `80b8cce1773e4c31bf64cb6c2b7f43e8445ec3fe`
qualify only that ledger/source. They neither count workers nor qualify hosted
execution for this continuation.

## Next dependency-ready phase after session closure

**Retained independent M6 sequence:** the
[fidelity continuation](development/2026-11-15-fidelity-continuation/CHECKPOINT.md)
owns same-Hz numerical work. Recover its actual current source/results before
assigning changes. A new candidate still needs a versioned same-Hz protocol and
independent evaluation. The current ideal circuit, analog references and characterization
already supply the inputs for this engineering work. No new hardware data is
needed to compare declared numerical methods; physical-fidelity claims still
require acquisition.

### Inputs and affected boundaries

Use the [frozen crossover contract](LESLIE_CROSSOVER_CONTRACT.md),
[fixed registry](../data/crossover/leslie-122-ideal-v1.json),
[retained native/reference report](development/2026-11-15-product-continuation/reports/crossover-response-acceptance.json)
and [same-Hz characterization](LESLIE_CROSSOVER_CHARACTERIZATION.md).
The [developer workflow](CROSSOVER_DEVELOPER_GUIDE.md#5-continue-m6-through-explicit-gates)
gives the ordered numerical, acquisition and coupled-model gates. Relevant
modules are `LeslieCrossover`, the independent Python reference/native probe,
the response/lifecycle/allocation tests and their report identities. Agree
ownership before changing them. Preserve the fixed v1 registry, realization,
reports and nominal dry Engine as reproducible baselines.

### Concrete sequence and acceptance

1. **Freeze the experiment before changing the realization.** Declare input
   hold/reconstruction, external sample rates, signal boundaries, frequency band,
   load family and an independent check grid. Set justified magnitude/phase
   tolerances above a stated gain floor, absolute complex tolerances below it,
   and a separate input-admittance criterion. Record their engineering basis;
   no measured or audible threshold exists in the present report. An independent
   review must accept the protocol and the preserved failure/limitation record.
2. **Evaluate one explicit candidate.** State its realization identity and
   physical-state semantics. Compare actual processed output as well as response
   functions, with independent steady-state and precharged transient references.
   A higher internal rate requires explicit input reconstruction, conversion
   filters, latency and clock/history handling. The admitted v1 rates do not
   include 176.4 kHz; a 44.1 kHz fourfold path needs a reviewed extension or a
   different candidate. Preserve documentary L/C values instead of retuning them
   to hide numerical error.
3. **Accept only the declared result.** Retain all grid points and failures,
   signed port/polarity and admittance errors, transient-convergence evidence,
   energy behavior, stopped-rate state preservation, partition equivalence,
   late-failure rollback and subsequent continuation. Measure bounded storage,
   allocation scope and runtime cost on identified builds. A candidate passes
   only its frozen criteria; inconclusive or failed comparisons stay visible.
4. **Leave live integration for its own contract.** A better ideal curve does
   not supply amplifier source impedance, measured driver loading, acoustic
   response or a calibrated cabinet. Coupled M6 and runtime/Engine integration
   require their own ports, ownership and acceptance after the prerequisite
   electrical and dry-organ work.

## Separately owned and acquisition-dependent work

| Track | Next concrete action and inputs | Exit evidence |
| --- | --- | --- |
| M4 scanner | Coordinate with the [scanner handoff](SCANNER_HANDOFF.md) and [ScannerLineFoh owner](development/2026-11-15-next-phase/CHECKPOINT.md); recover their distinct source, graph, transient and [numerical contract](SCANNER_NUMERICAL_CONTRACT.md) identities before further combined-stage work. | Six modes/four tablet combinations, one continuing phase, Q outside modulation, one chorus return, precharged transitions and transactional continuation; then same-Hz/transient/sideband/filter/latency evidence under unchanged declared budgets. Preserve the existing G5 failure at every investigated rate. |
| M5 and physical M6 | Select the applicable primary drawings and actual AO-28/Leslie assembly; independently trace endpoints, differential signs, loads and revision boundaries. Acquire missing transformer, operating-point, source/load and component-loss data. | Reviewed connected topology and explicit unknowns before numerical export; independent loaded AC/nonlinear/alias tests and complete dry G–G validation before cabinet fitting. Leslie 122/147 remain separate. |
| M0/M3/M8 acquisition | Use [A1–A6](CALIBRATION_NEXT_ACQUISITION.md) with identified specimen, permission, calibrated chain/clock and repeatability plan. Begin an external-output pilot archive, then boundary-specific captures. | Immutable originals, source/condition/uncertainty records, admission and acquisition-group splits; justified fitting and untouched held-out/listening outcomes. Contact/latch/tap loading, physical expression and pedal-reactor behavior remain unmeasured. |
| M9 native callback retirement | Assign the [A47-N1 gate](reviews/PRODUCT_NATIVE_RECOVERY_REVIEW.md): in an isolated source-identified prepared RtMidi build, inject failed WinMM reset/stop/close and CoreMIDI disposal below the wrapper while holding a callback before wrapper entry. The suppressed-error gap is source-proven; no hardware failure or use-after-free was observed. | First retain current behavior, then review checked close that reports failure and preserves native handles, callback storage, adapter context and inbox before destructive cleanup. Require poison/no-reopen/no-reset behavior and ordinary leak-free teardown. Successful close also needs platform-specific callback-retirement evidence; return-code checks alone are insufficient. |
| M9 display and device behavior | Use the current native guides and [desktop journey](reviews/REFERENCE_REFINEMENT_NATIVE_INPUT.md#concrete-next-actual-displaydevice-journey) on an identified display/controller/audio system. Preserve painted pre-held input, both navigation/resize directions, off-window release/fresh press, deliberate focus loss and joined shutdown. | Actual step frames, input/diagnostic records and numeric exit status, with OS/backend/device identities. Dummy SDL and synchronous dependency fixtures do not qualify physical timing or driver concurrency. |
| M9 accessibility and further visual work | Use the [current admitted gallery](reviews/UPPER_RACK_GALLERY_ADMISSION.md) and canonical layout/inspection contracts. Treat [older reference gaps](design/PRODUCT_REFERENCE_GAPS.md) as dated evidence; measure current small-label display usability and specify one platform's native semantic bridge before implementation. | Correct live inventory, focus/actions/value/status semantics, actual screen-reader journeys and source-bound visual comparisons. The relative paint budget does not establish frame rate; literal 1:1 equality remains unmet. |
| M9 release | Review [release readiness](RELEASE_READINESS.md), [dependencies and rights](DEPENDENCIES_AND_RIGHTS.md), actual installed artifacts and named DAW workflows. | Device deadlines, DAW save/reopen, redistribution/branding decisions, platform signing/notarization and qualified distribution remain separately observed gates. |

## Preserve the independent R4 owner

Preserve the other owners' unfinished work: [harmonic source/racks](development/2026-11-15-playable-continuation/CHECKPOINT.md),
[scanner and registration library/browser](development/2026-11-15-next-phase/CHECKPOINT.md),
[crossover/native retirement/deck](development/2026-11-15-fidelity-continuation/CHECKPOINT.md)
and [audio continuation](development/2026-11-15-audio-continuation/CHECKPOINT.md).
The earlier [product closure](PRODUCT_CONTINUATION_CLOSURE.md) and
[setup handoff](PRODUCT_HANDOFF.md) retain their original source-specific results;
their old workspace paths are not this streaming workspace.

The [waveform session](development/2026-11-14-waveform-continuation/README.md)
and its [checkpoint](development/2026-11-14-waveform-continuation/CHECKPOINT.md)
retain their other checkout and actual worker ledger. The implemented
[renderer contract](ROTARY_RENDERER_CONTRACT.md) and
[waveform acceptance](ROTARY_WAVEFORM_ACCEPTANCE.md) govern lifecycle,
scene/receiver symmetry, calibrated allocation and independent
[offline CLI](ROTARY_RENDER_CLI.md) qualification. The owner has its own local
results for these areas; consult its actual current records. Integration,
publication and final acceptance of that work remain with the owner. Its
source-bound full-waveform experiment does not replace those steps or transfer
ownership.
The later [d8 Linux full-mode pass](reviews/PRODUCT_LINUX_HOSTED_REVIEW.md)
likewise qualifies only its published inputs; it does not accept or discard the
other owner's dirty checkout, integration/publication/final acceptance of its
separate results or actual worker ledger.

Preserve `D+6` history capacity (maximum 12,806), the 8,192-entry per-write
journal, `max(D)+4` flush and the reviewed trajectory/borrow/rollback boundary.
Dense changes to both rotors every frame require calls of at most 512 frames
under the 1,024-event cap; legal 4,096-frame calls, repeated wraps, all sixteen
ordered stopped-rate pairs and overflow retain distinct acceptance. R5 audible
policy, R6 runtime/Engine integration and physical cabinet fidelity stay separate.
Inspect compatible remote advances before publication; never edit or remove the
other owner's checkout to simplify integration.

## Historical qualification and completion workflow

Earlier source-bound results remain in [STATUS.md](STATUS.md#historical-results-and-source-boundaries)
and the chronological [development log](DEVELOPMENT_LOG.md). Use the
[completed reference-refinement closure](REFERENCE_REFINEMENT_CLOSURE.md),
[interface recovery](INTERFACE_RECOVERY_HANDOFF.md),
[standalone handoff](STANDALONE_HANDOFF.md), [pedal handoff](PEDAL_HANDOFF.md)
and [calibration handoff](CALIBRATION_HANDOFF.md) for their named inputs and
original failures. The v1–v5 galleries keep their actual capture sources.
Do not repeat a completed session or use its strict checker to count this one.

Every future agent reads the whole plan and [AGENTS.md](../AGENTS.md), claims a
dependency-ready bounded task, records actual source/data/tool identities and
outcomes, and updates the relevant setup/status/next steps/log. Build selected
inputs before CTest and require nonempty required selections. Preserve 47 sound
identities, state4/readers 1–3, 91 shared sources and musical ownership. The
integrator accepts the owned diff, preserves concurrent advances, commits and
publishes authorized work with a fresh expected head and no force, then verifies
publication and its actual required results. Checkpoint each wave and retain
compact evidence before removing only owned reproducible intermediates.
