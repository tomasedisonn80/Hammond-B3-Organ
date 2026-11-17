# Standalone hosted verification at 03c70c1

## Terminal outcome

**This standalone run failed overall: four jobs succeeded and two failed.**
[Run 44021714635, attempt 1](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44021714635)
executed source 03c70c103a4a0dd72b323529416b909c19a4e139, tree
f639acf69061a4b66a0bd3d2219b1ed890e74e42, with sole parent
fba1911259346bfc6fd3ba7ec78b5cf6c4d1a6b2. Independent API and immutable Git
inspection bind the source, actual job attempts, runners and workflow bytes.
All six jobs are terminal and their complete returned logs are retained.

| Actual job | Job ID | Observed result | Workflow package result |
| --- | --- | --- | --- |
| Linux GCC, MIDI ON | 133832484738 | 68/68 passed; 363.64 s | 21 files, ALSA; verified |
| Linux GCC, MIDI OFF | 133832484541 | 68/68 passed; 425.53 s | 17 files, unavailable MIDI; verified |
| macOS ARM, MIDI ON | 133832484806 | 68/68 passed; 426.12 s | 21 files, CoreMIDI; verified |
| macOS Intel, MIDI ON | 133832484811 | 67 passed; preset raster timed out; 770.85 s total, exit 8 | Skipped after test failure |
| Windows MSVC x64 | 133832484867 | Fixture compilation failed with C4702/C2220 | Unreached |
| Linux GCC ASan/UBSan/leaks | 133832484818 | 34/34 passed; 705.12 s | This job has no package gate |

The [aggregate receipt](../development/2026-11-16-heading-title-continuation/reports/a53-repair-standalone-hosted.json)
binds all six detailed job records, source identities, native invocation counts,
header results, original failures and remaining gates. The
[run record](../development/2026-11-16-heading-title-continuation/reports/a53-repair-standalone-hosted/run-44021714635.json)
retains actual runner identities and nine artifact metadata records.

## Exact changed source and preserved workload

The executed workflow is 71,269 bytes, SHA-256
af5cf9421c5cdbae37b5f0d26e1bf3d96c8a5b26491f89b6518db0ca0e1cc319.
Compared with the original fba workflow, its only byte change is the overall
sanitizer job allowance from 20 to 35 minutes. All individual child/CTest
limits, selected tests, build targets, instrumentation and leak policy remain
unchanged. The published fixture is 96149cf482ad0a57512257a519b89198113f21b06c33b073b2861e13349d1809;
its active statistics test is
5f876087a4fea18acc46db16d4c1e7dba3a50e83d322ee6d835d16dd01e31e4f.
These identify the explicit dimension-cast correction, before the later
helper-branch change.

The normal workflow requires 45 names and executes all 68 standalone-prefix
tests. Every successful normal job passed that entire set. Intel attempted
the same 68 names and failed one completion guard. The sanitizer job discovered
and passed exactly its 34 gates mapped to 31 built inputs.

Header material passed 48 cases, 10,542 checks and 163 paintings on all four
normal platforms that reached tests, and under sanitizers. Statistics passed
all 103 numerical criteria; grain bounds passed four cases and 170 checks.
The canonical RGBA digest remains
20eea493c5b2fe75c467a5964b54a28c832edf7639f034d8eb83daf4036d4557,
and the header digest remains
1a7b0b316dc771428f2241eec9fbd25668ba337a6a2232b5787a2014f86eaaac.

Each normal platform that reached tests reports 37 actual workspace children,
ten calibration children across seven lifecycles with two deliberate replay
failures, and two native children for each real-application paint suite.
The full per-suite counts and actual executable hashes are retained.
Passing these tests does not turn either failed job into a pass.

## Windows: distinct second compiler failure

The [Windows record](../development/2026-11-16-heading-title-continuation/reports/a53-repair-standalone-hosted/job-133832484867.json)
retains the complete original CRLF log and exact compiler/summary blocks,
plus separately identified normalized readable views. MSVC 14.44.35207 uses
the unchanged /W4 /WX policy. It reports C4702, unreachable code, at
test_standalone_header_material.cpp line 49, promoted to C2220.

The original C4244 conversion diagnostic is absent from this complete log,
and immutable source inspection confirms the admitted casts. Nevertheless,
this translation unit fails; no successful fixture object, executable or
native acceptance is established. Compiled-MIDI verification, discovery,
all native tests, final source verification and packaging are unreached.

Line 49 is the false return following a constexpr helper-present branch that
already returns true. A53 froze a separate
[prospective admission](../development/2026-11-16-heading-title-continuation/reports/a53-repair-standalone-hosted/windows-helper-branch-admission.json)
and exact patch before root implemented it. The correction places the same
false return inside an explicit constexpr else and updates only the active
statistics fixture pin. The true specialization keeps the identical helper
call, arguments and true result. The absent-helper specialization still
discards the call and returns false. Exceptions, callsite guards, probe counts
and renderer-state assertions are unchanged. Absence preservation is source
and template-instantiation reasoning, not a newly executed absence experiment.

The separate [conformance receipt](../development/2026-11-16-heading-title-continuation/reports/a53-repair-standalone-hosted/windows-helper-branch-conformance.json)
verifies exact proposed bytes, preserved originals, identical Linux fixture
binaries, identical actual 48-case inventory and default stdout, and complete
statistics differing only in two source identities. Root's existing two CTests
passed once in 38.725693459 seconds. All 475 current code inputs were independently
checked: two differ from 03c70c1, with 473 unchanged; three differ from fba1911,
with 472 unchanged. Production, workflow, historical comparator and accepted
capture identities retain their earlier scope.

The proposed fixture is 86acc068fa23826fb39f245f9327e919c076660f315bed5d57f63e586d6d3ac6;
its active test is
3fb1584f497bd0883362b0f86068cb37625038969875cc1c3214a972117a97d3.
Those bytes are not the source of this failed Windows job. Actual hosted
qualification requires a separately published revision.

## Intel: exact ordinary preset-raster timeout

The [Intel record](../development/2026-11-16-heading-title-continuation/reports/a53-repair-standalone-hosted/job-133832484811.json)
retains all 68 result rows and the exact timeout and final-failure blocks.
Test 226, preset raster, starts at 05:23:47.072326 UTC with the computed
30-second CTest bound. At 05:24:17.120441 the result is Timeout, 30.05 seconds.
There is no fixture stdout or in-fixture assertion diagnostic before termination.
The completed case, painting and assertion counts are therefore unknown.

The preset fixture is 19,942 bytes, SHA-256
5733e529ecb06609d2e19fa9a367450a66ca8a2a41d99b5b7d42bfbbebe210eb.
It, the painter, Drawing implementation/header, FontData and CMake target
definition are byte-identical at fba1911, 03c70c1 and the inspected current
working source. The ordinary limit remains 30 seconds; the separately
instrumented configuration retains its existing 300-second limit.

The original fba Intel execution passed this test in 21.31 seconds. At 03c70c1,
Linux MIDI ON passed in 8.51 seconds, MIDI OFF in 13.02, ARM in 11.27, and
the instrumented job in 70.71 under its separate bound. These observations
do not identify why the Intel execution exceeded 30 seconds. No hardware,
scheduler, source-regression or hang mechanism is asserted. Nor is completion
with a longer limit presumed.

All other 67 Intel tests pass, including the installer, workspace, calibration
and paint suites. The workflow's source/dependency reverification and final
staging, archive checks and package upload are skipped after the test failure.
They are not supplied by the earlier successful installer CTest.

The [separate A52 review](../development/2026-11-16-heading-title-continuation/reports/a52-repair-core-hosted/intel-standalone-independent-review.json)
independently binds the retained evidence and supports publishing only the
reviewed helper change with the preset source, workload and 30-second guard
unchanged. This Intel gate remains failed at 03c70c1; no automatic retry,
new deadline or causal explanation is admitted here.

## Complete strict sanitizer execution

The instrumentation step passed checks for SDL C and project C++ sanitizer
flags, frame pointers, archive/object symbols and linked runtimes. The real
application includes its main and painter; the grain fixture includes the
real painter once. Private MIDI=0 is checked on the support library; the fake
calibration probe retains MIDI=1 and fake-header precedence. Both entry paths
link the required instrumented archives.

The policy remains ASAN_OPTIONS=detect_leaks=1:halt_on_error=1,
UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1, and LSAN_OPTIONS=exitcode=23.
There are no permitted test-level overrides. The relevant child launchers
inherit these values while selecting dummy/software SDL drivers.

All 34 tests passed, including preset raster in 70.71 seconds, calibration
in 21.24, replay paint in 1.03 and semantic paint in 1.18.
The actual log confirms ten calibration subprocesses, seven lifecycles and
two deliberate replay failures. Its explicit post-check verifies the matching
instrumented probe identity and scans every captured lifecycle stderr.
Both paint suites execute two children against application digest
866a126b9b42e9e1a0602b6e874276a63698ed981c6469d25259190c6a185d5a.
Final source and locked-SDL verification also passed. No actual sanitizer
finding is observed. The full log and
[sanitizer job record](../development/2026-11-16-heading-title-continuation/reports/a53-repair-standalone-hosted/job-133832484818.json)
retain these executed outcomes.

This establishes those gates for 03c70c1. It does not establish the reason
for the original fba cancellation, and does not qualify the later helper source.

## Installation and durable evidence

All four normal jobs that reached tests passed the complete eight-method
installer suite. Its immutable source includes Unicode and space-containing
prefixes, custom directories, copied installation, removal of a private
source/build copy, relocated operation and the fixed 800 ms inverted-CC11
replay. Complete script execution establishes coverage; individual unittest
method names are not printed.

Only the three successful normal jobs completed the workflow's additional
exact payload, moved-prefix help, 600 ms dummy smoke and archive byte/mode
checks. Their three package artifacts are present. All six jobs retain
diagnostics, for nine artifacts total. A53 inspected metadata and actual
executed assertions, without independently downloading those artifacts.

The [complete-log manifest](../development/2026-11-16-heading-title-continuation/reports/a53-repair-standalone-hosted/complete-log-archives.json)
retains all six complete decoded streams: 5,842,156 original UTF-8 bytes in
623,870 stored bytes. Deterministic gzip, decoded/compressed hashes, exact
round trips and original-block membership are checked. Windows CRLF bytes
remain lossless. Prior fba evidence, helper admissions and the accepted
833-word A53 note remain unchanged.

Root next publishes the reviewed helper-only correction and independently
verifies its exact source and complete matrix, keeping this Intel timeout
open and the preset guard unchanged. No new worker credit, native execution,
source mutation, CI retry or remote change was performed by A53. Physical
devices, real displays, native accessibility and literal whole-interface
1:1 remain independent, open requirements.
