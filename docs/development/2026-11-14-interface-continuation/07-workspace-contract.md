# A07 - Workspace API and lifecycle contract

Actual agent: `/root/w02_a07_workspace_contract`, wave 2.
Inspected source: `d493e998e5dd7cf44db46854e87309745063ac54` plus this session's
documentation overlay. This assignment owns only this note and
[INTERFACE_WORKSPACE_CONTRACT.md](../../INTERFACE_WORKSPACE_CONTRACT.md).

Read AGENTS, the current interface scope, all six wave-1 implications/acceptance
summaries and the actual UiModel declarations/implementation, native SDL key
mapping/replay admission, and existing literal UI/preset focus tests. No code,
build, cloned source, shared status file or prior evidence was changed.

## Frozen decisions

- Add presentation-only Play/Rotary/Service and Dimensional/Flat state; preserve
  all 47 sound parameter identities and state4/legacy bytes.
- Append Workspace=20 and Presentation=21 semantic IDs, with 68 ordinary control
  slots, 71 Play focus stops and 10 common stops in read-only Rotary/Service.
- Preserve four-argument layout calls via trailing default arguments. Provide
  atomic/idempotent workspace and presentation setters and shared visibility.
- Keep three workspace tabs left, six retained tools in two rows on the right,
  and a centered live title/caption plus Flat toggle.
- Preserve per-view semantic focus without overwriting it with navigation tabs.
- F4/F5/F6 select views and F7 toggles presentation. The parent explicitly
  confirmed that global computer-piano and F1/F2/F3/octave shortcuts stay live in
  every view for Service monitoring; hidden pointer/focus/direct performance
  activation is rejected.
- Every original Up remains paired with its original owner. View changes emit
  no sound command. Closing a drag on view/flat/resize suppresses all subsequent
  held-pointer Move until Up, preventing conversion to glissando.

Coordinated exact enum/field/layout APIs with A08 geometry and A09 inspection.
A08 retains key prefix fields and adds shared projected quadrilaterals; A09 uses
six simultaneous read-only inspection cards with no new body focus IDs.

## Concrete source risks identified

`UiModel::pointer` currently promotes Move to note glissando whenever capture
remains and no drag is active. Therefore merely clearing `drag_` on a view or
geometry change is insufficient: suppress that held gesture until its Up while
retaining any actual pointer-note owner. The existing early key-up and pointer-up
paths already establish the correct release-first pattern and must be preserved.

The current Tab array includes every stored control plus three playing-key stops.
It needs visibility filtering rather than just hiding the renderer, otherwise
hidden drawbars and preset keys remain actionable. Direct `activate` also needs
the non-Play visibility gate while preserving legacy compatibility actions in
Play. Header tool relocation and four new controls require explicit fixture
coordinate/count updates; musical assertions remain unchanged.

## Verification and next owner

This is source/requirements review and a concrete implementation contract only.
No CTest, native execution, screenshot, physical-device or accessibility pass is
claimed. The next owner implements UiModel/header/key admission from the contract;
independent workers must exercise hidden activation, focus memory, paired owner
release and parameter-drag closure. Parent integrator owns final contract
acceptance, coherent-source verification, manifest/status updates and publication.
