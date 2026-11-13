#pragma once

#include "hammond/ControlState.h"

#include <filesystem>
#include <string>

namespace hammond::standalone {

// Main-thread file operations only; the existing B3CONTROLS parser/writer owns
// the musical format. No Engine, held-note or DSP-history serialization occurs.
// Failures preserve the destination snapshot or existing on-disk file.
[[nodiscard]] bool load_control_file(const std::filesystem::path& path,
                                     ControlSnapshot& destination,
                                     std::string& error);
[[nodiscard]] bool save_control_file(const std::filesystem::path& path,
                                     const ControlSnapshot& controls,
                                     std::string& error);

} // namespace hammond::standalone
