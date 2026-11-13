# Assignment 10 — Original scanner paper comparison

Date: 2026-11-13. Wave 2/10; assignment 10/60.
Agent: `/root/w02_a10_primary_source_review`.
Baseline HEAD: `6dc0702d5473912268e8af8f852b9b9984198ef3`.
Baseline tree: `a4f1d4b300de236436e22b748b1d4c46ed501ceb`.

## Scope and files

Independently reviewed the full eight-page Werner/Dunkel/Germain DAFx-2016
paper and compared its circuit, component table, output references, depth
maps and scanner figures against the atlas and new nominal graph. Read
`AGENTS.md` and the scanner gate before work. This assignment owned only
this note, [the primary review](../../research/SCANNER_PRIMARY_REVIEW.md)
and the isolated E01 follow-up in [ERRATA.md](../../research/ERRATA.md).
No graph, solver, runtime, control, shared status or source PDF was edited.

The paper was already supplied outside the repository at
`/workspace/scratch/1742da7072be/dafx2016-scanner.pdf`. Its verified SHA-256 is
`ccdace0e88d456d7d80cd3b675a0936ab1313680f5b2dda0ba33445df0caae83`.
The source URL, atlas identity and separately hashed uncommitted fixture are
recorded in the primary review. Neither the paper nor its rendered images
was redistributed in the repository.

## Findings

The visually inspected paper Figure 1/Figure 2/Table 1 agree with atlas
pp. 157/158/182 and every graph component: 18 L, 18 C and 14 R; all six
divider branches attach before their inductor. All nineteen outputs agree
and use ground as their negative reference. The return switch is closed
for vibrato and open for chorus. The paper's three nine-entry depth maps
also agree with atlas p. 170. The review preserves every component endpoint
and nominal value and every output pair in explicit tables.

Paper Figure 1's stator wiring and Figure 3's weights corroborate the cyclic
zero-based order `[0,1,2,3,4,5,6,7,8,7,6,5,4,3,2,1]`. This strengthens E01
from an internally inferred missing entry to a primary-paper-supported
model interpretation. The distinction remains consequential: Figure 3's
terminal-1 peak is at `pi/8`, while the repository convention starts that
terminal at phase zero. The review specifies that one-sixteenth-turn shift.
It does not claim measured physical phase or production wiring.

The paper's approximately 6 Hz speed does not independently substantiate
the atlas's 412 rpm nominal. The paper's prose also incorrectly calls the
network nineteen LC stages; its circuit/table/partition support eighteen
pairs and nineteen outputs. These conflicts remain visible. No selected
production assembly, factory drawing, specimen, electrical loading or
calibrated speed was acquired. Prior author simulation results were read
as published results, not counted as locally executed verification.

## Executed work and verification

Commands actually used included:

```sh
sha256sum /workspace/scratch/1742da7072be/dafx2016-scanner.pdf Hammond_B3_Leslie_Research_Atlas_500pp.pdf
pdfinfo /workspace/scratch/1742da7072be/dafx2016-scanner.pdf
pdftotext -f 1 -l 2 -layout /workspace/scratch/1742da7072be/dafx2016-scanner.pdf -
pdftotext -f 3 -l 4 -layout /workspace/scratch/1742da7072be/dafx2016-scanner.pdf -
pdftotext -f 5 -l 6 -layout /workspace/scratch/1742da7072be/dafx2016-scanner.pdf -
pdftotext -f 7 -l 8 -layout /workspace/scratch/1742da7072be/dafx2016-scanner.pdf -
pdftotext -f 157 -l 158 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftotext -f 163 -l 164 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftotext -f 170 -l 170 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
pdftotext -f 182 -l 182 -layout Hammond_B3_Leslie_Research_Atlas_500pp.pdf -
```

Fresh `pdftoppm -f PAGE -l PAGE -scale-to SIZE -singlefile -png SOURCE PREFIX`
renders were visually inspected for primary PDF pages 2/3 at size 2200 and
atlas pages 157/158/166/170/182 at size 1800. Temporary images remain outside
the repository. All eight paper pages were read; only the stated pages were
rendered and inspected. Truncated combined tool output was reread separately
before being counted as covered.

An independently authored Python comparison used `json`, `Decimal` and
literal source-transcribed expectations without importing the compiler.
Actual result: 50/50 component identities/kinds/endpoints/magnitudes/units,
19/19 output references, 27/27 nodes, the ideal source and both switch
states matched. This is documentary fixture verification only. Local
Markdown targets and whitespace were checked after writing the review.

## Handoff

Use the primary review for nominal graph provenance and the sixteen-position
cycle; retain explicit phase origin and speed provenance in the rotor
contract. Numerical/reference comparisons and runtime tests belong to the
subsequent implementation assignments. Physical loading and production
applicability still need separately identified evidence. Parent owns shared
status integration, commit and push; this assignment performed no Git
mutation and makes no publication claim.
