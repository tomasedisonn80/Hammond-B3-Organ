#include "hammond/PedalRouting.h"
#include "hammond/generated/PedalRoutingData.h"

#include <cmath>

namespace hammond {
namespace {

[[nodiscard]] bool normalized(double value) noexcept {
    return std::isfinite(value) && value >= -1.0 && value <= 1.0;
}

} // namespace

const PedalRouteDefinition& compiled_pedal_routes() noexcept {
    return generated::kPedalRoutes;
}

PedalRoutingIdentity compiled_pedal_identity() noexcept {
    return {kPedalBusReferenceModelId, generated::kPedalMapId,
            generated::kPedalMapRawSha256, generated::kPedalMapCanonicalSha256,
            generated::kFactoryComparisonId, generated::kFactoryComparisonRawSha256,
            generated::kPedalReviewASha256, generated::kPedalReviewBSha256};
}

Status PedalBusKernel::prepare(std::span<const PedalRoute> routes,
                               const PedalWeights& weights) noexcept {
    if (routes.size() != kPedalContactPositionCount) return Status::InvalidProfile;
    for (std::size_t position = 0; position < kPedalContactPositionCount; ++position) {
        const auto& route = routes[position];
        const auto expected_pedal = position / kPedalContactCount + 1;
        const auto expected_contact = position % kPedalContactCount;
        if (route.pedal.value != expected_pedal || route.contact != expected_contact ||
            static_cast<std::size_t>(route.bus) != expected_contact / 2 ||
            (route.tone && (*route.tone < kMinToneId || *route.tone > kMaxToneId)) ||
            !normalized(weights[position])) {
            return Status::InvalidProfile;
        }
    }

    // Nothing below validation can fail. The definition and weights are owned;
    // callers may retire or modify their authoring buffers after this returns.
    for (std::size_t position = 0; position < kPedalContactPositionCount; ++position) {
        routes_[position] = routes[position];
    }
    weights_ = weights;
    contacts_.fill(false);
    prepared_ = true;
    return Status::Ok;
}

Status PedalBusKernel::apply_contacts(std::span<const PedalContactEdit> edits) noexcept {
    if (!prepared_) return Status::NotPrepared;
    if (edits.size() > kPedalContactPositionCount) return Status::TooManyEvents;
    for (const auto& edit : edits) {
        std::size_t position = 0;
        if (!pedal_contact_to_index(edit.pedal, edit.contact, position)) {
            return Status::InvalidEvent;
        }
    }
    for (const auto& edit : edits) {
        const auto position = (static_cast<std::size_t>(edit.pedal.value) - 1) *
                              kPedalContactCount + edit.contact;
        contacts_[position] = edit.closed;
    }
    return Status::Ok;
}

Status PedalBusKernel::render_frame(const PedalSourceFrame& sources,
                                    PedalBusFrame& destination) const noexcept {
    if (!prepared_) return Status::NotPrepared;
    for (const double source : sources) {
        if (!normalized(source)) return Status::InvalidBuffer;
    }
    PedalBusFrame result{};
    for (std::size_t position = 0; position < kPedalContactPositionCount; ++position) {
        const auto& route = routes_[position];
        if (contacts_[position] && route.tone) {
            const auto source_index = static_cast<std::size_t>(*route.tone) - 1;
            result[static_cast<std::size_t>(route.bus)] += weights_[position] * sources[source_index];
        }
    }
    destination = result;
    return Status::Ok;
}

std::size_t PedalBusKernel::closed_contact_count() const noexcept {
    std::size_t count = 0;
    for (const bool closed : contacts_) {
        if (closed) ++count;
    }
    return count;
}

bool PedalBusKernel::contact_closed(PedalId pedal, std::uint32_t contact,
                                    bool& destination) const noexcept {
    std::size_t position = 0;
    if (!prepared_ || !pedal_contact_to_index(pedal, contact, position)) return false;
    destination = contacts_[position];
    return true;
}

} // namespace hammond
