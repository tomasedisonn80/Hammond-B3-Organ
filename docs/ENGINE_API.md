# Initial engine and offline interface

This contract guides the next implementation wave. Update it to match integrated
code before claiming completion. Its scope is an ideal, unmeasured dry source/mix
engine; the organ and cabinet electronics remain future stages.

## Engine facade

Use `hammond::Engine` with the agreed value types in `Types.h` and `Profile.h`:

```cpp
Status prepare(const RuntimeProfile&, const ProcessSpec&) noexcept;
ProcessResult process(std::uint32_t frames,
                      std::span<float> mono_output,
                      std::span<const Event> events) noexcept;
std::uint64_t frame_clock() const noexcept;
bool prepared() const noexcept;
```

A positive call accepts an empty output span (disconnected output) or a span with
at least `frames` samples. A nonempty shorter span is invalid. A zero call can use
an empty span. An invalid call leaves all musical state, the clock and output
unchanged; the host adapter must decide its output-silencing policy. ProcessResult
reports zero consumed events on rejection and the full count on success. Preflight
checks the whole request before dispatch. There are no partially accepted calls.

Preparation is a stopped-engine action. Validate all inputs before replacing a
working engine. Maximum block size must be 1..65536; event capacity is1024. The
initial frame is a timeline origin, not a request to simulate earlier samples.
Initial controls are muted drawbars, no held keys and expression1. The offline
client explicitly supplies a registration. Physical key state is boolean per
manual/MIDI key: repeated note-ons do not multiply voices, and a release clears
that physical key. A future host adapter must define note-ID/channel ownership.

## Events

Order events by nondecreasing relative offset and preserve ties in supplied order.
Require `offset < frames` for positive calls; require zero for flushes. Validate
manual enum, event enum, finite value and payload ranges for every event.

| Type | index | value | Effect |
|---|---|---|---|
| NoteOn | MIDI36..96 | integer0..127 | Hold/release physical key; zero velocity releases; nonzero velocity never scales sustained level |
| NoteOff | MIDI36..96 |0 | Release physical key |
| Drawbar | physical position index0..8 | integer0..8 | Set retained manual control |
| Expression |0 |0..1 | Global normalized linear gain surrogate |
| AllNotesOff |0 |0 | Clear held keys on selected manual; preserve sources and controls |

Expression changes are initially steps. The implementation must not advertise
native VST3 ramp reconstruction until a separate curve contract is implemented
and tested. Preset Cancel, physical contact trajectories, pedal shaping and shared
percussion are later console work; no placeholder enum implies their completion.

## Source bank

The source-bank interface is:

```cpp
Status prepare(const RuntimeProfile&, double sample_rate, std::uint64_t seed) noexcept;
void process_frame(std::array<double, kToneSourceCount>& output) noexcept;
bool phase_turns(ToneId, double& destination) const noexcept;
bool prepared() const noexcept;
```

`TonewheelBank` owns exactly91 phase accumulators and source samples. Preparation
copies source parameters and uses a specified deterministic integer PRNG to add
proposed seeded phase offsets to base phases. Document the algorithm. One
`process_frame` returns all source values at the current phase, then advances every
phase once. Never reseed or reset phases in note/drawbar/flush operations. All
branches referencing one tone ID consume that same frame's sample.

No source filters, hum, leakage, calibrated levels, gearing, physical shaft
coupling, scanner, valves, rotary processing or room responses are implied.

## Mix and diagnostics

For every sounding key, each drawbar routes to its explicit profile tone ID. Add
all branch gains algebraically, then apply the fixed profile output gain and the
expression surrogate. Do not deduplicate colliding branches, power-sum them, or
normalize by active-key count. Cached per-source coefficients may be recomputed
only when controls/keys change. This bounds per-sample mixing without changing
coherence. No clipping/limiting is hidden in the floating-point core.

Expose copied diagnostics such as clock, active-key count, control values and
source phases only with documented stopped/same-thread access. Do not leak mutable
DSP references or claim a concurrent UI snapshot protocol.

## Offline client

`hammond_render` loads a compiled profile before rendering. It accepts a finite,
bounded duration or frame count, supported sample rate, block size, seed, explicit
registration and optional absolute-frame event fixture. Render block boundaries
must not quantize event times. Write two identical dry PCM16 channels with an
explicit RIFF/WAVE header, count clipped samples, and report status/metrics. File
I/O is outside the engine call. Diagnostics and manifests name the nominal model
and supplied profile identity. The same events with different block partitions
must produce the declared equivalent audio on the same build.
