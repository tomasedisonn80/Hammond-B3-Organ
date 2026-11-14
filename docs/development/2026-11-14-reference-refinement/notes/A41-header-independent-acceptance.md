# A41 — Independent wide-header acceptance

Actual worker `/root/w07_a41_header_independent_acceptance`, wave 7. **Accepted
the narrow Dimensional/sidebar header exception**, with the initial timing
threshold trigger retained. Owned only this note and `reports/A41-*`; no product,
author-test, CMake, workflow, README, commit or publication changes. Read AGENTS,
the complete M0–M9 plan, current scope/checkpoint, material addendum, layout,
A36 review and A25 procedure. A40 explicitly froze and released its work before
the isolated build; no shared build or live app was used by A41.

## Independently measured ink

Directly inspected the original reference, immutable v3 and both new fixed-state
reference/minimum-sidebar renders. The unchanged A36 mask is `R≥130, G≥105,
R≥G, B≤0.9R`, within named half-open regions; no resampling or registration.

| Ink at 1672×941 | Original reference | Original v3 / before painter | Final painter |
|---|---|---|---|
| Title | `[603,20,1067,53]`, 464×33 | `[617,28,1051,59]`, 434×31 | `[602,20,1065,53]`, 463×33 |
| Subtitle | `[650,71,1021,83]`, 371×12 | `[769,93,888,100]`, 119×7 | `[650,71,1020,83]`, 370×12 |

Both targets pass. Title top/height now match; width differs by one pixel.
Its ink center is 833.5 versus reference 835, inside the ±2 budget. Subtitle
center is 835 versus 835.5. The exact `NOMINAL DRY ORGAN` source has 17 characters
and retains all 15 nonspace ink runs. At 1400×820, final title/caption boxes are
`[466,20,929,53]` / `[514,71,884,83]`. Root confirmed the assignment’s old
subtitle x coordinates were a transcription error; original v3 bytes supplied
the corrected values above, without changing any target.

## Isolation and boundaries

The independent [probe](../reports/A41-raster-probe.cpp) passed **1,897 checks,
zero failures**, comparing **352,552,950 pixels**. Its 156 full-frame pairs cover
11 dimensions, all workspaces and both presentations at scales 1/1.25, including
both breakpoint axes, fractional 1400.25×820.25 and short/wide windows; minimum
sidebar and reference sizes also run at 1.5/2. All **120 Flat/non-sidebar pairs
are completely identical**. All 36 enabled pairs differ only inside the header.

Another 120 focused header-strip pairs preserve all ten common controls and
their two-pixel focus halos, with visible cyan. Twelve cut-clip/offset-viewport
pairs at all four scales have zero nonclear ink escape, including bounded
strips at logical width 8192. This is not full-frame 8192 acceptance. Renderer
state is preserved. Only four useful PNGs remain; transient raster RSS peaked
at 82,904 KiB. V1/v2/v3 galleries remain unchanged.

## One timing cell and its sole repeat

Each process used A25’s unchanged benchmark, 30 warmups/300 measured draws,
1672×941 Play/Dimensional/no-overlay, software RGBA32, batching, scale 1,
full viewport, no clip and verified CPU-0 affinity. Geometry fingerprints and
all renderer settings match. Values include paint, explicit flush and surface
present, excluding capture/I/O.

| Observation | Before median / p95 ms | Final median / p95 ms | p95 change |
|---|---|---|---|
| Initial, old then final | 106.769578 / 117.952085 | 106.520051 / 136.904572 | **+18.952487 ms / +16.067954%** |
| Sole reversed repeat | 108.147900 / 132.594383 | 107.107163 / 127.329805 | −5.264578 ms / −3.970438% |

The initial combined threshold trigger is preserved; it did not reproduce.
No cause or statistical equivalence is established. Native processes ran
21:45:15–21:46:27 and 21:47:33–21:48:46 UTC; all four exited zero. Observed
workers paused, but another checkout/virtual-host activity precludes exclusive
machine ownership. No additional timings ran.

## Identity and handoff

Baseline is `2e161dc3a60fc3442051799574feed37bffbfc5c`; observed build HEAD was
`f9c11a498ecd88886349415205fc5dccc627033e`. Final InstrumentView SHA-256 is
`f323c8c2f5529b03c25deccb74f482d8b6312487492a45d14b94ef0e24cfbb6a`;
its complete source outside `paint_header` equals baseline. GCC 14.2.0,
`-O3 -DNDEBUG`, SDL 2.32.10 and frozen A25 support archives were shared by
both isolated executables. The [build report](../reports/A41-build.json) retains
all commands, dependencies and full binary hashes: before `0b9acdc4…a21`,
final `15e008ae…2ab`, differential probe `d0ce63c7…e94`.

[Final acceptance](../reports/A41-final-acceptance.json) links the retained raw
timings, distributions, raster records and precise limits. The
[runner](../reports/A41-run-acceptance.py) supplies reproduction modes. Root owns
publication and fresh native gallery/README integration. Physical display/DPI,
accessibility, devices, audio deadlines and FPS remain unqualified. Other
control/material differences still prevent literal whole-interface 1:1 equality.
