#ifndef SDL_MAIN_HANDLED
#define SDL_MAIN_HANDLED
#endif

#include "AudioDevice.h"
#include "Drawing.h"
#include "EmbeddedProfile.h"
#include "InstrumentView.h"
#include "MidiDevice.h"
#include "MidiInput.h"
#include "MidiReplay.h"
#include "ScriptedInput.h"
#include "StateFiles.h"
#include "UiModel.h"
#include "../../tools/CliArguments.h"

#include <SDL.h>

#include <algorithm>
#include <array>
#include <charconv>
#include <chrono>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <locale>
#include <limits>
#include <memory>
#include <optional>
#include <span>
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
constexpr std::size_t kMidiReplayEventBudget = 512;
constexpr std::size_t kMidiReplayObservationCapacity = 4 * kMidiReplayMaxEvents + kReplayObservationCapacity;

struct Options {
    AudioDeviceConfig audio{};
    MidiRouting midi_routing{};
    std::string midi_port{};
    std::filesystem::path state{};
    std::filesystem::path screenshot{};
    std::filesystem::path diagnostics{};
    std::filesystem::path input_script{};
    std::filesystem::path midi_script{};
    int width{1280};
    int height{900};
    std::uint32_t smoke_ms{0};
    bool help{false};
    bool list_audio{false};
    bool list_midi{false};
};

void print_help() {
    std::cout <<
        "B-3 Workshop -- nominal dry organ\n"
        "Usage: hammond_standalone [options]\n\n"
        "  --help                 Show this help without initializing SDL.\n"
        "  --list-audio           List SDL output devices without a window.\n"
        "  --list-midi            List exact MIDI input names without initializing SDL.\n"
        "  --midi-port NAME       Open this exact MIDI input; omitted means no input.\n"
        "  --midi-upper-channel N Upper wire channel, 1..16 (default 1).\n"
        "  --midi-lower-channel N Lower wire channel, 1..16 (default 2).\n"
        "  --midi-pedal-channel N Pedal wire channel, 1..16 (default 3).\n"
        "                         The three MIDI channels must be distinct.\n"
        "  --device NAME          Exact SDL output name; omitted means default.\n"
        "  --sample-rate N        44100, 48000 (default), or 96000 Hz.\n"
        "  --buffer-frames N      128, 256, 512 (default), 1024, or 2048.\n"
        "  --state PATH           Control-state file for startup, Save, and Load.\n"
        "                         Default: SDL preference directory/controls.b3controls.\n"
        "  --width N              Initial logical width: 960..8192, default 1280.\n"
        "  --height N             Initial logical height: 700..8192, default 900.\n"
        "  --smoke-ms N           Actual window/device smoke, 250..10000 ms.\n"
        "  --input-script PATH    Bounded B3UIREPLAY1 events; excludes --smoke-ms.\n"
        "  --midi-script PATH     Synthetic B3MIDIREPLAY1 input; excludes --midi-port,\n"
        "                         --list-midi, and --smoke-ms. Starts disconnected.\n"
        "                         Paired UI/MIDI scripts must have equal durations.\n"
        "  --screenshot PATH      Write one BMP before presenting the rendered frame.\n"
        "  --diagnostics PATH     Write JSON after closing and joining the device.\n\n"
        "Playing: A W S E D F T G Y H U J K O L P ;. F1/F2/F3 select\n"
        "Upper/Lower/Pedals; [ and ] change octave. Tab/Shift+Tab move focus;\n"
        "arrows, Home, End adjust controls; Space holds the focused playing key.\n"
        "Escape releases UI notes. Ctrl+S saves, Ctrl+O loads, Ctrl+, opens Audio,\n"
        "Ctrl+M opens MIDI, and Shift+/ opens Help (Command also works for Ctrl).\n"
        "Audio/MIDI dialogs: Tab/Shift+Tab, arrows, Home/End, Enter/Space, Escape.\n"
        "MIDI uses one explicit input port; Apply connects and Disconnect releases\n"
        "only MIDI owners. A fault, Panic, or audio restart requires explicit Apply.\n\n"
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
        if (option == "--list-midi") { options.list_midi = true; continue; }
        const bool path_option = option == "--state" || option == "--screenshot" ||
            option == "--diagnostics" || option == "--input-script" || option == "--midi-script";
        const bool number_option = option == "--sample-rate" || option == "--buffer-frames" ||
            option == "--width" || option == "--height" || option == "--smoke-ms" ||
            option == "--midi-upper-channel" || option == "--midi-lower-channel" ||
            option == "--midi-pedal-channel";
        if (!path_option && !number_option && option != "--device" && option != "--midi-port") {
            error = "Unknown option: " + std::string(option);
            return false;
        }
        if (index + 1 >= argc || std::string_view{argv[index + 1]}.empty()) {
            error = "Missing value for " + std::string(option);
            return false;
        }
        const std::string_view value{argv[++index]};
        if (option == "--device") { options.audio.device_name = value; continue; }
        if (option == "--midi-port") {
            if (value.size() > kMidiMaximumPortNameBytes || value.find('\0') != std::string_view::npos) {
                error = "Invalid exact MIDI input name";
                return false;
            }
            options.midi_port = value;
            continue;
        }
        if (path_option) {
            auto path = cli::argument_path(value);
            if (option == "--state") options.state = std::move(path);
            else if (option == "--screenshot") options.screenshot = std::move(path);
            else if (option == "--diagnostics") options.diagnostics = std::move(path);
            else if (option == "--midi-script") options.midi_script = std::move(path);
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
        } else if (option == "--smoke-ms") {
            valid = number >= 250 && number <= 10000;
            if (valid) options.smoke_ms = static_cast<std::uint32_t>(number);
        } else {
            valid = number >= 1 && number <= 16;
            if (valid) {
                const auto channel = static_cast<std::uint8_t>(number);
                if (option == "--midi-upper-channel") options.midi_routing.upper_channel = channel;
                else if (option == "--midi-lower-channel") options.midi_routing.lower_channel = channel;
                else options.midi_routing.pedal_channel = channel;
            }
        }
        if (!valid) {
            error = "Unsupported value for " + std::string(option) + "; see --help";
            return false;
        }
    }
    if (!valid_midi_routing(options.midi_routing)) {
        error = "MIDI upper, lower, and pedal channels must be distinct values from 1 through 16";
        return false;
    }
    if (options.list_audio && options.list_midi) {
        error = "--list-audio and --list-midi are mutually exclusive";
        return false;
    }
    if (!options.input_script.empty() && options.smoke_ms != 0) {
        error = "--input-script and --smoke-ms are mutually exclusive";
        return false;
    }
    if (!options.midi_script.empty() &&
        (!options.midi_port.empty() || options.smoke_ms != 0 || options.list_midi)) {
        error = "--midi-script excludes --midi-port, --list-midi, and --smoke-ms";
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

[[nodiscard]] const char* midi_state_name(MidiDeviceState state) noexcept {
    switch (state) {
    case MidiDeviceState::Unavailable: return "unavailable";
    case MidiDeviceState::Closed: return "closed";
    case MidiDeviceState::Open: return "open";
    case MidiDeviceState::Disconnected: return "disconnected";
    case MidiDeviceState::Faulted: return "faulted";
    }
    return "unknown";
}

void increment_counter(std::uint64_t& value) noexcept {
    if (value != std::numeric_limits<std::uint64_t>::max()) ++value;
}

// There is exactly one device and one inbox for the lifetime of the app. A
// backend that cannot establish callback quiescence quarantines its context;
// the matching inbox must also survive until process termination. Ordinary
// close destroys both normally, including during initialization exceptions.
struct MidiLifetime {
    std::unique_ptr<MidiInbox> inbox{std::make_unique<MidiInbox>()};
    MidiDevice device;

    ~MidiLifetime() {
        device.close();
        if (!device.is_quiescent()) (void)inbox.release();
    }
};

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
           << static_cast<unsigned int>(controls.selected_banks[1]) << "],\"fixed_registrations\":["
           << static_cast<unsigned int>(controls.fixed_registrations[0]) << ','
           << static_cast<unsigned int>(controls.fixed_registrations[1]) << "],\"preset_selections\":[";
    for (std::size_t manual = 0; manual < kManualCount; ++manual) {
        if (manual != 0) output << ',';
        PresetSelection selection{};
        if (control_preset_selection(controls, static_cast<Manual>(manual), selection)) {
            output << static_cast<unsigned int>(selection);
        } else output << "null"; // Invalid copied controls must not masquerade as Cancel.
    }
    output << "],\"route_enabled\":["
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
        midi_input_.end_epoch();
        midi_.device.close();
        audio_.close();
        release_capture();
    }

    [[nodiscard]] bool initialize() {
        // Admit both complete scripts before selecting a state directory or
        // opening any output. Parsing and all file access stay off audio.
        std::optional<ScriptedInputPlan> replay_plan;
        if (!options_.input_script.empty()) {
            replay_plan.emplace();
            std::string error;
            if (!load_scripted_input(options_.input_script, *replay_plan, error)) {
                fail("Cannot load input script: " + error); return false;
            }
        }
        if (midi_replay_requested()) {
            std::string error;
            if (!load_midi_replay(options_.midi_script, midi_replay_.plan, error)) {
                fail("Cannot load MIDI script: " + error); return false;
            }
            if (replay_plan && replay_plan->duration_ms != midi_replay_.plan.duration_ms) {
                fail("Paired --input-script and --midi-script durations must be equal"); return false;
            }
            for (std::size_t index = 0; index < midi_replay_.plan.event_count; ++index) {
                if (midi_replay_.plan.events[index].kind == MidiReplayKind::Bytes) {
                    ++midi_replay_.scheduled_packets;
                }
            }
        }
        if (replay_requested()) replay_observations_.reserve(replay_observation_capacity());
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
        midi_routing_ = options_.midi_routing;
        selected_midi_routing_ = midi_routing_;
        midi_requested_port_ = options_.midi_port;
        midi_native_requested_ = !options_.midi_port.empty();
        if (midi_replay_requested()) {
            midi_status_ = "Synthetic replay is disconnected; waiting for an explicit script connect event.";
        } else if (!MidiDevice::backend_available()) midi_status_ = "MIDI backend unavailable in this build.";
        if (!options_.midi_port.empty()) {
            const bool connected = request_midi(options_.midi_port, midi_routing_);
            midi_startup_failed_ = !connected;
        }
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
            if (running_) {
                pump_midi_replay(SDL_GetTicks64() - started);
                process_midi();
            }
            complete_save();
            check_capture();
            const auto elapsed = SDL_GetTicks64() - started;
            if (options_.smoke_ms != 0) advance_smoke(elapsed);
            if (replay_requested()) {
                record_replay_observation(elapsed);
                const bool ui_finished = options_.input_script.empty() || replay_.completed(elapsed);
                const bool midi_finished = !midi_replay_requested() ||
                    (elapsed >= midi_replay_.plan.duration_ms &&
                     midi_replay_.cursor == midi_replay_.plan.event_count &&
                     midi_.inbox->pending() == 0 && !pending_midi_open_ && !midi_retirement_waiting_);
                if (running_ && ui_finished && midi_finished && replay_acknowledged()) {
                    replay_completed_ = !options_.input_script.empty();
                    midi_replay_.completed = midi_replay_requested();
                    running_ = false;
                } else if (running_ && elapsed >= replay_duration_ms() + kReplayDrainMilliseconds) {
                    fail(midi_replay_requested() ?
                        "MIDI replay could not finish delivery and acknowledgment within its bounded drain interval" :
                        "Input replay could not finish delivery and acknowledgment within its bounded drain interval");
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
        replay_desired_controls_ = ui_.view().controls;
        replay_snapshot_available_ = snapshot_available_;
        replay_controls_pending_ = ui_.view().controls_pending;
        replay_save_pending_ = pending_save_.has_value();
        replay_last_submitted_sequence_ = last_submitted_sequence_;
        replay_final_acknowledged_ = replay_acknowledged();
        replay_finalized_ = true;
        midi_before_shutdown_ = midi_.device.info();
        midi_active_before_shutdown_ = midi_input_.active();
        midi_replay_.connected_before_shutdown = midi_replay_.connected;
        midi_replay_.faulted_before_shutdown = midi_replay_.faulted;
        midi_replay_.pending_packets_before_shutdown = midi_.inbox->pending();
        midi_replay_.pending_connect_before_shutdown = pending_midi_open_.has_value();
        midi_replay_.release_pending_before_shutdown = midi_retirement_waiting_;
        retire_midi("MIDI input closed for application shutdown.");
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
        copy_midi_diagnostics(); // Quarantine, if any, remains explicitly nonquiescent.
        release_capture();
        if (!options_.screenshot.empty() && !screenshot_written_) {
            fail("The requested screenshot was not written");
            fatal_failure_ = true;
        }
        smoke_passed_ = options_.smoke_ms != 0 && smoke_completed_ && smoke_on_sent_ && smoke_off_sent_ &&
            smoke_held_observed_ && smoke_release_observed_ && render_count_ != 0 &&
            (options_.screenshot.empty() || screenshot_while_held_) &&
            audio_before_close_.open && audio_before_close_.running &&
            final_diagnostics_.callback_count != 0 && final_diagnostics_.rendered_frames != 0 &&
            final_diagnostics_.render_failures == 0 && final_diagnostics_.format_failures == 0 &&
            final_diagnostics_.nonfinite_failures == 0 && final_diagnostics_.overrange_failures == 0 &&
            snapshot_available_ && snapshot_.fault_flags == 0 && !any_held(snapshot_) && !fatal_failure_ &&
            !midi_startup_failed_ && !midi_shutdown_failed_;
        if (options_.smoke_ms != 0 && !smoke_passed_) fail("Native smoke failed; inspect the copied diagnostics");
        if (replay_requested()) {
            const bool healthy_replay = replay_final_acknowledged_ && !replay_.failed() &&
                !replay_observations_truncated_ && !replay_observations_.empty() &&
                audio_before_close_.open && audio_before_close_.running &&
                final_diagnostics_.callback_count != 0 && final_diagnostics_.rendered_frames != 0 &&
                final_diagnostics_.render_failures == 0 && final_diagnostics_.format_failures == 0 &&
                final_diagnostics_.nonfinite_failures == 0 && final_diagnostics_.overrange_failures == 0 &&
                snapshot_available_ && snapshot_.fault_flags == 0 && !any_held(snapshot_) &&
                error_count_ == 0 && !fatal_failure_ && !midi_startup_failed_ && !midi_shutdown_failed_;
            replay_passed_ = !options_.input_script.empty() && replay_completed_ && healthy_replay;
            midi_replay_.passed = midi_replay_requested() && midi_replay_.completed && healthy_replay;
            if ((!options_.input_script.empty() && !replay_passed_) ||
                (midi_replay_requested() && !midi_replay_.passed)) {
                fail(midi_replay_requested() ?
                    "Native MIDI replay failed or was interrupted; inspect the copied diagnostics" :
                    "Native input replay failed or was interrupted; inspect the copied diagnostics");
            }
        }
        if (!write_diagnostics()) fatal_failure_ = true;
        if (options_.smoke_ms != 0) {
            std::cout << "Native SDL smoke " << (smoke_passed_ && !fatal_failure_ ? "passed" : "failed")
                      << ": callbacks=" << final_diagnostics_.callback_count
                      << ", frames=" << final_diagnostics_.rendered_frames << ", images=" << render_count_
                      << ", driver=" << audio_before_close_.driver << '\n';
        }
        return fatal_failure_ || midi_startup_failed_ || midi_shutdown_failed_ ||
            (options_.smoke_ms != 0 && !smoke_passed_) ||
            (!options_.input_script.empty() && !replay_passed_) ||
            (midi_replay_requested() && !midi_replay_.passed) ? 1 : 0;
    }

    [[nodiscard]] bool write_diagnostics() const {
        if (options_.diagnostics.empty()) return true;
        std::ofstream output(options_.diagnostics, std::ios::binary | std::ios::trunc);
        if (!output) { std::cerr << "hammond_standalone: Cannot open diagnostics output\n"; return false; }
        output.imbue(std::locale::classic());
        output << std::boolalpha << std::setprecision(17);
        SDL_version linked{};
        SDL_GetVersion(&linked);
        output << "{\n  \"schema_version\":3,\n  \"application\":\"hammond_standalone\",\n  \"profile\":{\"id\":";
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
        output << "},\n  \"midi\":";
        write_midi_json(output);
        output << ",\n  \"session\":{\"snapshot_available\":" << snapshot_available_
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
        if (midi_replay_requested()) write_midi_replay_json(output);
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
    struct MidiRequest {
        std::string port;
        MidiRouting routing;
        bool synthetic{false};
    };

    // Main-thread synthetic producer state. MidiDevice remains unopened; its
    // native diagnostics must never inherit this source's connection state.
    struct MidiReplayState {
        MidiReplayPlan plan{};
        std::size_t cursor{0};
        std::size_t maximum_events_per_turn{0};
        std::size_t pending_packets_before_shutdown{0};
        std::uint64_t scheduled_packets{0};
        std::uint64_t offered_packets{0};
        std::uint64_t accepted_packets{0};
        std::uint64_t ignored_while_closed{0};
        std::uint64_t rejected_packets{0};
        std::uint64_t connect_events{0};
        std::uint64_t connections_started{0};
        std::uint64_t disconnect_events{0};
        std::uint64_t intentional_backend_faults{0};
        std::uint64_t intentional_overflow_faults{0};
        std::uint64_t faults_while_closed{0};
        std::uint64_t connect_barriers{0};
        std::uint64_t barrier_wait_turns{0};
        std::uint64_t cancelled_connects{0};
        std::uint64_t budget_exhaustions{0};
        std::uint64_t last_arrival_ns{0};
        bool connected{false};
        bool faulted{false};
        bool connected_before_shutdown{false};
        bool faulted_before_shutdown{false};
        bool pending_connect_before_shutdown{false};
        bool release_pending_before_shutdown{false};
        bool completed{false};
        bool passed{false};
    };

    struct ReplayObservation {
        SessionSnapshot snapshot;
        std::uint64_t elapsed_ms;
        std::uint64_t last_submitted_sequence;
    };

    [[nodiscard]] bool midi_replay_requested() const noexcept {
        return !options_.midi_script.empty();
    }

    [[nodiscard]] bool replay_requested() const noexcept {
        return !options_.input_script.empty() || midi_replay_requested();
    }

    [[nodiscard]] std::uint32_t replay_duration_ms() const noexcept {
        return midi_replay_requested() ? midi_replay_.plan.duration_ms : replay_.duration_ms();
    }

    [[nodiscard]] std::size_t replay_observation_capacity() const noexcept {
        return midi_replay_requested() ? kMidiReplayObservationCapacity : kReplayObservationCapacity;
    }

    void write_midi_json(std::ostream& output) const {
        output << "{\"source\":";
        json_string(output, midi_replay_requested() ? "synthetic-replay" :
            (midi_native_requested_ ? "native" : "none"));
        output << ",\"backend_available\":" << MidiDevice::backend_available() << ",\"backend\":";
        json_string(output, MidiDevice::backend_name());
        output << ",\"requested_port\":"; json_string(output, midi_requested_port_);
        output << ",\"port_name\":"; json_string(output, midi_final_info_.port_name);
        output << ",\"opened_port_index\":" << midi_final_info_.opened_port_index
               << ",\"generation\":" << midi_final_info_.generation
               << ",\"state_before_shutdown\":";
        json_string(output, midi_state_name(midi_before_shutdown_.state));
        output << ",\"state_after_shutdown\":"; json_string(output, midi_state_name(midi_final_info_.state));
        output << ",\"active_before_shutdown\":" << midi_active_before_shutdown_
               << ",\"active_after_shutdown\":" << midi_input_.active()
               << ",\"quiescent_after_shutdown\":" << midi_final_quiescent_
               << ",\"diagnostics_stable_after_shutdown\":" << midi_final_quiescent_
               << ",\"shutdown_failed\":" << midi_shutdown_failed_
               << ",\"startup_failed\":" << midi_startup_failed_
               << ",\"channels\":{\"upper\":" << static_cast<unsigned int>(midi_routing_.upper_channel)
               << ",\"lower\":" << static_cast<unsigned int>(midi_routing_.lower_channel)
               << ",\"pedals\":" << static_cast<unsigned int>(midi_routing_.pedal_channel)
               << "},\"drain_budget\":" << kMidiDrainBudget
               << ",\"maximum_drained_per_turn\":" << midi_maximum_drain_
               << ",\"timing_policy\":\"arrival_order_next_callback_boundary\""
               << ",\"arrival_time_unit\":\"steady_clock_nanoseconds\""
               << ",\"arrival_time_source\":";
        json_string(output, midi_replay_requested() ? "synthetic_main_thread_receipt" :
            (midi_native_requested_ ? "native_callback_receipt" : "none"));
        output << ",\"arrival_time_is_sample_time\":false"
               << ",\"retirements\":" << midi_retirements_
               << ",\"fault_retirements\":" << midi_fault_retirements_
               << ",\"session_recoveries_observed\":" << midi_session_recoveries_
               << ",\"open_failures\":" << midi_open_failures_
               << ",\"submit_failures\":" << midi_submit_failures_
               << ",\"release_batches\":" << midi_release_batches_
               << ",\"release_commands_accepted\":" << midi_release_commands_
               << ",\"release_sequence\":" << midi_release_sequence_
               << ",\"release_pending\":" << midi_retirement_waiting_
               << ",\"parameter_messages\":" << midi_parameter_messages_
               << ",\"retired_fault_bits\":" << midi_retired_faults_
               << ",\"last_submit_status\":";
        json_string(output, status_name(midi_last_submit_status_));
        output << ",\"status\":"; json_string(output, midi_status_);
        output << ",\"device\":{\"callback_messages\":" << midi_final_device_.callback_messages
               << ",\"forwarded_messages\":" << midi_final_device_.forwarded_messages
               << ",\"filtered_messages\":" << midi_final_device_.filtered_messages
               << ",\"admission_failures\":" << midi_final_device_.admission_failures
               << ",\"backend_errors\":" << midi_final_device_.backend_errors
               << ",\"callback_contentions\":" << midi_final_device_.callback_contentions
               << ",\"disconnects\":" << midi_final_device_.disconnects
               << ",\"close_errors\":" << midi_final_device_.close_errors
               << ",\"last_arrival_ns\":" << midi_final_device_.last_arrival_ns
               << "},\"inbox\":{\"capacity\":" << kMidiInboxCapacity
               << ",\"pending_packets\":" << midi_final_pending_
               << ",\"received_packets\":" << midi_final_inbox_.received_packets
               << ",\"accepted_packets\":" << midi_final_inbox_.accepted_packets
               << ",\"invalid_size_packets\":" << midi_final_inbox_.invalid_size_packets
               << ",\"faulted_packets\":" << midi_final_inbox_.faulted_packets
               << ",\"overflow_events\":" << midi_final_inbox_.overflow_events
               << ",\"popped_packets\":" << midi_final_inbox_.popped_packets
               << ",\"discarded_packets\":" << midi_final_inbox_.discarded_packets
               << ",\"resets\":" << midi_final_inbox_.resets
               << ",\"fault_bits\":" << midi_final_inbox_.faults
               << "},\"decoder\":{\"packets\":" << midi_final_input_.packets
               << ",\"actions\":" << midi_final_input_.actions
               << ",\"unsupported\":" << midi_final_input_.unsupported
               << ",\"unmapped_channels\":" << midi_final_input_.unmapped_channels
               << ",\"out_of_range\":" << midi_final_input_.out_of_range
               << ",\"malformed\":" << midi_final_input_.malformed
               << ",\"inactive\":" << midi_final_input_.inactive
               << ",\"timestamp_regressions\":" << midi_final_input_.timestamp_regressions
               << ",\"epochs\":" << midi_final_input_.epochs << "}}";
    }

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
        if (replay_observations_.size() == replay_observation_capacity()) {
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
               << ",\"pushed_events\":" << replay_.pushed_count();
        write_replay_results(output);
        output << '}';
    }

    void write_midi_replay_json(std::ostream& output) const {
        output << ",\n  \"midi_replay\":{\"source\":\"synthetic-replay\""
               << ",\"completed\":" << midi_replay_.completed
               << ",\"delivered\":" << (midi_replay_.cursor == midi_replay_.plan.event_count)
               << ",\"passed\":" << midi_replay_.passed
               << ",\"duration_ms\":" << midi_replay_.plan.duration_ms
               << ",\"scheduled_events\":" << midi_replay_.plan.event_count
               << ",\"delivered_events\":" << midi_replay_.cursor
               << ",\"scheduled_packets\":" << midi_replay_.scheduled_packets
               << ",\"offered_packets\":" << midi_replay_.offered_packets
               << ",\"accepted_packets\":" << midi_replay_.accepted_packets
               << ",\"dropped_packets\":" << (midi_replay_.ignored_while_closed +
                    midi_replay_.rejected_packets + midi_final_inbox_.discarded_packets)
               << ",\"ignored_while_closed\":" << midi_replay_.ignored_while_closed
               << ",\"rejected_packets\":" << midi_replay_.rejected_packets
               << ",\"discarded_queued_packets\":" << midi_final_inbox_.discarded_packets
               << ",\"connect_events\":" << midi_replay_.connect_events
               << ",\"connections_started\":" << midi_replay_.connections_started
               << ",\"disconnect_events\":" << midi_replay_.disconnect_events
               << ",\"intentional_backend_faults\":" << midi_replay_.intentional_backend_faults
               << ",\"intentional_overflow_faults\":" << midi_replay_.intentional_overflow_faults
               << ",\"faults_while_closed\":" << midi_replay_.faults_while_closed
               << ",\"failure_count\":" << error_count_
               << ",\"connect_barriers\":" << midi_replay_.connect_barriers
               << ",\"barrier_wait_turns\":" << midi_replay_.barrier_wait_turns
               << ",\"cancelled_connects\":" << midi_replay_.cancelled_connects
               << ",\"event_budget\":" << kMidiReplayEventBudget
               << ",\"maximum_events_per_turn\":" << midi_replay_.maximum_events_per_turn
               << ",\"budget_exhaustions\":" << midi_replay_.budget_exhaustions
               << ",\"arrival_time_source\":\"synthetic_main_thread_steady_clock_receipt\""
               << ",\"arrival_time_is_sample_time\":false"
               << ",\"last_arrival_ns\":" << midi_replay_.last_arrival_ns
               << ",\"connected_before_shutdown\":" << midi_replay_.connected_before_shutdown
               << ",\"faulted_before_shutdown\":" << midi_replay_.faulted_before_shutdown
               << ",\"connected_after_shutdown\":" << midi_replay_.connected
               << ",\"pending_packets_before_shutdown\":" << midi_replay_.pending_packets_before_shutdown
               << ",\"pending_connect_before_shutdown\":" << midi_replay_.pending_connect_before_shutdown
               << ",\"release_pending_before_shutdown\":" << midi_replay_.release_pending_before_shutdown;
        write_replay_results(output);
        output << '}';
    }

    // Both transports use the same Session observations and sequence barrier.
    // The existing UI replay event/delivery fields keep their original meaning.
    void write_replay_results(std::ostream& output) const {
        output << ",\"final_acknowledged\":" << replay_final_acknowledged_
               << ",\"snapshot_available_before_shutdown\":" << replay_snapshot_available_
               << ",\"session_running_before_shutdown\":" << replay_before_shutdown_.running
               << ",\"controls_pending_before_shutdown\":" << replay_controls_pending_
               << ",\"save_pending_before_shutdown\":" << replay_save_pending_
               << ",\"desired_controls_before_shutdown\":";
        write_controls_json(output, replay_desired_controls_);
        output << ",\"last_submitted_sequence\":" << replay_last_submitted_sequence_
               << ",\"accepted_note_on_commands\":" << replay_accepted_note_on_
               << ",\"accepted_note_off_commands\":" << replay_accepted_note_off_
               << ",\"device_starts\":" << device_starts_
               << ",\"observation_capacity\":" << replay_observation_capacity()
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
        output << ']';
    }

    void record_accepted(const SessionCommand& command, const SubmitResult& result) noexcept {
        last_submitted_sequence_ = result.sequence;
        if (std::holds_alternative<ControlSnapshot>(command)) last_control_sequence_ = result.sequence;
        if (!replay_requested() || replay_finalized_) return;
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

    // MIDI note/release commands deliberately bypass UiModel::submitted: an
    // unexpected adapter rejection must never become ReleaseUiNotes. Controls
    // take external_parameter() and the ordinary UI acknowledgment path below.
    [[nodiscard]] SubmitResult post_midi_command(const SessionCommand& command) {
        const auto result = commands_enabled_ ? session_.post(command) :
            SubmitResult{SessionStatus::NotRunning, 0};
        midi_last_submit_status_ = result.status;
        if (result.ok()) record_accepted(command, result);
        else increment_counter(midi_submit_failures_);
        return result;
    }

    void retire_midi(std::string_view reason) {
        const bool had_pending_request = pending_midi_open_.has_value();
        if (pending_midi_open_ && pending_midi_open_->synthetic) {
            increment_counter(midi_replay_.cancelled_connects);
        }
        pending_midi_open_.reset();
        if (midi_shutdown_failed_) return; // Never retry or replace a quarantined epoch.
        const bool had_epoch = midi_input_.active() || midi_.device.is_open() || midi_replay_.connected ||
            midi_.inbox->faults() != 0 || midi_.inbox->pending() != 0;
        if (!had_epoch) {
            if (had_pending_request) midi_status_ = reason;
            return;
        }
        midi_input_.end_epoch();
        // No synthetic producer callback exists. Closing admission here, on
        // its sole main thread, establishes quiescence before the same reset.
        midi_replay_.connected = false;
        midi_status_ = reason;
        midi_retired_faults_ |= midi_.inbox->faults();
        if (!midi_replay_requested()) midi_.device.close();
        midi_retired_faults_ |= midi_.inbox->faults();
        if (midi_.device.is_quiescent()) {
            midi_.inbox->reset_quiescent();
        } else if (!midi_shutdown_failed_) {
            midi_shutdown_failed_ = true;
            midi_status_ = "MIDI shutdown failed; restart the application before using MIDI.";
            fail(midi_status_);
        }
        increment_counter(midi_retirements_);
        midi_retirement_waiting_ = true;
        midi_release_failed_ = false;
        midi_release_sequence_ = 0;
        midi_retirement_recovery_ = snapshot_.recovery_count;
        if (!commands_enabled_) return; // The audio close/stop lifecycle resolves owners.
        increment_counter(midi_release_batches_);
        for (const auto& command : midi_release_commands()) {
            const auto result = post_midi_command(command);
            if (!result.ok()) {
                midi_release_failed_ = true;
                midi_release_sequence_ = 0; // A partial batch is not a retirement acknowledgment.
                fail(std::string("MIDI release rejected: ") + status_name(result.status) +
                    "; awaiting Session recovery or an explicit audio restart.");
                break; // Never retry a full queue or send later releases out of order.
            }
            midi_release_sequence_ = result.sequence;
            increment_counter(midi_release_commands_);
        }
    }

    void observe_midi_retirement(const SessionSnapshot& candidate) noexcept {
        if (!midi_retirement_waiting_) return;
        const bool applied = midi_release_sequence_ != 0 &&
            candidate.resolved_sequence >= midi_release_sequence_ &&
            candidate.last_applied_sequence >= midi_release_sequence_;
        const bool recovered = candidate.recovery_count > midi_retirement_recovery_;
        // AudioDevice::close joins the callback and calls Session::stop, which
        // clears every owner and pending command. A merely paused callback is
        // not used as an acknowledgment, nor is queue admission alone.
        const bool stopped = !audio_.is_open() && !candidate.running && candidate.prepared;
        if (applied || recovered || stopped) {
            midi_retirement_waiting_ = false;
            midi_release_failed_ = false;
        }
    }

    [[nodiscard]] bool start_pending_midi() {
        if (!pending_midi_open_ || midi_retirement_waiting_) return true;
        auto request = std::move(*pending_midi_open_);
        pending_midi_open_.reset(); // A failed open is never automatically retried.
        if (!commands_enabled_ || !audio_.is_running() || midi_shutdown_failed_ ||
            !midi_.device.is_quiescent()) {
            midi_status_ = midi_shutdown_failed_ ? "MIDI shutdown failed; restart the application." :
                "MIDI is disconnected. Start audio, then explicitly Apply MIDI settings.";
            fail(midi_status_);
            return false;
        }
        if (request.synthetic && (midi_.inbox->pending() != 0 || midi_.inbox->faults() != 0)) {
            midi_status_ = "Synthetic replay cannot open an epoch with stale inbox state.";
            increment_counter(midi_open_failures_);
            fail(midi_status_);
            return false;
        }
        if (!midi_input_.begin_epoch(request.routing)) {
            midi_status_ = "MIDI routing could not begin a fresh input epoch.";
            fail(midi_status_);
            return false;
        }
        if (request.synthetic) {
            midi_replay_.connected = true;
            midi_replay_.faulted = false;
            increment_counter(midi_replay_.connections_started);
        } else {
            std::string error;
            if (!midi_.device.open(*midi_.inbox, request.port, error)) {
                increment_counter(midi_open_failures_);
                const auto explanation = "Cannot open MIDI input: " + error;
                retire_midi(explanation);
                fail(explanation);
                return false;
            }
        }
        midi_routing_ = request.routing;
        midi_requested_port_ = std::move(request.port);
        midi_last_poll_ = SDL_GetTicks64();
        midi_startup_failed_ = false;
        midi_status_ = request.synthetic ?
            "Synthetic replay active. Messages apply at the next audio callback boundary." :
            "MIDI connected. Messages apply at the next audio callback boundary.";
        message(midi_status_);
        return true;
    }

    [[nodiscard]] bool request_midi(std::string port, const MidiRouting& routing) {
        if (midi_replay_requested()) {
            midi_status_ = "Synthetic replay is script controlled. Only a later script connect event can open input.";
            message(midi_status_);
            return true; // UI Apply cannot enumerate, alter routes, or open a native port.
        }
        if (!valid_midi_routing(routing)) {
            midi_status_ = "Choose three distinct MIDI channels from 1 through 16.";
            fail(midi_status_);
            return false; // Preserve the existing transport and routing.
        }
        if (!port.empty()) midi_native_requested_ = true;
        if (!port.empty() && (!MidiDevice::backend_available() || midi_shutdown_failed_)) {
            midi_status_ = midi_shutdown_failed_ ? "MIDI shutdown failed; restart the application." :
                "MIDI backend unavailable in this build.";
            fail(midi_status_);
            return false;
        }
        if (!port.empty() && (!commands_enabled_ || !audio_.is_running())) {
            midi_status_ = "Start audio before applying a MIDI input port.";
            fail(midi_status_);
            return false;
        }
        if (midi_input_.active() && midi_.device.is_open() && midi_.inbox->faults() == 0 &&
            port == midi_requested_port_ && routing == midi_routing_) {
            midi_status_ = "The selected MIDI port and channels are already active.";
            return true;
        }
        retire_midi("MIDI input retired. Waiting for its scoped release acknowledgment.");
        if (midi_shutdown_failed_ || midi_release_failed_) return false;
        midi_requested_port_ = port;
        midi_routing_ = routing;
        if (port.empty()) {
            midi_startup_failed_ = false;
            midi_status_ = midi_retirement_waiting_ ?
                "MIDI disconnected; waiting for scoped releases to be acknowledged." : "No MIDI input selected.";
            return true;
        }
        pending_midi_open_ = MidiRequest{std::move(port), routing};
        if (midi_retirement_waiting_) {
            midi_status_ = "Apply requested. Waiting for the previous MIDI release acknowledgment.";
            return true;
        }
        return start_pending_midi();
    }

    void request_midi_replay_connect() {
        // Every script connect requests a fresh epoch, even if already active.
        // The common retirement cancels any earlier intent and discards only
        // after the producer has stopped; no packet crosses its release barrier.
        retire_midi("Synthetic replay retired its previous epoch; waiting for scoped release acknowledgment.");
        if (midi_shutdown_failed_ || midi_release_failed_) return;
        if (!commands_enabled_ || !audio_.is_running()) {
            midi_status_ = "Synthetic replay connect requires running audio; the request was not retained.";
            increment_counter(midi_open_failures_);
            fail(midi_status_);
            return;
        }
        pending_midi_open_ = MidiRequest{{}, midi_routing_, true};
        if (midi_retirement_waiting_) {
            increment_counter(midi_replay_.connect_barriers);
            midi_status_ = "Synthetic replay connect is waiting for the previous scoped release acknowledgment.";
            return;
        }
        const bool opened = start_pending_midi();
        (void)opened; // Failure is visible and the consumed request is never retried.
    }

    void feed_midi_replay_bytes(const MidiReplayEvent& event) {
        if (!midi_replay_.connected || !midi_input_.active()) {
            increment_counter(midi_replay_.ignored_while_closed);
            return;
        }
        // This is synthetic receipt metadata sampled on the main thread. Script
        // due times and steady nanoseconds are never Engine frames/deadlines.
        const auto receipt = std::chrono::duration_cast<std::chrono::nanoseconds>(
            std::chrono::steady_clock::now().time_since_epoch()).count();
        midi_replay_.last_arrival_ns = receipt > 0 ? static_cast<std::uint64_t>(receipt) : 0;
        increment_counter(midi_replay_.offered_packets);
        const auto pushed = midi_.inbox->push(
            std::span<const std::uint8_t>{event.bytes.data(), event.size}, midi_replay_.last_arrival_ns);
        if (pushed == MidiPushResult::Accepted) {
            increment_counter(midi_replay_.accepted_packets);
            return;
        }
        increment_counter(midi_replay_.rejected_packets);
        if (pushed == MidiPushResult::Overflow) {
            increment_counter(midi_replay_.intentional_overflow_faults);
            midi_fault("Synthetic replay overflowed the real inbox; old packets discarded. A later connect event is required.", true);
        } else if (pushed == MidiPushResult::Faulted) {
            midi_fault("Synthetic replay reached a faulted inbox; old packets discarded. A later connect event is required.", true);
        } else {
            // The admitted fixed plan cannot contain an invalid-size packet.
            midi_fault("Synthetic replay produced an invalid packet size after admission.");
        }
    }

    void deliver_midi_replay_event(const MidiReplayEvent& event) {
        switch (event.kind) {
        case MidiReplayKind::Bytes:
            feed_midi_replay_bytes(event);
            break;
        case MidiReplayKind::Connect:
            increment_counter(midi_replay_.connect_events);
            request_midi_replay_connect();
            break;
        case MidiReplayKind::Disconnect:
            increment_counter(midi_replay_.disconnect_events);
            if (midi_replay_.connected) midi_.inbox->signal_fault(MidiInboxFault::Disconnected);
            retire_midi("Synthetic replay disconnected; MIDI owners are being released.");
            midi_status_ = "Synthetic replay is disconnected. Only a later script connect event can open input.";
            break;
        case MidiReplayKind::BackendFault:
            increment_counter(midi_replay_.intentional_backend_faults);
            if (midi_replay_.connected) {
                midi_.inbox->signal_fault(MidiInboxFault::Backend);
                midi_fault("Synthetic replay injected a backend fault; old packets discarded. A later connect event is required.", true);
            } else {
                increment_counter(midi_replay_.faults_while_closed);
                retire_midi("Synthetic replay cancelled pending input after a scripted backend fault.");
                midi_replay_.faulted = true;
                midi_status_ = "Synthetic replay counted a backend fault while disconnected; input remains closed.";
            }
            break;
        }
    }

    void pump_midi_replay(std::uint64_t elapsed) {
        if (!midi_replay_requested()) return;
        if (pending_midi_open_ && !midi_retirement_waiting_) {
            const bool opened = start_pending_midi();
            (void)opened;
        }
        std::size_t delivered = 0;
        while (midi_replay_.cursor < midi_replay_.plan.event_count && delivered < kMidiReplayEventBudget) {
            const auto& event = midi_replay_.plan.events[midi_replay_.cursor];
            if (event.at_ms > elapsed) break;
            if (pending_midi_open_) {
                // Preserve FIFO ties across the pending open. UI Panic, audio
                // restart, or Session recovery may cancel this intent first.
                increment_counter(midi_replay_.barrier_wait_turns);
                break;
            }
            ++midi_replay_.cursor;
            ++delivered;
            deliver_midi_replay_event(event);
        }
        midi_replay_.maximum_events_per_turn = std::max(midi_replay_.maximum_events_per_turn, delivered);
        if (delivered == kMidiReplayEventBudget && midi_replay_.cursor < midi_replay_.plan.event_count &&
            midi_replay_.plan.events[midi_replay_.cursor].at_ms <= elapsed) {
            increment_counter(midi_replay_.budget_exhaustions);
        }
    }

    void midi_fault(std::string explanation, bool synthetic_injection = false) {
        increment_counter(midi_fault_retirements_);
        if (!midi_replay_requested() && midi_.inbox->faults() != 0 && midi_.device.is_open()) {
            std::string error;
            const bool connected = midi_.device.poll_connection(error);
            (void)connected;
        }
        retire_midi(explanation);
        if (midi_replay_requested()) midi_replay_.faulted = true;
        if (!midi_shutdown_failed_) {
            midi_status_ = std::move(explanation);
            if (synthetic_injection && midi_replay_requested()) message(midi_status_);
            else fail(midi_status_);
        }
    }

    void process_midi() {
        if (pending_midi_open_ && !midi_retirement_waiting_) {
            const bool opened = start_pending_midi();
            (void)opened;
        }
        if (!midi_input_.active()) return;
        if (!commands_enabled_ || !audio_.is_running()) {
            retire_midi("MIDI disconnected after audio stopped. Apply MIDI settings to reconnect.");
            return;
        }
        const auto now = SDL_GetTicks64();
        if (midi_replay_requested()) {
            if (!midi_replay_.connected || midi_.inbox->faults() != 0) {
                midi_fault("Synthetic replay inbox fault; old packets discarded. A later connect event is required.", true);
                return;
            }
        } else if (midi_.inbox->faults() != 0 || !midi_.device.is_open() ||
            now - midi_last_poll_ >= kMidiConnectionPollMilliseconds) {
            midi_last_poll_ = now;
            std::string error;
            const bool connected = midi_.device.poll_connection(error);
            if (!connected || midi_.inbox->faults() != 0) {
                midi_fault(error.empty() ?
                    "MIDI input fault; old packets discarded. Apply MIDI settings to reconnect." :
                    "MIDI input disconnected: " + error + ". Apply MIDI settings to reconnect.");
                return;
            }
        }
        std::size_t drained = 0;
        for (; drained < kMidiDrainBudget && midi_input_.active();) {
            if (midi_.inbox->faults() != 0) {
                midi_fault("MIDI inbox fault; old packets discarded. Apply MIDI settings to reconnect.");
                break;
            }
            MidiPacket packet;
            if (!midi_.inbox->pop(packet)) break;
            ++drained;
            const auto decoded = midi_input_.decode(packet);
            if (decoded.status != MidiDecodeStatus::Action) continue;
            bool accepted = false;
            if (const auto* command = std::get_if<SessionCommand>(&decoded.action)) {
                const auto result = post_midi_command(*command);
                accepted = result.ok();
                if (!accepted) {
                    midi_fault(std::string("MIDI command rejected: ") + status_name(result.status) +
                        ". Input retired; reconnect explicitly after recovery.");
                }
            } else {
                const auto& edit = std::get<MidiParameterEdit>(decoded.action);
                increment_counter(midi_parameter_messages_);
                accepted = dispatch(ui_.external_parameter(edit.parameter_id, edit.normalized));
                if (!accepted && midi_input_.active()) {
                    midi_fault("MIDI control submission failed. Apply MIDI settings after recovery.");
                }
            }
            if (!accepted) break;
            // Observe recovery between accepted actions too. A UI or Engine
            // failure can retire this epoch while acquisition is still active.
            observe();
        }
        midi_maximum_drain_ = std::max(midi_maximum_drain_, drained);
        if (midi_input_.active() && midi_.inbox->faults() != 0) {
            midi_fault("MIDI inbox fault; old packets discarded. Apply MIDI settings to reconnect.");
        }
    }

    void copy_midi_diagnostics() {
        midi_final_info_ = midi_.device.info();
        midi_final_device_ = midi_.device.diagnostics();
        midi_final_inbox_ = midi_.inbox->diagnostics();
        midi_final_input_ = midi_input_.diagnostics();
        midi_final_quiescent_ = midi_.device.is_quiescent();
        midi_final_pending_ = midi_.inbox->pending();
    }

    void choose_state_path() {
        if (!options_.state.empty()) return;
        char* preference = SDL_GetPrefPath("B3Workshop", "HammondStandalone");
        if (preference == nullptr) { fail(std::string("Cannot choose state directory: ") + SDL_GetError()); return; }
        const std::unique_ptr<char, decltype(&SDL_free)> owned(preference, &SDL_free);
        options_.state = cli::argument_path(preference) / "controls.b3controls";
    }

    [[nodiscard]] bool output_paths_distinct() {
        const std::array<std::filesystem::path, 5> paths{
            options_.state, options_.screenshot, options_.diagnostics, options_.input_script, options_.midi_script};
        std::array<bool, paths.size()> present{};
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
                fail("State, screenshot, diagnostics, and replay script paths must not be symbolic links"); return false;
            }
            present[index] = std::filesystem::exists(status);
            if (index != 0 && std::filesystem::exists(status) && !std::filesystem::is_regular_file(status)) {
                fail("Screenshot, diagnostics, and replay script paths must be regular files or new paths"); return false;
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
                // Equivalent compares existing file identities. libc++ can
                // report operation_not_supported for two absent output leaves;
                // their resolved path equality above already detects aliases.
                const bool same = a == b || (present[first] && present[second] &&
                                             std::filesystem::equivalent(a, b, error));
                if (same) { fail("State, screenshot, diagnostics, and replay scripts must use different files"); return false; }
                if (error && error != std::errc::no_such_file_or_directory) {
                    fail("Cannot compare selected file identities: " + error.message()); return false;
                }
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
        const bool recovered = snapshot_available_ && candidate.recovery_count > snapshot_.recovery_count;
        snapshot_ = candidate;
        snapshot_available_ = true;
        retained_controls_ = candidate.controls;
        ui_.observe(candidate);
        if (recovered && (midi_input_.active() || pending_midi_open_ || midi_retirement_waiting_)) {
            increment_counter(midi_session_recoveries_);
            retire_midi("MIDI disconnected after global Session recovery. Apply MIDI settings to reconnect.");
        }
        observe_midi_retirement(candidate);
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
                if (std::holds_alternative<Panic>(*command)) {
                    retire_midi("MIDI disconnected by global Panic. Apply MIDI settings to reconnect.");
                }
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
                if (midi_input_.active() || pending_midi_open_) {
                    retire_midi("MIDI disconnected after Session submission failure. Apply MIDI settings after recovery.");
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
        case UiAppRequest::MidiSettings: open_overlay(ViewOverlay::Midi); break;
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
        if (overlay == ViewOverlay::Midi) {
            selected_midi_routing_ = midi_routing_;
            midi_choices_.clear();
            if (midi_replay_requested()) {
                midi_choices_.emplace_back("Synthetic replay (script controlled)");
                selected_midi_port_ = 0;
                midi_status_ = "Synthetic replay: Apply leaves the script route unchanged; Disconnect retires MIDI owners.";
                message("Synthetic replay uses explicit script connect events. Native MIDI ports are not enumerated.");
                return;
            }
            midi_choices_.emplace_back("No input");
            std::vector<std::string> names;
            std::string error;
            if (midi_shutdown_failed_) {
                midi_status_ = "MIDI shutdown failed; restart the application before using MIDI.";
            } else if (MidiDevice::backend_available()) {
                if (MidiDevice::enumerate_input_ports(names, error)) {
                    for (auto& name : names) midi_choices_.push_back(std::move(name));
                    if (names.empty() && !midi_input_.active()) midi_status_ = "No MIDI input ports were found.";
                } else {
                    midi_status_ = "Cannot enumerate MIDI input ports: " + error;
                    fail(midi_status_);
                }
            } else midi_status_ = "MIDI backend unavailable in this build.";
            selected_midi_port_ = 0;
            if (!midi_requested_port_.empty()) {
                const auto found = std::find(midi_choices_.begin() + 1, midi_choices_.end(), midi_requested_port_);
                if (found != midi_choices_.end()) {
                    selected_midi_port_ = static_cast<std::size_t>(found - midi_choices_.begin());
                }
            }
            message("MIDI: choose an exact port and distinct channels; Apply connects; Disconnect releases MIDI notes.");
            return;
        }
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

    [[nodiscard]] std::size_t modal_control_count() const noexcept {
        return overlay_ == ViewOverlay::Midi ? 8U : 6U;
    }

    [[nodiscard]] std::array<UiRect, 8> modal_rectangles() const noexcept {
        if (overlay_ == ViewOverlay::Midi) {
            const auto boxes = midi_overlay_layout(ui_.layout().width, ui_.layout().height);
            return {boxes.previous_port, boxes.next_port, boxes.upper_channel,
                    boxes.lower_channel, boxes.pedal_channel, boxes.apply, boxes.disconnect, boxes.close};
        }
        const auto boxes = audio_overlay_layout(ui_.layout().width, ui_.layout().height);
        return {boxes.previous_device, boxes.next_device, boxes.sample_rate,
                boxes.buffer_frames, boxes.apply, boxes.close, {}, {}};
    }

    [[nodiscard]] std::uint8_t* selected_midi_channel() noexcept {
        if (modal_focus_ == 2) return &selected_midi_routing_.upper_channel;
        if (modal_focus_ == 3) return &selected_midi_routing_.lower_channel;
        if (modal_focus_ == 4) return &selected_midi_routing_.pedal_channel;
        return nullptr;
    }

    void change_modal_value(int direction) {
        if (overlay_ == ViewOverlay::Midi) {
            if (modal_focus_ <= 1 && !midi_choices_.empty()) {
                selected_midi_port_ = direction < 0 ?
                    (selected_midi_port_ + midi_choices_.size() - 1) % midi_choices_.size() :
                    (selected_midi_port_ + 1) % midi_choices_.size();
            } else if (auto* channel = selected_midi_channel()) {
                *channel = static_cast<std::uint8_t>(direction < 0 ? (*channel == 1 ? 16 : *channel - 1) :
                    (*channel == 16 ? 1 : *channel + 1));
            }
            return;
        }
        if (modal_focus_ <= 1 && !audio_choices_.empty()) {
            selected_device_ = direction < 0 ? (selected_device_ + audio_choices_.size() - 1) % audio_choices_.size() :
                (selected_device_ + 1) % audio_choices_.size();
        } else if (modal_focus_ == 2) cycle_value(selected_config_.sample_rate, kSampleRates, direction);
        else if (modal_focus_ == 3) cycle_value(selected_config_.buffer_frames, kBufferSizes, direction);
    }

    void activate_modal() {
        if (overlay_ == ViewOverlay::Midi) {
            if (modal_focus_ == 7) { close_overlay(); return; }
            if (modal_focus_ < 5) { change_modal_value(modal_focus_ == 0 ? -1 : 1); return; }
            if (modal_focus_ == 6) {
                retire_midi("MIDI disconnected by request. MIDI owners are being released.");
                midi_requested_port_.clear();
                selected_midi_port_ = 0;
                if (!midi_shutdown_failed_) {
                    if (midi_replay_requested()) {
                        midi_status_ = "Synthetic replay disconnected. Only a later script connect event can open input.";
                    } else {
                        midi_status_ = midi_retirement_waiting_ ?
                            "MIDI disconnected; waiting for scoped release acknowledgment." : "No MIDI input selected.";
                    }
                }
                return;
            }
            if (selected_midi_port_ >= midi_choices_.size()) return;
            std::string port = selected_midi_port_ == 0 ? std::string{} : midi_choices_[selected_midi_port_];
            if (!port.empty() && std::count(midi_choices_.begin() + 1, midi_choices_.end(), port) != 1) {
                midi_status_ = "The selected MIDI name is ambiguous. Reopen MIDI settings after resolving duplicate names.";
                fail(midi_status_);
                return;
            }
            const bool requested = request_midi(std::move(port), selected_midi_routing_);
            (void)requested;
            return; // Keep the selected configuration and connection result reviewable.
        }
        if (overlay_ == ViewOverlay::Help || modal_focus_ == 5) { close_overlay(); return; }
        if (modal_focus_ < 4) { change_modal_value(modal_focus_ == 0 ? -1 : 1); return; }
        pending_save_.reset();
        lose_input(UiReleaseReason::FocusLost);
        retire_midi("MIDI disconnected for audio restart. Apply MIDI settings to reconnect.");
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
            const auto count = modal_control_count();
            modal_focus_ = input.shift ? (modal_focus_ + count - 1) % count : (modal_focus_ + 1) % count;
        } else if (input.key == UiKey::Enter || input.key == UiKey::Space) activate_modal();
        else if (input.key == UiKey::Left || input.key == UiKey::Down) change_modal_value(-1);
        else if (input.key == UiKey::Right || input.key == UiKey::Up) change_modal_value(1);
        else if (input.key == UiKey::Home || input.key == UiKey::End) {
            const bool end = input.key == UiKey::End;
            if (overlay_ == ViewOverlay::Midi) {
                if (modal_focus_ <= 1 && !midi_choices_.empty()) {
                    selected_midi_port_ = end ? midi_choices_.size() - 1 : 0;
                } else if (auto* channel = selected_midi_channel()) *channel = end ? 16 : 1;
                return;
            }
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
            else if (event.keysym.scancode == SDL_SCANCODE_M) open_overlay(ViewOverlay::Midi);
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
                for (std::size_t index = first; index < modal_control_count(); ++index) {
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
            retire_midi("MIDI disconnected after audio-device removal. Apply MIDI settings after restarting audio.");
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
        retire_midi("MIDI disconnected after audio failure. Apply MIDI settings after restarting audio.");
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
        const auto midi_device = midi_.device.info();
        const std::string replay_status = midi_replay_requested() ? "Synthetic replay: " + midi_status_ : std::string{};
        InstrumentViewInfo information{device.running, device.sample_rate, device.buffer_frames,
            device.driver, device.device_name, status_, diagnostics.overrange_samples, overlay_, audio_choices_,
            selected_device_, selected_config_.sample_rate, selected_config_.buffer_frames};
        information.midi_available = midi_replay_requested() || MidiDevice::backend_available();
        information.midi_open = !midi_replay_requested() && midi_.device.is_open() && midi_input_.active();
        information.midi_backend = midi_replay_requested() ? "Synthetic replay" : MidiDevice::backend_name();
        information.midi_port = midi_replay_requested() ?
            (midi_replay_.connected ? "Synthetic replay (active)" : "Synthetic replay (disconnected)") :
            std::string_view{midi_device.port_name};
        information.midi_status = midi_replay_requested() ? replay_status : midi_status_;
        information.midi_choices = midi_choices_;
        information.selected_midi_port = selected_midi_port_;
        information.selected_midi_channels = {selected_midi_routing_.upper_channel,
            selected_midi_routing_.lower_channel, selected_midi_routing_.pedal_channel};
        information.midi_messages = midi_input_.diagnostics().packets;
        paint_instrument(*drawing_, ui_, information);
        if (overlay_ != ViewOverlay::None) drawing_->outline(modal_rectangles()[modal_focus_], kUiFocusCyan, 2.0F);
        if (SDL_RenderFlush(renderer_.get()) != 0) {
            fail(std::string("Cannot render instrument: ") + SDL_GetError()); return false;
        }
        ++render_count_;
        // Keys were painted from this main-thread copy. A queued key-up does
        // not change that frame, even if the callback has since applied it.
        const auto& painted = ui_.view().applied;
        constexpr std::size_t middle_c_index = 60 - kMinManualMidiNote;
        const bool smoke_capture = smoke_held_observed_ && painted.held_keys[0][middle_c_index];
        const bool last_chance = options_.smoke_ms != 0 && elapsed >= options_.smoke_ms;
        const bool replay_capture = replay_requested() &&
            (options_.input_script.empty() || replay_completed_) &&
            (!midi_replay_requested() || midi_replay_.completed);
        if (!options_.screenshot.empty() && !screenshot_attempted_ &&
            (replay_capture || (!replay_requested() &&
                (options_.smoke_ms == 0 || smoke_capture || last_chance)))) {
            screenshot_attempted_ = true;
            std::string error;
            // The backbuffer is defined here; RenderPresent invalidates it.
            screenshot_written_ = drawing_->save_bmp(cli::path_text(options_.screenshot), error);
            screenshot_while_held_ = screenshot_written_ && (smoke_capture || (replay_capture && any_held(painted)));
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
    MidiLifetime midi_; // The sole inbox outlives its backend, including quarantine.
    MidiInput midi_input_;
    MidiReplayState midi_replay_;
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
    ControlSnapshot replay_desired_controls_{};
    bool replay_snapshot_available_{false};
    bool replay_controls_pending_{false};
    bool replay_save_pending_{false};
    std::optional<PendingSave> pending_save_;
    std::optional<MidiRequest> pending_midi_open_;
    AudioDeviceInfo audio_before_close_{};
    AudioDeviceDiagnostics final_diagnostics_{};
    MidiDeviceInfo midi_before_shutdown_{};
    MidiDeviceInfo midi_final_info_{};
    MidiDeviceDiagnostics midi_final_device_{};
    MidiInboxDiagnostics midi_final_inbox_{};
    MidiInputDiagnostics midi_final_input_{};
    MidiRouting midi_routing_{};
    MidiRouting selected_midi_routing_{};
    std::vector<std::string> audio_choices_;
    std::vector<std::string> midi_choices_;
    std::string midi_requested_port_;
    std::string midi_status_{"No MIDI input selected."};
    std::string status_;
    std::string last_error_;
    std::string renderer_name_;
    std::string video_driver_;
    ViewOverlay overlay_{ViewOverlay::None};
    std::size_t selected_device_{0};
    std::size_t selected_midi_port_{0};
    std::size_t midi_maximum_drain_{0};
    std::size_t midi_final_pending_{0};
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
    std::uint64_t midi_last_poll_{0};
    std::uint64_t midi_retirements_{0};
    std::uint64_t midi_fault_retirements_{0};
    std::uint64_t midi_session_recoveries_{0};
    std::uint64_t midi_open_failures_{0};
    std::uint64_t midi_submit_failures_{0};
    std::uint64_t midi_release_batches_{0};
    std::uint64_t midi_release_commands_{0};
    std::uint64_t midi_release_sequence_{0};
    std::uint64_t midi_retirement_recovery_{0};
    std::uint64_t midi_parameter_messages_{0};
    std::uint32_t midi_retired_faults_{0};
    SessionStatus midi_last_submit_status_{SessionStatus::Ok};
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
    bool midi_retirement_waiting_{false};
    bool midi_release_failed_{false};
    bool midi_shutdown_failed_{false};
    bool midi_startup_failed_{false};
    bool midi_active_before_shutdown_{false};
    bool midi_final_quiescent_{true};
    bool midi_native_requested_{false};
};

int run_application(int argc, char** argv) {
    Options options;
    std::string error;
    if (!parse_options(argc, argv, options, error)) {
        std::cerr << "hammond_standalone: " << error << '\n';
        return 2;
    }
    if (options.help) { print_help(); return 0; }
    if (options.list_midi) {
        std::cout << "MIDI backend: " << MidiDevice::backend_name() << '\n';
        std::vector<std::string> names;
        if (!MidiDevice::enumerate_input_ports(names, error)) {
            std::cerr << "hammond_standalone: " << error << '\n';
            return 1;
        }
        std::cout << "Default input: none; select an exact name with --midi-port or MIDI settings\n";
        if (names.empty()) std::cout << "No MIDI input ports found.\n";
        for (std::size_t index = 0; index < names.size(); ++index) {
            std::cout << index + 1 << ": " << names[index] << '\n';
        }
        return 0;
    }
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
