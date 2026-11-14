#include "StateFiles.h"
#include "hammond/ControlStateIO.h"

#include <array>
#include <chrono>
#include <cmath>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <iterator>
#include <limits>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>

#ifdef _WIN32
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#elif defined(__unix__) || defined(__APPLE__)
#include <csignal>
#include <sys/resource.h>
#endif

namespace {
namespace fs = std::filesystem;
using hammond::ControlSnapshot;
using hammond::DrawbarBank;
using hammond::FixedRegistration;
using hammond::standalone::load_control_file;
using hammond::standalone::save_control_file;

// Literal documents and field values are separate oracles. No production
// serializer generates an expected file or a legacy migration input.
constexpr std::string_view kManualRecords =
    "manual upper selected A route_enabled 0\n"
    "bank A 8 0 3 1 6 2 7 4 5\n"
    "bank B 1 2 3 4 5 6 7 8 0\n"
    "manual lower selected B route_enabled 1\n"
    "bank A 2 4 6 8 0 1 3 5 7\n"
    "bank B 7 5 3 1 8 6 4 2 0\n"
    "end\n";
constexpr std::string_view kPercussion =
    "percussion enabled 1 harmonic third volume soft decay fast\n";
constexpr std::string_view kDefaultPercussion =
    "percussion enabled 0 harmonic second volume normal decay slow\n";
constexpr std::string_view kLegacyDefaultDocument =
    "B3CONTROLS3\n"
    "expression 1\n"
    "percussion enabled 0 harmonic second volume normal decay slow\n"
    "pedal drawbars 0 0\n"
    "manual upper selected B route_enabled 1\n"
    "bank A 0 0 0 0 0 0 0 0 0\n"
    "bank B 0 0 0 0 0 0 0 0 0\n"
    "manual lower selected B route_enabled 1\n"
    "bank A 0 0 0 0 0 0 0 0 0\n"
    "bank B 0 0 0 0 0 0 0 0 0\n"
    "end\n";
constexpr std::string_view kCatalogRecord =
    "registration_catalog atlas-chapel-nominal-v1 sha256 "
    "c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf\n";
constexpr std::string_view kCurrentManualRecords =
    "manual upper selected A fixed_registration none route_enabled 0\n"
    "bank A 8 0 3 1 6 2 7 4 5\n"
    "bank B 1 2 3 4 5 6 7 8 0\n"
    "manual lower selected B fixed_registration none route_enabled 1\n"
    "bank A 2 4 6 8 0 1 3 5 7\n"
    "bank B 7 5 3 1 8 6 4 2 0\n"
    "end\n";
constexpr std::string_view kDefaultDocument =
    "B3CONTROLS4\n"
    "registration_catalog atlas-chapel-nominal-v1 sha256 "
    "c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf\n"
    "expression 1\n"
    "percussion enabled 0 harmonic second volume normal decay slow\n"
    "pedal drawbars 0 0\n"
    "manual upper selected B fixed_registration none route_enabled 1\n"
    "bank A 0 0 0 0 0 0 0 0 0\n"
    "bank B 0 0 0 0 0 0 0 0 0\n"
    "manual lower selected B fixed_registration none route_enabled 1\n"
    "bank A 0 0 0 0 0 0 0 0 0\n"
    "bank B 0 0 0 0 0 0 0 0 0\n"
    "end\n";

void require(bool condition, std::string_view detail) {
    // Exceptions unwind the private temporary tree even when a check fails.
    if (!condition) throw std::runtime_error(std::string(detail));
}

class TemporaryTree {
public:
    TemporaryTree() {
        const auto stamp = std::chrono::steady_clock::now().time_since_epoch().count();
        for (int attempt = 0; attempt < 100; ++attempt) {
            const auto candidate = fs::temp_directory_path() /
                ("hammond-state-files-test-" + std::to_string(stamp) + "-" +
                 std::to_string(attempt));
            std::error_code error;
            if (fs::create_directory(candidate, error)) {
                root_ = candidate;
                return;
            }
            require(!error || error == std::errc::file_exists,
                    "Could not create private temporary test directory");
        }
        throw std::runtime_error("Could not obtain a unique temporary test directory");
    }
    ~TemporaryTree() {
        if (!root_.empty()) {
            std::error_code ignored;
            fs::remove_all(root_, ignored);
        }
    }
    TemporaryTree(const TemporaryTree&) = delete;
    TemporaryTree& operator=(const TemporaryTree&) = delete;
    [[nodiscard]] const fs::path& root() const noexcept { return root_; }
    void cleanup() {
        fs::remove_all(root_);
        require(!fs::exists(root_), "Private test tree was not removed");
        root_.clear();
    }
private:
    fs::path root_;
};

ControlSnapshot varied_controls() {
    ControlSnapshot result;
    result.drawbars[0][0] = {8, 0, 3, 1, 6, 2, 7, 4, 5};
    result.drawbars[0][1] = {1, 2, 3, 4, 5, 6, 7, 8, 0};
    result.drawbars[1][0] = {2, 4, 6, 8, 0, 1, 3, 5, 7};
    result.drawbars[1][1] = {7, 5, 3, 1, 8, 6, 4, 2, 0};
    result.selected_banks = {DrawbarBank::A, DrawbarBank::B};
    result.route_enabled = {false, true};
    result.expression = 0.625;
    result.percussion = {true, hammond::PercussionHarmonic::Third,
                         hammond::PercussionVolume::Soft, hammond::PercussionDecay::Fast};
    result.pedal_drawbars = {6, 2};
    result.fixed_registrations = {FixedRegistration::CSharp, FixedRegistration::A};
    return result;
}

ControlSnapshot sentinel_controls() {
    auto result = varied_controls();
    result.expression = -0.0;
    result.selected_banks = {DrawbarBank::B, DrawbarBank::A};
    result.route_enabled = {true, false};
    result.pedal_drawbars = {8, 7};
    result.drawbars[1][1][8] = 8;
    result.fixed_registrations = {FixedRegistration::G, FixedRegistration::DSharp};
    return result;
}

std::string legacy_version3_document() {
    return std::string("B3CONTROLS3\nexpression 0.625\n") +
        std::string(kPercussion) + "pedal drawbars 6 2\n" + std::string(kManualRecords);
}

std::string canonical_document() {
    return
        "B3CONTROLS4\n"
        "registration_catalog atlas-chapel-nominal-v1 sha256 "
        "c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf\n"
        "expression 0.625\n"
        "percussion enabled 1 harmonic third volume soft decay fast\n"
        "pedal drawbars 6 2\n"
        "manual upper selected A fixed_registration C# route_enabled 0\n"
        "bank A 8 0 3 1 6 2 7 4 5\n"
        "bank B 1 2 3 4 5 6 7 8 0\n"
        "manual lower selected B fixed_registration A route_enabled 1\n"
        "bank A 2 4 6 8 0 1 3 5 7\n"
        "bank B 7 5 3 1 8 6 4 2 0\n"
        "end\n";
}

std::string replaced(std::string document, std::string_view from, std::string_view to) {
    const auto position = document.find(from);
    require(position != std::string::npos &&
            document.find(from, position + from.size()) == std::string::npos,
            "Fixture mutation must identify exactly one literal field");
    document.replace(position, from.size(), to);
    return document;
}

void same_controls(const ControlSnapshot& actual, const ControlSnapshot& expected) {
    require(actual == expected, "A retained control or route bit changed");
    require(std::signbit(actual.expression) == std::signbit(expected.expression),
            "Expression signed zero changed");
}

void write_bytes(const fs::path& path, std::string_view bytes) {
    std::ofstream stream(path, std::ios::binary | std::ios::trunc);
    require(static_cast<bool>(stream), "Could not write test fixture");
    stream.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
    stream.close();
    require(static_cast<bool>(stream), "Could not finish test fixture");
}

std::string read_bytes(const fs::path& path) {
    std::ifstream stream(path, std::ios::binary);
    require(static_cast<bool>(stream), "Could not read test fixture");
    std::string result{std::istreambuf_iterator<char>(stream), std::istreambuf_iterator<char>()};
    require(!stream.bad(), "Could not finish reading test fixture");
    return result;
}

void no_temporary_files(const fs::path& root) {
    const auto prefix = fs::path(".b3-save-").native();
    for (const auto& entry : fs::recursive_directory_iterator(root)) {
        require(!entry.path().filename().native().starts_with(prefix),
                "A .b3-save- temporary entry survived a complete API call");
    }
}

void expect_save(const fs::path& root, const fs::path& path,
                 const ControlSnapshot& controls, std::string_view expected) {
    std::string error = "stale diagnostic";
    const bool saved = save_control_file(path, controls, error);
    require(saved, "Valid save failed: " + error);
    require(error.empty(), "Successful save retained an error");
    require(fs::is_regular_file(fs::symlink_status(path)), "Save did not create a regular file");
    require(read_bytes(path) == expected, "Saved file differs from independent canonical bytes");
    no_temporary_files(root);
}

void expect_load(const fs::path& root, const fs::path& path,
                 const ControlSnapshot& expected) {
    auto destination = sentinel_controls();
    std::string error = "stale diagnostic";
    const bool loaded = load_control_file(path, destination, error);
    require(loaded, "Valid load failed: " + error);
    require(error.empty(), "Successful load retained an error");
    same_controls(destination, expected);
    no_temporary_files(root);
}

void reject_load(const fs::path& root, const fs::path& path) {
    auto destination = sentinel_controls();
    const auto before = destination;
    std::string error = "stale diagnostic";
    require(!load_control_file(path, destination, error), "Invalid load succeeded");
    require(!error.empty() && error != "stale diagnostic", "Rejected load omitted its diagnostic");
    same_controls(destination, before);
    no_temporary_files(root);
}

void reject_save(const fs::path& root, const fs::path& path,
                 const ControlSnapshot& controls = varied_controls()) {
    std::string error = "stale diagnostic";
    require(!save_control_file(path, controls, error), "Invalid save succeeded");
    require(!error.empty() && error != "stale diagnostic", "Rejected save omitted its diagnostic");
    no_temporary_files(root);
}

void normal_roundtrip_and_overwrite(const fs::path& root) {
    // char8_t input constructs the native path on Windows as well as POSIX;
    // this test does not depend on a narrow locale conversion of Unicode.
    const auto directory = root / fs::path(u8"registration space \u00e9 \u97f3");
    require(fs::create_directory(directory), "Could not create native Unicode directory");
    const auto path = directory / fs::path(u8"upper lower \u00f8 \u7434.b3controls");
    const auto controls = varied_controls();
    expect_save(root, path, controls, canonical_document());
    expect_load(root, path, controls);

    // A cancelled route is not enough to reconstruct either retained fixed row
    // or remembered bank. Save both cancelled rows, with expression negative zero.
    auto cancelled = controls;
    cancelled.expression = -0.0;
    cancelled.route_enabled[1] = false;
    const auto signed_zero_document = replaced(replaced(canonical_document(),
        "expression 0.625\n", "expression -0\n"),
        "manual lower selected B fixed_registration A route_enabled 1\n",
        "manual lower selected B fixed_registration A route_enabled 0\n");
    expect_save(root, path, cancelled, signed_zero_document);
    expect_load(root, path, cancelled);

    expect_save(root, path, ControlSnapshot{}, kDefaultDocument);
    expect_load(root, path, ControlSnapshot{});
    require(read_bytes(path) == kDefaultDocument, "Overwrite retained old file bytes");
}

void historical_migration(const fs::path& root) {
    const std::array<std::string, 3> historical{
        std::string("B3CONTROLS1\nexpression 0.625\n") + std::string(kManualRecords),
        std::string("B3CONTROLS2\nexpression 0.625\n") +
            std::string(kPercussion) + std::string(kManualRecords),
        legacy_version3_document()};
    for (std::size_t index = 0; index < historical.size(); ++index) {
        const auto path = root / ("legacy-" + std::to_string(index + 1) + ".b3controls");
        write_bytes(path, historical[index]);
        auto expected = varied_controls();
        expected.fixed_registrations = {FixedRegistration::None, FixedRegistration::None};
        if (index < 2) expected.pedal_drawbars = {0, 0};
        if (index == 0) expected.percussion = {};
        expect_load(root, path, expected);
        require(read_bytes(path) == historical[index], "Loading rewrote an old-format file");
        const auto upgraded = std::string("B3CONTROLS4\n") + std::string(kCatalogRecord) +
            "expression 0.625\n" +
            std::string(index == 0 ? kDefaultPercussion : kPercussion) +
            (index < 2 ? "pedal drawbars 0 0\n" : "pedal drawbars 6 2\n") +
            std::string(kCurrentManualRecords);
        expect_save(root, path, expected, upgraded);
        expect_load(root, path, expected);
    }
    // Retain the complete former default-writer literal as a version-3 input.
    const auto defaults = root / "legacy-default-3.b3controls";
    write_bytes(defaults, kLegacyDefaultDocument);
    expect_load(root, defaults, ControlSnapshot{});
    require(read_bytes(defaults) == kLegacyDefaultDocument, "Loading rewrote legacy defaults");
    expect_save(root, defaults, ControlSnapshot{}, kDefaultDocument);
}

void rejected_documents_preserve_destination(const fs::path& root) {
    const auto valid = canonical_document();
    const std::array<std::string, 13> invalid{
        "", "not a control-state file\n", valid.substr(0, valid.size() - 5),
        valid + "held_note upper 60\n",
        replaced(valid, "B3CONTROLS4\n", "B3CONTROLS5\n"),
        valid.substr(0, valid.rfind("end")) + "bank B 9\nend\n",
        valid + std::string(hammond::kMaxControlStateBytes + 1 - valid.size(), ' '),
        // The historical bare version-4 mutation remains malformed, and cannot
        // fall back to a legacy reader when its new mandatory fields are absent.
        std::string("B3CONTROLS4") +
            legacy_version3_document().substr(std::string_view("B3CONTROLS3").size()),
        // Validate catalog binding even when BOTH retained modes are none.
        replaced(std::string(kDefaultDocument), "atlas-chapel-nominal-v1",
                 "atlas-chapel-nominal-v2"),
        replaced(std::string(kDefaultDocument), "c9f1dd2d", "d9f1dd2d"),
        replaced(std::string(kDefaultDocument), "e7b72ebcbf722cf\n", "e7b72ebcbf722c\n"),
        replaced(std::string(kDefaultDocument), kCatalogRecord, ""),
        replaced(valid, "fixed_registration C#", "fixed_registration c#")};
    const auto path = root / "rejected.b3controls";
    for (const auto& document : invalid) {
        write_bytes(path, document);
        reject_load(root, path);
        require(read_bytes(path) == document, "Rejected load modified the input file");
    }
    const auto maximum = valid + std::string(hammond::kMaxControlStateBytes - valid.size(), ' ');
    write_bytes(path, maximum);
    expect_load(root, path, varied_controls());
    require(read_bytes(path) == maximum, "Maximum-size load modified the input file");
}

void invalid_controls_preserve_target(const fs::path& root) {
    const auto path = root / "keep-existing.b3controls";
    const std::string original = "existing user bytes\r\nincluding an unrelated suffix\n";
    write_bytes(path, original);
    std::array<ControlSnapshot, 10> invalid;
    invalid.fill(varied_controls());
    invalid[0].drawbars[1][0][8] = 9;
    invalid[1].selected_banks[0] = static_cast<DrawbarBank>(255);
    invalid[2].expression = std::numeric_limits<double>::quiet_NaN();
    invalid[3].expression = -0.25;
    invalid[4].percussion.harmonic = static_cast<hammond::PercussionHarmonic>(255);
    invalid[5].percussion.volume = static_cast<hammond::PercussionVolume>(255);
    invalid[6].percussion.decay = static_cast<hammond::PercussionDecay>(255);
    invalid[7].pedal_drawbars[1] = 9;
    invalid[8].fixed_registrations[0] = static_cast<FixedRegistration>(10);
    invalid[9].fixed_registrations[1] = static_cast<FixedRegistration>(255);
    invalid[9].route_enabled[1] = false;
    for (const auto& controls : invalid) {
        reject_save(root, path, controls);
        require(read_bytes(path) == original, "Invalid controls changed the existing target");
    }
    const auto absent = root / "invalid-must-not-create.b3controls";
    reject_save(root, absent, invalid[8]);
    require(!fs::exists(absent), "Invalid controls created a target");
}

void path_rejections(const fs::path& root) {
    const auto missing_parent = root / "caller-must-create-parent";
    const auto missing = missing_parent / "state.b3controls";
    reject_load(root, missing);
    reject_save(root, missing);
    require(!fs::exists(missing_parent), "Helper created a missing parent directory");

    const auto directory = root / "directory-is-not-a-state-file";
    require(fs::create_directory(directory), "Could not create directory fixture");
    write_bytes(directory / "keep.txt", "directory child survives\n");
    reject_load(root, directory);
    reject_save(root, directory);
    require(read_bytes(directory / "keep.txt") == "directory child survives\n",
            "Rejected directory operation modified its child");

    const auto parent_file = root / "parent-is-a-file";
    write_bytes(parent_file, "regular parent survives\n");
    reject_load(root, parent_file / "state.b3controls");
    reject_save(root, parent_file / "state.b3controls");
    require(read_bytes(parent_file) == "regular parent survives\n", "Parent file changed");
    reject_load(root, fs::path{});
    for (const auto& empty_name : std::array<fs::path, 4>{fs::path{}, root / "", root / ".", root / ".."}) {
        reject_save(root, empty_name);
    }
}

bool symlink_unavailable(const std::error_code& error) {
#ifdef _WIN32
    if (error.category() == std::system_category() &&
        error.value() == static_cast<int>(ERROR_PRIVILEGE_NOT_HELD)) return true;
#endif
    return error == std::errc::operation_not_permitted ||
        error == std::errc::permission_denied || error == std::errc::not_supported ||
        error == std::errc::function_not_supported;
}

void symlink_rejections(const fs::path& root) {
    const auto target = root / "symlink-referent.b3controls";
    const auto link = root / "symlink-state.b3controls";
    const auto dangling = root / "dangling-state.b3controls";
    const auto absent = root / "missing-referent.b3controls";
    write_bytes(target, canonical_document());
    std::error_code error;
    fs::create_symlink(target.filename(), link, error);
    if (error) {
        require(symlink_unavailable(error), "Unexpected symbolic-link setup failure: " + error.message());
        std::cout << "NOT TESTED: symlink policy; platform could not create a symbolic link: "
                  << error.message() << '\n';
        return;
    }
    fs::create_symlink(absent.filename(), dangling);
    for (const auto& candidate : std::array<fs::path, 2>{link, dangling}) {
        const auto original_link = fs::read_symlink(candidate);
        reject_load(root, candidate);
        reject_save(root, candidate);
        require(fs::is_symlink(fs::symlink_status(candidate)), "A symbolic link was replaced");
        require(fs::read_symlink(candidate) == original_link, "A symbolic link's target changed");
        require(read_bytes(target) == canonical_document(), "Symbolic-link referent changed");
        require(!fs::exists(absent), "Dangling symbolic-link referent was created");
    }
    std::cout << "TESTED: regular and dangling symbolic-link load/save rejection\n";
}

#if defined(__unix__) || defined(__APPLE__)
class FileSizeLimit {
public:
    FileSizeLimit() {
        require(getrlimit(RLIMIT_FSIZE, &original_) == 0, "Could not read file-size resource limit");
        previous_signal_ = std::signal(SIGXFSZ, SIG_IGN);
        require(previous_signal_ != SIG_ERR, "Could not install bounded-write signal guard");
        auto limited = original_;
        limited.rlim_cur = original_.rlim_max == 0 ? 0 : 1;
        if (setrlimit(RLIMIT_FSIZE, &limited) != 0) {
            std::signal(SIGXFSZ, previous_signal_);
            throw std::runtime_error("Could not impose deterministic file-size resource limit");
        }
    }
    ~FileSizeLimit() {
        if (active_) {
            static_cast<void>(setrlimit(RLIMIT_FSIZE, &original_));
            std::signal(SIGXFSZ, previous_signal_);
        }
    }
    FileSizeLimit(const FileSizeLimit&) = delete;
    FileSizeLimit& operator=(const FileSizeLimit&) = delete;
    void restore() {
        require(setrlimit(RLIMIT_FSIZE, &original_) == 0, "Could not restore file-size resource limit");
        require(std::signal(SIGXFSZ, previous_signal_) != SIG_ERR, "Could not restore file-size signal");
        active_ = false;
    }
private:
    struct rlimit original_ {};
    using SignalHandler = void (*)(int);
    SignalHandler previous_signal_{};
    bool active_{true};
};
#endif

void failure_after_temporary_creation(const fs::path& root) {
    const auto path = root / "failed-publication.b3controls";
    const auto original = canonical_document();
    write_bytes(path, original);
#ifdef _WIN32
    class LockedFile {
    public:
        explicit LockedFile(const fs::path& target)
            : handle_(CreateFileW(target.c_str(), GENERIC_READ, FILE_SHARE_READ, nullptr,
                                  OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr)) {
            require(handle_ != INVALID_HANDLE_VALUE, "Could not lock target against replacement");
        }
        ~LockedFile() { CloseHandle(handle_); }
        LockedFile(const LockedFile&) = delete;
        LockedFile& operator=(const LockedFile&) = delete;
    private:
        HANDLE handle_;
    };
    {
        const LockedFile locked(path);
        reject_save(root, path, ControlSnapshot{});
    }
    std::cout << "TESTED: failed replacement under a Windows sharing lock and temporary cleanup\n";
#elif defined(__unix__) || defined(__APPLE__)
    {
        FileSizeLimit limit;
        reject_save(root, path, ControlSnapshot{});
        const auto absent = root / "failed-write-must-not-create.b3controls";
        reject_save(root, absent);
        require(!fs::exists(absent), "Failed temporary write created a target");
        limit.restore();
    }
    std::cout << "TESTED: failed write under RLIMIT_FSIZE and temporary cleanup\n"
                 "NOT TESTED: POSIX failed replacement after a complete temporary write; "
                 "no deterministic non-racing fixture\n";
#else
    std::cout << "NOT TESTED: controlled write/replace failure on this platform\n";
#endif
    require(read_bytes(path) == original, "Failed publication modified the existing target");
    no_temporary_files(root);
    expect_save(root, path, ControlSnapshot{}, kDefaultDocument);
}
} // namespace

int main() {
    try {
        TemporaryTree tree;
        normal_roundtrip_and_overwrite(tree.root());
        historical_migration(tree.root());
        rejected_documents_preserve_destination(tree.root());
        invalid_controls_preserve_target(tree.root());
        path_rejections(tree.root());
        symlink_rejections(tree.root());
        failure_after_temporary_creation(tree.root());
        tree.cleanup();
        std::cout << "Standalone state-file acceptance: 7 scenarios completed; "
                     "platform exclusions are reported above\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Standalone state-file acceptance failed: " << error.what() << '\n';
        return 1;
    }
}
