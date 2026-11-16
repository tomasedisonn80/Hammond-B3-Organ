# Contact-grid converter proposal

**Unadmitted proposal, A37, 16 November 2026.** No implementation/fidelity claim.
Preserve frozen
[grid v1](../CAUSAL_CONTACT_GRID_CONTRACT.md), [fractional v1](../FRACTIONAL_CONTACT_REFERENCE.md),
[validation v1](../CONTACT_SWITCHING_VALIDATION.md), original reports and
[current guide](../CAUSAL_CONTACT_GRID_GUIDE.md).

## Inputs and units

Inputs: `tools/contact_switching_io.py`, `tools/fractional_contact_reference.py`;
`data/contact-switching/reference-v1/` holds `manifest.json`, `probes.json` and
`F00`–`F11` files at `44100/48000/96000`.
Compare exact trajectories, not displayed coordinates.

Let `b(x)=Fraction.from_float(x)`, `T=2^16` ticks/frame,
`Q=2^48` units/full travel and `R` exact rational round-to-nearest, ties-to-even.
Use integer quotient/remainder/parity, no intermediate floats.

| Original input | Grid mapping |
| --- | --- |
| F∈{44100,48000,96000} Hz, N frames | `sample_rate_hz=F`, `frames=N` |
| `u=frame+b(fraction)` host frames | `tick=R(T*u)`; seconds are `tick/(T*F)` |
| Normalized target, on, off | `position`, `contacts[].on/off = R(Q*b(x))` |
| Full-travel P seconds, press/release separately | `s*=Q/(T*F*b(P))`; `press_units_per_tick` / `release_units_per_tick=R(s*)` |
| Key/contact IDs | Original key/contact indices |

Initial state is zero/open. Sidecar retains source IDs, Hz, amplitude, phase turns
at absolute zero, signed gains and routes as original bits; no waveform conversion.

## Rejection and ordering

Validate original collisions/subnormals and all v1 domains: 1–4 keys, nine contacts, N≤4096,
M≤512 including no-ops/ties/closure, tick∈[0,NT], position∈[0,Q],
`0<=off<on<=Q`, speed∈[1,2^32−1]. No clamping, saturation or rate rescaling.

Stable-sort by exact u and input ordinal. Reject distinct u mapping to one tick
across all keys; preserve tied caller order. Reject interior commands rounded to 0/NT.
Convert the whole epoch once; partition only converted commands.
Distinct per-key threshold/target values must stay distinct; no new no-ops/equality.
Original ties stay independent; never deduplicate or nudge collisions apart.

Independently replay both trajectories. Require identical edge identities/directions,
pairwise time-order signs (including equality), edge-versus-command/0/N relations
and final bits. Reject changes with exact witnesses. Incoming equality precedes
tied commands; endpoint commands are closure-only. Certification covers one epoch.

## Prospective output

Propose `fractional-to-contact-grid-rne-v1`, class `synthetic`, source
`fractional-contact-reference-v1`, target `causal-contact-grid-v1`. JSON contains:

- `schema_version`, `conversion_id`, model IDs, input SHA-256,
  converter/oracle/contract hashes, Python identity, rounding/units;
- `grid_case={sample_rate_hz,frames,keys,targets}` using the existing field
  names in `tests/reference/causal_contact_grid_reference.py`; rejection has
  `grid_case=null`, reason/path and exact witnesses;
- key-ID/index/ordinal maps, unchanged source/route bits;
- `field_errors`, both exact edge ledgers/final states, topology and root bounds.
  Rationals use reduced decimal-string numerator/positive-denominator pairs.

Preflight/atomic success output; rejection preserves prior output.
Emit `CGGRID1` after certification; freeze the install payload.

## Bounds and counterexamples

Rounding gives `|Δu|<=1/(2T)` frames (`1/(2TF)` seconds),
`|Δx|<=1/(2Q)` travel and `|Δv|<=T/(2Q)=2^-33` travel/frame.
Effective duration `P'=Q/(TFs)` has `|P'-P|/P=|s*-s|/s`.
Anchor-position error accumulates. For a matched eligible crossing, positive v,v',
distance d and time-anchor/position-anchor/threshold/speed errors Ea,Ep,Eθ,Ev give
`|Δu_edge|<=Ea+(Eθ+Ep)/v'+d*Ev/(v*v')`. Compute/report these exactly per segment;
it cannot guarantee eligibility or topology.

The [author-only Fraction receipt](../development/2026-11-15-streaming-continuation/reports/A37-fraction-boundaries.json)
checks these fragments:

| Exact original fragment | RNE consequence |
| --- | --- |
| on=1/2, target=1/2−2^-54, off=1/4 | Both round to Q/2: unreachable make becomes reachable with only 2^-54 error. |
| off=1/2, on=1/2+2^-53 | Both round to Q/2: hysteresis collapses. |
| u=1/2±2^-18 | Ticks 32768±1/4 round to 32768, deleting 2^-17 frames. |
| c0.on=1/2+2^-53, c1.on=1/2; F=48000, P=1/2048 | Roots c1,c0 differ by 375/2^57 frames. Rounded thresholds tie; index order becomes c0,c1. |
| F09-48000: P=1/2048, on=1/2, command u=375/32 | s*=2^36/375 rounds to 183251938; edge is 7/2932031008 frames before the command. Equality is lost. |

Threshold/time inputs are binary64-representable. But **no admitted binary64
duration has an exact integer speed**: P is dyadic, while F has odd factor 11025 (44100) or 375
(48000/96000), which cannot cancel in `2^32/(F*P)`. Exact time/position fixtures,
holds and same-topology examples prove no moving-model parity.

## Next files and acceptance

Prospective files after independent review:
`tools/contact_grid_conversion.py`, `tests/test_contact_grid_conversion.py` and
`tests/reference/contact_grid_conversion_oracle.py`; preserve the existing native
`include/hammond/research/CausalContactGrid.h`, `src/research/CausalContactGrid.cpp`
and `tools/causal_contact_grid_probe.cpp`.
Freeze fixtures first: midpoint parity, subnormal/zero,
all three rates, collisions across keys/partitions, order/equality, clipped arrival,
reversal, partial holds, repeated targets, mute/shared routes, N=0 and endpoint
closure. No candidate helpers in the oracle; native/grid-oracle edges
and snapshots must agree across partitions/retries. Retain rejections and all
36 inputs. Missing: reviewed protocol, root/position budgets,
report/work bounds, implementation and independent admission. Audio/full-window
criteria, D=16/33-sample drain, indefinite capacity, live integration and physical
captures remain separate. No original tolerance changes or universal parity claim.
