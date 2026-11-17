# Semantic paint regression: CI and generated coverage

**A51 follow-up, 17 November 2026: the inspected CMake/workflow additions and
normal generated metadata satisfy the admitted coverage and scheduling scope.**
This is the same A51 assignment, with no new worker credit. The earlier
[source audit](HEADING_HEADER_FINAL_SOURCE_AUDIT.md), its receipt and A51 note
remain byte-identical. The new [bounded receipt](../development/2026-11-16-heading-title-continuation/reports/a51-semantic-paint-ci-coverage.json)
records source comparisons and independent metadata checks. Native execution,
runtime implementation acceptance, publication and hosted results remain root-owned.

## Exact inspected inputs

| Input | SHA-256 |
| --- | --- |
| Standalone workflow, 71,269 bytes | `4fe89694b7b85fe83b27f4bd2b3dc60e2b45ce88e30e1209e94a30a5469bf48c` |
| Standalone CMake, 44,925 bytes | `ca7fd58cfb5f77df9f095e5e1e58766e11acb0ca29cb2523172ee56736729547` |
| Frozen A59 fixture, 16,743 bytes | `8a6ecd4ac9747c3596983d345afb789163ad2fff2e880db198bdcc6e31361048` |
| Generated normal CTest discovery | `e7f41b261e1108c94327415db36d7bbf21ac5431def0c37b1cdd5d3539cc18b1` |

This follow-up reviews only the new semantic test registration, its hosted
coverage, and the independently admitted two scheduling additions. A60 owns
the event-loop implementation. I deliberately did not inspect or qualify its
active `main.cpp` source, execute a native process, configure, build, or edit
the application, tests, CMake or workflow.

## One additional regression, existing native target

The [semantic-event admission](SEMANTIC_EVENT_PAINT_ADMISSION.md) and frozen
[A59 fixture](../../apps/standalone/native_tests/test_standalone_semantic_paint_boundary.py)
require actual painted semantic transitions. The fixture is added as
`test_standalone_semantic_paint_boundary`, using the already selected real
`hammond_standalone` target. It does not substitute the calibration probe or
require an additional compiled executable.

| Coverage | Previous admitted value | Inspected value |
| --- | ---: | ---: |
| Normal hosted required-name set | 44 | **45** |
| Sanitizer required CTests | 33 | **34** |
| Distinct sanitizer build targets | 31 | **31** |

Every previous required name and target mapping remains. The normal job still
discovers and executes all `test_standalone_*` tests; the new explicit required
name makes an omitted registration fail discovery. The sanitizer map adds only
the new test-to-application association. All count/uniqueness checks, generated
selection and printed totals agree. A stale step title saying thirty-three was
reported and corrected to thirty-four before this final source inspection.

The new fixture is the only source-hash inventory addition relative to frozen
A51 workflow `b572d1e3…`. Its three imported test helpers—application, MIDI replay
and workflows—were already pinned in that inventory. All eleven inline Python
blocks parse. The real-application instrumentation block is byte-identical to
the earlier admitted workflow: exact sources, six instrumented archives, flags,
runtime references, private support-library MIDI definition and calibration
probe distinction remain intact.

The sanitizer job's policy block is also byte-identical. It retains ASan leak
detection and fatal errors, fatal UBSan, and LSan exit code 23. Disabled required
tests and per-test sanitizer overrides remain rejected. No system-library
instrumentation or physical-device behavior is inferred from those checks.

## Exact commands and bounds

The new CMake command has seven arguments: Python, `-B`, the exact semantic
fixture, `--executable`, the real app, `--timeout-seconds`, and its child limit.
Normal configuration uses **12 seconds per child / 60 seconds per CTest**.
Sanitizer configuration uses **30 / 90 seconds**, through the already existing
replay-child timeout variable and the added per-test property. The workflow's
sanitizer command verifier recognizes this fixture and requires the exact
seven-argument shape and 30-second child value. The fixture itself accepts only
finite child limits in its frozen 12–30-second domain.

The normal generated metadata confirms that exact command and 12-second value,
the 60-second test property, and the existing native/standalone/workspace labels.
Actual sanitizer metadata and execution remain future hosted gates; static
conditional source inspection is not labeled an executed sanitizer discovery.

## Independently bounded scheduling delta

[A54's additional admission](ADDITIONAL_NATIVE_SCHEDULING_ADMISSION.md), SHA
`0134a37956da506a3a49595d33f42c55eb419e93fd3f8574b98bb05a6e834c55`,
permits `RUN_SERIAL TRUE` for exactly native calibration and MIDI CLI. Removing
only those two additions, their explanatory CLI comment/line wrapping, and the
new semantic registration reproduces the preceding frozen CMake bytes' digest:
`7c7e1b42825d1ecd5b9cdc75508ed44117283dade74c0d473f171d8ab2482bb4`,
44,093 bytes. Both scheduled Python fixtures still match A54's frozen identities.
Their existing workloads and child bounds are unchanged. Both normal CTest
limits remain 90 seconds; calibration retains its 180-second sanitizer limit.

I independently compared the complete prior and new generated test sets and
property maps, rather than relying solely on root's summary:

- **241 existing tests remain**, with all 241 command vectors identical.
- **Exactly one test is added**: the semantic paint boundary, producing 242.
- The only existing property deltas are boolean `RUN_SERIAL=true` for native
  calibration and MIDI CLI. Labels, environments, working directories and
  timeouts remain equal.
- App smoke, native MIDI replay and workspace replay retain their earlier
  serial properties. Together with the two additions, all five named serial
  tests have actual boolean true values.

These checks reproduce the [generated-property summary](../development/2026-11-16-heading-title-continuation/reports/semantic-generated-properties.json)
and [actual discovery](../development/2026-11-16-heading-title-continuation/reports/semantic-final-test-discovery.json).
Their recorded workflow, CMake and fixture identities match the inspected bytes.
Serial CTest properties control overlap within that invocation; they do not
reserve CPU or guarantee callback deadlines.

## Handoff

Root must retain actual native before/after, affected, complete-suite and
published-source hosted results separately. The earlier failed runs and their
unreached assertions remain failures at their named inputs. This coverage review
does not turn isolated diagnostics into a blanket pass or qualify the changed
event loop. Original A51 records remain frozen, and all real-device, display,
accessibility, physical-fidelity, whole-interface 1:1 and release gates retain
their existing boundaries.
