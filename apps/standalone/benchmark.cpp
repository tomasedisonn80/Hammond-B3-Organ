#include "CliArguments.h"
#include "Session.h"

#include <algorithm>
#include <array>
#include <bit>
#include <charconv>
#include <chrono>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <locale>
#include <numeric>
#include <span>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>
#include <vector>

namespace {

using Clock = std::chrono::steady_clock;
using hammond::standalone::Session;
using hammond::standalone::SessionCommand;
using hammond::standalone::SessionSnapshot;
using hammond::standalone::SessionStatus;
constexpr std::uint64_t kHashBasis = 14695981039346656037ULL;
constexpr std::size_t kDenseCommands = 256;
constexpr std::size_t kClockPairs = 1000;
static_assert(Clock::is_steady);
static_assert(hammond::standalone::kSessionCommandCapacity == kDenseCommands);
static_assert(sizeof(float) == sizeof(std::uint32_t));

[[noreturn]] void fail(const std::string& message) {
    throw std::runtime_error(message);
}

void require(bool condition, std::string_view message) {
    if (!condition) fail(std::string(message));
}

[[nodiscard]] std::string_view session_status(SessionStatus status) noexcept {
    switch (status) {
    case SessionStatus::Ok: return "Ok";
    case SessionStatus::NotPrepared: return "NotPrepared";
    case SessionStatus::AlreadyRunning: return "AlreadyRunning";
    case SessionStatus::NotRunning: return "NotRunning";
    case SessionStatus::InvalidSpec: return "InvalidSpec";
    case SessionStatus::InvalidProfile: return "InvalidProfile";
    case SessionStatus::InvalidBuffer: return "InvalidBuffer";
    case SessionStatus::BlockTooLarge: return "BlockTooLarge";
    case SessionStatus::TimelineOverflow: return "TimelineOverflow";
    case SessionStatus::InvalidCommand: return "InvalidCommand";
    case SessionStatus::QueueFull: return "QueueFull";
    case SessionStatus::RecoveryPending: return "RecoveryPending";
    case SessionStatus::SequenceExhausted: return "SequenceExhausted";
    case SessionStatus::CoreFailure: return "CoreFailure";
    }
    return "Unknown";
}

void require_status(SessionStatus actual, SessionStatus expected, std::string_view operation) {
    if (actual != expected) {
        fail(std::string(operation) + ": expected " + std::string(session_status(expected)) +
             ", got " + std::string(session_status(actual)) + '.');
    }
}

struct Options {
    std::filesystem::path profile;
    std::uint32_t sample_rate = 48000;
    std::uint32_t buffer_frames = 512;
    std::uint32_t iterations = 500;
    std::uint32_t warmup = 16;
    std::string_view workload = "performance";
};

[[nodiscard]] std::uint64_t unsigned_number(std::string_view value,
                                           std::string_view option) {
    if (value.empty() || value.size() > 20 ||
        !std::all_of(value.begin(), value.end(), [](char character) {
            return character >= '0' && character <= '9';
        })) {
        fail(std::string(option) + " requires an unsigned decimal integer of at most 20 digits.");
    }
    std::uint64_t number = 0;
    const auto result = std::from_chars(value.data(), value.data() + value.size(), number);
    if (result.ec != std::errc{} || result.ptr != value.data() + value.size()) {
        fail(std::string(option) + " is out of range.");
    }
    return number;
}

[[nodiscard]] Options parse_options(int argc, char* argv[]) {
    constexpr std::array<std::string_view, 6> names{
        "--profile", "--sample-rate", "--buffer-frames", "--iterations", "--warmup", "--workload"};
    require(argc >= 1 && argc <= 13, "Too many arguments. Use --help for usage.");
    Options options;
    std::array<bool, names.size()> seen{};
    for (int argument = 1; argument < argc; ++argument) {
        const std::string_view name(argv[argument]);
        const auto found = std::find(names.begin(), names.end(), name);
        if (found == names.end()) fail("Unknown argument: " + std::string(name.substr(0, 128)));
        const auto index = static_cast<std::size_t>(found - names.begin());
        if (seen[index]) fail("Duplicate argument: " + std::string(name));
        seen[index] = true;
        if (++argument == argc) fail("Missing value for " + std::string(name));
        const std::string_view value(argv[argument]);
        if (value.empty() || value.size() > 4096 || value.starts_with("--")) {
            fail("Missing or oversized value for " + std::string(name));
        }
        if (name == "--profile") {
            options.profile = hammond::cli::argument_path(value);
        } else if (name == "--workload") {
            require(value == "silence" || value == "performance" || value == "dense" ||
                        value == "recovery", "Workload must be silence, performance, dense, or recovery.");
            options.workload = value;
        } else {
            const auto number = unsigned_number(value, name);
            if (name == "--sample-rate") {
                require(number == 44100 || number == 48000 || number == 96000,
                        "Sample rate must be 44100, 48000, or 96000 Hz.");
                options.sample_rate = static_cast<std::uint32_t>(number);
            } else if (name == "--buffer-frames") {
                require(number == 128 || number == 256 || number == 512 || number == 1024 ||
                            number == 2048, "Buffer frames must be 128, 256, 512, 1024, or 2048.");
                options.buffer_frames = static_cast<std::uint32_t>(number);
            } else if (name == "--iterations") {
                require(number >= 100 && number <= 5000, "Iterations must be in 100..5000.");
                options.iterations = static_cast<std::uint32_t>(number);
            } else {
                require(number <= 1000, "Warmup must be in 0..1000.");
                options.warmup = static_cast<std::uint32_t>(number);
            }
        }
    }
    require(seen[0], "--profile PATH is required.");
    return options;
}

void hash_bytes(std::uint64_t& hash, std::span<const std::byte> bytes) noexcept {
    for (const auto byte : bytes) {
        hash ^= std::to_integer<std::uint8_t>(byte);
        hash *= 1099511628211ULL;
    }
}

[[nodiscard]] std::string hash_text(std::uint64_t hash) {
    std::ostringstream output;
    output.imbue(std::locale::classic());
    output << std::hex << std::setfill('0') << std::setw(16) << hash;
    return output.str();
}

struct LoadedProfile {
    hammond::RuntimeProfile value{};
    std::uint64_t bytes_hash = kHashBasis;
    std::size_t bytes = 0;
};

[[nodiscard]] LoadedProfile load_profile(const std::filesystem::path& path) {
    std::ifstream input(path, std::ios::binary);
    require(input.is_open(), "Cannot open the compiled profile.");
    std::string bytes(hammond::kMaxCompiledProfileBytes + 1, '\0');
    input.read(bytes.data(), static_cast<std::streamsize>(bytes.size()));
    require(!input.bad() && (input.eof() || !input.fail()), "Cannot read the compiled profile.");
    const auto count = input.gcount();
    require(count >= 0 && static_cast<std::uint64_t>(count) <= hammond::kMaxCompiledProfileBytes,
            "Compiled profile exceeds its size bound.");
    bytes.resize(static_cast<std::size_t>(count));
    LoadedProfile profile;
    profile.bytes = bytes.size();
    hash_bytes(profile.bytes_hash, std::as_bytes(std::span<const char>(bytes)));
    std::istringstream parser(bytes);
    std::string error;
    if (!hammond::load_runtime_profile(parser, profile.value, error)) {
        fail("Cannot parse the compiled profile: " + error);
    }
    return profile;
}

[[nodiscard]] hammond::ControlSnapshot registration() noexcept {
    hammond::ControlSnapshot controls;
    controls.drawbars[0][1] = {8, 8, 8, 0, 0, 0, 0, 0, 0};
    controls.drawbars[1][1] = {0, 0, 8, 8, 0, 0, 0, 0, 0};
    controls.pedal_drawbars = {8, 5};
    controls.expression = 0.75;
    controls.percussion = {true, hammond::PercussionHarmonic::Third,
        hammond::PercussionVolume::Soft, hammond::PercussionDecay::Fast};
    return controls;
}

[[nodiscard]] std::array<SessionCommand, 6> held_notes() noexcept {
    return {{
        hammond::PerformanceInputEvent{hammond::HostNoteEvent{
            0, hammond::HostNoteKind::On, 0, 0, 60, 127, 1}},
        hammond::PerformanceInputEvent{hammond::HostNoteEvent{
            0, hammond::HostNoteKind::On, 0, 0, 64, 127, 2}},
        hammond::PerformanceInputEvent{hammond::HostNoteEvent{
            0, hammond::HostNoteKind::On, 0, 0, 67, 127, 3}},
        hammond::PerformanceInputEvent{hammond::HostNoteEvent{
            0, hammond::HostNoteKind::On, 1, 0, 48, 127, 4}},
        hammond::PerformanceInputEvent{hammond::HostNoteEvent{
            0, hammond::HostNoteKind::On, 1, 0, 55, 127, 5}},
        hammond::PerformanceInputEvent{hammond::PedalNoteEvent{
            0, hammond::PedalNoteKind::On, 0, 0, hammond::PedalId{1}, 127, 6}}
    }};
}

[[nodiscard]] std::array<SessionCommand, kDenseCommands> dense_controls() noexcept {
    std::array<SessionCommand, kDenseCommands> commands{};
    for (std::size_t index = 0; index < commands.size(); ++index) {
        commands[index] = hammond::PerformanceInputEvent{hammond::Event{
            0, hammond::EventType::Expression, hammond::Manual::Upper, 0,
            index % 2 == 0 ? 0.5 : 0.75}};
    }
    return commands;
}

struct Stage {
    std::uint64_t post_attempts = 0;
    std::uint64_t accepted_commands = 0;
    std::uint64_t applied_commands = 0;
    std::uint64_t discarded_commands = 0;
    std::uint64_t queue_full_posts = 0;
    std::uint64_t recovery_pending_posts = 0;
    std::uint64_t recoveries = 0;
    std::uint64_t positive_render_calls = 0;
    std::uint64_t zero_frame_render_calls = 0;
    std::uint64_t rendered_frames = 0;
    std::uint64_t start_frame = 0;
    std::uint64_t end_frame = 0;
    std::uint64_t start_resolved_sequence = 0;
    std::uint64_t end_resolved_sequence = 0;
};

struct Expected {
    SessionSnapshot snapshot{};
    std::uint64_t accepted_sequence = 0;
    std::uint64_t pending_commands = 0;
    bool recovery_pending = false;
};

void set_holds(SessionSnapshot& snapshot, bool held) noexcept {
    snapshot.held_keys = {};
    snapshot.held_pedals = {};
    if (held) {
        for (const auto note : {60U, 64U, 67U}) {
            snapshot.held_keys[0][note - hammond::kMinManualMidiNote] = true;
        }
        for (const auto note : {48U, 55U}) {
            snapshot.held_keys[1][note - hammond::kMinManualMidiNote] = true;
        }
        snapshot.held_pedals[0] = true;
    }
}

[[nodiscard]] SessionSnapshot read_checked(const Session& session, const Expected& expected) {
    SessionSnapshot snapshot;
    require(session.read_snapshot(snapshot), "Session snapshot publication was unavailable.");
    const auto& wanted = expected.snapshot;
    require(snapshot.prepared == wanted.prepared && snapshot.running == wanted.running,
            "Snapshot lifecycle does not match the workload.");
    require(snapshot.sample_rate == wanted.sample_rate && snapshot.frame_clock == wanted.frame_clock,
            "Snapshot sample clock does not match accepted frames.");
    require(snapshot.controls == wanted.controls, "Snapshot registration does not match the workload.");
    require(snapshot.held_keys == wanted.held_keys && snapshot.held_pedals == wanted.held_pedals,
            "Snapshot held notes do not match the workload.");
    require(snapshot.publication_revision == wanted.publication_revision,
            "Snapshot publication count does not match lifecycle/render calls.");
    require(snapshot.resolved_sequence == wanted.resolved_sequence &&
                snapshot.last_applied_sequence == wanted.last_applied_sequence,
            "Snapshot command acknowledgments do not match admitted work.");
    require(snapshot.recovery_count == wanted.recovery_count &&
                snapshot.queue_overflows == wanted.queue_overflows &&
                snapshot.discarded_commands == wanted.discarded_commands &&
                snapshot.rejected_commands == 0 && snapshot.fault_flags == wanted.fault_flags &&
                snapshot.last_core_status == hammond::Status::Ok,
            "Snapshot recovery/fault counters do not match declared expected overflow work.");
    require(std::isfinite(snapshot.peak) && snapshot.peak == wanted.peak,
            "Snapshot peak does not match the actual stereo output.");
    return snapshot;
}

void post_checked(Session& session, Expected& expected, Stage& stage,
                  const SessionCommand& command) {
    const auto result = session.post(command);
    require_status(result.status, SessionStatus::Ok, "Session::post");
    require(result.sequence == expected.accepted_sequence + 1,
            "Accepted command did not receive the next sequence.");
    ++expected.accepted_sequence;
    ++expected.pending_commands;
    ++stage.post_attempts;
    ++stage.accepted_commands;
}

void post_batch(Session& session, Expected& expected, Stage& stage,
                std::span<const SessionCommand> commands) {
    for (const auto& command : commands) post_checked(session, expected, stage, command);
}

void request_recovery(Session& session, Expected& expected, Stage& stage,
                      const SessionCommand& command) {
    require(expected.pending_commands == kDenseCommands, "Recovery queue was not filled exactly.");
    const auto overflow = session.post(command);
    require_status(overflow.status, SessionStatus::QueueFull, "Intentional overflow");
    require(overflow.sequence == 0, "Overflow unexpectedly accepted a command.");
    ++stage.post_attempts;
    ++stage.queue_full_posts;
    const auto blocked = session.post(command);
    require_status(blocked.status, SessionStatus::RecoveryPending, "Recovery barrier probe");
    require(blocked.sequence == 0, "Recovery barrier unexpectedly accepted a command.");
    ++stage.post_attempts;
    ++stage.recovery_pending_posts;
    ++expected.snapshot.queue_overflows;
    expected.snapshot.fault_flags =
        static_cast<std::uint32_t>(hammond::standalone::SessionFault::QueueOverflow);
    expected.recovery_pending = true;
}

// Only the actual Session::render invocation lies between these clock reads.
// All command admission, output checking, snapshot copies and accounting follow
// or precede that interval. The caller owns preallocated output/time storage.
[[nodiscard]] SessionSnapshot render_checked(Session& session, Expected& expected, Stage& stage,
                                             std::uint32_t frames, std::span<float> stereo,
                                             double* duration_ns = nullptr) {
    hammond::standalone::RenderResult result;
    if (duration_ns != nullptr) {
        const auto begin = Clock::now();
        result = session.render(frames, stereo);
        const auto end = Clock::now();
        *duration_ns = std::chrono::duration<double, std::nano>(end - begin).count();
        require(std::isfinite(*duration_ns) && *duration_ns >= 0.0, "Invalid elapsed clock sample.");
    } else {
        result = session.render(frames, stereo);
    }
    require_status(result.status, SessionStatus::Ok, "Session::render");
    require(result.frames_rendered == frames, "Session::render returned an unexpected frame count.");
    if (expected.recovery_pending) {
        expected.snapshot.discarded_commands += expected.pending_commands;
        stage.discarded_commands += expected.pending_commands;
        ++expected.snapshot.recovery_count;
        ++stage.recoveries;
        set_holds(expected.snapshot, false);
        expected.recovery_pending = false;
    } else if (expected.pending_commands != 0) {
        expected.snapshot.last_applied_sequence = expected.accepted_sequence;
        stage.applied_commands += expected.pending_commands;
    }
    expected.snapshot.resolved_sequence = expected.accepted_sequence;
    expected.pending_commands = 0;
    expected.snapshot.frame_clock += result.frames_rendered;
    expected.snapshot.publication_revision += 2;
    stage.rendered_frames += result.frames_rendered;
    if (frames == 0) {
        ++stage.zero_frame_render_calls;
    } else {
        ++stage.positive_render_calls;
        float peak = 0.0F;
        for (std::size_t frame = 0; frame < frames; ++frame) {
            const float left = stereo[frame * 2];
            const float right = stereo[frame * 2 + 1];
            require(std::isfinite(left) && std::isfinite(right), "Nonfinite stereo output sample.");
            require(std::bit_cast<std::uint32_t>(left) == std::bit_cast<std::uint32_t>(right),
                    "Session left/right output samples differ.");
            peak = std::max(peak, std::abs(left));
        }
        expected.snapshot.peak = peak;
    }
    return read_checked(session, expected);
}

void finish_stage(Stage& stage, const SessionSnapshot& begin, const SessionSnapshot& end) {
    stage.start_frame = begin.frame_clock;
    stage.end_frame = end.frame_clock;
    stage.start_resolved_sequence = begin.resolved_sequence;
    stage.end_resolved_sequence = end.resolved_sequence;
    require(stage.accepted_commands == stage.applied_commands + stage.discarded_commands &&
                stage.post_attempts == stage.accepted_commands + stage.queue_full_posts +
                    stage.recovery_pending_posts &&
                stage.accepted_commands == end.resolved_sequence - begin.resolved_sequence &&
                stage.rendered_frames == end.frame_clock - begin.frame_clock &&
                stage.discarded_commands == end.discarded_commands - begin.discarded_commands &&
                stage.queue_full_posts == end.queue_overflows - begin.queue_overflows &&
                stage.recoveries == end.recovery_count - begin.recovery_count,
            "Stage counts do not reconcile with actual published Session state.");
}

struct Distribution {
    double minimum = 0.0;
    double median = 0.0;
    double p95 = 0.0;
    double p99 = 0.0;
    double maximum = 0.0;
    double total = 0.0;
};

[[nodiscard]] Distribution distribution(std::span<const double> samples,
                                         std::span<double> sorted) {
    require(!samples.empty() && samples.size() == sorted.size(), "Invalid statistics storage.");
    std::copy(samples.begin(), samples.end(), sorted.begin());
    std::sort(sorted.begin(), sorted.end());
    const auto middle = sorted.size() / 2;
    return {sorted.front(), sorted.size() % 2 == 0 ?
        (sorted[middle - 1] + sorted[middle]) / 2.0 : sorted[middle],
        sorted[(sorted.size() * 95 + 99) / 100 - 1],
        sorted[(sorted.size() * 99 + 99) / 100 - 1], sorted.back(),
        std::accumulate(samples.begin(), samples.end(), 0.0)};
}

[[nodiscard]] Distribution clock_calibration() {
    std::array<double, kClockPairs> samples{};
    std::array<double, kClockPairs> sorted{};
    for (auto& sample : samples) {
        const auto begin = Clock::now();
        const auto end = Clock::now();
        sample = std::chrono::duration<double, std::nano>(end - begin).count();
        require(std::isfinite(sample) && sample >= 0.0, "Invalid clock calibration sample.");
    }
    return distribution(samples, sorted);
}

struct Report {
    Stage setup;
    Stage warmup;
    Stage measured;
    SessionSnapshot after_setup;
    SessionSnapshot after_warmup;
    SessionSnapshot after_measurement;
    SessionSnapshot after_stop;
    std::vector<double> samples;
    Distribution render_ns;
    Distribution clock_pair_ns;
    double measured_loop_elapsed_ns = 0.0;
    std::uint64_t audio_hash = kHashBasis;
    float measured_peak_max = 0.0F;
    std::uint64_t calls_above_period = 0;
};

[[nodiscard]] Report run(const Options& options, const hammond::RuntimeProfile& profile) {
    Report report;
    report.samples.resize(options.iterations);
    std::vector<double> sorted(options.iterations);
    std::vector<float> stereo(static_cast<std::size_t>(options.buffer_frames) * 2);
    const auto notes = held_notes();
    const auto controls = dense_controls();
    const bool silent = options.workload == "silence";
    const bool recovery = options.workload == "recovery";
    const bool dense = options.workload == "dense";
    const SessionCommand initial_controls = registration();
    report.clock_pair_ns = clock_calibration();
    Session session;
    Expected expected;
    static_cast<void>(read_checked(session, expected));
    require_status(session.prepare(profile, {static_cast<double>(options.sample_rate),
                   options.buffer_frames, 0, 0}), SessionStatus::Ok, "Session::prepare");
    expected.snapshot.prepared = true;
    expected.snapshot.sample_rate = options.sample_rate;
    expected.snapshot.publication_revision += 2;
    static_cast<void>(read_checked(session, expected));
    require_status(session.start(), SessionStatus::Ok, "Session::start");
    expected.snapshot.running = true;
    expected.snapshot.publication_revision += 2;
    const auto started = read_checked(session, expected);
    if (!silent) {
        post_checked(session, expected, report.setup, initial_controls);
        expected.snapshot.controls = registration();
        if (!recovery) {
            post_batch(session, expected, report.setup, notes);
            set_holds(expected.snapshot, true);
        }
    }
    report.after_setup = render_checked(session, expected, report.setup, 0, {});
    finish_stage(report.setup, started, report.after_setup);

    const auto cycle = [&](Stage& stage, double* elapsed) {
        require(expected.pending_commands == 0 && !expected.recovery_pending,
                "A previous callback left unresolved commands.");
        if (recovery) {
            post_batch(session, expected, stage, notes);
            set_holds(expected.snapshot, true);
            // This unmeasured zero-frame call establishes actual held notes
            // before the subsequent queue overflow requests global recovery.
            static_cast<void>(render_checked(session, expected, stage, 0, {}));
        }
        if (dense || recovery) post_batch(session, expected, stage, controls);
        if (recovery) request_recovery(session, expected, stage, controls.front());
        const auto snapshot = render_checked(session, expected, stage,
                                              options.buffer_frames, stereo, elapsed);
        require((silent || recovery) ? snapshot.peak == 0.0F : snapshot.peak > 0.0F,
                "Workload audio activity does not match its declared held state.");
        return snapshot;
    };

    report.after_warmup = report.after_setup;
    for (std::uint32_t index = 0; index < options.warmup; ++index) {
        report.after_warmup = cycle(report.warmup, nullptr);
    }
    finish_stage(report.warmup, report.after_setup, report.after_warmup);
    const auto begin = Clock::now();
    for (auto& elapsed : report.samples) {
        report.after_measurement = cycle(report.measured, &elapsed);
        hash_bytes(report.audio_hash, std::as_bytes(std::span<const float>(stereo)));
        report.measured_peak_max = std::max(report.measured_peak_max, report.after_measurement.peak);
    }
    const auto end = Clock::now();
    report.measured_loop_elapsed_ns = std::chrono::duration<double, std::nano>(end - begin).count();
    finish_stage(report.measured, report.after_warmup, report.after_measurement);
    const auto positive_calls = static_cast<std::uint64_t>(options.warmup) + options.iterations;
    require(expected.snapshot.frame_clock == positive_calls * options.buffer_frames &&
                report.warmup.positive_render_calls == options.warmup &&
                report.measured.positive_render_calls == options.iterations &&
                report.setup.zero_frame_render_calls == 1 &&
                report.warmup.zero_frame_render_calls == (recovery ? options.warmup : 0) &&
                report.measured.zero_frame_render_calls == (recovery ? options.iterations : 0),
            "Final render counts do not match requested workload blocks/frames.");
    require(expected.pending_commands == 0 && !expected.recovery_pending,
            "Benchmark ended with unresolved queue work.");
    require_status(session.stop(), SessionStatus::Ok, "Session::stop");
    expected.snapshot.running = false;
    expected.snapshot.peak = 0.0F;
    expected.snapshot.publication_revision += 2;
    set_holds(expected.snapshot, false);
    report.after_stop = read_checked(session, expected);
    report.render_ns = distribution(report.samples, sorted);
    require(std::isfinite(report.measured_loop_elapsed_ns) &&
                report.measured_loop_elapsed_ns >= report.render_ns.total,
            "Measured-loop elapsed time does not contain all render intervals.");
    const double period_ns = static_cast<double>(options.buffer_frames) * 1.0e9 / options.sample_rate;
    report.calls_above_period = static_cast<std::uint64_t>(std::count_if(
        report.samples.begin(), report.samples.end(),
        [period_ns](double value) { return value > period_ns; }));
    return report;
}

void write_string(std::ostream& output, std::string_view value) {
    constexpr char digits[] = "0123456789abcdef";
    output << '"';
    for (const char character : value) {
        const auto byte = static_cast<unsigned char>(character);
        if (byte == '"' || byte == '\\') output << '\\' << character;
        else if (byte < 0x20U || byte >= 0x7fU) {
            output << "\\u00" << digits[byte >> 4U] << digits[byte & 15U];
        } else output << character;
    }
    output << '"';
}

template <typename Values>
void write_numbers(std::ostream& output, const Values& values) {
    output << '[';
    bool first = true;
    for (const auto value : values) {
        if (!first) output << ',';
        first = false;
        output << +value;
    }
    output << ']';
}

template <std::size_t Size>
void write_holds(std::ostream& output, const std::array<bool, Size>& holds, std::size_t first_id) {
    output << '[';
    bool first = true;
    for (std::size_t index = 0; index < holds.size(); ++index) {
        if (!holds[index]) continue;
        if (!first) output << ',';
        first = false;
        output << index + first_id;
    }
    output << ']';
}

void write_controls(std::ostream& output, const hammond::ControlSnapshot& controls) {
    output << "{\"upper_a\":"; write_numbers(output, controls.drawbars[0][0]);
    output << ",\"upper_b\":"; write_numbers(output, controls.drawbars[0][1]);
    output << ",\"lower_a\":"; write_numbers(output, controls.drawbars[1][0]);
    output << ",\"lower_b\":"; write_numbers(output, controls.drawbars[1][1]);
    output << ",\"selected_banks\":[" << static_cast<unsigned int>(controls.selected_banks[0])
        << ',' << static_cast<unsigned int>(controls.selected_banks[1])
        << "],\"fixed_registrations\":[" << static_cast<unsigned int>(controls.fixed_registrations[0])
        << ',' << static_cast<unsigned int>(controls.fixed_registrations[1])
        << "],\"preset_selections\":[";
    for (std::size_t manual = 0; manual < hammond::kManualCount; ++manual) {
        if (manual != 0) output << ',';
        hammond::PresetSelection selection{};
        if (hammond::control_preset_selection(controls, static_cast<hammond::Manual>(manual), selection)) {
            output << static_cast<unsigned int>(selection);
        } else output << "null";
    }
    output << "],\"route_enabled\":[" << controls.route_enabled[0] << ',' << controls.route_enabled[1]
        << "],\"pedal_drawbars\":";
    write_numbers(output, controls.pedal_drawbars);
    output << ",\"expression\":" << controls.expression << ",\"percussion\":{\"enabled\":"
        << controls.percussion.enabled << ",\"harmonic\":"
        << static_cast<unsigned int>(controls.percussion.harmonic) << ",\"volume\":"
        << static_cast<unsigned int>(controls.percussion.volume) << ",\"decay\":"
        << static_cast<unsigned int>(controls.percussion.decay) << "}}";
}

void write_snapshot(std::ostream& output, const SessionSnapshot& snapshot) {
    output << "{\"prepared\":" << snapshot.prepared << ",\"running\":" << snapshot.running
        << ",\"sample_rate_hz\":" << snapshot.sample_rate << ",\"frame_clock\":" << snapshot.frame_clock
        << ",\"peak\":" << snapshot.peak << ",\"publication_revision\":" << snapshot.publication_revision
        << ",\"resolved_sequence\":" << snapshot.resolved_sequence
        << ",\"last_applied_sequence\":" << snapshot.last_applied_sequence
        << ",\"recovery_count\":" << snapshot.recovery_count
        << ",\"queue_overflows\":" << snapshot.queue_overflows
        << ",\"rejected_commands\":" << snapshot.rejected_commands
        << ",\"discarded_commands\":" << snapshot.discarded_commands
        << ",\"fault_flags\":" << snapshot.fault_flags << ",\"last_core_status\":";
    write_string(output, hammond::status_name(snapshot.last_core_status));
    output << ",\"held_upper_midi\":"; write_holds(output, snapshot.held_keys[0], 36);
    output << ",\"held_lower_midi\":"; write_holds(output, snapshot.held_keys[1], 36);
    output << ",\"held_pedal_ids\":"; write_holds(output, snapshot.held_pedals, 1);
    output << ",\"controls\":"; write_controls(output, snapshot.controls);
    output << '}';
}

void write_stage(std::ostream& output, const Stage& stage) {
    output << "{\"post_attempts\":" << stage.post_attempts
        << ",\"accepted_commands\":" << stage.accepted_commands
        << ",\"applied_commands\":" << stage.applied_commands
        << ",\"discarded_commands\":" << stage.discarded_commands
        << ",\"queue_full_posts\":" << stage.queue_full_posts
        << ",\"recovery_pending_posts\":" << stage.recovery_pending_posts
        << ",\"recoveries\":" << stage.recoveries
        << ",\"positive_render_calls\":" << stage.positive_render_calls
        << ",\"zero_frame_render_calls\":" << stage.zero_frame_render_calls
        << ",\"rendered_frames\":" << stage.rendered_frames
        << ",\"start_frame\":" << stage.start_frame << ",\"end_frame\":" << stage.end_frame
        << ",\"start_resolved_sequence\":" << stage.start_resolved_sequence
        << ",\"end_resolved_sequence\":" << stage.end_resolved_sequence << '}';
}

void write_distribution(std::ostream& output, const Distribution& values, double divisor = 1.0,
                         bool total = true) {
    output << "{\"minimum\":" << values.minimum / divisor
        << ",\"median\":" << values.median / divisor << ",\"p95\":" << values.p95 / divisor
        << ",\"p99\":" << values.p99 / divisor << ",\"maximum\":" << values.maximum / divisor;
    if (total) output << ",\"total\":" << values.total / divisor;
    output << '}';
}

[[nodiscard]] std::string report_json(const Options& options, const LoadedProfile& profile,
                                      const Report& report) {
    std::ostringstream output;
    output.imbue(std::locale::classic());
    output << std::setprecision(std::numeric_limits<double>::max_digits10) << std::boolalpha;
    const double period_ns = static_cast<double>(options.buffer_frames) * 1.0e9 / options.sample_rate;
    output << "{\"schema\":\"hammond-standalone-benchmark-v2\",\"status\":\"ok\","
        "\"scope\":\"offline observed wall-clock intervals around actual Session::render\","
        "\"workload\":";
    write_string(output, options.workload);
    output << ",\"workload_version\":1,\"sample_rate_hz\":" << options.sample_rate
        << ",\"buffer_frames\":" << options.buffer_frames << ",\"iterations\":" << options.iterations
        << ",\"warmup\":" << options.warmup << ",\"seed\":0,\"initial_frame\":0,"
        "\"nominal_callback_period_ns\":" << period_ns << ",\"session_model\":";
    write_string(output, hammond::standalone::kSessionModelId);
    output << ",\"source_model\":\"ideal-shared-sine-v1\",\"build\":{\"configuration\":";
    write_string(output, HAMMOND_STANDALONE_BENCHMARK_CONFIGURATION);
    output << ",\"compiler_id\":"; write_string(output, HAMMOND_STANDALONE_BENCHMARK_COMPILER_ID);
    output << ",\"compiler_version\":"; write_string(output, HAMMOND_STANDALONE_BENCHMARK_COMPILER_VERSION);
    output << ",\"target_system\":"; write_string(output, HAMMOND_STANDALONE_BENCHMARK_TARGET_SYSTEM);
    output << ",\"target_processor\":"; write_string(output, HAMMOND_STANDALONE_BENCHMARK_TARGET_PROCESSOR);
    output << ",\"source_manifest_sha256\":"; write_string(output, HAMMOND_STANDALONE_BENCHMARK_SOURCE_ID);
#ifdef NDEBUG
    constexpr bool ndebug = true;
#else
    constexpr bool ndebug = false;
#endif
    output << ",\"cplusplus\":" << __cplusplus << ",\"ndebug\":" << ndebug
        << ",\"project_sanitizers_enabled\":" << (HAMMOND_STANDALONE_BENCHMARK_SANITIZERS != 0)
        << ",\"sanitizer_scope\":\"project option; externally injected flags are not detected\"},"
        "\"profile\":{\"id\":";
    write_string(output, profile.value.profile_id.data());
    output << ",\"authoring_sha256_retained\":";
    write_string(output, profile.value.authoring_sha256.data());
    output << ",\"compiled_bytes\":" << profile.bytes << ",\"compiled_fnv1a64\":";
    write_string(output, hash_text(profile.bytes_hash));
    output << "},\"stages\":{\"setup\":"; write_stage(output, report.setup);
    output << ",\"warmup\":"; write_stage(output, report.warmup);
    output << ",\"measured\":"; write_stage(output, report.measured);
    output << "},\"snapshots\":{\"after_setup\":"; write_snapshot(output, report.after_setup);
    output << ",\"after_warmup\":"; write_snapshot(output, report.after_warmup);
    output << ",\"after_measurement\":"; write_snapshot(output, report.after_measurement);
    output << ",\"after_stop\":"; write_snapshot(output, report.after_stop);
    output << "},\"timing\":{\"clock\":\"std::chrono::steady_clock\",\"clock_is_steady\":"
        << Clock::is_steady << ",\"clock_tick_seconds\":"
        << static_cast<double>(Clock::period::num) / static_cast<double>(Clock::period::den)
        << ",\"warmup_included\":false,\"timer_overhead_subtracted\":false,\"samples_ns\":";
    write_numbers(output, report.samples);
    output << ",\"render_ns\":"; write_distribution(output, report.render_ns);
    output << ",\"callback_period_ratio\":"; write_distribution(output, report.render_ns, period_ns, false);
    output << ",\"observed_calls_above_period\":" << report.calls_above_period
        << ",\"measured_loop_elapsed_ns\":" << report.measured_loop_elapsed_ns
        << ",\"clock_pair_calibration\":{\"iterations\":" << kClockPairs << ",\"ns\":";
    write_distribution(output, report.clock_pair_ns);
    output << "}},\"audio\":{\"measured_stereo_fnv1a64\":";
    write_string(output, hash_text(report.audio_hash));
    output << ",\"sample_encoding\":\"native float32 object bytes; same-build diagnostic sink\","
        "\"measured_stereo_samples\":" << static_cast<std::uint64_t>(options.iterations) * options.buffer_frames * 2
        << ",\"all_samples_finite\":true,\"channels_bit_identical\":true,\"measured_peak_max\":"
        << report.measured_peak_max << "},\"claims\":{\"hard_realtime\":false,\"device_deadline_pass\":null,"
        "\"device_underruns\":null,\"device_latency_seconds\":null,\"timing_threshold_applied\":false}}\n";
    require(static_cast<bool>(output), "Cannot format the benchmark report.");
    return output.str();
}

static int benchmark_main(int argc, char* argv[]) {
    try {
        if (argc == 2 && std::string_view(argv[1]) == "--help") {
            std::cout <<
                "Usage: hammond_standalone_benchmark --profile PATH [options]\n"
                "  --sample-rate 44100|48000|96000        default: 48000\n"
                "  --buffer-frames 128|256|512|1024|2048  default: 512\n"
                "  --iterations N                       100..5000, default: 500\n"
                "  --warmup N                           0..1000, default: 16\n"
                "  --workload silence|performance|dense|recovery  default: performance\n"
                "JSON stdout; only Session::render is timed. Queue posting, recovery rearm,\n"
                "validation and output are outside measured render intervals. Offline timings\n"
                "do not establish real-device deadlines, underruns, or device latency.\n";
        } else {
            const auto options = parse_options(argc, argv);
            const auto profile = load_profile(options.profile);
            const auto report = run(options, profile.value);
            // No success report is constructed or written until all workload,
            // state, sequence, clock, finite-output and shutdown checks pass.
            const auto json = report_json(options, profile, report);
            std::cout.write(json.data(), static_cast<std::streamsize>(json.size()));
        }
        std::cout.flush();
        require(static_cast<bool>(std::cout), "Cannot write stdout.");
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "hammond_standalone_benchmark: " << error.what() << '\n';
        return 1;
    } catch (...) {
        std::cerr << "hammond_standalone_benchmark: unknown failure.\n";
        return 1;
    }
}

} // namespace

#ifdef _WIN32
int wmain(int argc, wchar_t* argv[]) {
    return hammond::cli::run_windows(argc, argv, benchmark_main,
        "hammond_standalone_benchmark", {13, 4096});
}
#else
int main(int argc, char* argv[]) {
    return benchmark_main(argc, argv);
}
#endif
