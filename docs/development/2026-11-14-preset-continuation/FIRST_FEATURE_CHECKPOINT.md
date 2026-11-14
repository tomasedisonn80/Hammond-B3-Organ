# First implemented preset checkpoint

This checkpoint publishes the dependency-ready M3 fixed-registration feature and
its M9 native preset controls. It is an intermediate checkpoint in the owner's
sixty-agent session, not final session completion or measured instrument fidelity.
The actual assignment manifest distinguishes completed and active workers.

## Qualified source and explicit deltas

The runtime implementation is the [A31 combined source](../../reviews/PRESET_FIRST_INTEGRATED_GATE.md):
original manifest `1f805c9257e2843c8ac1345938ff28603e2780e93831f0e2c02c907cc420ac8b`,
corrected manifest `db1001d3ab1b506c205aed06a347d2279d6aea0afa6f72b59949cf13e57eb8e5`.
The full 143-suite run passed 141 suites. The two observed test/documentation
corrections then passed their affected 2-suite recheck without rebuilding any
production binary. Those results are retained separately, including the original
failures, two in-method capability skips and SDK diagnostic limitations.

The later [A32 generator repair](../../reviews/PRESET_GENERATOR_ACCEPTANCE.md)
executes exact strict-compiler source bytes instead of trusting stale Python
bytecode. Its four cache-direction regressions, existing 17 methods and isolated
25-command CMake gate qualify that source-only generation delta. Valid generated
data remains exactly 2,099 bytes, SHA-256
`66cbb1a23cb5ebf14844afd6f98e13829c9f69c1511b09d5974ca5a4527157c6`.
The [A33 old/current comparison](../../reviews/PRESET_LEGACY_PCM_ACCEPTANCE.md)
passes 63 paired legacy cases, including complete PCM16 and native-summary equality.

The README now describes 47 parameters, state4, retained banks and 24 native preset
keys. Its [actual preview](../../../examples/demos/standalone-presets-preview-v1/README.md)
is explicitly bound to A28's native executable after A25's focus repairs, with
its own copied source manifest and original pixels. The current runbook and
initial handoff are included in source. The hosted relocated-smoke expectation
is aligned to diagnostic schema3.

## Boundaries of this publication

The first checkpoint keeps the qualified 13-file MIDI-off / 17-file MIDI-on
Standalone package mapping. A35's expanded workflow provenance and A36's new
installed preset runbook remain a coordinated later change. A34's current
capture-producer migration/full gallery also remains separately owned. Their
in-progress files are preserved in the working tree and excluded from this
coherent checkpoint. Earlier capture tools and galleries retain their dated
source meaning; the new manual preview command uses the actual current CLI.

Continue the remaining logical waves: complete the reusable gallery and package,
inspect actual hosted macOS diagnostics, refine the reference appearance, qualify
sanitizers/platforms and final source, reconcile all current documentation, and
finish the actual 60-worker accounting and publication handoff. The reference
perspective/proportions, tiny labels, semantic accessibility, physical devices,
measured preset loading and scanner/AO-28/Leslie integration remain explicit gates.
