# Native standalone operational handoff

This is the active independent M9 dry-organ adapter track. The
[actual session manifest](development/2026-11-13-next-phases/assignments.json)
records new assignments only. The separate [scanner handoff](SCANNER_HANDOFF.md)
remains authoritative for its unfinished model work. Read both tracks, current
status and the remote head before taking ownership.

## Current checkpoint and boundaries

Published contract/assets checkpoint: `96a37a977ef22b7adf38e1a841f57ffcf32519a7`,
tree `ab85e45d6776229c00fa394a540d72803daf8281`. Both existing hosted workflows
succeeded for that revision. The native application/runtime and first 27 assignments are accepted; the
[next checkpoint evidence](reviews/STANDALONE_NATIVE_CHECKPOINT.md) records its
frozen full gate and subsequent focused acceptance. Inspect the manifest and exact
source before relying on a later count or result.
The baseline Release gate passed 77/77 suites. Actual full-application SDL dummy smoke and screenshots now supplement the
baseline; none establish a physical-device or hardware-fidelity result.

The UI exposes the existing dry engine: two 61-key manuals, 25 pedals, separate
A/B edit and sounding banks, Cancel, percussion and nominal linear expression.
Scanner, AO-28, Leslie and measured physical behavior are not part of this app
checkpoint. A keyboard-operable SDL canvas has no qualified native accessibility
tree. Fixed chapel presets remain a later model dependency from atlas p122.

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
[Standalone component](STANDALONE_INSTALL.md) now passes staging and relocation;
the [hosted workflow](STANDALONE_CI.md) has not yet executed at this checkpoint.
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
concurrent recovery/snapshot and installation tests exist. Integrate the tested
scripted-input helper into the ordinary application loop and execute independent
musical workflows. Add the SDK-free render benchmark with source/toolchain
identity. Preserve screenshots and diagnostics from the linked application and
execute the new hosted Linux/macOS/Windows smoke checks. Physical-device
latency/underruns, hotplug, musician workflow and native accessibility remain
separate evidence gates. Update this handoff, STATUS, NEXT_STEPS and the log,
commit/push authorized completed work, inspect concurrent advances and verify
publication without force-pushing.
