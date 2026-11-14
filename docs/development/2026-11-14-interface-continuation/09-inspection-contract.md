# A09 - Service and Rotary inspection contract

Actual assignment: `/root/w02_a09_inspection_contract`, wave 2, worker 09.
Owned outputs: `docs/INTERFACE_INSPECTION_CONTRACT.md` and this note only.

## Source inspected

Read `AGENTS.md`, the interface scope, the complete wave-1 product and completion
notes, current plan/status/next-step and development-log entry points, and the
actual `RuntimeProfile`, `SessionSnapshot`, `UiViewState`, controls, preset,
contact, percussion, pedal, parameter and generator declarations. Traced
`Session::prepare` into the default `Engine::prepare` overload and inspected
the application's existing copied-observation and paint bindings. Reread all
six original atlas text pages 421-426; relied on the separate wave-1 full-atlas
coverage for other chapter anchors.

Observed checkout HEAD `d493e998e5dd7cf44db46854e87309745063ac54`, committed tree
`3de6c3396ae0e826987e5994b2d00844d4f75706`. Other workers' documentation edits were
present and were preserved. The source PDF and all production files remain
unchanged by this assignment.

## Decisions and their consequences

The contract defines a small SDK-free `InspectionModel.h/.cpp` boundary for
the implementation worker: six simultaneous read-only cards with at most six
rows each, and six Rotary rows, all with stable row identities, source locators,
explicit availability/evidence, and fixed owned dynamic text. It accepts only
the immutable profile, copied UI state and two observation-status flags. Existing
`InstrumentViewInfo` remains the sole device-status presentation input.
There is no live Engine/Session reference, file read, backend enumeration,
sound command, physical-state mutation or selectable fake audio control.

Coordinated with A07: the Service/Rotary bodies remain read-only and introduce
no bespoke focus IDs; `UiLayout.workspace_panel` supplies their area. The ten
common header controls remain operable, and global computer-key playing may
continue while inspecting. The model itself never owns input or releases notes.

Three source findings prevent misleading presentation:

1. The standalone calls the default Engine preparation path and actually uses
   **`ideal-contacts-v1`**. A separately implemented synthetic linear-travel
   profile does not make its 8/12 ms defaults active. The Service model must show
   the prepared family's actual identity.
2. `RuntimeProfile` owns source frequencies/amplitudes, mapping and gain. It
   does not own contact/percussion/scanner/Leslie parameters. The contract reads
   actual profile values and compiled active family identifiers without claiming
   they are physical measurements or a complete circuit.
3. `view.controls` may be pending desired state; `view.applied.controls` is the
   copied applied state. The inspector distinguishes applied routes, retained
   banks, presentation-only edit-bank selection and pending acknowledgment.
   Held arrays count logical targets, not individual owners, physical contacts
   or guaranteed audible notes.

Snapshot state is explicit: unavailable, unprepared, retained after a failed
bounded read, stopped, or current. The document carries the last observed frame
and publication revision. No missing value becomes zero; there is no invented
RPM, angle, electrical scale, specimen, health diagnosis or `Measured` badge.
The application must supply the latest existing read outcome instead of letting
the inspector make a second reader or infer freshness from a nonzero clock.

The retained concept cabinet remains decorative and its audio unconnected.
Documentary 122/147 distinctions and optional brake status remain separate from
the actual running model. No camera coordinate or reference knob is promoted to
a functional microphone/rotor control.

## Validation plan and successor ownership

The contract supplies exact row IDs and sources plus prospective cases for
snapshot state precedence, conflicting desired/applied settings, fixed/Cancel
memory, percussion eligibility, profile-value substitution, unknowns and bounded
text. Independent tests must also exercise invalid values, malformed or
unterminated bounded profile identity arrays, immutable input and output ownership.
Native rendering/readability and musical continuity stay separate from the
SDK-free formatting checks.

The next implementation worker owns `InspectionModel.h/.cpp` under this contract;
the native integration worker binds it to the application's one observation
path. The independent acceptance worker should check factual sources and
adversarial input rather than merely repeat the formatter's string construction.
The integrator owns shared status, setup, CMake integration, source freeze and
publication. Any later physical telemetry or selectable draft/probe interface
needs a separately reviewed extension instead of silently filling these unknowns.

Only source/document inspection and authoring were performed. No build,
acceptance test, native capture, physical measurement, commit or push is claimed
by A09. The exact verification results belong to the subsequent implementation
and independent acceptance records.
