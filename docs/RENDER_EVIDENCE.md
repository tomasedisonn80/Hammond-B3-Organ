# Reproducible synthetic render evidence

`tools/render_fixture.py` is a Python 3.10+ standard-library client of the existing
profile compiler and C++ offline renderer. Its evidence scope is always
`synthetic_engineering`. A WAV, matching hashes, a successful replay, and a clean
working tree establish no specimen calibration, acoustic match, host validation,
or real-time deadline guarantee. See [RENDER_FORMAT.md](RENDER_FORMAT.md) and
[the atlas review](research/ATLAS_REVIEW.md) for the physical evidence boundary.

## Run a fixture

Build `hammond_render` first, then choose a result directory that does not exist:

```sh
python3 tools/render_fixture.py \
  --renderer build/hammond_render \
  --profile-json data/profiles/nominal-unmeasured-v1.json \
  --output-dir out/evidence-example \
  --frames 48000 --sample-rate 48000 --block-size 64 --seed 7 \
  --drawbars 008000000 --note 60
```

The parent directory must already exist. Existing files, directories and symlinks
at `--output-dir` are rejected without modification. The wrapper never chooses a
renderer from `PATH`; `--renderer` is required. `--profile-json` defaults to the
repository's nominal unmeasured profile. Profile and score copies preserve exact
input bytes, including whitespace and line endings. Compilation uses the existing
importable `compile_profile.compile_profile()` on validated authoring data.

| Option | Default and accepted range |
| --- | --- |
| `--frames` | Four seconds at the selected sample rate; positive, at most 600 seconds |
| `--sample-rate` | 48000; one of 44100, 48000, 96000 Hz |
| `--block-size` | 64; integer 1..65536 |
| `--seed` | 0; unsigned 64-bit decimal integer |
| `--drawbars` | `888000000`; exactly nine ASCII digits 0..8 |
| `--note` | 60; integer MIDI note 36..96 |
| `--events` | Optional absolute-event file; incompatible with an explicit `--note` |
| `--contacts` | `ideal`; one of `ideal`, `nominal` |
| `--percussion` | `off`; one of `off`, `second`, `third` |
| `--percussion-volume` | `normal`; one of `normal`, `soft` |
| `--percussion-decay` | `slow`; one of `slow`, `fast` |
| `--timeout-seconds` | 120; integer 1..600, renderer wall-time bound |

Unsigned numeric syntax and event grammar follow the C++ CLI; duplicate options,
unknown options and abbreviated options are rejected. Event validation includes
`bank_drawbar`, `select_bank`, `cancel`, `percussion` and `key_position` from the
console extension.
A `percussion` event requires manual `upper`, unsigned index 0..3, and a finite
integer value exactly 0 or 1. Indices select enable, harmonic, volume and decay;
their 0/1 meanings are Off/On, Second/Third, Normal/Soft and Slow/Fast respectively.
Finite decimal spellings such as `1.0` or `1e0` follow the renderer's numeric
grammar and are accepted as the integer value 1; nonintegral parsed values are rejected.
`key_position` requires either manual, MIDI index 36..96 and a finite target in
0..1. Nominal contacts accept interior targets; ideal contacts accept only 0 or 1.
The wrapper validates this mode-dependent rule before creating the evidence
directory or launching the renderer. The public helper
`validate_events(raw, frames, contacts="ideal")` keeps the previous two-argument
call valid; pass `contacts="nominal"` when preflighting a nominal partial-key score.
Targets preserve the chosen model's contact history and do not represent saved
controls or measured position calibration; see [the score contract](RENDER_FORMAT.md).
The wrapper always passes `--fail-on-clip`, never normalizes audio, and invokes an argument list
without a shell. An empty event file is a valid silence fixture. The default note
gesture is the renderer's frame-zero note-on and floor(3*frames/4) note-off.

The public `run_fixture()` API accepts the same keyword-only controls, named
`contacts`, `percussion`, `percussion_volume` and `percussion_decay`, with the
defaults in the table. Values must be strings from the exact case-sensitive choices.
The defaults preserve ideal-contact, percussion-off audio, while the retained
metadata identifies the installed algorithms. To opt into the named nominal
contact model and third-harmonic percussion, add:

```sh
  --contacts nominal --percussion third --percussion-volume soft --percussion-decay fast
```

These are initial controls. A score's frame-zero events follow the initialization
flush and can override them. With `--percussion off`, the retained initial harmonic
is Second; volume and decay still initialize their controls. The manifest records
the initial choices and exact score bytes, without pretending they describe every
later control state or the current percussion readiness.

### Fixed renderer invocation

Schema 2 retains this exact argument order, with every console choice explicit
even when its default is selected:

```text
RENDERER --profile PROFILE_COPY --output WAV --frames FRAMES
  --sample-rate RATE --block-size BLOCK --seed SEED --drawbars DRAWBARS
  --contacts CONTACTS --percussion PERCUSSION
  --percussion-volume VOLUME --percussion-decay DECAY --fail-on-clip
  (--events EVENTS_COPY | --note NOTE)
```

This is a schematic argument list, not shell syntax. `RENDERER` and all file paths
are absolute. The last two arguments are exactly `--events` and the copied score
path, or `--note` and the resolved default/explicit note. Numeric arguments use
canonical unsigned decimal strings. Profile, WAV and event paths refer to
`profile.b3p`, `render.wav` and `events.txt` inside the new evidence directory.

## Result files and failure semantics

A completed successful directory contains `manifest.json`, `profile.json`,
`profile.b3p`, `render.wav`, `renderer.stdout.txt`, and `renderer.stderr.txt`.
`events.txt` exists only for an explicit event file. Logs retain the renderer's
actual bytes, and `renderer_metrics` is parsed from the retained stdout JSON.
Float peak/RMS are never replaced with statistics derived from the WAV.

Preflight errors exit nonzero without creating a directory. After exclusive
creation, the initial manifest has `status: "incomplete"`; an interruption must
never be interpreted as success. Runtime errors produce `status: "failed"`, an
error stage/message and a nonzero CLI exit. Successful runs alone use
`status: "succeeded"` and CLI exit zero. Disk or finalization failures can leave
an incomplete manifest; absence of a final successful manifest is a failed gate.

A failure retains available inputs, logs, actual JSON metrics and diagnostic
output. A clipping failure preserves the renderer's `status: "clipped"` JSON and
exit status 2; it has no successful WAV record. An output file may exist after a
later verification failure, but its mere existence is not successful evidence.
A launch failure has null return code and null unavailable metrics/log records.
Consumers must require the manifest success state and every verification below.

## Manifest schema version 2

The `key_position` command extends the version-2 score grammar without changing
the manifest's 13 parameter fields, the renderer's 18 metric fields, the 26-token
invocation, or any model identity. Retained score bytes and `parameters.contacts`
fully identify its selected model. Earlier version-2 bundles remain valid, while
historical version-1 bundles retain their original grammar and reject this command.

JSON uses UTF-8, sorted keys, two-space indentation and a final LF. It contains
no NaN/Infinity values. All hashes are lowercase hexadecimal SHA-256 of raw file
bytes; `size_bytes` is an integer. Artifact `path` fields are the fixed relative
filenames above, never file URLs or paths that escape the result directory.

| Field | Meaning |
| --- | --- |
| `schema_version` | Integer 2 |
| `evidence_scope` | Literal `synthetic_engineering` |
| `status` | `incomplete`, `failed` or `succeeded` |
| `started_at_utc`, `finished_at_utc` | ISO 8601 UTC strings ending `Z`; finish is null until finalization |
| `parameters` | Actual frames, sample rate, block size, seed, drawbars, note, event mode, event count, the four initial console choices and `fail_on_clip: true` |
| `inputs.profile_json` | Artifact path/hash/size, absolute original `source_path`, and `canonical_authoring_sha256` |
| `inputs.events` | Optional artifact path/hash/size and absolute source path; null for the default note gesture |
| `compiled_profile` | `profile.b3p` raw-byte path/hash/size |
| `renderer` | Absolute executable path, size, `sha256_before`, `sha256_after`; after is null if unavailable |
| `tools` | Wrapper/compiler absolute source paths, hashes and sizes sampled for this run |
| `git` | Source repository path, sampled UTC time, HEAD, dirty flag, and `binary_association: "not_established"`; unavailable values are null with an error |
| `environment` | Python version/implementation, platform, machine and byte order |
| `limits` | Renderer timeout, maximum bytes per log/metrics JSON/event/executable and expected WAV bytes |
| `invocation` | Exact absolute `argv`, return code, timeout/capture flags, capture errors and stdout/stderr artifact records |
| `renderer_metrics` | Actual parsed renderer JSON object, or null; a parse failure adds `metrics_parse_error` |
| `wav` | Verified WAV artifact and decoded statistics, or null when unavailable/unverified |
| `metric_comparison` | Float-versus-PCM differences, domains, numerical tolerance and quantization bound; null until evaluated |
| `integrity_verified` | Whether executable, original inputs, copied inputs, compiled profile and tool bytes passed post-run checks |
| `error` | Null on success, otherwise `{stage, message}` |

The exact `parameters` keys are `frames`, `sample_rate`, `block_size`, `seed`,
`drawbars`, `note`, `event_mode`, `event_count`, `contacts`, `percussion`,
`percussion_volume`, `percussion_decay` and `fail_on_clip`. Console choices use the
exact strings in the option table. `parameters.note` and `event_count` are null
when inapplicable; the latter counts only explicit score events, excluding the
thirteen initialization controls (nine drawbars followed by four percussion controls).
`event_mode` is `default_note` or `file`. `invocation` capture flags are
`timed_out`, `stdout_truncated`, `stderr_truncated`, `capture_incomplete` and
`capture_errors` (an array). Capture flags other than `timed_out` are available
only after an attempted process capture; unavailable logs remain null.

Successful `renderer_metrics` and parsed stdout have exactly these keys:
`status`, `model`, `evidence_status`, `profile_id`, `authoring_sha256`, `sample_rate`,
`block_size`, `frames`, `seed`, `channels`, `sample_format`, `clipped_frames`,
`clipped_channel_samples`, `peak`, `rms`, `render_schema_version`, `contact_model`
and `percussion_model`. The three new required fields are:

| Field | Required value |
| --- | --- |
| `render_schema_version` | Integer `2`, not a float or Boolean |
| `contact_model` | `ideal-contacts-v1` for `parameters.contacts == "ideal"`; `nominal-linear-travel-v1` for `"nominal"` |
| `percussion_model` | `shared-readiness-v1`, including when percussion starts disabled |

`model` remains `ideal-shared-sine-v1`, the source-generator identity, and
`evidence_status` remains `unmeasured`. Missing, extra, mistyped or inconsistent
fields fail the metrics gate; the wrapper does not accept an older renderer merely
because it emits the old fields. The chosen contact factory is independent of
score controls. The fixed shared-readiness identity names a software algorithm,
without asserting measured contact mechanics or percussion circuit fidelity.

Earlier schema-1 bundles remain historical evidence with their original exact
field sets and invocation order. They lack all four console parameters and the
three new metric fields, and put `--fail-on-clip` immediately after `--drawbars`
and its value. They describe the legacy ideal-contact, percussion-off renderer.
The current producer only writes schema 2. An independent consumer supporting both
versions must choose the corresponding strict contract explicitly; it must not
silently upgrade a schema-1 bundle or accept mixed-version fields. See
[RENDER_VERIFICATION.md](RENDER_VERIFICATION.md) for the independent consumer's
supported versions and replay rules.

The raw authoring-file hash and canonical authoring hash are deliberately distinct.
The canonical digest follows [PROFILE_FORMAT.md](PROFILE_FORMAT.md); it is repeated
in the compiled profile and actual renderer metrics. Git HEAD and dirty status
are context about this checkout. They do **not** authenticate how the supplied
executable was built. Executable before/after hashes establish stable observed
bytes, not a reproducible build, linked-library provenance or resistance to a
concurrent actor that changes and restores a file between observations.

### Portable file integrity

Repository text uses LF on checkout, including the catalog, scores and authoring
profile; `.gitattributes` marks PDF, WAV and compiled-profile files as binary.
This keeps checked-in raw-byte identities stable with `core.autocrlf=true`.
The wrapper still preserves the actual bytes of supplied inputs and captured
stdout/stderr. A caller's CRLF score or profile is not converted to LF.

The bounded hash reader and WAV inspector require regular nonsymlink paths and
regular opened files of matching size. Each compares complete metadata stamps
(device, inode, mode, size, modification time and change/creation time) within
the same API: path `lstat` before/after, and descriptor `fstat` before/after.
POSIX additionally requires matching path/descriptor device and inode identities.
The hash reader also checks the actual byte count against the observed size.
Windows can report different timestamp meanings through the two APIs, so a full
path-versus-descriptor stamp equality is not a portable integrity criterion.
Raw-byte SHA-256 checks before/after the renderer remain required on every platform.
See [Windows evidence repair](WINDOWS_EVIDENCE.md) for the observed failure,
upstream explanation, regression coverage and native rerun status.

### WAV and metric definitions

`wav` records `path`, `sha256`, `size_bytes`, `sample_format: "pcm_s16le"`,
`sample_rate`, `frames`, `channels: 2`, `channels_identical: true`,
`normalization_divisor: 32768`, `pcm_peak_integer`, `pcm_sum_squares_integer`,
`pcm_peak`, `pcm_rms`, and `metric_domain: "quantized_pcm16"`.
The integers describe one channel because both channels are verified identical.

For decoded left-channel samples `s[n]`, the PCM peak is `max(abs(s[n]))/32768`
and PCM RMS is `sqrt(sum(s[n]*s[n])/frames)/32768`. The sum of squares is accumulated
as an exact Python integer while streaming bounded blocks. Floating-point metrics
come from the engine before quantization and are not generally identical to PCM
metrics. Rounding normally contributes at most half a PCM16 step; positive endpoint
saturation can contribute a full step even with zero reported clipping. Therefore
both absolute differences must be at most `1/32768 + 1e-12`. This is a software
quantization check in normalized units, not an acoustic tolerance.

### Independent verification procedure

An independent consumer should implement these checks from this document rather
than trusting the producer's Boolean fields or importing its verification helpers:

1. Require schema 2 for current producer output, the exact evidence scope,
   `status == "succeeded"`, null error,
   UTC start/finish, `integrity_verified == true`, and all expected typed fields.
   Bound the manifest size and reject duplicate keys or nonfinite JSON numbers.
2. Require the documented artifact filenames, regular nonsymlink files inside the
   result directory, and matching raw-byte sizes/SHA-256. Reject missing or extra
   unexpected evidence paths. Hash retained stdout/stderr too.
3. Parse `profile.json` with the supported strict compiler, compile it independently,
   and compare all `profile.b3p` bytes plus the canonical authoring digest. Validate
   score events against parameters; preserve file order at equal timestamps.
4. Require an argument list using the documented copied files and actual parameters,
   in the fixed order above with all four console flags and `--fail-on-clip`, exit 0,
   no timeout/truncation/capture errors, and an unchanged
   executable hash. Rehash the executable if still available; an unavailable external
   executable limits current re-verification and replay, even when artifact hashes pass.
5. Parse stdout and require exact equality to `renderer_metrics`; check `status: "ok"`,
   the exact schema-2 field set and types, contact factory and percussion algorithm,
   the supported source-model/unmeasured/profile identities, canonical digest, frames, rate,
   block, seed, stereo PCM16 and zero clipped-frame/channel counts. Float peak/RMS
   must be finite, nonnegative, at most 1, and RMS must not exceed peak.
6. Verify the exact 44-byte little-endian RIFF/WAVE header: PCM format 1, `fmt ` size
   16, two channels, 16 bits/sample, byte rate `rate*4`, block alignment 4, data size
   `frames*4`, RIFF size `36+frames*4`, and total file size `44+frames*4`. Reject extra
   chunks/trailing bytes for this version. Stream every frame and require equal
   channels, expected count, matching hash, integer peak and sum of squares.
7. Recompute normalized PCM statistics and their quantization-qualified comparison.
   Do not grant authenticity from a self-consistent manifest: an unauthenticated
   bundle can be forged or rewritten along with its hashes. Keep independent trust,
   build provenance, reproducibility and physical-fidelity decisions separate.

Replay may compare raw input/compiled/WAV hashes, actual metrics and parameters
while excluding timestamps, directory-dependent argv paths and sampled repository
metadata. Bitwise equality is a same-build engineering check. Compiler, standard
library, architecture or runtime changes may alter floating-point audio bytes.

## Bounds and test entry point

Profile/compiler limits come from the existing compiler (256 KiB authoring,
128 KiB compiled). Scores are bounded to 16 MiB, 4096 bytes/line, 262144 events and
1024 events at one frame. Executables are bounded to 512 MiB; wrapper/compiler
source files to 1 MiB each. Each stdout/stderr stream retains at most 1 MiB; excess
output terminates the renderer and marks capture truncation. A timeout terminates
the renderer; POSIX termination also targets its process group. Parsed metrics are
bounded to 16 KiB and a flat object of at most 64 scalar fields; malformed/oversized
metrics remain in the raw log but cannot create successful evidence. WAV inspection
uses 64 KiB blocks and no whole-audio allocation. Maximum expected PCM output is
230,400,044 bytes at 96000 Hz for 600 seconds. This wrapper is not an execution
sandbox for an arbitrary malicious executable, and a timeout is not a callback
performance benchmark.

CTest discovers `tests/test_render_fixture.py` and supplies
`HAMMOND_RENDER_EXECUTABLE` and `HAMMOND_TEST_PROFILE`. Both are required; missing
inputs fail clearly rather than skip. The suite uses modest real renders and
covers retained identities, deterministic replay, literal paths, rate/seed/event
boundaries, preflight failures, no-clobber behavior, actual clipping, changed inputs
or executable, malformed WAV/metrics, process failure, capture bounds and timeout.
It also exercises Windows metadata asymmetry on every platform, rejects changes
within either metadata API, retains deliberate CRLF inputs/raw logs, and checks a
temporary Git checkout with `core.autocrlf=true` without changing this checkout's
configuration. Missing Git or renderer prerequisites fail; these checks do not skip.
