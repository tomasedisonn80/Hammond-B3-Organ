# Reconciled main523 standalone review

**All six original attempt-one standalone jobs succeed at
`523c1979334b0fbb624ce120128a0b8ada078383`.** A53/60 remains the same accepted
worker. [Run 44043394005](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44043394005)
is separate from the frozen [548 qualification](../combined-main-standalone/review.md).
No previous failure, cancellation or timing observation is replaced.

The exact tree is `893441fe87859b9dbad81a5d81a453f7c96030f8`, with parents
`8189a49eacab5d4e6ce6c178862e83b03bdec437` and
`54859886268ce83c36f359c43327f7c72a77ae82`. API metadata and every actual
checkout agree. [Inventory](inventory.json), [terminal metadata](final-observation.json)
and [summary](summary.json) retain source, runner, step, counter and archive bindings.

## Original run outcomes

| Family | Job receipt | Actual CTests | CTest seconds | Package |
| --- | --- | ---: | ---: | --- |
| Linux GCC, MIDI ON | [133903129162](job-133903129162.json) | 78/78 | 412.77 | 21 files, ALSA |
| Linux GCC, MIDI OFF | [133903129190](job-133903129190.json) | 78/78 | 499.09 | 17 files, unavailable |
| macOS ARM | [133903129154](job-133903129154.json) | 78/78 | 456.23 | 21 files, CoreMIDI |
| macOS Intel | [133903129393](job-133903129393.json) | 78/78 | 574.83 | 21 files, CoreMIDI |
| Windows x64 | [133903129277](job-133903129277.json) | 78/78 | 549.92 | 21 files, WinMM |
| Linux ASan/UBSan/leaks | [133903128857](job-133903128857.json) | 41/41 | 785.99 | No package stage |

This is 431 CTest observations across configurations, not 431 distinct project
tests. All actual names match the unchanged workflow/CMake inventory: 55
explicit required normal names, 75 standalone-prefixed plus three Python-tool
names discovered, and exactly 41 sanitizer gates from 37 built targets.
The standalone workflow hash remains `d298ac55…`; CMake remains `927f48c1…`.

## Changed readers and actual native evidence

Exactly five Python/tool inputs differ from548. Title and H1 readers admit
two independently frozen complete sources; the indexed form requires the
canonical whole helper exactly once, no original helper, exact reversal and
the complete indexed hash. After execution they require the actually admitted
fixture identity to remain unchanged. Both readers print
`indexed-array-v1` and `whole_file_reversal_verified=true` in all six jobs.
The C++ fixtures, production, build/workflow inputs, strict copied-state equality,
numerical criteria, workloads and individual bounds are unchanged.

Actual normal logs execute **45 capture / 41 H1 / 71 P1 Python methods** with
successful outcomes. The nine additional H1 and seven additional P1 methods
retain all previous methods; the independent source review is bound in the
summary. P1 stdout adds bounded failure-only details, capped at eight records,
160-character check names and 512-character details. These current reader runs
all pass; they do not claim execution of that failure branch.

All six jobs report:

- Title: 18/18 cases against the strict 44-case fixture inventory.
- H1: 48 cases, 10,542 checks, 163 paintings and 95 helper probes; statistics
  pass 103/103, with canonical RGBA `56392ccf…`.
- Grain: four cases and 170 checks.
- P1: 34 cases, 53,648 checks, 111 paintings; 191 numerical checks with zero
  failures and all 62 candidate screens passing.
- All five library gates, ten calibration subprocesses across seven lifecycles
  with two deliberately failed replay scenarios, and two children for each
  real-application replay/semantic paint gate.

Each normal configuration reports 37 actual workspace children. The sanitizer
selection does not include that full workspace replay suite. Windows records
the explicit unsupported FIFO subcase skip, 28 replay-boundary children and
18 preserved setup rejections; no CTest is skipped. Its three native fixtures
actually compile with unchanged `/W4 /WX`.

## Instrumentation, packages and limits

The sanitizer instrumentation step succeeds, including SDL C/project C++
objects, frame pointers, archive/runtime and app/probe/P1 linkage checks.
Production support uses private MIDI=0 and the isolated fake calibration probe
uses MIDI=1. The job retains its 35-minute budget and strict
`detect_leaks=1:halt_on_error=1`, UBSan halt/stacktrace and LSan exit23 policy.
The actual postcheck confirms ten children/all seven lifecycles and scans their
stderr, including expected application failures. Both paint gates identify app
`b7f298dd…`; final source/locked-SDL re-verification succeeds.

All five normal source/dependency postchecks and package stages succeed.
Executed assertions cover exact installed inventory/bytes, rename/relocation,
relocated help and 600 ms dummy smoke, MIDI metadata and archive-member byte
equality. The unchanged eight-method install suite contains the Unicode
custom-prefix/relocation checks; its individual methods are not printed.
A53 retains artifact metadata and original executed assertions, without
downloading package ZIP bodies or claiming signed-release acceptance.

Intel preset raster passes in **19.09 seconds under the unchanged 30-second
guard**. The original 03c timeout remains failed; this observation establishes
no timing repair, originating cause or repeated stability.

## Retention and handoff

The [six complete original logs](complete-log-archives.json) retain
**6,572,863 decoded bytes in 734,082 compressed bytes**, using deterministic
gzip with empty filename and mtime zero. Every stored log was checked against
the original provider-decoded bytes and decompression round trip; Windows
newlines remain unmodified. The final API observation was 08:26:34 UTC on
17 November 2026. Per-job receipts bind original result rows and all skipped
or unprovided scope.

No native/build/project test, remote mutation, retry or extra worker was used
by A53. Root can combine the exact523 matrix and reconcile its separately
preserved documentation branch, then verify the final staged input equivalence
and guarded publication. This review claims no later merge/publication.
Earlier records and the accepted A53 note remain frozen. Whole-UI literal 1:1,
real display/DPI, native accessibility, physical MIDI/audio, calibrated fidelity,
callback lifetime/deadlines and signed distribution remain open.
