# Continuation platform qualification

Audit date: 2026-11-13 UTC. Reviewer:
`/root/w08_a47_platform_qualification` (continuation assignment 47).

**Both audited checkpoints passed all four hosted jobs.** The lifecycle revision
passed 39 CTest suites and 324 Python methods per job; the later partial-key,
trace and plot revision passed 43 suites and 352 Python methods per job. All
eight complete diagnostic archives have zero failed, disabled or skipped tests.
These are revision-specific offline software results.

## Exact revisions and observed jobs

| Checkpoint | Commit | Published tree | Hosted run |
| --- | --- | --- | --- |
| Sample-rate lifecycle | `53bb6e1e37eedf84f566ffb8bd9037b50f123a20` | `c88d2f0a6749cf79b7310c131b4f5d335c7d6ab3` | [43372984603](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43372984603) |
| Partial keys, console traces and SVG plots | `9a5c99a862daf26a2bab9b05613c98803727a3e7` | `a85f1bcb43d2815b6f661172f7ab394ad34bee7e` | [43375043990](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43375043990) |

Both runs are attempt 1 and were observed as completed/success. Each downloaded
archive's `ci-logs/source-revision.txt` matches its run's exact head SHA and the
revision printed by its job. The published Git trees were checked independently
from the local Git objects. No result is inferred from the current branch name.

| Job | Lifecycle run | Partial-key/trace run | Observed CTest result |
| --- | --- | --- | --- |
| Linux GCC Release | [131712857259](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43372984603/job/131712857259) | [131719446226](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43375043990/job/131719446226) | 39/39, then 43/43 |
| macOS AppleClang Release | [131712857238](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43372984603/job/131712857238) | [131719446165](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43375043990/job/131719446165) | 39/39, then 43/43 |
| Windows MSVC Release | [131712856856](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43372984603/job/131712856856) | [131719446285](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43375043990/job/131719446285) | 39/39, then 43/43 |
| Linux GCC Debug, ASan/UBSan/leaks | [131712857395](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43372984603/job/131712857395) | [131719445919](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43375043990/job/131719445919) | 39/39, then 43/43 |

The complete CTest run durations were respectively 18.12/16.37 seconds for Linux
Release, 20.85/25.30 for macOS, 29.60/42.23 for Windows, and 51.56/47.79 for the
sanitizer job. These are test-run observations, not audio callback measurements
or performance comparisons between platforms.

## Actual toolchains and instrumentation

Both revisions used the following observed tools. The workflow and presets are
byte-identical between the two audited commits.

| Job | Recorded platform | Compiler | CMake / CTest | Python |
| --- | --- | --- | --- | --- |
| Linux Release | Linux x86_64, kernel `7.0.0-1017-azure`, glibc 2.39 | GCC 13.3.0 | 3.31.6 / 3.31.6 | 3.12.16 |
| macOS Release | macOS 15.8.2, arm64 | AppleClang 17.0.0.17000013 | 4.4.5 / 4.4.5 | 3.12.10 |
| Windows Release | Windows Server 2022, `10.0.20348`, AMD64 | MSVC 19.44.35229.0 | 3.31.6 / 3.31.6 | 3.12.10 |
| Linux sanitizer | Ubuntu `ubuntu-24.04` runner image `20261111.370.1` | GCC 13.3.0, Ubuntu package `13.3.0-6ubuntu2~24.04.1` | 3.31.6 / 3.31.6 | 3.12.16 |

The sanitizer toolchain record does not print a kernel/architecture string; the
Release job's kernel record is not attributed to that separate job. Linux/macOS
verbose compilation commands use C++20 and `-Werror`. Windows commands contain
`/std:c++20` and `/WX`; MSBuild explicitly selects `Configuration=Release`.
Its unused `CMAKE_BUILD_TYPE` configure warning does not select a different build
configuration for the Visual Studio generator.

The lifecycle sanitizer build contains **36 instrumented compilation commands
and 26 instrumented executable links**. The later build contains **38 and 28**.
All inspected compile commands contain `-fsanitize=address,undefined` and
`-fno-omit-frame-pointer`; the executable links contain the sanitizer flags.
The actual hosted test step, not only the workflow text, records:

```text
ASAN_OPTIONS=detect_leaks=1:halt_on_error=1
UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1
LSAN_OPTIONS=exitcode=23
```

The step runs CTest with `--no-tests=error`, a 600-second per-test timeout and
Bash `-e -o pipefail`. No AddressSanitizer, LeakSanitizer or UBSan diagnostic was
found in the complete job and test output. No local leak-disable setting is
substituted for these hosted results.

## Complete test and skip audit

The earlier revision contains **22 C++ suites and 17 Python suites**. The later
revision retains them and adds `test_partial_key`, `python_test_partial_key_render`,
`python_test_console_trace` and `python_test_plot_console_trace`, giving **23 C++
and 20 Python suites**. In every archive the complete `LastTest.log` name set
matches the JUnit case set and the CTest console's declared total. Every LastTest
block says `Test Passed`; every JUnit file reports `failures=0`, `disabled=0` and
`skipped=0`, with no failure/skip nodes or failed-test list.

JUnit truncates five passing test outputs at 1024 bytes in each archive. Therefore
Python method totals below come from the complete `LastTest.log` blocks. Counting
only the visible JUnit output would undercount methods. The four platforms agree
on every per-suite count at each revision.

| Python suite | Lifecycle methods | Partial-key/trace methods |
| --- | ---: | ---: |
| `test_audio_analysis` | 15 | 15 |
| `test_capture` | 41 | 41 |
| `test_compile_profile` | 37 | 37 |
| `test_console_catalog` | 4 | 4 |
| `test_console_evidence` | 3 | 3 |
| `test_console_trace` | — | 10 |
| `test_demo_bundle` | 8 | 8 |
| `test_factory_reference` | 22 | 22 |
| `test_fixture_catalog` | 2 | 2 |
| `test_install` | 1 | 1 |
| `test_model_info` | 7 | 7 |
| `test_parameter_bridge` | 8 | 8 |
| `test_parameters` | 24 | 24 |
| `test_partial_key_render` | — | 7 |
| `test_pedal_map` | 15 | 15 |
| `test_plot_console_trace` | — | 11 |
| `test_render` | 34 | 34 |
| `test_render_fixture` | 28 | 28 |
| `test_repository_integrity` | 41 | 41 |
| `test_verify_render` | 34 | 34 |
| **Total per hosted job** | **324** | **352** |

These are unittest method counts, not counts of loop iterations, subtests or C++
assertions. No skipped-method or disabled-test marker appears in the complete
test output. The Windows job skips the Unix configure step; Linux/macOS skip the
Windows configure step. Those expected workflow branches and CMake compiler-probe
messages ending in `skipped` are not skipped tests.

## Verified diagnostic archive identities

Each ZIP was downloaded through the connected GitHub artifact endpoint. Its byte
length and locally computed SHA-256 match GitHub's artifact metadata. The audit
read source revision, toolchain, configure/build/CTest logs, JUnit, CMake cache and
complete LastTest output. Raw logs are not copied into the repository. The
workflow's 14-day retention expires on 2026-11-27 for these artifacts; this report
retains the observed results and identities after those hosted downloads expire.

| Run | Artifact | Verified ZIP SHA-256 |
| --- | --- | --- |
| 43372984603 | [Linux Release 14013331737](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43372984603/artifacts/14013331737) | `034095ba23b7666ffa7f6284e2357f954dab36d9d035ba79f91ebca53edf5acf` |
| 43372984603 | [macOS Release 14013670743](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43372984603/artifacts/14013670743) | `4961f084ed4f6c347f23cc9c9f653889c538adf26a3bd05e0e06c05007452a57` |
| 43372984603 | [Windows Release 14013680720](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43372984603/artifacts/14013680720) | `3cf34a6f5c372fe0fb97e0c8c2a9577caae4a0ca4156d42d48dc9f71fc007223` |
| 43372984603 | [Linux sanitizer 14013531068](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43372984603/artifacts/14013531068) | `dfba934932f36765c74596319b02d2512cd06eb0722b54f0c7883290eb6f7648` |
| 43375043990 | [Linux Release 14013533542](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43375043990/artifacts/14013533542) | `9d17cb696d7cd76af870b268b9af194ad4a82fa27f9d603243924038b22a9069` |
| 43375043990 | [macOS Release 14014058076](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43375043990/artifacts/14014058076) | `4effaec4659a2d5298a1da9e701510a9cf2ccf836910b7af024c1fd70b17528a` |
| 43375043990 | [Windows Release 14013628570](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43375043990/artifacts/14013628570) | `9f7abb599c7e0e53fe1572db902de18c9ac23aeae3f93d3248fd7307b5257643` |
| 43375043990 | [Linux sanitizer 14014336056](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43375043990/artifacts/14014336056) | `6b30f71e4407c84c26da151bf390b075af2eefb1d29b156509647abf0e08334d` |

## Historical failures and current scope

The earlier console run `43369940466` failed its producer test on Windows and
macOS because the test compared unresolved temporary paths with the producer's
canonical paths. The [retained repair review](CONSOLE_CI_REPAIR.md) records the
cause, unchanged producer/runtime behavior, and all-four-job repair pass at
`72b5062`. Both audited later checkpoints include the 28-method producer suite
and its real path-alias regression; that historical failure has not been erased
or reclassified. Older unrelated CI findings remain in
[CI_QUALIFICATION.md](../CI_QUALIFICATION.md).

The current qualified scope is the named nominal offline engine, lifecycle,
typed adapters, partial-key input, trace exporter and plotter at `9a5c99a` under
the tested runners and numerical tolerances. Same-build identity checks do not
establish bit-identical libm audio across different platforms.

Later wave-eight changes to enabled allocation instrumentation, expanded
OfflineTools installation and console benchmarking were not in either audited
revision. In particular, the one-method install suite here tests the older
renderer/profile/fixture component, not the later sixteen-file package. Those
changes require their own combined-source and hosted gate. Actual native devices,
DAWs/VST3, callback deadlines, concurrency, signed distribution, physical
calibration and scanner/AO-28/Leslie fidelity remain separate project gates.

The next integrator should qualify its exact new revision, preserve this record,
repeat complete-log count/skip reconciliation, and update the
[current status](../STATUS.md) and [continuation ledger](../development/2026-11-13-continuation/README.md).
