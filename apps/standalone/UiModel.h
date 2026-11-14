#pragma once

#include "Session.h"

#include "hammond/ControlState.h"
#include "hammond/ParameterBridge.h"
#include "hammond/PerformanceInput.h"

#include <array>
#include <cstddef>
#include <cstdint>
#include <span>
#include <string_view>
#include <variant>

namespace hammond::standalone {

// Frozen SDK-free interface; UiModel.cpp is a subsequent implementation task.
// Main-thread values only. Neither drawing nor input enters a live Engine.
inline constexpr std::string_view kUiModelId = "standalone-dry-ui-v1";
inline constexpr float kUiReferenceWidth = 1280.0F;
inline constexpr float kUiReferenceHeight = 900.0F;
inline constexpr float kUiMinimumWidth = 960.0F;
inline constexpr float kUiMinimumHeight = 700.0F;
inline constexpr float kUiMaximumDimension = 8192.0F;
inline constexpr std::size_t kUiVisibleDrawbars = kManualCount * kDrawbarCount;
inline constexpr std::size_t kUiMaxControls = 64;
inline constexpr std::size_t kUiMaxActions = 4;
inline constexpr std::uint8_t kUiNoteVelocity = 127;

struct UiColor {
    std::uint8_t red{0}, green{0}, blue{0}, alpha{255};
};

inline constexpr UiColor kUiCharcoal{0x24, 0x27, 0x25};
inline constexpr UiColor kUiIvory{0xF2, 0xE7, 0xCF};
inline constexpr UiColor kUiBrass{0xD6, 0xB6, 0x7C};
inline constexpr UiColor kUiFocusCyan{0xA5, 0xE4, 0xDF};
inline constexpr UiColor kUiWalnut{0x55, 0x36, 0x24};

inline constexpr std::array<std::string_view, kDrawbarCount> kUiFootageLabels{
    "16'", "5 1/3'", "8'", "4'", "2 2/3'", "2'", "1 3/5'", "1 1/3'", "1'"};
inline constexpr std::array<std::string_view, kPedalDrawbarCount> kUiPedalLabels{
    "Nominal mixture 1", "Nominal mixture 2"};
inline constexpr std::string_view kUiModelLabel = "NOMINAL DRY ORGAN";

struct UiPoint {
    float x{0.0F}, y{0.0F};
};

// Logical window units. Shared by painting and hit testing: left/top inclusive,
// right/bottom exclusive. Zero/negative extents are empty; border paint does not
// enlarge the hit region. Layout creation admits finite values only.
struct UiRect {
    float x{0.0F}, y{0.0F}, width{0.0F}, height{0.0F};

    [[nodiscard]] constexpr bool contains(UiPoint point) const noexcept {
        return width > 0.0F && height > 0.0F && point.x >= x && point.y >= y &&
               point.x < x + width && point.y < y + height;
    }
};

enum class UiTarget : std::uint8_t { Upper, Lower, Pedals };

// Manual notes use MIDI 36..96; pedals use one-based IDs 1..25. The tagged
// value is never a tone-source number, physical terminal or array index.
struct UiNote {
    UiTarget target{UiTarget::Upper};
    std::uint8_t value{kMinManualMidiNote};

    [[nodiscard]] bool operator==(const UiNote&) const noexcept = default;
};

enum class UiControlKind : std::uint8_t {
    None,
    EditBank,
    SoundingBank,
    CancelManual,
    ManualDrawbar,
    PedalDrawbar,
    Percussion,
    Expression,
    KeyboardTarget,
    OctaveDown,
    OctaveUp,
    SaveControls,
    LoadControls,
    AudioSettings,
    Help,
    Panic,
    ManualKey,
    PedalKey,
    MidiSettings,
    PresetKey = 19,
};

// Semantic identity, independent of rectangle, ordinal in a list or focus.
// ManualDrawbar: manual/bank/index 0..8. Edit/SoundingBank: manual/bank.
// Percussion: index 0 enabled, 1 harmonic, 2 volume, 3 decay.
// PedalDrawbar: index 0..1. KeyboardTarget: index Upper=0, Lower=1, Pedals=2.
// ManualKey: manual/index 0..60. PedalKey: index 0..24. Irrelevant fields are
// canonical defaults. PresetKey: manual/index 0..11, canonical unused bank A;
// all twelve keys of a manual target its one preset-selection parameter.
// SoundingBank and CancelManual remain semantic compatibility actions only.
struct UiControlId {
    UiControlKind kind{UiControlKind::None};
    Manual manual{Manual::Upper};
    DrawbarBank bank{DrawbarBank::A};
    std::uint8_t index{0};

    [[nodiscard]] bool operator==(const UiControlId&) const noexcept = default;
};

struct UiControlGeometry {
    UiControlId id{};
    UiRect bounds{};
    UiRect label_bounds{};
    UiRect value_bounds{};
    UiRect track{}; // Empty except for drawbars and expression.
};

struct UiKeyGeometry {
    UiNote note{};
    UiRect bounds{};
    bool accidental{false};
};

// A single layout owns every visible/hit rectangle. Draw naturals first and
// accidentals last; hit-test accidentals first. Arrays are in ascending pitch
// or pedal-ID order. The 64 control slots include 24 PresetKey controls and
// exclude the 147 playing-key slots. Presets also paint natural-first and hit
// accidental-first, independently of their semantic insertion order.
struct UiLayout {
    float width{kUiReferenceWidth}, height{kUiReferenceHeight};
    bool show_cabinet{false};
    bool bank_controls_in_cheeks{false};
    UiRect header{};
    std::array<UiRect, kManualCount> registration_panels{};
    UiRect performance_panel{};
    UiRect keyboard_toolbar{};
    std::array<UiRect, kManualCount> manual_panels{};
    UiRect pedal_panel{};
    UiRect footer{};
    UiRect cabinet_panel{};
    UiRect cabinet_art{};
    std::array<UiRect, kManualCount> manual_rail_panels{};
    std::array<UiControlGeometry, kUiMaxControls> controls{};
    std::size_t control_count{0};
    std::array<std::array<UiKeyGeometry, kManualKeyCount>, kManualCount> manual_keys{};
    std::array<UiKeyGeometry, kPedalCount> pedal_keys{};
    std::array<UiRect, kManualCount> preset_key_panels{};
};

// Validation failure preserves destination. The same function supplies the
// renderer and input handler; neither derives a second keyboard geometry.
[[nodiscard]] bool make_ui_layout(
    float width, float height,
    const std::array<DrawbarBank, kManualCount>& edited_banks,
    UiLayout& destination) noexcept;
[[nodiscard]] UiControlId ui_hit_test(const UiLayout& layout, UiPoint point) noexcept;
[[nodiscard]] bool ui_parameter_id(UiControlId control,
                                   std::uint32_t& destination) noexcept;

// SDL maps physical scancodes into this vocabulary before calling the model.
// A..Semicolon in this listed chromatic mapping span C..E (17 semitones):
// A W S E D F T G Y H U J K O L P Semicolon. Labels describe the US positions;
// an app may display local key names without changing captured press identity.
enum class UiKey : std::uint8_t {
    Unknown,
    A, W, S, E, D, F, T, G, Y, H, U, J, K, O, L, P, Semicolon,
    Tab, Left, Right, Up, Down, Home, End, Space, Enter, Escape,
    LeftBracket, RightBracket, F1, F2, F3,
    Count,
};

inline constexpr std::array<UiKey, 17> kUiPlayingKeys{
    UiKey::A, UiKey::W, UiKey::S, UiKey::E, UiKey::D, UiKey::F,
    UiKey::T, UiKey::G, UiKey::Y, UiKey::H, UiKey::U, UiKey::J,
    UiKey::K, UiKey::O, UiKey::L, UiKey::P, UiKey::Semicolon};
inline constexpr std::int32_t kUiKeyboardOwnerBase = 1;
inline constexpr std::int32_t kUiPointerOwnerId = 100;
inline constexpr std::int32_t kUiAuditionOwnerId = 101;

struct UiKeyInput {
    UiKey key{UiKey::Unknown};
    bool down{false};
    bool repeat{false};
    bool shift{false};
    bool control{false};
    bool alt{false};
    bool meta{false};
};

enum class UiPointerKind : std::uint8_t { Down, Move, Up, CaptureLost };

// One primary mouse pointer only in v1; multi-touch is a later adapter. The app
// requests capture for playing/drag gestures and forwards Up outside the window.
// Preset keys create no capture or note owner. Capture
// failure is delivered as CaptureLost. Coordinates already use logical units.
struct UiPointerInput {
    UiPointerKind kind{UiPointerKind::Move};
    UiPoint point{};
};

enum class UiReleaseReason : std::uint8_t { FocusLost, WindowClosing, Escape };
enum class UiAppRequest : std::uint8_t { SaveControls, LoadControls, AudioSettings, Help, MidiSettings };

// SessionCommand is the exact Session.h variant, not another wire protocol.
// Musical actions have offset 0 and target the next callback boundary. App
// requests execute on the main thread. No filename, SDL object or dynamic text
// crosses the audio boundary. Preserve array order, including glissando Off/On.
using UiAction = std::variant<SessionCommand, UiAppRequest>;

struct UiActions {
    std::array<UiAction, kUiMaxActions> items{};
    std::size_t count{0};

    [[nodiscard]] std::span<const UiAction> span() const noexcept {
        return {items.data(), count};
    }
};

struct UiHeldPress {
    bool active{false};
    UiNote note{};
    std::int32_t owner_id{-1};
};

struct UiDrawbarGesture {
    bool active{false};
    UiControlId control{}; // Captured permanent bank identity.
    std::uint32_t parameter_id{0};
    UiRect track{}; // Captured before drag; close gesture when layout changes.
};

// Complete fixed-size main-thread presentation state. controls is the latest
// desired whole snapshot; applied.controls is authoritative for SOUNDING and
// actual held-key indicators. Pending edits are labeled until resolved.
// Edit-bank/focus/octave/saved marker are never musical snapshot fields.
struct UiViewState {
    ControlSnapshot controls{};
    SessionSnapshot applied{};
    std::array<DrawbarBank, kManualCount> edited_banks{DrawbarBank::B, DrawbarBank::B};
    UiControlId focus{};
    std::array<std::uint8_t, kManualCount> roving_manual_keys{24, 24};
    std::uint8_t roving_pedal_key{0};
    UiTarget keyboard_target{UiTarget::Upper};
    std::uint8_t manual_base_midi{60}; // [36,84], multiples of 12.
    std::uint8_t pedal_octave{0}; // [0,2]; derived IDs outside 1..25 do not play.
    bool controls_pending{false};
    bool controls_dirty{false};
    bool text_entry_active{false};
    bool pointer_captured{false};
    bool input_recovery{false};
    SessionStatus last_submit_status{};
};

class UiModel {
public:
    UiModel() noexcept;

    [[nodiscard]] const UiViewState& view() const noexcept { return view_; }
    [[nodiscard]] const UiLayout& layout() const noexcept { return layout_; }

    // Finite sizes from minimum through kUiMaximumDimension; invalid input preserves state.
    // Resize closes a parameter drag, keeps note owners/focus and emits no audio.
    [[nodiscard]] bool resize(float width, float height) noexcept;
    [[nodiscard]] UiActions key(const UiKeyInput& input) noexcept;
    [[nodiscard]] UiActions pointer(const UiPointerInput& input) noexcept;
    [[nodiscard]] UiActions activate(UiControlId control) noexcept;
    [[nodiscard]] UiActions release_ui(UiReleaseReason reason) noexcept;
    [[nodiscard]] UiActions panic() noexcept;

    // Called after an off-callback parser has validated the existing file
    // format. Valid input emits one copied ControlSnapshot. Invalid input emits
    // no action and preserves state. Does not resurrect/release notes or change
    // the edited bank. The loaded snapshot becomes the clean-file reference.
    [[nodiscard]] UiActions load_controls(const ControlSnapshot& controls) noexcept;
    // Main-thread external controller edit. Uses the same desired snapshot and
    // acknowledgment path as native gestures, so a pending MIDI edit is retained
    // by subsequent unrelated UI changes. Invalid/unchanged values emit nothing;
    // the caller dispatches returned actions once, never a second raw CC event.
    [[nodiscard]] UiActions external_parameter(std::uint32_t parameter_id,
                                               double normalized) noexcept;
    void mark_saved(const ControlSnapshot& saved_controls) noexcept;
    void set_text_entry_active(bool active) noexcept;

    // Deliver every Session::post result immediately, in action order. Accepted
    // controls retain their sequence until acknowledged. On rejection, stop
    // dispatching the rest of the original batch and dispatch only the returned
    // recovery actions. InvalidCommand requests ReleaseUiNotes once; transport
    // overflow/recovery uses Session's out-of-band global recovery. No retry loop.
    [[nodiscard]] UiActions submitted(const SessionCommand& command,
                                     const SubmitResult& result) noexcept;

    // Snapshot observation never echoes a command. A newer recovery count clears
    // local gestures/owners and adopts applied controls. Held physical keys stay
    // suppressed until Up; focus restoration cannot automatically retrigger.
    void observe(const SessionSnapshot& snapshot) noexcept;

private:
    UiViewState view_{};
    UiLayout layout_{};
    ControlSnapshot saved_controls_{};
    std::array<UiHeldPress, kUiPlayingKeys.size()> keyboard_holds_{};
    UiHeldPress pointer_hold_{};
    UiHeldPress audition_hold_{};
    std::array<bool, static_cast<std::size_t>(UiKey::Count)> physical_keys_down_{};
    std::array<bool, static_cast<std::size_t>(UiKey::Count)> suppressed_keys_{};
    bool pointer_down_{false};
    bool pointer_suppressed_{false};
    bool invalid_release_requested_{false};
    UiDrawbarGesture drag_{};
    std::uint64_t pending_control_sequence_{0};
};

static_assert(kUiVisibleDrawbars == 18);
static_assert(kManualKeyCount == 61 && kPedalCount == 25);
static_assert(static_cast<std::uint8_t>(UiControlKind::MidiSettings) == 18);
static_assert(static_cast<std::uint8_t>(UiControlKind::PresetKey) == 19);
static_assert(kPresetSelectionCount == 12);
static_assert(kParameterCount == 47);

} // namespace hammond::standalone
