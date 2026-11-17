# Current checkpoint

Base `9d60dbf462a90fe422fd4e69757fe202264acb7c`; branch `main`.
Root owns this checkout and the single `../build-native`. Other workspaces stay read-only.

**Root record closure, 17 November 2026 UTC: 60 actual workers dispatched and accepted.**
All ten waves have exactly six accepted deliveries. Root reviewed A60 and executed
the [strict record check](reports/final-worker-strict.json): 60 note hashes verified,
zero running workers and zero errors. This closes worker records; hosted/product
qualification remains separate. The [ledger](assignments.json) records every review.

## Current reconciled source — 17 November 2026 UTC

Root committed the separately qualified eight-input candidate and accepted worker
records locally as `4378fff74a3a11de400e3a38b877d170bad6c57e`, tree
`5248bcfe68f15225060dd09adec1e7d6849d6e20`. Its independently API/Git-verified
[equivalent immutable object](reports/combined-indexed-object-preparation.json) is
`8189a49eacab5d4e6ce6c178862e83b03bdec437`; preparing it did not move `main`.
The remote advanced independently to `54859886268ce83c36f359c43327f7c72a77ae82`,
tree `f5f8f037af301f8b1ff5b9b4a00ff5581647667a`; the preserving merge is in progress.
The three indexed C++ serializers are byte-identical in both branches. The
[remote delta review](reports/A59-copied-state-followup/remote-548-source-review.json)
admits its exact H1/P1 source transitions. The merge keeps those published schemas,
adds bounded failure-only P1 diagnostics, and separates original/active reader pins.

Source `5485988` now has [all sixteen attempt-one jobs successful](reports/indexed-remote-ci-complete.json),
with no cancellations: Core 6/6, native 6/6 and VST3 4/4. Windows native passes 78/78,
including title 18, header 103 and P1's 191 checks/62 screens; strict sanitizer passes 41/41.
A57 independently retains the complete six-job Native evidence, all deadlines,
37 instrumented executables and 63 inputs. No result transfers to the merged Python.

The [merged source-only suites](reports/A56-combined-indexed-regressions/source-only-qualification.json)
pass 71/71 P1 and 41/41 header methods, first invocation without skips; every
published 64/32 method body is retained. The separate
[real-reader selection](reports/combined-indexed-local-qualification.json) passes
3/3 in 9.461962 seconds, with all 587 inputs stable. Five Python inputs change from `5485988`;
582 inputs, all C++ fixtures, the application, workflows and numerical/deadline
criteria remain unchanged. The [complete P1 output](reports/combined-indexed-p1-retention.json)
was copied without reexecution and its temporary originals remain present. Earlier
[seven-test and byte-identical stream evidence](reports/array-local-qualification.json)
retains its original source boundary.

Root has refreshed the current README, agent instructions, plan/status/next steps,
log and handoff. Next: finish document integrity after authoring; accept A56/A57/A59
follow-up reports; resolve/stage the owned merge; preserve both parents in the
published commit; use a fresh expected remote SHA without force; independently
verify commit/tree/parents/content and observe all new-source hosted families.
All `5485988` jobs are terminal, so they will not be cancelled by the next push.
All 60 accepted notes and strict record closure remain unchanged. More than 40 GiB
is free; no original evidence or another workspace requires cleanup.

## Historical checkpoint sequence

The following source-bound entries retain earlier observations and next-action
wording. The current section above supersedes their workflow status; immutable
reports and accepted notes remain unchanged.

## Current verified repair; complete CI and next candidate

The [current verified repair publication](reports/repair-publication.json)
is `d2ed03b94114e35d0caa65968d11afe896a5e9f5`, tree
`45f3f2bc1bc844061be7d1303b13b10bfaba9938`, sole parent
`cf87a587d0002d106e5210b57a39fd1967245a8f`. Guarded nonforced publication,
independent API/Git verification and all 587 repaired input identities are recorded.
**All sixteen jobs are terminal: 15 successes and one Windows native failure.**
[Core](reports/A56-repair-hosted/core-d2ed03b9-admission.json) passes all six
families: five 209/209 CTest runs and full R4. Windows actually executes the
45/24/54-method suites and Unicode-generator qualification. Root independently
rehashed all 48 retained Core payloads. [VST3](reports/A58-repair-hosted/summary.json)
passes all four jobs, 29/29 CTests and 47/47 actual-module validator checks per
platform; root rehashed all 58 payloads. Native passes four normal 78/78 families
and sanitizer 41/41; Windows builds successfully then finishes 75/78.
Runs: Core `44034656790`, native `44034656779`, VST3 `44034656821`, all attempt one.

The [actual Windows diagnosis](reports/A57-repair-hosted/windows-copied-state-diagnosis.json)
identifies empty drawbar bank `[0][1]` where nine values are required in both title
and header output. P1 passes all 62 visual screens but one other check fails;
its precise detail was not retained, so a shared cause is unproven. The original
full log, failed result and expected inner FIFO subcase skip remain preserved.

Root's next **uncommitted** candidate replaces one common array traversal block
in each of three native fixtures with indexed traversal. The
[exact transition](reports/array-source-transition.json) and
[genuine before binaries/streams](reports/array-serialization-before/receipt.json)
are retained. A59 independently admits the six fixture/reader/comparator source
files; original pins, strict equality, numerical criteria and paired tools are
preserved. A56 owns two source-only test adaptations and regressions. Root next
runs the three builds, three exact-stream comparisons and seven affected gates.
No Windows success, deeper compiler cause or P1 failure cause is claimed.

## Retained first verified source and terminal CI

The first console source is published as
`cf87a587d0002d106e5210b57a39fd1967245a8f`, tree
`2565ac86f9d31b7ab9d24d0d5353289c2359bf12`, ordered parents
`6287055a111dc4e2747564da3d48edc9b65e2e3e` and
`8cd9034f7e1dd21dab373f0e4ad0d1be0bab61e7`. The immutable
[publication receipt](reports/implementation-publication.json) records expected-SHA/
no-force publication and independent API/Git verification. Its 58/55 and pending-CI
fields retain the original publication-time snapshot, not current progress.

All sixteen original attempt-one jobs are terminal: **14 successes, two failures,
zero cancellations**. [A56 Core](reports/A56-core-hosted.json) has five successes:
four 209/209 CTest families plus full R4. Windows is 207/209 on two Python fixture
path failures; the Unicode-checkout generator step is skipped.
[A57 native](reports/A57-native-hosted.json) has four normal 78/78 successes
(Linux MIDI OFF/ON, ARM/Intel macOS) and Linux sanitizer 41/41. Windows fails P1
fixture C4702/C2220 before any acceptance CTest, copied-state diagnostic reader or
successful installed-package stage executes. [A58 VST3](reports/A58-vst3-hosted.json)
passes all four families, 29/29 CTests and 47/47 actual-module validator checks
per platform. Original logs, attempts and every failed/unrun step remain retained.

## Admitted repair; new-source qualification remains separate

[A59](../../reviews/CONSOLE_WINDOWS_REPAIR_ADMISSION.md) independently admits the
five repaired fixture/comparator/test files. Exactly five of the published
source's 587 inputs change; 582 remain unchanged. Production/app/gallery,
CMake/workflows, `/W4 /WX`, numerical criteria, typed equality, bounds and workloads
stay unchanged. Native path expectations match the unchanged producer, and header
normalization affects only mock lookup keys. The capture newline mismatch is a
source-derived latent expectation, not a separately observed Windows hash failure.

Source-only suites pass **54/54, 45/45 and 24/24 once each**. The separate
[affected local qualification](reports/windows-repair-local-qualification.json)
passes the fixture build and **3/3 CTests**: repository integrity, native P1 and
candidate-only P1 numerical (**191 checks, all 62 screens**). All inputs remain
stable, and the rebuilt Linux fixture and application are byte-identical.
No helper-absent runtime, new paired comparison or full-suite aggregate is
claimed by that local receipt. The repair is independently published as `d2ed03b…`;
its subsequent exact-source hosted outcomes are recorded above.

The predecessor `6287055` Windows run compiled and passed 66/68, rejecting title/
header copied state before numerical evaluation. Its [original complete log](reports/prepublication-628-windows-original.json)
and the separately admitted [failure-only diagnostics](reports/copied-state-diagnostic-qualification.json)
remain retained. The first console source failed P1 compilation before those
readers ran. The later `d2ed03b` output now establishes the two empty-list leaves
recorded above. The indexed serializer candidate preserves the required complete
state and needs fresh execution; a particular compiler mechanism remains unproven.
No weakened oracle/deadline/workload or unchanged-source retry is admitted.

## Immediate root work

1. Recover the completed `d2ed03b…` publication receipt and its verified input
   identities. The same A56/A57/A58 reviewers inspect the new source in separate
   receipts; their follow-ups add no worker. Do not repeat the completed publication.
2. Finish the independent eight-input candidate review and local qualification,
   then publish it with a fresh remote lease. All `d2ed03b` jobs are terminal.
   Its failures remain failures; the next published source needs fresh Windows
   and other-family results without any relaxed oracle, deadline or workload.
3. A60 acceptance and strict worker closure are complete. Execute the final
   repository document-integrity gate after all authoring and retain its receipt
   without promoting the old 246/247 full result or earlier checks.
4. Publish accepted final records/navigation and independently verify remote
   contents and the applicable source-specific CI. Update this live section with
   actual observations while preserving accepted notes and dated receipts.

## Retained qualification and next implementation

The earlier [combined result](reports/combined-qualification.json) remains
46/46 build steps, 78/78 affected tests and 15/15 captures on 587 stable inputs;
all 69 gallery payloads were verified and A48's all-frame review is accepted.
The original full 246/247 stays failed; later document checks pass separately.
The 78-test selection is not a full 251-test rerun. Application
`3bb46f2ff0a830935b5f1122116b7ff457f5e8532ed1f7860843c237d09a89e9`
and the displayed combined gallery remain unchanged by the repair.

Earlier staging/recovery (`34f4f497…`, local `3263b17`/`d22fb75`, API
`280d0f8`/`8cd9034`) and first tree-request failures retain their receipts;
[first publication](reports/implementation-publication.json) is the actual remote
source, not a local authored alias. A55's [exact helper transition](reports/A55-helper-transition.json)
and its [4/4 qualification](reports/helper-transition-qualification.json) preserve
all 117 imported `6287055` evidence additions and original source pins.
More than 41 GiB was free at root's resource observation; no original was removed.

Native browser/main wiring remains absent. The [next plan](../../design/LIBRARY_NATIVE_INTEGRATION_NEXT.md)
starts with model-owned Save availability and a new post-Start proof, then native
input, lifecycle/submission/storage and browser/view hooks. H1/P1 separation is
qualified only in recorded fixture/gallery domains; tiny scales can alias a pixel.
Literal whole-interface **1:1 remains unmet and unwaived**. Recover the
[handoff](../../CONSOLE_COMPLETION_HANDOFF.md), [setup](../../CONSOLE_SETUP_AND_HANDOFF.md)
and [queue](ROOT_NEXT_QUEUE.md). All dated sections below preserve their original
sequence and outcomes; earlier next-action wording is historical.

## Actual progress

Wave 1: all six fresh readers are accepted and cover pages 1–500. The coverage
receipt binds each range, extraction and accepted note. A07–A09 delivered the library API, frozen P1 proposal and exact hosted audit.
A10 independently admits the final LibraryModel API/design; A13 implements only
`LibraryModel.cpp`. A11 verifies P1 statistics/resource/support; A12 owns the
34-export real-painter baseline fixture. Root coordinates all build inputs.
Root inspected the entire M0–M9 plan and current source, extracted all 500 pages,
and completed a clean Release native build with tests enabled, MIDI/VST3 disabled.
The nine required baseline native/model/session selections pass (20.90 seconds).
Genuine pre-edit application, benchmark, header fixture and painter source are
preserved in `../baseline-native`, with a source/binary receipt. The first baseline capture failed its intermediate-held-state assertion: only
three frames rendered during the original 1800 ms run. Original output remains
in `../baseline-gallery`; the failure receipt is retained. A later explicit
replay-time-scale option must preserve the default bytes and every assertion.
The environment has about 50 GiB free; the repository and single build are bounded.

## Next actions

Complete the P1 fixture and its genuine unchanged-source qualification before
production paint. P1 contract final editorial hash is
`20c8839d38229bf24d983eac0baad7381f601c4e6763bbbe556bcdfa6c75ae45`.
The admitted library API hash is
`4ea94b611e4fdc27ea48c6bad47ddf9ed99761f2e12ae264b7482ac8d3b093e2`.
A13 owns model implementation; root must not build partially written inputs.
Next workers implement explicit capture replay scaling, P1 paint, independent
model tests/comparator, and the source-pinned Windows fixture correction.
Root reviews and integrates accepted work, executes affected tests, captures the
actual interface, updates durable guidance, then commits and pushes to `main`.
Starting-source CI has 15/16 successful jobs. Windows native failed at build
on two integer-to-float fixture conversions under warnings-as-errors; the exact
minimal literal repair is required, with original failure preserved. No new
implementation, product acceptance or publication is claimed yet.

## Wave 2 closure and implementation GO

All twelve workers in waves1–2 are accepted. The new P1 fixture compiles, its
ordinary gate passes1/1 in22.31seconds, and all12 canonical quiet-patch RGB
hashes match the frozen T3 source. The unchanged baseline fixture is retained
at `../baseline-native/test_standalone_performance_plate`, SHA-256
`65d0cc74e53faf2d655cba5f6254d5087715c730f22556ec81940195ad18149e`.
A14 now owns only the admitted P1 painter insertion. A13 owns LibraryModel.cpp;
A15 owns explicit capture replay scaling and its focused Python tests. Root
waits for source-ready messages before compiling those inputs.

## Wave 3 implementation checkpoint

A13 delivered LibraryModel.cpp (`ae5348c731b0559a6816b75cc190622918ca89d1fe938dd56445d51591904b98`);
root added it to the SDK-free support target and built the support library and
application successfully. Independent A16 contract tests are still being authored.
A14 delivered the exact P1-only painter insertion
(`8ca5c05138ed4cd12fe8ef416ea35a3d78a8a3c4915645f53d8c0c0df2fcf927`).
The candidate application, benchmark and native fixture build successfully;
the candidate fixture's ordinary gate passes 1/1 in 25.75 seconds. A17 owns
independent paired/numerical comparison, still pending. A15's explicit replay
scale preserves all original default replay bytes and semantic assertions; its
39 Python test methods pass. Root selected scale 3 (5400 ms) and an independent
30-second timeout for later new native captures; the failed original stays retained.
No paired numerical/visual/timing acceptance or new publication is claimed.

## Captured application evidence

The explicit scale-3 native protocol passed all 15 actual application captures
in `docs/design/native-gallery-console-p1`, with every recorded source/build/input
identity unchanged. Application SHA-256 is
`7b812bbbfd86779bb01cb76fe225309dd2d3101d08c6bb7fe2d6730e9d02c2c9`;
canonical PNG SHA-256 is
`a8c9bcb9b35910e09dc040766693553e6385f57e94e144118dcb3bb4eae2b56c`.
These dummy-SDL software captures establish their exact recorded state and views;
independent full-frame visual admission and the P1 paired/numerical/timing gates
remain pending. The original 1800-ms failure is retained separately.
A16 delivered 32 independent pure-model contract groups; root is building them.
A19 now owns a separate real-Session boundary harness. No browser is wired yet.

## Independent model gate and Windows repair

The first pure-model run retained one failed oracle expectation: it assumed an
already resolved but unapplied command might later apply. Independent A19 review
of the real Session confirmed resolved means consumed; root admitted the explicit
[receipt correction](../../reviews/LIBRARY_RESOLVED_RECEIPT_ADMISSION.md) without
changing implementation or relaxing proof. The corrected suite passes all
32 groups / 3,250 assertions; original source/failure and amendment are retained.
A18 delivered the exact reversible Windows float-literal fixture repair with
original baseline/comparator pins preserved. Its 9 Python methods / 22 refusal
cases and original/repaired static comparison pass; root rebuilt the native
header fixture successfully. Exact Windows hosted qualification remains pending.
A17 still owns P1 comparator completion. A19 and A20 own real Session and
real create-only storage boundary tests respectively. Wave4 preparation overlaps
wave3's final comparator review; no unreviewed production branch is enabled.

## Wave 4 boundary and preservation findings

A19 real Session tests pass 12 groups / 42,634 assertions, including 696 real
snapshots, 150 renders, 6,252 bit-exact paired stereo samples, 10,101 source-phase
checks and 60 percussion-history checks. A20 real storage integration passes
9 groups / 1,115 checks; its control-proof input is explicitly synthetic.
All three model suites use unchanged LibraryModel.cpp ae5348c7…; no production
repair was needed for these gates. A21 independently reviews the complete source.

The first P1 paired run completed all 34 pairs and all 70 processes. All 62
candidate numerical screens and pixel preservation checks pass; overall v1 is
FAILED on four metadata oracle errors in both genuine before and candidate
Rotary/Service frames. A22 independently traced the error to the unchanged
UiModel excluding tab focus from remembered workspace-body focus. Root admitted
only that exact comparator correction with refusal regressions; no painter,
fixture, support or numerical criterion changes. Preserve the complete v1.
A23 prepares the frozen eight-process timing runner; no timing sample is run.
Root's supplemental before build reproduces the genuine original benchmark
byte-for-byte and records its new object/link inputs. This is reproducibility
evidence, not an assertion that the original object had been retained.

## Wave 4 closure and wave 5 integration preparation

All 24 workers in waves 1–4 are accepted. The corrected P1 paired-v2 run passes
34 pairs / 70 processes / 74,008,097 pixel positions, with zero forbidden
changes and all 62 numerical screens passing. Report SHA-256:
`f64b634d5455e69e506730acac036e6b3764804d775ff4bdabb4d0a4e0abe1d4`.
A24 directly compared all 15 current and preceding full-frame captures and
admits this narrow P1 material change. Literal whole-interface 1:1 remains
unmet. Original paired-v1 failures, streams and comparator source remain intact.

A26 delivered an independently testable, patch-only `UiModel::recall_controls`
helper. It validates the complete snapshot, publishes exactly one whole-control
action and preserves the legacy saved baseline. Root has not applied it while
timing inputs are frozen. A27 owns independent public-API tests; A28 owns real
UiModel/LibraryModel/Session/storage roundtrips. Neither is a native browser.

The first same-scene Flat capture stopped before SDL initialization or painting:
the explicit `SDL_RENDER_BATCHING=1` environment causes SDL's normal-priority
`SDL_SetHint` to return false even for the same value. A25 independently verified
the pinned SDL implementation. The complete failed before-process streams and
receipt are retained in `reports/p1-flat-witness-v1`; after was unrun, with zero
timing samples. Source snapshots retain the original runner/driver and admission.
The admitted prospective correction removes only that environment entry; the
unchanged native code must still set and report effective batching 1. New
preflight-v2 protocol SHA-256 is
`9b9cef5f2c1ea0d6900c90ef6df63da5c5f7f9aaca9a91505f5b94192e2aa8f6`.
Capture-v2 and the fixed eight-process timing batch await final independent
source admission. No timing result is claimed. The source/build freeze ends
after this admitted batch; then root applies the helper and builds coherent inputs.

Fresh remote `main` remains the starting `9d60dbf…`; no session publication has
occurred. About 47 GiB remains free. All other workspaces remain read-only.
