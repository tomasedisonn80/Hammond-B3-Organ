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
    // Each computed frequency/sample_rate increment must be in [2^-53, 0.5)
    // turns/sample or preparation returns InvalidProfile. The lower bound
    // guarantees phase progress, not frequency accuracy near that bound.
    // See docs/NUMERICAL_BOUNDS.md for this binary64 numerical support contract.
    [[nodiscard]] Status prepare(const RuntimeProfile& profile, double sample_rate,
                                 std::uint64_t seed) noexcept;

    // Stopped or same-processing-thread lifecycle operation; advances no time.
    // Preserve every current source phase/sample/amplitude/frequency and replace
    // only the increments after validating all 91 at the new supported rate.
    // Unprepared -> NotPrepared; unsupported rate -> InvalidSpec; any increment
    // outside [2^-53, 0.5) -> InvalidProfile. Failure preserves all state and
    // future output. The same rate is an exact no-op, not a new preparation.
    [[nodiscard]] Status reconfigure_sample_rate(double sample_rate) noexcept;

    // Emit each current-phase sample, then advance every source exactly once.
    // No key/control API exists: callers must process silent/disconnected frames
    // as well. An unprepared bank fills output with zeros and advances nothing.
    void process_frame(std::array<double, kToneSourceCount>& output) noexcept;

    // Reports the phase of the next sample, in [0,1) turns. Invalid IDs and an
    // unprepared bank return false without changing destination.
    [[nodiscard]] bool phase_turns(ToneId id, double& destination) const noexcept;

    [[nodiscard]] bool prepared() const noexcept { return prepared_; }
    // Installed samples/second, or zero before the first successful prepare.
    [[nodiscard]] double sample_rate() const noexcept { return sample_rate_; }

private:
    struct SourceState {
        double frequency_hz{0.0};
        double peak_amplitude{0.0};
        double phase_turns{0.0};
        double increment_turns{0.0};
        double sample{0.0};
    };

    std::array<SourceState, kToneSourceCount> sources_{};
    double sample_rate_{0.0};
    bool prepared_{false};
};

} // namespace hammond
