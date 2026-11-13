# Runtime boundary review

Reviewed by `/root/w08_a46_runtime_boundary_review` on 2026-11-13 UTC.
The reviewed source is frozen tree
`b9146546fcf756360e1da89d6698c4999359579f`: the published sample-rate lifecycle
plus the frozen partial-key and trace integration. Later packaging, plotting and
benchmark work is outside this runtime review.

## Verdict

**No actionable runtime defect was found in the reviewed scope.** The implemented
admission, timing, ownership and lifecycle boundaries agree with their declared
contracts. A clean, coherent strict GCC 14.2 Release build passed all six selected
acceptance suites in **0.84 seconds**, with no failures or skips. No production
change or additional regression was warranted.

This is a scoped code review and local replay of existing acceptance tests. It
does not replace the integrator's complete staged-source gate or that revision's
hosted platform qualification. Commands and source identities are retained in the
[assignment 46 note](../development/2026-11-13-continuation/46-runtime-boundary-review.md).

## Reviewed boundaries

| Boundary | Code finding | Retained acceptance selected for this review |
| --- | --- | --- |
| Engine admission | Preparation, prepared block limit, output length, event capacity, clock overflow, and every event's offset/order/payload are checked before dispatch or output writes. Enum/index conversions occur only after validation. | [InputProcessor](../../tests/test_input_processor.cpp), [partial keys](../../tests/test_partial_key.cpp) |
| Ownership admission | Structural checks precede state work. Identity conflicts, simultaneous owner capacity and expanded physical output capacity operate on a value-owned candidate and fixed temporary output. A late failure installs neither. | [NoteOwnership](../../tests/test_note_ownership.cpp), [InputProcessor](../../tests/test_input_processor.cpp) |
| Combined commit | The facade translates a private ownership candidate, processes the resulting physical prefix, and installs ownership only after Engine succeeds. Translation errors deliberately precede Engine errors. | [InputProcessor](../../tests/test_input_processor.cpp) |
| Timing and contact history | Stable same-offset order is preserved. Zero-frame calls apply commands without elapsed phase/readiness time. Nominal targets retain position and hysteresis; ideal endpoints act immediately. Repeated targets preserve their travel segment. | [Partial keys](../../tests/test_partial_key.cpp), [owned lifecycle](../../tests/test_owned_lifecycle.cpp) |
| Rate changes | NotPrepared and invalid-rate admission precede candidate work. Same-rate requests return without rebuilding. Changed rates validate owned source data and all module candidates before installation. Musical state, phase, contacts, readiness and frame count survive. | [Engine rate](../../tests/test_engine_rate.cpp), [owned lifecycle](../../tests/test_owned_lifecycle.cpp) |
| Parameter conversion | The immutable 43-record table maps permanent IDs to fixed targets. Exact binary thresholds avoid rounding-mode-dependent half-step decisions; invalid IDs/scalars leave the destination unchanged. Engine retains responsibility for offset admission. | [Parameter bridge](../../tests/test_parameter_bridge.cpp) |

The principal implementations inspected directly were
[Engine.cpp](../../src/Engine.cpp), [ContactBank.cpp](../../src/ContactBank.cpp),
[Percussion.cpp](../../src/Percussion.cpp),
[TonewheelBank.cpp](../../src/TonewheelBank.cpp),
[NoteOwnership.cpp](../../src/NoteOwnership.cpp),
[InputProcessor.cpp](../../src/InputProcessor.cpp),
[ParameterBridge.cpp](../../src/ParameterBridge.cpp),
[ControlState.cpp](../../src/ControlState.cpp) and runtime-profile validation in
[Profile.cpp](../../src/Profile.cpp), with their public types and contracts.

### Capacity and rollback

The owner table admits at most 256 simultaneous owners. Its per-key 16-bit
counters therefore cannot overflow through the public API. The 1,024-command
input bound and 1,024-event output bound are separate: channel retirement can
expand one command into several physical releases. The implementation checks
the actual emitted prefix even when the caller supplies a larger output span.
Existing tests exercise this expansion and rejection after earlier candidate
mutations; they compare subsequent behavior, not only the returned status.
[NoteOwnership.cpp](../../src/NoteOwnership.cpp) and
[its capacity tests](../../tests/test_note_ownership.cpp) retain those checks.

The render-clock test uses subtraction before addition, so a positive request
cannot wrap the 64-bit frame count. Reaching the maximum does not prohibit valid
zero-frame ownership releases. Rate changes retain the prepared block limit and
clock rather than silently granting a different process specification.
[Engine.cpp](../../src/Engine.cpp) and
[owned lifecycle acceptance](../../tests/test_owned_lifecycle.cpp) cover these
boundaries.

### Original routes and one note authority

Identified owners retain their first manual destination, including after bus
remapping and duplicate NoteOn. Anonymous release scans surviving insertion order
for the original bus/channel/pitch. Channel AllNotesOff retires only that channel's
owners and emits final-owner NoteOffs; it never emits the Engine's manual panic.
This preserves unrelated owners and normal release travel.
[Ownership semantics](../NOTE_OWNERSHIP.md) and
[the implementation](../../src/NoteOwnership.cpp) agree.

These guarantees require the documented sole-authority rule. Direct physical
note/partial-key/panic commands, a separate competing ownership table, or an
Engine reprepare cannot be interleaved while retaining incompatible old owners.
The wrapper does not claim to repair that misuse. Its explicit coordinated-reset
and valid-span requirements are in [INPUT_PROCESSOR.md](../INPUT_PROCESSOR.md).

### Shared history and copied inputs

Each source is sampled once per rendered frame and shared by all routed branches.
Note, preset and expression events do not reset its phase. Current contact
connections and readiness produce the current sample; readiness and travel then
advance once. The ninth-contact detector is distinct from the selected harmonic
contact, so partial harmonic audio before detector closure is intentional. Cancel
changes routing; manual panic opens contacts; neither fabricates elapsed recovery
or reseeds the generator. [Engine.cpp](../../src/Engine.cpp) implements the
[console timing contract](../CONSOLE_DYNAMICS.md).

Contact transitions can dirty coefficients even without an input event. The
implementation performs at most one complete coefficient rebuild before each
rendered sample, after that sample's event cluster. An event-count-only bound
would not describe the enabled nominal contact path. Allocation and execution
cost qualification belongs to the separate [real-time audit](../REALTIME.md).

Preparation copies the source profile and all contact/percussion parameters.
Reconfiguration uses these owned copies. The selected Engine rate test poisons
every field of both caller inputs after preparation, then verifies accepted rate
changes, exact paired continuation, and independent state/sample formulas.
No caller-owned profile reference remains in these runtime objects.
[Engine rate acceptance](../../tests/test_engine_rate.cpp) retains that case.

## Evidence boundary and next action

The review reread atlas pages 105, 115, 120, 130, 132, 135, 151, 385, 388 and 398.
They distinguish continuous source/history ownership, synthetic mechanism tests,
declared host policies and actual physical/native-host qualification. The current
code implements a nominal partial M3 model under those boundaries; it does not
establish specimen contact physics, a complete percussion circuit or the atlas's
fuller continuous control proposal. The [atlas](../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf)
and [project plan](../PLAN.md) retain the physical and product gates.

Access to mutable Engine, module and ownership state still requires stopped or
same-processing-thread use. This
review did not run native MIDI/SDK/device callbacks, concurrency or reclamation
tests, allocator instrumentation, deadline campaigns, physical captures, the
offline I/O tool suites, or a new hosted matrix. Those are separate work scopes,
not hidden failures of these six tests.

**Next action:** integrate the remaining wave-eight files, qualify the complete
staged source, and observe its hosted results. For a future native adapter, define
the common note/control event order, coordinated reset and input rejection/output
policy before connecting a device. Preserve the existing internal parameter law
unless an explicit exported mapping and migration is approved; the current bridge
does not claim native VST3 curve semantics.
