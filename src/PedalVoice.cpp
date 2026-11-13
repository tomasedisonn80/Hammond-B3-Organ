#include "hammond/PedalVoice.h"

#include <cmath>

namespace hammond {

Status render_nominal_pedal_voice(const PedalBusFrame& buses,
                                  const PedalDrawbarPositions& positions,
                                  PedalVoiceFrame& destination) noexcept {
    for (const double bus : buses) {
        if (!std::isfinite(bus) || bus < -kNominalPedalBusInputLimit ||
            bus > kNominalPedalBusInputLimit) {
            return Status::InvalidBuffer;
        }
    }
    if (!is_valid_pedal_drawbar_positions(positions)) return Status::InvalidEvent;

    PedalVoiceFrame result{};
    for (std::size_t mixture = 0; mixture < kPedalDrawbarCount; ++mixture) {
        for (std::size_t bus = 0; bus < kPedalBusCount; ++bus) {
            result.mixtures[mixture] += kNominalPedalMixtureMatrix[mixture][bus] * buses[bus];
        }
    }
    if (positions[0] != 0 || positions[1] != 0) {
        result.output = kNominalPedalPositionGains[positions[0]] * result.mixtures[0] +
                        kNominalPedalPositionGains[positions[1]] * result.mixtures[1];
    }
    destination = result;
    return Status::Ok;
}

} // namespace hammond
