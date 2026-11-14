# Hosted recovery review — actual A58

## Verdict and exact source

At the recorded observation, recovered commit `6f69c68ed5bf51d77dba1ae4f75d4bc75d144747` has **nine successful jobs and three cancelled macOS jobs that never acquired runners**. Hosted qualification of the recovered macOS fixture remains pending. Each cancelled job has runner ID zero and an empty step list. These are unexecuted gates; neither a macOS fixture failure nor a repaired macOS pass can be inferred. The three workflow runs conclude failure. The cancellation cause is not established by the available primary metadata.

The reviewed tree is `daa6195fd3cfc4e56dd0d99b46972c68ae3c7e81`, parent `b1efcdfc34cde92e07f2f6bcb563fc12701dfc01`. GitHub source retrieval independently matched the repaired workspace fixture's SHA-256 `0488bc549bbe4475fac8daa4f5d69c76a58db5ca7a94f1ff7e146f7ac11c0692` over 31,885 UTF-8 bytes. The seven-file recovery changes that Python fixture, recovery documentation, a CLI flag and evidence-preservation attributes; it changes no product C++, CMake or workflow. See the [exact commit](https://github.com/tomasedisonn80/Hammond-B3-Organ/commit/6f69c68ed5bf51d77dba1ae4f75d4bc75d144747), [recovery record](../development/2026-11-14-interface-continuation/RECOVERY.md) and [bounded primary audit](../development/2026-11-14-interface-continuation/reports/a58-recovery-hosted-6f69c68.json).

A58's primary-source and hosted-status audit is complete. Acceptance of this assignment does not mean that every platform passed. This is a newly authored recovery review by the same actual A58 in wave ten; it does not claim to recover the original local review or raw evidence files.

## Exact recovered matrix, attempt one

| Workflow | Run | Executed successes | Cancelled without execution |
|---|---:|---:|---|
| CI | [43604228149](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43604228149) | 3 | macOS Release, job 132475290423 |
| Native VST3 | [43604228166](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43604228166) | 2 | macOS, job 132475290079 |
| Native standalone | [43604228118](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43604228118) | 4 | macOS MIDI ON, job 132475290118 |

All twelve job records bind to the exact recovered commit. The three macOS jobs were cancelled at 2026-11-14T14:34:10Z. A58 did not cancel or rerun them. Their advertised check-run endpoints were rejected by the connector as unsupported, so this review makes no claim about a cancellation-cause annotation.

The complete twelve-row matrix, attempt numbers, dates, job URLs and evidence limits are retained in the machine audit. Core and VST3 results in this review are job-metadata observations. Detailed primary decoded logs were inspected for the three completed standalone Release jobs and the native sanitizer job.

## Executed standalone acceptance

| Job | CTest | Native MIDI replay | Workspace replay | Actual workspace subprocesses |
|---|---:|---:|---:|---:|
| [Linux GCC, MIDI OFF](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43604228118/job/132475289818) | 38/38 | 12 methods | 6 methods | 30 |
| [Linux GCC, MIDI ON](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43604228118/job/132475290025) | 38/38 | 12 methods | 6 methods | 30 |
| [Windows MSVC x64, MIDI ON](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43604228118/job/132475290063) | 38/38 | 12 methods | 6 methods | 30 |
| macOS AppleClang, MIDI ON | Not executed | Not executed | Not executed | Not executed |

For each successful Release log, A58 checked all 38 distinct passed CTest names against the same discovered inventory, the twelve expected MIDI method success lines, all six workspace method success lines, the explicit thirty-process line, source checkout identity and package-verification assertion. The header-matrix method and synthetic MIDI/UI method both have their own successful lines. The Linux compiler is GCC 13.3.0; the Windows compiler is MSVC 19.44.35230.0. Job logs verify the expected unavailable/ALSA/WinMM package capabilities and relocated help/dummy smoke within their own hosted environment.

**Inventory correction:** the full Release selection has fourteen native-labelled tests. Earlier thirteen-name source lists covered only `apps/standalone/CMakeLists.txt`; the top-level `test_standalone_install` registration adds the fourteenth native label. All four historical b1 Release logs and the three completed recovery Release logs already report fourteen. The focused native sanitizer selection remains thirteen total suites, of which five carry the native label. This correction changes no historical pass/failure result.

The exact repaired source adds two original-prefix invocations at each of seven header sizes: a startup-only prefix and a first-Upper-note prefix. These add fourteen processes to the existing sixteen. The full scripts retain their original events and timings, exact 2 On/2 Off counts, six view transitions, canonical Save and release assertions. Every full-run observation is checked against the literal applied-command state; the separately completed first-Upper prefix supplies evidence for a state that can fall between full-run samples. Passing methods qualify those assertions in the cited executed jobs. A58 has not independently recovered individual prefix state files, BMPs or diagnostics during this cloud audit.

## Native sanitizer and leak evidence

The recovered [native sanitizer job 132475290037](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43604228118/job/132475290037) passes **13/13 selected interface suites** in 245.54 seconds. Five are native-labelled. Its decoded log includes actual GCC/G++ compile commands using `-fsanitize=address,undefined -fno-omit-frame-pointer`, the sanitizer-enabled configuration with MIDI OFF and pinned SDL C sources, and these runtime options:

```text
ASAN_OPTIONS=detect_leaks=1:halt_on_error=1
UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1
LSAN_OPTIONS=exitcode=23
```

The instrumented-object/archive/runtime enforcement step, exact thirteen-gate discovery/CTest step and source/SDL reverification step all completed successfully. No sanitizer diagnostic was found in the executed CTest section. The report preserves primary excerpts and the exact decoded UTF-8 log hash. The uploaded artifact's API digest agrees with its primary upload log, but no current ZIP was downloaded or independently rehashed during recovery. This supports the selected hosted gate with leak checking enabled; it does not establish whole-product or system-library leak freedom.

The historical [cdb native sanitizer job 132455309517](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43597589820/job/132455309517) remains **13/13**, 244.67 seconds, with the same leak policy and five native-labelled suites. Its raw decoded-log SHA-256 is `0d7d598bbb261e571c1a4029545f8fa367cd33c8b47f90adc668ba45cbc47b61`. The retained primary connector response was re-extracted during recovery. Before the workspace interruption, A58 independently downloaded and rehashed its 125,978-byte artifact, verified 196 SDL C plus 44 project C++ selected objects, thirteen runtime-link records, source hashes and JUnit zero failures/skips. That historical inspection is preserved with its original identity; its ZIP and local reports are unavailable now. A41's separate local LeakSanitizer attach blocker and ten-pass/three-timeout attempt remain historical failures.

## Original macOS failure remains preserved

At `b1efcdfc34cde92e07f2f6bcb563fc12701dfc01`, eleven jobs passed and the [macOS standalone job 132467248056](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43601574718/job/132467248056) failed **37/38**. The [new historical recovery report](../development/2026-11-14-interface-continuation/reports/a58-recovery-checkpoint6-primary.json) retains all twelve identities, the original trace and observed samples.

The failing header-matrix subtest was 1399×820. It expected an initial Upper-only sampled state between empty and Upper+Lower, but no such sample was copied. Both note-down commands were already submitted by the 356 ms observation after a preceding sample at 53 ms; applied sequence 7 appeared with both notes held at 440 ms. This supports the observation-gap diagnosis and does not demonstrate a lost note. Assertions after the failed held-state comparison were not reached. The previously repaired synthetic MIDI/UI method passed, while its containing workspace suite and job failed. A fresh primary-log retrieval during recovery matched the original 699,663-byte SHA-256 `ea124243de963a5c72c9756cc9cc55cd141264b9e87ec30a7319e7302db5bb9c`.

The new prefixes are new fixture evidence. They are not described as executions or saved files from that historical macOS job. A later macOS pass must be recorded at its own exact source and attempt.

## Retention and next gate

The original 137-file staged candidate `655b1f17577af95ea2c5cacea9eacfa60088d341` was never uploaded. The recovery commit and these reports do not claim to reproduce that candidate. Raw log hashes cover UTF-8 bytes including BOM and original CRLF; parsing normalization does not replace or rewrite raw evidence.

The remaining platform evidence requires fresh macOS execution, including full standalone 38/38 with six workspace methods and thirty actual native subprocesses. Root will publish final recovery records and a strict Linux completion-checker step with the unchanged exact fixture. That final head's separate matrix supplies the bounded fresh macOS opportunity and strict-checker execution. No retry or cancellation of these recovered attempt-one workflows is requested or performed by A58. The first attempt's nonexecution remains preserved. A58 owns only evidence blobs; root owns tree, commit and reference publication.

Dummy-driver synthetic replay, software rendering, package assertions and leak-enabled selected suites do not close real-device/DAW, native-accessibility, real-time timing, literal reference-equality, physical-model or release-rights gates.
