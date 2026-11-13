# Engine and offline interface

This contract describes the nominal dry engine, its manual console extension and
its separate 25-pedal division. The default uses ideal manual contacts; explicit
preparation can select independent nominal manual travel. Pedal contacts remain
ideal, and their two retained controls drive the fixed nominal mixture in
[PEDAL_ENGINE.md](PEDAL_ENGINE.md). Source, console and pedal-voice models remain
unmeasured. Organ and cabinet electronics remain future stages.

## Engine facade

Use `hammond::Engine` with the agreed value types in `Types.h` and `Profile.h`:

```cpp
Status prepare(const RuntimeProfile&, const ProcessSpec&) noexcept;
Status prepare(const RuntimeProfile&, const ProcessSpec&, const ConsoleModel&) noexcept;
Status reconfigure_sample_rate(double sample_rate) noexcept;
double sample_rate() const noexcept;
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

The first failing condition determines the error, in this order:

| Check | Status |
| --- | --- |
| Engine is unprepared | `NotPrepared` |
| Frames exceed the prepared maximum | `BlockTooLarge` |
| Nonempty output is shorter than the requested frame count | `InvalidBuffer` |
| More than 1024 events | `TooManyEvents` |
| Adding frames would overflow the absolute frame clock | `TimelineOverflow` |
| An offset, ordering or payload is invalid | `InvalidEvent` |

Every event, including an inaudible pedal edit, must pass before the first event
is applied or the first output sample is written.

Preparation is a stopped-engine action. Validate all inputs before replacing a
working engine. Maximum block size must be 1..65536; event capacity is 1024. The
initial frame is a timeline origin, not a request to simulate earlier samples.
Initial controls are four muted retained banks, bank B selected and routes enabled
on both manuals, two muted pedal mixtures, no held keys or pedals, expression 1,
and percussion Off/Second/Normal/Slow with readiness 1. Preparation also builds a
candidate pedal kernel from the compiled routes and explicitly supplied nominal
unit weights before installing any state. Its last-rendered pedal record starts
invalid. The offline client explicitly supplies a registration. Physical key targets are retained per
manual/MIDI key: repeated note-ons do not multiply voices, and a release commands
normal travel to zero. An explicit `KeyPosition` can retain a partial target in
the nominal contact model. Held-key diagnostics mean target greater than zero;
they do not imply that any or all contacts are closed. [NoteOwnership](NOTE_OWNERSHIP.md) separately implements bounded
note-ID/channel ownership, and [InputProcessor](INPUT_PROCESSOR.md) commits it only
after Engine accepts the translated block. These typed adapters do not provide a
native host SDK, byte-level MIDI parser or device application.

`reconfigure_sample_rate()` is a stopped/same-thread transaction between processing
calls. It preserves source phases, current contact positions and hysteresis,
percussion readiness, controls, held keys, all pedal targets/contact states and
the frame clock while replacing rate-dependent coefficients. The stateless pedal
voice needs no rate change; its last-rendered record retains the rate of that
actual sample. Supported rates are 44100, 48000 and 96000 Hz, subject
to the owned profile's source-increment bounds. Same-rate requests are exact no-ops;
rejected changes preserve future output. The rate diagnostic is zero before
preparation. See [sample-rate lifecycle](SAMPLE_RATE_LIFECYCLE.md) for admission,
mixed-rate time accounting and the separate native-host/device requirements.

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
| BankDrawbar | bank*9 + drawbar,0..17 | integer0..8 | Edit an explicit retained bank without selecting it |
| SelectBank |0 | integer0=A or1=B | Select bank and enable manual routing |
| Cancel |0 |0 | Disable routing while preserving held keys and controls |
| Percussion |0..3 | integer0..1 | Upper only: enable, harmonic, volume, decay; see console contract |
| KeyPosition | MIDI 36..96 | finite 0..1 | Set physical target; nominal mode permits partial travel, ideal mode accepts only 0/1 |
| PedalOn | One-based pedal ID 1..25 | integer 0..127 | Positive velocity closes eight ideal contacts; zero releases; velocity does not scale level |
| PedalOff | One-based pedal ID 1..25 | 0 | Opens that pedal's eight contacts |
| PedalDrawbar | Mixture index 0..1 | integer 0..8 | Sets the independent retained pedal position |
| PedalAllNotesOff | 0 | 0 | Opens all pedal contacts and clears only held-pedal targets |

`KeyPosition` is appended as event value 9, preserving the earlier 0..8 values.
Target changes preserve the current contact position and hysteresis and consume
no elapsed time. Repeating the same target preserves its current trajectory.
A positive-velocity NoteOn commands full target 1 even after a positive partial
hold. NoteOff or velocity-zero NoteOn commands normal release to 0; AllNotesOff
retains its immediate panic behavior. Unsupported partial targets reject the
complete call in preflight. These direct key commands require coordinated note
authority when used alongside the ownership adapter and are not saved controls.

The pedal types append values 10, 11, 12 and 13 in the table's order. Existing
event values 0..9 and `Manual::Upper=0` / `Manual::Lower=1` are unchanged. Every
pedal event requires canonical `Manual::Lower`; `Upper` rejects. This convention
does not map pedals onto lower-manual MIDI keys or add a third manual. Repeated
pedal presses/releases are idempotent physical commands. All 25 may be held
together, independently of all 122 manual keys. Manual Cancel, bank selection
and manual panic leave pedals intact; pedal panic leaves both manuals, controls,
source phases and percussion history intact. A pedal never contributes to upper
percussion detection, readiness, sustain attenuation or one-foot masking.

Expression changes are initially steps. The implementation must not advertise
native VST3 ramp reconstruction until a separate curve contract is implemented
and tested. The implemented Cancel and retained-bank model is described in
[CONSOLE_EXTENSION.md](CONSOLE_EXTENSION.md). Independent contact trajectories and
one shared percussion state are specified in [CONSOLE_DYNAMICS.md](CONSOLE_DYNAMICS.md).
Physical multi-preset latches, measured pedal shaping and loaded expression remain later work.
Copied snapshots and `restore_controls()` require the same processing thread or
stopped processing; restore rejects unprepared or invalid state atomically and
never resets held keys/pedals, contact trajectories/states, percussion readiness,
source phase, time or the last-rendered pedal record. Control persistence is separate
from an exact DSP checkpoint; see [CONTROL_STATE_FORMAT.md](CONTROL_STATE_FORMAT.md).

## Source bank

The source-bank interface is:

```cpp
Status prepare(const RuntimeProfile&, double sample_rate, std::uint64_t seed) noexcept;
void process_frame(std::array<double, kToneSourceCount>& output) noexcept;
bool phase_turns(ToneId, double& destination) const noexcept;
bool prepared() const noexcept;
```

`TonewheelBank` owns exactly 91 phase accumulators and source samples. Preparation
copies source parameters and uses a specified deterministic integer PRNG to add
proposed seeded phase offsets to base phases. Document the algorithm. One
`process_frame` returns all source values at the current phase, then advances every
phase once. Never reseed or reset phases in note/drawbar/flush operations. All
branches referencing one tone ID consume that same frame's sample. Engine calls
the bank once per rendered sample and passes that array to pedal routing as well
as the existing manual/percussion path. Pedal diagnostics do not render another
source frame.

No source filters, hum, leakage, calibrated levels, gearing, physical shaft
coupling, scanner, valves, rotary processing or room responses are implied.

## Mix and diagnostics

For every closed contact, its drawbar routes to its explicit profile tone ID. Add
all branch gains algebraically, then apply the fixed profile output gain and the
expression surrogate. Do not deduplicate colliding branches, power-sum them, or
normalize by active-key count. Cached per-source coefficients may be recomputed
when controls or contact connectivity change. Upper-B percussion selects its
harmonic independently of retained drawbar gain, masks the sustained one-foot
branch without erasing that setting, and uses the physical ninth contact detector.
The console contract defines eligibility, sustain compensation and render-before-
advance timing. This bounds per-sample mixing without changing
coherence. No clipping/limiting is hidden in the floating-point core.

The separate pedal contribution `P` is built from four independently accumulated
buses and two named nominal mixtures. It joins the existing dry mix before the
one common expression/profile-gain multiplication. It belongs semantically to
the future lower/Great path, but is independent of the lower-manual routing gate.
The existing order of manual/percussion arithmetic is retained. When `P == 0`,
Engine skips its addition, preserving the legacy output's arithmetic and signed
zero. Pedals are never normalized by held count. See
[PEDAL_VOICE.md](PEDAL_VOICE.md) for the chosen dimensionless matrix, gain law and
finite bounds; these values do not represent a measured reactor transfer.

Expose copied diagnostics such as clock, active-key count, control values and
source phases only with documented stopped/same-thread access. Do not leak mutable
DSP references or claim a concurrent UI snapshot protocol.

`active_key_count()` continues to count manuals only, up to 122.
`active_pedal_count()` and `pedal_down(PedalId)` describe the separate current
pedal targets. Checked `pedal_drawbar_position`, `pedal_contact_closed` and
`pedal_contacts_snapshot` expose current controls and all 200 contact states,
including the five disconnected positions; invalid/unprepared queries preserve
their destinations. Contact index is 0..7 and snapshot order is pedal-major.

`last_pedal_frame()` instead returns a copied `PedalRenderDiagnostics` containing
`valid`, the absolute sample `frame`, its actual `sample_rate`, both `positions`,
four `buses`, and the `voice` mixtures/output. A successful positive call records
its final sample, including with disconnected output. Zero-frame events, control
restores and rate changes never recompute or relabel that historical record.
Rejected calls preserve it; fresh successful preparation invalidates it. The
record is not musical saved state and does not establish a concurrent reader API.

## Offline client

`hammond_render` loads a compiled profile before rendering. It accepts a finite,
bounded duration or frame count, supported sample rate, block size, seed, explicit
registration and optional absolute-frame event fixture. Render block boundaries
must not quantize event times. Write two identical dry PCM16 channels with an
explicit RIFF/WAVE header, count clipped samples, and report status/metrics. File
I/O is outside the engine call. Diagnostics and manifests name the nominal model
and supplied profile identity. The same events with different block partitions
must produce the declared equivalent audio on the same build.

## Numerical support boundary

Preparation rejects computed source increments below `2^-53` turns per sample
or at/above `0.5`. The lower bound prevents a positive increment from silently
rounding away across the binary64 phase range. It is a conservative support
bound, not a low-frequency accuracy guarantee. The supplied nominal profile
is unchanged. [NUMERICAL_BOUNDS.md](NUMERICAL_BOUNDS.md) retains the derivation,
atomic rejection tests and finite-window drift evidence.
