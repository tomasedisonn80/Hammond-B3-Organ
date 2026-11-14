# Independent rotary motion and propagation scope

This nominal M7 research track is governed by atlas pp. 289–294, 301–324 and
343–348 and the [implementation plan](PLAN.md). The supplied atlas has no new
instrument measurements (p. 2). Its worked examples and reported companion
results are not measurements or executed tests of this repository.

## Current status — 14 November 2026

The [reference-refinement continuation](REFERENCE_REFINEMENT_SCOPE.md) has
implemented and independently qualified the named native **R2 motion and R3
historical propagation** workloads on the source identified in its reports.
[ROTARY_MOTION.md](ROTARY_MOTION.md) records the repaired arithmetic and retained
R2 failures; [ROTARY_PROPAGATION.md](ROTARY_PROPAGATION.md) is the current API,
storage-lifetime, query-boundary, rejection and reproduction handoff.

| Slice | Current evidence and remaining boundary |
| --- | --- |
| R2 | A16/A24 pass seven Python methods with 3,780 native requests and 327,720 separate bit-identical owner-state comparisons. All 66 original underflow failures were independently replayed successfully; original reports remain retained. |
| R3 | A19 passes six independent methods including 1,440 geometry fixtures and 4,466 roots; maximum native residual `9.980e-15 s`, maximum 41 of 48 evaluations. A28 audits admission and adds a passing late-rejection regression. |
| Primitive allocation/lifetime | A27 observes zero C++ allocations/deallocations in the named prepared/query/copy/rejection intervals. This is not a callback or device-deadline qualification. |
| Sanitizers | A44 confirms `26ff2fb` core **137/137** and native **16/16**. Required R2/R3/allocation/oracle gates and all sixteen native gates pass with leak checking enabled; the core suite retains its separate pre-existing MIDI quarantine leak exception. A27's original local full LSan/EPERM failure remains unchanged. |
| R4 → R5 → R6 | The concurrent waveform continuation owns bounded fractional-delay histories and the transactional two-input R4 renderer; R4 acceptance, audible policy and runtime/integration remain separate gates. |

The original reports hash numerical sources added on top of observed HEAD
`e4968b2`; that commit alone is not their tested worktree identity. The later
[A44 hosted audit](development/2026-11-14-reference-refinement/notes/A44-hosted-sanitizer-audit.md)
qualifies their unchanged numerical inputs and A38's repaired allocation fixture
at `26ff2fbe66a50260bd7601cbfa54c1f5d35ff3a8`, tree
`530d5fcf777003f470f64558de9e5631d31a21a4`, a documentation-only child of
`f9c11a4`. The unpublished A40/A41 header refinement is outside those jobs.
The current
[checkpoint](development/2026-11-14-reference-refinement/CHECKPOINT.md) owns
publication status. The original
[2026-11-13 session](development/2026-11-13-rotary/README.md) remains historical.
All fixtures remain nominal/unmeasured, with separate horn/drum radiation-boundary
inputs. Engine sound, all 47 parameters and state4/readers 1–3 stay unchanged.
Scanner G5, M5/M6 inputs, physical captures and device/host qualification remain
separate unresolved work.

## Deliverable

Develop a host-independent, inspectable C++ module and offline tools that:

- retain independent horn and drum speed/angle states under sample-stamped
  Chorale/Tremolo commands, using the declared first-order speed surrogate;
- expose separate horn and drum input waveforms at their effective radiation
  boundaries, with no implicit electrical crossover or organ processing;
- solve emission time for each path from one shared trajectory per rotor;
- render bounded fractional waveform delays with explicit interpolation error,
  algorithmic latency, geometry limits and diagnostic counters;
- preserve the same trajectories across block partitions, silence and command
  reversals, and explicitly define preparation, rejection and rate changes;
- retain reproducible profiles, independent numerical references, tests and
  offline evidence sufficient for the next integration decision.

The default Engine sound, existing parameter IDs, musical state formats, VST3
identities and active scanner/standalone tracks remain owned by their existing
contracts. This module is not inserted in that audio graph in this session.

## Physical and numerical boundaries

All distances are metres in a declared right-handed cabinet frame, times are
seconds, angles are radians, and speed magnitudes are rad/s with a separate
direction sign. Profile metadata identifies proposed numerical fixtures,
documentary information and missing specimen measurements. No proposed speed,
radius, time constant or microphone placement is a factory specification.

The horn and drum inputs are referenced at their modeled effective radiation
points. A stationary driver is not a physically rotating loudspeaker. Horn
transit, crossover/driver response, electrical loading, cabinet reflection,
measured directivity, room and microphone response each need separate effect
ownership. A named unity/omnidirectional diagnostic is permissible; an
unidentified cabinet or directivity model is not.

The emitted waveform and path geometry must use the solved emission time.
Each microphone sees a different emission time from the same physical rotor.
Use a safeguarded finite iteration budget and check the residual. Do not add
an independent pitch modulation oscillator. The centered interpolation kernel
must have causal support; report any added processing latency separately from
propagation. Interpolation and dynamic spectral limits remain explicit even
when the root solver and state tests pass.

Chorale and Tremolo are the baseline commands. A physical stop/brake accessory
is not inferred from a decaying numerical speed. Initial conditions and reset
are offline preparation controls, separate from ordinary musical presets.

## Acceptance and continuation

Freeze tolerances before grading the new runtime. Independent closed-form or
high-precision motion and bracketed propagation references must exercise zero
motion, both signs, rapid reversals, historical queries, integer/fractional
delay endpoints, stereo symmetry, invalid geometry and bounded capacity.
Meaningful renderer tests cover rejection before mutation, event order,
block partition equivalence, rate lifecycle, allocation probes and actual
rendered samples. Source inspection cannot substitute for execution.

Complete M5 dry-organ validation and M6 electrical/driver boundaries are
required before end-to-end cabinet fitting. Physical M7 fidelity additionally
requires identified rotor/microphone captures and held-out comparisons. Native
host integration, audio device deadlines and production anti-aliasing each
remain separate gates. Follow the
[session record](development/2026-11-13-rotary/README.md) for actual progress.
