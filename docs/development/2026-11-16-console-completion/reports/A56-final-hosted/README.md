# A56 final published-source Core qualification

All six required Core families passed on their original attempt for published commit `523c1979334b0fbb624ce120128a0b8ada078383`, tree `893441fe87859b9dbad81a5d81a453f7c96030f8`. This is the same accepted A56 worker continuation, with no additional agent credit. Root owns final acceptance and the separate native standalone/VST3 results.

The source has ordered parents `8189a49eacab5d4e6ce6c178862e83b03bdec437` and `54859886268ce83c36f359c43327f7c72a77ae82`. GitHub commit metadata and local Git objects agree. The workflow and the protected core, plugin, data and build-definition objects remain identical to the reviewed predecessor. Current P1/header/capture source inventories are 71/41/45 methods. Earlier execution results were not used as passes for this source.

## Six terminal jobs

Run: [CI 44043394024, attempt 1](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44043394024).

| Required family | Outcome | Actual gate result | Execution seconds |
| --- | --- | --- | ---: |
| [Release (Linux GCC)](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44043394024/job/133903128480) | Success | 209/209 CTests | 122.54 |
| [Release (macOS AppleClang)](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44043394024/job/133903128374) | Success | 209/209 CTests | 151.72 |
| [Release (macOS Intel AppleClang)](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44043394024/job/133903128616) | Success | 209/209 CTests | 555.07 |
| [Release (Windows MSVC)](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44043394024/job/133903128389) | Success | 209/209 CTests | 346.52 |
| [Complete R4 waveform qualification (Linux GCC)](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44043394024/job/133903128709) | Success | Full R4; 24/24 partitions | 532.16 |
| [Linux GCC ASan + UBSan + leaks](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44043394024/job/133903128309) | Success | 209/209 CTests | 332.67 |

Execution seconds are the CTest wall time, or the full R4 qualification wall time in the R4 row. Exact job/step starts, completions and durations are retained in the API payloads and admission report. The initially queued Intel job and every observation remain in the evidence. There were no retries, cancellations or replaced outcomes.

All five unfiltered CTest inventories contain the same 209 names. Each includes the twelve required registration/apron gates and five library suites, all passing. Complete original job logs and every original artifact ZIP are retained; each ZIP SHA-256 matches the GitHub artifact digest.

## Actual Python method executions

Each cell shows the hosted method count and reported unittest duration. All fifteen suite executions below ended `OK` with zero method skips, matching the exact published-source inventories.

| Core family | P1 | Header | Capture |
| --- | ---: | ---: | ---: |
| Release (Linux GCC) | 71 / 0.537 s | 41 / 0.606 s | 45 / 1.020 s |
| Release (macOS AppleClang) | 71 / 0.598 s | 41 / 0.592 s | 45 / 1.330 s |
| Release (macOS Intel AppleClang) | 71 / 2.834 s | 41 / 3.155 s | 45 / 5.855 s |
| Release (Windows MSVC) | 71 / 1.108 s | 41 / 1.560 s | 45 / 5.809 s |
| Linux GCC ASan + UBSan + leaks | 71 / 0.656 s | 41 / 0.635 s | 45 / 1.147 s |

These source/comparator suites do not substitute for the native raster workflow. Other Python suites have optional method skips, retained explicitly in `optional_internal_method_skips` and the full artifact reviews. No CTest was skipped or disabled. The Linux standard-library-only apron step passed its 25- and 14-method suites while disclosing six and two optional skips.

## Windows Unicode generator

The actual MSVC generator ran from a Unicode source checkout bound to this exact commit and tree. Its build metadata contains `/utf-8` and the intended compiled Unicode source definition. It emitted 25 JSON records and saved all 24 payloads; every payload byte count and digest matches the committed starter pack. Output is LF-only, and generation/refusal stderr is empty. A protected-source destination was refused with zero attempted or committed files, and the source pack remained unchanged. Complete command records, executable/archive identities and payload inventories are retained in `windows-unicode-generator-review.json` and the original Windows ZIP.

## Strict sanitizer and full R4 evidence

The sanitizer job built Debug with ASan and UBSan, with leak detection and halt-on-error options enabled and LSAN exit code 23. Retained compiler/linker lines prove instrumentation of Engine, LibraryModel and its test. All 209 registered tests passed. This covers the Core/headless sanitizer job; native SDL sanitizer qualification is separate.

The R4 run completed full mode with four rates and 24 partitions. Its 38,010,000 partition comparisons all matched; all 16 qualification groups passed. The strict report-admission suite passed 14 methods. Original native stdout/stderr digests match the retained receipt, native totals match the qualification, and source commit/tree are unchanged before and after. The artifact retains selected decimal crosschecks and static-grid evidence. Transaction lifecycle, R5 audible policy, R6 device deadlines and physical fidelity remain separate gates.

## Retention and preserved history

`core-523c1979-admission.json` is the source-bound six-job admission record. `source-review.json` and `source-method-inventory.json` bind the workflow and reviewed source. `job-*.log.gz` preserve complete connector log text losslessly, including BOM/carriage returns; corresponding receipts record raw and compressed hashes and round-trip verification. `artifact-*.zip` are the original archives with receipt and entry-level reviews. API snapshots retain all steps, attempts and timings. `evidence-inventory.json` hashes all evidence files except itself.

All 128 prior A56 evidence files and accepted records were rehashed and remain unchanged. The original cf87 Core Windows failure remains 207/209 with its skipped Unicode generator. The d2ed native Windows 75/78 failure remains historical failure. The original local 246/247 failure and all prior source-specific results remain intact. No accepted A56 note was rewritten.

A56 performed read-only GitHub/source inspection and evidence retention, with no source changes, local product tests/builds/native execution, Git mutation or CI mutation. Literal whole-interface 1:1 remains unmet and unwaived. Real-device, display/DPI/accessibility, callback, measured physical fidelity, rights and signed-distribution limits remain separate. Any later source change requires new qualification.
