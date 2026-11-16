#include "hammond/research/CausalContactGrid.h"

#include <array>
#include <charconv>
#include <cstddef>
#include <cstdint>
#include <exception>
#include <iostream>
#include <limits>
#include <span>
#include <string>
#include <string_view>
#include <system_error>

#ifdef _WIN32
#include <cstdio>
#include <fcntl.h>
#include <io.h>
#endif

namespace {

using namespace hammond::research;

constexpr std::size_t kMaximumInputBytes = 128 * 1024;
constexpr std::size_t kMaximumReportBytes = 2 * 1024 * 1024;

struct ProbeError {
    std::string_view message;
};

[[noreturn]] void fail(std::string_view message) { throw ProbeError{message}; }

[[nodiscard]] bool ascii_space(char value) noexcept {
    return value == ' ' || value == '\t' || value == '\n'
        || value == '\r' || value == '\f' || value == '\v';
}

[[nodiscard]] std::string read_input() {
    std::string input;
    input.reserve(kMaximumInputBytes);
    char next{};
    while (std::cin.get(next)) {
        // Read at most one extra byte to distinguish exact-limit input from
        // oversized input; never store an unbounded token or diagnostic.
        if (input.size() == kMaximumInputBytes) fail("stdin exceeds 131072 bytes");
        input.push_back(next);
    }
    if (!std::cin.eof() || std::cin.bad()) fail("stdin read failed");
    return input;
}

class InputReader {
public:
    explicit InputReader(std::string_view input) noexcept : input_(input) {}

    [[nodiscard]] std::string_view token() {
        skip_space();
        if (cursor_ == input_.size()) fail("missing input token");
        const std::size_t begin = cursor_;
        while (cursor_ < input_.size() && !ascii_space(input_[cursor_])) ++cursor_;
        return input_.substr(begin, cursor_ - begin);
    }

    [[nodiscard]] std::uint64_t integer(std::uint64_t maximum) {
        const auto text = token();
        std::uint64_t value = 0;
        for (const char character : text) {
            if (character < '0' || character > '9') {
                fail("expected unsigned decimal digits only");
            }
            const auto digit = static_cast<std::uint64_t>(character - '0');
            // Check against the field limit before multiplying or narrowing.
            if (value > maximum / 10
                || (value == maximum / 10 && digit > maximum % 10)) {
                fail("integer exceeds its field limit");
            }
            value = value * 10 + digit;
        }
        return value;
    }

    void require_end() {
        skip_space();
        if (cursor_ != input_.size()) fail("unexpected trailing input token");
    }

private:
    void skip_space() noexcept {
        while (cursor_ < input_.size() && ascii_space(input_[cursor_])) ++cursor_;
    }

    std::string_view input_;
    std::size_t cursor_{};
};

struct InputCase {
    ContactGridConfig config{};
    std::uint32_t frames{}, targetCount{}, blockCount{};
    std::array<ContactGridTarget, kContactGridMaxCommands> targets{};
    std::array<std::uint32_t, kContactGridMaxFrames> blocks{};
};

void parse_input(std::string_view text, InputCase& input) {
    InputReader reader{text};
    if (reader.token() != "CGGRID1") fail("expected CGGRID1 transport version");
    input.config.sampleRateHz = static_cast<std::uint32_t>(
        reader.integer(std::numeric_limits<std::uint32_t>::max()));
    if (input.config.sampleRateHz != 44100 && input.config.sampleRateHz != 48000
        && input.config.sampleRateHz != 96000) fail("unsupported sample rate");
    input.config.keyCount = static_cast<std::uint32_t>(reader.integer(kContactGridMaxKeys));
    if (input.config.keyCount == 0) fail("key count must be 1 through 4");
    input.frames = static_cast<std::uint32_t>(reader.integer(kContactGridMaxFrames));
    input.targetCount = static_cast<std::uint32_t>(reader.integer(kContactGridMaxCommands));
    input.blockCount = static_cast<std::uint32_t>(reader.integer(input.frames));
    if (input.frames != 0 && input.blockCount == 0) {
        fail("a positive epoch needs at least one block");
    }

    for (std::uint32_t index = 0; index < input.config.keyCount; ++index) {
        auto& key = input.config.keys[index];
        key.pressUnitsPerTick = static_cast<std::uint32_t>(
            reader.integer(std::numeric_limits<std::uint32_t>::max()));
        key.releaseUnitsPerTick = static_cast<std::uint32_t>(
            reader.integer(std::numeric_limits<std::uint32_t>::max()));
        if (key.pressUnitsPerTick == 0 || key.releaseUnitsPerTick == 0) {
            fail("press and release speeds must be positive");
        }
        for (auto& contact : key.contacts) {
            contact.off = reader.integer(kContactGridFullTravel);
            contact.on = reader.integer(kContactGridFullTravel);
            if (contact.off >= contact.on) fail("each contact requires off < on");
        }
    }

    const std::uint32_t endTick = input.frames * kContactGridTicksPerFrame;
    for (std::uint32_t index = 0; index < input.targetCount; ++index) {
        auto& target = input.targets[index];
        target.tick = static_cast<std::uint32_t>(reader.integer(endTick));
        target.keyIndex = static_cast<std::uint32_t>(reader.integer(input.config.keyCount - 1));
        target.position = reader.integer(kContactGridFullTravel);
    }
    for (std::uint32_t index = 1; index < input.targetCount; ++index) {
        if (input.targets[index].tick < input.targets[index - 1].tick) {
            fail("target ticks must be globally nondecreasing");
        }
    }

    std::uint32_t totalFrames = 0;
    for (std::uint32_t index = 0; index < input.blockCount; ++index) {
        const auto frames = static_cast<std::uint32_t>(reader.integer(input.frames - totalFrames));
        if (frames == 0) fail("block lengths must be positive");
        input.blocks[index] = frames;
        totalFrames += frames;
    }
    if (totalFrames != input.frames) fail("block lengths must sum to N");
    reader.require_end();
}

struct BlockReport {
    std::uint32_t frames{}, cursorFrames{}, edgesWritten{};
};

struct RunReport {
    ContactGridSnapshot snapshot{};
    std::uint32_t edgeCount{};
    std::array<ContactGridEdge, kContactGridMaxEdges> edges{};
    std::array<BlockReport, kContactGridMaxFrames> blocks{};
};

void run_case(const InputCase& input, RunReport& report) {
    CausalContactGrid model;
    if (model.prepare(input.config) != ContactGridStatus::ok) fail("model preparation failed");
    std::uint32_t cursorFrames = 0;
    std::uint32_t nextTarget = 0;
    const auto targets = std::span<const ContactGridTarget>{input.targets}.first(input.targetCount);
    for (std::uint32_t index = 0; index < input.blockCount; ++index) {
        const std::uint32_t frames = input.blocks[index];
        cursorFrames += frames;
        const std::uint32_t endTick = cursorFrames * kContactGridTicksPerFrame;
        const std::uint32_t firstTarget = nextTarget;
        // Commands on this block's right endpoint belong to the next call or
        // closure. Their order is unchanged, including every tied no-op.
        while (nextTarget < input.targetCount && targets[nextTarget].tick < endTick) {
            ++nextTarget;
        }
        const auto result = model.process(
            frames, targets.subspan(firstTarget, nextTarget - firstTarget),
            std::span<ContactGridEdge>{report.edges}.subspan(report.edgeCount));
        if (result.status != ContactGridStatus::ok) fail("model processing failed");
        if (result.edgesWritten > kContactGridMaxEdges - report.edgeCount
            || result.requiredEdges != result.edgesWritten) fail("invalid model edge count");
        report.edgeCount += result.edgesWritten;
        report.blocks[index] = {frames, cursorFrames, result.edgesWritten};
    }
    if (model.close_observation(targets.subspan(nextTarget)) != ContactGridStatus::ok) {
        fail("model observation closure failed");
    }
    report.snapshot = model.snapshot();
    if (report.snapshot.cursorFrames != input.frames
        || report.snapshot.commandCount != input.targetCount
        || report.snapshot.edgeCount != report.edgeCount) fail("inconsistent model snapshot");
}

class JsonWriter {
public:
    JsonWriter() { output_.reserve(4096); }

    void append(std::string_view text) {
        if (text.size() > kMaximumReportBytes - output_.size()) fail("JSON report exceeds its byte limit");
        output_.append(text);
    }

    void number(std::uint64_t value) {
        std::array<char, 20> buffer{};
        const auto converted = std::to_chars(buffer.data(), buffer.data() + buffer.size(), value);
        if (converted.ec != std::errc{}) fail("integer serialization failed");
        append(std::string_view{buffer.data(), static_cast<std::size_t>(converted.ptr - buffer.data())});
    }

    void boolean(bool value) { append(value ? "true" : "false"); }
    [[nodiscard]] const std::string& output() const noexcept { return output_; }

private:
    std::string output_;
};

[[nodiscard]] std::string_view phase_name(ContactGridPhase phase) {
    switch (phase) {
    case ContactGridPhase::unprepared: return "unprepared";
    case ContactGridPhase::ready: return "ready";
    case ContactGridPhase::active: return "active";
    case ContactGridPhase::closed: return "closed";
    }
    fail("invalid model phase");
}

void write_config(JsonWriter& json, const ContactGridConfig& config) {
    json.append("{\"sample_rate_hz\":");
    json.number(config.sampleRateHz);
    json.append(",\"key_count\":");
    json.number(config.keyCount);
    json.append(",\"keys\":[");
    for (std::size_t index = 0; index < config.keys.size(); ++index) {
        if (index != 0) json.append(",");
        const auto& key = config.keys[index];
        json.append("{\"press_units_per_tick\":");
        json.number(key.pressUnitsPerTick);
        json.append(",\"release_units_per_tick\":");
        json.number(key.releaseUnitsPerTick);
        json.append(",\"contacts\":[");
        for (std::size_t contact = 0; contact < key.contacts.size(); ++contact) {
            if (contact != 0) json.append(",");
            json.append("{\"off\":");
            json.number(key.contacts[contact].off);
            json.append(",\"on\":");
            json.number(key.contacts[contact].on);
            json.append("}");
        }
        json.append("]}");
    }
    json.append("]}");
}

void write_snapshot(JsonWriter& json, const ContactGridSnapshot& snapshot) {
    json.append("{\"phase\":\"");
    json.append(phase_name(snapshot.phase));
    json.append("\",\"config\":");
    write_config(json, snapshot.config);
    json.append(",\"cursor_frames\":");
    json.number(snapshot.cursorFrames);
    json.append(",\"command_count\":");
    json.number(snapshot.commandCount);
    json.append(",\"edge_count\":");
    json.number(snapshot.edgeCount);
    json.append(",\"keys\":[");
    for (std::size_t index = 0; index < snapshot.keys.size(); ++index) {
        if (index != 0) json.append(",");
        const auto& key = snapshot.keys[index];
        json.append("{\"position\":");
        json.number(key.position);
        json.append(",\"target\":");
        json.number(key.target);
        json.append(",\"anchor_position\":");
        json.number(key.anchorPosition);
        json.append(",\"anchor_tick\":");
        json.number(key.anchorTick);
        json.append(",\"closed\":[");
        for (std::size_t contact = 0; contact < key.closed.size(); ++contact) {
            if (contact != 0) json.append(",");
            json.boolean(key.closed[contact]);
        }
        json.append("]}");
    }
    json.append("]}");
}

void write_report(JsonWriter& json, const InputCase& input, const RunReport& report) {
    json.append("{\"schema_version\":1,\"model_id\":\"");
    json.append(kCausalContactGridModelId);
    json.append("\",\"edges\":[");
    for (std::uint32_t index = 0; index < report.edgeCount; ++index) {
        if (index != 0) json.append(",");
        const auto& edge = report.edges[index];
        json.append("{\"time\":{\"tick\":");
        json.number(edge.time.tick);
        json.append(",\"numerator\":");
        json.number(edge.time.numerator);
        json.append(",\"denominator\":");
        json.number(edge.time.denominator);
        json.append("},\"key_index\":");
        json.number(edge.keyIndex);
        json.append(",\"contact_index\":");
        json.number(edge.contactIndex);
        json.append(",\"closed_after\":");
        json.boolean(edge.closedAfter);
        json.append("}");
    }
    json.append("],\"snapshot\":");
    write_snapshot(json, report.snapshot);
    json.append(",\"blocks\":[");
    for (std::uint32_t index = 0; index < input.blockCount; ++index) {
        if (index != 0) json.append(",");
        const auto& block = report.blocks[index];
        json.append("{\"frames\":");
        json.number(block.frames);
        json.append(",\"cursor_frames\":");
        json.number(block.cursorFrames);
        json.append(",\"edges_written\":");
        json.number(block.edgesWritten);
        json.append("}");
    }
    json.append("]}\n");
}

constexpr std::string_view help = R"(Usage: causal_contact_grid_probe [--help]

With no arguments, read one complete CGGRID1 case from stdin (maximum 131072
bytes). Tokens are separated by ASCII space, tab, LF, CR, form feed or vertical
tab; leading/trailing whitespace is allowed. All numbers are unsigned decimal
digits [0-9]+, with no signs, fractions, exponents or comments. No file paths
or other arguments are accepted. The exact token grammar, in this order, is:

  CGGRID1 F K N C P
  K key records:    press release off0 on0 off1 on1 ... off8 on8
  C target records: tick key_index position
  P block lengths:  frames0 frames1 ... frames(P-1)

F is 44100, 48000 or 96000 Hz. K is 1..4; N is the total frame count, 0..4096;
C is the command count, 0..512. P is 0..N and each block length is positive;
the lengths must sum to N. N=0 requires P=0 and has no block-length tokens.
Each press/release speed is 1..4294967295 position units per tick. Each key
has exactly nine off/on pairs in contact-index order, each satisfying
0 <= off < on <= 281474976710656 (2^48, full travel).

Target ticks are absolute epoch ticks, 65536 per frame, in [0,N*65536].
They must be globally nondecreasing; tied targets retain their supplied order.
key_index is 0..K-1; position is 0..281474976710656. Commands at a block's
right endpoint belong to the next block. Commands at N*65536 instead feed
close_observation, including tick-zero commands when N=0. Closure always runs.
Extra/missing tokens, out-of-range integers and oversized input are errors.

Success writes one JSON object with schema_version=1, model_id, edges,
snapshot and blocks. Edges and the final closed snapshot use the exact oracle
snake_case fields; snapshot configuration and state each include all four keys,
with inactive keys zero-padded. Each block is {frames,cursor_frames,edges_written}.
The complete input, model run and bounded JSON report are prepared before stdout
is written. Errors exit nonzero with a bounded stderr diagnostic. This isolated
synthetic trajectory probe produces no waveform, conversion or Engine changes.
)";

} // namespace

int main(int argc, char* argv[]) {
    try {
        if (argc == 2 && std::string_view{argv[1]} == "--help") {
            std::cout << help;
            std::cout.flush();
            if (!std::cout) fail("stdout write failed");
            return 0;
        }
        if (argc != 1) fail("only --help or no arguments are accepted");
#ifdef _WIN32
        // Admit raw bytes: CRT text mode collapses CRLF and treats Ctrl-Z as
        // EOF, which could hide oversized input or unexpected trailing data.
        const int inputDescriptor = _fileno(stdin);
        if (inputDescriptor < 0 || _setmode(inputDescriptor, _O_BINARY) == -1) {
            fail("cannot set stdin to binary mode");
        }
#endif
        const std::string text = read_input();
        InputCase input;
        parse_input(text, input);
        RunReport report;
        run_case(input, report);
        JsonWriter json;
        write_report(json, input, report);
        const auto& output = json.output();
        std::cout.write(output.data(), static_cast<std::streamsize>(output.size()));
        std::cout.flush();
        if (!std::cout) fail("stdout write failed");
        return 0;
    } catch (const ProbeError& error) {
        std::cerr << "causal_contact_grid_probe: " << error.message << '\n';
    } catch (const std::exception&) {
        std::cerr << "causal_contact_grid_probe: allocation or standard-library failure\n";
    } catch (...) {
        std::cerr << "causal_contact_grid_probe: unexpected failure\n";
    }
    return 2;
}
