# Next causal contact audio stage

**16 November 2026: prospective, unadmitted `causal-contact-audio-grid-v1`.**
Build on the [grid trajectory](../CAUSAL_CONTACT_GRID_CONTRACT.md). Preserve the
[offline model](../FRACTIONAL_CONTACT_REFERENCE.md),
[validation](../CONTACT_SWITCHING_VALIDATION.md), [earlier proposal](../CONTACT_STREAMING_NEXT_DESIGN.md),
reports, dry Engine, 91 source identities, 47 parameters and state4/readers 1–3.

## Signal and clocks

Propose F=44100/48000/96000 Hz, L=256, 1–4 keys/nine routes each, ≤36 unique
sources (IDs 1–91, frequency 0..0.45F Hz, amplitude 0..1, phase [0,1) turns),
signed gains −1..1 and immutable epoch configuration.
Initially qualify **N≤256**, blocks ≤256 and ≤512 commands including closure;
the trajectory's existing 4096-frame domain remains intact.

For root `(T,a,b)`, exact `u=(T+a/b)/65536` gives input time t0+u/F.
Phase phi at declared origin t0 defines `s(u)=A*sin(2*pi*(phi+f*u/F))`.
Raw x sums gain×contact-bit×shared-source. Resolve contacts independently;
silence/disconnection, notes and callbacks never restart phase. Output m at
t0+m/F represents reference n=m−16; delay never changes input phase.
Prepare outward B off-thread; underflow/cancellation cannot establish zero
routing. Apply no gain fitting or polyphony normalization.

## Cells and the actual filter indexing

The [Python source](../../tools/fractional_contact_reference.py) uses
`C[j]=L*integral x(u)du` over `[(j−.5)/L,(j+.5)/L)`, gated to `[0,N)`;
only j=0..NL contribute. Cell boundaries are **256j±128 integer ticks**.
Clip at exact roots/cell/gate boundaries; form exact widths/midpoints before
binary64 analytic sine integration.

Carry completed pieces and per-route open starts in the host-boundary cell.
Callbacks create no integration breaks: finish an unchanged connected interval
once. Freeze deterministic signed-piece accumulation; rounding combined gains
or partial sums can lose cancellation residuals. Prove portable exact clipping,
width/midpoint arithmetic separately from the grid's root-comparison proof.

Keep H=16, beta=.45 and the normalized Blackman-windowed sinc.
`_filter_coefficients` stores c[k]=w[k−16L], k=0..32L, with exact mirrored
symmetry and zero endpoints. `render` sums **ascending j**:

```text
y[n] = sum_j C[j] * c[nL−j+16L]
z[m] = y[m−16] = sum_j C[j] * c[mL−j]
```

Decimate at **mL**, phase zero. Nonzero support is
`(m−32)L+1 ≤ j ≤ mL−1`; its newest cell ends at `m−1/512`. Emit z[m] before
integrating `[m,m+1)`: unfinished cell mL has zero weight, allowing **D=16**.
Check library FIR phase/order/endpoints; compare cross-language arithmetic.

Retain the next output's cells and the open cell in a proposed
32L+2=8194-cell ring; evict only below that output's lower bound.

## API, closure and ownership

Prospective files: `include/hammond/research/ContactStream.h`,
`src/research/ContactStream.cpp`, `tests/test_contact_stream.cpp`,
`tests/reference/contact_audio_grid_reference.py`. First admit
`docs/CAUSAL_CONTACT_AUDIO_CONTRACT.md`.

| Proposed operation | Required behavior |
| --- | --- |
| `prepare(config, limits, origin)` | Unprepared/ready/drained only: validate/copy configuration, prepare storage/phases. |
| `process(frames, targets, output)` | Grid commands in `[cursor,cursor+frames)`; incoming endpoint edges retained; exactly frames contiguous outputs. |
| `close_observation(endpointTargets)` | No travel; apply ordered endpoint targets, retain bits/position; finalize cell NL's left portion, zero only its right portion. |
| `drain(count, output)` | After closure: exactly count outputs; reject excess count/short output. Partial drains retain state; count zero is identity. |
| `reset(origin)` | After complete drain: clear histories, explicitly set phase origin. Rate change requires drain/prepare; no seamless conversion. |

For **N>0**, process m=0..N−1 then drain m=N..N+32: **33 extra samples**,
all N+33 reference n=−16..N+16 including endpoint zeros (N256 gives 289).
**N=0** closure applies time-zero targets and is immediately drained: no audio.
Release is ordinary travel. Keep N's physical edges, endpoint commands, final
snapshot and gate jump from the ungated left limit distinct. Drain advances only
output m; input trajectory remains at N and phase never follows output time.

Stage trajectory, audio contact cursor, cells, ring, origin and output cursor
together. Replay edges from entry bits, never final bits. Noncopyable
`CausalContactGrid` commits inside `process`; `snapshot()` cannot restore it.
Review a private stage/commit seam preserving its public semantics. Validate/stage
before writes; late numeric failure preserves all state/output bytes. Reject closed
processing, repeated closure, premature reset/reconfigure, excess limits and
zero-frame targets; empty valid processing is identity. Serialize access and
borrow spans per call. Prepare/replace/destruct off-thread.

## Admission before implementation and grading

One ring costs 65,552 bytes; coefficients, rollback, endpoints, event/piece and
summation/output staging add storage. Prove capacities/work including bursts;
avoid all-edge scans per cell. No allocation/free, locks, logging or I/O
in process/rejection/drain. Original reference W is **4,744,518** at
N256/K4/M512/L256, versus **71,595,078** at N4096, above its 20-million cap.
These planning counts supply no audio deadline or resource admission.

Use an independent exact-grid oracle: speed s implies duration
`2^48/(65536*s*F)`, generally not exact binary64 and sometimes outside v1's
range. Rounding changes trajectory. Separately admit original-fixture conversion/
topology error. Extend quadrature to all samples of every retained 289-sample
row under frozen resource limits; 64-probe admission gives no full-window grade.
Proposed peak/B and eligible NRMSE 1e−4 limits remain unadmitted. Preserve
refinements/responses/tails/failures; allow only D=16 alignment.

Cases: half-cell/gate clipping; cell/host/closure equality; equal-display roots;
DC/high frequency; shared phase after silence; cancellation/subnormal B;
no-ops/reversals; N=0/1/256; early ringing without a forced 16-zero prefix;
single/irregular/max blocks; split/empty drains; ring wrap; future causality;
late rejection/short output/retry. Require exact same-build partition output/state,
exact grid events and independent audio grades. Later gates cover 4096 frames,
full-organ/indefinite clocks, platform deadlines, host latency/retirement and Engine
routing. Physical bounce/resistance/loading/calibration need acquired evidence.

The [bounded index audit](../development/2026-11-15-streaming-continuation/reports/A38-audio-index-audit.json)
binds source hashes, one coefficient construction and index/count algebra only.
No audio implementation, render, oracle, build or physical grade is delivered.
