# Assignment 40 — actual standalone demonstration

Actual agent `/root/w07_a40_native_demo`, wave 7, assignment 40 of this
standalone session's sixty actual assignments.
Owned paths: `examples/demos/standalone-window-v1/`,
`docs/reviews/STANDALONE_WINDOW_DEMO.md`, and this note. No production code,
shared status, manifest, CMake or other worker file was changed; no commit or
publication was attempted by this worker.

## Source basis and execution

Read the standing agent requirements, standalone scope/application/model,
input-replay and installation contracts, plus the M9/art-direction plan and
atlas review. The integrator confirmed the frozen native binary ready before
capture; source/build inputs remained read-only.

- Source commit: `387275289410d12af27cf235d6e45fd91f29bafa`.
- Source tree: `0d6da163edd6531338938e12e0d393841d569a80`.
- Executable: `../build-w6-frozen/apps/standalone/hammond_standalone`.
- Executable SHA-256: `7377e8c2c146636ef3b4ca28891d257bbfcc9db8b6f42caa257b6857d97d9925`.
- Build: GCC 14.2.0 / CMake 4.4.4, Release, pinned static SDL 2.32.10.
- Runtime: explicit dummy audio/video, obtained `software` renderer.
- Conversion: Python 3.12.14 / Pillow 13.0.0; RGBA pixels preserved exactly.

Captures ran from four fresh private directories under
`/workspace/scratch/5ba97739b54c/hammond-native-demo-a40-5gpa4z59`.
Each used `--state controls.b3controls`, explicit width/height, `--screenshot
capture.bmp` and `--diagnostics diagnostics.json`; the exact full argument
arrays are in [provenance.json](../../../examples/demos/standalone-window-v1/provenance.json).
The state file was absent before and after every run. BMPs/logs stayed in
scratch; only PNGs, unmodified JSON and bounded input scripts entered the bundle.

| Actual run | Inputs | Observed outcome |
| --- | --- | --- |
| Reference | 1280 × 900, `--smoke-ms 600` | Exit 0; hold/release passed; 57 callbacks / 29184 frames; held-note image. |
| Minimum | 960 × 700, `--smoke-ms 600` | Exit 0; hold/release passed; 56 callbacks / 28672 frames; held-note image. |
| Help | 960 × 700, `help.b3ui`, 600 ms / 2 events | Exit 0; replay passed/delivered/acknowledged; 61 callbacks / 31232 frames. |
| Audio | 1280 × 900, `audio.b3ui`, 1000 ms / 18 events | Exit 0; replay passed; 2 device starts; obtained 96000 Hz / 128 frames; 464 callbacks / 76288 frames. |

Every run had positive rendered images/frames, native stereo float32, no
application error or audio/session fault, and no held notes after joined
shutdown. The binary hash was unchanged afterward. PNG mode, dimensions and
every decoded pixel byte matched its original BMP. Selected source files
matched the named Git commit; dependency/profile/build hashes were retained.

## Visual inspection and limits

Inspected all four PNGs directly with `view_image`. No clipped panel/keyboard
edge, control-label collision or footer overlap was observed in these states.
The held upper key is distinct at both sizes. The minimum Help panel and
reference Audio panel fit, including their cyan focus outlines. Pitch labels
and footer are compact at minimum size; real-display usability is still open.
The [review](../../reviews/STANDALONE_WINDOW_DEMO.md) records the observations.

These are real application backbuffers on dummy devices, not a physical
desktop capture, heard audio, high-DPI or native accessibility qualification.
The nominal profile/proposed audition remains unmeasured. Timing/counters may
vary, so artifact hashes identify this retained run rather than deterministic
image reproduction on every machine. No failed application capture occurred.
The first artifact audit incorrectly required exit 0 from `git diff --no-index
--check` on new files; it returned 1 with no whitespace diagnostics. The audit
was corrected to accept the documented difference status and rerun.
The final artifact audit passed: exact 12-file bundle, image/JSON/script hashes,
all four original BMP/PNG pixel comparisons, 26 local Markdown targets, owned
text whitespace, reproduction Bash syntax and unchanged executable identity.

## Handoff

The [bundle README](../../../examples/demos/standalone-window-v1/README.md)
contains portable commands, acceptance fields, four images and source/rights
links. Integrator: review the owned paths, link the accepted demo from the
project entry point, update shared session records and include it in the next
verified commit/push. Future worker: obtain a real desktop/audio device, retain
platform/renderer/device and pixel-scale identities, inspect these same states
and qualify physical input, label usability and assistive technology separately.
