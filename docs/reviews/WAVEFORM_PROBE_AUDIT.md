# Independent waveform probe audit

**Reviewer:** actual A23, `/root/w04_a23_probe_audit`, 14 November 2026.
**Result:** no implementation blocker found in the frozen probe/reference and
reviewed runner. This is a source audit plus validation of existing smoke
evidence. **A23 did not execute or accept the full ten-second experiment.**
Exact identities, executed checks and limitations are retained in the
[worker note](../development/2026-11-14-waveform-continuation/notes/A23-probe-audit.md).

## Contract-to-implementation findings

| Requirement | Observed implementation and finding |
| --- | --- |
| Complete full workload | `run_rate` renders `10*Fs` for all four frozen rates, with fixed blocks 1/7/64/257/4096 and the fourteen-length irregular pattern. Only the last block is shortened. Totals are 3,801,000 reference frames, 22,806,000 native frames and 38,010,000 direct alternate-partition scalar comparisons. |
| Independent expected values | The reference header includes only standard headers. Its timeline, Cartesian geometry, delay solver and product-form cubic are independently implemented. Only fixture values, events and absolute-index inputs are shared. Every canonical frame calls `expected.at`; no native state, support sample, root, gain or output enters that calculation. |
| Inputs, latency and paths | Horn/Drum use separate salts and sequences. Observation is fixed at `n-2`; reported native latency is checked against two. Reference channel-major paths map explicitly to native rotor-major paths through `[0,2,1,3]`. Horn precedes Drum in each signed sum. No fitted gain/delay, clipping or extra frequency effect occurs. |
| Events and exact replay | Inclusive end admission consumes each ordered event once, preserving ties and both final `10*Fs` commands. Alternate streams compare each output's binary64 bits. State and persistent diagnostics enumerate 32 and 46 fields respectively; padding and call-local counters are excluded. |
| Failures and resources | Numerical/bit mismatches retain complete per-channel frame bitmaps, counts, first/last indices, hashes and worst values. Exceptions fail the run and retain stage/partial counts. One canonical rate buffer peaks at 30,720,000 bytes; expected samples are streamed, with a single current native block. |
| Provenance and admission | SHA-256 uses explicit little-endian binary64 stream encoding and three known vectors. The Python runner rejects missing/malformed/incomplete reports, wrong modes, altered budgets, unequal replay, source drift and failed processes. It preserves raw stdout/stderr and records source, executable, precision and build facts. |

## Executed evidence and boundary

The existing `rotary-r4-shifted-input-smoke-v1` report passed admission with
four rates, 24 completed partitions, 98,328 native frames, 360 consumed events,
163,880 equal direct comparisons and maximum normalized error
`1.20659368074701270776e-9`. A23 independently regenerated its inputs and
matched all 24 hashes. Nine runner self-tests and 64 selected Decimal path
checks passed. These are actual lightweight checks of retained evidence.

Smoke shifts nonnegative input indices by `2*Fs` to exercise bounded nonzero
signals in 4,097 frames while preserving negative-time zero; its separate name,
duration, counters and report admission prevent promotion to full acceptance.
It does not traverse the full impulse/silence/event schedule or one complete
irregular-pattern cycle. Full execution must supply its own complete report.

Command-only calls, explicit offset-N followed by a later offset-zero call,
routing/symmetry, reset/rate replacement, history and rollback fixtures remain
separate behavioral evidence. Static-grid execution belongs to A14 and is
admitted as retained evidence by the runner. Build-command observation is not
proof that a preexisting binary was rebuilt; the integrator must use the
coherent build-before-run target. R5, R6 and physical fidelity remain separate.
