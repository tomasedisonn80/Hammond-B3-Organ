#include "MidiReplay.h"
#include "MidiInput.h"

#include <algorithm>
#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <span>
#include <string>
#include <string_view>
#include <type_traits>

#if defined(__unix__) || defined(__APPLE__)
#include <sys/stat.h>
#endif

namespace {

using namespace hammond::standalone;
namespace fs = std::filesystem;

static_assert(std::is_trivially_copyable_v<MidiReplayEvent>);
static_assert(std::is_trivially_copyable_v<MidiReplayPlan>);

struct Totals {
    std::size_t parsed{}, parse_rejections{}, loaded{}, load_rejections{}, capability_skips{};
} totals;

[[noreturn]] void fail(std::string_view expression, int line, std::string_view detail = {}) {
    std::cerr << __FILE__ << ':' << line << ": CHECK failed: " << expression;
    if (!detail.empty()) std::cerr << " (" << detail << ')';
    std::cerr << '\n';
    std::exit(EXIT_FAILURE);
}

void check(bool condition, std::string_view expression, int line, std::string_view detail = {}) {
    if (!condition) fail(expression, line, detail);
}

#define CHECK(expression) check(static_cast<bool>(expression), #expression, __LINE__)
#define CHECK_DETAIL(expression, detail) \
    check(static_cast<bool>(expression), #expression, __LINE__, (detail))

[[nodiscard]] bool same_event(const MidiReplayEvent& left, const MidiReplayEvent& right) {
    return left.at_ms == right.at_ms && left.kind == right.kind &&
        left.bytes == right.bytes && left.size == right.size;
}

void same_plan(const MidiReplayPlan& left, const MidiReplayPlan& right) {
    CHECK(left.event_count == right.event_count);
    CHECK(left.duration_ms == right.duration_ms);
    for (std::size_t index = 0; index < left.events.size(); ++index) {
        CHECK(same_event(left.events[index], right.events[index]));
    }
}

[[nodiscard]] MidiReplayPlan sentinel() {
    MidiReplayPlan plan;
    plan.event_count = 3;
    plan.duration_ms = 4321;
    for (std::size_t index = 0; index < plan.events.size(); ++index) {
        plan.events[index] = MidiReplayEvent{
            static_cast<std::uint32_t>(index + 17), MidiReplayKind::BackendFault,
            {0xDE, 0xAD, 0xBE}, 253};
    }
    return plan;
}

[[nodiscard]] std::string script(std::string_view body, unsigned duration = 250) {
    return "B3MIDIREPLAY1\nduration_ms " + std::to_string(duration) + '\n' + std::string{body};
}

[[nodiscard]] MidiReplayPlan parsed(std::string_view source) {
    auto plan = sentinel();
    std::string error = "clear this on success";
    CHECK_DETAIL(parse_midi_replay(source, plan, error), error);
    CHECK(error.empty());
    ++totals.parsed;
    return plan;
}

void rejected(std::string_view source) {
    auto plan = sentinel();
    const auto before = plan;
    std::string error;
    CHECK_DETAIL(!parse_midi_replay(source, plan, error), source.substr(0, 100));
    CHECK(!error.empty());
    same_plan(plan, before); // Includes inactive entries without comparing padding.
    ++totals.parse_rejections;
}

[[nodiscard]] std::string hex(unsigned value, bool lower = false) {
    const std::string_view digits = lower ? "0123456789abcdef" : "0123456789ABCDEF";
    return std::string{digits[(value >> 4U) & 15U], digits[value & 15U]};
}

void grammar_and_owned_storage() {
    CHECK(kMidiReplayFormat == "B3MIDIREPLAY1");
    CHECK(kMidiReplayMaxEvents == 2048);
    CHECK(kMidiReplayMaxBytes == 65536);
    CHECK(kMidiReplayMaxLineBytes == 256);
    CHECK(kMidiReplayMinimumDurationMs == 250);
    CHECK(kMidiReplayMaximumDurationMs == 10000);

    const auto empty = parsed("B3MIDIREPLAY1\nduration_ms 250");
    CHECK(empty.event_count == 0 && empty.duration_ms == 250);
    for (const auto& event : empty.events) CHECK(same_event(event, MidiReplayEvent{}));
    CHECK(parsed("B3MIDIREPLAY1\r\n\tduration_ms\t10000 \t\r\n\t# comment\r\n \t\r\n").duration_ms == 10000);

    std::string source = script(
        "# pure data; comments never become actions\n\n"
        "\t000 bytes 00\n"
        "0 connect\n"
        "0 bytes 90 3c 7F\n"
        "0 bytes c0 01\n"
        "0 disconnect\n"
        "0 fault backend\n"
        "0 connect\n"
        "249 bytes f8\n");
    const auto plan = parsed(source);
    source.assign(source.size(), 'x'); // No string_view into the caller survives.
    CHECK(plan.event_count == 8 && plan.duration_ms == 250);
    constexpr std::array kinds{
        MidiReplayKind::Bytes, MidiReplayKind::Connect, MidiReplayKind::Bytes,
        MidiReplayKind::Bytes, MidiReplayKind::Disconnect, MidiReplayKind::BackendFault,
        MidiReplayKind::Connect, MidiReplayKind::Bytes};
    for (std::size_t index = 0; index < kinds.size(); ++index) {
        CHECK(plan.events[index].kind == kinds[index]);
        CHECK(plan.events[index].at_ms == (index == 7 ? 249U : 0U));
        if (kinds[index] != MidiReplayKind::Bytes) {
            CHECK(plan.events[index].size == 0);
            CHECK((plan.events[index].bytes == std::array<std::uint8_t, 3>{0, 0, 0}));
        }
    }
    CHECK(plan.events[0].size == 1);
    CHECK((plan.events[0].bytes == std::array<std::uint8_t, 3>{0, 0, 0}));
    CHECK(plan.events[2].size == 3);
    CHECK((plan.events[2].bytes == std::array<std::uint8_t, 3>{0x90, 0x3C, 0x7F}));
    CHECK(plan.events[3].size == 2);
    CHECK((plan.events[3].bytes == std::array<std::uint8_t, 3>{0xC0, 1, 0}));
    CHECK(plan.events[7].size == 1);
    CHECK((plan.events[7].bytes == std::array<std::uint8_t, 3>{0xF8, 0, 0}));
    for (std::size_t index = plan.event_count; index < plan.events.size(); ++index) {
        CHECK(same_event(plan.events[index], MidiReplayEvent{}));
    }
    const auto copy = plan;
    same_plan(copy, plan);
}

void every_raw_byte_value() {
    std::string body;
    for (unsigned value = 0; value < 256; ++value) {
        const auto upper = hex(value);
        const auto lower = hex(value, true);
        body += "0 bytes " + upper + '\n';
        body += "0 bytes " + lower + ' ' + upper + '\n';
        body += "0 bytes " + upper + ' ' + lower + ' ' + upper + '\n';
    }
    const auto plan = parsed(script(body));
    CHECK(plan.event_count == 768);
    for (unsigned value = 0; value < 256; ++value) {
        for (std::size_t length = 1; length <= 3; ++length) {
            const auto& event = plan.events[3U * value + length - 1];
            CHECK(event.kind == MidiReplayKind::Bytes && event.at_ms == 0);
            CHECK(event.size == length);
            for (std::size_t position = 0; position < 3; ++position) {
                CHECK(event.bytes[position] == (position < length ? value : 0U));
            }
        }
    }
}

void malformed_syntax_and_ascii() {
    constexpr std::array bad_headers{
        "", "B3MIDIREPLAY1", "B3MIDIREPLAY1\n", "B3MIDIREPLAY2\nduration_ms 250\n",
        " B3MIDIREPLAY1\nduration_ms 250\n", "B3MIDIREPLAY1 \nduration_ms 250\n",
        "# comment\nB3MIDIREPLAY1\nduration_ms 250\n", "B3MIDIREPLAY1\n\nduration_ms 250\n",
        "B3MIDIREPLAY1\n# comment\nduration_ms 250\n", "B3MIDIREPLAY1\nduration_ms\n",
        "B3MIDIREPLAY1\nDuration_ms 250\n", "B3MIDIREPLAY1\nduration_ms 250 extra\n",
        "B3MIDIREPLAY1\nduration_ms 250 # inline\n"};
    for (const auto source : bad_headers) rejected(source);

    constexpr std::array bad_records{
        "0", "0 bytes", "0 bytes 0", "0 bytes 000", "0 bytes 0x90", "0 bytes +1",
        "0 bytes -1", "0 bytes GG", "0 bytes Fg", "0 bytes f:", "0 bytes /0",
        "0 bytes 90 3C 7F 00", "0 bytes 90 3C 7F # comment", "0 bytes 90 # comment",
        "0 bytes 90,3C,7F", "0 bytes 90;", "0 Bytes 90", "0 connect extra",
        "0 disconnect extra", "0 fault", "0 fault Backend", "0 fault disconnected",
        "0 fault overflow", "0 fault backend extra", "0 reconnect", "0 include other",
        "0 run command", "0 quit", "0 duration_ms 250", "0 Connect", "0 bytes \"90\""};
    for (const auto record : bad_records) {
        // Prefix mutation must never leak into the destination on a late error.
        rejected(script("0 connect\n0 bytes 90 3C 7F\n" + std::string{record} + '\n'));
    }

    // Check every non-text byte, including NUL, DEL and all high bytes. Even a
    // comment is data validation input; it cannot conceal arbitrary binary data.
    for (unsigned value = 0; value < 256; ++value) {
        if ((value >= 0x20 && value <= 0x7E) || value == '\t' || value == '\n' || value == '\r') continue;
        auto source = script("#");
        source.push_back(static_cast<char>(value));
        source.push_back('\n');
        rejected(source);
    }
    rejected("B3MIDIREPLAY1\rduration_ms 250\n");
    rejected(script("0 connect\r"));
    rejected(script("0 connect\rX\n"));
    rejected(std::string{"\xEF\xBB\xBF"} + script(""));
    rejected(script("0\vconnect\n"));
}

void duration_and_order_boundaries() {
    CHECK(parsed(script("249 disconnect\n", 250)).events[0].at_ms == 249);
    CHECK(parsed(script("9999 disconnect\n", 10000)).events[0].at_ms == 9999);
    CHECK(parsed("B3MIDIREPLAY1\nduration_ms 00250\n000 connect\n").duration_ms == 250);
    constexpr std::array bad_durations{
        "0", "249", "10001", "4294967295", "4294967296", "9999999999999999999999",
        "-250", "+250", "250.0", "2.5e2", "0xFA", "250ms"};
    for (const auto value : bad_durations) rejected("B3MIDIREPLAY1\nduration_ms " + std::string{value} + '\n');
    constexpr std::array bad_times{
        "-1", "-0", "+0", "250", "251", "4294967295", "4294967296",
        "9999999999999999999999", "0.0", "0x00", "0ms"};
    for (const auto value : bad_times) rejected(script(std::string{value} + " connect\n"));
    rejected(script("0 connect\n9 bytes 90 3C 7F\n8 disconnect\n"));
    rejected(script("10000 connect\n", 10000));
    // The parser does not invent connection state or repair an input schedule.
    const auto ties = parsed(script("0 disconnect\n0 connect\n0 connect\n0 fault backend\n0 bytes FF\n"));
    CHECK(ties.event_count == 5);
    CHECK(ties.events[0].kind == MidiReplayKind::Disconnect);
    CHECK(ties.events[1].kind == MidiReplayKind::Connect);
    CHECK(ties.events[2].kind == MidiReplayKind::Connect);
    CHECK(ties.events[3].kind == MidiReplayKind::BackendFault);
    CHECK(ties.events[4].kind == MidiReplayKind::Bytes);
}

[[nodiscard]] std::string maximum_text() {
    std::string source = script("");
    while (source.size() < 65536) {
        const auto remaining = 65536 - source.size();
        const auto chunk = std::min<std::size_t>(remaining, 257);
        if (chunk == 1) source.push_back('\n');
        else {
            source.push_back('#');
            source.append(chunk == 257 ? 255 : chunk - 1, 'x');
            if (chunk == 257) source.push_back('\n');
        }
    }
    return source;
}

void resource_limits() {
    std::string body;
    for (std::size_t index = 0; index < 2048; ++index) body += "0 bytes 90 24 01\n";
    const auto maximum_events = parsed(script(body));
    CHECK(maximum_events.event_count == 2048);
    CHECK(maximum_events.events[2047].size == 3);
    CHECK((maximum_events.events[2047].bytes == std::array<std::uint8_t, 3>{0x90, 0x24, 1}));
    CHECK(parsed(script(body + "# trailing comment\n\n")).event_count == 2048);
    rejected(script(body + "0 disconnect\n"));

    CHECK(parsed(script('#' + std::string(255, 'x'))).event_count == 0);
    CHECK(parsed(script('#' + std::string(255, 'x') + "\r\n")).event_count == 0);
    rejected(script('#' + std::string(256, 'x')));
    CHECK(parsed(script(std::string(247, ' ') + "0 connect")).event_count == 1);
    rejected(script(std::string(248, ' ') + "0 connect"));
    CHECK(parsed(script(std::string(256, ' '))).event_count == 0);
    rejected(script(std::string(257, ' ')));

    const auto maximum = maximum_text();
    CHECK(maximum.size() == 65536);
    CHECK(parsed(maximum).event_count == 0);
    rejected(maximum + '\n');
}

class TemporaryDirectory {
public:
    TemporaryDirectory() {
        const auto root = fs::temp_directory_path();
        const auto tick = std::chrono::steady_clock::now().time_since_epoch().count();
        for (unsigned attempt = 0; attempt < 100; ++attempt) {
            path_ = root / ("hammond-midi-replay-" + std::to_string(tick) + '-' + std::to_string(attempt));
            std::error_code error;
            if (fs::create_directory(path_, error)) return;
        }
        fail("create isolated temporary directory", __LINE__);
    }
    ~TemporaryDirectory() { std::error_code error; fs::remove_all(path_, error); }
    [[nodiscard]] const fs::path& path() const { return path_; }
private:
    fs::path path_;
};

void write(const fs::path& path, std::string_view contents) {
    std::ofstream output{path, std::ios::binary};
    CHECK(output.is_open());
    output.write(contents.data(), static_cast<std::streamsize>(contents.size()));
    output.close();
    CHECK(output.good());
}

void load_rejected(const fs::path& path) {
    auto destination = sentinel();
    const auto before = destination;
    std::string error;
    CHECK(!load_midi_replay(path, destination, error));
    CHECK(!error.empty());
    same_plan(destination, before);
    ++totals.load_rejections;
}

void file_admission() {
    const TemporaryDirectory temporary;
    const auto unicode_directory = temporary.path() / fs::path{u8"MIDI replay é 音"};
    CHECK(fs::create_directory(unicode_directory));
    const auto regular = unicode_directory / fs::path{u8"entrée data.b3midi"};
    const auto source = script("0 connect\n0 bytes 90 3C 7F\n249 disconnect\n");
    write(regular, source);
    const auto expected = parsed(source);
    auto destination = sentinel();
    std::string error = "clear this";
    CHECK_DETAIL(load_midi_replay(regular, destination, error), error);
    CHECK(error.empty());
    same_plan(destination, expected);
    ++totals.loaded;
    write(regular, script("0 bytes FF\n"));
    same_plan(destination, expected); // Loading copies, never lazily rereads.
    write(regular, source);

    load_rejected(fs::path{});
    auto embedded_nul = regular.native();
    embedded_nul.push_back(fs::path::value_type{});
    embedded_nul += fs::path{".suffix"}.native();
    load_rejected(fs::path{embedded_nul});
    load_rejected(temporary.path() / "missing.b3midi");
    load_rejected(temporary.path());
    const auto bad = temporary.path() / "bad.b3midi";
    write(bad, script("0 connect\n250 bytes 80 3C 00\n"));
    load_rejected(bad);
    write(bad, "");
    load_rejected(bad);

    const auto maximum = temporary.path() / "maximum.b3midi";
    const auto maximum_source = maximum_text();
    write(maximum, maximum_source);
    CHECK_DETAIL(load_midi_replay(maximum, destination, error), error);
    CHECK(error.empty() && destination.event_count == 0 && destination.duration_ms == 250);
    ++totals.loaded;
    write(maximum, maximum_source + '\n');
    load_rejected(maximum);
    const auto sparse = temporary.path() / "oversized-sparse.b3midi";
    write(sparse, script(""));
    fs::resize_file(sparse, 64U * 1024U * 1024U);
    load_rejected(sparse);

    const auto link = temporary.path() / "leaf-link.b3midi";
    std::error_code symlink_error;
    fs::create_symlink(regular, link, symlink_error);
    if (!symlink_error) {
        load_rejected(link);
        const auto dangling = temporary.path() / "dangling-link.b3midi";
        fs::create_symlink(temporary.path() / "absent", dangling);
        load_rejected(dangling);
        const auto parent_link = temporary.path() / "permitted-parent-link";
        fs::create_directory_symlink(unicode_directory, parent_link);
        load_rejected(parent_link);
        CHECK_DETAIL(load_midi_replay(parent_link / regular.filename(), destination, error), error);
        CHECK(error.empty());
        same_plan(destination, expected); // Only the final path component is restricted.
        ++totals.loaded;
    } else {
#if defined(__unix__) || defined(__APPLE__)
        CHECK_DETAIL(false, symlink_error.message());
#else
        ++totals.capability_skips;
        std::cout << "Symlink admission not run: " << symlink_error.message() << '\n';
#endif
    }
#if defined(__unix__) || defined(__APPLE__)
    const auto fifo = temporary.path() / "not-a-regular-file";
    CHECK(::mkfifo(fifo.c_str(), 0600) == 0);
    load_rejected(fifo); // No writer; rejection must not wait for an input stream.
    load_rejected(fs::path{"/dev/null"});
#endif
}

void decoder_admission_from_script() {
    const auto plan = parsed(script(
        "0 bytes 90\n0 bytes 00 FF 80\n0 bytes 90 80 01\n0 bytes F8\n"
        "0 bytes C0 01\n0 bytes 9F 3C 7F\n0 bytes 92 3D 7F\n0 bytes 90 3C 7F\n"));
    constexpr std::array expected{
        MidiDecodeStatus::Malformed, MidiDecodeStatus::Malformed, MidiDecodeStatus::Malformed,
        MidiDecodeStatus::Unsupported, MidiDecodeStatus::Unsupported,
        MidiDecodeStatus::UnmappedChannel, MidiDecodeStatus::OutOfRange, MidiDecodeStatus::Action};
    MidiInbox inbox;
    MidiInput input;
    CHECK(input.begin_epoch());
    CHECK(plan.event_count == expected.size());
    for (std::size_t index = 0; index < plan.event_count; ++index) {
        const auto& event = plan.events[index];
        CHECK(inbox.push(std::span{event.bytes.data(), event.size}, index) == MidiPushResult::Accepted);
    }
    for (std::size_t index = 0; index < expected.size(); ++index) {
        MidiPacket packet;
        CHECK(inbox.pop(packet));
        CHECK(packet.arrival_ns == index);
        CHECK(input.decode(packet).status == expected[index]);
    }
    CHECK(inbox.pending() == 0);
    CHECK(input.diagnostics().packets == 8 && input.diagnostics().actions == 1);
    CHECK(input.diagnostics().malformed == 3);
}

void actual_burst_overflow_from_script() {
    std::string body = "0 connect\n";
    for (unsigned index = 0; index < 257; ++index) body += "0 bytes 90 3C 01\n";
    const auto plan = parsed(script(body));
    CHECK(plan.event_count == 258 && plan.events[0].kind == MidiReplayKind::Connect);
    MidiInbox inbox;
    for (std::size_t index = 1; index < plan.event_count; ++index) {
        const auto& event = plan.events[index];
        CHECK(event.at_ms == 0 && event.kind == MidiReplayKind::Bytes);
        const auto result = inbox.push(std::span{event.bytes.data(), event.size}, 0);
        CHECK(result == (index <= 256 ? MidiPushResult::Accepted : MidiPushResult::Overflow));
    }
    const auto diagnostics = inbox.diagnostics();
    CHECK(inbox.pending() == 256);
    CHECK(diagnostics.received_packets == 257 && diagnostics.accepted_packets == 256);
    CHECK(diagnostics.overflow_events == 1 && diagnostics.faults == 1);
    MidiPacket destination{{0xDE, 0xAD, 0xBE}, 253, 91};
    CHECK(!inbox.pop(destination));
    CHECK((destination.bytes == std::array<std::uint8_t, 3>{0xDE, 0xAD, 0xBE}));
    CHECK(destination.size == 253 && destination.arrival_ns == 91);
    inbox.reset_quiescent();
    CHECK(inbox.pending() == 0 && inbox.faults() == 0);
    CHECK(inbox.diagnostics().discarded_packets == 256);
}

} // namespace

int main() {
    grammar_and_owned_storage();
    every_raw_byte_value();
    malformed_syntax_and_ascii();
    duration_and_order_boundaries();
    resource_limits();
    file_admission();
    decoder_admission_from_script();
    actual_burst_overflow_from_script();
    std::cout << "Standalone MIDI replay acceptance: 8 scenarios passed; "
              << totals.parsed << " parsed, " << totals.parse_rejections << " parse rejections, "
              << totals.loaded << " loaded, " << totals.load_rejections << " load rejections, "
              << totals.capability_skips << " capability skips\n";
}
