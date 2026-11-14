#include "CliArguments.h"
#include "RotaryNominalProfile.h"
#include "hammond/RotaryRenderer.h"

#include <algorithm>
#include <array>
#include <bit>
#include <charconv>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <locale>
#include <memory>
#include <span>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>
#include <utility>

namespace {

namespace fs = std::filesystem;
namespace rotary = hammond::rotary;

constexpr std::size_t kMaxArgumentBytes = 4096;
constexpr int kMaxArgumentCount = 13;
constexpr std::uint64_t kMaxInputSeconds = 60;
constexpr std::size_t kMaxEventBytes = 64 * 1024;
constexpr std::size_t kMaxEventLineBytes = 64;
constexpr std::size_t kSampleBytes = 8;
constexpr std::string_view kReportContract = "rotary-offline-render-v1";
constexpr std::string_view kGainWarning =
    "Normalized inputs do not bound the output to [-1,1]: cubic interpolation, "
    "reference-distance/path-distance gain and signed horn/drum sums can exceed unity. "
    "Output is never clipped, normalized or resampled.";
constexpr std::string_view kBoundary =
    "Synthetic nominal research model with separate normalized horn/drum "
    "radiation-boundary inputs. Not a measured cabinet, connected Engine output, "
    "R5 audible reconstruction qualification, or R6 host/device qualification.";

static_assert(sizeof(double) == kSampleBytes && std::numeric_limits<double>::is_iec559 &&
              std::numeric_limits<double>::digits == 53,
              "The offline file format requires IEEE-754 binary64 double.");

[[noreturn]] void fail(const std::string& message) {
    throw std::runtime_error(message);
}

[[nodiscard]] std::uint64_t unsigned_number(std::string_view value,
                                           std::string_view name) {
    if (value.empty() || value.size() > 20 ||
        !std::all_of(value.begin(), value.end(), [](char ch) { return ch >= '0' && ch <= '9'; })) {
        fail(std::string(name) + " must be an unsigned decimal integer.");
    }
    std::uint64_t result = 0;
    const auto parsed = std::from_chars(value.data(), value.data() + value.size(), result);
    if (parsed.ec != std::errc{} || parsed.ptr != value.data() + value.size()) {
        fail(std::string(name) + " is out of range.");
    }
    return result;
}

struct Options {
    fs::path horn;
    fs::path drum;
    fs::path output;
    fs::path events;
    std::uint32_t sample_rate = 0;
    std::uint32_t block_size = 64;
    bool has_events = false;
};

[[nodiscard]] Options parse_options(int argc, char* argv[]) {
    constexpr std::array<std::string_view, 6> names{
        "--horn", "--drum", "--sample-rate", "--output-dir", "--block-size", "--events"};
    if (argc < 1 || argc > kMaxArgumentCount) fail("Too many command-line arguments.");
    Options result;
    std::array<bool, names.size()> seen{};
    for (int index = 1; index < argc; ++index) {
        const std::string_view name(argv[index]);
        if (name.size() > kMaxArgumentBytes) fail("Oversized command-line argument.");
        const auto found = std::find(names.begin(), names.end(), name);
        if (found == names.end()) fail("Unknown argument: " + std::string(name));
        const auto flag = static_cast<std::size_t>(found - names.begin());
        if (seen[flag]) fail("Duplicate argument: " + std::string(name));
        seen[flag] = true;
        if (++index == argc) fail("Missing value for " + std::string(name));
        const std::string_view value(argv[index]);
        if (value.empty() || value.size() > kMaxArgumentBytes || value.starts_with("--")) {
            fail("Missing or oversized value for " + std::string(name));
        }
        switch (flag) {
        case 0: result.horn = hammond::cli::argument_path(value); break;
        case 1: result.drum = hammond::cli::argument_path(value); break;
        case 2: {
            const auto rate = unsigned_number(value, name);
            if (rate != 44100 && rate != 48000 && rate != 96000 && rate != 192000) {
                fail("Sample rate must be 44100, 48000, 96000 or 192000 Hz.");
            }
            result.sample_rate = static_cast<std::uint32_t>(rate);
            break;
        }
        case 3: result.output = hammond::cli::argument_path(value); break;
        case 4: {
            const auto block = unsigned_number(value, name);
            if (block == 0 || block > rotary::kMaxBlockFrames) {
                fail("Block size must be in 1..4096.");
            }
            result.block_size = static_cast<std::uint32_t>(block);
            break;
        }
        case 5:
            result.events = hammond::cli::argument_path(value);
            result.has_events = true;
            break;
        default: fail("Invalid argument index.");
        }
    }
    for (std::size_t index = 0; index < 4; ++index) {
        if (!seen[index]) fail("Required argument missing: " + std::string(names[index]));
    }
    return result;
}

struct CheckedInput {
    fs::path path;
    std::uint64_t bytes = 0;
};

[[nodiscard]] CheckedInput checked_input(const fs::path& path, std::uint64_t limit,
                                          std::string_view name) {
    std::error_code error;
    const auto resolved = fs::canonical(path, error);
    if (error || !fs::is_regular_file(resolved, error) || error) {
        fail(std::string(name) + " must name a readable regular file.");
    }
    const auto bytes = fs::file_size(resolved, error);
    if (error || bytes > limit) fail(std::string(name) + " exceeds its byte limit or is unreadable.");
    return {resolved, static_cast<std::uint64_t>(bytes)};
}

void require_end(std::ifstream& input, std::string_view name) {
    if (input.peek() != std::char_traits<char>::eof() || input.bad()) {
        fail(std::string(name) + " changed size during reading or could not be read completely.");
    }
}

struct AbsoluteEvent {
    std::uint64_t frame = 0;
    rotary::RotorId rotor = rotary::RotorId::Horn;
    rotary::SpeedCommand command = rotary::SpeedCommand::Chorale;
};

struct EventList {
    std::array<AbsoluteEvent, rotary::kMaxEventsPerBlock> values{};
    std::size_t size = 0;
};

[[nodiscard]] AbsoluteEvent parse_event(std::string_view line, std::uint64_t input_frames,
                                         bool newline_terminated) {
    if (newline_terminated && !line.empty() && line.back() == '\r') line.remove_suffix(1);
    if (line.empty() || line.size() > kMaxEventLineBytes) {
        fail("Each event line must contain three fields and at most 64 ASCII bytes.");
    }
    std::array<std::string_view, 3> tokens{};
    std::size_t position = 0;
    std::size_t count = 0;
    while (position < line.size()) {
        const auto space = [](char ch) { return ch == ' ' || ch == '\t'; };
        while (position < line.size() && space(line[position])) ++position;
        if (position == line.size()) break;
        const auto start = position;
        while (position < line.size() && !space(line[position])) {
            const auto byte = static_cast<unsigned char>(line[position]);
            if (byte < 0x21U || byte > 0x7eU) fail("Events require ASCII tokens and LF or CRLF lines.");
            ++position;
        }
        if (count == tokens.size()) fail("Each event line must contain exactly three fields.");
        tokens[count++] = line.substr(start, position - start);
    }
    if (count != tokens.size()) fail("Each event line must contain exactly three fields; blank lines are invalid.");
    AbsoluteEvent result;
    result.frame = unsigned_number(tokens[0], "Event frame");
    if (result.frame > input_frames) fail("Event frame must lie in inclusive [0,input_frames].");
    if (tokens[1] == "horn") result.rotor = rotary::RotorId::Horn;
    else if (tokens[1] == "drum") result.rotor = rotary::RotorId::Drum;
    else fail("Event rotor must be horn or drum.");
    if (tokens[2] == "chorale") result.command = rotary::SpeedCommand::Chorale;
    else if (tokens[2] == "tremolo") result.command = rotary::SpeedCommand::Tremolo;
    else fail("Event command must be chorale or tremolo.");
    return result;
}

[[nodiscard]] EventList read_events(Options& options, std::uint64_t input_frames) {
    EventList result;
    if (!options.has_events) return result;
    const auto checked = checked_input(options.events, kMaxEventBytes, "Events");
    options.events = checked.path;
    std::ifstream input(checked.path, std::ios::binary);
    if (!input) fail("Cannot open events file.");
    std::string contents(static_cast<std::size_t>(checked.bytes), '\0');
    if (!contents.empty()) {
        input.read(contents.data(), static_cast<std::streamsize>(contents.size()));
        if (input.gcount() != static_cast<std::streamsize>(contents.size()) || !input) {
            fail("Cannot read complete events file.");
        }
    }
    require_end(input, "Events file");
    std::string_view remaining(contents);
    while (!remaining.empty()) {
        const auto newline = remaining.find('\n');
        const auto line = remaining.substr(0, newline);
        remaining.remove_prefix(newline == std::string_view::npos ? remaining.size() : newline + 1);
        if (result.size == result.values.size()) fail("Events file exceeds 1024 events.");
        const auto event = parse_event(line, input_frames, newline != std::string_view::npos);
        if (result.size != 0 && event.frame < result.values[result.size - 1].frame) {
            fail("Events must have nondecreasing frame numbers; supplied order is preserved.");
        }
        result.values[result.size++] = event;
    }
    return result;
}

[[nodiscard]] fs::path output_path(const fs::path& requested) {
    if (requested.filename().empty() || requested.filename() == "." || requested.filename() == "..") {
        fail("Output directory must have a new final name and an existing parent.");
    }
    std::error_code error;
    const auto parent = fs::canonical(requested.parent_path().empty() ? fs::path(".") : requested.parent_path(), error);
    if (error || !fs::is_directory(parent, error) || error) {
        fail("Output directory parent must already exist.");
    }
    return parent / requested.filename();
}

// Never remove recursively: cleanup touches only files this invocation created.
class OutputDirectory {
public:
    explicit OutputDirectory(fs::path directory) : directory_(std::move(directory)),
        audio_(directory_ / "stereo.f64le"), report_(directory_ / "report.json") {
        std::error_code error;
        if (!fs::create_directory(directory_, error)) {
            fail("Cannot exclusively create output directory; existing paths are never overwritten.");
        }
    }
    ~OutputDirectory() {
        if (committed_) return;
        std::error_code ignored;
        if (report_created_) fs::remove(report_, ignored);
        if (audio_created_) fs::remove(audio_, ignored);
        fs::remove(directory_, ignored);
    }
    OutputDirectory(const OutputDirectory&) = delete;
    OutputDirectory& operator=(const OutputDirectory&) = delete;
    [[nodiscard]] const fs::path& audio() const noexcept { return audio_; }
    [[nodiscard]] const fs::path& report() const noexcept { return report_; }
    void claim_audio() noexcept { audio_created_ = true; }
    void claim_report() noexcept { report_created_ = true; }
    void commit() noexcept { committed_ = true; }
private:
    fs::path directory_;
    fs::path audio_;
    fs::path report_;
    bool audio_created_ = false;
    bool report_created_ = false;
    bool committed_ = false;
};

class ExclusiveFile {
public:
    explicit ExclusiveFile(const fs::path& path) {
#ifdef _MSC_VER
        if (_wfopen_s(&file_, path.c_str(), L"wbx") != 0) file_ = nullptr;
#elif defined(_WIN32)
        file_ = _wfopen(path.c_str(), L"wbx");
#else
        file_ = std::fopen(path.c_str(), "wbx");
#endif
        if (file_ == nullptr) fail("Cannot exclusively create output file.");
    }
    ~ExclusiveFile() { if (file_ != nullptr) std::fclose(file_); }
    ExclusiveFile(const ExclusiveFile&) = delete;
    ExclusiveFile& operator=(const ExclusiveFile&) = delete;
    void write(const void* data, std::size_t bytes) {
        if (bytes != 0 && std::fwrite(data, 1, bytes, file_) != bytes) fail("Cannot write complete output file.");
    }
    void close() {
        const bool failed = std::ferror(file_) != 0;
        const int closed = std::fclose(file_);
        file_ = nullptr;
        if (failed || closed != 0) fail("Cannot close complete output file.");
    }
private:
    std::FILE* file_ = nullptr;
};

struct Workspace {
    std::array<double, rotary::kMaxBlockFrames> horn{};
    std::array<double, rotary::kMaxBlockFrames> drum{};
    std::array<double, rotary::kMaxBlockFrames> left{};
    std::array<double, rotary::kMaxBlockFrames> right{};
    std::array<unsigned char, rotary::kMaxBlockFrames * kSampleBytes> input_bytes{};
    std::array<unsigned char, rotary::kMaxBlockFrames * 2 * kSampleBytes> output_bytes{};
    std::array<rotary::CommandEvent, rotary::kMaxEventsPerBlock> events{};
};

void read_samples(std::ifstream& input, std::span<double> destination,
                  Workspace& workspace, std::string_view name, std::uint64_t first_frame) {
    const auto bytes = destination.size() * kSampleBytes;
    input.read(reinterpret_cast<char*>(workspace.input_bytes.data()), static_cast<std::streamsize>(bytes));
    if (input.gcount() != static_cast<std::streamsize>(bytes) || !input) {
        fail(std::string(name) + " input was truncated or could not be read.");
    }
    for (std::size_t index = 0; index < destination.size(); ++index) {
        std::uint64_t bits = 0;
        for (std::size_t byte = 0; byte < kSampleBytes; ++byte) {
            bits |= static_cast<std::uint64_t>(workspace.input_bytes[index * kSampleBytes + byte]) << (byte * 8U);
        }
        const auto value = std::bit_cast<double>(bits);
        if (!std::isfinite(value) || value < -1.0 || value > 1.0) {
            fail(std::string(name) + " input frame " + std::to_string(first_frame + index) +
                 " must be finite and in [-1,1].");
        }
        destination[index] = value;
    }
}

struct Metrics {
    std::array<double, 2> peak{};
    std::array<std::uint64_t, 2> above_unity{};
    std::uint64_t output_frames = 0;
    std::uint64_t events_consumed = 0;
};

void process_block(rotary::RotaryRenderer& renderer, Workspace& workspace,
                   std::size_t frames, std::size_t event_count, ExclusiveFile& output,
                   Metrics& metrics) {
    const auto result = renderer.process(
        std::span<const double>(workspace.horn.data(), frames),
        std::span<const double>(workspace.drum.data(), frames),
        std::span<double>(workspace.left.data(), frames),
        std::span<double>(workspace.right.data(), frames),
        std::span<const rotary::CommandEvent>(workspace.events.data(), event_count));
    if (!result.ok()) fail("RotaryRenderer rejected a block: " + std::string(rotary::status_name(result.status)));
    if (result.events_consumed != event_count) fail("Renderer did not consume every admitted event.");
    metrics.events_consumed += result.events_consumed;
    for (std::size_t frame = 0; frame < frames; ++frame) {
        const std::array<double, 2> pair{workspace.left[frame], workspace.right[frame]};
        for (std::size_t channel = 0; channel < pair.size(); ++channel) {
            if (!std::isfinite(pair[channel])) fail("Renderer produced nonfinite output.");
            const auto magnitude = std::abs(pair[channel]);
            metrics.peak[channel] = std::max(metrics.peak[channel], magnitude);
            if (magnitude > 1.0) ++metrics.above_unity[channel];
            const auto bits = std::bit_cast<std::uint64_t>(pair[channel]);
            const auto position = (frame * 2 + channel) * kSampleBytes;
            for (std::size_t byte = 0; byte < kSampleBytes; ++byte) {
                workspace.output_bytes[position + byte] = static_cast<unsigned char>((bits >> (byte * 8U)) & 0xffU);
            }
        }
    }
    output.write(workspace.output_bytes.data(), frames * 2 * kSampleBytes);
    metrics.output_frames += frames;
}

// Valid UTF-8 remains readable. Invalid native POSIX bytes use U+00xx escapes;
// the report also retains exact native path bytes in hexadecimal.
[[nodiscard]] std::string json_string(std::string_view value) {
    constexpr char hex[] = "0123456789abcdef";
    std::string result = "\"";
    for (std::size_t index = 0; index < value.size();) {
        const auto byte = static_cast<unsigned char>(value[index]);
        if (byte == '"' || byte == '\\') {
            result.push_back('\\');
            result.push_back(static_cast<char>(byte));
            ++index;
        } else if (byte >= 0x20U && byte < 0x80U) {
            result.push_back(static_cast<char>(byte));
            ++index;
        } else {
            std::size_t length = byte >= 0xc2U && byte <= 0xdfU ? 2U :
                                 byte >= 0xe0U && byte <= 0xefU ? 3U :
                                 byte >= 0xf0U && byte <= 0xf4U ? 4U : 0U;
            if (length > value.size() - index) length = 0;
            for (std::size_t offset = 1; offset < length; ++offset) {
                const auto next = static_cast<unsigned char>(value[index + offset]);
                if (next < 0x80U || next > 0xbfU ||
                    (offset == 1 && ((byte == 0xe0U && next < 0xa0U) ||
                                     (byte == 0xedU && next > 0x9fU) ||
                                     (byte == 0xf0U && next < 0x90U) ||
                                     (byte == 0xf4U && next > 0x8fU)))) {
                    length = 0;
                    break;
                }
            }
            if (length != 0) {
                result.append(value.substr(index, length));
                index += length;
            } else {
                result += "\\u00";
                result.push_back(hex[byte >> 4U]);
                result.push_back(hex[byte & 0xfU]);
                ++index;
            }
        }
    }
    result.push_back('"');
    return result;
}

[[nodiscard]] std::string path_hex(const fs::path& path) {
    constexpr char hex[] = "0123456789abcdef";
    const auto bytes = hammond::cli::path_text(path);
    std::string result;
    result.reserve(bytes.size() * 2);
    for (const char character : bytes) {
        const auto byte = static_cast<unsigned char>(character);
        result.push_back(hex[byte >> 4U]);
        result.push_back(hex[byte & 0xfU]);
    }
    return result;
}

[[nodiscard]] std::string make_report(const Options& options, std::uint64_t input_frames,
                                       std::size_t event_count,
                                       const rotary::RotaryRenderer& renderer,
                                       const Metrics& metrics) {
    const auto diagnostics = renderer.diagnostics();
    const auto state = renderer.state();
    const auto bounds = renderer.path_bounds();
    const auto profile = renderer.profile();
    constexpr std::array<std::string_view, rotary::kPathCount> path_names{
        "horn_left", "horn_right", "drum_left", "drum_right"};
    std::ostringstream json;
    json.imbue(std::locale::classic());
    json << std::setprecision(std::numeric_limits<double>::max_digits10)
         << "{\n  \"schema_version\":1,\n  \"report_contract\":" << json_string(kReportContract)
         << ",\n  \"tool\":\"hammond_rotary_render\",\n  \"status\":\"ok\","
         << "\n  \"renderer_contract\":" << json_string(rotary::kRendererContractId)
         << ",\n  \"numerical_contract\":" << json_string(rotary::kNumericalContractId)
         << ",\n  \"model_id\":" << json_string(rotary::kModelId)
         << ",\n  \"profile\":{\"id\":" << json_string(rotary::generated::kProfileId)
         << ",\"sha256\":" << json_string(rotary::generated::kProfileSha256)
         << ",\"compiled_function\":\"hammond::rotary::generated::nominal_profile\"},"
         << "\n  \"sample_rate_hz\":" << options.sample_rate
         << ",\n  \"block_size\":" << options.block_size
         << ",\n  \"input_format\":\"mono-f64le\","
         << "\n  \"output_format\":\"stereo-interleaved-f64le\","
         << "\n  \"channel_order\":[\"left\",\"right\"],"
         << "\n  \"input_frames\":" << input_frames
         << ",\n  \"tail_flush_frames\":" << renderer.tail_flush_frames()
         << ",\n  \"output_frames\":" << metrics.output_frames
         << ",\n  \"output_bytes\":" << metrics.output_frames * 2 * kSampleBytes
         << ",\n  \"algorithmic_latency_frames\":" << rotary::RotaryRenderer::algorithmic_latency_frames()
         << ",\n  \"history_capacity_frames\":" << renderer.history_capacity_frames()
         << ",\n  \"event_count\":" << event_count
         << ",\n  \"events_consumed\":" << metrics.events_consumed
         << ",\n  \"paths\":{\"horn\":" << json_string(hammond::cli::path_text(options.horn))
         << ",\"drum\":" << json_string(hammond::cli::path_text(options.drum))
         << ",\"events\":" << (options.has_events ? json_string(hammond::cli::path_text(options.events)) : "null")
         << ",\"output_directory\":" << json_string(hammond::cli::path_text(options.output))
         << ",\"audio\":" << json_string(hammond::cli::path_text(options.output / "stereo.f64le"))
         << ",\"report\":" << json_string(hammond::cli::path_text(options.output / "report.json")) << "},"
         << "\n  \"path_bytes_hex\":{\"encoding\":\"UTF-8 on Windows; native POSIX bytes\",\"horn\":"
         << json_string(path_hex(options.horn)) << ",\"drum\":" << json_string(path_hex(options.drum))
         << ",\"events\":" << (options.has_events ? json_string(path_hex(options.events)) : "null")
         << ",\"output_directory\":" << json_string(path_hex(options.output)) << "},"
         << "\n  \"physical_path_bounds\":[";
    for (std::size_t index = 0; index < bounds.size(); ++index) {
        if (index != 0) json << ',';
        json << "{\"path\":" << json_string(path_names[index])
             << ",\"min_distance_m\":" << bounds[index].min_distance_m
             << ",\"max_distance_m\":" << bounds[index].max_distance_m
             << ",\"min_delay_seconds\":" << bounds[index].min_distance_m / profile.sound_speed_m_s
             << ",\"max_delay_seconds\":" << bounds[index].max_distance_m / profile.sound_speed_m_s << '}';
    }
    json << "],\n  \"diagnostics\":{\"has_rendered_sample\":" << (diagnostics.has_rendered_sample ? "true" : "false")
         << ",\"last_input_frame\":" << diagnostics.last_input_frame
         << ",\"last_observation\":{\"frame\":" << diagnostics.last_observation.frame
         << ",\"fraction\":" << diagnostics.last_observation.fraction << '}'
         << ",\"max_solver_residual_s\":" << diagnostics.max_solver_residual_s
         << ",\"max_solver_iterations\":" << diagnostics.max_solver_iterations
         << ",\"last_paths\":[";
    for (std::size_t index = 0; index < diagnostics.last_paths.size(); ++index) {
        if (index != 0) json << ',';
        const auto& path = diagnostics.last_paths[index];
        json << "{\"path\":" << json_string(path_names[index])
             << ",\"delay_s\":" << path.delay_s << ",\"distance_m\":" << path.distance_m
             << ",\"emission_phase_rad\":" << path.emission_phase_rad
             << ",\"radial_speed_m_s\":" << path.radial_speed_m_s
             << ",\"frequency_ratio\":" << path.frequency_ratio
             << ",\"distance_gain\":" << path.distance_gain
             << ",\"residual_s\":" << path.residual_s << ",\"iterations\":" << path.iterations
             << ",\"emission\":{\"frame\":" << diagnostics.last_emissions[index].frame
             << ",\"fraction\":" << diagnostics.last_emissions[index].fraction << "}}";
    }
    json << "]},\n  \"final_state\":{\"frame\":" << state.frame << ",\"rotors\":[";
    for (std::size_t index = 0; index < state.motion.size(); ++index) {
        if (index != 0) json << ',';
        json << "{\"rotor\":" << json_string(index == 0 ? "horn" : "drum")
             << ",\"command\":" << json_string(rotary::command_name(state.commands[index]))
             << ",\"phase_rad\":" << state.motion[index].phase_rad
             << ",\"turns\":" << state.motion[index].turns
             << ",\"speed_rad_s\":" << state.motion[index].speed_rad_s << '}';
    }
    json << "]},\n  \"peak_absolute_output\":{\"left\":" << metrics.peak[0]
         << ",\"right\":" << metrics.peak[1] << "},"
         << "\n  \"output_samples_above_unity\":{\"left\":" << metrics.above_unity[0]
         << ",\"right\":" << metrics.above_unity[1] << "},"
         << "\n  \"normalized_gain_warning\":" << json_string(kGainWarning)
         << ",\n  \"synthetic_boundary\":" << json_string(kBoundary)
         << ",\n  \"tail_policy\":\"Explicit zero inputs; motion continues; no latency trimming\"\n}\n";
    return json.str();
}

int render(Options options) {
    const auto byte_limit = static_cast<std::uint64_t>(options.sample_rate) * kMaxInputSeconds * kSampleBytes;
    const auto horn = checked_input(options.horn, byte_limit, "Horn input");
    const auto drum = checked_input(options.drum, byte_limit, "Drum input");
    if (horn.bytes % kSampleBytes != 0 || drum.bytes % kSampleBytes != 0 || horn.bytes != drum.bytes) {
        fail("Horn and drum inputs must contain equal whole binary64 frames.");
    }
    options.horn = horn.path;
    options.drum = drum.path;
    const auto input_frames = horn.bytes / kSampleBytes;
    const auto events = read_events(options, input_frames);
    options.output = output_path(options.output);
    std::ifstream horn_input(options.horn, std::ios::binary);
    std::ifstream drum_input(options.drum, std::ios::binary);
    if (!horn_input || !drum_input) fail("Cannot open both input files.");
    rotary::RotaryRenderer renderer;
    const auto prepared = renderer.prepare(rotary::generated::nominal_profile(),
                                           {static_cast<double>(options.sample_rate), options.block_size});
    if (prepared != rotary::Status::Ok) fail("Cannot prepare nominal profile: " + std::string(rotary::status_name(prepared)));
    auto workspace = std::make_unique<Workspace>();
    OutputDirectory directory(options.output);
    ExclusiveFile audio(directory.audio());
    directory.claim_audio();
    Metrics metrics;
    std::uint64_t frame = 0;
    std::size_t next_event = 0;
    do {
        const auto frames = static_cast<std::size_t>(std::min<std::uint64_t>(options.block_size, input_frames - frame));
        if (frames != 0) {
            read_samples(horn_input, std::span<double>(workspace->horn.data(), frames), *workspace, "Horn", frame);
            read_samples(drum_input, std::span<double>(workspace->drum.data(), frames), *workspace, "Drum", frame);
        }
        std::size_t count = 0;
        while (next_event < events.size && events.values[next_event].frame <= frame + frames) {
            const auto& event = events.values[next_event++];
            workspace->events[count++] = {static_cast<std::uint32_t>(event.frame - frame), event.rotor, event.command};
        }
        process_block(renderer, *workspace, frames, count, audio, metrics);
        frame += frames;
    } while (frame < input_frames);
    require_end(horn_input, "Horn input");
    require_end(drum_input, "Drum input");
    if (next_event != events.size) fail("Not all admitted events were consumed.");
    workspace->horn.fill(0.0);
    workspace->drum.fill(0.0);
    std::uint32_t remaining_tail = renderer.tail_flush_frames();
    while (remaining_tail != 0) {
        const auto frames = std::min(options.block_size, remaining_tail);
        process_block(renderer, *workspace, frames, 0, audio, metrics);
        remaining_tail -= frames;
    }
    if (metrics.output_frames != input_frames + renderer.tail_flush_frames()) {
        fail("Output frame count does not include exactly the explicit tail.");
    }
    audio.close();
    const auto contents = make_report(options, input_frames, events.size, renderer, metrics);
    ExclusiveFile report(directory.report());
    directory.claim_report();
    report.write(contents.data(), contents.size());
    report.close();
    std::cout << "Rendered " << input_frames << " input frames plus " << renderer.tail_flush_frames()
              << " explicit tail frames. " << kGainWarning << '\n';
    std::cout.flush();
    if (!std::cout) fail("Cannot write completion to stdout.");
    directory.commit();
    return 0;
}

int renderer_main(int argc, char* argv[]) {
    try {
        if (argc == 2 && std::string_view(argv[1]) == "--help") {
            std::cout <<
                "Usage: hammond_rotary_render --horn FILE --drum FILE --sample-rate RATE\n"
                "       --output-dir NEW_DIRECTORY [--block-size N] [--events FILE]\n"
                "RATE is 44100, 48000, 96000 or 192000 Hz; N is 1..4096 (default 64).\n"
                "Inputs: separate raw little-endian IEEE-754 binary64 mono samples,\n"
                "finite in [-1,1], equal whole-frame lengths, at most 60 seconds each.\n"
                "Empty inputs are valid. No headers, conversion or resampling.\n"
                "Events: at most 1024 ASCII lines: frame horn|drum chorale|tremolo.\n"
                "Frames are unsigned decimal in inclusive [0,input_frames], in stable\n"
                "nondecreasing order. Spaces/tabs separate exactly three fields; LF/CRLF.\n"
                "Empty files are valid; blank lines, comments, BOM and extra tokens reject.\n"
                "Event files are at most 64 KiB; each line at most 64 ASCII bytes.\n"
                "Output parent must exist. The new directory is created exclusively.\n"
                "Existing files/directories are never overwritten. Successful output:\n"
                "  stereo.f64le: raw interleaved left/right little-endian binary64.\n"
                "  report.json: profile/contract IDs and SHA256, counts and diagnostics.\n"
                "Every render appends exactly tail_flush_frames zero-input frames while\n"
                "motion continues. Input and flush counts remain separate; the two-frame\n"
                "algorithmic latency and physical propagation delay are not trimmed.\n"
                "Compiled profile: " << rotary::generated::kProfileId << "\n"
                "Profile SHA256: " << rotary::generated::kProfileSha256 << '\n'
                << kGainWarning << '\n' << kBoundary << '\n';
            std::cout.flush();
            if (!std::cout) fail("Cannot write help to stdout.");
            return 0;
        }
        return render(parse_options(argc, argv));
    } catch (const std::exception& error) {
        std::cerr << "hammond_rotary_render: " << error.what() << '\n';
        return 1;
    } catch (...) {
        std::cerr << "hammond_rotary_render: unknown failure.\n";
        return 1;
    }
}

} // namespace

#ifdef _WIN32
int wmain(int argc, wchar_t* argv[]) {
    return hammond::cli::run_windows(argc, argv, renderer_main, "hammond_rotary_render",
        {kMaxArgumentCount, kMaxArgumentBytes, "Too many command-line arguments.",
         "Command-line argument is invalid Unicode or oversized (maximum 4096 UTF-8 bytes)."});
}
#else
int main(int argc, char* argv[]) {
    return renderer_main(argc, argv);
}
#endif
