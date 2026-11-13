# Assignment 16: actual Engine pedal division

Owner: /root/w03_a16_pedal_engine

Wave 3 of the new pedal session. Implemented the actual Engine path from the
[adopted contract](../../PEDAL_INTEGRATION_CONTRACT.md), consuming the frozen
routing kernel, assignment 13 voice and assignment 14 retained controls.

## Delivered behavior

Appended `PedalOn=10`, `PedalOff=11`, `PedalDrawbar=12` and
`PedalAllNotesOff=13`, preserving `Manual` and event values 0-9. Exact payloads
require canonical Lower and pass the existing whole-call preflight. Preparation
validates a candidate compiled pedal kernel with explicit +1 nominal weights
before installing anything. Each physical press/release changes eight ideal
contacts; all 25 held pedals remain independent of the manual count and panic,
lower Cancel, upper percussion and source history. Controls default to `[0,0]`.

Each positive frame consumes the existing single source-bank frame, computes the
four buses and separate nominal `P`, and then joins the unchanged manual/
percussion arithmetic before common expression/output gain. Zero `P` bypasses
the extra addition, preserving the previous path's signed-zero behavior. No
second source bank, envelope, limiter or polyphony normalization was added.

Copied current queries expose held pedals, two controls and all 200 contact
states. Separate `last_pedal_frame()` exposes `PedalRenderDiagnostics` with
validity, actual absolute sample frame/rate, positions, buses, mixtures and `P`.
Disconnected rendering updates it; flushes, restores and rate changes preserve
its historical tags. Successful fresh preparation invalidates it. Checked
queries and rejected calls preserve their destinations/state.

Owned files: `Types.h`, `Engine.h`, `Engine.cpp`, new
`tests/test_pedal_engine.cpp`, updated [ENGINE_API.md](../../ENGINE_API.md), new
[PEDAL_ENGINE.md](../../PEDAL_ENGINE.md) and this note. No registry, renderer,
CMake, shared status, commits or pushes were changed by this worker. The header/
runtime freeze was sent to root and assignments 17/18 before their builds.

## Coherent verification

Created `/workspace/scratch/f364bc93d920/a16-coherent/source` from root's frozen
wave-2 tree `81b1c30436a239d8c04ffcd1ec658d356eb81acc`, then overlaid the six
frozen PedalVoice/ControlState/ControlStateIO files and four owned runtime/test
files. Checked overlay SHA-256 values before/after copying and again after the
tests. This avoids mixing live changed layouts with an older library. The test
snapshot deliberately retains the earlier parameter bridge; assignment 17 owns
its separate gate and root owns combined regression.

From the snapshot's parent, using task-local CMake/CTest 3.31.6, GCC 14.2.0 and
Python 3.12.14:

```sh
cmake -S source -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --target test_pedal_engine test_engine \
  test_console_engine test_engine_rate test_realtime_console -j 3
ctest --test-dir build \
  -R '^(test_pedal_engine|test_engine|test_console_engine|test_engine_rate|test_realtime_console)$' \
  --output-on-failure -V
```

Result: **5/5 suites passed, zero failures, 2.22 seconds**. No runtime repairs or
test retries were needed. The new Engine suite reported **1,442 exact audio
comparisons, 11,921 exact phase comparisons and 19 rejected-event transactions**.
It includes an independently calculated source-one pedal fixture, eight-contact
closures including a null, idempotent targets, both manual contact modes,
percussion independence, muted signed-zero output, 122+25 occupancy, current versus
historical diagnostics, disconnected output and lifecycle failure preservation.

The existing console suite retained 1,179 source/audio oracles, 318 closed-form
readiness checks, 42 partition/disconnected comparisons and 16 failure cases.
The rate suite retained its 36 rate-pair scenarios, 81 rejected changes and
32,603 exact audio frames. The baseline realtime suite passed with calibrated
zero C++ allocation/deallocation results; its existing workloads do **not**
establish enabled-pedal allocation instrumentation. That remains a separate
integration gate.

| Tested owned file | SHA-256 |
| --- | --- |
| `include/hammond/Types.h` | `c533cc0b59838e22aff1dd081e30482df76c747407ea76d4b1788e0536a3ef7b` |
| `include/hammond/Engine.h` | `b2aea1dae1e54654cacb8576295b27d47673c87a9a01e17fd3eba7a843fa188c` |
| `src/Engine.cpp` | `e082d07323c506f58c726c76a8459bbbec9b01fcb7b20ca6d6323c065fa6664c` |
| `tests/test_pedal_engine.cpp` | `17ad6af9b42c8d1659ca2b7d9c289284f681429694821b28097cc6d31bd00371` |

The six dependency hashes match the frozen
[assignment 13](13-pedal-voice.md) and [assignment 14](14-pedal-state.md) records.
`git diff --check` passed for the tracked owned files; separate checks verified
new-file whitespace, line endings and local documentation links. These are
working-source results, not a claim about a later published commit or CI job.

## Next concrete gate

Assignment 18 should finish the independent CSV-based actual-Engine oracle,
partition/disconnected/rate scenarios and enabled-pedal runtime instrumentation.
Root should rebuild all consumers from the combined frozen source tree, qualify
the parameter/renderer integration and publish only observed passing work. This
assignment does not close physical pedal response, complete M3, native host
qualification or concurrent UI publication. Replacement electrical models must
retain explicit identity/units and keep their dynamic histories separate from
musical controls.
