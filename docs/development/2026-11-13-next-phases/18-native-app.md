# Assignment 18 — native application entry point

- Actual agent: `/root/w03_a18_native_app`, wave 3 of the independent
  2026-11-13 next-phases session. No earlier assignment is recounted.
- Owned files: `apps/standalone/main.cpp`, `docs/STANDALONE_APP.md`, this note.
  The integrator owns CMake, drawing, file helpers and shared status records.
- Inspected HEAD: `96a37a977ef22b7adf38e1a841f57ffcf32519a7`.
  Concurrent adapters were uncommitted; final main source identity is below.

## Implementation and boundary

Read `AGENTS.md`, current status/next steps/scanner handoff/plan, the retained
atlas product/closure reviews, and every assigned Session/UiModel/AudioDevice/
Drawing/InstrumentView/StateFiles header before implementation. The core,
profile, 45 parameter identities and B3CONTROLS formats are unchanged.

The app owns SDL initialization/quit, a resizable 1280×900 window with
960×700 minimum and 8192 maximum dimensions, input, modal focus, renderer and
files. Scancode input always forwards key-up. Pointer capture failure,
deactivation and shutdown release UI ownership. Bounded dispatch acknowledges
each post, stops a failed original batch and admits one recovery batch.

Audio settings enumerate actual names and expose rate/buffer choices through
the shared overlay rectangles. Close/join precedes reprepare; acknowledged
controls survive and notes/transient DSP reset. Offline musical commands are
rejected locally instead of accumulating in stopped Session queues. Help and
Audio have keyboard operation and visible focus. Initial/loaded intent survives
failed open. The explicit proposed audition registration is Upper B888000000,
Lower B008000000, pedals80; muted core defaults remain intact.

Startup/Load use existing StateFiles validation. Save takes acknowledged
coherent controls only, with a bounded wait/cancellation policy; no autosave.
Windows uses the existing Unicode CLI adapter and wmain. The documented smoke
uses the actual window, SDL events and audio callbacks; its screenshot is read
before presentation and JSON is copied after callback join.

## Executed evidence, 2026-11-13

Build root: `/workspace/scratch/5ba97739b54c/build-native-app`.
Compiler: GCC 14.2.0, C++20, repository `-Wall -Wextra -Wpedantic -Wconversion
-Wsign-conversion -Wshadow -Werror`; CMake 4.4.4. SDL2 is the locked 2.32.10,
commit `5d249570393f7a37e037abf22cd6012a4cc56a71`.

```sh
/workspace/scratch/1742da7072be/build-tools/lib/python3.12/site-packages/cmake/data/bin/cmake \
  -S /workspace/scratch/5ba97739b54c/Hammond-B3-Organ \
  -B /workspace/scratch/5ba97739b54c/build-native-app -DCMAKE_BUILD_TYPE=Release \
  -DHAMMOND_BUILD_STANDALONE=ON -DHAMMOND_SDL2_ROOT=/workspace/scratch/5ba97739b54c/SDL2 \
  -DBUILD_TESTING=ON -DCMAKE_INSTALL_DATADIR=share
/workspace/scratch/1742da7072be/build-tools/lib/python3.12/site-packages/cmake/data/bin/cmake \
  --build /workspace/scratch/5ba97739b54c/build-native-app --target hammond_standalone --parallel 3
SDL_AUDIODRIVER=dummy SDL_VIDEODRIVER=dummy \
  /workspace/scratch/5ba97739b54c/build-native-app/apps/standalone/hammond_standalone \
  --state /workspace/scratch/5ba97739b54c/native-evidence-a18/fresh.b3controls --smoke-ms 600 \
  --screenshot /workspace/scratch/5ba97739b54c/native-evidence-a18/final-reference.bmp \
  --diagnostics /workspace/scratch/5ba97739b54c/native-evidence-a18/final-reference.json
```

Initial configure without explicit DATADIR failed at the existing empty-cache
guard after SDL inclusion. The private build used `share`; root owns the
subsequent CMake correction and its independent fresh/repeated-configure gate.

First strict build and 600ms smoke passed at main SHA-256
`7a741a0e668e7d513451f737dee179ca1a774107d16ebfbf54bda3d0c95d49ff`:
60 callbacks, 30,720 frames, 16 rendered images. Twenty subprocess cases passed:
help/list; twelve invalid CLI cases; 44100/2048 and 96000/128; failed audio driver;
malformed state preservation; Unicode paths; output/state collision preservation.
The no-audio smoke returned 1 with zero callbacks; malformed startup state was
reported and preserved while the declared audition fallback remained playable.

After adding the required open/running-at-shutdown smoke check, strict rebuild
and actual 600ms 1280×900 smoke passed at final main SHA-256
`6b3e5b13dc362495f0bd224a3a046a1129652385faa4d20804a03edd162d6f78`:
56 callbacks, 28,672 frames, 15 images, note On/Off observed, BMP while held,
zero render/format/nonfinite/overrange errors and no held notes after close.
Joined controls exactly retained the proposed registration. These are coordinated
live-source checks; root owns a coherent complete-tree integration result.

## Limits and next handoff

This executor compiled dummy/offscreen video and dummy/disk/OSS audio, without
desktop/audio development backends. No visible desktop, physical device,
latency/underrun, Windows/macOS, high-DPI pointer-capture or native-accessibility
pass is claimed. Maintained native event/modal/reopen/Save/Load workflows remain
assigned acceptance work. No optional temporary event harness was added. Root
will integrate, run the coherent gate and publish; this agent did not commit.
