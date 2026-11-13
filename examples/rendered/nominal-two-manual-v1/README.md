# Nominal dry-organ audible example

**[Listen to or download render.wav](bundle/render.wav)** — 4.0 seconds,
48,000 Hz, 2 identical dry PCM16 channels. This is an actual retained
render of the existing `two-manual-changes-v1` synthetic score, using
`nominal-unmeasured-v1` / `ideal-shared-sine-v1`. It contains no recorded
instrument samples or physical capture.

## What to listen for

The score moves through C–F–G–C on two manuals. At 1.75 seconds, the upper
registration changes from `006400000` to `007503000`: the 8-foot and 4-foot
branches rise and a 2-foot branch is added. At frame zero, the score sets the
linear expression control to 0.75 and lower bank B to `405000000`.
The final half-second is exactly silent.

The timeline comes from the [retained score](bundle/events.txt) and
[versioned catalog](../../fixtures/catalog-v1.json). The independent window
reports below measure activity and silence in the actual PCM. Intervals are
half-open; nonzero counts and RMS are per channel, and both channels agree.

| Time, seconds | Frames | Score event / listening cue | Nonzero samples | PCM RMS / report |
| --- | --- | --- | ---: | ---: |
| [0.00, 0.05) | [0, 2400) | Initial silence | 0 | [0.0](reports/analyze-leading-silence.json) |
| [0.05, 0.90) | [2400, 43200) | C major on both manuals | 40774 | [0.018317496298050226](reports/analyze-c-opening.json) |
| [0.90, 1.75) | [43200, 84000) | F major on both manuals | 40766 | [0.018274587423533675](reports/analyze-f.json) |
| [1.75, 2.60) | [84000, 124800) | G major; brighter upper registration | 40772 | [0.024370418755814516](reports/analyze-g-brighter.json) |
| [2.60, 3.50) | [124800, 168000) | C major return; brighter registration retained | 43184 | [0.024405497092609574](reports/analyze-c-return.json) |
| [3.50, 4.00) | [168000, 192000) | All keys released; final silence | 0 | [0.0](reports/analyze-trailing-silence.json) |

The ideal gates and stepped control changes can click at event boundaries.
The output has no scanner, percussion, pedal audio, AO-28 electronics, Leslie,
room, or stereo rotary field. No frequency estimate was requested for this
polyphonic score; the analyzer is not being used as a general pitch recognizer.

## Actual run and observed results

The wrapper completed successfully at `2026-11-13T04:33:12.990304Z` and
captured 34 explicit score events. It used a 127-frame block size,
seed 2601, and initial upper-B drawbars `006400000`. The wrapper
compiled the copied authoring profile and passed `--fail-on-clip` to the renderer.
No audio normalization or post-processing was applied.

| Observation | Actual result | Evidence |
| --- | --- | --- |
| WAV frames / rate / channels | 192000 / 48000 Hz / 2 | [Whole-file analysis](reports/analyze-whole.json) |
| WAV size, including 44-byte header | 768,044 bytes | [Manifest](bundle/manifest.json) |
| Renderer float peak / RMS | 0.08130008727312088 / 0.02006219567993473 | [Raw renderer stdout](bundle/renderer.stdout.txt) |
| PCM peak / RMS | 0.081298828125 / 0.020062170290109253 | [Whole-file analysis](reports/analyze-whole.json) |
| PCM DC | -4.130045572916667e-06 | Whole-file analysis; normalized PCM |
| PCM integer peak / sum of squares | 2664 / 82976846092 | Manifest; one channel |
| Renderer clipped frames / channel samples | 0 / 0 | Raw renderer stdout; pre-encoding observation |
| PCM full-scale channel samples | 0 | Whole-file analysis; both channels combined |
| Differing stereo frames | 0 | Whole-file analysis |
| Independent bundle verification | `verified_retained_bundle` | [Verifier report](reports/verify-render.json) |

The float-to-PCM peak difference is
`1.259148120880127e-06` and the RMS difference is
`2.538982547817259e-08`. The verifier independently accepted both
within the documented bound of one PCM16 step (`3.0517578125e-05`)
plus numerical tolerance `1e-12`.

Renderer clipping counts and PCM endpoint counts describe different observations.
The PCM analyzer reports `not_inferable_from_pcm16` for earlier
clipping; zero endpoint codes alone cannot establish that history. Peak here is
sample peak, not intersample true peak. All amplitudes are normalized digital
quantities with no volts, pressure, clock calibration, or hardware-fidelity claim.

## Executed commands

Working directory: `/workspace/scratch/c871510c69b2/Hammond-B3-Organ`.
The demo parent was created first, with `bundle/` absent. `render_fixture.py`
created `bundle/` itself; `reports/` was then created beside it. Every command
below returned exit code 0. The producer's exact renderer argument list and raw
stdout/stderr are retained in the bundle. The manifest has not been edited.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tools/render_fixture.py --renderer /tmp/hammond-wave07-asuv11lz/build/hammond_render --profile-json data/profiles/nominal-unmeasured-v1.json --output-dir examples/rendered/nominal-two-manual-v1/bundle --events examples/fixtures/two-manual-changes-v1.events --sample-rate 48000 --frames 192000 --block-size 127 --seed 2601 --drawbars 006400000
PYTHONDONTWRITEBYTECODE=1 python3 tools/verify_render.py examples/rendered/nominal-two-manual-v1/bundle > examples/rendered/nominal-two-manual-v1/reports/verify-render.json
PYTHONDONTWRITEBYTECODE=1 python3 tools/analyze_wav.py --input examples/rendered/nominal-two-manual-v1/bundle/render.wav > examples/rendered/nominal-two-manual-v1/reports/analyze-whole.json
PYTHONDONTWRITEBYTECODE=1 python3 tools/analyze_wav.py --input examples/rendered/nominal-two-manual-v1/bundle/render.wav --start-frame 0 --end-frame 2400 > examples/rendered/nominal-two-manual-v1/reports/analyze-leading-silence.json
PYTHONDONTWRITEBYTECODE=1 python3 tools/analyze_wav.py --input examples/rendered/nominal-two-manual-v1/bundle/render.wav --start-frame 2400 --end-frame 43200 > examples/rendered/nominal-two-manual-v1/reports/analyze-c-opening.json
PYTHONDONTWRITEBYTECODE=1 python3 tools/analyze_wav.py --input examples/rendered/nominal-two-manual-v1/bundle/render.wav --start-frame 43200 --end-frame 84000 > examples/rendered/nominal-two-manual-v1/reports/analyze-f.json
PYTHONDONTWRITEBYTECODE=1 python3 tools/analyze_wav.py --input examples/rendered/nominal-two-manual-v1/bundle/render.wav --start-frame 84000 --end-frame 124800 > examples/rendered/nominal-two-manual-v1/reports/analyze-g-brighter.json
PYTHONDONTWRITEBYTECODE=1 python3 tools/analyze_wav.py --input examples/rendered/nominal-two-manual-v1/bundle/render.wav --start-frame 124800 --end-frame 168000 > examples/rendered/nominal-two-manual-v1/reports/analyze-c-return.json
PYTHONDONTWRITEBYTECODE=1 python3 tools/analyze_wav.py --input examples/rendered/nominal-two-manual-v1/bundle/render.wav --start-frame 168000 --end-frame 192000 > examples/rendered/nominal-two-manual-v1/reports/analyze-trailing-silence.json
```

These are historical command paths. For another render, use a newly built
renderer and a new output directory; the wrapper preserves existing destinations.
Write new reports outside `bundle/`. Its strict seven-file inventory excludes
this README and the eight independent reports.

## Raw-byte identities

The WAV SHA-256 below covers the entire original `render.wav` file, including its
header and PCM data. The table was generated from the retained files; values in
the result tables were read from the actual JSON outputs. Hashes are integrity
identities, not signatures or independent authentication.

| Retained artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| [bundle/events.txt](bundle/events.txt) | 1607 | `d86b7fb3e3a62865b218400828aaef7ee176c39da7f08ef29aed5ae5b0627ae8` |
| [bundle/manifest.json](bundle/manifest.json) | 5495 | `74ad49caa3cc5170870bed1002ea64ffaaf8a202c0614095b31fdcd8308da2ce` |
| [bundle/profile.b3p](bundle/profile.b3p) | 4545 | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| [bundle/profile.json](bundle/profile.json) | 19627 | `d17a266ed97cbbd3a2925ebebafafbd6c0e3f84763635732e0a9351d0eab2bff` |
| [bundle/render.wav](bundle/render.wav) | 768044 | `9c46d82dc8da8ba5be078e895765e98672b51a30da52e0684d75a293aa4d84fd` |
| [bundle/renderer.stderr.txt](bundle/renderer.stderr.txt) | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| [bundle/renderer.stdout.txt](bundle/renderer.stdout.txt) | 408 | `a7778003ce642c29b39609602082d1824f4b4df279a3513b0815fd9eacc949b1` |
| [reports/analyze-c-opening.json](reports/analyze-c-opening.json) | 2481 | `3d9c55eed17681bd86f36d45a58d7f7f5953685de57a12adff8060a6e37c4971` |
| [reports/analyze-c-return.json](reports/analyze-c-return.json) | 2479 | `cc150468983463978c81764718539033008723bc7046c28e409ee7a99cb36ced` |
| [reports/analyze-f.json](reports/analyze-f.json) | 2476 | `dff691959cab30daf691e09f843d6b8ac4b204ac3c76b175415cf99127c643b6` |
| [reports/analyze-g-brighter.json](reports/analyze-g-brighter.json) | 2473 | `0807300bdc54a368b85e576cfdf2c810282c0712c2d19292f54ca923d39af709` |
| [reports/analyze-leading-silence.json](reports/analyze-leading-silence.json) | 2364 | `555e70240d641e78347b6148e79d0d463108c685a3cb924e24ad09e3a8013706` |
| [reports/analyze-trailing-silence.json](reports/analyze-trailing-silence.json) | 2373 | `fe6c67d3d0c16332fbd634a344f0dfd9027e28ae91006b9d8deec62721c32d5b` |
| [reports/analyze-whole.json](reports/analyze-whole.json) | 2475 | `48be2e4b670e3d103225c848da95ba0e3d8c4d3b836ac75448be3eb70b17a58a` |
| [reports/verify-render.json](reports/verify-render.json) | 1026 | `6f16672e9ec97f05e2a4b14d8bec83a27ac38ecd34468ea4b45eaed2692b65b0` |

The canonical authoring SHA-256 is
`49791eac8d0b556b0abd2018b8cabc6f240161edab8a9fa0ef97905f2badda83`.
It matches the catalog's authoring identity and differs intentionally from the
raw `profile.json` hash. The compiled profile also matches the catalog's
compiled identity. Tool/catalog identities sampled for the independent checks:

| Source | Bytes | SHA-256 |
| --- | ---: | --- |
| [tools/verify_render.py](../../../tools/verify_render.py) | 30277 | `b87b64da5577c17265ef7c52bebf950a2b32a530f8a26c39ab7228b4d0822db2` |
| [tools/analyze_wav.py](../../../tools/analyze_wav.py) | 15835 | `e39d3b414854066af2510c3dedf26c70ea71066a09efce5a9cdb41114e8b5fb7` |
| [examples/fixtures/catalog-v1.json](../../../examples/fixtures/catalog-v1.json) | 15544 | `98ffa2c3bc30f60ceb839e1fc2ab978e45dcf5f2cb4970fe77f91894344c34f8` |

The producer manifest separately records the wrapper and profile-compiler
source hashes. The external renderer was `/tmp/hammond-wave07-asuv11lz/build/hammond_render`,
106,368 bytes, SHA-256
`8e781cb1df6f87443c4b6c88587cfa0e7d2bc8e23d32b5ef0a0bfb84d9ee8be4` before and after the run.
The verifier found matching readable executable bytes at verification time.
The executable and build tree are not included in this package.

## Provenance and verification limits

The producer recorded checkout HEAD
`6c3dd8bc923a3c11f6b234425b056e135fbe9f4b` with `dirty: true` at
`2026-11-13T04:33:12.675942Z`. This is invocation-time checkout context.
`git.binary_association` remains `not_established`; this package does
not authenticate the source revision that built the external executable.

The verifier checked 6 retained artifacts plus the manifest, recompiled the
retained profile, checked the score and invocation, reconciled raw stdout with
producer metrics, and independently checked WAV bytes and numerical assertions.
It did not replay the renderer. Authentication, source/build association, physical
fidelity, host qualification, and real-time deadline evidence remain unestablished.
If the temporary executable later disappears, the verifier may report it
unavailable while still checking the retained artifacts. Rebuilt audio is not
promised to be bitwise identical across compilers, libraries, or platforms.

See [render evidence](../../../docs/RENDER_EVIDENCE.md),
[independent verification](../../../docs/RENDER_VERIFICATION.md), and
[PCM measurement definitions](../../../docs/AUDIO_MEASUREMENTS.md) for the exact
contracts and remaining limits.
