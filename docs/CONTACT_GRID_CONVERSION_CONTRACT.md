# Contact-grid conversion contract v1

**A07 proposal for independent admission before implementation.** Identity:
`fractional-to-contact-grid-rne-v1`; evidence class `synthetic`. This is an
offline, finite-epoch **trajectory certificate; audio accuracy is unqualified**.
It preserves the existing fractional/grid models, fixture bytes, nominal Engine,
91 source identities, 47 parameters and state formats. Read the
[proposal](research/CONTACT_GRID_CONVERSION_NEXT.md) and its
[independent review](reviews/CONTACT_GRID_CONVERSION_NEXT_REVIEW.md).

## 1. Input authority and exact conversion

Use the unchanged `contact_switching_io.parse_input`/`load_input` admission.
The authority is its canonical immutable `InputDocument.case`, not the apparent
decimal intent of the original JSON. Retain the original input SHA-256/byte count.
Signed zero becomes positive zero under that existing admission; permitted
subnormal source/gain/phase values survive exactly. Do not render audio.

Let `b(x)=Fraction.from_float(x)`, `T=65536`, `Q=2^48`, and F be the admitted
integer sample rate. Define RNE on a nonnegative rational `n/d`: write
`n=q*d+r`; return q when `2*r<d`, q+1 when `2*r>d`, and the even member of
`{q,q+1}` at equality. No intermediate float, clamp or adjustment is allowed.

| Input | Converted value |
| --- | --- |
| Exact command time `u=frame+b(fraction)` in frames | `tick=RNE(T*u)` |
| Target, on or off in normalized travel | `position=RNE(Q*b(value))` |
| Press/release duration P seconds, separately | `speed=RNE(Q/(T*F*b(P)))` units/tick |
| Source/key/contact/caller identities | Retain original indices and input order |

The original/grid velocities in travel/frame are `v=1/(F*b(P))` and
`v'=T*speed/Q`; effective duration is `P'=Q/(T*F*speed)`. Every rounded speed
must be in `[1,2^32-1]`; thresholds must satisfy `0<=off<on<=Q`. Rates are
44100/48000/96000, keys 1–4, contacts nine/key, frames 0–4096 and commands
0–512 including no-ops, ties and closure commands. Initial position/target is
zero and every contact is open. Sample rate is fixed for the entire epoch.

### Collision policy

Stable-sort commands once by exact u then original caller ordinal. Never
deduplicate, nudge, rescale or independently round a callback partition.
Different exact command times must map to different ticks globally, including
commands on different keys. An interior time must remain strictly inside
`(0,N*T)`; exact 0/N stay exact endpoints. Original ties retain caller order.

For each key, form a set containing implicit 0 and 1, all 18 thresholds and
every supplied target. Distinct exact values in this set must map to distinct
integers. Existing equality is permitted and retained. This includes positive
subnormal targets colliding with initial zero and values colliding with full
travel. Compare off/on validity before reporting other position collisions.

## 2. Exact replay and topology predicate

Reconstruct both continuous, piecewise-affine trajectories in **host frames and
normalized travel**, using exact Fractions. Grid speed is rational `T*s/Q`,
never a rounded effective duration passed back through the fractional parser.
Production may use a new generic exact replay, but its grid computation must not
import a test oracle. Existing fractional/grid kernels remain unchanged.

At each distinct command time, advance incoming motion and resolve inclusive
threshold crossings/arrival before applying tied commands in caller order.
Every supplied command is retained for observations and quota accounting. An
unchanged target preserves the current motion anchor; tied changes have no
intervening travel. Moving segments stop at their target; holding never emits a
new edge. Endpoint commands change target/anchor only. N=0 has no motion/edges.

Retain and compare the following identities and facts, including muted contacts
and contacts sharing one source:

| Record | Identity and required relation |
| --- | --- |
| Contact edge | `E:key:contact:direction:occurrence`, with direction 0/1 and zero-based occurrence within that key/contact/direction; identical identities/counts |
| Target arrival | `A:key:direction:occurrence`, direction -1/+1, ordinal within key/direction; only a positive-duration move reaching its target at or before N counts; identical identities/counts |
| Command | `C:caller_ordinal`, including no-ops, every member of ties and endpoint commands |
| Boundaries | `B:0` and `B:1` at 0 and N; both labels exist when N=0 |

At each command, compare sign(target_before-position), sign(target_after-position)
and whether the new target equals the prior target, in the two models. Zero
direction is distinct from either movement. Reached-target events, including an
arrival exactly at a command or N, must not appear/disappear or change direction.
Only positive-duration travel creates an arrival; a tied transient target equal
to position does not create one. Compare all final contact bits; each final grid
target must be the defined rounding of its corresponding original final target.
Position values have the separate budget below.

For each replay, sort all labeled records by exact time, partition into equality
groups, and sort the ASCII labels within each group. The resulting sequence of
label groups must be identical. This is the **complete total preorder**, not just
a sorted edge list: every pair's `<`, `=` or `>` relation is determined by its
group indices. Thus equality groups plus their order replace quadratic pairwise
comparisons without dropping edge/command, edge/arrival or boundary relations.
Within an equal-time group, execution still uses incoming edges/arrival before
commands and native key/contact ordering; lexical label order is evidence only.

## 3. Frozen numerical budgets and exact witnesses

These are chosen engineering limits for this version's accepted subset, not
physical measurements, old-reference tolerances or an allocation of audio error:

| Quantity | Required maximum |
| --- | --- |
| Scalar time rounding | `1/(2*T)` frames |
| Scalar target/threshold rounding | `1/(2*Q)` travel |
| Scalar speed error | `T/(2*Q)` travel/frame |
| Continuous position error on `[0,N]`, per key | `2^-18` travel |
| Each matched edge or reached-target time error | `2^-10` frames |
| Each matched root's analytic upper bound below | `2^-10` frames |

The root limit is 64 ticks (about 10.17–22.14 ns over the supported rates),
128 times the worst scalar half-tick. The position limit is about 3.815 ppm of
full travel: it admits some ordinary conversions while rejecting accumulated
motion drift. These finite conservative research choices are frozen before
candidate outcomes; they promise neither universal admission nor perceptual
equivalence. Report seconds by exact division by F, never a fitted delay/gain.

For each key evaluate both positions at the sorted union of **both** paths'
segment endpoints, commands, arrivals and 0/N. Between these knots the position
difference is affine, so its absolute maximum occurs at an endpoint. Retain every
union-knot pair and the earliest maximum witness (key index then time breaks
ties). This certifies the continuous supremum, including held/final positions,
reversals and differently rounded command boundaries.

For each matched root use its actual emitting moving segment in each model.
Let a,p,theta,v and a',p',theta',v' be segment start time/position, crossed
threshold or reached target, and **positive speed magnitudes**. With
`Ea=abs(a'-a)`, `Ep=abs(p'-p)`, `Etheta=abs(theta'-theta)`,
`Ev=abs(v'-v)` and `d=abs(theta-p)`, retain and check:

```text
abs(t'-t) <= Ea + (Etheta+Ep)/v' + d*Ev/(v*v') <= 2^-10 frames.
```

The segment positions are propagated exact anchors, not the scalar half-unit
bound. Root eligibility, matched directions and topology must already pass.
No-root maxima are zero with a null witness. No-contact/no-source-gain silence
exempts no other check. Retain signed field differences and effective-duration
relative error `abs(P'-P)/P=abs(s*-s)/s` as exact rational diagnostics.

## 4. Fixed refusal precedence and bounded work

Refuse at the first failing stage, with a code, path and exact witness:

1. `input`: original schema/domain/admission or invalid document metadata.
2. `grid_domain`: key order; press then release; contact index off/on validity.
3. `time_collision`: chronological commands, then interior/end collision.
4. `position_collision`: key index, increasing source value; implicit endpoints,
   off/on and caller-ordered targets identify colliding values in that order.
5. `dynamic_topology`: chronological command ordinal, before direction then
   after direction then repeated-target flag; final target mapping/key order.
6. `event_identity`: edges then arrivals, canonical label order; counts/labels.
7. `event_order`: first unequal equality groups S/G; retain their indices/counts.
   Choose the ASCII-lexicographically smallest label x in their symmetric
   difference. If x is in S only, choose y=min(G); otherwise choose y=min(S).
   Report the pair in ASCII lexical order with both exact time pairs. Earlier
   groups are identical, so this witnesses a changed relation without quadratic
   pair search. Diagnostics need not duplicate complete large groups.
8. `final_contacts`: key/contact order.
9. `position_budget`: key order then increasing union-knot time.
10. `root_budget`: edges then arrivals in canonical label order; error first,
    triangle-inequality verification second, analytic bound third.
11. `certificate`: strict schema/encoding/byte cap or transport inconsistency.

`resource` may stop any stage before exceeding a cap; it is an operational
refusal, not evidence of a mathematical failure. JSON/argument/path failures
occur before conversion; no mathematical precedence is implied for those.

Bounds: input 256 KiB/depth 12 under original admission; each retained reduced
rational numerator/denominator at most 4096 bits, checked after every arithmetic
result before retention/use; at most 8192-bit transient products; at most 1032
affine segments/replay, 4608 edges/replay, 512 arrivals/replay, 5634 labeled
records/replay, and 4096 union knots summed across all keys (a shared time on
two keys counts twice). Reject rather than truncate. All canonical label order
in this contract means ASCII lexicographic order, not numeric field order.
Count command applications, segment/contact visits, root constructions, knot
position evaluations and event-sort key/comparator evaluations against a common
**1,000,000-unit** cap; one listed operation is one unit. Cache/sweep position
lookups to avoid uncounted quadratic scans. Storage is finite and allocating;
there is no callback-memory claim. Final UTF-8 certificate is at most 32 MiB;
CGGRID1 text at most 131072 ASCII bytes; refusal JSON at most 8192 bytes.
If an exact diagnostic witness cannot fit that cap, report `resource` with the
diagnostic-size reason instead; never truncate a rational or claim its original
mathematical refusal has been fully witnessed.

The CLI supplies a 30-second monotonic cooperative deadline; check it at each
outer replay/comparison/encoding iteration and before publication. Standalone
acceptance processes use a 60-second external timeout and record timeout as
unqualified, never accepted. The pure API may omit a deadline for deterministic
tests; its count/bit/size limits remain mandatory. No hard real-time deadline or
portable process-RSS ceiling is claimed.

## 5. API, certificate and atomic CLI

Production numerical owner: `tools/contact_grid_conversion.py`:

```python
class ConversionRefusal(ValueError):  # code: str, path: str, witness: dict
    ...
def convert_document(document, *, deadline=None) -> dict: ...
def encode_certificate(result, *, implementation_sha256, contract_sha256,
                       deadline=None) -> bytes: ...
```

The first function revalidates canonical case/metadata, performs no filesystem,
clock-origin, native-process or test-oracle work, and returns the result below;
deadline checks alone may read the monotonic clock. The encoder admits every
nested field/type, adds provenance and emits one sorted-key compact ASCII-safe
UTF-8 JSON object followed by LF, using `allow_nan=False`. No extra fields,
duplicate identities, nonreduced rationals or nonfinite values are accepted.
Before encoding, bound all arrays/strings and reconstruct the original canonical
case from the sidecar. Rerun the bounded conversion and require exact equality
with every supplied numerical/result field; this rejects forged nested facts,
not merely malformed types. The second replay has the same count/bit limits and
shares the CLI deadline. Source-byte hash/count metadata is syntax-checked and
bound by the CLI's actual read; re-encoding cannot independently authenticate
original bytes that it was not given.

All exact numbers use `R={"numerator":"n","denominator":"d"}` with reduced
base-10 strings, positive d, no plus/leading zero, and zero `0/1`. Canonical
binary64 values use exactly 16 lowercase hex digits, big-endian IEEE-754 bytes.
Integer counts/indices remain JSON integers excluding booleans. Schema v1 is:

| Object/array | Exact fields |
| --- | --- |
| Result root | `schema_version`=1, `conversion_id`, `status`=`accepted`, `evidence_class`=`synthetic`, `source_model_id`=`fractional-contact-reference-v1`, `target_model_id`=`causal-contact-grid-v1`, `audio_accuracy`=`unqualified`, `fixture_id`, `input_sha256`, `input_bytes`, `grid_case`, `sidecar`, `scalar_errors`, `edges`, `arrivals`, `commands`, `final_keys`, `preorder`, `position_samples`, `root_bounds`, `summary`, `transport` |
| `grid_case` | `sample_rate_hz`, `frames`, `keys`, `targets`; exact existing grid-oracle field names, with no ignored metadata |
| `sidecar` | `sources`, `keys`, `targets`: original admitted input records in original order/field names, but every float-valued field/array element is encoded as binary64 hex; IDs/frame/source routes remain their original string/integer types |
| `scalar_errors[]` | `path`, `unit`, `source` R, `grid` R, `difference` R = grid-source; paths cover every time/position/threshold/speed and effective duration |
| `edges[]` / `arrivals[]` | `label`, `source_time` R, `grid_time` R; identity is fully encoded in the label |
| `commands[]` | `ordinal`, `key_index`, `source_time` R, `grid_time` R, `source_position` R, `grid_position` R, `before_direction`, `after_direction`, `repeated_target`; last three are the equal admitted facts |
| `final_keys[]` | `key_index`, `source_position` R, `grid_position` R, `source_target` R, `grid_target` R, `closed9` (nine equal Boolean bits) |
| `preorder` | List of equality groups, each a sorted nonempty list of labels; this single sequence has been checked against both replays |
| `position_samples[]` | `key_index`, `time` R, `source` R, `grid` R |
| `root_bounds[]` | `label`, `source_anchor_time` R, `grid_anchor_time` R, `source_anchor_position` R, `grid_anchor_position` R, `source_threshold` R, `grid_threshold` R, `source_speed` R, `grid_speed` R, `error` R, `bound` R |
| `summary` | `max_position_error` R, `position_witness` (sample index/null), `max_root_error` R, `root_witness` (root index/null), `work_units` integer |
| `transport` | `format`=`CGGRID1`, `text`, `sha256` of its ASCII bytes, `partitions`=[] for N=0 or [N] otherwise |
| Encoder-added `provenance` | `implementation_sha256` map of the four Python paths below to actual hashes; `contract_sha256`; `python_version` |

The binary sidecar preserves canonical source frequency/amplitude/phase, signed
route gains, press/release durations, thresholds and all commands. It can recover
the admitted original case, but does not claim preservation of raw JSON spelling.
Every array order above is input order, key/time order for position samples,
canonical label order for paired edges/arrivals/root bounds, and stable
chronological command order. Scalar paths use source key/contact/caller indices.
All declared limits/rounding constants are bound by the version and contract hash.

CLI owner: `tools/convert_contact_grid.py`, invocation
`python3 -B tools/convert_contact_grid.py --input INPUT --output CERTIFICATE`.
Require each flag once, no abbreviations, no stdin/multiple-output options. Use
existing path preflight/load semantics: resolved input and parent may be symlinked;
output leaf symlinks, inode aliases, nonregular endpoints and missing parents fail.
Encode/verify the entire accepted certificate before creating a same-parent temp;
recheck the path plan, write/flush/fsync, recheck again, then `os.replace` exactly
one destination. Clean only the owned temp on pre-replacement failure. Existing
regular output may be replaced on success; on every refusal it remains unchanged.

Exit 0 and empty stdout/stderr mean the certificate was published. Conversion,
argument, path and operational refusal exits 2 with exactly one bounded JSON line
on stdout: `{schema_version:1,conversion_id,status:"refused",code,path,witness}`;
no success fields/grid payload. Invalid-input witnesses contain bounded sanitized
text, not unbounded input. An interruption observed before publication exits 130
and preserves the destination. Successful replacement is the irrevocable commit
point: post-commit handling must never report an uncommitted refusal or promise
rollback. Do not perform fallible work after replacement and then report a failed
conversion. This is not protection against
hostile concurrent directory mutation or power-loss durability of directory data.

The source-tree tool needs only Python standard library and these four files:
`contact_grid_conversion.py`, `convert_contact_grid.py`,
`contact_switching_io.py`, `fractional_contact_reference.py`. A separately named
`ContactGridConversionTools` component may copy exactly those files under `tools/`
and this contract under `docs/`, preserving the relative layout and source bytes.
Do not alter the frozen 48-file `ContactReferenceTools` component or install the
native probe implicitly. CLI hashes its actual four modules and contract.

## 6. Independent acceptance before a completion claim

Freeze complete nine-contact fixtures and expected acceptance/refusal before
candidate evaluation: both midpoint parities; all five reviewed counterexamples;
0/1/subnormal positions; all three rates; global cross-key time collisions;
ties/no-ops; clipped arrivals/equalities; reversals/partial holds; N=0/closure;
muted/shared routes; numerical-budget boundary and quota/bit/byte refusals.
Keep outcomes for **all 36 original fixtures**, especially F09 refusal, without
changing inputs or omitting rejected cases to inflate admission rates.

An independent test oracle must not import candidate conversion/replay helpers.
Verify paired times/positions/preorder/root bounds, exact native grid edges and
full padded snapshots under one-frame/irregular partitions and retry, canonical
sidecar reconstruction, strict schema and transactional I/O failure/alias cases.
Record actual resource observations and all failures. Only then can root admit
the named implementation. Audio/filter/latency/tails, indefinite/full-organ
capacity, live integration and physical contact calibration remain next gates.
