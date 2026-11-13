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
constexpr std::uint8_t kPrimaryNote = 60;
constexpr std::uint8_t kCompanionNote = 67;
constexpr std::size_t kSecondHarmonicContact = 3;

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
            if (value != "partial" && value != "legato" && value != "routing") {
                fail("Scenario must be partial, legato or routing.");
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
    std::uint8_t index;
    double value;
};

[[nodiscard]] std::span<const ScheduledEvent> scenario_events(std::string_view name) {
    static constexpr std::array partial{
        ScheduledEvent{0, EventType::KeyPosition, kPrimaryNote, 0.5},
        ScheduledEvent{16, EventType::NoteOn, kPrimaryNote, 100.0},
        ScheduledEvent{32, EventType::KeyPosition, kPrimaryNote, 0.5},
        ScheduledEvent{48, EventType::KeyPosition, kPrimaryNote, 0.46},
        ScheduledEvent{56, EventType::KeyPosition, kPrimaryNote, 0.4},
        ScheduledEvent{64, EventType::NoteOff, kPrimaryNote, 0.0},
        ScheduledEvent{68, EventType::KeyPosition, kPrimaryNote, 0.55},
        ScheduledEvent{84, EventType::NoteOn, kPrimaryNote, 100.0},
        ScheduledEvent{100, EventType::NoteOff, kPrimaryNote, 0.0},
        ScheduledEvent{104, EventType::NoteOn, kPrimaryNote, 100.0},
        ScheduledEvent{112, EventType::AllNotesOff, 0, 0.0}};
    static constexpr std::array legato{
        ScheduledEvent{0, EventType::NoteOn, kPrimaryNote, 100.0},
        ScheduledEvent{16, EventType::NoteOn, kCompanionNote, 100.0},
        ScheduledEvent{32, EventType::NoteOff, kPrimaryNote, 0.0},
        ScheduledEvent{48, EventType::NoteOff, kCompanionNote, 0.0},
        ScheduledEvent{52, EventType::NoteOn, kPrimaryNote, 100.0},
        ScheduledEvent{72, EventType::NoteOff, kPrimaryNote, 0.0},
        ScheduledEvent{96, EventType::NoteOn, kPrimaryNote, 100.0},
        ScheduledEvent{112, EventType::AllNotesOff, 0, 0.0}};
    static constexpr std::array routing{
        ScheduledEvent{0, EventType::NoteOn, kPrimaryNote, 100.0},
        ScheduledEvent{16, EventType::Cancel, 0, 0.0},
        ScheduledEvent{32, EventType::SelectBank, 0, 0.0},
        ScheduledEvent{48, EventType::SelectBank, 0, 1.0},
        ScheduledEvent{64, EventType::Percussion, 0, 0.0},
        ScheduledEvent{80, EventType::Percussion, 0, 1.0},
        ScheduledEvent{96, EventType::NoteOff, kPrimaryNote, 0.0},
        ScheduledEvent{112, EventType::AllNotesOff, 0, 0.0}};
    if (name == "partial") return partial;
    if (name == "legato") return legato;
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
    hammond::Engine engine;
    const hammond::ProcessSpec spec{static_cast<double>(options.sample_rate), 1, options.seed, 0};
    const auto prepared = engine.prepare(profile, spec, hammond::make_nominal_console_model());
    if (prepared != hammond::Status::Ok) {
        fail("Engine preparation failed: " + std::string(hammond::status_name(prepared)));
    }
    const std::array initial{
        Event{0, EventType::Percussion, Manual::Upper, 0, 1.0},
        Event{0, EventType::Percussion, Manual::Upper, 1, 0.0},
        Event{0, EventType::Percussion, Manual::Upper, 2, 0.0},
        Event{0, EventType::Percussion, Manual::Upper, 3, 1.0}};
    flush(engine, initial);
    const auto primary_tone = profile.manual_map[kPrimaryNote - hammond::kMinManualMidiNote]
                                                [kSecondHarmonicContact];
    const auto companion_tone = profile.manual_map[kCompanionNote - hammond::kMinManualMidiNote]
                                                  [kSecondHarmonicContact];
    const auto& primary_source = profile.sources[static_cast<std::size_t>(primary_tone - 1)];
    const auto& companion_source = profile.sources[static_cast<std::size_t>(companion_tone - 1)];
    std::ostringstream row;
    row.imbue(std::locale::classic());
    row << std::setprecision(std::numeric_limits<double>::max_digits10);
    row << "# hammond_console_trace_schema=1\n"
           "# evidence_scope=synthetic_engineering\n"
           "# source_model=ideal-shared-sine-v1\n"
           "# contact_model=" << hammond::kNominalContactModelId << '\n'
        << "# percussion_model=" << hammond::kPercussionModelId << '\n'
        << "# scenario=" << options.scenario << '\n'
        << "# scenario_version=1\n"
           "# profile_id=" << profile.profile_id.data() << '\n'
        << "# authoring_sha256=" << profile.authoring_sha256.data() << '\n'
        << "# profile_digest_scope=declared_authoring_not_compiled_hash\n"
           "# sample_rate=" << options.sample_rate << '\n'
        << "# seed=" << options.seed << '\n'
        << "# frames=" << frames << '\n'
        << "# timing=after_events_before_render_and_advance\n"
           "# manual=upper\n"
           "# primary_midi=" << static_cast<unsigned>(kPrimaryNote) << '\n'
        << "# companion_midi=" << static_cast<unsigned>(kCompanionNote) << '\n'
        << "# primary_tone_id=" << static_cast<unsigned>(primary_tone) << '\n'
        << "# companion_tone_id=" << static_cast<unsigned>(companion_tone) << '\n'
        << "# primary_frequency_hz=" << primary_source.frequency_hz << '\n'
        << "# companion_frequency_hz=" << companion_source.frequency_hz << '\n'
        << "# primary_source_peak=" << primary_source.peak_amplitude << '\n'
        << "# companion_source_peak=" << companion_source.peak_amplitude << '\n'
        << "# profile_output_gain=" << profile.output_gain << '\n'
        << "# initial_percussion=on_second_normal_fast\n"
           "# sustained_drawbars=all_zero\n"
           "# row_count_limit=" << kMaxRows << '\n'
        << "# byte_limit=" << kMaxTraceBytes << '\n'
        << "frame,time_seconds,position,target";
    for (std::size_t index = 0; index < hammond::kDrawbarCount; ++index) row << ",c" << index;
    row << ",companion_position,companion_target";
    for (std::size_t index = 0; index < hammond::kDrawbarCount; ++index) row << ",companion_c" << index;
    row << ",readiness,physical_detector,eligible,routed_detector,percussion_gain,"
           "upper_sustain_gain,route_enabled,selected_bank,percussion_enabled,"
           "primary_phase_turns,companion_phase_turns,audio\n";
    std::string output;
    output.reserve(static_cast<std::size_t>(frames) * 384);
    append_bounded(output, row.str());
    const auto events = scenario_events(options.scenario);
    std::size_t event_index = 0;
    for (std::uint32_t frame = 0; frame < frames; ++frame) {
        while (event_index < events.size() &&
               frame_at(events[event_index].milliseconds, options.sample_rate) == frame) {
            const auto& scheduled = events[event_index++];
            const std::array event{Event{0, scheduled.type, Manual::Upper,
                                         scheduled.index, scheduled.value}};
            flush(engine, event);
        }
        hammond::ContactKeySnapshot primary;
        hammond::ContactKeySnapshot companion;
        double primary_phase = 0.0;
        double companion_phase = 0.0;
        if (engine.frame_clock() != frame ||
            !engine.contact_snapshot(Manual::Upper, kPrimaryNote, primary) ||
            !engine.contact_snapshot(Manual::Upper, kCompanionNote, companion) ||
            !engine.source_phase_turns(primary_tone, primary_phase) ||
            !engine.source_phase_turns(companion_tone, companion_phase)) {
            fail("Trace diagnostic failed.");
        }
        const auto percussion = engine.percussion_diagnostics();
        const auto controls = engine.controls_snapshot();
        std::array<float, 1> sample{};
        const auto rendered = engine.process(1, sample, {});
        if (!rendered.ok() || !std::isfinite(sample[0])) {
            fail("Engine failed to render a finite trace sample.");
        }
        row.str({});
        row.clear();
        row << frame << ',' << static_cast<double>(frame) / options.sample_rate
            << ',' << primary.position << ',' << primary.target;
        for (const bool closed : primary.closed) row << ',' << static_cast<unsigned>(closed);
        row << ',' << companion.position << ',' << companion.target;
        for (const bool closed : companion.closed) row << ',' << static_cast<unsigned>(closed);
        row << ',' << percussion.readiness << ',' << static_cast<unsigned>(percussion.physical_detector)
            << ',' << static_cast<unsigned>(percussion.eligible)
            << ',' << static_cast<unsigned>(percussion.routed_detector)
            << ',' << percussion.gain << ',' << percussion.upper_sustain_gain
            << ',' << static_cast<unsigned>(controls.route_enabled[0])
            << ',' << static_cast<unsigned>(controls.selected_banks[0])
            << ',' << static_cast<unsigned>(controls.percussion.enabled)
            << ',' << primary_phase << ',' << companion_phase << ',' << sample[0] << '\n';
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
                (".hammond-trace-" + std::to_string(stamp) + "-" + std::to_string(attempt));
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
                "Usage: hammond_console_trace --profile PROFILE --scenario partial|legato|routing\n"
                "       --sample-rate 44100|48000|96000 --seed UINT64 --output TRACE.csv\n"
                "All five options are required exactly once. --help must be used alone.\n"
                "Fixed 120 ms nominal linear-contact trace; at most 11520 rows and 8 MiB.\n"
                "Initial percussion: on/second/normal/fast; all sustained drawbars zero.\n"
                "Rows: state after events, before rendering/advancing the same-frame audio sample.\n"
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
        std::cerr << "hammond_console_trace: " << error.what() << '\n';
        return 1;
    }
}
