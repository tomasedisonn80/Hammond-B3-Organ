# Three-second nominal pedal and manual phrase

[Listen to the WAV](bundle/render.wav). This original C–F–G–C gesture combines
both manuals with the implemented pedal division. It is **three seconds of
stereo PCM16 at 48 kHz**, with identical dry channels and no post-processing.
The retained [score](bundle/events.txt) is an exact copy of the accepted
[pedal phrase fixture](../../fixtures/pedals/pedal-phrase-v1.events).

The source and pedal voice are explicitly **nominal and unmeasured**. Both
manuals and the pedals use the same 91 continuously running sine sources.
Pedal Mixture 1 and Mixture 2 are the named fixed engineering mixtures; their
positions are not a claim of calibrated physical 16-foot/8-foot responses.
There is no scanner, AO-28 or Leslie processing in this audio.

## What the score does

The upper B registration is `006400000`: its 8-foot position is six and its
4-foot position is four. The score sets the lower B 8-foot position to six.
The two pedal positions are `32`, expression is `0.75`, seed is `2704`, manual
contacts are ideal and percussion is off. Velocity 100 is a full-press command,
with no velocity-dependent steady loudness. The 38 score events retain their
literal ordering, including the separate manual and pedal panics at each chord
boundary.

| Time | Half-open frames | Gesture in the nominal pitch model |
| --- | --- | --- |
| 0–0.10 s | `[0, 4800)` | Controls are initialized; all divisions remain silent. |
| 0.10–0.70 s | `[4800, 33600)` | Upper MIDI 60/64/67 and lower 48/55, with pedal row 1: C opening. |
| 0.70–1.30 s | `[33600, 62400)` | Upper MIDI 60/65/69 and lower 53/60, with pedal row 6: F. |
| 1.30–1.90 s | `[62400, 91200)` | Upper MIDI 59/62/67 and lower 55/62, with pedal row 8: G. |
| 1.90–2.50 s | `[91200, 120000)` | The opening manual keys and pedal row 1 return at their continuing source phases. |
| 2.50–3.00 s | `[120000, 144000)` | Independent upper, lower and pedal panics leave an exactly silent tail. |

Pedal rows are wiring identifiers 1–25, not an inferred physical MIDI octave.
The C/F/G names describe the nominal 12-TET software profile. The return chord
need not repeat the opening samples because the shared sources keep running.
Ideal contact switching can produce discontinuities; this example does not
qualify switching-bandwidth suppression.

## Observed audio and evidence

The untouched producer-created [schema-3 bundle](bundle/manifest.json) passed
the [independent retained-bundle verifier](analysis/verification.json). It
checked six retained artifacts plus the manifest: input profile compilation,
the exact score, raw renderer logs, pedal/model identities, WAV bytes and
numerical consistency. Its source/build authentication field remains
`not_established`; the separate local build record below supplies observed
archive/build provenance without rewriting that verdict.

Three actual renders used blocks **64, 127 and 1024**. Their complete
**576,044-byte WAV files are identical**, including all 144,000 stereo frames.
Only block 127 is retained here; alternate WAVs were temporary comparison
outputs. There was no normalization, limiting, editing or resampling.

The renderer reported float peak **0.08429475128650665**, float RMS
**0.022980303816301697**, **zero clipped frames** and **zero clipped channel
samples**. The independent PCM analyzer measured signed integer samples divided
by 32768:

| Analysis window | Half-open frames | PCM peak | PCM RMS |
| --- | --- | ---: | ---: |
| [Whole file](analysis/whole.json) | `[0, 144000)` | 0.0842895508 | 0.0229803181 |
| [Leading silence](analysis/leading-silence.json) | `[0, 4800)` | 0 | 0 |
| [C opening](analysis/c-opening.json) | `[7200, 30000)` | 0.0842895508 | 0.0244948678 |
| [F](analysis/f.json) | `[36000, 58800)` | 0.0673828125 | 0.0271844681 |
| [G](analysis/g.json) | `[64800, 87600)` | 0.0723266602 | 0.0265116712 |
| [C return](analysis/c-return.json) | `[93600, 116400)` | 0.0646667480 | 0.0244192689 |
| [Trailing silence](analysis/trailing-silence.json) | `[120000, 144000)` | 0 | 0 |

Every report found identical channels and no full-scale endpoint codes. The
leading 4,800 and trailing 24,000 frames are exactly zero on both channels.
The four chord windows are the catalog's stationary spans and do not cross
score events. They are mixtures, so no single-tone crossing-rate or general
pitch estimate was requested. Windows overlap the whole-file report; their
counts are not independent additional audio duration. PCM endpoint counts do
not establish pre-quantization clipping; the renderer's separate counters above
provide that observation. Subjective listening was not performed.

## Source and artifact identities

The build used an exact archive of published commit
[`d7b886103f8c9d4649ffa1c35930b79808217a3d`](https://github.com/tomasedisonn80/Hammond-B3-Organ/tree/d7b886103f8c9d4649ffa1c35930b79808217a3d),
tree `018c3897889aaae0070f632981e0c889a35cad30`. All **474 committed file blobs**
were checked before compilation and after rendering. A fresh SDK-free Release
build used GCC 14.2.0, CMake 3.31.6 and Python 3.12.14. The
[source inventory](source-blobs.json) retains the observed Git blobs, SHA-256
values and sizes; [provenance.json](provenance.json) records actual commands,
all 17 compilation units, the executable, tools, profile, comparison runs and
payload hashes.

The source archive has no Git metadata. The genuine producer manifest therefore
correctly records unavailable Git HEAD/dirty observations. The separate source
record is an observed local build record, not a signed attestation. Historical
absolute paths identify that run and are not instructions to execute.

| Artifact | SHA-256 |
| --- | --- |
| Complete WAV | `a3d1958189e811b8e353a75380d380016db5286eb08a2005626d95df64dde6f1` |
| PCM data bytes | `3107d186bb811b2cf1a2a3497422f5d77169f92ca2c9c7f22a1553482141c77c` |
| Compiled profile | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| Score | `47daa264ca9524c98d7a189d28728778c9057852b8fd3d68e7fea9d2e63b9be5` |
| Renderer executable | `a0a33ffad00f01f82e3e25fb59b9225c0d4aa5655ce601fea3b81e2c8af9079e` |

The immutable authoring JSON's raw SHA-256 is
`d17a266ed97cbbd3a2925ebebafafbd6c0e3f84763635732e0a9351d0eab2bff`.
Its distinct canonical authoring identity remains
`49791eac8d0b556b0abd2018b8cabc6f240161edab8a9fa0ef97905f2badda83`.

## Verify and replay

From the repository root, verify the retained bundle without executing its
historical invocation:

```sh
python tools/verify_render.py examples/demos/pedal-phrase-v1/bundle
python tools/analyze_wav.py --input examples/demos/pedal-phrase-v1/bundle/render.wav
```

Rebuild the recorded source in fresh worktree/build paths, then choose a new
output directory. These commands leave the retained example unchanged:

```sh
git worktree add --detach ../hammond-pedal-demo-source d7b886103f8c9d4649ffa1c35930b79808217a3d
cmake -S ../hammond-pedal-demo-source -B ../hammond-pedal-demo-build -DCMAKE_BUILD_TYPE=Release
cmake --build ../hammond-pedal-demo-build --config Release --parallel 2 --target hammond_render
cmake -E make_directory out
python ../hammond-pedal-demo-source/tools/render_fixture.py \
  --renderer ../hammond-pedal-demo-build/hammond_render \
  --profile-json examples/demos/pedal-phrase-v1/bundle/profile.json \
  --events examples/demos/pedal-phrase-v1/bundle/events.txt \
  --output-dir out/pedal-phrase-replay \
  --frames 144000 --sample-rate 48000 --block-size 127 --seed 2704 \
  --drawbars 006400000 --pedal-drawbars 32 --contacts ideal \
  --percussion off --percussion-volume normal --percussion-decay slow
python ../hammond-pedal-demo-source/tools/verify_render.py out/pedal-phrase-replay
```

For Windows or another multi-configuration generator, select the actual
configuration subdirectory and suffix, such as
`../hammond-pedal-demo-build/Release/hammond_render.exe`. Output paths must be
new. A replay has fresh paths/timestamps and its own executable identity;
cross-compiler/libm byte equality is not promised by the same-build partition
observation. If the original external executable later becomes unavailable,
verification can still validate retained artifacts while reporting renderer
status `unavailable`; a present executable with different bytes fails its hash
check.

See [the catalog and independent amplitude checks](../../../docs/PEDAL_AUDIO_ACCEPTANCE.md),
[schema-3 evidence](../../../docs/PEDAL_RENDER_EVIDENCE.md) and
[current status](../../../docs/STATUS.md) for the scope and remaining work.
Physical pedal shaping, low-wheel spectra, contact timing, loaded expression,
scanner/AO-28/Leslie modeling, DAW/device operation and fidelity need separate
evidence. This demo supplies a reproducible musical example of the current
nominal software.
