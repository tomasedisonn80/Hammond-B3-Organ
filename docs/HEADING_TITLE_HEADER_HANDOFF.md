# Heading, title and header: development handoff

17 November 2026. This handoff belongs to the active continuation in
`/workspace/scratch/5a28c3564dbf/Hammond-B3-Organ`. The
[latest checkpoint](development/2026-11-16-heading-title-continuation/CHECKPOINT.md)
and [actual ledger](development/2026-11-16-heading-title-continuation/assignments.json)
own subsequent progress. Read them before treating any dated result below as
current. The [complete M0–M9 plan](PLAN.md) remains the project specification;
this document makes recovery and the next decisions practical.

## Where the work stands

T2 rack headings, T3 revision 2 title treatment and H1 header material are
accepted within their separately frozen visual scopes.
All **60 distinct workers were dispatched in ten waves of six;
60 deliveries are accepted**.
All ten waves have six accepted deliveries.
Follow-ups retain their original worker identities and create no additional credit.
The [executed strict record check](development/2026-11-16-heading-title-continuation/reports/helper-worker-strict.json)
passes with zero pending workers/errors; it verifies record consistency only.

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

All sixteen original job families are terminal at that exact source, attempt 1:
[14 successes, one failure and one cancellation](development/2026-11-16-heading-title-continuation/reports/source-ci-complete.json).

| Workflow | Original source-specific result |
| --- | --- |
| [Core CI](development/2026-11-16-heading-title-continuation/reports/a52-core-hosted.json), run `44016021552` | **6/6 successful**: four platform Release jobs and Linux ASan/UBSan/leaks each pass 202/202; full R4 qualification also passes. |
| [Native VST3](development/2026-11-16-heading-title-continuation/reports/a54-vst3-hosted.json), run `44016021543` | **4/4 successful**, 29 CTests across the jobs; each actual module validator passes 47/47, with installation and packaging checked. |
| [Native standalone](development/2026-11-16-heading-title-continuation/reports/source-ci-complete.json), run `44016021554` | Four normal jobs pass **68/68 each**: Linux MIDI OFF/ON and both macOS architectures. Windows fails fixture compilation under `/W4 /WX`; the Linux sanitizer job is cancelled after **30 of 34 selected tests pass**. |

The standalone cancellation occurred during preset raster, leaving it and three
later tests incomplete. No sanitizer finding or originating cancellation cause
is established. It is not a successful sanitizer gate. Original logs, failures
and cancelled/unreached work remain retained.

The [first independently reviewed Windows fixture correction](reviews/HEADER_MATERIAL_WINDOWS_PORTABILITY_CONFORMANCE.md)
is [locally qualified](development/2026-11-16-heading-title-continuation/reports/windows-header-local-qualification.json):
two explicit float casts plus one active fixture-hash literal across two files.
Both affected CTests pass **2/2 in 43.593519385 seconds**. The Linux fixture
binary, all 48 case descriptions and default 10,542-check/163-painting result
are identical. All **103/103** canonical criteria pass; complete statistics
differ only in the two source identity values, with unchanged canonical pixels.
At this Windows-only stage, **473 of 475 qualified code inputs are unchanged**.
Production app `1fa2a247…`, painter, workloads, criteria and historical comparators
are unchanged. This first local correction entered published `03c70c1`;
its Windows job subsequently failed C4702 at the optional-helper fallback.
That actual compilation failure remains retained separately.

Root [implemented the separately admitted sanitizer job budget](development/2026-11-16-heading-title-continuation/reports/native-sanitizer-job-budget-implementation.json):
only `jobs.native-sanitizers.timeout-minutes` changes **20 → 35 minutes**.
Every other workflow byte, all 34 selected tests, 31 build inputs, individual
test/child limits, workloads, instrumentation and leak policies are unchanged.
Published `03c70c1` changed only the Windows fixture pair and workflow scalar:
**exactly three of 475 inputs change; 472 remain unchanged**. Production
sources and app `1fa2a247…` are unchanged. The observed prefix plus existing
tail-limit envelope is 1,823.666679 seconds; this supports the job allowance
without proving what caused the original cancellation. Publication is verified
at `03c70c1`; its actual hosted outcomes are identified above.

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

The [reconciliation review](reviews/CONCURRENT_UI_DELIVERY_RECONCILIATION.md)
preserves both histories and the adopted comparators' historical protected-main
pin. Reproduce old H1 evidence with its named source view. Other sessions retain
their own workers, evidence, checkout and unfinished ownership.

The current application is `1fa2a247…`, main `0c02c619…`, with unchanged H1
painter `0bf731a6…`. Its reviewed replay fixes preserve UI history, resize
boundaries and intermediate scripted semantic paints. Both genuine-before
six-view cases fail only actual painted visits; both current cases pass, as do
three unchanged resize/helper CTests. A [fresh 17-file installation](development/2026-11-16-heading-title-continuation/reports/final-native-install.json)
passes exact metadata, 38 guide-link and relocated-help checks. The
[two current installed captures](design/native-heading-final/README.md) pass
unchanged native capture validation and independent visual review; original
BMP bytes are retained losslessly. The historical 15-view H1 gallery keeps its
original app bfe8 identity.

The independently admitted [startup-prefix oracle](reviews/WORKSPACE_STARTUP_OBSERVATION_CONFORMANCE.md)
is now implemented. Its acknowledged startup prefixes and stronger copied-state
chronology retain every original journey and timing requirement. The current
workspace fixture is `38808674…`; standalone CMake is `64265511…`. The
[qualified workspace records](development/2026-11-16-heading-title-continuation/reports/qualified-workspace-records.json)
retain all 37 actual children from the complete run.

The [qualified-final full run](development/2026-11-16-heading-title-continuation/reports/qualified-final-coherent-results.json)
completed **240/242**, exit 8, in **740.263707625 seconds**. All **475 code inputs
and recorded build inputs remained unchanged**; six serialized tests had
verified nonoverlap. Workspace replay passed with **37 actual native children**,
and Starter Load passed. The two failed CTests were the preset-raster
**30-second timeout** and native MIDI replay, with two missing
acknowledgment-window observations. This is distinct from the earlier
[semantic full run's 240/242](development/2026-11-16-heading-title-continuation/reports/semantic-final-coherent-results.json).

Exactly three bounded, unchanged diagnostics followed. The
[preset-raster diagnostic](development/2026-11-16-heading-title-continuation/reports/preset-raster-one-isolated.json)
passed once in **27.517879209 seconds**, retaining its 30-second limit.
The [two failed MIDI methods](development/2026-11-16-heading-title-continuation/reports/qualified-midi-one-isolated-diagnostics.json)
each passed once in **2.031860108** and **2.037485655 seconds**, with their
nine-second child deadlines and all 475 code inputs unchanged. These separate
passes preserve the original failed full-run outcome; they establish neither
a green 242-test aggregate nor a particular CPU/scheduler cause. The published
source and its original hosted outcomes are recorded separately in this session.

The earlier H1 237/240, combined 239/241, scheduling 238/241 and semantic
240/242 remain separate original outcomes. These finite software results close
no literal whole-interface 1:1, specimen fidelity, actual hardware/accessibility
or complete product-release gate.

Six new readers covered all **500 atlas pages** in ranges 1–84, 85–168,
169–252, 253–336, 337–420 and 421–500. The
[coverage receipt](development/2026-11-16-heading-title-continuation/reports/atlas-reading-coverage.json)
and [reading map](PROJECT_GUIDE.md#source-and-reading-records) retain their
identities. This is complete textual coverage; it does not assert independent
verification of every figure, cited paper or missing physical measurement.
The atlas's research waves, M0–M9 milestones and ten staffing waves describe
different kinds of progress.

## Recover before editing

1. Read all [AGENTS.md](../AGENTS.md) and [PLAN.md](PLAN.md), then this handoff,
   the [session entry](development/2026-11-16-heading-title-continuation/README.md),
   latest checkpoint, actual ledger and assigned source/contract/review evidence.
2. Inspect actual HEAD, tree, index, worktree and fresh remote state. Preserve
   every unpublished overlay and original. A remembered commit or old document
   cannot establish today's source identity.
3. Confirm exclusive file ownership with root. Root coordinates shared source,
   CMake, configuration, builds, native runs, capture, integration and publication.
   Do not run another build while a comparison or capture is locking provenance.
4. Recover genuine before binaries and their receipts before another visual
   implementation. A rebuilt approximation is not an original baseline.
5. Record setup, commands, results, failed and unrun gates, missing inputs,
   exact identities and next steps. Checkpoint before long work or a context
   change. Root commits and pushes accepted authorized work, then independently
   verifies remote commit/tree/parent and source-specific hosted results.

The existing manual/rim/cap, native browser/semantic, contact/audio, scanner,
crossover and waveform owners keep their boundaries. Use the
[ownership map](PLAN.md#current-ownership-and-source) before proposing work
that overlaps them. Never edit another session's checkout or clean its files.

## Delivered interface scope and evidence

| Stage | Evidence and practical meaning |
| --- | --- |
| **T2 rack headings** | [Acceptance](development/2026-11-16-heading-title-continuation/reports/t2-acceptance.json): 158 genuine paired cases, 92 complete-model pairs, 213 protected inputs and zero forbidden changes. Upper/Lower live text, spacing and side rules were independently reviewed. The bounded UI-only observation trace preserves initial focus without changing musical acknowledgment. |
| **T3 title, revision 2** | [Acceptance](development/2026-11-16-heading-title-continuation/reports/t3-r2-acceptance.json): 158 pairs, zero outside changes, 1,317 material assertions and 18 density cases. The original revision's two geometry failures remain preserved. The accepted revision narrows the highlight offset; it keeps live glyphs and the truthful subtitle. |
| **H1 header interior** | [Complete comparison](development/2026-11-16-heading-title-continuation/reports/h1-candidate-comparison/report.json): 48 main and 16 companion pairs, four repeats, 103/103 frozen numerical criteria, 10,542 candidate fixture checks and zero outside changes. The genuine pre-H1 baseline has 44 passing and 59 failing criteria. The scope is the admitted procedural header field and grain. |
| **Actual visual review** | The [15-view H1 gallery](design/native-gallery-header-h1-v1/README.md) and [independent review](reviews/HEADER_MATERIAL_H1_VISUAL.md) include compact, active wide, unequal-aspect, Flat and other workspace views. These are real dummy-SDL software captures, with named application and painter hashes. |
| **Permanent numerical and clipping coverage** | [Statistics qualification](development/2026-11-16-heading-title-continuation/reports/h1-statistics-qualification.json) retains genuine before 44/59 and after 103/0 results. [Grain qualification](development/2026-11-16-heading-title-continuation/reports/h1-grain-bounds-qualification.json) retains the initial implementation's real tiny-scale failure and the corrected four-case, 96,000-pixel pass. |
| **Paint cost** | [Five-case timing](development/2026-11-16-heading-title-continuation/reports/h1-paint-timing/report.json) uses genuine before/current executables, 30 warmups and 300 samples per case. Active minimum/canonical/wide median growth is 4.47%, 3.24% and 1.26%; no frozen investigation flag triggers. Compact and Flat pixels remain identical. These software timings establish neither display FPS nor audio deadlines. |

H1 reduces the admitted aggregate mean-luminance error from approximately
3.7103 to 0.3675 and residual RMS error from 1.6673 to 0.3183 at the specified
reference patches. These local metrics do not score the entire interface.
The current captured H1 title's encoded-Y′≥100 pixel count in the title ROI,
with no hue filter, is **5,499**; the earlier T3 capture has **5,512**, against
**5,415** in the reference. Keep those stages
distinct. Density acceptance does not remove the remaining higher-threshold
face-density difference or establish 1:1 typography. See the independent H1
visual review for the actual boundary.

### Source identities must stay attached to their results

| Named input | SHA-256 |
| --- | --- |
| Accepted T3/pre-H1 painter | `10865a6bad39bc0a254b8b3f4cf6b013bef48770a2b39c7e9f9a70f438d56366` |
| Accepted H1 painter | `0bf731a692b7cb7c88c200afea86f4ca14239f20a7000f06be484f2a11ebc20d` |
| Application in the H1 gallery and first complete H1 run | `bfe8e36d16f4c5fd15009f2fc4707c06c93388f40870dc9f84696d3367447e7b` |
| Selective replay-repair `main.cpp` | `361ae03aa9e1a369a8fd8d125c21b10e40841d08d768a4c5637b2a3ecf0232f3` |
| Rebuilt replay-repair application before concurrent reconciliation | `2c64e585d8f1da521ff4c4dafe51613dd3aa0692461bfcb8d6450f9ca4971479` |
| Current semantic event-drain main | `0c02c619bd04e69ed70aa7c50cbb8345cbc41a188619e94ca6b8a56a24547537` |
| Current installed/captured application | `1fa2a247e6e90379540ad431776241a885b93223430ac3b0798480d58e96a28a` |
| Reviewed Load observation fixture | `96139c491057d1b3c28e4a79b9ae2b89fb1118b1afcaff4c4dd67c4a0c56f060` |

The [capture provenance](design/native-gallery-header-h1-v1/provenance.json),
[candidate build identity](development/2026-11-16-heading-title-continuation/reports/h1-candidate-build-identity.json)
and [repair qualification](development/2026-11-16-heading-title-continuation/reports/replay-load-link-repair-qualification.json)
bind these observations. A later main-only repair does not turn an older capture
into a new executable's capture. Preserve each source-bound record and add a
supplement for new inputs. Concurrent comparator, fixture and contract versions
require their own reconciliation; do not silently substitute one into another's
frozen acceptance history.

## Original integration failures and their separate resolutions

The original [240-test log](development/2026-11-16-heading-title-continuation/reports/h1-final-ctest.log)
and [coherent-input receipt](development/2026-11-16-heading-title-continuation/reports/h1-final-coherent-inputs.json)
retain **237 passes / three failures in 561.57 seconds**. Do not relabel that run.

| Original failure | Correction and executed evidence |
| --- | --- |
| Workspace replay omitted an actual old-size Flat frame before resizing. | The [independent diagnosis](reviews/WORKSPACE_PAINT_REPLAY_DIAGNOSIS.md) admits eager continuation only when workspace, presentation and overlay already match the last real paint. Dimensions remain excluded, preserving resize-only throughput. The new six-action regression fails against the genuine original app and passes both rebuilt variants. The unchanged workspace, maximum 256-resize and input-replay gates pass 3/3. |
| Starter Load rejected a complete edited snapshot observed after the nominal Load timestamp with Load already queued. | The [independent protocol clarification](reviews/STARTER_LOAD_OBSERVATION_DIAGNOSIS.md) replaces two unsupported observation assumptions with strict actual copied startup → edit → restoration order and advancing applied sequences. It preserves startup <750 ms, restoration ≥2200 ms, every action, full controls and all file checks. The original checker reproduces both retained failures; the corrected checker accepts both actual histories. The complete corrected fixture passes against the preserved original app: eight methods, four standalone processes and two CLI processes, including the formerly unreached file-tail assertions. |
| Six relative links in a frozen archived proposal lacked their original context. | Root restored exact source copies at the referenced relative paths. The proposal bytes and checker are unchanged; [context receipt](development/2026-11-16-heading-title-continuation/reports/archived-proposal-link-context.json) and [integrity requalification](development/2026-11-16-heading-title-continuation/reports/archive-link-integrity-requalification.json) retain the repair. |

The [combined repair receipt](development/2026-11-16-heading-title-continuation/reports/replay-load-link-repair-qualification.json)
links the individual before/after reports. These are targeted results, followed
by the combined integration gate in root's current checkpoint. The Load review
explicitly supersedes the original stronger “before Ctrl+O” observation claim;
it does not prove the callback's exact application timestamp. A pending later
submission cannot replace an actual complete applied edited state.

Retain the other original outcomes as well: rejected T3 geometry, the initial H1
fixture/checker failures and reviewed corrections, and the field-only early return
that hid grain at scale 0.1. The
[installed journeys](reviews/HEADING_HEADER_INSTALLED_JOURNEYS.md) retain a failed
600 ms canonical smoke and a separately passing 2000 ms diagnostic; they do not
claim the original six journeys all passed. The
[renderer-race review](reviews/RENDER_RACE_COMPLETION_REVIEW.md) preserves the
original 15-second completion timeout, unchanged workload and reviewed 45-second
guard. Local ASan/UBSan execution with leak checking disabled for its documented
runtime limitation is not hosted leak-check qualification.

## Setup and operation

Normal clean-checkout desktop setup belongs in [README](../README.md),
[the source build guide](PRESET_RUNBOOK.md#build-from-source) and the
[native operating guide](INTERFACE_RUNBOOK.md). Keep physical audio/video drivers
for ordinary use. The following is the existing headless recovery configuration,
not a substitute for a desktop or hardware journey.

| Recovery item | Existing configuration |
| --- | --- |
| Writable checkout | `/workspace/scratch/5a28c3564dbf/Hammond-B3-Organ` |
| Coordinated build | `../build-native`, Release, C++20, GCC/Unix Makefiles |
| CMake/CTest | `/workspace/scratch/3edffb787db3/build-tools/cmake/data/bin` |
| Read-only SDL dependency | `/workspace/scratch/3edffb787db3/SDL2`, SDL 2.32.10, commit `5d249570393f7a37e037abf22cd6012a4cc56a71` |
| CMake cache | `BUILD_TESTING=ON`, `HAMMOND_BUILD_STANDALONE=ON`, `HAMMOND_BUILD_VST3=OFF`, `HAMMOND_ENABLE_MIDI=OFF`, `HAMMOND_ENABLE_SANITIZERS=OFF`, `HAMMOND_SDL2_ROOT` set to the dependency above |
| Native qualification | SDL dummy audio/video and software renderer; no physical display, MIDI device or audio device established |

After root confirms no other native/capture/comparison owner is active, these
commands recover the existing build from the repository root:

```sh
/workspace/scratch/3edffb787db3/build-tools/cmake/data/bin/cmake -S . -B ../build-native
/workspace/scratch/3edffb787db3/build-tools/cmake/data/bin/cmake --build ../build-native --parallel 2
/workspace/scratch/3edffb787db3/build-tools/cmake/data/bin/ctest --test-dir ../build-native --parallel 2 --output-on-failure --no-tests=error
```

Preserve each new run under a new report/log name and bind its source, dependency,
configuration and executable identities. Inspect the actual cache before reuse.
If a borrowed dependency or tool disappears, recover the pinned prerequisite
through the clean-checkout guide; do not call a reconstructed binary an original.
Do not clone or rebuild extra trees without a concrete configuration need.

For operation, use `hammond_standalone --help`, then choose a writable state path.
Save is explicit; shutdown does not save. F4/F5/F6 select Play/Rotary/Service;
F7 toggles Flat. Ctrl+S saves, Ctrl+O loads, Ctrl+, opens Audio and Ctrl+M opens
MIDI. The [operating guide](INTERFACE_RUNBOOK.md) defines focus, held-note
ownership, pending values and platform-specific executable paths. Rotary and
Service descriptions preserve the distinction between available software facts
and models not integrated into live sound.

## Whole-project dependencies that remain

All exact [milestone exits](PLAN.md#milestones-and-exit-evidence) remain binding.
The current interface work advances bounded M9 delivery and inspection. It
does not close the following engineering and physical dependencies.

| Milestone | Recoverable state and next dependency |
| --- | --- |
| **M0 — reference/contracts** | Preserve the unchanged atlas, profile/evidence classes, rights and unknowns. Identify the actual organ serial, AO-28 revision, condition and cabinet specimen before measured claims. |
| **M1 — skeleton** | Keep the framework-independent prepared graph, bounded events, offline render and lifecycle/error qualification. Callback deadlines and platform lifetimes require their own observations. |
| **M2 — shared generator** | Preserve 91 shared free-running sources and verified routing identities. Measured pickup waves, levels, phases, production gear relationships and leakage still need evidence. |
| **M3 — console** | Preserve four banks, presets, pedals, percussion, expression and note ownership. Recover contact/audio owners before full-organ capacity, causal scheduling or Engine integration; acquire contact/tap-loading and circuit evidence. |
| **M4 — scanner** | Preserve the original G5 same-Hz failure and the separate ScannerLineFoh gates. Resolve revision-specific loaded connectivity and acquire actual scanner captures before live integration. |
| **M5 — AO-28** | Independently trace a complete loaded graph with transformer data and operating points; validate dry G–G output before cabinet fitting. Component placement prose is not a complete netlist. |
| **M6 — Leslie electronics** | Keep Leslie 122 and 147 profiles separate, with explicit differential ports, crossover and driver loading. Acquire identified cabinet/driver impedances and electrical measurements. |
| **M7 — rotary acoustics** | Preserve one trajectory per horn/drum and explicit effect ownership. R4 acceptance remains with its owner; R5 audible policy and R6 runtime integration are separate from numerical propagation. |
| **M8 — calibration** | Acquire immutable raw captures, uncertainty and held-out groups under the [acquisition plan](CALIBRATION_NEXT_ACQUISITION.md). Synthetic audio or schema passes cannot supply physical measurements. |
| **M9 — product/release** | Complete actual platform/host/device journeys, callback deadlines/retirement, native accessibility, rights and signed packaging. Literal whole-interface 1:1 remains unmet and unwaived. |

Across all work preserve **47 parameter IDs, `B3CONTROLS4` and readers 1–3,
plugin UUIDs, 91 continuously running shared sources, four banks, 147 playing
keys, 24 presets and 68 ordinary controls including presets**. The playable
Engine remains **nominal and dry**. Scanner, complete AO-28 and Leslie research
has not become a live audio route. Presentation changes cannot change musical
state, source clocks, note ownership or routing. The three additive schema-3
UI-observation members require accommodation by external exact-key diagnostic
consumers; saved-control formats remain unchanged. See the
[compatibility review](reviews/HEADING_HEADER_COMPATIBILITY_REVIEW.md) and
later source supplements in the checkpoint.

## Next work and durable completion

The complete published `03c70c1` matrix remains **14 successes and two
failures**, including Windows C4702 and the Intel preset-raster timeout.
The [independent Intel review](development/2026-11-16-heading-title-continuation/reports/a52-repair-core-hosted/intel-standalone-independent-review.json)
is complete, and [root's publication admission](development/2026-11-16-heading-title-continuation/reports/helper-publication-admission.json)
permits publishing only the separately reviewed, locally qualified two-file
Windows helper correction with complete evidence and current documentation.
Preserve the normal preset **30-second guard**, all **256 paints/272 readbacks**,
every assertion and the original failed result. The timeout provides no
completed counters or measured remaining runtime; no timing fix or specific
cause is claimed. A later pass would be a separate source/runner observation,
not proof of repaired cause or repeated stability.

Root must check the exact staged repository and strict worker records, publish
with a fresh expected remote head and no force, independently verify the exact
commit/tree/parent/contents, and release the same A52 Core, A53 standalone and
A54 VST3 reviewers for **all sixteen new-source families**. The next helper
publication and its CI remain pending; do not invent a SHA or transfer earlier
passes. Preserve both earlier Windows failures, the Intel failure and its
skipped post-acceptance/package steps, and the original sanitizer cancellation.
Keep both helper specializations and do not claim a new helper-absent runtime
run. Wait for all next-source jobs before another same-ref push, because
workflow concurrency cancels older runs. All 60 deliveries and strict record
closure remain complete; follow-ups add no worker credit. Root then commits
and pushes accepted final evidence, README/current-plan/status/handoff and
concrete next actions, and verifies remote contents. No local test or CI retry,
aggregate-only rerun, timeout/oracle change or broader source repair is admitted.

After that delivery, recover existing UI owners before choosing the next
reference slice. Remaining differences include wood illumination, bevels and
shadows, key/cap surfaces, small labels and title face density. Freeze reference
regions, support, genuine baseline, numerical criteria and full-frame review
before implementing another slice. Preserve truthful control counts and
unconnected-model labels despite inaccuracies in generated reference art.
Real display/DPI/input and native accessibility journeys remain necessary.
Use [NEXT_STEPS](NEXT_STEPS.md) for the currently assigned dependency-ready work.

Validate this session's records from the repository root:

```sh
python3 -B docs/development/2026-11-16-heading-title-continuation/check_session.py
python3 -B docs/development/2026-11-16-heading-title-continuation/check_session.py --strict
```

This checker has no `--repo` option. Strict closure requires all sixty actual
accepted notes in ten complete six-worker waves. It validates records, not
external dispatch, fidelity, product quality, execution or publication. Use only
this session's actual workers; follow-ups and other sessions create no credit.

Keep one coordinated build, bounded native children and concise console output.
The last root checkpoint retained about 50 GiB free; inspect actual disk use
before large work. Preserve original reports, failures, captures and genuine
baseline directories, including `../t3-native` and
`../h1-replay-before-native`. Store reproducible temporary work outside the source
tree, retain compact provenance and commit accepted durable work. Clean only
owned reproducible intermediates when needed, after checking recovery evidence;
never delete another owner's checkout, index, build or originals. A future
agent should be able to identify what exists, what was tested, what failed,
what remains and the next concrete command without reconstructing this chat.
