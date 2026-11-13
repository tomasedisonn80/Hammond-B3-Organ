# Assignment 09: frozen comparison and policy contract

## Actual assignment and ownership

- Assignment: `/root/cal_w2_a09`, wave 2, assignment 09 of the independent
  2026-11-13 capture/calibration-readiness session.
- Owned paths: `docs/CAPTURE_COMPARISON_CONTRACT.md` and this note only.
- Inspected checkout: `08fa8de8f718584c4ee4ab3b392c779f3290289c`, tree
  `f5cff4b89d19f36a73f9d2a8ddb966db487f832c`; the local remote-tracking
  `origin/main` resolved to the same commit. No fetch/publication was performed.
- No implementation, global status/manifest edit, git mutation, acquisition,
  numerical acceptance-suite execution or physical acceptance is claimed.

## Inputs actually read

Read repository `AGENTS.md`, README, current status/next steps, scanner handoff,
latest development-log entry, plan, atlas review, calibration scope/session README,
capture metadata v1, and active rotary/standalone scopes. Read the fresh calibration
atlas notes 03, 05 and 06 in full. An initially combined response truncated note 05;
it was reread separately in full before drafting. This assignment does not claim
another complete 500-page reading or another worker's visual inspections.

Used PyMuPDF to read the actual unchanged source PDF pages **364 and 484** as
extracted text. These pages explicitly require shared evidence-supported nuisance
corrections with before/after results, retained uncertainty and physical delay,
predeclared bounds and inconclusive decisions when uncertainty crosses the limit.
The source's identity is retained by the fresh readers and source manifest; this
assignment did not independently recompute its hash or inspect new page images.

## Frozen decisions

The [comparison contract](../../CAPTURE_COMPARISON_CONTRACT.md) freezes:

- Standard-library `compare_signals` and `evaluate_policy` APIs, exact report keys,
  nonmutation, finite/strict scalar types and bounded arrays/work. Channel pairing
  is by index; windows are explicitly half-open; the selected spectral window does
  not change the full-array pointwise errors.
- Signed DC and absolute bias, RMS/max errors, both raw RMS values, normalized
  error and signal-to-error dB. Silence, null denominators and zero error retain
  explicit null/reason values, never NaN, Infinity or a fictitious perfect ratio.
- Optional selected-frequency weighted complex coefficients with negative-exponent
  phase, explicit rectangular/symmetric-Hann weights, no one-sided doubling,
  declared FS floor, retained phase masks and signed/absolute phase errors.
- Exact strict JSON policy bytes and SHA-256 of those original bytes; typed safe
  metric targets; fixed nonnegative upper bounds; required uncertainty declarations.
  A full interval must lie within the limit for pass; a wholly excessive interval
  fails; overlap, undefined metrics or unknown uncertainty are inconclusive.
- Numerical `pass`/`fail`/`inconclusive` kept separate from mandatory
  `physical_fidelity: not_established`, including each criterion result. No hash
  or policy declaration establishes preregistration chronology.
- Distinct fit, development validation and final-test roles. Later fixed shared
  gain/integer-delay corrections require a separate wrapper retaining both raw and
  corrected comparisons, exact coverage and evidence; no fitting occurs here.

These are original engineering choices derived from the source requirements,
not field names or universal fidelity thresholds recovered from the atlas.

## Independent acceptance handoff

Section 9 supplies independent literal zero/silence, gain, offset, polarity,
integer-delay and sine/cosine-phase vectors with closed-form expectations. It
also fixes policy equality/overlap/missing-uncertainty cases, preserving failures,
phase masks, strict types, malformed input, work limits and all-criteria coverage.
Producer output must not become the test author's only reference.

The integrator received an early API/field-name handoff during drafting, followed
by the completed contract. Producer assignment 15 should implement the frozen
surface; later independent acceptance should record its own executions and source
identity. This note does not label those future tests as run.

## Verification and limitations

Executed read-only shell inspection of the above files, current working changes,
and checkout/tree/remote-tracking identities. Read source pages 364/484 through
PyMuPDF. An inline Python documentation check parsed both JSON examples, checked
the complete policy example's exact root/analysis/criterion/target/uncertainty key
sets, resolved all three local Markdown links, and found no trailing whitespace.
It also checked the offset/delay algebra and all four binary-exact interval examples.
All checks passed. These are document consistency checks, not producer acceptance.
No audio comparison or policy implementation exists as a result of this assignment.

Frozen contract SHA-256 at this handoff:
`9be191da6491324d77ff88cd3d098671dd3765bd33b595b4cfae5940ff920e06`.
This byte identity identifies the document; it does not independently attest the
chronology of a policy, a physical comparison or final-test isolation.

The contract deliberately leaves audio/header admission, complete corpus relation
auditing, source/artifact binding, CLI/filesystem publication, immutable acquisition
archives, physical calibration, listening and actual instrument qualification to
their separately owned dependencies. A structurally valid report or passing
synthetic vector cannot close those gates. Concurrent files were preserved.
