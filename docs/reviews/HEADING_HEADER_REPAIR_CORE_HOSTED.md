# Successor Core CI qualification — A52 follow-up

**All six required Core CI families pass on attempt 1 at published commit
`03c70c103a4a0dd72b323529416b909c19a4e139`.** The
[actual run](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44021714612)
is completed/success. Every job acquired a runner and executed; none failed or
was cancelled. This is the same accepted A52 worker, with no additional worker
credit. The accepted note and every original A52 report remain byte-identical.

The [source-bound report](../development/2026-11-16-heading-title-continuation/reports/a52-repair-core-hosted.json)
and [final API observation](../development/2026-11-16-heading-title-continuation/reports/a52-repair-core-hosted/core-03c70c1-attempt1-final.json)
retain all job IDs, actual runner assignments, step outcomes, toolchain evidence,
each CTest result, complete decoded logs and their hashes.

## Exact source and observation boundary

The independently fetched Git commit has tree
`f639acf69061a4b66a0bd3d2219b1ed890e74e42` and sole parent
`fba1911259346bfc6fd3ba7ec78b5cf6c4d1a6b2`. These agree with root's
[publication receipt](../development/2026-11-16-heading-title-continuation/reports/hosted-repair-publication.json).
The exact-source Core workflow has SHA-256
`d35b85df082bfa51d0fb71ba698d0cd16819b5cab0858f78cb03c34df68e7daa`
and Git blob `295897e4b960f0fdc7fe55ba55e6cad5e23c2501`.
It is byte-identical to the retained original Core workflow. Fresh results
were nevertheless observed at this successor: all six API jobs bind its SHA,
and every complete log prints that actual revision.

The successor's three changed qualified inputs concern the standalone fixture
casts, its active source-hash transition and the standalone sanitizer job's
overall budget. Root's receipt retains the unchanged other 472 inputs and
production executable. Core MSVC success does not supply the standalone
fixture's separate compilation/acceptance evidence; A53 owns that workflow.
The original source's successes and failures retain their own identities.

## Actual results

| Required family and job ID | Observed compiler and platform | Executed result |
| --- | --- | --- |
| Linux Release — `133832484757` | GNU 13.3.0, actual x86_64, Ubuntu 24.04 runner; CMake/CTest 3.31.6 | **202/202 CTests**, **107.61 s** |
| macOS Release — `133832484837` | AppleClang 17.0.0.17000013, actual **arm64**, macOS 15.8.2; CMake/CTest 4.4.5 | **202/202 CTests**, **215.84 s** |
| Intel macOS Release — `133832484846` | AppleClang 17.0.0.17000013, actual **x86_64**, macOS 15.7.9; CMake/CTest 4.4.2 | **202/202 CTests**, **469.07 s** |
| Windows Release — `133832484751` | MSVC 19.44.35230.0, actual AMD64, Windows Server 2022; CMake/CTest 3.31.6 | **202/202 CTests**, **292.07 s**; actual Unicode generator acceptance passes |
| Linux ASan + UBSan + leaks — `133832484835` | GNU 13.3.0, Debug, Ubuntu 24.04 runner; CMake/CTest 3.31.6 | **202/202 CTests**, **263.97 s** |
| Complete R4 waveform — `133832484411` | GNU 13.3.0, dedicated Release target, Ubuntu 24.04 runner; CMake 3.31.6 | **14 admission tests pass**; actual full experiment **passes in 724.2499095390001 s**, with `failures: []` |

The five CTest jobs each record 202 distinct names and numbers, a complete
ordinal range, 202 passing dispositions and all twelve mandatory registration,
render, starter-pack and apron names. Their name sets match. Four Release jobs
execute the unfiltered preset with parallelism two, timeout 300 and the
nonempty-test guard. The Core sanitizer job executes the unfiltered sanitizer
preset with parallelism two, timeout 600 and the same guard. Repeated platform
executions do not create 1,010 distinct tests.

All four Release architectures above are actual machine output. The dedicated
Linux sanitizer and R4 logs record compiler identity and x64 Python locations,
but do not separately print machine architecture. Their runner labels are
retained without treating those labels as an independently observed machine
architecture. Both macOS architectures did execute; neither was only queued.

## Instrumentation and full R4 execution

The sanitizer log contains actual core compilation with
`-fsanitize=address,undefined` and `-fno-omit-frame-pointer`, plus the instrumented
renderer link. The executed CTest step records
`ASAN_OPTIONS=detect_leaks=1:halt_on_error=1`,
`UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1` and
`LSAN_OPTIONS=exitcode=23`. All 202 tests finish with no reported sanitizer
failure. This qualifies the executed Core workloads, with standalone sanitizer
coverage retained as a separate job and review.

R4 runs its dedicated full target. Its fourteen report-admission methods all
report `ok`, followed by `OK`. The log then records actual probe compilation,
`--mode full` with the unchanged 1,500-second experiment bound, a full-mode
pass with an empty failure list, and completion of `check_rotary_waveform_full`.
The twelve registration/apron CTest inventory names do not apply to this
dedicated target. Numerical completion retains the waveform owner's separate
R4 acceptance and later R5/R6 boundaries.

## Supplemental checks and artifact limits

Linux's standard-library-only apron suites report 25 methods with **six optional
Pillow skips**, and 14 methods with **two optional NumPy skips**. The actual skip
names and reasons remain in its summary. Optional source-decoding/pixel work is
not counted as an executed method pass. Linux's three prior-session record
steps also complete; their accounting scope is separate from this continuation's
already executed strict sixty-record closure.

Windows actually compiles the starter generator under a Unicode source root
using `/utf-8` and the expected compiled source definition. Its log contains
24 Saved file records and a Complete summary with 24 attempted/committed files,
zero unattempted files and no uncertain file. The ProtectedPath result records
zero attempted/committed files for the authored pack. The unchanged workflow
then completes canonical-payload, source-pack and unchanged-source assertions.
These observations concern the generator's exercised Windows path behavior.

All six artifact uploads complete. Their IDs, sizes and SHA-256 digests match
the independently fetched [artifact metadata](../development/2026-11-16-heading-title-continuation/reports/a52-repair-core-hosted/core-03c70c1-artifacts-metadata.json).
The R4 artifact is **14302066281**, **111,737 bytes**, SHA-256
`22a6d91d738734de36210b34b5afd50c15f8d572d72c8096aa68c5da28748c83`.
A52 did not download the detailed artifact bodies. Full-mode success and the
empty failure list are actual log output; no additional per-experiment numerical
claim is derived from unread members. Windows' detailed payload-hash artifact
retains the same explicit reading limit.

## Preservation and next action

All six complete decoded job logs were inspected and retained as deterministic,
lossless gzip: **2,626,337 UTF-8 bytes**, compressed to **272,720 bytes**.
Each archive has zero mtime, no original filename, recorded sizes/SHA-256 and
verified decompression. Initial assigned-run metadata and the final terminal
observation remain separate. Compact summaries retain every CTest disposition
and decisive source, toolchain, instrumentation and supplemental output.

The [final preservation check](../development/2026-11-16-heading-title-continuation/reports/a52-repair-core-hosted/preservation-verification.json)
verifies all **34 original A52 files unchanged**, including the accepted note,
original Core report/review and MIDI diagnosis evidence. The local 240/242
aggregate, three separate unchanged diagnostics, earlier failed runs and original
standalone compilation failure/cancellation retain their exact outcomes.

Root can integrate this new scoped evidence and combine it with A53/A54's
separate successor reviews. Qualification here belongs to **`03c70c1` only**;
a later documentation/evidence publication must retain its own identity and
source-equivalence record and is not automatically qualified by this run.
No build, native execution, workflow retry, source edit, remote mutation or
extra worker was performed by A52.

Physical Hammond/Leslie fidelity, connected model integration, actual devices
and DAWs, callback deadlines, native accessibility and signed release remain
separate requirements. **Literal whole-interface 1:1 remains unmet and unwaived.**
