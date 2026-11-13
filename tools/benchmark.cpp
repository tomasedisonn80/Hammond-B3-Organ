#include "CliArguments.h"
#include "hammond/Engine.h"
#include "hammond/InputProcessor.h"
#include "hammond/Profile.h"

#include <algorithm>
#include <array>
#include <charconv>
#include <chrono>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <filesystem>
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
#include <vector>

namespace {

using Clock = std::chrono::steady_clock;
constexpr std::uint64_t kMaxFramesPerCase = 1048576;
constexpr std::uint64_t kMaxCallsPerCase = 10000;
constexpr std::uint64_t kHashBasis = 14695981039346656037ULL;
constexpr std::array<std::string_view, 4> kCases{
    "silence", "all_keys", "disconnected", "dense_automation"};
constexpr std::array<std::string_view, 2> kConsoleCases{"console_motion", "owned_input"};
constexpr std::size_t kConsoleKeys = hammond::kManualCount * hammond::kManualKeyCount;

[[nodiscard]] bool console_selection(std::string_view name) noexcept {
    return name == "console_all" ||
        std::find(kConsoleCases.begin(), kConsoleCases.end(), name) != kConsoleCases.end();
}

[[noreturn]] void fail(const std::string& message) {
    throw std::runtime_error(message);
}

struct Options {
    std::filesystem::path profile{HAMMOND_BENCHMARK_PROFILE};
    std::uint32_t sample_rate = 48000;
    std::uint32_t block_size = 64;
    std::uint32_t iterations = 128;
    std::uint32_t warmup = 16;
    std::uint64_t seed = 0;
    std::string_view selected_case = "all";
};

[[nodiscard]] std::uint64_t unsigned_number(std::string_view value,
                                           std::string_view name) {
    if (value.empty() || value.size() > 20 ||
        !std::all_of(value.begin(), value.end(), [](char ch) {
            return ch >= '0' && ch <= '9';
        })) {
        fail(std::string(name) + " must be an unsigned decimal integer (at most 20 digits).");
    }
    std::uint64_t result = 0;
    const auto parsed = std::from_chars(value.data(), value.data() + value.size(), result);
    if (parsed.ec != std::errc{} || parsed.ptr != value.data() + value.size()) {
        fail(std::string(name) + " is out of range.");
    }
    return result;
}

[[nodiscard]] Options parse_options(int argc, char* argv[]) {
    constexpr std::array<std::string_view, 7> names{
        "--profile", "--sample-rate", "--block-size", "--iterations", "--warmup", "--seed", "--case"};
    if (argc > 15) {
        fail("Too many arguments. Use --help for usage.");
    }
    Options options;
    std::array<bool, names.size()> seen{};
    for (int argument = 1; argument < argc; ++argument) {
        const std::string_view name(argv[argument]);
        const auto found = std::find(names.begin(), names.end(), name);
        if (found == names.end()) {
            fail("Unknown argument: " + std::string(name.substr(0, 128)));
        }
        const auto index = static_cast<std::size_t>(found - names.begin());
        if (seen[index]) {
            fail("Duplicate argument: " + std::string(name));
        }
        seen[index] = true;
        if (++argument == argc) {
            fail("Missing value for " + std::string(name));
        }
        const std::string_view value(argv[argument]);
        if (value.empty() || value.size() > 4096 || value.starts_with("--")) {
            fail("Missing or oversized value for " + std::string(name));
        }
        if (name == "--profile") {
            options.profile = hammond::cli::argument_path(value);
        } else if (name == "--case") {
            if (value != "all" && std::find(kCases.begin(), kCases.end(), value) == kCases.end() &&
                !console_selection(value)) {
                fail("Unknown case. Use a legacy case, console_motion, owned_input, or console_all.");
            }
            options.selected_case = value;
        } else {
            const auto number = unsigned_number(value, name);
            if (name == "--seed") {
                options.seed = number;
            } else if (name == "--sample-rate") {
                if (number != 44100 && number != 48000 && number != 96000) {
                    fail("Sample rate must be 44100, 48000, or 96000 Hz.");
                }
                options.sample_rate = static_cast<std::uint32_t>(number);
            } else {
                const std::uint64_t maximum = name == "--block-size" ? hammond::kHardMaxBlockFrames :
                    (name == "--warmup" ? 1000 : kMaxCallsPerCase);
                if (number == 0 || number > maximum) {
                    fail(std::string(name) + " must be in 1.." + std::to_string(maximum) + '.');
                }
                if (name == "--block-size") {
                    options.block_size = static_cast<std::uint32_t>(number);
                } else if (name == "--iterations") {
                    options.iterations = static_cast<std::uint32_t>(number);
                } else {
                    options.warmup = static_cast<std::uint32_t>(number);
                }
            }
        }
    }
    const auto calls = static_cast<std::uint64_t>(options.iterations) + options.warmup;
    if (calls > kMaxCallsPerCase || calls * options.block_size > kMaxFramesPerCase) {
        fail("Warmup plus measured work must fit 10000 calls and 1048576 frames per case.");
    }
    return options;
}

// Diagnostics, hashing, JSON construction and all container work are outside
// the two clock reads around process. Native object bytes are not a portable
// audio fingerprint; this sink makes the observed output/state externally used.
void hash_bytes(std::uint64_t& hash, std::span<const std::byte> bytes) noexcept {
    for (const auto byte : bytes) {
        hash ^= std::to_integer<std::uint8_t>(byte);
        hash *= 1099511628211ULL;
    }
}

[[nodiscard]] std::string hash_text(std::uint64_t hash) {
    std::ostringstream text;
    text.imbue(std::locale::classic());
    text << std::hex << std::setfill('0') << std::setw(16) << hash;
    return text.str();
}

void write_string(std::ostream& output, std::string_view value) {
    constexpr char digits[] = "0123456789abcdef";
    output << '"';
    for (const char character : value) {
        const auto byte = static_cast<unsigned char>(character);
        if (byte == '"' || byte == '\\') {
            output << '\\' << character;
        } else if (byte < 0x20U || byte >= 0x7fU) {
            output << "\\u00" << digits[byte >> 4U] << digits[byte & 15U];
        } else {
            output << character;
        }
    }
    output << '"';
}

void require_result(hammond::ProcessResult result, std::size_t events,
                    std::string_view stage) {
    if (!result || result.events_consumed != events) {
        fail(std::string(stage) + " failed: " + hammond::status_name(result.status) +
             "; consumed " + std::to_string(result.events_consumed) + " events.");
    }
}

struct Result {
    std::string_view name;
    bool connected = true;
    std::size_t active_keys = 0;
    std::size_t setup_events = 0;
    std::size_t events_per_call = 0;
    std::uint64_t events_consumed = 0;
    std::uint64_t start_frame = 0;
    std::uint64_t end_frame = 0;
    std::uint64_t sample_hash = kHashBasis;
    std::uint64_t phase_hash = kHashBasis;
    double minimum_ns = 0.0;
    double median_ns = 0.0;
    double p95_ns = 0.0;
    double maximum_ns = 0.0;
    std::uint64_t physical_events_consumed = 0;
    std::uint64_t warmup_physical_events_consumed = 0;
    std::size_t start_active_keys = 0;
    std::size_t final_active_keys = 0;
    std::size_t start_owners = 0;
    std::size_t final_owners = 0;
    std::size_t max_observed_owners = 0;
    std::uint32_t motion_calls = 0;
    std::uint64_t primary_contact_edges = 0;
    double final_primary_position = 0.0;
    double final_primary_target = 0.0;
    double final_readiness = 1.0;
};

[[nodiscard]] Result run_case(const Options& options, const hammond::RuntimeProfile& profile,
                              std::string_view name) {
    Result report;
    report.name = name;
    report.connected = name != "disconnected";
    const bool held_keys = name != "silence";
    hammond::Engine engine;
    const hammond::ProcessSpec spec{static_cast<double>(options.sample_rate),
                                    options.block_size, options.seed, 0};
    const auto prepared = engine.prepare(profile, spec);
    if (prepared != hammond::Status::Ok || !engine.prepared()) {
        fail("Preparation failed: " + std::string(hammond::status_name(prepared)));
    }

    constexpr std::size_t kSetupCapacity =
        hammond::kManualCount * (hammond::kDrawbarCount + hammond::kManualKeyCount);
    std::array<hammond::Event, kSetupCapacity> setup{};
    for (const auto manual : {hammond::Manual::Upper, hammond::Manual::Lower}) {
        for (std::size_t drawbar = 0; drawbar < hammond::kDrawbarCount; ++drawbar) {
            setup[report.setup_events++] = {0, hammond::EventType::Drawbar, manual,
                                            static_cast<std::uint8_t>(drawbar), 8.0};
        }
        if (held_keys) {
            for (std::uint32_t note = hammond::kMinManualMidiNote;
                 note <= hammond::kMaxManualMidiNote; ++note) {
                setup[report.setup_events++] = {0, hammond::EventType::NoteOn, manual,
                                                static_cast<std::uint8_t>(note), 127.0};
            }
        }
    }
    require_result(engine.process(0, {}, std::span<const hammond::Event>(setup.data(), report.setup_events)),
                   report.setup_events, "Setup");
    report.active_keys = engine.active_key_count();
    const auto expected_keys = held_keys ? hammond::kManualCount * hammond::kManualKeyCount : 0;
    if (report.active_keys != expected_keys || engine.frame_clock() != 0) {
        fail("Setup produced an unexpected key count or frame clock.");
    }

    std::array<hammond::Event, hammond::kMaxEventsPerBlock> automation{};
    if (name == "dense_automation") {
        report.events_per_call = automation.size();
        for (std::size_t i = 0; i < automation.size(); ++i) {
            const auto pair = i / 2;
            const auto manual = pair % 2 == 0 ? hammond::Manual::Upper : hammond::Manual::Lower;
            // Each pair changes one selected-bank drawbar 8 -> 7 -> 8.
            // All pairs finish at 8, so repeating the prebuilt array changes
            // every event again. Ties preserve this order within a sample.
            automation[i] = {
                static_cast<std::uint32_t>(i * options.block_size / automation.size()),
                hammond::EventType::Drawbar, manual,
                static_cast<std::uint8_t>((pair / 2) % hammond::kDrawbarCount),
                i % 2 == 0 ? 7.0 : 8.0};
        }
    }
    const std::span<const hammond::Event> events(automation.data(), report.events_per_call);
    std::vector<float> storage(options.block_size, 0.0F);
    std::vector<double> durations(options.iterations, 0.0);
    const auto output = report.connected ? std::span<float>(storage) : std::span<float>{};

    for (std::uint32_t call = 0; call < options.warmup; ++call) {
        require_result(engine.process(options.block_size, output, events), events.size(), "Warmup");
    }
    report.start_frame = engine.frame_clock();
    for (std::size_t call = 0; call < durations.size(); ++call) {
        const auto begin = Clock::now();
        const auto result = engine.process(options.block_size, output, events);
        const auto end = Clock::now();
        durations[call] = std::chrono::duration<double, std::nano>(end - begin).count();

        require_result(result, events.size(), "Recorded process");
        report.events_consumed += result.events_consumed;
        for (const auto sample : output) {
            if (!std::isfinite(sample)) {
                fail("Recorded process produced a nonfinite output sample.");
            }
        }
        hash_bytes(report.sample_hash, std::as_bytes(output));
    }
    report.end_frame = engine.frame_clock();
    const auto expected_start = static_cast<std::uint64_t>(options.warmup) * options.block_size;
    const auto expected_frames = static_cast<std::uint64_t>(options.iterations) * options.block_size;
    if (report.start_frame != expected_start || report.end_frame - report.start_frame != expected_frames ||
        report.events_consumed != static_cast<std::uint64_t>(options.iterations) * events.size()) {
        fail("Recorded process counts do not match the requested workload.");
    }
    for (std::uint32_t id = hammond::kMinToneId; id <= hammond::kMaxToneId; ++id) {
        double phase = 0.0;
        if (!engine.source_phase_turns(static_cast<hammond::ToneId>(id), phase) || !std::isfinite(phase)) {
            fail("Final source phase is unavailable or nonfinite.");
        }
        hash_bytes(report.phase_hash, std::as_bytes(std::span<const double>(&phase, 1)));
    }
    std::sort(durations.begin(), durations.end());
    report.minimum_ns = durations.front();
    const auto middle = durations.size() / 2;
    report.median_ns = durations.size() % 2 == 0 ?
        (durations[middle - 1] + durations[middle]) / 2.0 : durations[middle];
    report.p95_ns = durations[(durations.size() * 95 + 99) / 100 - 1];
    report.maximum_ns = durations.back();
    return report;
}

[[nodiscard]] Result run_console_case(const Options& options,
                                      const hammond::RuntimeProfile& profile,
                                      std::string_view name) {
    Result report;
    report.name = name;
    report.events_per_call = kConsoleKeys;
    const bool owned = name == "owned_input";
    hammond::Engine engine;
    hammond::NoteOwnership ownership;
    const hammond::ProcessSpec spec{static_cast<double>(options.sample_rate),
                                    options.block_size, options.seed, 0};
    const auto prepared = engine.prepare(profile, spec, hammond::make_nominal_console_model());
    if (prepared != hammond::Status::Ok || !engine.prepared()) {
        fail("Console preparation failed: " + std::string(hammond::status_name(prepared)));
    }

    std::array<hammond::Event, hammond::kManualCount * hammond::kDrawbarCount + 4> setup{};
    for (const auto manual : {hammond::Manual::Upper, hammond::Manual::Lower}) {
        for (std::size_t drawbar = 0; drawbar < hammond::kDrawbarCount; ++drawbar) {
            setup[report.setup_events++] = {0, hammond::EventType::Drawbar, manual,
                                            static_cast<std::uint8_t>(drawbar), 8.0};
        }
    }
    for (std::uint8_t index = 0; index < 4; ++index) {
        setup[report.setup_events++] = {0, hammond::EventType::Percussion,
            hammond::Manual::Upper, index, index == 0 || index == 3 ? 1.0 : 0.0};
    }
    require_result(engine.process(0, {}, setup), setup.size(), "Console setup");
    if (engine.active_key_count() != 0 || engine.frame_clock() != 0) {
        fail("Console setup unexpectedly advanced time or held a key.");
    }

    // Every event array and view is constructed outside the timed invocation.
    // Ownership uses two identified owners per physical key and never mixes
    // direct note commands with the transactional facade.
    std::array<std::array<hammond::Event, kConsoleKeys>, 2> targets{};
    std::array<std::array<hammond::HostNoteEvent, kConsoleKeys>, 4> notes{};
    for (std::size_t key = 0; key < kConsoleKeys; ++key) {
        const auto bus = static_cast<std::uint8_t>(key / hammond::kManualKeyCount);
        const auto manual = bus == 0 ? hammond::Manual::Upper : hammond::Manual::Lower;
        const auto note = static_cast<std::uint8_t>(hammond::kMinManualMidiNote +
                                                   key % hammond::kManualKeyCount);
        for (std::size_t phase = 0; phase < targets.size(); ++phase) {
            targets[phase][key] = {0, hammond::EventType::KeyPosition, manual, note,
                                   phase == 0 ? 1.0 : 0.0};
        }
        for (std::size_t phase = 0; phase < notes.size(); ++phase) {
            notes[phase][key] = {0, phase < 2 ? hammond::HostNoteKind::On :
                hammond::HostNoteKind::Off, bus, static_cast<std::uint8_t>(phase % 2), note,
                static_cast<std::uint8_t>(phase < 2 ? 100 : 0), static_cast<std::int32_t>(key)};
        }
    }
    std::vector<float> storage(options.block_size, 0.0F);
    std::vector<double> durations(options.iterations, 0.0);
    const std::span<float> output(storage);
    const auto invoke = [&](std::uint64_t call, double* duration) {
        std::array<std::uint32_t, 2> counts{};
        if (owned) {
            const std::span<const hammond::HostNoteEvent> events(notes[call % notes.size()]);
            hammond::InputProcessResult result;
            if (duration != nullptr) {
                const auto begin = Clock::now();
                result = hammond::process_owned_notes(engine, ownership, options.block_size, output, events);
                const auto end = Clock::now();
                *duration = std::chrono::duration<double, std::nano>(end - begin).count();
            } else {
                result = hammond::process_owned_notes(engine, ownership, options.block_size, output, events);
            }
            const auto expected_physical = call % 4 == 0 || call % 4 == 3 ? kConsoleKeys : 0;
            if (!result || result.host_events_consumed != events.size() ||
                result.physical_events_consumed != expected_physical) {
                fail("Owned-input call failed or consumed unexpected input/physical events.");
            }
            counts = {result.host_events_consumed, result.physical_events_consumed};
        } else {
            const std::span<const hammond::Event> events(targets[call % targets.size()]);
            hammond::ProcessResult result;
            if (duration != nullptr) {
                const auto begin = Clock::now();
                result = engine.process(options.block_size, output, events);
                const auto end = Clock::now();
                *duration = std::chrono::duration<double, std::nano>(end - begin).count();
            } else {
                result = engine.process(options.block_size, output, events);
            }
            require_result(result, events.size(), "Console motion");
            counts = {result.events_consumed, result.events_consumed};
        }
        const std::size_t expected_owners = owned ?
            std::array<std::size_t, 4>{kConsoleKeys, 2 * kConsoleKeys, kConsoleKeys, 0}[call % 4] : 0;
        const bool down = owned ? call % 4 != 3 : call % 2 == 0;
        if (ownership.owner_count() != expected_owners ||
            engine.active_key_count() != (down ? kConsoleKeys : 0)) {
            fail("Console workload produced unexpected owners or physical targets.");
        }
        report.max_observed_owners = std::max(report.max_observed_owners, ownership.owner_count());
        return counts;
    };
    for (std::uint32_t call = 0; call < options.warmup; ++call) {
        report.warmup_physical_events_consumed += invoke(call, nullptr)[1];
    }
    report.start_frame = engine.frame_clock();
    report.start_owners = ownership.owner_count();
    report.start_active_keys = engine.active_key_count();
    hammond::ContactKeySnapshot before;
    hammond::ContactKeySnapshot after;
    for (std::size_t call = 0; call < durations.size(); ++call) {
        if (!engine.contact_snapshot(hammond::Manual::Upper, 60, before)) {
            fail("Primary contact diagnostic is unavailable.");
        }
        const auto counts = invoke(static_cast<std::uint64_t>(options.warmup) + call, &durations[call]);
        report.events_consumed += counts[0];
        report.physical_events_consumed += counts[1];
        if (!engine.contact_snapshot(hammond::Manual::Upper, 60, after) ||
            !std::isfinite(after.position) || !std::isfinite(after.target)) {
            fail("Primary contact diagnostic is unavailable or nonfinite.");
        }
        if (before.position != after.position) ++report.motion_calls;
        for (std::size_t contact = 0; contact < after.closed.size(); ++contact) {
            if (before.closed[contact] != after.closed[contact]) ++report.primary_contact_edges;
        }
        for (const auto sample : output) {
            if (!std::isfinite(sample)) fail("Console process produced a nonfinite sample.");
        }
        hash_bytes(report.sample_hash, std::as_bytes(output));
    }
    report.end_frame = engine.frame_clock();
    report.final_owners = ownership.owner_count();
    report.final_active_keys = engine.active_key_count();
    report.final_primary_position = after.position;
    report.final_primary_target = after.target;
    report.final_readiness = engine.percussion_diagnostics().readiness;
    const auto expected_start = static_cast<std::uint64_t>(options.warmup) * options.block_size;
    const auto expected_frames = static_cast<std::uint64_t>(options.iterations) * options.block_size;
    if (report.start_frame != expected_start || report.end_frame - report.start_frame != expected_frames ||
        report.events_consumed != static_cast<std::uint64_t>(options.iterations) * kConsoleKeys ||
        !std::isfinite(report.final_readiness) || report.final_readiness < 0 || report.final_readiness > 1) {
        fail("Console work counts or readiness disagree with the workload contract.");
    }
    for (std::uint32_t id = hammond::kMinToneId; id <= hammond::kMaxToneId; ++id) {
        double phase = 0.0;
        if (!engine.source_phase_turns(static_cast<hammond::ToneId>(id), phase) || !std::isfinite(phase)) {
            fail("Final source phase is unavailable or nonfinite.");
        }
        hash_bytes(report.phase_hash, std::as_bytes(std::span<const double>(&phase, 1)));
    }
    std::sort(durations.begin(), durations.end());
    report.minimum_ns = durations.front();
    const auto middle = durations.size() / 2;
    report.median_ns = durations.size() % 2 == 0 ?
        (durations[middle - 1] + durations[middle]) / 2.0 : durations[middle];
    report.p95_ns = durations[(durations.size() * 95 + 99) / 100 - 1];
    report.maximum_ns = durations.back();
    return report;
}

void write_report(const Options& options, const hammond::RuntimeProfile& profile,
                  std::span<const Result> reports) {
    std::cout.imbue(std::locale::classic());
    std::cout << std::setprecision(std::numeric_limits<double>::max_digits10) << std::boolalpha;
    const double interval_ns = static_cast<double>(options.block_size) * 1.0e9 / options.sample_rate;
    const bool console = console_selection(options.selected_case);
    std::cout << "{\"schema\":";
    write_string(std::cout, console ? "hammond-console-benchmark-v1" : "hammond-benchmark-v1");
    std::cout << ",\"status\":\"ok\",\"scope\":";
    write_string(std::cout, console ?
        "observed elapsed wall-clock intervals around nominal Engine and owned-input calls" :
        "observed elapsed wall-clock intervals around prepared Engine::process calls");
    std::cout << ",\"hard_realtime_guarantee\":false,\"timing_threshold_applied\":false,"
        "\"clock\":\"std::chrono::steady_clock\",\"clock_is_steady\":" << Clock::is_steady
        << ",\"clock_tick_seconds\":" << static_cast<double>(Clock::period::num) / Clock::period::den
        << ",\"timer_overhead_subtracted\":false,\"warmup_included_in_timings\":false,"
        "\"build\":{\"configuration\":";
    write_string(std::cout, HAMMOND_BENCHMARK_CONFIGURATION);
    std::cout << ",\"compiler_id\":";
    write_string(std::cout, HAMMOND_BENCHMARK_COMPILER_ID);
    std::cout << ",\"compiler_version\":";
    write_string(std::cout, HAMMOND_BENCHMARK_COMPILER_VERSION);
    std::cout << ",\"target_system\":";
    write_string(std::cout, HAMMOND_BENCHMARK_TARGET_SYSTEM);
    std::cout << ",\"target_processor\":";
    write_string(std::cout, HAMMOND_BENCHMARK_TARGET_PROCESSOR);
#ifdef NDEBUG
    constexpr bool ndebug = true;
#else
    constexpr bool ndebug = false;
#endif
    std::cout << ",\"cplusplus\":" << __cplusplus << ",\"ndebug\":" << ndebug
        << ",\"project_sanitizers_enabled\":" << (HAMMOND_BENCHMARK_SANITIZERS != 0)
        << ",\"source_revision\":null,\"binary_sha256\":null},"
        "\"runtime_machine\":null,\"host_underruns\":null,\"profile_id\":";
    write_string(std::cout, profile.profile_id.data());
    std::cout << ",\"profile_authoring_sha256_retained\":";
    write_string(std::cout, profile.authoring_sha256.data());
    std::cout << ",\"sample_rate_hz\":" << options.sample_rate
        << ",\"block_frames\":" << options.block_size << ",\"seed\":" << options.seed
        << ",\"recorded_calls_per_case\":" << options.iterations
        << ",\"warmup_calls_per_case\":" << options.warmup
        << ",\"nominal_frame_interval_ns\":" << interval_ns
        << ",\"checksum_encoding\":\"fnv1a64 over native object bytes; same-build diagnostic sink\"";
    if (console) {
        std::cout << ",\"source_model\":\"ideal-shared-sine-v1\",\"contact_model\":";
        write_string(std::cout, hammond::kNominalContactModelId);
        std::cout << ",\"percussion_model\":";
        write_string(std::cout, hammond::kPercussionModelId);
        std::cout << ",\"ownership_model\":";
        write_string(std::cout, hammond::kNoteOwnershipModelId);
        std::cout << ",\"workload_version\":1";
    }
    std::cout << ",\"cases\":[";
    bool first = true;
    for (const auto& report : reports) {
        if (!first) {
            std::cout << ',';
        }
        first = false;
        std::cout << "{\"name\":";
        write_string(std::cout, report.name);
        std::cout << ",\"output_connected\":" << report.connected
            << ",\"active_keys\":" << report.active_keys
            << ",\"initial_selected_bank_drawbars\":\"888888888 on each manual\","
            "\"prepare_status\":\"ok\",\"setup_status\":\"ok\",\"setup_events_consumed\":" << report.setup_events
            << ",\"warmup_ok_calls\":" << options.warmup << ",\"recorded_status_counts\":{\"ok\":"
            << options.iterations << "},\"recorded_rejected_calls\":0,\"recorded_calls\":" << options.iterations
            << ",\"processed_frames\":" << report.end_frame - report.start_frame
            << ",\"start_frame\":" << report.start_frame << ",\"end_frame\":" << report.end_frame
            << ",\"events_per_call\":" << report.events_per_call
            << ",\"event_offsets_per_call\":" << (console ? 1 :
                std::min<std::size_t>(options.block_size, report.events_per_call))
            << ",\"events_consumed\":" << report.events_consumed << ",\"call_time_ns\":{\"min\":" << report.minimum_ns
            << ",\"median\":" << report.median_ns << ",\"p95\":" << report.p95_ns << ",\"max\":" << report.maximum_ns
            << "},\"observed_p95_interval_fraction\":" << report.p95_ns / interval_ns
            << ",\"observed_max_interval_fraction\":" << report.maximum_ns / interval_ns
            << ",\"sample_checksum\":";
        if (report.connected) {
            write_string(std::cout, hash_text(report.sample_hash));
        } else {
            std::cout << "null";
        }
        std::cout << ",\"final_source_phase_checksum\":";
        write_string(std::cout, hash_text(report.phase_hash));
        if (console) {
            const bool owned = report.name == "owned_input";
            std::cout << ",\"timed_api\":";
            write_string(std::cout, owned ? "process_owned_notes" : "Engine::process");
            std::cout << ",\"input_event_domain\":";
            write_string(std::cout, owned ? "typed_host_notes" : "physical_key_targets");
            std::cout << ",\"initial_percussion\":\"on_second_normal_fast\","
                "\"initial_owner_count\":0,\"start_owner_count\":" << report.start_owners
                << ",\"final_owner_count\":" << report.final_owners
                << ",\"max_observed_owner_count\":" << report.max_observed_owners
                << ",\"workload_owner_bound\":" << (owned ? 2 * kConsoleKeys : 0)
                << ",\"start_active_keys\":" << report.start_active_keys
                << ",\"final_active_keys\":" << report.final_active_keys
                << ",\"physical_events_consumed\":" << report.physical_events_consumed
                << ",\"warmup_events_consumed\":" << static_cast<std::uint64_t>(options.warmup) * kConsoleKeys
                << ",\"warmup_physical_events_consumed\":" << report.warmup_physical_events_consumed
                << ",\"primary_key_midi\":60,\"primary_key_manual\":\"upper\","
                "\"recorded_primary_motion_calls\":" << report.motion_calls
                << ",\"recorded_primary_contact_edges\":" << report.primary_contact_edges
                << ",\"final_primary_position\":" << report.final_primary_position
                << ",\"final_primary_target\":" << report.final_primary_target
                << ",\"final_readiness\":" << report.final_readiness;
        }
        std::cout << '}';
    }
    std::cout << "]}\n";
    std::cout.flush();
    if (!std::cout) {
        fail("Cannot write JSON report to stdout.");
    }
}

int benchmark(const Options& options) {
    std::error_code error;
    if (!std::filesystem::is_regular_file(options.profile, error) || error) {
        fail("Profile must name a readable regular file.");
    }
    hammond::RuntimeProfile profile;
    std::string load_error;
    if (!hammond::load_runtime_profile_file(options.profile, profile, load_error)) {
        fail("Cannot load profile: " + load_error);
    }
    std::array<Result, kCases.size()> reports{};
    std::size_t count = 0;
    if (console_selection(options.selected_case)) {
        for (const auto name : kConsoleCases) {
            if (options.selected_case == "console_all" || options.selected_case == name) {
                reports[count++] = run_console_case(options, profile, name);
            }
        }
    } else {
        for (const auto name : kCases) {
            if (options.selected_case == "all" || options.selected_case == name) {
                reports[count++] = run_case(options, profile, name);
            }
        }
    }
    write_report(options, profile, std::span<const Result>(reports.data(), count));
    return 0;
}

} // namespace

static int benchmark_main(int argc, char* argv[]) {
    try {
        if (argc == 2 && std::string_view(argv[1]) == "--help") {
            std::cout <<
                "Usage: hammond_benchmark [options]\n"
                "  --profile FILE                (default: this build's nominal.b3p)\n"
                "  --sample-rate 44100|48000|96000 (default 48000)\n"
                "  --block-size 1..65536          (default 64)\n"
                "  --iterations 1..10000          (recorded calls per case; default 128)\n"
                "  --warmup 1..1000               (unrecorded calls per case; default 16)\n"
                "  --seed UNSIGNED64              (default 0)\n"
                "  --case all|silence|all_keys|disconnected|dense_automation (default all)\n"
                "         console_motion|owned_input|console_all (explicit nominal workloads)\n"
                "Warmup + recorded work: at most 10000 calls and 1048576 frames per case.\n"
                "Output: JSON wall-clock observations; no real-time guarantee or timing pass/fail.\n";
            std::cout.flush();
            if (!std::cout) fail("Cannot write help output to stdout.");
            return 0;
        }
        return benchmark(parse_options(argc, argv));
    } catch (const std::exception& error) {
        std::cerr << "hammond_benchmark: " << error.what() << '\n';
        return 1;
    } catch (...) {
        std::cerr << "hammond_benchmark: unknown failure.\n";
        return 1;
    }
}

#ifdef _WIN32
int wmain(int argc, wchar_t* argv[]) {
    return hammond::cli::run_windows(argc, argv, benchmark_main, "hammond_benchmark");
}
#else
int main(int argc, char* argv[]) {
    return benchmark_main(argc, argv);
}
#endif
