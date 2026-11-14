# Native standalone operational handoff

This is the active independent M9 dry-organ adapter track. The
[actual session manifest](development/2026-11-13-next-phases/assignments.json)
records new assignments only. The separate [scanner handoff](SCANNER_HANDOFF.md)
remains authoritative for its unfinished model work. Read all active tracks, current
status and the remote head before taking ownership.

## Current checkpoint and boundaries

Published code candidate: `0085e338388f2c7516a7d455f11692b94e9451f4`, tree
`19c763503f67e1f054d2d27b6ec3d8fca2e36474`. Root fetched and verified equality
with local `fa6df9d`. Its fresh full native-enabled Release gate passes **105/105**.
The first instrumented native gate retains **13/14**, with a sampled chapel hold
oracle under repair. Native and VST3 Linux/Windows jobs pass; core Linux Release
and sanitizer jobs pass, while Windows core retains **92/96** from calibration
JSON/fixture portability. The three queued macOS jobs were cancelled without
observed execution. Later repairs require their own named source and results.

Earlier platform-qualified checkpoint: `649b12c7d1faa7601fde1019e913347c65a6634a`, tree
`cf63327d857b02029e8c5c6f406cab3d3c6890d1`. Root fetched and verified exact tree
equality. All three standalone platforms passed **14/14**, installation and
packaging; all three VST3 jobs passed. Core Windows/macOS passed **90/90**, and
the Linux sanitizer job passed. Linux Release passed **89/90**, retaining a
scheduler-dependent observer assertion. Exact jobs and earlier failures are in
the [platform follow-up](reviews/STANDALONE_PLATFORM_FOLLOWUP.md). A workflow's
successful subset does not override failed or unrun gates.
There are 59 actual assignments, of which 56 are accepted. The 60-case benchmark,
Debug/Release custom-path installation, complete milestone reconciliation,
two source-identified chapel views and partial session audit are accepted.
Assignment 55 qualifies the chapel observation repair, 58 independently reviews
the concurrent calibration portability fixes and 59 reviews the final repairs
and handoff. The final actual assignment remains undispatched. The
[combined-source evidence](reviews/STANDALONE_WAVE6_INTEGRATION.md) records the
fresh 94/94 Release gate at local `3872752` and separate later chapel/device
integration. The [native sanitizer audit](reviews/STANDALONE_NATIVE_SANITIZERS.md)
retains its actual 92/94 result and timing failures; it is not a full pass.
The [earlier checkpoint evidence](reviews/STANDALONE_NATIVE_CHECKPOINT.md)
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
cmake --build build --config Release --parallel 2
ctest --test-dir build -C Release --output-on-failure --no-tests=error
```

The native window is explicitly enabled. Acquire its reviewed exact dependency
outside the repository; configuration only verifies existing files:

```sh
python3 tools/acquire_sdl2.py --destination ../SDL2
python3 tools/acquire_sdl2.py --verify-existing ../SDL2
cmake -S . -B build-standalone -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DHAMMOND_BUILD_STANDALONE=ON -DHAMMOND_SDL2_ROOT="$PWD/../SDL2"
cmake --build build-standalone --config Release --target hammond_standalone --parallel 2
```

For the complete native acceptance group, build its actual inputs before CTest:

```sh
cmake --build build-standalone --config Release --target hammond_standalone_test_inputs --parallel 2
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
the [hosted workflow](STANDALONE_CI.md) has Linux, Windows and macOS package
passes at `649b12c`. The [clean setup audit](reviews/STANDALONE_CLEAN_SETUP.md)
also verifies a fresh Unicode-path build and seven relocated executable runs.
The remaining core assertion and later timing source require their own gates.
Platform audio/window development headers determine enabled SDL backends. This
container lacks ALSA/Pulse/X11/Wayland development headers; its executed audio
checks explicitly select the dummy backend, which is not physical hardware.

## Reproduce an interaction, registration or measurement

Run these commands from the repository root after the native build above.
`--input-script` drives the ordinary SDL event handlers and records controls,
note ownership and acknowledgment before shutdown. Use fresh output filenames:

```sh
cmake -E make_directory out
SDL_AUDIODRIVER=dummy SDL_VIDEODRIVER=dummy \
  ./build-standalone/apps/standalone/hammond_standalone \
  --state out/replay-missing.b3controls \
  --input-script examples/standalone-input/keyboard-notes.b3ui \
  --diagnostics out/keyboard-notes.json
```

The [workflow guide](STANDALONE_WORKFLOWS.md) describes the maintained scripts;
the [replay contract](STANDALONE_INPUT_REPLAY.md) specifies admission and limits.
Script delivery alone is not proof of applied or audible notes; the app's
completion diagnostics and acceptance suite check the relevant acknowledgment.

To copy an admitted documentary chapel registration to ordinary controls,
generate the catalog explicitly and export to a new file:

```sh
cmake --build build-standalone --target hammond_chapel_catalog --config Release
python3 tools/chapel_controls.py --catalog build-standalone/chapel-catalog.json \
  --upper 'C#' --lower off --bank A --expression 0.75 \
  --output out/chapel-upper-csharp-a.b3controls
./build-standalone/apps/standalone/hammond_standalone \
  --state out/chapel-upper-csharp-a.b3controls
```

The final command requests the actual default audio/video drivers. The exporter
requires an existing parent and preserves existing destinations. It copies
atlas p122 tap digits to current nominal gains, with the other manual and pedals
muted. It does not add physical fixed-preset selection or claim factory timbre.
See [CHAPEL_CONTROLS.md](CHAPEL_CONTROLS.md) for exact keys, banks and limits.

The Session benchmark also exists with native standalone OFF. Its native-build
location and one explicit workload are:

```sh
cmake --build build-standalone --target hammond_standalone_benchmark --config Release
./build-standalone/apps/standalone/hammond_standalone_benchmark \
  --profile build-standalone/nominal.b3p --sample-rate 48000 \
  --buffer-frames 512 --iterations 500 --warmup 16 --workload performance
```

The JSON retains every measured interval, source/toolchain/profile identity and
exact workload accounting. It applies no physical deadline or latency pass
threshold; compare only appropriately controlled runs. Multi-configuration
generators add the configuration subdirectory to all executable paths above.

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
gates, inspect the published reader/concurrency repairs and qualify the timing repair, then audit
clean setup, package/runtime compatibility and the
final session records. Physical-device
latency/underruns, hotplug, musician workflow and native accessibility remain
separate evidence gates. Update this handoff, STATUS, NEXT_STEPS and the log,
commit/push authorized completed work, inspect concurrent advances and verify
publication without force-pushing.
