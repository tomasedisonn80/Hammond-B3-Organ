# Independent review of the prospective contact-grid converter

**A49, 16 November 2026: arithmetic verified; converter protocol remains
unadmitted.** A37's [proposal](../research/CONTACT_GRID_CONVERSION_NEXT.md) is a
useful basis for the next contract. Its five counterexamples, unit conversions
and impossibility argument are correct. The remaining decisions below must be
frozen and independently reviewed before implementing the proposed converter.
This review accepts mathematical findings for planning, not a converter,
production route, audio error budget or physical result.

The implemented [grid v1 contract](../CAUSAL_CONTACT_GRID_CONTRACT.md) accepts
explicit finite integer inputs. It has no implicit binary64 converter. Preserve
its identity and the original [fractional model](../FRACTIONAL_CONTACT_REFERENCE.md),
[validation protocol](../CONTACT_SWITCHING_VALIDATION.md), fixtures and reports.

## 1. Independent evidence and source boundary

The [reproducible A49 calculation](../development/2026-11-15-streaming-continuation/reports/A49-independent-arithmetic.py)
uses standard-library exact Fractions and `Fraction.__round__`, derives the
results before comparing selected A37 receipt fields, and imports no candidate
helpers. It does not execute A37's embedded recipe. The
[A49 receipt](../development/2026-11-15-streaming-continuation/reports/A49-independent-arithmetic.json)
records five fragments, six duration-endpoint calculations, midpoint checks,
the actual F09 scalar fields and source comparisons. No native process, build,
broad test suite, waveform or 36-fixture conversion study was run.

| Reviewed input | SHA-256 |
| --- | --- |
| A37 proposal | `87e3a5e513790af7a4dd1fdf4d3ca46852f97acfca5973decbef7449934c1251` |
| A37 author-only Fraction receipt | `b8fb5c44b26f7862a564b017b13138418762d08d6d01837ae61275d3c5f4be88` |
| Original I/O source bound by A37 | `e3219265f1496a36b4f5d8a13941672b46ddc4116f331b7a1b99115a2dac9dc6` |
| Current repaired I/O source inspected by A49 | `1281cd0726a6cf16dcc0ceea8445b4e42900ed995bb82dfea70c6dffdd104cc6` |
| Unchanged fractional numerical kernel | `fc269514eca98c05ee8fb14ff362248d140862cff942a250a01714bb06788e23` |

Nine of A37's ten input hashes still match. The original I/O bytes are recovered
exactly from published `af2b74760ee195c9497b314a1a29172f5238dd44`.
Only `OutputPlan`, `load_input` and `preflight_paths` change, plus the new
`_preflight_input_signature` helper; `parse_input` and its admission helpers
are text-identical. This separates A45's filesystem repair from the numerical
reasoning. Keep A37's original receipt intact. A future invocation must bind its
actual current I/O bytes; the old whole-file hash does not qualify those new
filesystem paths. [A47's separate review](CONTACT_REFERENCE_WINDOWS_REPAIR_ADMISSION.md)
owns their repair admission, while root owns platform qualification.

## 2. Units, rates and exact embedding

Let `T=2^16` ticks/frame, `Q=2^48` position units/full travel, F be frames/second,
and P be the exact rational value of the admitted binary64 duration in seconds.
The original speed is `v=1/(F*P)` full travel/frame. Therefore the ideal grid
speed is `s*=Q*v/T=2^32/(F*P)` position units/tick. The rounded speed s gives
`v'=T*s/Q` and effective full-travel duration `P'=Q/(T*F*s)` seconds.

Nearest-even rounding establishes the following field bounds, before topology
or error-budget admission:

| Field | Bound in its stated units |
| --- | --- |
| Command time | `abs(u'-u) <= 1/(2T) = 2^-17` host frames; divide by F for seconds |
| Target or threshold | `abs(x'-x) <= 1/(2Q) = 2^-49` normalized full travel |
| Moving speed | `abs(v'-v) <= T/(2Q) = 2^-33` full travel/frame; multiply by F for full travel/second |
| Effective duration | `abs(P'-P)/P = abs(s*-s)/s <= 1/(2s)` |

The duration denominator is **the rounded speed s**. These bounds are correct,
but they are not accepted root, accumulated-position or audio tolerances.
Monotonicity in P means the six checked duration endpoints also bound all speeds
in the existing `[binary64(0.0001),1]` second domain: every supported rate maps
within the grid's legal positive `uint32_t` speed range. Keep the explicit grid
range check as a contract requirement.

For reduced `P=p/2^k`, p is odd. The rates factor as
`44100=2^2*11025`, `48000=2^7*375`, `96000=2^8*375`.
Writing `F=2^a*m` gives `s*=2^(32+k-a)/(m*p)`. The odd factor `m>1` cannot cancel
against the power-of-two numerator. Thus **no admitted binary64 duration has an
exact integral speed under this direct mapping**, for either press or release.
No positive-length moving segment has an identical continuous slope. This does
not imply that all moving cases must fail a separately defined approximate,
topology-preserving conversion; isolated roots or bits can still agree.

There is a further oracle boundary: at P=1 second, F=48000/96000 rounds to
s=89478/44739 and produces `P'>1`. At the admitted lower duration endpoint,
F=44100/96000 produces `P'<binary64(0.0001)`. Even when P' is within range,
rounding it back to binary64 changes the grid trajectory. Use an independently
defined exact-grid replay, not a rounded effective duration passed through the
old reference as if that were an exact grid oracle.

## 3. Five independently reconstructed topology examples

Where travel is needed, use a rise from zero with F=48000 Hz, P=`1/2048` second,
`v=16/375` travel/frame and a sufficiently long observation. These are local
fragments; complete admitted nine-contact JSON fixtures still need freezing.

| Fragment | Independent result | Required disposition |
| --- | --- | --- |
| `on=1/2`, `target=1/2-2^-54`, `off=1/4` | Original travel holds below make, leaving the bit open. Both target and on round to `Q/2`; the hypothetical converted path makes at arrival. Target error is only `2^-54` travel. | Reject the distinct target/threshold collision. |
| `off=1/2`, `on=1/2+2^-53` | Both round to `Q/2`; a positive hysteresis width becomes zero. | Reject before replay because grid `off < on` fails. |
| `u=1/2 +/- 2^-18` | Unrounded ticks are `32768 +/- 1/4`; both round to 32768, deleting an interval of `2^-17` frames. | Reject globally, including different keys and later partition boundaries. |
| `c0.on=1/2+2^-53`, `c1.on=1/2` | Source roots are ordered c1 then c0, separated by exactly `375/2^57` frames. Converted thresholds tie and serialization would give c0 then c1. | Reject the threshold collision; retain the lost strict relation as a witness. |
| Actual F09 at 48 kHz, contact 4 | Source make equals command time `375/32`; converted make is `7/2932031008` frames early. | Scalar collision checks pass. Reject at exact edge-versus-command equality comparison. |

The first four examples are refusals under the proposal's own preflight policy,
not admitted grid outputs exhibiting a defect. F09 demonstrates why scalar
checks alone are insufficient. All displayed source fragments are exactly
binary64-representable; none requires replacing a decimal with a different
intended rational.

For F09, `s*=2^36/375`, `s=183251938`, and `s-s*=14/375`. The converted make is
at `2^46/91625969` ticks, or `2^30/91625969` host frames. The command remains
at exactly 768000 ticks. Direct subtraction gives:

```text
375/32 - 2^30/91625969 = 7/2932031008 host frames.
768000*183251938 - Q/2 = 28672 position units.
```

Both keys' make edges still tie with each other, but their relation to all four
tied commands changes from equality to strictly earlier. Incoming equality must
resolve before the commands, whose caller order remains A:0, A:1, B:1, B:0.
All final contacts can nevertheless be open: both final releases reach zero
before N=256 in either trajectory. Final-bit agreement, signed-source
cancellation or silence cannot excuse the lost equality. Histories include
muted contacts, and equal-time edges are independent even when routes share a
source.

## 4. Conditional root bound and the meaning of topology

For matched eligible roots with the same movement direction, let a,p,theta,v
and their primed counterparts denote time anchor, position anchor, threshold
and positive speed magnitude. Put `d=abs(theta-p)`. The proposed inequality
follows by adding/subtracting `d/v'`:

```text
abs(u_edge'-u_edge)
  <= Ea + (Etheta+Ep)/v' + d*Ev/(v*v').
```

It is correct when `Ea`, `Ep`, `Etheta` and `Ev` bound those exact differences.
**Ep is propagated anchor-position error**, including earlier travel, time
rounding, clamp/arrival and reversal effects; it is not merely `1/(2Q)`.
The inequality does not prove that both roots exist, that they correspond to
the same segment, that directions agree, or that equality/order survives.
Holds need their own position comparison. Report exact witnesses and bounds
in host frames/travel, with seconds explicitly derived from F.

Freeze an event correspondence using key index, contact index, direction and
occurrence ordinal. Compare counts, identities, directions and the exact total
preorder of matched edge times, including equality groups, all supplied command
times and 0/N. A matching sorted identity list alone can conceal a tie becoming
strict; final bits alone conceal more. The edge-at-N distinction also controls
whether an edge lies inside the observation gate. Topology agreement still
allows differing contact bits between two shifted roots at the same absolute
time; it is not equality of the contact functions or audio.

Original-versus-grid state comparison must distinguish their surfaces. Original
final positions and targets are rational travel values; native grid snapshots
also contain integer anchors, counters and padded configuration. Compare native
snapshots exactly with an independent grid oracle across partitions/retries.
Compare original-versus-grid positions under declared error criteria, without
pretending that those incompatible snapshots should be byte-identical.

## 5. Required corrections and freezes before implementation

1. **Input and scalar equality rules.** Name canonical admitted binary64 values
   as the conversion input, retaining original JSON bytes/hash separately.
   Existing admission canonicalizes signed zero; “original source bits” must
   mean the admitted values, not a promise to preserve a raw `-0.0` spelling.
   Preserve permitted subnormal source/gain/phase values. Define the per-key
   collision set to include thresholds, every target and implicit initial
   position/target zero, and declare how full-travel endpoint equality is
   handled. A first positive subnormal target rounds to zero and otherwise
   becomes a new initial no-op. Specify dynamic arrival/target/position
   equality and direction checks rather than treating “no new equality” as an
   undefined blanket condition. Stable whole-epoch ordering, cross-key time
   collision rejection and no deduplication/nudging are appropriate.
2. **Certification claim and numeric budgets.** Freeze the admissible subset,
   exact topology predicate, root/position budgets, aggregation rules and
   deterministic rejection precedence before examining candidate error results.
   Include accumulated/held/final position, target arrival and reversal cases.
   Existing v1's `32*ulp` allowance concerns floating-coordinate conversion of
   the same exact root; it is not a new input-quantization budget. No such new budgets
   are supplied by A37 or admitted here.
3. **Audio boundary.** Explicitly decide what the certificate promises about
   audio. A trajectory-only result must mark audio accuracy unqualified. Any
   claim of suitability within a numerical audio tolerance needs a reviewed
   conversion-error allocation, combined reconstruction/filter error policy,
   silence/cancellation handling and full-window independent comparison.
   Preserving source/route bits does not bound switched audio error. The old
   64-probe results and prospective `1e-4`, D=16 and 33-drain-sample proposals
   do not supply that acceptance. This review approves no missing audio budget.
4. **Schema and transactional output.** Replace the prose JSON outline with a
   versioned strict schema: units, reduced-rational encoding, canonical bit
   encoding, ID/ordinal maps, success/rejection variants, source identities,
   field/state errors and exact first-failure witnesses. Specify the rejection
   channel: a JSON rejection cannot overwrite the same destination whose prior
   bytes are promised preservation. Define how certificate, sidecar and
   `CGGRID1` payload are associated and published, including partial failure;
   the transport also needs an explicit partition choice. Freeze output aliases,
   parent/type checks, finite diagnostics and the install payload. Do not reuse
   the grid oracle's permissive extra-field parsing as a strict converter schema.
5. **Independent fixtures and bounded work.** Freeze full fixtures and expected
   acceptance/refusal before implementation, including all five fragments,
   both midpoint parities, endpoints/subnormals, all three rates, collisions
   across keys/partitions, tied changes/no-op anchors, clipped arrival,
   reversal/holds, N=0/closure and muted/shared routes. Retain outcomes for all
   36 original inputs, including F09 refusal under this policy; do not omit it
   to improve an accepted percentage. Freeze independent oracle ownership and
   prohibit candidate conversion/replay helpers in it. Define input/report-byte,
   rational-size, storage/work and elapsed limits with bounded rejection.
   Literal all-pairs comparisons at E=4608 require 10,614,528 edge-pair and up
   to 2,368,512 edge-command/endpoint comparisons; an exact total-preorder
   alternative needs its own equivalence argument. Native finite resource
   bounds do not automatically bound this allocating offline certificate tool.

The next deliverable is a revised, independently admitted converter contract and
frozen fixtures incorporating these decisions. Implementation, native agreement,
audio/full-window qualification, indefinite capacity, live Engine/host use and
physical acquisition remain subsequent source-specific gates. A49 changes only
this review and its own note/calculation receipt; no original proposal or
historical evidence is rewritten.
