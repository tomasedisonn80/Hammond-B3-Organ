#include "ScriptedInput.h"

#include <charconv>
#include <limits>
#include <system_error>
#include <utility>

#if defined(_WIN32)
#ifndef NOMINMAX
#define NOMINMAX
#endif
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
#else
#include <cerrno>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#endif

namespace hammond::standalone {
namespace {

constexpr int kMinimumCoordinate = -8192;
constexpr int kMaximumCoordinate = 16384;
constexpr int kMinimumWidth = 960;
constexpr int kMinimumHeight = 700;
constexpr int kMaximumDimension = 8192;

struct KeyName {
    std::string_view name;
    SDL_Scancode scancode;
    SDL_Keycode keycode;
};

constexpr std::array<KeyName, 35> kKeys{{
    {"A", SDL_SCANCODE_A, SDLK_a}, {"W", SDL_SCANCODE_W, SDLK_w},
    {"S", SDL_SCANCODE_S, SDLK_s}, {"E", SDL_SCANCODE_E, SDLK_e},
    {"D", SDL_SCANCODE_D, SDLK_d}, {"F", SDL_SCANCODE_F, SDLK_f},
    {"T", SDL_SCANCODE_T, SDLK_t}, {"G", SDL_SCANCODE_G, SDLK_g},
    {"Y", SDL_SCANCODE_Y, SDLK_y}, {"H", SDL_SCANCODE_H, SDLK_h},
    {"U", SDL_SCANCODE_U, SDLK_u}, {"J", SDL_SCANCODE_J, SDLK_j},
    {"K", SDL_SCANCODE_K, SDLK_k}, {"O", SDL_SCANCODE_O, SDLK_o},
    {"L", SDL_SCANCODE_L, SDLK_l}, {"P", SDL_SCANCODE_P, SDLK_p},
    {"M", SDL_SCANCODE_M, SDLK_m},
    {"Semicolon", SDL_SCANCODE_SEMICOLON, SDLK_SEMICOLON},
    {"Tab", SDL_SCANCODE_TAB, SDLK_TAB},
    {"Left", SDL_SCANCODE_LEFT, SDLK_LEFT}, {"Right", SDL_SCANCODE_RIGHT, SDLK_RIGHT},
    {"Up", SDL_SCANCODE_UP, SDLK_UP}, {"Down", SDL_SCANCODE_DOWN, SDLK_DOWN},
    {"Home", SDL_SCANCODE_HOME, SDLK_HOME}, {"End", SDL_SCANCODE_END, SDLK_END},
    {"Space", SDL_SCANCODE_SPACE, SDLK_SPACE}, {"Return", SDL_SCANCODE_RETURN, SDLK_RETURN},
    {"Escape", SDL_SCANCODE_ESCAPE, SDLK_ESCAPE},
    {"LeftBracket", SDL_SCANCODE_LEFTBRACKET, SDLK_LEFTBRACKET},
    {"RightBracket", SDL_SCANCODE_RIGHTBRACKET, SDLK_RIGHTBRACKET},
    {"F1", SDL_SCANCODE_F1, SDLK_F1}, {"F2", SDL_SCANCODE_F2, SDLK_F2},
    {"F3", SDL_SCANCODE_F3, SDLK_F3},
    {"Comma", SDL_SCANCODE_COMMA, SDLK_COMMA}, {"Slash", SDL_SCANCODE_SLASH, SDLK_SLASH},
}};

[[nodiscard]] const KeyName* find_key(std::string_view name) noexcept {
    for (const auto& key : kKeys) {
        if (!key.name.empty() && key.name == name) return &key;
    }
    return nullptr;
}

[[nodiscard]] const KeyName* find_key(SDL_Scancode scancode) noexcept {
    for (const auto& key : kKeys) {
        if (!key.name.empty() && key.scancode == scancode) return &key;
    }
    return nullptr;
}

template <class Integer>
[[nodiscard]] bool integer(std::string_view text, Integer& destination) noexcept {
    if (text.empty() || text.front() == '+') return false;
    Integer candidate{};
    const auto result = std::from_chars(text.data(), text.data() + text.size(), candidate);
    if (result.ec != std::errc{} || result.ptr != text.data() + text.size()) return false;
    destination = candidate;
    return true;
}

[[nodiscard]] bool modifiers(std::string_view text, SDL_Keymod& destination) noexcept {
    if (text == "none") { destination = KMOD_NONE; return true; }
    unsigned int combined = 0;
    while (!text.empty()) {
        const auto separator = text.find('+');
        const auto part = text.substr(0, separator);
        unsigned int flag = 0;
        if (part == "shift") flag = KMOD_LSHIFT;
        else if (part == "ctrl") flag = KMOD_LCTRL;
        else if (part == "alt") flag = KMOD_LALT;
        else if (part == "meta") flag = KMOD_LGUI;
        else return false;
        if ((combined & flag) != 0) return false;
        combined |= flag;
        if (separator == std::string_view::npos) {
            destination = static_cast<SDL_Keymod>(combined);
            return true;
        }
        text.remove_prefix(separator + 1);
    }
    return false; // Empty input or a trailing '+'.
}

struct Tokens {
    std::array<std::string_view, 6> items{};
    std::size_t count{0};
};

[[nodiscard]] bool split(std::string_view line, Tokens& result) noexcept {
    while (!line.empty()) {
        const auto first = line.find_first_not_of(" \t");
        if (first == std::string_view::npos) return true;
        line.remove_prefix(first);
        if (result.count == result.items.size()) return false;
        const auto end = line.find_first_of(" \t");
        result.items[result.count++] = line.substr(0, end);
        if (end == std::string_view::npos) return true;
        line.remove_prefix(end);
    }
    return true;
}

[[nodiscard]] bool next_line(std::string_view& source, std::string_view& line) noexcept {
    if (source.empty()) return false;
    const auto end = source.find('\n');
    line = source.substr(0, end);
    if (!line.empty() && line.back() == '\r') line.remove_suffix(1);
    if (end == std::string_view::npos) source = {};
    else source.remove_prefix(end + 1);
    return true;
}

[[nodiscard]] bool line_error(std::size_t number, std::string_view message,
                              std::string& error) {
    error = "Input replay line " + std::to_string(number) + ": " + std::string(message);
    return false;
}

[[nodiscard]] bool valid_event(const ScriptedInputEvent& event) noexcept {
    switch (event.kind) {
    case ScriptedInputKind::KeyDown:
    case ScriptedInputKind::KeyUp: {
        constexpr auto allowed = static_cast<unsigned int>(KMOD_LSHIFT | KMOD_LCTRL | KMOD_LALT | KMOD_LGUI);
        return find_key(event.scancode) != nullptr &&
            (static_cast<unsigned int>(event.modifiers) & ~allowed) == 0 &&
            (event.kind != ScriptedInputKind::KeyUp || !event.repeat);
    }
    case ScriptedInputKind::MouseDown:
    case ScriptedInputKind::MouseMove:
    case ScriptedInputKind::MouseUp:
        return event.x >= kMinimumCoordinate && event.x <= kMaximumCoordinate &&
            event.y >= kMinimumCoordinate && event.y <= kMaximumCoordinate;
    case ScriptedInputKind::Resize:
        return event.width >= kMinimumWidth && event.width <= kMaximumDimension &&
            event.height >= kMinimumHeight && event.height <= kMaximumDimension;
    case ScriptedInputKind::FocusLost:
    case ScriptedInputKind::Quit:
        return true;
    }
    return false;
}

[[nodiscard]] bool valid_plan(const ScriptedInputPlan& plan, std::string& error) {
    if (plan.duration_ms < kScriptedInputMinimumDurationMs ||
        plan.duration_ms > kScriptedInputMaximumDurationMs ||
        plan.event_count > plan.events.size()) {
        error = "Input replay plan has an invalid duration or event count";
        return false;
    }
    for (std::size_t index = 0; index < plan.event_count; ++index) {
        const auto& event = plan.events[index];
        if (event.at_ms >= plan.duration_ms ||
            (index != 0 && event.at_ms < plan.events[index - 1].at_ms) || !valid_event(event)) {
            error = "Input replay plan has an invalid event at index " + std::to_string(index);
            return false;
        }
    }
    return true;
}

// Open the leaf itself, then inspect that same handle. A path-status/open race
// must not redirect the bounded loader through a symlink or into a FIFO/device.
[[nodiscard]] bool read_source(const std::filesystem::path& path,
                               std::array<char, kScriptedInputMaxBytes + 1>& bytes,
                               std::size_t& size, std::string& error) {
    if (path.empty() || path.native().find(typename std::filesystem::path::value_type{}) !=
                            std::filesystem::path::string_type::npos) {
        error = "Input replay path is empty or contains NUL";
        return false;
    }
#if defined(_WIN32)
    struct File {
        HANDLE value;
        ~File() { CloseHandle(value); }
    };
    const auto handle = CreateFileW(path.c_str(), GENERIC_READ, FILE_SHARE_READ, nullptr,
        OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL | FILE_FLAG_OPEN_REPARSE_POINT, nullptr);
    if (handle == INVALID_HANDLE_VALUE) {
        error = "Cannot open input replay file (Windows error " + std::to_string(GetLastError()) + ")";
        return false;
    }
    const File file{handle};
    BY_HANDLE_FILE_INFORMATION info{};
    if (GetFileType(file.value) != FILE_TYPE_DISK || !GetFileInformationByHandle(file.value, &info) ||
        (info.dwFileAttributes & (FILE_ATTRIBUTE_DIRECTORY | FILE_ATTRIBUTE_REPARSE_POINT)) != 0) {
        error = "Input replay must be a regular file with a nonsymlink leaf";
        return false;
    }
    if (info.nFileSizeHigh != 0 || info.nFileSizeLow > kScriptedInputMaxBytes) {
        error = "Input replay exceeds 65536 bytes";
        return false;
    }
    const auto expected_size = static_cast<std::size_t>(info.nFileSizeLow);
    size = 0;
    while (size < bytes.size()) {
        DWORD obtained = 0;
        if (!ReadFile(file.value, bytes.data() + size,
                      static_cast<DWORD>(bytes.size() - size), &obtained, nullptr)) {
            error = "Cannot read complete input replay file";
            return false;
        }
        if (obtained == 0) break;
        size += static_cast<std::size_t>(obtained);
    }
#else
    struct File {
        int value;
        ~File() { close(value); }
    };
    const int descriptor = open(path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW | O_NONBLOCK);
    if (descriptor < 0) {
        error = "Cannot open nonsymlink input replay file: " +
            std::error_code(errno, std::generic_category()).message();
        return false;
    }
    const File file{descriptor};
    struct stat info{};
    if (fstat(file.value, &info) != 0 || !S_ISREG(info.st_mode)) {
        error = "Input replay must be a regular file with a nonsymlink leaf";
        return false;
    }
    if (info.st_size < 0 || static_cast<std::uintmax_t>(info.st_size) > kScriptedInputMaxBytes) {
        error = "Input replay exceeds 65536 bytes";
        return false;
    }
    const auto expected_size = static_cast<std::size_t>(info.st_size);
    size = 0;
    while (size < bytes.size()) {
        const auto obtained = read(file.value, bytes.data() + size, bytes.size() - size);
        if (obtained < 0) {
            if (errno == EINTR) continue;
            error = "Cannot read complete input replay file";
            return false;
        }
        if (obtained == 0) break;
        size += static_cast<std::size_t>(obtained);
    }
#endif
    if (size > kScriptedInputMaxBytes || size != expected_size) {
        error = "Input replay changed size while reading or exceeds 65536 bytes";
        return false;
    }
    return true;
}

} // namespace

bool parse_scripted_input(std::string_view source, ScriptedInputPlan& destination,
                          std::string& error) {
    if (source.empty() || source.size() > kScriptedInputMaxBytes) {
        error = "Input replay must contain 1..65536 bytes";
        return false;
    }
    for (std::size_t index = 0; index < source.size(); ++index) {
        const auto byte = static_cast<unsigned char>(source[index]);
        if ((byte < 0x20U && byte != '\t' && byte != '\n' && byte != '\r') || byte > 0x7EU ||
            (byte == '\r' && (index + 1 == source.size() || source[index + 1] != '\n'))) {
            error = "Input replay requires printable ASCII, tabs, and LF or CRLF line endings";
            return false;
        }
    }
    ScriptedInputPlan candidate;
    std::string_view line;
    if (!next_line(source, line) || line != kScriptedInputFormat) {
        return line_error(1, "expected B3UIREPLAY1", error);
    }
    Tokens duration;
    if (!next_line(source, line) || !split(line, duration) || duration.count != 2 ||
        duration.items[0] != "duration_ms" || !integer(duration.items[1], candidate.duration_ms) ||
        candidate.duration_ms < kScriptedInputMinimumDurationMs ||
        candidate.duration_ms > kScriptedInputMaximumDurationMs) {
        return line_error(2, "expected duration_ms N with N in 250..10000", error);
    }
    std::size_t line_number = 2;
    while (next_line(source, line)) {
        ++line_number;
        const auto first = line.find_first_not_of(" \t");
        if (first == std::string_view::npos || line[first] == '#') continue;
        Tokens fields;
        if (!split(line, fields) || fields.count < 2) {
            return line_error(line_number, "invalid or trailing record fields", error);
        }
        if (candidate.event_count == candidate.events.size()) {
            return line_error(line_number, "more than 256 events", error);
        }
        ScriptedInputEvent event;
        if (!integer(fields.items[0], event.at_ms) || event.at_ms >= candidate.duration_ms ||
            (candidate.event_count != 0 && event.at_ms < candidate.events[candidate.event_count - 1].at_ms)) {
            return line_error(line_number, "event times must be nondecreasing and less than duration_ms", error);
        }
        const auto action = fields.items[1];
        if (action == "key_down" || action == "key_up") {
            const bool down = action == "key_down";
            if (fields.count != (down ? 5U : 4U)) {
                return line_error(line_number, "expected key_down KEY MODIFIERS REPEAT or key_up KEY MODIFIERS", error);
            }
            const auto* key = find_key(fields.items[2]);
            if (key == nullptr || !modifiers(fields.items[3], event.modifiers) ||
                (down && fields.items[4] != "0" && fields.items[4] != "1")) {
                return line_error(line_number, "unsupported key, modifiers, or repeat (0 or 1)", error);
            }
            event.kind = down ? ScriptedInputKind::KeyDown : ScriptedInputKind::KeyUp;
            event.scancode = key->scancode;
            event.repeat = down && fields.items[4] == "1";
        } else if (action == "mouse_down" || action == "mouse_move" || action == "mouse_up") {
            event.kind = action == "mouse_down" ? ScriptedInputKind::MouseDown :
                action == "mouse_move" ? ScriptedInputKind::MouseMove : ScriptedInputKind::MouseUp;
            if (fields.count != 4 || !integer(fields.items[2], event.x) || !integer(fields.items[3], event.y) ||
                !valid_event(event)) {
                return line_error(line_number, "expected mouse action X Y with integer coordinates in -8192..16384", error);
            }
        } else if (action == "resize") {
            event.kind = ScriptedInputKind::Resize;
            if (fields.count != 4 || !integer(fields.items[2], event.width) ||
                !integer(fields.items[3], event.height) || !valid_event(event)) {
                return line_error(line_number, "expected resize W H with W in 960..8192 and H in 700..8192", error);
            }
        } else if (action == "focus_lost" || action == "quit") {
            if (fields.count != 2) return line_error(line_number, "trailing action fields", error);
            event.kind = action == "focus_lost" ? ScriptedInputKind::FocusLost : ScriptedInputKind::Quit;
        } else {
            return line_error(line_number, "unknown action", error);
        }
        candidate.events[candidate.event_count++] = event;
    }
    destination = candidate;
    error.clear();
    return true;
}

bool load_scripted_input(const std::filesystem::path& path, ScriptedInputPlan& destination,
                         std::string& error) {
    std::array<char, kScriptedInputMaxBytes + 1> bytes{};
    std::size_t size = 0;
    if (!read_source(path, bytes, size, error)) return false;
    return parse_scripted_input({bytes.data(), size}, destination, error);
}

bool ScriptedInput::initialize(const ScriptedInputPlan& plan, SDL_Window* window,
                               std::string& error) {
    if (initialized_) { error = "Input replay is already initialized"; return false; }
    if (!valid_plan(plan, error)) return false;
    if (window == nullptr || (SDL_WasInit(SDL_INIT_VIDEO) & SDL_INIT_VIDEO) == 0) {
        error = "Input replay requires an initialized SDL video window";
        return false;
    }
    const Uint32 window_id = SDL_GetWindowID(window);
    if (window_id == 0 || SDL_GetWindowFromID(window_id) != window) {
        error = "Input replay requires a live SDL window";
        return false;
    }
    const Uint32 marker_type = SDL_RegisterEvents(1);
    if (marker_type == std::numeric_limits<Uint32>::max()) {
        error = "Cannot register input replay completion event";
        return false;
    }
    plan_ = plan;
    window_ = window;
    window_id_ = window_id;
    marker_type_ = marker_type;
    initialized_ = true;
    delivered_ = plan_.event_count == 0;
    error.clear();
    return true;
}

bool ScriptedInput::fail(std::string message, std::string& error) {
    failed_ = true;
    failure_ = std::move(message);
    error = failure_;
    return false;
}

bool ScriptedInput::push(SDL_Event& event, std::string& error) {
    SDL_ClearError();
    const int result = SDL_PushEvent(&event);
    if (result == 1) return true;
    return fail("Input replay SDL queue refused event after " + std::to_string(pushed_count_) +
        " of " + std::to_string(plan_.event_count) + " actions (" +
        (result == 0 ? std::string("filtered") : std::string(SDL_GetError())) + ")", error);
}

bool ScriptedInput::push_marker(std::string& error) {
    SDL_Event marker{};
    marker.type = marker_type_;
    marker.user.windowID = window_id_;
    marker.user.code = static_cast<Sint32>(pushed_count_);
    marker.user.data1 = this;
    if (!push(marker, error)) return false;
    marker_pushed_ = true;
    return true;
}

bool ScriptedInput::pump(std::uint64_t elapsed_ms, std::string& error) {
    if (!initialized_) { error = "Input replay is not initialized"; return false; }
    if (failed_) { error = failure_; return false; }
    if (elapsed_ms < last_elapsed_ms_) return fail("Input replay elapsed time moved backwards", error);
    last_elapsed_ms_ = elapsed_ms;
    error.clear();
    if (delivered_ || marker_pushed_) return true;
    if (SDL_GetWindowFromID(window_id_) != window_) return fail("Input replay window no longer exists", error);
    while (pushed_count_ < plan_.event_count && plan_.events[pushed_count_].at_ms <= elapsed_ms) {
        const auto& input = plan_.events[pushed_count_];
        // A resize changes the native window synchronously. Drain preceding
        // input first, and drain this actual size before any subsequent input.
        if (input.kind == ScriptedInputKind::Resize && acknowledged_count_ != pushed_count_) {
            return push_marker(error);
        }
        SDL_Event event{};
        switch (input.kind) {
        case ScriptedInputKind::KeyDown:
        case ScriptedInputKind::KeyUp:
            event.type = input.kind == ScriptedInputKind::KeyDown ? SDL_KEYDOWN : SDL_KEYUP;
            event.key.windowID = window_id_;
            event.key.state = event.type == SDL_KEYDOWN ? SDL_PRESSED : SDL_RELEASED;
            event.key.repeat = input.repeat ? 1U : 0U;
            event.key.keysym.scancode = input.scancode;
            event.key.keysym.sym = find_key(input.scancode)->keycode;
            event.key.keysym.mod = static_cast<Uint16>(input.modifiers);
            break;
        case ScriptedInputKind::MouseDown:
        case ScriptedInputKind::MouseUp:
            event.type = input.kind == ScriptedInputKind::MouseDown ? SDL_MOUSEBUTTONDOWN : SDL_MOUSEBUTTONUP;
            event.button.windowID = window_id_;
            event.button.button = SDL_BUTTON_LEFT;
            event.button.state = event.type == SDL_MOUSEBUTTONDOWN ? SDL_PRESSED : SDL_RELEASED;
            event.button.clicks = 1;
            event.button.x = input.x;
            event.button.y = input.y;
            break;
        case ScriptedInputKind::MouseMove:
            event.type = SDL_MOUSEMOTION;
            event.motion.windowID = window_id_;
            event.motion.state = pointer_down_ ? SDL_BUTTON_LMASK : 0U;
            event.motion.x = input.x;
            event.motion.y = input.y;
            event.motion.xrel = pointer_position_known_ ? input.x - pointer_x_ : 0;
            event.motion.yrel = pointer_position_known_ ? input.y - pointer_y_ : 0;
            break;
        case ScriptedInputKind::Resize: {
            SDL_SetWindowSize(window_, input.width, input.height);
            int width = 0, height = 0;
            SDL_GetWindowSize(window_, &width, &height);
            if (width < kMinimumWidth || width > kMaximumDimension ||
                height < kMinimumHeight || height > kMaximumDimension) {
                return fail("Input replay resize produced an unsupported actual window size", error);
            }
            event.type = SDL_WINDOWEVENT;
            event.window.windowID = window_id_;
            event.window.event = SDL_WINDOWEVENT_SIZE_CHANGED;
            event.window.data1 = width;
            event.window.data2 = height;
            break;
        }
        case ScriptedInputKind::FocusLost:
            event.type = SDL_WINDOWEVENT;
            event.window.windowID = window_id_;
            event.window.event = SDL_WINDOWEVENT_FOCUS_LOST;
            break;
        case ScriptedInputKind::Quit:
            event.type = SDL_QUIT;
            break;
        }
        if (!push(event, error)) return false;
        ++pushed_count_;
        if (input.kind == ScriptedInputKind::MouseDown || input.kind == ScriptedInputKind::MouseUp ||
            input.kind == ScriptedInputKind::MouseMove) {
            pointer_x_ = input.x;
            pointer_y_ = input.y;
            pointer_position_known_ = true;
            if (input.kind != ScriptedInputKind::MouseMove) pointer_down_ = input.kind == ScriptedInputKind::MouseDown;
        } else if (input.kind == ScriptedInputKind::FocusLost) {
            pointer_down_ = false;
        }
        if (input.kind == ScriptedInputKind::Resize) return push_marker(error);
    }
    if (pushed_count_ == plan_.event_count) return push_marker(error);
    return true;
}

bool ScriptedInput::acknowledge(const SDL_Event& event) noexcept {
    if (!initialized_ || failed_ || !marker_pushed_ || event.type != marker_type_ ||
        event.user.windowID != window_id_ || event.user.data1 != this || event.user.data2 != nullptr ||
        event.user.code != static_cast<Sint32>(pushed_count_)) return false;
    acknowledged_count_ = pushed_count_;
    marker_pushed_ = false;
    delivered_ = pushed_count_ == plan_.event_count;
    return true;
}

} // namespace hammond::standalone
