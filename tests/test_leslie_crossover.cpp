#include "TestSupport.h"
#include "hammond/LeslieCrossover.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <complex>
#include <cstddef>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numbers>
#include <span>
#include <vector>

namespace {

using namespace hammond;
using Complex = std::complex<double>;
constexpr std::array<double, 4> rates{44100.0, 48000.0, 96000.0, 192000.0};
constexpr std::array<LeslieCrossoverLoads, 5> load_cases{{
    {16.0, 16.0}, {8.0, 32.0}, {1.0, 1024.0}, {1024.0, 1.0}, {1024.0, 1024.0}}};
constexpr double nan = std::numeric_limits<double>::quiet_NaN();
constexpr double infinity = std::numeric_limits<double>::infinity();
constexpr auto last_frame = std::numeric_limits<std::uint64_t>::max();

double maximum_response_error = 0.0;
double maximum_response_residual = 0.0;
double maximum_sine_error = 0.0;
double maximum_energy_residual = 0.0;
std::size_t response_checks = 0;

[[nodiscard]] LeslieCrossoverFrame sentinel() {
    return {7.0, -3.0, 2.0, -4.0, 5.0, 6.0, 777};
}

// Independent series/parallel impedance oracle from the literal topology:
// RT || L2 is A-H, then C16A to B; L3 is A-W, then RW || C16B to B.
// No state matrix, native helper response, or runtime coefficient is used.
[[nodiscard]] LeslieCrossoverResponse analog(double frequency, LeslieCrossoverLoads loads) {
    const Complex s{0.0, 2.0 * std::numbers::pi * frequency};
    const Complex treble_parallel = (s * 0.0032 * loads.treble_ohms)
        / (loads.treble_ohms + s * 0.0032);
    const Complex treble_series = treble_parallel + 1.0 / (s * 7.8e-6);
    const Complex bass_parallel = loads.bass_ohms / (1.0 + s * 12.5e-6 * loads.bass_ohms);
    const Complex bass_series = s * 0.0052 + bass_parallel;
    return {treble_parallel / treble_series, bass_parallel / bass_series,
            1.0 / treble_series + 1.0 / bass_series, 0.0};
}

void complex_near(Complex actual, Complex expected, double tolerance, double& maximum) {
    const double error = std::abs(actual - expected) / std::max(1.0, std::abs(expected));
    CHECK(std::isfinite(error));
    maximum = std::max(maximum, error);
    CHECK(error <= tolerance);
}

void check_responses() {
    for (const auto rate : rates) {
        for (const auto loads : load_cases) {
            LeslieCrossover crossover;
            CHECK(crossover.prepare(rate, loads) == Status::Ok);
            CHECK(crossover.preparation_residual() <= 1.0e-12);
            CHECK(crossover.state() == LeslieCrossoverState{});
            LeslieCrossoverResponse dc;
            CHECK(crossover.response(0.0, dc) == Status::Ok);
            CHECK(dc.treble_gain == Complex{});
            CHECK(dc.bass_gain == Complex{1.0});
            CHECK(dc.input_admittance == Complex{1.0 / loads.bass_ohms});
            CHECK(dc.normalized_residual <= 1.0e-12);
            for (std::size_t point = 0; point < 124; ++point) {
                const double frequency = point < 121
                    ? 10.0 * std::pow(2000.0, static_cast<double>(point) / 120.0)
                    : std::array<double, 3>{400.0, 800.0, 1600.0}[point - 121];
                // The native recurrence is trapezoidal. Compare to its exact
                // bilinear frequency mapping, not to an analog same-Hz claim.
                const double warped = rate / std::numbers::pi
                    * std::tan(std::numbers::pi * frequency / rate);
                const auto expected = analog(warped, loads);
                LeslieCrossoverResponse actual;
                CHECK(crossover.response(frequency, actual) == Status::Ok);
                complex_near(actual.treble_gain, expected.treble_gain, 2.0e-10, maximum_response_error);
                complex_near(actual.bass_gain, expected.bass_gain, 2.0e-10, maximum_response_error);
                complex_near(actual.input_admittance, expected.input_admittance, 2.0e-10, maximum_response_error);
                maximum_response_residual = std::max(maximum_response_residual, actual.normalized_residual);
                CHECK(actual.normalized_residual <= 1.0e-12);
                ++response_checks;
            }
            CHECK(crossover.state() == LeslieCrossoverState{});
        }
    }
}

void check_processed_sines() {
    constexpr std::size_t warmup = 8192;
    constexpr std::size_t fit = 4096;
    constexpr double omega = 2.0 * std::numbers::pi / 64.0;
    for (const auto rate : rates) {
        LeslieCrossover crossover;
        CHECK(crossover.prepare(rate) == Status::Ok);
        std::array<Complex, 3> sums{};
        for (std::size_t index = 0; index < warmup + fit; ++index) {
            const double phase = omega * static_cast<double>(index);
            const double input = std::sin(phase);
            LeslieCrossoverFrame frame;
            CHECK(crossover.process_frame(input, frame) == Status::Ok);
            if (index >= warmup) {
                const Complex projection{input, std::cos(phase)};
                sums[0] += frame.treble_volts * projection;
                sums[1] += frame.bass_volts * projection;
                sums[2] += frame.input_current_amps * projection;
            }
        }
        const double warped = rate / std::numbers::pi * std::tan(std::numbers::pi / 64.0);
        const auto expected = analog(warped, {});
        const double normalization = 2.0 / static_cast<double>(fit);
        complex_near(sums[0] * normalization, expected.treble_gain, 2.0e-8, maximum_sine_error);
        complex_near(sums[1] * normalization, expected.bass_gain, 2.0e-8, maximum_sine_error);
        complex_near(sums[2] * normalization, expected.input_admittance, 2.0e-8, maximum_sine_error);
    }
}

void check_partitions_and_atomic_blocks() {
    constexpr std::size_t count = kLeslieCrossoverBlockCapacity;
    std::vector<double> input(count);
    for (std::size_t index = 0; index < count; ++index) {
        input[index] = 0.5 * std::sin(0.071 * static_cast<double>(index));
    }
    std::vector<LeslieCrossoverFrame> scalar(count), whole(count), partitioned(count);
    LeslieCrossover one, block, pieces;
    CHECK(one.prepare(48000.0) == Status::Ok);
    block = one;
    pieces = one;
    for (std::size_t index = 0; index < count; ++index) {
        CHECK(one.process_frame(input[index], scalar[index]) == Status::Ok);
    }
    CHECK(block.process(input, whole) == Status::Ok);
    std::size_t offset = 0;
    constexpr std::array<std::size_t, 6> lengths{1, 17, 64, 257, 1024, 2733};
    for (const auto length : lengths) {
        CHECK(pieces.process(std::span{input}.subspan(offset, length),
                             std::span{partitioned}.subspan(offset, length)) == Status::Ok);
        offset += length;
        CHECK(pieces.process({}, {}) == Status::Ok);
    }
    CHECK(offset == count);
    CHECK(scalar == whole);
    CHECK(scalar == partitioned);
    CHECK(one.state() == block.state());
    CHECK(one.state() == pieces.state());

    const auto before = block;
    std::fill(whole.begin(), whole.end(), sentinel());
    const auto output_before = whole;
    input.back() = nan;
    CHECK(block.process(input, whole) == Status::InvalidBuffer);
    CHECK(block.state() == before.state());
    CHECK(whole == output_before);
    input.back() = 0.25;
    auto control = before;
    CHECK(control.process(input, scalar) == Status::Ok);
    CHECK(block.process(input, whole) == Status::Ok);
    CHECK(scalar == whole);
    CHECK(control.state() == block.state());

    auto aliased = sentinel();
    const auto state_before_alias = block.state();
    CHECK(block.process(std::span<const double>{&aliased.treble_volts, 1},
                        std::span<LeslieCrossoverFrame>{&aliased, 1}) == Status::InvalidBuffer);
    CHECK(aliased == sentinel());
    CHECK(block.state() == state_before_alias);

    // An admitted high-energy numerical fixture fails on the third interval,
    // after two valid intervals. A block must still commit none of its prefix.
    LeslieCrossover limited;
    CHECK(limited.prepare(192000.0) == Status::Ok);
    const LeslieCrossoverState precharge{{60000.0, 0.0}, {}, 0.0, 0};
    CHECK(limited.restore_state(precharge) == Status::Ok);
    auto scalar_limit = limited;
    const std::array<double, 3> zeros{};
    std::array<LeslieCrossoverFrame, 3> rejected{sentinel(), sentinel(), sentinel()};
    const auto untouched = rejected;
    CHECK(limited.process(zeros, rejected) == Status::InvalidBuffer);
    CHECK(limited.state() == precharge);
    CHECK(rejected == untouched);
    auto frame = sentinel();
    CHECK(scalar_limit.process_frame(0.0, frame) == Status::Ok);
    CHECK(scalar_limit.process_frame(0.0, frame) == Status::Ok);
    const auto last_valid_state = scalar_limit.state();
    frame = sentinel();
    CHECK(scalar_limit.process_frame(0.0, frame) == Status::InvalidBuffer);
    CHECK(scalar_limit.state() == last_valid_state);
    CHECK(frame == sentinel());
}

void check_rate_and_checkpoint_transactions() {
    const LeslieCrossoverState charged{{0.25, -0.5}, {0.001, -0.003}, 0.125, 42};
    for (const auto from : rates) {
        for (const auto to : rates) {
            LeslieCrossover crossover;
            CHECK(crossover.prepare(from, {8.0, 32.0}) == Status::Ok);
            CHECK(crossover.restore_state(charged) == Status::Ok);
            LeslieCrossoverFrame before;
            CHECK(crossover.observe(before) == Status::Ok);
            CHECK(crossover.reconfigure_sample_rate(to) == Status::Ok);
            CHECK(crossover.state() == charged);
            CHECK(crossover.sample_rate() == to);
            CHECK((crossover.loads() == LeslieCrossoverLoads{8.0, 32.0}));
            LeslieCrossoverFrame after;
            CHECK(crossover.observe(after) == Status::Ok);
            CHECK(after == before);
            CHECK(crossover.process_frame(0.3, after) == Status::Ok);
            CHECK(after.frame == 43);
            CHECK(crossover.prepare(from) == Status::Ok);
            CHECK(crossover.state() == LeslieCrossoverState{});
        }
    }
}

void check_rejections_and_precedence() {
    LeslieCrossover crossover;
    auto output = sentinel();
    LeslieCrossoverResponse response{{2.0, 3.0}, {4.0, 5.0}, {6.0, 7.0}, 8.0};
    const auto response_before = response;
    CHECK(crossover.process_frame(nan, output) == Status::NotPrepared);
    CHECK(crossover.process({}, {}) == Status::NotPrepared);
    CHECK(crossover.observe(output) == Status::NotPrepared);
    CHECK(crossover.response(nan, response) == Status::NotPrepared);
    CHECK(crossover.restore_state({}) == Status::NotPrepared);
    CHECK(crossover.reconfigure_sample_rate(nan) == Status::NotPrepared);
    CHECK(output == sentinel());
    CHECK(response == response_before);
    CHECK(crossover.prepare(48000.0) == Status::Ok);
    CHECK(crossover.process_frame(1.0, output) == Status::Ok);
    const auto state_before = crossover.state();
    const double residual_before = crossover.preparation_residual();
    for (const auto rate : std::array<double, 6>{0.0, -1.0, 32000.0, 88200.0, infinity, nan}) {
        CHECK(crossover.prepare(rate) == Status::InvalidSpec);
        CHECK(crossover.reconfigure_sample_rate(rate) == Status::InvalidSpec);
        CHECK(crossover.state() == state_before);
        CHECK(crossover.sample_rate() == 48000.0);
        CHECK(crossover.preparation_residual() == residual_before);
    }
    for (const auto resistance : std::array<double, 6>{0.0, 0.999, 1024.001, -1.0, infinity, nan}) {
        CHECK(crossover.prepare(96000.0, {resistance, 16.0}) == Status::InvalidSpec);
        CHECK(crossover.prepare(96000.0, {16.0, resistance}) == Status::InvalidSpec);
        CHECK(crossover.state() == state_before);
        CHECK(crossover.sample_rate() == 48000.0);
        CHECK(crossover.loads() == LeslieCrossoverLoads{});
    }
    for (const auto frequency : std::array<double, 5>{-1.0, 24000.0, 48000.0, infinity, nan}) {
        CHECK(crossover.response(frequency, response) == Status::InvalidSpec);
        CHECK(response == response_before);
    }
    for (const auto input : std::array<double, 5>{-64.001, 64.001, infinity, -infinity, nan}) {
        output = sentinel();
        CHECK(crossover.process_frame(input, output) == Status::InvalidBuffer);
        CHECK(output == sentinel());
        CHECK(crossover.state() == state_before);
    }
    for (std::size_t field = 0; field < 5; ++field) {
        for (const auto invalid : std::array<double, 2>{nan, infinity}) {
            auto state = state_before;
            if (field < 2) state.capacitor_volts[field] = invalid;
            else if (field < 4) state.inductor_amps[field - 2] = invalid;
            else state.previous_input_volts = invalid;
            CHECK(crossover.restore_state(state) == Status::InvalidProfile);
            CHECK(crossover.state() == state_before);
        }
    }
    for (const auto sign : std::array<double, 2>{-1.0, 1.0}) {
        auto state = state_before;
        state.capacitor_volts[0] = sign * 65536.001;
        CHECK(crossover.restore_state(state) == Status::InvalidProfile);
        state = state_before;
        state.inductor_amps[1] = sign * 256.001;
        CHECK(crossover.restore_state(state) == Status::InvalidProfile);
        state = state_before;
        state.previous_input_volts = sign * 64.001;
        CHECK(crossover.restore_state(state) == Status::InvalidProfile);
    }
    CHECK(crossover.state() == state_before);

    auto exhausted = state_before;
    exhausted.frames = last_frame;
    CHECK(crossover.restore_state(exhausted) == Status::Ok);
    output = sentinel();
    CHECK(crossover.process_frame(nan, output) == Status::TimelineOverflow);
    CHECK(output == sentinel());
    CHECK(crossover.process({}, {}) == Status::Ok);
    CHECK(crossover.state() == exhausted);
    std::vector<double> input(kLeslieCrossoverBlockCapacity + 1, nan);
    std::vector<LeslieCrossoverFrame> frames(input.size(), sentinel());
    CHECK(crossover.process(input, std::span{frames}.first(1)) == Status::InvalidBuffer);
    CHECK(crossover.process(input, frames) == Status::BlockTooLarge);
    CHECK(crossover.process(std::span{input}.first(1), std::span{frames}.first(1)) == Status::TimelineOverflow);
    CHECK(std::all_of(frames.begin(), frames.end(), [](const auto& frame) { return frame == sentinel(); }));
    CHECK(crossover.state() == exhausted);
    CHECK(crossover.observe(output) == Status::Ok);
    CHECK(output.frame == last_frame);
}

void check_midpoint_energy_and_decay() {
    for (const auto rate : rates) {
        LeslieCrossover crossover;
        CHECK(crossover.prepare(rate, {8.0, 32.0}) == Status::Ok);
        CHECK(crossover.restore_state({{0.4, -0.2}, {0.01, -0.02}, 0.3, 0}) == Status::Ok);
        for (std::size_t index = 0; index < 5000; ++index) {
            LeslieCrossoverFrame before, after;
            CHECK(crossover.observe(before) == Status::Ok);
            const double previous_input = crossover.state().previous_input_volts;
            const double input = 0.9 * std::sin(0.073 * static_cast<double>(index));
            CHECK(crossover.process_frame(input, after) == Status::Ok);
            const double midpoint_input = 0.5 * (previous_input + input);
            const double midpoint_current = 0.5 * (before.input_current_amps + after.input_current_amps);
            const double midpoint_treble = 0.5 * (before.treble_volts + after.treble_volts);
            const double midpoint_bass = 0.5 * (before.bass_volts + after.bass_volts);
            const double source_work = midpoint_input * midpoint_current / rate;
            const double load_work = (midpoint_treble * midpoint_treble / 8.0
                + midpoint_bass * midpoint_bass / 32.0) / rate;
            const double residual = std::abs(after.energy_joules - before.energy_joules - source_work + load_work);
            const double scale = std::max({1.0, std::abs(before.energy_joules),
                                           std::abs(after.energy_joules), std::abs(source_work)});
            maximum_energy_residual = std::max(maximum_energy_residual, residual / scale);
            CHECK(residual <= 2.0e-11 * scale);
        }
        // Exercise nominal zero-input decay through the denormal tail. The
        // endpoint remains finite; numerical passivity is not acoustic evidence.
        CHECK(crossover.prepare(rate) == Status::Ok);
        CHECK(crossover.restore_state({{1.0, -0.5}, {0.01, -0.02}, 0.0, 0}) == Status::Ok);
        LeslieCrossoverFrame frame;
        for (std::uint64_t index = 0; index < static_cast<std::uint64_t>(rate) * 10; ++index) {
            CHECK(crossover.process_frame(0.0, frame) == Status::Ok);
            CHECK(std::isfinite(frame.energy_joules));
        }
        CHECK(frame.energy_joules <= 1.0e-24);
    }
}

} // namespace

int main() {
    check_responses();
    check_processed_sines();
    check_partitions_and_atomic_blocks();
    check_rate_and_checkpoint_transactions();
    check_rejections_and_precedence();
    check_midpoint_energy_and_decay();
    std::cout << std::setprecision(17)
              << "Leslie crossover author checks passed: responses=" << response_checks
              << " max_response_error=" << maximum_response_error
              << " max_response_residual=" << maximum_response_residual
              << " max_processed_sine_error=" << maximum_sine_error
              << " max_midpoint_energy_residual=" << maximum_energy_residual << '\n';
}
