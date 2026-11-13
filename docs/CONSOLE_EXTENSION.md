# Early console extension (partial M3)

This adds useful control behavior to the nominal dry engine. It does not close
M3: individual contact timing, physical multi-preset latches/loading, pedal audio,
percussion/recharge and loaded expression remain later work. The atlas requires
four retained manual drawbar banks and distinguishes preset Cancel from key
release (pp. 121-132, 389, 447). These relationships can be implemented with
explicit ideal controls before their circuit model exists.

## State model

A value-owned `ControlState` holds two banks (A/B) for each manual, nine discrete
positions per bank, one selected sounding bank per manual, a route-enabled bit
per manual and global normalized expression. Initial state: all positions 0,
selected bank B, routes enabled, expression 1. Keys and source phases belong to
Engine, not to this control object.

- Setting a bank position never selects it or changes the other banks.
- Selecting A/B enables that manual's route and uses its retained positions.
- Cancel disables the manual route and retains selected bank, all bank positions,
  held physical keys, expression and source phase.
- Editing a cancelled route's selected bank does not reconnect it.
- AllNotesOff releases keys on the selected manual and preserves the controls.
- A full control snapshot is validated before restoration; bad input cannot partly
  replace state. Restoration changes no key/source/clock state.

The chosen A/B selector is an explicitly exclusive engineering model. Physical
multi-preset latching and transformer loading are not inferred from it. The
factory chapel presets printed on p. 122 are future optional documentary data,
not silently installed or described as universal factory registrations.

## Engine compatibility and new events

Keep existing EventType numeric values 0..4 unchanged. Append:

| Event type | Value | index | value field |
|---|---:|---|---|
| BankDrawbar |5 | bank*9 + drawbar,0..17 | integer position0..8 |
| SelectBank |6 |0 | integer0=A or1=B |
| Cancel |7 |0 |0 |

Existing Drawbar targets the manual's selected bank. Direct BankDrawbar makes
stable bank identity available without changing the sounding route. Cancel is
a routing action; it must not be implemented as AllNotesOff. CLI fixture names
are `bank_drawbar`, `select_bank`, `cancel` when the renderer adapter is updated.

The renderer's initial nine Drawbar controls select the prepared bank B implicitly;
its legacy audio and five existing event semantics remain unchanged. Explicit
snapshot and bank diagnostics are copied values and are only safe on the same
processing thread or with processing stopped. No concurrent GUI protocol or
native host-state promise is introduced.

## Control persistence

Add a separate stopped/control-thread serializer for this bounded control state.
Use a versioned text grammar with fixed counts and strict trailing-token checks;
keep its I/O outside Engine. It saves musical controls, not oscillator phases,
held-note ownership, frame clock, capacitor charge or an exact DSP checkpoint.
The format and tests must state that distinction. Unknown versions or malformed
values reject atomically. A future plugin wrapper owns profile/host compatibility.

## Required evidence

Retained hidden-bank edits, held-key A/B changes, Cancel/reselect behavior, panic
separation, velocity independence, snapshot round trip/rejection, sample-offset
ordering and unchanged legacy render fixtures. Keep full M3 physical behavior
open in the status/next-step handoff even when these engineering tests pass.
