# Assignment 24 — end-to-end console evidence acceptance

Agent: `/root/w04_a24_console_evidence_acceptance`

Wave: 04 of the continuation's ten work waves

Date: 2026-11-13 UTC

## Scope and inputs

Read `AGENTS.md`, the current status/next-step/development log, the continuation
ledger, project plan and atlas review, console dynamics and evidence contracts.
Read atlas pp. 127, 128, 134 and 135 directly from the existing complete text
extraction. The central requirements are one shared upper-B process, detector
contact index 8 independently of audible registration, shared selected-harmonic
audio and finite charge/recovery history. The isolated RC times and present gain
map remain named nominal hypotheses, not acquired circuit measurements.

Agent 21 owns the independent schema-1/schema-2 verifier migration; its stable
interface was used without editing its files. Agent 23 independently owns the
new console fixture catalog. This assignment does not depend on that catalog.

Only these new files were written:

- `tests/test_console_evidence.py`
- `docs/CONSOLE_ACCEPTANCE.md`
- This note.

No production code, existing tests, shared status files, CMake, index, commits or
remote refs were changed by this agent. The parent integrated incoming remote
`61c6ecb` during the assignment; it did not overlap these files. The tested binary
was already built before that integration, so full combined-tree publication
verification remains the integrator's responsibility.

## Independent acceptance implementation

The suite builds actual evidence through `run_fixture()`, verifies each bundle
through independent `verify_bundle()`, then decodes and measures PCM separately.
The oracle has its own closed-form decay/recovery calculation and a weighted
two-basis fit with unknown source phase. It copies neither the engine's sample
recurrence nor the source PRNG. Quantization error is propagated through the
finite-window normal system; no statistical noise assumption is used.

Three test methods cover:

1. Ideal-contact shared legato and distinct finite recovery gaps at all three
   supported rates, including duplicate and same-frame release/press operations.
   Eighteen single-tone windows use known detector intervals and assert amplitude
   0.045 within an independently calculated error bound. Silent gaps are exact zero.
2. Nominal-contact harmonic closure before detector closure, active decay and
   detector recovery while the releasing harmonic remains connected. Nine more
   windows cover 44.1, 48 and 96 kHz; surrounding PCM silence is asserted.
3. Six exact WAV/PCM comparisons between blocks 1 and 1024, across both contact
   modes and all three rates. Both sides of every comparison are real verified
   schema-2 bundles, with source/score/compiled-profile/model identities checked.

The normal-percussion amplitude oracle also detects accidental application of
upper sustain compensation to the percussion path. It is independent of retained
drawbar gain because all sustained drawbars are zero.

## Observed commands and results

The parent-provided Release binary and generated nominal profile were used:

```sh
HAMMOND_RENDER_EXECUTABLE=/workspace/scratch/60e8291da354/integration-w04-build/hammond_render \
HAMMOND_TEST_PROFILE=/workspace/scratch/60e8291da354/integration-w04-build/nominal.b3p \
PYTHONDONTWRITEBYTECODE=1 python3 tests/test_console_evidence.py -v
```

Result: **3/3 methods passed in 3.133 seconds**, zero skipped tests, 18 actual
rendered and independently verified bundles, 27 analytic amplitude windows and
six exact partition-comparison pairs. No implementation defect was found.

A second in-process execution of the two analytic methods exported their actual
measurement records for the numerical handoff: **2/2 passed in 0.736 seconds**,
six bundles and 27 windows. Observed values:

| Quantity | Observed value |
| --- | ---: |
| Maximum absolute amplitude error | `1.132816160855088e-6` |
| Smallest calculated error bound | `5.494313067993226e-5` |
| Largest calculated error bound | `1.2158128253878025e-4` |
| Largest error / its own bound | `0.02061797620259823` |
| Required maximum per-window bound | `< 0.0002` |

The temporary measurement export is reproducible from the suite's `measurements`
records; it is not an additional shipped artifact or a physical capture.

Tested renderer SHA-256:

```text
b9c0acab7615820091bd7baaf782d894a8b85bb910a2dfba72b84463445d74c9
```

Tested compiled profile SHA-256:

```text
b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f
```

The permanent tests require CMake-provided environment variables and contain no
session-specific paths. Missing inputs fail explicitly. They use only the Python
standard library, modest bounded durations and temporary directories. Scoped
`git diff --check` passed.

## Limits and next step

The error allowance is one PCM16 step plus `1e-8` for float/short-window numerical
effects, propagated through each measured window. These amplitude checks do not
resolve every sub-LSB or single-sample readiness difference; direct C++ tests own
the tighter state/timing assertions. Exact byte comparisons are same-build only.
This assignment did not execute Windows, macOS, native hosts, device audio or
callback deadline measurements. No physical calibration or authenticity follows
from a retained bundle pass.

The next concrete step is to include these three files in the combined wave-04
staged source tree, let CMake discover `python_test_console_evidence`, run the full
integration gate, publish with the expected-head guard and observe hosted CI.
The parent should link `CONSOLE_ACCEPTANCE.md` from the current user/developer
handoff as appropriate. Subsequent host-ownership and lifecycle work must preserve
these nominal console results while keeping its own acceptance gates explicit.
