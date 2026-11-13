# Fixed capture comparison policies

`tools/compare_capture.py` implements the fixed policy and decision portions of
the [capture comparison contract](CAPTURE_COMPARISON_CONTRACT.md), sections 6–7.
It uses Python 3.10+ and the standard library. Its metric producer and bounded
comparison-report validator retain their accepted definitions.

An evaluation reports numerical `pass`, `fail` or `inconclusive` for every listed
criterion and for the complete policy. Every result keeps physical fidelity and
preregistration unestablished. A role declaration, small residual or matching
policy hash does not supply an acquisition, uncertainty method or freeze history.

## Public interfaces

| Interface | Behavior |
| --- | --- |
| `parse_policy(policy_json: bytes) -> dict` | Fully admits the exact input bytes and intrinsic policy semantics without a comparison report or audio work. Returns a fresh parsed object without inserted, dropped or normalized fields. |
| `evaluate_policy(comparison, policy_json: bytes) -> dict` | Reuses `parse_policy`, admits the complete comparison report, checks matching analysis, evaluates every criterion and retains the complete comparison. |
| `ComparisonError(ValueError)` | Rejects malformed bytes, invalid policy/report shapes, unsafe types, exceeded bounds and incompatible metadata without returning a partial evaluation. |

`parse_policy` is an additive preflight interface for callers that must reject a
bad policy before scanning audio. It validates target channels and selected
frequencies, typed metric/unit relationships, all uncertainty declarations and
the combined analysis work budget. It does not grade anything, establish that a
comparison exists, or add a checksum to the returned policy. Keep the original
bytes for evaluation and replay.

Neither function reads files, writes files, loads audio, fits parameters, accesses
a network or changes external state. A command-line file workflow is a separate
wrapper. The [array metric guide](CAPTURE_COMPARISON.md) describes the supplied
comparison's definitions and scope.

## Run the retained synthetic example

From the repository root:

```sh
python3 - <<'PY'
import json
from tools.capture_common import read_bytes
from tools.compare_capture import compare_signals, evaluate_policy, parse_policy

policy_bytes = read_bytes("data/capture-policy-synthetic-example.json", max_bytes=65536)
policy = parse_policy(policy_bytes)
comparison = compare_signals(
    [[0, 1, 0, -1]],
    [[0, 1, 0, -1]],
    4,
    frequencies_hz=[1],
)
evaluation = evaluate_policy(comparison, policy_bytes)
assert evaluation["numerical_verdict"] == "pass"
assert evaluation["preregistration"] == "not_established"
assert evaluation["physical_fidelity"] == "not_established"
print(json.dumps(evaluation, sort_keys=True, indent=2, allow_nan=False))
PY
```

The [example policy](../data/capture-policy-synthetic-example.json) is the frozen
contract's literal repeated-array example, with a final LF. Identical finite
arrays have zero pointwise error, so its explicitly synthetic zero-margin RMS
criterion passes. The absent freeze evidence remains absent. This is a numerical
illustration with no instrument recording or physical tolerance.

Importing from a `tools` directory already on `sys.path` also works, using
`from compare_capture import parse_policy, evaluate_policy`.

## Input contract and bounds

The root requires exactly `schema_version`, `metric_contract`, `policy_id`,
`evidence_class`, `evaluation_role`, `freeze_evidence`, `analysis` and `criteria`.
Every nested object rejects unknown and missing fields. The frozen contract and
[shape schema](../data/capture-policy.schema.json) enumerate the complete form.

| Admission | Exact limit or rule |
| --- | --- |
| Bytes | Exact Python `bytes`, at most 65,536 bytes; strict UTF-8 JSON. |
| Generic structure | At most 4,096 value nodes, container depth 8 with the root at 0, and 4,096 members per generic container. |
| Strings | Nonblank, at most 2,048 characters; no C0/C1 control characters or unpaired surrogates. IDs match `[a-z][a-z0-9_-]{0,63}`. |
| Numbers | Finite exact integers/floats with magnitude at most `1e6`; Boolean substitutes are rejected. Numeric tokens are at most 64 characters. |
| JSON spelling | BOMs, duplicate keys, nonfinite tokens, invalid encoding, excessive depth/size and unsupported types are rejected. |
| Analysis | Exactly rate, channel count, frame count, window, floor and ordered frequencies. The metric contract's geometry, Nyquist, Hann and combined work bounds all apply. |
| Criteria | 1–256 rows, with unique criterion IDs and unique numeric target triples. Supplied order is retained. The generic node/byte limits also apply and can bind before the row limit. |

The policy's six analysis fields must equal the corresponding comparison fields.
Integer-only fields retain exact integer-token admission. For admitted numeric
frequency/floor values, numeric equality is used; no nearest-bin choice, rounding,
epsilon or inferred analysis setting is introduced. Two numerically equal target
frequencies such as `1` and `1.0` cannot create duplicate criteria for one target.

The policy parser uses a `1e6` numeric ceiling. Comparison reports independently
retain the larger `2e18` ceiling needed by near-floor normalized errors. Known
interval endpoints are finite, but `value + margin` can exceed `2e18`; consumers
must not apply the comparison-only ceiling to the entire evaluation envelope.

### Typed upper-bound targets

Each target has exactly `channel_index`, `frequency_hz` and `metric`. Channels
must exist. A frequency target must name an exact selected frequency; a pointwise
target must use null frequency.

| Target | Metric | Unit |
| --- | --- | --- |
| Pointwise | `absolute_dc_bias_fs`, `rms_error_fs`, `max_abs_error_fs` | `FS` |
| Pointwise | `normalized_rms_error` | `ratio` |
| Selected frequency | `complex_abs_error_fs` | `FS` |
| Selected frequency | `normalized_complex_error` | `ratio` |
| Selected frequency | `absolute_phase_error_rad` | `rad` |

Only these typed targets are admitted. Signed bias, diagnostic dB values, phase
signs, expressions, arbitrary field paths and reductions are not policy targets.
The criterion and its uncertainty must use the exact target unit. A positive
limit cannot hide a negative signed error because the admitted error quantities
are nonnegative.

### Explicit uncertainty

Each criterion retains a nonnegative upper bound, its rationale and an uncertainty
object with exactly `margin`, `unit`, `basis`, `evidence` and `unknown_reason`.

| Basis | Admitted declaration |
| --- | --- |
| `unknown` | Margin and evidence are null, with a nonblank reason. |
| `declared_margin` | Margin is strictly positive and at most `1e6`; a nonblank evidence/method locator is required and unknown reason is null. |
| `synthetic_numerical` | Root evidence class must be `synthetic_numerical_fixture`; margin may be zero, with a nonblank numerical-budget/fixture locator and null unknown reason. |

`digital_comparison` cannot use the synthetic basis. The evaluator checks the
declaration's shape and compatibility; it cannot authenticate its evidence.
The supplied margin is already the justified symmetric decision margin for that
metric. It is not automatically a standard uncertainty, confidence interval or
residual standard error. Coverage, common errors and correlation treatment require
separate evidence and review. Repetition does not silently reduce the margin.

## Decisions and retained results

For known nonnegative observed value `v`, margin `u` and upper bound `L`, the
closed interval is `[max(0, v-u), v+u]`.

| Condition | Numerical verdict | Retained reason |
| --- | --- | --- |
| Upper endpoint `<= L` | `pass` | `within_upper_bound` |
| Lower endpoint `> L` | `fail` | `above_upper_bound` |
| Otherwise | `inconclusive` | `interval_overlaps_upper_bound` |
| Metric is undefined | `inconclusive` | `metric_undefined` |
| Metric is known but margin is unknown | `inconclusive` | `uncertainty_unknown` |

An upper endpoint exactly on the bound passes. A lower endpoint exactly on the
bound with an upper endpoint above it is inconclusive. Missing metric evidence
takes precedence over an unknown margin; both original reasons remain in the
observed metric and retained uncertainty. An unknown margin at zero observed
error does not become a pass. No hidden tolerance or rounding is applied.

Every criterion remains in supplied order, even after a failure. Any failed row
makes the overall result fail; otherwise any inconclusive row makes it
inconclusive; otherwise it passes. Untargeted metrics remain in the complete
comparison and are not silently graded by an aggregate score.

The evaluation has exactly the fields specified in contract section 7: version,
metric contract, policy ID/hash, evidence class, evaluation role, preregistration,
overall numerical verdict, all evaluated criteria, complete comparison and
physical-fidelity status. Each criterion retains its target, observed metric,
bound, uncertainty, interval, verdict and reason. Mutable output objects do not
alias caller-owned comparison objects. Each observed criterion metric is also
separate from the returned full comparison.

## Byte identity, roles and evidence limits

`policy_sha256` hashes exactly the admitted original bytes, including whitespace
and the final newline. It is not a hash of the parsed/reformatted object. Equivalent
JSON spellings can have equal numerical results and different policy identities.
Retain the bytes to preserve the rationale, freeze-evidence declaration and
replayable identity.

Roles are `fit`, `validation`, `final_test` and `unassigned`. The evaluator loads
no corpus and cannot independently establish a split. A corpus wrapper must apply
the exact mapping `fit → fit`, `validation → validation`, `final → final_test`,
`unassigned → unassigned`, together with whole-group relationship checks. A
declared final role is not proof that the final evidence was untouched.

Known or unknown `freeze_evidence` never changes `preregistration` from
`not_established`. Every criterion and the overall result likewise retain
`physical_fidelity: "not_established"`. Actual permissions, specimen/revision,
physical scale/clock/chain calibration, boundary compatibility, uncertainty
methods, held-out history, listening and product qualification remain separate.

## Schema boundary and verification

The JSON Schema covers exact required object fields, enums, ranges, text bounds,
typed metric/unit combinations, uncertainty branches and the restriction on
synthetic margins. It does not replace the Python parser. Byte encoding and
numeric-token constraints, node/depth limits, cross-row IDs/targets, dynamic
channel/frequency membership, ordered frequencies and combined work require the
runtime checks. JSON Schema's mathematical integer type also admits a token such
as `1.0`; this Python interface requires an integer token for integer fields.
No JSON Schema package is needed at runtime.

[Assignment 20](development/2026-11-13-calibration/20-policy-implementation.md)
records exact source/example/schema identities, actual author checks and the
unchanged metric regression. The separately authored assignment-21 suite and
root's coherent integration are independent acceptance gates. The implementation
does not claim cross-platform numerical identity, audio-source authentication,
freeze chronology or physical qualification from these policy checks.
