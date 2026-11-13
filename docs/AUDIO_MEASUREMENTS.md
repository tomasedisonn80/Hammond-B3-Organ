# Independent PCM audio measurements

`tools/analyze_wav.py` is a Python standard-library, read-only analyzer for the
repository's synthetic engineering WAV fixtures. It does not import the renderer,
fixture wrapper, or their metrics implementations. It inspects actual RIFF headers
and PCM bytes, then emits JSON to standard output. It creates no files and performs
no normalization, resampling, or source modification.

These are measurements of serialized digital samples. They establish no specimen,
AO-28/Leslie response, hardware calibration, physical clock accuracy, or fidelity.
The distinction follows atlas chapters 058 and 060, PDF pp. 355–360 and 367–372;
see [the evidence review](research/ATLAS_REVIEW.md). The renderer's separate float
metrics are defined in [RENDER_FORMAT.md](RENDER_FORMAT.md).

## Commands and API

From the repository root, with an existing rendered WAV:

```sh
python tools/analyze_wav.py --input out/dry-organ.wav
python tools/analyze_wav.py --input out/a4.wav \
  --start-frame 4800 --end-frame 28800 --expected-frequency 440
```

The first command reports the complete file. The second selects the half-open
frame interval `[4800, 28800)` and declares a steady monophonic fixture expected at
440 Hz. Frame indices are zero-based, and a frame contains one sample per channel.
The end defaults to the file's total frame count; start defaults to zero. Empty,
reversed, fractional, negative, and out-of-file windows are errors. The selected
window governs all reported amplitudes, counts, stereo comparisons, and crossings.
Container validation always covers the complete file, including data outside that
window. Crossings use only samples inside the window and report absolute frames.

The import interface is:

```python
from analyze_wav import analyze_wav
report = analyze_wav(path, start_frame=4800, end_frame=28800,
                     expected_frequency=440.0)
```

Place `tools` on the Python module search path when importing. The function raises
`AnalysisError` for invalid/unsupported data or ranges and `OSError` for I/O errors.
CLI rejection returns exit code 2, a stderr diagnostic, and no partial stdout
report. JSON serialization forbids NaN and Infinity. The version identifier is
`analyzer_version: "pcm16-engineering-v1"`; downstream consumers should check it.

## Exact measurement definitions

For channel codes `s[i]` in the selected window of `N` frames, let
`x[i] = s[i] / 32768`. Amplitude unit `normalized_pcm` is dimensionless. The range
is `[-1, 32767/32768]`, and one PCM code step is `1/32768`. There is no volts-per-full-
scale or pascals-per-full-scale calibration; neither volts nor pressure is reported.

| JSON field under each `channels` entry | Definition |
| --- | --- |
| `channel_index` | Zero-based file channel index; no physical channel identity inferred |
| `sample_count` | `N`, one channel sample per selected frame |
| `peak` | `max(abs(s[i])) / 32768`; sample peak, not intersample/true peak |
| `rms` | `sqrt(sum(s[i]**2) / N) / 32768`; includes DC |
| `dc` | Arithmetic mean `sum(s[i]) / (N * 32768)` |
| `nonzero_sample_count` | Number of integer codes unequal to zero |
| `full_scale_sample_count` | Number of codes equal to either `-32768` or `32767` |
| `positive_full_scale_sample_count` | Number of codes equal to `32767` |
| `negative_full_scale_sample_count` | Number of codes equal to `-32768` |

Sums and squared sums accumulate as exact Python integers; only final division and
square root use floating point. `stereo.identical` compares the two integer samples
at every selected frame, and `stereo.differing_frames` counts unequal pairs. For
channel counts other than two, `stereo.applicable` is false and both results are
null. Equal channels alone establish no stereo imaging or acoustic fidelity.

`clipping.full_scale_channel_samples` sums endpoint counts across channels.
An endpoint code can result from a valid full-scale input, rounding, or saturation.
Earlier clipping followed by gain reduction can leave no endpoint codes at all.
Consequently `clipping.confirmed_pre_quantization_clipping` is always null and
`clipping.pre_quantization_status` is `not_inferable_from_pcm16`. This field never
substitutes endpoint counts for the renderer's observed pre-encoding clipping.

## Optional frequency estimate and ambiguity

`--expected-frequency` accepts a finite positive frequency strictly below the WAV
header's Nyquist frequency. Supplying it declares that the chosen window is a
steady monophonic engineering fixture. That declaration is an assumption supplied
by the caller; the analyzer does not recognize a general signal's musical pitch.

Each channel tracks negative-to-positive crossings. Between adjacent nonzero
samples `a < 0 < b` at frames `k` and `k+1`, the crossing is `k - a/(b-a)`.
One exact zero between negative and positive values supplies its exact frame;
a longer zero plateau uses its first zero and receives an ambiguity flag. A zero
tail without a subsequent positive sample does not count as a rising crossing.

At least three crossings wholly inside the selected window are required. With
`C` crossings at first/last positions `t0`/`t1`, the candidate frequency is
`sample_rate_hz * (C-1) / (t1-t0)`. The report retains the complete-period count,
period extrema/spread, observed error in Hz and cents relative to the declaration,
and ambiguity flags. With too few crossings, the candidate and errors are null
and status is `insufficient_crossings`, including for silence and unipolar DC.

Diagnostic flags cover period spread above 1%, mismatch to the declared frequency
above 1%, zero plateaus, fewer than eight samples per expected period, peak below
32 PCM codes, and absolute DC above 10% of peak. These explicit engineering
heuristics select `ambiguous`; they are not calibrated uncertainty intervals or
acceptance thresholds. An unflagged result is `estimated_under_fixture_assumption`,
which is an observation under that assumption, not an automatic test pass.

Harmonics, mixtures, DC bias, noise, transients, aliasing, and short windows can
mislead crossing rates. Stable crossings can correspond to a harmonic or a mixture.
Linear interpolation and PCM quantization also limit timing resolution. The method
does not prove a fundamental, identify notes generally, or measure instrument
fidelity. Select the steady portion of a declared fixture and retain its stimulus,
sample rate, profile, seed, and analysis window with the result.

## Supported input and bounded work

- A regular file with little-endian RIFF/WAVE, PCM format code 1, and signed 16-bit
  samples. IEEE float, compressed, extensible, RIFX, and RF64 WAV are rejected.
- One `fmt ` chunk before one nonempty `data` chunk. PCM `fmt ` size is 16 bytes,
  or 18 with a zero extension length. Duplicate, missing, or disordered format/data
  chunks are rejected. Ancillary chunks are skipped with RIFF padding accounted for.
- 1–8 channels; integer header rates of 1–192000 Hz; at most 600 seconds and
  256 MiB total file size; at most 1024 chunks. These are tool resource limits,
  not a claim that the renderer supports all such rates or channel counts.
- Actual and declared RIFF sizes must match exactly, with no trailing bytes.
  Chunk boundaries, required padding, byte rate, block alignment, and complete
  PCM frames are validated. Truncation is rejected even outside a selected window.
- Header reads are small; PCM is streamed in blocks of at most 4096 frames
  (64 KiB for eight channels). No full-file audio or crossing array is allocated.
  Work is linear in bounded chunk count plus selected frames times channels.
- File descriptor size/modification/change timestamps are checked again after
  analysis to reject detected concurrent changes. This is not an immutable-capture
  guarantee; retain and hash the actual source independently for provenance.

PCM16 has no nonfinite sample representation. Float WAV containing NaN is rejected
as unsupported format, and nonfinite expected frequencies are rejected explicitly.

## Independent tests and real-render integration

The test module generates its own PCM fixtures with Python `wave` and `struct`:
silence, DC, sine, inverted channels, full-scale endpoints, multichannel data,
window boundaries, ancillary chunks, malformed/truncated formats, and numeric
limits. A separate integration class invokes the actual C++ renderer for A4 with
only the 8-foot drawbar (`008000000`, MIDI 69, nominal profile, seed 0).

```sh
HAMMOND_RENDER_EXECUTABLE=/absolute/build/hammond_render \
HAMMOND_TEST_PROFILE=/absolute/build/nominal.b3p \
PYTHONDONTWRITEBYTECODE=1 python tests/test_audio_analysis.py -v
```

Without environment overrides, the executable is `build/hammond_render` (with
`.exe` on Windows), and the profile is `nominal.b3p` alongside it. An explicit
missing path fails setup; it never falls back to another build or silently skips.
CTest supplies both variables through the existing Python-test discovery rules.

For this fixture, whose samples lie well inside PCM16 endpoints, nearest rounding
contributes at most half a PCM step. Peak and RMS comparisons against the producer's
float values use that bound plus `1e-12` for arithmetic. The steady `[4800,28800)`
window at 48 kHz contains 220 nominal 440 Hz cycles before the default note-off at
frame 36000. Its RMS/DC checks add `1e-7` for float engine arithmetic;
peak permits one PCM step for sampled
extrema plus quantization. At amplitude 0.03, half a code shifts a rising crossing
approximately 0.009 frame. Two endpoint errors over the roughly half-second span
contribute about 0.00034 Hz; the predeclared 0.005 Hz tolerance additionally covers
linear sine interpolation and float samples. These are synthetic numerical
tolerances, with no historical service-meter or hardware acceptance meaning.

Executed results and exact identities are retained in
[agent 27's evidence note](development/agent-notes/27-audio-measurements.md).
