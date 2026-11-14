# R4 implementation review brief

Status: implementation brief for wave-2 review; not an accepted API or test result.
The unchanged [numerical contract](ROTARY_NUMERICAL_CONTRACT.md), especially
sections 4–6, remains authoritative. This brief connects the accepted R2/R3
primitives to the next discrete waveform implementation without connecting it
to the existing dry Engine.

## Ownership and bounded history

One processor owns two independent continuous motion owners, two double
waveform rings, and four prepared rotor-to-microphone paths. Waveforms are
normalized signals at the effective horn/drum radiation boundaries. They are
not a newly invented electrical crossover or calibrated acoustic pressure.
Add signed Horn then Drum paths for each microphone, with only the contract's
reference-distance/path-distance gain. Preserve absolute timing and polarity.

The immutable R3 fixture history, capped at 4,097 command segments and beginning
at frame zero, cannot be reused as an unbounded streaming event queue. A useful
bounded representation retains the original event-anchored MotionSegment for
each frame covered by the propagation window. Querying an emission floor index
selects its retained segment, then evaluates the exact fractional position.
This must not reanchor motion at process-block boundaries. Same-frame events
retain their input order; only the final future target is needed after their
common boundary, while every event is consumed in the declared order.

Prepare capacity from the maximum admitted path delay, plus the exact fixed
latency and cubic support. Preserve the 16,384-frame cap and allocation-free
processing. Define negative-time motion and negative audio separately, support
all four interpolation nodes, and never invent an unavailable future sample.

## Required reviewed API properties

- Preparation accepts the existing `Profile` and `ProcessSpec`, performs full
  orbit admission and resource allocation before replacing a prepared owner.
- Process accepts separate const double horn/drum spans, separate mutable
  left/right spans and ordered `CommandEvent` values. Length, alias, finite
  magnitude, event and timeline admission precedes persistent mutation.
- Exactly two frames of algorithmic latency are separate from propagation.
  Write input n, observe n−2, solve four paths and read centered cubic support.
- Expose copied physical state and bounded diagnostic metadata for tests and
  tools. Diagnostics must not fabricate measurements or enter musical state.
  Keep call-local counters separate from partition-invariant physical state.
- Define transaction scratch and persistent storage precisely. A late failure
  must restore waveform/motion histories, physical state and diagnostics, leave
  caller output unchanged and consume zero events. Review a bounded journal or
  prepared candidate storage; demonstrate nonzero-history rollback in tests.
- Reset restores original profile seed/commands at the current rate with silent
  histories. Stopped rate replacement preserves current phase/turns/speed and
  commands, starts a new epoch, discards tails and admits constant-speed negative
  motion. Invalid or allocation-failed replacement preserves the old object.
- Expose the prescribed complete zero-input flush length. Silence advances
  motion; no GUI, transport or musical preset is allowed to own its clock.

## Independent acceptance ownership

Separate implementation from cubic polynomial/static-grid characterization,
streaming-history boundary tests, same-cubic oracle construction, transactions,
partition/event equivalence, lifecycle/rate/symmetry and allocation probes.
Retain input/source identities and actual worst/RMS errors. The complete frozen
ten-second all-rate comparison and blocks 1/7/64/257/4096 plus irregular
partitions remain acceptance requirements, even if their full workloads run
outside the ordinary fast CTest configuration. Any reduced smoke has its own
explicit name and cannot replace the complete gate.

Use independent mathematics or independently authored reference code; do not
call the production renderer to generate its own expected output. Static cubic
characterization retains high-frequency error even where the low-band budget
passes. R5 reconstruction/alias policy and R6 real-device integration remain
separate from this exact discrete-signal implementation.

The [session scope](development/2026-11-14-waveform-continuation/README.md) and
[checkpoint](development/2026-11-14-waveform-continuation/CHECKPOINT.md) record
actual assignments, reviews, implementations and results as they occur.
