# P1 timing outcome — independent admission

Reviewer **A44**, `/root/w08_a44`, wave 8, 17 November 2026 UTC.

**ADMIT the recorded pre-helper, pre-H1 batch as
`NO_INVESTIGATION_SIGNAL_IN_THIS_BATCH`, with its mandatory Flat witness gate
passed.** This admits descriptive results for the frozen four scenes. It
does not qualify performance of the later helper, H1 merge, integrated gallery
or combined publication. The [machine audit](../development/2026-11-16-console-completion/reports/A44-timing-outcome.json)
records 225 passing offline checks, original artifact hashes, every process,
exact statistics and limitations. A44 executed no build, native capture,
benchmark or test rerun.

## Frozen authority and retained failures

The [prospective admission](PERFORMANCE_PLATE_TIMING_PROTOCOL_ADMISSION.md)
authorizes corrected protocol SHA-256
`9b9cef5f2c1ea0d6900c90ef6df63da5c5f7f9aaca9a91505f5b94192e2aa8f6`
and runner `0a5b7a42…`. The original prospective-v1 protocol remains unexecuted.
Its first supplemental Flat capture failed the batching-hint assertion before
SDL initialization or painting: before exited 1, after remained unrun, and
zero timing samples resulted. The [failed receipt](../development/2026-11-16-console-completion/reports/p1-flat-witness-v1/report.json)
and complete streams retain their original hashes.

Independent source comparison confirms the runner correction removes only the
28-byte `SDL_RENDER_BATCHING` environment entry. Native code still sets and
reports hint `1`; binaries, CPU, sample counts, order and thresholds are unchanged.
Capture-v2 was separately admitted before execution. The original failed paired
comparison also remains failed; its later correction does not rewrite it.

The timed before executable is the genuine retained `9f8b2eff…`; candidate is
`5cf0d904…`. A44 directly compared all **3,756,168 bytes** of the original and
[reproduced before executable](../development/2026-11-16-console-completion/reports/p1-before-reproduction.json):
they match. The original painter object was **not retained**. The newly compiled
object and recorded link inputs supply supplemental reproducibility, without
recovering an original-object receipt or observing the historical compilation.
The capture-before executable uses that reconstructed object; the timed before
uses the genuine original.

## Batch integrity and independently recomputed results

The [retained batch](../development/2026-11-16-console-completion/reports/p1-timing-v1/report.json)
ran on 17 November, 04:20:48–04:30:12 UTC, with recorded wall duration
**564.590189 seconds**. Its exclusive claim follows independent admission and
precedes launch. Exactly eight processes followed canonical before/after,
minimum after/before, wide before/after and Flat after/before. Each reports
CPU-0 affinity, exit 0, complete stream EOFs, empty stderr and no truncation.
All process and batch bounds pass; no command remains unattempted.

All **1,507 prospective identities / 83,723,847 bytes** agree with both recorded
batch endpoints. The protocol and admission bring execution references to
1,509; all six fast identities also match around every process. This checks
historical endpoint records, not the subsequently changed live build, and
does not establish continuous monitoring. Root's quiet-interval statement and
host observations remain recorded; shared-host isolation is not established.

A44 independently parsed every stdout, retained all **2,400 integer samples**,
and recomputed minimum, maximum, median from sorted positions 150/151 and
nearest-rank p95 from position 285. Half-nanosecond medians remain exact.
Every supplied total summary agrees within its printing precision. Each process
has 30 warmups, 300 measured draws and a separate final fingerprint draw.
Paint and flush/present component samples are unavailable; their summaries
cannot be independently recomputed.

| Scene | Median before → after, ms | p95 before → after, ms | Screen |
| --- | --- | --- | --- |
| Canonical | 179.826282 → 185.499996 | 493.530628 → 471.078019 | No signal |
| Minimum active | 154.281369 → 161.6146045 | 407.865956 → 429.172327 | No signal |
| Wide | 290.183045 → 289.974812 | 684.644977 → 612.086931 | No signal |
| Flat control | 54.852951 → 42.5639765 | 140.093098 → 71.116109 | No signal |

The unchanged screen requires **strictly >2 ms AND strictly >15%** growth in
either total median or p95. Exact integer comparisons reproduce every decision.
Canonical median and minimum median/p95 exceed 2 ms, but their relative growth
is only 3.1551%, 4.7532% and 5.2239%. No samples were trimmed, pooled or replaced.

## Mandatory Flat gate and limits

A44 bounded and decompressed both [same-scene streams](../development/2026-11-16-console-completion/reports/p1-flat-witness-v2/report.json),
verified their hashes, directly compared all **6,293,408 RGBA bytes**, and
independently recomputed FNV-1a-64 `aa58ce2e68f71fbe`. Both timing Flat outputs
match it, layout `9ac2bac0db68cf6f`, dimensions and shared scene/renderer metadata.
The witnesses contain 331 paints and zero timing samples. Different-state
case-21 evidence cannot substitute for this witness; the unchanged timing
binary emits a fingerprint, not raw pixels. Batching metadata reads an SDL
hint, not the renderer's internal batching flag.

No causal attribution, equivalence, confidence interval, display smoothness,
audio deadline or full-domain performance follows. Literal whole-interface
1:1, native accessibility, physical/device acceptance and release exits remain
separate. Any future timing batch needs a separately reviewed prospective reason
and protocol; this review authorizes no additional executions.
