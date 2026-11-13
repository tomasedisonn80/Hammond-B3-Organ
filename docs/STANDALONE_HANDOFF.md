# Native standalone operational handoff

This is the active independent M9 dry-organ adapter track. The
[actual session manifest](development/2026-11-13-next-phases/assignments.json)
records new assignments only. The separate [scanner handoff](SCANNER_HANDOFF.md)
remains authoritative for its unfinished model work. Read both tracks, current
status and the remote head before taking ownership.

## Current checkpoint and boundaries

Published native checkpoint: `219821dfaca6bfee8ba0905993ed8deec7a66396`, tree
`f2db7aee1d45a897273e4e68a2fefc6a2de4d433`. Its Linux standalone and native VST3
hosted gates passed; Windows/macOS standalone test builds failed and have scoped
[portability repairs](reviews/STANDALONE_PORTABILITY_REPAIR.md) awaiting publication/rerun.
The first 41 assignments are accepted; assignments 42–44 are running. The
[combined-source evidence](reviews/STANDALONE_WAVE6_INTEGRATION.md) records the
fresh 94/94 gate at local commit `3872752` and the separate later 2/2 chapel
integration gate. The [earlier checkpoint evidence](reviews/STANDALONE_NATIVE_CHECKPOINT.md)
records its frozen full gate and subsequent focused acceptance. Inspect the manifest and exact
source before relying on a later count or result.
The baseline Release gate passed 77/77 suites. Actual full-application SDL dummy smoke and screenshots now supplement the
baseline; none establish a physical-device or hardware-fidelity result.

The UI exposes the existing dry engine: two 61-key manuals, 25 pedals, separate
A/B edit and sounding banks, Cancel, percussion and nominal linear expression.
Scanner, AO-28, Leslie and measured physical behavior are not part of this app
checkpoint. A keyboard-operable SDL canvas has no qualified native accessibility
tree. The [atlas p122 catalog](CHAPEL_PRESETS_CATALOG.md) is admitted documentary
data. The [exporter](CHAPEL_CONTROLS.md) writes explicit ordinary B3CONTROLS3
auditions; the physical fixed-preset selector remains a later model dependency.

## Build prerequisites and commands

Use a C++20 compiler, CMake 3.21 or newer, Python 3.10 or newer and Git. The ordinary
SDK-free build does not require SDL2 and does not download dependencies:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build build --parallel 2
ctest --test-dir build -C Release --output-on-failure --no-tests=error
```

The native window is explicitly enabled. Acquire its reviewed exact dependency
outside the repository; configuration only verifies existing files:

```sh
python3 tools/acquire_sdl2.py --destination ../SDL2
python3 tools/acquire_sdl2.py --verify-existing ../SDL2
cmake -S . -B build-standalone -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DHAMMOND_BUILD_STANDALONE=ON -DHAMMOND_SDL2_ROOT="$PWD/../SDL2"
cmake --build build-standalone --target hammond_standalone --parallel 2
```

For the complete native acceptance group, build its actual inputs before CTest:

```sh
cmake --build build-standalone --target hammond_standalone_test_inputs --parallel 2
ctest --test-dir build-standalone -C Release -R '^test_standalone_' \
  --output-on-failure --no-tests=error
```

For a single-configuration Linux/macOS build:

```sh
./build-standalone/apps/standalone/hammond_standalone --help
./build-standalone/apps/standalone/hammond_standalone
```

The native Visual Studio executable is under `apps/standalone/Release/` with an
`.exe` suffix. Use the [app guide](STANDALONE_APP.md) for controls, paths, errors,
Audio/Help operation and the full CLI. A bounded software-only check is explicit:

```sh
SDL_AUDIODRIVER=dummy SDL_VIDEODRIVER=dummy \
  ./build-standalone/apps/standalone/hammond_standalone \
  --state /tmp/b3-smoke-missing.b3controls --smoke-ms 600 \
  --screenshot /tmp/b3-smoke.bmp --diagnostics /tmp/b3-smoke.json
```

Choose fresh output paths and a deliberately missing state path for the default
proposed registration. The app embeds the nominal profile and glyphs. It does
not need the PDF or source font files to run. The explicit nine-file
[Standalone component](STANDALONE_INSTALL.md) passes staging and relocation;
the [hosted workflow](STANDALONE_CI.md) has a Linux pass and named Windows/macOS
test-build repairs awaiting an actual rerun.
Platform audio/window development headers determine enabled SDL backends. This
container lacks ALSA/Pulse/X11/Wayland development headers; its executed audio
checks explicitly select the dummy backend, which is not physical hardware.

## Architecture and evidence entry points

- [Session](STANDALONE_SESSION.md): one main-thread producer, one serialized audio
  consumer, fixed commands, coherent snapshots, admission and emergency recovery.
- [UI](STANDALONE_UI.md): shared geometry/hit testing, control identities, original
  note ownership, key repeat/focus/capture behavior and pending acknowledgments.
- [Audio](STANDALONE_AUDIO.md): obtained-format admission, actual callback lifetime,
  output clamp/nonfinite policy and copied diagnostics.
- [Dependency](STANDALONE_DEPENDENCY.md): version/provenance/rights and acquisition.
- [Fonts](STANDALONE_FONTS.md): redistributable inputs and exact atlas regeneration.
- [Session accounting](STANDALONE_SESSION_RECORDS.md): actual-assignment checker.

Read concrete filenames in the repository if a later task renames an entry.
Build the exact selected inputs before CTest. Freeze coherent sources for claims;
do not link stale core objects against changed live headers. Keep ordinary saved
controls separate from held notes, phases, contact trajectories and audio history.

## Next concrete acceptance work

The app and independent Session/UI/state/device, calibrated callback-allocation,
concurrent recovery/snapshot and installation tests exist. The scripted-input
application workflows and source-identified SDK-free benchmark now pass their
independent suites. Maximum-plan replay and chapel control-file audition are
qualified; [four actual native views](../examples/demos/standalone-window-v1/README.md)
retain their source and diagnostics. Inspect the repaired hosted Linux/macOS/Windows
gates, finish coherent native sanitizer qualification and independent open-device
removal handling, then audit clean setup, package/runtime compatibility and the
final session records. Physical-device
latency/underruns, hotplug, musician workflow and native accessibility remain
separate evidence gates. Update this handoff, STATUS, NEXT_STEPS and the log,
commit/push authorized completed work, inspect concurrent advances and verify
publication without force-pushing.
