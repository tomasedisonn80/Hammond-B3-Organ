# Read-only Service and Rotary inspection contract

Contract: `standalone-inspection-v1`, for the [interface continuation](INTERFACE_CONTINUATION_SCOPE.md).
Reviewed source: `d493e998e5dd7cf44db46854e87309745063ac54`.
This is an implementation contract; authoring it does not establish acceptance.

## Scope

Service shows which model is running, which copied settings are applied and what
remains unavailable. It has six simultaneous read-only cards: Generator,
Contacts/routing, Scanner, AO-28, Leslie and Retained controls (atlas p. 413).
Rotary displays the retained decorative cabinet and honest connection facts.
Neither body adds focus IDs, sound commands, fake knobs, profile editing,
waveforms, parts-tree selection or physical telemetry. The atlas explicitly
prioritizes an evidence-only inspector before those richer workflows (pp. 421-426).

The [workspace contract](INTERFACE_WORKSPACE_CONTRACT.md) owns navigation and
input. Global computer-key playing can continue while inspecting; this data model
never receives input or releases notes. Actual audio/MIDI device status continues
through the existing `InstrumentViewInfo` and common status display; do not create
a second device observation or settings model here.

## Small SDK-free API

Implement `apps/standalone/InspectionModel.h/.cpp` in
`hammond_standalone_support`. Include `UiModel.h` and standard-library headers,
without SDL, `Drawing.h`, a device backend or a host SDK. The public shape is:

```cpp
enum class InspectionSection : std::uint8_t {
    Generator = 0, ContactsRouting = 1, Scanner = 2,
    Ao28 = 3, Leslie = 4, Controls = 5,
};
enum class InspectionSnapshotState : std::uint8_t {
    Unavailable, Unprepared, Retained, Stopped, Current,
};
enum class InspectionAvailability : std::uint8_t {
    Available, NotObserved, NotIntegrated, NotAcquired, Invalid,
};
enum class InspectionEvidence : std::uint8_t {
    Software, Documented, Derived, Proposed, Unknown,
};
inline constexpr std::size_t kInspectionSectionCount = 6;
inline constexpr std::size_t kInspectionRowsPerSection = 6;
inline constexpr std::size_t kInspectionRotaryRows = 6;
inline constexpr std::size_t kInspectionTextCapacity = 128;

struct InspectionText {
    std::array<char, kInspectionTextCapacity> bytes{};
    std::uint16_t size{0};
    bool truncated{false};
    [[nodiscard]] std::string_view view() const noexcept;
};
struct InspectionRow {
    std::string_view id{};       // Stable literal; not a sound parameter ID.
    std::string_view label{};
    InspectionText value{};     // Owns every dynamic byte.
    std::string_view unit{};
    std::string_view source{};   // Literal code/atlas locator.
    InspectionAvailability availability{InspectionAvailability::NotObserved};
    InspectionEvidence evidence{InspectionEvidence::Unknown};
};
struct InspectionCard {
    InspectionSection section{InspectionSection::Generator};
    std::string_view title{};
    std::string_view summary{};  // Short limitation, readable independently.
    std::array<InspectionRow, kInspectionRowsPerSection> rows{};
    std::size_t row_count{0};
};
struct InspectionRuntimeInfo {
    bool snapshot_available{false};
    bool snapshot_read_succeeded{false};
};
struct InspectionDocument {
    InspectionSnapshotState snapshot_state{InspectionSnapshotState::Unavailable};
    bool controls_pending{false};
    std::uint64_t frame_clock{0};
    std::uint64_t publication_revision{0};
    InspectionText profile_id{};
    InspectionText profile_authoring_sha256{};
    std::array<InspectionCard, kInspectionSectionCount> sections{};
    std::array<InspectionRow, kInspectionRotaryRows> rotary_rows{};
    std::size_t rotary_row_count{0};
};
[[nodiscard]] InspectionDocument make_inspection_document(
    const RuntimeProfile& profile, const UiViewState& view,
    const InspectionRuntimeInfo& runtime) noexcept;
```

All `string_view` output fields refer to program-lifetime literals. Dynamic
profile/value text is copied into the document; it never borrows an input buffer.
`InspectionText::view()` returns `size` bytes, followed in storage by a NUL; at
most 127 payload bytes are stored. Overflow is visibly truncated with `...` and
sets `truncated`. This fixed object needs no heap allocation, file read, resource
initialization, lock or callback. Formatting remains main-thread work even though
its storage is bounded. No function receives a live Engine or Session reference.

## Observation and model truth

The caller passes its immutable profile used for the current successful prepare
and the UI's already copied state. There is no concurrent profile activation in
this slice. Before preparation, call its ID the **loaded profile**, not an active
graph. The authoring digest is retained declared provenance, not proof that the
unseen authoring file or a physical specimen was verified.

`snapshot_available` records whether the application obtained a coherent copy;
`snapshot_read_succeeded` records its most recent bounded read attempt for this
paint cycle. The application supplies these beside its existing observation
path. The inspector makes no second read and needs no new audio instrumentation
or change to `SessionSnapshot`.

Classification precedence is: no copy → `Unavailable`; copied `prepared == false`
→ `Unprepared`; latest read failed → `Retained`; copied `running == false` →
`Stopped`; otherwise `Current`. Unavailable/unprepared applied readouts say
**Not observed**, never a fictitious zero. Retained values remain visible with
**Retained snapshot**, frame and publication revision. Stopped state is explicit.
A nonzero frame/revision is not a freshness test. These are copied software
observations, not physical timing, health, latency or deadline measurements.

Applied musical values come only from `view.applied.controls` and held arrays.
`view.controls` may be pending desired state and must not be shown as applied.
The document copies `view.controls_pending` separately. Edit-bank labels use
`view.edited_banks` and explicitly identify presentation state. Held counts count
logical targets, not owners, physical contacts or guaranteed audible notes.

The actual `Session::prepare()` calls `Engine::prepare(profile, spec)`, which
selects `make_legacy_console_model()`: the standalone contact family is therefore
**`ideal-contacts-v1`**, from `kIdealContactModelId`. Do not display the separately
available linear-travel model or its synthetic 8/12 ms defaults as active.
`RuntimeProfile` contains no contact, percussion, scanner or Leslie parameters.
`kPercussionModelId` identifies the nominal shared-readiness family; readiness
history itself is absent from `SessionSnapshot` and is unavailable to this view.

The generator family is `ideal-shared-sine-v1`, documented in `TonewheelBank.h`.
One local literal is permitted because no exported constant exists. Actual source
frequencies and output gain come from the supplied profile. Do not hardcode 440 Hz,
12-TET tuning, gain or default registrations into live value rows.

## Six Service cards

Each card has at most six short rows plus a short limitation summary. The exact
row IDs below are stable; wording/layout may improve without changing meaning.
All rows retain static source locators. The renderer does not need to print C++
paths on every card. Full source metadata and hashes remain in the owned model
for diagnostics; do not shrink user-facing text to fit them all on screen.

| Card | Required row IDs | Source and meaning |
|---|---|---|
| Generator | `generator.model`, `.sources`, `.tone46_hz`, `.output_gain` | Family above; `kToneSourceCount`; `profile.sources[45].frequency_hz` in Hz; `profile.output_gain` in normalized amplitude. Loaded model quantities remain proposed/unmeasured. Sources: `Profile.h`, `TonewheelBank.h`, atlas pp. 61-72. |
| Contacts/routing | `contacts.model`, `.upper_held`, `.lower_held`, `.pedals_held`, `.inventory`, `.pedal_model` | `kIdealContactModelId`; true-target counts from the applied arrays; constants 61 + 61 keys and 25 pedals; `kNominalPedalVoiceModelId`. Summary distinguishes targets from audibility and nominal mixtures from a measured reactor. Sources: `Session.h/.cpp`, `ContactBank.h`, `PedalVoice.h`, atlas pp. 37-42, 115-120, 139-144. |
| Scanner | `scanner.audio`, `.research_model`, `.physical_capture` | **Not connected** / `NotIntegrated`; `kScannerLineModelId` explicitly **research module only**; specimen captures **Not acquired**. Sources: `Engine.cpp`, `ScannerLine.h`, `SCANNER_HANDOFF.md`, atlas pp. 157-192. Do not embed changing test counts or invent a selected active mode. |
| AO-28 | `ao28.circuit`, `.percussion_model`, `.specimen`, `.voltage` | Complete circuit **Not connected**; `kPercussionModelId` is a nominal surrogate, not a full AO-28; specimen/revision **Not acquired**; voltage **Unavailable**, unit V. Sources: `ConsoleModel.h`, `Percussion.h`, `PLAN.md`, atlas pp. 193-252. |
| Leslie | `leslie.audio`, `.target`, `.horn_speed`, `.drum_speed`, `.microphone` | Audio **Not connected**; documentary target **122 baseline; 147 separate**; both speeds **Unavailable**, unit rpm; microphone geometry **Not acquired**, unit m. The target is not an installed specimen. Sources: `PLAN.md`, `ROTARY_SCOPE.md`, atlas pp. 253-348. |
| Retained controls | `controls.upper`, `.lower`, `.banks`, `.pedals`, `.expression`, `.percussion` | Upper/lower each combine **Sound [effective selection] / Edit [UI bank]**; all four applied nine-position bank strings; two nominal pedal positions; applied expression 0..1; four applied percussion choices plus Upper-B eligibility. Sources: `ControlState.h`, `FixedRegistration.h`, `UiModel.h`, atlas pp. 109-156, 397-402. |

Derive effective applied selection with `control_preset_selection()` after
validation. Cancel retains the remembered bank and fixed mode; display **Cancel**
without zeroing memory or claiming held notes were released. `controls.banks`
uses Upper A/B then Lower A/B order, for example
`UA 000000000 / UB 888000000 / LA 000000000 / LB 008000000`.
These are applied retained memories, not substituted fixed-registration taps.
The compact row may wrap once. The profile summary may identify
`kParameterCount` (currently 47) and `B3CONTROLS4`, without using the atlas's
superseded proposed 62-entry registry.

Percussion eligibility is exactly: upper route enabled, upper fixed mode None,
and selected upper bank B. Retained enable and eligibility remain separate;
neither is a current capacitor/charge/readiness or transient measurement.

## Rotary rows and evidence labels

The six read-only Rotary rows are:

| ID | Required value and boundary |
|---|---|
| `rotary.path` | **Nominal dry organ; cabinet audio not connected** (`NotIntegrated`), from the current Engine/Session path. |
| `rotary.target` | **Leslie 122 baseline; 147 separate** (`Documented`), atlas pp. 55-60, 253-264; no specimen identity implied. |
| `rotary.artwork` | **Atlas concept, decorative** (`Documented`), `docs/design/atlas-reference.json`, PDF cover/p409; no calibrated dimensions. |
| `rotary.speeds` | **Horn unavailable / Drum unavailable** (`NotIntegrated`), unit rpm. Neither zero nor documentary nominal speeds are current state. |
| `rotary.microphone` | **Not acquired** (`NotAcquired`), unit m; no integrated pose control or measured microphone scene. |
| `rotary.brake` | **Not modeled** (`NotIntegrated`); Slow/Fast baseline differs from an optional Stop/brake accessory (pp. 256, 289, 413). |

The Rotary summary states that no specimen captures qualify physical fidelity.
Read-only unknowns must look like information rather than enabled knobs. Camera
coordinates do not become microphone coordinates, and artwork supplies no rotor
telemetry. `Software` means observed software or compiled implementation fact;
`Proposed` identifies unmeasured model choices; `Documented` has a source;
`Unknown` accompanies missing physical evidence. Availability and evidence are
independent. There is intentionally no `Measured` badge in this initial API.

## Formatting and independent acceptance

Use locale-independent unsigned decimal for counts and at most six significant
decimal digits for frequency, gain and expression. Units remain separate. Display
rounding never changes inputs; display-only negative zero may read `0`. Validate
applied `ControlSnapshot` and edited-bank
enums before indexing; invalid dependent rows say **Invalid snapshot** or
**Invalid edit bank**, rather than falling back to defaults. Nonfinite or
out-of-domain displayed numbers say **Invalid**, never `nan`, infinity or zero.

Read bounded profile arrays only within their capacity; missing termination is
invalid. The current profile grammar accepts exactly `kNominalProfileId` with
zero-filled remaining storage and a 64-character lowercase hexadecimal digest.
Another ID is unsupported in this slice, not an active replacement profile.
Unexpected control/non-ASCII bytes must not become multiline/control injection;
mark invalid identity visibly. All valid profile identifiers and 64-character
digests fit without truncation. No arbitrary device strings enter this API;
the existing device display keeps its own text handling.

Required independent cases are:

- All five snapshot states and precedence; missing observations never shown as
  current zeros, and failed reads visibly retain prior frame/revision.
- Different valid digest, source-46 frequency and gain arguments; actual values
  replace defaults, while the active standalone contact family stays ideal.
  A different/invalid profile ID is visibly unsupported instead of being silently
  relabeled as the nominal profile.
- Conflicting desired/applied state, fixed selection, Cancel and four unequal
  bank memories; applied routes, raw memories, UI edit banks and pending state
  remain distinct. Cover every percussion eligibility boundary and held counts.
- Invalid enums/nonfinite numbers, malformed or unterminated profile identity
  arrays, capacity boundaries, counted-row bounds, value ownership and immutable
  input. Identical inputs produce identical documents without side effects.
- Every stable row ID, source, availability, unit and evidence label. No false
  connected scanner/Leslie, physical `Measured` claim, numeric unknown or fake
  health diagnosis. Compile the inspection tests in the SDK-free configuration.

Native raster/interaction acceptance separately checks readable six-card layouts,
visible profile/pending/snapshot status, actual existing device status, no hidden
performance targets and preserved musical continuity. A UI frame stall cannot
block audio. Native accessibility, detailed parts selection, profile drafting,
analysis, measured overlays and physical calibration remain later work.
