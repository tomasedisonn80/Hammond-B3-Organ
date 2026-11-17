# Preset raster local timing review — A54, wave 9 follow-up

## Decision and exact local outcome

**Admit proceeding to exact-published-source hosted verification with the
local evidence reported as mixed.** This admits no source, test-property,
workload, assertion, or timeout change. The complete coherent local run
remains **240/242**, exit 8, 740.264 seconds at the root wrapper and 740.22
seconds reported by CTest. Its two failed CTests were preset raster's
30-second timeout and native MIDI replay. The MIDI failures have their own
A52 review; this document adjudicates only the preset raster evidence.

Root subsequently ran exactly one unchanged isolated preset-raster CTest.
It passed in **27.4798 seconds** in JUnit, **27.48 seconds** in CTest output,
and **27.517879209 seconds** at the wrapper. The verbose log explicitly
reports the computed timeout as **30 seconds**, and the complete output
contains every expected case counter with `failures=0`. This is a separate
passing gate; it does not replace the failed full run or produce a green
242-test aggregate.

The [full result receipt](../development/2026-11-16-heading-title-continuation/reports/qualified-final-coherent-results.json)
retains unchanged code and build identities, all 475 frozen code inputs,
six actual serial nonoverlap windows, and the separate 37-child workspace
evidence. The [full log](../development/2026-11-16-heading-title-continuation/reports/qualified-final-ctest.log)
is 130,384 bytes, SHA-256
`c8fa5c2d326bb22069121f245d307e4c4aad588e0727bd15baf3454e65268b1c`.
The [A54 receipt](../development/2026-11-16-heading-title-continuation/reports/a54-preset-raster-local-timing.json)
binds the original timeout, JUnit failure element, scheduling context,
generated configuration, workload, source/binary hashes, and successful
isolated output. Original failure evidence remains unchanged.

## What this executable measures

The complete
[preset raster fixture](../../apps/standalone/native_tests/test_standalone_preset_raster.cpp)
initializes SDL without hardware subsystems, creates an RGBA software
surface and software renderer, and paints `InstrumentView` directly.
It creates no window, opens no audio device, launches no standalone child,
and measures no audio callback. Its model acknowledgment helper supplies
explicit `SessionSnapshot` values to exercise pending and applied UI states.

The fixed matrix is four dimensions—960×700, 1280×900, 1672×941, and
1400×820—each in Dimensional and Flat presentation. The source performs
256 full instrument paints and 272 RGBA readbacks, including the independent
glyph templates. Its explicit loops are finite, and there are no sleeps,
stopwatch assertions, internal duration targets, or child-process deadlines.
It validates raster correctness under an external finite execution guard;
it is not a real-time performance benchmark.

| Complete isolated output counter | Required and observed |
| --- | ---: |
| Preserved label/focus cases | 192 |
| Full-size accidental glyph cases | 160 |
| Other-manual/accidental isolation cases | 752 |
| Applied/pending/Cancel/rejection checks | 96 |
| Reported failures | 0 |

The counters cover the full original workload, not a shortened subset. CTest
selected one executable and added no fixture tests. The successful JUnit
contains one executed testcase, zero failures, zero skipped tests, and the
same complete output. The normal CMake property is 30 seconds. An existing
300-second sanitizer-only property remains separate; this normal Release
execution used no sanitizer and did not borrow that larger budget.

## Timings, identities, and inference limits

| Retained full run | Preset raster result |
| --- | --- |
| Combined 241 | Passed, 18.80 seconds |
| Serialized 241 | Passed, 22.19 seconds |
| Semantic 242 | Passed, 27.25 seconds |
| Qualified 242 | Timeout, 30.02 seconds in log; 30.015 seconds in JUnit |
| Separate single isolated diagnostic | Passed, 27.48 seconds in log; 27.4798 seconds in JUnit |

The fixture and painter hashes match across all four frozen full-run input
receipts. The current fixture SHA-256 is
`5733e529ecb06609d2e19fa9a367450a66ca8a2a41d99b5b7d42bfbbebe210eb`;
the painter is
`0bf731a692b7cb7c88c200afea86f4ca14239f20a7000f06be484f2a11ebc20d`.
The preset executable observed during the full run and selected unchanged
for the isolated diagnostic is
`2f064905f2edb47d2d50369c1c468f005dedd386cefcb0d81419e1bdd3322fb9`.
Its hash was independently read while the full run was active and matches
root's isolated input receipt. Historical full input receipts did not
explicitly hash this particular target, so this review does not assert its
binary identity across all earlier runs from source hashes alone.

During the original timeout, `python_test_chapel_controls` was already
active when preset raster started. That test completed and
`test_standalone_chapel` began before preset raster ended. Concurrent CTest
work is observed. The log contains no partial assertion failure or case
counter output for the timed-out process; the fixture normally prints its
summary only at completion. The exact operation at termination and a
specific CPU/scheduler cause are therefore not established.

The isolated success establishes that the complete unchanged workload
finished within the unchanged deadline in one later execution. Its margin
was approximately 2.52 seconds. This is consistent with timing sensitivity,
but proves neither repeated stability nor causality. It does not establish
a new safe timeout or justify changing any scheduling property. No such
change is admitted here.

## Publication and hosted verification boundary

The [isolated receipt](../development/2026-11-16-heading-title-continuation/reports/preset-raster-one-isolated.json)
records one `ctest -R '^test_standalone_preset_raster$' --parallel 1 --verbose`
invocation, with the original no-tests/error and output semantics. The
[success log](../development/2026-11-16-heading-title-continuation/reports/preset-raster-one-isolated.log)
hash is
`b245f3df496da5086be88f982bf3443cc13c65c5ab82e7c3a9fd1fc320167d23`;
the corresponding JUnit hash is
`2f0b11ae8484aaa9eb89ccb3b4e8c9213b28f451c53ea17f092cdb0795646190`.
A54 checked both hashes, the exact test selection and executable, the
computed timeout, complete counters, exit zero, and unchanged relevant
input identities.

Root may publish the reviewed source and obtain hosted evidence for that
exact commit while openly retaining the failed local aggregate and separate
isolated outcomes. A full local rerun solely to replace the aggregate is
not required by this bounded admission, and no repeated diagnostic is
authorized. The publication must not describe 242/242 passing or claim
repeated timing stability. Hosted runs remain pending until their exact
SHA, jobs, attempts, platforms, and actual outcomes are inspected.

Native VST3 validator success cannot by itself qualify this standalone
raster test. A relevant hosted standalone gate supplies separate evidence
for its own build, configured deadline, and runner. Neither hosted result
removes the original local timeout. No all-host, hardware, physical
calibration, signing, or whole-UI 1:1 acceptance is implied.

A54 performed read-only inspection and wrote only this review and its new
receipt. No prior note or review, source file, CMake property, fixture,
assertion, or native artifact changed, and A54 executed no native test,
build, or retry. Exact-source hosted VST3 review remains the same worker's
pending assignment.
