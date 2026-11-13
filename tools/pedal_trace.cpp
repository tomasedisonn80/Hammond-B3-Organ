#include "hammond/Engine.h"

#include <array>
#include <charconv>
#include <chrono>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <exception>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <locale>
#include <span>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>
#include <utility>

namespace {
namespace fs = std::filesystem;
using hammond::Event;
using hammond::EventType;
using hammond::Manual;

constexpr std::uint32_t kDurationMilliseconds = 120;
constexpr std::uint32_t kMaxRows = 11520;
constexpr std::size_t kMaxTraceBytes = 8 * 1024 * 1024;
constexpr std::uint8_t kManualNote = 48;
constexpr std::size_t kManualDrawbar = 2;
constexpr hammond::ToneId kTrackedTone = 25;

[[noreturn]] void fail(const std::string& message) {
    throw std::runtime_error(message);
}

struct Options {
    fs::path profile;
    fs::path output;
    std::string_view scenario;
    std::uint32_t sample_rate{0};
    std::uint64_t seed{0};
};

[[nodiscard]] std::uint64_t unsigned_number(std::string_view text) {
    if (text.empty() || text.size() > 20) {
        fail("Numeric arguments require 1..20 unsigned decimal digits.");
    }
    for (const char character : text) {
        if (character < '0' || character > '9') {
            fail("Numeric arguments require unsigned decimal digits.");
        }
    }
    std::uint64_t result = 0;
    const auto parsed = std::from_chars(text.data(), text.data() + text.size(), result);
    if (parsed.ec != std::errc{} || parsed.ptr != text.data() + text.size()) {
        fail("Numeric argument exceeds uint64 range.");
    }
    return result;
}

[[nodiscard]] Options parse_options(int argc, char** argv) {
    constexpr std::array<std::string_view, 5> names{
        "--profile", "--scenario", "--sample-rate", "--seed", "--output"};
    std::array<bool, names.size()> seen{};
    Options options;
    for (int argument = 1; argument < argc; ++argument) {
        const std::string_view name(argv[argument]);
        std::size_t index = 0;
        while (index < names.size() && names[index] != name) ++index;
        if (index == names.size()) fail("Unknown argument: " + std::string(name));
        if (seen[index]) fail("Duplicate argument: " + std::string(name));
        seen[index] = true;
        if (argument + 1 >= argc) fail("Missing value for " + std::string(name));
        const std::string_view value(argv[++argument]);
        if (value.empty() || value.size() > 4096) {
            fail("Argument values require 1..4096 bytes.");
        }
        switch (index) {
        case 0: options.profile = fs::path(value); break;
        case 1:
            if (value != "unmute" && value != "overlap" && value != "routing") {
                fail("Scenario must be unmute, overlap or routing.");
            }
            options.scenario = value;
            break;
        case 2: {
            const auto rate = unsigned_number(value);
            if (rate != 44100 && rate != 48000 && rate != 96000) {
                fail("Sample rate must be 44100, 48000 or 96000.");
            }
            options.sample_rate = static_cast<std::uint32_t>(rate);
            break;
        }
        case 3: options.seed = unsigned_number(value); break;
        case 4: options.output = fs::path(value); break;
        default: fail("Internal option index.");
        }
    }
    for (std::size_t index = 0; index < seen.size(); ++index) {
        if (!seen[index]) fail("Required argument: " + std::string(names[index]));
    }
    return options;
}

void validate_paths(Options& options) {
    std::error_code error;
    options.profile = fs::canonical(options.profile, error);
    if (error || !fs::is_regular_file(options.profile, error) || error) {
        fail("Profile must be an existing regular file.");
    }
    const auto output = fs::weakly_canonical(options.output, error);
    if (error) fail("Cannot resolve output path: " + error.message());
    if (output == options.profile) fail("Output path collides with the input profile.");
    const auto status = fs::symlink_status(options.output, error);
    if (error && error != std::errc::no_such_file_or_directory) {
        fail("Cannot inspect output path: " + error.message());
    }
    if (fs::exists(status) || fs::is_symlink(status)) {
        fail("Output already exists; existing files are never overwritten.");
    }
    error.clear();
    const auto parent = fs::canonical(output.parent_path().empty() ? fs::path(".") :
                                     output.parent_path(), error);
    if (error || !fs::is_directory(parent, error) || error || output.filename().empty()) {
        fail("Output parent must be an existing directory.");
    }
    options.output = parent / output.filename();
}

struct ScheduledEvent {
    std::uint32_t milliseconds;
    EventType type;
    Manual manual;
    std::uint8_t index;
    double value;
};

[[nodiscard]] std::span<const ScheduledEvent> scenario_events(std::string_view name) {
    static constexpr std::array unmute{
        ScheduledEvent{0, EventType::PedalOn, Manual::Lower, 8, 100.0},
        ScheduledEvent{0, EventType::PedalOn, Manual::Lower, 12, 100.0},
        ScheduledEvent{20, EventType::PedalDrawbar, Manual::Lower, 0, 8.0},
        ScheduledEvent{40, EventType::PedalDrawbar, Manual::Lower, 1, 4.0},
        ScheduledEvent{60, EventType::PedalDrawbar, Manual::Lower, 0, 0.0},
        ScheduledEvent{72, EventType::PedalDrawbar, Manual::Lower, 1, 0.0},
        ScheduledEvent{80, EventType::PedalDrawbar, Manual::Lower, 1, 8.0},
        ScheduledEvent{96, EventType::PedalOff, Manual::Lower, 8, 0.0},
        ScheduledEvent{104, EventType::PedalOff, Manual::Lower, 12, 0.0},
        ScheduledEvent{112, EventType::PedalAllNotesOff, Manual::Lower, 0, 0.0}};
    static constexpr std::array overlap{
        ScheduledEvent{0, EventType::PedalOn, Manual::Lower, 1, 100.0},
        ScheduledEvent{16, EventType::NoteOn, Manual::Upper, kManualNote, 100.0},
        ScheduledEvent{32, EventType::PedalOn, Manual::Lower, 25, 100.0},
        ScheduledEvent{48, EventType::NoteOn, Manual::Lower, kManualNote, 100.0},
        ScheduledEvent{64, EventType::PedalOff, Manual::Lower, 1, 0.0},
        ScheduledEvent{80, EventType::NoteOff, Manual::Upper, kManualNote, 0.0},
        ScheduledEvent{96, EventType::PedalOff, Manual::Lower, 25, 0.0},
        ScheduledEvent{112, EventType::NoteOff, Manual::Lower, kManualNote, 0.0}};
    static constexpr auto routing = []() constexpr {
        std::array<ScheduledEvent, hammond::kPedalCount + 7> events{};
        for (std::size_t pedal = 0; pedal < hammond::kPedalCount; ++pedal) {
            events[pedal] = {0, EventType::PedalOn, Manual::Lower,
                             static_cast<std::uint8_t>(pedal + 1), 100.0};
        }
        const auto first = hammond::kPedalCount;
        events[first] = {0, EventType::NoteOn, Manual::Upper, kManualNote, 100.0};
        events[first + 1] = {0, EventType::NoteOn, Manual::Lower, kManualNote, 100.0};
        events[first + 2] = {20, EventType::Cancel, Manual::Lower, 0, 0.0};
        events[first + 3] = {40, EventType::SelectBank, Manual::Lower, 0, 1.0};
        events[first + 4] = {60, EventType::AllNotesOff, Manual::Lower, 0, 0.0};
        events[first + 5] = {80, EventType::PedalAllNotesOff, Manual::Lower, 0, 0.0};
        events[first + 6] = {100, EventType::AllNotesOff, Manual::Upper, 0, 0.0};
        return events;
    }();
    if (name == "unmute") return unmute;
    if (name == "overlap") return overlap;
    if (name == "routing") return routing;
    fail("Internal scenario selection.");
}

[[nodiscard]] std::uint32_t frame_at(std::uint32_t milliseconds, std::uint32_t rate) {
    return rate * milliseconds / 1000;
}

void flush(hammond::Engine& engine, std::span<const Event> events) {
    const auto result = engine.process(0, {}, events);
    if (!result.ok() || result.events_consumed != events.size()) {
        fail("Engine rejected trace controls: " + std::string(hammond::status_name(result.status)));
    }
}

void append_bounded(std::string& destination, const std::string& text) {
    if (text.size() > kMaxTraceBytes - destination.size()) fail("Trace exceeds 8 MiB.");
    destination.append(text);
}

[[nodiscard]] std::string trace(const Options& options, const hammond::RuntimeProfile& profile) {
    const auto frames = frame_at(kDurationMilliseconds, options.sample_rate);
    if (frames == 0 || frames > kMaxRows) fail("Trace exceeds its fixed row bound.");
    // This fixed comparison must actually share tone 25 with pedal 25's first
    // contact and pedal 1's fourth. A different manual map needs another scenario.
    if (profile.manual_map[kManualNote - hammond::kMinManualMidiNote][kManualDrawbar] !=
        kTrackedTone) {
        fail("Trace requires manual MIDI 48 drawbar 2 to select source 25.");
    }
    hammond::Engine engine;
    const hammond::ProcessSpec spec{static_cast<double>(options.sample_rate), 1, options.seed, 0};
    const auto prepared = engine.prepare(profile, spec, hammond::make_legacy_console_model());
    if (prepared != hammond::Status::Ok) {
        fail("Engine preparation failed: " + std::string(hammond::status_name(prepared)));
    }
    const double first_position = options.scenario == "unmute" ? 0.0 :
                                  options.scenario == "overlap" ? 6.0 : 4.0;
    const double second_position = options.scenario == "unmute" ? 0.0 : 2.0;
    const std::array initial{
        Event{0, EventType::Drawbar, Manual::Upper, static_cast<std::uint8_t>(kManualDrawbar), 8.0},
        Event{0, EventType::Drawbar, Manual::Lower, static_cast<std::uint8_t>(kManualDrawbar), 4.0},
        Event{0, EventType::PedalDrawbar, Manual::Lower, 0, first_position},
        Event{0, EventType::PedalDrawbar, Manual::Lower, 1, second_position}};
    flush(engine, initial);
    const auto identity = hammond::compiled_pedal_identity();
    const auto& tracked = profile.sources[static_cast<std::size_t>(kTrackedTone - 1)];
    std::ostringstream row;
    row.imbue(std::locale::classic());
    row << std::setprecision(std::numeric_limits<double>::max_digits10);
    row << "# hammond_pedal_trace_schema=1\n"
           "# evidence_scope=synthetic_engineering\n"
           "# source_model=ideal-shared-sine-v1\n"
           "# manual_contact_model=ideal-contacts-v1\n"
           "# pedal_contact_model=ideal-eight-contact-pedal-v1\n"
        << "# pedal_routing_model=" << identity.model_id << '\n'
        << "# pedal_voice_model=" << hammond::kNominalPedalVoiceModelId << '\n'
        << "# pedal_gain_law=" << hammond::kNominalPedalGainLawId << '\n'
        << "# pedal_map_id=" << identity.map_id << '\n'
        << "# pedal_map_raw_sha256=" << identity.map_raw_sha256 << '\n'
        << "# pedal_map_canonical_sha256=" << identity.map_canonical_sha256 << '\n'
        << "# pedal_reference_a_sha256=" << identity.review_a_sha256 << '\n'
        << "# pedal_reference_b_sha256=" << identity.review_b_sha256 << '\n'
        << "# mixture_matrix=";
    for (std::size_t mixture = 0; mixture < hammond::kPedalDrawbarCount; ++mixture) {
        if (mixture != 0) row << ';';
        for (std::size_t bus = 0; bus < hammond::kPedalBusCount; ++bus) {
            if (bus != 0) row << ',';
            row << hammond::kNominalPedalMixtureMatrix[mixture][bus];
        }
    }
    row << "\n# pedal_position_gains=";
    for (std::size_t position = 0; position < hammond::kNominalPedalPositionGains.size(); ++position) {
        if (position != 0) row << ',';
        row << hammond::kNominalPedalPositionGains[position];
    }
    row << "\n# pedal_weight_policy=all-200-unit-positive-v1\n"
           "# signal_units=dimensionless_source_normalized\n"
        << "# scenario=" << options.scenario << '\n'
        << "# scenario_version=1\n"
           "# profile_id=" << profile.profile_id.data() << '\n'
        << "# authoring_sha256=" << profile.authoring_sha256.data() << '\n'
        << "# profile_digest_scope=declared_authoring_not_compiled_hash\n"
           "# sample_rate=" << options.sample_rate << '\n'
        << "# seed=" << options.seed << '\n'
        << "# frames=" << frames << '\n'
        << "# timing=events_then_pre_render_state_then_one_render_then_historical_record\n"
           "# contact_bits_order=pedal_1_to_25_each_contact_0_to_7\n"
           "# pedal_targets_order=pedal_1_to_25\n"
           "# manual_midi=" << static_cast<unsigned>(kManualNote) << '\n'
        << "# manual_drawbar_index=" << kManualDrawbar << '\n'
        << "# tracked_tone_id=" << static_cast<unsigned>(kTrackedTone) << '\n'
        << "# tracked_frequency_hz=" << tracked.frequency_hz << '\n'
        << "# tracked_source_peak=" << tracked.peak_amplitude << '\n'
        << "# profile_output_gain=" << profile.output_gain << '\n'
        << "# percussion=off\n"
           "# row_count_limit=" << kMaxRows << '\n'
        << "# byte_limit=" << kMaxTraceBytes << '\n'
        << "frame,sample_rate,time_seconds,pedal_position_0,pedal_position_1,"
           "brown,red,orange,yellow,mixture_0,mixture_1,pedal_output,audio,expression,"
           "active_pedals,pedal_targets,contact_bits,upper_down,lower_down,"
           "upper_route,lower_route,upper_bank,lower_bank,upper_drawbar,lower_drawbar,"
           "source_phase_before,clock_after\n";
    std::string output;
    output.reserve(static_cast<std::size_t>(frames) * 640);
    append_bounded(output, row.str());
    const auto events = scenario_events(options.scenario);
    std::size_t event_index = 0;
    for (std::uint32_t frame = 0; frame < frames; ++frame) {
        while (event_index < events.size() &&
               frame_at(events[event_index].milliseconds, options.sample_rate) == frame) {
            const auto& scheduled = events[event_index++];
            const std::array event{Event{0, scheduled.type, scheduled.manual,
                                         scheduled.index, scheduled.value}};
            flush(engine, event);
        }
        hammond::PedalContactStates contacts{};
        double phase_before = 0.0;
        std::uint8_t upper_drawbar = 0;
        std::uint8_t lower_drawbar = 0;
        if (engine.frame_clock() != frame ||
            !engine.pedal_contacts_snapshot(contacts) ||
            !engine.source_phase_turns(kTrackedTone, phase_before) ||
            !engine.drawbar_position(Manual::Upper, kManualDrawbar, upper_drawbar) ||
            !engine.drawbar_position(Manual::Lower, kManualDrawbar, lower_drawbar)) {
            fail("Trace diagnostic failed.");
        }
        const auto controls = engine.controls_snapshot();
        const auto active = engine.active_pedal_count();
        std::array<bool, hammond::kPedalCount> targets{};
        for (std::size_t pedal = 0; pedal < targets.size(); ++pedal) {
            targets[pedal] = engine.pedal_down({static_cast<std::uint8_t>(pedal + 1)});
        }
        const auto upper_down = engine.key_down(Manual::Upper, kManualNote);
        const auto lower_down = engine.key_down(Manual::Lower, kManualNote);
        std::array<float, 1> sample{};
        const auto rendered = engine.process(1, sample, {});
        const auto pedal = engine.last_pedal_frame();
        if (!rendered.ok() || rendered.events_consumed != 0 || !std::isfinite(sample[0]) ||
            !pedal.valid || pedal.frame != frame || pedal.sample_rate != options.sample_rate ||
            pedal.positions != controls.pedal_drawbars || engine.frame_clock() != frame + 1U) {
            fail("Engine failed to produce a consistent actual pedal frame.");
        }
        row.str({});
        row.clear();
        row << pedal.frame << ',' << pedal.sample_rate << ','
            << static_cast<double>(pedal.frame) / pedal.sample_rate
            << ',' << static_cast<unsigned>(pedal.positions[0])
            << ',' << static_cast<unsigned>(pedal.positions[1]);
        for (const double bus : pedal.buses) row << ',' << bus;
        for (const double mixture : pedal.voice.mixtures) row << ',' << mixture;
        row << ',' << pedal.voice.output << ',' << sample[0] << ',' << controls.expression
            << ',' << active << ',';
        for (const bool target : targets) row << static_cast<unsigned>(target);
        row << ',';
        for (const bool closed : contacts) row << static_cast<unsigned>(closed);
        row << ',' << static_cast<unsigned>(upper_down) << ',' << static_cast<unsigned>(lower_down)
            << ',' << static_cast<unsigned>(controls.route_enabled[0])
            << ',' << static_cast<unsigned>(controls.route_enabled[1])
            << ',' << static_cast<unsigned>(controls.selected_banks[0])
            << ',' << static_cast<unsigned>(controls.selected_banks[1])
            << ',' << static_cast<unsigned>(upper_drawbar)
            << ',' << static_cast<unsigned>(lower_drawbar)
            << ',' << phase_before << ',' << engine.frame_clock() << '\n';
        if (!row) fail("Cannot format trace row.");
        append_bounded(output, row.str());
    }
    if (event_index != events.size()) fail("Trace did not consume its complete scenario.");
    return output;
}

// Reserve a sibling directory atomically. A hard link publishes the complete
// file without replacing a destination created after path preflight.
class TemporaryTrace {
public:
    TemporaryTrace() = default;
    TemporaryTrace(const TemporaryTrace&) = delete;
    TemporaryTrace& operator=(const TemporaryTrace&) = delete;
    ~TemporaryTrace() {
        if (stream_.is_open()) stream_.close();
        std::error_code ignored;
        if (!file_.empty()) fs::remove(file_, ignored);
        if (!directory_.empty()) fs::remove(directory_, ignored);
    }

    void publish(const fs::path& output, const std::string& contents) {
        const auto stamp = static_cast<std::uint64_t>(
            std::chrono::steady_clock::now().time_since_epoch().count());
        for (std::uint32_t attempt = 0; attempt < 128; ++attempt) {
            const auto candidate = output.parent_path() /
                (".hammond-pedal-trace-" + std::to_string(stamp) + "-" + std::to_string(attempt));
            std::error_code error;
            if (fs::create_directory(candidate, error)) {
                directory_ = candidate;
                file_ = directory_ / "trace.csv";
                stream_.open(file_, std::ios::binary | std::ios::out | std::ios::trunc);
                if (!stream_) fail("Cannot open temporary trace output.");
                stream_.write(contents.data(), static_cast<std::streamsize>(contents.size()));
                if (!stream_) fail("Error writing temporary trace output.");
                stream_.flush();
                if (!stream_) fail("Error flushing temporary trace output.");
                stream_.close();
                if (!stream_) fail("Error closing temporary trace output.");
                fs::create_hard_link(file_, output, error);
                if (error) {
                    fail("Cannot publish trace without overwriting; hard links are required: " +
                         error.message());
                }
                return;
            }
            if (error && error != std::errc::file_exists) {
                fail("Cannot create temporary trace directory: " + error.message());
            }
        }
        fail("Cannot reserve a unique temporary trace directory.");
    }

private:
    fs::path directory_;
    fs::path file_;
    std::ofstream stream_;
};

} // namespace

int main(int argc, char** argv) {
    try {
        if (argc == 2 && std::string_view(argv[1]) == "--help") {
            std::cout <<
                "Usage: hammond_pedal_trace --profile PROFILE --scenario unmute|overlap|routing\n"
                "       --sample-rate 44100|48000|96000 --seed UINT64 --output TRACE.csv\n"
                "All five options are required exactly once. --help must be used alone.\n"
                "Fixed 120 ms nominal pedal trace; at most 11520 rows and 8 MiB.\n"
                "Ideal manuals and eight ideal pedal contacts; percussion off; fixed scenario controls.\n"
                "Rows: actual rendered pedal record and audio; phase before that sample; clock after it.\n"
                "Output parent must exist; existing paths are never overwritten; hard links required.\n"
                "Synthetic engineering diagnostics, not measured hardware or a DSP checkpoint.\n";
            std::cout.flush();
            if (!std::cout) fail("Cannot write help output.");
            return 0;
        }
        auto options = parse_options(argc, argv);
        validate_paths(options);
        hammond::RuntimeProfile profile;
        std::string error;
        if (!hammond::load_runtime_profile_file(options.profile, profile, error)) {
            fail("Cannot load profile: " + error);
        }
        const auto contents = trace(options, profile);
        TemporaryTrace temporary;
        temporary.publish(options.output, contents);
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "hammond_pedal_trace: " << error.what() << '\n';
        return 1;
    }
}
