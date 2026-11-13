# Assignment 08: shared percussion readiness module

Agent: `/root/w02_a08_shared_percussion`, continuation wave 02, 2026-11-13.
Implemented only `include/hammond/Percussion.h`, `src/Percussion.cpp` and this
note. The integrating agent owns Engine, controls, persistence, renderer,
shared status documents and publication. No commit or push was performed here.

## Sources, scope and model identity

Read the standing agent instructions, current development handoff, plan and
research review, continuation review 02, and atlas pp. 127-138. Source:
[preserved research atlas](../../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf).
Its source hash and limits are retained by the repository's research manifest.

The new algorithm is **`shared-readiness-v1`**, exposed as
`kPercussionModelId`. It implements the explicitly temporary, dimensionless
readiness surrogate on p. 129; it is not a capacitor-voltage or complete AO-28
circuit model. One `PercussionState` belongs to one organ, with no note count,
voice allocation, source oscillator or per-note retrigger inside it.

| Nominal field | Value and unit | Evidence and uncertainty |
| --- | --- | --- |
| Slow decay | 1.551 s | Derived isolated R58*C31 hypothesis, p. 135; not measured audible decay |
| Fast decay | 0.37524193548387097 s | Derived `(R57 parallel R58)*C31` from nominal parts on pp. 133/135; loading and bias unresolved |
| Recovery | 0.03432 s | Derived `(R55+R56)*C31` hypothesis, p. 135; actual recharge unresolved |
| Normal / soft gain | 1 / 0.5, normalized amplitude | Proposed engineering levels; specimen transfer and cutoff unknown |
| Fast gain multiplier | 1.5 | Proposed use of the approximate increase reported on p. 134; no acquisition or bias model |
| Normal upper sustain gain | 0.7071067811865475 | Proposed `1/sqrt(2)` attenuation, approximately -3.0103 dB; not a measured R1 network |
| Readiness gain map | `F(q)=q` | Proposed linear surrogate, p. 129; not a fitted valve transfer |

These fields do not identify a specimen, circuit revision, transformer response,
percussion leakage floor or calibrated electrical voltage. The named factory
function is `make_nominal_percussion_profile()`; default zero initialization
instead produces an invalid profile so unknown data cannot silently become the
nominal model.

## Public contract for integration

`PercussionSettings` stores `enabled=false`, harmonic `Second`, volume `Normal`
and decay `Slow` by default. The three enums use explicit 0/1 values.
`is_valid_percussion_settings()` checks every enum, including while disabled.
The settings support equality for control-state persistence and tests; they
contain no transient readiness state.

`PercussionState::prepare(profile, sample_rate)` returns the existing `Status`
vocabulary. It validates all inputs and prepares three exponential coefficients
before installing any state. Success installs owned values and sets `q=1`.
Failure retains the prior profile, coefficients, rate and readiness. A new,
unprepared instance reports `prepared=false`, `q=0`, rate zero. Preparation is
initialization, not a phase/history-preserving sample-rate migration operation.

The engine renders sample `n` with `gain(settings)` and current `readiness()`,
then calls `advance_frame(routed_detector, settings)` exactly once. With an
active detector it multiplies q by the prepared slow/fast decay coefficient.
With an open detector it computes `q += (1-q)*recovery_step`, where preparation
uses `-expm1(-1/(Fs*tau_recovery))` to retain the small positive increment.
There is no block-size term and no exponential calculation in advancement.

The engine must resolve the routed detector as:

```text
eligible = settings.enabled && upper_route_enabled && upper_selected_bank == B
routed_detector = eligible && OR(upper physical contact[8])
```

Readiness survives route, tablet and drawbar changes. Under the chosen nominal
policy an ineligible/open route recovers; reconnecting uses the accumulated q.
The ninth physical contact is independent of audible 1-foot gain. Percussion
audio comes from current upper second/third-harmonic contacts at indices 3/4,
using the existing shared source frame and no sustained drawbar multiplier.
The engine must independently mask only the eligible upper-B sustained 1-foot
branch, without clearing its stored control or physical contact.

`gain(settings)` includes current q, normal/soft level and fast boost. It returns
zero for disabled, invalid or unprepared use. `upper_sustain_gain(settings)` is
separate: Normal returns the profile's attenuation; Soft/disabled/invalid/
unprepared returns unity. Apply that attenuation only to eligible upper-B
sustain, never lower-manual or percussion audio. The module does not know a
bank or route and cannot enforce this engine integration boundary itself.

`advance_frame()` rejects unprepared use, invalid settings, or a connected
routed detector while percussion is disabled, returning false without changes.
The engine's eligibility predicate prevents the latter inconsistent request.
Disabled settings with an open detector are valid and recover normally.
A zero-frame call must not call advancement; same-offset release/repress
therefore supplies no recovery interval. Merely reading gain, diagnostics or
new settings never changes q. `diagnostics()` returns a fixed-size copied
record with preparation status, readiness and sample rate.

## Numerical and runtime limits

Preparation accepts only 44,100, 48,000 and 96,000 Hz. Every parameter must be
finite. Tau support is `[1e-4, 60]` seconds; normal/soft gains and fast multiplier
are `[0,4]`; upper attenuation is `[0,1]`. These bounds are software choices,
not manufacturing tolerances. Independent gains are allowed rather than
silently deriving a percussion level from upper sustain compensation.

All state is fixed-size and value-owned. Processing performs bounded scalar
arithmetic and validation, with no allocation, I/O, logging, locking, callback,
or source lookup. Same-thread or stopped access is required. No concurrent
UI/publication protocol is implied by copied diagnostics.

The recurrence is a binary64 implementation of the exact first-order
exponential step, not exact real-number integration. q is bounded to `[0,1]`.
Decay below the smallest normal double (`numeric_limits<double>::min()`) is
explicitly flushed to zero, avoiding an indefinitely subnormal tail; recovery
then proceeds normally. Recovery near one is limited by floating-point
resolution. Neither behavior models measured residual leakage or cutoff.

## Checks actually executed

- Configured an isolated Release build with `BUILD_TESTING=OFF`, using CMake
  4.4.4 and GCC 14.2.0, then built `hammond_core` successfully under the
  repository's strict warning-as-error options. Build directory was temporary
  task tooling outside the repository; this was not a full integrated test run.
- Compiled a separate bounded smoke executable directly with C++20, `-O2`,
  `-Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror`.
  It linked only `src/Percussion.cpp` and used analytic closed-form decay and
  recovery values as the numerical oracle.
- All three supported rates and both decay modes passed one-second decay and
  0.1-second recovery comparisons with an absolute q tolerance of `8e-12`.
  That tolerance is an engineering check, not a hardware specification.
- The smoke also checked bounded/monotonic recovery, current first-sample gain,
  gain-control changes without q reset, atomic rejection of NaN profile/invalid
  rate/invalid enum/inconsistent detector, safe unprepared behavior, subnormal
  tail termination and recovery from zero.
- No permanent tests were added by this implementation assignment: the next
  independent percussion test assignment owns them. No callback-allocation
  instrumentation, sanitizers, other compiler/platform, actual audio render,
  plugin host or hardware acquisition was run for this module here.

## Next dependency-ready work

Integrate this module after contact-state routing; extend retained controls and
their versioned migration without serializing q. Preserve default disabled
percussion and legacy ideal audio. Independent engine tests must establish
upper-B eligibility, 1-foot masking, drawbar independence, overlap, same-time
release/repress, Cancel/reselect, mode changes, rejected-call atomicity, and
fixed/irregular block partition identity. Physical switch-transition and audio
fidelity claims remain pending the captures described on pp. 131/137/138.
