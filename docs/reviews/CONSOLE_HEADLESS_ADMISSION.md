# Console library: distinct SDK-free admission

**A32, 17 November 2026 UTC: ADMIT this exact Linux Release configuration for
the LibraryModel/UiModel recall foundation and the twelve selected SDK-free
regression suites.** The fresh configuration, first 68-step build and first
runtime selection all passed. CTest reports **12/12 passed, zero failed**, in
5.69 seconds. No production/test repair or runtime rerun was needed. This is
the required distinct configuration, separate from root's native build.

The [qualification record](../development/2026-11-16-console-completion/reports/A32-headless/qualification.json)
contains every command, cwd, timestamp, status and complete per-test output.
Its SHA-256 is `81052af68844da6c89414103205acfe437158eb0c82a8905be8ec1a8da35d24e`.
Root retains combined native/sanitizer/platform acceptance, integration,
publication and release. The [frozen design](../LIBRARY_MODEL_DESIGN.md),
[design admission](LIBRARY_MODEL_DESIGN_ADMISSION.md),
[source admission](LIBRARY_MODEL_SOURCE_ADMISSION.md) and
[A26 helper contract](../development/2026-11-16-console-completion/notes/A26.md)
retain their boundaries.

## Exact setup and source

Checkout: `/workspace/scratch/21cce69f7784/Hammond-B3-Organ`.
New build: `/workspace/scratch/21cce69f7784/a32-headless`; it did not exist at
preflight. The parent explicitly released the timing freeze and confirmed the
reviewed helper/CMake inputs before any configure, build or project execution.
HEAD was `9d60dbf462a90fe422fd4e69757fe202264acb7c`, base tree
`6bfdb87625ea7626e1b7c30ce9e78bad622a5978`; the working additions below are not
identified by that base commit alone. The [preflight](../development/2026-11-16-console-completion/reports/A32-headless/preflight.json)
retains tool hashes, actual dirty state, source pins and available space.

| Configuration input | Actual value |
| --- | --- |
| CMake / CTest | 4.0.3, pinned executables in `/workspace/scratch/3edffb787db3/build-tools/cmake/data/bin/` |
| Ninja | `1.11.1.git.kitware.jobserver-1`, pinned `/workspace/scratch/3edffb787db3/build-tools/bin/ninja` |
| Compiler / language | `/usr/bin/g++`, GNU 14.2.0; C++20 with extensions disabled |
| Generator / configuration | Ninja / Release, actual `-O3 -DNDEBUG` |
| `BUILD_TESTING` | `ON` |
| `HAMMOND_BUILD_STANDALONE`, `HAMMOND_BUILD_VST3`, `HAMMOND_ENABLE_MIDI` | All `OFF` |
| `HAMMOND_ENABLE_SANITIZERS` | `OFF`; this admission is not an instrumented run |
| SDL2, RtMidi and VST3 SDK roots | None supplied; all three actual cache paths empty |
| Build and test parallelism | Two; root independently built native inputs with its own bound |

The original [cache](../development/2026-11-16-console-completion/reports/A32-headless/configured-CMakeCache.txt)
has SHA-256 `2747a3b64cefeedf7cc45e96051ca0ed9e5a4867f06952ec9ad31b215575340e`.
The [configuration check](../development/2026-11-16-console-completion/reports/A32-headless/configuration-verification.json)
reads back real option values and generated registrations; it does not infer
them from the planned command. All twelve selected names were present among
33 registered standalone tests. Native application/P1 gates were absent.

| Principal source | SHA-256 |
| --- | --- |
| `apps/standalone/LibraryModel.h` | `4ea94b611e4fdc27ea48c6bad47ddf9ed99761f2e12ae264b7482ac8d3b093e2` |
| `apps/standalone/LibraryModel.cpp` | `ae5348c731b0559a6816b75cc190622918ca89d1fe938dd56445d51591904b98` |
| `apps/standalone/UiModel.h` | `34337e5db254bfbc4e23ee4fadf76ecc8fe792f003bd13ab5b54d0a302b5bb15` |
| `apps/standalone/UiModel.cpp` | `b4889e0b5d1b6eb0b88b140b8af92815df4bf021158a902994db2c15ed798986` |
| `apps/standalone/CMakeLists.txt` | `c2da131f35b6f8e3827f8cef93244d997f0921c60de9235ad4e88775702cf690` |

The [complete used-source manifest](../development/2026-11-16-console-completion/reports/A32-headless/qualified-source-identities.json)
records 112 source/configuration inputs and verifies their hashes against actual
preconfigure records. This includes the five new tests and the support/core
consumers. The [built identities](../development/2026-11-16-console-completion/reports/A32-headless/built-identities.json)
retain all 50 object, two archive and twelve executable hashes. The support
archive is `9608fbbe51e00bba1a67a07300f9408fee53c5138fcd242d5611e87bbc422191`;
the core archive is `afbde61ccfad209c74c140d8f76e4752ae3ac7c4eef44667f9fb5be9367e4b1c`.
The separate [generated-input record](../development/2026-11-16-console-completion/reports/A32-headless/generated-identities.json)
binds the three generated headers and actual nominal profile to their four
generator commands. The profile hash is
`b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.

## SDK independence observed

The [dependency audit](../development/2026-11-16-console-completion/reports/A32-headless/sdk-independence.json)
checks actual built inputs, beyond disabled cache options. All 50 translation
units use C++20 and the repository's warnings-as-errors flags, including
`-Wconversion` and `-Wsign-conversion`. All nine support translation units use
`HAMMOND_HAS_RTMIDI=0`. The archive contains the real `LibraryModel.cpp.o` and
`UiModel.cpp.o`, alongside Session, storage and the remaining support objects.

The retained Ninja database has **62 valid compile/link dependency groups** and
**531 unique actual dependency paths**, with no SDL, RtMidi, VST3 or host SDK
dependency. Each of the twelve selected executable link commands uses exactly
the support/core archives. `readelf --dynamic` independently reports only
`libstdc++.so.6`, `libm.so.6`, `libgcc_s.so.1` and `libc.so.6` for every executable.
Standard compiler/runtime, filesystem and Threads facilities remain required;
SDK-free does not mean freestanding or independent of the operating system.

The [original command graph](../development/2026-11-16-console-completion/reports/A32-headless/09-ninja-commands.stdout.log),
[actual dependency log](../development/2026-11-16-console-completion/reports/A32-headless/12-ninja-deps.stdout.log),
[ELF readback](../development/2026-11-16-console-completion/reports/A32-headless/13-elf-dynamic.stdout.log)
and [archive listing](../development/2026-11-16-console-completion/reports/A32-headless/14-support-members.stdout.log)
are retained. No native app, paint fixture, device, host or timing process ran.

## Executed selection and original outcomes

The [first configure](../development/2026-11-16-console-completion/reports/A32-headless/05-configure.json)
completed with exit zero in 0.937 seconds. The
[first coherent build](../development/2026-11-16-console-completion/reports/A32-headless/07-first-build.json)
completed all 68 steps with exit zero in 81.278 seconds. Their complete original
stdout and stderr remain beside these command records; both stderr streams are
empty. These elapsed observations are not performance or callback-deadline
acceptance.

After the build, the [CTest JSON inventory](../development/2026-11-16-console-completion/reports/A32-headless/08-ctest-discover.stdout.log)
proved exactly twelve enabled selected tests, each pointing at its newly built
headless executable. The [first runtime command](../development/2026-11-16-console-completion/reports/A32-headless/10-first-ctest.json)
used `-V --output-on-failure --no-tests=error --parallel 2 --timeout 180`, the
anchored [exact-name filter](../development/2026-11-16-console-completion/reports/A32-headless/selection.txt)
and JUnit output. All five new suites passed:

| Registered CTest name | Actual result and evidence boundary |
| --- | --- |
| `test_standalone_library_model` | 32 groups / 3,250 assertions, zero failed groups; copied-model contract fixtures |
| `test_standalone_library_session` | 12 groups / 42,634 assertions, 696 real snapshots, 150 renders and 428 accepted posts; 6,252 bit-exact paired stereo samples, 10,101 phase checks and 60 percussion-history checks |
| `test_standalone_library_storage` | Nine groups / 1,115 checks, zero failures; real filesystem with explicitly synthetic control proof |
| `test_standalone_library_recall` | Nine groups / 743,728 assertions, 98 invalid snapshots and 72 presentation/owner contexts, zero failures; synthetic public UiModel boundary inputs |
| `test_standalone_library_roundtrip` | Four real UI/model/Session/storage journeys / 1,489 checks, 138 fresh snapshots, 20 renders, 24 actual posts with 24 reports to each model, four recall dispatches and seven storage/authorizer calls; zero failures |

The seven adjacent passes are `test_standalone_ui`,
`test_standalone_preset_ui`, `test_standalone_external_control`,
`test_standalone_workspace_continuity`, `test_standalone_session`,
`test_standalone_registration_library` and `test_standalone_state_files`.
The [complete verbose output](../development/2026-11-16-console-completion/reports/A32-headless/10-first-ctest.stdout.log)
and [JUnit](../development/2026-11-16-console-completion/reports/A32-headless/ctest-first.xml)
retain every count and platform exclusion. In particular, state-file acceptance
explicitly did **not** test POSIX failed replacement after a complete temporary
write because it lacks a deterministic non-racing fixture. Its overall pass
does not erase that unrun branch.

The first evidence-inspector attempt separately failed closed because the broad
source snapshot omitted the standalone `CMakeLists.txt` map key. Its exact hash
was already retained in the preconfigure `preflight.json`. The
[original inspector/error and correction record](../development/2026-11-16-console-completion/reports/A32-headless/inspection-v1-failure.json)
are preserved. The corrected reader used that existing hash and passed; it
changed no source baseline, build, test, assertion or runtime result. No duplicate
full-suite or second runtime selection was performed.

## Remaining admission and release ownership

This closes the distinct Linux SDK-free build/run gate for the exact recorded
foundation and helper. Root still owns coherent native/full-suite and sanitizer
qualification, exact-source Windows/macOS/VST3/host results, guarded publication
and source-specific hosted/release acceptance. Native main/browser wiring,
modal Down suppression and original Up handling, parameter-gesture closure and
actual SDL/display/DPI/controller/audio-device journeys retain their own gates.
The four real harness journeys are not the native browser adapter.

Native semantic accessibility, callback deadlines and OS callback retirement,
physical instrument/cabinet fidelity, signed distribution and **literal
whole-interface 1:1** remain unqualified here. The full M0–M9 plan and preservation
of 47 parameter identities, state4/readers 1–3, 91 shared sources, plugin UUIDs,
musical histories and the nominal dry Engine remain binding. Any later relevant
source change requires affected coherent qualification before reusing this
source-specific admission.
