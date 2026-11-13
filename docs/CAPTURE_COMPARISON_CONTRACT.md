# Capture comparison contract v1

This is a **project-proposed, offline digital comparison contract**, frozen before
its producer is graded. It extends [capture metadata v1](CAPTURE_FORMAT.md) without
changing that format. Its identity is `capture-comparison-v1`; it requires Python
3.10+ and the standard library only. It specifies engineering calculations, not a
universal organ-fidelity tolerance or an acquired measurement.

The governing source is atlas PDF pp. 187-192, 203, 233, 347, 363-366, 367-372 and
481-486, especially p. 364 (retain comparisons before and after declared shared
corrections) and p. 484 (freeze bounds and retain uncertainty/inconclusive results).
The [fresh reviews](development/2026-11-13-calibration/09-comparison-contract.md)
record how those requirements constrain this first slice. The atlas does not
supply these field names, numerical resource limits, or software tolerances.

## 1. Public interfaces and scope

The intended module is `tools/compare_capture.py`. These nonmutating interfaces
are frozen; a CLI, audio loading, corpus loading and correction wrapper are separate
deliverables and must call these interfaces rather than redefine the metrics.

```python
class ComparisonError(ValueError):
    pass

def compare_signals(
    reference_channels,
    candidate_channels,
    sample_rate_hz,
    *,
    frequencies_hz=(),
    window="rectangular",
    floor_fs=1e-12,
) -> dict: ...

def evaluate_policy(comparison, policy_json: bytes) -> dict: ...
```

Inputs are not modified, and returned nested containers do not alias mutable input
containers. Invalid arguments, incompatible policy/report metadata, unknown keys,
invalid report shapes or exceeded bounds raise `ComparisonError` before returning
any result. Failure must not return a partial or passing report. Neither API reads
files, accesses a network, fits a parameter or changes external state.

`compare_signals` compares the arrays **exactly as supplied**. It performs no
automatic gain adjustment, DC removal, normalization, channel matching, lag search,
phase fit, resampling, time warping, padding, truncation or clipping. `window` affects
only the optional frequency coefficients; all pointwise metrics always use every
supplied frame with uniform weight, including pre-roll, silence and transients.

`evaluate_policy` validates and grades a supplied comparison report. It cannot
prove that report was calculated from particular audio bytes. A retained acquisition
or replay wrapper must bind and re-read the actual inputs, select the declared
channels/windows, rerun this API, and preserve its own source/tool identities.

## 2. Input geometry and bounded work

| Input | Exact admission rule |
| --- | --- |
| Channel arrays | Both outer containers and every channel are exact Python `list` or `tuple`; generators, mappings, strings and array-library objects are rejected. Channel-major order is required. |
| Channels | Each side has the same count `C`, with `1 <= C <= 16`. Reference channel `i` pairs with candidate channel `i`; there is no mixdown, reordering or averaging. |
| Frames | Every channel on both sides has exactly the same length `N`, with `1 <= N <= 262144`. The local analysis interval is the half-open frame range `[0, N)`. |
| Samples | Exact Python `int` or `float`, excluding Boolean and subclasses; finite and `abs(sample) <= 1e6`. Conversion to binary64 is explicit; no peak normalization occurs. |
| Digital rate | Exact integer, excluding Boolean, in `1..768000` Hz. This is the declared digital rate, not proof of a calibrated physical clock. |
| Frequencies | Exact `list` or `tuple`, with `0..64` exact finite integer/float values, excluding Boolean/subclasses. Values are strictly increasing numerically, unique, and in `[0, sample_rate_hz/2]`. No nearest-bin rounding occurs. |
| Window | Exact string `rectangular` or `hann_symmetric`; the latter requires `N >= 3`. |
| Floor | Exact finite integer/float, excluding Boolean/subclasses, in `[1e-12, 1e6]` FS. |
| Total work | `C*N <= 4194304` and, for `K` selected frequencies, `C*N*K <= 16777216`. Check geometry/work before spectral loops; reject excess work rather than truncate. |

The largest two-sided input has 8,388,608 scalar samples. The caller already owns
these arrays; the implementation must not create an unbounded iterator, a dense
`C*N*K` table, or input-dependent recursive algorithm. Use channel/frame loops and
bounded temporary storage. Spectral work is linear in the declared `C*N*K` budget.

The floor is a **declared digital amplitude mask**, in the same FS scale as the
input. The default is a numerical convention, not an estimated noise floor,
calibration uncertainty, ADC specification or measured SNR. A physical study must
retain the evidence for its selected floor outside this array-only report. No floor
is subtracted from the data, and no excluded phase bin is removed from the report.

The caller must retain original artifact IDs/digests, physical boundaries, channel
IDs/polarities, units, original half-open frame bounds, digital rates, physical-clock
status, initial-state evidence and exclusions. Passing two equally shaped arrays
does not establish compatible G-G/pickup/microphone boundaries or synchronization.
There is no implicit conversion from FS to volts, amperes or pascals.

## 3. Pointwise definitions and undefined values

For one paired channel, let `r[n]` be reference, `c[n]` candidate and
`e[n] = c[n] - r[n]`, for `n = 0..N-1`. All sums use `math.fsum`; means, square
roots and logarithms use finite binary64 arithmetic. RMS includes DC. There is no
sample weighting or subtraction of channel means.

Every metric has exactly this shape, including when it is undefined:

```json
{"value":0.0,"unit":"FS","undefined_reason":null}
```

A known metric has a finite numeric `value` and null reason. An undefined metric
has `value: null` and the explicit reason specified below. No NaN, Infinity, signed
infinity string, magic sentinel or silently substituted zero is allowed. Units
are exactly `FS`, `ratio`, `dB` or `rad`. Computed ratios may exceed the input scalar
bound; they remain finite and bounded by the admitted samples and positive floor.
All reported numeric values have magnitude at most `2e18`.

| Metric key | Definition | Unit / undefined rule |
| --- | --- | --- |
| `reference_dc_fs` | `sum(r)/N` | FS; always known. |
| `candidate_dc_fs` | `sum(c)/N` | FS; always known. |
| `dc_bias_fs` | `sum(e)/N` | FS; signed candidate-minus-reference bias. |
| `absolute_dc_bias_fs` | `abs(dc_bias_fs)` | FS; nonnegative upper-bound quantity. |
| `reference_rms_fs` | `sqrt(sum(r*r)/N)` | FS; always known. |
| `candidate_rms_fs` | `sqrt(sum(c*c)/N)` | FS; always known. |
| `rms_error_fs` | `sqrt(sum(e*e)/N)` | FS; always known. |
| `max_abs_error_fs` | `max(abs(e))` | FS; always known. |
| `normalized_rms_error` | `rms_error_fs/reference_rms_fs` | ratio; undefined with `reference_at_or_below_floor` when reference RMS is `<= floor_fs`. |
| `signal_to_error_db` | `20*log10(reference_rms_fs/rms_error_fs)` | dB; reference RMS `<= floor_fs` gives `reference_at_or_below_floor`; otherwise zero error gives `zero_error`; otherwise error RMS `<= floor_fs` gives `error_at_or_below_floor`. Evaluate those conditions in that order. |

Zero error against a nonzero reference therefore has normalized error zero and an
explicitly undefined signal-to-error dB value; an infinite dB score is not emitted.
Both-silent input has zero absolute errors, but its normalized error and dB ratio
remain undefined. A silent reference with a nonzero candidate still reports the
candidate level and absolute errors. The floor does not suppress those errors.

The signed DC bias and signal-to-error dB are diagnostic values. Neither can be
used as an upper-bound policy criterion in this version. A negative bias must not
pass a positive absolute-error limit merely because it has the opposite sign.

## 4. Selected-frequency complex coefficients

For each supplied frequency `f`, calculate the weighted complex mean

```text
D_x(f) = sum(w[n] * x[n] * exp(-j * 2*pi*f*n/sample_rate_hz)) / sum(w[n])
```

Use separately accumulated real and imaginary sums, `math.cos`/`math.sin`, and
`math.fsum`. The frame phase origin is local input frame zero for every channel.
This is a finite-record coefficient at the exact supplied hertz value, not an
estimated LTI transfer function, cross-spectrum, coherence or fitted sinusoid.
Off-bin leakage is retained. No automatic DC removal, padding, interpolation,
one-sided doubling, power normalization or compensation for physical delay occurs.

Window weights are exactly:

- `rectangular`: `w[n] = 1`.
- `hann_symmetric`: `w[n] = 0.5*(1-cos(2*pi*n/(N-1)))`; both endpoint weights are
  explicitly zero. `N >= 3` ensures a positive weight sum.

The normalization is the sum of the actual weights. A coherent rectangular-window
interior-bin sinusoid of amplitude `A` has coefficient magnitude `A/2`; DC and
Nyquist are not doubled. All channels use the same window and normalization.

For `R = D_r(f)` and `C = D_c(f)`, each frequency row retains both signed complex
coefficients. Its metric object has exactly these keys:

| Metric key | Definition | Unit / undefined rule |
| --- | --- | --- |
| `reference_magnitude_fs` | `abs(R)` | FS; always known. |
| `candidate_magnitude_fs` | `abs(C)` | FS; always known. |
| `complex_abs_error_fs` | `abs(C-R)` | FS; always known. |
| `normalized_complex_error` | `abs(C-R)/abs(R)` | ratio; `reference_at_or_below_floor` when `abs(R) <= floor_fs`. |
| `reference_phase_rad` | `arg(R)` | rad; `reference_at_or_below_floor` when `abs(R) <= floor_fs`. |
| `candidate_phase_rad` | `arg(C)` | rad; `candidate_at_or_below_floor` when `abs(C) <= floor_fs`. |
| `phase_error_rad` | `arg(C*conj(R))` | rad; known only when both magnitudes exceed the floor. |
| `absolute_phase_error_rad` | `abs(phase_error_rad)` | rad; the same undefined condition/reason as signed phase error. |

All phases are wrapped to `(-pi, pi]`, mapping an exact `-pi` result to `+pi`.
Positive phase error means the candidate coefficient leads the reference. Do not
unwrap across frequencies or estimate group delay. The phase-error reason is
`both_at_or_below_floor`, `reference_at_or_below_floor`, or
`candidate_at_or_below_floor`, in that precedence order. Each row's `phase_mask`
is exactly that reason when phase error is undefined, or `none` when it is known.
Masked rows, their frequency, coefficients, absolute error and undefined reasons
remain present; masks cannot improve coverage by deleting a difficult bin.

## 5. Exact comparison report

Every object rejects additional fields when consumed by `evaluate_policy`. All
listed fields are required. The report has exactly:

```text
schema_version: 1
metric_contract: "capture-comparison-v1"
sample_rate_hz: admitted integer rate
channel_count: C
frame_count: N
analysis:
  pairing: "index"
  frame_start: 0
  frame_stop: N
  window: admitted window
  floor_fs: admitted numeric floor
  frequencies_hz: supplied frequencies in increasing order
  dft_normalization: "weighted_mean"
  transform: "none"
channels: C rows, in index order
physical_fidelity: "not_established"
```

Each channel row has exactly `reference_channel_index`, `candidate_channel_index`,
`metrics`, and `frequencies`. Both indices equal its array position. `metrics`
contains exactly the ten pointwise entries in section 3. `frequencies` contains
exactly `K` rows in supplied frequency order, including masked rows; it is empty
when `K` is zero.

Each frequency row has exactly `frequency_hz`, `reference_coefficient`,
`candidate_coefficient`, `metrics`, and `phase_mask`. A coefficient has exactly
`real_fs` and `imag_fs`, both finite numbers. Its metric object has exactly the
eight entries in section 4. Every scalar metric follows the known/undefined shape
in section 3. Always-known quantities cannot be null; nonnegative quantities cannot
be negative; phase values must be in their stated range. Reasons, masks, units,
frequency arrays, frame/channel counts and constant metadata must agree.

The report deliberately contains no timestamp, filesystem-dependent value, random
value, inferred physical metadata, policy verdict or mutable process-global state.
The same inputs and Python/platform math environment produce the same ordered
content. Cross-platform trigonometric/logarithmic last bits are not promised to be
identical; independently justified numerical budgets and recorded tool identities
are required. Use `allow_nan=False` when serializing any report.

## 6. Strict policy input and byte identity

`evaluate_policy` accepts exact `bytes`, at most 65,536 bytes, containing strict
UTF-8 JSON with an object root. Reject a BOM, duplicate keys at every level,
nonfinite tokens, overflow, invalid UTF-8, unpaired surrogates, numeric tokens longer
than 64 characters, unsupported types, more than 4,096 value nodes, container depth
greater than 8 (root at 0), or any object/list with more than 4,096 members before
the tighter limits below. Booleans cannot stand in for numbers or integers.

Every listed policy key is required, and additional fields are rejected at every
level. IDs match `[a-z][a-z0-9_-]{0,63}`. Text is nonblank, at most 2,048 characters,
and contains no control characters or unpaired surrogates. Exact finite policy
numbers have magnitude at most `1e6`; all bounds/margins are nonnegative.

| Root field | Contract |
| --- | --- |
| `schema_version` | Exact integer `1`. |
| `metric_contract` | Literal `capture-comparison-v1`. |
| `policy_id` | ID; descriptive identity, not a content checksum. |
| `evidence_class` | `synthetic_numerical_fixture` or `digital_comparison`. Neither establishes hardware evidence. |
| `evaluation_role` | `fit`, `validation`, `final_test`, or `unassigned`; a declared use, subject to an independent corpus audit. |
| `freeze_evidence` | Exactly `value` and `unknown_reason`; known value is nonblank text locating the retained freeze evidence with null reason; missing value is null with a nonblank reason. |
| `analysis` | Exactly `sample_rate_hz`, `channel_count`, `frame_count`, `window`, `floor_fs`, `frequencies_hz`; each follows sections 2/4 and must equal the comparison report's corresponding values. |
| `criteria` | `1..256` criterion objects, with unique IDs and unique target triples; retain supplied order. |

Each criterion has exactly `criterion_id`, `target`, `upper_bound`, `unit`,
`rationale`, and `uncertainty`. Its ID and rationale follow the preceding rules.
`upper_bound` is finite in `[0, 1e6]` in the exact metric unit. It is a declared
limit with a documented rationale, not a tolerance supplied by the atlas.

`target` has exactly `channel_index`, `frequency_hz`, and `metric`. The channel is
an exact integer in `0..C-1`. The frequency is null for a pointwise target, or an
exact numeric match to one selected frequency for a frequency target. `metric`
must come from this finite, typed whitelist:

| Target kind | Admitted metric names | Exact unit |
| --- | --- | --- |
| Pointwise | `absolute_dc_bias_fs`, `rms_error_fs`, `max_abs_error_fs` | FS |
| Pointwise | `normalized_rms_error` | ratio |
| Frequency | `complex_abs_error_fs` | FS |
| Frequency | `normalized_complex_error` | ratio |
| Frequency | `absolute_phase_error_rad` | rad |

Targets are typed names, not Python expressions, dotted paths, JSONPath, arbitrary
JSON pointers, regexes, callbacks or import names. Missing channels/frequencies,
diagnostic-only metrics, wrong units or unmatched analysis are rejected inputs,
not automatically skipped criteria. No wildcard, per-channel reduction, weighting
or aggregate average can conceal a failing listed condition. Untargeted metrics
remain in the comparison report; a pass claims only the listed criteria.

The `uncertainty` object has exactly `margin`, `unit`, `basis`, `evidence`, and
`unknown_reason`. Its unit must equal the criterion unit. Its margin is the already
justified symmetric decision margin for this particular metric; it is **not**
automatically a standard uncertainty, confidence level or residual standard error.
No coverage-factor choice or correlation assumption is inferred by the evaluator.

| Basis | Required values |
| --- | --- |
| `unknown` | Null margin and evidence; nonblank unknown reason. This is required when the applicable physical/numerical uncertainty is unavailable. |
| `declared_margin` | Finite margin in `(0, 1e6]`, nonblank method/evidence locator, null unknown reason. Evidence must define coverage and relevant common-error/correlation treatment. |
| `synthetic_numerical` | Only with root `synthetic_numerical_fixture`; finite margin in `[0, 1e6]`, nonblank independent-fixture/numerical-budget evidence, null unknown reason. Zero is allowed only by this explicit synthetic declaration. |

An unknown physical uncertainty cannot become zero by using a synthetic margin
label. The evaluator validates the declaration but cannot authenticate its truth.
Neither many samples nor multiple bins make shared calibration errors independent.

`policy_sha256` is lowercase SHA-256 of the **exact admitted `policy_json` bytes**,
including whitespace and final newline. Do not reserialize, sort, strip, normalize
numeric tokens or accept a caller-supplied hash as a replacement for hashing those
bytes. The policy contains no self-hash field. Retain those bytes for replay.
Two equivalent JSON spellings can intentionally have different policy identities.
A hash identifies bytes; it does not prove when they were created or that the final
data was untouched. `freeze_evidence` is a declaration/evidence locator, not an
automatic chronological attestation. Every evaluation retains
`preregistration: "not_established"`; separate review must establish chronology.

## 7. Decision rule and exact evaluation report

For each admitted nonnegative metric value `v`, known decision margin `u`, and
upper bound `L`, use the closed interval

```text
lower = max(0, v-u)
upper = v+u
pass         if upper <= L
fail         if lower > L
inconclusive otherwise
```

The entire interval must lie within `[0,L]` for pass. An interval touching `L` at
its lower endpoint but extending above it is inconclusive, not fail. Undefined
metrics and unknown uncertainty are inconclusive even when another displayed
number looks favorable. Apply no rounding, hidden epsilon, clipping to the limit,
or retrospective threshold adjustment. Numerical allowance belongs in the stated
margin. Enlarging a margin must never convert an inconclusive/failing criterion
to a pass.

Each evaluated criterion has exactly `criterion_id`, `target`, `observed`,
`upper_bound`, `uncertainty`, `interval`, `numerical_verdict`, `reason`, and
`physical_fidelity`. Target and uncertainty are retained unchanged; `observed` is
the selected metric object including its unit/reason. The interval object has
exactly `lower`, `upper`, `unit`, and `undefined_reason`. Known endpoints are finite
and reason null. Missing endpoints are both null, with `metric_undefined` or
`uncertainty_unknown` as reason; a missing metric takes precedence when both are
missing. Retain the original uncertainty and metric reasons alongside that summary.

Criterion reasons are exactly `within_upper_bound`, `above_upper_bound`,
`interval_overlaps_upper_bound`, `metric_undefined`, or `uncertainty_unknown`.
Every criterion has `physical_fidelity: "not_established"` independently of its
numerical verdict.

The top-level evaluation report has exactly:

```text
schema_version: 1
metric_contract: "capture-comparison-v1"
policy_id: supplied policy ID
policy_sha256: hash of exact admitted policy bytes
evidence_class: supplied declaration
evaluation_role: supplied declaration
preregistration: "not_established"
numerical_verdict: "pass" | "fail" | "inconclusive"
criteria: all evaluated criterion rows, in policy order
comparison: complete supplied comparison report, retained without mutable aliasing
physical_fidelity: "not_established"
```

The overall numerical result is fail if any criterion fails; otherwise
inconclusive if any criterion is inconclusive; otherwise pass. Evaluate and retain
all criteria even after a failure. A fail cannot be hidden by an undefined neighbor.
`blocked` and `not_run` belong to the later execution/replay wrapper: malformed or
unavailable input does not produce an artificial passing calculation here.

Before traversing a caller-supplied comparison report, enforce at most 65,536 value
nodes, depth at most 12, and at most 4,096 members per generic container, then the
tighter section-5 limits. No report may contain an unrecognized key, unsafe type,
nonfinite value, out-of-range number or inconsistent constant/geometry/unit/mask.
These checks establish report structure, not its correspondence to original audio.
If using `capture_common.validate_json_value` for this guard, explicitly pass
`max_number=2e18`; its metadata-oriented default of `1e12` is too small for valid
near-floor normalized-error ratios. Policy inputs retain their own tighter bounds.

## 8. Complete minimal policy example

This example grades literal repeated four-frame arrays at one declared frequency.
It is a synthetic policy illustration, not executed evidence or a physical budget.
The absent freeze evidence remains visible even if its numerical criterion passes.

```json
{
  "schema_version": 1,
  "metric_contract": "capture-comparison-v1",
  "policy_id": "literal-repeat-v1",
  "evidence_class": "synthetic_numerical_fixture",
  "evaluation_role": "validation",
  "freeze_evidence": {
    "value": null,
    "unknown_reason": "Illustrative policy; no independently retained chronology."
  },
  "analysis": {
    "sample_rate_hz": 4,
    "channel_count": 1,
    "frame_count": 4,
    "window": "rectangular",
    "floor_fs": 1e-12,
    "frequencies_hz": [1]
  },
  "criteria": [
    {
      "criterion_id": "repeat-rms",
      "target": {"channel_index": 0, "frequency_hz": null, "metric": "rms_error_fs"},
      "upper_bound": 0,
      "unit": "FS",
      "rationale": "Identical literal finite arrays have exactly zero pointwise difference.",
      "uncertainty": {
        "margin": 0,
        "unit": "FS",
        "basis": "synthetic_numerical",
        "evidence": "Independent algebra for repeated binary-representable literals; synthetic zero margin only.",
        "unknown_reason": null
      }
    }
  ]
}
```

## 9. Independent acceptance vectors and rejection gates

The producer cannot be its own oracle. Independently written acceptance must use
literal arrays and the following algebra, plus independently computed spectral
expectations. Values in this table are exact mathematical targets; declared small
binary64 tolerances apply only to square roots, logarithms and trigonometry.

| Reference `r`; candidate `c` | Required results |
| --- | --- |
| `[0,0,0,0]`; same | Both RMS values, DC and absolute errors zero; normalized error and dB undefined with `reference_at_or_below_floor`. |
| `[0,0,0,0]`; `[1,1,1,1]` | DC bias 1, candidate RMS 1, RMS/max error 1; relative metrics undefined, not a silent pass. |
| `[1,-1,1,-1]`; same | Reference/candidate RMS 1, error and normalized error 0; dB undefined with `zero_error`. |
| `[1,-1,1,-1]`; `[0,0,0,0]` | Reference RMS 1, candidate RMS 0, RMS/max/normalized error 1, dB 0. |
| `[1,-1,1,-1]`; `[2,-2,2,-2]` | DC bias 0; reference and candidate RMS 1 and 2 respectively; RMS/max/normalized error 1; dB 0. This must not be normalized away. |
| `[1,-1,1,-1]`; `[1.25,-0.75,1.25,-0.75]` | Bias/absolute bias/RMS/max/normalized error 0.25; candidate RMS `sqrt(17)/4`; dB `20*log10(4)`. |
| `[1,-1,1,-1]`; `[-1,1,-1,1]` | Bias 0; RMS/max/normalized error 2; dB `20*log10(0.5)`. Polarity reversal remains an error. |
| `[1,0,0,0]`; `[0,1,0,0]` | One-frame delay: RMS values 0.5, RMS error `1/sqrt(2)`, max 1, normalized error `sqrt(2)`, dB `-10*log10(2)`; no lag search. |
| `[0,1,0,-1]`; `[1,0,-1,0]`, rate 4, frequency 1, rectangular | Sine/cosine phase test: coefficients `-0.5j` and `0.5`; complex error `1/sqrt(2)`, normalized complex error `sqrt(2)`, phase error `+pi/2`; pointwise RMS error 1. |

Also require independent checks for two-channel order preservation, nonzero/negative
DC, selected DC/Nyquist bins without doubling, off-bin leakage, Hann endpoint/weight
normalization, window-independent pointwise metrics, phase wrap at polarity,
one-sided and both-sided floor masks, retained masked-bin coverage and floor equality.
At a selected DC bin a constant input must retain its signed level as the real
coefficient under either admitted window. Empty frequency lists must do no spectral
work and still return every pointwise metric.

Independent policy vectors must include exact binary-representable boundaries:
`v=0.25,u=0.125,L=0.375` passes; `v=0.5,u=0.125,L=0.25` fails;
`v=0.25,u=0.125,L=0.25` is inconclusive; `v=0.375,u=0.125,L=0.25` touches
the limit at its lower endpoint and is inconclusive. Missing uncertainty remains
inconclusive at `v=0`; explicit synthetic `u=0,v=0,L=0` passes numerically.
Test all-criteria retention, fail precedence, diagnostic-target rejection, policy
byte-hash changes after whitespace edits, and unknown chronology preservation.

Boundary/rejection tests cover unequal channels/frames, zero/over-limit dimensions,
bad scalar types/Booleans, NaN/Infinity, excessive amplitude, invalid rate/floor,
duplicate/unsorted/out-of-band frequencies, Hann lengths 1/2, exact/exceeded work
budgets, malformed/deep/oversized/duplicate-key JSON, unknown fields, invalid units,
unsafe metric strings, missing target bins, and mismatched policy analysis. Rejected
calls must preserve input arrays and existing external report files owned by a caller.

## 10. Corpus roles, corrections and later evidence

`fit` may inform parameter estimation. `validation` may inform model selection and
policy design. `final_test` is reserved for assessment of a locked choice against
predeclared criteria; `unassigned` has no independent holdout status. Existing
capture v1 `held_out` is not automatically `final_test`. A corpus companion must
resolve complete takes, sessions, synchronized channels, duplicates, common parents,
derived crops and declared related groups before assigning these purposes. A role
string, a different path or a matching manifest schema does not establish independence.

At the corpus/comparison boundary the exact mapping is `fit -> fit`,
`validation -> validation`, `final -> final_test`, and `unassigned -> unassigned`.
The corpus token `final` and policy token `final_test` are intentionally distinct;
the wrapper validates this mapping explicitly instead of silently rewriting a role.

Freeze policy bytes, candidate/model/profile identities, corpus split, declared
windows, channel mapping, floors and correction rules before inspecting final
outcomes. Preserve the earlier policy and failed/inconclusive results after a
revision. If final results influence tuning or selection, that final set has been
used for development; a new final evaluation needs independently reserved evidence.
Hash equality is a content check, not proof of chronological preregistration.

A later correction wrapper may permit **one fixed shared gain and one fixed
integer frame delay** for a declared channel group, with independent evidence,
units, sign convention, exact parameters and provenance fixed before grading. It
must retain raw comparison and corrected comparison together. They must use the
same declared frames, or explicitly report each original half-open interval,
overlap and excluded coverage when delay changes the usable interval. No silent
crop, padding, per-channel/per-note/per-window correction or fitted parameter is
admitted by this foundation. Fractional delays, clock-rate corrections, measured
microphone inverses and constrained physical-state estimation require separately
reviewed contracts; the atlas's discussion does not authorize hidden execution.

Numerical metrics and decisions always retain `physical_fidelity:
"not_established"`. Actual specimen/revision identity, acquisition permissions,
calibration and uncertainty, clock/synchronization, boundary/loading compatibility,
chain response, independent physical holdout, perceptual evidence and product
qualification remain separate gates. This contract creates no physical capture,
fitted model, recovered atlas companion, listening result or hardware-fidelity pass.
