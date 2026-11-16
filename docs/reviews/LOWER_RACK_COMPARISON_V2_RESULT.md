# Lower-rack comparison v2 — independent checker result

**A24 result: the separately versioned v2 software comparison passes all 98
pairs. The original v1 result remains failed.** The candidate passes all35 v2
material inequalities, and all150 excluded border pixels plus16 descriptive
focus pixels preserve both exact RGBA equality and their expected source colors.
This result supplies the versioned checker evidence required by
[A22's admission](LOWER_RACK_MATERIAL_V2_ADMISSION.md). Root owns integrated L1
acceptance. Literal whole-interface **1:1 remains unmet and unwaived**.

Worker `/root/w04_a24` implemented the extension only after A22 wrote its exact
hash admission. Read the full standing `AGENTS.md`, M0–M9 plan, frozen Lower v1
contract and v2 amendment, A16 implementation review, A17 note, complete checker,
immutable comparator snapshot and original failed report. No production painter,
fixture, material constant, grain seed, support, threshold or native binary was
changed by this work. The complete executable results are in the
[v2 report](../development/2026-11-16-conversion-material/reports/A24-v2-comparison/report.json)
and [compact receipt](../development/2026-11-16-conversion-material/reports/A24-result-summary.json).

## Explicit versioning and preserved original evidence

[`compare_lower_rack_material.py`](../../tools/compare_lower_rack_material.py)
continues to select `lower-rack-material-v1` by default. The new comparison must
explicitly request `--protocol lower-rack-material-v2`. Unknown versions are
refused. The native fixture still reports its original v1 protocol because its
32 inputs, metadata and rendering are unchanged.

The new checker retains the original `before_statistics`, `after_statistics`
and both `*_reference_screens` records. All ten original patches and every one
of the35 original inequalities remain visible for the genuine before and
candidate. The original combined result is retained as `v1_passed` per case
and `retained_v1_result.status = "failed"`. Corrected metrics occupy the separate
case `v2` object and top-level `reference_statistics_v2`/`v2_result` objects.
Top-level status grades the explicitly selected protocol and all98 preservation
obligations; a canonical material pass alone cannot pass the complete report.

Before accepting v2 inputs, the checker verifies the exact amendment, A22
admission, original A17 report, original mask and immutable v1 comparator hashes.
It verifies all five original failure PNGs in their original directory. No
original report, image or snapshot was rewritten, and successful v2 execution
does not duplicate the old failure images. The new run requires every original
case fact to reproduce exactly, including complete header and RGBA hashes,
per-row differences, child/focus results, all original statistics, every original
inequality and the failed v1 case. Original reference, inventories, native
results and aggregate totals must also reproduce.

The source-derived mask retains its original operation model and fixture
protocol; its additional `comparison_protocol` and admission bindings identify
the selected v2 measurement. All original mask fields except its timestamp and
run identities equal the immutable A17 declaration. It is written and fsynced
before any paired pixel stream. No observed delta is used to expand support.

## Admitted sampling and added foreground guards

Only the three right sample rectangles differ. They exclude the source-derived
last-slot border column x1094 while preserving their original right edge,
y positions and heights. Reference, genuine-before and candidate statistics
are recomputed from unresampled pixels at all ten v2 rectangles.

| Sample | Original v1 `(x,y,w,h)` | Admitted v2 `(x,y,w,h)` |
| --- | --- | --- |
| right | `(1094,320,14,128)` | `(1095,320,13,128)` |
| right_top | `(1094,298,14,14)` | `(1095,298,13,14)` |
| right_bottom | `(1094,460,14,20)` | `(1095,460,13,20)` |

All seven other rectangles and all35 numerical limits are unchanged. The exact
v1 threshold function is reused without modification: means and slopes compare
rational values, and population residual RMS uses the same exact radical
inequality. The selfcheck confirms that36 original functions, including every
mask, foreground, statistics, threshold and source-identity helper, are
unchanged; only original `compare_case` and `main` gained version handling.

| Additional canonical case28 guard | Pixels | Required source RGBA | Measured result |
| --- | ---: | --- | --- |
| Last-slot border: x1094, y311–460 | 150 | `[36,34,30,255]` | All150 exact before/candidate and source color; zero changed channels |
| Descriptive focus: x855–856, y492–499 | 16 | `[165,228,223,255]` | All16 exact before/candidate and source color; zero changed channels |

The full150-pixel border guard includes the20 border pixels outside the original
primary samples. Equality alone is insufficient: equal but wrong colors on both
sides fail. The unchanged middle-bottom descriptive sample `(852,492,14,8)`
retains all112 raw pixels and explicitly records16 source-focus pixels. It is
not a pure-material sample and is not a numerical acceptance patch.

## Executed result

The full run returned **exit0 / passed** in **88.5958866300025 seconds**, with
no process, metadata or source-stability errors. Comparison output totals
**3,808,477 bytes**, below the unchanged80 MiB cap. No native compilation or
dependency installation was needed.

| Measurement | Observed outcome |
| --- | --- |
| Explicit v2 combined cases | **98/98 pass** |
| Original preservation obligations | **98/98 pass**, 313,612,634 compared pixels |
| Protected output | 303,580,749 pixels; **zero escaping pixels or channels** |
| Required full-frame equality | **37/37 exact** |
| Active/nonempty allowances | 70 active cases, 61 nonempty allowances; every nonempty allowance has a visible change |
| Candidate changes | 4,985,696 pixels, 14,225,129 channels; identical to A17 |
| Independent opaque foreground probes | **252 probes / 142,099 pixels exact**; minimum111 pixels |
| Independent cyan focus preservation | **25,508 pixels exact**; minimum412 per full-frame case |
| Both ordinary native Lower suites | Each passes32 cases, 58,957,343 checks, 51 state restorations, 15 clip companions, 826 glyphs, 14 focus cases and two case28 repeats |
| Retained v1 before / candidate material screens | **7/35 / 33/35**; original overall v1 remains **failed, 97/98** |
| Separate v2 before / candidate material screens | **6/35 / 35/35** |
| New border and focus guards | **150/150 + 16/16**, exact pair equality and expected source RGBA |

The two original v1 candidate failures remain explicit:

| Original right-strip comparison | Absolute error | Unchanged maximum | V1 outcome |
| --- | ---: | ---: | --- |
| Y′ residual RMS | 1.865211887973828 | 0.50 | Failed |
| Horizontal Y′ slope/pixel | `3026571/8320000` = 0.3637705528846154 | 0.060 | Failed |

Selected corrected v2 comparisons illustrate the sampling result; the report
contains all35 rows and their exact rational sufficient statistics.

| V2 comparison | Reference | Candidate | Absolute error | Maximum |
| --- | ---: | ---: | ---: | ---: |
| Corrected right mean Y′ | 20.49218846153846 | 20.52277848557692 | 0.03059002403846154 | 2.5 |
| Corrected right Y′ residual RMS | 1.4651208997940872 | 1.5931857180553533 | 0.12806481826126603 | 0.50 |
| Corrected right horizontal Y′ slope | −0.11455879120879121 | −0.13226671531593406 | `158663/8960000` | 0.060 |
| Corrected right vertical Y′ slope | −0.02941216387531165 | −0.03267268080127618 | 0.003260516925964532 | 0.025 |
| Corrected right-minus-left mean Y′ | −7.437564576655983 | −7.365702938034188 | 0.07186163862179487 | 1.75 |

## Targeted negative checks

The [selfcheck source](../development/2026-11-16-conversion-material/reports/A24-checker-selfcheck.py)
and [receipt](../development/2026-11-16-conversion-material/reports/A24-checker-selfcheck.json)
record **116 successful checks**. Each of the35 numerical limits accepts its
exact boundary and rejects an infinitesimal over-boundary value. Tests reject
wrong sample rectangles, reused v1 reference samples, altered border/focus RGB
and alpha, before-only corruption, equal-but-wrong colors, resized/non-RGBA
guard inputs, changed painter/binary identities, widened mask support, a
tampered original report, altered retained thresholds and a fabricated v1 pass.
Unsupported versions and existing output directories are refused without
creating or overwriting results.

One genuine canonical capture pair is also evaluated with the frozen checker,
the new implicit v1, explicit v1 and explicit v2. Both v1 routes retain exactly
the frozen case facts, failure and all five PNG payload hashes. Explicit v2
passes while preserving the failed v1 result and all original records. Those
temporary duplicate test images were deleted; original A17 evidence remains.
The full98-pair run above is separate from that canonical regression check.

## Reproduction and source binding

Exact commands from the repository root:

```sh
python3 -B docs/development/2026-11-16-conversion-material/reports/A24-checker-selfcheck.py \
  --output docs/development/2026-11-16-conversion-material/reports/A24-checker-selfcheck.json

python3 -B tools/compare_lower_rack_material.py \
  --protocol lower-rack-material-v2 \
  --before-percussion ../baseline/test_standalone_percussion_raster \
  --after-percussion ../build-native/apps/standalone/test_standalone_percussion_raster \
  --before-lower ../baseline/test_standalone_lower_rack_material_raster \
  --after-lower ../build-native/apps/standalone/test_standalone_lower_rack_material_raster \
  --before-painter ../baseline/InstrumentView.cpp \
  --build-dir ../build-native \
  --output-dir docs/development/2026-11-16-conversion-material/reports/A24-v2-comparison \
  > docs/development/2026-11-16-conversion-material/reports/A24-v2-run.log 2>&1
```

These paths now contain immutable evidence; a repeat must use fresh output and
log names. The checker refuses an existing output directory. Root froze HEAD,
native sources, executables and build inputs across both verification runs.
Observed HEAD was `a411268fd498f65c083203137831bf5afed83bd8`; all four executable
payloads, every A17 source hash, reference, genuine-before painter and receipt
match A17. The current painter remains
`45b710a9c207f456701732f55ec1086487d63bdb9a8b6ed995f4de12cd5bdb10`.
The Lower fixture remains
`281df1de3edce6a91a851d0b5674677646f1741fac1512f474ea7ffda67350e7`.

Root's earlier unrelated installer reconfiguration changed `build.ninja` from
the A17 receipt. The new report binds its current hash
`9ce835b2628f1e40b18b59e64038f4e4948bc3fb35cd5910ec374458aa781dc0`
and confirms stability throughout execution. CMake cache, generated reference
art and SDL contents remain identical to A17. Hash matching supplies source and
executable identity; root retains responsibility for coherent build evidence.

| Evidence | SHA-256 |
| --- | --- |
| Exact admitted amendment | `b2ebad8944a31ac6e631f457507017dfac1c6191c721fb961c7adafe9b659695` |
| A22 independent admission | `6800031150e7a37335f32c6613471998c1acd3ff0c173c7a210e4514c0ab644b` |
| Extended comparator | `34a8ce6f68625a528aca749c8913e2aff2cb25d82b9d65a69c874aca5c04e4e4` |
| Complete v2 report | `0f9bece7e5ab0fb23eae5823c07c07bc65c570f6f180912dcf6d8c4d2a16402a` |
| Predeclared v2 run mask | `48ee74e075ee89a12f35cb954630345138a635e1700b1dc0ed3ff83846563f44` |
| A24 selfcheck result | `aacf3bfdef35b351e8ecb79770e8be74190c7ea02abaa519620d4d2fd6d1e8fd` |
| Retained failed original v1 report | `1db2294e250a36aa73d0a354b264656eff3d1e5f292628bc2c7c28e560b623ed` |
| Immutable original v1 comparator | `2c21521211555adc1076c258a8c1659549ad7f1c0f2bccdc2ce160fa6485554f` |

## Limits and next owner

This is exact software containment, state/foreground preservation and local
material measurement. Resource cases expose64×64 output with zero protected
exterior pixels and make no whole-window containment claim. Actual visual
judgment belongs to [A16's implementation review](LOWER_RACK_IMPLEMENTATION_REVIEW.md)
and the separately source-qualified
[actual-app gallery](../../examples/demos/lower-rack-material-v2/README.md);
A24 did not perform a new gallery visual admission.

Root should combine these explicit v2 results with those visual/source records
and coherent affected native gates before accepting scoped L1. Retain the v1
failure after acceptance. Then qualify the accepted painter as a genuine
next-stage baseline before typography work. The warm lower reflection,
mixed-footage typography and other whole-interface residuals remain open.
Real display/DPI/input, semantic accessibility, hosted/platform acceptance,
physical calibration and audio fidelity are not established by this report.
