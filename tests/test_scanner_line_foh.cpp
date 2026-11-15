#include "TestSupport.h"
#include "hammond/ScannerLineFoh.h"

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

namespace {

using namespace hammond;
using Complex = std::complex<double>;

constexpr std::array<double, 11> rates{
    44100.0, 48000.0, 88200.0, 96000.0, 176400.0, 192000.0,
    352800.0, 384000.0, 705600.0, 768000.0, 1536000.0};
constexpr std::array<ScannerReturnMode, 2> modes{
    ScannerReturnMode::Vibrato, ScannerReturnMode::Chorus};
// Independent documentary constants and exact rational DC results. These do
// not import the generated graph or the producer's preparation/reconstruction.
constexpr std::array<long double, 6> upper{
    27000.0L, 56000.0L, 39000.0L, 33000.0L, 18000.0L, 12000.0L};
constexpr std::array<long double, 6> lower{
    68000.0L, 150000.0L, 150000.0L, 180000.0L, 180000.0L, 180000.0L};
constexpr std::array<long double, 6> vibrato_dc{
    68.0L / 95.0L, 75.0L / 103.0L, 50.0L / 63.0L,
    60.0L / 71.0L, 10.0L / 11.0L, 15.0L / 16.0L};
constexpr std::array<long double, 6> chorus_dc{
    12463311899.0L / 13657495547.0L, 12515270267.0L / 13657495547.0L,
    12790466267.0L / 13657495547.0L, 13006519067.0L / 13657495547.0L,
    146030693737.0L / 150232451017.0L, 13394885717.0L / 13657495547.0L};
constexpr long double chorus_return_dc = 9455738267.0L / 13657495547.0L;
constexpr long double vibrato_input_dc = 9455738267.0L / 92438660160000.0L;
constexpr long double chorus_input_dc = 9455738267.0L / 300464902034000.0L;

std::size_t dc_cases = 0;
std::size_t reconfiguration_pairs = 0;
std::size_t subdivision_paths = 0;
std::size_t rejected_calls = 0;
double maximum_dc_error = 0.0;
double maximum_process_response_error = 0.0;

[[nodiscard]] long double physical_energy(const ScannerLineState& state) {
    long double result = 0.0L;
    for (std::size_t section = 0; section < 18; ++section) {
        const long double capacitance = section == 17 ? 1.0e-9L : 4.0e-9L;
        const long double voltage = state.capacitor_volts[section];
        const long double current = state.inductor_amps[section];
        result += 0.5L * capacitance * voltage * voltage + 0.25L * current * current;
    }
    return result;
}

[[nodiscard]] ScannerLineState nonzero_checkpoint() {
    ScannerLineState state;
    state.capacitor_volts[0] = 0.375;
    state.capacitor_volts[8] = -0.25;
    state.capacitor_volts[17] = 0.125;
    state.inductor_amps[0] = 2.0e-5;
    state.inductor_amps[9] = -4.0e-5;
    state.inductor_amps[17] = 3.0e-5;
    state.previous_input_volts = -0.3125;
    state.frames = 73;
    return state;
}

[[nodiscard]] ScannerLineFoh precharged(double rate = 48000.0) {
    ScannerLineFoh line;
    CHECK(line.prepare(rate) == Status::Ok);
    CHECK(line.restore_state(nonzero_checkpoint()) == Status::Ok);
    return line;
}

[[nodiscard]] ScannerLineFrame frame_sentinel() {
    ScannerLineFrame frame;
    frame.taps_volts.fill(7.125);
    frame.return_volts = -0.75;
    frame.input_current_amps = 3.0;
    frame.energy_joules = 0.75;
    frame.frame = 9999;
    return frame;
}

[[nodiscard]] ScannerLineResponse response_sentinel() {
    ScannerLineResponse response;
    response.taps.fill({7.0, -3.0});
    response.return_gain = {9.0, 1.0};
    response.input_admittance = {5.0, -2.0};
    response.normalized_residual = 0.125;
    response.condition_inf = 7.0;
    return response;
}

void check_diagnostics_equal(const ScannerLineFoh& left, const ScannerLineFoh& right) {
    const auto a = left.preparation_diagnostics();
    const auto b = right.preparation_diagnostics();
    for (std::size_t index = 0; index < 2; ++index) {
        CHECK(a[index].augmented_norm_one == b[index].augmented_norm_one);
        CHECK(a[index].squarings == b[index].squarings);
        CHECK(a[index].normalized_residual == b[index].normalized_residual);
        CHECK(a[index].condition_inf == b[index].condition_inf);
    }
}

void check_equal_continuation(ScannerLineFoh left, ScannerLineFoh right, bool zero_input = false) {
    CHECK(left.prepared() == right.prepared());
    CHECK(left.sample_rate() == right.sample_rate());
    CHECK(left.preparation_residual() == right.preparation_residual());
    check_diagnostics_equal(left, right);
    CHECK(left.state() == right.state());
    for (std::size_t sample = 0; sample < 32; ++sample) {
        const double input = zero_input ? 0.0 : 0.125 * std::sin(0.31 * static_cast<double>(sample));
        const auto mode = modes[sample % 2];
        ScannerLineFrame a, b;
        CHECK(left.process_frame(input, mode, a) == Status::Ok);
        CHECK(right.process_frame(input, mode, b) == Status::Ok);
        CHECK(a == b);
        CHECK(left.state() == right.state());
    }
}

void check_observation(const ScannerLineState& state, ScannerReturnMode mode,
                       const ScannerLineFrame& frame) {
    const long double input = state.previous_input_volts;
    // Independent KCL at the common return, and two-resistor node equations.
    const long double returned = mode == ScannerReturnMode::Vibrato ? 0.0L :
        (static_cast<long double>(state.inductor_amps[0]) + input / 95000.0L)
        / (1.0L / 22000.0L + 1.0L / 95000.0L);
    CHECK_NEAR(frame.return_volts, returned, 1.0e-12L + 1.0e-12L * std::abs(returned));
    for (std::size_t tap = 0; tap < 6; ++tap) {
        const long double upstream = tap == 0 ? input : returned + state.capacitor_volts[tap - 1];
        const long double expected = (lower[tap] * upstream + upper[tap] * returned)
                                   / (upper[tap] + lower[tap]);
        CHECK_NEAR(frame.taps_volts[tap], expected, 1.0e-12L + 1.0e-12L * std::abs(expected));
    }
    for (std::size_t tap = 6; tap < 19; ++tap) {
        const long double expected = returned + state.capacitor_volts[tap - 1];
        CHECK_NEAR(frame.taps_volts[tap], expected, 1.0e-12L + 1.0e-12L * std::abs(expected));
    }
    const long double current = state.inductor_amps[0] + (input - returned) / 95000.0L;
    CHECK_NEAR(frame.input_current_amps, current, 1.0e-15L + 1.0e-12L * std::abs(current));
    if (mode == ScannerReturnMode::Chorus) {
        CHECK_NEAR(frame.input_current_amps, returned / 22000.0L,
                   1.0e-15L + 1.0e-12L * std::abs(current));
    }
    const long double stored = physical_energy(state);
    CHECK_NEAR(frame.energy_joules, stored, 1.0e-24L + 1.0e-12L * stored);
    CHECK(frame.frame == state.frames);
}

void check_physical_near(const ScannerLineState& actual, const ScannerLineState& expected) {
    for (std::size_t section = 0; section < 18; ++section) {
        CHECK_NEAR(actual.capacitor_volts[section], expected.capacitor_volts[section],
                   1.0e-10 + 2.0e-11 * std::abs(expected.capacitor_volts[section]));
        CHECK_NEAR(actual.inductor_amps[section], expected.inductor_amps[section],
                   1.0e-14 + 2.0e-11 * std::abs(expected.inductor_amps[section]));
    }
    CHECK(actual.previous_input_volts == expected.previous_input_volts);
}

void test_preparation_and_cold_endpoint() {
    static_assert(sizeof(ScannerLineFoh) <= 24 * 1024);
    CHECK(kScannerLineFohRealizationId == "scaled-physical-exponential-foh-scanner-line-v1");
    CHECK(kScannerLineFohPreparationId == "scanner-augmented38-pade13-scaling-squaring-v1");
    CHECK(ScannerLineFoh::authoring_sha256()
          == "1d236be5e6b63e938a9f147808386173949d167e09aee8e902c55002e4ea4604");
    ScannerLineFoh cold;
    CHECK(!cold.prepared());
    CHECK(cold.sample_rate() == 0.0);
    CHECK(cold.preparation_residual() == 0.0);
    CHECK(cold.state() == ScannerLineState{});
    for (const auto& diagnostic : cold.preparation_diagnostics()) {
        CHECK(diagnostic.augmented_norm_one == 0.0);
        CHECK(diagnostic.squarings == 0);
        CHECK(diagnostic.normalized_residual == 0.0);
        CHECK(diagnostic.condition_inf == 0.0);
    }
    const auto invalid_mode = static_cast<ScannerReturnMode>(255);
    const double nan = std::numeric_limits<double>::quiet_NaN();
    auto frame = frame_sentinel();
    auto response = response_sentinel();
    CHECK(cold.reconfigure_sample_rate(nan) == Status::NotPrepared);
    CHECK(cold.restore_state(nonzero_checkpoint()) == Status::NotPrepared);
    CHECK(cold.observe(invalid_mode, frame) == Status::NotPrepared);
    CHECK(cold.process_frame(nan, invalid_mode, frame) == Status::NotPrepared);
    CHECK(cold.response(nan, invalid_mode, response) == Status::NotPrepared);
    CHECK(frame == frame_sentinel());
    CHECK(response == response_sentinel());
    CHECK(cold.prepare(nan) == Status::InvalidSpec);
    CHECK(!cold.prepared());
    for (const double rate : rates) {
        ScannerLineFoh line;
        CHECK(line.prepare(rate) == Status::Ok);
        CHECK(line.prepared());
        CHECK(line.sample_rate() == rate);
        const auto diagnostics = line.preparation_diagnostics();
        CHECK(line.preparation_residual()
              == std::max(diagnostics[0].normalized_residual, diagnostics[1].normalized_residual));
        // The last inductor's column has 1/(C17*Zref)+1/(C18*Zref).
        // The unit augmented superdiagonal sets the lower one-norm bound.
        const double expected_norm = std::max(1.0, 111803.39887498949 / rate);
        for (const auto& diagnostic : diagnostics) {
            CHECK_NEAR(diagnostic.augmented_norm_one, expected_norm, 2.0e-14);
            CHECK(diagnostic.squarings >= 1 && diagnostic.squarings <= 3);
            CHECK(std::ldexp(diagnostic.augmented_norm_one,
                             -static_cast<int>(diagnostic.squarings)) <= 0.5);
            CHECK(std::ldexp(diagnostic.augmented_norm_one,
                             1 - static_cast<int>(diagnostic.squarings)) > 0.5);
            CHECK(std::isfinite(diagnostic.normalized_residual));
            CHECK(diagnostic.normalized_residual >= 0.0 && diagnostic.normalized_residual <= 1.0e-9);
            CHECK(std::isfinite(diagnostic.condition_inf) && diagnostic.condition_inf > 0.0);
            CHECK(diagnostic.condition_inf * std::numeric_limits<double>::epsilon() <= 1.0e-4);
        }
        for (const auto mode : modes) {
            CHECK(line.observe(mode, frame) == Status::Ok);
            CHECK(frame == ScannerLineFrame{});
        }
        CHECK(line.process_frame(1.0, ScannerReturnMode::Vibrato, frame) == Status::Ok);
        CHECK(frame.frame == 1);
        CHECK(line.state().frames == 1);
        CHECK(line.state().previous_input_volts == 1.0);
        CHECK(line.state().capacitor_volts[0] > 0.0);
        CHECK(line.state().inductor_amps[0] > 0.0);
        CHECK_NEAR(frame.taps_volts[0], 68.0 / 95.0, 1.0e-15);
        check_observation(line.state(), ScannerReturnMode::Vibrato, frame);
        const auto before_observation = line.state();
        CHECK(line.observe(ScannerReturnMode::Chorus, frame) == Status::Ok);
        CHECK(line.state() == before_observation);
        check_observation(line.state(), ScannerReturnMode::Chorus, frame);
        CHECK(line.prepare(rate) == Status::Ok);
        CHECK(line.state() == ScannerLineState{});
    }
}

void test_dc_and_response() {
    for (const double rate : rates) {
        auto line = precharged(rate);
        const auto original = line;
        for (const auto mode : modes) {
            ScannerLineResponse response;
            CHECK(line.response(0.0, mode, response) == Status::Ok);
            const auto& expected_dividers = mode == ScannerReturnMode::Vibrato ? vibrato_dc : chorus_dc;
            for (std::size_t tap = 0; tap < 19; ++tap) {
                const double expected = tap < 6 ? static_cast<double>(expected_dividers[tap]) : 1.0;
                const double error = std::abs(response.taps[tap] - Complex{expected, 0.0});
                maximum_dc_error = std::max(maximum_dc_error, error);
                CHECK(error <= 1.0e-10 + 1.0e-9 * std::abs(expected));
            }
            const double returned = mode == ScannerReturnMode::Vibrato ? 0.0
                                  : static_cast<double>(chorus_return_dc);
            CHECK(std::abs(response.return_gain - Complex{returned, 0.0})
                  <= 1.0e-10 + 1.0e-9 * std::abs(returned));
            const double current = 15000.0 * static_cast<double>(mode == ScannerReturnMode::Vibrato
                                  ? vibrato_input_dc : chorus_input_dc);
            CHECK(std::abs(15000.0 * response.input_admittance - Complex{current, 0.0})
                  <= 1.0e-10 + 1.0e-9 * std::abs(current));
            ++dc_cases;
            for (const double frequency : {100.0, 997.0, 5000.0, 7000.0}) {
                CHECK(line.response(frequency, mode, response) == Status::Ok);
                CHECK(std::isfinite(response.normalized_residual) && response.normalized_residual <= 1.0e-9);
                CHECK(std::isfinite(response.condition_inf) && response.condition_inf > 0.0);
                for (const auto& tap : response.taps) {
                    CHECK(std::isfinite(tap.real()) && std::isfinite(tap.imag()));
                }
                CHECK(std::isfinite(response.return_gain.real()) && std::isfinite(response.return_gain.imag()));
                CHECK(std::isfinite(response.input_admittance.real()) && std::isfinite(response.input_admittance.imag()));
            }
        }
        check_equal_continuation(line, original);
    }
}

void test_linear_segment_subdivision() {
    // Exact interval flow must compose over identical input polygons, unlike
    // trapezoidal endpoint forcing. This checks both endpoint weights, the unit
    // augmented superdiagonal and sample-rate units through public processing.
    for (const double base_rate : {44100.0, 48000.0, 96000.0}) {
        for (const auto mode : modes) {
            for (const std::size_t subdivisions : {std::size_t{1}, std::size_t{2}, std::size_t{4},
                                                   std::size_t{8}, std::size_t{16}}) {
                auto coarse = precharged(base_rate);
                auto fine = precharged(base_rate * static_cast<double>(subdivisions));
                for (std::size_t knot = 0; knot < 48; ++knot) {
                    const double input = 0.4 * std::sin(0.27 * static_cast<double>(knot))
                                       - 0.125 * std::cos(0.13 * static_cast<double>(knot));
                    const double previous = fine.state().previous_input_volts;
                    ScannerLineFrame coarse_frame, fine_frame;
                    CHECK(coarse.process_frame(input, mode, coarse_frame) == Status::Ok);
                    for (std::size_t part = 1; part <= subdivisions; ++part) {
                        const double endpoint = part == subdivisions ? input :
                            previous + (input - previous) * (static_cast<double>(part)
                                                           / static_cast<double>(subdivisions));
                        CHECK(fine.process_frame(endpoint, mode, fine_frame) == Status::Ok);
                    }
                    check_physical_near(fine.state(), coarse.state());
                    CHECK(coarse_frame.frame == 73 + static_cast<std::uint64_t>(knot + 1));
                    CHECK(fine_frame.frame == 73 + static_cast<std::uint64_t>((knot + 1) * subdivisions));
                    check_observation(coarse.state(), mode, coarse_frame);
                    check_observation(fine.state(), mode, fine_frame);
                }
                ++subdivision_paths;
            }
        }
    }
}

void test_forcing_and_energy() {
    for (const double rate : rates) {
        ScannerLineFoh prepared;
        CHECK(prepared.prepare(rate) == Status::Ok);
        for (const auto mode : modes) {
            auto current = prepared;
            auto previous = prepared;
            auto negative = prepared;
            ScannerLineState checkpoint;
            checkpoint.previous_input_volts = 1.0;
            CHECK(previous.restore_state(checkpoint) == Status::Ok);
            ScannerLineFrame a, b, opposite;
            CHECK(current.process_frame(1.0, mode, a) == Status::Ok);
            CHECK(previous.process_frame(0.0, mode, b) == Status::Ok);
            CHECK(negative.process_frame(-1.0, mode, opposite) == Status::Ok);
            CHECK(std::abs(current.state().capacitor_volts[0] - previous.state().capacitor_volts[0]) > 1.0e-10);
            check_observation(current.state(), mode, a);
            check_observation(previous.state(), mode, b);
            check_observation(negative.state(), mode, opposite);
            for (std::size_t section = 0; section < 18; ++section) {
                CHECK(negative.state().capacitor_volts[section] == -current.state().capacitor_volts[section]);
                CHECK(negative.state().inductor_amps[section] == -current.state().inductor_amps[section]);
            }
            for (std::size_t tap = 0; tap < 19; ++tap) CHECK(opposite.taps_volts[tap] == -a.taps_volts[tap]);
            for (std::size_t fixture = 0; fixture < 4; ++fixture) {
                auto line = prepared;
                ScannerLineState initial;
                if (fixture == 0) initial.capacitor_volts[0] = 1.0;
                else if (fixture == 1) initial.capacitor_volts[17] = -1.0;
                else if (fixture == 2) initial.inductor_amps[0] = 1.0e-4;
                else initial.inductor_amps[17] = -1.0e-4;
                CHECK(line.restore_state(initial) == Status::Ok);
                const long double starting = physical_energy(initial);
                long double last = starting;
                for (std::size_t sample = 0; sample < 64; ++sample) {
                    ScannerLineFrame frame;
                    CHECK(line.process_frame(0.0, mode, frame) == Status::Ok);
                    const long double stored = physical_energy(line.state());
                    CHECK(stored - last <= 1.0e-12L * starting + 1.0e-24L);
                    CHECK(stored - starting <= 1.0e-10L * starting + 1.0e-24L);
                    check_observation(line.state(), mode, frame);
                    last = stored;
                }
            }
        }
    }
}

void test_reconfiguration() {
    for (const double old_rate : rates) {
        const auto original = precharged(old_rate);
        for (const double new_rate : rates) {
            auto line = original;
            std::array<ScannerLineFrame, 2> before;
            for (std::size_t mode = 0; mode < 2; ++mode) {
                CHECK(line.observe(modes[mode], before[mode]) == Status::Ok);
                check_observation(line.state(), modes[mode], before[mode]);
            }
            CHECK(line.reconfigure_sample_rate(new_rate) == Status::Ok);
            CHECK(line.sample_rate() == new_rate);
            CHECK(line.state() == original.state());
            if (old_rate == new_rate) check_diagnostics_equal(line, original);
            for (std::size_t mode = 0; mode < 2; ++mode) {
                ScannerLineFrame after;
                CHECK(line.observe(modes[mode], after) == Status::Ok);
                CHECK(after == before[mode]);
            }
            auto independently_prepared = precharged(new_rate);
            check_equal_continuation(line, independently_prepared);
            ++reconfiguration_pairs;
        }
    }
}

void test_rejections_and_precedence() {
    const auto original = precharged();
    const auto invalid_mode = static_cast<ScannerReturnMode>(255);
    const double nan = std::numeric_limits<double>::quiet_NaN();
    const double infinity = std::numeric_limits<double>::infinity();
    for (const double input : {nan, infinity, -infinity, std::nextafter(64.0, infinity),
                               -std::nextafter(64.0, infinity)}) {
        auto line = original;
        auto frame = frame_sentinel();
        CHECK(line.process_frame(input, ScannerReturnMode::Chorus, frame) == Status::InvalidBuffer);
        CHECK(frame == frame_sentinel());
        check_equal_continuation(line, original);
        ++rejected_calls;
    }
    for (const double rate : {nan, infinity, -infinity, -48000.0, 0.0, 48001.0,
                              std::nextafter(44100.0, infinity), std::nextafter(1536000.0, infinity)}) {
        auto line = original;
        CHECK(line.prepare(rate) == Status::InvalidSpec);
        check_equal_continuation(line, original);
        CHECK(line.reconfigure_sample_rate(rate) == Status::InvalidSpec);
        check_equal_continuation(line, original);
        rejected_calls += 2;
    }
    for (const double frequency : {nan, infinity, -infinity, -1.0, 24000.0,
                                   std::nextafter(24000.0, infinity)}) {
        auto line = original;
        auto response = response_sentinel();
        CHECK(line.response(frequency, ScannerReturnMode::Chorus, response) == Status::InvalidSpec);
        CHECK(response == response_sentinel());
        check_equal_continuation(line, original);
        ++rejected_calls;
    }
    for (std::size_t coordinate = 0; coordinate < 37; ++coordinate) {
        const double limit = coordinate < 18 ? kScannerMaxCapacitorVolts
                           : coordinate < 36 ? kScannerMaxInductorAmps : kScannerMaxInputVolts;
        for (const double value : {nan, infinity, -infinity,
                                   std::nextafter(limit, infinity), -std::nextafter(limit, infinity)}) {
            auto line = original;
            auto invalid = original.state();
            if (coordinate < 18) invalid.capacitor_volts[coordinate] = value;
            else if (coordinate < 36) invalid.inductor_amps[coordinate - 18] = value;
            else invalid.previous_input_volts = value;
            CHECK(line.restore_state(invalid) == Status::InvalidProfile);
            check_equal_continuation(line, original);
            ++rejected_calls;
        }
    }
    auto line = original;
    ScannerLineState excessive_energy;
    excessive_energy.inductor_amps[7] = 1.5;
    excessive_energy.inductor_amps[8] = -1.5;
    CHECK(physical_energy(excessive_energy) > 1.0L);
    CHECK(line.restore_state(excessive_energy) == Status::InvalidProfile);
    check_equal_continuation(line, original);
    ++rejected_calls;
    auto frame = frame_sentinel();
    auto response = response_sentinel();
    CHECK(line.observe(invalid_mode, frame) == Status::InvalidEvent);
    CHECK(line.process_frame(nan, invalid_mode, frame) == Status::InvalidEvent);
    CHECK(line.response(nan, invalid_mode, response) == Status::InvalidEvent);
    CHECK(frame == frame_sentinel());
    CHECK(response == response_sentinel());
    check_equal_continuation(line, original);
    rejected_calls += 3;
    for (const double sign : {-1.0, 1.0}) {
        ScannerLineState boundary;
        boundary.inductor_amps[17] = sign * 2.0;
        CHECK(physical_energy(boundary) == 1.0L);
        CHECK(line.restore_state(boundary) == Status::Ok);
        CHECK(line.observe(ScannerReturnMode::Chorus, frame) == Status::Ok);
        check_observation(boundary, ScannerReturnMode::Chorus, frame);
        boundary = {};
        boundary.previous_input_volts = sign * 64.0;
        CHECK(line.restore_state(boundary) == Status::Ok);
        CHECK(line.observe(ScannerReturnMode::Vibrato, frame) == Status::Ok);
        CHECK(line.prepare(48000.0) == Status::Ok);
        CHECK(line.process_frame(sign * 64.0, ScannerReturnMode::Chorus, frame) == Status::Ok);
    }
    auto saturated = original.state();
    saturated.frames = std::numeric_limits<std::uint64_t>::max() - 1;
    CHECK(line.restore_state(saturated) == Status::Ok);
    CHECK(line.process_frame(0.0, ScannerReturnMode::Vibrato, frame) == Status::Ok);
    CHECK(frame.frame == std::numeric_limits<std::uint64_t>::max());
    const auto before = line.state();
    const auto frame_before = frame;
    CHECK(line.process_frame(nan, invalid_mode, frame) == Status::InvalidEvent);
    CHECK(line.process_frame(nan, ScannerReturnMode::Chorus, frame) == Status::InvalidBuffer);
    CHECK(line.process_frame(0.0, ScannerReturnMode::Chorus, frame) == Status::TimelineOverflow);
    CHECK(line.state() == before);
    CHECK(frame == frame_before);
    CHECK(line.restore_state(before) == Status::Ok);
    CHECK(line.observe(ScannerReturnMode::Chorus, frame) == Status::Ok);
    check_observation(before, ScannerReturnMode::Chorus, frame);
    rejected_calls += 3;
}

void test_late_candidate_rejection() {
    for (const auto mode : modes) {
        for (const double sign : {-1.0, 1.0}) {
            ScannerLineFoh line;
            CHECK(line.prepare(48000.0) == Status::Ok);
            ScannerLineState state;
            state.inductor_amps[9] = sign * 1.999999999;
            state.frames = 127;
            CHECK(physical_energy(state) < 1.0L);
            CHECK(line.restore_state(state) == Status::Ok);
            const auto original = line;
            auto half = line;
            state.inductor_amps[9] *= 0.5;
            CHECK(half.restore_state(state) == Status::Ok);
            ScannerLineFrame half_frame;
            CHECK(half.process_frame(sign * 32.0, mode, half_frame) == Status::Ok);
            auto full = half.state();
            for (double& voltage : full.capacitor_volts) voltage *= 2.0;
            for (double& current : full.inductor_amps) current *= 2.0;
            CHECK(physical_energy(full) > 1.0L + 1.0e-10L);
            auto frame = frame_sentinel();
            CHECK(line.process_frame(sign * 64.0, mode, frame) == Status::InvalidBuffer);
            CHECK(frame == frame_sentinel());
            check_equal_continuation(line, original, true);
            ++rejected_calls;
        }
    }
}

void test_partitions() {
    constexpr std::size_t samples = 257;
    constexpr std::array<std::size_t, 7> irregular{1, 17, 64, 3, 127, 2, 31};
    std::array<double, samples> input{};
    for (std::size_t index = 0; index < samples; ++index) {
        input[index] = 0.4 * std::sin(0.113 * static_cast<double>(index))
                     + 0.2 * std::cos(0.039 * static_cast<double>(index));
    }
    const auto mode_at = [](std::size_t index) { return modes[(index / 11) % 2]; };
    for (const double rate : rates) {
        auto reference = precharged(rate);
        const auto initial = reference;
        std::array<ScannerLineFrame, samples> expected{};
        for (std::size_t index = 0; index < samples; ++index) {
            CHECK(reference.process_frame(input[index], mode_at(index), expected[index]) == Status::Ok);
        }
        for (const std::size_t partition : {std::size_t{1}, std::size_t{64}, std::size_t{127}, std::size_t{0}}) {
            auto line = initial;
            std::size_t cursor = 0;
            std::size_t chunk = 0;
            while (cursor < samples) {
                const auto before = line.state();
                ScannerLineFrame observation;
                CHECK(line.observe(modes[chunk % 2], observation) == Status::Ok);
                CHECK(line.state() == before);
                const std::size_t count = std::min(samples - cursor,
                    partition == 0 ? irregular[chunk % irregular.size()] : partition);
                for (std::size_t offset = 0; offset < count; ++offset) {
                    const std::size_t index = cursor + offset;
                    ScannerLineFrame frame;
                    CHECK(line.process_frame(input[index], mode_at(index), frame) == Status::Ok);
                    CHECK(frame == expected[index]);
                }
                cursor += count;
                ++chunk;
            }
            CHECK(line.state() == reference.state());
        }
    }
}

void test_actual_process_response_consistency() {
    // Bounded producer smoke only: two 997-Hz cosines at 48 kHz, an explicit
    // two-second startup and one-second integer-cycle measurement. The full
    // independent settling/reference protocol belongs to later acceptance.
    constexpr std::size_t rate = 48000;
    constexpr std::size_t startup = 2 * rate;
    constexpr double amplitude = 0.125;
    for (const auto mode : modes) {
        ScannerLineFoh line;
        CHECK(line.prepare(static_cast<double>(rate)) == Status::Ok);
        std::array<Complex, 21> estimates{};
        for (std::size_t sample = 0; sample < startup + rate; ++sample) {
            const double angle = 2.0 * std::numbers::pi * 997.0 * static_cast<double>(sample)
                               / static_cast<double>(rate);
            const Complex projection{std::cos(angle), -std::sin(angle)};
            ScannerLineFrame frame;
            CHECK(line.process_frame(amplitude * projection.real(), mode, frame) == Status::Ok);
            if (sample >= startup) {
                for (std::size_t tap = 0; tap < 19; ++tap) estimates[tap] += frame.taps_volts[tap] * projection;
                estimates[19] += frame.return_volts * projection;
                estimates[20] += 15000.0 * frame.input_current_amps * projection;
            }
        }
        const auto final_state = line.state();
        ScannerLineResponse response;
        CHECK(line.response(997.0, mode, response) == Status::Ok);
        CHECK(line.state() == final_state);
        for (std::size_t channel = 0; channel < estimates.size(); ++channel) {
            estimates[channel] *= 2.0 / (amplitude * static_cast<double>(rate));
            const Complex expected = channel < 19 ? response.taps[channel]
                                   : channel == 19 ? response.return_gain : 15000.0 * response.input_admittance;
            const double error = std::abs(estimates[channel] - expected);
            maximum_process_response_error = std::max(maximum_process_response_error, error);
            CHECK(error <= 1.0e-8 + 1.0e-6 * std::abs(expected));
        }
    }
}

} // namespace

int main() {
    test_preparation_and_cold_endpoint();
    test_dc_and_response();
    test_linear_segment_subdivision();
    test_forcing_and_energy();
    test_reconfiguration();
    test_rejections_and_precedence();
    test_late_candidate_rejection();
    test_partitions();
    test_actual_process_response_consistency();
    std::cout << std::setprecision(17)
              << "scanner FOH producer behavior checks passed\n"
              << "sizeof_scanner_line_foh=" << sizeof(ScannerLineFoh)
              << " dc_cases=" << dc_cases << " maximum_dc_complex_error=" << maximum_dc_error << '\n'
              << "rate_pairs=" << reconfiguration_pairs << " subdivision_paths=" << subdivision_paths
              << " rejected_calls=" << rejected_calls << '\n'
              << "process_response_smoke_cases=2 maximum_complex_error=" << maximum_process_response_error << '\n'
              << "independent_full_grid_transients_resources_acceptance=not_run_by_this_test\n";
}
