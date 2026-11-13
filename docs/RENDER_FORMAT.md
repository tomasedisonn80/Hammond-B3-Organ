# Offline rendering contract

The renderer is a command-line engineering client of the same C++ core. It writes
an unmeasured, normalized organ model into two identical PCM16 channels. This
executable is not an audio-device application or a VST3 plugin. Source synthesis,
contact motion and percussion have separate model identities.

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

| Option | Accepted values | Default / meaning |
| --- | --- | --- |
| `--sample-rate` | `44100`, `48000`, `96000` | `48000` Hz |
| `--block-size` | Integer `1..65536` | `64` frames |
| `--frames` | Positive integer, at most 600 seconds at the selected rate | Four seconds |
| `--seed` | Unsigned 64-bit decimal integer | `0` |
| `--drawbars` | Exactly nine digits `0..8` in physical order | `888000000`, upper selected bank |
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
controls, followed by four percussion controls: enable, harmonic, volume and decay.
Lower drawbars start muted; both manuals initially select bank B. This flush
advances no source, contact trajectory, readiness state or render clock.

Score events then run in their supplied order. A score event at frame 0 can
override a CLI percussion setting; initial flags are never reapplied during the
render. Volume and decay flags can therefore initialize a disabled percussion
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
`all_notes_off`, `bank_drawbar`, `select_bank`, `cancel`, `percussion` and
`key_position`.
The manual is `upper` or `lower`, except that percussion controls require `upper`.
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
shared readiness. Eligibility remains `enabled && upper route enabled && upper B`.
The physical detector uses upper contact index 8 independently of the audible
1-foot drawbar and its percussion mask.

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

Whitespace and full-line comments are allowed. Extra tokens, unknown names,
nonfinite values, invalid payloads, unsorted frames and events outside
`[0,total_frames)` are rejected before output creation. Limits are 16 MiB per
score, 262,144 events, 4,096 bytes per line, and 1,024 events at one frame. Same-frame
file order is stable. All new names and choices are case-sensitive.

The adapter partitions absolute events without moving an event to another sample.
An event at a block end belongs to the next block. If a block would exceed the
engine's event capacity, subdivide without changing times. The initial 13 controls
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

Every render summary now uses **render schema 2**. It retains all earlier fields
and adds these three mandatory fields:

| Field | Meaning |
| --- | --- |
| `render_schema_version` | Integer `2`; older unversioned summaries are a distinct retained format |
| `contact_model` | `ideal-contacts-v1` or `nominal-linear-travel-v1`, matching the chosen factory |
| `percussion_model` | `shared-readiness-v1`; identifies the installed algorithm even when percussion is disabled |

`key_position` is an extension of the schema-2 score grammar; it adds no summary
fields or CLI flags and changes no model identity. Existing schema-2 scores keep
their meanings. Historical schema-1 bundles retain their original eight-event
grammar and reject both `percussion` and `key_position`.

`model` remains `ideal-shared-sine-v1`, identifying the source generator. It does
not describe the entire organ. `evidence_status` remains `unmeasured`. Model
identities are separate from retained initial controls and time-varying score
content; retain the invocation, source/profile bytes, score and executable when
replaying a render. Strict consumers must explicitly support schema 2 instead of
assuming that its extra fields are absent. The independent evidence tools have
their own versioned producer/consumer contracts.

The default ideal/percussion-off path preserves the prior audio behavior, with
byte comparisons against the retained baseline executable on the tested toolchain.
Stdout JSON intentionally changes to identify its metadata contract and console
algorithms. Cross-compiler or cross-library byte identity is not promised.

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

Same-build replay, partition invariance and a valid WAV are software evidence.
They do not establish measured contact mechanics, key-click antialiasing, AO-28
circuit response, scanner/Leslie sound, physical fidelity or host qualification.
