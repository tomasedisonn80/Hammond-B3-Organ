#include "hammond/TonewheelBank.h"

#include <cmath>
#include <numbers>

namespace hammond {
namespace {

// SplitMix64, Sebastiano Vigna (2015), public-domain reference:
// https://prng.di.unimi.it/splitmix.c (verified 2026-11-13).
// Unsigned 64-bit arithmetic intentionally wraps modulo 2^64. No global state.
[[nodiscard]] std::uint64_t next_phase_bits(std::uint64_t& state) noexcept {
    state += std::uint64_t{0x9e3779b97f4a7c15};
    std::uint64_t mixed = state;
    mixed = (mixed ^ (mixed >> 30U)) * std::uint64_t{0xbf58476d1ce4e5b9};
    mixed = (mixed ^ (mixed >> 27U)) * std::uint64_t{0x94d049bb133111eb};
    return mixed ^ (mixed >> 31U);
}

[[nodiscard]] double wrapped_turns(double turns) noexcept {
    // Both initialization and advancement supply a finite value in [0,2).
    return turns >= 1.0 ? turns - 1.0 : turns;
}

} // namespace

Status TonewheelBank::prepare(const RuntimeProfile& profile, double sample_rate,
                              std::uint64_t seed) noexcept {
    const Status status = validate_runtime_profile(profile, sample_rate);
    if (status != Status::Ok) {
        return status;
    }

    std::array<SourceState, kToneSourceCount> candidate{};
    std::uint64_t seed_state = seed;
    for (std::size_t index = 0; index < candidate.size(); ++index) {
        const ToneSource& source = profile.sources[index];
        const double increment = source.frequency_hz / sample_rate;
        // 2^-53 is the largest binary64 spacing for stored phase in [0,1).
        // Require a full spacing so every phase can advance; a merely positive
        // increment may round away. This support floor is not an accuracy claim
        // near the floor. Also reject division that rounds onto Nyquist.
        if (!std::isfinite(increment) || increment < 0x1p-53 || increment >= 0.5) {
            return Status::InvalidProfile;
        }

        // Draw once per ascending tone ID, including seed zero. The top 53 bits
        // become an exactly representable offset in [0,1), in units of 2^-53.
        const double offset = static_cast<double>(next_phase_bits(seed_state) >> 11U)
                              * 0x1.0p-53;
        candidate[index] = SourceState{source.frequency_hz, source.peak_amplitude,
                                      wrapped_turns(source.base_phase_turns + offset),
                                      increment, 0.0};
    }

    sources_ = candidate;
    prepared_ = true;
    return Status::Ok;
}

void TonewheelBank::process_frame(std::array<double, kToneSourceCount>& output) noexcept {
    if (!prepared_) {
        output.fill(0.0);
        return;
    }

    constexpr double two_pi = 2.0 * std::numbers::pi_v<double>;
    for (std::size_t index = 0; index < sources_.size(); ++index) {
        SourceState& source = sources_[index];
        source.sample = source.peak_amplitude * std::sin(two_pi * source.phase_turns);
        output[index] = source.sample;
        source.phase_turns = wrapped_turns(source.phase_turns + source.increment_turns);
    }
}

bool TonewheelBank::phase_turns(ToneId id, double& destination) const noexcept {
    std::size_t index = 0;
    if (!prepared_ || !tone_id_to_index(id, index)) {
        return false;
    }
    destination = sources_[index].phase_turns;
    return true;
}

} // namespace hammond
