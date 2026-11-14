# Native workspace contract v1

Contract identity: `standalone-workspaces-v1`.
Source baseline: `d493e998e5dd7cf44db46854e87309745063ac54`.
Scope: [interface continuation](INTERFACE_CONTINUATION_SCOPE.md), M9 presentation
only. This is the wave-2 implementation contract. Its acceptance gates below
are requirements, not claims of executed or completed implementation.

## Source and state boundary

Atlas pp. 34, 105-106, 379, 389, 412, 415-417 and 421-426 require presentation
to consume copied state and preserve musical histories. The fresh six-reader
coverage is retained in the [session](development/2026-11-14-interface-continuation/README.md).
Pages 409-411 and 431 require correct musical labels/inventory when the concept
art is inaccurate. Pages 433 and 438 require a separately qualified native
accessibility bridge; keyboard-operable SDL controls do not establish that gate.

This slice has **three workspaces over the same UiModel and Session**. It does
not create another engine, clock, registration copy, parameter namespace or
device connection. The current 47 sound parameters, state4 writer, readers 1-3,
model identities, fixed-registration catalog and native VST3 remain unchanged.
Workspace and presentation selections are transient main-thread UI state and
are not serialized by `B3CONTROLS4` or published through sound parameters.

| Workspace | Body | Sound/input relationship |
|---|---|---|
| Play | Current live drawbars, fixed/preset octaves, percussion/expression, two manuals, pedals and optional cabinet column. | All existing controls remain available with their original meanings. |
| Rotary | Cabinet/reference inspection and explicit implementation/evidence status. | Read-only body. Rotary audio remains unconnected; no fake speed, microphone, Stop or drive control. |
| Service | Six simultaneous read-only subjects: generator, contacts/routing, scanner, AO-28, Leslie and retained controls. | Uses copied data under the inspection contract. No editable draft values or additional focus targets in v1. |

The ten common header controls remain visible in every workspace. Global
computer-piano playing and F1/F2/F3/octave shortcuts remain operational in all
three workspaces, enabling Service monitoring while playing. New pointer,
focus/Space or direct-semantic activation of hidden performance controls is
rejected outside Play. The global keyboard mappings are documented shortcuts,
not invisible pointer targets.

## Frozen SDK-free declarations

The following public names belong in `apps/standalone/UiModel.h`. Append enum
values; preserve the numeric values of existing `UiControlKind` and `UiKey`
members. `UiKey::Count` remains last and grows with the new members.

```cpp
inline constexpr std::size_t kUiWorkspaceCount = 3;
inline constexpr std::size_t kUiCommonControlCount = 10;
inline constexpr std::size_t kUiMaxControls = 68;

enum class UiWorkspace : std::uint8_t { Play = 0, Rotary = 1, Service = 2 };
enum class UiPresentation : std::uint8_t { Dimensional = 0, Flat = 1 };

// Append after the existing PresetKey = 19:
// UiControlKind::Workspace = 20
// UiControlKind::Presentation = 21
// Append UiKey::F4, F5, F6, F7 before Count.

// Append to UiViewState:
// UiWorkspace workspace{UiWorkspace::Play};
// UiPresentation presentation{UiPresentation::Dimensional};
// std::array<UiControlId, kUiWorkspaceCount> workspace_focus{};

// Append to UiLayout:
// UiWorkspace workspace{UiWorkspace::Play};
// UiPresentation presentation{UiPresentation::Dimensional};
// UiRect workspace_panel{};

[[nodiscard]] bool make_ui_layout(
    float width, float height,
    const std::array<DrawbarBank, kManualCount>& edited_banks,
    UiLayout& destination,
    UiWorkspace workspace = UiWorkspace::Play,
    UiPresentation presentation = UiPresentation::Dimensional) noexcept;

[[nodiscard]] bool ui_control_visible(
    const UiLayout& layout, UiControlId control) noexcept;

// New UiModel members:
// [[nodiscard]] bool set_workspace(UiWorkspace workspace) noexcept;
// [[nodiscard]] bool set_presentation(UiPresentation presentation) noexcept;
```

`Workspace` IDs use canonical unused fields `manual=Upper`, `bank=A` and
`index=0..2`, corresponding exactly to the workspace enum. `Presentation` uses
canonical `manual=Upper`, `bank=A`, `index=0` and toggles Dimensional/Flat.
Malformed enum or semantic values are rejected before indexing any array.
`ui_parameter_id` returns false for both new kinds and preserves its destination.
There is no new `UiAppRequest` or Session command for either operation.

The existing four-argument `make_ui_layout` call remains source-compatible and
means Play/Dimensional. Invalid dimensions, bank values, workspace or presentation
leave the destination unchanged. UiModel construction is Play/Dimensional with
no initial focus, retaining the current default instrument behavior. Native
startup may use the two setters after parsing explicit view options.

The setters return true for a valid value, including a no-op selection; false
for an invalid enum or failed candidate layout, preserving all state on failure.
An idempotent setter does not end a gesture or alter focus. A real change prepares
the complete candidate layout before committing its presentation fields.
Successful switching returns no `UiActions` and posts no Session command.

## Layout, visibility and navigation order

The layout retains **all 68 ordinary control records** and the current 147 playing
key records so changing view does not destroy musical/semantic identities. The
new control inventory is the original 64 plus three workspace tabs and one
presentation toggle. Rotary/Service hide the performance records rather than
replacing their IDs with inspection records.

`ui_control_visible` means a currently displayed semantic target: one of the
ten common controls in every workspace; one of the retained live controls or a
valid playing-key ID in Play; false for malformed IDs and everything else.
The legacy non-painted `SoundingBank` and `CancelManual` compatibility actions
remain directly activatable in Play, as before, but are not added to focus/hit
inventories and are rejected outside Play. Rendering, focus traversal and
hit-testing use the same current workspace visibility rule.

Freeze this control-array and Tab order:

1. Workspace Play, Rotary, Service.
2. Save, Load, Help, Audio, MIDI, Panic.
3. Presentation toggle.
4. Original performance-control order, unchanged relative to itself: each
   manual's Edit A/B, twelve preset keys and nine drawbars; percussion choices;
   expression; pedal mixtures; keyboard target; octave controls.
5. In Play only, the existing three roving playing-key stops: Upper, Lower, Pedals.

There are **71 focus stops in Play** and **10 in Rotary/Service**. Tab and
Shift+Tab wrap only within the visible set. Direct invalid/hidden activation
does not move focus or change any view/controls. Space cannot begin a new
audition from a hidden manual/pedal key. Arrow/Home/End navigation cannot reach
or edit a hidden performance control.

The three tabs occupy the left header group. The existing six tools occupy two
rows of three on the right: Save/Load/Help above Audio/MIDI/Panic. The title fits
between those groups; the nominal-output caption and the Flat toggle fit below
the title. The toggle's label is `FLAT`, with a visible selected state when Flat
is active. A service/rotary body uses `layout.workspace_panel`, spanning the
content width below the header and above the existing footer. It does not paint
over the shared header/footer or their hit regions. Exact responsive geometry
and projected-key containment follow the separate geometry contract.

Dimensional/Flat change appearance and the geometry described by that contract,
not inventory, meaning, sound state or keyboard mapping. Flat removes perspective
and ornamental depth where specified; it is a complete usable presentation,
not a screenshot or a reduced set of musical controls.

## Focus memory and transitions

`workspace_focus` retains each workspace's latest visible **non-Workspace**
focus. Moving through workspace tabs does not erase a remembered body/tool focus.
All other visible focus changes update the active workspace's entry. Initial
entries are None. On entry to a workspace, restore its remembered target if it
is still valid and visible; otherwise focus that workspace's own tab. In Play,
restoration retains the semantic manual, bank and key identity, including the
existing roving key indices. It never activates the remembered target.

Workspace activation must therefore run before the generic focus assignment in
`activate` and before pointer-down assigns the clicked tab as ordinary focus.
Do not overwrite the outgoing memory with the clicked tab before switching.
Selecting the already-active workspace leaves the current focus unchanged.
Switching presentation preserves the current focus and all workspace memories.
Resize preserves view/presentation, valid focus and remembered identities.

Shortcuts use the same setter path as pointer/Tab activation:

| Key | Operation |
|---|---|
| F4 | Enter Play. |
| F5 | Enter Rotary. |
| F6 | Enter Service. |
| F7 | Toggle Dimensional/Flat. |
| F1/F2/F3 | Retain Upper/Lower/Pedals computer-key target in every workspace. |
| `[` / `]` | Retain existing octave operation in every workspace. |
| Computer-piano keys | Retain original press/owner behavior in every workspace. |
| Tab / Shift+Tab | Traverse the active workspace's visible focus set. |

As with existing shortcuts, key-repeat, a still-down/suppressed physical key,
text-entry/modal state and Ctrl/Alt/Meta suppress new F4-F7 actions. Shift alone
does not change their meaning. Every physical release is processed before all
these gates. The native SDL mapping and replay key-name admission must add F4-F7
without changing existing `B3UIREPLAY1` event meanings or bounds. Native Help and
`--help` must describe the new mappings.

## Held ownership and gesture closure

Changing workspace or presentation sends **no** note-off, ReleaseUiNotes, Panic,
ControlSnapshot, bank selection or engine operation. It changes no desired/applied
controls, dirty/pending flags, pending sequence, active keyboard owners, pointer
note owner, Space audition owner, or Session/DSP history. Existing external MIDI
admission and asynchronous snapshot acknowledgement continue normally.

On a real workspace/presentation change or successful resize:

- Close any current parameter drag against its captured parameter identity; do
  not apply its final pointer position to another bank/control and do not emit a
  compensating audio command.
- If the pointer is down, suppress subsequent Move handling until its original
  Up/CaptureLost. This prevents a closed parameter drag from becoming a keyboard
  glissando and prevents a hidden held note from changing when a panel moves.
- Preserve an existing pointer note and its original capture/owner until Up or
  the already-defined capture-loss/recovery/close handling releases it. Preserve
  the capture flag until that terminal event; this keeps the adapter able to
  receive an Up outside the window.
- Preserve existing computer-key and Space holds. Their original Up releases
  exactly the captured target/owner even after view, focus, target, octave,
  presentation, modifier or modal changes.

Pointer Up and CaptureLost retain their current early release path regardless
of workspace or pointer position. Focus loss, Escape, Panic, window close and
Session recovery retain their existing explicit musical release semantics;
presentation switching must not call those paths implicitly.

An input begun outside Play on a non-header body location remains suppressed
through subsequent Move events, including after returning to Play, until its
original Up. A new deliberate pointer Down is required to start a new gesture.
While a saved pointer is suppressed, a second Down cannot replace its owner.

## Native integration and copied inspection

The main loop continues to own the one UiModel. It maps F4-F7 and paints the body
selected by `model.view().workspace`. Common controls and overlays remain
functional in every workspace. Opening a pre-existing Audio/MIDI/Help modal
retains that modal's established behavior; closing it returns to the current
workspace without changing workspace selection. Modal keyboard navigation does
not operate underlying F4-F7 or performance controls.

New diagnostic presentation fields are separate from controls and have stable
string values `play|rotary|service` and `dimensional|flat`. Preserve all existing
diagnostic fields and their meanings. Any retained before-shutdown/capture view
record must identify the view actually painted; final shutdown observations
cannot substitute for that record. CLI parsing rejects unknown view values
before initializing devices or writing output. The integration author may add
`--workspace play|rotary|service` and `--flat` as optional startup choices, with
Play/Dimensional as defaults; neither changes sound-state loading.

Inspection reads `InspectionModel.h/.cpp` under the separate wave-2 inspection
contract. `make_inspection_document(const RuntimeProfile&, const UiViewState&,
const InspectionRuntimeInfo&) noexcept` returns a bounded value-owned document.
It receives copied UiViewState, immutable profile metadata and the two existing
snapshot-read outcome flags. Device facts remain in InstrumentViewInfo. Applied values come from `view.applied` only;
desired and pending values are separately labeled. It must not call Engine,
enumerate/open devices, advance model clocks, post commands or fill unknown
physical fields with zero. The read-only six-card body has no tab stops in v1.

## Required acceptance and preserved fixtures

1. **Semantic admission:** all new enum/ID boundaries, canonical unused fields,
   idempotent setters, invalid rollback, false parameter mapping, exact common
   inventory and 71/10 focus sets. Retain literal checks of all 47 sound IDs.
2. **Hidden-input rejection:** probe old drawbar/preset/manual/pedal locations in
   Rotary/Service; direct activation, Tab, Space and arrows cannot edit them.
   Header tools remain available. Global piano shortcuts still play correctly.
3. **Ownership through transitions:** hold keyboard, Space, pointer and
   independently owned MIDI notes; change view, presentation, octave and size;
   verify no switch command and one correct later release per original owner.
   Specifically move a held pointer after a closed drag/view change, including
   returning to Play before Up; no glissando or parameter edit may occur.
4. **State/audio isolation:** compare desired/applied control bytes, dirty and
   pending state, continuing source phase/percussion histories and deterministic
   PCM against equivalent no-navigation processing. Ordinary save bytes remain
   identical for otherwise identical controls. Load can still deliberately
   change sound controls from any workspace.
5. **Native route:** run actual replay using F4-F7 and header pointer targets;
   verify view observations, screenshots, modal return and final owner cleanup.
   Include minimum 960x700, default 1280x900, reference 1672x941 and the existing
   cabinet/bank breakpoints. Raster tests independently check drawn/hidden areas
   and live state; geometry tests use the shared projected boundaries.
6. **Publication:** retain source/binary/replay identities and actual captures of
   all views and Flat. Compare to the source concept, document residuals and
   update README and the current handoff. No acceptance above asserts literal
   pixel equality, physical fidelity or native screen-reader qualification.

Historical fixture captures and their hashes remain unchanged. Existing source
tests may update their literal 64/67 counts, expected Tab sequence, changed header
coordinates and newly projected key geometry to this explicit contract. Do not
weaken note, bank, preset, migration, pending/acknowledged, invalid-input or
failure-preservation assertions to accommodate the redesign. New replay fixtures
must identify their new UI source; archived screenshots remain dated evidence.
