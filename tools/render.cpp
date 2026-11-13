#include "hammond/Engine.h"
#include "hammond/Profile.h"
#include "hammond/detail/Decimal.h"

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
#include <limits>
#include <locale>
#include <optional>
#include <span>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>
#include <utility>
#include <vector>

namespace {

namespace fs = std::filesystem;

constexpr std::size_t kMaxArgumentBytes = 4096;
constexpr std::size_t kMaxScoreBytes = 16 * 1024 * 1024;
constexpr std::size_t kMaxScoreEvents = 262144;
constexpr std::size_t kMaxScoreLineBytes = 4096;
constexpr std::size_t kMaxNumberBytes = 128;
constexpr std::uint64_t kMaxSeconds = 600;
constexpr std::uint32_t kBytesPerFrame = 4;

[[noreturn]] void fail(const std::string& message) {
    throw std::runtime_error(message);
}

[[nodiscard]] bool ascii_space(char ch) noexcept {
    return ch == ' ' || ch == '\t' || ch == '\r' || ch == '\n' ||
           ch == '\f' || ch == '\v';
}

[[nodiscard]] std::uint64_t unsigned_number(std::string_view token,
                                           std::string_view name) {
    if (token.empty() || token.size() > kMaxNumberBytes ||
        !std::all_of(token.begin(), token.end(), [](char ch) {
            return ch >= '0' && ch <= '9';
        })) {
        fail(std::string(name) + " must be an unsigned decimal integer.");
    }
    std::uint64_t result = 0;
    const auto parsed = std::from_chars(token.data(), token.data() + token.size(), result);
    if (parsed.ec != std::errc{} || parsed.ptr != token.data() + token.size()) {
        fail(std::string(name) + " is out of range.");
    }
    return result;
}

[[nodiscard]] double finite_number(std::string_view token) {
    if (token.empty() || token.size() > kMaxNumberBytes) {
        fail("Event value must be a finite decimal number.");
    }
    double result = 0.0;
    const auto parsed = hammond::detail::parse_decimal(token, result);
    if (parsed == hammond::detail::DecimalResult::InvalidSyntax) {
        fail("Event value must be a finite decimal number.");
    }
    if (parsed != hammond::detail::DecimalResult::Ok) {
        fail("Event value is nonfinite or out of range.");
    }
    return result;
}

struct Options {
    fs::path profile;
    fs::path output;
    fs::path events;
    std::uint32_t sample_rate = 48000;
    std::uint32_t block_size = 64;
    std::uint64_t frames = 0;
    std::uint64_t seed = 0;
    std::uint8_t note = 60;
    std::array<std::uint8_t, hammond::kDrawbarCount> drawbars{8, 8, 8, 0, 0, 0, 0, 0, 0};
    hammond::ContactMode contact_mode = hammond::ContactMode::Ideal;
    hammond::PercussionSettings percussion{};
    bool has_events = false;
    bool fail_on_clip = false;
};

enum class Flag : std::size_t {
    Profile, Output, SampleRate, BlockSize, Frames, Seed, Drawbars, Note, Events,
    Contacts, Percussion, PercussionVolume, PercussionDecay, FailOnClip, Count
};

[[nodiscard]] Options parse_options(int argc, char* argv[]) {
    Options options;
    constexpr std::array<std::string_view, static_cast<std::size_t>(Flag::Count)> names{
        "--profile", "--output", "--sample-rate", "--block-size", "--frames",
        "--seed", "--drawbars", "--note", "--events", "--contacts", "--percussion",
        "--percussion-volume", "--percussion-decay", "--fail-on-clip"};
    // One program argument, two per value-taking flag, and one valueless flag.
    // Duplicates and the mutually exclusive note/score pair still reject below.
    if (argc > static_cast<int>(names.size() * 2)) {
        fail("Too many command-line arguments.");
    }
    std::array<bool, names.size()> seen{};
    for (int argument = 1; argument < argc; ++argument) {
        const std::string_view name(argv[argument]);
        const auto found = std::find(names.begin(), names.end(), name);
        if (found == names.end()) {
            fail("Unknown argument: " + std::string(name.substr(0, kMaxArgumentBytes)));
        }
        const auto index = static_cast<std::size_t>(found - names.begin());
        if (seen[index]) {
            fail("Duplicate argument: " + std::string(name));
        }
        seen[index] = true;
        const auto flag = static_cast<Flag>(index);
        if (flag == Flag::FailOnClip) {
            options.fail_on_clip = true;
            continue;
        }
        if (++argument == argc) {
            fail("Missing value for " + std::string(name));
        }
        const std::string_view value(argv[argument]);
        if (value.empty() || value.size() > kMaxArgumentBytes || value.starts_with("--")) {
            fail("Missing or oversized value for " + std::string(name));
        }
        switch (flag) {
        case Flag::Profile: options.profile = fs::path(value); break;
        case Flag::Output: options.output = fs::path(value); break;
        case Flag::Events:
            options.events = fs::path(value);
            options.has_events = true;
            break;
        case Flag::SampleRate: {
            const auto rate = unsigned_number(value, name);
            if (rate != 44100 && rate != 48000 && rate != 96000) {
                fail("Sample rate must be 44100, 48000 or 96000 Hz.");
            }
            options.sample_rate = static_cast<std::uint32_t>(rate);
            break;
        }
        case Flag::BlockSize: {
            const auto size = unsigned_number(value, name);
            if (size == 0 || size > hammond::kHardMaxBlockFrames) {
                fail("Block size must be in 1..65536.");
            }
            options.block_size = static_cast<std::uint32_t>(size);
            break;
        }
        case Flag::Frames: options.frames = unsigned_number(value, name); break;
        case Flag::Seed: options.seed = unsigned_number(value, name); break;
        case Flag::Note: {
            const auto note = unsigned_number(value, name);
            if (note < hammond::kMinManualMidiNote || note > hammond::kMaxManualMidiNote) {
                fail("Note must be a MIDI integer in 36..96.");
            }
            options.note = static_cast<std::uint8_t>(note);
            break;
        }
        case Flag::Drawbars:
            if (value.size() != options.drawbars.size()) {
                fail("Drawbars must contain exactly nine digits in 0..8.");
            }
            for (std::size_t i = 0; i < value.size(); ++i) {
                if (value[i] < '0' || value[i] > '8') {
                    fail("Drawbars must contain exactly nine digits in 0..8.");
                }
                options.drawbars[i] = static_cast<std::uint8_t>(value[i] - '0');
            }
            break;
        case Flag::Contacts:
            if (value == "ideal") {
                options.contact_mode = hammond::ContactMode::Ideal;
            } else if (value == "nominal") {
                options.contact_mode = hammond::ContactMode::LinearTravel;
            } else {
                fail("Contacts must be ideal or nominal.");
            }
            break;
        case Flag::Percussion:
            if (value == "off") {
                options.percussion.enabled = false;
            } else if (value == "second" || value == "third") {
                options.percussion.enabled = true;
                options.percussion.harmonic = value == "second"
                    ? hammond::PercussionHarmonic::Second : hammond::PercussionHarmonic::Third;
            } else {
                fail("Percussion must be off, second or third.");
            }
            break;
        case Flag::PercussionVolume:
            if (value == "normal") {
                options.percussion.volume = hammond::PercussionVolume::Normal;
            } else if (value == "soft") {
                options.percussion.volume = hammond::PercussionVolume::Soft;
            } else {
                fail("Percussion volume must be normal or soft.");
            }
            break;
        case Flag::PercussionDecay:
            if (value == "slow") {
                options.percussion.decay = hammond::PercussionDecay::Slow;
            } else if (value == "fast") {
                options.percussion.decay = hammond::PercussionDecay::Fast;
            } else {
                fail("Percussion decay must be slow or fast.");
            }
            break;
        case Flag::FailOnClip:
        case Flag::Count: fail("Internal option parsing error.");
        }
    }
    if (!seen[static_cast<std::size_t>(Flag::Profile)] ||
        !seen[static_cast<std::size_t>(Flag::Output)]) {
        fail("Both --profile and --output are required. Use --help for usage.");
    }
    if (options.has_events && seen[static_cast<std::size_t>(Flag::Note)]) {
        fail("Explicit --note is incompatible with --events.");
    }
    if (!seen[static_cast<std::size_t>(Flag::Frames)]) {
        options.frames = static_cast<std::uint64_t>(options.sample_rate) * 4;
    }
    if (options.frames == 0 ||
        options.frames > static_cast<std::uint64_t>(options.sample_rate) * kMaxSeconds ||
        options.frames > (std::numeric_limits<std::uint32_t>::max() - 36U) / kBytesPerFrame) {
        fail("Frames must be positive and no more than 600 seconds at the selected rate.");
    }
    return options;
}

[[nodiscard]] fs::path checked_input(const fs::path& path, std::uintmax_t limit,
                                     std::string_view name) {
    std::error_code error;
    const auto resolved = fs::canonical(path, error);
    if (error || !fs::is_regular_file(resolved, error) || error) {
        fail(std::string(name) + " must name a readable regular file: " + path.string());
    }
    const auto bytes = fs::file_size(resolved, error);
    if (error || bytes > limit) {
        fail(std::string(name) + " is unreadable or exceeds its byte limit.");
    }
    return resolved;
}

void preflight_paths(Options& options) {
    options.profile = checked_input(options.profile, hammond::kMaxCompiledProfileBytes, "Profile");
    if (options.has_events) {
        options.events = checked_input(options.events, kMaxScoreBytes, "Event score");
    }
    std::error_code error;
    const auto output = fs::weakly_canonical(options.output, error);
    if (error) {
        fail("Cannot resolve output path: " + error.message());
    }
    if (output == options.profile || (options.has_events && output == options.events)) {
        fail("Output path collides with an input file.");
    }
    const auto status = fs::symlink_status(options.output, error);
    if (error && error != std::errc::no_such_file_or_directory) {
        fail("Cannot inspect output path: " + error.message());
    }
    if (fs::exists(status) || fs::is_symlink(status)) {
        fail("Output already exists; existing files are never overwritten.");
    }
    error.clear();
    const auto parent = fs::canonical(output.parent_path().empty() ? fs::path(".") : output.parent_path(),
                                      error);
    if (error || !fs::is_directory(parent, error) || error || output.filename().empty()) {
        fail("Output parent must be an existing directory.");
    }
    options.output = parent / output.filename();
}

[[nodiscard]] bool valid_utf8(std::string_view text) noexcept {
    for (std::size_t i = 0; i < text.size();) {
        const auto first = static_cast<unsigned char>(text[i++]);
        if (first == 0) {
            return false;
        }
        if (first < 0x80U) {
            continue;
        }
        std::size_t continuation = 0;
        std::uint32_t codepoint = 0;
        std::uint32_t minimum = 0;
        if (first >= 0xc2U && first <= 0xdfU) {
            continuation = 1; codepoint = first & 0x1fU; minimum = 0x80U;
        } else if (first >= 0xe0U && first <= 0xefU) {
            continuation = 2; codepoint = first & 0x0fU; minimum = 0x800U;
        } else if (first >= 0xf0U && first <= 0xf4U) {
            continuation = 3; codepoint = first & 0x07U; minimum = 0x10000U;
        } else {
            return false;
        }
        if (continuation > text.size() - i) {
            return false;
        }
        for (std::size_t j = 0; j < continuation; ++j) {
            const auto byte = static_cast<unsigned char>(text[i++]);
            if ((byte & 0xc0U) != 0x80U) {
                return false;
            }
            codepoint = (codepoint << 6U) | (byte & 0x3fU);
        }
        if (codepoint < minimum || codepoint > 0x10ffffU ||
            (codepoint >= 0xd800U && codepoint <= 0xdfffU)) {
            return false;
        }
    }
    return true;
}

struct AbsoluteEvent {
    std::uint64_t frame = 0;
    hammond::Event event;
};

[[nodiscard]] AbsoluteEvent parse_event_line(std::string_view line, std::uint64_t frames,
                                             hammond::ContactMode contact_mode) {
    std::array<std::string_view, 5> tokens{};
    std::size_t position = 0;
    std::size_t count = 0;
    while (position < line.size()) {
        while (position < line.size() && ascii_space(line[position])) {
            ++position;
        }
        if (position == line.size()) {
            break;
        }
        const auto start = position;
        while (position < line.size() && !ascii_space(line[position])) {
            ++position;
        }
        if (count == tokens.size()) {
            fail("Expected exactly five event fields; extra tokens are forbidden.");
        }
        tokens[count++] = line.substr(start, position - start);
    }
    if (count != tokens.size()) {
        fail("Expected exactly five event fields.");
    }
    AbsoluteEvent result;
    result.frame = unsigned_number(tokens[0], "Event frame");
    if (result.frame >= frames) {
        fail("Event frame must lie in [0,total_frames).");
    }
    if (tokens[2] == "upper") {
        result.event.manual = hammond::Manual::Upper;
    } else if (tokens[2] == "lower") {
        result.event.manual = hammond::Manual::Lower;
    } else {
        fail("Unknown event manual.");
    }
    const auto index = unsigned_number(tokens[3], "Event index");
    const double value = finite_number(tokens[4]);
    using hammond::EventType;
    if (tokens[1] == "note_on" || tokens[1] == "note_off") {
        if (index < hammond::kMinManualMidiNote || index > hammond::kMaxManualMidiNote) {
            fail("Note event index must be MIDI 36..96.");
        }
        result.event.type = tokens[1] == "note_on" ? EventType::NoteOn : EventType::NoteOff;
        if (result.event.type == EventType::NoteOn) {
            if (value < 0.0 || value > 127.0 || std::trunc(value) != value) {
                fail("Note-on velocity must be an integer in 0..127.");
            }
        } else if (value != 0.0) {
            fail("Note-off value must be zero.");
        }
    } else if (tokens[1] == "key_position") {
        result.event.type = EventType::KeyPosition;
        if (index < hammond::kMinManualMidiNote || index > hammond::kMaxManualMidiNote ||
            value < 0.0 || value > 1.0) {
            fail("Key-position index must be MIDI 36..96 and target must be in 0..1.");
        }
        if (contact_mode == hammond::ContactMode::Ideal && value != 0.0 && value != 1.0) {
            fail("Ideal contacts accept only key-position targets 0 or 1.");
        }
    } else if (tokens[1] == "drawbar") {
        result.event.type = EventType::Drawbar;
        if (index >= hammond::kDrawbarCount || value < 0.0 || value > 8.0 ||
            std::trunc(value) != value) {
            fail("Drawbar index and integer value must be in 0..8.");
        }
    } else if (tokens[1] == "expression") {
        result.event.type = EventType::Expression;
        if (index != 0 || value < 0.0 || value > 1.0) {
            fail("Expression index must be zero and value in 0..1.");
        }
    } else if (tokens[1] == "all_notes_off") {
        result.event.type = EventType::AllNotesOff;
        if (index != 0 || value != 0.0) {
            fail("All-notes-off index and value must be zero.");
        }
    } else if (tokens[1] == "bank_drawbar") {
        result.event.type = EventType::BankDrawbar;
        if (index >= hammond::kDrawbarBankCount * hammond::kDrawbarCount ||
            value < 0.0 || value > 8.0 || std::trunc(value) != value) {
            fail("Bank-drawbar index must be in 0..17 and integer value in 0..8.");
        }
    } else if (tokens[1] == "select_bank") {
        result.event.type = EventType::SelectBank;
        if (index != 0 || value < 0.0 || value > 1.0 || std::trunc(value) != value) {
            fail("Select-bank index must be zero and integer value 0=A or 1=B.");
        }
    } else if (tokens[1] == "cancel") {
        result.event.type = EventType::Cancel;
        if (index != 0 || value != 0.0) {
            fail("Cancel index and value must be zero.");
        }
    } else if (tokens[1] == "percussion") {
        result.event.type = EventType::Percussion;
        if (result.event.manual != hammond::Manual::Upper || index >= 4 ||
            value < 0.0 || value > 1.0 || std::trunc(value) != value) {
            fail("Percussion requires upper manual, index 0..3 and integer value 0 or 1.");
        }
    } else {
        fail("Unknown event type.");
    }
    result.event.index = static_cast<std::uint8_t>(index);
    result.event.value = value;
    return result;
}

[[nodiscard]] std::vector<AbsoluteEvent> load_score(const Options& options) {
    if (!options.has_events) {
        return {{0, {0, hammond::EventType::NoteOn, hammond::Manual::Upper, options.note, 100.0}},
                {options.frames * 3 / 4,
                 {0, hammond::EventType::NoteOff, hammond::Manual::Upper, options.note, 0.0}}};
    }
    std::ifstream input(options.events, std::ios::binary);
    if (!input) {
        fail("Cannot open event score.");
    }
    std::string contents;
    std::array<char, 8192> buffer{};
    while (input) {
        input.read(buffer.data(), static_cast<std::streamsize>(buffer.size()));
        const auto bytes = static_cast<std::size_t>(input.gcount());
        if (bytes > kMaxScoreBytes - contents.size()) {
            fail("Event score exceeds 16 MiB.");
        }
        contents.append(buffer.data(), bytes);
    }
    if (!input.eof() || input.bad()) {
        fail("Error reading event score.");
    }
    if (!valid_utf8(contents)) {
        fail("Event score must be valid UTF-8/ASCII without embedded NUL bytes.");
    }
    std::string_view text(contents);
    if (text.starts_with("\xef\xbb\xbf")) {
        text.remove_prefix(3);
    }
    std::vector<AbsoluteEvent> events;
    events.reserve(std::min(kMaxScoreEvents, text.size() / 16));
    std::size_t line_number = 0;
    std::size_t same_frame_count = 0;
    while (!text.empty()) {
        ++line_number;
        const auto newline = text.find('\n');
        auto line = text.substr(0, newline);
        text.remove_prefix(newline == std::string_view::npos ? text.size() : newline + 1);
        try {
            if (line.size() > kMaxScoreLineBytes) {
                fail("Event score line exceeds 4096 bytes.");
            }
            while (!line.empty() && ascii_space(line.front())) {
                line.remove_prefix(1);
            }
            if (line.empty() || line.front() == '#') {
                continue;
            }
            if (events.size() == kMaxScoreEvents) {
                fail("Event score exceeds 262144 events.");
            }
            auto event = parse_event_line(line, options.frames, options.contact_mode);
            if (!events.empty() && event.frame < events.back().frame) {
                fail("Event frames must be sorted in nondecreasing order.");
            }
            same_frame_count = !events.empty() && event.frame == events.back().frame
                ? same_frame_count + 1 : 1;
            if (same_frame_count > hammond::kMaxEventsPerBlock) {
                fail("More than 1024 score events at one frame are unsupported.");
            }
            events.push_back(event);
        } catch (const std::runtime_error& error) {
            fail("Event score line " + std::to_string(line_number) + ": " + error.what());
        }
    }
    return events;
}

// A sibling directory is reserved atomically, avoiding C++20 ofstream's lack of
// exclusive creation. Publication uses a hard link: an existing destination is
// never replaced, including one created after the initial path preflight.
class TemporaryWave {
public:
    TemporaryWave() = default;
    TemporaryWave(const TemporaryWave&) = delete;
    TemporaryWave& operator=(const TemporaryWave&) = delete;

    ~TemporaryWave() {
        if (stream_.is_open()) {
            stream_.close();
        }
        std::error_code ignored;
        if (!file_.empty()) {
            fs::remove(file_, ignored);
        }
        if (!directory_.empty()) {
            fs::remove(directory_, ignored);
        }
    }

    void open(const fs::path& output) {
        const auto stamp = static_cast<std::uint64_t>(
            std::chrono::steady_clock::now().time_since_epoch().count());
        for (std::uint32_t attempt = 0; attempt < 128; ++attempt) {
            auto candidate = output.parent_path() /
                (".hammond-render-" + std::to_string(stamp) + "-" + std::to_string(attempt));
            auto candidate_file = candidate / "render.wav";
            std::error_code error;
            if (fs::create_directory(candidate, error)) {
                directory_ = std::move(candidate);
                file_ = std::move(candidate_file);
                stream_.open(file_, std::ios::binary | std::ios::out | std::ios::trunc);
                if (!stream_) {
                    fail("Cannot open temporary WAV output.");
                }
                return;
            }
            if (error && error != std::errc::file_exists) {
                fail("Cannot create temporary output directory: " + error.message());
            }
        }
        fail("Cannot reserve a unique temporary output directory.");
    }

    void write(std::span<const std::uint8_t> bytes) {
        stream_.write(reinterpret_cast<const char*>(bytes.data()),
                      static_cast<std::streamsize>(bytes.size()));
        if (!stream_) {
            fail("Error writing temporary WAV output.");
        }
    }

    void finish() {
        stream_.flush();
        if (!stream_) {
            fail("Error flushing temporary WAV output.");
        }
        stream_.close();
        if (!stream_) {
            fail("Error closing temporary WAV output.");
        }
    }

    void publish(const fs::path& output) const {
        std::error_code error;
        fs::create_hard_link(file_, output, error);
        if (error) {
            fail("Cannot publish WAV without overwriting (a filesystem supporting hard links is required): " +
                 error.message());
        }
    }

private:
    fs::path directory_;
    fs::path file_;
    std::ofstream stream_;
};

[[nodiscard]] std::array<std::uint8_t, 44> wave_header(const Options& options) {
    std::array<std::uint8_t, 44> bytes{};
    const auto put16 = [&bytes](std::size_t offset, std::uint16_t value) {
        bytes[offset] = static_cast<std::uint8_t>(value & 0xffU);
        bytes[offset + 1] = static_cast<std::uint8_t>(value >> 8U);
    };
    const auto put32 = [&bytes](std::size_t offset, std::uint32_t value) {
        for (std::size_t i = 0; i < 4; ++i) {
            bytes[offset + i] = static_cast<std::uint8_t>((value >> (i * 8)) & 0xffU);
        }
    };
    const auto tag = [&bytes](std::size_t offset, std::string_view text) {
        for (std::size_t i = 0; i < text.size(); ++i) {
            bytes[offset + i] = static_cast<std::uint8_t>(text[i]);
        }
    };
    const auto data_bytes = static_cast<std::uint32_t>(options.frames * kBytesPerFrame);
    tag(0, "RIFF"); put32(4, 36U + data_bytes); tag(8, "WAVE");
    tag(12, "fmt "); put32(16, 16); put16(20, 1); put16(22, 2);
    put32(24, options.sample_rate); put32(28, options.sample_rate * kBytesPerFrame);
    put16(32, 4); put16(34, 16); tag(36, "data"); put32(40, data_bytes);
    return bytes;
}

struct Metrics {
    double peak = 0.0;
    long double sum_squares = 0.0L;
    std::uint64_t clipped_frames = 0;
};

void encode_pcm(std::span<const float> samples, std::span<std::uint8_t> bytes,
                Metrics& metrics) {
    for (std::size_t i = 0; i < samples.size(); ++i) {
        const double sample = samples[i];
        if (!std::isfinite(sample)) {
            fail("Engine produced a nonfinite sample; WAV will not be published.");
        }
        metrics.peak = std::max(metrics.peak, std::abs(sample));
        const long double wide = sample;
        metrics.sum_squares += wide * wide;
        if (sample < -1.0 || sample > 1.0) {
            ++metrics.clipped_frames;
        }
        // Round to nearest (ties away from zero), then saturate to PCM16. The
        // float clipping count is per mono frame, before channel duplication.
        const auto rounded = std::lround(std::clamp(sample, -1.0, 1.0) * 32768.0);
        const auto pcm = static_cast<std::uint16_t>(std::clamp(rounded, -32768L, 32767L));
        const auto low = static_cast<std::uint8_t>(pcm & 0xffU);
        const auto high = static_cast<std::uint8_t>(pcm >> 8U);
        const auto offset = i * kBytesPerFrame;
        bytes[offset] = low; bytes[offset + 1] = high;
        bytes[offset + 2] = low; bytes[offset + 3] = high;
    }
}

[[nodiscard]] std::string summary(const Options& options, const hammond::RuntimeProfile& profile,
                                   const Metrics& metrics, std::string_view status) {
    const double rms = static_cast<double>(std::sqrt(
        metrics.sum_squares / static_cast<long double>(options.frames)));
    std::ostringstream json;
    json.imbue(std::locale::classic());
    json << std::setprecision(std::numeric_limits<double>::max_digits10)
         << "{\"status\":\"" << status << "\",\"model\":\"ideal-shared-sine-v1\","
         << "\"render_schema_version\":2,\"contact_model\":\""
         << hammond::contact_model_id(options.contact_mode)
         << "\",\"percussion_model\":\"" << hammond::kPercussionModelId << "\","
         << "\"evidence_status\":\"unmeasured\",\"profile_id\":\"" << profile.profile_id.data()
         << "\",\"authoring_sha256\":\"" << profile.authoring_sha256.data()
         << "\",\"sample_rate\":" << options.sample_rate
         << ",\"block_size\":" << options.block_size << ",\"frames\":" << options.frames
         << ",\"seed\":" << options.seed << ",\"channels\":2,\"sample_format\":\"pcm_s16le\""
         << ",\"peak\":" << metrics.peak << ",\"rms\":" << rms
         << ",\"clipped_frames\":" << metrics.clipped_frames
         << ",\"clipped_channel_samples\":" << metrics.clipped_frames * 2 << '}';
    return json.str();
}

int render(Options options) {
    preflight_paths(options);
    hammond::RuntimeProfile profile;
    std::string error;
    if (!hammond::load_runtime_profile_file(options.profile, profile, error)) {
        fail("Cannot load profile: " + error);
    }
    const auto score = load_score(options);
    hammond::Engine engine;
    const hammond::ProcessSpec spec{static_cast<double>(options.sample_rate), options.block_size,
                                    options.seed, 0};
    const auto console_model = options.contact_mode == hammond::ContactMode::Ideal
        ? hammond::make_legacy_console_model() : hammond::make_nominal_console_model();
    const auto prepared = engine.prepare(profile, spec, console_model);
    if (prepared != hammond::Status::Ok || !engine.prepared()) {
        fail("Engine preparation failed: " + std::string(hammond::status_name(prepared)));
    }
    std::array<hammond::Event, hammond::kDrawbarCount + 4> initial_controls{};
    for (std::size_t i = 0; i < options.drawbars.size(); ++i) {
        initial_controls[i] = {0, hammond::EventType::Drawbar, hammond::Manual::Upper,
                               static_cast<std::uint8_t>(i), static_cast<double>(options.drawbars[i])};
    }
    // These controls follow registration and precede all scored events. Later
    // score automation, including frame zero, therefore overrides CLI defaults.
    const std::array<double, 4> percussion_values{
        options.percussion.enabled ? 1.0 : 0.0,
        options.percussion.harmonic == hammond::PercussionHarmonic::Third ? 1.0 : 0.0,
        options.percussion.volume == hammond::PercussionVolume::Soft ? 1.0 : 0.0,
        options.percussion.decay == hammond::PercussionDecay::Fast ? 1.0 : 0.0};
    for (std::size_t i = 0; i < percussion_values.size(); ++i) {
        initial_controls[hammond::kDrawbarCount + i] = {
            0, hammond::EventType::Percussion, hammond::Manual::Upper,
            static_cast<std::uint8_t>(i), percussion_values[i]};
    }
    const auto flushed = engine.process(0, {}, initial_controls);
    if (!flushed || flushed.events_consumed != initial_controls.size() || engine.frame_clock() != 0) {
        fail("Engine rejected initial zero-frame controls.");
    }
    std::vector<float> mono(options.block_size);
    std::vector<std::uint8_t> pcm(static_cast<std::size_t>(options.block_size) * kBytesPerFrame);
    std::array<hammond::Event, hammond::kMaxEventsPerBlock> local_events{};
    const auto header = wave_header(options);
    TemporaryWave output;
    output.open(options.output);
    output.write(header);
    Metrics metrics;
    std::uint64_t frame = 0;
    std::size_t next_event = 0;
    while (frame < options.frames) {
        const auto window_end = std::min(options.frames, frame + options.block_size);
        while (frame < window_end) {
            auto end_frame = window_end;
            auto end_event = next_event;
            while (end_event < score.size() && score[end_event].frame < window_end &&
                   end_event - next_event < local_events.size()) {
                ++end_event;
            }
            if (end_event < score.size() && score[end_event].frame < window_end) {
                end_frame = score[end_event].frame;
                // Keep every event at a tied timestamp in the same positive call.
                while (end_event > next_event && score[end_event - 1].frame == end_frame) {
                    --end_event;
                }
            }
            if (end_frame <= frame) {
                fail("Internal event partition did not advance the timeline.");
            }
            const auto count = end_event - next_event;
            for (std::size_t i = 0; i < count; ++i) {
                local_events[i] = score[next_event + i].event;
                local_events[i].offset = static_cast<std::uint32_t>(score[next_event + i].frame - frame);
            }
            const auto frames = static_cast<std::uint32_t>(end_frame - frame);
            const auto samples = std::span<float>(mono.data(), frames);
            const auto result = engine.process(frames, samples,
                std::span<const hammond::Event>(local_events.data(), count));
            if (!result || result.events_consumed != count || engine.frame_clock() != end_frame) {
                fail("Engine processing failed: " + std::string(hammond::status_name(result.status)));
            }
            const auto packed = std::span<std::uint8_t>(pcm.data(),
                static_cast<std::size_t>(frames) * kBytesPerFrame);
            encode_pcm(samples, packed, metrics);
            output.write(packed);
            frame = end_frame;
            next_event = end_event;
        }
    }
    if (next_event != score.size()) {
        fail("Internal event partition left unconsumed events.");
    }
    output.finish();
    const bool clip_failure = options.fail_on_clip && metrics.clipped_frames != 0;
    const auto report = summary(options, profile, metrics, clip_failure ? "clipped" : "ok");
    if (!clip_failure) {
        output.publish(options.output);
    }
    std::cout << report << '\n';
    if (!std::cout) {
        fail("Cannot write render JSON summary to stdout.");
    }
    if (clip_failure) {
        std::cerr << "hammond_render: clipping detected with --fail-on-clip; output was not published.\n";
        return 2;
    }
    return 0;
}

} // namespace

int main(int argc, char* argv[]) {
    try {
        if (argc == 2 && std::string_view(argv[1]) == "--help") {
            std::cout <<
                "Usage: hammond_render --profile FILE --output FILE [options]\n"
                "  --sample-rate 44100|48000|96000  (default 48000)\n"
                "  --block-size 1..65536           (default 64)\n"
                "  --frames N                     (default 4 seconds; maximum 600 seconds)\n"
                "  --seed UNSIGNED64              (default 0)\n"
                "  --drawbars NNNNNNNNN           (nine digits 0..8; default 888000000)\n"
                "  --note 36..96                  (default 60; incompatible with --events)\n"
                "  --events FILE                  (absolute events replace the default note)\n"
                "  --contacts ideal|nominal        (default ideal; nominal travel is unmeasured)\n"
                "  --percussion off|second|third    (default off; upper-B route only)\n"
                "  --percussion-volume normal|soft (default normal)\n"
                "  --percussion-decay slow|fast     (default slow)\n"
                "  --fail-on-clip                  (do not publish a clipped render)\n"
                "Output: unmeasured dry model, stereo little-endian PCM16; existing files are rejected.\n"
                "Scores: at most 16 MiB, 262144 events, 4096 bytes/line, 1024 events/frame.\n"
                "Score fields: frame type upper|lower index value (five fields).\n"
                "Types: note_on, note_off, drawbar, expression, all_notes_off,\n"
                "       bank_drawbar, select_bank, cancel, percussion, key_position.\n"
                "bank_drawbar: index bank*9+drawbar (A=0, B=1), integer value 0..8.\n"
                "select_bank: index 0, integer value 0=A or 1=B; reconnects the manual.\n"
                "cancel: index/value 0; retains held keys and banks. Drawbar edits selected bank.\n"
                "percussion: upper only; indices 0=enable, 1=third, 2=soft, 3=fast; value 0|1.\n"
                "key_position: either manual, MIDI36..96, target 0..1; ideal contacts require 0|1.\n"
                "Initial percussion controls follow drawbars; score events then take precedence.\n"
                "JSON summary schema 2 identifies source, contact and percussion models separately.\n";
            return std::cout ? 0 : 1;
        }
        return render(parse_options(argc, argv));
    } catch (const std::exception& error) {
        std::cerr << "hammond_render: " << error.what() << '\n';
        return 1;
    } catch (...) {
        std::cerr << "hammond_render: unknown failure.\n";
        return 1;
    }
}
