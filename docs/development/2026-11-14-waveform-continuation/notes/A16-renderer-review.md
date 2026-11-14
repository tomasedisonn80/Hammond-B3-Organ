# A16 — Actual renderer review and analytical qualification

Actual worker `/root/w03_a16_renderer_review`, wave 3, 14 November 2026.
Inspected HEAD `26ff2fbe66a50260bd7601cbfa54c1f5d35ff3a8`, tree
`530d5fcf777003f470f64558de9e5631d31a21a4`. The R4 sources were uncommitted
at execution; the file identities below, rather than HEAD alone, identify the
qualified code. No production changes or commits were made by this worker.

Read standing instructions, current session scope/checkpoint/actual manifest,
the full M0–M9 plan, atlas review and A04 rotary source reading, frozen numerical,
propagation and renderer contracts, public headers and actual implementations.
Owned files: `tests/test_rotary_renderer.cpp`,
`docs/reviews/WAVEFORM_RENDERER_REVIEW.md`, and this note. Full histories and
rejection snapshots are heap owned. No shared CMake/build/status files changed.

## Outcome

Strict direct compilation and both actual executions pass all six suites.
Nine independent stationary long-double/product-cubic fixtures compare 57,568
output samples: max absolute error `1.4698916354916047e-09`, RMS
`2.0352041431145979e-10`, worst fixture/channel/frame `[8,0,8]`, the high-gain
four-sample overshoot fixture. Per-sample allowance is `5e-9 * sum(path gains)`.
No alignment or gain fitting is used.

Observed 31 process and 36 lifecycle rejections preserve retained histories,
state, diagnostics and watched output; accepted continuation matches a control.
Observed 5,149 consumed events include 5,120 zero-frame alternating events.
End/zero/next-zero order, unchanged anchors, signed separate inputs and impulses,
unclamped output above 900, frozen nonzero-radius geometry, reset, changed/equal
rate epochs, current-speed negative prehistory and explicit tail flushing pass.
Maximum admitted history is 12,806 frames at 192 kHz. An accelerated private
stationary clock fixture checks the one-day rejection boundary; it is explicitly
not a continuously rendered day. No implementation defect was found.

The [review](../../../reviews/WAVEFORM_RENDERER_REVIEW.md) separates source
inspection from executed evidence and records remaining gates. A20 owns actual
late partial-frame/multi-wrap rollback; A26 full partitioning; A27 full symmetry
and rate pairs; A29 calibrated allocations; later independent/hosted work owns
sanitizers and full moving parity. None of R5, device deadlines, Engine integration
or physical fidelity follows from this result.

## Exact build and execution

Environment: Linux 6.18.57 x86_64; `g++ (Debian 14.2.0-19) 14.2.0`.
Working directory: `/workspace/scratch/e3cacb90cc81/Hammond-B3-Organ`.
Build products and compact raw records are in the sibling
`/workspace/scratch/e3cacb90cc81/a16-renderer-review/`.

```sh
g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Wconversion \
  -Wsign-conversion -Wshadow -Werror -ffp-contract=off \
  -DHAMMOND_TEST_PROFILE='"unused"' \
  -DHAMMOND_SOURCE_DIR='"/workspace/scratch/e3cacb90cc81/Hammond-B3-Organ"' \
  -Iinclude -Isrc -Itests tests/test_rotary_renderer.cpp \
  src/RotaryRenderer.cpp src/RotaryHistory.cpp src/RotaryStreamingPath.cpp \
  src/RotaryMotion.cpp src/RotaryPropagation.cpp \
  -o /workspace/scratch/e3cacb90cc81/a16-renderer-review/test_rotary_renderer
/workspace/scratch/e3cacb90cc81/a16-renderer-review/test_rotary_renderer
```

The compiler returned 0 with no diagnostics. No fast-math was enabled; floating
contraction was explicitly disabled. The final normal execution returned 0 in
`0.6772298520008917 s`; the final 1 MiB-stack execution returned 0 in
`0.660490235000907 s`. Python `subprocess.run` captured stdout/stderr and
`time.perf_counter` measured elapsed time. The stack run set the child's
`RLIMIT_STACK` soft limit to `1048576` bytes before exec; the hard limit was
retained. `resource.getrusage(RUSAGE_CHILDREN).ru_maxrss` reported 14,388 KiB
(cumulative child maximum, not a per-call allocation measure). Both stderr
streams were empty and both stdout JSON records were identical:

```json
{"suites":6,"analytical_samples":57568,"analytical_fixtures":9,"maximum_analytical_error":1.4698916354916047e-09,"rms_analytical_error":2.0352041431145979e-10,"worst_fixture_channel_frame":[8,0,8],"rejected_process_calls":31,"rejected_lifecycle_calls":36,"accepted_events":5149,"accelerated_epoch_fixture":true,"result":"pass"}
```

One preliminary timing invocation failed with exit 127 because `/usr/bin/time`
is absent. That invocation did not run the test; Python then ran the executable
successfully. The initial passing fixture was followed only by correcting the
test's temporary input restoration index and adding worst-coordinate reporting.
The final rebuilt source and both final outcomes are identified here. No
sanitizer run was attempted; the integrator assigned that gate separately.

The integrator separately reported an initial shared-build failure because the
new renderer test lacked the private `src` include directory. Root corrected
only the target-private CMake include rule for renderer test targets; the direct
command above already supplied `-Isrc`. This was an integration setup failure,
not a failing renderer assertion. The original failed build and subsequent
shared-build outcome belong to the integrator's records; this note claims only
the independently observed direct builds and executions above.

Raw local files: `release-result.json`, `stack-1mib-result.json`,
`source-identities.json`, and `test_rotary_renderer`. The compact results above
are retained in this tracked note if reproducible local products are removed.

## SHA-256 identities

The independent oracle and all synthetic profile definitions reside in the
test source. There is no separate mutable fixture or random seed; input sequences
use explicit integer modular formulas in that source.

| Input | SHA-256 |
| --- | --- |
| `tests/test_rotary_renderer.cpp` | `43d0e5e1332f63c07c0cd73c5b120d11a7997607c7666c8a53b5ba26c4d4bd7e` |
| `src/RotaryRenderer.cpp` | `b48d82deae98d087493a25976f767c995d4e1db0ae79acb8c699a62dc21c7d04` |
| `src/RotaryRendererInternal.h` | `56a2fb6e0c3af5b7f686e2d2dc2fad07fd7858920657812ba6d4e28153637796` |
| `src/RotaryHistory.cpp` | `4f3c4fbd957f7cc9131b1f4e7c6e77f69df1b7e85c9ba4073de59fe52322a0f5` |
| `src/RotaryStreamingPath.cpp` | `ed79d6ce3653f52f5f9a7d43d4f5cf9743f18cc3c9458ee7734928e42dcbae50` |
| `src/RotaryMotion.cpp` | `a3f986892078254f6dfae936bbbf1b5e1c4967882d06c13b3b28649f2273cfa1` |
| `src/RotaryPropagation.cpp` | `dcc36819747b8d215130c5031a955e4b00af29a114832d0bf273ca60eaaf0c2e` |
| `include/hammond/RotaryRenderer.h` | `5f74af0a7ca629b433fe7f3d72a44a2b39daf90fd2d64afa579aecd26f48ccd0` |
| `include/hammond/RotaryHistory.h` | `9e6930342a5c83bdcf99102aaeb0dc9b0714e85561bd8205a53155a7fca4a25b` |
| `include/hammond/RotaryTypes.h` | `b27ce4934188c24ebe557469fa5191dd7cdcd98a1c3fdbe274b0d7585e4578b4` |
| `include/hammond/RotaryMotion.h` | `7bc81331f84b7ce490bf9047114336e633f3da91a39bbfd2a13e3fd406f61d36` |
| `include/hammond/RotaryPropagation.h` | `c304a1ac99eed6e6e3f80b5107d026880aeb2b5b18499af0a6a7ed3018521a4a` |
| `tests/TestSupport.h` | `8869acab1e7492699b656984c7b24eb6d33f09dad6f989814a8a0c04e3c86be5` |
| Frozen renderer contract | `52eaaeda293376abd47af3f788e3bd5967452b176cba021f23ab7bc3b1e141a9` |
| Frozen numerical contract | `4c060088f0718586a7c6810e5c055c652d8924db4474db770237193ab459bd63` |
| Final executable | `acd2f556d343b0c7119fca8409c67c9eed18d19e5b347541ec01a4f712828d5b` |

Next concrete action: integrator wires `test_rotary_renderer.cpp` to the shared
library/private-header include path and CTest, then preserves this bounded result
while completing the assigned independent late-failure, moving-parity and
allocation gates on a coherent source revision before publication.
