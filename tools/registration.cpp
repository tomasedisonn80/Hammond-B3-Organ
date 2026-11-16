#include "CliArguments.h"
#include "ControlFileInput.h"
#include "RegistrationLibrary.h"
#include "hammond/ControlStateIO.h"

#include <algorithm>
#include <array>
#include <charconv>
#include <csignal>
#include <cstdio>
#include <exception>
#include <filesystem>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>
#include <utility>
#include <vector>

#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif

namespace {
namespace fs = std::filesystem;
namespace library = hammond::standalone;
using hammond::tools::ControlFileInput;
using hammond::tools::ControlFileInputStatus;
using hammond::tools::read_control_file;
using library::LibraryCatalog;
using library::LibraryCatalogStatus;
using library::LibraryEntry;
using library::LibraryEntryStatus;
using library::LibrarySaveResult;
using library::LibrarySaveStatus;
using library::RegistrationScope;

constexpr std::size_t kMaximumReportBytes = 1024 * 1024;
constexpr std::size_t kMaximumTokenBytes = 4096;
constexpr std::size_t kMaximumArgumentBytes = 16384;
constexpr std::size_t kMaximumPathUnits = 8192;
constexpr int kMaximumArguments = 12;
constexpr std::array<std::string_view, 5> kUsage{
    "hammond_registration list --library DIR",
    "hammond_registration inspect --library DIR --key KEY",
    "hammond_registration import --input FILE --library DIR --name NAME --scope registration|performance",
    "hammond_registration materialize --library DIR --key KEY [--current FILE] --destination DIR --name NAME",
    "hammond_registration --help"};

// Returns one complete, strictly valid UTF-8 sequence, or zero. This same
// validator rejects argument substitutions and repairs only diagnostic text.
[[nodiscard]] std::size_t utf8_sequence(std::string_view value, std::size_t at) noexcept {
    const auto byte = [&value](std::size_t index) { return static_cast<unsigned char>(value[index]); };
    const auto first = byte(at);
    if (first < 0x80U) return 1;
    const std::size_t length = first >= 0xc2U && first <= 0xdfU ? 2 :
        first >= 0xe0U && first <= 0xefU ? 3 : first >= 0xf0U && first <= 0xf4U ? 4 : 0;
    if (length == 0 || length > value.size() - at) return 0;
    for (std::size_t index = 1; index < length; ++index) {
        if ((byte(at + index) & 0xc0U) != 0x80U) return 0;
    }
    const auto second = byte(at + 1);
    if ((first == 0xe0U && second < 0xa0U) || (first == 0xedU && second >= 0xa0U) ||
        (first == 0xf0U && second < 0x90U) || (first == 0xf4U && second >= 0x90U)) return 0;
    return length;
}

[[nodiscard]] bool valid_token(std::string_view value) noexcept {
    for (std::size_t at = 0; at < value.size();) {
        const auto c = static_cast<unsigned char>(value[at]);
        if (c < 0x20U || c == 0x7fU) return false;
        const auto length = utf8_sequence(value, at);
        if (length == 0) return false;
        at += length;
    }
    return true;
}

[[nodiscard]] std::string diagnostic(std::string_view value) {
    std::string result;
    result.reserve(library::kRegistrationLibraryMaxDiagnosticBytes);
    for (std::size_t at = 0; at < value.size();) {
        const auto length = utf8_sequence(value, at);
        const std::string_view piece = length == 0 ? std::string_view("\xef\xbf\xbd") : value.substr(at, length);
        if (piece.size() > library::kRegistrationLibraryMaxDiagnosticBytes - result.size()) break;
        result.append(piece);
        at += length == 0 ? 1 : length;
    }
    return result;
}

[[nodiscard]] std::string_view token(LibraryCatalogStatus status) {
    switch (status) {
    case LibraryCatalogStatus::Ready: return "Ready";
    case LibraryCatalogStatus::Empty: return "Empty";
    case LibraryCatalogStatus::MissingDirectory: return "MissingDirectory";
    case LibraryCatalogStatus::InvalidRoot: return "InvalidRoot";
    case LibraryCatalogStatus::CapacityExceeded: return "CapacityExceeded";
    case LibraryCatalogStatus::DirectoryUnavailable: return "DirectoryUnavailable";
    }
    throw std::logic_error("Unknown catalog status");
}

[[nodiscard]] std::string_view token(LibraryEntryStatus status) {
    switch (status) {
    case LibraryEntryStatus::Valid: return "Valid";
    case LibraryEntryStatus::InvalidKey: return "InvalidKey";
    case LibraryEntryStatus::Ambiguous: return "Ambiguous";
    case LibraryEntryStatus::InvalidPayload: return "InvalidPayload";
    case LibraryEntryStatus::TooLarge: return "TooLarge";
    case LibraryEntryStatus::NotRegularFile: return "NotRegularFile";
    case LibraryEntryStatus::Unavailable: return "Unavailable";
    }
    throw std::logic_error("Unknown entry status");
}

[[nodiscard]] std::string_view token(LibrarySaveStatus status) {
    switch (status) {
    case LibrarySaveStatus::Saved: return "Saved";
    case LibrarySaveStatus::SavedWithWarning: return "SavedWithWarning";
    case LibrarySaveStatus::InvalidName: return "InvalidName";
    case LibrarySaveStatus::InvalidScope: return "InvalidScope";
    case LibrarySaveStatus::InvalidControls: return "InvalidControls";
    case LibrarySaveStatus::NameExists: return "NameExists";
    case LibrarySaveStatus::CapacityExceeded: return "CapacityExceeded";
    case LibrarySaveStatus::InvalidRoot: return "InvalidRoot";
    case LibrarySaveStatus::DirectoryUnavailable: return "DirectoryUnavailable";
    case LibrarySaveStatus::ProtectedPath: return "ProtectedPath";
    case LibrarySaveStatus::StagingFailed: return "StagingFailed";
    case LibrarySaveStatus::WriteFailed: return "WriteFailed";
    case LibrarySaveStatus::FlushFailed: return "FlushFailed";
    case LibrarySaveStatus::CloseFailed: return "CloseFailed";
    case LibrarySaveStatus::NotAuthorized: return "NotAuthorized";
    case LibrarySaveStatus::CommitFailed: return "CommitFailed";
    }
    throw std::logic_error("Unknown save status");
}

[[nodiscard]] std::string_view scope_text(RegistrationScope scope) {
    switch (scope) {
    case RegistrationScope::Registration: return "registration";
    case RegistrationScope::Performance: return "performance";
    }
    throw std::logic_error("Unknown registration scope");
}

struct InputReport {
    std::optional<fs::path> path;
    std::optional<ControlFileInput> admitted;
};

struct Report {
    std::optional<std::string_view> command;
    std::string_view code{"InternalError"};
    std::string message;
    int exit_code{70};
    std::optional<bool> committed{false};
    std::optional<LibraryCatalog> catalog;
    std::optional<LibraryEntry> entry;
    std::optional<std::string> entry_controls;
    std::optional<InputReport> input;
    std::optional<LibrarySaveResult> save;
    std::optional<fs::path> save_path;
    std::optional<std::string> save_key;
    std::optional<RegistrationScope> save_scope;
};

void outcome(Report& report, int exit_code, std::string_view code, std::string_view message) {
    report.exit_code = exit_code;
    report.code = code;
    report.message = diagnostic(message);
}

[[nodiscard]] bool usage_error(Report& report, std::string_view message) {
    outcome(report, 2, "UsageError", message);
    return false;
}

class Json {
public:
    explicit Json(std::string& buffer) : buffer_(buffer) { buffer_.clear(); }
    void raw(std::string_view text) {
        if (text.size() > kMaximumReportBytes - buffer_.size()) throw std::length_error("Report exceeds 1 MiB");
        buffer_.append(text);
    }
    void string(std::string_view value) {
        constexpr char digits[] = "0123456789abcdef";
        raw("\"");
        for (const char character_value : value) {
            const auto c = static_cast<unsigned char>(character_value);
            if (c == '"') raw("\\\"");
            else if (c == '\\') raw("\\\\");
            else if (c < 0x20U) {
                const std::array<char, 6> escaped{'\\', 'u', '0', '0', digits[c >> 4], digits[c & 15U]};
                raw(std::string_view(escaped.data(), escaped.size()));
            } else {
                const char character = static_cast<char>(c);
                raw(std::string_view(&character, 1));
            }
        }
        raw("\"");
    }
    void reason(std::string_view value) { string(diagnostic(value)); }
    void boolean(bool value) { raw(value ? "true" : "false"); }
    void number(std::size_t value) {
        std::array<char, 32> digits{};
        const auto result = std::to_chars(digits.data(), digits.data() + digits.size(), value);
        if (result.ec != std::errc{}) throw std::logic_error("Cannot format report count");
        raw(std::string_view(digits.data(), static_cast<std::size_t>(result.ptr - digits.data())));
    }
    void path(const fs::path& path) {
#ifdef _WIN32
        raw("{\"encoding\":\"windows-utf16le-hex\",\"value\":\"");
#else
        raw("{\"encoding\":\"posix-bytes-hex\",\"value\":\"");
#endif
        static constexpr char digits[] = "0123456789abcdef";
        const auto byte = [this](unsigned value) {
            const std::array<char, 2> encoded{digits[(value >> 4) & 15U], digits[value & 15U]};
            raw(std::string_view(encoded.data(), encoded.size()));
        };
        for (const auto unit : path.native()) {
#ifdef _WIN32
            const auto value = static_cast<unsigned>(static_cast<unsigned short>(unit));
            byte(value & 255U);
            byte(value >> 8);
#else
            byte(static_cast<unsigned char>(unit));
#endif
        }
        raw("\"}");
    }

private:
    std::string& buffer_;
};

void entry_json(Json& json, const LibraryEntry& entry, const std::optional<std::string>* controls = nullptr) {
    json.raw("{\"key\":"); json.string(entry.key);
    json.raw(",\"name\":"); json.string(entry.name);
    json.raw(",\"scope\":"); json.string(scope_text(entry.scope));
    json.raw(",\"status\":"); json.string(token(entry.status));
    json.raw(",\"reason\":"); json.reason(entry.reason);
    if (controls != nullptr) {
        json.raw(",\"canonical_controls\":");
        if (controls->has_value()) json.string(**controls); else json.raw("null");
    }
    json.raw("}");
}

void catalog_json(Json& json, const LibraryCatalog& catalog) {
    json.raw("{\"status\":"); json.string(token(catalog.status));
    json.raw(",\"complete\":"); json.boolean(catalog.complete());
    json.raw(",\"reason\":"); json.reason(catalog.reason);
    json.raw(",\"directory_items\":"); json.number(catalog.directory_items);
    json.raw(",\"candidate_count\":"); json.number(catalog.candidate_count);
    json.raw(",\"invalid_name_count\":"); json.number(catalog.invalid_name_count);
    json.raw(",\"invalid_entry_count\":"); json.number(catalog.invalid_entry_count);
    json.raw(",\"ambiguous_entry_count\":"); json.number(catalog.ambiguous_entry_count);
    json.raw(",\"warning_count\":"); json.number(catalog.warning_count());
    json.raw(",\"entries\":[");
    bool first = true;
    for (const auto& entry : catalog.entries) {
        if (!first) json.raw(",");
        first = false;
        entry_json(json, entry);
    }
    json.raw("]}");
}

void encode_report(const Report& report, std::string& buffer) {
    Json json(buffer);
    json.raw("{\"schema\":\"hammond-registration-cli-v1\",\"command\":");
    if (report.command) json.string(*report.command); else json.raw("null");
    json.raw(",\"outcome\":");
    json.string(report.exit_code == 0 ? "ok" : report.exit_code == 1 ? "warning" : "error");
    json.raw(",\"code\":"); json.string(report.code);
    json.raw(",\"message\":"); json.reason(report.message);
    json.raw(",\"committed\":");
    if (report.committed) json.boolean(*report.committed); else json.raw("null");
    json.raw(",\"catalog\":");
    if (report.catalog) catalog_json(json, *report.catalog); else json.raw("null");
    json.raw(",\"entry\":");
    if (report.entry) entry_json(json, *report.entry, &report.entry_controls); else json.raw("null");
    json.raw(",\"input\":");
    if (report.input) {
        json.raw("{\"path\":");
        if (report.input->path) json.path(*report.input->path); else json.raw("null");
        json.raw(",\"source_version\":");
        if (report.input->admitted) json.number(report.input->admitted->source_version); else json.raw("null");
        json.raw(",\"source_bytes\":");
        if (report.input->admitted) json.number(report.input->admitted->source_bytes); else json.raw("null");
        json.raw(",\"canonical_controls\":");
        if (report.input->admitted) json.string(report.input->admitted->canonical_controls); else json.raw("null");
        json.raw("}");
    } else json.raw("null");
    json.raw(",\"save\":");
    if (report.save) {
        json.raw("{\"status\":"); json.string(token(report.save->status));
        json.raw(",\"reason\":"); json.reason(report.save->reason);
        json.raw(",\"key\":");
        if (report.save->committed_entry) json.string(report.save->committed_entry->key);
        else if (report.save_key) json.string(*report.save_key); else json.raw("null");
        json.raw(",\"scope\":");
        if (report.save->committed_entry) json.string(scope_text(report.save->committed_entry->scope));
        else if (report.save_scope) json.string(scope_text(*report.save_scope)); else json.raw("null");
        json.raw(",\"path\":");
        if (report.save_path) json.path(*report.save_path); else json.raw("null");
        json.raw(",\"refreshed_catalog\":");
        if (report.save->refreshed_catalog) catalog_json(json, *report.save->refreshed_catalog); else json.raw("null");
        json.raw("}");
    } else json.raw("null");
    json.raw(",\"usage\":");
    if (report.command == "help" && report.code == "Help") {
        json.raw("[");
        for (std::size_t index = 0; index < kUsage.size(); ++index) {
            if (index != 0) json.raw(",");
            json.string(kUsage[index]);
        }
        json.raw("]");
    } else json.raw("null");
    json.raw("}\n");
}

[[nodiscard]] int write_report(std::string_view bytes, int exit_code) noexcept {
#ifdef _WIN32
    const bool ready = _setmode(_fileno(stdout), _O_BINARY) != -1;
#else
    const bool ready = true;
#endif
    const bool written = ready && std::fwrite(bytes.data(), 1, bytes.size(), stdout) == bytes.size();
    const bool flushed = std::fflush(stdout) == 0;
    if (!written || !flushed || std::ferror(stdout) != 0) {
        constexpr std::string_view fallback =
            "hammond_registration: ReportFailed: could not write or flush JSON report; file publication may already have occurred.\n";
        (void)std::fwrite(fallback.data(), 1, fallback.size(), stderr);
        (void)std::fflush(stderr);
        return 5;
    }
    return exit_code;
}

[[nodiscard]] int emergency_report(std::optional<bool> committed) noexcept {
    constexpr std::string_view prefix = "{\"schema\":\"hammond-registration-cli-v1\",\"command\":null,"
        "\"outcome\":\"error\",\"code\":\"InternalError\",\"message\":\"Unexpected report preparation failure\",\"committed\":";
    constexpr std::string_view suffix = ",\"catalog\":null,\"entry\":null,\"input\":null,\"save\":null,\"usage\":null}\n";
    std::array<char, 512> storage{};
    const auto state = committed ? (*committed ? std::string_view("true") : std::string_view("false")) : std::string_view("null");
    auto cursor = std::copy(prefix.begin(), prefix.end(), storage.begin());
    cursor = std::copy(state.begin(), state.end(), cursor);
    cursor = std::copy(suffix.begin(), suffix.end(), cursor);
    return write_report(std::string_view(storage.data(), static_cast<std::size_t>(cursor - storage.begin())), 70);
}

[[nodiscard]] int finish_report(Report& report, std::string& buffer) noexcept {
    try {
        encode_report(report, buffer);
        return write_report(buffer, report.exit_code);
    } catch (...) {
        return emergency_report(report.committed);
    }
}

struct Options {
    std::optional<std::string_view> library, key, input, current, destination, name, scope;
};

[[nodiscard]] bool recognized_command(std::string_view value) noexcept {
    return value == "list" || value == "inspect" || value == "import" || value == "materialize";
}

[[nodiscard]] bool valid_key(std::string_view key) noexcept {
    for (const auto scope : {RegistrationScope::Registration, RegistrationScope::Performance}) {
        const auto suffix = library::registration_scope_suffix(scope);
        if (key.ends_with(suffix)) return library::is_valid_registration_name(key.substr(0, key.size() - suffix.size()));
    }
    return false;
}

[[nodiscard]] bool parse_arguments(int argc, char* argv[], Report& report, Options& options) {
    if (argc >= 2 && argv != nullptr && argv[1] != nullptr && recognized_command(argv[1])) report.command = argv[1];
    if (argc < 2 || argc > kMaximumArguments || argv == nullptr) return usage_error(report, "Expected one command; at most 12 arguments are permitted");
    std::size_t total = 0;
    for (int index = 1; index < argc; ++index) {
        if (argv[index] == nullptr) return usage_error(report, "Missing command-line token");
        const std::string_view value(argv[index]);
        if (value.size() > kMaximumTokenBytes || value.size() > kMaximumArgumentBytes - total) {
            return usage_error(report, "Command-line token or total byte limit exceeded");
        }
        total += value.size();
        if (!valid_token(value)) return usage_error(report, "Arguments must be valid UTF-8 without ASCII control bytes");
    }
    const std::string_view verb(argv[1]);
    if (verb == "--help" && argc == 2) {
        report.command = "help";
        outcome(report, 0, "Help", "Offline registration inspection and create-only preparation");
        return true;
    }
    if (!recognized_command(verb)) return usage_error(report, "Unknown command, or --help did not stand alone");
    if ((argc - 2) % 2 != 0) return usage_error(report, "Every option requires one value");
    for (int index = 2; index < argc; index += 2) {
        const std::string_view flag(argv[index]);
        const std::string_view value(argv[index + 1]);
        if (value.empty() || value.starts_with("--")) return usage_error(report, "Option values must be nonempty and must not begin with --");
        std::optional<std::string_view>* field = nullptr;
        if (flag == "--library") field = &options.library;
        else if (flag == "--key" && (verb == "inspect" || verb == "materialize")) field = &options.key;
        else if (flag == "--input" && verb == "import") field = &options.input;
        else if (flag == "--current" && verb == "materialize") field = &options.current;
        else if (flag == "--destination" && verb == "materialize") field = &options.destination;
        else if (flag == "--name" && (verb == "import" || verb == "materialize")) field = &options.name;
        else if (flag == "--scope" && verb == "import") field = &options.scope;
        if (field == nullptr) return usage_error(report, "Unknown option for this command");
        if (*field) return usage_error(report, "Each option may occur only once");
        *field = value;
    }
    if (!options.library || ((verb == "inspect" || verb == "materialize") && !options.key) ||
        (verb == "import" && (!options.input || !options.name || !options.scope)) ||
        (verb == "materialize" && (!options.destination || !options.name))) return usage_error(report, "Missing required option");
    if (options.key && !valid_key(*options.key)) return usage_error(report, "Key must be an exact portable name with a case-sensitive registration or performance suffix");
    if (options.name && !library::is_valid_registration_name(*options.name)) return usage_error(report, "Name must satisfy the portable 1-48 byte ASCII name grammar");
    if (options.scope && *options.scope != "registration" && *options.scope != "performance") return usage_error(report, "Scope must be registration or performance");
    return true;
}

struct Paths {
    fs::path invocation;
    fs::path resolved;
};

[[nodiscard]] bool path_bound(const fs::path& path, Report& report) {
    return path.native().size() <= kMaximumPathUnits || usage_error(report, "Resolved native path exceeds 8192 code units");
}

[[nodiscard]] bool invocation_path(std::string_view value, const fs::path& cwd, Paths& paths, Report& report) {
    const auto supplied = hammond::cli::argument_path(value);
    paths.invocation = supplied.is_absolute() ? supplied : cwd / supplied;
    return path_bound(paths.invocation, report);
}

[[nodiscard]] int catalog_exit(const LibraryCatalog& catalog) noexcept {
    if (catalog.complete()) return catalog.warning_count() == 0 ? 0 : 1;
    return catalog.status == LibraryCatalogStatus::DirectoryUnavailable ? 4 : 3;
}

void catalog_outcome(Report& report) {
    const auto& catalog = *report.catalog;
    outcome(report, catalog_exit(catalog), token(catalog.status), catalog.reason);
}

[[nodiscard]] bool source_root(std::string_view value, const fs::path& cwd, Paths& paths, Report& report) {
    if (!invocation_path(value, cwd, paths, report)) return false;
    std::string error;
    if (!library::resolve_registration_library_root(paths.invocation, paths.resolved, error)) {
        report.catalog = library::scan_registration_library(paths.invocation);
        if (report.catalog->complete()) {
            // A later successful diagnostic scan cannot complete the original
            // inspect/materialize operation whose path resolution failed.
            outcome(report, 4, "DirectoryUnavailable", error);
        } else catalog_outcome(report);
        return false;
    }
    return path_bound(paths.resolved, report);
}

[[nodiscard]] bool input_path(std::string_view value, const fs::path& cwd, Paths& paths, Report& report) {
    report.input.emplace();
    if (!invocation_path(value, cwd, paths, report)) return false;
    report.input->path = paths.invocation;
    // Admit the original leaf before resolving its parent. In particular this
    // lets the shared reader reject Windows device/pipe namespaces pre-open.
    ControlFileInput admitted;
    const auto read = read_control_file(paths.invocation, admitted);
    if (read.status != ControlFileInputStatus::Read) {
        switch (read.status) {
        case ControlFileInputStatus::Unavailable: outcome(report, 4, "InputUnavailable", read.reason); break;
        case ControlFileInputStatus::NotRegularFile: outcome(report, 3, "InputNotRegularFile", read.reason); break;
        case ControlFileInputStatus::TooLarge: outcome(report, 3, "InputTooLarge", read.reason); break;
        case ControlFileInputStatus::InvalidPayload: outcome(report, 3, "InvalidPayload", read.reason); break;
        case ControlFileInputStatus::Read: break;
        }
        return false;
    }
    std::error_code error;
    const auto parent = fs::weakly_canonical(paths.invocation.parent_path(), error);
    if (error) {
        outcome(report, 4, "InputUnavailable", "Could not resolve control input parent: " + error.message());
        return false;
    }
    paths.resolved = parent / paths.invocation.filename();
    if (!path_bound(paths.resolved, report)) return false;
    report.input->path = paths.resolved;
    report.input->admitted = std::move(admitted);
    return true;
}

[[nodiscard]] bool select_entry(const Paths& source, std::string_view key, Report& report) {
    if (!path_bound(source.resolved / key, report)) return false;
    report.catalog = library::scan_registration_library(source.resolved);
    if (!report.catalog->complete()) {
        catalog_outcome(report);
        return false;
    }
    const auto found = std::find_if(report.catalog->entries.begin(), report.catalog->entries.end(),
        [key](const LibraryEntry& entry) { return entry.key == key; });
    if (found == report.catalog->entries.end()) {
        outcome(report, 3, "NotFound", "No library entry has the exact requested key");
        return false;
    }
    report.entry = *found;
    if (!found->valid()) {
        outcome(report, found->status == LibraryEntryStatus::Unavailable ? 4 : 3, token(found->status), found->reason);
        return false;
    }
    std::string canonical;
    std::string error;
    if (!hammond::serialize_controls(*found->controls, canonical, error)) throw std::logic_error("Admitted controls did not serialize");
    report.entry_controls = std::move(canonical);
    const auto fresh = library::read_registration_entry(source.resolved, key);
    if (!fresh.valid()) {
        outcome(report, fresh.status == LibraryEntryStatus::Unavailable ? 4 : 3, token(fresh.status), fresh.reason);
        return false;
    }
    if (*fresh.controls != *found->controls) {
        outcome(report, 3, "SourceChanged", "Selected controls changed after catalog admission");
        return false;
    }
    return true;
}

[[nodiscard]] library::LibraryCommitAuthorization revalidate_input(const Paths& paths, const ControlFileInput& captured) {
    for (const auto* path : {&paths.invocation, &paths.resolved}) {
        ControlFileInput fresh;
        const auto read = read_control_file(*path, fresh);
        if (read.status != ControlFileInputStatus::Read) return {false, "Input revalidation failed: " + read.reason};
        if (fresh.controls != captured.controls) return {false, "Input controls changed before publication"};
    }
    return {true, {}};
}

[[nodiscard]] library::LibraryCommitAuthorization revalidate_source(const Paths& paths, const LibraryEntry& captured) {
    for (const auto* root : {&paths.invocation, &paths.resolved}) {
        const auto catalog = library::scan_registration_library(*root);
        if (!catalog.complete()) return {false, "Source catalog is no longer complete: " + catalog.reason};
        const auto found = std::find_if(catalog.entries.begin(), catalog.entries.end(),
            [&captured](const LibraryEntry& entry) { return entry.key == captured.key; });
        if (found == catalog.entries.end() || !found->valid() || *found->controls != *captured.controls) {
            return {false, "Selected source changed or is no longer unambiguous"};
        }
        const auto fresh = library::read_registration_entry(*root, captured.key);
        if (!fresh.valid() || *fresh.controls != *captured.controls) return {false, "Selected source changed before publication"};
    }
    return {true, {}};
}

void save_outcome(Report& report) {
    const auto& saved = *report.save;
    int exit_code;
    switch (saved.status) {
    case LibrarySaveStatus::Saved:
    case LibrarySaveStatus::SavedWithWarning:
        exit_code = saved.status == LibrarySaveStatus::SavedWithWarning ||
            (report.catalog && report.catalog->warning_count() != 0) ||
            (saved.refreshed_catalog && saved.refreshed_catalog->warning_count() != 0) ? 1 : 0;
        break;
    case LibrarySaveStatus::InvalidName:
    case LibrarySaveStatus::InvalidScope: exit_code = 2; break;
    case LibrarySaveStatus::InvalidControls:
    case LibrarySaveStatus::NameExists:
    case LibrarySaveStatus::CapacityExceeded:
    case LibrarySaveStatus::InvalidRoot:
    case LibrarySaveStatus::ProtectedPath:
    case LibrarySaveStatus::NotAuthorized: exit_code = 3; break;
    case LibrarySaveStatus::DirectoryUnavailable:
    case LibrarySaveStatus::StagingFailed:
    case LibrarySaveStatus::WriteFailed:
    case LibrarySaveStatus::FlushFailed:
    case LibrarySaveStatus::CloseFailed:
    case LibrarySaveStatus::CommitFailed: exit_code = 4; break;
    default: throw std::logic_error("Unknown save outcome");
    }
    outcome(report, exit_code, token(saved.status), saved.reason);
}

[[nodiscard]] bool destination_root(std::string_view value, const fs::path& cwd,
                                    RegistrationScope scope, std::string_view name,
                                    Paths& paths, Report& report) {
    if (!invocation_path(value, cwd, paths, report)) return false;
    report.save_key = std::string(name) + std::string(library::registration_scope_suffix(scope));
    report.save_scope = scope;
    std::string error;
    if (!library::resolve_registration_library_root(paths.invocation, paths.resolved, error)) {
        const auto catalog = library::scan_registration_library(paths.invocation);
        LibrarySaveResult result;
        result.status = catalog.status == LibraryCatalogStatus::InvalidRoot ? LibrarySaveStatus::InvalidRoot : LibrarySaveStatus::DirectoryUnavailable;
        result.reason = std::move(error);
        report.save = std::move(result);
        save_outcome(report);
        return false;
    }
    if (!path_bound(paths.resolved, report) || !path_bound(paths.resolved / *report.save_key, report)) return false;
    report.save_path = paths.resolved / *report.save_key;
    return true;
}

void execute(int argc, char* argv[], Report& report) {
    Options options;
    if (!parse_arguments(argc, argv, report, options) || report.command == "help") return;
    std::error_code cwd_error;
    const auto cwd = fs::current_path(cwd_error);
    if (cwd_error) {
        outcome(report, 4, "DirectoryUnavailable", "Could not resolve invocation directory: " + cwd_error.message());
        return;
    }
    Paths source;
    if (report.command != "import") {
        if (!source_root(*options.library, cwd, source, report)) return;
        if (report.command == "list") {
            report.catalog = library::scan_registration_library(source.resolved);
            catalog_outcome(report);
            return;
        }
        if (!select_entry(source, *options.key, report)) return;
        if (report.command == "inspect") {
            outcome(report, report.catalog->warning_count() == 0 ? 0 : 1, "Valid", "Selected entry was validated and serialized");
            return;
        }
        if ((report.entry->scope == RegistrationScope::Registration) != options.current.has_value()) {
            (void)usage_error(report, "Registration materialization requires --current; Performance forbids --current");
            return;
        }
    }
    Paths input;
    if (options.input || options.current) {
        if (!input_path(options.input ? *options.input : *options.current, cwd, input, report)) return;
    }
    const auto scope = report.command == "import" && *options.scope == "registration" ?
        RegistrationScope::Registration : RegistrationScope::Performance;
    Paths destination;
    if (!destination_root(options.destination ? *options.destination : *options.library,
            cwd, scope, *options.name, destination, report)) return;
    hammond::ControlSnapshot controls;
    if (report.command == "import") {
        controls = report.input->admitted->controls;
    } else {
        const auto& current = report.input ? report.input->admitted->controls : *report.entry->controls;
        if (!library::merge_registration_controls(report.entry->scope, *report.entry->controls, current, controls)) {
            throw std::logic_error("Validated controls did not merge");
        }
    }
    std::vector<fs::path> protected_paths;
    protected_paths.reserve(4);
    if (report.input) {
        protected_paths.push_back(input.invocation);
        protected_paths.push_back(input.resolved);
    }
    if (report.entry) {
        protected_paths.push_back(source.invocation / report.entry->key);
        protected_paths.push_back(source.resolved / report.entry->key);
    }
    const library::LibraryAuthorizeCommit authorize = [&report, &input, &source]() -> library::LibraryCommitAuthorization {
        if (report.input) {
            const auto checked = revalidate_input(input, *report.input->admitted);
            if (!checked.permitted) return checked;
        }
        if (report.entry) return revalidate_source(source, *report.entry);
        return {true, {}};
    };
    // If the writer throws, it may have published before a refresh allocation
    // failed. No rollback, retry or guess about publication is authorized.
    report.committed.reset();
    auto saved = library::save_registration_entry_new(destination.resolved, *options.name,
        scope, controls, protected_paths, authorize);
    report.committed = saved.committed();
    report.save = std::move(saved);
    save_outcome(report);
}

[[nodiscard]] int registration_main(int argc, char* argv[]) noexcept {
#ifndef _WIN32
    (void)std::signal(SIGPIPE, SIG_IGN);
#endif
    Report report;
    std::string buffer;
    try {
        // Reserve the complete bounded transport buffer before any save can run.
        buffer.reserve(kMaximumReportBytes);
        execute(argc, argv, report);
    } catch (const std::exception& error) {
        try { outcome(report, 70, "InternalError", error.what()); }
        catch (...) { return emergency_report(report.committed); }
    } catch (...) {
        try { outcome(report, 70, "InternalError", "Unexpected offline registration failure"); }
        catch (...) { return emergency_report(report.committed); }
    }
    return finish_report(report, buffer);
}

#ifdef _WIN32
[[nodiscard]] int windows_failure(std::optional<std::string_view> command,
                                   int exit_code, std::string_view message) noexcept {
    Report report;
    try {
        report.command = command;
        outcome(report, exit_code, exit_code == 2 ? "UsageError" : "InternalError", message);
        std::string buffer;
        buffer.reserve(kMaximumReportBytes);
        return finish_report(report, buffer);
    } catch (...) {
        return emergency_report(false);
    }
}
#endif

} // namespace

#ifdef _WIN32
int wmain(int argc, wchar_t* argv[]) {
    std::optional<std::string_view> command;
    try {
        if (argc >= 2 && argv != nullptr && argv[1] != nullptr) {
            const std::wstring_view verb(argv[1]);
            if (verb == L"list") command = "list";
            else if (verb == L"inspect") command = "inspect";
            else if (verb == L"import") command = "import";
            else if (verb == L"materialize") command = "materialize";
            else if (verb == L"--help" && argc == 2) command = "help";
        }
        if (argc < 1 || argc > kMaximumArguments || argv == nullptr) {
            return windows_failure(command, 2, "At most 12 arguments are permitted");
        }
        std::vector<std::string> arguments;
        arguments.reserve(static_cast<std::size_t>(argc));
        arguments.emplace_back("hammond_registration");
        std::size_t total = 0;
        for (int index = 1; index < argc; ++index) {
            if (argv[index] == nullptr) return windows_failure(command, 2, "Missing command-line token");
            const std::wstring_view wide(argv[index]);
            if (wide.size() > kMaximumTokenBytes) return windows_failure(command, 2, "Command-line token byte limit exceeded");
            const int bytes = wide.empty() ? 0 : WideCharToMultiByte(CP_UTF8, WC_ERR_INVALID_CHARS,
                wide.data(), static_cast<int>(wide.size()), nullptr, 0, nullptr, nullptr);
            if ((!wide.empty() && bytes <= 0) || bytes > static_cast<int>(kMaximumTokenBytes) ||
                static_cast<std::size_t>(bytes) > kMaximumArgumentBytes - total) {
                return windows_failure(command, 2, "Command-line argument is invalid Unicode or exceeds byte limits");
            }
            std::string value(static_cast<std::size_t>(bytes), '\0');
            if (bytes > 0 && WideCharToMultiByte(CP_UTF8, WC_ERR_INVALID_CHARS, wide.data(),
                    static_cast<int>(wide.size()), value.data(), bytes, nullptr, nullptr) != bytes) {
                return windows_failure(command, 2, "Cannot strictly convert command-line argument to UTF-8");
            }
            total += value.size();
            arguments.push_back(std::move(value));
        }
        std::vector<char*> pointers;
        pointers.reserve(arguments.size() + 1);
        for (auto& value : arguments) pointers.push_back(value.data());
        pointers.push_back(nullptr);
        return registration_main(argc, pointers.data());
    } catch (...) {
        return windows_failure(command, 70, "Unexpected Windows argument adapter failure");
    }
}
#else
int main(int argc, char* argv[]) {
    return registration_main(argc, argv);
}
#endif
