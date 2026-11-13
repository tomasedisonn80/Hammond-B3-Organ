# Hosted CI qualification evidence

Audit date: 2026-11-13. This report preserves the observed result for each tested
revision. The repair integration at `6c3dd8b` passed all four hosted jobs; the
earlier failed run and its local investigation remain below. A later change needs
its own qualification. See [CI.md](CI.md) for the workflow and scope.

## Revision-specific results

| Hosted run | Exact revision | Observed result |
| --- | --- | --- |
| [43361632464](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43361632464) | `b9c1cac4841db4cf7320d9571ea576bb5285aa01` | Historical first run: Linux Release and sanitizer passed 12 suites; macOS build and Windows evidence tests failed. |
| [43363048563](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43363048563) | `9c8068c95f6843dce95f7f22d729738eef8074f6` | Historical qualified baseline: all four jobs passed all 16 registered suites, including hosted leak detection. |
| [43364414017](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43364414017) | `7c2ad2089f795b2147f5fc72cf10a4542d953a8c` | Audited here: Linux/macOS Release passed 18/18; Windows Release and Linux sanitizer each passed 17/18. The complete matrix failed. |
| [43365901429](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43365901429) | `6c3dd8bc923a3c11f6b234425b056e135fbe9f4b` | Repair integration: all four jobs passed 21/21 suites; 257 Python methods per job and zero test skips. |

## Passing integration audit at 6c3dd8b

The coordinator downloaded all four complete archives for run 43365901429,
verified their ZIP digests against GitHub metadata, and checked each retained
source revision. Every JUnit document contains 21 cases, no failure and no skip;
the complete unittest output totals 257 methods per job with no skipped methods.
This adds capture, factory-reference and real install/relocation suites to the
earlier 18-suite set. The factory runtime test developed after this commit is
not included in these 21 suites.

The sanitizer job explicitly records `detect_leaks=1:halt_on_error=1`, fatal UBSan
reporting, and `LSAN_OPTIONS=exitcode=23`. All 21 suites passed. The Windows checker
diagnostic repair and executable-mutation test now have actual hosted results;
the original mutation exception remains unestablished.

| Archive | GitHub artifact | Verified ZIP SHA-256 |
| --- | --- | --- |
| Linux Release | [14009683735](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43365901429/artifacts/14009683735) | `47ac2862ea70abf248a0540e44d145d6429283027aa4d0bb51a8d82b313fbc42` |
| macOS Release | [14009629816](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43365901429/artifacts/14009629816) | `da7c55fbc2457c517e73827eafa07ce1bdca643e4d54461c2d2404959f28843d` |
| Windows Release | [14009664803](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43365901429/artifacts/14009664803) | `859d337ac2e856eb9eafcac1d4bd6516833b41a64a97b0e5ca003f21f41c5101` |
| Linux sanitizer | [14010615934](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43365901429/artifacts/14010615934) | `83d194069721f538e0f53bdce310bd186bf205660dba33e7be4af2400f9f86e8` |

## Earlier failed-run investigation

The two historical rows retain the results recorded in the
[development log](DEVELOPMENT_LOG.md); this audit independently inspected the
four complete diagnostic archives from run **43364414017**, attempt 1.
All four `ci-logs/source-revision.txt` files contain the exact `7c2ad20` revision
above. Later source, test, documentation and acquisition changes need a new run.

## Actual tools and configurations in run 43364414017

| Job | Observed platform / architecture | Compiler | CMake / CTest | Python | Result |
| --- | --- | --- | --- | --- | --- |
| Linux Release | `ubuntu-24.04`, x86_64 | GCC 13.3.0 | 3.31.6 / 3.31.6 | 3.12.16 | 18/18 passed |
| macOS Release | macOS 15.8.2, arm64 | AppleClang 17.0.0.17000013 | 4.4.5 / 4.4.5 | 3.12.10 | 18/18 passed |
| Windows Release | Windows Server 2022, 10.0.20348, AMD64 | MSVC 19.44.35229.0 | 3.31.6 / 3.31.6 | 3.12.10 | 17/18 passed |
| Linux Debug, ASan/UBSan/leaks | Ubuntu 24.04.5, x86_64 | GCC 13.3.0 | 3.31.6 / 3.31.6 | 3.12.16 | 17/18 passed |

The Linux Release platform record is
`Linux-7.0.0-1017-azure-x86_64-with-glibc2.39`. The sanitizer raw job log records
Ubuntu image `20261101.360.1`; its compiler identifies the Ubuntu package
`13.3.0-6ubuntu2~24.04.1`. The sanitizer toolchain file does not independently
print the kernel, so the Release kernel string is not attributed to that job.
Windows selected SDK 10.0.26100.0 and MSVC tools directory 14.44.35207.

Configure and verbose build logs confirm the selected compilers and actual
Release/Debug configurations. Linux/macOS compile commands use C++20 and
`-Werror`; Windows uses `/std:c++20 /W4 /WX` and reports zero build warnings/errors.
The Windows configure warning that `CMAKE_BUILD_TYPE` is unused is retained:
Visual Studio's build command explicitly selects `/p:Configuration=Release`.
All 16 sanitizer compilation commands include
`-fsanitize=address,undefined -fno-omit-frame-pointer`. The raw hosted job records
`ASAN_OPTIONS=detect_leaks=1:halt_on_error=1`,
`UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1`, and `LSAN_OPTIONS=exitcode=23`.
No local leak-disable workaround was used in that hosted job.

## Full-suite and skip audit

Each archive contains all 18 entries in `build-*/Testing/Temporary/LastTest.log`,
matching 18 JUnit test cases and the CTest console result. All four JUnit files
report `disabled=0` and `skipped=0`; none contains a skipped test node. The full
unittest output reports **195 Python methods per job**, with no skipped methods.
The expected CMake compiler-probe message ending in `skipped` is a configure
optimization, not a skipped test. No test-output skip or disabled marker was found.

| Registered CTest suite | Python methods per job | Observed outcome across four jobs |
| --- | ---: | --- |
| `test_control_io` | — | All passed |
| `test_controls` | — | All passed |
| `test_core_robustness` | — | All passed |
| `test_decimal` | — | All passed |
| `test_engine` | — | All passed |
| `test_numerics` | — | All passed |
| `test_profile` | — | All passed |
| `test_realtime` | — | All passed |
| `test_tonewheel` | — | All passed |
| `python_test_audio_analysis` | 15 | All passed |
| `python_test_compile_profile` | 37 | All passed |
| `python_test_fixture_catalog` | 2 | All passed |
| `python_test_parameters` | 19 | All passed |
| `python_test_pedal_map` | 15 | All passed |
| `python_test_render` | 20 | All passed |
| `python_test_render_fixture` | 19 | Sanitizer failed one mutation subtest; other jobs passed |
| `python_test_repository_integrity` | 41 | Windows failed three methods; other jobs passed |
| `python_test_verify_render` | 27 | All passed |
| **Total** | **195** | **9 C++ suites plus 9 Python suites in every job** |

The profile compiler's hardlink and symlink alias tests explicitly report `ok`
on every platform, including Windows. Those conditional checks were executed.
Method totals include failed methods and do not count each loop/subtest as a
separate method. Passing C++ executables are suite results, not Python method
counts. No ASan/UBSan diagnostic was printed in the retained full test output;
the sanitizer job nevertheless failed and is not qualified at this revision.

## Retained failures and the scoped repair

At the time of Agent 43's investigation, Windows failed three origin-path assertions in `python_test_repository_integrity`:
the expected `docs/guide.md` diagnostic appeared as `docs\\guide.md`. The integrator
changed the repository-relative origin to `as_posix()` and reported all 41 local
methods passing. Native Windows confirmation was then pending; the later
`6c3dd8b` hosted audit recorded above closes that scoped gate. The checker was
outside this report author's edit scope.

The sanitizer failure was
`test_modified_sources_copies_and_executable_cannot_be_success(target='renderer')`:
the manifest reported error stage `renderer`, while the test required `integrity`.
The old assertion did not print `manifest.error.message`, invocation status or
captured child output. The temporary bundle was deleted by test cleanup. Thus the
retained logs do **not** establish the underlying exception or a producer defect.
An in-place append to a recently executed binary is a plausible test-setup issue,
not an observed diagnosis of this particular failure.

The narrow [test repair](../tests/test_render_fixture.py) gives each mutation a
fresh renderer path. For the renderer scenario, it prepares a separate copy with
an actual appended byte and replaces the checked path after the real invocation.
Independent SHA-256 calculations must match the manifest's original and changed
digests. The test still requires exactly `failed` / `integrity`, false integrity
verification, and no accepted WAV record. It additionally requires a zero child
return code and complete, untruncated capture so an unrelated renderer failure
cannot be hidden by the deliberate mutation. Failure diagnostics retain the
concrete manifest error, invocation fields, actual child status and raw output.
There are no retries, sleeps, skip conditions or broadened accepted error stages.
`tools/render_fixture.py` and the workflow are unchanged by this repair.

## Local verification and its limits

Agent 43 used the integrator's frozen source/build at
`/tmp/hammond-wave06b-xawzydwm/{source,build}` and a new sanitizer build directory
`/workspace/scratch/c871510c69b2/agent43-sanitizers`. Local tools were GCC 14.2.0,
CMake 4.4.4 and CPython 3.12.14 on Linux x86_64 (kernel 6.18.57, glibc 2.41).
The current repaired test script was executed directly with the explicit
`HAMMOND_RENDER_EXECUTABLE` and `HAMMOND_TEST_PROFILE` prerequisites; the frozen
source and its original tests were not edited.

| Check | Observed result |
| --- | --- |
| All repaired producer tests against frozen Release renderer | 19 methods passed, no skips; 2.042 s |
| Fresh Debug renderer build with `HAMMOND_ENABLE_SANITIZERS=ON` | Passed strict GCC build |
| All repaired producer tests against fresh ASan/UBSan renderer | 19 methods passed, no skips; 2.537 s; `ASAN_OPTIONS=detect_leaks=0:halt_on_error=1` |
| Original mutation method, diagnostic-only in-memory assertion change | 10 ASan/UBSan iterations / 60 scenarios passed; 1.741 s; leak detection disabled |
| Local instrumented `--help` with hosted leak settings | Exit 23: LeakSanitizer fatal error explicitly states that it does not work under ptrace |

The original failure was not reproduced in that bounded local probe. The
integrator's separate Release probe also passed 20 iterations / 120 scenarios.
Neither observation identifies the hosted cause. Leak-disabled local execution
does not qualify leak detection; different toolchains and the focused test scope
do not replace a complete hosted rerun. The next integration must pass all four
jobs, retain its new exact revision, and repeat the full-log skip/count audit.

## Diagnostic archive identities

The integrator verified each downloaded ZIP digest against GitHub artifact
metadata. This audit independently recomputed the following hashes and read
`source-revision.txt`, `toolchain.log`, configure/build/CTest logs, JUnit XML and
each complete `LastTest.log`; failed-test lists were present for the two failures.
Raw logs are not copied into the source tree. Hosted retention is 14 days.

| Archive | GitHub artifact | SHA-256 of downloaded ZIP |
| --- | --- | --- |
| Linux Release | [14009822175](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43364414017/artifacts/14009822175) | `5acc37947862df14b240771ca2e3abc053027bae29517c765d6e8719b495303d` |
| macOS Release | [14009163956](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43364414017/artifacts/14009163956) | `d4cc162856f00b87c00fd5222a0576045b378a22bff42993137a67d6ce8e54d9` |
| Windows Release | [14009991559](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43364414017/artifacts/14009991559) | `b9457e2c112da9e75ae69b3354889d19ea162e1c537fedd17e5f668a0b903262` |
| Linux sanitizer | [14009572108](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43364414017/artifacts/14009572108) | `28d40b9cbc66ae02756db672b61cb9e34eacac1fd1affde43c353e0d10bd9686` |

These results concern the nominal offline software. They establish no native
device/DAW/VST3 qualification, audio deadline, signed distribution, source-to-binary
reproducibility, physical specimen match, or measured AO-28/scanner/Leslie fidelity.
