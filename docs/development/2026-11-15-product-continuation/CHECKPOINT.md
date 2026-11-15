# Product continuation checkpoint

## Current recovery authority

**All 60 actual workers are accepted in ten logical waves of six.** The
[manifest](assignments.json), [strict local result](reports/product-session-strict.json)
and [integrator dispatch account](reports/integrator-dispatch-reconciliation.json)
retain current-session identities and note hashes. Historical workers and
followups are not counted. At most three workers ran concurrently; dependency-ready
work could overlap wave boundaries. The strict checker validates records, not
external dispatch or semantic acceptance.

The [batch record](../../PRODUCT_CONTINUATION_CLOSURE.md) and
[final requirements audit](../../reviews/PRODUCT_FINAL_REQUIREMENTS_REVIEW.md)
state the remaining original requirement plainly: **literal whole-interface
1:1 reference equality is unmet and unwaived**. Selected M9/M6 work is accepted;
complete physical fidelity, the whole milestones and release are not claimed.

All workers have delivered and released ownership. Root owns the frozen notes,
ledger, shared docs, primary build, publication and final hosted qualification.
The only current integration work is the final publication/CI/evidence sequence
below. Do not invent more worker credit or rewrite historical failed outcomes.

## Source and executed gates

The latest published checkpoint is
**`c4486bafccbcfbcd9bcd9492e8949ddd44ea1340`**, tree
`2d21135e570c5b328a7f54d17582ffc7ac62a489`, parent
`d8c39f7986746eacc991747153c7dbb012bb9a32`.
[The publication receipt](reports/final-source-publication.json) records the
expected-head/nonforced update, exact-tree/blob verification and preserved local
predecessor65e9ea5 under `refs/checkpoints/local-product-final-source`.
All sixty accepted records and the strict CI invocation are published.

Required source runs are **CI43672641490**, **Native standalone43672641506**
and **Native VST343672641501**. At 03:38 UTC, macOS core job132685867386
**failed**: 156/157 CTests pass, with four assertions failing inside the new
`python_test_product_session` module. A51 reproduced those exact four failures
through a private symlinked temporary directory and repaired the fixture's
canonical path. Its original 19 methods then pass for both ordinary and aliased
directories. Windows core job132685867528 separately **failed** 156/157 with
111 assertions (one existing FIFO skip) because the checker compares Windows
path-stat creation time with descriptor-stat change time. A50 owns the narrow
portable reader repair and meaningful regression additions, building on A51's
released fixture change. The published c448 matrix is not fully qualified.
All thirteen c448 jobs have now completed: **eleven success and two failed core
jobs**. Linux core Release/sanitizers, four native Release configurations,
native sanitizers (21/21), R4 and all three VST3 jobs pass their named source.
The [root status receipt](reports/c448-hosted-status.json) retains the complete
failed-matrix observation; it must not be relabeled as overall success.
A49/A50/A51/A52 followups add no worker/wave credit.
The c448 runs are finished, so the reviewed portability repair can be published
without cancelling their evidence. The earlier d8 thirteen-job success
remains historical; it does not qualify this new source by inheritance.

That source includes A46's record checker, A48's report-admission repair,
identical-pixel plot metadata refresh, all notes/reviews and current handoffs.
The strict local check was rerun after root removed four formatting-only EOF
blank lines; the [formatting receipt](reports/final-eof-formatting.json) records
reconstructable before/after identities, and A50's note hash is current.

The [coherent local receipt](reports/wave8-coherent-build.json) records successful
reconfigure/all-target build and **180/180 CTest in 507.55 seconds** over d8 plus
A46/A48. All **366 code/test/build/data hashes** remained unchanged throughout
during that run. The portable checker/test changes now differ in exactly two
of those inputs; all other 364 and all three binaries still match. The
[focused root verification](reports/checker-portability-root-verification.json)
passes the registered affected CTest in 1.31 seconds and current actual strict
records (60 accepted/verified, ten waves, zero errors). Only checker identity
changes in the strict JSON; manifest and note hashes remain unchanged. The
current production binaries are:

- Application: `7ded143b676e9d51a29549dae12184763042a1f12192f72802db7927fa707852`.
- Calibration probe: `16da718ff92bdd940a6e457f100b08b54098dbd4183fd149f9a4b137460b4335`.
- Crossover probe: `da09640f7520cd887a836961658ed8a79d6b6bff28f0e33a0ce44cf76f992eac`.

The unchanged eleven-frame gallery was captured at d556 and independently
admitted; all 108 production inputs match current bytes. README uses those
actual captures. Original BMP intermediates are unavailable after recorded
lossless conversion. Original failures, 277 historical gallery files and earlier
session records retain their identities.

## Immediate next actions

1. The portability code is frozen: checker SHA-256
   `3496024e026abf8732623f16b9ef8ebec392a7636fe64f3f1d6e2efaab89d631`;
   test module `d821b36ebb3b859f7b852c050adc37c65428fc8cc2aae93c2850081323cb1f11`.
   A50's repair passes four reader methods / 30 synthetic subcases and all 23
   current methods locally. A46 independently accepts the narrow repair for
   integration and new hosted qualification. Preserve the exact original
   [c448 strict result](reports/c448-product-session-strict.json), primary failures,
   A51 alias reproduction and A50 metadata reproduction.
2. Finish accepting the bounded A50/A46 followup receipts, stage only their
   agreed paths and the root records, and publish the coherent repair with
   expected head c448 and no force. Fetch and verify exact commit/tree/parent.
   The old runs have finished. New Windows/macOS core success is mandatory;
   observe the entire newly dispatched matrix and strict actual-record step.
3. After all repaired-source outcomes are known, retain the compact root hosted
   receipt and reconcile current README/status/next/log/handoff/plan/checkpoint.
   Identify the replacement revision as the tested source. Earlier results stay
   attached to their own inputs, including the failed c448 matrix.
4. Verify the final evidence diff contains no further code/test/build/workflow
   change before using `[skip ci]` for its publication. Recheck strict records,
   source identities and changed document links. Preserve raw evidence bytes;
   document any exact whitespace-only log exclusions rather than altering them.
5. Publish with a fresh expected head and `force:false`, compare local/remote
   trees, fetch, preserve the same-tree local predecessor and update local main
   with an expected old SHA. Finish with clean local main and matching remote.
6. Report the completed sixty-worker/development batch with the still-unmet,
   unwaived 1:1 UI requirement and concrete next engineering gates. Do not label
   the whole original request or physical/product milestones complete.

## Build, preservation and next engineering task

Only `/workspace/scratch/5b7d983ac078/Hammond-B3-Organ` is writable by this session.
Root exclusively coordinates `/workspace/scratch/5b7d983ac078/build-native`:
GCC 14.2 Release, standalone ON, physical MIDI backend OFF, VST3 OFF; SDL X11,
Wayland and ALSA OFF, explicit dummy drivers. CMake/CTest 4.4.5 are under
`/workspace/scratch/1bb6ee17ad7e/build-tools/cmake/data/bin/`; Ninja is under
`/workspace/scratch/1bb6ee17ad7e/build-tools/bin/`. SDL2.32.10 and RtMidi6.0.0
sources in that workspace are borrowed read-only. The
[recovery handoff](../../PRODUCT_HANDOFF.md) also provides normal clean-clone setup.

The separate R4 checkout `/workspace/scratch/e3cacb90cc81/Hammond-B3-Organ`
retains its owner's staged/untracked progress. Its local results are distinct
from integration/publication/final acceptance; do not replace them with d8's
published full-mode result. About 56 GiB remains free; checkout roughly181 MiB,
primary build93 MiB. No cleanup is needed. Keep bounded evidence and checkpoint
before context changes; preserve all other sessions.

Next development is specified by [A56](../../reviews/PRODUCT_PHASE_READINESS.md):
a declared M6 same-Hz protocol/floors before a separate numerical candidate;
A47's below-RtMidi checked-close/callback-retirement experiment; and A54's native
visual/input gate before the next scoped reference candidate. Preserve scanner
G5's same-Hz failure, 47 parameters, state4/readers1–3, 91 sources, nominal dry
Engine and separate R4/R5/R6/physical/DAW/accessibility/deadline gates.
