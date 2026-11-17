# H1 pre-candidate paint timing admission

**A23, 17 November 2026: independently admit this bounded procedure before H1
paint. Measurements and candidate acceptance remain unrun.** The
[H1 contract](../design/HEADER_MATERIAL_H1_CONTRACT.md) requires representative
timing and rejects visible regression; it freezes no numeric timing allowance.
The [machine protocol](../development/2026-11-16-ui-delivery/reports/header-timing-protocol.json)
contains all twenty ordered commands and output names.

## Identity and quiet execution

Use genuine retained `../pre-header-native/hammond_standalone_paint_benchmark`
(SHA-256 `9f8b2eff710db91a1bb786e1093e6bf3c9df4f70160c76619447750db28a196f`)
and the coherently rebuilt current target. The immutable pre-H1 receipt hashes
to `eaf89814ff181b2c8559fccc00c1f001d25fa8d8a81d1021d38aca00530dc2d2`.
Require the separate timing identity receipt: the original 229-source inventory
does not include the benchmark. Retain benchmark/painter source, objects,
compile/link arguments, dependency/archive/generated-asset identities and both
executable hashes before and after measurement. Only the admitted H1 painter
may differ among paint inputs. Preserve the original receipt unchanged.

Root reserves a quiet interval after builds, CTest, captures and heavy worker
jobs finish. Run one process at a time on the same available logical CPU;
record affinity, host/kernel/CPU, configuration, relevant SDL settings, load and
UTC bounds. Shared-host isolation cannot be assumed. Use Release, unchanged
benchmark source, no heap observer, sanitizer or profiler. Initialization and
final pixel hashing stay outside measured intervals.

## Fixed matrix and commands

All cases use the existing `mixed-held` fixture, Play, overlay None, scale 1,
full viewport and no clip. This holds musical state fixed while varying H1
activity and extent.

| Order | Case | Arguments |
| --- | --- | --- |
| 1 | Canonical active | `1672 941 dimensional mixed-held` |
| 2 | Minimum active | `1400 820 dimensional mixed-held` |
| 3 | Wide active | `1920 1080 dimensional mixed-held` |
| 4 | Compact inactive | `960 700 dimensional mixed-held` |
| 5 | Flat inactive | `1672 941 flat mixed-held` |

From the repository, the canonical commands are:

```sh
../pre-header-native/hammond_standalone_paint_benchmark 1672 941 dimensional mixed-held
../build-native/apps/standalone/hammond_standalone_paint_benchmark 1672 941 dimensional mixed-held
```

Block 1 visits cases 1–5, before then after. Block 2 visits cases 5–1, after then
before. Each process supplies **30 warmups and 300 measurements**: twenty
processes, 6,000 measured draws, 600 samples per side/case. Preserve stdout,
stderr, exits and command order. Require `paired:false`, `before:null` and
`alternating_order:false`; order reversal occurs between genuine executables.
Require matching renderer/state/layout metadata, stable repeated pixel hashes,
and equal before/after pixels for both inactive controls. The H1 raster
comparator remains the stronger containment/state oracle.

## Aggregation and decisions

Independently recalculate each total median from sorted positions 150/151 and
nearest-rank p95 from 285. Also report pooled per-side/case 600-sample median
(300/301) and p95(570), every block delta, and supplied paint/flush summaries.
Never pool different cases, trim samples or replace a failed block with a repeat.
Separate-process samples are not frame-paired observations.

The existing benchmark investigates median growth **strictly over 2 ms AND 15%**;
[earlier material contracts](../REFERENCE_REFINEMENT_MATERIALS.md) apply that
conjunction to p95. Prospectively apply both screens to each block and pooled
case. Any trigger holds timing admission for investigation; persistent active
growth with stable inactive controls rejects the scoped timing result. A
one-block signal remains inconclusive. Identity/metadata mismatch invalidates
comparison; visible performance regression rejects H1 regardless of numbers.
Retain every failure; further repetitions need a separately reviewed reason.

These are software paint/flush/offscreen-present observations. SDL may flush
inside paint. They establish neither display smoothness/FPS, input latency,
audio deadlines nor scaled/maximal-domain performance. Full-frame appearance,
real display/DPI journeys and literal whole-interface 1:1 remain separate gates.
