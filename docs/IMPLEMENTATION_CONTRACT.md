# Initial implementation contract (M0-M2 engineering baseline)

This is new implementation design derived from atlas pp. 5, 61-66, 97-108,
385-390 and 445-454. The companion header and machine-readable data referenced
by the PDF were not present in the initial repository. These files are original
reconstructions with their own versions, not recovered companion assets.

## Selected scope

Build a dependency-free C++20, framework-independent dry organ engine and offline
WAV renderer. Compile and validate authoring data outside processing. Implement
91 shared continuous sine sources, explicit manual routes, ideal key gating,
retained drawbar controls and reproducible sample-offset events. The initial
profile is named `nominal-unmeasured-v1` and uses 12-TET frequencies with A4=440 Hz.
It models engineering behavior in normalized amplitude units, not pickup or G-G
voltage. Measured tuning, gears, phase relationships, pickup harmonics, loading,
contact timing, scanner, AO-28, Leslie and host/UI product gates remain open.

## Module ownership

- `include/hammond/Types.h`: fixed capacities, domain identifiers and event records.
- `include/hammond/Profile.h` / `src/Profile.cpp`: fixed-size runtime data,
  validation and stopped-engine profile loading. No parsing in processing.
- `include/hammond/TonewheelBank.h` / `src/TonewheelBank.cpp`: exactly 91 sources;
  deterministic initial phases; no note-triggered resets; source sample advances
  exactly once per rendered frame regardless of manual/polyphony/output connection.
- `include/hammond/Engine.h` / `src/Engine.cpp`: console state, stable event dispatch,
  dry mixing, clock ownership, bounded error handling and diagnostics.
- `tools/render.cpp`: file and command-line operations; stereo PCM16 WAV with
  identical dry channels; offline absolute events adapted to half-open blocks.
- `tools/compile_profile.py`: strict authoring validation, derived source/map
  generation and deterministic C++-readable compiled profile outside rendering.
- `tools/render_fixture.py`: reproducible fixture runner and hash/metric manifest.

## Data rules

Authoring JSON carries schema/model versions, source PDF hash and page locators,
evidence class, explicit unknowns, and named model/effect boundaries. Use only
`documented`, `measured`, `derived`, `proposed`, or `unknown` as evidence classes.
No measured record without an acquisition reference; no non-finite values, duplicate
IDs, missing required inputs, silent clamping, or unbounded record counts. A compiled
profile is copied into fixed-size engine-owned storage at prepare time; borrowed
mutable authoring memory never survives preparation. File paths and dynamic storage
belong outside the callback. Profile replacement requires a stopped engine in this
first implementation; hot-swap publication is explicitly deferred.

Manual mapping is a reconstruction of the algorithm on PDF pp. 98-99; test six
printed rows on p. 102 independently and all 549 generated ranges. The later
[factory comparison](FACTORY_REFERENCE.md) also matches every assignment to two
independently frozen Table III transcriptions. Original profile provenance remains
unchanged; gearing and physical calibration are separate gates. Tone IDs 1-91,
array indices 0-90, manual keys 1-61 and MIDI 36-96 are
separate domains. Store the explicit generated map rather than multiplying oscillator
frequency by nominal harmonics. Pedal maps have their own disconnected sentinel.

## Timing and failure rules

The render clock is unsigned 64-bit and independent of transport/wall time.
Positive calls own [start, start+frames); local event offsets satisfy offset<frames.
A zero-frame call accepts offset-zero controls once and advances no oscillator,
clock or dynamic state. Caller must not resubmit already consumed events. Preserve
supplied same-offset order. Reject unsorted/out-of-range/over-capacity events,
invalid values and clock overflow before mutating musical state. Null output on
a positive call still advances state. Prepare supports 44100, 48000 and 96000 Hz
and a declared maximum block size; reject larger calls without dynamic allocation.
Explicit reset is separate from note release, preset cancel and transport changes.

## Validation ownership

Independent tests compare source pitch, manual boundary vectors, coherent foldback,
phase continuity through silence, sample-accurate events, zero-frame flushes,
invalid-call atomicity, deterministic seed behavior, block partitions, supported
rates and callback allocations. Offline PCM clipping is counted and reported;
no silent normalization changes drawbar/polyphony relationships. Sanitizer, source
compiler, CLI and schema tests have their own results and limitations.
