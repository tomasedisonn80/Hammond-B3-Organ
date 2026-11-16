#include "ControlFileInput.h"

#include "hammond/ControlStateIO.h"

#include <array>
#include <cerrno>
#include <cstdint>
#include <sstream>
#include <string_view>
#include <system_error>
#include <utility>

#ifdef _WIN32
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#else
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#endif

namespace hammond::tools {
namespace {

constexpr std::size_t kDiagnosticBytes = 256;

[[nodiscard]] ControlFileInputResult failure(ControlFileInputStatus status,
                                             std::string reason) {
    if (reason.size() > kDiagnosticBytes) reason.resize(kDiagnosticBytes);
    return {status, std::move(reason)};
}

[[nodiscard]] std::string system_message(int code) {
#ifdef _WIN32
    return std::error_code(code, std::system_category()).message();
#else
    return std::error_code(code, std::generic_category()).message();
#endif
}

#ifdef _WIN32
[[nodiscard]] bool native_equal(std::wstring_view a, std::wstring_view b) noexcept {
    if (a.size() != b.size()) return false;
    for (std::size_t index = 0; index < a.size(); ++index) {
        const auto fold = [](wchar_t c) { return c >= L'A' && c <= L'Z' ? c + (L'a' - L'A') : c; };
        if (fold(a[index]) != fold(b[index])) return false;
    }
    return true;
}

// Reject special namespaces before CreateFileW: opening a named pipe or console
// can block before there is a handle whose type we can inspect. Extended native
// namespaces are deliberately excluded from this portable offline input policy.
[[nodiscard]] bool special_windows_path(const std::filesystem::path& path) {
    std::wstring native = path.native();
    for (auto& c : native) if (c == L'/') c = L'\\';
    if (native.starts_with(L"\\\\.\\") || native.starts_with(L"\\\\?\\") ||
        native.starts_with(L"\\??\\") || native.starts_with(L"\\\\??\\")) return true;
    if (native.starts_with(L"\\\\")) {
        const auto server_end = native.find(L'\\', 2);
        if (server_end != std::wstring::npos) {
            const auto share_end = native.find(L'\\', server_end + 1);
            const auto share = std::wstring_view(native).substr(server_end + 1,
                share_end == std::wstring::npos ? share_end : share_end - server_end - 1);
            if (native_equal(share, L"pipe")) return true;
        }
    }
    for (std::size_t first = 0; first < native.size();) {
        const auto last = native.find(L'\\', first);
        auto component = std::wstring_view(native).substr(first,
            last == std::wstring::npos ? last : last - first);
        const auto extension = component.find_first_of(L".:");
        component = component.substr(0, extension);
        while (!component.empty() && component.back() == L' ') component.remove_suffix(1);
        if (native_equal(component, L"con") || native_equal(component, L"prn") ||
            native_equal(component, L"aux") || native_equal(component, L"nul") ||
            native_equal(component, L"conin$") || native_equal(component, L"conout$")) return true;
        if (component.size() == 4 &&
            (native_equal(component.substr(0, 3), L"com") ||
             native_equal(component.substr(0, 3), L"lpt")) &&
            ((component[3] >= L'1' && component[3] <= L'9') ||
             component[3] == L'\u00b9' || component[3] == L'\u00b2' || component[3] == L'\u00b3')) return true;
        if (last == std::wstring::npos) break;
        first = last + 1;
    }
    return false;
}
#endif

} // namespace

ControlFileInputResult read_control_file(const std::filesystem::path& path,
                                         ControlFileInput& destination) {
    std::array<char, kMaxControlStateBytes + 1> buffer{};
    std::size_t count = 0;
#ifdef _WIN32
    if (special_windows_path(path)) {
        return failure(ControlFileInputStatus::NotRegularFile,
            "Control input must not use a device, pipe or native namespace");
    }
    const HANDLE handle = CreateFileW(path.c_str(), GENERIC_READ,
        FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE, nullptr, OPEN_EXISTING,
        FILE_FLAG_OPEN_REPARSE_POINT | FILE_FLAG_BACKUP_SEMANTICS, nullptr);
    if (handle == INVALID_HANDLE_VALUE) {
        return failure(ControlFileInputStatus::Unavailable,
            "Could not open control input: " + system_message(static_cast<int>(GetLastError())));
    }
    const auto finish = [handle](ControlFileInputStatus status, const char* reason, int code = 0) {
        if (CloseHandle(handle) == 0) {
            return failure(ControlFileInputStatus::Unavailable,
                "Could not close control input: " + system_message(static_cast<int>(GetLastError())));
        }
        return failure(status, std::string(reason) + (code == 0 ? "" : ": " + system_message(code)));
    };
    BY_HANDLE_FILE_INFORMATION info{};
    if (GetFileInformationByHandle(handle, &info) == 0) {
        return finish(ControlFileInputStatus::Unavailable, "Could not inspect opened control input",
            static_cast<int>(GetLastError()));
    }
    if (GetFileType(handle) != FILE_TYPE_DISK ||
        (info.dwFileAttributes & (FILE_ATTRIBUTE_DIRECTORY | FILE_ATTRIBUTE_REPARSE_POINT)) != 0) {
        return finish(ControlFileInputStatus::NotRegularFile,
            "Control input must be a regular file, not a link, directory or device");
    }
    if (info.nFileSizeHigh != 0 || info.nFileSizeLow > kMaxControlStateBytes) {
        return finish(ControlFileInputStatus::TooLarge, "Control input exceeds the 16 KiB byte limit");
    }
    while (count < buffer.size()) {
        DWORD received = 0;
        if (ReadFile(handle, buffer.data() + count,
                static_cast<DWORD>(buffer.size() - count), &received, nullptr) == 0) {
            return finish(ControlFileInputStatus::Unavailable, "Could not read control input",
                static_cast<int>(GetLastError()));
        }
        if (received == 0) break;
        count += static_cast<std::size_t>(received);
    }
    const auto closed = finish(ControlFileInputStatus::Read, "");
#else
    int handle;
    do {
        handle = ::open(path.c_str(), O_RDONLY | O_NOFOLLOW | O_NONBLOCK | O_CLOEXEC);
    } while (handle < 0 && errno == EINTR);
    if (handle < 0) {
        const int code = errno;
        return failure(code == ELOOP ? ControlFileInputStatus::NotRegularFile :
            ControlFileInputStatus::Unavailable,
            "Could not open control input without following links: " + system_message(code));
    }
    const auto finish = [handle](ControlFileInputStatus status, const char* reason, int code = 0) {
        // Retrying close after EINTR can close a reused descriptor on some OSes.
        if (::close(handle) != 0) {
            return failure(ControlFileInputStatus::Unavailable,
                "Could not close control input: " + system_message(errno));
        }
        return failure(status, std::string(reason) + (code == 0 ? "" : ": " + system_message(code)));
    };
    struct stat info {};
    int inspected;
    do { inspected = ::fstat(handle, &info); } while (inspected != 0 && errno == EINTR);
    if (inspected != 0) {
        return finish(ControlFileInputStatus::Unavailable, "Could not inspect opened control input", errno);
    }
    if (!S_ISREG(info.st_mode)) {
        return finish(ControlFileInputStatus::NotRegularFile,
            "Control input must be a regular file, not a link, directory or device");
    }
    if (info.st_size < 0 || static_cast<std::uintmax_t>(info.st_size) > kMaxControlStateBytes) {
        return finish(ControlFileInputStatus::TooLarge, "Control input exceeds the 16 KiB byte limit");
    }
    while (count < buffer.size()) {
        const auto received = ::read(handle, buffer.data() + count, buffer.size() - count);
        if (received < 0) {
            if (errno == EINTR) continue;
            return finish(ControlFileInputStatus::Unavailable, "Could not read control input", errno);
        }
        if (received == 0) break;
        count += static_cast<std::size_t>(received);
    }
    const auto closed = finish(ControlFileInputStatus::Read, "");
#endif
    if (closed.status != ControlFileInputStatus::Read) return closed;
    if (count > kMaxControlStateBytes) {
        return failure(ControlFileInputStatus::TooLarge, "Control input exceeds the 16 KiB byte limit");
    }
    const std::string bytes(buffer.data(), count);
    std::istringstream input(bytes);
    ControlFileInput candidate;
    std::string error;
    if (!parse_controls(input, candidate.controls, error) ||
        !serialize_controls(candidate.controls, candidate.canonical_controls, error)) {
        return failure(ControlFileInputStatus::InvalidPayload, std::move(error));
    }
    // Only the successful core parser admits the header. Extract provenance
    // afterward, including valid leading ASCII whitespace and legacy versions.
    const auto header = bytes.find_first_not_of(" \t\r\n\f\v");
    candidate.source_version = static_cast<unsigned>(bytes.at(header + 10) - '0');
    candidate.source_bytes = count;
    destination = std::move(candidate);
    return {ControlFileInputStatus::Read, {}};
}

} // namespace hammond::tools
