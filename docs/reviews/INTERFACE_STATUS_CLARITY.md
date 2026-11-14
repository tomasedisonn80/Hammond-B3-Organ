# Native status clarity — A36

**Outcome:** A30-G2 is corrected by one successful-Load message change. One native
replay and its inspected screenshot confirm the footer remains truthful after
acknowledgment. [Exact source, build and observation identities](../development/2026-11-14-interface-continuation/reports/a36-status-clarity.json)
qualify this working source independently of A30's older executable.

## The observed ambiguity and bounded correction

[A30-G2](INTERFACE_OPERATOR_AUDIT.md#a30-g2--replace-or-qualify-the-stale-load-waiting-message)
retains the original failure: Ctrl+O at 2100 ms was acknowledged at 2186 ms, but
the 3166 ms capture still displayed **Loaded controls; waiting for the audio
callback.** Its Service banner said **CURRENT SNAPSHOT** and copied
`controls_pending` was false. The original diagnostic, input, state and image
remain unchanged.

The only production change in `Application::load_state()` is **Loaded saved
controls.** This describes the successful file-load event. `message()` retains
its existing six-second notice duration. The pending indicators and applied
snapshot continue to describe application timing; no new state machine,
acknowledgment rule, audio operation or state format is introduced.

## Read the signals separately

The [inspection contract](../INTERFACE_INSPECTION_CONTRACT.md) defines this
classification order:

| Banner | Exact copied-state meaning |
| --- | --- |
| **SNAPSHOT UNAVAILABLE** | No coherent copy exists; applied values say **Not observed**. |
| **UNPREPARED SNAPSHOT** | A copy exists but is unprepared; applied values remain **Not observed**. |
| **RETAINED SNAPSHOT** | A prepared prior copy exists and the latest bounded read failed. Its frame/revision identify the retained observation. |
| **STOPPED SNAPSHOT** | The latest successful copy is prepared and stopped. |
| **CURRENT SNAPSHOT** | The latest successful copy is prepared and running. |

The precedence matters: failed latest reads of prepared stopped copies are
retained. A nonzero frame/revision is not a freshness guarantee. Current can
coexist with desired controls pending: the snapshot is coherent while a later
request still awaits acknowledgment. Service **Sound** uses applied controls;
**Edit** describes the UI bank. **DESIRED CONTROLS PENDING**, pending preset
outlines and contextual pending text remain independent of the timed notice.

Each row's **Availability** describes whether information is available, not
observed, not integrated, not acquired or invalid. **Evidence** describes
Software, Documented, Derived, Proposed or Unknown. Neither axis establishes
physical measurement. Voltage stays unavailable in V, rotor speeds unavailable
in rpm and microphone geometry unacquired in m; unknown does not become zero.
The cabinet artwork stays decorative and the scanner, full AO-28 and cabinet
audio remain unconnected. A static success notice cannot upgrade these facts.

## Verification boundary and next action

After A34's explicit release, `hammond_standalone` rebuilt in 7.74 seconds. The
327-path source inventory and pinned libraries/build settings stayed unchanged
during compilation. The [single-case observation](../development/2026-11-14-interface-continuation/reports/a36-load-evidence/result.json)
reused A30's exact Load journey, literal controls and strict schema/lifecycle
helper. Its one process passed in 3.23 seconds with zero application errors.
Controls were acknowledged at **2189 ms**; the **3162 ms**
[native Service image](../development/2026-11-14-interface-continuation/reports/a36-load-evidence/02-edit-save-live-load/frame.png)
shows **CURRENT SNAPSHOT**, no desired controls pending, and **Loaded saved
controls.** A36 opened and inspected the PNG; diagnostics independently record
the snapshot and pending state, not the static string. Exact saved bytes and
held-note continuity match A30. [Setup and commands](../development/2026-11-14-interface-continuation/session36-status-clarity.md)
are retained. A23's inspection-model and A28's value/raster gates were not repeated.

Source review found that Save's waiting notice is replaced by completion or
failure, while stopped-audio Load explicitly instructs the operator to start
audio. Neither is changed. Native MIDI scoped-release wording is an unexecuted
candidate for A37's operator review, not an additional established defect.
Error counters, last-error retention and failure paths are preserved. Dummy
SDL observations do not qualify physical audio/MIDI, display/DPI, accessibility,
deadlines, fidelity or reference-image equality. A37 should continue the final
operator flow on the newly identified executable.
