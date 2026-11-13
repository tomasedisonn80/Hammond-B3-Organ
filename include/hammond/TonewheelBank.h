#pragma once

#include "hammond/Profile.h"

#include <array>
#include <cstdint>

namespace hammond {

// ideal-shared-sine-v1: 91 normalized, unmeasured sine sources. Frequencies and
// amplitudes come only from the supplied profile; there is no tuning fallback.
// All state is value-owned. Prepare and inspect only while stopped or on the
// processing thread; this class does not provide a concurrent snapshot protocol.
class TonewheelBank {
public:
    // A successful prepare starts a new seeded source field. Failure preserves
    // all previous state. See the agent-13 note for the exact seed convention.
    [[nodiscard]] Status prepare(const RuntimeProfile& profile, double sample_rate,
                                 std::uint64_t seed) noexcept;

    // Emit each current-phase sample, then advance every source exactly once.
    // No key/control API exists: callers must process silent/disconnected frames
    // as well. An unprepared bank fills output with zeros and advances nothing.
    void process_frame(std::array<double, kToneSourceCount>& output) noexcept;

    // Reports the phase of the next sample, in [0,1) turns. Invalid IDs and an
    // unprepared bank return false without changing destination.
    [[nodiscard]] bool phase_turns(ToneId id, double& destination) const noexcept;

    [[nodiscard]] bool prepared() const noexcept { return prepared_; }

private:
    struct SourceState {
        double frequency_hz{0.0};
        double peak_amplitude{0.0};
        double phase_turns{0.0};
        double increment_turns{0.0};
        double sample{0.0};
    };

    std::array<SourceState, kToneSourceCount> sources_{};
    bool prepared_{false};
};

} // namespace hammond
