# Assignment 15: comparison metrics and report admission

## Actual assignment and ownership

- Canonical assignment: `/root/cal_w3_a15`, wave 3, assignment 15 of the distinct
  2026-11-13 capture/calibration-readiness session.
- Owned paths: `tools/compare_capture.py`, `docs/CAPTURE_COMPARISON.md` and this
  note. No shared status, manifest, CMake, core, capture-v1 or git mutation.
- Starting checkout and locally recorded `origin/main`:
  `08fa8de8f718584c4ee4ab3b392c779f3290289c`. Other workers' current changes were
  present and preserved. No fetch, commit, push or publication is claimed here.
- Scope: implement the array metric producer and reusable report admission now;
  policy evaluation remains assignment 20, independently tested by assignment
  21. Assignment 18 independently qualifies this metric producer.

## Inputs and source identity

Read repository instructions and the current README, status/next steps,
development-log entry, scanner handoff, plan, atlas-review navigation and active
calibration/rotary/standalone scopes. Read the complete frozen comparison contract,
contract integration review, shared-JSON documentation and implementation, and
the original assignment-09 handoff. This assignment does not claim another full
atlas reading or additional physical acquisition.

The contract's atlas basis remains pp. 187-192, 203, 233, 347, 363-372 and 481-486;
its field names and resource limits are project proposals. The independently
reviewed correction explicitly admits large near-floor comparison ratios and
preserves the corpus `final` to policy `final_test` boundary for later consumers.

| Complete file bytes | SHA-256 used by the executed checks |
| --- | --- |
| `tools/compare_capture.py` | `5165543a66c42ae0dbb1200e38b26cb739bbaa0dfcb3878cc05ce4f665132e3d` |
| `tools/capture_common.py` | `e06dd82e37dd178863af61aa66bee877da1fc7e498a47b729e060215ca79c3f2` |
| `docs/CAPTURE_COMPARISON_CONTRACT.md` | `4ec3037aa0588528fe3c9e520d099cc48a82d78135fc86bd3851c2667860750c` |

The module was uncommitted when checked; the starting commit alone is therefore
not its implementation identity. The integrator owns the subsequent coherent
tree and publication identity. Later policy additions will change the module hash
and need their own retained checks.

## Implemented result

The module exposes `ComparisonError`, the exact frozen `compare_signals` signature
and `validate_comparison_report(comparison) -> None`. It contains no policy stub,
CLI, filesystem access, network access, correction fit or mutable output alias.

Input admission rejects nonexact containers/scalars, Boolean/subclass numbers,
nonfinite values, amplitude/rate/floor violations, incompatible dimensions,
unsorted/duplicate/out-of-band frequencies, short Hann windows and exceeded work.
Geometry/work preflight occurs before spectral work; every sample is validated
before results are built. Binary64 sample conversion and channel pairing are
explicit. The implementation uses bounded per-channel/per-frequency storage.

Pointwise definitions retain all ten fields and use `math.fsum`. Spectral output
retains both complex coefficients, all eight metrics, exact selected frequencies
and every masked row. Rectangular and endpoint-zero symmetric Hann windows use
actual weight-sum normalization without doubling. Signed phase is wrapped to
`(-pi, pi]`; candidate-leading sine/cosine phase is positive. All prescribed
silence/floor/zero-error reasons and their precedence are implemented.

The report gate explicitly calls the common JSON validator with `max_number=2e18`,
65,536 nodes and depth 12, then enforces the 4,096-member bound and exact schema.
It validates constants, channel/frame geometry, work, selected-frequency coverage,
numeric types/bounds, units, known/null values, phase ranges and floor-dependent
reasons/masks. It does not authenticate audio bytes or infer pointwise values
from absent samples. No new recomputation tolerance is silently imposed.

## Executed author checks

Working directory for all commands:
`/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ`.
Toolchain: Python **3.12.14**, standard library only. A directly executed
`PYTHONPATH=tools python3 - <<'PY'` probe performed **433 assertions**, all passing.
It was an author probe, not the independent assignment-18 suite and not a saved
producer-output snapshot used as its own oracle.

| Executed area | Independent expected basis and observed result |
| --- | --- |
| Nine contract pointwise examples | Literal zero, silence, identical, mute, gain-two, quarter-offset, polarity, delayed impulse and sine/cosine arrays. Every pointwise field, metric shape, unit and dB reason agreed with direct algebra. |
| Sine reference / cosine candidate | Coefficients agreed with `-0.5j` and `0.5`; complex error `1/sqrt(2)`, normalized error `sqrt(2)` and phase error `+pi/2`. Observed phase was `1.5707963267948966`. |
| DC, Nyquist and polarity | Constant negative DC retained its signed coefficient, Nyquist amplitude was not doubled, negative-real phase and polarity error were `+pi`. |
| Off-bin leakage | A separately expressed elementary complex-exponential sum for `[1,-2,3,-4]`, `0.375 Hz`, rate `8 Hz` agreed within `2e-14` absolute/relative budget. |
| Hann and pointwise isolation | Literal N=3 weights `[0,1,0]` retained only the middle sample; literal N=5 weights `[0,0.5,1,0.5,0]` gave the expected DC. Pointwise metrics were unchanged by spectral window selection. |
| Floor/null behavior | Both-side and one-side masks, exact floor equality, dB reference/zero/error precedence and retained masked-bin absolute errors passed. |
| Large valid ratio | Reference `nextafter(1e-12,+inf)` and candidate `1e6`, with selected DC, produced `9.999999999999999e17` for pointwise and complex normalized errors. Report validation and finite JSON serialization accepted it. |
| Compensated accumulation | `[1e6,1e-11,-1e6]` DC agreed with the independently specified `1e-11/3` under an absolute `1e-25` budget. |
| Pairing and nonmutation | Opposite biases remained in their two channel positions. Tuple inputs worked. Mutating result containers left original arrays/frequencies unchanged. Rejected report admission left its input unchanged. |
| Work preflight | A 2-channel, 262144-frame, 33-frequency request was rejected while `_frequency_row` was patched to fail if entered. Empty frequency input also avoided that function. |
| Rejected array inputs | Invalid outer/inner containers, mismatched/zero/excessive dimensions, Booleans/subclasses, nonfinite/huge scalars, invalid rate/floor/frequencies/window and Hann lengths 1/2 all raised `ComparisonError`. |
| Rejected reports | Unknown keys, Boolean/float metadata, invalid constants/geometry, negative/nullable always-known metrics, wrong units/reasons, excessive/Boolean ratios, mismatched frequency/mask, `-pi` phase, negative absolute phase, nonfinite/extra coefficient fields, tuple report containers, 4097-member containers, excessive depth and cycles all raised `ComparisonError`. |

Additional commands completed successfully:

```sh
python3 -m py_compile tools/compare_capture.py
sha256sum tools/compare_capture.py tools/capture_common.py docs/CAPTURE_COMPARISON_CONTRACT.md
git diff --check -- tools/compare_capture.py docs/CAPTURE_COMPARISON.md docs/development/2026-11-13-calibration/15-metrics-implementation.md
```

The first smoke command printed a complete finite JSON report for the four-frame
sine/cosine pair. The following compact repeat checks the main integration edges
without depending on a retained producer snapshot:

```sh
python3 - <<'PY'
import json
import math
from tools.compare_capture import ComparisonError, compare_signals, validate_comparison_report

report = compare_signals([[0,1,0,-1]], [[1,0,-1,0]], 4, frequencies_hz=[1])
row = report["channels"][0]["frequencies"][0]
assert math.isclose(row["metrics"]["phase_error_rad"]["value"], math.pi/2, abs_tol=2e-14)
assert math.isclose(row["metrics"]["complex_abs_error_fs"]["value"], 1/math.sqrt(2), abs_tol=2e-14)
near = math.nextafter(1e-12, math.inf)
large = compare_signals([[near]], [[1e6]], 2, frequencies_hz=[0])
assert large["channels"][0]["metrics"]["normalized_rms_error"]["value"] == (1e6-near)/near
validate_comparison_report(large)
json.dumps(large, allow_nan=False)
silent = compare_signals([[0]], [[0]], 1, frequencies_hz=[0])
assert silent["channels"][0]["frequencies"][0]["phase_mask"] == "both_at_or_below_floor"
try:
    compare_signals([[True]], [[0]], 1)
except ComparisonError:
    pass
else:
    raise AssertionError("Boolean sample was admitted")
print("metric integration smoke passed")
PY
```

## Limits and next dependency

No implementation defect remained in these author checks. Early file/API readiness
and sine/cosine/near-floor results were sent to the integrator before completion.
Independent assignment-18 acceptance remains required; author checks do not
replace it. This record does not claim execution at the maximum admitted spectral
workload, cross-platform numerical equivalence, CTest integration, policy grading,
retained audio/report replay, publication or physical fidelity.

Assignment 20 can call `validate_comparison_report` before selecting metrics and
can reuse the existing strict numeric/geometry helpers if useful. It must add the
frozen policy interface, strict exact-byte identity and uncertainty-aware interval
rules under sections 6-7 without changing these definitions. Subsequent audio-file
wrappers must bind exact source/channel/window identities and preserve
`transform: "none"` unless a separately reviewed correction contract is implemented.
