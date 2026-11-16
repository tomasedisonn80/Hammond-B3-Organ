#include "ControlFileInput.h"
#include "hammond/ControlStateIO.h"

#include <array>
#include <chrono>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <iterator>
#include <stdexcept>
#include <string>
#include <string_view>

#ifndef _WIN32
#include <sys/stat.h>
#endif

namespace {
namespace fs = std::filesystem;
using namespace hammond;
using namespace hammond::tools;
std::size_t checks = 0;
std::size_t link_skips = 0;

void check(bool condition, std::string_view expression, int line) {
    ++checks;
    if (!condition) throw std::runtime_error("line " + std::to_string(line) + ": " + std::string(expression));
}
#define REQUIRE(expression) check(static_cast<bool>(expression), #expression, __LINE__)

// Independent literal input/output oracle; no serializer prepares these bytes.
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

constexpr std::string_view kLegacyManuals =
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
            path_ = fs::temp_directory_path() / ("hammond-control-input-" + std::to_string(stamp) +
                "-" + std::to_string(attempt));
            std::error_code code;
            if (fs::create_directory(path_, code)) return;
            if (code && code != std::errc::file_exists) break;
        }
        throw std::runtime_error("Could not reserve control-input test directory");
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

[[nodiscard]] ControlFileInput sentinel() {
    ControlFileInput input;
    input.controls = expected_controls();
    input.controls.expression = 0.875;
    input.canonical_controls = std::string("old\0canonical", 13);
    input.source_version = 99;
    input.source_bytes = 17777;
    return input;
}

void refused(const fs::path& path, ControlFileInputStatus status) {
    auto destination = sentinel();
    const auto before = destination;
    const auto result = read_control_file(path, destination);
    REQUIRE(result.status == status);
    REQUIRE(!result.reason.empty() && result.reason.size() <= 256);
    REQUIRE(destination.controls == before.controls);
    REQUIRE(destination.canonical_controls == before.canonical_controls);
    REQUIRE(destination.source_version == before.source_version);
    REQUIRE(destination.source_bytes == before.source_bytes);
}

void successful_metadata_and_boundaries() {
    TemporaryTree tree;
    const auto file = tree.path() / "controls";
    const std::string padded = " \t\r\n\f\v" + std::string(kDocument);
    write_file(file, padded);
    auto destination = sentinel();
    const auto result = read_control_file(file, destination);
    REQUIRE(result.status == ControlFileInputStatus::Read && result.reason.empty());
    REQUIRE(destination.controls == expected_controls());
    REQUIRE(destination.canonical_controls == kDocument);
    REQUIRE(destination.source_version == 4 && destination.source_bytes == padded.size());
    REQUIRE(read_bytes(file) == padded);

    std::string exact(kDocument);
    exact.resize(kMaxControlStateBytes, ' ');
    write_file(file, exact);
    REQUIRE(read_control_file(file, destination).status == ControlFileInputStatus::Read);
    REQUIRE(destination.controls == expected_controls() && destination.canonical_controls == kDocument);
    REQUIRE(destination.source_version == 4 && destination.source_bytes == kMaxControlStateBytes);
    exact.push_back(' ');
    write_file(file, exact);
    refused(file, ControlFileInputStatus::TooLarge);
    REQUIRE(read_bytes(file) == exact);

    for (unsigned version = 1; version <= 3; ++version) {
        std::string legacy = " \tB3CONTROLS" + std::to_string(version) + "\nexpression 0.25\n";
        if (version >= 2) legacy += "percussion enabled 1 harmonic third volume soft decay fast\n";
        if (version >= 3) legacy += "pedal drawbars 7 3\n";
        legacy += kLegacyManuals;
        write_file(file, legacy);
        destination = sentinel();
        const auto migrated = read_control_file(file, destination);
        auto expected = expected_controls();
        expected.fixed_registrations = {FixedRegistration::None, FixedRegistration::None};
        if (version == 1) expected.percussion = {};
        if (version <= 2) expected.pedal_drawbars = {};
        REQUIRE(migrated.status == ControlFileInputStatus::Read && migrated.reason.empty());
        REQUIRE(destination.controls == expected);
        REQUIRE(destination.source_version == version && destination.source_bytes == legacy.size());
        REQUIRE(destination.canonical_controls.starts_with("B3CONTROLS4\n"));
        REQUIRE(read_bytes(file) == legacy);
    }
}

void transactional_refusals() {
    TemporaryTree tree;
    const auto file = tree.path() / "controls";
    refused(file, ControlFileInputStatus::Unavailable);
    refused(tree.path(), ControlFileInputStatus::NotRegularFile);
    std::string wrong_catalog(kDocument);
    wrong_catalog.replace(wrong_catalog.find("c9f1dd2d"), 8, "00000000");
    const std::array<std::string, 6> invalid{
        "", "B3CONTROLS5\n", std::string(kDocument) + "trailing\n",
        wrong_catalog, std::string(kDocument.substr(0, kDocument.size() - 4)),
        std::string(kDocument) + '\0'};
    for (const auto& bytes : invalid) {
        write_file(file, bytes);
        refused(file, ControlFileInputStatus::InvalidPayload);
        REQUIRE(read_bytes(file) == bytes);
    }
#ifndef _WIN32
    const auto fifo = tree.path() / "pipe";
    REQUIRE(::mkfifo(fifo.c_str(), 0600) == 0);
    refused(fifo, ControlFileInputStatus::NotRegularFile);
#else
    for (const auto* native : {L"CON", L"NUL", L"\\\\.\\pipe\\hammond-control-test",
            L"\\\\?\\C:\\hammond-control-test", L"\\\\server\\pipe\\hammond-control-test"}) {
        refused(fs::path(native), ControlFileInputStatus::NotRegularFile);
    }
#endif
}

void native_paths_and_links() {
    TemporaryTree tree;
    const auto directory = tree.path() / fs::path(u8"caf\u00e9 controls");
    REQUIRE(fs::create_directory(directory));
    const auto file = directory / "source";
    write_file(file, kDocument);
    auto destination = sentinel();
    REQUIRE(read_control_file(file, destination).status == ControlFileInputStatus::Read);
    REQUIRE(destination.controls == expected_controls() && destination.canonical_controls == kDocument);
    std::error_code code;
    const auto leaf = tree.path() / "leaf alias";
    fs::create_symlink(file, leaf, code);
    if (!code) {
        refused(leaf, ControlFileInputStatus::NotRegularFile);
        REQUIRE(read_bytes(file) == kDocument && fs::is_symlink(fs::symlink_status(leaf)));
    } else {
        ++link_skips;
    }
    const auto ancestor = tree.path() / "directory alias";
    code.clear();
    fs::create_directory_symlink(directory, ancestor, code);
    if (!code) {
        REQUIRE(read_control_file(ancestor / "source", destination).status == ControlFileInputStatus::Read);
        REQUIRE(destination.controls == expected_controls() && destination.canonical_controls == kDocument);
    } else {
        ++link_skips;
    }
    const auto hard_link = tree.path() / "hard alias";
    code.clear();
    fs::create_hard_link(file, hard_link, code);
    if (!code) {
        REQUIRE(fs::equivalent(file, hard_link));
        REQUIRE(read_control_file(hard_link, destination).status == ControlFileInputStatus::Read);
        REQUIRE(destination.controls == expected_controls() && destination.canonical_controls == kDocument);
        REQUIRE(read_bytes(file) == kDocument);
    } else {
        ++link_skips;
    }
}

} // namespace

int main() {
    try {
        successful_metadata_and_boundaries();
        transactional_refusals();
        native_paths_and_links();
        std::cout << "control_file_input checks=" << checks << " link_unavailable=" << link_skips << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "control_file_input: " << error.what() << '\n';
        return 1;
    }
}
