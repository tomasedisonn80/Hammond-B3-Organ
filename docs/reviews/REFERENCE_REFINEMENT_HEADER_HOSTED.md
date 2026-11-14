# Published header: exact-source hosted qualification

**All twelve jobs passed at published source
`0881d1f4c5a26ce9c75dda7a3adde46382e5ab6b`, tree
`f8144b771cda1264a8788f8297f5bfec999f4a08`.** A56 independently fetched all
three workflow records, all twelve job/step records and every decoded primary
job log. Each run is a completed successful push run on attempt 1; every job
log prints the exact checked-out commit. This is the first retained hosted
qualification of the accepted measured header and its expanded material test.

The [machine audit](../development/2026-11-14-reference-refinement/reports/A56-published-header-hosted-audit.json)
retains exact log hashes, toolchains, test counts, required gates, source
comparisons and diagnostics. The
[numbered primary extracts](../development/2026-11-14-reference-refinement/reports/A56-primary-log-excerpts.txt)
include every CTest result line and selected identity, numerical, material,
policy and warning lines. The full decoded logs remain scratch intermediates;
no original ZIP, instrumented binary or package payload was downloaded by A56.

## Completed matrix

Times below are each job's reported CTest wall time, not build time, callback
deadlines or an across-platform performance comparison.

| Workflow / configuration | Exact job | CTest result | Seconds |
| --- | --- | --- | ---: |
| CI / Linux GCC Release | [132605474816](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43646527300/job/132605474816) | **138/138** | 106.54 |
| CI / macOS AppleClang Release | [132605474588](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43646527300/job/132605474588) | **138/138** | 147.80 |
| CI / Windows MSVC Release | [132605474823](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43646527300/job/132605474823) | **138/138** | 244.01 |
| CI / Linux GCC Debug ASan + UBSan + leaks | [132605474892](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43646527300/job/132605474892) | **138/138**, named quarantine exception below | 272.44 |
| Native standalone / Linux MIDI OFF | [132605475127](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43646527323/job/132605475127) | **41/41** | 215.36 |
| Native standalone / Linux MIDI ON, ALSA | [132605475146](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43646527323/job/132605475146) | **41/41** | 253.54 |
| Native standalone / macOS MIDI ON, CoreMIDI | [132605475094](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43646527323/job/132605475094) | **41/41** | 244.62 |
| Native standalone / Windows MIDI ON, WinMM | [132605475118](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43646527323/job/132605475118) | **41/41** | 285.97 |
| Native standalone / Linux Release ASan + UBSan + leaks, MIDI OFF | [132605474865](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43646527323/job/132605474865) | **16/16** | 278.47 |
| Native VST3 / Linux | [132605474498](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43646527347/job/132605474498) | **8/8**, SDK validator **47/47** | 4.96 |
| Native VST3 / macOS | [132605474721](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43646527347/job/132605474721) | **7/7**, SDK validator **47/47** | 3.78 |
| Native VST3 / Windows | [132605474799](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43646527347/job/132605474799) | **7/7**, SDK validator **47/47** | 4.68 |

Each CTest total matches a complete ordinal sequence and unique test IDs/names,
with every individual result passed. All four core name sets match; all four
native Release name sets match. The new core count includes
`python_test_refinement_session`, the checker regression suite. It is separate
from strict verification of this session's eventual sixty accepted records.

## Header and required native evidence

All five native jobs report **1,071 material checks, zero failures**:
**901 legacy checks plus 170 header checks**, across **88 frames** with 88
state checks and 88 clip frames. Their exact published painter SHA-256 is
`f323c8c2f5529b03c25deccb74f482d8b6312487492a45d14b94ef0e24cfbb6a`;
material fixture SHA-256 is
`66963058652bd0673a043e03f342c94d71fd3c07e2f37a0d1d94093cc4d4a134`.
This extends the earlier 26ff fixture's 901 checks/56 frames and does not
retroactively change that result.

Each native log also passes the independent **78-layout** acceptance with
11,466 playing-key records, 5,304 control records including 1,872 presets, and
the **six-frame pending/acknowledged harness with 947 assertions**. The latter
records frame clocks 32/32 and publications 6/8. These are software-surface
observations with no application window or audio device in those harnesses.

Release installation guards verify 15 installed files with MIDI OFF and 19
with MIDI ON, followed by relocated help, a 600 ms dummy-device smoke and
archive-byte comparison. A56 observed those successful hosted steps and their
primary output; it did not independently download or inspect the payloads.

## Numerical and sanitizer scope

Every core job passes native rotary motion, propagation and repaired allocation,
both independent Python native-probe acceptance gates, and rotary profile and
reference gates. Windows allocation passes in **0.17 seconds**; Linux core
sanitizer allocation passes in **0.57 seconds**. The repaired fixture SHA-256
is unchanged:
`022845759fe2e604ad4c8003dc0acf4e2b693d79933da86e25a0ac8e0f9f39d7`.
The numerical sources, headers, probes, reference tools and frozen contracts
match the preceding A44-qualified inputs. Passing core stdout is suppressed,
so detailed workload counts remain the retained A27/A38 evidence for that
identified source, rather than newly printed measurements in these logs.

Both sanitizer jobs retain these exact defaults:

```text
ASAN_OPTIONS=detect_leaks=1:halt_on_error=1
UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1
LSAN_OPTIONS=exitcode=23
```

The core suite retains one pre-existing explicit exception:
`test_standalone_midi_backend_quarantine` sets
`ASAN_OPTIONS=detect_leaks=0:halt_on_error=1` for injected failed-close cases
that intentionally retain callback contexts until process exit. **138/138 does
not mean every individual core test enabled leak detection.** Ordinary backend
destruction, all required rotary gates and all sixteen selected native gates
retain leak checking; the quarantine gate is outside the selected sixteen.

The successful native instrumentation step requires ASan/UBSan and frame-pointer
flags on all selected project C++ and pinned SDL C objects, nonempty object
files, sanitizer references in four archives, and sanitizer link flags/runtime
dependencies for all sixteen executables. Discovery requires exactly sixteen
unique built commands, rejects disabled tests and sanitizer environment
overrides, and retains `--no-tests=error`. Existing raster timeouts remain
180/360/300 seconds and inspection/material timeouts 60/60 seconds. No waiver,
new exception or numerical-budget relaxation was introduced. System libraries
are outside the rebuild, and missing rotary probes fail rather than skip.

## Actual tools and retained diagnostics

| Runner family | Compiler | CMake / CTest | Python |
| --- | --- | --- | --- |
| Ubuntu 24.04 x64 | GCC **13.3.0** | **3.31.6** | **3.12.16** |
| macOS 15 arm64 | AppleClang **17.0.0.17000013** | **4.4.5** | **3.12.10** |
| Windows 2022 x64 | MSVC **19.44.35230.0**, toolset directory **14.44.35207** | **3.31.6** | **3.12.10** |

Native dependency checks identify SDL2 **2.32.10**, commit
`5d249570393f7a37e037abf22cd6012a4cc56a71`; MIDI ON verifies RtMidi **6.0.0**,
commit `1e5b49925aa60065db52de44c366d446a902547b` and the locked CoreMIDI
zero-initialization preparation patch. VST3 verifies SDK **3.8.1**, commit
`3cdf9ca5d1f5b1b21e0a86832aa4abe55607bd96`, with its four locked submodules.
The report retains dependency-lock and workflow hashes.

Diagnostics remain visible: the Windows core configure reports unused
`CMAKE_BUILD_TYPE`; all five SDL builds report their minimum-CMake deprecation;
macOS SDL emits 25 deprecated-API warnings; Linux VST3 emits four SDK format
warnings. Windows standalone installation reports a nonfatal CMake developer
warning for `\h` in its generated Python executable path under unset CMP0010.
The installation, relocation and archive guards still complete successfully.
Windows build summaries report zero compiler warnings/errors; that does not
erase the separate configure/install warnings.

## Current candidate, history and remaining gates

The [bounded source comparison](../development/2026-11-14-reference-refinement/reports/A56-source-comparison.json)
identifies **365 unchanged published inputs** below `apps`, `assets`, `cmake`,
`data`, `include`, `plugins`, `src`, `tests` and `tools`, plus the named root
build/control files. The three workflows are compared separately: standalone
and VST3 remain identical, while A55 adds the future strict refinement checker
step to the unpublished `ci.yml` candidate. Documentation, session records,
reports and gallery files are excluded from this equality claim.

**The 0881 run does not execute A55's future strict current-session sixty-record
CI gate.** Its Linux core job executes the historical interface-session checker,
and all core jobs execute the new refinement checker regression test. Final
documentation integrity, accepted sixty-record completion, publication and
the actual final publication's hosted CI remain root's separate observations.
This audit cannot transfer the full suite's Markdown identity to later records.

[A43](../development/2026-11-14-reference-refinement/notes/A43-hosted-fixture-closure.md)
and [A44](../development/2026-11-14-reference-refinement/notes/A44-hosted-sanitizer-audit.md)
remain exact historical qualifications of 26ff. A27's local full sanitizer
process remains failed/environment-blocked at LSan thread-attach EPERM;
`2e161dc` Windows remains 135/136 with the 0.02-second allocation SEGFAULT;
f9c's six cancellations and partial Windows suite remain cancellations and
partial execution. Neither repaired pass supplies an original Windows stack
trace or changes the earlier local sanitizer policy.

Physical devices/displays, actual DAWs, native semantic accessibility,
deadlines, signing and physical cabinet fidelity remain separate gates.
Literal 1:1 visual equality remains unmet. R4 waveform work belongs to the
concurrent session; R5 audible policy, R6/Engine integration and scanner G5's
same-hertz failure are not closed by these engineering tests.
