#include "ScriptedInput.h"

#include <SDL.h>

#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <memory>
#include <string>
#include <string_view>
#include <type_traits>
#include <utility>
#include <vector>

#if defined(__unix__) || defined(__APPLE__)
#include <sys/stat.h>
#endif

namespace {

using namespace hammond::standalone;
namespace fs = std::filesystem;

static_assert(!std::is_copy_constructible_v<ScriptedInput>);
static_assert(!std::is_move_constructible_v<ScriptedInput>);

struct Totals {
    std::size_t parsed{}, parse_rejections{}, loaded{}, load_rejections{};
    std::size_t plan_rejections{}, queued{}, markers{}, expected_failures{}, lifetimes{};
} totals;

[[noreturn]] void fail(std::string_view expression, int line, std::string_view detail = {}) {
    std::cerr << __FILE__ << ':' << line << ": CHECK failed: " << expression;
    if (!detail.empty()) std::cerr << " (" << detail << ')';
    std::cerr << '\n';
    std::exit(EXIT_FAILURE);
}

void check(bool condition, std::string_view expression, int line,
           std::string_view detail = {}) {
    if (!condition) fail(expression, line, detail);
}

#define CHECK(expression) check(static_cast<bool>(expression), #expression, __LINE__)
#define CHECK_DETAIL(expression, detail) \
    check(static_cast<bool>(expression), #expression, __LINE__, (detail))

[[nodiscard]] bool same_event(const ScriptedInputEvent& left, const ScriptedInputEvent& right) {
    return left.at_ms == right.at_ms && left.kind == right.kind &&
        left.scancode == right.scancode && left.modifiers == right.modifiers &&
        left.repeat == right.repeat && left.x == right.x && left.y == right.y &&
        left.width == right.width && left.height == right.height;
}

void same_plan(const ScriptedInputPlan& left, const ScriptedInputPlan& right) {
    CHECK(left.event_count == right.event_count);
    CHECK(left.duration_ms == right.duration_ms);
    for (std::size_t index = 0; index < left.events.size(); ++index) {
        CHECK(same_event(left.events[index], right.events[index]));
    }
}

[[nodiscard]] ScriptedInputPlan sentinel() {
    ScriptedInputPlan plan;
    plan.event_count = 3;
    plan.duration_ms = 5432;
    for (std::size_t index = 0; index < plan.events.size(); ++index) {
        auto& event = plan.events[index];
        event.at_ms = static_cast<std::uint32_t>(index + 19);
        event.kind = ScriptedInputKind::KeyDown;
        event.scancode = SDL_SCANCODE_P;
        event.modifiers = KMOD_LALT;
        event.repeat = true;
        event.x = -37;
        event.y = 83;
        event.width = 1234;
        event.height = 789;
    }
    return plan;
}

[[nodiscard]] std::string script(std::string_view body, unsigned duration = 250) {
    return "B3UIREPLAY1\nduration_ms " + std::to_string(duration) + '\n' + std::string{body};
}

[[nodiscard]] ScriptedInputPlan parsed(std::string_view source) {
    auto plan = sentinel();
    std::string error = "clear this on success";
    CHECK_DETAIL(parse_scripted_input(source, plan, error), error);
    CHECK(error.empty());
    ++totals.parsed;
    return plan;
}

void rejected(std::string_view source) {
    auto plan = sentinel();
    const auto before = plan;
    std::string error;
    CHECK_DETAIL(!parse_scripted_input(source, plan, error), source.substr(0, 100));
    CHECK(!error.empty());
    same_plan(plan, before); // Includes inactive records, without comparing padding.
    ++totals.parse_rejections;
}

struct KeyCase {
    std::string_view name;
    SDL_Scancode scan;
    SDL_Keycode symbol;
};

// Independent, literal public whitelist. Do not derive this from the parser or
// SDL_GetScancodeFromName: several SDL names/aliases are deliberately forbidden.
constexpr std::array kKeys{
    KeyCase{"A", SDL_SCANCODE_A, SDLK_a}, KeyCase{"W", SDL_SCANCODE_W, SDLK_w},
    KeyCase{"S", SDL_SCANCODE_S, SDLK_s}, KeyCase{"E", SDL_SCANCODE_E, SDLK_e},
    KeyCase{"D", SDL_SCANCODE_D, SDLK_d}, KeyCase{"F", SDL_SCANCODE_F, SDLK_f},
    KeyCase{"T", SDL_SCANCODE_T, SDLK_t}, KeyCase{"G", SDL_SCANCODE_G, SDLK_g},
    KeyCase{"Y", SDL_SCANCODE_Y, SDLK_y}, KeyCase{"H", SDL_SCANCODE_H, SDLK_h},
    KeyCase{"U", SDL_SCANCODE_U, SDLK_u}, KeyCase{"J", SDL_SCANCODE_J, SDLK_j},
    KeyCase{"K", SDL_SCANCODE_K, SDLK_k}, KeyCase{"O", SDL_SCANCODE_O, SDLK_o},
    KeyCase{"L", SDL_SCANCODE_L, SDLK_l}, KeyCase{"P", SDL_SCANCODE_P, SDLK_p},
    KeyCase{"M", SDL_SCANCODE_M, SDLK_m},
    KeyCase{"Semicolon", SDL_SCANCODE_SEMICOLON, SDLK_SEMICOLON},
    KeyCase{"Tab", SDL_SCANCODE_TAB, SDLK_TAB},
    KeyCase{"Left", SDL_SCANCODE_LEFT, SDLK_LEFT},
    KeyCase{"Right", SDL_SCANCODE_RIGHT, SDLK_RIGHT},
    KeyCase{"Up", SDL_SCANCODE_UP, SDLK_UP},
    KeyCase{"Down", SDL_SCANCODE_DOWN, SDLK_DOWN},
    KeyCase{"Home", SDL_SCANCODE_HOME, SDLK_HOME},
    KeyCase{"End", SDL_SCANCODE_END, SDLK_END},
    KeyCase{"Space", SDL_SCANCODE_SPACE, SDLK_SPACE},
    KeyCase{"Return", SDL_SCANCODE_RETURN, SDLK_RETURN},
    KeyCase{"Escape", SDL_SCANCODE_ESCAPE, SDLK_ESCAPE},
    KeyCase{"LeftBracket", SDL_SCANCODE_LEFTBRACKET, SDLK_LEFTBRACKET},
    KeyCase{"RightBracket", SDL_SCANCODE_RIGHTBRACKET, SDLK_RIGHTBRACKET},
    KeyCase{"F1", SDL_SCANCODE_F1, SDLK_F1},
    KeyCase{"F2", SDL_SCANCODE_F2, SDLK_F2},
    KeyCase{"F3", SDL_SCANCODE_F3, SDLK_F3},
    KeyCase{"Comma", SDL_SCANCODE_COMMA, SDLK_COMMA},
    KeyCase{"Slash", SDL_SCANCODE_SLASH, SDLK_SLASH},
};

struct ModifierCase { std::string_view text; SDL_Keymod value; };

constexpr SDL_Keymod mods(unsigned bits) { return static_cast<SDL_Keymod>(bits); }

constexpr std::array kModifiers{
    ModifierCase{"none", KMOD_NONE}, ModifierCase{"shift", KMOD_LSHIFT},
    ModifierCase{"ctrl", KMOD_LCTRL}, ModifierCase{"shift+ctrl", mods(KMOD_LSHIFT | KMOD_LCTRL)},
    ModifierCase{"alt", KMOD_LALT}, ModifierCase{"alt+shift", mods(KMOD_LALT | KMOD_LSHIFT)},
    ModifierCase{"ctrl+alt", mods(KMOD_LCTRL | KMOD_LALT)},
    ModifierCase{"alt+ctrl+shift", mods(KMOD_LALT | KMOD_LCTRL | KMOD_LSHIFT)},
    ModifierCase{"meta", KMOD_LGUI}, ModifierCase{"shift+meta", mods(KMOD_LSHIFT | KMOD_LGUI)},
    ModifierCase{"meta+ctrl", mods(KMOD_LGUI | KMOD_LCTRL)},
    ModifierCase{"ctrl+meta+shift", mods(KMOD_LCTRL | KMOD_LGUI | KMOD_LSHIFT)},
    ModifierCase{"alt+meta", mods(KMOD_LALT | KMOD_LGUI)},
    ModifierCase{"meta+shift+alt", mods(KMOD_LGUI | KMOD_LSHIFT | KMOD_LALT)},
    ModifierCase{"meta+alt+ctrl", mods(KMOD_LGUI | KMOD_LALT | KMOD_LCTRL)},
    ModifierCase{"meta+ctrl+alt+shift", mods(KMOD_LGUI | KMOD_LCTRL | KMOD_LALT | KMOD_LSHIFT)},
};

void test_parser_boundaries() {
    CHECK(kScriptedInputFormat == "B3UIREPLAY1");
    CHECK(kScriptedInputMaxEvents == 256);
    CHECK(kScriptedInputMaxBytes == 65536);
    CHECK(kScriptedInputMinimumDurationMs == 250);
    CHECK(kScriptedInputMaximumDurationMs == 10000);
    CHECK(parsed("B3UIREPLAY1\nduration_ms 250").event_count == 0);
    CHECK(parsed("B3UIREPLAY1\r\n\tduration_ms\t10000 \t\r\n\t# comment\r\n \t\r\n").duration_ms == 10000);
    const auto zeroes = parsed("B3UIREPLAY1\nduration_ms 00250\n000 mouse_move -000 00012\n");
    CHECK(zeroes.events[0].at_ms == 0 && zeroes.events[0].x == 0 && zeroes.events[0].y == 12);
    const auto ties = parsed(script(
        "# comment\n\n 0 key_down A none 0\n0 key_up A none\n\t0 focus_lost\n249 quit\n"));
    CHECK(ties.event_count == 4);
    CHECK(ties.events[0].kind == ScriptedInputKind::KeyDown);
    CHECK(ties.events[1].kind == ScriptedInputKind::KeyUp);
    CHECK(ties.events[2].kind == ScriptedInputKind::FocusLost);
    CHECK(ties.events[3].kind == ScriptedInputKind::Quit);
    CHECK(ties.events[3].at_ms == 249);
    CHECK(parsed(script("9999 quit", 10000)).events[0].at_ms == 9999);

    const std::array malformed_headers{
        "", "\n", "B3UIREPLAY1", "B3UIREPLAY1\n", "b3uireplay1\nduration_ms 250\n",
        "B3UIREPLAY2\nduration_ms 250\n", " B3UIREPLAY1\nduration_ms 250\n",
        "B3UIREPLAY1 \nduration_ms 250\n", "# before\nB3UIREPLAY1\nduration_ms 250\n",
        "\nB3UIREPLAY1\nduration_ms 250\n", "B3UIREPLAY1\n\nduration_ms 250\n",
        "B3UIREPLAY1\n# before duration\nduration_ms 250\n",
        "B3UIREPLAY1\rduration_ms 250\n", "B3UIREPLAY1\nduration_ms 250\r",
        "B3UIREPLAY1\nduration 250\n", "B3UIREPLAY1\nDuration_ms 250\n",
        "B3UIREPLAY1\nduration_ms\n", "B3UIREPLAY1\nduration_ms 250 extra\n",
        "B3UIREPLAY1\nduration_ms 250 # inline\n",
    };
    for (const auto* source : malformed_headers) rejected(source);
    for (const auto* value : {"0", "249", "10001", "-250", "+250", "250.0", "2.5e2",
                              "nan", "inf", "250x", "4294967296", "999999999999999999999"}) {
        rejected(std::string{"B3UIREPLAY1\nduration_ms "} + value + '\n');
    }
    rejected(std::string{"\xEF\xBB\xBF"} + script(""));
    rejected(script("# caf\xC3\xA9\n"));
    rejected(script(std::string{"0 quit\0\n", 8}));
    rejected(script("0 quit\v\n"));
    rejected(script("0 quit\f\n"));
    rejected(script("# DEL\x7F\n"));
    rejected(script("0 quit\r1 quit\n"));
    rejected(script("duration_ms 250\n"));
    rejected(script("0 quit extra\n"));
    rejected(script("0 quit # inline\n"));
    rejected(script("0 Quit\n"));
    rejected(script("0 unknown\n"));
    rejected(script("0\n"));
    rejected(script("0 focus_lost extra\n"));
    rejected(script("10 quit\n9 focus_lost\n"));
    for (const auto* timestamp : {"-1", "+1", "1.0", "1e2", "nan", "inf", "1x", "250",
                                  "251", "4294967296", "999999999999999999999999"}) {
        rejected(script(std::string{timestamp} + " quit\n"));
    }

    std::string maximum = script("");
    for (unsigned index = 0; index < 256; ++index) maximum += "0 focus_lost\n";
    CHECK(parsed(maximum).event_count == 256);
    rejected(maximum + "0 focus_lost\n");
    std::string bytes = script("#");
    bytes.append(65536 - bytes.size(), 'x');
    CHECK(bytes.size() == 65536);
    CHECK(parsed(bytes).event_count == 0);
    rejected(bytes + 'x');
}

void test_parser_payloads() {
    for (const auto& key : kKeys) {
        for (const auto& modifier : kModifiers) {
            const auto text = "0 key_down " + std::string{key.name} + ' ' +
                std::string{modifier.text} + " 1\n0 key_up " + std::string{key.name} + ' ' +
                std::string{modifier.text} + '\n';
            const auto plan = parsed(script(text));
            CHECK(plan.event_count == 2);
            CHECK(plan.events[0].kind == ScriptedInputKind::KeyDown);
            CHECK(plan.events[1].kind == ScriptedInputKind::KeyUp);
            CHECK(plan.events[0].scancode == key.scan && plan.events[1].scancode == key.scan);
            CHECK(plan.events[0].modifiers == modifier.value);
            CHECK(plan.events[1].modifiers == modifier.value);
            CHECK(plan.events[0].repeat && !plan.events[1].repeat);
        }
    }
    for (const auto* name : {"a", "m", "Q", "Z", "Enter", "KP_ENTER", "SDL_SCANCODE_A",
                            "SDL_SCANCODE_M", ";", "F4"}) {
        rejected(script(std::string{"0 key_down "} + name + " none 0\n"));
    }
    for (const auto* modifier : {"None", "Shift", "0", "super", "none+shift", "shift+none",
                                 "shift+shift", "ctrl+alt+ctrl", "+shift", "shift+", "shift++alt"}) {
        rejected(script(std::string{"0 key_down A "} + modifier + " 0\n"));
        rejected(script(std::string{"0 key_up A "} + modifier + '\n'));
    }
    for (const auto* repeat : {"2", "-1", "+1", "00", "01", "true", "1.0", "nan", "1x"}) {
        rejected(script(std::string{"0 key_down A none "} + repeat + '\n'));
    }
    for (const auto* record : {"0 key_down A none", "0 key_down A", "0 key_down",
                               "0 key_down A none 0 extra", "0 key_up A", "0 key_up",
                               "0 key_up A none 0", "0 key_up A none extra"}) {
        rejected(script(std::string{record} + '\n'));
    }
    for (const auto* action : {"mouse_down", "mouse_move", "mouse_up"}) {
        const auto minimum = parsed(script(std::string{"0 "} + action + " -8192 16384\n"));
        CHECK(minimum.events[0].x == -8192 && minimum.events[0].y == 16384);
        const auto maximum = parsed(script(std::string{"0 "} + action + " 16384 -8192\n"));
        CHECK(maximum.events[0].x == 16384 && maximum.events[0].y == -8192);
        for (const auto* bad : {"-8193", "16385", "+1", "1.5", "nan", "inf", "12x",
                               "2147483648", "-2147483649", "999999999999999999999999"}) {
            rejected(script(std::string{"0 "} + action + ' ' + bad + " 0\n"));
            rejected(script(std::string{"0 "} + action + " 0 " + bad + '\n'));
        }
        rejected(script(std::string{"0 "} + action + " 0\n"));
        rejected(script(std::string{"0 "} + action + " 0 0 extra\n"));
    }
    const auto sizes = parsed(script("0 resize 960 700\n0 resize 8192 8192\n"));
    CHECK(sizes.events[0].width == 960 && sizes.events[0].height == 700);
    CHECK(sizes.events[1].width == 8192 && sizes.events[1].height == 8192);
    for (const auto* bad : {"959 700", "960 699", "8193 700", "960 8193", "-960 700",
                           "+960 700", "960.0 700", "960 nan", "960 inf", "960 700x",
                           "4294967296 700", "960 4294967296", "960", "960 700 extra"}) {
        rejected(script(std::string{"0 resize "} + bad + '\n'));
    }
}

class TemporaryDirectory {
public:
    TemporaryDirectory() {
        const auto root = fs::temp_directory_path();
        const auto tick = std::chrono::steady_clock::now().time_since_epoch().count();
        for (unsigned attempt = 0; attempt < 100; ++attempt) {
            path_ = root / ("hammond-replay-" + std::to_string(tick) + '-' + std::to_string(attempt));
            std::error_code error;
            if (fs::create_directory(path_, error)) return;
        }
        fail("create isolated temporary directory", __LINE__);
    }
    ~TemporaryDirectory() { std::error_code error; fs::remove_all(path_, error); }
    [[nodiscard]] const fs::path& path() const { return path_; }
private:
    fs::path path_;
};

void write(const fs::path& path, std::string_view contents) {
    std::ofstream output{path, std::ios::binary};
    CHECK(output.is_open());
    output.write(contents.data(), static_cast<std::streamsize>(contents.size()));
    output.close();
    CHECK(output.good());
}

void load_rejected(const fs::path& path) {
    auto destination = sentinel();
    const auto before = destination;
    std::string error;
    CHECK(!load_scripted_input(path, destination, error));
    CHECK(!error.empty());
    same_plan(destination, before);
    ++totals.load_rejections;
}

void test_files() {
    const TemporaryDirectory temporary;
    const auto unicode_directory = temporary.path() / fs::path{u8"replay space é 音"};
    CHECK(fs::create_directory(unicode_directory));
    const auto regular = unicode_directory / fs::path{u8"entrée file.b3replay"};
    const auto text = script("0 key_down A shift+ctrl 0\n249 key_up A none\n");
    write(regular, text);
    const auto expected = parsed(text);
    auto destination = sentinel();
    std::string error = "clear this";
    CHECK_DETAIL(load_scripted_input(regular, destination, error), error);
    CHECK(error.empty());
    same_plan(destination, expected);
    ++totals.loaded;
    load_rejected(fs::path{});
    auto embedded_nul = regular.native();
    embedded_nul.push_back(fs::path::value_type{});
    embedded_nul += fs::path{".suffix"}.native();
    load_rejected(fs::path{embedded_nul});
    load_rejected(temporary.path() / "missing.b3replay");
    load_rejected(temporary.path());
    const auto malformed = temporary.path() / "malformed.b3replay";
    write(malformed, script("0 key_down A none 0\n250 key_up A none\n"));
    load_rejected(malformed);
    const auto empty = temporary.path() / "empty.b3replay";
    write(empty, "");
    load_rejected(empty);
    const auto maximum = temporary.path() / "maximum.b3replay";
    std::string maximum_text = script("#");
    maximum_text.append(65536 - maximum_text.size(), 'x');
    write(maximum, maximum_text);
    CHECK_DETAIL(load_scripted_input(maximum, destination, error), error);
    CHECK(error.empty() && destination.event_count == 0 && destination.duration_ms == 250);
    ++totals.loaded;
    write(maximum, maximum_text + 'x');
    load_rejected(maximum);
    // A sparse large regular file makes the declared size bound observable
    // without allocating, writing, or retaining its whole contents in this test.
    const auto sparse = temporary.path() / "oversized-sparse.b3replay";
    write(sparse, script(""));
    fs::resize_file(sparse, 64U * 1024U * 1024U);
    load_rejected(sparse);

    const auto link = temporary.path() / "final-link.b3replay";
    std::error_code symlink_error;
    fs::create_symlink(regular, link, symlink_error);
    if (!symlink_error) {
        load_rejected(link);
        const auto dangling = temporary.path() / "dangling-link.b3replay";
        fs::create_symlink(temporary.path() / "absent", dangling);
        load_rejected(dangling);
        const auto parent_link = temporary.path() / "permitted-parent-link";
        fs::create_directory_symlink(unicode_directory, parent_link);
        load_rejected(parent_link); // A symlink directory is not a regular leaf.
        CHECK_DETAIL(load_scripted_input(parent_link / regular.filename(), destination, error), error);
        CHECK(error.empty());
        same_plan(destination, expected); // Parent links are explicitly permitted.
        ++totals.loaded;
    } else {
#if defined(__unix__) || defined(__APPLE__)
        CHECK_DETAIL(false, symlink_error.message());
#else
        std::cout << "symlink admission not run: " << symlink_error.message() << '\n';
#endif
    }
#if defined(__unix__) || defined(__APPLE__)
    const auto fifo = temporary.path() / "not-a-regular-file";
    CHECK(::mkfifo(fifo.c_str(), 0600) == 0);
    load_rejected(fifo); // No writer: opening before type validation would block.
#endif
}

struct WindowDeleter { void operator()(SDL_Window* value) const { SDL_DestroyWindow(value); } };
using Window = std::unique_ptr<SDL_Window, WindowDeleter>;

[[nodiscard]] Window make_window() {
    Window window{SDL_CreateWindow("replay acceptance", SDL_WINDOWPOS_UNDEFINED,
        SDL_WINDOWPOS_UNDEFINED, 960, 700, SDL_WINDOW_HIDDEN | SDL_WINDOW_RESIZABLE)};
    CHECK_DETAIL(window != nullptr, SDL_GetError());
    CHECK(SDL_GetWindowID(window.get()) != 0);
    return window;
}

void flush_events() { SDL_PumpEvents(); SDL_FlushEvents(SDL_FIRSTEVENT, SDL_LASTEVENT); }

[[nodiscard]] std::vector<SDL_Event> poll_events() {
    std::vector<SDL_Event> events;
    SDL_Event event{};
    while (SDL_PollEvent(&event) != 0) {
        CHECK(events.size() < 70000);
        events.push_back(event);
    }
    return events;
}

[[nodiscard]] bool is_input(const SDL_Event& event) {
    return event.type == SDL_KEYDOWN || event.type == SDL_KEYUP ||
        event.type == SDL_MOUSEBUTTONDOWN || event.type == SDL_MOUSEBUTTONUP ||
        event.type == SDL_MOUSEMOTION || event.type == SDL_QUIT;
}

void initialized(ScriptedInput& input, const ScriptedInputPlan& plan, SDL_Window* window) {
    std::string error = "clear this";
    CHECK_DETAIL(input.initialize(plan, window, error), error);
    CHECK(error.empty());
    CHECK(input.scheduled_count() == plan.event_count);
    CHECK(input.pushed_count() == 0);
    CHECK(input.duration_ms() == plan.duration_ms);
    CHECK(!input.failed());
}

void pump(ScriptedInput& input, std::uint64_t elapsed) {
    std::string error = "clear this";
    CHECK_DETAIL(input.pump(elapsed, error), error);
    CHECK(error.empty());
}

void test_empty_and_admission(SDL_Window* window) {
    const auto empty = parsed(script(""));
    ScriptedInput unused;
    CHECK(!unused.completed(std::numeric_limits<std::uint64_t>::max()));
    CHECK(!unused.delivered() && !unused.failed());
    SDL_Event unrelated{};
    unrelated.type = SDL_QUIT;
    CHECK(!unused.acknowledge(unrelated));
    std::string error;
    CHECK(!unused.initialize(empty, nullptr, error));
    CHECK(!error.empty());
    CHECK(unused.scheduled_count() == 0 && unused.duration_ms() == 0);
    initialized(unused, empty, window); // A rejected initialization is retryable.
    CHECK(unused.delivered());
    CHECK(!unused.completed(249));
    CHECK(unused.completed(250));
    pump(unused, 0);
    pump(unused, 250);
    CHECK(poll_events().empty());

    const auto valid = parsed(script("10 key_down A none 0\n10 key_up A none\n"));
    const auto refuse_plan = [&](ScriptedInputPlan plan) {
        ScriptedInput input;
        std::string detail;
        CHECK(!input.initialize(plan, window, detail));
        CHECK(!detail.empty());
        CHECK(input.scheduled_count() == 0 && input.duration_ms() == 0);
        CHECK(input.pushed_count() == 0 && !input.delivered() && !input.failed());
        CHECK(poll_events().empty());
        ++totals.plan_rejections;
    };
    for (const auto duration : {0U, 249U, 10001U, std::numeric_limits<unsigned>::max()}) {
        auto plan = valid; plan.duration_ms = duration; refuse_plan(plan);
    }
    { auto plan = valid; plan.event_count = 257; refuse_plan(plan); }
    { auto plan = valid; plan.event_count = std::numeric_limits<std::size_t>::max(); refuse_plan(plan); }
    { auto plan = valid; plan.events[0].at_ms = 250; refuse_plan(plan); }
    { auto plan = valid; plan.events[1].at_ms = 9; refuse_plan(plan); }
    { auto plan = valid; plan.events[0].kind = static_cast<ScriptedInputKind>(255); refuse_plan(plan); }
    for (const auto scan : {SDL_SCANCODE_UNKNOWN, SDL_SCANCODE_Q, SDL_SCANCODE_KP_ENTER,
                           SDL_NUM_SCANCODES, static_cast<SDL_Scancode>(1023)}) {
        auto plan = valid; plan.events[0].scancode = scan; refuse_plan(plan);
    }
    for (const auto modifier : {KMOD_SHIFT, KMOD_RCTRL, KMOD_RALT, KMOD_RGUI, KMOD_CAPS,
                               KMOD_NUM, KMOD_MODE, static_cast<SDL_Keymod>(0x8000)}) {
        auto plan = valid; plan.events[0].modifiers = modifier; refuse_plan(plan);
    }
    { auto plan = valid; plan.events[1].repeat = true; refuse_plan(plan); }
    for (const auto kind : {ScriptedInputKind::MouseDown, ScriptedInputKind::MouseMove,
                           ScriptedInputKind::MouseUp}) {
        for (const auto coordinate : {-8193, 16385, std::numeric_limits<int>::min(),
                                     std::numeric_limits<int>::max()}) {
            auto plan = valid;
            plan.events[0] = {};
            plan.events[0].kind = kind;
            plan.events[0].x = coordinate;
            refuse_plan(plan);
            plan.events[0].x = 0;
            plan.events[0].y = coordinate;
            refuse_plan(plan);
        }
    }
    for (const auto& dimensions : std::array{std::pair{959, 700}, std::pair{960, 699},
                                           std::pair{8193, 700}, std::pair{960, 8193}}) {
        auto plan = valid;
        plan.events[0] = {};
        plan.events[0].kind = ScriptedInputKind::Resize;
        plan.events[0].width = dimensions.first;
        plan.events[0].height = dimensions.second;
        refuse_plan(plan);
    }
    // Only active records belong to admission. Unused capacity is not script.
    auto inactive = sentinel();
    inactive.event_count = 0;
    inactive.duration_ms = 250;
    ScriptedInput ignores_inactive;
    initialized(ignores_inactive, inactive, window);
    CHECK(ignores_inactive.delivered());

    ScriptedInput once;
    initialized(once, valid, window);
    CHECK(!once.initialize(empty, window, error));
    CHECK(!error.empty());
    CHECK(once.scheduled_count() == 2 && once.duration_ms() == 250 && !once.failed());
    pump(once, 10);
    for (const auto& event : poll_events()) {
        if (!once.acknowledge(event)) CHECK(event.type == SDL_KEYDOWN || event.type == SDL_KEYUP);
    }
    CHECK(once.delivered() && once.pushed_count() == 2);
}

void check_key(const SDL_Event& event, const KeyCase& key, SDL_Keymod modifier,
               bool down, bool repeat, Uint32 window_id) {
    CHECK(event.type == static_cast<Uint32>(down ? SDL_KEYDOWN : SDL_KEYUP));
    CHECK(event.key.windowID == window_id);
    CHECK(event.key.state == (down ? SDL_PRESSED : SDL_RELEASED));
    CHECK(event.key.keysym.scancode == key.scan);
    CHECK(event.key.keysym.sym == key.symbol);
    CHECK(event.key.keysym.mod == static_cast<Uint16>(modifier));
    CHECK(event.key.repeat == static_cast<Uint8>(repeat));
    ++totals.queued;
}

void test_key_queue(SDL_Window* window) {
    std::string body;
    for (const auto& key : kKeys) {
        body += "5 key_down " + std::string{key.name} + " none 0\n";
        body += "5 key_up " + std::string{key.name} + " none\n";
    }
    for (const auto& modifier : kModifiers) {
        body += "5 key_down Slash " + std::string{modifier.text} + " 1\n";
        body += "5 key_up Slash " + std::string{modifier.text} + '\n';
    }
    auto plan = parsed(script(body));
    ScriptedInput input;
    initialized(input, plan, window);
    plan.events[0].scancode = SDL_SCANCODE_P; // initialize owns a value copy.
    plan.event_count = 0;
    plan.duration_ms = 9999;
    pump(input, 0);
    pump(input, 4);
    pump(input, 4);
    CHECK(poll_events().empty());
    CHECK(input.pushed_count() == 0 && !input.delivered());
    pump(input, 5);
    CHECK(input.pushed_count() == 102);
    CHECK(!input.delivered() && !input.completed(250));
    const auto events = poll_events();
    CHECK(events.size() == 103);
    std::size_t index = 0;
    const auto window_id = SDL_GetWindowID(window);
    for (const auto& key : kKeys) {
        check_key(events[index++], key, KMOD_NONE, true, false, window_id);
        check_key(events[index++], key, KMOD_NONE, false, false, window_id);
    }
    for (const auto& modifier : kModifiers) {
        check_key(events[index++], kKeys.back(), modifier.value, true, true, window_id);
        check_key(events[index++], kKeys.back(), modifier.value, false, false, window_id);
    }
    for (std::size_t action = 0; action < index; ++action) CHECK(!input.acknowledge(events[action]));
    CHECK(events[index].type >= SDL_USEREVENT);
    CHECK(events[index].user.windowID == window_id);
    CHECK(!input.delivered()); // Polling without acknowledgment cannot complete it.
    CHECK(input.acknowledge(events[index]));
    ++totals.markers;
    CHECK(input.delivered());
    CHECK(!input.completed(249) && input.completed(250));
    pump(input, 5);
    pump(input, 249);
    pump(input, 250);
    pump(input, std::numeric_limits<std::uint64_t>::max());
    CHECK(input.completed(std::numeric_limits<std::uint64_t>::max()));
    CHECK(input.pushed_count() == 102 && poll_events().empty());
}

void test_midi_shortcut_queue(SDL_Window* window) {
    // Native handle_key consumes the M scancode with Ctrl or Command. Check
    // those complete key events, including the release and nonrepeat bit,
    // independently of the parser's ordinary whitelist traversal above.
    const auto plan = parsed(script(
        "0 key_down M ctrl 0\n1 key_up M ctrl\n"
        "2 key_down M meta 0\n3 key_up M meta\n"));
    ScriptedInput input;
    initialized(input, plan, window);
    pump(input, 3);
    CHECK(input.pushed_count() == 4 && !input.delivered());
    const auto events = poll_events();
    CHECK(events.size() == 5);
    const KeyCase expected{"M", SDL_SCANCODE_M, SDLK_m};
    const auto window_id = SDL_GetWindowID(window);
    check_key(events[0], expected, KMOD_LCTRL, true, false, window_id);
    check_key(events[1], expected, KMOD_LCTRL, false, false, window_id);
    check_key(events[2], expected, KMOD_LGUI, true, false, window_id);
    check_key(events[3], expected, KMOD_LGUI, false, false, window_id);
    for (std::size_t index = 0; index < 4; ++index) CHECK(!input.acknowledge(events[index]));
    CHECK(input.acknowledge(events[4]));
    ++totals.markers;
    CHECK(input.delivered() && input.completed(250));
    pump(input, 250);
    CHECK(poll_events().empty());
}

void test_pointer_queue(SDL_Window* window) {
    const auto plan = parsed(script(
        "0 mouse_move -8192 16384\n1 mouse_down 10 20\n2 mouse_move 30 50\n"
        "3 focus_lost\n4 mouse_move 40 70\n5 mouse_up 16384 -8192\n6 quit\n"));
    ScriptedInput input;
    initialized(input, plan, window);
    const auto window_id = SDL_GetWindowID(window);
    for (std::uint64_t at = 0; at <= 6; ++at) {
        pump(input, at);
        const auto events = poll_events();
        CHECK(events.size() == (at == 6 ? 2U : 1U));
        const auto& event = events.front();
        CHECK(!input.acknowledge(event));
        if (at == 0 || at == 2 || at == 4) {
            CHECK(event.type == SDL_MOUSEMOTION);
            CHECK(event.motion.windowID == window_id);
            CHECK(event.motion.state == (at == 2 ? SDL_BUTTON_LMASK : 0U));
            CHECK(event.motion.x == (at == 0 ? -8192 : at == 2 ? 30 : 40));
            CHECK(event.motion.y == (at == 0 ? 16384 : at == 2 ? 50 : 70));
            CHECK(event.motion.xrel == (at == 0 ? 0 : at == 2 ? 20 : 10));
            CHECK(event.motion.yrel == (at == 0 ? 0 : at == 2 ? 30 : 20));
        } else if (at == 1 || at == 5) {
            CHECK(event.type == static_cast<Uint32>(at == 1 ? SDL_MOUSEBUTTONDOWN : SDL_MOUSEBUTTONUP));
            CHECK(event.button.windowID == window_id);
            CHECK(event.button.button == SDL_BUTTON_LEFT);
            CHECK(event.button.state == (at == 1 ? SDL_PRESSED : SDL_RELEASED));
            CHECK(event.button.clicks == 1);
            CHECK(event.button.x == (at == 1 ? 10 : 16384));
            CHECK(event.button.y == (at == 1 ? 20 : -8192));
        } else if (at == 3) {
            CHECK(event.type == SDL_WINDOWEVENT);
            CHECK(event.window.windowID == window_id);
            CHECK(event.window.event == SDL_WINDOWEVENT_FOCUS_LOST);
        } else {
            CHECK(event.type == SDL_QUIT);
            CHECK(!input.delivered());
            CHECK(input.acknowledge(events.back()));
            ++totals.markers;
        }
        ++totals.queued;
        CHECK(input.pushed_count() == at + 1);
        pump(input, at);
        CHECK(poll_events().empty());
    }
    CHECK(input.delivered() && !input.completed(249) && input.completed(250));
}

void test_resize_order(SDL_Window* window) {
    const auto plan = parsed(script(
        "10 key_down A none 0\n10 resize 1200 800\n10 mouse_down 1100 750\n"
        "10 resize 1000 720\n10 mouse_up 990 710\n11 key_up A none\n"));
    ScriptedInput input;
    initialized(input, plan, window);
    pump(input, 9);
    CHECK(poll_events().empty());
    std::size_t input_index = 0;
    std::size_t resize_count = 0;
    std::size_t barrier_count = 0;
    bool first_resize_observed = false;
    bool second_resize_observed = false;
    for (unsigned iteration = 0; iteration < 16 && !input.delivered(); ++iteration) {
        pump(input, 11);
        const auto events = poll_events();
        CHECK(!events.empty());
        for (const auto& event : events) {
            int width = 0, height = 0;
            SDL_GetWindowSize(window, &width, &height);
            if (input.acknowledge(event)) {
                ++barrier_count;
                continue;
            }
            if (event.type == SDL_WINDOWEVENT) {
                CHECK(event.window.windowID == SDL_GetWindowID(window));
                CHECK(event.window.event == SDL_WINDOWEVENT_SIZE_CHANGED ||
                      event.window.event == SDL_WINDOWEVENT_RESIZED);
                CHECK(event.window.data1 == width && event.window.data2 == height);
                if (width == 1200 && height == 800) first_resize_observed = true;
                else if (width == 1000 && height == 720) second_resize_observed = true;
                else CHECK(false);
                ++resize_count; // SDL may also enqueue its own actual size event.
                continue;
            }
            CHECK(is_input(event));
            if (input_index == 0) {
                check_key(event, kKeys.front(), KMOD_NONE, true, false, SDL_GetWindowID(window));
                CHECK(width == 960 && height == 700);
            } else if (input_index == 1) {
                CHECK(event.type == SDL_MOUSEBUTTONDOWN);
                CHECK(event.button.x == 1100 && event.button.y == 750);
                CHECK(width == 1200 && height == 800 && first_resize_observed);
                ++totals.queued;
            } else if (input_index == 2) {
                CHECK(event.type == SDL_MOUSEBUTTONUP);
                CHECK(event.button.x == 990 && event.button.y == 710);
                CHECK(width == 1000 && height == 720 && second_resize_observed);
                ++totals.queued;
            } else {
                CHECK(input_index == 3);
                check_key(event, kKeys.front(), KMOD_NONE, false, false, SDL_GetWindowID(window));
                CHECK(width == 1000 && height == 720);
            }
            ++input_index;
        }
    }
    CHECK(input_index == 4 && resize_count >= 2 && barrier_count >= 3);
    CHECK(first_resize_observed && second_resize_observed);
    CHECK(input.pushed_count() == 6 && input.delivered());
    CHECK(!input.completed(249) && input.completed(250));
    pump(input, 250);
    CHECK(poll_events().empty());
    totals.queued += 2;
    totals.markers += barrier_count;
}

void test_marker_identity(SDL_Window* window) {
    const auto plan = parsed(script("0 focus_lost\n"));
    ScriptedInput first, second;
    initialized(first, plan, window);
    initialized(second, plan, window);
    pump(first, 0);
    pump(second, 0);
    const auto events = poll_events();
    CHECK(events.size() == 4);
    CHECK(events[0].type == SDL_WINDOWEVENT && events[2].type == SDL_WINDOWEVENT);
    CHECK(events[1].type >= SDL_USEREVENT && events[3].type >= SDL_USEREVENT);
    CHECK(events[1].type != events[3].type);
    CHECK(!second.acknowledge(events[1]));
    CHECK(!first.acknowledge(events[3]));
    CHECK(!first.delivered() && !second.delivered());
    auto wrong_window = events[1];
    wrong_window.user.windowID = 0;
    CHECK(!first.acknowledge(wrong_window));
    auto wrong_owner = events[1];
    wrong_owner.user.data1 = nullptr;
    CHECK(!first.acknowledge(wrong_owner));
    CHECK(!first.delivered());
    CHECK(first.acknowledge(events[1]));
    CHECK(second.acknowledge(events[3]));
    CHECK(first.delivered() && second.delivered());
    totals.queued += 2;
    totals.markers += 2;
}

int SDLCALL reject_key_up(void*, SDL_Event* event) { return event->type == SDL_KEYUP ? 0 : 1; }
int SDLCALL reject_user_event(void*, SDL_Event* event) { return event->type >= SDL_USEREVENT ? 0 : 1; }

class EventFilter {
public:
    explicit EventFilter(SDL_EventFilter filter) { SDL_SetEventFilter(filter, nullptr); }
    ~EventFilter() { SDL_SetEventFilter(nullptr, nullptr); }
};

void test_failures(SDL_Window* window) {
    const auto plan = parsed(script("0 key_down A none 0\n0 key_up A none\n1 quit\n"));
    std::string error;
    {
        ScriptedInput uninitialized;
        CHECK(!uninitialized.pump(0, error));
        CHECK(!error.empty());
        CHECK(!uninitialized.completed(250));
        ++totals.expected_failures;
    }
    {
        ScriptedInput input;
        initialized(input, plan, window);
        const EventFilter filter{reject_key_up}; // Real SDL filtering returns zero.
        CHECK(!input.pump(1, error));
        CHECK(!error.empty() && input.failed());
        CHECK(input.pushed_count() == 1 && !input.delivered() && !input.completed(250));
        const auto first_error = error;
        const auto events = poll_events();
        CHECK(events.size() == 1);
        check_key(events.front(), kKeys.front(), KMOD_NONE, true, false, SDL_GetWindowID(window));
        CHECK(!input.pump(250, error));
        CHECK(error == first_error && input.pushed_count() == 1);
        CHECK(poll_events().empty());
        ++totals.expected_failures;
    }
    {
        ScriptedInput input;
        initialized(input, parsed(script("0 key_down A none 0\n")), window);
        const EventFilter filter{reject_user_event};
        CHECK(!input.pump(0, error));
        CHECK(!error.empty() && input.failed());
        CHECK(input.pushed_count() == 1 && !input.delivered());
        const auto events = poll_events();
        CHECK(events.size() == 1 && events.front().type == SDL_KEYDOWN);
        CHECK(!input.completed(std::numeric_limits<std::uint64_t>::max()));
        ++totals.expected_failures;
    }
    {
        ScriptedInput input;
        initialized(input, parsed(script("10 quit\n")), window);
        pump(input, 9);
        CHECK(!input.pump(8, error));
        CHECK(!error.empty() && input.failed() && input.pushed_count() == 0);
        CHECK(!input.pump(250, error));
        CHECK(!input.delivered() && poll_events().empty());
        ++totals.expected_failures;
    }
    {
        ScriptedInput input;
        initialized(input, parsed(script("0 quit\n")), window);
        const auto filler_type = SDL_RegisterEvents(1);
        CHECK(filler_type != std::numeric_limits<Uint32>::max());
        SDL_Event filler{};
        filler.type = filler_type;
        std::size_t count = 0;
        while (count < 70000 && SDL_PushEvent(&filler) == 1) ++count;
        CHECK(count > 0 && count < 70000); // Real SDL's bounded queue is full.
        CHECK(!input.pump(0, error));
        CHECK(!error.empty() && input.failed() && input.pushed_count() == 0);
        CHECK(!input.delivered() && !input.completed(250));
        SDL_FlushEvents(SDL_FIRSTEVENT, SDL_LASTEVENT);
        CHECK(!input.pump(250, error)); // Freeing queue space never retries a failed run.
        CHECK(poll_events().empty());
        ++totals.expected_failures;
    }
}

void test_lifetimes() {
    for (unsigned cycle = 0; cycle < 4; ++cycle) {
        const auto window = make_window();
        flush_events();
        const auto plan = parsed(script("0 key_down A none 0\n0 key_up A none\n"));
        {
            ScriptedInput destroyed;
            initialized(destroyed, plan, window.get());
            pump(destroyed, 0);
        } // Pending value events may outlive their helper; no callback owns it.
        ScriptedInput replacement;
        initialized(replacement, plan, window.get());
        const auto old_events = poll_events();
        CHECK(old_events.size() == 3);
        for (const auto& event : old_events) CHECK(!replacement.acknowledge(event));
        CHECK(!replacement.delivered());
        pump(replacement, 0);
        for (const auto& event : poll_events()) {
            if (replacement.acknowledge(event)) ++totals.markers;
            else CHECK(event.type == SDL_KEYDOWN || event.type == SDL_KEYUP);
        }
        CHECK(replacement.delivered() && replacement.completed(250));
        ++totals.lifetimes;
    } // Every helper is destroyed before its window and before SDL_Quit.
}

} // namespace

int main() {
    SDL_SetMainReady();
    const auto* driver = SDL_getenv("SDL_VIDEODRIVER");
    CHECK(driver != nullptr && std::string_view{driver} == "dummy");
    test_parser_boundaries();
    test_parser_payloads();
    test_files();
    CHECK_DETAIL(SDL_Init(SDL_INIT_VIDEO | SDL_INIT_EVENTS) == 0, SDL_GetError());
    CHECK(std::string_view{SDL_GetCurrentVideoDriver()} == "dummy");
    {
        const auto window = make_window();
        flush_events();
        test_empty_and_admission(window.get());
        flush_events();
        test_key_queue(window.get());
        test_midi_shortcut_queue(window.get());
        test_pointer_queue(window.get());
        test_resize_order(window.get());
        test_marker_identity(window.get());
        test_failures(window.get());
        test_lifetimes();
    }
    SDL_Quit();
    CHECK(SDL_WasInit(0) == 0);
    std::cout << "standalone replay acceptance (SDL dummy): " << totals.parsed
              << " valid parses, " << totals.parse_rejections << " atomic parser rejections, "
              << totals.loaded << " regular-file loads, " << totals.load_rejections
              << " atomic file rejections, " << totals.plan_rejections << " forged-plan rejections, "
              << totals.queued << " checked queue actions, " << totals.markers
              << " acknowledged markers, " << totals.expected_failures
              << " expected runtime failures, " << totals.lifetimes << " lifetime cycles\n";
    return 0;
}
