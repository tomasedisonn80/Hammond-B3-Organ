#include "RegistrationLibrary.h"

#include "hammond/ControlStateIO.h"

#include <algorithm>
#include <array>
#include <atomic>
#include <cerrno>
#include <chrono>
#include <exception>
#include <sstream>
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

namespace hammond::standalone {
namespace {
namespace fs = std::filesystem;

[[nodiscard]] std::string bounded(std::string text) {
    if (text.size() > kRegistrationLibraryMaxDiagnosticBytes) {
        text.resize(kRegistrationLibraryMaxDiagnosticBytes);
    }
    return text;
}

[[nodiscard]] bool ascii_alphanumeric(char c) noexcept {
    return (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') || (c >= '0' && c <= '9');
}

[[nodiscard]] char fold(char c) noexcept {
    return c >= 'A' && c <= 'Z' ? static_cast<char>(c + ('a' - 'A')) : c;
}

[[nodiscard]] std::string folded(std::string_view text) {
    std::string result(text);
    for (auto& c : result) c = fold(c);
    return result;
}

[[nodiscard]] bool same_ascii_name(std::string_view a, std::string_view b) noexcept {
    return a.size() == b.size() && std::equal(a.begin(), a.end(), b.begin(),
        [](char x, char y) { return fold(x) == fold(y); });
}

[[nodiscard]] bool missing(const std::error_code& error) noexcept {
    return error == std::errc::no_such_file_or_directory;
}

[[nodiscard]] bool decode_key(std::string_view key, LibraryEntry& entry) {
    for (const auto scope : {RegistrationScope::Registration, RegistrationScope::Performance}) {
        const auto suffix = registration_scope_suffix(scope);
        if (!key.ends_with(suffix)) continue;
        const auto name = key.substr(0, key.size() - suffix.size());
        if (!is_valid_registration_name(name)) return false;
        entry.key = key;
        entry.name = name;
        entry.scope = scope;
        return true;
    }
    return false;
}

// Inspect native code units before any narrowing. Recognition still counts a
// candidate whose stem cannot be represented by the portable name grammar.
[[nodiscard]] std::optional<RegistrationScope> native_scope(const fs::path& filename) {
    const auto& native = filename.native();
    for (const auto scope : {RegistrationScope::Registration, RegistrationScope::Performance}) {
        const auto suffix = registration_scope_suffix(scope);
        if (native.size() < suffix.size()) continue;
        const auto start = native.size() - suffix.size();
        bool matches = true;
        for (std::size_t i = 0; i < suffix.size(); ++i) {
            if (native[start + i] != static_cast<fs::path::value_type>(suffix[i])) {
                matches = false;
                break;
            }
        }
        if (matches) return scope;
    }
    return std::nullopt;
}

[[nodiscard]] bool native_ascii(const fs::path& filename, std::string& text) {
    text.clear();
    const auto& native = filename.native();
    if (native.size() > kRegistrationLibraryMaxNameBytes +
            registration_scope_suffix(RegistrationScope::Registration).size()) return false;
    for (const auto c : native) {
        // Conversion to an unsigned value also rejects negative signed chars.
        const auto value = static_cast<std::uint32_t>(c);
        if (value > 127U) return false;
        text.push_back(static_cast<char>(value));
    }
    return true;
}

void entry_error(LibraryEntry& entry, LibraryEntryStatus status, std::string reason) {
    entry.status = status;
    entry.reason = bounded(std::move(reason));
    entry.controls.reset();
}

[[nodiscard]] std::string system_message(int code) {
#ifdef _WIN32
    return std::error_code(code, std::system_category()).message();
#else
    return std::error_code(code, std::generic_category()).message();
#endif
}

[[nodiscard]] bool read_regular(const fs::path& path, std::string& bytes, LibraryEntry& entry) {
    std::array<char, kMaxControlStateBytes + 1> buffer{};
    std::size_t count = 0;
#ifdef _WIN32
    const HANDLE handle = CreateFileW(path.c_str(), GENERIC_READ,
        FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE, nullptr, OPEN_EXISTING,
        FILE_FLAG_OPEN_REPARSE_POINT | FILE_FLAG_BACKUP_SEMANTICS, nullptr);
    if (handle == INVALID_HANDLE_VALUE) {
        entry_error(entry, LibraryEntryStatus::Unavailable,
            "Could not open entry: " + system_message(static_cast<int>(GetLastError())));
        return false;
    }
    BY_HANDLE_FILE_INFORMATION info{};
    if (GetFileInformationByHandle(handle, &info) == 0) {
        const auto code = static_cast<int>(GetLastError());
        (void)CloseHandle(handle);
        entry_error(entry, LibraryEntryStatus::Unavailable,
            "Could not inspect opened entry: " + system_message(code));
        return false;
    }
    if (GetFileType(handle) != FILE_TYPE_DISK ||
        (info.dwFileAttributes & (FILE_ATTRIBUTE_DIRECTORY | FILE_ATTRIBUTE_REPARSE_POINT)) != 0) {
        (void)CloseHandle(handle);
        entry_error(entry, LibraryEntryStatus::NotRegularFile, "Entry must be a regular file, not a link or directory");
        return false;
    }
    if (info.nFileSizeHigh != 0 || info.nFileSizeLow > kMaxControlStateBytes) {
        (void)CloseHandle(handle);
        entry_error(entry, LibraryEntryStatus::TooLarge, "Entry exceeds the 16 KiB byte limit");
        return false;
    }
    while (count < buffer.size()) {
        DWORD received = 0;
        if (ReadFile(handle, buffer.data() + count,
                static_cast<DWORD>(buffer.size() - count), &received, nullptr) == 0) {
            const auto code = static_cast<int>(GetLastError());
            (void)CloseHandle(handle);
            entry_error(entry, LibraryEntryStatus::Unavailable, "Could not read entry: " + system_message(code));
            return false;
        }
        if (received == 0) break;
        count += static_cast<std::size_t>(received);
    }
    if (CloseHandle(handle) == 0) {
        entry_error(entry, LibraryEntryStatus::Unavailable,
            "Could not close read entry: " + system_message(static_cast<int>(GetLastError())));
        return false;
    }
#else
    const int handle = ::open(path.c_str(), O_RDONLY | O_NOFOLLOW | O_NONBLOCK | O_CLOEXEC);
    if (handle < 0) {
        const int code = errno;
        entry_error(entry, code == ELOOP ? LibraryEntryStatus::NotRegularFile : LibraryEntryStatus::Unavailable,
            "Could not open entry without following links: " + system_message(code));
        return false;
    }
    struct stat info {};
    if (::fstat(handle, &info) != 0) {
        const int code = errno;
        (void)::close(handle);
        entry_error(entry, LibraryEntryStatus::Unavailable,
            "Could not inspect opened entry: " + system_message(code));
        return false;
    }
    if (!S_ISREG(info.st_mode)) {
        (void)::close(handle);
        entry_error(entry, LibraryEntryStatus::NotRegularFile, "Entry must be a regular file, not a link or directory");
        return false;
    }
    if (info.st_size < 0 || static_cast<std::uintmax_t>(info.st_size) > kMaxControlStateBytes) {
        (void)::close(handle);
        entry_error(entry, LibraryEntryStatus::TooLarge, "Entry exceeds the 16 KiB byte limit");
        return false;
    }
    while (count < buffer.size()) {
        const auto received = ::read(handle, buffer.data() + count, buffer.size() - count);
        if (received < 0) {
            const int code = errno;
            if (code == EINTR) continue;
            (void)::close(handle);
            entry_error(entry, LibraryEntryStatus::Unavailable, "Could not read entry: " + system_message(code));
            return false;
        }
        if (received == 0) break;
        count += static_cast<std::size_t>(received);
    }
    if (::close(handle) != 0) {
        entry_error(entry, LibraryEntryStatus::Unavailable, "Could not close read entry: " + system_message(errno));
        return false;
    }
#endif
    if (count > kMaxControlStateBytes) {
        entry_error(entry, LibraryEntryStatus::TooLarge, "Entry exceeds the 16 KiB byte limit");
        return false;
    }
    bytes.assign(buffer.data(), count);
    return true;
}

[[nodiscard]] LibraryEntry read_at(const fs::path& root, std::string_view key) {
    LibraryEntry entry;
    if (!decode_key(key, entry)) {
        entry.reason = "Invalid library filename or scope";
        return entry;
    }
    std::string bytes;
    if (!read_regular(root / entry.key, bytes, entry)) return entry;
    std::istringstream input(bytes);
    ControlSnapshot controls;
    std::string error;
    if (!parse_controls(input, controls, error)) {
        entry_error(entry, LibraryEntryStatus::InvalidPayload, std::move(error));
        return entry;
    }
    entry.status = LibraryEntryStatus::Valid;
    entry.controls = controls;
    return entry;
}

[[nodiscard]] LibraryCatalog failed_catalog(LibraryCatalog catalog, LibraryCatalogStatus status,
                                            std::string reason) {
    catalog.entries.clear();
    catalog.status = status;
    catalog.reason = bounded(std::move(reason));
    return catalog;
}

enum class NativeComparison { Same, Different, Uncertain };

[[nodiscard]] bool distinct_ascii_components(const fs::path& a, const fs::path& b) {
    const auto& x = a.native();
    const auto& y = b.native();
    const auto ascii = [](auto c) { return static_cast<std::uint32_t>(c) <= 127U; };
    if (!std::all_of(x.begin(), x.end(), ascii) || !std::all_of(y.begin(), y.end(), ascii)) return false;
    return x.size() != y.size() || !std::equal(x.begin(), x.end(), y.begin(),
        [](auto u, auto v) { return fold(static_cast<char>(u)) == fold(static_cast<char>(v)); });
}

// Exact non-ASCII code units are safe to compare. Different non-ASCII units may
// be aliases under a volume's case/normalization policy, so do not guess.
[[nodiscard]] NativeComparison portable_path_compare(const fs::path& a, const fs::path& b) {
    // Unicode length changes can misalign a flat native-string comparison. A
    // complete ASCII component pair, aligned by path boundaries, can still prove
    // distinction despite uncertainty elsewhere. Native identity and existing-
    // ancestor/suffix checks remain mandatory in distinct_from_protected.
    for (auto x = a.begin(), y = b.begin(); x != a.end() && y != b.end(); ++x, ++y) {
        if (distinct_ascii_components(*x, *y)) return NativeComparison::Different;
    }
    const auto& x = a.native();
    const auto& y = b.native();
    bool uncertain = false;
    bool different = x.size() != y.size();
    const auto size = std::min(x.size(), y.size());
    for (std::size_t i = 0; i < size; ++i) {
        if (x[i] == y[i]) continue;
        const auto u = static_cast<std::uint32_t>(x[i]);
        const auto v = static_cast<std::uint32_t>(y[i]);
        if (u > 127U || v > 127U) {
            uncertain = true;
        } else if (fold(static_cast<char>(u)) != fold(static_cast<char>(v))) {
            different = true;
        }
    }
    for (std::size_t i = size; i < x.size(); ++i) {
        if (static_cast<std::uint32_t>(x[i]) > 127U) uncertain = true;
    }
    for (std::size_t i = size; i < y.size(); ++i) {
        if (static_cast<std::uint32_t>(y[i]) > 127U) uncertain = true;
    }
    if (uncertain) return NativeComparison::Uncertain;
    return different ? NativeComparison::Different : NativeComparison::Same;
}

[[nodiscard]] bool ambiguous_native_path(const fs::path& path) {
#ifdef _WIN32
    for (const auto& component : path.relative_path()) {
        const auto& text = component.native();
        // Navigation components are resolved normally; they are not native
        // filenames whose trailing characters could conceal another spelling.
        if (text == L"." || text == L"..") continue;
        if (!text.empty() && (text.back() == L'.' || text.back() == L' ' ||
                text.find(L':') != std::wstring::npos)) return true;
    }
#else
    (void)path;
#endif
    return false;
}

struct PathIdentity {
    fs::path resolved;
    fs::path ancestor;
    fs::path suffix;
    bool exists{};
};

[[nodiscard]] bool identify_path(const fs::path& requested, PathIdentity& identity, std::string& error) {
    // Win32 normalization can remove a trailing dot or space. Inspect the
    // caller's spelling before absolute/weakly_canonical can erase it.
    if (ambiguous_native_path(requested)) {
        error = "Cannot establish distinctness for a native path with ambiguous components";
        return false;
    }
    std::error_code code;
    const auto absolute = fs::absolute(requested, code);
    if (code) {
        error = "Could not resolve protected path: " + code.message();
        return false;
    }
    identity.resolved = fs::weakly_canonical(absolute, code);
    if (code) {
        error = "Could not resolve protected path ancestors: " + code.message();
        return false;
    }
    if (ambiguous_native_path(identity.resolved)) {
        error = "Cannot establish distinctness for a native path with ambiguous components";
        return false;
    }
    const auto status = fs::status(identity.resolved, code);
    if (code && !missing(code)) {
        error = "Could not inspect protected path: " + code.message();
        return false;
    }
    identity.exists = fs::exists(status);
    if (!identity.exists) {
        code.clear();
        const auto leaf = fs::symlink_status(identity.resolved, code);
        if ((code && !missing(code)) || fs::is_symlink(leaf)) {
            error = "Cannot establish distinctness from an unresolved protected link";
            return false;
        }
    }
    identity.ancestor = identity.resolved.parent_path();
    identity.suffix = identity.resolved.filename();
    if (identity.ancestor.empty()) identity.ancestor = identity.resolved.root_path();
    for (;;) {
        code.clear();
        const auto parent = fs::status(identity.ancestor, code);
        if (!code && fs::is_directory(parent)) return true;
        if ((code && !missing(code)) || (!code && fs::exists(parent))) {
            error = "Protected path has an unavailable or non-directory ancestor";
            return false;
        }
        code.clear();
        const auto link = fs::symlink_status(identity.ancestor, code);
        if ((code && !missing(code)) || fs::is_symlink(link)) {
            error = "Protected path has an unresolved ancestor link";
            return false;
        }
        const auto parent_path = identity.ancestor.parent_path();
        if (parent_path.empty() || parent_path == identity.ancestor) {
            error = "Could not find an existing protected-path ancestor";
            return false;
        }
        identity.suffix = identity.ancestor.filename() / identity.suffix;
        identity.ancestor = parent_path;
    }
}

[[nodiscard]] bool distinct_from_protected(const fs::path& creation,
    std::span<const fs::path> protected_paths, std::string& error) {
    PathIdentity created;
    if (!identify_path(creation, created, error)) return false;
    for (const auto& path : protected_paths) {
        if (path.empty()) continue;
        PathIdentity protected_path;
        if (!identify_path(path, protected_path, error)) return false;
        const auto comparison = portable_path_compare(created.resolved, protected_path.resolved);
        if (comparison != NativeComparison::Different) {
            error = comparison == NativeComparison::Same ?
                "Library creation conflicts with a protected application path" :
                "Cannot establish distinctness from a protected application path";
            return false;
        }
        std::error_code code;
        if (created.exists && protected_path.exists) {
            const bool equivalent = fs::equivalent(created.resolved, protected_path.resolved, code);
            if (code || equivalent) {
                error = code ? "Could not compare existing protected paths: " + code.message() :
                    "Library creation aliases a protected application path";
                return false;
            }
        }
        const bool same_parent = fs::equivalent(created.ancestor, protected_path.ancestor, code);
        if (code) {
            error = "Could not compare protected-path ancestors: " + code.message();
            return false;
        }
        if (same_parent && portable_path_compare(created.suffix, protected_path.suffix) !=
                NativeComparison::Different) {
            error = "Library creation aliases a reserved protected filename";
            return false;
        }
    }
    return true;
}

class Staging {
public:
    fs::path directory;
    fs::path file;
    bool owned{};

    Staging() = default;
    Staging(const Staging&) = delete;
    Staging& operator=(const Staging&) = delete;
    ~Staging() {
        if (!owned) return;
        std::error_code ignored;
        (void)fs::remove(file, ignored);
        ignored.clear();
        (void)fs::remove(directory, ignored);
    }
    [[nodiscard]] std::string cleanup() {
        if (!owned) return {};
        owned = false;
        std::error_code file_error;
        (void)fs::remove(file, file_error);
        std::error_code directory_error;
        (void)fs::remove(directory, directory_error);
        if (file_error) return "Temporary file cleanup failed: " + file_error.message();
        if (directory_error) return "Temporary directory cleanup failed: " + directory_error.message();
        return {};
    }
};

[[nodiscard]] bool write_staged(const fs::path& file, std::string_view bytes, LibrarySaveResult& result) {
#ifdef _WIN32
    const HANDLE handle = CreateFileW(file.c_str(), GENERIC_WRITE, 0, nullptr, CREATE_NEW,
        FILE_ATTRIBUTE_NORMAL | FILE_FLAG_OPEN_REPARSE_POINT, nullptr);
    if (handle == INVALID_HANDLE_VALUE) {
        result.status = LibrarySaveStatus::WriteFailed;
        result.reason = "Could not open temporary file: " + system_message(static_cast<int>(GetLastError()));
        return false;
    }
    std::size_t written = 0;
    while (written < bytes.size()) {
        DWORD count = 0;
        if (WriteFile(handle, bytes.data() + written,
                static_cast<DWORD>(bytes.size() - written), &count, nullptr) == 0 || count == 0) {
            const auto code = static_cast<int>(GetLastError());
            (void)CloseHandle(handle);
            result.status = LibrarySaveStatus::WriteFailed;
            result.reason = "Could not write complete temporary file: " + system_message(code);
            return false;
        }
        written += static_cast<std::size_t>(count);
    }
    if (FlushFileBuffers(handle) == 0) {
        const auto code = static_cast<int>(GetLastError());
        (void)CloseHandle(handle);
        result.status = LibrarySaveStatus::FlushFailed;
        result.reason = "Could not flush temporary file: " + system_message(code);
        return false;
    }
    if (CloseHandle(handle) == 0) {
        result.status = LibrarySaveStatus::CloseFailed;
        result.reason = "Could not close temporary file: " + system_message(static_cast<int>(GetLastError()));
        return false;
    }
#else
    const int handle = ::open(file.c_str(), O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW | O_CLOEXEC, 0600);
    if (handle < 0) {
        result.status = LibrarySaveStatus::WriteFailed;
        result.reason = "Could not open temporary file: " + system_message(errno);
        return false;
    }
    std::size_t written = 0;
    while (written < bytes.size()) {
        const auto count = ::write(handle, bytes.data() + written, bytes.size() - written);
        if (count < 0 && errno == EINTR) continue;
        if (count <= 0) {
            const int code = count < 0 ? errno : EIO;
            (void)::close(handle);
            result.status = LibrarySaveStatus::WriteFailed;
            result.reason = "Could not write complete temporary file: " + system_message(code);
            return false;
        }
        written += static_cast<std::size_t>(count);
    }
    if (::fsync(handle) != 0) {
        const int code = errno;
        (void)::close(handle);
        result.status = LibrarySaveStatus::FlushFailed;
        result.reason = "Could not flush temporary file: " + system_message(code);
        return false;
    }
    if (::close(handle) != 0) {
        result.status = LibrarySaveStatus::CloseFailed;
        result.reason = "Could not close temporary file: " + system_message(errno);
        return false;
    }
#endif
    return true;
}

// This function performs exactly the publication syscall after authorization.
// There is deliberately no replace-existing fallback or existence precheck.
[[nodiscard]] bool publish_new(const fs::path& from, const fs::path& to, LibrarySaveResult& result) {
#ifdef _WIN32
    if (MoveFileExW(from.c_str(), to.c_str(), MOVEFILE_WRITE_THROUGH) != 0) return true;
    const auto native_code = GetLastError();
    const bool exists = native_code == ERROR_ALREADY_EXISTS || native_code == ERROR_FILE_EXISTS;
    const auto code = static_cast<int>(native_code);
#else
    if (::link(from.c_str(), to.c_str()) == 0) return true;
    const int code = errno;
    const bool exists = code == EEXIST;
#endif
    result.status = exists ? LibrarySaveStatus::NameExists : LibrarySaveStatus::CommitFailed;
    result.reason = exists ? "An entry with this name and scope already exists" :
        "Could not publish new entry without replacing a destination: " + system_message(code);
    return false;
}

[[nodiscard]] bool admit_save(const LibraryCatalog& catalog, std::string_view name,
                              RegistrationScope scope, bool staged, LibrarySaveResult& result) {
    if (!catalog.complete()) {
        result.status = catalog.status == LibraryCatalogStatus::CapacityExceeded ? LibrarySaveStatus::CapacityExceeded :
            catalog.status == LibraryCatalogStatus::InvalidRoot ? LibrarySaveStatus::InvalidRoot :
            LibrarySaveStatus::DirectoryUnavailable;
        result.reason = catalog.reason;
        return false;
    }
    if (catalog.candidate_count >= kRegistrationLibraryMaxEntries ||
        (!staged && catalog.directory_items >= kRegistrationLibraryMaxDirectoryItems)) {
        result.status = LibrarySaveStatus::CapacityExceeded;
        result.reason = "Library has no capacity for another entry";
        return false;
    }
    for (const auto& entry : catalog.entries) {
        if (entry.scope == scope && same_ascii_name(entry.name, name)) {
            result.status = LibrarySaveStatus::NameExists;
            result.reason = "An entry with this name and scope already exists";
            return false;
        }
    }
    return true;
}

} // namespace

bool is_valid_registration_scope(RegistrationScope scope) noexcept {
    return scope == RegistrationScope::Registration || scope == RegistrationScope::Performance;
}

bool is_valid_registration_name_draft(std::string_view name) noexcept {
    return name.size() <= kRegistrationLibraryMaxNameBytes &&
        std::all_of(name.begin(), name.end(), [](char c) {
            return ascii_alphanumeric(c) || c == ' ' || c == '-' || c == '_';
        });
}

bool is_valid_registration_name(std::string_view name) noexcept {
    if (name.empty() || !is_valid_registration_name_draft(name) ||
        !ascii_alphanumeric(name.front()) || !ascii_alphanumeric(name.back())) return false;
    if (same_ascii_name(name, "CON") || same_ascii_name(name, "PRN") ||
        same_ascii_name(name, "AUX") || same_ascii_name(name, "NUL")) return false;
    if (name.size() == 4 && name[3] >= '1' && name[3] <= '9' &&
        (same_ascii_name(name.substr(0, 3), "COM") || same_ascii_name(name.substr(0, 3), "LPT"))) return false;
    return true;
}

std::string_view registration_scope_suffix(RegistrationScope scope) noexcept {
    switch (scope) {
    case RegistrationScope::Registration: return ".b3registration";
    case RegistrationScope::Performance: return ".b3performance";
    }
    return {};
}

std::string_view registration_scope_label(RegistrationScope scope) noexcept {
    switch (scope) {
    case RegistrationScope::Registration: return "Registration";
    case RegistrationScope::Performance: return "Performance - current controls";
    }
    return "Invalid scope";
}

namespace {
[[nodiscard]] bool resolve_root(const fs::path& requested, fs::path& root, std::string& error,
                                LibraryCatalogStatus& failure) {
    failure = LibraryCatalogStatus::DirectoryUnavailable;
    if (requested.empty()) {
        failure = LibraryCatalogStatus::InvalidRoot;
        error = "Choose a library directory";
        return false;
    }
    if (ambiguous_native_path(requested)) {
        failure = LibraryCatalogStatus::InvalidRoot;
        error = "Library root has ambiguous native path components";
        return false;
    }
    std::error_code code;
    const auto absolute = fs::absolute(requested, code);
    if (code) {
        error = bounded("Could not resolve library directory: " + code.message());
        return false;
    }
    auto resolved = fs::weakly_canonical(absolute, code);
    if (code) {
        error = bounded("Could not resolve library directory ancestors: " + code.message());
        return false;
    }
    // Drop a trailing separator, retaining the filesystem root itself.
    if (resolved.filename().empty() && resolved.has_relative_path()) resolved = resolved.parent_path();
    if (ambiguous_native_path(resolved)) {
        failure = LibraryCatalogStatus::InvalidRoot;
        error = "Library root has ambiguous native path components";
        return false;
    }
    const auto status = fs::status(resolved, code);
    if (code && !missing(code)) {
        error = bounded("Library directory is unavailable: " + code.message());
        return false;
    }
    if (fs::exists(status) && !fs::is_directory(status)) {
        failure = LibraryCatalogStatus::InvalidRoot;
        error = "Library root must be a directory";
        return false;
    }
    if (!fs::exists(status)) {
        code.clear();
        const auto leaf = fs::symlink_status(resolved, code);
        if ((code && !missing(code)) || fs::is_symlink(leaf)) {
            if (fs::is_symlink(leaf)) failure = LibraryCatalogStatus::InvalidRoot;
            error = "Library root is an unresolved link or unavailable path";
            return false;
        }
    }
    root = std::move(resolved);
    error.clear();
    return true;
}
} // namespace

bool resolve_registration_library_root(const fs::path& requested, fs::path& root, std::string& error) {
    LibraryCatalogStatus failure{};
    return resolve_root(requested, root, error, failure);
}

LibraryCatalog scan_registration_library(const fs::path& requested, std::uint64_t generation) {
    LibraryCatalog catalog;
    catalog.generation = generation;
    fs::path root;
    std::string error;
    LibraryCatalogStatus failure{};
    if (!resolve_root(requested, root, error, failure)) {
        return failed_catalog(std::move(catalog), failure, std::move(error));
    }
    std::error_code code;
    fs::directory_iterator cursor(root, code);
    if (code) {
        if (missing(code)) {
            catalog.status = LibraryCatalogStatus::MissingDirectory;
            catalog.reason = "Library directory is missing; Save new may create it";
            return catalog;
        }
        return failed_catalog(std::move(catalog), LibraryCatalogStatus::DirectoryUnavailable,
            "Could not enumerate library directory: " + code.message());
    }
    const fs::directory_iterator end;
    for (; cursor != end; cursor.increment(code)) {
        if (code) break;
        ++catalog.directory_items;
        if (catalog.directory_items > kRegistrationLibraryMaxDirectoryItems) {
            return failed_catalog(std::move(catalog), LibraryCatalogStatus::CapacityExceeded,
                "Library exceeds the 512 directory-item limit");
        }
        const auto filename = cursor->path().filename();
        if (!native_scope(filename)) continue;
        ++catalog.candidate_count;
        if (catalog.candidate_count > kRegistrationLibraryMaxEntries) {
            return failed_catalog(std::move(catalog), LibraryCatalogStatus::CapacityExceeded,
                "Library exceeds the 128 candidate-entry limit");
        }
        std::string key;
        LibraryEntry decoded;
        if (!native_ascii(filename, key) || !decode_key(key, decoded)) {
            ++catalog.invalid_name_count;
            continue;
        }
        catalog.entries.push_back(read_at(root, key));
    }
    if (code) {
        return failed_catalog(std::move(catalog), LibraryCatalogStatus::DirectoryUnavailable,
            "Library enumeration failed: " + code.message());
    }
    std::sort(catalog.entries.begin(), catalog.entries.end(), [](const LibraryEntry& a, const LibraryEntry& b) {
        const auto left = folded(a.name);
        const auto right = folded(b.name);
        if (left != right) return left < right;
        if (a.scope != b.scope) return a.scope < b.scope;
        return a.key < b.key;
    });
    for (std::size_t first = 0; first < catalog.entries.size();) {
        std::size_t last = first + 1;
        while (last < catalog.entries.size() &&
            catalog.entries[first].scope == catalog.entries[last].scope &&
            same_ascii_name(catalog.entries[first].name, catalog.entries[last].name)) ++last;
        if (last - first > 1) {
            for (std::size_t i = first; i < last; ++i) {
                entry_error(catalog.entries[i], LibraryEntryStatus::Ambiguous,
                    "Ambiguous case-insensitive name in this scope");
                ++catalog.ambiguous_entry_count;
            }
        }
        first = last;
    }
    for (const auto& entry : catalog.entries) {
        if (!entry.valid() && entry.status != LibraryEntryStatus::Ambiguous) ++catalog.invalid_entry_count;
    }
    catalog.status = catalog.entries.empty() ? LibraryCatalogStatus::Empty : LibraryCatalogStatus::Ready;
    if (catalog.warning_count() != 0) {
        catalog.reason = "Scan completed with " + std::to_string(catalog.warning_count()) + " entry warnings";
    } else if (catalog.entries.empty()) {
        catalog.reason = "Library is empty";
    }
    return catalog;
}

LibraryEntry read_registration_entry(const fs::path& requested, std::string_view key) {
    LibraryEntry entry;
    if (!decode_key(key, entry)) {
        entry.reason = "Invalid library filename or scope";
        return entry;
    }
    fs::path root;
    std::string error;
    if (!resolve_registration_library_root(requested, root, error)) {
        entry_error(entry, LibraryEntryStatus::Unavailable, std::move(error));
        return entry;
    }
    return read_at(root, key);
}

LibrarySaveResult save_registration_entry_new(const fs::path& requested, std::string_view name,
    RegistrationScope scope, const ControlSnapshot& acknowledged,
    std::span<const fs::path> protected_paths, const LibraryAuthorizeCommit& authorize_commit) {
    LibrarySaveResult result;
    const auto fail = [&result](LibrarySaveStatus status, std::string reason) {
        result.status = status;
        result.reason = bounded(std::move(reason));
        return result;
    };
    if (!is_valid_registration_scope(scope)) return fail(LibrarySaveStatus::InvalidScope, "Invalid registration scope");
    if (!is_valid_registration_name(name)) return fail(LibrarySaveStatus::InvalidName, "Choose a valid portable name of 1 to 48 ASCII bytes");
    if (!is_valid_control_snapshot(acknowledged)) return fail(LibrarySaveStatus::InvalidControls, "Cannot save invalid acknowledged controls");
    if (!authorize_commit) return fail(LibrarySaveStatus::NotAuthorized, "A fresh commit authorization is required");
    fs::path root;
    std::string error;
    LibraryCatalogStatus root_failure{};
    if (!resolve_root(requested, root, error, root_failure)) return fail(
        root_failure == LibraryCatalogStatus::InvalidRoot ? LibrarySaveStatus::InvalidRoot :
        LibrarySaveStatus::DirectoryUnavailable, std::move(error));
    const auto initial = scan_registration_library(root);
    if (!admit_save(initial, name, scope, false, result)) return result;
    const std::string key = std::string(name) + std::string(registration_scope_suffix(scope));
    const auto destination = root / key;
    if (!distinct_from_protected(root, protected_paths, error) ||
        !distinct_from_protected(destination, protected_paths, error)) return fail(LibrarySaveStatus::ProtectedPath, std::move(error));
    if (initial.status == LibraryCatalogStatus::MissingDirectory) {
        std::error_code code;
        if (!fs::is_directory(root.parent_path(), code) || code) {
            return fail(LibrarySaveStatus::DirectoryUnavailable, "Library parent directory does not exist or is unavailable");
        }
        (void)fs::create_directory(root, code);
        if (code || !fs::is_directory(root, code) || code) {
            return fail(LibrarySaveStatus::DirectoryUnavailable, "Could not create the library directory: " + code.message());
        }
    }
    std::string bytes;
    if (!serialize_controls(acknowledged, bytes, error)) return fail(LibrarySaveStatus::InvalidControls, std::move(error));
    Staging staged;
    static std::atomic<std::uint64_t> serial{0};
    const auto stamp = std::chrono::steady_clock::now().time_since_epoch().count();
    for (std::size_t attempt = 0; attempt < kRegistrationLibraryTemporaryAttempts; ++attempt) {
        staged.directory = root / (".b3-library-save-" + std::to_string(stamp) + "-" +
            std::to_string(serial.fetch_add(1, std::memory_order_relaxed)));
        staged.file = staged.directory / "controls.tmp";
        if (!distinct_from_protected(staged.directory, protected_paths, error) ||
            !distinct_from_protected(staged.file, protected_paths, error)) return fail(LibrarySaveStatus::ProtectedPath, std::move(error));
#ifdef _WIN32
        if (CreateDirectoryW(staged.directory.c_str(), nullptr) != 0) {
            staged.owned = true;
            break;
        }
        const auto code = GetLastError();
        if (code != ERROR_ALREADY_EXISTS && code != ERROR_FILE_EXISTS) {
            return fail(LibrarySaveStatus::StagingFailed, "Could not reserve temporary directory: " + system_message(static_cast<int>(code)));
        }
#else
        if (::mkdir(staged.directory.c_str(), 0700) == 0) {
            staged.owned = true;
            break;
        }
        const int code = errno;
        if (code != EEXIST) return fail(LibrarySaveStatus::StagingFailed, "Could not reserve temporary directory: " + system_message(code));
#endif
    }
    if (!staged.owned) return fail(LibrarySaveStatus::StagingFailed, "Could not reserve a temporary directory in 32 attempts");
    const auto abort_staging = [&result, &staged]() {
        const auto cleanup = staged.cleanup();
        if (!cleanup.empty()) result.reason += "; " + cleanup;
        result.reason = bounded(std::move(result.reason));
        return result;
    };
    if (!write_staged(staged.file, bytes, result)) return abort_staging();
    if (!distinct_from_protected(root, protected_paths, error) ||
        !distinct_from_protected(destination, protected_paths, error) ||
        !distinct_from_protected(staged.directory, protected_paths, error) ||
        !distinct_from_protected(staged.file, protected_paths, error)) {
        result.status = LibrarySaveStatus::ProtectedPath;
        result.reason = std::move(error);
        return abort_staging();
    }
    const auto final_catalog = scan_registration_library(root);
    if (!admit_save(final_catalog, name, scope, true, result)) return abort_staging();
    LibraryEntry committed;
    committed.key = key;
    committed.name = name;
    committed.scope = scope;
    committed.status = LibraryEntryStatus::Valid;
    committed.controls = acknowledged;
    LibraryCommitAuthorization authorization;
    try {
        authorization = authorize_commit();
    } catch (const std::exception& exception) {
        result.status = LibrarySaveStatus::NotAuthorized;
        result.reason = bounded("Commit authorization failed: " + std::string(exception.what()));
        return abort_staging();
    } catch (...) {
        result.status = LibrarySaveStatus::NotAuthorized;
        result.reason = "Commit authorization failed";
        return abort_staging();
    }
    if (!authorization.permitted) {
        result.status = LibrarySaveStatus::NotAuthorized;
        result.reason = authorization.reason.empty() ? "Save authorization was cancelled" : bounded(std::move(authorization.reason));
        return abort_staging();
    }
    if (!publish_new(staged.file, destination, result)) return abort_staging();
    result.status = LibrarySaveStatus::Saved;
    result.committed_entry = std::move(committed);
    result.reason = "Saved";
    const auto cleanup = staged.cleanup();
    result.refreshed_catalog = scan_registration_library(root);
    const auto& refreshed = *result.refreshed_catalog;
    const auto found = std::find_if(refreshed.entries.begin(), refreshed.entries.end(),
        [&key](const LibraryEntry& entry) { return entry.key == key; });
    if (!cleanup.empty() || !refreshed.complete() || found == refreshed.entries.end() ||
        !found->valid() || *found->controls != acknowledged) {
        result.status = LibrarySaveStatus::SavedWithWarning;
        result.reason = "Saved; ";
        if (!cleanup.empty()) result.reason += cleanup;
        if (!refreshed.complete()) {
            if (!cleanup.empty()) result.reason += "; ";
            result.reason += "refresh failed: " + refreshed.reason;
        } else if (found == refreshed.entries.end() || !found->valid() || *found->controls != acknowledged) {
            if (!cleanup.empty()) result.reason += "; ";
            result.reason += "the committed entry changed or became unavailable during refresh";
        }
        result.reason = bounded(std::move(result.reason));
    }
    return result;
}

bool merge_registration_controls(RegistrationScope scope, const ControlSnapshot& entry,
    const ControlSnapshot& latest_desired, ControlSnapshot& destination) noexcept {
    if (!is_valid_registration_scope(scope) || !is_valid_control_snapshot(entry) ||
        !is_valid_control_snapshot(latest_desired)) return false;
    auto candidate = entry;
    if (scope == RegistrationScope::Registration) candidate.expression = latest_desired.expression;
    if (!is_valid_control_snapshot(candidate)) return false;
    destination = candidate;
    return true;
}

bool registration_controls_equal(RegistrationScope scope, const ControlSnapshot& a,
    const ControlSnapshot& b) noexcept {
    if (!is_valid_registration_scope(scope) || !is_valid_control_snapshot(a) ||
        !is_valid_control_snapshot(b)) return false;
    auto compared = a;
    if (scope == RegistrationScope::Registration) compared.expression = b.expression;
    return compared == b;
}

} // namespace hammond::standalone
