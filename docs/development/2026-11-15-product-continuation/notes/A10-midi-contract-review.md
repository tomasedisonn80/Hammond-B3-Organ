# A10 — independent MIDI contract review

Actual worker `/root/w02_a10_midi_contract_review`, wave 2. Read the complete
agent instructions, M0–M9 plan, session scope and both proposed MIDI contracts.
Reviewed source at `da48180390a9fd473643d1759c153cb9d37ecfb6`, including
Session admission/application/recovery, both ownership APIs, Engine contact and
percussion routing, MIDI decoding, UI acknowledgment, native reconnect/replay,
modal handling and CLI validation. Product sources remain the initial baseline.
This is source/contract review, not execution of the proposed behavior.

## Result

**Both contracts are suitable for implementation**, with the explicit
clarifications below. No required sound-state migration or generic core change
was found. The parent's baseline 166/166 result does not qualify these features.

- `Session::prepare` uses the two-argument Engine preparation, whose legacy
  console model has ideal contacts. Ordinary final-owner release immediately
  opens those contacts. Engine rebuilds sustained and borrowed-percussion
  coefficients before the next rendered sample, while shared source phases and
  percussion history continue. Thus the distinct Session-only `ScopedSoundOff`
  reduction is valid for the declared native path. A surviving same-key owner
  remains sounding; this is required isolation, not a failed global mute.
- Append the variant alternative after the four existing alternatives. Validate
  domain, bus and channel before queue/sequence reservation. Both manual and
  **pedal namespaces have two buses, 0 and 1**; MIDI's pedal mapping uses only
  bus 0. Test valid pedal bus 1 as well as rejection of bus 2 and channel 16.
- The existing `process_midi` Session-command branch uses `post_midi_command`,
  bypassing `UiModel::submitted`. Preserve that route: a rejected MIDI command
  must not accidentally become `ReleaseUiNotes`. Queue faults still enter the
  documented recovery and transport-retirement path.
- A future non-ideal-mode refusal inside `apply` triggers Session's existing
  **global recovery**, not a harmless scoped no-op. The defensive guard prevents
  a false immediate-silence claim; it does not qualify non-ideal behavior or
  preserve other owners on that unsupported path. State this consequence when
  implementing/documenting the guard.
- CC121 through `external_parameter(8192, 1.0)` preserves unrelated desired
  controls and existing pending acknowledgment. Bypassing calibration is
  necessary with inversion. The global-expression effect and unchanged CC123
  nonzero-value compatibility are explicit and internally consistent.
- Calibration validation precedes subtraction/narrowing; defaults retain exact
  division by 127. Epoch immutability prevents queued bytes from being
  reinterpreted. Existing retirement joins the producer, clears the inbox and
  waits for scoped releases before reopening, making the proposed lifecycle
  coherent. Audit every `MidiRequest` aggregate and replay connect call.
- Resolve one UI precedence ambiguity explicitly: validate selected endpoints
  before synthetic replay's Apply early-return if invalid Apply must show an
  error everywhere. Valid synthetic Apply remains a script-owned no-op. Neither
  case may change configured/active calibration or send expression events.

Only this note was written. No product edits, builds, runtime tests, publication
or physical-device qualification were performed.
