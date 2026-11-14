# A18 — Genuine pending native rendering harness

Worker `/root/w03_a18_pending_raster_impl`, wave 3. Base HEAD
`d2972a5744c63219f785e118055b7992656cf8b3`; the source overlay is identified in
[the 102-input inventory](../reports/A18-source-before.json), with no changes
across the targeted build/capture. This inventory excludes the separate,
in-progress RotaryPropagation sources and does not attest the whole worktree.
Owned the new `apps/standalone/native_tests/test_standalone_inspection_raster.cpp`,
this note and A18 reports/captures. Root owns CMake integration. No production
source, Session/model, callback timing or shared documentation was changed.

Read AGENTS, the current scope/checkpoint/manifest, complete M0–M9 plan,
current status/next steps, recovery handoff/checkpoint, atlas review and the
full inspection contract. Reviewed atlas text pp. 34, 40, 151–156 and 415.

## Implemented and observed

The harness loads the unchanged compiled nominal profile, prepares a real
Session with `{48000.0, 64, 819, 0}` and forwards actual UiModel actions through
`Session::post` and immediate `UiModel::submitted`. A key Down submits Upper
MIDI 60, channel 0, owner 1 at sequence 1; rendering 32 frames holds that target.
Actual Upper preset F activation queues its whole desired control copy at
sequence 2. Before any further render, the real publication remains revision
6, frame 32, resolved/applied sequence 1, sounding Bank B, with F pending.

Actual Drawing/InstrumentView paint pending Play/Service at 1672×941 and Service
at 960×700. Workspace/resize/painting leave Session publication, held targets
and desired state unchanged. `render(0,{})` acknowledges exactly sequence 2,
publishes revision 8 and clears pending while preserving frame 32, holds and
peak. The same three views paint again. Real A Up uses the original owner at
sequence 3; zero-frame release and orderly stop clear all targets without
clock advancement or faults. No Session observation is fabricated.

Every frame uses SDL Init(0), RGBA32 software surface, software renderer,
Drawing initialization and native painting. Flush, pixel reads and optional
BMP save precede Present. Default InstrumentViewInfo reports stopped audio;
no device or application window is opened. Optional `--capture-dir` accepts
only a new directory; ordinary operation writes no gallery.

## Executed verification

Working directory: `/workspace/scratch/1bb6ee17ad7e/Hammond-B3-Organ`.
Root assigned the native build slot after A16; it was released immediately
after this gate. Existing GCC 14.2.0 Release/CMake 4.4.5/Ninja tree uses pinned
SDL 2.32.10, standalone ON, MIDI/VST3/sanitizers OFF.

```sh
../build-tools/cmake/data/bin/cmake --build ../build-native --target test_standalone_inspection_author test_standalone_inspection_acceptance test_standalone_inspection_raster --parallel 2
../build-tools/cmake/data/bin/ctest --test-dir ../build-native -R '^test_standalone_inspection_(author|acceptance|raster)$' --output-on-failure --no-tests=error
../build-native/apps/standalone/test_standalone_inspection_raster --capture-dir ../A18-inspection-pending-raw
```

Build exited 0; **3/3 suites passed in 0.63 seconds**, raster 0.61 seconds.
Capture passed in 0.58763 seconds with six frames and 965 assertions. Actual
pending/acknowledged changed-pixel counts were 5,317 / 2,918 / 2,698. A fresh
ordinary run created zero files in an empty working directory. Reusing the
capture directory exited 1 and preserved every original artifact hash.
[Exact results and commands](../reports/A18-result.json) retain these checks;
original build/test/capture logs are adjacent.

Source SHA-256:
`d04873c3d4d7d2b76c2c678e592ac8bc8e13f01af64faafce581fbf69b35950d`.
Executable SHA-256:
`44e059f761aff6c04af62088b7a26d500839f95043e297dcf7769c08e3094b60`.
[Binary/profile identities](../reports/A18-built-identity.json) and
[BMP/PNG inventory](../reports/A18-pending-capture/capture-inventory.json)
bind the artifacts. Six retained lossless PNGs total 2,470,292 bytes; decoded
RGBA equality with their BMPs passed. Native metadata retains complete control
copies, sequence/owner/frame/publication observations and row text.

Visually inspected all six PNGs: pending/sounding states are distinct; Upper
`1 target` and Lower/Pedals `0 targets` remain legible at both Service sizes.
No label collision or clipping was observed. Small minimum-size typography
still requires physical display/DPI review. These are **native rendering
harness captures, no application window or audio device**. Next: independent
pending-raster review and coherent integration; whole-application desktop,
physical device and fidelity gates remain separate. No commit/push/spawn.
