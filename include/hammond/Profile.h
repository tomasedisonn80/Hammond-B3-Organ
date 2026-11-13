#pragma once

#include "hammond/Types.h"

#include <array>
#include <filesystem>
#include <iosfwd>
#include <string>
#include <string_view>

namespace hammond {

inline constexpr std::size_t kMaxCompiledProfileBytes = 128 * 1024;
inline constexpr std::size_t kProfileIdMaxLength = 64;
inline constexpr std::size_t kSha256HexLength = 64;
inline constexpr std::string_view kNominalProfileId = "nominal-unmeasured-v1";

struct ToneSource {
    double frequency_hz{0.0};
    // Proposed normalized peak amplitude, never a calibrated pickup voltage.
    double peak_amplitude{0.0};
    double base_phase_turns{0.0};
};

using ManualMap = std::array<std::array<ToneId, kDrawbarCount>, kManualKeyCount>;

// All data is value-owned. Zero initialization intentionally produces an invalid
// profile, not an undocumented substitute for missing authoring data.
struct RuntimeProfile {
    std::array<char, kProfileIdMaxLength + 1> profile_id{};
    std::array<char, kSha256HexLength + 1> authoring_sha256{};
    double output_gain{0.0};
    std::array<double, kDrawbarPositionCount> drawbar_gains{};
    std::array<ToneSource, kToneSourceCount> sources{};
    ManualMap manual_map{};
};

// Bounded, allocation-free validation for preparation. Unsupported sample rates
// return InvalidSpec; invalid data (including Nyquist violations) InvalidProfile.
[[nodiscard]] Status validate_runtime_profile(const RuntimeProfile& profile,
                                              double sample_rate) noexcept;

// These loaders perform I/O, parsing and allocation and require audio processing
// to be stopped. Only the exact version-1 grammar in docs/PROFILE_FORMAT.md is
// accepted. Failure preserves destination and provides a descriptive error.
// The supplied digest is retained provenance, not verification of unseen JSON.
[[nodiscard]] bool load_runtime_profile(std::istream& input,
                                        RuntimeProfile& destination,
                                        std::string& error);
[[nodiscard]] bool load_runtime_profile_file(const std::filesystem::path& path,
                                             RuntimeProfile& destination,
                                             std::string& error);

} // namespace hammond
