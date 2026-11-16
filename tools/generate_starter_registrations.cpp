#include "CliArguments.h"
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

#ifndef HAMMOND_STARTER_SOURCE_DIR
#error "The developer generator requires HAMMOND_STARTER_SOURCE_DIR for source protection"
#endif

namespace {
namespace fs = std::filesystem;
namespace library = hammond::standalone;
using Bank = hammond::DrawbarBank;
using Fixed = hammond::FixedRegistration;
using Harmonic = hammond::PercussionHarmonic;
using Volume = hammond::PercussionVolume;
using Decay = hammond::PercussionDecay;
using Scope = library::RegistrationScope;
using SaveStatus = library::LibrarySaveStatus;

constexpr std::size_t kRecipeCount = 12;
constexpr std::size_t kFileCount = 2 * kRecipeCount;
constexpr std::size_t kMaximumArgumentBytes = 4096;
constexpr std::size_t kMaximumPathUnits = 8192;
constexpr std::string_view kSchema = "hammond-starter-generator-v1";

[[nodiscard]] consteval hammond::DrawbarPositions positions(std::string_view text) {
    if (text.size() != hammond::kDrawbarCount) throw "A recipe needs nine drawbar positions";
    hammond::DrawbarPositions result{};
    for (std::size_t index = 0; index < result.size(); ++index) {
        if (text[index] < '0' || text[index] > '8') throw "Invalid recipe drawbar position";
        result[index] = static_cast<std::uint8_t>(text[index] - '0');
    }
    return result;
}

[[nodiscard]] consteval hammond::AllDrawbarBanks banks(std::string_view ua,
    std::string_view ub, std::string_view la, std::string_view lb) {
    return {hammond::ManualDrawbarBanks{positions(ua), positions(ub)},
            hammond::ManualDrawbarBanks{positions(la), positions(lb)}};
}

struct Recipe {
    std::string_view name;
    hammond::ControlSnapshot controls;
};

// Independent literal transcription of STARTER_REGISTRATION_PACK_CONTRACT.md.
// Every ControlSnapshot field is explicit. No manifest, default recipe,
// inheritance, state-file grammar or runtime authoring input supplies values.
constexpr std::array<Recipe, kRecipeCount> kRecipes{{
    {"01 Quiet Foundation", {
        .drawbars = banks("008000000", "008400000", "008000000", "004000000"),
        .selected_banks = {Bank::B, Bank::B}, .route_enabled = {true, true},
        .expression = 0.5, .percussion = {false, Harmonic::Second, Volume::Normal, Decay::Slow},
        .pedal_drawbars = {2, 0}, .fixed_registrations = {Fixed::None, Fixed::None}}},
    {"02 Warm Comp", {
        .drawbars = banks("808000000", "808400000", "008400000", "008300000"),
        .selected_banks = {Bank::B, Bank::B}, .route_enabled = {true, true},
        .expression = 0.625, .percussion = {false, Harmonic::Second, Volume::Normal, Decay::Slow},
        .pedal_drawbars = {3, 0}, .fixed_registrations = {Fixed::None, Fixed::None}}},
    {"03 Clear Lead", {
        .drawbars = banks("008400000", "808600000", "006000000", "006400000"),
        .selected_banks = {Bank::B, Bank::B}, .route_enabled = {true, true},
        .expression = 0.625, .percussion = {false, Harmonic::Second, Volume::Normal, Decay::Slow},
        .pedal_drawbars = {2, 0}, .fixed_registrations = {Fixed::None, Fixed::None}}},
    {"04 Reed Edge", {
        .drawbars = banks("008620400", "008640400", "008200000", "008300000"),
        .selected_banks = {Bank::B, Bank::B}, .route_enabled = {true, true},
        .expression = 0.5, .percussion = {false, Harmonic::Second, Volume::Normal, Decay::Slow},
        .pedal_drawbars = {2, 0}, .fixed_registrations = {Fixed::None, Fixed::None}}},
    {"05 Bright Ensemble", {
        .drawbars = banks("808600004", "808600008", "008400000", "008440000"),
        .selected_banks = {Bank::B, Bank::B}, .route_enabled = {true, true},
        .expression = 0.5, .percussion = {false, Harmonic::Second, Volume::Normal, Decay::Slow},
        .pedal_drawbars = {4, 0}, .fixed_registrations = {Fixed::None, Fixed::None}}},
    {"06 High Shimmer", {
        .drawbars = banks("008000248", "008000468", "008000000", "008200000"),
        .selected_banks = {Bank::B, Bank::B}, .route_enabled = {true, true},
        .expression = 0.5, .percussion = {false, Harmonic::Second, Volume::Normal, Decay::Slow},
        .pedal_drawbars = {1, 0}, .fixed_registrations = {Fixed::None, Fixed::None}}},
    {"07 Percussive Pair", {
        .drawbars = banks("888000000", "888000000", "008400000", "008400000"),
        .selected_banks = {Bank::B, Bank::B}, .route_enabled = {true, true},
        .expression = 0.5, .percussion = {true, Harmonic::Third, Volume::Normal, Decay::Fast},
        .pedal_drawbars = {4, 0}, .fixed_registrations = {Fixed::None, Fixed::None}}},
    {"08 Slow Accent", {
        .drawbars = banks("808000000", "808000000", "008000000", "008200000"),
        .selected_banks = {Bank::B, Bank::B}, .route_enabled = {true, true},
        .expression = 0.625, .percussion = {true, Harmonic::Second, Volume::Soft, Decay::Slow},
        .pedal_drawbars = {3, 0}, .fixed_registrations = {Fixed::None, Fixed::None}}},
    {"09 Split Dialogue", {
        .drawbars = banks("008400000", "008600004", "808000000", "808400000"),
        .selected_banks = {Bank::A, Bank::B}, .route_enabled = {true, true},
        .expression = 0.5, .percussion = {false, Harmonic::Second, Volume::Normal, Decay::Slow},
        .pedal_drawbars = {4, 0}, .fixed_registrations = {Fixed::None, Fixed::None}}},
    {"10 Pedal Study", {
        .drawbars = banks("008000000", "008400000", "008000000", "008200000"),
        .selected_banks = {Bank::A, Bank::B}, .route_enabled = {false, false},
        .expression = 0.5, .percussion = {false, Harmonic::Second, Volume::Normal, Decay::Slow},
        .pedal_drawbars = {6, 2}, .fixed_registrations = {Fixed::None, Fixed::None}}},
    {"11 Fixed Contrast", {
        .drawbars = banks("008000000", "808400000", "008400000", "008440000"),
        .selected_banks = {Bank::B, Bank::A}, .route_enabled = {true, true},
        .expression = 0.5, .percussion = {false, Harmonic::Second, Volume::Normal, Decay::Slow},
        .pedal_drawbars = {3, 0}, .fixed_registrations = {Fixed::DSharp, Fixed::F}}},
    {"12 Manual Return", {
        .drawbars = banks("808000000", "808600000", "008400000", "008440000"),
        .selected_banks = {Bank::A, Bank::B}, .route_enabled = {false, true},
        .expression = 0.5, .percussion = {true, Harmonic::Third, Volume::Soft, Decay::Fast},
        .pedal_drawbars = {4, 0}, .fixed_registrations = {Fixed::GSharp, Fixed::None}}},
}};

struct Failure : std::runtime_error {
    Failure(int exit_value, const char* category, std::string message)
        : std::runtime_error(std::move(message)), exit_code(exit_value), status(category) {}
    int exit_code;
    const char* status;
};

struct Output {
    std::string_view name;
    std::string key;
    Scope scope{};
    hammond::ControlSnapshot controls;
};

struct BatchIntent {
    fs::path invocation;
    fs::path root;
    fs::path pack_source;
    std::array<Output, kFileCount> files;
    std::vector<fs::path> protected_paths;
};

struct Progress {
    std::size_t committed{};
    std::size_t attempted{};
    std::array<char, 128> filename{};
    std::size_t filename_size{};
    std::optional<bool> current_committed{false};
    bool current_reported{};

    void begin(std::string_view key) {
        if (key.size() > filename.size()) throw std::logic_error("Unexpected filename bound");
        std::copy(key.begin(), key.end(), filename.begin());
        filename_size = key.size();
        ++attempted;
        current_committed.reset();
        current_reported = false;
    }
    [[nodiscard]] std::string_view key() const noexcept { return {filename.data(), filename_size}; }
};

// Fixed report storage is prepared on the stack even after an allocating save
// throws. System diagnostic bytes are JSON-escaped independently of locale.
class JsonLine {
public:
    void raw(std::string_view text) {
        if (text.size() > storage_.size() - used_) throw std::length_error("Report bound exceeded");
        std::copy(text.begin(), text.end(), storage_.begin() + static_cast<std::ptrdiff_t>(used_));
        used_ += text.size();
    }
    void string(std::string_view text) {
        constexpr char hex[] = "0123456789abcdef";
        raw("\"");
        for (const char byte : text) {
            const auto value = static_cast<unsigned char>(byte);
            if (value == '"') raw("\\\"");
            else if (value == '\\') raw("\\\\");
            else if (value < 0x20U || value >= 0x7fU) {
                const std::array<char, 6> escaped{'\\', 'u', '0', '0', hex[value >> 4], hex[value & 15U]};
                raw({escaped.data(), escaped.size()});
            } else {
                raw({&byte, 1});
            }
        }
        raw("\"");
    }
    void number(std::size_t value) {
        std::array<char, 32> text{};
        const auto result = std::to_chars(text.data(), text.data() + text.size(), value);
        if (result.ec != std::errc{}) throw std::logic_error("Unexpected report number bound");
        raw({text.data(), static_cast<std::size_t>(result.ptr - text.data())});
    }
    [[nodiscard]] bool write() const noexcept {
        const bool written = std::fwrite(storage_.data(), 1, used_, stdout) == used_;
        const bool flushed = std::fflush(stdout) == 0;
        return written && flushed && std::ferror(stdout) == 0;
    }

private:
    std::array<char, 4096> storage_{};
    std::size_t used_{};
};

void report_header(JsonLine& json, std::string_view event) {
    json.raw("{\"schema\":"); json.string(kSchema);
    json.raw(",\"event\":"); json.string(event);
}

[[nodiscard]] bool file_report(const Progress& progress, std::string_view status,
                                std::string_view message) {
    JsonLine json;
    report_header(json, "file");
    json.raw(",\"file\":"); json.string(progress.key());
    json.raw(",\"status\":"); json.string(status);
    json.raw(",\"committed\":");
    json.raw(progress.current_committed ? (*progress.current_committed ? "true" : "false") : "null");
    json.raw(",\"message\":"); json.string(message.substr(0, library::kRegistrationLibraryMaxDiagnosticBytes));
    json.raw("}\n");
    return json.write();
}

[[nodiscard]] int report_failed(const Progress& progress) noexcept {
    (void)std::fprintf(stderr,
        "hammond_generate_starter_registrations: ReportFailed; committed_count=%zu; "
        "attempted_count=%zu; current_file=%.*s; current_publication=%s. "
        "No retry or rollback was attempted.\n",
        progress.committed, progress.attempted,
        static_cast<int>(progress.filename_size), progress.filename.data(),
        progress.current_committed ? (*progress.current_committed ? "committed" : "not_committed") : "unknown");
    (void)std::fflush(stderr);
    return 5;
}

[[nodiscard]] int summary(const Progress& progress, std::string_view status,
                           std::string_view message, int exit_code) {
    JsonLine json;
    report_header(json, "summary");
    json.raw(",\"status\":"); json.string(status);
    json.raw(",\"committed_count\":"); json.number(progress.committed);
    json.raw(",\"attempted_count\":"); json.number(progress.attempted);
    json.raw(",\"unattempted_count\":"); json.number(kFileCount - progress.attempted);
    json.raw(",\"uncertain_file\":");
    if (!progress.current_committed) json.string(progress.key()); else json.raw("null");
    json.raw(",\"message\":"); json.string(message.substr(0, library::kRegistrationLibraryMaxDiagnosticBytes));
    json.raw("}\n");
    return json.write() ? exit_code : report_failed(progress);
}

[[nodiscard]] std::string_view save_status(SaveStatus status) {
    switch (status) {
    case SaveStatus::Saved: return "Saved";
    case SaveStatus::SavedWithWarning: return "SavedWithWarning";
    case SaveStatus::InvalidName: return "InvalidName";
    case SaveStatus::InvalidScope: return "InvalidScope";
    case SaveStatus::InvalidControls: return "InvalidControls";
    case SaveStatus::NameExists: return "NameExists";
    case SaveStatus::CapacityExceeded: return "CapacityExceeded";
    case SaveStatus::InvalidRoot: return "InvalidRoot";
    case SaveStatus::DirectoryUnavailable: return "DirectoryUnavailable";
    case SaveStatus::ProtectedPath: return "ProtectedPath";
    case SaveStatus::StagingFailed: return "StagingFailed";
    case SaveStatus::WriteFailed: return "WriteFailed";
    case SaveStatus::FlushFailed: return "FlushFailed";
    case SaveStatus::CloseFailed: return "CloseFailed";
    case SaveStatus::NotAuthorized: return "NotAuthorized";
    case SaveStatus::CommitFailed: return "CommitFailed";
    }
    throw std::logic_error("Unknown storage result");
}

[[nodiscard]] bool same_name(std::string_view a, std::string_view b) noexcept {
    const auto fold = [](char value) {
        return value >= 'A' && value <= 'Z' ? static_cast<char>(value + ('a' - 'A')) : value;
    };
    return a.size() == b.size() && std::equal(a.begin(), a.end(), b.begin(),
        [&fold](char x, char y) { return fold(x) == fold(y); });
}

void validate_path_bound(const fs::path& path) {
    if (path.native().size() > kMaximumPathUnits) {
        throw Failure(2, "UsageError", "Resolved output path exceeds 8192 native code units");
    }
}

// Protect the whole authored pack, including not-yet-created entries. Neither
// this check nor the storage protected-path list reads the independent oracle.
[[nodiscard]] bool inside_pack(const fs::path& output, const fs::path& source_pack) {
    std::error_code code;
    const auto pack = fs::weakly_canonical(source_pack, code);
    if (code) throw Failure(4, "DirectoryUnavailable", "Could not resolve protected source pack");
    for (auto path = output; !path.empty();) {
        if (path == pack) return true;
        code.clear();
        if (fs::equivalent(path, pack, code) && !code) return true;
        const auto parent = path.parent_path();
        if (parent == path) break;
        path = parent;
    }
    return false;
}

[[nodiscard]] BatchIntent prepare(std::string_view output) {
    BatchIntent intent;
    // Validate all twelve literal snapshots and both names before any write.
    for (std::size_t index = 0; index < kRecipes.size(); ++index) {
        const auto& recipe = kRecipes[index];
        if (!library::is_valid_registration_name(recipe.name) ||
            !hammond::is_valid_control_snapshot(recipe.controls)) {
            throw std::logic_error("Invalid compiled starter recipe");
        }
        for (std::size_t prior = 0; prior < index; ++prior) {
            if (same_name(recipe.name, kRecipes[prior].name)) throw std::logic_error("Duplicate compiled recipe name");
        }
        std::string canonical;
        std::string error;
        if (!hammond::serialize_controls(recipe.controls, canonical, error) ||
            canonical.empty() || canonical.size() > hammond::kMaxControlStateBytes || canonical.back() != '\n') {
            throw std::logic_error("Compiled recipe did not serialize canonically: " + error);
        }
        for (std::size_t scope_index = 0; scope_index < 2; ++scope_index) {
            const auto scope = scope_index == 0 ? Scope::Registration : Scope::Performance;
            intent.files[2 * index + scope_index] = {recipe.name,
                std::string(recipe.name) + std::string(library::registration_scope_suffix(scope)),
                scope, recipe.controls};
        }
    }
    std::error_code code;
    intent.invocation = fs::absolute(hammond::cli::argument_path(output), code);
    if (code) throw Failure(4, "DirectoryUnavailable", "Could not resolve invocation directory");
    std::string error;
    if (!library::resolve_registration_library_root(intent.invocation, intent.root, error)) {
        throw Failure(3, "InvalidOutput", std::move(error));
    }
    validate_path_bound(intent.invocation);
    validate_path_bound(intent.root);
    for (const auto& file : intent.files) validate_path_bound(intent.root / file.key);
    const auto source = hammond::cli::argument_path(HAMMOND_STARTER_SOURCE_DIR);
    if (!source.is_absolute()) throw std::logic_error("Compiled source protection root must be absolute");
    intent.pack_source = source / "data/registrations/starter-v1";
    intent.protected_paths = {
        source / "tools/generate_starter_registrations.cpp",
        source / "docs/STARTER_REGISTRATION_PACK_CONTRACT.md",
        source / "data/registrations/atlas-chapel-nominal-v1.json",
        intent.pack_source, intent.pack_source / "entries",
        intent.pack_source / "README.md", intent.pack_source / "recipes.json"};
    if (inside_pack(intent.root, intent.pack_source)) {
        throw Failure(3, "ProtectedPath", "Generate into a separate staging directory; authored pack paths are protected");
    }
    code.clear();
    const auto status = fs::status(intent.root, code);
    if (code && code != std::errc::no_such_file_or_directory) {
        throw Failure(4, "DirectoryUnavailable", "Could not inspect output directory");
    }
    if (fs::exists(status)) {
        code.clear();
        const fs::directory_iterator first(intent.root, code);
        if (code) throw Failure(4, "DirectoryUnavailable", "Could not inspect output directory contents");
        if (first != fs::directory_iterator{}) {
            throw Failure(3, "OutputNotEmpty", "Output directory must be empty; no existing files were changed");
        }
    } else {
        code.clear();
        if (!fs::is_directory(intent.root.parent_path(), code) || code) {
            throw Failure(3, "MissingParent", "A missing output directory requires an existing parent directory");
        }
    }
    return intent;
}

[[nodiscard]] library::LibraryCommitAuthorization authorize(const BatchIntent& intent,
                                                             std::size_t committed) {
    fs::path fresh;
    std::string error;
    if (!library::resolve_registration_library_root(intent.invocation, fresh, error) || fresh != intent.root) {
        return {false, "Output directory no longer resolves to the immutable batch destination"};
    }
    if (inside_pack(fresh, intent.pack_source)) return {false, "Output now aliases a protected source pack"};
    std::error_code code;
    fs::directory_iterator cursor(intent.root, code);
    if (code) return {false, "Could not revalidate batch directory"};
    std::array<bool, kFileCount> seen{};
    std::size_t count = 0;
    std::size_t staging_count = 0;
    const auto staging_prefix = fs::path(".b3-library-save-").native();
    for (; cursor != fs::directory_iterator{}; cursor.increment(code)) {
        if (code) return {false, "Could not finish batch directory revalidation"};
        if (++count > committed + 1) return {false, "Output acquired an unexpected directory item"};
        const auto filename = cursor->path().filename();
        if (filename.native().starts_with(staging_prefix)) {
            const auto status = cursor->symlink_status(code);
            if (code || !fs::is_directory(status) || ++staging_count != 1) {
                return {false, "Output has an unexpected staging object"};
            }
            continue;
        }
        bool expected = false;
        for (std::size_t index = 0; index < committed; ++index) {
            if (filename == fs::path(intent.files[index].key) && !seen[index]) {
                seen[index] = true;
                expected = true;
                break;
            }
        }
        if (!expected) return {false, "Output contains an item outside the immutable batch intent"};
    }
    if (code || count != committed + 1 || staging_count != 1) {
        return {false, "Output directory changed before publication"};
    }
    for (std::size_t index = 0; index < committed; ++index) {
        if (!seen[index]) return {false, "A previously committed entry is missing"};
        const auto entry = library::read_registration_entry(intent.root, intent.files[index].key);
        if (!entry.valid() || *entry.controls != intent.files[index].controls) {
            return {false, "A previously committed entry changed before publication"};
        }
    }
    return {true, {}};
}

[[nodiscard]] int execute(int argc, char* argv[], Progress& progress) {
    if (argc < 1 || argc > 3) throw Failure(2, "UsageError", "Use --output DIR or --help");
    for (int index = 1; index < argc; ++index) {
        const std::string_view argument(argv[index]);
        if (argument.empty() || argument.size() > kMaximumArgumentBytes ||
            std::any_of(argument.begin(), argument.end(), [](unsigned char byte) { return byte < 0x20U || byte == 0x7fU; })) {
            throw Failure(2, "UsageError", "Arguments must be nonempty, at most 4096 bytes, and contain no control bytes");
        }
    }
    if (argc == 2 && std::string_view(argv[1]) == "--help") {
        constexpr std::string_view usage =
            "Usage: hammond_generate_starter_registrations --output DIR\n"
            "       hammond_generate_starter_registrations --help\n"
            "Generate 12 proposed nominal dry-Engine recipes as 24 canonical paired files.\n"
            "DIR must be empty, or a missing child of an existing parent, outside the authored pack.\n"
            "Files are create-only. Each save is reported as JSONL; the batch is not atomic.\n"
            "Stop on a failure or saved warning, retain committed files, and never retry or overwrite.\n";
        const bool written = std::fwrite(usage.data(), 1, usage.size(), stdout) == usage.size();
        const bool flushed = std::fflush(stdout) == 0;
        return written && flushed && std::ferror(stdout) == 0 ? 0 : report_failed(progress);
    }
    if (argc != 3 || std::string_view(argv[1]) != "--output" || std::string_view(argv[2]).starts_with("--")) {
        throw Failure(2, "UsageError", "Use --output DIR or --help");
    }
    const BatchIntent intent = prepare(argv[2]);
    for (std::size_t index = 0; index < intent.files.size(); ++index) {
        const auto& file = intent.files[index];
        // This synchronous callback compares the observed directory and prior
        // snapshots against this const offline intent; it never pumps events.
        const auto permit = [&intent, index]() { return authorize(intent, index); };
        progress.begin(file.key);
        const auto saved = library::save_registration_entry_new(intent.root, file.name,
            file.scope, file.controls, intent.protected_paths, permit);
        progress.current_committed = saved.committed();
        if (saved.committed()) ++progress.committed;
        if (!file_report(progress, save_status(saved.status), saved.reason)) return report_failed(progress);
        progress.current_reported = true;
        if (saved.status != SaveStatus::Saved) {
            return summary(progress, "Stopped", saved.committed() ?
                "Stopped after a committed warning; committed files are retained" :
                "Stopped after a failed save; committed files are retained", saved.committed() ? 1 : 4);
        }
    }
    return summary(progress, "Complete", "All 24 files committed; no existing files were replaced", 0);
}

[[nodiscard]] int generator_main(int argc, char* argv[]) noexcept {
    Progress progress;
#ifdef _WIN32
    if (_setmode(_fileno(stdout), _O_BINARY) == -1) return report_failed(progress);
#else
    (void)std::signal(SIGPIPE, SIG_IGN);
#endif
    try {
        return execute(argc, argv, progress);
    } catch (const Failure& error) {
        try { return summary(progress, error.status, error.what(), error.exit_code); }
        catch (...) { return report_failed(progress); }
    } catch (const std::exception& error) {
        try {
            if (progress.attempted != 0 && !progress.current_reported &&
                !file_report(progress, "InternalError", error.what())) return report_failed(progress);
            return summary(progress, "InternalError", error.what(), 70);
        } catch (...) { return report_failed(progress); }
    } catch (...) {
        try {
            if (progress.attempted != 0 && !progress.current_reported &&
                !file_report(progress, "InternalError", "Unexpected save failure")) return report_failed(progress);
            return summary(progress, "InternalError", "Unexpected generator failure", 70);
        } catch (...) { return report_failed(progress); }
    }
}
} // namespace

#ifdef _WIN32
int wmain(int argc, wchar_t* argv[]) {
    return hammond::cli::run_windows(argc, argv, generator_main,
        "hammond_generate_starter_registrations", {3, kMaximumArgumentBytes,
            "Use --output DIR or --help", "Argument exceeds 4096 UTF-8 bytes or is invalid Unicode"});
}
#else
int main(int argc, char* argv[]) { return generator_main(argc, argv); }
#endif
