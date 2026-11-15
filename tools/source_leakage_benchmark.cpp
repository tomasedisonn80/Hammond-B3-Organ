#include "CliArguments.h"
#include "hammond/Engine.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cfenv>
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

#ifdef _WIN32
#include <cstdio>
#include <fcntl.h>
#include <io.h>
#endif

#ifndef HAMMOND_BENCHMARK_CONFIGURATION
#define HAMMOND_BENCHMARK_CONFIGURATION "unspecified"
#define HAMMOND_BENCHMARK_COMPILER_ID "unspecified"
#define HAMMOND_BENCHMARK_COMPILER_VERSION "unspecified"
#define HAMMOND_BENCHMARK_TARGET_SYSTEM "unspecified"
#define HAMMOND_BENCHMARK_TARGET_PROCESSOR "unspecified"
#define HAMMOND_BENCHMARK_SANITIZERS 0
#endif

namespace {
using namespace hammond;
using Clock = std::chrono::steady_clock;
constexpr std::uint32_t kBlock = 64, kWarmupBlocks = 16;
constexpr std::size_t kMaximumRepetitions = 9, kRowCount = 19;
constexpr std::uint64_t kHashBasis = 14695981039346656037ULL;
constexpr std::uint64_t kHashPrime = 1099511628211ULL;
constexpr std::array<std::string_view, 4> kNames{
    "unconfigured", "empty-gain-one", "pair-gain-0.75", "maximum-728-gain-0.5"};
constexpr std::array<std::string_view, 3> kGraphNames{"empty", "pair", "maximum-728"};
constexpr std::array<double, 4> kGains{1.0, 1.0, 0.75, 0.5};

[[noreturn]] void fail(const std::string& message) { throw std::runtime_error(message); }
void require(bool condition, const char* message) { if (!condition) fail(message); }
void ok(Status status, const char* operation) {
    if (status != Status::Ok) fail(std::string(operation) + ": " + status_name(status));
}
void process_ok(ProcessResult result, std::size_t events = 0) {
    ok(result.status, "Engine processing");
    require(result.events_consumed == events, "Unexpected event count.");
}
void budget(Clock::time_point started) {
    // Checked outside each timed block. This is a cooperative work limit,
    // not a scheduling guarantee on an arbitrarily stalled operating system.
    require(Clock::now() - started < std::chrono::seconds(50),
            "Shared-runner wall budget exceeded; reduce --blocks or --repetitions.");
}
void quoted(std::ostream& output, std::string_view value) {
    constexpr std::string_view hex = "0123456789abcdef";
    output << '"';
    for (const char character : value) {
        const auto byte = static_cast<unsigned char>(character);
        if (character == '"' || character == '\\') output << '\\' << character;
        else if (byte < 0x20U || byte >= 0x7fU)
            output << "\\u00" << hex[byte >> 4U] << hex[byte & 15U];
        else output << character;
    }
    output << '"';
}
std::string hash_text(std::uint64_t hash) {
    std::ostringstream text;
    text.imbue(std::locale::classic());
    text << std::hex << std::setfill('0') << std::setw(16) << hash;
    return text.str();
}

struct Options {
    std::filesystem::path profile;
    std::uint32_t sample_rate{48000}, blocks{256};
    std::size_t repetitions{5};
    std::uint64_t seed{739};
};
std::uint64_t number(std::string_view text) {
    require(!text.empty() && text.size() <= 20 &&
            std::all_of(text.begin(), text.end(), [](char c) { return c >= '0' && c <= '9'; }),
            "Numeric arguments require 1..20 decimal digits.");
    std::uint64_t value = 0;
    const auto parsed = std::from_chars(text.data(), text.data() + text.size(), value);
    require(parsed.ec == std::errc{} && parsed.ptr == text.data() + text.size(),
            "Numeric argument is out of range.");
    return value;
}
Options options(int argc, char* argv[]) {
    constexpr std::array<std::string_view, 5> names{
        "--profile", "--sample-rate", "--blocks", "--repetitions", "--seed"};
    require(argc >= 3 && argc <= 11, "Require --profile FILE; use --help for bounded options.");
    Options result;
    std::array<bool, names.size()> seen{};
    for (int index = 1; index < argc; ++index) {
        const std::string_view name(argv[index]);
        const auto found = std::find(names.begin(), names.end(), name);
        require(found != names.end(), "Unknown benchmark argument.");
        const auto slot = static_cast<std::size_t>(found - names.begin());
        require(!seen[slot], "Duplicate benchmark argument.");
        seen[slot] = true;
        require(++index < argc, "Missing benchmark argument value.");
        const std::string_view value(argv[index]);
        require(!value.empty() && value.size() <= 32768 && !value.starts_with("--"),
                "Missing or oversized benchmark value.");
        if (slot == 0) result.profile = cli::argument_path(value);
        else {
            const auto parsed = number(value);
            if (slot == 1) {
                require(parsed == 44100 || parsed == 48000 || parsed == 96000,
                        "Sample rate must be 44100, 48000 or 96000.");
                result.sample_rate = static_cast<std::uint32_t>(parsed);
            } else if (slot == 2) {
                require(parsed >= 1 && parsed <= 512, "Blocks must be in 1..512.");
                result.blocks = static_cast<std::uint32_t>(parsed);
            } else if (slot == 3) {
                require(parsed >= 1 && parsed <= kMaximumRepetitions,
                        "Repetitions must be in 1..9.");
                result.repetitions = static_cast<std::size_t>(parsed);
            } else result.seed = parsed;
        }
    }
    require(seen[0], "--profile FILE is required.");
    std::error_code error;
    result.profile = std::filesystem::canonical(result.profile, error);
    require(!error && std::filesystem::is_regular_file(result.profile, error) && !error,
            "Profile must be an existing regular file.");
    const auto size = std::filesystem::file_size(result.profile, error);
    require(!error && size <= kMaxCompiledProfileBytes, "Profile exceeds the 128 KiB limit.");
    return result;
}

struct Graphs {
    std::array<SourceLeakage, 3> values{};
    Graphs() {
        ok(values[0].prepare({}), "empty graph");
        const std::array pair{SourceLeakageEdge{37, 25, 0.0625},
                              SourceLeakageEdge{25, 37, -0.03125}};
        ok(values[1].prepare(pair), "pair graph");
        std::array<SourceLeakageEdge, kMaxSourceLeakageEdges> maximum{};
        std::size_t next = 0;
        for (std::size_t d = 0; d < kToneSourceCount; ++d)
            for (std::size_t j = 1; j <= 8; ++j)
                maximum[next++] = {
                    static_cast<ToneId>((d + j) % kToneSourceCount + 1),
                    static_cast<ToneId>(d + 1), j % 2 == 0 ? 0.0625 : -0.0625};
        ok(values[2].prepare(maximum), "maximum graph");
    }
};
struct Observation {
    std::uint64_t hash{kHashBasis};
    double peak{};
    void sample(double value, std::uint64_t bits) {
        require(std::isfinite(value), "Nonfinite observed sample.");
        hash = (hash ^ bits) * kHashPrime; // Word checksum, not a byte-file digest.
        peak = std::max(peak, std::abs(value));
    }
};
struct Trial {
    double nanoseconds{}, phase{};
    Observation timed{}, warmup{};
};
struct Row {
    bool engine{}, nominal{}, polyphony{};
    std::size_t selection{};
    std::array<double, kMaximumRepetitions> nanoseconds_per_frame{};
    Trial observation{};
};
std::array<Row, kRowCount> rows() {
    std::array<Row, kRowCount> result{};
    for (std::size_t index = 0; index < 3; ++index) result[index].selection = index + 1;
    std::size_t index = 3;
    for (const bool nominal : {false, true})
        for (const bool polyphony : {false, true})
            for (std::size_t selection = 0; selection < kNames.size(); ++selection)
                result[index++] = {true, nominal, polyphony, selection, {}, {}};
    return result;
}
std::uint64_t random_word(std::uint64_t& state) {
    state ^= state << 13U; state ^= state >> 7U; state ^= state << 17U;
    return state;
}
Trial core_trial(const Options& option, const SourceLeakage& graph, Clock::time_point started) {
    std::array<SourceLeakageFrame, kBlock> input{}, output{};
    std::uint64_t random = option.seed ^ 0x9e3779b97f4a7c15ULL;
    if (random == 0) random = 1;
    Trial result;
    for (std::uint32_t block = 0; block < option.blocks + kWarmupBlocks; ++block) {
        budget(started);
        for (auto& frame : input) for (double& value : frame)
            value = static_cast<double>(static_cast<int>(random_word(random) & 65535U) - 32768) / 65536.0;
        Status status = Status::Ok;
        const auto begin = Clock::now();
        for (std::size_t frame = 0; frame < input.size(); ++frame) {
            const auto current = graph.process_frame(input[frame], output[frame]);
            if (current != Status::Ok) status = current;
        }
        const auto end = Clock::now();
        ok(status, "core frame");
        const bool measured = block >= kWarmupBlocks;
        if (measured) result.nanoseconds += std::chrono::duration<double, std::nano>(end - begin).count();
        auto& observed = measured ? result.timed : result.warmup;
        for (const auto& frame : output) for (const double value : frame)
            observed.sample(value, std::bit_cast<std::uint64_t>(value));
    }
    return result;
}
Trial engine_trial(const Options& option, const Graphs& graphs, const Row& row,
                   const RuntimeProfile& profile, Clock::time_point started) {
    Engine engine;
    ok(engine.prepare(profile, {static_cast<double>(option.sample_rate), kBlock, option.seed, 0},
                      row.nominal ? make_nominal_console_model() : make_legacy_console_model()), "prepare");
    if (row.selection != 0)
        ok(engine.set_source_leakage(graphs.values[row.selection - 1], kGains[row.selection]), "install");
    std::array<Event, 256> setup{};
    std::size_t count = 0;
    for (const auto manual : {Manual::Upper, Manual::Lower}) {
        for (std::size_t drawbar = 0; drawbar < kDrawbarCount; ++drawbar)
            setup[count++] = {0, EventType::Drawbar, manual, static_cast<std::uint8_t>(drawbar), 8.0};
    }
    setup[count++] = {0, EventType::Expression, Manual::Upper, 0, 0.5};
    setup[count++] = {0, EventType::Percussion, Manual::Upper, 0, 1.0};
    setup[count++] = {0, EventType::PedalDrawbar, Manual::Lower, 0, 8.0};
    setup[count++] = {0, EventType::PedalDrawbar, Manual::Lower, 1, 8.0};
    if (row.polyphony) {
        for (const auto manual : {Manual::Upper, Manual::Lower})
            for (std::uint32_t note = kMinManualMidiNote; note <= kMaxManualMidiNote; ++note)
                setup[count++] = {0, EventType::NoteOn, manual, static_cast<std::uint8_t>(note), 127.0};
        for (std::size_t pedal = 1; pedal <= kPedalCount; ++pedal)
            setup[count++] = {0, EventType::PedalOn, Manual::Lower, static_cast<std::uint8_t>(pedal), 127.0};
    }
    process_ok(engine.process(0, {}, std::span<const Event>(setup.data(), count)), count);
    require(engine.active_key_count() == (row.polyphony ? 122U : 0U) &&
            engine.active_pedal_count() == (row.polyphony ? 25U : 0U), "Incorrect benchmark note inventory.");
    Trial result;
    std::array<float, kBlock> output{};
    for (std::uint32_t block = 0; block < option.blocks + kWarmupBlocks; ++block) {
        budget(started);
        const auto begin = Clock::now();
        const auto status = engine.process(kBlock, output, {});
        const auto end = Clock::now();
        process_ok(status);
        const bool measured = block >= kWarmupBlocks;
        if (measured) result.nanoseconds += std::chrono::duration<double, std::nano>(end - begin).count();
        auto& observed = measured ? result.timed : result.warmup;
        for (const float value : output)
            observed.sample(static_cast<double>(value), std::bit_cast<std::uint32_t>(value));
        if (block + 1 == kWarmupBlocks && row.polyphony) {
            for (const auto manual : {Manual::Upper, Manual::Lower})
                for (std::uint32_t note = kMinManualMidiNote; note <= kMaxManualMidiNote; ++note) {
                    ContactKeySnapshot snapshot;
                    require(engine.contact_snapshot(manual, note, snapshot) && snapshot.position == 1.0 &&
                            std::all_of(snapshot.closed.begin(), snapshot.closed.end(), [](bool v) { return v; }),
                            "Warm-up did not settle the nominal contacts.");
                }
        }
    }
    require(engine.frame_clock() == static_cast<std::uint64_t>(option.blocks + kWarmupBlocks) * kBlock,
            "Unexpected final frame clock.");
    require(engine.source_phase_turns(1, result.phase), "Missing actual source phase.");
    require(row.polyphony ? result.timed.peak > 0.0 : result.timed.peak == 0.0,
            "Expected finite audible polyphony or exact silence; use a nonzero profile.");
    return result;
}
double median(const Row& row, std::size_t repetitions) {
    auto values = row.nanoseconds_per_frame;
    require(repetitions >= 1 && repetitions <= values.size(), "Invalid median sample count.");
    // At most nine values: explicit bounded insertion avoids libstdc++ sort's
    // larger internal insertion threshold and its optimized array-bounds warning.
    for (std::size_t index = 1; index < repetitions; ++index) {
        const double value = values[index];
        std::size_t destination = index;
        while (destination > 0 && values[destination - 1] > value) {
            values[destination] = values[destination - 1];
            --destination;
        }
        values[destination] = value;
    }
    const auto center = repetitions / 2;
    return repetitions % 2 ? values[center] : (values[center - 1] + values[center]) / 2.0;
}
std::string benchmark(const Options& option) {
    require(std::fegetround() == FE_TONEAREST, "Benchmark requires round-to-nearest arithmetic.");
    volatile double tiny = std::numeric_limits<double>::denorm_min();
    require(std::bit_cast<std::uint64_t>(tiny + tiny) == 2, "Benchmark requires gradual underflow.");
    RuntimeProfile profile;
    std::string error;
    if (!load_runtime_profile_file(option.profile, profile, error)) fail("Cannot load profile: " + error);
    const auto started = Clock::now();
    const Graphs graphs;
    auto results = rows();
    const double frames = static_cast<double>(option.blocks) * kBlock;
    for (std::size_t repetition = 0; repetition < option.repetitions; ++repetition) {
        for (std::size_t offset = 0; offset < results.size(); ++offset) {
            auto& row = results[(offset + repetition * 7) % results.size()];
            const auto current = row.engine ?
                engine_trial(option, graphs, row, profile, started) :
                core_trial(option, graphs.values[row.selection - 1], started);
            require(std::isfinite(current.nanoseconds) && current.nanoseconds > 0.0,
                    "Clock resolution did not produce a positive finite observation.");
            if (repetition != 0) require(
                current.timed.hash == row.observation.timed.hash &&
                current.warmup.hash == row.observation.warmup.hash &&
                current.timed.peak == row.observation.timed.peak &&
                std::bit_cast<std::uint64_t>(current.phase) == std::bit_cast<std::uint64_t>(row.observation.phase),
                "Repeated deterministic workload changed its observed data.");
            row.nanoseconds_per_frame[repetition] = current.nanoseconds / frames;
            row.observation = current;
        }
    }
    for (std::size_t base = 3; base < results.size(); base += 4)
        require(results[base].observation.timed.hash == results[base + 1].observation.timed.hash &&
                results[base].observation.warmup.hash == results[base + 1].observation.warmup.hash &&
                results[base].observation.phase == results[base + 1].observation.phase,
                "Default/empty-gain-one benchmark checksums or phase differ.");
    require(results[0].observation.timed.hash != results[1].observation.timed.hash &&
            results[0].observation.timed.hash != results[2].observation.timed.hash,
            "Nonempty core workload did not produce distinct data.");

    std::ostringstream out;
    out.imbue(std::locale::classic());
    out << std::setprecision(std::numeric_limits<double>::max_digits10)
        << "{\"schema_version\":1,\"benchmark\":\"source-leakage-cost-v1\",\"status\":\"completed\","
           "\"sanity_passed\":true,\"configuration\":";
    quoted(out, HAMMOND_BENCHMARK_CONFIGURATION);
    out << ",\"compiler_id\":"; quoted(out, HAMMOND_BENCHMARK_COMPILER_ID);
    out << ",\"compiler_version\":"; quoted(out, HAMMOND_BENCHMARK_COMPILER_VERSION);
    out << ",\"target_system\":"; quoted(out, HAMMOND_BENCHMARK_TARGET_SYSTEM);
    out << ",\"target_processor\":"; quoted(out, HAMMOND_BENCHMARK_TARGET_PROCESSOR);
    out << ",\"sanitizers\":" << (HAMMOND_BENCHMARK_SANITIZERS ? "true" : "false")
        << ",\"profile_id\":"; quoted(out, profile.profile_id.data());
    out << ",\"declared_authoring_sha256\":"; quoted(out, profile.authoring_sha256.data());
    out << ",\"profile_digest_verification\":\"file-supplied-unverified\","
           "\"clock\":\"steady_clock\",\"clock_call_overhead_included\":true,"
           "\"timed_region\":\"64 core frame calls with status branches, or one Engine block call\","
           "\"preparation_timed\":false,\"input_generation_timed\":false,\"checksum_timed\":false,"
           "\"note_events_timed\":false,\"warmup_blocks\":" << kWarmupBlocks
        << ",\"block_frames\":" << kBlock << ",\"blocks_per_trial\":" << option.blocks
        << ",\"measured_frames_per_trial\":" << option.blocks * kBlock
        << ",\"repetitions\":" << option.repetitions << ",\"sample_rate\":" << option.sample_rate
        << ",\"seed\":" << option.seed << ",\"row_order\":\"(offset+7*repetition)%19\","
           "\"core_input\":\"seed xor0x9e3779b97f4a7c15,zero->1;xorshift64(13,7,17);low16 centered/65536;fresh[-0.5,0.5) inputs\","
           "\"pair_edges\":\"37->25:+1/16;25->37:-1/32\","
           "\"maximum_edges\":\"destination d=1..91;source=((d-1+j)%91)+1;j=1..8;odd:-1/16,even:+1/16\","
           "\"polyphony\":\"122 manual keys plus25 pedals;selected B drawbars888888888;"
           "both pedal mixtures8;expression0.5;percussion on/second/normal/slow\","
           "\"floating_point\":\"round-to-nearest and gradual underflow checked\","
           "\"identity_checksums_match\":true,\"source_leakage_bytes\":" << sizeof(SourceLeakage)
        << ",\"engine_bytes\":" << sizeof(Engine)
        << ",\"stack_high_water_measured\":false,\"callback_deadlines_measured\":false,"
           "\"shared_runner_pinning_and_frequency_control\":\"not performed\","
           "\"limits\":\"Synthetic offline workload; timing is not a CTest gate or physical/host/device qualification\","
           "\"elapsed_seconds\":" << std::chrono::duration<double>(Clock::now() - started).count()
        << ",\"rows\":[";
    for (std::size_t index = 0; index < results.size(); ++index) {
        if (index != 0) out << ',';
        const auto& row = results[index];
        const auto& observed = row.observation;
        out << "{\"index\":" << index << ",\"kind\":\"" << (row.engine ? "engine" : "core")
            << "\",\"selection\":"; quoted(out, row.engine ? kNames[row.selection] : kGraphNames[row.selection - 1]);
        out << ",\"input_gain\":" << (row.engine ? kGains[row.selection] : 1.0)
            << ",\"edge_count\":" << (row.selection == 0 ? 0 : graphs.values[row.selection - 1].edge_count())
            << ",\"contacts\":\"" << (row.engine ? (row.nominal ? "nominal" : "ideal") : "none")
            << "\",\"workload\":\"" << (row.engine ? (row.polyphony ? "sustained-polyphony" : "silence") : "dense-input-frames")
            << "\",\"nanoseconds_per_frame_samples\":[";
        for (std::size_t sample = 0; sample < option.repetitions; ++sample) {
            if (sample != 0) out << ',';
            out << row.nanoseconds_per_frame[sample];
        }
        out << "],\"median_nanoseconds_per_frame\":" << median(row, option.repetitions)
            << ",\"relative_to_unconfigured\":";
        if (row.engine) out << median(row, option.repetitions) /
            median(results[3 + ((index - 3) / 4) * 4], option.repetitions);
        else out << "null";
        out << ",\"output_word_checksum\":\"" << hash_text(observed.timed.hash)
            << "\",\"warmup_word_checksum\":\"" << hash_text(observed.warmup.hash)
            << "\",\"maximum_observed_magnitude\":" << observed.timed.peak
            << ",\"final_source1_phase\":";
        if (row.engine) out << observed.phase; else out << "null";
        out << '}';
    }
    out << "]}\n";
    require(static_cast<bool>(out), "Cannot assemble benchmark report.");
    auto text = out.str();
    require(text.size() <= 128 * 1024, "Benchmark report exceeds its fixed bound.");
    return text;
}
} // namespace

static int benchmark_main(int argc, char* argv[]) {
    try {
#ifdef _WIN32
        if (_setmode(_fileno(stdout), _O_BINARY) == -1) fail("Cannot select binary stdout.");
#endif
        if (argc == 2 && std::string_view(argv[1]) == "--help") {
            std::cout << "Usage: hammond_source_leakage_benchmark --profile FILE [options]\n"
                         "  --sample-rate 44100|48000|96000 (default48000)\n"
                         "  --blocks 1..512                (default256; fixed64-frame blocks)\n"
                         "  --repetitions 1..9             (default5)\n"
                         "  --seed UINT64                  (default739)\n"
                         "Requires a regular compiled profile <=128KiB with audible polyphony.\n"
                         "Nineteen cases;16 warm-up blocks; rotated order; cooperative50s work budget.\n"
                         "Stdout JSON; no output files. Offline timing, not a callback deadline gate.\n";
        } else std::cout << benchmark(options(argc, argv));
        std::cout.flush();
        require(static_cast<bool>(std::cout), "Cannot write benchmark report.");
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "hammond_source_leakage_benchmark: " << error.what() << '\n';
        return 1;
    } catch (...) {
        std::cerr << "hammond_source_leakage_benchmark: unknown failure.\n";
        return 1;
    }
}
#ifdef _WIN32
int wmain(int argc, wchar_t* argv[]) {
    return hammond::cli::run_windows(argc, argv, benchmark_main, "hammond_source_leakage_benchmark", {11, 32768});
}
#else
int main(int argc, char* argv[]) { return benchmark_main(argc, argv); }
#endif
