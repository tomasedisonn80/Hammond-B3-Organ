# A18 — standalone Session and preset UI model

Assignment: `/root/w03_a18_session_ui_model`, logical wave 3. Implemented on
2026-11-14 in the shared continuation checkout. The inspected committed base is
`352a398e4f004467c2dab081168be3d8b5206ea9`; the executed build also includes the
uncommitted A13–A17 dependencies and the owned changes below. The base commit
alone does not identify this tested implementation.

Read the repository instructions, complete project plan, current continuation
records, the frozen selection/core/state/UI contracts and adapter audit. This
assignment changes only the two standalone implementation/header pairs, their
three assigned tests, and this note. It makes no commit or push and dispatches
no additional workers. Shared status, publication, native rendering, diagnostics
and independent acceptance remain with their assigned owners.

## Implemented behavior

- `Session` admits offset-zero `SelectPreset` controls. Existing payload
  validation still occurs at the callback boundary through `PerformanceInput`
  and Engine; malformed offsets and complete invalid snapshots still reject
  before queue admission. FIFO sequence, recovery and ownership behavior remain
  the existing Session contract.
- Atomic publication remains **22 words**. Word 4 bits 32–39 and 40–47 now copy
  the raw Upper/Lower fixed modes, with explicit `0xff` masks on encoding and
  decoding and compile-time shape/range assertions. The first 36 drawbar bytes
  and all word-5 bank/route/percussion/pedal fields retain their positions.
  Cancelled fixed memory is preserved independently of effective selector 0.
- `UiControlKind::PresetKey = 19` is appended after unchanged `MidiSettings = 18`.
  `UiLayout::preset_key_panels[2]` is appended. Preset controls have canonical
  IDs `{PresetKey, manual, A, index}` for indices 0–11, and map through the shared
  parameter bridge to 20480/20481. Invalid manual/bank/index IDs preserve state.
- Exactly 24 preset controls replace the six PLAY A/B/Cancel rectangles. The
  layout has **64 ordinary controls**, **147 independent playing-key records**,
  and **67 Tab stops**. Legacy `SoundingBank` and `CancelManual` activation still
  work, without geometry or Tab entries.
- Both manual cheeks now exist at every admitted size, using the frozen
  156–168-unit rail rule and shared preset-panel/key rectangles. EDIT A/B moves
  between rack and cheek at height 820. The twelve presets remain in semantic
  pitch order; hit testing explicitly checks accidentals before naturals.
  The complete candidate layout validates its fixed inventory and visible
  geometry before replacing the prior layout. The renderer must separately
  paint naturals before accidentals, then focus, using these same rectangles.
- A fresh preset pointer-down or Space/Enter activation creates one copied
  controls command, including an explicit reassertion of an already selected
  key. Duplicate Down/repeat input and release create no further command.
  Presets acquire neither pointer capture nor note owners and do not glissando.
  `external_parameter` retains its existing unchanged-value no-op policy.
- Left/Right and Home/End change preset focus within the same octave; Up/Down
  choose the same index on Upper/Lower. Navigation changes no controls or roving
  playing-key indices. Resize keeps semantic preset focus and independent notes.
  Bank editing, desired/applied separation, dirty tracking, pending sequence
  acknowledgment, rejection and recovery use the existing paths with the now
  complete snapshot.

The public header was announced stable to the integrator before renderer work.
There are no new view fields: desired controls are `view.controls`; sounding
selection must derive from `view.applied.controls` using the checked effective
selection helper. Renderer work must also include fixed mode in upper-B
percussion eligibility and must never latch C visually.

## Executed qualification

Copied all 20 current core `.cpp` files, their 24 public headers, the four owned
standalone source/header files, the three assigned tests and `TestSupport.h`
into `/tmp/hammond-preset-a18/source` before compiling. The 52-file manifest is
`/tmp/hammond-preset-a18/source-manifest.json`, SHA-256
`86e6cc3f2a83e71d8de2a689e186cfc2f8f267405a11f05709efd2e639bf30c0`.
A post-test hash comparison found **no differences** between those copied
sources and the corresponding live source files. No old library was linked
against the enlarged current headers.

Copied the existing generated pedal/scanner headers and compiled profile from
`/workspace/scratch/a472c29da8b3/build-baseline`, and the admitted fixed data from
`/tmp/hammond-preset-a13/generated`. The preserved baseline build was neither
reconfigured nor rebuilt. The isolated harness compiles all copied core sources
plus `Session.cpp`/`UiModel.cpp` into one static library and links the three
assigned test executables. It excludes SDL rendering, VST3, and native devices.

The initial unqualified `cmake` invocation failed with exit 127 because CMake is
not on this shell's PATH. Reading the baseline CMake cache identified the
existing executable. The successful commands, from the repository directory,
were:

```sh
/workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin/cmake \
  -S /tmp/hammond-preset-a18/source -B /tmp/hammond-preset-a18/build \
  -DCMAKE_BUILD_TYPE=Release
/workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin/cmake \
  --build /tmp/hammond-preset-a18/build --parallel 3
/workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin/ctest \
  --test-dir /tmp/hammond-preset-a18/build \
  -R '^test_standalone_(session|ui|external_control)$' \
  --output-on-failure --no-tests=error
git diff --check
```

Toolchain: GNU C++ 14.2.0, CMake/CTest 4.4.4, C++20 Release, with
`-Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror`.
All compilation succeeded. CTest passed **3/3 in 0.38 seconds**. The retained
local detailed output is `/tmp/hammond-preset-a18/build/Testing/Temporary/LastTest.log`.
`git diff --check` passed.

| Suite | Observed result |
|---|---|
| `test_standalone_session` | Pass, 0.35 s. All 100 raw fixed-mode pairs × 16 remembered-bank/route combinations survive queue/render/publication, including negative-zero expression. Hidden invalid enum bytes 10–255 reject for either manual. Both manuals accept all twelve selector events; legacy/new FIFO order, Cancel memory and invalid selector payload recovery pass. The whole suite reports 9 rate/partition scores, 4,929 renders, 157,552 bit-exact stereo samples, 6,432 partition samples, 15,860 coherent snapshots, 5,563 accepted posts, 534 rejected posts, 20 rejected renders, 70 future-output probes and 1,600 fixed-mode publications. |
| `test_standalone_ui` | Pass, 0.02 s. Nine behavioral scenarios; twelve literal size cases including minimum/default/reference, all four 1399/1400 × 819/820 combinations, and extreme admitted aspects. Exact inventory/order, preset accidental boundaries, all 24 pointer and Space/Enter activations, repeat/release suppression, focus-only navigation, 67-stop traversal, retained notes, fixed-aware dirty state and existing pending/recovery paths pass. |
| `test_standalone_external_control` | Pass, 0.01 s. Preset selection survives the full post/render/read/observe path and subsequent unrelated copied UI/permanent MIDI B-bank edits, including cancelled fixed memory. Explicit legacy bank B exits fixed mode even when B is already remembered. |

These are focused author regressions. They do not replace A25 independent UI
acceptance, broader concurrent publication/allocation acceptance, or the final
coherent combined-source suite.

## Tested source and input identities

SHA-256 values identify the exact compiled bytes, independent of the base commit.

| Owned compiled path | SHA-256 |
|---|---|
| `apps/standalone/Session.cpp` | `196bc1872b526854a801ae09fcebf408a76c746e7d8e5f0ebd11d066e978f5af` |
| `apps/standalone/Session.h` | `8c26342cafcad2022aabba273cdc8d22432fa3c450819f238fa8d546bc22528b` |
| `apps/standalone/UiModel.cpp` | `b45b5f7e462f33d91ffe8d1ac495f4bfd8376bc1ed6035a23169dbaba6f30a19` |
| `apps/standalone/UiModel.h` | `4ee7569a81d44b88e7d77f385f3c342b080b83f322717a93bbababc167d01a3e` |
| `apps/standalone/tests/test_standalone_session.cpp` | `61180332f23a0cc248c55809386fb197ad0f2eac4142e2c258d7444ed2ff17e8` |
| `apps/standalone/tests/test_standalone_ui.cpp` | `67fc4ee7889e83b6e8dd3e0b1ba209a65525616f60e4366c911b85f245bd0fa1` |
| `apps/standalone/tests/test_standalone_external_control.cpp` | `bee2220cb8d26eaed47091be2de5374c4df6f43c9ef7d3ac64ba3f50db074fa8` |

| Input or executable | SHA-256 |
|---|---|
| Generated `FixedRegistrationData.h` | `66cbb1a23cb5ebf14844afd6f98e13829c9f69c1511b09d5974ca5a4527157c6` |
| Generated `PedalRoutingData.h` | `efddce2ea3619a7dd9e153382e307928f7aed60bdb8a0318ca6c0e71ee5f6034` |
| Generated `ScannerLineData.h` | `d508e3856e637a8e107364ad2a8fed09893a2e50ae05d99db3d4b3da37a5a082` |
| Compiled `nominal.b3p` | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| Isolated harness `CMakeLists.txt` | `ec02171e447fb4e6c648352ed71c50727cc660f97918c65200de106c6dc6779d` |
| `test_standalone_session` | `8c0c546cf97d19faec0b4191e99421d8bad90d97a034d8d16df7100c175413df` |
| `test_standalone_ui` | `222ab6899b7e5ee594b91813998868a3ed2c0a4820bcd463635ad948341b3a18` |
| `test_standalone_external_control` | `474ee09060cf994ad08eec29fb5cef052f8cb827d71d40d00760158dbe6c481b` |

## Remaining handoff

The renderer owner must consume the stable `UiModel.h` fields, implement the
frozen preset paint/focus/selection/pending treatments, replace obsolete cheek
annotations and Help text, and qualify applied percussion eligibility. Then
capture actual 960×700, 1280×900 and 1672×941 windows plus responsive boundaries;
inspect narrow labels and focus/pending/rejected states. No native raster,
screen-reader, real-device, callback allocation, complete host, physical-latch,
loaded-gain or instrument-fidelity pass is claimed here. Main/benchmark
diagnostics and shared publication/status changes remain outside this ownership.
