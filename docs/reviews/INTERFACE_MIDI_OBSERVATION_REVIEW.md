# Native MIDI observation review

A35, 2026-11-14. **The two failures are observation-oracle defects; no production
defect was established.** The [result record](../development/2026-11-14-interface-continuation/reports/a35-result.json)
identifies both frozen applications, fixtures, commands and retained evidence.

## Diagnosis

The coherent Release gate passed 146/147 suites. Its MIDI suite failed two
assertions while both final musical states were correct. The
[decoded original failures](../development/2026-11-14-interface-continuation/reports/a35-original-failures.json)
retain the diagnostics and compact sequence traces; the original CTest log remains
unchanged.

For paired controls, the fixture equated matching UI/MIDI schedule times with four
simultaneously pending commands. `ScriptedInput::pump` and MIDI replay sample time
separately. The main loop observes after UI delivery, and `process_midi` observes
again after every accepted packet. A callback can therefore acknowledge a UI edit
before a MIDI edit, or MIDI can become due before the next UI pump. Furthermore,
the first high CC16 repeats the initial B-bank value 8 and emits no snapshot. The
failed trace legitimately contains pending suffixes of three, followed by the UI
submission on another turn; all final controls are preserved.

For Panic, the exact acknowledged held state appears at **487 ms, sequence 7**,
outside the fixture's `[150,480)` window. The acknowledged empty state appears at
707 ms/sequence 11, and the correct reconnect/fresh-press result at sequence 13.
These are sampled software observations, not hardware deadline failures.

The prior first-UI gate passed this unchanged fixture. A35's first isolated
two-method probe also passed unchanged on the failing gate's pinned executable.
That outcome corroborates the scheduling dependence; it is not classified as a
repair.

## Corrected acceptance

Six controls runs complete the unedited prefix, each alternating edit phase, and
the full original script. They require exact whole controls, parameter/action
counts and command deltas **1/4/8/12/16/21** from the restored startup sequence.
Every new edit phase must include an actual unacknowledged control submission,
identified by source sequence, followed by complete acknowledgement. Suffix size
does not assert simultaneous delivery. The existing deterministic
`external_control` and `midi_session` gates retain controlled pending-UI/MIDI
coverage; both passed in the original coherent gate.

Three Panic runs complete the held, Panic/repeat-suppression and reconnect
prefixes. They verify exact notes, accepted counts, closed-input behavior,
retirements and command deltas **4/8/10**. The full original input order and times
remain the final case. Shutdown cannot substitute for any phase's result.

The 2,000 ms application drain, nine-second process timeout, FIFO acceptance,
global `assert_window` helper and ten other methods are unchanged.

## Verification and limits

| Application | Fixture | Observed result |
|---|---|---|
| Pinned A28 `55b094…` | Original | Two focused methods pass, 3.600 s; original failures retained |
| Pinned A28 `55b094…` | Corrected | **12/12 methods, 24 native processes, 29.231 s** |
| Copied A31 `968938…` | Corrected | **2/2 changed methods, nine native prefixes, 9.562 s** |

Strict Python parsing/compilation and whitespace checks pass. The
[evidence bundle](../development/2026-11-14-interface-continuation/reports/a35-native-evidence.json)
preserves all 152 exact input, process and diagnostics files with hashes. No
production source, build configuration or shared index was changed. SDL dummy
audio/video and synthetic MIDI establish software behavior only; physical
devices, callback deadlines and display timing remain unqualified.
