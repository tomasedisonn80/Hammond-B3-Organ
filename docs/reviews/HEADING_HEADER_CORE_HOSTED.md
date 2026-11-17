# Heading and header Core CI observation

**All six required Core CI families pass on the first attempt at published
commit fba1911259346bfc6fd3ba7ec78b5cf6c4d1a6b2.** A52, 17 November 2026 UTC.
The [actual run](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44016021552)
is completed/success, attempt 1. Every required job acquired a runner and
executed. There are no failed or cancelled Core jobs at this source and no
retry. This review does not qualify later source changes or the separate
standalone/VST3 workflows.

The [source-bound report](../development/2026-11-16-heading-title-continuation/reports/a52-core-hosted.json)
and [final API observation](../development/2026-11-16-heading-title-continuation/reports/a52-core-hosted/core-fba1911-attempt1-final.json)
retain job IDs, actual runner assignment, complete step outcomes, source/tool
observations, every CTest outcome and complete losslessly compressed job logs.
The original preparation review, report and note were independently checked
against their [immutable archive](../development/2026-11-16-heading-title-continuation/reports/hosted-preparation-archive.json)
before these current records were completed.

## Exact source

A52 independently fetched the published Git commit through the connected
read-only API: tree **b62f212300d75633346ab8fc5ffdd722255fe00a**, with parents
**9d60dbf462a90fe422fd4e69757fe202264acb7c** and
**835755a9069c25ce55bc2c231547458b4b3ffce4**. These match the
[root publication receipt](../development/2026-11-16-heading-title-continuation/reports/source-publication.json).
The workflow was fetched at that exact SHA, with SHA-256
**d35b85df082bfa51d0fb71ba698d0cd16819b5cab0858f78cb03c34df68e7daa**
and Git blob **295897e4b960f0fdc7fe55ba55e6cad5e23c2501**.
All six API jobs bind the same head SHA and attempt; each complete log also
records that SHA as actual revision output. No historical successful run or
moving default-branch read supplies this qualification.

## Actual results

| Required family and job ID | Observed compiler/platform | Executed result |
| --- | --- | --- |
| Linux Release — 133814025466 | GNU 13.3.0, x86_64, Ubuntu 24.04 runner | **202/202 CTests**, 108.64 s |
| macOS Release — 133814025572 | AppleClang 17.0.0.17000013, macOS 15.8.2, **arm64** | **202/202 CTests**, 171.96 s |
| Intel macOS Release — 133814025534 | AppleClang 17.0.0.17000013, macOS 15.7.9, **x86_64** | **202/202 CTests**, 446.55 s |
| Windows Release — 133814025483 | MSVC 19.44.35230.0, Windows Server 2022, AMD64 | **202/202 CTests**, 336.91 s; actual Unicode generator checks pass |
| Linux ASan + UBSan + leaks — 133814025396 | GNU 13.3.0, Debug with actual sanitizer compile/link flags | **202/202 CTests**, 262.99 s |
| Complete R4 waveform — 133814025154 | GNU 13.3.0, separate Release qualification | **14 report-admission tests pass**; actual full experiment passes in **533.89119289 s**, with an empty failure list |

The five CTest jobs each have 202 distinct recorded test names and numbers,
202 passing outcomes and the complete expected ordinal range. All twelve
required registration, render, starter-pack and apron names appear in each.
The four Release jobs use the unfiltered Release preset, parallelism two,
timeout 300 and the nonempty-test guard. The sanitizer job uses the unfiltered
sanitizer preset, parallelism two, timeout 600 and the same guard. Counts come
from the actual logs; repeated platform executions are not 1,010 distinct tests.
Both macOS architectures are actual machine outputs, not deductions from labels.

The complete R4 job uses its dedicated target, so the CTest count and twelve
registration/apron inventory requirements do not apply to that job. The log
shows actual probe compilation, the full-mode command with its 1,500-second
experiment bound, a pass result and completion of the full target. The 14
report-admission self-tests are separate from that executed experiment.

## Instrumentation and supplemental checks

The sanitizer log contains actual core compilation with address and undefined
behavior instrumentation and frame pointers, plus an instrumented renderer link.
The executed test step retains ASAN_OPTIONS=detect_leaks=1:halt_on_error=1,
UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1 and LSAN_OPTIONS=exitcode=23.
All 202 CTests complete with no reported sanitizer failure. This is executed
instrumentation evidence for these workloads, not a statement about untested
paths, physical devices or callback deadlines.

Linux's additional standard-library-only apron checks report 25 tests with
six optional-Pillow skips, and 14 tests with two optional-NumPy skips. Those
skips are retained explicitly; optional image-authoring/pixel comparisons
are not represented as executed passes. The three historical session checkers
report passed records for interface, reference-refinement and product sessions.
Those accounting checks do not close this continuation's still separately
managed sixty-worker ledger.

Windows actually compiles the starter generator in a Unicode source path with
the expected UTF-8/source-root configuration. Its log contains all 24 Saved
file records, a Complete summary with 24 attempted/committed files, and the
ProtectedPath refusal with zero attempted/committed files. The workflow then
completes its canonical payload, source-pack preservation and unchanged source
assertions. This qualifies the generator's tested Windows path behavior;
it does not execute the native SDL interface.

The R4 artifact upload completes as artifact **14298663828**, 111,722 bytes,
SHA-256 **381586a2f147b0d1dcd6f6afc182c316f9deecd9f844896eab5115b5a89c0f4d**.
The complete job log and actual full-mode result are retained. A52 did not
independently download the detailed artifact bodies, and makes no additional
per-experiment numerical claim from those unread bodies. The same distinction
applies to Windows' detailed payload-hash artifact.

## Preservation and limits

All six complete decoded job logs were inspected and retained losslessly:
**2,624,523 UTF-8 bytes**, compressed to **272,658 bytes**, with individual
byte counts, SHA-256 and verified decompression. Compact derived records retain
every CTest disposition and the decisive compiler, machine, source, policy and
supplemental outputs. Initial in-progress assignment metadata remains alongside
the final terminal observation. No account inventory, credentials or raw log
archive was dumped into the written review.

The original local 239/241 and later 240/242 failures remain unchanged. The
[separate MIDI comparison](../development/2026-11-16-heading-title-continuation/reports/a52-core-hosted/qualified-midi-failure-review.md)
retains the two timing-window failures and two exact isolated passes without
relabeling the full suite. Older T2 sanitizer failure/retry evidence remains
source-specific. The preparation archive and all original diagnosis artifacts
are preserved.

Root owns any subsequent Windows native-fixture correction, publication and
source-equivalence admission. This Core result is bound to fba1911 alone.
Standalone and VST3 acceptance remain with their assigned owners. Physical
Hammond/Leslie fidelity, live model integration, devices/DAWs, callback deadlines,
native accessibility and literal whole-interface 1:1 remain separate open gates.

A52 performed no build, native execution, source/workflow edit, retry, external
message or remote mutation. Root can accept this scoped delivery, use its final
note hash in the actual ledger, and publish the evidence/documentation closure
after resolving the other source-specific hosted work.
