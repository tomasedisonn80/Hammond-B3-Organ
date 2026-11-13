# Assignment 27 — native parameter bridge

Agent: `/root/w05_a27_native_parameter_bridge`

Wave: 05, assignment 27 of the sixty-agent continuation

Date: 2026-11-13 UTC

## Scope and sources

Read the standing instructions, current README/status/next-step/log, milestone
plan and consolidated atlas review. Read atlas pp. 397-398 in full for permanent
identity, internal versus exported host IDs and normalized-law compatibility.
The full registry and its validator/documentation supplied the actual internal
43-control contract. The supplied atlas and registry were not modified.

The parent at this task's implementation check was
`61c6ecbd87f46a91b4d0d975c823eeae2e2fb3f8`, with the continuation's wave-04 changes
already in the shared worktree. The registry used here has raw SHA-256
`658858a8e0f3e722ae1deef1c80e799ab5761c60213af22d5e80696996fd50f5`.
Its schema is 2 and model is `exclusive-ab-percussion-console-v2`.

Owned files:

- `include/hammond/ParameterBridge.h`
- `src/ParameterBridge.cpp`
- `tools/parameter_info.cpp`
- `docs/PARAMETER_BRIDGE.md`
- `CMakeLists.txt`, limited to the executable and its Python-test environment
- This evidence note

No Engine, Types, registry, producer, verifier, shared-status, index or history
changes were made. The work remained unstaged for the integrating agent. No
commits, pushes or additional agents were created by this assignment.

## Implementation and decisions

The native bridge provides a fixed immutable descriptor table for all 43 controls,
checked descriptor lookup, normalized-to-Event conversion and plain-to-normalized
conversion. Metadata literals were materialized from the existing authoritative
JSON during development; the compiled runtime has no JSON dependency. Independent
tests in assignment 28 compare the table against that registry.

All destinations are changed only after complete scalar validation. Undefined
IDs, nonfinite values, out-of-domain inputs and fractional discrete plain values
reject. Typed C++ IDs and offsets have uint32 domains. The offset is passed through
unchanged: block length/order/timing admission belongs to Engine, not a scalar
converter without a clock. Every conversion uses the permanent bank identity.
Same-value selector calls still create events because reselect after Cancel can
reconnect routing. No implicit deduplication or snapshot restoration is invented.

Quantization compares the binary64 input with exact power-of-two thresholds.
Drawbars use odd sixteenths; selectors/percussion use one half. This preserves the
existing internal mathematical round-half-up law without the intermediate-addition
error immediately below a threshold. No rounding-mode change, allocation, file
operation, logging, lock or SDK call occurs in the bridge. Lookup is bounded to 43
records and drawbar threshold comparisons to eight. Expression passes through,
including signed zero. Discrete canonical normalization divides integer values
by the exactly representable maximum 8 or 1.

The `hammond_parameter_info` diagnostic accepts no arguments (U=0.5), `--help`
alone, or exactly `--normalized U`. Its strict decimal token is at most 128 bytes.
It emits diagnostic schema1 with explicit registry schema2/model, all descriptors,
defaults, converted event targets and false native-host qualification flags.
Invalid input returns 1 with empty stdout. Output is constructed before writing,
bounded below 32 KiB, formatted with classic locale/nearest rounding/max_digits10,
escaped ASCII and LF termination. Windows stdout uses binary mode. A failed
stdout write produces a nonzero status. This offline command may allocate; the
core scalar bridge does not.

The frozen header and JSON shape were sent directly to the integrator and
`/root/w05_a28_parameter_bridge_tests` before independent testing.

## Observed checks

Strict Release configuration and targeted build both passed on their first run:

```sh
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  -S . -B /workspace/scratch/60e8291da354/a27-parameter-build \
  -DCMAKE_BUILD_TYPE=Release
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  --build /workspace/scratch/60e8291da354/a27-parameter-build \
  --target hammond_parameter_info -j 4
```

Compiler: GCC 14.2.0, configured C++20 with the repository's warnings-as-errors.
The build includes the current shared core; it is not a claim that an exact
published tree or another platform has been qualified.

A scratch Python smoke called the actual compiled CLI for eight normalized values,
including zero/half/one and adjacent-below drawbar/binary thresholds. It independently
computed the mathematical discrete output using the input's exact integer ratio.
All **344 full metadata/event comparisons** against the registry passed.

Additional observed checks:

- **13 invalid CLI forms/tokens** rejected with exit 1, empty stdout and stderr.
- Omitted U and explicit `--normalized 0.5` produced identical bytes.
- A read-only stdout handle caused exit 1 and the expected output-failure message;
  its pre-existing file bytes were unchanged.
- Successful output sizes were **11,708–11,746 bytes**, below 32 KiB.
- All **seven local documentation links** resolve.
- Scoped `git diff --check` passed for CMake; a separate whitespace check covered
  all five implementation/documentation files, including the new untracked files.

The tested executable SHA-256 is
`62e8e4990e1211eb73bfc918951f8291287c77fcf2b79f94b1650865528b425f`.
The scratch aggregate is `/workspace/scratch/60e8291da354/a27-smoke-report.json`.
Permanent tests do not reference this scratch path. No implementation defect was
found in the assigned focused scope. Before handoff, assignment 28 independently
reported its strict Release/CTest **2/2 pass**, 5,635 native conversions, 25,243
failure-atomic rejections, all 43 live Engine targets and all four rounding modes.
It also reported eight Python methods with 97 actual CLI calls and no defect.
Those checks were run by agent 28, with its own retained commands/results; this
assignment did not count them as its own execution.

## Limits and next step

The IDs/defaults/laws are proposed internal engineering choices, not recovered
atlas companion data or calibrated manufacturer controls. The atlas's fuller
continuous drawbar and discrete host law require an explicit future compatibility
decision. No VST3 exports, automation interpolation, UI gestures, smoothing,
audio-device deadlines or DAW recall are qualified by this bridge.

The 43 scalars exclude route-enable bits and dynamic organ histories; use the
control snapshot contract for coherent restore. The diagnostic target is built
but was not added to the scoped install component in this assignment. A later
packaging task must explicitly choose and test its installed location.

Next: include these six files and assignment 28's independently passing tests in
the full staged wave-05 checkpoint, preserving their separate evidence notes.
The integrator owns shared handoff updates, publication and observed hosted CI.
