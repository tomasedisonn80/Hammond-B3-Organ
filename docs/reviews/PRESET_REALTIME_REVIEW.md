# Fixed-selector callback allocation acceptance

A26, `/root/w05_a26_realtime_selector`, 2026-11-14. The independent SDK-free
`test_preset_realtime` passed **1/1 selected CTest in 0.08 seconds** on a fresh
Linux Release build. Its **761 measured API regions observed zero global C++
allocations and zero deallocations**. No production defect or production change
was found. The [execution record](../development/2026-11-14-preset-continuation/26-realtime-selector.md)
identifies copied source, commands and artifacts; checkout HEAD alone does not
identify the uncommitted implementation that was tested.

## Instrumentation and independent expectations

The new test reuses only the repository's portable allocation-probe plumbing.
Explicit calls through volatile function pointers calibrate **12 allocation
and 12 matching deallocation forms**, including scalar/array, zero-size,
sized, nothrow and aligned operations. Aligned payloads are checked. Calibration
is separate from every product measurement and cannot disappear through
new-expression elision. The core is linked statically into this test executable;
there is no separately loaded SDK module to interpose.

Every measured region contains only the target API call and its value return.
Profile parsing, preparation, large-object construction, fixture creation,
reference processing, diagnostics, assertions, formatting and printing remain
outside the probe. Results therefore do not depend on allocation in the test
framework or on warming a failing product path before observation.

The first fixed-row lookup occurs before profile loading or Engine preparation.
All eighteen warmed rows and labels use A10's independent page-122 transcription
as the expected source. A separate literal transition oracle checks fixed,
Cancel and bank behavior without calling ControlState to construct expectations.
The callbacks then use distinct nonzero retained banks, both manual divisions,
folded end notes, two pedals, enabled percussion and moving/partial contacts.

## Executed regions

| Path | Calls | Accepted | Rejected | Accepted frames | Accepted records |
|---|---:|---:|---:|---:|---:|
| Immutable lookup, identity and labels | 57 | 51 | 6 | 0 | 0 |
| Control restore and effective-selector query | 156 | 150 | 6 | 0 | 0 |
| Engine callback | 482 | 398 | 84 | 17,600 | 6,348 |
| Combined PerformanceInput | 6 | 4 | 2 | 128 | 20 |
| HostTimeline callback | 60 | 48 | 12 | 1,920 | 6,210 |
| **Total** | **761** | **651** | **110** | **19,648** | **12,578** |

Every row reports zero observed allocations and deallocations. Rejected-call
counts include immutable lookup and control rejection, not only audio callbacks.
The test's 0.08-second suite duration is not a measured callback deadline.

Core and HostTimeline cases run at **44.1, 48 and 96 kHz**, with both ideal and
nominal linear-travel contacts. Combined-input cases use both contact models at
48 kHz. The measured cases include:

- The first prepared Engine callback selecting fixed registrations with notes,
  pedals and a moving partial target; all twelve commands on both manuals;
  both upper-B percussion eligibility outcomes; negative-zero Cancel; retained
  bank memory; 1,024 per-frame selection events; disconnected output.
- Complete zero-time histories across **152** transitions: all 91 source phases,
  122 contact snapshots, 200 pedal contacts, frame clock, percussion readiness
  and the last rendered pedal record. Owners remain intact in the combined and
  host paths, and checks distinguish routing changes from note authority.
- Late invalid manual/index/fraction/range/nonfinite events following valid
  commands; invalid fixed memory hidden behind Cancel; unchanged output and
  complete rollback. **104** next-call probes compare **6,656 rendered mono
  samples plus 312 untouched tail sentinels**, all bit-identical to untouched
  value copies. The aggregate `compared_samples=6968` includes those tails.
- Four queued control restores in the first host call; reverse queue enumeration
  with literal 8208/20480/20481 identities; higher-ID selector precedence;
  repeated old-bank commands; carried Cancel; all selector thresholds in a
  continuous sweep; 1,024 same-offset parameter points; rejected fresh notes
  combined with a bad selector while an endpoint remains carried.

The tested rendering inspected **12,800 nonzero samples**. These counts make the
enabled musical paths observable; a zero-allocation result on an otherwise
silent fixture would not have supplied the same evidence.

## Scope and next gate

This is calling-thread **global C++ operator** instrumentation for the named
Linux build. It does not observe arbitrary `malloc`/system allocation, other
threads, locks, file I/O, physical callback deadlines, devices or host behavior.
The allocation result is separate from source inspection and native VST3
interposition evidence. No sanitizer, AppleClang, MSVC or device run was performed
by A26. Large HostTimeline objects are allocated outside observation to avoid
depending on a platform's default thread-stack reserve.

The test is registered by the existing root CMake glob without a build-system
edit. The integrator should include it in the final coherent source build and
published platform gates. Unchanged legacy PCM, complete UI/host qualification
and physical fidelity retain their separately assigned evidence. Documentary
registrations still use the nominal gain law and do not close a physical
latching, loading, factory-table acquisition or measured-response gate.
