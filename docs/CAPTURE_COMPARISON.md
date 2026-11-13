# Array capture comparison metrics

`tools/compare_capture.py` implements the metric-producing portion of the frozen
[capture comparison contract v1](CAPTURE_COMPARISON_CONTRACT.md), sections 1-5,
and its bounded report-admission gate. The same module now implements the
[fixed policy parser/evaluator](CAPTURE_POLICY.md). It requires Python 3.10+ and the standard
library. The [contract integration review](CALIBRATION_CONTRACT_REVIEW.md) records
the source boundary and the report numeric-limit correction.

This is an offline digital calculation. Every result retains
`physical_fidelity: "not_established"`. Matching arrays, a valid report and a
small error cannot establish instrument identity, calibrated units, physical
clock accuracy, measurement uncertainty or independent acquisition.

## Current API and implementation boundary

| API | Implemented behavior |
| --- | --- |
| `ComparisonError(ValueError)` | Rejects invalid array arguments, exceeded limits and invalid supplied reports. |
| `compare_signals(reference_channels, candidate_channels, sample_rate_hz, *, frequencies_hz=(), window="rectangular", floor_fs=1e-12) -> dict` | Produces all ten pointwise metrics and eight metrics at every selected frequency, with exact section-5 metadata and explicit undefined reasons. |
| `validate_comparison_report(comparison) -> None` | Nonmutating, reusable report admission used by the policy evaluator. Rejects unknown/missing fields, unsafe types, excessive work/JSON structure, invalid units and inconsistent geometry or floor masks. |
| `parse_policy(policy_json: bytes) -> dict` | Strict policy preflight without audio or a verdict; returns the admitted parsed value. |
| `evaluate_policy(comparison, policy_json: bytes) -> dict` | Grades every declared criterion using its uncertainty interval and exact original policy-byte identity; retains the complete comparison. |

Audio decoding, audio-file or corpus loading, a command-line wrapper, retained
report publication, replay and correction wrappers remain outside this array
module's scope. The reviewed file-job contract composes those separate APIs. Callers
must use these array definitions and retain their own source/input identities.

## Example from the repository root

```sh
python3 - <<'PY'
import json
from tools.compare_capture import compare_signals

comparison = compare_signals(
    [[0, 1, 0, -1]],
    [[1, 0, -1, 0]],
    4,
    frequencies_hz=[1],
)
print(json.dumps(comparison, indent=2, allow_nan=False))
PY
```

These literal sine/cosine samples have pointwise RMS error `1 FS`. Their
rectangular-window frequency coefficients are approximately `-0.5j` and `0.5`,
with complex absolute error `1/sqrt(2) FS`, normalized complex error `sqrt(2)`,
and candidate-leading phase error `+pi/2 rad`. The tiny real/imaginary remnants
from `sin`/`cos` are retained. The example is synthetic numerical evidence.

Importing from the tools directory also works when that directory is already on
`sys.path`, for example `PYTHONPATH=tools python3` followed by
`from compare_capture import compare_signals`.

## Array admission and work

Both outer arrays and every channel must be exact Python lists or tuples.
Channel pairing is by index. Each side has the same `1..16` channels and all
channels have the same `1..262144` frames. Exact integer/float samples must be
finite and within `[-1e6, 1e6] FS`; Booleans and subclasses are rejected.
Admitted samples are explicitly converted to binary64 one channel pair at a
time. Inputs remain unchanged, and returned nested containers never alias them.

The digital rate is an exact integer in `1..768000 Hz`. Selected frequencies
form an exact list or tuple of at most 64 finite numeric values, strictly
increasing and within `[0, sample_rate_hz/2]`. The floor is finite in
`[1e-12, 1e6] FS`. It is a declared digital mask, not an inferred noise floor or
measurement uncertainty. The floor is never subtracted from any sample or error.

Geometry and total-work checks precede sample processing and spectral loops.
At most `4,194,304` scalar samples per side and `16,777,216` channel-frame-frequency
products are admitted. Excess is rejected without cropping. Temporary storage is
linear in the frame count: one channel pair, its pointwise errors, one weight
vector and one frequency's trigonometric vectors. No dense
channel-frame-frequency table is allocated. Empty frequency selections perform
no window/trigonometric work and still return every pointwise metric.

## Pointwise and selected-frequency behavior

All frame accumulations use `math.fsum`. Pointwise means, RMS and errors cover
every supplied frame uniformly, including DC, silence, pre-roll and transients.
The module performs no gain adjustment, DC removal, channel matching, lag search,
phase fitting, resampling, padding, truncation or clipping.

Pointwise output retains both signed DC levels, signed and absolute DC bias, both
RMS levels, RMS/max absolute error, normalized RMS error and signal-to-error dB.
A reference at or below the floor makes relative metrics undefined. For dB,
reference masking takes precedence over zero error, which takes precedence over
error at or below the floor. Every undefined value is `null` with its prescribed
reason; no infinite dB result or substituted zero is emitted.

Selected coefficients use the exact supplied frequency, negative-exponent phase
and the local frame-zero origin. `rectangular` uses unit weights.
`hann_symmetric` requires at least three frames, explicitly sets both endpoints
to zero and divides by the sum of the actual weights. The window affects only
the frequency coefficients. No one-sided doubling or power normalization occurs.
DC, Nyquist and off-bin leakage remain visible.

Each frequency retains signed real/imaginary coefficients, both magnitudes,
complex absolute/normalized error, both phases, and signed/absolute phase error.
Phases occupy `(-pi, pi]`; exact `-pi` maps to `+pi`. Positive phase error means
the candidate coefficient leads. Reference, candidate and both-sided floor masks
retain the row, coefficients and absolute error. Masked coverage is never deleted.

## Report admission

`validate_comparison_report` first applies the common JSON guard with explicit
`max_nodes=65536`, `max_depth=12` and `max_number=2e18`, then checks the 4,096-member
generic-container limit and tighter comparison schema. The `2e18` numeric bound
is necessary: an admitted reference immediately above `1e-12 FS` and candidate
at `1e6 FS` can produce a normalized error close to `1e18`.

Every object has exact required keys. Report containers are JSON dictionaries
and lists; scalar numbers exclude Booleans/subclasses and must remain finite.
Metadata, indices, half-open frame geometry, window, floor, frequency order and
work limits are checked together. Always-known metrics cannot be null;
nonnegative metrics cannot be negative; phases must have the stated range.
Units, null reasons and phase masks must agree with each metric's floor status.

This validates the supplied report's structure and declared internal mask
semantics. It cannot regenerate pointwise measurements without samples or bind
the report to audio bytes. A later retained-evidence wrapper must re-read declared
inputs and rerun the producer to establish that correspondence. JSON serialization
must use `allow_nan=False`; this array API does not define a CLI byte encoding or
a report digest.

## Executed checks and remaining acceptance

The [assignment-15 record](development/2026-11-13-calibration/15-metrics-implementation.md)
identifies the exact implementation and records 433 passing author assertions on
Python 3.12.14. These used literal pointwise algebra, independent elementary
complex exponentials, null/floor/phase cases, work preflight, strict rejection and
nonmutation checks. Compilation and the documented example also passed.

Independent [assignment 18](development/2026-11-13-calibration/18-metric-acceptance.md)
passed 42 methods, and independent
[assignment 21](development/2026-11-13-calibration/21-policy-acceptance.md) passed
49 policy methods after the separate implementation. Root repeated both suites.
The later policy addition preserves all 20 original function/class definitions.
Maximum admitted spectral-work runtime,
cross-platform last-bit differences, retained replay and physical fidelity have
not been qualified by this author record.
