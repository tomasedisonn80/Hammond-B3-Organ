#pragma once

#include <array>
#include <cstdint>
#include <span>
#include <string_view>

namespace hammond::research {

inline constexpr std::string_view kCausalContactGridModelId =
    "causal-contact-grid-v1";
inline constexpr std::uint32_t kContactGridTicksPerFrame = 65536;
inline constexpr std::uint64_t kContactGridFullTravel = std::uint64_t{1} << 48;
inline constexpr std::uint32_t kContactGridMaxKeys = 4;
inline constexpr std::uint32_t kContactGridContactsPerKey = 9;
inline constexpr std::uint32_t kContactGridMaxFrames = 4096;
inline constexpr std::uint32_t kContactGridMaxCommands = 512;
inline constexpr std::uint32_t kContactGridMaxEdges = 4608;

struct ContactGridThreshold {
    std::uint64_t off{}, on{};
};

struct ContactGridKeyConfig {
    std::uint32_t pressUnitsPerTick{}, releaseUnitsPerTick{};
    std::array<ContactGridThreshold, 9> contacts{};
};

struct ContactGridConfig {
    std::uint32_t sampleRateHz{}, keyCount{};
    std::array<ContactGridKeyConfig, 4> keys{};
};

struct ContactGridTarget {
    std::uint32_t tick{}, keyIndex{};
    std::uint64_t position{};
};

// Exact epoch ticks plus a reduced proper fraction; integer times use 0/1.
struct ContactGridTime {
    std::uint32_t tick{}, numerator{};
    std::uint32_t denominator{1};
};

struct ContactGridEdge {
    ContactGridTime time{};
    std::uint32_t keyIndex{}, contactIndex{};
    bool closedAfter{};
};

enum class ContactGridPhase : std::uint8_t {
    unprepared, ready, active, closed
};

enum class ContactGridStatus : std::uint8_t {
    ok, invalid_state, invalid_configuration, frame_limit, command_limit,
    invalid_target, unordered_targets, output_too_small, arithmetic_overflow
};

struct ContactGridResult {
    ContactGridStatus status{ContactGridStatus::ok};
    std::uint32_t edgesWritten{}, requiredEdges{};
};

struct ContactGridKeySnapshot {
    std::uint64_t position{}, target{}, anchorPosition{};
    std::uint32_t anchorTick{};
    std::array<bool, 9> closed{};
};

struct ContactGridSnapshot {
    ContactGridPhase phase{ContactGridPhase::unprepared};
    ContactGridConfig config{};
    std::uint32_t cursorFrames{}, commandCount{}, edgeCount{};
    std::array<ContactGridKeySnapshot, 4> keys{};
};

// Isolated synthetic trajectory model; see docs/CAUSAL_CONTACT_GRID_CONTRACT.md.
// All access, including snapshots, must be serialized and non-reentrant. Spans
// must have valid, stable, mutually nonoverlapping storage outside this object.
// All operations use fixed storage and perform no allocation, locking or I/O.
class CausalContactGrid {
public:
    CausalContactGrid() noexcept;
    CausalContactGrid(const CausalContactGrid&) = delete;
    CausalContactGrid& operator=(const CausalContactGrid&) = delete;

    // Stopped operation, allowed only while unprepared, ready or closed.
    // Copies active configuration and starts a fresh ready epoch on success.
    [[nodiscard]] ContactGridStatus prepare(const ContactGridConfig&) noexcept;

    // Commands occupy [cursor,end); edges occupy (cursor,end]. A zero-frame
    // call with no commands is an identity. Failure preserves state and output;
    // short output reports the actual required edge count without writing.
    [[nodiscard]] ContactGridResult process(
        std::uint32_t frames, std::span<const ContactGridTarget> targets,
        std::span<ContactGridEdge> output) noexcept;

    // Counts/applies commands at the cursor without travel or new edges.
    [[nodiscard]] ContactGridStatus close_observation(
        std::span<const ContactGridTarget> endpointTargets) noexcept;
    // Closed only; retains configuration and clears the completed epoch.
    [[nodiscard]] ContactGridStatus reset() noexcept;
    [[nodiscard]] ContactGridSnapshot snapshot() const noexcept;

private:
    [[nodiscard]] bool advance_interval(std::uint32_t beginTick,
                                        std::uint32_t endTick,
                                        std::uint32_t& callEdges) noexcept;

    ContactGridSnapshot state_{};
    ContactGridSnapshot staged_{};
    std::array<ContactGridEdge, kContactGridMaxEdges> stagedEdges_{};
    std::array<ContactGridEdge,
               kContactGridMaxKeys * kContactGridContactsPerKey> intervalEdges_{};
};

} // namespace hammond::research
