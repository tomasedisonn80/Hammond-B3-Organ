#include "TestSupport.h"
#include "hammond/RotaryRenderer.h"
#include "RotaryRendererInternal.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <memory>
#include <span>
#include <vector>

namespace hammond::rotary::detail {

// Defined only in this executable. The accelerated endpoint fixture checks
// admission at a coherent stationary clock; it is not a continuous one-day run.
struct RotaryRendererTestAccess {
    struct Retained {
        std::array<WaveformHistory, kRotorCount> waveform{};
        std::array<MotionFrameHistory, kRotorCount> motion_history{};
        std::array<RotaryMotion, kRotorCount> motion{};
    };

    static bool bits(double a, double b) {
        return std::bit_cast<std::uint64_t>(a) == std::bit_cast<std::uint64_t>(b);
    }

    static bool same_motion(const MotionState& a, const MotionState& b) {
        return bits(a.phase_rad, b.phase_rad) && a.turns == b.turns
            && bits(a.speed_rad_s, b.speed_rad_s);
    }

    static bool same_segment(const MotionSegment& a, const MotionSegment& b) {
        return a.anchor_frame == b.anchor_frame && same_motion(a.initial, b.initial)
            && bits(a.target_rad_s, b.target_rad_s) && bits(a.tau_s, b.tau_s)
            && a.direction == b.direction;
    }

    static std::unique_ptr<Retained> snapshot(const RotaryRenderer& renderer) {
        if (!renderer.storage_) return {};
        auto result = std::make_unique<Retained>();
        result->waveform = renderer.storage_->waveform;
        result->motion_history = renderer.storage_->motion_history;
        result->motion = renderer.storage_->motion;
        return result;
    }

    static bool unchanged(const RotaryRenderer& renderer, const Retained* before) {
        if (before == nullptr) return !renderer.storage_;
        if (!renderer.storage_ || renderer.storage_->motion != before->motion) return false;
        for (std::size_t rotor = 0; rotor < kRotorCount; ++rotor) {
            const auto& waveform = renderer.storage_->waveform[rotor];
            const auto& old_waveform = before->waveform[rotor];
            if (!bits(waveform.sample_rate_, old_waveform.sample_rate_)
                || waveform.capacity_frames_ != old_waveform.capacity_frames_
                || waveform.next_frame_ != old_waveform.next_frame_
                || waveform.max_frame_ != old_waveform.max_frame_
                || waveform.prepared_ != old_waveform.prepared_) return false;
            for (std::size_t index = 0; index < waveform.samples_.size(); ++index) {
                if (!bits(waveform.samples_[index], old_waveform.samples_[index])) return false;
            }
            const auto& history = renderer.storage_->motion_history[rotor];
            const auto& old_history = before->motion_history[rotor];
            if (history.profile_ != old_history.profile_
                || !same_motion(history.epoch_initial_, old_history.epoch_initial_)
                || !bits(history.sample_rate_, old_history.sample_rate_)
                || history.capacity_frames_ != old_history.capacity_frames_
                || history.next_frame_ != old_history.next_frame_
                || history.max_frame_ != old_history.max_frame_
                || history.prepared_ != old_history.prepared_) return false;
            for (std::size_t index = 0; index < history.segments_.size(); ++index) {
                if (!same_segment(history.segments_[index], old_history.segments_[index])) return false;
            }
        }
        return true;
    }

    static bool coherent(const RotaryRenderer& renderer) {
        if (!renderer.storage_) return false;
        const auto& storage = *renderer.storage_;
        const auto frame = storage.motion[0].frame();
        for (std::size_t rotor = 0; rotor < kRotorCount; ++rotor) {
            if (storage.motion[rotor].frame() != frame
                || storage.waveform[rotor].next_frame_ != frame
                || storage.motion_history[rotor].next_frame_ != frame
                || storage.waveform[rotor].capacity_frames_ != storage.capacity_frames
                || storage.motion_history[rotor].capacity_frames_ != storage.capacity_frames
                || storage.waveform[rotor].sample_rate_ != storage.spec.sample_rate
                || storage.motion_history[rotor].sample_rate_ != storage.spec.sample_rate) return false;
        }
        return true;
    }

    static void stationary_silent_endpoint(RotaryRenderer& renderer) {
        CHECK(coherent(renderer));
        auto& storage = *renderer.storage_;
        CHECK(storage.motion[0].frame() >= storage.capacity_frames);
        const auto maximum = storage.motion[0].max_frame();
        for (std::size_t rotor = 0; rotor < kRotorCount; ++rotor) {
            auto& owner = storage.motion[rotor];
            CHECK(owner.profile().slow_rad_s == 0.0 && owner.profile().fast_rad_s == 0.0);
            CHECK(owner.state().speed_rad_s == 0.0 && owner.segment().anchor_frame == 0);
            for (std::size_t slot = 0; slot < storage.capacity_frames; ++slot) {
                CHECK(storage.waveform[rotor].samples_[slot] == 0.0);
                CHECK(same_segment(storage.motion_history[rotor].segments_[slot], owner.segment()));
            }
            CHECK(owner.advance_to(maximum) == Status::Ok);
            storage.waveform[rotor].next_frame_ = maximum;
            storage.motion_history[rotor].next_frame_ = maximum;
        }
        CHECK(coherent(renderer));
    }
};

} // namespace hammond::rotary::detail

namespace {

using namespace hammond::rotary;
using Access = detail::RotaryRendererTestAccess;
constexpr double kRate = 48000.0;
std::size_t rejected_process_calls = 0;
std::size_t rejected_lifecycle_calls = 0;
std::size_t analytical_samples = 0;
std::size_t analytical_fixtures = 0;
std::size_t accepted_events = 0;
long double maximum_analytical_error = 0.0L;
long double analytical_squared_error = 0.0L;
std::array<std::size_t, 3> worst_analytical_coordinate{};

bool same_state(const RendererState& a, const RendererState& b) {
    if (a.prepared != b.prepared || !Access::bits(a.sample_rate, b.sample_rate)
        || a.frame != b.frame || a.max_frame != b.max_frame || a.commands != b.commands) return false;
    for (std::size_t rotor = 0; rotor < kRotorCount; ++rotor) {
        if (!Access::same_motion(a.motion[rotor], b.motion[rotor])
            || !Access::same_motion(a.epoch_initial[rotor], b.epoch_initial[rotor])
            || !Access::same_segment(a.segments[rotor], b.segments[rotor])) return false;
    }
    return true;
}

bool same_position(SamplePosition a, SamplePosition b) {
    return a.frame == b.frame && Access::bits(a.fraction, b.fraction);
}

bool same_path(const PathResult& a, const PathResult& b) {
    return Access::bits(a.delay_s, b.delay_s) && Access::bits(a.distance_m, b.distance_m)
        && Access::bits(a.emission_phase_rad, b.emission_phase_rad)
        && Access::bits(a.radial_speed_m_s, b.radial_speed_m_s)
        && Access::bits(a.frequency_ratio, b.frequency_ratio)
        && Access::bits(a.distance_gain, b.distance_gain)
        && Access::bits(a.residual_s, b.residual_s) && a.iterations == b.iterations;
}

bool same_diagnostics(const RendererDiagnostics& a, const RendererDiagnostics& b) {
    if (a.has_rendered_sample != b.has_rendered_sample || a.last_input_frame != b.last_input_frame
        || !same_position(a.last_observation, b.last_observation)
        || !Access::bits(a.max_solver_residual_s, b.max_solver_residual_s)
        || a.max_solver_iterations != b.max_solver_iterations) return false;
    for (std::size_t path = 0; path < kPathCount; ++path) {
        if (!same_path(a.last_paths[path], b.last_paths[path])
            || !same_position(a.last_emissions[path], b.last_emissions[path])) return false;
    }
    return true;
}

void same_audio(std::span<const double> a, std::span<const double> b) {
    CHECK(a.size() == b.size());
    for (std::size_t index = 0; index < a.size(); ++index) CHECK(Access::bits(a[index], b[index]));
}

struct Snapshot {
    RendererState state{};
    RendererDiagnostics diagnostics{};
    Profile profile{};
    ProcessSpec spec{0.0, 0};
    std::array<PathBounds, kPathCount> bounds{};
    std::size_t capacity{0};
    std::uint32_t flush{0};
    std::unique_ptr<Access::Retained> retained{};

    explicit Snapshot(const RotaryRenderer& renderer)
        : state(renderer.state()), diagnostics(renderer.diagnostics()), profile(renderer.profile()),
          spec(renderer.spec()), bounds(renderer.path_bounds()), capacity(renderer.history_capacity_frames()),
          flush(renderer.tail_flush_frames()), retained(Access::snapshot(renderer)) {}

    void check(const RotaryRenderer& renderer) const {
        CHECK(same_state(renderer.state(), state));
        CHECK(same_diagnostics(renderer.diagnostics(), diagnostics));
        CHECK(renderer.profile() == profile && renderer.spec() == spec && renderer.path_bounds() == bounds);
        CHECK(renderer.history_capacity_frames() == capacity && renderer.tail_flush_frames() == flush);
        CHECK(Access::unchanged(renderer, retained.get()));
    }
};

template <typename Call>
void reject_process(RotaryRenderer& renderer, Status expected, Call call,
                    std::span<const double> watched = {}) {
    const Snapshot before(renderer);
    const std::vector<double> original(watched.begin(), watched.end());
    const auto result = call();
    CHECK(result.status == expected);
    CHECK(result.events_consumed == 0);
    CHECK(result.max_solver_residual_s == 0.0 && result.max_solver_iterations == 0);
    before.check(renderer);
    same_audio(watched, original);
    ++rejected_process_calls;
}

template <typename Call>
void reject_lifecycle(RotaryRenderer& renderer, Status expected, Call call) {
    const Snapshot before(renderer);
    CHECK(call() == expected);
    before.check(renderer);
    ++rejected_lifecycle_calls;
}

Profile stationary_profile(bool fractional = false) {
    Profile profile;
    profile.sound_speed_m_s = 375.0;
    profile.reference_distance_m = 0.5;
    for (std::size_t rotor = 0; rotor < kRotorCount; ++rotor) {
        profile.rotors[rotor].motion = {0.0, 0.0, 0.01, 0.03, rotor == 0 ? std::int8_t{1} : std::int8_t{-1}};
        profile.rotors[rotor].initial_phase_rad = 0.25 + static_cast<double>(rotor);
    }
    profile.rotors[1].origin_m.x = 0.125;
    const double shift = fractional ? 0.00390625 : 0.0;
    profile.microphones[0].position_m = {0.25 + shift, 0.0, 0.0};
    profile.microphones[1].position_m = {0.375 + shift, 0.0, 0.0};
    return profile;
}

Profile moving_profile() {
    auto profile = stationary_profile();
    profile.sound_speed_m_s = 343.0;
    profile.rotors[0].motion = {4.0, 90.0, 0.007, 0.013, 1};
    profile.rotors[1].motion = {3.0, 75.0, 0.011, 0.019, -1};
    profile.rotors[0].radius_m = 0.04;
    profile.rotors[1].radius_m = 0.03;
    profile.rotors[0].initial_phase_rad = 6.2;
    profile.rotors[1].initial_phase_rad = 0.025;
    profile.rotors[0].initial_speed_rad_s = 45.0;
    profile.rotors[1].initial_speed_rad_s = 55.0;
    return profile;
}

std::vector<double> signal(std::size_t frames, std::uint32_t multiplier, std::uint32_t offset) {
    std::vector<double> result(frames);
    for (std::size_t index = 0; index < frames; ++index) {
        const auto code = (static_cast<std::uint32_t>(index) * multiplier + offset) % 257U;
        result[index] = static_cast<double>(static_cast<int>(code) - 128) / 256.0;
    }
    return result;
}

ProcessResult accept(RotaryRenderer& renderer, std::span<const double> horn,
                     std::span<const double> drum, std::span<double> left, std::span<double> right,
                     std::span<const CommandEvent> events = {}) {
    const auto result = renderer.process(horn, drum, left, right, events);
    CHECK(result.status == Status::Ok);
    CHECK(result.events_consumed == events.size());
    CHECK(result.max_solver_residual_s <= kMaxSolverResidualSeconds);
    CHECK(result.max_solver_iterations <= kMaxSolverIterations);
    CHECK(Access::coherent(renderer));
    if (horn.empty()) CHECK(result.max_solver_residual_s == 0.0 && result.max_solver_iterations == 0);
    else CHECK(result.max_solver_iterations >= 2);
    accepted_events += result.events_consumed;
    return result;
}

// This stationary oracle uses direct long-double Cartesian geometry and a
// generic product-form interpolation; it calls no native path/history kernel.
long double stationary_distance(const Profile& profile, std::size_t rotor, std::size_t channel) {
    const auto& source = profile.rotors[rotor];
    const auto& microphone = profile.microphones[channel].position_m;
    const long double phase = source.initial_phase_rad;
    const long double x = static_cast<long double>(source.origin_m.x)
        + static_cast<long double>(source.radius_m) * std::cos(phase);
    const long double y = static_cast<long double>(source.origin_m.y)
        + static_cast<long double>(source.radius_m) * std::sin(phase);
    const long double dx = static_cast<long double>(microphone.x) - x;
    const long double dy = static_cast<long double>(microphone.y) - y;
    const long double dz = static_cast<long double>(microphone.z) - source.origin_m.z;
    return std::sqrt(dx * dx + dy * dy + dz * dz);
}

long double independent_cubic(std::span<const double> input, long double position) {
    const auto floor = static_cast<std::int64_t>(std::floor(position));
    const long double fraction = position - static_cast<long double>(floor);
    long double result = 0.0L;
    for (std::int64_t node = -1; node <= 2; ++node) {
        long double weight = 1.0L;
        for (std::int64_t other = -1; other <= 2; ++other) {
            if (node != other) weight *= (fraction - static_cast<long double>(other))
                / static_cast<long double>(node - other);
        }
        const auto frame = floor + node;
        CHECK(frame < 0 || static_cast<std::uint64_t>(frame) < input.size());
        const long double sample = frame < 0 ? 0.0L : input[static_cast<std::size_t>(frame)];
        result += weight * sample;
    }
    return result;
}

void check_stationary(const Profile& profile, std::span<const double> horn,
                      std::span<const double> drum, std::span<const double> left,
                      std::span<const double> right) {
    ++analytical_fixtures;
    const std::array<std::span<const double>, kRotorCount> inputs{horn, drum};
    const std::array<std::span<const double>, kMicrophoneCount> outputs{left, right};
    for (std::size_t channel = 0; channel < kMicrophoneCount; ++channel) {
        std::array<long double, kRotorCount> distances{};
        long double gain_sum = 0.0L;
        for (std::size_t rotor = 0; rotor < kRotorCount; ++rotor) {
            distances[rotor] = stationary_distance(profile, rotor, channel);
            gain_sum += static_cast<long double>(profile.reference_distance_m) / distances[rotor];
        }
        for (std::size_t frame = 0; frame < horn.size(); ++frame) {
            long double expected = 0.0L;
            for (std::size_t rotor = 0; rotor < kRotorCount; ++rotor) {
                const long double position = static_cast<long double>(frame) - 2.0L
                    - static_cast<long double>(kRate) * distances[rotor] / profile.sound_speed_m_s;
                expected += independent_cubic(inputs[rotor], position)
                    * static_cast<long double>(profile.reference_distance_m) / distances[rotor];
            }
            const long double error = std::abs(static_cast<long double>(outputs[channel][frame]) - expected);
            if (error > maximum_analytical_error) {
                maximum_analytical_error = error;
                worst_analytical_coordinate = {analytical_fixtures, channel, frame};
            }
            analytical_squared_error += error * error;
            ++analytical_samples;
            CHECK_NEAR(outputs[channel][frame], expected, 5.0e-9L * gain_sum);
        }
    }
}

void defaults_and_preparation() {
    RotaryRenderer renderer;
    CHECK(!renderer.prepared());
    CHECK(renderer.profile() == Profile{});
    CHECK((renderer.spec() == ProcessSpec{0.0, 0}));
    CHECK(same_state(renderer.state(), RendererState{}));
    CHECK(same_diagnostics(renderer.diagnostics(), RendererDiagnostics{}));
    CHECK((renderer.path_bounds() == std::array<PathBounds, kPathCount>{}));
    CHECK(renderer.history_capacity_frames() == 0 && renderer.tail_flush_frames() == 0);
    CHECK(RotaryRenderer::algorithmic_latency_frames() == 2);
    reject_process(renderer, Status::NotPrepared, [&] { return renderer.process({}, {}, {}, {}); });
    reject_lifecycle(renderer, Status::NotPrepared, [&] { return renderer.reset(); });
    reject_lifecycle(renderer, Status::NotPrepared, [&] { return renderer.reconfigure_sample_rate(1.0); });

    const auto profile = stationary_profile();
    const double infinity = std::numeric_limits<double>::infinity();
    const double nan = std::numeric_limits<double>::quiet_NaN();
    for (double rate : {0.0, 48001.0, std::nextafter(kRate, infinity), infinity, nan}) {
        reject_lifecycle(renderer, Status::InvalidSpec, [&] { return renderer.prepare(profile, {rate, 64}); });
    }
    for (std::uint32_t block : {0U, kMaxBlockFrames + 1U}) {
        reject_lifecycle(renderer, Status::InvalidSpec, [&] { return renderer.prepare(profile, {kRate, block}); });
    }
    CHECK(renderer.prepare(profile, {kRate, kMaxBlockFrames}) == Status::Ok);
    CHECK(renderer.history_capacity_frames() == 54 && renderer.tail_flush_frames() == 52);
    auto copied_profile = renderer.profile();
    copied_profile.sound_speed_m_s = 1.0;
    auto copied_state = renderer.state();
    copied_state.motion[0].phase_rad = 1.0;
    CHECK(renderer.profile() == profile && renderer.state().motion[0].phase_rad == profile.rotors[0].initial_phase_rad);
    CHECK(copied_profile != renderer.profile() && !same_state(copied_state, renderer.state()));

    std::vector<Profile> invalid;
    auto add = [&](auto mutation) { auto value = profile; mutation(value); invalid.push_back(value); };
    for (std::size_t rotor = 0; rotor < kRotorCount; ++rotor) {
        add([&](auto& value) { value.rotors[rotor].initial_command = static_cast<SpeedCommand>(7); });
        add([&](auto& value) { value.rotors[rotor].initial_phase_rad = kTwoPi; });
        add([&](auto& value) { value.rotors[rotor].initial_speed_rad_s = -1.0; });
        add([&](auto& value) { value.rotors[rotor].motion.direction = 0; });
        add([&](auto& value) { value.rotors[rotor].motion.tau_up_s = 0.0; });
        add([&](auto& value) { value.rotors[rotor].radius_m = 1.01; });
        add([&](auto& value) { value.rotors[rotor].origin_m.z = nan; });
    }
    for (std::size_t channel = 0; channel < kMicrophoneCount; ++channel) {
        add([&](auto& value) { value.microphones[channel].position_m.y = infinity; });
        add([&](auto& value) { value.microphones[channel].position_m.x = 10.01; });
    }
    add([](auto& value) { value.sound_speed_m_s = 299.0; });
    add([](auto& value) { value.reference_distance_m = 10.01; });
    add([](auto& value) {
        value.rotors[0].radius_m = 0.125;
        value.rotors[0].initial_phase_rad = kTwoPi / 2.0;
        value.microphones[0].position_m = {0.125, 0.0, 0.0};
    }); // Initial pose clears the mic; another point on the full orbit collides.
    add([](auto& value) {
        value.rotors[1].origin_m = {-10.0, -10.0, 0.0};
        value.microphones[1].position_m = {10.0, 10.0, 0.0};
    });
    for (const auto& value : invalid) {
        reject_lifecycle(renderer, Status::InvalidProfile, [&] { return renderer.prepare(value, {kRate, 64}); });
    }
    auto bad_seed = profile;
    bad_seed.rotors[0].initial_command = static_cast<SpeedCommand>(5);
    reject_lifecycle(renderer, Status::InvalidSpec, [&] { return renderer.prepare(bad_seed, {1.0, 64}); });

    auto maximum = profile;
    maximum.sound_speed_m_s = 300.0;
    for (auto& source : maximum.rotors) source.origin_m = {-10.0, 0.0, 0.0};
    for (auto& mic : maximum.microphones) mic.position_m = {10.0, 0.0, 0.0};
    CHECK(renderer.prepare(maximum, {192000.0, kMaxBlockFrames}) == Status::Ok);
    CHECK(renderer.history_capacity_frames() == 12806 && renderer.tail_flush_frames() == 12804);
    for (const auto& bounds : renderer.path_bounds()) CHECK(bounds.min_distance_m == 20.0 && bounds.max_distance_m == 20.0);

    auto mach = profile;
    mach.sound_speed_m_s = 300.0;
    for (auto& source : mach.rotors) {
        source.origin_m = {};
        source.radius_m = 1.0;
        source.initial_speed_rad_s = 75.0; // Original seed exceeds both target speeds.
        source.motion.slow_rad_s = 2.0;
        source.motion.fast_rad_s = 20.0;
    }
    for (auto& mic : mach.microphones) mic.position_m = {2.0, 0.0, 0.0};
    CHECK(renderer.prepare(mach, {kRate, 64}) == Status::Ok);
    for (const auto& bounds : renderer.path_bounds()) {
        CHECK(bounds.min_distance_m == 1.0 && bounds.max_distance_m == 3.0 && bounds.max_tangential_mach == 0.25);
    }
    mach.rotors[1].initial_speed_rad_s = std::nextafter(75.0, infinity);
    reject_lifecycle(renderer, Status::InvalidProfile, [&] { return renderer.prepare(mach, {kRate, 64}); });
}

void stationary_waveform_and_signed_inputs() {
    constexpr std::size_t frames = 4096;
    const auto horn = signal(frames, 37, 0);
    const auto drum = signal(frames, 71, 19);
    std::vector<double> zero(frames, 0.0);
    std::vector<double> left(frames, -99.0), right(frames, -98.0);
    for (bool fractional : {false, true}) {
        const auto profile = stationary_profile(fractional);
        RotaryRenderer renderer;
        CHECK(renderer.prepare(profile, {kRate, kMaxBlockFrames}) == Status::Ok);
        CHECK(frames > 2 * renderer.history_capacity_frames());
        accept(renderer, horn, zero, left, right);
        check_stationary(profile, horn, zero, left, right);
        CHECK(renderer.reset() == Status::Ok);
        accept(renderer, zero, drum, left, right);
        check_stationary(profile, zero, drum, left, right);
        CHECK(renderer.reset() == Status::Ok);
        const auto result = accept(renderer, horn, drum, left, right);
        check_stationary(profile, horn, drum, left, right);
        const auto diagnostics = renderer.diagnostics();
        CHECK(diagnostics.last_input_frame == frames - 1);
        CHECK((diagnostics.last_observation == SamplePosition{static_cast<std::int64_t>(frames) - 3, 0.0}));
        CHECK(diagnostics.max_solver_residual_s == result.max_solver_residual_s);
        CHECK(diagnostics.max_solver_iterations == result.max_solver_iterations);
        for (std::size_t path = 0; path < kPathCount; ++path) {
            const auto distance = stationary_distance(profile, path / kMicrophoneCount, path % kMicrophoneCount);
            const auto& actual = diagnostics.last_paths[path];
            CHECK_NEAR(actual.delay_s, distance / profile.sound_speed_m_s, 1.0e-14L);
            CHECK_NEAR(actual.distance_m, distance, 2.0e-15L);
            CHECK_NEAR(actual.distance_gain, static_cast<long double>(profile.reference_distance_m) / distance, 2.0e-14L);
            CHECK(actual.radial_speed_m_s == 0.0 && actual.frequency_ratio == 1.0);
        }
    }

    // Freeze nonzero-radius sources at distinct phases: the point position,
    // receiver distances and gains still have to remain time invariant.
    auto frozen = stationary_profile();
    frozen.rotors[0].radius_m = 0.04;
    frozen.rotors[1].radius_m = 0.03;
    frozen.microphones[1].position_m = {-0.375, 0.125, 0.25};
    RotaryRenderer frozen_renderer;
    CHECK(frozen_renderer.prepare(frozen, {kRate, kMaxBlockFrames}) == Status::Ok);
    accept(frozen_renderer, horn, drum, left, right);
    check_stationary(frozen, horn, drum, left, right);

    auto coincident = stationary_profile(true);
    coincident.rotors[1] = coincident.rotors[0];
    const auto negative_horn = [&] { auto value = horn; for (auto& sample : value) sample = -sample; return value; }();
    RotaryRenderer cancellation;
    CHECK(cancellation.prepare(coincident, {kRate, kMaxBlockFrames}) == Status::Ok);
    accept(cancellation, horn, negative_horn, left, right);
    for (std::size_t frame = 0; frame < frames; ++frame) CHECK(left[frame] == 0.0 && right[frame] == 0.0);

    auto loud = coincident;
    loud.reference_distance_m = 10.0;
    for (auto& microphone : loud.microphones) microphone.position_m = {0.02734375, 0.0, 0.0};
    RotaryRenderer unclamped;
    CHECK(unclamped.prepare(loud, {kRate, 16}) == Status::Ok);
    std::array<double, 16> shape{}, loud_left{}, loud_right{};
    shape[0] = -1.0;
    shape[1] = 1.0;
    shape[2] = 1.0;
    shape[3] = -1.0;
    accept(unclamped, shape, shape, loud_left, loud_right);
    check_stationary(loud, shape, shape, loud_left, loud_right);
    CHECK(loud_left[7] > 900.0); // Cubic overshoot and signed pressure sum are not clipped.
    same_audio(loud_left, loud_right);

    RotaryRenderer impulses;
    const auto impulse_profile = stationary_profile();
    CHECK(impulses.prepare(impulse_profile, {kRate, 96}) == Status::Ok);
    std::array<double, 96> horn_impulse{}, drum_impulse{}, impulse_left{}, impulse_right{};
    horn_impulse[0] = 1.0;
    drum_impulse[7] = -0.5;
    accept(impulses, horn_impulse, drum_impulse, impulse_left, impulse_right);
    check_stationary(impulse_profile, horn_impulse, drum_impulse, impulse_left, impulse_right);
    CHECK_NEAR(impulse_left[34], 2.0, 2.0e-10);
    CHECK_NEAR(impulse_left[25], -2.0, 2.0e-10);
    CHECK_NEAR(impulse_right[50], 4.0 / 3.0, 2.0e-10);
    CHECK_NEAR(impulse_right[41], -1.0, 2.0e-10);
}

void event_boundaries_and_zero_calls() {
    const auto profile = moving_profile();
    RotaryRenderer split, joined;
    CHECK(split.prepare(profile, {kRate, 128}) == Status::Ok);
    CHECK(joined.prepare(profile, {kRate, 128}) == Status::Ok);
    const auto horn = signal(128, 37, 0), drum = signal(128, 71, 19);
    std::array<double, 128> split_left{}, split_right{}, joined_left{}, joined_right{};
    const std::array<CommandEvent, 4> first{{{19, RotorId::Horn, SpeedCommand::Tremolo},
        {19, RotorId::Horn, SpeedCommand::Chorale}, {64, RotorId::Horn, SpeedCommand::Tremolo},
        {64, RotorId::Drum, SpeedCommand::Tremolo}}};
    accept(split, std::span(horn).first(64), std::span(drum).first(64),
           std::span(split_left).first(64), std::span(split_right).first(64), first);
    const auto boundary = split.state();
    CHECK(boundary.frame == 64 && boundary.commands[0] == SpeedCommand::Tremolo
          && boundary.commands[1] == SpeedCommand::Tremolo);
    CHECK(boundary.segments[0].anchor_frame == 64 && boundary.segments[1].anchor_frame == 64);
    const auto before_zero_diagnostics = split.diagnostics();
    const std::array<CommandEvent, 2> zero{{{0, RotorId::Horn, SpeedCommand::Chorale},
                                          {0, RotorId::Drum, SpeedCommand::Chorale}}};
    accept(split, {}, {}, {}, {}, zero);
    CHECK(split.state().frame == 64);
    CHECK(split.state().commands[0] == SpeedCommand::Chorale && split.state().commands[1] == SpeedCommand::Chorale);
    for (std::size_t rotor = 0; rotor < kRotorCount; ++rotor) {
        CHECK(Access::same_motion(split.state().motion[rotor], boundary.motion[rotor]));
        CHECK(split.state().segments[rotor].anchor_frame == 64);
    }
    CHECK(same_diagnostics(split.diagnostics(), before_zero_diagnostics));
    const Snapshot before_empty(split);
    accept(split, {}, {}, {}, {});
    before_empty.check(split);
    const std::array<CommandEvent, 1> next_zero{{{0, RotorId::Horn, SpeedCommand::Tremolo}}};
    accept(split, std::span(horn).subspan(64), std::span(drum).subspan(64),
           std::span(split_left).subspan(64), std::span(split_right).subspan(64), next_zero);
    const std::array<CommandEvent, 7> all{{{19, RotorId::Horn, SpeedCommand::Tremolo},
        {19, RotorId::Horn, SpeedCommand::Chorale}, {64, RotorId::Horn, SpeedCommand::Tremolo},
        {64, RotorId::Drum, SpeedCommand::Tremolo}, {64, RotorId::Horn, SpeedCommand::Chorale},
        {64, RotorId::Drum, SpeedCommand::Chorale}, {64, RotorId::Horn, SpeedCommand::Tremolo}}};
    accept(joined, horn, drum, joined_left, joined_right, all);
    same_audio(split_left, joined_left);
    same_audio(split_right, joined_right);
    CHECK(same_state(split.state(), joined.state()));
    CHECK(same_diagnostics(split.diagnostics(), joined.diagnostics()));

    // An unchanged command counts as an event but retains the old anchor.
    const auto before_unchanged = split.state();
    const auto unchanged_diagnostics = split.diagnostics();
    const std::array<CommandEvent, 3> unchanged{{{0, RotorId::Horn, SpeedCommand::Tremolo},
        {0, RotorId::Horn, SpeedCommand::Tremolo}, {0, RotorId::Drum, SpeedCommand::Chorale}}};
    accept(split, {}, {}, {}, {}, unchanged);
    CHECK(same_state(split.state(), before_unchanged));
    CHECK(same_diagnostics(split.diagnostics(), unchanged_diagnostics));

    // More than the R3 fixture's lifetime event cap is legal in this owner.
    std::array<CommandEvent, kMaxEventsPerBlock> repeated{};
    for (std::size_t index = 0; index < repeated.size(); ++index) {
        repeated[index] = {0, RotorId::Drum, index % 2 == 0 ? SpeedCommand::Tremolo : SpeedCommand::Chorale};
    }
    for (std::size_t batch = 0; batch < 5; ++batch) accept(split, {}, {}, {}, {}, repeated);
    CHECK(split.state().frame == before_unchanged.frame);
    CHECK(split.state().segments[1].anchor_frame == before_unchanged.frame);
    CHECK(split.state().commands[1] == SpeedCommand::Chorale);
    CHECK(Access::same_motion(split.state().motion[1], before_unchanged.motion[1]));
    CHECK(same_diagnostics(split.diagnostics(), unchanged_diagnostics));
    std::array<double, 16> zeros{}, tail_left{}, tail_right{};
    accept(split, zeros, zeros, tail_left, tail_right);
}

void rejection_order_and_aliases() {
    const auto profile = moving_profile();
    RotaryRenderer renderer, control;
    CHECK(renderer.prepare(profile, {kRate, 64}) == Status::Ok);
    CHECK(control.prepare(profile, {kRate, 64}) == Status::Ok);
    auto horn = signal(65, 37, 0), drum = signal(65, 71, 19);
    std::vector<double> outputs(130, -0.0), control_outputs(128, -0.0);
    const auto h = std::span<const double>(horn).first(64), d = std::span<const double>(drum).first(64);
    const auto left = std::span(outputs).first(64), right = std::span(outputs).subspan(64, 64);
    accept(renderer, h, d, left, right);
    accept(control, h, d, std::span(control_outputs).first(64), std::span(control_outputs).subspan(64));
    std::fill(outputs.begin(), outputs.end(), -0.0);
    std::vector<CommandEvent> too_many(kMaxEventsPerBlock + 1, {0, static_cast<RotorId>(9), SpeedCommand::Chorale});
    const std::array<CommandEvent, 1> invalid_rotor{{{0, static_cast<RotorId>(9), SpeedCommand::Chorale}}};
    reject_process(renderer, Status::BlockTooLarge, [&] {
        return renderer.process(horn, {}, left, right, too_many);
    }, outputs);
    reject_process(renderer, Status::TooManyEvents, [&] { return renderer.process(h, {}, left, right, too_many); }, outputs);
    reject_process(renderer, Status::InvalidBuffer, [&] { return renderer.process(h, {}, left, right, invalid_rotor); }, outputs);
    reject_process(renderer, Status::InvalidBuffer, [&] { return renderer.process(h, d, left.first(63), right, invalid_rotor); }, outputs);
    reject_process(renderer, Status::InvalidBuffer, [&] { return renderer.process(h, d, left, right.first(63), invalid_rotor); }, outputs);
    reject_process(renderer, Status::InvalidBuffer, [&] { return renderer.process(h, d, left, left, invalid_rotor); }, outputs);
    reject_process(renderer, Status::InvalidBuffer, [&] { return renderer.process(h, d, left, std::span(outputs).subspan(1, 64)); }, outputs);
    reject_process(renderer, Status::InvalidBuffer, [&] { return renderer.process(h, d, std::span(horn).first(64), right); }, horn);
    reject_process(renderer, Status::InvalidBuffer, [&] { return renderer.process(h, d, left, std::span(drum).subspan(1, 64)); }, drum);
    reject_process(renderer, Status::InvalidBuffer, [&] { return renderer.process(h, d, std::span(drum).first(64), right); }, drum);
    reject_process(renderer, Status::InvalidBuffer, [&] { return renderer.process(h, d, left, std::span(horn).subspan(1, 64)); }, horn);

    const std::array<CommandEvent, 1> invalid_command{{{0, RotorId::Horn, static_cast<SpeedCommand>(8)}}};
    const std::array<CommandEvent, 1> beyond{{{65, RotorId::Horn, SpeedCommand::Chorale}}};
    const std::array<CommandEvent, 2> descending{{{17, RotorId::Horn, SpeedCommand::Tremolo},
                                               {16, RotorId::Drum, SpeedCommand::Tremolo}}};
    const auto old_horn = horn[0];
    horn[0] = std::numeric_limits<double>::quiet_NaN();
    for (std::span<const CommandEvent> events : {std::span<const CommandEvent>(invalid_rotor),
             std::span<const CommandEvent>(invalid_command), std::span<const CommandEvent>(beyond),
             std::span<const CommandEvent>(descending)}) {
        reject_process(renderer, Status::InvalidEvent, [&] { return renderer.process(h, d, left, right, events); }, outputs);
    }
    horn[0] = old_horn;
    const double infinity = std::numeric_limits<double>::infinity();
    for (auto* input : {&horn, &drum}) {
        const auto saved = (*input)[63];
        for (double bad : {std::nextafter(1.0, infinity), std::nextafter(-1.0, -infinity),
                           infinity, -infinity, std::numeric_limits<double>::quiet_NaN()}) {
            (*input)[63] = bad;
            reject_process(renderer, Status::InvalidBuffer, [&] { return renderer.process(h, d, left, right); }, outputs);
        }
        (*input)[63] = saved;
    }
    // Restore deterministic original inputs, then qualify actual continuation.
    horn = signal(65, 37, 0);
    drum = signal(65, 71, 19);
    accept(renderer, std::span(horn).first(64), std::span(drum).first(64), left, right);
    accept(control, std::span(horn).first(64), std::span(drum).first(64),
           std::span(control_outputs).first(64), std::span(control_outputs).subspan(64));
    same_audio(std::span(outputs).first(128), control_outputs);
    CHECK(same_state(renderer.state(), control.state()));
    CHECK(same_diagnostics(renderer.diagnostics(), control.diagnostics()));

    // Inputs can overlap completely or partially; adjacent outputs are legal.
    for (std::size_t input_offset : {std::size_t{0}, std::size_t{1}}) {
        RotaryRenderer aliased, independent;
        CHECK(aliased.prepare(profile, {kRate, 64}) == Status::Ok);
        CHECK(independent.prepare(profile, {kRate, 64}) == Status::Ok);
        const auto storage = signal(65, 41, 7);
        const auto input_a = std::span(storage).first(64);
        const auto input_b = std::span(storage).subspan(input_offset, 64);
        const std::vector<double> separate_a(input_a.begin(), input_a.end()), separate_b(input_b.begin(), input_b.end());
        std::array<double, 128> a{}, b{};
        accept(aliased, input_a, input_b, std::span(a).first(64), std::span(a).subspan(64));
        accept(independent, separate_a, separate_b, std::span(b).first(64), std::span(b).subspan(64));
        same_audio(a, b);
        CHECK(same_state(aliased.state(), independent.state()));
    }
}

void accelerated_epoch_boundary_precedence() {
    RotaryRenderer renderer;
    CHECK(renderer.prepare(stationary_profile(), {kRate, 64}) == Status::Ok);
    std::array<double, 65> zero{}, outputs_left{}, outputs_right{};
    accept(renderer, std::span(zero).first(64), std::span(zero).first(64),
           std::span(outputs_left).first(64), std::span(outputs_right).first(64));
    Access::stationary_silent_endpoint(renderer);
    const auto maximum = renderer.state().max_frame;
    const std::array<CommandEvent, 1> invalid{{{0, static_cast<RotorId>(9), SpeedCommand::Chorale}}};
    const std::vector<CommandEvent> too_many(kMaxEventsPerBlock + 1);
    zero[0] = std::numeric_limits<double>::quiet_NaN();
    reject_process(renderer, Status::BlockTooLarge, [&] { return renderer.process(zero, zero, outputs_left, outputs_right, too_many); }, outputs_left);
    reject_process(renderer, Status::TooManyEvents, [&] {
        return renderer.process(std::span(zero).first(1), {}, {}, {}, too_many);
    }, outputs_left);
    reject_process(renderer, Status::InvalidBuffer, [&] {
        return renderer.process(std::span(zero).first(1), {}, {}, {}, invalid);
    }, outputs_left);
    reject_process(renderer, Status::TimelineOverflow, [&] {
        return renderer.process(std::span(zero).first(1), std::span(zero).first(1),
            std::span(outputs_left).first(1), std::span(outputs_right).first(1), invalid);
    }, outputs_left);
    reject_process(renderer, Status::InvalidEvent, [&] { return renderer.process({}, {}, {}, {}, invalid); });
    const std::array<CommandEvent, 2> end_commands{{{0, RotorId::Horn, SpeedCommand::Tremolo},
                                                 {0, RotorId::Drum, SpeedCommand::Tremolo}}};
    const auto diagnostics = renderer.diagnostics();
    accept(renderer, {}, {}, {}, {}, end_commands);
    CHECK(renderer.state().frame == maximum && renderer.state().segments[0].anchor_frame == maximum);
    CHECK(same_diagnostics(renderer.diagnostics(), diagnostics));
    zero[0] = 0.0;
    CHECK(renderer.reset() == Status::Ok);
    accept(renderer, std::span(zero).first(64), std::span(zero).first(64),
           std::span(outputs_left).first(64), std::span(outputs_right).first(64));
    CHECK(renderer.state().frame == 64);
}

void lifecycle_reset_reconfigure_and_explicit_tail() {
    const auto profile = moving_profile();
    RotaryRenderer renderer, fresh;
    CHECK(renderer.prepare(profile, {kRate, kMaxBlockFrames}) == Status::Ok);
    CHECK(fresh.prepare(profile, {kRate, kMaxBlockFrames}) == Status::Ok);
    const auto horn = signal(4096, 37, 0), drum = signal(4096, 71, 19);
    std::vector<double> left(4096), right(4096), fresh_left(4096), fresh_right(4096);
    const std::array<CommandEvent, 2> commands{{{97, RotorId::Horn, SpeedCommand::Tremolo},
                                              {113, RotorId::Drum, SpeedCommand::Tremolo}}};
    accept(renderer, horn, drum, left, right, commands);
    CHECK(renderer.state().motion[0].turns != 0 && renderer.state().motion[1].turns != 0);
    const auto prepared_bounds = renderer.path_bounds();
    const auto capacity = renderer.history_capacity_frames();
    const auto flush = renderer.tail_flush_frames();
    CHECK(renderer.reset() == Status::Ok);
    CHECK(same_state(renderer.state(), fresh.state()));
    CHECK(same_diagnostics(renderer.diagnostics(), RendererDiagnostics{}));
    CHECK(renderer.path_bounds() == prepared_bounds && renderer.history_capacity_frames() == capacity
          && renderer.tail_flush_frames() == flush && renderer.profile() == profile);
    accept(renderer, horn, drum, left, right, commands);
    accept(fresh, horn, drum, fresh_left, fresh_right, commands);
    same_audio(left, fresh_left);
    same_audio(right, fresh_right);
    CHECK(same_state(renderer.state(), fresh.state()));

    reject_lifecycle(renderer, Status::InvalidSpec, [&] { return renderer.reconfigure_sample_rate(48001.0); });
    reject_lifecycle(renderer, Status::InvalidSpec, [&] {
        return renderer.reconfigure_sample_rate(std::numeric_limits<double>::quiet_NaN());
    });
    auto invalid_profile = profile;
    invalid_profile.rotors[1].initial_command = static_cast<SpeedCommand>(9);
    reject_lifecycle(renderer, Status::InvalidProfile, [&] { return renderer.prepare(invalid_profile, {kRate, 64}); });
    const auto physical = renderer.state();
    CHECK(renderer.reconfigure_sample_rate(96000.0) == Status::Ok);
    CHECK(renderer.profile() == profile && renderer.spec().max_block_frames == kMaxBlockFrames);
    CHECK(renderer.state().frame == 0 && renderer.state().sample_rate == 96000.0);
    CHECK(renderer.state().max_frame == kMaxEpochSeconds * 96000U);
    CHECK(same_diagnostics(renderer.diagnostics(), RendererDiagnostics{}));
    CHECK(renderer.path_bounds() == prepared_bounds);
    double maximum_distance = 0.0;
    for (const auto& bound : prepared_bounds) maximum_distance = std::max(maximum_distance, bound.max_distance_m);
    const auto propagation = static_cast<std::uint32_t>(std::ceil(96000.0 * maximum_distance / profile.sound_speed_m_s));
    CHECK(renderer.history_capacity_frames() == propagation + 6U && renderer.tail_flush_frames() == propagation + 4U);
    for (std::size_t rotor = 0; rotor < kRotorCount; ++rotor) {
        CHECK(Access::same_motion(renderer.state().motion[rotor], physical.motion[rotor]));
        CHECK(Access::same_motion(renderer.state().epoch_initial[rotor], physical.motion[rotor]));
        CHECK(renderer.state().commands[rotor] == physical.commands[rotor]);
        CHECK(renderer.state().segments[rotor].anchor_frame == 0);
        CHECK(Access::same_motion(renderer.state().segments[rotor].initial, physical.motion[rotor]));
    }
    std::array<double, 256> zero{}, silent_left{}, silent_right{};
    accept(renderer, std::span(zero).first(1), std::span(zero).first(1),
           std::span(silent_left).first(1), std::span(silent_right).first(1));
    CHECK(silent_left[0] == 0.0 && silent_right[0] == 0.0);
    const auto startup = renderer.diagnostics();
    for (std::size_t path = 0; path < kPathCount; ++path) {
        const auto rotor = path / kMicrophoneCount;
        const auto position = startup.last_emissions[path];
        CHECK(position.frame < 0);
        const long double elapsed = (static_cast<long double>(position.frame) + position.fraction) / 96000.0L;
        long double phase = static_cast<long double>(physical.motion[rotor].phase_rad)
            + static_cast<long double>(profile.rotors[rotor].motion.direction)
            * physical.motion[rotor].speed_rad_s * elapsed;
        phase = std::fmod(phase, static_cast<long double>(kTwoPi));
        if (phase < 0.0L) phase += static_cast<long double>(kTwoPi);
        CHECK_NEAR(startup.last_paths[path].emission_phase_rad, phase, 3.0e-12L);
    }
    accept(renderer, zero, zero, silent_left, silent_right);
    for (std::size_t frame = 0; frame < zero.size(); ++frame) CHECK(silent_left[frame] == 0.0 && silent_right[frame] == 0.0);
    const auto same_rate_seed = renderer.state();
    CHECK(renderer.reconfigure_sample_rate(96000.0) == Status::Ok);
    CHECK(renderer.state().frame == 0 && same_diagnostics(renderer.diagnostics(), RendererDiagnostics{}));
    for (std::size_t rotor = 0; rotor < kRotorCount; ++rotor) {
        CHECK(Access::same_motion(renderer.state().motion[rotor], same_rate_seed.motion[rotor]));
        CHECK(Access::same_motion(renderer.state().epoch_initial[rotor], same_rate_seed.motion[rotor]));
    }
    CHECK(renderer.reset() == Status::Ok);
    CHECK(fresh.prepare(profile, {96000.0, kMaxBlockFrames}) == Status::Ok);
    CHECK(same_state(renderer.state(), fresh.state()));
    CHECK(renderer.reset() == Status::Ok); // Original seed, even after two rate epochs.
    accept(renderer, horn, drum, left, right, commands);
    accept(fresh, horn, drum, fresh_left, fresh_right, commands);
    same_audio(left, fresh_left);
    same_audio(right, fresh_right);

    const auto first_tail_frame = renderer.state().frame;
    const auto total_flush = renderer.tail_flush_frames();
    std::uint32_t remaining = total_flush;
    while (remaining != 0) {
        const auto count = std::min<std::uint32_t>(remaining, static_cast<std::uint32_t>(zero.size()));
        accept(renderer, std::span(zero).first(count), std::span(zero).first(count),
               std::span(silent_left).first(count), std::span(silent_right).first(count));
        remaining -= count;
        if (remaining == 0) CHECK(silent_left[count - 1] == 0.0 && silent_right[count - 1] == 0.0);
    }
    CHECK(renderer.state().frame == first_tail_frame + total_flush);
    accept(renderer, zero, zero, silent_left, silent_right);
    for (std::size_t frame = 0; frame < zero.size(); ++frame) CHECK(silent_left[frame] == 0.0 && silent_right[frame] == 0.0);
}

} // namespace

int main() {
    defaults_and_preparation();
    stationary_waveform_and_signed_inputs();
    event_boundaries_and_zero_calls();
    rejection_order_and_aliases();
    accelerated_epoch_boundary_precedence();
    lifecycle_reset_reconfigure_and_explicit_tail();
    std::cout << std::setprecision(17)
              << "{\"suites\":6,\"analytical_samples\":" << analytical_samples
              << ",\"analytical_fixtures\":" << analytical_fixtures
              << ",\"maximum_analytical_error\":" << maximum_analytical_error
              << ",\"rms_analytical_error\":" << std::sqrt(analytical_squared_error / static_cast<long double>(analytical_samples))
              << ",\"worst_fixture_channel_frame\":[" << worst_analytical_coordinate[0]
              << ',' << worst_analytical_coordinate[1] << ',' << worst_analytical_coordinate[2] << ']'
              << ",\"rejected_process_calls\":" << rejected_process_calls
              << ",\"rejected_lifecycle_calls\":" << rejected_lifecycle_calls
              << ",\"accepted_events\":" << accepted_events
              << ",\"accelerated_epoch_fixture\":true,\"result\":\"pass\"}\n";
}
