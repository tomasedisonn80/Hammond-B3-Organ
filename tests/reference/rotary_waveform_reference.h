#pragma once

// Offline R4 oracle. This file deliberately includes no Hammond production
// header and calls no production motion, geometry, root, history or cubic code.
// Its scalar is the implementation's long double, NOT an 80-digit type. See
// docs/ROTARY_WAVEFORM_ACCEPTANCE.md for precision and qualification boundaries.

#include <algorithm>
#include <array>
#include <cmath>
#include <complex>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <stdexcept>
#include <string_view>
#include <utility>
#include <vector>

namespace rotary_waveform_reference {

using Real = long double;

inline constexpr std::string_view kReferenceId = "independent-long-double-waveform-v1";
inline constexpr std::string_view kFixtureId = "rotary-r4-full-stream-v1";
inline constexpr std::string_view kContractId = "rotary-numerics-v1";
inline constexpr Real kTwoPi =
    6.283185307179586476925286766559005768394338798750211641949889L;
inline constexpr Real kReferenceResidualTarget = 5.0e-15L;
inline constexpr Real kReferenceResidualLimit = 1.0e-14L;
inline constexpr Real kNormalizedWaveformLimit = 2.0e-5L;
inline constexpr std::uint32_t kFullDurationSeconds = 10;
inline constexpr std::array<std::uint32_t, 4> kRates{44100, 48000, 96000, 192000};
inline constexpr std::array<std::uint32_t, 5> kFixedBlocks{1, 7, 64, 257, 4096};
inline constexpr std::array<std::uint32_t, 14> kIrregularBlocks{
    3, 1, 511, 7, 4096, 64, 257, 1023, 2, 389, 11, 2048, 5, 127};
inline constexpr std::uint64_t kSignalSeed = 0x726f746172792d34ULL;

struct Precision {
    int radix{std::numeric_limits<Real>::radix};
    int significand_bits{std::numeric_limits<Real>::digits};
    int decimal_digits{std::numeric_limits<Real>::digits10};
    int max_decimal_digits{std::numeric_limits<Real>::max_digits10};
    std::size_t scalar_bytes{sizeof(Real)};
    bool wider_than_double{std::numeric_limits<Real>::digits >
                           std::numeric_limits<double>::digits};
};

[[nodiscard]] inline bool supported_rate(std::uint32_t rate) noexcept {
    return std::find(kRates.begin(), kRates.end(), rate) != kRates.end();
}

inline void require(bool condition, const char* message) {
    if (!condition) throw std::runtime_error(message);
}

// Source/profile/input scalars are doubles so an explicit native adapter and
// this independent oracle receive exactly the same binary64 parameter values.
struct Vec3 { double x{}, y{}, z{}; };
struct RealVec3 { Real x{}, y{}, z{}; };
enum class Command : unsigned char { Chorale, Tremolo };

struct Rotor {
    Vec3 origin_m{};
    double radius_m{};
    double slow_rad_s{};
    double fast_rad_s{};
    double tau_up_s{};
    double tau_down_s{};
    int direction{1};
    double initial_phase_rad{};
    double initial_speed_rad_s{};
    Command initial_command{Command::Chorale};
};

struct Scene {
    std::array<Rotor, 2> rotors{}; // Horn, then Drum.
    std::array<Vec3, 2> microphones{}; // Left, then Right.
    double sound_speed_m_s{};
    double reference_distance_m{};
};

struct Event {
    std::int64_t frame{}; // Absolute boundary in this offline epoch.
    std::size_t rotor{};
    Command command{};
};

struct Position {
    std::int64_t frame{}; // Signed floor index, never truncation toward zero.
    Real fraction{};
};

[[nodiscard]] inline Position subtract_delay(Position observation, Real delay_s,
                                             std::uint32_t rate) {
    require(std::isfinite(delay_s) && delay_s >= 0, "invalid reference delay");
    require(std::isfinite(observation.fraction) && observation.fraction >= 0 &&
                observation.fraction < 1, "invalid split observation");
    const Real local = observation.fraction - delay_s * static_cast<Real>(rate);
    const Real whole = std::floor(local);
    require(whole >= -32768 && whole <= 0, "reference delay outside local range");
    Position result{observation.frame + static_cast<std::int64_t>(whole), local - whole};
    // Only normalize a rounded split representation; never clamp the delay.
    if (result.fraction >= 1) { ++result.frame; result.fraction -= 1; }
    if (result.fraction < 0) { --result.frame; result.fraction += 1; }
    return result;
}

struct MotionState { Real angle_rad{}, speed_rad_s{}; };
struct WrappedState { Real phase_rad{}; std::int64_t turns{}; Real speed_rad_s{}; };

[[nodiscard]] inline WrappedState wrap(MotionState state) {
    const Real turns = std::floor(state.angle_rad / kTwoPi);
    require(turns >= static_cast<Real>(std::numeric_limits<std::int64_t>::min()) &&
                turns < static_cast<Real>(std::numeric_limits<std::int64_t>::max()),
            "reference turns overflow");
    WrappedState result{state.angle_rad - turns * kTwoPi,
                        static_cast<std::int64_t>(turns), state.speed_rad_s};
    if (result.phase_rad >= kTwoPi) { result.phase_rad -= kTwoPi; ++result.turns; }
    if (result.phase_rad < 0) { result.phase_rad += kTwoPi; --result.turns; }
    return result;
}

// Integrated step response divided by elapsed time:
// 1 - (1-exp(-z))/z = z/2! - z^2/3! + z^3/4! - ... .
// This converges dynamically at Real precision; no production polynomial or
// coefficient table is imported. exp/expm1 are the platform long-double libm.
[[nodiscard]] inline Real average_step_response(Real z) {
    require(std::isfinite(z) && z >= 0, "invalid reference elapsed/tau");
    if (z == 0) return 0;
    if (z >= 0.5L) return 1 + std::expm1(-z) / z;
    Real term = z / 2;
    Real sum = term;
    for (unsigned factorial = 3; factorial <= 128; ++factorial) {
        term *= -z / static_cast<Real>(factorial);
        const Real next = sum + term;
        if (next == sum) return sum;
        sum = next;
    }
    throw std::runtime_error("reference integral series did not converge");
}

[[nodiscard]] inline MotionState segment_state(MotionState initial, Real target,
                                               Real tau_s, int direction,
                                               Real elapsed_s) {
    require(std::isfinite(elapsed_s) && elapsed_s >= 0 && tau_s > 0,
            "invalid reference segment query");
    if (elapsed_s == 0) return initial;
    const Real z = elapsed_s / tau_s;
    const Real difference = target - initial.speed_rad_s;
    Real speed{};
    Real displacement{};
    if (z < 0.5L) {
        speed = initial.speed_rad_s + difference * -std::expm1(-z);
        displacement = elapsed_s *
            (initial.speed_rad_s + difference * average_step_response(z));
    } else {
        speed = target + (initial.speed_rad_s - target) * std::exp(-z);
        displacement = target * elapsed_s +
            (initial.speed_rad_s - target) * tau_s * -std::expm1(-z);
    }
    return {initial.angle_rad + static_cast<Real>(direction) * displacement, speed};
}

class Timeline {
public:
    Timeline(const Rotor& rotor, std::uint32_t rate, const std::vector<Event>& events,
             std::size_t rotor_index)
        : rotor_(rotor), rate_(rate), initial_{rotor.initial_phase_rad,
                                              rotor.initial_speed_rad_s} {
        require(supported_rate(rate) && rotor_index < 2, "invalid reference timeline");
        require(rotor.direction == -1 || rotor.direction == 1, "invalid reference direction");
        require(std::isfinite(rotor.slow_rad_s) && std::isfinite(rotor.fast_rad_s) &&
                    rotor.slow_rad_s >= 0 && rotor.slow_rad_s <= rotor.fast_rad_s &&
                    rotor.fast_rad_s <= 200 && std::isfinite(rotor.initial_speed_rad_s) &&
                    rotor.initial_speed_rad_s >= 0 && rotor.initial_speed_rad_s <= 200,
                "invalid reference speeds");
        require(std::isfinite(rotor.initial_phase_rad) && rotor.initial_phase_rad >= 0 &&
                    static_cast<Real>(rotor.initial_phase_rad) < kTwoPi &&
                    std::isfinite(rotor.tau_up_s) && std::isfinite(rotor.tau_down_s) &&
                    rotor.tau_up_s >= 0.001 && rotor.tau_up_s <= 60 &&
                    rotor.tau_down_s >= 0.001 && rotor.tau_down_s <= 60,
                "invalid reference phase/time constants");
        segments_.push_back(anchor(0, initial_, rotor.initial_command));
        std::int64_t previous = 0;
        for (const Event& event : events) {
            require(event.frame >= previous && event.frame <= 86400LL * rate &&
                        event.rotor < 2 && valid_command(event.command),
                    "invalid reference event sequence");
            previous = event.frame;
            if (event.rotor != rotor_index || event.command == segments_.back().command)
                continue;
            const MotionState at_boundary = at({event.frame, 0});
            const Segment next = anchor(event.frame, at_boundary, event.command);
            if (event.frame == segments_.back().frame) segments_.back() = next;
            else segments_.push_back(next);
        }
    }

    [[nodiscard]] MotionState at(Position time) const {
        require(std::isfinite(time.fraction) && time.fraction >= 0 && time.fraction < 1 &&
                    time.frame >= -86400LL * rate_ && time.frame <= 86400LL * rate_ &&
                    (time.frame != 86400LL * rate_ || time.fraction == 0),
                "invalid reference motion position");
        if (time.frame < 0) {
            const Real seconds = (static_cast<Real>(time.frame) + time.fraction) / rate_;
            return {initial_.angle_rad + rotor_.direction * initial_.speed_rad_s * seconds,
                    initial_.speed_rad_s};
        }
        const Segment& segment = segment_at(time.frame);
        const Real elapsed = (static_cast<Real>(time.frame - segment.frame) +
                              time.fraction) / rate_;
        return segment_state(segment.initial, segment.target, segment.tau,
                             rotor_.direction, elapsed);
    }

    [[nodiscard]] Command command_at(std::int64_t frame) const {
        return frame < 0 ? rotor_.initial_command : segment_at(frame).command;
    }

    [[nodiscard]] std::size_t segment_count() const noexcept { return segments_.size(); }

private:
    struct Segment {
        std::int64_t frame{};
        MotionState initial{};
        Command command{};
        Real target{}, tau{};
    };

    [[nodiscard]] static bool valid_command(Command command) noexcept {
        return command == Command::Chorale || command == Command::Tremolo;
    }

    [[nodiscard]] Segment anchor(std::int64_t frame, MotionState state,
                                 Command command) const {
        require(valid_command(command), "invalid reference command");
        const Real target = command == Command::Chorale ? rotor_.slow_rad_s : rotor_.fast_rad_s;
        return {frame, state, command, target,
                target >= state.speed_rad_s ? rotor_.tau_up_s : rotor_.tau_down_s};
    }

    [[nodiscard]] const Segment& segment_at(std::int64_t frame) const {
        const auto after = std::upper_bound(segments_.begin(), segments_.end(), frame,
            [](std::int64_t query, const Segment& segment) { return query < segment.frame; });
        require(after != segments_.begin(), "reference segment unavailable");
        return *(after - 1);
    }

    Rotor rotor_;
    std::uint32_t rate_{};
    MotionState initial_{};
    std::vector<Segment> segments_;
};

struct Bounds { Real minimum_m{}, maximum_m{}, beta{}; };

[[nodiscard]] inline Bounds path_bounds(const Rotor& rotor, Vec3 mic, Real sound_speed) {
    const auto finite_coordinate = [](double value) {
        return std::isfinite(value) && std::abs(value) <= 10;
    };
    require(finite_coordinate(rotor.origin_m.x) && finite_coordinate(rotor.origin_m.y) &&
                finite_coordinate(rotor.origin_m.z) && finite_coordinate(mic.x) &&
                finite_coordinate(mic.y) && finite_coordinate(mic.z) &&
                std::isfinite(rotor.radius_m) && rotor.radius_m >= 0 && rotor.radius_m <= 1 &&
                std::isfinite(sound_speed) && sound_speed >= 300 && sound_speed <= 380,
            "invalid reference geometry");
    const Real x = static_cast<Real>(mic.x) - rotor.origin_m.x;
    const Real y = static_cast<Real>(mic.y) - rotor.origin_m.y;
    const Real z = static_cast<Real>(mic.z) - rotor.origin_m.z;
    const Real horizontal = std::sqrt(x * x + y * y);
    const Real inner = horizontal - rotor.radius_m;
    const Real outer = horizontal + rotor.radius_m;
    const Real maximum_speed = std::max({rotor.initial_speed_rad_s, rotor.slow_rad_s,
                                          rotor.fast_rad_s});
    const Bounds result{std::sqrt(inner * inner + z * z),
                        std::sqrt(outer * outer + z * z),
                        rotor.radius_m * maximum_speed / sound_speed};
    require(result.minimum_m >= static_cast<Real>(0.02) && result.maximum_m <= 20 &&
                result.beta <= 0.25L, "reference scene outside full-orbit domain");
    return result;
}

struct Geometry {
    RealVec3 position_m{}, velocity_m_s{};
    Real distance_m{}, radial_speed_m_s{}, frequency_ratio{};
};

[[nodiscard]] inline Geometry cartesian_geometry(const Rotor& rotor, Vec3 microphone,
                                                  MotionState motion, Real sound_speed) {
    const Real sine = std::sin(motion.angle_rad);
    const Real cosine = std::cos(motion.angle_rad);
    const Real radius = rotor.radius_m;
    const Real signed_speed = rotor.direction * motion.speed_rad_s;
    Geometry result;
    result.position_m = {rotor.origin_m.x + radius * cosine,
                         rotor.origin_m.y + radius * sine, rotor.origin_m.z};
    result.velocity_m_s = {-radius * signed_speed * sine,
                           radius * signed_speed * cosine, 0};
    const Real x = static_cast<Real>(microphone.x) - result.position_m.x;
    const Real y = static_cast<Real>(microphone.y) - result.position_m.y;
    const Real z = static_cast<Real>(microphone.z) - result.position_m.z;
    result.distance_m = std::sqrt(x * x + y * y + z * z);
    require(std::isfinite(result.distance_m) && result.distance_m > 0,
            "invalid reference Cartesian distance");
    result.radial_speed_m_s =
        (x * result.velocity_m_s.x + y * result.velocity_m_s.y) / result.distance_m;
    result.frequency_ratio = 1 / (1 - result.radial_speed_m_s / sound_speed);
    return result;
}

enum class SolveMethod { ContractiveBracket, PureBisection };

struct Path {
    Position emission{};
    MotionState motion{};
    Geometry geometry{};
    Real delay_s{}, residual_s{}, distance_gain{}, bracket_width_s{};
    unsigned evaluations{}, contraction_steps{}, bisections{};
};

// H(d)=r(t-d)/c has |H'(d)|<=beta<=1/4, independently of native Newton code.
// The global analytical bracket is retained and every candidate is checked.
// The fast route uses at most 24 contraction steps; up to 96 bisections form
// a bounded fallback. PureBisection is a separate cross-check route.
[[nodiscard]] inline Path solve_path(const Timeline& timeline, const Rotor& rotor,
                                     Vec3 microphone, Bounds bounds, Position observation,
                                     std::uint32_t rate, Real sound_speed,
                                     Real reference_distance,
                                     SolveMethod method = SolveMethod::ContractiveBracket,
                                     Real target = kReferenceResidualTarget) {
    require(std::isfinite(target) && target > 0 && target <= kReferenceResidualLimit,
            "invalid reference residual target");
    const Real margin = 64 * std::numeric_limits<Real>::epsilon() *
                        std::max(1.0L, bounds.maximum_m);
    Real lo = std::max(0.0L, bounds.minimum_m - margin) / sound_speed;
    Real hi = (bounds.maximum_m + margin) / sound_speed;
    unsigned evaluations = 0;
    const auto evaluate = [&](Real delay) {
        Path path;
        path.delay_s = delay;
        path.emission = subtract_delay(observation, delay, rate);
        path.motion = timeline.at(path.emission);
        path.geometry = cartesian_geometry(rotor, microphone, path.motion, sound_speed);
        path.residual_s = delay - path.geometry.distance_m / sound_speed;
        path.distance_gain = reference_distance / path.geometry.distance_m;
        ++evaluations;
        require(std::isfinite(path.residual_s), "nonfinite reference root residual");
        return path;
    };
    Path low = evaluate(lo);
    Path high = evaluate(hi);
    require(low.residual_s <= 0 && high.residual_s >= 0,
            "reference analytical bracket does not contain root");
    Path best = std::abs(low.residual_s) < std::abs(high.residual_s) ? low : high;
    Real candidate = (lo + hi) / 2;
    unsigned contractions = 0;
    unsigned bisections = 0;
    for (unsigned step = 0; std::abs(best.residual_s) > target && step < 120; ++step) {
        const bool contraction = method == SolveMethod::ContractiveBracket && step < 24;
        if (!contraction) {
            if (bisections == 96) break;
            candidate = lo + (hi - lo) / 2;
        }
        if (!(candidate > lo && candidate < hi)) break;
        const Path current = evaluate(candidate);
        if (contraction) ++contractions;
        else ++bisections;
        if (std::abs(current.residual_s) < std::abs(best.residual_s)) best = current;
        if (current.residual_s < 0) lo = candidate;
        else hi = candidate;
        if (contraction) {
            const Real mapped = current.geometry.distance_m / sound_speed;
            candidate = mapped > lo && mapped < hi ? mapped : lo + (hi - lo) / 2;
        }
    }
    require(std::abs(best.residual_s) <= target && best.delay_s > 0,
            "reference root did not meet its frozen residual target");
    require(best.emission.frame < observation.frame ||
                (best.emission.frame == observation.frame &&
                 best.emission.fraction < observation.fraction),
            "reference emission is not causal");
    best.evaluations = evaluations;
    best.contraction_steps = contractions;
    best.bisections = bisections;
    best.bracket_width_s = hi - lo;
    return best;
}

[[nodiscard]] inline std::array<Real, 4> cubic_weights(Real fraction) {
    require(std::isfinite(fraction) && fraction >= 0 && fraction <= 1,
            "invalid reference cubic fraction");
    constexpr std::array<int, 4> nodes{-1, 0, 1, 2};
    std::array<Real, 4> weights{};
    for (std::size_t j = 0; j < nodes.size(); ++j) {
        weights[j] = 1;
        for (std::size_t other = 0; other < nodes.size(); ++other) {
            if (j != other)
                weights[j] *= (fraction - nodes[other]) /
                              static_cast<Real>(nodes[j] - nodes[other]);
        }
    }
    return weights;
}

[[nodiscard]] inline Real cubic(const std::array<Real, 4>& values, Real fraction) {
    const auto weights = cubic_weights(fraction);
    Real result = 0;
    for (std::size_t j = 0; j < values.size(); ++j) result += weights[j] * values[j];
    return result;
}

[[nodiscard]] inline Real bounded_polynomial(unsigned degree, Real x) {
    require(degree <= 3, "reference polynomial degree exceeds three");
    Real value = 1;
    for (unsigned power = 0; power < degree; ++power) value *= x / 2;
    return value;
}

[[nodiscard]] inline std::complex<Real> cubic_frequency_response(Real fraction,
                                                                Real cycles_per_sample) {
    const auto weights = cubic_weights(fraction);
    std::complex<Real> response{0, 0};
    for (std::size_t j = 0; j < weights.size(); ++j) {
        const Real phase = kTwoPi * cycles_per_sample * (static_cast<Real>(j) - 1);
        response += weights[j] * std::complex<Real>{std::cos(phase), std::sin(phase)};
    }
    return response;
}

[[nodiscard]] inline std::complex<Real> ideal_frequency_response(Real fraction,
                                                                Real cycles_per_sample) {
    const Real phase = kTwoPi * cycles_per_sample * fraction;
    return {std::cos(phase), std::sin(phase)};
}

struct Frame {
    std::array<Real, 2> output{};
    std::array<Path, 4> paths{}; // Left-Horn, Left-Drum, Right-Horn, Right-Drum.
};

class Renderer {
public:
    Renderer(Scene scene, std::uint32_t rate, const std::vector<Event>& events)
        : scene_(std::move(scene)), rate_(rate),
          timelines_{Timeline(scene_.rotors[0], rate, events, 0),
                     Timeline(scene_.rotors[1], rate, events, 1)} {
        require(std::isfinite(scene_.reference_distance_m) && scene_.reference_distance_m >= 0.02 &&
                    scene_.reference_distance_m <= 10, "invalid reference gain distance");
        for (std::size_t channel = 0; channel < 2; ++channel)
            for (std::size_t rotor = 0; rotor < 2; ++rotor)
                bounds_[channel][rotor] = path_bounds(scene_.rotors[rotor],
                    scene_.microphones[channel], scene_.sound_speed_m_s);
    }

    // The callback returns a double input at (rotor, absolute nonnegative frame).
    // Inputs are read directly from their independent definition, not from any
    // production ring. Negative-time zero and future support checks are explicit.
    template<class Input>
    [[nodiscard]] Frame at(std::int64_t frame, Input&& input,
                           SolveMethod method = SolveMethod::ContractiveBracket,
                           Real target = kReferenceResidualTarget) const {
        require(frame >= 0 && frame < 86400LL * rate_, "invalid reference render frame");
        Frame result;
        const Position observation{frame - 2, 0};
        for (std::size_t channel = 0; channel < 2; ++channel) {
            for (std::size_t rotor = 0; rotor < 2; ++rotor) {
                Path& path = result.paths[channel * 2 + rotor];
                path = solve_path(timelines_[rotor], scene_.rotors[rotor],
                    scene_.microphones[channel], bounds_[channel][rotor], observation, rate_,
                    scene_.sound_speed_m_s, scene_.reference_distance_m, method, target);
                std::array<Real, 4> values{};
                for (std::size_t j = 0; j < values.size(); ++j) {
                    const std::int64_t source_frame = path.emission.frame +
                                                     static_cast<std::int64_t>(j) - 1;
                    require(source_frame <= frame, "reference requires an unavailable future sample");
                    if (source_frame < 0) continue;
                    const double value = input(rotor, source_frame);
                    require(std::isfinite(value) && std::abs(value) <= 1,
                            "reference input violates normalized bound");
                    values[j] = value;
                }
                result.output[channel] += path.distance_gain * cubic(values, path.emission.fraction);
            }
        }
        return result;
    }

    [[nodiscard]] Real normalization(std::size_t channel) const {
        require(channel < 2, "invalid reference output channel");
        return scene_.reference_distance_m / bounds_[channel][0].minimum_m +
               scene_.reference_distance_m / bounds_[channel][1].minimum_m;
    }

    [[nodiscard]] const Timeline& timeline(std::size_t rotor) const {
        require(rotor < 2, "invalid reference rotor");
        return timelines_[rotor];
    }

private:
    Scene scene_;
    std::uint32_t rate_{};
    std::array<Timeline, 2> timelines_;
    std::array<std::array<Bounds, 2>, 2> bounds_{};
};

// These are synthetic numerical fixtures, not measured Leslie specifications.
[[nodiscard]] inline Scene full_scene() {
    return {{{{{-0.12, 0.07, 1.10}, 0.18, 4.2, 40.5, 0.67, 1.10, 1,
                0.31, 7.25, Command::Chorale},
               {{0.09, -0.05, 0.35}, 0.22, 3.1, 31.0, 1.40, 2.60, -1,
                4.40, 5.75, Command::Chorale}}},
             {{{1.35, -0.80, 1.25}, {-1.20, -0.65, 0.90}}}, 343.0, 1.0};
}

[[nodiscard]] inline std::vector<Event> full_events(std::uint32_t rate) {
    require(supported_rate(rate), "unsupported full-fixture rate");
    const std::int64_t fs = rate;
    const auto c = Command::Chorale;
    const auto t = Command::Tremolo;
    return {{0, 0, t}, {0, 0, c}, {1, 1, t}, {6, 0, t}, {7, 0, c}, {8, 0, t},
            {63, 1, c}, {64, 1, t}, {65, 1, c}, {256, 0, c}, {257, 0, t}, {258, 0, c},
            {4095, 0, t}, {4096, 1, t}, {4097, 0, c},
            {fs / 2 - 1, 0, t}, {fs / 2, 1, c}, {fs / 2 + 1, 1, t},
            {2 * fs, 0, t}, {2 * fs, 1, t}, {3 * fs + 17, 0, c}, {4 * fs - 1, 1, c},
            {4 * fs, 0, t}, {4 * fs, 0, c}, {4 * fs, 0, t}, {5 * fs + 64, 1, t},
            {6 * fs - 1, 0, c}, {6 * fs, 1, c}, {6 * fs + 1, 0, t},
            {7 * fs + 257, 1, t}, {8 * fs - 1, 0, c}, {8 * fs, 1, c},
            {9 * fs, 0, t}, {10 * fs, 0, c}, {10 * fs, 1, t}};
}

[[nodiscard]] inline std::uint64_t mix64(std::uint64_t value) noexcept {
    value += 0x9e3779b97f4a7c15ULL;
    value = (value ^ (value >> 30)) * 0xbf58476d1ce4e5b9ULL;
    value = (value ^ (value >> 27)) * 0x94d049bb133111ebULL;
    return value ^ (value >> 31);
}

[[nodiscard]] inline double full_input(std::uint32_t rate, std::size_t rotor,
                                       std::int64_t frame) {
    require(supported_rate(rate) && rotor < 2, "invalid full-fixture input request");
    if (frame < 0) return 0;
    const std::int64_t fs = rate;
    if (frame < 2 * fs) {
        if (rotor == 0 && frame == 0) return 1;
        if (rotor == 1 && frame == fs / 2) return -1;
        if (rotor == 0 && frame == fs) return -0.5;
        if (rotor == 1 && frame == 3 * fs / 2) return 0.75;
        return 0;
    }
    if (frame >= 9 * fs || (frame >= 6 * fs && frame < 6 * fs + fs / 8)) return 0;
    const std::uint64_t n = static_cast<std::uint64_t>(frame);
    const std::uint64_t bits = mix64(n ^ kSignalSeed ^
        (rotor == 0 ? 0x484f524eULL : 0x4452554dULL));
    const auto noise_integer = static_cast<std::int32_t>((bits >> 32) & 0xffffU) - 32768;
    const double noise = static_cast<double>(noise_integer) / 32768.0;
    const auto phase = static_cast<std::int32_t>((n * (rotor == 0 ? 5U : 7U) +
                                                (rotor == 0 ? 0U : 257U)) % 2048U);
    const double triangle = static_cast<double>(phase < 1024 ? 2 * phase - 1024
                                                             : 3072 - 2 * phase) / 1024.0;
    const double square = (n / (rotor == 0 ? 31U : 43U)) % 2U == 0 ? 1.0 : -1.0;
    return rotor == 0 ? 0.5 * noise + 0.25 * triangle + 0.125 * square
                      : 0.375 * noise + 0.375 * triangle + 0.125 * square;
}

struct ErrorSummary {
    std::uint64_t count{};
    Real maximum_absolute{}, maximum_normalized{}, sum_squared{}, sum_squared_normalized{};
    std::int64_t worst_frame{-1};
    double worst_actual{};
    Real worst_reference{};

    void observe(std::int64_t frame, double actual, Real reference, Real normalization) {
        require(std::isfinite(actual) && std::isfinite(reference) &&
                    std::isfinite(normalization) && normalization > 0,
                "invalid waveform comparison");
        const Real error = std::abs(static_cast<Real>(actual) - reference);
        const Real normalized = error / normalization;
        ++count;
        sum_squared += error * error;
        sum_squared_normalized += normalized * normalized;
        if (worst_frame < 0 || error > maximum_absolute) {
            maximum_absolute = error;
            worst_frame = frame;
            worst_actual = actual;
            worst_reference = reference;
        }
        maximum_normalized = std::max(maximum_normalized, normalized);
    }

    [[nodiscard]] Real rms() const { return count == 0 ? 0 : std::sqrt(sum_squared / count); }
    [[nodiscard]] Real normalized_rms() const {
        return count == 0 ? 0 : std::sqrt(sum_squared_normalized / count);
    }
    [[nodiscard]] bool passes() const noexcept {
        return count > 0 && maximum_normalized <= kNormalizedWaveformLimit;
    }
};

} // namespace rotary_waveform_reference
