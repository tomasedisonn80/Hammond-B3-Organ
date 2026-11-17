# Helper-source Core CI qualification — A52 follow-up

**All six required Core CI families pass on attempt 1 at published commit
`6287055a111dc4e2747564da3d48edc9b65e2e3e`.** The
[actual run](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44026516631)
is completed/success. Every job acquired a runner and executed; none failed or
was cancelled. This is the same accepted A52 worker, with no additional worker
credit. The accepted note and every original A52 report remain byte-identical.

The [source-bound report](../development/2026-11-16-heading-title-continuation/reports/a52-helper-core-hosted.json)
and [final API observation](../development/2026-11-16-heading-title-continuation/reports/a52-helper-core-hosted/core-6287055-attempt1-final.json)
retain all job IDs, actual runner assignments, step outcomes, toolchain evidence,
each CTest result, complete decoded logs and their hashes.

## Exact source and observation boundary

The independently fetched Git commit has tree
`c96fe07c4241f5afe423306945508a114506f0c2` and sole parent
`03c70c103a4a0dd72b323529416b909c19a4e139`. These agree with root's
[publication receipt](../development/2026-11-16-heading-title-continuation/reports/helper-branch-publication.json).
The exact-source Core workflow has SHA-256
`d35b85df082bfa51d0fb71ba698d0cd16819b5cab0858f78cb03c34df68e7daa`
and Git blob `295897e4b960f0fdc7fe55ba55e6cad5e23c2501`.
It is byte-identical to the retained original Core workflow. Fresh results
were nevertheless observed at this successor: all six API jobs bind its SHA,
and every complete log prints that actual revision.

Within the 475 qualified code/build inputs, the helper publication changes
only the reviewed constexpr branch in the standalone header fixture and its
active source-hash literal relative to `03c70c1`. Root's receipt retains the
other 473 inputs and unchanged production executable; the publication also
contains documentation and evidence. The already-published sanitizer job budget is unchanged.
Core MSVC success does not supply the standalone fixture's separate compilation
and acceptance evidence; A53 owns that workflow. Earlier source outcomes remain
unchanged, including the Intel standalone preset timeout and its 30-second guard.

## Actual results

| Required family and job ID | Actual toolchain/platform evidence | Executed result |
| --- | --- | --- |
| Linux Release — 133848047021 | GNU 13.3.0; Linux-7.0.0-1014-aws-x86_64-with-glibc2.39; CMake 3.31.6 | **202/202 CTests**, **108.01 s** |
| macOS ARM64 Release — 133848046977 | AppleClang 17.0.0.17000013; macOS-15.8.2-arm64-arm-64bit; CMake 4.4.5 | **202/202 CTests**, **134.99 s** |
| Intel macOS Release — 133848046893 | AppleClang 17.0.0.17000013; macOS-15.7.9-x86_64-i386-64bit; CMake 4.4.2 | **202/202 CTests**, **302.72 s** |
| Windows Release — 133848046993 | MSVC 19.44.35230.0; Windows-2022Server-10.0.20348-SP0, AMD64; CMake 3.31.6 | **202/202 CTests**, **343.24 s**; actual Unicode generator checks pass |
| Linux ASan + UBSan + leaks — 133848047047 | GNU 13.3.0; Ubuntu 24.04 runner; machine architecture not separately printed; CMake 3.31.6 | **202/202 CTests**, **265.43 s** |
| Complete R4 waveform — 133848046591 | GNU 13.3.0; Ubuntu 24.04 runner; machine architecture not separately printed; CMake 3.31.6 | **14 admission tests pass**; full-mode result **pass**, 613.307703575 s, failures [] |

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
the independently fetched [artifact metadata](../development/2026-11-16-heading-title-continuation/reports/a52-helper-core-hosted/core-6287055-artifacts-metadata.json).
The R4 artifact is **14303582890**, **111,747 bytes**, SHA-256
`266ab25afd9f6ae6ea912a117694977d014f9708a08c7696a7144516bd4882a0`.
A52 did not download the detailed artifact bodies. Full-mode success and the
empty failure list are actual log output; no additional per-experiment numerical
claim is derived from unread members. Windows' detailed payload-hash artifact
retains the same explicit reading limit.

## Preservation and next action

All six complete decoded job logs were inspected and retained as deterministic,
lossless gzip: **2,619,513 UTF-8 bytes**, compressed to **271,213 bytes**.
Each archive has zero mtime, no original filename, recorded sizes/SHA-256 and
verified decompression. Initial assigned-run metadata and the final terminal
observation remain separate. Compact summaries retain every CTest disposition
and decisive source, toolchain, instrumentation and supplemental output.

The [final preservation check](../development/2026-11-16-heading-title-continuation/reports/a52-helper-core-hosted/preservation-verification.json)
verifies all **63 original A52 files unchanged**, including the accepted note,
both earlier Core reports/reviews, MIDI diagnosis evidence and the
[independent Intel timeout review](../development/2026-11-16-heading-title-continuation/reports/a52-repair-core-hosted/intel-standalone-independent-review.json).
The local 240/242 aggregate, three separate unchanged diagnostics, earlier failed
runs, standalone Windows failures/cancellation and Intel preset timeout retain
their exact outcomes. The unchanged preset workload/30-second guard and its
original failure are not repaired by this helper correction.

Root can integrate this new scoped evidence and combine it with A53/A54's
separate successor reviews. Qualification here belongs to **`6287055` only**;
a later documentation/evidence publication must retain its own identity and
source-equivalence record and is not automatically qualified by this run.
No build, native execution, workflow retry, source edit, remote mutation or
extra worker was performed by A52.

Physical Hammond/Leslie fidelity, connected model integration, actual devices
and DAWs, callback deadlines, native accessibility and signed release remain
separate requirements. **Literal whole-interface 1:1 remains unmet and unwaived.**
