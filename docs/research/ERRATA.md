# Atlas errata and interpretation hazards

Source identity and coverage: [ATLAS_REVIEW.md](ATLAS_REVIEW.md) and
[source-manifest.json](source-manifest.json). All page references below are atlas
PDF pages. The source PDF is preserved unchanged. These entries guide independent
implementation and review; they are not a claim of published author corrections,
external-source verification or locally executed DSP tests.

## E01 — Scanner traversal has 15 entries for 16 positions

**Confirmed printed mismatch:** p. 166 calls for sixteen positions, computes
`k=floor(16*phaseTurns)`, and wraps modulo 16, but prints only:

```text
[0,1,2,3,4,5,6,7,8,7,6,5,4,3,2]
```

The printed wrap requirement says terminal 2 blends back to terminal 1. The
inferred completion is a trailing `1`, giving:

```text
[0,1,2,3,4,5,6,7,8,7,6,5,4,3,2,1]
```

This repairs the printed algorithm under its declared coordinate convention; the
trailing `1` is an inference, not independently recovered factory wiring. Before
M4 acceptance, retain tests for length/range, forward/return traversal, wrap
continuity, equal-input unity and uninterrupted rotor phase, plus independent
documentary confirmation. See [review 02](../development/agent-notes/02-atlas-pages-085-168.md).

**2026-11-13 primary-source follow-up:** the complete DAFx-2016 paper was
read, and its Figures 1 and 3 were freshly rendered and inspected. Both
independently corroborate the sixteen-position cyclic order above for the
paper's model. Figure 3 places its terminal-1 peak at `pi/8`; the atlas's
terminal-1 phase origin therefore shifts the plotted origin by one sixteenth
of a turn. The trailing entry now has primary documentary support, while
factory wiring, specimen phase/direction, exact speed and scanner loading
remain unverified. Preserve the listed executable acceptance checks. Source
identity, complete component/tap comparisons and limits are recorded in
[SCANNER_PRIMARY_REVIEW.md](SCANNER_PRIMARY_REVIEW.md). The original atlas
list and its earlier inference remain source history.

## E02 — Chapter 028 reports inconsistent publication equations

Chapter 028's discrepancies concern its cited WDF paper; this review inspected
the atlas account, not the external paper or authors' implementation. Under the
atlas's convention `a=v+Rp*i`, `b=v-Rp*i`, current enters the positive-voltage
terminal and `Rp>0` (pp. 176-180, reiterated p. 465).

| Reported hazard | Implementation contract and validation boundary |
| --- | --- |
| Printed root equation 7 does not reproduce the general elimination (p. 177) | Use `M=I-Phi*S11`, `Gamma=S21*solve(M,Phi*S12)+S22`, `Theta=S21*solve(M,Psi)`. Check residuals of both original simultaneous equations; multiplication order matters. |
| Source signs in equations 13/15 and switch labels in equation 14 conflict (pp. 177, 180) | Under this convention source `b=2*Vs-a`, open `b=a`, short `b=-a`. Reconstruct voltage/current to verify each constraint. |
| Equation 19 has the wrong inductor DC limit; equation 23 does not yield its stated positive-inductance adaptation (p. 180) | Adapted inductor: `Rp=K*L`, `b[n]=-a[n-1]`; capacitor: `Rp=1/(K*C)`, `b[n]=a[n-1]`. Verify leaf identities and stored-state conversion. |
| Prewarp example mixes hertz and radians/second (p. 178) | Use `omega0=2*pi*f0` and `K=omega0/tan(omega0/(2*fs))`. At 44,100 Hz and `f0=7075 Hz`, `2/K≈24.8133 us`; using 7075 rad/s gives about 22.7245 us. Neither is specimen calibration. |
| Nineteen-stage prose conflicts with circuit enumeration (pp. 157, 175, 181, 465) | Preserve 18 LC sections and 19 ground-relative outputs; outputs 1-6 are divider midpoints, 7-19 are p6-p18. Nine selected depth terminals and sixteen scan positions are separate counts. |

The atlas's reported 100-matrix/`1.11e-16` fixture is a historical synthetic
algebra result. Its script is absent from the baseline; it qualifies neither a
complete scanner circuit nor hardware. Re-derive and execute independent loaded
AC/transient comparisons for all nineteen signed outputs before accepting M4
(pp. 179-186). [Review 03](../development/agent-notes/03-atlas-pages-169-252.md)
retains the numerical and physical acceptance distinctions.

## E03 — Conceptual diagrams can look like serial signal paths

The illustrated arrows on p. 274 (treble/bass ports), p. 322 (horn/drum histories)
and p. 334 (divider/spring blocks) must not be copied as serial wiring or serial
state dependencies. The accompanying text specifies parallel electrical/acoustic
branches or independent owners. Use source-reviewed connectivity and explicit
port equations; treble voltage is `VA-VH`, bass voltage is `VW-VB`. The optional
RV spring branch returns through its separate amplifier and fixed speaker.
[Review 04](../development/agent-notes/04-atlas-pages-253-336.md) records the visual
inspection. The responsibility map on p. 4 and algorithm map on p. 177 likewise
do not establish component connectivity.

## E04 — UI status is internally stale and remains source history

Page 461 calls chapter 072 checks pending; pp. 439-444 and the later reconciliation
on pp. 482/491 report 28 JavaScript checks passing after three fixes. Retain p. 461
as stale wording. The later report is still an atlas claim about an absent test
double and absent companion files. Browser verification was unrun; these counts
are not present repository, native accessibility, host or audio tests. Pages
409/415/422/440 are art or original design studies, not proof of a working product.
See [review 06](../development/agent-notes/06-atlas-pages-421-500.md).

## Other implementation-critical source limits

| Atlas locator | Hazard and required interpretation |
| --- | --- |
| pp. 98-102, 464, 491 | High manual foldback uses repeated octave subtraction. A generated 549-entry map and six printed boundary rows do not recover the absent independent factory transcription. |
| pp. 140, 248, 464 | Pedal map has 200 contact positions, 195 connections and five explicit disconnections. Preserve duplicate branches; disconnected is not source zero. |
| pp. 92-93, 350 | Factory Table V is a G-G service-output reference under a particular load/setup, not 91 pickup amplitudes. |
| pp. 171, 465 | Ground-relative scanner taps already include the return once. Adding another dry copy can double chorus return. |
| pp. 217, 235-240, 458, 488 | AO-28 inventory/124 placements are not a connected netlist or installed-package count. Preserve factory C59 versus duplicate redraw C56 and alternative P-D/no-code networks; unresolved R62 blocks that active circuit export. |
| pp. 458, 463, 488 | Selected factory AO-28 upper Figure 24 is printed 3-50/source PDF 129, not PDF 127/lower drawing. Compilation PDF p. 71 is a 1995 redraw; these locators are atlas-reported. |
| pp. 293, 295, 466 | Five-to-eight seconds is a bass fast-to-Chorale service adjustment, not a universal motor time constant. Driver 020305 differs from spacer 020313; 122 and 147 require distinct electrical profiles. |
| pp. 302-303, 467 | Atlas flags a cited Doppler cosine sign and reversed interpolation weights. Validate the declared coordinate norm and `(1-mu)*x[i]+mu*x[i+1]` endpoint identity independently; no external author erratum was verified here. |
| pp. 338-339, 467 | Variable-inductance driver energy requires electrical `Lprime*i*v` and mechanical `0.5*Lprime*i^2`. Atlas flags copper 0.039 versus 0.00393 per degree C at 20 C; installed-coil calibration remains unknown. |
| pp. 311, 329, 475-480 | Published 122A measurement and simulation are different evidence; retouched P005/P020 images cannot support geometry. Neighboring model evidence must retain its applicability limits. |

Future resolutions must name source revision/page, selected convention, independent
review and executed results. Keep unresolved items visible rather than silently
editing the preserved PDF or inheriting a historical pass.
