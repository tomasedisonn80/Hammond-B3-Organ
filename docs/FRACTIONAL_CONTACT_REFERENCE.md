# Fractional contact reference v1

## Status, purpose and preserved boundaries

This freezes the proposed executable **offline Python standard-library** scope
for independent review and implementation; it reports no numerical pass.
Model identity is `fractional-contact-reference-v1`, evidence class `synthetic`.
It implements a fixed-load, normalized switched-sine reference for M3; neither
contact resistance/bounce nor transformer, percussion or expression circuitry
is inferred. The nominal dry Engine, existing contact model IDs, 91 source IDs,
47 sound parameters, `B3CONTROLS4` and readers 1–3 remain unchanged.

Basis: [atlas](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf), pp. 109–120;
[remaining M3 gate](M3_REMAINING_AND_SCANNER_GATE.md#2-m3-work-that-remains);
execution notes [A02](development/2026-11-15-execution-continuation/notes/A02.md)
and [A06](development/2026-11-15-execution-continuation/notes/A06.md).
The atlas's `1e-4` normalized-RMS proposal is neither a factory tolerance nor an
achieved result. Hardware fidelity still requires synchronized acquired evidence.

## 1. Input, interfaces and bounded domain

Three owned implementation files separate pure numerics, admission and command:
`tools/fractional_contact_reference.py`, `tools/contact_switching_io.py`, and
`tools/contact_switching_reference.py`. No C++ or live processing API is added.
Proposed CLI: `python3 -B tools/contact_switching_reference.py --input FILE
--factor L --output REPORT`; all three options are required, no implicit render.

Strict input JSON has exactly these top-level fields:

| Field | Required value or record |
| --- | --- |
| `schema_version`, `model_id`, `evidence_class` | `1`, identity above, `synthetic` |
| `fixture_id` | ASCII `[A-Za-z0-9][A-Za-z0-9._-]{0,63}` |
| `sample_rate_hz`, `frames` | F in `{44100,48000,96000}`; integer N in `[0,4096]` |
| `sources` | 1–36 unique records `{source_id,frequency_hz,amplitude,phase_turns}` |
| `keys` | 1–4 records `{key_id,press_seconds,release_seconds,on,off,source_ids,gains}` |
| `targets` | 0–512 records `{frame,fraction,key_id,target}`, in caller order |

Source IDs are integers 1–91, independent of list index; frequency is in
`[0,0.45*F]` Hz, amplitude in `[0,1]`, phase in `[0,1)` turns at absolute time zero.
Every key ID is unique and uses the fixture-ID grammar. Each key has exactly
nine entries in `on`, `off`, `source_ids` and `gains`; every referenced source
exists. For each contact independently, `0 <= off < on <= 1`; thresholds need
not be sorted or distinct across contacts. Gains are fixed signed multipliers
in `[-1,1]`; each full-travel duration is in `[0.0001,1]` seconds.
All source amplitudes and gains are explicit; no factory map or gain is inferred.

`frame` is an integer, `fraction` is in `[0,1)`, and target is in `[0,1]`.
The absolute host coordinate is `u=frame+fraction=F*t`, in `[0,N]`;
at frame N only fraction zero is legal. Reject a nonzero fraction lost when
added to its frame in binary64. Integers reject booleans; numeric fields reject
booleans and nonfinite values. Canonicalize signed zero, never clamp an input.
Reject duplicate JSON members, unknown/missing fields, invalid identifiers,
duplicate key/source IDs, unresolved routes, invalid bounds and UTF-8/JSON errors.
Input is at most 256 KiB, nesting at most 12, and factor L is exactly one of
`{32,64,128,256}`. No stochastic, bounce, harmonic, leakage, rate-change,
gain-automation, arbitrary-initial-state or physical-unit extension belongs to v1.

Pure kernel values use immutable tuples, independently validated at entry:
`Source=(source_id,frequency_hz,amplitude,phase_turns)`;
`Key=(key_id,press_seconds,release_seconds,on9,off9,source_ids9,gains9)`;
`Target=(frame,fraction,key_id,target)`;
`Case=(sample_rate_hz,frames,sources,keys,targets)`.
Input arrays become tuples without reordering keys, sources or targets.
Reject distinct supplied `(frame,fraction)` pairs that round to the same
binary64 absolute coordinate; identical pairs remain legal and stably ordered.
Interpret admitted float values as exact binary64 rationals using
`Fraction.from_float` for bounded offline trajectory preparation: command time,
position, target, duration, velocity, endpoints, eligibility, equality and roots.
Keep exact coordinates through ordering, state changes and cell clipping. Only
source/filter evaluations and displayed coordinates are rounded to binary64.
This is an offline preparation choice, not a real-time implementation technique.
`build_trajectory(case)` returns `Trajectory=(segments,edges,final_keys)`.
`Segment=(key_index,u0,u1,q0,velocity_per_host_frame,target)` includes holds;
`Edge=(u,key_index,contact_index,closed_after)` uses zero-based key/contact indices;
`FinalKey=(position,target,closed9)` follows key input order at u=N.
Segments are ordered by key index then u0; edges by time, key index, contact index.
`render(case,factor)` returns `Render=(trajectory,first_frame,samples,bound,work)`;
samples are a tuple of finite binary64 values, `first_frame=-16` when N>0.
Trajectory scalar fields may be immutable `Fraction` values. `Render.bound` is
the outward-rounded raw bound B below, and `Render.work` is the declared W.
`read_samples(render,first_frame,count)` returns a tuple addressed by absolute
host-frame coordinates; integer arguments reject booleans and out-of-range
intervals. Empty reads are allowed at either endpoint. It reads the complete
immutable render, without recomputing or restarting the convolution. This is
output-range/tail preservation, not streaming-filter-state qualification.
Validation raises `ValueError` before any result; helpers have no file I/O.

## 2. Continuous travel, equality and stable event ordering

Every key begins at position=target=0 with nine open contacts. For a target
command at u0, preserve current position and all contact bits. Until the next
command, move toward its target at `+1/(F*press_seconds)` or
`-1/(F*release_seconds)`, stop exactly on arrival, then hold. Repeating the
current target is an exact no-op; it does not rebase a moving segment.
Target commands are stably ordered by `(frame,fraction,input_ordinal)`.

Resolve the incoming continuous segment **through** its end time before applying
all commands at that time in their original order. No time passes between those
commands; their last target for a key determines outgoing motion. They cannot
create a contact edge by themselves. A threshold reached exactly at a target or
reversal time still switches. On an upward segment, an open contact closes at
`on`; on a downward segment, a closed contact opens at `off`. Holding inside the
hysteresis band preserves history. Equal-time edges are retained independently
and serialized by key input index, then contact index; never merged by source ID.

For an eligible threshold theta on a moving segment starting at `(u0,q0)`, use
`u_edge = u0 + (theta-q0)/velocity`, provided it is reached before or exactly at
the segment endpoint/target. This uses **full unsaturated velocity**, never
linear interpolation between positions clipped to a target at a host boundary.
Split the segment at arrival and command times. Contacts are right-continuous;
audio intervals are half-open. Do not use epsilon merging of nearby events.
Report edge time as `frame=floor(u_edge)`, `fraction=u_edge-frame`, normalized
once with carry if a computed fraction is exactly 1; zero is positive zero.

At u=N resolve incoming edges, then apply commands at N to the final snapshot;
those commands have no duration. For N=0, apply stable time-zero targets but
return no segments, edges or audio samples; positions/contacts do not advance.
For this empty render, `first_frame=0`, time offset=0, filter metadata/hash=null,
cell/filter counts=0 and `work=M+10*K+len(sources)`; factor is validated and
retained but unused, B is still computed, and elapsed time/memory are observed.
No quadrature grade applies. This is an offline flush, not Engine serialization.
There are at most nine threshold candidates/edges per effective target segment,
bounded conservatively by `9*M` for M supplied commands.

## 3. Shared sources and exact switching before bandwidth reduction

For source s, `s_s(u)=A_s*sin(2*pi*(phase_s+f_s*u/F))`. Its phase depends only
on absolute time and its explicit identity. Notes, silence, disconnected paths,
block boundaries and repeated foldback routes never restart or privately copy it.
The raw signal is `x(u)=sum_contacts gain_j*c_j(u)*s_source(j)(u)` for `0<=u<N`,
and is **exactly zero outside [0,N)**. This finite observation gate is part of the
synthetic experiment: it can create a terminal jump at N even with held contacts.
It does not release keys or erase their final snapshot. The oracle must split at
both 0 and N and include this gate; it must never silently continue the source.

Compute the exact rational `B_exact=sum_contacts abs(gain_j)*A_source(j)` from
the admitted binary64 inputs, and report B as the smallest binary64 value at
least B_exact. Only `B_exact==0` qualifies as exact-zero routing. This avoids
rounding nonzero subnormal products into a false zero-bound declaration.
No polyphony-dependent normalization, fitted gain or clipping is applied.
Each contact owns its own transitions even when its gain is zero or sources
collide. Aggregate contributions only after evaluating those histories.
For each physical edge retain signed jumps `gain*Delta(c)*s(t_edge)` and
`gain*Delta(c)*ds/dt(t_edge)` (slope per second); record observation-gate jumps
separately. Physical edges at N remain in the ledger with
`inside_observation=false`; the terminal gate jump is minus the ungated
left-limit value/slope, so those physical edges are not counted twice as audible
jumps. At zero source frequency use the same phase/constant-value rule.

Internal cell j is `[(j-.5)/L,(j+.5)/L)` in host coordinates. Define
`xbar_L[j]=L*integral_cell x(u)du`, split at every relevant exact contact edge
and observation endpoint. For a connected sine over [a,b], its integral is
`A*(b-a)*sin(2*pi*(phase+(f/F)*(a+b)/2))*sinc((f/F)*(b-a))`,
where `sinc(z)=sin(pi*z)/(pi*z)` and `sinc(0)=1`.
Use the stable small-argument limit and `math.fsum` for signed contributions.
Only j=0 through N*L can be nonzero. No base-rate switched render is an input
to this step. Thus fractional switching is resolved before the first reduction.

## 4. Finite filter, gain, time and complete tails

Freeze support H=16 host frames and cutoff beta=0.45 cycles/host frame:

```text
k(v) = 2*beta*sinc(2*beta*v) *
       (0.42 + 0.5*cos(pi*v/H) + 0.08*cos(2*pi*v/H)), |v| < H
k(v) = 0, |v| >= H                         [endpoints forced exactly zero]
R = H*L; Z_L = fsum(k(r/L), r=-R..R)
w_L[r] = k(r/L)/Z_L
y_L[n] = fsum(w_L[r]*xbar_L[n*L-r], r=-R..R)
```

Reject a nonfinite/nonpositive Z_L. Discrete DC gain is unity by this declared
normalization; finite floating summation residual is reported. This Blackman
windowed sinc is a named approximation, not an ideal brick-wall or measured
organ response. Report its coefficients or their canonical binary64 hash,
sum, absolute sum, support, cutoff and actual normalized response at the
protocol's frequencies. `output_bound=B*fsum(abs(w_L[r]))` is a mathematical
ideal bound, not a certified floating-point rounding or headroom gate. Report
observed peak separately. `coefficient_sha256` hashes concatenated big-endian
binary64 `struct.pack('>d',w_L[r])`, r=-16L through 16L, with positive zero and
no prefix/header/text encoding; it identifies normalized coefficients.

For N>0 return **N+33** samples, n=-16 through N+16 inclusive, at physical times
`t=n/F`. This is an offline centered, acausal convolution with zero-phase
alignment, not a realizable zero-latency callback. Stored index i corresponds
to time `(i-16)/F`; declare `first_frame=-16`, `time_offset_seconds=-16/F`.
If a container starts index zero at time zero, that is a documented 16/F timeline
shift, not evidence of a causal runtime's latency. Do not fit/subtract another
delay, normalize amplitude or trim tails. Endpoints are zero; outside this
returned host-index range outputs are zero. Keep all cells/filter contributions
across notes and chunk boundaries. A different F is a separate replay in
physical seconds with unchanged source phase origin; mid-render rate changes
are rejected, not treated as preserving a runtime's filter history.

## 5. Resource admission and transactional outputs

Before cell/filter allocation, compute the conservative dominant-work bound
`W=(N+33)*(32*L+1)+(N*L+1)*9*K+18*M+(32*L+1)` for K keys, M commands.
It counts tap products, cell/contact pieces, threshold/edge work and coefficients;
it is not a CPU-instruction or elapsed-time guarantee. Require `W<=20,000,000`;
N=0 uses the bounded event-only path. Store a single accumulated cell vector,
not a dense contact-by-cell matrix. Build ordered per-contact intervals once and
sweep cells/edges; scanning the entire edge ledger for each cell violates this
work contract. Report actual elapsed time, peak memory,
sizes and work; the complete declared reference suite is capped at 300 seconds,
256 MiB resident memory, 180 million FIR products and 10 million oracle
integrand evaluations. An overrun is incomplete, never a convergence pass.

Admit and validate the entire input, numeric domain, path aliases and budgets
before opening any output or creating its parent. Reject missing parent,
input/output alias (including resolved symlinks/hardlinks), unsupported output
type, nonfinite intermediate/result or budget failure. Return nonzero with a
bounded diagnostic on stderr; no success-shaped partial report on stdout.
Compute and validate the complete finite report before atomic same-directory
temporary-file replacement. Clean owned temporary files on failure and preserve
any previous destination byte-for-byte; never delete another user's files.
One invocation writes one report. Subsequent experiment attempts use distinct
report paths so failed/inconclusive runs and their exact criteria are retained.

Report schema v1 root keys are `schema_version`, `model_id`, `evidence_class`,
`fixture_id`, `input_sha256`, `implementation_sha256`, `python_version`,
`platform`, `sample_rate_hz`, `frames`, `factor`, `first_frame`,
`time_offset_seconds`, `samples`, `raw_bound`, `output_bound`, `work`, `caps`,
`observations`, `targets`, `edges`, `final_keys`, `filter`, `gate_jumps`.
Targets retain stable processing order and `input_ordinal`. Every edge includes
`exact_u={numerator:decimal_string,denominator:decimal_string}`, normalized
display `frame`/`fraction`, `key_index`, `contact_index`, `closed_after`,
`inside_observation`, `value_jump`, `slope_jump_per_second`. Exact coordinates
own ordering even when generated roots share rounded displays. Final keys retain
input order and `key_id`/`position`/`target`/`closed`. Observations include
`elapsed_seconds`, `peak_resident_bytes` and the measurement method; an unavailable
measurement is null with an explicit reason and cannot pass a resource gate.
For N>0 filter contains `H`, `beta`, `normalizer`, `coefficient_count`,
`coefficient_sha256`, `sum`, `absolute_sum`, `dc_residual`, `responses`.
For N=0 it is null and output_bound is zero. All numeric results are finite;
null is reserved for declared empty/ineligible/unavailable fields. JSON forbids
NaN/Infinity. No report may qualify a different source or an unrun factor.

## 6. Independent admission and scope of conclusions

Use [the independent protocol](CONTACT_SWITCHING_VALIDATION.md), whose
author must not reuse production crossing, cell-integral or filter helpers.
Its continuous reference is `y(n)=integral k(v)*x(n-v)dv / integral k(v)dv`,
split at actual edges, gate endpoints and support. Eight-point Gauss–Legendre
quadrature refines panel widths 1, 1/2, 1/4 host frame; retain every comparison.
The frozen suite has 12 fixtures at each of three rates, N=256, all four factors,
and 64 deterministic oracle probes per fixture including both boundary tails,
floor/ceil edge neighborhoods and fixed stratified coverage. Short known-answer
fixtures additionally check closed-form edges, integrals and filter conventions.

Normalize samples/errors by outward B **before** RMS squaring; use the normalized
reference RMS floor `1e-8`, avoiding underflow in either squares or `1e-8*B`.
Below that floor report absolute-only/ineligible status.
B=0 requires exact zero output. Oracle final refinement requires peak error
`<=1e-9*B` and eligible NRMSE `<=1e-7`. Factor 128→256 requires peak
`<=6e-5*B`, NRMSE `<=3e-5`; factor 256 versus converged independent probes
requires peak `<=2e-5*B`, NRMSE `<=1e-5`. Pair agreement alone proves nothing
about oracle accuracy; disagreement/failure remains explicit and never widens
v1 limits. These are proposed engineering budgets, not observed outcomes.

Include source peaks/zero crossings, zero frequency, signed/zero gains, shared
source collisions, partial holds, reversal at equality, clipped-arrival roots,
simultaneous contacts, repeated targets, release/repress, gate truncation,
irregular chunk partitions, empty flushes and rejection/output preservation.
Probe admission covers those probes only; it does not establish all-sample or
out-of-band accuracy. Any optimized-renderer atlas `1e-4` claim requires a
separately admitted full-window comparison and complete response/resource
evidence. Native integration and measured keyboard fidelity remain separate.
