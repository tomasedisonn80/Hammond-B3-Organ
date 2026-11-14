# Offline rendering contract

The renderer is a command-line engineering client of the same C++ core. It writes
an unmeasured, normalized organ model into two identical PCM16 channels. This
executable is not an audio-device application or a VST3 plugin. Source synthesis,
manual contact motion, percussion and nominal pedal routing/voicing have separate
model identities.

## Command line

The default preserves the earlier ideal-contact, percussion-off audio behavior:

```sh
hammond_render --profile build/nominal.b3p --output out/dry-organ.wav \
  --sample-rate 48000 --block-size 64 --frames 192000 --seed 0 \
  --drawbars 888000000 --note 60
```

Opt into the named synthetic contact/percussion checkpoint:

```sh
hammond_render --profile build/nominal.b3p --output out/nominal-percussion.wav \
  --sample-rate 48000 --block-size 64 --frames 192000 --seed 0 \
  --drawbars 888000000 --note 60 --contacts nominal --percussion third \
  --percussion-volume normal --percussion-decay fast --fail-on-clip
```

The output parent directory must already exist. `--profile` and `--output` are
required. All flags are unique; duplicates, missing values, unknown flags,
unsupported choices and positional arguments are rejected. `--help` is accepted
by itself. The argument-count bound is derived from the complete flag inventory,
including the valueless `--fail-on-clip` flag.

Numeric controls and option names use their exact ASCII grammar. On Windows,
the wide entry point preserves arguments as checked UTF-8 before validation;
full-width digits and other Unicode lookalikes remain invalid. Profile, score
and output paths use explicit UTF-8 filesystem conversion there, preserving
Unicode filenames. Arguments remain bounded to 4,096 UTF-8 bytes. The
[Windows repair record](reviews/PEDAL_WINDOWS_UNICODE.md) retains the observed
failure, regression cases and exact qualification scope.

| Option | Accepted values | Default / meaning |
| --- | --- | --- |
| `--sample-rate` | `44100`, `48000`, `96000` | `48000` Hz |
| `--block-size` | Integer `1..65536` | `64` frames |
| `--frames` | Positive integer, at most 600 seconds at the selected rate | Four seconds |
| `--seed` | Unsigned 64-bit decimal integer | `0` |
| `--drawbars` | Exactly nine digits `0..8` in physical order | `888000000`, upper selected bank |
| `--pedal-drawbars` | Exactly two digits `0..8`, Mixture 1 then Mixture 2 | `00`; both pedal mixtures muted |
| `--note` | Integer MIDI `36..96` | `60`; explicit use is incompatible with `--events` |
| `--events` | Existing bounded UTF-8/ASCII score file | Replaces the default note gesture |
| `--contacts` | `ideal`, `nominal` | `ideal`; selects the corresponding console factory |
| `--percussion` | `off`, `second`, `third` | `off`; enabled choices select the upper-B harmonic |
| `--percussion-volume` | `normal`, `soft` | `normal`; a retained initial setting even while disabled |
| `--percussion-decay` | `slow`, `fast` | `slow`; a retained initial setting even while disabled |
| `--fail-on-clip` | No value | Reject publication if any float sample clips |

Unsigned numeric flags reject signs, fractions, trailing garbage and overflow.
The compiled source profile is validated before use. `ideal` selects
`make_legacy_console_model()`; `nominal` selects `make_nominal_console_model()`.
These are fixed named factories; arbitrary custom contact/percussion parameter
files are not accepted by this CLI. Their actual parameters can be inspected with
[the model metadata exporter](MODEL_METADATA.md).

Without `--events`, generate NoteOn at frame 0 and NoteOff at three quarters of the
requested frame count. Before the first positive frame, flush nine upper drawbar
controls, followed by four percussion controls (enable, harmonic, volume and decay)
and two pedal mixture controls. Lower manual drawbars start muted; both manuals
initially select bank B. Pedal positions default to `00`, independent of either
manual's registration or selected bank. This flush
advances no source, contact trajectory, readiness state or render clock.

Score events then run in their supplied order. A score event at frame 0 can
override a CLI percussion or pedal setting; initial flags are never reapplied during
the render. Volume and decay flags can therefore initialize a disabled percussion
control that a later score event enables. Source phase and readiness are not reset
by a later control change. See [the console contract](CONSOLE_DYNAMICS.md) for
routing, timing and the explicit unmeasured assumptions.

## Absolute event fixture

`--events path` replaces the default note gesture. Lines have exactly five fields:

```text
# absolute_frame type manual index value
0 percussion upper 0 1
0 percussion upper 1 1
0 note_on upper 60 100
12000 note_on upper 64 100
24000 percussion upper 2 1
36000 note_off upper 60 0
48000 note_off upper 64 0
60000 percussion upper 3 1
60000 note_on upper 67 100
72000 all_notes_off upper 0 0
```

The score above requires a render longer than 72,000 frames. NoteOn remains a
physical-key target command, with duplicate positive NoteOn idempotent; this text
format is not a host note-ID ownership protocol.

Supported event names are `note_on`, `note_off`, `drawbar`, `expression`,
`all_notes_off`, `bank_drawbar`, `select_bank`, `select_preset`, `cancel`, `percussion`,
`key_position`, `pedal_on`, `pedal_off`, `pedal_drawbar` and
`pedal_all_notes_off`.
The manual is `upper` or `lower`; percussion controls require `upper`, and every
pedal command requires canonical `lower`. Pedal `lower` is an unused-field
admission convention, not a lower-manual key or an inferred MIDI octave. There
is no third `Manual` enum or `pedals` text token.
Existing event meanings remain in [ENGINE_API.md](ENGINE_API.md). Percussion
extends them as follows:

| Index | Retained percussion control | Value 0 | Value 1 |
| --- | --- | --- | --- |
| 0 | Enabled | Off | On |
| 1 | Harmonic | Second, source/contact index 3 | Third, source/contact index 4 |
| 2 | Volume | Normal | Soft |
| 3 | Decay | Slow | Fast |

A percussion event rejects lower-manual selection, any other index, and any value
that is not a finite integer 0 or 1. It changes retained controls, without resetting
shared readiness. Eligibility requires enabled percussion, an enabled upper route,
no fixed registration and retained upper bank B.
The physical detector uses upper contact index 8 independently of the audible
1-foot drawbar and its percussion mask.

`select_preset` requires either manual, unsigned index `0`, and a finite integral
value in `0..11`. Value `0` (including signed negative zero) means Cancel;
`1..9` select fixed C#, D, D#, E, F, F#, G, G#, A respectively; `10` selects
adjustable A# / bank A and `11` selects bank B. A fixed selection enables its
route and preserves both retained banks. Cancel disables that manual's route
while retaining its fixed choice, banks and held notes. Existing `select_bank`
and selector values 10/11 clear fixed mode and reconnect the requested bank,
even if that bank was already remembered. Drawbar edits keep their existing
remembered-bank targets. Equal-frame commands retain file order, and every
score is fully admitted before output creation. The fixed catalog identity,
example and current-schema evidence rules are in [PRESET_OFFLINE.md](PRESET_OFFLINE.md).

`key_position` uses either manual, MIDI note `36..96` as its index, and a finite
normalized target in `0..1`. With `--contacts nominal`, it commands the existing
linear-travel model toward that target, preserving current position and all nine
contact histories. It does not teleport the key, advance time, scale steady
amplitude or reset a source/percussion state. Repeating the same target leaves
motion unchanged. A subsequent positive `note_on` commands full target 1 even
after a partial hold; `note_off` and zero-velocity `note_on` command target 0.
With `--contacts ideal`, only endpoint targets 0 and 1 are accepted. An interior
target is rejected during score preflight, before any output file is created.

For example, render the following score with `--contacts nominal --frames 4000`:

```text
0 key_position upper 60 0.5
1000 note_on upper 60 100
2000 key_position upper 60 0.5
3000 note_off upper 60 0
```

The two partial holds can retain different connections because make and break
thresholds differ. Targets are direct physical-key input, not counted host notes
or saved controls. The named trajectory remains synthetic and unmeasured; this
score does not implement a calibrated continuous-position controller, fractional
event times, contact bounce or antialiasing.

### Pedal commands and registration

The four pedal commands extend the score grammar with the explicit domains from
[PEDAL_ENGINE.md](PEDAL_ENGINE.md):

| Command | Required manual field | Index | Value |
| --- | --- | --- | --- |
| `pedal_on` | `lower` | One-based pedal ID `1..25` | Finite integer velocity `0..127`; positive closes eight contacts, zero releases |
| `pedal_off` | `lower` | One-based pedal ID `1..25` | Exactly zero; opens eight contacts |
| `pedal_drawbar` | `lower` | Mixture index `0..1` | Finite integer position `0..8` |
| `pedal_all_notes_off` | `lower` | Exactly zero | Exactly zero; releases all pedals only |

Render a pedal-only score using `--drawbars 000000000 --pedal-drawbars 80`:

```text
0 pedal_on lower 1 100
12000 pedal_on lower 13 100
24000 cancel lower 0 0
36000 pedal_drawbar lower 1 4
48000 pedal_off lower 1 0
60000 pedal_all_notes_off lower 0 0
```

This score needs more than 60,000 frames. Lower Cancel leaves the pedals audible.
Pedal panic preserves manual notes, registrations, source phase and percussion
readiness; manual `all_notes_off` never releases pedals. Repeated positive
`pedal_on` commands are idempotent physical presses, and velocity has no amplitude
effect. External note ownership is a separate typed adapter, not this score format.

Both mixtures consume the same free-running 91-source frame already used by the
manuals. The four ordered buses are Brown, Red, Orange and Yellow. The adopted
unmeasured transfer uses numerator rows `[4,2,1,1]` and `[1,4,2,1]`, divided by
eight. Each retained position supplies linear gain `position/8`. These are
**Pedal Mixture 1/2**, without a calibrated 16-foot/8-foot claim. The scalar
expression and profile output gain act once after adding the separate pedal
contribution. No limiter, envelope or polyphony normalization is introduced.
See [the voice contract](PEDAL_VOICE.md) for its model identity and replacement
boundary.

Pedals always use eight simultaneous ideal closures, including when
`--contacts nominal` selects manual key travel. A held pedal remains physically
closed while its positions are zero; a later `pedal_drawbar` makes its current
source phase audible without a new press. All 25 pedals may sound together.

This CLI does not read or write control-snapshot files. The separate
[B3CONTROLS3 API](CONTROL_STATE_FORMAT.md) retains both pedal positions and
explicitly migrates versions 1/2 to muted pedals. The CLI's initial flags and
absolute score are its replay inputs; neither reconstructs a DSP checkpoint.

Whitespace and full-line comments are allowed. Extra tokens, unknown names,
nonfinite values, invalid payloads, unsorted frames and events outside
`[0,total_frames)` are rejected before output creation. Limits are 16 MiB per
score, 262,144 events, 4,096 bytes per line, and 1,024 events at one frame. Same-frame
file order is stable. All new names and choices are case-sensitive.

The adapter partitions absolute events without moving an event to another sample.
An event at a block end belongs to the next block. If a block would exceed the
engine's event capacity, subdivide without changing times. The initial 15 controls
are consumed in their separate zero-frame flush and do not consume a score frame's
1,024-event capacity.

`all_notes_off` immediately opens the selected manual's contacts and clears its
key targets; it does not reset sources or percussion readiness. In nominal contact
mode, ordinary NoteOff follows the declared release trajectory. Cancel only changes
routing and preserves physical contact/gesture state.

## Results and metadata version

Write explicit little-endian RIFF/WAVE PCM16 with two identical channels, valid
sizes and partial final blocks. Record actual frame/rate/block/seed/profile identity,
float peak, RMS and clipping counts. No polyphony-dependent or silent output
normalization is performed.

Every current render summary uses **render schema 3**, including renders with
muted or unplayed pedals. All previous metric fields remain present. Schema 2
introduced these console fields, which schema 3 retains:

| Field | Meaning |
| --- | --- |
| `render_schema_version` | Integer `3` for current output; older schema 2 and unversioned summaries are retained historical formats |
| `contact_model` | `ideal-contacts-v1` or `nominal-linear-travel-v1`, matching the chosen factory |
| `percussion_model` | `shared-readiness-v1`; identifies the installed algorithm even when percussion is disabled |

Schema 3 adds thirteen mandatory pedal fields:

| Field | Value / meaning |
| --- | --- |
| `pedal_routing_model` | `linear-pedal-bus-reference-v1`, from the compiled routing identity |
| `pedal_voice_model` | `nominal-static-pedal-mixture-v1`, from the compiled voice model |
| `pedal_gain_law` | `linear-pedal-position-v1`, position divided by eight |
| `pedal_contact_model` | `ideal-eight-contact-pedal-v1`, independent of manual contact mode |
| `pedal_map_id` | `atlas-derived-b3-c3-pedal-v1`, from compiled documentary data |
| `pedal_map_raw_sha256` | SHA-256 of the exact compiled map input bytes |
| `pedal_map_canonical_sha256` | SHA-256 of the complete canonical map JSON |
| `pedal_reference_a_sha256`, `pedal_reference_b_sha256` | Exact hashes of the two retained independent pedal CSV readings |
| `pedal_mixture_matrix` | String `4,2,1,1;1,4,2,1`; row-major numerators derived from the compiled matrix, Brown/Red/Orange/Yellow columns |
| `pedal_mixture_denominator` | Integer `8`, applied to every matrix numerator |
| `pedal_gain_denominator` | Integer `8`, applied to each retained position |
| `pedal_weight_policy` | `all-200-unit-positive-v1`, explicit normalized +1 weights even at disconnected positions |

Map/reference hashes identify documentary inputs; they do not attest to measured
branch conductance, source spectra, pedal shaping or a specimen. The rational
matrix and gain metadata identify the original engineering fixture, not hidden
calibration. The two denominator fields are JSON integers, not quoted strings.

Existing scores keep their meanings. Historical schema-2 bundles retain their
console grammar, including `percussion` and `key_position`; they reject the four
new pedal commands and `select_preset`, and have no pedal flag or pedal metadata.
Historical schema-1 bundles retain their original eight-event grammar and also
reject `select_preset`. The evidence producer emits
schema 3, while the independent verifier checks each retained format under its
own explicit contract. Fixed selection extends only the current schema-3 event
grammar; its parameter, invocation and metric fields are unchanged.

`model` remains `ideal-shared-sine-v1`, identifying the source generator. It does
not describe the entire organ. `evidence_status` remains `unmeasured`. Model
identities are separate from retained initial controls and time-varying score
content; retain the invocation, source/profile bytes, score and executable when
replaying a render. Strict consumers must explicitly support schema 3 instead of
assuming that its extra fields are absent. The independent evidence tools have
their own versioned producer/consumer contracts.

The default ideal/percussion-off/muted-pedal path preserves the prior audio
behavior. Legacy byte comparisons against the retained baseline executable have
their own executed scope in the session record.
Stdout JSON intentionally changes to identify its metadata contract and console
algorithms and pedal documentary/model identities. Cross-compiler or cross-library
byte identity is not promised.

## Publication and failure handling

Existing destinations, including symlinks, are rejected and never overwritten.
Input/output path collisions reject before rendering. Output is written to a
reserved temporary sibling directory and published with an atomic hard link;
therefore the output filesystem must support hard links. An intervening writer's
existing destination is preserved. Failure removes temporary work.

Clipping is counted per float mono frame before channel duplication. PCM conversion
rounds and saturates explicitly; `--fail-on-clip` reports `status: "clipped"`, returns
exit status 2, and publishes no WAV. Ordinary validation or I/O errors return
status 1. No file operation occurs inside `Engine::process`.

Help text and the final JSON summary are explicitly flushed to stdout, and a
failed write returns status 1 with a stderr diagnostic. WAV publication precedes
summary delivery: if that later summary write fails, the complete WAV remains
at its destination. The error does not roll back or delete a completed artifact.
Require both a successful process exit and a valid summary when collecting
successful render evidence; a WAV's existence alone does not establish success.

Same-build replay, partition invariance and a valid WAV are software evidence.
The focused pedal CLI suite checks actual WAV output, all 25 pedals at each
supported rate, all 81 initial position pairs versus equivalent scored controls,
muted-held source continuity, division independence, dense scheduling, clipping,
malformed early/late commands and path-preserving publication failures. Its
[assignment note](development/2026-11-13-pedals/20-pedal-renderer.md) records actual
commands and results; the broader publication gate remains the integrator's task.

These checks do not establish measured contact mechanics, key-click antialiasing, AO-28
circuit response, scanner/Leslie sound, physical fidelity or host qualification.
