# Assignment 28 — independent native parameter bridge tests

Agent: `/root/w05_a28_parameter_bridge_tests`

Wave: 05, assignment 28 of this continuation's 60 new assignments

Date: 2026-11-13 UTC

## Scope and source basis

Read the standing instructions, current status/next steps/log, full project plan,
atlas review, [registry contract](../../PARAMETERS.md), independent Python
converter and atlas pp. 397-402. The atlas motivates permanent identities,
historical normalized laws and explicit host qualification; the repository's
43-ID inventory and discrete round-half-up law are its own proposed internal
contract. They are not the absent 62-record companion or verified VST3 exports.

Agent 27 supplied the frozen public header and diagnostic JSON contract. This
assignment owns only:

- [tests/test_parameter_bridge.cpp](../../../tests/test_parameter_bridge.cpp)
- [tests/test_parameter_bridge.py](../../../tests/test_parameter_bridge.py)
- This note.

No production source, registry, CMake, shared status, index, commit or remote
was modified by this assignment. No subagents were spawned.

## Independent native evidence

The C++ test contains a separately transcribed 43-row ID/type/manual/index/default
inventory. It does not derive expected targets from the bridge's descriptors.
It checks complete descriptor membership/order, unique paths, copied lookup,
canonical defaults and all holes through ID 12292 plus upper uint32 boundaries.

There are **5,635 exact successful conversion comparisons** and **25,243 rejected
conversions** whose destinations retain every semantic field and binary64 payload
bit. Descriptor rejection is checked separately for all 12,254 undefined IDs in
the enumerated range/boundary set. Invalid values include nonfinite numbers,
negative subnormal values, out-of-range adjacent floats and fractional plain
values for discrete controls. Valid positive subnormal expression values and
signed zero are preserved. Valid discrete subnormal normalized inputs select
zero; they are not incorrectly rejected merely for being small.

All eight drawbar half thresholds and the binary threshold are checked at the
exact value and both immediate binary64 neighbours for every applicable ID,
under `FE_TONEAREST`, `FE_DOWNWARD`, `FE_UPWARD` and `FE_TOWARDZERO`. Every canonical
plain setting round-trips under those modes. The caller's rounding mode is
unchanged by successful and rejected conversions. Offset zero, an ordinary offset
and the uint32 maximum are copied exactly; Engine retains block-admission ownership.

The test then applies all **43 native targets to an actual prepared Engine** and
compares the complete expected retained-control snapshot after each event. It
checks hidden Upper-A edits while B is selected and cancelled, same-value B
reselection after Cancel, source-phase continuity for all 91 sources, unchanged
contact/readiness history and no elapsed render time during zero-frame updates.
A successfully converted but out-of-block offset is atomically rejected by Engine,
including unchanged output, controls and clock.

## Cross-language and actual CLI evidence

The Python suite has **eight methods** and makes **97 actual diagnostic CLI calls**.
Every successful inspected JSON document has the independently frozen exact root,
record and event field sets, integer versions/IDs/indices, sorted 43-ID inventory,
model/status boundaries, finite numbers and the stated output bound.

Compiled paths, kinds, units, domains, defaults, steps and event targets are
compared with the validated registry. Native plain results are compared with the
independent Python converter and an exact integer-ratio quantization oracle.
The original 39 complete records must retain the fixed historical digest:

```text
61669b54e0a0499da950ece28c855e70ab4cb815d204f625f0aee8542d8b4f1b
```

Actual CLI cases include every threshold/neighbour, canonical positions, signed
zero, minimum positive subnormal/normal values, adjacent-to-one inputs and an
ordinary noncanonical expression. Decimal spelling, the 128-byte input boundary,
explicit versus implicit defaults, LF/ASCII output and locale-environment
independence are covered. Setting locale environment names does not claim that
those locales are installed; it verifies the command's explicit classic-locale
output policy.

Thirty-eight malformed CLI invocations reject with nonzero status, diagnostic
stderr and empty stdout. A real read-only stdout handle exercises the portable
output-failure path while retaining the destination's bytes. The JSON reader
preserves the valid spelling `-0` when inspecting expression signed-zero behavior.

## Observed commands and results

The strict Release build used GCC 14.2.0 and Python 3.12.14. Build products are
outside the repository at `/workspace/scratch/60e8291da354/a28-parameter-build`.

```sh
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  -S . -B /workspace/scratch/60e8291da354/a28-parameter-build -DCMAKE_BUILD_TYPE=Release
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  --build /workspace/scratch/60e8291da354/a28-parameter-build \
  --target test_parameter_bridge hammond_parameter_info -j 4
/workspace/scratch/60e8291da354/a28-parameter-build/test_parameter_bridge
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/60e8291da354/a28-parameter-build \
  --output-on-failure -R '^(test_parameter_bridge|python_test_parameter_bridge)$'
```

- Strict warning-as-error compilation: **passed** on its first test build.
- Native executable: **passed**, with the counts above.
- Direct Python suite against agent 27's built executable: **8/8 passed** in
  0.330 seconds, zero skips, 97 actual CLI calls.
- CMake-discovered native/Python gate against this assignment's build:
  **2/2 passed** in 0.41 seconds.
- New-file whitespace checks using `git diff --no-index --check /dev/null FILE`:
  no diagnostics. Their status 1 denotes a new-file difference, not whitespace
  errors.
- No implementation defect or weakened assertion/tolerance was required.

The completion-time repository HEAD was `7bbd8e75deeef6e20393b89ce1b42ef005a4c74c`;
wave-05 files were still unstaged working additions. This scoped gate is not a
claim that that commit contains or qualifies them.

| Tested item | SHA-256 |
| --- | --- |
| `ParameterBridge.h` | `a39e7dd02e595d4687e706f28200c4ad8a247520a80dd2187773df6ef1355237` |
| `ParameterBridge.cpp` | `e6dc1b0e1721e00fd89b3f2614f97ecd9b4aaf9bffd998468185c15fd15627e5` |
| `parameter_info.cpp` | `42dc8f8fb1dede6343af7785ed6a055f28a5dd2bfe624404c585ceef0ff88223` |
| `test_parameter_bridge.cpp` | `d32f71ae4b29e23fb5201a1535a1de8e3427a2268227d7a853a8d85810883794` |
| `test_parameter_bridge.py` | `18f689fd59e535ce274b7fbd34058ab65963ecf67f948d55b229b5e44f18ed86` |
| Built `hammond_parameter_info` | `62e8e4990e1211eb73bfc918951f8291287c77fcf2b79f94b1650865528b425f` |
| Built `test_parameter_bridge` | `ea888f0d4e82e9288fd119fc4ad324c2d287ab47b37023732ab834976d268bb1` |
| Built `nominal.b3p` | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |

## Limits and next step

These are software mapping, CLI and retained Engine-control checks. They do not
establish native automation curves, queue merging, gestures, DAW recall, exported
VST3 IDs, audio deadlines, device playback or physical console fidelity. No
allocation instrumentation is claimed by this assignment. Platform qualification
requires the integrator's combined staged-source gate and observed hosted matrix.

Next: include the bridge, diagnostic, CMake changes and these tests in the wave-05
checkpoint. Preserve the frozen old-ID law and failure/offset boundaries when a
future native host adapter supplies actual parameter queues.
