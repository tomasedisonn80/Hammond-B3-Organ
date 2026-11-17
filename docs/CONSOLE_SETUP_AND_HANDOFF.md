# Console setup and developer handoff

These are **source-reviewed reproduction commands**, not a fresh installation or
execution report. The [live checkpoint](development/2026-11-16-console-completion/CHECKPOINT.md)
owns combined H1/P1 qualification, exact tested sources and hosted outcomes.
Run commands from the repository root. Shell examples use Linux/macOS with a
single-configuration generator; [Windows and multi-configuration instructions](MIDI_EXPRESSION_GUIDE.md#build-the-native-application)
give the corresponding executable paths and PowerShell syntax.

## Prerequisites and core/headless build

Use CMake **3.21+**, Python **3.10+**, a **C++20** compiler and its build tool.
Native builds additionally need a C compiler, Git and the
[platform development packages](MIDI_EXPRESSION_GUIDE.md#build-the-native-application).
The core, offline tools and library foundation require no SDL, RtMidi or VST3 SDK:

```sh
cmake -S . -B build-core -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_BUILD_VST3=OFF \
  -DHAMMOND_ENABLE_MIDI=OFF
cmake --build build-core --config Release --parallel 2
ctest --test-dir build-core -C Release --output-on-failure --no-tests=error
```

Use new build directories when changing compiler/generator. Build before CTest:
CTest does not compile prerequisites. The existing `check` target combines those
steps. [General builds](BUILD.md) and [offline rendering](RENDER_FORMAT.md) explain
other configurations and the generated `nominal.b3p` profile.

## Opt into the native application

SDL is pinned to **2.32.10**, official tag `release-2.32.10`, commit
`5d249570393f7a37e037abf22cd6012a4cc56a71`, with its Zlib notice identity in the
[dependency lock](../data/dependencies/sdl2-lock.json). Acquisition is explicit;
CMake only verifies the existing source. Use a new external dependency directory:

```sh
python3 tools/acquire_sdl2.py --destination ../SDL2
cmake -S . -B build-native -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DHAMMOND_BUILD_STANDALONE=ON -DHAMMOND_SDL2_ROOT="$PWD/../SDL2" \
  -DHAMMOND_BUILD_VST3=OFF -DHAMMOND_ENABLE_MIDI=OFF
cmake --build build-native --config Release --parallel 2 \
  --target hammond_standalone_test_inputs
ctest --test-dir build-native -C Release --output-on-failure --no-tests=error \
  -R '^test_standalone_'
./build-native/apps/standalone/hammond_standalone --width 1672 --height 941
```

For an existing dependency, replace acquisition with
`python3 tools/acquire_sdl2.py --verify-existing ../SDL2`.
`hammond_standalone_test_inputs` builds the application and native/support test
inputs; building only `hammond_standalone` is sufficient for launching.
The reference composition activates in Dimensional Play at width ≥1400 and
height ≥820; default startup is 1280×900. Use AUDIO / Ctrl+, for output settings.
Normal launch uses actual platform drivers. Dummy-SDL captures/tests have a
separate software-only scope.

Physical MIDI is optional: follow the [MIDI setup](MIDI_EXPRESSION_GUIDE.md) for
locked RtMidi 6.0.0, `HAMMOND_ENABLE_MIDI=ON`, `HAMMOND_RTMIDI_ROOT` and explicit
port selection. [VST3 setup](VST3_BUILD.md) separately uses CMake **3.25+**,
`HAMMOND_BUILD_VST3=ON` and `HAMMOND_VST3_SDK_ROOT`; its generic host controls do
not supply this standalone editor.

## Explicit installation

After the builds above, choose fresh staging destinations; keep
`CMAKE_INSTALL_MODE` unset or `COPY`:

```sh
cmake --install build-native --config Release --component Standalone \
  --prefix "$PWD/stage-console"
cmake --install build-core --config Release --component OfflineTools \
  --prefix "$PWD/stage-tools"
cmake --install build-core --config Release --component RegistrationTools \
  --prefix "$PWD/stage-tools"
cmake --install build-core --config Release --component StarterRegistrations \
  --prefix "$PWD/stage-tools"
./stage-console/bin/hammond_standalone --width 1672 --height 941
```

| Component | Actual payload and boundary |
| --- | --- |
| `Standalone` | `bin/hammond_standalone` plus documentation/notices/capability metadata: **17 files MIDI-OFF, 21 MIDI-ON**. Profile, fonts and reference art are embedded. |
| `OfflineTools` | Five native tools including `hammond_render`, compiled profile, catalogs/scores and plotting scripts. |
| `RegistrationTools` | `hammond_registration` plus its guide: **two files**. |
| `StarterRegistrations` | **24 saved-control files plus README/recipes**, under `share/hammond/registrations/starter-v1`. |

Install never builds missing inputs or imports/recalls a user registration.
Standalone and registration destinations refuse replacement/merging; OfflineTools
can replace selected files. Ordinary installation selects OfflineTools; the other
three require explicit components. Keep installed payloads together when moving
them. System runtimes are not bundled, and local staging is not signed release
qualification. See [native installation](STANDALONE_INSTALL.md),
[offline installation](OFFLINE_INSTALL.md) and [registration operations](REGISTRATION_GUIDE.md).

## Foundation and next implementation

`hammond_standalone_support` contains the copied-state `LibraryModel`, Session,
storage and `UiModel::recall_controls`. The model owns catalogs, selection,
drafts and operation receipts; callers perform I/O. The helper validates and
publishes one whole-control action without changing the legacy saved baseline.
The five focused suites cover model, real Session, storage, recall helper and
combined roundtrips:

```sh
ctest --test-dir build-core -C Release --output-on-failure --no-tests=error \
  -R '^test_standalone_library_(model|session|storage|recall|roundtrip)$'
```

Their executable targets have those exact test names. Read the
[model guide](LIBRARY_MODEL_GUIDE.md) for synthetic versus real boundaries.
**Native browser/main wiring and a native `--library` option are absent.**
[A33’s integration plan](design/LIBRARY_NATIVE_INTEGRATION_NEXT.md) next requires
independent admission of model-owned Save availability, genuine post-Start
control proof, lifecycle/submission hooks and held-input-safe modal routing.
Generic Load restores complete controls, including expression. Registration Recall
preserves current desired expression; CLI materialization takes it from the
explicit `--current` file. Starter recipes are proposed, unmeasured software settings.

The combined [workflow](../.github/workflows/standalone.yml) declares a **55-test
required platform subset** and **41 sanitizer tests mapped to 37 build targets**,
including explicit SDL C instrumentation. These obligations are not fresh passes;
retain original failures when qualifying changed code. The [prior integrated P1
gallery](design/native-gallery-console-integrated/manifest.json) and [H1 gallery](design/native-gallery-header-h1-v1/README.md)
retain their own executable/source identities; use the checkpoint for combined-source
gallery admission.

## Permanent recovery and product boundaries

Every future agent must recover the entire [AGENTS](../AGENTS.md) and [M0–M9 plan](PLAN.md),
then the current [session](development/2026-11-16-console-completion/README.md),
checkpoint, actual ledger, full-atlas coverage and assigned contracts. Confirm
exclusive ownership and live source before editing. Record setup, commands,
actual progress, failures/unrun gates and concrete next work; update README with
real application captures after UI changes. Root integrates, commits and pushes
accepted authorized work using a fresh expected remote head without force, then
independently verifies remote contents and exact-source CI.

Preserve 147 playing keys, 24 reversed presets, four banks, 47 parameter IDs,
`B3CONTROLS4`/readers 1–3, 91 free-running sources and plugin UUIDs. Correct live
controls take precedence over inaccurate concept legends. [Preset behavior](PRESET_RUNBOOK.md)
and [model limits](STANDALONE_MODEL.md) distinguish documentary routing from
factory Table IV, loaded gain and physical-latch evidence still required.
The Engine remains nominal and dry. **Literal whole-interface 1:1 remains unmet
and unwaived**; real display/DPI/input, device/host, native accessibility,
callback deadlines/retirement, physical fidelity and signed distribution retain
separate [release gates](RELEASE_READINESS.md).
