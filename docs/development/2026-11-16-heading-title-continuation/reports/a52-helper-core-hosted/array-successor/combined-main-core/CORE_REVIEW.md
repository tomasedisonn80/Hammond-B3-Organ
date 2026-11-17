# Exact combined-source Core CI review — A52

**Qualified for this source and workflow:** Core run [44038196587](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44038196587), attempt 1, completed successfully with all six required jobs. Every complete job log was retained and inspected. Five unfiltered CTest suites each contain exactly **209 distinct passing results**, with identical test-name sets; full R4 qualification also completed successfully. No rerun or cancellation occurred in this run. The final API update is `2026-11-17T07:33:54Z`.

This is a follow-up by the already accepted A52 worker, with no additional worker credit. The machine-readable admission is [core-review.json](core-review.json), SHA-256 `d1588ab3b099b4c397f0929f13547d71a77b2a9db1e4218eadb398fd5e9fd6fd`.

## Source and actual execution

The tested main commit is [`54859886268ce83c36f359c43327f7c72a77ae82`](https://github.com/tomasedisonn80/Hammond-B3-Organ/commit/54859886268ce83c36f359c43327f7c72a77ae82), tree `f5f8f037af301f8b1ff5b9b4a00ff5581647667a`, with parents `d2ed03b94114e35d0caa65968d11afe896a5e9f5` and `ea02c5465b6c6a896cbbc83b55479d6f62bbf8c9`. Local Git object inspection confirms this graph. The connected final main-ref, run and job metadata all identify this exact commit. Every job also prints the source SHA in its actual log. The retained workflow is byte-identical to the source blob: 20,374 bytes, SHA-256 `d35b85df082bfa51d0fb71ba698d0cd16819b5cab0858f78cb03c34df68e7daa`.

| Required family | Actual job | Observed result | Actual toolchain and architecture evidence |
|---|---:|---|---|
| Release Linux GCC | 133886099035 | 209/209; 108.16 s CTest time | GNU 13.3.0; CMake/CTest 3.31.6; Python 3.12.16; printed `x86_64` |
| Release macOS ARM | 133886099160 | 209/209; 185.23 s | AppleClang 17.0.0.17000013; CMake/CTest 4.4.5; Python 3.12.10; printed `arm64`, macOS 15.8.2 |
| Release macOS Intel | 133886098969 | 209/209; 296.51 s | AppleClang 17.0.0.17000013; CMake/CTest 4.4.2; Python 3.12.10; printed `x86_64`, macOS 15.7.9 |
| Release Windows MSVC | 133886099088 | 209/209; 347.80 s | MSVC 19.44.35230.0; CMake/CTest 3.31.6; Python 3.12.10; printed `AMD64`, Windows Server 2022 |
| Linux ASan, UBSan and leak policy | 133886098987 | 209/209; 263.71 s | GNU 13.3.0; CMake/CTest 3.31.6; Python 3.12.16; x64 Python installation path, no direct machine print |
| Complete R4 waveform qualification | 133886098680 | 14 report-admission methods; full result `pass`, empty failures; 514.233848492 s qualification wall time | GNU 13.3.0; CMake 3.31.6; Python 3.12.16; x64 Python installation path, no direct machine print |

The ARM job was initially queued without a runner, then received runner `1000001477` and executed. Its queued state was never treated as success. [Final API evidence](final-api-observation.json) retains all runner assignments, actual step conclusions and platform-specific skipped steps.

All twelve required registration/apron gates and all eight additional affected gates passed in every full CTest suite. The latter comprise the capture-interface, header-comparator and performance-plate Python suites, plus Library model, session, storage, recall and roundtrip tests. [Requirements](requirements.json) records the exact twenty names; individual summaries retain all 1,045 result rows across the five suites. Release uses the workflow's global 300-second CTest limit; sanitizer uses 600 seconds, with source-declared individual properties preserved.

## Instrumentation, optional skips and additional execution

The [sanitizer command audit](sanitizer-command-audit.json) checks all **160 observed native compile commands and 119 link commands**. Every command includes `-fsanitize=address,undefined`; every compile retains `-fno-omit-frame-pointer`. The actual `LibraryModel.cpp` compile is instrumented. The executed CTest step prints `ASAN_OPTIONS=detect_leaks=1:halt_on_error=1`, `UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1` and `LSAN_OPTIONS=exitcode=23`.

The existing `test_standalone_midi_backend_quarantine` exception explicitly disables leak detection only for its intentional retained callback context; ASan memory and UBSan instrumentation remain. Its CMake source is unchanged from d2ed. Nonverbose CTest does not print that individual test's environment, so this report does not claim that every individual case performed leak checking.

Linux's separate standard-library exercise reports 25 apron-art methods with six optional Pillow skips, and 14 raster-checker methods with two optional NumPy skips. Those skipped image methods remain unqualified by that exercise. A passing registered CTest is not a claim that every optional internal Python method executed.

Windows additionally ran the actual Unicode-path starter generator: 24 committed file events, a `Complete` summary, and a `ProtectedPath` refusal with zero committed files. The workflow's validation step succeeded. Full R4 executed the actual `check_rotary_waveform_full` target after its fourteen admission self-tests, and its emitted result reports full mode, success and no failures. The uploaded qualification JSON itself was not downloaded for this review.

## Retention and interpretation limits

[Six complete deterministic gzip logs](retention-manifest.json) preserve **2,727,208 decoded bytes / 17,497 lines in 279,820 stored bytes**. Each gzip uses an empty filename and mtime zero; decompression, exact decoded hashes and stored hashes were checked. No complete log was truncated. [Artifact comparison](artifact-upload-comparison.json) matches every artifact's ID, name, size, digest and source to the actual upload log and API metadata. All six were unexpired at the API read. **Artifact ZIP bodies were not independently downloaded or inspected.**

CTest 4.4 omits the older “0 tests failed” phrase from its all-passed summary. The first ARM parser result and original parser remain preserved. The [additive format review](ctest-summary-format-review.json) accepts either exact all-passed form while keeping all 209 row, source and required-name checks intact. It re-read retained logs only; it changed no test predicate and invoked no native process.

All **110 prior frozen A52 files remain byte-identical**, including the accepted note and original failure evidence; see [preservation verification](prior-evidence-verification.json). Earlier Windows compilation and copied-state failures, sanitizer cancellation, Intel preset timeout, cf87 path failures and local full-suite failures retain their original outcomes.

This review qualifies only the six Core families at the stated commit and attempt. Concurrent standalone/VST3 jobs, future commits, whole-interface reference-photo 1:1 matching and physical audio/MIDI hardware acceptance require their own evidence. A52 performed read-only source/API/log inspection and wrote additive evidence solely in this assigned directory; no source edit, build, native test, CI retry or remote mutation was performed.
