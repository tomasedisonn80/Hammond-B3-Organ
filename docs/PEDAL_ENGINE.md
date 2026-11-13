# Nominal pedal division in Engine

`Engine` renders all 25 pedals through the existing shared 91-source field. Each
physical pedal command closes or opens eight ideal binary contacts. Four buses
feed the two explicitly unmeasured mixtures adopted in
[PEDAL_INTEGRATION_CONTRACT.md](PEDAL_INTEGRATION_CONTRACT.md); their combined
contribution remains identifiable before the common expression and profile gain.
The two retained positions default to zero, so pedals become audible only after
an explicit registration edit.

The documentary basis is [atlas pp. 139-150](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=139)
for pedal routing and the separate pedal path, pp. 151-156 and 389-401 for controls
versus runtime history, and [p. 447](../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=447)
for a replaceable nominal console stage. The adopted matrix is a project
engineering fixture; it is not a recovered companion dataset, measured loading
network or calibrated 16-foot/8-foot response.

## Installed models and ownership

| Component | Identity or policy |
| --- | --- |
| Documentary routing | `atlas-derived-b3-c3-pedal-v1`; compiled 200 positions, 195 connected, five disconnected |
| Branch sum | `linear-pedal-bus-reference-v1`, with explicit dimensionless +1 weights at all 200 positions |
| Physical target | One checked `PedalId` in 1-25, separate from manual MIDI notes and source IDs |
| Contact policy | Eight simultaneous ideal closures per held pedal, independent of manual travel mode |
| Voice | `nominal-static-pedal-mixture-v1` |
| Retained gain law | `linear-pedal-position-v1`, integer position divided by eight |
| Polyphony | All 25 pedals alongside all 122 manual keys; no priority or count normalization |

Preparation constructs a candidate `PedalBusKernel` from the compiled routes and
`nominal_pedal_reference_weights()`. Every fallible source, manual-contact,
percussion and pedal preparation succeeds before Engine installs any candidate.
Success opens every pedal contact, clears every pedal target, mutes both pedal
controls and invalidates the last-rendered pedal record. Failure preserves the
previous Engine and its future output. No caller-owned route, weight or sample
buffer is retained.

Each rendered sample calls `TonewheelBank::process_frame` exactly once. The
already computed source array feeds the existing manuals/percussion and pedal
kernel. Repeated source numbers in different contacts remain independent
branches before their bus contributions sum. The five null connections still
have observable physical contact states. Neither contact commands nor diagnostic
queries evaluate a source or advance time.

The four bus values are ordered Brown, Red, Orange and Yellow. The fixed voice
computes `z0 = Brown/2 + Red/4 + Orange/8 + Yellow/8` and
`z1 = Brown/8 + Red/2 + Orange/4 + Yellow/8`, then
`P = (p0/8)*z0 + (p1/8)*z1`. Both mixture values remain observable while muted.
See [PEDAL_VOICE.md](PEDAL_VOICE.md) for exact operation order, bounds and its
independent numerical tests.

Engine preserves the previous manual/percussion summation order and then adds
`P` if it is nonzero. Skipping a zero-valued addition preserves the prior path's
signed-zero behavior as well as its ordinary arithmetic. The common expression
and profile output gain are applied once afterward. This is the dry scalar
connection for the future Great path; it introduces no limiter, envelope,
physical loading, additional oscillator or second expression law.

## Commands and musical independence

The appended event values are stable; all earlier values 0-9 remain unchanged.
Every new event requires `Event.manual == Manual::Lower` as a canonical unused
field convention. `Manual` itself still has only Upper and Lower. This does not
define a MIDI octave, MIDI channel or lower-manual key mapping for pedals.

| Event | Numeric type | Index | Value |
| --- | ---: | --- | --- |
| `PedalOn` | 10 | Pedal ID 1-25 | Finite integer 0-127; positive presses, zero releases |
| `PedalOff` | 11 | Pedal ID 1-25 | Exactly zero |
| `PedalDrawbar` | 12 | Mixture index 0-1 | Finite integer 0-8 |
| `PedalAllNotesOff` | 13 | Exactly zero | Exactly zero |

Positive velocity has no amplitude or contact-speed effect. Repeated presses and
releases are idempotent physical target edits, not counted ownership claims.
Pedal panic opens all 200 states immediately, including null positions, and
clears only pedal targets. It retains registrations and all source history.

Manual Cancel, bank reselection and manual `AllNotesOff` do not change pedal
targets, contacts or registration. Pedal activity cannot enter the upper ninth-
contact detector, recharge shared percussion readiness, select upper-B
eligibility, or alter sustained one-foot masking/attenuation. A muted held pedal
becomes audible at the current source phase when a pedal position increases.
Changing an output connection cannot change its later source or musical state.

For an already prepared engine, this stopped/same-thread flush registers and
presses pedal 13 without rendering a sample:

```cpp
const std::array<hammond::Event, 3> events{{
    {0, hammond::EventType::PedalDrawbar, hammond::Manual::Lower, 0, 8.0},
    {0, hammond::EventType::PedalDrawbar, hammond::Manual::Lower, 1, 3.0},
    {0, hammond::EventType::PedalOn, hammond::Manual::Lower, 13, 127.0},
}};
const auto result = engine.process(0, {}, events);
// Check result.status == hammond::Status::Ok before relying on the new state.
```

Engine preflights the complete call using the existing error order documented in
[ENGINE_API.md](ENGINE_API.md). A bad pedal payload, wrong canonical manual,
unsorted offset or invalid offset rejects every event and preserves output,
contacts, controls, diagnostics and time. Positive calls require offsets below
the frame count; flushes allow only zero. Equal offsets apply in supplied order
before that frame renders. Flushing changes no phase, contact travel, readiness
or frame clock.

## Current state and last-rendered state

All diagnostics are copied values for stopped or same-processing-thread access.
They are not a concurrent publication mechanism for a UI thread.

| Query | Meaning and failure behavior |
| --- | --- |
| `active_key_count()` | Existing manual-only count, maximum 122 |
| `active_pedal_count()` | Current held-pedal count, maximum 25; zero before preparation |
| `pedal_down(PedalId)` | Current physical target; false for an invalid ID or unprepared Engine |
| `pedal_drawbar_position(index, destination)` | Current retained position 0-8; invalid index or unprepared Engine preserves destination |
| `pedal_contact_closed(id, contact, destination)` | Current closure for contact 0-7; invalid/unprepared query preserves destination |
| `pedal_contacts_snapshot(destination)` | All 200 current states in pedal-major/contact-minor order; unprepared query preserves destination |
| `last_pedal_frame()` | Historical copied `PedalRenderDiagnostics`, independent of newer controls and contacts |

The historical record contains:

```cpp
struct PedalRenderDiagnostics {
    bool valid;
    std::uint64_t frame;
    double sample_rate;
    PedalDrawbarPositions positions;
    PedalBusFrame buses;
    PedalVoiceFrame voice; // two pre-control mixtures and the separate output P
};
```

`valid` is false after construction and fresh successful preparation. A positive
call updates the record using its last actual sample, even when the output span
is disconnected. `frame` is that sample's absolute frame identity: after a call
of `n > 0` frames beginning at `F`, the diagnostic is tagged `F+n-1` while the
next-sample Engine clock is `F+n`. The record carries the sample rate and pedal
positions used for that sample.

Zero-frame commands and control restores change current state without fabricating
a rendered sample. A rate change also leaves the record's old rate/frame tags
intact until a new sample renders. Rejected processing/preparation/rate/restore
operations preserve the record. Queries never recompute mixtures from newer
settings or call the source bank. These rules let consumers distinguish a past
audio observation from current settings without mislabeling history.

## Lifecycle, persistence and acceptance

Same-thread control restore validates the whole snapshot, including both pedal
positions, before replacement. It retains held pedals, all contacts, source
phases, percussion readiness, the clock and last-rendered diagnostics. The
[B3CONTROLS3 format](CONTROL_STATE_FORMAT.md) saves both positions but none of
those runtime histories. Older control documents explicitly migrate to muted
pedals. A saved control file is not an exact DSP continuation checkpoint.

Supported rate reconfiguration preserves pedal contacts/targets and controls
because this reference voice has no reactive or rate-dependent history. It
preserves the same source phases and existing manual/percussion histories through
their own admitted rate transition. Same-rate calls are exact no-ops; unsupported
rates reject without changing the installed rate or subsequent output.

[test_pedal_engine.cpp](../tests/test_pedal_engine.cpp) exercises this actual
Engine path: default/query semantics, eight-contact presses including a null,
an independently calculated source-one voice, actual sample/rate tags,
disconnected rendering, division/percussion independence, signed-zero-preserving
muted pedals, 122+25 occupancy, restore/rate history and whole-call rejection.
The baseline Engine, console and rate suites additionally guard the prior path.
The [assignment 16 evidence](development/2026-11-13-pedals/16-pedal-engine.md)
records the precise source snapshot and executed outcomes. Independent CSV
acceptance, enabled-pedal allocation instrumentation, renderer admission and full
combined regression remain separate gates owned by their respective workers.

This implementation is a nominal playable core division. Measured low-wheel
spectra, branch impedances, reactive pedal shaping, physical contact timing,
loaded expression, complete M3 acceptance and native host/device operation still
need their own models and retained evidence. A replacement must preserve shared
source identity and the four-bus/control boundaries, name its physical units and
variant, validate its complete candidate, and keep musical saved controls
separate from newly introduced electrical history.
