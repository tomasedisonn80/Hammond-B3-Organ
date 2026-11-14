#include "MidiReplay.h"

#include <charconv>
#include <system_error>

#if defined(_WIN32)
#ifndef NOMINMAX
#define NOMINMAX
#endif
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
#else
#include <cerrno>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#endif

namespace hammond::standalone {
namespace {

[[nodiscard]] bool unsigned_integer(std::string_view text, std::uint32_t& destination) noexcept {
    if (text.empty() || text.front() == '+') return false;
    std::uint32_t candidate{};
    const auto result = std::from_chars(text.data(), text.data() + text.size(), candidate);
    if (result.ec != std::errc{} || result.ptr != text.data() + text.size()) return false;
    destination = candidate;
    return true;
}

[[nodiscard]] bool hex_byte(std::string_view text, std::uint8_t& destination) noexcept {
    if (text.size() != 2) return false;
    unsigned int value = 0;
    for (const char character : text) {
        unsigned int digit = 0;
        if (character >= '0' && character <= '9') digit = static_cast<unsigned int>(character - '0');
        else if (character >= 'A' && character <= 'F') digit = static_cast<unsigned int>(character - 'A') + 10U;
        else if (character >= 'a' && character <= 'f') digit = static_cast<unsigned int>(character - 'a') + 10U;
        else return false;
        value = value * 16U + digit;
    }
    destination = static_cast<std::uint8_t>(value);
    return true;
}

struct Tokens {
    std::array<std::string_view, 5> items{};
    std::size_t count{0};
};

[[nodiscard]] bool split(std::string_view line, Tokens& result) noexcept {
    while (!line.empty()) {
        const auto first = line.find_first_not_of(" \t");
        if (first == std::string_view::npos) return true;
        line.remove_prefix(first);
        if (result.count == result.items.size()) return false;
        const auto end = line.find_first_of(" \t");
        result.items[result.count++] = line.substr(0, end);
        if (end == std::string_view::npos) return true;
        line.remove_prefix(end);
    }
    return true;
}

[[nodiscard]] bool next_line(std::string_view& source, std::string_view& line) noexcept {
    if (source.empty()) return false;
    const auto end = source.find('\n');
    line = source.substr(0, end);
    if (!line.empty() && line.back() == '\r') line.remove_suffix(1);
    if (end == std::string_view::npos) source = {};
    else source.remove_prefix(end + 1);
    return true;
}

[[nodiscard]] bool line_error(std::size_t number, std::string_view message, std::string& error) {
    error = "MIDI replay line " + std::to_string(number) + ": " + std::string(message);
    return false;
}

[[nodiscard]] bool valid_text(std::string_view source, std::string& error) {
    if (source.empty() || source.size() > kMidiReplayMaxBytes) {
        error = "MIDI replay must contain 1..65536 bytes";
        return false;
    }
    std::size_t line_number = 1;
    std::size_t line_bytes = 0;
    for (std::size_t index = 0; index < source.size(); ++index) {
        const auto byte = static_cast<unsigned char>(source[index]);
        if ((byte < 0x20U && byte != '\t' && byte != '\n' && byte != '\r') || byte > 0x7EU ||
            (byte == '\r' && (index + 1 == source.size() || source[index + 1] != '\n'))) {
            error = "MIDI replay requires printable ASCII, tabs, and LF or CRLF line endings";
            return false;
        }
        if (byte == '\n') {
            ++line_number;
            line_bytes = 0;
        } else if (byte != '\r' && ++line_bytes > kMidiReplayMaxLineBytes) {
            return line_error(line_number, "more than 256 bytes excluding the line ending", error);
        }
    }
    return true;
}

// Open the leaf itself, then inspect that same handle. Do not redirect this
// bounded data loader through a leaf symlink or into a FIFO/device.
[[nodiscard]] bool read_source(const std::filesystem::path& path,
                               std::array<char, kMidiReplayMaxBytes + 1>& bytes,
                               std::size_t& size, std::string& error) {
    if (path.empty() || path.native().find(typename std::filesystem::path::value_type{}) !=
                            std::filesystem::path::string_type::npos) {
        error = "MIDI replay path is empty or contains NUL";
        return false;
    }
#if defined(_WIN32)
    struct File {
        HANDLE value;
        ~File() { CloseHandle(value); }
    };
    const auto handle = CreateFileW(path.c_str(), GENERIC_READ, FILE_SHARE_READ, nullptr,
        OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL | FILE_FLAG_OPEN_REPARSE_POINT, nullptr);
    if (handle == INVALID_HANDLE_VALUE) {
        error = "Cannot open MIDI replay file (Windows error " + std::to_string(GetLastError()) + ")";
        return false;
    }
    const File file{handle};
    BY_HANDLE_FILE_INFORMATION info{};
    if (GetFileType(file.value) != FILE_TYPE_DISK || !GetFileInformationByHandle(file.value, &info) ||
        (info.dwFileAttributes & (FILE_ATTRIBUTE_DIRECTORY | FILE_ATTRIBUTE_REPARSE_POINT)) != 0) {
        error = "MIDI replay must be a regular file with a nonsymlink leaf";
        return false;
    }
    if (info.nFileSizeHigh != 0 || info.nFileSizeLow > kMidiReplayMaxBytes) {
        error = "MIDI replay exceeds 65536 bytes";
        return false;
    }
    const auto expected_size = static_cast<std::size_t>(info.nFileSizeLow);
    size = 0;
    while (size < bytes.size()) {
        DWORD obtained = 0;
        if (!ReadFile(file.value, bytes.data() + size,
                      static_cast<DWORD>(bytes.size() - size), &obtained, nullptr)) {
            error = "Cannot read complete MIDI replay file";
            return false;
        }
        if (obtained == 0) break;
        size += static_cast<std::size_t>(obtained);
    }
#else
    struct File {
        int value;
        ~File() { close(value); }
    };
    const int descriptor = open(path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW | O_NONBLOCK);
    if (descriptor < 0) {
        error = "Cannot open nonsymlink MIDI replay file: " +
            std::error_code(errno, std::generic_category()).message();
        return false;
    }
    const File file{descriptor};
    struct stat info{};
    if (fstat(file.value, &info) != 0 || !S_ISREG(info.st_mode)) {
        error = "MIDI replay must be a regular file with a nonsymlink leaf";
        return false;
    }
    if (info.st_size < 0 || static_cast<std::uintmax_t>(info.st_size) > kMidiReplayMaxBytes) {
        error = "MIDI replay exceeds 65536 bytes";
        return false;
    }
    const auto expected_size = static_cast<std::size_t>(info.st_size);
    size = 0;
    while (size < bytes.size()) {
        const auto obtained = read(file.value, bytes.data() + size, bytes.size() - size);
        if (obtained < 0) {
            if (errno == EINTR) continue;
            error = "Cannot read complete MIDI replay file";
            return false;
        }
        if (obtained == 0) break;
        size += static_cast<std::size_t>(obtained);
    }
#endif
    if (size > kMidiReplayMaxBytes || size != expected_size) {
        error = "MIDI replay changed size while reading or exceeds 65536 bytes";
        return false;
    }
    return true;
}

} // namespace

bool parse_midi_replay(std::string_view source, MidiReplayPlan& destination, std::string& error) {
    if (!valid_text(source, error)) return false;
    MidiReplayPlan candidate;
    std::string_view line;
    if (!next_line(source, line) || line != kMidiReplayFormat) {
        return line_error(1, "expected B3MIDIREPLAY1", error);
    }
    Tokens duration;
    if (!next_line(source, line) || !split(line, duration) || duration.count != 2 ||
        duration.items[0] != "duration_ms" || !unsigned_integer(duration.items[1], candidate.duration_ms) ||
        candidate.duration_ms < kMidiReplayMinimumDurationMs ||
        candidate.duration_ms > kMidiReplayMaximumDurationMs) {
        return line_error(2, "expected duration_ms N with N in 250..10000", error);
    }
    std::size_t line_number = 2;
    while (next_line(source, line)) {
        ++line_number;
        const auto first = line.find_first_not_of(" \t");
        if (first == std::string_view::npos || line[first] == '#') continue;
        Tokens fields;
        if (!split(line, fields) || fields.count < 2) {
            return line_error(line_number, "invalid or trailing record fields", error);
        }
        if (candidate.event_count == candidate.events.size()) {
            return line_error(line_number, "more than 2048 events", error);
        }
        MidiReplayEvent event;
        if (!unsigned_integer(fields.items[0], event.at_ms) || event.at_ms >= candidate.duration_ms ||
            (candidate.event_count != 0 && event.at_ms < candidate.events[candidate.event_count - 1].at_ms)) {
            return line_error(line_number, "event times must be nondecreasing and less than duration_ms", error);
        }
        const auto action = fields.items[1];
        if (action == "bytes") {
            if (fields.count < 3 || fields.count > 5) {
                return line_error(line_number, "expected bytes HH [HH [HH]]", error);
            }
            event.kind = MidiReplayKind::Bytes;
            event.size = static_cast<std::uint8_t>(fields.count - 2);
            for (std::size_t index = 0; index < event.size; ++index) {
                if (!hex_byte(fields.items[index + 2], event.bytes[index])) {
                    return line_error(line_number, "each raw byte must have exactly two hexadecimal digits", error);
                }
            }
        } else if (action == "connect" || action == "disconnect") {
            if (fields.count != 2) return line_error(line_number, "trailing action fields", error);
            event.kind = action == "connect" ? MidiReplayKind::Connect : MidiReplayKind::Disconnect;
        } else if (action == "fault") {
            if (fields.count != 3 || fields.items[2] != "backend") {
                return line_error(line_number, "expected fault backend", error);
            }
            event.kind = MidiReplayKind::BackendFault;
        } else {
            return line_error(line_number, "unknown action", error);
        }
        candidate.events[candidate.event_count++] = event;
    }
    destination = candidate;
    error.clear();
    return true;
}

bool load_midi_replay(const std::filesystem::path& path, MidiReplayPlan& destination, std::string& error) {
    std::array<char, kMidiReplayMaxBytes + 1> bytes{};
    std::size_t size = 0;
    if (!read_source(path, bytes, size, error)) return false;
    return parse_midi_replay({bytes.data(), size}, destination, error);
}

} // namespace hammond::standalone
