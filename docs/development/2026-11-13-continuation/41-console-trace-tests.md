# Assignment 41 — independent console trace acceptance

Agent: `/root/w07_a41_console_trace_tests`

Wave: 07; assignment 41 of this continuation's 60 new agents

Date: 2026-11-13 UTC

## Scope and independent expectations

Added only [test_console_trace.py](../../../tests/test_console_trace.py) and this
note. The test invokes the actual `hammond_console_trace` executable; it does not
import the exporter, profile compiler, Engine, or another test's model helpers.
The [trace contract](../../CONSOLE_TRACE.md) supplies the versioned schedules and
CSV schema. The [console contract](../../CONSOLE_DYNAMICS.md) supplies the nominal
model, whose proposed coefficients are not physical measurements. Atlas pages
117, 127, 128 and 135 were read for contact history, the separate physical/routed
detector, shared state and the simplified exponential model.

The permanent suite independently transcribes the three millisecond schedules
and computes each event frame by integer floor. It derives contact positions
from exact rational elapsed time and the declared full-travel speeds, retaining
nine independent hysteresis bits per key. It computes readiness from closed-form
constant-detector segments, rather than replaying the production per-frame
recurrence. Source phases use elapsed frequency plus fixed initial answers;
same-frame audio follows the independently predicted contacts, phases, gains
and readiness, with a binary32 rounding allowance.

The fixed phase answers cover source IDs 49 and 56 for seed zero and the maximum
unsigned 64-bit seed. They were derived with independent arbitrary-precision
integer evaluation of the documented SplitMix64 convention. Answers at IDs 46
and 91 were cross-checked against the earlier tonewheel suite's retained constants.
The permanent test contains no PRNG recurrence. Frequencies, amplitudes, output
gain and canonical authoring identity come from the retained authoring JSON,
independently of the trace's claims; the two routed source IDs are fixed anchors.

## Observed result

Strict GCC 14.2.0 Release compilation succeeded. **1/1 CTest suite passed in
4.43 seconds: 10 Python methods, zero skips, 62 actual CLI calls.** The Python
methods took 4.306 seconds. No build/test failure or production defect was
observed, and no production correction was requested.

| Check | Observed scope |
| --- | --- |
| Scenario/rate matrix | Partial, legato and routing at 44100, 48000 and 96000 Hz; 9 complete traces |
| Independent numeric rows | All 67,716 rows, not selected screenshots or sparse windows |
| CSV contract | Exact 28 ordered metadata records and 36 columns; finite numbers, contiguous frames, exact bit syntax, LF output, row/byte bounds and binary32 audio representation |
| Mechanical history | Partial 0.5 holds approached from both directions, their different contact subsets, reversal, full NoteOn after partial hold and immediate panic |
| Percussion and routing | Harmonic audio before ninth-contact detection, one shared legato history, finite recovery, Cancel, A/B routing and percussion Off/On |
| Source continuity | Both tracked free-running phases on every row, including silence and cancelled routing |
| Determinism and seeds | Byte-identical replay with reordered options, leading-zero seed and changed locale environment; maximum uint64 seed accepted with fixed initial answers and unchanged mechanical history |
| Admission failures | Missing/unknown/duplicate arguments; malformed, out-of-range and oversized values; invalid, missing, oversized and unpreparable profiles |
| Destination preservation | Existing regular files, directories, hard links, input/output collision, missing parent and nondirectory parent |
| Publication | Two competing processes leave exactly one complete expected CSV and no temporary remnants |
| Provenance boundary | A changed declared authoring digest is exported explicitly as declared provenance; it is not authenticated or confused with a compiled-byte hash |
| Actual stream failure | A read-only stdout handle causes help output to fail with nonzero status while retaining the destination bytes |

| Independent quantity | Maximum observed absolute error | Acceptance allowance |
| --- | ---: | --- |
| Contact position | `1.4224732503009818e-16` | `3e-14` normalized travel |
| Readiness | `7.671641100159832e-14` | `5e-12` dimensionless |
| Source phase | `2.077227279073668e-13` turns | Circular distance no greater than `frame * 2^-51 + 8e-14` |
| Same-frame audio | `3.7242897099609706e-9` | `2^-23 * max(abs(expected), 0.001) + 1e-10` normalized amplitude; exact zero when the independent path is silent |

These are bounded 120 ms software-model comparisons. The float allowance admits
rounding and the separately bounded analytic phase/readiness differences; it does
not hide a one-sample detector, source, contact or event-order shift.

## Coherent source and actual commands

The qualified source was an archive of commit
`53bb6e1e37eedf84f566ffb8bd9037b50f123a20`, with exactly the seven overlays below.
All production overlays matched their owners' frozen SHA-256 values before copying.
Core, executable and test came from this one source snapshot. The later live
renderer/parser edits were neither needed nor included in this scoped trace gate.

| Overlay | SHA-256 |
| --- | --- |
| `include/hammond/Types.h` | `a8f86c3b0910a5e0921b1ff583b4c947573dfecb955bff2c8341613ffdf95fe0` |
| `include/hammond/Engine.h` | `efb8f0eb36dccbe5f0416186ef9478091be48e5634cfd6a8f0155b3dfd1c81c0` |
| `src/Engine.cpp` | `53c07390447796f4c57e96e58b9d6720df76094e14a0e6240b284f62e4310ccf` |
| `CMakeLists.txt` | `f37c6bd8dedb1325db4f79ed15162b837139254b1f1c2ac100e105b8a2dbfeac` |
| `tools/console_trace.cpp` | `810574b16848ba34ccf3d1e26be10339357230deffc5df4fbb8bab23891b7f75` |
| `docs/CONSOLE_TRACE.md` | `a954a1670131e215e322fa2806c1527efb6998c3f15e6f2776dd056592863996` |
| `tests/test_console_trace.py` | `c2905ac8e4dc6fc5e4aae59058c06cee8cc63be000db47a92d392b4d0574c646` |

```sh
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  -S /workspace/scratch/60e8291da354/a41-trace-qualification/source \
  -B /workspace/scratch/60e8291da354/a41-trace-qualification/build \
  -DCMAKE_BUILD_TYPE=Release
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  --build /workspace/scratch/60e8291da354/a41-trace-qualification/build \
  --target hammond_console_trace --parallel 4
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/60e8291da354/a41-trace-qualification/build \
  --output-on-failure -V -R '^python_test_console_trace$'
```

The executable SHA-256 was
`0334f85343477c427c3de094b3e81802eb2d18d7df664b9f8596ced6cfb66a5c`;
the generated nominal profile was
`b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.
The repository test was byte-compared with the qualified copy after the run.
The permanent test uses CMake-provided executable/profile/source paths; none of
the temporary session paths above is embedded in it.

## Next gate and limits

The integrator must include this test with the trace and partial-key changes in
one full staged-source gate, publish under the standing expected-head workflow,
and observe that revision's hosted platform results. Assignment 40 supplied the
CMake environment registration. No staging, commits, pushes, shared-document
edits or subagents were performed by assignment 41.

This gate did not inject disk-full or mid-write CSV failures or force a specific
publication interleaving. It checks the actual two-process outcome and cleanup.
Local installation, cross-platform/sanitizer execution, live tracing, callback
deadlines, native host/device behavior and physical fidelity remain separate
gates; passing synthetic trace equations establishes none of those claims.
