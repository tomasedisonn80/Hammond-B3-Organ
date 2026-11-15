# A07 — Additive scanner FOH contract

**Assignment:** `/root/w02_a07`, wave 2, 15 November 2026.  
**Checkout:** `/workspace/scratch/116ca0948095/Hammond-B3-Organ`.  
**Owned files:** this note and `docs/SCANNER_FOH_CONTRACT.md` only.  
**Result:** authored contract pending A10 review and integrator freeze; no native
implementation or acceptance is claimed.

## Decisions and source basis

I read the complete live `AGENTS.md` and `docs/PLAN.md`, session entry/checkpoint
and assignments, A03's complete atlas/feasibility note, current navigation,
the current ScannerLine header/implementation, and the scanner line, frozen
numerical, AC parity, probe and independent transient contracts/acceptance.
This assignment relies on the retained atlas readings and graph/primary-source
review; it does not claim a new full atlas reading or specimen evidence.

The contract preserves the exact documentary graph and public 36 physical
coordinates. `ScannerLineFoh` is additive, reusing the existing state/frame/
response types, rate predicate and numerical bounds without editing v1.
The exponential's two auxiliary input coordinates exist only during
preparation. Its endpoint update uses separate previous/current forcing
vectors; cold first processing advances an interval and observes frame 1.
Return switching applies to the entire upcoming interval and retains physical
capacitor/current continuity, with algebraic nodes reconstructed afterward.

Preparation is fixed-size, off-thread Padé-13 scaling/squaring of a 38-by-38
augmentation, with norm target 0.5 and at most sixteen squarings. I verified
the coefficient list and U/V evaluation order in Higham's primary 2005 paper,
Algorithm 2.3, DOI `10.1137/04061101X`, using the author-hosted Manchester PDF.
The fixed conservative variant, finite/pivot/residual/conditioning admission,
resource caps and no-fallback behavior are explicit. A Padé solve residual
alone does not establish exponential forward accuracy.

Root accepted the additive API/scope and requested A10 review before freeze.
Root also accepted the probe's explicit offline `--subdivisions` fixture
adapter. It consumes original input knots, generates exactly j=1..m internal
endpoints and emits their final state, retaining different input-knot and
line clocks. This avoids an extra first frame and accommodates frozen
2400-knot traces without mislabeling an actual host resampler or filter.

## Acceptance and limitations

The independent native gate retains all eleven rates/fifteen host labels,
282 positive frequencies, exact DC, both return modes and signed tap/return/
current evidence. New FOH discrete parity is separate from the old bilinear
comparison; original same-Hz G5 bounds and failures remain unchanged.
Eight-times-host labels are predeclared line-only stationary candidates;
all lower-rate failures remain reportable. A03's success from 352800 Hz is
exploratory evidence only and is not attributed to native code.

Required work includes all 88 actual process carrier cases with independent
settling, full frozen transient refinements, all-coordinate basis checks,
250-ms passive energy runs, every ordered internal-rate pair, rollback from
nonzero history, partition equality, allocation instrumentation and identified
Release timings. The report contract names exact identities, completeness,
conditioning, error bounds, rejected metadata and honest not-run gates.
Actual interpolation/decimation and the complete rotating pipeline remain
next, followed separately by G6 and physical M4; this phase cannot claim a
full audible G5 pass or modify the nominal dry Engine.

## Verification and handoff

Executed work was source/document inspection, primary-paper lookup and
document consistency checks only. No build, test suite, native experiment,
git operation, child dispatch, shared-file edit or publication was performed.
The concrete next action is A10's independent
review, then assigned native/reference/probe implementation against the
reviewed contract. Any unresolved review item remains open before grading.

The executed `python3 -B` document check found balanced fenced blocks, no
missing local Markdown links and no unintended trailing whitespace in either
owned file. SHA-256 checks confirmed the frozen numerical contract, old
ScannerLine header/implementation and authoring graph remain byte-identical
to A03's recorded inputs. Contract bytes at handoff: 36,830; SHA-256
`b90dff5638abaadc9acd3ff8ff8870b3f1f2f606911c27e1bbe6974fa45bb11e`.
