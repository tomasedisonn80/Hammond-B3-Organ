# Offline rendering contract

The renderer is a command-line engineering client of the same C++ core. It is not
an audio-device standalone application or a VST3 plugin. Output is an unmeasured,
normalized dry model, duplicated into two PCM16 channels.

## Command line

The initial interface is:

```sh
hammond_render --profile build/nominal.b3p --output out/demo.wav \
  --sample-rate 48000 --block-size 64 --frames 192000 --seed 0 \
  --drawbars 888000000 --note 60
```

`--profile` and `--output` are required. The output parent directory must exist;
existing destinations are rejected and never overwritten. Publication uses an
atomic hard link from a temporary sibling, so the output filesystem must support
hard links. Failure removes temporary work and preserves any existing file.
 Defaults are48000 Hz,64 frames/block,
four seconds of frames at the selected rate, seed0, registration888000000 and
MIDI note60. Accept only the three supported rates. Numeric flags reject signs
for unsigned integers, fractions, trailing garbage and overflow. Frames must be
positive and no more than600 seconds at the selected rate; block size1..65536.
Output clipping is counted, reported and optionally an error through
`--fail-on-clip`. Do not silently normalize output.

Without `--events`, generate note-on at frame0 and note-off at3/4 of the total
frame count. The initial nine upper drawbar events precede fixture events at
frame0. Lower drawbars start muted. `--note` is incompatible with `--events` when
explicitly supplied. Registration is exactly nine digits0..8 in physical order.
No processing-time file operations are inside `Engine::process`.

## Absolute event fixture

`--events path` replaces the default note gesture. UTF-8/ASCII lines use:

```text
# absolute_frame type manual index value
0 note_on upper 60 100
12000 expression upper 0 0.5
24000 note_off upper 60 0
24000 note_on lower 48 127
36000 all_notes_off lower 0 0
```

Supported types are `note_on`, `note_off`, `drawbar`, `expression`,
`all_notes_off`; manual is `upper` or `lower`. The meaning/range of index/value
is defined in ENGINE_API.md. Whitespace and full-line comments are allowed;
extra tokens, unknown names, nonfinite numbers, unsorted frames, oversized files
and events outside `[0,total_frames)` are rejected before output creation.
Same-frame file order is stable. New controls need documented version-compatible
extensions and tests.

The adapter partitions absolute events without moving an event to another sample.
An event at a block end belongs to the next block. If a block would exceed the
engine's event capacity, subdivide without changing times; more than1024 actual
fixture events at one frame is a preflight error. Initial registration controls
may be applied in a separate zero-frame flush before accepted score events.

## Results

Write explicit little-endian RIFF/WAVE PCM16 (two identical channels), including
valid sizes and partial final blocks. Record actual frame/rate/block/seed/profile
identity, float peak, RMS and clipped-frame count, and identify the model as
unmeasured. Use a temporary output and publish only after successful rendering;
reject input/output path collisions. A companion Python fixture wrapper hashes
profile, event, executable and output bytes and retains JSON run metadata.

Bitwise same-build replay and partition independence are engineering checks.
Cross-library/compiler floating-point identity, hardware calibration, analog
harmonics, scanner/Leslie sound and host validation are not established by a WAV.
