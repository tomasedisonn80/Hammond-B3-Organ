#include "TestSupport.h"
#include "hammond/RotaryPropagation.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <cstring>
#include <limits>
#include <span>
#include <type_traits>
#include <utility>
#include <vector>

namespace {

using namespace hammond::rotary;
constexpr std::array<double, 4> rates{44100.0, 48000.0, 96000.0, 192000.0};
constexpr double nan = std::numeric_limits<double>::quiet_NaN();
constexpr double inf = std::numeric_limits<double>::infinity();
std::size_t history_queries = 0;
std::size_t rejected_calls = 0;
std::size_t solved_paths = 0;
double maximum_constant_delay_error = 0.0;
double maximum_residual = 0.0;
std::uint32_t maximum_evaluations = 0;

template<class T>
[[nodiscard]] auto bytes(const T& value) {
    static_assert(std::is_trivially_copyable_v<T>);
    std::array<std::byte, sizeof(T)> result{};
    std::memcpy(result.data(), &value, sizeof(T));
    return result;
}

[[nodiscard]] MotionState sentinel_state() { return {2.25, -1234, 31.0}; }
[[nodiscard]] PathResult sentinel_path() { return {9.0, 8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2}; }

struct Fixture {
    MotionProfile profile{5.0, 40.0, 0.01, 0.1, 1};
    MotionState seed{0.3, 0, 7.0};
    std::array<MotionSegment, 3> segments{};
    MotionHistoryView history{};
    explicit Fixture(double rate = 48000.0, std::int8_t direction = 1) {
        profile.direction = direction;
        CHECK(make_motion_segment(profile, seed, SpeedCommand::Chorale, 0, segments[0]) == Status::Ok);
        MotionState next;
        CHECK(evaluate_motion_segment_at(segments[0], {48, 0.0}, rate, next) == Status::Ok);
        CHECK(make_motion_segment(profile, next, SpeedCommand::Tremolo, 48, segments[1]) == Status::Ok);
        CHECK(evaluate_motion_segment_at(segments[1], {96, 0.0}, rate, next) == Status::Ok);
        CHECK(make_motion_segment(profile, next, SpeedCommand::Chorale, 96, segments[2]) == Status::Ok);
        CHECK(history.prepare(profile, seed, rate, segments, static_cast<std::uint64_t>(rate)) == Status::Ok);
    }
};

void check_history_queries() {
    MotionHistoryView unprepared;
    auto state = sentinel_state();
    CHECK(unprepared.state_at({0, 0.0}, state) == Status::NotPrepared);
    CHECK(state == sentinel_state());
    CHECK(!unprepared.prepared());

    for (const double rate : rates) {
        for (const auto direction : std::array<std::int8_t, 2>{-1, 1}) {
            Fixture fixture(rate, direction);
            CHECK(fixture.history.prepared());
            CHECK(fixture.history.sample_rate() == rate);
            CHECK(fixture.history.profile() == fixture.profile);
            CHECK(fixture.history.epoch_initial_state() == fixture.seed);
            CHECK(fixture.history.through_frame() == static_cast<std::uint64_t>(rate));
            const auto preserved = bytes(fixture.history);
            for (const SamplePosition position : std::array<SamplePosition, 13>{{
                     {-1, 0.0}, {-1, 0.75}, {0, 0.0}, {0, 0.125}, {47, 0.999},
                     {48, 0.0}, {48, 0.125}, {95, 0.999}, {96, 0.0}, {96, 0.125},
                     {99, 0.9}, {static_cast<std::int64_t>(rate) - 1, 0.999},
                     {static_cast<std::int64_t>(rate), 0.0}}}) {
                MotionState expected;
                if (position.frame < 0) {
                    CHECK(evaluate_motion_prehistory_at(fixture.seed, direction, position, rate, expected) == Status::Ok);
                } else {
                    const std::size_t index = position.frame >= 96 ? 2 : (position.frame >= 48 ? 1 : 0);
                    CHECK(evaluate_motion_segment_at(fixture.segments[index], position, rate, expected) == Status::Ok);
                }
                CHECK(fixture.history.state_at(position, state) == Status::Ok);
                CHECK(state == expected);
                ++history_queries;
            }
            CHECK(bytes(fixture.history) == preserved);
            CHECK(fixture.history.state_at({-1, 0.5}, state) == Status::Ok);
            CHECK(state.speed_rad_s == fixture.seed.speed_rad_s);
            for (const double fraction : {-1.0, 1.0, nan, inf}) {
                state = sentinel_state();
                CHECK(fixture.history.state_at({0, fraction}, state) == Status::InvalidSpec);
                CHECK(state == sentinel_state());
                ++rejected_calls;
            }
            const auto end = static_cast<std::int64_t>(kMaxEpochSeconds * static_cast<std::uint64_t>(rate));
            CHECK(fixture.history.state_at({-end, 0.0}, state) == Status::Ok);
            CHECK(state.speed_rad_s == fixture.seed.speed_rad_s);
            ++history_queries;
            for (const SamplePosition position : std::array<SamplePosition, 3>{{
                     {-end - 1, 0.0}, {end + 1, 0.0}, {end, 0.125}}}) {
                state = sentinel_state();
                CHECK(fixture.history.state_at(position, state) == Status::TimelineOverflow);
                CHECK(state == sentinel_state());
                ++rejected_calls;
            }
            state = sentinel_state();
            CHECK(fixture.history.state_at({static_cast<std::int64_t>(rate), 0.125}, state) == Status::InsufficientHistory);
            CHECK(state == sentinel_state());
            ++rejected_calls;
            CHECK(bytes(fixture.history) == preserved);
        }
    }
}

void check_history_admission() {
    Fixture fixture;
    const auto preserved = bytes(fixture.history);
    const auto reject = [&](const MotionProfile& profile, const MotionState& seed,
                            double rate, std::span<const MotionSegment> segments,
                            std::uint64_t through, Status expected) {
        CHECK(fixture.history.prepare(profile, seed, rate, segments, through) == expected);
        CHECK(bytes(fixture.history) == preserved);
        ++rejected_calls;
    };
    reject(fixture.profile, fixture.seed, 12345.0, fixture.segments, 48000, Status::InvalidSpec);
    reject(fixture.profile, fixture.seed, nan, fixture.segments, 48000, Status::InvalidSpec);
    reject(fixture.profile, fixture.seed, 48000.0, {}, 48000, Status::InvalidSpec);
    std::vector<MotionSegment> excessive(kMaxMotionSegments + 1, fixture.segments[0]);
    reject(fixture.profile, fixture.seed, 48000.0, excessive, 48000, Status::InvalidSpec);
    reject(fixture.profile, fixture.seed, 48000.0, fixture.segments,
           kMaxEpochSeconds * 48000ULL + 1, Status::TimelineOverflow);
    for (const double invalid : {-1.0, 201.0, nan, inf}) {
        auto profile = fixture.profile;
        profile.slow_rad_s = invalid;
        reject(profile, fixture.seed, 48000.0, fixture.segments, 48000, Status::InvalidProfile);
        profile = fixture.profile;
        profile.fast_rad_s = invalid;
        reject(profile, fixture.seed, 48000.0, fixture.segments, 48000, Status::InvalidProfile);
        auto seed = fixture.seed;
        seed.speed_rad_s = invalid;
        reject(fixture.profile, seed, 48000.0, fixture.segments, 48000, Status::InvalidProfile);
    }
    for (const double invalid : {0.0, 60.001, nan, inf}) {
        auto profile = fixture.profile;
        profile.tau_up_s = invalid;
        reject(profile, fixture.seed, 48000.0, fixture.segments, 48000, Status::InvalidProfile);
        profile = fixture.profile;
        profile.tau_down_s = invalid;
        reject(profile, fixture.seed, 48000.0, fixture.segments, 48000, Status::InvalidProfile);
    }
    for (const auto invalid : std::array<std::int8_t, 3>{-2, 0, 2}) {
        auto profile = fixture.profile;
        profile.direction = invalid;
        reject(profile, fixture.seed, 48000.0, fixture.segments, 48000, Status::InvalidProfile);
    }
    auto swapped_profile = fixture.profile;
    swapped_profile.slow_rad_s = fixture.profile.fast_rad_s + 1.0;
    reject(swapped_profile, fixture.seed, 48000.0, fixture.segments, 48000, Status::InvalidProfile);
    for (const double invalid : {-1.0, kTwoPi, nan, inf}) {
        auto seed = fixture.seed;
        seed.phase_rad = invalid;
        reject(fixture.profile, seed, 48000.0, fixture.segments, 48000, Status::InvalidProfile);
    }
    auto segments = fixture.segments;
    segments[0].anchor_frame = 1;
    reject(fixture.profile, fixture.seed, 48000.0, segments, 48000, Status::InvalidEvent);
    segments = fixture.segments;
    segments[1].anchor_frame = 0;
    reject(fixture.profile, fixture.seed, 48000.0, segments, 48000, Status::InvalidEvent);
    segments = fixture.segments;
    segments[2].anchor_frame = 47;
    reject(fixture.profile, fixture.seed, 48000.0, segments, 48000, Status::InvalidEvent);
    reject(fixture.profile, fixture.seed, 48000.0, fixture.segments, 95, Status::InvalidEvent);
    segments = fixture.segments;
    segments[2].anchor_frame = kMaxEpochSeconds * 48000ULL + 1;
    reject(fixture.profile, fixture.seed, 48000.0, segments, 48000, Status::TimelineOverflow);
    for (std::size_t index = 0; index < fixture.segments.size(); ++index) {
        segments = fixture.segments;
        segments[index].initial.phase_rad += 0.001;
        reject(fixture.profile, fixture.seed, 48000.0, segments, 48000, Status::InvalidProfile);
        segments = fixture.segments;
        ++segments[index].initial.turns;
        reject(fixture.profile, fixture.seed, 48000.0, segments, 48000, Status::InvalidProfile);
        segments = fixture.segments;
        segments[index].target_rad_s = 17.0;
        reject(fixture.profile, fixture.seed, 48000.0, segments, 48000, Status::InvalidProfile);
        segments = fixture.segments;
        segments[index].tau_s = 0.5;
        reject(fixture.profile, fixture.seed, 48000.0, segments, 48000, Status::InvalidProfile);
        segments = fixture.segments;
        segments[index].direction = -1;
        reject(fixture.profile, fixture.seed, 48000.0, segments, 48000, Status::InvalidProfile);
    }
    const MotionProfile overflowing{200.0, 200.0, 1.0, 1.0, 1};
    const MotionState full_turns{0.0, std::numeric_limits<std::int64_t>::max(), 200.0};
    MotionSegment overflow_segment;
    CHECK(make_motion_segment(overflowing, full_turns, SpeedCommand::Chorale, 0, overflow_segment) == Status::Ok);
    reject(overflowing, full_turns, 48000.0, {&overflow_segment, 1}, 48000, Status::TimelineOverflow);

    // Callers replace tied anchors and omit unchanged snapshots; no replay or
    // reanchoring is hidden inside the history view.
    RotaryMotion owner;
    CHECK(owner.prepare(fixture.profile, fixture.seed.phase_rad, fixture.seed.speed_rad_s,
                        SpeedCommand::Chorale, 48000.0) == Status::Ok);
    const MotionSegment initial = owner.segment();
    CHECK(owner.apply_command(24, SpeedCommand::Chorale) == Status::Ok);
    CHECK(owner.segment() == initial);
    CHECK(owner.apply_command(48, SpeedCommand::Tremolo) == Status::Ok);
    CHECK(owner.apply_command(48, SpeedCommand::Chorale) == Status::Ok);
    const std::array<MotionSegment, 2> replaced{initial, owner.segment()};
    MotionHistoryView replaced_history;
    CHECK(replaced_history.prepare(fixture.profile, fixture.seed, 48000.0, replaced, 48000) == Status::Ok);
    CHECK(owner.advance_to(48000) == Status::Ok);
    MotionState at_end;
    CHECK(replaced_history.state_at({48000, 0.0}, at_end) == Status::Ok);
    CHECK(at_end == owner.state());
}

void check_capacity_and_day_fractions() {
    for (const double rate : rates) {
        for (const auto direction : std::array<std::int8_t, 2>{-1, 1}) {
            MotionProfile profile{2.0, 30.0, 0.001, 0.01, direction};
            RotaryMotion owner;
            CHECK(owner.prepare(profile, 0.5, 9.0, SpeedCommand::Chorale, rate) == Status::Ok);
            std::vector<MotionSegment> segments;
            segments.reserve(kMaxMotionSegments);
            segments.push_back(owner.segment());
            for (std::size_t index = 1; index < kMaxMotionSegments; ++index) {
                CHECK(owner.apply_command(index, index % 2 == 0 ? SpeedCommand::Chorale : SpeedCommand::Tremolo) == Status::Ok);
                segments.push_back(owner.segment());
            }
            MotionHistoryView history;
            CHECK(history.prepare(profile, segments[0].initial, rate, segments, kMaxMotionSegments) == Status::Ok);
            for (std::size_t index = 0; index < segments.size(); ++index) {
                MotionState state;
                CHECK(history.state_at({static_cast<std::int64_t>(index), 0.0}, state) == Status::Ok);
                CHECK(state == segments[index].initial);
                CHECK(history.state_at({static_cast<std::int64_t>(index), 0.5}, state) == Status::Ok);
                MotionState expected;
                CHECK(evaluate_motion_segment_at(segments[index], {static_cast<std::int64_t>(index), 0.5}, rate, expected) == Status::Ok);
                CHECK(state == expected);
                history_queries += 2;
            }
        }

        const MotionProfile profile{10.0, 10.0, 1.0, 1.0, 1};
        const MotionState seed{0.3, 0, 10.0};
        MotionSegment segment;
        CHECK(make_motion_segment(profile, seed, SpeedCommand::Chorale, 0, segment) == Status::Ok);
        MotionHistoryView history;
        const auto end = kMaxEpochSeconds * static_cast<std::uint64_t>(rate);
        CHECK(history.prepare(profile, seed, rate, {&segment, 1}, end) == Status::Ok);
        MotionState before;
        MotionState after;
        CHECK(history.state_at({static_cast<std::int64_t>(end) - 1, 0.25}, before) == Status::Ok);
        CHECK(history.state_at({static_cast<std::int64_t>(end) - 1, 0.5}, after) == Status::Ok);
        const double phase_difference = after.phase_rad - before.phase_rad
            + static_cast<double>(after.turns - before.turns) * kTwoPi;
        CHECK_NEAR(phase_difference, 2.5 / rate, 2.0e-15);
        PreparedRetardedPath path;
        CHECK(path.prepare(history, {}, 0.0, {{0.02, 0.0, 0.0}}, 380.0, 1.0) == Status::Ok);
        for (const SamplePosition observation : std::array<SamplePosition, 3>{{
                 {static_cast<std::int64_t>(end) - 1, 0.25},
                 {static_cast<std::int64_t>(end) - 1, 0.5},
                 {static_cast<std::int64_t>(end), 0.0}}}) {
            PathResult result;
            SamplePosition emission;
            CHECK(path.solve(observation, result, emission) == Status::Ok);
            const long double local_frames = static_cast<long double>(observation.frame - emission.frame)
                + static_cast<long double>(observation.fraction) - emission.fraction;
            CHECK_NEAR(local_frames, static_cast<long double>(result.delay_s) * rate, 4.0e-14L);
            CHECK_NEAR(result.delay_s, 0.02 / 380.0, 3.0e-17);
            CHECK(result.iterations == 2);
            ++solved_paths;
        }
    }
}

void check_geometry() {
    const Vec3 origin{1.0, -2.0, 3.0};
    for (const auto direction : std::array<std::int8_t, 2>{-1, 1}) {
        for (std::size_t quadrant = 0; quadrant < 4; ++quadrant) {
            const MotionState state{static_cast<double>(quadrant) * kTwoPi / 4.0, -888, 10.0};
            Vec3 position;
            Vec3 velocity;
            CHECK(evaluate_circular_source(origin, 0.5, state, direction, position, velocity) == Status::Ok);
            const std::array<double, 4> cosine{1.0, 0.0, -1.0, 0.0};
            const std::array<double, 4> sine{0.0, 1.0, 0.0, -1.0};
            CHECK_NEAR(position.x, origin.x + 0.5 * cosine[quadrant], 3.0e-16);
            CHECK_NEAR(position.y, origin.y + 0.5 * sine[quadrant], 3.0e-16);
            CHECK(position.z == origin.z);
            CHECK_NEAR(velocity.x, -5.0 * direction * sine[quadrant], 1.0e-15);
            CHECK_NEAR(velocity.y, 5.0 * direction * cosine[quadrant], 1.0e-15);
            CHECK(velocity.z == 0.0);
        }
    }
    Vec3 position{9.0, 8.0, 7.0};
    Vec3 velocity{6.0, 5.0, 4.0};
    const auto initial_position = position;
    const auto initial_velocity = velocity;
    CHECK(evaluate_circular_source(origin, 0.5, {}, 1, position, position) == Status::InvalidBuffer);
    CHECK(position == initial_position);
    for (const double radius : {-1.0, 1.01, nan, inf}) {
        CHECK(evaluate_circular_source(origin, radius, {}, 1, position, velocity) == Status::InvalidProfile);
        CHECK(position == initial_position && velocity == initial_velocity);
        ++rejected_calls;
    }
    for (const Vec3 invalid : std::array<Vec3, 4>{{{10.1, 0.0, 0.0}, {0.0, -10.1, 0.0},
                                                 {0.0, 0.0, nan}, {inf, 0.0, 0.0}}}) {
        CHECK(evaluate_circular_source(invalid, 0.5, {}, 1, position, velocity) == Status::InvalidProfile);
        CHECK(position == initial_position && velocity == initial_velocity);
        ++rejected_calls;
    }
    for (const auto direction : std::array<std::int8_t, 3>{-2, 0, 2}) {
        CHECK(evaluate_circular_source(origin, 0.5, {}, direction, position, velocity) == Status::InvalidProfile);
        CHECK(position == initial_position && velocity == initial_velocity);
        ++rejected_calls;
    }
    for (const MotionState invalid : std::array<MotionState, 4>{{
             {kTwoPi, 0, 1.0}, {nan, 0, 1.0}, {0.0, 0, -1.0}, {0.0, 0, inf}}}) {
        CHECK(evaluate_circular_source(origin, 0.5, invalid, 1, position, velocity) == Status::InvalidProfile);
        CHECK(position == initial_position && velocity == initial_velocity);
        ++rejected_calls;
    }
    Vec3 origin_alias = origin;
    CHECK(evaluate_circular_source(origin_alias, 0.5, {0.0, 0, 10.0}, 1, origin_alias, velocity) == Status::Ok);
    CHECK((origin_alias == Vec3{1.5, -2.0, 3.0}));
    CHECK((velocity == Vec3{0.0, 5.0, 0.0}));
}

void check_path_transactions() {
    Fixture fixture;
    PreparedRetardedPath path;
    PathResult result = sentinel_path();
    SamplePosition emission{12345, 0.875};
    CHECK(path.bounds() == PathBounds{});
    CHECK(path.solve({0, 0.0}, result, emission) == Status::NotPrepared);
    CHECK(result == sentinel_path());
    CHECK((emission == SamplePosition{12345, 0.875}));
    CHECK(path.prepare(fixture.history, {}, 0.18, {{1.0, 0.1, 0.2}}, 343.0, 1.0) == Status::Ok);
    const auto preserved = bytes(path);
    const auto reject = [&](const MotionHistoryView& history, const Vec3& origin, double radius,
                            const MicrophoneProfile& mic, double c, double reference, Status expected) {
        CHECK(path.prepare(history, origin, radius, mic, c, reference) == expected);
        CHECK(bytes(path) == preserved);
        ++rejected_calls;
    };
    reject({}, {}, 0.18, {{1.0, 0.0, 0.0}}, 343.0, 1.0, Status::NotPrepared);
    reject(fixture.history, {}, 0.18, {{0.18, 0.0, 0.0}}, 343.0, 1.0, Status::InvalidProfile);
    reject(fixture.history, {-10.0, -10.0, -10.0}, 0.18, {{10.0, 10.0, 10.0}}, 343.0, 1.0, Status::InvalidProfile);
    for (const double invalid : {-1.0, 1.01, nan, inf}) {
        reject(fixture.history, {}, invalid, {{1.0, 0.0, 0.0}}, 343.0, 1.0, Status::InvalidProfile);
    }
    for (const double invalid : {299.0, 381.0, nan, inf}) {
        reject(fixture.history, {}, 0.18, {{1.0, 0.0, 0.0}}, invalid, 1.0, Status::InvalidProfile);
    }
    for (const double invalid : {0.019, 10.01, nan, inf}) {
        reject(fixture.history, {}, 0.18, {{1.0, 0.0, 0.0}}, 343.0, invalid, Status::InvalidProfile);
    }
    for (const Vec3 invalid : std::array<Vec3, 4>{{{10.1, 0.0, 0.0}, {0.0, -10.1, 0.0},
                                                 {0.0, 0.0, nan}, {inf, 0.0, 0.0}}}) {
        reject(fixture.history, invalid, 0.18, {{1.0, 0.0, 0.0}}, 343.0, 1.0, Status::InvalidProfile);
        reject(fixture.history, {}, 0.18, {invalid}, 343.0, 1.0, Status::InvalidProfile);
    }
    const MotionProfile slow_profile{1.0, 10.0, 1.0, 1.0, 1};
    const MotionState fast_seed{0.0, 0, 200.0};
    MotionSegment seed_segment;
    CHECK(make_motion_segment(slow_profile, fast_seed, SpeedCommand::Chorale, 0, seed_segment) == Status::Ok);
    MotionHistoryView seeded;
    CHECK(seeded.prepare(slow_profile, fast_seed, 48000.0, {&seed_segment, 1}, 48000) == Status::Ok);
    reject(seeded, {}, 1.0, {{2.0, 0.0, 0.0}}, 300.0, 1.0, Status::InvalidProfile);
    for (const auto& pair : std::array<std::pair<SamplePosition, Status>, 5>{{
             {{0, nan}, Status::InvalidSpec}, {{0, 1.0}, Status::InvalidSpec},
             {{48000, 0.25}, Status::InsufficientHistory},
             {{static_cast<std::int64_t>(kMaxEpochSeconds * 48000ULL) + 1, 0.0}, Status::TimelineOverflow},
             {{-static_cast<std::int64_t>(kMaxEpochSeconds * 48000ULL), 0.0}, Status::TimelineOverflow}}}) {
        CHECK(path.solve(pair.first, result, emission) == pair.second);
        CHECK(result == sentinel_path());
        CHECK((emission == SamplePosition{12345, 0.875}));
        CHECK(bytes(path) == preserved);
        ++rejected_calls;
    }

    // A path owns its view copy. Destruction/repreparation of another view does
    // not affect it while the backing segment array remains alive and immutable.
    PreparedRetardedPath copied;
    {
        MotionHistoryView local = fixture.history;
        CHECK(copied.prepare(local, {}, 0.18, {{1.0, 0.1, 0.2}}, 343.0, 1.0) == Status::Ok);
    }
    PathResult original_result;
    SamplePosition original_emission;
    CHECK(path.solve({100, 0.125}, original_result, original_emission) == Status::Ok);
    CHECK(copied.solve({100, 0.125}, result, emission) == Status::Ok);
    CHECK(result == original_result && emission == original_emission);
    CHECK(bytes(path) == preserved);
}

void check_analytical_paths() {
    for (const double rate : rates) {
        for (const double c : {300.0, 343.0, 380.0}) {
            for (const auto direction : std::array<std::int8_t, 2>{-1, 1}) {
                const MotionProfile profile{0.0, 0.0, 1.0, 1.0, direction};
                const MotionState seed{0.0, 0, 0.0};
                MotionSegment segment;
                CHECK(make_motion_segment(profile, seed, SpeedCommand::Chorale, 0, segment) == Status::Ok);
                MotionHistoryView history;
                CHECK(history.prepare(profile, seed, rate, {&segment, 1}, static_cast<std::uint64_t>(rate)) == Status::Ok);
                for (const double radius : {0.0, 0.02, 0.18, 1.0}) {
                    PreparedRetardedPath path;
                    CHECK(path.prepare(history, {}, radius, {{2.0, 0.0, 0.0}}, c, 0.75) == Status::Ok);
                    for (const SamplePosition observation : std::array<SamplePosition, 3>{{
                             {0, 0.0}, {2, 0.125}, {static_cast<std::int64_t>(rate), 0.0}}}) {
                        PathResult result;
                        SamplePosition emission;
                        CHECK(path.solve(observation, result, emission) == Status::Ok);
                        const double expected_distance = 2.0 - radius;
                        CHECK_NEAR(result.distance_m, expected_distance, 1.0e-15);
                        CHECK_NEAR(result.delay_s, expected_distance / c, 1.0e-14);
                        CHECK_NEAR(result.distance_gain, 0.75 / expected_distance, 1.0e-15);
                        CHECK(result.frequency_ratio == 1.0);
                        CHECK(result.radial_speed_m_s == 0.0);
                        CHECK(result.iterations >= 2 && result.iterations <= kMaxSolverIterations);
                        CHECK(std::abs(result.residual_s) <= 1.0e-14);
                        if (radius == 0.0) CHECK(result.iterations == 2);
                        maximum_residual = std::max(maximum_residual, std::abs(result.residual_s));
                        maximum_evaluations = std::max(maximum_evaluations, result.iterations);
                        ++solved_paths;
                    }
                }
                // Exact admitted clearance and maximum-distance endpoints.
                for (const double distance : {0.02, 20.0}) {
                    PreparedRetardedPath path;
                    CHECK(path.prepare(history, {-distance / 2.0, 0.0, 0.0}, 0.0,
                                       {{distance / 2.0, 0.0, 0.0}}, c, 1.0) == Status::Ok);
                    PathResult result;
                    SamplePosition emission;
                    CHECK(path.solve({0, 0.0}, result, emission) == Status::Ok);
                    CHECK_NEAR(result.delay_s, distance / c, 5.0e-16);
                    CHECK(result.iterations == 2);
                    ++solved_paths;
                }
            }
        }
    }
}

void check_second_endpoint_turn_overflow() {
    // This valid stopped-rate epoch can move backward less than half a radian
    // without borrowing a turn, but a larger prehistory query cannot. The
    // distance bracket is [1/300, 3/300] seconds: its first evaluation has phase
    // about 0.25, while its second would need phase -0.25 and one missing turn.
    // The specified 32-ulp widening is far smaller than either safety margin.
    const MotionProfile profile{75.0, 75.0, 1.0, 1.0, 1};
    const MotionState seed{0.5, std::numeric_limits<std::int64_t>::min(), 75.0};
    MotionSegment segment;
    CHECK(make_motion_segment(profile, seed, SpeedCommand::Chorale, 0, segment) == Status::Ok);
    MotionHistoryView history;
    CHECK(history.prepare(profile, seed, 48000.0, {&segment, 1}, 0) == Status::Ok);

    MotionState state;
    CHECK(history.state_at({-160, 0.0}, state) == Status::Ok);
    CHECK_NEAR(state.phase_rad, 0.25, 2.0e-15);
    CHECK(state.turns == seed.turns);
    const auto state_before = bytes(state);
    CHECK(history.state_at({-480, 0.0}, state) == Status::TimelineOverflow);
    CHECK(bytes(state) == state_before);

    PreparedRetardedPath path;
    CHECK(path.prepare(history, {}, 1.0, {{2.0, 0.0, 0.0}}, 300.0, 1.0) == Status::Ok);
    CHECK((path.bounds() == PathBounds{1.0, 3.0, 0.25}));
    PathResult result = sentinel_path();
    SamplePosition emission{12345, 0.875};
    const auto path_before = bytes(path);
    const auto history_before = bytes(history);
    const auto segment_before = bytes(segment);
    const auto result_before = bytes(result);
    const auto emission_before = bytes(emission);
    CHECK(path.solve({0, 0.0}, result, emission) == Status::TimelineOverflow);
    CHECK(bytes(path) == path_before);
    CHECK(bytes(history) == history_before);
    CHECK(bytes(segment) == segment_before);
    CHECK(bytes(result) == result_before);
    CHECK(bytes(emission) == emission_before);
    ++rejected_calls;
}

void check_constant_motion_roots() {
    // Independent long-double constant-speed Cartesian root. The complete
    // 80-digit ramp/history acceptance remains a separate R3 executable gate.
    for (const auto direction : std::array<std::int8_t, 2>{-1, 1}) {
        for (const double radius : {0.02, 0.18, 1.0}) {
            for (const double phase : {0.0, 0.5, 3.0}) {
                const double speed = radius == 1.0 ? 75.0 : 200.0;
                const MotionProfile profile{speed, speed, 1.0, 1.0, direction};
                const MotionState seed{phase, 0, speed};
                MotionSegment segment;
                CHECK(make_motion_segment(profile, seed, SpeedCommand::Chorale, 0, segment) == Status::Ok);
                MotionHistoryView history;
                CHECK(history.prepare(profile, seed, 48000.0, {&segment, 1}, 48000) == Status::Ok);
                PreparedRetardedPath path;
                CHECK(path.prepare(history, {}, radius, {{1.3, -0.4, 0.2}}, 300.0, 1.0) == Status::Ok);
                PathResult result;
                SamplePosition emission;
                CHECK(path.solve({6000, 0.0}, result, emission) == Status::Ok);
                long double lo = 0.0L;
                long double hi = 20.0L / 300.0L;
                const auto distance_at = [&](long double delay) {
                    const long double angle = static_cast<long double>(phase)
                        + direction * static_cast<long double>(speed) * (0.125L - delay);
                    const long double dx = 1.3L - radius * std::cos(angle);
                    const long double dy = -0.4L - radius * std::sin(angle);
                    return std::sqrt(dx * dx + dy * dy + 0.2L * 0.2L);
                };
                for (int iteration = 0; iteration < 96; ++iteration) {
                    const long double middle = (lo + hi) / 2.0L;
                    if (middle - distance_at(middle) / 300.0L < 0.0L) lo = middle;
                    else hi = middle;
                }
                const long double expected_delay = (lo + hi) / 2.0L;
                const double error = std::abs(result.delay_s - static_cast<double>(expected_delay));
                CHECK(error <= 2.0e-14);
                CHECK(std::abs(result.residual_s) <= 1.0e-14);
                CHECK(result.iterations <= kMaxSolverIterations);
                maximum_constant_delay_error = std::max(maximum_constant_delay_error, error);
                maximum_residual = std::max(maximum_residual, std::abs(result.residual_s));
                maximum_evaluations = std::max(maximum_evaluations, result.iterations);
                ++solved_paths;
            }
        }
    }
}

void check_command_crossing() {
    const MotionProfile profile{5.0, 40.0, 0.01, 0.1, 1};
    RotaryMotion motion;
    CHECK(motion.prepare(profile, 0.3, 5.0, SpeedCommand::Tremolo, 48000.0) == Status::Ok);
    const MotionState seed = motion.epoch_initial_state();
    std::array<MotionSegment, 2> segments{};
    segments[0] = motion.segment();
    CHECK(motion.apply_command(4800, SpeedCommand::Chorale) == Status::Ok);
    segments[1] = motion.segment();
    MotionHistoryView commanded;
    MotionHistoryView uninterrupted;
    CHECK(commanded.prepare(profile, seed, 48000.0, segments, 48000) == Status::Ok);
    CHECK(uninterrupted.prepare(profile, seed, 48000.0, {segments.data(), 1}, 48000) == Status::Ok);
    PreparedRetardedPath historical_path;
    PreparedRetardedPath original_path;
    CHECK(historical_path.prepare(commanded, {}, 0.18, {{1.0, 0.0, 0.1}}, 343.0, 1.0) == Status::Ok);
    CHECK(original_path.prepare(uninterrupted, {}, 0.18, {{1.0, 0.0, 0.1}}, 343.0, 1.0) == Status::Ok);
    for (const std::int64_t observation : {4799, 4800, 4801}) {
        PathResult historical;
        PathResult original;
        SamplePosition historical_emission;
        SamplePosition original_emission;
        CHECK(historical_path.solve({observation, 0.5}, historical, historical_emission) == Status::Ok);
        CHECK(original_path.solve({observation, 0.5}, original, original_emission) == Status::Ok);
        CHECK(historical_emission.frame > 0 && historical_emission.frame < 4800);
        CHECK(historical == original && historical_emission == original_emission);
        ++solved_paths;
    }
    PathResult later;
    SamplePosition later_emission;
    CHECK(historical_path.solve({5000, 0.0}, later, later_emission) == Status::Ok);
    CHECK(later_emission.frame >= 4800);
    MotionState historical_state;
    CHECK(commanded.state_at(later_emission, historical_state) == Status::Ok);
    CHECK(later.emission_phase_rad == historical_state.phase_rad);
}

} // namespace

int main() {
    check_history_queries();
    check_history_admission();
    check_capacity_and_day_fractions();
    check_geometry();
    check_path_transactions();
    check_analytical_paths();
    check_second_endpoint_turn_overflow();
    check_constant_motion_roots();
    check_command_crossing();
    std::cout << "Rotary propagation author checks: " << history_queries << " history queries, "
              << rejected_calls << " rejected calls, " << solved_paths << " solved paths; max constant-root error "
              << std::setprecision(17) << maximum_constant_delay_error << " s, max residual "
              << maximum_residual << " s, max evaluations " << maximum_evaluations << '\n';
    return 0;
}
