#include "StateFiles.h"
#include "hammond/ControlStateIO.h"

#include <atomic>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <system_error>

#ifdef _WIN32
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#endif

namespace hammond::standalone {
namespace {

class TemporaryState {
public:
    explicit TemporaryState(std::filesystem::path directory)
        : directory_(std::move(directory)), file_(directory_ / "controls.tmp") {}
    ~TemporaryState() {
        std::error_code ignored;
        std::filesystem::remove(file_, ignored);
        std::filesystem::remove(directory_, ignored);
    }
    TemporaryState(const TemporaryState&) = delete;
    TemporaryState& operator=(const TemporaryState&) = delete;
    [[nodiscard]] const std::filesystem::path& file() const noexcept { return file_; }
private:
    std::filesystem::path directory_;
    std::filesystem::path file_;
};

[[nodiscard]] bool replace_file(const std::filesystem::path& from,
                                 const std::filesystem::path& to,
                                 std::string& error) {
#ifdef _WIN32
    if (MoveFileExW(from.c_str(), to.c_str(),
                    MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH) == 0) {
        const auto code = static_cast<int>(GetLastError());
        error = "Could not replace saved controls: " +
            std::error_code(code, std::system_category()).message();
        return false;
    }
#else
    std::error_code code;
    std::filesystem::rename(from, to, code);
    if (code) {
        error = "Could not replace saved controls: " + code.message();
        return false;
    }
#endif
    return true;
}

} // namespace

bool load_control_file(const std::filesystem::path& path, ControlSnapshot& destination,
                       std::string& error) {
    std::error_code code;
    const auto status = std::filesystem::symlink_status(path, code);
    if (code || !std::filesystem::is_regular_file(status)) {
        error = "Choose an existing regular control-state file";
        return false;
    }
    std::ifstream input(path, std::ios::binary);
    if (!input) {
        error = "Could not open saved controls";
        return false;
    }
    return parse_controls(input, destination, error);
}

bool save_control_file(const std::filesystem::path& path, const ControlSnapshot& controls,
                       std::string& error) {
    std::string text;
    if (!serialize_controls(controls, text, error)) return false;
    if (path.empty() || path.filename().empty() || path.filename() == "." ||
        path.filename() == "..") {
        error = "Choose a control-state filename";
        return false;
    }
    std::error_code code;
    const auto status = std::filesystem::symlink_status(path, code);
    if (code && code != std::errc::no_such_file_or_directory) {
        error = "Could not inspect control-state destination: " + code.message();
        return false;
    }
    if (std::filesystem::exists(status) && !std::filesystem::is_regular_file(status)) {
        error = "Control-state destination must be a regular file";
        return false;
    }
    const auto parent = path.has_parent_path() ? path.parent_path() : std::filesystem::path(".");
    code.clear();
    if (!std::filesystem::is_directory(parent, code) || code) {
        error = "Control-state destination directory does not exist";
        return false;
    }
    static std::atomic<std::uint64_t> serial{0};
    const auto stamp = std::chrono::steady_clock::now().time_since_epoch().count();
    std::filesystem::path temporary;
    bool created = false;
    for (int attempt = 0; attempt < 32; ++attempt) {
        temporary = parent / (".b3-save-" + std::to_string(stamp) + "-" +
            std::to_string(serial.fetch_add(1, std::memory_order_relaxed)));
        code.clear();
        if (std::filesystem::create_directory(temporary, code)) {
            created = true;
            break;
        }
        if (code && code != std::errc::file_exists) break;
    }
    if (!created) {
        error = "Could not create temporary control-state file";
        return false;
    }
    const TemporaryState pending(temporary);
    std::ofstream output(pending.file(), std::ios::binary | std::ios::trunc);
    if (!output) {
        error = "Could not open temporary control-state file";
        return false;
    }
    output.write(text.data(), static_cast<std::streamsize>(text.size()));
    output.flush();
    if (!output) {
        error = "Could not write complete control state";
        return false;
    }
    output.close();
    if (!output) {
        error = "Could not close complete control-state file";
        return false;
    }
    if (!replace_file(pending.file(), path, error)) return false;
    error.clear();
    return true;
}

} // namespace hammond::standalone
