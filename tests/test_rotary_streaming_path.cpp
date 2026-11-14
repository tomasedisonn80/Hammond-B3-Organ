#include "hammond/RotaryPropagation.h"
#include "hammond/RotaryRenderer.h"
#include "reference/rotary_waveform_reference.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <limits>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <type_traits>
#include <vector>

// Full-day arithmetic is tested with a coherent retained window, not billions
// of appends. This accessor exists only in this separately linked test binary.
namespace hammond::rotary::detail {
struct RotaryRendererTestAccess {
    static void prime_window(MotionFrameHistory& history,
                             const std::vector<MotionSegment>& segments,
                             std::uint64_t next_frame) {
        history.next_frame_ = next_frame;
        for (std::uint64_t frame = history.oldest_frame(); frame < next_frame; ++frame) {
            const auto after = std::upper_bound(segments.begin(), segments.end(), frame,
                [](std::uint64_t query, const MotionSegment& segment) {
                    return query < segment.anchor_frame;
                });
            if (after == segments.begin()) throw std::runtime_error("missing test anchor");
            history.segments_[static_cast<std::size_t>(frame % history.capacity_frames_)] =
                *(after - 1);
        }
    }

    static std::uint64_t anchor_at(const MotionFrameHistory& history, std::uint64_t frame) {
        return history.segments_[static_cast<std::size_t>(frame % history.capacity_frames_)].anchor_frame;
    }
};
} // namespace hammond::rotary::detail

namespace {
using namespace hammond::rotary;
namespace reference = rotary_waveform_reference;
using Real = reference::Real;

constexpr std::array<std::uint32_t, 4> rates{44100, 48000, 96000, 192000};
constexpr std::array<std::int8_t, 2> directions{-1, 1};
constexpr double nan = std::numeric_limits<double>::quiet_NaN();
constexpr double infinity = std::numeric_limits<double>::infinity();
constexpr double below_one = 0x1.fffffffffffffp-1;
std::uint64_t checks{};
std::string context;

void require(bool condition, const char* expression, int line) {
    ++checks;
    if (!condition) {
        throw std::runtime_error("line " + std::to_string(line) + ": " + expression +
                                 " [" + context + "]");
    }
}
#define CHECK(expression) require(static_cast<bool>(expression), #expression, __LINE__)

struct ErrorStats {
    std::uint64_t count{};
    Real maximum{};
    Real sum_squared{};
    std::string worst;

    void add(Real error) {
        CHECK(std::isfinite(error) && error >= 0);
        ++count;
        sum_squared += error * error;
        if (worst.empty() || error > maximum) {
            maximum = error;
            worst = context;
        }
    }
    [[nodiscard]] Real rms() const {
        return count == 0 ? 0 : std::sqrt(sum_squared / static_cast<Real>(count));
    }
};

struct Results {
    std::uint64_t exact_r3_paths{};
    std::uint64_t successful_paths{};
    std::uint64_t analytic_paths{};
    std::uint64_t command_side_roots{};
    std::uint64_t retired_anchor_paths{};
    std::uint64_t epoch_paths{};
    std::uint64_t preparation_rejections{};
    std::uint64_t solve_rejections{};
    std::uint64_t mismatch_rejections{};
    std::uint64_t conservative_bracket_rejections{};
    std::uint64_t changed_seed_paths{};
    std::uint64_t mach_limit_paths{};
    double maximum_native_residual{};
    std::uint32_t maximum_native_evaluations{};
    Real maximum_reference_residual{};
    unsigned maximum_reference_evaluations{};
    ErrorStats root_delay;
    ErrorStats root_ratio;
    ErrorStats emission_frame_error;
    ErrorStats identical_state_distance;
    ErrorStats identical_state_ratio;
    ErrorStats identical_state_gain;
    ErrorStats motion_angle;
    ErrorStats motion_speed;
    ErrorStats motion_root_bound;
    ErrorStats analytic_delay;
    ErrorStats analytic_distance;
    ErrorStats analytic_gain;
};
Results results;

[[nodiscard]] bool same_bits(double first, double second) {
    return std::bit_cast<std::uint64_t>(first) == std::bit_cast<std::uint64_t>(second);
}

[[nodiscard]] bool same_path(const PathResult& first, const PathResult& second) {
    return same_bits(first.delay_s, second.delay_s)
        && same_bits(first.distance_m, second.distance_m)
        && same_bits(first.emission_phase_rad, second.emission_phase_rad)
        && same_bits(first.radial_speed_m_s, second.radial_speed_m_s)
        && same_bits(first.frequency_ratio, second.frequency_ratio)
        && same_bits(first.distance_gain, second.distance_gain)
        && same_bits(first.residual_s, second.residual_s)
        && first.iterations == second.iterations;
}

[[nodiscard]] bool same_position(SamplePosition first, SamplePosition second) {
    return first.frame == second.frame && same_bits(first.fraction, second.fraction);
}

template<class T>
[[nodiscard]] auto bytes(const T& value) {
    static_assert(std::is_trivially_copyable_v<T>);
    std::array<std::byte, sizeof(T)> answer{};
    std::memcpy(answer.data(), &value, sizeof(T));
    return answer;
}

[[nodiscard]] PathResult sentinel_path() {
    return {9.0, 8.0, 7.0, 6.0, 5.0, 4.0, -0.0, 123};
}
[[nodiscard]] SamplePosition sentinel_position() { return {-123456, 0.375}; }

[[nodiscard]] std::string position_text(SamplePosition position) {
    std::ostringstream out;
    out << position.frame << '+' << std::setprecision(std::numeric_limits<double>::max_digits10)
        << position.fraction;
    return out.str();
}

[[nodiscard]] RotorProfile moving_rotor(std::int8_t direction = 1) {
    return {{-0.12, 0.07, 1.10}, 0.18, {5.0, 70.0, 0.001, 0.01, direction},
            0.31, 7.25, SpeedCommand::Chorale};
}

[[nodiscard]] reference::Rotor reference_rotor(const RotorProfile& rotor) {
    return {{rotor.origin_m.x, rotor.origin_m.y, rotor.origin_m.z}, rotor.radius_m,
            rotor.motion.slow_rad_s, rotor.motion.fast_rad_s, rotor.motion.tau_up_s,
            rotor.motion.tau_down_s, rotor.motion.direction, rotor.initial_phase_rad,
            rotor.initial_speed_rad_s,
            rotor.initial_command == SpeedCommand::Chorale ? reference::Command::Chorale
                                                           : reference::Command::Tremolo};
}

[[nodiscard]] reference::Vec3 reference_mic(const MicrophoneProfile& mic) {
    return {mic.position_m.x, mic.position_m.y, mic.position_m.z};
}

struct Event {
    std::uint64_t frame{};
    SpeedCommand command{};
};

[[nodiscard]] std::vector<reference::Event> reference_events(const std::vector<Event>& events) {
    std::vector<reference::Event> answer;
    for (const auto& event : events) {
        answer.push_back({static_cast<std::int64_t>(event.frame), 0,
            event.command == SpeedCommand::Chorale ? reference::Command::Chorale
                                                   : reference::Command::Tremolo});
    }
    return answer;
}

struct Fixture {
    RotorProfile rotor;
    std::uint32_t rate;
    RotaryMotion owner;
    std::unique_ptr<MotionFrameHistory> history = std::make_unique<MotionFrameHistory>();
    std::vector<MotionSegment> segments;
    MotionHistoryView immutable;

    Fixture(RotorProfile initial, std::uint32_t sample_rate, std::size_t capacity,
            std::uint64_t through, const std::vector<Event>& events = {}, bool prime = false)
        : rotor(initial), rate(sample_rate) {
        CHECK(owner.prepare(rotor.motion, rotor.initial_phase_rad, rotor.initial_speed_rad_s,
                            rotor.initial_command, rate) == Status::Ok);
        CHECK(history->prepare(owner, capacity) == Status::Ok);
        segments.push_back(owner.segment());
        if (prime) {
            for (const Event& event : events) {
                CHECK(event.frame <= through);
                CHECK(owner.apply_command(event.frame, event.command) == Status::Ok);
                remember_segment();
            }
            CHECK(owner.advance_to(through) == Status::Ok);
            detail::RotaryRendererTestAccess::prime_window(*history, segments, through);
        } else {
            std::size_t event_index = 0;
            for (std::uint64_t frame = 0; frame <= through; ++frame) {
                CHECK(owner.advance_to(frame) == Status::Ok);
                while (event_index < events.size() && events[event_index].frame == frame) {
                    CHECK(owner.apply_command(frame, events[event_index].command) == Status::Ok);
                    remember_segment();
                    ++event_index;
                }
                if (frame < through) CHECK(history->append(owner) == Status::Ok);
            }
            CHECK(event_index == events.size());
        }
        // No writes or container movement occur after this borrowed view is
        // admitted. All R3 paths are destroyed before this fixture's segments.
        CHECK(immutable.prepare(rotor.motion, owner.epoch_initial_state(), rate,
                                segments, through) == Status::Ok);
    }

    void remember_segment() {
        const auto next = owner.segment();
        if (next == segments.back()) return;
        if (next.anchor_frame == segments.back().anchor_frame) segments.back() = next;
        else segments.push_back(next);
    }

    Fixture(const Fixture&) = delete;
    Fixture& operator=(const Fixture&) = delete;
};

void observe_success(SamplePosition observation, const PathResult& path, SamplePosition emission) {
    CHECK(std::isfinite(path.delay_s) && path.delay_s > 0);
    CHECK(std::isfinite(path.residual_s) && std::abs(path.residual_s) <= 1.0e-11);
    CHECK(path.iterations >= 2 && path.iterations <= 48);
    CHECK(emission.frame < observation.frame ||
          (emission.frame == observation.frame && emission.fraction < observation.fraction));
    CHECK(std::isfinite(emission.fraction) && emission.fraction >= 0 && emission.fraction < 1);
    CHECK(path.frequency_ratio >= 1.0 / (1.25 + 2.0e-15)
          && path.frequency_ratio <= 1.0 / (0.75 - 2.0e-15));
    ++results.successful_paths;
    results.maximum_native_residual = std::max(results.maximum_native_residual, std::abs(path.residual_s));
    results.maximum_native_evaluations = std::max(results.maximum_native_evaluations, path.iterations);
}

[[nodiscard]] PathResult compare_exact(const PreparedStreamingPath& streaming,
                                       const PreparedRetardedPath& immutable,
                                       const MotionFrameHistory& history,
                                       SamplePosition observation, SamplePosition& emission) {
    PathResult actual = sentinel_path();
    PathResult expected = sentinel_path();
    emission = sentinel_position();
    SamplePosition expected_emission = sentinel_position();
    CHECK(streaming.solve(history, observation, actual, emission) == Status::Ok);
    CHECK(immutable.solve(observation, expected, expected_emission) == Status::Ok);
    CHECK(same_path(actual, expected));
    CHECK(same_position(emission, expected_emission));
    observe_success(observation, actual, emission);
    ++results.exact_r3_paths;
    return actual;
}

void compare_independent(const Fixture& fixture, const MicrophoneProfile& mic, double sound_speed,
                         double reference_distance, const reference::Timeline& timeline,
                         SamplePosition observation, const PathResult& actual,
                         SamplePosition emission) {
    const auto rotor = reference_rotor(fixture.rotor);
    const auto microphone = reference_mic(mic);
    const auto bounds = reference::path_bounds(rotor, microphone, sound_speed);
    const auto expected = reference::solve_path(timeline, rotor, microphone, bounds,
        {observation.frame, observation.fraction}, fixture.rate, sound_speed, reference_distance,
        reference::SolveMethod::PureBisection, 1.0e-16L);
    const Real delay_error = std::abs(static_cast<Real>(actual.delay_s) - expected.delay_s);
    const Real ratio_error = std::abs(static_cast<Real>(actual.frequency_ratio) - expected.geometry.frequency_ratio);
    results.root_delay.add(delay_error);
    results.root_ratio.add(ratio_error);
    CHECK(delay_error <= 2.0e-11L);
    CHECK(ratio_error <= 2.0e-10L);
    const Real emission_error = std::abs(static_cast<Real>(emission.frame - expected.emission.frame)
        + static_cast<Real>(emission.fraction) - expected.emission.fraction);
    results.emission_frame_error.add(emission_error);
    CHECK(emission_error <= 2.0e-11L * fixture.rate + 1.0e-12L);
    results.maximum_reference_residual = std::max(results.maximum_reference_residual,
                                                 std::abs(expected.residual_s));
    results.maximum_reference_evaluations = std::max(results.maximum_reference_evaluations,
                                                    expected.evaluations);

    MotionState supplied;
    CHECK(fixture.history->state_at(emission, supplied) == Status::Ok);
    const auto at_supplied = reference::cartesian_geometry(rotor, microphone,
        {supplied.phase_rad, supplied.speed_rad_s}, sound_speed);
    const Real distance_error = std::abs(static_cast<Real>(actual.distance_m) - at_supplied.distance_m);
    const Real geometry_ratio_error = std::abs(static_cast<Real>(actual.frequency_ratio) - at_supplied.frequency_ratio);
    const Real gain_error = std::abs(static_cast<Real>(actual.distance_gain)
        - static_cast<Real>(reference_distance) / at_supplied.distance_m);
    results.identical_state_distance.add(distance_error);
    results.identical_state_ratio.add(geometry_ratio_error);
    results.identical_state_gain.add(gain_error);
    CHECK(distance_error <= 2.0e-12L);
    CHECK(geometry_ratio_error <= 2.0e-10L);
    CHECK(gain_error <= 1.0e-10L);

    const auto independent_motion = timeline.at({emission.frame, emission.fraction});
    const Real angle = static_cast<Real>(supplied.phase_rad)
        + static_cast<Real>(supplied.turns) * reference::kTwoPi;
    const Real phase_error = std::abs(angle - independent_motion.angle_rad);
    const Real speed_error = std::abs(static_cast<Real>(supplied.speed_rad_s) - independent_motion.speed_rad_s);
    results.motion_angle.add(phase_error);
    results.motion_speed.add(speed_error);
    results.motion_root_bound.add(rotor.radius_m * phase_error /
        (static_cast<Real>(sound_speed) * (1 - bounds.beta)));
    CHECK(phase_error <= 5.0e-12L + 4.0e-15L * std::abs(independent_motion.angle_rad));
    CHECK(speed_error <= 5.0e-12L + 4.0e-14L * std::abs(independent_motion.speed_rad_s));
}

[[nodiscard]] SamplePosition add_seconds(reference::Position position, Real seconds, std::uint32_t rate) {
    const Real local = position.fraction + seconds * rate;
    const Real whole = std::floor(local);
    SamplePosition answer{position.frame + static_cast<std::int64_t>(whole),
                          static_cast<double>(local - whole)};
    if (answer.fraction == 1) { ++answer.frame; answer.fraction = 0; }
    return answer;
}

void rejection(const PreparedStreamingPath& path, const MotionFrameHistory& history,
               SamplePosition observation, Status expected) {
    PathResult output = sentinel_path();
    SamplePosition emission = sentinel_position();
    const auto path_before = bytes(path);
    CHECK(path.solve(history, observation, output, emission) == expected);
    CHECK(same_path(output, sentinel_path()));
    CHECK(same_position(emission, sentinel_position()));
    CHECK(bytes(path) == path_before);
    ++results.solve_rejections;
}

void moving_parity() {
    const auto c = SpeedCommand::Chorale;
    const auto t = SpeedCommand::Tremolo;
    const std::vector<Event> events{{0, t}, {0, c}, {1, t}, {31, c}, {32, t}, {32, c},
        {32, t}, {63, t}, {64, c}, {257, t}, {1024, c}, {1025, t}, {2048, c},
        {3071, t}, {4096, c}};
    const std::array<MicrophoneProfile, 2> microphones{{{{1.35, -0.80, 1.25}},
                                                      {{-1.20, -0.65, 0.90}}}};
    for (const auto rate : rates) {
        for (const auto direction : directions) {
            for (unsigned mode = 0; mode < 2; ++mode) {
                auto rotor = moving_rotor(direction);
                if (mode == 1) {
                    rotor.motion = {0.0, 75.0, 0.01, 60.0, direction};
                    rotor.initial_speed_rad_s = 90.0;
                    rotor.initial_phase_rad = 5.9;
                }
                context = "moving fs=" + std::to_string(rate) + " dir=" + std::to_string(direction)
                    + " mode=" + std::to_string(mode);
                Fixture fixture(rotor, rate, 4096, 4096, events);
                CHECK(fixture.segments.size() == 11);
                const auto history_before = std::make_unique<MotionFrameHistory>(*fixture.history);
                reference::Timeline independent(reference_rotor(rotor), rate, reference_events(events), 0);
                for (std::size_t receiver = 0; receiver < microphones.size(); ++receiver) {
                    const auto& mic = microphones[receiver];
                    PreparedStreamingPath streaming;
                    PreparedRetardedPath immutable;
                    CHECK(streaming.prepare(rotor, mic, 343.0, 1.0) == Status::Ok);
                    CHECK(immutable.prepare(fixture.immutable, rotor.origin_m, rotor.radius_m,
                                            mic, 343.0, 1.0) == Status::Ok);
                    CHECK(streaming.bounds() == immutable.bounds());
                    const auto path_before = bytes(streaming);
                    const std::array<SamplePosition, 25> observations{{
                        {-2048, 0.125}, {-1, below_one}, {0, 0}, {0, 0.125}, {1, 0},
                        {30, below_one}, {31, 0}, {31, below_one}, {32, 0}, {32, 0.125},
                        {63, below_one}, {64, 0}, {256, below_one}, {257, 0}, {257, 0.875},
                        {1023, below_one}, {1024, 0}, {1025, 0.25}, {2047, below_one},
                        {2048, 0}, {2048, 0.5}, {3071, 0}, {4095, 0}, {4095, below_one},
                        {4096, 0}}};
                    const auto prefix = "moving fs=" + std::to_string(rate) + " dir="
                        + std::to_string(direction) + " mode=" + std::to_string(mode)
                        + " mic=" + std::to_string(receiver);
                    for (const auto observation : observations) {
                        context = prefix + " obs=" + position_text(observation);
                        SamplePosition emission;
                        const auto actual = compare_exact(streaming, immutable, *fixture.history, observation, emission);
                        compare_independent(fixture, mic, 343.0, 1.0, independent, observation, actual, emission);
                    }
                    // Construct receiver arrival times from independent emission
                    // states one sample before, on, and after each command.
                    for (const std::int64_t anchor : {1, 31, 32, 64, 257, 1024, 1025, 2048}) {
                        for (const std::int64_t side : {-1, 0, 1}) {
                            const reference::Position intended{anchor + side, 0};
                            const auto state = independent.at(intended);
                            const auto geometry = reference::cartesian_geometry(reference_rotor(rotor),
                                reference_mic(mic), state, 343.0);
                            const auto observation = add_seconds(intended, geometry.distance_m / 343.0L, rate);
                            context = prefix + " emission-command=" + std::to_string(anchor)
                                + " side=" + std::to_string(side);
                            SamplePosition emission;
                            const auto actual = compare_exact(streaming, immutable, *fixture.history, observation, emission);
                            compare_independent(fixture, mic, 343.0, 1.0, independent, observation, actual, emission);
                            const Real offset = static_cast<Real>(emission.frame - intended.frame) + emission.fraction;
                            CHECK(std::abs(offset) <= 2.0e-11L * rate);
                            if (side < 0) CHECK(emission.frame < anchor);
                            if (side > 0) CHECK(emission.frame >= anchor);
                            ++results.command_side_roots;
                        }
                    }
                    CHECK(bytes(streaming) == path_before);
                }
                CHECK(*fixture.history == *history_before);
            }
        }
    }
}

void analytic_stationary() {
    struct Case { Vec3 origin; double radius; double phase; Vec3 mic; double speed; };
    const std::array<Case, 5> cases{{
        {{0, 0, 0}, 0, 0.7, {0.02, 0, 0}, 200},
        {{-10, 0, 0}, 0, 2.3, {10, 0, 0}, 200},
        {{1, 2, 3}, 0, 4.0, {4, 6, 3}, 0},
        {{0, 0, 0}, 0.18, 0, {1.18, 0, 0}, 0},
        {{0, 0, 0}, 1, kTwoPi / 4, {0, 2, 0.2}, 0}}};
    for (const auto rate : rates) {
        for (const auto direction : directions) {
            for (std::size_t index = 0; index < cases.size(); ++index) {
                const auto& item = cases[index];
                const RotorProfile rotor{item.origin, item.radius, {0, item.speed, 0.001, 60, direction},
                                         item.phase, item.speed, SpeedCommand::Chorale};
                const MicrophoneProfile mic{item.mic};
                context = "stationary fixture fs=" + std::to_string(rate) + " case=" + std::to_string(index);
                Fixture fixture(rotor, rate, 1, 0);
                for (const double sound_speed : {300.0, 343.0, 380.0}) {
                    for (const double distance_reference : {0.02, 1.0, 10.0}) {
                        PreparedStreamingPath streaming;
                        PreparedRetardedPath immutable;
                        CHECK(streaming.prepare(rotor, mic, sound_speed, distance_reference) == Status::Ok);
                        CHECK(immutable.prepare(fixture.immutable, rotor.origin_m, rotor.radius_m,
                                                mic, sound_speed, distance_reference) == Status::Ok);
                        // This is an explicit Cartesian analytic stationary
                        // source, independent of either native path solver.
                        const Real x = static_cast<Real>(item.mic.x) - item.origin.x
                            - static_cast<Real>(item.radius) * std::cos(static_cast<Real>(item.phase));
                        const Real y = static_cast<Real>(item.mic.y) - item.origin.y
                            - static_cast<Real>(item.radius) * std::sin(static_cast<Real>(item.phase));
                        const Real z = static_cast<Real>(item.mic.z) - item.origin.z;
                        const Real distance = std::sqrt(x * x + y * y + z * z);
                        for (const SamplePosition observation : std::array<SamplePosition, 3>{{{-1, 0.125}, {-1, below_one}, {0, 0}}}) {
                            context = "stationary fs=" + std::to_string(rate) + " dir=" + std::to_string(direction)
                                + " case=" + std::to_string(index) + " c=" + std::to_string(sound_speed)
                                + " ref=" + std::to_string(distance_reference) + " obs=" + position_text(observation);
                            SamplePosition emission;
                            const auto actual = compare_exact(streaming, immutable, *fixture.history, observation, emission);
                            const Real delay_error = std::abs(static_cast<Real>(actual.delay_s) - distance / sound_speed);
                            const Real distance_error = std::abs(static_cast<Real>(actual.distance_m) - distance);
                            const Real gain_error = std::abs(static_cast<Real>(actual.distance_gain) - distance_reference / distance);
                            results.analytic_delay.add(delay_error);
                            results.analytic_distance.add(distance_error);
                            results.analytic_gain.add(gain_error);
                            CHECK(delay_error <= 2.0e-11L);
                            CHECK(distance_error <= 2.0e-12L);
                            CHECK(gain_error <= 1.0e-10L);
                            CHECK(actual.frequency_ratio == 1 && actual.radial_speed_m_s == 0);
                            ++results.analytic_paths;
                        }
                    }
                }
            }
        }
    }
}

void geometry_grid() {
    for (const auto rate : rates) {
        for (const auto direction : directions) {
            for (const double radius : {0.0, 0.02, 0.18, 1.0}) {
                for (const double phase : {0.0, kTwoPi / 4, kTwoPi / 2, 3 * kTwoPi / 4}) {
                    for (const double sound_speed : {300.0, 343.0, 380.0}) {
                        const double speed = radius == 0 ? 200 : std::min(200.0, 0.25 * sound_speed / radius);
                        const RotorProfile rotor{{0, 0, 0}, radius, {0, speed, 0.01, 1, direction},
                                                 phase, speed, SpeedCommand::Chorale};
                        context = "geometry fixture";
                        Fixture fixture(rotor, rate, 1, 0);
                        reference::Timeline timeline(reference_rotor(rotor), rate, {}, 0);
                        const std::array<MicrophoneProfile, 3> microphones{{
                            {{radius + 0.020001, 0, 0}}, {{-radius - 1, 0.3, 0}}, {{0, 0, 1}}}};
                        for (std::size_t receiver = 0; receiver < microphones.size(); ++receiver) {
                            const auto& mic = microphones[receiver];
                            context = "geometry fs=" + std::to_string(rate) + " dir=" + std::to_string(direction)
                                + " r=" + std::to_string(radius) + " phase=" + std::to_string(phase)
                                + " c=" + std::to_string(sound_speed) + " mic=" + std::to_string(receiver);
                            PreparedStreamingPath streaming;
                            PreparedRetardedPath immutable;
                            CHECK(streaming.prepare(rotor, mic, sound_speed, 1.0) == Status::Ok);
                            CHECK(immutable.prepare(fixture.immutable, rotor.origin_m, rotor.radius_m,
                                                    mic, sound_speed, 1.0) == Status::Ok);
                            SamplePosition emission;
                            const auto actual = compare_exact(streaming, immutable, *fixture.history, {0, 0}, emission);
                            compare_independent(fixture, mic, sound_speed, 1.0, timeline, {0, 0}, actual, emission);
                        }
                    }
                }
            }
        }
    }
}

void admission_and_preservation() {
    context = "admission baseline";
    const auto rotor = moving_rotor();
    const MicrophoneProfile mic{{1.35, -0.80, 1.25}};
    Fixture fixture(rotor, 48000, 256, 256);
    const auto history_before = std::make_unique<MotionFrameHistory>(*fixture.history);
    PreparedStreamingPath path;
    CHECK(!path.prepared() && path.bounds() == PathBounds{});
    rejection(path, *fixture.history, {0, 0}, Status::NotPrepared);
    const auto unprepared_before = bytes(path);
    CHECK(path.prepare(rotor, mic, 299, 1) == Status::InvalidProfile);
    CHECK(bytes(path) == unprepared_before);
    ++results.preparation_rejections;
    CHECK(path.prepare(rotor, mic, 343, 1) == Status::Ok);
    PathResult baseline;
    SamplePosition baseline_emission;
    CHECK(path.solve(*fixture.history, {100, 0.25}, baseline, baseline_emission) == Status::Ok);
    const auto prepared_before = bytes(path);
    const auto reject_prepare = [&](RotorProfile candidate, MicrophoneProfile receiver,
                                    double speed_of_sound, double distance_reference) {
        CHECK(path.prepare(candidate, receiver, speed_of_sound, distance_reference) == Status::InvalidProfile);
        CHECK(bytes(path) == prepared_before);
        PathResult current;
        SamplePosition emission;
        CHECK(path.solve(*fixture.history, {100, 0.25}, current, emission) == Status::Ok);
        CHECK(same_path(current, baseline) && same_position(emission, baseline_emission));
        ++results.preparation_rejections;
    };
    for (const double invalid : {-10.01, 10.01, nan, infinity}) {
        for (unsigned coordinate = 0; coordinate < 3; ++coordinate) {
            auto changed = rotor;
            auto receiver = mic;
            if (coordinate == 0) { changed.origin_m.x = invalid; receiver.position_m.x = invalid; }
            if (coordinate == 1) { changed.origin_m.y = invalid; receiver.position_m.y = invalid; }
            if (coordinate == 2) { changed.origin_m.z = invalid; receiver.position_m.z = invalid; }
            reject_prepare(changed, mic, 343, 1);
            reject_prepare(rotor, receiver, 343, 1);
        }
    }
    for (const double invalid : {-0.001, 1.001, nan, infinity}) {
        auto changed = rotor; changed.radius_m = invalid;
        reject_prepare(changed, mic, 343, 1);
    }
    for (const double invalid : {-0.001, 200.001, nan, infinity}) {
        auto changed = rotor; changed.motion.slow_rad_s = invalid;
        reject_prepare(changed, mic, 343, 1);
        changed = rotor; changed.motion.fast_rad_s = invalid;
        reject_prepare(changed, mic, 343, 1);
        changed = rotor; changed.initial_speed_rad_s = invalid;
        reject_prepare(changed, mic, 343, 1);
    }
    for (const double invalid : {0.0, 0.000999, 60.001, nan, infinity}) {
        auto changed = rotor; changed.motion.tau_up_s = invalid;
        reject_prepare(changed, mic, 343, 1);
        changed = rotor; changed.motion.tau_down_s = invalid;
        reject_prepare(changed, mic, 343, 1);
    }
    for (const double invalid : {-0.001, kTwoPi, nan, infinity}) {
        auto changed = rotor; changed.initial_phase_rad = invalid;
        reject_prepare(changed, mic, 343, 1);
    }
    for (const std::int8_t invalid : std::array<std::int8_t, 3>{-2, 0, 2}) {
        auto changed = rotor; changed.motion.direction = invalid;
        reject_prepare(changed, mic, 343, 1);
    }
    for (const double invalid : {299.999, 380.001, nan, infinity}) reject_prepare(rotor, mic, invalid, 1);
    for (const double invalid : {0.019999, 10.001, nan, infinity}) reject_prepare(rotor, mic, 343, invalid);
    auto changed = rotor; changed.motion.slow_rad_s = changed.motion.fast_rad_s + 1;
    reject_prepare(changed, mic, 343, 1);
    changed = rotor; changed.initial_command = static_cast<SpeedCommand>(255);
    reject_prepare(changed, mic, 343, 1);
    // Initial pose is clear, but a later part of the orbit intersects the mic.
    changed = rotor; changed.origin_m = {}; changed.radius_m = 1; changed.initial_phase_rad = kTwoPi / 2;
    reject_prepare(changed, {{1, 0, 0}}, 300, 1);
    changed.radius_m = 0;
    reject_prepare(changed, {{std::nextafter(0.02, 0.0), 0, 0}}, 300, 1);
    changed.origin_m = {-10, 0, 0};
    reject_prepare(changed, {{10, 0.01, 0}}, 300, 1);
    changed.origin_m = {}; changed.radius_m = 1; changed.motion.fast_rad_s = 75.001;
    reject_prepare(changed, {{2, 0, 0}}, 300, 1);
    changed.motion.fast_rad_s = 40; changed.initial_speed_rad_s = 75.001;
    reject_prepare(changed, {{2, 0, 0}}, 300, 1);
    CHECK(*fixture.history == *history_before);

    auto empty = std::make_unique<MotionFrameHistory>();
    rejection(path, *empty, {0, 0}, Status::NotPrepared);
    for (const double invalid : {-0.001, 1.0, nan, infinity}) {
        rejection(path, *fixture.history, {0, invalid}, Status::InvalidSpec);
    }
    const auto maximum = static_cast<std::int64_t>(kMaxEpochSeconds * 48000ULL);
    for (const SamplePosition observation : std::array<SamplePosition, 5>{{
            {-maximum - 1, 0}, {maximum + 1, 0}, {maximum, 0.25},
            {std::numeric_limits<std::int64_t>::min(), 0}, {std::numeric_limits<std::int64_t>::max(), 0}}}) {
        rejection(path, *fixture.history, observation, Status::TimelineOverflow);
    }
    rejection(path, *fixture.history, {256, 0.125}, Status::InsufficientHistory);
    rejection(path, *fixture.history, {257, 0}, Status::InsufficientHistory);
    CHECK(*fixture.history == *history_before);

    for (unsigned field = 0; field < 5; ++field) {
        auto incompatible = rotor;
        if (field == 0) incompatible.motion.slow_rad_s += 1;
        if (field == 1) incompatible.motion.fast_rad_s += 1;
        if (field == 2) incompatible.motion.tau_up_s *= 2;
        if (field == 3) incompatible.motion.tau_down_s *= 2;
        if (field == 4) incompatible.motion.direction = -1;
        Fixture mismatch(incompatible, 48000, 1, 0);
        rejection(path, *mismatch.history, {0, 0}, Status::InvalidProfile);
        ++results.mismatch_rejections;
    }
    auto excessive = rotor;
    excessive.initial_speed_rad_s = std::nextafter(rotor.motion.fast_rad_s, infinity);
    Fixture mismatch(excessive, 48000, 1, 0);
    rejection(path, *mismatch.history, {0, 0}, Status::InvalidProfile);
    ++results.mismatch_rejections;
    CHECK(bytes(path) == prepared_before);
}

void retired_coverage() {
    for (const auto rate : rates) {
        for (const auto direction : directions) {
            auto rotor = moving_rotor(direction);
            rotor.origin_m = {};
            rotor.radius_m = 0.02;
            const MicrophoneProfile mic{{0.4, 0.1, 0}};
            const std::vector<Event> events{{31, SpeedCommand::Tremolo}};
            context = "retired fixture fs=" + std::to_string(rate);
            Fixture fixture(rotor, rate, 512, 4096, events);
            CHECK(fixture.history->oldest_frame() == 3584);
            CHECK(detail::RotaryRendererTestAccess::anchor_at(*fixture.history, 3584) == 31);
            CHECK(detail::RotaryRendererTestAccess::anchor_at(*fixture.history, 4095) == 31);
            PreparedStreamingPath path;
            PreparedRetardedPath immutable;
            CHECK(path.prepare(rotor, mic, 343, 1) == Status::Ok);
            CHECK(immutable.prepare(fixture.immutable, rotor.origin_m, rotor.radius_m, mic, 343, 1) == Status::Ok);
            const auto history_before = std::make_unique<MotionFrameHistory>(*fixture.history);
            reference::Timeline timeline(reference_rotor(rotor), rate, reference_events(events), 0);
            const auto safe = static_cast<std::int64_t>(3584 + static_cast<std::uint64_t>(
                std::ceil(path.bounds().max_distance_m / 343 * rate)) + 2);
            for (const SamplePosition observation : std::array<SamplePosition, 7>{{
                    {-128, 0.25}, {-1, below_one}, {safe, 0}, {safe, 0.75},
                    {4095, 0}, {4095, below_one}, {4096, 0}}}) {
                context = "retired fs=" + std::to_string(rate) + " dir=" + std::to_string(direction)
                    + " obs=" + position_text(observation);
                SamplePosition emission;
                const auto actual = compare_exact(path, immutable, *fixture.history, observation, emission);
                compare_independent(fixture, mic, 343, 1, timeline, observation, actual, emission);
                ++results.retired_anchor_paths;
            }
            for (const SamplePosition observation : std::array<SamplePosition, 6>{{
                    {0, 0}, {3583, below_one}, {3584, 0}, {3584, 0.5}, {4096, 0.5}, {4097, 0}}}) {
                rejection(path, *fixture.history, observation, Status::InsufficientHistory);
            }
            CHECK(*fixture.history == *history_before);
        }
    }

    // The actual stationary root is retained, but the required full analytical
    // upper endpoint reaches retired history. The API must reject this case.
    context = "conservative full bracket coverage";
    const RotorProfile rotor{{0, 0, 0}, 0.5, {0, 0, 1, 1, 1}, 0, 0, SpeedCommand::Chorale};
    const MicrophoneProfile mic{{0.6, 0, 0.1}};
    Fixture fixture(rotor, 192000, 1024, 2048);
    PreparedStreamingPath path;
    PreparedRetardedPath immutable;
    CHECK(path.prepare(rotor, mic, 300, 1) == Status::Ok);
    CHECK(immutable.prepare(fixture.immutable, rotor.origin_m, rotor.radius_m, mic, 300, 1) == Status::Ok);
    PathResult actual;
    SamplePosition emission;
    CHECK(immutable.solve({1124, 0}, actual, emission) == Status::Ok);
    CHECK(emission.frame >= static_cast<std::int64_t>(fixture.history->oldest_frame()));
    rejection(path, *fixture.history, {1124, 0}, Status::InsufficientHistory);
    ++results.conservative_bracket_rejections;
}

void changed_epochs_and_speed_envelope() {
    auto original = moving_rotor();
    original.motion = {5, 40, 0.01, 0.1, 1};
    original.initial_speed_rad_s = 70;
    const MicrophoneProfile mic{{1.35, -0.80, 1.25}};
    PreparedStreamingPath path;
    context = "rate independent original geometry";
    CHECK(path.prepare(original, mic, 343, 1) == Status::Ok);
    CHECK(path.bounds().max_tangential_mach == original.radius_m * 70 / 343);
    const auto before = bytes(path);
    for (const auto rate : rates) {
        for (const double seed_speed : {0.0, 40.0, 70.0}) {
            context = "changed seed fs=" + std::to_string(rate) + " speed=" + std::to_string(seed_speed);
            auto rotor = original;
            rotor.initial_speed_rad_s = seed_speed;
            rotor.initial_phase_rad = 4.75;
            rotor.initial_command = SpeedCommand::Tremolo;
            Fixture fixture(rotor, rate, 256, 256);
            // Different admitted seed/phase/command can use this same path.
            PathResult actual;
            SamplePosition emission;
            CHECK(path.solve(*fixture.history, {0, 0}, actual, emission) == Status::Ok);
            observe_success({0, 0}, actual, emission);
            reference::Timeline timeline(reference_rotor(rotor), rate, {}, 0);
            compare_independent(fixture, mic, 343, 1, timeline, {0, 0}, actual, emission);
            ++results.changed_seed_paths;
        }
        RotaryMotion owner;
        CHECK(owner.prepare(original.motion, original.initial_phase_rad, original.initial_speed_rad_s,
                            original.initial_command, 48000) == Status::Ok);
        CHECK(owner.advance_to(48000) == Status::Ok);
        CHECK(owner.state().turns != 0);
        const auto seed = owner.state();
        CHECK(owner.reconfigure_sample_rate(rate) == Status::Ok);
        CHECK(owner.epoch_initial_state() == seed && owner.frame() == 0);
        const auto history = std::make_unique<MotionFrameHistory>();
        CHECK(history->prepare(owner, 16) == Status::Ok);
        const std::array<MotionSegment, 1> segments{owner.segment()};
        MotionHistoryView view;
        CHECK(view.prepare(original.motion, seed, rate, segments, 0) == Status::Ok);
        PreparedRetardedPath immutable;
        CHECK(immutable.prepare(view, original.origin_m, original.radius_m, mic, 343, 1) == Status::Ok);
        // R3 uses the smaller new epoch envelope, while its distance bracket
        // and every path result must still match this reused geometry exactly.
        PathResult actual;
        PathResult expected;
        SamplePosition emission;
        SamplePosition expected_emission;
        CHECK(path.solve(*history, {0, 0}, actual, emission) == Status::Ok);
        CHECK(immutable.solve({0, 0}, expected, expected_emission) == Status::Ok);
        // Distance bounds do not depend on speed, so these particular reused
        // geometries actually retain every R3 result bit as well.
        CHECK(same_path(actual, expected) && same_position(emission, expected_emission));
        observe_success({0, 0}, actual, emission);
        ++results.exact_r3_paths;
        ++results.changed_seed_paths;
    }
    auto excessive = original;
    excessive.initial_speed_rad_s = std::nextafter(70.0, infinity);
    Fixture incompatible(excessive, 48000, 1, 0);
    rejection(path, *incompatible.history, {0, 0}, Status::InvalidProfile);
    ++results.mismatch_rejections;
    CHECK(bytes(path) == before);
}

void epoch_boundaries() {
    for (const auto rate : rates) {
        for (const auto direction : directions) {
            const auto maximum = kMaxEpochSeconds * rate;
            const auto end = static_cast<std::int64_t>(maximum);
            RotorProfile rotor{{0, 0, 0}, 0, {5, 40, 0.01, 0.1, direction},
                               0.3, 7, SpeedCommand::Chorale};
            const MicrophoneProfile mic{{1, 0, 0}};
            const std::vector<Event> events{{maximum - 1000, SpeedCommand::Tremolo}};
            context = "primed coherent day window fs=" + std::to_string(rate);
            Fixture fixture(rotor, rate, 2048, maximum, events, true);
            PreparedStreamingPath path;
            PreparedRetardedPath immutable;
            CHECK(path.prepare(rotor, mic, 343, 1) == Status::Ok);
            CHECK(immutable.prepare(fixture.immutable, rotor.origin_m, rotor.radius_m, mic, 343, 1) == Status::Ok);
            const auto history_before = std::make_unique<MotionFrameHistory>(*fixture.history);
            for (const SamplePosition observation : std::array<SamplePosition, 8>{{
                    {-end + 1000, 0.125}, {-end + 1000, below_one},
                    {end - 900, 0.125}, {end - 900, 0.125 + 0x1p-30},
                    {end - 900, 0.125 + 0x1p-29}, {end - 1, 0.5},
                    {end - 1, below_one}, {end, 0}}}) {
                context = "day fs=" + std::to_string(rate) + " dir=" + std::to_string(direction)
                    + " obs=" + position_text(observation);
                SamplePosition emission;
                const auto actual = compare_exact(path, immutable, *fixture.history, observation, emission);
                CHECK(std::abs(actual.delay_s - 1.0 / 343) <= 2.0e-11);
                ++results.epoch_paths;
            }
            PathResult first;
            PathResult second;
            SamplePosition first_emission;
            SamplePosition second_emission;
            CHECK(path.solve(*fixture.history, {end - 900, 0.125}, first, first_emission) == Status::Ok);
            CHECK(path.solve(*fixture.history, {end - 900, 0.125 + 0x1p-30}, second, second_emission) == Status::Ok);
            CHECK(first_emission.frame == second_emission.frame);
            CHECK(same_bits(second_emission.fraction - first_emission.fraction, 0x1p-30));
            CHECK(same_bits(first.delay_s, second.delay_s));
            rejection(path, *fixture.history, {-end, 0}, Status::TimelineOverflow);
            rejection(path, *fixture.history, {-end - 1, 0}, Status::TimelineOverflow);
            rejection(path, *fixture.history, {end, 0.125}, Status::TimelineOverflow);
            rejection(path, *fixture.history, {end + 1, 0}, Status::TimelineOverflow);
            rejection(path, *fixture.history, {end - 2049, 0}, Status::InsufficientHistory);
            CHECK(*fixture.history == *history_before);
        }
    }
}

void tangential_mach_extrema() {
    for (const auto rate : rates) {
        for (const auto direction : directions) {
            const RotorProfile rotor{{0, 0, 0}, 0.375, {200, 200, 0.001, 60, direction},
                                     0, 200, SpeedCommand::Chorale};
            context = "mach fixture";
            Fixture fixture(rotor, rate, 2048, 2048);
            reference::Timeline timeline(reference_rotor(rotor), rate, {}, 0);
            for (const int sign : {-1, 1}) {
                const MicrophoneProfile mic{{0.375, static_cast<double>(sign * direction), 0}};
                context = "mach limit fs=" + std::to_string(rate) + " dir=" + std::to_string(direction)
                    + " radial-sign=" + std::to_string(sign);
                PreparedStreamingPath path;
                PreparedRetardedPath immutable;
                CHECK(path.prepare(rotor, mic, 300, 1) == Status::Ok);
                CHECK(path.bounds().max_tangential_mach == 0.25);
                CHECK(immutable.prepare(fixture.immutable, rotor.origin_m, rotor.radius_m, mic, 300, 1) == Status::Ok);
                const auto observation = add_seconds({0, 0}, 1.0L / 300, rate);
                SamplePosition emission;
                const auto actual = compare_exact(path, immutable, *fixture.history, observation, emission);
                compare_independent(fixture, mic, 300, 1, timeline, observation, actual, emission);
                CHECK(std::abs(actual.radial_speed_m_s - sign * 75.0) <= 2.0e-10);
                CHECK(std::abs(actual.frequency_ratio - 1.0 / (1.0 - sign * 0.25)) <= 2.0e-10);
                CHECK(std::abs(actual.delay_s - 1.0 / 300.0) <= 2.0e-11);
                ++results.mach_limit_paths;
            }
        }
    }
}

void print_stat(std::string_view name, const ErrorStats& metric, bool comma = true) {
    std::cout << "    \"" << name << "\": {\"count\":" << metric.count
              << ",\"maximum\":" << metric.maximum << ",\"rms\":" << metric.rms()
              << ",\"worst\":\"" << metric.worst << "\"}" << (comma ? ",\n" : "\n");
}

void print_report() {
    std::cout << std::setprecision(std::numeric_limits<Real>::max_digits10)
        << "{\n  \"experiment\":\"a17-bounded-streaming-path-v1\",\n"
        << "  \"status\":\"pass\",\n  \"rates\":[44100,48000,96000,192000],\n"
        << "  \"directions\":[-1,1],\n  \"reference\":\"" << reference::kReferenceId << "\",\n"
        << "  \"reference_method\":\"pure_bisection\",\n  \"reference_target_s\":1e-16,\n"
        << "  \"long_double_significand_bits\":" << std::numeric_limits<Real>::digits << ",\n"
        << "  \"checks\":" << checks << ",\n"
        << "  \"successful_paths\":" << results.successful_paths << ",\n"
        << "  \"exact_r3_paths\":" << results.exact_r3_paths << ",\n"
        << "  \"analytic_paths\":" << results.analytic_paths << ",\n"
        << "  \"command_side_roots\":" << results.command_side_roots << ",\n"
        << "  \"retired_anchor_paths\":" << results.retired_anchor_paths << ",\n"
        << "  \"epoch_paths\":" << results.epoch_paths << ",\n"
        << "  \"preparation_rejections\":" << results.preparation_rejections << ",\n"
        << "  \"solve_rejections\":" << results.solve_rejections << ",\n"
        << "  \"mismatch_rejections\":" << results.mismatch_rejections << ",\n"
        << "  \"conservative_bracket_rejections\":" << results.conservative_bracket_rejections << ",\n"
        << "  \"changed_seed_paths\":" << results.changed_seed_paths << ",\n"
        << "  \"mach_limit_paths\":" << results.mach_limit_paths << ",\n"
        << "  \"maximum_native_residual_s\":" << results.maximum_native_residual << ",\n"
        << "  \"maximum_native_evaluations\":" << results.maximum_native_evaluations << ",\n"
        << "  \"maximum_reference_residual_s\":" << results.maximum_reference_residual << ",\n"
        << "  \"maximum_reference_evaluations\":" << results.maximum_reference_evaluations << ",\n"
        << "  \"errors\":{\n";
    print_stat("root_delay_s", results.root_delay);
    print_stat("root_frequency_ratio", results.root_ratio);
    print_stat("emission_frames", results.emission_frame_error);
    print_stat("identical_state_distance_m", results.identical_state_distance);
    print_stat("identical_state_frequency_ratio", results.identical_state_ratio);
    print_stat("identical_state_gain", results.identical_state_gain);
    print_stat("motion_angle_rad", results.motion_angle);
    print_stat("motion_speed_rad_s", results.motion_speed);
    print_stat("motion_root_contribution_s", results.motion_root_bound);
    print_stat("analytic_delay_s", results.analytic_delay);
    print_stat("analytic_distance_m", results.analytic_distance);
    print_stat("analytic_gain", results.analytic_gain, false);
    std::cout << "  }\n}\n";
}
} // namespace

int main() {
    try {
        moving_parity();
        analytic_stationary();
        geometry_grid();
        admission_and_preservation();
        retired_coverage();
        changed_epochs_and_speed_envelope();
        epoch_boundaries();
        tangential_mach_extrema();
        print_report();
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "streaming path acceptance failed: " << error.what() << '\n';
        return 1;
    }
}
