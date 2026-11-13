#include "hammond/ParameterBridge.h"

#include <array>
#include <cmath>

namespace hammond {
namespace {

// Literal metadata for this approved internal subset. This table is checked
// against the independent JSON registry by the cross-language test; it is never
// parsed, allocated or generated while processing audio.
constexpr std::array<ParameterDescriptor, kParameterCount> kDescriptors{{
    {4096U, "manual.upper.bank.A.drawbar.16ft", "drawbar_position",
     "drawbar-position", 8.0, 0.0, 8,
     EventType::BankDrawbar, Manual::Upper, 0},
    {4097U, "manual.upper.bank.A.drawbar.5_1/3ft", "drawbar_position",
     "drawbar-position", 8.0, 0.0, 8,
     EventType::BankDrawbar, Manual::Upper, 1},
    {4098U, "manual.upper.bank.A.drawbar.8ft", "drawbar_position",
     "drawbar-position", 8.0, 0.0, 8,
     EventType::BankDrawbar, Manual::Upper, 2},
    {4099U, "manual.upper.bank.A.drawbar.4ft", "drawbar_position",
     "drawbar-position", 8.0, 0.0, 8,
     EventType::BankDrawbar, Manual::Upper, 3},
    {4100U, "manual.upper.bank.A.drawbar.2_2/3ft", "drawbar_position",
     "drawbar-position", 8.0, 0.0, 8,
     EventType::BankDrawbar, Manual::Upper, 4},
    {4101U, "manual.upper.bank.A.drawbar.2ft", "drawbar_position",
     "drawbar-position", 8.0, 0.0, 8,
     EventType::BankDrawbar, Manual::Upper, 5},
    {4102U, "manual.upper.bank.A.drawbar.1_3/5ft", "drawbar_position",
     "drawbar-position", 8.0, 0.0, 8,
     EventType::BankDrawbar, Manual::Upper, 6},
    {4103U, "manual.upper.bank.A.drawbar.1_1/3ft", "drawbar_position",
     "drawbar-position", 8.0, 0.0, 8,
     EventType::BankDrawbar, Manual::Upper, 7},
    {4104U, "manual.upper.bank.A.drawbar.1ft", "drawbar_position",
     "drawbar-position", 8.0, 0.0, 8,
     EventType::BankDrawbar, Manual::Upper, 8},
    {4112U, "manual.upper.bank.B.drawbar.16ft", "drawbar_position",
     "drawbar-position", 8.0, 0.0, 8,
     EventType::BankDrawbar, Manual::Upper, 9},
    {4113U, "manual.upper.bank.B.drawbar.5_1/3ft", "drawbar_position",
     "drawbar-position", 8.0, 0.0, 8,
     EventType::BankDrawbar, Manual::Upper, 10},
    {4114U, "manual.upper.bank.B.drawbar.8ft", "drawbar_position",
     "drawbar-position", 8.0, 0.0, 8,
     EventType::BankDrawbar, Manual::Upper, 11},
    {4115U, "manual.upper.bank.B.drawbar.4ft", "drawbar_position",
     "drawbar-position", 8.0, 0.0, 8,
     EventType::BankDrawbar, Manual::Upper, 12},
    {4116U, "manual.upper.bank.B.drawbar.2_2/3ft", "drawbar_position",
     "drawbar-position", 8.0, 0.0, 8,
     EventType::BankDrawbar, Manual::Upper, 13},
    {4117U, "manual.upper.bank.B.drawbar.2ft", "drawbar_position",
     "drawbar-position", 8.0, 0.0, 8,
     EventType::BankDrawbar, Manual::Upper, 14},
    {4118U, "manual.upper.bank.B.drawbar.1_3/5ft", "drawbar_position",
     "drawbar-position", 8.0, 0.0, 8,
     EventType::BankDrawbar, Manual::Upper, 15},
    {4119U, "manual.upper.bank.B.drawbar.1_1/3ft", "drawbar_position",
     "drawbar-position", 8.0, 0.0, 8,
     EventType::BankDrawbar, Manual::Upper, 16},
    {4120U, "manual.upper.bank.B.drawbar.1ft", "drawbar_position",
     "drawbar-position", 8.0, 0.0, 8,
     EventType::BankDrawbar, Manual::Upper, 17},
    {4128U, "manual.lower.bank.A.drawbar.16ft", "drawbar_position",
     "drawbar-position", 8.0, 0.0, 8,
     EventType::BankDrawbar, Manual::Lower, 0},
    {4129U, "manual.lower.bank.A.drawbar.5_1/3ft", "drawbar_position",
     "drawbar-position", 8.0, 0.0, 8,
     EventType::BankDrawbar, Manual::Lower, 1},
    {4130U, "manual.lower.bank.A.drawbar.8ft", "drawbar_position",
     "drawbar-position", 8.0, 0.0, 8,
     EventType::BankDrawbar, Manual::Lower, 2},
    {4131U, "manual.lower.bank.A.drawbar.4ft", "drawbar_position",
     "drawbar-position", 8.0, 0.0, 8,
     EventType::BankDrawbar, Manual::Lower, 3},
    {4132U, "manual.lower.bank.A.drawbar.2_2/3ft", "drawbar_position",
     "drawbar-position", 8.0, 0.0, 8,
     EventType::BankDrawbar, Manual::Lower, 4},
    {4133U, "manual.lower.bank.A.drawbar.2ft", "drawbar_position",
     "drawbar-position", 8.0, 0.0, 8,
     EventType::BankDrawbar, Manual::Lower, 5},
    {4134U, "manual.lower.bank.A.drawbar.1_3/5ft", "drawbar_position",
     "drawbar-position", 8.0, 0.0, 8,
     EventType::BankDrawbar, Manual::Lower, 6},
    {4135U, "manual.lower.bank.A.drawbar.1_1/3ft", "drawbar_position",
     "drawbar-position", 8.0, 0.0, 8,
     EventType::BankDrawbar, Manual::Lower, 7},
    {4136U, "manual.lower.bank.A.drawbar.1ft", "drawbar_position",
     "drawbar-position", 8.0, 0.0, 8,
     EventType::BankDrawbar, Manual::Lower, 8},
    {4144U, "manual.lower.bank.B.drawbar.16ft", "drawbar_position",
     "drawbar-position", 8.0, 0.0, 8,
     EventType::BankDrawbar, Manual::Lower, 9},
    {4145U, "manual.lower.bank.B.drawbar.5_1/3ft", "drawbar_position",
     "drawbar-position", 8.0, 0.0, 8,
     EventType::BankDrawbar, Manual::Lower, 10},
    {4146U, "manual.lower.bank.B.drawbar.8ft", "drawbar_position",
     "drawbar-position", 8.0, 0.0, 8,
     EventType::BankDrawbar, Manual::Lower, 11},
    {4147U, "manual.lower.bank.B.drawbar.4ft", "drawbar_position",
     "drawbar-position", 8.0, 0.0, 8,
     EventType::BankDrawbar, Manual::Lower, 12},
    {4148U, "manual.lower.bank.B.drawbar.2_2/3ft", "drawbar_position",
     "drawbar-position", 8.0, 0.0, 8,
     EventType::BankDrawbar, Manual::Lower, 13},
    {4149U, "manual.lower.bank.B.drawbar.2ft", "drawbar_position",
     "drawbar-position", 8.0, 0.0, 8,
     EventType::BankDrawbar, Manual::Lower, 14},
    {4150U, "manual.lower.bank.B.drawbar.1_3/5ft", "drawbar_position",
     "drawbar-position", 8.0, 0.0, 8,
     EventType::BankDrawbar, Manual::Lower, 15},
    {4151U, "manual.lower.bank.B.drawbar.1_1/3ft", "drawbar_position",
     "drawbar-position", 8.0, 0.0, 8,
     EventType::BankDrawbar, Manual::Lower, 16},
    {4152U, "manual.lower.bank.B.drawbar.1ft", "drawbar_position",
     "drawbar-position", 8.0, 0.0, 8,
     EventType::BankDrawbar, Manual::Lower, 17},
    {8192U, "global.expression", "expression",
     "normalized-linear-gain-surrogate", 1.0, 1.0, 0,
     EventType::Expression, Manual::Upper, 0},
    {8208U, "manual.upper.selected_bank", "bank_selector",
     "bank-index-0=A-1=B", 1.0, 1.0, 1,
     EventType::SelectBank, Manual::Upper, 0},
    {8209U, "manual.lower.selected_bank", "bank_selector",
     "bank-index-0=A-1=B", 1.0, 1.0, 1,
     EventType::SelectBank, Manual::Lower, 0},
    {12288U, "percussion.enabled", "percussion_switch",
     "enabled-index-0=off-1=on", 1.0, 0.0, 1,
     EventType::Percussion, Manual::Upper, 0},
    {12289U, "percussion.harmonic", "percussion_switch",
     "harmonic-index-0=second-1=third", 1.0, 0.0, 1,
     EventType::Percussion, Manual::Upper, 1},
    {12290U, "percussion.volume", "percussion_switch",
     "volume-index-0=normal-1=soft", 1.0, 0.0, 1,
     EventType::Percussion, Manual::Upper, 2},
    {12291U, "percussion.decay", "percussion_switch",
     "decay-index-0=slow-1=fast", 1.0, 0.0, 1,
     EventType::Percussion, Manual::Upper, 3},
}};

constexpr std::array<double, 8> kDrawbarThresholds{
    0.0625, 0.1875, 0.3125, 0.4375, 0.5625, 0.6875, 0.8125, 0.9375};

[[nodiscard]] const ParameterDescriptor* find_descriptor(std::uint32_t id) noexcept {
    for (const auto& descriptor : kDescriptors) {
        if (descriptor.id == id) return &descriptor;
        if (descriptor.id > id) break;
    }
    return nullptr;
}

[[nodiscard]] double to_plain(const ParameterDescriptor& descriptor,
                               double normalized) noexcept {
    if (descriptor.step_count == 0) return normalized;
    if (descriptor.step_count == 1) return normalized >= 0.5 ? 1.0 : 0.0;
    std::size_t position = 0;
    while (position < kDrawbarThresholds.size() &&
           normalized >= kDrawbarThresholds[position]) {
        ++position;
    }
    return static_cast<double>(position);
}

} // namespace

std::span<const ParameterDescriptor, kParameterCount> parameter_descriptors() noexcept {
    return kDescriptors;
}

bool parameter_descriptor(std::uint32_t id, ParameterDescriptor& destination) noexcept {
    const auto* descriptor = find_descriptor(id);
    if (descriptor == nullptr) return false;
    destination = *descriptor;
    return true;
}

bool normalized_to_event(std::uint32_t id, double normalized,
                          std::uint32_t offset, Event& destination) noexcept {
    const auto* descriptor = find_descriptor(id);
    if (descriptor == nullptr || !std::isfinite(normalized) ||
        normalized < 0.0 || normalized > 1.0) {
        return false;
    }
    destination = Event{offset, descriptor->event_type, descriptor->manual,
                        descriptor->index, to_plain(*descriptor, normalized)};
    return true;
}

bool plain_to_normalized(std::uint32_t id, double plain, double& destination) noexcept {
    const auto* descriptor = find_descriptor(id);
    if (descriptor == nullptr || !std::isfinite(plain) || plain < 0.0 ||
        plain > descriptor->maximum ||
        (descriptor->step_count != 0 && std::trunc(plain) != plain)) {
        return false;
    }
    // Every discrete valid value divided by 8 or 1 is exactly representable;
    // expression is deliberately passed through without arithmetic.
    destination = descriptor->step_count == 0 ? plain : plain / descriptor->maximum;
    return true;
}

} // namespace hammond
