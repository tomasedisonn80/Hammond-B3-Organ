# Standalone checkpoint: core and control preservation

**Result:** the published standalone checkpoint preserves the audited nominal
dry-organ implementation, parameter identities, plugin class IDs, compiled
profile and control-state contracts. Two fresh SDK-free Release builds passed
the same **11/11 selected suites**. Forty actual render invocations produced
byte-identical WAV/PCM and matching applicable metrics across the baseline and
checkpoint, including a second pedal block partition. The independently built
renderer executables themselves are byte-identical on this toolchain.

This is assignment **51**, `/root/w09_a51_core_preservation`, performed on
2026-11-13. It compares the specific revisions below; it does not qualify later
native timing/concurrency edits, physical sound, host automation or devices.
The owning [standalone scope](../STANDALONE_SCOPE.md) requires these existing
identities and dry-core behavior to remain authoritative.

## Exact source and build identity

| Item | Baseline | Published checkpoint |
| --- | --- | --- |
| Commit | `ba0d9c9c75bd7a39152470f9f7ddb82287cb01b1` | `649b12c7d1faa7601fde1019e913347c65a6634a` |
| Git tree | `51fd7b24d2f373a693ced8dbde0fba762a3cc434` | `cf63327d857b02029e8c5c6f406cab3d3c6890d1` |
| Archived tracked files | 616 | 842 |
| Archive SHA-256 | `d9adb0ad06c51e05c3094e96e21b0b0cbf0815e5047ebb4f8bb250b4ea174633` | `66fe3544c87f47b034ee33d97ac2ac4abf1e5af7bf50d90611098d5191069d36` |
| Fresh selected-target build | Passed, 35.842 seconds | Passed, 37.601 seconds |
| Selected CTest group | 11/11, 2.97 seconds | 11/11, 3.13 seconds |

Each source was extracted from `git archive` into its own new directory, with
its own new build directory. All tracked Git blob identities and executable
modes were checked before and after the builds and again after replay. No live
worktree headers, previous objects, agent 49's relocated files or concurrent
agent 47/50 edits entered these builds. The preserved PDF has SHA-256
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769` in both sources.

The host was Linux 6.18.57 x86-64, glibc 2.41, GCC/G++ 14.2.0, CMake/CTest 4.4.4
and Python 3.12.14. Both configurations used `Release`, `BUILD_TESTING=ON`,
standalone OFF and VST3 OFF. Actual Engine compile commands use `-O3 -DNDEBUG
-std=c++20` and the same strict warnings, including `-Werror`. Include and output
paths differ as expected. No sanitizer, SDL or VST3 SDK was required for these
selected SDK-free targets. Elapsed times are execution records, not performance
or device-deadline comparisons.

## Source preservation and independent tracks

Every pre-existing file in the following roots retains exactly the same Git
blob, SHA-256, byte length and executable mode at the checkpoint. There are
**196 preserved files** in these disjoint groups, with no deletion, rename or
modification among them.

| Protected baseline group | Unchanged files |
| --- | ---: |
| `src/` | 18 |
| `include/` | 21 |
| `plugins/` | 19 |
| `tools/` | 30 |
| `data/` | 15 |
| `tests/` | 78 |
| `examples/fixtures/` | 15 |

This comparison includes the whole existing Engine, console/contact/percussion
and pedal implementations; state parser/writer; parameter bridge and registry;
VST3 implementation, tests and class IDs; profile compiler and data; and all
retained manual, console and pedal scores. It does not say that every repository
file is unchanged: the standalone app, tests, assets, chapel tools and supporting
documents are new, and top-level CMake integrates the optional adapter and
documentary catalog.

The independently integrated [rotary scope](../ROTARY_SCOPE.md) adds
`RotaryMotion.cpp`, two rotary headers, a profile/schema and offline validation
tools/tests. The core archive consequently has 19 members instead of 18. Actual
`ar t` output names `RotaryMotion.cpp.o` as the sole added member; `nm -C` finds no
`RotaryMotion` symbols in either renderer. More strongly, the renderer bytes and
the rendered samples are identical below. This is consistent with the declared
boundary that the rotary research module is not inserted into Engine's graph.

The independent [calibration scope](../CALIBRATION_SCOPE.md) adds offline Python
capture/session tooling and tests. It changes none of the protected pre-existing
files in this comparison. These two tracks are preserved additions, not work
attributed to the standalone adapter. This audit makes no new scanner numerical,
rotary physical or calibration claim.

Selected matching source identities provide a compact spot-check for a later
integrator; the private source inventories retain every tracked file.

| File | Common SHA-256 |
| --- | --- |
| `src/Engine.cpp` | `e082d07323c506f58c726c76a8459bbbec9b01fcb7b20ca6d6323c065fa6664c` |
| `include/hammond/Engine.h` | `b2aea1dae1e54654cacb8576295b27d47673c87a9a01e17fd3eba7a843fa188c` |
| `src/ParameterBridge.cpp` | `14d7dcfd24f5e7d6d59de8b31999ee52b33c64f73df453bff82b9eaa4f89dce0` |
| `src/ControlStateIO.cpp` | `a1043d29d2321cccad4e994afbf62e16d93ce6cd15ce5c7593556daff1b0a8cf` |
| `data/parameter-registry.json` | `a80b0f391a37dd9264dc6962131e61c6ba8a0b8ce570d15e89042abe13d148c4` |
| `plugins/vst3/PluginIds.h` | `2bc93839216f52d5920046931d83ba14fd2d01e15fdbdd477b71b15ebb8415fc` |
| `data/profiles/nominal-unmeasured-v1.json`, raw file | `d17a266ed97cbbd3a2925ebebafafbd6c0e3f84763635732e0a9351d0eab2bff` |

## Parameter IDs, state formats and generated inputs

Both actual `hammond_parameter_info` executables emitted byte-identical JSON for
no argument, `--normalized 0`, `--normalized 0.5` and `--normalized 1`. Each output
contains 45 distinct IDs and 45 distinct paths under registry schema 3 and model
`exclusive-ab-percussion-pedal-console-v3`. Equality covers units, ranges,
defaults, step counts and resulting Engine events, not just the record count.
The default invocation also equals the explicit midpoint within each build.

| Normalized input | Output bytes | Common SHA-256 |
| --- | ---: | --- |
| Default or explicit 0.5 | 12,298 | `71d300d5e074b7b00b28ac801739d47834898235ba286bf1efa80c1d2b65182c` |
| 0 | 12,294 | `ab6fac123144a6d30d6f2976bce778e25289f3c1090cef9e812c505d1ce3c2c1` |
| 1 | 12,294 | `abc080427320a8b0c99dfbe1b56323a684067f915e1772b6ebaf43c00314c22a` |

The unchanged VST3 class definitions are processor words
`19F9ADC0 533F42B4 B96BD51D 6547E838` and controller words
`0DEE76AB 26BC475A BF64F138 C89FB0E0`. This is source-identity verification of
[`PluginIds.h`](../../plugins/vst3/PluginIds.h); these SDK-free builds do not
inspect a native module's exports. The parameter tool correctly retains
`host_exports_verified: false` and `native_host_curves_verified: false`.

The current state grammar remains `B3CONTROLS3`. The selected tests execute
literal v1, v2 and v3 fixtures: v1 supplies off/second/normal/slow percussion and
zero pedal controls; v2 retains its percussion and supplies zero pedals; v3
retains both pedal positions. Old version markers are not accepted as migration
of a newer body. Canonical decimal behavior, retained A/B banks, route bits,
expression, percussion, malformed input rejection and preservation of the
destination on failure are exercised by the unchanged acceptance tests.

Observed current-run results include 590 malformed-document preservation cases
in `test_control_io`; 105 pedal round trips, 162 legacy migrations, 133 rejected
documents and 494 rejected snapshots in `test_pedal_controls`; and 5,933
independent conversions, 33,461 rejected conversions and all 45 live Engine
targets in `test_parameter_bridge`. The bridge covers all four rounding modes.
These are counters printed by the actual successful test executables, not new
coverage inferred merely from unchanged source.

Both builds regenerate these inputs independently and obtain identical bytes:

| Generated input | Bytes | Common SHA-256 |
| --- | ---: | --- |
| `nominal.b3p` | 4,545 | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| `PedalRoutingData.h` | 13,333 | `efddce2ea3619a7dd9e153382e307928f7aed60bdb8a0318ca6c0e71ee5f6034` |
| `ScannerLineData.h` | 1,104 | `d508e3856e637a8e107364ad2a8fed09893a2e50ae05d99db3d4b3da37a5a082` |

## Actual render parity

The retained [`compare_legacy_renders.py`](../../tools/compare_legacy_renders.py)
ran all eight cataloged manual/console scores in three forms: baseline, current
with its ordinary default pedals, and current with explicit `--pedal-drawbars
00`. All **24 renders** have exact WAV/PCM equality and matching retained
metrics, with zero clipping. This includes two manuals, held bank selection and
Cancel, both fold boundaries, nominal contact travel, percussion legato and
routing/masking behavior. All use the catalog's 48 kHz rate and 127-frame blocks.

The independent audit then invoked both renderers on all four retained pedal
scores using 127-frame and 1-frame blocks: **16 more renders**. All four outputs
per score are byte-identical, including WAV headers. All metrics except the
intentionally different `block_size` field are exactly equal. Additional
literal catalog expectations require identical stereo channels, zero clipping,
nonzero content within each audible span, exact silence in every declared
silent span and a positive peak no larger than the declared bound.

These scores exercise two distinct pedal mixtures, coherent sharing of ToneId
13 with a lower-manual note and another pedal, separate release authorities,
held muted pedals, lower Cancel/reselection/panic, the pedal-8 disconnected
contact boundary, and the original two-manual/pedal C-F-G-C phrase. They do not
establish a physical pedal octave or measured instrument timbre.

Across both groups, **40 actual renders process 3,241,200 frames**. Representative
complete WAV identities, equal across every compared form of each score, are:

| Score | Frames per render | Common WAV SHA-256 |
| --- | ---: | --- |
| `two-manual-changes-v1` | 192,000 | `9c46d82dc8da8ba5be078e895765e98672b51a30da52e0684d75a293aa4d84fd` |
| `held-bank-cancel-v1` | 144,000 | `5a55f8fa6583a52abae58a9dc048a765082a11b2168b17a1d0f0078ad81cc09e` |
| `console-percussion-legato-v1` | 42,000 | `8fed69e2aed6af4979cd74136d34e52b992644930f85cd43c01509dd681663c3` |
| `pedal-mixtures-v1` | 48,000 | `24c1367e9ffa4d4bf80a79891036b23e661354fd506420a0f9664db8b5185ae6` |
| `pedal-shared-source-v1` | 57,600 | `0e1442790fdb6e5b425126a95f2442f7ed1d323fe682f0457ef37fb51faaa39f` |
| `pedal-held-routing-v1` | 57,600 | `120001c205c0ceeda08fbdbf91d7b14e51212fc3c2f7dfe2584d5c55517e4dd1` |
| `pedal-phrase-v1` | 144,000 | `a3d1958189e811b8e353a75380d380016db5286eb08a2005626d95df64dde6f1` |

The independently built `hammond_render` executables are each 135,320 bytes,
SHA-256 `9b80a370078e87b4535b6d4d7fee7ed79f9949c443f1bd0432ed54b21c9e39b6`.
The `hammond_parameter_info` executables are each 41,176 bytes, SHA-256
`e66ebd2334836874f045d1a92fd456796b1e74bc495804220abfd8f3c7ed0e23`.
This byte identity is an observed same-toolchain result, not a portable binary
reproducibility promise for different compilers or configurations.

## Executed recipes and retained evidence

The private audit root is
`/workspace/scratch/5ba97739b54c/a51-core-preservation`. `baseline-source` and
`current-source` contain the frozen archives; `baseline-build` and
`current-build` contain their distinct builds. The exact command vectors, cwd,
UTC timestamps, durations, return codes and complete outputs are retained in
`records/` and `logs/`. All 31 recorded outer commands returned zero; the legacy
comparator separately retains the command and output for its 24 child renders.
No failed execution, retry, altered assertion or skipped selected test occurred.

The actual build/test recipe for **each** source is reproduced below, using
`SOURCE` and `BUILD` for the corresponding private directories. In the recorded
execution, the two independent source/build jobs ran concurrently.

```sh
CMAKE='/workspace/scratch/1742da7072be/build-tools/lib/python3.12/site-packages/cmake/data/bin/cmake'
CTEST='/workspace/scratch/1742da7072be/build-tools/lib/python3.12/site-packages/cmake/data/bin/ctest'
"$CMAKE" -S "$SOURCE" -B "$BUILD" -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
"$CMAKE" --build "$BUILD" --parallel 2 --target \
  hammond_render hammond_parameter_info \
  test_control_io test_controls test_parameter_bridge test_pedal_controls \
  test_percussion_controls test_console_engine test_pedal_engine \
  test_performance_acceptance test_performance_input
"$CTEST" --test-dir "$BUILD" -C Release -V --no-tests=error \
  -R '^(test_control_io|test_controls|test_parameter_bridge|test_pedal_controls|test_percussion_controls|test_console_engine|test_pedal_engine|test_performance_acceptance|test_performance_input|python_test_parameters|python_test_parameter_bridge)$'
"$BUILD/hammond_parameter_info"
"$BUILD/hammond_parameter_info" --normalized 0
"$BUILD/hammond_parameter_info" --normalized 0.5
"$BUILD/hammond_parameter_info" --normalized 1
```

The legacy replay used the current frozen source's unchanged comparator:

```sh
AUDIT='/workspace/scratch/5ba97739b54c/a51-core-preservation'
python3 "$AUDIT/current-source/tools/compare_legacy_renders.py" \
  --baseline-renderer "$AUDIT/baseline-build/hammond_render" \
  --baseline-profile "$AUDIT/baseline-build/nominal.b3p" \
  --current-renderer "$AUDIT/current-build/hammond_render" \
  --current-profile "$AUDIT/current-build/nominal.b3p" \
  --output-dir "$AUDIT/legacy-comparison"
```

The output directory must be new. To reproduce the separate pedal comparison,
invoke each renderer on every fixture in
[`pedal-catalog-v1.json`](../../examples/fixtures/pedals/pedal-catalog-v1.json),
using its `frames`, `sample_rate`, `seed`, `registration`,
`pedal_registration`, score file and four `controls` fields. Run `--block-size
127` and `--block-size 1`, each with `--fail-on-clip` and a fresh WAV output.
The expression is set by each score's frame-zero command. Compare complete WAV
bytes and parsed JSON excluding only `block_size`, then check the declared
silence/audible spans, peak bound, stereo identity and zero clipping. The private
`run_replays.py` retains these exact checks and all 16 argument vectors.

`legacy-comparison/comparison.json` is 87,953 bytes, SHA-256
`f87e18798995469bbfdff062c5427fc3fa403edfc0368e226d463bd41fd2e4a8`.
`preserved-source.json` is SHA-256
`efb987795ebaf4f25bffb935f8f6df3bf77276034b1127d256e3c7fc12045d46`.
The private `parity-results.json`, SHA-256
`61ba47f2dde54ef8f1a8decd8e843c394b1da62fc75bba1208ad8c873ce0ea73`,
additionally retains all pedal WAV and PCM digests, complete render metrics,
parameter outputs, generated-input identities, archive members and the
source-reverification result. These private artifacts are supporting execution
records; the recipes and substantive results are retained here for a future
checkout.

## Limits and next step

No production repair was necessary or made. This assignment owns only this
report and [its session note](../development/2026-11-13-next-phases/51-core-preservation.md).
It is a preservation audit of exact Linux Release sources, not a full-core
CTest run, native ABI/host test, sanitizer pass, 44.1/96 kHz cross-build render
comparison or physical-model acceptance. Existing selected tests contain their
own rate/state cases, but the explicit render parity here is at 48 kHz.

The integrator should retain the native timing and concurrency qualification
gates, freeze the completed adapter repair with its consumers, and execute the
assigned full-source and hosted acceptance. Before carrying this preservation
conclusion to a later checkpoint, inspect the protected paths and generated
inputs against the named revision. Any change to Engine, parameter/state
contracts, compiler inputs or audio graph needs the relevant new evidence.
The broader M3–M8 physical dependencies in the [plan](../PLAN.md) remain open.
