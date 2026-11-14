#pragma once

#include "UiModel.h"

#include <array>
#include <cstddef>
#include <cstdint>
#include <string_view>

namespace hammond::standalone {

enum class InspectionSection : std::uint8_t {
    Generator = 0, ContactsRouting = 1, Scanner = 2,
    Ao28 = 3, Leslie = 4, Controls = 5,
};
enum class InspectionSnapshotState : std::uint8_t {
    Unavailable, Unprepared, Retained, Stopped, Current,
};
enum class InspectionAvailability : std::uint8_t {
    Available, NotObserved, NotIntegrated, NotAcquired, Invalid,
};
enum class InspectionEvidence : std::uint8_t {
    Software, Documented, Derived, Proposed, Unknown,
};
inline constexpr std::size_t kInspectionSectionCount = 6;
inline constexpr std::size_t kInspectionRowsPerSection = 6;
inline constexpr std::size_t kInspectionRotaryRows = 6;
inline constexpr std::size_t kInspectionTextCapacity = 128;

struct InspectionText {
    std::array<char, kInspectionTextCapacity> bytes{};
    std::uint16_t size{0};
    bool truncated{false};
    [[nodiscard]] std::string_view view() const noexcept;
};
struct InspectionRow {
    std::string_view id{}; // Stable presentation identity, never a sound parameter.
    std::string_view label{};
    InspectionText value{};
    std::string_view unit{};
    std::string_view source{};
    InspectionAvailability availability{InspectionAvailability::NotObserved};
    InspectionEvidence evidence{InspectionEvidence::Unknown};
};
struct InspectionCard {
    InspectionSection section{InspectionSection::Generator};
    std::string_view title{};
    std::string_view summary{};
    std::array<InspectionRow, kInspectionRowsPerSection> rows{};
    std::size_t row_count{0};
};
struct InspectionRuntimeInfo {
    bool snapshot_available{false};
    bool snapshot_read_succeeded{false};
};
struct InspectionDocument {
    InspectionSnapshotState snapshot_state{InspectionSnapshotState::Unavailable};
    bool controls_pending{false};
    std::uint64_t frame_clock{0};
    std::uint64_t publication_revision{0};
    InspectionText profile_id{};
    InspectionText profile_authoring_sha256{};
    std::array<InspectionCard, kInspectionSectionCount> sections{};
    std::array<InspectionRow, kInspectionRotaryRows> rotary_rows{};
    std::size_t rotary_row_count{0};
};

// Main-thread formatting of immutable, already copied inputs. No allocation,
// device queries, Session reads or Engine access. Output views refer only to
// program-lifetime literals; each dynamic value owns its bounded text storage.
// A loaded profile before preparation is not an observed active audio graph.
[[nodiscard]] InspectionDocument make_inspection_document(
    const RuntimeProfile& profile, const UiViewState& view,
    const InspectionRuntimeInfo& runtime) noexcept;

} // namespace hammond::standalone
