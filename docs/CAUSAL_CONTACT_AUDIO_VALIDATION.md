# Causal contact audio: independent frozen validation inputs

**16 November 2026 — A12, wave 2; preimplementation freeze for independent
review.** Evidence class: **synthetic**. This document and
[`contact_audio_cases.py`](../tests/reference/contact_audio_cases.py) freeze
inputs and acceptance decisions before candidate code or candidate errors are
examined. They implement neither an audio candidate nor an oracle and report no
numerical pass. The [audio contract](CAUSAL_CONTACT_AUDIO_CONTRACT.md) defines
the signal, API and arithmetic. Its independent review must admit both documents
before implementation. A change to a frozen input, threshold, budget or model
requires a reviewed new protocol version and preservation of the earlier result.

This is a new **integer-grid** study. The original F00–F11 binary64 fixtures,
their [validation](CONTACT_SWITCHING_VALIDATION.md), 64-probe reports and
conversion acceptance/refusals retain their exact identities. No Gxx or Sxx
row is a replacement for, or an assertion of equivalence to, an Fxx row.

## 1. Four separate decisions

| Decision / protocol | Inputs and acceptance boundary |
| --- | --- |
| Exact-grid discrete parity, `contact-audio-exact-grid-validation-v1` | All 75 G/S inputs; independent exact trajectories and L256 cell/filter reconstruction; every sample; exact event/state and same-build partition/lifecycle gates. |
| Exact-grid continuous grade, `contact-audio-grid-full-window-v1` | Every output of all nonempty G/S inputs; independently converged direct continuous quadrature. The 36 G rows are the nominal matrix; subnormal and exact-empty rows retain explicitly separate classifications. |
| Original reference expansion, `contact-audio-full-window-continuous-v1` | All original 36 F00–F11/rate rows at their unchanged binary64 inputs; all 289 outputs and retained refinement/response/tail diagnostics. This gate remains open until that distinct run passes. |
| Conversion and native comparison against originals | Original input, certified conversion or retained refusal, original/converted L256 difference and native/original continuous difference. An event-topology certificate is necessary but supplies no audio-error result. All 36 original rows remain accounted for. |

Passing one row, one rate or one decision cannot close another. In particular,
discrete L256 parity is not continuous accuracy; exact grid arithmetic is not
binary64-fixture equivalence; software grades are not a measured instrument,
callback deadline, host latency, device or Engine-routing grade.

## 2. Input authority, provenance and independence

The fixture module is the sole executable recipe authority. It returns fresh
JSON-compatible dictionaries using the existing grid fields
`sample_rate_hz`, `frames`, `keys`, `targets`, and additionally `sources`,
per-key nine-entry `source_ids`/`gains`, and `origin_frame`. All grid positions,
thresholds, speeds and target ticks are explicit integers. They never pass
through a duration converter or an implicit rounding step.

`origin_frame` is an exact host-frame **label**, inclusive ±2^48. The configured
phase is phase at that origin. The label does not enter source evaluation;
reset replays the same phases at a new label. Sources retain independent IDs
1–91, shared phase and independent route histories. All fixtures start from
the grid contract's zero positions/targets and open contacts.

Canonical input encoding recursively replaces each binary64 value with the
single-member object `{"binary64": value.hex()}`; integers remain integers.
Serialize sorted keys, compact separators, ASCII escapes and exactly one final
LF. The module's `canonical_bytes` and `manifest` define this encoding and bind
every case. Hex tags preserve exact binary64 inputs without depending on a
decimal JSON reader's rounding. The manifest has 36 nominal plus 39 stress
rows, in recipe/rate order. The [freeze receipt](development/2026-11-16-runtime-continuation/reports/A12-fixture-freeze.json)
binds the source/module/document/input-manifest hashes, original F manifest and
all original F bytes. The [worker note](development/2026-11-16-runtime-continuation/notes/A12.md)
states exactly what was and was not executed.

The independent oracle author reconstructs each key's affine path, arrivals,
hysteresis, event order, connected intervals, B, cells, kernel and convolution
from the contracts and these inputs. Use Python standard-library `Fraction`
for exact trajectory/interval arithmetic. Do not import candidate/native/grid
oracle/old renderer crossing, clipping, cell-integral, summation or filter
helpers, or use candidate-generated edges as quadrature boundaries. Sharing
these fixture definitions and equations is intentional. Candidate and Python
may share system libm; record that limitation instead of claiming independent
transcendental libraries. The discrete oracle may use `math.fsum`; it must not
copy the candidate's compensated streaming recurrence.

Freeze the oracle source and its independently reconstructed expected facts
before reading candidate comparison errors. Bind every subsequent report to
the exact fixture manifest, protocol, oracle/native/header/build/compiler/libm
identities, command, current commit plus dirty inputs, platform and timing.
Preserve original failures and interruptions. A changed implementation may be
rerun under a new hash; previous observations retain their original meaning.

## 3. The 36 nominal integer-grid rows

Run each G01–G12 recipe at **44100, 48000 and 96000 Hz**, N=256, L=256,
H=D=16. Let Q=2^48 and T=65536 ticks/frame. Defaults: one key, press=2^28 and
release=2^27 units/tick, source ID7, A=1, f=997 Hz, phase=.137 turns; only
contact index 4 has gain 1. All nine routes name source ID7. Thresholds in
contact-index order are:

| Field | Exact integer values |
| --- | --- |
| on | `(4,7,10,13,17,20,23,26,29)*(Q/32)` |
| off | `(1,4,7,10,13,16,19,22,25)*(Q/32)` |
| targets | `(tick=0,position=Q)`, `(tick=48T,position=0)` on key 0 |

All integers in those expressions are exact. Decimal signal values and divisions
such as `1/9` denote their frozen binary64 values, as bound by the manifest.
Changes in the following table replace only the specified defaults. Target
lists include closure targets; tied entries retain their supplied order.

| ID | Frozen changes and required discrimination |
| --- | --- |
| G01 | All gains zero. Moving contact histories, exact positive-zero samples and complete silent tails. |
| G02 | f=0, phase=1/4. DC pulse, plateau gain, half cells, pre-ringing and release tails. |
| G03 | f=F/32, phase=63/64. Contact 4 makes at exact u=17/2, phase=5/4 turns: positive source peak. Retain actual finite-libm residual. |
| G04 | f=F/32, phase=47/64. The same make is at mathematical phase 1 turn: zero value with nonzero slope. Do not snap a numerical residual to zero. |
| G05 | f=2F/5. High-frequency source with the unchanged declared filter and attenuation. |
| G06 | Key 0 has all gains1/18 and targets `(16T,Q),(64T,0),(128T,Q),(192T,0)`. Key 1 has only gain4=1/2 and targets `(23T+128,Q),(83T+128,0)`. Both share source ID7. Initial and intervening silence cannot restart phase; the half-cell offset remains exact. |
| G07 | All gains1/9; targets `(0,Q/2),(128T,0)`. Four contacts close when half travel is approached from below. |
| G08 | All gains1/9; targets `(0,Q),(32T,Q/2),(128T,0)`. Five contacts remain closed at that same hold when approached from above. |
| G09 | All gains1/9; targets `(0,Q),(6T,0),(12T,Q),(12T,Q),(17T,Q),(72T,0)`. Reverse before full travel, break/repress, tied duplicate and later no-op; preserve original anchors. |
| G10 | Two keys with contact4 on=Q/2, off=3Q/8, gains +1/2 and −1/2. Targets at0 bothQ; at8T key0 gets0 thenQ, key1 getsQ then0; at72T both0. Incoming equality closes both contacts before those stable tied commands. |
| G11 | Contact4 on=2049Q/4096, off=3Q/8. Targets `(0,513Q/1024),(64T+T/4,0)`. Its make at8+1/256 and arrival at8+1/64 share a host sample interval; unsaturated travel, not interpolation to a clamped endpoint, determines the root. |
| G12 | Press=2^29, release=2^28, all gains1/9; targets `(0,Q),(256T,0)`. Early ringing is valid before m16; the closing target causes no travel, while the observation gate retains its left limit and the complete tail. |

Unlike the earlier physical-time F recipes, these are explicit host-grid
gestures at each rate. Their durations in seconds differ across rates. Each
rate has its own waveform and oracle; cross-rate sample identity is not a gate.

## 4. The 39 explicit stress rows

Every S00–S12 recipe also runs at all three rates. These are separate inputs,
not substitutions for nominal rows. Unspecified values use the defaults above.
Let p=2^32−1, r=p−1. Repeated thresholds still represent nine independent
contacts, including muted ones.

| ID / N | Exact construction and required distinction |
| --- | --- |
| S00 / 0 | Origin −Q. Closing targets `(0,Q),(0,0),(0,Q)`. Three commands, zero positions/open bits, final target Q, empty audio and zero drain. |
| S01 / 1 | Origin +Q; both speeds p; all off0/on1. Targets `(0,1),(T,0)`. One-frame epoch, initial/terminal half cells, closure without release travel. |
| S02 / 1 | Both speeds2^20; all off=`(T/2)*2^20`, on=`T*2^20`; DC phase1/4. Targets `(0,Q),(T,0)`. Incoming make exactly at N leaves closed physical bits but no audible interval; terminal left value is zero. |
| S03 / 1 | Both speeds2^20; all off0/on=`128*2^20`; DC phase1/4. Targets `(0,Q),(T/2,0)`. Make exactly at cell0's right boundary; break exactly at N. Final bits are open while terminal ungated left value is1. |
| S04 / 256 | Both speeds1. Contact0 off0/on1, others offQ−1/onQ; only gain0=1. Targets `(0,Q),(128T,0)`. Minimum speed, unreached full-travel target, exact terminal break after reversal. |
| S05 / 4 | Both speeds p; on=`(9,1,9,5,2,8,3,7,4)`, each off=on−1; all gains1/9; f=9F/20. Targets `(0,Q),(2T,0)`. Maximum speed, maximum frequency, unsorted/repeated thresholds and very close roots. |
| S06 / 256 | Four keys, 36 unique IDs `(1..35,91)`, source array reversed. Source i=0..35 has f=`F*(i+1)/128`, A=`1/(1+i mod4)`, phase=`(i mod16)/16`. Key k/contact c routes source index9k+c; gain=−1/36 if `(k+c) mod3=0`, otherwise+1/36. Each key targets Q at `k*(3T+128)`, 0 at `(128+k)T`. Maximum sources/routes, signed sums and ID lookup independent of configuration order. |
| S07 / 64 | Both speeds p, all off0/on1; DC phase1/4. Gains `[1,2^-54,-1,0,0,0,0,0,0]`; targets `(0,1),(64T,0)`. Known positive cancellation residual 2^-54 must survive; precombining gains is detectable. |
| S08 / 1 | Both speeds p, all off0/on1; DC phase1/4, A=2^-1074 and gain4=2^-1074. Targets `(0,1),(T,0)`. B_exact=2^-2148; outward B=2^-1074 and exactZeroRouting=false although the binary64 product is zero. |
| S09 / 64 | Both speeds p, all off0/on1; DC phase1/4, A=2^-1022, gain4=1. Targets `(0,1),(64T,0)`. Gradual-underflow waveform tier; do not confer nominal relative accuracy on its absolute allowance. |
| S10 / 256 | Origin−Q, press p/release r; all off=p−2/on=p−1; DC phase1/4. With t=255T−1, targets `(t,p−1),(t+1,0)`. Positive connected interval whose two host endpoints both round to255.0. |
| S11 / 256 | Origin+Q, press p/release r; all off0/on1; DC phase1/4. With t=`256*65535−128`, targets `(t,1),(t+255,0)`. Connected interval inside cell65535 with a72/80-bit numerator/denominator width and89/81-bit midpoint. |
| S12 / 1 | Four keys, both speeds p, all off0/on1, all gains1/36, shared ID7. At every tick0..127 command every key in index order to1 if even,0 if odd. Exactly512 commands,4608 edges and2304 connected pieces fit in cell0's positive half. |

S10/S11 are explicit realizations of the published
[A50 arithmetic counterexamples](reviews/CAUSAL_CONTACT_AUDIO_NEXT_REVIEW.md).
S10 roots are `(255T−1+(p−1)/p)/T` and `(255T+1/r)/T`, hence exact width
`(1/p+1/r)/T>0`; subtracting their binary64 displays would lose it. S11 roots
are `(t+1/p)/T` and `(t+255+1/r)/T`. Their exact width and midpoint are formed
before binary64 conversion. These identities and S12's count are mathematical
input witnesses, not candidate execution results.

## 5. Discrete oracle and numerical decisions

The oracle independently rebuilds all physical edges, including muted and tied
ones, exact connected intervals, final targets/anchors/bits, and exact rational
`B_exact=sum(A*abs(gain))`. Return the smallest binary64 B≥B_exact, with an exact
zero predicate. Cancellation or product underflow cannot establish B_exact=0.
Compare grid edge count/time/direction/key/contact/order exactly, and every grid
snapshot field exactly. No epsilon may merge events. Since the stream has no
public edge output, a probe may obtain an independent native grid trace for
comparison; that trace must not become the oracle's authority. Arithmetic-helper
tests compare exact limb ratios and correctly rounded conversion bits against
independent `Fraction` expectations, including invalid domains and rounding ties.

Reconstruct exact centered cells at L256, splitting only at true physical
edges/cell/gate boundaries, then independently reconstruct the finite kernel and
ascending-j convolution. Use every m=0..N+32 for N>0, corresponding only to
**n=m−16**. N0 is empty. Require positive-zero output at m0 and mN+32;
never require a16-sample zero prefix. No fitted gain, fitted delay, rephasing,
clipping, normalization, pooling across rows or omitted tail samples is allowed.

For each row report max absolute error, RMS error, reference RMS, peak/B and
eligible NRMSE. Compute error and reference samples divided by B **before**
squaring; NRMSE is eligible only when RMS(reference/B)≥1e-8. Below that floor
report `ineligible`, not zero or a manufactured NRMSE pass. B_exact=0 requires
all samples to be exact positive zero. Nonfinite values always fail.

| Discrete gate | Frozen requirement |
| --- | --- |
| Ordinary B≥2^-900 | All-sample peak/B≤1e-10 and eligible NRMSE≤1e-9, separately for every row/rate. |
| Cancellation S07 | Also peak(error)/2^-54≤1e-10, and candidate m48 is positive with `abs(candidate[48]/2^-54−1)≤2e-13`. Its full-support interior is a DC witness, not a fitted scale. |
| Noncollapsed S10/S11 | Also nonzero candidate peak and peak(error)≤1e-9 times the independent discrete oracle's nonzero peak. A B-normalized tolerance alone could miss a lost tiny interval. |
| Underflow 0<B<2^-900, including S08/S09 | Exact rational comparison `max_abs_error≤1e-10*B+2^18*2^-1074`, plus exact upward B and exactZeroRouting checks. Retain peak/B diagnostically; no nominal relative-error/NRMSE pass is conferred. |
| Coefficients | Exact mirrored bytes and positive-zero support endpoints; finite positive normalizer; DC residual≤2e-14; absolute coefficient sum≤2; oracle/candidate max coefficient difference≤5e-16. |
| Edge/gate diagnostics | Independently retained signed per-contact value/slope jumps and distinct observation-gate jumps. For ordinary B, value error≤2e-12B and slope error≤2e-10B·max(1,2πfmax), slope in amplitude/second. Underflow jump diagnostics are retained without a nominal relative jump grade. |

The ordinary margins are engineering headroom for the bounded piece/FIR sums
and named binary64/libm builds, not a theorem about every transcendental library.
The explicit underflow floor permits accumulated rounding on unrepresentably
small outputs; it cannot be relabeled as nominal relative accuracy. S07, S10
and S11 retain additional scales so tiny meaningful signals cannot disappear
behind a large B. Failed witnesses remain failures; they cannot be removed as
"pathological" after errors are observed.

## 6. Same-build partitions, causality and transactions

Run every row with a single N-frame process call, all one-frame calls, and the
repeating pattern `[1,7,3,32,2,19]` truncated to N. Insert valid empty calls
before/after each irregular block. Split targets by their unchanged absolute
integer ticks; process endpoints belong to the next call or closure. For N>0
combine these with drains `[33]`, thirty-three calls of1, and
`[0,7,0,13,13,0]`. N0 closes directly and permits only zero drain. These nine
process/drain combinations must produce bit-identical concatenated samples and
equal observable snapshots at common cursors on the same strict build.

In addition to final state, compare continuations from common cursors and a
test-only complete committed-state observation where needed: public snapshots
omit private ring bytes. Different scratch bytes are irrelevant. Preserve the
input clock during draining, all33 tail samples and both endpoint zeros. Ring
wrap occurs repeatedly in the N256 rows; partial cells must remain unchanged
when a call ends at an integer frame.

Compare complete semantic state internally at the cursors common to each pair
of schedules, using named fields and exact floating bits, not object padding.
Keep only a bounded number of comparison states in memory. Retain complete
final public snapshots, compared-cursor counts, compact state identities and
the first mismatch with its field/cell index and values. Do not serialize a
complete large private object for every frame/partition. State identities
support provenance; they do not replace the actual internal equality check.
This compact native report has its own 64 MiB retained-byte ceiling. Report
actual native work/time separately; nine native schedules are not charged to,
or qualified by, an oracle-only product count.

For every nominal row, freeze causal-prefix cuts P=`1,16,64,128,255`. Compare
the original stream with a variant retaining only original targets with tick
<PT, then appending all keys to0 at PT, all keys toQ at `(P+1)T` if P+1<N,
and all keys to0 at NT as closure targets. Within each new group use key order.
At the common cursor P, before commands at PT are applied, require identical
emitted sample bytes and committed physical/audio history. Future targets or
the later observation gate cannot revise those emitted samples. Later output
may differ and is retained. At least G06 is also replayed with origin labels
0,−Q,+Q; same phases/commands give identical sample bytes and appropriately
translated labels.

The separate lifecycle suite must exercise all contract statuses and precedence
pairs, excess frames/commands, endpoint/zero-frame errors, duplicate sources,
unconfigured IDs, malformed last targets, short output, untouched suffixes and
retry. Require full committed-state/output preservation after late staged numeric
failure in process **and closure**, through a test-only fault hook with no
production backdoor. Also cover reset/reprepare before complete drain, repeated
close, zero/overlong drains, origin limits, replay after reset and rate replacement
while ready before any input is consumed, or after complete old-rate drain once
input has been consumed. An early validation failure does not prove late
rollback. These requirements are not implemented by the fixture module.

## 7. Full-window continuous quadrature and retained diagnostics

For both continuous protocols independently integrate
`r[n]=integral x(u)k(n−u)du / integral k(v)dv`, using the contract's finite
H16, beta.45 Blackman-windowed sinc and unchanged source/route gains. Rebuild
true trajectories from the appropriate **exact grid inputs or original binary64
inputs**; do not convert one into the other's parser.

Use independently implemented eight-point Gauss–Legendre quadrature, split at
every oracle-derived contact/gate/support boundary. Form exact interval widths
and quadrature coordinates before binary64 conversion, including equal-displayed
endpoints. Subdivide smooth intervals into panels no wider than1,1/2,1/4 host
frame. Recompute the continuous normalizer at every width. Retain all three
estimates at **all N+33 output indices**, including both complete tails; for
each original F row this means all289 samples, not the old64 probes.

| Continuous decision | Every applicable row/rate and complete output |
| --- | --- |
| Oracle refinement | Width1/2 versus1/4: peak/B≤1e-9 and eligible NRMSE≤1e-7. Retain width1 differences. Failure blocks a continuous grade. |
| Nominal discrete convergence | L128 versusL256: peak/B≤6e-5, eligible NRMSE≤3e-5. Retain L32→64 and L64→128 arrays/differences/orders without assuming monotonicity. This is required for every G nominal and original F row. Stress rows retain L256 plus continuous refinements; they do not acquire a four-factor convergence claim. |
| New grid native/full continuous | Every nonempty ordinary G/S row: peak/B≤1e-4 and eligible NRMSE≤1e-4 against the independently converged width1/4 reference. Exact-grid discrete admission and all required preceding gates are prerequisites. |
| Original F reference expansion | Original L256 versus full converged quadrature: peak/B≤2e-5, eligible NRMSE≤1e-5. Preserve original inputs and stricter original reference criteria when extending coverage. |
| Original/converted L256 | Conversion-only peak/B≤2e-5, eligible NRMSE≤1e-4, plus accepted topology/error certificate. Refused conversions remain refused; do not substitute a G row. |
| Converted native/original continuous | Peak/B≤1e-4, eligible NRMSE≤1e-4 after only D16 translation; all original-reference and conversion prerequisites required. |

B=0 and RMS eligibility retain section5 semantics. For S08/S09, compare exact
rational absolute error with `t*B+2^18*2^-1074`, where t is the peak/B threshold
of the relevant gate: 1e-9 for oracle refinement and 1e-4 for native/continuous
comparison. These rows receive only an explicitly labeled underflow result,
never nominal relative accuracy or NRMSE admission. The discrete parity tier
retains its separate t=1e-10 requirement.
N0 is an exact empty/lifecycle result with no continuous quadrature grade. No
all75 "nominal accuracy" claim is permitted.

Retain independent continuous/discrete normalizers, coefficient sums, all source
responses and tail diagnostics. For L32/64/128/256 characterize the complete
stationary renderer response including source cell-average `sinc(nu/L)` at
nu=j/256, j0..256, and1.5,2. Retain continuous response from independent
quadrature, DC residual, passband ripple nu≤.30, transition response, sampled
stopband nu≥.60 and phase where magnitude≥1e-8. These are characterizations,
not a new physical or stopband admission. Retain full-output L256−L128 RMS/peak,
unwindowed DFT residual energy in `[0,.30],(.30,.45],(.45,.50]`, and tail energy
for nominal G and original F rows. Finite-window leakage is not physical aliasing.

The original F expansion also retains `ceil-edge-same-kernel-v1` at all289
indices, widths1/2 and1/4, with stable equal-time order, common source phase,
the same observation gate and independently computed kernel. Its refinement
uses the same1e-9/1e-7 limits. Report differences without an assumed success
direction. All its quadrature is charged to the new original-expansion budget;
the old64-probe reports and10-million ceiling remain unchanged historical gates.

## 8. Prospective independent resource budgets

The three numerical jobs below have independent whole-job ceilings, frozen
before candidate errors. Unused capacity cannot be transferred between jobs.
These ceilings cover independent numerical reconstruction, not the separate
native partition/lifecycle/allocation test invocations. Native work/memory must
also satisfy the [audio contract](CAUSAL_CONTACT_AUDIO_CONTRACT.md#6-floating-environment-and-source-bound-resources)
on every admitted build; neither set of bounds proves a callback deadline.

| Job | FIR products | Cell/route visits | GL8 integrand evaluations | External elapsed / peak exact-child RSS / retained reports |
| --- | ---: | ---: | ---: | --- |
| Exact-grid discrete, all75 | ≤180 million | ≤180 million | None required for this decision | ≤600s /512MiB /64MiB |
| Exact-grid full continuous | ≤256 million | ≤256 million | ≤64 million | ≤600s /512MiB /64MiB |
| Original F expansion and converted comparisons | ≤256 million | ≤256 million | ≤64 million | ≤600s /512MiB /64MiB |

An integrand evaluation means one real or complex GL8 node evaluation, including
normalizers, response and retained ceil-edge diagnostics. Report source-sine/
route evaluations separately, including any reuse. Cache only mathematically
identical oracle quantities; do not count repeated candidate array reads as
new oracle work or omit a new quadrature evaluation from the counter. Record
wall time externally around the exact child and an actual peak-RSS measurement;
missing resource observation leaves resource admission incomplete. Stream rows
and retain compact JSON rather than per-term logs.

The ceilings are independently motivated by these **input-only upper counts**:

* All75 inputs have15,075 nonempty output samples. Using the conservative full
 8193-tap span gives **123,509,475** L256 FIR products and **38,127,456**
 cell/route visits. The real clipped/zero-endpoint count can be smaller.
* Four-factor rendering of the36 G rows uses **159,847,056** products. Adding
 all stress L256 rows gives **198,116,559**, before response diagnostics, below
 the256-million ceiling. Original F four factors plus36 converted L256 rows
 use **245,087,028**; all discrete response grids add fewer than4 million.
* For one nonempty row, let E=9M, with M all supplied commands including
 closure, and S=min(N,32). At width h the conservative per-output panel bound
 is `ceil(S/h)+E+1`. Count8 nodes/panel. This allows all physical boundaries,
 even muted/tied ones, plus an optional kernel-center cut. With all three
 widths and all output indices the75 grid inputs require at most
 **47,998,224** evaluations by this bound.
* The36 unchanged original F rows require at most **25,635,456** for three
 full-window widths plus **20,641,536** for the two-width full-window ceil
 diagnostic: **46,276,992**. Normalizer/continuous response evaluations at
 all259 frequencies and all three widths add at most466,000 when reused
 across identical normalized rates. Both full-window jobs fit separately
 below64 million without inheriting the64-probe limit.

These counts establish planning headroom, not observed runtime. Keep the old
reference's per-invocation W≤20,000,000 unchanged where that renderer is used.
The grid study's worst N256/K4/M512/L256 planning W is4,744,518; it does not
replace exact implementation-specific counts. Resource overrun is **incomplete**,
with retained partial evidence, rather than a numerical pass/fail or permission
to enlarge a frozen ceiling. Retain actual counts and their counting definitions.

Each completed job retains every input hash, full output/refinement arrays,
exact events/state/jumps, response/tail/residual summaries, metrics and failed
cells, plus all source/configuration/toolchain hashes and resource observations.
Compact reports preserve enough values for an independent grader to reproduce
each decision. Failures, unsupported environments, rejected conversions, missing
runners and unrun continuous work stay visible in the final acceptance table.

## 9. Remaining scientific and product gates

No acquired bounce, resistance, transformer loading, source-waveform, tuning,
specimen or synchronized gesture/contact/source/dry measurements are supplied
here. The finite kernel is not strictly bandlimited; numerical convergence
does not establish the bandwidth or loading of a physical B-3/AO-28. Preserve
the default dry Engine,91 source identities,47 parameters, B3CONTROLS4/readers1–3
and plugin UUIDs. Full-organ/indefinite processing,4096-frame audio, allocation
and stack observations, native platforms, device deadlines, host retirement,
live routing and physical calibration retain their own acceptance gates.
