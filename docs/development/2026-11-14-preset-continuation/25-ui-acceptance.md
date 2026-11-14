# A25 — independent preset UI and raster acceptance

Actual assignment `/root/w05_a25_ui_acceptance`, logical wave 5, 2026-11-14.
The independent [review](../../reviews/PRESET_UI_ACCEPTANCE.md) gives the oracles,
observed defects, retained failures, repairs, visual findings and limitations.

## Owned result

- Added `apps/standalone/tests/test_standalone_preset_ui.cpp`, automatically
  discovered by the SDK-free standalone test glob. The final name deliberately
  matches hosted standalone CI's `^test_standalone_` selection.
- Added `apps/standalone/native_tests/test_standalone_preset_raster.cpp` and its
  narrow native target/CTest registration in `apps/standalone/CMakeLists.txt`.
- After independently reproducing defects and receiving integrator ownership,
  repaired only preset focus painting in `apps/standalone/InstrumentView.cpp`.
  Natural keys keep visible focus at 1400×820; accidental focus avoids repainting
  their scaled labels. UiModel geometry, audio and state APIs are unchanged.
- Wrote this note, the independent review and `reports/a25-*` evidence. No shared
  status, README, next-step, manifest or publication file was edited. No commits,
  pushes, child agents or preserved-build mutations were performed.

## Executed checks

| Check | Result |
|---|---|
| Initial SDK-free target `test_preset_ui_acceptance` | 1/1 pass, 0.07 s |
| Final renamed target `test_standalone_preset_ui` | 1/1 pass, 0.07 s; 12 layouts, 549,388 classified hit points, 288 route transitions, 48 keyboard activations, 144 focus moves and 753 invalid IDs |
| First native raster against A23 renderer | Fail, 11.55 s: 14 missing natural focus indicators, 14 accidental-label pixel changes, four overlapping-C# test-oracle errors |
| Corrected oracle plus natural-only repair | Fail, 12.06 s: all natural/Cancel checks pass; 14 actual accidental pitch-ink changes remain |
| Final native raster | 1/1 pass, 15.45 s: 96 label/focus cases, 376 isolation checks, 48 applied/pending/Cancel/rejection checks |
| Owned-path whitespace check | Pass |

The original Cancel oracle compared C's full bounds, including overlapping C#;
the final oracle uses C's exposed natural face. The final pitch check classifies
high-contrast original glyph ink instead of requiring blank label margins to be
unchanged. Both test corrections and the two real renderer defects remain
explicit in the review and raw logs.

## Reproduction and source identity

Working directory:
`/workspace/scratch/a472c29da8b3/Hammond-B3-Organ`.
Committed base: `35554c068492fe2b20c1f8a602d8354ae762dc42`; tested files also include
the in-progress preset overlay. Initial source was copied before compilation to
`/tmp/hammond-preset-a25/source`; only the owned test/renderer corrections and
rename were then applied to that frozen copy. All linked project code was built
from that copy. The final 1,249-file manifest is
`/tmp/hammond-preset-a25/source-final-manifest.json`, SHA-256
`85f93c43931f416479fb67dc9e4d6fd268f03062fcac70df39e7b22430c7d906`.
All 56 selected current core/UI/drawing/configuration/test inputs matched it.

The actual CMake executable is not on the default PATH. The executed focused
build/test commands use:

```sh
/workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin/cmake \
  -S /tmp/hammond-preset-a25/source -B /tmp/hammond-preset-a25/build \
  -DCMAKE_BUILD_TYPE=Release -DHAMMOND_BUILD_STANDALONE=OFF \
  -DHAMMOND_ENABLE_MIDI=OFF -DHAMMOND_BUILD_VST3=OFF
/workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin/cmake \
  --build /tmp/hammond-preset-a25/build --target test_standalone_preset_ui --parallel 3
/workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin/ctest \
  --test-dir /tmp/hammond-preset-a25/build -R '^test_standalone_preset_ui$' \
  --output-on-failure --no-tests=error

/workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin/cmake \
  -S /tmp/hammond-preset-a25/source -B /tmp/hammond-preset-a25/native-build \
  -DCMAKE_BUILD_TYPE=Release -DHAMMOND_BUILD_STANDALONE=ON \
  -DHAMMOND_SDL2_ROOT=/workspace/scratch/7ffc2842608b/SDL2 \
  -DSDL_ALSA=OFF -DHAMMOND_ENABLE_MIDI=OFF -DHAMMOND_BUILD_VST3=OFF
/workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin/cmake \
  --build /tmp/hammond-preset-a25/native-build \
  --target test_standalone_preset_raster --parallel 3
/workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin/ctest \
  --test-dir /tmp/hammond-preset-a25/native-build -R '^test_standalone_preset_raster$' \
  --output-on-failure --no-tests=error
```

CTest also retained JUnit output and complete logs under the task directory.
GNU C++ 14.2.0/CMake 4.4.4/Python 3.12.14 compiled in C++20 Release with strict
project warnings. SDL 2.32.10 is the existing pinned source at
`5d249570393f7a37e037abf22cd6012a4cc56a71`. No physical window/audio/MIDI or VST3
host is exercised by the raster harness. Final source and executable hashes,
capture-review identities, counters and failure classifications are retained in
[`reports/a25-ui-acceptance.json`](reports/a25-ui-acceptance.json).

## Handoff

Final renderer SHA-256:
`c4be416d5a0e715d26d0d582d6f4539224561e591220bbae165ea2b00a0246e7`.
A28 was notified to rebuild its native application from that renderer. A23's
five inspected full-application frames precede these fixes. The gallery owner
must produce new actual application frames, including the 1400×820 natural-focus
case and a fractional-position focused accidental, before publishing the current
README visuals. A25 separately inspected repaired native-surface QA images at
1400×820 and 1280×900; those are not whole-application screenshots.

Retain both focused tests in the final coherent build. Subsequent material and
perspective work must preserve semantic geometry, all 24 presets and 147 playing
keys, and the applied/pending/Cancel distinction. Literal source-photo equality,
small accidental-label readability, native semantic accessibility and real-device
qualification remain open; passing these software checks does not close them.
