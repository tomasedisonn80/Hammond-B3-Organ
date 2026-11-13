# Capture audio inspection contract v1

**Contract frozen before implementation:** `capture-audio-v1`, 2026-11-13.
This is a project-authored companion to [capture metadata v1](CAPTURE_FORMAT.md)
under [the calibration scope](CALIBRATION_SCOPE.md). It specifies dependency-free,
offline Python 3.10+ inspection of actual digital samples. It does not establish
authentic acquisition, physical clock accuracy, calibration, rights or fidelity.
The implementation and its independently executed acceptance are later work;
this contract alone is not a passing test result.

## 1. Public API and compatibility

The new module is `tools/capture_audio.py`. Put `tools` on the Python import path.
The public signatures are:

```python
class AudioError(ValueError):
    code: str
    message: str
    details: dict

def inspect_audio(
    path: str | pathlib.Path, *, raw_format: str | None = None,
    sample_rate_hz: int | None = None, channel_count: int | None = None,
) -> dict: ...

def read_audio_window(
    path: str | pathlib.Path, start_frame: int, frame_count: int, *,
    raw_format: str | None = None, sample_rate_hz: int | None = None,
    channel_count: int | None = None,
) -> dict: ...

def main(argv: list[str] | None = None) -> int: ...
```

Both audio functions are read-only, perform complete admission and return only
JSON-compatible built-in values. No normalization, resampling, alignment, dither,
gain, channel selection, acquisition or network access occurs. Integer parameters
must have `type(value) is int`; Boolean, float and numeric-string substitutes are
rejected. The input is a nonempty string or `pathlib.Path`, not a stream or bytes
object. NUL and unpaired-surrogate path strings are invalid arguments.

`raw_format` is exactly `None` or `"raw_float32_le"`, preserving the existing v1
spelling. When it is the latter, both rate and channel count are mandatory and
describe the headerless stream; no defaults or filename inference are allowed.
When it is `None`, the file must contain a supported WAV header. Optional rate
and channel arguments are assertions against that header and never overrides;
a disagreement is `declaration_mismatch`. A supplied raw selector always selects
raw decoding, even when the first sample bytes happen to resemble a file signature.
Expected format is compared by the caller with the returned `format` token.

Keep `tools/analyze_wav.py`, its `analyze_wav` API, `AnalysisError`, existing
PCM16 statistics, crossing estimator, limits, report version and CLI semantics
unchanged. Keep `tools/validate_capture.py`, `CaptureError`, its metadata-only
default, opt-in byte checking, supported declaration enum and reports unchanged.
New audio support does not expand either old API implicitly, and an unsupported
audio decoder does not make an otherwise valid v1 metadata declaration invalid.

## 2. Supported digital representations

| Returned `format` | WAV format tag | Bits per scalar sample | Decoding to Python binary64 |
| --- | ---: | ---: | --- |
| `wav_pcm16` | 1 | 16 | Signed little-endian integer divided by `2**15` |
| `wav_pcm24` | 1 | 24 | Signed little-endian three-byte integer divided by `2**23` |
| `wav_pcm32` | 1 | 32 | Signed little-endian integer divided by `2**31` |
| `wav_float32` | 3 | 32 | IEEE binary32 little-endian, widened exactly |
| `wav_float64` | 3 | 64 | IEEE binary64 little-endian, retained |
| `raw_float32_le` | None | 32 | Interleaved headerless IEEE binary32, widened exactly |

Each frame contains one scalar sample for every channel in ascending file index.
PCM division is by the negative endpoint magnitude, so positive full scale is
`1 - 2**(-(bits-1))`, not `1`. Three-byte PCM must sign-extend bit 23. All specified
PCM fractions are exactly representable in binary64. Do not reinterpret a 24-bit
sample as an unsigned integer or as a left-justified 32-bit container.

This version explicitly **rejects WAVE_FORMAT_EXTENSIBLE (`0xfffe`)**, including
its PCM and float subformats. It does not discard valid-bit counts, channel masks
or GUIDs to guess a plain format. It also rejects RIFX, RF64, BW64, Wave64, FLAC,
compressed WAV, unsigned PCM8, other bit widths and unknown containers as
`unsupported_format`. `flac_pcm16` and `flac_pcm24` remain legal v1 declarations;
their audio inspection is unavailable here. There is no subprocess or decoder
fallback. A `.wav` or `.flac` suffix cannot override observed bytes.

The admitted ordinary-tag multichannel/24-bit/32-bit/64-bit layouts are this
project's explicit file-decoding subset. They do not promise Windows playback
support or supply physical speaker assignments. Channels are numbered storage
positions only; physical channel names, boundaries and polarity remain separate
capture or derivative declarations. Microsoft documents the additional valid-bit,
channel-mask and subformat meanings of
[WAVEFORMATEXTENSIBLE](https://learn.microsoft.com/en-us/windows/win32/api/mmreg/ns-mmreg-waveformatextensible).

## 3. RIFF structure and complete-file admission

All multibyte RIFF fields are little-endian. Require `RIFF` at offset 0 and
`WAVE` at offset 8, and require the unsigned 32-bit RIFF size plus 8 to equal
the actual file size exactly. Reject trailing bytes, partial headers and any
chunk extending outside that exact boundary. The chunk size excludes its
eight-byte header and the one required padding byte when its payload size is
odd. Padding must exist; its byte value is uninterpreted and is hashed.
These structural meanings follow Microsoft's
[RIFF description](https://learn.microsoft.com/en-us/windows/win32/xaudio2/resource-interchange-file-format--riff-).

Require exactly one top-level `fmt ` chunk before exactly one nonempty top-level
`data` chunk. Parse the entire chunk sequence, including chunks after `data`.
Reject duplicate or missing format/data chunks, `data` preceding `fmt `,
incomplete frame data, a partial final chunk header, or nonprogressing/overflowing
chunk bounds. Chunk positions and counters use bounded integer arithmetic.

For admitted tags, the `fmt ` payload is exactly 16 bytes, or exactly 18 bytes
with `cbSize == 0`; no implicit trailing format extension is accepted. Require:

- `block_align == channel_count * (bits_per_sample // 8)`;
- `byte_rate == sample_rate_hz * block_align`;
- `data_size_bytes > 0` and `data_size_bytes % block_align == 0`;
- `frame_count == data_size_bytes // block_align`.

The alignment meanings follow
[WAVEFORMATEX](https://learn.microsoft.com/en-us/windows/win32/api/mmreg/ns-mmreg-waveformatex);
the exact accepted sizes and stricter rejection rules are project policy.
For this subset a `fact` chunk is optional for either PCM or float; if present,
there may be only one, its payload must be exactly four bytes, and its unsigned
frame count must equal the count computed from `data`. It may precede or follow
`data`, but follows `fmt `. Thus absent `fact` does not make a float file fail,
and a contradictory `fact` cannot be ignored. This admission choice is not a
claim of conformance with every WAV writer or playback implementation.

Other top-level chunks are opaque bounded ancillary bytes, may occur on either
side of `data`, and contribute to byte identity. They are skipped without
allocating their payloads or interpreting metadata. Reject a top-level `slnt`
or a `LIST` whose four-byte list type is `wavl` as `unsupported_format` because
this decoder does not implement alternate audio-sequence semantics. An ordinary
`LIST` requires at least its four-byte list type; otherwise it is malformed.
No ancillary chunk supplies or overrides the accepted audio geometry.

For raw audio, `data_offset_bytes` is zero, `data_size_bytes` is the entire file,
and file length must be a nonzero multiple of `4 * channel_count`. The explicit
rate supplies the digital timebase only. Neither raw declarations nor WAV
headers establish the actual acquisition-clock frequency.

## 4. Resource and arithmetic bounds

These are deliberate offline admission limits, not physical instrument limits.
They preserve the per-file/rate/channel limits of capture v1 while adding bounded
inspection and window policies. Constants are exposed by the new module.

| Constant | Required value and meaning |
| --- | --- |
| `MAX_FILE_BYTES` | `268435456` (256 MiB), including every header and ancillary byte |
| `MAX_SAMPLE_RATE` | `768000`; accepted rate is an integer in `1..768000` Hz |
| `MAX_CHANNELS` | `16`; accepted count is an integer in `1..16` |
| `MAX_SECONDS` | `3600`; require `frame_count <= sample_rate_hz * 3600` |
| `MAX_CHUNKS` | `4096` top-level chunks, including `fmt `, `data` and ancillary chunks |
| `MAX_DECODED_SAMPLES` | `134217728` scalar channel samples; require `frame_count * channel_count` within this bound |
| `CHUNK_BYTES` | `65536`; no individual file read or canonical-digest update buffer exceeds this many bytes |
| `MAX_WINDOW_FRAMES` | `262144` frames in a returned sample window |
| `MAX_WINDOW_SAMPLES` | `1048576` scalar channel samples retained/returned across a window |
| `MAX_WINDOW_SECONDS` | `600`; require `window_frame_count <= sample_rate_hz * 600` |
| `MAX_SAMPLE_MAGNITUDE` | `1000000.0`; every decoded sample must satisfy `abs(x) <= 1e6` |

Zero-length audio is malformed; oversized input is `resource_limit`. Check file
size before reading its contents and announced geometry before decoding. The
sample-work ceiling follows the smallest admitted scalar storage width, two
bytes, and remains explicit if formats change later. Audio and window duration
checks use integer products, not rounded floating-point seconds.

Inspection is linear in bounded file bytes, chunk count and scalar samples, and
uses `O(channel_count + CHUNK_BYTES)` working storage. Header scanning may seek
over ancillary payloads; a complete bounded sequential content pass hashes all
bytes and decodes all data. At most two full-file passes are permitted, in
addition to bounded chunk-header reads. Do not materialize the file, a whole
audio stream, an unbounded chunk list or a per-sample digest buffer. Window
reading adds only its explicitly bounded per-channel lists. Header, statistics,
byte hash, decoded hash and returned window bind the same open descriptor.

There is no elapsed wall-clock timeout that changes a result according to CPU
load. Byte/sample/chunk/duration limits bound admitted work, not elapsed storage
latency; a caller can impose an outer operational deadline with a separate
not-run/aborted outcome. A comparison tool applies the intersection of its own
window bounds and this API's bounds, never silently crops a requested window.

Every float sample is checked with `math.isfinite` before arithmetic. NaN,
positive/negative infinity and values beyond the magnitude limit are rejected,
including outside a selected window. The `1e6` ceiling deliberately declines
extreme but representable floats; it is numerical safety policy, not an ADC
clipping or physical-gain threshold. Even the worst admitted unscaled sums are
bounded by `1.34217728e14` and squared sums by `1.34217728e20`, far below binary64
overflow. Check every reported float is finite before returning or serializing.

## 5. File identity and filesystem boundaries

A direct API call admits only a regular leaf file. Use no-follow leaf metadata
before opening; reject leaf symlinks, dangling symlinks, Windows reparse points,
directories, FIFOs, sockets and devices. Use `O_NOFOLLOW` where available and
`O_NONBLOCK` where available to avoid a raced FIFO blocking before descriptor
validation. Verify the opened descriptor is still a regular, non-reparse file
with the admitted size. Close descriptors on every success or rejection path.

Resolve the **parent** directory to a canonical absolute path, then retain the
leaf name. A direct call permits parent aliases such as macOS `/var`; it must
not resolve away an unsafe leaf before checking it. `input_path` reports this
canonical-parent/leaf path. Capture-root confinement is a different operation.

Record pre/post snapshots of the requested leaf, canonical leaf, canonical parent
identity and descriptor. Compare descriptor and pathname `(st_dev, st_ino)` when
both expose usable nonzero file identities; reject disagreement. At least one
usable nonzero file identity must exist, otherwise raise `identity_unavailable`.
For each API independently, compare type, identity, size, `st_mtime_ns` and
`st_ctime_ns` before/after. Do not compare path timestamps directly with descriptor
timestamps: those APIs differ on some platforms. Recheck both leaf paths and
canonical-parent identity after processing; a detected substitution, removal,
retargeted alias, size/time change or descriptor mutation is `file_changed`.
If one API omits usable identity, retain the other API's identity checks and the
same-API descriptor type/size/time checks; do not claim stronger race exclusion.

Direct calls allow a regular file with multiple hard links; this single-file API
does not decide whether different paths are independent evidence. Capture and
corpus checks retain their own hardlink and duplicate rules. In a capture archive,
the selected root itself and all artifact-relative directories must satisfy
capture v1's non-symlink/non-reparse confinement rules; only ancestors above the
selected root may be canonicalized. Calling the direct inspector on an absolute
path does not provide this confinement. The caller must preserve those checks
and compare the inspector's observed size/SHA with the declared and separately
checked identity.

These portable observations detect supported classes of mutation; they are not
an adversarial filesystem sandbox, filesystem lock, immutable snapshot or proof
against a writer that restores all observable metadata. Keep archives quiescent
for verification. Any failed call returns no partial inspection or sample list.

## 6. Exact identities and canonical decoded digest

`sha256` is lowercase SHA-256 of the **entire original file**, including headers,
ancillary chunks and padding, streamed under the bounds above. `size_bytes` is
the actual verified byte count, not the caller's declaration. No audio bytes are
rewritten to calculate this identity.

`decoded_digest_version` is exactly `"hammond-capture-decoded-v1"`.
`decoded_sha256` is SHA-256 of this precise byte sequence:

```python
b"HAMMOND-CAPTURE-DECODED-V1\x00"  # 27 bytes, including the final NUL
+ struct.pack("<IIQ", sample_rate_hz, channel_count, frame_count)
+ b"".join(
    struct.pack("<d", 0.0 if sample == 0.0 else sample)
    for frame in frames_in_file_order
    for sample in channels_in_ascending_file_index
)
```

The concatenation expresses bytes only; an implementation streams it and must
not execute the illustrated whole-stream join. The three header integers are
unsigned little-endian 32-bit rate, 32-bit channel count and 64-bit frame count,
without padding. Each normalized scalar is an eight-byte IEEE binary64 value
in little-endian order. The stream is **frame-major**, never channel-planar.
Both `-0.0` and `+0.0` become positive zero. Float32 widens exactly; float64 has
no rounding-to-float32 step. PCM uses the exact normalization in section 2.
No NaN encoding reaches the digest because nonfinite input has already failed.

The digest deliberately excludes container, integer/float storage width,
ancillary metadata, filename, calibration and evidence class. Exactly equal
normalized samples under different admitted wrappers/encodings therefore match
when rate, channel ordering and frame count also match. Quantization differences,
channel swaps, changed digital rate or changed geometry do not match. Equality
does not prove common physical acquisition; inequality does not prove independent
takes. A crop, gain, polarity inversion, resample or other near-duplicate needs
declared lineage and further corpus analysis. Digest equality is not a perceptual
or approximate-audio fingerprint.

## 7. Complete inspection report and statistics

The successful `inspect_audio` dictionary has exactly these top-level fields.
Fields shown together in a table row are nevertheless separate keys.

| Field | Value |
| --- | --- |
| `schema_version` | Integer `1` |
| `inspector_version` | `"capture-audio-v1"` |
| `status` | `"inspected"` |
| `input_path` | Absolute canonical-parent/leaf path from section 5 |
| `size_bytes`, `sha256` | Verified original byte identity |
| `decoded_digest_version`, `decoded_sha256` | Exact section 6 identity |
| `format` | One of the six admitted capture-format tokens |
| `container` | `"RIFF/WAVE"` or `"raw"` |
| `bits_per_sample` | Integer storage width, 16, 24, 32 or 64 |
| `sample_rate_hz`, `channel_count`, `frame_count` | Positive admitted integers |
| `duration_seconds` | `frame_count / sample_rate_hz`, finite binary64 |
| `data_offset_bytes`, `data_size_bytes` | Actual contiguous encoded-sample region |
| `chunk_count` | Number of top-level RIFF chunks, or zero for raw |
| `amplitude_unit` | `"digital_full_scale"`, dimensionless |
| `channels` | Ordered per-channel statistic objects below |
| `clipping` | Exact aggregate object below |
| `evidence_scope` | `"decoded-digital-audio-only"` |
| `authenticity`, `physical_clock`, `calibration`, `physical_fidelity` | Each `"not_established"` |

For one channel's `N == frame_count` normalized samples `x[i]`, each channel
object has exactly the following fields. Negative zero in returned numeric
values is normalized to positive zero.

| Field | Definition |
| --- | --- |
| `channel_index` | Zero-based file-channel index |
| `sample_count` | `N` |
| `peak` | `max(abs(x[i]))`; sample peak, not intersample/true peak |
| `rms` | `sqrt(sum(x[i]**2) / N)`, including DC |
| `dc` | `sum(x[i]) / N` |
| `nonzero_sample_count` | Count of `x[i] != 0.0`; signed zeros both count as zero |
| `positive_full_scale_sample_count` | PCM code `2**(bits-1)-1`, or float exactly `+1.0` |
| `negative_full_scale_sample_count` | PCM code `-2**(bits-1)`, or float exactly `-1.0` |
| `full_scale_sample_count` | Sum of the preceding two counts |
| `positive_over_full_scale_sample_count` | Float `x[i] > 1.0`; zero for integer PCM |
| `negative_over_full_scale_sample_count` | Float `x[i] < -1.0`; zero for integer PCM |
| `over_full_scale_sample_count` | Sum of the preceding two counts |

All counts are exact integers. For PCM, use exact integer sums and squared sums
before final scaling. For float, use bounded compensated accumulation for DC
and a stable RMS computation; simple uncompensated summation is not an adequate
reference. Avoid losing an entire subnormal-only signal by squaring every sample
to zero; scaled sum-of-squares or an equivalent stable calculation is required.
The numerical acceptance tolerance in section 11 permits final binary64 rounding,
not changes to the definitions. Statistics cover all frames, even when called
through `read_audio_window`.

The `clipping` object has exactly:

```json
{"full_scale_channel_samples":0,"over_full_scale_channel_samples":0,"confirmed_pre_encoding_clipping":null,"pre_encoding_status":"not_inferable_from_samples"}
```

The first two values are sums of the corresponding per-channel counts, not
fixed zeroes. Endpoint occurrence and floating values outside `[-1,1]` are
diagnostics, not automatic inspection failures. They cannot establish whether
an ADC, earlier processor or encoder clipped; prior clipping can remain after
attenuation, and an endpoint can be an intentional signal. Keep the null result.

## 8. Bounded sample-window result

`start_frame` and `frame_count` are exact integers. Require `start_frame >= 0`,
`frame_count > 0`, and `start_frame + frame_count <= inspection.frame_count`.
Frames are zero-based and the interval is half-open. Check the three window
limits in section 4. Empty, reversed, negative, noninteger, out-of-file and
oversized windows fail; there is no padding, truncation or wraparound.

The result has exactly these fields:

```python
{
    "schema_version": 1,
    "window_version": "capture-audio-window-v1",
    "inspection": complete_inspect_audio_report,
    "start_frame": start_frame,
    "frame_count": frame_count,
    "end_frame": start_frame + frame_count,
    "samples": [[...], ...],
}
```

`samples[channel_index][window_relative_frame]` is the exact normalized binary64
sample, with signed zeros canonicalized to `+0.0`. There are exactly
`inspection.channel_count` lists, each exactly `frame_count` long. All channels
share the same frame boundaries. The nested `inspection` is the same complete
report that `inspect_audio` would return for the unchanged path and options.

Window reading validates all headers and all samples and computes both complete
identities using the same descriptor while retaining only the requested window.
It is not permission to inspect selected good samples from an otherwise invalid
file. In particular, a NaN beyond the window fails the entire call. A caller
wanting a derived crop must retain a separate identified artifact and ancestry.

## 9. Capture and corpus composition

For every **raw** file in a recorded capture, the corpus caller uses the v1
`digital.format`, `digital.sample_rate_hz` and `digital.channel_count`, and compares
all three with this inspector's observed report. All raw artifacts must decode
and agree when claiming complete audio verification. For raw float, pass the
explicit rate/count and `raw_format="raw_float32_le"`; for WAV, pass header
assertions and compare the returned format. A planned capture has no files and
cannot become inspected audio evidence.

The v1 digital object describes the raw acquisition stream **only**. A derivative
may legitimately change encoding, rate or channel count. The corpus companion
therefore owns a per-capture `derived_audio` list whose descriptors are exactly
`{file_id, format, sample_rate_hz, channel_count}` and refer only to derived file
IDs. Use a derivative's own descriptor when inspecting it. Headerless derived
float is supported only with its explicitly declared derivative rate/count;
never borrow those values from the raw capture declaration. Self-described
derived WAV headers still must match their own descriptor for a declared check.

An unlisted derived artifact stays `not_inspected` with reason
`derived_audio_not_declared`; it cannot silently count toward complete audio
coverage. Support artifacts remain uninterpreted and are not audio duplicate
candidates merely because they resemble WAV bytes. The corpus companion owns
coverage, graph, grouping and split outcomes; this two-function API has no
manifest mutation, acquisition inference or capture-wide verdict.

## 10. Errors and deterministic command line

All expected argument, admission, decoding and I/O failures become `AudioError`,
a `ValueError` subclass. No ordinary file error leaks as a bare `OSError`.
`code` is one of the stable tokens below; `message` is nonblank explanatory text;
`details` is a finite JSON-compatible object, empty when no extra context exists.
`str(error)` includes its code and message. Diagnostics may include a field or
parameter name, expected/observed values, byte offset or absolute zero-based
frame/channel index, but never a partial successful report.

| `code` | Meaning |
| --- | --- |
| `invalid_argument` | Wrong API/CLI type, invalid raw selector, missing raw geometry or invalid option combination |
| `path_not_found` | Input leaf or required parent was absent before admission |
| `unsafe_file` | Initial/opened leaf is a symlink, reparse point or nonregular file |
| `identity_unavailable` | Neither path nor descriptor supplies usable nonzero identity |
| `io_error` | Other filesystem read/open/seek/stat failure |
| `file_changed` | Detected mutation or replacement/removal after initial admission |
| `unsupported_format` | Recognized unsupported container/tag/width or unrecognized non-WAV bytes without explicit raw selection |
| `malformed_audio` | Truncation, contradictory structure, missing/duplicate/disordered chunks, invalid format extension, partial/empty frames or `fact` mismatch |
| `resource_limit` | File, rate/channel, chunk, duration, scalar-work, or returned-window bound exceeded |
| `declaration_mismatch` | Optional WAV rate/count assertion disagrees with the header |
| `nonfinite_sample` | Any decoded float is NaN or infinity |
| `sample_out_of_range` | A finite decoded sample has magnitude greater than `1e6` |
| `window_out_of_range` | Integer window has nonpositive count, negative start, or extends outside admitted frame geometry |

Check argument shapes first, then file admission/size, container/chunks/geometry,
WAV assertions, window geometry/bounds, sample content, and final identities.
Within a valid data stream report the first bad scalar in frame-major order.
For an input violating multiple rules, this phase order defines the first error;
within a malformed chunk the earliest byte-position failure wins. A recognized
unsupported format tag is `unsupported_format` even if its extension is not an
admitted 16/18-byte format; do not misclassify every extensible file as malformed.
An observed mutation during any failure cleanup takes precedence as `file_changed`
when it invalidates the initial file snapshot; otherwise preserve the original
error. Cancellation such as `KeyboardInterrupt` is not swallowed or reported as
successful inspection.

Commands, from the repository root or with an absolute tool path:

```sh
python3 tools/capture_audio.py --input capture.wav
python3 tools/capture_audio.py --input stream.f32 --raw-format raw_float32_le --sample-rate-hz 48000 --channel-count 2
python3 tools/capture_audio.py --input capture.wav --start-frame 100 --frame-count 200
```

`--start-frame` and `--frame-count` must appear together. All integer CLI tokens
are at most 20 ASCII decimal digits with no sign, whitespace, exponent or decimal
point. Integer-value bounds still apply. The other optional arguments are
`--raw-format`, `--sample-rate-hz` and `--channel-count` as described above.
No output file is written. Success exits 0 and emits exactly one JSON object
and newline to stdout, with empty stderr. Audio admission/I/O rejection exits 1,
has empty stdout and emits exactly this shape to stderr:

```json
{"error":{"code":"unsupported_format","details":{},"message":"Unsupported audio format"},"inspector_version":"capture-audio-v1","status":"rejected"}
```

Its code/message/details contain the actual error. CLI syntax or option-shape
errors exit 2 with the same JSON error envelope and `invalid_argument`, no partial
stdout. `--help` is the sole human-readable stdout exception and exits 0.
Serialize with `sort_keys=True`, `separators=(",", ":")`, `ensure_ascii=True`,
`allow_nan=False`, UTF-8 and one final newline. Include no run timestamp, elapsed
time, random ID or mutable host inventory. Identical unchanged input path,
options and supported interpreter yield identical JSON bytes. Relocation changes
`input_path`; byte and decoded identities remain comparable. Machine consumers
use error codes, not platform-dependent prose. Cross-platform numeric results
obey section 11; the digest byte algorithm is platform-independent and exact.

## 11. Independent acceptance vectors and tolerances

These fixtures are explicit engineering oracles, not recorded instruments.
Independent tests must construct bytes directly with literals/`struct` or a
separate writer, and calculate expected values without calling the new decoder,
its header parser or its digest helper. Existing producer/analyzer output cannot
be the sole oracle. All hashes/counts/sample decoding are exact; no hash tolerance
or channel reordering is allowed. Peak is exact for these representable examples.
For ordinary nonzero RMS/DC compare an independent exact/Decimal oracle with
`abs(actual-expected) <= max(2e-12, 2e-12*abs(expected))`; zero examples must be
within `2e-12`. Signed-zero and subnormal requirements below are exact exceptions.
These bounds are arithmetic acceptance, not physical or audible tolerances.

### A. Cross-wrapper stereo identity, window ordering and known statistics

At 48000 Hz, the four frames are `(0, 1/4)`, `(1/2, -1/4)`,
`(-1/2, 3/4)`, `(0, -3/4)`. The complete minimal PCM16 WAV is 60 bytes:

```text
524946463400000057415645666d7420100000000100020080bb000000ee020004001000
646174611000000000000020004000e000c00060000000a0
```

Remove the newline before interpreting hexadecimal. Expected full-file SHA-256:
`5b56dc77fda85da22f9346b0d250c56bdf467a0d073bb07663db4f07702ed9ac`.
Expected decoded SHA-256:
`6b650fe3f66cfaec1d3ad75b2a91716b3a1868a7a2d3d1b0cc9ebb1b4f641d55`.
Data offset is 44, data size 16, chunk count 2, channel count 2 and frame count 4.

| Channel | Peak | RMS | DC | Nonzero count | Endpoint/over-range counts |
| --- | ---: | --- | ---: | ---: | ---: |
| 0 | `0.5` | `sqrt(1/8)` = approximately `0.3535533905932738` | 0 | 2 | All 0 |
| 1 | `0.75` | `sqrt(5/16)` = approximately `0.5590169943749475` | 0 | 4 | All 0 |

`read_audio_window(path, 1, 2)` returns `samples == [[0.5, -0.5], [-0.25, 0.75]]`
and the same complete inspection identities/statistics. Re-encode these exact
samples as PCM24, PCM32, WAV float32, WAV float64 and explicit raw float32: all
decoded hashes must equal the frozen value while original byte hashes differ.
Add an odd-length `JUNK` chunk with a real pad byte, or use a zero-extension
18-byte `fmt `: the decoded identity stays equal, and byte identity changes.

Changing only the rate to 44100 gives decoded SHA-256
`fe1772f596b6b7c4ff1a09704ebf59e791330e01f5a76143b364aea2b4551449`.
Swapping the two channels gives
`9d3372f8b3fcad782a640c25d7cff8c3696bed39b36feafc7b1f4b6de4a52df8`.
Flattening the same eight scalars into mono/eight frames gives
`1c109115de62460b2e716478bed19d044a6ccaebd18859b53083cb57792c3d81`.
Each differs from A for the stated semantic reason.

### B. Signed PCM edges, one-LSB values and odd data padding

For each width `b` in 16, 24, 32, let `q=2**(b-1)` and store five mono codes
`[-q, -1, 0, 1, q-1]` at 48000 Hz. Data bytes are respectively:

| Bits | Literal little-endian data hex | Expected DC | Approximate RMS |
| --- | --- | ---: | ---: |
| 16 | `0080ffff00000100ff7f` | `-6.103515625e-6` | `0.6324458818962644` |
| 24 | `000080ffffff000000010000ffff7f` | `-2.384185791015625e-8` | `0.6324554943363941` |
| 32 | `00000080ffffffff0000000001000000ffffff7f` | `-9.313225746154786e-11` | `0.6324555318864208` |

For every width, peak is 1, nonzero count is 4, each endpoint count is 1,
full-scale count is 2, over-range count is 0, `dc=-1/(5*q)` and
`rms=sqrt((2*q*q-2*q+3)/5)/q`. PCM24 data is 15 bytes and requires one pad byte
outside the data-size field. Omitting that pad fails even though all five frames
would otherwise decode. The normalized positive endpoint and LSB change with
width, so these three streams must not share a decoded digest.

### C. Floating endpoints, headroom and signed zero

The mono raw float32 bytes at 48000 Hz are:

```text
00000000000000800000803f000080bf0000a03f0000c0bf0000003f000080be
```

They encode `[+0, -0, 1, -1, 1.25, -1.5, 0.5, -0.25]`. Expected peak is 1.5,
RMS is exactly 0.875, DC is 0, nonzero count is 6, each endpoint count is 1,
and each over-range count is 1. The full-file SHA-256 is
`a537928ab210bdc28f972326557be866963cf75a254529433785b1c100814f46`;
the decoded digest is
`6125d66e14d8eba940491f56e21d047b507f10e75841605658432fc8c08cbb57`.
Changing negative zero to positive zero changes only the byte identity. Both
returned zero samples have a positive sign bit. The same samples in WAV float32
and WAV float64 share the decoded identity. Calling the raw API without either
required geometry value is `invalid_argument`; calling without the raw selector
is `unsupported_format`.

### D. Finite arithmetic and complete-stream validation

- Binary32 NaN bytes `0000c07f`, positive infinity `0000807f` and negative infinity
  `000080ff` each produce `nonfinite_sample`. Put them before, inside and after
  an otherwise valid requested window; every call must fail.
- `+1e6` and `-1e6` are admitted. Their two-sample mono DC is 0 and RMS/peak are
  exactly `1e6`. Binary32 `1000000.0625` and binary64
  `math.nextafter(1000000.0, math.inf)` produce `sample_out_of_range`.
- Four equal WAV float64 samples with bytes `0100000000000000` each represent
  the least positive binary64 subnormal. Peak, RMS and DC must all equal
  `float.fromhex("0x0.0000000000001p-1022")`, with nonzero count 4. A zero RMS
  fails this vector despite the generic absolute tolerance.
- Float64 mono `[1e6, 1e-9, -1e6, 1e-9]` exercises cancellation; an independent
  Decimal calculation of the exact stored binary64 samples supplies the DC/RMS
  oracle. This exposes naive accumulation while remaining well inside bounds.

### E. Structure, assertions, resource limits and identity

Independently exercise malformed RIFF size, truncated data, missing odd padding,
trailing bytes, incorrect block/byte rates, duplicate/missing/disordered chunks,
empty/partial frames, contradictory/duplicate `fact`, and nonzero/oversized format
extensions. Test explicit rejection of extensible PCM and float, FLAC signatures,
RIFX/RF64, PCM8 and compressed tags. A correct file with a wrong asserted rate or
channel count is `declaration_mismatch`, not rewritten geometry.

Test rate endpoints 1 and 768000 and channel endpoints 1 and 16; adjacent
out-of-range values reject. At rate 1, a 3600-frame file passes the duration
bound and 3601 frames fails. Window duration 600 passes and 601 fails when other
bounds permit. Test 262144/262145 window frames and scalar counts at/above
1048576 with geometry chosen so other limits do not mask the intended bound. With
16 channels, 65536 frames reach the scalar-window maximum and 65537 exceed it.
4094 empty `JUNK` chunks plus `fmt `/`data` reach the chunk bound; one more fails.
An actual sparse oversized regular file must reject before bulk reads. A normal
fixture crossing a 65536-byte boundary verifies frame alignment and that no
read is unbounded or exceeds `CHUNK_BYTES`.

Test valid first/last one-frame windows, zero/negative/fractional/Boolean/outside
windows, partial raw frames, and wrong raw geometry. Wrong but arithmetically
consistent raw geometry cannot be discovered from headerless bytes alone; the
report must faithfully retain that explicit declaration and its unestablished
physical meaning.

Use real leaf symlinks, dangling links, directories and FIFOs where supported;
Windows acceptance additionally uses a real reparse-point fixture. Verify direct
parent aliases succeed while capture-relative aliases reject at the companion
boundary. Controlled mutation/replacement hooks must exercise both descriptor
and path snapshots without timing-dependent races. Test unavailable identities,
preserved source bytes, descriptor cleanup, deterministic repeated CLI output,
JSON error exits and absence of partial stdout. Record platform-skipped cases as
unexecuted, not passing. Run existing analyzer/capture suites unchanged as the
compatibility gate when the implementation is integrated.

## Source basis and next evidence

Atlas pp. 355-360 require retained raw identities, digital/physical distinctions
and derivation history; pp. 367-372 require independent mathematical oracles and
reproducible reports; pp. 481-486 separate bounded engineering acceptance from
physical claims. The six current-session notes retain the fresh complete atlas
reading; [assignment 07](development/2026-11-13-calibration/07-audio-contract.md)
records this contract's authorship, consulted sources and actual work.
The Microsoft links above define container terminology, while subset selection,
resource limits, canonical digest, report schema and numerical tolerances are
explicit project decisions. No new physical data or external decoder is supplied.
Next implement this exact contract, then qualify it with separately authored
tests and retained actual execution evidence before calling it supported tooling.
