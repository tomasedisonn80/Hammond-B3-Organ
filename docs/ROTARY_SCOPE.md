# Independent rotary motion and propagation scope

This nominal M7 research track is governed by atlas pp. 289–294, 301–324 and
343–348 and the [implementation plan](PLAN.md). The supplied atlas has no new
instrument measurements (p. 2). Its worked examples and reported companion
results are not measurements or executed tests of this repository.

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
