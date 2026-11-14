# Native standalone operational handoff

This is the active independent M9 dry-organ adapter track. The
[actual session manifest](development/2026-11-13-next-phases/assignments.json)
records new assignments only. The separate [scanner handoff](SCANNER_HANDOFF.md)
remains authoritative for its unfinished model work. Read all active tracks, current
status and the remote head before taking ownership.

## Current checkpoint and boundaries

Standalone package-audit checkpoint: `6214032f3565f9e221fcf3988e33a22a73bb4ea8`, tree
`10f070c54d176571f1919d8141d24dd82db0e41c`. Root fetched and verified exact tree
equality with local `fcc22346`; the local source history is preserved. Its two
changed tests follow `183fc9e2`, whose production, build and installed payload
inputs are unchanged. The final documentation/ledger closure is recorded by
this checkout's actual HEAD and the session manifest, not by assuming the code
candidate already contained later review files.

The complete integrated closure is published at
`27209a7fec075b082aa911c9ea2159938deaae85`, tree
`087d81ba1ea83834e866ab47cdd44a53fd9251ec`. It preserves concurrent calibration
publication `3b0979b`, which adds report replay and a separate CaptureTools component. The
[root integration record](reviews/STANDALONE_CONCURRENT_CALIBRATION_INTEGRATION.md)
names the merged tree, fresh 69-method replay/16-method install checks and the
new package's Windows sentinel repair. All ten hosted jobs now succeed at 272:
core 103/103 in all four jobs, standalone 14/14 on each platform, and VST3 8/8
Linux / 7/7 Windows/macOS. Actual Windows diagnostics confirm the corrected
preservation method passed; its one existing POSIX-only installation skip remains
explicit. This later scope does not extend the 621 standalone artifact audit or
the earlier 110-suite combined gate. Subsequent documentation records the outcomes
without changing the tested implementation.

All sixty requested assignments are complete and accepted in ten logical waves.
The [manifest](development/2026-11-13-next-phases/assignments.json) and
[strict completion record](development/2026-11-13-next-phases/completion-check.json)
show zero running, blocked or undispatched rows. Earlier console/pedal/scanner/
rotary/calibration ledgers are separate sessions and are not counted toward these
sixty. Future work starts from the concrete successor contracts below.

| Retained qualification | Exact result and source boundary |
| --- | --- |
| [Combined Release](reviews/STANDALONE_COMBINED_FINAL_GATE.md) | Fresh native-enabled 183 source: **110/110 suites**, 957 source blobs/modes unchanged, nine installed files. One Python suite reports two capability skips. |
| [Native ASan/UBSan](reviews/STANDALONE_FINAL_INTEGRATION.md) | **14/14** with the final chapel/workflow test overlays, 22 chapel auditions and 25 workflow processes; all instrumented compiled inputs/binaries verified unchanged. Local leak detection remains excluded. |
| [Final platform/artifact audit](reviews/STANDALONE_FINAL_PLATFORM_AUDIT.md) | At 621, all ten jobs succeed: core **101/101** on three platforms and Linux sanitizers/leaks; native **14/14** on each; VST3 **8/8 Linux, 7/7 Windows/macOS**. Actual nine-file package/notice bytes and relocated Linux execution are retained; internal capability skips remain separate. |
| [Core preservation](reviews/STANDALONE_CORE_PRESERVATION.md) | Named baseline/649 audit: 196 protected files, all 45 parameter records, migrations and 40 actual comparison renders match; it is not a physical timbre claim. |
| [Clean setup](reviews/STANDALONE_CLEAN_SETUP.md) and [multi-config install](reviews/STANDALONE_MULTICONFIG_INSTALL.md) | Named-source builds and relocation, Debug/Release, custom Unicode/space paths, unknown-config destination preservation and exact nine-file payload. |
| [Final repair/handoff review](reviews/STANDALONE_REPAIR_HANDOFF_REVIEW.md) | Independent literal-prefix/endpoint, canonical stream, actual symlink preservation and build-recipe review, with separate executed check scopes. |

Earlier failures remain: the original native sanitizer gate was 92/94; the two
later native groups were each 13/14 before their concrete oracle changes.
Windows core at 0085 was 92/96, and at 183 was 100/101 before the final demo-fixture
repair. Linux core at 649 was 89/90 before deterministic reader publication
handshakes. Their exact evidence and limits are linked from the reports above
and [STATUS.md](STATUS.md); a passing subset does not supersede them.

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
the [hosted workflow](STANDALONE_CI.md) and
[final artifact audit](reviews/STANDALONE_FINAL_PLATFORM_AUDIT.md) retain the
actual platform/package results. The [clean setup audit](reviews/STANDALONE_CLEAN_SETUP.md)
also verifies a fresh Unicode-path build and seven relocated executable runs.
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

## Resume the next development phase

The native app, Session/UI/state/device acceptance, bounded callback/concurrency
handling, replay, installed component, benchmark and chapel auditions now exist.
Use the two [current chapel views](../examples/demos/standalone-chapel-v1/README.md)
and four [earlier window views](../examples/demos/standalone-window-v1/README.md)
for actual source-identified render evidence. Neither establishes physical output
or native accessibility.

Start the independent **external MIDI adapter contract**. Pin the backend and
notice, define timestamps/late events and disconnect/overflow behavior, and
serialize device events through the Session's single producer. Preserve separate
UI/device ownership so focus loss releases only UI notes. Verify complete musical
state, duplicate/channel behavior, velocity-zero release, restart and shutdown
using independent event streams before a named hardware-controller/audio-device
run. The existing performance-input and Session contracts are the code boundary.

A parallel **native accessibility bridge** should expose the existing semantic
control names, roles, values, focus and actions from copied UI state. Qualify an
actual screen reader, keyboard editing, announcements and scale changes on one
named platform. The M3 successor is a typed exclusive fixed-registration selector
with declared append-only IDs/state migration and upper-B percussion history;
documentary chapel export alone does not implement that selector or loaded gains.
[Next steps](NEXT_STEPS.md) and the
[milestone reconciliation](reviews/STANDALONE_MILESTONE_RECONCILIATION.md)
spell out affected modules, concrete acceptance and acquisition prerequisites.

Respect current scanner, rotary and calibration ownership. Keep scanner G5,
connected AO-28, separate Leslie 122/147 electronics, measured captures and final
product release gates visible. Update this handoff, STATUS, NEXT_STEPS, the log
and affected contracts; commit/push completed authorized work with an expected-
head guard, then verify the actual remote result. Never force-push or count an
earlier/resumed worker as a new assignment.
