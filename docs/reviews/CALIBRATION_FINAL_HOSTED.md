# Final hosted qualification of the calibration toolchain

## Result and source boundary

All **ten hosted jobs completed successfully** for published commit
[`d7f6100010eb4cdd028ec93000cd9e893ac6d190`](https://github.com/tomasedisonn80/Hammond-B3-Organ/commit/d7f6100010eb4cdd028ec93000cd9e893ac6d190),
tree `0140c737de4db28288b118744c2beef57976697f`. The four core configurations each pass **106/106 CTest suites**;
native standalone passes **14/14** on Linux, macOS and Windows; VST3 passes
**8/8** on Linux and **7/7** on macOS and Windows.

Assignment **55**, `/root/cal_w10_a55`, independently observed these exact
completed jobs, retrieved every full decoded job log, and downloaded all four
core diagnostic ZIPs. Final metadata observation: **2026-11-14 01:17:19 UTC**.
The [assignment note](../development/2026-11-13-calibration/55-final-hosted.md)
retains exact identities, complete capture-method counters and the audit procedure.

This source includes the descriptor-sized metadata allocation change, new
metadata/graph/CLI acceptance suites, actual executable stdout/stderr delivery
repair, and the literal binary-copy installation fixture. Its 22 selected
production/test/build/workflow inputs equal the independently retained
`48a19074b7a99ab6a50ea1e29c1114d5ba95fc0a` source. Every changed path between
that full local 106-suite source and the hosted revision is documentation or a
development record. The [coherent local gate](CALIBRATION_WAVE8_INTEGRATION.md)
keeps its own execution and published equal-tree mapping.

The concurrent `7ec79fb1` closure concerns the prior 103-suite source. It is a
preserved ancestor, not a substitute for this new hosted qualification. The
historical [3b0979b failure](CALIBRATION_HOSTED_PACKAGE_RECHECK.md) remains a
failed Windows fixture observation with its own exact source and later repair.

## Completed platform matrix

All three runs are push-triggered attempt 1, created at 2026-11-14T01:09:54Z:
[CI](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43538885659),
[native standalone](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43538885648),
and [native VST3](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43538885785).
Elapsed values below are actual CTest totals, not workflow duration or a
performance comparison between machines.

| Configuration | Actual job | Result | CTest elapsed |
| --- | ---: | --- | ---: |
| Linux Release | [132274559239](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43538885659/job/132274559239) | 106/106 passed | 67.65 s |
| macOS Release | [132274559424](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43538885659/job/132274559424) | 106/106 passed | 109.52 s |
| Windows Release | [132274559492](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43538885659/job/132274559492) | 106/106 passed | 193.57 s |
| Linux ASan/UBSan/leaks | [132274559498](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43538885659/job/132274559498) | 106/106 passed | 216.51 s |
| Standalone Linux | [132274499329](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43538885648/job/132274499329) | 14/14 passed | 77.50 s |
| Standalone macOS | [132274499513](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43538885648/job/132274499513) | 14/14 passed | 81.01 s |
| Standalone Windows | [132274499283](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43538885648/job/132274499283) | 14/14 passed | 92.39 s |
| VST3 Linux | [132274496366](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43538885785/job/132274496366) | 8/8 passed | 4.95 s |
| VST3 macOS | [132274496265](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43538885785/job/132274496265) | 7/7 passed | 4.86 s |
| VST3 Windows | [132274496494](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43538885785/job/132274496494) | 7/7 passed | 7.44 s |

The four core diagnostic JUnit files each contain exactly the same 106 test
names as the source-qualified local selection, with zero failed, disabled or
skipped **CTest entries**. Nested unittest capability skips are separate and
remain visible below. A complete CTest suite is not a claim that every optional
method body or every possible hardware path ran.

Core [CI](../../.github/workflows/ci.yml) builds before unfiltered
`ctest --preset release --parallel 2 --timeout 300 --no-tests=error` or
`ctest --preset sanitizers --parallel 2 --timeout 600 --no-tests=error`.
The native [standalone](../../.github/workflows/standalone.yml) selection is
`^test_standalone_`; [VST3](../../.github/workflows/native-vst3.yml) selects
`^(hammond_vst3_validator|test_native_)`. Their smaller counts are their actual
selections, not 106-suite runs. The recorded commands also retain JUnit output.

## Actual Windows repairs and new acceptance

The Windows core artifact binds the final source SHA and contains the real
`LastTest.log`, including the new CLI, metadata and graph suites and the
installation suite. The table below gives the actual method totals and skips.
The CLI suite launches real child interpreters with actual pipe readers closed
before launch. Its tests cover all eight executable tools, failed help/output
delivery, rejected-input stderr, both closed streams, complete saved-report and
demo preservation, UTF-8 bytes under an ASCII terminal, destination collisions,
and independent generator/legacy-validator copies. No simulated Windows result
is substituted for this hosted execution.

In the actual Windows output, pipeline **9/9 in 12.519 s**, metadata
**24/24 in 2.358 s**, graph **7/7 in 15.395 s**, and demo **43/43 in 2.546 s**
all have plain `OK` with no skips. Installation reports **16 methods in
33.402 s, OK (skipped=1)**; its one excluded method is POSIX `DESTDIR`, not the
repaired late-abort method. No metadata-lag or neighboring-platform result is
used to fill this evidence.

The new metadata suite exercises the descriptor-sized read and its original-byte,
growth, truncation, replacement, cleanup and source-context boundaries. The graph
suite independently covers 512-capture scale, all seven linkage reasons,
purpose leakage, permutations and deep ancestry. These are bounded software
cases involving recorded synthetic data, not acquired instrument captures.

The installation regression retains a foreign writer's literal
`b"preserve other writer\r\n\x00unchanged\n"` via CMake `COPY_FILE`, then
deliberately aborts after the first actual package copy. The repaired test checks
the abort, partial-copy warning, exact marker bytes and retained package contents.
Its source SHA-256 is
`c7731f8bbcec56ed65243bb483cf59031048d978ebd0b9a7582ea6a429ea3602`.
This observed Windows result closes the prior fixture's LF-versus-CRLF failure
for the retained binary-copy repair. Production installer bytes remain unchanged,
SHA-256 `b7658c5ac2083e7661dd01d6ebf1cb66ee838a73e71fa2300c6d9b1affd5f015`.

## Complete capture-method observations

Counts below are the actual unittest summaries from full `LastTest.log`, which
does not have the successful JUnit output's 1024-byte truncation. `OK (skipped=n)`
retains its reported capability counter; it must not be described as every
method body or nested subcase running without exclusion.

| Suite suffix | Methods | Linux Release | macOS Release | Windows Release | Linux sanitizers |
| --- | ---: | --- | --- | --- | --- |
| `audio` | 41 | OK | OK | OK | OK |
| `audio_admission` | 63 | OK (skipped=1) | OK (skipped=1) | OK (skipped=5) | OK (skipped=1) |
| `cli_pipeline` | 9 | OK | OK | OK | OK |
| `common` | 49 | OK | OK | OK (skipped=2) | OK |
| `comparison` | 42 | OK | OK | OK | OK |
| `corpus` | 47 | OK | OK | OK | OK |
| `corpus_admission` | 59 | OK | OK | OK (skipped=6) | OK |
| `demo` | 43 | OK | OK | OK | OK |
| `graph_scale` | 7 | OK | OK | OK | OK |
| `install` | 16 | OK | OK | OK (skipped=1) | OK |
| `job` | 81 | OK | OK (skipped=1) | OK (skipped=2) | OK |
| `metadata_read` | 24 | OK | OK | OK | OK |
| `numerics` | 19 | OK | OK | OK | OK |
| `policy` | 49 | OK | OK | OK | OK |
| `readiness` | 65 | OK | OK | OK | OK |
| `replay` | 69 | OK | OK | OK (skipped=1) | OK |
| `study` | 61 | OK | OK | OK (skipped=1) | OK |

The installation skip on Windows is the explicitly POSIX-only `DESTDIR` case.
Other platform capability skips and the separate session/reference suites are
retained in the assignment note. The earlier demo symlink-preservation repair
also retains its own actual method outcomes at this exact source.

## Native and sanitizer scope

All three standalone job logs show successful native build, fourteen-suite
acceptance, nine-file installed inventory, relocation, help, SDL dummy-driver
smoke and archive steps. Windows explicitly skips its unsupported FIFO subcase.
All three VST3 job logs show successful actual bundle build, SDK validator and
native selection, inventory, archive and upload. Each SDK validator reports
47 internal cases within one CTest entry. Linux alone selects
`test_native_realtime`; its absence in the other two native configurations is
not an executed pass there. This reviewer downloaded diagnostic ZIPs only and
did not download or execute any native product package.

Linux ASan/UBSan runs the complete 106-suite source with leak detection enabled
and leak exit code 23. The retained decoded log contains no AddressSanitizer,
UndefinedBehaviorSanitizer runtime-error or LeakSanitizer failure diagnostic.
This observation does not assert coverage of unexecuted workloads or sanitizer
instrumentation of every external library.

These gates qualify the stated software and hosted platforms. They do not
establish a physical audio device, external MIDI controller, DAW compatibility,
native accessibility acceptance, all callback deadlines, measured organ/Leslie
parameters, permissions, listening equivalence or physical fidelity. Continue
the [operating guide](../CALIBRATION_RUNBOOK.md) and the current
[handoff](../CALIBRATION_HANDOFF.md) with those boundaries intact.

## Durable follow-up

The four diagnostic ZIPs were verified against GitHub's sizes and SHA-256
digests; embedded revisions and their complete test-name sets agree. Their
hosted retention expires on 2026-11-28, so the permanent source/job identities,
outcomes, original failure context and complete nested counters are retained
here and in the assignment note. Temporary download URLs are not durable links.

Root may now record the exact successful matrix, complete the remaining real
assignments and publish the final documentation. Future code changes require
their affected new gates; this dated result must not silently qualify a changed
checkout. Assignment 55 changed only its review and note and did not trigger,
retry or cancel workflows, edit production/tests, mutate shared status or move
Git refs. Integration and final session accounting belong to root.
