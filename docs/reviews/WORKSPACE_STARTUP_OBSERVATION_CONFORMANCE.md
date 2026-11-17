# Workspace startup observation implementation conformance

## Decision

**A59's implementation conforms to the frozen A53 admission and is ready for
root-owned native qualification.** This is a source/AST review, not an executed
native pass. The previously failed invocation and its unreached saved-byte
tail remain unchanged historical evidence.

The implementation reviewed is
[`test_standalone_workspace_replay.py`](../../apps/standalone/native_tests/test_standalone_workspace_replay.py),
47,128 bytes, SHA-256
`38808674e491c2224a7b425df55f26ac076e3560c302a6319dbff49e5e1d961b`.
It is bound to the [frozen admission](WORKSPACE_STARTUP_OBSERVATION_ADMISSION.md)
SHA `68a13c87bdab02b6a624e7845a6f60ec370fa7fb606554198bca0f9bdc94de56`
and its unchanged [receipt](../development/2026-11-16-heading-title-continuation/reports/a53-workspace-startup-observation.json)
SHA `c92a7d8f4fbd7679dfcd816d49ee04f5f228dda49062fbbb436a2514f582581c`.
The [separate conformance receipt](../development/2026-11-16-heading-title-continuation/reports/a53-workspace-startup-conformance.json)
records A53's independent comparisons and identities. A59's
[implementation receipt](../development/2026-11-16-heading-title-continuation/reports/a59-workspace-startup-prefix-implementation.json)
is independently identified; its native acceptance status remains unrun.

## Independent preservation proof

A53 compared the candidate against root's byte-exact original fixture, SHA
`9a226a6b17b1d7eb84a079a113f5ef97a6f37935ba16d1d3f55876bed907d6f3`.
Removing only the admitted prefix assignment, first-startup assertion and
explicit-origin argument from each of the four changed test methods restores
the original AST exactly. Every other original native method remains equal.
No replacement of an original expected control/held/view/file predicate is
hidden inside those additions.

The full `run_native`, control-path, held-path, view, capture-refusal,
header-held-prefix, header-journey and mixed-MIDI-journey bodies are individually
byte-identical. Original top-level imports, constants and helpers are unchanged.
Within `assert_commands`, all original accepted-note, command-delta and
final-acknowledgment assertions are AST-identical after the admitted startup
branch is replaced by the chronology validator.

A53 independently enumerated the pure plan-building expressions, replacing
native contexts with data collection and removing their assertion bodies.
No real test setup, executable, subprocess or production implementation was
invoked. All **30 original plans** remain identical and in order, including
exact UI/MIDI script hashes, state bytes, dimensions, presentation flags,
final-size expectations and screenshot choices. Exactly **seven new empty
250 ms plans** account for the prospective total of **37 native children**.
Every added prefix immediately precedes its matching full plan with identical
initial size, presentation and state. A dummy origin used solely during this
plan enumeration supplies no runtime or startup evidence.

## Predicate conformance

`assert_startup_prefix` creates a fresh actual native child when the suite is
executed. It reuses the unchanged strict runtime/schema/lifecycle checker,
requires exact loaded controls and empty musical/painted holds, establishes
positive final sequence `S`, requires zero note commands and final applied/
resolved acknowledgment, and compares the exact saved bytes to the input.
The zero command delta and chronology bounds force every retained prefix
musical sample to agree with that completed origin. No result is cached.

The four affected methods call it seven times: all four Rotary/Service ×
Dimensional/Flat hidden-region configurations, followed separately by the
focus-memory, parameter-gesture and keyboard-owner journeys. Their original
full plans are untouched. Every full run then calls `assert_copied_startup`,
requiring a nonempty history whose first copied applied/resolved values equal
the independently measured `S`, with complete `CONTROLS` and empty holds.
Queued submission may already be ahead. A missing copied startup cannot pass
by relying on the separate prefix.

`assert_copied_chronology` requires positive `S`, a nonempty history, monotone
elapsed/applied/submitted values, `resolved == applied`, and
`S ≤ applied ≤ submitted ≤ final`. At an unchanged applied sequence, complete
controls, manual-note sets and pedal IDs must remain identical. It also
checks the final copied state for that same-sequence consistency. Exact note
counts, command delta and before-shutdown acknowledgment remain enforced by
`assert_commands`. Its origin is now a required keyword, preventing silent
reintroduction of the old implicit origin.

The first-`S` requirement is separate from general chronology. This correctly
preserves the existing header Upper-only prefix, whose first copied musical
sample may be `S+1`, and its independently established origin. Existing
header coalescing exceptions and required stages remain unchanged. Mixed MIDI
retains its genuine connection prefix, packet counts, owner checks and the
acknowledged `[2100,2350)` ms window. The pointer journey retains its allowed
coalesced histories and final-empty observation at or after 2050 ms.

## Pure checks and execution boundary

A59 records 13 passing pure validator tests in 0.010 seconds, with zero native
children. A53 inspected their source and receipt without rerunning them. They
reject omitted/advanced startup, incomplete loaded controls, held startup
notes, regressing times/counters, inconsistent applied/resolved/submitted
bounds, changed state at the same applied sequence, incorrect command counts,
wrong deltas and incomplete final acknowledgment. Positive cases preserve
queued-ahead startup and both legitimate header sampling patterns. Synthetic
dictionaries are explicitly labeled as oracle tests, not native evidence.

The complete Python suite now contains six native journey methods and 13 pure
methods. Its expected **37 native children** are distinct from those 19 Python
methods and from the single CTest registration. The existing 9-second child,
90-second CTest, `RUN_SERIAL`, original full-script durations, 600 ms header
settle and production completion-drain bounds remain unchanged.

Root must execute and retain the amended suite on the intended candidate,
demonstrate all 37 actual children, and reach the previously blocked exact
view/file assertions. A59's pure passes and A53's source conformance do not
provide those results. Keep the old failure, frozen admission and this review
separate from subsequent qualification. Full coherent and exact-source hosted
acceptance, physical devices, real display, native accessibility, literal
whole-interface parity and audio deadline claims remain separate gates.
