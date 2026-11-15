#pragma once

#include "hammond/Types.h"

#include <array>
#include <filesystem>
#include <iosfwd>
#include <span>
#include <string>
#include <string_view>

namespace hammond {

inline constexpr std::size_t kMaxSourceLeakageEdgesPerDestination = 8;
inline constexpr std::size_t kMaxSourceLeakageEdges =
    kToneSourceCount * kMaxSourceLeakageEdgesPerDestination;
inline constexpr std::size_t kMaxCompiledSourceLeakageBytes = 128 * 1024;
inline constexpr std::size_t kSourceLeakageProfileIdMaxLength = 64;
inline constexpr std::size_t kSourceLeakageSha256HexLength = 64;
inline constexpr std::string_view kSourceLeakageModel = "static-source-leakage-v1";
inline constexpr std::string_view kSourceLeakageEvidenceStatus = "synthetic";
inline constexpr std::string_view kSourceLeakageBoundary =
    "normalized-generator-precontact-v1";
inline constexpr std::string_view kSourceLeakageSourceContent = "excludes-leakage";

using SourceLeakageFrame = std::array<double, kToneSourceCount>;

struct SourceLeakageEdge {
    ToneId source{0};
    ToneId destination{0};
    // Dimensionless synthetic coupling, not a measured pickup coefficient.
    double gain{0.0};
};

// Simultaneous y = x + Cx on normalized, uncoupled generator frames. The
// allocation-free state owns every coefficient. Replacement requires a stopped
// or exclusively owned processing thread; concurrent preparation is unsupported.
class SourceLeakage {
public:
    SourceLeakage() noexcept = default;

    // Accepts any author ordering. Failure preserves the entire previous state.
    [[nodiscard]] Status prepare(std::span<const SourceLeakageEdge> edges) noexcept;

    // Inputs must all be finite and in [-1, 1]. Full input/output aliasing is
    // supported. Unprepared or invalid calls leave output untouched. No clipping
    // or headroom gain is applied; downstream unit-domain consumers must supply
    // an explicitly validated headroom gain.
    [[nodiscard]] Status process_frame(const SourceLeakageFrame& input,
                                       SourceLeakageFrame& output) const noexcept;

    [[nodiscard]] bool prepared() const noexcept { return prepared_; }
    [[nodiscard]] std::size_t edge_count() const noexcept { return edge_count_; }
    [[nodiscard]] bool row_absolute_gain_sum(ToneId destination,
                                             double& value) const noexcept;
    [[nodiscard]] double max_row_absolute_gain_sum() const noexcept {
        return max_row_absolute_gain_sum_;
    }

private:
    struct Term {
        std::size_t source_index{0};
        double gain{0.0};
    };
    struct Row {
        std::array<Term, kMaxSourceLeakageEdgesPerDestination> terms{};
        std::size_t count{0};
        double absolute_gain_sum{0.0};
    };

    // Rows follow destination IDs; terms are sorted by ascending source ID.
    std::array<Row, kToneSourceCount> rows_{};
    std::size_t edge_count_{0};
    double max_row_absolute_gain_sum_{0.0};
    bool prepared_{false};
};

static_assert(sizeof(SourceLeakage) <= 32 * 1024,
              "Source leakage state must fit its fixed 32 KiB budget.");

// Zero initialization is intentionally invalid: provenance is required. Only
// edge_count entries are used, in strict (destination, source) ascending order.
struct SourceLeakageProfile {
    std::array<char, kSourceLeakageProfileIdMaxLength + 1> profile_id{};
    std::array<char, kSourceLeakageSha256HexLength + 1> authoring_sha256{};
    std::array<SourceLeakageEdge, kMaxSourceLeakageEdges> edges{};
    std::size_t edge_count{0};
};

[[nodiscard]] Status validate_source_leakage_profile(
    const SourceLeakageProfile& profile) noexcept;

// Native loaders may allocate and perform I/O; never call them from processing.
// Failure preserves destination. The digest is retained provenance supplied by
// the file, not verification of authoring bytes that were not supplied.
[[nodiscard]] bool load_source_leakage_profile(std::istream& input,
                                               SourceLeakageProfile& destination,
                                               std::string& error);
[[nodiscard]] bool load_source_leakage_profile_file(
    const std::filesystem::path& path, SourceLeakageProfile& destination,
    std::string& error);

} // namespace hammond
