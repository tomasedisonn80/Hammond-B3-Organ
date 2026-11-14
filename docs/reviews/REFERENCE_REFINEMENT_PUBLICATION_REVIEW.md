# Reference-refinement publication review

**A59 — independent preflight, 14 November 2026.** The inspected candidate
preserves the accepted product sources, original evidence and concurrent
ownership. Publication is still conditional on the remaining actual acceptances,
the current-navigation corrections listed below, root's final two gates and a
fresh guarded remote update. This is an initial closing-candidate review, not
a staged-tree acceptance, strict-completion result or publication receipt.

The [retained snapshot](../development/2026-11-14-reference-refinement/reports/A59-publication-preflight.json)
was captured from **22:49:18.778687 to 22:49:20.221045 UTC**. Its
[read-only inventory script](../development/2026-11-14-reference-refinement/reports/A59-publication-snapshot.py)
reads Git metadata, file bytes and bounded storage inventories; it runs neither
CTest nor a session checker. All 2,335 observed input files, Git status and HEAD
were unchanged during that interval. This was an observed stable interval, not
an exclusive whole-repository freeze. This review, A59's note and the snapshot
output itself were written afterward and are outside its candidate digest.

## Exact source and publication boundary

| Identity | Observed boundary |
| --- | --- |
| Local HEAD and cached `origin/main` | `0881d1f4c5a26ce9c75dda7a3adde46382e5ab6b` |
| Published tree / current index basis | `f8144b771cda1264a8788f8297f5bfec999f4a08` |
| Actual HEAD parent | `26ff2fbe66a50260bd7601cbfa54c1f5d35ff3a8` |
| Index | **No staged changes**; it still contains the HEAD tree. |
| Candidate | 147 files: 18 modified tracked paths and 129 untracked paths; 8,027,799 bytes of current file contents, not patch size. |
| Candidate inventory SHA-256 | `1824b5b7131143fcd88902df318a7146487ded61b94a2fb56178f2669fb56e0d` |
| Remote freshness | No A59 network query or remote mutation. The cached ref and historical receipts cannot serve as the final fresh expected-head observation. |

The [header publication receipt](../development/2026-11-14-reference-refinement/reports/root-header-publication.json)
records the prior expected-head, `force=false`, exact-tree, fetched-parent and
index verification. The [native receipt](../development/2026-11-14-reference-refinement/reports/root-native-publication.json)
retains the earlier `2e161dc` publication and original Windows failure. The
[concurrent integration receipt](../development/2026-11-14-reference-refinement/reports/root-concurrent-integration.json)
retains the 18 incoming documentation paths at `26ff2fbe` and preservation of
the then-dirty header/material inputs. Their different outcomes and times must
remain distinct.

The earlier `d2972a5744c63219f785e118055b7992656cf8b3`,
`e4968b2acd37b6f79683704356350070fe2fc329`,
`2e161dc3a60fc3442051799574feed37bffbfc5c` and
`f9c11a498ecd88886349415205fc5dccc627033e` commit objects remain locally
available, as do `26ff2fbe` and `0881d1f4`. Object availability is not a new
remote observation or a substitute for the retained publication receipts.

## What actually changes, and who owns it

The JSON inventory names every candidate path, its size, SHA-256, tracked status,
category and recorded worker state where its filename identifies an assignment.
Every candidate path belongs to the four categories below; no unclassified
file, deletion or nonregular candidate appeared.

| Category | Files | Content and acceptance boundary |
| --- | ---: | --- |
| Workflow | 1 | A55's accepted six-line addition to `.github/workflows/ci.yml`, requiring the strict refinement checker in Linux Release. Removing those bytes restores the published workflow exactly. |
| Documentation | 19 | Thirteen changed existing documents and six new reviews. These cover current UI/setup, full-plan navigation, source-specific release/hosted limits, R2/R3 documentation, completion semantics and A57's still-running R4 design review. |
| Refinement records | 86 | Root's four tracking/navigation files, A43–A58 notes and reports, the header receipt and this inventory script. Presence on disk alone does not admit a worker's files. |
| V4 gallery | 41 | A46's accepted native captures, replay inputs, diagnostics, provenance, manifest and README, admitted independently by A50. |

The 18 modified tracked paths are the workflow; `AGENTS.md`; `README.md`;
`docs/DEVELOPMENT_LOG.md`, `INTERFACE_RUNBOOK.md`, `NEXT_STEPS.md`, `PLAN.md`,
`PROJECT_GUIDE.md`, `REFERENCE_REFINEMENT_HANDOFF.md`, `RELEASE_READINESS.md`,
`ROTARY_MOTION.md`, `ROTARY_PROPAGATION.md`, `ROTARY_SCOPE.md`, `STATUS.md`;
and this session's `CHECKPOINT.md`, `CONCURRENT_HANDOFF.md`, `README.md` and
`assignments.json`. None is native product, native test, asset or build-input
implementation. The remaining 129 paths are listed individually in the report.

Content ownership is substantive. A47/A58 own the accepted current README/UI
evidence changes; A48 owns the standing/session navigation layer; A52 owns
plan/project navigation; A54/root own status, next actions, log and setup;
A45/A58 own release wording; A43/A44 own earlier hosted and rotary-policy
documentation; A50/A51/A53/A56 own their independent reviews. Root controls the
live manifest/checkpoint and all staging. A57's new
`ROTARY_RENDERER_IMPLEMENTATION_READINESS.md`, note and two reports were present
but **running** at this snapshot. They define implementation preconditions and
claim no new R4 code or runtime result. A60 was actually dispatched and running,
but had no candidate payload in this snapshot. A59's script was present while
this review and note were still being prepared. Root must review actual final
artifacts instead of blanket-staging all untracked files.

### Product, workflow and test evidence are different boundaries

All **365 non-workflow product/test/asset/data/build inputs** named by A56 match
both its retained SHA-256 records and the `0881d1f4` Git blobs. Their inventory
digest is `dc36f0de8231827ba5b11aa34cf7f3d3187d21d0d8d372660010c35297b7fd31`.
The standalone and VST3 workflows are unchanged. The modified CI workflow is
6,385 bytes with SHA-256
`7ab2a791b0c4b9a0c1b04127b4159f2565e088ffedff0591c875ff538361b536`.
Its strict invocation retains `pipefail` and the existing failure-artifact
policy; [A55](../development/2026-11-14-reference-refinement/notes/A55-strict-ci-gate.md)
owns its focused structure/transport evidence.

[A49](../development/2026-11-14-reference-refinement/notes/A49-coherent-final-build.md)
already records one 157/157 full local run and its exact 2,625-file freeze.
[A56](REFERENCE_REFINEMENT_HEADER_HOSTED.md) already records all twelve passing
primary hosted jobs at `0881d1f4`. These observations support their named source
and configuration. The 368-file A49 product/control inventory included three
workflows; the current source comparison deliberately excludes those workflows
and checks them separately. Later Markdown, records and the additive strict CI
step do not inherit A49's frozen documentation identity or the old head's
execution of a step that did not yet exist. No broad product rerun was needed
for this static preflight, and none was performed.

## Accounting and preservation

The snapshot manifest is 34,813 bytes, SHA-256
`5b2de99bb0b157fd54a6dddc42bb8080f8b139672aad08ee58ec12b4c404d992`.
It records **60 distinct actual identities, 57 accepted and three running**:
A57, A59 and A60. Every accepted note matches its declared digest. These are
as-of declarations inspected directly; no strict or progress checker ran, and
this review does not independently authenticate external dispatch or substantive
acceptance. A53's older 54-record/51-accepted observation remains its unchanged
historical snapshot. Sixty dispatched records are not sixty accepted results.

Direct comparisons preserve the following evidence:

| Protected set | Observed check |
| --- | --- |
| Other development sessions | All 1,208 tracked files match published blobs, including the separate waveform ledger and its retained baseline. |
| Already-published refinement notes/reports | All 311 files match published blobs. |
| Published examples and earlier galleries | All 298 files match published blobs; the accepted earlier v1/v2/v3 bytes remain historical. |
| Original reference | The supplied PDF, original reference JPEG and their two retained provenance records match published blobs. |
| A49 original run bundle | All 15 manifest payloads match; all three gzip streams also expand to the exact recorded 1,571,928-byte original inventories. |
| A50 retained inputs | All 11 retained evidence identities match. |
| A56 historical evidence | All eight named original failure/cancellation records match, along with its three retained audit payloads. |
| A58 protected release evidence | All seven identities match. |

The preserved records retain the original motion-underflow failures, material
regression and both timing observations; the old 154/155 run and separate 1/1
repair; inherited CTest failure file; A27 local LSan EPERM failure; original
`2e161dc` Windows 135/136 failure; incomplete/cancelled f9c matrix; and 26ff's
distinct pre-header result. The named core quarantine leak exception remains
visible. A later success cannot erase any of those outcomes.

Eight focused document-section comparisons also pass: historical AGENTS body;
waveform prefixes and historical suffixes in STATUS/NEXT_STEPS; the complete
older development-log body; README's waveform prefix; and both historical
release assessments. Root should append a new dated closure entry and refresh
current navigation while retaining those protected historical bytes.

## Bounded binary and storage inventory

| Binary addition | Count | Bytes |
| --- | ---: | ---: |
| Actual v4 PNG captures | 8 | 2,722,450 |
| A49 lossless gzip input snapshots | 3 | 1,285,052 |
| Total | **11** | **4,007,502** |

All eleven binary SHA-256 values are distinct. The v4 gallery has 41 files and
2,948,483 bytes; all 39 payload hashes and the exact manifest/provenance/README
identities match A50. No candidate executable, object/archive, generated build
tree, raw BMP, WAV or raw-audio duplicate was found. Ten ignored Python bytecode
files total 455,370 bytes and remain outside the candidate. This is not a claim
that the workspace contains no legitimate external build products.

The bounded `du -sb` observation reports apparent sizes of 149,669,333 bytes
for this repository, including Git storage; 75,138,036 for the existing native
build; 47,377,127 for the desktop build; 87,464,415 for SDL2; 1,538,259 for
RtMidi; 11,001,622 for the native sysroot; and 76,910,324 for build tools.
Free space was 61,679,587,328 bytes. A59 created no build/dependency tree,
removed no evidence and did not visit the other session's checkout. The two
existing build trees and shared dependencies are not publication payloads.

Root reported preparing eleven immutable Git blobs with the same binary byte
budget. That is object preparation only. A59 neither observed a remote object
creation nor changed a branch or index, and no publication follows merely from
the existence of those blobs. Root must bind their final hashes to the exact
accepted tree before updating `main`.

## Concrete blockers and exact resolution

These findings belong to the snapshot above. A later root reconciliation may
close them without changing this historical review.

| Blocker at this snapshot | Required resolution |
| --- | --- |
| A57/A59/A60 still running | Finish and substantively accept their actual notes/reports, record exact note hashes and results, and retain all sixty distinct identities. This A59 task delivers its review now; its note does not require its own acceptance or future publication to exist. |
| Current STATUS/setup wording is stale | Replace current “wave 9”/A55–A60 future-work language with actual completed/current state. Replace metadata-only/pending-A56 language in STATUS and `REFERENCE_REFINEMENT_HANDOFF.md` with accepted A56's exact-source primary matrix and named leak exception. |
| Current NEXT_STEPS/session pointers are stale | Replace the request to dispatch A55–A60 and pending primary audit in NEXT_STEPS; replace CHECKPOINT's old “continue A46–A60”/“A49 owns” future commands with observed outcomes and the real next owner. Update the session entry's instruction to await `0881` primary logs and its A46/A47 ownership-only gallery row to accepted A46/A50/A56 evidence. Preserve dated log entries and every independent product gate. |
| Final records lack final gate evidence | After the stable final records exist, root alone executes the affected repository-integrity gate and strict refinement checker, retaining stdout, exits and final manifest/note identities. A49's older Markdown pass and A53's progress result do not close this. |
| No final candidate tree or fresh remote observation | Root inspects/stages only accepted paths, records the staged tree, obtains a fresh remote head, reconciles any incoming changes and qualifies affected claims before publication. |
| New strict CI step unexecuted at final source | After publication, observe the actual final commit's required workflow jobs and Linux strict step, including exact retained JSON. A dispatch, skipped/cancelled job, artifact filename or prior 0881 pass is insufficient. |

The intended root-only final gates, from the repository root after all final
notes and shared documents are present, are:

```sh
../build-tools/cmake/data/bin/ctest --test-dir ../build-native -C Release \
  --output-on-failure --no-tests=error -R '^python_test_repository_integrity$'
python3 tools/check_refinement_session.py --repo . --json
```

Coordinate ownership of the existing build tree and preserve pipeline failures
if outputs are retained through `tee`. Require sixty accepted/verified notes,
ten complete waves and zero strict errors. Bind these outputs to the final
records; do not edit accepted notes afterward without rehashing and reconciling
the affected gate. Neither command was executed by A59.

### Expected-head, non-force publication checks

1. Read/fetch the actual current remote `main` immediately before final tree
   preparation and inspect any advancement from `0881d1f4`, especially the
   independent waveform session. Preserve both sessions and all unfinished
   files. If the expected parent changes, rebuild the candidate from the newly
   integrated tree and recheck affected evidence rather than relying on cached
   `origin/main` or overwriting concurrent work.
2. Compare the exact staged paths/modes and blob identities with the accepted
   candidate, including all eleven binaries. Record the staged tree hash and
   intended parent. Require the three existing workflow files to contain only
   the reviewed CI delta unless another accepted change is separately explained.
3. Through the established connected Git-data method, create the exact
   blobs/tree/commit. Verify the created tree equals the local staged tree and
   the commit names the intended freshly observed parent. Re-observe `main`
   before the ref update, require it still equals that expected old head, and
   update with the connector's expected-head guard and **`force=false`**.
   A non-fast-forward rejection or changed expected head requires inspection
   and integration, not a forced retry.
4. Independently fetch/read the resulting remote ref and require the intended
   commit, tree and parent. Verify the index still matches the published tree
   before root advances local `main` with the expected old local ref. Recheck
   that remaining worker/unrelated files retain their bytes; do not use a
   destructive reset to make the checkout appear clean.
5. Retain the publication receipt and the final head's observed hosted outcome.
   Confirm that the new strict step actually ran successfully and produced the
   expected complete JSON. Keep all failures, cancellations and nonexecution
   distinct. Publication and hosted acceptance are separately observed events.

The complete M0–M9 plan, nominal dry Engine, 47 parameters, state4/readers 1–3,
scanner G5 failure, separate R4/R5/R6 gates, actual-device/DAW/accessibility/
deadline/signing/rights work and unmet literal 1:1 visual/physical fidelity
remain visible. They are product boundaries, not reasons to invent broader
results or to recount the concurrent session's workers.
