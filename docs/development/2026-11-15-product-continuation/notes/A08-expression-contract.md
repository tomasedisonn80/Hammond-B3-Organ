# A08 — expression-calibration contract

Actual assignment `/root/w02_a08_expression_contract`, wave 2. Reviewed complete
`AGENTS.md`, the M0–M9 plan, session scope, `MidiInput.h/.cpp`, the native parser,
MIDI request/retirement/reconnect path, replay connection, modal focus/input,
shared modal geometry/paint and copied diagnostics at starting source `647ae1b`.

Created [MIDI_EXPRESSION_CALIBRATION.md](../../../MIDI_EXPRESSION_CALIBRATION.md),
identity `midi-expression-endpoints-v1`. It specifies exact APIs and numerical
mapping, CLI options, eleven-stop native modal behavior, epoch transitions,
non-persistence in musical controls and independent acceptance requirements.

The mapping clamps the raw 0–127 input between two strictly increasing endpoints,
divides in double, then optionally inverts. Default mapping is exactly the prior
`double(raw)/127.0` for every raw value. Calibration affects only CC11 and keeps
parameter 8192, all 47 IDs, state4/readers1–3 and nominal Engine arithmetic intact.
CC121 resets normalized expression to 1.0 directly; calibration must not transform
that default, particularly when inverted.

The reviewed existing lifecycle already retires input, joins the backend,
discards stale packets and awaits scoped-note release acknowledgment before a
new epoch. Reuse it for changed calibration. Identical active port/route/calibration
Apply is a no-op. Reconfiguration explicitly releases MIDI notes; it does not
reset phases or change musical expression by itself. Every epoch retains an
immutable calibration. Selected, configured, pending and active settings remain
distinct; failed opens cannot claim active calibration. Synthetic replay remains
script controlled and accepts calibration through CLI startup settings.

The contract requires invalid CLI/Apply transactions to preserve existing state,
shared hit/paint geometry, full minimum-size/Flat functionality, truthful pre/post
shutdown metadata, and decoder-to-Session evidence rather than formula-only tests.

Only this note and the assigned contract were written. No implementation, build,
runtime test, hardware calibration or commit was performed. The contract is
specified for the next independent review; this note does not claim acceptance
or execution of its required gates.
