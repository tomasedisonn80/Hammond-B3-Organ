# A18 — Independent material timing

Assignment: A18, wave 3 of the waveform continuation's sixty actual assignments.
Agent: `/root/w03_a18_material_timing`.
Date: 14 November 2026.

## Owned deliverables and result

Owned only [the timing review](../../../reviews/WAVEFORM_MATERIAL_TIMING.md),
this note and [the compact actual report](../reports/a18-material-timing.json).
**PASS:** all four original paired cells complete with no combined p95
investigation trigger. Eight processes performed 240 warmup draws and retain
2,400 raw measured total-draw samples. No repeat was run, and no observation was
discarded. The review records full medians/p95, actual order, source/archive/
binary hashes, layout/pixel fingerprints, limitations and next actions.

| Cell | p95 before → after, ms | Change | Investigation |
| --- | ---: | ---: | --- |
| 1672×941 Dimensional | 123.804439 → 127.332737 | +2.8499%, +3.528298 ms | No |
| 1672×941 Flat | 34.040047 → 33.445460 | −1.7467%, −0.594587 ms | No |
| 1280×900 Dimensional | 96.372286 → 99.787933 | +3.5442%, +3.415647 ms | No |
| 960×700 Dimensional | 57.402260 → 54.519466 | −5.0221%, −2.882794 ms | No |

The criterion is growth strictly greater than **both 15% and 2 ms**. Every paired
layout fingerprint matches; reference Flat's final surface fingerprint also
matches. The largest percentage increase is 3.5442%. These observations qualify
this offscreen software-renderer fixture and do not assert a physical-device,
audio-deadline or literal reference-equality pass.

## Source, setup and actual work

Read `AGENTS.md`, the complete project plan and atlas evidence boundaries, current
session/checkpoint/assignments, current status/next steps/log, the UI timing
contract and the complete unchanged benchmark. Inspected the actual worktree
and preserved concurrent edits. HEAD was
`26ff2fbe66a50260bd7601cbfa54c1f5d35ff3a8`, tree
`530d5fcf777003f470f64558de9e5631d31a21a4`; the after source is the identified
uncommitted paint slice, not a claim that HEAD already contains it.

Before InstrumentView SHA-256 is
`428f74c4b2aae72e1ee048d1fa878575d0cd2edc064b1a3865ba40c446c30da2`,
matching both sibling `baseline-ui/InstrumentView-before.cpp` and HEAD. After is
`6570c97f1c62b555a1df3477954514e379d61165a36cf20f879dea5151ff866b`.
The unchanged benchmark SHA-256 is
`58f6c7e0a7d940c9732b955df3b659cc84f45f4a3ac1dbb21abcc3d42d05b43a`.

Compiled three isolated objects with GCC 14.2, C++20, `-O3 -DNDEBUG` and the
current strict native warnings; linked two binaries against exactly the same
current Drawing/support/core/SDL archives. All compilation/link steps passed
with empty stderr. Root's incremental build finished before linking; A16/A17
held CPU-heavy work and root deferred CTest throughout measurement. The actual
window was 22:15:39.924–22:18:41.249 UTC, with fixed CPU-0 affinity on the shared
Linux/AMD EPYC environment. No exclusive-host timing claim follows.

Ran `python3 /workspace/scratch/e3cacb90cc81/a18-material-timing/run_pairs.py`
from `/workspace/scratch/e3cacb90cc81/Hammond-B3-Organ`. Actual process order:
reference Dimensional before/after, reference Flat after/before, default
Dimensional before/after, minimum Dimensional after/before. Each unchanged
program performs 30 warmups + 300 samples using SDL 2.32.10's offscreen software
renderer, batching 1, scale 1, full viewport, no clip, Play and no overlay.
All eight processes returned zero with empty stderr. Recalculated every total
median/p95 from the actual raw samples; source/archive/shared input hashes
remained stable. No threshold-triggered repeat, production edit, dependency,
shared build/CMake change, manifest edit or commit was made by A18.

## Concrete handoff

The timing slice is ready for integration. The measurement window was closed
and announced to root/A16/A17 before their heavier work resumed. Root may proceed
with full renderer acceptance and, separately, coherent-source native gallery
qualification and README refresh. A15's 79-pair exact containment and 55-frame
portable acceptance are separate completed evidence, not rerun by A18. Preserve
source-specific observations and residual visual differences; numerical R4,
R5/R6, real devices and literal 1:1 equality remain distinct gates.
