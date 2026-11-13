#pragma once

#include <SDL.h>

#include <array>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <string>
#include <string_view>

namespace hammond::standalone {

inline constexpr std::string_view kScriptedInputFormat = "B3UIREPLAY1";
inline constexpr std::size_t kScriptedInputMaxEvents = 256;
inline constexpr std::size_t kScriptedInputMaxBytes = 64 * 1024;
inline constexpr std::uint32_t kScriptedInputMinimumDurationMs = 250;
inline constexpr std::uint32_t kScriptedInputMaximumDurationMs = 10000;

enum class ScriptedInputKind : std::uint8_t {
    KeyDown, KeyUp, MouseDown, MouseMove, MouseUp, Resize, FocusLost, Quit,
};

struct ScriptedInputEvent {
    std::uint32_t at_ms{0};
    ScriptedInputKind kind{ScriptedInputKind::FocusLost};
    SDL_Scancode scancode{SDL_SCANCODE_UNKNOWN};
    SDL_Keymod modifiers{KMOD_NONE};
    bool repeat{false};
    int x{0}, y{0};
    int width{0}, height{0};
};

// Value-owned plan. Parsing and initialization validate every active record;
// failed parsing/loading leaves the destination unchanged. No Engine/DSP data.
struct ScriptedInputPlan {
    std::array<ScriptedInputEvent, kScriptedInputMaxEvents> events{};
    std::size_t event_count{0};
    std::uint32_t duration_ms{0};
};

[[nodiscard]] bool parse_scripted_input(std::string_view source,
                                      ScriptedInputPlan& destination,
                                      std::string& error);
[[nodiscard]] bool load_scripted_input(const std::filesystem::path& path,
                                     ScriptedInputPlan& destination,
                                     std::string& error);

// Optional SDL layer, main thread only. Initialize once, before entering the
// event loop; the live window must outlive this helper. No file I/O, waits,
// callbacks supplied by the script, or audio operations occur in pump().
class ScriptedInput {
public:
    ScriptedInput() = default;
    ScriptedInput(const ScriptedInput&) = delete;
    ScriptedInput& operator=(const ScriptedInput&) = delete;
    ScriptedInput(ScriptedInput&&) = delete;
    ScriptedInput& operator=(ScriptedInput&&) = delete;

    [[nodiscard]] bool initialize(const ScriptedInputPlan& plan, SDL_Window* window,
                                  std::string& error);
    // Posts each due action once in source order; a refused SDL push is a
    // sticky failure, with the accepted prefix retained in pushed_count().
    [[nodiscard]] bool pump(std::uint64_t elapsed_ms, std::string& error);
    // Call for each polled event before ordinary dispatch. True consumes this
    // helper's resize barrier or final marker. Only the final marker sets
    // delivered(): queue delivery, not Session acknowledgment.
    [[nodiscard]] bool acknowledge(const SDL_Event& event) noexcept;

    [[nodiscard]] std::size_t scheduled_count() const noexcept { return plan_.event_count; }
    [[nodiscard]] std::size_t pushed_count() const noexcept { return pushed_count_; }
    [[nodiscard]] std::uint32_t duration_ms() const noexcept { return plan_.duration_ms; }
    [[nodiscard]] bool delivered() const noexcept { return delivered_; }
    [[nodiscard]] bool failed() const noexcept { return failed_; }
    [[nodiscard]] bool completed(std::uint64_t elapsed_ms) const noexcept {
        return initialized_ && !failed_ && delivered_ && elapsed_ms >= plan_.duration_ms;
    }

private:
    [[nodiscard]] bool push(SDL_Event& event, std::string& error);
    [[nodiscard]] bool push_marker(std::string& error);
    [[nodiscard]] bool fail(std::string message, std::string& error);

    ScriptedInputPlan plan_{};
    SDL_Window* window_{nullptr};
    Uint32 window_id_{0};
    Uint32 marker_type_{0};
    std::size_t pushed_count_{0};
    std::size_t acknowledged_count_{0};
    std::uint64_t last_elapsed_ms_{0};
    int pointer_x_{0}, pointer_y_{0};
    bool pointer_position_known_{false};
    bool pointer_down_{false};
    bool initialized_{false};
    bool failed_{false};
    bool marker_pushed_{false};
    bool delivered_{false};
    std::string failure_{};
};

} // namespace hammond::standalone
