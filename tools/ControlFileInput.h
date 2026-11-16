#pragma once

#include "hammond/ControlState.h"

#include <cstddef>
#include <filesystem>
#include <string>

namespace hammond::tools {

enum class ControlFileInputStatus {
    Read, Unavailable, NotRegularFile, TooLarge, InvalidPayload
};

struct ControlFileInput {
    ControlSnapshot controls;
    std::string canonical_controls;
    unsigned source_version{};
    std::size_t source_bytes{};
};

struct ControlFileInputResult {
    ControlFileInputStatus status;
    std::string reason;
};

// Offline/control-thread only. Admit a bounded regular file through its opened
// handle without following its leaf link, then use the core parser and writer.
// Every failure preserves the complete destination; diagnostics are <=256 bytes.
[[nodiscard]] ControlFileInputResult read_control_file(
    const std::filesystem::path& path, ControlFileInput& destination);

} // namespace hammond::tools
