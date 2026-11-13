# Primary scanner source review

Date: 2026-11-13. Assignment 10/60, wave 2/10. Scope: independently compare
the published late-B3 circuit and scanner geometry with the atlas reconstruction;
this is documentary review, not a runtime or specimen acceptance result.

## Sources and actual coverage

The primary source is Kurt James Werner, W. Ross Dunkel and François G. Germain,
**A Computational Model of the Hammond Organ Vibrato/Chorus using Wave Digital
Filters**, DAFx-16 (2016), printed pages DAFX-271–278.
[Publisher PDF](https://dafx.de/paper-archive/2016/dafxpapers/38-DAFx-16_paper_54-PN.pdf).
The supplied download was independently hashed and read in full: 8 PDF pages,
1,471,656 bytes, SHA-256
`ccdace0e88d456d7d80cd3b675a0936ab1313680f5b2dda0ba33445df0caae83`.
It was not added to this repository.

| PDF pages | Material read |
| --- | --- |
| 1–2 / DAFX-271–272 | Scope, prior approaches, full circuit, partition, component table, depth table, stage-count prose and scanner construction |
| 3–4 / DAFX-273–274 | Scanner weight model, terminal gain plot, output references, WDF tree and multiple-element root formulation |
| 5–6 / DAFX-275–276 | Root application, source/switch relations, frequency-warped discretization, leaf relations and polarity handling |
| 7–8 / DAFX-277–278 | Published simulations, response plots, conclusions and references |

Text extraction covered all eight pages. Fresh 2200-pixel renders of PDF pages
2 and 3 were visually inspected, including Figures 1–3 and Tables 1–2. Thus the
circuit and rotor conclusions below do not rely on text extraction alone.
The remaining primary pages were read as extracted text; their plots were not
independently digitized or reproduced.

The preserved [atlas](../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf) hash was
also freshly checked:
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
Atlas pp. 157, 158, 166, 170 and 182 were freshly rendered at 1800 pixels and
visually inspected; pp. 157–158, 163–164, 170 and 182 were read as extracted
text. No claim of rereading all 500 atlas pages is made for this assignment.

Compared fixture:
[atlas-late-b3-nominal-v1.json](../../data/scanner/atlas-late-b3-nominal-v1.json),
model `atlas-late-b3-nominal-line-v1`, SHA-256
`1d236be5e6b63e938a9f147808386173949d167e09aee8e902c55002e4ea4604`.
This is the newly reconstructed fixture, not the atlas's absent original
companion graph. Review baseline HEAD was
`6dc0702d5473912268e8af8f852b9b9984198ef3`; the fixture was an uncommitted
session addition, so its separate hash identifies what was actually reviewed.

## Complete component comparison

The paper's Figure 1, Figure 2 and Table 1 (PDF p. 2 / DAFX-272) agree with
atlas pp. 157–158 and the divider attachment clarification on p. 182. The
following names are the repository's explicit node vocabulary: `g` is the
source/receiver ground, `r` the common line return, `p0` the source positive
node, `p1`–`p18` the post-inductor nodes, and `d1`–`d6` the divider midpoints.
Endpoint order declares a mathematical branch orientation; it does not imply
physical polarity markings on the passive parts.

Every row below matched the fixture. There are **18 inductors, 18 capacitors
and 14 resistors: 50 passive components across 27 named nodes**. The ideal
voltage source and return switch are separate boundary elements.

| Inductor | Endpoints | Nominal | Capacitor | Endpoints | Nominal |
| --- | --- | --- | --- | --- | --- |
| L1 | p0 → p1 | 500 mH | C1 | p1 → r | 0.004 µF |
| L2 | p1 → p2 | 500 mH | C2 | p2 → r | 0.004 µF |
| L3 | p2 → p3 | 500 mH | C3 | p3 → r | 0.004 µF |
| L4 | p3 → p4 | 500 mH | C4 | p4 → r | 0.004 µF |
| L5 | p4 → p5 | 500 mH | C5 | p5 → r | 0.004 µF |
| L6 | p5 → p6 | 500 mH | C6 | p6 → r | 0.004 µF |
| L7 | p6 → p7 | 500 mH | C7 | p7 → r | 0.004 µF |
| L8 | p7 → p8 | 500 mH | C8 | p8 → r | 0.004 µF |
| L9 | p8 → p9 | 500 mH | C9 | p9 → r | 0.004 µF |
| L10 | p9 → p10 | 500 mH | C10 | p10 → r | 0.004 µF |
| L11 | p10 → p11 | 500 mH | C11 | p11 → r | 0.004 µF |
| L12 | p11 → p12 | 500 mH | C12 | p12 → r | 0.004 µF |
| L13 | p12 → p13 | 500 mH | C13 | p13 → r | 0.004 µF |
| L14 | p13 → p14 | 500 mH | C14 | p14 → r | 0.004 µF |
| L15 | p14 → p15 | 500 mH | C15 | p15 → r | 0.004 µF |
| L16 | p15 → p16 | 500 mH | C16 | p16 → r | 0.004 µF |
| L17 | p16 → p17 | 500 mH | C17 | p17 → r | 0.004 µF |
| L18 | p17 → p18 | 500 mH | C18 | p18 → r | 0.001 µF |

SI conversions are 0.5 H for each inductor, 4e-9 F for C1–C17 and 1e-9 F
for C18. In particular, there is no C19 or L19.

| Resistor | Endpoints | Published nominal | SI value |
| --- | --- | --- | --- |
| R1+ | p0 → d1 | 27 kΩ | 27000 Ω |
| R1− | d1 → r | 68 kΩ | 68000 Ω |
| R2+ | p1 → d2 | 56 kΩ | 56000 Ω |
| R2− | d2 → r | 0.15 MΩ | 150000 Ω |
| R3+ | p2 → d3 | 39 kΩ | 39000 Ω |
| R3− | d3 → r | 0.15 MΩ | 150000 Ω |
| R4+ | p3 → d4 | 33 kΩ | 33000 Ω |
| R4− | d4 → r | 0.18 MΩ | 180000 Ω |
| R5+ | p4 → d5 | 18 kΩ | 18000 Ω |
| R5− | d5 → r | 0.18 MΩ | 180000 Ω |
| R6+ | p5 → d6 | 12 kΩ | 12000 Ω |
| R6− | d6 → r | 0.18 MΩ | 180000 Ω |
| Rc | r → g | 22 kΩ | 22000 Ω |
| Rt | p18 → r | 15 kΩ | 15000 Ω |

The six divider branches attach **before** their respective inductors. Their
lower arms, all capacitors and Rt return to `r`; they do not individually
return to `g` in chorus mode. Figure 1 explicitly marks the `r`–`g` switch
closed for vibrato and open for chorus. The fixture's ideal `Vin` acts between
`p0` and `g`; its closed-switch node contraction preserves the drawn ideal
short without inventing a finite resistance. These observations agree with
atlas pp. 158/182 and the fixture's `drive` and `return_switch` records.

## All nineteen output references

Figure 1 places the first six outputs at divider midpoints, then thirteen
outputs at `p6`–`p18`. Equations 1–3 on PDF p. 3 / DAFX-273 reconstruct each
output by adding the common-return voltage to its local line voltage. Thus
the observable is relative to source/receiver ground, matching atlas p. 158.
The complete fixture mapping is:

| Output | Positive node | Negative reference |
| --- | --- | --- |
| v1 | d1 | g |
| v2 | d2 | g |
| v3 | d3 | g |
| v4 | d4 | g |
| v5 | d5 | g |
| v6 | d6 | g |
| v7 | p6 | g |
| v8 | p7 | g |
| v9 | p8 | g |
| v10 | p9 | g |
| v11 | p10 | g |
| v12 | p11 | g |
| v13 | p12 | g |
| v14 | p13 | g |
| v15 | p14 | g |
| v16 | p15 | g |
| v17 | p16 | g |
| v18 | p17 | g |
| v19 | p18 | g |

All 19 records matched. Ground-relative outputs already contain the return
contribution once; this comparison does not justify adding another dry signal.
The unloaded probes are an explicitly simplified boundary, not evidence that
the actual scanner and recovery stage have infinite input impedance.

## Depth maps and sixteen-position traversal

Paper Table 2 (PDF p. 2 / DAFX-272) and atlas p. 170 agree in every entry:

| Mode pair | t1 through t9 select these one-based output indices |
| --- | --- |
| V1 / C1 | 1, 2, 3, 4, 5, 6, 7, 8, 9 |
| V2 / C2 | 1, 2, 3, 5, 7, 9, 11, 12, 13 |
| V3 / C3 | 1, 2, 4, 7, 10, 13, 16, 18, 19 |

These are three depth connection maps shared by their V/C pairs, separately
from the return-switch state. The reviewed line fixture does not itself encode
depth or rotor arrays; this paragraph compares the primary paper with the
atlas, not a nonexistent JSON field.

**The original paper independently corroborates the sixteen-position cyclic
terminal traversal for its simplified model.** Following the connections
around Figure 1's sixteen stator positions, starting at terminal 1, gives
`t1,t2,t3,t4,t5,t6,t7,t8,t9,t8,t7,t6,t5,t4,t3,t2`.
Figure 3 (PDF p. 3 / DAFX-273) separately shows terminal 1 and terminal 9
reaching their maxima once per rotation and terminals 2–8 twice. Their
adjacent triangular weights produce the same cycle. The corresponding
zero-based order is:

```text
[0,1,2,3,4,5,6,7,8,7,6,5,4,3,2,1]
```

This supplies primary documentary support for the trailing `1` missing from
atlas p. 166; [E01](ERRATA.md#e01--scanner-traversal-has-15-entries-for-16-positions)
retains the original printed mismatch. It is support for the paper's model,
not independently recovered factory assembly wiring.

**Phase origin must remain explicit.** Figure 3 places the terminal-1 peak at
θ = π/8 and the terminal-9 peak at θ = 9π/8. At its plotted θ = 0, terminal
2 is active on the return toward terminal 1. Atlas p. 166 instead chooses
zero angle at terminal 1. For the illustrated increasing-angle traversal,
the correspondence is
`theta_paper = (2*pi*phase_repo + pi/8) modulo 2*pi`.
This one-sixteenth-turn shift is a coordinate choice, not a measured rotor
alignment. Figure 1's arrow depicts clockwise rotation; no selected specimen's
viewing direction, absolute phase or rotation alignment was acquired. Reverse
direction or rotate origin only under an explicit comparison convention.

Section 3 describes a two-capacitor crossfade with complementary weights,
neglecting the small gaps and using symmetric overlap. These assumptions support
the piecewise linear interpolation shown in Figure 3. They do not establish
measured capacitance-versus-angle, fringing fields or receiver loading.

**Speed remains unresolved across sources.** Paper Section 3 says approximately
6 Hz. Atlas p. 163 attributes 412 rpm, or 6.8667 Hz, to its factory source.
This paper cannot independently establish the latter value. The factory manual
and patent cited by the paper were not separately acquired or reviewed in this
assignment. Retain speed provenance and uncertainty; do not label either value
a measured speed or silently substitute one for the other.

## Erratum and remaining evidence boundaries

Paper Section 2.1 on PDF p. 2 / DAFX-272 calls the circuit nineteen LC stages
and names L1–L19/C1–C19. This is internally inconsistent with Figure 1,
Table 1 and Figure 2's six-plus-twelve partition. The reviewed reconstruction
therefore preserves **eighteen LC pairs and nineteen observable voltages**.
The prose error remains recorded; the paper PDF and atlas were not modified.

The complete paper read does not independently qualify its printed WDF
equations or its authors' simulations as repository execution evidence.
The numerical hazards listed in [E02](ERRATA.md#e02--chapter-028-reports-inconsistent-publication-equations)
still require the applicable independent derivations and checks. No simulator,
runtime implementation, physical measurement or audio comparison was run by
this assignment.

Production applicability is still open: no identified production drawing,
line assembly revision, selected organ, AO-28 source/recovery impedance,
coil loss/coupling, parasitic capacitance, scanner loading, calibrated signal
scale or uncertainty was acquired. The paper expressly studies a late-model
B3 and uses an idealized unloaded scanner model. It does not turn nominal
component values into measurements of a particular instrument.

The next implementation step can use this **documentary nominal graph** and
the corroborated cyclic order with a declared phase convention. Acceptance
still needs independent electrical/numerical comparisons, rotor continuity
and state-transition tests, and separately identified hardware evidence before
making production or specimen fidelity claims. See the
[scanner gate](../M3_REMAINING_AND_SCANNER_GATE.md) and
[numerical contract](../SCANNER_NUMERICAL_CONTRACT.md).

## Executed comparison result

After visual transcription, a separate Python/Decimal comparison read the JSON
and checked every component ID, kind, positive/negative endpoint, nominal
magnitude and unit against independently written expectations. It also checked
all outputs, the complete node set, ideal drive and both switch states. It did
not import the graph compiler or solver. Result: **50/50 components, 19/19
outputs, 27/27 nodes and both boundaries matched**; no discrepancies in those
records. The explicit tables above preserve the comparison expectations for
review independently of any generated runtime artifact.
