# Sample-rate lifecycle

The nominal engine supports an explicit rate transition between **44,100**,
**48,000** and **96,000 samples per second**. It preserves the current musical and
dynamic state while changing coefficients that depend on the sampling interval.
This is a stopped or same-processing-thread operation between processing calls.
It provides no concurrent publication protocol, native device transition, host
reactivation procedure or callback deadline guarantee.

The [research atlas](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf) requires explicit
source phase ownership through rate changes (p. 105), continuous percussion state
(p. 135), a wrapper-independent core (p. 385), and host-specific deactivation/setup
for native lifecycle changes (p. 394). The API below implements the nominal core
policy. It does not establish any of the cited native host behavior or a measured
mechanical/electrical model.

## Public API and admission

```cpp
Status Engine::reconfigure_sample_rate(double sample_rate) noexcept;
double Engine::sample_rate() const noexcept;
```

The copied rate diagnostic returns zero before the first successful `prepare()`.
After preparation it returns the installed rate in samples per second. A failed
preparation or rate change preserves the previous installed rate. All diagnostics
require the same processing thread or stopped processing.

Admission has a deliberate order:

| Condition | Result | Effect |
| --- | --- | --- |
| Engine is unprepared | `NotPrepared` | No state change, even if the requested rate is invalid |
| Rate is outside the exact supported set, including NaN/infinity | `InvalidSpec` | Complete state preserved |
| Rate equals the installed rate | `Ok` | Exact no-op; no coefficient rebuilding or trajectory rebasing |
| Owned source profile or a module cannot support the new rate | Its validation status, normally `InvalidProfile` | Complete state and future output preserved |
| Every validation succeeds | `Ok` | Install the new rate and rate-dependent candidates together |

There is no clamping, resampling fallback or replacement profile. Source increments
must remain finite in `[2^-53, 0.5)` turns per sample; the upper limit is strictly
below Nyquist. A profile that is valid at 96 kHz can therefore reject a transition
to 44.1 or 48 kHz. Very small frequencies can also violate the lower support bound
after a rate increase. [NUMERICAL_BOUNDS.md](NUMERICAL_BOUNDS.md) explains that
computational bound and its accuracy limits.

## One transaction across owned modules

Engine first validates its owned `RuntimeProfile` at the proposed rate. It then
copies `TonewheelBank`, `ContactBank` and `PercussionState` into local candidates
and calls each candidate's `reconfigure_sample_rate()` method. No installed module
changes while another candidate can still reject the transition. Only after all
three succeed does Engine install them and change `ProcessSpec::sample_rate`.
These are fixed value copies; this path performs no allocation, file access,
logging or locking. Coefficient computation and copying remain lifecycle work.

| State | Transition behavior |
| --- | --- |
| All 91 sources | Preserve current phases, frequencies, amplitudes and cached samples; replace per-sample increments |
| Every manual key | Preserve held target identity, current normalized position, target and all nine contact bits |
| Moving contact segments | Rebase from the preserved current position and recompute steps from owned press/release durations in seconds |
| Contact hysteresis | Preserve it exactly; a rate change itself evaluates no contact edge |
| Shared percussion | Preserve readiness exactly; recompute slow/fast decay and recovery coefficients from the owned profile |
| Musical controls | Preserve all retained banks, selected routes, expression and percussion settings |
| Cached mix coefficients | Preserve arrays, dirty flag and eligibility cache; routes, current connections and source amplitudes are unchanged |
| Process specification | Change only `sample_rate`; retain maximum block size, initial origin and seed |
| Render clock | Preserve the current 64-bit frame count; no sample elapses |

The source phase, contact travel and readiness still advance once after rendering
each current-state sample, including disconnected output. A zero-frame call
advances none of them. The first sample following a rate change uses the same
current dynamic state; subsequent state advancement uses the new interval.
[CONSOLE_DYNAMICS.md](CONSOLE_DYNAMICS.md) defines that rendering convention and
the unmeasured contact/percussion coefficients.

## Frame count and elapsed seconds

`frame_clock()` continues counting rendered frames. It does not become wall time,
transport position or a clock expressed in seconds. `initial_frame` is an origin;
it does not request simulated history. A sample-rate change performs no wall-clock
catch-up and does not reinterpret previously rendered frames.

For a reproducible mixed-rate run, the caller must retain the transition schedule,
for example `(frame 1000, 48000 Hz)` followed by `(frame 5800, 96000 Hz)`. For each
segment, elapsed model time is its number of rendered frames divided by that
segment's rate. Add the segment durations; dividing the final frame count by the
last rate is generally incorrect. Future sample-offset events remain the caller's
responsibility, including any conversion from an external seconds-based timeline.
The current offline renderer selects one rate for an entire render; this API does
not silently extend its score or evidence format with mixed-rate events.

## Preparation, controls and input ownership

Successful `prepare()` deliberately starts a new seeded engine state. Rate
reconfiguration preserves the existing state. A retained musical-control document
is neither operation: [B3CONTROLS2](CONTROL_STATE_FORMAT.md) saves musical controls,
excluding source phase, contact motion, readiness, rate and frame history.

The [note-ownership adapter](NOTE_OWNERSHIP.md) retains its existing owners through
a successful Engine rate change because physical targets do not change. Its sole-
note-authority requirement still applies. Deliberately preparing or replacing an
engine must instead coordinate ownership as described by
[INPUT_PROCESSOR.md](INPUT_PROCESSOR.md). This rate API does not renegotiate host
buses, change maximum block sizes or merge pending external event streams.

## Verification boundary

The source, contact and percussion lifecycle suites check their module contracts
independently. The continuation's
[assignment 34 note](development/2026-11-13-continuation/34-engine-rate-lifecycle.md)
records the Engine implementation smoke and its exact source snapshot. Assignment
35 supplies separate permanent Engine acceptance tests. Combined publication and
hosted-platform results belong to the continuation ledger and current status.
No written interface or local check substitutes for an actual native host/device
transition, concurrent-access qualification, physical calibration or deadline test.
