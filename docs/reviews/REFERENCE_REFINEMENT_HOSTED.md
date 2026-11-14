# Hosted fixture repair and full matrix review

**All twelve hosted jobs passed at
`26ff2fbe66a50260bd7601cbfa54c1f5d35ff3a8`, tree
`530d5fcf777003f470f64558de9e5631d31a21a4`.** A43 independently read every job's
decoded primary log, checked the complete selected CTest result set against its
reported total, and retained the exact run/job/source identities. The Windows
allocation fixture repair passes within the complete 137-test Release suite.

This qualifies the product/test/workflow source shared with
`f9c11a498ecd88886349415205fc5dccc627033e`, tree
`39ac16b12526143eee4136e4cc4a534b71013660`. The two complete Git trees differ:
26ff is a direct child containing eighteen documentation/record changes from
the concurrent waveform continuation. Independent API and local Git comparisons
agree that all **666 non-documentation entries**, including product, tests,
workflows, build definitions, dependencies and assets, are identical. Neither
audited head contains A40's later header refinement.

## Completed 26ff matrix

All rows below have job conclusion `success` and complete successful CTest
summaries in their decoded logs. Core rows cover every registered test in their
chosen preset; standalone and VST3 rows cover the workflows' selected native
acceptance sets. Counts are not interchangeable across configurations.

| Configuration | Run ID | Job ID | Tests passed | CTest seconds |
|---|---:|---:|---:|---:|
| Core Release, Linux GCC | 43644278142 | [132598497240](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43644278142/job/132598497240) | 137/137 | 100.14 |
| Core Release, macOS AppleClang | 43644278142 | [132598496957](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43644278142/job/132598496957) | 137/137 | 153.42 |
| Core Release, Windows MSVC | 43644278142 | [132598497386](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43644278142/job/132598497386) | 137/137 | 228.22 |
| Core Linux ASan/UBSan | 43644278142 | [132598497275](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43644278142/job/132598497275) | 137/137 | 268.61 |
| Standalone Linux, MIDI OFF | 43644278159 | [132598532193](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43644278159/job/132598532193) | 41/41 | 228.28 |
| Standalone Linux, MIDI ON | 43644278159 | [132598532092](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43644278159/job/132598532092) | 41/41 | 251.14 |
| Standalone macOS, MIDI ON | 43644278159 | [132598532165](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43644278159/job/132598532165) | 41/41 | 255.64 |
| Standalone Windows, MIDI ON | 43644278159 | [132598532058](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43644278159/job/132598532058) | 41/41 | 264.68 |
| Standalone Linux ASan/UBSan | 43644278159 | [132598531735](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43644278159/job/132598531735) | 16/16 | 272.49 |
| Native VST3, Linux GCC | 43644278198 | [132598446162](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43644278198/job/132598446162) | 8/8 | 6.89 |
| Native VST3, Windows MSVC | 43644278198 | [132598446402](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43644278198/job/132598446402) | 7/7 | 6.04 |
| Native VST3, macOS AppleClang | 43644278198 | [132598446423](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43644278198/job/132598446423) | 7/7 | 4.61 |

Every VST3 job also records **47 passed, zero failed** internal SDK-validator
checks. Those checks sit inside the selected validator CTest case and are not
added to the CTest totals. GCC identifies itself as **13.3.0**; AppleClang as
**17.0.0.17000013**; MSVC as **19.44.35230.0**, with tools under **14.44.35207**.
Windows uses the `windows-2022` image, Windows Server 2022 version 10.0.20348.

## Windows repair closure and numerical coverage

| Exact head | Run / job | Allocation fixture | Full core Release result |
|---|---|---|---|
| `2e161dc3a60fc3442051799574feed37bffbfc5c` | 43641918154 / 132591143228 | SEGFAULT, 0.02 s | 135/136; failure preserved |
| `f9c11a498ecd88886349415205fc5dccc627033e` | 43643877469 / 132597198333 | Passed, 0.15 s | Cancelled after 69/137 passed results |
| `26ff2fbe66a50260bd7601cbfa54c1f5d35ff3a8` | 43644278142 / 132598497386 | Passed, 0.14 s | 137/137 in 228.22 s |

The completed Windows build reports **zero compiler warnings and zero errors**.
Its allocation source matches A38's accepted SHA-256
`022845759fe2e604ad4c8003dc0acf4e2b693d79933da86e25a0ac8e0f9f39d7`.
The complete numerical result includes `test_rotary_motion`,
`test_rotary_propagation`, `test_rotary_propagation_allocation`,
`python_test_rotary_motion_acceptance`,
`python_test_rotary_propagation_acceptance`, `python_test_rotary_profile` and
`python_test_rotary_reference`. All seven also passed in Linux/macOS Release and
the core sanitizer job. Consequently the earlier unfinished Windows independent
oracle qualification is now observed on actual MSVC for this exact source.

Successful core CTest output suppresses passing-test stdout, so A43 does not
claim a separately captured Windows allocation JSON payload. A38's unchanged
workload/source evidence and this actual test pass remain separate observations.
The repaired pass closes the observed fixture regression; it does not create an
original Windows crash stack trace or prove the exact original failure mechanism.

## Preserve the f9c cancellations

The original f9c workflows are **six successful and six cancelled jobs**. Core
Linux/macOS Release and the core sanitizer each completed 137/137; VST3 completed
8/8 on Linux and 7/7 on Windows/macOS. The cancelled Windows core run recorded
69/137 passed results. Standalone Linux OFF/ON and macOS ON each recorded 36/41;
Windows ON recorded 28/41; native sanitizer recorded 11/16. Every observed result
passed, but none of these incomplete suites is counted as completed.

The f9c run IDs are CI **43643877469**, standalone **43643877502** and VST3
**43643877495**. Cancellation occurred around 21:43:10–15 UTC, after the direct
child's workflows started at 21:43:02 UTC. This is consistent with the unchanged
`cancel-in-progress: true` configuration. The logs do not identify a human
requester; no such attribution is made.

## Diagnostics, sanitizer limits and retention

Windows configure reports that `CMAKE_BUILD_TYPE` is unused by its selected
multi-configuration generator. This is separate from the clean compiler build.
Linux VST3 records four integer-format warnings in the locked external SDK;
macOS standalone records SDL deprecation warnings. These warnings are retained
instead of describing the entire matrix as warning-free.

Both sanitizer jobs completed their actual selected suites. The core job's
default is `ASAN_OPTIONS=detect_leaks=1:halt_on_error=1`; the pre-existing
`test_standalone_midi_backend_quarantine` CTest property intentionally sets
`detect_leaks=0` for retained failed-close callback contexts. Therefore this
review does not claim exception-free leak checking across all 137 core tests.
A44 separately audits instrumentation, admission guards and the rotary/native
selected gates. A27's original local LSan thread-attachment EPERM result remains
unchanged historical evidence.

The [A43 report](../development/2026-11-14-reference-refinement/reports/A43-hosted-fixture-closure.json)
records all 24 jobs across both heads, exact decoded-log hashes, build/test
diagnostics, individual numerical results, selected-test ID coverage and
source comparisons. The
[26ff extracts](../development/2026-11-14-reference-refinement/reports/A43-26ff-primary-log-excerpts.txt)
and [f9c extracts](../development/2026-11-14-reference-refinement/reports/A43-f9c-primary-log-excerpts.txt)
retain numbered primary lines. Full decoded Windows logs are retained for
[26ff](../development/2026-11-14-reference-refinement/reports/A43-26ff-windows-release-decoded.log)
and [f9c](../development/2026-11-14-reference-refinement/reports/A43-f9c-windows-release-decoded.log).
The existing [2e failure log](../development/2026-11-14-reference-refinement/reports/root-windows-2e.log)
was hash-checked against A38 and remains untouched. These are UTF-8 encodings of
connector-decoded job logs, not original artifact ZIP bytes. No binaries or
workflow artifacts were downloaded.

Future source changes need their own applicable acceptance. These results do
not qualify A40's header, physical fidelity, connected rotary audio, real
controllers/audio devices/DAWs, callback deadlines, semantic accessibility,
release signing or literal reference-image equality.
