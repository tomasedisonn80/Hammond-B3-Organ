# Product numerical admission review

Actual worker **A48**, `/root/w08_a48_numerical_admission`, wave 8,
15 November 2026. Starting main was
`d556da017ea0a5d4f2d231416782dbc5066e58c2`; the integrator published unrelated
accepted product work as `d8c39f7986746eacc991747153c7dbb012bb9a32` during this
audit. The six numerical inputs below remained unchanged. Full AGENTS/PLAN,
the active checkpoint/assignments, A19/A28/A33 handoffs, and task-relevant
contracts, source and retained evidence were recovered before modification.

## Decision and scope

The retained native acceptance report is consistent with its declared numerical
budgets, experiment families and current six source identities. Its original
figure has matching report, source, binary and original-generator metadata.
**This audit found and repaired a narrower defect in admitting replacement
reports:** the plotter trusted incomplete provenance and contradictory successful
summaries. The accepted numerical result itself was not overturned.

Initial ownership covered this review, the short worker note and bounded report.
After receiving the three concrete counterexamples, the integrator explicitly
expanded ownership to the [plotter](../../tools/plot_crossover_characterization.py)
and [new regression module](../../tests/test_plot_crossover_characterization.py).
The circuit, native probe, reference, acceptance producer, frozen thresholds,
retained numerical report and PNG were not modified by A48.

The [A48 report](../development/2026-11-15-product-continuation/reports/A48-numerical-admission.json)
retains exact input hashes, original mutation recipes/digests, before/after
outcomes, metadata comparisons and unrun limits. Matching hashes and internally
consistent JSON do not authenticate invented observations or independently
attest compilation. Original execution evidence remains necessary.

## Original finding and repair

With the original plotter `fecd825b3736de148926544ebd74cf7adc6994d366666d0910929d62c592822c`,
each private mutated copy still admitted 24 plotted points:

| Mutation to the successful retained report | Original result | Repaired result |
| --- | --- | --- |
| Remove the native header, implementation, probe and acceptance-test hashes, retaining only reference and registry hashes | Admitted | Rejected: exact source set differs |
| Replace `binary_sha256` with JSON null | Admitted | Rejected: lowercase 64-digit SHA-256 required |
| Set `maximum_warped_response_error` to `1.0`, retaining `passed: true` | Admitted | Rejected: frozen `2e-10` budget exceeded |

Explicit `passed: false` and a present but stale native-source hash were already
rejected. The gap was incomplete admission, rather than failure to compare a
supplied hash. The repair now admits the complete v1 schema with strict scalar
types, six exact source paths and hashes, a syntactically valid binary identity,
the unchanged limits and research/provenance boundaries. It checks every
response/sine group, rejects missing/duplicate/unsupported experiments, verifies
bounded decay/warmup and metrics, and reconciles derived counts and maxima with
the summary. Nominal point metrics must also fit their retained same-Hz maxima
and the existing magnitude/phase/complex-error consistency relation.

JSON duplicate members, nonfinite numbers including exponent overflow, wrong
root/field shapes, malformed identities and reports larger than 1 MiB are
rejected before rendering. Bounded reading replaces an unbounded whole-file
read. The CLI retains its no-overwrite rule and refuses invalid input before
calling the renderer. This remains report admission for a characterization
tool; it does not repeat native acceptance or add a physical criterion.

## Confirmed retained numerical evidence

The [coherent report](../development/2026-11-15-product-continuation/reports/crossover-response-acceptance.json)
contains the complete Cartesian product of four rates and six resistor pairs:
44,100/48,000/96,000/192,000 Hz; `(16,16)`, `(1,1)`, `(1024,1024)`,
`(1,1024)`, `(1024,1)` and `(8,32)` ohm, ordered treble then bass.

| Retained quantity | Independently reconciled value |
| --- | --- |
| Response groups | 24, each with 130 frequencies |
| Response-port comparisons | `24 × 130 × 3 = 9,360` |
| Sine experiments | 96, four frequencies per rate/load pair |
| Sine-port comparisons | `96 × 3 fits × 3 ports = 864` |
| Producer processes | 153: 24 response + 96 sine + 33 refusal cases |
| Maximum warped response error | `2.0923475127225402e-13`, budget `2e-10` |
| Maximum warped sine error | `3.429777428091277e-13`, budget `2e-8` |
| Maximum response solve residual | `1.7554167342883506e-16`, budget `1e-12` |
| Maximum independent fitted startup bound | `4.014564579287608e-11`, admission ceiling `2e-10` |
| Maximum half-window gain difference | `6.064307873515581e-13`, budget `2e-8` |

These values were reconciled from retained groups and producer source; A48 did
not rerun the 153-process experiment. The response set contains **126 in-band
10–20,000 Hz points**: the independent reference's 124-point grid plus 5,000 and
10,000 Hz. DC, 1e-8 Hz and two near-Nyquist points bring each group to 130.
The integrator subsequently corrected the characterization's original
124-point-maxima wording. The figure contains only six checkpoints per rate;
neither those lines nor a finite-grid maximum establish a continuous envelope.

The numerical normalization is `abs(error)/max(1,abs(reference))`, separately
for V/V gains and A/V admittance. Its denominator is a numerical convention,
not a declared audibility or attenuated-port floor. The plot correctly restores
the denominator before labeling absolute error. Its 24 stored observations,
including all three ports, are unchanged after admission repair.

## Reference, probe and boundary consistency

Source inspection found the registry/reference/native contract consistent:
L2 A–H = 0.0032 H, L3 A–W = 0.0052 H, C16A H–B = 7.8 µF and
C16B W–B = 12.5 µF. Treble remains the floating A–H port; bass is W–B.
Default loads are ideal 16-ohm resistors. The imposed zero-source-impedance
fixture and eight explicitly null physical fields remain distinct. The
reference admits the exact ordered v1 topology, values, units, evidence and
types, rejects duplicate/nonfinite/malformed bounded registry JSON, and labels
its report as analog algebra with no atlas-byte verification or physical pass.
Existing negative fixtures and invalid-output-preservation paths were inspected.

The native probe consumes bounded CLI experiments, not historical reports.
Its strict parser, finite decimal checks, duplicate/inapplicable-option refusals
and delayed JSON emission preserve failure separation. Response admits
`0 <= f < fs/2`; sine admits `0 < f < fs/2`. Limits remain 512 response
frequencies, at least eight measured sine frames, and at most 16,777,216 total
sine frames. It reports actual processed right endpoints but does not claim
startup convergence; the independent producer supplies that bound.

The API/registry/guide agree on the four admitted rates, finite `[1,1024]`-ohm
loads, 4096-frame transactional block capacity, and computational ceilings of
64 V input, 65,536 V per capacitor, 256 A per inductor and 1e6 J stored energy.
These are not component ratings, clipping thresholds or measured operating
limits. The retained lifecycle/allocation work remains its own evidence;
this review does not requalify those tests or introduce an Engine route.

## Executed checks and exact identities

From `/workspace/scratch/5b7d983ac078/Hammond-B3-Organ`, Python 3.12.14:

```sh
python3 -B tests/test_plot_crossover_characterization.py -v
git diff --check -- tools/plot_crossover_characterization.py tests/test_plot_crossover_characterization.py
```

All **11 regression methods passed in 0.280 s**. They include the three original
counterexamples, missing/stale/extra identities, contradictory finite summaries,
strict types, complete experiment/count checks, inclusive budget boundaries,
decay/warmup bounds, malformed JSON and output-preserving CLI refusals. The
unchanged retained report and reordered complete group lists are positive
fixtures. No native process, new sweep or Matplotlib rendering ran. CMake's
existing `tests/test_*.py` discovery will register the new module after the
integrator's coordinated reconfigure; A48 did not operate the shared build.

| Input or delivered source | SHA-256 |
| --- | --- |
| Retained numerical report | `2773a6fa1b7b81292296d9c29e4677cd5dfe56921ce9e34ee6d126c3ce3269d8` |
| Registry | `f55fa98c246b4a19dce12ca829a141cff744f71242cccb68db12b404400319cc` |
| Native header | `54efff218f873045bd07a2eb3270d07637e3f3fc5d2d51bac032b7efca53559c` |
| Native implementation | `1a1bdde72af95709143afc4f62991c138ff3458cc78765fbe49a229d82693525` |
| Native probe source | `e9525de45f6df95c05785f50430a049e71fcd5299a00a6b95db11337b65dc475` |
| Independent reference | `33eaa88da2534e52f88c044b5fbabf19828655bacb357dc55bbeb6510b580ec5` |
| Native acceptance producer | `cf9d8e94e4b57a623fa7fcfaa91d50e81ad19818d151f7dc7f5a1ead69070f95` |
| Existing probe binary, read only | `da09640f7520cd887a836961658ed8a79d6b6bff28f0e33a0ce44cf76f992eac` |
| Repaired plotter | `3bc78b38516de384cf07e94b1cd9f33dbd71c0a6057b2012617814dfbd29ccf4` |
| New regression module | `dd7ff3d635c54e680594fd8af6771cfe2af66871570a0cd5b1cb9df28f50b360` |

At A48's pre-refresh inspection, the original PNG hash was
`6084be255054c1f11afdac26b3d8972721f9711598b13b30231ace69326bf39c`.
Its metadata correctly pinned the **original** plotter hash above. A48 checked
metadata/observation identity, not a new rendering or pixel comparison.
Subsequently, the integrator's separate
[refresh receipt](../development/2026-11-15-product-continuation/reports/crossover-plot-admission-refresh.json)
records exact equality of all decoded 1800×1230 RGBA pixels and only the
`Description.plotter_sha256` change. The current PNG SHA-256 is
`57bc9ff8fb5e6f12d84bf9d2cd726ca2dfdd4dff5d24de05e8b7da9e7569054c`.
The report and numerical inputs stayed unchanged; A48's original audit record
retains its pre-refresh identities. Read-only binary/hash agreement is not an
independent compiler/source-to-binary attestation.

## Next gate and limits

The [declared next M6 task](../NEXT_STEPS.md#next-dependency-ready-phase-after-session-closure)
remains to freeze an independently reviewed same-Hz electrical-accuracy protocol
**before** evaluating a separately identified numerical candidate. It must name
input hold/reconstruction, external rates, band, load family, signal boundaries
and independent check grid; justify gain floors and magnitude/phase budgets
above them; specify absolute complex V/V criteria below them and a separate A/V
input-admittance criterion. Present evidence supplies no measured or audible
threshold. Actual processed output, independently bounded precharged transients,
state-preserving rate changes, energy behavior, partition equivalence, rollback
and bounded allocation/runtime cost need candidate-specific acceptance.

Preserve v1 values and identities. A 48→192 kHz observation is not a tested
resampling pipeline, and 176.4 kHz is not an admitted v1 rate. Primary-drawing
verification, identified component/source/complex-driver measurements, coupled
M6 qualification and dry-organ validation remain separate prerequisites.
Scanner G5's same-Hz failure, independent R4 ownership, R5 audible policy and
R6 runtime/Engine integration remain open and unchanged.

No full characterization, native acceptance, shared configure/build/CTest,
platform/sanitizer/device/hardware test, physical/audible qualification, commit
or publication was performed by A48. The integrator owns coherent final-source
qualification and publication of this admission-only repair.
