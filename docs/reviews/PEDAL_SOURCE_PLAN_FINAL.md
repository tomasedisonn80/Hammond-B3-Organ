# Source identity and next-model plan: independent final review

Owner: /root/w10_a56_source_plan_audit

Assignment 56 of 60, wave 10, 2026-11-13 pedal continuation.

The retained source and evidence identities pass this review. The
[remaining M3 and scanner contract](../M3_REMAINING_AND_SCANNER_GATE.md) agrees
with the actual atlas pages inspected here, and its proposed DC answers agree
with an independent exact-rational circuit solve. No correction to that contract
was needed. It is suitable for the next graph-admission and offline-oracle work;
this review does not qualify scanner DSP, close M3/M4, or establish an acquired
instrument response.

## 1. Review boundary and source identity

The comparison baseline is `b4fc61ccfcc59724f14fb0cee947ed7bb7142075`. The
published wave-8 checkpoint is `d601eb166ea3206748f8e012b20a463ff365c0b1`.
The separately qualified wave-8 source tree,
`5370890e32045a556cb61a88cdb1f04fb5a18f7e`, and its integration results remain
root's qualification record; this assignment did not repeat that CI run.

Read [the project plan](../PLAN.md), [standing instructions](../../AGENTS.md),
[the source manifest](../research/source-manifest.json), the complete scanner
contract, the coverage portions of the six fresh-reader notes, current pedal
handoff/demo material, and the earlier
[legacy identity](PEDAL_LEGACY_FINAL.md) and
[demo acceptance](PEDAL_DEMO_ACCEPTANCE.md) records. The independent checks below
are newly executed; earlier render and native-test observations are not claimed
as reruns.

| Identity checked | Actual observation |
| --- | --- |
| Original atlas | 500 pages from `pdfinfo`, 21,248,265 bytes; SHA-256 `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`. |
| Original source manifest | 809 bytes; SHA-256 `25ef38e97910ee80d6b1657dccd04553338601c36b9d5f4d24298e5ea8caa8f8`; byte-equal to the baseline. Its PDF size/hash/page count agree with the actual PDF. |
| Reviewed scanner contract | 32,743 bytes; SHA-256 `dcad3a8d65c3283188aeaae7f155599ede70375a38da782214fc9dc945e72fa4`; byte-equal to the published wave-8 copy. |
| Original authoring profile | SHA-256 `d17a266ed97cbbd3a2925ebebafafbd6c0e3f84763635732e0a9351d0eab2bff`; byte-equal to baseline. |
| Original pedal map | SHA-256 `58a30850c08933a075cfcec04faeb2cb479f60bd9dda82ace3246552221623bd`; byte-equal to baseline. |
| Factory Table III reference | SHA-256 `8c52ccca13653c6e379da33a10197bfc9ac1a1f3ab6bea6bbe8edf81f7a47b52`; byte-equal to baseline. |

Used `git ls-tree` to enumerate the baseline paths, then compared each live file
with its actual `git show <baseline>:<path>` bytes. All **57 original assets**
matched: the PDF, ten original data files excluding the deliberately extended
parameter registry, ten original fixture/catalog files, 34 retained rendered
artifacts and both `TonewheelBank` source/header files. The ten data files include
the original profile, pedal map, four manual/pedal reference CSVs, Table III
reference, profile schema, capture schema and planned-capture example. The source
manifest is an additional matched file, outside the 57.

This preserves the original fixtures and their historical schema-1/schema-2
bundles without rewriting their provenance. It does not by itself rerun their
audio regressions. The earlier legacy review's executed PCM results remain
separately attributed.

The source manifest still says the original companions were absent. Its missing
chapter JSON, catalog/license records, original transcriptions, capture/calibration
schemas, reference implementations, acceptance matrix and mission text have not
been relabeled as recovered originals. In particular, the atlas's references to
`025-scanner-network.json` and `scanner_ac_reference.py` do not make those missing
original companions available. The new plan correctly requires a labeled
reconstruction with separate provenance.

## 2. What full-atlas coverage means here

The current session has six distinct, complete wave-1 reader records. Their
manifest assignments, canonical owners, file identities and inclusive ranges
agree. Each note is byte-equal to its published wave-8 copy. Counting the claimed
ranges gives exactly **500 unique pages, zero missing pages and zero overlaps**.

| Assignment and note | Canonical owner | Claimed complete text range | Pages |
| --- | --- | --- | ---: |
| [01](../development/2026-11-13-pedals/01-atlas-foundations.md) | `/root/w01_a01_atlas_foundations` | 1-84 | 84 |
| [02](../development/2026-11-13-pedals/02-atlas-console.md) | `/root/w01_a02_atlas_console` | 85-168 | 84 |
| [03](../development/2026-11-13-pedals/03-atlas-electronics.md) | `/root/w01_a03_atlas_electronics` | 169-252 | 84 |
| [04](../development/2026-11-13-pedals/04-atlas-leslie.md) | `/root/w01_a04_atlas_leslie` | 253-336 | 84 |
| [05](../development/2026-11-13-pedals/05-atlas-product.md) | `/root/w01_a05_atlas_product` | 337-420 | 84 |
| [06](../development/2026-11-13-pedals/06-atlas-closure.md) | `/root/w01_a06_atlas_closure` | 421-500 | 80 |

The notes distinguish complete assigned text reading, selected rendered-page
inspection and external-source verification. Five print the PDF hash inline;
assignment 03 links the same preserved PDF and identifies the baseline instead.
Its lack of an inline hash is not a page-coverage gap. This is verification of
those retained records, not a claim that assignment 56 personally reread all 500
pages or independently observed every reader's work.

For this review, freshly extracted and read **20 actual PDF pages**: 110, 122,
143, 148, 157-159, 163-166, 169-171, 175-176 and 181-184. Rendered and visually
inspected **122, 158, 166, 170, 171 and 182**. The first combined image/text tool
response was truncated; its contents were not counted. The images and text were
subsequently opened in bounded, untruncated calls. Page numbers here are one-based
PDF pages, matching the printed atlas numbers.

## 3. Actual graph and source-page findings

[Atlas pp. 157-159](../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=157)
support the proposed nominal values and connected graph. The rendered page-158
diagram is decisive for connectivity: its first-six divider branch begins
**before** each inductor, while each capacitor follows that inductor. The diagram
also shows the shared return, chorus resistor and vibrato bypass. Text extraction
alone omits that detailed drawing.

| Graph item | Independently checked finding |
| --- | --- |
| Named nodes | Ground `g`, `p0` through `p18`, common return `r`, divider midpoints `d1` through `d6`: 27 named nodes. |
| Drive | Ideal source from `p0` to `g`; voltage polarity is positive at `p0`. |
| Inductors | `Lk: p(k-1) -> pk`, `k=1..18`, each 0.5 H. |
| Capacitors | `Ck: pk -> r`; `C1..C17 = 4e-9 F`, `C18 = 1e-9 F`. |
| Early dividers | `Rk+: p(k-1) -> dk`, `Rk-: dk -> r`, `k=1..6`. The positive-side values are 27, 56, 39, 33, 18 and 12 kilohms; the negative-side values are 68, 150, 150, 180, 180 and 180 kilohms. |
| Termination/return | `Rt: p18 -> r`, 15 kilohms; `Rc: r -> g`, 22 kilohms. Vibrato shorts `r` to `g`; chorus retains `Rc`. |
| Passive count | 18 inductors + 18 capacitors + 14 resistors = **50**. The ideal drive and switch are additional boundaries. |
| Signed outputs | `v1..v6 = V(d1..d6,g)`; `v7..v19 = V(p6..p18,g)`: **19 ground-referenced voltages**. |

The node names are a proposed graph namespace. Neither these names nor the
paper's tap labels establish factory wire colors, physical terminals or an
identified specimen. The graph has 18 LC sections, not 19 independent delay
buffers; [pp. 175 and 181-182](../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=175)
explicitly separate output count from the at-most-36 physical energy coordinates
and the algebraic unknowns. The actual independent state rank remains to be
established by the future solver.

The sign convention in the gate agrees with the viewed p. 182 equations: branch
incidence is positive at the declared positive endpoint, current injection is
positive into a node, and the inductor equation contains `-A_L^T v`. It retains
singular-descriptor handling rather than requiring an inverse of `E`. The patent
plate printed on p. 182 is explicitly an invention illustration; it does not
independently verify production connectivity.

## 4. Independent exact-rational DC check

A scratch Python checker independently transcribed the 50 edges and 19 output
pairs above from the viewed figure and printed values. It contracted the actual
18 inductor edges for DC, opened the capacitors, constrained `V(p0)=1` and
`V(g)=0`, and stamped every remaining resistor into nodal KCL equations. For
vibrato it also contracted `r` with `g`. It solved the six vibrato or seven chorus
unknowns using `fractions.Fraction` Gauss-Jordan elimination. It did **not** use
the gate's parallel-resistance or divider closed forms to obtain the solution.

All nodal KCL residuals are exactly zero as rationals. The first six normalized
outputs are:

| Output | Vibrato, exact | Chorus, exact | Chorus, decimal |
| --- | --- | --- | ---: |
| 1 | `68/95` | `12463311899/13657495547` | 0.912562032776038 |
| 2 | `75/103` | `12515270267/13657495547` | 0.916366417541985 |
| 3 | `50/63` | `12790466267/13657495547` | 0.936516231909704 |
| 4 | `60/71` | `13006519067/13657495547` | 0.952335589071966 |
| 5 | `10/11` | `146030693737/150232451017` | 0.972031626645534 |
| 6 | `15/16` | `13394885717/13657495547` | 0.980771743318805 |
| 7-19 | `1` each | `1` each | 1 |

Vibrato's return is zero. Chorus's return ratio is
`9455738267/13657495547 = 0.6923478931008726`.

Input current was calculated independently by summing the stamped resistor
currents leaving the driven node. The resulting input resistances are:

| Topology | Exact ohms | Decimal ohms |
| --- | --- | ---: |
| Vibrato | `92438660160000/9455738267` | 9775.932618884532 |
| Chorus | `300464902034000/9455738267` | 31775.932618884533 |

Their exact difference is 22,000 ohms. Every 12-decimal tap entry printed in the
plan rounds correctly: the maximum absolute rounding differences are
`2.1126760563380282e-13` for vibrato and `4.661243193993812e-13` for chorus, both
below half a unit in the twelfth decimal place. Repeating the solve with a -1 V
drive negated every signed output and return value exactly.

A deliberate mutation moved all six divider attachments to the **after-inductor**
nodes. It produced identical DC answers, because ideal inductors collapse those
nodes at DC. This confirms the plan's stated limitation: these answers cannot
qualify the finite-frequency endpoint graph. The next oracle must include
finite-frequency complex responses, loading sensitivity and independent source
comparison.

The separate uniform-LC arithmetic gives `sqrt(L*C) = 44.721359549995795`
microseconds, `sqrt(L/C) = 11180.339887498947` ohms and
`1/(pi*sqrt(L*C)) = 7117.62543417177` Hz. These agree with the gate's rounded
checks and with p. 159's scope. They omit finite-line loading, termination, coil
losses and the smaller final capacitor, so they are not measured delay or bandwidth.

## 5. Depth, rotor erratum and chorus reference

The viewed [page-170 table](../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=170)
agrees with all three proposed nine-entry, one-based maps:

| Mode pair | Selected ladder outputs |
| --- | --- |
| V1 / C1 | `1, 2, 3, 4, 5, 6, 7, 8, 9` |
| V2 / C2 | `1, 2, 3, 5, 7, 9, 11, 12, 13` |
| V3 / C3 | `1, 2, 4, 7, 10, 13, 16, 18, 19` |

The checker confirmed nine distinct indices in 1-19 for each map. These are
paper-specific nominal connections, not acquired specimen wiring. Pages 163-165
keep **16 physical positions**, **nine terminals** and **19 line outputs**
distinct, and label linear complementary weights as an unloaded approximation.
The 412 rpm description corresponds to `412/60` Hz; it is not a measured speed.

The rendered [page 166](../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf#page=166)
actually prints 15 entries, ending in `..., 4, 3, 2`, while the code multiplies
phase by 16 and takes indices modulo 16. The gate explicitly labels its added
final `1` as an **inferred correction**:

```text
0, 1, 2, 3, 4, 5, 6, 7, 8, 7, 6, 5, 4, 3, 2, 1
```

The corrected candidate has 16 entries; endpoints 0 and 8 occur once, each
interior terminal occurs twice, and every cyclic neighboring pair differs by one.
That matches the page's stated terminal-2-to-terminal-1 wrap. These consistency
checks do not independently establish the physical traversal. The primary-paper/
factory-mechanism comparison must still close the documentary gate before this
inference is promoted to verified wiring.

The viewed p. 171 derivation also agrees with the plan: with local voltage `z_k`
and return `r`, absolute output is `v_k = r + z_k`. A normalized weighted sum of
these absolute outputs includes `r` once. Another dry copy would duplicate that
contribution. A fixed 50:50 interpretation is therefore not a circuit identity.

## 6. Current evidence and compatibility are preserved

Compared the current parameter registry against the baseline's parsed records.
All **43 original parameter objects are exactly retained** as the first 43 of
45. Their canonical JSON-list SHA-256 is
`5e161206e203cce130330b993590d892182c4ead62daba50b468b5348d70bed2`.
The raw baseline registry is also byte-equal to
[the retained version-2 reference](../../data/references/parameter-registry-v2.json).
The current registry schema 3, `B3CONTROLS3`, render-bundle schema 3 and original
profile/capture schemas are separate version domains; the scanner plan does not
collapse or rewrite them.

Inspected the actual [Engine](../../src/Engine.cpp),
[control parser](../../src/ControlStateIO.cpp),
[parameter boundary](../../include/hammond/ParameterBridge.h) and
[native class IDs](../../plugins/vst3/PluginIds.h). The engine advances one source
frame before both pedal rendering and manual/percussion mixing. Its sustained
coefficients combine upper and lower routes before the source loop; it then adds
percussion and only a nonzero pedal contribution before gain/expression. The
plan correctly preserves that original disabled-scanner arithmetic rather than
assuming separately accumulated `U + L` will retain identical floating-point
results. The control parser admits versions 1/2/3 with explicit muted-pedal
migration for older versions. The proposed later scanner migration preserves all
existing IDs, thresholds and native UUIDs and defaults old states to both tablets
off. No scanner IDs or new state grammar are introduced by this review.

The proposed division routing agrees with actual atlas p. 169:

| Swell / Great | Scanner input | Direct material | Percussion |
| --- | --- | --- | --- |
| Off / Off | 0 | U + L + P | Q downstream |
| On / Off | U | L + P | Q downstream |
| Off / On | L + P | U | Q downstream |
| On / On | U + L + P | 0 | Q downstream |

These identities still need an explicit normalized-to-volts boundary. The plan
calls for one scanner history, continued rotor/source clocks, basis-signal
routing checks, preserved reactive energy on switching, and zero-frame control
flushes that do not advance clocks. Its zero-input/decaying-line behavior while
both tablets are off is explicitly a nominal integration policy, not a verified
factory connection. Existing allocation and transaction claims will require
scanner-enabled tests with nonzero stored energy before they can cover that path.

Also independently compared all **five pedal fixture/catalog files** and all
**18 demo files** with published wave 8. Every file matched. The demo provenance's
17 other-file byte counts/hashes matched the actual files and exact payload set.
All **474 source-inventory records** were checked against the actual Git tree
and `git cat-file --batch` contents: paths, modes, blob IDs, sizes and SHA-256
matched source commit `d7b886103f8c9d4649ffa1c35930b79808217a3d`, tree
`018c3897889aaae0070f632981e0c889a35cad30`.

The retained WAV remains SHA-256
`a3d1958189e811b8e353a75380d380016db5286eb08a2005626d95df64dde6f1`.
The inventory check establishes retained bytes and observed source lineage; it
does not establish a signed source-to-binary association. The demo's reported
`not_established` limit is preserved. This assignment did not replay or listen
to the demo and does not relabel its nominal mixtures as measured pedal spectra.

## 7. M3 scope, evidence labels and the next executable gate

The whole [M0-M9 plan](../PLAN.md) remains broader than the present nominal
console/pedal implementation. The atlas's research waves, the project's
implementation milestones and the user's agent waves are separate counts.
The new contract correctly keeps fixed presets/latches, loaded drawbar/expression
behavior, contact bandwidth, pedal electrical response and physical validation
open while making the next scanner data/numerical work concrete.

The additional M3 page checks support the plan's limits. Page 110 retains the
production transformer branches and documents the 1-ohm contact connection
without claiming a full loading model. The viewed p. 122 identifies the chapel
arrangement and 162 tap assignments; it still requires a second comparison to
the primary table. This review does not supply that independent primary-source
comparison. Page 143's 425 axis states plus 50 paired states are **475 proposed
captures**, not available recordings. Page 148 distinguishes controller position,
calibration and persistent expression-filter history. Page 165 requires the
changing-capacitance term in `d(C*v)/dt`.

The scanner plan honestly labels ideal coils/drive, negligible receiver loading,
linear rotor overlap, the inferred traversal, numerical tolerances and bypass
policy. Source/load impedance, winding loss, mutual coupling, overlap capacitance,
physical wiring and specimen applicability remain unknown where evidence is
missing. Its proposed numerical residual/parity limits are engineering acceptance
criteria, not executed results or manufacturer tolerances.

**Next action:** implement only the scanner authoring profile/schema/compiler and
independent endpoint-admission tests described in section 3 of the gate. Retain
all 50 components, 19 signed output pairs, SI/printed units, explicit unknowns,
source locators and reconstructed provenance. Independently consult the selected
primary circuit before closing graph admission. The existing dry engine, registry
and state format should remain untouched during that ticket.

The following gates are concrete and ordered: a separate AC reference with both
return states and all taps; a prepared line with rank/conditioning, energy and
state-migration checks; rotor/depth behavior after resolving the traversal
source; then opt-in engine/native routing and compatibility qualification.
The 20 Hz-20 kHz AC grid, refined null/resonance regions, phase floor, matched
bilinear-frequency comparison, input/load sensitivity and converged transient
reference prevent DC agreement from being mistaken for full numerical parity.
Capture records additionally require calibrated voltage/current scales, physical
clock uncertainty, synchronized references, loading, rights and frozen lineage/
holdout groups. No hardware gate is closed by a JSON-schema or synthetic test.

## 8. Reproduction and remaining limits

The assignment's [execution note](../development/2026-11-13-pedals/56-source-plan-audit.md)
records local command paths, audit hashes and corrected scratch-checker mistakes.
The exact-rational results above, explicit graph and solve method provide the
numerical anchors to reproduce in the later independent oracle. This review
creates no production schema, scanner code, controls or acquired capture record.

No original external paper/manual was independently acquired here, no full CI or
native host was rerun, and no physical instrument was measured. No timing,
real-time allocation, AC response, transient convergence, spectral sideband,
physical traversal or subjective fidelity pass is implied. The existing source
and evidence remain preserved, and the next work is precisely the graph and
oracle gate described above.
