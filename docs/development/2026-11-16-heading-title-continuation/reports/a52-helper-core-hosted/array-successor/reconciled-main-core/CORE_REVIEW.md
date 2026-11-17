# Reconciled main523 Core review — A52

**All six Core families qualified at the exact incoming source**, on their original attempt. [Run 44043394024](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44043394024), attempt 1, completed successfully at `2026-11-17T08:23:22Z`. The final main ref, run metadata, six job records and every actual source stdout identify `523c1979334b0fbb624ce120128a0b8ada078383`, tree `893441fe87859b9dbad81a5d81a453f7c96030f8`. Its parents are `8189a49eacab5d4e6ce6c178862e83b03bdec437` and `54859886268ce83c36f359c43327f7c72a77ae82`.

This is the same accepted A52 worker, with no new worker credit. [core-review.json](core-review.json) is the aggregate receipt, SHA-256 `e96d180e0a1adc8c4a4c199c321cdc39d0361a5b60d300b584ba8155e8275028`.

## Actual source-specific outcomes

| Required Core family | Job | Verified execution |
|---|---:|---|
| Release (Linux GCC) | 133903128480 | 209/209; 122.54 s |
| Release (macOS AppleClang) | 133903128374 | 209/209; 151.72 s |
| Release (macOS Intel AppleClang) | 133903128616 | 209/209; 555.07 s |
| Release (Windows MSVC) | 133903128389 | 209/209; 346.52 s |
| Linux GCC ASan + UBSan + leaks | 133903128309 | 209/209; 332.67 s |
| Complete R4 waveform qualification (Linux GCC) | 133903128709 | 14 admission methods; full pass, 532.158836296 s |

Five full CTest suites each report 209 distinct passing tests, with identical name sets and all twenty required registration/apron and affected Python/Library gates. The 1,045 passing rows are observations across configurations. Intel's complete original log records 555.07 seconds and success; its longer active interval was never classified as a failure, retry or scheduler diagnosis. All six jobs had real assigned runners and completed their actual required steps. No cancelled or queued job was counted as a pass.

Linux used GNU 13.3.0, CMake/CTest 3.31.6 and Python 3.12.16 on printed x86_64. ARM used AppleClang 17.0.0.17000013, CMake/CTest 4.4.5 and Python 3.12.10 on printed arm64/macOS 15.8.2. Intel used the same AppleClang version, CMake/CTest 4.4.2 and Python 3.12.10 on printed x86_64/macOS 15.7.9. Windows used MSVC 19.44.35230.0, CMake/CTest 3.31.6 and Python 3.12.10 on printed AMD64/Windows Server 2022. Sanitizer/R4 logs identify GNU 13.3.0 and x64 Python installation paths but do not print a direct machine measurement.

## Five incoming source changes

The independently accepted [source review](incoming-source-review.json) records the exact five Python/tool paths differing from 548; C++ fixtures, production code, CMake and workflows are unchanged. Header comparator tests increase from 32 to 41 declared methods, and P1 tests from 64 to 71. Every original test class and method remains AST-identical. These are source-declared method counts, distinct from the actual 209 registered CTests; no local unittest/native execution was performed by A52.

The native title/header readers replace the single active fixture pin with two explicitly frozen whole-file variants. Indexed input must contain exactly one canonical array block, exclude the old block, reverse to the independently pinned original whole file, and match the complete indexed identity. Both fixtures remain byte-identical to 548. Final source-drift checks compare the actual admitted identity. Existing typed equality, copied-state validation, numerical screens, density checks, stream caps, workloads and native deadlines remain intact. The P1 comparator retains its audit body, original summary fields and exit predicate; failure-only stdout now includes at most 8 bounded diagnostic entries, with 160-character check names and 512-character details.

## Sanitizers and scope limits

[The complete-log sanitizer audit](sanitizer-command-audit.json) finds 160 compile commands and 119 links, all with address/undefined instrumentation; every compile retains frame pointers, including LibraryModel. Actual CTest environment is `ASAN_OPTIONS=detect_leaks=1:halt_on_error=1`, `UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1`, and `LSAN_OPTIONS=exitcode=23`. The pre-existing intentional `test_standalone_midi_backend_quarantine` leak exception remains unchanged and explicit; its per-test environment is not printed by nonverbose CTest.

Linux's separate standard-library exercise has 25 art methods with 6 optional Pillow skips and 14 raster methods with 2 optional NumPy skips. Those skipped methods remain unqualified by that exercise. Windows additionally completed the actual Unicode starter generator with 24 committed file events and a zero-write protected-path refusal. R4 ran its 14 admission methods and actual full qualification, reporting full mode, success and no failures. Its uploaded qualification JSON was not independently downloaded.

## Retention and preservation

[The retention manifest](retention-manifest.json) binds all six complete decoded logs: **2,724,773 bytes / 17,443 lines**, preserved in **280,409 gzip bytes**. Compression uses empty filenames and mtime0; every stream was decompressed and hash-verified. No complete log was truncated. [All six artifact comparisons](artifact-upload-comparison.json) match actual log-upload IDs, names, sizes, digests and exact-source API metadata. The ZIP bodies were not downloaded or inspected. A single direct-job metadata response lacked a structured JSON body; the already-used run-jobs API then supplied complete terminal metadata. This acquisition limitation did not become a CI failure claim or retry.

[All 148 earlier frozen A52 files remain unchanged](prior-evidence-verification.json), including the 548 Core review and final-publication safety note. Original failures and source-specific results retain their actual commits and attempts. This new Core qualification does not automatically qualify a later documentation commit, standalone/VST3 workflows, whole-interface reference-photo 1:1, or physical audio/MIDI hardware. Root owns reconciliation/publication; A52 made no native/build/test invocation, source change, CI retry or remote mutation.
