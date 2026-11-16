#include "RegistrationLibrary.h"
#include "hammond/ControlStateIO.h"

#include <algorithm>
#include <array>
#include <barrier>
#include <chrono>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <iterator>
#include <limits>
#include <stdexcept>
#include <string>
#include <string_view>
#include <thread>

#ifndef _WIN32
#include <sys/stat.h>
#endif

namespace {
namespace fs = std::filesystem;
using namespace hammond;
using namespace hammond::standalone;
std::size_t checks = 0;
std::size_t link_skips = 0;

void check(bool condition, std::string_view expression, int line) {
    ++checks;
    if (!condition) throw std::runtime_error("line " + std::to_string(line) + ": " + std::string(expression));
}
#define REQUIRE(expression) check(static_cast<bool>(expression), #expression, __LINE__)

// Literal payload and independent literal field expectations. The serializer
// under test does not generate these input documents or the save-byte oracle.
constexpr std::string_view kDocument =
    "B3CONTROLS4\n"
    "registration_catalog atlas-chapel-nominal-v1 sha256 "
    "c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf\n"
    "expression 0.25\n"
    "percussion enabled 1 harmonic third volume soft decay fast\n"
    "pedal drawbars 7 3\n"
    "manual upper selected A fixed_registration D# route_enabled 0\n"
    "bank A 8 0 3 1 6 2 7 4 5\n"
    "bank B 1 2 3 4 5 6 7 8 0\n"
    "manual lower selected B fixed_registration G# route_enabled 1\n"
    "bank A 2 4 6 8 0 1 3 5 7\n"
    "bank B 7 5 3 1 8 6 4 2 0\n"
    "end\n";

constexpr std::string_view kOldManuals =
    "manual upper selected A route_enabled 0\n"
    "bank A 8 0 3 1 6 2 7 4 5\n"
    "bank B 1 2 3 4 5 6 7 8 0\n"
    "manual lower selected B route_enabled 1\n"
    "bank A 2 4 6 8 0 1 3 5 7\n"
    "bank B 7 5 3 1 8 6 4 2 0\n"
    "end\n";

[[nodiscard]] ControlSnapshot expected_controls() {
    ControlSnapshot controls;
    controls.drawbars[0][0] = {8, 0, 3, 1, 6, 2, 7, 4, 5};
    controls.drawbars[0][1] = {1, 2, 3, 4, 5, 6, 7, 8, 0};
    controls.drawbars[1][0] = {2, 4, 6, 8, 0, 1, 3, 5, 7};
    controls.drawbars[1][1] = {7, 5, 3, 1, 8, 6, 4, 2, 0};
    controls.selected_banks = {DrawbarBank::A, DrawbarBank::B};
    controls.route_enabled = {false, true};
    controls.fixed_registrations = {FixedRegistration::DSharp, FixedRegistration::GSharp};
    controls.expression = 0.25;
    controls.pedal_drawbars = {7, 3};
    controls.percussion = {true, PercussionHarmonic::Third, PercussionVolume::Soft, PercussionDecay::Fast};
    return controls;
}

class TemporaryTree {
public:
    TemporaryTree() {
        const auto stamp = std::chrono::steady_clock::now().time_since_epoch().count();
        for (int attempt = 0; attempt < 100; ++attempt) {
            path_ = fs::temp_directory_path() / ("hammond-library-test-" + std::to_string(stamp) +
                "-" + std::to_string(attempt));
            std::error_code code;
            if (fs::create_directory(path_, code)) return;
            if (code && code != std::errc::file_exists) break;
        }
        throw std::runtime_error("Could not reserve test directory");
    }
    ~TemporaryTree() {
        std::error_code ignored;
        (void)fs::remove_all(path_, ignored);
    }
    TemporaryTree(const TemporaryTree&) = delete;
    TemporaryTree& operator=(const TemporaryTree&) = delete;
    [[nodiscard]] const fs::path& path() const noexcept { return path_; }
private:
    fs::path path_;
};

void write_file(const fs::path& path, std::string_view bytes) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    output.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
    output.close();
    if (!output) throw std::runtime_error("Fixture write failed");
}

[[nodiscard]] std::string read_bytes(const fs::path& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) throw std::runtime_error("Fixture read failed");
    return {std::istreambuf_iterator<char>(input), std::istreambuf_iterator<char>()};
}

[[nodiscard]] LibraryCommitAuthorization permit() { return {true, {}}; }

[[nodiscard]] LibrarySaveResult save(const fs::path& root, std::string_view name,
    RegistrationScope scope = RegistrationScope::Registration) {
    return save_registration_entry_new(root, name, scope, expected_controls(), {}, permit);
}

[[nodiscard]] const LibraryEntry& find_entry(const LibraryCatalog& catalog, std::string_view key) {
    const auto found = std::find_if(catalog.entries.begin(), catalog.entries.end(),
        [key](const LibraryEntry& entry) { return entry.key == key; });
    if (found == catalog.entries.end()) throw std::runtime_error("Expected row missing: " + std::string(key));
    return *found;
}

[[nodiscard]] std::size_t staging_count(const fs::path& root) {
    std::size_t count = 0;
    for (const auto& item : fs::directory_iterator(root)) {
        const auto name = item.path().filename().string();
        if (name.starts_with(".b3-library-save-")) ++count;
    }
    return count;
}

void names_and_scopes() {
    for (const std::string_view name : {"A", "Sunday warm", "Combo_2-A", "COM0", "COM10", "CONtemporary"}) {
        REQUIRE(is_valid_registration_name(name));
    }
    REQUIRE(is_valid_registration_name(std::string(48, 'A')));
    REQUIRE(!is_valid_registration_name(std::string(49, 'A')));
    for (const std::string_view name : {"", " A", "A ", "-A", "A_", ".", "A.B", "A/B", "A\\B", "A\nB",
            "CON", "pRn", "aux", "NUL", "cOm1", "COM9", "lpt1", "LPT9", "\xc3\xa9"}) {
        REQUIRE(!is_valid_registration_name(name));
    }
    REQUIRE(is_valid_registration_name_draft(""));
    REQUIRE(is_valid_registration_name_draft("CON"));
    REQUIRE(is_valid_registration_name_draft("A "));
    REQUIRE(!is_valid_registration_name_draft("A.B"));
    REQUIRE(!is_valid_registration_name_draft(std::string(49, 'A')));
    const auto entry = expected_controls();
    ControlSnapshot desired;
    desired.expression = 0.875; // A newer desired CC11 value, not entry.expression.
    ControlSnapshot destination;
    REQUIRE(merge_registration_controls(RegistrationScope::Registration, entry, desired, destination));
    auto expected = entry;
    expected.expression = 0.875;
    REQUIRE(destination == expected);
    REQUIRE(destination.drawbars[0][0] == DrawbarPositions({8, 0, 3, 1, 6, 2, 7, 4, 5}));
    REQUIRE(destination.drawbars[0][1] == DrawbarPositions({1, 2, 3, 4, 5, 6, 7, 8, 0}));
    REQUIRE(destination.drawbars[1][0] == DrawbarPositions({2, 4, 6, 8, 0, 1, 3, 5, 7}));
    REQUIRE(destination.drawbars[1][1] == DrawbarPositions({7, 5, 3, 1, 8, 6, 4, 2, 0}));
    REQUIRE(destination.fixed_registrations[0] == FixedRegistration::DSharp && !destination.route_enabled[0]);
    REQUIRE(destination.fixed_registrations[1] == FixedRegistration::GSharp && destination.route_enabled[1]);
    REQUIRE(destination.pedal_drawbars == PedalDrawbarPositions({7, 3}));
    REQUIRE(destination.percussion == entry.percussion);
    REQUIRE(registration_controls_equal(RegistrationScope::Registration, destination, entry));
    REQUIRE(!registration_controls_equal(RegistrationScope::Performance, destination, entry));
    REQUIRE(merge_registration_controls(RegistrationScope::Performance, entry, desired, destination));
    REQUIRE(destination == entry);
    auto invalid = entry;
    invalid.drawbars[1][1][8] = 9;
    REQUIRE(!merge_registration_controls(RegistrationScope::Registration, invalid, desired, destination));
    REQUIRE(destination == entry);
    invalid = desired;
    invalid.expression = std::numeric_limits<double>::quiet_NaN();
    REQUIRE(!merge_registration_controls(RegistrationScope::Performance, entry, invalid, destination));
    REQUIRE(destination == entry);
    const auto invalid_scope = static_cast<RegistrationScope>(255);
    REQUIRE(!merge_registration_controls(invalid_scope, entry, desired, destination));
    REQUIRE(!registration_controls_equal(invalid_scope, entry, entry));
    REQUIRE(!registration_controls_equal(RegistrationScope::Registration, invalid, invalid));
    auto changed = entry;
    changed.pedal_drawbars[1] = 1;
    REQUIRE(!registration_controls_equal(RegistrationScope::Registration, entry, changed));
}

void reading_and_catalogs() {
    TemporaryTree tree;
    const auto root = tree.path() / "library";
    const auto missing = scan_registration_library(root, 11);
    REQUIRE(missing.complete() && missing.status == LibraryCatalogStatus::MissingDirectory);
    REQUIRE(missing.generation == 11 && !fs::exists(root));
    REQUIRE(fs::create_directory(root));
    REQUIRE(scan_registration_library(root).status == LibraryCatalogStatus::Empty);
    write_file(root / "Warm.b3registration", kDocument);
    write_file(root / "Warm.b3performance", kDocument);
    write_file(root / "Alpha.b3registration", kDocument);
    write_file(root / "Ignored.B3REGISTRATION", kDocument);
    write_file(root / "Ignored.b3controls", kDocument);
    // A leading hyphen is invalid for the library but an ordinary filename on
    // every platform. CON is a Win32 device alias even with this extension;
    // reserved names are tested through validators, never by writing a device.
    write_file(root / "-Bad.b3registration", kDocument);
    write_file(root / "bad.name.b3registration", kDocument);
#ifdef _WIN32
    write_file(root / fs::path(L"\u00e9.b3registration"), kDocument);
#else
    write_file(root / fs::path("\xc3\xa9.b3registration"), kDocument);
#endif
    write_file(root / "Broken.b3registration", "B3CONTROLS5\n");
    REQUIRE(fs::create_directory(root / "Directory.b3registration"));
    std::string exact(kDocument);
    exact.resize(kMaxControlStateBytes, ' ');
    write_file(root / "Exact.b3registration", exact);
    exact.push_back(' ');
    write_file(root / "Oversize.b3registration", exact);
    auto catalog = scan_registration_library(root, 12);
    REQUIRE(catalog.complete() && catalog.generation == 12);
    REQUIRE(catalog.directory_items == 12 && catalog.candidate_count == 10);
    REQUIRE(catalog.invalid_name_count == 3 && catalog.invalid_entry_count == 3);
    REQUIRE(catalog.entries.size() == 7 && catalog.entries.front().name == "Alpha");
    REQUIRE(find_entry(catalog, "Exact.b3registration").valid());
    REQUIRE(find_entry(catalog, "Oversize.b3registration").status == LibraryEntryStatus::TooLarge);
    REQUIRE(find_entry(catalog, "Directory.b3registration").status == LibraryEntryStatus::NotRegularFile);
    REQUIRE(find_entry(catalog, "Broken.b3registration").status == LibraryEntryStatus::InvalidPayload);
    REQUIRE(*find_entry(catalog, "Warm.b3registration").controls == expected_controls());
    for (const auto& entry : catalog.entries) REQUIRE(entry.reason.size() <= 256);
    const auto repeated = scan_registration_library(root);
    REQUIRE(repeated.entries.size() == catalog.entries.size());
    for (std::size_t i = 0; i < catalog.entries.size(); ++i) REQUIRE(repeated.entries[i].key == catalog.entries[i].key);
    REQUIRE(!read_registration_entry(root, "../Warm.b3registration").valid());
    REQUIRE(read_registration_entry(root, "CON.b3registration").status == LibraryEntryStatus::InvalidKey);
    REQUIRE(!read_registration_entry(root, "Warm.b3registration/child").valid());
    REQUIRE(!read_registration_entry(root, "Warm.B3REGISTRATION").valid());
    std::string changed(kDocument);
    changed.replace(changed.find("expression 0.25"), std::string_view("expression 0.25").size(), "expression 0.75");
    write_file(root / "Warm.b3registration", changed);
    const auto reread = read_registration_entry(root, "Warm.b3registration");
    REQUIRE(reread.valid() && reread.controls->expression == 0.75);
    REQUIRE(find_entry(catalog, "Warm.b3registration").controls->expression == 0.25);
    write_file(root / "Trailing.b3registration", std::string(kDocument) + "unexpected\n");
    REQUIRE(read_registration_entry(root, "Trailing.b3registration").status == LibraryEntryStatus::InvalidPayload);

    for (int version = 1; version <= 3; ++version) {
        std::string legacy = "B3CONTROLS" + std::to_string(version) + "\nexpression 0.25\n";
        if (version >= 2) legacy += "percussion enabled 1 harmonic third volume soft decay fast\n";
        if (version >= 3) legacy += "pedal drawbars 7 3\n";
        legacy += kOldManuals;
        const auto key = "Old" + std::to_string(version) + ".b3performance";
        write_file(root / key, legacy);
        auto expected = expected_controls();
        expected.fixed_registrations = {FixedRegistration::None, FixedRegistration::None};
        if (version == 1) expected.percussion = {};
        if (version <= 2) expected.pedal_drawbars = {};
        const auto read = read_registration_entry(root, key);
        REQUIRE(read.valid() && *read.controls == expected);
        REQUIRE(read_bytes(root / key) == legacy);
    }
    // Case variants are distinct files only on a case-sensitive volume.
    write_file(root / "warm.b3registration", kDocument);
    std::error_code code;
    const bool distinct = !fs::equivalent(root / "Warm.b3registration", root / "warm.b3registration", code);
    REQUIRE(!code);
    catalog = scan_registration_library(root);
    if (distinct) {
        REQUIRE(catalog.ambiguous_entry_count == 2);
        REQUIRE(find_entry(catalog, "Warm.b3registration").status == LibraryEntryStatus::Ambiguous);
        REQUIRE(!find_entry(catalog, "warm.b3registration").controls);
    } else {
        REQUIRE(catalog.ambiguous_entry_count == 0);
    }
    REQUIRE(find_entry(catalog, "Warm.b3performance").valid());

    const auto target = tree.path() / "outside";
    write_file(target, kDocument);
    fs::create_symlink(target, root / "Link.b3registration", code);
    if (!code) {
        REQUIRE(read_registration_entry(root, "Link.b3registration").status == LibraryEntryStatus::NotRegularFile);
    } else {
        ++link_skips;
    }
#ifndef _WIN32
    REQUIRE(::mkfifo((root / "Pipe.b3registration").c_str(), 0600) == 0);
    REQUIRE(read_registration_entry(root, "Pipe.b3registration").status == LibraryEntryStatus::NotRegularFile);
    REQUIRE(!find_entry(scan_registration_library(root), "Pipe.b3registration").valid());
#endif
    write_file(tree.path() / "ordinary", "not a directory");
    REQUIRE(scan_registration_library(tree.path() / "ordinary").status == LibraryCatalogStatus::InvalidRoot);
    REQUIRE(scan_registration_library({}).status == LibraryCatalogStatus::InvalidRoot);
}

void save_and_protection() {
    TemporaryTree tree;
    const auto root = tree.path() / "library";
    const auto saved = save(root, "Sunday warm");
    REQUIRE(saved.status == LibrarySaveStatus::Saved && saved.committed());
    REQUIRE(saved.committed_entry && *saved.committed_entry->controls == expected_controls());
    REQUIRE(saved.refreshed_catalog && saved.refreshed_catalog->complete());
    REQUIRE(read_bytes(root / "Sunday warm.b3registration") == kDocument);
    REQUIRE(staging_count(root) == 0);
    REQUIRE(save(root, "sunday WARM").status == LibrarySaveStatus::NameExists);
    REQUIRE(read_bytes(root / "Sunday warm.b3registration") == kDocument);
    REQUIRE(save(root, "Sunday warm", RegistrationScope::Performance).committed());
    REQUIRE(save(root, "CON").status == LibrarySaveStatus::InvalidName);
    REQUIRE(save(root, "Bad", static_cast<RegistrationScope>(255)).status == LibrarySaveStatus::InvalidScope);
    auto invalid = expected_controls();
    invalid.expression = -1;
    REQUIRE(save_registration_entry_new(root, "Invalid", RegistrationScope::Registration,
        invalid, {}, permit).status == LibrarySaveStatus::InvalidControls);
    REQUIRE(save_registration_entry_new(root, "No authorization", RegistrationScope::Registration,
        expected_controls(), {}, {}).status == LibrarySaveStatus::NotAuthorized);
    std::size_t authorizations = 0;
    const auto cancelled = save_registration_entry_new(root, "Cancelled", RegistrationScope::Registration,
        expected_controls(), {}, [&]() {
            ++authorizations;
            REQUIRE(staging_count(root) == 1);
            REQUIRE(!fs::exists(root / "Cancelled.b3registration"));
            return LibraryCommitAuthorization{false, std::string(400, 'x')};
        });
    REQUIRE(cancelled.status == LibrarySaveStatus::NotAuthorized && !cancelled.committed());
    REQUIRE(authorizations == 1 && cancelled.reason.size() == 256);
    REQUIRE(!fs::exists(root / "Cancelled.b3registration") && staging_count(root) == 0);
    const auto thrown = save_registration_entry_new(root, "Throw", RegistrationScope::Registration,
        expected_controls(), {}, []() -> LibraryCommitAuthorization { throw std::runtime_error("no fresh snapshot"); });
    REQUIRE(thrown.status == LibrarySaveStatus::NotAuthorized && staging_count(root) == 0);
    const std::array<fs::path, 1> protected_destination{root / "OUTPUT.b3registration"};
    const auto protected_save = save_registration_entry_new(root, "Output", RegistrationScope::Registration,
        expected_controls(), protected_destination, permit);
    REQUIRE(protected_save.status == LibrarySaveStatus::ProtectedPath && !protected_save.committed());
    REQUIRE(!fs::exists(root / "Output.b3registration"));
    const auto absent_root = tree.path() / "reserved";
    const std::array<fs::path, 1> protected_root{tree.path() / "RESERVED"};
    REQUIRE(save_registration_entry_new(absent_root, "A", RegistrationScope::Registration,
        expected_controls(), protected_root, permit).status == LibrarySaveStatus::ProtectedPath);
    REQUIRE(!fs::exists(absent_root));
    const auto missing_parents = tree.path() / "missing" / "child";
    REQUIRE(save(missing_parents, "A").status == LibrarySaveStatus::DirectoryUnavailable);
    REQUIRE(!fs::exists(tree.path() / "missing"));
    std::error_code code;
    const auto alias = tree.path() / "alias";
    fs::create_directory_symlink(root, alias, code);
    if (!code) {
        const std::array<fs::path, 1> protected_alias{alias / "Alias.b3registration"};
        REQUIRE(save_registration_entry_new(root, "Alias", RegistrationScope::Registration,
            expected_controls(), protected_alias, permit).status == LibrarySaveStatus::ProtectedPath);
        fs::path resolved;
        std::string error;
        REQUIRE(resolve_registration_library_root(alias, resolved, error));
        REQUIRE(fs::equivalent(resolved, root));
    } else {
        ++link_skips;
    }
    // An injected exact-path creator at the final authorization boundary wins;
    // the native no-replace commit must preserve its arbitrary existing bytes.
    const auto collision = save_registration_entry_new(root, "Late winner", RegistrationScope::Registration,
        expected_controls(), {}, [&]() {
            write_file(root / "Late winner.b3registration", "other process owns this\n");
            return permit();
        });
    REQUIRE(collision.status == LibrarySaveStatus::NameExists && !collision.committed());
    REQUIRE(read_bytes(root / "Late winner.b3registration") == "other process owns this\n");
    REQUIRE(staging_count(root) == 0);
}

void unicode_path_protection() {
    TemporaryTree tree;
    const auto output = tree.path() / "output";
    const auto source = tree.path() / "source";
    REQUIRE(fs::create_directory(output));
    REQUIRE(fs::create_directory(source));
    write_file(source / "reference.controls", "protected source bytes\n");
    const std::array<fs::path, 1> protected_source{source / "reference.controls"};

    // Distinct complete ASCII ancestors prove separation even though a later
    // Unicode component makes a flat byte-offset comparison uncertain.
    const auto unicode_parent = output / fs::path(u8"caf\u00e9 staging");
    REQUIRE(fs::create_directory(unicode_parent));
    const auto root = unicode_parent / "entries";
    const auto saved = save_registration_entry_new(root, "Unicode", RegistrationScope::Registration,
        expected_controls(), protected_source, permit);
    REQUIRE(saved.status == LibrarySaveStatus::Saved && saved.committed());
    REQUIRE(read_bytes(root / "Unicode.b3registration") == kDocument);
    REQUIRE(read_bytes(protected_source[0]) == "protected source bytes\n");
    REQUIRE(staging_count(root) == 0);
    const auto repeated = save_registration_entry_new(root, "Second", RegistrationScope::Performance,
        expected_controls(), protected_source, permit);
    REQUIRE(repeated.status == LibrarySaveStatus::Saved && repeated.committed());
    REQUIRE(read_bytes(root / "Second.b3performance") == kDocument);
    REQUIRE(staging_count(root) == 0);

    // A shared exact Unicode ancestor is also compatible with distinct ASCII
    // leaf components. The same-parent suffix comparison must agree.
    const std::array<fs::path, 1> sibling{unicode_parent / "reserved.controls"};
    const auto sibling_save = save_registration_entry_new(root, "Sibling", RegistrationScope::Registration,
        expected_controls(), sibling, permit);
    REQUIRE(sibling_save.status == LibrarySaveStatus::Saved && sibling_save.committed());
    REQUIRE(!fs::exists(sibling[0]));

    // Normalization/case variants can have different native lengths. ASCII
    // differences at shifted byte offsets are never a distinct-component proof.
    const auto uncertain_parent = tree.path() / fs::path(u8"caf\u00e9");
    REQUIRE(fs::create_directory(uncertain_parent));
    const auto uncertain_root = uncertain_parent / "reserved";
    for (const auto& spelling : {fs::path(u8"cafe\u0301"), fs::path(u8"CAF\u00c9")}) {
        const std::array<fs::path, 1> uncertain{tree.path() / spelling / "RESERVED"};
        std::size_t authorizations = 0;
        const auto refused = save_registration_entry_new(uncertain_root, "Blocked", RegistrationScope::Registration,
            expected_controls(), uncertain, [&]() { ++authorizations; return permit(); });
        REQUIRE(refused.status == LibrarySaveStatus::ProtectedPath && !refused.committed());
        REQUIRE(authorizations == 0 && !fs::exists(uncertain_root));
    }

    // Canonical/equivalent aliases stay protected even when invocation paths
    // have distinct ASCII ancestors and one contains Unicode.
    std::error_code code;
    const auto alias = source / "output alias";
    fs::create_directory_symlink(root, alias, code);
    if (!code) {
        REQUIRE(fs::equivalent(alias, root));
        const std::array<fs::path, 1> reserved_alias{alias / "ALIAS.b3registration"};
        const auto refused = save_registration_entry_new(root, "Alias", RegistrationScope::Registration,
            expected_controls(), reserved_alias, permit);
        REQUIRE(refused.status == LibrarySaveStatus::ProtectedPath && !refused.committed());
        REQUIRE(!fs::exists(root / "Alias.b3registration") && staging_count(root) == 0);
    } else {
        ++link_skips;
    }

    const auto hard_alias = source / "hard alias.controls";
    code.clear();
    fs::create_hard_link(root / "Unicode.b3registration", hard_alias, code);
    if (!code) {
        REQUIRE(fs::equivalent(hard_alias, root / "Unicode.b3registration"));
        const std::array<fs::path, 1> reserved_hard_alias{hard_alias};
        const auto refused = save_registration_entry_new(root, "Unicode", RegistrationScope::Registration,
            expected_controls(), reserved_hard_alias, permit);
        REQUIRE(refused.status == LibrarySaveStatus::NameExists && !refused.committed());
        REQUIRE(read_bytes(hard_alias) == kDocument);
        REQUIRE(read_bytes(root / "Unicode.b3registration") == kDocument);
    } else {
        ++link_skips;
    }

    const auto dangling = source / "dangling alias";
    code.clear();
    fs::create_symlink(source / "missing target", dangling, code);
    if (!code) {
        const std::array<fs::path, 1> unresolved{dangling};
        const auto refused = save_registration_entry_new(root, "Unresolved", RegistrationScope::Registration,
            expected_controls(), unresolved, permit);
        REQUIRE(refused.status == LibrarySaveStatus::ProtectedPath && !refused.committed());
        REQUIRE(!fs::exists(root / "Unresolved.b3registration") && staging_count(root) == 0);
        REQUIRE(fs::is_symlink(fs::symlink_status(dangling)));
    } else {
        ++link_skips;
    }
#ifdef _WIN32
    const auto initial_items = std::distance(fs::recursive_directory_iterator(tree.path()),
        fs::recursive_directory_iterator{});
    for (const auto* spelling : {L"ambiguous.", L"ambiguous ", L"ambiguous:stream",
            L"...", L". ", L".. "}) {
        const std::array<fs::path, 1> ambiguous{source / spelling};
        std::size_t authorizations = 0;
        const auto refused = save_registration_entry_new(root, "Ambiguous", RegistrationScope::Registration,
            expected_controls(), ambiguous, [&]() { ++authorizations; return permit(); });
        REQUIRE(refused.status == LibrarySaveStatus::ProtectedPath && !refused.committed());
        REQUIRE(authorizations == 0);
        REQUIRE(!fs::exists(root / "Ambiguous.b3registration") && staging_count(root) == 0);
        const auto ambiguous_root = unicode_parent / spelling;
        const auto root_refused = save_registration_entry_new(ambiguous_root, "Ambiguous root",
            RegistrationScope::Registration, expected_controls(), {},
            [&]() { ++authorizations; return permit(); });
        REQUIRE(root_refused.status == LibrarySaveStatus::InvalidRoot && !root_refused.committed());
        REQUIRE(scan_registration_library(ambiguous_root).status == LibraryCatalogStatus::InvalidRoot);
        REQUIRE(authorizations == 0);
        REQUIRE(std::distance(fs::recursive_directory_iterator(tree.path()),
            fs::recursive_directory_iterator{}) == initial_items);
        REQUIRE(read_bytes(protected_source[0]) == "protected source bytes\n");
    }
    // Raw navigation must reach each entry point, rather than relying on a
    // caller that has already normalized it. Both legal spellings remain usable.
    const std::array<fs::path, 2> navigation_roots{root / ".", root / ".." / "entries"};
    const std::array<fs::path, 2> navigation_sources{
        source / "." / "reference.controls", source / ".." / "source" / "reference.controls"};
    for (std::size_t index = 0; index < navigation_roots.size(); ++index) {
        const std::array<fs::path, 1> reserved{navigation_sources[index]};
        const auto name = "Navigation " + std::to_string(index);
        std::size_t authorizations = 0;
        const auto navigation = save_registration_entry_new(navigation_roots[index], name,
            RegistrationScope::Registration, expected_controls(), reserved,
            [&]() { ++authorizations; return permit(); });
        REQUIRE(navigation.status == LibrarySaveStatus::Saved && navigation.committed());
        REQUIRE(authorizations == 1 && read_bytes(root / (name + ".b3registration")) == kDocument);
        REQUIRE(read_bytes(protected_source[0]) == "protected source bytes\n" && staging_count(root) == 0);
    }
#endif
}

void capacity() {
    TemporaryTree tree;
    const auto candidates = tree.path() / "candidates";
    REQUIRE(fs::create_directory(candidates));
    for (std::size_t i = 0; i < 128; ++i) write_file(candidates / ("Row" + std::to_string(i) + ".b3registration"), kDocument);
    const auto full = scan_registration_library(candidates, 71);
    REQUIRE(full.complete() && full.entries.size() == 128 && full.candidate_count == 128);
    REQUIRE(save(candidates, "Extra").status == LibrarySaveStatus::CapacityExceeded);
    write_file(candidates / "invalid.name.b3registration", kDocument);
    const auto overflow = scan_registration_library(candidates, 72);
    REQUIRE(!overflow.complete() && overflow.status == LibraryCatalogStatus::CapacityExceeded);
    REQUIRE(overflow.entries.empty() && overflow.candidate_count == 129);
    REQUIRE(full.entries.size() == 128 && full.generation == 71);
    const auto items = tree.path() / "items";
    REQUIRE(fs::create_directory(items));
    for (std::size_t i = 0; i < 511; ++i) write_file(items / ("ignored" + std::to_string(i)), "");
    REQUIRE(scan_registration_library(items).directory_items == 511);
    const auto boundary_save = save(items, "Last room");
    REQUIRE(boundary_save.status == LibrarySaveStatus::Saved);
    REQUIRE(boundary_save.refreshed_catalog->directory_items == 512);
    REQUIRE(staging_count(items) == 0);
    REQUIRE(save(items, "No room").status == LibrarySaveStatus::CapacityExceeded);
    write_file(items / "overflow", "");
    const auto item_overflow = scan_registration_library(items);
    REQUIRE(item_overflow.status == LibraryCatalogStatus::CapacityExceeded && item_overflow.entries.empty());
    REQUIRE(item_overflow.directory_items == 513);
}

void concurrent_and_committed_warning() {
    TemporaryTree tree;
    const auto root = tree.path() / "concurrent";
    REQUIRE(fs::create_directory(root));
    std::barrier rendezvous(2);
    std::array<LibrarySaveResult, 2> results;
    auto first = expected_controls();
    auto second = first;
    second.expression = 0.75;
    const auto worker = [&](std::size_t i, const ControlSnapshot& controls) {
        results[i] = save_registration_entry_new(root, "Shared", RegistrationScope::Registration,
            controls, {}, [&]() { rendezvous.arrive_and_wait(); return permit(); });
    };
    // Explicitly joined threads also support the pinned Apple libc++ baseline.
    std::thread a(worker, 0U, std::cref(first));
    std::thread b(worker, 1U, std::cref(second));
    a.join();
    b.join();
    REQUIRE(results[0].committed() != results[1].committed());
    const std::size_t winner = results[0].committed() ? 0 : 1;
    REQUIRE(results[1 - winner].status == LibrarySaveStatus::NameExists);
    const auto actual = read_registration_entry(root, "Shared.b3registration");
    REQUIRE(actual.valid() && *actual.controls == (winner == 0 ? first : second));
    REQUIRE(staging_count(root) == 0);
    const auto warnings = tree.path() / "warnings";
    REQUIRE(fs::create_directory(warnings));
    // Deliberately leave an unowned occupant in the owned staging directory.
    // Production cleanup must not recursively delete it or misreport commit.
    const auto cleanup_warning = save_registration_entry_new(warnings, "Complete", RegistrationScope::Registration,
        expected_controls(), {}, [&]() {
            for (const auto& item : fs::directory_iterator(warnings)) {
                if (item.is_directory()) write_file(item.path() / "foreign", "retain me");
            }
            return permit();
        });
    REQUIRE(cleanup_warning.status == LibrarySaveStatus::SavedWithWarning && cleanup_warning.committed());
    REQUIRE(cleanup_warning.committed_entry && *cleanup_warning.committed_entry->controls == expected_controls());
    REQUIRE(read_bytes(warnings / "Complete.b3registration") == kDocument);
    REQUIRE(staging_count(warnings) == 1);
    REQUIRE(cleanup_warning.reason.find("cleanup") != std::string::npos);
    const auto refresh = tree.path() / "refresh";
    REQUIRE(fs::create_directory(refresh));
    // External directory changes after final admission may invalidate refresh,
    // but cannot retroactively turn an already committed save into a failure.
    const auto refresh_warning = save_registration_entry_new(refresh, "Committed", RegistrationScope::Registration,
        expected_controls(), {}, [&]() {
            for (std::size_t i = 0; i < 128; ++i) write_file(refresh / ("New" + std::to_string(i) + ".b3registration"), kDocument);
            return permit();
        });
    REQUIRE(refresh_warning.status == LibrarySaveStatus::SavedWithWarning && refresh_warning.committed());
    REQUIRE(refresh_warning.committed_entry && refresh_warning.committed_entry->key == "Committed.b3registration");
    REQUIRE(refresh_warning.refreshed_catalog && !refresh_warning.refreshed_catalog->complete());
    REQUIRE(read_bytes(refresh / "Committed.b3registration") == kDocument);
    REQUIRE(staging_count(refresh) == 0);
}

} // namespace

int main() {
    try {
        names_and_scopes();
        reading_and_catalogs();
        save_and_protection();
        unicode_path_protection();
        capacity();
        concurrent_and_committed_warning();
        std::cout << "registration_library checks=" << checks << " symlink_unavailable=" << link_skips << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "registration_library: " << error.what() << '\n';
        return 1;
    }
}
