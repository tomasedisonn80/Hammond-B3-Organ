# Agent 27 — independent PCM audio measurements

Wave 05 assignment; completed 2026-11-13. Owned only `tools/analyze_wav.py`,
`tests/test_audio_analysis.py`, `docs/AUDIO_MEASUREMENTS.md`, and this note.
Read AGENTS/shared handoff, RENDER_FORMAT/actual CLI, profile/mix contracts, and
atlas chapters 058/060 (PDF pp. 355–360/367–372). Preserved unrelated active work.

## Delivered behavior

- Stdlib-only, read-only bounded RIFF/PCM16 parser and streaming integer statistics;
  per-channel peak/RMS/DC/nonzero/endpoint counts; exact stereo equality.
- Explicit normalized PCM units, half-open frame windows, optional linearly
  interpolated rising-crossing estimates under a declared steady fixture assumption.
- Nonfinite/range/unsupported/truncated/oversized input rejection; finite JSON.
  Full-scale codes never become confirmed pre-quantization clipping: that is null.
- Independent `wave`/`struct` fixtures and a separately required actual C++ A4 render.
  No producer metrics implementation imported; no dependencies or binaries added.

## Executed commands and results

```sh
HAMMOND_RENDER_EXECUTABLE=/workspace/scratch/c871510c69b2/agent22-debug/hammond_render \
HAMMOND_TEST_PROFILE=/workspace/scratch/c871510c69b2/agent22-debug/nominal.b3p \
PYTHONDONTWRITEBYTECODE=1 python tests/test_audio_analysis.py -v
```

All 15 tests passed (final run 0.548 s), including the real renderer integration case.
`HAMMOND_RENDER_EXECUTABLE=/missing/required/hammond_render python tests/test_audio_analysis.py RealRendererIntegrationTests`
returned nonzero exit 5 with `FAILED (errors=1)` and explicit missing-input diagnostic;
this deliberate negative check confirms there is no successful skip/fallback.
`agent22-debug/hammond_render --help` matched the invocation below; four added-file
diff checks reported no whitespace errors. Temporary render/fixture files were deleted.

Reproduction (set `RENDER`/`PROFILE` to the two absolute paths above; existing output
destinations are rejected, so use a fresh temporary output directory):

```sh
"$RENDER" --profile "$PROFILE" --output /tmp/fresh-audio-analysis/a4.wav \
  --sample-rate 48000 --frames 48000 --block-size 127 --seed 0 \
  --drawbars 008000000 --note 69 --fail-on-clip
python tools/analyze_wav.py --input /tmp/fresh-audio-analysis/a4.wav \
  --start-frame 4800 --end-frame 28800 --expected-frequency 440
```

| Observed steady-window quantity (each channel) | Value |
| --- | --- |
| Frames / normalized PCM peak | 24000 / 0.029998779296875 |
| RMS / DC | 0.021212537545914806 / 0 |
| Nonzero / endpoint samples | 24000 / 0 |
| Stereo differing frames | 0 |
| Rising crossings / complete periods | 220 / 219 |
| Candidate Hz / error Hz | 439.9999816417002 / -0.000018358299826104485 |

Full-file PCM RMS was 0.018370596393493432; producer float RMS was
0.018371173065559514 with 0 clipped frames. Quantization/error tolerances and
crossing ambiguity are justified in AUDIO_MEASUREMENTS.md; no fidelity follows.
SHA-256 identities for this executed synthetic render:

- Renderer: `eb9ebb0a5f0617ad62eb680490ace85974f4ca6d81b56aa76113ca02cc5b28fc`.
- Profile: `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.
- WAV: `0aa5ab98cc464cfd1deba581813074fd2ecf10165e1db035245278f943400026`.

Next integration: retain analyzer JSON with catalog fixture identities and windows;
physical captures, calibrated clock/levels, general pitch recognition and fidelity
remain outside this assignment. Shared status/log/commit/push belong to integrator.
