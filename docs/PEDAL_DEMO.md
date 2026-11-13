# Retained nominal pedal phrase

The [three-second C–F–G–C example](../examples/demos/pedal-phrase-v1/README.md)
is an actual render of the accepted pedal phrase, combining both manuals and
the two named nominal pedal mixtures. [Listen to its WAV](../examples/demos/pedal-phrase-v1/bundle/render.wav)
or inspect the retained [schema-3 manifest](../examples/demos/pedal-phrase-v1/bundle/manifest.json).

The artifact is 144,000 stereo PCM16 frames at 48 kHz, with identical dry
channels. It uses upper B registration `006400000`, the score's lower B 8-foot
position six, pedal positions `32`, expression `0.75`, seed `2704`, ideal manual
contacts and percussion off. Thirty-eight ordered score events retain separate
upper/lower/pedal panics and the literal pedal rows 1, 6 and 8. Pedal identifiers
are wiring rows, not an inferred physical MIDI octave.

## What was verified

The demo was built from published source
`d7b886103f8c9d4649ffa1c35930b79808217a3d`, tree
`018c3897889aaae0070f632981e0c889a35cad30`. All 474 archived file blobs matched
before and after the fresh GCC 14.2.0 Release build and audio generation. The
[provenance record](../examples/demos/pedal-phrase-v1/provenance.json) identifies
the source, actual 17 compilation units, renderer, exact commands, input bytes,
tools and outputs. The producer's unavailable Git observation for a plain
archive was preserved rather than rewritten.

| Check | Observed result |
| --- | --- |
| Independent bundle verifier | Schema 3 accepted; six artifact payloads plus manifest checked |
| Same-build blocks 64 / 127 / 1024 | Complete WAV files byte-identical |
| Float renderer peak / RMS | `0.08429475128650665` / `0.022980303816301697` |
| Pre-encoding clipping counters | Zero frames and zero channel samples |
| Independent whole-file PCM peak / RMS | `0.08428955078125` / `0.02298031808643901` |
| Channels / PCM endpoint codes | Identical channels; zero full-scale codes |
| Silent spans | `[0, 4800)` and `[120000, 144000)` are exactly zero |
| Retained WAV identity | 576,044 bytes; SHA-256 `a3d1958189e811b8e353a75380d380016db5286eb08a2005626d95df64dde6f1` |

Seven independent analyzer reports retain the full file, leading/trailing silence
and the four catalog-defined stationary chord windows. These are overlapping
views of the same three seconds. No monophonic-frequency declaration was made
for a harmonic mixture. PCM endpoint counts and pre-encoding clipping remain
different observations. No normalization, resampling or subjective listening
was performed.

## Use and continue

From the repository root:

```sh
python tools/verify_render.py examples/demos/pedal-phrase-v1/bundle
python tools/analyze_wav.py --input examples/demos/pedal-phrase-v1/bundle/render.wav
```

The [example README](../examples/demos/pedal-phrase-v1/README.md#verify-and-replay)
gives the exact recorded-source worktree/build/render recipe and Windows
configuration-path adjustment. Always choose new outputs. Verification is
read-only and never executes historical paths from the manifest.

This retained example is synthetic engineering evidence for the existing
`nominal-static-pedal-mixture-v1` and ideal shared sine source model. It does not
establish measured pedal spectra, physical reactor/loading response, calibrated
footage, scanner/AO-28/Leslie processing, native host/device behavior or a
specimen match. The [catalog's independent amplitude/phase acceptance](PEDAL_AUDIO_ACCEPTANCE.md)
and [pedal evidence contract](PEDAL_RENDER_EVIDENCE.md) supply the model and
verification context. The next demo gate is an independent replay and byte/
provenance review of this actual retained artifact, separate from this producer
assignment's executed checks.
