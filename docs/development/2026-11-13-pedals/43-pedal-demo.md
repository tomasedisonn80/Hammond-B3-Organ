# Assignment 43 — retained nominal pedal phrase

Owner: /root/w08_a43_pedal_demo

Wave: 08. Session: 2026-11-13 pedal development. This is one newly dispatched
worker in the current sixty-assignment, ten-wave session.

## Scope and source basis

Owned only the new `examples/demos/pedal-phrase-v1/` directory,
`docs/PEDAL_DEMO.md` and this note. The original catalog/score, renderer, evidence
tools, core, CMake, shared status files and assignment manifest were not edited.
No staging, commit, push, SDK mutation or additional agent dispatch was performed.
Root owns integration and publication under [AGENTS.md](../../../AGENTS.md).

Read the standing instructions, active README/status/next steps/development-log
handoff, project plan, atlas review, dated console handoff and prior retained
console example. Read the pedal catalog/evidence contracts and producer,
verification and analyzer interfaces. Reread the complete extracted atlas text
for **PDF pages 139–144 and 447**: shared pedal source identity, literal repeated
and disconnected contact paths, explicitly unknown electrical values, proposed
capture gates and permission to implement named nominal console surrogates.
This focused rereading does not count as another complete-PDF assignment.

The existing accepted phrase supplies the exact settings. Its score SHA-256 is
`47daa264ca9524c98d7a189d28728778c9057852b8fd3d68e7fea9d2e63b9be5`.
There are 38 ordered score events. The original score/catalog were preserved,
including ideal contacts, percussion off, upper B `006400000`, lower B 8-foot
position six set by the score, pedal positions `32`, expression `0.75`, seed
2704, 48 kHz, 144,000 frames and nominal block size 127.

## Coherent published-source build

Used published commit `d7b886103f8c9d4649ffa1c35930b79808217a3d`, tree
`018c3897889aaae0070f632981e0c889a35cad30`. Created a fresh `git archive` in
`/workspace/scratch/f364bc93d920/a43-pedal-demo/source`. The raw archive SHA-256
is `cd12275adc2a32385c9b1c6f098a05a85b969e80e20ef3b5f7506c266e77d84c`.

All **474 committed file blobs** were checked against their Git blob identifiers
and SHA-256 values before compilation and again after audio generation. The
retained `source-blobs.json` is 124,311 bytes, SHA-256
`4b207c6ad747761442ab326b3fd683ecd48fbbf6b1eedea4a8de600b832b64e8`.
The coherent fresh build never linked later live headers to older libraries.
Root's checkpoint directories were read only and were not modified or used as
the build destination.

Executed:

```sh
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake \
  -S /workspace/scratch/f364bc93d920/a43-pedal-demo/source \
  -B /workspace/scratch/f364bc93d920/a43-pedal-demo/build \
  -DCMAKE_BUILD_TYPE=Release
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake \
  --build /workspace/scratch/f364bc93d920/a43-pedal-demo/build \
  --config Release --target hammond_render --parallel 2
```

Both commands exited zero. GCC 14.2.0, CMake 3.31.6 and Python 3.12.14 were
observed. The actual 17 translation-unit command records and source hashes are
retained in the demo's `provenance.json`, together with the linked core library
and generated pedal-header identities. Ordinary SDK-free Release defaults were
used. Make emitted an existing jobserver-FIFO diagnostic and then completed
all compilation/link steps successfully; it was not a build or test failure.

The 135,320-byte renderer SHA-256 is
`a0a33ffad00f01f82e3e25fb59b9225c0d4aa5655ce601fea3b81e2c8af9079e`.
The compiled profile remains 4,545 bytes, SHA-256
`b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.

## Actual render, verification and analysis

The producer used the source archive's `tools/render_fixture.py`, the fresh
renderer and the archive's unchanged authoring profile/phrase score. It wrote
directly to the new owned demo `bundle` directory, without rewriting any
producer-created artifact afterwards. Exact absolute argument arrays, tool
identities and successful return codes are retained in `provenance.json`.
The portable equivalent is:

```sh
python tools/render_fixture.py --renderer build/hammond_render \
  --profile-json data/profiles/nominal-unmeasured-v1.json \
  --events examples/fixtures/pedals/pedal-phrase-v1.events \
  --output-dir NEW_OUTPUT_DIRECTORY \
  --frames 144000 --sample-rate 48000 --block-size 127 --seed 2704 \
  --drawbars 006400000 --pedal-drawbars 32 --contacts ideal \
  --percussion off --percussion-volume normal --percussion-decay slow
python tools/verify_render.py NEW_OUTPUT_DIRECTORY
```

The producer and independent verifier both succeeded. The seven-file schema-3
bundle includes the untouched manifest, authoring/compiled profiles, score,
WAV and both raw logs. The verifier checked six payload artifacts plus the
manifest and reported `verified_retained_bundle`. The manifest SHA-256 is
`8cca3be0d5f451e9574590a211db748885062446674e46efb2a5e385027efb87`.
Its archive Git HEAD/dirty observations correctly remain unavailable. The
verifier's `source_build_association` and authentication remain
`not_established`; the separate observed local provenance does not alter that
verdict or claim cryptographic build authentication.

Two additional actual renderer invocations used the same retained compiled
profile/score, seed and controls with blocks **64 and 1024**. Both complete
WAVs matched the retained block-127 WAV exactly. The three calls rendered
432,000 stereo frames in total; the retained musical duration remains three
seconds. Temporary alternate WAVs are not included in the repository.

| Observation | Actual result |
| --- | --- |
| Retained WAV | 576,044 bytes; 144,000 stereo PCM16 frames at 48 kHz |
| WAV SHA-256 | `a3d1958189e811b8e353a75380d380016db5286eb08a2005626d95df64dde6f1` |
| PCM data SHA-256 | `3107d186bb811b2cf1a2a3497422f5d77169f92ca2c9c7f22a1553482141c77c` |
| Float peak | `0.08429475128650665`, below catalog bound `0.103` |
| Float RMS | `0.022980303816301697` |
| Clipped frames / channel samples | `0 / 0` |
| Independent whole-file PCM peak | `0.08428955078125` |
| Independent whole-file PCM RMS | `0.02298031808643901` |
| Channels / full-scale codes | Identical channels; zero endpoint codes |
| Leading / trailing silence | All 4,800 / 24,000 frames exactly zero on both channels |
| Alternate partitions | Complete WAV bytes identical at 64 / 127 / 1024 |

Seven actual `analyze_wav.py` executions retain JSON for the whole file,
`[0,4800)`, `[7200,30000)`, `[36000,58800)`, `[64800,87600)`,
`[93600,116400)` and `[120000,144000)`. Four chord windows are the accepted
catalog's stationary spans. The README presents their exact scope and rounded
readable metrics; JSON retains full precision. The windows overlap the whole
file and are not additional independent duration. No frequency declaration was
made for mixed harmonic audio. No subjective listening, normalization,
resampling, amplitude editing or post-processing was performed.

No render, verifier, analyzer or byte-comparison failure occurred. These were
actual focused artifact checks, not a newly executed full CTest/platform matrix.
Separate native platform repairs being handled by root do not establish a new
claim for this fixed offline-source example.

## Deliverables and next step

The demo directory retains the seven-file producer bundle, eight analysis/
verification reports, source inventory, explicit local build/provenance record
and practical README. `docs/PEDAL_DEMO.md` supplies a short entry point. The
README provides a recorded-source worktree/build/render recipe, a Windows
configuration-path adjustment, all score boundaries and meaningful evidence
limits. Its historical absolute paths are never presented as replay commands.

Root must explicitly include ignored `bundle/render.wav` and `bundle/profile.b3p`
when staging the completed directory; no worker staging was performed. The
files belong to the Git-backed project and were not separately duplicated to
another artifact store.

Assignment 44 owns independent replay/provenance/PCM acceptance and an automated
retained-demo gate. The bundle and analysis bytes were frozen and announced to
root before that review began. Root then integrates the demo, updates shared
navigation/status and publishes only after its coherent gate. Final source and
artifact hashes are sent with this worker's completion report.

Final hygiene checked all 17 generation-payload inventory entries against their
recorded sizes/hashes, all three owned Markdown files for trailing whitespace
and final newlines, and all 25 local Markdown links. All checks passed. The
current repository verifier was executed once more after documentation and
returned `verified_retained_bundle`, with the external renderer still `matched`.
The demo contains 18 files totaling 796,234 bytes; provenance excludes only its
own file from the recursive inventory. Both ignored WAV/profile paths were
confirmed explicitly for root's staging handoff.

This example establishes reproducible nominal software audio. Physical low-wheel
spectra, contact timing, reactor/loading response, calibrated pedal footage,
loaded expression, scanner/AO-28/Leslie processing, native DAW/device behavior,
deadline performance, subjective listening and specimen fidelity remain separate
gates. Preserve this example's named nominal identity when measured models are
introduced later.
