# Assignment 17: pedal parameter registry and bridge

Owner: /root/w03_a17_pedal_parameters

Date: 2026-11-13. Wave: 3. Status: implemented; focused checks passed.
Publication and the complete integrated gate belong to the root integrator.

## Scope and decision

Implemented the exact two-control extension in the
[pedal integration contract](../../PEDAL_INTEGRATION_CONTRACT.md). Registry
schema 3, model `exclusive-ab-percussion-pedal-console-v3`, contains exactly
45 records. The new IDs are `0x4000` / 16384 and `0x4001` / 16385, paths
`pedal.drawbar.mixture1` and `pedal.drawbar.mixture2`, labels **Pedal Mixture 1**
and **Pedal Mixture 2**. Both are retained integer positions 0–8, default zero,
with eight intervals. They emit `PedalDrawbar = 12`, canonical Lower, indices
0 and 1. Their kind is `pedal_drawbar_position`; position normalization is
separate from the voice's named audio-gain law.

The existing exact half-up converter was retained. All eight binary-exact
thresholds choose the higher position at equality; each immediate predecessor
chooses the lower position. No original conversion, expression meaning, ID,
default or record metadata changed. The offline diagnostic keeps its own
outer schema 1 while reporting registry schema 3 and all 45 compiled records.
Both host-verification flags remain false.

Owned changes: `data/parameter-registry.json`, new immutable
`data/references/parameter-registry-v2.json`, `include/hammond/ParameterBridge.h`,
`src/ParameterBridge.cpp`, `tools/validate_parameters.py`,
`tools/parameter_info.cpp`, the three parameter test files,
`docs/PARAMETERS.md`, `docs/PARAMETER_BRIDGE.md`, and this note. No CMake,
Engine, Types, saved-state or shared status files were edited by this assignment.

## Independent compatibility evidence

Before editing, copied the complete registry bytes directly from committed
parent `6768ef2388819ebbaaf7cc23bdf72265dc72c561` into the immutable version-2
fixture. The compatibility test does not derive the old records from the new
validator or native descriptor implementation. It compares every complete
record and independently freezes these SHA-256 values:

| Oracle | SHA-256 |
| --- | --- |
| Historical fixture bytes | `658858a8e0f3e722ae1deef1c80e799ab5761c60213af22d5e80696996fd50f5` |
| Canonical 43 earlier records | `5e161206e203cce130330b993590d892182c4ead62daba50b468b5348d70bed2` |
| Retained original 39-record oracle | `61669b54e0a0499da950ece28c855e70ab4cb815d204f625f0aee8542d8b4f1b` |

Canonical encoding sorts records by numeric ID, sorts object keys recursively,
uses compact JSON separators and ASCII escaping, then hashes the ASCII bytes.
Tests also verify that reordering does not affect the digest and that changing
an old percussion meaning does. Preserve these oracles for future extensions.
Whole schema-1 and schema-2 registry documents continue to reject explicitly;
this policy is distinct from saved-control migration. Each unchanged historical
record remains usable by the scalar helpers.

## Actual checks

Agent 16 explicitly froze `Types.h`, `Engine.h` and `Engine.cpp` before this
assignment's native build. A fresh, isolated Release build compiled the current
core and both consumers together under GCC 14.2.0, C++20, strict warnings and
`-Werror`; no earlier library was linked against newer live headers. Python was
3.12.14. Build directory:
`/workspace/scratch/f364bc93d920/build-a17-parameters`.

Commands executed from the repository root:

```sh
python3 tools/validate_parameters.py data/parameter-registry.json
python3 tests/test_parameters.py -v
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake -S . -B /workspace/scratch/f364bc93d920/build-a17-parameters -DCMAKE_BUILD_TYPE=Release
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake --build /workspace/scratch/f364bc93d920/build-a17-parameters --target test_parameter_bridge hammond_parameter_info -j 4
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/ctest --test-dir /workspace/scratch/f364bc93d920/build-a17-parameters --output-on-failure -R '^(test_parameter_bridge|python_test_parameter_bridge|python_test_parameters)$'
```

Results: validator accepted the 45-record model; all 28 Python registry tests
passed; the focused CTest selection passed **3/3**, zero failures, 1.62 seconds.
The native suite reported **5,933 independent conversions**, **33,461 atomic
conversion rejections**, all **45 live Engine targets** and all **four supported
rounding modes**. All discrete controls exercise every threshold and immediate
binary64 neighbors, every canonical position, bounds and nonfinite rejection;
continuous expression preserves its value and signed zero. The two new pedal
controls are tested through actual Engine calls, including all nine positions,
held pedal contacts, lower Cancel/reselection, unchanged manual controls,
percussion readiness, frame clock and all 91 source phases.

The cross-language suite passed **10 tests**, making **98 actual diagnostic CLI
calls**. Each successful export checks all 45 compiled records against the JSON,
Python conversion and an exact-rational discrete oracle. It covers threshold
neighbors, canonical positions, subnormals, signed zero, strict CLI failures,
output bounds, environment independence and stdout failures. These checks
exercise the real native executable; no host export is inferred.

Relevant verified source SHA-256 values:

| File | SHA-256 |
| --- | --- |
| `data/parameter-registry.json` | `a80b0f391a37dd9264dc6962131e61c6ba8a0b8ce570d15e89042abe13d148c4` |
| `include/hammond/ParameterBridge.h` | `da68b2e5e2dae211597270924dbdad33c6be8606c5aaa164bd8de92878ea90a0` |
| `src/ParameterBridge.cpp` | `14d7dcfd24f5e7d6d59de8b31999ee52b33c64f73df453bff82b9eaa4f89dce0` |
| `src/Engine.cpp` | `e082d07323c506f58c726c76a8459bbbec9b01fcb7b20ca6d6323c065fa6664c` |
| `tests/test_parameter_bridge.cpp` | `fe9f9d9a5b515bf5c73024ffef08844f0265ad2ea7e8482836ef4ea93e8b95c5` |

## Next integration step and limits

The integrator must run the complete gate on its coherent staged tree and update
the shared status/handoff before commit and push. Reported cross-file follow-up:
`tests/test_install.py` still asserted 43 exported records at the time of this
assignment, while the README parameter row and `docs/HOST_INTEGRATION.md` still
described the earlier registry/state versions. Those files belong outside this
assignment and were reported to root for coordinated integration.

The parameter work closes the offline registry/native-conversion portion of the
pedal contract. Whole-engine acoustic regressions, complete pedal transaction
coverage and the staged publication gate have their own owners. Native VST3
exports, curves, UI gestures and DAW project recall require later actual tests.
No measured mixture, calibrated footage response, manufacturer mapping or
physical-fidelity result is claimed.
