# Native fixed-registration workflows and diagnostics

This is the current standalone adapter contract for the
[exclusive selector](PRESET_SELECTION_CONTRACT.md). The core, host and saved-state
contracts remain authoritative. Actual qualification and original failures are
recorded in [A28's execution note](development/2026-11-14-preset-continuation/28-native-workflows.md).

## Applied controls, remembered controls and report versions

The application now writes native diagnostic **schema version 3**. Its previous
schema-2 reports remain historical evidence with unchanged bytes. Every emitted
controls object—including final controls and replay observations—contains:

| Field | Domain | Meaning |
| --- | --- | --- |
| `manual_drawbars` | Two manuals × two banks × nine positions 0–8 | All four retained adjustable banks. |
| `selected_banks` | Two values 0/A or 1/B | Remembered bank, including during fixed selection or Cancel. |
| `fixed_registrations` | Two values 0/None through 9/A | Raw retained fixed memory; Cancel does not erase it. |
| `route_enabled` | Two booleans | Whether each manual's route is connected. |
| `preset_selections` | Two values 0–11 | Effective Cancel/fixed/bank choice derived through the checked core helper. |
| Existing expression, pedal and percussion fields | Existing domains | Unchanged meanings and values. |

The effective selector is 0 when disconnected, otherwise the nonzero fixed value,
otherwise 10/A or 11/B. A cancelled F# therefore reports raw fixed value 6 and
effective value 0 while retaining its selected A/B bank. Effective values are
copied diagnostics, not a second independently editable or serialized control.
An invalid copied snapshot emits `null` for a derived selection instead of
silently describing invalid data as Cancel. Successful-report acceptance requires
valid numeric fields and the complete expected controls object.

The SDK-free benchmark now emits **`hammond-standalone-benchmark-v2`** with the
same two additional control fields. Its four existing score definitions retain
**workload version 1**, including their original no-fixed registrations, work
counts, timing boundaries and audio accounting. Archived benchmark-v1 reports
remain unchanged. The benchmark's source fingerprint now includes the actual
fixed-data generator, strict chapel compiler/schema, authoring catalog and both
admitted readings, in addition to its existing source/profile/pedal/scanner
inputs. See [the benchmark contract](STANDALONE_BENCHMARK.md).

## Preset operation and ownership

Each manual's left cheek contains C through B. C momentarily cancels its route;
C# through A select the nine documentary fixed rows; A# selects retained bank A;
B selects retained bank B. Fixed A and adjustable A#/bank A are different actions.
EDIT A/B changes the adjustable bank displayed by the drawbars. It does not
select that bank as the sounding route. Selecting, releasing or moving focus
between preset keys never creates or releases a note owner.

Native acceptance uses literal key points at the minimum 960×700 window and
requires all 24 commands to finish with both original manual note owners still
held. It checks the complete four-bank arrays, remembered banks, raw fixed
memory, route bits, effective selection and desired/applied agreement. Pointer
selection never saves a file implicitly.

The current default-layout focus order has six header controls, two Upper EDIT
controls, then twelve Upper presets: the first Upper drawbar is the twenty-first
Tab from initial unfocused state. From EDIT A it is fourteen Tabs; from EDIT B,
thirteen. End while a preset is focused moves focus to B without selecting it;
Return activates it. The historical input-v2 save example retains its original
four-Tab geometry and is not silently rewritten as current evidence.

MIDI drawbar CCs retain their permanent B-bank edit targets. An edit received
while a fixed row sounds, or while that row is remembered during Cancel, leaves
raw fixed memory and routing unchanged. Explicit bank reselection clears the
fixed mode and reconnects the remembered live note owners. No new program-change
or MIDI-note preset mapping is implied.

## Save, live Load, cold Load and audio restart

The ordinary state writer emits canonical **B3CONTROLS4**, including
`registration_catalog atlas-chapel-nominal-v1 sha256` followed by the frozen
authoring identity, and `fixed_registration` on each manual record. Every older
1/2/3 input remains admitted under its original grammar and migrates fixed modes
to None. Native tests retain their original legacy input bytes; No-Save cases
require those bytes to remain unchanged.

Ctrl+S waits for acknowledged controls and writes the complete current state.
Ctrl+O restores those controls without releasing an existing note owner. A fresh
application loading the same bytes creates no held notes. Applying an audio
configuration deliberately performs the existing stopped lifecycle: controls,
including cancelled fixed memory, survive; notes are released and source phase
restarts. Fixed selection does not change that pre-existing lifecycle policy.
The exact state format is [documented separately](CONTROL_STATE_FORMAT.md).

The new native Save oracle is an independently written state4 literal. The
existing chapel bank-copy exporter continues producing its documented state3
output; native Ctrl+S is checked against a separate state4 grammar constructed
from the independent chapel rows. Exporting a chapel row into a bank is still a
different operation from selecting the immutable fixed registration.

## Replay acknowledgment and failure evidence

All existing replay delivery, sequence and completion requirements remain.
The two-second drain allowance has not been extended. Schema 3 additionally
copies these values **before ordinary shutdown cleanup**:

- `snapshot_available_before_shutdown` and `session_running_before_shutdown`;
- `controls_pending_before_shutdown` and `save_pending_before_shutdown`;
- `desired_controls_before_shutdown` alongside the existing applied
  `before_shutdown.controls`, sequence counters and `final_acknowledged`.

This preserves the predicates that can prevent completion even when the final
Session sequence looks current. MIDI CLI/runtime and modal assertion failures
now include bounded copied JSON before temporary files are removed. A successful
musical replay requires pending controls/save to be false and desired controls
to equal the acknowledged applied controls.

At baseline commit `35554c0`, the hosted macOS focus/resize/Help/MIDI test missed a
fully acknowledged observation in its `[400,590)` ms interval. The actual copied
run had correct external owners and completed successfully. UI observations are
sampled once per main-loop turn and unchanged snapshots may be omitted; that
interval had no qualified sampling-latency guarantee. The current test requires
four separately completed, acknowledged prefixes ending at 380, 590, 990 and
1750 ms. Each preserves its original action bytes/order, required note owners,
channel state and final acknowledgment; the complete original script still runs.
This strengthens the intermediate-state requirement without assuming a display
or callback deadline.

The separate hosted modal Escape timeout was missing sufficient diagnostics to
identify its cause. A local ALSA-backed case can exercise expected enumeration
errors, but cannot establish CoreMIDI behavior. Its original failure remains
visible in the [baseline follow-up](development/2026-11-14-preset-continuation/BASELINE_REPLAY_FOLLOWUP.md);
actual hosted qualification is required before closing that gate. Neither a
passing dummy-driver run nor an unchanged retry proves physical MIDI/audio
behavior or timing.
