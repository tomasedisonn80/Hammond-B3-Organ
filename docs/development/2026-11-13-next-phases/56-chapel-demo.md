# Assignment 56 — final-candidate chapel audition demonstration

Actual agent `/root/w10_a56_chapel_demo`, assignment **56/60**, wave **10**,
13 November 2026. The initial spawn response was interrupted, but this canonical
worker started once; no replacement worker is counted.

## Owned files and source basis

Owned only the ten files under
`examples/demos/standalone-chapel-v1/`,
[STANDALONE_CHAPEL_DEMO.md](../../reviews/STANDALONE_CHAPEL_DEMO.md), and this note.
The bundle contains `README.md`, `chapel-pair.b3controls`, `held-manuals.b3ui`,
`reference.png`, `reference.json`, `minimum.png`, `minimum.json`,
`provenance.json`, `manifest.json` and `verify_demo.py`.

Read standing instructions, current standalone scope/plan/handoff, app and
input-replay contracts, control format, chapel authoring/export data and the
earlier actual window demonstration. Reviewed the retained atlas consolidation;
this assignment does not claim an additional independent 500-page reading or
verification of primary Table IV. Relevant source boundaries remain atlas p122
documentary taps and pp391–444/450 adapter/UI goals. An initial oversized grouped
documentation read was truncated; relevant contracts were read again in smaller
complete chunks before capture.

## Exact executed work

The coordinator supplied published source
`0085e338388f2c7516a7d455f11692b94e9451f4`, equivalent local
`fa6df9d04916da8e23938cc3e85f524e3707e7d8`, exact tree
`19c763503f67e1f054d2d27b6ec3d8fca2e36474`. Assignment 55 reported its fresh
Release build completed before this worker used it read-only. All **894** source
Git blobs and executable modes were independently verified before/after capture.
The actual main compile metadata identifies GCC 14.2.0, Release `-O3 -DNDEBUG`,
C++20 and strict warnings. No new build or CTest suite was run by assignment 56.

From the repository root, the frozen exporter was executed with Python `-B`:

```sh
python3 -B /workspace/scratch/5ba97739b54c/a55-full-integration/source/tools/chapel_controls.py \
  --catalog /workspace/scratch/5ba97739b54c/a55-full-integration/release/chapel-catalog.json \
  --upper 'C#' --lower A --bank B --expression 0.5 \
  --output /workspace/scratch/5ba97739b54c/a56-chapel-demo/chapel-pair.b3controls
python3 /workspace/scratch/5ba97739b54c/a56-chapel-demo/capture.py
python3 examples/demos/standalone-chapel-v1/verify_demo.py
```

The private capture checker launches exactly two processes with explicit dummy
audio/video, software rendering and empty PATH. The bundle README spells out
their actual arguments and provides a portable reproduction recipe. Source,
build and earlier demonstration directories were never changed.

The exporter produced the independent **292-byte** complete state:
Upper C# `005320000`, Lower A `427866244`, sounding bank B, expression 0.5,
other banks zero, both routes on, pedals `00`, percussion Off/Second/Normal/Slow.
The **1400 ms / eight-action** replay selects Upper and presses A, selects Lower
and presses D, then returns future presses to Upper. Both actual runs observe
empty → Upper MIDI 60 → Upper 60 plus Lower MIDI 64, retain every control field,
accept exactly two On / zero Off commands, and acknowledge the final prefix at
sequence 3 before screenshot/shutdown. The original files remain byte-identical.

| Actual capture | Callbacks | Frames | Painted images | Result |
| --- | ---: | ---: | ---: | --- |
| 1280 × 900 reference | 130 | 66,560 | 34 | Exit 0; complete held endpoint, zero faults, joined empty state. |
| 960 × 700 minimum | 129 | 66,048 | 50 | Exit 0; same complete controls/holds, zero faults, joined empty state. |

Both use 48,000 Hz / 512-frame native float32 stereo. The one discarded command
per run is bounded normal automatic cleanup, after the scripted prefix is fully
acknowledged. No exporter or app failure, retry or relaxed expectation occurred.
The 2,598,768-byte executable retains SHA-256
`def97cef70b3eafcd108170a985c61215b878c918debde6ff2fb236a2a9c3416`.
The [review](../../reviews/STANDALONE_CHAPEL_DEMO.md) and
[provenance](../../../examples/demos/standalone-chapel-v1/provenance.json)
retain complete source/profile/catalog/image/diagnostic identities and actual
process timestamps, environment, durations and counters.

## Visual verification and handoff

Pillow 13.0.0 writes each PNG directly from the original decoded RGBA BMP;
mode, dimensions and every pixel byte compare equal. Both actual PNGs were
inspected directly. Drawbar values, bank selection, expression/percussion,
manual/pedal panels and status text fit without observed edge clipping or label
overlap. Independently selected literal pixel samples distinguish pictured
Upper C4 and Lower E4 from adjacent unheld white keys at both sizes. Small
minimum-size text still needs real-display usability evaluation.

The bundle's independent verifier checks all retained file identities,
state/script literals, musical snapshots/acknowledgments, final stopped/no-held
state and full decoded PNG pixels. Root owns shared accounting/status and final
publication. The existing window-v1 demonstration is unchanged.

The retained verifier's first execution passed on 14 November 2026 UTC with
**10 files / 165,762 bytes** and both capture records. Final executable/profile/
catalog hashes, Python syntax, whitespace and local Markdown links also passed.
The manifest SHA-256 is
`deca520a43d6aaf57e5ca3c5878c3e74bb67db6eb9ddb15298a547ca90f65293`.

Next: complete the exact-source integrator/hosted gates, then real desktop/DPI,
pointer capture, native accessibility and physical device/controller acceptance.
These software-renderer captures, documentary tap auditions and positive nominal
sample peaks do not establish audible hardware output, measured factory timbre,
latency/deadlines or physical fidelity.
