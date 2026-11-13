# Final hosted-platform review

Agent 59, original-session wave 10; completed 2026-11-13.
[Run 43368537860, attempt 1](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43368537860) qualifies exactly `61c6ecbd87f46a91b4d0d975c823eeae2e2fb3f8`.
All four jobs passed **26/26 CTest suites and 274 Python methods per job, with zero failures, disabled cases or test skips**.
Every archive's recorded revision and GitHub workflow SHA match this commit.

## Jobs and observed toolchains

| Platform / configuration | Job ID | Compiler | CMake / CTest | Python |
| --- | --- | --- | --- | --- |
| Ubuntu 24.04.5 x86_64, Release | `131698605419` | GCC 13.3.0 | 3.31.6 / 3.31.6 | 3.12.16 |
| macOS 15.8.2 arm64, Release | `131698605170` | AppleClang 17.0.0.17000013 | 4.4.5 / 4.4.5 | 3.12.10 |
| Windows Server 2022 10.0.20348 AMD64, Release | `131698605184` | MSVC 19.44.35229.0 | 3.31.6 / 3.31.6 | 3.12.10 |
| Ubuntu 24.04.5 x86_64, Debug sanitizers | `131698604928` | GCC 13.3.0 | 3.31.6 / 3.31.6 | 3.12.16 |

Linux records kernel `7.0.0-1017-azure`; sanitizer runner image is `20261111.370.1`.
Windows used SDK 10.0.26100.0 and MSVC tools 14.44.35207; MSBuild explicitly selected Release despite the unused `CMAKE_BUILD_TYPE` configure warning.
Actual compilation uses C++20 and warnings as errors; Windows build reports 0 warnings/errors.

## Verified diagnostic archives

| Archive | GitHub artifact ID | Recomputed ZIP SHA-256 |
| --- | --- | --- |
| Linux Release | [14010904328](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43368537860/artifacts/14010904328) | `1dc0ced5f140662ba93a1587a3ce924e27e3453f5850cd64c9ad230d99ed5a1e` |
| macOS Release | [14011890289](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43368537860/artifacts/14011890289) | `29e84f66be60ad4fb06df091dd68a75e326d0be1751486ecb35024835cc7bffc` |
| Windows Release | [14012050023](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43368537860/artifacts/14012050023) | `71da3b95d87e542f2bff31c27f9a812ab6d1523d94532851f87f3192e16e47ed` |
| Linux sanitizers | [14011113530](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43368537860/artifacts/14011113530) | `7cf2e98e31f11f825550c0a1fe4dea1a7e51f01aae3c8e324433c0de9305835f` |

ZIP sizes/digests match GitHub metadata. Read all raw job logs and complete revision,
toolchain/configure/build/CTest/JUnit/LastTest records. Hosted retention is 14 days,
expiring 2026-11-27; these identifiers/digests preserve the evidence identity.

## Complete registered test set

All four jobs executed these 12 C++ suites:
`test_contact_bank`, `test_control_io`, `test_controls`, `test_core_robustness`,
`test_decimal`, `test_engine`, `test_factory_runtime`, `test_numerics`,
`test_percussion`, `test_profile`, `test_realtime`, `test_tonewheel`.

| Python CTest suite | Actual methods in each job |
| --- | ---: |
| `python_test_audio_analysis` | 15 |
| `python_test_capture` | 41 |
| `python_test_compile_profile` | 37 |
| `python_test_demo_bundle` | 8 |
| `python_test_factory_reference` | 22 |
| `python_test_fixture_catalog` | 2 |
| `python_test_install` | 1 |
| `python_test_model_info` | 7 |
| `python_test_parameters` | 19 |
| `python_test_pedal_map` | 15 |
| `python_test_render` | 20 |
| `python_test_render_fixture` | 19 |
| `python_test_repository_integrity` | 41 |
| `python_test_verify_render` | 27 |

JUnit and full LastTest names match the exact commit's CMake registration. Method totals use complete LastTest because some JUnit output is truncated.
Every unittest summary is OK; conditional hardlink/symlink methods explicitly pass on all platforms. Conditional configure steps and compiler probes are not test skips.

## New gates and sanitizer evidence

Factory runtime passes 1,098 routes plus 64 cross-rate routes, 6 coherent cases, 8 routing/Cancel stages and 2 negative probes: 150,528 matching audio frames.
Contact tests pass 1,098 identities and three-rate edges; percussion passes 103 closed-form comparisons, 41 invalid profiles and 762 enum cases.
Demo (8 methods), factory validator (22), metadata (7) and control persistence (338 malformed inputs) pass across all four jobs.
All 22 sanitizer compiles and 15 executable links contain `-fsanitize=address,undefined`; compiles also contain `-fno-omit-frame-pointer`.
The actual CTest-step environment is `ASAN_OPTIONS=detect_leaks=1:halt_on_error=1`,
`UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1`, `LSAN_OPTIONS=exitcode=23`.
No leak-disable override or sanitizer diagnostic was observed.

F59-1's authorized portable stdout-failure repair and focused local proof are in [note 59](../development/agent-notes/59-platform-review.md).
The earlier [21-suite / 257-method result](../CI_QUALIFICATION.md) remains specific to `6c3dd8b`.
This qualifies offline software and independent model modules; Engine integration,
VST3/native-device qualification, deadlines, distribution rights, source-to-binary
reproducibility and measured contact/AO-28/scanner/Leslie/specimen fidelity remain open.
