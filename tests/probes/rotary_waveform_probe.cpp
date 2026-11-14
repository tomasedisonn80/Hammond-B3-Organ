#include "hammond/RotaryRenderer.h"
#include "reference/rotary_waveform_reference.h"

#include <algorithm>
#include <array>
#include <bit>
#include <cfenv>
#include <chrono>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <limits>
#include <locale>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

// Test-only native adapter. Expected values come solely from the independent
// reference. No native state, root, gain, ring sample or output enters it.
// stdout contains one final JSON object. Progress is confined to stderr.
namespace {
namespace native = hammond::rotary;
namespace reference = rotary_waveform_reference;
using Real = reference::Real;
using Clock = std::chrono::steady_clock;

constexpr std::uint64_t kSmokeFrames = 4097;
constexpr std::string_view kSmokeFixture = "rotary-r4-shifted-input-smoke-v1";
constexpr std::size_t kPartitionCount = 6;
constexpr Real kConvergenceLimit = 2.0e-14L;
constexpr Real kPureBisectionTarget = 1.0e-16L;
constexpr Real kAngleAbsoluteLimit = 5.0e-12L;
constexpr Real kAngleRelativeLimit = 4.0e-15L;
constexpr Real kSpeedAbsoluteLimit = 5.0e-12L;
constexpr Real kSpeedRelativeLimit = 4.0e-14L;
// Reference channel-major -> native rotor-major: HL,DL,HR,DR -> HL,HR,DL,DR.
constexpr std::array<std::size_t, 4> kReferenceToNativePath{0, 2, 1, 3};

#ifndef HAMMOND_WAVEFORM_BUILD_CONFIG
#define HAMMOND_WAVEFORM_BUILD_CONFIG "not_embedded"
#endif
#ifndef HAMMOND_WAVEFORM_BUILD_FLAGS
#define HAMMOND_WAVEFORM_BUILD_FLAGS "not_embedded_runner_must_record_actual_flags"
#endif

void require(bool condition, const std::string& message) {
    if (!condition) throw std::runtime_error(message);
}

double seconds_since(Clock::time_point start) {
    return std::chrono::duration<double>(Clock::now() - start).count();
}

std::uint64_t bits(double value) noexcept {
    return std::bit_cast<std::uint64_t>(value);
}

std::string hex64(std::uint64_t value) {
    std::ostringstream output;
    output << std::hex << std::setfill('0') << std::setw(16) << value;
    return output.str();
}

void quoted(std::ostream& output, std::string_view value) {
    constexpr char digits[] = "0123456789abcdef";
    output << '"';
    for (const char character : value) {
        const auto byte = static_cast<unsigned char>(character);
        switch (character) {
        case '"': output << "\\\""; break;
        case '\\': output << "\\\\"; break;
        case '\b': output << "\\b"; break;
        case '\f': output << "\\f"; break;
        case '\n': output << "\\n"; break;
        case '\r': output << "\\r"; break;
        case '\t': output << "\\t"; break;
        default:
            if (byte < 0x20U) output << "\\u00" << digits[byte >> 4U] << digits[byte & 15U];
            else output << character;
        }
    }
    output << '"';
}

// Test-local SHA-256. Stream records have explicitly little-endian binary64
// scalars, independent of host byte order. Three known vectors are checked.
class Sha256 {
public:
    void byte(std::uint8_t value) {
        pending_[used_++] = value;
        ++bytes_;
        if (used_ == pending_.size()) { compress(); used_ = 0; }
    }

    void binary64(double value) {
        const std::uint64_t representation = bits(value);
        for (unsigned index = 0; index < 8; ++index)
            byte(static_cast<std::uint8_t>(representation >> (8U * index)));
    }

    [[nodiscard]] std::string digest() const {
        Sha256 final = *this;
        const std::uint64_t length_bits = final.bytes_ * 8U;
        final.byte(0x80U);
        while (final.used_ != 56) final.byte(0);
        for (unsigned index = 0; index < 8; ++index)
            final.byte(static_cast<std::uint8_t>(length_bits >> (56U - 8U * index)));
        std::ostringstream output;
        output << std::hex << std::setfill('0');
        for (const auto word : final.state_) output << std::setw(8) << word;
        return output.str();
    }

private:
    void compress() {
        constexpr std::array<std::uint32_t, 64> constants{
            0x428a2f98U,0x71374491U,0xb5c0fbcfU,0xe9b5dba5U,0x3956c25bU,0x59f111f1U,0x923f82a4U,0xab1c5ed5U,
            0xd807aa98U,0x12835b01U,0x243185beU,0x550c7dc3U,0x72be5d74U,0x80deb1feU,0x9bdc06a7U,0xc19bf174U,
            0xe49b69c1U,0xefbe4786U,0x0fc19dc6U,0x240ca1ccU,0x2de92c6fU,0x4a7484aaU,0x5cb0a9dcU,0x76f988daU,
            0x983e5152U,0xa831c66dU,0xb00327c8U,0xbf597fc7U,0xc6e00bf3U,0xd5a79147U,0x06ca6351U,0x14292967U,
            0x27b70a85U,0x2e1b2138U,0x4d2c6dfcU,0x53380d13U,0x650a7354U,0x766a0abbU,0x81c2c92eU,0x92722c85U,
            0xa2bfe8a1U,0xa81a664bU,0xc24b8b70U,0xc76c51a3U,0xd192e819U,0xd6990624U,0xf40e3585U,0x106aa070U,
            0x19a4c116U,0x1e376c08U,0x2748774cU,0x34b0bcb5U,0x391c0cb3U,0x4ed8aa4aU,0x5b9cca4fU,0x682e6ff3U,
            0x748f82eeU,0x78a5636fU,0x84c87814U,0x8cc70208U,0x90befffaU,0xa4506cebU,0xbef9a3f7U,0xc67178f2U};
        std::array<std::uint32_t, 64> words{};
        for (std::size_t index = 0; index < 16; ++index) {
            const auto offset = index * 4;
            words[index] = (static_cast<std::uint32_t>(pending_[offset]) << 24U)
                         | (static_cast<std::uint32_t>(pending_[offset + 1]) << 16U)
                         | (static_cast<std::uint32_t>(pending_[offset + 2]) << 8U)
                         | static_cast<std::uint32_t>(pending_[offset + 3]);
        }
        for (std::size_t index = 16; index < words.size(); ++index) {
            const auto a = words[index - 15];
            const auto b = words[index - 2];
            const auto first = std::rotr(a, 7) ^ std::rotr(a, 18) ^ (a >> 3U);
            const auto second = std::rotr(b, 17) ^ std::rotr(b, 19) ^ (b >> 10U);
            words[index] = words[index - 16] + first + words[index - 7] + second;
        }
        auto [a, b, c, d, e, f, g, h] = state_;
        for (std::size_t index = 0; index < words.size(); ++index) {
            const auto upper = std::rotr(e, 6) ^ std::rotr(e, 11) ^ std::rotr(e, 25);
            const auto choose = (e & f) ^ (~e & g);
            const auto first = h + upper + choose + constants[index] + words[index];
            const auto lower = std::rotr(a, 2) ^ std::rotr(a, 13) ^ std::rotr(a, 22);
            const auto majority = (a & b) ^ (a & c) ^ (b & c);
            const auto second = lower + majority;
            h = g; g = f; f = e; e = d + first;
            d = c; c = b; b = a; a = first + second;
        }
        const std::array<std::uint32_t, 8> working{a, b, c, d, e, f, g, h};
        for (std::size_t index = 0; index < state_.size(); ++index) state_[index] += working[index];
    }

    std::array<std::uint32_t, 8> state_{
        0x6a09e667U,0xbb67ae85U,0x3c6ef372U,0xa54ff53aU,
        0x510e527fU,0x9b05688cU,0x1f83d9abU,0x5be0cd19U};
    std::array<std::uint8_t, 64> pending_{};
    std::size_t used_{};
    std::uint64_t bytes_{};
};

bool hash_self_check() {
    Sha256 hash;
    if (hash.digest() != "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855") return false;
    for (const char character : std::string_view("abc")) hash.byte(static_cast<std::uint8_t>(character));
    if (hash.digest() != "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad") return false;
    Sha256 long_hash;
    for (const char character : std::string_view("abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq"))
        long_hash.byte(static_cast<std::uint8_t>(character));
    return long_hash.digest() == "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1";
}

struct FailedFrames {
    std::uint64_t count{};
    std::int64_t first{-1};
    std::int64_t last{-1};
    std::uint64_t total_frames{};
    std::vector<std::uint8_t> bitmap;

    void observe(std::uint64_t frame, std::uint64_t frames) {
        if (bitmap.empty()) {
            total_frames = frames;
            bitmap.resize(static_cast<std::size_t>((frames + 7U) / 8U), 0);
        }
        require(frame < frames && frames == total_frames, "invalid failure bitmap coordinate");
        ++count;
        if (first < 0) first = static_cast<std::int64_t>(frame);
        last = static_cast<std::int64_t>(frame);
        bitmap[static_cast<std::size_t>(frame / 8U)] |= static_cast<std::uint8_t>(1U << (frame % 8U));
    }
};

struct PathMetrics {
    std::uint64_t count{};
    Real maximum_residual_s{};
    unsigned maximum_evaluations{};
    unsigned maximum_contraction_steps{};
    unsigned maximum_bisections{};
    std::int64_t worst_frame{-1};
    std::size_t worst_reference_path{};

    void observe(std::uint64_t frame, std::size_t path_index, const reference::Path& path) {
        ++count;
        const auto absolute = std::abs(path.residual_s);
        if (worst_frame < 0 || absolute > maximum_residual_s) {
            maximum_residual_s = absolute;
            worst_frame = static_cast<std::int64_t>(frame);
            worst_reference_path = path_index;
        }
        maximum_evaluations = std::max(maximum_evaluations, path.evaluations);
        maximum_contraction_steps = std::max(maximum_contraction_steps, path.contraction_steps);
        maximum_bisections = std::max(maximum_bisections, path.bisections);
    }
};

struct SignalRegion {
    std::uint64_t frame_count{};
    std::array<std::uint64_t, 2> input_nonzero{};
    std::array<std::uint64_t, 2> actual_nonzero{};
    std::array<std::uint64_t, 2> reference_nonzero{};
    std::array<std::uint64_t, 2> nonzero_comparison_count{};
};

struct ChannelMetrics {
    reference::ErrorSummary error;
    FailedFrames failures;
    Real normalization{};
};

struct BitComparison {
    std::uint64_t compared{};
    std::uint64_t equal{};
    FailedFrames failures;
    Real maximum_absolute{};
    std::int64_t worst_frame{-1};
    double worst_actual{};
    double worst_canonical{};

    void observe(std::uint64_t frame, std::uint64_t frames, double actual, double canonical) {
        ++compared;
        if (bits(actual) == bits(canonical)) { ++equal; return; }
        failures.observe(frame, frames);
        const auto error = std::abs(static_cast<Real>(actual) - canonical);
        if (worst_frame < 0 || error > maximum_absolute) {
            maximum_absolute = error;
            worst_frame = static_cast<std::int64_t>(frame);
            worst_actual = actual;
            worst_canonical = canonical;
        }
    }
};

struct FieldComparison {
    std::uint64_t compared{};
    std::vector<std::string> mismatches;
    template<class T> void value(std::string name, T actual, T canonical) {
        ++compared;
        if (actual != canonical) mismatches.push_back(std::move(name));
    }
    void scalar(std::string name, double actual, double canonical) {
        value(std::move(name), bits(actual), bits(canonical));
    }
    void motion(const std::string& prefix, const native::MotionState& actual,
                const native::MotionState& canonical) {
        scalar(prefix + ".phase_rad", actual.phase_rad, canonical.phase_rad);
        value(prefix + ".turns", actual.turns, canonical.turns);
        scalar(prefix + ".speed_rad_s", actual.speed_rad_s, canonical.speed_rad_s);
    }
    void position(const std::string& prefix, native::SamplePosition actual,
                  native::SamplePosition canonical) {
        value(prefix + ".frame", actual.frame, canonical.frame);
        scalar(prefix + ".fraction", actual.fraction, canonical.fraction);
    }
};

FieldComparison compare_state(const native::RendererState& actual,
                              const native::RendererState& canonical) {
    FieldComparison result;
    result.value("prepared", actual.prepared, canonical.prepared);
    result.scalar("sample_rate", actual.sample_rate, canonical.sample_rate);
    result.value("frame", actual.frame, canonical.frame);
    result.value("max_frame", actual.max_frame, canonical.max_frame);
    for (std::size_t rotor = 0; rotor < 2; ++rotor) {
        const auto suffix = "[" + std::to_string(rotor) + "]";
        result.motion("motion" + suffix, actual.motion[rotor], canonical.motion[rotor]);
        result.motion("epoch_initial" + suffix, actual.epoch_initial[rotor], canonical.epoch_initial[rotor]);
        result.value("commands" + suffix, actual.commands[rotor], canonical.commands[rotor]);
        const auto prefix = "segments" + suffix;
        const auto& left = actual.segments[rotor];
        const auto& right = canonical.segments[rotor];
        result.value(prefix + ".anchor_frame", left.anchor_frame, right.anchor_frame);
        result.motion(prefix + ".initial", left.initial, right.initial);
        result.scalar(prefix + ".target_rad_s", left.target_rad_s, right.target_rad_s);
        result.scalar(prefix + ".tau_s", left.tau_s, right.tau_s);
        result.value(prefix + ".direction", left.direction, right.direction);
    }
    return result;
}

FieldComparison compare_diagnostics(const native::RendererDiagnostics& actual,
                                    const native::RendererDiagnostics& canonical) {
    FieldComparison result;
    result.value("has_rendered_sample", actual.has_rendered_sample, canonical.has_rendered_sample);
    result.value("last_input_frame", actual.last_input_frame, canonical.last_input_frame);
    result.position("last_observation", actual.last_observation, canonical.last_observation);
    result.scalar("max_solver_residual_s", actual.max_solver_residual_s, canonical.max_solver_residual_s);
    result.value("max_solver_iterations", actual.max_solver_iterations, canonical.max_solver_iterations);
    for (std::size_t path = 0; path < 4; ++path) {
        const auto prefix = "last_paths[" + std::to_string(path) + "]";
        const auto& left = actual.last_paths[path];
        const auto& right = canonical.last_paths[path];
        result.scalar(prefix + ".delay_s", left.delay_s, right.delay_s);
        result.scalar(prefix + ".distance_m", left.distance_m, right.distance_m);
        result.scalar(prefix + ".emission_phase_rad", left.emission_phase_rad, right.emission_phase_rad);
        result.scalar(prefix + ".radial_speed_m_s", left.radial_speed_m_s, right.radial_speed_m_s);
        result.scalar(prefix + ".frequency_ratio", left.frequency_ratio, right.frequency_ratio);
        result.scalar(prefix + ".distance_gain", left.distance_gain, right.distance_gain);
        result.scalar(prefix + ".residual_s", left.residual_s, right.residual_s);
        result.value(prefix + ".iterations", left.iterations, right.iterations);
        result.position("last_emissions[" + std::to_string(path) + "]",
                        actual.last_emissions[path], canonical.last_emissions[path]);
    }
    return result;
}

struct PartitionReport {
    std::string id;
    std::vector<std::uint32_t> pattern;
    bool baseline{}, completed{}, passed{};
    std::uint64_t native_frames{}, calls{}, events_consumed{};
    std::uint64_t end_boundary_events{}, offset_zero_events{}, tied_adjacent_events{};
    std::uint32_t maximum_block_observed{};
    double maximum_native_residual_s{};
    std::uint32_t maximum_native_iterations{};
    double wall_seconds{};
    std::string input_sha256, audio_sha256;
    std::array<BitComparison, 2> audio_comparison;
    FieldComparison state_comparison, diagnostics_comparison;
    native::RendererState final_state;
    native::RendererDiagnostics final_diagnostics;
};

struct SelectedTrace {
    std::uint64_t frame{};
    std::size_t reference_path{};
    reference::Path expected;
    bool has_native{};
    native::PathResult actual;
    native::SamplePosition native_emission;
};

struct ConvergencePair {
    std::uint64_t frame{};
    std::size_t reference_path{};
    Real contractive_delay_s{}, bisection_delay_s{}, difference_s{};
    Real contractive_residual_s{}, bisection_residual_s{};
    unsigned contractive_evaluations{}, bisection_evaluations{};
    bool passed{};
};

struct FinalMotionCheck {
    reference::WrappedState expected;
    Real expected_angle_rad{}, angle_error_rad{}, speed_error_rad_s{};
    Real angle_limit_rad{}, speed_limit_rad_s{};
    bool command_match{}, passed{};
};

struct RateReport {
    std::uint32_t rate{};
    std::uint64_t frames{};
    bool completed{}, passed{};
    std::uint64_t reference_frames{};
    std::size_t history_capacity{};
    std::uint32_t tail_flush_frames{};
    std::uint64_t canonical_audio_bytes{};
    std::array<native::PathBounds, 4> path_bounds{};
    std::vector<reference::Event> events;
    std::array<ChannelMetrics, 2> channels;
    std::array<SignalRegion, 3> regions;
    PathMetrics reference_paths;
    std::string reference_binary64_audio_sha256;
    std::array<PartitionReport, kPartitionCount> partitions;
    std::vector<SelectedTrace> selected_traces;
    std::vector<ConvergencePair> convergence_pairs;
    std::array<FinalMotionCheck, 2> final_motion;
    double wall_seconds{};
};

struct RunReport {
    std::string mode{"smoke"};
    bool completed{}, passed{}, hash_self_check_passed{}, environment_passed{};
    std::vector<std::string> invocation;
    std::string failed_stage, exception;
    std::vector<std::string> failures;
    std::vector<RateReport> rates;
    double wall_seconds{};
};

native::SpeedCommand native_command(reference::Command command) {
    return command == reference::Command::Chorale ? native::SpeedCommand::Chorale
                                                 : native::SpeedCommand::Tremolo;
}

native::Profile native_profile(const reference::Scene& scene) {
    native::Profile result;
    for (std::size_t rotor = 0; rotor < 2; ++rotor) {
        const auto& value = scene.rotors[rotor];
        result.rotors[rotor] = {
            {value.origin_m.x, value.origin_m.y, value.origin_m.z}, value.radius_m,
            {value.slow_rad_s, value.fast_rad_s, value.tau_up_s, value.tau_down_s,
             static_cast<std::int8_t>(value.direction)},
            value.initial_phase_rad, value.initial_speed_rad_s, native_command(value.initial_command)};
    }
    for (std::size_t channel = 0; channel < 2; ++channel) {
        const auto& mic = scene.microphones[channel];
        result.microphones[channel].position_m = {mic.x, mic.y, mic.z};
    }
    result.sound_speed_m_s = scene.sound_speed_m_s;
    result.reference_distance_m = scene.reference_distance_m;
    return result;
}

double input_value(bool full, std::uint32_t rate, std::size_t rotor, std::int64_t frame) {
    // Never shift negative history into the active bounded signal.
    if (frame < 0) return 0;
    return reference::full_input(rate, rotor, frame + (full ? 0 : 2LL * rate));
}

std::vector<std::uint64_t> selected_frames(std::uint32_t rate, bool full) {
    if (!full) return {0, 7, 256, 4096};
    const std::uint64_t fs = rate;
    return {0, 7, 256, 4096, fs / 2, 2 * fs - 1, 2 * fs,
            4 * fs, 6 * fs, 9 * fs, 10 * fs - 1};
}

std::vector<std::uint64_t> convergence_frames(std::uint32_t rate, bool full) {
    if (!full) return {0, 1, 7, 64, 257, 4096};
    const std::uint64_t fs = rate;
    return {0, 1, 7, 64, 257, 4096, fs / 2 - 1, fs / 2, fs / 2 + 1,
            2 * fs - 1, 2 * fs, 3 * fs + 17, 4 * fs, 6 * fs - 1,
            6 * fs, 6 * fs + 1, 9 * fs, 10 * fs - 1};
}

std::size_t signal_region(bool full, std::uint32_t rate, std::uint64_t frame) {
    if (!full) return 1;
    const std::uint64_t fs = rate;
    if (frame < 2 * fs) return 0;
    if (frame >= 9 * fs || (frame >= 6 * fs && frame < 6 * fs + fs / 8)) return 2;
    return 1;
}

void qualify_reference_convergence(RateReport& report, const reference::Scene& scene,
                                  const reference::Renderer& expected, bool full) {
    for (const auto frame : convergence_frames(report.rate, full)) {
        for (std::size_t reference_path = 0; reference_path < 4; ++reference_path) {
            const auto rotor = reference_path % 2;
            const auto channel = reference_path / 2;
            const auto bounds = reference::path_bounds(scene.rotors[rotor], scene.microphones[channel],
                                                       scene.sound_speed_m_s);
            const reference::Position observation{static_cast<std::int64_t>(frame) - 2, 0};
            const auto fast = reference::solve_path(expected.timeline(rotor), scene.rotors[rotor],
                scene.microphones[channel], bounds, observation, report.rate,
                scene.sound_speed_m_s, scene.reference_distance_m);
            const auto pure = reference::solve_path(expected.timeline(rotor), scene.rotors[rotor],
                scene.microphones[channel], bounds, observation, report.rate,
                scene.sound_speed_m_s, scene.reference_distance_m,
                reference::SolveMethod::PureBisection, kPureBisectionTarget);
            const auto difference = std::abs(fast.delay_s - pure.delay_s);
            report.convergence_pairs.push_back({frame, reference_path, fast.delay_s, pure.delay_s,
                difference, fast.residual_s, pure.residual_s, fast.evaluations, pure.evaluations,
                difference <= kConvergenceLimit});
        }
    }
}

void qualify_final_motion(RateReport& report, const reference::Renderer& expected) {
    const auto& actual = report.partitions[0].final_state;
    for (std::size_t rotor = 0; rotor < 2; ++rotor) {
        auto& check = report.final_motion[rotor];
        const auto motion = expected.timeline(rotor).at({static_cast<std::int64_t>(report.frames), 0});
        check.expected = reference::wrap(motion);
        check.expected_angle_rad = motion.angle_rad;
        const Real actual_angle = static_cast<Real>(actual.motion[rotor].phase_rad)
                                + static_cast<Real>(actual.motion[rotor].turns) * reference::kTwoPi;
        check.angle_error_rad = std::abs(actual_angle - motion.angle_rad);
        check.speed_error_rad_s = std::abs(static_cast<Real>(actual.motion[rotor].speed_rad_s)
                                        - motion.speed_rad_s);
        check.angle_limit_rad = kAngleAbsoluteLimit + kAngleRelativeLimit * std::abs(motion.angle_rad);
        check.speed_limit_rad_s = kSpeedAbsoluteLimit + kSpeedRelativeLimit * std::abs(motion.speed_rad_s);
        check.command_match = actual.commands[rotor]
            == native_command(expected.timeline(rotor).command_at(static_cast<std::int64_t>(report.frames)));
        check.passed = check.command_match && check.angle_error_rad <= check.angle_limit_rad
                    && check.speed_error_rad_s <= check.speed_limit_rad_s
                    && actual.motion[rotor].turns == check.expected.turns;
    }
}

struct AudioBlock {
    std::array<double, native::kMaxBlockFrames> horn{};
    std::array<double, native::kMaxBlockFrames> drum{};
    std::array<double, native::kMaxBlockFrames> left{};
    std::array<double, native::kMaxBlockFrames> right{};
};

void render_partition(RunReport& run, RateReport& report, std::size_t partition_index,
                      const native::Profile& profile, const reference::Renderer& expected,
                      std::vector<std::array<double, 2>>& canonical, bool full) {
    auto& part = report.partitions[partition_index];
    const auto start = Clock::now();
    native::RotaryRenderer renderer;
    run.failed_stage = "prepare/rate=" + std::to_string(report.rate) + "/partition=" + part.id;
    const auto prepared = renderer.prepare(profile, {static_cast<double>(report.rate), native::kMaxBlockFrames});
    require(prepared == native::Status::Ok, "native prepare: " + std::string(native::status_name(prepared)));
    require(renderer.algorithmic_latency_frames() == 2, "native algorithmic latency is not exactly two frames");
    if (part.baseline) {
        report.history_capacity = renderer.history_capacity_frames();
        report.tail_flush_frames = renderer.tail_flush_frames();
        report.path_bounds = renderer.path_bounds();
        for (std::size_t channel = 0; channel < 2; ++channel)
            report.channels[channel].normalization = expected.normalization(channel);
    }
    auto block = std::make_unique<AudioBlock>();
    std::vector<native::CommandEvent> commands;
    commands.reserve(report.events.size());
    std::size_t next_event = 0;
    std::uint64_t next_frame = 0;
    std::size_t pattern_index = 0;
    Sha256 input_hash, audio_hash, reference_audio_hash;
    const auto selected = selected_frames(report.rate, full);
    while (next_frame < report.frames) {
        const auto requested = part.pattern[pattern_index++ % part.pattern.size()];
        const auto count = static_cast<std::uint32_t>(std::min<std::uint64_t>(requested, report.frames - next_frame));
        const auto end_frame = next_frame + count;
        commands.clear();
        // Inclusive end-boundary admission, each absolute event consumed once.
        // Offset-N is applied before any later call's offset-zero event.
        while (next_event < report.events.size()
               && static_cast<std::uint64_t>(report.events[next_event].frame) <= end_frame) {
            const auto& event = report.events[next_event];
            require(event.frame >= 0 && static_cast<std::uint64_t>(event.frame) >= next_frame,
                    "event cursor attempted to move an absolute event");
            const auto offset = static_cast<std::uint32_t>(static_cast<std::uint64_t>(event.frame) - next_frame);
            commands.push_back({offset, static_cast<native::RotorId>(event.rotor), native_command(event.command)});
            if (offset == count) ++part.end_boundary_events;
            if (offset == 0) ++part.offset_zero_events;
            if (next_event > 0 && report.events[next_event - 1].frame == event.frame) ++part.tied_adjacent_events;
            ++next_event;
        }
        for (std::uint32_t index = 0; index < count; ++index) {
            const auto frame = static_cast<std::int64_t>(next_frame + index);
            block->horn[index] = input_value(full, report.rate, 0, frame);
            block->drum[index] = input_value(full, report.rate, 1, frame);
            input_hash.binary64(block->horn[index]);
            input_hash.binary64(block->drum[index]);
        }
        run.failed_stage = "process/rate=" + std::to_string(report.rate) + "/partition=" + part.id
                         + "/frame=" + std::to_string(next_frame);
        const auto result = renderer.process(std::span<const double>(block->horn.data(), count),
            std::span<const double>(block->drum.data(), count),
            std::span<double>(block->left.data(), count), std::span<double>(block->right.data(), count), commands);
        ++part.calls;
        require(result.ok(), "native process rejected: " + std::string(native::status_name(result.status))
                             + "; events_consumed=" + std::to_string(result.events_consumed));
        require(result.events_consumed == commands.size(), "native event consumption differs from supplied stream");
        require(std::isfinite(result.max_solver_residual_s)
                && result.max_solver_residual_s >= 0
                && result.max_solver_residual_s <= native::kMaxSolverResidualSeconds
                && result.max_solver_iterations > 0
                && result.max_solver_iterations <= native::kMaxSolverIterations,
                "native process solver budget failed");
        part.native_frames += count;
        part.events_consumed += result.events_consumed;
        part.maximum_block_observed = std::max(part.maximum_block_observed, count);
        part.maximum_native_residual_s = std::max(part.maximum_native_residual_s, result.max_solver_residual_s);
        part.maximum_native_iterations = std::max(part.maximum_native_iterations, result.max_solver_iterations);
        for (std::uint32_t index = 0; index < count; ++index) {
            const auto frame = next_frame + index;
            const std::array<double, 2> actual{block->left[index], block->right[index]};
            require(std::isfinite(actual[0]) && std::isfinite(actual[1]), "native output is nonfinite");
            audio_hash.binary64(actual[0]);
            audio_hash.binary64(actual[1]);
            if (!part.baseline) {
                for (std::size_t channel = 0; channel < 2; ++channel)
                    part.audio_comparison[channel].observe(frame, report.frames, actual[channel],
                        canonical[static_cast<std::size_t>(frame)][channel]);
                continue;
            }
            canonical[static_cast<std::size_t>(frame)] = actual;
            run.failed_stage = "reference/rate=" + std::to_string(report.rate) + "/frame=" + std::to_string(frame);
            const auto sample = expected.at(static_cast<std::int64_t>(frame),
                [full, rate = report.rate](std::size_t rotor, std::int64_t source_frame) {
                    return input_value(full, rate, rotor, source_frame);
                });
            ++report.reference_frames;
            auto& region = report.regions[signal_region(full, report.rate, frame)];
            ++region.frame_count;
            if (block->horn[index] != 0) ++region.input_nonzero[0];
            if (block->drum[index] != 0) ++region.input_nonzero[1];
            for (std::size_t channel = 0; channel < 2; ++channel) {
                auto& metrics = report.channels[channel];
                metrics.error.observe(static_cast<std::int64_t>(frame), actual[channel],
                                      sample.output[channel], metrics.normalization);
                if (std::abs(static_cast<Real>(actual[channel]) - sample.output[channel])
                    / metrics.normalization > reference::kNormalizedWaveformLimit)
                    metrics.failures.observe(frame, report.frames);
                if (actual[channel] != 0) ++region.actual_nonzero[channel];
                if (sample.output[channel] != 0) ++region.reference_nonzero[channel];
                if (actual[channel] != 0 || sample.output[channel] != 0) ++region.nonzero_comparison_count[channel];
                reference_audio_hash.binary64(static_cast<double>(sample.output[channel]));
            }
            for (std::size_t path = 0; path < sample.paths.size(); ++path)
                report.reference_paths.observe(frame, path, sample.paths[path]);
            if (std::binary_search(selected.begin(), selected.end(), frame)) {
                // Canonical partition size one ensures this diagnostic belongs
                // to the selected sample, not some later process-block endpoint.
                require(count == 1, "selected native path evidence requires the one-frame baseline");
                const auto diagnostics = renderer.diagnostics();
                require(diagnostics.has_rendered_sample && diagnostics.last_input_frame == frame
                        && diagnostics.last_observation.frame == static_cast<std::int64_t>(frame) - 2
                        && bits(diagnostics.last_observation.fraction) == bits(0.0),
                        "native diagnostic observation differs from fixed frame-minus-two query");
                for (std::size_t path = 0; path < sample.paths.size(); ++path) {
                    const auto native_path = kReferenceToNativePath[path];
                    report.selected_traces.push_back({frame, path, sample.paths[path], true,
                        diagnostics.last_paths[native_path], diagnostics.last_emissions[native_path]});
                }
            }
        }
        next_frame = end_frame;
    }
    require(next_event == report.events.size(), "final end-boundary events were omitted");
    part.final_state = renderer.state();
    part.final_diagnostics = renderer.diagnostics();
    require(part.final_state.frame == report.frames, "native final clock is incomplete");
    part.input_sha256 = input_hash.digest();
    part.audio_sha256 = audio_hash.digest();
    if (part.baseline) {
        report.reference_binary64_audio_sha256 = reference_audio_hash.digest();
    } else {
        part.state_comparison = compare_state(part.final_state, report.partitions[0].final_state);
        part.diagnostics_comparison = compare_diagnostics(part.final_diagnostics,
                                                          report.partitions[0].final_diagnostics);
    }
    part.completed = part.native_frames == report.frames && part.events_consumed == report.events.size();
    part.passed = part.completed;
    if (!part.baseline) {
        part.passed = part.passed && part.input_sha256 == report.partitions[0].input_sha256
                    && part.audio_comparison[0].equal == report.frames
                    && part.audio_comparison[1].equal == report.frames
                    && part.state_comparison.mismatches.empty() && part.diagnostics_comparison.mismatches.empty()
                    && part.state_comparison.compared == 32 && part.diagnostics_comparison.compared == 46;
    }
    part.wall_seconds = seconds_since(start);
    std::cerr << "waveform " << run.mode << " rate=" << report.rate << " partition=" << part.id
              << " frames=" << part.native_frames << " events=" << part.events_consumed
              << " status=" << (part.passed ? "pass" : "fail") << " wall_s=" << part.wall_seconds << '\n';
}

void run_rate(RunReport& run, RateReport& report, bool full) {
    const auto start = Clock::now();
    report.frames = full ? static_cast<std::uint64_t>(reference::kFullDurationSeconds) * report.rate : kSmokeFrames;
    report.events = reference::full_events(report.rate);
    report.events.erase(std::remove_if(report.events.begin(), report.events.end(),
        [&report](const reference::Event& event) { return static_cast<std::uint64_t>(event.frame) > report.frames; }),
        report.events.end());
    for (std::size_t partition = 0; partition < reference::kFixedBlocks.size(); ++partition) {
        auto& part = report.partitions[partition];
        part.id = "fixed_" + std::to_string(reference::kFixedBlocks[partition]);
        part.pattern = {reference::kFixedBlocks[partition]};
        part.baseline = partition == 0;
    }
    report.partitions.back().id = "irregular_v1";
    report.partitions.back().pattern.assign(reference::kIrregularBlocks.begin(), reference::kIrregularBlocks.end());
    const auto scene = reference::full_scene();
    const auto profile = native_profile(scene);
    const reference::Renderer expected(scene, report.rate, report.events);
    // Exactly one full waveform buffer, at most 30,720,000 bytes; one rate at a
    // time. Reference output is calculated and accumulated only as a stream.
    std::vector<std::array<double, 2>> canonical(static_cast<std::size_t>(report.frames));
    report.canonical_audio_bytes = report.frames * 2U * sizeof(double);
    for (std::size_t partition = 0; partition < kPartitionCount; ++partition)
        render_partition(run, report, partition, profile, expected, canonical, full);
    run.failed_stage = "reference_convergence/rate=" + std::to_string(report.rate);
    qualify_reference_convergence(report, scene, expected, full);
    qualify_final_motion(report, expected);
    const auto expected_selected = static_cast<std::uint64_t>(selected_frames(report.rate, full).size()) * 4U;
    const auto expected_convergence = static_cast<std::uint64_t>(convergence_frames(report.rate, full).size()) * 4U;
    report.completed = report.reference_frames == report.frames
                    && report.reference_paths.count == 4U * report.frames
                    && report.selected_traces.size() == expected_selected
                    && report.convergence_pairs.size() == expected_convergence;
    report.passed = report.completed;
    for (const auto& part : report.partitions) {
        report.completed = report.completed && part.completed;
        report.passed = report.passed && part.passed;
    }
    for (const auto& channel : report.channels)
        report.passed = report.passed && channel.error.count == report.frames && channel.error.passes()
                     && channel.failures.count == 0;
    for (const auto& check : report.final_motion) report.passed = report.passed && check.passed;
    for (const auto& pair : report.convergence_pairs) report.passed = report.passed && pair.passed;
    for (std::size_t channel = 0; channel < 2; ++channel) {
        report.passed = report.passed && report.regions[1].input_nonzero[channel] > 0
                     && report.regions[1].actual_nonzero[channel] > 0
                     && report.regions[1].reference_nonzero[channel] > 0;
        if (full) {
            report.passed = report.passed && report.regions[0].input_nonzero[channel] == 2
                         && report.regions[0].actual_nonzero[channel] > 0
                         && report.regions[0].reference_nonzero[channel] > 0
                         && report.regions[2].input_nonzero[channel] == 0;
        }
    }
    report.wall_seconds = seconds_since(start);
    if (!report.passed)
        run.failures.push_back("rate=" + std::to_string(report.rate) + ": inspect complete channel/partition/convergence records");
}

void write_failed_frames(std::ostream& output, const FailedFrames& failures) {
    output << "{\"count\":" << failures.count << ",\"first_frame\":" << failures.first
           << ",\"last_frame\":" << failures.last << ",\"complete\":true";
    if (!failures.bitmap.empty()) {
        Sha256 hash;
        for (const auto byte : failures.bitmap) hash.byte(byte);
        output << ",\"encoding\":\"lsb0-per-frame-hex\",\"frame_count\":" << failures.total_frames
               << ",\"byte_count\":" << failures.bitmap.size() << ",\"sha256\":";
        quoted(output, hash.digest());
        output << ",\"hex\":\"";
        constexpr char digits[] = "0123456789abcdef";
        for (const auto byte : failures.bitmap) output << digits[byte >> 4U] << digits[byte & 15U];
        output << '"';
    }
    output << '}';
}

void write_motion(std::ostream& output, const native::MotionState& value) {
    output << "{\"phase_rad\":" << value.phase_rad << ",\"phase_bits\":";
    quoted(output, hex64(bits(value.phase_rad)));
    output << ",\"turns\":" << value.turns << ",\"speed_rad_s\":" << value.speed_rad_s << ",\"speed_bits\":";
    quoted(output, hex64(bits(value.speed_rad_s)));
    output << '}';
}

void write_position(std::ostream& output, native::SamplePosition value) {
    output << "{\"frame\":" << value.frame << ",\"fraction\":" << value.fraction << ",\"fraction_bits\":";
    quoted(output, hex64(bits(value.fraction)));
    output << '}';
}

void write_native_path(std::ostream& output, const native::PathResult& value) {
    output << "{\"delay_s\":" << value.delay_s << ",\"distance_m\":" << value.distance_m
           << ",\"emission_phase_rad\":" << value.emission_phase_rad
           << ",\"radial_speed_m_s\":" << value.radial_speed_m_s << ",\"frequency_ratio\":" << value.frequency_ratio
           << ",\"distance_gain\":" << value.distance_gain << ",\"residual_s\":" << value.residual_s
           << ",\"iterations\":" << value.iterations << '}';
}

void write_state(std::ostream& output, const native::RendererState& state) {
    output << "{\"prepared\":" << state.prepared << ",\"sample_rate\":" << state.sample_rate
           << ",\"frame\":" << state.frame << ",\"max_frame\":" << state.max_frame << ",\"motion\":[";
    for (std::size_t rotor = 0; rotor < 2; ++rotor) {
        if (rotor != 0) output << ',';
        write_motion(output, state.motion[rotor]);
    }
    output << "],\"epoch_initial\":[";
    for (std::size_t rotor = 0; rotor < 2; ++rotor) {
        if (rotor != 0) output << ',';
        write_motion(output, state.epoch_initial[rotor]);
    }
    output << "],\"commands\":[";
    for (std::size_t rotor = 0; rotor < 2; ++rotor) {
        if (rotor != 0) output << ',';
        quoted(output, native::command_name(state.commands[rotor]));
    }
    output << "],\"segments\":[";
    for (std::size_t rotor = 0; rotor < 2; ++rotor) {
        if (rotor != 0) output << ',';
        const auto& value = state.segments[rotor];
        output << "{\"anchor_frame\":" << value.anchor_frame << ",\"initial\":";
        write_motion(output, value.initial);
        output << ",\"target_rad_s\":" << value.target_rad_s << ",\"tau_s\":" << value.tau_s
               << ",\"direction\":" << static_cast<int>(value.direction) << '}';
    }
    output << "]}";
}

void write_diagnostics(std::ostream& output, const native::RendererDiagnostics& diagnostics) {
    output << "{\"path_order\":\"rotor_major\",\"has_rendered_sample\":" << diagnostics.has_rendered_sample
           << ",\"last_input_frame\":" << diagnostics.last_input_frame << ",\"last_observation\":";
    write_position(output, diagnostics.last_observation);
    output << ",\"max_solver_residual_s\":" << diagnostics.max_solver_residual_s
           << ",\"max_solver_iterations\":" << diagnostics.max_solver_iterations << ",\"last_paths\":[";
    for (std::size_t path = 0; path < 4; ++path) {
        if (path != 0) output << ',';
        write_native_path(output, diagnostics.last_paths[path]);
    }
    output << "],\"last_emissions\":[";
    for (std::size_t path = 0; path < 4; ++path) {
        if (path != 0) output << ',';
        write_position(output, diagnostics.last_emissions[path]);
    }
    output << "]}";
}

void write_field_comparison(std::ostream& output, const FieldComparison& comparison) {
    output << "{\"field_count\":" << comparison.compared
           << ",\"match\":" << comparison.mismatches.empty() << ",\"floating_comparison\":\"binary64_bits\""
           << ",\"compares_struct_padding\":false,\"mismatched_fields\":[";
    for (std::size_t index = 0; index < comparison.mismatches.size(); ++index) {
        if (index != 0) output << ',';
        quoted(output, comparison.mismatches[index]);
    }
    output << "]}";
}

void write_path_metrics(std::ostream& output, const PathMetrics& metrics) {
    output << "{\"path_solutions\":" << metrics.count << ",\"max_residual_s\":" << metrics.maximum_residual_s
           << ",\"max_evaluations\":" << metrics.maximum_evaluations
           << ",\"max_contraction_steps\":" << metrics.maximum_contraction_steps
           << ",\"max_bisections\":" << metrics.maximum_bisections
           << ",\"worst_frame\":" << metrics.worst_frame
           << ",\"worst_reference_path_index\":" << metrics.worst_reference_path << '}';
}

template<class T, std::size_t Size>
void write_array(std::ostream& output, const std::array<T, Size>& values) {
    output << '[';
    for (std::size_t index = 0; index < values.size(); ++index) {
        if (index != 0) output << ',';
        output << values[index];
    }
    output << ']';
}

void write_scene(std::ostream& output) {
    const auto scene = reference::full_scene();
    output << "{\"synthetic_engineering_fixture\":true,\"rotors\":[";
    for (std::size_t rotor = 0; rotor < 2; ++rotor) {
        if (rotor != 0) output << ',';
        const auto& value = scene.rotors[rotor];
        output << "{\"rotor\":" << rotor << ",\"origin_m\":[" << value.origin_m.x << ',' << value.origin_m.y << ','
               << value.origin_m.z << "],\"radius_m\":" << value.radius_m << ",\"slow_rad_s\":" << value.slow_rad_s
               << ",\"fast_rad_s\":" << value.fast_rad_s << ",\"tau_up_s\":" << value.tau_up_s
               << ",\"tau_down_s\":" << value.tau_down_s << ",\"direction\":" << value.direction
               << ",\"initial_phase_rad\":" << value.initial_phase_rad
               << ",\"initial_speed_rad_s\":" << value.initial_speed_rad_s << ",\"initial_command\":";
        quoted(output, native::command_name(native_command(value.initial_command)));
        output << '}';
    }
    output << "],\"microphones_m\":[";
    for (std::size_t channel = 0; channel < 2; ++channel) {
        if (channel != 0) output << ',';
        const auto& mic = scene.microphones[channel];
        output << '[' << mic.x << ',' << mic.y << ',' << mic.z << ']';
    }
    output << "],\"sound_speed_m_s\":" << scene.sound_speed_m_s
           << ",\"reference_distance_m\":" << scene.reference_distance_m << '}';
}

template<class T>
void write_precision(std::ostream& output) {
    output << "{\"radix\":" << std::numeric_limits<T>::radix
           << ",\"digits\":" << std::numeric_limits<T>::digits
           << ",\"digits10\":" << std::numeric_limits<T>::digits10
           << ",\"max_digits10\":" << std::numeric_limits<T>::max_digits10
           << ",\"sizeof\":" << sizeof(T) << ",\"is_iec559\":" << std::numeric_limits<T>::is_iec559 << '}';
}

constexpr bool fast_math_enabled() {
#if defined(__FAST_MATH__) || defined(_M_FP_FAST)
    return true;
#elif defined(__FINITE_MATH_ONLY__) && __FINITE_MATH_ONLY__ != 0
    return true;
#else
    return false;
#endif
}

std::string compiler_identity() {
#if defined(__clang__)
    return std::string("Clang ") + __clang_version__;
#elif defined(__GNUC__)
    return std::string("GCC ") + __VERSION__;
#elif defined(_MSC_FULL_VER)
    return "MSVC " + std::to_string(_MSC_FULL_VER);
#else
    return "unknown_compiler";
#endif
}

std::string library_identity() {
#if defined(_LIBCPP_VERSION)
    return "libc++ " + std::to_string(_LIBCPP_VERSION);
#elif defined(__GLIBCXX__)
    return "libstdc++ " + std::to_string(__GLIBCXX__);
#elif defined(_MSVC_STL_VERSION)
    return "MSVC STL " + std::to_string(_MSVC_STL_VERSION);
#else
    return "unknown_standard_library";
#endif
}

std::string_view platform_identity() {
#if defined(_WIN32)
    return "Windows";
#elif defined(__APPLE__)
    return "Apple";
#elif defined(__linux__)
    return "Linux";
#else
    return "unknown_platform";
#endif
}

void write_environment(std::ostream& output, const RunReport& run) {
    output << "{\"status\":"; quoted(output, run.environment_passed ? "pass" : "fail");
    output << ",\"compiler\":"; quoted(output, compiler_identity());
    output << ",\"standard_library\":"; quoted(output, library_identity());
    output << ",\"platform\":"; quoted(output, platform_identity());
    output << ",\"cplusplus\":" << __cplusplus << ",\"build_configuration\":";
    quoted(output, HAMMOND_WAVEFORM_BUILD_CONFIG);
    output << ",\"build_flags\":"; quoted(output, HAMMOND_WAVEFORM_BUILD_FLAGS);
    output << ",\"floating_contraction_options\":\"runner_records_actual_core_and_probe_options\""
           << ",\"fast_math_enabled\":" << fast_math_enabled()
           << ",\"rounding_mode\":" << std::fegetround()
           << ",\"rounding_is_to_nearest\":" << (std::fegetround() == FE_TONEAREST)
           << ",\"double\":";
    write_precision<double>(output);
    output << ",\"long_double\":"; write_precision<Real>(output);
    output << ",\"wider_than_double\":" << (std::numeric_limits<Real>::digits > std::numeric_limits<double>::digits)
           << ",\"pointer_bytes\":" << sizeof(void*) << ",\"native_byte_order\":";
    quoted(output, std::endian::native == std::endian::little ? "little" : "big_or_mixed");
    output << '}';
}

void write_partition(std::ostream& output, const PartitionReport& part) {
    output << "{\"id\":"; quoted(output, part.id);
    output << ",\"status\":"; quoted(output, !part.completed ? "not_run" : (part.passed ? "pass" : "fail"));
    output << ",\"completed\":" << part.completed << ",\"baseline\":" << part.baseline << ",\"pattern\":[";
    for (std::size_t index = 0; index < part.pattern.size(); ++index) {
        if (index != 0) output << ',';
        output << part.pattern[index];
    }
    output << "],\"native_frames\":" << part.native_frames << ",\"native_path_solutions\":" << 4U * part.native_frames
           << ",\"process_calls\":" << part.calls << ",\"events_consumed\":" << part.events_consumed
           << ",\"end_boundary_events\":" << part.end_boundary_events << ",\"offset_zero_events\":" << part.offset_zero_events
           << ",\"tied_adjacent_events\":" << part.tied_adjacent_events << ",\"max_block_observed\":" << part.maximum_block_observed
           << ",\"max_native_residual_s\":" << part.maximum_native_residual_s
           << ",\"max_native_iterations\":" << part.maximum_native_iterations
           << ",\"wall_seconds\":" << part.wall_seconds << ",\"input_sha256\":";
    quoted(output, part.input_sha256);
    output << ",\"audio_sha256\":"; quoted(output, part.audio_sha256);
    output << ",\"audio_bit_comparison\":[";
    for (std::size_t channel = 0; channel < 2; ++channel) {
        if (channel != 0) output << ',';
        const auto& comparison = part.audio_comparison[channel];
        output << "{\"channel\":" << channel << ",\"compared_samples\":" << comparison.compared
               << ",\"equal_samples\":" << comparison.equal << ",\"max_absolute_difference\":" << comparison.maximum_absolute
               << ",\"worst_frame\":" << comparison.worst_frame << ",\"worst_actual\":" << comparison.worst_actual
               << ",\"worst_canonical\":" << comparison.worst_canonical << ",\"worst_actual_bits\":";
        quoted(output, hex64(bits(comparison.worst_actual)));
        output << ",\"worst_canonical_bits\":"; quoted(output, hex64(bits(comparison.worst_canonical)));
        output << ",\"failures\":"; write_failed_frames(output, comparison.failures);
        output << '}';
    }
    output << "],\"final_state_comparison\":"; write_field_comparison(output, part.state_comparison);
    output << ",\"final_diagnostics_comparison\":"; write_field_comparison(output, part.diagnostics_comparison);
    output << ",\"final_state\":"; write_state(output, part.final_state);
    output << ",\"final_diagnostics\":"; write_diagnostics(output, part.final_diagnostics);
    output << '}';
}

void write_rate(std::ostream& output, const RateReport& report, bool full) {
    output << "{\"rate\":" << report.rate << ",\"status\":";
    quoted(output, report.completed && report.passed ? "pass" : "fail");
    output << ",\"completed\":" << report.completed << ",\"duration_seconds\":"
           << static_cast<Real>(report.frames) / report.rate << ",\"required_frames\":" << report.frames
           << ",\"reference_frames\":" << report.reference_frames << ",\"reference_scalar_comparisons\":"
           << 2U * report.reference_frames << ",\"history_capacity_frames\":" << report.history_capacity
           << ",\"tail_flush_frames\":" << report.tail_flush_frames << ",\"canonical_audio_bytes\":" << report.canonical_audio_bytes
           << ",\"wall_seconds\":" << report.wall_seconds << ",\"event_count\":" << report.events.size() << ",\"events\":[";
    for (std::size_t index = 0; index < report.events.size(); ++index) {
        if (index != 0) output << ',';
        const auto& event = report.events[index];
        output << "{\"frame\":" << event.frame << ",\"rotor\":" << event.rotor << ",\"command\":";
        quoted(output, native::command_name(native_command(event.command)));
        output << '}';
    }
    output << "],\"path_bounds\":[";
    for (std::size_t path = 0; path < 4; ++path) {
        if (path != 0) output << ',';
        const auto& bounds = report.path_bounds[path];
        output << "{\"native_path_index\":" << path << ",\"min_distance_m\":" << bounds.min_distance_m
               << ",\"max_distance_m\":" << bounds.max_distance_m << ",\"max_tangential_mach\":"
               << bounds.max_tangential_mach << '}';
    }
    output << "],\"channels\":[";
    for (std::size_t channel = 0; channel < 2; ++channel) {
        if (channel != 0) output << ',';
        const auto& metrics = report.channels[channel];
        const auto& error = metrics.error;
        output << "{\"channel\":" << channel << ",\"status\":";
        quoted(output, error.count == report.frames && error.passes() ? "pass" : "fail");
        output << ",\"samples\":" << error.count << ",\"normalization_G\":" << metrics.normalization
               << ",\"maximum_absolute_error\":" << error.maximum_absolute
               << ",\"rms_absolute_error\":" << error.rms()
               << ",\"maximum_normalized_error\":" << error.maximum_normalized
               << ",\"rms_normalized_error\":" << error.normalized_rms()
               << ",\"worst_frame\":" << error.worst_frame << ",\"worst_actual\":" << error.worst_actual
               << ",\"worst_reference\":" << error.worst_reference << ",\"failures\":";
        write_failed_frames(output, metrics.failures);
        output << '}';
    }
    output << "],\"signal_regions\":[";
    const std::array<std::string_view, 3> names{"impulses", "bounded_input", "explicit_silence"};
    for (std::size_t index = 0; index < report.regions.size(); ++index) {
        if (index != 0) output << ',';
        const auto& region = report.regions[index];
        output << "{\"id\":"; quoted(output, names[index]);
        output << ",\"required\":" << (full || index == 1) << ",\"frames\":" << region.frame_count
               << ",\"input_nonzero\":"; write_array(output, region.input_nonzero);
        output << ",\"actual_nonzero\":"; write_array(output, region.actual_nonzero);
        output << ",\"reference_nonzero\":"; write_array(output, region.reference_nonzero);
        output << ",\"nonzero_comparison_count\":"; write_array(output, region.nonzero_comparison_count);
        output << '}';
    }
    output << "],\"reference_solver\":"; write_path_metrics(output, report.reference_paths);
    output << ",\"reference_audio_sha256\":"; quoted(output, report.reference_binary64_audio_sha256);
    output << ",\"reference_audio_digest_representation\":\"binary64_cast_for_digest_only_no_change_to_error_computation\""
           << ",\"partitions\":[";
    for (std::size_t index = 0; index < report.partitions.size(); ++index) {
        if (index != 0) output << ',';
        write_partition(output, report.partitions[index]);
    }
    output << "],\"final_reference_motion\":[";
    for (std::size_t rotor = 0; rotor < 2; ++rotor) {
        if (rotor != 0) output << ',';
        const auto& check = report.final_motion[rotor];
        output << "{\"rotor\":" << rotor << ",\"passed\":" << check.passed << ",\"angle_rad\":" << check.expected_angle_rad
               << ",\"phase_rad\":" << check.expected.phase_rad << ",\"turns\":" << check.expected.turns
               << ",\"speed_rad_s\":" << check.expected.speed_rad_s << ",\"angle_error_rad\":" << check.angle_error_rad
               << ",\"speed_error_rad_s\":" << check.speed_error_rad_s << ",\"angle_limit_rad\":" << check.angle_limit_rad
               << ",\"speed_limit_rad_s\":" << check.speed_limit_rad_s << ",\"command_match\":" << check.command_match << '}';
    }
    output << "],\"selected_traces\":[";
    for (std::size_t index = 0; index < report.selected_traces.size(); ++index) {
        if (index != 0) output << ',';
        const auto& trace = report.selected_traces[index];
        const auto& path = trace.expected;
        output << "{\"frame\":" << trace.frame << ",\"observation_frame\":" << static_cast<std::int64_t>(trace.frame) - 2
               << ",\"rotor\":" << trace.reference_path % 2 << ",\"channel\":" << trace.reference_path / 2
               << ",\"reference_path_index\":" << trace.reference_path
               << ",\"native_path_index\":" << kReferenceToNativePath[trace.reference_path]
               << ",\"delay_s\":" << path.delay_s << ",\"emission_frame\":" << path.emission.frame
               << ",\"fraction\":" << path.emission.fraction << ",\"angle_rad\":" << path.motion.angle_rad
               << ",\"speed_rad_s\":" << path.motion.speed_rad_s << ",\"distance_m\":" << path.geometry.distance_m
               << ",\"frequency_ratio\":" << path.geometry.frequency_ratio
               << ",\"radial_speed_m_s\":" << path.geometry.radial_speed_m_s
               << ",\"distance_gain\":" << path.distance_gain << ",\"residual_s\":" << path.residual_s
               << ",\"evaluations\":" << path.evaluations << ",\"has_native\":" << trace.has_native << ",\"native_path\":";
        write_native_path(output, trace.actual);
        output << ",\"native_emission\":"; write_position(output, trace.native_emission);
        output << '}';
    }
    output << "],\"reference_convergence\":{\"difference_limit_s\":" << kConvergenceLimit
           << ",\"contractive_target_s\":" << reference::kReferenceResidualTarget
           << ",\"bisection_target_s\":" << kPureBisectionTarget
           << ",\"pair_count\":" << report.convergence_pairs.size() << ",\"pairs\":[";
    for (std::size_t index = 0; index < report.convergence_pairs.size(); ++index) {
        if (index != 0) output << ',';
        const auto& pair = report.convergence_pairs[index];
        output << "{\"frame\":" << pair.frame << ",\"reference_path_index\":" << pair.reference_path
               << ",\"rotor\":" << pair.reference_path % 2 << ",\"channel\":" << pair.reference_path / 2
               << ",\"contractive_delay_s\":" << pair.contractive_delay_s << ",\"bisection_delay_s\":" << pair.bisection_delay_s
               << ",\"difference_s\":" << pair.difference_s << ",\"contractive_residual_s\":" << pair.contractive_residual_s
               << ",\"bisection_residual_s\":" << pair.bisection_residual_s
               << ",\"contractive_evaluations\":" << pair.contractive_evaluations
               << ",\"bisection_evaluations\":" << pair.bisection_evaluations << ",\"passed\":" << pair.passed << '}';
    }
    output << "]}}";
}

void write_report(std::ostream& output, const RunReport& run) {
    std::uint64_t reference_frames = 0, native_frames = 0, compared = 0, equal = 0, events = 0;
    std::uint64_t selected = 0, pairs = 0, peak_canonical_bytes = 0, completed_partitions = 0;
    for (const auto& rate : run.rates) {
        reference_frames += rate.reference_frames;
        selected += static_cast<std::uint64_t>(rate.selected_traces.size());
        pairs += static_cast<std::uint64_t>(rate.convergence_pairs.size());
        peak_canonical_bytes = std::max(peak_canonical_bytes, rate.canonical_audio_bytes);
        for (const auto& part : rate.partitions) {
            native_frames += part.native_frames;
            events += part.events_consumed;
            if (part.completed) ++completed_partitions;
            for (const auto& channel : part.audio_comparison) {
                compared += channel.compared;
                equal += channel.equal;
            }
        }
    }
    const bool full = run.mode == "full";
    output << std::boolalpha << std::setprecision(std::numeric_limits<Real>::max_digits10);
    output << "{\"schema_version\":1,\"status\":"; quoted(output, run.passed ? "pass" : "fail");
    output << ",\"mode\":"; quoted(output, run.mode);
    output << ",\"completed\":" << run.completed << ",\"fixture_id\":";
    quoted(output, full ? reference::kFixtureId : kSmokeFixture);
    output << ",\"experiment_id\":"; quoted(output, full ? reference::kFixtureId : kSmokeFixture);
    output << ",\"model_id\":"; quoted(output, native::kModelId);
    output << ",\"contract_id\":"; quoted(output, native::kNumericalContractId);
    output << ",\"renderer_contract_id\":"; quoted(output, native::kRendererContractId);
    output << ",\"reference_id\":"; quoted(output, reference::kReferenceId);
    output << ",\"full_duration_seconds\":";
    if (full) output << reference::kFullDurationSeconds; else output << "null";
    output << ",\"required_rate_count\":4,\"partition_count\":6,\"required_rates\":";
    write_array(output, reference::kRates);
    output << ",\"required_reference_frames\":" << (full ? 3801000U : 4U * kSmokeFrames)
           << ",\"required_native_frames\":" << (full ? 22806000U : 24U * kSmokeFrames)
           << ",\"fixed_blocks\":"; write_array(output, reference::kFixedBlocks);
    output << ",\"irregular_blocks\":"; write_array(output, reference::kIrregularBlocks);
    output << ",\"invocation\":[";
    for (std::size_t index = 0; index < run.invocation.size(); ++index) {
        if (index != 0) output << ',';
        quoted(output, run.invocation[index]);
    }
    output << "],\"precision_environment\":"; write_environment(output, run);
    output << ",\"provenance\":{\"source_and_executable_sha256\":\"required_from_orchestrating_runner\""
           << ",\"source_stability\":\"required_before_and_after_from_runner\",\"sha256_self_check_passed\":"
           << run.hash_self_check_passed << ",\"sha256_self_check_vectors\":3,\"stream_encoding\":\"frame_interleaved_little_endian_binary64\"}"
           << ",\"fixture\":"; write_scene(output);
    output << ",\"signal\":{\"seed_hex\":\"726f746172792d34\",\"generator\":\"reference::full_input\""
           << ",\"input_frame_shift_in_sample_rates\":" << (full ? 0 : 2)
           << ",\"negative_history\":\"zero\",\"input_channel_order\":[\"horn\",\"drum\"],\"output_channel_order\":[\"left\",\"right\"]}"
           << ",\"comparison_policy\":{\"algorithmic_latency_frames\":2,\"observation\":\"(n-2)/Fs\""
           << ",\"normalization\":\"sum(reference_distance_m/full_orbit_minimum_distance_m) per receiver\""
           << ",\"normalized_maximum_limit\":" << reference::kNormalizedWaveformLimit
           << ",\"reference_residual_target_s\":" << reference::kReferenceResidualTarget
           << ",\"reference_residual_limit_s\":" << reference::kReferenceResidualLimit
           << ",\"native_residual_limit_s\":" << native::kMaxSolverResidualSeconds
           << ",\"native_iteration_limit\":" << native::kMaxSolverIterations
           << ",\"fitted_gain\":false,\"fitted_time_shift\":false,\"clipping\":false,\"frequency_remapping\":false"
           << ",\"end_boundary_events\":\"inclusive_once_stable_input_order\",\"reference_path_order\":\"channel_major\""
           << ",\"native_path_order\":\"rotor_major\",\"reference_to_native_path\":";
    write_array(output, kReferenceToNativePath);
    output << "},\"totals\":{\"rate_count\":" << run.rates.size() << ",\"completed_partitions\":" << completed_partitions
           << ",\"reference_frames\":" << reference_frames << ",\"reference_scalar_comparisons\":" << 2U * reference_frames
           << ",\"reference_path_solutions\":" << 4U * reference_frames
           << ",\"native_frames\":" << native_frames << ",\"native_path_solutions\":" << 4U * native_frames
           << ",\"partition_compared_samples\":" << compared << ",\"partition_equal_samples\":" << equal
           << ",\"native_events_consumed\":" << events << ",\"selected_trace_paths\":" << selected
           << ",\"convergence_pairs\":" << pairs << ",\"auxiliary_convergence_path_solutions\":" << 2U * pairs << '}'
           << ",\"resource_observations\":{\"max_canonical_audio_bytes\":" << peak_canonical_bytes
           << ",\"canonical_audio_limit_bytes\":30720000,\"current_audio_block_bytes\":" << sizeof(AudioBlock)
           << ",\"sizeof_waveform_history\":" << sizeof(native::WaveformHistory)
           << ",\"sizeof_motion_frame_history\":" << sizeof(native::MotionFrameHistory)
           << ",\"sizeof_renderer_state\":" << sizeof(native::RendererState)
           << ",\"sizeof_renderer_diagnostics\":" << sizeof(native::RendererDiagnostics)
           << ",\"full_waveform_buffers\":1,\"reference_audio_buffered\":false,\"wall_seconds\":" << run.wall_seconds << '}'
           << ",\"groups\":{\"waveform_and_partition_execution\":";
    quoted(output, run.passed ? "pass" : "fail");
    output << ",\"selected_decimal_crosscheck\":\"not_run_in_native_probe\",\"static_grid\":\"not_run_in_native_probe\""
           << ",\"behavioral_transaction_lifecycle\":\"not_run_in_native_probe\",\"r5_audible_policy\":\"not_run\""
           << ",\"r6_device_deadlines\":\"not_run\",\"physical_fidelity\":\"not_run\"}"
           << ",\"failed_stage\":";
    quoted(output, run.failed_stage);
    output << ",\"exception\":"; quoted(output, run.exception);
    output << ",\"failures\":[";
    for (std::size_t index = 0; index < run.failures.size(); ++index) {
        if (index != 0) output << ',';
        quoted(output, run.failures[index]);
    }
    output << "],\"rates\":[";
    for (std::size_t index = 0; index < run.rates.size(); ++index) {
        if (index != 0) output << ',';
        write_rate(output, run.rates[index], full);
    }
    output << "]}\n";
}

} // namespace

int main(int argc, char** argv) {
    RunReport run;
    const auto start = Clock::now();
    std::cout.imbue(std::locale::classic());
    std::cerr.imbue(std::locale::classic());
    try {
        for (int index = 0; index < argc; ++index) run.invocation.emplace_back(argv[index]);
        run.failed_stage = "arguments";
        if (argc == 3 && std::string_view(argv[1]) == "--mode") run.mode = argv[2];
        else require(argc == 1, "usage: rotary_waveform_probe [--mode smoke|full]");
        require(run.mode == "smoke" || run.mode == "full", "mode must be smoke or full");
        const bool full = run.mode == "full";
        run.failed_stage = "arithmetic_environment";
        run.environment_passed = sizeof(double) == 8 && std::numeric_limits<double>::is_iec559
            && std::numeric_limits<double>::radix == 2 && std::numeric_limits<double>::digits == 53
            && std::numeric_limits<Real>::digits >= std::numeric_limits<double>::digits
            && !fast_math_enabled() && std::fegetround() == FE_TONEAREST;
#if defined(__linux__)
        if (full) run.environment_passed = run.environment_passed
            && std::numeric_limits<Real>::digits > std::numeric_limits<double>::digits;
#endif
        require(run.environment_passed, "unqualified arithmetic environment; inspect precision/environment facts");
        run.failed_stage = "sha256_self_check";
        run.hash_self_check_passed = hash_self_check();
        require(run.hash_self_check_passed, "SHA-256 known-vector self-check failed");
        run.rates.reserve(reference::kRates.size());
        for (const auto rate : reference::kRates) {
            run.rates.emplace_back();
            run.rates.back().rate = rate;
            run_rate(run, run.rates.back(), full);
        }
        run.completed = run.rates.size() == reference::kRates.size()
            && std::all_of(run.rates.begin(), run.rates.end(), [](const RateReport& rate) { return rate.completed; });
        run.passed = run.completed
            && std::all_of(run.rates.begin(), run.rates.end(), [](const RateReport& rate) { return rate.passed; });
        run.failed_stage = run.passed ? "" : "completed_comparisons";
    } catch (const std::exception& error) {
        run.exception = error.what();
        run.failures.push_back(run.failed_stage + ": " + error.what());
        std::cerr << "waveform probe failure at " << run.failed_stage << ": " << error.what() << '\n';
    } catch (...) {
        run.exception = "non_standard_exception";
        run.failures.push_back(run.failed_stage + ": non-standard exception");
        std::cerr << "waveform probe non-standard failure at " << run.failed_stage << '\n';
    }
    run.wall_seconds = seconds_since(start);
    write_report(std::cout, run);
    return run.passed ? 0 : 1;
}
