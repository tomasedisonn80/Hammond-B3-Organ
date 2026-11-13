# Assignment 07 — fixed-size contact bank

Agent: `/root/w02_a07_contact_bank`; continuation wave 02, assignment 07.
Starting integrated baseline: `7c2ad2089f795b2147f5fc72cf10a4542d953a8c`.
This is new M3 engineering work. The preceding session's implementations and
reviews are preserved and are not counted as this assignment's work.

## Scope and source basis

Read the standing instructions, current status and next-step documents, the
continuation's complete review 02, the existing core type/source-bank contracts,
and atlas keyboard/contact chapters. Relevant requirements are atlas pp. 37–42,
109–120: a common key gesture, nine distinct contact states and thresholds,
separate make/break behavior, partial closure, interruption/reversal, and shared
source phase that does not restart on keys. The atlas distinguishes a named MIDI
trajectory from measured finger motion and requires later switching-bandwidth
and specimen-calibration evidence.

Changed only:

- [ContactBank.h](../../../include/hammond/ContactBank.h)
- [ContactBank.cpp](../../../src/ContactBank.cpp)
- This assigned note.

No engine, event type, control persistence, source profile, build file, shared
status document or PDF was changed. No commit or remote write was performed.

## Implemented contract

`ContactProfile` owns 122 separate `ContactKeyProfile` records, each with nine
on thresholds, nine off thresholds, and full-travel press/release seconds.
`ContactBank` owns all preparation coefficients and running state in fixed
arrays. There is no source, drawbar, preset, percussion, host-ownership or
GUI dependency. Preparation and inspection require a stopped engine or the
processing thread; this is not a concurrent snapshot protocol.

The two algorithm identities are:

| Mode / factory | Behavior |
| --- | --- |
| `Ideal` / `make_ideal_contact_profile()` / `ideal-contacts-v1` | Default legacy behavior. A Boolean key command immediately sets normalized position and all nine contacts to 0 or 1. Explicit fractional targets are rejected. |
| `LinearTravel` / `make_nominal_contact_profile()` / `nominal-linear-travel-v1` | Proposed normalized gesture. Commands set a target without moving position. Each positive-frame advancement moves toward it using the prepared full-travel rate, then applies independent contact hysteresis. |

The nominal factory proposes **0.008 s press / 0.012 s release**, with on
thresholds `[.12,.22,.32,.42,.52,.62,.72,.82,.92]` and off thresholds
`[.04,.14,.24,.34,.44,.54,.64,.74,.84]`. These are engineering defaults,
identical initially across keys but stored independently. They are neither
millimetres, recovered component specifications, measured B-3 timings nor
universal contact order. A caller may provide independent per-key values;
its custom parameters require their own retained identity even though the
algorithm-family identifier remains the same.

Validation requires a recognized mode, supported sample rate, finite durations
within `[0.0001, 1]` seconds, and independently finite
`0 <= off_threshold < on_threshold <= 1` for all 1,098 contacts. Unused travel
fields are validated in Ideal too. Invalid preparation preserves the complete
previous bank. Successful preparation copies the profile and starts all keys
open at position/target zero.

`set_key_target` is an idempotent physical-key command. The parent-approved
`set_position_target` accepts finite normalized `[0,1]` in LinearTravel, allowing
stable partial holds; it is an explicit extension, not inferred MIDI motion.
`key_target` means `target > 0`, distinct from contacts still closed during a
release. `position_target` exposes the exact partial target. Duplicate targets
do not restart a segment. A changed target preserves current position and
contact history, so a repress can reverse an incomplete return.

The current state belongs to the next sample to render. The integrator must
render that state and call `advance_frame()` **after** each positive sample,
including silent/disconnected output. Zero-frame flushes never call advancement.
Motion is evaluated from a fixed segment origin and elapsed-frame count instead
of repeatedly adding position increments. Segment length is bounded below
96,002 advances by the supported rate, duration and normalized-distance limits.
Each contact closes at `position >= on` and opens at `position <= off`; between
its thresholds it retains its history. `advance_frame()` reports connection
changes, not position-only movement, so it can invalidate a mixer cache exactly
when needed.

`panic_manual` immediately clears one manual's positions, targets and contacts
without touching any external source, percussion state or clock. Every checked
query rejects unprepared/invalid manual, MIDI-note or contact indices while
preserving its destination. Copied per-key snapshots expose position, target
and all nine states without dynamic storage.

## Verification actually executed

Compiled the new source independently with GCC 14.2.0 and the repository's
strict flags:

```sh
g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Wconversion \
  -Wsign-conversion -Wshadow -Werror -I include \
  -c src/ContactBank.cpp -o ../agent07-contact/ContactBank.o
```

A bounded scratch smoke program at `../agent07-contact/smoke.cpp` was compiled
with the same flags and linked directly with `src/ContactBank.cpp`; its binary
`../agent07-contact/smoke` exited 0. It checked:

- Unprepared and malformed query/command rejection with preserved destinations.
- Ideal immediate nine-contact closure, rejected fractional targets and isolated
  per-manual panic.
- A stable 0.5 partial hold with four contacts closed, explicit release hysteresis,
  and repress from position 0.25 instead of restarting at zero.
- Rejection of a final-key NaN profile, invalid sample rate and infinite target,
  followed by 1,000 advances identical to an untouched copied reference.
- First nominal contact closure after **43 / 47 / 93** advances at
  **44,100 / 48,000 / 96,000 Hz**, matching the independently calculated
  `ceil(.12 * Fs * .008)` values for these non-boundary cases.
- Full endpoint convergence for the maximum one-second duration at 96 kHz.
- Compile-time trivial-copyability of the bank and profile. `sizeof(ContactBank)`
  was **27,336 bytes** on this GCC/x86-64 build; other ABI sizes are not inferred.

These are scoped implementation checks, not the independent permanent test
suite or engine integration. The independent contact-test assignment owns those
regressions; the integrator owns combined builds, allocation instrumentation,
platform CI and publication. No sanitizer, native-host, callback deadline or
hardware result is claimed here.

## Remaining limits and integration handoff

Connections are binary and changes are quantized to processing sample
boundaries. There is no bounce, fractional-edge renderer, oversampling,
electrical conductance/load model or click-bandwidth qualification. In
particular, this work does not pass the atlas p. 120 high-rate-reference error
gate or establish a measured mechanical model. The trajectory ignores MIDI
velocity, preserving steady-level independence; future transient extensions
must keep that boundary explicit.

Integrate contacts before summing shared source branches. Preserve each source's
free-running phase and stable event order. Read current contacts for audio and
the percussion detector, render current readiness/source state, then advance
contacts and readiness once. Routing Cancel must neither clear contacts nor
pause travel. Ordinary control restoration must not serialize or restart these
running trajectories. Retain Ideal as the legacy-audio regression path.
