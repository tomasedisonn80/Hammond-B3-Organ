#ifndef SDL_MAIN_HANDLED
#define SDL_MAIN_HANDLED
#endif

#include "AudioDevice.h"
#include "Drawing.h"
#include "EmbeddedProfile.h"
#include "InstrumentView.h"
#include "ScriptedInput.h"
#include "StateFiles.h"
#include "UiModel.h"
#include "../../tools/CliArguments.h"

#include <SDL.h>

#include <algorithm>
#include <array>
#include <charconv>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <locale>
#include <memory>
#include <optional>
#include <sstream>
#include <string>
#include <string_view>
#include <system_error>
#include <utility>
#include <variant>
#include <vector>

namespace hammond::standalone {
namespace {

constexpr std::array<int, 3> kSampleRates{44100, 48000, 96000};
constexpr std::array<std::uint16_t, 5> kBufferSizes{128, 256, 512, 1024, 2048};
constexpr std::uint64_t kSaveWaitMilliseconds = 2000;
constexpr std::uint64_t kCallbackWatchdogMilliseconds = 2000;
constexpr std::uint64_t kReplayDrainMilliseconds = 2000;
constexpr std::size_t kReplayObservationCapacity = 512;

struct Options {
    AudioDeviceConfig audio{};
    std::filesystem::path state{};
    std::filesystem::path screenshot{};
    std::filesystem::path diagnostics{};
    std::filesystem::path input_script{};
    int width{1280};
    int height{900};
    std::uint32_t smoke_ms{0};
    bool help{false};
    bool list_audio{false};
};

void print_help() {
    std::cout <<
        "B-3 Workshop -- nominal dry organ\n"
        "Usage: hammond_standalone [options]\n\n"
        "  --help                 Show this help without initializing SDL.\n"
        "  --list-audio           List SDL output devices without a window.\n"
        "  --device NAME          Exact SDL output name; omitted means default.\n"
        "  --sample-rate N        44100, 48000 (default), or 96000 Hz.\n"
        "  --buffer-frames N      128, 256, 512 (default), 1024, or 2048.\n"
        "  --state PATH           Control-state file for startup, Save, and Load.\n"
        "                         Default: SDL preference directory/controls.b3controls.\n"
        "  --width N              Initial logical width: 960..8192, default 1280.\n"
        "  --height N             Initial logical height: 700..8192, default 900.\n"
        "  --smoke-ms N           Actual window/device smoke, 250..10000 ms.\n"
        "  --input-script PATH    Bounded B3UIREPLAY1 events; excludes --smoke-ms.\n"
        "  --screenshot PATH      Write one BMP before presenting the rendered frame.\n"
        "  --diagnostics PATH     Write JSON after closing and joining the device.\n\n"
        "Playing: A W S E D F T G Y H U J K O L P ;. F1/F2/F3 select\n"
        "Upper/Lower/Pedals; [ and ] change octave. Tab/Shift+Tab move focus;\n"
        "arrows, Home, End adjust controls; Space holds the focused playing key.\n"
        "Escape releases UI notes. Ctrl+S saves, Ctrl+O loads, Ctrl+, opens Audio,\n"
        "and Shift+/ opens Help (Command also works for the Ctrl shortcuts).\n"
        "Audio dialog: Tab/Shift+Tab, arrows, Home/End, Enter/Space, Escape.\n\n"
        "Existing valid state loads at startup; Save is explicit, never automatic.\n"
        "Without a state: proposed audition registration Upper B 888000000,\n"
        "Lower B 008000000, pedals 80. This is not a factory preset.\n"
        "Smoke sends one short UI note and checks real SDL callbacks and output.\n"
        "Dummy drivers are used only when explicitly selected in the environment,\n"
        "for example SDL_AUDIODRIVER=dummy SDL_VIDEODRIVER=dummy.\n"
        "No physical-device, latency, or acoustic-fidelity result is implied.\n";
}

[[nodiscard]] bool parse_integer(std::string_view text, int& destination) noexcept {
    if (text.empty() || text.front() < '0' || text.front() > '9') return false;
    int value = 0;
    const auto result = std::from_chars(text.data(), text.data() + text.size(), value);
    if (result.ec != std::errc{} || result.ptr != text.data() + text.size()) return false;
    destination = value;
    return true;
}

[[nodiscard]] bool parse_options(int argc, char** argv, Options& options, std::string& error) {
    std::vector<std::string_view> seen;
    for (int index = 1; index < argc; ++index) {
        const std::string_view option{argv[index]};
        if (std::find(seen.begin(), seen.end(), option) != seen.end()) {
            error = "Repeated option: " + std::string(option);
            return false;
        }
        seen.push_back(option);
        if (option == "--help") { options.help = true; continue; }
        if (option == "--list-audio") { options.list_audio = true; continue; }
        const bool path_option = option == "--state" || option == "--screenshot" ||
            option == "--diagnostics" || option == "--input-script";
        const bool number_option = option == "--sample-rate" || option == "--buffer-frames" ||
            option == "--width" || option == "--height" || option == "--smoke-ms";
        if (!path_option && !number_option && option != "--device") {
            error = "Unknown option: " + std::string(option);
            return false;
        }
        if (index + 1 >= argc || std::string_view{argv[index + 1]}.empty()) {
            error = "Missing value for " + std::string(option);
            return false;
        }
        const std::string_view value{argv[++index]};
        if (option == "--device") { options.audio.device_name = value; continue; }
        if (path_option) {
            auto path = cli::argument_path(value);
            if (option == "--state") options.state = std::move(path);
            else if (option == "--screenshot") options.screenshot = std::move(path);
            else if (option == "--diagnostics") options.diagnostics = std::move(path);
            else options.input_script = std::move(path);
            continue;
        }
        int number = 0;
        if (!parse_integer(value, number)) {
            error = "Invalid integer for " + std::string(option);
            return false;
        }
        bool valid = false;
        if (option == "--sample-rate") {
            valid = std::find(kSampleRates.begin(), kSampleRates.end(), number) != kSampleRates.end();
            if (valid) options.audio.sample_rate = number;
        } else if (option == "--buffer-frames") {
            valid = std::find(kBufferSizes.begin(), kBufferSizes.end(), number) != kBufferSizes.end();
            if (valid) options.audio.buffer_frames = static_cast<std::uint16_t>(number);
        } else if (option == "--width") {
            valid = number >= 960 && number <= 8192;
            if (valid) options.width = number;
        } else if (option == "--height") {
            valid = number >= 700 && number <= 8192;
            if (valid) options.height = number;
        } else {
            valid = number >= 250 && number <= 10000;
            if (valid) options.smoke_ms = static_cast<std::uint32_t>(number);
        }
        if (!valid) {
            error = "Unsupported value for " + std::string(option) + "; see --help";
            return false;
        }
    }
    if (!options.input_script.empty() && options.smoke_ms != 0) {
        error = "--input-script and --smoke-ms are mutually exclusive";
        return false;
    }
    return true;
}

[[nodiscard]] const char* status_name(SessionStatus status) noexcept {
    switch (status) {
    case SessionStatus::Ok: return "ok";
    case SessionStatus::NotPrepared: return "not_prepared";
    case SessionStatus::AlreadyRunning: return "already_running";
    case SessionStatus::NotRunning: return "not_running";
    case SessionStatus::InvalidSpec: return "invalid_spec";
    case SessionStatus::InvalidProfile: return "invalid_profile";
    case SessionStatus::InvalidBuffer: return "invalid_buffer";
    case SessionStatus::BlockTooLarge: return "block_too_large";
    case SessionStatus::TimelineOverflow: return "timeline_overflow";
    case SessionStatus::InvalidCommand: return "invalid_command";
    case SessionStatus::QueueFull: return "queue_full";
    case SessionStatus::RecoveryPending: return "recovery_pending";
    case SessionStatus::SequenceExhausted: return "sequence_exhausted";
    case SessionStatus::CoreFailure: return "core_failure";
    }
    return "unknown";
}

[[nodiscard]] UiKey ui_key(SDL_Scancode code) noexcept {
    switch (code) {
    case SDL_SCANCODE_A: return UiKey::A;
    case SDL_SCANCODE_W: return UiKey::W;
    case SDL_SCANCODE_S: return UiKey::S;
    case SDL_SCANCODE_E: return UiKey::E;
    case SDL_SCANCODE_D: return UiKey::D;
    case SDL_SCANCODE_F: return UiKey::F;
    case SDL_SCANCODE_T: return UiKey::T;
    case SDL_SCANCODE_G: return UiKey::G;
    case SDL_SCANCODE_Y: return UiKey::Y;
    case SDL_SCANCODE_H: return UiKey::H;
    case SDL_SCANCODE_U: return UiKey::U;
    case SDL_SCANCODE_J: return UiKey::J;
    case SDL_SCANCODE_K: return UiKey::K;
    case SDL_SCANCODE_O: return UiKey::O;
    case SDL_SCANCODE_L: return UiKey::L;
    case SDL_SCANCODE_P: return UiKey::P;
    case SDL_SCANCODE_SEMICOLON: return UiKey::Semicolon;
    case SDL_SCANCODE_TAB: return UiKey::Tab;
    case SDL_SCANCODE_LEFT: return UiKey::Left;
    case SDL_SCANCODE_RIGHT: return UiKey::Right;
    case SDL_SCANCODE_UP: return UiKey::Up;
    case SDL_SCANCODE_DOWN: return UiKey::Down;
    case SDL_SCANCODE_HOME: return UiKey::Home;
    case SDL_SCANCODE_END: return UiKey::End;
    case SDL_SCANCODE_SPACE: return UiKey::Space;
    case SDL_SCANCODE_RETURN:
    case SDL_SCANCODE_KP_ENTER: return UiKey::Enter;
    case SDL_SCANCODE_ESCAPE: return UiKey::Escape;
    case SDL_SCANCODE_LEFTBRACKET: return UiKey::LeftBracket;
    case SDL_SCANCODE_RIGHTBRACKET: return UiKey::RightBracket;
    case SDL_SCANCODE_F1: return UiKey::F1;
    case SDL_SCANCODE_F2: return UiKey::F2;
    case SDL_SCANCODE_F3: return UiKey::F3;
    default: return UiKey::Unknown;
    }
}

[[nodiscard]] ControlSnapshot audition_registration() noexcept {
    ControlSnapshot controls;
    controls.drawbars[0][1] = {8, 8, 8, 0, 0, 0, 0, 0, 0};
    controls.drawbars[1][1] = {0, 0, 8, 0, 0, 0, 0, 0, 0};
    controls.pedal_drawbars = {8, 0};
    return controls;
}

struct SdlLifetime {
    ~SdlLifetime() { SDL_Quit(); }
};
struct WindowDeleter {
    void operator()(SDL_Window* window) const noexcept { SDL_DestroyWindow(window); }
};
struct RendererDeleter {
    void operator()(SDL_Renderer* renderer) const noexcept { SDL_DestroyRenderer(renderer); }
};

// UTF-8 remains UTF-8; arbitrary invalid POSIX filename bytes are escaped so
// diagnostics still constitute valid JSON. Windows arguments were validated.
void json_string(std::ostream& output, std::string_view value) {
    constexpr char hex[] = "0123456789abcdef";
    output.put('"');
    for (std::size_t index = 0; index < value.size(); ++index) {
        const auto byte = static_cast<unsigned char>(value[index]);
        if (byte == '"' || byte == '\\') { output.put('\\'); output.put(value[index]); }
        else if (byte < 0x20U) {
            output << "\\u00" << hex[byte >> 4U] << hex[byte & 0x0FU];
        } else if (byte < 0x80U) output.put(value[index]);
        else {
            const std::size_t length = byte >= 0xF0U && byte <= 0xF4U ? 4U :
                byte >= 0xE0U && byte <= 0xEFU ? 3U : byte >= 0xC2U && byte <= 0xDFU ? 2U : 0U;
            bool valid = length != 0 && length <= value.size() - index;
            std::uint32_t codepoint = length == 4 ? byte & 0x07U : length == 3 ? byte & 0x0FU : byte & 0x1FU;
            for (std::size_t next = 1; valid && next < length; ++next) {
                const auto continuation = static_cast<unsigned char>(value[index + next]);
                valid = (continuation & 0xC0U) == 0x80U;
                codepoint = (codepoint << 6U) | (continuation & 0x3FU);
            }
            valid = valid && codepoint <= 0x10FFFFU && !(codepoint >= 0xD800U && codepoint <= 0xDFFFU) &&
                (length != 3 || codepoint >= 0x800U) && (length != 4 || codepoint >= 0x10000U);
            if (valid) {
                output.write(value.data() + index, static_cast<std::streamsize>(length));
                index += length - 1;
            } else output << "\\u00" << hex[byte >> 4U] << hex[byte & 0x0FU];
        }
    }
    output.put('"');
}

void write_controls_json(std::ostream& output, const ControlSnapshot& controls) {
    output << "{\"manual_drawbars\":[";
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        if (manual != 0) output << ',';
        output << '[';
        for (std::size_t bank = 0; bank < kDrawbarBankCount; ++bank) {
            if (bank != 0) output << ',';
            output << '[';
            for (std::size_t drawbar = 0; drawbar < kDrawbarCount; ++drawbar) {
                if (drawbar != 0) output << ',';
                output << static_cast<unsigned int>(controls.drawbars[manual][bank][drawbar]);
            }
            output << ']';
        }
        output << ']';
    }
    output << "],\"selected_banks\":[" << static_cast<unsigned int>(controls.selected_banks[0]) << ','
           << static_cast<unsigned int>(controls.selected_banks[1]) << "],\"route_enabled\":["
           << controls.route_enabled[0] << ',' << controls.route_enabled[1] << "],\"expression\":"
           << controls.expression << ",\"pedal_drawbars\":[" << static_cast<unsigned int>(controls.pedal_drawbars[0])
           << ',' << static_cast<unsigned int>(controls.pedal_drawbars[1]) << "],\"percussion\":{\"enabled\":"
           << controls.percussion.enabled << ",\"harmonic\":" << static_cast<unsigned int>(controls.percussion.harmonic)
           << ",\"volume\":" << static_cast<unsigned int>(controls.percussion.volume)
           << ",\"decay\":" << static_cast<unsigned int>(controls.percussion.decay) << "}}";
}

template <typename Value, std::size_t Size>
void cycle_value(Value& current, const std::array<Value, Size>& choices, int direction) noexcept {
    const auto found = std::find(choices.begin(), choices.end(), current);
    std::size_t index = found == choices.end() ? 0 : static_cast<std::size_t>(found - choices.begin());
    index = direction < 0 ? (index + Size - 1) % Size : (index + 1) % Size;
    current = choices[index];
}

class Application {
public:
    Application(Options options, RuntimeProfile profile)
        : options_(std::move(options)), profile_(std::move(profile)), config_(options_.audio),
          intended_controls_(audition_registration()) {}

    ~Application() {
        // The callback must return before Session, graphics, and finally SDL die.
        audio_.close();
        release_capture();
    }

    [[nodiscard]] bool initialize() {
        // Admit the complete script before selecting a state directory or
        // opening any output. Parsing and all file access stay off audio.
        std::optional<ScriptedInputPlan> replay_plan;
        if (!options_.input_script.empty()) {
            replay_plan.emplace();
            std::string error;
            if (!load_scripted_input(options_.input_script, *replay_plan, error)) {
                fail("Cannot load input script: " + error); return false;
            }
            replay_observations_.reserve(kReplayObservationCapacity);
        }
        window_.reset(SDL_CreateWindow("B-3 Workshop | Nominal dry organ", SDL_WINDOWPOS_CENTERED,
            SDL_WINDOWPOS_CENTERED, options_.width, options_.height,
            SDL_WINDOW_RESIZABLE | SDL_WINDOW_ALLOW_HIGHDPI));
        if (!window_) { fail(std::string("Cannot create instrument window: ") + SDL_GetError()); return false; }
        SDL_SetWindowMinimumSize(window_.get(), 960, 700);
        SDL_SetWindowMaximumSize(window_.get(), 8192, 8192);
        renderer_.reset(SDL_CreateRenderer(window_.get(), -1, SDL_RENDERER_ACCELERATED));
        if (!renderer_) renderer_.reset(SDL_CreateRenderer(window_.get(), -1, SDL_RENDERER_SOFTWARE));
        if (!renderer_) { fail(std::string("Cannot create instrument renderer: ") + SDL_GetError()); return false; }
        SDL_RendererInfo renderer_info{};
        if (SDL_GetRendererInfo(renderer_.get(), &renderer_info) != 0) {
            fail(std::string("Cannot inspect renderer: ") + SDL_GetError()); return false;
        }
        renderer_name_ = renderer_info.name != nullptr ? renderer_info.name : "unknown";
        if (const char* driver = SDL_GetCurrentVideoDriver()) video_driver_ = driver;
        drawing_ = std::make_unique<Drawing>(renderer_.get());
        std::string error;
        if (!drawing_->initialize(error)) { fail("Cannot initialize instrument text: " + error); return false; }
        if (!resize()) return false;
        choose_state_path();
        if (!output_paths_distinct()) return false;
        if (replay_plan && !replay_.initialize(*replay_plan, window_.get(), error)) {
            fail("Cannot initialize input script: " + error); return false;
        }
        load_startup_state();
        const bool opened = open_audio(config_);
        (void)opened; // A visible No Audio window remains usable for device selection.
        observe();
        return true;
    }

    [[nodiscard]] int run() {
        const std::uint64_t started = SDL_GetTicks64();
        replay_started_ = started;
        while (running_) {
            if (!pump_replay(SDL_GetTicks64() - started)) break;
            // Gather native input once per main-loop turn. Marker handlers can
            // append another due replay prefix while this bounded drain runs.
            SDL_PumpEvents();
            SDL_Event event{};
            if (SDL_WaitEventTimeout(&event, 12) != 0) {
                handle_event(event);
                for (std::size_t count = 1; count < 256 && running_; ++count) {
                    const int received = SDL_PeepEvents(&event, 1, SDL_GETEVENT,
                        SDL_FIRSTEVENT, SDL_LASTEVENT);
                    if (received < 0) {
                        fail(std::string("Cannot drain instrument events: ") + SDL_GetError());
                        fatal_failure_ = true;
                        running_ = false;
                        break;
                    }
                    if (received == 0) break;
                    handle_event(event);
                }
            }
            observe();
            monitor_audio();
            complete_save();
            check_capture();
            const auto elapsed = SDL_GetTicks64() - started;
            if (options_.smoke_ms != 0) advance_smoke(elapsed);
            if (!options_.input_script.empty()) {
                record_replay_observation(elapsed);
                if (running_ && replay_.completed(elapsed) && replay_acknowledged()) {
                    replay_completed_ = true;
                    running_ = false;
                } else if (running_ && elapsed >= replay_.duration_ms() + kReplayDrainMilliseconds) {
                    fail("Input replay could not finish delivery and acknowledgment within its bounded drain interval");
                    fatal_failure_ = true;
                    running_ = false;
                }
            }
            if (!render_frame(elapsed)) { fatal_failure_ = true; running_ = false; }
            if (options_.smoke_ms != 0 && elapsed >= options_.smoke_ms) {
                smoke_completed_ = true;
                running_ = false;
            }
        }
        // Retain script results before ordinary close cleanup can release held
        // keys or resolve additional commands. A held final script state is legal.
        replay_before_shutdown_ = snapshot_;
        replay_last_submitted_sequence_ = last_submitted_sequence_;
        replay_final_acknowledged_ = replay_acknowledged();
        replay_finalized_ = true;
        // Off always traverses the normal UiModel path, even after a smoke error.
        if (smoke_on_sent_ && !smoke_off_sent_) {
            const bool released = dispatch(ui_.key({UiKey::A, false}));
            (void)released;
        }
        const bool released = dispatch(ui_.release_ui(UiReleaseReason::WindowClosing));
        (void)released;
        audio_before_close_ = audio_.info();
        if (audio_before_close_.driver.empty()) {
            if (const char* driver = SDL_GetCurrentAudioDriver()) audio_before_close_.driver = driver;
        }
        audio_.close();
        commands_enabled_ = false;
        observe();
        final_diagnostics_ = audio_.diagnostics(); // Joined: stable copied counters.
        release_capture();
        if (!options_.screenshot.empty() && !screenshot_written_) {
            fail("The requested screenshot was not written");
            fatal_failure_ = true;
        }
        smoke_passed_ = options_.smoke_ms != 0 && smoke_completed_ && smoke_on_sent_ && smoke_off_sent_ &&
            smoke_held_observed_ && smoke_release_observed_ && render_count_ != 0 &&
            audio_before_close_.open && audio_before_close_.running &&
            final_diagnostics_.callback_count != 0 && final_diagnostics_.rendered_frames != 0 &&
            final_diagnostics_.render_failures == 0 && final_diagnostics_.format_failures == 0 &&
            final_diagnostics_.nonfinite_failures == 0 && final_diagnostics_.overrange_failures == 0 &&
            snapshot_available_ && snapshot_.fault_flags == 0 && !any_held(snapshot_) && !fatal_failure_;
        if (options_.smoke_ms != 0 && !smoke_passed_) fail("Native smoke failed; inspect the copied diagnostics");
        if (!options_.input_script.empty()) {
            replay_passed_ = replay_completed_ && replay_final_acknowledged_ && !replay_.failed() &&
                !replay_observations_truncated_ && !replay_observations_.empty() &&
                audio_before_close_.open && audio_before_close_.running &&
                final_diagnostics_.callback_count != 0 && final_diagnostics_.rendered_frames != 0 &&
                final_diagnostics_.render_failures == 0 && final_diagnostics_.format_failures == 0 &&
                final_diagnostics_.nonfinite_failures == 0 && final_diagnostics_.overrange_failures == 0 &&
                snapshot_available_ && snapshot_.fault_flags == 0 && !any_held(snapshot_) &&
                error_count_ == 0 && !fatal_failure_;
            if (!replay_passed_) fail("Native input replay failed or was interrupted; inspect the copied diagnostics");
        }
        if (!write_diagnostics()) fatal_failure_ = true;
        if (options_.smoke_ms != 0) {
            std::cout << "Native SDL smoke " << (smoke_passed_ && !fatal_failure_ ? "passed" : "failed")
                      << ": callbacks=" << final_diagnostics_.callback_count
                      << ", frames=" << final_diagnostics_.rendered_frames << ", images=" << render_count_
                      << ", driver=" << audio_before_close_.driver << '\n';
        }
        return fatal_failure_ || (options_.smoke_ms != 0 && !smoke_passed_) ||
            (!options_.input_script.empty() && !replay_passed_) ? 1 : 0;
    }

    [[nodiscard]] bool write_diagnostics() const {
        if (options_.diagnostics.empty()) return true;
        std::ofstream output(options_.diagnostics, std::ios::binary | std::ios::trunc);
        if (!output) { std::cerr << "hammond_standalone: Cannot open diagnostics output\n"; return false; }
        output.imbue(std::locale::classic());
        output << std::boolalpha << std::setprecision(17);
        SDL_version linked{};
        SDL_GetVersion(&linked);
        output << "{\n  \"schema_version\":1,\n  \"application\":\"hammond_standalone\",\n  \"profile\":{\"id\":";
        json_string(output, profile_.profile_id.data());
        output << ",\"authoring_sha256\":"; json_string(output, profile_.authoring_sha256.data());
        output << "},\n  \"runtime\":{\"video_driver\":"; json_string(output, video_driver_);
        output << ",\"renderer\":"; json_string(output, renderer_name_);
        output << ",\"sdl_version\":\"" << static_cast<unsigned int>(linked.major) << '.'
               << static_cast<unsigned int>(linked.minor) << '.' << static_cast<unsigned int>(linked.patch)
               << "\",\"window_width\":" << window_width_ << ",\"window_height\":" << window_height_
               << ",\"drawable_width\":" << drawable_width_ << ",\"drawable_height\":" << drawable_height_
               << ",\"rendered_images\":" << render_count_ << ",\"screenshot_written\":" << screenshot_written_
               << ",\"screenshot_while_held\":" << screenshot_while_held_ << "},\n  \"audio\":{\"driver\":";
        json_string(output, audio_before_close_.driver);
        output << ",\"device_name\":"; json_string(output, audio_before_close_.device_name);
        output << ",\"requested_device\":"; json_string(output, config_.device_name);
        output << ",\"requested_sample_rate\":" << config_.sample_rate
               << ",\"requested_buffer_frames\":" << config_.buffer_frames
               << ",\"sample_rate\":" << audio_before_close_.sample_rate
               << ",\"buffer_frames\":" << audio_before_close_.buffer_frames
               << ",\"channels\":" << static_cast<unsigned int>(audio_before_close_.channels)
               << ",\"sample_format\":" << audio_before_close_.sample_format
               << ",\"native_float32_format\":" << AUDIO_F32SYS
               << ",\"buffer_bytes\":" << audio_before_close_.buffer_bytes
               << ",\"open_before_shutdown\":" << audio_before_close_.open
               << ",\"running_before_shutdown\":" << audio_before_close_.running
               << ",\"callback_count\":" << final_diagnostics_.callback_count
               << ",\"rendered_frames\":" << final_diagnostics_.rendered_frames
               << ",\"render_failures\":" << final_diagnostics_.render_failures
               << ",\"format_failures\":" << final_diagnostics_.format_failures
               << ",\"overrange_failures\":" << final_diagnostics_.overrange_failures
               << ",\"overrange_samples\":" << final_diagnostics_.overrange_samples
               << ",\"nonfinite_failures\":" << final_diagnostics_.nonfinite_failures
               << ",\"nonfinite_samples\":" << final_diagnostics_.nonfinite_samples
               << ",\"last_render_status\":";
        json_string(output, status_name(final_diagnostics_.last_render_status));
        output << ",\"last_lifecycle_status\":";
        json_string(output, status_name(final_diagnostics_.last_lifecycle_status));
        output << "},\n  \"session\":{\"snapshot_available\":" << snapshot_available_
               << ",\"prepared\":" << snapshot_.prepared << ",\"running_after_shutdown\":" << snapshot_.running
               << ",\"sample_rate\":" << snapshot_.sample_rate << ",\"frame_clock\":" << snapshot_.frame_clock
               << ",\"publication_revision\":" << snapshot_.publication_revision
               << ",\"resolved_sequence\":" << snapshot_.resolved_sequence
               << ",\"last_applied_sequence\":" << snapshot_.last_applied_sequence
               << ",\"recovery_count\":" << snapshot_.recovery_count
               << ",\"queue_overflows\":" << snapshot_.queue_overflows
               << ",\"rejected_commands\":" << snapshot_.rejected_commands
               << ",\"discarded_commands\":" << snapshot_.discarded_commands
               << ",\"fault_flags\":" << snapshot_.fault_flags
               << ",\"held_after_shutdown\":" << any_held(snapshot_)
               << ",\"maximum_observed_peak\":" << maximum_observed_peak_ << "},\n  \"controls\":";
        write_controls_json(output, snapshot_.controls);
        output << ",\n  \"smoke\":{\"requested\":" << (options_.smoke_ms != 0)
               << ",\"duration_ms\":" << options_.smoke_ms << ",\"completed\":" << smoke_completed_
               << ",\"note_on_sent\":" << smoke_on_sent_ << ",\"note_off_sent\":" << smoke_off_sent_
               << ",\"held_observed\":" << smoke_held_observed_ << ",\"release_observed\":" << smoke_release_observed_
               << ",\"passed\":" << smoke_passed_ << '}';
        if (!options_.input_script.empty()) write_replay_json(output);
        output << ",\n  \"state_path\":";
        json_string(output, cli::path_text(options_.state));
        output << ",\n  \"status\":"; json_string(output, status_);
        output << ",\n  \"errors\":{\"count\":" << error_count_ << ",\"last\":";
        json_string(output, last_error_);
        output << "}\n}\n";
        output.flush();
        if (!output) { std::cerr << "hammond_standalone: Cannot write complete diagnostics\n"; return false; }
        output.close();
        return static_cast<bool>(output);
    }

private:
    struct ReplayObservation {
        SessionSnapshot snapshot;
        std::uint64_t elapsed_ms;
        std::uint64_t last_submitted_sequence;
    };

    [[nodiscard]] bool pump_replay(std::uint64_t elapsed) {
        if (options_.input_script.empty()) return true;
        std::string error;
        if (replay_.pump(elapsed, error)) return true;
        fail("Cannot deliver input script: " + error);
        fatal_failure_ = true;
        running_ = false;
        return false;
    }

    [[nodiscard]] bool replay_acknowledged() const noexcept {
        return snapshot_available_ && snapshot_.running &&
            snapshot_.resolved_sequence >= last_submitted_sequence_ &&
            snapshot_.last_applied_sequence >= last_submitted_sequence_ &&
            !pending_save_ && !ui_.view().controls_pending;
    }

    void record_replay_observation(std::uint64_t elapsed) {
        // Preparation publishes defaults before the queued restore. Record
        // running musical observations only after that restore is acknowledged.
        if (!snapshot_available_ || !snapshot_.running ||
            snapshot_.resolved_sequence < intended_sequence_) return;
        if (!replay_observations_.empty()) {
            const auto& previous = replay_observations_.back();
            if (previous.snapshot.controls == snapshot_.controls &&
                previous.snapshot.held_keys == snapshot_.held_keys &&
                previous.snapshot.held_pedals == snapshot_.held_pedals &&
                previous.snapshot.resolved_sequence == snapshot_.resolved_sequence &&
                previous.snapshot.last_applied_sequence == snapshot_.last_applied_sequence &&
                previous.last_submitted_sequence == last_submitted_sequence_) return;
        }
        if (replay_observations_.size() == kReplayObservationCapacity) {
            if (!replay_observations_truncated_) fail("Input replay observation capacity was exceeded");
            replay_observations_truncated_ = true;
            fatal_failure_ = true;
            running_ = false;
            return;
        }
        replay_observations_.push_back({snapshot_, elapsed, last_submitted_sequence_});
    }

    static void write_replay_snapshot(std::ostream& output, const SessionSnapshot& snapshot) {
        output << "\"manual_notes\":[";
        for (std::size_t manual = 0; manual < kManualCount; ++manual) {
            if (manual != 0) output << ',';
            output << '[';
            bool first = true;
            for (std::size_t key = 0; key < kManualKeyCount; ++key) {
                if (!snapshot.held_keys[manual][key]) continue;
                if (!first) output << ',';
                first = false;
                output << key + kMinManualMidiNote;
            }
            output << ']';
        }
        output << "],\"pedal_ids\":[";
        bool first = true;
        for (std::size_t pedal = 0; pedal < kPedalCount; ++pedal) {
            if (!snapshot.held_pedals[pedal]) continue;
            if (!first) output << ',';
            first = false;
            output << pedal + 1;
        }
        output << "],\"controls\":";
        write_controls_json(output, snapshot.controls);
        output << ",\"resolved_sequence\":" << snapshot.resolved_sequence
               << ",\"last_applied_sequence\":" << snapshot.last_applied_sequence;
    }

    void write_replay_json(std::ostream& output) const {
        output << ",\n  \"replay\":{\"completed\":" << replay_completed_
               << ",\"delivered\":" << replay_.delivered() << ",\"passed\":" << replay_passed_
               << ",\"duration_ms\":" << replay_.duration_ms()
               << ",\"scheduled_events\":" << replay_.scheduled_count()
               << ",\"pushed_events\":" << replay_.pushed_count()
               << ",\"final_acknowledged\":" << replay_final_acknowledged_
               << ",\"last_submitted_sequence\":" << replay_last_submitted_sequence_
               << ",\"accepted_note_on_commands\":" << replay_accepted_note_on_
               << ",\"accepted_note_off_commands\":" << replay_accepted_note_off_
               << ",\"device_starts\":" << device_starts_
               << ",\"observations_truncated\":" << replay_observations_truncated_
               << ",\"before_shutdown\":{";
        write_replay_snapshot(output, replay_before_shutdown_);
        output << "},\"observations\":[";
        for (std::size_t index = 0; index < replay_observations_.size(); ++index) {
            if (index != 0) output << ',';
            const auto& observation = replay_observations_[index];
            output << "{\"elapsed_ms\":" << observation.elapsed_ms
                   << ",\"last_submitted_sequence\":" << observation.last_submitted_sequence << ',';
            write_replay_snapshot(output, observation.snapshot);
            output << '}';
        }
        output << "]}";
    }

    void record_accepted(const SessionCommand& command, const SubmitResult& result) noexcept {
        last_submitted_sequence_ = result.sequence;
        if (std::holds_alternative<ControlSnapshot>(command)) last_control_sequence_ = result.sequence;
        if (options_.input_script.empty() || replay_finalized_) return;
        const auto* input = std::get_if<PerformanceInputEvent>(&command);
        if (input == nullptr) return;
        if (const auto* manual = std::get_if<HostNoteEvent>(input)) {
            if (manual->kind == HostNoteKind::On && manual->velocity != 0) ++replay_accepted_note_on_;
            else if (manual->kind == HostNoteKind::Off || manual->kind == HostNoteKind::On) ++replay_accepted_note_off_;
        } else if (const auto* pedal = std::get_if<PedalNoteEvent>(input)) {
            if (pedal->kind == PedalNoteKind::On && pedal->velocity != 0) ++replay_accepted_note_on_;
            else if (pedal->kind == PedalNoteKind::Off || pedal->kind == PedalNoteKind::On) ++replay_accepted_note_off_;
        }
    }

    [[nodiscard]] static bool any_held(const SessionSnapshot& snapshot) noexcept {
        for (const auto& manual : snapshot.held_keys) {
            if (std::any_of(manual.begin(), manual.end(), [](bool held) { return held; })) return true;
        }
        return std::any_of(snapshot.held_pedals.begin(), snapshot.held_pedals.end(), [](bool held) { return held; });
    }

    void message(std::string text) { status_ = std::move(text); status_until_ = SDL_GetTicks64() + 6000; }
    void fail(std::string text) {
        last_error_ = text;
        status_ = std::move(text);
        status_until_ = 0;
        ++error_count_;
        std::cerr << "hammond_standalone: " << last_error_ << '\n';
    }

    void choose_state_path() {
        if (!options_.state.empty()) return;
        char* preference = SDL_GetPrefPath("B3Workshop", "HammondStandalone");
        if (preference == nullptr) { fail(std::string("Cannot choose state directory: ") + SDL_GetError()); return; }
        const std::unique_ptr<char, decltype(&SDL_free)> owned(preference, &SDL_free);
        options_.state = cli::argument_path(preference) / "controls.b3controls";
    }

    [[nodiscard]] bool output_paths_distinct() {
        const std::array<std::filesystem::path, 4> paths{
            options_.state, options_.screenshot, options_.diagnostics, options_.input_script};
        // A dangling leaf on any selected path can alias an absent state file.
        // StateFiles also requires a nonsymlink leaf; preserve that boundary.
        for (std::size_t index = 0; index < paths.size(); ++index) {
            if (paths[index].empty()) continue;
            std::error_code error;
            const auto status = std::filesystem::symlink_status(paths[index], error);
            if (error && error != std::errc::no_such_file_or_directory) {
                fail("Cannot inspect selected path: " + error.message()); return false;
            }
            if (std::filesystem::is_symlink(status)) {
                fail("State, screenshot, diagnostics, and input script paths must not be symbolic links"); return false;
            }
            if (index != 0 && std::filesystem::exists(status) && !std::filesystem::is_regular_file(status)) {
                fail("Screenshot and diagnostics outputs must be regular files or new paths"); return false;
            }
        }
        const auto resolve = [](const std::filesystem::path& path, std::error_code& error) {
            const auto absolute = std::filesystem::absolute(path, error);
            if (error) return std::filesystem::path{};
            // Resolve the existing prefix even when the final filename is new.
            return std::filesystem::weakly_canonical(absolute, error);
        };
        for (std::size_t first = 0; first < paths.size(); ++first) {
            if (paths[first].empty()) continue;
            for (std::size_t second = first + 1; second < paths.size(); ++second) {
                if (paths[second].empty()) continue;
                std::error_code error;
                const auto a = resolve(paths[first], error);
                if (error) { fail("Cannot resolve output path: " + error.message()); return false; }
                const auto b = resolve(paths[second], error);
                if (error) { fail("Cannot resolve output path: " + error.message()); return false; }
                const bool same = a == b || std::filesystem::equivalent(a, b, error);
                if (same) { fail("State, screenshot, diagnostics, and input script must use different files"); return false; }
            }
        }
        return true;
    }

    void load_startup_state() {
        if (options_.state.empty()) return;
        std::error_code error_code;
        const bool exists = std::filesystem::exists(options_.state, error_code);
        if (error_code) { fail("Cannot inspect saved controls: " + error_code.message()); return; }
        if (!exists) return;
        ControlSnapshot candidate;
        std::string error;
        if (!load_control_file(options_.state, candidate, error)) {
            fail("Startup state was not loaded: " + error); return;
        }
        intended_controls_ = candidate;
        initial_from_file_ = true;
    }

    [[nodiscard]] bool initialize_audio() {
        if ((SDL_WasInit(SDL_INIT_AUDIO) & SDL_INIT_AUDIO) != 0) return true;
        if (SDL_InitSubSystem(SDL_INIT_AUDIO) != 0) {
            fail(std::string("No Audio: cannot initialize selected SDL audio driver: ") + SDL_GetError());
            return false;
        }
        return true;
    }

    [[nodiscard]] bool open_audio(const AudioDeviceConfig& candidate) {
        commands_enabled_ = false;
        config_ = candidate; // Retain exact requested choices even when open fails.
        if (!initialize_audio()) return false;
        std::string error;
        if (!audio_.open(session_, profile_, config_, error)) { fail("No Audio: " + error); return false; }
        commands_enabled_ = true; // Paused preparation admits the explicit restore.
        UiActions restore;
        if (intended_controls_) restore = ui_.load_controls(*intended_controls_);
        else {
            restore.items[0] = SessionCommand{retained_controls_};
            restore.count = 1;
        }
        if (!dispatch(restore) || !audio_.start(error)) {
            commands_enabled_ = false;
            audio_.close();
            observe();
            fail(error.empty() ? "No Audio: controls could not be queued before start" : "No Audio: " + error);
            return false;
        }
        intended_sequence_ = last_control_sequence_;
        ++device_starts_;
        last_callback_count_ = audio_.diagnostics().callback_count;
        last_callback_time_ = SDL_GetTicks64();
        if (error_count_ == 0) {
            message(initial_from_file_ ? "Loaded saved controls. Audio is running." :
                "Proposed audition registration: Upper B 888000000 / Lower B 008000000 / Pedals 80.");
        }
        return true;
    }

    void observe() {
        SessionSnapshot candidate;
        if (!session_.read_snapshot(candidate)) return;
        snapshot_ = candidate;
        snapshot_available_ = true;
        retained_controls_ = candidate.controls;
        ui_.observe(candidate);
        if (std::isfinite(candidate.peak)) maximum_observed_peak_ = std::max(maximum_observed_peak_, candidate.peak);
        if (intended_controls_ && intended_sequence_ != 0 && candidate.resolved_sequence >= intended_sequence_ &&
            candidate.last_applied_sequence >= intended_sequence_ && candidate.controls == *intended_controls_) {
            intended_controls_.reset();
        }
        constexpr std::size_t middle_c_index = 60 - kMinManualMidiNote;
        if (smoke_on_sent_ && candidate.held_keys[0][middle_c_index]) smoke_held_observed_ = true;
        if (smoke_off_sent_ && smoke_held_observed_ && !candidate.held_keys[0][middle_c_index]) smoke_release_observed_ = true;
    }

    [[nodiscard]] bool dispatch(const UiActions& actions) {
        for (const auto& action : actions.span()) {
            if (const auto* command = std::get_if<SessionCommand>(&action)) {
                // A stopped Session intentionally admits commands. Reject at the
                // device gate instead of accumulating work without a consumer.
                const SubmitResult result = commands_enabled_ ? session_.post(*command) :
                    SubmitResult{SessionStatus::NotRunning, 0};
                const auto recovery = ui_.submitted(*command, result);
                if (result.ok()) {
                    record_accepted(*command, result);
                    continue;
                }
                pending_save_.reset();
                if (commands_enabled_) fail(std::string("Input rejected: ") + status_name(result.status));
                else if (!std::holds_alternative<ReleaseUiNotes>(*command)) {
                    message("No Audio. Open AUDIO settings to select and start an output.");
                }
                // Exactly one recovery batch; never continue the original batch,
                // recursively retry, or replay discarded notes after an overflow.
                for (const auto& item : recovery.span()) {
                    const auto* release = std::get_if<SessionCommand>(&item);
                    if (release == nullptr) continue;
                    const auto recovered = commands_enabled_ ? session_.post(*release) :
                        SubmitResult{SessionStatus::NotRunning, 0};
                    const auto ignored = ui_.submitted(*release, recovered);
                    (void)ignored;
                    if (!recovered.ok()) break;
                    record_accepted(*release, recovered);
                }
                return false;
            }
            handle_request(std::get<UiAppRequest>(action));
        }
        return true;
    }

    void handle_request(UiAppRequest request) {
        switch (request) {
        case UiAppRequest::SaveControls: request_save(); break;
        case UiAppRequest::LoadControls: load_state(); break;
        case UiAppRequest::AudioSettings: open_overlay(ViewOverlay::Audio); break;
        case UiAppRequest::Help: open_overlay(ViewOverlay::Help); break;
        }
    }

    void request_save() {
        observe();
        if (options_.state.empty()) { fail("No state path. Restart with --state PATH."); return; }
        if (!snapshot_available_ || !snapshot_.prepared || intended_controls_) {
            fail("Save requires acknowledged controls. Start audio and wait for the controls to apply."); return;
        }
        pending_save_ = PendingSave{ui_.view().controls, snapshot_.recovery_count, snapshot_.rejected_commands,
            snapshot_.discarded_commands, last_control_sequence_, SDL_GetTicks64() + kSaveWaitMilliseconds};
        complete_save();
        if (pending_save_) message("Waiting for the audio callback to acknowledge controls before saving...");
    }

    void complete_save() {
        if (!pending_save_) return;
        const auto pending = *pending_save_;
        if (snapshot_.recovery_count != pending.recoveries || snapshot_.rejected_commands != pending.rejections ||
            snapshot_.discarded_commands != pending.discards || !(ui_.view().controls == pending.controls)) {
            pending_save_.reset();
            fail("Save cancelled because controls changed or input recovered. Choose Save again."); return;
        }
        if (ui_.view().controls_pending || snapshot_.resolved_sequence < pending.sequence ||
            !(snapshot_.controls == pending.controls)) {
            if (SDL_GetTicks64() >= pending.deadline) {
                pending_save_.reset(); fail("Save timed out waiting for acknowledged controls.");
            }
            return;
        }
        pending_save_.reset();
        std::string error;
        const auto saved = snapshot_.controls; // One coherent, acknowledged copy.
        if (!save_control_file(options_.state, saved, error)) { fail("Cannot save controls: " + error); return; }
        ui_.mark_saved(saved);
        message("Saved controls to " + cli::path_text(options_.state));
    }

    void load_state() {
        pending_save_.reset();
        ControlSnapshot candidate;
        std::string error;
        if (!load_control_file(options_.state, candidate, error)) { fail("Cannot load controls: " + error); return; }
        if (!commands_enabled_) {
            intended_controls_ = candidate;
            intended_sequence_ = 0;
            message("State read. Open AUDIO settings to apply these controls.");
            return;
        }
        if (dispatch(ui_.load_controls(candidate))) message("Loaded controls; waiting for the audio callback.");
    }

    void release_capture() noexcept {
        if (captured_) {
            const int ignored = SDL_CaptureMouse(SDL_FALSE);
            (void)ignored;
            captured_ = false;
        }
    }

    void lose_input(UiReleaseReason reason) {
        const bool released = dispatch(ui_.release_ui(reason));
        const bool pointer_released = dispatch(ui_.pointer({UiPointerKind::CaptureLost, {}}));
        (void)released;
        (void)pointer_released;
        release_capture();
    }

    void check_capture() {
        if (captured_ && (SDL_GetWindowFlags(window_.get()) & SDL_WINDOW_MOUSE_CAPTURE) == 0) {
            captured_ = false;
            const bool released = dispatch(ui_.pointer({UiPointerKind::CaptureLost, {}}));
            (void)released;
        }
    }

    [[nodiscard]] bool resize() {
        SDL_GetWindowSize(window_.get(), &window_width_, &window_height_);
        const int width = std::clamp(window_width_, 960, 8192);
        const int height = std::clamp(window_height_, 700, 8192);
        if (width != window_width_ || height != window_height_) {
            SDL_SetWindowSize(window_.get(), width, height);
            SDL_GetWindowSize(window_.get(), &window_width_, &window_height_);
        }
        if (!ui_.resize(static_cast<float>(window_width_), static_cast<float>(window_height_)) ||
            SDL_GetRendererOutputSize(renderer_.get(), &drawable_width_, &drawable_height_) != 0 ||
            drawable_width_ <= 0 || drawable_height_ <= 0 ||
            SDL_RenderSetScale(renderer_.get(), static_cast<float>(drawable_width_) / static_cast<float>(window_width_),
                static_cast<float>(drawable_height_) / static_cast<float>(window_height_)) != 0) {
            fail(std::string("Cannot resize instrument layout: ") + SDL_GetError()); return false;
        }
        return true;
    }

    void open_overlay(ViewOverlay overlay) {
        lose_input(UiReleaseReason::FocusLost);
        overlay_ = overlay;
        ui_.set_text_entry_active(true);
        modal_focus_ = overlay == ViewOverlay::Help ? 5U : 0U;
        if (overlay != ViewOverlay::Audio) return;
        selected_config_ = config_;
        const auto current = audio_.info();
        if (current.open) {
            selected_config_.sample_rate = current.sample_rate;
            selected_config_.buffer_frames = current.buffer_frames;
        }
        audio_choices_.clear();
        audio_choices_.emplace_back("Default output");
        std::vector<std::string> names;
        std::string error;
        if (initialize_audio() && AudioDevice::enumerate_output_devices(names, error)) {
            for (auto& name : names) audio_choices_.push_back(std::move(name));
        } else if (!error.empty()) fail(error);
        selected_device_ = 0;
        if (!config_.device_name.empty()) {
            const auto found = std::find(audio_choices_.begin() + 1, audio_choices_.end(), config_.device_name);
            if (found != audio_choices_.end()) selected_device_ = static_cast<std::size_t>(found - audio_choices_.begin());
        }
        message("Audio: Tab selects a control; arrows change values; Enter applies a button; Escape closes.");
    }

    void close_overlay() {
        overlay_ = ViewOverlay::None;
        ui_.set_text_entry_active(false);
        // Physical-key records are intentionally retained until their actual Up.
    }

    [[nodiscard]] std::array<UiRect, 6> modal_rectangles() const noexcept {
        const auto boxes = audio_overlay_layout(ui_.layout().width, ui_.layout().height);
        return {boxes.previous_device, boxes.next_device, boxes.sample_rate,
                boxes.buffer_frames, boxes.apply, boxes.close};
    }

    void change_modal_value(int direction) {
        if (modal_focus_ <= 1 && !audio_choices_.empty()) {
            selected_device_ = direction < 0 ? (selected_device_ + audio_choices_.size() - 1) % audio_choices_.size() :
                (selected_device_ + 1) % audio_choices_.size();
        } else if (modal_focus_ == 2) cycle_value(selected_config_.sample_rate, kSampleRates, direction);
        else if (modal_focus_ == 3) cycle_value(selected_config_.buffer_frames, kBufferSizes, direction);
    }

    void activate_modal() {
        if (overlay_ == ViewOverlay::Help || modal_focus_ == 5) { close_overlay(); return; }
        if (modal_focus_ < 4) { change_modal_value(modal_focus_ == 0 ? -1 : 1); return; }
        pending_save_.reset();
        lose_input(UiReleaseReason::FocusLost);
        audio_.close(); // Joins callbacks, then stops Session, before any prepare.
        commands_enabled_ = false;
        observe(); // Includes every control actually applied before the join.
        selected_config_.device_name = selected_device_ == 0 ? std::string{} : audio_choices_[selected_device_];
        if (open_audio(selected_config_)) {
            message("Audio restarted. Acknowledged controls retained; notes released and source phase reset.");
            close_overlay();
        }
    }

    void modal_key(const UiKeyInput& input) {
        if (input.repeat || input.control || input.alt || input.meta) return;
        if (input.key == UiKey::Escape) { close_overlay(); return; }
        if (overlay_ == ViewOverlay::Help) {
            if (input.key == UiKey::Enter || input.key == UiKey::Space) close_overlay();
            return;
        }
        if (input.key == UiKey::Tab) {
            modal_focus_ = input.shift ? (modal_focus_ + 5) % 6 : (modal_focus_ + 1) % 6;
        } else if (input.key == UiKey::Enter || input.key == UiKey::Space) activate_modal();
        else if (input.key == UiKey::Left || input.key == UiKey::Down) change_modal_value(-1);
        else if (input.key == UiKey::Right || input.key == UiKey::Up) change_modal_value(1);
        else if (input.key == UiKey::Home || input.key == UiKey::End) {
            const bool end = input.key == UiKey::End;
            if (modal_focus_ <= 1) selected_device_ = end ? audio_choices_.size() - 1 : 0;
            else if (modal_focus_ == 2) selected_config_.sample_rate = end ? kSampleRates.back() : kSampleRates.front();
            else if (modal_focus_ == 3) selected_config_.buffer_frames = end ? kBufferSizes.back() : kBufferSizes.front();
        }
    }

    void handle_key(const SDL_KeyboardEvent& event) {
        const auto modifiers = event.keysym.mod;
        const UiKeyInput input{ui_key(event.keysym.scancode), event.type == SDL_KEYDOWN, event.repeat != 0,
            (modifiers & KMOD_SHIFT) != 0, (modifiers & KMOD_CTRL) != 0,
            (modifiers & KMOD_ALT) != 0, (modifiers & KMOD_GUI) != 0};
        const auto previous_overlay = overlay_;
        const bool accepted = dispatch(ui_.key(input)); // Up precedes every modal/modifier/focus gate.
        (void)accepted;
        if (!input.down) return;
        if (previous_overlay != ViewOverlay::None) { modal_key(input); return; }
        if (input.repeat || input.alt) return;
        if (input.control || input.meta) {
            if (event.keysym.scancode == SDL_SCANCODE_S) request_save();
            else if (event.keysym.scancode == SDL_SCANCODE_O) load_state();
            else if (event.keysym.scancode == SDL_SCANCODE_COMMA) open_overlay(ViewOverlay::Audio);
        } else if (event.keysym.scancode == SDL_SCANCODE_SLASH && input.shift) open_overlay(ViewOverlay::Help);
    }

    void handle_event(const SDL_Event& event) {
        if (!options_.input_script.empty() && replay_.acknowledge(event)) {
            // Consumed-prefix markers permit the next resize immediately,
            // within the ordinary bounded 256-event poll budget.
            if (running_) { const bool pumped = pump_replay(SDL_GetTicks64() - replay_started_); (void)pumped; }
            return;
        }
        if (event.type == SDL_QUIT) { lose_input(UiReleaseReason::WindowClosing); running_ = false; return; }
        if (event.type == SDL_KEYUP) { handle_key(event.key); return; }
        if (event.type == SDL_KEYDOWN && event.key.windowID == SDL_GetWindowID(window_.get())) {
            handle_key(event.key); return;
        }
        if (event.type == SDL_MOUSEBUTTONUP && event.button.button == SDL_BUTTON_LEFT) {
            const bool released = dispatch(ui_.pointer({UiPointerKind::Up,
                {static_cast<float>(event.button.x), static_cast<float>(event.button.y)}}));
            (void)released;
            release_capture();
            return;
        }
        if (event.type == SDL_MOUSEBUTTONDOWN && event.button.button == SDL_BUTTON_LEFT &&
            event.button.windowID == SDL_GetWindowID(window_.get())) {
            const UiPoint point{static_cast<float>(event.button.x), static_cast<float>(event.button.y)};
            if (overlay_ != ViewOverlay::None) {
                const auto rectangles = modal_rectangles();
                const std::size_t first = overlay_ == ViewOverlay::Help ? 5U : 0U;
                for (std::size_t index = first; index < rectangles.size(); ++index) {
                    if (rectangles[index].contains(point)) { modal_focus_ = index; activate_modal(); break; }
                }
            } else {
                const bool capture_succeeded = SDL_CaptureMouse(SDL_TRUE) == 0;
                captured_ = capture_succeeded;
                const bool accepted = dispatch(ui_.pointer({UiPointerKind::Down, point}));
                (void)accepted;
                if (!capture_succeeded) {
                    const bool released = dispatch(ui_.pointer({UiPointerKind::CaptureLost, point}));
                    (void)released;
                } else if (!ui_.view().pointer_captured) release_capture();
            }
            return;
        }
        if (event.type == SDL_MOUSEMOTION && overlay_ == ViewOverlay::None &&
            event.motion.windowID == SDL_GetWindowID(window_.get())) {
            const bool accepted = dispatch(ui_.pointer({UiPointerKind::Move,
                {static_cast<float>(event.motion.x), static_cast<float>(event.motion.y)}}));
            (void)accepted;
            return;
        }
        if (event.type == SDL_WINDOWEVENT && event.window.windowID == SDL_GetWindowID(window_.get())) {
            switch (event.window.event) {
            case SDL_WINDOWEVENT_CLOSE: lose_input(UiReleaseReason::WindowClosing); running_ = false; break;
            case SDL_WINDOWEVENT_FOCUS_LOST:
            case SDL_WINDOWEVENT_HIDDEN:
            case SDL_WINDOWEVENT_MINIMIZED: lose_input(UiReleaseReason::FocusLost); break;
            case SDL_WINDOWEVENT_SIZE_CHANGED:
            case SDL_WINDOWEVENT_DISPLAY_CHANGED:
                if (!resize()) { fatal_failure_ = true; running_ = false; }
                break;
            default: break;
            }
        } else if (event.type == SDL_AUDIODEVICEREMOVED && audio_.is_removed_by(event.adevice)) {
            lose_input(UiReleaseReason::FocusLost);
            audio_.close();
            commands_enabled_ = false;
            observe();
            fail("No Audio: an output device was removed. Open AUDIO settings to restart.");
        } else if (event.type == SDL_RENDER_DEVICE_RESET) {
            drawing_.reset();
            drawing_ = std::make_unique<Drawing>(renderer_.get());
            std::string error;
            if (!drawing_->initialize(error)) {
                fail("Cannot restore renderer textures: " + error); fatal_failure_ = true; running_ = false;
            }
        }
    }

    void monitor_audio() {
        if (!audio_.is_running()) return;
        const auto diagnostics = audio_.diagnostics();
        const auto now = SDL_GetTicks64();
        if (diagnostics.callback_count != last_callback_count_) {
            last_callback_count_ = diagnostics.callback_count;
            last_callback_time_ = now;
        }
        const bool fault = diagnostics.render_failures > handled_render_failures_ ||
            diagnostics.format_failures > handled_format_failures_ ||
            diagnostics.nonfinite_failures > handled_nonfinite_failures_;
        const bool stalled = now - last_callback_time_ >= kCallbackWatchdogMilliseconds;
        if (!fault && !stalled) return;
        handled_render_failures_ = diagnostics.render_failures;
        handled_format_failures_ = diagnostics.format_failures;
        handled_nonfinite_failures_ = diagnostics.nonfinite_failures;
        lose_input(UiReleaseReason::FocusLost);
        audio_.close();
        commands_enabled_ = false;
        observe();
        fail(stalled ? "No Audio: no callback progress for two seconds. Open AUDIO settings to restart." :
            "No Audio: callback output failed validation. Open AUDIO settings to restart.");
    }

    void send_smoke_key(bool down) {
        SDL_Event event{};
        event.type = down ? SDL_KEYDOWN : SDL_KEYUP;
        event.key.type = event.type;
        event.key.windowID = SDL_GetWindowID(window_.get());
        event.key.state = down ? SDL_PRESSED : SDL_RELEASED;
        event.key.keysym.scancode = SDL_SCANCODE_A;
        event.key.keysym.sym = SDLK_a;
        event.key.keysym.mod = KMOD_NONE;
        if (SDL_PushEvent(&event) != 1) {
            fail(std::string("Cannot submit smoke key event: ") + SDL_GetError());
            fatal_failure_ = true;
        } else if (down) smoke_on_sent_ = true;
        else smoke_off_sent_ = true;
    }

    void advance_smoke(std::uint64_t elapsed) {
        if (!smoke_on_sent_ && elapsed >= 30 && elapsed < options_.smoke_ms / 2U &&
            audio_.is_running() && snapshot_.running && !ui_.view().controls_pending) send_smoke_key(true);
        if (smoke_on_sent_ && !smoke_off_sent_ && elapsed >= (options_.smoke_ms * 2U) / 3U) send_smoke_key(false);
    }

    [[nodiscard]] bool render_frame(std::uint64_t elapsed) {
        if (!drawing_) return false;
        if (status_until_ != 0 && SDL_GetTicks64() >= status_until_) { status_.clear(); status_until_ = 0; }
        const auto device = audio_.info();
        const auto diagnostics = audio_.diagnostics();
        const InstrumentViewInfo information{device.running, device.sample_rate, device.buffer_frames,
            device.driver, device.device_name, status_, diagnostics.overrange_samples, overlay_, audio_choices_,
            selected_device_, selected_config_.sample_rate, selected_config_.buffer_frames};
        paint_instrument(*drawing_, ui_, information);
        if (overlay_ != ViewOverlay::None) drawing_->outline(modal_rectangles()[modal_focus_], kUiFocusCyan, 2.0F);
        if (SDL_RenderFlush(renderer_.get()) != 0) {
            fail(std::string("Cannot render instrument: ") + SDL_GetError()); return false;
        }
        ++render_count_;
        const bool smoke_capture = smoke_held_observed_ && !smoke_off_sent_;
        const bool last_chance = options_.smoke_ms != 0 && elapsed >= options_.smoke_ms;
        const bool replay_capture = !options_.input_script.empty() && replay_completed_;
        if (!options_.screenshot.empty() && !screenshot_attempted_ &&
            (replay_capture || (options_.input_script.empty() &&
                (options_.smoke_ms == 0 || smoke_capture || last_chance)))) {
            screenshot_attempted_ = true;
            std::string error;
            // The backbuffer is defined here; RenderPresent invalidates it.
            screenshot_written_ = drawing_->save_bmp(cli::path_text(options_.screenshot), error);
            screenshot_while_held_ = screenshot_written_ && (smoke_capture || (replay_capture && any_held(snapshot_)));
            if (!screenshot_written_) { fail("Cannot save screenshot: " + error); fatal_failure_ = true; }
        }
        SDL_RenderPresent(renderer_.get());
        return true;
    }

    struct PendingSave {
        ControlSnapshot controls;
        std::uint64_t recoveries;
        std::uint64_t rejections;
        std::uint64_t discards;
        std::uint64_t sequence;
        std::uint64_t deadline;
    };

    Options options_;
    RuntimeProfile profile_;
    Session session_;
    AudioDevice audio_; // Destruction precedes Session.
    UiModel ui_;
    std::unique_ptr<SDL_Window, WindowDeleter> window_;
    std::unique_ptr<SDL_Renderer, RendererDeleter> renderer_;
    std::unique_ptr<Drawing> drawing_; // Font textures precede renderer/window destruction.
    ScriptedInput replay_; // The window outlives its replay helper.
    std::vector<ReplayObservation> replay_observations_;
    AudioDeviceConfig config_;
    AudioDeviceConfig selected_config_;
    std::optional<ControlSnapshot> intended_controls_;
    ControlSnapshot retained_controls_{};
    SessionSnapshot snapshot_{};
    SessionSnapshot replay_before_shutdown_{};
    std::optional<PendingSave> pending_save_;
    AudioDeviceInfo audio_before_close_{};
    AudioDeviceDiagnostics final_diagnostics_{};
    std::vector<std::string> audio_choices_;
    std::string status_;
    std::string last_error_;
    std::string renderer_name_;
    std::string video_driver_;
    ViewOverlay overlay_{ViewOverlay::None};
    std::size_t selected_device_{0};
    std::size_t modal_focus_{0};
    std::uint64_t last_control_sequence_{0};
    std::uint64_t last_submitted_sequence_{0};
    std::uint64_t replay_last_submitted_sequence_{0};
    std::uint64_t replay_started_{0};
    std::uint64_t replay_accepted_note_on_{0};
    std::uint64_t replay_accepted_note_off_{0};
    std::uint64_t device_starts_{0};
    std::uint64_t intended_sequence_{0};
    std::uint64_t last_callback_count_{0};
    std::uint64_t last_callback_time_{0};
    std::uint64_t handled_render_failures_{0};
    std::uint64_t handled_format_failures_{0};
    std::uint64_t handled_nonfinite_failures_{0};
    std::uint64_t status_until_{0};
    std::uint64_t error_count_{0};
    std::uint64_t render_count_{0};
    int window_width_{0};
    int window_height_{0};
    int drawable_width_{0};
    int drawable_height_{0};
    float maximum_observed_peak_{0.0F};
    bool initial_from_file_{false};
    bool commands_enabled_{false};
    bool running_{true};
    bool captured_{false};
    bool snapshot_available_{false};
    bool fatal_failure_{false};
    bool screenshot_attempted_{false};
    bool screenshot_written_{false};
    bool screenshot_while_held_{false};
    bool smoke_on_sent_{false};
    bool smoke_off_sent_{false};
    bool smoke_held_observed_{false};
    bool smoke_release_observed_{false};
    bool smoke_completed_{false};
    bool smoke_passed_{false};
    bool replay_completed_{false};
    bool replay_passed_{false};
    bool replay_final_acknowledged_{false};
    bool replay_finalized_{false};
    bool replay_observations_truncated_{false};
};

int run_application(int argc, char** argv) {
    Options options;
    std::string error;
    if (!parse_options(argc, argv, options, error)) {
        std::cerr << "hammond_standalone: " << error << '\n';
        return 2;
    }
    if (options.help) { print_help(); return 0; }
    SDL_SetMainReady();
    const SdlLifetime sdl;
    if (options.list_audio) {
        if (SDL_Init(SDL_INIT_AUDIO) != 0) {
            std::cerr << "hammond_standalone: Cannot initialize audio: " << SDL_GetError() << '\n'; return 1;
        }
        std::vector<std::string> names;
        if (!AudioDevice::enumerate_output_devices(names, error)) { std::cerr << error << '\n'; return 1; }
        const char* driver = SDL_GetCurrentAudioDriver();
        std::cout << "SDL audio driver: " << (driver != nullptr ? driver : "unknown")
                  << "\nDefault output: omit --device\n";
        for (std::size_t index = 0; index < names.size(); ++index) std::cout << index + 1 << ": " << names[index] << '\n';
        return 0;
    }
    if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_TIMER | SDL_INIT_EVENTS) != 0) {
        std::cerr << "hammond_standalone: Cannot initialize video: " << SDL_GetError() << '\n'; return 1;
    }
    RuntimeProfile profile;
    std::istringstream input{std::string{vst3::kEmbeddedProfileText}};
    if (!load_runtime_profile(input, profile, error)) {
        std::cerr << "hammond_standalone: Cannot load embedded nominal profile: " << error << '\n'; return 1;
    }
    Application application{std::move(options), std::move(profile)};
    if (!application.initialize()) return 1;
    return application.run();
}

int guarded_application(int argc, char** argv) {
    try { return run_application(argc, argv); }
    catch (const std::exception& error) {
        std::cerr << "hammond_standalone: " << error.what() << '\n';
        return 1;
    } catch (...) {
        std::cerr << "hammond_standalone: Unexpected application failure\n";
        return 1;
    }
}

} // namespace
} // namespace hammond::standalone

#ifdef _WIN32
int wmain(int argc, wchar_t* argv[]) {
    return hammond::cli::run_windows(argc, argv, &hammond::standalone::guarded_application,
                                    "hammond_standalone");
}
#else
int main(int argc, char* argv[]) {
    return hammond::standalone::guarded_application(argc, argv);
}
#endif
