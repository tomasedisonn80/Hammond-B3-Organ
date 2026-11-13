# Offline digital audio inspection

`tools/capture_audio.py` implements the frozen
[`capture-audio-v1` contract](CAPTURE_AUDIO_CONTRACT.md) using only the Python
3.10+ standard library. It reads actual file bytes, validates the complete
audio stream, reports digital statistics, and can return a bounded sample
window. It does not acquire audio or establish authenticity, calibration,
physical clock accuracy, or instrument fidelity.

The [assignment 13 record](development/2026-11-13-calibration/13-audio-implementation.md)
identifies this implementation and its author checks. Independently authored
acceptance is a separate integration gate; the author checks are not an
independent qualification result. The existing `analyze_wav.py` and
`validate_capture.py` retain their existing APIs and meanings.

## Commands and Python API

From the repository root:

```sh
python3 tools/capture_audio.py --input capture.wav
python3 tools/capture_audio.py --input capture.wav --start-frame 100 --frame-count 200
python3 tools/capture_audio.py --input stream.f32 --raw-format raw_float32_le --sample-rate-hz 48000 --channel-count 2
```

With `tools` on the Python import path:

```python
from capture_audio import AudioError, inspect_audio, read_audio_window

inspection = inspect_audio("capture.wav", sample_rate_hz=48000, channel_count=2)
window = read_audio_window("capture.wav", 100, 200)
left_channel = window["samples"][0]
```

WAV rate/channel arguments assert observed header geometry. A disagreement is
`declaration_mismatch`; the caller's value never changes decoded geometry.
Headerless float32 requires all three explicit raw options. An explicit raw
selector chooses raw decoding even if its first bytes resemble a WAV signature.
Filename extensions do not select a decoder. Exact integer argument types are
required: Booleans, numeric strings and floats are not integer API arguments.

`read_audio_window` uses zero-based, half-open frame intervals. Its channel-planar
`samples[channel][relative_frame]` lists contain all channels in file order.
Its nested `inspection` covers the complete file and agrees with an ordinary
inspection of the unchanged input. A NaN outside the requested window rejects
the entire call. Empty, out-of-range or oversized windows are not padded or
cropped.

## Supported bytes and retained meaning

| Representation | Decoded scalar |
| --- | --- |
| Ordinary-tag PCM16, PCM24, PCM32 WAV | Signed little-endian code divided by `2**(bits-1)` |
| Ordinary-tag float32 WAV and explicit raw float32 | IEEE little-endian binary32 widened exactly to binary64 |
| Ordinary-tag float64 WAV | IEEE little-endian binary64 retained exactly |

The inspector validates RIFF size, all top-level chunk boundaries, required odd
padding, exactly one `fmt ` before one nonempty `data`, exact block/byte rates,
and optional `fact` consistency. Supported `fmt ` payloads are exactly 16 bytes,
or 18 bytes with zero `cbSize`. Unknown ancillary chunks are opaque bytes and are
included in the original-file hash. Their payloads are not allocated or parsed.
Ordinary `LIST` needs a four-byte type. Top-level `slnt` and `LIST/wavl` are
unsupported alternate sequence formats.

Extensible WAV, compressed WAV, PCM8, other widths, FLAC, RIFX, RF64, BW64,
Wave64 and unknown containers are rejected. In particular, legal capture-v1
FLAC metadata does not become invalid metadata merely because this decoder
cannot inspect its audio. Physical channel names and signal boundaries remain
capture/derivative metadata; storage channel indices do not supply those facts.

The report includes complete-file SHA-256 and a separate exact decoded digest.
The decoded digest starts with `HAMMOND-CAPTURE-DECODED-V1` plus NUL, then
little-endian `<IIQ` rate/channel/frame geometry, then frame-major `<d` samples.
Both signs of zero become positive zero. Equal normalized samples in different
admitted wrappers can share this digest. Rate changes, channel permutations,
geometry changes or quantization differences change it. Equality is not an
acquisition or perceptual-independence judgment.

Per-channel peak, RMS including DC, DC mean, nonzero counts, endpoint counts and
floating over-range counts cover every frame. PCM sums and squared sums use exact
integers until final scaling. Float DC uses Neumaier compensated accumulation;
RMS uses compensated, scaled sums of squares, preserving a signal made entirely
of the least positive binary64 subnormal. Returned zero values have positive
sign. Endpoint and over-range counts are diagnostics: prior clipping remains
`null` / `not_inferable_from_samples`.

## Bounds and processing

| Bound | Inclusive limit |
| --- | ---: |
| Complete file | 268,435,456 bytes |
| Digital sample rate | 1–768,000 Hz |
| Channels | 1–16 |
| Complete duration | 3,600 digital seconds |
| Top-level RIFF chunks | 4,096 |
| Decoded scalar samples | 134,217,728 |
| Individual read / canonical digest update buffer | 65,536 bytes |
| Returned window | 262,144 frames and 1,048,576 scalar samples |
| Returned window duration | 600 digital seconds |
| Finite sample magnitude | 1,000,000 |

Byte size is checked before contents are read. Header scanning seeks over opaque
payloads and retains only geometry, counters and the optional `fact` count. A
single sequential content pass hashes every original byte and decodes the entire
contiguous audio region. Audio reads contain whole frames; a separate bounded
buffer streams the normalized digest. Inspection storage is proportional to
channel count plus the fixed block size. Window calls additionally retain only
their admitted per-channel window lists. There is no elapsed-time-dependent
verdict, fallback decoder, subprocess or third-party runtime dependency.

## Identity, rejection and output

Each call binds headers, bytes, statistics, decoded identity and samples to one
open descriptor. It uses no-follow leaf observations, no-follow/nonblocking
opening where supported, and a regular-file descriptor check. Leaf symlinks,
reparse points and nonregular files are rejected. Descriptors are closed on
success, rejection, cancellation and `fdopen` failure.

The parent directory is canonicalized while the requested leaf name is retained.
Direct parent aliases and regular hard links are allowed. Before/after checks
independently compare the requested leaf, canonical leaf and descriptor type,
identity, size and nanosecond modification/change times. Path timestamps are not
compared directly with descriptor timestamps. A nonzero inode is usable with
its device scope, including a valid zero device number; neither path nor
descriptor supplying identity produces `identity_unavailable`.

Canonical parent checks compare type and usable identity and re-resolve the
requested parent alias. They do not compare directory size/timestamps, which
can change when unrelated siblings are created. This is the integrator's narrow
implementation interpretation of the frozen parent-identity rule. Detected
mutation during failure cleanup takes precedence as `file_changed`. These
portable observations are not a filesystem sandbox or immutable snapshot;
archives must remain quiescent. Capture-root confinement remains the caller's
separate responsibility under capture v1 and the corpus contract.

All expected rejections use `AudioError`, with stable `code`, explanatory
`message`, finite JSON-compatible `details`, and both code/message in `str(error)`.
Argument shapes are checked first, then file admission, container/geometry,
assertions, window geometry, complete sample content and final identities.
Exact-int rate/channel values outside the admitted interval are `resource_limit`;
wrong types or absent raw geometry are `invalid_argument`.

The CLI writes no file. Success returns exit 0 and exactly one compact, sorted,
ASCII-escaped JSON object plus LF on stdout, with empty stderr. Admission/I/O
rejection returns exit 1 with the contract's error envelope on stderr and empty
stdout. Syntax/option-shape errors use the same envelope, `invalid_argument` and
exit 2. `--help` is the human-readable stdout exception. Integer CLI tokens must
contain 1–20 ASCII decimal digits without a sign. Repeated unchanged inputs and
options produce identical JSON bytes on the same supported interpreter.

## Integration and remaining evidence

Corpus callers must retain their root-confinement rules, inspect every selected
raw artifact, compare returned format/rate/channel/size/hash with the relevant
declarations, and use each derivative's own descriptor. Successful decoding
does not populate missing physical observations or prove split independence.

Independent acceptance should qualify the exact coherent implementation with
the frozen contract's mathematical vectors, complete resource boundaries,
deterministic mutation hooks and unchanged legacy suites. Native Windows reparse
fixtures and platform-specific filesystem behavior require actual platform
execution. Synthetic bytes and passing software checks do not close an
acquisition, calibration, listening or physical-fidelity gate.
