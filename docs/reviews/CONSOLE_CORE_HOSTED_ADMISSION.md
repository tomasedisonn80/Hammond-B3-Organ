# Console Core hosted qualification

**A56, wave 10: all six Core jobs at published `cf87a587d0002d106e5210b57a39fd1967245a8f`
are terminal on attempt 1. Five succeed and Windows fails. Complete Core
admission remains blocked at this source.** There are no cancelled jobs,
unassigned runners or retries in the observed run. Root retains final acceptance
and publication authority.

The [complete source-specific report](../development/2026-11-16-console-completion/reports/A56-core-hosted.json)
and [immutable original-source snapshot](../development/2026-11-16-console-completion/reports/A56-core-hosted/core-cf87a587-admission.json)
retain every job's source, runner, attempt, steps, timings, log identity and
outcome. The [Core workflow run](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44030833273)
concluded **failure** at 06:36:14 UTC on 17 November 2026.

## Exact published inputs

I independently read the commit, root tree and workflow through the selected
read-only GitHub connection. The commit is
[cf87a587…](https://github.com/tomasedisonn80/Hammond-B3-Organ/commit/cf87a587d0002d106e5210b57a39fd1967245a8f),
tree `2565ac86f9d31b7ab9d24d0d5353289c2359bf12`, with ordered parents
`6287055a111dc4e2747564da3d48edc9b65e2e3e` and
`8cd9034f7e1dd21dab373f0e4ad0d1be0bab61e7`. The run and every job report that
exact head SHA. The complete primary logs also record the checked-out revision.

The [published Core workflow](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/cf87a587d0002d106e5210b57a39fd1967245a8f/.github/workflows/ci.yml)
is byte-identical to predecessor `6287055`: 20,374 bytes, SHA-256
`d35b85df082bfa51d0fb71ba698d0cd16819b5cab0858f78cb03c34df68e7daa`,
Git blob `295897e4b960f0fdc7fe55ba55e6cad5e23c2501`.

The [independent source comparison](../development/2026-11-16-console-completion/reports/A56-core-hosted/core-cf87a587-source-comparison.json)
reproduces all **81 protected files** as unchanged Git subtrees: 31 under
`include/`, 30 under `src/` and 20 under `plugins/`. The published
`data/`, root CMake and presets identities also equal the predecessor.
This preserves the reviewed 47 parameter identities, `B3CONTROLS4` writer
and readers 1–3, 91 shared free-running sources, plugin UUIDs and nominal dry
Engine. The detailed semantic boundaries remain in the
[compatibility admission](CONSOLE_COMPATIBILITY_ADMISSION.md) and
[combined source admission](CONSOLE_SOURCE_RECONCILIATION_ADMISSION.md).

## Every required family

| Exact-source job | Terminal result | Inspected execution |
| --- | --- | --- |
| [Linux GCC Release](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44030833273/job/133862108664) | Success | **209/209** CTests, **132.33 s** |
| [ARM macOS AppleClang Release](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44030833273/job/133862108689) | Success | **209/209**, **188.47 s** |
| [Intel macOS AppleClang Release](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44030833273/job/133862108770) | Success | **209/209**, **395.98 s** |
| [Windows MSVC Release](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44030833273/job/133862108675) | **Failure** | **207/209**, **219.81 s**, CTest exit **8** |
| [Linux GCC ASan + UBSan + leaks](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44030833273/job/133862108741) | Success | **209/209**, **261.05 s** |
| [Complete R4 waveform qualification](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44030833273/job/133862108317) | Success | Full mode reports **pass**, no failures, **534.283344642 s**; separate **14-method** report-admission self-test passes |

All five ordinary/sanitizer CTest inventories contain the same **209 unique
names**, including all twelve required registration/apron names and all five
new library suites. The library suites pass on every listed CTest platform,
including the Windows run that fails two other Python gates.

The Linux Release standard-library apron steps separately pass 25 and 14
methods, with their explicit **six** and **two** optional-method skips. These
skips remain disclosed. A passing registered CTest does not establish that
every internal branch or optional method ran.

The sanitizer primary log records the effective `detect_leaks=1`,
`halt_on_error=1`, UBSan stacktrace and LSan exit-code policies. It also shows
actual `Engine.cpp`, `LibraryModel.cpp` and model-test compilation using
`-fsanitize=address,undefined`, and model-test sanitizer linkage. This is
Core/headless qualification; the separate SDL/native sanitizer job belongs
to its own review.

All original limits remain: Release jobs 20 minutes with the 300-second CTest
default; Core sanitizer job 25 minutes with the 600-second default; parallelism
two and `--no-tests=error`; R4 job 35 minutes, full step 30 minutes and the
unchanged 1,500-second child limit. No retry or changed guard was used.

## Retained Windows failure

The [original failure record](../development/2026-11-16-console-completion/reports/A56-core-hosted/core-cf87a587-windows-failure.json)
and [complete compressed primary log](../development/2026-11-16-console-completion/reports/A56-core-hosted/core-cf87a587-job-133862108675.log.gz)
retain both failed CTests, all ten reported subcase errors and the skipped
downstream work.

* `python_test_capture_standalone_interface` runs 45 methods and reports
  three errors in the scale/timeout cases `(1, 12)`, `(3, 30)` and
  `(10, 12)`. The expected lookup key
  `inputs/play-dimensional.b3uireplay` raises `KeyError` at original
  test line 366.
* `python_test_compare_header_material` runs 24 methods and reports seven
  errors. Retained POSIX baseline paths miss the mock dictionary after the
  existing wrapper converts requests to native Windows `Path` values.
  The real identity fallback then raises `FileNotFoundError: [WinError 3]`
  for those historical paths.
* MSVC compilation and the twelve-name required-inventory check succeed.
  **The actual Windows Unicode-checkout generator step is skipped after the
  failed CTest step.** It has no executed result at this source.

The original Windows log preserves its **3,903 carriage-return bytes**. Its
uncompressed SHA-256 is
`c47eee99796358d5a7f0cba50883c62d63df69994e701b96d5758f68d1de3d95`.

## Separately bounded test correction

Root subsequently assigned A56 the two failing Python test files. The
[repair record](../development/2026-11-16-console-completion/reports/A56-core-hosted/windows-portability-repair.json)
and [exact patch](../development/2026-11-16-console-completion/reports/A56-core-hosted/windows-portability-repair.patch)
preserve the failed-source originals and all source identities.

The capture expectation now constructs its native relative key with `Path`
and hashes the exact native newline serialization of the replay. The newline
issue is a **source-derived latent mismatch**: the observed KeyError stopped
the Windows test before that hash comparison. No separate Windows hash-failure
execution is claimed. The existing producer's path/newline behavior is
unchanged, and all frozen returned-replay hashes remain unchanged.

The header test normalizes only the mock dictionary's lookup key. Every
original identity row—including its retained path, digest and byte count—is
still returned intact, and unknown paths retain the real identity fallback.
All 24 header test method ASTs and all top-level pins are unchanged, preserving
the previously admitted 78 refusal cases. The complete capture inventory
retains 45 methods and all existing typed/timing checks.

Exactly one authorized Linux source-only invocation of each suite passes:
**45/45** and **24/24**, without skips and with recorded inputs unchanged.
No native process, build, configure, CTest, benchmark, application capture or
CI retry was executed by A56. These two local results do not qualify Windows
or change the failed `cf87a587` outcome.

[A59 independently admitted the five frozen repair inputs](../development/2026-11-16-console-completion/reports/A59-windows-repair.json)
with no source blockers. Root's subsequent
[local qualification](../development/2026-11-16-console-completion/reports/windows-repair-local-qualification.json)
passes the fixture build and **three affected CTests**, with no failures,
errors or skips. All **587 inputs** remain stable during qualification:
five repaired inputs and 582 unchanged inputs. The P1 fixture binary is
identical before and after, and the production application remains unchanged.
The separate source suites retain their **54/45/24** method results. These
root-owned checks do not establish Windows execution. Guarded publication and
exact new-source hosted qualification remain separate gates.

## Retention and acceptance boundary

All six complete decoded job logs are retained losslessly: **2,710,212
uncompressed bytes** in **273,968 compressed bytes**, with verified gzip round
trips. Initial/final run metadata, complete final job steps, intermediate
observations and six artifact upload records are retained. Artifact IDs,
sizes and digests match the successful uploads; their bodies and detailed
numerical payloads were not independently downloaded.

The original console **246/247** local full result remains failed. Earlier
46-step/78-affected-test/15-capture observations and earlier hosted outcomes keep
their own sources and limits. Changed source receives its own qualification;
no older pass is promoted.

Standalone, VST3, real devices/display/DPI, native accessibility, callback
deadlines and retirement, physical AO-28/scanner/Leslie fidelity, rights and
signed distribution remain separate. **Literal whole-interface 1:1 remains
unmet and unwaived.**
