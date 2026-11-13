# Final continuation platform qualification

Audit date: 2026-11-13 UTC. Reviewer:
`/root/w10_a59_final_platform_review` (continuation assignment 59).

**The corrected checkpoint passed all four hosted jobs**, each with **46 CTest
suites, 372 Python methods and zero failed, disabled or skipped tests**. This
review also retains the earlier 45-suite qualification and the intervening
Windows accounting failure. The integrator's CRLF repair closes that observed
portability defect at the named revision; it does not erase the failed run.

## Revisions and observed outcomes

| Checkpoint | Commit and published tree | Hosted run | Observed result |
| --- | --- | --- | --- |
| Enabled allocation, expanded install and console benchmarks | Commit `2046b9388f6aab1122e37646b2f20199b5c6079f`; tree `759ddcaf93be2047a5732034663e565f728fb5ad` | [43376892064](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43376892064) | All four jobs passed 45 suites and 358 Python methods. |
| Demo, handoff, separate accounting and renderer stdout repair | Commit `6bdce067ecdfa2b918113e254ed0ae706fdc9b43`; tree `6f7948c1cc83945f2ca872b96e668de3796cf8a5` | [43380337294](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43380337294) | Three jobs passed all 46 suites; Windows passed 45/46. Every job executed 371 Python methods; the Windows ledger suite failed. |
| CRLF portability repair | Commit `7469ebf759ced820cc34fc9012beff6f772e4b89`; tree `096e2cd13c5aa3fc40e996c923ed80be36b0f622` | [43380966473](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43380966473) | All four jobs passed 46/46 suites and 372 Python methods. |

All three runs are attempt 1. Every downloaded diagnostic archive's source revision
matches its run's exact head SHA. The published Git tree was checked independently
from local Git objects. A branch name, passing workflow definition or earlier run
is not substituted for a revision-specific result.

The integrator's corrected-renderer source gate used tree
`08d944734efcd1b7a8ed5a93392deabca70a178f` and passed 46/46 local Release suites in
14.68 seconds. This reviewer independently checked that its later published tree
differs only in four Markdown result records: development log, next steps, status
and the continuation README. Thirty-five selected core, build, allocation, install,
benchmark, trace and profile files in that frozen source are byte-identical to
`2046b93`. The renderer correction and new accounting tool/tests have their own
changes and gates; they are not included in that unchanged-file statement.

## Hosted jobs and complete logs

| Job | Earlier checkpoint | First 46-suite candidate | CTest elapsed seconds, earlier / candidate |
| --- | --- | --- | --- |
| Linux GCC Release | [131725355497](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43376892064/job/131725355497), 45/45 | [131736381573](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43380337294/job/131736381573), 46/46 | 29.01 / 22.42 |
| macOS AppleClang Release | [131725355621](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43376892064/job/131725355621), 45/45 | [131736381962](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43380337294/job/131736381962), 46/46 | 29.68 / 24.73 |
| Windows MSVC Release | [131725355406](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43376892064/job/131725355406), 45/45 | [131736381912](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43380337294/job/131736381912), 45/46 | 25.13 / 25.26 |
| Linux GCC Debug, ASan/UBSan/leaks | [131725355031](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43376892064/job/131725355031), 45/45 | [131736382027](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43380337294/job/131736382027), 46/46 | 51.49 / 60.77 |

These are whole test-run durations, not callback timing measurements or a speed
comparison. Complete `LastTest.log` names and outcomes were reconciled with JUnit
cases and CTest totals. The failed Windows archive also retains its exact
`LastTestsFailed.log` entry. There are no disabled or skipped tests. Expected
platform-specific configure-step skips are workflow branches, not test skips.

Five passing JUnit outputs in every archive are truncated at 1,024 bytes. Python
method totals therefore come from the complete LastTest blocks, including the
failed suite's actual `Ran 12 tests` result. Each platform has the same per-suite
method counts for its revision. The first checkpoint has 24 C++ and 21 Python
suites; the later one has the same 24 C++ and 22 Python suites. Accounting adds
12 methods, and the renderer adds one method with two stdout subcases, producing
358 + 12 + 1 = 371 executed methods. Counts are unittest methods, not subtests,
loop iterations or C++ assertions. Executed methods in a failed suite are not
reported as passing methods.

## Windows ledger failure and independently confirmed cause

Only `python_test_continuation_ledger` failed in run `43380337294`: its twelve
methods reported **three failures and three errors**. Existing DSP, ownership,
allocation, install, benchmark and evidence suites passed. In particular, all
**35 renderer methods**, including the new read-only-stdout regression, passed
on Windows. This was a separate accounting-tool portability defect.

The checker read bounded raw UTF-8 bytes without newline normalization. Windows
`Path.write_text` fixtures contain CRLF. The explicit owner-line regular expression
captured the trailing carriage return, while the identity-value expression allowed
only trailing spaces/tabs. Correct fixture identities were therefore rejected.
Several negative tests encountered that earlier rejection instead of their
intended later diagnostic.

This reviewer independently reproduced the defect using a one-complete-slot
temporary manifest against the frozen candidate: the LF note passed; the same
logical note with explicit CRLF bytes failed with `note must have exactly one
matching explicit Agent identity`. The captured owner ended in `\r`, and the
same owner matched after removing that carriage return.

The integrator owns the narrow repair: normalize CRLF only after checking the
original raw byte limit and decoding UTF-8; add a platform-independent explicit-
CRLF regression that also proves duplicate-owner rejection; and document LF/CRLF
acceptance. This reviewer inspected that patch and found the byte bounds and
owner-count semantics preserved. No DSP, renderer, profile or fixture repair is
needed for this finding. Local reproduction and inspection do not replace the
required hosted rerun.

## Actual toolchains and sanitizer instrumentation

All three audited runs recorded the same toolchain versions:

| Job | Recorded platform | Compiler | CMake / CTest | Python |
| --- | --- | --- | --- | --- |
| Linux Release | Linux x86_64, kernel `7.0.0-1017-azure`, glibc 2.39 | GCC 13.3.0 | 3.31.6 / 3.31.6 | 3.12.16 |
| macOS Release | macOS 15.8.2, arm64 | AppleClang 17.0.0.17000013 | 4.4.5 / 4.4.5 | 3.12.10 |
| Windows Release | Windows Server 2022, `10.0.20348`, AMD64 | MSVC 19.44.35229.0 | 3.31.6 / 3.31.6 | 3.12.10 |
| Linux sanitizer | Separate Ubuntu GCC toolchain record | GCC 13.3.0, package `13.3.0-6ubuntu2~24.04.1` | 3.31.6 / 3.31.6 | 3.12.16 |

The sanitizer record does not print the Release job's kernel/architecture, so that
separate observation is not attributed to it. Actual Unix compilation uses C++20
and `-Werror`; actual Windows compilation uses `/std:c++20` and `/WX`, with
MSBuild selecting Release. Its unused single-configuration `CMAKE_BUILD_TYPE`
warning does not change that explicit multi-configuration selection.

Each sanitizer build contains **39 instrumented C++ compilation commands and
29 instrumented executable links**. Every inspected compilation command includes
`-fsanitize=address,undefined` and `-fno-omit-frame-pointer`; every executable link
includes the sanitizer flags. The actual hosted test-step logs record:

```text
ASAN_OPTIONS=detect_leaks=1:halt_on_error=1
UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1
LSAN_OPTIONS=exitcode=23
```

CTest runs with `--no-tests=error`, the 600-second sanitizer per-test timeout,
and Bash `-e -o pipefail`. No AddressSanitizer, LeakSanitizer or UBSan diagnostic
appears in any of the three complete sanitizer build/test records. Sanitizer execution
qualifies the named correctness scope, not optimized callback deadlines.

## Enabled allocation, installation and benchmark scope

The complete hosted allocation output is identical across all twelve audited jobs:

| Observed API category | Accepted / rejected calls | Declared observed work |
| --- | --- | --- |
| Enabled Engine | 63 / 18 | 218,193 elapsed frames; 15,012 input events |
| Owned-input facade | 24 / 21 | 204,636 elapsed frames; 7,011 host commands; 6,879 physical events |
| Standalone ownership translation | 3 / 3 | 1,312 host commands; 1,268 physical events; no Engine time |
| Parameter APIs | 130 / 7 | All 43 mappings and invalid-input cases; rate-independent |
| Stopped rate lifecycle | 6 / 8 | Preserving/no-op transitions and rejection; no elapsed processing |

Every category reports zero observed C++ allocations/deallocations. Independent
overload calibration reports 12 allocations and 12 deallocations and is excluded
from those API counts. The 126 Engine/facade calls comprise 87 accepted and
39 rejected calls, with 422,829 elapsed frames, including disconnected work.
The [allocation contract](../REALTIME.md) accurately limits the hooks to the
recorded thread's global C++ allocation/deallocation functions. It does not
interpose general C/system allocators, locks, I/O, other threads or math-runtime
internals. No native callback, deadline or concurrency result follows.

Source inspection of `tests/test_install.py` confirms that its passing one-method
suite actually installs and checks the exact **16-file** component, moves a prefix
containing spaces, and executes every installed tool from an unrelated directory
with `HAMMOND_*` variables removed. It checks unchanged catalog/script/profile
bytes; exact same-build original and nominal-console WAVs/metrics; both metadata
exporters; CSV/SVG equality; and missing-profile failure without output. The
original prefix is absent after relocation. This qualifies the exercised
[offline component](../OFFLINE_INSTALL.md), not compiler-runtime bundling, signed
installers or native host/device operation. Same-build equality is not
cross-compiler bit-identical audio.

Each hosted `python_test_console_benchmark` executes six methods and 33 actual
CLI invocations. Maximum rational-position error is
`1.1102230246251565e-16` on every audited job. The source constructs event arrays,
output storage and observations before timing; the measured region brackets
only `Engine::process` or `process_owned_notes`. Status/count checks, contact
snapshots, checksums and statistics follow the second clock read. The four-phase
owned fixture preserves counts 122/244/122/0, and only first acquisition/final
release produce physical events. Its 244-owner peak remains below capacity 256.

The [benchmark contract](../BENCHMARKING.md) correctly preserves legacy default
`all` and gives the explicit console cases a separate schema. Counts and finite
ordered timing statistics are checked; no speed threshold is applied. Timer
overhead, scheduling, thermal/cache context, missing native underrun counters,
cold starts, contention and worst-case deadlines remain explicit limitations.
Atlas pages 379, 383, 385 and 390 were reread for these boundaries; their proposed
profiling/native-host campaign has not been inferred from an offline test pass.

## Verified diagnostic archive identities

Each ZIP was downloaded through the connected GitHub artifact endpoint. Its
actual byte length and computed SHA-256 matched GitHub metadata before inspection.
The audit read source revision, toolchain, configure/build/CTest logs, JUnit and
complete LastTest output. Hosted retention is 14 days, through 2026-11-27 for
these runs; this record retains identities and outcomes after downloads expire.
Raw diagnostic archives remain review intermediates rather than repository assets.

| Run | Artifact | ZIP bytes | Verified SHA-256 |
| --- | --- | ---: | --- |
| 43376892064 | [ci-windows-2022-release-1 / 14014433981](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43376892064/artifacts/14014433981) | 30169 | `19bdbeb5c927fe5f04d3af5f407ad93d73c4e3a8032dd6fcaa7bfc6224c06a1b` |
| 43376892064 | [ci-ubuntu-24.04-release-1 / 14014613252](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43376892064/artifacts/14014613252) | 29008 | `f618f8496c5896013b90fe9b8c865bf2b517ca41ae5544e0792b885f6e96fcf3` |
| 43376892064 | [ci-macos-15-release-1 / 14015062005](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43376892064/artifacts/14015062005) | 33589 | `d0fea6987185d54b239a137ea1d76f4ec5937d6433b3dd8411b220a7c1f1e07a` |
| 43376892064 | [ci-linux-gcc-sanitizers-1 / 14015235949](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43376892064/artifacts/14015235949) | 29666 | `112f612caff97bb1aa1d7c8fd47e84333ffd178bde8b67b145c0d57c59220e5f` |
| 43380337294 | [ci-ubuntu-24.04-release-1 / 14015533322](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43380337294/artifacts/14015533322) | 29142 | `0ab057ca3fb2a3538d7c0dd46ceb7145033ec05144eab8bad18ce07edeeffd0e` |
| 43380337294 | [ci-linux-gcc-sanitizers-1 / 14016078521](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43380337294/artifacts/14016078521) | 29812 | `1831e697204dac3d4e1e847080e9d262ab684fdcd491e20eb6c830e1f1b793c4` |
| 43380337294 | [ci-macos-15-release-1 / 14016313241](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43380337294/artifacts/14016313241) | 33722 | `cbdde27d21d14a83345b05a2b16b6e1ff9a0f162dc433e770bea4c3ca641597d` |
| 43380337294 | [ci-windows-2022-release-1 / 14016660801](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43380337294/artifacts/14016660801) | 33714 | `e9ac42bfdb7850632ed1a530325d2f680adcb8b4bff9d030903ee58db9a55ad1` |

## Corrected-checker rerun

The repaired-checker [run 43380966473](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43380966473)
completed successfully at `7469ebf759ced820cc34fc9012beff6f772e4b89`. Complete
artifacts for every platform retain **24 C++ suites, 22 Python suites and 372
Python methods**, with zero failures, disabled tests, skipped tests or failed-test
lists. Both the 13-method accounting suite and 35-method renderer suite pass on
all platforms. The explicit CRLF regression adds the thirteenth accounting method;
all other per-suite method counts remain unchanged from the first candidate.

| Job | Observed successful job | Full CTest elapsed seconds |
| --- | --- | ---: |
| Linux GCC Release | [131738364953](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43380966473/job/131738364953) | 24.66 |
| macOS AppleClang Release | [131738364737](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43380966473/job/131738364737) | 27.36 |
| Windows MSVC Release | [131738365036](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43380966473/job/131738365036) | 44.51 |
| Linux GCC Debug, ASan/UBSan/leaks | [131738364885](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43380966473/job/131738364885) | 42.82 |

The reviewer independently verified all **347 source-archive blobs, totaling
27,360,175 bytes**, against published tree
`096e2cd13c5aa3fc40e996c923ed80be36b0f622`. Beyond Markdown and assignment
records, only the checker and its permanent Python suite changed from `6bdce06`.
Native runtime, renderer, headers, build configuration and retained artifacts
remain byte-identical. The repair's complete hosted allocation counters, benchmark
33-call/rational-position output and toolchain records match the earlier observed
scope. Its sanitizer build again has 39 instrumented compiles and 29 links, with
the same actual leak-enabled environment and no sanitizer diagnostics.

| Repair artifact | ZIP bytes | Verified SHA-256 |
| --- | ---: | --- |
| [ci-macos-15-release-1 / 14015658908](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43380966473/artifacts/14015658908) | 33704 | `9960ab443490388490f3ce0dd327bedb3e2619a771bd9201e3c5250864de7350` |
| [ci-ubuntu-24.04-release-1 / 14016004493](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43380966473/artifacts/14016004493) | 29147 | `a567b492dadb833dd082a35ebd00d239a55f81a55e4e50edf82cd0ab0dc93565` |
| [ci-linux-gcc-sanitizers-1 / 14016134154](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43380966473/artifacts/14016134154) | 29801 | `4864b48ea465f5678f2a1567fd4266c341cf970a3e33c645326d71f84d2bee90` |
| [ci-windows-2022-release-1 / 14016213313](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43380966473/artifacts/14016213313) | 30706 | `89d8c71a75a130690fd12ffdfb068fcc248bb5a0e95d33f5b07fc8b87ff8640a` |

The complete per-suite method audit is retained below. The middle column counts
executed methods; its Windows accounting suite failed as described above.

| Python suite | Earlier 45-suite run | First 46-suite candidate | Corrected run |
| --- | ---: | ---: | ---: |
| `test_audio_analysis` | 15 | 15 | 15 |
| `test_capture` | 41 | 41 | 41 |
| `test_compile_profile` | 37 | 37 | 37 |
| `test_console_benchmark` | 6 | 6 | 6 |
| `test_console_catalog` | 4 | 4 | 4 |
| `test_console_evidence` | 3 | 3 | 3 |
| `test_console_trace` | 10 | 10 | 10 |
| `test_continuation_ledger` | — | 12 | 13 |
| `test_demo_bundle` | 8 | 8 | 8 |
| `test_factory_reference` | 22 | 22 | 22 |
| `test_fixture_catalog` | 2 | 2 | 2 |
| `test_install` | 1 | 1 | 1 |
| `test_model_info` | 7 | 7 | 7 |
| `test_parameter_bridge` | 8 | 8 | 8 |
| `test_parameters` | 24 | 24 | 24 |
| `test_partial_key_render` | 7 | 7 | 7 |
| `test_pedal_map` | 15 | 15 | 15 |
| `test_plot_console_trace` | 11 | 11 | 11 |
| `test_render` | 34 | 35 | 35 |
| `test_render_fixture` | 28 | 28 | 28 |
| `test_repository_integrity` | 41 | 41 | 41 |
| `test_verify_render` | 34 | 34 | 34 |
| **Total per job** | **358** | **371 executed** | **372 passed** |

## Limits and next action

The earlier [platform audit](CONTINUATION_PLATFORM_REVIEW.md) and historical
[CI repairs](CONSOLE_CI_REPAIR.md) remain intact. This review does not erase a
failure, label a skipped platform as tested, or use retained synthetic audio as
physical evidence. The nominal core and partial M3 remain distinct from runtime
pedals, scanner/AO-28/Leslie, calibration, VST3/device/UI and release qualification.

The integrator must retain actual final assignment states, verify the final
source/remote identities and observe any later published commit's CI. A later Markdown/accounting-only
publication may preserve this code/test qualification only after verifying those
unchanged bytes and the applicable documentation/record gates. The next product
implementation remains the [prepared pedal routing kernel](../M3_NEXT_GATE.md).
