#pragma once

#include "hammond/ControlState.h"

#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <functional>
#include <optional>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace hammond::standalone {

inline constexpr std::size_t kRegistrationLibraryMaxNameBytes = 48;
inline constexpr std::size_t kRegistrationLibraryMaxEntries = 128;
inline constexpr std::size_t kRegistrationLibraryMaxDirectoryItems = 512;
inline constexpr std::size_t kRegistrationLibraryMaxDiagnosticBytes = 256;
inline constexpr std::size_t kRegistrationLibraryTemporaryAttempts = 32;

enum class RegistrationScope : std::uint8_t { Registration, Performance };
using LibraryEntryKey = std::string; // Exact, validated relative ASCII filename.

enum class LibraryEntryStatus : std::uint8_t {
    Valid, InvalidKey, Ambiguous, InvalidPayload, TooLarge, NotRegularFile, Unavailable
};

struct LibraryEntry {
    LibraryEntryKey key;
    std::string name;
    RegistrationScope scope{RegistrationScope::Registration};
    LibraryEntryStatus status{LibraryEntryStatus::InvalidKey};
    std::string reason;
    std::optional<ControlSnapshot> controls;

    [[nodiscard]] bool valid() const noexcept {
        return status == LibraryEntryStatus::Valid && controls.has_value();
    }
};

enum class LibraryCatalogStatus : std::uint8_t {
    Ready, Empty, MissingDirectory, InvalidRoot, CapacityExceeded, DirectoryUnavailable
};

struct LibraryCatalog {
    std::vector<LibraryEntry> entries;
    std::uint64_t generation{};
    LibraryCatalogStatus status{LibraryCatalogStatus::DirectoryUnavailable};
    std::string reason;
    std::size_t directory_items{};
    std::size_t candidate_count{}; // Includes recognized suffixes with invalid names.
    std::size_t invalid_name_count{};
    std::size_t invalid_entry_count{};
    std::size_t ambiguous_entry_count{};

    [[nodiscard]] bool complete() const noexcept {
        return status == LibraryCatalogStatus::Ready || status == LibraryCatalogStatus::Empty ||
               status == LibraryCatalogStatus::MissingDirectory;
    }
    [[nodiscard]] std::size_t warning_count() const noexcept {
        return invalid_name_count + invalid_entry_count + ambiguous_entry_count;
    }
};

enum class LibrarySaveStatus : std::uint8_t {
    Saved, SavedWithWarning, InvalidName, InvalidScope, InvalidControls, NameExists,
    CapacityExceeded, InvalidRoot, DirectoryUnavailable, ProtectedPath, StagingFailed,
    WriteFailed, FlushFailed, CloseFailed, NotAuthorized, CommitFailed
};

struct LibraryCommitAuthorization {
    bool permitted{};
    std::string reason;
};
using LibraryAuthorizeCommit = std::function<LibraryCommitAuthorization()>;

struct LibrarySaveResult {
    LibrarySaveStatus status{LibrarySaveStatus::CommitFailed};
    std::string reason;
    // Retained after commit even when cleanup or the following refresh fails.
    std::optional<LibraryEntry> committed_entry;
    std::optional<LibraryCatalog> refreshed_catalog;

    [[nodiscard]] bool committed() const noexcept {
        return status == LibrarySaveStatus::Saved || status == LibrarySaveStatus::SavedWithWarning;
    }
};

[[nodiscard]] bool is_valid_registration_scope(RegistrationScope scope) noexcept;
[[nodiscard]] bool is_valid_registration_name(std::string_view name) noexcept;
// Drafts may be empty, reserved, or start/end with a permitted interior byte.
[[nodiscard]] bool is_valid_registration_name_draft(std::string_view name) noexcept;
[[nodiscard]] std::string_view registration_scope_suffix(RegistrationScope scope) noexcept;
[[nodiscard]] std::string_view registration_scope_label(RegistrationScope scope) noexcept;

// Resolve once at invocation setup. Existing symlink ancestors are allowed;
// missing roots are retained, without creating anything. Failure preserves root.
[[nodiscard]] bool resolve_registration_library_root(const std::filesystem::path& requested,
                                                      std::filesystem::path& root,
                                                      std::string& error);

// Main-thread operations only. No Session, Engine, stream, or filesystem handle
// is retained. A failed scan has no partial rows; the model keeps its old catalog
// and marks it stale. The caller supplies its generation without implicit wrap.
[[nodiscard]] LibraryCatalog scan_registration_library(const std::filesystem::path& root,
                                                        std::uint64_t generation = 0);
[[nodiscard]] LibraryEntry read_registration_entry(const std::filesystem::path& root,
                                                    std::string_view key);

// New canonical B3CONTROLS4 file only. A missing root may be created when its
// parent exists. All paths this operation creates are checked against protected
// outputs. The synchronous authorizer is mandatory and runs after staging and
// final admission, immediately before atomic no-replace publication. It must not
// pump events or submit a new intent. Returning false/throwing cancels the save.
[[nodiscard]] LibrarySaveResult save_registration_entry_new(
    const std::filesystem::path& root, std::string_view name, RegistrationScope scope,
    const ControlSnapshot& acknowledged, std::span<const std::filesystem::path> protected_paths,
    const LibraryAuthorizeCommit& authorize_commit);

// Pure, validated operations. Registration differs from Performance only by
// preserving/ignoring expression; all other current fields are copied/compared.
// Invalid inputs leave destination unchanged, including invalid enum values.
[[nodiscard]] bool merge_registration_controls(RegistrationScope scope,
    const ControlSnapshot& entry, const ControlSnapshot& latest_desired,
    ControlSnapshot& destination) noexcept;
[[nodiscard]] bool registration_controls_equal(RegistrationScope scope,
    const ControlSnapshot& a, const ControlSnapshot& b) noexcept;

} // namespace hammond::standalone
