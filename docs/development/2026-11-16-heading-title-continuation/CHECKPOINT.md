# Original hosted results complete; successor ready for publication — 17 November 2026

All **60 distinct workers were dispatched in ten waves of six;
60 deliveries are accepted**.
All ten waves have six accepted deliveries.
Follow-ups retain their original worker identities and create no additional credit.
The [executed strict record check](reports/sixty-worker-strict.json)
passes with zero pending workers/errors; it verifies record consistency only.
Accepted notes and original hosted reports remain frozen. Follow-up qualifications
use separate receipts.

The [verified source publication](reports/source-publication.json) is
`fba1911259346bfc6fd3ba7ec78b5cf6c4d1a6b2`, tree
`b62f212300d75633346ab8fc5ffdd722255fe00a`, with parents
`9d60dbf462a90fe422fd4e69757fe202264acb7c` and
`835755a9069c25ce55bc2c231547458b4b3ffce4`. The guarded, nonforced
update and independent API/Git verification preserve both histories and verify
the exact contents. This published tree equals local authored merge `07aafd218…`.

All sixteen original job families are terminal at that exact source, attempt 1:
[14 successes, one failure and one cancellation](reports/source-ci-complete.json).

| Workflow | Original source-specific result |
| --- | --- |
| [Core CI](reports/a52-core-hosted.json), run `44016021552` | **6/6 successful**: four platform Release jobs and Linux ASan/UBSan/leaks each pass 202/202; full R4 qualification also passes. |
| [Native VST3](reports/a54-vst3-hosted.json), run `44016021543` | **4/4 successful**, 29 CTests across the jobs; each actual module validator passes 47/47, with installation and packaging checked. |
| [Native standalone](reports/source-ci-complete.json), run `44016021554` | Four normal jobs pass **68/68 each**: Linux MIDI OFF/ON and both macOS architectures. Windows fails fixture compilation under `/W4 /WX`; the Linux sanitizer job is cancelled after **30 of 34 selected tests pass**. |

The standalone cancellation occurred during preset raster, leaving it and three
later tests incomplete. No sanitizer finding or originating cancellation cause
is established. It is not a successful sanitizer gate. Original logs, failures
and cancelled/unreached work remain retained.

The [independently reviewed Windows fixture correction](../../reviews/HEADER_MATERIAL_WINDOWS_PORTABILITY_CONFORMANCE.md)
is [locally qualified](reports/windows-header-local-qualification.json):
two explicit float casts plus one active fixture-hash literal across two files.
Both affected CTests pass **2/2 in 43.593519385 seconds**. The Linux fixture
binary, all 48 case descriptions and default 10,542-check/163-painting result
are identical. All **103/103** canonical criteria pass; complete statistics
differ only in the two source identity values, with unchanged canonical pixels.
At this Windows-only stage, **473 of 475 qualified code inputs are unchanged**.
Production app `1fa2a247…`, painter, workloads, criteria and historical comparators
are unchanged. This is local equivalence evidence; successor MSVC compilation
and hosted acceptance remain pending.

Root [implemented the separately admitted sanitizer job budget](reports/native-sanitizer-job-budget-implementation.json):
only `jobs.native-sanitizers.timeout-minutes` changes **20 → 35 minutes**.
Every other workflow byte, all 34 selected tests, 31 build inputs, individual
test/child limits, workloads, instrumentation and leak policies are unchanged.
The final successor changes only the Windows fixture pair and workflow scalar:
**exactly three of 475 inputs change; 472 remain unchanged**. Production
sources and app `1fa2a247…` are unchanged. The observed prefix plus existing
tail-limit envelope is 1,823.666679 seconds; this supports the job allowance
without proving what caused the original cancellation. Successor publication
and all exact-source hosted results remain pending; no successor SHA is recorded.

The Windows fixture source is
`96149cf482ad0a57512257a519b89198113f21b06c33b073b2861e13349d1809`;
its active statistics test is
`5f876087a4fea18acc46db16d4c1e7dba3a50e83d322ee6d835d16dd01e31e4f`.
The unchanged Linux fixture executable is `5dca7e7d…`; historical comparator
pins and original sources/binary in `../windows-fixture-before-native` remain
preserved. The two-file qualification needs no further local native execution.

The complete local run remains **240/242**, with one unchanged preset diagnostic
and two unchanged one-method MIDI diagnostics passing separately. Its 475 code
inputs were unchanged during that run; later repair-stage counts are distinct.
Production app `1fa2a247…` and the accepted current package/captures remain intact.

## Concrete next sequence

The independently admitted Windows fixture correction and separate sanitizer
job-budget change are implemented and recorded. Root next publishes this
three-input successor with a fresh expected remote head and no force, independently
verifies its commit/tree/parent/contents, and supplies that exact source to the
same A52 Core, A53 standalone and A54 VST3 reviewers. Preserve all original
attempts; prior successes do not qualify the successor automatically. Staffing
and strict record closure are complete. Publish the final evidence and handoff
after all successor jobs finish and are reviewed. No further local aggregate-only
rerun is authorized by these results.

Root retains shared source/build/native/publication ownership. Same-ref workflow
concurrency cancels older runs; after publishing the successor, wait for all
sixteen jobs to finish before another push. Inspect disk use before large work;
preserve all genuine baselines, raw evidence and other owners' files.

## Retained publication and qualification checkpoints

The following dated entries preserve earlier states. Their former pending-work
and staffing counts are historical; this opening owns current recovery.

---

# Windows fixture repair in qualification — 17 November 2026

Main remains the independently verified `fba1911259346bfc6fd3ba7ec78b5cf6c4d1a6b2`.
The original Windows standalone job `133814025240`, run `44016021554` attempt 1,
fails compilation because two conditional integer assignments in the header
fixture trigger MSVC C4244 under `/W4 /WX`. Native tests and packaging are
unreached in that job. The [frozen independent admission](../../reviews/HEADER_MATERIAL_WINDOWS_PORTABILITY.md)
permits exactly two explicit float casts and one active fixture-hash update;
production, CMake/workflows, warning policy, criteria and workload are unchanged.

Root implemented the exact admitted bytes: fixture SHA
`96149cf482ad0a57512257a519b89198113f21b06c33b073b2861e13349d1809`, active
statistics test SHA `5f876087a4fea18acc46db16d4c1e7dba3a50e83d322ee6d835d16dd01e31e4f`.
The [target rebuild](reports/windows-header-fixture-build.json) passes.
The [observed equivalence](reports/windows-header-fixture-equivalence.json)
confirms the original and rebuilt Linux fixture are byte-identical (`5dca7e7d…`),
and all 48 actual `--list` case records match exactly. The other 473 frozen
code inputs and application `1fa2a247…` remain unchanged. Historical comparator
pins and original records remain untouched; old reproduction uses its named
source view. Genuine pre-repair sources/binary remain in
`../windows-fixture-before-native` and are identified in the originals receipt.

Both affected CTests passed serially: **2/2 in 43.593519385 seconds**. The
[complete local qualification](reports/windows-header-local-qualification.json)
confirms the original default result exactly (48 cases, 10,542 checks and 163
paintings) and 103/103 canonical criteria. Every complete statistics field equals
`h1-statistics-after.json` except the two admitted source hashes; canonical
header and RGBA bytes are unchanged. The qualified-final JUnit statistics text
was truncated, so the comparison used the original complete JSON instead.
No further local native execution is needed for this two-file portability fix.

A52–A54 continue all original source-specific hosted reviews. All four original
VST3 jobs are successful, subject to A54's completed report; Linux standalone
MIDI ON passes 68/68, and original Core jobs are still finishing. Preserve every
original outcome before a new push cancels work. Root then publishes only the
reviewed fixture correction and complete evidence, verifies the new source, and
releases the same three reviewers for actual repaired-source outcomes. Worker
follow-ups do not change the count of sixty actual dispatches.

The earlier checkpoint below retains the first source publication and its
initial workflow states. This opening owns the current repair and next action.

---

# Published source; exact-source hosted review active — 17 November 2026

**Main is published at `fba1911259346bfc6fd3ba7ec78b5cf6c4d1a6b2`, tree
`b62f212300d75633346ab8fc5ffdd722255fe00a`.** The guarded, nonforced update
preserves parents `9d60dbf462a90fe422fd4e69757fe202264acb7c` and
`835755a9069c25ce55bc2c231547458b4b3ffce4`. Independent API verification and
Git fetch confirm the ref, exact tree, both parents and all contents. The
[publication receipt](reports/source-publication.json) maps the local authored
merge `07aafd21829c2c006414c05d04b8e93dc4ada5c8` to that same tree. Local main
now follows the provider commit; a backup branch preserves the local merge.
Unfinished hosted work was preserved without a reset.

All **475 qualified code inputs remain unchanged**. The complete local run
remains **240/242** with three separate unchanged isolated passes. Actual staged
archive integrity passes for 1,669 Markdown files and 9,235 local links, and the
progress checker records 60 actual dispatches / 57 accepted notes. Five
integrity/whitespace receipt files were the only additions after that staged
archive check. Original raw logs and frozen evidence retain their exact bytes.

## Current workers and exact-source workflows

| Same worker | Workflow run | Required families | State at release |
| --- | --- | ---: | --- |
| A52 | Core CI `44016021552`, attempt 1 | 6 | In progress |
| A53 | Native standalone `44016021554`, attempt 1 | 6 | Queued |
| A54 | Native VST3 `44016021543`, attempt 1 | 4 | In progress |

The [initial observation](reports/source-ci-initial.json) is not a terminal
qualification. These same workers own actual source/job/log review and their
remaining hosted notes; follow-ups create no additional credit. They may change
only their assigned hosted reports, logs and pending notes. Original preparatory
records are preserved in the [archive](reports/hosted-preparation-archive.json).
Root owns repairs, retries, integration and publication. Report a concrete
failure before proposing a correction; retain all original attempts.

**Do not push another commit while these workflows run:** their configured
concurrency cancels older work on the same ref. Prepare final documentation in
the worktree, then wait for all sixteen job families to finish and be reviewed.
Accept A52–A54 from their actual completed evidence, run the matching strict
sixty-record check, update current README/AGENTS/plan/status/handoff and next
steps, then publish the documentation/evidence closure with a fresh expected
head and no force. Verify the final commit/tree and code equivalence separately.
No whole-interface 1:1, physical, hardware, accessibility or release claim follows
from source publication or staffing closure.

Root's last disk observation was **46.4 GiB free**. The temporary 355 MB staged
source view was removed after its checks. Retain all original baselines,
artifacts, upload manifests and other owners' work. No cleanup is required to
finish the hosted review and documentation.

---

## Retained prepublication checkpoints

The entries below retain their original dated states. Their older pending
publication wording is superseded by the verified publication above.

# Current recovery — qualified-final results and publication, 17 November 2026

This is the current entry. All checkpoints below are retained historical
snapshots; their former pending tasks do not replace this sequence. Recover the
[standing instructions](../../../AGENTS.md), [complete plan](../../PLAN.md),
[handoff](../../HEADING_TITLE_HEADER_HANDOFF.md), [actual ledger](assignments.json)
and [current staffing sequence](NEXT_ASSIGNMENTS.md) before acting.

## Actual staffing and ownership

**60 distinct workers dispatched; 57 accepted deliveries.** Waves 1–8 and all
six wave-10 deliveries are accepted. A49–A51 are accepted in wave 9; only A52
(core), A53 (standalone) and A54 (VST3) await exact-published-source hosted
acceptance. Follow-ups create no new worker credit. Root owns the coordinated
build, shared integration, acceptance and publication in
`/workspace/scratch/5a28c3564dbf/Hammond-B3-Organ`. No other native workload may
overlap root's assigned native qualification work.

## Source and completed local evidence

| Frozen input | SHA-256 |
| --- | --- |
| Current main | `0c02c619bd04e69ed70aa7c50cbb8345cbc41a188619e94ca6b8a56a24547537` |
| Current application | `1fa2a247e6e90379540ad431776241a885b93223430ac3b0798480d58e96a28a` |
| Current standalone CMake | `642655110b803592e0943d6bb1aa367cd74c81d72b6ebef0b3f1058916157a96` |
| Current workspace fixture | `38808674e491c2224a7b425df55f26ac076e3560c302a6319dbff49e5e1d961b` |
| Unchanged H1 painter | `0bf731a692b7cb7c88c200afea86f4ca14239f20a7000f06be484f2a11ebc20d` |

The [qualified-final full run](reports/qualified-final-coherent-results.json)
completed **240/242**, exit 8, in **740.263707625 seconds**. All **475 code inputs
and recorded build inputs remained unchanged**; six serialized tests had
verified nonoverlap. Workspace replay passed with **37 actual native children**,
and Starter Load passed. The two failed CTests were the preset-raster
**30-second timeout** and native MIDI replay, with two missing
acknowledgment-window observations. This is distinct from the earlier
[semantic full run's 240/242](reports/semantic-final-coherent-results.json).

Exactly three bounded, unchanged diagnostics followed. The
[preset-raster diagnostic](reports/preset-raster-one-isolated.json)
passed once in **27.517879209 seconds**, retaining its 30-second limit.
The [two failed MIDI methods](reports/qualified-midi-one-isolated-diagnostics.json)
each passed once in **2.031860108** and **2.037485655 seconds**, with their
nine-second child deadlines and all 475 code inputs unchanged. These separate
passes preserve the original failed full-run outcome; they establish neither
a green 242-test aggregate nor a particular CPU/scheduler cause. Root proceeds
to exact-source hosted qualification with this complete local evidence.

The earlier semantic run also finished 240/242, at different fixture/scheduling
inputs. Preserve its separate receipt. The preset diagnostic retained all
192 label/focus, 160 glyph, 752 isolation and 96 state cases, with zero failures.
The two MIDI diagnostics are the failed CC120 external-division and real-overflow
methods; exact member archives and unchanged nine-second children are retained.
No source/property change or full-suite retry solely for a green aggregate is
authorized by this recovery entry.


The [local publication admission](../../reviews/HEADING_HEADER_LOCAL_PUBLICATION_ADMISSION.md)
accepts the unchanged source for guarded publication with the failed full-run
result and three passing diagnostics retained. Exact-source hosted acceptance
remains pending; this is not a green full-suite aggregate.

The current fixture and scheduling changes have separate
[startup-observation admission](../../reviews/WORKSPACE_STARTUP_OBSERVATION_ADMISSION.md),
[conformance review](../../reviews/WORKSPACE_STARTUP_OBSERVATION_CONFORMANCE.md)
and [Starter Load scheduling admission](../../reviews/STARTER_LOAD_SCHEDULING_ADMISSION.md).
Main and application bytes remain unchanged. Earlier H1, combined, scheduling
and semantic failures retain their own original reports and thresholds.

A55 independently accepted [two fresh actual installed-app captures](../../reviews/FINAL_INSTALLED_CAPTURE_REVIEW.md);
A56 accepted the [fresh relocated 17-file installation and its two recorded journeys](../../reviews/FINAL_NATIVE_INSTALL_REVIEW.md).
Those current `1fa2a247…` results do not relabel the original `bfe8e36d…` H1
gallery or repair the original 600 ms smoke failure. Whole-interface 1:1,
physical/model, hardware/display/DPI, accessibility and release exits remain
unmet or separately pending as specified in the full plan.

## Verified recovery object; branch publication pending

Root verified provider recovery commit
`835755a9069c25ce55bc2c231547458b4b3ffce4`, tree
`9faad3ce95cc0f4a5c0fd4113a08f0b0915ef97c`, parent
`6047723b595259de355c74342e48a8ae2ee1e228`. All **366 blobs / 51,076,715 bytes**
for that recovery tree were uploaded and verified. This preserves the local
`045c95d…` recovery tree; it is not the final current candidate tree.
Root has also uploaded **141 new preflight blobs / 6,399,504 bytes**.
**Main remains `9d60dbf…`; no branch ref has been updated.** Preserve the upload receipt at
`../publication-h1-recovery-upload-state.json` and owned immutable blobs at
`../publication-immutable-blobs`.

Final publication must preserve both concurrent UI-delivery commit
`9d60dbf462a90fe422fd4e69757fe202264acb7c` and recovery commit
`835755a9069c25ce55bc2c231547458b4b3ffce4` as parents. Inspect the fresh remote
before the guarded, nonforced ref update, and reconcile any additional advance.
Verify the exact final tree, parents and intended contents independently.
Recovery-object creation is separate from publishing that final merge.

## Concrete continuation

1. Preserve the qualified-final 240/242 and exactly three passing unchanged
   diagnostics as distinct local evidence. The independent A52/A53 source-specific supplements are complete; source/property changes remain unauthorized.
   Do not rerun the whole suite only to manufacture a green aggregate.
2. Root preserves the admitted source and finishes reviewable documentation,
   then publishes the final merge with both required histories and a fresh
   expected remote head. Verify the resulting commit/tree/parents/contents.
3. Give that exact published source to A52, A53 and A54. Observe all **16 required
   hosted job families**, including the actual sanitizer and platform outcomes.
   Keep failures, cancellations, retries and unrun gates source-specific.
4. Review and accept the remaining three actual deliveries, run this session's
   matching strict checker for all sixty accepted records, then commit and push
   final evidence/documentation closure. Verify that final publication too.

Continue using the existing root-owned `../build-native` and pinned read-only
dependencies from the handoff. About **50 GiB** was free at root's latest
observation; inspect actual space before large work. Preserve original reports,
baselines, captures and every other owner's checkout. No new worker, duplicate
build or cleanup is needed merely to advance the ledger.

---

## Retained checkpoint history

The entries below are preserved unchanged. Read their source identities and
dates as historical evidence; the current entry above owns recovery.

## Current recovery checkpoint — semantic paint qualification

This entry supersedes earlier pending-task statements below. All **60 distinct
workers have actually been dispatched in ten waves of six; 57 deliveries are
accepted**. A52–A54 still own exact-published-source hosted qualification. Their
follow-ups do not add worker credit.

A58 independently admitted a minimal scripted semantic event-drain boundary;
A59 froze its twelve-zero-time-action regression; A60 implemented the reviewed
run-loop change after root's genuine-before execution. Both before children
exited zero but painted only their final view; both rebuilt candidate children
paint all six required views. Original saved controls, musical guards and
A46's resize-marker branch remain unchanged. The unchanged three boundary
CTest selection also passes, including both maximum-256-resize plans.

Current main is `0c02c619bd04e69ed70aa7c50cbb8345cbc41a188619e94ca6b8a56a24547537`;
current application is `1fa2a247e6e90379540ad431776241a885b93223430ac3b0798480d58e96a28a`.
Painter `0bf731a6…` remains unchanged. The independent coverage review verifies
242 discovered tests, all 241 previous commands unchanged, 45 normal hosted
required names and 34 sanitizer gates from 31 targets. CMake adds only the new
regression and A54's separately admitted calibration/MIDI CLI serial properties.

Root is executing the complete **242-test** suite with **475 frozen code
inputs**, two CTest slots, and five explicitly serialized native tests.
The [live original log](reports/semantic-final-ctest.log) currently retains a
starter-Load failure: the copied history has startup at applied sequence1,
partial edits at5, then restored controls at7; complete edited sequence6 is
missing. A48's strict chronology oracle correctly rejects it. A54 is reviewing
this distinct scheduling candidate; root will execute exactly one unchanged
materialized-scopes method after the complete suite ends. No fixture, assertion,
duration or timeout change is admitted. Preserve this full run and all three
previous failed full-suite records.

No other native workload may overlap this run. Root can prepare immutable Git
objects and read-only documentation reviews. Original recovery commit045c95d
and concurrent remote9d60dbf are retained in the pending merge. Some immutable
recovery blobs have been uploaded with provider SHA verification; **no new
branch update or final-source publication is claimed**. Durable scratch upload
receipts are `../publication-h1-recovery-upload-state.json`; source objects are
in the owned `../publication-immutable-blobs`. Never remove originals or another
workspace. About50GiB remains available.

After resolving actual qualification findings, root must refresh current docs,
install to a fresh owned prefix, retain current-source capture provenance,
finish the nonforced merge/publication, observe all sixteen required hosted job
families at that exact source, close the sixty accepted records, and publish the
final evidence/documentation. Whole-interface1:1 and every physical/device/
accessibility/connected-audio milestone exit remain open and unwaived.

# Heading/title and delivery continuation

Started 16 November 2026 from `113c29b7b14c8fde0859bc405ef8e4141a131ea6`. This session owns only the new checkout `/workspace/scratch/5a28c3564dbf/Hammond-B3-Organ`; prior workspaces and originals remain untouched. Root coordinates one native build at `../build-native`.

## Current work

Fresh atlas reading: six distinct workers, PDF ranges 1–84, 85–168, 169–252, 253–336, 337–420, 421–500. Ten staffing waves of six will be dispatched in two groups of three; actual identities and accepted notes are recorded in assignments.json. Full plan exits and standing engineering/UI requirements remain binding.

## Next actions

Finish full atlas/context review, inspect current CI and reference art, freeze bounded next-phase contracts, preserve a genuine baseline, implement and verify accepted changes. Root updates this checkpoint after every wave and before long operations/context resets.

## Wave 1 accepted

A01–A06 completed fresh contiguous textual coverage of all 500 pages, with hashes and individual chapter notes in reports/atlas-reading-coverage.json. Root additionally read source/evidence/UI/acceptance pages and viewed the original/full current image. All six reading deliveries are accepted; no product gate follows from reading.

Wave 2 A07–A09 are dispatched: T2 contract, exact-source CI investigation, protected-input/regression inventory. The baseline coherent build succeeded; full CTest is running. Genuine baseline app, two frame fixtures and paint benchmark are retained at ../baseline-native with reports/baseline-identity.json. No production painter has changed.

## Wave 2 accepted; implementation started

All twelve first-two-wave workers are accepted. T2 contract `e7074c5f` has
independent A10 admission. T3 contract `6e45c095` is proposed and still needs
independent review before its implementation. The read-only session checker now
validates actual progress; `--strict` deliberately refuses incomplete closure.

Baseline full CTest: **234/235 in 300.90 s**. The original failure is
`test_standalone_midi_cli`: observed focus set omitted initial 0, although final
channels/calibration were correct. The exact isolated method then passed at the
same binary. Both original logs are retained. A15 owns diagnosis and a narrow
replay-observation correction; root does not treat a repeat as erasing failure.
The baseline thirteen-view actual application capture passed; originals are
in `../baseline-gallery`, with source/binary identity in the capture records.

Wave 3 current exclusive paths: A13 `InstrumentView.cpp` T2 helper/calls; A14
new independent `tools/compare_heading_typography.py`; A15 `main.cpp` and the
MIDI CLI native test for the observed baseline issue. No root build runs while
these workers edit production inputs. Next assign T3 independent review,
targeted native typography fixtures, and the two admitted legacy heading-oracle
transitions. Preserve all other source/owner boundaries.

## Wave 3 accepted; wave 4 verification

All A01–A18 delivered and were reviewed. T2 painter is `94186192`; T3 contract
`6e45c095` is independently admitted but not implemented. The new 48-case
partial-clip fixture is root-registered; Upper/Lower literal heading oracles
transition narrowly, retaining every other assertion. A15 repaired the
startup UI observation loss with a bounded 512-entry UI-only trace; normal
operation and acknowledged musical observations retain their semantics.

First T2 run: all 110 raster pairs passed individually, but its overall
receipt correctly failed because root regenerated compile_commands.json while
it ran. Retain this invalidated receipt; run the complete extension on stable
inputs after all builds/configuration finish. First focused replay run: real
app MIDI CLI and expression tests passed; separate calibration probe was stale
and is being rebuilt. No final replay or T2 acceptance is claimed yet.

Wave 4 A19 owns comparator extension, A20 independent replay review/overflow
regression, A21 actual T2 full-frame visual admission. Root owns CMake, current
build, frozen-source clip baseline, captures and acceptance. Never start another
build/configure while a provenance-locked comparator is running. Storage 53 GiB
free; original baseline binaries/reports/failure evidence remain preserved.

An environment turn interrupted A19/A21 and temporarily removed live process
handles; root resumed the same A19/A20/A21 assignments without counting new
workers. Rebuilt calibration probe, Upper/Lower raster oracles and all 48 new
clip fixture cases now pass (four CTest targets, 26.75 s). Frozen-source clip
binary and exact commands are retained in reports/frozen-clip-baseline.json.
The original unfinished test log has no outcome; the completed log is distinct.

## T2 accepted; actual pre-T3 checkpoint preserved

Stable complete T2 comparison passed158/158 in104.216s:92 complete model pairs,
74 exact frames,18 reference placement checks,24 partial heading/rule clips,
zero forbidden changes, unchanged inputs and both48-case default fixture runs.
A21 independently admitted all13 actualfullframes and14 lossless crops. The
23-method MIDI CLI suite passed22.83s; retained musical/calibration/expression
gates also pass at the repaired sources. Original failures remain unchanged.

Actual app/threefixtures/benchmark and painter are frozen at ../t2-native before
T3; reports/t3-baseline-identity.json pins229sources, including all213 protected
paths. Only main.cpp differs from the original protectedbaseline, for the
separately admitted replay repair; it must remain identical across T3.

A22 owns distinct headerproposal, A23 independentT3tool, A24 exactT3fivepasses.
Root stages/publishes acceptedT2 while furtherwork continues from this checkpoint.
README now embeds actualT2capture; finalgallery refresh follows the next accepted
stage. Whole-interface1:1 and physical/platform/productgates remain open.

## First publication and T3 rejection retained

AcceptedT2/replaycheckpoint is published on main as6047723b595259de355c74342e48a8ae2ee1e228,
identicaltree8bb162b1d5bd153436649339cf9253eaee5c28eb tolocal91914c65690b1451f075a66231737da1b7326b97.
Independentref/parent/full225changed-entryverification passed. See t2-publication
and t2-local-alignment reports. LocalHEAD nowfollows publishedcommit; allT3
worktreechanges arepreserved and localauthoredT2commit has itsownbranch.
Exactsource CI runs43986430633/core,43986430649/standalone,43986430625/VST3
were observedqueued; no passclaim.

OriginalexactT3candidate40de4489 is rejected by unchangednative materialgate:
two1400x820 cases(renderer1and1.25) have warm title top16 versus17.13848 expected,
error1.13848 > maximum1. Canonicaldensity5512 passes4500..6000, but doesnot
overrulegeometry. Originalcandidate source, sixbinaries,13captures andfailedlog
are retained; reports/t3-v1-rejection.json binds them. No full158pairedrun was
spent on analreadyrejectedcandidate. Nextwaveindependentlyproposes/admitsthe
narrow highlight revision; alloriginaldensity/geometry/state/support limitsstay.
A22headerproposalremainsseparate andrequiresacceptedpostT3baselinefirst.

## Wave 4 complete; Wave 5 reviews

All 24 workers in the first four waves are accepted for their scoped deliveries.
Product acceptance remains separate: T2 and the replay repair are accepted and
published; the original T3 painter is rejected and preserved. A22 delivered the
separate H1 proposal and exact reference observations, without painting it.

Wave 5 assigns A25 the narrow T3 revision proposal, A26 its independent review,
and A27 independent H1 protocol/support review. Neither proposal authorizes a
painter edit by itself. Root keeps all existing acceptance thresholds and failed
evidence, then assigns implementation and independent comparison work.


## T3 revision2 accepted; wave6 begins (17 November UTC)

All158 actual paired cases pass, including92 complete-model pairs,213 protected inputs and zero exterior changed pixels. Native1317 material assertions and18/18 density cases pass. Independent A30 visual review admits only title scope; v1 rejection is retained. Whole-interface1:1 remains unmet. A01–A30 are accepted actual workers. Wave6: A31 examines the hosted core sanitizer race timeout; A32 owns the frozen48case H1 fixture; A33 owns the independent103screen comparator. H1 paint has not started. A single unchanged exact-job retry of T2 sanitizer job133715652514 was requested as a diagnostic; original failure remains recorded.


### Wave6 sanitizer diagnostic and baseline recovery

T2 has16 successful latest job families after exactlyone unchanged core sanitizer retry (202/202;312.10s). Original15secondtimeout remains recorded. Local Debug ASan/UBSan reproduced >15s; a separate no-LSan diagnostic reached every unchanged assertion in16.47s. A31 narrowly changes onlypostresume completion guard to45s insideunchanged90sCTestbound. Root changed-suite5/5,45CLIinvocations passesRelease4.253s andlocalASan/UBSan20.095s; localLSan runtime limitation remains, changed-source hostedleakqualification pending. Rootcopied acceptedT3 to../t3-native and recorded h1-baseline-identity.json;18/18primaryRGBpatches exactlyequalT2. IndependentH1fixture/checker stillpreparing; painter notauthorizedyet.


### Pre-H1 genuine baseline and checker correction review

A32corrected an initial stored-versus-visible control inventory assertion beforecandidatework; originalsource/failureare retained. Correctedfixturea6b65d06 builtandpassed10447checks/163paintings/48cases in29.343485s; genuineexecutablec598ff86 and immutableobject/source/libraries copiedinto../t3-native with h1-fixture-baseline-identity.json (82164ea2…). Initialindependentchecker16476f70 fullbaseline runfinished295.712s,137nativecalls,48main+16companions,allpairedRGBAequal,zerooutsidechanges,all213protectedinputsunchanged,and44/59original103screens reproduced. Itfailed its ownutility-IDgeometry expectation plusaNONE-blendapplicationofolderBLEND-onlywarminkROIs. Sourceandcompletefailedreportare retained. A33proposes sourcedoraclecorrections; A27independentlyreviewsbefore rerun. Productionpainterstays10865a6b; H1notstarted. A36captureflagaccepted;15viewgenuinebeforegalleryatdocs/design/native-gallery-header-before-v1 passedandA35independentlyverifiedall69payloads/15decodedframes. A35visualcandidateadmission remainswaiting. Ledger35actualdispatched,33accepted; A34notyetdispatched.


## H1 matrix passed; wave7 permanent coverage

The corrected checker09839856 completed its genuine baseline: all64pairs and4repeats preserved,44/59 original numerical outcomes reproduced. Initial checker rejection remains retained. A34 then implemented only admitted H1; root static review caught one field-only early return that incorrectly skipped21grain marks across9pixels at renderer scale0.1. IndependentA27 admission approved exactlyone75byte deletion; initialsource0385765a is preserved. Currentpainter0bf731a6 builtcoherently. CompleteH1 comparison passed233.244s:48main+16companionpairs,4repeats,103/103numerical screens,10542candidatefixturechecks,95directhelperrestoration probes,1317materialassertions,213protectedpaths andzerooutsidechanges. Currentappbfe8e36d. Final visual/timing/rootacceptance remains pending; actual15view candidatecapture is running. A37owns permanent103screen CI, A38compatibilityaudit, A39tiny-scalegrainregression. Native/CMake integration waits for captures and these frozen handoffs. Ledger39dispatched/35accepted atthischeckpoint.


## H1 visual, timing and permanent regressions — 17 November UTC

A35 admits the scoped H1 visual gate after directly inspecting all fifteen actual candidate frames and reference/before strips. Current app remains bfe8e36d and painter0bf731a6; all original galleries and failures remain intact. Five serial genuine-before/current timing cases completed449.677s: active minimum/canonical/wide median growth4.47%,3.24%,1.26%; all investigation flags false. Absolute software timings and run-to-run variation do not establish hardware FPS or audio deadlines. Compact and Flat pixels are identical. Root final configure/full coherent build and seventeen-file Standalone install all exit0; installed app exactlymatches captured app. A37 permanent numerical regression now executes genuinebefore44/59 andafter103/0 withvalidtransport and expectedhelperdifference. A39 currentfour-case96000-pixel grain regression passes; root is compiling identicalfixture against archived initial H1 to demonstrate the predicted genuinefailure. Fullsuite follows.

A41 installed journeys retain a600ms canonical smoke failure (no note-on/off observations). Five other original journeys match expected success/refusal. A separately authorized2000ms diagnostic passes every unchanged note, held/release, audio and shutdown assertion. No600ms pass or fullsix-run blanketpass is claimed. A40 fullplan/guideaccepted with completeM0–M9 exits preserved; A42README and A43currentstatus/nextsteps/log updates are in progress. Currentledger43dispatched/40accepted; six completeaccepted staffingwaves, wave7pendingA41/A42. Storage52GiBfree.


## Recovery: full-suite diagnosis and wave 8 repairs

48 actual workers dispatched; A01–A45 accepted, A46–A48 active. The first coherent H1 suite completed 237/240 with three retained failures, not a green acceptance: workspace painted-prefix omission, repeatable starter-Load observation predicate, and six archived relative links. Original logs and exact sources remain. Root restored the archived proposal’s link context with byte-identical source copies; the original proposal is unchanged. A44 independently rejected unconditional marker deferral because of the 256-resize contract. A45’s permanent six-action zero-time fixture genuinely failed both original-binary variants solely at the actual painted-view assertion. Root admitted only the selective workspace/presentation/overlay guard to A46, with no dimension gate or changed grace. A47 is finalizing an independent Load protocol clarification; A48 remains unmodified until root reads that review. Original Load fixture saved in inputs/test_standalone_starter_load-before-observation.py. Root owns CMake, rebuilding, before/after runs, all publication and updated acceptance. Next: close these two native issues, run affected then coherent gates, publish accepted source, observe all 16 hosted job families, dispatch and accept A49–A60, and push final recovery records. No whole-interface 1:1, physical-model or hardware qualification is claimed.


## Wave 8 complete; concurrent remote reconciliation

All 48 actual workers in waves 1–8 are accepted; the progress validator passes. A46 main is `361ae03aa9e1a369a8fd8d125c21b10e40841d08d768a4c5637b2a3ecf0232f3`, rebuilt app `2c64e585d8f1da521ff4c4dafe51613dd3aa0692461bfcb8d6450f9ca4971479`. Both new paint cases and all three unchanged workspace/maximum-resize/input-replay tests pass. Archived-link integrity passes. The original Load checker reproduces both retained failures; the corrected checker passes both actual histories, and the full changed fixture passes against the genuine pre-repair app: eight methods, four app processes, two CLI processes, all file-tail assertions executed. Original failures are unchanged. Root discovered and fetched remote `9d60dbf462a90fe422fd4e69757fe202264acb7c`, a direct child of the previously published `6047723`. It contains the separate UI-delivery session, accepted T3 painter and overlapping tool/contract/build advances. Preserve all remote work and original evidence; independently review overlaps before a combined final build/test and guarded publication. Root is committing a local recovery snapshot before reconciliation. Wave 9 will use A49–A54 for this reconciliation, permanent handoff, compatibility and exact-source hosted qualification; no old worker is recounted.


## Combined source frozen; parallel-run diagnostics

54 actual workers are dispatched and A01–A51 accepted. The merge preserves
190 remote-only changed paths and 14 identical overlaps; A49 independently
reviewed the seven differing paths. Current painter, main and app remain
`0bf731…`, `361ae…` and `2c64e…`. Exact remote stronger title validation and
portable comparator interfaces are adopted, with all originally qualified
predecessors archived byte for byte. The current-tree static check correctly
rejects the old protected-main pin. An explicit historical Git source view
(26 files, 3,918,956 bytes) passes static checks without native execution.
The current stronger title gate passes one inventory and 18 frame processes.
A51 admits 44 named normal gates and 33 sanitizer CTests from 31 targets,
with the private MIDI=0 check correctly applied to support. Final workflow
SHA is `b572d1e34d891657964d8ca6f5882fbaf157ab91ddbb309fd183af89fbdfac6e`.

Combined configuration and build pass. Root froze 474 code inputs and started
all 241 CTests with parallelism two. Two completed failures are retained:
native MIDI lacks a fully acknowledged observation in [950,1230) ms, and the
workspace's first loaded-state observation is at 292 ms against its <180 ms
requirement. A53 confirms that this run contains all nine required painted
visits, including the old-size Flat frame; this is a different failure from
the corrected paint omission. No exact CPU or scheduler cause is established.
A52 and A53 independently diagnose the two histories. A54 reviews a narrowly
scoped scheduling correction against the existing serial smoke admission.
No source edits or extra native processes run while this complete suite is
active. These same three workers retain core, standalone and VST3 hosted roles
after verified publication. The combined source is not yet published.
