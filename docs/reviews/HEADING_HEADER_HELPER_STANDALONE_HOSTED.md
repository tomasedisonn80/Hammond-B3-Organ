# Standalone hosted verification at 6287055

## Terminal outcome

**This standalone run failed overall: five jobs succeeded and Windows failed.**
[Run 44026516737, attempt 1](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44026516737)
executed source 6287055a111dc4e2747564da3d48edc9b65e2e3e, tree
c96fe07c4241f5afe423306945508a114506f0c2, with sole parent
03c70c103a4a0dd72b323529416b909c19a4e139. Independent API and immutable Git
inspection bind that source, the actual runner identities and the workflow.
All six jobs are terminal and all six complete returned log streams are retained.

| Actual job | Job ID | Observed test result | Workflow package result |
| --- | --- | --- | --- |
| Linux GCC, MIDI ON | 133848047337 | 68/68 passed; 454.84 s | 21 files, ALSA; verified |
| Linux GCC, MIDI OFF | 133848047285 | 68/68 passed; 396.00 s | 17 files, unavailable MIDI; verified |
| macOS ARM, MIDI ON | 133848047251 | 68/68 passed; 479.82 s | 21 files, CoreMIDI; verified |
| macOS Intel, MIDI ON | 133848047288 | 68/68 passed; 577.89 s | 21 files, CoreMIDI; verified |
| Windows MSVC x64 | 133848047271 | 66 passed, two protocol failures; 465.15 s, exit 8 | Skipped after test failure |
| Linux GCC ASan/UBSan/leaks | 133848047071 | 34/34 passed; 1,101.79 s | This job has no package gate |

The [aggregate receipt](../development/2026-11-16-heading-title-continuation/reports/a53-helper-standalone-hosted.json)
binds every detailed job record, exact source identities, native invocation
counts, reached and skipped work, and the preserved prior outcomes. The
[run record](../development/2026-11-16-heading-title-continuation/reports/a53-helper-standalone-hosted/run-44026516737.json)
retains actual attempts, runners, step conclusions and ten artifact metadata
records. No earlier-source pass is substituted for a current result.

## Published correction and unchanged workload

The published C++ header fixture is 61,275 bytes, SHA-256
86acc068fa23826fb39f245f9327e919c076660f315bed5d57f63e586d6d3ac6.
Its active statistics source is
3fb1584f497bd0883362b0f86068cb37625038969875cc1c3214a972117a97d3.
The fixture puts the existing false return inside the constexpr helper-absent
else branch. The only companion source change is the active fixture identity
literal. The [frozen admission and conformance](../development/2026-11-16-heading-title-continuation/reports/a53-repair-standalone-hosted/windows-helper-branch-conformance.json)
remain unchanged. Helper-absent behavior was reviewed through source and
template-instantiation semantics; this run is not a newly executed
helper-absent experiment.

All 475 frozen code paths were compared between the published Git trees.
Only those two files differ from 03c70c1; 473 remain identical. Production,
preset source, ordinary CTest properties and workflow are unchanged. The
workflow remains 71,269 bytes, SHA-256
af5cf9421c5cdbae37b5f0d26e1bf3d96c8a5b26491f89b6518db0ca0e1cc319.
Its sanitizer job allowance is 35 minutes, with the same individual child
and CTest bounds, 34 selected gates, 31 build inputs and strict leak policy.

Each normal job discovered and executed the same 68 standalone-prefix names,
including all 45 explicitly required names. The four successful normal jobs
passed the entire set. Windows attempted the same set and retained both failures.
The sanitizer job discovered and passed exactly its separate 34-name set.

## Windows: compilation repaired, copied-state gates failed

The [Windows job record](../development/2026-11-16-heading-title-continuation/reports/a53-helper-standalone-hosted/job-133848047271.json)
retains actual MSVC 19.44.35230.0 identification, toolset path 14.44.35207,
and both fixture CL.exe invocations under /W4 /WX and /fp:precise.
The complete application and acceptance-input build succeeded, followed by
successful compiled WinMM identity verification. Neither prior C4244 nor
C4702 diagnostic appears in the complete returned log.

The native header-material fixture then passed all 48 cases, 10,542 checks,
163 paintings and 95 helper probes in 26.18 seconds. Grain bounds passed
four cases and 170 checks. Those are actual successful executions of the
published helper source.

Two later Python gates fail before numerical image evaluation:

| Gate | Exact observed predicate | Completed before failure | Unreached numerical work |
| --- | --- | --- | --- |
| Title density, test 218 | `copied view controls differs` | The complete 44-case inventory and fixed case0 protocol fields validate | Result cases are empty; no title-density case is evaluated |
| Header statistics, test 221 | `complete canonical copied session differs` | One native case46 invocation, fixed protocol fields and equal before/after records | All 103 criteria remain unevaluated; evaluated, passed and failed counters are zero |

Title density fails in 0.23 seconds; statistics fails in 0.44.
The statistics report retains the exact new fixture and active-test hashes.
Its protocol/helper completion flags remain false because validation exits
early; they do not establish a missing helper. The raw RGBA-length checks
after model validation are also unreached in both Python gates.

The [original failure-retention receipt](../development/2026-11-16-heading-title-continuation/reports/a53-helper-standalone-hosted/windows-first-failure-retention.json)
binds exact CRLF blocks for the first complete title failure, successful native
header result, statistics failure and final exit-8 summary. Separate readable
LF views have distinct hashes and verified newline-normalization equality.
The original complete Windows stream is 605,930 bytes, SHA-256
285945725cd6b549ab7c942a99f7e8a951debed844b62b2e6eb1abb61dd09517.

### What the original evidence cannot identify

Both failed predicates use strict recursive type-and-value equality.
The native controls writers explicitly cast integer, enumeration and route
values to unsigned, and model/session streams enable boolalpha and the
double max_digits10 precision. The fixed expression .625 and peak .125 are
exactly representable. Both Windows frame exports set stdout binary mode,
and the JSON parsers already reached the reported model checks.

The actual differing model/session field is absent from the returned log.
Both Python scripts hold the native frame in bounded memory and emit only
the generic predicate failure; the original workflow artifact paths do not
retain the raw case0/case46 header. Zero child exit, empty child stderr and
earlier successful checks follow from reaching the later guarded predicate,
rather than from a separately retained per-child payload.

Therefore no floating-point, newline, serialization, rendering or model cause
is established. The title fixture and title Python source are unchanged from
03c70c1, at facc85f516454964ed55e406f95db4046923d7a2441fdf72e65719b3685fec4f
and 9abe3ba03b00efeb3665aa691d36715cebb2f9d708d37eae90cdcd778de171e2.
No expected field, typed comparison or numerical criterion is relaxed.

Root is collecting the missing bounded native headers through a separately
reviewed Windows diagnostic workflow that checks out the exact failed source.
That observation must remain distinct from this failed product acceptance.

### Passed Windows work and skipped tails

All other 66 tests pass. The installer executes all eight methods successfully.
The native suites report 184 application children, 159 MIDI CLI/modal children,
three expression-diagnostics children, ten calibration children across seven
lifecycles with two deliberate replay failures, 33 native MIDI replays, 52
workflow children and 37 workspace children. Both real-application paint
suites execute two children against Windows application digest
806358a837af8b9e49eb20b58e85d145352c5b734d66bcc2c59f3c20493ea404.

Replay-boundary acceptance specifically reports 28 children and 18 preserved
setup rejections, with one explicit FIFO subcase skipped because FIFO creation
is unsupported on that platform. Unix executions retain 29 and 19 respectively.
That skip is recorded separately from the two failed CTests.

Final source/dependency reverification and all workflow staging, archive checks
and executable-package upload are skipped after CTest exits 8. The successful
installer CTest does not supply those skipped workflow outcomes.

## Intel: new pass under the unchanged guard

The [Intel record and exact preset block](../development/2026-11-16-heading-title-continuation/reports/a53-helper-standalone-hosted/job-133848047288.json)
show preset raster starting at 06:02:46.951307 UTC with the computed
30-second ordinary CTest bound. It completes in 22.80 seconds, with the
original 192 preserved label/focus cases, 160 full-size accidental glyph
cases, 752 other-manual/accidental isolation cases and 96
applied/pending/Cancel/rejection checks; failures are zero.

The preset fixture remains
5733e529ecb06609d2e19fa9a367450a66ca8a2a41d99b5b7d42bfbbebe210eb,
and the CMake definition remains
642655110b803592e0943d6bb1aa367cd74c81d72b6ebef0b3f1058916157a96.
All 68 Intel tests, source/dependency reverification and final package checks
pass in this execution.

The prior 03c70c1 Intel timeout at 30.05 seconds remains failed in its frozen
record. This new pass does not repair or explain it, establish a causal
mechanism, or prove performance stability. No preset timing change was made.

## Complete strict sanitizer execution

The [sanitizer record](../development/2026-11-16-heading-title-continuation/reports/a53-helper-standalone-hosted/job-133848047071.json)
binds all 34 actual result rows and the successful instrumentation step.
That step executes checks for SDL C and project C++ address/undefined flags,
frame pointers, object/archive symbols and linked runtimes across the 31
selected inputs. It checks real application main/painter coverage and one
real painter inclusion in the grain fixture. The support library has private
MIDI=0; the fake calibration probe has MIDI=1 and fake-header precedence.
Both application and probe link the six required instrumented archives.

The policy remains:

- ASAN_OPTIONS=detect_leaks=1:halt_on_error=1
- UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1
- LSAN_OPTIONS=exitcode=23

No test-level override is permitted by the executed discovery checks.
Child launchers retain this environment while selecting dummy/software SDL
drivers. Actual commands retain statistics child60/CTest240, grain90,
header480, title240, preset300, calibration180, and both paint suites'
child30/CTest90 bounds.

The 34 tests pass in 1,101.79 seconds. Preset raster passes in 112.83;
native calibration in 21.55; replay paint in 1.16; semantic paint in 1.26.
The log explicitly confirms ten calibration subprocesses and all seven
lifecycles, with two deliberately failed replay scenarios. Its post-check
verifies the matching instrumented probe identity and checks every retained
lifecycle stderr. Both paint suites execute two children against
application digest 866a126b9b42e9e1a0602b6e874276a63698ed981c6469d25259190c6a185d5a.
Final source and locked-SDL reverification also passes. No actual sanitizer
finding is observed.

The four successful normal platforms and the sanitizer job each pass all 103
header numerical criteria with canonical RGBA
20eea493c5b2fe75c467a5964b54a28c832edf7639f034d8eb83daf4036d4557
and header digest
1a7b0b316dc771428f2241eec9fbd25668ba337a6a2232b5787a2014f86eaaac.
Windows contributes no numerical-statistics pass or canonical pixel digest.

Instrumentation and archive claims bind the immutable workflow, actual
successful steps and returned logs. A53 did not independently download the
instrumentation or package artifacts.

## Installation, evidence retention and next step

All five normal jobs pass the complete eight-method installer suite.
Its immutable source includes Unicode/space paths, custom directories,
a private copied installation, removal of its private source/build,
relocated operation and the fixed 800 ms inverted-CC11 replay.
Individual unittest method names are not printed; source and complete
unfiltered execution establish the covered methods.

The four successful normal jobs also finish the workflow's exact payload
hash/mode inventory, relocated help and 600 ms dummy smoke outside the
repository, quiescent MIDI and unchanged-payload assertions, and archive
member/byte/mode checks. Four package artifacts and six diagnostic artifacts
are present. This review inspected metadata and executed assertions,
without directly downloading those ten artifacts.

The [complete-log manifest](../development/2026-11-16-heading-title-continuation/reports/a53-helper-standalone-hosted/complete-log-archives.json)
retains 6,057,027 original decoded UTF-8 bytes in 669,518 deterministic gzip
bytes. Every compressed/decoded hash, round trip and bounded excerpt's
membership in the original stream is checked. Windows CRLF bytes remain
lossless. The original fba and 03c outcomes, helper admission/conformance,
and accepted 833-word A53 note retain their frozen identities.

The next step is exact-source Windows field diagnosis before any source or
parser correction. The original failure status, all typed equality predicates,
numerical criteria, workloads, child/CTest bounds and warning policy remain.
Any later correction requires its own review and actual qualification.

This is the same accepted A53 follow-up, with no additional worker credit.
A53 performed no project build, native/test execution, source/workflow edit,
CI retry or remote mutation. Physical devices, real displays and DPI,
native accessibility, and literal whole-interface 1:1 remain separate,
unclosed requirements.
