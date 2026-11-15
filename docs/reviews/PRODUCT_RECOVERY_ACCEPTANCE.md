# Product recovery acceptance — A59

**Decision: accept the revised recovery path for the observed workspace and
retained source identities.** Future agents can find current ownership, exact
setup, accepted and unfinished work, source-qualified evidence and concrete next
gates without private conversation context. This accepts documentation recovery;
the final actual-sixty gate, final publication and hosted qualification remain
root's pending work. The user's literal whole-interface **1:1 objective remains
unmet and unwaived** under [A54](PRODUCT_UI_ACCEPTANCE.md).

Actual worker `/root/w10_a59_recovery_audit`, wave 10, 15 November 2026 UTC.
Scope: [AGENTS.md](../../AGENTS.md), [PRODUCT_HANDOFF.md](../PRODUCT_HANDOFF.md),
this review, a short [note](../development/2026-11-15-product-continuation/notes/A59-recovery-audit.md)
and a bounded [receipt](../development/2026-11-15-product-continuation/reports/A59-recovery-audit.json).
The live [checkpoint](../development/2026-11-15-product-continuation/CHECKPOINT.md)
and [actual manifest](../development/2026-11-15-product-continuation/assignments.json)
own subsequent counts and observations. This review does not freeze another
quickly outdated worker count or accept forthcoming deliveries.

## Recovery basis and exact source

Read full AGENTS and the complete [M0–M9 plan](../PLAN.md), current session entry,
checkpoint and actual assignments, current README/status/next steps/latest log,
A45's recovery note/handoff, A53's documentation reconciliation and A56's
[whole-project readiness](PRODUCT_PHASE_READINESS.md). Relevant current A46,
A47 and A54 contracts/reviews provide the checker, native-lifetime and visual
boundaries. This audits retained atlas reading coverage; it is not a new personal
500-page reading or an acquisition claim.

| Identity checked | Observation and proper recovery meaning |
| --- | --- |
| Local HEAD, HEAD tree, cached origin/main and a live read-only `git ls-remote origin refs/heads/main` | Commit **`d8c39f7986746eacc991747153c7dbb012bb9a32`**, tree **`edf67b978f93e8dbea6537ce92d3928c171bc1f3`**; remote main agrees at A59's query. The [publication receipt](../development/2026-11-15-product-continuation/reports/gallery-publication.json) binds parent `d556da017ea0a5d4f2d231416782dbc5066e58c2`, guarded update and fetched verification. This does not observe a future publication. |
| Working files and index | Read-only status/diff inspection finds the later working overlay and an empty staged diff at the initial observation. Accepted A46/A48 code and later delivered reviews are not inferred to be in d8. Live assignments and each note govern ownership; preserve unfinished files until root selects accepted paths. |
| Published qualification | [d8's receipt](../development/2026-11-15-product-continuation/reports/d8-hosted-status.json) records thirteen completed successful jobs. A59 checks the receipt source/tree and statuses, relying on A49–A52 for primary-log inspection. The [Linux review](PRODUCT_LINUX_HOSTED_REVIEW.md) records actual **21/21 native sanitizer execution**, including the repaired test facade. No new hosted run is claimed. |
| Later coherent local gate | Independently rehashed **all 366 inputs**, three recorded binaries, the cache and original configure/build/CTest logs in [root's coherent receipt](../development/2026-11-15-product-continuation/reports/wave8-coherent-build.json): all match. Its retained **180/180 in 507.55 s** applies to d8 plus A46/A48; this is applicability verification, not repeated test execution or later-source hosted qualification. |
| Native captures | All **108 production inputs** from the [capture build receipt](../development/2026-11-15-product-continuation/reports/capture-qualified-build.json) and application SHA-256 **`7ded143b676e9d51a29549dae12184763042a1f12192f72802db7927fa707852`** match. The eleven admitted frames retain `d556da01` capture identity; the older target-build receipt and later coherent gate are distinct. Original BMP intermediates remain unavailable. |
| Atlas and dependencies | Unchanged atlas: **21,248,265 bytes**, SHA-256 **`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`**. Both dependency helpers pass `--verify-existing` offline at their locked revisions; no new acquisition is asserted. |

**Recovery limit made explicit:** a fresh clone of current d8 cannot recover the
unpublished A46/A48 overlay or later notes. Hashes identify surviving bytes; they
cannot reconstruct lost originals. A future agent needs the surviving workspace,
the assigned owners' retained originals, or root's later verified publication.
If none exists, record the missing work instead of relabeling a d8 checkout as
the later tested source. Do not reset or clean the current index/worktree to
simplify reconciliation.

## Normal setup and workspace setup remain distinct

The handoff's [normal checkout recipe](../PRODUCT_HANDOFF.md#clean-checkout-with-a-normal-toolchain)
uses ordinary CMake/Python commands, separate acquired sibling dependencies,
desktop development prerequisites and MIDI ON for a Linux/macOS single-
configuration build. Windows and multi-configuration paths go to the native
guide. The default core preset remains available without external audio/UI
dependencies. Source inspection confirms the documented options, targets,
minimum versions and preset; shell syntax is checked without configuring or
running those recipes.

The [workspace recipe](../PRODUCT_HANDOFF.md#this-workspaces-recovery-setup)
recovers the existing root-owned build, with these independently observed inputs:

| Input | Exact observed setup |
| --- | --- |
| Source/build ownership | Source `/workspace/scratch/5b7d983ac078/Hammond-B3-Organ`; primary build `/workspace/scratch/5b7d983ac078/build-native`. Only root coordinates configure/build/test/capture. Workers edit assigned source paths. |
| CMake/CTest | `/workspace/scratch/1bb6ee17ad7e/build-tools/cmake/data/bin/cmake` and adjacent `ctest`, both **4.4.5**. No system `cmake` is on PATH at this check. |
| Ninja and compilers | `/workspace/scratch/1bb6ee17ad7e/build-tools/bin/ninja`, **1.13.2.git.kitware.jobserver-pipe-1**; `/usr/bin/cc` and `/usr/bin/c++`, **GCC 14.2.0**. |
| Selected Python | `/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3.12`, **3.12.14**; agrees with the cached `_Python3_EXECUTABLE`. |
| Dependencies | SDL **2.32.10**, commit `5d249570393f7a37e037abf22cd6012a4cc56a71`, at `/workspace/scratch/1bb6ee17ad7e/SDL2`; RtMidi **6.0.0**, commit `1e5b49925aa60065db52de44c366d446a902547b`, at `/workspace/scratch/1bb6ee17ad7e/rtmidi`. Both are borrowed read-only; the existing RtMidi preparation transform belongs only to prepared copies. |
| Cached configuration | Ninja, Release, testing ON, standalone ON, native MIDI backend OFF, VST3 OFF, sanitizers OFF, static SDL; X11/Wayland/ALSA OFF. Cache SHA-256 **`94735cbc53d80045da267e2d1451b92fc2e2a11bb53838f3b1dab2a3b50b2a35`** matches the coherent receipt. Native fixtures use explicit dummy drivers. |

The optional installed-gate recipe is conditioned on root releasing the build
and an affected-input need. It builds selected inputs before CTest and requires
a nonempty selection. A native-only aggregate is not an all-target preparation.
No physical backend or display claim follows from this workspace configuration.
The existing 180-test result need not be repeated for documentary recovery.

## Corrections and preserved boundaries

- Replaced current d556/undelivered-A46 pointers with d8 hosted qualification,
  the distinct later local gate and actual accepted checker commands. Progress
  mode declines closure; strict mode requires all actual acceptances. Final CI
  and publication still belong to root.
- Retained A45's original d556 commit/tree/parent and pending-at-that-time
  observations, ff41's source-bound 176-test result, b9/Windows failures, d556's
  unexecuted sanitizer selection, local ptrace blocks and original A42/A43
  attempts/timings. D8 closes the specific repaired sanitizer build/selection
  gap without rewriting those records or adding a leak exception.
- Preserved every byte from AGENTS' historical-reference-refinement heading
  through the end of the file. Active additions retain the full-plan obligation,
  dependency-ready continuation, authorized commit/push with actual expected-
  head/no-force evidence, setup/status/next/log and actual README UI updates,
  bounded context/storage and separate ownership.
- A56's dated foreign-R4 observation remains attributed: `fd2f6060…`, **151
  staged/four untracked entries** and later local lifecycle/allocation/CLI
  results. A59 does not inspect or operate that checkout/build. Its unpublished
  overlay, integration, publication, final acceptance and ledger stay with that
  owner; a published d8 R4 pass does not decide them.
- Kept **47 sound parameters**, **state4/readers 1–3**, **91 shared free-running
  sources**, nominal dry Engine, scanner G5, R5/R6, physical fidelity, native
  semantics, devices/DAWs, deadlines and release limits explicit. The 1:1
  objective is not reduced to the already accepted scoped raster contract.

## Concrete next work and root closure updates

Root finishes the actual assigned reviews, accepts final note hashes and retains
the strict checker result before switching CI. Then root publishes a coherent
accepted tree, inspects concurrent main, verifies exact commit/tree/parent and
intended bytes after a non-force expected-head update, and observes final-source
hosted execution of the added Python modules and strict record step. Current
handoff/status/next/log/README/checkpoint need their final observed identities;
an evidence-only follow-up identifies its previously tested source. An older
hosted pass cannot fill this pending gate.

After session closure, [A56](PRODUCT_PHASE_READINESS.md) gives two concrete,
independent work orders. M6 first needs a versioned same-Hz electrical protocol
with justified gain floors, V/V magnitude/phase/complex errors and separate A/V
admittance criteria before evaluating a separately identified realization.
Preserve v1 and documentary values. A47-N1 first needs below-RtMidi native-failure
injection with a parked pre-wrapper callback, then checked close preserving
native/dependency/context/inbox storage and poison/no-reopen/no-reset behavior.
Successful close also needs actual platform retirement evidence; the risk model
has not been reproduced as a hardware failure or use-after-free.

A54's identified native-display usability/response journey precedes additional
material work. Any accepted UI change gets new actual captures, independent
comparison and README promotion. Physical acquisition, semantic accessibility,
DAW/device deadlines and signed release have their own prerequisites.

## Bounded verification and resource use

The receipt retains exact commands, hashes, Markdown target/heading checks,
shell-block `bash -n` checks, whitespace/fence checks, history preservation and
the note's 400-word bound. The read-only allocated-size observation is about
**320 MiB** for this workspace, **181 MiB** for the repository, **93 MiB** for
the build and **56 GiB available**. These are dated rounded values; A45's earlier
measurements remain separately labeled. No cleanup or duplicated large artifact
was needed.

A59 performs no configure/build, full or focused runtime test, native launch,
capture, actual-record gate, foreign-checkout operation, index/ref mutation,
commit or push. The accepted review is limited to recovery accuracy and
retained-evidence applicability, with root's remaining closure work explicit.
